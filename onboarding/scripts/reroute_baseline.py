"""Routing-only calibration harness: re-route the cached supply chain with the
CURRENT logistics parameters and write the baseline edge flows, without
rebuilding agents, re-solving the equilibrium, stepping or exporting.

Why it is exact: for a given supply chain the baseline flows are a function
of the network and the cost parameters only — origin/destination nodes,
tons and cargo types of every link are fixed by the build (supplier choice
uses network distance, not cost). So mode-cost calibration can loop here
(≈ 2 min on the EU scope) and confirm with a full run at the end.

Steps
  1. materialise the routable links once per supply chain: load the cached
     sc_network (validated by its stage fingerprint), run set_initial_conditions
     (the one 5-min step, cached afterwards as a parquet keyed by the sc hash),
     collect (origin, destination, cargo_type, tons, value, product_type, category);
  2. build the transport network from the gpkg with the config's logistics;
  3. scipy Dijkstra per cargo type for every (source, needed destinations);
  4. accumulate tons/value per edge (per cargo type and product type, like
     compute_flow_per_segment) and write
     output/<Scope>/<name>/transport_edges_with_flows_0.geojson, which
     flow_checks.py and eurostat_mode_targets.py --compare read unchanged.

Usage:
    python reroute_baseline.py <Scope> [--name reroute_v6] [--rebuild-links]
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

sys.path.insert(0, str(locate.find_repo_root() / "src"))

from disruptsc.config import build_params, load_config, setup_logging  # noqa: E402
from disruptsc.init_pipeline.routing import _cargo_subgraph, _collect_link_specs, shortest_paths_for  # noqa: E402
from disruptsc.init_pipeline.transport import build_transport_network  # noqa: E402
from disruptsc.run_pipeline.cache import get_cache_dir, load_cached_sc_network  # noqa: E402
from disruptsc.run_pipeline.fingerprint import build_stage_fingerprint  # noqa: E402
from disruptsc.run_pipeline.simulate import set_initial_conditions  # noqa: E402


def materialise_links(scope: str, config: dict, tp, sp, rebuild: bool,
                      trust_cache: bool = False) -> pd.DataFrame:
    """(origin, destination, cargo_type, tons, value, product_type, category) per routable link."""
    sc_fp = build_stage_fingerprint(config, "sc_network")
    cache = get_cache_dir() / f"{scope}_reroute_links_{sc_fp['hash'][:10]}.parquet"
    if cache.exists() and not rebuild:
        df = pd.read_parquet(cache)
        logging.info(f"links: {len(df):,} from {cache.name}")
        return df
    t0 = time.time()
    # --trust-cache: skip the stage-fingerprint check (caches written before the
    # transport-key split carry a hash the new scheme cannot reproduce)
    sc_network, firms, households, countries = load_cached_sc_network(
        scope=scope, stage_fp=None if trust_cache else sc_fp)
    logging.info(f"cached supply chain loaded ({time.time() - t0:.0f} s); solving the equilibrium once")
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)
    specs = _collect_link_specs(sc_network, tp)
    df = pd.DataFrame({
        "origin": [s["origin"] for s in specs],
        "destination": [s["destination"] for s in specs],
        "cargo_type": [s["cargo_type"] for s in specs],
        "tons": [float(s["tons"]) for s in specs],
        "value": [float(s["link"].order) for s in specs],
        "product_type": [s["link"].product_type for s in specs],
        "category": [s["link"].category for s in specs],
    })
    df.to_parquet(cache, index=False)
    logging.info(f"links: {len(df):,} materialised in {time.time() - t0:.0f} s -> {cache.name}")
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scope")
    ap.add_argument("--name", default=None, help="output subfolder (default reroute_<timestamp>)")
    ap.add_argument("--rebuild-links", action="store_true")
    ap.add_argument("--trust-cache", action="store_true",
                    help="load the sc_network cache without the stage-fingerprint check "
                         "(caches written before the transport-key split)")
    ap.add_argument("--seed", type=int, default=None,
                    help="the seed the full run was launched with (disruptsc <scope> --seed N): the "
                         "supply chain and its cache fingerprint depend on it")
    args = ap.parse_args()
    setup_logging("info")
    scope = args.scope
    config = load_config(scope)
    if args.seed is not None:
        config["seed"] = args.seed
    tp, sp, ap_, lp = build_params(config)
    if tp.capacity_constraint_enabled:
        raise SystemExit("reroute_baseline reproduces the unconstrained assignment only")

    links = materialise_links(scope, config, tp, sp, args.rebuild_links, args.trust_cache)

    t0 = time.time()
    fp = config.get("filepaths", {})
    tn, te, tnodes = build_transport_network(
        config.get("transport_modes", ["roads"]), fp, config.get("logistics", {}),
        sp.time_resolution, capacity_overrides=config.get("transport_capacity_overrides"),
        default_transport_capacity=config.get("default_transport_capacity"),
        use_cargo_types=tp.use_cargo_types)
    tn.shrink_cargo_types_to(set(links["cargo_type"].unique()))
    logging.info(f"transport network built with the current logistics ({time.time() - t0:.0f} s)")

    # routes per (cargo, origin, destination) group; value split by product
    # type and category rides along so the flow_<pt> / flow_<category>
    # columns of the full export exist too (Kaub composition checks)
    t0 = time.time()
    groups = links.groupby(["cargo_type", "origin", "destination"], as_index=False).agg(
        tons=("tons", "sum"), value=("value", "sum"))
    pt_by_group = {k: dict(zip(g["product_type"], g["value"])) for k, g in
                   links.groupby(["cargo_type", "origin", "destination", "product_type"], as_index=False)["value"]
                   .sum().groupby(["cargo_type", "origin", "destination"])}
    cat_by_group = {k: dict(zip(g["category"], g["value"])) for k, g in
                    links.groupby(["cargo_type", "origin", "destination", "category"], as_index=False)["value"]
                    .sum().groupby(["cargo_type", "origin", "destination"])}
    edge_id = {}
    for u, v, d in tn.edges(data=True):
        edge_id[(u, v)] = d["id"]; edge_id[(v, u)] = d["id"]
    edge_tons, edge_val = defaultdict(float), defaultdict(float)
    edge_ct_tons, edge_ct_val = defaultdict(float), defaultdict(float)
    edge_extra = defaultdict(float)       # (eid, "flow_<pt>" | "flow_<category>") -> value
    unreachable = 0
    for ct, g in groups.groupby("cargo_type"):
        weight = f"cost_per_ton_{ct}"
        sub = _cargo_subgraph(tn, weight)
        dest_by_source = defaultdict(set)
        for o, dst in zip(g["origin"], g["destination"]):
            dest_by_source[int(o)].add(int(dst))
        paths = shortest_paths_for(sub, weight, dict(dest_by_source))
        for o, dst, tons, val in zip(g["origin"], g["destination"], g["tons"], g["value"]):
            path = paths.get((int(o), int(dst)))
            if path is None:
                unreachable += 1
                continue
            key = (ct, o, dst)
            pts, cats = pt_by_group.get(key, {}), cat_by_group.get(key, {})
            for a, b in zip(path[:-1], path[1:]):
                eid = edge_id[(a, b)]
                edge_tons[eid] += tons; edge_val[eid] += val
                edge_ct_tons[(eid, ct)] += tons; edge_ct_val[(eid, ct)] += val
                for pt, pv in pts.items():
                    edge_extra[(eid, f"flow_{pt}")] += pv
                for cat, cv in cats.items():
                    edge_extra[(eid, f"flow_{cat}")] += cv
    logging.info(f"routed {len(groups):,} OD-cargo groups ({unreachable} unreachable) in {time.time() - t0:.0f} s")

    cargo_types = sorted(set(links["cargo_type"]))
    rows = []
    for eid in te["id"]:
        row = {"id": eid, "flow_total": edge_val.get(eid, 0.0), "flow_total_tons": edge_tons.get(eid, 0.0)}
        for ct in cargo_types:
            if (eid, ct) in edge_ct_tons:
                row[f"tons_{ct}"] = edge_ct_tons[(eid, ct)]
                row[f"usd_{ct}"] = edge_ct_val[(eid, ct)]
        rows.append(row)
    flows = pd.DataFrame(rows)
    if edge_extra:
        extra = pd.Series(edge_extra).unstack(level=1).fillna(0.0)
        extra.index.name = "id"
        flows = flows.merge(extra.reset_index(), on="id", how="left")
    out_dir = locate.find_repo_root() / "output" / scope / (args.name or f"reroute_{time.strftime('%Y%m%d_%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    merged = te.drop(columns=[c for c in ("node_tuple",) if c in te.columns]).merge(flows, on="id", how="left")
    merged.to_file(out_dir / "transport_edges_with_flows_0.geojson", driver="GeoJSON", index=False)

    inland = merged[merged["type"].isin(["roads", "railways", "waterways"])].copy()
    inland["tkm"] = inland["flow_total_tons"] * inland["km"]
    tot = inland["tkm"].sum()
    shares = {m: 100 * inland.loc[inland["type"] == m, "tkm"].sum() / tot for m in ("roads", "railways", "waterways")}
    print(f"\nwritten {out_dir}")
    print(f"inland tkm split (period): roads {shares['roads']:.1f} / rail {shares['railways']:.1f} / IWW {shares['waterways']:.1f}")
    for ct in sorted(set(links["cargo_type"])):
        col = f"tons_{ct}"
        if col not in inland.columns:
            continue
        ctkm = inland[col].fillna(0) * inland["km"]
        t = ctkm.sum()
        if t > 0:
            print(f"  {ct:12s}: roads {100*ctkm[inland['type']=='roads'].sum()/t:.1f} / rail "
                  f"{100*ctkm[inland['type']=='railways'].sum()/t:.1f} / IWW {100*ctkm[inland['type']=='waterways'].sum()/t:.1f}")
    print("next: python studies/rhine2026/flow_checks.py --run", out_dir.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
