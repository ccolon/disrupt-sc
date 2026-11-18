"""Region-specific stock depths and dated stock injections (MC1, Hormuz 2026, 18 Nov 2026).

``inventory_duration_targets_by_region`` ({REGION: {input id | sector | type: days}})
overrides the inventory targets of the firms (and of the households holding stocks)
located in REGION; a ``stock_injection`` disruption adds, once, at the start of its
step, ``days`` of the agents' equilibrium use of an input to the stocks of the agents
of a region that use it. Both are off without their keys.
"""

from __future__ import annotations

import copy
import logging
from types import SimpleNamespace

import pandas as pd
import pytest

from disruptsc.build import build_agents, build_common
from disruptsc.config import build_params, load_config
from disruptsc.init_pipeline.agents import configure_household_inventories, load_inventories
from disruptsc.run_pipeline.disruption import StockInjection, parse_disruptions
from disruptsc.run_pipeline.fingerprint import (
    WATERMARKED_CONFIG_KEYS, _STAGE_CONFIG_KEYS, build_fingerprint, build_stage_fingerprint,
)
from disruptsc.run_pipeline.simulate import _run_one_time_step, set_initial_conditions

AGRI = "TESTKISTAN_AGRI"


# ----------------------------------------------------------------------
# The override rule (unit)
# ----------------------------------------------------------------------

class _F:
    def __init__(self, region, sector, mix):
        self.region, self.sector, self.region_sector = region, sector, f"{region}_{sector}"
        self.input_mix = mix
        self.inventory_duration_target = {}


_TABLE = pd.DataFrame({"sector": ["A01", "B06", "C19", "C28"],
                       "type": ["agriculture", "mining", "oil_and_gas", "manufacturing"]})
_BASE = {"definition": "per_input_type", "unit": "day",
         "values": {"default": 30, "agriculture": 15, "mining": 20, "imports": 40}}


def test_region_override_precedence_units_and_other_regions():
    mix = {"SAU_B06": 0.3, "IRQ_B06": 0.1, "JPN_C28": 0.1, "JPN_A01": 0.1, "ROW_imports": 0.2}
    jpn, kor, deu = _F("JPN", "C19", dict(mix)), _F("KOR", "C19", dict(mix)), _F("DEU", "C19", dict(mix))
    by_region = {"JPN": {"SAU_B06": 90, "B06": 60, "manufacturing": 5},   # full id > sector > type
                 "KOR": {"mining": 45, "imports": 10}}
    load_inventories({"j": jpn, "k": kor, "d": deu}, _BASE, "week", _TABLE, by_region=by_region)
    j, k, d = jpn.inventory_duration_target, kor.inventory_duration_target, deu.inventory_duration_target
    assert j["SAU_B06"] == pytest.approx(90 / 7) and j["IRQ_B06"] == pytest.approx(60 / 7)
    assert j["JPN_C28"] == pytest.approx(5 / 7)
    assert j["JPN_A01"] == pytest.approx(15 / 7) and j["ROW_imports"] == pytest.approx(40 / 7)   # untouched
    assert k["SAU_B06"] == pytest.approx(45 / 7) and k["ROW_imports"] == pytest.approx(10 / 7)
    assert k["JPN_C28"] == pytest.approx(30 / 7)
    load_inventories({"d2": (d2 := _F("DEU", "C19", dict(mix)))}, _BASE, "week", _TABLE)
    assert d == d2.inventory_duration_target                              # a region not listed: as without the key


def test_region_override_of_an_import_bundle_by_composition():
    # ROW_imports of a JPN refinery is 75 % crude (B06) and 25 % machinery (C28): a crude cover
    # of 60 days moves the bundle to 0.75 x 60 + 0.25 x 30 (machinery keeps its base value)
    f = _F("JPN", "C19", {"ROW_imports": 1.0})
    shares = {("JPN", "C19"): {"ROW": {"B06": 0.75, "C28": 0.25}}}
    base = {"definition": "per_input_type", "unit": "day", "values": {"default": 30, "mining": 20}}
    load_inventories({"f": f}, base, "week", _TABLE, bundle_shares=shares, by_region={"JPN": {"B06": 60}})
    assert f.inventory_duration_target["ROW_imports"] == pytest.approx((0.75 * 60 + 0.25 * 30) / 7)
    load_inventories({"f": f}, base, "week", _TABLE, bundle_shares=shares)
    assert f.inventory_duration_target["ROW_imports"] == pytest.approx((0.75 * 20 + 0.25 * 30) / 7)


def test_region_override_with_per_buying_sector_targets():
    f = _F("JPN", "C19", {"SAU_B06": 0.5, "JPN_C28": 0.1})
    targets = {"definition": "per_buying_sector", "unit": "day", "values": {"default": 30, "C19": 12}}
    load_inventories({"f": f}, targets, "week", _TABLE, by_region={"JPN": {"B06": 70}})
    assert f.inventory_duration_target == {"SAU_B06": pytest.approx(70 / 7), "JPN_C28": pytest.approx(12 / 7)}


def test_households_get_the_override_only_when_they_hold_stocks(caplog):
    def hh(region, agent_type="household"):
        return SimpleNamespace(region=region, agent_type=agent_type, inventory={},
                               sector_consumption={"SAU_C19": 1.0, "JPN_A01": 2.0})
    hhs = {"a": hh("JPN"), "b": hh("KOR"), "g": hh("JPN", "government")}
    base = {"definition": "per_input_type", "unit": "day", "values": {"default": 7, "oil_and_gas": 3}}
    configure_household_inventories(hhs, True, base, 4.0, "week", _TABLE, by_region={"JPN": {"C19": 30}})
    assert hhs["a"].inventory_duration_target == {"SAU_C19": pytest.approx(30 / 7), "JPN_A01": pytest.approx(7 / 7)}
    assert hhs["b"].inventory_duration_target["SAU_C19"] == pytest.approx(3 / 7)
    assert hhs["g"].inventory_duration_target == {} and hhs["g"].use_inventories is False
    with caplog.at_level(logging.INFO):
        configure_household_inventories(hhs, False, base, 4.0, "week", _TABLE, by_region={"JPN": {"C19": 30}})
    assert hhs["a"].inventory_duration_target["SAU_C19"] == pytest.approx(3 / 7)
    assert "act on firms only" in caplog.text


def test_a_region_or_key_matching_nothing_is_said(caplog):
    f = _F("JPN", "C19", {"SAU_B06": 0.5})
    with caplog.at_level(logging.INFO):
        load_inventories({"f": f}, _BASE, "week", _TABLE, by_region={"JPM": {"B06": 60}, "JPN": {"B60": 1}})
    assert "no firms located in region 'JPM'" in caplog.text
    assert "keys matching no input of them: ['B60']" in caplog.text


@pytest.mark.parametrize("bad", [[1, 2], {"JPN": 60}, {"JPN": {}}, {"JPN": {"B06": -1}},
                                 {"JPN": {"B06": "60"}}, {"JPN": {"B06": float("nan")}}])
def test_bad_config_raises(bad):
    cfg = load_config("Testkistan")
    cfg["inventory_duration_targets_by_region"] = bad
    with pytest.raises(ValueError, match="inventory_duration_targets_by_region"):
        build_params(cfg)


# ----------------------------------------------------------------------
# Testkistan fixtures
# ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def tk():
    cfg = load_config("Testkistan")
    cfg["with_transport"] = False
    cfg["export_files"] = False
    # base: 30 days of every input, so that the rest of the economy holds a 3-week outage
    cfg["inventory_duration_targets"] = {"definition": "per_input_type", "unit": "day",
                                         "values": {"default": 30, "agriculture": 30}}
    tp, sp, ap, lp = build_params(cfg)
    return dict(cfg=cfg, tp=tp, sp=sp, ap=ap, common=build_common(cfg, tp, sp, ap, lp))


def _build(tk, **cfg_over):
    if cfg_over:
        cfg = copy.deepcopy(tk["cfg"]); cfg.update(cfg_over)
        tp, sp, ap, _ = build_params(cfg)
    else:
        tp, sp, ap = tk["tp"], tk["sp"], tk["ap"]
    sc, firms, hh, countries = build_agents(tk["common"], ap, sp, tp, seed=0)
    return dict(sc=sc, firms=firms, hh=hh, countries=countries, tp=tp, sp=sp, ap=ap)


def _step(tk, m, t, ds):
    tn = tk["common"]["tn"]
    _run_one_time_step(t, m["sc"], tn, tn, m["firms"], m["hh"], m["countries"], m["tp"], m["sp"], disruptions=ds)


def test_config_key_reaches_firms_and_households_through_the_build(tk):
    m = _build(tk, enable_household_inventories=True,
               inventory_duration_targets_by_region={"TESTKISTAN": {"AGRI": 60}})
    for f in m["firms"].values():
        assert f.inventory_duration_target[AGRI] == pytest.approx(60 / 7)
        assert f.inventory[AGRI] == pytest.approx(f.eq_needs[AGRI] * 60 / 7)
    holders = [h for h in m["hh"].values() if h.use_inventories]
    assert holders and all(h.inventory_duration_target[AGRI] == pytest.approx(60 / 7) for h in holders)
    assert all(h.inventory[AGRI] == pytest.approx(h.eq_needs[AGRI] * 60 / 7) for h in holders)


def test_sixty_days_hold_output_longer_than_ten_and_both_return_to_baseline(tk):
    """Same input (AGRI), same shock (every AGRI firm at zero output for 3 weekly steps),
    two MANUF firms whose only difference is the region they sit in: 60 days of AGRI in
    R60, 10 days in R10. Testkistan has one region, so the two firms are placed in R60 and
    R10 - the region label is the only thing the rule reads - and the targets re-applied."""
    m = _build(tk)
    firms = m["firms"]
    a, b = sorted((pid for pid, f in firms.items() if f.sector == "MANUF"), key=str)[:2]
    firms[a].region, firms[b].region = "R60", "R10"
    load_inventories(firms, m["ap"].inventory_duration_targets, m["sp"].time_resolution,
                     tk["common"]["sector_table"], by_region={"R60": {"AGRI": 60}, "R10": {"AGRI": 10}})
    set_initial_conditions(m["sc"], firms, m["hh"], m["countries"], m["tp"], m["sp"])
    assert firms[a].inventory_duration_target[AGRI] == pytest.approx(60 / 7)
    assert firms[b].inventory_duration_target[AGRI] == pytest.approx(10 / 7)
    others = [f for pid, f in firms.items() if pid not in (a, b)]
    assert all(f.inventory_duration_target[AGRI] == pytest.approx(30 / 7) for f in others)

    ds = parse_disruptions([{"type": "productivity_shock", "productivity_reduction": 1.0,
                             "filter": {"sector": ["AGRI"]}, "start_time": 1, "duration": 3}],
                           tk["common"]["te"], tk["common"]["firm_table"], firms, "mUSD", "week")
    ratio = {a: [], b: []}
    for t in range(0, 61):
        _step(tk, m, t, ds if t else [])
        for pid in (a, b):
            ratio[pid].append(firms[pid].production / firms[pid].eq_production)

    # the 10-day firm runs out in the second week of the outage (10/7 - 1 of a week left) and
    # stops in the third; the 60-day firm produces its equilibrium output throughout
    assert ratio[b][2] == pytest.approx(10 / 7 - 1) and ratio[b][3] == pytest.approx(0.0, abs=1e-12)
    assert all(r == pytest.approx(1.0, abs=1e-12) for r in ratio[a][:4])
    first_drop = {pid: next((t for t, r in enumerate(ratio[pid]) if r < 1 - 1e-9), None) for pid in (a, b)}
    assert first_drop[b] == 2 and first_drop[a] is None
    assert sum(max(0.0, 1 - r) for r in ratio[a]) < sum(max(0.0, 1 - r) for r in ratio[b])

    # both back to baseline: equilibrium output, stocks at least back at their targets (a
    # stock above target is not drawn down by the purchase rule, so it may stay above)
    for pid in (a, b):
        f = firms[pid]
        assert all(abs(r - 1.0) < 1e-6 for r in ratio[pid][-5:]), (pid, ratio[pid][-5:])
        assert f.inventory[AGRI] >= f.eq_needs[AGRI] * f.inventory_duration_target[AGRI] * (1 - 1e-6)
    for hh in m["hh"].values():
        assert abs(hh.consumption_loss) < 1e-6 * max(1.0, sum(hh.sector_consumption.values()))


# ----------------------------------------------------------------------
# Stock injection
# ----------------------------------------------------------------------

def _injection(**over):
    cfg = {"type": "stock_injection", "region": "TESTKISTAN", "input": "AGRI", "days": 14, "start_time": 3}
    cfg.update(over)
    return cfg


def test_injection_raises_the_stock_at_its_step_only(tk):
    k, q_days = 3, 14
    on, off = _build(tk, enable_household_inventories=True), _build(tk, enable_household_inventories=True)
    ds = parse_disruptions([_injection(days=q_days, start_time=k)], None, None, on["firms"], "mUSD", "week")
    assert len(ds) == 1 and isinstance(ds[0], StockInjection)

    def stocks(m):
        return ({pid: dict(f.inventory) for pid, f in m["firms"].items()},
                {pid: dict(h.inventory) for pid, h in m["hh"].items()})

    expected_firm = {pid: f.eq_needs[AGRI] * q_days / 7 for pid, f in on["firms"].items()}
    holders = [pid for pid, h in on["hh"].items() if h.use_inventories]
    assert holders
    expected_hh = {pid: on["hh"][pid].eq_needs[AGRI] * q_days / 7 for pid in holders}
    for t in range(0, 8):
        inv_before = {pid: sum(f.inventory.values()) for pid, f in on["firms"].items()}
        _step(tk, on, t, ds if t else [])
        _step(tk, off, t, [])
        (f_on, h_on), (f_off, h_off) = stocks(on), stocks(off)
        if t < k:      # no effect before k: bit-identical to the run without the injection
            assert f_on == f_off and h_on == h_off
            continue
        # from k on, the AGRI stocks are the twin's plus the injection, once (no repeat)
        for pid in on["firms"]:
            assert f_on[pid][AGRI] - f_off[pid][AGRI] == pytest.approx(expected_firm[pid], rel=1e-9)
            for key in f_on[pid]:
                if key != AGRI:
                    assert f_on[pid][key] == pytest.approx(f_off[pid][key], rel=1e-12)
            assert on["firms"][pid].production == pytest.approx(off["firms"][pid].production, rel=1e-12)
        for pid in holders:
            assert h_on[pid][AGRI] - h_off[pid][AGRI] == pytest.approx(expected_hh[pid], rel=1e-9)
        if t == k:     # the inventory ledger of step k: before + injected + received - consumed
            for pid, f in on["firms"].items():
                assert sum(f.inventory.values()) == pytest.approx(
                    inv_before[pid] + expected_firm[pid] + f.total_input - f.input_consumed, rel=1e-12)
    assert ds[0].n_agents == len(on["firms"]) + len(holders)
    assert ds[0].injected == pytest.approx(sum(expected_firm.values()) + sum(expected_hh.values()))


def test_injection_matching_rules(caplog):
    def firm(region, mix, needs):
        return SimpleNamespace(region=region, input_mix=mix, eq_needs=needs, inventory={k: 1.0 for k in mix})

    def hh(region, use, agent_type="household"):
        return SimpleNamespace(region=region, use_inventories=use, agent_type=agent_type,
                               eq_needs={"SAU_C19": 7.0, "JPN_A01": 7.0}, inventory={})
    firms = {"ref": firm("JPN", {"SAU_B06": 0.5, "IRQ_B06": 0.2, "JPN_C28": 0.1}, {"SAU_B06": 14.0, "IRQ_B06": 7.0, "JPN_C28": 1.0}),
             "zero": firm("JPN", {"SAU_B06": 0.0}, {"SAU_B06": 0.0}),
             "kor": firm("KOR", {"SAU_B06": 0.5}, {"SAU_B06": 14.0})}
    hhs = {"h": hh("JPN", True), "nostock": hh("JPN", False), "gov": hh("JPN", True, "government")}
    d = StockInjection(region="JPN", input="B06", days=7, start_time=2, days_per_step=7.0)
    d.implement(firms, hhs)
    assert firms["ref"].inventory == {"SAU_B06": 1.0 + 14.0, "IRQ_B06": 1.0 + 7.0, "JPN_C28": 1.0}
    assert firms["zero"].inventory == {"SAU_B06": 1.0} and firms["kor"].inventory == {"SAU_B06": 1.0}
    assert d.n_agents == 1 and d.injected == pytest.approx(21.0)
    StockInjection(region="JPN", input="SAU_C19", days=14, days_per_step=7.0).implement(firms, hhs)
    assert hhs["h"].inventory == {"SAU_C19": 14.0} and hhs["nostock"].inventory == {} and hhs["gov"].inventory == {}
    with caplog.at_level(logging.WARNING):
        StockInjection(region="JPM", input="B06", days=7).implement(firms, hhs)
    assert "no-op" in caplog.text


@pytest.mark.parametrize("over, match", [({"start_time": None}, "start_time"), ({"days": -1}, "days"),
                                         ({"start_time": 0}, "start_time"), ({"days": True}, "days")])
def test_injection_config_is_validated(over, match):
    cfg = _injection(**over)
    if over.get("start_time", 1) is None:
        del cfg["start_time"]
    with pytest.raises(ValueError, match=match):
        parse_disruptions([cfg], None, None, {}, "mUSD", "week")


def test_injection_keeps_the_run_going_until_its_step():
    # the early stop waits for the last start_time: an injection in week 9 is not skipped
    ds = parse_disruptions([_injection(start_time=9)], None, None, {}, "mUSD", "week")
    assert max(d.start_time for d in ds) == 9 and ds[0].days_per_step == 7.0


# ----------------------------------------------------------------------
# Off by default, provenance
# ----------------------------------------------------------------------

def test_off_by_default(tk):
    assert tk["ap"].inventory_duration_targets_by_region == {}
    assert "inventory_duration_targets_by_region" not in tk["cfg"]
    m = _build(tk)
    ref = {pid: dict(f.inventory_duration_target) for pid, f in m["firms"].items()}
    load_inventories(m["firms"], m["ap"].inventory_duration_targets, "week", tk["common"]["sector_table"],
                     by_region={})
    assert ref == {pid: f.inventory_duration_target for pid, f in m["firms"].items()}


def test_new_keys_are_in_the_run_fingerprint_not_in_the_caches():
    assert "inventory_duration_targets_by_region" in WATERMARKED_CONFIG_KEYS
    assert "disruptions" in WATERMARKED_CONFIG_KEYS                    # the stock_injection entries
    assert all("inventory_duration_targets_by_region" not in keys for keys in _STAGE_CONFIG_KEYS.values())
    base = {"scope": "X", "seed": 1, "time_resolution": "week"}
    reg = dict(base, inventory_duration_targets_by_region={"JPN": {"B06": 60}},
               disruptions=[_injection()])
    fp = build_fingerprint(reg)
    assert fp["config"]["inventory_duration_targets_by_region"] == {"JPN": {"B06": 60}}
    assert fp["config"]["disruptions"][0]["type"] == "stock_injection"
    for stage in ("transport_network", "agents", "sc_network", "logistic_routes"):
        assert build_stage_fingerprint(reg, stage)["hash"] == build_stage_fingerprint(base, stage)["hash"]
