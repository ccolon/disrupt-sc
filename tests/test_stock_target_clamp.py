"""KI-87 (Hormuz A6, 20 Nov 2026): a firm's stock target is clamped to one step, as its initial stock.

initialize_inventory starts every input at need x max(duration, 1 step). The purchase plan's target used
need x duration without the clamp, so an input whose duration is under one step (utilities 3 days, transport
5 days at weekly steps) had a target below its starting stock: after a depletion the firm refilled it only to
the sub-step target and the economy drifted instead of recovering. Now both use max(duration, 1).
"""
import math

from disruptsc.agents.firm import Firm


def _firm(durations):
    f = Firm(pid="f1", region="GLF", sector="Trade", sector_type="trade", region_sector="GLF_Trade")
    f.utilization_rate = 0.8
    f.input_mix = {"util": 0.05, "fuel": 0.20}
    f.initialize_production(100.0)                     # eq needs: util 5, fuel 20 per step
    f.inventory_duration_target = dict(durations)       # in steps
    f.initialize_inventory("week")
    f.inventory_restoration_time = 1.0                  # steps: the whole gap in one step
    f.suppliers = {"u": {"sector": "util", "weight": 1.0}, "f": {"sector": "fuel", "weight": 1.0}}
    return f


def test_a_sub_step_input_starts_at_one_step_and_orders_its_need():
    f = _firm({"util": 3 / 7, "fuel": 2.0})
    assert math.isclose(f.inventory["util"], 5.0)        # 5 x max(3/7, 1)
    assert math.isclose(f.inventory["fuel"], 40.0)       # 20 x 2
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=False)
    assert math.isclose(f.purchase_plan["u"], 5.0)      # at rest: the need, no restoration
    assert math.isclose(f.purchase_plan["f"], 20.0)


def test_a_sub_step_input_is_refilled_to_one_step_after_a_depletion():
    f = _firm({"util": 3 / 7, "fuel": 2.0})
    f.inventory["util"] = 2.5                            # half a step left after a shock
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=False)
    # need 5 + (one step 5 - 2.5) / 1. Without the clamp the target was 5 x 3/7 = 2.14 < 2.5: the order stayed at
    # the need and the stock never came back to the one step it started with.
    assert math.isclose(f.purchase_plan["u"], 7.5)


def test_an_input_of_one_step_or_more_is_unchanged():
    f = _firm({"util": 3 / 7, "fuel": 2.0})
    f.inventory["fuel"] = 20.0                           # one step of a two-step target
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=False)
    assert math.isclose(f.purchase_plan["f"], 20.0 + 20.0)


def test_the_clamp_also_holds_with_adaptive_inventories():
    f = _firm({"util": 3 / 7, "fuel": 2.0})
    f.input_needs = {"util": 6.0, "fuel": 24.0}          # a production target 20 % above equilibrium
    f.inventory["util"] = 5.0
    f._decide_purchase_plan(adaptive_inventories=True, adaptive_weight=False)
    assert math.isclose(f.purchase_plan["u"], 6.0 + (6.0 * 1.0 - 5.0))   # target = need x max(3/7, 1)
