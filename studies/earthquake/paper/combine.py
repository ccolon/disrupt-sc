"""Combine sweep shards and aggregate across Monte-Carlo seeds.

Reads sensitivity_losses.csv (or all *.csv in a directory, for SLURM shards),
groups by the config parameters (everything except seed + loss columns), and
reports the Monte-Carlo mean / std / p10 / p90 / min / max of the metric across
seeds. This is the DisruptSC uncertainty band for the multi-model table.

CLI:
  python combine.py --in <csv|dir> --out sensitivity_summary.csv [--metric COL]
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd

CONFIG = ["flow_coverage", "nb_suppliers_per_input", "utilization_rate", "reconstruction_market",
          "reconstruction_public_share", "reconstruction_target_time", "reconstruction_lag"]


def main():
    ap = argparse.ArgumentParser(description="Aggregate sweep across Monte-Carlo seeds")
    ap.add_argument("--in", dest="inp", type=Path, required=True, help="CSV file or dir of shard CSVs")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--metric", default="household_loss_pct_annual_gdp")
    args = ap.parse_args()

    if args.inp.is_dir():
        files = sorted(glob.glob(str(args.inp / "*.csv")))
        if not files:
            raise SystemExit(f"no CSVs in {args.inp}")
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    else:
        df = pd.read_csv(args.inp)

    cfg = [c for c in CONFIG if c in df.columns]
    g = df.groupby(cfg, dropna=False)[args.metric]
    summ = g.agg(n_seeds="count", mean="mean", std="std",
                 p10=lambda s: s.quantile(0.10), p90=lambda s: s.quantile(0.90),
                 min="min", max="max").reset_index()
    summ = summ.round(4).sort_values("mean")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    summ.to_csv(args.out, index=False)

    print(f"metric = {args.metric}   ({df.seed.nunique() if 'seed' in df else '?'} seeds, "
          f"{len(summ)} configs)")
    print(summ.to_string(index=False))
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
