"""Run one Rhine low-water scenario on the EU scope (disruption mode).

The scenario is a WEEKLY CAPACITY PROFILE on the Middle Rhine edge that carries
the Kaub bottleneck (``rhine_mainz_koblenz``, Rhine-km 498-592, named by
``onboarding/scripts/tent_to_scope.py``): each week the edge keeps the share of
its normal capacity that vessels can still load at that week's Kaub gauge
(``load_factor``), i.e. ``capacity_reduction = 1 - load_factor``. A sequence
of one-step ``transport_disruption`` entries reproduces any profile, because
DisruptSC clears a disruption when its duration elapses and re-applies the
next one at the next step (see ``run_pipeline/disruption.py``).

Without capacity routing (EU default, user decision 2026-09-03) each week is
a COST SHOCK on the Kaub edge — ``transport_cost_shock`` with multiplier
1/load_factor, the model's counterpart of the Kleinwasserzuschlag: buyers
pay the surcharge (passed into prices), reroute to rail/road when that is
cheaper, or give up beyond ``price_increase_threshold`` — or a CLOSURE in
the weeks where the fleet cannot sail (reduction >= --closure-threshold).
Partial capacity reductions remain available for capacity-routing modes.

Inputs (studies/rhine2026/scenarios/):
  <profile>.csv      week_start, kaub_cm  (weekly mean Kaub gauge, cm)  [or load_factor]
  draught_table.csv  kaub_cm, load_factor (vessel loading vs gauge; evidence-based)
  rhine_capacities.csv  name, tons_per_day (normal-year capacity per rhine_* edge)

Usage:
    python studies/rhine2026/run_rhine.py --profile 2026 [--edges rhine_mainz_koblenz]
    python studies/rhine2026/run_rhine.py --profile 2018 --recovery-weeks 12 --seed 42
    python studies/rhine2026/run_rhine.py --profile closure8w      # counterfactual: full closure 8 weeks
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, setup_logging  # noqa: E402
from disruptsc.run import execute                        # noqa: E402

HERE = Path(__file__).resolve().parent
SCEN = HERE / "scenarios"
RUNS_DIR = ROOT / "runs" / "rhine2026"
KAUB_EDGE = "rhine_mainz_koblenz"


def load_factor_curve(path: Path):
    """Piecewise-linear vessel load factor as a function of the Kaub gauge (cm)."""
    t = pd.read_csv(path).sort_values("kaub_cm")
    x, y = t["kaub_cm"].to_numpy(float), t["load_factor"].to_numpy(float)
    return lambda cm: float(np.interp(cm, x, y, left=y[0], right=y[-1]))


def weekly_reductions(profile: pd.DataFrame, curve) -> list[float]:
    if "load_factor" in profile.columns:
        lf = profile["load_factor"].astype(float).clip(0, 1).tolist()
    else:
        lf = [curve(c) for c in profile["kaub_cm"].astype(float)]
    return [round(1.0 - v, 4) for v in lf]


def build_disruptions(reductions: list[float], edges: list[str], min_reduction=0.01,
                      closure_threshold: float | None = None,
                      max_multiplier: float = 20.0,
                      substitution_share: float = 1.0) -> list[dict]:
    """One disruption entry per week.

    Without capacity routing (the EU default) a week is either a CLOSURE
    (capacity reduction at or above *closure_threshold*: the fleet cannot
    sail, Kaub below ~30 cm; ``transport_disruption`` with reduction 1.0,
    rerouting + price pass-through through the alternative-route logic) or a
    COST SHOCK (``transport_cost_shock`` with multiplier 1/(1 - reduction):
    barges at 40 % load cost 2.5x per ton; buyers pay, reroute where rail or
    road is cheaper, or give up beyond price_increase_threshold). With
    *closure_threshold* None the partial capacity reductions are emitted as
    such — meaningful only under capacity-constrained routing.
    """
    out = []
    for t, r in enumerate(reductions, start=1):
        if r < min_reduction:
            continue
        if closure_threshold is None:
            out.append({"type": "transport_disruption", "attribute": "name", "values": list(edges),
                        "capacity_reduction": float(r), "start_time": t, "duration": 1})
        elif r >= closure_threshold:
            out.append({"type": "transport_disruption", "attribute": "name", "values": list(edges),
                        "capacity_reduction": 1.0, "start_time": t, "duration": 1,
                        "substitution_share": substitution_share})
        else:
            out.append({"type": "transport_cost_shock", "attribute": "name", "values": list(edges),
                        "cost_multiplier": round(min(max_multiplier, 1.0 / (1.0 - r)), 3),
                        "capacity_factor": round(1.0 - r, 4), "substitution_share": substitution_share,
                        "start_time": t, "duration": 1})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--profile", required=True, help="<name> -> scenarios/<name>.csv")
    ap.add_argument("--edges", default=KAUB_EDGE, help="comma-separated rhine_* edge names")
    ap.add_argument("--draught-table", default=str(SCEN / "draught_table.csv"))
    ap.add_argument("--capacities", default=str(SCEN / "rhine_capacities.csv"))
    ap.add_argument("--edge-capacities",
                    default=str(ROOT.parent / "disrupt-sc-data" / "EU" / "Transport" / "scenario_edge_capacities.csv"),
                    help="baseline-derived rail/road/waterway capacities (baseline_capacities.py); "
                         "merged into transport_capacity_overrides for the scenario run when the file exists; "
                         "pass an empty string to disable")
    ap.add_argument("--recovery-weeks", type=int, default=8, help="extra weeks after the profile ends")
    ap.add_argument("--flow-coverage", type=float, default=None)
    ap.add_argument("--constraint-mode", choices=["off", "gradual", "binary"], default="off",
                    help="off = no capacity routing (EU default: the heuristic does not scale; use "
                         "--closure-threshold); gradual = congestion surcharge; binary = over-capacity "
                         "edges are not routed (both need capacity-constrained routing)")
    ap.add_argument("--closure-threshold", type=float, default=0.75,
                    help="weeks whose capacity reduction is >= this value close the Kaub edge entirely "
                         "(2026 profile at 0.75: the four weeks of 27 Jul-23 Aug); lighter weeks become "
                         "cost shocks x1/(1-reduction) (transport_cost_shock). Set to a negative value "
                         "to emit partial capacity reductions instead (needs --constraint-mode "
                         "gradual|binary)")
    ap.add_argument("--price-threshold", type=float, default=None,
                    help="override price_increase_threshold for the scenario (config default 2.0 = give up "
                         "a delivery once its transport bill more than doubles; 2026 shippers paid x5 rates)")
    ap.add_argument("--substitution-share", type=float, default=1.0,
                    help="substitution ceiling: share of the tonnage displaced from the Rhine that rail and road "
                         "can absorb (1.0 = unlimited substitutes, legacy; evidence: DB Cargo ~100 barges of ~1,000, "
                         "trucks bound by drivers -> 0.2-0.4). Applied to closures and cost shocks alike")
    ap.add_argument("--legacy-give-up", action="store_true",
                    help="sensitivity: drop the delivered-price give-up rule (delivered_price_increase_threshold "
                         "= None) so the legacy freight-bill rule (price_increase_threshold) applies")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--cache", default="auto",
                    help="cache preset passed to execute(); 'auto' reuses every stage whose fingerprint "
                         "matches (a scenario differs from the calibrated baseline only by its "
                         "disruptions, so all four stages are reused: build in minutes, not 40)")
    ap.add_argument("--scope", default="EU")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the disruption list and exit")
    ap.add_argument("--log-level", default="info", choices=["info", "debug"])
    args = ap.parse_args()

    setup_logging(args.log_level)
    profile = pd.read_csv(SCEN / f"{args.profile}.csv")
    curve = load_factor_curve(Path(args.draught_table))
    reductions = weekly_reductions(profile, curve)
    edges = [e.strip() for e in args.edges.split(",") if e.strip()]
    closure = args.closure_threshold if (args.closure_threshold is not None and args.closure_threshold >= 0) else None
    if closure is None and args.constraint_mode == "off":
        raise SystemExit("partial capacity reductions need --constraint-mode gradual|binary; "
                         "with capacity routing off use --closure-threshold (default 0.75)")
    disruptions = build_disruptions(reductions, edges, closure_threshold=closure,
                                    substitution_share=args.substitution_share)
    t_final = len(reductions) + args.recovery_weeks

    print(f"profile {args.profile}: {len(reductions)} weeks, {len(disruptions)} disrupted weeks "
          f"({'closure >= ' + format(closure, '.0%') if closure is not None else 'partial reductions'}), "
          f"max reduction {max(reductions):.0%}, t_final={t_final}, edges={edges}")
    for d in disruptions:
        wk = profile.iloc[d["start_time"] - 1]
        if d["type"] == "transport_cost_shock":
            what = f"cost x{d['cost_multiplier']:.2f}"
        elif d["capacity_reduction"] >= 1.0:
            what = "CLOSED"
        else:
            what = f"capacity -{d['capacity_reduction']:.0%}"
        print(f"  t={d['start_time']:2d} {wk.get('week_start', '')} "
              f"kaub={wk.get('kaub_cm', float('nan'))} -> {what}")
    if args.dry_run:
        return

    config = load_config(args.scope)
    config["simulation_type"] = "disruption"
    config["t_final"] = t_final
    config["epsilon_stop_condition"] = 0
    config["seed"] = args.seed
    config["capacity_constraint"] = args.constraint_mode
    if args.flow_coverage is not None:
        config["flow_coverage"] = args.flow_coverage
    if args.price_threshold is not None:
        config["price_increase_threshold"] = args.price_threshold
    if args.legacy_give_up:
        config["delivered_price_increase_threshold"] = None
    if args.constraint_mode != "off":
        overrides = dict(config.get("transport_capacity_overrides") or {})   # port throughputs from the config
        if args.edge_capacities and Path(args.edge_capacities).exists():
            ec = pd.read_csv(args.edge_capacities)
            overrides.update({str(r["name"]): float(r["capacity_tpd"]) for _, r in ec.iterrows()})
            print(f"edge capacities: {len(ec)} rail/road/waterway edges from {args.edge_capacities}")
        caps = pd.read_csv(args.capacities)                               # Rhine cross-sections last (win)
        overrides.update({r["name"]: float(r["tons_per_day"]) for _, r in caps.iterrows()})
        config["transport_capacity_overrides"] = overrides
        print(f"transport_capacity_overrides: {len(overrides)} edges; capacity_constraint: {args.constraint_mode}")
    else:
        n_closed = sum(1 for d in disruptions if d["type"] == "transport_disruption")
        print(f"capacity routing off: {n_closed} closure week(s) + {len(disruptions) - n_closed} "
              f"cost-shock week(s), no capacity overrides")
    config["disruptions"] = disruptions

    export_folder = Path(args.out) if args.out else RUNS_DIR / f"{args.profile}_seed{args.seed}"
    print(f"Export folder: {export_folder}")
    execute(config, cache=(args.cache or None), export_folder=export_folder, open_report=not args.no_open)
    print(f"\nDone. Time series + report in: {export_folder}")


if __name__ == "__main__":
    main()
