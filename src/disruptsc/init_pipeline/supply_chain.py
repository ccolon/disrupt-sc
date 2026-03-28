"""Wire the supply-chain network: supplier selection for firms, households, countries."""

from __future__ import annotations

import logging
import math
import random

import numpy as np

from disruptsc.agents.firm import Firm
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.sc_network import ScNetwork


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

    # 1. Households select retailers (domestic B2C + import B2C)
    logging.info("Households selecting retailers")
    for hh in households.values():
        _household_select_suppliers(
            hh, sc, firms, countries, rs_to_firms,
            nb_suppliers_per_input, weight_localization_household,
            sector_to_cargo_type, import_label, transport_network,
        )

    # 2. Countries select exporters and create transit links
    logging.info("Countries selecting exporters and creating transit links")
    share_exporting = {}
    if sector_table is not None and "share_exporting_firms" in sector_table.columns:
        share_exporting = sector_table.set_index("sector")["share_exporting_firms"].to_dict()

    for country in countries.values():
        _country_select_suppliers(
            country, sc, firms, countries, rs_to_firms,
            share_exporting, sector_to_cargo_type,
        )

    # 3. Firms select B2B + import suppliers
    logging.info("Firms selecting suppliers")
    for firm in firms.values():
        _firm_select_suppliers(
            firm, sc, firms, countries, rs_to_firms,
            nb_suppliers_per_input, weight_localization_firm,
            sector_to_cargo_type, import_label, transport_network,
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

def _household_select_suppliers(hh, sc, firms, countries, rs_to_firms,
                                nb_suppliers_per_input, weight_loc,
                                sector_to_cargo_type, import_label,
                                transport_network):
    hh.purchase_plan = {}
    hh.retailers = {}
    for region_sector, amount in hh.sector_consumption.items():
        supplier_type, ids, weights, distances = _identify_suppliers(
            hh, region_sector, firms, rs_to_firms,
            nb_suppliers_per_input, weight_loc, import_label, transport_network,
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

def _firm_select_suppliers(firm, sc, firms, countries, rs_to_firms,
                           nb_suppliers_per_input, weight_loc,
                           sector_to_cargo_type, import_label,
                           transport_network):
    for sector_id, sector_weight in firm.input_mix.items():
        supplier_type, ids, weights, distances = _identify_suppliers(
            firm, sector_id, firms, rs_to_firms,
            nb_suppliers_per_input, weight_loc, import_label, transport_network,
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

def _identify_suppliers(buyer, region_sector, firms, rs_to_firms,
                        nb_suppliers_per_input, weight_loc, import_label,
                        transport_network):
    """Return (supplier_type, selected_ids, weights, distances|None)."""

    # Import case
    if import_label and import_label in region_sector:
        country_code = region_sector.split("_")[0]
        return "country", [country_code], [1.0], None

    # Firm selection
    potential = list(rs_to_firms.get(region_sector, []))
    # Remove self
    buyer_pid = buyer.pid
    if hasattr(buyer, "region_sector") and buyer.region_sector == region_sector:
        potential = [p for p in potential if p != buyer_pid]

    if not potential:
        raise ValueError(f"{buyer.pid}: no supplier for {region_sector}")

    n = len(potential)
    importances = np.array([firms[p].importance for p in potential], dtype=float)
    raw_dists = np.array([_distance_between(buyer, firms[p], transport_network)
                          for p in potential], dtype=float)
    dists = _rescale(raw_dists)
    weighted = importances / (dists ** weight_loc)

    # Draw nb suppliers
    nb = _draw_nb_suppliers(nb_suppliers_per_input, n)
    probs = weighted / weighted.sum()
    chosen_idx = np.random.choice(n, size=nb, p=probs, replace=False)
    chosen_ids = [potential[i] for i in chosen_idx]
    chosen_w = probs[chosen_idx]
    chosen_w = chosen_w / chosen_w.sum()

    chosen_dists = [raw_dists[i] for i in chosen_idx]
    return "firm", chosen_ids, chosen_w.tolist(), chosen_dists


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

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
    elif nb_suppliers_per_input >= 2:
        nb = 2
    else:
        nb = 2 if random.random() < (nb_suppliers_per_input - 1) else 1
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
