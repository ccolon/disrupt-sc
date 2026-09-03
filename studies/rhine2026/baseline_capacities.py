"""Derive per-edge capacities for the scenario runs from a calibrated baseline.

Why: the Rhine scenario reduces the capacity of the Kaub edge week by week. For
that to matter, the substitutes must be finite too - DB Cargo could mobilise
~400-900 wagons (roughly 100 barges, a tenth of Rhine tonnage) and road haulage
was bound by drivers and tank equipment. Without capacities on rail and road,
the model would move the whole Rhine traffic onto them at zero friction.

Method: capacity_e = headroom_mode x baseline load_e (tons/day) for every rail,
road and waterway edge of the calibrated baseline run, floored so that unused
edges keep a small capacity. Rhine edges get the normal-year cross-section
capacities of scenarios/rhine_capacities.csv (the scenario scales them by the
weekly Kaub factor). Port connectors keep the Eurostat throughput capacities
already in the config; other connectors are left unconstrained.

The headroom factors are ASSUMPTIONS to be stated in the paper and swept
(rail 1.15 / 1.3 / 1.6; road 1.3 / 1.5 / 2.0).

Usage:
    python studies/rhine2026/baseline_capacities.py --run <output subfolder> \
        [--rail 1.3 --road 1.5 --iww 1.3 --floor-tpd 500] [--apply]
Writes disrupt-sc-data/EU/Transport/scenario_edge_capacities.csv (id, type,
name, baseline_tpd, capacity_tpd); run_rhine.py merges it into
transport_capacity_overrides for scenario runs only (the calibrated baseline
config stays untouched). With --apply, the edges are NAMED in transport.gpkg
(cap_<mode>_<id>, only where the name is empty) so that the overrides can
address them. Re-run the baseline after --apply (the network file changed)
before running scenarios.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT.parent / "disrupt-sc-data" / "EU"
HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--periods-per-year", type=float, default=52.0)
    ap.add_argument("--rail", type=float, default=1.3)
    ap.add_argument("--road", type=float, default=1.5)
    ap.add_argument("--iww", type=float, default=1.3, help="headroom for non-Rhine waterway edges")
    ap.add_argument("--floor-tpd", type=float, default=500.0)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    e = gpd.read_file(ROOT / "output" / "EU" / args.run / "transport_edges_with_flows_0.geojson")
    tons_col = next(c for c in e.columns if c in ("flow_total_tons", "flow_tons", "tons"))
    e["baseline_tpd"] = e[tons_col] * args.periods_per_year / 365.0
    inland = e[e["type"].isin(["roads", "railways", "waterways"])].copy()
    head = {"roads": args.road, "railways": args.rail, "waterways": args.iww}
    inland["capacity_tpd"] = [max(args.floor_tpd, b * head[m]) for b, m in zip(inland["baseline_tpd"], inland["type"])]

    # Rhine edges: normal-year cross-section capacities instead of baseline x headroom
    rh = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv").set_index("name")["tons_per_day"]
    is_rhine = inland["name"].astype(str).str.startswith("rhine")
    inland.loc[is_rhine, "capacity_tpd"] = inland.loc[is_rhine, "name"].map(rh).fillna(inland.loc[is_rhine, "capacity_tpd"])

    # names: keep existing (rhine_*, stitches...), otherwise cap_<mode>_<id>
    names = inland["name"].astype(str)
    blank = names.isin(["", "None", "nan"]) | inland["name"].isna()
    inland["cap_name"] = names.where(~blank, "cap_" + inland["type"].str[:4] + "_" + inland["id"].astype(int).astype(str))

    out = inland[["id", "type", "cap_name", "baseline_tpd", "capacity_tpd"]].rename(columns={"cap_name": "name"})
    out["baseline_tpd"] = out["baseline_tpd"].round(1)
    out["capacity_tpd"] = out["capacity_tpd"].round(0)
    out_path = DATA / "Transport" / "scenario_edge_capacities.csv"
    out.to_csv(out_path, index=False)
    summ = out.groupby("type").agg(edges=("id", "size"), baseline_Mt=("baseline_tpd", lambda s: s.sum() * 365 / 1e6),
                                   capacity_Mt=("capacity_tpd", lambda s: s.sum() * 365 / 1e6)).round(1)
    print(f"run {args.run}: {len(out)} inland edges -> {out_path}\n{summ.to_string()}")
    print(f"Rhine edges with cross-section capacities: {int(is_rhine.sum())}")
    if not args.apply:
        print("dry run (no --apply): network and config unchanged")
        return

    # 1. name the unnamed inland edges in transport.gpkg (layer per mode)
    gpkg = DATA / "Transport" / "transport.gpkg"
    changed = 0
    for mode in ("roads", "railways", "waterways"):
        layer = gpd.read_file(gpkg, layer=mode)
        sub = out[(out["type"] == mode)]
        # loader ids are offset per layer in load order (roads, railways, waterways, maritime):
        # recover the layer-local id from the run's transport_edges ids by position
        run_ids = e[e["type"] == mode].sort_values("id")["id"].to_numpy()
        if len(run_ids) != len(layer):
            raise SystemExit(f"{mode}: {len(layer)} edges in transport.gpkg vs {len(run_ids)} in the run - "
                             f"network changed since the run; rebuild the baseline first")
        id_map = dict(zip(run_ids, layer.index))
        for _, r in sub.iterrows():
            idx = id_map[int(r["id"])]
            cur = layer.at[idx, "name"] if "name" in layer.columns else None
            if cur in (None, "", "nan") or (isinstance(cur, float) and pd.isna(cur)):
                layer.at[idx, "name"] = r["name"]
                changed += 1
        layer.to_file(gpkg, layer=mode, driver="GPKG")
    print(f"named {changed} previously unnamed inland edges in {gpkg}; "
          f"re-run the baseline before scenario runs (network file changed)")


if __name__ == "__main__":
    main()
