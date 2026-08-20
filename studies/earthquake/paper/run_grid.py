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
from dataclasses import replace
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
    create_households, create_countries, add_representative_demand_agents)
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
    households = add_representative_demand_agents(households, common["mrio"], common["selection"],
                                                 ap_, sp.time_resolution)
    configure_household_inventories(households, ap_.enable_household_inventories, ap_.household_inventory_duration_targets,
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
    ap.add_argument("--nb-suppliers", type=float, default=2,
                    help="suppliers per input; fractional values in (1,2) are a stochastic 1-or-2 "
                         "mix (see _draw_nb_suppliers), which resolves the 1->2 cliff")
    ap.add_argument("--t-final", type=int, default=13)
    ap.add_argument("--seeds", type=_seeds, default=None, help="explicit seeds, e.g. 0-9 or 0,1,2")
    ap.add_argument("--n-seeds", type=int, default=None, help="convenience: seeds 0..n-1 (e.g. 10)")
    # swept levels
    ap.add_argument("--utils", type=_floats, default=[0.6, 0.8, 1.0])
    ap.add_argument("--recon", type=_bools, default=[True, False], help="reconstruction on/off, e.g. true,false")
    ap.add_argument("--public-shares", type=_floats, default=[0.0, 0.5, 0.8, 1.0])
    ap.add_argument("--target-times", type=_floats, default=[365.0, 730.0])
    ap.add_argument("--recon-lags", type=_floats, default=[30.0, 60.0, 90.0], help="reconstruction lag (DAYS)")
    ap.add_argument("--crit-thresholds", type=_floats, default=[0.0, 0.02, 0.05],
                    help="critical_input_threshold: materiality floor gating the IHS matrix "
                         "(0 = pure matrix, does not saturate)")
    # strategy: OAT (one-at-a-time vs baseline) or full factorial
    ap.add_argument("--oat", action="store_true", help="one-at-a-time from baseline (default: full factorial)")
    ap.add_argument("--oat-tag", default="", help="oat_param label for these rows (build-param variation jobs)")
    ap.add_argument("--util-base", type=float, default=0.8)
    ap.add_argument("--tau-base", type=float, default=None,
                    help="OAT base for time_to_activate_idle_capital (DAYS); defaults to the "
                         "config value. Set it explicitly from the launcher: the scope config is "
                         "gitignored, and a base at or below one time step is degenerate "
                         "(activation completes inside the step).")
    ap.add_argument("--recon-base", type=lambda s: str(s).lower() in ("true", "1", "yes", "on"), default=True)
    ap.add_argument("--public-base", type=float, default=0.8)
    ap.add_argument("--target-base", type=float, default=730.0)
    ap.add_argument("--lag-base", type=float, default=60.0)
    ap.add_argument("--crit-base", type=float, default=0.02, help="baseline materiality floor")
    # Inventory sensitivity: multiplicative scales (OAT, x1 = baseline) applied in-process
    # per config -- no rebuild (run_disruption re-inits inventory from the scaled targets).
    ap.add_argument("--firm-inv-scales", type=_floats, default=[0.5, 2.0],
                    help="multiply ALL firm input buffers by these factors")
    ap.add_argument("--hh-inv-scales", type=_floats, default=[0.5, 2.0],
                    help="multiply ALL household buffers by these factors")
    ap.add_argument("--type-buffer-days", type=_floats, default=[30.0, 90.0, 180.0],
                    help="ABSOLUTE buffer duration (DAYS) for each firm input type in turn -- "
                         "utility/agriculture/manufacturing/trade/transport/service, one OAT axis "
                         "per type. Levels below one time step are inert (see the note in main), "
                         "so 30 = no buffer beyond the mandatory step at monthly resolution")
    ap.add_argument("--restoration-scales", type=_floats, default=[0.5, 2.0],
                    help="multiply inventory_restoration_time (restock speed; firm+household)")
    # --- mechanism / severity axes (all applied in-process: no extra build) ---
    ap.add_argument("--recon-localities", type=_floats, default=[0.0, 0.4, 0.8, 1.0],
                    help="reconstruction_locality: 0 = national by size, 1 = fully damage-proximate")
    ap.add_argument("--tau-activate", type=_floats, default=[15.0, 30.0, 60.0, 90.0],
                    help="time_to_activate_idle_capital (DAYS): how fast spare capacity comes online")
    ap.add_argument("--capital-ratios", type=_floats, default=[2.0, 3.0, 4.0, 5.0],
                    help="capital_to_value_added_ratio: sets how big a FRACTION of capital a fixed "
                         "absolute destruction removes, i.e. effective shock severity")
    ap.add_argument("--shock-scales", type=_floats, default=[0.5, 1.0, 1.5, 2.0],
                    help="multiply every destroyed-capital cell (locations unchanged)")
    ap.add_argument("--price-thresholds", type=_floats, default=[2.0, 5.0],
                    help="price_increase_threshold")
    ap.add_argument("--adaptive-supplier", type=_bools, default=[True, False],
                    help="adaptive_supplier_weight on/off (supplier substitution)")
    ap.add_argument("--capacity-constrained", type=_bools, default=[True, False],
                    help="capacity_constrained_orders on/off")
    ap.add_argument("--adaptive-inv", type=_bools, default=[True, False],
                    help="adaptive_inventories on/off")
    ap.add_argument("--rationing-modes", type=lambda s: [x.strip() for x in str(s).split(",") if x.strip()],
                    default=["equal", "household_first"], help="rationing_mode levels")
    ap.add_argument("--canton-mmi", type=Path, default=None,
                    help="canton_mmi_bin.csv -> also record the MMI>7 vs control DiD per config "
                         "(the UQ validation target), turning the sweep into a calibration search")
    ap.add_argument("--criticality", type=Path, default=None,
                    help="path to the input-criticality matrix CSV (overrides config filepaths.input_criticality)")
    ap.add_argument("--shock", type=Path, default=None,
                    help="path to the capital-destruction shock CSV (overrides config disruptions[0].file)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    seeds = args.seeds if args.seeds is not None else (
        list(range(args.n_seeds)) if args.n_seeds is not None else [0])

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
    step_days = DAYS_PER_STEP.get(sp.time_resolution, 30)
    ppy = 365.0 / step_days
    print(f"flow_coverage={args.flow_coverage} nb_suppliers={args.nb_suppliers} t_final={sp.t_final} "
          f"seeds={seeds} recon={args.recon}")

    # ---- runtime configs run within each build: (oat_param_label, {param: value}) ----
    # Built here (not before build_params) because the per-type buffer axes are swept in
    # ABSOLUTE DAYS and need the config's own baseline day values as the OAT base level.
    # WHY DAYS, NOT SCALES: at monthly resolution a target below one step is inert --
    # Firm.initialize_inventory floors the initial stock at max(target, 1 step) and
    # plan_purchase only restocks when the target EXCEEDS current stock, so 3d / 5d / 15d all
    # behave exactly like 30d. Multiplicative scales around those bases therefore measured
    # nothing (they returned pure state-leakage noise). 30d = "no buffer beyond the mandatory
    # one step"; only levels above one step actually bite.
    FIRM_BUF_TYPES = ["utility", "agriculture", "manufacturing", "trade", "transport", "service"]
    _inv = ap_.inventory_duration_targets or {}
    _vals = _inv.get("values", {})
    _unit_days = {"day": 1, "week": 7, "month": 30, "year": 365}.get(_inv.get("unit", "day"), 1)
    base_days = {t: float(_vals.get(t, _vals.get("default", 30))) * _unit_days for t in FIRM_BUF_TYPES}
    # Mechanism/severity axes take their OAT base from the CONFIG (not a CLI default), so the
    # baseline config is by construction the one the paper runs.
    base_locality = disr.get("reconstruction_locality", 0.0)
    if isinstance(base_locality, dict):          # per-sector dict -> not a scalar OAT axis
        base_locality = None
    base = dict(util=args.util_base, recon=args.recon_base, public=args.public_base,
                target=args.target_base, lag=args.lag_base, crit=args.crit_base,
                firm_inv=1.0, hh_inv=1.0, restore=1.0,
                tau=float(args.tau_base if args.tau_base is not None
                          else sp.time_to_activate_idle_capital),
                capratio=float(ap_.capital_to_value_added_ratio),
                shock=float(disr.get("amount_scale", 1.0)),
                price_thr=float(tp.price_increase_threshold or 0.0),
                adasup=bool(sp.adaptive_supplier_weight),
                capcon=bool(sp.capacity_constrained_orders),
                adainv=bool(sp.adaptive_inventories),
                ration=str(tp.rationing_mode))
    if base_locality is not None:
        base["locality"] = float(base_locality)
    for _t in FIRM_BUF_TYPES:
        base[f"buf_{_t}"] = base_days[_t]
    RT = [("utilization_rate", "util", args.utils), ("reconstruction_market", "recon", args.recon),
          ("reconstruction_public_share", "public", args.public_shares),
          ("reconstruction_target_time", "target", args.target_times),
          ("reconstruction_lag", "lag", args.recon_lags),
          ("critical_input_threshold", "crit", args.crit_thresholds),
          ("firm_inventory_scale", "firm_inv", args.firm_inv_scales),
          ("household_inventory_scale", "hh_inv", args.hh_inv_scales),
          ("inventory_restoration_scale", "restore", args.restoration_scales),
          ("time_to_activate_idle_capital", "tau", args.tau_activate),
          ("capital_to_value_added_ratio", "capratio", args.capital_ratios),
          ("shock_scale", "shock", args.shock_scales),
          ("price_increase_threshold", "price_thr", args.price_thresholds),
          ("adaptive_supplier_weight", "adasup", args.adaptive_supplier),
          ("capacity_constrained_orders", "capcon", args.capacity_constrained),
          ("adaptive_inventories", "adainv", args.adaptive_inv),
          ("rationing_mode", "ration", args.rationing_modes)]
    if base_locality is not None:
        RT.append(("reconstruction_locality", "locality", args.recon_localities))
    RT += [(f"firm_{_t}_buffer_days", f"buf_{_t}", args.type_buffer_days) for _t in FIRM_BUF_TYPES]
    if args.oat:
        run_configs = [("baseline", dict(base))]
        for name, key, levels in RT:
            for v in levels:
                if v != base[key]:
                    c = dict(base); c[key] = v; run_configs.append((name, c))
        print(f"OAT: {len(run_configs)} configs/seed (per-type buffer bases, days: {base_days})")
    else:                                                  # full factorial (dedupe recon=False)
        run_configs = []
        for u in args.utils:
            for r in args.recon:
                inner = ([(p, t, lg) for p in args.public_shares for t in args.target_times for lg in args.recon_lags]
                         if r else [(args.public_base, args.target_base, args.lag_base)])
                for p, t, lg in inner:
                    # derive from `base` so every key exists (the mechanism/severity axes are
                    # held at their config values here); only the factorial dims are overridden
                    c = dict(base)
                    c.update(util=u, recon=r, public=p, target=t, lag=lg, crit=args.crit_base)
                    run_configs.append((args.oat_tag, c))

    # ---- seed-independent build (once) ----
    tn, te, tnodes = build_transport_network(
        cfg.get("transport_modes", ["roads"]), fp, cfg.get("logistics", {}), sp.time_resolution,
        capacity_overrides=cfg.get("transport_capacity_overrides"),
        default_transport_capacity=cfg.get("default_transport_capacity"), use_cargo_types=tp.use_cargo_types)
    mrio = load_mrio(fp.get("mrio"), ap_.monetary_units_in_data)
    sector_table = load_sector_table(fp.get("sector_table"))
    _type_of = sector_table.drop_duplicates("sector").set_index("sector")["type"].to_dict()
    def _input_type(region_sector):        # sector-type of an input, for per-type buffer scales
        t = _type_of.get(region_sector.split("_", 1)[-1], "default")
        return "service" if t == "services" else t  # normalise plural
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

    # ---- MMI-bin DiD (the UQ validation target) computed in-process, no firm_data export ----
    # Same definitions as analyze/uq_did.py: exclude ISIC K+O, tau = time_step-1, acute = tau 0-1,
    # recovery = tau 2-12, outcome vs each group's own t=0, DiD = bin_7p - control.
    DID_EXCLUDED = {"FIN", "SEG", "ADP"}
    DID_ACUTE, DID_RECOVERY = [0, 1], list(range(2, 13))
    canton2bin = {}
    if args.canton_mmi and Path(args.canton_mmi).exists():
        _cb = pd.read_csv(args.canton_mmi)
        canton2bin = dict(zip(_cb.subregion_canton, _cb.mmi_bin))
        print(f"MMI DiD enabled: {len(canton2bin)} cantons mapped from {args.canton_mmi}")
    elif args.canton_mmi:
        print(f"WARNING: --canton-mmi not found ({args.canton_mmi}); DiD columns will be blank")

    def _did_groups(firms):
        """pid -> 'bin_7p' | 'control' for the firms entering the DiD (others excluded)."""
        g = {}
        for pid, f in firms.items():
            if f.sector in DID_EXCLUDED:
                continue
            canton = (getattr(f, "subregions", None) or {}).get("subregion_canton")
            b = canton2bin.get(canton, "control")
            if b in ("bin_7p", "control"):
                g[pid] = b
        return g

    def _did(series_by_group):
        """{group: [per-step totals]} -> (acute_did, recovery_did) in % points."""
        out = []
        for taus in (DID_ACUTE, DID_RECOVERY):
            vals = {}
            for grp, xs in series_by_group.items():
                if len(xs) < 2 or xs[0] <= 1e-9:
                    vals[grp] = float("nan"); continue
                pct = [100.0 * (xs[i] / xs[0] - 1.0) for i in range(1, len(xs))]  # index i -> tau i-1
                sel = [pct[t] for t in taus if t < len(pct)]
                vals[grp] = sum(sel) / len(sel) if sel else float("nan")
            out.append(vals.get("bin_7p", float("nan")) - vals.get("control", float("nan")))
        return out

    # ---- one global trace (reads the current seed's firm_va) ----
    state = {"firm_va": {}, "did_groups": {}}
    TRACE_VA, TRACE_HH = [], []
    TRACE_SALES = {"bin_7p": [], "control": []}      # MMI-bin production (UQ "sales")
    TRACE_PURCH = {"bin_7p": [], "control": []}      # MMI-bin total_input (UQ "purchases")
    _orig = S._run_one_time_step
    def traced(time_step, *a, **k):
        r = _orig(time_step, *a, **k)
        fs, hh = a[3], a[4]
        fv = state["firm_va"]
        TRACE_VA.append(sum(f.production * fv.get(pid, 0.0) for pid, f in fs.items()))
        # welfare = households only; the national government/investment agents share the
        # hh dict but are separate accounting agents (would inflate the loss ~2.5x here).
        TRACE_HH.append(sum(h.consumption_loss for h in hh.values()
                            if getattr(h, "agent_type", "household") == "household"))
        grp = state["did_groups"]
        if grp:
            s = {"bin_7p": 0.0, "control": 0.0}; p = {"bin_7p": 0.0, "control": 0.0}
            for pid, b in grp.items():
                f = fs.get(pid)
                if f is None:
                    continue
                s[b] += f.production
                p[b] += f.total_input
            for b in ("bin_7p", "control"):
                TRACE_SALES[b].append(s[b]); TRACE_PURCH[b].append(p[b])
        return r
    S._run_one_time_step = traced

    rows = []
    for seed in seeds:
        print(f"[seed {seed}] building ...")
        sc, firms, households, countries, firm_va = build_agents(common, ap_, sp, tp, lp, seed)
        state["firm_va"] = firm_va
        state["did_groups"] = _did_groups(firms) if canton2bin else {}
        # capture the built (x1) inventory scheme + capital so each config re-derives from baseline
        base_firm_inv = {f.pid: dict(f.inventory_duration_target) for f in firms.values()}
        base_hh_inv = {h.pid: dict(h.inventory_duration_target) for h in households.values()}
        base_restore = ap_.inventory_restoration_time
        for oat_param, rc in run_configs:
            fscale = rc.get("firm_inv", 1.0)
            hscale, rscale = rc.get("hh_inv", 1.0), rc.get("restore", 1.0)
            # ---- runtime params: SimParams/TransportParams are frozen dataclasses, so build a
            # per-config copy and hand it to run_disruption (which takes tp/sp as arguments).
            # Deriving from the built sp/tp every time also means no config can leak into the next.
            sp_cfg = replace(sp, time_to_activate_idle_capital=rc["tau"],
                             adaptive_supplier_weight=rc["adasup"],
                             capacity_constrained_orders=rc["capcon"],
                             adaptive_inventories=rc["adainv"])
            tp_cfg = replace(tp, rationing_mode=rc["ration"],
                             price_increase_threshold=(rc["price_thr"] or None))
            # Per-type absolute-day targets -> time steps. At the baseline these reproduce the
            # built targets exactly (load_inventories also computes days/step_days), so only the
            # one type varied by this OAT config actually differs.
            buf_steps = {t: rc[f"buf_{t}"] / step_days for t in FIRM_BUF_TYPES if f"buf_{t}" in rc}
            for f in firms.values():
                f.utilization_rate = rc["util"]
                f.critical_input_threshold = rc["crit"]
                # types without a per-type axis (default/mining/construction) keep their built value
                f.inventory_duration_target = {k: buf_steps.get(_input_type(k), v) * fscale
                                               for k, v in base_firm_inv[f.pid].items()}
                f.inventory_restoration_time = base_restore * rscale
                # Set the ATTRIBUTE, not the stocks: set_initial_conditions -> initialize_finance
                # re-derives capital_initial = ratio * annual VA each run, so rescaling the stocks
                # here would be silently overwritten. A bigger ratio means a fixed absolute
                # destruction removes a smaller FRACTION -> a pure shock-severity lever.
                f.capital_to_value_added_ratio = rc["capratio"]
            for h in households.values():
                h.inventory_duration_target = {k: v * hscale for k, v in base_hh_inv[h.pid].items()}
                h.inventory_restoration_time = base_restore * rscale
            TRACE_VA.clear(); TRACE_HH.clear()
            for _b in ("bin_7p", "control"):
                TRACE_SALES[_b].clear(); TRACE_PURCH[_b].clear()
            d = dict(disr)
            d.update(reconstruction_market=rc["recon"], reconstruction_public_share=rc["public"],
                     reconstruction_target_time=rc["target"], reconstruction_lag=rc["lag"],
                     amount_scale=rc["shock"],
                     capital_input_mix={"CON": 0.7, "MAN": 0.2, "IMP": 0.1})
            if "locality" in rc:
                d["reconstruction_locality"] = rc["locality"]
            logging.disable(logging.INFO)
            run_disruption(sc, tn, firms, households, countries, tp_cfg, sp_cfg, [d], te, firm_table,
                           sp_cfg.t_final, export_folder=None)
            logging.disable(logging.NOTSET)
            annual_gdp = TRACE_VA[0] * ppy
            gdp_loss = float(sum(TRACE_VA[0] - v for v in TRACE_VA[1:]))
            hh_loss = float(sum(TRACE_HH))
            # UQ validation target: MMI>7 minus control, acute (tau 0-1) and recovery (tau 2-12)
            if state["did_groups"] and len(TRACE_SALES["control"]) > 2:
                s_ac, s_rec = _did(TRACE_SALES)
                p_ac, p_rec = _did(TRACE_PURCH)
            else:
                s_ac = s_rec = p_ac = p_rec = float("nan")
            rows.append({"seed": seed, "oat_param": oat_param, "flow_coverage": args.flow_coverage,
                         "nb_suppliers_per_input": args.nb_suppliers, "utilization_rate": rc["util"],
                         "reconstruction_market": rc["recon"], "reconstruction_public_share": rc["public"],
                         "reconstruction_target_time": rc["target"], "reconstruction_lag": rc["lag"],
                         "critical_input_threshold": rc["crit"],
                         "firm_inventory_scale": rc.get("firm_inv", 1.0),
                         "household_inventory_scale": rc.get("hh_inv", 1.0),
                         "inventory_restoration_scale": rc.get("restore", 1.0),
                         "time_to_activate_idle_capital": rc["tau"],
                         "capital_to_value_added_ratio": rc["capratio"],
                         "shock_scale": rc["shock"],
                         "price_increase_threshold": rc["price_thr"],
                         "adaptive_supplier_weight": rc["adasup"],
                         "capacity_constrained_orders": rc["capcon"],
                         "adaptive_inventories": rc["adainv"],
                         "rationing_mode": rc["ration"],
                         "reconstruction_locality": rc.get("locality", base_locality),
                         **{f"firm_{_t}_buffer_days": rc.get(f"buf_{_t}", base_days[_t]) for _t in FIRM_BUF_TYPES},
                         "household_loss_pct_annual_gdp": round(100.0 * hh_loss / annual_gdp, 4),
                         "household_loss_mUSD": round(hh_loss, 2),
                         "gdp_loss_pct_annual_gdp": round(100.0 * gdp_loss / annual_gdp, 4),
                         "did_sales_acute": round(s_ac, 3), "did_sales_recovery": round(s_rec, 3),
                         "did_purchases_acute": round(p_ac, 3), "did_purchases_recovery": round(p_rec, 3)})
            print(f"    seed={seed} [{oat_param or 'grid'}] hh {rows[-1]['household_loss_pct_annual_gdp']:.2f}% "
                  f"| VA {rows[-1]['gdp_loss_pct_annual_gdp']:.2f}% | acute sales DiD {s_ac:.2f} (UQ -9.6)")

    df = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, mode="a", header=not args.out.exists(), index=False)
    print(f"\n-> appended {len(df)} rows ({len(seeds)} seeds) to {args.out}")


if __name__ == "__main__":
    main()
