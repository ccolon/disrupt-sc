"""Driver for the 2016 Ecuador earthquake DisruptSC runs.

Loads the Ecuador config, replaces its disruptions with the heterogeneous
canton x IO-sector capital-destruction shock (model-ready CSV produced by
runs/earthquake/build_model_shock.py), applies the variant toggles, sets the
seed, and runs the pipeline into runs/earthquake/<variant>/seed_<seed>/.

Variants (paper's 2x2):
    V1  substitution off, reconstruction off
    V2  substitution on,  reconstruction off
    V3  substitution off, reconstruction on
    V4  substitution on,  reconstruction on

Pass --cache-isolation so each run uses a private cache dir (tmp/<scope>_pid_...);
the shared tmp/ cache is NOT scope-namespaced, so a concurrent run of another
scope can otherwise clobber the Ecuador build and silently break the shock match.

Examples:
    python scripts/run_earthquake.py --variant V1 --seed 0 --t-final 365 --cache-isolation
    python scripts/run_earthquake.py --variant V1 --seeds 0-49        # Phase 2 (V1)
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

# The pipeline pickles logistic routes when writing the cache; deep route graphs
# recurse past Python's default 1000-frame limit (see disruptsc/run.py).
sys.setrecursionlimit(50000)

from disruptsc import paths  # noqa: E402
from disruptsc._version import __version__  # noqa: E402
from disruptsc.config import load_config, setup_logging  # noqa: E402
from disruptsc.run import execute  # noqa: E402

SCOPE = "Ecuador"
RUNS_ROOT = ROOT / "runs" / "earthquake"
DEFAULT_SHOCK = RUNS_ROOT / "_shock" / "earthquake_shock_modelready.csv"

# Per-variant overrides. Reconstruction flagged until the mechanism exists.
VARIANTS: dict[str, dict] = {
    "V1": {"substitution": False, "reconstruction": False},
    "V2": {"substitution": True, "reconstruction": False},
    "V3": {"substitution": False, "reconstruction": True},
    "V4": {"substitution": True, "reconstruction": True},
}
RECONSTRUCTION_IMPLEMENTED = True
# Reconstruction defaults: v1.1.6 bill-of-materials, ~365-day rebuild horizon.
RECONSTRUCTION_TARGET_TIME = 365
RECONSTRUCTION_INPUT_MIX = {"CON": 0.7, "MAN": 0.2, "IMP": 0.1}


def build_config(variant: str, seed: int, t_final: int, shock_file: Path,
                 with_transport: bool = False, baseline: bool = False) -> dict:
    spec = VARIANTS[variant]
    config = load_config(SCOPE)
    config["simulation_type"] = "disruption"
    config["t_final"] = t_final
    config["export_files"] = True
    config["mc_repetitions"] = 0
    config["seed"] = seed
    config["epsilon_stop_condition"] = 0  # always run the full horizon

    # Transport OFF by default for the earthquake ensemble (chosen for speed):
    # the shock propagates through supply chains, not the physical network.
    config["with_transport"] = with_transport
    if not with_transport:
        config["use_cargo_types"] = False  # routing skipped; avoid per-cargo overhead

    # Supplier substitution: multi-sourcing + adaptive reweighting toward suppliers
    # that covered prior orders. Off = single-source (no substitution).
    if spec["substitution"]:
        config["nb_suppliers_per_input"] = 2
        config["adaptive_supplier_weight"] = True
    else:
        config["nb_suppliers_per_input"] = 1
        config["adaptive_supplier_weight"] = False

    # The earthquake shock — replaces any existing disruptions (no transport shock).
    disruption = {
        "type": "capital_destruction",
        "description_type": "subregion_file",
        "file": str(shock_file),
        "unit": "mUSD",
        "start_time": 1,
        "reconstruction_market": bool(spec["reconstruction"]),
    }
    if spec["reconstruction"]:
        disruption["reconstruction_target_time"] = RECONSTRUCTION_TARGET_TIME
        disruption["capital_input_mix"] = dict(RECONSTRUCTION_INPUT_MIX)
    config["disruptions"] = [] if baseline else [disruption]
    return config


def run_one(variant: str, seed: int, t_final: int, shock_file: Path,
            cache: str | None, cache_isolation: bool = False,
            with_transport: bool = False, baseline: bool = False) -> Path:
    label = f"{variant}_baseline" if baseline else variant
    out = RUNS_ROOT / label / f"seed_{seed}"
    out.mkdir(parents=True, exist_ok=True)
    config = build_config(variant, seed, t_final, shock_file,
                          with_transport=with_transport, baseline=baseline)

    logging.info(f"=== Earthquake run: {variant} seed={seed} t_final={t_final} -> {out} ===")
    t0 = time.time()
    execute(config, export_folder=out, cache=cache, cache_isolation=cache_isolation)
    runtime = time.time() - t0

    meta = {
        "variant": variant,
        "seed": seed,
        "t_final": t_final,
        "substitution": VARIANTS[variant]["substitution"],
        "reconstruction": VARIANTS[variant]["reconstruction"],
        "baseline": baseline,
        "with_transport": config["with_transport"],
        "nb_suppliers_per_input": config["nb_suppliers_per_input"],
        "adaptive_supplier_weight": config["adaptive_supplier_weight"],
        "shock_file": str(shock_file),
        "disruptsc_version": __version__,
        "data_root": str(paths.INPUT_FOLDER),
        "runtime_seconds": round(runtime, 1),
    }
    with open(out / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    logging.info(f"=== Done {variant} seed={seed} in {runtime/60:.1f} min ===")
    return out


def _parse_seeds(args) -> list[int]:
    if args.seed is not None:
        return [args.seed]
    if args.seeds:
        s = args.seeds
        if "-" in s:
            a, b = s.split("-")
            return list(range(int(a), int(b) + 1))
        return [int(x) for x in s.split(",")]
    return [0]


def main():
    p = argparse.ArgumentParser(description="DisruptSC 2016 Ecuador earthquake driver")
    p.add_argument("--variant", default="V1", choices=list(VARIANTS))
    p.add_argument("--seed", type=int, default=None, help="single seed")
    p.add_argument("--seeds", type=str, default=None, help="range '0-49' or list '0,1,2'")
    p.add_argument("--t-final", type=int, default=365, help="horizon in days (365 / 730)")
    p.add_argument("--shock-file", type=Path, default=DEFAULT_SHOCK)
    p.add_argument("--cache", default=None, help="cache preset passthrough (see run_pipeline.cache)")
    p.add_argument("--cache-isolation", action="store_true",
                   help="use a private per-process cache dir (avoids cross-scope clobbering)")
    p.add_argument("--transport", action="store_true",
                   help="enable the transport network (default OFF for the ensemble)")
    p.add_argument("--baseline", action="store_true",
                   help="no shock (disruptions=[]); used to verify the equilibrium holds")
    p.add_argument("--log-level", default="info", choices=["info", "debug"])
    args = p.parse_args()

    setup_logging(args.log_level)
    if not args.shock_file.exists():
        raise SystemExit(f"Shock file not found: {args.shock_file}\n"
                         f"Run: python runs/earthquake/build_model_shock.py")

    for seed in _parse_seeds(args):
        run_one(args.variant, seed, args.t_final, args.shock_file, args.cache,
                cache_isolation=args.cache_isolation,
                with_transport=args.transport, baseline=args.baseline)


if __name__ == "__main__":
    main()
