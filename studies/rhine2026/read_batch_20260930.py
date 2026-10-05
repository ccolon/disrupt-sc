"""Reading of the batch of 30 Sep 2026 (jobs_20260930_main.txt + jobs_20260930_paired.txt): the paper set on the
adopted rules and the rebuilt 2026 season, the review's open points. One compact summary, written to
additional_data/batch_20260930_summary.txt.

Usage:
    python studies/rhine2026/read_batch_20260930.py [--runs C:/dsc_runs/rhine2026]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "studies/rhine2026/additional_data"
LEVERS = ["stock7", "deep20", "fleet", "stock7t", "package"]
INDUSTRY = ("B", "C", "D", "E")
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec"]
import sys
sys.path.insert(0, str(ROOT / "studies/rhine2026"))
from matched_estimand_2018 import model_path      # noqa: E402  one integration rule for every industrial path (6 Oct 2026)
from benchmark_ademmer import record, EVENT_MONTHS  # noqa: E402  the published dynamic specification with its band
_rec_t, REC_S = record(2018, 1)
RECORD = {pd.Timestamp(m + "-01").strftime("%b"): float(v) for m, v in
          zip(_rec_t.month, _rec_t.central) if m in EVENT_MONTHS[2018]}


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def firm_losses(run: Path):
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm").production
    fd["base"] = fd.firm.map(b0)
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    fd["vs"] = fd.sector.map((va.mrio_va / va.mrio_output).to_dict()).fillna(0.3)
    fd["loss"] = (fd.base - fd.production).clip(lower=0) * fd.vs
    return fd


def matched(run: Path) -> dict:
    """Monthly industrial shortfall (%), plain-sum integral (percent-months) and peak month, from the shared rule."""
    d = model_path(run, 2018)
    return {**{m: d[f"ind_{m}"] for m in MONTHS}, "integral": d["ind_integrated_pct_months"], "peak": d["peak_month_ind"]}


def main(runs: Path):
    L = []
    main_t = table(runs / "compare_runs_batch_jobs_20260930_main.csv")
    pair_t = table(runs / "compare_runs_batch_jobs_20260930_paired.csv")
    allruns = list(main_t.index) + list(pair_t.index)
    done = [r for r in allruns if (runs / f"{r}.log").exists() and "Done." in (runs / f"{r}.log").read_text(encoding="utf-8", errors="replace")]
    L.append(f"runs in the two tables: {len(allruns)}; completed (Done.): {len(done)}; missing: {sorted(set(allruns) - set(done))}")
    q = main_t.loc["2026_s30_base", "DEU_cum_mUSD"] / main_t.loc["2026_s30_base", "DEU_%quarter"]

    cols = ["DEU_cum_mUSD", "DEU_%quarter", "DEU_peak_%week", "DEU_peak_week", "DEU_loss_weeks", "EU_cum_mUSD", "cons_loss_cum_mUSD", "DEU_net_mUSD", "DEU_gross_perishable_mUSD", "firms<99%_peak_%"]
    core = [r for r in main_t.index if not r.startswith("wave") and "seed" not in r]
    L.append("\n== headline (main list, all but seeds and waves) ==")
    L.append(main_t.loc[core, cols].round(3).to_string())

    for label, base, seeds in (("2026", "2026_s30_base", [f"2026_s30_seed{s}_base" for s in range(1, 11)]),
                               ("2018", "2018_s30_base", [f"2018_s30_seed{s}" for s in range(1, 11)])):
        t = pair_t if label == "2026" else main_t
        v = list(t.loc[seeds, "DEU_%quarter"]) + [main_t.loc[base, "DEU_%quarter"]]
        pk = list(t.loc[seeds, "DEU_peak_week"].astype(int))
        L.append(f"\n{label} ensemble (11 draws): DEU {np.mean(v):.2f} +/- {np.std(v, ddof=1):.2f} % of a quarter, range {min(v):.2f}-{max(v):.2f}; "
                 f"peak weeks {sorted(set(pk))}; EU {t.loc[seeds, 'EU_cum_mUSD'].min():,.0f}-{t.loc[seeds, 'EU_cum_mUSD'].max():,.0f} mUSD")

    L.append("\n== levers: German gross loss avoided, % of the base ==")
    b42 = main_t.loc["2026_s30_base", "DEU_cum_mUSD"]; e42 = main_t.loc["2026_s30_base", "EU_cum_mUSD"]
    rows = []
    for lv in LEVERS:
        r42 = 100 * (1 - main_t.loc[f"2026_s30_{lv}", "DEU_cum_mUSD"] / b42)
        eu42 = 100 * (1 - main_t.loc[f"2026_s30_{lv}", "EU_cum_mUSD"] / e42)
        per_seed = [100 * (1 - pair_t.loc[f"2026_s30_seed{s}_{lv}", "DEU_cum_mUSD"] / pair_t.loc[f"2026_s30_seed{s}_base", "DEU_cum_mUSD"]) for s in range(1, 11)]
        rows.append({"lever": lv, "seed42_%": round(r42, 0), "EU_seed42_%": round(eu42, 0), "paired_mean_%": round(np.mean(per_seed), 0),
                     "paired_sd": round(np.std(per_seed, ddof=1), 0), "paired_min": round(min(per_seed), 0), "paired_max": round(max(per_seed), 0)})
    L.append(pd.DataFrame(rows).to_string(index=False))
    ranks = []
    for s in range(1, 11):
        ben = {lv: pair_t.loc[f"2026_s30_seed{s}_base", "DEU_cum_mUSD"] - pair_t.loc[f"2026_s30_seed{s}_{lv}", "DEU_cum_mUSD"] for lv in LEVERS if lv != "package"}
        ranks.append(" > ".join(sorted(ben, key=ben.get, reverse=True)))
    L.append("ranking of the four single levers by seed: " + "; ".join(f"{k} x{v}" for k, v in pd.Series(ranks).value_counts().items()))

    L.append("\n== wave isolation (gap 0 = 2026_s30_base) ==")
    A, B = main_t.loc["wave30_A", "DEU_cum_mUSD"], main_t.loc["wave30_B", "DEU_cum_mUSD"]
    L.append(f"A alone {A / q:.3f}, B alone {B / q:.3f}, sum {(A + B) / q:.3f} % of a quarter")
    for g, r in ((0, "2026_s30_base"), (1, "wave30_AB_gap1"), (2, "wave30_AB_gap2"), (4, "wave30_AB_gap4"), (8, "wave30_AB_gap8")):
        v = main_t.loc[r, "DEU_cum_mUSD"]
        L.append(f"  gap {g}: {v / q:.3f} %; interaction {100 * (v - A - B) / (A + B):+.0f} % of the sum; B adds {(v - A) / q:.3f} ({(v - A) / B:.2f} x B alone)")
    f = main_t.loc["wave30_flat", "DEU_cum_mUSD"]
    L.append(f"  flat (same tonnage, spread evenly): {f / q:.3f} %; the season is {100 * (b42 / f - 1):+.0f} % against it")

    L.append("\n== channel decomposition ==")
    for r in ("2026_s30_gateonly", "2026_s30_surchargeonly", "2026_s30_base"):
        L.append(f"  {r:24s} DEU {main_t.loc[r, 'DEU_%quarter']:.3f} % of a quarter, peak {main_t.loc[r, 'DEU_peak_%week']:.2f} % wk {int(main_t.loc[r, 'DEU_peak_week'])}, EU {main_t.loc[r, 'EU_cum_mUSD']:,.0f}")

    L.append("\n== structural sensitivities ==")
    for r in ("2026_s30_tablelow", "2026_s30_base", "2026_s30_tablehigh", "2026_s30_sup2", "2026_s30_nopool",
              "2018_s30_tablelow", "2018_s30_base", "2018_s30_tablehigh", "2018_s30_sup2", "2018_s30_nopool"):
        L.append(f"  {r:20s} DEU {main_t.loc[r, 'DEU_%quarter']:.3f} % of a quarter, peak {main_t.loc[r, 'DEU_peak_%week']:.2f} % wk {int(main_t.loc[r, 'DEU_peak_week'])}")

    L.append("\n== 2018 industrial path (matched estimand; record = the published dynamic specification, Aug-Dec " + ", ".join(f"{RECORD[m]:.2f}" for m in MONTHS)
             + f" = {REC_S['integral']:.2f} percent-months, 16-84 % band {REC_S['p16']:.2f}-{REC_S['p84']:.2f}) ==")
    ens = []
    for r in ["2018_s30_base", "2018_s30_tablelow", "2018_s30_tablehigh", "2018_s30_sup2"] + [f"2018_s30_seed{s}" for s in range(1, 11)]:
        if (runs / r / "firm_data.csv").exists():
            m = matched(runs / r)
            L.append(f"  {r:18s} " + " ".join(f"{m[mo]:.2f}" for mo in MONTHS) + f"  integral {m['integral']:.2f}  peak {m['peak']}")
            if "seed" in r or r == "2018_s30_base":
                ens.append(m)
    if ens:
        ints = [m["integral"] for m in ens]
        L.append(f"  11 draws: integral {np.mean(ints):.2f} +/- {np.std(ints, ddof=1):.2f} (range {min(ints):.2f}-{max(ints):.2f}); peak month " +
                 ", ".join(f"{k} x{v}" for k, v in pd.Series([m['peak'] for m in ens]).value_counts().items()) +
                 f"; Aug {np.mean([m['Aug'] for m in ens]):.2f}, Sep {np.mean([m['Sep'] for m in ens]):.2f} (record {RECORD['Aug']:.2f}, {RECORD['Sep']:.2f})")

    L.append("\n== 2026 base: German loss by sector and wave ==")
    fd = firm_losses(runs / "2026_s30_base"); de = fd[fd.region == "DEU"]; tot = de.loss.sum()
    s = de.groupby("sector").loss.sum().sort_values(ascending=False)
    L.append("  shares %: " + ", ".join(f"{k} {100 * v / tot:.1f}" for k, v in s.head(10).items()))
    ind = de[de.sector.str[:1].isin(INDUSTRY)].loss.sum()
    L.append(f"  industry (B-E) {100 * ind / tot:.0f} %; total {tot:,.0f} mUSD = {tot / q:.3f} % of a quarter; industry {ind / q:.3f} %")
    w = de.groupby("time_step").loss.sum()
    for k, (a, b) in {"weeks 1-6": (1, 6), "weeks 7-11 (August trough)": (7, 11), "weeks 12-19 (autumn trough)": (12, 19), "weeks 20-27": (20, 27), "tail 28+": (28, 99)}.items():
        L.append(f"  {k}: {w.loc[a:b].sum() / q:.3f} % of a quarter")
    L.append("  weekly DEU mUSD wk 1-30: " + str([round(x) for x in w.loc[1:30]]))
    cty = fd.groupby("region").loss.sum().sort_values(ascending=False)
    L.append("  countries mUSD: " + ", ".join(f"{k} {v:,.0f}" for k, v in cty.head(7).items()) + f"; non-DE share of EU {100 * (1 - cty['DEU'] / cty.sum()):.0f} %")
    b = main_t.loc["2026_s30_base"]
    L.append(f"  net {b['DEU_net_mUSD']:,.0f} ({100 * b['DEU_net_mUSD'] / b['DEU_cum_mUSD']:.0f} % of gross), perishable {100 * b['DEU_gross_perishable_mUSD'] / b['DEU_cum_mUSD']:.0f} %, delay {b['DEU_delay_mUSD']:.0f} mUSD, consumption loss {b['cons_loss_cum_mUSD']:,.0f}")

    full = runs / "2026_s30_full"
    if (full / "price_by_cargo.csv").exists():
        L.append("\n== link-level run 2026_s30_full: delivered prices of the routed deliveries (value-weighted) ==")
        p = pd.read_csv(full / "price_by_cargo.csv")
        for ct in ("dry_bulk", "liquid_bulk", "container"):
            x = p[p.cargo_type == ct]
            L.append(f"  {ct:12s} median max {x.ratio_median.max():.3f}, p90 max {x.ratio_p90.max():.3f}, max {x.ratio_max.max():.2f}, share of value paying > 1 % more: max {100 * x.share_value_above_1pct.max():.0f} % (week {int(x.loc[x.share_value_above_1pct.idxmax(), 'time_step'])})")
        lf = pd.read_csv(full / "link_flows_disrupted.csv.gz")
        lf["short"] = (lf.base_realized - lf.realized_delivery).clip(lower=0)
        L.append("== disrupted chains, cumulated shortfall of deliveries (mUSD, eq. prices), by buyer country and input ==")
        for c in ("FRA", "DEU", "NLD", "AUT"):
            x = lf[lf.buyer_region == c].groupby(["seller_sector", "buyer_sector"])[["short", "withheld_by_transport", "capacity_blocked"]].sum().sort_values("short", ascending=False).head(6)
            L.append(f"  {c}: " + "; ".join(f"{a}->{bs} {v.short:,.0f} (transport {v.withheld_by_transport:,.0f})" for (a, bs), v in x.iterrows()))
        x = lf[(lf.buyer_region == "FRA")].groupby("seller_region").short.sum().sort_values(ascending=False).head(5)
        L.append("  FRA shortfall by seller region: " + ", ".join(f"{k} {v:,.0f}" for k, v in x.items()))
        inv = pd.read_csv(full / "inventory_trace.csv")
        L.append("== stock trace, German firms, days of cover (need-weighted) at t = 0 / 10 / 11 / 15 / 19 ==")
        for bs, inp in (("H49", "C19"), ("D", "C19"), ("H52", "C19"), ("F", "C23"), ("F", "B08"), ("C20", "C19"), ("C23", "B05")):
            x = inv[(inv.buyer_sector == bs) & (inv.input == inp)].set_index("time_step").days_of_cover
            if len(x):
                L.append(f"  {bs} <- {inp}: " + " / ".join(f"{x.get(t, np.nan):.0f}" for t in (0, 10, 11, 15, 19)))
    text = "\n".join(L)
    print(text)
    (AD / "batch_20260930_summary.txt").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="C:/dsc_runs/rhine2026")
    a = ap.parse_args()
    main(Path(a.runs))
