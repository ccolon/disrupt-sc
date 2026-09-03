"""Transport cost shocks: an edge stays open but its cost labels are
multiplied; buyers pay the surcharge, reroute where cheaper, or give up
beyond price_increase_threshold. No capacity routing involved.

Network (costs per ton for cargo "dry_bulk"):

    A --(river, 10)-- B --(river, 10)-- C          main route A-B-C, cost 20
    A --(rail,  25)------------------ C            alternative,      cost 25
"""

from __future__ import annotations

import networkx as nx
import pytest

from disruptsc.agents.transport_utils import send_shipment
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams
from disruptsc.run_pipeline.disruption import TransportCostShock, parse_disruptions

CT = "dry_bulk"


def _network() -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    for n, (x, y) in {1: (0, 0), 2: (1, 0), 3: (2, 0)}.items():
        tn.add_node(n, id=n, long=x, lat=y, shipments={}, disruption_duration=0, type="road")
    edges = [(1, 2, 10, "waterways", 1), (2, 3, 10, "waterways", 2), (1, 3, 25, "railways", 3)]
    for u, v, cost, mode, eid in edges:
        tn.add_edge(u, v, id=eid, type=mode, km=100.0, name=f"e{eid}", shipments={},
                    disruption_duration=0, closed=False, overused=False,
                    **{f"cost_per_ton_{CT}": float(cost), f"cost_per_ton_with_capacity_{CT}": float(cost),
                       f"current_load_{CT}": 0})
    return tn


def _link(tn: TransportNetwork) -> CommercialLink:
    route = Route([1, 2, 3], tn, CT)
    link = CommercialLink(pid="L", supplier_id="S", buyer_id="B", product="P", product_type="mining",
                          category="domestic_B2B", origin_node=1, destination_node=3, route=route,
                          route_cost_per_ton=tn.compute_route_cost(route, CT), use_transport_network=True,
                          cargo_type=CT, delivery=100.0, delivery_in_tons=50.0, eq_price=1.0, price=1.0,
                          route_plan=[(route, 1.0)])
    return link


def _send(tn, link, tp, transport_share=0.1):
    send_shipment("S", 1, transport_share, link, tn, tn, tp)


def test_shock_state_machine_restores_base_costs():
    tn = _network()
    e = tn[1][2]
    tn.start_edge_cost_shock(e, 3.0, duration=2)
    assert e[f"cost_per_ton_{CT}"] == 30.0 and e["cost_shock_duration"] == 2
    tn.start_edge_cost_shock(e, 4.0, duration=2)      # overlapping shock does not compound
    assert e[f"cost_per_ton_{CT}"] == 40.0
    tn.update_road_disruption_state()
    assert e["cost_shock_duration"] == 1 and e[f"cost_per_ton_{CT}"] == 40.0
    tn.update_road_disruption_state()
    assert e["cost_shock_duration"] == 0 and e[f"cost_per_ton_{CT}"] == 10.0
    tn.start_edge_cost_shock(e, {CT: 2.0, "default": 1.0}, duration=float("inf"))
    assert e[f"cost_per_ton_{CT}"] == 20.0
    tn.reinitialize_flows_and_disruptions()            # reset between runs
    assert e[f"cost_per_ton_{CT}"] == 10.0 and e["cost_shock_duration"] == 0


def test_moderate_shock_is_paid_on_the_main_route():
    tn, tp = _network(), TransportParams(price_increase_threshold=2.0)
    link = _link(tn)
    tn.start_edge_cost_shock(tn[1][2], 1.4, duration=1)   # main 20 -> 24, alternative 25
    _send(tn, link, tp)
    assert link.current_route == "main"
    assert link.realized_delivery == pytest.approx(100.0)
    assert link.price == pytest.approx(1.0 * (1 + 0.1 * (24 - 20) / 20))   # pass-through
    assert link.main_route_realized_delivery == pytest.approx(100.0)


def test_large_shock_reroutes_when_the_alternative_is_cheaper():
    tn, tp = _network(), TransportParams(price_increase_threshold=2.0)
    link = _link(tn)
    tn.start_edge_cost_shock(tn[1][2], 3.0, duration=1)   # main 20 -> 40, alternative 25
    _send(tn, link, tp)
    assert link.current_route == "alternative"
    assert link.alternative_route.transport_nodes == [1, 3]
    rel = (25 - 20) / 20 + tp.switching_costs["modal_switch"]      # rail instead of river
    assert link.price == pytest.approx(1.0 * (1 + 0.1 * rel))
    assert link.realized_delivery == pytest.approx(100.0)


def test_extreme_shock_beyond_threshold_blocks_delivery():
    tn, tp = _network(), TransportParams(price_increase_threshold=1.2)
    link = _link(tn)
    tn.start_edge_cost_shock(tn[1][2], 3.0, duration=1)   # cheapest option 25 = +25% + 15% switch > 20%
    _send(tn, link, tp)
    assert link.realized_delivery == 0.0 and link.delivery == 0.0


def test_no_shock_keeps_the_previous_behaviour():
    tn, tp = _network(), TransportParams()
    link = _link(tn)
    _send(tn, link, tp)
    assert link.current_route == "main" and link.price == 1.0 and link.realized_delivery == 100.0


def test_parse_transport_cost_shock():
    import geopandas as gpd
    from shapely.geometry import LineString
    edges = gpd.GeoDataFrame({"id": [1, 2, 3], "name": ["rhine_a", "rhine_b", "rail"],
                              "disruption": ["rhine;a", "rhine;b", None]},
                             geometry=[LineString([(0, 0), (1, 0)])] * 3)
    ds = parse_disruptions([{"type": "transport_cost_shock", "attribute": "name",
                             "values": ["rhine_a"], "cost_multiplier": 4.5,
                             "start_time": 3, "duration": 1}], edges, None, {}, "mUSD")
    assert len(ds) == 1 and isinstance(ds[0], TransportCostShock)
    assert ds[0].description == {1: 4.5} and ds[0].start_time == 3 and ds[0].duration == 1
    ds = parse_disruptions([{"type": "transport_cost_shock", "attribute": "disruption",
                             "values": ["rhine"], "cost_multiplier": {CT: 3.0, "default": 1.5}}],
                           edges, None, {}, "mUSD")
    assert set(ds[0].description) == {1, 2}
    with pytest.raises(ValueError):
        parse_disruptions([{"type": "transport_cost_shock", "attribute": "name", "values": ["rhine_a"]}],
                          edges, None, {}, "mUSD")
