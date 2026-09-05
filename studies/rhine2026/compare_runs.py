"""Side-by-side summary of Rhine scenario runs (paper table T2).

Same definitions as analyze_scenario.py section 5: a firm's loss in a week is its
production shortfall against its own t=0 production (clipped at zero), weighted by
the sector's value-added share (mrio_by_sector.csv); weekly value added of a
country is mrio_va / 52; "% of a quarter" divides by 13 weeks. Works on partial
runs (firm_data.csv is written every week).

Usage:
    python studies/rhine2026/compare_runs.py C:\\dsc_runs\\rhine2026\\2026_seed42_base C:\\dsc_runs\\rhine2026\\2026_seed42_floors
    python studies/rhine2026/compare_runs.py <run> ... --weekly DEU     # add the weekly DEU series
    python studies/rhine2026/compare_runs.py <run> ... --csv out.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def run_summary(run: Path, countries=("DEU", "NLD", "AUT", "FRA", "CHE", "BEL")) -> tuple[dict, pd.DataFrame]:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd["time_step"] == 0].set_index("firm")["production"]
    fd["base"] = fd["firm"].map(b0)
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    va_share = (va["mrio_va"] / va["mrio_output"]).to_dict()
    fd["va_loss"] = (fd["base"] - fd["production"]).clip(lower=0) * fd["sector"].map(va_share).fillna(0.3)
    by = fd.groupby(["time_step", "region"])["va_loss"].sum().unstack("region").fillna(0.0)
    weekly_va = pd.read_csv(run / "mrio_by_region.csv").set_index("region")["mrio_va"] / 52.0
    eu = by.sum(axis=1)
    live = fd[fd["base"] > 0]
    below = live.assign(low=live["production"] < 0.99 * live["base"]).groupby("time_step")["low"].mean() * 100
    hh = pd.read_csv(run / "household_data.csv", usecols=["time_step", "consumption_loss", "tot_consumption"])
    cl = hh.groupby("time_step")[["consumption_loss", "tot_consumption"]].sum()
    cl_pct = 100 * cl["consumption_loss"] / (cl["consumption_loss"] + cl["tot_consumption"])
    weeks = int(fd["time_step"].max())
    row = {"run": run.name, "weeks": weeks,
           "EU_cum_mUSD": round(eu.sum(), 0), "EU_%quarter": round(100 * eu.sum() / (weekly_va.sum() * 13), 3),
           "EU_peak_%week": round(100 * eu.max() / weekly_va.sum(), 3),
           "firms<99%_peak_%": round(below.max(), 2),
           "cons_loss_cum_mUSD": round(cl["consumption_loss"].sum(), 0), "cons_loss_peak_%": round(cl_pct.max(), 3)}
    for c in countries:
        if c in by.columns:
            s = by[c]
            row[f"{c}_cum_mUSD"] = round(s.sum(), 0)
            row[f"{c}_%quarter"] = round(100 * s.sum() / (weekly_va[c] * 13), 3)
            row[f"{c}_peak_%week"] = round(100 * s.max() / weekly_va[c], 3)
            row[f"{c}_peak_week"] = int(s.idxmax()) if s.max() > 0 else None
            row[f"{c}_loss_weeks"] = int((100 * s / weekly_va[c] > 0.01).sum())
    weekly = pd.DataFrame({"EU_mUSD": eu.round(1), **{c: by[c].round(1) for c in countries if c in by.columns},
                           "firms<99%": below.round(2), "cons_loss_%": cl_pct.round(3)})
    return row, weekly


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--weekly", default=None, help="country code: print the weekly VA-loss series (mUSD) per run")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()
    rows, weeklies = [], {}
    for r in args.runs:
        run = Path(r)
        if not run.exists():
            run = ROOT / "runs" / "rhine2026" / r
        row, weekly = run_summary(run)
        rows.append(row)
        weeklies[run.name] = weekly
    tab = pd.DataFrame(rows).set_index("run")
    pd.set_option("display.width", 250)
    print("== cumulated value-added loss (mUSD), % of a quarter, peak week (% of a week's VA), loss weeks (> 0.01 % of a week) ==")
    cols = [c for c in tab.columns if c.startswith(("weeks", "EU_", "DEU_", "firms", "cons"))]
    print(tab[cols].T.to_string())
    other = [c for c in tab.columns if c not in cols]
    if other:
        print("\n== other countries ==")
        print(tab[other].T.to_string())
    if args.weekly:
        print(f"\n== weekly value-added loss of {args.weekly} (mUSD/week) ==")
        w = pd.DataFrame({k: v[args.weekly] for k, v in weeklies.items() if args.weekly in v.columns})
        print(w.to_string())
    if args.csv:
        tab.to_csv(args.csv)
        print(f"\nwritten {args.csv}")


if __name__ == "__main__":
    main()
