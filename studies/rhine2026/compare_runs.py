"""Side-by-side summary of Rhine scenario runs (paper table T2).

Same definitions as analyze_scenario.py section 5: a firm's loss in a week is its
production shortfall against its own t=0 production (clipped at zero), weighted by
the sector's value-added share (mrio_by_sector.csv); weekly value added of a
country is mrio_va / 52; "% of a quarter" divides by 13 weeks. Works on partial
runs (firm_data.csv is written every week).

Accounting (9 Sep 2026): besides the GROSS loss (weekly shortfalls clipped at zero)
the summary reports the NET loss and the DELAY COST. Firms refill their input stocks
after a shock, so suppliers of storable goods produce above baseline afterwards; for
the deferrable sectors (goods and construction, NACE A-F) the backlog B_t =
max(0, B_{t-1} + shortfall_t) is worked off and only the backlog left at the end of
the run is a net loss, while the weeks it stays outstanding cost a carrying rate
(default 13 %/yr, the inventory cost of capital used for the value of time). For the
perishable sectors (utilities, trade, transport, hospitality and other services,
NACE D-E and G-T) a lost week is lost: net = gross. Household consumption loss stays
gross by construction (households do not re-order).

Usage:
    python studies/rhine2026/compare_runs.py C:\\dsc_runs\\rhine2026\\2026_seed42_base C:\\dsc_runs\\rhine2026\\2026_seed42_floors
    python studies/rhine2026/compare_runs.py <run> ... --weekly DEU     # add the weekly DEU series
    python studies/rhine2026/compare_runs.py <run> ... --csv out.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFERRABLE_PREFIXES = ("A", "B", "C", "F")     # goods and construction: backlog is worked off


def is_deferrable(sector: str) -> bool:
    return str(sector)[:1] in DEFERRABLE_PREFIXES


def loss_accounting(fd: pd.DataFrame, rate_per_year: float = 0.13) -> pd.DataFrame:
    """Per firm: gross loss, net loss and delay cost of value added over the run.

    *fd* needs columns firm, sector, region, time_step, base, production, va_share.
    gross = sum of max(base - production, 0) x va_share; for deferrable sectors
    net = backlog left at the last step (B_t = max(0, B_{t-1} + shortfall_t)) x va_share
    and delay = sum_t B_t x va_share x rate_per_week; for perishable sectors net = gross,
    delay = 0.
    """
    r_week = rate_per_year / 52.0
    piv = fd.pivot_table(index="firm", columns="time_step", values="production", aggfunc="sum").sort_index(axis=1)
    meta = fd.drop_duplicates("firm").set_index("firm")[["sector", "region", "base", "va_share"]].reindex(piv.index)
    short = (meta["base"].to_numpy()[:, None] - piv.to_numpy())          # signed weekly shortfall (output units)
    short = np.nan_to_num(short, nan=0.0)
    gross = np.clip(short, 0, None).sum(axis=1)
    backlog = np.zeros(short.shape[0])
    delay_units = np.zeros(short.shape[0])
    for t in range(short.shape[1]):
        backlog = np.maximum(0.0, backlog + short[:, t])
        delay_units += backlog
    deferrable = meta["sector"].map(is_deferrable).to_numpy()
    net = np.where(deferrable, backlog, gross)
    delay = np.where(deferrable, delay_units * r_week, 0.0)
    va = meta["va_share"].to_numpy()
    out = meta[["sector", "region"]].copy()
    out["gross"] = gross * va
    out["net"] = net * va
    out["delay"] = delay * va
    out["deferrable"] = deferrable
    return out


def run_summary(run: Path, countries=("DEU", "NLD", "AUT", "FRA", "CHE", "BEL"),
                rate_per_year: float = 0.13) -> tuple[dict, pd.DataFrame]:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd["time_step"] == 0].set_index("firm")["production"]
    fd["base"] = fd["firm"].map(b0)
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    va_share = (va["mrio_va"] / va["mrio_output"]).to_dict()
    fd["va_share"] = fd["sector"].map(va_share).fillna(0.3)
    fd["va_loss"] = (fd["base"] - fd["production"]).clip(lower=0) * fd["va_share"]
    acc = loss_accounting(fd, rate_per_year)
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
    for c in list(countries) + ["EU"]:
        a = acc if c == "EU" else acc[acc["region"] == c]
        if len(a):
            row[f"{c}_net_mUSD"] = round(a["net"].sum(), 0)
            row[f"{c}_delay_mUSD"] = round(a["delay"].sum(), 1)
            row[f"{c}_net_deferrable_mUSD"] = round(a.loc[a["deferrable"], "net"].sum(), 0)
            row[f"{c}_gross_perishable_mUSD"] = round(a.loc[~a["deferrable"], "gross"].sum(), 0)
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
    ap.add_argument("--rate", type=float, default=0.13, help="annual carrying rate of the backlog (delay cost)")
    args = ap.parse_args()
    rows, weeklies = [], {}
    for r in args.runs:
        run = Path(r)
        if not run.exists():
            run = ROOT / "runs" / "rhine2026" / r
        row, weekly = run_summary(run, rate_per_year=args.rate)
        rows.append(row)
        weeklies[run.name] = weekly
    tab = pd.DataFrame(rows).set_index("run")
    pd.set_option("display.width", 250)
    print("== cumulated value-added loss (mUSD), % of a quarter, peak week (% of a week's VA), loss weeks (> 0.01 % of a week) ==")
    print("   gross = weekly shortfalls clipped at zero; net = backlog left at the end for goods and construction (A-F)"
          " + gross for the perishable sectors; delay = carrying cost of the backlog while outstanding")
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
