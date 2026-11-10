"""Fig. 3 of the Cambodia paper (headline claim H2, evidence E_curve): the loss of successive floods against the time
between them, at one-day resolution (10 Nov 2026).

(a) Three basins in succession (Saigon, Mekong, Tonle Sap starting on days 1, 1 + lag, 1 + 2 lag), closures of 4, 8 and
    12 days: loss / sum of the three single-basin losses against the lag (grid_d4/d8/d12_20261108).
(b) Two basins (Mekong and Tonle Sap), 12-day closures, either order: loss / (single Mekong + single Tonle Sap) against
    tau = start of the Tonle Sap closure - start of the Mekong closure (pair_d12_20261108; singles from grid_d12).
Leftover = ratio - 1 once the closures no longer overlap (lag >= d). 95 % intervals, t over networks.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from paper import (BASINS, DURATIONS, DUR_COLOR, INK, MUTED, SHADE, WIDTH, WORD, ci, grid_wide, num, pair_ratio,
                   pair_wide, panel, save)


def lag_ratios(w):
    singles = w[[f"single_{b}" for b in BASINS]].sum(axis=1)
    lags = sorted(int(c[3:]) for c in w.columns if c.startswith("lag"))
    return {L: w[f"lag{L}"] / singles for L in lags}, singles


def make(I, out, N):
    W = {d: grid_wide(I, d) for d in DURATIONS}
    curves = {}
    for d in DURATIONS:
        curves[d], _ = lag_ratios(W[d])
        k = WORD[d]
        for mult, name in ((1, "Btb"), (2, "TwoD"), (4, "FourD")):
            N.ci(f"Leftover{name}{k}", curves[d][mult * d], 1,
                 f"% (ratio - 1), three floods, d = {d}, starts {mult * d} days apart"
                 + (" (back to back)" if mult == 1 else ""), scale=100, shift=-1)
    btb = 100 * (curves[12][12] - 1)
    N.put("LeftoverBtbTwelveMedian", num(btb.median(), 1), "% median over networks, back to back, d = 12")
    N.put("LeftoverBtbTwelveMax", num(btb.max(), 1), "% largest network, back to back, d = 12")
    N.put("LeftoverBtbTwelveMaxNet", str(int(btb.idxmax())), "the network with the largest leftover (its id)")
    gap = W[12].lag13 / W[12].lag12 - 1
    N.ci("OneDayGapTwelve", gap, 2, "% change of the loss when one day separates back-to-back 12-day closures "
         "(lag 13 vs 12, paired)", scale=100)

    # Two floods: tent, order effect, and Saigon's additivity.
    P = pair_ratio(I)
    taus = sorted(P.columns)
    N.put("PairNets", str(len(P)), "networks of the two-flood runs")
    for t in (0, 12, 24, 36):
        both = (P[t] + P[-t]) / 2 if t else P[0]
        N.ci(f"PairRatioTau{WORD[t]}", both, 2 if t == 0 else 3,
             f"two floods / sum of the two singles, |tau| = {t}" + (" (mean of both orders)" if t else ""))
    pos = [t for t in taus if t > 0 and -t in taus]
    diff = {t: P[t] - P[-t] for t in pos}          # Mekong first minus Tonle Sap first
    tmax = min(pos, key=lambda t: diff[t].mean())
    N.put("OrderEffectMax", num(-diff[tmax].mean(), 3), "largest mean advantage of Tonle Sap first over Mekong first "
          "(difference of the ratios, in units of the singles' sum)")
    N.put("OrderEffectTau", str(tmax), "|tau| (days) where the order effect is largest")
    N.put("OrderEffectNets", str(int((diff[tmax] < 0).sum())), f"networks where Tonle Sap first loses more at |tau| = {tmax}")
    late = [t for t in pos if t >= 12]
    N.put("OrderEffectLateMax", num(max(abs(diff[t].mean()) for t in late), 3),
          "largest mean order effect once the closures no longer overlap (|tau| >= 12)")
    Pw, G = pair_wide(I), W[12]
    nets = Pw.index
    x3 = G.loc[nets, "lag0"] - G.loc[nets, [f"single_{b}" for b in BASINS]].sum(axis=1)
    x2 = Pw[0] - G.loc[nets, "single_mekong"] - G.loc[nets, "single_tonle"]
    N.put("ExcessThreeTwelve", num(x3.mean(), 2), "mUSD, three basins at once minus the three singles, d = 12, "
          f"networks {nets.min()}-{nets.max()}")
    N.put("ExcessPairTwelve", num(x2.mean(), 2), "mUSD, Mekong and Tonle Sap at once minus their two singles, same "
          "networks: Saigon adds nothing to the interaction")

    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH["double"], 64 / 25.4), gridspec_kw=dict(width_ratios=[1.25, 1]))
    for d in DURATIONS:
        c = curves[d]
        lags = list(c)
        st = np.array([ci(c[L]) for L in lags])
        col = DUR_COLOR[d]
        a.fill_between(lags, st[:, 1], st[:, 2], color=col, alpha=0.22, lw=0)
        a.plot(lags, st[:, 0], color=col, lw=1.3, marker="o", ms=2.2, label=f"{d}-day closures ({len(W[d])} networks)")
        i = lags.index(d)
        a.plot(d, st[i, 0], marker="o", ms=5.5, mfc="white", mec=col, mew=1.2, zorder=4)
        a.text(lags[-1] + 0.8, st[-1, 0] + 0.004, f"{d} d", color=INK, fontsize=6.5, va="bottom")
    a.plot([], [], marker="o", ms=5.5, mfc="white", mec=INK, mew=1.2, ls="", label="back to back (lag = closure length)")
    a.axhline(1, color=INK, lw=0.6, ls=":")
    a.text(51, 0.995, "additive", ha="right", va="top", fontsize=6.5)
    a.set(xlabel="days between the starts of successive floods", ylabel="loss / sum of the single-basin losses",
          xlim=(-1, 52), ylim=(0.95, None))
    a.legend(loc="upper right", fontsize=6.5)
    panel(a, "a", "Three basins in succession")

    st = np.array([ci(P[t]) for t in taus])
    b.axvspan(-12, 12, color=SHADE, lw=0, zorder=0)
    b.text(0, 0.94, "closures overlap", ha="center", va="bottom", fontsize=6.5, color=INK)
    for s in P.index:
        b.plot(taus, P.loc[s, taus], color=MUTED, lw=0.4, alpha=0.7, zorder=1)
    b.fill_between(taus, st[:, 1], st[:, 2], color=DUR_COLOR[12], alpha=0.22, lw=0, zorder=2)
    b.plot(taus, st[:, 0], color=DUR_COLOR[12], lw=1.4, marker="o", ms=2.2, zorder=3,
           label=f"mean, 95 % interval ({len(P)} networks)")
    b.plot([], [], color=MUTED, lw=0.6, label="each network")
    b.axhline(1, color=INK, lw=0.6, ls=":")
    b.set(xlabel="start of Tonle Sap closure − start of Mekong closure (days)",
          ylabel="loss / sum of the two single-basin losses", ylim=(0.93, None))
    b.annotate("← Tonle Sap first", (0.0, -0.25), xycoords="axes fraction", fontsize=6.5, color=INK, ha="left")
    b.annotate("Mekong first →", (1.0, -0.25), xycoords="axes fraction", fontsize=6.5, color=INK, ha="right")
    b.legend(loc="upper left", fontsize=6.5)
    panel(b, "b", "Two basins, 12-day closures, either order")
    fig.tight_layout(w_pad=1.5)
    return save(fig, out, "fig3_timing")
