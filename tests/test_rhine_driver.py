"""Rhine study driver (studies/rhine2026/run_rhine.py): weekly schedule with
closure floors by cargo class (5 Sep 2026) and the unchanged single-floor rule."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studies" / "rhine2026"))

from run_rhine import (CLOSED_MULTIPLIER, DEFAULT_CLOSURE_FLOORS, build_disruptions,  # noqa: E402
                       closed_classes, parse_closure_floors)

CTS = ["container", "dry_bulk", "liquid_bulk"]


def test_parse_closure_floors():
    f = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    assert f == {"container": 40.0, "liquid_bulk": 50.0, "dry_bulk": 30.0, "default": 30.0}
    assert parse_closure_floors("none") is None and parse_closure_floors(None) is None
    assert parse_closure_floors("container=45")["default"] == 45.0


def test_closed_classes_at_or_below_the_floor():
    f = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    assert closed_classes(66, f, CTS) == []
    assert closed_classes(50, f, CTS) == ["liquid_bulk"]
    assert closed_classes(40, f, CTS) == ["container", "liquid_bulk"]
    assert closed_classes(30, f, CTS) == CTS


def test_weekly_schedule_by_cargo_floor():
    f = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    gauges = [100, 45, 33, 24, 200]
    reductions = [0.2, 0.667, 0.735, 0.78, 0.0]
    by_t = {d["start_time"]: d for d in build_disruptions(
        reductions, ["kaub"], closure_threshold=0.75, gauges=gauges, closure_floors=f, cargo_types=CTS)}
    assert by_t[1]["type"] == "transport_cost_shock" and by_t[1]["cost_multiplier"] == 1.25
    m2 = by_t[2]["cost_multiplier"]                      # 45 cm: tank barges out, the rest pays x3
    assert m2["liquid_bulk"] == CLOSED_MULTIPLIER and m2["container"] == m2["dry_bulk"] == m2["default"] == 3.003
    m3 = by_t[3]["cost_multiplier"]                      # 33 cm: only the small dry-bulk units sail
    assert m3["container"] == m3["liquid_bulk"] == CLOSED_MULTIPLIER and m3["dry_bulk"] == 3.774
    assert by_t[4]["type"] == "transport_disruption" and by_t[4]["capacity_reduction"] == 1.0
    assert 5 not in by_t                                  # nothing to apply at 200 cm
    assert by_t[2]["capacity_factor"] == 1.0              # no substitution ceiling: all-or-nothing


def test_single_floor_rule_unchanged_without_floors():
    reductions = [0.2, 0.667, 0.735, 0.78]
    legacy = build_disruptions(reductions, ["kaub"], closure_threshold=0.75)
    assert [d["type"] for d in legacy] == ["transport_cost_shock"] * 3 + ["transport_disruption"]
    assert legacy[2]["cost_multiplier"] == 3.774
    same = build_disruptions(reductions, ["kaub"], closure_threshold=0.75, closure_floors=None, gauges=[1, 2, 3, 4])
    assert same == legacy
