"""Fig. 2 of the Cambodia paper (claim H1, evidence E_ratio): floods closing roads in the three basins at once, against
the sum of the single-basin losses, for closures of 4, 8 and 12 days (10 Nov 2026).

Inputs: the grid batches grid_d4/d8/d12_20261108 (read_batch.py tables; scenarios lag0 = simultaneous, single_<basin>).
Ratio = simultaneous loss / sum of the three single-basin losses of the same network; 95 % intervals, t over networks
(10 networks at d = 4, 20 at d = 8 and 12); differences between closure lengths paired by network.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from paper import (BASIN_COLOR, BASIN_LABEL, BASIN_WORD, BASINS, DURATIONS, INK, MUTED, WIDTH, WORD, ci, num,
                   grid_wide, panel, save)
import matplotlib.pyplot as plt


def make(I, out, N):
    W = {d: grid_wide(I, d) for d in DURATIONS}
    R, S = {}, {}
    for d in DURATIONS:
        w = W[d]
        S[d] = w[[f"single_{b}" for b in BASINS]].sum(axis=1)
        R[d] = w.lag0 / S[d]
        k = WORD[d]
        N.put(f"Nets{k}", str(len(w)), f"networks of the grid at d = {d}")
        N.ci(f"RatioSim{k}", R[d], 2, f"three basins at once / sum of the three single-basin losses, d = {d}")
        N.put(f"ExcessSim{k}", num(100 * (R[d].mean() - 1), 0), f"% by which the simultaneous loss exceeds the sum of "
              f"the singles, d = {d} (mean ratio - 1)")
        N.put(f"LossSim{k}", num(w.lag0.mean(), 1), f"mUSD, household loss of the simultaneous floods, d = {d}")
        N.put(f"LossSumSingles{k}", num(S[d].mean(), 1), f"mUSD, sum of the three single-basin losses, d = {d}")
        for b in BASINS:
            N.put(f"LossSingle{BASIN_WORD[b]}{k}", num(w[f"single_{b}"].mean(), 2),
                  f"mUSD, household loss of the {BASIN_LABEL[b]} closure alone, d = {d}")
    allr = pd.concat(R.values())
    N.put("RatioSimMin", num(allr.min(), 2), "lowest ratio of any network and closure length")
    N.put("RatioSimMax", num(allr.max(), 2), "highest ratio of any network and closure length")
    for a, b in ((4, 8), (8, 12)):
        common = R[a].index.intersection(R[b].index)
        N.ci(f"RatioDiff{WORD[b]}{WORD[a]}", R[b][common] - R[a][common], 3,
             f"paired difference of the ratio, d = {b} minus d = {a} ({len(common)} networks)")

    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH["onehalf"], 58 / 25.4), gridspec_kw=dict(width_ratios=[1.35, 1]))
    x = np.arange(len(DURATIONS))
    for i, d in enumerate(DURATIONS):
        w, bottom = W[d], 0.0
        for bsn in BASINS:
            v = w[f"single_{bsn}"].mean()
            a.bar(i - 0.19, v, 0.34, bottom=bottom, color=BASIN_COLOR[bsn], edgecolor="white", linewidth=0.6,
                  label=f"{BASIN_LABEL[bsn]} alone" if i == 0 else None)
            bottom += v
        m, lo, hi = ci(w.lag0)
        a.bar(i + 0.19, m, 0.34, color=INK, label="three basins at once" if i == 0 else None)
        a.errorbar(i + 0.19, m, yerr=[[m - lo], [hi - m]], color=MUTED, lw=0.8, capsize=2)
        a.text(i + 0.19, hi + 0.4, f"×{R[d].mean():.2f}", ha="center", va="bottom", fontsize=6.5)
    a.set(xticks=x, xticklabels=[f"{d} days" for d in DURATIONS], xlabel="closure length",
          ylabel="household loss (million USD)")
    a.set_ylim(0, max(W[d].lag0.mean() for d in DURATIONS) * 1.18)
    h, lab = a.get_legend_handles_labels()
    a.legend(h[::-1], lab[::-1], loc="upper left", fontsize=6.5)
    panel(a, "a", "Losses: singles added vs at once")

    for i, d in enumerate(DURATIONS):
        r = R[d]
        jit = (np.asarray(r.index, float) - r.index.to_series().mean()) / max(len(r), 1) * 0.28
        b.scatter(i - 0.12 + jit, r, s=6, color=MUTED, linewidths=0, zorder=2)
        m, lo, hi = ci(r)
        b.errorbar(i + 0.22, m, yerr=[[m - lo], [hi - m]], fmt="o", color=INK, ms=3.5, lw=1, capsize=2.5, zorder=3)
    b.axhline(1, color=INK, lw=0.6, ls=":")
    b.text(2.45, 1.0, "additive", ha="right", va="bottom", fontsize=6.5, color=INK)
    b.set(xticks=x, xticklabels=[f"{d} days" for d in DURATIONS], xlabel="closure length",
          ylabel="at once / sum of the singles", ylim=(0.95, max(allr.max() * 1.03, 1.75)), xlim=(-0.5, 2.5))
    b.scatter([], [], s=6, color=MUTED, label="each network")
    b.errorbar([], [], fmt="o", color=INK, ms=3.5, label="mean, 95 % interval")
    b.legend(loc="lower left", bbox_to_anchor=(0.0, 0.18), fontsize=6.5)
    panel(b, "b", "Ratio by network")
    fig.tight_layout(w_pad=1.5)
    return save(fig, out, "fig2_simultaneous")
