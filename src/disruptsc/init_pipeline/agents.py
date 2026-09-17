"""Create firms, households, and countries from MRIO and spatial data."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from disruptsc.agents.firm import Firm
from disruptsc.agents.household import Household, GovernmentDemand, InvestmentDemand
from disruptsc.agents.country import Country
from disruptsc.network.mrio import Mrio, Selection, rescale_monetary_values, _UNITS
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


def attachment_nodes(transport_nodes: gpd.GeoDataFrame,
                     transport_edges: gpd.GeoDataFrame | None,
                     attachment: str, what: str = "Agent") -> gpd.GeoDataFrame:
    """Candidate nodes for agent placement under ``agent_attachment``.

    ``"any"`` keeps every node (legacy). ``"roads"`` keeps only endpoints of
    road edges: the first/last mile is by road and rail or barge are reached
    through the multimodal connectors, so no agent ships from a rail or
    waterway node with no access leg and no transfer cost.
    """
    if attachment != "roads" or transport_edges is None or "type" not in transport_edges.columns:
        return transport_nodes
    road_edges = transport_edges[transport_edges["type"] == "roads"]
    road_node_ids = set(road_edges["end1"].tolist() + road_edges["end2"].tolist())
    nodes = transport_nodes[transport_nodes.index.isin(road_node_ids)]
    if nodes.empty:
        logging.warning(f"{what} placement: no road nodes found - falling back to all transport nodes")
        return transport_nodes
    logging.info(f"{what} placement restricted to {len(nodes)} road nodes "
                 f"(of {len(transport_nodes)}; agent_attachment: roads)")
    return nodes


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
                      params: AgentParams,
                      selection: Selection) -> pd.DataFrame:
    """Build firm_table DataFrame from MRIO + spatial data.

    Only region_sectors kept by *selection* (i.e. those surviving the
    flow-coverage filter) get firms.
    """
    if params.firm_data_type == "transaction_based":
        raise NotImplementedError("Transaction-based firm creation not yet implemented in v2")

    # Phase 1: Base table from kept region_sectors
    total_output = mrio.get_total_output()
    region_centroids = _load_region_centroids(households_spatial_path)
    from shapely.geometry import Point
    default_centroid = Point(0, 0)
    rows = []
    for rs in selection.region_sectors:
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
        # Spatial integration may add firms for region_sectors that were
        # dropped by the selection; strip them so the firm set matches.
        kept_names = {f"{r}_{s}" for r, s in selection.region_sectors}
        before = len(ft)
        ft = ft[ft["region_sector"].isin(kept_names)].reset_index(drop=True)
        dropped = before - len(ft)
        if dropped:
            logging.info(
                f"Dropped {dropped} spatially-disaggregated firms whose "
                f"region_sector failed the flow_coverage filter"
            )

    # Phase 3: Handle internal flows (duplicate if needed)
    ft = _handle_internal_flows(ft, selection)

    # Phase 4: Assign transport nodes
    ft["od_point"] = find_nearest_node_id(transport_nodes, ft)
    coords = _get_long_lat(ft["od_point"], transport_nodes)
    ft["long"] = coords["long"].values
    ft["lat"] = coords["lat"].values

    # Phase 5: Enrich with sector metadata. Build the sector_name → type map
    # once and reuse it for the firm's own `sector_type` attribute and for
    # transport-industry detection in `get_transport_input_share`.
    if sector_table is not None:
        sector_type_map = (sector_table.drop_duplicates("sector")
                                       .set_index("sector")["type"].to_dict())
    else:
        sector_type_map = {}
    ft["sector_type"] = ft["sector"].map(sector_type_map).fillna("manufacturing")

    # Surface MRIO sectors missing from the type map — they won't be detected
    # as transport for transport_share purposes, which is usually a data bug
    # rather than an intent.
    missing_types = sorted({rs[1] for rs in mrio.region_sectors
                            if rs[1] not in sector_type_map})
    if missing_types:
        preview = ", ".join(missing_types[:5])
        suffix = f" (+{len(missing_types) - 5} more)" if len(missing_types) > 5 else ""
        logging.warning(
            f"sector_table is missing the 'type' entry for "
            f"{len(missing_types)} MRIO sector(s): {preview}{suffix}. "
            f"They won't be classified as 'transport' for transport_share."
        )

    # USD per ton
    ft["usd_per_ton"] = ft["region_sector"].map(usd_per_ton).fillna(2864.0)

    # Margins and transport share from MRIO. Both ratios are computed against
    # the *full* MRIO (no flow_coverage filter) so that pricing reflects the
    # true economic intensity of each sector regardless of which cells were
    # pruned for graph construction. `firm_transport_share` is the fallback
    # used when a firm's region_sector is missing from the MRIO ratio dict.
    margins = mrio.get_margin_per_industry()
    transport_shares = mrio.get_transport_input_share(sector_type_map)
    ft["target_margin"] = [margins.get(k, 0.2) for k in zip(ft["region"], ft["sector"])]
    ft["transport_share"] = [
        transport_shares.get((r, s), params.firm_transport_share)
        for r, s in zip(ft["region"], ft["sector"])
    ]

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
            critical_input_threshold=params.critical_input_threshold,
            inventory_restoration_time=params.inventory_restoration_time,
            capital_to_value_added_ratio=params.capital_to_value_added_ratio,
            subregions=subregion_kwargs,
        )
        firms[firm.pid] = firm

    return firms


def load_tech_coefs(firms: dict[str, Firm], mrio: Mrio, selection: Selection):
    """Load input_mix (technical coefficients) into each firm.

    Inputs are restricted to the cells kept by *selection* — i.e. the
    union of per-buyer top inputs and per-supplier top buyers under the
    flow-coverage rule. Buyers thereby retain at least
    ``selection.flow_coverage`` of their intermediate consumption, plus
    any cells added by the supplier-side rule (small inputs that are
    nonetheless large flows for the supplier).
    """
    tech_coefs = mrio.get_tech_coef_dict_for_selection(selection)

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
        firm.input_mix = dict(sorted(coefs.items()))   # deterministic key order (KI-34)


def import_bundle_shares(mrio) -> dict:
    """Sector composition of each firm-level import bundle, from the MRIO.

    The supply-chain build folds a buyer's sector-resolved import needs into
    one ``{BLOC}_imports`` input per partner bloc (supply_chain.
    _aggregate_import_inputs), which loses the sector that the inventory
    target and the criticality weight are keyed on. The MRIO still has it:
    the import rows (BLOC, sector) of the buyer's column. Returns
    ``{(region, sector): {bloc: {sector: share}}}`` with shares summing to 1
    per bloc (blocs with no import flow to that buyer are absent).
    """
    shares: dict = {}
    try:
        imp = mrio.get_import_rows()
    except Exception:  # legacy MRIO without import rows
        return shares
    ext = set(getattr(mrio, "external_selling_countries", []) or [])
    import_label = getattr(mrio, "import_label", "imports")
    for col in imp.columns:
        series = imp[col]
        series = series[series > 0]
        if series.empty:
            continue
        by_bloc: dict = {}
        for (bloc, sector), value in series.items():
            if bloc not in ext and sector != import_label:
                continue
            by_bloc.setdefault(bloc, {})[sector] = by_bloc.get(bloc, {}).get(sector, 0.0) + float(value)
        out = {}
        for bloc, comp in by_bloc.items():
            tot = sum(comp.values())
            if tot > 0:
                out[bloc] = {s: v / tot for s, v in comp.items()}
        if out:
            shares[tuple(col)] = out
    return shares


def _bundle_composition(firm, input_id: str, bundle_shares: dict | None) -> dict | None:
    """{sector: share} of a ``{BLOC}_imports`` input of *firm*, or None."""
    if not bundle_shares or not input_id.endswith("_imports"):
        return None
    bloc = input_id[: -len("_imports")]
    return (bundle_shares.get((firm.region, firm.sector)) or {}).get(bloc)


def load_input_pooling(firms: dict[str, Firm], poolable_products: set[str]) -> tuple[int, int]:
    """Pool the same product across regions for the commodity-like products.

    For every firm, each input ``<REGION>_<sector>`` whose sector is in *poolable_products*
    joins the pool ``<sector>``; differentiated products and import bundles
    (``{BLOC}_imports``, whose composition mixes products) keep their own pool. Returns
    (number of firms with at least one multi-region pool, number of pooled inputs).
    """
    n_firms = n_inputs = 0
    for firm in firms.values():
        pools: dict[str, str] = {}
        for input_id in firm.input_mix:
            if input_id.endswith("_imports"):
                continue
            sector = input_id.split("_", 1)[-1] if "_" in input_id else input_id
            if sector in poolable_products:
                pools[input_id] = sector
        firm.input_pools = pools
        members = {}
        for input_id, pool in pools.items():
            members[pool] = members.get(pool, 0) + 1
        multi = sum(v for v in members.values() if v > 1)
        if multi:
            n_firms += 1
            n_inputs += multi
    logging.info(f"input_pooling: {len(poolable_products)} poolable products; {n_firms}/{len(firms)} firms hold "
                 f"a product from several regions ({n_inputs} pooled inputs)")
    return n_firms, n_inputs


def load_input_criticality(firms: dict[str, Firm], criticality: pd.DataFrame,
                           bundle_shares: dict | None = None):
    """Attach per-input criticality weights (Pichler adapted Leontief) to firms.

    ``criticality`` is a sector-by-sector matrix (index = input sector, columns =
    buyer sector) of weights in {0, 0.5, 1}. For each firm (buyer) and each input in
    its input_mix we look up ``criticality.loc[input_sector, buyer_sector]``. Sectors
    absent from the matrix default to 1.0 (critical) so coverage gaps stay
    conservative (strict-Leontief behaviour), never silently non-binding.

    Import bundles (``{BLOC}_imports``, see import_bundle_shares) get the
    share-weighted mean of their sectors' weights when *bundle_shares* is
    given; otherwise they default to critical.
    """
    # (input_sector, buyer_sector) -> weight, for O(1) lookups
    lookup = {(i, j): float(criticality.at[i, j])
              for i in criticality.index for j in criticality.columns}

    def _sector(region_sector: str) -> str:
        return region_sector.split("_", 1)[-1] if "_" in region_sector else region_sector

    missing_sectors = set()
    n_bundles = n_resolved = 0
    for firm in firms.values():
        buyer = _sector(firm.region_sector)
        weights = {}
        for input_id in firm.input_mix:
            inp = _sector(input_id)
            if inp == "imports":
                n_bundles += 1
                comp = _bundle_composition(firm, input_id, bundle_shares)
                if comp:
                    n_resolved += 1
                    weights[input_id] = sum(share * lookup.get((s, buyer), 1.0) for s, share in comp.items())
                else:
                    weights[input_id] = 1.0
                continue
            key = (inp, buyer)
            if key in lookup:
                weights[input_id] = lookup[key]
            else:
                weights[input_id] = 1.0  # conservative default: critical
                if inp not in criticality.index or buyer not in criticality.columns:
                    missing_sectors.add(inp if inp not in criticality.index else buyer)
        firm.input_criticality = weights
    if n_bundles:
        logging.info(f"input_criticality: {n_resolved}/{n_bundles} import bundles resolved from their "
                     f"MRIO sector composition (the rest default to critical)")

    if missing_sectors:
        logging.warning(
            f"input_criticality: {len(missing_sectors)} sector(s) absent from the "
            f"criticality matrix, defaulted to critical: {sorted(missing_sectors)[:10]}"
        )
    n_crit = sum(sum(1 for w in f.input_criticality.values() if w >= 1.0) for f in firms.values())
    n_imp = sum(sum(1 for w in f.input_criticality.values() if 0.5 <= w < 1.0) for f in firms.values())
    n_non = sum(sum(1 for w in f.input_criticality.values() if w < 0.5) for f in firms.values())
    tot = max(1, n_crit + n_imp + n_non)
    logging.info(
        f"Loaded input criticality: {n_crit} critical / {n_imp} important / {n_non} "
        f"non-critical input links ({100*n_crit/tot:.0f}/{100*n_imp/tot:.0f}/"
        f"{100*n_non/tot:.0f}%)")


def load_inventories(firms: dict[str, Firm], inventory_targets: dict,
                     time_resolution: str, sector_table: pd.DataFrame = None,
                     bundle_shares: dict | None = None):
    """Set inventory duration targets per input sector.

    Import bundles (``{BLOC}_imports``) get the share-weighted mean of their
    sectors' type durations when *bundle_shares* (import_bundle_shares) is
    given, else the ``imports`` value or the default.
    """
    definition = inventory_targets.get("definition", "per_input_type")
    values = inventory_targets.get("values", {"default": 30})
    target_unit = inventory_targets.get("unit", "day")

    # Convert target to time_resolution units
    time_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    factor = time_days.get(target_unit, 1) / time_days.get(time_resolution, 7)

    sector_type_map = {}
    if sector_table is not None:
        sector_type_map = (sector_table.drop_duplicates("sector")
                                       .set_index("sector")["type"].to_dict())

    if definition == "per_buying_sector":
        # Days of goods-input stock keyed on the BUYER's sector (balance-sheet
        # raw-material stocks over material costs, e.g. Bundesbank RHB days),
        # with optional overrides per (buyer, input sector or input type) and
        # a "*" buyer for overrides that hold for every buyer (non-storable
        # utilities). Service inputs keep a coping duration, not a stock.
        # See studies/rhine2026/evidence/inventory_durations_by_industry.md.
        overrides = inventory_targets.get("overrides", {}) or {}
        service_types = set(inventory_targets.get("service_types", ("service", "services", "trade", "transport")))
        service_days = inventory_targets.get("service_days", 90)
        default_days = values.get("default", 30)

        def _days(buyer_sector: str, input_sector: str) -> float:
            itype = sector_type_map.get(input_sector, "default")
            for scope in (overrides.get(buyer_sector, {}), overrides.get("*", {})):
                if input_sector in scope:
                    return float(scope[input_sector])
                if itype in scope:
                    return float(scope[itype])
            if itype in service_types:
                return float(service_days)
            return float(values.get(buyer_sector, default_days))

        n_imports = n_resolved = 0
        for firm in firms.values():
            targets = {}
            for input_id in firm.input_mix:
                input_sector = input_id.split("_", 1)[-1] if "_" in input_id else input_id
                if input_sector == "imports":
                    n_imports += 1
                    comp = _bundle_composition(firm, input_id, bundle_shares)
                    if comp:
                        n_resolved += 1
                        duration = sum(share * _days(firm.sector, s) for s, share in comp.items())
                    else:
                        duration = float(values.get(firm.sector, default_days))
                else:
                    duration = _days(firm.sector, input_sector)
                targets[input_id] = duration * factor
            firm.inventory_duration_target = targets
        logging.info(f"Inventory targets per buying sector: {len(values)} sectors, {len(overrides)} override blocks; "
                     f"{n_resolved}/{n_imports} import bundles resolved from their composition")
        return

    if definition == "per_input_type":
        n_imports = 0
        for firm in firms.values():
            targets = {}
            for input_id in firm.input_mix:
                # input_id is a region_sector like "ARM_mining"
                input_sector = input_id.split("_", 1)[-1] if "_" in input_id else input_id
                if input_sector == "imports":
                    # Sector-resolved import needs are folded into one
                    # "{BLOC}_imports" bundle per partner when the supply chain
                    # is built (supply_chain._aggregate_import_inputs), AFTER
                    # this function ran on the agents; the bundle then had no
                    # target and fell back to one time step (EU Rhine study,
                    # 4 Sep 2026: one closed week zeroed the power plants'
                    # coal and the hauliers' fuel). Re-applied on every cache
                    # load (run.py _configure_firms): the bundle gets the mean
                    # duration of its MRIO sector composition, else the
                    # `imports` value, or the default, of the config.
                    comp = _bundle_composition(firm, input_id, bundle_shares)
                    if comp:
                        duration = sum(share * values.get(sector_type_map.get(s, "default"), values.get("default", 30))
                                       for s, share in comp.items())
                    else:
                        duration = values.get("imports", values.get("default", 30))
                    n_imports += 1
                else:
                    input_type = sector_type_map.get(input_sector, "default")
                    duration = values.get(input_type, values.get("default", 30))
                targets[input_id] = duration * factor
            firm.inventory_duration_target = targets
        if n_imports:
            logging.info(f"Inventory targets: {n_imports} import bundles set to "
                         f"{values.get('imports', values.get('default', 30))} {target_unit}s")


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
        # National government/investment agents hold no inventory (accounting-only,
        # excluded from the welfare metric) -- never buffer them regardless of `enabled`.
        if getattr(hh, "agent_type", "household") != "household":
            hh.use_inventories = False
            hh.inventory = {}
            hh.inventory_duration_target = {}
            hh.eq_needs = dict(hh.sector_consumption)
            continue
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


_DAYS_PER_STEP = {"day": 1, "week": 7, "month": 30, "year": 365}


def report_inventory_to_gdp(firms: dict, households: dict, time_resolution: str) -> dict:
    """Standing defensibility check: total inventory stock as % of annual GDP.

    Call after set_initial_conditions (needs firm.eq_finance + initialized
    inventories). Firm input inventories map to national-accounts *business*
    inventories (~10-15% of GDP in most economies); household consumption
    inventories are an extra behavioural buffer (retail shelf + pantry) that
    should stay modest. Logs the split and warns if the total looks
    over-parametrised, so an inflated buffer can't silently return.
    """
    ppy = 365.0 / _DAYS_PER_STEP.get(time_resolution, 7)

    def _va(f):
        ef = getattr(f, "eq_finance", None) or {}
        s = ef.get("sales", 0.0)
        c = ef.get("costs", {})
        return (s - c.get("input", 0.0)) if s > 1e-12 else 0.0

    gdp = sum(_va(f) for f in firms.values()) * ppy
    firm_inv = sum(sum(f.inventory.values()) for f in firms.values() if f.inventory)
    hh_inv = sum(sum(h.inventory.values()) for h in households.values() if h.inventory)
    if gdp <= 0:
        return {}
    firm_pct, hh_pct = 100 * firm_inv / gdp, 100 * hh_inv / gdp
    total_pct = firm_pct + hh_pct
    logging.info(
        f"Inventory/GDP check: firm {firm_pct:.1f}% + household {hh_pct:.1f}% "
        f"= {total_pct:.1f}% of annual GDP (business-inventory benchmark ~10-15%)"
    )
    if total_pct > 20.0:
        logging.warning(
            f"Total inventory is {total_pct:.1f}% of annual GDP (>20%): buffers may be "
            f"over-parametrised (firm {firm_pct:.1f}%, household {hh_pct:.1f}%). Check "
            f"inventory_duration_targets / household_inventory_duration_target."
        )
    return {"firm_pct": firm_pct, "household_pct": hh_pct, "total_pct": total_pct}


# ======================================================================
# Households
# ======================================================================

def create_household_table(mrio: Mrio, households_spatial_path: Path,
                           transport_nodes: gpd.GeoDataFrame,
                           selection: Selection,
                           params: AgentParams,
                           time_resolution: str = "week") -> tuple[pd.DataFrame, dict]:
    """Build household_table and consumption patterns.

    A household consumes from supplier *S* iff the MRIO cell
    ``(S, (region, FinalDemand))`` is in ``selection.kept_cells`` for
    the household's region. The cell-level filter (already symmetric
    per-buyer + per-supplier under flow_coverage) replaces the old
    per-household monetary cutoff.
    """
    # Load spatial data and assign transport / IDs
    ht = gpd.read_file(households_spatial_path)
    mrio_regions = set(mrio.regions)
    ht = ht[ht["region"].isin(mrio_regions)].copy()

    ht["od_point"] = find_nearest_node_id(transport_nodes, ht)
    coords = _get_long_lat(ht["od_point"], transport_nodes)
    ht["long"] = coords["long"].values
    ht["lat"] = coords["lat"].values

    ht = ht.reset_index(drop=True)
    ht["id"] = range(len(ht))
    ht["household"] = "hh_" + ht["id"].astype(str)
    ht["name"] = ht["region"] + "_household" + ht["id"].astype(str)
    if "population" not in ht.columns:
        ht["population"] = 1.0
    else:
        ht["population"] = ht["population"].fillna(1.0)

    # Group kept cells by their FD-column → set of kept supplier rows.
    fd_label = mrio.final_demand_label
    kept_suppliers_by_fd_col: dict = {}
    for (row, col) in selection.kept_cells:
        if col[1] == fd_label:
            kept_suppliers_by_fd_col.setdefault(col, set()).add(row)

    # Build a (supplier_row × fd_col) frame with the kept values only, in
    # model units / time resolution. Cells outside kept_cells are zero.
    all_suppliers = sorted({s for sups in kept_suppliers_by_fd_col.values() for s in sups})
    all_fd_cols = sorted(kept_suppliers_by_fd_col.keys())
    if all_suppliers and all_fd_cols:
        fd_raw = mrio.loc[all_suppliers, all_fd_cols]
        fd_scaled = rescale_monetary_values(
            fd_raw,
            input_units=params.monetary_units_in_data,
            input_time_resolution="year",
            target_units=params.monetary_units_in_model,
            target_time_resolution=time_resolution,
        )
        # Zero out cells that didn't make the cut
        for col in all_fd_cols:
            keep_rows = kept_suppliers_by_fd_col[col]
            drop_mask = [s not in keep_rows for s in all_suppliers]
            fd_scaled.loc[drop_mask, col] = 0.0
        # Aggregate across FD columns belonging to the same region
        region_demand = fd_scaled.T.groupby(level=0).sum().T  # cols = regions, rows = suppliers
    else:
        region_demand = pd.DataFrame()

    # Distribute per household by population proportion within each region
    consumption = {}
    if not region_demand.empty:
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
                if v > 0
            }
            if hh_consumption:
                consumption[hh.Index] = hh_consumption

    logging.info(
        f"Created household table with {len(ht)} households, "
        f"{len(consumption)} with non-empty consumption "
        f"(flow_coverage={selection.flow_coverage})"
    )
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


def create_representative_demand_agent(mrio: Mrio, label: str, agent_cls,
                                       selection: Selection, params: AgentParams,
                                       time_resolution: str, od_point: int,
                                       region: str | None = None):
    """Build ONE national final-demand agent (government or investment) from the whole
    ``label`` column of the MRIO.

    Unlike households, these are NOT spatially explicit -- a single representative buyer
    keeps firm equilibrium production correct (its column is part of every seller's row
    sum) and yields a separate shortfall metric. It buys every consumed sector nationally
    (``weight_localization=0`` -> suppliers by size only; ``nb_suppliers`` large -> spread
    across the whole sector so the aggregate agent still "sees" localized disruption) and
    holds no inventory. Returns ``None`` if the column is absent/empty (e.g. a bundled
    MRIO with no separate government column).
    """
    cols = [c for c in mrio.columns if c[1] == label]
    if not cols:
        return None
    # Valid suppliers = modeled firm region-sectors (selection) + import country rows
    # (legacy (BLOC, "imports") or sector-resolved (BLOC, sector) — match by region).
    valid = set(selection.region_sectors)
    ext = set(mrio.external_selling_countries)
    rows = [r for r in mrio.index if (r in valid) or (r[0] in ext)]
    raw = mrio.loc[rows, cols]
    scaled = rescale_monetary_values(
        raw, input_units=params.monetary_units_in_data, input_time_resolution="year",
        target_units=params.monetary_units_in_model, target_time_resolution=time_resolution)
    series = scaled.sum(axis=1)
    sector_consumption = {f"{r}_{s}": float(v) for (r, s), v in series.items() if v > 0}
    if not sector_consumption:
        return None
    region = region or (mrio.regions[0] if mrio.regions else "DOM")
    agent = agent_cls(
        pid=label, region=region, od_point=int(od_point), name=f"{label}_national",
        population=1.0, sector_consumption=sector_consumption,
        use_inventories=False, weight_localization=0.0, nb_suppliers=1e9,
    )
    agent.purchase_plan = dict(sector_consumption)  # refined during supply-chain wiring
    logging.info(
        f"Created national {label} agent: {len(sector_consumption)} sectors, "
        f"total demand {sum(sector_consumption.values()):,.0f} {params.monetary_units_in_model}/step"
    )
    return agent


def add_representative_demand_agents(households: dict, mrio: Mrio, selection: Selection,
                                     params: AgentParams, time_resolution: str) -> dict:
    """Add single national government + investment agents into the household dict.

    They flow through all the household machinery (supply-chain wiring, init, ordering,
    receiving, collection) but are tagged by ``agent_type`` and kept out of the welfare
    headline. No-op for a bundled MRIO (no separate government/investment columns).
    Must be called AFTER create_households and BEFORE build_supply_chain_network.
    """
    if not households:
        return households
    # National od_point = the most-populous household's node. Transport is off for these
    # ensembles, so the exact node is immaterial; pick a populous, valid one.
    anchor = max(households.values(), key=lambda h: getattr(h, "population", 0.0) or 0.0)
    for label, cls in (("government", GovernmentDemand), ("investment", InvestmentDemand)):
        agent = create_representative_demand_agent(
            mrio, label, cls, selection, params, time_resolution, anchor.od_point)
        if agent is not None:
            households[agent.pid] = agent
    return households


# ======================================================================
# Countries
# ======================================================================

def create_countries(mrio: Mrio, transport_nodes: gpd.GeoDataFrame,
                     countries_spatial_path: Path, usd_per_ton: dict,
                     time_resolution: str, params: AgentParams,
                     selection: Selection,
                     transport_edges: gpd.GeoDataFrame | None = None,
                     countries_no_transport: tuple = (),
                     country_attachment: str = "roads",
                     sector_table=None) -> dict[str, Country]:
    """Create Country objects from MRIO trade data.

    Only countries kept by *selection* (i.e. those that retain at least
    one bilateral cell under flow_coverage) are created. Per-country
    ``qty_purchased`` is built from the kept cells of the country's
    export column, and ``supply_importance`` is computed from the kept
    cells of its import row.

    Countries are assigned to the nearest **road** node so that they connect
    to the road network and reach other modes via multimodal edges.
    If *transport_edges* is provided, only nodes that are endpoints of road
    edges are considered; otherwise all transport nodes are used.

    With ``country_attachment="any"`` the road restriction is lifted: a
    country Point placed at sea snaps to the nearest maritime node, so its
    port of entry becomes a routing decision per buyer instead of a fixed
    gateway (continental scopes with several competing seaboards).
    """
    # Identify countries kept by the flow-coverage selection
    buying = set(selection.external_buying_countries)
    selling = set(selection.external_selling_countries)
    all_countries = sorted(buying | selling)

    # Filter transport nodes to road-only for country placement (legacy rule);
    # "any" keeps every node so sea-placed blocs attach to the maritime layer.
    if country_attachment == "any":
        country_nodes = transport_nodes
        logging.info(f"Country placement on any of the {len(transport_nodes)} transport nodes "
                     f"(country_attachment: any)")
    elif transport_edges is not None and "type" in transport_edges.columns:
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

    # Aggregate kept-cell trade per country, in model units / time_resolution.
    exp_label = mrio.export_label
    imp_label = mrio.import_label

    def _rescale(df):
        return rescale_monetary_values(
            df, input_units=params.monetary_units_in_data,
            input_time_resolution="year",
            target_units=params.monetary_units_in_model,
            target_time_resolution=time_resolution,
        )

    # Per-country export demand from kept cells (buyer = external country)
    exports_by_country: dict[str, dict[str, float]] = {}
    kept_export_cells = [
        (row, col) for (row, col) in selection.kept_cells
        if col[1] == exp_label
    ]
    if kept_export_cells:
        exp_rows = sorted({row for row, _ in kept_export_cells})
        exp_cols = sorted({col for _, col in kept_export_cells})
        exp_sub = _rescale(mrio.loc[exp_rows, exp_cols])
        for row, col in kept_export_cells:
            val = float(exp_sub.at[row, col])
            if val > 0:
                exports_by_country.setdefault(col[0], {})[f"{row[0]}_{row[1]}"] = val

    # Per-country imports (supply) from kept cells (supplier = external country).
    # Import rows are (BLOC, "imports") in the legacy format and (BLOC, sector)
    # in the sector-resolved format — match by region, not label.
    country_set = set(all_countries)
    imports_per_country: dict[str, float] = {}
    kept_import_cells = [
        (row, col) for (row, col) in selection.kept_cells
        if row[0] in country_set
    ]
    # Per-sector density (USD/ton) averaged over regions, for the
    # sector-resolved import format: a country's effective density is the
    # value-weighted harmonic mean over its kept import mix (tons add up).
    sector_density: dict[str, float] = {}
    for key, val in usd_per_ton.items():
        sec = key.split("_", 1)[1] if "_" in key else key
        sector_density.setdefault(sec, []).append(float(val))
    sector_density = {s: sum(v) / len(v) for s, v in sector_density.items() if v}
    country_import_tons: dict[str, float] = {}
    imports_per_cs: dict[tuple, float] = {}
    if kept_import_cells:
        imp_rows = sorted({row for row, _ in kept_import_cells})
        imp_cols = sorted({col for _, col in kept_import_cells})
        imp_sub = _rescale(mrio.loc[imp_rows, imp_cols])
        for row, col in kept_import_cells:
            val = float(imp_sub.at[row, col])
            imports_per_country[row[0]] = imports_per_country.get(row[0], 0.0) + val
            imports_per_cs[(row[0], row[1])] = imports_per_cs.get((row[0], row[1]), 0.0) + val
            dens = sector_density.get(row[1], 0.0)
            if dens > 0:
                country_import_tons[row[0]] = country_import_tons.get(row[0], 0.0) + val / dens
    total_imports = sum(imports_per_country.values()) or 1.0

    # Build countries
    # The MRIO is the source of truth for *which* countries to model. The geojson
    # supplies a point location for each one — except for virtual countries
    # (listed in countries_no_transport), whose flows never touch the transport
    # network and therefore don't need a real location. Such virtual countries
    # are allowed to be absent from the geojson; they are stamped with
    # od_point = -1 (the sentinel _distance_between already understands).
    countries = {}

    # Phase 1: resolve spatial data per country.
    # Each entry is (country_code, centroid_or_None). centroid is None when the
    # country is virtual and missing from the geojson.
    country_specs: list[tuple[str, "object | None"]] = []
    upt_override: dict[str, float] = {}
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
        # Optional per-country import density override (USD/ton) from the
        # geojson: use it when the observed physical trade mix (e.g. BACI
        # value/quantity) contradicts the harmonic density of the kept
        # value mix - value-heavy sectors can mask a physically bulk-heavy
        # trade (Moldova: cable harnesses vs grain and fuel).
        if "usd_per_ton" in countries_gdf.columns:
            v = match.iloc[0].get("usd_per_ton")
            if pd.notna(v) and float(v) > 0:
                upt_override[country_code] = float(v)

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
        # (already restricted to kept cells)
        qty_purchased = dict(exports_by_country.get(country_code, {}))

        # Supply importance: share of kept-cell imports originating here
        supply_importance = (
            imports_per_country.get(country_code, 0.0) / total_imports
            if total_imports > 0 else 0.0
        )

        # USD per ton: exact-match resolution — the country's own import row,
        # then the generic import row, then any import row (deterministic,
        # sorted). The previous substring scan matched the first key merely
        # CONTAINING the code ("US" hit any "AUS_*" row) and could take an
        # arbitrary import row before a country-specific one, dict-order
        # permitting.
        imp = mrio.import_label or "IMP"
        # Sector-resolved import format: value-weighted harmonic density of
        # the country's kept import mix (correct for total tonnage). Legacy
        # fallback: exact-match resolution against the usd_per_ton dict.
        c_val = imports_per_country.get(country_code, 0.0)
        c_tons = country_import_tons.get(country_code, 0.0)
        if c_tons > 0 and c_val > 0:
            country_upt = c_val / c_tons
        else:
            country_upt = 2864.0
            for key in (f"{country_code}_{imp}", country_code, imp,
                        *sorted(k for k in usd_per_ton if k.endswith(f"_{imp}"))):
                if key in usd_per_ton:
                    country_upt = float(usd_per_ton[key])
                    break
        if country_code in upt_override:
            logging.info(
                f"Country {country_code}: usd_per_ton {country_upt:,.0f} -> "
                f"{upt_override[country_code]:,.0f} (override from {geojson_name})")
            country_upt = upt_override[country_code]

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

    # Per-sector import sellers: one sub-agent per kept (country, sector)
    # import cell, pid = the region_sector string buyers carry in input_mix
    # ("UKRW_A01"), sharing the parent's attachment node. Import links then
    # have the same granularity as export links: one product per link, the
    # product's own density and cargo class. The parent country remains the
    # buyer of scope exports and the transit anchor, and sells nothing.
    if getattr(params, "per_sector_import_links", False):
        sec_types = {}
        if sector_table is not None and "type" in sector_table.columns:
            sec_types = sector_table.set_index("sector")["type"].to_dict()
        n_sub, n_scaled = 0, 0
        for (country_code, sector), val in sorted(imports_per_cs.items()):
            parent = countries.get(country_code)
            if parent is None or parent.virtual or val <= 0:
                continue
            dens = float(sector_density.get(sector, 0.0))
            # A country-level usd_per_ton override (observed aggregate density,
            # e.g. BACI value/quantity) rescales every sector density by one
            # factor so the country's TOTAL tonnage matches the observation
            # while the split across products follows relative densities.
            c_val = imports_per_country.get(country_code, 0.0)
            c_tons = country_import_tons.get(country_code, 0.0)
            implied = c_val / c_tons if c_tons > 0 else 0.0
            if country_code in upt_override and implied > 0 and dens > 0:
                dens *= upt_override[country_code] / implied
                n_scaled += 1
            if dens <= 0:
                dens = parent.usd_per_ton
            pid = f"{country_code}_{sector}"
            countries[pid] = Country(
                pid=pid, region=country_code, od_point=parent.od_point,
                name=pid, long=parent.long, lat=parent.lat,
                sector=sector, sector_type=sec_types.get(sector, "imports"),
                region_sector=pid, usd_per_ton=dens,
                monetary_unit_factor=parent.monetary_unit_factor,
                transport_share=parent.transport_share,
                supply_importance=val / total_imports if total_imports > 0 else 0.0,
            )
            n_sub += 1
        logging.info(
            f"per_sector_import_links: {n_sub} per-sector country sellers created"
            + (f" ({n_scaled} with densities rescaled to country overrides)" if n_scaled else ""))

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

    # Add spatial firms sized by the MRIO output of their region_sector,
    # distributed in PROPORTION to the file's per-point values (population,
    # plant capacity, production tonnage...). Units cancel in the within-
    # sector normalization, so any consistent per-sector basis works, but
    # mixing bases within one region_sector is the file producer's problem.
    # Points without a usable value fall back to an equal split - the
    # pre-2026-08-31 behavior, under which supplier choice was effectively
    # distance-only within a region_sector (KI-17).
    total_output = mrio.get_total_output()
    spatial_rows = []
    for rs in sorted(available_rs):   # deterministic firm order (KI-34: set iteration followed the hash seed)
        rs_spatial = spatial[spatial["region_sector"] == rs].copy()
        rs_tuple = tuple(rs.split("_", 1))
        total_out = total_output.get(rs_tuple, 0)
        weights = None
        if "importance" in rs_spatial.columns:
            weights = pd.to_numeric(rs_spatial["importance"], errors="coerce").fillna(0.0)
            weights = weights.clip(lower=0.0)
        if weights is not None and weights.sum() > 0:
            rs_spatial["importance"] = total_out * weights / weights.sum()
        else:
            rs_spatial["importance"] = total_out / max(len(rs_spatial), 1)
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


def _handle_internal_flows(ft: gpd.GeoDataFrame,
                           selection: Selection) -> gpd.GeoDataFrame:
    """Duplicate single-firm region_sectors that have internal consumption.

    A region_sector needs an intra-sector duplicate firm iff its
    self-supply diagonal cell ``(rs, rs)`` survived the flow-coverage
    filter — that is the cell is in ``selection.kept_cells``.
    """
    internal_rs_tuples = {
        row for (row, col) in selection.kept_cells if row == col
    }
    internal_rs_names = {f"{r}_{s}" for (r, s) in internal_rs_tuples}
    logging.info(
        f"Internal flows: {len(internal_rs_names)} region-sectors with self-supply "
        f"surviving flow_coverage={selection.flow_coverage}"
    )

    new_rows = []
    for rs_name in sorted(internal_rs_names):   # deterministic order (KI-34)
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



# ======================================================================
# Transit flows
# ======================================================================

def load_transit_matrix(countries: dict, path, time_resolution: str,
                        monetary_units_in_model: str) -> None:
    """Populate ``Country.transit_from`` from a transit-matrix CSV.

    Transit flows are exogenous background load: goods that neither
    originate nor end in the scope but cross its network (e.g. Ukrainian
    grain leaving through Constanta). They are off-MRIO by design - the
    MRIO covers the scope's own trade - so the matrix is physical:

        from,to,tons_per_year,cargo_type[,note]

    ``from``/``to`` are country pids; both must be sited, non-virtual
    countries or the row is skipped with a warning. The value pushed
    through the supply chain is tons x the seller's usd_per_ton, so
    Country.deliver (which divides by the same density) reproduces
    tons_per_year on the network exactly; the monetary value of transit
    is approximate and never enters scope totals (the buyer books it
    from a Country, not a Firm). cargo_type defaults to dry_bulk.
    """
    df = pd.read_csv(path, comment="#")
    required = {"from", "to", "tons_per_year"}
    if not required.issubset(df.columns):
        raise ValueError(f"transit matrix {path} must have columns {sorted(required)}")
    muf = _UNITS.get(monetary_units_in_model, 1e6)
    days = _DAYS_PER_STEP.get(time_resolution, 7)
    total_mt, n_rows = 0.0, 0
    for _, row in df.iterrows():
        seller_pid, buyer_pid = str(row["from"]).strip(), str(row["to"]).strip()
        tons_per_year = float(row["tons_per_year"])
        if tons_per_year <= 0:
            continue
        problem = None
        if seller_pid == buyer_pid:
            problem = "identical endpoints"
        elif seller_pid not in countries or buyer_pid not in countries:
            problem = "country not in model (dropped by flow_coverage or absent from MRIO)"
        elif countries[seller_pid].virtual or countries[buyer_pid].virtual:
            problem = "virtual country (no network attachment)"
        elif countries[seller_pid].od_point == -1 or countries[buyer_pid].od_point == -1:
            problem = "country has no od_point"
        if problem:
            logging.warning(f"Transit row {seller_pid}->{buyer_pid} skipped: {problem}")
            continue
        seller = countries[seller_pid]
        tons_per_step = tons_per_year * days / 365.0
        quantity = tons_per_step * seller.usd_per_ton / muf  # model units/step
        cargo = str(row["cargo_type"]).strip() if "cargo_type" in df.columns and pd.notna(row.get("cargo_type")) else "dry_bulk"
        spec = countries[buyer_pid].transit_from.setdefault(
            seller_pid, {"quantity": 0.0, "cargo_type": cargo})
        spec["quantity"] += quantity
        spec["cargo_type"] = cargo
        seller.transit_to[buyer_pid] = seller.transit_to.get(buyer_pid, 0.0) + quantity
        total_mt += tons_per_year / 1e6
        n_rows += 1
    logging.info(
        f"Transit matrix {Path(path).name}: {n_rows} flows, "
        f"{total_mt:.1f} Mt/yr riding the network as background load"
    )
