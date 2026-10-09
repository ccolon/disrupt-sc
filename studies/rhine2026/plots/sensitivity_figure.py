"""F8: the German loss under each kind of uncertainty, grouped by type (30 Sep 2026; review G5, F8 note; extended 9 Oct
2026 with the rules of the revision, review of 8 Oct G4).

For 2026 and 2018 side by side: the reference draw and the ten further draws of the supply-chain network (a
sampling uncertainty); the loading-table band (a structural assumption: the shortfall of the draught table x 0.85
and x 1.15); two suppliers per input instead of one (a specification); no input pooling (a specification); for
2026, the two channels alone (the quantity constraint without the surcharge, the surcharge without the
constraint); and the rules tested in the revision: substitution by rail at 50 and 140 kt a week (both events), the
refill time of a stock gap at 15 and 60 days, and the service propagation (a 45-day coping duration for the
non-storable inputs; the power sector's fuel-oil input non-critical). These are not one distribution: the panel
keeps them apart.

Usage:
    python studies/rhine2026/plots/sensitivity_figure.py [--out studies/rhine2026/figures]
Inputs: additional_data/compare_runs_batch_jobs_20261007_{main,paired,rev}.csv.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
AD = HERE / "additional_data"
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, ORANGE, GREEN, PINK = "#2f6fdb", "#e0842a", "#3a9a5b", "#d1519a"
PURPLE, TEAL, GOLD = "#7b4fb8", "#1f9e9e", "#b8860b"


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
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    p = table(AD / "compare_runs_batch_jobs_20261007_paired.csv")
    rv = AD / "compare_runs_batch_jobs_20261007_rev.csv"
    r = table(rv) if rv.exists() else pd.DataFrame()
    q = "DEU_%quarter"
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.75, 1]})
    fig.patch.set_facecolor("white")
    rng = np.random.default_rng(2)
    for ax, year in zip(axes, ("2026", "2018")):
        style(ax)
        base = m.loc[f"{year}_s07_base", q]
        draws = ([p.loc[f"2026_s07_seed{s}_base", q] for s in range(1, 11)] if year == "2026"
                 else [m.loc[f"2018_s07_seed{s}", q] for s in range(1, 11)])
        groups = [("supply-chain\ndraws (11)", draws + [base], BLUE),
                  ("loading table\n(shortfall\n×1.15, ×0.85)", [m.loc[f"{year}_s07_tablelow", q], m.loc[f"{year}_s07_tablehigh", q]], GREEN),
                  ("two suppliers\nper input", [m.loc[f"{year}_s07_sup2", q]], PINK),
                  ("no input\npooling", [m.loc[f"{year}_s07_nopool", q]], ORANGE)]
        if year == "2026":
            groups.append(("one channel:\nconstraint only,\nsurcharge only", [m.loc["2026_s07_gateonly", q], m.loc["2026_s07_surchargeonly", q]], MUTED))
        if len(r) and f"{year}_rev_rail50" in r.index:
            groups.append(("substitution\nby rail\n(50, 140 kt a week)", [r.loc[f"{year}_rev_rail50", q], r.loc[f"{year}_rev_rail140", q]], PURPLE))
        if year == "2026" and len(r) and "2026_rev_rest15" in r.index:
            groups.append(("refill time of\na stock gap\n(15, 60 days)", [r.loc["2026_rev_rest15", q], r.loc["2026_rev_rest60", q]], TEAL))
            groups.append(("service propagation:\ncoping 45 days,\nfuel oil non-critical", [r.loc["2026_rev_serv45", q], r.loc["2026_rev_dfuel0", q]], GOLD))
        ax.axhline(base, color=INK, linewidth=1.2, linestyle="--")
        ax.text(-0.45, base + 0.04, f"reference {base:.2f}", color=INK, fontsize=7.5, ha="left", va="bottom")
        top = max(max(v) for lab, v, _ in groups if not lab.startswith("no input")) * 1.22
        for x, (lab, vals, col) in enumerate(groups):
            if lab.startswith("no input") and max(vals) > top:
                ax.scatter([x], [top * 0.97], color=col, marker="^", s=40, zorder=3)
                ax.annotate(f"{max(vals):.2f} (off scale)", (x, top * 0.97), textcoords="offset points", xytext=(8, -3), fontsize=7.5, color=INK)
                continue
            jitter = rng.uniform(-0.12, 0.12, len(vals)) if len(vals) > 2 else np.zeros(len(vals))
            ax.scatter(x + jitter, vals, color=col, s=26, alpha=0.8, zorder=3)
            if len(vals) <= 2:
                for v in vals:
                    ax.annotate(f"{v:.2f}", (x, v), textcoords="offset points", xytext=(8, -3), fontsize=7.5, color=INK)
            else:
                ax.text(x + 0.2, float(np.mean(vals)), f"{np.mean(vals):.2f} ± {np.std(vals, ddof=1):.2f}", fontsize=7.5, color=INK, va="center")
        ax.set_xticks(range(len(groups))); ax.set_xticklabels([g[0] for g in groups], fontsize=7.2)
        ax.set_xlim(-0.5, len(groups) - 0.4)
        ax.set_ylim(0, top)
        ax.set_ylabel("German value-added loss, % of a quarter", color=MUTED, fontsize=8)
        ax.set_title(("a  " if year == "2026" else "b  ") + f"{year}: sampling, structural and specification uncertainties, and the rules", loc="left", fontsize=9, color=INK)
    fig.tight_layout(w_pad=2.0)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F8_sensitivity.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F8 written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
