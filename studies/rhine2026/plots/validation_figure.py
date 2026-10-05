"""F9: the 2018 record (Fig. 4 of the paper), rebuilt 30 Sep 2026 on the batch of that day.

(a) Monthly shortfall of German industrial production in 2018: the path implied by the published coefficients
    (Ademmer et al., with and without the lagged term), the model on the reference draw (quantity constraint with
    the surcharge, stocks at their evidence value), the band of ten further draws, and the priced river with
    closures (stocks x2, the representation of the earlier drafts).
(b) The shortfall cumulated from August to December (percent-months) against the stock multiplier under the two
    representations, with the range of the record shaded, the loading-table band and two suppliers per input at x1.
(c) Weekly German value-added loss in 2018: reference draw and the band of ten further draws, against the events.
(d) The two ensembles, 2018 and 2026, as strips.

Usage:
    python studies/rhine2026/plots/validation_figure.py [--runs C:/dsc_runs/rhine2026] [--out studies/rhine2026/figures]
Inputs: firm_data.csv of 2018_s07_base, 2018_s07_seed1..10, 2018_s07_tablelow/high, 2018_s07_sup2 (matched
estimand computed here); additional_data/compare_runs_batch_jobs_20261007_{main,paired}.{csv,txt}; scenarios/2018.csv.
The stock ladder (x1.25, x1.5, x2) and the priced river come from the runs of 22-28 Sep (before construction was
made non-storable, which leaves the 2018 industrial path unchanged: 5.57 percent-months before and after).
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
AD = HERE / "additional_data"
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, ORANGE, GREEN = "#2f6fdb", "#e0842a", "#3a9a5b"
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec"]
import sys
sys.path.insert(0, str(HERE))
from matched_estimand_2018 import model_path       # noqa: E402  one integration rule for every industrial path (6 Oct 2026)
from benchmark_ademmer import record, EVENT_MONTHS  # noqa: E402  the published dynamic specification with its band


def matched(run: Path) -> dict:
    d = model_path(run, 2018)
    return {**{m: d[f"ind_{m}"] for m in MONTHS}, "integral": d["ind_integrated_pct_months"]}


def weekly_block(txt_path: Path) -> pd.DataFrame:
    txt = txt_path.read_text(encoding="utf-8", errors="replace")
    block = txt.split("== weekly value-added loss of DEU (mUSD/week) ==")[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#") and not l.startswith("==")]
    return pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_%quarter" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main(runs: Path, out: Path):
    ref = matched(runs / "2018_s07_base")
    seeds = [matched(runs / f"2018_s07_seed{s}") for s in range(1, 11)]
    low, high = matched(runs / "2018_s07_tablelow"), matched(runs / "2018_s07_tablehigh")
    sup2 = matched(runs / "2018_s07_sup2")
    # the record: the published dynamic specification (column 1) with its 16-84 % band
    rec_t, rec_s = record(2018, 1)
    ev = rec_t[rec_t.month.isin(EVENT_MONTHS[2018])]
    REC, REC16, REC84 = ev.central.values, ev.p16.values, ev.p84.values
    # the stock ladder of 28 Sep (x1.25, x1.5, x2) and the priced river with closures (x1, x1.5, x2), same rule
    INT_GATE = {1.25: matched(runs / "2018_gs_inv125")["integral"], 1.5: matched(runs / "2018_gs_inv150")["integral"],
                2.0: matched(runs / "2018_gs")["integral"]}
    priced1 = matched(runs / "2018_baseline")
    INT_PRICED = {1.0: priced1["integral"], 1.5: matched(runs / "2018_inv150")["integral"], 2.0: matched(runs / "2018_pipe")["integral"]}
    PRICED_X1 = [priced1[mo] for mo in MONTHS]
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    p = table(AD / "compare_runs_batch_jobs_20261007_paired.csv")
    Q_DEU = m.loc["2026_s07_base", "DEU_cum_mUSD"] / m.loc["2026_s07_base", "DEU_%quarter"]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.8), gridspec_kw={"height_ratios": [1.1, 1]})
    fig.patch.set_facecolor("white")

    # (a) monthly industrial shortfall
    ax = axes[0, 0]; style(ax)
    x = np.arange(len(MONTHS))
    band = np.array([[s[mo] for mo in MONTHS] for s in seeds])
    ax.fill_between(x, band.min(axis=0), band.max(axis=0), color=BLUE, alpha=0.13, linewidth=0, label="ten further draws (range)")
    ax.fill_between(x, REC16, REC84, color=GREEN, alpha=0.2, linewidth=0, label="record: published specification, 16–84 % band")
    ax.plot(x, REC, color=GREEN, linewidth=1.5, marker="s", markersize=4)
    ax.plot(x, [ref[mo] for mo in MONTHS], color=INK, linewidth=2.2, marker="o", markersize=5, label="model, reference draw")
    ax.plot(x, PRICED_X1, color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=3.5, label="priced river with closures, same stocks")
    ax.set_xticks(x); ax.set_xticklabels([f"{mo} 2018" for mo in MONTHS], fontsize=8)
    ax.set_ylabel("shortfall of German industrial production, %", color=MUTED, fontsize=8)
    ax.set_ylim(0, 3.0)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_title("a  Monthly industrial production through the 2018 low water", loc="left", fontsize=9.5, color=INK)

    # (b) cumulated shortfall: stocks, loading table, suppliers
    ax = axes[0, 1]; style(ax)
    ax.axhspan(rec_s["p16"], rec_s["p84"], color=GREEN, alpha=0.2, linewidth=0)
    ax.axhline(rec_s["integral"], color=GREEN, linewidth=1.2)
    ax.text(0.82, rec_s["p84"] + 0.1, f"record: {rec_s['integral']:.1f} percent-months ({rec_s['p16']:.1f}–{rec_s['p84']:.1f}, 16–84 % band)",
            color=GREEN, fontsize=7.5, ha="left", va="bottom")
    gate = {1.0: ref["integral"], **INT_GATE}
    ax.plot(list(gate), list(gate.values()), color=INK, linewidth=1.8, marker="o", markersize=5, label="stock multiplier (reference draw)")
    ax.plot(list(INT_PRICED), list(INT_PRICED.values()), color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=4, label="priced river with closures")
    for mm, v in gate.items():
        ax.annotate(f"{v:.1f}", (mm, v), textcoords="offset points", xytext=(5, 5), fontsize=7.5, color=INK)
    ints = [s["integral"] for s in seeds]
    ax.scatter([0.93] * len(ints), ints, color=BLUE, s=14, alpha=0.7, zorder=3, label="ten further draws at ×1")
    ax.plot([1.0, 1.0], [high["integral"], low["integral"]], color=GREEN, linewidth=2.5, alpha=0.8, solid_capstyle="round", zorder=2)
    ax.text(1.03, low["integral"], f"loading table ×1.15: {low['integral']:.1f}", fontsize=7, color=GREEN, va="center")
    ax.text(1.03, high["integral"] - 0.12, f"loading table ×0.85: {high['integral']:.1f}", fontsize=7, color=GREEN, va="top")
    ax.scatter([1.0], [sup2["integral"]], color=INK, marker="x", s=40, zorder=4)
    ax.text(1.03, sup2["integral"], f"two suppliers per input: {sup2['integral']:.1f}", fontsize=7, color=INK, va="center")
    ax.set_xticks([1.0, 1.25, 1.5, 2.0]); ax.set_xticklabels(["×1\n(evidence value)", "×1.25", "×1.5", "×2"], fontsize=8)
    ax.set_xlim(0.8, 2.1)
    ax.set_xlabel("multiplier on the stock days of the balance-sheet statistics", color=MUTED, fontsize=8)
    ax.set_ylabel("industrial shortfall, Aug–Dec 2018, percent-months", color=MUTED, fontsize=8)
    ax.set_ylim(0, 8.2)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    ax.set_title("b  The size of the loss: stocks, loading table, suppliers", loc="left", fontsize=9.5, color=INK)

    # (c) weekly 2018 loss with the band
    ax = axes[1, 0]; style(ax)
    ens = weekly_block(AD / "compare_runs_batch_jobs_20261007_main.txt")
    cols = [f"2018_s07_seed{s}" for s in range(1, 11)]
    first = pd.Timestamp(pd.read_csv(HERE / "scenarios" / "2018.csv")["week_start"].iloc[0])
    dates = [first + pd.Timedelta(weeks=int(t) - 1) for t in ens.index]
    band = ens[cols] * 13 / Q_DEU
    ax.fill_between(dates, band.min(axis=1), band.max(axis=1), color=BLUE, alpha=0.15, linewidth=0, label="ten further draws (range)")
    ax.fill_between(dates, band.quantile(0.25, axis=1), band.quantile(0.75, axis=1), color=BLUE, alpha=0.3, linewidth=0, label="interquartile range")
    ax.plot(dates, ens["2018_s07_base"] * 13 / Q_DEU, color=INK, linewidth=2, label="reference draw")
    top = float(max(band.max().max(), (ens["2018_s07_base"] * 13 / Q_DEU).max())) * 1.15
    ax.set_ylim(0, top)
    for d in ("2018-10-22", "2018-10-25"):
        ax.axvline(pd.Timestamp(d), color=ORANGE, linewidth=1, linestyle="--")
    ax.text(pd.Timestamp("2018-10-20"), top * 0.97, "force majeure thyssenkrupp, 22 Oct", color=ORANGE, fontsize=7, ha="right", va="top", rotation=90)
    ax.text(pd.Timestamp("2018-10-13"), top * 0.97, "fuel-reserve release, 24–26 Oct", color=ORANGE, fontsize=7, ha="right", va="top", rotation=90)
    ax.axvspan(pd.Timestamp("2018-11-01"), pd.Timestamp("2018-11-30"), color=ORANGE, alpha=0.08, linewidth=0)
    ax.text(pd.Timestamp("2018-12-02"), top * 0.97, "industrial-production\ntrough: November", color=ORANGE, fontsize=7.5, ha="left", va="top")
    ax.set_ylabel("German value-added loss, all sectors, % of a week", color=MUTED, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(pd.Timestamp("2018-07-16"), pd.Timestamp("2019-01-07"))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_title("c  2018, all sectors: weekly loss against the observed events", loc="left", fontsize=9.5, color=INK)

    # (d) the two ensembles
    ax = axes[1, 1]; style(ax)
    e26 = [p.loc[f"2026_s07_seed{s}_base", "DEU_%quarter"] for s in range(1, 11)] + [m.loc["2026_s07_base", "DEU_%quarter"]]
    e18 = [m.loc[f"2018_s07_seed{s}", "DEU_%quarter"] for s in range(1, 11)] + [m.loc["2018_s07_base", "DEU_%quarter"]]
    rng = np.random.default_rng(3)
    for xx, vals, col in [(0, e18, BLUE), (1, e26, ORANGE)]:
        jitter = rng.uniform(-0.12, 0.12, len(vals))
        ax.scatter(xx + jitter, vals, color=col, s=22, alpha=0.75, zorder=3)
        mu, sd = float(np.mean(vals)), float(np.std(vals, ddof=1))
        ax.plot([xx - 0.22, xx + 0.22], [mu, mu], color=INK, linewidth=1.5)
        ax.text(xx + 0.26, mu, f"{mu:.2f} ± {sd:.2f}", fontsize=8, color=INK, va="center")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["2018\n(eleven draws)", "2026\n(eleven draws)"], fontsize=8)
    ax.set_xlim(-0.5, 1.7)
    ax.set_ylabel("German loss, all sectors, % of a quarter", color=MUTED, fontsize=8)
    ax.set_ylim(0, 2.2)
    ax.set_title("d  Draw-to-draw uncertainty of the two events", loc="left", fontsize=9.5, color=INK)

    fig.tight_layout(h_pad=2.0, w_pad=2.0)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F9_validation.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F9 written to {out}; reference integral {ref['integral']:.2f}, draws {min(ints):.2f}-{max(ints):.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="C:/dsc_runs/rhine2026")
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.runs), Path(a.out))
