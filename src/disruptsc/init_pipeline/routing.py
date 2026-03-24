"""Assign initial logistics routes to every commercial link in the SC network."""

from __future__ import annotations

import logging
import random

import networkx as nx
import pandas as pd
from tqdm import tqdm

from disruptsc.params import TransportParams


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def setup_logistic_routes(
    sc_network,
    transport_network,
    firms: dict,
    countries: dict,
    tp: TransportParams,
    nb_cost_profiles: int,
) -> pd.DataFrame:
    """Assign routes to every commercial link and return a summary table.

    Steps:
      1. Assign cost profiles to firms & countries.
      2. Choose initial routes for countries (transit + import supply).
      3. Choose initial routes for firms (domestic B2B + export).
      4. Build commercial link table.
      5. Reset transport loads for a clean simulation start.

    Returns
    -------
    pd.DataFrame
        One row per commercial link with route metadata.
    """
    # Assign cost profiles
    for c in countries.values():
        c.assign_cost_profile(nb_cost_profiles)
    for f in firms.values():
        if hasattr(f, "assign_cost_profile"):
            f.assign_cost_profile(nb_cost_profiles)
        else:
            if nb_cost_profiles > 0:
                f.cost_profile = random.randint(0, nb_cost_profiles - 1)

    use_cache = tp.use_route_cache and not tp.capacity_constraint_enabled
    if tp.capacity_constraint_enabled and tp.use_route_cache:
        logging.info("Route caching disabled due to capacity constraints")

    # Countries first (transit/import routes)
    logging.info("Selecting routes for countries")
    for country in tqdm(countries.values(), total=len(countries), desc="Country routes"):
        _choose_initial_routes_for_agent(
            country, sc_network, transport_network, tp, use_cache,
        )

    # Firms second (B2B/export routes)
    logging.info("Selecting routes for firms")
    for firm in tqdm(firms.values(), total=len(firms), desc="Firm routes"):
        _choose_initial_routes_for_agent(
            firm, sc_network, transport_network, tp, use_cache,
        )

    # Build summary table
    cl_table = _build_commercial_link_table(sc_network)

    # Reset loads so simulation starts fresh
    if tp.capacity_constraint_enabled:
        logging.info("Resetting transport loads after route setup")
        transport_network.reset_loads()

    return cl_table


# ------------------------------------------------------------------
# Route selection per agent
# ------------------------------------------------------------------

def _choose_initial_routes_for_agent(agent, sc_network, transport_network, tp, use_cache):
    """For every outgoing edge of *agent*, find and store the cheapest route."""

    agent_type = getattr(agent, "agent_type", type(agent).__name__.lower())
    sector_type = getattr(agent, "sector_type", "")

    for _, client, data in sc_network.out_edges(agent, data=True):
        link = data["object"]

        # Skip if this agent's sector doesn't use transport
        if sector_type in tp.sectors_no_transport:
            continue

        # Skip households when transport_to_households is off
        client_type = getattr(client, "agent_type", type(client).__name__.lower())
        if client_type == "household" and not tp.transport_to_households:
            continue

        # Skip service products
        if link.product_type in tp.sectors_no_transport:
            continue

        if not tp.with_transport:
            continue

        destination = client.od_point
        origin = agent.od_point
        cost_profile = getattr(agent, "cost_profile", 0)

        # Get route
        route = _get_route(
            transport_network, origin, destination,
            link.shipment_method, cost_profile,
            tp.capacity_constraint_enabled, use_cache,
        )

        if route is None:
            logging.warning(
                f"No route {origin}→{destination} for {link.pid} "
                f"(shipment={link.shipment_method})"
            )
            continue

        # Calculate cost
        cost_label = f"cost_per_ton_{cost_profile}_{link.shipment_method}"
        cost_per_ton = route.sum_indicator(transport_network, cost_label)
        link.store_route_information(route, "main", cost_per_ton)

        # Update loads if capacity constrained
        if tp.capacity_constraint_enabled:
            load_tons = link.delivery_in_tons if link.delivery_in_tons > 0 else 0
            if load_tons > 0:
                transport_network.update_load_on_route(
                    route, load_tons,
                    tp.capacity_constraint_enabled,
                    tp.capacity_constraint_mode,
                )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _get_route(transport_network, origin, destination, shipment_method,
               cost_profile, capacity_constraint, use_cache):
    """Get route with optional caching."""

    effective_cache = use_cache and not capacity_constraint

    if effective_cache:
        cached = transport_network.retrieve_cached_route(
            origin, destination, cost_profile, "normal", shipment_method,
        )
        if cached:
            return cached

    weight = f"cost_per_ton_{cost_profile}"
    if capacity_constraint:
        weight = f"cost_per_ton_with_capacity_{cost_profile}"

    route = transport_network.provide_shortest_route(
        origin, destination, shipment_method, route_weight=weight,
    )

    if route and effective_cache:
        transport_network.cache_route(
            origin, destination, cost_profile, "normal", shipment_method, route,
        )

    return route


def _build_commercial_link_table(sc_network) -> pd.DataFrame:
    """Build a summary DataFrame of all commercial links."""
    rows = {}
    for link in nx.get_edge_attributes(sc_network, "object").values():
        rows[link.pid] = {
            "supplier_id": link.supplier_id,
            "buyer_id": link.buyer_id,
            "product": link.product,
            "product_type": link.product_type,
            "category": link.category,
            "shipment_method": link.shipment_method,
            "use_transport_network": link.use_transport_network,
            "from": link.route.transport_nodes[0] if link.use_transport_network and link.route else None,
            "to": link.route.transport_nodes[-1] if link.use_transport_network and link.route else None,
            "transport_modes": link.route.transport_modes if link.use_transport_network and link.route else None,
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "pid"
    return df
