"""Edge costs are per ton for the trip and must not depend on the simulation
step (KI-37): distance x rate per tkm, fees, and hours x cost_of_time in USD
per ton-hour. Until 16 Sep 2026 the time term carried a days_per_step / 7
factor, so on the EU parameters a 500 km container barge was the cheapest
option at daily resolution and the dearest at monthly. Capacities, by
contrast, are tons per step and must scale with the resolution; since
21 Sep 2026 they exist only on the edges named in transport_capacity_overrides."""

import pytest

from disruptsc.config import build_params, load_config
from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.network.transport_network import _calculate_cost_per_ton

OVERRIDES = {"Main Road North": 1000.0, "Port Terminal": {"container": 500.0, "dry_bulk": 0}}


def _costs_and_capacities(time_resolution):
    cfg = load_config("Testkistan")
    cfg["transport_capacity_overrides"] = OVERRIDES
    tp, _, _, _ = build_params(cfg)
    tn, _, _ = build_transport_network(
        cfg.get("transport_modes", ["roads"]), cfg.get("filepaths", {}),
        cfg.get("logistics", {}), time_resolution,
        capacity_overrides=cfg.get("transport_capacity_overrides"),
        cargo_mode_eligibility=tp.cargo_mode_eligibility,
        use_cargo_types=tp.use_cargo_types,
    )
    # Only the labels _calculate_cost_per_ton writes: the example GeoPackage also
    # carries legacy v1 columns such as cost_per_ton_0_maritime (NaN).
    cost_keys = [f"cost_per_ton_{ct}" for ct in tn.cargo_types]
    cap_keys = ["capacity"] + [f"capacity_{ct}" for ct in tn.cargo_types]
    costs, caps = {}, {}
    for edge, attr in tn.edges.items():
        for key in cost_keys:
            if key in attr:
                costs[(edge, key)] = attr[key]
        for key in cap_keys:
            if key in attr:
                caps[(edge, key)] = attr[key]
    return tn, costs, caps


def test_trip_cost_independent_of_time_resolution_while_capacity_scales():
    _, c_day, cap_day = _costs_and_capacities("day")
    _, c_month, cap_month = _costs_and_capacities("month")
    assert c_day and c_day.keys() == c_month.keys()
    for key, value in c_day.items():
        assert c_month[key] == pytest.approx(value), key
    # capacities are tons per step: day -> month multiplies by 30
    positive = [k for k, v in cap_day.items() if v > 0]
    assert positive, "no positive capacity to check"
    for key in positive:
        assert cap_month[key] == pytest.approx(30 * cap_day[key]), key


def test_capacities_exist_only_on_named_edges_and_zero_blocks():
    tn, _, caps = _costs_and_capacities("week")
    named = {tn[u][v]["name"] for (u, v), _ in caps}
    assert named == set(OVERRIDES)
    assert len(tn.capacitated_edges()) == 2
    terminal = next(tn[u][v] for u, v in tn.edges if tn[u][v]["name"] == "Port Terminal")
    assert terminal["capacity_container"] == 500.0 * 7 and terminal["capacity_dry_bulk"] == 0
    assert "capacity_liquid_bulk" not in terminal and "capacity" not in terminal
    assert "cost_per_ton_dry_bulk" not in terminal          # explicit 0 blocks the cargo
    assert "cost_per_ton_container" in terminal and "cost_per_ton_liquid_bulk" in terminal


def test_time_term_is_hours_times_cost_per_ton_hour():
    edge = {"id": 1, "type": "roads", "km": 120.0}
    params = {"speeds": {"roads": 60.0}, "basic_cost": {"roads": 0.0}, "cost_of_time": 0.5}
    _calculate_cost_per_ton(edge, params, ["container"])
    assert edge["cost_per_ton_container"] == pytest.approx(2.0 * 0.5)   # 2 h x 0.5 USD per ton-hour
