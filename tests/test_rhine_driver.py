"""Rhine study driver (studies/rhine2026/run_rhine.py): weekly schedule with
closure floors by cargo class (5 Sep 2026) and the unchanged single-floor rule."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studies" / "rhine2026"))

from run_rhine import (CLOSED_MULTIPLIER, DEFAULT_CLOSURE_FLOORS, adjust_inventory_targets,  # noqa: E402
                       build_disruptions, closed_classes, kaub_entries, parse_closure_floors,
                       parse_inventory_add_days, rail_relief_entries)

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


def test_voyage_surcharge_entries():
    """7 Sep 2026: the week's multiplier on the other upstream edges, a third of the excess on the
    Lower Rhine, the Kaub edge keeps its own entry (class dict or closure)."""
    f = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    up = ["rhine_basel", "rhine_mainz", "kaub"]
    low = ["rhine_koblenz", "rhine_rotterdam"]
    d = build_disruptions([0.6, 0.78, 0.0], ["kaub"], closure_threshold=0.75, gauges=[45, 24, 200],
                          closure_floors=f, cargo_types=CTS, surcharge_edges=up, lower_rhine_edges=low,
                          lower_rhine_factor=1 / 3)
    k = kaub_entries(d, "kaub")
    assert [x["start_time"] for x in k] == [1, 2]
    assert k[0]["cost_multiplier"]["liquid_bulk"] == CLOSED_MULTIPLIER and k[1]["type"] == "transport_disruption"
    others = [x for x in d if x not in k]
    w1 = [x for x in others if x["start_time"] == 1]
    assert [x["values"] for x in w1] == [["rhine_basel", "rhine_mainz"], low]
    assert w1[0]["cost_multiplier"] == 2.5 and w1[1]["cost_multiplier"] == 1.5      # 1 + 1.5/3
    w2 = [x for x in others if x["start_time"] == 2]                                # closure week: x4.545 upstream
    assert w2[0]["cost_multiplier"] == 4.545 and w2[1]["cost_multiplier"] == round(1 + 3.545 / 3, 3)
    assert not [x for x in d if x["start_time"] == 3]                                # nothing at 200 cm
    legacy = build_disruptions([0.6, 0.78], ["kaub"], closure_threshold=0.75, gauges=[45, 24],
                               closure_floors=f, cargo_types=CTS)
    assert legacy == [x for x in d if x["start_time"] <= 2 and "kaub" in x["values"]]


# --- adaptation counterfactual switches (10 Sep 2026) ---

def test_gauge_offset_moves_the_closure_classes():
    # fairway deepening: the same week is read 20 cm higher, tank barges alone stay closed at 27 + 20 = 47 cm
    f = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    assert closed_classes(27.0, f, CTS) == CTS
    assert closed_classes(27.0 + 20.0, f, CTS) == ['liquid_bulk']
    assert closed_classes(42.0 + 20.0, f, CTS) == []


def test_rail_relief_entries_cover_the_shock_weeks_for_bulk_only():
    entries = rail_relief_entries([0.0, 0.3, 0.75, 1.0], 0.4, CTS)
    assert [e['start_time'] for e in entries] == [2, 3, 4]           # week 1 has no shock
    e = entries[0]
    assert e['type'] == 'transport_cost_shock' and e['attribute'] == 'type' and e['values'] == ['railways']
    assert e['cost_multiplier'] == {'container': 1.0, 'dry_bulk': 0.4, 'liquid_bulk': 0.4, 'default': 1.0}
    assert e['duration'] == 1
    assert kaub_entries(entries) == []                                 # not Kaub entries


_TARGETS = {
    'definition': 'per_buying_sector', 'unit': 'day', 'service_days': 90,
    'values': {'default': 30, 'H49': 7, 'D': 20, 'C20': 30},
    'overrides': {'*': {'D': 90, 'E': 90}, 'D': {'B05': 30, 'B06': 90, 'C19': 10}, 'C20': {'C19': 14}},
}


def test_inventory_add_days_global_leaves_coping_proxies_alone():
    out = adjust_inventory_targets(_TARGETS, add_days=7)
    assert out['values'] == {'default': 37, 'H49': 14, 'D': 27, 'C20': 37}
    assert out['overrides']['*'] == {'D': 90, 'E': 90}                 # utilities block untouched
    assert out['overrides']['D'] == {'B05': 37, 'B06': 90, 'C19': 17}  # pipeline proxy (90) untouched
    assert _TARGETS['values']['H49'] == 7                               # input not mutated


def test_inventory_add_days_targeted_and_scale():
    days, sectors = parse_inventory_add_days('7:H49,D,C23')
    assert days == 7.0 and sectors == ['H49', 'D', 'C23']
    out = adjust_inventory_targets(_TARGETS, add_days=days, sectors=sectors)
    assert out['values']['H49'] == 14 and out['values']['D'] == 27 and out['values']['C20'] == 30
    assert out['values']['C23'] == 37                                   # inherits the default, then +7
    assert out['values']['default'] == 30
    assert out['overrides']['C20'] == {'C19': 14} and out['overrides']['D']['C19'] == 17
    scaled = adjust_inventory_targets(_TARGETS, scale=0.5)
    assert scaled['values'] == {'default': 15, 'H49': 3.5, 'D': 10, 'C20': 15}
    assert parse_inventory_add_days(None) == (0.0, None)
