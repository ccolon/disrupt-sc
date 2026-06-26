"""6x3 multi-panel plot of GDP deviation from baseline for the macroMIP s1 runs.

Reads the adapter CSVs (``<id>-DisruptSC.csv``, one per run folder under
``runs/macromip/<exp>/``) and draws a grid with one row per forced experiment
(exp1p, exp1t, exp2p, exp2t, exp3p, exp3t) and one column per country
(ESP, FRA, DEU). Each panel shows whole-economy GDP deviation from the no-forcing
baseline (exp0), in percent, by year:

    deviation(year) = 100 * (GDP_exp[year] - GDP_base[year]) / GDP_base[year]

Generate the adapter CSVs first, e.g.:

    for e in exp0 exp1p exp1t exp2p exp2t exp3p exp3t; do
        python -m disruptsc.reporting.macromip --run-dir runs/macromip/$e
    done
    python studies/macromip/plot_gdp_deviation.py            # -> runs/macromip/figures/gdp_deviation.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless (cluster-friendly)
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

ROOT = Path(__file__).resolve().parents[2]

COUNTRIES = ["ESP", "FRA", "DEU"]
BASELINE = "exp0"
WHOLE_ECONOMY = "TOTAL"
EXPERIMENTS = [
    ("exp1p", "1-p  Spain labour (persist.)"),
    ("exp1t", "1-t  Spain labour (temp.)"),
    ("exp2p", "2-p  France agri. (persist.)"),
    ("exp2t", "2-t  France agri. (temp.)"),
    ("exp3p", "3-p  Germany mfg (persist.)"),
    ("exp3t", "3-t  Germany mfg (temp.)"),
]


def load_gdp(run_dir: Path, variable: str) -> pd.Series | None:
    """Whole-economy GDP indexed by (Region, Year); None if no adapter CSV present."""
    csvs = sorted(run_dir.glob("*-DisruptSC.csv"))
    if not csvs:
        return None
    df = pd.read_csv(csvs[0])
    df = df[df["Sector"] == WHOLE_ECONOMY]
    return df.set_index(["Region", "Year"])[variable].sort_index()


def main():
    p = argparse.ArgumentParser(description="macroMIP GDP-deviation panel plot")
    p.add_argument("--runs-dir", type=Path, default=ROOT / "runs" / "macromip")
    p.add_argument("--variable", default="GDP_quantity",
                   choices=["GDP_quantity", "GDP_monetary"],
                   help="GDP_quantity = real/quantity effect (default); GDP_monetary = nominal")
    p.add_argument("--out", type=Path, default=None,
                   help="output figure path (default: <runs-dir>/figures/gdp_deviation.png)")
    args = p.parse_args()

    base = load_gdp(args.runs_dir / BASELINE, args.variable)
    if base is None:
        raise SystemExit(f"No baseline CSV under {args.runs_dir / BASELINE} — "
                         f"run `python -m disruptsc.reporting.macromip --run-dir "
                         f"{args.runs_dir / BASELINE}` first.")

    years = sorted(base.index.get_level_values("Year").unique())
    forcing_year = years[0] + 1 if len(years) > 1 else None   # year 1 = first forced year

    nrow, ncol = len(EXPERIMENTS), len(COUNTRIES)
    fig, axes = plt.subplots(nrow, ncol, figsize=(9.5, 14), sharex=True)

    for i, (key, label) in enumerate(EXPERIMENTS):
        gdp = load_gdp(args.runs_dir / key, args.variable)
        for j, country in enumerate(COUNTRIES):
            ax = axes[i, j]
            ax.axhline(0.0, color="0.6", lw=0.7, zorder=1)
            if forcing_year is not None:
                ax.axvline(forcing_year, color="0.85", lw=0.8, ls="--", zorder=1)
            if gdp is not None and country in gdp.index.get_level_values("Region"):
                exp_c = gdp.xs(country, level="Region")
                base_c = base.xs(country, level="Region")
                dev = (100.0 * (exp_c - base_c) / base_c).sort_index()
                ax.plot(dev.index, dev.values, marker="o", ms=3, lw=1.4,
                        color="#c0392b", zorder=3)
            else:
                ax.text(0.5, 0.5, "no data", ha="center", va="center",
                        transform=ax.transAxes, color="0.6", fontsize=8)
            ax.grid(True, alpha=0.25)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))   # y ticks as %
            if i == 0:
                ax.set_title(country, fontsize=11, fontweight="bold")
            if j == 0:
                ax.set_ylabel(label, fontsize=8)
    for j in range(ncol):
        axes[-1, j].set_xlabel("Year")

    fig.suptitle(f"GDP deviation from baseline (%) — {args.variable}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.985))

    out = args.out or (args.runs_dir / "figures" / "gdp_deviation.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}  ({nrow}x{ncol} panels, variable={args.variable})")


if __name__ == "__main__":
    main()
