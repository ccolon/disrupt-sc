"""Paper figures from the calibrated EU baseline run.

F1  network map: TEN-T edges by mode (recessive), the named Rhine chain
    highlighted, firm points sized by baseline output (importance).
F2  modal split, model vs Eurostat 2023: per country (road/rail/IWW % of
    inland tkm) and per cargo class (vs the DE NST targets).
F3  Rhine profile: modelled tonnage per named segment along the river-km
    against the CCNR cross-sections / estimates (rhine_capacities.csv).

Colour: the dataviz reference palette's first three categorical slots (blue,
orange, aqua - validated all-pairs in both modes) for road / rail / waterway
in that fixed order; model = filled marks, data = outlined/hatched marks, so
model-vs-data never relies on a fourth hue. Text in ink tokens, never in a
series colour. Static output for the manuscript (PNG 300 dpi + PDF).

Usage:
    python studies/rhine2026/plots/baseline_figures.py --run 20260903_150745 [--out studies/rhine2026/figures]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "disrupt-sc-data" / "EU"

# reference palette (light mode), fixed categorical order: 1 blue, 2 orange, 3 aqua
SERIES = {"roads": "#2a78d6", "railways": "#eb6834", "waterways": "#1baf7a"}
MODE_LABEL = {"roads": "Road", "railways": "Rail", "waterways": "Inland waterway"}
INK, INK2, INK3, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8985", "#e6e5e1", "#fcfcfb"

EUROSTAT_2023 = {  # tran_hv_frmod 2023, % of inland tkm road / rail / IWW
    "DE": (72.8, 20.6, 6.6), "NL": (52.8, 6.4, 40.9), "BE": (77.6, 11.7, 10.7), "FR": (88.9, 9.2, 1.9),
    "AT": (68.9, 29.3, 1.7), "CH": (65.6, 34.3, 0.1), "PL": (75.8, 24.1, 0.0), "IT": (88.0, 12.0, 0.0),
}
DE_CARGO_TARGETS = {"container": (68, 28, 5), "dry_bulk": (53, 27, 20), "liquid_bulk": (28, 42, 30)}
CARGO_LABEL = {"container": "General cargo", "dry_bulk": "Dry bulk", "liquid_bulk": "Liquid bulk"}


def style(ax, title=None, ylabel=None):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=3)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, loc="left", fontsize=10, color=INK, pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8, color=INK2)


def fig_modal_split(edges: gpd.GeoDataFrame, out: Path):
    inland = edges[edges["type"].isin(["roads", "railways", "waterways"])].copy()
    inland["cc"] = inland["country_code"].astype(str).str.split(";").str[0].str.strip()
    inland["tkm"] = inland["flow_total_tons"] * inland["km"]
    modes = ["roads", "railways", "waterways"]
    countries = [c for c in EUROSTAT_2023 if c in set(inland["cc"])]
    model = {}
    for cc in countries:
        sub = inland[inland["cc"] == cc]
        tot = sub["tkm"].sum()
        model[cc] = [100 * sub.loc[sub["type"] == m, "tkm"].sum() / tot for m in modes]
    cargo = {}
    for ct in DE_CARGO_TARGETS:
        col = f"tons_{ct}"
        if col not in inland.columns:
            continue
        ctkm = inland[col].fillna(0) * inland["km"]
        tot = ctkm.sum()
        cargo[ct] = [100 * ctkm[inland["type"] == m].sum() / tot for m in modes]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [len(countries), len(cargo) + 1.0]})
    fig.patch.set_facecolor(SURFACE)
    w = 0.13
    for ax, groups, table, title in (
            (axes[0], countries, EUROSTAT_2023, "By country: model vs Eurostat 2023"),
            (axes[1], list(cargo), DE_CARGO_TARGETS, "By cargo class vs German targets")):
        x = np.arange(len(groups))
        for i, m in enumerate(modes):
            off = (i - 1) * 2.3 * w
            mod = [(model if table is EUROSTAT_2023 else cargo)[g][i] for g in groups]
            dat = [table[g][i] for g in groups]
            ax.bar(x + off - w / 2 - 0.01, mod, width=w, color=SERIES[m], linewidth=0, label=f"{MODE_LABEL[m]} - model")
            ax.bar(x + off + w / 2 + 0.01, dat, width=w, facecolor="none", edgecolor=SERIES[m], linewidth=1.2,
                   hatch="////", label=f"{MODE_LABEL[m]} - data")
        ax.set_xticks(x)
        ax.set_xticklabels([CARGO_LABEL.get(g, g) for g in groups], fontsize=8, color=INK2,
                           rotation=0 if table is EUROSTAT_2023 else 0)
        style(ax, title, "% of inland tonne-km")
        ax.set_ylim(0, 100)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, frameon=False, fontsize=8, labelcolor=INK2,
               bbox_to_anchor=(0.5, 0.045))
    fig.text(0.01, 0.005, "Filled = model baseline (run 20260903_150745); hatched outline = data. Model shares exclude short-haul "
             "road traffic by construction (firms at NUTS2/3 points); judge rail and waterways by tonne-km as well.",
             fontsize=7, color=INK3)
    fig.suptitle("Inland freight by mode, % of tonne-km", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0.11, 1, 0.95))
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F2_modal_split.{ext}", dpi=300, facecolor=SURFACE)
    plt.close(fig)


def fig_rhine_profile(edges: gpd.GeoDataFrame, out: Path):
    caps = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv")
    rhe = edges[edges["name"].astype(str).str.startswith("rhine")]
    grp = rhe.groupby("name")
    tkm = (rhe["flow_total_tons"] * rhe["km"]).groupby(rhe["name"]).sum()
    km = grp["km"].sum()
    model_mt = (tkm / km) * 52 / 1e6
    # river-km position: from the disruption tag "rhine;<seg>;km<a>-<b>" -> midpoint
    pos = {}
    for name, tag in zip(rhe["name"], rhe["disruption"].astype(str)):
        try:
            a, b = tag.split("km")[-1].split("-")
            pos[name] = (float(a) + float(b)) / 2
        except Exception:
            continue
    df = caps.set_index("name")
    df["model_mt"] = model_mt
    df["km"] = pd.Series(pos)
    # stop at the German-Dutch border: downstream of Lobith the delta splits into
    # branches and the model's Rotterdam traffic does not follow the one chain named here
    df = df.dropna(subset=["km", "model_mt"]).sort_values("km")
    df = df[df["km"] <= 890]

    fig, ax = plt.subplots(figsize=(9, 4.2))
    fig.patch.set_facecolor(SURFACE)
    ax.plot(df["km"], df["mt_per_year"], color=INK2, linewidth=2, marker="o", markersize=5,
            markerfacecolor=SURFACE, markeredgewidth=1.5, label="Normal year (CCNR cross-sections; estimates between)")
    ax.plot(df["km"], df["model_mt"], color=SERIES["waterways"], linewidth=2, marker="o", markersize=5,
            label="Model baseline")
    ax.set_ylim(0, 150)
    for town, k in (("Basel", 170), ("Strasbourg", 294), ("Karlsruhe", 360), ("Mannheim", 425), ("Mainz", 498),
                    ("Kaub", 546), ("Koblenz", 592), ("Köln", 688), ("Duisburg", 780), ("Emmerich", 852)):
        ax.axvline(k, color=GRID, linewidth=0.6, zorder=0)
        ax.text(k + 3, 2, town, rotation=90, va="bottom", ha="left", fontsize=7, color=INK3)
    ax.axvspan(546 - 4, 546 + 4, color=SERIES["railways"], alpha=0.25, linewidth=0)   # slot-2 orange as the highlight
    style(ax, "Rhine tonnage along the river, Basel to the German-Dutch border (Mt per year)", "Mt per year")
    ax.set_xlabel("Rhine-km (from Konstanz)", fontsize=8, color=INK2)
    ax.set_xlim(150, 890)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2, loc="upper left")
    fig.text(0.01, 0.005, "Kaub (km 546) shaded: the scenario edge. CCNR 2023: Emmerich 118 Mt, Iffezheim 16 Mt; other points interpolated from port volumes.",
             fontsize=7, color=INK3)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F3_rhine_profile.{ext}", dpi=300, facecolor=SURFACE)
    plt.close(fig)


def fig_network_map(edges: gpd.GeoDataFrame, firms: gpd.GeoDataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
    e = edges.to_crs(3035)
    for mode, lw, alpha in (("maritime", 0.4, 0.35), ("roads", 0.5, 0.6), ("railways", 0.5, 0.6), ("waterways", 0.9, 0.9)):
        sub = e[e["type"] == mode]
        if len(sub):
            sub.plot(ax=ax, color=SERIES.get(mode, INK3), linewidth=lw, alpha=alpha, zorder=2)
    rh = e[e["name"].astype(str).str.startswith("rhine")]
    rh.plot(ax=ax, color=SERIES["waterways"], linewidth=2.2, zorder=4)
    f = firms.to_crs(3035)
    size = np.sqrt(f["importance"].clip(lower=0).fillna(0))
    size = 60 * size / (size.max() or 1) + 1
    ax.scatter(f.geometry.x, f.geometry.y, s=size, color=INK, alpha=0.25, linewidths=0, zorder=3)
    ax.set_xlim(2.4e6, 6.3e6); ax.set_ylim(1.3e6, 5.4e6)
    ax.set_axis_off()
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color=SERIES[m], lw=2, label=MODE_LABEL[m]) for m in ("roads", "railways", "waterways")]
    handles.append(Line2D([0], [0], color=INK3, lw=1.5, alpha=0.6, label="Maritime lanes"))
    handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor=INK, alpha=0.4, markersize=7, label="Firm points (area = baseline output)"))
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8, labelcolor=INK2)
    ax.set_title("EU scope: TEN-T multimodal network and firm geography (Rhine chain highlighted)", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F1_network_firms.{ext}", dpi=300, facecolor=SURFACE)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="20260903_150745")
    ap.add_argument("--out", default=str(HERE / "figures"))
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    run = ROOT / "output" / "EU" / args.run
    edges = gpd.read_file(run / "transport_edges_with_flows_0.geojson")
    firms = gpd.read_file(run / "firm_table.geojson")
    fig_modal_split(edges, out)
    fig_rhine_profile(edges, out)
    fig_network_map(edges, firms, out)
    print(f"figures written to {out}")


if __name__ == "__main__":
    main()
