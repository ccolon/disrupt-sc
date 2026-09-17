"""F9: the validation figure of the paper (Fig. 4 of plan.md), 17 Sep 2026.

(a) 2018: weekly German value-added loss on the calibrated buffer, reference draw and the band of ten further
    draws, against the observed timing (thyssenkrupp force majeure 22 Oct, strategic fuel-reserve release
    24-26 Oct, industrial-production trough in November).
(b) The stock ladder: cumulated 2018 loss against the multiplier on the raw-material stock days, with the
    ex-post range shaded and the ensemble at the calibrated value.
(c) The August 2026 wave (weeks 7-11) at multipliers 1, 1.5 and 2 against the ex-ante estimates issued in
    August 2026 (Kiel 0.1-0.2 points of quarterly GDP; Commerzbank 0.35).
(d) The two ensembles, 2026 and 2018, as strips.

Usage:
    python studies/rhine2026/plots/validation_figure.py [--out studies/rhine2026/figures]
Inputs: additional_data/compare_runs_batch_20260917_ens2018.{csv,txt}, compare_runs_batch_20260916_cal2018.txt,
compare_runs_batch_20260916_paper.csv, compare_runs_batch_20260915.csv (the x1 point), scenarios/2018.csv.
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
Q_DEU = 20659.0 / 2.163          # mUSD per 1 % of a quarter of German value added (15 Sep base)


def weekly_block(txt_path: Path) -> pd.DataFrame:
    txt = txt_path.read_text(encoding="utf-8", errors="replace")
    block = txt.split("== weekly value-added loss of DEU (mUSD/week) ==")[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#")]
    w = pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")
    return w


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main(out: Path):
    ens = weekly_block(AD / "compare_runs_batch_20260917_ens2018.txt")
    seeds = [c for c in ens.columns if c.startswith("2018_cal_seed")]
    ref = weekly_block(AD / "compare_runs_batch_20260916_cal2018.txt")["2018_inv200"]
    first = pd.Timestamp(pd.read_csv(HERE / "scenarios" / "2018.csv")["week_start"].iloc[0])
    dates = [first + pd.Timedelta(weeks=int(t) - 1) for t in ens.index]     # t = profile row + 1
    band = ens[seeds]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.6), gridspec_kw={"height_ratios": [1.1, 1]})
    fig.patch.set_facecolor("white")

    # (a) 2018 weekly loss, band and observed timing
    ax = axes[0, 0]; style(ax)
    ax.fill_between(dates, band.min(axis=1) * 13 / Q_DEU, band.max(axis=1) * 13 / Q_DEU, color=BLUE, alpha=0.15, linewidth=0, label="ten further draws (range)")
    ax.fill_between(dates, band.quantile(0.25, axis=1) * 13 / Q_DEU, band.quantile(0.75, axis=1) * 13 / Q_DEU, color=BLUE, alpha=0.3, linewidth=0, label="interquartile range")
    ax.plot(dates[:len(ref)], ref.values * 13 / Q_DEU, color=INK, linewidth=2, label="reference draw")
    ax.set_ylim(0, 1.7)
    for d, txt in [("2018-10-22", "force majeure thyssenkrupp, 22 Oct"), ("2018-10-25", "strategic fuel-reserve release, 24–26 Oct")]:
        x = pd.Timestamp(d); ax.axvline(x, color=ORANGE, linewidth=1, linestyle="--")
    ax.text(pd.Timestamp("2018-10-21"), 1.05, "force majeure thyssenkrupp, 22 Oct", color=ORANGE, fontsize=7.5, ha="right", va="bottom", rotation=90)
    ax.text(pd.Timestamp("2018-10-27"), 1.05, "fuel-reserve release, 24–26 Oct", color=ORANGE, fontsize=7.5, ha="left", va="bottom", rotation=90)
    ax.axvspan(pd.Timestamp("2018-11-01"), pd.Timestamp("2018-11-30"), color=ORANGE, alpha=0.08, linewidth=0)
    ax.text(pd.Timestamp("2018-11-15"), 1.66, "industrial-production trough: November", color=ORANGE, fontsize=7.5, ha="center", va="top")
    ax.set_ylabel("German value-added loss, % of a week", color=MUTED, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(pd.Timestamp("2018-09-24"), pd.Timestamp("2018-12-31"))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    ax.set_title("a  2018 on the calibrated buffer: timing against the record", loc="left", fontsize=9.5, color=INK)

    # (b) the stock ladder
    ax = axes[0, 1]; style(ax)
    mult = [1.0, 1.25, 1.5, 1.75, 2.0]
    loss = [1.339, 0.668, 0.510, 0.410, 0.323]
    ax.axhspan(0.3, 0.4, color=GREEN, alpha=0.15, linewidth=0)
    ax.text(1.02, 0.405, "ex-post estimates of 2018: 0.3–0.4 % of a quarter", color=GREEN, fontsize=7.5, va="bottom")
    ax.plot(mult, loss, color=INK, linewidth=1.5, marker="o", markersize=5, label="reference draw")
    e = pd.read_csv(AD / "compare_runs_batch_20260917_ens2018.csv").set_index("run")["DEU_%quarter"]
    e = e[[i for i in e.index if i.startswith("2018_cal_seed")]]
    ax.scatter([2.0] * len(e), e.values, color=BLUE, s=14, alpha=0.7, zorder=3, label="ten further draws at ×2")
    for m, v in zip(mult, loss):
        ax.annotate(f"{v:.2f}", (m, v), textcoords="offset points", xytext=(6, 4) if m < 2 else (-26, 6), fontsize=7.5, color=INK)
    ax.set_xticks(mult); ax.set_xticklabels(["×1\n(raw materials only)", "×1.25", "×1.5", "×1.75", "×2\n(calibrated)"], fontsize=8)
    ax.set_ylabel("2018 loss, % of a quarter of German value added", color=MUTED, fontsize=8)
    ax.set_ylim(0, 1.5)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("b  The single calibrated parameter: the stock buffer", loc="left", fontsize=9.5, color=INK)

    # (c) August 2026 wave vs the ex ante
    ax = axes[1, 0]; style(ax)
    labels = ["×1", "×1.5", "×2 (calibrated)"]
    aug = [0.512, 0.276, 0.134]
    ax.axhspan(0.1, 0.2, color=GREEN, alpha=0.15, linewidth=0)
    ax.text(2.45, 0.205, "ex ante, August 2026:\nKiel Institute 0.1–0.2 points of quarterly GDP", color=GREEN, fontsize=7.5, ha="right", va="bottom")
    ax.axhline(0.35, color=GREEN, linewidth=1, linestyle=":")
    ax.text(2.45, 0.355, "Commerzbank 0.35", color=GREEN, fontsize=7.5, ha="right", va="bottom")
    bars = ax.bar(range(3), aug, color=[MUTED, MUTED, INK], width=0.55)
    for i, v in enumerate(aug):
        ax.text(i, v + 0.012, f"{v:.2f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(3)); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("August wave (weeks 7–11), % of a quarter", color=MUTED, fontsize=8)
    ax.set_ylim(0, 0.6)
    ax.set_title("c  The August 2026 closure against the estimates made at the time", loc="left", fontsize=9.5, color=INK)

    # (d) the two ensembles
    ax = axes[1, 1]; style(ax)
    p = pd.read_csv(AD / "compare_runs_batch_20260916_paper.csv").set_index("run")["DEU_%quarter"]
    e26 = list(p[[i for i in p.index if i.startswith("2026_cal_seed")]].values) + [p["2026_cal_base"]]
    e18 = list(e.values) + [0.323]
    rng = np.random.default_rng(3)
    for x, vals, col, lab in [(0, e18, BLUE, "2018 (calibration case)"), (1, e26, ORANGE, "2026 (this event)")]:
        jitter = rng.uniform(-0.12, 0.12, len(vals))
        ax.scatter(x + jitter, vals, color=col, s=22, alpha=0.75, zorder=3)
        m, s = float(np.mean(vals)), float(np.std(vals, ddof=1))
        ax.plot([x - 0.22, x + 0.22], [m, m], color=INK, linewidth=1.5)
        ax.text(x + 0.26, m, f"{m:.2f} ± {s:.2f}", fontsize=8, color=INK, va="center")
    ax.axhspan(0.3, 0.4, xmin=0.05, xmax=0.45, color=GREEN, alpha=0.15, linewidth=0)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["2018\n(eleven draws)", "2026\n(eleven draws)"], fontsize=8)
    ax.set_xlim(-0.5, 1.7)
    ax.set_ylabel("German loss, % of a quarter", color=MUTED, fontsize=8)
    ax.set_ylim(0, 0.9)
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
