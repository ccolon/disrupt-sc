"""Panel (b) of the 'who loses' figure (Fig. 3): cumulated German value-added loss of the 2026 event by sector
(gross and net) and the loss by country (30 Sep 2026; review G6, F5 note).

Usage:
    python studies/rhine2026/plots/who_loses_panel.py [--run C:/dsc_runs/rhine2026/2026_s07_base] [--out studies/rhine2026/figures]
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

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from va_shares import add_va_share  # noqa: E402  country-sector value-added ratios (12 Oct 2026, review E1)

HERE = Path(__file__).resolve().parents[1]
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
BLUE, ORANGE, GREEN = "#2f6fdb", "#e0842a", "#3a9a5b"
DEFERRABLE = ("A", "B", "C", "F")
NAMES = {"F": "construction", "H52": "warehousing and logistics", "H49": "land transport", "D": "electricity and gas", "C20": "chemicals",
         "I": "hospitality", "H50": "water transport", "C19": "refined petroleum", "C23": "cement, glass, ceramics", "A01": "farming",
         "H51": "air transport", "C10T12": "food", "C24A": "basic iron and steel", "G": "trade", "L": "real estate", "C22": "rubber and plastics"}


def main(run: Path, out: Path):
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm").production
    fd["base"] = fd.firm.map(b0)
    add_va_share(fd, run, "vs")              # the firm's own country-sector ratio (12 Oct 2026)
    fd["short"] = (fd.base - fd.production) * fd.vs                      # signed
    fd["gross"] = fd["short"].clip(lower=0)
    de = fd[fd.region == "DEU"]
    gross = de.groupby("sector").gross.sum().sort_values(ascending=False)
    # net: backlog left at the end for the deferrable sectors (signed shortfalls accumulate, floored at zero per firm)
    net = {}
    for sec, g in de.groupby("sector"):
        if sec[:1] in DEFERRABLE:
            tot = 0.0
            for _, f in g.groupby("firm"):
                b = 0.0
                for v in f.sort_values("time_step").short:
                    b = max(0.0, b + v)
                tot += b
            net[sec] = tot
        else:
            net[sec] = gross[sec]
    top = gross.head(10)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), gridspec_kw={"width_ratios": [1, 1]})
    fig.patch.set_facecolor("white")
    for ax in axes:
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=8); ax.grid(axis="x", color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax = axes[1]
    ys = np.arange(len(top))[::-1]
    # two classifications kept apart (6 Oct 2026, review G3): the NACE group in the label, the catch-up convention in the colour
    GROUP = {"A": "agriculture", "F": "construction"}
    def group(s: str) -> str:
        c = s[:1]
        return GROUP.get(c, "industry" if c in "BCDE" else "services")
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    ax.barh(ys, top.values / 1e3, color=[ORANGE if s[:1] in DEFERRABLE else BLUE for s in top.index], height=0.6)
    ax.scatter([net[s] / 1e3 for s in top.index], ys, color=INK, s=16, zorder=3)
    ax.set_yticks(ys); ax.set_yticklabels([NAMES.get(s, s) for s in top.index], fontsize=7.5)
    ax.set_xlabel("German loss, billion USD", color=MUTED, fontsize=8)
    ax.legend([Patch(color=ORANGE), Patch(color=BLUE), Line2D([], [], marker="o", color=INK, linestyle="none", markersize=4)],
              ["gross, can catch up", "gross, cannot catch up", "net of the backlog worked off"], frameon=False, fontsize=7, loc="lower right")
    ax.set_title("(c) German loss by sector", loc="left", fontsize=9.5, color=INK)
    ax = axes[0]
    cty = fd.groupby("region").gross.sum().sort_values(ascending=False).head(8)
    ys = np.arange(len(cty))[::-1]
    ax.scatter(cty.values / 1e3, ys, color=GREEN, s=36, zorder=3)
    ax.set_yticks(ys); ax.set_yticklabels(list(cty.index), fontsize=8)
    ax.set_xscale("log"); ax.set_xlim(0.02, cty.max() / 1e3 * 3)
    ax.set_xlabel("value-added loss, billion USD (log scale)", color=MUTED, fontsize=8)
    ax.set_title("(b) Loss by country", loc="left", fontsize=9.5, color=INK)
    finish(fig)
    fig.tight_layout(w_pad=2.0)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F5b_sectors_countries.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    print(f"F5b written to {out}: gross {gross.sum():,.0f} mUSD, net {sum(net.values()):,.0f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="C:/dsc_runs/rhine2026/2026_s07_base")
    ap.add_argument("--out", default=str(HERE / "figures"))
    a = ap.parse_args()
    main(Path(a.run), Path(a.out))
