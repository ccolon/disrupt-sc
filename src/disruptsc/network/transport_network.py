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

    def ingest_logistic_data(self, logistic_parameters: dict, time_resolution: str):
        # Derive cargo types from sector_to_cargo_type mapping
        cargo_type_values = list(logistic_parameters.get("sector_to_cargo_type", {}).values())
        self.cargo_types = sorted(set(ct for ct in cargo_type_values if ct != "default"))
        if not self.cargo_types:
            self.cargo_types = ["container", "dry_bulk", "liquid_bulk"]
        self.shortest_path_library = {
            "normal": {m: {} for m in self.cargo_types},
            "alternative": {m: {} for m in self.cargo_types},
        }
        for _, attr in self.edges.items():
            _calculate_cost_per_ton(attr, logistic_parameters, self.cargo_types, time_resolution)

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

    def compute_route_cost(self, route: Route, cargo_type: str) -> float:
        """Sum cost_per_ton along a route."""
        weight = f"cost_per_ton_{cargo_type}"
        return route.sum_indicator(self, weight)

    # ------------------------------------------------------------------
    # Disruption
    # ------------------------------------------------------------------

    def get_undisrupted_network(self) -> TransportNetwork:
        available_edges = [(u, v) for u, v in self.edges if self[u][v]["disruption_duration"] == 0]
        sub = self.edge_subgraph(available_edges)
        tn = TransportNetwork(sub)
        tn.min_cost_per_tonkm = self.min_cost_per_tonkm
        return tn

    def disrupt_edges(self, edge_ids: list[int], duration: int):
        """Disrupt edges by their 'id' attribute."""
        edges_by_type = defaultdict(list)
        for u, v in self.edges:
            edge = self[u][v]
            if edge["id"] in edge_ids:
                edge["disruption_duration"] = duration
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
                edge["disruption_duration"] = duration
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
                d["disruption_duration"] -= 1

    def reinitialize_flows_and_disruptions(self):
        for node_id in self.nodes:
            d = self._node[node_id]
            d["disruption_duration"] = 0
            d["shipments"] = {}
        for u, v in self.edges:
            d = self[u][v]
            d["disruption_duration"] = 0
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
                        accumulate_at_dest: bool = False, dest_key: str = ""):
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

    def transport_shipment(self, link: CommercialLink, capacity_constraint: bool,
                           capacity_constraint_mode: str = "gradual"):
        """Legacy method: place shipment and update load from a CommercialLink."""
        route = link.get_current_route()
        shipment = {
            "supplier_id": link.supplier_id,
            "buyer_id": link.buyer_id,
            "origin_node": link.origin_node,
            "destination_node": link.destination_node,
            "quantity": link.delivery,
            "tons": link.delivery_in_tons,
            "product_type": link.product_type,
            "flow_category": link.category,
            "price": link.price,
        }
        for u, v in route.transport_edges:
            self[u][v]["shipments"][link.pid] = shipment
        self._node[link.destination_node]["shipments"][link.pid] = shipment
        self.update_load_on_route(route, link.delivery_in_tons, link.cargo_type,
                                 capacity_constraint, capacity_constraint_mode)

    def update_load_on_route(self, route: Route, load: float,
                             cargo_type: str,
                             capacity_constraint: bool,
                             capacity_constraint_mode: str = "gradual"):
        """Update per-cargo-type loads on route edges and adjust capacity costs."""
        for u, v in route.transport_edges:
            edge = self[u][v]
            load_key = f"current_load_{cargo_type}"
            edge[load_key] = edge.get(load_key, 0) + load

            if capacity_constraint:
                cap = _get_cargo_capacity(edge, cargo_type)
                current = edge[load_key]
                # Also check shared capacity (total load across all cargo types)
                total_load = sum(edge.get(f"current_load_{ct}", 0) for ct in self.cargo_types)
                shared_cap = edge.get("capacity", 1e9)

                if capacity_constraint_mode == "gradual":
                    # Congestion from cargo-specific capacity
                    ct_mult = _capacity_multiplier(current, cap) if cap < 1e8 else 1.0
                    # Congestion from shared capacity
                    shared_mult = _capacity_multiplier(total_load, shared_cap) if f"capacity_{cargo_type}" not in edge else 1.0
                    mult = max(ct_mult, shared_mult)

                    # Update cost_per_ton_with_capacity for this cargo type only
                    base_key = f"cost_per_ton_{cargo_type}"
                    cap_key = f"cost_per_ton_with_capacity_{cargo_type}"
                    if base_key in edge:
                        edge[cap_key] = edge[base_key] * mult

                    edge["overused"] = total_load > shared_cap or current > cap
                else:  # binary
                    over = current > cap or total_load > shared_cap
                    if over and not edge.get("overused", False):
                        edge["overused"] = True
                        cap_key = f"cost_per_ton_with_capacity_{cargo_type}"
                        if cap_key in edge:
                            edge[cap_key] += 1e10

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
    """Barrier cost multiplier that grows to infinity at and beyond capacity.

    Below capacity:  1 + (u / (1 - u))²   — smooth barrier approaching capacity
    Above capacity:  scales as (u)²        — continues growing with overcapacity

    This ensures that overcapacity edges become progressively more expensive,
    not capped at a fixed maximum.
    """
    if capacity <= 0:
        return 1.0
    u = current_load / capacity
    if u < 0.999:
        return 1.0 + (u / (1.0 - u)) ** 2
    else:
        # Beyond capacity: multiplier keeps growing with load
        # At u=1: ~1e6, at u=2: ~4e6, at u=10: ~1e8
        return 1.0 + (u * 1000) ** 2


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
