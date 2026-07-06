"""Regression tests for firm production-capacity disruptions.

These lock the two fixes made on the firm-capacity disruption path:

1. A productivity/capacity shock smaller than the ``1/utilization_rate``
   head-room must still constrain output (bind at equilibrium output), rather
   than being silently absorbed by spare capacity.
2. A finite-``duration`` shock must actually revert after ``duration`` steps
   (temporary forcing), while a shock with no recovery persists indefinitely.

Previously ``ProductivityShock``/``CapitalDestruction`` wrote to dead
attributes (``disruption_duration``/``disruption_reduction``) and the firm's
recovery API (``disrupt_production_capacity``) was never called, so temporary
shocks never lifted.
"""

import math

from disruptsc.agents.firm import Firm
from disruptsc.run_pipeline.disruption import (
    ProductivityShock, CapitalDestruction, Recovery,
)


def _make_firm(eq=100.0, utilization=0.8):
    f = Firm(pid="f1", region="ESP", sector="agriculture",
             sector_type="agriculture", region_sector="ESP_agriculture")
    f.utilization_rate = utilization
    f.initialize_production(eq)  # production_capacity = eq / utilization
    return f


def test_small_shock_binds_despite_capacity_buffer():
    """A 4% cut must reduce output even though the firm has 25% spare capacity."""
    f = _make_firm()
    assert math.isclose(f.production_capacity, 125.0)

    f.disrupt_production_capacity(duration=3, reduction=0.04)
    # Binds at eq output (96), not 4% off the 125 ceiling (which would be 120 > demand).
    assert math.isclose(f.current_production_capacity, 96.0)

    f.production_target = 100.0  # demand at equilibrium
    f.produce()
    assert math.isclose(f.production, 96.0)


def test_temporary_shock_reverts_after_duration():
    f = _make_firm()
    f.disrupt_production_capacity(duration=3, reduction=0.04)

    for _ in range(3):
        assert f.current_production_capacity < f.production_capacity
        f.update_disrupted_production_capacity()

    # Reverts to resting capacity = eq_production (100), not the physical ceiling
    # (125): the 25% head-room is now idle capital, reachable only by mobilizing
    # it over tau (adjust_active_capital), not free after a shock lifts.
    assert math.isclose(f.current_production_capacity, f.eq_production)
    assert f.production_capacity_reduction == 0.0


def test_persistent_shock_never_reverts():
    f = _make_firm()
    f.disrupt_production_capacity(duration=float("inf"), reduction=0.04)

    for _ in range(50):
        f.update_disrupted_production_capacity()

    assert math.isclose(f.current_production_capacity, 96.0)


def test_productivity_increase_lifts_ceiling_but_is_demand_capped():
    """A positive shock raises the cap but cannot push output above demand."""
    f = _make_firm()
    f.disrupt_production_capacity(duration=2, reduction=-0.04)
    assert math.isclose(f.current_production_capacity, 104.0)

    f.production_target = 100.0
    f.produce()
    assert math.isclose(f.production, 100.0)  # demand-constrained, no quantity gain


def test_productivity_shock_implement_honours_recovery_duration():
    f = _make_firm()
    firms = {"f1": f}
    shock = ProductivityShock(description={"f1": 0.04},
                              recovery=Recovery(duration=2), start_time=1)
    shock.implement(firms)

    assert math.isclose(f.current_production_capacity, 96.0)
    assert f.remaining_disrupted_time == 2
    # The old dead attributes are no longer written.
    assert not hasattr(f, "disruption_duration")
    assert not hasattr(f, "disruption_reduction")


def test_productivity_shock_without_recovery_is_permanent():
    f = _make_firm()
    firms = {"f1": f}
    shock = ProductivityShock(description={"f1": 0.04}, start_time=1)  # no recovery
    shock.implement(firms)

    assert f.remaining_disrupted_time == float("inf")
    for _ in range(50):
        f.update_disrupted_production_capacity()
    assert math.isclose(f.current_production_capacity, 96.0)


def test_capital_destruction_implement_uses_recovery_api():
    f = _make_firm()
    firms = {"f1": f}
    shock = CapitalDestruction(description={"f1": 0.10},
                               recovery=Recovery(duration=4), start_time=1)
    shock.implement(firms)

    assert math.isclose(f.current_production_capacity, 90.0)
    assert f.remaining_disrupted_time == 4
    assert not hasattr(f, "disruption_duration")
