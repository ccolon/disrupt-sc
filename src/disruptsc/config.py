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
    """Load default.yaml, overlay user_defined_<scope>.yaml, return flat dict."""
    parameter_folder = parameter_folder or paths.PARAMETER_FOLDER

    with open(parameter_folder / "default.yaml", "r") as f:
        config = yaml.safe_load(f)

    user_file = parameter_folder / f"user_defined_{scope}.yaml"
    if os.path.exists(user_file):
        logging.info(f"User-defined parameter file found for {scope}")
        with open(user_file, "r") as f:
            overrides = yaml.safe_load(f)
        _merge_dicts(config, overrides)
    else:
        logging.info(f"No user-defined parameter file for {scope}, using defaults")

    config["scope"] = scope

    # Resolve filepaths to absolute
    for key, val in config.get("filepaths", {}).items():
        if val and val != "None":
            config["filepaths"][key] = paths.INPUT_FOLDER / scope / val
        else:
            config["filepaths"][key] = None

    return config


# ---------------------------------------------------------------------------
# Build param bundles from config dict
# ---------------------------------------------------------------------------

def _parse_capacity_constraint(raw) -> tuple[bool, str]:
    """Return (enabled, mode) from the capacity_constraint config value."""
    if isinstance(raw, bool):
        return raw, "gradual"
    if isinstance(raw, str):
        low = raw.lower()
        if low in ("off", "disabled", "false"):
            return False, "gradual"
        if low in ("gradual", "binary"):
            return True, low
        return True, "gradual"
    return True, "gradual"


def _parse_chunk_size(logistics: dict, time_resolution: str) -> float:
    """Convert chunk_size from tons/day (YAML) to tons/time-step."""
    raw = logistics.get("chunk_size", 1e9)
    time_factor = {"day": 1, "week": 7, "month": 30, "year": 365}.get(time_resolution, 7)
    return float(raw) * time_factor


def build_params(config: dict) -> tuple[TransportParams, SimParams, AgentParams, LogisticsParams]:
    """Build frozen parameter bundles from a raw config dict."""
    logistics = config.get("logistics", {})
    cap_enabled, cap_mode = _parse_capacity_constraint(config.get("capacity_constraint", "off"))

    transport_params = TransportParams(
        with_transport=config.get("with_transport", True),
        transport_to_households=config.get("transport_to_households", True),
        capacity_constraint_enabled=cap_enabled,
        capacity_constraint_mode=cap_mode,
        initial_route_assignment=logistics.get("initial_route_assignment", "heuristic"),
        rationing_mode=config.get("rationing_mode", "equal"),
        use_route_cache=config.get("use_route_cache", True),
        switching_costs=logistics.get("switching_costs", {"modal_switch": 0.15, "port_switch": 0.05}),
        price_increase_threshold=config.get("price_increase_threshold", 2.0),
        sectors_no_transport=tuple(config.get("sectors_no_transport_network",
                                              ["utility", "transport", "trade", "services", "service", "construction"])),
        monetary_units=config.get("monetary_units_in_model", "mUSD"),
        route_optimization_weight=config.get("route_optimization_weight", "cost_per_ton"),
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
        mc_caching=config.get("mc_caching", {
            "transport_network": True, "agents": True,
            "sc_network": False, "logistic_routes": False,
        }),
        propagate_input_price_change=config.get("propagate_input_price_change", True),
        adaptive_inventories=config.get("adaptive_inventories", False),
        adaptive_supplier_weight=config.get("adaptive_supplier_weight", False),
        sensitivity=config.get("sensitivity") or {},
    )

    agent_params = AgentParams(
        io_cutoff=config.get("io_cutoff", 0.95),
        cutoff_sector_output=config.get("cutoff_sector_output", {"type": "absolute", "value": 1.0, "unit": "mUSD"}),
        cutoff_sector_demand=config.get("cutoff_sector_demand", {"type": "absolute", "value": 1.0, "unit": "mUSD"}),
        cutoff_firm_output=config.get("cutoff_firm_output", {"type": "absolute", "value": 10, "unit": "kUSD"}),
        cutoff_household_demand=config.get("cutoff_household_demand", {"type": "absolute", "value": 10, "unit": "kUSD"}),
        combine_sector_cutoff=config.get("combine_sector_cutoff", "and"),
        nb_suppliers_per_input=config.get("nb_suppliers_per_input", 1),
        weight_localization_firm=config.get("weight_localization_firm", 1.0),
        weight_localization_household=config.get("weight_localization_household", 4.0),
        utilization_rate=config.get("utilization_rate", 0.8),
        inventory_duration_targets=config.get("inventory_duration_targets", {}),
        inventory_restoration_time=config.get("inventory_restoration_time", 4.0),
        enable_household_inventories=config.get("enable_household_inventories", False),
        firm_data_type=config.get("firm_data_type", "mrio"),
        sectors_to_include=config.get("sectors_to_include", "all"),
        sectors_to_exclude=tuple(config.get("sectors_to_exclude") or []),
        countries_to_include=config.get("countries_to_include", "all"),
        min_nb_firms_per_sector=config.get("min_nb_firms_per_sector", 5),
        pop_density_cutoff=config.get("pop_density_cutoff", 0.0),
        pop_cutoff=config.get("pop_cutoff", 0.0),
        local_demand_cutoff=config.get("local_demand_cutoff", 0.0),
        explicit_service_firm=config.get("explicit_service_firm", True),
        monetary_units_in_model=config.get("monetary_units_in_model", "mUSD"),
        monetary_units_in_data=config.get("monetary_units_in_data", "mUSD"),
        capital_to_value_added_ratio=config.get("capital_to_value_added_ratio", 3.0),
        country_transport_share=config.get("country_transport_share", 0.2),
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
        variability_coef=logistics.get("variability_coef", 0.44),
        variability=logistics.get("variability", {}),
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


def setup_logging(level: str = "info"):
    """Configure console logging."""
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if level == "debug" else logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
