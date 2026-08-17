"""Sensitivity figure: aggregate GDP loss (% of annual GDP) vs each swept parameter.

Small-multiples partial dependence: one panel per parameter that varies; x = its
levels, y = GDP loss, each other-parameter combo shown as a point with the mean
drawn as a line. Reads sensitivity_losses.csv (run_grid.py / combine.py).

CLI: python plot_sensitivity.py <sensitivity_losses.csv> [--metric COL] [--fig PATH]
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PARAMS = ["flow_coverage", "critical_input_threshold", "utilization_rate", "nb_suppliers_per_input",
          "reconstruction_market", "reconstruction_public_share", "reconstruction_target_time",
          "reconstruction_lag",
          # inventory sensitivity (multiplicative scales, x1 = baseline)
          "firm_inventory_scale", "household_inventory_scale", "inventory_restoration_scale",
          # per-input-type buffers in absolute DAYS (below one time step they are inert)
          "firm_utility_buffer_days", "firm_agriculture_buffer_days", "firm_manufacturing_buffer_days",
          "firm_trade_buffer_days", "firm_transport_buffer_days", "firm_service_buffer_days"]


def main():
    ap = argparse.ArgumentParser(description="Sensitivity partial-dependence figure")
    ap.add_argument("csv", type=Path)
    ap.add_argument("--metric", default="household_loss_pct_annual_gdp")
    ap.add_argument("--ncols", type=int, default=None,
                    help="panels per row (default min(6, n); a single long row is unreadable)")
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
    # Wrap into a grid: one row of ~18 panels is far too wide to read.
    ncols = args.ncols if args.ncols else min(6, n)
    nrows = math.ceil(n / ncols)
    # per-panel y-axis (effect sizes differ by ~20x across parameters, e.g. nb_suppliers)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.3 * ncols, 3.7 * nrows), squeeze=False, sharey=False)
    flat = [a for row in axes for a in row]

    # Baseline reference: with per-panel y-axes and the base level sitting at a different x in
    # every panel (leftmost for flow_coverage, middle for firm_inventory_scale, rightmost for
    # reconstruction_target_time), the baseline is otherwise impossible to locate by eye.
    base_rows = df[df.oat_param == "baseline"] if is_oat else df.iloc[0:0]
    base_val = base_rows[args.metric].mean() if len(base_rows) else None

    for ax, p in zip(flat, swept):
        sub = df[df.oat_param.isin(["baseline", p])] if is_oat else df
        gp = sub.groupby(p)[args.metric]
        levels = sorted(sub[p].unique())
        mean = gp.mean().reindex(levels)
        lo = gp.quantile(0.10).reindex(levels)                 # Monte-Carlo p10-p90 band across seeds
        hi = gp.quantile(0.90).reindex(levels)
        ax.scatter(sub[p], sub[args.metric], color="steelblue", alpha=0.30, s=18, zorder=3,
                   label=f"runs ({n_seeds} seeds)")
        ax.fill_between(levels, lo.values, hi.values, color="firebrick", alpha=0.18, zorder=2,
                        label="p10-p90")
        ax.plot(levels, mean.values, "-o", color="firebrick", lw=2, zorder=4, label="mean")
        if base_val is not None:
            ax.axhline(base_val, ls="--", lw=1.0, color="0.30", zorder=1,
                       label=f"baseline ({base_val:.2f}%)")
            bx = base_rows[p].iloc[0]                          # ring the baseline level itself
            if bx in mean.index:
                ax.scatter([bx], [mean.loc[bx]], s=130, facecolors="none", edgecolors="black",
                           lw=1.4, zorder=5)
        ax.set_xlabel(p, fontsize=8)
        ax.set_title(p, fontsize=9)
        ax.grid(alpha=0.3)
        ax.tick_params(labelsize=8)
        if sub[p].nunique() <= 5:
            ax.set_xticks(levels)
    for ax in flat[n:]:                                        # blank any unused grid cells
        ax.axis("off")
    for r in range(nrows):                                     # y-label once per row
        axes[r][0].set_ylabel(f"loss ({args.metric.replace('_', ' ')})", fontsize=8)
    flat[0].legend(fontsize=7, frameon=False)
    span = df[args.metric].max() - df[args.metric].min()
    label = "household loss (% of GDP)" if "household" in args.metric else args.metric.replace("_", " ")
    base_txt = f"baseline {base_val:.2f}% — " if base_val is not None else ""
    fig.suptitle(f"DisruptSC — sensitivity of {label}  ({base_txt}"
                 f"range {df[args.metric].min():.2f}–{df[args.metric].max():.2f}%, "
                 f"span {span:.2f} pp, {n_seeds} seeds)", fontsize=12)
    fig.tight_layout()
    figpath = args.fig or args.csv.with_name("fig_sensitivity.png")
    fig.savefig(figpath, dpi=140, bbox_inches="tight")
    print(f"-> {figpath}")


if __name__ == "__main__":
    main()
