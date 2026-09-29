"""F9: the 2018 record (Fig. 4 of the paper), rebuilt 29 Sep 2026 for the quantity-constraint representation.

(a) Monthly shortfall of German industrial production in 2018: the path implied by the published coefficients
    (Ademmer et al., with and without the lagged term), the model (quantity constraint with the surcharge, stocks
    at their evidence value) and the priced river with closures (stocks x1 and x2).
(b) The shortfall cumulated from August to December (percent-months) against the stock multiplier, under the two
    representations, with the range of the record shaded.
(c) Weekly German value-added loss in 2018: reference draw and the band of ten further draws, against the
    observed events.
(d) The two ensembles, 2018 and 2026, as strips.

Usage:
    python studies/rhine2026/plots/validation_figure.py [--out studies/rhine2026/figures]
Inputs: additional_data/matched_estimand_2018_gsladder.txt and matched_estimand_2018_pipe.txt (the monthly values
below are copied from them), compare_runs_batch_20260929_gs1paper.{csv,txt}, compare_runs_gsladder_20260928.txt,
scenarios/2018.csv.
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
Q_DEU = 15056.0 / 1.576          # mUSD per 1 % of a quarter of German value added
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec"]
RECORD_LAG = [1.02, 1.23, 1.38, 1.74, 0.82]        # matched_estimand_2018.py: with the lagged term, 6.19 %-months
RECORD_NOLAG = [1.02, 0.51, 1.02, 1.02, 0.10]      # contemporaneous term only, 3.67
MODEL = [0.76, 0.70, 1.63, 1.91, 1.28]             # 2018_gs_inv100 (quantity constraint + surcharge, stocks x1), 5.57
PRICED_X1 = [0.00, 0.00, 0.71, 2.95, 3.08]         # 2018_baseline (priced river with closures, stocks x1), 4.95
PRICED_X2 = [0.00, 0.00, 0.17, 1.23, 1.37]         # 2018_pipe (priced river, stocks x2), 1.96
INT_GATE = {1.0: 5.57, 1.25: 4.29, 1.5: 3.36, 2.0: 2.11}
INT_PRICED = {1.0: 4.95, 1.5: 3.19, 2.0: 1.96}


def weekly_block(txt_path: Path) -> pd.DataFrame:
    txt = txt_path.read_text(encoding="utf-8", errors="replace")
    block = txt.split("== weekly value-added loss of DEU (mUSD/week) ==")[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#")
             and not l.startswith("==")]
    return pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main(out: Path):
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.6), gridspec_kw={"height_ratios": [1.1, 1]})
    fig.patch.set_facecolor("white")

    # (a) monthly industrial shortfall
    ax = axes[0, 0]; style(ax)
    x = np.arange(len(MONTHS))
    ax.fill_between(x, RECORD_NOLAG, RECORD_LAG, color=GREEN, alpha=0.18, linewidth=0, label="record: with and without the lagged term")
    ax.plot(x, RECORD_LAG, color=GREEN, linewidth=1.5, marker="s", markersize=4)
    ax.plot(x, MODEL, color=INK, linewidth=2, marker="o", markersize=5, label="model: quantity constraint, stocks ×1")
    ax.plot(x, PRICED_X2, color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=3.5, label="priced river with closures, stocks ×2")
    ax.plot(x, PRICED_X1, color=ORANGE, linewidth=1.0, linestyle=":", marker="o", markersize=3, label="priced river with closures, stocks ×1")
    ax.set_xticks(x); ax.set_xticklabels([f"{m} 2018" for m in MONTHS], fontsize=8)
    ax.set_ylabel("shortfall of German industrial production, %", color=MUTED, fontsize=8)
    ax.set_ylim(0, 3.4)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_title("a  Monthly industrial production through the 2018 low water", loc="left", fontsize=9.5, color=INK)

    # (b) cumulated shortfall against the stock multiplier
    ax = axes[0, 1]; style(ax)
    ax.axhspan(sum(RECORD_NOLAG), sum(RECORD_LAG), color=GREEN, alpha=0.18, linewidth=0)
    ax.text(2.0, sum(RECORD_LAG) + 0.08, "record: 3.7–6.2 percent-months", color=GREEN, fontsize=7.5, ha="right", va="bottom")
    ax.plot(list(INT_GATE), list(INT_GATE.values()), color=INK, linewidth=1.8, marker="o", markersize=5, label="quantity constraint (trough in November)")
    ax.plot(list(INT_PRICED), list(INT_PRICED.values()), color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=4, label="priced river with closures (trough in December)")
    for m, v in INT_GATE.items():
        ax.annotate(f"{v:.1f}", (m, v), textcoords="offset points", xytext=(5, 5), fontsize=7.5, color=INK)
    ax.set_xticks([1.0, 1.25, 1.5, 2.0]); ax.set_xticklabels(["×1\n(evidence value)", "×1.25", "×1.5", "×2"], fontsize=8)
    ax.set_xlabel("multiplier on the stock days of the balance-sheet statistics", color=MUTED, fontsize=8)
    ax.set_ylabel("industrial shortfall, Aug–Dec 2018, percent-months", color=MUTED, fontsize=8)
    ax.set_ylim(0, 7.2)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    ax.set_title("b  The size of the loss follows the stocks", loc="left", fontsize=9.5, color=INK)

    # (c) 2018 weekly loss, band and observed events
    ax = axes[1, 0]; style(ax)
    ens = weekly_block(AD / "compare_runs_batch_20260929_gs1paper.txt")
    seeds = [c for c in ens.columns if c.startswith("2018_gs1_seed")]
    ref = weekly_block(AD / "compare_runs_gsladder_20260928.txt")["2018_gs_inv100"]
    first = pd.Timestamp(pd.read_csv(HERE / "scenarios" / "2018.csv")["week_start"].iloc[0])
    dates = [first + pd.Timedelta(weeks=int(t) - 1) for t in ens.index]
    band = ens[seeds] * 13 / Q_DEU
    ax.fill_between(dates, band.min(axis=1), band.max(axis=1), color=BLUE, alpha=0.15, linewidth=0, label="ten further draws (range)")
    ax.fill_between(dates, band.quantile(0.25, axis=1), band.quantile(0.75, axis=1), color=BLUE, alpha=0.3, linewidth=0, label="interquartile range")
    ax.plot([first + pd.Timedelta(weeks=int(t) - 1) for t in ref.index], ref.values * 13 / Q_DEU, color=INK, linewidth=2, label="reference draw")
    top = float(max(band.max().max(), (ref * 13 / Q_DEU).max())) * 1.12
    ax.set_ylim(0, top)
    for d in ("2018-10-22", "2018-10-25"):
        ax.axvline(pd.Timestamp(d), color=ORANGE, linewidth=1, linestyle="--")
    ax.text(pd.Timestamp("2018-10-20"), top * 0.97, "force majeure thyssenkrupp, 22 Oct", color=ORANGE, fontsize=7, ha="right", va="top", rotation=90)
    ax.text(pd.Timestamp("2018-10-13"), top * 0.97, "fuel-reserve release, 24–26 Oct", color=ORANGE, fontsize=7, ha="right", va="top", rotation=90)
    ax.axvspan(pd.Timestamp("2018-11-01"), pd.Timestamp("2018-11-30"), color=ORANGE, alpha=0.08, linewidth=0)
    ax.text(pd.Timestamp("2018-12-02"), top * 0.97, "industrial-production\ntrough: November", color=ORANGE, fontsize=7.5, ha="left", va="top")
    ax.set_ylabel("German value-added loss, % of a week", color=MUTED, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(pd.Timestamp("2018-07-16"), pd.Timestamp("2019-01-07"))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", bbox_to_anchor=(0.0, 1.0))
    ax.set_title("c  2018, all sectors: weekly loss against the observed events", loc="left", fontsize=9.5, color=INK)

    # (d) the two ensembles
    ax = axes[1, 1]; style(ax)
    p = pd.read_csv(AD / "compare_runs_batch_20260929_gs1paper.csv")
    p = p.set_index(p.columns[0])
    if "DEU_%quarter" not in p.columns:
        p = p.T
    q = pd.to_numeric(p["DEU_%quarter"], errors="coerce")
    e26 = list(q[[i for i in q.index if i.startswith("2026_gs1_seed")]].values) + [float(q["2026_gs1_base"])]
    e18 = list(q[[i for i in q.index if i.startswith("2018_gs1_seed")]].values) + [1.159]
    rng = np.random.default_rng(3)
    for xx, vals, col in [(0, e18, BLUE), (1, e26, ORANGE)]:
        jitter = rng.uniform(-0.12, 0.12, len(vals))
        ax.scatter(xx + jitter, vals, color=col, s=22, alpha=0.75, zorder=3)
        m, s = float(np.mean(vals)), float(np.std(vals, ddof=1))
        ax.plot([xx - 0.22, xx + 0.22], [m, m], color=INK, linewidth=1.5)
        ax.text(xx + 0.26, m, f"{m:.2f} ± {s:.2f}", fontsize=8, color=INK, va="center")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["2018\n(eleven draws)", "2026\n(eleven draws)"], fontsize=8)
    ax.set_xlim(-0.5, 1.7)
    ax.set_ylabel("German loss, all sectors, % of a quarter", color=MUTED, fontsize=8)
    ax.set_ylim(0, 2.2)
    ax.set_title("d  Draw-to-draw uncertainty of the two events", loc="left", fontsize=9.5, color=INK)

    fig.tight_layout(h_pad=2.0, w_pad=2.0)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F9_validation.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F9 written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
