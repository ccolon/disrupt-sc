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

def _pkl(name: str, scope: str | None = None) -> Path:
    # Scope-keyed filenames: without the scope prefix, `disruptsc ECA --cache …`
    # after an Ecuador run silently loaded Ecuador's pickles. scope=None keeps
    # the legacy unscoped name for old callers.
    stem = f"{scope}_{name}" if scope else name
    return get_cache_dir() / f"{stem}.pkl"


def save_cache(name: str, data: dict, scope: str | None = None,
               stage_fp: dict | None = None):
    path = _pkl(name, scope)
    payload = {"__cache_format__": 2, "fingerprint": stage_fp, "data": data}
    with open(path, "wb") as f:
        # Pin to HIGHEST_PROTOCOL (= protocol 5 on Python 3.8+) explicitly so
        # behavior doesn't drift if the default ever changes. Protocol 5
        # supports out-of-band buffers and is more efficient for the large
        # numpy/pandas blobs we serialize.
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    logging.info(f"Cached {name} → {path}")


def load_cache(name: str, scope: str | None = None,
               stage_fp: dict | None = None) -> dict:
    """Load one cache stage, validating its stored stage fingerprint.

    A cache built under a different configuration (any watermarked key of
    this stage or an earlier one) is REFUSED with a key-level diff — the
    silent alternative is a run whose parameters are partly the YAML's and
    partly whatever the pickle was built with. Old-format caches (no stored
    fingerprint) load with a warning; delete them to silence it.
    """
    path = _pkl(name, scope)
    if not path.exists():
        raise FileNotFoundError(
            f"No cache for stage '{name}'"
            + (f" (scope {scope})" if scope else "")
            + f" at {path}. Run once without --cache to build it."
        )
    with open(path, "rb") as f:
        raw = pickle.load(f)
    if isinstance(raw, dict) and raw.get("__cache_format__") == 2:
        data, stored = raw["data"], raw.get("fingerprint")
    else:
        data, stored = raw, None
    if stage_fp is not None:
        if stored is None:
            logging.warning(
                f"Cache {path.name} predates fingerprint validation — using it "
                f"UNVERIFIED. Rebuild without --cache to upgrade it."
            )
        elif stored.get("hash") != stage_fp.get("hash"):
            from disruptsc.run_pipeline.fingerprint import diff_fingerprints
            diff = diff_fingerprints({"payload": stored.get("payload") or {}},
                                     stage_fp.get("payload") or {})
            raise RuntimeError(
                f"Cache {path.name} was built under a DIFFERENT configuration; "
                f"refusing to reuse it.\nChanged keys:\n{diff}\n"
                f"Drop the --cache flag (or delete {path}) to rebuild."
            )
    logging.info(f"Loaded cache {name} ← {path}")
    return data


# ------------------------------------------------------------------
# Level-specific helpers (thin wrappers for clarity)
# ------------------------------------------------------------------
# scope/stage_fp default to None so legacy callers (e.g. older study
# scripts reading unscoped, unvalidated caches) keep working.

def cache_transport_network(transport_network, transport_edges, transport_nodes,
                            scope=None, stage_fp=None):
    save_cache("transport_network", {
        "transport_network": transport_network,
        "transport_edges": transport_edges,
        "transport_nodes": transport_nodes,
    }, scope=scope, stage_fp=stage_fp)


def load_cached_transport_network(scope=None, stage_fp=None):
    d = load_cache("transport_network", scope=scope, stage_fp=stage_fp)
    return d["transport_network"], d["transport_edges"], d["transport_nodes"]


def cache_agents(firms, households, countries, mrio, sector_table,
                 firm_table, household_table, scope=None, stage_fp=None):
    save_cache("agents", {
        "firms": firms, "households": households, "countries": countries,
        "mrio": mrio, "sector_table": sector_table,
        "firm_table": firm_table, "household_table": household_table,
    }, scope=scope, stage_fp=stage_fp)


def load_cached_agents(scope=None, stage_fp=None):
    d = load_cache("agents", scope=scope, stage_fp=stage_fp)
    return (d["mrio"], d["sector_table"], d["firms"], d["firm_table"],
            d["households"], d["household_table"], d["countries"])


def cache_sc_network(sc_network, firms, households, countries,
                     scope=None, stage_fp=None):
    save_cache("sc_network", {
        "sc_network": sc_network, "firms": firms,
        "households": households, "countries": countries,
    }, scope=scope, stage_fp=stage_fp)


def load_cached_sc_network(scope=None, stage_fp=None):
    d = load_cache("sc_network", scope=scope, stage_fp=stage_fp)
    return d["sc_network"], d["firms"], d["households"], d["countries"]


def cache_logistic_routes(sc_network, transport_network, commercial_link_table,
                          firms, households, countries, scope=None, stage_fp=None):
    save_cache("logistic_routes", {
        "sc_network": sc_network, "transport_network": transport_network,
        "commercial_link_table": commercial_link_table,
        "firms": firms, "households": households, "countries": countries,
    }, scope=scope, stage_fp=stage_fp)


def load_cached_logistic_routes(scope=None, stage_fp=None):
    d = load_cache("logistic_routes", scope=scope, stage_fp=stage_fp)
    return (d["sc_network"], d["transport_network"],
            d["commercial_link_table"],
            d["firms"], d["households"], d["countries"])
