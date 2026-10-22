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
from print_style import finish  # noqa: E402  text at print size (13 Oct 2026)
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
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main(out: Path):
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    p = table(AD / "compare_runs_batch_jobs_20261007_paired.csv")
    rv = AD / "compare_runs_batch_jobs_20261007_rev.csv"
    r = table(rv) if rv.exists() else pd.DataFrame()
    nr = AD / "compare_runs_batch_jobs_20261020_norail.csv"  # no rail alternative for any bulk (20 Oct 2026)
    if nr.exists():
        r = pd.concat([r, table(nr)])
    q = "DEU_%quarter"
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.6), gridspec_kw={"width_ratios": [1.0, 1.0]})
    fig.patch.set_facecolor("white")
    rng = np.random.default_rng(2)
    for ax, year in zip(axes, ("2026", "2018")):
        style(ax)
        base = m.loc[f"{year}_s07_base", q]
        draws = ([p.loc[f"2026_s07_seed{s}_base", q] for s in range(1, 11)] if year == "2026"
                 else [m.loc[f"2018_s07_seed{s}", q] for s in range(1, 11)])
        groups = [("network\ndraws\n(11)", draws + [base], BLUE),
                  ("loading\ncurve\n(±15 %)", [m.loc[f"{year}_s07_tablelow", q], m.loc[f"{year}_s07_tablehigh", q]], GREEN),
                  ("two\nsuppliers", [m.loc[f"{year}_s07_sup2", q]], PINK),
                  ("no input\npooling", [m.loc[f"{year}_s07_nopool", q]], ORANGE)]
        if year == "2026":
            groups.append(("one\nchannel\nonly", [m.loc["2026_s07_gateonly", q], m.loc["2026_s07_surchargeonly", q]], MUTED))
        if len(r) and f"{year}_rev_rail50" in r.index:
            rail = [r.loc[f"{year}_rev_rail50", q], r.loc[f"{year}_rev_rail140", q]]
            if f"{year}_rev_norail" in r.index:
                groups.append(("rail\nnone, 50,\n140 kt", [r.loc[f"{year}_rev_norail", q]] + rail, PURPLE))
            else:
                groups.append(("rail\n50, 140 kt", rail, PURPLE))
        if year == "2026" and len(r) and "2026_rev_rest15" in r.index:
            groups.append(("refill\ntime\n15, 60 d", [r.loc["2026_rev_rest15", q], r.loc["2026_rev_rest60", q]], TEAL))
            groups.append(("service\nrules", [r.loc["2026_rev_serv45", q], r.loc["2026_rev_dfuel0", q]], GOLD))
        ax.axvline(base, color=INK, linewidth=1.2, linestyle="--")
        ax.text(base + 0.02, -0.5, f"reference {base:.2f}", color=INK, fontsize=7.5, ha="left", va="top")
        top = max(max(v) for lab, v, _ in groups if not lab.startswith("no input")) * 1.22
        for y, (lab, vals, col) in enumerate(groups):
            if lab.startswith("no input") and max(vals) > top:
                ax.scatter([top * 0.97], [y], color=col, marker=">", s=40, zorder=3)
                ax.annotate(f"{max(vals):.2f}, off scale", (top * 0.97, y), textcoords="offset points", xytext=(-4, 7), fontsize=7, color=INK, ha="right")
                continue
            network = lab.startswith("network")
            jitter = rng.uniform(-0.12, 0.12, len(vals)) if network else np.zeros(len(vals))
            ax.scatter(vals, y + jitter, color=col, s=26, alpha=0.8, zorder=3)
            if network:
                ax.text(max(vals) + 0.06, y, f"{np.mean(vals):.2f} ± {np.std(vals, ddof=1):.2f}", fontsize=7, color=INK, ha="left", va="center")
        ax.set_yticks(range(len(groups))); ax.set_yticklabels([g[0].replace("\n", " ") for g in groups], fontsize=7.5)
        ax.set_ylim(-0.6, len(groups) - 0.3)
        ax.set_xlim(0, top)
        ax.invert_yaxis()
        ax.set_xlabel("German loss (% of a quarter)", color=MUTED, fontsize=8)
        ax.set_title(("(a) " if year == "2026" else "(b) ") + (f"{year}: sources of uncertainty" if year == "2026" else f"{year}"), loc="left", fontsize=9, color=INK)
    finish(fig)
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
