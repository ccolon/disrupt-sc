"""Fig. 4 of the Cambodia paper (claim S1, evidence E_mech): why the timing matters (10 Nov 2026).

(a) When the excess occurs: daily household loss with both basins closed on days 1-12 (pair run, tau 0) against the
    sum of the two single closures, mean over networks 1-10 (overlap_excess.py daily paths, runs/overlap_logs/
    paths_mean.csv).
(b) Why: during the closure, order value that travels by an alternative route or finds no route at all (blocked),
    both basins closed against the two singles added (base__routing_closure_days.csv, container and dry-bulk cargo,
    mean over networks).
(c) What inventories do: two-flood ratio at tau 0, 12 and 24 with inventory targets x0.5, x1 and x2 (rob_d12_20261108,
    pair and grid batches for x1). The overlap interaction (tau 0) does not depend on them; the leftover after the
    closures stop overlapping (tau >= 12) does.
Report 10 (reports/10_overlap.md) holds the analysis; the robustness macros are put by figS_robustness.py.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from paper import (BASIN_COLOR, BASIN_LABEL, EXCESS, INK, INV_COLOR, MUTED, OVERLAP, SHADE, WIDTH, ci, num, panel,
                   rob_wide, save)

D = 12


def make(I, out, N):
    paths = I.csv(f"{OVERLAP}/paths_mean.csv", index_col=["series", "run"])
    paths.columns = paths.columns.astype(int)
    hh = {r: paths.loc[("hh_consumption_loss", r)] + paths.loc[("hh_extra_spending", r)]
          for r in ("pair", "mekong", "tonle")}
    sing = hh["mekong"] + hh["tonle"]

    C = I.csv(f"{OVERLAP}/base__household_components.csv")
    piv = C.pivot_table(index=["seed", "component", "period"], columns="run", values="loss", aggfunc="sum")
    ex = (piv["pair"] - piv["mekong"] - piv["tonle"]).groupby(["component", "period"]).mean()
    tot = ex.sum()
    N.put("ExcessOverlapTotal", num(tot, 2), "mUSD, household loss of both closures at once (tau 0, d = 12) minus "
          "the two singles, networks 1-10 (overlap_excess.py)")
    N.put("ExcessUnmetShare", num(100 * ex.loc["consumption_loss"].sum() / tot, 0),
          "% of that excess that is unmet consumption (the rest: extra spending on dearer goods)")
    per = ex.groupby("period").sum()
    for lab, name in (("days 1-12 (closed)", "Closed"), ("days 13-42", "ThirtyAfter"), ("days 43 on", "Later")):
        N.put(f"ExcessShare{name}", num(100 * per[lab] / tot, 0), f"% of the excess falling on {lab}")

    G = I.csv(f"{OVERLAP}/base__routing_closure_days.csv")
    G = G[G.cargo.isin(["container", "dry_bulk"])]
    R = G.groupby(["run", "seed"])[["alternative_usd", "blocked_usd"]].sum().groupby("run").mean()
    for col, name in (("blocked_usd", "Blocked"), ("alternative_usd", "Alt")):
        N.put(f"{name}Pair", num(R.loc["pair", col], 1), f"mUSD of orders over days 1-12, both closed: {col[:-4]}")
        N.put(f"{name}Singles", num(R.loc["mekong", col] + R.loc["tonle", col], 1),
              f"mUSD of orders over days 1-12, Mekong alone + Tonle Sap alone: {col[:-4]}")
    for sec, name in (("CRO", "Crop"), ("FIS", "Fish")):
        s = f"{sec}_production"
        gp = 1 - paths.loc[(s, "pair")][D]
        gs = (1 - paths.loc[(s, "mekong")][D]) + (1 - paths.loc[(s, "tonle")][D])
        N.put(f"{name}CutPair", num(100 * gp, 1), f"% below day 0 of {name.lower()} output on day {D}, both closed")
        N.put(f"{name}CutSingles", num(100 * gs, 1), f"% below day 0 of {name.lower()} output on day {D}, the two "
              "single closures' shortfalls added")

    fig, ax = plt.subplots(1, 3, figsize=(WIDTH["double"], 62 / 25.4), gridspec_kw=dict(width_ratios=[1.3, 0.8, 1]))
    a = ax[0]
    days = np.arange(0, 61)
    a.axvspan(1, D, color=SHADE, lw=0, zorder=0)
    a.text(D / 2 + 0.5, 0.02, "roads\nclosed", ha="center", va="bottom", fontsize=6.5)
    a.fill_between(days, sing.loc[0:60], hh["pair"].loc[0:60], color=EXCESS, lw=0, label="excess")
    a.plot(days, hh["pair"].loc[0:60], color=INK, lw=1.3, label="both basins at once")
    a.plot(days, sing.loc[0:60], color=MUTED, lw=1.1, ls="--", label="Mekong alone + Tonle Sap alone")
    a.set(xlabel="day", ylabel="household loss (million USD a day)", xlim=(0, 60), ylim=(0, None))
    a.legend(loc="upper right", fontsize=6.5)
    panel(a, "a", "When the excess occurs")

    a = ax[1]
    for i, col in enumerate(("blocked_usd", "alternative_usd")):
        a.bar(i - 0.19, R.loc["pair", col], 0.34, color=INK, label="both at once" if i == 0 else None)
        a.bar(i + 0.19, R.loc["mekong", col], 0.34, color=BASIN_COLOR["mekong"], edgecolor="white", linewidth=0.6,
              label=f"{BASIN_LABEL['mekong']} alone" if i == 0 else None)
        a.bar(i + 0.19, R.loc["tonle", col], 0.34, bottom=R.loc["mekong", col], color=BASIN_COLOR["tonle"],
              edgecolor="white", linewidth=0.6, label=f"{BASIN_LABEL['tonle']} alone" if i == 0 else None)
    a.set(xticks=[0, 1], xticklabels=["no route", "detour"], ylabel="orders during the closure (million USD)",
          ylim=(0, 150))
    a.legend(loc="upper left", fontsize=6.5)
    panel(a, "b", "Routing")

    a = ax[2]
    L = rob_wide(I)
    taus = (0, 12, 24)
    for v, lab, off, mk, fc, col, ls in (
            ("inv0.5", "inventory targets ×0.5", -1.2, "o", "white", INV_COLOR, "--"),
            ("base", "inventory targets ×1 (base)", 0.0, "o", INK, INK, "-"),
            ("inv2", "inventory targets ×2", 1.2, "s", INV_COLOR, INV_COLOR, "-")):
        st = np.array([ci(L.loc[v][f"R{t}"]) for t in taus])
        a.errorbar(np.array(taus) + off, st[:, 0], yerr=[st[:, 0] - st[:, 1], st[:, 2] - st[:, 0]], color=col,
                   marker=mk, mfc=fc, mec=col, ms=3.5, lw=1, ls=ls, capsize=2, label=lab)
    a.axvspan(-3, D, color=SHADE, lw=0, zorder=0)
    a.text(D / 2 - 1.5, 1.015, "closures overlap", ha="center", va="bottom", fontsize=6.5)
    a.axhline(1, color=INK, lw=0.6, ls=":")
    a.set(xticks=taus, xlim=(-3, 27), ylim=(0.92, None), xlabel="days between the starts (Mekong first)",
          ylabel="loss / sum of the two single-basin losses")
    a.legend(loc="upper right", fontsize=6.5)
    panel(a, "c", "Inventories")
    fig.tight_layout(w_pad=1.2)
    return save(fig, out, "fig4_mechanism")
