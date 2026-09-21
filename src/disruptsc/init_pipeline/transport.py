"""Build the multimodal transport network from a GeoPackage file."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd

import pandas as pd

from disruptsc.network.mrio import rescale_monetary_values
from disruptsc.network.transport_network import TransportNetwork


def build_transport_network(transport_modes: list, filepaths: dict,
                            logistics_params: dict, time_resolution: str,
                            capacity_overrides: dict = None,
                            cargo_mode_eligibility: dict = None,
                            use_cargo_types: bool = True) -> tuple[TransportNetwork, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Build transport network from a GeoPackage file.

    Expects *filepaths["transport"]* to point to a ``.gpkg`` file with one
    layer per transport mode (layer names must match the mode names in
    *transport_modes*, e.g. ``roads``, ``maritime``, ``multimodal``).

    *capacity_overrides* (``transport_capacity_overrides``: edge name -> tons/day,
    or {cargo type: tons/day}) are the ONLY capacities of the network; an edge
    that is not named has none. *cargo_mode_eligibility* ({mode: [cargo types]})
    says which cargo may use which mode (no bulk by air, only liquid bulk in
    pipelines); both are validated here and raise on unknown names, modes or
    cargo types (21 Sep 2026: a misspelt override name used to be ignored).

    Returns (transport_network, transport_edges, transport_nodes).
    """
    all_edges = []
    id_offset = 0

    gpkg_path = filepaths.get("transport")
    if gpkg_path is None or not Path(gpkg_path).exists():
        raise FileNotFoundError(
            f"Transport GeoPackage not found: {gpkg_path}. "
            f"Expected a .gpkg file at filepaths['transport']."
        )

    available_layers = set(gpd.list_layers(gpkg_path)["name"])
    logging.info(f"Loading transport from {gpkg_path} "
                 f"(layers: {sorted(available_layers)})")

    for mode in transport_modes:
        if mode == "multimodal":
            continue  # loaded after other modes
        if mode not in available_layers:
            logging.warning(f"Layer '{mode}' not found in {gpkg_path}")
            continue

        edges = _load_transport_edges(gpkg_path, mode, time_resolution, layer=mode)
        edges["id"] = edges["id"] + id_offset
        id_offset = edges["id"].max() + 1
        all_edges.append(edges)
        logging.info(f"Loaded {len(edges)} {mode} edges")

    # Multimodal layer — from separate file if provided, else from main gpkg
    mm_gpkg = filepaths.get("multimodal")
    if mm_gpkg is not None and Path(mm_gpkg).exists():
        mm_edges = _load_transport_edges(mm_gpkg, "multimodal", time_resolution,
                                         layer="multimodal")
        logging.info(f"Loading multimodal edges from {mm_gpkg}")
    elif "multimodal" in available_layers:
        mm_edges = _load_transport_edges(gpkg_path, "multimodal", time_resolution,
                                         layer="multimodal")
    else:
        mm_edges = None

    if mm_edges is not None:
        if "multimodes" in mm_edges.columns:
            mm_edges = mm_edges[mm_edges["multimodes"].apply(
                lambda m: _multimodal_relevant(m, transport_modes) if isinstance(m, str) else True
            )]
        mm_edges["id"] = mm_edges["id"] + id_offset
        all_edges.append(mm_edges)
        logging.info(f"Loaded {len(mm_edges)} multimodal edges")

    if not all_edges:
        raise ValueError("No transport edges loaded")

    edges_gdf = pd.concat([df.dropna(axis=1, how="all") for df in all_edges], ignore_index=True)
    edges_gdf = gpd.GeoDataFrame(edges_gdf, geometry="geometry")

    # Guard: edge IDs must be unique (duplicate IDs break the flow export merge)
    dup_ids = edges_gdf[edges_gdf.duplicated(subset="id", keep=False)]
    if not dup_ids.empty:
        n_dups = dup_ids["id"].nunique()
        logging.warning(f"{n_dups} duplicate edge IDs found — reassigning all IDs sequentially. "
                        f"Fix the source data (e.g. re-run build_transport.py) to silence this warning.")
        edges_gdf["id"] = range(len(edges_gdf))

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

    # Determine cargo types. Single "any" bucket when cargo types are
    # disabled — Dijkstra/LP will run once instead of once per type.
    if use_cargo_types:
        cargo_types = list(logistics_params.get("sector_to_cargo_type", {}).values())
        cargo_types = sorted(set(ct for ct in cargo_types if ct != "default"))
        if not cargo_types:
            cargo_types = ["container", "dry_bulk", "liquid_bulk"]
    else:
        cargo_types = ["any"]
        logging.info("Cargo types disabled — using a single 'any' bucket")

    for _, row in edges_gdf.iterrows():
        u, v = int(row["end1"]), int(row["end2"])
        edge_data = row.to_dict()
        edge_data["node_tuple"] = (u, v)
        edge_data["shipments"] = {}
        edge_data["disruption_duration"] = 0
        tn.add_edge(u, v, **edge_data)

    # Capacities: the named overrides only (validated), then the cost labels
    # (a cargo excluded by eligibility or blocked by a 0 capacity gets none)
    eligibility = _validate_cargo_mode_eligibility(cargo_mode_eligibility, cargo_types, use_cargo_types)
    if capacity_overrides:
        _apply_capacity_overrides(tn, capacity_overrides, cargo_types, time_resolution, use_cargo_types)

    # Ingest logistics cost parameters
    tn.ingest_logistic_data(logistics_params, use_cargo_types=use_cargo_types,
                            cargo_mode_eligibility=eligibility)

    # Set min cost for heuristic
    min_costs = [v for v in logistics_params["basic_cost"].values() if isinstance(v, (int, float))]
    tn.min_cost_per_tonkm = min(min_costs) if min_costs else 0.001

    logging.info(tn.info())
    tn.log_km_per_transport_modes()

    return tn, edges_gdf, nodes_gdf


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _load_transport_edges(filepath: Path, mode: str, time_resolution: str,
                          layer: str | None = None) -> gpd.GeoDataFrame:
    """Load transport edges from a GeoPackage layer and standardize columns."""
    gdf = gpd.read_file(filepath, layer=layer)

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
                         ("class", ""), ("disruption", 0),
                         ("multimodes", None)]:
        if col not in gdf.columns:
            gdf[col] = default

    # Capacity columns of the GeoPackage are not an input (21 Sep 2026): they
    # were overwritten by the per-mode defaults in every case, and the
    # per-edge capacities of a scope live in transport_capacity_overrides,
    # keyed by edge name. Drop them so that they never reach the edge dicts.
    _ = time_resolution
    cap_cols = [c for c in gdf.columns if c == "capacity" or c.startswith("capacity_")]
    if cap_cols:
        logging.info(f"{layer or mode}: GeoPackage column(s) {cap_cols} ignored - "
                     f"edge capacities come from transport_capacity_overrides only")
        gdf = gdf.drop(columns=cap_cols)

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


def _validate_cargo_mode_eligibility(eligibility: dict | None, cargo_types: list,
                                     use_cargo_types: bool) -> dict | None:
    """``cargo_mode_eligibility`` as {mode: set of cargo types}, validated.

    A mode not listed takes every cargo; a listed mode takes only the listed
    cargo types. Unknown cargo types raise (a typo would silently close a mode
    to a cargo class). With ``use_cargo_types: False`` there is one "any" cargo
    and the table cannot apply: it is ignored with a message.
    """
    if not eligibility:
        return None
    if not use_cargo_types:
        logging.info("cargo_mode_eligibility ignored: use_cargo_types is False (one 'any' cargo)")
        return None
    if not isinstance(eligibility, dict):
        raise ValueError(f"cargo_mode_eligibility must be a mapping mode -> [cargo types] (got {eligibility!r})")
    out = {}
    for mode, allowed in eligibility.items():
        if isinstance(allowed, str):
            allowed = [allowed]
        if allowed is None:
            allowed = []
        try:
            allowed = [str(a) for a in allowed]
        except TypeError:
            raise ValueError(f"cargo_mode_eligibility['{mode}'] must be a list of cargo types (got {allowed!r})")
        unknown = sorted(set(allowed) - set(cargo_types))
        if unknown:
            raise ValueError(
                f"cargo_mode_eligibility['{mode}'] names unknown cargo type(s) {unknown}; "
                f"the cargo types of this scope (logistics.sector_to_cargo_type) are {sorted(cargo_types)}"
            )
        out[str(mode)] = set(allowed)
    return out


def _apply_capacity_overrides(tn: TransportNetwork, overrides: dict,
                              cargo_types: list, time_resolution: str,
                              use_cargo_types: bool = True):
    """Set edge capacities by edge name (the only capacity channel).

    *overrides* maps edge name to either:
      - a number  -> shared capacity (tons/day, all cargo types together)
      - a dict    -> per-cargo-type capacity (tons/day); an explicit 0 BLOCKS
                     that cargo on the edge, a cargo not listed has no
                     capacity there (unlimited)

    Every edge carrying the name gets the value (a terminal usually has a road
    and a rail connector: the value is per edge, two-way). A name that matches
    no edge, a cargo type outside the scope's, or a negative value raise: a
    silent no-op here was a calibration error waiting to happen (Gulf, 2026).
    """
    time_factor = {"day": 1, "week": 7, "month": 30, "year": 365}.get(time_resolution, 7)
    by_name: dict[str, list] = {}
    for u, v in tn.edges:
        name = tn[u][v].get("name", "")
        if isinstance(name, str) and name:
            by_name.setdefault(name, []).append(tn[u][v])

    for name, override in overrides.items():
        edges = by_name.get(str(name))
        if not edges:
            raise ValueError(
                f"transport_capacity_overrides['{name}'] matches no edge of the transport "
                f"network (edge names are the 'name' column of the GeoPackage layers)"
            )
        if isinstance(override, dict):
            if not use_cargo_types:
                raise ValueError(
                    f"transport_capacity_overrides['{name}'] is per cargo type but "
                    f"use_cargo_types is False; give a single number"
                )
            unknown = sorted(set(map(str, override)) - set(cargo_types))
            if unknown:
                raise ValueError(
                    f"transport_capacity_overrides['{name}'] names unknown cargo type(s) {unknown}; "
                    f"the cargo types of this scope are {sorted(cargo_types)}"
                )
            values = {str(ct): float(val) for ct, val in override.items()}
        else:
            values = {"": float(override)}
        for key, val in values.items():
            if val < 0 or val != val:
                raise ValueError(f"transport_capacity_overrides['{name}']: capacity must be >= 0 (got {val!r})")
        for edge in edges:
            for ct, val in values.items():
                edge["capacity" if ct == "" else f"capacity_{ct}"] = val * time_factor
        logging.info(f"capacity override '{name}': {len(edges)} edge(s), "
                     + ", ".join(f"{ct or 'all cargo'} {val:,.0f} t/day" for ct, val in values.items()))
