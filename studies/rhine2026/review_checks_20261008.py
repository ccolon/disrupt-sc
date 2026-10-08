"""Checks for the review of 8 October 2026 (review_20261008): facts the rewrite needs and that no table prints.

  1. pairwise ordering of the levers on the ten further draws (OR2): stock7 vs deep20, fleet last, fleet vs stock7t
  2. the fleet's peak week against the base on every draw (caption of Fig. levers)
  3. the industrial series re-aggregated with value-added weights against the production-weighted one (E1):
     2018 monthly path and integral, 2026 prospective path, reference draw
  4. the sector-group shares (A / B-E / F / G-T) of the coping-duration and fuel-criticality runs (E3)
  5. the gate ledger by horizon (OR4): the 23 profile weeks of the table, the 37 gated weeks of the season
  6. the forecast of 30 September on the earlier loading table (G1): 2026_s30_base
  7. the re-sent share of the cut tonnage by week (S3 attribution)

Run:  python studies/rhine2026/review_checks_20261008.py  (writes additional_data/review_checks_20261008.txt)
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
AD = HERE / "additional_data"
RUNS = Path("C:/dsc_runs/rhine2026")
INDUSTRY = ("B", "C", "D", "E")
MONTHS18 = ["2018-08", "2018-09", "2018-10", "2018-11", "2018-12"]
MONTHS26 = ["2026-07", "2026-08", "2026-09", "2026-10", "2026-11", "2026-12"]
FIRST = {2018: pd.Timestamp("2018-07-16"), 2026: pd.Timestamp("2026-06-22")}


def group_of(sector: str) -> str:
    s = str(sector)[:1]
    return {"A": "A", "B": "B-E", "C": "B-E", "D": "B-E", "E": "B-E", "F": "F"}.get(s, "G-T")


def levers(L: list[str]) -> None:
    p = pd.read_csv(AD / "compare_runs_batch_jobs_20261007_paired.csv", index_col=0)
    m = pd.read_csv(AD / "compare_runs_batch_jobs_20261007_main.csv", index_col=0)
    names = {"stock7": "stocks +1 week", "deep20": "fairway +20 cm", "fleet": "low-water fleet", "stock7t": "targeted stocks", "package": "the three together"}
    rows = []
    for seed in range(1, 11):
        b = p.loc[f"2026_s07_seed{seed}_base"]
        r = {"seed": seed}
        for k in names:
            x = p.loc[f"2026_s07_seed{seed}_{k}"]
            r[k] = 100 * (1 - x.DEU_cum_mUSD / b.DEU_cum_mUSD)
            r[k + "_peak"] = x["DEU_peak_%week"]
        r["base_peak"] = b["DEU_peak_%week"]
        rows.append(r)
    d = pd.DataFrame(rows).set_index("seed")
    ref = {k: 100 * (1 - m.loc[f"2026_s07_{k}", "DEU_cum_mUSD"] / m.loc["2026_s07_base", "DEU_cum_mUSD"]) for k in names}
    L.append("== 1. Levers on the ten further draws: loss avoided (% of the draw's base) ==")
    L.append(d[list(names)].round(1).to_string())
    L.append("reference draw: " + ", ".join(f"{names[k]} {v:.1f}" for k, v in ref.items()))
    ind = ["stock7", "deep20", "fleet", "stock7t"]
    L.append(f"stocks > fairway in {(d.stock7 > d.deep20).sum()} of 10 draws (reference: {ref['stock7']:.1f} vs {ref['deep20']:.1f})")
    L.append(f"fleet last of the four single levers in {(d[ind].idxmin(axis=1) == 'fleet').sum()} of 10 draws; "
             f"fleet < targeted stocks in {(d.fleet < d.stock7t).sum()} of 10")
    L.append(f"targeted stocks < general stocks in {(d.stock7t < d.stock7).sum()} of 10; targeted < fairway in {(d.stock7t < d.deep20).sum()} of 10")
    L.append(f"package > every single lever in {((d.package > d[ind].max(axis=1))).sum()} of 10")
    L.append(f"stocks or fairway first in {(d[ind].idxmax(axis=1).isin(['stock7', 'deep20'])).sum()} of 10 "
             f"(first lever by draw: {d[ind].idxmax(axis=1).tolist()})")
    L.append("== 2. Peak week: fleet against the base ==")
    L.append(f"reference draw: base {m.loc['2026_s07_base', 'DEU_peak_%week']:.2f}, fleet {m.loc['2026_s07_fleet', 'DEU_peak_%week']:.2f}")
    up = (d.fleet_peak > d.base_peak).sum()
    L.append(f"fleet peak above the base's in {up} of 10 draws; by draw: " + ", ".join(f"{s}: {r.base_peak:.2f}->{r.fleet_peak:.2f}" for s, r in d.iterrows()))
    L.append("")


def monthly(s: pd.Series, first: pd.Timestamp, months: list[str]) -> dict:
    days = {}
    for t, v in s.items():
        w0 = first + pd.Timedelta(days=7 * (int(t) - 1))
        for k in range(7):
            days[w0 + pd.Timedelta(days=k)] = float(v)
    d = pd.Series(days)
    per = d.index.to_period("M").astype(str)
    return {mo: float(d[per == mo].mean()) if (per == mo).any() else float("nan") for mo in months}


def industrial_series(run: Path) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Industrial shortfall by week: production-weighted (the paper), value-added-weighted, and the industrial
    part of total value added (the va series restricted to B-E)."""
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm")["production"]
    fd = fd[(fd.region == "DEU") & (fd.time_step >= 1)].copy()
    fd["base"] = fd.firm.map(b0)
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    fd["va_share"] = fd.sector.map((va.mrio_va / va.mrio_output).to_dict()).fillna(0.3)
    ind = fd[fd.sector.astype(str).str[:1].isin(INDUSTRY)].copy()
    ind["short"] = ind.base - ind.production
    prod_w = 100 * ind.short.groupby(ind.time_step).sum() / ind.base.groupby(ind.time_step).sum()
    va_w = 100 * (ind.short * ind.va_share).groupby(ind.time_step).sum() / (ind.base * ind.va_share).groupby(ind.time_step).sum()
    # sector-level: the shortfall rate of each sector weighted by its value added (the index convention)
    sec = ind.groupby(["time_step", "sector"]).agg(short=("short", "sum"), base=("base", "sum")).reset_index()
    sec["rate"] = sec.short / sec.base
    sec["w"] = sec.sector.map(va.mrio_va.to_dict())
    sec_w = 100 * (sec.rate * sec.w).groupby(sec.time_step).sum() / sec.w.groupby(sec.time_step).sum()
    return prod_w, va_w, sec_w


def weights_table(run: Path, L: list[str]) -> None:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    fd = fd[(fd.region == "DEU") & (fd.time_step == 0)]
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    ind = fd[fd.sector.astype(str).str[:1].isin(INDUSTRY)]
    g = ind.groupby("sector").production.sum()
    w = pd.DataFrame({"production_share_%": 100 * g / g.sum(), "va_share_%": 100 * va.mrio_va.reindex(g.index) / va.mrio_va.reindex(g.index).sum()})
    w["ratio"] = w["va_share_%"] / w["production_share_%"]
    L.append("German industrial sectors: weight in the production-weighted and in the value-added-weighted series (%)")
    L.append(w.round(2).sort_values("production_share_%", ascending=False).to_string())


def index_bridge(L: list[str]) -> None:
    L.append("== 3. The industrial series under three aggregations (E1): production-weighted (the paper), firm shortfall weighted by "
             "the sector's value-added ratio, and sector shortfall rates weighted by sector value added (the production-index convention) ==")
    for run, year, months in (("2018_s07_base", 2018, MONTHS18), ("2026_s07_base", 2026, MONTHS26)):
        p, v, s = industrial_series(RUNS / run)
        for lab, ser in (("production-weighted", p), ("firm x va ratio", v), ("sector rate x sector va", s)):
            mo = monthly(ser, FIRST[year], months)
            L.append(f"  {run} {lab:24s} " + "  ".join(f"{m[-2:]}: {mo[m]:5.2f}" for m in months) + f"   integral {sum(mo.values()):.2f}  peak week {ser.idxmax()} ({ser.max():.2f} %)")
    weights_table(RUNS / "2026_s07_base", L)
    L.append("")


def sector_groups(L: list[str]) -> None:
    L.append("== 4. Sector groups of the coping-duration and fuel-criticality runs (E3): German gross loss by group, % of the run's loss ==")
    q = None
    for run in ("2026_s07_base", "2026_rev_serv45", "2026_rev_dfuel0", "2026_rev_rail50", "2026_rev_rail140"):
        path = RUNS / run / "firm_data.csv"
        if not path.exists():
            L.append(f"  {run}: no firm_data.csv")
            continue
        fd = pd.read_csv(path, usecols=["time_step", "firm", "region", "sector", "production"])
        b0 = fd[fd.time_step == 0].set_index("firm")["production"]
        de = fd[(fd.region == "DEU") & (fd.time_step >= 1)].copy()
        de["loss"] = (de.firm.map(b0) - de.production).clip(lower=0)
        va = pd.read_csv(RUNS / run / "mrio_by_sector.csv").set_index("sector")
        de["va"] = de.loss * de.sector.map((va.mrio_va / va.mrio_output).to_dict()).fillna(0.3)
        g = de.groupby(de.sector.map(group_of)).va.sum()
        de_sub = de[de.sector.astype(str).str[:1].isin(("D", "E"))].va.sum()
        tot = g.sum()
        L.append(f"  {run:18s} total {tot:8.0f} mUSD: A {100 * g.get('A', 0) / tot:4.1f}  B-E {100 * g.get('B-E', 0) / tot:4.1f} (D+E {100 * de_sub / tot:4.1f})  "
                 f"F {100 * g.get('F', 0) / tot:4.1f}  G-T {100 * g.get('G-T', 0) / tot:4.1f}   total/industry {tot / g.get('B-E', 1):.2f}")
        top = de.groupby("sector").va.sum().sort_values(ascending=False).head(6)
        L.append("      largest sectors: " + ", ".join(f"{k} {100 * v / tot:.1f}" for k, v in top.items()))
    L.append("")


def gate_ledger(L: list[str]) -> None:
    L.append("== 5. The gate ledger by horizon (OR4): cut / re-sent / withheld (kt) ==")
    log = RUNS / "2026_s07_base.log"
    if not log.exists():
        L.append("  no log"); return
    pat = re.compile(r"t=(\d+).*?cut ([\d,\.]+) t.*?re-?sent ([\d,\.]+) t.*?(?:withheld|blocked) ([\d,\.]+) t")
    rows = {}
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = pat.search(line)
        if m:
            rows[int(m.group(1))] = tuple(float(m.group(i).replace(",", "")) / 1000 for i in (2, 3, 4))
    if not rows:
        L.append("  no gate lines matched; sample lines:")
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if "cut" in line and "re-sent" in line:
                L.append("  " + line.strip()[:200]); break
        return
    d = pd.DataFrame(rows, index=["cut", "resent", "withheld"]).T.sort_index()
    for lab, sel in (("profile weeks 1-23", d.loc[1:23]), ("recovery weeks 24+", d.loc[24:]), ("all gated weeks", d)):
        L.append(f"  {lab:22s} weeks {len(sel):2d}: cut {sel.cut.sum():8.0f}  re-sent {sel.resent.sum():7.0f}  withheld {sel.withheld.sum():8.0f}  "
                 f"re-sent share {100 * sel.resent.sum() / sel.cut.sum():.1f} %")
    share = (100 * d.resent / d.cut).loc[1:23]
    L.append("  re-sent share of the cut by profile week: " + ", ".join(f"{t}: {v:.0f}" for t, v in share.items()))
    L.append(f"  profile weeks: min {share.min():.0f} %, max {share.max():.0f} %; trough weeks (LF < 0.3): " +
             ", ".join(f"{t}: {v:.0f}" for t, v in share.items() if t in (7, 8, 9, 14, 15, 16)))
    L.append("")


def forecast_vintages(L: list[str]) -> None:
    L.append("== 6. The forecast by vintage (G1) ==")
    for f, run, lab in (("compare_runs_batch_jobs_20260930_main.csv", "2026_s30_base", "30 Sep profile, loading table v1, batch of 30 Sep"),
                        ("compare_runs_batch_jobs_20261007_main.csv", "2026_s07_base", "30 Sep profile, rebuilt loading table, batch of 7 Oct")):
        t = pd.read_csv(AD / f, index_col=0)
        if "DEU_%quarter" not in t.columns:
            t = t.T.apply(pd.to_numeric, errors="coerce")
        if run in t.index:
            L.append(f"  {run:16s} {lab}: DEU {t.loc[run, 'DEU_%quarter']:.2f} % of a quarter, peak {t.loc[run, 'DEU_peak_%week']:.2f} % in week {int(t.loc[run, 'DEU_peak_week'])}, EU {t.loc[run, 'EU_cum_mUSD'] / 1000:.1f} bn")
        else:
            L.append(f"  {run}: not in {f}; rows: {list(t.index)[:6]}")
    for f in ("compare_runs_batch_20260929_gs1paper.csv",):
        if (AD / f).exists():
            t = pd.read_csv(AD / f, index_col=0)
            if "DEU_%quarter" not in t.columns:
                t = t.T.apply(pd.to_numeric, errors="coerce")
            L.append(f"  {f}: rows {list(t.index)[:12]}")
    L.append("")


def main() -> None:
    L: list[str] = ["Checks for the review of 8 October 2026 (review_checks_20261008.py)", ""]
    levers(L)
    index_bridge(L)
    sector_groups(L)
    gate_ledger(L)
    forecast_vintages(L)
    out = AD / "review_checks_20261008.txt"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print("written", out)


if __name__ == "__main__":
    main()
