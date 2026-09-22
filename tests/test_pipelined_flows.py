"""Pipelined flows (Rhine study, 22 Sep 2026): the share of a link that reaches its buyer by pipeline is
delivered without transport, at the supplier's price, whatever the network does to the rest.

Network (cost per ton for "dry_bulk"): 1 --(river 10)-- 2 --(river 10)-- 3 and a rail leg 1 --(rail 25)-- 3.
The link 1 -> 3 ships 100 (50 t) on the river; a prohibitive modal-switch penalty makes the rail leg a
give-up when the river closes, and a x3 surcharge on edge 2-3 re-prices the river when it is open.
"""
from __future__ import annotations

from types import SimpleNamespace

import networkx as nx

from disruptsc.agents.transport_utils import send_shipment
from disruptsc.init_pipeline.supply_chain import load_pipelined_flows
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams
from disruptsc.run_pipeline.simulate import _collect_routing_summary

CT = "dry_bulk"
TP = TransportParams(switching_costs={"modal_switch": {"default": 0.15, CT: 1000}, "port_switch": 0.05},
                     delivered_price_increase_threshold=5.0)


def _network() -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    for n, (x, y) in {1: (0, 0), 2: (1, 0), 3: (2, 0)}.items():
        tn.add_node(n, id=n, long=x, lat=y, shipments={}, disruption_duration=0, type="road")
    for u, v, cost, mode, eid in [(1, 2, 10, "waterways", 1), (2, 3, 10, "waterways", 2), (1, 3, 25, "railways", 3)]:
        tn.add_edge(u, v, id=eid, type=mode, km=100.0, name=f"e{eid}", shipments={},
                    disruption_duration=0, closed=False, **{f"cost_per_ton_{CT}": float(cost)})
    return tn


def _link(tn: TransportNetwork, share: float) -> CommercialLink:
    route = Route([1, 2, 3], tn, CT)
    link = CommercialLink(pid="L", supplier_id="S", buyer_id="B", product="DEU_B06", product_type="mining",
                          category="domestic_B2B", origin_node=1, destination_node=3, route=route,
                          route_cost_per_ton=tn.compute_route_cost(route, CT), use_transport_network=True,
                          cargo_type=CT, delivery=100.0, delivery_in_tons=50.0, eq_price=1.0, price=1.0)
    link.pipelined_share = share
    return link


def _send(tn, link, calls, price=1.2):
    avail = tn.get_undisrupted_network()
    send_shipment("S", 1, 0.1, link, tn, avail, TP, None, lambda l, r: calls.append((l.realized_delivery, r)),
                  supplier_price=price)


def _edge_tons(tn):
    return sum(s["tons"] for _, _, d in tn.edges(data=True) for s in d["shipments"].values())


def test_pipelined_part_survives_a_closure_and_the_rest_gives_up():
    tn = _network(); link = _link(tn, 0.6); calls = []
    tn.start_edge_disruption(tn[2][3], 1.0, 3)
    _send(tn, link, calls)
    assert abs(link.realized_delivery - 60.0) < 1e-9 and abs(link.delivery - 60.0) < 1e-9
    assert link.pipelined_delivery == 60.0 and link.delivery_offered == 100.0
    assert link.delivery_in_tons == 0.0 and _edge_tons(tn) == 0.0          # nothing moved on the network
    assert abs(link.price - 1.2) < 1e-9 and abs(link.payment - 72.0) < 1e-9   # supplier's price, no surcharge
    dest = tn._node[3]["shipments"]["L"]
    assert abs(dest["quantity"] - 60.0) < 1e-9 and dest["tons"] == 0.0
    assert calls == [(60.0, None)]                                          # stock deducted once, no route


def test_pipelined_part_is_not_surcharged_and_the_price_blends():
    tn = _network(); link = _link(tn, 0.6); calls = []
    tn.start_edge_cost_shock(tn[2][3], 3.0, duration=2)                   # river open, route cost 20 -> 40
    _send(tn, link, calls)
    assert abs(link.realized_delivery - 100.0) < 1e-9
    assert abs(link.delivery_in_tons - 20.0) < 1e-9 and abs(_edge_tons(tn) - 40.0) < 1e-9   # 20 t on two edges
    routed_price = 1.2 * (1 + 0.1 * (40.0 / 20.0 - 1.0))                    # +100 % freight on the routed part
    assert abs(link.price - (0.4 * routed_price + 0.6 * 1.2)) < 1e-9
    assert abs(tn._node[3]["shipments"]["L"]["quantity"] - 100.0) < 1e-9
    assert len(calls) == 1 and calls[0][0] == 100.0 and calls[0][1] is link.route


def test_fully_pipelined_link_never_touches_the_network():
    tn = _network(); link = _link(tn, 1.0); calls = []
    tn.start_edge_disruption(tn[2][3], 1.0, 3)
    _send(tn, link, calls)
    assert link.realized_delivery == 100.0 and link.pipelined_delivery == 100.0
    assert link.delivery_in_tons == 0.0 and _edge_tons(tn) == 0.0 and link.current_route == "main"
    assert link.main_route_realized_delivery == 0.0 and abs(link.price - 1.2) < 1e-9
    assert calls == [(100.0, None)]


def test_zero_share_keeps_the_previous_behaviour():
    tn = _network(); link = _link(tn, 0.0); calls = []
    tn.start_edge_disruption(tn[2][3], 1.0, 3)
    _send(tn, link, calls)
    assert link.realized_delivery == 0.0 and link.pipelined_delivery == 0.0 and calls == []
    assert "L" not in tn._node[3]["shipments"]


def test_routing_summary_reports_the_pipelined_part():
    tn = _network(); link = _link(tn, 0.6)
    tn.start_edge_disruption(tn[2][3], 1.0, 3)
    link.served_order = 100.0
    _send(tn, link, [])
    sc = nx.DiGraph(); sc.add_edge("S", "B", object=link)
    (row,) = _collect_routing_summary(sc, 1)
    assert row["cargo_type"] == CT and row["total_usd"] == 100.0
    assert abs(row["pipelined_usd"] - 60.0) < 1e-9 and row["main_usd"] == 0.0 and abs(row["blocked_usd"] - 40.0) < 1e-9


class _Agent(SimpleNamespace):
    __hash__ = object.__hash__       # a graph node


def test_load_pipelined_flows_marks_products_and_bundle_shares():
    refinery = _Agent(pid="F1", region="DEU", sector="C19")
    plant = _Agent(pid="F2", region="DEU", sector="D")
    household = _Agent(pid="H1", region="DEU")
    links = {
        "crude": CommercialLink(pid="a", product="DEU_B06", category="domestic_B2B"),
        "fuel": CommercialLink(pid="b", product="DEU_C19", category="domestic_B2B"),
        "bundle": CommercialLink(pid="c", product="MEA_imports", category="import"),
        "coal_bundle": CommercialLink(pid="d", product="AFR_imports", category="import"),
        "hh_gas": CommercialLink(pid="e", product="DEU_B06", category="B2C"),
        "hh_bundle": CommercialLink(pid="f", product="MEA_imports", category="B2C"),
    }
    sc = nx.DiGraph()
    sc.add_edge("S1", refinery, object=links["crude"]); sc.add_edge("S2", refinery, object=links["fuel"])
    sc.add_edge("MEA", refinery, object=links["bundle"]); sc.add_edge("AFR", plant, object=links["coal_bundle"])
    sc.add_edge("S1", household, object=links["hh_gas"]); sc.add_edge("MEA", household, object=links["hh_bundle"])
    shares = {("DEU", "C19"): {"MEA": {"B06": 0.88, "G": 0.08, "H49": 0.04}},
              ("DEU", "D"): {"AFR": {"B06": 0.56, "B05": 0.31, "G": 0.13}}}
    assert load_pipelined_flows(sc, {"products": ["B06"]}, shares) == (2, 2)
    got = {k: round(v.pipelined_share, 2) for k, v in links.items()}
    assert got == {"crude": 1.0, "fuel": 0.0, "bundle": 0.88, "coal_bundle": 0.56, "hh_gas": 1.0, "hh_bundle": 0.0}
    # restricted to refineries: the plant's bundle and the household are left on the network
    assert load_pipelined_flows(sc, {"products": ["B06"], "buyer_sectors": ["C19"]}, shares) == (1, 1)
    assert links["coal_bundle"].pipelined_share == 0.0 and links["hh_gas"].pipelined_share == 0.0
    # no rule: every share back to zero (the model as before)
    assert load_pipelined_flows(sc, None, shares) == (0, 0)
    assert all(l.pipelined_share == 0.0 for l in links.values())


def test_pipelined_share_is_not_pickled():
    import pickle
    tn = _network(); link = _link(tn, 0.6); link.pipelined_delivery = 60.0
    back = pickle.loads(pickle.dumps(link))
    assert back.pipelined_share == 0.0 and back.pipelined_delivery == 0.0 and back.product == "DEU_B06"
