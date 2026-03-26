"""Build the multimodal transport network from GeoJSON files."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from disruptsc.network.mrio import rescale_monetary_values
from disruptsc.network.transport_network import TransportNetwork


def build_transport_network(transport_modes: list, filepaths: dict,
                            logistics_params: dict, time_resolution: str,
                            capacity_overrides: dict = None) -> tuple[TransportNetwork, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Build transport network from GeoJSON edge files.

    Returns (transport_network, transport_edges, transport_nodes).
    """
    # Load and merge all edge files
    all_edges = []
    id_offset = 0

    mode_file_map = {
        "roads": "roads_edges",
        "railways": "railways_edges",
        "waterways": "waterways_edges",
        "airways": "airways_edges",
        "maritime": "maritime_edges",
        "pipelines": "pipelines_edges",
    }

    for mode in transport_modes:
        if mode == "multimodal":
            continue  # loaded separately
        file_key = mode_file_map.get(mode)
        if not file_key or filepaths.get(file_key) is None:
            logging.warning(f"No file for transport mode: {mode}")
            continue
        filepath = filepaths[file_key]
        if not Path(filepath).exists():
            logging.warning(f"Transport file not found: {filepath}")
            continue

        edges = _load_transport_edges(filepath, mode, time_resolution)
        edges["id"] = edges["id"] + id_offset
        id_offset = edges["id"].max() + 1
        all_edges.append(edges)
        logging.info(f"Loaded {len(edges)} {mode} edges")

    # Load multimodal edges (always present if multiple modes)
    mm_key = "multimodal_edges"
    if filepaths.get(mm_key) and Path(filepaths[mm_key]).exists():
        mm_edges = _load_transport_edges(filepaths[mm_key], "multimodal", time_resolution)
        # Filter multimodal by available modes
        if "multimodes" in mm_edges.columns:
            mm_edges = mm_edges[mm_edges["multimodes"].apply(
                lambda m: _multimodal_relevant(m, transport_modes) if isinstance(m, str) else True
            )]
        mm_edges["id"] = mm_edges["id"] + id_offset
        all_edges.append(mm_edges)
        logging.info(f"Loaded {len(mm_edges)} multimodal edges")

    if not all_edges:
        raise ValueError("No transport edges loaded")

    edges_gdf = pd.concat(all_edges, ignore_index=True)
    edges_gdf = gpd.GeoDataFrame(edges_gdf, geometry="geometry")

    # Create nodes from edge endpoints
    nodes_gdf, edges_gdf = _create_nodes_and_update_edges(edges_gdf)

    # Build network
    tn = TransportNetwork()
    for node_id, row in nodes_gdf.iterrows():
        tn.add_node(node_id, **{
            "id": node_id,
            "long": row["geometry"].x,
            "lat": row["geometry"].y,
            "geometry": row["geometry"],
            "shipments": {},
            "disruption_duration": 0,
            "firms_there": [],
            "households_there": None,
            "type": "road",
            **({"special": row["special"]} if "special" in nodes_gdf.columns else {}),
            **({"name": row["name"]} if "name" in nodes_gdf.columns else {}),
        })

    for _, row in edges_gdf.iterrows():
        u, v = int(row["end1"]), int(row["end2"])
        edge_data = row.to_dict()
        edge_data["node_tuple"] = (u, v)
        edge_data["shipments"] = {}
        edge_data["disruption_duration"] = 0
        edge_data["current_load"] = 0
        edge_data["overused"] = False
        edge_data["current_capacity"] = edge_data.get("capacity", 1e9)
        tn.add_edge(u, v, **edge_data)

    # Apply capacity overrides
    if capacity_overrides:
        _apply_capacity_overrides(tn, capacity_overrides, time_resolution)

    # Prepare cost profiles and ingest logistics
    _prepare_cost_profiles(logistics_params)
    tn.ingest_logistic_data(logistics_params, time_resolution)

    # Set min cost for heuristic
    min_costs = [v for v in logistics_params["basic_cost"].values() if isinstance(v, (int, float))]
    tn.min_cost_per_tonkm = min(min_costs) if min_costs else 0.001

    logging.info(tn.info())
    tn.log_km_per_transport_modes()

    return tn, edges_gdf, nodes_gdf


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _load_transport_edges(filepath: Path, mode: str, time_resolution: str) -> gpd.GeoDataFrame:
    """Load a GeoJSON transport edge file and standardize columns."""
    gdf = gpd.read_file(filepath)

    # Ensure required columns
    if "id" not in gdf.columns:
        gdf["id"] = range(len(gdf))
    if "type" not in gdf.columns:
        gdf["type"] = mode

    # Calculate km from geometry if missing or has NaN values
    if "km" not in gdf.columns or gdf["km"].isna().any():
        gdf_proj = gdf.to_crs(epsg=8857)
        km_from_geom = gdf_proj.geometry.length / 1000
        if "km" not in gdf.columns:
            gdf["km"] = km_from_geom
        else:
            gdf["km"] = gdf["km"].fillna(km_from_geom)

    # Fill missing optional columns
    for col, default in [("special", None), ("name", ""), ("surface", ""),
                         ("class", ""), ("capacity", 1e9), ("disruption", 0),
                         ("multimodes", None)]:
        if col not in gdf.columns:
            gdf[col] = default

    # Adapt capacity to time resolution
    if "capacity" in gdf.columns:
        time_factor = {"day": 1, "week": 7, "month": 30, "year": 365}.get(time_resolution, 7)
        gdf["capacity"] = pd.to_numeric(gdf["capacity"], errors="coerce").fillna(1e9) * time_factor
        gdf.loc[gdf["capacity"] == 0, "capacity"] = 1e9

    return gdf


def _create_nodes_and_update_edges(edges: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Extract unique nodes from edge endpoints, assign IDs."""
    from shapely.geometry import Point

    # Extract endpoints
    endpoints = []
    for idx, row in edges.iterrows():
        geom = row.geometry
        start = Point(round(geom.coords[0][0], 6), round(geom.coords[0][1], 6))
        end = Point(round(geom.coords[-1][0], 6), round(geom.coords[-1][1], 6))
        endpoints.append((idx, "start", start))
        endpoints.append((idx, "end", end))

    # Deduplicate by WKT
    wkt_to_id = {}
    nodes = []
    next_id = 0
    for _, pos, pt in endpoints:
        wkt = pt.wkt
        if wkt not in wkt_to_id:
            wkt_to_id[wkt] = next_id
            nodes.append({"id": next_id, "geometry": pt})
            next_id += 1

    nodes_gdf = gpd.GeoDataFrame(nodes, geometry="geometry").set_index("id")

    # Map edge endpoints to node IDs
    end1_ids = []
    end2_ids = []
    for idx, row in edges.iterrows():
        geom = row.geometry
        start_wkt = Point(round(geom.coords[0][0], 6), round(geom.coords[0][1], 6)).wkt
        end_wkt = Point(round(geom.coords[-1][0], 6), round(geom.coords[-1][1], 6)).wkt
        end1_ids.append(wkt_to_id[start_wkt])
        end2_ids.append(wkt_to_id[end_wkt])

    edges["end1"] = end1_ids
    edges["end2"] = end2_ids

    # Propagate special/name from edges to nodes where applicable
    for col in ("special", "name"):
        if col in edges.columns:
            nodes_gdf[col] = None
            for _, row in edges.iterrows():
                val = row.get(col)
                if val and isinstance(val, str) and val.strip():
                    for nid in (row["end1"], row["end2"]):
                        if nid in nodes_gdf.index and not nodes_gdf.loc[nid, col]:
                            nodes_gdf.loc[nid, col] = val

    return nodes_gdf, edges


def _multimodal_relevant(multimodes_str: str, transport_modes: list) -> bool:
    """Check if a multimodal edge connects relevant transport modes."""
    parts = multimodes_str.replace("-", " ").split()
    return any(p in transport_modes or p == "roads" for p in parts)


def _apply_capacity_overrides(tn: TransportNetwork, overrides: dict, time_resolution: str):
    """Override edge capacities by edge name."""
    time_factor = {"day": 1, "week": 7, "month": 30, "year": 365}.get(time_resolution, 7)
    for u, v in tn.edges:
        edge = tn[u][v]
        name = edge.get("name", "")
        if name in overrides:
            edge["capacity"] = overrides[name] * time_factor
            edge["current_capacity"] = edge["capacity"]


def _prepare_cost_profiles(logistics_params: dict):
    """Generate basic_cost_profiles from basic_cost and variability."""
    nb_profiles = logistics_params.get("nb_cost_profiles", 1)
    if logistics_params.get("basic_cost_random", False) and nb_profiles > 1:
        variability = logistics_params.get("basic_cost_variability", {})
        profiles = {}
        for i in range(nb_profiles):
            profile = {}
            for mode, base_cost in logistics_params["basic_cost"].items():
                cv = variability.get(mode, 0)
                if cv > 0:
                    sigma2 = np.log(1 + cv ** 2)
                    mu = np.log(base_cost) - sigma2 / 2
                    profile[mode] = float(np.random.lognormal(mu, np.sqrt(sigma2)))
                else:
                    profile[mode] = base_cost
            profiles[i] = profile
    else:
        profiles = {0: dict(logistics_params["basic_cost"])}
        logistics_params["nb_cost_profiles"] = 1

    logistics_params["basic_cost_profiles"] = profiles
