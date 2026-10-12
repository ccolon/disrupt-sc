"""F1b: what happens to one shipment in a low-water week (the per-shipment decision diagram, 5 Oct 2026; laid out at
print width on 13 Oct 2026).

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


def arrow(ax, x0, y0, x1, y1, text=None, color=INK, tx=0.0, ty=0.0, fs=7):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, color=color, linewidth=0.9))
    if text:
        ax.text((x0 + x1) / 2 + tx, (y0 + y1) / 2 + ty, text, fontsize=fs, color=color, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none"))


def main(out: Path):
    fig, ax = plt.subplots(figsize=(6.3, 3.0))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 11.2); ax.set_ylim(-0.1, 4.7); ax.axis("off")
    # row 1: the gauge, the loading curve, the surcharge
    box(ax, 1.15, 3.85, 2.0, 1.0, "Kaub gauge\nof the week", fc=GREY, ec=MUTED)
    box(ax, 3.9, 3.85, 2.6, 1.0, "loading curve:\nshare of the normal\ntonnage that passes", fc=GREY, ec=MUTED)
    box(ax, 6.85, 3.85, 2.5, 1.0, "voyage surcharge\n= 1 / that share", fc=GREY, ec=MUTED)
    arrow(ax, 2.2, 3.85, 2.55, 3.85); arrow(ax, 5.25, 3.85, 5.55, 3.85)
    # row 2: the shipment
    box(ax, 1.15, 2.3, 2.0, 1.0, "shipment on its\nnormal route", bold=True)
    box(ax, 3.9, 2.3, 2.6, 1.0, "pays the surcharge,\nor takes a cheaper route\n(mode change costed)")
    box(ax, 6.85, 2.3, 2.5, 1.0, "the reach is full:\nshipments cut\nin proportion")
    arrow(ax, 2.2, 2.3, 2.55, 2.3); arrow(ax, 5.25, 2.3, 5.55, 2.3)
    arrow(ax, 6.85, 3.33, 6.85, 2.83, color=MUTED)
    arrow(ax, 3.9, 3.33, 3.9, 2.83, color=MUTED)
    # row 3: the cut share
    box(ax, 6.85, 0.8, 2.5, 1.0, "cut share looks for\na route around the reach\n(switching penalty)")
    arrow(ax, 6.85, 1.78, 6.85, 1.33)
    box(ax, 9.75, 1.5, 2.3, 0.8, "containers:\nrail or road", fc="#eaf1fb", ec=BLUE)
    box(ax, 9.75, 0.45, 2.3, 0.8, "bulk: no alternative,\nback to the supplier", fc="#fbeee2", ec=ORANGE)
    arrow(ax, 8.12, 1.0, 8.58, 1.4, color=BLUE)
    arrow(ax, 8.12, 0.65, 8.58, 0.5, color=ORANGE)
    # the buyer
    box(ax, 9.75, 3.85, 2.3, 1.0, "buyer draws on its stock;\nloses output when a\ncritical input runs out", fc="#e9f4ee", ec=GREEN)
    arrow(ax, 8.12, 2.3, 8.58, 3.45, text="delivered\n(at the new price)", color=GREEN, tx=-0.15, ty=0.3)
    arrow(ax, 9.75, 1.92, 9.75, 3.33, text="delivered later", color=BLUE, tx=0.82, ty=0.0)
    ax.text(0.1, 4.6, "b", fontsize=10, color=INK, fontweight="bold", va="top")
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
