"""Edge costs are per ton for the trip and must not depend on the simulation
step (KI-37): distance x rate per tkm, fees, and hours x cost_of_time in USD
per ton-hour. Until 16 Sep 2026 the time term carried a days_per_step / 7
factor, so on the EU parameters a 500 km container barge was the cheapest
option at daily resolution and the dearest at monthly. Capacities, by
contrast, are tons per step and must scale with the resolution."""

import pytest

from disruptsc.config import build_params, load_config
from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.network.transport_network import _calculate_cost_per_ton


def _costs_and_capacities(time_resolution):
    cfg = load_config("Testkistan")
    tp, _, _, _ = build_params(cfg)
    tn, _, _ = build_transport_network(
        cfg.get("transport_modes", ["roads"]), cfg.get("filepaths", {}),
        cfg.get("logistics", {}), time_resolution,
        capacity_overrides=cfg.get("transport_capacity_overrides"),
        default_transport_capacity=cfg.get("default_transport_capacity"),
        use_cargo_types=tp.use_cargo_types,
    )
    # Only the labels _calculate_cost_per_ton writes: the example GeoPackage also
    # carries legacy v1 columns such as cost_per_ton_0_maritime (NaN).
    cost_keys = [f"{prefix}_{ct}" for ct in tn.cargo_types
                 for prefix in ("cost_per_ton", "cost_per_ton_with_capacity")]
    cap_keys = ["capacity"] + [f"capacity_{ct}" for ct in tn.cargo_types]
    costs, caps = {}, {}
    for edge, attr in tn.edges.items():
        for key in cost_keys:
            if key in attr:
                costs[(edge, key)] = attr[key]
        for key in cap_keys:
            if key in attr:
                caps[(edge, key)] = attr[key]
    return costs, caps


def test_trip_cost_independent_of_time_resolution_while_capacity_scales():
    c_day, cap_day = _costs_and_capacities("day")
    c_month, cap_month = _costs_and_capacities("month")
    assert c_day and c_day.keys() == c_month.keys()
    for key, value in c_day.items():
        assert c_month[key] == pytest.approx(value), key
    # capacities are tons per step: day -> month multiplies by 30
    positive = [k for k, v in cap_day.items() if v > 0]
    assert positive, "no positive capacity to check"
    for key in positive:
        assert cap_month[key] == pytest.approx(30 * cap_day[key]), key


def test_time_term_is_hours_times_cost_per_ton_hour():
    edge = {"id": 1, "type": "roads", "km": 120.0, "capacity": 1e9}
    params = {"speeds": {"roads": 60.0}, "basic_cost": {"roads": 0.0}, "cost_of_time": 0.5}
    _calculate_cost_per_ton(edge, params, ["container"])
    assert edge["cost_per_ton_container"] == pytest.approx(2.0 * 0.5)   # 2 h x 0.5 USD per ton-hour
