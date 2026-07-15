"""Foreign-aid 2D sweep figure: 4 mechanism diagnostics vs the import content of
reconstruction (capital_input_mix IMP fraction), one line per reconstruction_public_share.

Reads sweep_aid.py output. Each point is the Monte-Carlo mean across seeds (p10-p90 band).
The story to read off: at public_share=0.8 the lines are ~flat in IMP fraction (mix has
little leverage — only 20% is B2B); at public_share=0.0 the mix drives capital recovery,
CON/MAN crowding-out, and domestic reconstruction activity.

CLI: python plot_aid.py <aid_all.csv> [--fig PATH]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PANELS = [
    ("household_loss_pct_annual_gdp", "household loss (% of annual GDP)"),
    ("household_loss_conman_pct", "CON+MAN household loss (% GDP) — crowding-out"),
    ("conman_production_cum", "cumulative CON+MAN production — domestic activity"),
    ("capital_recovery_pct", "capital recovery by horizon (%)"),
]
COLORS = ["firebrick", "steelblue", "seagreen", "darkorange"]


def main():
    ap = argparse.ArgumentParser(description="Foreign-aid 2D sweep figure")
    ap.add_argument("csv", type=Path)
    ap.add_argument("--fig", type=Path, default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    n_seeds = df.seed.nunique() if "seed" in df.columns else 1
    shares = sorted(df["reconstruction_public_share"].unique())
    xs = sorted(df["imp_fraction"].unique())

    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    for ax, (col, title) in zip(axes.ravel(), PANELS):
        for i, ps in enumerate(shares):
            sub = df[df["reconstruction_public_share"] == ps]
            gp = sub.groupby("imp_fraction")[col]
            mean = gp.mean().reindex(xs)
            lo = gp.quantile(0.10).reindex(xs)
            hi = gp.quantile(0.90).reindex(xs)
            c = COLORS[i % len(COLORS)]
            ax.fill_between(xs, lo.values, hi.values, color=c, alpha=0.15, zorder=2)
            ax.plot(xs, mean.values, "-o", color=c, lw=2, zorder=3, label=f"public_share={ps:g}")
        ax.set_xlabel("import content of reconstruction (capital_input_mix IMP fraction)")
        ax.set_ylabel(title, fontsize=9)
        ax.set_title(title, fontsize=9)
        ax.set_xticks(xs)
        ax.grid(alpha=0.3)
    axes[0][0].legend(title="aid funding", fontsize=9, frameon=False)
    fig.suptitle(f"DisruptSC — foreign aid: reconstruction funding (public_share) x import "
                 f"sourcing (mix)\n{n_seeds} seeds, p10-p90 band", fontsize=12)
    fig.tight_layout()
    figpath = args.fig or args.csv.with_name("fig_aid.png")
    fig.savefig(figpath, dpi=140, bbox_inches="tight")
    print(f"-> {figpath}")


if __name__ == "__main__":
    main()
