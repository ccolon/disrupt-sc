# -*- coding: utf-8 -*-
"""Terrain-resolved road speeds from OSM maxspeed (v25b, Deliverable 3).

Problem (ValidationNote3 / manifest p34): per-km class costs cannot separate
roads of the same class - DN73 (curvy Carpathian trunk, OSM lw-mean maxspeed
54 km/h) prices identically to DN1 (fast valley trunk, 72 km/h), so routing
concentrates on the shortest trunk (DN73 CESTRIN ratio 2.37) while DN1A
reads 0.00.

Fix: stamp a `speed_class` attribute on the roads layer of transport.gpkg,
banded from OSM maxspeed where present (85% of domestic road-km), class-
fallback elsewhere; the speeds config then keys on it (the `attribute:`
mechanism of _resolve_by_attribute), while basic_cost stays keyed on class.

Method:
  - effective truck speed = RATIO x mean(maxspeed), clipped [25, 68] km/h
    (RATIO = truck practical / legal limit);
  - MEAN-PRESERVING: RATIO is solved so the v24-flow tkm-weighted mean road
    speed equals the one under the current class speeds (62/52/46/35) -
    the v7 and v24 mode-choice calibrations are preserved in aggregate;
  - speeds rounded to 4 km/h bands -> classes ms28..ms68; edges without
    maxspeed (and the foreign skeleton) get cls_<class> fallbacks at the
    current class values. Attribute-only edit: geometries untouched (KI-48).

Writes transport.gpkg (roads layer) in place after a .pre_v25b backup copy,
and prints the speeds config block to paste into user_defined_Romania.yaml.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import geopandas as gpd
import numpy as np

DATA = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc-data\Romania")
GPKG = DATA / "Transport" / "transport.gpkg"
REPO = Path(__file__).resolve().parents[2]
V24 = REPO / "output" / "Romania" / "20261020_111601" / "transport_edges_with_flows_0.geojson"
CUR = {"motorway": 62, "trunk": 52, "primary": 46, "secondary": 35}
DEFAULT_SPEED = 50.0
CLIP = (25.0, 68.0)
BAND = 4


def mean_ms(x) -> float | None:
    vals = [int(v) for v in re.findall(r"\d+", str(x) or "")]
    vals = [v for v in vals if 5 <= v <= 130]
    return sum(vals) / len(vals) if vals else None


def main() -> int:
    roads = gpd.read_file(GPKG, layer="roads")
    flows = gpd.read_file(V24, ignore_geometry=True)[["id", "flow_total_tons"]]
    r = roads.merge(flows, on="id", how="left")
    r["flow"] = r["flow_total_tons"].fillna(0.0)
    r["ms"] = r["maxspeed"].map(mean_ms)
    dom = (r["foreign"].fillna(0) != 1)
    use_ms = dom & r["ms"].notna()

    # current class speed per edge (for the preserved mean and the fallback)
    r["cur_speed"] = r["class"].map(CUR).fillna(DEFAULT_SPEED)

    # solve RATIO so that the flow-weighted mean speed over domestic
    # flow-carrying road edges is preserved (fallback edges keep cur_speed,
    # so the equation is on the maxspeed subset)
    w = (r["flow"] * r["km"]).where(dom, 0.0)
    w_ms = w.where(use_ms, 0.0)
    target = float((w * r["cur_speed"]).sum() / w.sum())

    def mean_with(ratio: float) -> float:
        sp = np.clip(ratio * r["ms"].fillna(0), *CLIP).where(use_ms, r["cur_speed"])
        return float((w * sp).sum() / w.sum())

    lo, hi = 0.4, 1.1
    for _ in range(60):
        mid = (lo + hi) / 2
        if mean_with(mid) < target:
            lo = mid
        else:
            hi = mid
    ratio = (lo + hi) / 2
    print(f"tkm-weighted mean speed target {target:.2f} km/h -> RATIO = {ratio:.3f}"
          f" (mean with ratio: {mean_with(ratio):.2f})")

    sp = np.clip(ratio * r["ms"], *CLIP)
    band = (np.round(sp / BAND) * BAND).astype("Int64")
    r["speed_class"] = None
    r.loc[use_ms, "speed_class"] = "ms" + band[use_ms].astype(str)
    r.loc[~use_ms, "speed_class"] = "cls_" + r.loc[~use_ms, "class"].astype(str)

    counts = r.loc[dom, "speed_class"].value_counts()
    print("domestic speed_class distribution:")
    print(counts.to_string())

    roads["speed_class"] = r["speed_class"].values
    backup = GPKG.with_suffix(".gpkg.pre_v25b")
    if not backup.exists():
        shutil.copy2(GPKG, backup)
        print(f"backup -> {backup.name}")
    roads.to_file(GPKG, layer="roads", driver="GPKG")
    print(f"written speed_class to {GPKG.name} (roads layer, "
          f"{roads['speed_class'].notna().sum()}/{len(roads)} stamped)")

    # config block
    bands = sorted(int(c[2:]) for c in counts.index if c.startswith("ms"))
    entries = ", ".join(f"ms{b}: {b}" for b in bands)
    fallb = ", ".join(f"cls_{k}: {v}" for k, v in CUR.items())
    print("\npaste into user_defined_Romania.yaml -> logistics.speeds:")
    print(f"    roads: {{attribute: speed_class, {entries},\n"
          f"            {fallb}, default: {DEFAULT_SPEED:.0f}}}")
    return 0


if __name__ == "__main__":
    main()
