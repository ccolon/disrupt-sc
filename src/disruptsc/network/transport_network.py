"""TransportNetwork — nx.Graph wrapper for multimodal transport infrastructure."""

from __future__ import annotations

import logging
import math
from collections import defaultdict
from typing import TYPE_CHECKING

import networkx as nx
import numpy as np
import pandas as pd

from disruptsc.network.route import Route

if TYPE_CHECKING:
    from disruptsc.network.commercial_link import CommercialLink



def degrees_to_km(lon1, lat1, lon2, lat2) -> float:
    """Haversine-approximation distance in km."""
    lat_km = 111 * abs(lat2 - lat1)
    lon_km = 111 * abs(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return math.sqrt(lat_km ** 2 + lon_km ** 2)


class TransportNetwork(nx.Graph):

    def __init__(self, graph=None, **attr):
        super().__init__(graph, **attr)
        self.cargo_types: list[str] | None = None
        self.min_cost_per_tonkm: float | None = None
        self.shortest_path_library: dict = {"normal": {}, "alternative": {}}
        self._distance_cache: dict[tuple, float] = {}
        # Per-step statistics of the capacity gate (run_pipeline/capacity_gate.py),
        # keyed by edge id: offered / accepted / withheld tons; read by
        # compute_logistics_report while the step's shipments are on the edges.
        self.capacity_gate_stats: dict = {}

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    def info(self) -> str:
        modes = self.get_transport_modes()
        return (f"Transport network with {len(modes)} modes: {modes}\n"
                f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}")

    def get_transport_modes(self) -> list[str]:
        return list(set(nx.get_edge_attributes(self, "type").values()))

    def log_km_per_transport_modes(self):
        km_per_mode = pd.DataFrame({
            "km": nx.get_edge_attributes(self, "km"),
            "type": nx.get_edge_attributes(self, "type"),
        }).groupby("type")["km"].sum().to_dict()
        logging.info(
            f"Total network length: {sum(km_per_mode.values()):.0f} km. "
            + ", ".join(f"{m}: {k:.0f} km" for m, k in km_per_mode.items())
        )

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def add_transport_node(self, node_id, all_nodes_data):
        cols = ["id", "geometry"]
        for optional in ("special", "name"):
            if optional in all_nodes_data.columns:
                cols.append(optional)
        node_data = all_nodes_data.loc[node_id, cols].to_dict()
        node_data["long"] = all_nodes_data.loc[node_id, "geometry"].x
        node_data["lat"] = all_nodes_data.loc[node_id, "geometry"].y
        node_data["shipments"] = {}
        node_data["disruption_duration"] = 0
        node_data["firms_there"] = []
        node_data["households_there"] = None
        node_data["type"] = "road"
        self.add_node(node_id, **node_data)

    def locate_firms_on_nodes(self, firms):
        for node_id in self.nodes:
            self._node[node_id]["firms_there"] = []
        for firm in firms.values():
            self._node[firm.od_point]["firms_there"].append(firm.pid)

    def locate_households_on_nodes(self, households):
        for pid, hh in households.items():
            self._node[hh.od_point]["households_there"] = pid

    # ------------------------------------------------------------------
    # Distance
    # ------------------------------------------------------------------

    def get_distance_between_nodes(self, node_id1: int, node_id2: int) -> float:
        if node_id1 == node_id2:
            return 0.0
        key = (min(node_id1, node_id2), max(node_id1, node_id2))
        if key not in self._distance_cache:
            n1, n2 = self._node[node_id1], self._node[node_id2]
            self._distance_cache[key] = degrees_to_km(n1["long"], n1["lat"], n2["long"], n2["lat"])
        return self._distance_cache[key]

    # ------------------------------------------------------------------
    # Logistic cost setup
    # ------------------------------------------------------------------

    def ingest_logistic_data(self, logistic_parameters: dict, use_cargo_types: bool = True,
                             cargo_mode_eligibility: dict | None = None):
        """Write the ``cost_per_ton_<cargo>`` label of every edge for every cargo type.

        *cargo_mode_eligibility* ({mode: [cargo types]}) says which cargo may use
        which mode; a cargo that may not use the edge's mode gets no label there
        (invisible to Dijkstra), as does a cargo whose capacity on the edge is an
        explicit 0 (transport_capacity_overrides).
        """
        # Derive cargo types from sector_to_cargo_type mapping, or fall
        # back to a single "any" bucket when the feature is disabled.
        if use_cargo_types:
            cargo_type_values = list(logistic_parameters.get("sector_to_cargo_type", {}).values())
            self.cargo_types = sorted(set(ct for ct in cargo_type_values if ct != "default"))
            if not self.cargo_types:
                self.cargo_types = ["container", "dry_bulk", "liquid_bulk"]
        else:
            self.cargo_types = ["any"]
        self.shortest_path_library = {
            "normal": {m: {} for m in self.cargo_types},
            "alternative": {m: {} for m in self.cargo_types},
        }
        eligibility = cargo_mode_eligibility if use_cargo_types else None
        for _, attr in self.edges.items():
            _calculate_cost_per_ton(attr, logistic_parameters, self.cargo_types, eligibility)
        self.capture_base_capacity_state()

    def shrink_cargo_types_to(self, used: set[str]) -> None:
        """Prune cargo_types to only those listed in *used*.

        Removes per-cargo-type labels (cost_per_ton_, capacity_,
        base_capacity_) for the dropped types, and resets
        shortest_path_library. Safe to call after ingest_logistic_data —
        useful when the actual supply chain uses fewer cargo types than the
        network was set up for, so Dijkstra runs N× fewer times.
        """
        if not self.cargo_types:
            return
        used = {ct for ct in used if ct in self.cargo_types}
        if not used:
            logging.warning("shrink_cargo_types_to: no overlap with current cargo_types; keeping all")
            return
        dropped = set(self.cargo_types) - used
        if not dropped:
            return
        kept = sorted(used)
        logging.info(
            f"Pruning unused cargo types {sorted(dropped)} "
            f"({len(self.cargo_types)} → {len(kept)}); routing will run "
            f"{len(kept)}× instead of {len(self.cargo_types)}×"
        )
        # Strip per-cargo-type labels from every edge
        prefixes = ("cost_per_ton_", "capacity_", "base_capacity_")
        for _, attr in self.edges.items():
            for ct in dropped:
                for prefix in prefixes:
                    attr.pop(f"{prefix}{ct}", None)
        # Reset routing state for the new cargo type set
        self.cargo_types = kept
        self.shortest_path_library = {
            "normal": {m: {} for m in kept},
            "alternative": {m: {} for m in kept},
        }

    # An edge carries a ``capacity`` key (tons per step, all cargo together) and /
    # or ``capacity_<cargo>`` keys ONLY when transport_capacity_overrides names it;
    # every other edge has no capacity key at all and is never gated. The
    # ``base_*`` twins hold the undisrupted values that transport disruptions
    # scale (apply_edge_capacity_factor) and restore.

    def _capacity_keys(self, edge: dict) -> list[str]:
        keys = ["capacity"] if "capacity" in edge else []
        keys += [f"capacity_{ct}" for ct in (self.cargo_types or []) if f"capacity_{ct}" in edge]
        return keys

    def capacitated_edges(self) -> list[tuple[int, int]]:
        """Edges with a capacity (shared or per cargo), in a deterministic order."""
        out = []
        for u, v, edge in self.edges(data=True):
            if "capacity" in edge or any(f"capacity_{ct}" in edge for ct in (self.cargo_types or [])):
                out.append((edge.get("id", 0), u, v))
        out.sort()
        return [(u, v) for _, u, v in out]

    def capture_base_capacity_state(self):
        """Snapshot the edge capacities that represent the undisrupted network."""
        for u, v in self.edges:
            edge = self[u][v]
            for key in self._capacity_keys(edge):
                edge[f"base_{key}"] = float(edge[key])

    def ensure_base_capacity_state(self, edge: dict):
        """Backfill a missing base-capacity twin (an override applied after ingest)."""
        for key in self._capacity_keys(edge):
            if edge.get(f"base_{key}") is None:
                edge[f"base_{key}"] = float(edge[key])

    def restore_edge_capacity(self, edge: dict):
        """Restore dynamic capacities from the saved undisrupted state."""
        self.ensure_base_capacity_state(edge)
        for key in self._capacity_keys(edge):
            edge[key] = float(edge[f"base_{key}"])
        edge["closed"] = False

    def apply_edge_capacity_factor(self, edge: dict, factor: float):
        """Scale the edge's dynamic capacities by *factor* relative to base state.

        An edge without a capacity key is closed (factor 0) or open; a partial
        factor on it has nothing to scale and is a no-op apart from the
        ``closed`` flag, which only a full reduction sets."""
        self.ensure_base_capacity_state(edge)
        factor = max(0.0, min(1.0, float(factor)))
        for key in self._capacity_keys(edge):
            edge[key] = float(edge[f"base_{key}"]) * factor
        edge["closed"] = factor <= 1e-12

    def start_edge_disruption(self, edge: dict, reduction: float, duration: float,
                              recovery_shape: str = "threshold",
                              recovery_rate: float = 1.0):
        """Attach disruption metadata and update dynamic capacities immediately."""
        edge["disruption_duration"] = duration
        edge["disruption_total_duration"] = duration
        edge["disruption_elapsed"] = 0
        edge["disruption_initial_reduction"] = max(0.0, min(1.0, float(reduction)))
        edge["disruption_recovery_shape"] = recovery_shape
        edge["disruption_recovery_rate"] = float(recovery_rate)
        self._refresh_edge_disruption_state(edge)

    def clear_edge_disruption(self, edge: dict):
        """Remove disruption metadata and restore the edge to its base capacity."""
        self.restore_edge_capacity(edge)
        edge["closure_substitution_share"] = 1.0
        edge["disruption_duration"] = 0
        edge["disruption_total_duration"] = 0
        edge["disruption_elapsed"] = 0
        edge["disruption_initial_reduction"] = 0.0
        edge["disruption_recovery_shape"] = "threshold"
        edge["disruption_recovery_rate"] = 1.0

    # ------------------------------------------------------------------
    # Cost shocks (the edge stays open, its cost labels are multiplied)
    # ------------------------------------------------------------------
    # A low-water river, a congested corridor or a toll: capacity is not
    # zero, but every ton costs more. Buyers whose route crosses a shocked
    # edge pay the surcharge, reroute if an alternative is cheaper, or give
    # up beyond price_increase_threshold (see agents/transport_utils.py) —
    # without the capacity-routing heuristic, which does not scale to
    # continental scopes (EU: 197k OD groups, killed after 81 CPU-min).

    def invalidate_alternative_routes(self):
        """Forget cached alternative routes - every 'alternative*' library, including the
        same-mode searches of the penalty-aware discovery: their costs no longer hold."""
        keys = [k for k in self.shortest_path_library if str(k).startswith("alternative")] or ["alternative"]
        for key in keys:
            self.shortest_path_library[key] = {
                ct: {} for ct in self.shortest_path_library.get(key, {})
            } or {ct: {} for ct in (self.cargo_types or [])}

    def start_edge_cost_shock(self, edge: dict, multiplier, duration: float,
                              capacity_factor: float = 1.0, substitution_share: float = 1.0):
        """Multiply the edge's cost labels for *duration* steps.

        *multiplier* is a number or a per-cargo dict ({cargo_type: m,
        "default": m}). Base labels are captured the first time an edge is
        shocked so that repeated or overlapping shocks never compound.
        *capacity_factor* (share of each link's tonnage the shocked mode still
        carries) and *substitution_share* (share of the displaced remainder the
        substitutes absorb) define the substitution ceiling; 1.0/1.0 = legacy.
        """
        edge["cost_shock_capacity_factor"] = float(capacity_factor)
        edge["cost_shock_substitution_share"] = float(substitution_share)
        for ct in (self.cargo_types or []):
            key = f"cost_per_ton_{ct}"
            if key not in edge:
                continue  # blocked cargo type on this edge
            base_key = f"base_{key}"
            if base_key not in edge:
                edge[base_key] = float(edge[key])
            m = multiplier.get(ct, multiplier.get("default", 1.0)) if isinstance(multiplier, dict) else multiplier
            edge[key] = float(edge[base_key]) * float(m)
        edge["cost_shock_multiplier"] = multiplier
        edge["cost_shock_duration"] = duration
        self.invalidate_alternative_routes()

    def clear_edge_cost_shock(self, edge: dict):
        """Restore the edge's base cost labels."""
        for ct in (self.cargo_types or []):
            key = f"cost_per_ton_{ct}"
            base_key = f"base_{key}"
            if base_key in edge:
                edge[key] = float(edge[base_key])
        edge["cost_shock_multiplier"] = 1.0
        edge["cost_shock_duration"] = 0
        edge["cost_shock_capacity_factor"] = 1.0
        edge["cost_shock_substitution_share"] = 1.0

    def _refresh_edge_disruption_state(self, edge: dict):
        """Recompute dynamic capacities from the edge's stored disruption metadata."""
        reduction = float(edge.get("disruption_initial_reduction", 0.0))
        recovered_fraction = _recovery_factor(
            edge.get("disruption_elapsed", 0),
            edge.get("disruption_total_duration", 0),
            edge.get("disruption_recovery_shape", "threshold"),
            edge.get("disruption_recovery_rate", 1.0),
        )
        active_factor = 1.0 - reduction * (1.0 - recovered_fraction)
        self.apply_edge_capacity_factor(edge, active_factor)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def provide_shortest_route(self, origin: int, destination: int,
                               cargo_type: str, route_weight: str,
                               allowed_modes=None, mode_weights: dict | None = None,
                               excluded_edges=None) -> Route | None:
        """Cheapest route for *cargo_type* under *route_weight*; *allowed_modes* (an iterable
        of edge types) restricts the search to those modes and *mode_weights* ({type: factor})
        scales the cost of the edges of a mode in the search only - used by the penalty-aware
        alternative discovery to look for a detour on the shipper's line-haul mode, with its
        access modes made as dear as the modal-switch penalty. *excluded_edges* (a set of
        ``(min(u, v), max(u, v))`` keys) removes edges from the search: the capacity gate
        passes the edges saturated earlier in the step."""
        if origin not in self.nodes:
            logging.debug(f"Origin {origin} not in available network")
            return None
        if destination not in self.nodes:
            logging.debug(f"Destination {destination} not in available network")
            return None
        weight = route_weight + "_" + cargo_type
        modes = set(allowed_modes) if allowed_modes else None
        excluded = excluded_edges or None

        # Use a subgraph view that only includes edges carrying this weight.
        # Edges without the label (blocked cargo type) would otherwise get
        # NetworkX's default weight of 1, making them appear cheapest.
        def edge_ok(u, v):
            e = self[u][v]
            if weight not in e or (modes is not None and e.get("type") not in modes):
                return False
            return excluded is None or (u, v) not in excluded and (v, u) not in excluded

        subgraph = nx.subgraph_view(self, filter_edge=edge_ok)
        if mode_weights:
            factors = dict(mode_weights)

            def search_weight(u, v, d, _w=weight, _f=factors):
                return d[_w] * _f.get(d.get("type"), 1.0)
        else:
            search_weight = weight
        try:
            sp = nx.shortest_path(subgraph, origin, destination, weight=search_weight)
            return Route(sp, self, cargo_type)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            logging.debug(f"No path {origin} → {destination} for {weight}")
            return None

    def retrieve_cached_route(self, from_node: int, to_node: int,
                              normal_or_disrupted: str, cargo_type: str) -> Route | None:
        key = tuple(sorted((from_node, to_node)))
        cached = self.shortest_path_library.setdefault(normal_or_disrupted, {}).setdefault(cargo_type, {}).get(key)
        if cached is None:
            return None
        if from_node == key[0]:
            return cached
        return cached.reversed_copy()

    def cache_route(self, from_node: int, to_node: int,
                    normal_or_disrupted: str, cargo_type: str, route: Route):
        key = tuple(sorted((from_node, to_node)))
        library = self.shortest_path_library.setdefault(normal_or_disrupted, {}).setdefault(cargo_type, {})
        if from_node == key[0]:
            library[key] = route
        else:
            library[key] = route.reversed_copy()

    def is_route_available(self, route: Route) -> bool:
        """Check if a route's edges are all undisrupted."""
        return route.is_usable(self)

    def compute_route_cost(self, route: Route, cargo_type: str) -> float:
        """Sum the transport cost label of *cargo_type* along a route."""
        return route.sum_indicator(self, f"cost_per_ton_{cargo_type}")

    # ------------------------------------------------------------------
    # Disruption
    # ------------------------------------------------------------------

    def get_undisrupted_network(self) -> TransportNetwork:
        available_edges = [(u, v) for u, v in self.edges if not self[u][v].get("closed", False)]
        sub = self.edge_subgraph(available_edges)
        tn = TransportNetwork(sub)
        tn.cargo_types = list(self.cargo_types or [])
        tn.min_cost_per_tonkm = self.min_cost_per_tonkm
        return tn

    def disrupt_edges(self, edge_ids: list[int], duration: int):
        """Disrupt edges by their 'id' attribute."""
        edges_by_type = defaultdict(list)
        for u, v in self.edges:
            edge = self[u][v]
            if edge["id"] in edge_ids:
                self.start_edge_disruption(edge, 1.0, duration)
                edges_by_type[edge["type"]].append(edge["id"])
        if edges_by_type:
            logging.info("Transport disruption:")
            for etype, ids in sorted(edges_by_type.items()):
                logging.info(f"  {len(ids)} {etype} edge(s) disrupted for {duration} steps")

    def disrupt_edges_by_attribute(self, attribute: str, values: list, duration: int):
        """Disrupt edges where edge[attribute] is in values."""
        edge_ids = []
        for u, v in self.edges:
            edge = self[u][v]
            if edge.get(attribute) in values:
                self.start_edge_disruption(edge, 1.0, duration)
                edge_ids.append(edge["id"])
        if edge_ids:
            logging.info(f"Disrupted {len(edge_ids)} edges where {attribute} in {values} for {duration} steps")

    def update_road_disruption_state(self):
        for node_id in self.nodes:
            d = self._node[node_id]
            if d["disruption_duration"] > 0:
                d["disruption_duration"] -= 1
        for u, v in self.edges:
            d = self[u][v]
            if d["disruption_duration"] > 0:
                if math.isinf(d["disruption_duration"]):
                    continue
                d["disruption_duration"] = max(d["disruption_duration"] - 1, 0)
                d["disruption_elapsed"] = d.get("disruption_elapsed", 0) + 1
                if d["disruption_duration"] <= 0:
                    self.clear_edge_disruption(d)
                else:
                    self._refresh_edge_disruption_state(d)
        # Cost shocks expire the same way; cached alternatives are stale once
        # any shock ends.
        expired = False
        for u, v in self.edges:
            d = self[u][v]
            if d.get("cost_shock_duration", 0) > 0:
                if math.isinf(d["cost_shock_duration"]):
                    continue
                d["cost_shock_duration"] -= 1
                if d["cost_shock_duration"] <= 0:
                    self.clear_edge_cost_shock(d)
                    expired = True
        if expired:
            self.invalidate_alternative_routes()

    def reinitialize_flows_and_disruptions(self):
        for node_id in self.nodes:
            d = self._node[node_id]
            d["disruption_duration"] = 0
            d["shipments"] = {}
        shocked = False
        for u, v in self.edges:
            d = self[u][v]
            self.clear_edge_disruption(d)
            if d.get("cost_shock_duration", 0) or d.get("cost_shock_multiplier", 1.0) != 1.0:
                self.clear_edge_cost_shock(d)
                shocked = True
            d["shipments"] = {}
        self.capacity_gate_stats = {}
        if shocked:
            self.invalidate_alternative_routes()

    # ------------------------------------------------------------------
    # Shipment placement
    # ------------------------------------------------------------------
    # A shipment is one dict, shared by reference by every edge of its route
    # (``edge["shipments"][edge_key]``) and copied, or accumulated, at the
    # destination node under the link pid. It carries what the capacity gate
    # needs to cut it and to re-send the cut share: the link, the route, the
    # origin node, the round of the step it was placed in, the sender's pid and
    # transport share, and the unit price of this part of the delivery.

    def place_shipment(self, route: Route, link_pid: str, tons: float, destination_node: int,
                       monetary_quantity: float = 0.0, product_type: str = "",
                       flow_category: str = "", cargo_type: str = "",
                       accumulate_at_dest: bool = False, dest_key: str = "",
                       *, edge_key: str | None = None, link=None, origin: int | None = None,
                       leg: str = "main", round_no: int = 1, agent_pid=None,
                       transport_share: float = 0.0, price: float = 1.0,
                       base_price: float = 1.0) -> dict:
        """Place a shipment on all edges of a route and at the destination node.

        *edge_key* (default the link pid) identifies the shipment on the edges;
        a link that ships in several parts (the substitution-ceiling split, the
        gate's re-sent shares) uses one key per part so that they never
        overwrite each other on a shared edge. When *accumulate_at_dest* is
        True the destination-node shipment is accumulated under *dest_key*
        (the link pid), so the receiving agent sees one combined shipment per
        commercial link. Returns the shipment record.
        """
        node_key = dest_key if accumulate_at_dest and dest_key else link_pid
        key = edge_key or link_pid
        shipment = {
            "edge_key": key,
            "quantity": monetary_quantity,
            "tons": tons,
            "product_type": product_type,
            "flow_category": flow_category,
            "cargo_type": cargo_type,
            "link_pid": link_pid,
            "link": link,
            "route": route,
            "origin": origin,
            "destination": destination_node,
            "dest_key": node_key,
            "leg": leg,
            "round": round_no,
            "agent_pid": agent_pid,
            "transport_share": transport_share,
            "price": price,
            "base_price": base_price,
        }
        adj = self._adj
        for u, v in route.transport_edges:
            adj[u][v]["shipments"][key] = shipment

        # At destination node: accumulate parts or overwrite
        dest_shipments = self._node[destination_node].setdefault("shipments", {})
        if accumulate_at_dest and node_key in dest_shipments:
            existing = dest_shipments[node_key]
            existing["quantity"] = existing.get("quantity", 0) + monetary_quantity
            existing["tons"] = existing.get("tons", 0) + tons
        else:
            dest_shipments[node_key] = {"quantity": monetary_quantity, "tons": tons,
                                        "product_type": product_type, "flow_category": flow_category,
                                        "cargo_type": cargo_type, "link_pid": link_pid}
        return shipment

    def place_direct_delivery(self, link_pid: str, destination_node: int, monetary_quantity: float,
                              product_type: str = "", flow_category: str = "", cargo_type: str = ""):
        """Deposit a quantity at a destination node without a route.

        The pipelined part of a link's delivery: no edge carries it and no
        tonnage moves on the network, but the receiving agent collects it with
        the routed part under the link pid (accumulated like a second leg).
        """
        dest_shipments = self._node[destination_node].setdefault("shipments", {})
        existing = dest_shipments.get(link_pid)
        if existing is not None:
            existing["quantity"] = existing.get("quantity", 0) + monetary_quantity
        else:
            dest_shipments[link_pid] = {"quantity": monetary_quantity, "tons": 0.0,
                                        "product_type": product_type, "flow_category": flow_category,
                                        "cargo_type": cargo_type, "link_pid": link_pid}

    def adjust_destination_shipment(self, destination_node: int, dest_key: str,
                                    quantity_delta: float, tons_delta: float):
        """Change the quantity waiting at a destination node (a gate cut or re-send)."""
        dest = self._node[destination_node].get("shipments", {}).get(dest_key)
        if dest is None:
            return
        dest["quantity"] = max(0.0, dest.get("quantity", 0.0) + quantity_delta)
        dest["tons"] = max(0.0, dest.get("tons", 0.0) + tons_delta)

    def reset_loads(self):
        """Clear every shipment from the edges and the nodes (end of a step).

        The capacity gate statistics of the step are kept until the next gate
        run overwrites them (or a run reset clears them), so that a driver can
        read them after the step."""
        for _, _, edge in self.edges(data=True):
            edge["shipments"] = {}
        for node_id in self.nodes:
            self._node[node_id]["shipments"] = {}

    def check_no_uncollected_shipment(self):
        for u, v in self.edges:
            if self[u][v]["shipments"]:
                raise ValueError(f"Uncollected shipments on edge ({u},{v}): {list(self[u][v]['shipments'].keys())}")

    # ------------------------------------------------------------------
    # Flow analysis
    # ------------------------------------------------------------------

    def compute_flow_per_segment(self, time_step: int) -> list[dict]:
        flows = []
        for _, _, edge in self.edges(data=True):
            shipments = edge["shipments"].values()
            data = {"time_step": time_step, "id": edge["id"], "flow_total": 0, "flow_total_tons": 0}
            for s in shipments:
                fc, pt = s["flow_category"], s["product_type"]
                ct = s.get("cargo_type", "")
                qty, tons = s["quantity"], s["tons"]
                data[f"flow_{fc}_{pt}"] = data.get(f"flow_{fc}_{pt}", 0) + qty
                data[f"flow_{fc}"] = data.get(f"flow_{fc}", 0) + qty
                data[f"flow_{pt}"] = data.get(f"flow_{pt}", 0) + qty
                data["flow_total"] += qty
                data["flow_total_tons"] += tons
                if ct:
                    data[f"tons_{ct}"] = data.get(f"tons_{ct}", 0) + tons
                    data[f"usd_{ct}"] = data.get(f"usd_{ct}", 0) + qty
                # per-category tons (tons_cat_transit etc.): lets reporting
                # separate exogenous transit from the scope's own freight
                data[f"tons_cat_{fc}"] = data.get(f"tons_cat_{fc}", 0) + tons
            flows.append(data)
        return flows

    def compute_logistics_report(self, time_step: int,
                                 monitored_names: list[str] | None = None) -> dict:
        """Compute logistics report while shipments are on edges.

        Returns a dict with:
          - "monitored": list of dicts for edges matching *monitored_names*
          - "by_mode": dict of {mode: {tons, usd}} aggregates
          - "top_utilized": list of top 10 edges by max cargo utilization %
          - "network": dict of {total_tons, total_usd, n_edges_with_flow, n_edges_no_flow}
        """
        cargo_types = self.cargo_types or []
        monitored_set = set(monitored_names or [])

        monitored_rows = []
        mode_agg = defaultdict(lambda: {"tons": 0.0, "usd": 0.0})
        utilization_rows = []
        total_tons = 0.0
        total_usd = 0.0
        n_with_flow = 0
        n_no_flow = 0

        for _, _, edge in self.edges(data=True):
            shipments = edge["shipments"].values()

            # Accumulate per-cargo-type tons and USD from shipments
            ct_tons = defaultdict(float)
            ct_usd = defaultdict(float)
            edge_tons = 0.0
            edge_usd = 0.0
            for s in shipments:
                ct = s.get("cargo_type", "")
                tons = s["tons"]
                qty = s["quantity"]
                edge_tons += tons
                edge_usd += qty
                if ct:
                    ct_tons[ct] += tons
                    ct_usd[ct] += qty

            # Network-level aggregation
            mode = edge.get("type", "unknown")
            mode_agg[mode]["tons"] += edge_tons
            mode_agg[mode]["usd"] += edge_usd
            total_tons += edge_tons
            total_usd += edge_usd
            if edge_tons > 0:
                n_with_flow += 1
            else:
                n_no_flow += 1

            # Capacity utilization per cargo type (only capacitated edges have one)
            max_util = 0.0
            ct_detail = {}
            for ct in cargo_types:
                cap = _get_cargo_capacity(edge, ct)
                load = ct_tons.get(ct, 0.0)
                util = (load / cap * 100) if cap is not None and cap > 0 else 0.0
                ct_detail[ct] = {"tons": load, "usd": ct_usd.get(ct, 0.0),
                                 "capacity": cap,
                                 "utilization_pct": round(util, 1)}
                max_util = max(max_util, util)
            gate = getattr(self, "capacity_gate_stats", {}).get(edge.get("id"), {})

            row = {
                "time_step": time_step,
                "edge_id": edge.get("id", "?"),
                "name": edge.get("name", ""),
                "type": mode,
                "km": edge.get("km", 0),
                "flow_tons": round(edge_tons, 1),
                "flow_usd": round(edge_usd, 1),
                "max_utilization_pct": round(max_util, 1),
                **{f"tons_{ct}": round(ct_detail[ct]["tons"], 1) for ct in cargo_types},
                **{f"usd_{ct}": round(ct_detail[ct]["usd"], 1) for ct in cargo_types},
                **{f"capacity_{ct}": ct_detail[ct]["capacity"] for ct in cargo_types},
                **{f"utilization_{ct}_pct": ct_detail[ct]["utilization_pct"] for ct in cargo_types},
                # capacity gate of this step (empty when the edge was not gated)
                "offered_tons": round(gate.get("offered_tons", edge_tons), 1),
                "withheld_tons": round(gate.get("withheld_tons", 0.0), 1),
                "gate_rounds": gate.get("rounds", 0),
            }

            if edge.get("name", "") in monitored_set:
                monitored_rows.append(row)

            if max_util > 0:
                utilization_rows.append(row)

        # Sort by max utilization descending, keep top 10
        utilization_rows.sort(key=lambda r: r["max_utilization_pct"], reverse=True)
        top_utilized = utilization_rows[:10]

        return {
            "monitored": monitored_rows,
            "by_mode": dict(mode_agg),
            "top_utilized": top_utilized,
            "network": {
                "time_step": time_step,
                "total_tons": round(total_tons, 1),
                "total_usd": round(total_usd, 1),
                "n_edges_with_flow": n_with_flow,
                "n_edges_no_flow": n_no_flow,
            },
        }

# ======================================================================
# Module-level helpers
# ======================================================================

def _recovery_factor(time_since_start: int, duration: float,
                     shape: str, rate: float) -> float:
    """Return the recovered share of capacity for an edge disruption."""
    if duration <= 0:
        return 1.0
    if math.isinf(duration):
        return 0.0
    if time_since_start >= duration:
        return 1.0

    progress = time_since_start / duration
    if shape == "threshold":
        return 0.0
    if shape == "linear":
        return max(0.0, min(1.0, progress * rate))
    if shape == "exponential":
        if rate == 0:
            return progress
        return max(
            0.0,
            min(1.0, (1 - math.exp(-rate * progress)) / (1 - math.exp(-rate))),
        )
    raise ValueError(f"Unknown recovery shape: {shape}")


def _get_speed(edge_attr: dict, speed_dict: dict) -> float:
    if edge_attr["type"] in ("roads", "multimodal"):
        if isinstance(speed_dict.get("roads"), dict):
            attr_key = edge_attr.get(speed_dict["roads"]["attribute"], "default")
            return speed_dict["roads"].get(attr_key, speed_dict["roads"]["default"])
        return speed_dict.get("roads", 50)
    return speed_dict.get(edge_attr["type"], 50)


def _per_cargo(value, cargo_type: str) -> float:
    """Resolve a logistics value that may be a scalar or a per-cargo-type dict
    ({cargo_type: v, "default": v}). Per-cargo TRANSFER costs are what express
    dedicated transshipment infrastructure: a refinery rail siding makes the
    road-rail transfer near-free for liquid bulk while the same terminal costs
    a container its full lift - a distinction mode-level scalars cannot carry
    (the Romania v6 calibration bounded this: no scalar rail cost satisfies
    dry-bulk and liquid-bulk rail shares simultaneously)."""
    if isinstance(value, dict):
        return float(value.get(cargo_type, value.get("default", 0.0)))
    return float(value)


def _get_dwell_time_and_fee(edge_attr: dict, dwell_times: dict, loading_fees: dict):
    """Returns the configured values for this edge's multimodes key - each may
    be a scalar or a per-cargo dict; resolved per cargo in _calculate_cost_per_ton."""
    if edge_attr["type"] == "multimodal":
        key = edge_attr.get("multimodes", "")
        return dwell_times.get(key, 0.0), loading_fees.get(key, 0.0)
    return 0.0, 0.0


def _get_border_crossing_time_and_fee(edge_attr: dict, border_times: dict, border_fees: dict):
    special = edge_attr.get("special")
    if isinstance(special, str) and ("custom" in special or "border" in special):
        etype = edge_attr["type"]
        return border_times.get(etype, 0.0), border_fees.get(etype, 0.0)
    return 0.0, 0.0


def _calculate_cost_per_ton(edge_attr: dict, params: dict, cargo_types: list,
                            cargo_mode_eligibility: dict | None = None):
    """Calculate cost_per_ton for each cargo_type.

    The cost is per ton for the trip and does not depend on the simulation
    step: distance x rate per tkm, fees, and time in hours x cost_of_time in
    USD per ton-hour. Until 16 Sep 2026 the time term was also multiplied by
    days_per_step / 7, so the same trip valued an hour of travel 4.35x more
    at monthly resolution and 7x less at daily than at weekly (KI-37); the v1
    code had no such factor. Quantities that do scale with the step (edge
    capacities in tons per step) are converted in init_pipeline/transport.py.

    A cargo type that may not use this edge's mode (``cargo_mode_eligibility``:
    no bulk by air, only liquid bulk in pipelines) or whose capacity on this
    edge is an explicit 0 (transport_capacity_overrides) is skipped — no cost
    label is written, so the edge is invisible to Dijkstra for that cargo type.
    """
    edge_id = f"Edge {edge_attr.get('id', '?')} ({edge_attr.get('type', '?')})"

    km = edge_attr.get("km", 0.0)
    if isinstance(km, float) and np.isnan(km):
        raise ValueError(f"{edge_id}: km is nan")

    speed = _get_speed(edge_attr, params["speeds"])
    if speed == 0 or (isinstance(speed, float) and np.isnan(speed)):
        raise ValueError(f"{edge_id}: speed is 0 or nan")

    # cost_of_time is USD per ton-hour, either a scalar or a per-cargo-type
    # dict ({cargo_type: value, "default": value}). Per-cargo values of time
    # are what differentiates mode choice between cargo classes: containers
    # value time highly and shun slow modes, bulk barely values it and rides
    # the cheap slow ones — matching the commodity-level splits observed in
    # freight statistics (Eurostat NST breakdown).
    cot = params["cost_of_time"]

    # basic_cost per mode may itself be a per-cargo dict ({default: v, <cargo>: v}): line-haul
    # rates differ by vessel type on the Rhine (push-convoy bulk ~0.010, tank barges ~0.038,
    # container vessels ~0.022 EUR/tkm - evidence/waterway_rates_by_vessel_type.md, 8 Sep 2026).
    # It may also be keyed by an edge attribute, mirroring class-resolved speeds
    # ({attribute: class, <class>: rate, default: rate}) - e.g. 1520 mm UA/MD rail
    # tariffs run ~half the CFR level; the selected rate may itself be per-cargo.
    mode_basic_cost = _resolve_by_attribute(
        params["basic_cost"].get(edge_attr["type"], 0.01), edge_attr)
    transport_time = km / speed
    dwell_time, loading_fee = _get_dwell_time_and_fee(edge_attr, params.get("dwell_times", {}), params.get("loading_fees", {}))
    border_time, border_fee = _get_border_crossing_time_and_fee(edge_attr, params.get("border_crossing_times", {}), params.get("border_crossing_fees", {}))
    fixed_time = transport_time + border_time
    special_cost = params.get("name-specific", {}).get(edge_attr.get("name", ""), 0)

    fixed_base = special_cost + border_fee
    allowed = (cargo_mode_eligibility or {}).get(edge_attr["type"])

    for ct in cargo_types:
        # Skip ineligible or blocked cargo types — no cost label means the
        # edge is excluded from Dijkstra for this cargo type
        if allowed is not None and ct not in allowed:
            edge_attr.pop(f"cost_per_ton_{ct}", None)
            continue
        if _get_cargo_capacity(edge_attr, ct) == 0:
            edge_attr.pop(f"cost_per_ton_{ct}", None)
            continue
        ct_cot = _resolve_cost_of_time(cot, ct, edge_attr["type"])
        # dwell_times / loading_fees entries may be per-cargo dicts (see
        # _per_cargo): transfer costs, unlike line-haul costs, differ by
        # cargo class because of dedicated transshipment infrastructure
        cost = (fixed_base + km * _per_cargo(mode_basic_cost, ct) + _per_cargo(loading_fee, ct)
                + (fixed_time + _per_cargo(dwell_time, ct)) * ct_cot)
        edge_attr[f"cost_per_ton_{ct}"] = cost


def _resolve_by_attribute(value, edge_attr: dict):
    """Resolve a cost spec keyed by an edge attribute.

    {attribute: <edge attr>, <attr value>: rate, default: rate} picks the
    rate for this edge's attribute value; any other form passes through.
    The returned rate may itself be a per-cargo dict (handled downstream).
    """
    if isinstance(value, dict) and "attribute" in value:
        key = str(edge_attr.get(value["attribute"], "default"))
        return value.get(key, value.get("default", 0.01))
    return value


def _resolve_cost_of_time(cot, cargo_type: str, edge_type: str) -> float:
    """Value of time (USD per ton-hour) for a cargo type on an edge of *edge_type*.

    Accepted forms of ``logistics.cost_of_time``:
      - scalar                                   -> every cargo, every mode
      - {cargo_type: scalar, default: scalar}    -> per cargo class
      - {cargo_type: {default: v, <mode>: v}}    -> per cargo AND per mode

    The per-mode form exists because the inland value of time stands in for
    service quality (frequency, reliability, damage risk) and is calibrated
    to separate road from rail; applied to a sea leg, where every option is a
    ship, it priced 100 extra hours Suez->Rotterdam at 160 USD/t for
    containers (EU scope, 2026-09-03) and pushed Asian imports into the
    nearest Mediterranean port. Connector edges (type "multimodal") use the
    cargo's default: terminal dwell is inland handling time.
    """
    if isinstance(cot, dict):
        value = cot.get(cargo_type, cot.get("default", 0.49))
    else:
        value = cot
    if isinstance(value, dict):
        value = value.get(edge_type, value.get("default", 0.49))
    return float(value)


def _get_cargo_capacity(edge_attr: dict, cargo_type: str) -> float | None:
    """Effective capacity (tons per step) for a cargo type on an edge.

    The per-cargo capacity if defined, otherwise the shared capacity, otherwise
    None (no capacity: the edge is never gated). 0 means blocked.
    """
    ct_cap = edge_attr.get(f"capacity_{cargo_type}")
    if ct_cap is not None:
        return float(ct_cap)
    shared = edge_attr.get("capacity")
    return float(shared) if shared is not None else None
