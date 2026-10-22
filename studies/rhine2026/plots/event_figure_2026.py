"""The event figure (Fig. 2) in two panels (22 Oct 2026, the author's notes of 21 Oct): (a) the weekly Kaub gauge with the
provenance of the weeks shaded and the share of the normal tonnage that the Kaub reach passes on the right axis; (b) the
weekly German value-added loss as the mean, interquartile range and range of the eleven supplier-buyer networks.
Replaces F4_shock_2026 + F4c_loss_2026 in the manuscript.

Usage:
    python studies/rhine2026/plots/event_figure_2026.py [--out studies/rhine2026/figures]
Inputs: scenarios/2026.csv, scenarios/draught_table.csv, additional_data/compare_runs_batch_jobs_20261007_{main,paired}.{csv,txt}.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from event_loss_panel import AD, HERE, SHADE, table, weekly_block  # noqa: E402
from print_style import finish  # noqa: E402
from scenario_figures import load_factor_curve, weekly_reductions  # noqa: E402

INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, GREEN = "#2f6fdb", "#3a9a5b"


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8); ax.grid(axis="y", color=GRID, linewidth=0.6); ax.set_axisbelow(True)


def main(out: Path):
    prof = pd.read_csv(HERE / "scenarios" / "2026.csv")
    weeks = pd.to_datetime(prof["week_start"])
    curve = load_factor_curve(HERE / "scenarios" / "draught_table.csv")
    share = [100 * (1 - r) for r in weekly_reductions(prof, curve)]
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    wm = weekly_block(AD / "compare_runs_batch_jobs_20261007_main.txt")
    wp = weekly_block(AD / "compare_runs_batch_jobs_20261007_paired.txt")
    q_week = m.loc["2026_s07_base", "DEU_cum_mUSD"] / m.loc["2026_s07_base", "DEU_%quarter"] / 13.0
    first = pd.Timestamp(prof.week_start.iloc[0])
    wk = range(0, 30)
    dates = [first + pd.Timedelta(weeks=i - 1) for i in wk]
    nets = pd.DataFrame({s: wp[f"2026_s07_seed{s}_base"].reindex(wk).fillna(0) / q_week for s in range(1, 11)})
    nets["ref"] = wm["2026_s07_base"].reindex(wk).fillna(0) / q_week
    mean = nets.mean(axis=1)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.6), sharex=True, gridspec_kw={"height_ratios": [1, 1.15]})
    fig.patch.set_facecolor("white")
    obs = prof[prof.status.astype(str) == "observed"]
    last_obs = pd.Timestamp(obs.week_start.max()) + pd.Timedelta(days=3.5) if len(obs) else None
    for ax in (a1, a2):
        style(ax)
        for w, st in zip(weeks, prof.status.astype(str)):
            if st in SHADE:
                ax.axvspan(w - pd.Timedelta(days=3.5), w + pd.Timedelta(days=3.5), color=SHADE[st][0], alpha=0.35, linewidth=0)
        if last_obs is not None:
            ax.axvline(last_obs, color=MUTED, linewidth=0.9)
    # (a) the gauge and the share passing
    a1.plot(weeks, prof["kaub_cm"], color=INK, linewidth=1.8, marker="o", markersize=3.5, label="Kaub gauge, weekly mean (cm)")
    a1.axhline(78, color=MUTED, linewidth=0.8, linestyle="--")
    a1.text(weeks.iloc[0], 82, "78 cm, equivalent low water", fontsize=7, color=MUTED, va="bottom")
    a1.set_ylabel("Kaub gauge (cm)", color=MUTED, fontsize=8)
    a1.set_ylim(-15, max(175, float(prof.kaub_cm.max()) + 60))
    a1r = a1.twinx()
    a1r.plot(weeks, share, color=GREEN, linewidth=1.6, marker="s", markersize=3, label="share of normal tonnage passing (%)")
    a1r.set_ylim(0, 105); a1r.set_ylabel("tonnage passing (% of normal)", color=GREEN, fontsize=8)
    a1r.tick_params(colors=GREEN, labelsize=8)
    for s in ("top",):
        a1r.spines[s].set_visible(False)
    a1r.spines["right"].set_color(GREEN)
    seen = []
    for st, (col, lab) in SHADE.items():
        if (prof.status.astype(str) == st).any():
            seen.append(plt.Rectangle((0, 0), 1, 1, color=col, alpha=0.35, linewidth=0, label=lab))
    h1, l1 = a1.get_legend_handles_labels(); h2, l2 = a1r.get_legend_handles_labels()
    a1.legend(h1 + h2 + seen, l1 + l2 + [p.get_label() for p in seen], frameon=False, fontsize=7, loc="upper center", ncol=3)
    a1.set_title("(a) The 2026 low water at Kaub", loc="left", fontsize=9.5, color=INK)
    # (b) the weekly loss, eleven networks
    a2.fill_between(dates, nets.min(axis=1), nets.max(axis=1), color=BLUE, alpha=0.15, linewidth=0, label="range of the eleven networks")
    a2.fill_between(dates, nets.quantile(0.25, axis=1), nets.quantile(0.75, axis=1), color=BLUE, alpha=0.3, linewidth=0, label="interquartile range")
    a2.plot(dates, mean, color=INK, linewidth=2.2, label="mean of the eleven networks")
    pk1, pk2 = mean.loc[1:10].idxmax(), mean.loc[11:].idxmax()
    a2.text(dates[pk1], mean[pk1] + 0.12, "August episode", color=MUTED, fontsize=8, ha="center")
    a2.text(dates[pk2], mean[pk2] + 0.12, "autumn episode", color=MUTED, fontsize=8, ha="center")
    if last_obs is not None:
        a2.text(last_obs - pd.Timedelta(days=1.5), float(nets.max().max()) * 0.82, "forecast from here ", color=MUTED, fontsize=7.5, ha="right", va="center", rotation=90)
    a2.set_ylabel("German value-added loss\n(% of a week)", color=MUTED, fontsize=8)
    a2.set_ylim(0, float(nets.max().max()) * 1.12)
    a2.legend(frameon=False, fontsize=7, loc="upper left")
    a2.set_title("(b) Weekly German loss", loc="left", fontsize=9.5, color=INK)
    a2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    a2.set_xlim(first - pd.Timedelta(weeks=1), first + pd.Timedelta(weeks=27))
    finish(fig)
    fig.tight_layout()
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F4_event_2026.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F4_event_2026 written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
