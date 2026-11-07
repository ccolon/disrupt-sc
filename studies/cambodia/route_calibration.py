"""Route-split calibration of the Cambodia gateways (7 Nov 2026): re-route one seed's cached supply chain with the
paper configuration and overrides, without stepping, and compare the gateway split with the 2015 anchors.

Same method as onboarding/scripts/reroute_baseline.py (exact for the unconstrained assignment: the supply chain fixes
origins, destinations, tons and cargo types; the logistics parameters only choose the routes), but with the paper's
configuration (run_cambodia.load_paper_config, never the machine's user_defined_Cambodia.yaml: KI-52) and a gateway
report instead of a geojson. The capacity gate is not emulated: the loads of the capacitated edges are printed
against their capacities, and the gated split is confirmed with a full run.

Anchors (Paper_Cambodia/pipeline/validation/logistics2016_flows.md; JICA 2016 brochure, GDCE 2015):
  laden containers by gateway (TEU, imports / exports): Sihanoukville 167k / 122k, Phnom Penh port by Mekong barge
  45k / 59k, Bavet - Moc Bai 70k / 24k, Poipet 10k / 2k (shares of the 499k: 57.9 / 20.8 / 18.8 / 2.4 %);
  import tonnes among the four gateways: SHV 49.5, Poipet 30.5, Phnom Penh port 13.3, Bavet 6.9 %.

Usage (after `run_cambodia.py --setup --seed 1 --cache-dir cam_sea_s1`):
    python studies/cambodia/route_calibration.py --seed 1 --cache-dir cam_sea_s1 \
        --set logistics.basic_cost.waterways=0.074 [--set ...] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "onboarding" / "scripts"))

from run_cambodia import SCOPE, apply_set, load_paper_config               # noqa: E402
from reroute_baseline import materialise_links                             # noqa: E402
from disruptsc.config import build_params, setup_logging                   # noqa: E402
from disruptsc.init_pipeline.routing import _cargo_subgraph, shortest_paths_for  # noqa: E402
from disruptsc.init_pipeline.transport import build_transport_network      # noqa: E402
from disruptsc.run_pipeline.cache import setup_cache_dir                   # noqa: E402

DAYS = 365
TEU_2015 = {"Sihanoukville": (167, 122), "Mekong barge": (45, 59), "Bavet": (70, 24), "Poipet": (10, 2)}
IMPORT_T_2015 = {"Sihanoukville": 37.2, "Poipet": 22.9, "Mekong barge": 10.0, "Bavet": 5.2}   # % of import tonnes


def gateways(te):
    """Gateway name -> edge ids (each international shipment crosses one edge of its gateway)."""
    def ids(mask):
        return set(te.loc[mask, "id"])
    name = te["name"].astype(str)
    special = te["special"].astype(str)
    port = te["port_name"].astype(str) if "port_name" in te.columns else name * 0
    g = {
        "Sihanoukville": ids(port == "Sihanoukville"),
        "Mekong barge": ids(name == "mekong_border"),
        "Bavet": ids(name == "bavet_border_crossing"),
        "Poipet": ids(name == "poipet_border_crossing"),
        "NR7 Laos": ids(name == "nr7_laos_border"),
        "other road borders": ids((te["type"] == "roads") & special.str.contains("border|custom|international")
                                  & ~name.isin(["bavet_border_crossing", "poipet_border_crossing", "nr7_laos_border"])),
    }
    detail = {"HCMC sea connector": ids(port == "HoChiMinh"), "Cai Mep barge connector": ids(port == "CaiMep"),
              "Phnom Penh river connectors": ids(port == "PhnomPenh"), "rail PP-SHV": ids(name == "pp_sihanoukville")}
    return g, detail


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--trust-cache", action="store_true")
    ap.add_argument("--rebuild-links", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    setup_logging("warning" if a.quiet else "info")

    config = load_paper_config()
    for item in a.set:
        apply_set(config, item)
    config.update(seed=a.seed, simulation_type="initial_state", t_final=1, disruptions=[], export_files=False)
    caps = config.get("transport_capacity_overrides") or {}
    config["capacity_constraint"] = False            # the harness routes unconstrained; loads vs caps are printed
    setup_cache_dir(a.cache_dir or f"cam_s{a.seed}")
    tp, sp, _, _ = build_params(config)
    links = materialise_links(SCOPE, config, tp, sp, a.rebuild_links, a.trust_cache)
    links["dir"] = links["category"].astype(str).map(
        lambda c: "imp" if c.startswith("import") else ("exp" if c.startswith("export") else "dom"))

    t0 = time.time()
    tn, te, _ = build_transport_network(config["transport_modes"], config.get("filepaths", {}), config["logistics"],
                                        sp.time_resolution, capacity_overrides=caps or None,
                                        cargo_mode_eligibility=tp.cargo_mode_eligibility,
                                        use_cargo_types=tp.use_cargo_types)
    tn.shrink_cargo_types_to(set(links["cargo_type"].unique()))
    edge_id = {}
    for u, v, d in tn.edges(data=True):
        edge_id[(u, v)] = d["id"]
        edge_id[(v, u)] = d["id"]
    load = defaultdict(float)                         # (edge id, cargo, dir) -> tons per day
    groups = links.groupby(["cargo_type", "dir", "origin", "destination"], as_index=False)["tons"].sum()
    unreachable = 0
    for ct, g in groups.groupby("cargo_type"):
        weight = f"cost_per_ton_{ct}"
        sub = _cargo_subgraph(tn, weight)
        dests = defaultdict(set)
        for o, d in zip(g["origin"], g["destination"]):
            dests[int(o)].add(int(d))
        paths = shortest_paths_for(sub, weight, dict(dests))
        for dr, o, d, t in zip(g["dir"], g["origin"], g["destination"], g["tons"]):
            path = paths.get((int(o), int(d)))
            if path is None:
                unreachable += 1
                continue
            for x, y in zip(path[:-1], path[1:]):
                load[(edge_id[(x, y)], ct, dr)] += t
    logging.info(f"routed {len(groups):,} groups ({unreachable} unreachable) in {time.time() - t0:.0f} s")

    gw, detail = gateways(te)
    cargos = sorted(links["cargo_type"].unique())

    def sum_ids(idset, ct=None, dr=None):
        return sum(v for (e, c, d), v in load.items() if e in idset and (ct is None or c == ct) and (dr is None or d == dr))

    rows = {}
    for name, idset in {**gw, **detail}.items():
        rows[name] = {f"{ct}_{dr}": sum_ids(idset, ct, dr) * DAYS / 1e3 for ct in cargos for dr in ("imp", "exp", "dom")}
    tot_ct = {dr: sum(rows[n][f"container_{dr}"] for n in gw) for dr in ("imp", "exp")}
    tot_imp_t = sum(sum(rows[n][f"{ct}_imp"] for ct in cargos) for n in gw)
    teu_tot = sum(i + e for i, e in TEU_2015.values())
    print(f"\nseed {a.seed}; overrides {a.set}; {unreachable} unreachable groups")
    print(f"{'gateway':28s} {'cont imp':>9s} {'cont exp':>9s} {'bulk imp':>9s} {'bulk exp':>9s}  (kt/yr) | "
          f"cont share model / 2015 | import t share model / 2015")
    err = 0.0
    for name in gw:
        r = rows[name]
        bulk_i = sum(r[f"{ct}_imp"] for ct in cargos if ct != "container")
        bulk_e = sum(r[f"{ct}_exp"] for ct in cargos if ct != "container")
        cs = 100 * (r["container_imp"] + r["container_exp"]) / max(tot_ct["imp"] + tot_ct["exp"], 1e-9)
        ts = 100 * sum(r[f"{ct}_imp"] for ct in cargos) / max(tot_imp_t, 1e-9)
        teu = TEU_2015.get(name)
        cs0 = 100 * sum(teu) / teu_tot if teu else 0.0
        err += abs(cs - cs0)
        ts0 = IMPORT_T_2015.get(name)
        print(f"{name:28s} {r['container_imp']:9.0f} {r['container_exp']:9.0f} {bulk_i:9.0f} {bulk_e:9.0f}        | "
              f"{cs:5.1f} / {cs0:4.1f}              | {ts:5.1f} / " + (f"{ts0:4.1f}" if ts0 else "  - "))
    for name in detail:
        r = rows[name]
        print(f"  {name:26s} {r['container_imp']:9.0f} {r['container_exp']:9.0f} "
              f"{sum(r[f'{ct}_imp'] for ct in cargos if ct != 'container'):9.0f} "
              f"{sum(r[f'{ct}_exp'] for ct in cargos if ct != 'container'):9.0f}")
    print(f"container share error (sum |model - 2015|, pp): {err:.1f}")
    rail = rows["rail PP-SHV"]["container_imp"] + rows["rail PP-SHV"]["container_exp"]
    shv = rows["Sihanoukville"]["container_imp"] + rows["Sihanoukville"]["container_exp"]
    print(f"rail share of Sihanoukville containers: {100 * rail / max(shv, 1e-9):.1f} % (2015: 17k of 289k TEU, 5.9 %)")
    if caps:
        print("capacitated edges (t/day, unconstrained load vs capacity):")
        for nm, cap in caps.items():
            ids_ = set(te.loc[te["name"] == nm, "id"])
            ld = sum_ids(ids_)
            capv = cap if isinstance(cap, (int, float)) else sum(cap.values())
            print(f"  {nm:24s} {ld:9.0f} / {capv:9.0f}  ({100 * ld / capv:.0f} %)")
    if a.json:
        a.json.write_text(json.dumps({"seed": a.seed, "set": a.set, "rows": rows, "err": err}, indent=1))


if __name__ == "__main__":
    main()
