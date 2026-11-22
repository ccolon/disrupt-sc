"""Pool origins at the level of the buyer's region (input_pooling.origins: region; KI-89, 22 Nov 2026).

With the default pools a firm can only turn to the origins of its own (pruned) input mix: a firm whose gas
comes from one region has a one-member pool. widen_pools_to_region_origins spreads each firm's coefficient
of a pooled product over the origin shares of that product in its whole region, keeping the firm's total
coefficient and, per origin, the region's total demand.
"""
import math

from disruptsc.agents.firm import Firm
from disruptsc.init_pipeline.agents import load_input_pooling, widen_pools_to_region_origins
from disruptsc.run_pipeline.fingerprint import build_stage_fingerprint

POOLABLE = {"Gas", "Oil"}


def _firm(pid, region, sector, mix):
    f = Firm(pid=pid, region=region, sector=sector, sector_type="x", region_sector=f"{region}_{sector}")
    f.input_mix = dict(mix)
    return f


def _korea():
    # KOR Electricity buys its gas from Qatar only (pruned mix); KOR Industry from Qatar and EAS
    return {
        "e": _firm("e", "KOR", "Electricity", {"QAT_Gas": 0.02, "KOR_Coal": 0.2, "EAS_Machinery": 0.05}),
        "i": _firm("i", "KOR", "Industry", {"QAT_Gas": 0.01, "EAS_Gas": 0.03, "RoW_imports": 0.1}),
        "j": _firm("j", "JPN", "Electricity", {"RoW_Gas": 0.04}),
    }


WEIGHT = {"KOR_Electricity": 1000.0, "KOR_Industry": 2000.0, "JPN_Electricity": 500.0}


def _demand(firms, region, origin):
    return sum(f.input_mix.get(origin, 0.0) * WEIGHT[f.region_sector] for f in firms.values() if f.region == region)


def test_each_firm_takes_its_region_origin_shares():
    firms = _korea()
    before = {o: _demand(firms, "KOR", o) for o in ("QAT_Gas", "EAS_Gas")}
    added = widen_pools_to_region_origins(firms, POOLABLE, WEIGHT)
    # KOR gas demand: QAT 0.02*1000 + 0.01*2000 = 40, EAS 0.03*2000 = 60 -> shares 0.4 / 0.6
    assert math.isclose(firms["e"].input_mix["QAT_Gas"], 0.02 * 0.4)
    assert math.isclose(firms["e"].input_mix["EAS_Gas"], 0.02 * 0.6)
    assert math.isclose(firms["i"].input_mix["QAT_Gas"], 0.04 * 0.4)
    assert math.isclose(firms["i"].input_mix["EAS_Gas"], 0.04 * 0.6)
    assert added == 1                                            # EAS_Gas is new for the electricity firm
    for o, d in before.items():                                  # the region's demand per origin is unchanged
        assert math.isclose(_demand(firms, "KOR", o), d)
    # other products, import bundles and other regions are untouched
    assert firms["e"].input_mix["KOR_Coal"] == 0.2 and firms["e"].input_mix["EAS_Machinery"] == 0.05
    assert firms["i"].input_mix["RoW_imports"] == 0.1
    assert firms["j"].input_mix == {"RoW_Gas": 0.04}


def test_the_widened_pool_holds_every_origin():
    firms = _korea()
    widen_pools_to_region_origins(firms, POOLABLE, WEIGHT)
    load_input_pooling(firms, POOLABLE)
    members = sorted(i for i, p in firms["e"].input_pools.items() if p == "Gas")
    assert members == ["EAS_Gas", "QAT_Gas"]                     # before: QAT_Gas alone


def test_applying_twice_changes_nothing():
    firms = _korea()
    widen_pools_to_region_origins(firms, POOLABLE, WEIGHT)
    once = {k: dict(f.input_mix) for k, f in firms.items()}
    assert widen_pools_to_region_origins(firms, POOLABLE, WEIGHT) == 0
    assert {k: f.input_mix for k, f in firms.items()} == once


def test_a_firm_alone_in_its_sector_does_not_supply_itself():
    firms = {
        "g": _firm("g", "KOR", "Gas", {"QAT_Gas": 0.1}),
        "e": _firm("e", "KOR", "Electricity", {"KOR_Gas": 0.05, "QAT_Gas": 0.05}),
    }
    w = {"KOR_Gas": 100.0, "KOR_Electricity": 100.0}
    widen_pools_to_region_origins(firms, POOLABLE, w)
    assert "KOR_Gas" not in firms["g"].input_mix                 # its own region_sector left out
    assert math.isclose(sum(firms["g"].input_mix.values()), 0.1) # total kept, all on QAT
    assert math.isclose(firms["e"].input_mix["KOR_Gas"], 0.1 * 5 / 20)   # KOR demand: KOR 5, QAT 15


def test_the_option_is_a_cache_key_only_when_set():
    base = {"scope": "X", "filepaths": {}, "input_pooling": {"enabled": True}}
    region = {"scope": "X", "filepaths": {}, "input_pooling": {"enabled": True, "origins": "region"}}
    for stage in ("agents", "sc_network", "logistic_routes"):
        assert build_stage_fingerprint(base, stage)["hash"] != build_stage_fingerprint(region, stage)["hash"]
    assert (build_stage_fingerprint(base, "transport_network")["hash"]
            == build_stage_fingerprint(region, "transport_network")["hash"])
    no_key = {"scope": "X", "filepaths": {}}
    assert (build_stage_fingerprint(no_key, "agents")["payload"]["config"].keys()
            == build_stage_fingerprint(base, "agents")["payload"]["config"].keys())
