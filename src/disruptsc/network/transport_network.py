"""TransportNetwork — nx.Graph wrapper for multimodal transport infrastructure."""

from __future__ import annotations

import copy
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

    def ingest_logistic_data(self, logistic_parameters: dict, time_resolution: str,
                             use_cargo_types: bool = True):
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
        for _, attr in self.edges.items():
            _calculate_cost_per_ton(attr, logistic_parameters, self.cargo_types, time_resolution)
        self.capture_base_capacity_state()

    def shrink_cargo_types_to(self, used: set[str]) -> None:
        """Prune cargo_types to only those listed in *used*.

        Removes per-cargo-type labels (cost_per_ton_, current_load_,
        capacity_, base_capacity_, cost_per_ton_with_capacity_) for the
        dropped types, and resets shortest_path_library. Safe to call after
        ingest_logistic_data — useful when the actual supply chain uses
        fewer cargo types than the network was set up for, so Dijkstra/LP
        runs N× fewer times.
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
        prefixes = (
            "cost_per_ton_", "cost_per_ton_with_capacity_",
            "current_load_", "capacity_", "base_capacity_",
        )
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

    def capture_base_capacity_state(self):
        """Snapshot the edge capacities that represent the undisrupted network."""
        for u, v in self.edges:
            edge = self[u][v]
            edge["base_capacity"] = float(edge.get("capacity", 1e9))
            for ct in (self.cargo_types or []):
                key = f"capacity_{ct}"
                base_key = f"base_{key}"
                if key in edge:
                    edge[base_key] = float(edge[key])
                else:
                    edge.pop(base_key, None)

    def ensure_base_capacity_state(self, edge: dict):
        """Backfill missing base-capacity fields for networks loaded from old caches."""
        if edge.get("base_capacity") is None:
            edge["base_capacity"] = float(edge.get("capacity", 1e9))
        for ct in (self.cargo_types or []):
            key = f"capacity_{ct}"
            base_key = f"base_{key}"
            if key in edge and edge.get(base_key) is None:
                edge[base_key] = float(edge[key])

    def restore_edge_capacity(self, edge: dict):
        """Restore dynamic capacities from the saved undisrupted state."""
        self.ensure_base_capacity_state(edge)
        edge["capacity"] = float(edge.get("base_capacity", edge.get("capacity", 1e9)))
        for ct in (self.cargo_types or []):
            key = f"capacity_{ct}"
            base_key = f"base_{key}"
            if base_key in edge:
                edge[key] = float(edge[base_key])
            else:
                edge.pop(key, None)
        edge["closed"] = False

    def apply_edge_capacity_factor(self, edge: dict, factor: float):
        """Scale the edge's dynamic capacities by *factor* relative to base state."""
        self.ensure_base_capacity_state(edge)
        factor = max(0.0, min(1.0, float(factor)))
        edge["capacity"] = float(edge.get("base_capacity", edge.get("capacity", 1e9))) * factor
        for ct in (self.cargo_types or []):
            key = f"capacity_{ct}"
            base_key = f"base_{key}"
            if base_key in edge:
                edge[key] = float(edge[base_key]) * factor
            elif key in edge:
                edge.pop(key, None)
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
        edge["disruption_duration"] = 0
        edge["disruption_total_duration"] = 0
        edge["disruption_elapsed"] = 0
        edge["disruption_initial_reduction"] = 0.0
        edge["disruption_recovery_shape"] = "threshold"
        edge["disruption_recovery_rate"] = 1.0

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
                               cargo_type: str, route_weight: str) -> Route | None:
        if origin not in self.nodes:
            logging.debug(f"Origin {origin} not in available network")
            return None
        if destination not in self.nodes:
            logging.debug(f"Destination {destination} not in available network")
            return None
        weight = route_weight + "_" + cargo_type

        # Use a subgraph view that only includes edges carrying this weight.
        # Edges without the label (blocked cargo type) would otherwise get
        # NetworkX's default weight of 1, making them appear cheapest.
        def edge_ok(u, v):
            return weight in self[u][v]

        subgraph = nx.subgraph_view(self, filter_edge=edge_ok)
        try:
            sp = nx.shortest_path(subgraph, origin, destination, weight=weight)
            return Route(sp, self, cargo_type)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            logging.debug(f"No path {origin} → {destination} for {weight}")
            return None

    def retrieve_cached_route(self, from_node: int, to_node: int,
                              normal_or_disrupted: str, cargo_type: str) -> Route | None:
        key = tuple(sorted((from_node, to_node)))
        cached = self.shortest_path_library[normal_or_disrupted][cargo_type].get(key)
        if cached is None:
            return None
        if from_node == key[0]:
            return cached
        route = copy.deepcopy(cached)
        route.revert()
        return route

    def cache_route(self, from_node: int, to_node: int,
                    normal_or_disrupted: str, cargo_type: str, route: Route):
        key = tuple(sorted((from_node, to_node)))
        if from_node == key[0]:
            self.shortest_path_library[normal_or_disrupted][cargo_type][key] = route
        else:
            canonical = copy.deepcopy(route)
            canonical.revert()
            self.shortest_path_library[normal_or_disrupted][cargo_type][key] = canonical

    def is_route_available(self, route: Route) -> bool:
        """Check if a route's edges are all undisrupted."""
        return route.is_usable(self)

    def compute_route_cost(self, route: Route, cargo_type: str,
                           with_capacity: bool = False) -> float:
        """Sum the chosen transport cost label along a route."""
        prefix = "cost_per_ton_with_capacity" if with_capacity else "cost_per_ton"
        weight = f"{prefix}_{cargo_type}"
        return route.sum_indicator(self, weight)

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

    def reinitialize_flows_and_disruptions(self):
        for node_id in self.nodes:
            d = self._node[node_id]
            d["disruption_duration"] = 0
            d["shipments"] = {}
        for u, v in self.edges:
            d = self[u][v]
            self.clear_edge_disruption(d)
            d["shipments"] = {}
            for ct in (self.cargo_types or []):
                d[f"current_load_{ct}"] = 0
            d["overused"] = False

    # ------------------------------------------------------------------
    # Shipment placement & load tracking
    # ------------------------------------------------------------------

    def place_shipment(self, route: Route, link_pid: str, tons: float, destination_node: int,
                        monetary_quantity: float = 0.0, product_type: str = "",
                        flow_category: str = "", cargo_type: str = "",
                        accumulate_at_dest: bool = False, dest_key: str = "",
                        capacity_constraint: bool = False,
                        capacity_constraint_mode: str = "gradual"):
        """Place a shipment on all edges of a route and at the destination node.

        When *accumulate_at_dest* is True, the destination-node shipment is
        accumulated under *dest_key* (used for chunked multi-route delivery
        so the receiving agent sees one combined shipment per commercial link).
        """
        shipment = {
            "quantity": monetary_quantity,
            "tons": tons,
            "product_type": product_type,
            "flow_category": flow_category,
            "cargo_type": cargo_type,
        }
        for u, v in route.transport_edges:
            self[u][v]["shipments"][link_pid] = shipment

        # At destination node: accumulate chunks or overwrite
        node_key = dest_key if accumulate_at_dest and dest_key else link_pid
        dest_shipments = self._node[destination_node].setdefault("shipments", {})
        if accumulate_at_dest and node_key in dest_shipments:
            existing = dest_shipments[node_key]
            existing["quantity"] = existing.get("quantity", 0) + monetary_quantity
            existing["tons"] = existing.get("tons", 0) + tons
        else:
            dest_shipments[node_key] = dict(shipment)

        if tons > 0 and cargo_type:
            self.update_load_on_route(
                route, tons, cargo_type,
                capacity_constraint, capacity_constraint_mode,
            )

    def transport_shipment(self, link: CommercialLink, capacity_constraint: bool,
                           capacity_constraint_mode: str = "gradual"):
        """Legacy method: place shipment and update load from a CommercialLink."""
        route = link.get_current_route()
        self.place_shipment(
            route, link.pid, link.delivery_in_tons, link.destination_node,
            monetary_quantity=link.delivery, product_type=link.product_type,
            flow_category=link.category, cargo_type=link.cargo_type,
            capacity_constraint=capacity_constraint,
            capacity_constraint_mode=capacity_constraint_mode,
        )

    def update_load_on_route(self, route: Route, load: float,
                             cargo_type: str,
                             capacity_constraint: bool,
                             capacity_constraint_mode: str = "gradual"):
        """Update per-cargo-type loads on route edges.

        Load tracking always happens. When *capacity_constraint* is enabled,
        edge costs are also refreshed so later routes see the updated scarcity.
        """
        for u, v in route.transport_edges:
            edge = self[u][v]
            load_key = f"current_load_{cargo_type}"
            edge[load_key] = edge.get(load_key, 0) + load

            if capacity_constraint:
                _refresh_edge_capacity_costs(edge, self.cargo_types or [], capacity_constraint_mode)

    def reset_loads(self):
        """Reset all load tracking and capacity costs to base values."""
        cost_labels = self._get_cost_labels(with_capacity=False)
        cap_labels = self._get_cost_labels(with_capacity=True)
        for u, v in self.edges:
            edge = self[u][v]
            for ct in (self.cargo_types or []):
                edge[f"current_load_{ct}"] = 0
            edge["overused"] = False
            edge["shipments"] = {}
            for i, cl in enumerate(cost_labels):
                if cl in edge:  # blocked cargo types have no cost labels
                    edge[cap_labels[i]] = edge[cl]
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
        for u, v in self.edges():
            shipments = self[u][v]["shipments"].values()
            data = {"time_step": time_step, "id": self[u][v]["id"], "flow_total": 0, "flow_total_tons": 0}
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

        for u, v in self.edges():
            edge = self[u][v]
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

            # Capacity utilization per cargo type
            max_util = 0.0
            ct_detail = {}
            for ct in cargo_types:
                cap = _get_cargo_capacity(edge, ct)
                load = ct_tons.get(ct, 0.0)
                util = (load / cap * 100) if cap > 0 and cap < 1e8 else 0.0
                ct_detail[ct] = {"tons": load, "usd": ct_usd.get(ct, 0.0),
                                 "capacity": cap if cap < 1e8 else None,
                                 "utilization_pct": round(util, 1)}
                max_util = max(max_util, util)

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

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_cost_labels(self, with_capacity: bool) -> list[str]:
        _, _, data = next(iter(self.edges(data=True)))
        prefix = "cost_per_ton_with_capacity" if with_capacity else "cost_per_ton"
        exclude = "cost_per_ton_with" if not with_capacity else None
        return [k for k in data if k.startswith(prefix) and (exclude is None or not k.startswith(exclude) or with_capacity)]


# ======================================================================
# Module-level helpers
# ======================================================================

def _capacity_multiplier(current_load: float, capacity: float) -> float:
    """Piecewise capacity surcharge (Form A, 5-branch).

    - u ≤ 0.8          :  0.5·(1 + u/0.8)          — gentle ramp 0.5 → 1.0
    - 0.8 < u ≤ 1.0    :  1 + 5·(u − 0.8)          — linear       1.0 → 2.0
    - 1.0 < u ≤ 1.05   :  2 + 60·(u − 1.0)         — steep        2.0 → 5.0
    - 1.05 < u ≤ 1.1   :  5 + 100·(u − 1.05)       — steeper      5.0 → 10.0
    - u > 1.1          :  10 + 1000·(u − 1.1)      — linear blowup

    Aligned (at breakpoints) with LP piecewise surcharge in
    init_pipeline/routing.py via h(u) = (f(u)−1)·u.
    """
    if capacity <= 0:
        return 1.0
    u = current_load / capacity
    if u <= 0.8:
        return 0.5 * (1.0 + u / 0.8)
    if u <= 1.0:
        return 1.0 + 5.0 * (u - 0.8)
    if u <= 1.05:
        return 2.0 + 60.0 * (u - 1.0)
    if u <= 1.1:
        return 5.0 + 100.0 * (u - 1.05)
    return 10.0 + 1000.0 * (u - 1.1)


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


def _refresh_edge_capacity_costs(edge: dict, cargo_types: list[str], mode: str):
    """Refresh all congestion-adjusted cost labels for a single edge."""
    shared_cap = edge.get("capacity", 1e9)
    total_load = sum(edge.get(f"current_load_{ct}", 0) for ct in cargo_types)
    edge["overused"] = False

    for ct in cargo_types:
        base_key = f"cost_per_ton_{ct}"
        cap_key = f"cost_per_ton_with_capacity_{ct}"
        if base_key not in edge:
            continue

        ct_cap = _get_cargo_capacity(edge, ct)
        ct_load = edge.get(f"current_load_{ct}", 0)
        has_ct_cap = f"capacity_{ct}" in edge
        over_ct = ct_cap < 1e8 and ct_cap > 0 and ct_load > ct_cap
        over_shared = shared_cap < 1e8 and total_load > shared_cap and not has_ct_cap
        edge["overused"] = edge["overused"] or over_ct or over_shared

        if mode == "binary":
            edge[cap_key] = edge[base_key] + (1e10 if (over_ct or over_shared) else 0.0)
            continue

        ct_mult = _capacity_multiplier(ct_load, ct_cap) if ct_cap < 1e8 else 1.0
        shared_mult = _capacity_multiplier(total_load, shared_cap) if not has_ct_cap else 1.0
        edge[cap_key] = edge[base_key] * max(ct_mult, shared_mult)


def _get_speed(edge_attr: dict, speed_dict: dict) -> float:
    if edge_attr["type"] in ("roads", "multimodal"):
        if isinstance(speed_dict.get("roads"), dict):
            attr_key = edge_attr.get(speed_dict["roads"]["attribute"], "default")
            return speed_dict["roads"].get(attr_key, speed_dict["roads"]["default"])
        return speed_dict.get("roads", 50)
    return speed_dict.get(edge_attr["type"], 50)


def _get_dwell_time_and_fee(edge_attr: dict, dwell_times: dict, loading_fees: dict):
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


def _calculate_cost_per_ton(edge_attr: dict, params: dict, cargo_types: list, time_resolution: str):
    """Calculate cost_per_ton for each cargo_type.

    Cargo types with zero capacity on this edge are skipped — no cost label
    is written, so the edge is invisible to Dijkstra for that cargo type.
    """
    edge_id = f"Edge {edge_attr.get('id', '?')} ({edge_attr.get('type', '?')})"

    km = edge_attr.get("km", 0.0)
    if isinstance(km, float) and np.isnan(km):
        raise ValueError(f"{edge_id}: km is nan")

    speed = _get_speed(edge_attr, params["speeds"])
    if speed == 0 or (isinstance(speed, float) and np.isnan(speed)):
        raise ValueError(f"{edge_id}: speed is 0 or nan")

    time_factor = {"day": 1, "week": 7, "month": 365.25 / 12, "year": 365.25}
    adjusted_delay_cost = params["cost_of_time"] * (time_factor[time_resolution] / 7)

    basic_cost = km * params["basic_cost"].get(edge_attr["type"], 0.01)
    transport_time = km / speed
    dwell_time, loading_fee = _get_dwell_time_and_fee(edge_attr, params.get("dwell_times", {}), params.get("loading_fees", {}))
    border_time, border_fee = _get_border_crossing_time_and_fee(edge_attr, params.get("border_crossing_times", {}), params.get("border_crossing_fees", {}))
    total_time = transport_time + dwell_time + border_time
    total_fee = loading_fee + border_fee
    special_cost = params.get("name-specific", {}).get(edge_attr.get("name", ""), 0)

    cost = basic_cost + special_cost + total_fee + total_time * adjusted_delay_cost

    for ct in cargo_types:
        # Skip blocked cargo types — no cost label means the edge is
        # excluded from Dijkstra for this cargo type
        ct_capacity = _get_cargo_capacity(edge_attr, ct)
        if ct_capacity == 0:
            continue
        edge_attr[f"cost_per_ton_{ct}"] = cost
        edge_attr[f"cost_per_ton_with_capacity_{ct}"] = cost


def _get_cargo_capacity(edge_attr: dict, cargo_type: str) -> float:
    """Get the effective capacity for a cargo type on an edge.

    Returns the per-cargo-type capacity if defined, otherwise the shared capacity.
    A return value of 0 means this cargo type is blocked on this edge.
    """
    ct_cap = edge_attr.get(f"capacity_{cargo_type}")
    if ct_cap is not None:
        return float(ct_cap)
    return float(edge_attr.get("capacity", 1e9))
