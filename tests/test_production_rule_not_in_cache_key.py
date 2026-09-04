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
