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
    df_to_html, pct_dev, warn_box, ok_box,
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
    if firm_data is not None:
        sections.append(_section_mrio_comparison(
            firm_data, mrio_by_sector, mrio_by_region, params))

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

    # Filter to edges with flow
    gdf = flow_gdf.copy()

    # Determine cargo types present
    cargo_types = detect_cargo_types(gdf)

    if not cargo_types:
        return "<h2>1. Transport Flow Maps</h2><p>No cargo type columns found.</p>"

    # Bounding box from data
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    pad = 2
    lon_range = [bounds[0] - pad, bounds[2] + pad]
    lat_range = [bounds[1] - pad, bounds[3] + pad]

    # --- Total flow map (2 panels: USD, tons) ---
    fig_total = _make_flow_map_pair(
        gdf, "flow_total", "flow_total_tons",
        "Total flow (mUSD)", "Total flow (tons)",
        lon_range, lat_range,
    )
    html_parts.append(fig_to_div(fig_total, height=500))

    # --- Per cargo type (3 rows x 2 cols) ---
    n_ct = len(cargo_types)
    titles = []
    for ct in cargo_types:
        label = ct.replace("_", " ").title()
        titles.extend([f"{label} (mUSD)", f"{label} (tons)"])

    fig = make_subplots(
        rows=n_ct, cols=2,
        subplot_titles=titles,
        specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}]] * n_ct,
        vertical_spacing=0.06,
        horizontal_spacing=0.02,
    )

    for i, ct in enumerate(cargo_types):
        row = i + 1
        add_flow_traces(fig, gdf, f"usd_{ct}", lon_range, lat_range,
                         row=row, col=1, value_label="mUSD")
        add_flow_traces(fig, gdf, f"tons_{ct}", lon_range, lat_range,
                         row=row, col=2, value_label="tons")

    fig.update_layout(
        height=400 * n_ct,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    apply_geo_layout(fig, lon_range, lat_range, n_ct)

    html_parts.append(fig_to_div(fig, height=400 * n_ct))
    return "\n".join(html_parts)


def _make_flow_map_pair(gdf, usd_col, tons_col, title_usd, title_tons,
                        lon_range, lat_range):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[title_usd, title_tons],
        specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}]],
        horizontal_spacing=0.02,
    )
    add_flow_traces(fig, gdf, usd_col, lon_range, lat_range,
                    row=1, col=1, value_label="mUSD")
    add_flow_traces(fig, gdf, tons_col, lon_range, lat_range,
                    row=1, col=2, value_label="tons")
    fig.update_layout(
        height=500, showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    apply_geo_layout(fig, lon_range, lat_range, 1)
    return fig


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
                             params: dict) -> str:
    html = ["<h2>3. Model vs. MRIO Comparison</h2>"]

    scale = time_scale_factor(params)
    mu = monetary_label(params)
    mrio_conv = mrio_to_model_annual(params)  # data_units/yr → model_units/yr

    data_mu = params.get("monetary_units_in_data", mu)
    if mrio_conv != 1:
        html.append(f"<p><em>MRIO values converted from {data_mu}/yr to {mu}/yr "
                    f"(factor {mrio_conv:g})</em></p>")

    # Model: aggregate t=0 data per region and sector
    t0 = firm_data[firm_data["time_step"] == 0].copy()
    if t0.empty:
        return "<h2>3. Model vs. MRIO Comparison</h2><p>No firm data at t=0.</p>"

    # Use total_input if available (realized intermediate input), else fall back to total_order
    input_col = "total_input" if "total_input" in t0.columns else "total_order"

    model_by_region = t0.groupby("region").agg(
        total_output=("production", "sum"),
        total_input=(input_col, "sum"),
    ).reset_index()
    model_by_region["total_output_annual"] = model_by_region["total_output"] * scale
    model_by_region["total_input_annual"] = model_by_region["total_input"] * scale

    model_by_sector = t0.groupby("sector").agg(
        total_output=("production", "sum"),
        total_input=(input_col, "sum"),
    ).reset_index()
    model_by_sector["total_output_annual"] = model_by_sector["total_output"] * scale
    model_by_sector["total_input_annual"] = model_by_sector["total_input"] * scale

    # --- By-sector comparison ---
    if mrio_by_sector is not None:
        # Convert MRIO values to model monetary units (annual)
        for col in ["mrio_output", "mrio_input", "mrio_va", "mrio_final_demand", "mrio_export"]:
            if col in mrio_by_sector.columns:
                mrio_by_sector[col] = mrio_by_sector[col] * mrio_conv

        merged = model_by_sector.merge(mrio_by_sector, on="sector", how="outer")
        merged["model_va"] = merged["total_output_annual"] - merged["total_input_annual"]
        merged["output_dev_pct"] = pct_dev(
            merged["total_output_annual"], merged["mrio_output"])

        display_cols = ["sector", "total_output_annual", "mrio_output", "output_dev_pct",
                        "total_input_annual", "mrio_input",
                        "model_va", "mrio_va",
                        "mrio_final_demand", "mrio_export"]
        rename = {
            "total_output_annual": f"Model output ({mu}/yr)",
            "mrio_output": f"MRIO output ({mu}/yr)",
            "output_dev_pct": "Dev (%)",
            "total_input_annual": f"Model input ({mu}/yr)",
            "mrio_input": f"MRIO input ({mu}/yr)",
            "model_va": f"Model VA ({mu}/yr)",
            "mrio_va": f"MRIO VA ({mu}/yr)",
            "mrio_final_demand": f"MRIO FD ({mu}/yr)",
            "mrio_export": f"MRIO export ({mu}/yr)",
        }
        available = [c for c in display_cols if c in merged.columns]
        display_df = merged[available].rename(columns=rename)
        html.append("<h3>By sector (annualized)</h3>")
        html.append(df_to_html(display_df, fmt_nums=True))

        # Scatter plot: model vs MRIO output
        plot_df = merged.dropna(subset=["total_output_annual", "mrio_output"])
        if not plot_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=plot_df["mrio_output"], y=plot_df["total_output_annual"],
                mode="markers+text", text=plot_df["sector"],
                textposition="top center", textfont_size=9,
                marker=dict(size=10, color="#2c3e50"),
                hovertemplate="%{text}<br>MRIO: %{x:,.1f}<br>Model: %{y:,.1f}<extra></extra>",
            ))
            max_val = max(plot_df["total_output_annual"].max(),
                         plot_df["mrio_output"].max()) * 1.1
            fig.add_trace(go.Scatter(
                x=[0, max_val], y=[0, max_val],
                mode="lines", line=dict(dash="dash", color="gray"),
                showlegend=False,
            ))
            fig.update_layout(
                title="Model vs. MRIO output by sector",
                xaxis_title=f"MRIO output ({mu}/yr)",
                yaxis_title=f"Model output ({mu}/yr)",
                height=450, width=600,
                margin=dict(l=60, r=20, t=40, b=60),
            )
            html.append(fig_to_div(fig))
    else:
        html.append("<p><em>mrio_by_sector.csv not found — sector MRIO comparison "
                    "unavailable.</em></p>")

    # --- By-region comparison ---
    html.append("<h3>By region (annualized)</h3>")
    if mrio_by_region is not None:
        for col in ["mrio_output", "mrio_input", "mrio_va"]:
            if col in mrio_by_region.columns:
                mrio_by_region[col] = mrio_by_region[col] * mrio_conv

        merged_r = model_by_region.merge(mrio_by_region, on="region", how="outer")
        merged_r["model_va"] = merged_r["total_output_annual"] - merged_r["total_input_annual"]
        merged_r["output_dev_pct"] = pct_dev(
            merged_r["total_output_annual"], merged_r["mrio_output"])

        display_cols_r = ["region", "total_output_annual", "mrio_output", "output_dev_pct",
                          "total_input_annual", "mrio_input",
                          "model_va", "mrio_va"]
        rename_r = {
            "total_output_annual": f"Model output ({mu}/yr)",
            "mrio_output": f"MRIO output ({mu}/yr)",
            "output_dev_pct": "Dev (%)",
            "total_input_annual": f"Model input ({mu}/yr)",
            "mrio_input": f"MRIO input ({mu}/yr)",
            "model_va": f"Model VA ({mu}/yr)",
            "mrio_va": f"MRIO VA ({mu}/yr)",
        }
        available_r = [c for c in display_cols_r if c in merged_r.columns]
        html.append(df_to_html(merged_r[available_r].rename(columns=rename_r), fmt_nums=True))

        # Scatter plot: model vs MRIO output per region
        plot_r = merged_r.dropna(subset=["total_output_annual", "mrio_output"])
        if not plot_r.empty:
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(
                x=plot_r["mrio_output"], y=plot_r["total_output_annual"],
                mode="markers+text", text=plot_r["region"],
                textposition="top center", textfont_size=9,
                marker=dict(size=10, color="#2c3e50"),
                hovertemplate="%{text}<br>MRIO: %{x:,.1f}<br>Model: %{y:,.1f}<extra></extra>",
            ))
            max_val_r = max(plot_r["total_output_annual"].max(),
                           plot_r["mrio_output"].max()) * 1.1
            fig_r.add_trace(go.Scatter(
                x=[0, max_val_r], y=[0, max_val_r],
                mode="lines", line=dict(dash="dash", color="gray"),
                showlegend=False,
            ))
            fig_r.update_layout(
                title="Model vs. MRIO output by region",
                xaxis_title=f"MRIO output ({mu}/yr)",
                yaxis_title=f"Model output ({mu}/yr)",
                height=450, width=600,
                margin=dict(l=60, r=20, t=40, b=60),
            )
            html.append(fig_to_div(fig_r))
    else:
        region_display = model_by_region[["region", "total_output_annual", "total_input_annual"]].copy()
        region_display["va"] = region_display["total_output_annual"] - region_display["total_input_annual"]
        region_display = region_display.rename(columns={
            "total_output_annual": f"Output ({mu}/yr)",
            "total_input_annual": f"Input ({mu}/yr)",
            "va": f"VA ({mu}/yr)",
        })
        html.append(df_to_html(region_display, fmt_nums=True))

    return "\n".join(html)


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


