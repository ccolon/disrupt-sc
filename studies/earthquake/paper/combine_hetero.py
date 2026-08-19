"""Concatenate the per-seed heterogeneity shards and summarise by resolution.

Reads every ``hetero_s*.csv`` written by ``run_hetero.py`` and emits:

  --raw-out   every (seed, resolution, draw) row, concatenated
  --out       one row per (resolution, horizon): the mean and coefficient of
              variation of the loss ACROSS DRAWS, which is what Fig. 6 reports

The coefficient of variation is computed on the seed-averaged loss of each draw.
Averaging over seeds first removes network noise from the statistic, so the
dispersion that remains is draw-to-draw heterogeneity -- the quantity the figure
is about. The homogeneous reference is reported separately rather than pooled
into any resolution.
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd

HORIZONS = (3, 6, 12)
METRICS = ("household", "government", "investment", "va")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="indir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--raw-out", type=Path, required=True)
    args = ap.parse_args()

    files = sorted(glob.glob(str(args.indir / "hetero_s*.csv")))
    if not files:
        raise SystemExit(f"no hetero_s*.csv in {args.indir}")
    raw = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    raw = raw.drop_duplicates(["seed", "resolution", "draw_id"], keep="last")
    args.raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(args.raw_out, index=False)
    print(f"{len(raw)} rows over {raw.seed.nunique()} seeds, "
          f"{raw.resolution.nunique()} resolutions -> {args.raw_out}")

    # average over seeds within each draw, then describe the spread across draws
    keys = ["resolution", "draw_id"]
    per_draw = raw.groupby(keys, as_index=False).mean(numeric_only=True)

    rows = []
    for res, g in per_draw.groupby("resolution"):
        for m in HORIZONS:
            for metric in METRICS:
                col = f"{metric}_loss_pct_gdp_{m}m"
                if col not in g:
                    continue
                s = g[col].dropna()
                if s.empty:
                    continue
                mean = float(s.mean())
                rows.append({
                    "resolution": res, "horizon_months": m, "metric": metric,
                    "n_draws": int(len(s)), "mean_pct_gdp": round(mean, 5),
                    "std_pct_gdp": round(float(s.std(ddof=1)), 5) if len(s) > 1 else 0.0,
                    "coef_var": round(float(s.std(ddof=1)) / mean, 5) if len(s) > 1 and mean else 0.0,
                    "p10_pct_gdp": round(float(s.quantile(0.10)), 5),
                    "median_pct_gdp": round(float(s.median()), 5),
                    "p90_pct_gdp": round(float(s.quantile(0.90)), 5),
                })
    out = pd.DataFrame(rows).sort_values(["metric", "horizon_months", "resolution"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"wrote {args.out}")

    ref = out[(out.resolution == "homogeneous") & (out.metric == "household")]
    show = out[(out.metric == "household") & (out.horizon_months == 12)]
    if not ref.empty:
        r12 = ref[ref.horizon_months == 12].mean_pct_gdp
        print(f"\nhomogeneous reference, household loss at 12m: "
              f"{float(r12.iloc[0]):.3f}% of GDP" if len(r12) else "")
    print("\nhousehold loss at 12 months, by resolution:")
    for _, r in show.iterrows():
        print(f"  {r.resolution:<18} n={r.n_draws:>3}  mean {r.mean_pct_gdp:6.3f}%  CV {r.coef_var:5.2f}")


if __name__ == "__main__":
    main()
