"""Sensitivity figure: aggregate GDP loss (% of annual GDP) vs each swept parameter.

Small-multiples partial dependence: one panel per parameter that varies; x = its
levels, y = GDP loss, each other-parameter combo shown as a point with the mean
drawn as a line. Reads sensitivity_losses.csv (run_grid.py / combine.py).

CLI: python plot_sensitivity.py <sensitivity_losses.csv> [--metric COL] [--fig PATH]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PARAMS = ["flow_coverage", "critical_input_threshold", "utilization_rate", "nb_suppliers_per_input",
          "reconstruction_market", "reconstruction_public_share", "reconstruction_target_time",
          "reconstruction_lag"]


def main():
    ap = argparse.ArgumentParser(description="Sensitivity partial-dependence figure")
    ap.add_argument("csv", type=Path)
    ap.add_argument("--metric", default="household_loss_pct_annual_gdp")
    ap.add_argument("--fig", type=Path, default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    is_oat = "oat_param" in df.columns                     # OAT: each panel = baseline + that param's variations
    if is_oat:
        swept = [p for p in PARAMS if p in df.columns and (df.oat_param == p).any()]
    else:
        swept = [p for p in PARAMS if p in df.columns and df[p].nunique() > 1]
    if not swept:
        raise SystemExit("no parameter varies in the sweep")

    n_seeds = df.seed.nunique() if "seed" in df.columns else 1
    n = len(swept)
    # per-panel y-axis (effect sizes differ by ~20x across parameters, e.g. flow_coverage)
    fig, axes = plt.subplots(1, n, figsize=(3.3 * n, 4.2), squeeze=False, sharey=False)
    for ax, p in zip(axes[0], swept):
        sub = df[df.oat_param.isin(["baseline", p])] if is_oat else df
        gp = sub.groupby(p)[args.metric]
        levels = sorted(sub[p].unique())
        mean = gp.mean().reindex(levels)
        lo = gp.quantile(0.10).reindex(levels)                 # Monte-Carlo p10-p90 band across seeds
        hi = gp.quantile(0.90).reindex(levels)
        ax.scatter(sub[p], sub[args.metric], color="steelblue", alpha=0.35, s=22, zorder=3,
                   label=f"runs ({n_seeds} seeds)")
        ax.fill_between(levels, lo.values, hi.values, color="firebrick", alpha=0.18, zorder=2,
                        label="p10-p90")
        ax.plot(levels, mean.values, "-o", color="firebrick", lw=2, zorder=4, label="mean")
        ax.set_xlabel(p)
        ax.set_title(p, fontsize=9)
        ax.grid(alpha=0.3)
        if sub[p].nunique() <= 5:
            ax.set_xticks(levels)
    axes[0][0].set_ylabel(f"GDP loss ({args.metric.replace('_', ' ')})")
    axes[0][-1].legend(fontsize=8, frameon=False)
    span = df[args.metric].max() - df[args.metric].min()
    label = "household loss (% of GDP)" if "household" in args.metric else args.metric.replace("_", " ")
    fig.suptitle(f"DisruptSC — sensitivity of {label}  "
                 f"(range {df[args.metric].min():.2f}–{df[args.metric].max():.2f}%, "
                 f"span {span:.2f} pp, {n_seeds} seeds)", fontsize=12)
    fig.tight_layout()
    figpath = args.fig or args.csv.with_name("fig_sensitivity.png")
    fig.savefig(figpath, dpi=140, bbox_inches="tight")
    print(f"-> {figpath}")


if __name__ == "__main__":
    main()
