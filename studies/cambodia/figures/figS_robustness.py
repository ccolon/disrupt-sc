"""SI figure of the Cambodia paper (evidence E_rob): the two-flood result under other inventory targets and restoration
times (10 Nov 2026).

Inputs: rob_d12_20261108 (networks 1-10, d = 12, Mekong + Tonle Sap at tau 0, 12, 24 and the two singles, each variant
with its own singles), base = pair_d12_20261108 + grid_d12_20261108 singles. Variants: inventory targets x0.5 and x2
(every input's target), restoration 15 and 60 days (base: targets as in paper_config.yaml, restoration 30 days).
(a) ratio to the sum of the singles by tau and variant; (b) leftover at tau = 12 (closures back to back) by network,
variant against base.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from paper import INK, INV_COLOR, REST_COLOR, WIDTH, WORD, ci, num, panel, rob_wide, save

TAUS = (0, 12, 24)
VARIANTS = [  # key, label, macro word, colour, marker face, linestyle, x offset
    ("inv0.5", "inventory targets ×0.5", "InvHalf", INV_COLOR, "white", "--", -1.6),
    ("inv2", "inventory targets ×2", "InvTwo", INV_COLOR, None, "-", -0.8),
    ("base", "base (targets ×1, restoration 30 days)", "Base", INK, None, "-", 0.0),
    ("rest15", "restoration 15 days", "RestFifteen", REST_COLOR, "white", "--", 0.8),
    ("rest60", "restoration 60 days", "RestSixty", REST_COLOR, None, "-", 1.6),
]


def make(I, out, N):
    L = rob_wide(I)
    nets = sorted(L.loc["base"].index)
    N.put("RobNets", str(len(nets)), "networks of the robustness runs")
    for v, lab, w, *_ in VARIANTS:
        x = L.loc[v]
        for t in TAUS:
            N.ci(f"RatioRob{w}Tau{WORD[t]}", x[f"R{t}"], 3, f"two floods / sum of the two singles, {lab}, tau = {t}")
        if v != "base":
            d = (x.R12 - L.loc["base"].R12) * 100
            N.put(f"LeftoverDiff{w}", num(d.mean(), 1), f"pp, leftover at tau 12 minus the base's, {lab} (paired)")
            for k, name in (("single_mekong", "Mekong"), ("single_tonle", "Tonle")):
                ds = (x[k] / L.loc["base"][k] - 1) * 100
                N.put(f"SingleChange{w}{name}", num(ds.mean(), 1), f"% change of the single {name} loss, {lab}")
    N.put("LeftoverInvTwoRemovedNets", str(int((L.loc["inv2"].R12 < 1).sum())),
          "networks in which inventory targets x2 leave no leftover at tau 12 (ratio below 1)")

    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH["double"], 66 / 25.4), gridspec_kw=dict(width_ratios=[1.15, 1]))
    for v, lab, w, col, mfc, ls, off in VARIANTS:
        st = np.array([ci(L.loc[v][f"R{t}"]) for t in TAUS])
        a.errorbar(np.array(TAUS) + off, st[:, 0], yerr=[st[:, 0] - st[:, 1], st[:, 2] - st[:, 0]], color=col,
                   marker="o", mfc=mfc or col, mec=col, ms=3.5, lw=1.1 if v == "base" else 0.9, ls=ls, capsize=2,
                   label=lab, zorder=3 if v == "base" else 2)
    a.axhline(1, color=INK, lw=0.6, ls=":")
    a.set(xticks=TAUS, xlabel="days between the two starts (Mekong first)",
          ylabel="loss / sum of the two single-basin losses", ylim=(0.9, None))
    a.legend(loc="upper right", fontsize=6.5)
    panel(a, "a", "Two floods, 12-day closures, by variant")

    base = 100 * (L.loc["base"].R12 - 1)
    for v, lab, w, col, mfc, ls, off in VARIANTS:
        if v == "base":
            continue
        y = 100 * (L.loc[v].R12 - 1)
        b.scatter(base, y.loc[base.index], s=14, color=mfc or col, edgecolors=col, linewidths=0.8, label=lab, zorder=3)
    hi = max(55, float((100 * (L.R12 - 1)).max()) + 3)
    b.plot([-5, hi], [-5, hi], color=INK, lw=0.6, ls=":", label="same as the base")
    b.axhline(0, color=INK, lw=0.6)
    b.set(xlabel="leftover in the base (%)", ylabel="leftover in the variant (%)", xlim=(0, 25), ylim=(-5, hi))
    b.legend(loc="upper left", fontsize=6.5)
    panel(b, "b", "Leftover once the closures stop overlapping, by network")
    fig.tight_layout(w_pad=1.5)
    return save(fig, out, "figS_robustness")
