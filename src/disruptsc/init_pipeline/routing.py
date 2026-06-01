"""Assign initial logistics routes to every commercial link in the SC network."""

from __future__ import annotations

from collections import defaultdict
import logging
import math
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, lil_matrix

from disruptsc.network.route import Route
from disruptsc.network.transport_network import (
    TransportNetwork,
    _get_cargo_capacity,
    _refresh_edge_capacity_costs,
)
from disruptsc.params import TransportParams
from disruptsc.utils import progress


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

# Aligned with runtime Form A capacity multiplier f(u) in transport_network._capacity_multiplier.
# Slopes are chosen so that the LP piecewise-linear surcharge matches (f(u)-1)·u at breakpoints:
#   h(0.8)=0.0, h(1.0)=1.0, h(1.05)=4.2, h(1.1)=9.9
LP_CAPACITY_BREAKS = (0.8, 1.0, 1.05, 1.1)
LP_CAPACITY_SURCHARGES = (0.0, 5.0, 64.0, 114.0)
LP_OVERFLOW_SURCHARGE = 1200.0  # penalty multiplier for flow beyond overcapacity_limit
LP_SHARE_DROP_THRESHOLD = 0.01
CAPACITY_INF = 1e8

def setup_logistic_routes(
    sc_network,
    transport_network: TransportNetwork,
    firms: dict,
    countries: dict,
    tp: TransportParams,
    max_capacity_iterations: int = 3,
    export_folder: Path | None = None,
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

    modeled_regions = sorted({firm.region for firm in firms.values() if getattr(firm, "region", None)})
    _export_trade_capacity_diagnostic(
        link_specs, transport_network, export_folder, modeled_regions,
    )

    # 2. Pre-compute routes and assign (with capacity iterations if needed)
    if tp.capacity_constraint_enabled:
        if tp.initial_route_assignment == "edge_lp":
            _precompute_and_assign_with_edge_lp(
                link_specs, transport_network, tp, export_folder=export_folder,
            )
        elif tp.initial_route_assignment in ("lp", "candidate_path_lp"):
            _precompute_and_assign_with_capacity_lp(
                link_specs, transport_network, tp, export_folder=export_folder,
            )
        else:
            _precompute_and_assign_with_capacity(
                link_specs, transport_network,
                tp.capacity_constraint_mode, max_capacity_iterations,
                tp.chunk_size,
                tp.route_candidate_count,
                tp.route_candidate_stretch,
                tp.route_candidate_overlap,
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

        if getattr(supplier, "virtual", False) or getattr(client, "virtual", False):
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
            "supplier_region": getattr(supplier, "region", None),
            "buyer_region": getattr(client, "region", None),
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

        for source in progress(sources, f"Dijkstra {cargo_type}", total=len(sources)):
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
# Pre-computation with iterative capacity feedback
# ------------------------------------------------------------------

def _precompute_and_assign_with_capacity(
    link_specs: list[dict],
    transport_network: TransportNetwork,
    capacity_constraint_mode: str,
    max_iterations: int,
    chunk_size: float,
    route_candidate_count: int,
    route_candidate_stretch: float,
    route_candidate_overlap: float,
):
    """Assign routes using OD-cargo groups and a small candidate path set.

    Candidate routes are generated once from base costs for each
    (origin, destination, cargo_type) group. Tonnage is then assigned
    chunk by chunk across those candidates using live congestion-adjusted
    costs, which keeps the runtime manageable while allowing realistic
    corridor shifts.
    """
    _ = max_iterations  # retained for API compatibility with earlier versions
    network_cargo_types = transport_network.cargo_types or []

    od_groups = _build_od_cargo_groups(link_specs, chunk_size)
    total_chunks = sum(g["n_chunks"] for g in od_groups)
    logging.info(
        f"Capacity routing: {len(link_specs)} links aggregated into "
        f"{len(od_groups)} OD-cargo groups, {total_chunks} chunks "
        f"(chunk_size={chunk_size:,.0f} t)"
    )

    _generate_group_candidates(
        od_groups, transport_network,
        candidate_count=route_candidate_count,
        max_stretch=route_candidate_stretch,
        max_overlap=route_candidate_overlap,
    )

    transport_network.reset_loads()
    chunks_done = 0
    round_num = 0
    while chunks_done < total_chunks:
        round_num += 1
        _update_capacity_costs(transport_network, network_cargo_types, capacity_constraint_mode)
        newly_assigned = _assign_group_chunk_round(
            od_groups, transport_network, capacity_constraint_mode,
        )

        if newly_assigned == 0:
            remaining = total_chunks - chunks_done
            logging.warning(
                f"Capacity routing: {remaining} chunks could not be placed on "
                f"candidate routes, falling back to the primary corridor"
            )
            _assign_remaining_group_chunks(
                od_groups, transport_network, capacity_constraint_mode,
            )
            break

        chunks_done += newly_assigned
        if round_num == 1 or round_num % 10 == 0 or chunks_done == total_chunks:
            logging.info(
                f"Capacity routing: Round {round_num} — "
                f"{chunks_done}/{total_chunks} chunks assigned"
            )

    _build_group_route_plans(od_groups, transport_network)
    _assign_group_routes_to_links(od_groups, transport_network)

    n_multi = sum(1 for s in link_specs if len(s["link"].route_plan) > 1)
    if n_multi:
        logging.info(f"Capacity routing: {n_multi} links split across multiple routes")

    n_congested = len(_find_congested_edges(transport_network, network_cargo_types, threshold=1.0))
    if n_congested:
        logging.warning(f"Capacity routing: {n_congested} edges still over-capacity")

    _populate_route_cache(link_specs, transport_network)


def _precompute_and_assign_with_capacity_lp(
    link_specs: list[dict],
    transport_network: TransportNetwork,
    tp: TransportParams,
    export_folder: Path | None = None,
):
    """Assign routes by solving a global path-flow LP over candidate routes."""
    od_groups = _build_od_cargo_groups(link_specs, tp.chunk_size)
    total_tons = sum(group["tons"] for group in od_groups)
    logging.info(
        f"LP routing: {len(link_specs)} links aggregated into "
        f"{len(od_groups)} OD-cargo groups ({total_tons:,.0f} t)"
    )

    _generate_group_candidates(
        od_groups, transport_network,
        candidate_count=max(2, tp.lp_route_candidate_count),
        max_stretch=tp.lp_route_candidate_stretch,
        max_overlap=tp.lp_route_candidate_overlap,
    )
    _export_lp_candidate_diagnostics(od_groups, transport_network, export_folder)

    candidate_records = _build_lp_candidate_records(od_groups)
    logging.info(
        f"LP routing: solving path-flow LP with "
        f"{len(candidate_records)} path variables"
    )

    solution = _solve_path_flow_lp(
        od_groups, candidate_records, transport_network,
        overcapacity_limit=tp.lp_overcapacity_limit,
    )
    _apply_lp_solution(
        od_groups, candidate_records, solution, transport_network,
    )

    n_multi = sum(1 for spec in link_specs if len(spec["link"].route_plan) > 1)
    if n_multi:
        logging.info(f"LP routing: {n_multi} links split across multiple routes")

    n_congested = len(_find_congested_edges(
        transport_network, transport_network.cargo_types or [], threshold=1.0,
    ))
    if n_congested:
        logging.warning(f"LP routing: {n_congested} edges are at or above nominal capacity")

    _export_lp_diagnostics(
        od_groups, transport_network, export_folder,
        overcapacity_limit=tp.lp_overcapacity_limit,
    )
    _populate_route_cache(link_specs, transport_network)


def _build_lp_candidate_records(od_groups: list[dict]) -> list[dict]:
    """Flatten group candidate routes into a variable list for the LP."""
    records = []
    for group_idx, group in enumerate(od_groups):
        for route, base_cost in group.get("candidate_data", []):
            records.append({
                "group_idx": group_idx,
                "route": route,
                "base_cost": float(base_cost),
                "cargo_type": group["cargo_type"],
                "edge_keys": {tuple(sorted((u, v))) for u, v in route.transport_edges},
            })
    return records


def _solve_path_flow_lp(
    od_groups: list[dict],
    candidate_records: list[dict],
    transport_network: TransportNetwork,
    overcapacity_limit: float,
) -> list[float]:
    """Solve a global path-flow LP with piecewise-linear capacity surcharges."""
    if not candidate_records:
        raise RuntimeError("LP routing cannot start: no candidate routes were generated")

    group_to_vars = defaultdict(list)
    edge_to_vars = defaultdict(list)
    edge_ct_to_vars = defaultdict(list)
    edge_lookup = {}

    for var_idx, record in enumerate(candidate_records):
        group_to_vars[record["group_idx"]].append(var_idx)
        cargo_type = record["cargo_type"]
        for edge_key in record["edge_keys"]:
            edge_to_vars[edge_key].append(var_idx)
            edge_ct_to_vars[(edge_key, cargo_type)].append(var_idx)
            if edge_key not in edge_lookup:
                edge_lookup[edge_key] = transport_network[edge_key[0]][edge_key[1]]

    shared_specs = []
    for edge_key, var_ids in edge_to_vars.items():
        edge = edge_lookup[edge_key]
        capacity = float(edge.get("capacity", 1e9))
        if capacity <= 0 or capacity >= CAPACITY_INF:
            continue
        shared_specs.append({
            "edge_key": edge_key,
            "var_ids": var_ids,
            "capacity": capacity,
            "penalty_base": _shared_penalty_base_cost(edge, transport_network.cargo_types or []),
        })

    cargo_specs = []
    for (edge_key, cargo_type), var_ids in edge_ct_to_vars.items():
        edge = edge_lookup[edge_key]
        cap_key = f"capacity_{cargo_type}"
        if cap_key not in edge:
            continue
        capacity = float(_get_cargo_capacity(edge, cargo_type))
        if capacity <= 0 or capacity >= CAPACITY_INF:
            continue
        cargo_specs.append({
            "edge_key": edge_key,
            "cargo_type": cargo_type,
            "var_ids": var_ids,
            "capacity": capacity,
            "penalty_base": _cargo_penalty_base_cost(edge, cargo_type),
        })

    segment_widths = _capacity_segment_widths(overcapacity_limit)
    n_edge_constraints = len(shared_specs) + len(cargo_specs)
    n_path_vars = len(candidate_records)
    # +1 per edge constraint for the overflow segment (unbounded)
    n_seg_vars = n_edge_constraints * (len(segment_widths) + 1)
    n_vars = n_path_vars + n_seg_vars
    n_rows = len(od_groups) + n_edge_constraints

    c = [0.0] * n_vars
    bounds = [(0.0, None)] * n_vars
    for var_idx, record in enumerate(candidate_records):
        c[var_idx] = record["base_cost"]
        bounds[var_idx] = (0.0, od_groups[record["group_idx"]]["tons"])

    row_idx = 0
    A_eq = lil_matrix((n_rows, n_vars), dtype=float)
    b_eq = [0.0] * n_rows

    for group_idx, group in enumerate(od_groups):
        var_ids = group_to_vars.get(group_idx, [])
        if not var_ids:
            raise RuntimeError(
                f"LP routing cannot start: OD-cargo group {group_idx} has no candidate route"
            )
        for var_id in var_ids:
            A_eq[row_idx, var_id] = 1.0
        b_eq[row_idx] = group["tons"]
        row_idx += 1

    n_segs_per_edge = len(segment_widths) + 1  # +1 for overflow

    next_var = n_path_vars
    for spec in shared_specs:
        for var_id in spec["var_ids"]:
            A_eq[row_idx, var_id] = 1.0
        for seg_idx, width in enumerate(segment_widths):
            seg_var = next_var + seg_idx
            A_eq[row_idx, seg_var] = -1.0
            c[seg_var] = spec["penalty_base"] * LP_CAPACITY_SURCHARGES[seg_idx]
            bounds[seg_var] = (0.0, spec["capacity"] * width)
        # Overflow segment: unbounded, very high cost
        overflow_var = next_var + len(segment_widths)
        A_eq[row_idx, overflow_var] = -1.0
        c[overflow_var] = spec["penalty_base"] * LP_OVERFLOW_SURCHARGE
        bounds[overflow_var] = (0.0, None)
        spec["segment_vars"] = list(range(next_var, next_var + n_segs_per_edge))
        next_var += n_segs_per_edge
        row_idx += 1

    for spec in cargo_specs:
        for var_id in spec["var_ids"]:
            A_eq[row_idx, var_id] = 1.0
        for seg_idx, width in enumerate(segment_widths):
            seg_var = next_var + seg_idx
            A_eq[row_idx, seg_var] = -1.0
            c[seg_var] = spec["penalty_base"] * LP_CAPACITY_SURCHARGES[seg_idx]
            bounds[seg_var] = (0.0, spec["capacity"] * width)
        # Overflow segment: unbounded, very high cost
        overflow_var = next_var + len(segment_widths)
        A_eq[row_idx, overflow_var] = -1.0
        c[overflow_var] = spec["penalty_base"] * LP_OVERFLOW_SURCHARGE
        bounds[overflow_var] = (0.0, None)
        spec["segment_vars"] = list(range(next_var, next_var + n_segs_per_edge))
        next_var += n_segs_per_edge
        row_idx += 1

    result = linprog(
        c=c,
        A_eq=A_eq.tocsr(),
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(
            "LP routing failed to find a feasible initial-state assignment. "
            f"Solver message: {result.message}"
        )
    logging.info(
        f"LP routing: solved successfully "
        f"(objective={result.fun:,.2f}, nit={getattr(result, 'nit', '?')})"
    )
    return result.x[:n_path_vars]


def _apply_lp_solution(
    od_groups: list[dict],
    candidate_records: list[dict],
    solution: list[float],
    transport_network: TransportNetwork,
):
    """Map LP path flows back to OD groups, edge loads, and commercial links."""
    by_group = defaultdict(list)
    transport_network.reset_loads()

    for var_idx, flow in enumerate(solution):
        if flow <= 1e-9:
            continue
        record = candidate_records[var_idx]
        by_group[record["group_idx"]].append((record["route"], float(flow), record["base_cost"]))
        for u, v in record["route"].transport_edges:
            edge = transport_network[u][v]
            load_key = f"current_load_{record['cargo_type']}"
            edge[load_key] = edge.get(load_key, 0.0) + float(flow)

    _update_capacity_costs(
        transport_network, transport_network.cargo_types or [], "gradual",
    )

    for group_idx, group in enumerate(od_groups):
        allocations = by_group.get(group_idx, [])
        total_tons = sum(flow for _, flow, _ in allocations)

        if total_tons <= 1e-9:
            route_plan = [(group["candidate_data"][0][0], 1.0)] if group["candidate_data"] else []
            weighted_cost = group["candidate_data"][0][1] if group["candidate_data"] else 0.0
        else:
            route_plan = []
            kept_tons = 0.0
            for route, flow, base_cost in sorted(allocations, key=lambda x: x[1], reverse=True):
                share = flow / total_tons
                if share < LP_SHARE_DROP_THRESHOLD:
                    continue
                route_plan.append((route, flow, base_cost))
                kept_tons += flow
            if not route_plan:
                route, flow, base_cost = max(allocations, key=lambda x: x[1])
                route_plan = [(route, flow, base_cost)]
                kept_tons = flow
            route_plan = [(route, flow / kept_tons, base_cost) for route, flow, base_cost in route_plan]
            weighted_cost = sum(share * base_cost for route, share, base_cost in route_plan)
            route_plan = [(route, share) for route, share, _ in route_plan]

        route_plan.sort(key=lambda x: x[1], reverse=True)
        group["route_plan"] = route_plan
        group["primary_route"] = route_plan[0][0] if route_plan else None
        group["weighted_cost_per_ton"] = weighted_cost

    _assign_group_routes_to_links(od_groups, transport_network)


# ------------------------------------------------------------------
# Edge-based LP (multi-commodity min-cost flow)
# ------------------------------------------------------------------

def _precompute_and_assign_with_edge_lp(
    link_specs: list[dict],
    transport_network: TransportNetwork,
    tp: TransportParams,
    export_folder: Path | None = None,
):
    """Assign routes via multi-commodity min-cost edge-flow LP.

    Unlike the candidate-path LP, this formulation does not pre-generate
    candidate routes.  Variables represent flow per (OD-group, directed arc)
    and the LP finds optimal paths implicitly through flow conservation.
    """
    od_groups = _build_od_cargo_groups(link_specs, tp.chunk_size)
    total_tons = sum(g["tons"] for g in od_groups)
    logging.info(
        f"Edge LP: {len(link_specs)} links -> {len(od_groups)} OD groups "
        f"({total_tons:,.0f} t)"
    )

    # ---- directed-arc tables per cargo type --------------------------------
    cargo_types_used = sorted({g["cargo_type"] for g in od_groups})
    ct_arcs: dict[str, list[tuple[int, int]]] = {}
    ct_arc_costs: dict[str, list[float]] = {}
    ct_arc_idx: dict[str, dict[tuple[int, int], int]] = {}
    ct_nodes: dict[str, list[int]] = {}
    ct_node_idx: dict[str, dict[int, int]] = {}
    ct_arc_node_map: dict[str, np.ndarray] = {}  # (n_arcs, 2) int array

    for ct in cargo_types_used:
        weight = f"cost_per_ton_{ct}"
        arcs, costs, idx_map = [], [], {}
        node_set: set[int] = set()
        for u, v in transport_network.edges:
            if weight not in transport_network[u][v]:
                continue
            cost = float(transport_network[u][v][weight])
            idx_map[(u, v)] = len(arcs); arcs.append((u, v)); costs.append(cost)
            idx_map[(v, u)] = len(arcs); arcs.append((v, u)); costs.append(cost)
            node_set.update((u, v))
        nodes = sorted(node_set)
        node_map = {n: i for i, n in enumerate(nodes)}
        ct_arcs[ct] = arcs
        ct_arc_costs[ct] = costs
        ct_arc_idx[ct] = idx_map
        ct_nodes[ct] = nodes
        ct_node_idx[ct] = node_map
        ct_arc_node_map[ct] = np.array(
            [(node_map[u], node_map[v]) for u, v in arcs], dtype=np.int64,
        )

    # ---- check reachability ------------------------------------------------
    unreachable = []
    for g in od_groups:
        ct = g["cargo_type"]
        nm = ct_node_idx[ct]
        if g["origin"] not in nm or g["destination"] not in nm:
            unreachable.extend(g["members"])
    if unreachable:
        _report_unreachable(unreachable, transport_network)

    # ---- handle same-node groups (origin == destination) --------------------
    # These require no routing; assign trivial routes directly and exclude
    # from the LP (conservation with o_local == d_local would be infeasible).
    lp_group_indices: list[int] = []
    for g_idx, g in enumerate(od_groups):
        if g["origin"] == g["destination"]:
            ct = g["cargo_type"]
            trivial = Route([g["origin"]], transport_network, ct)
            g["route_plan"] = [(trivial, 1.0)]
            g["primary_route"] = trivial
            g["weighted_cost_per_ton"] = 0.0
        else:
            lp_group_indices.append(g_idx)

    if len(lp_group_indices) < len(od_groups):
        n_trivial = len(od_groups) - len(lp_group_indices)
        logging.info(f"Edge LP: {n_trivial} same-node groups assigned trivially")

    # ---- variable layout: [arc vars | segment vars] ------------------------
    var_offsets: list[int] = []
    offset = 0
    for g_idx in lp_group_indices:
        var_offsets.append(offset)
        offset += len(ct_arcs[od_groups[g_idx]["cargo_type"]])
    n_arc_vars = offset

    # ---- capacity-constrained edges ----------------------------------------
    all_edge_keys: set[tuple[int, int]] = set()
    for ct in cargo_types_used:
        for u, v in ct_arcs[ct]:
            all_edge_keys.add(tuple(sorted((u, v))))
    edge_data = {ek: transport_network[ek[0]][ek[1]] for ek in all_edge_keys}

    groups_by_ct: dict[str, list[int]] = defaultdict(list)
    for pos, g_idx in enumerate(lp_group_indices):
        groups_by_ct[od_groups[g_idx]["cargo_type"]].append(pos)

    shared_cap_specs: list[dict] = []
    cargo_cap_specs: list[dict] = []

    n_lp = len(lp_group_indices)

    for ek, edge in edge_data.items():
        # Shared (total) capacity
        shared_cap = float(edge.get("capacity", 1e9))
        if 0 < shared_cap < CAPACITY_INF:
            var_ids = []
            for pos, g_idx in enumerate(lp_group_indices):
                im = ct_arc_idx[od_groups[g_idx]["cargo_type"]]
                base = var_offsets[pos]
                for arc in [ek, (ek[1], ek[0])]:
                    if arc in im:
                        var_ids.append(base + im[arc])
            if var_ids:
                shared_cap_specs.append({
                    "var_ids": var_ids,
                    "capacity": shared_cap,
                    "penalty_base": _shared_penalty_base_cost(edge, cargo_types_used),
                })

        # Per-cargo-type capacity
        for ct in cargo_types_used:
            if f"capacity_{ct}" not in edge:
                continue
            cap = float(_get_cargo_capacity(edge, ct))
            if cap <= 0 or cap >= CAPACITY_INF:
                continue
            im = ct_arc_idx[ct]
            var_ids = []
            for pos in groups_by_ct[ct]:
                base = var_offsets[pos]
                for arc in [ek, (ek[1], ek[0])]:
                    if arc in im:
                        var_ids.append(base + im[arc])
            if var_ids:
                cargo_cap_specs.append({
                    "var_ids": var_ids,
                    "capacity": cap,
                    "penalty_base": _cargo_penalty_base_cost(edge, ct),
                })

    segment_widths = _capacity_segment_widths(tp.lp_overcapacity_limit)
    n_cap_constraints = len(shared_cap_specs) + len(cargo_cap_specs)
    n_segs_per = len(segment_widths) + 1  # +1 overflow
    n_seg_vars = n_cap_constraints * n_segs_per
    # One virtual direct arc per LP group guarantees feasibility even when
    # origin and destination are in disconnected components.
    n_virtual = n_lp
    n_conservation = sum(
        len(ct_nodes[od_groups[g_idx]["cargo_type"]]) for g_idx in lp_group_indices
    )
    n_rows = n_conservation + n_cap_constraints
    # Layout: [arc vars | virtual arc vars | segment vars]
    n_vars = n_arc_vars + n_virtual + n_seg_vars

    logging.info(
        f"Edge LP: {n_vars:,} vars ({n_arc_vars:,} arc + {n_virtual} virtual + "
        f"{n_seg_vars:,} seg), {n_rows:,} rows ({n_conservation:,} conservation + "
        f"{n_cap_constraints:,} capacity)"
    )

    # ---- objective and bounds ----------------------------------------------
    c = np.zeros(n_vars)
    lo = np.zeros(n_vars)
    hi = np.full(n_vars, np.inf)

    for pos, g_idx in enumerate(lp_group_indices):
        g = od_groups[g_idx]
        ct = g["cargo_type"]
        base = var_offsets[pos]
        n_a = len(ct_arc_costs[ct])
        c[base:base + n_a] = ct_arc_costs[ct]
        hi[base:base + n_a] = g["tons"]

    # Virtual arc costs: very high penalty so they are only used as last resort
    for ct in cargo_types_used:
        costs = ct_arc_costs[ct]
        ct_max = max(costs) if costs else 1.0
        ct_arc_costs[f"__virtual_{ct}"] = ct_max  # stash for reuse
    for pos, g_idx in enumerate(lp_group_indices):
        g = od_groups[g_idx]
        virt_var = n_arc_vars + pos
        ct = g["cargo_type"]
        c[virt_var] = ct_arc_costs[f"__virtual_{ct}"] * LP_OVERFLOW_SURCHARGE
        hi[virt_var] = g["tons"]

    # ---- build A_eq in COO (vectorised conservation) -----------------------
    conservation_nnz = sum(
        2 * len(ct_arcs[od_groups[g_idx]["cargo_type"]])
        for g_idx in lp_group_indices
    )
    virtual_nnz = 2 * n_virtual  # +1 at origin, -1 at destination per group
    cap_nnz = sum(len(s["var_ids"]) + n_segs_per for s in shared_cap_specs + cargo_cap_specs)
    total_nnz = conservation_nnz + virtual_nnz + cap_nnz

    row_i = np.empty(total_nnz, dtype=np.int64)
    col_j = np.empty(total_nnz, dtype=np.int64)
    val_v = np.empty(total_nnz, dtype=np.float64)
    b_eq = np.zeros(n_rows)

    ptr = 0
    row_base = 0
    for pos, g_idx in enumerate(lp_group_indices):
        g = od_groups[g_idx]
        ct = g["cargo_type"]
        mapping = ct_arc_node_map[ct]  # (n_arcs, 2)
        base = var_offsets[pos]
        n_a = len(mapping)
        n_nodes = len(ct_nodes[ct])

        o_local = ct_node_idx[ct].get(g["origin"])
        d_local = ct_node_idx[ct].get(g["destination"])
        if o_local is not None:
            b_eq[row_base + o_local] = g["tons"]
        if d_local is not None:
            b_eq[row_base + d_local] = -g["tons"]

        arc_var_ids = np.arange(base, base + n_a, dtype=np.int64)

        # +1 entries (outgoing: row = row_base + u_local)
        row_i[ptr:ptr + n_a] = row_base + mapping[:, 0]
        col_j[ptr:ptr + n_a] = arc_var_ids
        val_v[ptr:ptr + n_a] = 1.0
        ptr += n_a

        # -1 entries (incoming: row = row_base + v_local)
        row_i[ptr:ptr + n_a] = row_base + mapping[:, 1]
        col_j[ptr:ptr + n_a] = arc_var_ids
        val_v[ptr:ptr + n_a] = -1.0
        ptr += n_a

        # Virtual arc: +1 at origin row, -1 at destination row
        virt_var = n_arc_vars + pos
        if o_local is not None:
            row_i[ptr] = row_base + o_local
            col_j[ptr] = virt_var
            val_v[ptr] = 1.0
            ptr += 1
        if d_local is not None:
            row_i[ptr] = row_base + d_local
            col_j[ptr] = virt_var
            val_v[ptr] = -1.0
            ptr += 1

        row_base += n_nodes

    # ---- capacity constraints (appended after conservation) ----------------
    cap_row = n_conservation
    next_seg = n_arc_vars + n_virtual  # segment vars start after virtual arcs
    for spec in shared_cap_specs + cargo_cap_specs:
        # Flow variables
        for vid in spec["var_ids"]:
            row_i[ptr] = cap_row; col_j[ptr] = vid; val_v[ptr] = 1.0; ptr += 1
        # Segment variables
        for s_idx, width in enumerate(segment_widths):
            sv = next_seg + s_idx
            row_i[ptr] = cap_row; col_j[ptr] = sv; val_v[ptr] = -1.0; ptr += 1
            c[sv] = spec["penalty_base"] * LP_CAPACITY_SURCHARGES[s_idx]
            hi[sv] = spec["capacity"] * width
        # Overflow variable
        ov = next_seg + len(segment_widths)
        row_i[ptr] = cap_row; col_j[ptr] = ov; val_v[ptr] = -1.0; ptr += 1
        c[ov] = spec["penalty_base"] * LP_OVERFLOW_SURCHARGE
        hi[ov] = np.inf
        next_seg += n_segs_per
        cap_row += 1

    A_eq = coo_matrix(
        (val_v[:ptr], (row_i[:ptr], col_j[:ptr])), shape=(n_rows, n_vars),
    ).tocsr()

    bounds = list(zip(lo.tolist(), hi.tolist()))

    # ---- solve -------------------------------------------------------------
    result = linprog(
        c=c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs",
    )
    if not result.success:
        raise RuntimeError(f"Edge LP failed: {result.message}")

    # Check virtual arc usage (indicates disconnected OD pairs)
    virtual_usage = sum(
        float(result.x[n_arc_vars + pos]) for pos in range(n_lp)
    )
    if virtual_usage > 1e-3:
        n_using = sum(
            1 for pos in range(n_lp)
            if result.x[n_arc_vars + pos] > 1e-3
        )
        logging.warning(
            f"Edge LP: {n_using} groups used virtual arcs "
            f"({virtual_usage:,.0f} t unroutable)"
        )

    logging.info(
        f"Edge LP: solved (obj={result.fun:,.2f}, "
        f"nit={getattr(result, 'nit', '?')})"
    )

    # ---- decompose arc flows into paths and build route plans --------------
    transport_network.reset_loads()

    for pos, g_idx in enumerate(lp_group_indices):
        g = od_groups[g_idx]
        ct = g["cargo_type"]
        arcs = ct_arcs[ct]
        base = var_offsets[pos]

        edge_flows: dict[tuple[int, int], float] = {}
        for a_idx, (u, v) in enumerate(arcs):
            f = float(result.x[base + a_idx])
            if f > 1e-9:
                edge_flows[(u, v)] = f

        if not edge_flows:
            trivial = Route([g["origin"]], transport_network, ct)
            g["route_plan"] = [(trivial, 1.0)]
            g["primary_route"] = trivial
            g["weighted_cost_per_ton"] = 0.0
            continue

        paths_flows = _decompose_edge_flows(
            edge_flows, g["origin"], g["destination"],
        )

        total_flow = sum(f for _, f in paths_flows)
        route_plan: list[tuple[Route, float]] = []
        if total_flow > 1e-9:
            for path, flow in paths_flows:
                share = flow / total_flow
                if share < LP_SHARE_DROP_THRESHOLD:
                    continue
                try:
                    route = Route(path, transport_network, ct)
                    route_plan.append((route, share))
                except (KeyError, IndexError):
                    continue

        if not route_plan:
            # Emergency fallback: shortest path
            weight = f"cost_per_ton_{ct}"
            sg = _cargo_subgraph(transport_network, weight)
            try:
                p = nx.shortest_path(sg, g["origin"], g["destination"], weight=weight)
                route_plan = [(Route(p, transport_network, ct), 1.0)]
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                pass

        # Normalise shares
        total_share = sum(s for _, s in route_plan)
        if total_share > 0 and abs(total_share - 1.0) > 1e-6:
            route_plan = [(r, s / total_share) for r, s in route_plan]
        route_plan.sort(key=lambda x: x[1], reverse=True)

        g["route_plan"] = route_plan
        g["primary_route"] = route_plan[0][0] if route_plan else None
        g["weighted_cost_per_ton"] = sum(
            share * route.sum_indicator(transport_network, f"cost_per_ton_{ct}")
            for route, share in route_plan
        )

        # Accumulate loads on edges
        for route, share in route_plan:
            tons = g["tons"] * share
            for u, v in route.transport_edges:
                edge = transport_network[u][v]
                lk = f"current_load_{ct}"
                edge[lk] = edge.get(lk, 0.0) + tons

    _update_capacity_costs(
        transport_network, transport_network.cargo_types or [], "gradual",
    )
    _assign_group_routes_to_links(od_groups, transport_network)

    n_multi = sum(1 for s in link_specs if len(s["link"].route_plan) > 1)
    if n_multi:
        logging.info(f"Edge LP: {n_multi} links split across multiple routes")
    n_congested = len(_find_congested_edges(
        transport_network, transport_network.cargo_types or [], threshold=1.0,
    ))
    if n_congested:
        logging.warning(
            f"Edge LP: {n_congested} edges at or above nominal capacity"
        )

    _export_lp_diagnostics(
        od_groups, transport_network, export_folder, tp.lp_overcapacity_limit,
    )
    _populate_route_cache(link_specs, transport_network)


# ------------------------------------------------------------------
# Flow decomposition (edge flows → paths)
# ------------------------------------------------------------------

def _decompose_edge_flows(
    edge_flows: dict[tuple[int, int], float],
    origin: int,
    destination: int,
) -> list[tuple[list[int], float]]:
    """Decompose directed-arc flows into origin->destination paths.

    Standard successive-path decomposition: find a path with positive flow,
    record the bottleneck, subtract it, repeat.
    """
    flows = {k: v for k, v in edge_flows.items() if v > 1e-12}
    paths: list[tuple[list[int], float]] = []

    for _ in range(500):  # safety bound
        path = _find_flow_path(flows, origin, destination)
        if path is None:
            break
        bottleneck = min(flows[(path[i], path[i + 1])] for i in range(len(path) - 1))
        if bottleneck < 1e-12:
            break
        for i in range(len(path) - 1):
            arc = (path[i], path[i + 1])
            flows[arc] -= bottleneck
            if flows[arc] < 1e-12:
                del flows[arc]
        paths.append((path, bottleneck))

    return paths


def _find_flow_path(
    flows: dict[tuple[int, int], float],
    origin: int,
    destination: int,
) -> list[int] | None:
    """DFS from *origin* to *destination* following arcs with positive flow."""
    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in flows:
        adj[u].append(v)

    parent: dict[int, int | None] = {origin: None}
    stack = [origin]
    while stack:
        node = stack.pop()
        if node == destination:
            path: list[int] = []
            n: int | None = destination
            while n is not None:
                path.append(n)
                n = parent[n]
            return path[::-1]
        for nb in adj[node]:
            if nb not in parent:
                parent[nb] = node
                stack.append(nb)
    return None


def _capacity_segment_widths(overcapacity_limit: float) -> list[float]:
    """Convert absolute utilization breakpoints into successive segment widths."""
    effective_breaks = [b for b in LP_CAPACITY_BREAKS if b <= overcapacity_limit + 1e-9]
    if not effective_breaks or effective_breaks[-1] < overcapacity_limit:
        effective_breaks.append(overcapacity_limit)
    widths = []
    prev = 0.0
    for bound in effective_breaks:
        widths.append(max(bound - prev, 0.0))
        prev = bound
    return widths


def _shared_penalty_base_cost(edge: dict, cargo_types: list[str]) -> float:
    """Return a representative edge cost used to scale shared-capacity surcharges."""
    costs = []
    for cargo_type in cargo_types:
        key = f"cost_per_ton_{cargo_type}"
        if key in edge:
            costs.append(float(edge[key]))
    return max(costs) if costs else 1.0


def _cargo_penalty_base_cost(edge: dict, cargo_type: str) -> float:
    """Return the edge cost used to scale cargo-specific surcharges."""
    return float(edge.get(f"cost_per_ton_{cargo_type}", 1.0))


def _build_od_cargo_groups(link_specs: list[dict], chunk_size: float) -> list[dict]:
    """Aggregate link specs into OD-cargo groups for routing."""
    groups_by_key = {}
    for spec in link_specs:
        key = (spec["origin"], spec["destination"], spec["cargo_type"])
        if key not in groups_by_key:
            groups_by_key[key] = {
                "origin": spec["origin"],
                "destination": spec["destination"],
                "cargo_type": spec["cargo_type"],
                "tons": 0.0,
                "n_chunks": 0,
                "members": [],
                "candidate_data": [],
                "route_plan_entries": [],
            }
        groups_by_key[key]["tons"] += spec["tons"]
        groups_by_key[key]["n_chunks"] += max(1, math.ceil(spec["tons"] / chunk_size)) if spec["tons"] > 0 else 1
        groups_by_key[key]["members"].append(spec)

    od_groups = list(groups_by_key.values())
    for group in od_groups:
        tons = group["tons"]
        n_chunks = max(1, group["n_chunks"])
        group["chunk_tons"] = tons / n_chunks if n_chunks > 0 else 0.0
        group["n_chunks"] = n_chunks
        group["chunks_assigned"] = 0

    return od_groups


def _generate_group_candidates(od_groups: list[dict],
                               transport_network: TransportNetwork,
                               candidate_count: int,
                               max_stretch: float,
                               max_overlap: float = 0.9):
    """Generate hub-based candidate routes for each OD group.

    Each candidate is forced through a different strategic hub (port, border
    crossing, mode transition), guaranteeing meaningful infrastructure-level
    diversity.  The *max_overlap* parameter is accepted for API compatibility
    but ignored — hub-based candidates are distinct by construction.
    """
    _ = max_overlap  # not needed for hub-based generation

    hub_index = _build_hub_index(transport_network)
    unreachable = []
    total_candidates = 0
    max_candidates_seen = 0

    for group in od_groups:
        candidates = _generate_hub_based_candidates(
            group, transport_network, hub_index,
            max_candidates=max(1, candidate_count),
            max_stretch=max_stretch,
        )
        if not candidates:
            unreachable.extend(group["members"])
            continue
        group["candidate_data"] = candidates
        total_candidates += len(candidates)
        max_candidates_seen = max(max_candidates_seen, len(candidates))

    if unreachable:
        _report_unreachable(unreachable, transport_network)

    avg_candidates = total_candidates / len(od_groups) if od_groups else 0.0
    logging.info(
        f"Capacity routing: generated {total_candidates} candidate routes "
        f"across {len(od_groups)} OD-cargo groups "
        f"(avg={avg_candidates:.2f}, max={max_candidates_seen})"
    )


# ------------------------------------------------------------------
# Hub index
# ------------------------------------------------------------------

def _build_hub_index(transport_network: TransportNetwork) -> dict[str, list[tuple[int, int]]]:
    """Build an index of hub edges grouped by substitutable type.

    Returns ``{hub_type: [(u, v), ...]}`` where *hub_type* encodes the
    kind of gateway (e.g. ``"multimodal:roads-maritime"``, ``"border"``).
    """
    hubs: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for u, v in transport_network.edges:
        edge = transport_network[u][v]
        ht = _classify_hub(edge)
        if ht is not None:
            hubs[ht].append((u, v))
    return dict(hubs)


def _classify_hub(edge: dict) -> str | None:
    """Classify an edge as a hub type, or *None* if not a strategic hub.

    Hub types group edges that are **substitutable** — using one port
    instead of another, one border crossing instead of another, etc.
    """
    etype = edge.get("type", "")
    special = edge.get("special")

    if etype == "multimodal":
        multimodes = edge.get("multimodes", "unknown")
        return f"multimodal:{multimodes}"

    if isinstance(special, str) and ("border" in special or "custom" in special):
        return "border"

    return None


# ------------------------------------------------------------------
# Hub-based candidate generation
# ------------------------------------------------------------------

def _generate_hub_based_candidates(
    group: dict,
    transport_network: TransportNetwork,
    hub_index: dict[str, list[tuple[int, int]]],
    max_candidates: int,
    max_stretch: float,
) -> list[tuple[Route, float]]:
    """Generate candidate routes that each use a different strategic hub.

    1. Compute baseline shortest path.
    2. Identify hub edges on the baseline and their hub types.
    3. For each hub type, enumerate alternative hub edges in the network.
    4. For each alternative, build a two-leg forced path (origin → hub entry,
       hub exit → destination) with the hub edge temporarily removed so the
       legs cannot reuse it.
    5. Keep candidates within *max_stretch* of baseline cost.
    """
    origin = group["origin"]
    destination = group["destination"]
    cargo_type = group["cargo_type"]
    weight = f"cost_per_ton_{cargo_type}"

    if origin == destination:
        return [(Route([origin], transport_network, cargo_type), 0.0)]

    subgraph = _cargo_subgraph(transport_network, weight)

    # --- Pre-compute single-source Dijkstra from origin and destination ---
    try:
        dist_o, path_o = nx.single_source_dijkstra(subgraph, origin, weight=weight)
    except nx.NetworkXError:
        return []
    if destination not in dist_o:
        return []
    try:
        dist_d, path_d = nx.single_source_dijkstra(subgraph, destination, weight=weight)
    except nx.NetworkXError:
        return []

    baseline_cost = dist_o[destination]
    baseline_path = path_o[destination]
    baseline_route = Route(baseline_path, transport_network, cargo_type)
    candidates: list[tuple[Route, float]] = [(baseline_route, baseline_cost)]

    # --- Identify hub types on the baseline ---
    baseline_hub_types: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for u, v in baseline_route.transport_edges:
        edge = transport_network[u][v]
        ht = _classify_hub(edge)
        if ht is not None:
            baseline_hub_types[ht].append((u, v))

    if not baseline_hub_types:
        # Short local route with no strategic hubs — baseline only
        return candidates

    # --- For each hub type, try alternative hubs ---
    baseline_hub_edges = set()
    for edges in baseline_hub_types.values():
        for u, v in edges:
            baseline_hub_edges.add(tuple(sorted((u, v))))

    cost_limit = baseline_cost * max_stretch
    tried_hubs: set[tuple[int, int]] = set(baseline_hub_edges)

    for hub_type in baseline_hub_types:
        for au, av in hub_index.get(hub_type, []):
            edge_key = tuple(sorted((au, av)))
            if edge_key in tried_hubs:
                continue
            tried_hubs.add(edge_key)

            # Skip if this hub doesn't carry the cargo type
            if weight not in transport_network[au][av]:
                continue

            candidate = _build_forced_hub_candidate(
                origin, destination, cargo_type, weight,
                au, av, transport_network, subgraph,
                dist_o, path_o, dist_d, path_d, cost_limit,
            )
            if candidate is not None:
                candidates.append(candidate)

    # --- Deduplicate (same node sequence) and sort by cost ---
    seen_nodes: set[tuple] = set()
    unique: list[tuple[Route, float]] = []
    for route, cost in sorted(candidates, key=lambda x: x[1]):
        key = tuple(route.transport_nodes)
        if key in seen_nodes:
            continue
        seen_nodes.add(key)
        unique.append((route, cost))

    return unique[:max_candidates]


def _build_forced_hub_candidate(
    origin: int,
    destination: int,
    cargo_type: str,
    weight: str,
    hub_u: int,
    hub_v: int,
    transport_network: TransportNetwork,
    subgraph: nx.Graph,
    dist_o: dict,
    path_o: dict,
    dist_d: dict,
    path_d: dict,
    cost_limit: float,
) -> tuple[Route, float] | None:
    """Build a candidate route forced through hub edge (hub_u, hub_v).

    Tries both orientations.  Uses pre-computed Dijkstra trees and only
    falls back to edge-removal when a leg reuses the hub edge.
    """
    hub_cost = transport_network[hub_u][hub_v].get(weight, math.inf)

    best: tuple[Route, float] | None = None

    for entry, exit_ in [(hub_u, hub_v), (hub_v, hub_u)]:
        if entry not in dist_o or exit_ not in dist_d:
            continue

        total_cost = dist_o[entry] + hub_cost + dist_d[exit_]
        if total_cost > cost_limit:
            continue
        if best is not None and total_cost >= best[1]:
            continue

        leg1 = path_o.get(entry)
        leg2_rev = path_d.get(exit_)
        if leg1 is None or leg2_rev is None:
            continue

        # Check if either leg reuses the hub edge (causes backtracking)
        hub_edge_set = {(hub_u, hub_v), (hub_v, hub_u)}
        leg1_reuses = any(
            (leg1[i], leg1[i + 1]) in hub_edge_set
            for i in range(len(leg1) - 1)
        )
        leg2_reuses = any(
            (leg2_rev[i], leg2_rev[i + 1]) in hub_edge_set
            for i in range(len(leg2_rev) - 1)
        )

        if leg1_reuses or leg2_reuses:
            # Fall back to edge-removal for this hub
            result = _forced_hub_with_edge_removal(
                origin, destination, cargo_type, weight,
                entry, exit_, transport_network, subgraph, cost_limit,
            )
            if result is not None:
                route, cost = result
                if best is None or cost < best[1]:
                    best = (route, cost)
            continue

        # Build path: leg1 ends at entry, leg2_rev reversed starts at exit_
        leg2 = leg2_rev[::-1]  # [destination, ..., exit_] → [exit_, ..., destination]
        full_path = leg1 + leg2  # [..., entry, exit_, ..., destination]
        try:
            route = Route(full_path, transport_network, cargo_type)
        except (KeyError, IndexError):
            continue
        best = (route, total_cost)

    return best


def _forced_hub_with_edge_removal(
    origin: int,
    destination: int,
    cargo_type: str,
    weight: str,
    entry: int,
    exit_: int,
    transport_network: TransportNetwork,
    subgraph: nx.Graph,
    cost_limit: float,
) -> tuple[Route, float] | None:
    """Compute a forced-hub route by temporarily removing the hub edge.

    This ensures the legs cannot reuse the hub edge, avoiding backtracking.
    """
    hub_u, hub_v = entry, exit_
    if not transport_network.has_edge(hub_u, hub_v):
        return None

    saved_attrs = dict(transport_network[hub_u][hub_v])
    hub_cost = saved_attrs.get(weight, math.inf)
    transport_network.remove_edge(hub_u, hub_v)

    try:
        try:
            leg1 = nx.shortest_path(subgraph, origin, entry, weight=weight)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
        try:
            leg2 = nx.shortest_path(subgraph, exit_, destination, weight=weight)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

        leg1_cost = sum(
            subgraph[leg1[i]][leg1[i + 1]][weight]
            for i in range(len(leg1) - 1)
        )
        leg2_cost = sum(
            subgraph[leg2[i]][leg2[i + 1]][weight]
            for i in range(len(leg2) - 1)
        )
        total_cost = leg1_cost + hub_cost + leg2_cost
        if total_cost > cost_limit:
            return None

        full_path = leg1 + leg2
        return (Route(full_path, transport_network, cargo_type), total_cost)
    except Exception:
        return None
    finally:
        transport_network.add_edge(hub_u, hub_v, **saved_attrs)


def _assign_group_chunk_round(od_groups: list[dict],
                              transport_network: TransportNetwork,
                              capacity_mode: str) -> int:
    """Assign one chunk per OD-cargo group using the cheapest live candidate."""
    assigned = 0
    cargo_types = transport_network.cargo_types or []

    for group in od_groups:
        if group["chunks_assigned"] >= group["n_chunks"]:
            continue

        route, _ = _select_best_group_candidate(group, transport_network)
        if route is None:
            continue

        chunk_tons = group["chunk_tons"]
        cargo_type = group["cargo_type"]

        if not route.transport_edges:
            remaining_chunks = group["n_chunks"] - group["chunks_assigned"]
            remaining_tons = chunk_tons * remaining_chunks
            if remaining_tons > 0:
                group["route_plan_entries"].append((route, remaining_tons))
            group["chunks_assigned"] = group["n_chunks"]
            assigned += remaining_chunks
            continue

        for u, v in route.transport_edges:
            edge = transport_network[u][v]
            load_key = f"current_load_{cargo_type}"
            edge[load_key] = edge.get(load_key, 0) + chunk_tons
            if cargo_types:
                _refresh_edge_capacity_costs(edge, cargo_types, capacity_mode)

        group["route_plan_entries"].append((route, chunk_tons))
        group["chunks_assigned"] += 1
        assigned += 1

    return assigned


def _assign_remaining_group_chunks(od_groups: list[dict],
                                   transport_network: TransportNetwork,
                                   capacity_mode: str):
    """Safety valve: place any leftover chunks on each group's primary candidate."""
    cargo_types = transport_network.cargo_types or []
    for group in od_groups:
        while group["chunks_assigned"] < group["n_chunks"]:
            if not group["candidate_data"]:
                group["chunks_assigned"] = group["n_chunks"]
                break

            route = group["candidate_data"][0][0]
            chunk_tons = group["chunk_tons"]
            cargo_type = group["cargo_type"]

            if not route.transport_edges:
                remaining_chunks = group["n_chunks"] - group["chunks_assigned"]
                remaining_tons = chunk_tons * remaining_chunks
                if remaining_tons > 0:
                    group["route_plan_entries"].append((route, remaining_tons))
                group["chunks_assigned"] = group["n_chunks"]
                break

            for u, v in route.transport_edges:
                edge = transport_network[u][v]
                load_key = f"current_load_{cargo_type}"
                edge[load_key] = edge.get(load_key, 0) + chunk_tons
                if cargo_types:
                    _refresh_edge_capacity_costs(edge, cargo_types, capacity_mode)

            group["route_plan_entries"].append((route, chunk_tons))
            group["chunks_assigned"] += 1


def _select_best_group_candidate(group: dict,
                                 transport_network: TransportNetwork) -> tuple[Route | None, float]:
    """Pick the currently cheapest candidate route for a group."""
    best_route = None
    best_base_cost = None
    best_cost = None
    cargo_type = group["cargo_type"]

    for route, base_cost in group.get("candidate_data", []):
        live_cost = transport_network.compute_route_cost(route, cargo_type, with_capacity=True)
        if best_cost is None or live_cost < best_cost or (
            live_cost == best_cost and (best_base_cost is None or base_cost < best_base_cost)
        ):
            best_route = route
            best_base_cost = base_cost
            best_cost = live_cost

    if best_route is None or best_cost is None:
        return None, math.inf
    return best_route, best_cost


def _build_group_route_plans(od_groups: list[dict], transport_network: TransportNetwork):
    """Convert per-group chunk assignments into route fractions."""
    for group in od_groups:
        entries = group["route_plan_entries"]
        cargo_type = group["cargo_type"]

        if not entries:
            if group["candidate_data"]:
                route, base_cost = group["candidate_data"][0]
                group["route_plan"] = [(route, 1.0)]
                group["primary_route"] = route
                group["weighted_cost_per_ton"] = base_cost
            else:
                group["route_plan"] = []
                group["primary_route"] = None
                group["weighted_cost_per_ton"] = 0.0
            continue

        merged = []
        for route, tons in entries:
            found = False
            for i, (existing_route, existing_tons) in enumerate(merged):
                if existing_route.transport_nodes == route.transport_nodes:
                    merged[i] = (existing_route, existing_tons + tons)
                    found = True
                    break
            if not found:
                merged.append((route, tons))

        total_tons = sum(tons for _, tons in merged)
        if total_tons > 0:
            route_plan = [(route, tons / total_tons) for route, tons in merged]
        else:
            route_plan = [(group["candidate_data"][0][0], 1.0)] if group["candidate_data"] else []

        route_plan.sort(key=lambda x: x[1], reverse=True)
        group["route_plan"] = route_plan
        group["primary_route"] = route_plan[0][0] if route_plan else None
        group["weighted_cost_per_ton"] = sum(
            frac * route.sum_indicator(transport_network, f"cost_per_ton_{cargo_type}")
            for route, frac in route_plan
        )


def _assign_group_routes_to_links(od_groups: list[dict],
                                  transport_network: TransportNetwork):
    """Project OD-cargo route shares back to the member commercial links."""
    for group in od_groups:
        route_plan = group.get("route_plan", [])
        primary_route = group.get("primary_route")
        weighted_cost = group.get("weighted_cost_per_ton", 0.0)

        for spec in group["members"]:
            link = spec["link"]
            if primary_route is None:
                link.route_plan = []
                spec["route"] = None
                continue

            link.store_route_information(primary_route, "main", weighted_cost)
            link.route_plan = list(route_plan)
            spec["route"] = primary_route


def _route_edge_keys(route: Route) -> set[tuple[int, int]]:
    """Return undirected edge keys for overlap comparisons."""
    return {tuple(sorted((u, v))) for u, v in route.transport_edges}


def _strategic_edge_key(edge: dict) -> str | None:
    """Return a compact key for strategic gateway-like edges."""
    edge_type = edge.get("type", "")
    name = edge.get("name")
    special = edge.get("special")

    if edge_type == "multimodal":
        return f"multimodal:{name or edge.get('multimodes') or edge.get('id')}"
    if edge_type in ("maritime", "pipelines", "airways"):
        return f"{edge_type}:{name or special or edge.get('id')}"
    if isinstance(special, str) and ("border" in special or "custom" in special):
        return f"{edge_type}:{name or special or edge.get('id')}"
    if isinstance(name, str) and any(token in name for token in ("port", "border", "crossing")):
        return f"{edge_type}:{name}"
    return None


# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def _export_trade_capacity_diagnostic(link_specs: list[dict],
                                      transport_network: TransportNetwork,
                                      export_folder: Path | None,
                                      modeled_regions: list[str]):
    """Build and optionally export the region x cargo trade-capacity table."""
    df = _build_trade_capacity_diagnostic(link_specs, transport_network, modeled_regions)
    if df.empty:
        return
    n_tight = int((df["trade_to_capacity_ratio"] > 1.0).sum())
    logging.info(
        f"Trade-capacity diagnostic: {len(df)} region-cargo rows, "
        f"{n_tight} above gateway capacity"
    )
    if n_tight:
        tight_rows = df[df["trade_to_capacity_ratio"] > 1.0].sort_values(
            "trade_to_capacity_ratio", ascending=False,
        )
        for _, row in tight_rows.head(6).iterrows():
            logging.warning(
                "  %s / %s: trade=%s t, gateway_capacity=%s t, ratio=%.2f",
                row["region"], row["cargo_type"],
                f"{row['trade_tons']:,.0f}",
                f"{row['total_gateway_capacity']:,.0f}",
                row["trade_to_capacity_ratio"],
            )
    _export_dataframe(df, export_folder, "gateway_capacity_by_region_cargo.csv")


def _build_trade_capacity_diagnostic(link_specs: list[dict],
                                     transport_network: TransportNetwork,
                                     modeled_regions: list[str]) -> pd.DataFrame:
    """Compare cross-region trade demand to border capacity by region and cargo."""
    cargo_types = transport_network.cargo_types or sorted({
        spec["cargo_type"] for spec in link_specs if spec.get("cargo_type")
    })
    trade = defaultdict(lambda: {"imports_tons": 0.0, "exports_tons": 0.0})
    modeled_regions = sorted(set(modeled_regions))

    for spec in link_specs:
        tons = float(spec.get("tons", 0.0))
        supplier_region = spec.get("supplier_region")
        buyer_region = spec.get("buyer_region")
        cargo_type = spec.get("cargo_type")
        if tons <= 0 or not cargo_type:
            continue
        if supplier_region and buyer_region and supplier_region != buyer_region:
            if supplier_region in modeled_regions:
                trade[(supplier_region, cargo_type)]["exports_tons"] += tons
            if buyer_region in modeled_regions:
                trade[(buyer_region, cargo_type)]["imports_tons"] += tons

    rows = []
    for region in modeled_regions:
        for cargo_type in cargo_types:
            imports_tons = trade[(region, cargo_type)]["imports_tons"]
            exports_tons = trade[(region, cargo_type)]["exports_tons"]
            border_capacity = 0.0
            considered_edge_names = []
            for u, v in transport_network.edges:
                edge = transport_network[u][v]
                if edge.get("special") != "border":
                    continue
                if not _edge_region_matches(edge.get("region"), region):
                    continue
                cap = float(_get_cargo_capacity(edge, cargo_type))
                if cap <= 0 or cap >= CAPACITY_INF:
                    continue
                border_capacity += cap
                edge_name = edge.get("name")
                considered_edge_names.append(edge_name if isinstance(edge_name, str) and edge_name else "noname")

            total_capacity = border_capacity
            trade_total = imports_tons + exports_tons
            ratio = trade_total / total_capacity if total_capacity > 0 else math.inf
            rows.append({
                "region": region,
                "cargo_type": cargo_type,
                "imports_tons": imports_tons,
                "exports_tons": exports_tons,
                "trade_tons": trade_total,
                "border_capacity": border_capacity,
                "total_gateway_capacity": total_capacity,
                "trade_to_capacity_ratio": ratio,
                "considered_edge_names": "|".join(considered_edge_names),
            })

    return pd.DataFrame(rows)


def _export_lp_diagnostics(od_groups: list[dict],
                           transport_network: TransportNetwork,
                           export_folder: Path | None,
                           overcapacity_limit: float):
    """Export post-LP edge and route diagnostics when an output folder exists."""
    edge_rows = []
    cargo_types = transport_network.cargo_types or []
    for u, v in transport_network.edges:
        edge = transport_network[u][v]
        row = {
            "edge_id": edge.get("id"),
            "name": edge.get("name", ""),
            "type": edge.get("type", ""),
            "special": edge.get("special"),
            "region": edge.get("region"),
        }
        max_util = 0.0
        shared_capacity = float(edge.get("capacity", 1e9))
        shared_load = sum(edge.get(f"current_load_{ct}", 0.0) for ct in cargo_types)
        row["shared_capacity"] = None if shared_capacity >= CAPACITY_INF else shared_capacity
        row["shared_load"] = shared_load
        row["shared_utilization_pct"] = (
            shared_load / shared_capacity * 100 if 0 < shared_capacity < CAPACITY_INF else None
        )
        for cargo_type in cargo_types:
            load = float(edge.get(f"current_load_{cargo_type}", 0.0))
            cap = float(_get_cargo_capacity(edge, cargo_type))
            util = load / cap * 100 if 0 < cap < CAPACITY_INF else None
            row[f"load_{cargo_type}"] = load
            row[f"capacity_{cargo_type}"] = None if cap >= CAPACITY_INF else cap
            row[f"utilization_{cargo_type}_pct"] = util
            if util is not None:
                max_util = max(max_util, util)
        row["max_utilization_pct"] = max_util
        row["within_lp_limit"] = max_util <= overcapacity_limit * 100 + 1e-6
        edge_rows.append(row)

    route_rows = []
    for group in od_groups:
        for idx, (route, share) in enumerate(group.get("route_plan", []), start=1):
            route_rows.append({
                "origin": group["origin"],
                "destination": group["destination"],
                "cargo_type": group["cargo_type"],
                "group_tons": group["tons"],
                "route_rank": idx,
                "share": share,
                "route_cost_per_ton": route.sum_indicator(
                    transport_network, f"cost_per_ton_{group['cargo_type']}",
                ),
                "edge_ids": ",".join(str(edge_id) for edge_id in route.transport_edge_ids),
                "modes": ",".join(sorted(route.transport_modes)),
            })

    _export_dataframe(pd.DataFrame(edge_rows), export_folder, "routing_lp_edge_utilization.csv")
    _export_dataframe(pd.DataFrame(route_rows), export_folder, "routing_lp_group_routes.csv")


def _export_lp_candidate_diagnostics(od_groups: list[dict],
                                     transport_network: TransportNetwork,
                                     export_folder: Path | None):
    """Export candidate-route coverage before solving the LP."""
    group_rows = []
    path_rows = []
    for group in od_groups:
        candidates = group.get("candidate_data", [])
        group_rows.append({
            "origin": group["origin"],
            "destination": group["destination"],
            "cargo_type": group["cargo_type"],
            "tons": group["tons"],
            "n_members": len(group["members"]),
            "n_candidates": len(candidates),
        })
        for idx, (route, base_cost) in enumerate(candidates, start=1):
            path_rows.append({
                "origin": group["origin"],
                "destination": group["destination"],
                "cargo_type": group["cargo_type"],
                "route_rank": idx,
                "base_cost_per_ton": base_cost,
                "modes": ",".join(sorted(route.transport_modes)),
                "edge_ids": ",".join(str(edge_id) for edge_id in route.transport_edge_ids),
            })

    _export_dataframe(pd.DataFrame(group_rows), export_folder, "routing_lp_group_candidates.csv")
    _export_dataframe(pd.DataFrame(path_rows), export_folder, "routing_lp_candidate_paths.csv")


def _edge_region_matches(edge_region, region: str) -> bool:
    """Return True when an edge region label contains the requested region code."""
    if edge_region is None or pd.isna(edge_region):
        return False
    region_str = str(edge_region)
    parts = [part.strip() for part in region_str.split("_") if part]
    return region == region_str or region in parts


def _export_dataframe(df: pd.DataFrame,
                      export_folder: Path | None,
                      filename: str):
    """Write *df* to CSV when an export folder is available."""
    if export_folder is None or df.empty:
        return
    export_folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(export_folder / filename, index=False)


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

        if path is None or len(path) < 1:
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

    # Log individual unreachable links with both origin and destination coordinates
    logging.error("Unreachable links (origin → destination):")
    for spec in unreachable[:20]:
        o, d = spec["origin"], spec["destination"]
        o_data = transport_network._node.get(o, {})
        d_data = transport_network._node.get(d, {})
        link = spec["link"]
        logging.error(
            f"  {link.supplier_id} → {link.buyer_id}: "
            f"node {o} ({o_data.get('lat', '?'):.4f}, {o_data.get('long', '?'):.4f}) → "
            f"node {d} ({d_data.get('lat', '?'):.4f}, {d_data.get('long', '?'):.4f})"
        )
    if len(unreachable) > 20:
        logging.error(f"  ... and {len(unreachable) - 20} more")

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
        _refresh_edge_capacity_costs(edge, cargo_types, mode)


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
