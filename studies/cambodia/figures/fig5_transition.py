"""Fig. 5 of the Cambodia paper (claim S2, evidence E_trans): compound floods under a carbon tax on transport fuel at the
level the IMF analyses for Cambodia (USD 75/tCO2e in 2035), against the base freight costs (10 Nov 2026).

Inputs: trans_d12_20261109 (networks 1-10, d = 12, singles and pairs at tau 0, 6, 12, 24, taxed per-km costs, builds
that keep the base supplier links), the base runs pair_d12_20261108 + grid_d12_20261108 singles, and
trans_logs/trans_null.csv (the no-flood line-haul freight bill, base and taxed, per network; trans_null.py).
Interaction index I = L(flood | tax) / L(flood | base) - 1, paired by network and scenario, against the null = relative
rise of the network's no-flood freight bill. 95 % intervals, t over networks.
(a) I by scenario with the null; (b) the two-flood ratio at base and taxed costs.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from paper import (INK, MUTED, SHADE, TAX, TRANS, TRANS_NULL, WIDTH, WORD, ci, grid_wide, num, panel, pair_wide,
                   save)

TAUS = (0, 6, 12, 24)
KEYS = ["single_mekong", "single_tonle"] + [f"tau{t}" for t in TAUS]
KEYLAB = {"single_mekong": "Mekong\nalone", "single_tonle": "Tonle Sap\nalone",
          **{f"tau{t}": f"both,\nτ = {t}" for t in TAUS}}
KEYWORD = {"single_mekong": "Mekong", "single_tonle": "Tonle", **{f"tau{t}": f"Tau{WORD[t]}" for t in TAUS}}


def make(I, out, N):
    tr = I.csv(TRANS)
    key = [s if s.startswith("single_") else f"tau{int(t)}" for s, t in zip(tr.scenario, tr.tau)]
    tax = tr.assign(key=key).pivot(index="seed", columns="key", values="loss_households") / 1e6
    nets = tax.index
    Pw, G = pair_wide(I), grid_wide(I, 12)
    base = pd.DataFrame({**{f"tau{t}": Pw.loc[nets, t] for t in TAUS},
                         "single_mekong": G.loc[nets, "single_mekong"], "single_tonle": G.loc[nets, "single_tonle"]})
    Iix = tax[KEYS] / base[KEYS] - 1
    null = I.csv(TRANS_NULL).set_index("seed").rise.loc[nets]
    N.put("TransNets", str(len(nets)), "networks of the transition runs")
    N.ci("TransNull", null, 2, "% rise of the no-flood line-haul freight bill under the tax (upper bound: per-ton fees "
         "unchanged)", scale=100)
    for k in KEYS:
        N.ci(f"TransI{KEYWORD[k]}", Iix[k], 2 if k != "single_mekong" else 3,
             f"% change of the household loss under the tax, {k}", scale=100)
        N.put(f"TransLossBase{KEYWORD[k]}", num(base[k].mean(), 2), f"mUSD, base loss, {k}")
        N.put(f"TransLossTax{KEYWORD[k]}", num(tax[k].mean(), 2), f"mUSD, taxed loss, {k}")
    gapnull = (Iix[KEYS].sub(null, axis=0)) * 100
    N.put("TransBelowNullMin", num(-gapnull.max().max(), 1), "pp: the smallest gap between the null and I, any "
          "scenario and network")
    pos = Iix[[k for k in KEYS if k != "single_mekong"]]
    N.put("TransPositiveNets", f"{int((pos > 0).all(axis=1).sum())}", "networks in which every scenario except the "
          "Mekong closure alone loses more under the tax")
    ch = []
    for t in TAUS:
        rt = tax[f"tau{t}"] / (tax.single_mekong + tax.single_tonle)
        rb = base[f"tau{t}"] / (base.single_mekong + base.single_tonle)
        ch.append((rt - rb).abs().mean())
    N.put("TransRatioChangeMax", num(max(ch), 3), "largest mean absolute change of the two-flood ratio under the tax, "
          "any tau")

    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH["onehalf"], 60 / 25.4), gridspec_kw=dict(width_ratios=[1.3, 1]))
    x = np.arange(len(KEYS))
    m, lo, hi = ci(100 * null)
    a.axhspan(lo, hi, color=SHADE, lw=0, zorder=0)
    a.axhline(m, color=MUTED, lw=1, ls="--", zorder=1)
    a.text(len(KEYS) - 0.5, m + 0.12, "no-flood freight bill", ha="right", va="bottom", fontsize=6.5)
    st = np.array([ci(100 * Iix[k]) for k in KEYS])
    a.errorbar(x, st[:, 0], yerr=[st[:, 0] - st[:, 1], st[:, 2] - st[:, 0]], fmt="o", color=TAX, ms=3.5, capsize=2,
               label="flood loss, paired by network")
    for i, v in enumerate(st[:, 0]):
        a.text(i, max(v, 0) + 0.18, f"{v:+.2f}".replace("-", "−"), ha="center", va="bottom", fontsize=6.5)
    a.axhline(0, color=INK, lw=0.6)
    a.set(xticks=x, xlim=(-0.5, len(KEYS) - 0.5), ylim=(-0.4, 4.6), ylabel="change under the tax (%)")
    a.set_xticklabels([KEYLAB[k] for k in KEYS], fontsize=6.5)
    a.legend(loc="center right", fontsize=6.5)
    panel(a, "a", "Losses under a USD 75/tCO$_2$e tax")

    for lab, df, col, off, mfc in (("base freight costs", base, INK, -0.5, INK),
                                   ("with the tax", tax, TAX, 0.5, "white")):
        r = np.array([ci(df[f"tau{t}"] / (df.single_mekong + df.single_tonle)) for t in TAUS])
        b.errorbar(np.array(TAUS) + off, r[:, 0], yerr=[r[:, 0] - r[:, 1], r[:, 2] - r[:, 0]], color=col, marker="o",
                   mfc=mfc, mec=col, ms=3.5, lw=1, capsize=2, label=lab)
    b.axhline(1, color=INK, lw=0.6, ls=":")
    b.set(xticks=TAUS, xlabel="days between the two starts (Mekong first)",
          ylabel="loss / sum of the two single-basin losses", ylim=(0.95, None))
    b.legend(loc="upper right", fontsize=6.5)
    panel(b, "b", "Two floods, base and taxed")
    fig.tight_layout(w_pad=1.5)
    return save(fig, out, "fig5_transition")
