"""Fig. 1 of the Cambodia paper (claim S3, evidence E_dir): the direct impacts - the flood depth of the 2023 footprint,
the road edges it closes, by basin, on the network, and what each basin's closure alone costs (9 Nov 2026 draft; paper
style 10 Nov; depth added 10 Nov).

Inputs:
- <data>/Transport/transport.gpkg: roads (attribute flood_v3: the 36 edges of the paper's v3 footprint, by basin;
  written by studies/cambodia/add_flood_v3.py), waterways, railways;
- <data>/Hazard/glofas_fc20230927_depth.npz: the footprint's water depth (CLIMADA, GloFAS forecast of 27 Sep 2023;
  extracted by studies/cambodia/climada_depth.py; provenance in the README next to it);
- <data>/Spatial/cambodia_outline.geojson: the country's outline (Natural Earth), drawn, and used to leave out the
  depth of the neighbouring countries that the grid's box takes in;
- <data>/Spatial/households.geojson: household locations and population (the model's final-demand points);
- the grid batch at d = 12 (single-basin runs, 20 networks).

The depth is sampled along each road edge as the footprint's impact step did (points 500 m apart, the JRC Asia road
depth-damage curve, damaged at 50 % or more, i.e. 1.28 m of water or more): it gives how much of each closed edge lies
under damaging water, and checks the footprint against its hazard.

Usage: called by make_figures.py (make), or alone:
    python studies/cambodia/figures/fig1_direct.py --data <disrupt-sc-data>/Cambodia --runs <pipeline>/runs --out <dir>
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from pyproj import Transformer

from paper import (BASIN_COLOR, BASIN_LABEL, BASIN_WORD, BASINS, INK, INK2, MUTED, WIDTH, Inputs, Numbers, ci, count,
                   grid_wide, num, panel, save, style)

FLOOD_V3 = {"saigon": "Saigon", "mekong": "Siem Bok (Mekong)", "tonle": "St. Sen (Tonlè Sap)"}
STATION = {"saigon": "Saigon", "mekong": "Mekong (Siem Bok)", "tonle": "Tonle Sap (St. Sen)"}
MAJOR = ("trunk", "primary")
D = 12
DEPTH = "Hazard/glofas_fc20230927_depth.npz"
# JRC Asia road depth-damage curve of the footprint's impact step (climada-disruptsc/functions.py, ImpFuncsRiverFlood)
DMG_X = np.array([0, 0.5, 1, 1.5, 2, 3, 4, 5, 30.])
DMG_Y = np.array([0, 0.21, 0.37, 0.60, 0.71, 0.81, 0.89, 0.97, 1.0])
DEEP = float(np.interp(0.5, DMG_Y, DMG_X))     # 50 % damage: 1.28 m
DEPTH_BINS = (0.5, DEEP)
# light tints of the reference violet: water, kept apart from the basins' hues and the waterways' blue
DEPTH_COLOR = ("#e0dcf7", "#bfb8ef", "#9a8ee4")
UTM = 32648                                    # UTM 48N: metres for Cambodia


OUTLINE = "Spatial/cambodia_outline.geojson"  # Natural Earth admin-0 (public domain); the hazard has no country mask


def load_depth(p: Path):
    z = np.load(p)
    return z["depth"], float(z["lon0"]), float(z["lat0"]), float(z["dx"]), float(z["dy"])


def sample_depth(roads: gpd.GeoDataFrame, grid, lon0, lat0, dx, dy, step=500.0) -> pd.DataFrame:
    """Depth at points `step` m apart along each edge, both ends included (the footprint's impact step): the edge's
    deepest point, its largest damage, its km under damaging depth and under any water, its length in UTM 48N."""
    g = roads.to_crs(UTM).geometry.to_numpy()
    L = shapely.length(g)
    npt = np.maximum(np.ceil(L / step).astype(int), 1) + 1
    edge = np.repeat(np.arange(len(g)), npt)
    frac = np.concatenate([np.linspace(0, 1, k) for k in npt])
    pts = shapely.line_interpolate_point(g[edge], frac, normalized=True)
    x, y = Transformer.from_crs(UTM, 4326, always_xy=True).transform(shapely.get_x(pts), shapely.get_y(pts))
    ny, nx = grid.shape
    j, i = np.rint((x - lon0) / dx).astype(int), np.rint((lat0 - y) / dy).astype(int)
    ok = (i >= 0) & (i < ny) & (j >= 0) & (j < nx)
    d = np.zeros(edge.size)
    d[ok] = grid[i[ok], j[ok]]
    dmg = np.interp(d, DMG_X, DMG_Y)
    seg = (L / 1000 / npt)[edge]
    s = pd.DataFrame({"edge": edge, "d": d, "dmg": dmg, "deep": (dmg >= 0.5) * seg, "wet": (d > 0) * seg})
    a = s.groupby("edge").agg(depth_max=("d", "max"), dmg_max=("dmg", "max"), km_deep=("deep", "sum"),
                              km_wet=("wet", "sum"))
    a["km_geom"] = L / 1000
    a.index = roads.index
    return a


def tint(hex_color: str, t: float) -> str:
    """The colour mixed with white, t of the colour kept."""
    c = np.array([int(hex_color[k:k + 2], 16) for k in (1, 3, 5)])
    return "#" + "".join(f"{int(round(255 - t * (255 - v))):02x}" for v in c)


def make(I, out, N):
    gpkg = I.path("Transport/transport.gpkg", base="data")
    roads = gpd.read_file(gpkg, layer="roads")
    water = gpd.read_file(gpkg, layer="waterways")
    rail = gpd.read_file(gpkg, layer="railways")
    hh = gpd.read_file(I.path("Spatial/households.geojson", base="data"))
    grid, lon0, lat0, dx, dy = load_depth(I.path(DEPTH, base="data"))
    khm = gpd.read_file(I.path(OUTLINE, base="data"))
    G = grid_wide(I, D)

    major = roads["class"].astype(str).str.split(", ").apply(lambda c: any(x in MAJOR for x in c))
    closed = roads[roads.flood_v3.notna()]
    assert set(closed.flood_v3) == set(FLOOD_V3.values()), sorted(set(closed.flood_v3))
    S = sample_depth(roads, grid, lon0, lat0, dx, dy)
    # lengths in the model's km attribute: each edge's sampled shares applied to it
    deep_km = S.km_deep / S.km_geom * roads.km
    wet_km = S.km_wet / S.km_geom * roads.km
    hit = roads.flood_v3.notna()
    dam = S.dmg_max >= 0.5

    N.put("RoadEdges", count(len(roads)), "road edges of the model's network")
    N.put("RoadKm", count(round(roads.km.sum())), "km of road in the model's network")
    N.put("ClosedEdges", str(len(closed)), "road edges closed by the 2023 (v3) footprint, three basins")
    N.put("ClosedKm", count(round(closed.km.sum())), "km of road closed")
    N.put("ClosedKmShare", num(100 * closed.km.sum() / roads.km.sum(), 1), "% of the road km closed")
    N.put("DepthClose", num(DEEP, 2), "m of water at which the JRC Asia road curve reaches 50 % damage (edge closed)")
    N.put("ClosedKmDeep", count(round(deep_km[hit].sum())), "km of the closed edges under DepthClose m of water or more")
    N.put("ClosedKmDeepShare", num(100 * deep_km[hit].sum() / closed.km.sum(), 0),
          "% of the closed km under DepthClose m of water or more")
    N.put("ClosedKmWet", count(round(wet_km[hit].sum())), "km of the closed edges under any water")
    N.put("FootprintRederived", str(int((hit & dam).sum())),
          "of the closed edges reach 50 % damage when the depth grid is sampled every 500 m")
    N.put("FootprintExtra", str(int((dam & ~hit).sum())), "edges reaching 50 % damage that the footprint leaves open")
    N.put("FootprintExtraKm", count(round(roads.km[dam & ~hit].sum())), "km of those edges")
    km, edges, deep = {}, {}, {}
    for b in BASINS:
        e = closed[closed.flood_v3 == FLOOD_V3[b]]
        km[b], edges[b], deep[b] = e.km.sum(), len(e), deep_km[e.index].sum()
        N.put(f"Closed{BASIN_WORD[b]}Edges", str(len(e)), f"road edges closed in the {BASIN_LABEL[b]} basin")
        N.put(f"Closed{BASIN_WORD[b]}Km", count(round(e.km.sum())), f"km of road closed in the {BASIN_LABEL[b]} basin")
        N.put(f"Closed{BASIN_WORD[b]}Major", str(int(major[e.index].sum())), "of which trunk or primary edges")
        N.put(f"Closed{BASIN_WORD[b]}KmDeep", count(round(deep[b])),
              f"km of the closed edges of the {BASIN_LABEL[b]} basin under DepthClose m of water or more")
    N.put("HouseholdPoints", count(len(hh)), "household points (final-demand locations) of the model")

    fig = plt.figure(figsize=(WIDTH["double"], 96 / 25.4))
    ax = fig.add_axes([0.0, 0.0, 0.63, 0.93])
    ny, nx = grid.shape
    # drawn in Cambodia only (the grid's box reaches into the neighbours: cells whose centre is outside the outline are
    # left out); the sampling above uses the whole grid, as the footprint did
    jj, ii = np.meshgrid(np.arange(nx), np.arange(ny))
    inside = shapely.contains_xy(khm.geometry.union_all(), lon0 + jj * dx, lat0 - ii * dy)
    cls = np.ma.masked_where((grid <= 0) | ~inside, np.digitize(grid, DEPTH_BINS) + 1)
    ax.imshow(cls, cmap=ListedColormap(DEPTH_COLOR), vmin=0.5, vmax=3.5, interpolation="nearest", origin="upper",
              extent=(lon0 - dx / 2, lon0 + (nx - 0.5) * dx, lat0 - (ny - 0.5) * dy, lat0 + dy / 2), zorder=0.5)
    khm.boundary.plot(ax=ax, color=MUTED, linewidth=0.5, zorder=0.6)
    N.put("DepthWetCellsOutside", count(int(((grid > 0) & ~inside).sum())),
          "wet cells of the depth grid outside Cambodia (not drawn)")
    hh.plot(ax=ax, markersize=hh.population / hh.population.max() * 12, color="#c3c2b7", alpha=0.7, linewidth=0,
            zorder=1)
    roads[~major].plot(ax=ax, color="#c3c2b7", linewidth=0.3, zorder=2)
    roads[major].plot(ax=ax, color=INK2, linewidth=0.6, zorder=3)
    water.plot(ax=ax, color="#86b6ef", linewidth=0.8, zorder=2)
    rail.plot(ax=ax, color=INK2, linewidth=0.6, linestyle="--", zorder=3)
    for b in BASINS:
        e = closed[closed.flood_v3 == FLOOD_V3[b]]
        e.plot(ax=ax, color="white", linewidth=3.4, zorder=4.9)
        e.plot(ax=ax, color=BASIN_COLOR[b], linewidth=2.2, zorder=5,
               label=f"{STATION[b]}: {edges[b]} edges, {km[b]:.0f} km")
    pp = hh[hh.subregion.astype(str).str[:2] == "12"]
    if len(pp):
        c = pp.geometry.union_all().centroid
        ax.plot(c.x, c.y, marker="*", color=INK, markersize=6, zorder=6)
        ax.annotate("Phnom Penh", (c.x, c.y), xytext=(-6, -4), textcoords="offset points", fontsize=6.5, ha="right",
                    va="top")
    x0, y0, x1, y1 = hh.total_bounds          # the country, not the international links that leave it
    ax.set_xlim(x0 - 0.3, x1 + 0.3)
    ax.set_ylim(y0 - 0.3, y1 + 0.3)
    ax.set_aspect("equal")
    ax.set_axis_off()
    # two legends below the map; the taller one is the axes' own legend, so the saved bounding box takes it in
    net = [plt.Line2D([], [], color=INK2, lw=0.6), plt.Line2D([], [], color="#86b6ef", lw=0.8),
           plt.Line2D([], [], color=INK2, lw=0.6, ls="--"),
           plt.Line2D([], [], ls="none", marker="o", markersize=2.5, color="#c3c2b7")]
    ax.add_artist(ax.legend(net, ["trunk and primary roads", "waterways", "railways", "households (size: population)"],
                            loc="upper left", bbox_to_anchor=(0.62, 0.0), fontsize=6.5, alignment="left",
                            title="the network", title_fontsize=6.5))
    h, l = ax.get_legend_handles_labels()
    h += [Patch(facecolor=c, edgecolor="none") for c in DEPTH_COLOR]
    l += ["water depth under 0.5 m", f"0.5–{DEEP:.2f} m", f"{DEEP:.2f} m or more (road damage 50 % or more)"]
    ax.legend(h, l, loc="upper left", bbox_to_anchor=(0.0, 0.0), fontsize=6.5, alignment="left",
              title="closed edges, and the depth forecast of 27 Sep 2023", title_fontsize=6.5)
    panel(ax, "a", "Flood depth and the roads it closes, by basin")

    labels = [BASIN_LABEL[b] for b in BASINS]
    cols = [BASIN_COLOR[b] for b in BASINS]
    bx = fig.add_axes([0.71, 0.58, 0.28, 0.32])
    bx.bar(labels, [deep[b] for b in BASINS], color=cols, width=0.6)
    bx.bar(labels, [km[b] - deep[b] for b in BASINS], bottom=[deep[b] for b in BASINS],
           color=[tint(c, 0.35) for c in cols], width=0.6, edgecolor="white", linewidth=1.0)
    for i, b in enumerate(BASINS):
        bx.text(i, km[b] + 6, f"{edges[b]} edges", ha="center", va="bottom", fontsize=6.5)
    bx.set(ylabel="road km closed", ylim=(0, max(km.values()) * 1.6))
    bx.legend([Patch(facecolor=INK2), Patch(facecolor=tint(INK2, 0.35))],
              [f"under {DEEP:.2f} m of water or more", "rest of the closed edges"], loc="upper left", fontsize=6.5)
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
