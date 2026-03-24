"""4-level pickle caching for expensive initialization stages."""

from __future__ import annotations

import logging
import pickle
from pathlib import Path


# ------------------------------------------------------------------
# Cache directory
# ------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TMP_FOLDER = _ROOT / "tmp"

_isolated_dir: Path | None = None


def setup_cache_isolation(scope: str):
    """Create a process-private cache directory."""
    global _isolated_dir
    import os, time
    name = f"{scope}_pid_{os.getpid()}_{round(time.time() * 1000)}"
    _isolated_dir = TMP_FOLDER / name
    _isolated_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Isolated cache: {_isolated_dir}")


def get_cache_dir() -> Path:
    if _isolated_dir:
        return _isolated_dir
    TMP_FOLDER.mkdir(parents=True, exist_ok=True)
    return TMP_FOLDER


# ------------------------------------------------------------------
# Parse CLI cache argument → dict of booleans
# ------------------------------------------------------------------

CACHE_LEVELS = ("transport_network", "agents", "sc_network", "logistic_routes")

_PRESETS = {
    "same_transport_network_new_agents":       (True,  False, False, False),
    "same_agents_new_sc_network":              (True,  True,  False, False),
    "same_sc_network_new_logistic_routes":     (True,  True,  True,  False),
    "same_logistic_routes":                    (True,  True,  True,  True),
}


def parse_cache_arg(arg: str | None) -> dict[str, bool]:
    """Return {level: use_cache} from a CLI string (or None)."""
    base = {k: False for k in CACHE_LEVELS}
    if not arg:
        return base
    if arg not in _PRESETS:
        raise ValueError(f"Unknown cache preset '{arg}'. Options: {list(_PRESETS)}")
    for level, flag in zip(CACHE_LEVELS, _PRESETS[arg]):
        base[level] = flag
    return base


# ------------------------------------------------------------------
# Save / load helpers
# ------------------------------------------------------------------

def _pkl(name: str) -> Path:
    return get_cache_dir() / f"{name}.pkl"


def save_cache(name: str, data: dict):
    path = _pkl(name)
    with open(path, "wb") as f:
        pickle.dump(data, f)
    logging.info(f"Cached {name} → {path}")


def load_cache(name: str) -> dict:
    path = _pkl(name)
    with open(path, "rb") as f:
        data = pickle.load(f)
    logging.info(f"Loaded cache {name} ← {path}")
    return data


# ------------------------------------------------------------------
# Level-specific helpers (thin wrappers for clarity)
# ------------------------------------------------------------------

def cache_transport_network(transport_network, transport_edges, transport_nodes):
    save_cache("transport_network", {
        "transport_network": transport_network,
        "transport_edges": transport_edges,
        "transport_nodes": transport_nodes,
    })


def load_cached_transport_network():
    d = load_cache("transport_network")
    return d["transport_network"], d["transport_edges"], d["transport_nodes"]


def cache_agents(firms, households, countries, mrio, sector_table,
                 firm_table, household_table):
    save_cache("agents", {
        "firms": firms, "households": households, "countries": countries,
        "mrio": mrio, "sector_table": sector_table,
        "firm_table": firm_table, "household_table": household_table,
    })


def load_cached_agents():
    d = load_cache("agents")
    return (d["mrio"], d["sector_table"], d["firms"], d["firm_table"],
            d["households"], d["household_table"], d["countries"])


def cache_sc_network(sc_network, firms, households, countries):
    save_cache("sc_network", {
        "sc_network": sc_network, "firms": firms,
        "households": households, "countries": countries,
    })


def load_cached_sc_network():
    d = load_cache("sc_network")
    return d["sc_network"], d["firms"], d["households"], d["countries"]


def cache_logistic_routes(sc_network, transport_network, commercial_link_table,
                          firms, households, countries):
    save_cache("logistic_routes", {
        "sc_network": sc_network, "transport_network": transport_network,
        "commercial_link_table": commercial_link_table,
        "firms": firms, "households": households, "countries": countries,
    })


def load_cached_logistic_routes():
    d = load_cache("logistic_routes")
    return (d["sc_network"], d["transport_network"],
            d["commercial_link_table"],
            d["firms"], d["households"], d["countries"])
