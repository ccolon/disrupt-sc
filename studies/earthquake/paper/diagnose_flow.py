"""Diagnose flow_coverage x critical_input_threshold (Partially-Binding Leontief).

The strict-Leontief model does NOT saturate in flow_coverage: denser networks add
small links that each transmit full cascade. Raising critical_input_threshold makes
small-share inputs non-critical (they no longer zero a firm), which should (a) lower
losses toward realism and (b) make losses SATURATE across flow_coverage.

For each flow_coverage: agents/links, model-vs-MRIO initial-state coverage (unit- and
time-adjusted), build time; then for each threshold: household loss (% of annual GDP)
and sim time on the SAME build.

Run:  python studies/earthquake/paper/diagnose_flow.py --flows 0.6,0.9 --thresholds 0.0,0.05,0.10
"""
from __future__ import annotations

import argparse
import logging
import random
import sys
import time
from pathlib import Path

import numpy as np

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
import pandas as pd                                                            # noqa: E402
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network    # noqa: E402
import disruptsc.run_pipeline.simulate as S                                    # noqa: E402
from disruptsc.run_pipeline.simulate import run_disruption, set_initial_conditions  # noqa: E402

DAYS_PER_STEP = {"day": 1, "week": 7, "month": 30, "year": 365}
UNIT = {"USD": 1.0, "kUSD": 1e3, "mUSD": 1e6}


def build(flow):
    setup_logging("info")
    cfg = load_config("EcuadorEQ")
    cfg["flow_coverage"] = flow; cfg["rationing_mode"] = "equal"; cfg["t_final"] = 13
    tp, sp, ap_, lp = build_params(cfg)
    fp = cfg["filepaths"]; disr = cfg["disruptions"][0]
    ppy = 365.0 / DAYS_PER_STEP.get(sp.time_resolution, 30)
    data2model = UNIT[ap_.monetary_units_in_data] / UNIT[ap_.monetary_units_in_model]  # kUSD->mUSD

    t0 = time.time()
    tn, te, tnodes = build_transport_network(
        cfg.get("transport_modes", ["roads"]), fp, cfg.get("logistics", {}), sp.time_resolution,
        capacity_overrides=cfg.get("transport_capacity_overrides"),
        default_transport_capacity=cfg.get("default_transport_capacity"), use_cargo_types=tp.use_cargo_types)
    mrio = load_mrio(fp.get("mrio"), ap_.monetary_units_in_data)
    sector_table = load_sector_table(fp.get("sector_table")); usd_per_ton = load_usd_per_ton(sector_table)
    selection = filter_sectors(mrio, flow, ap_.sectors_to_include, ap_.sectors_to_exclude)
    firm_table = create_firm_table(mrio, sector_table, fp.get("firms_spatial"), fp.get("households_spatial"),
                                   usd_per_ton, tnodes, ap_, selection)
    firms = create_firms(firm_table, ap_); load_tech_coefs(firms, mrio, selection)
    load_inventories(firms, ap_.inventory_duration_targets, sp.time_resolution, sector_table)
    household_table, consumption = create_household_table(mrio, fp.get("households_spatial"), tnodes, selection, ap_,
                                                          time_resolution=sp.time_resolution)
    households = create_households(household_table, consumption)
    households = add_representative_demand_agents(households, mrio, selection, ap_, sp.time_resolution)
    configure_household_inventories(households, ap_.enable_household_inventories, ap_.household_inventory_duration_targets,
                                    ap_.inventory_restoration_time, sp.time_resolution, sector_table)
    countries = create_countries(mrio, tnodes, fp.get("countries_spatial"), usd_per_ton, sp.time_resolution, ap_,
                                 selection, transport_edges=te, countries_no_transport=tp.countries_no_transport)
    random.seed(0); np.random.seed(0)
    cargo_map = lp.sector_to_cargo_type if tp.use_cargo_types else {"default": "any"}
    sc = build_supply_chain_network(firms, households, countries, mrio, sector_table, ap_.nb_suppliers_per_input,
                                    ap_.weight_localization_firm, ap_.weight_localization_household, cargo_map, tn)
    set_initial_conditions(sc, firms, households, countries, tp, sp)
    build_time = time.time() - t0

    # coverage: model (per-step, mUSD) annualized vs MRIO (annual, converted to mUSD)
    m_sales = sum(f.eq_production for f in firms.values()) * ppy
    m_purch = sum(f.total_input for f in firms.values()) * ppy
    mrio_out = float(mrio.get_total_output(list(mrio.region_sectors)).sum()) * data2model
    mrio_in = float(mrio.get_total_input(list(mrio.region_sectors)).sum()) * data2model

    def _va(f):
        ef = getattr(f, "eq_finance", None) or {}; s = ef.get("sales", 0.0); c = ef.get("costs", {})
        return (s - c.get("input", 0.0) - c.get("transport", 0.0)) / s if s > 1e-12 else 0.0
    annual_gdp = sum(f.eq_production * _va(f) for f in firms.values()) * ppy

    crit_path = fp.get("input_criticality")
    crit_df = pd.read_csv(crit_path, index_col=0) if crit_path and Path(crit_path).exists() else None

    ctx = dict(sc=sc, tn=tn, te=te, firms=firms, households=households, countries=countries,
               firm_table=firm_table, tp=tp, sp=sp, disr=disr, annual_gdp=annual_gdp, crit_df=crit_df)
    struct = dict(flow_coverage=flow, n_firms=len(firms), n_edges=sc.number_of_edges(),
                  output_coverage_pct=100 * m_sales / mrio_out, input_coverage_pct=100 * m_purch / mrio_in,
                  annual_gdp_mUSD=annual_gdp, build_time_s=round(build_time, 1))
    return ctx, struct


def run_at(ctx, recipe):
    """recipe: ('strict',None) | ('share',thr) | ('matrix',None). Sets the
    production-function mode on every firm, then runs the disruption."""
    mode, val = recipe
    if mode == "matrix":
        if ctx["crit_df"] is None:
            raise SystemExit("No criticality matrix found (filepaths.input_criticality)")
        load_input_criticality(ctx["firms"], ctx["crit_df"])
        for f in ctx["firms"].values():
            f.critical_input_threshold = float(val or 0.0)  # 0 = pure matrix; >0 = gated
    else:
        for f in ctx["firms"].values():
            f.input_criticality = {}                       # disable matrix
            f.critical_input_threshold = float(val or 0.0)
    HH = []
    _orig = S._run_one_time_step
    def traced(ts, *a, **k):
        r = _orig(ts, *a, **k); HH.append(sum(h.consumption_loss for h in a[4].values())); return r
    S._run_one_time_step = traced
    t0 = time.time(); logging.disable(logging.INFO)
    run_disruption(ctx["sc"], ctx["tn"], ctx["firms"], ctx["households"], ctx["countries"], ctx["tp"], ctx["sp"],
                   [dict(ctx["disr"])], ctx["te"], ctx["firm_table"], ctx["sp"].t_final, export_folder=None)
    logging.disable(logging.NOTSET); S._run_one_time_step = _orig
    return 100.0 * float(sum(HH)) / ctx["annual_gdp"], round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flows", type=lambda s: [float(x) for x in s.split(",")], default=[0.6, 0.9])
    args = ap.parse_args()

    # Recipes: production-function variants to compare on identical builds.
    recipes = [("strict", None), ("matrix", None), ("matrix", 0.02), ("matrix", 0.05)]
    labels = {("strict", None): "strict Leontief",
              ("matrix", None): "matrix (pure)",
              ("matrix", 0.02): "matrix gated@0.02",
              ("matrix", 0.05): "matrix gated@0.05"}

    structs, losses = [], {}
    for flow in args.flows:
        ctx, struct = build(flow)
        structs.append(struct)
        for rc in recipes:
            loss, st = run_at(ctx, rc)
            losses[(flow, rc)] = loss
            print(f"  flow={flow} [{labels[rc]}]: household loss {loss:.2f}% of GDP  (sim {st}s)")

    print("\n==== structural (at build) ====")
    for k in ["flow_coverage", "n_firms", "n_edges", "output_coverage_pct", "input_coverage_pct",
              "annual_gdp_mUSD", "build_time_s"]:
        print(f"  {k:<20}: " + "  ".join(f"{s[k]:>12,.2f}" if isinstance(s[k], float) else f"{s[k]:>12,}" for s in structs))

    print("\n==== household loss (% GDP): rows=production function, cols=flow_coverage "
          "— SATURATION if a row is flat across columns ====")
    print(f"{'production function':>24} | " + " | ".join(f"fc={f:>5}" for f in args.flows))
    for rc in recipes:
        print(f"{labels[rc]:>24} | " + " | ".join(f"{losses[(f, rc)]:>8.2f}" for f in args.flows))


if __name__ == "__main__":
    main()
