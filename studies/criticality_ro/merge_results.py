# -*- coding: utf-8 -*-
"""Merge the Romania criticality chunk results; rank; build the map layer.

Reads every output/Romania/criticality/<prefix>_chunk_*/criticality_results.csv,
joins to the reference run's edge table, and writes into
output/Romania/criticality/<prefix>_merged/:
  * criticality_ranked.csv   - one row per edge: id, mode, name, class, km,
    baseline tons, household_loss, country_loss, total_loss (mUSD per event),
    loss_per_kt (irreplaceability), loss_per_km
  * criticality_map.geojson  - the same joined to geometries, for QGIS
  * tier2_top150.yaml        - (tier1 only) the Tier-2 chunk config: top 150
    edges by total loss, duration 4, run_id t2_top150

Usage: python studies/criticality_ro/merge_results.py [--prefix t1]
       python studies/criticality_ro/merge_results.py --prefix t2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="t1")
    ap.add_argument("--top", type=int, default=150)
    args = ap.parse_args()
    # chunk CSVs: the gathered/committed copies (laptop after git pull) take
    # precedence; fall back to the live run outputs (on the cluster)
    gathered = sorted((HERE / "results" / f"{args.prefix}_chunks").glob("*.csv"))
    crit_dir = REPO / "output" / "Romania" / "criticality"
    live = [p for p in sorted(crit_dir.glob(f"{args.prefix}_*/criticality_results.csv"))
            if "_merged" not in p.parent.name]
    parts = gathered or live
    if not parts:
        raise SystemExit(f"no {args.prefix} chunk results in "
                         f"{HERE / 'results'} nor {crit_dir}")
    df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
    df = df.drop_duplicates(subset="edge_id", keep="last")
    print(f"{len(parts)} chunk files, {len(df)} unique edges")

    # committed slim copy of the reference run's edge table - makes the
    # merge runnable on the cluster with nothing but the git checkout
    exp = HERE / "reference_edges.geojson"
    edges = gpd.read_file(exp)[["id", "type", "name", "class", "km",
                                "flow_total_tons", "geometry"]]
    m = edges.merge(df, left_on="id", right_on="edge_id", how="inner")
    for c in ("household_loss", "country_loss"):
        m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0.0)
        # The raw columns carry a large constant offset (the no-disruption
        # reference). Estimate it as the MEDIAN OF THE LOWEST QUARTILE:
        # robust both to below-reference Braess edges (v24 t1: one Bucharest
        # edge read ~13.5 mUSD BELOW reference and, as the minimum, inflated
        # every edge) and to selected populations like Tier 2's top-150,
        # where the global median is NOT the reference (only the weak tail
        # sits on it; t2 check: tail of 36 t1-noise edges clustered within
        # 1.5 mUSD). Small negatives clip to 0.
        q25 = m[c].quantile(0.25)
        ref = m.loc[m[c] <= q25, c].median()
        m[c] = (m[c] - ref).clip(lower=0.0)
    m["total_loss"] = m["household_loss"] + m["country_loss"]
    m["loss_per_kt"] = m["total_loss"] / (m["flow_total_tons"] / 1000).clip(lower=1e-9)
    m["loss_per_km"] = m["total_loss"] / m["km"].clip(lower=1e-3)
    m = m.sort_values("total_loss", ascending=False).reset_index(drop=True)

    out = HERE / "results" / f"{args.prefix}_merged"
    out.mkdir(parents=True, exist_ok=True)
    m.drop(columns="geometry").to_csv(out / "criticality_ranked.csv", index=False)
    gpd.GeoDataFrame(m, crs=edges.crs).to_file(out / "criticality_map.geojson",
                                               driver="GeoJSON")
    print(f"written {out}/criticality_ranked.csv + criticality_map.geojson")
    print("\ntop 10 by total loss (mUSD per closure event; t1 = 1 week, t2 = 4 weeks):")
    print(m[["id", "type", "name", "flow_total_tons", "household_loss",
             "country_loss", "total_loss"]].head(10).to_string(index=False))

    if args.prefix == "t1":
        top = m.head(args.top)["id"].astype(int).tolist()
        n_chunks = 15
        for old_f in (HERE / "chunks").glob("t2_chunk_*.yaml"):
            old_f.unlink()
        parts: list[list[int]] = [[] for _ in range(n_chunks)]
        for k, eid in enumerate(top):
            parts[k % n_chunks].append(eid)
        for k, ids in enumerate(parts):
            name = f"t2_chunk_{k:02d}"
            with open(HERE / "chunks" / f"{name}.yaml", "w") as f:
                f.write("simulation_type: criticality\n")
                f.write("export_files: False\n")
                f.write("t_final: 6\n")
                f.write("criticality:\n")
                f.write("  duration: 4\n")
                f.write(f"  run_id: {name}\n")
                f.write("  attribute: id\n")
                f.write("  edges: [" + ", ".join(str(i) for i in ids) + "]\n")
        print(f"\nTier-2 configs: {n_chunks} chunks x ~{len(top) // n_chunks} "
              f"edges (duration 4, t_final 6) - commit, git pull on the "
              f"cluster, launch with --tier2")
    return 0


if __name__ == "__main__":
    main()
