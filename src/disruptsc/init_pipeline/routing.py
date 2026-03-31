"""Assign initial logistics routes to every commercial link in the SC network."""

from __future__ import annotations

import logging
import math

import networkx as nx
import pandas as pd

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
    max_capacity_iterations: int = 3,
) -> pd.DataFrame:
    """Assign routes to every commercial link and return a summary table.

    Uses pre-computed single-source Dijkstra for efficiency.
    When capacity constraints are enabled, runs iterative chunk-based
    re-routing to distribute flows away from congested edges.
    """
    # 1. Collect all routable links with their metadata
    link_specs = _collect_link_specs(sc_network, tp)
    if not link_specs:
        logging.info("No routable links found")
        return _build_commercial_link_table(sc_network)

    # 2. Pre-compute routes and assign (with capacity iterations if needed)
    if tp.capacity_constraint_enabled:
        _precompute_and_assign_with_capacity(
            link_specs, transport_network,
            tp.capacity_constraint_mode, max_capacity_iterations,
            tp.chunk_size,
        )
    else:
        _precompute_and_assign(link_specs, transport_network)

    # 3. Build summary table
    cl_table = _build_commercial_link_table(sc_network)

    # 4. Reset loads so simulation starts fresh
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

        # Estimate tons from equilibrium order (set by set_initial_conditions)
        # In equilibrium delivery = order, so this is exact.
        tons = link.delivery_in_tons
        if tons <= 0 and link.order > 0:
            usd_per_ton = getattr(supplier, "usd_per_ton", 1.0)
            monetary_factor = getattr(supplier, "monetary_unit_factor", 1.0)
            tons = link.order * monetary_factor / usd_per_ton if usd_per_ton > 0 else 0.0

        specs.append({
            "link": link,
            "origin": supplier.od_point,
            "destination": client.od_point,
            "cargo_type": link.cargo_type,
            "tons": tons,
        })

    logging.info(f"Collected {len(specs)} routable commercial links")
    return specs


# ------------------------------------------------------------------
# Pre-computation without capacity constraints
# ------------------------------------------------------------------

def _precompute_and_assign(link_specs: list[dict],
                           transport_network: TransportNetwork):
    """Pre-compute shortest paths and assign routes to links."""

    # Group links by cargo_type to batch Dijkstra runs
    cargo_types = _get_cargo_types(link_specs)

    # Pre-compute all paths for each cargo type
    path_lookup = {}  # (cargo_type, source, dest) -> node_list
    for cargo_type in cargo_types:
        weight = f"cost_per_ton_{cargo_type}"
        # Subgraph with only edges that carry this cargo type
        subgraph = _cargo_subgraph(transport_network, weight)
        sources = {s["origin"] for s in link_specs
                   if s["cargo_type"] == cargo_type}

        logging.info(f"Pre-computing routes: cargo={cargo_type}, "
                     f"{len(sources)} sources, {subgraph.number_of_edges()} edges")

        for source in sources:
            try:
                paths = nx.single_source_dijkstra_path(
                    subgraph, source, weight=weight,
                )
            except nx.NetworkXError:
                paths = {}
            for dest, path in paths.items():
                path_lookup[(cargo_type, source, dest)] = path

    # Assign routes to links (single route per link → route_plan with 1 entry)
    _assign_routes_from_lookup(link_specs, path_lookup, transport_network)

    # Set route_plan = [(route, 1.0)] for each link
    for spec in link_specs:
        link = spec["link"]
        if link.route is not None:
            link.route_plan = [(link.route, 1.0)]

    # Populate the route cache for simulation-time use
    _populate_route_cache(link_specs, transport_network)


# ------------------------------------------------------------------
# Pre-computation with iterative capacity feedback (chunked)
# ------------------------------------------------------------------

def _precompute_and_assign_with_capacity(
    link_specs: list[dict],
    transport_network: TransportNetwork,
    capacity_constraint_mode: str,
    max_iterations: int,
    chunk_size: float,
):
    """Pre-compute routes with chunk-based iterative congestion feedback.

    Each link's tonnage is split into chunks of *chunk_size* tons.
    Round 0: assign one chunk per link using unconstrained costs.
    Subsequent rounds: update capacity costs, recompute routes from
    sources with remaining chunks, assign next batch of chunks.
    This naturally distributes large flows across multiple ports.
    """
    all_cargo_types = _get_cargo_types(link_specs)
    network_cargo_types = transport_network.cargo_types or []

    # --- Prepare chunk tracking per link spec ---
    for spec in link_specs:
        tons = spec["tons"]
        n_chunks = max(1, math.ceil(tons / chunk_size)) if tons > 0 else 1
        spec["chunk_tons"] = tons / n_chunks if n_chunks > 0 else 0
        spec["n_chunks"] = n_chunks
        spec["chunks_assigned"] = 0
        spec["route_plan_entries"] = []  # [(Route, tons), ...]

    total_chunks = sum(s["n_chunks"] for s in link_specs)
    logging.info(f"Capacity routing: {len(link_specs)} links, "
                 f"{total_chunks} chunks (chunk_size={chunk_size:.0f} t)")

    # --- Round 0: compute shortest paths (unconstrained) ---
    path_lookup = {}
    for cargo_type in all_cargo_types:
        weight = f"cost_per_ton_{cargo_type}"
        subgraph = _cargo_subgraph(transport_network, weight)
        sources = {s["origin"] for s in link_specs
                   if s["cargo_type"] == cargo_type}

        for source in sources:
            try:
                paths = nx.single_source_dijkstra_path(
                    subgraph, source, weight=weight,
                )
            except nx.NetworkXError:
                paths = {}
            for dest, path in paths.items():
                path_lookup[(cargo_type, source, dest)] = path

    # Assign initial routes (one route per link for primary route / cache)
    _assign_routes_from_lookup(link_specs, path_lookup, transport_network)

    # --- Assign first chunk for each link ---
    transport_network.reset_loads()
    _assign_chunk_batch(link_specs, path_lookup, transport_network)

    chunks_done = sum(s["chunks_assigned"] for s in link_specs)
    logging.info(f"Capacity routing: Round 0 assigned {chunks_done}/{total_chunks} chunks")

    # --- Subsequent rounds: capacity-aware chunk assignment ---
    round_num = 0
    max_chunk_rounds = max(s["n_chunks"] for s in link_specs) + max_iterations
    while True:
        round_num += 1
        if round_num > max_chunk_rounds:
            logging.warning(f"Capacity routing: reached max rounds ({max_chunk_rounds})")
            break

        # Any remaining chunks?
        remaining_specs = [s for s in link_specs if s["chunks_assigned"] < s["n_chunks"]]
        if not remaining_specs:
            logging.info(f"Capacity routing: all chunks assigned after {round_num} rounds")
            break

        # Update capacity costs
        _update_capacity_costs(transport_network, network_cargo_types, capacity_constraint_mode)

        # Recompute routes from sources with remaining chunks
        remaining_sources = {s["origin"] for s in remaining_specs}
        for cargo_type in all_cargo_types:
            weight = f"cost_per_ton_with_capacity_{cargo_type}"
            subgraph = _cargo_subgraph(transport_network, weight)
            combo_sources = remaining_sources & {
                s["origin"] for s in remaining_specs
                if s["cargo_type"] == cargo_type
            }
            for source in combo_sources:
                try:
                    paths = nx.single_source_dijkstra_path(
                        subgraph, source, weight=weight,
                    )
                except nx.NetworkXError:
                    paths = {}
                for dest, path in paths.items():
                    path_lookup[(cargo_type, source, dest)] = path

        # Assign next chunk batch
        newly_assigned = _assign_chunk_batch(remaining_specs, path_lookup, transport_network)
        if newly_assigned == 0:
            logging.warning("Capacity routing: no chunks assigned in this round (unreachable?)")
            break

        chunks_done = sum(s["chunks_assigned"] for s in link_specs)
        logging.info(f"Capacity routing: Round {round_num} — "
                     f"{chunks_done}/{total_chunks} chunks assigned")

    # --- Build route_plan on each link ---
    _build_route_plans(link_specs)

    # Log summary
    n_multi = sum(1 for s in link_specs if len(s["link"].route_plan) > 1)
    if n_multi:
        logging.info(f"Capacity routing: {n_multi} links split across multiple routes")

    # Check remaining congestion
    n_congested = len(_find_congested_edges(transport_network, network_cargo_types, threshold=1.0))
    if n_congested:
        logging.warning(f"Capacity routing: {n_congested} edges still over-capacity")

    # Populate route cache for simulation-time use
    _populate_route_cache(link_specs, transport_network)


def _assign_chunk_batch(link_specs: list[dict], path_lookup: dict,
                        transport_network: TransportNetwork) -> int:
    """Assign one chunk per link that has remaining chunks.  Returns count assigned."""
    assigned = 0
    for spec in link_specs:
        if spec["chunks_assigned"] >= spec["n_chunks"]:
            continue
        key = (spec["cargo_type"], spec["origin"], spec["destination"])
        path = path_lookup.get(key)
        if path is None or len(path) < 2:
            continue

        route = Route(path, transport_network, spec["cargo_type"])
        chunk_tons = spec["chunk_tons"]

        # Accumulate load on edges
        cargo_type = spec["cargo_type"]
        for u, v in route.transport_edges:
            edge = transport_network[u][v]
            load_key = f"current_load_{cargo_type}"
            edge[load_key] = edge.get(load_key, 0) + chunk_tons

        spec["route_plan_entries"].append((route, chunk_tons))
        spec["chunks_assigned"] += 1
        assigned += 1

    return assigned


def _build_route_plans(link_specs: list[dict]):
    """Consolidate chunk entries into route_plan (Route, fraction) on each link."""
    for spec in link_specs:
        entries = spec["route_plan_entries"]
        link = spec["link"]

        if not entries:
            link.route_plan = [(link.route, 1.0)] if link.route else []
            continue

        # Merge entries with the same route (compare by node list)
        merged = []  # [(Route, tons)]
        for route, tons in entries:
            found = False
            for i, (existing_route, existing_tons) in enumerate(merged):
                if existing_route.transport_nodes == route.transport_nodes:
                    merged[i] = (existing_route, existing_tons + tons)
                    found = True
                    break
            if not found:
                merged.append((route, tons))

        # Convert to fractions
        total_tons = sum(t for _, t in merged)
        if total_tons > 0:
            link.route_plan = [(r, t / total_tons) for r, t in merged]
        else:
            link.route_plan = [(link.route, 1.0)] if link.route else []

        # Primary route = largest fraction (for backward compatibility)
        if link.route_plan:
            link.route_plan.sort(key=lambda x: x[1], reverse=True)
            primary_route = link.route_plan[0][0]
            if link.route is None or primary_route.transport_nodes != link.route.transport_nodes:
                # Update primary route; cost was already set by _assign_routes_from_lookup
                link.route = primary_route


# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------

def _get_cargo_types(link_specs: list[dict]) -> set[str]:
    """Get unique cargo types from link specs."""
    return {s["cargo_type"] for s in link_specs}


def _cargo_subgraph(transport_network: TransportNetwork,
                    weight_attr: str) -> nx.Graph:
    """Return a subgraph view containing only edges that have *weight_attr*.

    Edges where a cargo type has zero capacity have no cost label for that
    cargo type, so they are automatically excluded from routing.
    This is a lightweight view — no data is copied.
    """
    def edge_filter(u, v):
        return weight_attr in transport_network[u][v]

    return nx.subgraph_view(transport_network, filter_edge=edge_filter)


def _assign_routes_from_lookup(link_specs: list[dict], path_lookup: dict,
                               transport_network: TransportNetwork,
                               *, fail_on_unreachable: bool = True):
    """Assign Route objects to links from the pre-computed path lookup."""
    assigned = 0
    unreachable = []
    for spec in link_specs:
        key = (spec["cargo_type"], spec["origin"], spec["destination"])
        path = path_lookup.get(key)
        link = spec["link"]

        if path is None or len(path) < 2:
            if spec["origin"] != spec["destination"]:
                unreachable.append(spec)
            continue

        route = Route(path, transport_network, spec["cargo_type"])
        cost_label = f"cost_per_ton_{spec['cargo_type']}"
        cost_per_ton = route.sum_indicator(transport_network, cost_label)
        link.store_route_information(route, "main", cost_per_ton)
        spec["route"] = route  # store for capacity tracking
        assigned += 1

    logging.info(f"  Assigned {assigned} routes ({len(unreachable)} unreachable)")
    if unreachable and fail_on_unreachable:
        _report_unreachable(unreachable, transport_network)


def _report_unreachable(unreachable: list[dict], transport_network: TransportNetwork):
    """Log diagnostic information about unreachable routes and raise at init."""
    # Collect unique unreachable OD points with coordinates
    problem_nodes = {}  # node_id -> {"lat", "lon", "agents"}
    for spec in unreachable:
        for node_id, role in [(spec["origin"], "origin"), (spec["destination"], "destination")]:
            if node_id not in problem_nodes:
                node_data = transport_network._node.get(node_id, {})
                problem_nodes[node_id] = {
                    "lat": node_data.get("lat", "?"),
                    "lon": node_data.get("long", "?"),
                    "as_origin": 0,
                    "as_destination": 0,
                    "agents": set(),
                }
            problem_nodes[node_id][f"as_{role}"] += 1
            link = spec["link"]
            agent_id = link.supplier_id if role == "origin" else link.buyer_id
            problem_nodes[node_id]["agents"].add(agent_id)

    # Find which nodes are actually disconnected
    # (a node that fails as both origin AND destination is isolated;
    #  a node that fails only as destination may just lack incoming edges)
    isolated_origins = {n for n, info in problem_nodes.items() if info["as_origin"] > 0}
    isolated_dests = {n for n, info in problem_nodes.items() if info["as_destination"] > 0}

    # Check graph connectivity to identify the issue
    components = list(nx.connected_components(nx.Graph(transport_network)))
    if len(components) > 1:
        comp_sizes = sorted([len(c) for c in components], reverse=True)
        logging.error(f"Transport network has {len(components)} disconnected components "
                      f"(sizes: {comp_sizes[:5]}{'...' if len(comp_sizes) > 5 else ''})")

    # Log each problem node
    logging.error(f"Unreachable routes: {len(unreachable)} links cannot be routed. "
                  f"Problem OD nodes ({len(problem_nodes)}):")
    for node_id, info in sorted(problem_nodes.items(),
                                 key=lambda x: x[1]["as_origin"] + x[1]["as_destination"],
                                 reverse=True):
        agents_str = ", ".join(sorted(str(a) for a in info["agents"])[:3])
        if len(info["agents"]) > 3:
            agents_str += f" (+{len(info['agents']) - 3} more)"
        logging.error(
            f"  Node {node_id} ({info['lat']:.4f}, {info['lon']:.4f}): "
            f"{info['as_origin']} as origin, {info['as_destination']} as dest — "
            f"agents: {agents_str}"
        )

    raise RuntimeError(
        f"Cannot initialize: {len(unreachable)} commercial links have no route. "
        f"{len(problem_nodes)} transport nodes are unreachable. "
        f"Check the transport network connectivity around the logged nodes. "
        f"The network has {len(components)} connected component(s)."
    )


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
                continue  # blocked — no cost labels exist for this cargo type

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
            "normal", spec["cargo_type"],
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
            "n_routes": len(link.route_plan) if link.route_plan else 1,
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "pid"
    return df
