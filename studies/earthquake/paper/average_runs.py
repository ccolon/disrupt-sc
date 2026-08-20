"""Average analyzer CSVs across Monte-Carlo seed run dirs (for the reference figures).

For each known analyzer CSV (from distribution.py / uq_did.py, run per seed), concat
across the given seed dirs, group by the key columns, and average the numeric value
columns. Writes the averaged CSVs to --out-dir, which the plotters then consume.

CLI:
  python average_runs.py --glob "output/earthquake_paper/reference/seed_*" --out-dir figures/ref_avg
  python average_runs.py --dirs run_a run_b run_c --out-dir figures/ref_avg
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd

# analyzer CSV -> key (grouping) columns; everything else numeric is averaged
FILES = {
    "loss_by_sector_time.csv": ["isic", "time_step", "sector_label"],
    "loss_by_province_year.csv": ["province"],
    "loss_by_canton_year.csv": ["canton", "province", "canton_name"],
    # "measure" separates the b2b and total variants; without it here the two would be
    # averaged together into a number belonging to neither
    "uq_eventstudy.csv": ["measure", "outcome", "mmi_bin", "time_step", "tau"],
    "uq_did.csv": ["measure", "outcome", "window"],
}


def main():
    ap = argparse.ArgumentParser(description="Average analyzer CSVs across seed runs")
    ap.add_argument("--dirs", nargs="*", type=Path, default=None)
    ap.add_argument("--glob", type=str, default=None)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    dirs = list(args.dirs) if args.dirs else [Path(p) for p in sorted(glob.glob(args.glob or ""))]
    dirs = [d for d in dirs if d.is_dir()]
    if not dirs:
        raise SystemExit("no seed dirs found")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"averaging across {len(dirs)} seed dirs")

    for fname, keys in FILES.items():
        frames = [pd.read_csv(d / fname) for d in dirs if (d / fname).exists()]
        if not frames:
            print(f"  skip {fname} (not found in any seed dir)")
            continue
        df = pd.concat(frames, ignore_index=True)
        keys = [k for k in keys if k in df.columns]
        val_cols = [c for c in df.columns if c not in keys and pd.api.types.is_numeric_dtype(df[c])]
        avg = df.groupby(keys, as_index=False)[val_cols].mean()
        avg["n_seeds"] = len(frames)
        avg.to_csv(args.out_dir / fname, index=False)
        print(f"  {fname}: {len(frames)} seeds -> {len(avg)} rows")
    print(f"-> {args.out_dir}")


if __name__ == "__main__":
    main()
