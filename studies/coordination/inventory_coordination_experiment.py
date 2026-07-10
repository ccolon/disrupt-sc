#!/usr/bin/env python
"""
2x2 factorial inventory-coordination experiment (Kunreuther & Heal, 2003).

A focal firm raising inventory unilaterally pays a private cost in normal
times but captures little benefit during a disruption (it is still hit by
indirect effects through unbuffered neighbors). When the whole network
raises inventory, the focal firm's disruption losses fall by much more.
The gap is the interdependence externality — a coordination failure.

Design
------
- Focal firms: 3 ECU_CON manufacturers in major demand centers
  (Quito ECU_CON_149, Guayaquil ECU_CON_22, Cuenca ECU_CON_82).
- Inventory lever: 2x multiplier on `inventory_duration_target` for all
  inputs of the relevant firms.
- Disruption: 14-day transport disruption of Scenario 5_50 (the 2022
  Ecuador flood proxy).
- Normal regime: no disruption.
- Cells: 2 (focal raised) x 2 (rest raised) x 2 (shock) = 8 runs.

Outputs
-------
- focal_firm_timeseries.csv   per-cell, per-focal-firm, per-timestep
- cell_aggregates.csv         per-cell aggregates (focal + household)
- console summary             four key quantities + wedge

Run
---
    python scripts/inventory_coordination_experiment.py

Requires the cached pickles in `<main-repo>/tmp/` from a prior Ecuador run.
"""
from __future__ import annotations

import argparse
import copy
import logging
import sys
import time
from pathlib import Path

# DisruptSC source lives in the main repo; cache pickles too.
# This script can run from a worktree as long as we import from main.
MAIN_REPO = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc")
sys.path.insert(0, str(MAIN_REPO / "src"))
sys.setrecursionlimit(50000)

import pandas as pd

from disruptsc.config import load_config, build_params, setup_logging
from disruptsc.init_pipeline.agents import configure_household_inventories
from disruptsc.run_pipeline.cache import (
    load_cached_transport_network,
    load_cached_agents,
    load_cached_sc_network,
    load_cached_logistic_routes,
)
from disruptsc.run_pipeline.simulate import (
    prepare_disruption_baseline,
    continue_disruption_run,
)
from disruptsc.run_pipeline.disruption import parse_disruptions


# ────────────────────── Experiment configuration ──────────────────────
SCOPE = "Ecuador"
FOCAL_FIRM_NAMES = ["ECU_CON_149", "ECU_CON_22", "ECU_CON_82"]  # Quito, Guayaquil, Cuenca
INVENTORY_FACTOR = 2.0
DISRUPTION_DURATION = 14
T_FINAL_SHOCK = 30   # 14-day shock + 16 days of recovery
T_FINAL_NORMAL = 7   # short — only need a few steady-state steps
DISRUPTION_CONFIG = [{
    "type": "transport_disruption",
    "attribute": "disruption",
    "values": ["Scenario 5_50"],
    "duration": DISRUPTION_DURATION,
    "start_time": 1,
}]

CELLS = [
    # (label,               focal_raised, all_raised, shock)
    ("normal_baseline",     False,        False,      False),
    ("normal_focal_only",   True,         False,      False),
    ("normal_all_only",     False,        True,       False),
    ("normal_both",         True,         True,       False),
    ("shock_baseline",      False,        False,      True),
    ("shock_focal_only",    True,         False,      True),
    ("shock_all_only",      False,        True,       True),
    ("shock_both",          True,         True,       True),
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "Ecuador_inventory_coordination"


# ────────────────────── State construction ──────────────────────
def build_state():
    """Load all init-pipeline state from cache."""
    config = load_config(SCOPE)
    config["simulation_type"] = "disruption"
    config["t_final"] = T_FINAL_SHOCK
    tp, sp, ap, lp = build_params(config)

    logging.info("Loading transport network from cache")
    transport_network, transport_edges, transport_nodes = load_cached_transport_network()

    logging.info("Loading agents from cache")
    mrio, sector_table, firms, firm_table, households, household_table, countries = load_cached_agents()

    logging.info("Loading SC network from cache")
    sc_network, firms, households, countries = load_cached_sc_network()

    logging.info("Loading routes from cache")
    sc_network, transport_network, cl_table, firms, households, countries = load_cached_logistic_routes()

    # Configure household inventories (needed after each cached load)
    configure_household_inventories(
        households, ap.enable_household_inventories,
        ap.inventory_duration_targets, ap.inventory_restoration_time,
        sp.time_resolution, sector_table,
    )

    return {
        "sc": sc_network, "tn": transport_network,
        "firms": firms, "hh": households, "countries": countries,
        "transport_edges": transport_edges, "firm_table": firm_table,
        "household_table": household_table, "sector_table": sector_table,
        "tp": tp, "sp": sp, "ap": ap, "lp": lp,
    }


# ────────────────────── Inventory lever ──────────────────────
def apply_inventory_lever(firms, focal_pids: set, factor: float,
                          focal_raised: bool, all_raised: bool):
    """Multiply each firm's inventory_duration_target by `factor` if selected."""
    for pid, firm in firms.items():
        is_focal = pid in focal_pids
        should_raise = (is_focal and focal_raised) or ((not is_focal) and all_raised)
        if should_raise:
            firm.inventory_duration_target = {
                k: v * factor for k, v in firm.inventory_duration_target.items()
            }


def baseline_inventory_value(firm) -> float:
    """Equilibrium daily input value held as inventory at baseline target.

    Returns sum_i eq_needs[i] * baseline_target_days[i].  In model units
    (mUSD, since eq_price=1).
    """
    total = 0.0
    for input_id, days in firm.inventory_duration_target.items():
        total += firm.eq_needs.get(input_id, 0.0) * days
    return total


# ────────────────────── Run one cell ──────────────────────
def run_cell(state, label, focal_raised, all_raised, shock, focal_pids):
    logging.info(f"=== Cell {label}: focal_raised={focal_raised}, "
                 f"all_raised={all_raised}, shock={shock} ===")

    s = copy.deepcopy(state)
    sc, tn = s["sc"], s["tn"]
    firms, hh, countries = s["firms"], s["hh"], s["countries"]
    tp, sp = s["tp"], s["sp"]

    apply_inventory_lever(firms, focal_pids, INVENTORY_FACTOR, focal_raised, all_raised)

    t_final = T_FINAL_SHOCK if shock else T_FINAL_NORMAL

    # Run t=0 (also re-initializes inventories from the new targets)
    all_data, lr, rs = prepare_disruption_baseline(sc, tn, firms, hh, countries, tp, sp)

    # Capture baseline inventory $ for focal firms (post-init)
    focal_baseline_inventory_value = {
        pid: sum(firms[pid].inventory.get(i, 0.0) for i in firms[pid].inventory)
        for pid in focal_pids
    }

    if shock:
        disruptions = parse_disruptions(
            DISRUPTION_CONFIG, s["transport_edges"], s["firm_table"],
            firms, tp.monetary_units,
        )
    else:
        disruptions = []

    all_data, lr, rs = continue_disruption_run(
        sc, tn, firms, hh, countries, tp, sp,
        disruptions=disruptions, t_start=1, t_final=t_final,
        all_data=all_data, logistics_reports=lr, all_routing_summaries=rs,
    )

    firm_df = pd.DataFrame(all_data["firm"])
    hh_df = pd.DataFrame(all_data["household"])

    # Focal-firm-only firm rows
    focal_df = firm_df[firm_df["firm"].isin(focal_pids)].copy()
    focal_df["label"] = label
    focal_df["focal_raised"] = focal_raised
    focal_df["all_raised"] = all_raised
    focal_df["shock"] = shock

    # Aggregate household loss
    hh_df["total_loss"] = hh_df["consumption_loss"] + hh_df["extra_spending"]
    total_hh_loss = hh_df["total_loss"].sum()

    return {
        "label": label,
        "focal_raised": focal_raised, "all_raised": all_raised, "shock": shock,
        "focal_df": focal_df,
        "total_hh_loss": total_hh_loss,
        "focal_baseline_inventory_value": focal_baseline_inventory_value,
    }


# ────────────────────── Aggregation ──────────────────────
def aggregate_cell(result, focal_pids, eq_total_orders, eq_baseline_inventory):
    """Per-focal-firm aggregate metrics for one cell."""
    fdf = result["focal_df"].copy()
    # `rationing` is fulfillment rate (1.0 = fully delivered); shortfall = 1 - rationing
    fdf["sales_shortfall"] = fdf["total_order"] * (1.0 - fdf["rationing"])
    # Production shortfall: gap vs target
    fdf["production_shortfall"] = fdf["production_target"] - fdf["production"]

    agg = fdf.groupby("firm").agg(
        n_timesteps=("time_step", "count"),
        sum_orders=("total_order", "sum"),
        sum_production=("production", "sum"),
        sum_production_target=("production_target", "sum"),
        sales_shortfall=("sales_shortfall", "sum"),
        production_shortfall=("production_shortfall", "sum"),
        mean_rationing=("rationing", "mean"),
        max_rationing=("rationing", "max"),
        mean_profit=("profit", "mean"),
    ).reset_index().rename(columns={"firm": "pid"})

    # Inventory excess vs counterfactual (factor-1) * baseline inventory $
    # If focal raised: excess = baseline_inv_value * (FACTOR - 1)
    # else: 0
    agg["excess_inventory_value"] = agg["pid"].map(
        lambda pid: eq_baseline_inventory.get(pid, 0.0) * (INVENTORY_FACTOR - 1.0)
        if result["focal_raised"] else 0.0
    )
    # Multiply by simulation horizon (days) and a default holding rate (20%/yr)
    # to get a holding cost in mUSD. The user requested decomposed output, so
    # we expose both the inventory value and the cost under 20%/yr.
    days_held = result["focal_df"]["time_step"].max() if len(result["focal_df"]) else 0
    agg["days_held"] = days_held
    agg["holding_cost_20pct_yr"] = agg["excess_inventory_value"] * days_held / 365.0 * 0.20

    agg["label"] = result["label"]
    agg["focal_raised"] = result["focal_raised"]
    agg["all_raised"] = result["all_raised"]
    agg["shock"] = result["shock"]
    agg["total_hh_loss"] = result["total_hh_loss"]
    return agg


def print_key_quantities(cell_agg: pd.DataFrame):
    """Pretty-print the four narrative quantities + wedge."""
    # Aggregate across the 3 focal firms by summing sales shortfall and holding cost
    by_cell = cell_agg.groupby(
        ["label", "focal_raised", "all_raised", "shock"], as_index=False
    ).agg(
        sales_shortfall=("sales_shortfall", "sum"),
        production_shortfall=("production_shortfall", "sum"),
        holding_cost=("holding_cost_20pct_yr", "sum"),
        excess_inv_value=("excess_inventory_value", "sum"),
        total_hh_loss=("total_hh_loss", "first"),
    )

    def get(label, col):
        return float(by_cell.loc[by_cell["label"] == label, col].iloc[0])

    # The four quantities (all in model monetary units, default mUSD)
    private_cost_normal = (
        get("normal_focal_only", "holding_cost")
        - get("normal_baseline", "holding_cost")
    )

    private_benefit_shock = (
        get("shock_baseline", "sales_shortfall")
        - get("shock_focal_only", "sales_shortfall")
    )
    collective_benefit_shock = (
        get("shock_baseline", "sales_shortfall")
        - get("shock_both", "sales_shortfall")
    )
    wedge = collective_benefit_shock - private_benefit_shock

    # Ratios
    sb = get("shock_baseline", "sales_shortfall")
    pct_private = private_benefit_shock / sb * 100 if sb else 0.0
    pct_collective = collective_benefit_shock / sb * 100 if sb else 0.0

    print("\n" + "=" * 70)
    print(f"Focal firms: {', '.join(FOCAL_FIRM_NAMES)}")
    print(f"Inventory lever: x{INVENTORY_FACTOR}")
    print(f"Shock: {DISRUPTION_DURATION}-day Scenario 5_50 transport disruption")
    print("=" * 70)
    print("\nFocal-firm sales shortfall (sum across 3 firms, model units = mUSD):")
    print(f"  shock_baseline    : {get('shock_baseline',   'sales_shortfall'):>10.3f}")
    print(f"  shock_focal_only  : {get('shock_focal_only', 'sales_shortfall'):>10.3f}")
    print(f"  shock_all_only    : {get('shock_all_only',   'sales_shortfall'):>10.3f}")
    print(f"  shock_both        : {get('shock_both',       'sales_shortfall'):>10.3f}")
    print("\nKey quantities (focal firms only):")
    print(f"  Private cost of acting alone (normal times) [holding cost @20%/yr]")
    print(f"                                  = {private_cost_normal:>10.4f} mUSD")
    print(f"  Private benefit of acting alone (in shock)")
    print(f"   = SS(shock_baseline) - SS(shock_focal_only)")
    print(f"                                  = {private_benefit_shock:>10.3f} mUSD  ({pct_private:5.1f}%)")
    print(f"  Collective benefit (everyone acts, in shock)")
    print(f"   = SS(shock_baseline) - SS(shock_both)")
    print(f"                                  = {collective_benefit_shock:>10.3f} mUSD  ({pct_collective:5.1f}%)")
    print(f"  Wedge (externality) = collective - private")
    print(f"                                  = {wedge:>10.3f} mUSD  ({pct_collective - pct_private:5.1f} pp)")
    print()
    print("If wedge > 0 and private_benefit < private_cost: coordination failure.")
    print("=" * 70)


# ────────────────────── Main ──────────────────────
def main():
    global T_FINAL_SHOCK, T_FINAL_NORMAL

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--cells", default=None,
                    help="Comma-separated cell labels to run (default: all 8)")
    ap.add_argument("--smoke", action="store_true",
                    help="Quick check: 2 cells (shock_baseline, shock_both) with short horizon")
    ap.add_argument("--t-final-shock", type=int, default=T_FINAL_SHOCK,
                    help=f"Override shock simulation length (default {T_FINAL_SHOCK})")
    ap.add_argument("--t-final-normal", type=int, default=T_FINAL_NORMAL,
                    help=f"Override normal simulation length (default {T_FINAL_NORMAL})")
    ap.add_argument("--log-level", default="info", choices=["info", "debug", "warning"])
    args = ap.parse_args()

    setup_logging(args.log_level)
    T_FINAL_SHOCK = args.t_final_shock
    T_FINAL_NORMAL = args.t_final_normal

    if args.smoke:
        cells_to_run = [c for c in CELLS if c[0] in ("shock_baseline", "shock_both")]
        T_FINAL_SHOCK = min(T_FINAL_SHOCK, 18)
    elif args.cells:
        wanted = {x.strip() for x in args.cells.split(",")}
        unknown = wanted - {c[0] for c in CELLS}
        if unknown:
            raise SystemExit(f"Unknown cells: {unknown}")
        cells_to_run = [c for c in CELLS if c[0] in wanted]
    else:
        cells_to_run = list(CELLS)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.info(f"Will run {len(cells_to_run)} cell(s): {[c[0] for c in cells_to_run]}")
    logging.info(f"T_FINAL_SHOCK={T_FINAL_SHOCK}, T_FINAL_NORMAL={T_FINAL_NORMAL}")

    state = build_state()
    firms = state["firms"]
    logging.info(f"Loaded state: {len(firms)} firms, {len(state['hh'])} households")

    by_name = {f.name: f for f in firms.values()}
    focal_pids = set()
    for n in FOCAL_FIRM_NAMES:
        if n not in by_name:
            raise SystemExit(f"Focal firm '{n}' not found")
        f = by_name[n]
        focal_pids.add(f.pid)
        logging.info(f"  Focal: {n}  pid={f.pid}  canton={getattr(f, 'subregion_canton', '?')}")

    results = []
    aggs = []
    t_start = time.time()
    for i, (label, focal_raised, all_raised, shock) in enumerate(cells_to_run, 1):
        logging.info(f"--- Cell {i}/{len(cells_to_run)} ---")
        t_cell = time.time()
        result = run_cell(state, label, focal_raised, all_raised, shock, focal_pids)
        logging.info(f"  Cell {label} took {time.time()-t_cell:.1f}s "
                     f"(elapsed: {time.time()-t_start:.1f}s)")
        results.append(result)

    # Baseline inventory $ from first cell (unmutated)
    eq_baseline_inventory = results[0]["focal_baseline_inventory_value"]

    for r in results:
        aggs.append(aggregate_cell(r, focal_pids, None, eq_baseline_inventory))
    all_agg = pd.concat(aggs, ignore_index=True)

    all_ts = pd.concat([r["focal_df"] for r in results], ignore_index=True)
    all_ts.to_csv(OUTPUT_DIR / "focal_firm_timeseries.csv", index=False)
    all_agg.to_csv(OUTPUT_DIR / "cell_aggregates.csv", index=False)
    logging.info(f"Outputs written to {OUTPUT_DIR}")

    # Console summary requires all 8 cells; warn if subset
    have_labels = {r["label"] for r in results}
    needed = {"normal_baseline", "normal_focal_only", "shock_baseline",
              "shock_focal_only", "shock_both"}
    if needed.issubset(have_labels):
        print_key_quantities(all_agg)
    else:
        missing = needed - have_labels
        print(f"\nSkipping key-quantities summary (missing cells: {missing}).")
        print("Cell aggregates:")
        print(all_agg[["label", "pid", "sales_shortfall", "production_shortfall",
                       "mean_rationing", "total_hh_loss"]].to_string(index=False))


if __name__ == "__main__":
    main()
