"""Stage caches must survive a logistics-cost change (agents and the supply
chain do not depend on costs) but not a change of the cargo mapping, the
network files, or anything the routes depend on."""

from __future__ import annotations

import copy

from disruptsc.run_pipeline.fingerprint import build_stage_fingerprint

BASE = {
    "scope": "X",
    "time_resolution": "week", "transport_modes": ["roads", "maritime"], "use_cargo_types": True,
    "logistics": {"basic_cost": {"roads": 0.05}, "cost_of_time": 0.5,
                  "sector_to_cargo_type": {"default": "container", "mining": "dry_bulk"}},
    "flow_coverage": 0.9, "seed": 1,
    "filepaths": {"transport": "T.gpkg", "multimodal": "M.gpkg", "mrio": "mrio.csv"},
}


def _hashes(cfg):
    return {st: build_stage_fingerprint(cfg, st)["hash"]
            for st in ("transport_network", "agents", "sc_network", "logistic_routes")}


def test_cost_change_keeps_agents_and_sc_caches():
    a = _hashes(BASE)
    cfg = copy.deepcopy(BASE); cfg["logistics"]["basic_cost"]["roads"] = 0.07
    b = _hashes(cfg)
    assert a["transport_network"] != b["transport_network"]
    assert a["logistic_routes"] != b["logistic_routes"]
    assert a["agents"] == b["agents"]
    assert a["sc_network"] == b["sc_network"]


def test_cargo_mapping_change_invalidates_sc_cache():
    a = _hashes(BASE)
    cfg = copy.deepcopy(BASE); cfg["logistics"]["sector_to_cargo_type"]["mining"] = "container"
    b = _hashes(cfg)
    assert a["agents"] != b["agents"] and a["sc_network"] != b["sc_network"]


def test_geometry_change_invalidates_everything():
    a = _hashes(BASE)
    for key, val in (("transport_modes", ["roads"]), ("time_resolution", "day")):
        cfg = copy.deepcopy(BASE); cfg[key] = val
        b = _hashes(cfg)
        assert all(a[st] != b[st] for st in a), key
    cfg = copy.deepcopy(BASE); cfg["filepaths"]["transport"] = "T2.gpkg"
    b = _hashes(cfg)
    assert all(a[st] != b[st] for st in a)


def test_seed_change_keeps_transport_and_agents():
    a = _hashes(BASE)
    cfg = copy.deepcopy(BASE); cfg["seed"] = 2
    b = _hashes(cfg)
    assert a["transport_network"] == b["transport_network"] and a["agents"] == b["agents"]
    assert a["sc_network"] != b["sc_network"]


def test_same_name_data_edit_invalidates_agents(tmp_path):
    """KI-47 (24 Sep + 3 Nov 2026): editing a data file IN PLACE, same
    filename, must invalidate the agents stage - and mtime churn alone
    (OneDrive sync, git checkout) must not."""
    import os
    import time

    from disruptsc.run_pipeline.fingerprint import _content_sha

    f = tmp_path / "firms.geojson"
    f.write_text('{"features": 1}')
    cfg = copy.deepcopy(BASE)
    cfg["filepaths"]["firms_spatial"] = str(f)
    a = _hashes(cfg)

    _content_sha.cache_clear()
    os.utime(f, (time.time() + 9999, time.time() + 9999))
    assert _hashes(cfg) == a  # mtime-only churn reuses every cache

    _content_sha.cache_clear()
    f.write_text('{"features": 2}')
    b = _hashes(cfg)
    assert a["agents"] != b["agents"]
    assert a["logistic_routes"] != b["logistic_routes"]
    assert a["transport_network"] == b["transport_network"]
