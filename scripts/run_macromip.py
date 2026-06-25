"""Driver for the macroMIP s1 stylized-forcing experiments (DisruptSC).

Runs the macroMIP s1 experiment matrix on the macroMIP world scope (OECD ICIO
2017, transport off, virtual ROW): a no-forcing baseline plus three
single-country productivity shocks, each in a temporary (one-year pulse) and a
persistent variant.

Per the protocol, forcing starts one model-year after the start (an unforced
year first). At monthly resolution that is ``start_time = 13`` and a temporary
duration of 12. ``t=0`` (last unforced period) maps to the model's pre-forcing
year; relative effects are computed against the baseline (exp0) by the adapter.

Build setting ("Option A", locked): ``flow_coverage = 0.9``,
``nb_suppliers_per_input = 1`` — captures ~72% of the MRIO's international
intermediate trade (the transmission channel) at ~80 s/step. The full matrix is
a SLURM array (one task per experiment) over a shared, cached build; see
runs/macromip/slurm/.

Examples:
    python scripts/run_macromip.py --experiment exp0 --t-final 120
    python scripts/run_macromip.py --experiment exp3t --cache same_logistic_routes
    python scripts/run_macromip.py --all                      # full matrix, one node
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Pickling deep logistic-route graphs recurses past the default limit (see run.py).
sys.setrecursionlimit(50000)

from disruptsc import paths  # noqa: E402
from disruptsc._version import __version__  # noqa: E402
from disruptsc.config import load_config, setup_logging  # noqa: E402
from disruptsc.run import execute  # noqa: E402

SCOPE = "macroMIP"
RUNS_ROOT = ROOT / "runs" / "macromip"

# sector_type buckets present in the OECD-2017 aggregation, minus agriculture and
# construction (Exp 1 applies 1/4 of its primary reduction to "all other sectors").
_ALL_OTHER = ("mining", "manufacturing", "utility", "trade", "transport", "services")

# Required macroMIP s1 forcing, primary magnitudes, socioeconomic scenario sq.
# Each entry: (country, (sector_types,), productivity_reduction). A negative
# reduction is a productivity *increase* (Exp 2 is +4% agricultural productivity).
_FORCING = {
    "exp1": (("ESP", ("agriculture", "construction"), 0.04),
             ("ESP", _ALL_OTHER, 0.01)),
    "exp2": (("FRA", ("agriculture",), -0.04),),
    "exp3": (("DEU", ("manufacturing",), 0.05),),
}

# experiment key -> (forcing key | None, persistent | None, protocol identifier)
EXPERIMENTS = {
    "exp0":  (None,   None,  "0"),
    "exp1p": ("exp1", True,  "1-p-sq-0"),
    "exp1t": ("exp1", False, "1-t-sq-0"),
    "exp2p": ("exp2", True,  "2-p-sq-0"),
    "exp2t": ("exp2", False, "2-t-sq-0"),
    "exp3p": ("exp3", True,  "3-p-sq-0"),
    "exp3t": ("exp3", False, "3-t-sq-0"),
}

_PERIODS_PER_YEAR = {"day": 365, "week": 52, "month": 12, "year": 1}


def _prod_shock(region, sector_types, reduction, start, duration):
    d = {
        "type": "productivity_shock",
        "description_type": "filter",
        "filter": {"region": [region], "sector_type": list(sector_types)},
        "productivity_reduction": reduction,
        "start_time": start,
    }
    if duration is not None:
        d["duration"] = duration
    return d


def build_disruptions(experiment: str, time_resolution: str) -> list[dict]:
    """macroMIP forcing: applied one year in; temporary = a one-year pulse."""
    ppy = _PERIODS_PER_YEAR[time_resolution]
    start = ppy + 1                       # one unforced year, then forcing
    forcing_key, persistent, _ = EXPERIMENTS[experiment]
    duration = None if persistent else ppy   # temporary = one year; persistent = no recovery

    if forcing_key is None:
        # Baseline: a filter that matches no firm makes the loop run the full
        # horizon with zero perturbation (run_disruption otherwise runs one step).
        return [_prod_shock("__baseline__", ("manufacturing",), 0.0, start, duration)]

    return [_prod_shock(region, stypes, red, start, duration)
            for (region, stypes, red) in _FORCING[forcing_key]]


def build_config(experiment: str, *, t_final: int, flow_coverage: float,
                 nb_suppliers: int, time_resolution: str, seed: int) -> dict:
    config = load_config(SCOPE)
    config["simulation_type"] = "disruption"
    config["time_resolution"] = time_resolution
    config["t_final"] = t_final
    config["flow_coverage"] = flow_coverage
    config["nb_suppliers_per_input"] = nb_suppliers
    config["with_transport"] = False
    config["epsilon_stop_condition"] = 0      # run the full horizon (capture dissipation)
    config["export_files"] = True
    config["mc_repetitions"] = 0
    config["seed"] = seed
    config["disruptions"] = build_disruptions(experiment, time_resolution)
    return config


def run_one(experiment: str, *, t_final: int, flow_coverage: float, nb_suppliers: int,
            time_resolution: str, seed: int, cache: str | None,
            cache_isolation: bool = False) -> Path:
    out = RUNS_ROOT / experiment
    out.mkdir(parents=True, exist_ok=True)
    config = build_config(experiment, t_final=t_final, flow_coverage=flow_coverage,
                          nb_suppliers=nb_suppliers, time_resolution=time_resolution,
                          seed=seed)
    forcing_key, persistent, proto_id = EXPERIMENTS[experiment]

    logging.info(f"=== macroMIP {experiment} (id {proto_id}) t_final={t_final} "
                 f"{time_resolution} fc={flow_coverage} nb={nb_suppliers} -> {out} ===")
    t0 = time.time()
    execute(config, export_folder=out, cache=cache, cache_isolation=cache_isolation)
    runtime = time.time() - t0

    meta = {
        "experiment": experiment,
        "protocol_identifier": proto_id,
        "is_baseline": forcing_key is None,
        "persistent": persistent,
        "scope": SCOPE,
        "flow_coverage": flow_coverage,
        "nb_suppliers_per_input": nb_suppliers,
        "time_resolution": time_resolution,
        "t_final": t_final,
        "forcing_start": _PERIODS_PER_YEAR[time_resolution] + 1,
        "temporary_duration": None if persistent else _PERIODS_PER_YEAR[time_resolution],
        "seed": seed,
        "disruptions": config["disruptions"],
        "disruptsc_version": __version__,
        "data_root": str(paths.INPUT_FOLDER),
        "mrio_path": str(paths.get_data_path(SCOPE) / config["filepaths"]["mrio"]),
        "monetary_units": config.get("monetary_units_in_data", "mUSD"),
        "runtime_seconds": round(runtime, 1),
    }
    (out / "run_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logging.info(f"=== Done {experiment} in {runtime/60:.1f} min ===")
    return out


def main():
    p = argparse.ArgumentParser(description="DisruptSC macroMIP s1 driver")
    p.add_argument("--experiment", choices=list(EXPERIMENTS), help="single experiment key")
    p.add_argument("--all", action="store_true", help="run the full matrix sequentially")
    p.add_argument("--t-final", type=int, default=120,
                   help="horizon in time steps (120 = 10 years monthly)")
    p.add_argument("--time-resolution", default="month",
                   choices=["day", "week", "month", "year"])
    p.add_argument("--flow-coverage", type=float, default=0.9)
    p.add_argument("--nb-suppliers", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--cache", default=None,
                   help="cache preset passthrough (e.g. same_logistic_routes)")
    p.add_argument("--cache-isolation", action="store_true",
                   help="isolate the cache per process (use for parallel SLURM array tasks "
                        "so concurrent builds don't clobber a shared tmp/)")
    p.add_argument("--log-level", default="info", choices=["info", "debug"])
    args = p.parse_args()

    setup_logging(args.log_level)
    if not args.all and not args.experiment:
        raise SystemExit("Specify --experiment <key> or --all")

    experiments = list(EXPERIMENTS) if args.all else [args.experiment]
    for exp in experiments:
        run_one(exp, t_final=args.t_final, flow_coverage=args.flow_coverage,
                nb_suppliers=args.nb_suppliers, time_resolution=args.time_resolution,
                seed=args.seed, cache=args.cache, cache_isolation=args.cache_isolation)


if __name__ == "__main__":
    main()
