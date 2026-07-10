"""Multi-model GDP-impact comparison table: the DisruptSC row (+ template).

DisruptSC household loss (% of GDP): a central-config Monte-Carlo estimate reported
as mean [p10-p90] across seeds, plus the sensitivity range (min-max of config means
across the swept parameters). Other model families (IO, CGE, ...) are placeholder
rows for the other teams to fill in. Reads sensitivity_summary.csv (combine.py).

CLI:
  python plot_model_table.py --summary sensitivity_summary.csv --out models_table.csv \
      [--central utilization_rate=0.8 reconstruction_market=True reconstruction_public_share=0.8]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _coerce(col: pd.Series, v: str):
    if col.dtype == bool:
        return str(v).lower() in ("true", "1", "yes", "on")
    try:
        return col.dropna().iloc[0].__class__(v)
    except Exception:
        return v


def main():
    ap = argparse.ArgumentParser(description="Multi-model comparison table (DisruptSC row + template)")
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--central", nargs="*", default=[], help="key=value filters for the central config")
    args = ap.parse_args()

    s = pd.read_csv(args.summary)

    sel = s.copy()
    for kv in args.central:
        k, v = kv.split("=", 1)
        if k in sel.columns:
            sel = sel[sel[k] == _coerce(sel[k], v)]
    if len(sel) == 0:                                    # fall back to the median-loss config
        med = s["mean"].median()
        sel = s.loc[[(s["mean"] - med).abs().idxmin()]]
    central = sel.iloc[0]

    disruptsc = {
        "model": "DisruptSC (network-firm ABM)",
        "central_mean_pct_gdp": round(float(central["mean"]), 3),
        "p10_pct_gdp": round(float(central["p10"]), 3),
        "p90_pct_gdp": round(float(central["p90"]), 3),
        "sensitivity_min_pct_gdp": round(float(s["mean"].min()), 3),
        "sensitivity_max_pct_gdp": round(float(s["mean"].max()), 3),
        "n_seeds": int(central.get("n_seeds", 0)),
    }
    others = [{"model": m} for m in ("IO model", "CGE model", "Other network model")]
    table = pd.DataFrame([disruptsc] + others)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out, index=False)

    print(f"DisruptSC household loss = {disruptsc['central_mean_pct_gdp']:.2f}% of GDP "
          f"[{disruptsc['p10_pct_gdp']:.2f}-{disruptsc['p90_pct_gdp']:.2f}] "
          f"(MC p10-p90, {disruptsc['n_seeds']} seeds); "
          f"sensitivity range {disruptsc['sensitivity_min_pct_gdp']:.2f}-"
          f"{disruptsc['sensitivity_max_pct_gdp']:.2f}%")
    print(table.to_string(index=False))
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
