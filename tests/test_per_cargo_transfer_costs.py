"""Per-cargo transfer costs: dwell_times / loading_fees entries may be per-cargo
dicts, expressing dedicated transshipment infrastructure (a refinery rail siding
is near-free for liquid bulk, a full lift for a container). Scalars must keep
their exact pre-enhancement behavior - existing scope configs are all scalar."""

import pytest

from disruptsc.network.transport_network import _calculate_cost_per_ton

CARGOS = ["container", "liquid_bulk"]


def _params(dwell, fee):
    return {
        "speeds": {"multimodal": 10, "roads": 50},
        "basic_cost": {"multimodal": 0.02, "roads": 0.06},
        "cost_of_time": {"container": 1.0, "liquid_bulk": 0.1, "default": 0.5},
        "dwell_times": {"roads-railways": dwell},
        "loading_fees": {"roads-railways": fee},
    }


def _edge():
    return {"id": 1, "type": "multimodal", "multimodes": "roads-railways", "km": 10.0}


def test_scalar_values_apply_to_every_cargo_identically():
    edge = _edge()
    _calculate_cost_per_ton(edge, _params(8.0, 5.0), CARGOS, "week")
    # multimodal edges ride the ROADS speed (50): transport_time = 10/50 = 0.2h
    # base = km*0.02 + fee 5; time = (0.2 + dwell 8) h * cot
    assert edge["cost_per_ton_container"] == pytest.approx(0.2 + 5 + 8.2 * 1.0)
    assert edge["cost_per_ton_liquid_bulk"] == pytest.approx(0.2 + 5 + 8.2 * 0.1)


def test_per_cargo_dicts_differentiate_transfer_costs():
    edge = _edge()
    _calculate_cost_per_ton(
        edge,
        _params({"default": 8.0, "liquid_bulk": 1.0}, {"default": 5.0, "liquid_bulk": 0.5}),
        CARGOS, "week")
    # container rides the defaults; liquid gets the siding economics
    assert edge["cost_per_ton_container"] == pytest.approx(0.2 + 5 + 8.2 * 1.0)
    assert edge["cost_per_ton_liquid_bulk"] == pytest.approx(0.2 + 0.5 + 1.2 * 0.1)


def test_non_multimodal_edges_ignore_transfer_costs():
    edge = {"id": 2, "type": "roads", "km": 10.0}
    _calculate_cost_per_ton(
        edge, _params({"default": 8.0, "liquid_bulk": 1.0}, 5.0), CARGOS, "week")
    assert edge["cost_per_ton_container"] == pytest.approx(0.6 + (10 / 50) * 1.0)
    assert edge["cost_per_ton_liquid_bulk"] == pytest.approx(0.6 + (10 / 50) * 0.1)


def test_per_cargo_basic_cost():
    """8 Sep 2026: logistics.basic_cost entries may be per-cargo dicts (waterway rates by vessel type)."""
    from disruptsc.network.transport_network import _calculate_cost_per_ton
    edge = {"id": 1, "type": "waterways", "km": 100.0, "capacity": 1e9}
    params = {"speeds": {"waterways": 10.0}, "basic_cost": {"waterways": {"default": 0.010, "liquid_bulk": 0.038}},
              "cost_of_time": 0.0}
    _calculate_cost_per_ton(edge, params, ["dry_bulk", "liquid_bulk", "container"], "week")
    assert edge["cost_per_ton_dry_bulk"] == 1.0            # 100 km x 0.010
    assert edge["cost_per_ton_container"] == 1.0           # default
    assert edge["cost_per_ton_liquid_bulk"] == 3.8         # 100 km x 0.038
    scalar = {"id": 2, "type": "waterways", "km": 100.0, "capacity": 1e9}
    _calculate_cost_per_ton(scalar, {"speeds": {"waterways": 10.0}, "basic_cost": {"waterways": 0.010}, "cost_of_time": 0.0},
                            ["dry_bulk"], "week")
    assert scalar["cost_per_ton_dry_bulk"] == 1.0
