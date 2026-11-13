"""Run a single DisruptSC disruption with inventory-sensitivity overrides.

Applies three overrides to the Cambodia parameter set before running:
  - scales every `inventory_duration_targets.values.<sector>` by M
  - sets `inventory_restoration_time` to T (so rho = 1/T)
  - sets each disruption's `duration` to D
Then runs the disruption and appends one row to a shared CSV.
"""

import argparse
import csv
import fcntl
import logging
import sys
import time
from pathlib import Path

import numpy as np

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from disruptsc import paths
from disruptsc.model.model import Model
from disruptsc.model.utils.caching import generate_cache_parameters_from_command_line_argument
from disruptsc.parameters import Parameters


HEADER = [
    "scope",
    "simulation_name",
    "duration",
    "time_lag",
    "tau",
    "inventory_multiplier",
    "target_sector",
    "excluded_sectors",
    "inventory_restoration_time",
    "rho",
    "seed",
    "t_final",
    "household_loss",
    "country_loss",
    "monetary_units",
    "runtime_s",
    "inventory_targets_applied",
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--scope", required=True)
    p.add_argument("--simulation_name", required=True)
    p.add_argument("--duration", type=int, required=True)
    p.add_argument("--inventory_multiplier", type=float, required=True)
    p.add_argument("--inventory_restoration_time", type=float, required=True)
    p.add_argument("--output_csv", required=True)
    p.add_argument("--cache", type=str, default=None)
    p.add_argument("--cache_isolation", action="store_true")
    p.add_argument("--seed", type=int, default=None,
                   help="If set, np.random.seed(seed) is called before model build "
                        "to fix the stochastic SC-network draw.")
    p.add_argument("--target_sector", type=str, default=None,
                   help="If set, --inventory_multiplier is applied ONLY to that "
                        "sector's inventory target (the others stay at baseline). "
                        "Must match a key in inventory_duration_targets.values "
                        "(e.g. 'utility', 'agriculture', 'transport').")
    p.add_argument("--exclude_sectors", type=str, default=None,
                   help="Comma-separated list of sectors kept at baseline. "
                        "--inventory_multiplier is applied to all OTHER sectors. "
                        "Mutually exclusive with --target_sector. "
                        "Example: 'utility,transport'.")
    args = p.parse_args()
    if args.target_sector and args.exclude_sectors:
        p.error("--target_sector and --exclude_sectors are mutually exclusive.")
    return args


def apply_overrides(parameters, duration, multiplier, restoration_time,
                    target_sector=None, exclude_sectors=None,
                    recovery_buffer_days=20):
    values = parameters.inventory_duration_targets["values"]
    if target_sector:
        if target_sector not in values:
            raise ValueError(
                f"--target_sector '{target_sector}' is not a key in "
                f"inventory_duration_targets.values (expected one of {list(values.keys())})."
            )
        values[target_sector] = float(values[target_sector]) * multiplier
    elif exclude_sectors:
        unknown = [s for s in exclude_sectors if s not in values]
        if unknown:
            raise ValueError(
                f"--exclude_sectors: unknown sector(s) {unknown}; "
                f"expected a subset of {list(values.keys())}."
            )
        for sector in list(values.keys()):
            if sector not in exclude_sectors:
                values[sector] = float(values[sector]) * multiplier
    else:
        for sector in list(values.keys()):
            values[sector] = float(values[sector]) * multiplier

    parameters.inventory_restoration_time = float(restoration_time)

    for d in parameters.disruptions:
        if "duration" in d:
            d["duration"] = int(duration)

    # Auto-extend t_final so the last cascade event + its disruption duration
    # is simulated plus a recovery buffer.  Otherwise yaml's t_final=30 clips
    # long-lag scenarios (e.g. cascading_hazards_24d with D=12 ends at t=61).
    required_end = max(
        (int(d.get("start_time", 0)) + int(d.get("duration", 0))
         for d in parameters.disruptions),
        default=0,
    )
    needed_t_final = required_end + recovery_buffer_days
    if needed_t_final > int(parameters.t_final):
        parameters.t_final = needed_t_final

    parameters.export_files = False
    parameters.with_output_folder = False


def append_row(csv_path, row):
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with open(csv_path, "a", newline="") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            w = csv.writer(f)
            if needs_header:
                w.writerow(HEADER)
            w.writerow(row)
            f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.cache_isolation:
        from disruptsc.paths import setup_cache_isolation, cleanup_isolated_cache
        setup_cache_isolation(args.scope)

    try:
        cache_parameters = generate_cache_parameters_from_command_line_argument(args.cache)

        parameters = Parameters.load_parameters(paths.PARAMETER_FOLDER, args.scope, args.simulation_name)
        parameters.simulation_name = args.simulation_name
        exclude_list = [s.strip() for s in args.exclude_sectors.split(",")] if args.exclude_sectors else None
        apply_overrides(parameters, args.duration, args.inventory_multiplier,
                        args.inventory_restoration_time,
                        target_sector=args.target_sector,
                        exclude_sectors=exclude_list)
        parameters.adjust_logging_behavior()

        if args.seed is not None:
            np.random.seed(args.seed)
            logging.info("np.random.seed(%d) set before model build", args.seed)

        model = Model(parameters)
        model.setup_transport_network(cache_parameters["transport_network"], parameters.with_transport)
        model.setup_agents(cache_parameters["agents"])
        model.setup_sc_network(cache_parameters["sc_network"])
        model.set_initial_conditions()
        model.setup_logistic_routes(cache_parameters["logistic_routes"], parameters.with_transport)

        t0 = time.time()
        simulation = model.run_disruption(t_final=parameters.t_final)
        runtime = time.time() - t0

        household_loss = float(simulation.calculate_household_loss(model.household_table))
        country_loss = float(simulation.calculate_country_loss())

        inv_targets_applied = ";".join(
            f"{k}={v}" for k, v in parameters.inventory_duration_targets["values"].items()
        )

        time_lag = getattr(parameters, "time_lag", None)
        if time_lag is None and "cascading_hazards_" in args.simulation_name:
            try:
                time_lag = int(args.simulation_name.split("cascading_hazards_")[1].rstrip("d"))
            except (IndexError, ValueError):
                time_lag = ""
        tau = (time_lag / args.duration) if isinstance(time_lag, int) and args.duration else ""

        row = [
            args.scope,
            args.simulation_name,
            args.duration,
            time_lag if time_lag is not None else "",
            tau,
            args.inventory_multiplier,
            args.target_sector if args.target_sector else "",
            args.exclude_sectors if args.exclude_sectors else "",
            args.inventory_restoration_time,
            1.0 / float(args.inventory_restoration_time),
            args.seed if args.seed is not None else "",
            parameters.t_final,
            household_loss,
            country_loss,
            parameters.monetary_units_in_model,
            runtime,
            inv_targets_applied,
        ]
        append_row(args.output_csv, row)
        logging.info(
            "DONE scope=%s sim=%s D=%d M=%.3f T=%.3f household_loss=%.6g country_loss=%.6g",
            args.scope, args.simulation_name, args.duration,
            args.inventory_multiplier, args.inventory_restoration_time,
            household_loss, country_loss,
        )
    finally:
        if args.cache_isolation:
            cleanup_isolated_cache()


if __name__ == "__main__":
    main()
