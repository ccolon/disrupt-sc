"""Parallel orchestrator for the TENT flood-event sweep.

Ensures the baseline snapshot is built/cached once, then spawns N worker
processes, each running a disjoint shard of events (``run_sweep.py --shard k
--of N``) into its own CSV. When all workers finish, merges the shard CSVs into
a single ``event_losses.csv``. Each worker is independently resumable, so a
crashed/killed worker just re-runs its remaining events on the next launch.

Usage:
  python studies/TENT/run_parallel.py --workers 6
  python studies/TENT/run_parallel.py --workers 6 --combine-only   # just merge shards
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from studies.TENT.run_sweep import (                       # noqa: E402
    OUT_DIR, OUT_DEFAULT, SNAPSHOT_DEFAULT, build_or_load_snapshot)
from disruptsc.config import load_config, setup_logging    # noqa: E402

PY = sys.executable
SWEEP = str(ROOT / "studies" / "TENT" / "run_sweep.py")


def combine(workers: int, out_path: Path):
    parts = []
    for k in range(workers):
        p = OUT_DEFAULT.with_name(f"event_losses_shard{k}of{workers}.csv")
        if p.exists():
            parts.append(pd.read_csv(p))
    if not parts:
        print("No shard CSVs found to combine.")
        return
    df = pd.concat(parts, ignore_index=True).sort_values(["return_period", "catchment"])
    df.to_csv(out_path, index=False)
    print(f"Combined {len(df)} events from {len(parts)} shards -> {out_path}")


def main():
    ap = argparse.ArgumentParser(description="TENT flood sweep — parallel orchestrator")
    ap.add_argument("--workers", type=int, default=6, help="number of parallel shards")
    ap.add_argument("--xlsx", default=None, help="event table path override")
    ap.add_argument("--return-periods", type=int, nargs="+", default=None)
    ap.add_argument("--combine-only", action="store_true")
    args = ap.parse_args()

    setup_logging("info")
    out_path = OUT_DEFAULT

    if args.combine_only:
        combine(args.workers, out_path)
        return

    # 1. Build/cache the snapshot ONCE before fanning out (workers then just load it).
    config = load_config("TENT")
    config["time_resolution"] = "day"
    config["simulation_type"] = "disruption"
    if not SNAPSHOT_DEFAULT.exists():
        print("Snapshot missing — building once before spawning workers…")
        build_or_load_snapshot(config, SNAPSHOT_DEFAULT)

    # 2. Spawn workers.
    logs_dir = OUT_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    procs = []
    for k in range(args.workers):
        cmd = [PY, SWEEP, "--shard", str(k), "--of", str(args.workers)]
        if args.xlsx:
            cmd += ["--xlsx", args.xlsx]
        if args.return_periods:
            cmd += ["--return-periods", *map(str, args.return_periods)]
        log = open(logs_dir / f"shard{k}of{args.workers}.log", "w")
        print("spawn:", " ".join(cmd))
        procs.append((k, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT), log))

    # 3. Wait for all, report exit codes.
    print(f"\n{args.workers} workers running. Progress: tail the per-shard logs in {logs_dir}")
    t0 = time.time()
    failures = []
    for k, p, log in procs:
        rc = p.wait()
        log.close()
        print(f"worker {k}: exit {rc} (elapsed {(time.time()-t0)/3600:.1f} h)")
        if rc != 0:
            failures.append(k)

    # 4. Combine.
    combine(args.workers, out_path)
    if failures:
        print(f"WARNING: workers {failures} exited non-zero — re-run to resume their shards.")


if __name__ == "__main__":
    main()
