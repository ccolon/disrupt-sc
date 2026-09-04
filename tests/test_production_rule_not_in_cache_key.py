"""The production-rule parameters are re-applied on cache load, not baked into the caches.

`critical_input_threshold` and the `input_criticality` matrix decide how a firm's output binds
to its inputs; they do not change which firms exist or how the supply chain is wired. On the EU
scope a sensitivity on them used to rebuild agents, supply chain and routes (~1 h per run).
"""

from disruptsc.run_pipeline.fingerprint import build_stage_fingerprint, _STAGE_CONFIG_KEYS, _STAGE_FILEPATH_KEYS


def _config(**over):
    c = {"scope": "Testkistan", "seed": 1, "time_resolution": "week", "transport_modes": ["roads"],
         "use_cargo_types": False, "flow_coverage": 0.9, "nb_suppliers_per_input": 2,
         "critical_input_threshold": 0.02, "filepaths": {"mrio": "a.csv", "input_criticality": None}}
    c.update(over)
    return c


def test_keys_are_not_part_of_the_agents_stage():
    assert "critical_input_threshold" not in _STAGE_CONFIG_KEYS["agents"]
    assert "input_criticality" not in _STAGE_FILEPATH_KEYS["agents"]


def test_changing_them_keeps_every_stage_fingerprint():
    base = {stage: build_stage_fingerprint(_config(), stage)["hash"]
            for stage in ("transport_network", "agents", "sc_network", "logistic_routes")}
    thr = _config(critical_input_threshold=0.10)
    crit = _config(filepaths={"mrio": "a.csv", "input_criticality": "crit.csv"})
    for stage, h in base.items():
        assert build_stage_fingerprint(thr, stage)["hash"] == h
        assert build_stage_fingerprint(crit, stage)["hash"] == h
    # a real build input still invalidates
    assert build_stage_fingerprint(_config(flow_coverage=0.8), "agents")["hash"] != base["agents"]


def test_switching_costs_do_not_invalidate_any_stage():
    base = _config(logistics={"basic_cost": {"roads": 0.05}, "switching_costs": {"modal_switch": 0.15}})
    changed = _config(logistics={"basic_cost": {"roads": 0.05},
                                 "switching_costs": {"modal_switch": {"default": 0.15, "dry_bulk": 1000}}})
    for stage in ("transport_network", "agents", "sc_network", "logistic_routes"):
        assert build_stage_fingerprint(changed, stage)["hash"] == build_stage_fingerprint(base, stage)["hash"]
    # a line-haul cost change still invalidates the transport network and the routes
    costlier = _config(logistics={"basic_cost": {"roads": 0.06}, "switching_costs": {"modal_switch": 0.15}})
    assert build_stage_fingerprint(costlier, "transport_network")["hash"] != build_stage_fingerprint(base, "transport_network")["hash"]


import pytest


def test_import_bundles_get_an_inventory_target():
    # "{BLOC}_imports" keys are created after load_inventories ran on the agents;
    # they must receive the `imports` value (or the default), not one time step.
    import pandas as pd
    from disruptsc.init_pipeline.agents import load_inventories

    class F:
        def __init__(self, mix):
            self.input_mix = mix
            self.inventory_duration_target = {}

    sector_table = pd.DataFrame({"sector": ["A01", "C19"], "type": ["agriculture", "oil_and_gas"]})
    firms = {"f": F({"DEU_A01": 0.2, "DEU_C19": 0.3, "RUS_imports": 0.5})}
    load_inventories(firms, {"definition": "per_input_type", "unit": "day",
                             "values": {"default": 30, "agriculture": 15}}, "week", sector_table)
    t = firms["f"].inventory_duration_target
    import pytest
    assert t["DEU_A01"] == pytest.approx(15 / 7) and t["DEU_C19"] == pytest.approx(30 / 7)
    assert t["RUS_imports"] == pytest.approx(30 / 7)
    load_inventories(firms, {"definition": "per_input_type", "unit": "day",
                             "values": {"default": 30, "imports": 45}}, "week", sector_table)
    assert firms["f"].inventory_duration_target["RUS_imports"] == pytest.approx(45 / 7)


def test_import_bundles_resolve_criticality_and_inventory_from_their_composition():
    import pandas as pd
    from disruptsc.init_pipeline.agents import load_inventories, load_input_criticality

    class F:
        def __init__(self, mix):
            self.input_mix = mix
            self.region, self.sector, self.region_sector = "DEU", "C19", "DEU_C19"
            self.inventory_duration_target = {}
            self.input_criticality = {}

    sector_table = pd.DataFrame({"sector": ["A01", "B06", "C19", "C28"], "type": ["agriculture", "mining", "oil_and_gas", "manufacturing"]})
    firms = {"f": F({"DEU_A01": 0.2, "RUS_imports": 0.5, "USA_imports": 0.3})}
    # RUS sends crude (B06) and machinery (C28) 80/20; USA is unknown -> fallback
    shares = {("DEU", "C19"): {"RUS": {"B06": 0.8, "C28": 0.2}}}
    crit = pd.DataFrame(1.0, index=["A01", "B06", "C19", "C28"], columns=["A01", "B06", "C19", "C28"])
    crit.loc["C28", "C19"] = 0.0     # machinery is non-critical for refining
    crit.loc["A01", "C19"] = 0.5
    load_input_criticality(firms, crit, bundle_shares=shares)
    w = firms["f"].input_criticality
    assert w["DEU_A01"] == 0.5 and w["RUS_imports"] == pytest.approx(0.8 * 1.0 + 0.2 * 0.0) and w["USA_imports"] == 1.0
    load_inventories(firms, {"definition": "per_input_type", "unit": "day",
                             "values": {"default": 30, "mining": 40, "manufacturing": 10, "imports": 20}},
                     "week", sector_table, bundle_shares=shares)
    t = firms["f"].inventory_duration_target
    assert t["RUS_imports"] == pytest.approx((0.8 * 40 + 0.2 * 10) / 7) and t["USA_imports"] == pytest.approx(20 / 7)


def test_inventory_targets_do_not_invalidate_the_agents_stage():
    base = _config(inventory_duration_targets={"definition": "per_input_type", "values": {"default": 30}})
    other = _config(inventory_duration_targets={"definition": "per_buying_sector", "values": {"default": 20, "C19": 12}})
    for stage in ("agents", "sc_network", "logistic_routes"):
        assert build_stage_fingerprint(other, stage)["hash"] == build_stage_fingerprint(base, stage)["hash"]


def test_per_buying_sector_inventories_with_overrides_and_bundles():
    import pandas as pd
    from disruptsc.init_pipeline.agents import load_inventories

    class F:
        def __init__(self, sector, mix):
            self.region, self.sector, self.region_sector = "DEU", sector, f"DEU_{sector}"
            self.input_mix = mix
            self.inventory_duration_target = {}

    sector_table = pd.DataFrame({"sector": ["A01", "B05", "B06", "C19", "C28", "D", "G", "H49"],
                                 "type": ["agriculture", "mining", "mining", "oil_and_gas", "manufacturing", "utility", "trade", "transport"]})
    targets = {"definition": "per_buying_sector", "unit": "day", "service_days": 90,
               "values": {"default": 30, "C19": 12, "D": 20, "C10T12": 18},
               "overrides": {"*": {"D": 2, "utility": 2}, "D": {"B05": 30, "B06": 2}, "C19": {"B06": 12}, "C10T12": {"A01": 10}}}
    refinery = F("C19", {"NOR_B06": 0.5, "DEU_C28": 0.1, "DEU_D": 0.05, "DEU_G": 0.05, "RUS_imports": 0.3})
    plant = F("D", {"DEU_B05": 0.4, "DEU_B06": 0.3, "DEU_H49": 0.1})
    mill = F("C10T12", {"DEU_A01": 0.6, "DEU_C28": 0.1})
    shares = {("DEU", "C19"): {"RUS": {"B06": 0.75, "C28": 0.25}}}
    load_inventories({"r": refinery, "p": plant, "m": mill}, targets, "week", sector_table, bundle_shares=shares)
    r = refinery.inventory_duration_target
    assert r["NOR_B06"] == pytest.approx(12 / 7)            # buyer override
    assert r["DEU_C28"] == pytest.approx(12 / 7)            # buyer's goods-input days
    assert r["DEU_D"] == pytest.approx(2 / 7)               # non-storable utility (any buyer)
    assert r["DEU_G"] == pytest.approx(90 / 7)              # service input: coping duration
    assert r["RUS_imports"] == pytest.approx((0.75 * 12 + 0.25 * 12) / 7)
    p = plant.inventory_duration_target
    assert p["DEU_B05"] == pytest.approx(30 / 7) and p["DEU_B06"] == pytest.approx(2 / 7) and p["DEU_H49"] == pytest.approx(90 / 7)
    m = mill.inventory_duration_target
    assert m["DEU_A01"] == pytest.approx(10 / 7) and m["DEU_C28"] == pytest.approx(18 / 7)
