"""Wire the supply-chain network: supplier selection for firms, households, countries."""

from __future__ import annotations

import logging
import math
import random

import numpy as np

from disruptsc.agents.firm import Firm
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.sc_network import ScNetwork
from disruptsc.utils import progress


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def build_supply_chain_network(
    firms: dict,
    households: dict,
    countries: dict,
    mrio,
    sector_table,
    nb_suppliers_per_input: float,
    weight_localization_firm: float,
    weight_localization_household: float,
    sector_to_cargo_type: dict,
    transport_network=None,
) -> ScNetwork:
    """Build full supply-chain graph.  Returns populated ScNetwork."""
    sc = ScNetwork()
    import_label = mrio.import_label

    # --- Build index: region_sector -> [firm_pid, ...] ---
    rs_to_firms = {}
    for f in firms.values():
        rs_to_firms.setdefault(f.region_sector, []).append(f.pid)

    # Precompute per-region-sector candidate arrays (pids, importance, coords)
    # once, so supplier selection can vectorize the distance computation
    # instead of looping in Python over every candidate for every buyer.
    rs_cache, node_lon, node_lat = _build_rs_cache(firms, rs_to_firms, transport_network)
    use_tn = transport_network is not None

    # 1. Households select retailers (domestic B2C + import B2C)
    logging.info("Households selecting retailers")
    for hh in progress(households.values(), "Households", total=len(households)):
        _household_select_suppliers(
            hh, sc, firms, countries, rs_cache,
            nb_suppliers_per_input, weight_localization_household,
            sector_to_cargo_type, import_label, transport_network,
            node_lon, node_lat, use_tn,
        )

    # 2. Countries select exporters and create transit links
    logging.info("Countries selecting exporters and creating transit links")
    share_exporting = {}
    if sector_table is not None and "share_exporting_firms" in sector_table.columns:
        share_exporting = sector_table.set_index("sector")["share_exporting_firms"].to_dict()

    for country in progress(countries.values(), "Countries", total=len(countries)):
        _country_select_suppliers(
            country, sc, firms, countries, rs_to_firms,
            share_exporting, sector_to_cargo_type,
        )

    # 3. Firms select B2B + import suppliers
    logging.info("Firms selecting suppliers")
    for firm in progress(firms.values(), "Firms", total=len(firms)):
        _firm_select_suppliers(
            firm, sc, firms, countries, rs_cache,
            nb_suppliers_per_input, weight_localization_firm,
            sector_to_cargo_type, import_label, transport_network,
            node_lon, node_lat, use_tn,
        )

    # 4. Cleanup: remove disconnected agents
    _cleanup_disconnected(sc, firms, countries, households)

    # 5. Iteratively remove firms without clients
    total_removed = 0
    for iteration in range(10):
        removed = sc.remove_useless_commercial_links()
        if removed == 0:
            logging.info(f"Cleanup converged after {iteration + 1} iterations")
            break
        total_removed += removed
        # Sync firms dict with network
        current_pids = {n.pid for n in sc.nodes() if isinstance(n, Firm)}
        for fid in list(firms.keys()):
            if fid not in current_pids:
                del firms[fid]
    else:
        logging.warning("Cleanup did not converge in 10 iterations")

    if total_removed:
        logging.info(f"Total firms removed in cleanup: {total_removed}")

    logging.info(f"Supply chain: {sc.number_of_nodes()} nodes, {sc.number_of_edges()} edges")
    return sc


# ------------------------------------------------------------------
# Household supplier selection
# ------------------------------------------------------------------

def _household_select_suppliers(hh, sc, firms, countries, rs_cache,
                                nb_suppliers_per_input, weight_loc,
                                sector_to_cargo_type, import_label,
                                transport_network, node_lon, node_lat, use_tn):
    hh.purchase_plan = {}
    hh.retailers = {}
    # National government/investment agents override the globals: no geographic weighting
    # (weight_localization=0) and connect to every supplier in each sector (large nb), so
    # a single aggregate buyer spreads demand by firm size and sees localized disruption.
    w_loc = weight_loc if hh.weight_localization is None else hh.weight_localization
    nb = nb_suppliers_per_input if hh.nb_suppliers is None else hh.nb_suppliers
    for region_sector, amount in hh.sector_consumption.items():
        supplier_type, ids, weights, distances = _identify_suppliers(
            hh, region_sector, rs_cache,
            nb, w_loc, import_label,
            node_lon, node_lat, use_tn,
        )
        for sid, w in zip(ids, weights):
            if supplier_type == "country":
                supplier = countries[sid]
                category = "import_B2C"
                ptype = "imports"
                distance = _distance_between(hh, supplier, transport_network)
            else:
                supplier = firms[sid]
                category = "domestic_B2C"
                ptype = supplier.sector_type
                distance = _distance_between(hh, supplier, transport_network)

            link = CommercialLink(
                pid=f"{sid}->{hh.pid}", product=region_sector, product_type=ptype,
                category=category, origin_node=supplier.od_point,
                destination_node=hh.od_point, supplier_id=sid, buyer_id=hh.pid,
            )
            link.determine_cargo_type(sector_to_cargo_type)
            sc.add_edge(supplier, hh, object=link)
            sc[supplier][hh]["weight"] = w

            hh.purchase_plan[sid] = w * amount
            hh.retailers[sid] = {"sector": region_sector, "weight": w}
            supplier.clients[hh.pid] = {"sector": "households", "share": 0,
                                        "transport_share": 0, "distance": distance}


# ------------------------------------------------------------------
# Country supplier selection
# ------------------------------------------------------------------

def _country_select_suppliers(country, sc, firms, countries, rs_to_firms,
                              share_exporting, sector_to_cargo_type):
    # Transit links
    for selling_pid, quantity in country.transit_from.items():
        seller = countries[selling_pid]
        link = CommercialLink(
            pid=f"{selling_pid}->{country.pid}", product="transit",
            product_type="transit", category="transit",
            origin_node=seller.od_point, destination_node=country.od_point,
            supplier_id=selling_pid, buyer_id=country.pid,
        )
        sc.add_edge(seller, country, object=link)
        sc[seller][country]["weight"] = 1
        country.purchase_plan[selling_pid] = quantity
        seller.clients[country.pid] = {"sector": country.pid, "share": 0, "transport_share": 0}

    # Export links: country buys from domestic firms
    present_rs = set(rs_to_firms.keys())
    for region_sector in list(country.qty_purchased.keys()):
        if region_sector not in present_rs:
            continue
        potential = rs_to_firms[region_sector]

        # How many firms to select
        sector = region_sector.split("_", 1)[1] if "_" in region_sector else region_sector
        if sector in share_exporting:
            nb = max(1, round(len(potential) * share_exporting[sector]))
        else:
            nb = 1
        nb = min(nb, len(potential))

        selected_ids, selected_weights = _select_by_importance(potential, nb, firms)

        for sid, w in zip(selected_ids, selected_weights):
            supplier = firms[sid]
            link = CommercialLink(
                pid=f"{sid}->{country.pid}", product=region_sector,
                product_type=supplier.sector_type, category="export",
                origin_node=supplier.od_point, destination_node=country.od_point,
                supplier_id=sid, buyer_id=country.pid,
            )
            link.determine_cargo_type(sector_to_cargo_type)
            sc.add_edge(supplier, country, object=link)
            sc[supplier][country]["weight"] = w

            country.qty_purchased_perfirm[sid] = {
                "sector": region_sector, "weight": w,
                "amount": country.qty_purchased[region_sector] * w,
            }
            country.purchase_plan[sid] = country.qty_purchased[region_sector] * w
            distance = _distance_between(country, supplier)
            supplier.clients[country.pid] = {"sector": country.pid, "share": 0,
                                             "transport_share": 0, "distance": distance}


# ------------------------------------------------------------------
# Firm supplier selection
# ------------------------------------------------------------------

def _firm_select_suppliers(firm, sc, firms, countries, rs_cache,
                           nb_suppliers_per_input, weight_loc,
                           sector_to_cargo_type, import_label,
                           transport_network, node_lon, node_lat, use_tn):
    for sector_id, sector_weight in firm.input_mix.items():
        supplier_type, ids, weights, distances = _identify_suppliers(
            firm, sector_id, rs_cache,
            nb_suppliers_per_input, weight_loc, import_label,
            node_lon, node_lat, use_tn,
        )
        for sid, w in zip(ids, weights):
            if supplier_type == "country":
                supplier = countries[sid]
                category = "import"
                ptype = "imports"
            else:
                supplier = firms[sid]
                category = "domestic_B2B"
                ptype = supplier.sector_type

            link = CommercialLink(
                pid=f"{sid}->{firm.pid}", product=sector_id, product_type=ptype,
                category=category, origin_node=supplier.od_point,
                destination_node=firm.od_point, supplier_id=sid, buyer_id=firm.pid,
            )
            link.determine_cargo_type(sector_to_cargo_type)
            sc.add_edge(supplier, firm, object=link)
            sc[supplier][firm]["weight"] = sector_weight * w

            firm.suppliers[sid] = {"sector": sector_id, "weight": w, "satisfaction": 1}
            distance = _distance_between(firm, supplier, transport_network)
            supplier.clients[firm.pid] = {"sector": firm.sector, "share": 0,
                                          "transport_share": 0, "distance": distance}


# ------------------------------------------------------------------
# Core supplier identification (shared by firms + households)
# ------------------------------------------------------------------

def _identify_suppliers(buyer, region_sector, rs_cache,
                        nb_suppliers_per_input, weight_loc, import_label,
                        node_lon, node_lat, use_tn):
    """Return (supplier_type, selected_ids, weights, distances|None).

    Vectorized over candidate suppliers: importance and candidate coordinates
    are read from the precomputed per-region-sector cache, and the buyer→
    candidate distances are computed in one numpy op. This is arithmetically
    identical to the old per-candidate Python loop (same candidate order, same
    distance formula), so the ``np.random.choice`` draw is unchanged for a
    given seed.
    """

    # Import case
    if import_label and import_label in region_sector:
        country_code = region_sector.split("_")[0]
        return "country", [country_code], [1.0], None

    entry = rs_cache.get(region_sector)
    if entry is None:
        raise ValueError(f"{buyer.pid}: no supplier for {region_sector}")

    pids = entry["pids"]
    importances = entry["importance"]
    cand_lon, cand_lat, cand_od = entry["lon"], entry["lat"], entry["od"]

    # Remove self (a firm buying from its own region_sector). Households have
    # no region_sector attribute, so this is a no-op for them.
    if getattr(buyer, "region_sector", None) == region_sector:
        keep = entry["pid_arr"] != buyer.pid
        if not keep.all():
            pids = [p for p, m in zip(pids, keep) if m]
            importances = importances[keep]
            cand_lon, cand_lat, cand_od = cand_lon[keep], cand_lat[keep], cand_od[keep]

    n = len(pids)
    if n == 0:
        raise ValueError(f"{buyer.pid}: no supplier for {region_sector}")

    raw_dists = _distances_from_buyer(buyer, cand_lon, cand_lat, cand_od,
                                      node_lon, node_lat, use_tn)
    dists = _rescale(raw_dists)
    weighted = importances / (dists ** weight_loc)

    # Draw nb suppliers
    nb = _draw_nb_suppliers(nb_suppliers_per_input, n)
    probs = weighted / weighted.sum()
    chosen_idx = np.random.choice(n, size=nb, p=probs, replace=False)
    chosen_ids = [pids[i] for i in chosen_idx]
    chosen_w = probs[chosen_idx]
    chosen_w = chosen_w / chosen_w.sum()

    chosen_dists = [raw_dists[i] for i in chosen_idx]
    return "firm", chosen_ids, chosen_w.tolist(), chosen_dists


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _build_rs_cache(firms, rs_to_firms, transport_network):
    """Precompute per-region-sector candidate arrays for fast supplier draws.

    Returns (rs_cache, node_lon, node_lat) where rs_cache[region_sector] holds
    the candidate pids (in ``rs_to_firms`` order) plus numpy arrays of their
    importance, transport-node coordinates, and od_points.
    """
    node_lon, node_lat = {}, {}
    if transport_network is not None:
        for nid, data in transport_network.nodes(data=True):
            node_lon[nid] = data["long"]
            node_lat[nid] = data["lat"]

    rs_cache = {}
    for rs, pid_list in rs_to_firms.items():
        n = len(pid_list)
        imp = np.empty(n, dtype=float)
        lon = np.empty(n, dtype=float)
        lat = np.empty(n, dtype=float)
        od = np.empty(n, dtype=np.int64)
        for i, p in enumerate(pid_list):
            f = firms[p]
            imp[i] = f.importance
            o = getattr(f, "od_point", -1)
            od[i] = o
            if transport_network is not None:
                lon[i] = node_lon.get(o, np.nan)
                lat[i] = node_lat.get(o, np.nan)
            else:
                lon[i] = getattr(f, "long", 0.0)
                lat[i] = getattr(f, "lat", 0.0)
        rs_cache[rs] = {
            "pids": list(pid_list),
            "pid_arr": np.array(pid_list, dtype=object),
            "importance": imp,
            "lon": lon, "lat": lat, "od": od,
        }
    return rs_cache, node_lon, node_lat


def _distances_from_buyer(buyer, cand_lon, cand_lat, cand_od,
                          node_lon, node_lat, use_tn):
    """Vectorized buyer→candidate distances, matching ``_distance_between``.

    Reproduces the scalar path exactly: od_point == -1 on either side -> 1.0;
    with a transport network, ``degrees_to_km`` between transport-node coords
    (same-node -> 0.0); without one, the euclidean lon/lat fallback (0 -> 1.0).
    """
    buyer_od = getattr(buyer, "od_point", -1)
    n = len(cand_od)
    if buyer_od == -1:
        return np.ones(n, dtype=float)

    if use_tn:
        blon = node_lon.get(buyer_od)
        blat = node_lat.get(buyer_od)
        if blon is None:  # buyer node absent from network (shouldn't happen)
            blon, blat = getattr(buyer, "long", 0.0), getattr(buyer, "lat", 0.0)
        lat_km = 111.0 * np.abs(cand_lat - blat)
        lon_km = 111.0 * np.abs(cand_lon - blon) * np.cos(np.radians((blat + cand_lat) / 2.0))
        d = np.sqrt(lat_km ** 2 + lon_km ** 2)
        d = np.where(cand_od == buyer_od, 0.0, d)
    else:
        blon, blat = getattr(buyer, "long", 0.0), getattr(buyer, "lat", 0.0)
        ew = (cand_lon - blon) * 112.5
        ns = (cand_lat - blat) * 111.0
        d = np.sqrt(ew ** 2 + ns ** 2)
        d = np.where(d == 0.0, 1.0, d)  # matches `... or 1.0`

    d = np.where(cand_od == -1, 1.0, d)
    return d


def _distance_between(a, b, transport_network=None):
    if getattr(a, "od_point", -1) == -1 or getattr(b, "od_point", -1) == -1:
        return 1.0
    if transport_network is not None:
        return transport_network.get_distance_between_nodes(a.od_point, b.od_point)
    ax, ay = getattr(a, "long", 0), getattr(a, "lat", 0)
    bx, by = getattr(b, "long", 0), getattr(b, "lat", 0)
    ew = (bx - ax) * 112.5
    ns = (by - ay) * 111
    return math.sqrt(ew ** 2 + ns ** 2) or 1.0


def _rescale(values, lo=0.1, hi=1.0):
    mn, mx = values.min(), values.max()
    if mx - mn < 1e-9:
        return np.full_like(values, (lo + hi) / 2)
    return lo + (values - mn) / (mx - mn) * (hi - lo)


def _draw_nb_suppliers(nb_suppliers_per_input: float, max_available: int) -> int:
    if nb_suppliers_per_input <= 1:
        nb = 1
    elif nb_suppliers_per_input < 2:
        nb = 2 if random.random() < (nb_suppliers_per_input - 1) else 1
    else:
        # Integer >= 2 (unchanged for the default 2). Representative national agents pass
        # a large value to connect to every supplier in the sector (capped at max_available
        # below), so their aggregate demand spreads across firms by size.
        nb = int(round(nb_suppliers_per_input))
    return min(nb, max_available)


def _select_by_importance(potential_pids, nb, firms):
    importances = np.array([firms[p].importance for p in potential_pids], dtype=float)
    importances = _rescale(importances)
    probs = importances / importances.sum()
    chosen = np.random.choice(potential_pids, size=min(nb, len(potential_pids)),
                              p=probs, replace=False).tolist()
    weights = np.array([firms[p].importance for p in chosen], dtype=float)
    weights = weights / weights.sum()
    return chosen, weights.tolist()


def _cleanup_disconnected(sc, firms, countries, households):
    node_pids = {n.pid for n in sc}
    for label, agents in [("firms", firms), ("countries", countries), ("households", households)]:
        to_remove = [pid for pid in agents if pid not in node_pids]
        if to_remove:
            logging.warning(f"Removing {len(to_remove)} disconnected {label}")
            for pid in to_remove:
                del agents[pid]
