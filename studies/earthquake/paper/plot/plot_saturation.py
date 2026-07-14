"""Saturation figure: household loss (% of annual GDP) vs flow_coverage, one line
per critical_input_threshold (materiality floor gating the IHS criticality matrix).

The point of the figure: under a good production function, flow_coverage is a *speed*
knob and the loss should be FLAT across it (saturated). The pure matrix (floor 0.0)
keeps rising; the gated floors (0.01, 0.02) are flat. Each point is the Monte-Carlo
mean across seeds with a p10-p90 band.

CLI: python plot_saturation.py <raw_concat.csv> [--metric COL] [--fig PATH]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

COLORS = ["firebrick", "steelblue", "seagreen", "darkorange", "purple"]


def main():
    ap = argparse.ArgumentParser(description="flow_coverage saturation figure")
    ap.add_argument("csv", type=Path, help="raw per-seed rows (run_grid/combine --raw-out)")
    ap.add_argument("--metric", default="household_loss_pct_annual_gdp")
    ap.add_argument("--fig", type=Path, default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    for col in ("flow_coverage", "critical_input_threshold", args.metric):
        if col not in df.columns:
            raise SystemExit(f"column '{col}' missing from {args.csv}")

    n_seeds = df.seed.nunique() if "seed" in df.columns else 1
    floors = sorted(df["critical_input_threshold"].unique())
    fcs = sorted(df["flow_coverage"].unique())

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    for i, thr in enumerate(floors):
        sub = df[df["critical_input_threshold"] == thr]
        gp = sub.groupby("flow_coverage")[args.metric]
        mean = gp.mean().reindex(fcs)
        lo = gp.quantile(0.10).reindex(fcs)
        hi = gp.quantile(0.90).reindex(fcs)
        c = COLORS[i % len(COLORS)]
        label = "pure matrix (0.0)" if thr == 0 else f"gated @{thr:g}"
        ax.fill_between(fcs, lo.values, hi.values, color=c, alpha=0.15, zorder=2)
        ax.plot(fcs, mean.values, "-o", color=c, lw=2, zorder=3, label=label)
        ax.scatter(sub["flow_coverage"], sub[args.metric], color=c, alpha=0.30, s=18, zorder=2)

    ax.set_xlabel("flow_coverage  (network density / speed cutoff)")
    ax.set_ylabel("household loss (% of annual GDP)")
    ax.set_xticks(fcs)
    ax.grid(alpha=0.3)
    ax.legend(title="criticality floor", fontsize=9, frameon=False)
    ax.set_title(f"DisruptSC — flow_coverage saturation by criticality treatment "
                 f"({n_seeds} seeds, p10-p90 band)\nflat line = saturated (speed knob); "
                 f"rising line = cascade intensity leaks through", fontsize=10)
    fig.tight_layout()
    figpath = args.fig or args.csv.with_name("fig_saturation.png")
    fig.savefig(figpath, dpi=140, bbox_inches="tight")
    print(f"-> {figpath}")


if __name__ == "__main__":
    main()
