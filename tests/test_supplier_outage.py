"""KI-57 (13 Nov 2026): supplier switching must not stop a firm ordering an input for good.

With adaptive_supplier_weight, a supplier's satisfaction is an EMA of its fill rate (smoothing
0.5), so n steps without delivery leave 0.5^n. After ~20 such steps every supplier of an input
can sit below EPSILON together; ordering nothing then was an absorbing state (satisfaction only
updates on a positive order). The firm now falls back to its baseline shares when the pool's
signals sum below EPSILON, and the signals recover once deliveries resume.
"""
import math
from types import SimpleNamespace

from disruptsc.agents.firm import Firm
from disruptsc.config import EPSILON


class _Net:
    """The two calls update_supplier_satisfaction makes on the supply-chain network."""

    def __init__(self, links):
        self.links = links

    def in_edges(self, node, data=False):
        return [(SimpleNamespace(pid=sid), node, {"object": link}) for sid, link in self.links.items()]


def _firm(weights):
    f = Firm(pid="f1", region="KHM", sector="M69", sector_type="service", region_sector="KHM_M69")
    f.input_mix = {"X": 0.1}
    f.eq_needs = {"X": 10.0}
    f.input_needs = {"X": 10.0}
    f.inventory_duration_target = {"X": 1.0}
    f.inventory_restoration_time = 1.0
    f.inventory = {"X": 10.0}                          # held at target: the order is the need, 10
    f.suppliers = {sid: {"sector": "X", "weight": w, "satisfaction": 1.0} for sid, w in weights.items()}
    return f


def _step(f, net, delivered):
    """Plan, send the plan as this step's served order, deliver a share of it, update the signals."""
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=True)
    for sid, link in net.links.items():
        link.served_order = f.purchase_plan[sid]
        link.delivery = delivered.get(sid, 0.0) * link.served_order
    f.update_supplier_satisfaction(net)
    return dict(f.purchase_plan)


def test_single_supplier_keeps_being_ordered_through_a_24_step_outage():
    f = _firm({"s1": 1.0})
    net = _Net({"s1": SimpleNamespace(served_order=0.0, delivery=0.0)})
    for _ in range(24):
        plan = _step(f, net, delivered={})
        assert math.isclose(plan["s1"], 10.0)          # before the fix the order fell to 0 from step 21
    assert f.suppliers["s1"]["satisfaction"] < EPSILON   # the outage did reach the absorbing state
    plan = _step(f, net, delivered={"s1": 1.0})         # deliveries resume
    assert math.isclose(plan["s1"], 10.0)
    assert f.suppliers["s1"]["satisfaction"] > 0.5 - 1e-9


def test_two_suppliers_out_together_get_baseline_shares_then_orders_follow_who_delivers():
    f = _firm({"a": 3.0, "b": 1.0})
    net = _Net({"a": SimpleNamespace(served_order=0.0, delivery=0.0),
                "b": SimpleNamespace(served_order=0.0, delivery=0.0)})
    for _ in range(24):
        plan = _step(f, net, delivered={})
    assert math.isclose(plan["a"], 7.5) and math.isclose(plan["b"], 2.5)   # baseline split 3:1
    _step(f, net, delivered={"a": 1.0})                 # only a's route reopens
    plan = _step(f, net, delivered={"a": 1.0})
    assert math.isclose(plan["a"] + plan["b"], 10.0)
    assert plan["b"] < 1e-6 * plan["a"]                 # switching still moves the order to the supplier that delivers


def test_switching_unchanged_while_one_supplier_delivers():
    f = _firm({"a": 3.0, "b": 1.0})
    net = _Net({"a": SimpleNamespace(served_order=0.0, delivery=0.0),
                "b": SimpleNamespace(served_order=0.0, delivery=0.0)})
    for _ in range(12):
        plan = _step(f, net, delivered={"b": 1.0})       # a fails for 12 steps, b delivers in full
    w_a, w_b = 0.75 * 0.5 ** 11, 0.25 * 1.0              # the 12th plan uses the signal after 11 updates
    assert math.isclose(plan["a"], 10.0 * w_a / (w_a + w_b), rel_tol=1e-9)
    assert math.isclose(plan["b"], 10.0 * w_b / (w_a + w_b), rel_tol=1e-9)
