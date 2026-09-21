"""Assign initial logistics routes to every commercial link in the SC network.

One route per link, the cheapest path on the base cost labels (batched scipy
Dijkstra per cargo type). Capacities play no part in the initial assignment:
a capacity below the baseline load of an edge is a calibration question that
``_check_baseline_capacities`` reports, not something an assignment algorithm
should hide, and the within-step capacity gate (run_pipeline/capacity_gate.py)
rations and reroutes from the first step on. The capacity-aware assignments of
the Gulf work (chunked hub heuristic, candidate-path LP, edge LP: KI-27, they
did not scale past ~50k links) were retired on 21 Sep 2026 and live on the
``legacy/v2-capacity-routing`` branch; docs/architecture/transport-capacity.md
has the review and the design.
"""

from __future__ import annotations

from collections import defaultdict
import logging
import math
from pathlib import Path

import networkx as nx
import pandas as pd

from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork, _get_cargo_capacity
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
    export_folder: Path | None = None,
) -> pd.DataFrame:
    """Assign routes to every commercial link and return a summary table.

    Uses pre-computed single-source Dijkstra for efficiency. With
    ``capacity_constraint`` on, the baseline load of every capacitated edge is
    compared with its capacity and the binding edges are reported (the gate
    then rations them from t = 0).
    """
    _ = (firms, countries)  # kept in the signature for the drivers (studies, run.py)
    # 1. Collect all routable links with their metadata
    link_specs = _collect_link_specs(sc_network, tp)
    if not link_specs:
        logging.info("No routable links found")
        return _build_commercial_link_table(sc_network)

    # 2. Pre-compute routes and assign
    _precompute_and_assign(link_specs, transport_network)

    # 3. Baseline loads against capacities (diagnostic only; nothing is reassigned)
    if tp.capacity_constraint_enabled:
        _check_baseline_capacities(link_specs, transport_network, export_folder)

    # 4. Build summary table
    cl_table = _build_commercial_link_table(sc_network)

    # 4b. Share Route objects between links with the same node sequence (KI-30)
    before, after = intern_routes(sc_network, transport_network)
    logging.info(f"Route objects shared across links: {before:,} -> {after:,} distinct routes")

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
# Pre-computation
# ------------------------------------------------------------------

def _precompute_and_assign(link_specs: list[dict],
                           transport_network: TransportNetwork):
    """Pre-compute shortest paths and assign routes to links."""

    # Group links by cargo_type to batch Dijkstra runs
    cargo_types = _get_cargo_types(link_specs)

    # Pre-compute paths for each cargo type. Only the destinations that a
    # source actually ships to are kept: single_source_dijkstra_path returns a
    # path to EVERY reachable node (6.8k on the EU scope), and keeping them all
    # for ~1.2k sources per cargo type (~8M path lists) exhausted memory on a
    # 32 GB machine; the links need ~200k (cargo, source, dest) keys in total.
    needed_dests: dict[tuple, set] = {}
    for s in link_specs:
        needed_dests.setdefault((s["cargo_type"], s["origin"]), set()).add(s["destination"])

    path_lookup = {}  # (cargo_type, source, dest) -> node_list
    for cargo_type in cargo_types:
        weight = f"cost_per_ton_{cargo_type}"
        # Subgraph with only edges that carry this cargo type
        subgraph = _cargo_subgraph(transport_network, weight)
        dest_by_source = {src: dests for (ct, src), dests in needed_dests.items()
                          if ct == cargo_type}

        logging.info(f"Pre-computing routes: cargo={cargo_type}, "
                     f"{len(dest_by_source)} sources, {subgraph.number_of_edges()} edges")

        for (source, dest), path in shortest_paths_for(subgraph, weight, dest_by_source).items():
            path_lookup[(cargo_type, source, dest)] = path

    # Assign routes to links (one route per link)
    _assign_routes_from_lookup(link_specs, path_lookup, transport_network)

    # Populate the route cache for simulation-time use
    _populate_route_cache(link_specs, transport_network)


def shortest_paths_for(subgraph, weight: str, dest_by_source: dict,
                       chunk: int = 256) -> dict:
    """Shortest paths (node lists) from every source to its needed
    destinations, as ``{(source, dest): [nodes]}``; unreachable pairs are
    absent.

    Runs scipy's C Dijkstra on a CSR view of *subgraph* (all sources of a
    chunk at once) and reconstructs paths from the predecessor matrix. On the
    EU scope this replaces ~7.7 min of per-source networkx Dijkstra by well
    under a minute; costs are identical, and only exact cost ties (rare with
    float labels) can pick a different equal-cost path. Falls back to
    networkx when scipy is unavailable.
    """
    if not dest_by_source:
        return {}
    try:
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import dijkstra as _sp_dijkstra
    except ImportError:  # pragma: no cover - scipy is a hard dependency elsewhere
        out = {}
        for source, dests in dest_by_source.items():
            try:
                paths = nx.single_source_dijkstra_path(subgraph, source, weight=weight)
            except nx.NetworkXError:
                paths = {}
            for dest in dests:
                if dest in paths:
                    out[(source, dest)] = paths[dest]
        return out

    nodes = list(subgraph.nodes)
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    rows, cols, vals = [], [], []
    for u, v, d in subgraph.edges(data=True):
        w = max(float(d[weight]), 1e-9)   # explicit zeros are not edges for csgraph
        rows.append(idx[u]); cols.append(idx[v]); vals.append(w)
        rows.append(idx[v]); cols.append(idx[u]); vals.append(w)
    mat = csr_matrix((vals, (rows, cols)), shape=(n, n))

    out = {}
    sources = [s for s in dest_by_source if s in idx]
    for start in range(0, len(sources), chunk):
        batch = sources[start:start + chunk]
        _, pred = _sp_dijkstra(mat, directed=False, indices=[idx[s] for s in batch],
                               return_predecessors=True)
        for row, source in enumerate(batch):
            si = idx[source]
            for dest in dest_by_source[source]:
                di = idx.get(dest)
                if di is None:
                    continue
                if di == si:
                    out[(source, dest)] = [source]
                    continue
                if pred[row, di] < 0:
                    continue  # unreachable
                path, cur = [di], di
                while cur != si:
                    cur = pred[row, cur]
                    path.append(cur)
                path.reverse()
                out[(source, dest)] = [nodes[i] for i in path]
    return out


# ------------------------------------------------------------------
# Baseline capacity check
# ------------------------------------------------------------------

def _accumulate_loads(link_specs: list[dict]) -> dict[tuple, dict[str, float]]:
    """Baseline tons per undirected edge key and cargo type from the assigned routes."""
    loads: dict[tuple, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for spec in link_specs:
        route = spec.get("route") or spec["link"].route
        if route is None or spec["tons"] <= 0:
            continue
        for u, v in route.transport_edges:
            loads[(min(u, v), max(u, v))][spec["cargo_type"]] += spec["tons"]
    return loads


def _check_baseline_capacities(link_specs: list[dict],
                               transport_network: TransportNetwork,
                               export_folder: Path | None) -> pd.DataFrame:
    """Compare the baseline load of every capacitated edge with its capacity.

    Baseline capacities are not meant to bind (the gate rations from t = 0 if
    they do); every binding edge is logged with its ratio and the whole table
    is exported as ``baseline_capacity_check.csv`` when an export folder exists.
    """
    loads = _accumulate_loads(link_specs)
    cargo_types = transport_network.cargo_types or []
    rows = []
    for u, v in transport_network.capacitated_edges():
        edge = transport_network[u][v]
        by_cargo = loads.get((min(u, v), max(u, v)), {})
        constraints = [(ct, edge[f"capacity_{ct}"], by_cargo.get(ct, 0.0))
                       for ct in cargo_types if f"capacity_{ct}" in edge]
        if "capacity" in edge:
            constraints.append(("all", edge["capacity"], math.fsum(by_cargo.values())))
        for cargo, cap, tons in constraints:
            ratio = tons / cap if cap > 0 else (math.inf if tons > 0 else 0.0)
            rows.append({"edge_id": edge.get("id"), "name": edge.get("name", ""),
                         "type": edge.get("type", ""), "cargo_type": cargo,
                         "baseline_tons": tons, "capacity": cap, "ratio": ratio})
    df = pd.DataFrame(rows)
    if df.empty:
        logging.info("Baseline capacity check: no capacitated edge")
        return df
    binding = df[df["ratio"] > 1.0].sort_values("ratio", ascending=False)
    logging.info(f"Baseline capacity check: {len(df)} edge-cargo constraints, "
                 f"{len(binding)} above capacity in the baseline")
    for _, row in binding.iterrows():
        logging.warning(
            "  baseline load above capacity: %s (%s) / %s: %s t vs %s t per step (x%.2f) "
            "- the gate rations this edge from t=0",
            row["name"] or row["edge_id"], row["type"], row["cargo_type"],
            f"{row['baseline_tons']:,.0f}", f"{row['capacity']:,.0f}", row["ratio"],
        )
    _export_dataframe(df, export_folder, "baseline_capacity_check.csv")
    return df


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

    Edges where a cargo type is not eligible (cargo_mode_eligibility, or an
    explicit capacity 0) have no cost label for that cargo type, so they are
    automatically excluded from routing. This is a lightweight view — no data
    is copied.
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
        spec["route"] = route  # store for the baseline capacity check
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


def intern_routes(sc_network, transport_network: TransportNetwork) -> tuple[int, int]:
    """Make links with the same (cargo type, node sequence) share one Route object.

    Route assignment builds one Route per link, so the many links between
    the same two transport nodes (firms at the same node, several products)
    each carried their own copy: 786k Route objects for 143k distinct routes
    on the EU scope, ~5 GB (KI-30). Routes are never mutated after
    construction (``revert`` has no caller), so sharing is safe. The route
    library is interned with the same table, so links and library share too.

    Returns (route objects before, distinct routes after).
    """
    canon: dict[tuple, Route] = {}

    def _c(route):
        if route is None:
            return None
        # A Route holds nodes, edge ids, modes and length only — nothing
        # cargo-specific (costs live on the link) — so the node sequence is
        # the identity.
        return canon.setdefault(tuple(route.transport_nodes), route)

    seen_before: set[int] = set()
    for _, _, data in sc_network.edges(data=True):
        link = data.get("object")
        if link is None or getattr(link, "route", None) is None:
            continue
        seen_before.add(id(link.route))
        link.route = _c(link.route)
        if getattr(link, "alternative_route", None) is not None:
            seen_before.add(id(link.alternative_route))
            link.alternative_route = _c(link.alternative_route)
    for per_cargo in getattr(transport_network, "shortest_path_library", {}).values():
        for routes in per_cargo.values():
            for key, route in routes.items():
                seen_before.add(id(route))
                routes[key] = _c(route)
    return len(seen_before), len(canon)


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
            "transport_modes": (sorted(link.route.transport_modes) if link.use_transport_network and link.route else None),   # deterministic listing (KI-34)
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "pid"
    return df
