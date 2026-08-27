"""Load YAML configuration and build scoped parameter bundles."""

import logging
import os
from datetime import datetime
from pathlib import Path

import yaml

from disruptsc import paths
from disruptsc.params import TransportParams, SimParams, AgentParams, LogisticsParams

EPSILON = 1e-6
SIMU_TYPES_WITH_EXPORT = ("initial_state", "disruption")


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def _merge_dicts(base: dict, overrides: dict):
    """Recursively merge overrides into base (mutates base)."""
    for key, val in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _merge_dicts(base[key], val)
        else:
            base[key] = val


def load_config(scope: str, parameter_folder: Path = None) -> dict:
    """Load default.yaml, overlay user_defined_<scope>.yaml then .local.yaml.

    Both the shared and the local file are optional. The shared file
    (``user_defined_<scope>.yaml``) is committed; the local file
    (``user_defined_<scope>.local.yaml``) is gitignored and overlays the
    shared one. If neither exists, only defaults are used.
    """
    parameter_folder = parameter_folder or paths.PARAMETER_FOLDER

    with open(parameter_folder / "default.yaml", "r") as f:
        config = yaml.safe_load(f)

    user_file = parameter_folder / f"user_defined_{scope}.yaml"
    local_file = parameter_folder / f"user_defined_{scope}.local.yaml"

    for candidate, label in ((user_file, "user-defined"),
                              (local_file, "local override")):
        if os.path.exists(candidate):
            logging.info(f"Loading {label} parameters for {scope}: {candidate.name}")
            with open(candidate, "r") as f:
                overrides = yaml.safe_load(f)
            if overrides:
                _merge_dicts(config, overrides)

    if not user_file.exists() and not local_file.exists():
        logging.info(
            f"No user-defined or local parameter file for {scope}; using defaults"
        )

    config["scope"] = scope
    if config.get("events") and not config.get("disruptions"):
        logging.warning("'events' is deprecated; use 'disruptions' instead.")
        config["disruptions"] = config["events"]

    # Resolve filepaths to absolute. Plain relative values resolve against the
    # scope's data folder; a "repo:" prefix resolves against the code-repo root
    # instead (for inputs committed with the code, e.g. the input-criticality
    # matrix under studies/); absolute values pass through unchanged.
    for key, val in config.get("filepaths", {}).items():
        if val and val != "None":
            resolved = resolve_repo_prefix(val)
            if resolved is not val:
                config["filepaths"][key] = Path(resolved)
            else:
                config["filepaths"][key] = paths.get_data_path(scope) / val
        else:
            config["filepaths"][key] = None

    return config


def resolve_repo_prefix(value):
    """Resolve a ``repo:<relpath>`` string against the code-repo root.

    Any other value is returned unchanged (identity preserved, so callers can
    detect whether resolution happened). Used for config paths that point at
    files committed with the code rather than the data repo — e.g.
    ``repo:studies/earthquake/additional_data/earthquake_shock_modelready.csv``.
    """
    if isinstance(value, str) and value.startswith("repo:"):
        return str(paths.ROOT_FOLDER / value[len("repo:"):])
    return value


# ---------------------------------------------------------------------------
# Build param bundles from config dict
# ---------------------------------------------------------------------------

def _parse_capacity_constraint(raw) -> tuple[bool, str]:
    """Return (enabled, mode) from the capacity_constraint config value.

    Unknown values RAISE instead of silently enabling gradual mode — a typo
    on a scientifically active switch must fail loudly, not pass as a choice.
    """
    if isinstance(raw, bool):
        return raw, "gradual"
    if isinstance(raw, str):
        low = raw.lower()
        if low in ("off", "disabled", "false", "no"):
            return False, "gradual"
        if low in ("on", "true", "yes"):
            return True, "gradual"
        if low in ("gradual", "binary"):
            return True, low
    raise ValueError(
        f"capacity_constraint must be a bool, 'off', 'gradual', or 'binary' "
        f"(got {raw!r})"
    )


_DAYS_PER_TIMESTEP = {"day": 1, "week": 7, "month": 30, "year": 365}


def days_per_timestep(time_resolution: str) -> float:
    """Calendar days in one model time step (for day<->step unit conversion)."""
    return float(_DAYS_PER_TIMESTEP.get(time_resolution, 7))


def _parse_chunk_size(logistics: dict, time_resolution: str) -> float:
    """Convert chunk_size from tons/day (YAML) to tons/time-step."""
    raw = logistics.get("chunk_size", 1e9)
    return float(raw) * days_per_timestep(time_resolution)


_REMOVED_CUTOFFS = (
    "cutoff_sector_output", "cutoff_sector_demand", "combine_sector_cutoff",
    "cutoff_firm_output", "cutoff_household_demand",
    "min_nb_firms_per_sector", "pop_density_cutoff", "pop_cutoff",
    "local_demand_cutoff", "io_cutoff",
)


# Keys that were parsed but never consumed by the v2 runtime — setting them
# has no effect. Kept here so old configs surface a warning instead of a
# silent no-op.
_INERT_KEYS = (
    "congestion", "mc_caching", "logging_level", "flow_data",
    "route_optimization_weight", "admin",
)
_INERT_LOGISTICS_KEYS = ("variability", "variability_coef")


def _warn_removed_cutoff_params(config: dict) -> None:
    """Surface old cutoff keys that are silently ignored under flow_coverage."""
    present = [k for k in _REMOVED_CUTOFFS if k in config]
    if present:
        logging.warning(
            f"The following config keys are no longer used (replaced by "
            f"flow_coverage): {present}. Remove them from your YAML."
        )
    inert = [k for k in _INERT_KEYS if k in config]
    inert += [f"logistics.{k}" for k in _INERT_LOGISTICS_KEYS
              if k in (config.get("logistics") or {})]
    if inert:
        logging.warning(
            f"The following config keys have NO effect in v2 and are ignored: "
            f"{inert}. Remove them from your YAML."
        )


def _validated_flow_coverage(config: dict) -> float:
    """flow_coverage is the cumulative flow-coverage fraction in (0, 1].

    A single quantile knob: per-buyer and per-supplier top cells are
    kept until cumulative share ≥ flow_coverage; the union defines the
    agent and link sets. Replaces input_coverage / cutoff_sector_output /
    cutoff_sector_demand / cutoff_firm_output / cutoff_household_demand /
    combine_sector_cutoff.

    For backward compatibility, falls back to `input_coverage` if
    `flow_coverage` is absent — that lets old configs keep running while
    they get migrated.
    """
    raw = config.get("flow_coverage")
    if raw is None:
        legacy = config.get("input_coverage")
        if legacy is not None:
            logging.warning(
                "`input_coverage` is deprecated; rename it to `flow_coverage`. "
                "Using the old value for now."
            )
            raw = legacy
        else:
            raw = 0.95
    f = float(raw)
    if not (0 < f <= 1):
        raise ValueError(
            f"flow_coverage must be in (0, 1] (got {f}). "
            f"Typical values are 0.7–0.99."
        )
    return f


def build_params(config: dict) -> tuple[TransportParams, SimParams, AgentParams, LogisticsParams]:
    """Build frozen parameter bundles from a raw config dict."""
    logistics = config.get("logistics", {})
    cap_enabled, cap_mode = _parse_capacity_constraint(config.get("capacity_constraint", "off"))

    rationing_mode = config.get("rationing_mode", "equal")
    if rationing_mode not in ("equal", "household_first"):
        raise ValueError(
            f"rationing_mode must be 'equal' or 'household_first' (got {rationing_mode!r})"
        )

    transport_params = TransportParams(
        with_transport=config.get("with_transport", True),
        transport_to_households=config.get("transport_to_households", True),
        capacity_constraint_enabled=cap_enabled,
        capacity_constraint_mode=cap_mode,
        initial_route_assignment=logistics.get("initial_route_assignment", "heuristic"),
        rationing_mode=rationing_mode,
        use_route_cache=config.get("use_route_cache", True),
        switching_costs=logistics.get("switching_costs", {"modal_switch": 0.15, "port_switch": 0.05}),
        price_increase_threshold=config.get("price_increase_threshold", 2.0),
        sectors_no_transport=tuple(config.get("sectors_no_transport_network",
                                              ["utility", "transport", "trade", "services", "service", "construction"])),
        countries_no_transport=tuple(config.get("countries_no_transport") or ()),
        use_cargo_types=bool(config.get("use_cargo_types", True)),
        monetary_units=config.get("monetary_units_in_model", "mUSD"),
        chunk_size=_parse_chunk_size(logistics, config.get("time_resolution", "week")),
        route_candidate_count=int(logistics.get("route_candidate_count", 4)),
        route_candidate_stretch=float(logistics.get("route_candidate_stretch", 3.0)),
        route_candidate_overlap=float(logistics.get("route_candidate_overlap", 0.85)),
        lp_route_candidate_count=int(logistics.get("lp_route_candidate_count", 20)),
        lp_route_candidate_stretch=float(logistics.get("lp_route_candidate_stretch", 4.0)),
        lp_route_candidate_overlap=float(logistics.get("lp_route_candidate_overlap", 0.9)),
        lp_overcapacity_limit=float(logistics.get("lp_overcapacity_limit", 1.1)),
    )

    sim_params = SimParams(
        t_final=config.get("t_final", 10),
        epsilon_stop=float(config.get("epsilon_stop_condition", 1e-3)),
        time_resolution=config.get("time_resolution", "week"),
        simulation_type=config.get("simulation_type", "initial_state"),
        mc_repetitions=config.get("mc_repetitions", 0) or 0,
        propagate_input_price_change=config.get("propagate_input_price_change", True),
        adaptive_inventories=config.get("adaptive_inventories", False),
        adaptive_supplier_weight=config.get("adaptive_supplier_weight", False),
        capacity_constrained_orders=config.get("capacity_constrained_orders", False),
        time_to_activate_idle_capital=config.get("time_to_activate_idle_capital", 30.0),
        sensitivity=config.get("sensitivity") or {},
        seed=(int(config["seed"]) if config.get("seed") is not None else None),
    )

    # Warn loudly about removed legacy params so existing configs surface them.
    _warn_removed_cutoff_params(config)

    agent_params = AgentParams(
        flow_coverage=_validated_flow_coverage(config),
        nb_suppliers_per_input=config.get("nb_suppliers_per_input", 1),
        weight_localization_firm=config.get("weight_localization_firm", 1.0),
        weight_localization_household=config.get("weight_localization_household", 4.0),
        utilization_rate=config.get("utilization_rate", 0.8),
        critical_input_threshold=config.get("critical_input_threshold", 0.0),
        inventory_duration_targets=config.get("inventory_duration_targets", {}),
        # Household buffers are a separate, retail/pantry-calibrated scheme (NOT the
        # firm map). Falls back to the storable/non-storable default in params.py
        # when the config omits it. (The legacy 'household_inventory_duration_target'
        # key was never read; this wires it up.)
        household_inventory_duration_targets=(
            config.get("household_inventory_duration_target")
            or AgentParams.__dataclass_fields__["household_inventory_duration_targets"].default_factory()),
        # inventory_restoration_time is given in DAYS in config; convert to time steps.
        inventory_restoration_time=config.get("inventory_restoration_time", 30.0)
        / days_per_timestep(config.get("time_resolution", "week")),
        enable_household_inventories=config.get("enable_household_inventories", False),
        firm_data_type=config.get("firm_data_type", "mrio"),
        sectors_to_include=config.get("sectors_to_include", "all"),
        sectors_to_exclude=tuple(config.get("sectors_to_exclude") or []),
        countries_to_include=config.get("countries_to_include", "all"),
        explicit_service_firm=config.get("explicit_service_firm", True),
        monetary_units_in_model=config.get("monetary_units_in_model", "mUSD"),
        monetary_units_in_data=config.get("monetary_units_in_data", "mUSD"),
        capital_to_value_added_ratio=config.get("capital_to_value_added_ratio", 3.0),
        country_transport_share=config.get("country_transport_share", 0.2),
        # Was declared on AgentParams and used as the firm transport-share
        # fallback, but never wired to the config — the YAML value was
        # silently ignored (its sibling country_transport_share was wired).
        firm_transport_share=config.get("firm_transport_share", 0.2),
    )

    logistics_params = LogisticsParams(
        speeds=logistics.get("speeds", {}),
        basic_cost=logistics.get("basic_cost", {}),
        switching_costs=logistics.get("switching_costs", {}),
        dwell_times=logistics.get("dwell_times", {}),
        loading_fees=logistics.get("loading_fees", {}),
        border_crossing_fees=logistics.get("border_crossing_fees", {}),
        border_crossing_times=logistics.get("border_crossing_times", {}),
        cost_of_time=logistics.get("cost_of_time", 0.49),
        name_specific=logistics.get("name-specific", {}),
        sector_to_cargo_type=logistics.get("sector_to_cargo_type", {}),
    )

    return transport_params, sim_params, agent_params, logistics_params


# ---------------------------------------------------------------------------
# Output folder setup
# ---------------------------------------------------------------------------

def setup_output(config: dict, sim_params: SimParams) -> Path | None:
    """Create timestamped output folder. Returns None if no export needed."""
    if not config.get("export_files", False):
        return None
    if sim_params.simulation_type not in SIMU_TYPES_WITH_EXPORT:
        return None
    if sim_params.is_monte_carlo:
        return None

    scope = config["scope"]
    output_dir = paths.OUTPUT_FOLDER / scope
    output_dir.mkdir(parents=True, exist_ok=True)
    export_folder = output_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    export_folder.mkdir()

    # Save config snapshot
    with open(export_folder / "parameters.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    return export_folder


_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_RUN_LOG_HANDLER: "logging.Handler | None" = None


def setup_logging(level: str = "info"):
    """Configure console logging."""
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(_LOG_FORMAT)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if level == "debug" else logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)


def attach_run_log(export_folder) -> None:
    """Mirror the log into ``<export_folder>/exp.log`` (DEBUG level).

    Restores the v1 behavior of archiving each run's log with its outputs —
    without it, the provenance of an exported run lives only in terminal
    scrollback. Replaces the handler from any previous run in this process,
    so programmatic drivers calling ``execute()`` in a loop never accumulate
    handlers.
    """
    global _RUN_LOG_HANDLER
    detach_run_log()
    handler = logging.FileHandler(Path(export_folder) / "exp.log", encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logging.getLogger().addHandler(handler)
    _RUN_LOG_HANDLER = handler


def detach_run_log() -> None:
    global _RUN_LOG_HANDLER
    if _RUN_LOG_HANDLER is not None:
        logging.getLogger().removeHandler(_RUN_LOG_HANDLER)
        _RUN_LOG_HANDLER.close()
        _RUN_LOG_HANDLER = None
