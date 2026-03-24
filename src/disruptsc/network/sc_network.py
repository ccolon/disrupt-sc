"""ScNetwork — supply chain network as a directed graph."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import networkx as nx
import pandas as pd

if TYPE_CHECKING:
    from disruptsc.network.commercial_link import CommercialLink


def _add_or_append(d: dict, key, value):
    d[key] = d.get(key, 0) + value


class ScNetwork(nx.DiGraph):

    def access_commercial_link(self, edge) -> CommercialLink:
        return self[edge[0]][edge[1]]["object"]

    def calculate_io_matrix(self) -> pd.DataFrame:
        io = {}
        for supplier, buyer, data in self.edges(data=True):
            link: CommercialLink = data["object"]
            if link.category == "domestic_B2C":
                _add_or_append(io, (supplier.sector, "final_demand"), link.order)
            elif link.category == "export":
                _add_or_append(io, (supplier.sector, "export"), link.order)
            elif link.category == "domestic_B2B":
                _add_or_append(io, (supplier.sector, buyer.sector), link.order)
            elif link.category == "import_B2C":
                _add_or_append(io, ("IMP", "final_demand"), link.order)
            elif link.category == "import":
                _add_or_append(io, ("IMP", buyer.sector), link.order)
            elif link.category == "transit":
                pass
            else:
                raise KeyError(f"Unknown link category: {link.category}")
        return pd.Series(io).unstack().fillna(0)

    def generate_edge_list(self) -> pd.DataFrame:
        rows = [
            (s.pid, s.id_str(), s.agent_type if hasattr(s, 'agent_type') else type(s).__name__.lower(), s.od_point,
             t.pid, t.id_str(), t.agent_type if hasattr(t, 'agent_type') else type(t).__name__.lower(), t.od_point)
            for s, t in self.edges()
        ]
        df = pd.DataFrame(rows, columns=[
            "source_id", "source_str_id", "source_type", "source_od_point",
            "target_id", "target_str_id", "target_type", "target_od_point",
        ])
        return df

    def identify_firms_without_clients(self) -> list:
        return [n for n in self.nodes() if self.out_degree(n) == 0 and type(n).__name__ == "Firm"]

    def identify_disconnected_nodes(self, firms: dict, countries: dict, households: dict) -> dict:
        node_pids = {n.pid for n in self}
        result = {}
        for label, agents in [("firms", firms), ("countries", countries), ("households", households)]:
            missing = set(agents.keys()) - node_pids
            if missing:
                result[label] = list(missing)
        return result

    def remove_useless_commercial_links(self) -> int:
        firms_without_clients = self.identify_firms_without_clients()
        logging.info(f"Removing {len(firms_without_clients)} firms without clients")

        for firm in firms_without_clients:
            suppliers = [edge[0] for edge in self.in_edges(firm)]
            for supplier in suppliers:
                self.remove_edge(supplier, firm)
                if hasattr(supplier, "clients") and firm.pid in supplier.clients:
                    del supplier.clients[firm.pid]
                if hasattr(firm, "suppliers") and supplier.pid in firm.suppliers:
                    del firm.suppliers[supplier.pid]
            self.remove_node(firm)

        return len(firms_without_clients)
