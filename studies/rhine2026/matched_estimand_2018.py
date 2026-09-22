"""The 2018 calibration target on a matched estimand (22 Sep 2026, review point EC1).

What the ex-post literature measures. Ademmer, Jannsen and Meuchelboeck (German Economic Review 2023; Kiel WP 2155,
2020; Wirtschaftsdienst 2019) regress German INDUSTRIAL PRODUCTION (the Destatis index, NACE B-E) on the number of days
per month with Kaub below 78 cm: -0.034 % of IP per day in the same month and -0.024 % per day in the next month. Their
"decline in GDP of close to 0.4 percent" is the NOVEMBER 2018 LEVEL effect (IP 1.5-1.7 % below its counterfactual, times
an industry share of GVA of about a quarter), a lower bound that excludes the value added of shipping itself and the
spillovers to services. It is not an event-integrated loss, and it says nothing about services.

What the model reports. The paper's headline is the cumulated German value-added loss over the whole event, all sectors,
divided by 13 weeks of baseline value added ("% of a quarter"). Two thirds of that loss sits in services (transport,
logistics, power and gas, shipping). Comparing it with 0.3-0.4 % compared a total, integrated quantity with a
peak-month, industry-only level effect. The two happen to be similar numbers; they are not the same quantity.

The matched quantity, computed here for every 2018 run that carries firm data: the model's monthly shortfall of German
industrial production (NACE B-E, production-weighted), month by month, against the path implied by the published
coefficients and the 2018 low-water days (Wirtschaftsdienst 2019: Aug 30, Sep 15, Oct 30, Nov 30, Dec 3 days below
78 cm), with and without the lagged term. The integral of the record path is 6.2 %-months with the lag, 3.7 without.

Usage:
    python studies/rhine2026/matched_estimand_2018.py [--runs 2018_baseline,2018_inv150,2018_inv200] [--out FILE]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path("C:/dsc_runs/rhine2026")
FIRST = pd.Timestamp("2018-07-16")          # the 2018 profile: t = row + 1, t = 1 -> week of 16 July
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = {"Aug": 30, "Sep": 15, "Oct": 30, "Nov": 30, "Dec": 3}          # Kaub < 78 cm, Wirtschaftsdienst 2019
PREV = {"Aug": 0, "Sep": 30, "Oct": 15, "Nov": 30, "Dec": 30}
SAME, LAG = 0.034, 0.024                                                 # % of IP per low-water day, GER 2023 / WP 2155
INDUSTRY = ("B", "C", "D", "E")                                          # Destatis industry = NACE B-E (excl. construction)


def record_path() -> tuple[dict, dict]:
    with_lag = {m: round(SAME * DAYS[m] + LAG * PREV[m], 2) for m in MONTHS}
    contemporaneous = {m: round(SAME * DAYS[m], 2) for m in MONTHS}
    return with_lag, contemporaneous


def model_path(run: Path) -> dict:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm")["production"]
    fd = fd[(fd.region == "DEU") & (fd.time_step >= 1) & (fd.time_step <= 22)].copy()
    fd["base"] = fd.firm.map(b0)
    fd["month"] = (FIRST + pd.to_timedelta((fd.time_step - 1) * 7, unit="D")).dt.strftime("%b")
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    fd["va_share"] = fd.sector.map((va.mrio_va / va.mrio_output).to_dict()).fillna(0.3)
    fd["is_ind"] = fd.sector.astype(str).str[:1].isin(INDUSTRY)
    out = {}
    for m in MONTHS:
        w = fd[fd.month == m]
        i = w[w.is_ind]
        out[f"ind_{m}"] = round(100 * (i.base - i.production).sum() / i.base.sum(), 2)
        out[f"va_{m}"] = round(100 * ((w.base - w.production) * w.va_share).sum() / (w.base * w.va_share).sum(), 2)
        out[f"weeks_{m}"] = int(w.time_step.nunique())
    out["ind_integrated_pct_months"] = round(sum(out[f"ind_{m}"] * out[f"weeks_{m}"] / 4.345 for m in MONTHS), 2)
    loss = ((fd.base - fd.production) * fd.va_share).clip(lower=0)
    out["ind_share_of_total_va_loss_pct"] = round(100 * loss[fd.is_ind].sum() / loss.sum(), 0)
    out["peak_month_ind"] = max(MONTHS, key=lambda m: out[f"ind_{m}"])
    return out


def main(runs: list[str], out: Path | None):
    lag, cont = record_path()
    lines = ["Record (Ademmer et al., implied monthly shortfall of German industrial production, %):",
             f"  with the lagged term      : {lag}  integrated {sum(lag.values()):.2f} %-months; peak Nov {lag['Nov']:.2f} (published: 1.5-1.7)",
             f"  contemporaneous term only : {cont} integrated {sum(cont.values()):.2f} %-months",
             f"  in the paper's unit (x industry share of GVA 0.25, / 3 months): {sum(lag.values())*0.25/3:.2f} and {sum(cont.values())*0.25/3:.2f} % of a quarter, INDUSTRY CHANNEL ONLY",
             ""]
    rows = []
    for r in runs:
        p = RUNS / r
        if not (p / "firm_data.csv").exists():
            lines.append(f"{r}: no firm_data.csv"); continue
        d = model_path(p); d["run"] = r; rows.append(d)
    t = pd.DataFrame(rows).set_index("run")
    pd.set_option("display.width", 220)
    lines.append("Model, Germany, monthly shortfall of INDUSTRIAL production (NACE B-E, production-weighted, % of the month's baseline):")
    lines.append(t[[f"ind_{m}" for m in MONTHS] + ["ind_integrated_pct_months", "peak_month_ind", "ind_share_of_total_va_loss_pct"]].to_string())
    lines.append("")
    lines.append("Model, Germany, monthly shortfall of TOTAL value added (all sectors, %):")
    lines.append(t[[f"va_{m}" for m in MONTHS]].to_string())
    text = "\n".join(lines)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8"); print("written", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="2018_baseline,2018_inv150,2018_inv200")
    ap.add_argument("--out", default=str(ROOT / "studies/rhine2026/additional_data/matched_estimand_2018.txt"))
    a = ap.parse_args()
    main(a.runs.split(","), Path(a.out) if a.out else None)
