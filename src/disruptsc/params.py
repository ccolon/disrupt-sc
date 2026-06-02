"""Scoped, frozen parameter bundles for DisruptSC v2."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TransportParams:
    """Parameters that govern transport and delivery behavior."""
    with_transport: bool = True
    transport_to_households: bool = True
    capacity_constraint_enabled: bool = False
    capacity_constraint_mode: str = "gradual"
    initial_route_assignment: str = "heuristic"
    rationing_mode: str = "equal"
    use_route_cache: bool = True
    switching_costs: dict = field(default_factory=lambda: {"modal_switch": 0.15, "port_switch": 0.05})
    price_increase_threshold: float | None = 2.0  # None = no threshold
    sectors_no_transport: tuple = ("utility", "transport", "trade", "services", "service", "construction")
    countries_no_transport: tuple = ()
    # When False, all shipments are tagged with a single cargo type
    # ("any") and the routing pipeline runs Dijkstra/LP once instead of
    # once per cargo type. Useful for studies without pipelines or other
    # per-cargo-type infrastructure. When True, cargo types are derived
    # from sector_to_cargo_type as before.
    use_cargo_types: bool = True
    monetary_units: str = "mUSD"
    route_optimization_weight: str = "cost_per_ton"
    chunk_size: float = 1e9  # tons per time-step; very large = no chunking
    route_candidate_count: int = 4
    route_candidate_stretch: float = 3.0
    route_candidate_overlap: float = 0.85
    lp_route_candidate_count: int = 20
    lp_route_candidate_stretch: float = 4.0
    lp_route_candidate_overlap: float = 0.9
    lp_overcapacity_limit: float = 1.1


@dataclass(frozen=True)
class SimParams:
    """Parameters that govern the simulation run."""
    t_final: int = 10
    epsilon_stop: float = 1e-3
    time_resolution: str = "week"
    simulation_type: str = "initial_state"
    mc_repetitions: int = 0
    mc_caching: dict = field(default_factory=lambda: {
        "transport_network": True, "agents": True,
        "sc_network": False, "logistic_routes": False,
    })
    propagate_input_price_change: bool = True
    adaptive_inventories: bool = False
    adaptive_supplier_weight: bool = False
    sensitivity: dict = field(default_factory=dict)

    @property
    def is_monte_carlo(self) -> bool:
        return self.mc_repetitions >= 1


@dataclass(frozen=True)
class AgentParams:
    """Parameters for agent creation and filtering."""
    # Cumulative flow-coverage fraction in (0, 1]. A single quantile-style
    # knob that decides which agents and bilateral trade cells are kept.
    # Per-buyer top inputs and per-supplier top buyers are unioned; every
    # kept agent retains at least this fraction of its in-flows and
    # out-flows. Replaces the legacy cutoff_*/input_coverage knobs.
    flow_coverage: float = 0.95
    nb_suppliers_per_input: float = 1
    weight_localization_firm: float = 1.0
    weight_localization_household: float = 4.0
    utilization_rate: float = 0.8
    inventory_duration_targets: dict = field(default_factory=lambda: {
        "definition": "per_input_type",
        "values": {"default": 30, "utility": 3, "agriculture": 15,
                   "manufacturing": 30, "service": 90, "services": 90,
                   "trade": 30, "transport": 5},
        "unit": "day",
    })
    inventory_restoration_time: float = 4.0
    enable_household_inventories: bool = False
    firm_data_type: str = "mrio"
    sectors_to_include: str = "all"
    sectors_to_exclude: tuple = ()
    countries_to_include: str = "all"
    explicit_service_firm: bool = True
    monetary_units_in_model: str = "mUSD"
    monetary_units_in_data: str = "mUSD"
    capital_to_value_added_ratio: float = 3.0
    country_transport_share: float = 0.2
    firm_transport_share: float = 0.2


@dataclass(frozen=True)
class LogisticsParams:
    """Parameters for logistics cost computation."""
    speeds: dict = field(default_factory=lambda: {"roads": 50, "maritime": 35})
    basic_cost: dict = field(default_factory=lambda: {"roads": 0.01, "maritime": 0.001})
    switching_costs: dict = field(default_factory=lambda: {"modal_switch": 0.15, "port_switch": 0.05})
    dwell_times: dict = field(default_factory=dict)
    loading_fees: dict = field(default_factory=dict)
    border_crossing_fees: dict = field(default_factory=dict)
    border_crossing_times: dict = field(default_factory=dict)
    cost_of_time: float = 0.49
    variability_coef: float = 0.44
    variability: dict = field(default_factory=dict)
    name_specific: dict = field(default_factory=dict)
    sector_to_cargo_type: dict = field(default_factory=dict)
