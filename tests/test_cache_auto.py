"""`--cache auto`: a stage is reused when its sidecar hash matches the current
stage fingerprint; routes only when every upstream stage is reused."""

from __future__ import annotations

import disruptsc.run_pipeline.cache as cache_mod
from disruptsc.run_pipeline.cache import (
    CACHE_LEVELS, cache_is_current, resolve_auto_cache_flags, save_cache,
)


def test_sidecar_and_auto_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "get_cache_dir", lambda: tmp_path)
    fps = {level: {"hash": f"h_{level}", "payload": {}} for level in CACHE_LEVELS}
    for level in CACHE_LEVELS:
        save_cache(level, {"x": 1}, scope="T", stage_fp=fps[level])
    assert all(cache_is_current(level, "T", fps[level]) for level in CACHE_LEVELS)
    flags = resolve_auto_cache_flags("T", fps)
    assert all(flags.values())

    # a cost change: transport fingerprint differs, agents/sc keep theirs
    changed = dict(fps); changed["transport_network"] = {"hash": "other", "payload": {}}
    changed["logistic_routes"] = {"hash": "other2", "payload": {}}
    flags = resolve_auto_cache_flags("T", changed)
    assert flags == {"transport_network": False, "agents": True, "sc_network": True, "logistic_routes": False}

    # routes current but an upstream stage stale -> routes are not reused
    stale_agents = dict(fps); stale_agents["agents"] = {"hash": "new_agents", "payload": {}}
    flags = resolve_auto_cache_flags("T", stale_agents)
    assert flags["agents"] is False and flags["logistic_routes"] is False and flags["transport_network"] is True

    # missing cache / missing sidecar
    assert cache_is_current("agents", "OTHER", fps["agents"]) is False
    (tmp_path / "T_agents.fp.json").unlink()
    assert cache_is_current("agents", "T", fps["agents"]) is False
