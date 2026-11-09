"""Fig. 1 of the Cambodia paper (node E_dir, claim S3): the direct impacts - the road edges the 2023 flood footprint
closes, by basin, on the network, and what each basin's closure alone costs (9 Nov 2026, draft).

Inputs:
- <data>/Transport/transport.gpkg: roads (attribute flood_v3: the 36 edges of the paper's v3 footprint, by basin;
  written by studies/cambodia/add_flood_v3.py), waterways, railways;
- <data>/Spatial/households.geojson: household locations and population (the model's final-demand points);
- --runs: a grid runs table (read_batch.py analysis/runs.csv) with the single-basin runs at d = 12.
Prints the numbers it draws (for the paper's macros) and writes fig1_direct.png and .pdf to --out.

Usage: python studies/cambodia/figures/fig1_direct.py --data <disrupt-sc-data>/Cambodia
           --runs <grid_d12 runs.csv> --out <folder>
"""
import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASINS = [  # flood_v3 value, scenario, label, colour
    ("Saigon", "single_saigon", "Saigon", "#1b9e77"),
    ("Siem Bok (Mekong)", "single_mekong", "Mekong (Siem Bok)", "#d95f02"),
    ("St. Sen (Tonlè Sap)", "single_tonle", "Tonle Sap (St. Sen)", "#7570b3"),
]
MAJOR = ("trunk", "primary")


def ci(x):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--d", type=int, default=12)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    gpkg = a.data / "Transport" / "transport.gpkg"
    roads = gpd.read_file(gpkg, layer="roads")
    water = gpd.read_file(gpkg, layer="waterways")
    rail = gpd.read_file(gpkg, layer="railways")
    hh = gpd.read_file(a.data / "Spatial" / "households.geojson")
    runs = pd.read_csv(a.runs)
    runs = runs[runs.duration == a.d]

    major = roads["class"].astype(str).str.split(", ").apply(lambda c: any(x in MAJOR for x in c))
    closed = roads[roads.flood_v3.notna()]
    print(f"== Road network: {len(roads)} edges, {roads.km.sum():.0f} km; closed by the v3 footprint: {len(closed)} edges, "
          f"{closed.km.sum():.1f} km ({100 * closed.km.sum() / roads.km.sum():.1f} % of the road km)")
    rows = []
    for v, sc, lab, _ in BASINS:
        e = closed[closed.flood_v3 == v]
        x = runs[runs.scenario == sc].loss_households / 1e6
        m, h = ci(x)
        rows.append(dict(basin=lab, edges=len(e), km=e.km.sum(), major_edges=int(major[e.index].sum()),
                         loss=m, loss_ci=h, networks=len(x)))
        print(f"  {lab}: {len(e)} edges ({int(major[e.index].sum())} trunk or primary), {e.km.sum():.1f} km; "
              f"single closure for {a.d} days: household loss {m:.2f} +/- {h:.2f} mUSD (95 %, {len(x)} networks)")
    T = pd.DataFrame(rows)
    print(f"  households: {len(hh)} points, population {hh.population.sum():,.0f}")

    fig = plt.figure(figsize=(13, 6.2))
    ax = fig.add_axes([0.02, 0.05, 0.6, 0.9])
    hh.plot(ax=ax, markersize=hh.population / hh.population.max() * 25, color="0.75", alpha=0.6, linewidth=0,
            zorder=1)
    roads[~major].plot(ax=ax, color="0.65", linewidth=0.4, zorder=2)
    roads[major].plot(ax=ax, color="0.35", linewidth=0.9, zorder=3)
    water.plot(ax=ax, color="#4a90c2", linewidth=1.0, zorder=2)
    rail.plot(ax=ax, color="0.2", linewidth=0.8, linestyle="--", zorder=3)
    for v, _, lab, col in BASINS:
        e = closed[closed.flood_v3 == v]
        e.plot(ax=ax, color=col, linewidth=3.0, zorder=5, label=f"{lab}: {len(e)} edges, {e.km.sum():.0f} km")
    pp = hh[hh.subregion.astype(str).str[:2] == "12"]
    if len(pp):
        c = pp.geometry.union_all().centroid
        ax.annotate("Phnom Penh", (c.x, c.y), xytext=(8, -12), textcoords="offset points", fontsize=9)
        ax.plot(c.x, c.y, marker="*", color="k", markersize=9, zorder=6)
    x0, y0, x1, y1 = hh.total_bounds          # the country, not the international links that leave it
    ax.set_xlim(x0 - 0.3, x1 + 0.3)
    ax.set_ylim(y0 - 0.3, y1 + 0.3)
    ax.set_axis_off()
    ax.set_title("a. Roads closed by the 2023 flood footprint, by basin", loc="left", fontsize=11)
    ax.legend(loc="upper left", fontsize=9, frameon=False,
              title="closed road edges (grey lines: roads; dots: households)", title_fontsize=8)

    bx = fig.add_axes([0.68, 0.58, 0.29, 0.33])
    cols = [b[3] for b in BASINS]
    bx.bar(T.basin, T.km, color=cols)
    for i, r in T.iterrows():
        bx.text(i, r.km, f"{r.edges} edges", ha="center", va="bottom", fontsize=8)
    bx.set(ylabel="road km closed", title="b. Closed road km")
    bx.tick_params(axis="x", labelsize=8)
    cx = fig.add_axes([0.68, 0.1, 0.29, 0.33])
    cx.bar(T.basin, T.loss, yerr=T.loss_ci, color=cols, capsize=3)
    cx.set(ylabel="household loss (mUSD)", title=f"c. One basin closed for {a.d} days")
    cx.tick_params(axis="x", labelsize=8)
    for ext in ("png", "pdf"):
        fig.savefig(a.out / f"fig1_direct.{ext}", dpi=200)
    print("figure:", a.out / "fig1_direct.png")


if __name__ == "__main__":
    main()
