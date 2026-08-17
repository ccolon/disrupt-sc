"""Run ONE TENT flood event as a full disruption-mode simulation.

Selects a single event (all edges sharing a catchment x return_period) from the
flood table, closes those road edges at 100% for their recovery_duration, and
runs the native disruption pipeline with an export folder — producing the full
per-timestep time series (firm/household/country/inventory/link/trade CSVs,
loss_per_region_sector_time.csv, transport flows) plus the HTML disruption
report. Settings match the 917-event campaign: daily resolution, full closure,
t_final = 2 x duration, no epsilon early-stop.

Targets edges by the gpkg's ``disruption_id`` column (== the xlsx ``edge_id``),
so the network read here must be the updated transport.gpkg that carries it.

Usage:
    python studies/TENT/run_single_event.py --catchment 24 --return-period 100
    python studies/TENT/run_single_event.py -c 24 -r 100 --no-open --flow-coverage 0.8
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, setup_logging, days_per_timestep  # noqa: E402
from disruptsc.run import execute                            # noqa: E402

from studies.TENT.events import load_events, DEFAULT_XLSX     # noqa: E402

RUNS_DIR = ROOT / "runs" / "TENT" / "single_event"


def find_event(xlsx, catchment: int, return_period: int, days_per_step: float):
    events = load_events(xlsx, days_per_step=days_per_step, return_periods=[return_period])
    for ev in events:
        if ev.catchment == catchment:
            return ev
    available = sorted({e.catchment for e in events})
    raise SystemExit(
        f"No event for catchment={catchment}, return_period={return_period}. "
        f"Catchments available at rp={return_period}: {available[:20]}"
        f"{' …' if len(available) > 20 else ''}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-c", "--catchment", type=int, required=True)
    ap.add_argument("-r", "--return-period", type=int, required=True)
    ap.add_argument("--xlsx", default=str(DEFAULT_XLSX), help="flood event table")
    ap.add_argument("--flow-coverage", type=float, default=1.0,
                    help="MRIO flow_coverage (default 1.0, the campaign value)")
    ap.add_argument("--horizon-factor", type=float, default=2.0,
                    help="t_final = factor x duration_steps (default 2, the campaign value)")
    ap.add_argument("--out", default=None, help="export folder (default runs/TENT/single_event/<key>)")
    ap.add_argument("--no-open", action="store_true", help="do not open the HTML report in a browser")
    ap.add_argument("--log-level", default="info", choices=["info", "debug"])
    args = ap.parse_args()

    setup_logging(args.log_level)
    config = load_config("TENT")
    # time_resolution comes from the TENT config file; the day->step conversion follows it.
    resolution = config.get("time_resolution", "week")
    days_per_step = days_per_timestep(resolution)
    ev = find_event(args.xlsx, args.catchment, args.return_period, days_per_step)
    t_final = max(1, int(round(args.horizon_factor * ev.duration_steps)))

    config["simulation_type"] = "disruption"
    config["flow_coverage"] = args.flow_coverage
    config["t_final"] = t_final
    config["epsilon_stop_condition"] = 0        # no early-stop: full 2 x duration horizon
    config["disruptions"] = [{
        "type": "transport_disruption",
        "attribute": "disruption_id",           # == xlsx edge_id, carried on transport.gpkg
        "values": [int(e) for e in ev.edge_ids],
        "capacity_reduction": 1.0,              # full closure
        "start_time": 1,
        "duration": ev.duration_steps,
    }]

    export_folder = Path(args.out) if args.out else RUNS_DIR / ev.key
    print(f"Event {ev.key}: {len(ev.edge_ids)} edge(s) {list(ev.edge_ids)}, "
          f"duration {ev.duration_days:.2f} d -> {ev.duration_steps} {resolution}-steps, "
          f"t_final={t_final}, resolution={resolution}, flow_coverage={args.flow_coverage}")
    print(f"Export folder: {export_folder}")

    execute(config, export_folder=export_folder, open_report=not args.no_open)
    print(f"\nDone. Time-series CSVs + report in: {export_folder}")


if __name__ == "__main__":
    main()
