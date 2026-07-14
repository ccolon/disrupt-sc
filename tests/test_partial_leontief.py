"""Tests for the Partially-Binding ("adapted") Leontief production function.

Locks the three input tiers (Pichler et al. 2022) implemented in ``Firm.produce``:

* critical (weight >= 1)  -> hard Leontief bind (output <= inventory/coef);
* important (weight 0.5)  -> soft floor 0.5*(inventory/coef) + 0.5*eq_production
                             (a fully depleted important input halves output);
* non-critical (weight 0) -> never caps output, but is still consumed.

Empty ``input_criticality`` must reproduce strict Leontief (backward compat).
"""

import math

from disruptsc.agents.firm import Firm


def _make_firm(eq=100.0, utilization=0.8):
    f = Firm(pid="f1", region="ESP", sector="agriculture",
             sector_type="agriculture", region_sector="ESP_agriculture")
    f.utilization_rate = utilization
    f.initialize_production(eq)  # eq_production=100, current cap=100 (rest), ceiling=125
    f.production_target = 100.0  # equilibrium demand
    return f


def _one_input(f, coef=0.5, inventory=10.0, weight=None):
    inp = "ESP_steel"
    f.input_mix = {inp: coef}
    f.inventory = {inp: inventory}
    if weight is not None:
        f.input_criticality = {inp: weight}
    return inp


def test_critical_input_binds_leontief():
    f = _make_firm()
    _one_input(f, coef=0.5, inventory=10.0, weight=1.0)  # 10/0.5 = 20
    f.produce()
    assert math.isclose(f.production, 20.0)  # hard-capped by the critical input


def test_non_critical_input_does_not_bind():
    f = _make_firm()
    _one_input(f, coef=0.5, inventory=0.0, weight=0.0)  # empty, but non-critical
    f.produce()
    # Not capped by the depleted input: bounded only by capacity/demand (=100).
    assert math.isclose(f.production, 100.0)


def test_non_critical_input_is_still_consumed():
    f = _make_firm()
    inp = _one_input(f, coef=0.5, inventory=80.0, weight=0.0)
    f.produce()
    assert math.isclose(f.production, 100.0)
    # Consumed coef*production = 0.5*100 = 50 -> 80-50 = 30.
    assert math.isclose(f.inventory[inp], 30.0)


def test_important_input_soft_floor_at_half_eq():
    f = _make_firm()
    _one_input(f, coef=0.5, inventory=0.0, weight=0.5)  # fully depleted important input
    f.produce()
    # soft floor = 0.5*(0/0.5) + 0.5*eq(100) = 50.
    assert math.isclose(f.production, 50.0)


def test_important_input_partial_inventory_interpolates():
    f = _make_firm()
    _one_input(f, coef=0.5, inventory=20.0, weight=0.5)  # 20/0.5 = 40
    f.produce()
    # soft floor = 0.5*40 + 0.5*100 = 70.
    assert math.isclose(f.production, 70.0)


def test_important_input_full_inventory_non_binding():
    f = _make_firm()
    _one_input(f, coef=0.5, inventory=200.0, weight=0.5)  # 200/0.5 = 400
    f.produce()
    # soft floor = 0.5*400 + 0.5*100 = 250 >> capacity(100) -> capacity/demand binds.
    assert math.isclose(f.production, 100.0)


def test_empty_criticality_recovers_strict_leontief():
    f = _make_firm()
    _one_input(f, coef=0.5, inventory=10.0, weight=None)  # no criticality assigned
    assert f.input_criticality == {}
    assert f.critical_input_threshold == 0.0
    f.produce()
    assert math.isclose(f.production, 20.0)  # every input binds, like a critical input


def test_materiality_floor_gates_out_tiny_critical_input():
    """critical_input_threshold composes with the matrix: a survey-critical input
    that is a trace cost share is forced non-critical (this is what restores
    saturation in flow_coverage)."""
    def build():
        f = _make_firm()
        f.input_mix = {"ESP_big": 0.5, "ESP_trace": 0.01}     # trace share ~2%
        f.inventory = {"ESP_big": 500.0, "ESP_trace": 0.0}    # trace depleted
        f.input_criticality = {"ESP_big": 1.0, "ESP_trace": 1.0}  # both critical in survey
        return f

    f0 = build()
    f0.critical_input_threshold = 0.0        # pure matrix: empty trace halts output
    f0.produce()
    assert math.isclose(f0.production, 0.0)

    f1 = build()
    f1.critical_input_threshold = 0.05       # floor > trace share ⇒ trace non-critical
    f1.produce()
    assert math.isclose(f1.production, 100.0)


def test_missing_input_key_defaults_to_critical():
    """A firm with a partial criticality map treats unlisted inputs as critical."""
    f = _make_firm()
    f.input_mix = {"ESP_steel": 0.5, "ESP_water": 0.5}
    f.inventory = {"ESP_steel": 200.0, "ESP_water": 5.0}  # water scarce
    f.input_criticality = {"ESP_steel": 0.0}              # water unlisted -> critical
    f.produce()
    assert math.isclose(f.production, 10.0)  # bound by water: 5/0.5 = 10
