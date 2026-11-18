"""Per-cargo capacity_reduction (MC3, Hormuz 2026, 18 Nov 2026).

A Strait shock does not hit every cargo alike, so ``transport_disruption`` takes
``capacity_reduction`` as a number (unchanged behaviour) or as
``{cargo_type: fraction, "default": fraction}``: each ``capacity_<cargo>`` of the
edge is scaled by its own factor and the within-step gate rations each cargo at
its reduced capacity. Synthetic network (every edge 100 km of road):

    1 --A(10)-- 4          A carries the per-cargo capacities
    1 --(30)-- 3 --(30)-- 4   the dear detour
"""

from __future__ import annotations

import copy
import logging
import math

import pandas as pd
import pytest

from disruptsc.agents.transport_utils import send_shipment
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams
from disruptsc.run_pipeline.capacity_gate import run_capacity_gate
from disruptsc.run_pipeline.disruption import TransportCostShock, parse_disruptions
from disruptsc.run_pipeline.fingerprint import build_fingerprint, fingerprint_hash

BULK, BOX = "dry_bulk", "container"


class _Firm:
    def __init__(self, pid, stock=0.0):
        self.pid, self.product_stock = pid, stock


def _network(caps: dict, cargo_types=(BULK, BOX)) -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = list(cargo_types)
    for n in (1, 3, 4):
        tn.add_node(n, id=n, long=float(n), lat=0.0, shipments={}, disruption_duration=0, type="road")
    for u, v, cost, eid, name in [(1, 4, 10, 1, "A"), (1, 3, 30, 4, "e13"), (3, 4, 30, 5, "e34")]:
        tn.add_edge(u, v, id=eid, type="roads", km=100.0, name=name, shipments={}, disruption_duration=0,
                    closed=False, **{f"cost_per_ton_{ct}": float(cost) for ct in cargo_types})
    for name, cap in caps.items():
        u, v = next((u, v) for u, v in tn.edges if tn[u][v]["name"] == name)
        if isinstance(cap, dict):
            for ct, val in cap.items():
                tn[u][v][f"capacity_{ct}"] = float(val)
        else:
            tn[u][v]["capacity"] = float(cap)
    tn.capture_base_capacity_state()
    return tn


_EDGES = pd.DataFrame({"id": [1, 4, 5], "name": ["A", "e13", "e34"]})


def _shock(reduction, duration=2, shape="threshold"):
    return parse_disruptions([{"type": "transport_disruption", "attribute": "name", "values": ["A"],
                               "capacity_reduction": reduction, "start_time": 1, "duration": duration,
                               "recovery_shape": shape}], _EDGES, None, {}, "mUSD", "week")[0]


def _edge(tn, name="A"):
    return next(tn[u][v] for u, v in tn.edges if tn[u][v]["name"] == name)


def _link(tn, pid, supplier, tons, cargo):
    route = Route([1, 4], tn, cargo)
    return CommercialLink(pid=pid, supplier_id=supplier, buyer_id="buyer", product="P", product_type="mining",
                          category="domestic_B2B", origin_node=1, destination_node=4, route=route,
                          route_cost_per_ton=tn.compute_route_cost(route, cargo), use_transport_network=True,
                          cargo_type=cargo, delivery=float(tons), delivery_in_tons=float(tons), eq_price=1.0, price=1.0)


def _ship(tn, tp, link, firms):
    send_shipment(link.supplier_id, link.origin_node, 0.1, link, tn, tn, tp,
                  after_shipment=lambda l, r: setattr(firms[l.supplier_id], "product_stock",
                                                      firms[l.supplier_id].product_stock - l.realized_delivery))


def _tons_by_cargo(edge):
    out = {}
    for r in edge["shipments"].values():
        out[r["cargo_type"]] = out.get(r["cargo_type"], 0.0) + r["tons"]
    return {k: round(v, 9) for k, v in out.items()}


# ----------------------------------------------------------------------
# accept: a two-cargo edge capped per cargo
# ----------------------------------------------------------------------

def test_two_cargo_edge_is_capped_per_cargo_by_the_gate():
    tn = _network({"A": {BULK: 100.0, BOX: 200.0}})
    _shock({BULK: 0.5, BOX: 0.75}).implement(tn)
    a = _edge(tn)
    assert a["capacity_dry_bulk"] == pytest.approx(50.0) and a["capacity_container"] == pytest.approx(50.0)
    assert a["base_capacity_dry_bulk"] == 100.0 and a["base_capacity_container"] == 200.0
    assert not a["closed"]

    # 80 t of bulk and 120 t of containers on A; the cut shares face the cost-60 detour
    # (+500 %) and give up under a freight-bill threshold of 2: they stay in stock
    tp = TransportParams(price_increase_threshold=2.0)
    firms = {"FB": _Firm("FB", 80.0), "FC": _Firm("FC", 120.0)}
    bulk, box = _link(tn, "b", "FB", 80, BULK), _link(tn, "c", "FC", 120, BOX)
    _ship(tn, tp, bulk, firms); _ship(tn, tp, box, firms)
    run_capacity_gate(tn, tn, firms, {}, tp, 1)
    assert _tons_by_cargo(a) == {BULK: 50.0, BOX: 50.0}
    assert bulk.realized_delivery == pytest.approx(50.0) and bulk.capacity_blocked == pytest.approx(30.0)
    assert box.realized_delivery == pytest.approx(50.0) and box.capacity_blocked == pytest.approx(70.0)
    assert firms["FB"].product_stock == pytest.approx(30.0) and firms["FC"].product_stock == pytest.approx(70.0)


def test_a_cargo_not_listed_takes_default_and_without_default_is_untouched():
    tn = _network({"A": {BULK: 100.0, BOX: 200.0}})
    _shock({BOX: 0.5, "default": 0.25}).implement(tn)
    assert _edge(tn)["capacity_dry_bulk"] == pytest.approx(75.0)
    assert _edge(tn)["capacity_container"] == pytest.approx(100.0)
    tn = _network({"A": {BULK: 100.0, BOX: 200.0}})
    _shock({BOX: 0.5}).implement(tn)
    assert _edge(tn)["capacity_dry_bulk"] == 100.0 and _edge(tn)["capacity_container"] == pytest.approx(100.0)


def test_each_cargo_recovers_on_the_same_curve_and_is_restored_exactly():
    tn = _network({"A": {BULK: 100.0, BOX: 200.0}})
    _shock({BULK: 0.5, BOX: 1.0}, duration=4, shape="linear").implement(tn)
    a = _edge(tn)
    assert a["capacity_container"] == 0.0 and not a["closed"]        # bulk still moves: not closed
    tn.update_road_disruption_state()                                 # 1 of 4 steps: 25 % recovered
    assert a["capacity_dry_bulk"] == pytest.approx(100.0 * (1 - 0.5 * 0.75))
    assert a["capacity_container"] == pytest.approx(200.0 * (1 - 1.0 * 0.75))
    for _ in range(3):
        tn.update_road_disruption_state()
    assert a["capacity_dry_bulk"] == 100.0 and a["capacity_container"] == 200.0
    assert a["disruption_initial_reduction"] == 0.0 and not a["closed"]


# ----------------------------------------------------------------------
# accept: a scalar gives the results of before
# ----------------------------------------------------------------------

@pytest.mark.parametrize("caps", [{"A": 100.0}, {"A": {BULK: 100.0, BOX: 200.0}}, {}])
@pytest.mark.parametrize("r", [0.0, 0.4, 1.0])
def test_scalar_and_uniform_dict_give_the_same_edge_state(caps, r):
    keys = ("capacity", "capacity_dry_bulk", "capacity_container", "closed")
    tn_s, tn_d = _network(caps), _network(caps)
    _shock(r, duration=3, shape="linear").implement(tn_s)
    _shock({"default": r}, duration=3, shape="linear").implement(tn_d)
    for _ in range(4):
        assert {k: _edge(tn_s).get(k) for k in keys} == {k: _edge(tn_d).get(k) for k in keys}
        tn_s.update_road_disruption_state(); tn_d.update_road_disruption_state()


def test_a_scalar_is_parsed_untouched():
    assert _shock(0.4).description == {1: 0.4}
    assert _shock(1).description == {1: 1}


# ----------------------------------------------------------------------
# shared capacity, uncapacitated edges, closures, validation
# ----------------------------------------------------------------------

def test_shared_capacity_takes_a_uniform_cut_and_refuses_a_split_one():
    tn = _network({"A": 300.0})
    _shock({BULK: 0.5, BOX: 0.5}).implement(tn)
    assert _edge(tn)["capacity"] == pytest.approx(150.0)
    tn = _network({"A": 300.0})
    with pytest.raises(ValueError, match="per-cargo capacities"):
        _shock({BULK: 0.5, BOX: 0.9}).implement(tn)


def test_shared_capacity_ignores_a_cargo_barred_from_the_edge():
    # containers may not use A (no cost label, as under cargo_mode_eligibility): only bulk counts
    tn = _network({"A": 300.0})
    del _edge(tn)["cost_per_ton_container"]
    _shock({BULK: 0.5, BOX: 0.0}).implement(tn)
    assert _edge(tn)["capacity"] == pytest.approx(150.0)
    tn = _network({}); del _edge(tn)["cost_per_ton_container"]
    _shock({BULK: 1.0}).implement(tn)
    assert _edge(tn)["closed"]                      # every cargo that may use it lost 100 %


def test_closed_only_when_every_cargo_is_cut_in_full(caplog):
    tn = _network({})
    _shock({BULK: 1.0, BOX: 1.0}).implement(tn)
    assert _edge(tn)["closed"]
    assert 1 not in [tn[u][v]["id"] for u, v in tn.get_undisrupted_network().edges]
    tn = _network({})
    with caplog.at_level(logging.WARNING):
        _shock({BULK: 1.0, BOX: 0.5}).implement(tn)
    assert not _edge(tn)["closed"]
    assert "cannot bind" in caplog.text and "container" in caplog.text and "dry_bulk" in caplog.text


def test_per_cargo_edge_warns_only_for_the_cargo_without_its_own_capacity(caplog):
    tn = _network({"A": {BULK: 100.0}})
    with caplog.at_level(logging.WARNING):
        _shock({BULK: 0.5, BOX: 0.5}).implement(tn)
    assert _edge(tn)["capacity_dry_bulk"] == pytest.approx(50.0)
    assert "the container cut cannot bind" in caplog.text and "dry_bulk cut" not in caplog.text


def test_invalid_dicts_raise():
    with pytest.raises(ValueError, match=r"in \[0, 1\]"):
        _shock({BULK: 1.5})
    with pytest.raises(ValueError, match="empty"):
        _shock({})
    with pytest.raises(ValueError, match="unknown cargo type"):
        _shock({"containers": 0.5}).implement(_network({"A": {BULK: 100.0}}))


def test_probability_variant_parses_the_dict():
    import numpy as np
    np.random.seed(0)
    ds = parse_disruptions([{"type": "transport_disruption_probability", "attribute": "name", "values": ["A"],
                             "capacity_reduction": {BULK: 0.5}, "scenario_duration": 20,
                             "probability_duration_pairs": [[0.5, 2]]}], _EDGES, None, {}, "mUSD", "week")
    assert ds and all(d.description == {1: {BULK: 0.5}} for d in ds)


# ----------------------------------------------------------------------
# accept: the fingerprint records the dict
# ----------------------------------------------------------------------

def test_run_fingerprint_records_the_dict_and_criticality_leaves_it_out():
    base = {"scope": "X", "seed": 1, "disruptions": [
        {"type": "transport_disruption", "attribute": "name", "values": ["A"],
         "capacity_reduction": {BULK: 0.5, "default": 0.2}, "start_time": 1, "duration": 2}]}
    fp = build_fingerprint(base)
    assert fp["config"]["disruptions"][0]["capacity_reduction"] == {BULK: 0.5, "default": 0.2}
    other = copy.deepcopy(base)
    other["disruptions"][0]["capacity_reduction"][BULK] = 0.6
    assert fingerprint_hash(build_fingerprint(other)) != fingerprint_hash(fp)
    crit = build_fingerprint(base, criticality_duration=4)
    assert "disruptions" not in crit["config"]
    assert fingerprint_hash(build_fingerprint(other, criticality_duration=4)) == fingerprint_hash(crit)


# ----------------------------------------------------------------------
# Testkistan: a per-cargo cut inside the time step keeps the ledgers
# ----------------------------------------------------------------------

def test_testkistan_per_cargo_cut_gates_one_cargo_and_keeps_the_ledgers():
    from disruptsc.build import build_agents, build_common
    from disruptsc.config import build_params, load_config
    from disruptsc.init_pipeline.routing import setup_logistic_routes
    from disruptsc.run_pipeline.simulate import _run_one_time_step

    cfg = load_config("Testkistan")
    cfg["export_files"] = False
    cfg["capacity_constraint"] = True
    cfg["transport_capacity_overrides"] = {"Main Road North": {BOX: 1e9, BULK: 1e9}}   # slack, set below
    tp, sp, ap, lp = build_params(cfg)
    common = build_common(cfg, tp, sp, ap, lp)
    sc, firms, hh, countries = build_agents(common, ap, sp, tp, seed=0)
    tn = common["tn"]
    setup_logistic_routes(sc, tn, firms, countries, tp)
    trunk = [tn[u][v] for u, v in tn.edges if tn[u][v]["name"] == "Main Road North"]
    ids = {e["id"] for e in trunk}

    def trunk_tons(flow):   # per edge of the trunk, per cargo (the step's flows, read before the reset)
        return [{ct: row.get(f"tons_{ct}", 0.0) for ct in (BOX, BULK)} for row in flow if row["id"] in ids]

    flow, _, _ = _run_one_time_step(0, sc, tn, tn, firms, hh, countries, tp, sp, disruptions=[])
    load = {ct: max(r[ct] for r in trunk_tons(flow)) for ct in (BOX, BULK)}
    assert load[BOX] > 0 and load[BULK] > 0, "the trunk carries both cargo types at baseline"
    for e in trunk:      # capacities at the baseline load (bulk with room), then the shock
        for ct, cap in ((BOX, load[BOX]), (BULK, 2 * load[BULK])):
            e[f"capacity_{ct}"] = e[f"base_capacity_{ct}"] = cap
    ds = parse_disruptions([{"type": "transport_disruption", "attribute": "name", "values": ["Main Road North"],
                             "capacity_reduction": {BOX: 0.5, BULK: 0.0}, "start_time": 1, "duration": 3}],
                           common["te"], common["firm_table"], firms, tp.monetary_units, sp.time_resolution)
    blocked_seen = False
    for t in range(1, 5):
        stock_before = {pid: f.product_stock for pid, f in firms.items()}
        inv_before = {pid: sum(f.inventory.values()) for pid, f in firms.items()}
        flow, _, _ = _run_one_time_step(t, sc, tn, tn, firms, hh, countries, tp, sp, disruptions=ds)
        for tons in trunk_tons(flow):
            if t <= 3:
                assert tons[BOX] <= 0.5 * load[BOX] * (1 + 1e-9)
            assert tons[BULK] <= 2 * load[BULK]
        sent = {pid: 0.0 for pid in firms}
        for u, v, data in sc.edges(data=True):
            link = data["object"]
            if getattr(u, "pid", None) in sent:
                sent[u.pid] += link.realized_delivery
            if link.capacity_blocked > 1e-9:
                blocked_seen = True
                assert link.cargo_type == BOX, "only containers are cut"
        for pid, f in firms.items():
            assert math.isclose(f.product_stock, stock_before[pid] + f.production - sent[pid] - f.reconstruction_produced,
                                rel_tol=1e-9, abs_tol=1e-6)
            assert math.isclose(sum(f.inventory.values()), inv_before[pid] + f.total_input - f.input_consumed,
                                rel_tol=1e-9, abs_tol=1e-6)
    assert blocked_seen, "the halved container capacity never bound"
    assert all(e[f"capacity_{BOX}"] == load[BOX] for e in trunk)          # restored after the 3 steps


# ----------------------------------------------------------------------
# transport_cost_shock: capacity_factor per cargo
# ----------------------------------------------------------------------

def test_cost_shock_capacity_factor_per_cargo():
    tn = _network({})
    TransportCostShock(description={1: 3.0}, duration=2, capacity_factor={BOX: 0.2, "default": 0.6},
                       substitution_share=0.5).implement(tn)
    route = Route([1, 4], tn, BOX)
    assert route.shock_ceiling(tn, BOX) == (0.2, 0.5)
    assert route.shock_ceiling(tn, BULK) == (0.6, 0.5)
    tn = _network({})
    TransportCostShock(description={1: 3.0}, duration=2, capacity_factor=0.4, substitution_share=0.5).implement(tn)
    assert route.shock_ceiling(tn, BOX) == route.shock_ceiling(tn) == (0.4, 0.5)
    tn = _network({})
    TransportCostShock(description={1: 4.0}, duration=2, substitution_share=0.5).implement(tn)   # default 1/m
    assert route.shock_ceiling(tn, BULK) == (0.25, 0.5)


def test_cost_shock_capacity_factor_dict_is_validated():
    with pytest.raises(ValueError, match=r"in \[0, 1\]"):
        parse_disruptions([{"type": "transport_cost_shock", "attribute": "name", "values": ["A"],
                            "cost_multiplier": 2, "capacity_factor": {BULK: 2}}], _EDGES, None, {}, "mUSD")
    d = parse_disruptions([{"type": "transport_cost_shock", "attribute": "name", "values": ["A"],
                            "cost_multiplier": 2, "capacity_factor": {"boxes": 0.5}}], _EDGES, None, {}, "mUSD")[0]
    with pytest.raises(ValueError, match="unknown cargo type"):
        d.implement(_network({}))
