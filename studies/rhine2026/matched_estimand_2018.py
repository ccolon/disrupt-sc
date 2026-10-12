"""The matched estimand: the model's monthly shortfall of German industrial production (22 Sep 2026, review EC1;
rebuilt 6 Oct 2026 on one integration rule, review of 5 Oct, points E1 and E2).

What the ex-post literature measures. Ademmer, Jannsen and Meuchelboeck (German Economic Review 2023; Kiel WP 2155,
2020) regress the growth of German INDUSTRIAL PRODUCTION (the Destatis index, NACE B-E) on the change in the number of
days per month with Kaub below 78 cm, with a lagged term and an autoregressive term. Their 2018 counterfactual is a
monthly path of the production level below its no-low-water counterfactual, peaking in November at 1.5 %. It is an
industry-only quantity: a lower bound that excludes the value added of shipping and the spillovers to services, as the
authors say. The path and its uncertainty are rebuilt in benchmark_ademmer.py.

What the model reports. The paper's headline is the cumulated German value-added loss over the whole event, all
sectors, divided by 13 weeks of baseline value added ("% of a quarter"). About half of that loss sits outside industry.
Comparing it with the November level effect would compare a total, integrated quantity with a peak-month,
industry-only level; they are not the same quantity.

The matched quantity, computed here for every run that carries firm data: the model's shortfall of German industrial
production (NACE B-E, production-weighted over the German industrial firms) week by week, turned into calendar months
by the days: every day of a month takes the value of the model week it belongs to, and the month is the mean of its
days. The integral over the event months (August to December 2018; July to December 2026) is the plain sum of the
monthly values, in percent-months, the same operation as on the record. (The rule until 5 Oct 2026 assigned the weeks
to months by their start date and weighted each month by its number of run weeks over 4.345, which is not what the
record's integral does; the review of 5 Oct found the printed integrals inconsistent with the monthly values.)

Usage:
    python studies/rhine2026/matched_estimand_2018.py [--runs 2018_s07_base,...] [--year 2018|2026] [--out FILE]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from va_shares import add_va_share  # noqa: E402  country-sector value-added ratios (12 Oct 2026, review E1)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = Path("C:/dsc_runs/rhine2026")
sys.path.insert(0, str(HERE))
from benchmark_ademmer import EVENT_MONTHS, record  # noqa: E402

FIRST = {2018: pd.Timestamp("2018-07-16"), 2026: pd.Timestamp("2026-06-22")}   # the date of model week t = 1
INDUSTRY = ("B", "C", "D", "E")                                                 # Destatis industry = NACE B-E
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec"]                                    # the five event months of 2018


INDEX_SECTIONS = ("B", "C", "D")      # the production index of industry: NACE B to D (and E36, not separable here)


def weekly_shortfall(run: Path, region: str = "DEU") -> tuple[pd.Series, pd.Series]:
    """(industrial shortfall on the production-index measure, total value-added shortfall) by model week, % of the
    baseline, for *region*. The index measure (12 Oct 2026, review E2): each sector's shortfall rate (production-weighted
    within the sector) weighted by the sector's value added IN THAT COUNTRY, sections B to D, as the Destatis production
    index aggregates its sectoral indices. The earlier production-weighted B-E series is weekly_shortfall_prod()."""
    s_idx, _, s_va = _series(run, region)
    return s_idx, s_va


def weekly_shortfall_prod(run: Path, region: str = "DEU") -> pd.Series:
    """The production-weighted B-E industrial shortfall by week (the measure of the paper until 12 Oct 2026)."""
    return _series(run, region)[1]


def _series(run: Path, region: str = "DEU") -> tuple[pd.Series, pd.Series, pd.Series]:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm")["production"]
    fd = fd[(fd.region == region) & (fd.time_step >= 1)].copy()
    fd["base"] = fd.firm.map(b0)
    add_va_share(fd, run)
    fd["short"] = fd.base - fd.production
    s_va = 100 * (fd.short * fd.va_share).groupby(fd.time_step).sum() / (fd.base * fd.va_share).groupby(fd.time_step).sum()
    ind = fd[fd.sector.astype(str).str[:1].isin(INDUSTRY)]
    s_prod = 100 * ind.short.groupby(ind.time_step).sum() / ind.base.groupby(ind.time_step).sum()
    idx = fd[fd.sector.astype(str).str[:1].isin(INDEX_SECTIONS)]
    sec = idx.groupby(["time_step", "sector"]).agg(short=("short", "sum"), base=("base", "sum")).reset_index()
    sec["rate"] = sec.short / sec.base
    w = (idx[idx.time_step == idx.time_step.min()].assign(va=lambda d: d.base * d.va_share).groupby("sector").va.sum())   # the sector's value added in *region*
    sec["w"] = sec.sector.map(w)
    s_idx = 100 * (sec.rate * sec.w).groupby(sec.time_step).sum() / sec.w.groupby(sec.time_step).sum()
    return s_idx, s_prod, s_va


def monthly_from_weekly(s: pd.Series, first: pd.Timestamp, months: list[str]) -> tuple[dict, dict]:
    """Day-weighted calendar months of a weekly series (week t covers first + 7(t-1) days .. + 6 days).
    Returns ({month: value}, {month: days covered})."""
    days = {}
    for t, v in s.items():
        w0 = first + pd.Timedelta(days=7 * (int(t) - 1))
        for k in range(7):
            days[w0 + pd.Timedelta(days=k)] = float(v)
    d = pd.Series(days)
    per = d.index.to_period("M").astype(str)
    out = {m: float(d[per == m].mean()) if (per == m).any() else float("nan") for m in months}
    cov = {m: int((per == m).sum()) for m in months}
    return out, cov


def model_path(run: Path, year: int = 2018) -> dict:
    """Monthly industrial and total shortfalls (%), the integral over the event months (percent-months), the peak
    month and the industrial share of the value-added loss. Keys as in the printed tables (ind_Aug, ...)."""
    s_ind, s_prod, s_va = _series(run)
    months = EVENT_MONTHS[year]
    ind, cov = monthly_from_weekly(s_ind, FIRST[year], months)
    prod, _ = monthly_from_weekly(s_prod, FIRST[year], months)
    va, _ = monthly_from_weekly(s_va, FIRST[year], months)
    out = {}
    for m in months:
        lab = pd.Timestamp(m + "-01").strftime("%b")
        out[f"ind_{lab}"] = round(ind[m], 2)            # the production-index measure (German value-added weights, B-D)
        out[f"indprod_{lab}"] = round(prod[m], 2)       # production-weighted B-E (the measure until 12 Oct 2026)
        out[f"va_{lab}"] = round(va[m], 2)
        out[f"days_{lab}"] = cov[m]
    out["ind_integrated_pct_months"] = round(sum(ind[m] for m in months), 2)
    out["indprod_integrated_pct_months"] = round(sum(prod[m] for m in months), 2)
    out["peak_month_ind"] = pd.Timestamp(max(months, key=lambda m: ind[m]) + "-01").strftime("%b")
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm")["production"]
    fd = fd[(fd.region == "DEU") & (fd.time_step >= 1)].copy(); fd["base"] = fd.firm.map(b0)
    add_va_share(fd, run)
    loss = ((fd.base - fd.production) * fd.va_share).clip(lower=0)
    is_ind = fd.sector.astype(str).str[:1].isin(INDUSTRY)
    out["ind_share_of_total_va_loss_pct"] = round(100 * loss[is_ind].sum() / loss.sum(), 0) if loss.sum() > 0 else float("nan")
    return out


def record_lines(year: int) -> list[str]:
    t, s = record(year, 1)
    ev = t[t.month.isin(EVENT_MONTHS[year])]
    labs = [pd.Timestamp(m + "-01").strftime("%b") for m in ev.month]
    lines = [f"Record (Ademmer et al., dynamic counterfactual of the published specification, column 1; shortfall of German industrial production, %):",
             "  central        : " + ", ".join(f"{l} {v:.2f}" for l, v in zip(labs, ev.central)) + f"  integrated {s['integral']:.2f} %-months; peak {s['peak_month'][5:]} {s['peak']:.2f} (published: 1.5)",
             "  16-84 % band   : " + ", ".join(f"{l} {a:.2f}-{b:.2f}" for l, a, b in zip(labs, ev.p16, ev.p84)) + f"  integral {s['p16']:.2f}-{s['p84']:.2f}",
             "  2.5-97.5 % band: integral " + f"{s['p2_5']:.2f}-{s['p97_5']:.2f}"]
    for col in (2, 3, 4):
        t2, s2 = record(year, col, draws=1)
        ev2 = t2[t2.month.isin(EVENT_MONTHS[year])]
        lines.append(f"  column {col}       : " + ", ".join(f"{l} {v:.2f}" for l, v in zip(labs, ev2.central)) + f"  integrated {s2['integral']:.2f}")
    return lines


def main(runs: list[str], out: Path | None, year: int):
    lines = record_lines(year) + [""]
    rows = []
    for r in runs:
        p = RUNS / r
        if not (p / "firm_data.csv").exists():
            lines.append(f"{r}: no firm_data.csv"); continue
        d = model_path(p, year); d["run"] = r; rows.append(d)
    t = pd.DataFrame(rows).set_index("run")
    pd.set_option("display.width", 250)
    labs = [pd.Timestamp(m + "-01").strftime("%b") for m in EVENT_MONTHS[year]]
    lines.append(f"Model, Germany, monthly shortfall of INDUSTRIAL production on the production-index measure (NACE B-D, sector rates weighted by the German sector value added; % of the month's baseline; days of the month covered by the run in days_*):")
    lines.append(t[[f"ind_{m}" for m in labs] + ["ind_integrated_pct_months", "peak_month_ind", "ind_share_of_total_va_loss_pct"]].to_string())
    lines.append("")
    lines.append("Model, Germany, monthly shortfall of TOTAL value added (all sectors, %):")
    lines.append(t[[f"va_{m}" for m in labs]].to_string())
    lines.append("")
    lines.append("Days of each month covered by the run:")
    lines.append(t[[f"days_{m}" for m in labs]].to_string())
    text = "\n".join(lines)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8"); print("written", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="2018_s07_base")
    ap.add_argument("--year", type=int, default=2018)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    main(a.runs.split(","), Path(a.out) if a.out else None, a.year)
