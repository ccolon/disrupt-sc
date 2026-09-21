"""How the capacity gate scales: synthetic grid networks, thousands of shippers,
a few capacitated edges (docs/architecture/transport-capacity.md, phase 4).

Cost claim of the design: the gate pass is linear in the shipments crossing the
capacitated edges, route searches run only for the cut shares (one per distinct
origin, destination and saturated set, cached), and the loop ends within
|C| + 1 rounds. This script measures it: an n x n road grid, M shippers on
seeded random OD pairs (1 t each, cheapest path), K capacitated edges chosen
among the busiest and set to half their load, then the placement time
(send_shipment for every shipper) against the gate time.

    python scripts/capacity_gate_scaling.py [--sizes 10,20,30] [--shippers 2000,8000] [--capacitated 2,8,32]
"""

from __future__ import annotations

import argparse
import logging
import math
import random
import sys
import time
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from disruptsc.agents.transport_utils import send_shipment  # noqa: E402
from disruptsc.init_pipeline.routing import shortest_paths_for  # noqa: E402
from disruptsc.network.commercial_link import CommercialLink  # noqa: E402
from disruptsc.network.route import Route  # noqa: E402
from disruptsc.network.transport_network import TransportNetwork  # noqa: E402
from disruptsc.params import TransportParams  # noqa: E402
from disruptsc.run_pipeline.capacity_gate import run_capacity_gate  # noqa: E402

logging.basicConfig(level=logging.ERROR)
CT = "any"


class _Firm:
    def __init__(self, pid):
        self.pid, self.product_stock = pid, 0.0


def grid_network(n: int, rng: random.Random) -> TransportNetwork:
    g = nx.grid_2d_graph(n, n)
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    ids = {node: i for i, node in enumerate(g.nodes)}
    for node, i in ids.items():
        tn.add_node(i, id=i, long=float(node[0]), lat=float(node[1]), shipments={}, disruption_duration=0, type="road")
    for eid, (a, b) in enumerate(g.edges):
        km = 10.0 * rng.uniform(0.8, 1.2)
        tn.add_edge(ids[a], ids[b], id=eid, type="roads", km=km, name=f"e{eid}", shipments={},
                    disruption_duration=0, closed=False, **{f"cost_per_ton_{CT}": km * 0.05})
    return tn


def run_case(n: int, m: int, k: int, seed: int = 0) -> dict:
    rng = random.Random(seed)
    tn = grid_network(n, rng)
    nodes = list(tn.nodes)
    pairs = [(rng.choice(nodes), rng.choice(nodes)) for _ in range(m)]
    pairs = [(o, d) for o, d in pairs if o != d]
    dest_by_source: dict = {}
    for o, d in pairs:
        dest_by_source.setdefault(o, set()).add(d)
    paths = shortest_paths_for(tn, f"cost_per_ton_{CT}", dest_by_source)
    firms, links = {}, []
    for i, (o, d) in enumerate(pairs):
        route = Route(paths[(o, d)], tn, CT)
        firms[f"F{i}"] = _Firm(f"F{i}")
        links.append(CommercialLink(pid=f"s{i}", supplier_id=f"F{i}", buyer_id="b", product="P",
                                    product_type="manufacturing", category="domestic_B2B", origin_node=o,
                                    destination_node=d, route=route, route_cost_per_ton=tn.compute_route_cost(route, CT),
                                    use_transport_network=True, cargo_type=CT, delivery=1.0, delivery_in_tons=1.0,
                                    eq_price=1.0, price=1.0))
    # baseline load per edge, capacities on the k busiest at half their load
    load: dict = {}
    for link in links:
        for u, v in link.route.transport_edges:
            key = (min(u, v), max(u, v))
            load[key] = load.get(key, 0.0) + 1.0
    busiest = sorted(load, key=load.get, reverse=True)[:k]
    for u, v in busiest:
        tn[u][v]["capacity"] = load[(u, v)] / 2.0
    tn.capture_base_capacity_state()
    tp = TransportParams(price_increase_threshold=2.0, use_route_cache=True)

    def after(link, route):
        firms[link.supplier_id].product_stock -= link.realized_delivery

    t0 = time.time()
    for link in links:
        send_shipment(link.supplier_id, link.origin_node, 0.1, link, tn, tn, tp, after_shipment=after)
    t_place = time.time() - t0
    crossing = sum(1 for link in links if any((min(u, v), max(u, v)) in set(busiest) for u, v in link.route.transport_edges))
    t0 = time.time()
    result = run_capacity_gate(tn, tn, firms, {}, tp, 0)
    t_gate = time.time() - t0
    return dict(nodes=tn.number_of_nodes(), edges=tn.number_of_edges(), shippers=len(links), capacitated=k,
                crossing=crossing, rounds=result["rounds"], saturated=result["n_saturated"],
                cut_t=result["cut_tons"], resent_t=result["resent_tons"], blocked_t=result["blocked_tons"],
                placement_s=t_place, gate_s=t_gate)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="10,20,30")
    ap.add_argument("--shippers", default="2000,8000")
    ap.add_argument("--capacitated", default="2,8,32")
    args = ap.parse_args()
    header = ("nodes", "edges", "shippers", "capacitated", "crossing", "rounds", "saturated",
              "cut_t", "resent_t", "blocked_t", "placement_s", "gate_s")
    print(" ".join(f"{h:>11}" for h in header))
    for n in (int(x) for x in args.sizes.split(",")):
        for m in (int(x) for x in args.shippers.split(",")):
            for k in (int(x) for x in args.capacitated.split(",")):
                r = run_case(n, m, k)
                print(" ".join(f"{r[h]:>11.2f}" if isinstance(r[h], float) else f"{r[h]:>11}" for h in header))


if __name__ == "__main__":
    main()
