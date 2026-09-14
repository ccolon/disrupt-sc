"""Penalty-aware alternative route search (Rhine study, 14 Sep 2026).

Network (costs per ton for cargo "dry_bulk"):

    1 --(river, 10)-- 2 --(river, 10)-- 3 --(road, 5)-- 5     normal route 1-2-3-5, modes {river, road}, cost 25
    2 --(road, 20)-- 4 --(road, 5)-- 5                         detour on the shipper's own modes, cost 35 from 1
    1 --(rail, 25)-- 3                                         rail leg: cheaper (30 from 1) but a NEW mode

When the river edge 2-3 closes, the cheapest path by transport cost alone is the rail leg. A shipper
whose cargo cannot switch modes (prohibitive penalty) used to be sent to it and then rejected by the
give-up rule, while the river+road detour would have carried the goods. The penalty-aware search
compares the candidates including the switching penalty.
"""
from __future__ import annotations

import networkx as nx

from disruptsc.agents.transport_utils import discover_route, send_shipment
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams

CT = "dry_bulk"


def _network() -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    for n, (x, y) in {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (1.5, 1), 5: (3, 0)}.items():
        tn.add_node(n, id=n, long=x, lat=y, shipments={}, disruption_duration=0, type="road")
    edges = [(1, 2, 10, "waterways", 1), (2, 3, 10, "waterways", 2), (3, 5, 5, "roads", 3),
             (2, 4, 20, "roads", 4), (4, 5, 5, "roads", 5), (1, 3, 25, "railways", 6)]
    for u, v, cost, mode, eid in edges:
        tn.add_edge(u, v, id=eid, type=mode, km=100.0, name=f"e{eid}", shipments={},
                    disruption_duration=0, closed=False, overused=False,
                    **{f"cost_per_ton_{CT}": float(cost), f"cost_per_ton_with_capacity_{CT}": float(cost),
                       f"current_load_{CT}": 0})
    return tn


def _link(tn: TransportNetwork) -> CommercialLink:
    route = Route([1, 2, 3, 5], tn, CT)
    return CommercialLink(pid="L", supplier_id="S", buyer_id="B", product="P", product_type="mining",
                          category="domestic_B2B", origin_node=1, destination_node=5, route=route,
                          route_cost_per_ton=tn.compute_route_cost(route, CT), use_transport_network=True,
                          cargo_type=CT, delivery=100.0, delivery_in_tons=50.0, eq_price=1.0, price=1.0,
                          route_plan=[(route, 1.0)])


def _closed_river(tn: TransportNetwork) -> TransportNetwork:
    tn.start_edge_disruption(tn[2][3], 1.0, 3)
    return tn.get_undisrupted_network()


def _modes(route: Route, tn: TransportNetwork) -> set:
    return {tn[u][v]["type"] for u, v in route.transport_edges}


def test_free_search_takes_the_rail_leg():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    route = discover_route(1, link, tn, avail, False, False)          # no switching costs: legacy behaviour
    assert _modes(route, tn) == {"railways", "roads"} and tn.compute_route_cost(route, CT) == 30.0


def test_prohibitive_penalty_prefers_the_same_mode_detour():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    costs = {"modal_switch": {"default": 0.15, CT: 1000}, "port_switch": 0.05}
    route = discover_route(1, link, tn, avail, False, False, switching_costs=costs)
    assert _modes(route, tn) == {"waterways", "roads"} and tn.compute_route_cost(route, CT) == 35.0


def test_cheap_penalty_takes_the_rail_leg_when_it_is_cheaper_all_in():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    costs = {"modal_switch": {"default": 0.15}, "port_switch": 0.05}   # 30 + 0.15 x 25 = 33.75 < 35
    route = discover_route(1, link, tn, avail, False, False, switching_costs=costs)
    assert _modes(route, tn) == {"railways", "roads"}


def test_bulk_is_delivered_on_the_detour_when_the_river_closes():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    tp = TransportParams(switching_costs={"modal_switch": {"default": 0.15, CT: 1000}, "port_switch": 0.05},
                         delivered_price_increase_threshold=5.0)
    send_shipment("S", 1, 0.1, link, tn, avail, tp)
    assert link.realized_delivery == 100.0 and link.current_route == "alternative"
    assert _modes(link.alternative_route, tn) == {"waterways", "roads"}
    assert abs(link.price - 1.0 * (1 + 0.1 * (35.0 / 25.0 - 1.0))) < 1e-9   # +40 % freight, no penalty


def test_dropping_a_mode_is_not_a_switch():
    tn = _network(); link = _link(tn)
    road_only = Route([2, 4, 5], tn, CT)                                 # subset of the normal route's modes
    assert not CommercialLink._routes_have_modal_switch(link.route, road_only)
    rail = Route([1, 3, 5], tn, CT)
    assert CommercialLink._routes_have_modal_switch(link.route, rail)


def test_cached_same_mode_search_is_invalidated_with_the_others():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    costs = {"modal_switch": {"default": 0.15, CT: 1000}, "port_switch": 0.05}
    discover_route(1, link, tn, avail, False, True, switching_costs=costs)
    assert tn.shortest_path_library["alternative_same_modes"][CT]
    tn.invalidate_alternative_routes()
    assert not tn.shortest_path_library["alternative_same_modes"][CT]
    assert not tn.shortest_path_library["alternative"][CT]
