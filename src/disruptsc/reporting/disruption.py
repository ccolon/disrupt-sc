"""Generate an HTML report for a disruption run.

Reads only from the output folder (+ parameters.yaml for config).
Produces a self-contained HTML file with interactive plotly figures.

Usage:
    python -m disruptsc.reporting disruption output/Gulf/20260401_120000
"""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from disruptsc.reporting._common import (
    load_params, load_csv, load_geodata, monetary_label,
    detect_cargo_types, add_flow_traces, apply_geo_layout, fig_to_div,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ── Color palettes ──────────────────────────────────────────────────
# Consistent colors across graphs
_REGION_COLORS = px.colors.qualitative.Set2
_SECTOR_COLORS = px.colors.qualitative.Dark24
_PATHWAY_COLORS = {"Shortage": "#e74c3c", "Cost-push inflation": "#3498db"}

# ======================================================================
# Public API
# ======================================================================


def generate_report(output_folder: Path) -> Path:
    """Build the disruption HTML report and return its path."""
    output_folder = Path(output_folder)
    params = load_params(output_folder)
    mu = monetary_label(params)

    sections: list[str] = []
    sections.append(_html_header(output_folder, params))

    # Load CSV data
    df_hh = load_csv(output_folder / "household_data.csv")
    # Household report = welfare agents only; government/investment are separate national
    # accounting agents (agent_type) and would inflate the household loss sections.
    if not df_hh.empty and "agent_type" in df_hh.columns:
        df_hh = df_hh[df_hh["agent_type"] == "household"].copy()
    df_hh_sector = load_csv(output_folder / "household_data_by_sector.csv")
    df_country = load_csv(output_folder / "country_data.csv")
    df_firm = load_csv(output_folder / "firm_data.csv")

    # 1. Flow comparison maps (t=0 vs t=1)
    gdf_t0 = load_geodata(output_folder / "transport_edges_with_flows_0.geojson")
    gdf_t1 = load_geodata(output_folder / "transport_edges_with_flows_1.geojson")
    df_routing = load_csv(output_folder / "routing_summary.csv")
    if gdf_t0 is not None and gdf_t1 is not None:
        sections.append(_section_flow_comparison(gdf_t0, gdf_t1, params, df_routing))
    elif gdf_t0 is not None:
        log.warning("transport_edges_with_flows_1.geojson not found — "
                    "skipping flow comparison")
    else:
        log.warning("No flow GeoJSON files found")

    # 2. Total welfare loss by agent (per region/country)
    if df_hh is not None and df_country is not None:
        sections.append(_section_loss_by_agent(df_hh, df_country, mu))

    # 3. Household loss by pathway (stacked area)
    if df_hh is not None:
        sections.append(_section_loss_by_pathway(
            df_hh, "Household", mu,
            group_cols=None,
        ))

    # 4. Country loss by pathway (stacked area)
    if df_country is not None:
        sections.append(_section_loss_by_pathway(
            df_country, "Country", mu,
            group_cols=None,
        ))

    # 5. Total output by sector
    if df_firm is not None:
        sections.append(_section_output_by_sector(df_firm, mu))

    # 6. Total output by region
    if df_firm is not None:
        sections.append(_section_output_by_region(df_firm, mu))

    # 7. Average purchase price increase by sector
    df_link = load_csv(output_folder / "link_data.csv")
    if df_link is not None:
        sections.append(_section_price_by_sector(df_link, mu))

    # 8. Weighted rationing by sector
    if df_firm is not None:
        sections.append(_section_rationing_by_sector(df_firm))

    # 9. Capacity utilization by sector
    if df_firm is not None:
        sections.append(_section_capacity_utilization(df_firm))

    # 10. Input shortfall by sector
    if df_firm is not None:
        sections.append(_section_input_shortfall(df_firm))

    # 11. Loss concentration (top agents)
    if df_hh is not None:
        sections.append(_section_loss_concentration(df_hh, mu))

    # 12. Recovery trajectory (normalized deviation)
    if df_firm is not None:
        sections.append(_section_recovery_trajectory(df_firm))

    # 13. Propagation heatmap
    if df_firm is not None:
        sections.append(_section_propagation_heatmap(df_firm))

    # 14. Inventory levels by input sector
    df_inv = load_csv(output_folder / "inventory_data.csv")
    if df_inv is not None:
        sections.append(_section_inventory_by_input_sector(df_inv))

    # Write HTML
    sections.append("</body></html>")
    html = "\n".join(sections)
    out_path = output_folder / "report_disruption.html"
    out_path.write_text(html, encoding="utf-8")
    log.info(f"Report written to {out_path}")
    return out_path


# ======================================================================
# HTML scaffold
# ======================================================================


def _html_header(output_folder: Path, params: dict) -> str:
    scope = params.get("scope", output_folder.parent.name)
    ts = output_folder.name
    mu = monetary_label(params)

    disruptions = params.get("disruptions") or []
    desc_parts = []
    for d in disruptions:
        dtype = d.get("type", "?")
        desc = d.get("description_type", "")
        vals = d.get("values", [])
        start = d.get("start_time", "?")
        dur = d.get("duration", "?")
        desc_parts.append(
            f"{dtype} ({desc}: {', '.join(str(v) for v in vals)}) "
            f"t={start}..{int(start)+int(dur)-1 if isinstance(start,int) and isinstance(dur,int) else '?'}"
        )
    disruption_summary = "; ".join(desc_parts) if desc_parts else "<em>none configured</em>"

    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Disruption Report — {scope}</title>
<script src="https://cdn.plot.ly/plotly-3.0.0.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
         sans-serif; max-width: 1400px; margin: auto; padding: 20px; }}
  h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
  h2 {{ color: #2c3e50; margin-top: 40px; }}
  h3 {{ color: #34495e; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: right; }}
  th {{ background: #f5f5f5; position: sticky; top: 0; }}
  td:first-child {{ text-align: left; }}
  .warning {{ background: #fff3cd; border-left: 4px solid #ffc107;
              padding: 10px; margin: 10px 0; }}
  .ok {{ background: #d4edda; border-left: 4px solid #28a745;
         padding: 10px; margin: 10px 0; }}
  .section-note {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 10px; }}
  /* Round caps/joins for flow map lines (matches QGIS round cap/join style) */
  .js-plotly-plot .scattergeolayer path,
  .js-plotly-plot .scatterlayer path.js-line {{
    stroke-linejoin: round;
    stroke-linecap: round;
  }}
</style>
</head><body>
<h1>Disruption Report — {scope}</h1>
<p>Run: <code>{ts}</code> &nbsp;|&nbsp;
   Time resolution: <b>{params.get('time_resolution', '?')}</b> &nbsp;|&nbsp;
   Monetary units: <b>{mu}</b></p>
<p>Disruption: {disruption_summary}</p>
"""


# ======================================================================
# Section 1: Flow comparison maps (unchanged)
# ======================================================================


def _section_flow_comparison(gdf_t0: gpd.GeoDataFrame,
                             gdf_t1: gpd.GeoDataFrame,
                             params: dict,
                             df_routing: pd.DataFrame | None = None) -> str:
    html = ["<h2>1. Flow Comparison — Pre-disruption vs. Disrupted</h2>"]
    mu = monetary_label(params)

    cargo_types = detect_cargo_types(gdf_t0) or detect_cargo_types(gdf_t1)
    if not cargo_types:
        return "<h2>1. Flow Comparison</h2><p>No cargo type columns found.</p>"

    b0 = gdf_t0.total_bounds
    b1 = gdf_t1.total_bounds
    pad = 2
    lon_range = [min(b0[0], b1[0]) - pad, max(b0[2], b1[2]) + pad]
    lat_range = [min(b0[1], b1[1]) - pad, max(b0[3], b1[3]) + pad]

    global_max_val = 0.0
    for ct in cargo_types:
        col = f"usd_{ct}"
        for gdf in (gdf_t0, gdf_t1):
            if col in gdf.columns:
                mx = gdf[col].fillna(0).max()
                if mx > global_max_val:
                    global_max_val = mx
    global_max = global_max_val if global_max_val > 0 else None

    n_ct = len(cargo_types)
    titles = []
    for ct in cargo_types:
        label = ct.replace("_", " ").title()
        titles.extend([f"{label} — t=0 ({mu})", f"{label} — t=1 ({mu})"])

    fig = make_subplots(
        rows=n_ct, cols=2,
        subplot_titles=titles,
        specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}]] * n_ct,
        vertical_spacing=0.06,
        horizontal_spacing=0.02,
    )

    for i, ct in enumerate(cargo_types):
        row = i + 1
        col_name = f"usd_{ct}"
        add_flow_traces(fig, gdf_t0, col_name, lon_range, lat_range,
                        row=row, col=1, value_label=mu,
                        max_value=global_max)
        add_flow_traces(fig, gdf_t1, col_name, lon_range, lat_range,
                        row=row, col=2, value_label=mu,
                        max_value=global_max)

    fig.update_layout(
        height=400 * n_ct,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    apply_geo_layout(fig, lon_range, lat_range, n_ct, n_cols=2)

    html.append(fig_to_div(fig, height=400 * n_ct))
    html.append(_disrupted_edge_baseline_flows(gdf_t0, cargo_types, params, mu))
    html.append(_flow_change_summary(gdf_t0, gdf_t1, cargo_types, mu, df_routing))

    return "\n".join(html)


def _disrupted_edge_baseline_flows(gdf_t0: gpd.GeoDataFrame,
                                   cargo_types: list[str],
                                   params: dict, mu: str) -> str:
    """Show value and tonnage flowing through disrupted edges at t=0."""
    disruptions = params.get("disruptions") or []
    # Collect attribute/values pairs that identify disrupted edges
    edge_filters = []
    for d in disruptions:
        if d.get("type") != "transport_disruption":
            continue
        attr = d.get("attribute", "name")
        desc_type = d.get("description_type", "")
        if desc_type == "edge_attributes":
            for val in d.get("values", []):
                edge_filters.append((attr, val))

    if not edge_filters:
        return ""

    # Find matching edges in t=0 GeoJSON
    mask = pd.Series(False, index=gdf_t0.index)
    for attr, val in edge_filters:
        if attr in gdf_t0.columns:
            mask |= gdf_t0[attr] == val

    disrupted = gdf_t0[mask]
    if disrupted.empty:
        edge_desc = ", ".join(f'{a}="{v}"' for a, v in edge_filters)
        return (f'<h3>Baseline flows on disrupted edges</h3>'
                f'<p class="warning">No edges found matching {edge_desc} '
                f'in t=0 flow data.</p>')

    html = ['<h3>Baseline flows on disrupted edges (t=0)</h3>',
            '<p class="section-note">Value and tonnage on transport edges '
            'that will be disrupted at t=1. This represents the flow '
            'directly exposed to the disruption.</p>']

    # Per-edge detail
    edge_rows = []
    for _, row in disrupted.iterrows():
        edge_name = row.get("name", "?")
        r = {"Edge": edge_name}
        for ct in cargo_types:
            usd_col = f"usd_{ct}"
            tons_col = f"tons_{ct}"
            r[f"{ct.replace('_', ' ').title()} ({mu})"] = f"{row.get(usd_col, 0) or 0:,.1f}"
            r[f"{ct.replace('_', ' ').title()} (tons)"] = f"{row.get(tons_col, 0) or 0:,.0f}"
        r[f"Total ({mu})"] = f"{row.get('flow_total', 0) or 0:,.1f}"
        r["Total (tons)"] = f"{row.get('flow_total_tons', 0) or 0:,.0f}"
        edge_rows.append(r)

    # Summary row if multiple edges
    if len(disrupted) > 1:
        summary = {"Edge": "All disrupted"}
        for ct in cargo_types:
            usd_col = f"usd_{ct}"
            tons_col = f"tons_{ct}"
            summary[f"{ct.replace('_', ' ').title()} ({mu})"] = (
                f"{disrupted[usd_col].fillna(0).sum():,.1f}" if usd_col in disrupted.columns else "0.0")
            summary[f"{ct.replace('_', ' ').title()} (tons)"] = (
                f"{disrupted[tons_col].fillna(0).sum():,.0f}" if tons_col in disrupted.columns else "0")
        summary[f"Total ({mu})"] = f"{disrupted['flow_total'].fillna(0).sum():,.1f}" if "flow_total" in disrupted.columns else "0.0"
        summary["Total (tons)"] = f"{disrupted['flow_total_tons'].fillna(0).sum():,.0f}" if "flow_total_tons" in disrupted.columns else "0"
        edge_rows.append(summary)

    df = pd.DataFrame(edge_rows)
    html.append(_df_to_html_table(df))
    return "\n".join(html)


def _flow_change_summary(gdf_t0, gdf_t1, cargo_types, mu,
                         df_routing: pd.DataFrame | None = None):
    _ = (gdf_t0, gdf_t1)  # this table is sourced only from routing_summary.csv
    if df_routing is None or df_routing.empty:
        return (
            "<h3>Flow change summary</h3>"
            '<p class="warning">routing_summary.csv is required to build this table.</p>'
        )
    return _flow_summary_from_routing(df_routing, cargo_types, mu)


def _flow_summary_from_routing(df_routing: pd.DataFrame,
                               cargo_types: list[str], mu: str) -> str:
    """Unified flow & routing table from routing_summary.csv."""
    html = ["<h3>Flow change summary</h3>",
            '<p class="section-note">Any flow between agents, split into: '
            'cargo types for transport-network flows with different OD points, '
            'one row for transport-network flows with the same OD point, and '
            'one row for flows that do not use the transport network. Values '
            'are in equilibrium prices.</p>']

    timesteps = sorted(df_routing["time_step"].unique())
    if len(timesteps) < 2:
        html.append("<p>Not enough time steps for comparison.</p>")
        return "\n".join(html)
    t0, t1 = timesteps[0], timesteps[1]

    rt0 = df_routing[df_routing["time_step"] == t0].set_index("cargo_type")
    rt1 = df_routing[df_routing["time_step"] == t1].set_index("cargo_type")
    special_rows = ["transport_same_od_point", "no_transport_network"]
    cargo_rows = [ct for ct in cargo_types if ct in rt0.index or ct in rt1.index]
    extra_rows = sorted(
        ct for ct in (set(rt0.index) | set(rt1.index))
        if ct not in set(cargo_rows) and ct not in set(special_rows)
    )
    all_ct = cargo_rows + extra_rows + [
        ct for ct in special_rows if ct in rt0.index or ct in rt1.index
    ]

    rows = []
    totals = {"t0": 0, "t1": 0, "blocked": 0, "rerouted": 0}
    for ct in all_ct:
        val_t0 = rt0.loc[ct, "total_usd"] if ct in rt0.index else 0
        val_t1 = rt1.loc[ct, "total_usd"] if ct in rt1.index else 0
        blocked = rt1.loc[ct, "blocked_usd"] if ct in rt1.index else 0
        rerouted = rt1.loc[ct, "alternative_usd"] if ct in rt1.index else 0
        change = val_t1 - val_t0
        pct_change = (change / val_t0 * 100) if val_t0 else 0
        pct_blocked = (blocked / val_t0 * 100) if val_t0 else 0
        pct_rerouted = (rerouted / val_t0 * 100) if val_t0 else 0

        totals["t0"] += val_t0
        totals["t1"] += val_t1
        totals["blocked"] += blocked
        totals["rerouted"] += rerouted

        if ct == "transport_same_od_point":
            label = "Transport Network, Same OD Point"
        elif ct == "no_transport_network":
            label = "No Transport Network"
        else:
            label = ct.replace("_", " ").title()

        rows.append({
            "Flow category": label,
            f"t=0 ({mu})": f"{val_t0:,.1f}",
            f"t=1 ({mu})": f"{val_t1:,.1f}",
            f"Change ({mu})": f"{change:+,.1f}",
            "Change (%)": f"{pct_change:+.1f}%",
            f"Blocked ({mu})": f"{blocked:,.1f}",
            "Blocked (%)": f"{pct_blocked:.1f}%",
            f"Rerouted ({mu})": f"{rerouted:,.1f}",
            "Rerouted (%)": f"{pct_rerouted:.1f}%",
        })

    # Total row
    t = totals
    change_all = t["t1"] - t["t0"]
    pct_all = (change_all / t["t0"] * 100) if t["t0"] else 0
    pct_b = (t["blocked"] / t["t0"] * 100) if t["t0"] else 0
    pct_r = (t["rerouted"] / t["t0"] * 100) if t["t0"] else 0
    rows.append({
        "Flow category": "Total",
        f"t=0 ({mu})": f"{t['t0']:,.1f}",
        f"t=1 ({mu})": f"{t['t1']:,.1f}",
        f"Change ({mu})": f"{change_all:+,.1f}",
        "Change (%)": f"{pct_all:+.1f}%",
        f"Blocked ({mu})": f"{t['blocked']:,.1f}",
        "Blocked (%)": f"{pct_b:.1f}%",
        f"Rerouted ({mu})": f"{t['rerouted']:,.1f}",
        "Rerouted (%)": f"{pct_r:.1f}%",
    })

    df = pd.DataFrame(rows)
    html.append(_df_to_html_table(df))
    return "\n".join(html)


def _df_to_html_table(df: pd.DataFrame) -> str:
    """Convert a DataFrame to a simple HTML table string."""
    lines = ["<table>"]
    lines.append("<tr>" + "".join(f"<th>{c}</th>" for c in df.columns) + "</tr>")
    for _, row in df.iterrows():
        lines.append("<tr>" + "".join(f"<td>{row[c]}</td>" for c in df.columns) + "</tr>")
    lines.append("</table>")
    return "\n".join(lines)


# ======================================================================
# Section 2: Total welfare loss by agent type
# ======================================================================


def _section_loss_by_agent(df_hh: pd.DataFrame, df_country: pd.DataFrame,
                           mu: str) -> str:
    html = ["<h2>2. Total Welfare Loss by Agent</h2>",
            '<p class="section-note">Loss = consumption shortfall + extra spending '
            'from price increases, relative to t=0 equilibrium.</p>']

    # Household: aggregate by region per timestep
    df_hh = df_hh.copy()
    df_hh["total_loss"] = df_hh["consumption_loss"] + df_hh["extra_spending"]
    hh_by_region = df_hh.groupby(["time_step", "region"])["total_loss"].sum().reset_index()

    # Country: aggregate per country per timestep
    df_c = df_country.copy()
    df_c["total_loss"] = df_c["consumption_loss"] + df_c["extra_spending"]
    c_by_country = df_c.groupby(["time_step", "country"])["total_loss"].sum().reset_index()

    fig = go.Figure()

    # Household lines (solid)
    regions = sorted(hh_by_region["region"].unique())
    for i, region in enumerate(regions):
        mask = hh_by_region["region"] == region
        sub = hh_by_region[mask]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["total_loss"],
            mode="lines+markers", name=f"HH — {region}",
            line=dict(color=_REGION_COLORS[i % len(_REGION_COLORS)]),
            legendgroup="households",
            legendgrouptitle_text="Households",
        ))

    # Country lines (dashed)
    countries = sorted(c_by_country["country"].unique())
    for i, country in enumerate(countries):
        mask = c_by_country["country"] == country
        sub = c_by_country[mask]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["total_loss"],
            mode="lines+markers", name=f"Country — {country}",
            line=dict(dash="dash",
                      color=_SECTOR_COLORS[i % len(_SECTOR_COLORS)]),
            legendgroup="countries",
            legendgrouptitle_text="Countries",
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title=f"Welfare loss ({mu})",
        height=500,
        legend=dict(groupclick="togglegroup"),
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Sections 3 & 4: Loss by pathway (stacked area)
# ======================================================================


def _section_loss_by_pathway(df: pd.DataFrame, agent_label: str, mu: str,
                             group_cols=None) -> str:
    section_num = 3 if agent_label == "Household" else 4
    html = [f"<h2>{section_num}. {agent_label} Loss — "
            f"Shortage vs. Cost-push Inflation</h2>"]

    agg = df.groupby("time_step")[["consumption_loss", "extra_spending"]].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg["time_step"], y=agg["consumption_loss"],
        mode="lines", name="Shortage",
        line=dict(color=_PATHWAY_COLORS["Shortage"]),
        fill="tozeroy", stackgroup="loss",
    ))
    fig.add_trace(go.Scatter(
        x=agg["time_step"], y=agg["extra_spending"],
        mode="lines", name="Cost-push inflation",
        line=dict(color=_PATHWAY_COLORS["Cost-push inflation"]),
        fill="tonexty", stackgroup="loss",
    ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title=f"Loss ({mu})",
        height=400,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 5: Total output by sector
# ======================================================================


def _section_output_by_sector(df_firm: pd.DataFrame, mu: str) -> str:
    html = ["<h2>5. Total Output by Sector</h2>",
            '<p class="section-note">Sum of firm production per sector '
            '(regional firms only, excluding country agents).</p>']

    agg = df_firm.groupby(["time_step", "sector"])["production"].sum().reset_index()
    sectors = sorted(agg["sector"].unique())

    fig = go.Figure()
    for i, sector in enumerate(sectors):
        sub = agg[agg["sector"] == sector]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["production"],
            mode="lines+markers", name=sector,
            line=dict(color=_SECTOR_COLORS[i % len(_SECTOR_COLORS)]),
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title=f"Total output ({mu})",
        height=500,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 6: Total output by region
# ======================================================================


def _section_output_by_region(df_firm: pd.DataFrame, mu: str) -> str:
    html = ["<h2>6. Total Output by Region</h2>"]

    agg = df_firm.groupby(["time_step", "region"])["production"].sum().reset_index()
    regions = sorted(agg["region"].unique())

    fig = go.Figure()
    for i, region in enumerate(regions):
        sub = agg[agg["region"] == region]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["production"],
            mode="lines+markers", name=region,
            line=dict(color=_REGION_COLORS[i % len(_REGION_COLORS)]),
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title=f"Total output ({mu})",
        height=500,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 7: Average price increase by sector
# ======================================================================


def _section_price_by_sector(df_link: pd.DataFrame, mu: str) -> str:
    html = ["<h2>7. Average Purchase Price Increase by Sector</h2>",
            '<p class="section-note">Order-weighted average purchase price '
            'increase relative to equilibrium, by seller sector. Includes '
            'both input cost-push and transport cost-push components. '
            'Columns = buyer type, rows = buyer region.</p>']

    df = df_link.copy()
    # Filter out rows with no eq_price or zero eq_price
    df = df[df["eq_price"] > 0]
    if df.empty:
        html.append("<p>No link data with positive equilibrium price.</p>")
        return "\n".join(html)

    # Map buyer_type to readable labels
    buyer_type_map = {"Firm": "Firm", "Household": "Household", "Country": "Country"}
    df["buyer_type_label"] = df["buyer_type"].map(buyer_type_map).fillna(df["buyer_type"])

    # For buyer_region: use buyer_region column; fill blanks with buyer_id for countries
    df["buyer_region_label"] = df["buyer_region"].replace("", np.nan).fillna(df["buyer_id"])

    # Relative price increase per link
    df["price_ratio"] = df["price"] / df["eq_price"]
    df["price_increase"] = df["price_ratio"] - 1.0
    # Weight by order value at equilibrium price
    df["order_value"] = df["order"] * df["eq_price"]
    df["weighted_dp"] = df["price_increase"] * df["order_value"]

    # Group by time_step, seller_sector, buyer_type, buyer_region
    agg = df.groupby(["time_step", "seller_sector", "buyer_type_label",
                       "buyer_region_label"]).agg(
        weighted_dp=("weighted_dp", "sum"),
        total_order=("order_value", "sum"),
    ).reset_index()
    agg["avg_price_increase"] = agg["weighted_dp"] / agg["total_order"].replace(0, np.nan)

    # Build facet grid: columns = buyer type, rows = buyer region.
    # Cap rows to the TOP_N regions by total order value to keep the figure
    # readable on large scopes (e.g. World has 80+ regions). Smaller regions
    # are aggregated into a summary count rendered below the figure.
    TOP_N_REGIONS = 10
    buyer_types = sorted(agg["buyer_type_label"].unique())
    sectors = sorted(agg["seller_sector"].unique())
    sector_color = {s: _SECTOR_COLORS[i % len(_SECTOR_COLORS)]
                    for i, s in enumerate(sectors)}

    region_order_value = (
        agg.groupby("buyer_region_label")["total_order"].sum()
        .sort_values(ascending=False)
    )
    n_regions_total = len(region_order_value)
    top_regions = region_order_value.head(TOP_N_REGIONS).index.tolist()
    buyer_regions = sorted(top_regions)
    dropped_regions = n_regions_total - len(buyer_regions)
    if dropped_regions > 0:
        dropped_share = (
            region_order_value.iloc[len(buyer_regions):].sum()
            / region_order_value.sum() if region_order_value.sum() > 0 else 0.0
        )
        html.append(
            f'<p class="section-note">Showing the top {len(buyer_regions)} '
            f'regions by total order value ({100*(1-dropped_share):.1f}% of '
            f'flow). {dropped_regions} smaller regions '
            f'({100*dropped_share:.1f}% of flow) omitted for readability.</p>'
        )

    agg = agg[agg["buyer_region_label"].isin(buyer_regions)]

    n_rows = len(buyer_regions)
    n_cols = len(buyer_types)
    if n_rows == 0 or n_cols == 0:
        html.append("<p>No data for price facets.</p>")
        return "\n".join(html)

    # Plotly requires vertical_spacing ≤ 1/(rows-1) and horizontal_spacing
    # ≤ 1/(cols-1). Clamp defensively just below the geometric limit.
    v_space = min(0.04, 0.95 / (n_rows - 1)) if n_rows > 1 else 0.04
    h_space = min(0.04, 0.95 / (n_cols - 1)) if n_cols > 1 else 0.04

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[f"{bt} — {br}" for br in buyer_regions for bt in buyer_types],
        shared_xaxes=True, shared_yaxes=True,
        vertical_spacing=v_space, horizontal_spacing=h_space,
    )

    # Track which sectors already have a legend entry
    legend_shown = set()

    for ri, region in enumerate(buyer_regions, 1):
        for ci, btype in enumerate(buyer_types, 1):
            sub = agg[(agg["buyer_type_label"] == btype) &
                      (agg["buyer_region_label"] == region)]
            for sector in sectors:
                ss = sub[sub["seller_sector"] == sector]
                if ss.empty:
                    continue
                show_legend = sector not in legend_shown
                legend_shown.add(sector)
                fig.add_trace(go.Scatter(
                    x=ss["time_step"], y=ss["avg_price_increase"] * 100,
                    mode="lines+markers", name=sector,
                    legendgroup=sector, showlegend=show_legend,
                    line=dict(color=sector_color[sector]),
                ), row=ri, col=ci)

    fig.update_layout(
        height=max(400, 250 * n_rows),
        yaxis_title="Price increase (%)",
        xaxis_title="Time step",
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 8: Weighted rationing by sector
# ======================================================================


def _section_rationing_by_sector(df_firm: pd.DataFrame) -> str:
    html = ["<h2>8. Rationing by Sector</h2>",
            '<p class="section-note">Production-weighted average rationing rate. '
            '1.0 = all orders fulfilled; &lt;1 = supply shortfall.</p>']

    df = df_firm.copy()
    # Use t=0 production as the "normal" weight for meaningful averaging
    baseline = df[df["time_step"] == 0][["firm", "production"]].rename(
        columns={"production": "baseline_production"})
    df = df.merge(baseline, on="firm", how="left")
    df["baseline_production"] = df["baseline_production"].fillna(0)

    df["weighted_rat"] = df["rationing"] * df["baseline_production"]
    agg = df.groupby(["time_step", "sector"]).agg(
        weighted_rat=("weighted_rat", "sum"),
        total_weight=("baseline_production", "sum"),
    ).reset_index()
    agg["avg_rationing"] = agg["weighted_rat"] / agg["total_weight"].replace(0, np.nan)

    sectors = sorted(agg["sector"].unique())
    fig = go.Figure()
    for i, sector in enumerate(sectors):
        sub = agg[agg["sector"] == sector]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["avg_rationing"],
            mode="lines+markers", name=sector,
            line=dict(color=_SECTOR_COLORS[i % len(_SECTOR_COLORS)]),
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title="Rationing rate (1 = no shortage)",
        yaxis_range=[
            max(0, agg["avg_rationing"].min() - 0.05),
            1.02,
        ],
        height=500,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 9: Capacity utilization by sector
# ======================================================================


def _section_capacity_utilization(df_firm: pd.DataFrame) -> str:
    html = ["<h2>9. Capacity Utilization by Sector</h2>",
            '<p class="section-note">production / production_capacity, '
            'averaged per sector (production-weighted).</p>']

    df = df_firm.copy()
    df["utilization"] = df["production"] / df["production_capacity"].replace(0, np.nan)
    df["weighted_util"] = df["utilization"] * df["production"]

    agg = df.groupby(["time_step", "sector"]).agg(
        weighted_util=("weighted_util", "sum"),
        total_prod=("production", "sum"),
    ).reset_index()
    agg["avg_utilization"] = agg["weighted_util"] / agg["total_prod"].replace(0, np.nan)

    sectors = sorted(agg["sector"].unique())
    fig = go.Figure()
    for i, sector in enumerate(sectors):
        sub = agg[agg["sector"] == sector]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["avg_utilization"],
            mode="lines+markers", name=sector,
            line=dict(color=_SECTOR_COLORS[i % len(_SECTOR_COLORS)]),
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title="Capacity utilization (production / capacity)",
        height=500,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 10: Input shortfall by sector
# ======================================================================


def _section_input_shortfall(df_firm: pd.DataFrame) -> str:
    html = ["<h2>10. Input Sourcing Rate by Sector</h2>",
            '<p class="section-note">total_input / production_target ratio, '
            'production-weighted average. Shows how well firms source inputs '
            'relative to what they need to produce.</p>']

    df = df_firm.copy()
    df["input_ratio"] = df["total_input"] / df["production_target"].replace(0, np.nan)
    # Clip for display (some firms may have 0 target)
    df["input_ratio"] = df["input_ratio"].clip(upper=2.0)
    df["weighted_ir"] = df["input_ratio"] * df["production"]

    agg = df.groupby(["time_step", "sector"]).agg(
        weighted_ir=("weighted_ir", "sum"),
        total_prod=("production", "sum"),
    ).reset_index()
    agg["avg_input_ratio"] = agg["weighted_ir"] / agg["total_prod"].replace(0, np.nan)

    sectors = sorted(agg["sector"].unique())
    fig = go.Figure()
    for i, sector in enumerate(sectors):
        sub = agg[agg["sector"] == sector]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["avg_input_ratio"],
            mode="lines+markers", name=sector,
            line=dict(color=_SECTOR_COLORS[i % len(_SECTOR_COLORS)]),
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title="Input sourcing rate (total_input / production_target)",
        height=500,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 11: Loss concentration
# ======================================================================


def _section_loss_concentration(df_hh: pd.DataFrame, mu: str) -> str:
    html = ["<h2>11. Loss Concentration across Households</h2>",
            '<p class="section-note">Cumulative share of total loss across '
            'households, sorted from largest to smallest loser. '
            'Uses total (time-summed) loss per household.</p>']

    df = df_hh.copy()
    df["total_loss"] = df["consumption_loss"] + df["extra_spending"]
    per_hh = df.groupby("household")["total_loss"].sum().sort_values(ascending=False)

    # Lorenz-style cumulative share
    total = per_hh.sum()
    if total <= 0:
        return "<h2>11. Loss Concentration</h2><p>No losses recorded.</p>"

    cumshare = per_hh.cumsum() / total * 100
    n = len(per_hh)
    x_pct = np.arange(1, n + 1) / n * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_pct, y=cumshare.values,
        mode="lines", name="Cumulative loss share",
        fill="tozeroy",
        line=dict(color="#e74c3c"),
    ))
    # Perfect equality line
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode="lines", name="Perfect equality",
        line=dict(dash="dash", color="#bdc3c7"),
    ))

    fig.update_layout(
        xaxis_title="% of households (sorted by loss, descending)",
        yaxis_title="Cumulative % of total loss",
        height=400,
    )

    html.append(fig_to_div(fig))

    # Top-10 bar chart
    top10 = per_hh.head(10).reset_index()
    top10.columns = ["household", "total_loss"]
    # Add region info
    region_map = df_hh.drop_duplicates("household").set_index("household")["region"]
    top10["label"] = top10["household"] + " (" + top10["household"].map(region_map) + ")"

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=top10["label"], y=top10["total_loss"],
        marker_color="#e74c3c",
    ))
    fig2.update_layout(
        xaxis_title="Household",
        yaxis_title=f"Total loss ({mu})",
        height=350,
        title="Top 10 households by cumulative loss",
    )
    html.append(fig_to_div(fig2))

    return "\n".join(html)


# ======================================================================
# Section 12: Recovery trajectory
# ======================================================================


def _section_recovery_trajectory(df_firm: pd.DataFrame) -> str:
    html = ["<h2>12. Recovery Trajectory</h2>",
            '<p class="section-note">Key metrics as % deviation from t=0 baseline, '
            'aggregated across all firms. Shows disruption impact and recovery.</p>']

    df = df_firm.copy()

    # Compute baselines at t=0
    baseline_prod = df[df["time_step"] == 0]["production"].sum()
    baseline_price = 1.0  # equilibrium price is normalized to 1

    # Per-timestep aggregates
    ts_agg = df.groupby("time_step").agg(
        total_production=("production", "sum"),
        avg_price=("price", "mean"),
        avg_rationing=("rationing", "mean"),
    ).reset_index()

    fig = go.Figure()

    # Production deviation (%)
    prod_dev = (ts_agg["total_production"] / baseline_prod - 1) * 100
    fig.add_trace(go.Scatter(
        x=ts_agg["time_step"], y=prod_dev,
        mode="lines+markers", name="Production",
        line=dict(color="#2ecc71"),
    ))

    # Price deviation (%)
    price_dev = (ts_agg["avg_price"] / baseline_price - 1) * 100
    fig.add_trace(go.Scatter(
        x=ts_agg["time_step"], y=price_dev,
        mode="lines+markers", name="Average price",
        line=dict(color="#e74c3c"),
    ))

    # Rationing deviation (%)
    rat_dev = (ts_agg["avg_rationing"] - 1) * 100
    fig.add_trace(go.Scatter(
        x=ts_agg["time_step"], y=rat_dev,
        mode="lines+markers", name="Rationing",
        line=dict(color="#3498db"),
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="#bdc3c7",
                  annotation_text="Baseline")

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title="% deviation from baseline",
        height=450,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)


# ======================================================================
# Section 13: Propagation heatmap
# ======================================================================


def _section_propagation_heatmap(df_firm: pd.DataFrame) -> str:
    html = ["<h2>13. Disruption Propagation Heatmap</h2>",
            '<p class="section-note">Production loss as % below t=0 baseline, '
            'by region and time step. Darker = larger drop.</p>']

    df = df_firm.copy()

    # Baseline production per region
    baseline = df[df["time_step"] == 0].groupby("region")["production"].sum()
    baseline.name = "baseline"

    # Production per region per timestep
    ts_region = df.groupby(["time_step", "region"])["production"].sum().reset_index()
    ts_region = ts_region.merge(baseline, on="region")
    ts_region["pct_loss"] = (1 - ts_region["production"] / ts_region["baseline"].replace(0, np.nan)) * 100

    # Pivot for heatmap: rows=region, cols=timestep
    pivot = ts_region.pivot(index="region", columns="time_step", values="pct_loss")
    pivot = pivot.fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"t={t}" for t in pivot.columns],
        y=pivot.index.tolist(),
        colorscale="Reds",
        colorbar_title="% production<br>loss",
        zmin=0,
        text=np.round(pivot.values, 1),
        texttemplate="%{text}%",
        hovertemplate="Region: %{y}<br>Time: %{x}<br>Loss: %{z:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title="Region",
        height=max(300, 50 * len(pivot)),
    )
    html.append(fig_to_div(fig))

    # Also do sector x time heatmap
    html.append("<h3>By Sector</h3>")
    baseline_s = df[df["time_step"] == 0].groupby("sector")["production"].sum()
    baseline_s.name = "baseline"

    ts_sector = df.groupby(["time_step", "sector"])["production"].sum().reset_index()
    ts_sector = ts_sector.merge(baseline_s, on="sector")
    ts_sector["pct_loss"] = (1 - ts_sector["production"] / ts_sector["baseline"].replace(0, np.nan)) * 100

    pivot_s = ts_sector.pivot(index="sector", columns="time_step", values="pct_loss")
    pivot_s = pivot_s.fillna(0)

    fig2 = go.Figure(data=go.Heatmap(
        z=pivot_s.values,
        x=[f"t={t}" for t in pivot_s.columns],
        y=pivot_s.index.tolist(),
        colorscale="Reds",
        colorbar_title="% production<br>loss",
        zmin=0,
        text=np.round(pivot_s.values, 1),
        texttemplate="%{text}%",
        hovertemplate="Sector: %{y}<br>Time: %{x}<br>Loss: %{z:.1f}%<extra></extra>",
    ))

    fig2.update_layout(
        xaxis_title="Time step",
        yaxis_title="Sector",
        height=max(400, 35 * len(pivot_s)),
    )
    html.append(fig_to_div(fig2))

    return "\n".join(html)


# ======================================================================
# Section 14: Inventory levels by input sector
# ======================================================================


def _section_inventory_by_input_sector(df_inv: pd.DataFrame) -> str:
    html = ["<h2>14. Inventory Levels by Input Sector</h2>",
            '<p class="section-note">Average inventory in days, weighted by '
            'equilibrium input need (eq_need), grouped by input sector '
            '(aggregated across regions).</p>']

    df = df_inv.copy()
    # Strip region prefix from input_sector (e.g., "ARE_Trade" → "Trade")
    df["sector"] = df["input_sector"].str.split("_", n=1).str[1]
    # Weighted average: weight by eq_need
    df["weighted_days"] = df["inventory_days"] * df["eq_need"]
    agg = df.groupby(["time_step", "sector"]).agg(
        weighted_days=("weighted_days", "sum"),
        total_need=("eq_need", "sum"),
    ).reset_index()
    agg["avg_inventory_days"] = agg["weighted_days"] / agg["total_need"].replace(0, np.nan)

    sectors = sorted(agg["sector"].unique())
    fig = go.Figure()
    for i, sector in enumerate(sectors):
        sub = agg[agg["sector"] == sector]
        fig.add_trace(go.Scatter(
            x=sub["time_step"], y=sub["avg_inventory_days"],
            mode="lines+markers", name=sector,
            line=dict(color=_SECTOR_COLORS[i % len(_SECTOR_COLORS)]),
        ))

    fig.update_layout(
        xaxis_title="Time step",
        yaxis_title="Inventory level (days)",
        height=500,
    )
    html.append(fig_to_div(fig))
    return "\n".join(html)
