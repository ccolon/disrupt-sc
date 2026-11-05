"""Add the paper's flood footprint (v3) to the v2 Cambodia network as the road attribute `flood_v3` (5 Nov 2026).

The v2 network (disrupt-sc-data/Cambodia/Transport/transport.gpkg, 9 Jul 2026) carries the v4 footprint in
`flood_disruption` (Saigon 6, Mekong 7, Tonle Sap 20 edges). The paper's runs of 2025 used v3,
Transport/roads_edges_with_disruptions_v3.geojson of the cluster's Cambodia data (CLIMADA, GloFAS forecast of
27 Sep 2023, 5-day lead, ensemble maximum): 3 / 8 / 25 edges, as the run logs say ("3 / 8 / 25 items
disrupted"). Both files describe the same 2,145 road edges; the join is on `id` and the script refuses to write
if the ids, the geometries' lengths (`km`) or the expected counts do not match. `flood_disruption` is left as it
is; the scenarios name the attribute (scenarios.FOOTPRINTS).

Usage:
    python studies/cambodia/add_flood_v3.py --v3 PATH/roads_edges_with_disruptions_v3.geojson [--write]
(without --write: report only)
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pyogrio

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scenarios import BASIN_LABEL, BASIN_ORDER, FOOTPRINTS  # noqa: E402

DATA = HERE.parents[1].parent / "disrupt-sc-data" / "Cambodia" / "Transport"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v3", type=Path, required=True)
    ap.add_argument("--gpkg", type=Path, default=DATA / "transport.gpkg")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    v3 = gpd.read_file(a.v3)
    layers = [l[0] for l in pyogrio.list_layers(a.gpkg)]
    roads = gpd.read_file(a.gpkg, layer="roads")
    print(f"v3: {len(v3)} edges; gpkg roads: {len(roads)} edges; layers {layers}")
    if set(v3["id"]) != set(roads["id"]) or len(v3) != len(roads):
        raise SystemExit("the v3 file and the gpkg roads layer do not hold the same edge ids")
    km = roads.set_index("id")["km"].sub(v3.set_index("id")["km"]).abs().max()
    if not np.isfinite(km) or km > 1e-6:
        raise SystemExit(f"edge lengths differ between the two files (max |dkm| = {km})")
    lab = v3.set_index("id")["flood_disruption"]
    roads["flood_v3"] = roads["id"].map(lab)
    counts = {b: int((roads["flood_v3"] == BASIN_LABEL[b]).sum()) for b in BASIN_ORDER}
    print(f"flood_v3 counts: {counts}; values: {sorted(roads['flood_v3'].dropna().unique())}")
    if counts != FOOTPRINTS["v3"]["edges"]:
        raise SystemExit(f"expected {FOOTPRINTS['v3']['edges']}")
    if not a.write:
        print("report only (--write to update the gpkg)")
        return
    backup = a.gpkg.with_name(a.gpkg.stem + "_before_flood_v3.gpkg")
    if not backup.exists():
        shutil.copy(a.gpkg, backup)
    pyogrio.write_dataframe(roads, a.gpkg, layer="roads", driver="GPKG")
    after = [l[0] for l in pyogrio.list_layers(a.gpkg)]
    if sorted(after) != sorted(layers):
        shutil.copy(backup, a.gpkg)
        raise SystemExit(f"layers changed {layers} -> {after}: gpkg restored from the backup")
    print(f"written: {a.gpkg} (roads layer, + flood_v3); backup {backup.name}")


if __name__ == "__main__":
    main()
