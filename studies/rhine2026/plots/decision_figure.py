"""Fig. 1b: what happens to a shipment in a low-water week (5 Oct 2026; review F1 note, G6).

A flow diagram of the per-shipment decision under the quantity constraint with the surcharge: surcharge or
cheaper route; the reach's capacity and the pro-rata cut; the alternative search with the modal-switch rule
(containers to rail, bulk back to the yard); the buyer's stock and its production.

Usage:
    python studies/rhine2026/plots/decision_figure.py [--out studies/rhine2026/figures]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parents[1]
INK, MUTED = "#1f2328", "#6e7781"
BLUE, ORANGE, GREEN, GREY = "#2f6fdb", "#e0842a", "#3a9a5b", "#e6e8eb"


def box(ax, x, y, w, h, text, fc="white", ec=INK, fs=8.2, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=fc, edgecolor=ec, linewidth=1.1))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=INK, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, x0, y0, x1, y1, text=None, color=INK, tx=0.0, ty=0.0, fs=7.5):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11, color=color, linewidth=1.1))
    if text:
        ax.text((x0 + x1) / 2 + tx, (y0 + y1) / 2 + ty, text, fontsize=fs, color=color, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none"))


def main(out: Path):
    fig, ax = plt.subplots(figsize=(11, 4.6))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.6); ax.axis("off")
    # row 1: the gauge, the surcharge, the capacity
    box(ax, 1.1, 3.8, 1.9, 0.9, "Kaub gauge\nof the week", fc=GREY, ec=MUTED)
    box(ax, 3.7, 3.8, 2.3, 0.9, "loading table:\nshare of the normal\ntonnage the reach passes", fc=GREY, ec=MUTED)
    box(ax, 6.6, 3.8, 2.2, 0.9, "surcharge on the voyage\n= 1 / that share", fc=GREY, ec=MUTED)
    arrow(ax, 2.05, 3.8, 2.55, 3.8); arrow(ax, 4.85, 3.8, 5.5, 3.8)
    # row 2: the shipment
    box(ax, 1.1, 2.3, 1.9, 0.9, "shipment on its\nnormal route", bold=True)
    box(ax, 3.7, 2.3, 2.3, 0.9, "pays the surcharge, or takes\na cheaper route including\nthe cost of changing mode")
    box(ax, 6.6, 2.3, 2.2, 0.9, "the reach is full:\nshipments cut pro rata\nso that it is exactly full")
    arrow(ax, 2.05, 2.3, 2.55, 2.3); arrow(ax, 4.85, 2.3, 5.5, 2.3)
    arrow(ax, 6.6, 3.35, 6.6, 2.75, color=MUTED)
    arrow(ax, 3.7, 3.35, 3.7, 2.75, color=MUTED)
    # row 3: the cut share
    box(ax, 6.6, 0.85, 2.2, 0.9, "cut share: search for a\nroute that avoids the reach,\nswitching penalty included")
    arrow(ax, 6.6, 1.85, 6.6, 1.3)
    box(ax, 9.4, 1.55, 1.9, 0.75, "containers:\nrail or road", fc="#eaf1fb", ec=BLUE)
    box(ax, 9.4, 0.5, 1.9, 0.75, "bulk: no mode at volume,\nback to the supplier's yard", fc="#fbeee2", ec=ORANGE)
    arrow(ax, 7.7, 1.0, 8.45, 1.45, color=BLUE)
    arrow(ax, 7.7, 0.7, 8.45, 0.55, color=ORANGE)
    # the buyer
    box(ax, 9.4, 3.8, 1.9, 0.9, "buyer: draws on its stock;\nloses output when a\ncritical input runs out", fc="#e9f4ee", ec=GREEN)
    arrow(ax, 7.7, 2.3, 8.45, 3.45, text="delivered\n(at the delivered price)", color=GREEN, tx=-0.2, ty=0.25)
    arrow(ax, 9.4, 1.93, 9.4, 3.35, text="delivered later", color=BLUE, tx=0.75, ty=0.0)
    ax.text(0.15, 4.45, "b", fontsize=11, color=INK, fontweight="bold", va="top")
    fig.tight_layout()
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F1b_decision.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F1b written to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.out))
