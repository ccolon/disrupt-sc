"""F10: the wave-isolation experiment (review point NS4, test T5), 29 Sep 2026.

(a) Weekly German value-added loss: the 2026 season (A then B, no gap), wave A alone, wave B alone placed at
    its calendar position, and their sum - the area between the season and the sum is the interaction.
(b) Cumulated loss of A then B against the weeks of normal water between them, with L(A) + L(B) as the
    reference, and the flat profile (same tonnage turned away, spread evenly).

Usage:
    python studies/rhine2026/plots/wave_figure.py [--out studies/rhine2026/figures]
Inputs: additional_data/compare_runs_batch_waves.{csv,txt}, compare_runs_batch_20260929_gs1paper.{csv,txt}.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
AD = HERE / "additional_data"
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, ORANGE, GREEN = "#2f6fdb", "#e0842a", "#3a9a5b"
SPLIT = 10                                   # wave B starts in profile week 11
FIRST = pd.Timestamp("2026-06-22")


def weekly_block(txt_path: Path) -> pd.DataFrame:
    txt = txt_path.read_text(encoding="utf-8", errors="replace")
    block = txt.split("== weekly value-added loss of DEU (mUSD/week) ==")[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#")
             and not l.startswith("==")]
    return pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main(out: Path):
    w = weekly_block(AD / "compare_runs_batch_jobs_20261007_main.txt")
    base = weekly_block(AD / "compare_runs_batch_jobs_20261007_main.txt")["2026_s07_base"]
    t = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    b0 = t.loc["2026_s07_base"]
    q = b0["DEU_cum_mUSD"] / b0["DEU_%quarter"]                 # mUSD per 1 % of a quarter
    wk = q / 13.0                                                  # mUSD per 1 % of a week

    weeks = range(0, 34)
    a = w["wave07_A"].reindex(weeks).fillna(0.0)
    b = w["wave07_B"].reindex(weeks).fillna(0.0)
    b_shift = pd.Series([b.get(i - SPLIT, 0.0) if i >= SPLIT else 0.0 for i in weeks], index=weeks)
    season = base.reindex(weeks).fillna(0.0)
    dates = [FIRST + pd.Timedelta(weeks=i - 1) for i in weeks]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.45, 1]})
    fig.patch.set_facecolor("white")

    ax = axes[0]; style(ax)
    total = (a + b_shift) / wk
    # signed interaction (6 Oct 2026, review G3): orange where the sequence costs more than the sum, blue where less
    ax.fill_between(dates, total, season / wk, where=(season / wk) >= total, color=ORANGE, alpha=0.22, linewidth=0,
                    label="interaction: the sequence costs more than the sum")
    ax.fill_between(dates, total, season / wk, where=(season / wk) < total, color=BLUE, alpha=0.22, linewidth=0,
                    label="the sequence costs less than the sum")
    ax.plot(dates, season / wk, color=INK, linewidth=2.2, label="the 2026 season (A then B)")
    ax.plot(dates, total, color=MUTED, linewidth=1.3, linestyle="--", label="A alone + B alone")
    ax.plot(dates, a / wk, color=BLUE, linewidth=1.5, label="first wave alone (22 June – 30 August)")
    ax.plot(dates, b_shift / wk, color=GREEN, linewidth=1.5, label="second wave alone (from 31 August)")
    ax.axvline(FIRST + pd.Timedelta(weeks=SPLIT), color=MUTED, linewidth=0.8, linestyle=":")
    ax.set_ylabel("German value-added loss, % of a week", color=MUTED, fontsize=8)
    ax.set_ylim(0, 3.2)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(FIRST - pd.Timedelta(weeks=1), FIRST + pd.Timedelta(weeks=28))
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_title("a  Two troughs, alone and in sequence", loc="left", fontsize=9.5, color=INK)

    ax = axes[1]; style(ax)
    gaps = [0, 1, 2, 4, 8]
    L = [b0["DEU_cum_mUSD"]] + [t.loc[f"wave07_AB_gap{g}", "DEU_cum_mUSD"] for g in gaps[1:]]
    s = (t.loc["wave07_A", "DEU_cum_mUSD"] + t.loc["wave07_B", "DEU_cum_mUSD"]) / q
    ax.axhline(s, color=MUTED, linewidth=1.3, linestyle="--")
    ax.text(8.0, s + 0.02, f"A alone + B alone: {s:.2f}", color=MUTED, fontsize=7.5, ha="right", va="bottom")
    ax.plot(gaps, [v / q for v in L], color=INK, linewidth=1.8, marker="o", markersize=5)
    for g, v in zip(gaps, L):
        ax.annotate(f"{v / q:.2f}", (g, v / q), textcoords="offset points", xytext=(6, 5) if g != 4 else (6, -13), fontsize=7.5, color=INK)
    f = t.loc["wave07_flat", "DEU_cum_mUSD"] / q
    ax.axhline(f, color=GREEN, linewidth=1.0, linestyle=":")
    ax.text(8.0, f - 0.02, f"same tonnage turned away, spread evenly: {f:.2f}", color=GREEN, fontsize=7.5, ha="right", va="top")
    ax.set_xticks(gaps)
    ax.set_xlabel("weeks of normal water between the two troughs", color=MUTED, fontsize=8)
    ax.set_ylabel("German loss, % of a quarter", color=MUTED, fontsize=8)
    ax.set_ylim(1.2, 1.85)
    ax.set_title("b  The interaction fades within a month", loc="left", fontsize=9.5, color=INK)

    fig.tight_layout(w_pad=2.0)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F10_wave_isolation.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F10 written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
