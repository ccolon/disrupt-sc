"""Within-step capacity gate (docs/architecture/transport-capacity.md, 21 Sep 2026).

Synthetic network (cost per ton for cargo "dry_bulk", every edge 100 km of road):

    1 --A(10)-- 4                      capacity on A
    1 --(5)-- 2 --B(6)-- 4             capacity on B; 1-2-4 costs 11 from node 1
    1 --(30)-- 3 --(30)-- 4            the dear detour, cost 60

Two shippers at node 1 send 80 t each to node 4 over A; a third at node 2
sends 60 t over B. With A and B at 100 t: round 1 cuts the two A shippers to
50 t each (proportional), their 30 t shares reroute over 1-2-4, B is offered
60 + 60 and takes 40 of the newcomers (round priority: the node-2 shipper is
untouched), the last 10 t each face the cost-60 detour and give up under a
freight-bill threshold of 2. Three rounds: the bound |C| + 1.
"""

from __future__ import annotations

import math

import pytest

from disruptsc.agents.transport_utils import send_shipment
from disruptsc.build import build_agents, build_common
from disruptsc.config import build_params, load_config
from disruptsc.init_pipeline.routing import setup_logistic_routes
from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import TransportParams
from disruptsc.run_pipeline.capacity_gate import run_capacity_gate
from disruptsc.run_pipeline.simulate import _run_one_time_step

CT = "dry_bulk"


class _Firm:
    def __init__(self, pid, stock=0.0):
        self.pid, self.product_stock = pid, stock


class _Country:
    def __init__(self, pid):
        self.pid = pid
        self.qty_sold = self.usd_transported = self.tons_transported = self.tonkm_transported = 0.0


def _network(caps: dict, cargo_types=(CT,)) -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = list(cargo_types)
    for n in (1, 2, 3, 4):
        tn.add_node(n, id=n, long=float(n), lat=0.0, shipments={}, disruption_duration=0, type="road")
    edges = [(1, 4, 10, 1, "A"), (1, 2, 5, 2, "e12"), (2, 4, 6, 3, "B"), (1, 3, 30, 4, "e13"), (3, 4, 30, 5, "e34")]
    for u, v, cost, eid, name in edges:
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


def _link(tn, pid, supplier, nodes, tons, cargo=CT):
    route = Route(nodes, tn, cargo)
    return CommercialLink(pid=pid, supplier_id=supplier, buyer_id="buyer", product="P", product_type="mining",
                          category="domestic_B2B", origin_node=nodes[0], destination_node=nodes[-1], route=route,
                          route_cost_per_ton=tn.compute_route_cost(route, cargo), use_transport_network=True,
                          cargo_type=cargo, delivery=float(tons), delivery_in_tons=float(tons), eq_price=1.0, price=1.0)


def _ship(tn, tp, link, firms):
    send_shipment(link.supplier_id, link.origin_node, 0.1, link, tn, tn, tp,
                  after_shipment=lambda l, r: setattr(firms[l.supplier_id], "product_stock",
                                                      firms[l.supplier_id].product_stock - l.realized_delivery))


def _loads(tn):
    return {tn[u][v]["name"]: round(math.fsum(r["tons"] for r in tn[u][v]["shipments"].values()), 6)
            for u, v in tn.edges}


def _scenario(tp, order=("s1", "s2", "s3"), caps=None):
    tn = _network(caps or {"A": 100.0, "B": 100.0})
    firms = {"F1": _Firm("F1", 80.0), "F2": _Firm("F2", 80.0), "F3": _Firm("F3", 60.0)}
    links = {"s1": _link(tn, "s1", "F1", [1, 4], 80), "s2": _link(tn, "s2", "F2", [1, 4], 80),
             "s3": _link(tn, "s3", "F3", [2, 4], 60)}
    for pid in order:
        _ship(tn, tp, links[pid], firms)
    result = run_capacity_gate(tn, tn, firms, {}, tp, 0)
    return tn, firms, links, result


def test_proportional_cut_round_priority_and_the_bound():
    tp = TransportParams(price_increase_threshold=2.0)
    tn, firms, links, result = _scenario(tp)
    assert result["rounds"] == 3 and result["n_saturated"] == 2          # |C| + 1 rounds, both edges filled
    assert _loads(tn) == {"A": 100.0, "e12": 40.0, "B": 100.0, "e13": 0.0, "e34": 0.0}
    for pid in ("s1", "s2"):
        link = links[pid]
        assert link.realized_delivery == pytest.approx(70.0) and link.delivery == pytest.approx(70.0)
        assert link.main_route_realized_delivery == pytest.approx(50.0)
        assert link.alternative_route_realized_delivery == pytest.approx(20.0)
        assert link.capacity_blocked == pytest.approx(10.0)
        assert link.delivery_offered == pytest.approx(80.0)
        # 50 t at the base price, 20 t on 1-2-4 at +10 % freight x 0.1 transport share
        assert link.payment == pytest.approx(50 * 1.0 + 20 * 1.01)
        assert link.price == pytest.approx(link.payment / 70.0)
        assert firms[link.supplier_id].product_stock == pytest.approx(10.0)   # the blocked goods stayed
    assert links["s3"].realized_delivery == pytest.approx(60.0) and links["s3"].capacity_blocked == 0.0
    assert firms["F3"].product_stock == pytest.approx(0.0)
    # the buyer at node 4 finds exactly the delivered quantities
    dest = tn._node[4]["shipments"]
    assert dest["s1"]["quantity"] == pytest.approx(70.0) and dest["s3"]["quantity"] == pytest.approx(60.0)
    # gross tonnage: 60 t cut on A and 20 t on B; 60 t re-sent in round 1 (20 of which B
    # cut again), nothing accepted in round 2; blocked = cut - re-sent = 20 t
    assert result["cut_tons"] == pytest.approx(60 + 20) and result["resent_tons"] == pytest.approx(60.0)
    assert result["blocked_tons"] == pytest.approx(20.0)
    stats = tn.capacity_gate_stats
    assert stats[1]["saturated"] and stats[3]["saturated"]
    assert stats[1]["withheld_tons"] == pytest.approx(60.0) and stats[3]["withheld_tons"] == pytest.approx(20.0)


def test_generous_threshold_takes_the_dear_detour_instead_of_blocking():
    tp = TransportParams(price_increase_threshold=None)
    tn, firms, links, result = _scenario(tp)
    assert _loads(tn)["e13"] == pytest.approx(20.0) and _loads(tn)["e34"] == pytest.approx(20.0)
    for pid in ("s1", "s2"):
        link = links[pid]
        assert link.realized_delivery == pytest.approx(80.0) and link.capacity_blocked == 0.0
        assert link.payment == pytest.approx(50 * 1.0 + 20 * 1.01 + 10 * 1.5)   # cost 60 vs 10: +500 % x 0.1
        assert firms[link.supplier_id].product_stock == pytest.approx(0.0)
    assert result["blocked_tons"] == pytest.approx(0.0)


def test_outcome_does_not_depend_on_the_delivery_order():
    tp = TransportParams(price_increase_threshold=2.0)
    a = _scenario(tp, order=("s1", "s2", "s3"))
    b = _scenario(tp, order=("s3", "s2", "s1"))
    assert _loads(a[0]) == _loads(b[0])
    for pid in ("s1", "s2", "s3"):
        for field in ("realized_delivery", "capacity_blocked", "payment", "price"):
            assert getattr(a[2][pid], field) == pytest.approx(getattr(b[2][pid], field), abs=1e-9)


def test_proportional_within_a_round():
    tp = TransportParams(price_increase_threshold=2.0)
    tn = _network({"A": 90.0, "B": 100.0})
    firms = {"F1": _Firm("F1", 80.0), "F2": _Firm("F2", 40.0)}
    links = [_link(tn, "s1", "F1", [1, 4], 80), _link(tn, "s2", "F2", [1, 4], 40)]
    for link in links:
        _ship(tn, tp, link, firms)
    run_capacity_gate(tn, tn, firms, {}, tp, 0)
    assert links[0].main_route_realized_delivery == pytest.approx(60.0)     # x 0.75 each
    assert links[1].main_route_realized_delivery == pytest.approx(30.0)
    assert _loads(tn) == {"A": 90.0, "e12": 30.0, "B": 30.0, "e13": 0.0, "e34": 0.0}
    assert all(l.capacity_blocked == 0.0 and l.realized_delivery == pytest.approx(l.delivery_offered) for l in links)


def test_less_binding_gate_keeps_its_slack_and_a_stranded_share_is_blocked():
    # s5 (80 t, 1-2-4) crosses e12 (cap 50) and B (cap 100); s3 (60 t) uses B only.
    # Round 1: e12 cuts to 0.625, B to 100/140: s5 takes the smaller factor (50 t),
    # s3 42.86 t; e12 is full, B keeps 7.14 t of slack and stays open. s5's 30 t go
    # over A (free); s3's 17.14 t can only come back through B, which fills, and the
    # last 10 t have no route at all from node 2 (e12 and B both excluded).
    tp = TransportParams(price_increase_threshold=2.0)
    tn = _network({"e12": 50.0, "B": 100.0})
    firms = {"F5": _Firm("F5", 80.0), "F3": _Firm("F3", 60.0)}
    s5 = _link(tn, "s5", "F5", [1, 2, 4], 80)
    s3 = _link(tn, "s3", "F3", [2, 4], 60)
    _ship(tn, tp, s5, firms); _ship(tn, tp, s3, firms)
    result = run_capacity_gate(tn, tn, firms, {}, tp, 0)
    loads = _loads(tn)
    assert loads["e12"] == pytest.approx(50.0) and loads["B"] == pytest.approx(100.0)
    assert loads["A"] == pytest.approx(30.0)
    assert s5.realized_delivery == pytest.approx(80.0) and s5.capacity_blocked == 0.0
    assert s3.realized_delivery == pytest.approx(50.0) and s3.capacity_blocked == pytest.approx(10.0)
    assert firms["F3"].product_stock == pytest.approx(10.0)
    assert result["rounds"] <= 3


def test_per_cargo_capacity_gates_only_that_cargo():
    tp = TransportParams(price_increase_threshold=2.0)
    tn = _network({"A": {CT: 100.0}}, cargo_types=(CT, "container"))
    firms = {"F1": _Firm("F1", 80.0), "F2": _Firm("F2", 80.0), "F4": _Firm("F4", 500.0)}
    bulk = [_link(tn, "s1", "F1", [1, 4], 80), _link(tn, "s2", "F2", [1, 4], 80)]
    box = _link(tn, "s4", "F4", [1, 4], 500, cargo="container")
    for link in bulk + [box]:
        _ship(tn, tp, link, firms)
    run_capacity_gate(tn, tn, firms, {}, tp, 0)
    assert box.realized_delivery == pytest.approx(500.0) and box.capacity_blocked == 0.0
    assert all(l.main_route_realized_delivery == pytest.approx(50.0) for l in bulk)
    assert _loads(tn)["A"] == pytest.approx(600.0)                # 100 t of bulk + 500 t of containers


def test_country_bookkeeping_follows_the_cut_and_the_resend():
    tp = TransportParams(price_increase_threshold=2.0)
    tn = _network({"A": 100.0, "B": 1000.0})
    countries = {"C": _Country("C")}
    link = _link(tn, "c1", "C", [1, 4], 160)
    send_shipment("C", 1, 0.1, link, tn, tn, tp,
                  after_shipment=lambda l, r: (setattr(countries["C"], "qty_sold", l.realized_delivery),
                                               setattr(countries["C"], "tons_transported", l.delivery_in_tons),
                                               setattr(countries["C"], "tonkm_transported", l.delivery_in_tons * r.length)))
    run_capacity_gate(tn, tn, {}, countries, tp, 0)
    assert link.realized_delivery == pytest.approx(160.0) and link.capacity_blocked == 0.0
    assert countries["C"].qty_sold == pytest.approx(160.0)
    assert countries["C"].tons_transported == pytest.approx(160.0)
    assert countries["C"].tonkm_transported == pytest.approx(100 * 100.0 + 60 * 200.0)   # 100 t over A, 60 t over 1-2-4


def test_searches_are_bounded_by_the_cut_shares_and_cached():
    tp = TransportParams(price_increase_threshold=2.0, use_route_cache=True)
    tn = _network({"A": 100.0, "B": 100.0})
    calls = {"n": 0}
    orig = TransportNetwork.provide_shortest_route

    def counting(self, *a, **k):
        calls["n"] += 1
        return orig(self, *a, **k)

    TransportNetwork.provide_shortest_route = counting
    try:
        firms = {"F1": _Firm("F1", 80.0), "F2": _Firm("F2", 80.0), "F3": _Firm("F3", 60.0)}
        links = [_link(tn, "s1", "F1", [1, 4], 80), _link(tn, "s2", "F2", [1, 4], 80), _link(tn, "s3", "F3", [2, 4], 60)]
        for link in links:
            _ship(tn, tp, link, firms)
        run_capacity_gate(tn, tn, firms, {}, tp, 0)
    finally:
        TransportNetwork.provide_shortest_route = orig
    # two rounds of re-sends for one (origin, destination, cargo) each, two searches per
    # uncached request (own modes, free): the second shipper of a round hits the cache
    assert calls["n"] <= 4


def test_no_capacitated_edge_is_a_no_op():
    tp = TransportParams(price_increase_threshold=2.0)
    tn = _network({})
    firms = {"F1": _Firm("F1", 80.0)}
    link = _link(tn, "s1", "F1", [1, 4], 80)
    _ship(tn, tp, link, firms)
    result = run_capacity_gate(tn, tn, firms, {}, tp, 0)
    assert result["rounds"] == 0 and link.realized_delivery == 80.0 and _loads(tn)["A"] == 80.0


# ----------------------------------------------------------------------
# Testkistan: the gate inside the time step, ledgers and the off/on identity
# ----------------------------------------------------------------------

ABS_TOL, REL_TOL = 1e-6, 1e-9


def _close(a, b, scale=1.0):
    return abs(a - b) <= ABS_TOL + REL_TOL * max(abs(a), abs(b), scale)


def _testkistan(capacity_constraint, overrides=None, seed=0):
    cfg = load_config("Testkistan")
    cfg["export_files"] = False
    cfg["capacity_constraint"] = capacity_constraint
    cfg["transport_capacity_overrides"] = overrides or {}
    tp, sp, ap, lp = build_params(cfg)
    common = build_common(cfg, tp, sp, ap, lp)
    sc, firms, hh, countries = build_agents(common, ap, sp, tp, seed=seed)
    setup_logistic_routes(sc, common["tn"], firms, countries, tp)
    return dict(cfg=cfg, tp=tp, sp=sp, tn=common["tn"], sc=sc, firms=firms, hh=hh, countries=countries)


def _step(m, t):
    _run_one_time_step(t, m["sc"], m["tn"], m["tn"], m["firms"], m["hh"], m["countries"], m["tp"], m["sp"],
                       disruptions=[])


def _link_state(m):
    return {d["object"].pid: (d["object"].realized_delivery, d["object"].price)
            for _, _, d in m["sc"].edges(data=True)}


def test_testkistan_slack_capacity_is_identical_to_capacity_off():
    off = _testkistan(False)
    on = _testkistan(True, {"Main Road North": 1e7})     # far above the 19 kt/step baseline load
    for t in range(3):
        _step(off, t); _step(on, t)
        assert _link_state(off) == _link_state(on)
        for pid, f in off["firms"].items():
            assert on["firms"][pid].production == f.production
            assert on["firms"][pid].product_stock == f.product_stock


def test_testkistan_gate_keeps_the_ledgers_and_blocks_what_the_tree_cannot_carry():
    # The Testkistan road network is a tree: a cut share has no other route, so the
    # gate withholds it and the goods stay in stock. Capacity: a tenth of the trunk's load.
    m = _testkistan(True, {"Main Road North": 275.0})
    tn, sc, firms = m["tn"], m["sc"], m["firms"]
    trunk = next(tn[u][v] for u, v in tn.edges if tn[u][v]["name"] == "Main Road North")
    blocked_seen = False
    for t in range(4):
        stock_before = {pid: f.product_stock for pid, f in firms.items()}
        inv_before = {pid: sum(f.inventory.values()) for pid, f in firms.items()}
        _step(m, t)
        assert trunk["capacity"] == pytest.approx(275.0 * 7)
        assert tn.capacity_gate_stats[trunk["id"]]["accepted_tons"] <= 275.0 * 7 * (1 + 1e-9)
        sent = {pid: 0.0 for pid in firms}
        blocked = 0.0
        for u, v, data in sc.edges(data=True):
            link = data["object"]
            if getattr(u, "pid", None) in sent:
                sent[u.pid] += link.realized_delivery
            blocked += link.capacity_blocked
            assert link.realized_delivery <= link.delivery_offered + ABS_TOL
        blocked_seen = blocked_seen or blocked > ABS_TOL
        for pid, f in firms.items():
            expected = stock_before[pid] + f.production - sent[pid] - f.reconstruction_produced
            assert _close(f.product_stock, expected, scale=f.eq_production), f"t={t} {pid}: stock ledger"
            expected_inv = inv_before[pid] + f.total_input - f.input_consumed
            assert _close(sum(f.inventory.values()), expected_inv, scale=max(f.eq_production, 1.0)), (
                f"t={t} {pid}: inventory ledger")
            # what a firm received is what its suppliers' links say they delivered
            received = sum(d["object"].realized_delivery for _, _, d in sc.in_edges(f, data=True))
            assert _close(f.total_input, received, scale=max(f.eq_production, 1.0)), f"t={t} {pid}: receipts"
    assert blocked_seen, "the capped trunk never withheld anything"


# ----------------------------------------------------------------------
# Configuration: the retired keys and the validation of the overrides
# ----------------------------------------------------------------------

def _cfg(**over):
    cfg = load_config("Testkistan")
    cfg.update(over)
    return cfg


@pytest.mark.parametrize("value", ["gradual", "binary"])
def test_retired_capacity_modes_raise_with_the_legacy_pointer(value):
    with pytest.raises(ValueError, match="legacy/v2-capacity-routing"):
        build_params(_cfg(capacity_constraint=value))


def test_retired_capacity_keys_raise():
    with pytest.raises(ValueError, match="default_transport_capacity"):
        build_params(_cfg(default_transport_capacity={"roads": 1000}))
    with pytest.raises(ValueError, match="capacity_routing_max_iterations"):
        build_params(_cfg(capacity_routing_max_iterations=3))
    cfg = _cfg()
    cfg["logistics"]["chunk_size"] = 1e9
    with pytest.raises(ValueError, match="chunk_size"):
        build_params(cfg)


def _build_network(cfg):
    tp, sp, _, _ = build_params(cfg)
    return build_transport_network(cfg["transport_modes"], cfg["filepaths"], cfg["logistics"], sp.time_resolution,
                                   capacity_overrides=cfg.get("transport_capacity_overrides"),
                                   cargo_mode_eligibility=tp.cargo_mode_eligibility,
                                   use_cargo_types=tp.use_cargo_types)


def test_unknown_override_name_or_cargo_raises():
    with pytest.raises(ValueError, match="matches no edge"):
        _build_network(_cfg(transport_capacity_overrides={"Main Road Nort": 100}))
    with pytest.raises(ValueError, match="unknown cargo type"):
        _build_network(_cfg(transport_capacity_overrides={"Main Road North": {"containers": 100}}))
    with pytest.raises(ValueError, match="unknown cargo type"):
        _build_network(_cfg(cargo_mode_eligibility={"airways": ["boxes"]}))


def test_eligibility_removes_the_cost_label():
    tn, _, _ = _build_network(_cfg(cargo_mode_eligibility={"maritime": ["container"]}))
    sea = next(tn[u][v] for u, v in tn.edges if tn[u][v]["type"] == "maritime")
    assert "cost_per_ton_container" in sea and "cost_per_ton_dry_bulk" not in sea
    road = next(tn[u][v] for u, v in tn.edges if tn[u][v]["type"] == "roads")
    assert "cost_per_ton_dry_bulk" in road                        # a mode not listed takes every cargo


def test_validate_inputs_names_the_unknown_overrides():
    from disruptsc.validate_inputs import _check_capacity_overrides
    cfg = _cfg(transport_capacity_overrides={"Main Road North": 100, "Main Road Nort": 5,
                                             "Port Terminal": {"container": 10, "boxes": 1, "dry_bulk": -3}})
    errors, warnings = [], []
    _check_capacity_overrides(cfg["filepaths"], cfg, errors, warnings)
    joined = "\n".join(errors)
    assert "Main Road Nort" in joined and "boxes" in joined and "negative" in joined
    assert "Main Road North" not in joined.replace("Main Road Nort'", "")
    errors = []
    _check_capacity_overrides(cfg["filepaths"], _cfg(transport_capacity_overrides={"Main Road North": 100}), errors, [])
    assert errors == []
