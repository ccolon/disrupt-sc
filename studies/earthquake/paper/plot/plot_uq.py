"""Event-study figure: model MMI-bin DiD vs UQ, sales + purchases.

Model DiD(bin, tau) = pct_change(bin) - pct_change(control)   [from uq_eventstudy.csv]
overlaid on UQ's twfe_event_study_coefs.csv (already a bin-vs-control DiD, pct_change).
Solid = model, dashed = UQ; acute window (tau 0,1) shaded.

CLI:
  python plot_uq.py <model uq_eventstudy.csv> --uq <twfe_event_study_coefs.csv> [--fig PATH]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BIN_COLORS = {"bin_56": "#f4a582", "bin_67": "#d6604d", "bin_7p": "#b2182b"}
BIN_LABEL = {"bin_56": "MMI 5-6", "bin_67": "MMI 6-7", "bin_7p": "MMI>7"}
ORDER = ["bin_56", "bin_67", "bin_7p"]


def model_did(es: pd.DataFrame) -> pd.DataFrame:
    out = []
    for outcome, g in es.groupby("outcome"):
        piv = g.pivot_table(index="tau", columns="mmi_bin", values="pct_change")
        if "control" not in piv:
            continue
        for b in ORDER:
            if b in piv:
                d = (piv[b] - piv["control"]).reset_index()
                d.columns = ["tau", "did"]
                d["outcome"], d["bin"] = outcome, b
                out.append(d)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def main():
    ap = argparse.ArgumentParser(description="Model-vs-UQ MMI event-study figure")
    ap.add_argument("eventstudy_csv", type=Path, help="model uq_eventstudy.csv")
    ap.add_argument("--uq", type=Path, required=True, help="twfe_event_study_coefs.csv")
    ap.add_argument("--fig", type=Path, default=None)
    args = ap.parse_args()

    md = model_did(pd.read_csv(args.eventstudy_csv))
    uq = pd.read_csv(args.uq)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), sharex=True)
    for ax, outcome in zip(axes, ["sales", "purchases"]):
        for b in ORDER:
            mm = md[(md.outcome == outcome) & (md.bin == b)].sort_values("tau")
            if len(mm):
                ax.plot(mm.tau, mm.did, "-o", color=BIN_COLORS[b], lw=2, ms=4, label=f"model {BIN_LABEL[b]}")
            uu = uq[(uq.outcome == outcome) & (uq.bin == b)].sort_values("tau")
            if len(uu):
                ax.plot(uu["tau"], uu["pct_change"], "--", color=BIN_COLORS[b], lw=1.6, alpha=0.85,
                        label=f"UQ {BIN_LABEL[b]}")
        ax.axhline(0, color="k", lw=0.6)
        ax.axvspan(-0.5, 1.5, color="grey", alpha=0.12)          # acute window (tau 0,1)
        ax.set_title(outcome)
        ax.set_xlabel("months since shock (tau)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("DiD % change (MMI bin vs control)")
    axes[0].legend(fontsize=7, ncol=2, frameon=False, loc="lower left")
    fig.suptitle("DisruptSC vs UQ — MMI-bin event study (solid = model, dashed = UQ; grey = acute)",
                 fontsize=12)
    fig.tight_layout()
    figpath = args.fig or args.eventstudy_csv.with_name("fig_uq.png")
    fig.savefig(figpath, dpi=140, bbox_inches="tight")
    print(f"-> {figpath}")


if __name__ == "__main__":
    main()
