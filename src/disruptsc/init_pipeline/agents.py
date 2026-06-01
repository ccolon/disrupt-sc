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
    node_coords = np.column_stack([transport_nodes.geometry.x.values,
                                   transport_nodes.geometry.y.values])
    query_coords = np.column_stack([gdf.geometry.x.values, gdf.geometry.y.values])
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
    region_centroids = _load_region_centroids(households_spatial_path)
    from shapely.geometry import Point
    default_centroid = Point(0, 0)
    rows = []
    for rs in mrio.region_sectors:
        region, sector = rs
        rows.append({
            "region": region,
            "sector": sector,
            "region_sector": f"{region}_{sector}",
            "importance": total_output.get(rs, 0),
            "geometry": region_centroids.get(region, default_centroid),
        })
    ft = gpd.GeoDataFrame(rows, geometry="geometry")

    # Phase 2: Integrate disaggregated spatial data if available
    if firms_spatial_path and Path(firms_spatial_path).exists():
        ft = _integrate_spatial_firms(ft, firms_spatial_path, mrio)

    # Phase 3: Handle internal flows (duplicate if needed)
    ft = _handle_internal_flows(ft, mrio, params.input_coverage)

    # Phase 4: Filter small firms
    ft = _filter_small_firms(ft, mrio, params.cutoff_firm_output, params.monetary_units_in_data)

    # Phase 5: Assign transport nodes
    ft["od_point"] = find_nearest_node_id(transport_nodes, ft)
    coords = _get_long_lat(ft["od_point"], transport_nodes)
    ft["long"] = coords["long"].values
    ft["lat"] = coords["lat"].values

    # Phase 6: Enrich with sector metadata
    if sector_table is not None:
        sector_type_map = (sector_table.drop_duplicates("sector")
                                       .set_index("sector")["type"].to_dict())
        ft["sector_type"] = ft["sector"].map(sector_type_map).fillna("manufacturing")
    else:
        ft["sector_type"] = "manufacturing"

    # USD per ton
    ft["usd_per_ton"] = ft["region_sector"].map(usd_per_ton).fillna(2864.0)

    # Margins and transport share from MRIO
    margins = mrio.get_margin_per_industry()
    transport_shares = mrio.get_transport_input_share(
        (sector_table.drop_duplicates("sector").set_index("sector")["type"]
         if sector_table is not None else {}),
    )
    ft["target_margin"] = [margins.get(k, 0.2) for k in zip(ft["region"], ft["sector"])]
    ft["transport_share"] = params.firm_transport_share  # uniform transport share from YAML

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
    for row in firm_table.to_dict(orient="records"):
        subregion_kwargs = {k: v for k, v in row.items() if k.startswith("subregion_")}

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

    return firms


def load_tech_coefs(firms: dict[str, Firm], mrio: Mrio, input_coverage: float):
    """Load input_mix (technical coefficients) into each firm.

    *input_coverage* is the cumulative input-coverage fraction in (0, 1]:
    e.g. 0.95 means keep enough inputs to cover 95 % of each buyer's
    intermediate consumption, ranked by absolute MRIO flow.
    """
    tech_coefs = mrio.get_tech_coef_dict(coverage=input_coverage)

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
            sector_type_map = (sector_table.drop_duplicates("sector")
                                           .set_index("sector")["type"].to_dict())

        for firm in firms.values():
            targets = {}
            for input_id in firm.input_mix:
                # input_id is a region_sector like "ARM_mining"
                input_sector = input_id.split("_", 1)[-1] if "_" in input_id else input_id
                input_type = sector_type_map.get(input_sector, "default")
                duration = values.get(input_type, values.get("default", 30))
                targets[input_id] = duration * factor
            firm.inventory_duration_target = targets


def configure_household_inventories(households: dict[str, Household],
                                    enabled: bool,
                                    inventory_targets: dict,
                                    inventory_restoration_time: float,
                                    time_resolution: str,
                                    sector_table: pd.DataFrame = None):
    """Attach firm-style inventory parameters to households."""
    definition = inventory_targets.get("definition", "per_input_type")
    values = inventory_targets.get("values", {"default": 30})
    target_unit = inventory_targets.get("unit", "day")

    time_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    factor = time_days.get(target_unit, 1) / time_days.get(time_resolution, 7)

    sector_type_map = {}
    if sector_table is not None:
        sector_type_map = (sector_table.drop_duplicates("sector")
                                       .set_index("sector")["type"].to_dict())

    for hh in households.values():
        hh.use_inventories = enabled
        hh.inventory_restoration_time = inventory_restoration_time
        hh.inventory_duration_target = {}
        hh.eq_needs = dict(hh.sector_consumption)

        for sector_id in hh.sector_consumption:
            if definition == "per_input_type":
                input_sector = sector_id.split("_", 1)[-1] if "_" in sector_id else sector_id
                input_type = sector_type_map.get(input_sector, "default")
                duration = values.get(input_type, values.get("default", 30))
            else:
                duration = values.get("default", 30)
            hh.inventory_duration_target[sector_id] = duration * factor

        if not enabled:
            hh.inventory = {}


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
    else:
        ht["population"] = ht["population"].fillna(1.0)

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
    # final_demand has been rescaled above to (model_units, time_resolution),
    # so the cutoff must match those units, not the raw data units.
    cutoff = _get_absolute_cutoff(
        params.cutoff_household_demand,
        target_units=params.monetary_units_in_model,
        target_time_resolution=time_resolution,
    )

    # Pre-aggregate: one column per region, rows = region_sectors
    region_demand = final_demand.T.groupby(level=0).sum().T
    total_pop_per_region = ht.groupby("region")["population"].transform("sum")
    proportion_per_hh = (ht["population"] / total_pop_per_region).fillna(0.0)

    for hh in ht.itertuples():
        region = hh.region
        if region not in region_demand.columns:
            continue
        proportion = proportion_per_hh.iloc[hh.Index]
        if proportion <= 0:
            continue
        series = region_demand[region] * proportion
        hh_consumption = {
            f"{r}_{s}": float(v)
            for (r, s), v in series.items()
            if v > cutoff
        }
        if hh_consumption:
            consumption[hh.Index] = hh_consumption

    logging.info(f"Created household table with {len(ht)} households, "
                 f"{len(consumption)} with demand above cutoff")
    return ht, consumption


def create_households(household_table: pd.DataFrame,
                      consumption: dict) -> dict[str, Household]:
    """Instantiate Household objects."""
    households = {}
    for idx, row in enumerate(household_table.to_dict(orient="records")):
        if idx not in consumption:
            continue  # Skip households with no demand
        subregion_kwargs = {k: v for k, v in row.items() if k.startswith("subregion_")}
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
                     transport_edges: gpd.GeoDataFrame | None = None,
                     countries_no_transport: tuple = ()) -> dict[str, Country]:
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

    # The geojson is optional: a virtual country (listed in
    # countries_no_transport) is allowed to be absent from it. A non-virtual
    # country missing from the geojson raises in Phase 1 below. An empty MRIO
    # country list also works — the phases below naturally produce {}.
    if countries_spatial_path and Path(countries_spatial_path).exists():
        countries_gdf = gpd.read_file(countries_spatial_path)
    else:
        if all_countries:
            reason = (f"file not found at {countries_spatial_path}"
                      if countries_spatial_path else "no filepath configured")
            logging.info(
                f"Country geojson unavailable ({reason}); only virtual "
                f"countries can be built without a geometry."
            )
        countries_gdf = gpd.GeoDataFrame({"region": [], "geometry": []}, geometry="geometry")

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
    # The MRIO is the source of truth for *which* countries to model. The geojson
    # supplies a point location for each one — except for virtual countries
    # (listed in countries_no_transport), whose flows never touch the transport
    # network and therefore don't need a real location. Such virtual countries
    # are allowed to be absent from the geojson; they are stamped with
    # od_point = -1 (the sentinel _distance_between already understands).
    countries = {}
    total_imports = import_table.sum().sum() if len(import_table) > 0 else 1.0

    # Phase 1: resolve spatial data per country.
    # Each entry is (country_code, centroid_or_None). centroid is None when the
    # country is virtual and missing from the geojson.
    country_specs: list[tuple[str, "object | None"]] = []
    geojson_name = Path(countries_spatial_path).name if countries_spatial_path else "countries.geojson"
    for country_code in all_countries:
        match = countries_gdf[countries_gdf["region"] == country_code]
        if match.empty:
            if country_code in countries_no_transport:
                country_specs.append((country_code, None))
                continue
            raise ValueError(
                f"Country {country_code!r} is present in the MRIO but missing "
                f"from {geojson_name}. Add a feature for it, or list it under "
                f"countries_no_transport (virtual countries skip the spatial lookup)."
            )
        geom = match.iloc[0].geometry
        centroid = geom.centroid if geom.geom_type != "Point" else geom
        country_specs.append((country_code, centroid))

    # Phase 2: batch KDTree once over countries that have a centroid.
    sited = [(code, ctr) for code, ctr in country_specs if ctr is not None]
    if sited:
        centroids_gdf = gpd.GeoDataFrame(
            [{"geometry": ctr} for _, ctr in sited], geometry="geometry"
        )
        sited_od_points = find_nearest_node_id(country_nodes, centroids_gdf)
    else:
        sited_od_points = np.array([], dtype=int)
    od_point_by_pid = {
        code: int(op) for (code, _), op in zip(sited, sited_od_points)
    }

    # Phase 3: build country agents.
    for country_code, centroid in country_specs:
        od_point = od_point_by_pid.get(country_code, -1)
        long_ = centroid.x if centroid is not None else None
        lat_ = centroid.y if centroid is not None else None

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
            long=long_,
            lat=lat_,
            sector=mrio.import_label or "IMP",
            region_sector=f"{country_code}_{mrio.import_label or 'IMP'}",
            usd_per_ton=country_upt,
            monetary_unit_factor=_UNITS.get(params.monetary_units_in_model, 1e6),
            transport_share=params.country_transport_share,
            virtual=country_code in countries_no_transport,
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
    virtual_pids = sorted(pid for pid, c in countries.items() if c.virtual)
    if virtual_pids:
        unsited = sorted(pid for pid in virtual_pids if countries[pid].od_point == -1)
        msg = f"Virtual countries (flows bypass transport network): {virtual_pids}"
        if unsited:
            msg += f"; of those, {unsited} have no geojson location"
        logging.info(msg)
    unknown = sorted(set(countries_no_transport) - set(countries))
    if unknown:
        logging.warning(
            f"countries_no_transport lists pids that are not in the MRIO: {unknown}"
        )
    return countries


# ======================================================================
# Private helpers
# ======================================================================

def _load_region_centroids(households_spatial_path: Path | None) -> dict:
    """Build a {region: centroid} dict from the households geojson.

    Reads the file once; callers use dict lookups instead of per-region I/O.
    """
    if not households_spatial_path or not Path(households_spatial_path).exists():
        return {}
    gdf = gpd.read_file(households_spatial_path)
    if "region" not in gdf.columns:
        return {}
    return {
        region: group.geometry.unary_union.centroid
        for region, group in gdf.groupby("region")
    }


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


def _handle_internal_flows(ft: gpd.GeoDataFrame, mrio: Mrio,
                           input_coverage: float) -> gpd.GeoDataFrame:
    """Duplicate single-firm region_sectors that have internal consumption.

    A region-sector is flagged iff its self-supply edge survives the same
    input-selection rule applied elsewhere — i.e. (rs, rs) is among the
    inputs kept by the coverage filter for buyer rs.
    """
    tech_coefs = mrio.get_tech_coef_dict(coverage=input_coverage)
    internal_rs_names = {buyer for buyer, inputs in tech_coefs.items() if buyer in inputs}
    logging.info(f"Internal flows: {len(internal_rs_names)} region-sectors with self-supply "
                 f"surviving input_coverage={input_coverage}")

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

    return ft


def _filter_small_firms(ft: gpd.GeoDataFrame, mrio: Mrio,
                        cutoff: dict, data_units: str) -> gpd.GeoDataFrame:
    """Filter out small firms, keeping at least 2 per region_sector."""
    threshold = _get_absolute_cutoff(cutoff, data_units)

    # Keep top 2 by importance per region_sector, plus any above threshold
    rank = ft.groupby("region_sector")["importance"].rank(method="first", ascending=False)
    keep = (rank <= 2) | (ft["importance"] > threshold)

    n_removed = int((~keep).sum())
    if n_removed:
        logging.info(f"Filtered out {n_removed} small firms (threshold={threshold:.2f})")

    return ft.loc[keep].reset_index(drop=True)


def _get_absolute_cutoff(cutoff_dict: dict, target_units: str,
                         target_time_resolution: str = "year") -> float:
    """Convert an absolute cutoff (yearly, in *unit*) to *target_units / target_time_resolution*.

    Cutoffs in the YAML are always declared as yearly values in their `unit`.
    Most call sites compare against raw MRIO aggregates (data_units/year), so
    the default `target_time_resolution="year"` is a no-op rescale. Call sites
    that compare against series already rescaled to model units / time-step
    must pass the matching `target_units` and `target_time_resolution`.
    """
    if cutoff_dict.get("type") != "absolute":
        return 0.0
    return rescale_monetary_values(
        cutoff_dict["value"],
        input_units=cutoff_dict.get("unit", "kUSD"),
        target_units=target_units,
        input_time_resolution="year",
        target_time_resolution=target_time_resolution,
    )
