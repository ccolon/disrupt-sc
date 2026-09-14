"""Penalty-aware alternative route search and the line-haul modal-switch rule (Rhine study, 14 Sep 2026).

Network (cost per ton for cargo "dry_bulk", km in brackets):

    1 --(river 10, 300 km)-- 2 --(river 10, 300 km)-- 3 --(road 5, 20 km)-- 5    normal route 1-2-3-5, cost 25
    2 --(road 20, 200 km)-- 4 --(road 5, 20 km)-- 5                              river+road detour, cost 35 from 1
    1 --(rail 25, 500 km)-- 3                                                    rail leg, cost 30 from 1
    2 --(canal 12, 400 km)-- 6 --(canal 12, 400 km)-- 3                          all-water detour, cost 39 from 1

When the river edge 2-3 closes, the cheapest path by transport cost alone is the rail leg. The line-haul
rule counts the rail leg and the 220 km road detour as modal switches (line-haul km on modes that
served no line haul in the normal route) but not the canal detour (more km on the water). A bulk
shipper with a prohibitive penalty therefore takes the canal when it exists and gives up otherwise.
"""
from __future__ import annotations

from disruptsc.agents.transport_utils import discover_route, send_shipment
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams

CT = "dry_bulk"
PROHIBITIVE = {"modal_switch": {"default": 0.15, CT: 1000}, "port_switch": 0.05}
CHEAP = {"modal_switch": {"default": 0.15}, "port_switch": 0.05}


def _network(with_canal: bool = False) -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    for n, (x, y) in {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (1.5, 1), 5: (3, 0), 6: (1.5, -1)}.items():
        tn.add_node(n, id=n, long=x, lat=y, shipments={}, disruption_duration=0, type="road")
    edges = [(1, 2, 10, "waterways", 1, 300), (2, 3, 10, "waterways", 2, 300), (3, 5, 5, "roads", 3, 20),
             (2, 4, 20, "roads", 4, 200), (4, 5, 5, "roads", 5, 20), (1, 3, 25, "railways", 6, 500)]
    if with_canal:
        edges += [(2, 6, 12, "waterways", 7, 400), (6, 3, 12, "waterways", 8, 400)]
    for u, v, cost, mode, eid, km in edges:
        tn.add_edge(u, v, id=eid, type=mode, km=float(km), name=f"e{eid}", shipments={},
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


def test_line_haul_rule_classifies_the_detours():
    tn = _network(with_canal=True); link = _link(tn)
    road_detour = Route([1, 2, 4, 5], tn, CT)           # 220 km by road where the normal route had 20
    rail = Route([1, 3, 5], tn, CT)                      # 500 km by rail
    canal = Route([1, 2, 6, 3, 5], tn, CT)               # more km on the water, same access leg
    longer_access = Route([1, 2, 3, 5], tn, CT)
    assert CommercialLink._routes_have_modal_switch(link.route, road_detour, tn, PROHIBITIVE)
    assert CommercialLink._routes_have_modal_switch(link.route, rail, tn, PROHIBITIVE)
    assert not CommercialLink._routes_have_modal_switch(link.route, canal, tn, PROHIBITIVE)
    assert not CommercialLink._routes_have_modal_switch(link.route, longer_access, tn, PROHIBITIVE)
    tn[3][5]["km"] = 60.0                                # a 40 km longer road access leg stays within the allowance
    assert not CommercialLink._routes_have_modal_switch(link.route, Route([1, 2, 3, 5], tn, CT), tn, PROHIBITIVE)


def test_free_search_takes_the_rail_leg():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    route = discover_route(1, link, tn, avail, False, False)          # no switching costs: legacy behaviour
    assert _modes(route, tn) == {"railways", "roads"} and tn.compute_route_cost(route, CT) == 30.0


def test_bulk_gives_up_when_every_detour_is_a_modal_switch():
    tn = _network(); link = _link(tn); avail = _closed_river(tn)
    tp = TransportParams(switching_costs=PROHIBITIVE, delivered_price_increase_threshold=5.0)
    send_shipment("S", 1, 0.1, link, tn, avail, tp)
    assert link.realized_delivery == 0.0                                # rail leg and road detour both prohibitive


def test_bulk_takes_the_water_detour_when_it_exists():
    tn = _network(with_canal=True); link = _link(tn); avail = _closed_river(tn)
    tp = TransportParams(switching_costs=PROHIBITIVE, delivered_price_increase_threshold=5.0)
    send_shipment("S", 1, 0.1, link, tn, avail, tp)
    assert link.realized_delivery == 100.0 and link.current_route == "alternative"
    assert _modes(link.alternative_route, tn) == {"waterways", "roads"} and link.alternative_route.length == 1120.0
    assert abs(link.price - (1 + 0.1 * (39.0 / 25.0 - 1.0))) < 1e-9       # +56 % freight, no penalty


def test_cheap_penalty_takes_the_rail_leg_when_it_is_cheaper_all_in():
    tn = _network(with_canal=True); link = _link(tn); avail = _closed_river(tn)
    route = discover_route(1, link, tn, avail, False, False, switching_costs=CHEAP)   # 30 + 0.15 x 25 = 33.75 < 39
    assert _modes(route, tn) == {"railways", "roads"}


def test_cached_same_mode_search_is_invalidated_with_the_others():
    tn = _network(with_canal=True); link = _link(tn); avail = _closed_river(tn)
    discover_route(1, link, tn, avail, False, True, switching_costs=PROHIBITIVE)
    same_keys = [k for k in tn.shortest_path_library if str(k).startswith("alternative_same_modes")]
    assert same_keys and tn.shortest_path_library[same_keys[0]][CT]
    tn.invalidate_alternative_routes()
    assert not tn.shortest_path_library[same_keys[0]][CT]
    assert not tn.shortest_path_library["alternative"][CT]
