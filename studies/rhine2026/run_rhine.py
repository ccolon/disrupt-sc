"""Run one Rhine low-water scenario on the EU scope (disruption mode).

The scenario is a WEEKLY CAPACITY PROFILE on the Middle Rhine edge that carries
the Kaub bottleneck (``rhine_mainz_koblenz``, Rhine-km 498-592, named by
``onboarding/scripts/tent_to_scope.py``): each week the edge keeps the share of
its normal capacity that vessels can still load at that week's Kaub gauge
(``load_factor``), i.e. ``capacity_reduction = 1 - load_factor``. A sequence
of one-step ``transport_disruption`` entries reproduces any profile, because
DisruptSC clears a disruption when its duration elapses and re-applies the
next one at the next step (see ``run_pipeline/disruption.py``).

The economics of low water then come out of the model's congestion surcharge
(``capacity_constraint: gradual``): utilisation above capacity multiplies the
edge cost (x2 at 100 %, x5 at 105 %, x10 at 110 %), which is the model's
counterpart of the Kleinwasserzuschlag; buyers reroute to rail/road when that
is cheaper, or give up deliveries beyond ``price_increase_threshold``.

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


def build_disruptions(reductions: list[float], edges: list[str], min_reduction=0.01) -> list[dict]:
    out = []
    for t, r in enumerate(reductions, start=1):
        if r < min_reduction:
            continue
        out.append({
            "type": "transport_disruption",
            "attribute": "name",
            "values": list(edges),
            "capacity_reduction": float(r),
            "start_time": t,
            "duration": 1,
        })
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--profile", required=True, help="<name> -> scenarios/<name>.csv")
    ap.add_argument("--edges", default=KAUB_EDGE, help="comma-separated rhine_* edge names")
    ap.add_argument("--draught-table", default=str(SCEN / "draught_table.csv"))
    ap.add_argument("--capacities", default=str(SCEN / "rhine_capacities.csv"))
    ap.add_argument("--recovery-weeks", type=int, default=8, help="extra weeks after the profile ends")
    ap.add_argument("--flow-coverage", type=float, default=None)
    ap.add_argument("--constraint-mode", choices=["gradual", "binary"], default="gradual",
                    help="gradual = congestion surcharge (the model's Kleinwasserzuschlag; re-prices every "
                         "capacitated edge by its utilisation); binary = over-capacity edges are not routed, "
                         "no re-pricing (see README section 2.2 design point)")
    ap.add_argument("--seed", type=int, default=42)
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
    disruptions = build_disruptions(reductions, edges)
    t_final = len(reductions) + args.recovery_weeks

    print(f"profile {args.profile}: {len(reductions)} weeks, {len(disruptions)} disrupted weeks, "
          f"max reduction {max(reductions):.0%}, t_final={t_final}, edges={edges}")
    for d in disruptions:
        wk = profile.iloc[d["start_time"] - 1]
        print(f"  t={d['start_time']:2d} {wk.get('week_start', '')} "
              f"kaub={wk.get('kaub_cm', float('nan'))} -> capacity -{d['capacity_reduction']:.0%}")
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
    caps = pd.read_csv(args.capacities)
    overrides = dict(config.get("transport_capacity_overrides") or {})
    overrides.update({r["name"]: float(r["tons_per_day"]) for _, r in caps.iterrows()})
    config["transport_capacity_overrides"] = overrides
    config["disruptions"] = disruptions

    export_folder = Path(args.out) if args.out else RUNS_DIR / f"{args.profile}_seed{args.seed}"
    print(f"Export folder: {export_folder}")
    execute(config, export_folder=export_folder, open_report=not args.no_open)
    print(f"\nDone. Time series + report in: {export_folder}")


if __name__ == "__main__":
    main()
