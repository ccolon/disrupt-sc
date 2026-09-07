"""Scenario figures for the Rhine 2026 paper.

F4  the shock: weekly Kaub gauge, the capacity factor it implies, and the
    schedule the model receives (cost multiplier per week; closure weeks).
    Needs only scenarios/<profile>.csv + draught_table.csv.
F5  production loss in the worst week, NUTS2 choropleth (sequential blue ramp).
F6  weekly value-added loss by country (top countries), % of weekly VA.
F5/F6 need a scenario run folder (analyze_scenario.py's inputs).

Colour: reference palette - series slots 1-3 (blue/orange/aqua) in fixed
order, sequential blue ramp for the choropleth, orange (slot 2) for the
closure highlight; text in ink tokens.

Usage:
    python studies/rhine2026/plots/scenario_figures.py --profile 2026 [--run runs/rhine2026/2026_seed42]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "disrupt-sc-data" / "EU"
sys.path.insert(0, str(HERE))
from run_rhine import (CLOSED_MULTIPLIER, DEFAULT_CARGO_TYPES, DEFAULT_CLOSURE_FLOORS,  # noqa: E402
                       build_disruptions, kaub_entries, load_factor_curve, parse_closure_floors,
                       weekly_reductions)

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
       "#1c5cab", "#184f95", "#104281", "#0d366b"]
INK, INK2, INK3, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8985", "#e6e5e1", "#fcfcfb"
COUNTRY = {"DEU": "Germany", "NLD": "Netherlands", "CHE": "Switzerland", "FRA": "France", "BEL": "Belgium",
           "AUT": "Austria", "ITA": "Italy", "POL": "Poland", "LUX": "Luxembourg", "CZE": "Czechia"}


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


def fig_shock(profile: str, closure_threshold: float, out: Path, closure_floors: str | None = DEFAULT_CLOSURE_FLOORS):
    prof = pd.read_csv(HERE / "scenarios" / f"{profile}.csv")
    curve = load_factor_curve(HERE / "scenarios" / "draught_table.csv")
    red = weekly_reductions(prof, curve)
    floors = parse_closure_floors(closure_floors) if "kaub_cm" in prof.columns else None
    cts = list(DEFAULT_CARGO_TYPES)
    sched = {d["start_time"]: d for d in kaub_entries(build_disruptions(
        red, ["rhine_mainz_koblenz"], closure_threshold=closure_threshold,
        gauges=prof["kaub_cm"].astype(float).tolist() if floors else None, closure_floors=floors, cargo_types=cts))}
    weeks = pd.to_datetime(prof["week_start"])
    factor = [1 - r for r in red]

    def _mult(d):
        m = d["cost_multiplier"]
        return m["default"] if isinstance(m, dict) else m

    def _closed_for(d):
        if d["type"] == "transport_disruption":
            return list(cts)
        m = d["cost_multiplier"]
        return [ct for ct in cts if m.get(ct, m["default"]) >= CLOSED_MULTIPLIER] if isinstance(m, dict) else []

    mult = [_mult(sched[t]) if t in sched and sched[t]["type"] == "transport_cost_shock" else np.nan
            for t in range(1, len(red) + 1)]
    closed = [t in sched and sched[t]["type"] == "transport_disruption" for t in range(1, len(red) + 1)]
    closed_for = [_closed_for(sched[t]) if t in sched else [] for t in range(1, len(red) + 1)]

    fig, axes = plt.subplots(4 if floors else 3, 1, figsize=(8.5, 8.2 if floors else 7), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1, 1, 0.45]} if floors else None)
    fig.patch.set_facecolor(SURFACE)
    ax = axes[0]
    ax.plot(weeks, prof["kaub_cm"], color=SERIES[0], linewidth=2, marker="o", markersize=5)
    ax.axhline(78, color=INK3, linewidth=1, linestyle="--")
    ax.text(weeks.iloc[0], 80, "GlW 78 cm (equivalent low water)", fontsize=7, color=INK3, va="bottom")
    style(ax, f"Kaub gauge, weekly mean ({profile})", "cm")
    ax = axes[1]
    ax.plot(weeks, [100 * f for f in factor], color=SERIES[2], linewidth=2, marker="o", markersize=5)
    style(ax, "Fleet capacity past Kaub implied by the draught table", "% of normal")
    ax.set_ylim(0, 105)
    ax = axes[2]
    ax.bar(weeks, [m if not np.isnan(m) else 0 for m in mult], width=5.5, color=SERIES[0], linewidth=0)
    ymax = max([m for m in mult if not np.isnan(m)] + [1]) * 1.15
    ax.set_ylim(0, ymax)
    for w, c in zip(weeks, closed):
        if c:
            ax.bar(w, ymax, width=5.5, color=SERIES[1], alpha=0.35, linewidth=0)
            ax.text(w, ymax * 0.55, "closed", rotation=90, ha="center", va="center", fontsize=7, color=INK2)
    ax.axhline(1, color=INK3, linewidth=0.8)
    style(ax, "What the model receives: cost multiplier on the Kaub edge (orange = closed for every class)", "× baseline cost")
    if floors:
        ax = axes[3]
        for i, ct in enumerate(cts):
            ys = [i for w, cf in zip(weeks, closed_for) if ct in cf]
            xs = [w for w, cf in zip(weeks, closed_for) if ct in cf]
            ax.scatter(xs, ys, marker="s", s=60, color=SERIES[1], linewidths=0)
        ax.set_yticks(range(len(cts)))
        ax.set_yticklabels([f"{ct} (≤ {floors.get(ct, floors['default']):.0f} cm)" for ct in cts], fontsize=7, color=INK2)
        ax.set_ylim(-0.7, len(cts) - 0.3)
        style(ax, "Closed for the cargo class (gauge at or below its sailing floor)", "")
    ax.set_xlabel("week", fontsize=8, color=INK2)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F4_shock_{profile}.{ext}", dpi=300, facecolor=SURFACE)
    plt.close(fig)


def _loss_by_firm(run: Path) -> pd.DataFrame:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    base = fd[fd["time_step"] == 0].set_index("firm")["production"]
    fd["base"] = fd["firm"].map(base)
    fd["loss"] = (fd["base"] - fd["production"]).clip(lower=0)
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    fd["va_share"] = fd["sector"].map((va["mrio_va"] / va["mrio_output"]).to_dict()).fillna(0.3)
    fd["va_loss"] = fd["loss"] * fd["va_share"]
    return fd


def fig_loss_map(run: Path, out: Path):
    fd = _loss_by_firm(run)
    weekly = fd.groupby("time_step")["va_loss"].sum()
    peak = int(weekly.idxmax())
    ft = gpd.read_file(run / "firm_table.geojson")
    ft["firm"] = ft.index
    sub = fd[fd["time_step"] == peak].set_index("firm")
    ft["va_loss"] = ft["firm"].map(sub["va_loss"]).fillna(0)
    ft["base"] = ft["firm"].map(sub["base"]).fillna(0)
    nuts = gpd.read_file(DATA / "Spatial" / "sources" / "nuts2_admin.geojson")
    joined = gpd.sjoin(ft[["va_loss", "base", "geometry"]], nuts[["nuts_id", "geometry"]], how="inner", predicate="within")
    agg = joined.groupby("nuts_id").agg(va_loss=("va_loss", "sum"), base=("base", "sum"))
    nuts = nuts.merge(agg, left_on="nuts_id", right_index=True, how="left")
    nuts["loss_pct"] = 100 * nuts["va_loss"] / nuts["base"].replace(0, np.nan)
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
    cmap = ListedColormap(SEQ)
    vmax = np.nanpercentile(nuts["loss_pct"], 98) if nuts["loss_pct"].notna().any() else 1
    nuts.to_crs(3035).plot(column="loss_pct", cmap=cmap, vmin=0, vmax=max(vmax, 0.1), ax=ax,
                          edgecolor="#ffffff", linewidth=0.3, missing_kwds={"color": "#f0efec"},
                          legend=True, legend_kwds={"label": "production loss, % of baseline (value-added weighted)",
                                                    "shrink": 0.5, "orientation": "horizontal", "pad": 0.02})
    edges = gpd.read_file(run / "transport_edges.geojson")
    rh = edges[edges["name"].astype(str).str.startswith("rhine")].to_crs(3035)
    rh.plot(ax=ax, color=SERIES[1], linewidth=1.5, zorder=3)
    ax.set_xlim(2.4e6, 6.3e6); ax.set_ylim(1.3e6, 5.4e6); ax.set_axis_off()
    ax.set_title(f"Production loss by NUTS2 region in the worst week (t = {peak}); Rhine chain in orange",
                 loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F5_loss_map.{ext}", dpi=300, facecolor=SURFACE)
    plt.close(fig)
    return peak


def fig_loss_by_country(run: Path, out: Path):
    fd = _loss_by_firm(run)
    by = fd.groupby(["time_step", "region"])["va_loss"].sum().unstack("region").fillna(0)
    va_region = pd.read_csv(run / "mrio_by_region.csv").set_index("region")["mrio_va"] / 52.0
    pct = 100 * by / va_region
    top = by.sum().sort_values(ascending=False).head(6).index.tolist()
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    fig.patch.set_facecolor(SURFACE)
    for i, c in enumerate(top):
        ax.plot(pct.index, pct[c], color=SERIES[i % len(SERIES)], linewidth=2, label=COUNTRY.get(c, c))
        ax.text(pct.index[-1] + 0.2, pct[c].iloc[-1], COUNTRY.get(c, c), fontsize=7, color=INK2, va="center")
    style(ax, "Weekly value-added loss by country, % of the country's weekly value added", "% of weekly VA")
    ax.set_xlabel("week of the run (1 = 22 June 2026)", fontsize=8, color=INK2)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2, ncol=3, loc="upper left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F6_loss_by_country.{ext}", dpi=300, facecolor=SURFACE)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="2026")
    ap.add_argument("--closure-threshold", type=float, default=0.75)
    ap.add_argument("--closure-floors", default=DEFAULT_CLOSURE_FLOORS,
                    help="per-cargo sailing floors as in run_rhine.py; 'none' = single floor")
    ap.add_argument("--run", default=None, help="scenario run folder for F5/F6")
    ap.add_argument("--out", default=str(HERE / "figures"))
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    fig_shock(args.profile, args.closure_threshold, out, closure_floors=args.closure_floors)
    print(f"F4 written for profile {args.profile}")
    if args.run:
        run = Path(args.run)
        if not run.exists():
            run = ROOT / "runs" / "rhine2026" / args.run
        if (run / "firm_data.csv").exists() and (run / "firm_data.csv").stat().st_size > 0:
            peak = fig_loss_map(run, out)
            fig_loss_by_country(run, out)
            print(f"F5/F6 written from {run} (peak week {peak})")
        else:
            print(f"no firm_data yet in {run}")


if __name__ == "__main__":
    main()
