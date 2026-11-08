"""One run of the Cambodia compound-flood paper through the standard pipeline (run.py execute), 5 Nov 2026.

The configuration is config/default.yaml + studies/cambodia/paper_config.yaml + this script's switches, never
the machine's config/user_defined_Cambodia*.yaml (gitignored, not on the cluster; KI-52). Each seed has its own
named build cache (tmp/cam_s<seed>, as in the Romania ensemble): the first run of a seed builds the network, the
other scenarios reuse it through the stage fingerprints, so every scenario of a seed runs on the same supply
network (paired design) and each run starts in a fresh process from a cache built before any disruption (no
run-order effect, KI-50 b). On the cluster, run `--setup` once per seed before the scenario jobs, so that
parallel jobs never build the same cache at once.

Not the programmatic builder (disruptsc.build): it has drifted from execute (KI-51).

Writes into --out: the pipeline's exports (parameters.yaml, run_fingerprint.json, household_data.csv,
country_data.csv, ...), study_run.json (scenario, seed, switches, git SHA, config hash, edges per event) and,
unless --keep-firm-data, firm_daily.csv (production, target, capacity and input stock summed by day and sector)
in place of the 20,860-firm firm_data.csv.

Usage:
    python studies/cambodia/run_cambodia.py --scenario lag12 --duration 12 --seed 1 --t-final 180 \
        --out C:/dsc_runs/cambodia/test_lag12_s1 [--footprint v3] [--set inventory_restoration_time=4] \
        [--inventory-scale 2]
    python studies/cambodia/run_cambodia.py --setup --seed 1        # build the seed's cache only

--inventory-scale X multiplies every inventory duration target of paper_config (inventory_duration_targets.values:
utility 3, agriculture 15, ... days) by X: the robustness runs' x0.5 and x2 (R_rob, Q21, 8 Nov 2026). One switch
instead of eight --set items, whose run-name tag would pass the 255-byte limit of a folder name. The targets are
re-applied on every cache load (fingerprint.py), so the variant reuses the seed's cache.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.setrecursionlimit(50000)

from disruptsc import paths                                                  # noqa: E402
from disruptsc.config import load_config, setup_logging                      # noqa: E402
from disruptsc.run import execute                                            # noqa: E402
from disruptsc.run_pipeline.cache import setup_cache_dir                     # noqa: E402
from scenarios import FOOTPRINTS, check_footprint, disruptions               # noqa: E402

SCOPE = "Cambodia"


def load_paper_config() -> dict:
    """default.yaml + paper_config.yaml through load_config itself (same filepath resolution), in a scratch
    parameter folder that holds no local override."""
    if os.environ.get("DISRUPT_SC_EXTRA_CONFIG"):
        raise SystemExit("DISRUPT_SC_EXTRA_CONFIG is set: the paper's runs take their configuration from "
                         "paper_config.yaml and this script's switches only")
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(paths.PARAMETER_FOLDER / "default.yaml", Path(tmp) / "default.yaml")
        shutil.copy(HERE / "paper_config.yaml", Path(tmp) / f"user_defined_{SCOPE}.yaml")
        return load_config(SCOPE, parameter_folder=Path(tmp))


def apply_set(config: dict, item: str):
    """KEY=VALUE with a dotted KEY and a YAML VALUE (e.g. logistics.basic_cost.roads=0.08)."""
    key, _, raw = item.partition("=")
    if not key or not _:
        raise SystemExit(f"--set expects KEY=VALUE, got {item!r}")
    node = config
    parts = key.split(".")
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    node[parts[-1]] = yaml.safe_load(raw)


def git_state() -> dict:
    def run(*a):
        try:
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:                                   # noqa: BLE001 - provenance is best effort
            return ""
    sha = run("rev-parse", "HEAD")
    if sha:
        return {"sha": sha, "dirty_files": run("status", "--porcelain", "--", "src", "studies/cambodia"),
                "sha_source": "git"}
    # The cluster's compute nodes have no git (6 Nov 2026): the launcher records the checkout's state at submit
    # time in the environment (and in the batch folder's CODE_VERSION.txt).
    return {"sha": os.environ.get("CAMBODIA_GIT_SHA", ""), "dirty_files": os.environ.get("CAMBODIA_GIT_DIRTY", ""),
            "sha_source": "launcher (submit time)" if os.environ.get("CAMBODIA_GIT_SHA") else "unknown"}


def config_hash(config: dict) -> str:
    blob = json.dumps(config, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def summarise_firm_data(folder: Path):
    """firm_data.csv -> firm_daily.csv and household_data_by_sector.csv -> household_daily_by_sector.csv (sums by
    day and sector), then delete the per-agent files."""
    import pandas as pd

    src = folder / "firm_data.csv"
    if not src.exists():
        return
    cols = ["time_step", "sector", "production", "production_target", "production_capacity", "input_stock",
            "total_order", "imports"]
    parts = []
    for chunk in pd.read_csv(src, usecols=cols, chunksize=2_000_000):
        parts.append(chunk.groupby(["time_step", "sector"], as_index=False).sum(numeric_only=True))
    daily = pd.concat(parts).groupby(["time_step", "sector"], as_index=False).sum(numeric_only=True)
    daily.to_csv(folder / "firm_daily.csv", index=False)
    src.unlink()
    # household_data_by_sector.csv has no export switch: 1,621 households x ~60 sectors a day, ~1.6 GB for 180
    # days. Kept as sums by day and sector (household_data.csv keeps the per-household totals).
    hs = folder / "household_data_by_sector.csv"
    if hs.exists():
        parts = []
        for chunk in pd.read_csv(hs, chunksize=2_000_000):
            parts.append(chunk.drop(columns=["household"]).groupby(["time_step", "sector"], as_index=False)
                         .sum(numeric_only=True))
        pd.concat(parts).groupby(["time_step", "sector"], as_index=False).sum(numeric_only=True) \
            .to_csv(folder / "household_daily_by_sector.csv", index=False)
        hs.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scenario", default="none")
    ap.add_argument("--duration", type=int, default=12, help="closure length of each event (days)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--t-final", type=int, default=180)
    ap.add_argument("--footprint", choices=sorted(FOOTPRINTS), default="v3")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="config override (dotted key, YAML value); repeatable")
    ap.add_argument("--cache-dir", default=None, help="named build cache (default cam_s<seed>)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--setup", action="store_true", help="build (or check) the seed's cache and stop")
    ap.add_argument("--inventory-scale", type=float, default=None, metavar="X",
                    help="multiply every inventory duration target (inventory_duration_targets.values) by X")
    ap.add_argument("--keep-firm-data", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the run's record and stop")
    args = ap.parse_args()

    setup_logging("info")
    config = load_paper_config()
    for item in args.set:
        apply_set(config, item)
    if args.inventory_scale is not None:
        if args.inventory_scale <= 0:
            raise SystemExit(f"--inventory-scale must be positive, got {args.inventory_scale}")
        targets = config["inventory_duration_targets"]
        targets["values"] = {k: v * args.inventory_scale for k, v in targets["values"].items()}
    config["seed"] = args.seed
    gpkg = Path(config["filepaths"]["transport"]) if config.get("filepaths", {}).get("transport") else \
        paths.get_data_path(SCOPE) / "Transport" / "transport.gpkg"
    edges = check_footprint(gpkg, args.footprint)
    if args.setup:
        config["simulation_type"] = "initial_state"
        config["t_final"] = 1
        config["disruptions"] = []
        config["export_files"] = False
    else:
        config["t_final"] = args.t_final
        config["disruptions"] = disruptions(args.scenario, args.duration, args.footprint)
    cache_dir = args.cache_dir or f"cam_s{args.seed}"
    record = {"scope": SCOPE, "scenario": args.scenario, "duration": args.duration, "seed": args.seed,
              "t_final": config["t_final"], "footprint": args.footprint, "edges_per_basin": edges,
              "overrides": args.set, "inventory_scale": args.inventory_scale,
              "inventory_duration_targets": config["inventory_duration_targets"]["values"],
              "inventory_restoration_time": config["inventory_restoration_time"],
              "cache_dir": cache_dir, "config_hash": config_hash(config), **git_state(),
              "disruptions": config["disruptions"]}
    print(json.dumps(record, indent=1, default=str))
    if args.dry_run:
        return
    setup_cache_dir(cache_dir)
    out = None
    if not args.setup:
        out = args.out or (ROOT / "output" / SCOPE / "paper" / f"{args.scenario}_d{args.duration}_s{args.seed}")
        out.mkdir(parents=True, exist_ok=True)
        (out / "study_run.json").write_text(json.dumps(record, indent=1, default=str), encoding="utf-8")
    execute(config, cache="auto", export_folder=out, open_report=False)
    if out is not None and not args.keep_firm_data:
        summarise_firm_data(out)
    logging.info(f"Done: {out or 'cache ' + cache_dir}")


if __name__ == "__main__":
    main()
