"""KI-90 (Hormuz Q57, 22 Nov 2026): input_constrained_orders.

A firm held back by a binding input kept ordering its other inputs for its production target; they piled up in
stock (never drawn down above target, KI-72) and their suppliers produced more than without the shock (world value
added rose in the Hormuz hindcast). With the option, the binding input is still ordered for the target, and every
other input only for the output the firm's inputs allow. Off by default: needs unchanged.
"""
import math

from disruptsc.agents.firm import Firm


def _firm(criticality=None, threshold=0.0):
    f = Firm(pid="f1", region="KOR", sector="Electricity", sector_type="utility", region_sector="KOR_Electricity")
    f.utilization_rate = 0.8
    f.input_mix = {"gas": 0.30, "services": 0.10, "parts": 0.05}
    f.initialize_production(100.0)                     # eq needs: gas 30, services 10, parts 5 per step
    f.inventory_duration_target = {"gas": 2.0, "services": 2.0, "parts": 2.0}
    f.initialize_inventory("week")
    f.inventory_restoration_time = 4.0
    f.input_criticality = dict(criticality or {})
    f.critical_input_threshold = threshold
    f.suppliers = {"g": {"sector": "gas", "weight": 1.0}, "s": {"sector": "services", "weight": 1.0},
                   "p": {"sector": "parts", "weight": 1.0}}
    f.production_target = 100.0
    return f


def test_off_by_default_needs_follow_the_target():
    f = _firm()
    f.inventory["gas"] = 0.0
    f._evaluate_input_needs()
    assert f.input_needs == {"gas": 30.0, "services": 10.0, "parts": 5.0}


def test_a_firm_without_its_binding_input_orders_only_that_input():
    f = _firm()
    f.inventory["gas"] = 0.0                            # gas allows no output at all
    f._evaluate_input_needs(input_constrained=True)
    assert math.isclose(f.input_needs["gas"], 30.0)     # still ordered for the target: the firm can recover
    assert math.isclose(f.input_needs["services"], 0.0)
    assert math.isclose(f.input_needs["parts"], 0.0)


def test_partial_stock_caps_the_other_inputs_at_the_output_it_allows():
    f = _firm()
    f.inventory["gas"] = 12.0                           # 12 / 0.30 = 40 units of output
    f._evaluate_input_needs(input_constrained=True)
    assert math.isclose(f.input_needs["gas"], 30.0)
    assert math.isclose(f.input_needs["services"], 0.10 * 40.0)
    assert math.isclose(f.input_needs["parts"], 0.05 * 40.0)


def test_no_binding_input_leaves_needs_unchanged():
    f = _firm()                                         # two steps of every input in stock
    f._evaluate_input_needs(input_constrained=True)
    assert f.input_needs == {"gas": 30.0, "services": 10.0, "parts": 5.0}


def test_a_non_critical_input_never_binds_or_caps():
    f = _firm(criticality={"gas": 1.0, "services": 0.0, "parts": 0.0})
    f.inventory["services"] = 0.0                       # non-critical: does not limit output
    f._evaluate_input_needs(input_constrained=True)
    assert f.input_needs == {"gas": 30.0, "services": 10.0, "parts": 5.0}


def test_an_important_input_caps_at_its_soft_floor():
    f = _firm(criticality={"gas": 0.5, "services": 1.0, "parts": 1.0})
    f.inventory["gas"] = 0.0                            # important: 0.5 x 0 + 0.5 x 100 = 50 units
    f._evaluate_input_needs(input_constrained=True)
    assert math.isclose(f.input_needs["gas"], 30.0)
    assert math.isclose(f.input_needs["services"], 0.10 * 50.0)


def test_capacity_and_inputs_together_take_the_smaller():
    f = _firm()
    f.current_production_capacity = 60.0
    f.inventory["gas"] = 24.0                           # 80 units: capacity (60) is the smaller, nothing capped
    f._evaluate_input_needs(capacity_constrained=True, input_constrained=True)
    assert f.input_needs == {"gas": 0.30 * 60.0, "services": 0.10 * 60.0, "parts": 0.05 * 60.0}


def test_produce_is_unchanged_by_the_refactor():
    f = _firm()
    f.inventory["gas"] = 12.0
    f.current_production_capacity = 125.0
    f.produce()
    assert math.isclose(f.production, 40.0)             # bound by gas, as before
