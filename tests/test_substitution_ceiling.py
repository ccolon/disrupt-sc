"""Substitution ceiling on cost shocks and closures: the shocked mode still
carries capacity_factor of a link's tonnage, the substitutes absorb at most
substitution_share of the displaced remainder, the rest is not delivered.
Defaults (1.0 / 1.0) reproduce the legacy all-or-nothing behaviour.

Network (costs per ton for cargo "dry_bulk"):
    A --(river, 10)-- B --(river, 10)-- C      main route A-B-C, cost 20
    A --(rail,  25)------------------ C        alternative,      cost 25
"""

from __future__ import annotations

import pytest

from disruptsc.agents.transport_utils import send_shipment
from disruptsc.params import TransportParams
import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location('test_cost_shock', pathlib.Path(__file__).with_name('test_cost_shock.py'))
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
CT, _link, _network = _m.CT, _m._link, _m._network


def _flows(tn, link_pid):
    return {(u, v): tn[u][v]["shipments"][link_pid]["tons"] for u, v in tn.edges if link_pid in tn[u][v]["shipments"]}


def test_cost_shock_ceiling_splits_delivery_and_flows():
    tn, tp = _network(), TransportParams(delivered_price_increase_threshold=0.5)
    link = _link(tn)
    tn.start_edge_cost_shock(tn[1][2], 3.0, duration=1, capacity_factor=0.4, substitution_share=0.25)
    send_shipment("S", 1, 0.1, link, tn, tn, tp)
    share = 0.4 + 0.25 * 0.6                      # 0.55 delivered
    assert link.realized_delivery == pytest.approx(100.0 * share)
    assert link.delivery_in_tons == pytest.approx(50.0 * share)
    assert link.main_route_realized_delivery == pytest.approx(40.0)
    assert link.alternative_route_realized_delivery == pytest.approx(15.0)
    f = _flows(tn, "L")
    assert f[(1, 2)] == pytest.approx(50.0 * 0.4) and f[(2, 3)] == pytest.approx(50.0 * 0.4)
    assert f[(1, 3)] == pytest.approx(50.0 * 0.15)
    # price: tonnage-weighted cost (40: main at 40 USD/t, 15: rail at 25) vs base 20, + switching share
    weighted = (0.4 * 40 + 0.15 * 25) / 0.55
    rel = (weighted - 20) / 20 + (0.15 / 0.55) * tp.switching_costs["modal_switch"]
    assert link.price == pytest.approx(1 + 0.1 * rel)
    assert link.payment == pytest.approx(link.realized_delivery * link.price)


def test_cost_shock_defaults_are_legacy():
    tn, tp = _network(), TransportParams(price_increase_threshold=2.0)
    link = _link(tn)
    tn.start_edge_cost_shock(tn[1][2], 1.4, duration=1)     # main 24 < alternative 25 -> all on main
    send_shipment("S", 1, 0.1, link, tn, tn, tp)
    assert link.realized_delivery == pytest.approx(100.0) and link.current_route == "main"
    assert _flows(tn, "L")[(1, 2)] == pytest.approx(50.0)


def test_closure_ceiling_delivers_only_the_substitutable_share():
    tn, tp = _network(), TransportParams(delivered_price_increase_threshold=0.5)
    link = _link(tn)
    tn.start_edge_disruption(tn[1][2], 1.0, duration=1)
    tn[1][2]["closure_substitution_share"] = 0.3
    available = tn.get_undisrupted_network()
    send_shipment("S", 1, 0.1, link, tn, available, tp)
    assert link.current_route == "alternative"
    assert link.realized_delivery == pytest.approx(30.0)
    assert _flows(tn, "L")[(1, 3)] == pytest.approx(15.0)
    tn.clear_edge_disruption(tn[1][2])
    assert tn[1][2]["closure_substitution_share"] == 1.0


def test_closure_default_is_full_reroute():
    tn, tp = _network(), TransportParams(delivered_price_increase_threshold=0.5)
    link = _link(tn)
    tn.start_edge_disruption(tn[1][2], 1.0, duration=1)
    send_shipment("S", 1, 0.1, link, tn, tn.get_undisrupted_network(), tp)
    assert link.realized_delivery == pytest.approx(100.0)
