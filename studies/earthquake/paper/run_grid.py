"""Sensitivity + Monte-Carlo sweep runner.

flow_coverage / nb_suppliers_per_input / seed all change the supply-chain BUILD, so
they are CLI args; the launcher fans them out (one build per combo per SEED). Within
each build, the runtime parameters (utilization_rate, reconstruction_public_share,
reconstruction_target_time) are swept in-process. For each (seed x runtime combo) the
household consumption loss and production-side VA loss are computed in-process (no
firm_data export) and appended as one row to --out; aggregating across seeds (see
combine.py) gives the Monte-Carlo mean/spread.

CLI:
    python run_grid.py --flow-coverage 0.6 --nb-suppliers 2 --t-final 6 \
        --seeds 0-49 --utils 0.6,0.8,1.0 --public-shares 0.0,0.8 --target-times 730 \
        --out studies/earthquake/paper/_out/sensitivity_losses.csv
"""
from __future__ import annotations

import argparse
import logging
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, build_params, setup_logging          # noqa: E402
from disruptsc.init_pipeline.transport import build_transport_network          # noqa: E402
from disruptsc.init_pipeline.load_data import (                                # noqa: E402
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors)
from disruptsc.init_pipeline.agents import (                                   # noqa: E402
    create_firm_table, create_firms, load_tech_coefs, load_input_criticality,
    load_inventories, configure_household_inventories, create_household_table,
    create_households, create_countries)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network    # noqa: E402
import disruptsc.run_pipeline.simulate as S                                    # noqa: E402
from disruptsc.run_pipeline.simulate import run_disruption, set_initial_conditions  # noqa: E402

DAYS_PER_STEP = {"day": 1, "week": 7, "month": 30, "year": 365}


def _floats(s): return [float(x) for x in str(s).split(",")]


def _bools(s): return [str(x).strip().lower() in ("true", "1", "yes", "on") for x in str(s).split(",")]


def _seeds(s):
    s = str(s)
    if "-" in s and "," not in s:
        a, b = s.split("-"); return list(range(int(a), int(b) + 1))
    return [int(x) for x in s.split(",")]


def build_agents(common, ap_, sp, tp, lp, seed):
    """Fresh agents + seeded supply-chain network for one Monte-Carlo seed."""
    firms = create_firms(common["firm_table"], ap_)
    load_tech_coefs(firms, common["mrio"], common["selection"])
    if common.get("crit_df") is not None:
        load_input_criticality(firms, common["crit_df"])
    load_inventories(firms, ap_.inventory_duration_targets, sp.time_resolution, common["sector_table"])
    households = create_households(common["household_table"], common["consumption"])
    configure_household_inventories(households, ap_.enable_household_inventories, ap_.inventory_duration_targets,
                                    ap_.inventory_restoration_time, sp.time_resolution, common["sector_table"])
    countries = create_countries(common["mrio"], common["tnodes"], common["countries_path"], common["usd_per_ton"],
                                 sp.time_resolution, ap_, common["selection"], transport_edges=common["te"],
                                 countries_no_transport=tp.countries_no_transport)
    random.seed(seed); np.random.seed(seed)
    sc = build_supply_chain_network(firms, households, countries, common["mrio"], common["sector_table"],
                                    ap_.nb_suppliers_per_input, ap_.weight_localization_firm,
                                    ap_.weight_localization_household, common["cargo_map"], common["tn"])
    set_initial_conditions(sc, firms, households, countries, tp, sp)

    def _va(f):
        ef = getattr(f, "eq_finance", None) or {}
        s = ef.get("sales", 0.0); c = ef.get("costs", {})
        return (s - c.get("input", 0.0) - c.get("transport", 0.0)) / s if s > 1e-12 else 0.0
    firm_va = {pid: _va(f) for pid, f in firms.items()}
    return sc, firms, households, countries, firm_va


def main():
    ap = argparse.ArgumentParser(description="Earthquake sensitivity + Monte-Carlo sweep")
    ap.add_argument("--flow-coverage", type=float, default=0.6)
    ap.add_argument("--nb-suppliers", type=int, default=2)
    ap.add_argument("--t-final", type=int, default=13)
    ap.add_argument("--seeds", type=_seeds, default=None, help="explicit seeds, e.g. 0-9 or 0,1,2")
    ap.add_argument("--n-seeds", type=int, default=None, help="convenience: seeds 0..n-1 (e.g. 10)")
    # swept levels
    ap.add_argument("--utils", type=_floats, default=[0.6, 0.8, 1.0])
    ap.add_argument("--recon", type=_bools, default=[True, False], help="reconstruction on/off, e.g. true,false")
    ap.add_argument("--public-shares", type=_floats, default=[0.0, 0.8])
    ap.add_argument("--target-times", type=_floats, default=[365.0, 730.0])
    ap.add_argument("--recon-lags", type=_floats, default=[30.0, 60.0, 90.0], help="reconstruction lag (DAYS)")
    ap.add_argument("--crit-thresholds", type=_floats, default=[0.0, 0.02, 0.05],
                    help="critical_input_threshold: materiality floor gating the IHS matrix "
                         "(0 = pure matrix, does not saturate)")
    # strategy: OAT (one-at-a-time vs baseline) or full factorial
    ap.add_argument("--oat", action="store_true", help="one-at-a-time from baseline (default: full factorial)")
    ap.add_argument("--oat-tag", default="", help="oat_param label for these rows (build-param variation jobs)")
    ap.add_argument("--util-base", type=float, default=0.8)
    ap.add_argument("--recon-base", type=lambda s: str(s).lower() in ("true", "1", "yes", "on"), default=True)
    ap.add_argument("--public-base", type=float, default=0.8)
    ap.add_argument("--target-base", type=float, default=730.0)
    ap.add_argument("--lag-base", type=float, default=60.0)
    ap.add_argument("--crit-base", type=float, default=0.02, help="baseline materiality floor")
    ap.add_argument("--criticality", type=Path, default=None,
                    help="path to the input-criticality matrix CSV (overrides config filepaths.input_criticality)")
    ap.add_argument("--shock", type=Path, default=None,
                    help="path to the capital-destruction shock CSV (overrides config disruptions[0].file)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    seeds = args.seeds if args.seeds is not None else (
        list(range(args.n_seeds)) if args.n_seeds is not None else [0])

    # runtime configs to run within each build: (oat_param_label, {util,recon,public,target,lag})
    base = dict(util=args.util_base, recon=args.recon_base, public=args.public_base,
                target=args.target_base, lag=args.lag_base, crit=args.crit_base)
    RT = [("utilization_rate", "util", args.utils), ("reconstruction_market", "recon", args.recon),
          ("reconstruction_public_share", "public", args.public_shares),
          ("reconstruction_target_time", "target", args.target_times),
          ("reconstruction_lag", "lag", args.recon_lags),
          ("critical_input_threshold", "crit", args.crit_thresholds)]
    if args.oat:
        run_configs = [("baseline", dict(base))]
        for name, key, levels in RT:
            for v in levels:
                if v != base[key]:
                    c = dict(base); c[key] = v; run_configs.append((name, c))
    else:                                                  # full factorial (dedupe recon=False)
        run_configs = []
        for u in args.utils:
            for r in args.recon:
                inner = ([(p, t, lg) for p in args.public_shares for t in args.target_times for lg in args.recon_lags]
                         if r else [(args.public_base, args.target_base, args.lag_base)])
                for p, t, lg in inner:
                    run_configs.append((args.oat_tag, dict(util=u, recon=r, public=p, target=t, lag=lg,
                                                           crit=args.crit_base)))

    setup_logging("info")
    cfg = load_config("EcuadorEQ")
    cfg["t_final"] = args.t_final
    cfg["rationing_mode"] = "equal"
    cfg["flow_coverage"] = args.flow_coverage
    cfg["nb_suppliers_per_input"] = args.nb_suppliers
    tp, sp, ap_, lp = build_params(cfg)
    fp = cfg["filepaths"]
    disr = cfg["disruptions"][0]
    if args.shock:                                          # override config's disruptions[0].file
        if not Path(args.shock).exists():
            raise SystemExit(f"--shock file not found: {args.shock}")
        disr = dict(disr, file=str(args.shock))
    ppy = 365.0 / DAYS_PER_STEP.get(sp.time_resolution, 30)
    print(f"flow_coverage={args.flow_coverage} nb_suppliers={args.nb_suppliers} t_final={sp.t_final} "
          f"seeds={seeds} recon={args.recon}")

    # ---- seed-independent build (once) ----
    tn, te, tnodes = build_transport_network(
        cfg.get("transport_modes", ["roads"]), fp, cfg.get("logistics", {}), sp.time_resolution,
        capacity_overrides=cfg.get("transport_capacity_overrides"),
        default_transport_capacity=cfg.get("default_transport_capacity"), use_cargo_types=tp.use_cargo_types)
    mrio = load_mrio(fp.get("mrio"), ap_.monetary_units_in_data)
    sector_table = load_sector_table(fp.get("sector_table"))
    usd_per_ton = load_usd_per_ton(sector_table)
    selection = filter_sectors(mrio, ap_.flow_coverage, ap_.sectors_to_include, ap_.sectors_to_exclude)
    firm_table = create_firm_table(mrio, sector_table, fp.get("firms_spatial"), fp.get("households_spatial"),
                                   usd_per_ton, tnodes, ap_, selection)
    household_table, consumption = create_household_table(mrio, fp.get("households_spatial"), tnodes, selection, ap_,
                                                          time_resolution=sp.time_resolution)
    cargo_map = lp.sector_to_cargo_type if tp.use_cargo_types else {"default": "any"}
    crit_path = args.criticality or fp.get("input_criticality")
    crit_df = pd.read_csv(crit_path, index_col=0) if crit_path and Path(crit_path).exists() else None
    if crit_df is None:
        print(f"WARNING: no criticality matrix at {crit_path} — running strict/proxy Leontief")
    common = dict(tn=tn, te=te, tnodes=tnodes, mrio=mrio, sector_table=sector_table, usd_per_ton=usd_per_ton,
                  selection=selection, firm_table=firm_table, household_table=household_table,
                  consumption=consumption, cargo_map=cargo_map, countries_path=fp.get("countries_spatial"),
                  crit_df=crit_df)

    # ---- one global trace (reads the current seed's firm_va) ----
    state = {"firm_va": {}}
    TRACE_VA, TRACE_HH = [], []
    _orig = S._run_one_time_step
    def traced(time_step, *a, **k):
        r = _orig(time_step, *a, **k)
        fs, hh = a[3], a[4]
        fv = state["firm_va"]
        TRACE_VA.append(sum(f.production * fv.get(pid, 0.0) for pid, f in fs.items()))
        TRACE_HH.append(sum(h.consumption_loss for h in hh.values()))
        return r
    S._run_one_time_step = traced

    rows = []
    for seed in seeds:
        print(f"[seed {seed}] building ...")
        sc, firms, households, countries, firm_va = build_agents(common, ap_, sp, tp, lp, seed)
        state["firm_va"] = firm_va
        for oat_param, rc in run_configs:
            for f in firms.values():
                f.utilization_rate = rc["util"]
                f.critical_input_threshold = rc["crit"]
            TRACE_VA.clear(); TRACE_HH.clear()
            d = dict(disr)
            d.update(reconstruction_market=rc["recon"], reconstruction_public_share=rc["public"],
                     reconstruction_target_time=rc["target"], reconstruction_lag=rc["lag"],
                     capital_input_mix={"CON": 0.7, "MAN": 0.2, "IMP": 0.1})
            logging.disable(logging.INFO)
            run_disruption(sc, tn, firms, households, countries, tp, sp, [d], te, firm_table, sp.t_final,
                           export_folder=None)
            logging.disable(logging.NOTSET)
            annual_gdp = TRACE_VA[0] * ppy
            gdp_loss = float(sum(TRACE_VA[0] - v for v in TRACE_VA[1:]))
            hh_loss = float(sum(TRACE_HH))
            rows.append({"seed": seed, "oat_param": oat_param, "flow_coverage": args.flow_coverage,
                         "nb_suppliers_per_input": args.nb_suppliers, "utilization_rate": rc["util"],
                         "reconstruction_market": rc["recon"], "reconstruction_public_share": rc["public"],
                         "reconstruction_target_time": rc["target"], "reconstruction_lag": rc["lag"],
                         "critical_input_threshold": rc["crit"],
                         "household_loss_pct_annual_gdp": round(100.0 * hh_loss / annual_gdp, 4),
                         "household_loss_mUSD": round(hh_loss, 2),
                         "gdp_loss_pct_annual_gdp": round(100.0 * gdp_loss / annual_gdp, 4)})
            print(f"    seed={seed} [{oat_param or 'grid'}] util={rc['util']} recon={rc['recon']} "
                  f"public={rc['public']} target={rc['target']} lag={rc['lag']}: "
                  f"hh {rows[-1]['household_loss_pct_annual_gdp']:.2f}% of GDP")

    df = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, mode="a", header=not args.out.exists(), index=False)
    print(f"\n-> appended {len(df)} rows ({len(seeds)} seeds) to {args.out}")


if __name__ == "__main__":
    main()
