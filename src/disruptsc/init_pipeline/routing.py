"""Assign initial logistics routes to every commercial link in the SC network."""

from __future__ import annotations

import copy
import logging
import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

import networkx as nx
import pandas as pd
from tqdm import tqdm

from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork, _get_cargo_capacity, _capacity_multiplier
from disruptsc.params import TransportParams


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def setup_logistic_routes(
    sc_network,
    transport_network: TransportNetwork,
    firms: dict,
    countries: dict,
    tp: TransportParams,
    nb_cost_profiles: int,
    max_capacity_iterations: int = 3,
) -> pd.DataFrame:
    """Assign routes to every commercial link and return a summary table.

    Uses pre-computed single-source Dijkstra for efficiency.
    When capacity constraints are enabled, runs iterative re-routing
    to distribute flows away from congested edges.
    """
    # 1. Assign cost profiles
    for c in countries.values():
        c.assign_cost_profile(nb_cost_profiles)
    for f in firms.values():
        if hasattr(f, "assign_cost_profile"):
            f.assign_cost_profile(nb_cost_profiles)
        else:
            if nb_cost_profiles > 0:
                f.cost_profile = random.randint(0, nb_cost_profiles - 1)

    # 2. Collect all routable links with their metadata
    link_specs = _collect_link_specs(sc_network, tp)
    if not link_specs:
        logging.info("No routable links found")
        return _build_commercial_link_table(sc_network)

    # 3. Pre-compute routes and assign (with capacity iterations if needed)
    if tp.capacity_constraint_enabled:
        _precompute_and_assign_with_capacity(
            link_specs, transport_network, nb_cost_profiles,
            tp.capacity_constraint_mode, max_capacity_iterations,
        )
    else:
        _precompute_and_assign(link_specs, transport_network, nb_cost_profiles)

    # 4. Build summary table
    cl_table = _build_commercial_link_table(sc_network)

    # 5. Reset loads so simulation starts fresh
    transport_network.reset_loads()

    return cl_table


# ------------------------------------------------------------------
# Link collection
# ------------------------------------------------------------------

def _collect_link_specs(sc_network, tp: TransportParams) -> list[dict]:
    """Collect all commercial links that need transport routing."""
    specs = []
    for supplier, client, data in sc_network.edges(data=True):
        link = data["object"]

        sector_type = getattr(supplier, "sector_type", "")
        if sector_type in tp.sectors_no_transport:
            continue

        client_type = getattr(client, "agent_type", type(client).__name__.lower())
        if client_type == "household" and not tp.transport_to_households:
            continue

        if link.product_type in tp.sectors_no_transport:
            continue

        if not tp.with_transport:
            continue

        specs.append({
            "link": link,
            "origin": supplier.od_point,
            "destination": client.od_point,
            "cost_profile": getattr(supplier, "cost_profile", 0),
            "cargo_type": link.cargo_type,
            "tons": link.delivery_in_tons if link.delivery_in_tons > 0 else 0,
        })

    logging.info(f"Collected {len(specs)} routable commercial links")
    return specs


# ------------------------------------------------------------------
# Pre-computation without capacity constraints
# ------------------------------------------------------------------

def _precompute_and_assign(link_specs: list[dict],
                           transport_network: TransportNetwork,
                           nb_cost_profiles: int):
    """Pre-compute shortest paths and assign routes to links."""

    # Group links by (cost_profile, cargo_type) to batch Dijkstra runs
    combos = _get_profile_cargo_combos(link_specs)

    # Pre-compute all paths for each combo
    path_lookup = {}  # (profile, cargo_type, source, dest) -> node_list
    for profile, cargo_type in combos:
        weight = f"cost_per_ton_{profile}_{cargo_type}"
        sources = {s["origin"] for s in link_specs
                   if s["cost_profile"] == profile and s["cargo_type"] == cargo_type}

        logging.info(f"Pre-computing routes: profile={profile}, cargo={cargo_type}, "
                     f"{len(sources)} sources")

        for source in sources:
            try:
                paths = nx.single_source_dijkstra_path(
                    transport_network, source, weight=weight,
                )
            except nx.NetworkXError:
                paths = {}
            for dest, path in paths.items():
                path_lookup[(profile, cargo_type, source, dest)] = path

    # Assign routes to links
    _assign_routes_from_lookup(link_specs, path_lookup, transport_network)

    # Populate the route cache for simulation-time use
    _populate_route_cache(link_specs, transport_network)


# ------------------------------------------------------------------
# Pre-computation with iterative capacity feedback
# ------------------------------------------------------------------

def _precompute_and_assign_with_capacity(
    link_specs: list[dict],
    transport_network: TransportNetwork,
    nb_cost_profiles: int,
    capacity_constraint_mode: str,
    max_iterations: int,
):
    """Pre-compute routes with iterative congestion feedback.

    Round 0: Compute shortest paths on base costs, assign all flows.
    Round 1..N: Update capacity costs on congested edges, re-compute
    paths from affected sources, re-assign affected links.
    """
    combos = _get_profile_cargo_combos(link_specs)
    cargo_types = transport_network.cargo_types or []

    # --- Round 0: unconstrained ---
    logging.info("Capacity routing: Round 0 (unconstrained)")
    path_lookup = {}
    for profile, cargo_type in combos:
        weight = f"cost_per_ton_{profile}_{cargo_type}"
        sources = {s["origin"] for s in link_specs
                   if s["cost_profile"] == profile and s["cargo_type"] == cargo_type}

        for source in sources:
            try:
                paths = nx.single_source_dijkstra_path(
                    transport_network, source, weight=weight,
                )
            except nx.NetworkXError:
                paths = {}
            for dest, path in paths.items():
                path_lookup[(profile, cargo_type, source, dest)] = path

    _assign_routes_from_lookup(link_specs, path_lookup, transport_network)

    # Accumulate loads from round 0
    transport_network.reset_loads()
    _accumulate_loads(link_specs, transport_network)

    # --- Rounds 1..N: congestion correction ---
    for iteration in range(1, max_iterations + 1):
        # Update capacity costs based on current loads
        _update_capacity_costs(transport_network, cargo_types, capacity_constraint_mode)

        # Find congested edges
        congested_edges = _find_congested_edges(transport_network, cargo_types, threshold=0.8)
        if not congested_edges:
            logging.info(f"Capacity routing: converged after {iteration} iterations (no congestion)")
            break

        logging.info(f"Capacity routing: Round {iteration}, "
                     f"{len(congested_edges)} congested edges")

        # Find affected sources: any source with a route through a congested edge
        affected_sources = _find_affected_sources(link_specs, congested_edges)
        if not affected_sources:
            break

        logging.info(f"  Re-routing {len(affected_sources)} affected sources")

        # Re-compute paths from affected sources using capacity-adjusted costs
        for profile, cargo_type in combos:
            weight = f"cost_per_ton_with_capacity_{profile}_{cargo_type}"
            combo_sources = affected_sources & {
                s["origin"] for s in link_specs
                if s["cost_profile"] == profile and s["cargo_type"] == cargo_type
            }
            for source in combo_sources:
                try:
                    paths = nx.single_source_dijkstra_path(
                        transport_network, source, weight=weight,
                    )
                except nx.NetworkXError:
                    paths = {}
                for dest, path in paths.items():
                    path_lookup[(profile, cargo_type, source, dest)] = path

        # Re-assign and re-accumulate
        _assign_routes_from_lookup(link_specs, path_lookup, transport_network)
        transport_network.reset_loads()
        _accumulate_loads(link_specs, transport_network)
    else:
        n_congested = len(_find_congested_edges(transport_network, cargo_types, threshold=1.0))
        if n_congested:
            logging.warning(f"Capacity routing: {n_congested} edges still over-capacity "
                            f"after {max_iterations} iterations")

    # Populate route cache for simulation-time use
    _populate_route_cache(link_specs, transport_network)


# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------

def _get_profile_cargo_combos(link_specs: list[dict]) -> set[tuple[int, str]]:
    """Get unique (cost_profile, cargo_type) combinations from link specs."""
    return {(s["cost_profile"], s["cargo_type"]) for s in link_specs}


def _assign_routes_from_lookup(link_specs: list[dict], path_lookup: dict,
                               transport_network: TransportNetwork):
    """Assign Route objects to links from the pre-computed path lookup."""
    assigned = 0
    no_route = 0
    for spec in link_specs:
        key = (spec["cost_profile"], spec["cargo_type"], spec["origin"], spec["destination"])
        path = path_lookup.get(key)
        link = spec["link"]

        if path is None or len(path) < 2:
            if spec["origin"] != spec["destination"]:
                no_route += 1
            continue

        route = Route(path, transport_network, spec["cargo_type"])
        cost_label = f"cost_per_ton_{spec['cost_profile']}_{spec['cargo_type']}"
        cost_per_ton = route.sum_indicator(transport_network, cost_label)
        link.store_route_information(route, "main", cost_per_ton)
        spec["route"] = route  # store for capacity tracking
        assigned += 1

    logging.info(f"  Assigned {assigned} routes ({no_route} unreachable)")


def _accumulate_loads(link_specs: list[dict], transport_network: TransportNetwork):
    """Add tonnage from all links onto their route edges (per cargo type)."""
    for spec in link_specs:
        route = spec.get("route") or spec["link"].route
        if route is None or spec["tons"] <= 0:
            continue
        cargo_type = spec["cargo_type"]
        for u, v in route.transport_edges:
            edge = transport_network[u][v]
            load_key = f"current_load_{cargo_type}"
            edge[load_key] = edge.get(load_key, 0) + spec["tons"]


def _update_capacity_costs(transport_network: TransportNetwork,
                           cargo_types: list, mode: str):
    """Update cost_per_ton_with_capacity based on current loads."""
    for u, v in transport_network.edges:
        edge = transport_network[u][v]
        shared_cap = edge.get("capacity", 1e9)
        total_load = sum(edge.get(f"current_load_{ct}", 0) for ct in cargo_types)

        for ct in cargo_types:
            ct_cap = _get_cargo_capacity(edge, ct)
            ct_load = edge.get(f"current_load_{ct}", 0)

            if ct_cap == 0:
                continue  # blocked — already TRANSPORT_MALUS

            # Multiplier from per-cargo-type capacity
            ct_mult = _capacity_multiplier(ct_load, ct_cap) if ct_cap < 1e8 else 1.0
            # Multiplier from shared capacity (only if no per-ct cap defined)
            has_ct_cap = f"capacity_{ct}" in edge
            shared_mult = _capacity_multiplier(total_load, shared_cap) if not has_ct_cap else 1.0
            mult = max(ct_mult, shared_mult)

            # Update with_capacity cost labels for this cargo type
            for key in list(edge.keys()):
                if key.startswith("cost_per_ton_") and key.endswith(f"_{ct}") and "with_capacity" not in key:
                    cap_key = key.replace("cost_per_ton_", "cost_per_ton_with_capacity_")
                    if edge[key] < 1e8:  # not TRANSPORT_MALUS
                        edge[cap_key] = edge[key] * mult


def _find_congested_edges(transport_network: TransportNetwork,
                          cargo_types: list, threshold: float) -> set[tuple]:
    """Find edges where load/capacity exceeds threshold for any cargo type."""
    congested = set()
    for u, v in transport_network.edges:
        edge = transport_network[u][v]
        shared_cap = edge.get("capacity", 1e9)
        total_load = sum(edge.get(f"current_load_{ct}", 0) for ct in cargo_types)

        if shared_cap < 1e8 and total_load / shared_cap > threshold:
            congested.add((u, v))
            continue

        for ct in cargo_types:
            ct_cap_key = f"capacity_{ct}"
            if ct_cap_key in edge:
                ct_cap = edge[ct_cap_key]
                ct_load = edge.get(f"current_load_{ct}", 0)
                if ct_cap > 0 and ct_cap < 1e8 and ct_load / ct_cap > threshold:
                    congested.add((u, v))
                    break

    return congested


def _find_affected_sources(link_specs: list[dict],
                           congested_edges: set[tuple]) -> set[int]:
    """Find source od_points that have routes passing through congested edges."""
    affected = set()
    for spec in link_specs:
        route = spec.get("route") or spec["link"].route
        if route is None:
            continue
        for u, v in route.transport_edges:
            if (u, v) in congested_edges:
                affected.add(spec["origin"])
                break
    return affected


def _populate_route_cache(link_specs: list[dict],
                          transport_network: TransportNetwork):
    """Populate the transport network's route cache from assigned routes."""
    cached = 0
    for spec in link_specs:
        link = spec["link"]
        if link.route is None:
            continue
        transport_network.cache_route(
            spec["origin"], spec["destination"],
            spec["cost_profile"], "normal", spec["cargo_type"],
            link.route,
        )
        cached += 1
    logging.info(f"Cached {cached} routes")


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
            "cargo_type": link.cargo_type,
            "use_transport_network": link.use_transport_network,
            "from": link.route.transport_nodes[0] if link.use_transport_network and link.route else None,
            "to": link.route.transport_nodes[-1] if link.use_transport_network and link.route else None,
            "transport_modes": link.route.transport_modes if link.use_transport_network and link.route else None,
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "pid"
    return df
