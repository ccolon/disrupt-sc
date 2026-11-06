"""KI-53 (6 Nov 2026): every positive delivery reaches its buyer.

Before the fix, a shipment of EPSILON tons (1 g) or less was booked as delivered (the supplier's stock drawn
down, the payment due) but never placed, so the buyer received nothing; and Firm.deliver / Country.deliver
skipped deliveries below EPSILON model units. On the v2 Cambodia scope (daily steps, 20,860 firms) thousands
of inputs were never received and an undisturbed run lost 36 % of national production by day 33.

Network as in test_pipelined_flows: 1 --(river)-- 2 --(river)-- 3, link 1 -> 3.
"""
from __future__ import annotations

import networkx as nx  # noqa: F401  (same fixtures as test_pipelined_flows)

from disruptsc.agents.transport_utils import send_shipment
from disruptsc.config import EPSILON
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams

CT = "dry_bulk"
TP = TransportParams()


def _network() -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    for n, (x, y) in {1: (0, 0), 2: (1, 0), 3: (2, 0)}.items():
        tn.add_node(n, id=n, long=x, lat=y, shipments={}, disruption_duration=0, type="road")
    for u, v, cost, mode, eid in [(1, 2, 10, "waterways", 1), (2, 3, 10, "waterways", 2), (1, 3, 25, "railways", 3)]:
        tn.add_edge(u, v, id=eid, type=mode, km=100.0, name=f"e{eid}", shipments={},
                    disruption_duration=0, closed=False, **{f"cost_per_ton_{CT}": float(cost)})
    return tn


def _link(tn: TransportNetwork, value: float, tons: float) -> CommercialLink:
    route = Route([1, 2, 3], tn, CT)
    return CommercialLink(pid="L", supplier_id="S", buyer_id="B", product="KHM_MCO", product_type="manufacturing",
                          category="domestic_B2B", origin_node=1, destination_node=3, route=route,
                          route_cost_per_ton=tn.compute_route_cost(route, CT), use_transport_network=True,
                          cargo_type=CT, delivery=value, delivery_in_tons=tons, eq_price=1.0, price=1.0)


def _send(tn, link):
    calls = []
    send_shipment("S", 1, 0.1, link, tn, tn.get_undisrupted_network(), TP, None,
                  lambda l, r: calls.append(l.realized_delivery))
    return calls


def _edge_tons(tn):
    return sum(s["tons"] for _, _, d in tn.edges(data=True) for s in d["shipments"].values())


def test_a_shipment_below_one_gram_reaches_the_buyer():
    tn = _network()
    link = _link(tn, value=0.004662, tons=EPSILON / 5)          # firm 27168's KHM_MCO input, Cambodia, USD units
    calls = _send(tn, link)
    assert calls == [0.004662]                                   # booked as delivered once by the supplier ...
    assert abs(tn._node[3]["shipments"]["L"]["quantity"] - 0.004662) < 1e-15   # ... and waiting at the buyer
    assert _edge_tons(tn) == 0.0                                 # no tonnage loaded on the edges


def test_a_normal_shipment_still_moves_on_the_edges():
    tn = _network()
    link = _link(tn, value=100.0, tons=50.0)
    _send(tn, link)
    assert abs(tn._node[3]["shipments"]["L"]["quantity"] - 100.0) < 1e-9
    assert abs(_edge_tons(tn) - 100.0) < 1e-9                    # 50 t on each of the two river edges
