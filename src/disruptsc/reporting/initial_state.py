"""Generate an HTML report for an initial-state (equilibrium) run.

Reads only from the output folder (+ parameters.yaml for config).
Produces a self-contained HTML file with interactive plotly figures.

Usage:
    python -m disruptsc.reporting initial_state output/Gulf/20260401_095732
"""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from disruptsc.reporting._common import (
    load_params, load_csv, load_geodata,
    time_scale_factor, monetary_label, mrio_to_model_annual,
    detect_cargo_types, add_flow_traces, apply_geo_layout, fig_to_div,
    df_to_html, warn_box, ok_box,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ======================================================================
# Public API
# ======================================================================


def generate_report(output_folder: Path) -> Path:
    """Build the initial-state HTML report and return its path."""
    output_folder = Path(output_folder)
    params = load_params(output_folder)

    sections: list[str] = []
    sections.append(_html_header(output_folder, params))

    # 1. Flow maps
    flow_gdf = load_geodata(output_folder / "transport_edges_with_flows_0.geojson")
    if flow_gdf is not None:
        sections.append(_section_flow_maps(flow_gdf, params))

    # 2. Capacity / logistics tables
    logistics_report = load_csv(output_folder / "logistics_report.csv")
    logistics_top = load_csv(output_folder / "logistics_top_utilized.csv")
    if logistics_report is not None:
        sections.append(_section_capacity_table(logistics_report, logistics_top))

    # 3. MRIO comparison
    firm_data = load_csv(output_folder / "firm_data.csv")
    mrio_by_sector = load_csv(output_folder / "mrio_by_sector.csv")
    mrio_by_region = load_csv(output_folder / "mrio_by_region.csv")
    mrio_by_country = load_csv(output_folder / "mrio_by_country.csv")
    trade_data = load_csv(output_folder / "trade_data.csv")
    country_table = load_geodata(output_folder / "country_table.geojson")
    if firm_data is not None:
        sections.append(_section_mrio_comparison(
            firm_data, mrio_by_sector, mrio_by_region,
            mrio_by_country, trade_data, country_table, params))

    # 4. Agent summary
    firm_table = load_geodata(output_folder / "firm_table.geojson")
    hh_table = load_geodata(output_folder / "household_table.geojson")
    if firm_table is not None:
        sections.append(_section_agent_summary(firm_table, hh_table, params))

    # 5. Checks & warnings
    if firm_data is not None:
        sections.append(_section_checks(firm_data, params))

    # 6. SC network statistics
    sc_edgelist = load_csv(output_folder / "sc_network_edgelist.csv", index_col=0)
    if sc_edgelist is not None:
        sections.append(_section_sc_network_stats(sc_edgelist))

    # 7. Route & transport statistics
    logistics_summary = load_csv(output_folder / "logistics_summary.csv")
    if logistics_summary is not None:
        sections.append(_section_route_transport_stats(
            logistics_summary, firm_data, params))

    sections.append("</body></html>")

    html = "\n".join(sections)
    report_path = output_folder / "report_initial_state.html"
    report_path.write_text(html, encoding="utf-8")
    log.info(f"Report written to {report_path}")
    return report_path




# ======================================================================
# HTML scaffold
# ======================================================================


def _html_header(output_folder: Path, params: dict) -> str:
    scope = params.get("scope", output_folder.parent.name)
    ts = output_folder.name
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Initial State Report — {scope} ({ts})</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         max-width: 1400px; margin: 0 auto; padding: 20px; color: #333; }}
  h1 {{ border-bottom: 3px solid #2c3e50; padding-bottom: 10px; }}
  h2 {{ color: #2c3e50; margin-top: 40px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }}
  th, td {{ padding: 6px 10px; border: 1px solid #ddd; text-align: right; }}
  th {{ background: #2c3e50; color: white; text-align: center; }}
  tr:nth-child(even) {{ background: #f8f9fa; }}
  .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 4px; margin: 10px 0; }}
  .ok {{ background: #d4edda; border: 1px solid #28a745; padding: 10px; border-radius: 4px; margin: 10px 0; }}
  .metric {{ display: inline-block; background: #eef2f7; padding: 8px 16px;
             border-radius: 4px; margin: 4px; font-size: 14px; }}
  .metric b {{ color: #2c3e50; }}
  td:first-child {{ text-align: left; }}
  /* Round caps/joins for flow map lines (matches QGIS round cap/join style) */
  .js-plotly-plot .scattergeolayer path,
  .js-plotly-plot .scatterlayer path.js-line {{
    stroke-linejoin: round;
    stroke-linecap: round;
  }}
</style>
</head><body>
<h1>Initial State Report — {scope}</h1>
<p>Run: <code>{ts}</code> &nbsp;|&nbsp;
   Time resolution: <b>{params.get('time_resolution', '?')}</b> &nbsp;|&nbsp;
   Monetary units: <b>{monetary_label(params)}</b></p>
"""


# ======================================================================
# Section 1: Flow Maps
# ======================================================================


def _section_flow_maps(flow_gdf: gpd.GeoDataFrame, params: dict) -> str:
    html_parts = ["<h2>1. Transport Flow Maps</h2>"]

    gdf = flow_gdf.copy()
    cargo_types = detect_cargo_types(gdf)

    if not cargo_types:
        return "<h2>1. Transport Flow Maps</h2><p>No cargo type columns found.</p>"

    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    pad = 2
    lon_range = [bounds[0] - pad, bounds[2] + pad]
    lat_range = [bounds[1] - pad, bounds[3] + pad]

    # --- Total flow (tons only) ---
    fig_total = make_subplots(
        rows=1, cols=1,
        subplot_titles=["Total flow (tons)"],
        specs=[[{"type": "scattergeo"}]],
    )
    add_flow_traces(fig_total, gdf, "flow_total_tons", lon_range, lat_range,
                    row=1, col=1, value_label="tons")
    fig_total.update_layout(
        height=500, showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    apply_geo_layout(fig_total, lon_range, lat_range, n_rows=1, n_cols=1)
    html_parts.append(fig_to_div(fig_total, height=500))

    # --- Per cargo type (tons only, single row) ---
    n_ct = len(cargo_types)
    titles = [ct.replace("_", " ").title() + " (tons)" for ct in cargo_types]

    fig = make_subplots(
        rows=1, cols=n_ct,
        subplot_titles=titles,
        specs=[[{"type": "scattergeo"}] * n_ct],
        horizontal_spacing=0.02,
    )

    for i, ct in enumerate(cargo_types):
        add_flow_traces(fig, gdf, f"tons_{ct}", lon_range, lat_range,
                        row=1, col=i + 1, value_label="tons")

    fig.update_layout(
        height=450,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    apply_geo_layout(fig, lon_range, lat_range, n_rows=1, n_cols=n_ct)

    html_parts.append(fig_to_div(fig, height=450))
    return "\n".join(html_parts)


# ======================================================================
# Section 2: Capacity Table
# ======================================================================


def _section_capacity_table(logistics_report: pd.DataFrame,
                            logistics_top: pd.DataFrame | None) -> str:
    html = ["<h2>2. Port & Capacity Utilization</h2>"]

    # Filter to t=0
    lr = logistics_report[logistics_report["time_step"] == 0].copy()
    if lr.empty:
        return "<h2>2. Port & Capacity Utilization</h2><p>No data for t=0.</p>"

    lr = lr.sort_values("max_utilization_pct", ascending=False)

    cols = ["name", "type", "flow_tons", "flow_usd",
            "tons_container", "capacity_container", "utilization_container_pct",
            "tons_dry_bulk", "capacity_dry_bulk", "utilization_dry_bulk_pct",
            "tons_liquid_bulk", "capacity_liquid_bulk", "utilization_liquid_bulk_pct",
            "max_utilization_pct"]
    available = [c for c in cols if c in lr.columns]
    html.append("<h3>Monitored edges (capacity overrides)</h3>")
    html.append(df_to_html(lr[available], fmt_nums=True,
                            highlight_col="max_utilization_pct", threshold=100))

    # Top 10 most utilized (including non-overridden)
    if logistics_top is not None:
        lt = logistics_top[logistics_top["time_step"] == 0].copy()
        if not lt.empty:
            lt = lt.sort_values("max_utilization_pct", ascending=False)
            available_top = [c for c in cols if c in lt.columns]
            html.append("<h3>Top 10 most utilized edges (any edge)</h3>")
            html.append(df_to_html(lt[available_top], fmt_nums=True,
                                    highlight_col="max_utilization_pct", threshold=100))

    return "\n".join(html)


# ======================================================================
# Section 3: MRIO Comparison
# ======================================================================


def _section_mrio_comparison(firm_data: pd.DataFrame,
                             mrio_by_sector: pd.DataFrame | None,
                             mrio_by_region: pd.DataFrame | None,
                             mrio_by_country: pd.DataFrame | None,
                             trade_data: pd.DataFrame | None,
                             country_table: gpd.GeoDataFrame | None,
                             params: dict) -> str:
    html = ["<h2>3. Model vs. MRIO Comparison</h2>"]

    scale = time_scale_factor(params)
    mu = monetary_label(params)
    mrio_conv = mrio_to_model_annual(params)  # data_units/yr → model_units/yr

    data_mu = params.get("monetary_units_in_data", mu)
    if mrio_conv != 1:
        html.append(f"<p><em>MRIO values converted from {data_mu}/yr to {mu}/yr "
                    f"(factor {mrio_conv:g})</em></p>")

    t0 = firm_data[firm_data["time_step"] == 0].copy()
    if t0.empty:
        return "<h2>3. Model vs. MRIO Comparison</h2><p>No firm data at t=0.</p>"

    model_by_region = t0.groupby("region").agg(
        total_output=("production", "sum"),
    ).reset_index()
    model_by_region["total_output_annual"] = model_by_region["total_output"] * scale

    model_by_sector = t0.groupby("sector").agg(
        total_output=("production", "sum"),
    ).reset_index()
    model_by_sector["total_output_annual"] = model_by_sector["total_output"] * scale

    def _scatter(fig, merged, label_col, col_idx, color,
                 x_col, y_col, x_title, y_title, row=1):
        plot_df = merged.dropna(subset=[x_col, y_col])
        if plot_df.empty:
            return
        fig.add_trace(go.Scatter(
            x=plot_df[x_col], y=plot_df[y_col],
            mode="markers+text", text=plot_df[label_col],
            textposition="top center", textfont_size=9,
            marker=dict(size=10, color=color),
            hovertemplate="%{text}<br>MRIO: %{x:,.1f}<br>Model: %{y:,.1f}<extra></extra>",
            showlegend=False,
        ), row=row, col=col_idx)
        mx = max(plot_df[y_col].max(), plot_df[x_col].max()) * 1.1
        fig.add_trace(go.Scatter(
            x=[0, mx], y=[0, mx],
            mode="lines", line=dict(dash="dash", color="gray"),
            showlegend=False,
        ), row=row, col=col_idx)
        fig.update_xaxes(title_text=x_title, row=row, col=col_idx)
        fig.update_yaxes(title_text=y_title, row=row, col=col_idx)

    # ── Output by sector / region ──
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Total output by sector", "Total output by region"],
        horizontal_spacing=0.12,
    )

    if mrio_by_sector is not None and "mrio_output" in mrio_by_sector.columns:
        ms = mrio_by_sector.copy()
        ms["mrio_output"] = ms["mrio_output"] * mrio_conv
        merged_s = model_by_sector.merge(ms[["sector", "mrio_output"]],
                                         on="sector", how="outer")
        _scatter(fig, merged_s, "sector", 1, "#2c3e50",
                 x_col="mrio_output", y_col="total_output_annual",
                 x_title=f"MRIO output ({mu}/yr)",
                 y_title=f"Model output ({mu}/yr)")
    else:
        html.append("<p><em>mrio_by_sector.csv not found — sector scatter unavailable.</em></p>")

    if mrio_by_region is not None and "mrio_output" in mrio_by_region.columns:
        mr = mrio_by_region.copy()
        mr["mrio_output"] = mr["mrio_output"] * mrio_conv
        merged_r = model_by_region.merge(mr[["region", "mrio_output"]],
                                         on="region", how="outer")
        _scatter(fig, merged_r, "region", 2, "#00CC96",
                 x_col="mrio_output", y_col="total_output_annual",
                 x_title=f"MRIO output ({mu}/yr)",
                 y_title=f"Model output ({mu}/yr)")
    else:
        html.append("<p><em>mrio_by_region.csv not found — region scatter unavailable.</em></p>")

    fig.update_layout(height=450, margin=dict(l=60, r=20, t=60, b=60))
    html.append(fig_to_div(fig))

    # ── Imports / exports per country ──
    # Model side comes from trade_data.csv aggregated at t=0.
    # A foreign country's `exports_value` (in the trade log it is the seller)
    # = model IMPORTS from that country (country plays exporter role).
    # A foreign country's `imports_value` = model EXPORTS to that country
    # (country plays importer role).
    if mrio_by_country is None:
        html.append("<p><em>mrio_by_country.csv not found — country scatter unavailable.</em></p>")
        return "\n".join(html)
    if trade_data is None:
        html.append("<p><em>trade_data.csv not found — country scatter unavailable.</em></p>")
        return "\n".join(html)

    trade0 = trade_data[trade_data["time_step"] == 0]
    model_by_country = trade0.groupby("country").agg(
        model_imports=("exports_value", "sum"),
        model_exports=("imports_value", "sum"),
    ).reset_index()
    model_by_country["model_imports_annual"] = model_by_country["model_imports"] * scale
    model_by_country["model_exports_annual"] = model_by_country["model_exports"] * scale

    mc = mrio_by_country.copy()
    mc["mrio_imports"] = mc["mrio_imports"] * mrio_conv
    mc["mrio_exports"] = mc["mrio_exports"] * mrio_conv
    # Restrict the join to the countries listed in the MRIO summary — the
    # trade log also carries region-region rows that aren't external trade.
    merged_c = mc.merge(model_by_country, on="country", how="left").fillna(
        {"model_imports_annual": 0.0, "model_exports_annual": 0.0}
    )

    has_maps = (
        country_table is not None
        and not country_table.empty
        and "country" in country_table.columns
    )
    if has_maps:
        pts = country_table[country_table.geometry.notna()].copy()
        pts["geometry"] = pts.geometry.representative_point()
        pts["lon"] = pts.geometry.x
        pts["lat"] = pts.geometry.y
        merged_c = merged_c.merge(
            pts[["country", "lon", "lat"]], on="country", how="left",
        )
        has_maps = merged_c[["lon", "lat"]].notna().any().all()

    n_rows = 2 if has_maps else 1
    subplot_titles = [
        "Total imports by country (country as exporter)",
        "Total exports by country (country as importer)",
    ]
    specs = [[{"type": "xy"}, {"type": "xy"}]]
    if has_maps:
        subplot_titles += [
            f"Model imports by country — bubble ∝ value ({mu}/yr)",
            f"Model exports by country — bubble ∝ value ({mu}/yr)",
        ]
        specs.append([{"type": "scattergeo"}, {"type": "scattergeo"}])

    fig_c = make_subplots(
        rows=n_rows, cols=2,
        subplot_titles=subplot_titles,
        specs=specs,
        horizontal_spacing=0.12,
        vertical_spacing=0.12,
        row_heights=[0.45, 0.55] if has_maps else None,
    )
    _scatter(fig_c, merged_c, "country", 1, "#FF7F0E",
             x_col="mrio_imports", y_col="model_imports_annual",
             x_title=f"MRIO imports ({mu}/yr)",
             y_title=f"Model imports ({mu}/yr)", row=1)
    _scatter(fig_c, merged_c, "country", 2, "#AB63FA",
             x_col="mrio_exports", y_col="model_exports_annual",
             x_title=f"MRIO exports ({mu}/yr)",
             y_title=f"Model exports ({mu}/yr)", row=1)

    if has_maps:
        _add_country_bubbles(fig_c, merged_c, "model_imports_annual",
                             row=2, col=1, color="#FF7F0E")
        _add_country_bubbles(fig_c, merged_c, "model_exports_annual",
                             row=2, col=2, color="#AB63FA")
        _apply_country_geo(fig_c, merged_c, n_maps=2, first_geo_index=1)

    fig_c.update_layout(
        height=850 if has_maps else 450,
        margin=dict(l=60, r=20, t=60, b=60),
    )
    html.append(fig_to_div(fig_c, height=850 if has_maps else 450))

    return "\n".join(html)


def _add_country_bubbles(fig, df: pd.DataFrame, value_col: str,
                         row: int, col: int, color: str) -> None:
    """Add a scattergeo bubble trace where marker area ∝ value_col."""
    plot_df = df.dropna(subset=["lon", "lat", value_col]).copy()
    plot_df = plot_df[plot_df[value_col] > 0]
    if plot_df.empty:
        return
    values = plot_df[value_col].astype(float).values
    max_marker = 40.0
    sizeref = 2.0 * float(values.max()) / (max_marker ** 2) if values.max() > 0 else 1.0
    fig.add_trace(
        go.Scattergeo(
            lon=plot_df["lon"], lat=plot_df["lat"],
            text=plot_df["country"],
            customdata=values,
            mode="markers+text",
            textposition="top center", textfont_size=9,
            marker=dict(
                size=values,
                sizemode="area",
                sizeref=sizeref,
                sizemin=3,
                color=color,
                opacity=0.7,
                line=dict(width=0.5, color="rgb(60,60,60)"),
            ),
            hovertemplate="%{text}<br>value: %{customdata:,.1f}<extra></extra>",
            showlegend=False,
        ),
        row=row, col=col,
    )


def _apply_country_geo(fig, df: pd.DataFrame, n_maps: int,
                       first_geo_index: int) -> None:
    """Apply a shared world-scope layout to the trailing scattergeo subplots."""
    pts = df.dropna(subset=["lon", "lat"])
    if pts.empty:
        lon_range = [-180, 180]
        lat_range = [-60, 80]
    else:
        pad = 5
        lon_range = [float(pts["lon"].min()) - pad, float(pts["lon"].max()) + pad]
        lat_range = [float(pts["lat"].min()) - pad, float(pts["lat"].max()) + pad]
    for i in range(n_maps):
        idx = first_geo_index + i
        geo_key = "geo" if idx == 1 else f"geo{idx}"
        fig.update_layout(**{
            geo_key: dict(
                scope="world",
                projection_type="natural earth",
                lonaxis_range=lon_range,
                lataxis_range=lat_range,
                showland=True, landcolor="rgb(243, 243, 243)",
                showocean=True, oceancolor="rgb(220, 230, 242)",
                showcountries=True, countrycolor="rgb(180, 180, 180)",
                showcoastlines=True, coastlinecolor="rgb(180, 180, 180)",
            )
        })


# ======================================================================
# Section 4: Agent Summary
# ======================================================================


def _section_agent_summary(firm_table: gpd.GeoDataFrame,
                           hh_table: gpd.GeoDataFrame | None,
                           params: dict) -> str:
    html = ["<h2>4. Agent Summary</h2>"]

    # Firms per sector per region
    firm_pivot = firm_table.groupby(["region", "sector_type"]).size().unstack(fill_value=0)
    firm_pivot["Total"] = firm_pivot.sum(axis=1)
    html.append("<h3>Firms per region and sector type</h3>")
    html.append(df_to_html(firm_pivot.reset_index(), fmt_nums=False))

    # Households
    if hh_table is not None and not hh_table.empty:
        hh_summary = hh_table.groupby("region").agg(
            n_households=("region", "size"),
            total_pop=("population", "sum"),
        ).reset_index()
        html.append("<h3>Households per region</h3>")
        html.append(df_to_html(hh_summary, fmt_nums=True))

    # OD points per region
    od_firms = firm_table.groupby("region")["od_point"].nunique().reset_index()
    od_firms.columns = ["region", "unique_od_points"]
    html.append("<h3>Unique transport nodes (od_points) per region</h3>")
    html.append(df_to_html(od_firms, fmt_nums=False))

    return "\n".join(html)


# ======================================================================
# Section 5: Checks & Warnings
# ======================================================================


def _section_checks(firm_data: pd.DataFrame, params: dict) -> str:
    html = ["<h2>5. Equilibrium Checks</h2>"]

    t0 = firm_data[firm_data["time_step"] == 0].copy()
    warnings_found = False

    # --- Rationing check ---
    under_rationed = t0[t0["rationing"] < 1.0 - 1e-6]
    if under_rationed.empty:
        html.append(ok_box("All firms have rationing = 1.0"))
    else:
        warnings_found = True
        n = len(under_rationed)
        html.append(warn_box(
            f"<b>{n} firm(s)</b> have rationing &lt; 1 at t=0 "
            f"(model did not reach equilibrium)"))
        cols = ["firm", "region", "sector", "rationing", "total_order",
                "production", "product_stock"]
        available = [c for c in cols if c in under_rationed.columns]
        html.append(df_to_html(
            under_rationed[available].sort_values("rationing").head(20),
            fmt_nums=True))

    # --- Price check ---
    price_off = t0[t0["price"].apply(lambda p: abs(p - 1.0) > 1e-6)]
    if price_off.empty:
        html.append(ok_box("All firms have price = 1.0"))
    else:
        warnings_found = True
        n = len(price_off)
        html.append(warn_box(
            f"<b>{n} firm(s)</b> have price != 1.0 at t=0"))
        cols = ["firm", "region", "sector", "price", "delta_price_input"]
        available = [c for c in cols if c in price_off.columns]
        html.append(df_to_html(price_off[available].head(20), fmt_nums=True))

    # --- Zero-delivery links (order > 0 but delivery missing) ---
    # Detect from firm_data: if production < total_order significantly
    underproducing = t0[
        (t0["total_order"] > 1e-6) &
        (t0["production"] < t0["total_order"] * 0.99)
    ]
    if not underproducing.empty:
        warnings_found = True
        html.append(warn_box(
            f"<b>{len(underproducing)} firm(s)</b> producing less than ordered "
            f"(potential supply gaps)"))
        cols = ["firm", "region", "sector", "production", "total_order",
                "production_capacity", "rationing"]
        available = [c for c in cols if c in underproducing.columns]
        html.append(df_to_html(
            underproducing[available].sort_values("rationing").head(20),
            fmt_nums=True))

    if not warnings_found:
        html.append(ok_box("No equilibrium issues detected"))

    return "\n".join(html)


# ======================================================================
# Section 6: Supply Chain Network Statistics
# ======================================================================


def _section_sc_network_stats(edgelist: pd.DataFrame) -> str:
    html = ["<h2>6. Supply Chain Network</h2>"]

    n_edges = len(edgelist)
    n_firms = edgelist[edgelist["source_type"] == "firm"]["source_id"].nunique()
    n_hh = edgelist[edgelist["target_type"] == "household"]["target_id"].nunique()
    n_countries = edgelist[edgelist["source_type"] == "country"]["source_id"].nunique()

    html.append(
        f'<div class="metric"><b>Links:</b> {n_edges:,}</div>'
        f'<div class="metric"><b>Firms:</b> {n_firms:,}</div>'
        f'<div class="metric"><b>Households:</b> {n_hh:,}</div>'
        f'<div class="metric"><b>Countries:</b> {n_countries:,}</div>'
    )

    # In-degree distribution for firms (as buyers)
    firm_buyers = edgelist[edgelist["target_type"] == "firm"]
    if not firm_buyers.empty:
        in_degree = firm_buyers.groupby("target_str_id").size()
        html.append("<h3>Firm in-degree (number of suppliers)</h3>")
        stats = in_degree.describe()
        html.append(f"<p>Mean: {stats['mean']:.1f}, Median: {stats['50%']:.0f}, "
                    f"Max: {stats['max']:.0f}, Std: {stats['std']:.1f}</p>")

        fig = go.Figure(go.Histogram(x=in_degree.values, nbinsx=30,
                                      marker_color="#2c3e50"))
        fig.update_layout(
            title="Firm in-degree distribution",
            xaxis_title="Number of suppliers",
            yaxis_title="Count",
            height=300, width=500,
            margin=dict(l=50, r=20, t=40, b=40),
        )
        html.append(fig_to_div(fig))

    # Out-degree distribution for firms (as suppliers)
    firm_suppliers = edgelist[edgelist["source_type"] == "firm"]
    if not firm_suppliers.empty:
        out_degree = firm_suppliers.groupby("source_str_id").size()
        html.append("<h3>Firm out-degree (number of clients)</h3>")
        stats = out_degree.describe()
        html.append(f"<p>Mean: {stats['mean']:.1f}, Median: {stats['50%']:.0f}, "
                    f"Max: {stats['max']:.0f}, Std: {stats['std']:.1f}</p>")

        fig = go.Figure(go.Histogram(x=out_degree.values, nbinsx=30,
                                      marker_color="#00CC96"))
        fig.update_layout(
            title="Firm out-degree distribution",
            xaxis_title="Number of clients",
            yaxis_title="Count",
            height=300, width=500,
            margin=dict(l=50, r=20, t=40, b=40),
        )
        html.append(fig_to_div(fig))

    # Concentration: top-5 suppliers by number of clients
    if not firm_suppliers.empty:
        top_suppliers = out_degree.nlargest(10).reset_index()
        top_suppliers.columns = ["supplier", "n_clients"]
        html.append("<h3>Top 10 suppliers by client count</h3>")
        html.append(df_to_html(top_suppliers, fmt_nums=False))

    return "\n".join(html)


# ======================================================================
# Section 7: Route & Transport Statistics
# ======================================================================


def _section_route_transport_stats(logistics_summary: pd.DataFrame,
                                   firm_data: pd.DataFrame | None,
                                   params: dict) -> str:
    html = ["<h2>7. Transport & Route Statistics</h2>"]
    mu = monetary_label(params)

    # Modal split from logistics_summary (t=0)
    t0 = logistics_summary[logistics_summary["time_step"] == 0]
    network_row = t0[t0["metric"].isna()]
    mode_rows = t0[t0["metric"].notna()].copy()

    if not network_row.empty:
        nr = network_row.iloc[0]
        html.append(
            f'<div class="metric"><b>Total tons:</b> {nr.get("total_tons", 0):,.0f}</div>'
            f'<div class="metric"><b>Total {mu}:</b> {nr.get("total_usd", 0):,.1f}</div>'
            f'<div class="metric"><b>Edges with flow:</b> {nr.get("n_edges_with_flow", 0):.0f}</div>'
            f'<div class="metric"><b>Edges no flow:</b> {nr.get("n_edges_no_flow", 0):.0f}</div>'
        )

    if not mode_rows.empty:
        mode_rows["mode"] = mode_rows["metric"].str.replace("mode_", "")
        mode_display = mode_rows[["mode", "tons", "usd"]].copy()
        total_tons = mode_display["tons"].sum()
        total_usd = mode_display["usd"].sum()
        mode_display["tons_pct"] = (mode_display["tons"] / total_tons * 100
                                     if total_tons > 0 else 0)
        mode_display["usd_pct"] = (mode_display["usd"] / total_usd * 100
                                    if total_usd > 0 else 0)
        mode_display = mode_display.rename(columns={
            "tons": "Tons", "usd": f"{mu}",
            "tons_pct": "Tons %", "usd_pct": f"{mu} %",
        })
        html.append("<h3>Modal split (t=0)</h3>")
        html.append(df_to_html(mode_display, fmt_nums=True))

        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Tons %",
            x=mode_display["mode"],
            y=mode_display["Tons %"],
            marker_color="#2c3e50",
        ))
        fig.add_trace(go.Bar(
            name=f"{mu} %",
            x=mode_display["mode"],
            y=mode_display[f"{mu} %"],
            marker_color="#00CC96",
        ))
        fig.update_layout(
            title="Modal split",
            barmode="group", height=350, width=500,
            margin=dict(l=50, r=20, t=40, b=40),
        )
        html.append(fig_to_div(fig))

    # Transport cost share (from firm_data)
    if firm_data is not None:
        t0_firms = firm_data[firm_data["time_step"] == 0]
        if "profit" in t0_firms.columns and "production" in t0_firms.columns:
            configured_share = params.get("transport_share", "?")
            html.append(f"<h3>Transport cost share</h3>")
            html.append(f"<p>Configured transport_share parameter: <b>{configured_share}</b></p>")

    return "\n".join(html)


# ======================================================================
# HTML helpers
# ======================================================================


