"""State-fingerprinting for resumable runs (criticality, Monte-Carlo).

A *fingerprint* captures everything that, if changed between two runs,
would invalidate already-computed results: code version, RNG seed, the
subset of config keys that drives agent / SC / route construction, and
the **filepaths** of the input data. We deliberately do not hash file
contents — it's the user's responsibility to bump the filename when the
data changes (e.g. ``mrio_oecd_2022.csv`` → ``mrio_oecd_2022_v2.csv``).
That keeps resume checks O(microseconds) rather than O(seconds).

Typical usage::

    payload = build_fingerprint(config, criticality_duration=duration)
    digest = fingerprint_hash(payload)
    save_fingerprint(payload, sidecar_path)

    prev = load_fingerprint(sidecar_path)
    if prev and prev["hash"] != digest:
        raise RuntimeError(diff_fingerprints(prev, payload))
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path

from disruptsc._version import __version__


# Keys whose value contributes to the fingerprint. Everything that
# changes the agent set, the supply-chain graph, or the routing problem.
WATERMARKED_CONFIG_KEYS = (
    # Economic filtering
    "flow_coverage",
    "sectors_to_include",
    "sectors_to_exclude",
    "countries_no_transport",
    "country_attachment",
    "countries_to_include",
    # Transport / routing
    "use_cargo_types",
    "transport_modes",
    "capacity_constraint",
    "transport_to_households",
    "sectors_no_transport_network",
    "with_transport",
    "price_increase_threshold",
    "rationing_mode",
    # Units & resolution
    "monetary_units_in_data",
    "monetary_units_in_model",
    "time_resolution",
    # Agent / SC params
    "nb_suppliers_per_input",
    "weight_localization_firm",
    "weight_localization_household",
    "country_transport_share",
    "firm_transport_share",
    "utilization_rate",
    "critical_input_threshold",
    "capital_to_value_added_ratio",
    "inventory_duration_targets",
    "inventory_restoration_time",
    "enable_household_inventories",
    "firm_data_type",
    "explicit_service_firm",
    # Reproducibility
    "seed",
    # Full logistics block (cost coefficients, speeds, switching costs…)
    "logistics",
    # Capacity overrides directly affect routing
    "default_transport_capacity",
    "transport_capacity_overrides",
)

# Filepath keys to include in the fingerprint. Values stored verbatim
# (as strings) — user is responsible for renaming when content changes.
WATERMARKED_FILEPATH_KEYS = (
    "mrio",
    "sector_table",
    "transport",
    "multimodal",
    "households_spatial",
    "firms_spatial",
    "countries_spatial",
    "input_criticality",
)


# ---------------------------------------------------------------------------
# Per-stage fingerprints for the pickle caches (run_pipeline/cache.py)
# ---------------------------------------------------------------------------
# Each cache stage is invalidated by the config keys that shape what it
# builds, plus everything an earlier stage depends on (agents are placed on
# transport nodes, the SC network wires those agents, routes serve that
# network) — so the key sets are CUMULATIVE down the pipeline. Deliberately
# NOT included: run-time parameters that do not change the build (t_final,
# epsilon_stop, simulation_type, disruptions, the household-inventory config
# — which is re-applied on every cache load), and the code version/git SHA
# (same contract as filenames-not-contents above: caches survive commits;
# delete tmp/ after a change that alters build behavior).

_STAGE_ORDER = ("transport_network", "agents", "sc_network", "logistic_routes")

_STAGE_CONFIG_KEYS = {
    "transport_network": (
        "time_resolution", "transport_modes", "use_cargo_types",
        "logistics", "default_transport_capacity", "transport_capacity_overrides",
    ),
    "agents": (
        "monetary_units_in_data", "monetary_units_in_model",
        "flow_coverage", "sectors_to_include", "sectors_to_exclude",
        "countries_to_include", "countries_no_transport", "country_attachment",
        "firm_data_type",
        "explicit_service_firm", "utilization_rate", "critical_input_threshold",
        "inventory_duration_targets", "inventory_restoration_time",
        "capital_to_value_added_ratio", "country_transport_share",
        "firm_transport_share",
    ),
    "sc_network": (
        "nb_suppliers_per_input", "weight_localization_firm",
        "weight_localization_household", "seed",
        "with_transport", "transport_to_households", "sectors_no_transport_network",
    ),
    "logistic_routes": (
        "capacity_constraint", "capacity_routing_max_iterations",
        "price_increase_threshold", "use_route_cache",
    ),
}

_STAGE_FILEPATH_KEYS = {
    "transport_network": ("transport", "multimodal"),
    "agents": ("mrio", "sector_table", "households_spatial", "firms_spatial",
               "countries_spatial", "input_criticality"),
    "sc_network": (),
    "logistic_routes": (),
}


def build_stage_fingerprint(config: dict, stage: str) -> dict:
    """Return ``{"hash", "payload"}`` for one cache stage.

    The payload covers the stage's own keys plus every earlier stage's
    (cumulative — later stages are built from earlier stages' outputs).
    A per-stage subset, rather than the full run fingerprint, keeps the
    legitimate sweep pattern working: changing e.g. the seed invalidates
    the sc_network cache but NOT the transport-network cache.
    """
    idx = _STAGE_ORDER.index(stage)
    cfg_keys: list = []
    fp_keys: list = []
    for s in _STAGE_ORDER[: idx + 1]:
        cfg_keys += list(_STAGE_CONFIG_KEYS[s])
        fp_keys += list(_STAGE_FILEPATH_KEYS[s])
    filepaths = config.get("filepaths") or {}
    payload = {
        "stage": stage,
        "scope": config.get("scope"),
        "config": {k: config.get(k) for k in cfg_keys},
        "filepaths": {k: _path_str(filepaths.get(k)) for k in fp_keys},
    }
    return {"hash": fingerprint_hash(payload), "payload": payload}


def _git_sha() -> str | None:
    """Return the current git HEAD SHA, or None if not in a git repo."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd=Path(__file__).resolve().parent,
            timeout=2,
        )
        return out.decode().strip()
    except (FileNotFoundError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired):
        return None


def _path_str(value) -> str | None:
    """Coerce a filepath-shaped value to a string for the fingerprint."""
    if value is None:
        return None
    return str(value)


def build_fingerprint(config: dict, *, criticality_duration: int | None = None) -> dict:
    """Return the fingerprint payload for the current run.

    *criticality_duration* is passed explicitly by the criticality path
    (so we don't have to peek into the already-parsed criticality
    sub-dict here); plain disruption/initial-state provenance stamps
    leave it None.
    """
    filepaths = config.get("filepaths") or {}
    payload = {
        "version": __version__,
        "git_sha": _git_sha(),
        "criticality_duration": criticality_duration,
        "config": {k: config.get(k) for k in WATERMARKED_CONFIG_KEYS},
        "filepaths": {k: _path_str(filepaths.get(k)) for k in WATERMARKED_FILEPATH_KEYS},
    }
    return payload


def fingerprint_hash(payload: dict) -> str:
    """Stable sha256 over a fingerprint payload (JSON-canonicalized)."""
    blob = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()


def save_fingerprint(payload: dict, path: Path) -> None:
    """Write the fingerprint + its hash to *path* as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = {"hash": fingerprint_hash(payload), "payload": payload}
    path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))


def load_fingerprint(path: Path) -> dict | None:
    """Return the persisted fingerprint dict (with keys ``hash`` and
    ``payload``), or ``None`` if no sidecar exists."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logging.warning(f"Could not read fingerprint sidecar {path}: {exc}")
        return None


def diff_fingerprints(prev: dict, current_payload: dict) -> str:
    """Human-readable diff between a persisted fingerprint and the
    current payload, listing only keys whose values changed."""
    prev_payload = prev.get("payload") or {}
    lines = []
    keys = sorted(set(prev_payload) | set(current_payload))
    for k in keys:
        old = prev_payload.get(k)
        new = current_payload.get(k)
        if old == new:
            continue
        if isinstance(old, dict) and isinstance(new, dict):
            sub_keys = sorted(set(old) | set(new))
            for sk in sub_keys:
                if old.get(sk) != new.get(sk):
                    lines.append(f"  {k}.{sk}: was={old.get(sk)!r}  now={new.get(sk)!r}")
        else:
            lines.append(f"  {k}: was={old!r}  now={new!r}")
    return "\n".join(lines) or "  (hashes differ but no key-level diff — check git_sha/version)"
