"""Merge per-shard event-loss CSVs into one event_losses.csv.

Run standalone or as the SLURM combine job:
    python studies/TENT/combine_shards.py --dir <output_dir> --num-shards 24 \
        --out <output_dir>/event_losses.csv
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="dir holding event_losses_shard*of*.csv")
    ap.add_argument("--num-shards", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    pattern = str(Path(args.dir) / f"event_losses_shard*of{args.num_shards}.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"No shard CSVs matched {pattern}")

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.drop_duplicates(["catchment", "return_period"]).sort_values(
        ["return_period", "catchment"])
    df.to_csv(args.out, index=False)
    print(f"combined {len(df)} events from {len(files)} shard file(s) -> {args.out}")
    expected = 917
    if len(df) != expected:
        print(f"NOTE: {len(df)} events (expected {expected}); some shards may be incomplete.")


if __name__ == "__main__":
    main()
