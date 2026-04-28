"""Route — ordered path through the transport network."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from disruptsc.network.transport_network import TransportNetwork


class Route(list):
    """A route is an alternating sequence of nodes and edges: [(n1,), (n1,n2), (n2,), ...]."""

    def __init__(self, node_list: list, transport_network: TransportNetwork, cargo_type: str):
        node_edge_tuple = [[(node_list[0],)]] + [
            [(node_list[i], node_list[i + 1]), (node_list[i + 1],)]
            for i in range(len(node_list) - 1)
        ]
        transport_nodes_and_edges = [item for sub in node_edge_tuple for item in sub]
        super().__init__(transport_nodes_and_edges)
        self.transport_nodes_and_edges = transport_nodes_and_edges
        self.transport_nodes = node_list
        self.transport_edges = [item for item in transport_nodes_and_edges if len(item) == 2]
        self.transport_edge_ids = [
            transport_network[u][v]["id"] for u, v in self.transport_edges
        ]
        self.transport_modes = list({
            transport_network[u][v]["type"] for u, v in self.transport_edges
        })
        self.length = self.sum_indicator(transport_network, "km")

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_usable(self, transport_network: TransportNetwork) -> bool:
        for u, v in self.transport_edges:
            if not transport_network.has_edge(u, v):
                return False
            if transport_network[u][v].get("closed", False):
                return False
        return True

    def has_over_capacity_edges(self, transport_network: TransportNetwork) -> bool:
        for u, v in self.transport_edges:
            if transport_network[u][v].get("overused", False):
                return True
        return False

    def is_edge_in_route(self, searched_edge, transport_network: TransportNetwork) -> bool:
        if isinstance(searched_edge, tuple):
            for u, v in self.transport_edges:
                if searched_edge[0] == u and searched_edge[1] == v:
                    return True
        elif isinstance(searched_edge, str):
            for u, v in self.transport_edges:
                if transport_network[u][v].get("name") == searched_edge:
                    return True
        return False

    def sum_indicator(self, transport_network: TransportNetwork, indicator: str, per_type: bool = False):
        if per_type:
            details = []
            for u, v in self.transport_edges:
                edge = transport_network[u][v]
                details.append({
                    "id": edge["id"],
                    "type": edge["type"],
                    "multimodes": edge.get("multimodes", "N/A"),
                    "special": edge.get("special", "N/A"),
                    indicator: edge[indicator],
                })
            df = pd.DataFrame(details).fillna("N/A")
            return df.groupby(["type", "multimodes", "special"])[indicator].sum()
        total = 0.0
        for u, v in self.transport_edges:
            total += transport_network[u][v][indicator]
        return total

    def get_maritime_multimodal_edges(self, transport_network: TransportNetwork) -> set:
        result = set()
        for u, v in self.transport_edges:
            edge = transport_network[u][v]
            if edge.get("type") == "multimodal" and "maritime" in (edge.get("multimodes") or ""):
                result.add((u, v))
        return result

    def revert(self):
        """Reverse the route in-place."""
        reversed_items = []
        for item in reversed(self):
            if isinstance(item, tuple) and len(item) == 2:
                reversed_items.append((item[1], item[0]))
            else:
                reversed_items.append(item)
        self[:] = reversed_items
        self.transport_nodes_and_edges = reversed_items
        self.transport_nodes = list(reversed(self.transport_nodes))
        self.transport_edges = [(e[1], e[0]) for e in reversed(self.transport_edges)]
        self.transport_edge_ids.reverse()

    # ------------------------------------------------------------------
    # Pickle hooks — minimal state to avoid recursion blow-up at scale
    # ------------------------------------------------------------------
    # Default pickling stores both the list contents (transport_nodes_and_edges)
    # AND every __dict__ attribute, which duplicates the same nodes/edges 3-4
    # times per Route. With ~316k Route objects on the China scope this drove
    # pickle's recursion depth past the limit and the C stack past Windows'
    # main-thread bound. Storing only the 4 minimal fields and rebuilding the
    # rest in __setstate__ cuts size ~75% and recursion depth proportionally.

    def __getstate__(self) -> dict:
        return {
            "transport_nodes": self.transport_nodes,
            "transport_edge_ids": self.transport_edge_ids,
            "transport_modes": self.transport_modes,
            "length": self.length,
        }

    def __setstate__(self, state: dict):
        nodes = state["transport_nodes"]
        if len(nodes) == 1:
            tne = [(nodes[0],)]
        else:
            tne = [(nodes[0],)]
            for i in range(len(nodes) - 1):
                tne.append((nodes[i], nodes[i + 1]))
                tne.append((nodes[i + 1],))
        list.__init__(self, tne)
        self.transport_nodes_and_edges = tne
        self.transport_nodes = nodes
        self.transport_edges = [
            (nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)
        ]
        self.transport_edge_ids = state["transport_edge_ids"]
        self.transport_modes = state["transport_modes"]
        self.length = state["length"]
