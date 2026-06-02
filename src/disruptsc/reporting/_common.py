"""Shared helpers for DisruptSC HTML reports."""

from __future__ import annotations

import logging
import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yaml

log = logging.getLogger(__name__)

# ── Data loaders ─────────────────────────────────────────────────────

def load_params(folder: Path) -> dict:
    path = folder / "parameters.yaml"
    if not path.exists():
        log.warning(f"parameters.yaml not found in {folder}")
        return {}
    with open(path, encoding="utf-8") as f:
        content = f.read()
    try:
        return yaml.safe_load(content) or {}
    except yaml.YAMLError:
        return yaml.unsafe_load(content) or {}


def load_csv(path: Path, **kwargs) -> pd.DataFrame | None:
    if not path.exists():
        log.warning(f"File not found: {path.name}")
        return None
    return pd.read_csv(path, **kwargs)


def load_geodata(path: Path) -> gpd.GeoDataFrame | None:
    if not path.exists():
        log.warning(f"File not found: {path.name}")
        return None
    return gpd.read_file(path)


# ── Parameter helpers ────────────────────────────────────────────────

def time_scale_factor(params: dict) -> float:
    """Factor to convert per-timestep values to annual."""
    res = params.get("time_resolution", "week")
    return {"day": 365, "week": 52, "month": 12, "year": 1}.get(res, 52)


def monetary_label(params: dict) -> str:
    return params.get("monetary_units_in_model", "mUSD")


_UNIT_VALUES = {"USD": 1, "kUSD": 1e3, "mUSD": 1e6}


def mrio_to_model_annual(params: dict) -> float:
    """Factor to convert MRIO values (data_units/year) to model_units/year."""
    data_u = _UNIT_VALUES.get(params.get("monetary_units_in_data", "mUSD"), 1e6)
    model_u = _UNIT_VALUES.get(params.get("monetary_units_in_model", "mUSD"), 1e6)
    return data_u / model_u


# ── Flow map helpers ─────────────────────────────────────────────────

MODE_COLORS = {
    "roads": "#636EFA",
    "maritime": "#00CC96",
    "airways": "#EF553B",
    "railways": "#AB63FA",
    "pipelines": "#FFA15A",
    "multimodal": "#19D3F3",
    "waterways": "#FF6692",
}


def detect_cargo_types(gdf: gpd.GeoDataFrame) -> list[str]:
    """Return cargo types present as columns in the GeoDataFrame.

    Scans for `tons_<cargo_type>` columns dynamically — works with the
    standard {container, dry_bulk, liquid_bulk} set and with single
    "any" bucket (when use_cargo_types is disabled). Excludes columns
    like `tons_pct` that share the prefix but aren't cargo-type buckets.
    """
    skip = {"tons_pct"}
    return sorted(
        col[len("tons_"):] for col in gdf.columns
        if col.startswith("tons_") and col not in skip
    )


def add_flow_traces(fig, gdf, value_col, lon_range, lat_range,
                    row, col, value_label="", max_value=None,
                    max_width=3.0, exponent=0.57, min_width=0.1):
    """Add flow lines to a scattergeo subplot with QGIS-style width scaling.

        width = max_width * (value / max_value) ** exponent

    Defaults (max_width=3, exponent=0.57) match the QGIS data-driven
    linewidth most commonly used for transport flow maps.

    If *max_value* is given, the scale is normalised against that global
    maximum so multiple subplots share the same visual scale.
    """
    if value_col not in gdf.columns:
        return

    has_flow = gdf[value_col].fillna(0) > 0
    gdf_flow = gdf[has_flow].copy()

    if gdf_flow.empty:
        return

    vals = gdf_flow[value_col].values.astype(float)
    vmax = max_value if max_value is not None else vals.max()
    if vmax > 0:
        widths = max_width * np.power(vals / vmax, exponent)
        widths = np.maximum(widths, min_width)
    else:
        widths = np.full_like(vals, min_width)

    for mode, color in MODE_COLORS.items():
        mask = gdf_flow["type"] == mode
        if not mask.any():
            continue
        subset = gdf_flow[mask]
        sub_widths = widths[mask.values]

        for idx, (_, edge) in enumerate(subset.iterrows()):
            coords = list(edge.geometry.coords)
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            val = edge[value_col]
            name = edge.get("name", "") or ""
            eid = edge.get("id", "")
            hover = f"{name} (id={eid})<br>{value_label}: {val:,.1f}<br>type: {mode}"

            fig.add_trace(
                go.Scattergeo(
                    lon=lons, lat=lats,
                    mode="lines",
                    line=dict(width=sub_widths[idx], color=color),
                    hovertext=hover,
                    hoverinfo="text",
                    showlegend=False,
                ),
                row=row, col=col,
            )


def apply_geo_layout(fig, lon_range, lat_range, n_rows, n_cols=2):
    """Apply consistent geo settings to all subplots."""
    for i in range(1, n_rows * n_cols + 1):
        geo_key = f"geo{i}" if i > 1 else "geo"
        fig.update_layout(**{
            geo_key: dict(
                scope="world",
                projection_type="mercator",
                lonaxis_range=lon_range,
                lataxis_range=lat_range,
                showland=True, landcolor="rgb(243, 243, 243)",
                showocean=True, oceancolor="rgb(220, 230, 242)",
                showcountries=True, countrycolor="rgb(180, 180, 180)",
                showcoastlines=True, coastlinecolor="rgb(180, 180, 180)",
                showlakes=True, lakecolor="rgb(220, 230, 242)",
                fitbounds=False,
            )
        })


def fig_to_div(fig, height=500) -> str:
    """Convert a plotly figure to an embeddable HTML div."""
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       config={"responsive": True})


# ── Table helpers ────────────────────────────────────────────────────

def df_to_html(df: pd.DataFrame, fmt_nums=True,
               highlight_col=None, threshold=100) -> str:
    """Render a DataFrame as a styled HTML table.

    If *highlight_col* is set, cells exceeding *threshold* are highlighted red.
    """
    df = df.reset_index(drop=True)
    rows = ["<table>"]
    rows.append("<tr>" + "".join(f"<th>{c}</th>" for c in df.columns) + "</tr>")

    for _, row in df.iterrows():
        cells = []
        for c in df.columns:
            val = row[c]
            style = ""
            if highlight_col and c == highlight_col and threshold is not None:
                try:
                    if float(val) > threshold:
                        style = ' style="background:#f8d7da; font-weight:bold;"'
                except (ValueError, TypeError):
                    pass
            cells.append(f"<td{style}>{_fmt(val, fmt_nums)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    rows.append("</table>")
    return "\n".join(rows)


def _fmt(val, fmt_nums=True) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return ""
    if not fmt_nums:
        return str(val)
    if isinstance(val, float):
        if abs(val) >= 1000:
            return f"{val:,.0f}"
        elif abs(val) >= 1:
            return f"{val:,.1f}"
        elif abs(val) >= 0.01:
            return f"{val:,.2f}"
        elif val == 0:
            return "0"
        else:
            return f"{val:.2e}"
    return str(val)


def pct_dev(model: pd.Series, data: pd.Series) -> pd.Series:
    """Percentage deviation: (model - data) / data * 100."""
    return ((model - data) / data.replace(0, float("nan")) * 100).round(1)


def warn_box(msg: str) -> str:
    return f'<div class="warning">{msg}</div>'


def ok_box(msg: str) -> str:
    return f'<div class="ok">{msg}</div>'
