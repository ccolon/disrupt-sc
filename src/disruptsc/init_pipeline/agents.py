"""Create firms, households, and countries from MRIO and spatial data."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from disruptsc.agents.firm import Firm
from disruptsc.agents.household import Household
from disruptsc.agents.country import Country
from disruptsc.network.mrio import Mrio, rescale_monetary_values, _UNITS
from disruptsc.params import AgentParams


# ======================================================================
# Utility functions
# ======================================================================

def find_nearest_node_id(transport_nodes: gpd.GeoDataFrame, gdf: gpd.GeoDataFrame) -> np.ndarray:
    """Find nearest transport node for each geometry in gdf using KDTree."""
    node_coords = np.array([(g.x, g.y) for g in transport_nodes.geometry])
    query_coords = np.array([(g.x, g.y) for g in gdf.geometry])
    tree = cKDTree(node_coords)
    _, indices = tree.query(query_coords)
    return transport_nodes.index.values[indices]


def _get_long_lat(node_ids: pd.Series, transport_nodes: gpd.GeoDataFrame) -> dict:
    """Get long/lat for given node IDs."""
    longs = node_ids.map(lambda nid: transport_nodes.loc[nid, "geometry"].x)
    lats = node_ids.map(lambda nid: transport_nodes.loc[nid, "geometry"].y)
    return {"long": longs, "lat": lats}


# ======================================================================
# Firms
# ======================================================================

def create_firm_table(mrio: Mrio, sector_table: pd.DataFrame,
                      firms_spatial_path: Path | None,
                      households_spatial_path: Path | None,
                      usd_per_ton: dict, transport_nodes: gpd.GeoDataFrame,
                      params: AgentParams) -> pd.DataFrame:
    """Build firm_table DataFrame from MRIO + spatial data."""
    if params.firm_data_type == "transaction_based":
        raise NotImplementedError("Transaction-based firm creation not yet implemented in v2")

    # Phase 1: Base table from MRIO (one firm per region_sector)
    total_output = mrio.get_total_output()
    rows = []
    for rs in mrio.region_sectors:
        region, sector = rs
        rows.append({
            "region": region,
            "sector": sector,
            "region_sector": f"{region}_{sector}",
            "importance": total_output.get(rs, 0),
            "geometry": _get_region_centroid(region, households_spatial_path),
        })
    ft = gpd.GeoDataFrame(rows, geometry="geometry")

    # Phase 2: Integrate disaggregated spatial data if available
    if firms_spatial_path and Path(firms_spatial_path).exists():
        ft = _integrate_spatial_firms(ft, firms_spatial_path, mrio)

    # Phase 3: Handle internal flows (duplicate if needed)
    ft = _handle_internal_flows(ft, mrio, params.io_cutoff)

    # Phase 4: Filter small firms
    ft = _filter_small_firms(ft, mrio, params.cutoff_firm_output, params.monetary_units_in_data)

    # Phase 5: Assign transport nodes
    ft["od_point"] = find_nearest_node_id(transport_nodes, ft)
    coords = _get_long_lat(ft["od_point"], transport_nodes)
    ft["long"] = coords["long"].values
    ft["lat"] = coords["lat"].values

    # Phase 6: Enrich with sector metadata
    if sector_table is not None:
        sector_type_map = sector_table.set_index("sector")["type"].to_dict()
        ft["sector_type"] = ft["sector"].map(sector_type_map).fillna("manufacturing")
    else:
        ft["sector_type"] = "manufacturing"

    # USD per ton
    ft["usd_per_ton"] = ft["region_sector"].map(usd_per_ton).fillna(2864.0)

    # Margins and transport share from MRIO
    margins = mrio.get_margin_per_industry()
    transport_shares = mrio.get_transport_input_share(
        sector_table.set_index("sector")["type"] if sector_table is not None else {},
    )
    ft["target_margin"] = ft.apply(
        lambda r: margins.get((r["region"], r["sector"]), 0.2), axis=1
    )
    ft["transport_share"] = ft.apply(
        lambda r: transport_shares.get((r["region"], r["sector"]), 0.2), axis=1
    )

    # Assign IDs
    ft = ft.reset_index(drop=True)
    ft["id"] = range(len(ft))
    ft["name"] = ft["region_sector"] + "_" + ft.groupby("region_sector").cumcount().astype(str)

    logging.info(f"Created firm table with {len(ft)} firms across {ft['region_sector'].nunique()} region_sectors")
    return ft


def create_firms(firm_table: pd.DataFrame, params: AgentParams) -> dict[str, Firm]:
    """Instantiate Firm objects from firm_table."""
    monetary_unit_factor = _UNITS.get(params.monetary_units_in_model, 1e6)
    firms = {}
    for _, row in firm_table.iterrows():
        # Collect subregion columns
        subregion_kwargs = {col: row[col] for col in firm_table.columns if col.startswith("subregion_")}

        firm = Firm(
            pid=row["id"],
            region=row["region"],
            sector=row["sector"],
            sector_type=row.get("sector_type", "manufacturing"),
            region_sector=row["region_sector"],
            od_point=int(row["od_point"]),
            name=row["name"],
            long=row.get("long"),
            lat=row.get("lat"),
            geometry=row.get("geometry"),
            importance=row.get("importance", 1.0),
            usd_per_ton=row.get("usd_per_ton", 2864.0),
            monetary_unit_factor=monetary_unit_factor,
            target_margin=row.get("target_margin", 0.2),
            transport_share=row.get("transport_share", 0.2),
            utilization_rate=params.utilization_rate,
            inventory_restoration_time=params.inventory_restoration_time,
            capital_to_value_added_ratio=params.capital_to_value_added_ratio,
            subregions=subregion_kwargs,
        )
        firms[firm.pid] = firm

    # Add small coordinate noise for visualization
    for firm in firms.values():
        if firm.long is not None:
            firm.long += np.random.uniform(-0.01, 0.01)
            firm.lat += np.random.uniform(-0.01, 0.01)

    return firms


def load_tech_coefs(firms: dict[str, Firm], mrio: Mrio, io_cutoff: float):
    """Load input_mix (technical coefficients) into each firm."""
    tech_coefs = mrio.get_tech_coef_dict(threshold=io_cutoff)

    # Count firms per region_sector to decide whether to keep diagonal entries
    from collections import Counter
    rs_counts = Counter(f.region_sector for f in firms.values())

    for firm in firms.values():
        coefs = dict(tech_coefs.get(firm.region_sector, {}))
        # Remove self-consumption only when there is a single firm in the
        # region_sector (a firm cannot supply itself).  When there are 2+
        # firms, the diagonal coefficient represents intra-sector trade and
        # another firm in the same region_sector will act as supplier.
        if rs_counts[firm.region_sector] < 2:
            coefs.pop(firm.region_sector, None)
        firm.input_mix = coefs


def load_inventories(firms: dict[str, Firm], inventory_targets: dict,
                     time_resolution: str, sector_table: pd.DataFrame = None):
    """Set inventory duration targets per input sector."""
    definition = inventory_targets.get("definition", "per_input_type")
    values = inventory_targets.get("values", {"default": 30})
    target_unit = inventory_targets.get("unit", "day")

    # Convert target to time_resolution units
    time_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    factor = time_days.get(target_unit, 1) / time_days.get(time_resolution, 7)

    if definition == "per_input_type":
        # Map sector to sector_type
        sector_type_map = {}
        if sector_table is not None:
            sector_type_map = sector_table.set_index("sector")["type"].to_dict()

        for firm in firms.values():
            targets = {}
            for input_id in firm.input_mix:
                # input_id is a region_sector like "ARM_mining"
                input_sector = input_id.split("_", 1)[-1] if "_" in input_id else input_id
                input_type = sector_type_map.get(input_sector, "default")
                duration = values.get(input_type, values.get("default", 30))
                targets[input_id] = duration * factor
            firm.inventory_duration_target = targets


# ======================================================================
# Households
# ======================================================================

def create_household_table(mrio: Mrio, households_spatial_path: Path,
                           transport_nodes: gpd.GeoDataFrame,
                           present_region_sectors: list[str],
                           params: AgentParams,
                           time_resolution: str = "week") -> tuple[pd.DataFrame, dict]:
    """Build household_table and consumption patterns."""
    # Load spatial data
    ht = gpd.read_file(households_spatial_path)

    # Filter to regions in MRIO
    mrio_regions = mrio.regions
    ht = ht[ht["region"].isin(mrio_regions)].copy()

    # Assign transport nodes
    ht["od_point"] = find_nearest_node_id(transport_nodes, ht)
    coords = _get_long_lat(ht["od_point"], transport_nodes)
    ht["long"] = coords["long"].values
    ht["lat"] = coords["lat"].values

    # Assign IDs
    ht = ht.reset_index(drop=True)
    ht["id"] = range(len(ht))
    ht["household"] = "hh_" + ht["id"].astype(str)
    ht["name"] = ht["region"] + "_household" + ht["id"].astype(str)
    if "population" not in ht.columns:
        ht["population"] = 1.0

    # Calculate consumption patterns
    final_demand = mrio.get_final_demand(
        [tuple(rs.split("_", 1)) if isinstance(rs, str) else rs for rs in present_region_sectors]
    )
    # Include import rows
    import_fd = mrio.get_final_demand()
    import_rows = [idx for idx in import_fd.index if idx[1] == mrio.import_label]
    if import_rows:
        final_demand = pd.concat([final_demand, import_fd.loc[import_rows]])

    # Rescale to model time resolution and units
    final_demand = rescale_monetary_values(
        final_demand,
        input_units=params.monetary_units_in_data,
        input_time_resolution="year",
        target_units=params.monetary_units_in_model,
        target_time_resolution=time_resolution,
    )

    # Distribute per household by population proportion in each region
    consumption = {}
    cutoff = _get_absolute_cutoff(params.cutoff_household_demand, params.monetary_units_in_data)

    for hh_idx, hh_row in ht.iterrows():
        region = hh_row["region"]
        pop = hh_row.get("population", 1.0)

        # Total population in this region
        region_mask = ht["region"] == region
        total_pop = ht.loc[region_mask, "population"].sum()
        proportion = pop / total_pop if total_pop > 0 else 0

        # Get final demand for this region
        hh_consumption = {}
        for rs_tuple in final_demand.index:
            rs_region = rs_tuple[0]
            if rs_region != region:
                continue
            rs_name = f"{rs_tuple[0]}_{rs_tuple[1]}"
            demand = final_demand.loc[rs_tuple].sum() * proportion
            if demand > cutoff:
                hh_consumption[rs_name] = demand

        # Also include import demand
        for rs_tuple in import_rows:
            demand_cols = final_demand.columns[final_demand.columns.get_level_values(0) == region]
            if len(demand_cols) > 0:
                demand = final_demand.loc[rs_tuple, demand_cols].sum() * proportion
                rs_name = f"{rs_tuple[0]}_{rs_tuple[1]}"
                if demand > cutoff:
                    hh_consumption[rs_name] = hh_consumption.get(rs_name, 0) + demand

        if hh_consumption:
            consumption[hh_idx] = hh_consumption

    logging.info(f"Created household table with {len(ht)} households, "
                 f"{len(consumption)} with demand above cutoff")
    return ht, consumption


def create_households(household_table: pd.DataFrame,
                      consumption: dict) -> dict[str, Household]:
    """Instantiate Household objects."""
    households = {}
    for idx, row in household_table.iterrows():
        if idx not in consumption:
            continue  # Skip households with no demand
        subregion_kwargs = {col: row[col] for col in household_table.columns if col.startswith("subregion_")}
        hh = Household(
            pid=row["household"],
            region=row["region"],
            od_point=int(row["od_point"]),
            name=row["name"],
            long=row.get("long"),
            lat=row.get("lat"),
            population=row.get("population", 1.0),
            sector_consumption=consumption[idx],
            subregions=subregion_kwargs,
        )
        hh.purchase_plan = dict(consumption[idx])  # Will be updated during supply_chain wiring
        households[hh.pid] = hh
    return households


# ======================================================================
# Countries
# ======================================================================

def create_countries(mrio: Mrio, transport_nodes: gpd.GeoDataFrame,
                     countries_spatial_path: Path, usd_per_ton: dict,
                     time_resolution: str, params: AgentParams,
                     transport_edges: gpd.GeoDataFrame | None = None) -> dict[str, Country]:
    """Create Country objects from MRIO trade data.

    Countries are assigned to the nearest **road** node so that they connect
    to the road network and reach other modes via multimodal edges.
    If *transport_edges* is provided, only nodes that are endpoints of road
    edges are considered; otherwise all transport nodes are used.
    """
    # Identify countries
    buying = set(mrio.external_buying_countries)
    selling = set(mrio.external_selling_countries)
    all_countries = sorted(buying | selling)

    # Filter transport nodes to road-only for country placement
    if transport_edges is not None and "type" in transport_edges.columns:
        road_edges = transport_edges[transport_edges["type"] == "roads"]
        road_node_ids = set(road_edges["end1"].tolist() + road_edges["end2"].tolist())
        country_nodes = transport_nodes[transport_nodes.index.isin(road_node_ids)]
        if country_nodes.empty:
            logging.warning("No road nodes found — falling back to all transport nodes for country placement")
            country_nodes = transport_nodes
        else:
            logging.info(f"Country placement restricted to {len(country_nodes)} road nodes "
                         f"(out of {len(transport_nodes)} total)")
    else:
        country_nodes = transport_nodes

    # Load spatial data
    countries_gdf = gpd.read_file(countries_spatial_path)

    # Extract trade matrices
    # Import table: what external countries sell TO model firms (import supply)
    import_table = mrio.get_import_rows()
    import_table = rescale_monetary_values(
        import_table, input_units=params.monetary_units_in_data,
        input_time_resolution="year",
        target_units=params.monetary_units_in_model,
        target_time_resolution=time_resolution,
    )

    # Export table: what external countries buy FROM model firms (export demand)
    export_label = mrio.export_label
    export_cols = [t for t in mrio.columns if t[1] == export_label]
    export_table = mrio.loc[mrio.region_sectors, export_cols]
    export_table = rescale_monetary_values(
        export_table, input_units=params.monetary_units_in_data,
        input_time_resolution="year",
        target_units=params.monetary_units_in_model,
        target_time_resolution=time_resolution,
    )

    # Build countries
    countries = {}
    total_imports = import_table.sum().sum() if len(import_table) > 0 else 1.0

    for country_code in all_countries:
        # Find spatial data
        match = countries_gdf[countries_gdf["region"] == country_code]
        if match.empty:
            logging.warning(f"No spatial data for country {country_code}, skipping")
            continue

        geom = match.iloc[0].geometry
        centroid = geom.centroid if geom.geom_type != "Point" else geom
        gdf_point = gpd.GeoDataFrame([{"geometry": centroid}], geometry="geometry")
        od_point = int(find_nearest_node_id(country_nodes, gdf_point)[0])

        # Export demand: what this country BUYS from model region-sectors
        qty_purchased = {}
        if country_code in buying and (country_code, export_label) in export_table.columns:
            exp_col = export_table[(country_code, export_label)]
            for rs_tuple, val in exp_col.items():
                if val > 0:
                    qty_purchased[f"{rs_tuple[0]}_{rs_tuple[1]}"] = val

        # Supply importance based on import volumes (what country sells to model)
        supply_importance = 0.0
        if country_code in selling:
            imp_row = import_table.loc[(country_code, mrio.import_label)]
            supply_importance = imp_row.sum() / total_imports if total_imports > 0 else 0

        # USD per ton — look for country-specific or default
        country_upt = 2864.0
        for key, val in usd_per_ton.items():
            if country_code.lower() in key.lower() or "imp" in key.lower():
                country_upt = val
                break

        c = Country(
            pid=country_code,
            region=country_code,
            od_point=od_point,
            name=country_code,
            long=centroid.x,
            lat=centroid.y,
            sector=mrio.import_label or "IMP",
            region_sector=f"{country_code}_{mrio.import_label or 'IMP'}",
            usd_per_ton=country_upt,
            monetary_unit_factor=_UNITS.get(params.monetary_units_in_model, 1e6),
            transport_share=params.country_transport_share,
            supply_importance=supply_importance,
            qty_purchased=qty_purchased,
        )
        countries[c.pid] = c

    # Log export demand summary
    total_export_demand = sum(
        sum(c.qty_purchased.values()) for c in countries.values()
    )
    logging.info(
        f"Created {len(countries)} countries — "
        f"total export demand: {total_export_demand:,.2f} {params.monetary_units_in_model}/{time_resolution}"
    )
    return countries


# ======================================================================
# Private helpers
# ======================================================================

def _get_region_centroid(region: str, households_spatial_path: Path | None):
    """Get centroid geometry for a region from households spatial data."""
    from shapely.geometry import Point
    if households_spatial_path and Path(households_spatial_path).exists():
        gdf = gpd.read_file(households_spatial_path)
        match = gdf[gdf["region"] == region]
        if not match.empty:
            return match.geometry.unary_union.centroid
    return Point(0, 0)


def _integrate_spatial_firms(ft: gpd.GeoDataFrame, filepath: Path, mrio: Mrio) -> gpd.GeoDataFrame:
    """Replace MRIO-derived firms with spatially disaggregated data where available."""
    spatial = gpd.read_file(filepath)

    # Handle wide-format spatial data (columns = sectors, rows = locations)
    if "region" in spatial.columns and "sector" not in spatial.columns:
        # Only columns matching MRIO sector names are treated as sectors;
        # everything else (e.g. "field", "operator", "capacity") is kept
        # as a plain attribute.
        mrio_sectors = set(mrio.sectors)
        sector_cols = [c for c in spatial.columns
                       if c in mrio_sectors and c != "geometry"]
        attr_cols = [c for c in spatial.columns
                     if c not in sector_cols and c != "geometry"
                     and c not in ("region",)
                     and not c.startswith("subregion_")]
        id_vars = ["region", "geometry"] + \
                  [c for c in spatial.columns if c.startswith("subregion_")] + \
                  attr_cols
        id_vars = [c for c in id_vars if c in spatial.columns]

        # Melt wide to long: one row per (location × sector)
        if sector_cols:
            spatial = spatial.melt(
                id_vars=id_vars,
                value_vars=sector_cols,
                var_name="sector", value_name="importance",
            )
            spatial = spatial.dropna(subset=["importance"])
            spatial = spatial[spatial["importance"] > 0.0]
            spatial["region_sector"] = spatial["region"] + "_" + spatial["sector"]
            logging.info(f"Melted wide-format spatial firms: {len(spatial)} rows "
                         f"({len(sector_cols)} sectors, {len(attr_cols)} attribute cols kept)")
        else:
            logging.warning("Spatial firms file has no columns matching MRIO sectors "
                            f"({list(spatial.columns)}), skipping integration")
            return ft
    elif "region_sector" not in spatial.columns and "region" in spatial.columns and "sector" in spatial.columns:
        spatial["region_sector"] = spatial["region"] + "_" + spatial["sector"]
    elif "region_sector" not in spatial.columns:
        logging.warning("Spatial firms file missing region_sector, skipping integration")
        return ft

    available_rs = set(spatial["region_sector"].unique())
    # Keep MRIO firms that have no spatial data
    keep = ft[~ft["region_sector"].isin(available_rs)].copy()

    # Add spatial firms with importance from MRIO output split
    total_output = mrio.get_total_output()
    spatial_rows = []
    for rs in available_rs:
        rs_spatial = spatial[spatial["region_sector"] == rs].copy()
        n_firms = len(rs_spatial)
        rs_tuple = tuple(rs.split("_", 1))
        total_imp = total_output.get(rs_tuple, 0) / max(n_firms, 1)
        rs_spatial["importance"] = total_imp
        if "region" not in rs_spatial.columns:
            rs_spatial["region"] = rs_tuple[0]
        if "sector" not in rs_spatial.columns:
            rs_spatial["sector"] = rs_tuple[1]
        spatial_rows.append(rs_spatial)

    if spatial_rows:
        spatial_combined = pd.concat(spatial_rows, ignore_index=True)
        result = pd.concat([keep, gpd.GeoDataFrame(spatial_combined, geometry="geometry")], ignore_index=True)
    else:
        result = keep

    return result


def _handle_internal_flows(ft: gpd.GeoDataFrame, mrio: Mrio, io_cutoff: float) -> gpd.GeoDataFrame:
    """Duplicate single-firm region_sectors that have internal consumption."""
    internal_rs = mrio.get_region_sectors_with_internal_flows(threshold=io_cutoff)
    internal_rs_names = {"_".join(t) for t in internal_rs} if internal_rs else set()
    logging.info(f"Internal flows: {len(internal_rs_names)} region-sectors above io_cutoff={io_cutoff}")

    new_rows = []
    for rs_name in internal_rs_names:
        rs_firms = ft[ft["region_sector"] == rs_name]
        if len(rs_firms) == 1:
            # Duplicate the single firm so intra-sector trade is possible
            row = rs_firms.iloc[0].copy()
            row["importance"] = row["importance"] / 2
            new_rows.append(row)
            ft.loc[rs_firms.index[0], "importance"] = ft.loc[rs_firms.index[0], "importance"] / 2
        elif len(rs_firms) > 1:
            logging.debug(f"  {rs_name}: already has {len(rs_firms)} firms, no duplication needed")

    if new_rows:
        extra = gpd.GeoDataFrame(new_rows, geometry="geometry")
        ft = pd.concat([ft, extra], ignore_index=True)
        logging.info(f"Duplicated {len(new_rows)} single-firm region_sectors for internal flows")
    else:
        logging.warning("No single-firm region_sectors needed duplication — check io_cutoff or MRIO diagonal")

    return ft


def _filter_small_firms(ft: gpd.GeoDataFrame, mrio: Mrio,
                        cutoff: dict, data_units: str) -> gpd.GeoDataFrame:
    """Filter out small firms, keeping at least 2 per region_sector."""
    threshold = _get_absolute_cutoff(cutoff, data_units)

    # For each region_sector, keep top 2 by importance + any above threshold
    keep_idx = set()
    for rs, group in ft.groupby("region_sector"):
        sorted_group = group.sort_values("importance", ascending=False)
        # Always keep top 2 (by original DataFrame index)
        keep_idx.update(sorted_group.head(2).index)
        # Also keep any above threshold
        keep_idx.update(sorted_group[sorted_group["importance"] > threshold].index)

    n_removed = len(ft) - len(keep_idx)
    if n_removed:
        logging.info(f"Filtered out {n_removed} small firms (threshold={threshold:.2f})")

    return ft.loc[sorted(keep_idx)].reset_index(drop=True)


def _get_absolute_cutoff(cutoff_dict: dict, data_units: str) -> float:
    """Convert cutoff to absolute value in data units."""
    if cutoff_dict.get("type") != "absolute":
        return 0.0
    return rescale_monetary_values(
        cutoff_dict["value"],
        input_units=cutoff_dict.get("unit", "kUSD"),
        target_units=data_units,
        input_time_resolution="year",
        target_time_resolution="year",
    )
