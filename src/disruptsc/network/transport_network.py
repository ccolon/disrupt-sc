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

# Cost used to penalize unsupported shipment-mode combinations
TRANSPORT_MALUS = 1e9


def degrees_to_km(lon1, lat1, lon2, lat2) -> float:
    """Haversine-approximation distance in km."""
    lat_km = 111 * abs(lat2 - lat1)
    lon_km = 111 * abs(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return math.sqrt(lat_km ** 2 + lon_km ** 2)


class TransportNetwork(nx.Graph):

    def __init__(self, graph=None, **attr):
        super().__init__(graph, **attr)
        self.shipment_methods: list[str] | None = None
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
        self.shipment_methods = list(logistic_parameters["shipment_methods_to_transport_modes"].keys())
        nb_profiles = logistic_parameters["nb_cost_profiles"]
        self.shortest_path_library = {
            i: {"normal": {m: {} for m in self.shipment_methods},
                "alternative": {m: {} for m in self.shipment_methods}}
            for i in range(nb_profiles)
        }
        for _, attr in self.edges.items():
            _calculate_cost_per_ton(attr, logistic_parameters, time_resolution)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def provide_shortest_route(self, origin: int, destination: int,
                               shipment_method: str, route_weight: str) -> Route | None:
        if origin not in self.nodes:
            logging.debug(f"Origin {origin} not in available network")
            return None
        if destination not in self.nodes:
            logging.debug(f"Destination {destination} not in available network")
            return None
        weight = route_weight + "_" + shipment_method
        try:
            sp = nx.shortest_path(self, origin, destination, weight=weight)
            return Route(sp, self, shipment_method)
        except nx.NetworkXNoPath:
            logging.debug(f"No path {origin} → {destination}")
            return None

    def retrieve_cached_route(self, from_node: int, to_node: int, cost_profile: int,
                              normal_or_disrupted: str, shipment_method: str) -> Route | None:
        key = tuple(sorted((from_node, to_node)))
        cached = self.shortest_path_library[cost_profile][normal_or_disrupted][shipment_method].get(key)
        if cached is None:
            return None
        if from_node == key[0]:
            return cached
        route = copy.deepcopy(cached)
        route.revert()
        return route

    def cache_route(self, from_node: int, to_node: int, cost_profile: int,
                    normal_or_disrupted: str, shipment_method: str, route: Route):
        key = tuple(sorted((from_node, to_node)))
        if from_node == key[0]:
            self.shortest_path_library[cost_profile][normal_or_disrupted][shipment_method][key] = route
        else:
            canonical = copy.deepcopy(route)
            canonical.revert()
            self.shortest_path_library[cost_profile][normal_or_disrupted][shipment_method][key] = canonical

    def is_route_available(self, route: Route) -> bool:
        """Check if a route's edges are all undisrupted."""
        return route.is_usable(self)

    def compute_route_cost(self, route: Route, shipment_method: str, cost_profile: int) -> float:
        """Sum cost_per_ton along a route."""
        weight = f"cost_per_ton_{cost_profile}_{shipment_method}"
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
            d["current_load"] = 0
            d["overused"] = False

    # ------------------------------------------------------------------
    # Shipment placement & load tracking
    # ------------------------------------------------------------------

    def place_shipment(self, route: Route, link_pid: str, tons: float, destination_node: int):
        """Place a shipment on all edges of a route and at the destination node."""
        shipment = {"quantity": tons}
        for u, v in route.transport_edges:
            self[u][v]["shipments"][link_pid] = shipment
        self._node[destination_node]["shipments"][link_pid] = shipment

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
        self.update_load_on_route(route, link.delivery_in_tons, capacity_constraint, capacity_constraint_mode)

    def update_load_on_route(self, route: Route, load: float,
                             capacity_constraint: bool, capacity_constraint_mode: str = "gradual"):
        cost_labels = self._get_cost_labels(with_capacity=False)
        cap_labels = self._get_cost_labels(with_capacity=True)
        for u, v in route.transport_edges:
            edge = self[u][v]
            edge["current_load"] += load
            if capacity_constraint:
                if capacity_constraint_mode == "gradual":
                    mult = _capacity_multiplier(edge["current_load"], edge["capacity"])
                    for i, cl in enumerate(cost_labels):
                        edge[cap_labels[i]] = edge[cl] * mult
                    edge["overused"] = edge["current_load"] > edge["capacity"]
                else:  # binary
                    if not edge.get("overused", False) and edge["current_load"] > edge["capacity"]:
                        edge["overused"] = True
                        for cl in cap_labels:
                            edge[cl] += 1e10

    def reset_loads(self):
        cost_labels = self._get_cost_labels(with_capacity=False)
        cap_labels = self._get_cost_labels(with_capacity=True)
        for u, v in self.edges:
            edge = self[u][v]
            edge["current_load"] = 0
            edge["overused"] = False
            edge["shipments"] = {}
            for i, cl in enumerate(cost_labels):
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
                qty, tons = s["quantity"], s["tons"]
                data[f"flow_{fc}_{pt}"] = data.get(f"flow_{fc}_{pt}", 0) + qty
                data[f"flow_{fc}"] = data.get(f"flow_{fc}", 0) + qty
                data[f"flow_{pt}"] = data.get(f"flow_{pt}", 0) + qty
                data["flow_total"] += qty
                data["flow_total_tons"] += tons
            flows.append(data)
        return flows

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
    if capacity <= 0:
        return 1.0
    u = current_load / capacity
    if u < 0.7:
        return 1.0
    elif u < 0.9:
        return 1.0 + (u - 0.7) * 2.5
    elif u < 1.0:
        return 1.5 + (u - 0.9) * 15.0
    else:
        return 3.0 + min(u - 1.0, 1.0) * 7.0


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


def _calculate_cost_per_ton(edge_attr: dict, params: dict, time_resolution: str):
    edge_id = f"Edge {edge_attr.get('id', '?')} ({edge_attr.get('type', '?')})"

    km = edge_attr.get("km", 0.0)
    if isinstance(km, float) and np.isnan(km):
        raise ValueError(f"{edge_id}: km is nan")

    speed = _get_speed(edge_attr, params["speeds"])
    if speed == 0 or (isinstance(speed, float) and np.isnan(speed)):
        raise ValueError(f"{edge_id}: speed is 0 or nan")

    time_factor = {"day": 1, "week": 7, "month": 365.25 / 12, "year": 365.25}
    adjusted_delay_cost = params["cost_of_time"] * (time_factor[time_resolution] / 7)

    basic_costs = {
        i: km * profile[edge_attr["type"]]
        for i, profile in params["basic_cost_profiles"].items()
    }
    transport_time = km / speed
    dwell_time, loading_fee = _get_dwell_time_and_fee(edge_attr, params.get("dwell_times", {}), params.get("loading_fees", {}))
    border_time, border_fee = _get_border_crossing_time_and_fee(edge_attr, params.get("border_crossing_times", {}), params.get("border_crossing_fees", {}))
    total_time = transport_time + dwell_time + border_time
    total_fee = loading_fee + border_fee
    special_cost = params.get("name-specific", {}).get(edge_attr.get("name", ""), 0)

    costs = {i: bc + special_cost + total_fee + total_time * adjusted_delay_cost
             for i, bc in basic_costs.items()}

    for method, modes in params["shipment_methods_to_transport_modes"].items():
        for i, cost in costs.items():
            if edge_attr["type"] in modes:
                edge_attr[f"cost_per_ton_{i}_{method}"] = cost
                edge_attr[f"cost_per_ton_with_capacity_{i}_{method}"] = cost
            else:
                edge_attr[f"cost_per_ton_{i}_{method}"] = TRANSPORT_MALUS
                edge_attr[f"cost_per_ton_with_capacity_{i}_{method}"] = TRANSPORT_MALUS
