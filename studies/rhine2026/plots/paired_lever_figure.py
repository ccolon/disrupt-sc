"""F7: adaptation levers paired with their base on eleven supply-chain draws (30 Sep 2026; review A05, OR7, T8).

(a) German value-added loss avoided by each lever, % of the base: the reference draw (bars) and the ten further
    draws, each lever against its own base on the same network (dots); EU in a second column.
(b) Weekly German loss of the base and of each lever on the reference draw.

Usage:
    python studies/rhine2026/plots/paired_lever_figure.py [--out studies/rhine2026/figures]
Inputs: additional_data/compare_runs_batch_jobs_20261007_main.{csv,txt}, compare_runs_batch_jobs_20261007_paired.csv.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
AD = HERE / "additional_data"
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, ORANGE, GREEN, PINK, TEAL = "#2f6fdb", "#e0842a", "#3a9a5b", "#d1519a", "#2aa7a0"
LEVERS = [("package", "Package: fairway + fleet + stocks"), ("stock7", "+7 days of input stocks, all buyers"),
          ("deep20", "Fairway +20 cm (Abladeoptimierung Mittelrhein)"), ("stock7t", "+7 days of stocks, barge-dependent buyers"),
          ("fleet", "Low-water fleet (loading table of low-water vessels)")]
COLORS = {"package": ORANGE, "stock7": TEAL, "deep20": GREEN, "stock7t": PINK, "fleet": BLUE}


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def weekly_block(txt_path: Path) -> pd.DataFrame:
    txt = txt_path.read_text(encoding="utf-8", errors="replace")
    block = txt.split("== weekly value-added loss of DEU (mUSD/week) ==")[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#") and not l.startswith("==")]
    return pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.set_axisbelow(True)


def main(out: Path):
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    p = table(AD / "compare_runs_batch_jobs_20261007_paired.csv")
    w = weekly_block(AD / "compare_runs_batch_jobs_20261007_main.txt")
    fig = plt.figure(figsize=(11, 7.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.95], width_ratios=[1, 1])
    fig.patch.set_facecolor("white")
    rng = np.random.default_rng(1)
    for col, (region, key) in enumerate((("Germany", "DEU_cum_mUSD"), ("European Union", "EU_cum_mUSD"))):
        ax = fig.add_subplot(gs[0, col]); style(ax); ax.grid(axis="x", color=GRID, linewidth=0.6)
        base = m.loc["2026_s07_base", key]
        ys = np.arange(len(LEVERS))[::-1]
        for y, (lv, lab) in zip(ys, LEVERS):
            ref = 100 * (1 - m.loc[f"2026_s07_{lv}", key] / base)
            ax.barh(y, ref, color=COLORS[lv], alpha=0.85, height=0.55)
            paired = [100 * (1 - p.loc[f"2026_s07_seed{s}_{lv}", key] / p.loc[f"2026_s07_seed{s}_base", key]) for s in range(1, 11)]
            ax.scatter(paired, y + rng.uniform(-0.16, 0.16, 10), color=INK, s=13, zorder=3, alpha=0.75)
            ax.text(max(ref, max(paired)) + 1.5, y, f"{ref:.0f} % (draws {min(paired):.0f}–{max(paired):.0f})", va="center", fontsize=7.5, color=INK)
        ax.set_yticks(ys); ax.set_yticklabels([lab for _, lab in LEVERS] if col == 0 else [""] * len(LEVERS), fontsize=8)
        ax.set_xlim(0, 105); ax.set_xlabel(f"{region}: value-added loss avoided, % of the base", color=MUTED, fontsize=8)
        ax.set_title(("a  " if col == 0 else "b  ") + f"{region}: reference draw (bars) and ten paired draws (dots)", loc="left", fontsize=8.8, color=INK)
    ax = fig.add_subplot(gs[1, :]); style(ax); ax.grid(axis="y", color=GRID, linewidth=0.6)
    q = m.loc["2026_s07_base", "DEU_cum_mUSD"] / m.loc["2026_s07_base", "DEU_%quarter"] / 13.0
    first = pd.Timestamp("2026-06-22")
    weeks = range(0, 30); dates = [first + pd.Timedelta(weeks=i - 1) for i in weeks]
    ax.plot(dates, w["2026_s07_base"].reindex(weeks).fillna(0) / q, color=INK, linewidth=2.2, label="base")
    for lv, lab in LEVERS:
        ax.plot(dates, w[f"2026_s07_{lv}"].reindex(weeks).fillna(0) / q, color=COLORS[lv], linewidth=1.5, label=lab)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_ylabel("German value-added loss, % of a week", color=MUTED, fontsize=8)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
    ax.set_title("c  Weekly German loss under each lever, reference draw", loc="left", fontsize=8.8, color=INK)
    fig.tight_layout(h_pad=1.5)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F7_levers.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F7 written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
