"""Fig. 1 of the Cambodia paper (claim S3, evidence E_dir): the direct impacts - the road edges the 2023 flood footprint
closes, by basin, on the network, and what each basin's closure alone costs (9 Nov 2026 draft; paper style 10 Nov).

Inputs:
- <data>/Transport/transport.gpkg: roads (attribute flood_v3: the 36 edges of the paper's v3 footprint, by basin;
  written by studies/cambodia/add_flood_v3.py), waterways, railways;
- <data>/Spatial/households.geojson: household locations and population (the model's final-demand points);
- the grid batch at d = 12 (single-basin runs, 20 networks).
Not yet in it: the CLIMADA depth footprints (on the cluster only; node E_dir stays open for them).

Usage: called by make_figures.py (make), or alone:
    python studies/cambodia/figures/fig1_direct.py --data <disrupt-sc-data>/Cambodia --runs <pipeline>/runs --out <dir>
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from paper import (BASIN_COLOR, BASIN_LABEL, BASIN_WORD, BASINS, INK, INK2, WIDTH, Inputs, Numbers, ci, count,
                   grid_wide, num, panel, save, style)

FLOOD_V3 = {"saigon": "Saigon", "mekong": "Siem Bok (Mekong)", "tonle": "St. Sen (Tonlè Sap)"}
STATION = {"saigon": "Saigon", "mekong": "Mekong (Siem Bok)", "tonle": "Tonle Sap (St. Sen)"}
MAJOR = ("trunk", "primary")
D = 12


def make(I, out, N):
    gpkg = I.path("Transport/transport.gpkg", base="data")
    roads = gpd.read_file(gpkg, layer="roads")
    water = gpd.read_file(gpkg, layer="waterways")
    rail = gpd.read_file(gpkg, layer="railways")
    hh = gpd.read_file(I.path("Spatial/households.geojson", base="data"))
    G = grid_wide(I, D)

    major = roads["class"].astype(str).str.split(", ").apply(lambda c: any(x in MAJOR for x in c))
    closed = roads[roads.flood_v3.notna()]
    assert set(closed.flood_v3) == set(FLOOD_V3.values()), sorted(set(closed.flood_v3))
    N.put("RoadEdges", count(len(roads)), "road edges of the model's network")
    N.put("RoadKm", count(round(roads.km.sum())), "km of road in the model's network")
    N.put("ClosedEdges", str(len(closed)), "road edges closed by the 2023 (v3) footprint, three basins")
    N.put("ClosedKm", count(round(closed.km.sum())), "km of road closed")
    N.put("ClosedKmShare", num(100 * closed.km.sum() / roads.km.sum(), 1), "% of the road km closed")
    km, edges = {}, {}
    for b in BASINS:
        e = closed[closed.flood_v3 == FLOOD_V3[b]]
        km[b], edges[b] = e.km.sum(), len(e)
        N.put(f"Closed{BASIN_WORD[b]}Edges", str(len(e)), f"road edges closed in the {BASIN_LABEL[b]} basin")
        N.put(f"Closed{BASIN_WORD[b]}Km", count(round(e.km.sum())), f"km of road closed in the {BASIN_LABEL[b]} basin")
        N.put(f"Closed{BASIN_WORD[b]}Major", str(int(major[e.index].sum())), "of which trunk or primary edges")
    N.put("HouseholdPoints", count(len(hh)), "household points (final-demand locations) of the model")

    fig = plt.figure(figsize=(WIDTH["double"], 96 / 25.4))
    ax = fig.add_axes([0.0, 0.0, 0.63, 0.93])
    hh.plot(ax=ax, markersize=hh.population / hh.population.max() * 12, color="#c3c2b7", alpha=0.7, linewidth=0,
            zorder=1)
    roads[~major].plot(ax=ax, color="#c3c2b7", linewidth=0.3, zorder=2)
    roads[major].plot(ax=ax, color=INK2, linewidth=0.6, zorder=3)
    water.plot(ax=ax, color="#86b6ef", linewidth=0.8, zorder=2)
    rail.plot(ax=ax, color=INK2, linewidth=0.6, linestyle="--", zorder=3)
    for b in BASINS:
        e = closed[closed.flood_v3 == FLOOD_V3[b]]
        e.plot(ax=ax, color=BASIN_COLOR[b], linewidth=2.2, zorder=5,
               label=f"{STATION[b]}: {edges[b]} edges, {km[b]:.0f} km")
    pp = hh[hh.subregion.astype(str).str[:2] == "12"]
    if len(pp):
        c = pp.geometry.union_all().centroid
        ax.plot(c.x, c.y, marker="*", color=INK, markersize=6, zorder=6)
        ax.annotate("Phnom Penh", (c.x, c.y), xytext=(6, -9), textcoords="offset points", fontsize=6.5)
    x0, y0, x1, y1 = hh.total_bounds          # the country, not the international links that leave it
    ax.set_xlim(x0 - 0.3, x1 + 0.3)
    ax.set_ylim(y0 - 0.3, y1 + 0.3)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.plot([], [], color=INK2, lw=0.6, label="trunk and primary roads")
    ax.plot([], [], color="#86b6ef", lw=0.8, label="waterways")
    ax.plot([], [], color=INK2, lw=0.6, ls="--", label="railways")
    ax.scatter([], [], s=6, color="#c3c2b7", label="households (size: population)")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.0), ncol=2, fontsize=6.5, alignment="left",
              title="road edges closed by the 2023 floods, and the network", title_fontsize=6.5)
    panel(ax, "a", "Roads closed by the 2023 flood footprint, by basin")

    labels = [BASIN_LABEL[b] for b in BASINS]
    cols = [BASIN_COLOR[b] for b in BASINS]
    bx = fig.add_axes([0.71, 0.58, 0.28, 0.32])
    bx.bar(labels, [km[b] for b in BASINS], color=cols, width=0.6)
    for i, b in enumerate(BASINS):
        bx.text(i, km[b] + 6, f"{edges[b]} edges", ha="center", va="bottom", fontsize=6.5)
    bx.set(ylabel="road km closed", ylim=(0, max(km.values()) * 1.2))
    panel(bx, "b", "Closed road km")
    cx = fig.add_axes([0.71, 0.1, 0.28, 0.32])
    st = np.array([ci(G[f"single_{b}"]) for b in BASINS])
    cx.bar(labels, st[:, 0], color=cols, width=0.6)
    cx.errorbar(range(3), st[:, 0], yerr=[st[:, 0] - st[:, 1], st[:, 2] - st[:, 0]], fmt="none", color=INK, lw=0.8,
                capsize=2)
    cx.set(ylabel="household loss (million USD)")
    panel(cx, "c", f"One basin closed for {D} days ({len(G)} networks)")
    return save(fig, out, "fig1_direct")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    style()
    N = Numbers()
    print("figure:", make(Inputs(a.runs, a.data), a.out, N))
    for k, (v, c) in N.M.items():
        print(f"  {k} = {v}  ({c})")
