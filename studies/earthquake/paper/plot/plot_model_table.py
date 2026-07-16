"""Multi-model GDP-impact comparison table: the DisruptSC row (+ template).

DisruptSC household loss (% of GDP) is a central-config Monte-Carlo estimate reported
as mean [p10-p90] across the REFERENCE seed runs (the same full-export runs that feed
the distribution/UQ figures) — self-contained, independent of the sensitivity sweep.
Each seed's total loss is the sum of loss_by_province_year.pct_gdp (= total household
consumption loss as % of annual GDP). Other model families are placeholder rows.

CLI:
  python plot_model_table.py --ref-glob 'output/.../reference/seed_*' --out models_table.csv
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np
import pandas as pd

TOTAL_FILE = "loss_by_province_year.csv"   # sum of pct_gdp = total household loss % of GDP


def main():
    ap = argparse.ArgumentParser(description="Multi-model comparison table (DisruptSC row + template)")
    ap.add_argument("--ref-glob", required=True, help="glob of reference seed dirs (each holds "
                                                      f"{TOTAL_FILE} from analyze/distribution.py)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    totals = []
    for d in sorted(glob.glob(args.ref_glob)):
        f = Path(d) / TOTAL_FILE
        if f.exists():
            totals.append(float(pd.read_csv(f)["pct_gdp"].sum()))
    if not totals:
        raise SystemExit(f"no {TOTAL_FILE} found under {args.ref_glob} — run analyze/distribution.py per seed first")
    t = np.array(totals)

    disruptsc = {
        "model": "DisruptSC (network-firm ABM)",
        "central_mean_pct_gdp": round(float(t.mean()), 3),
        "p10_pct_gdp": round(float(np.quantile(t, 0.10)), 3),
        "p90_pct_gdp": round(float(np.quantile(t, 0.90)), 3),
        "min_pct_gdp": round(float(t.min()), 3),
        "max_pct_gdp": round(float(t.max()), 3),
        "n_seeds": int(t.size),
    }
    others = [{"model": m} for m in ("IO model", "CGE model", "Other network model")]
    table = pd.DataFrame([disruptsc] + others)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out, index=False)

    print(f"DisruptSC household loss = {disruptsc['central_mean_pct_gdp']:.2f}% of GDP "
          f"[{disruptsc['p10_pct_gdp']:.2f}-{disruptsc['p90_pct_gdp']:.2f}] "
          f"(central config, MC p10-p90 over {disruptsc['n_seeds']} reference seeds)")
    print(table.to_string(index=False))
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
