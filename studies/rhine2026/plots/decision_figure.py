"""F1b: what happens to one shipment in a low-water week (the per-shipment decision diagram, 5 Oct 2026; laid out at
print width on 13 Oct 2026; redrawn 22 Oct 2026 on the author's notes: one loading-curve box that sets both the
surcharge and the capacity, a 'delivered with the surcharge' box and the 'cut share' box on one row feeding the buyer,
containers may switch, most bulk waits (the asterisk is explained in the caption)).

Usage:
    python studies/rhine2026/plots/decision_figure.py [--out studies/rhine2026/figures]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from print_style import finish  # noqa: E402  text at print size (13 Oct 2026)
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parents[1]
INK, MUTED = "#1f2328", "#6e7781"
BLUE, ORANGE, GREEN, GREY = "#2f6fdb", "#e0842a", "#3a9a5b", "#e6e8eb"


def box(ax, x, y, w, h, text, fc="white", ec=INK, fs=7.5, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=fc, edgecolor=ec, linewidth=0.9))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=INK, fontweight="bold" if bold else "normal", linespacing=1.2)


def arrow(ax, x0, y0, x1, y1, text=None, color=INK, tx=0.0, ty=0.0, fs=7, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, color=color, linewidth=0.9,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((x0 + x1) / 2 + tx, (y0 + y1) / 2 + ty, text, fontsize=fs, color=color, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none"))


def main(out: Path):
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 11.5); ax.set_ylim(-0.95, 4.7); ax.axis("off")
    # row 1: the gauge and the loading curve, which sets the surcharge and the capacity
    box(ax, 1.15, 3.85, 2.0, 1.0, "Kaub gauge\nof the week", fc=GREY, ec=MUTED)
    box(ax, 4.5, 3.85, 3.6, 1.0, "loading curve: share of the\nnormal tonnage that passes\n(the surcharge is its inverse)", fc=GREY, ec=MUTED)
    arrow(ax, 2.2, 3.85, 2.65, 3.85)
    # row 2: the shipment
    box(ax, 1.15, 2.3, 2.0, 1.0, "shipment on its\nnormal route", bold=True)
    box(ax, 4.5, 2.3, 2.6, 1.0, "pays the surcharge,\nor takes a cheaper route")
    box(ax, 7.6, 2.3, 2.3, 1.0, "the reach is full:\nshipments cut")
    arrow(ax, 2.2, 2.3, 3.15, 2.3); arrow(ax, 5.85, 2.3, 6.4, 2.3)
    arrow(ax, 4.5, 3.33, 4.5, 2.83, text="surcharge", color=MUTED, tx=0.75)
    arrow(ax, 6.0, 3.35, 7.3, 2.83, text="capacity", color=MUTED, tx=0.45, ty=0.12)
    # row 3: the two outcomes, side by side, both feeding the buyer
    box(ax, 4.5, 0.75, 2.6, 1.0, "delivered,\nwith the surcharge", fc="#e9f4ee", ec=GREEN)
    box(ax, 7.6, 0.72, 2.4, 1.55, "cut share looks for\nanother route:\ncontainers may switch\nto rail or road, most\nbulk* cannot and waits", fs=7)
    arrow(ax, 4.5, 1.78, 4.5, 1.28); arrow(ax, 7.6, 1.78, 7.6, 1.53)
    box(ax, 10.3, 0.75, 2.2, 1.3, "buyer draws on\nits inventory; output\nlost when a critical\ninput runs out", fc="#e9f4ee", ec=GREEN, fs=7)
    arrow(ax, 8.78, 0.75, 9.17, 0.75)
    arrow(ax, 4.5, 0.22, 10.3, 0.07, color=GREEN, rad=0.28)
    ax.text(0.1, 4.6, "(b)", fontsize=10, color=INK, fontweight="bold", va="top")
    finish(fig, 6.3)
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
