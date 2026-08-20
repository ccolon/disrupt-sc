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

# Outcome columns and the seed: everything else in a shard is a swept parameter, and the
# grouping has to use ALL of them. Naming the config columns explicitly is what broke this
# before -- run_grid.py sweeps around twenty axes (inventory scales, activation time, capital
# ratio, buffer days, mechanism switches) but only eight were listed, so every configuration
# that happened to share those eight was pooled into one row. The baseline then absorbed
# ~1950 runs spanning quite different settings and reported a spread that belonged to no
# single configuration.
NOT_CONFIG = {
    "seed",
    "household_loss_pct_annual_gdp", "household_loss_mUSD", "gdp_loss_pct_annual_gdp",
    "did_sales_acute", "did_sales_recovery", "did_purchases_acute", "did_purchases_recovery",
    # a label for which axis a row belongs to, not a parameter: the same configuration is
    # reached from several axes (each axis re-runs the baseline), and those must merge
    "oat_param",
}


def main():
    ap = argparse.ArgumentParser(description="Aggregate sweep across Monte-Carlo seeds")
    ap.add_argument("--in", dest="inp", type=Path, required=True, help="CSV file or dir of shard CSVs")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--raw-out", type=Path, default=None,
                    help="also write the clean concatenated rows here (default: <out dir>/sensitivity_all.csv)")
    ap.add_argument("--metric", default="household_loss_pct_annual_gdp")
    args = ap.parse_args()

    if args.inp.is_dir():
        files = sorted(glob.glob(str(args.inp / "*.csv")))
        if not files:
            raise SystemExit(f"no CSVs in {args.inp}")
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    else:
        df = pd.read_csv(args.inp)

    # clean concatenated rows (single header) for the sensitivity plot
    raw_out = args.raw_out or (args.out.parent / "sensitivity_all.csv")
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_out, index=False)

    cfg = [c for c in df.columns if c not in NOT_CONFIG and c != args.metric]
    if not cfg:
        raise SystemExit("no configuration columns found — is this a sweep shard?")
    g = df.groupby(cfg, dropna=False)[args.metric]
    summ = g.agg(n_seeds="count", mean="mean", std="std",
                 p10=lambda s: s.quantile(0.10), p90=lambda s: s.quantile(0.90),
                 min="min", max="max").reset_index()
    summ = summ.round(4).sort_values("mean")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    summ.to_csv(args.out, index=False)

    # A group holding many more rows than there are seeds means some swept axis is still
    # missing from cfg, and that group's spread is pooling configurations rather than seeds.
    n_seed_values = df.seed.nunique() if "seed" in df.columns else None
    if n_seed_values:
        worst = int(summ.n_seeds.max())
        if worst > n_seed_values:
            over = summ.loc[summ.n_seeds > n_seed_values]
            print(f"WARNING: {len(over)} group(s) hold more rows than the {n_seed_values} seeds "
                  f"(largest {worst}). A swept parameter is probably missing from the shard "
                  f"columns, so those rows pool different configurations.")

    print(f"metric = {args.metric}   ({df.seed.nunique() if 'seed' in df else '?'} seeds, "
          f"{len(summ)} configs)")
    print(summ.to_string(index=False))
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
