"""Panel (c) of the event figure (Fig. 2): weekly German value-added loss of the 2026 season, reference draw and the
band of the eleven supply-chain draws, on the calendar of the gauge, with the provenance of the weeks shaded
(30 Sep 2026; review G6, F4 note).

Usage:
    python studies/rhine2026/plots/event_loss_panel.py [--out studies/rhine2026/figures]
Inputs: additional_data/compare_runs_batch_jobs_20261007_{main,paired}.{csv,txt}, scenarios/2026.csv.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
AD = HERE / "additional_data"
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, ORANGE = "#2f6fdb", "#e0842a"
SHADE = {"observed+forecast": ("#f5d58a", "partly observed"), "forecast": ("#f2b56b", "BfG six-week outlook"), "assumption": ("#d9d9d9", "assumed recovery")}


def weekly_block(txt_path: Path) -> pd.DataFrame:
    txt = txt_path.read_text(encoding="utf-8", errors="replace")
    block = txt.split("== weekly value-added loss of DEU (mUSD/week) ==")[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#") and not l.startswith("==")]
    return pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def main(out: Path):
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    wm = weekly_block(AD / "compare_runs_batch_jobs_20261007_main.txt")
    wp = weekly_block(AD / "compare_runs_batch_jobs_20261007_paired.txt")
    q_week = m.loc["2026_s07_base", "DEU_cum_mUSD"] / m.loc["2026_s07_base", "DEU_%quarter"] / 13.0
    prof = pd.read_csv(HERE / "scenarios" / "2026.csv")
    first = pd.Timestamp(prof.week_start.iloc[0])
    weeks = range(0, 30)
    dates = [first + pd.Timedelta(weeks=i - 1) for i in weeks]
    ref = wm["2026_s07_base"].reindex(weeks).fillna(0) / q_week
    band = pd.DataFrame({s: wp[f"2026_s07_seed{s}_base"].reindex(weeks).fillna(0) / q_week for s in range(1, 11)})
    fig, ax = plt.subplots(figsize=(11, 3.6))
    fig.patch.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8); ax.grid(axis="y", color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    seen = set()
    for w, st in zip(pd.to_datetime(prof.week_start), prof.status.astype(str)):
        if st in SHADE:
            col, lab = SHADE[st]
            ax.axvspan(w - pd.Timedelta(days=3.5), w + pd.Timedelta(days=3.5), color=col, alpha=0.35, linewidth=0, label=lab if lab not in seen else None)
            seen.add(lab)
    ax.fill_between(dates, band.min(axis=1), band.max(axis=1), color=BLUE, alpha=0.15, linewidth=0, label="ten further draws (range)")
    ax.fill_between(dates, band.quantile(0.25, axis=1), band.quantile(0.75, axis=1), color=BLUE, alpha=0.3, linewidth=0, label="interquartile range")
    ax.plot(dates, ref, color=INK, linewidth=2.2, label="reference draw")
    ax.axvline(first + pd.Timedelta(weeks=10), color=MUTED, linewidth=0.8, linestyle=":")
    # the last fully observed week of the profile (6 Oct 2026, review G3)
    obs = prof[prof.status.astype(str) == "observed"]
    if len(obs):
        last_obs = pd.Timestamp(obs.week_start.max()) + pd.Timedelta(days=3.5)
        ax.axvline(last_obs, color=MUTED, linewidth=0.9)
        ax.text(last_obs, max(ref.max(), band.max().max()) * 0.30, " forecast from here", color=MUTED, fontsize=7.5, ha="left", va="center", rotation=90)
    pk1, pk2 = ref.loc[1:10].idxmax(), ref.loc[11:].idxmax()
    ax.text(dates[pk1], ref[pk1] + 0.12, "August trough", color=MUTED, fontsize=8, ha="center")
    ax.text(dates[pk2], ref[pk2] + 0.12, "autumn trough", color=MUTED, fontsize=8, ha="center")
    ax.set_ylabel("German value-added loss, % of a week", color=MUTED, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlim(first - pd.Timedelta(weeks=1), first + pd.Timedelta(weeks=27))
    ax.set_ylim(0, max(ref.max(), band.max().max()) * 1.12)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
    ax.set_title("d  Weekly German value-added loss, reference draw and eleven draws", loc="left", fontsize=9.5, color=INK)
    fig.tight_layout()
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F4c_loss_2026.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F4c written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
