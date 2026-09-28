# -*- coding: utf-8 -*-
"""Repair two collateral effects of the pass-2/pass-3 cleaners (28 Sep 2026).

1. KM RESTORE: the cleaners' blanket 'refresh km where it deviates >10%
   from geometry' overwrote ROUTE-LENGTH km attributes on edges whose
   geometry is legitimately simplified (TEN-T abroad, coarse UA lines,
   long BCP edges): 215 rail edges lost ~660 km in total (repricing
   foreign rail ~9% cheaper) and the road pass did the same on a smaller
   scale. Fix: for every edge whose GEOMETRY is unchanged vs the pre-edit
   reference run, restore that run's km. Edited edges (no geometry match)
   keep their geometry-derived km - correct, since the user traced real
   alignments.
     railways reference: run 20260925_150549 (pre rail edits)
     roads reference:    run 20260924_235138 (pre road edits)

2. MULTIMODAL RE-ANCHOR: node identity is exact (1e-6) with NO snapping,
   so a connector whose endpoint's node was deleted attaches to nothing.
   The border reworks orphaned three UAMD port connectors (Reni rail-water,
   Reni road-water, Giurgiulesti road-water). Fix: move each orphaned
   endpoint to the nearest node of its mode (within 5 km).

NB: 56 further connector endpoints at FOREIGN TEN-T ports have been
off-node since their creation (pre-existing; 'connectors active 137/154'
in the metrics) - left untouched, logged in the manifest.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

T = Path(r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Transport")
OUT = Path(r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/output/Romania")
REFS = {"railways": OUT / "20260925_150549" / "transport_edges_with_flows_0.geojson",
        "roads": OUT / "20260924_235138" / "transport_edges_with_flows_0.geojson"}


def hav(a, b):
    lo1, la1, lo2, la2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def gkey(g):
    cs = list(g.coords)
    e = tuple(sorted([(round(cs[0][0], 5), round(cs[0][1], 5)),
                      (round(cs[-1][0], 5), round(cs[-1][1], 5))]))
    return (e, len(cs))


def main() -> int:
    for layer, ref_path in REFS.items():
        cur = gpd.read_file(T / "transport.gpkg", layer=layer)
        ref = gpd.read_file(ref_path)
        ref = ref[ref["type"] == layer]
        rk = {}
        for _, r in ref.iterrows():
            rk[gkey(r.geometry)] = float(r["km"])
        n, dk = 0, 0.0
        for i in cur.index:
            k = gkey(cur.geometry[i])
            if k in rk and abs(float(cur.loc[i, "km"]) - rk[k]) > 0.05:
                dk += rk[k] - float(cur.loc[i, "km"])
                cur.loc[i, "km"] = rk[k]
                n += 1
        print(f"{layer}: km restored on {n} geometry-unchanged edges "
              f"({dk:+,.0f} km total)")
        cur["km"] = pd.to_numeric(cur["km"], errors="raise").astype(float)
        cur.to_file(T / "transport.gpkg", layer=layer, driver="GPKG")

    # ---- re-anchor orphaned UAMD port connectors ------------------------
    mm = gpd.read_file(T / "multimodal.gpkg")
    nodes = {}
    for mode in ("roads", "railways", "waterways", "maritime"):
        g = gpd.read_file(T / "transport.gpkg", layer=mode)
        s = set()
        for geom in g.geometry:
            cs = list(geom.coords)
            s.add((round(cs[0][0], 6), round(cs[0][1], 6)))
            s.add((round(cs[-1][0], 6), round(cs[-1][1], 6)))
        nodes[mode] = s
    n_fix = 0
    for i in mm.index:
        name = str(mm.loc[i, "name"])
        if not name.startswith("UAMD:"):
            continue
        modes = str(mm.loc[i, "multimodes"]).split("-")
        cs = list(mm.geometry[i].coords)
        changed = False
        for pos in (0, -1):
            key = (round(cs[pos][0], 6), round(cs[pos][1], 6))
            if any(key in nodes[m] for m in modes):
                continue
            best, bm = None, None
            for m in modes:
                cand = min(nodes[m], key=lambda x: hav(x, cs[pos]))
                d = hav(cand, cs[pos])
                if best is None or d < best[1]:
                    best, bm = (cand, d), m
            if best and best[1] < 5.0:
                cs[pos] = best[0]
                changed = True
                print(f"  re-anchored {name!r} end -> {bm} node "
                      f"({best[0][0]:.6f},{best[0][1]:.6f}), {best[1]*1000:.0f} m")
        if changed:
            mm.loc[i, mm.geometry.name] = LineString(cs)
            d_m = hav(cs[0], cs[-1]) * 1000
            mm.loc[i, "distance_m"] = round(d_m, 1)
            if "km" in mm.columns:
                mm.loc[i, "km"] = round(d_m / 1000, 3)
            n_fix += 1
    if n_fix:
        mm.to_file(T / "multimodal.gpkg", layer="multimodal", driver="GPKG")
    print(f"multimodal: {n_fix} connectors re-anchored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
