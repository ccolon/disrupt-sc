"""Shock-heterogeneity figure: what a fixed loss costs, depending on how it is spread.

Replaces the earlier seven-panel treatment (five loss-over-time panels plus a
separate mean / coefficient-of-variation pair) with two panels:

  (a) household loss at the final horizon, every draw shown, one column per
      resolution, against the homogeneous reference. Level, spread and the gap
      to a uniform national assumption are all readable at once.
  (b) the median trajectory per resolution over the reported horizons, which is
      where the widening of that gap over time becomes visible.

Resolutions are grouped into three families -- sectoral, spatial, crossed --
separated by rules, because they are not a single nested granularity scale:
sector and province are not nested, so a monotone axis would misrepresent them.

Reads hetero_all.csv (run_hetero.py / combine_hetero.py). Seeds are averaged
within a draw before anything is plotted, so the spread shown is draw-to-draw
heterogeneity rather than network noise.

CLI: python plot_hetero.py <hetero_all.csv> [--fig-dir DIR] [--metric household]
     [--earthquake-loss 2.60]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# display order, with the family each column belongs to
ORDER = [
    ("homogeneous", "reference"),
    ("sector", "sectoral"),
    ("province", "spatial"),
    ("canton", "spatial"),
    ("province_sector", "crossed"),
    ("canton_sector", "crossed"),
]
LABEL = {"homogeneous": "homogeneous", "sector": "sector", "province": "province",
         "canton": "canton", "province_sector": "province\n× sector",
         "canton_sector": "canton\n× sector"}
# Family identity is carried by hue and by the rules between column groups; the two
# members of a family differ in lightness, since panel (b) draws all six as lines and
# one hue per family would leave province indistinguishable from canton.
COLOR = {"homogeneous": "#6b7280", "sector": "#b45309",
         "province": "#60a5fa", "canton": "#1d4ed8",
         "province_sector": "#c084fc", "canton_sector": "#7e22ce"}


def horizons(df: pd.DataFrame, metric: str) -> list[int]:
    hs = []
    for c in df.columns:
        if c.startswith(f"{metric}_loss_pct_gdp_") and c.endswith("m"):
            try:
                hs.append(int(c.rsplit("_", 1)[-1][:-1]))
            except ValueError:
                pass
    return sorted(hs)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path)
    ap.add_argument("--metric", default="household",
                    help="household | government | investment | va")
    ap.add_argument("--fig-dir", type=Path, default=None)
    ap.add_argument("--fig", type=Path, default=None)
    ap.add_argument("--earthquake-loss", type=float, default=None,
                    help="household loss (%% of GDP) of the actual 2016 event; drawn as a "
                         "marker at the canton x sector column to locate the case study "
                         "on the same axis")
    args = ap.parse_args()

    raw = pd.read_csv(args.csv)
    hs = horizons(raw, args.metric)
    if not hs:
        raise SystemExit(f"no {args.metric}_loss_pct_gdp_*m columns in {args.csv}")
    final = hs[-1]
    ycol = f"{args.metric}_loss_pct_gdp_{final}m"

    # average seeds within a draw: the spread we plot is across draws, not networks
    per_draw = raw.groupby(["resolution", "draw_id"], as_index=False).mean(numeric_only=True)
    n_seeds = raw.seed.nunique()

    present = [(r, fam) for r, fam in ORDER if (per_draw.resolution == r).any()]
    if not present:
        raise SystemExit("no known resolutions in the input")
    ref = per_draw[per_draw.resolution == "homogeneous"][ycol]
    ref_val = float(ref.mean()) if len(ref) else None

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.5, 5.2),
                                   gridspec_kw={"width_ratios": [1.55, 1]})

    # ---------------- (a) distribution across draws, by resolution -------------
    rng = np.random.default_rng(0)          # jitter only; not part of the result
    xticks, xlabels = [], []
    for i, (res, fam) in enumerate(present):
        vals = per_draw.loc[per_draw.resolution == res, ycol].dropna().values
        if not len(vals):
            continue
        color = COLOR[res]
        if len(vals) > 2:
            axL.boxplot([vals], positions=[i], widths=0.55, showfliers=False,
                        medianprops=dict(color=color, lw=2),
                        boxprops=dict(color=color, lw=1.2),
                        whiskerprops=dict(color=color, lw=1.0),
                        capprops=dict(color=color, lw=1.0))
        axL.scatter(i + rng.uniform(-0.16, 0.16, len(vals)), vals, s=16, alpha=0.55,
                    color=color, edgecolors="none", zorder=3)
        xticks.append(i)
        xlabels.append(f"{LABEL.get(res, res)}\n(n={len(vals)})")

    if ref_val is not None:
        axL.axhline(ref_val, color=COLOR["homogeneous"], ls="--", lw=1.3, zorder=1)
        axL.annotate("homogeneous reference", xy=(len(present) - 0.45, ref_val),
                     xytext=(0, 5), textcoords="offset points", ha="right", va="bottom",
                     fontsize=9, color=COLOR["homogeneous"])

    # family separators: these are three families, not one nested scale
    for i in range(1, len(present)):
        if present[i][1] != present[i - 1][1]:
            axL.axvline(i - 0.5, color="0.85", lw=1.0, zorder=0)

    if args.earthquake_loss is not None:
        xi = next((i for i, (r, _) in enumerate(present) if r == "canton_sector"),
                  len(present) - 1)
        axL.scatter([xi], [args.earthquake_loss], marker="*", s=340, color="#dc2626",
                    edgecolors="white", linewidths=0.8, zorder=5,
                    label="2016 earthquake (actual shock)")
        axL.legend(loc="upper left", frameon=False, fontsize=9)

    axL.set_xticks(xticks)
    axL.set_xticklabels(xlabels, fontsize=9)
    axL.set_ylabel(f"{args.metric} loss, % of annual GDP (at {final} months)")
    axL.set_title("(a) Same destroyed capital, distributed differently", loc="left", fontsize=11)
    axL.grid(axis="y", ls=":", color="0.85")
    axL.set_axisbelow(True)
    for s in ("top", "right"):
        axL.spines[s].set_visible(False)

    # ---------------- (b) median trajectory per resolution ---------------------
    for res, fam in present:
        sub = per_draw[per_draw.resolution == res]
        ys = [sub[f"{args.metric}_loss_pct_gdp_{h}m"].median() for h in hs]
        axR.plot(hs, ys, marker="o", ms=4.5, lw=1.8, color=COLOR[res],
                 ls="--" if res == "homogeneous" else "-",
                 label=LABEL.get(res, res).replace("\n", " "))
    axR.set_xticks(hs)
    axR.set_xlabel("months after the shock")
    axR.set_ylabel(f"median {args.metric} loss, % of annual GDP")
    axR.set_title("(b) The gap widens with time", loc="left", fontsize=11)
    axR.grid(ls=":", color="0.85")
    axR.set_axisbelow(True)
    axR.legend(frameon=False, fontsize=9)
    for s in ("top", "right"):
        axR.spines[s].set_visible(False)

    fig.suptitle(f"Indirect cost of a fixed {'' if ref_val is None else ''}capital loss, "
                 f"by the resolution at which it is concentrated "
                 f"({n_seeds} network seed{'s' if n_seeds > 1 else ''}, averaged per draw)",
                 fontsize=12, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    out = args.fig or ((args.fig_dir or args.csv.parent) / "fig_hetero.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(f"wrote {out}")

    # a compact text version of panel (a), useful in logs and for the paper text
    print(f"\n{args.metric} loss at {final} months, % of annual GDP:")
    for res, _ in present:
        v = per_draw.loc[per_draw.resolution == res, ycol].dropna()
        if not len(v):
            continue
        cv = float(v.std(ddof=1) / v.mean()) if len(v) > 1 and v.mean() else float("nan")
        print(f"  {res:<16} n={len(v):>3}  median {v.median():6.3f}  mean {v.mean():6.3f}  CV {cv:5.2f}")


if __name__ == "__main__":
    main()
