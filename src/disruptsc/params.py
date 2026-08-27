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
    propagate_input_price_change: bool = True
    adaptive_inventories: bool = False
    adaptive_supplier_weight: bool = False
    # When True, firms cap input orders at current production capacity (a
    # capacity-destroyed firm stops over-ordering inputs it cannot process).
    capacity_constrained_orders: bool = False
    # Characteristic time (DAYS) to mobilize idle capital into active capacity.
    # Per step at most min(1, days_per_step/tau) of idle can be activated (or
    # active mothballed), so a firm reaches full mobilization in ~tau.
    time_to_activate_idle_capital: float = 30.0
    sensitivity: dict = field(default_factory=dict)
    # Seed both Python's `random` and `numpy.random` before stochastic
    # stages (currently: supply-chain build, Monte-Carlo disruption arrival).
    # None ⇒ no seeding (legacy non-reproducible behavior).
    seed: int | None = None

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
    # Partially-Binding Leontief: inputs below this share of a firm's intermediate
    # cost are non-critical (don't constrain output). 0.0 = strict Leontief.
    critical_input_threshold: float = 0.0
    # Firm INPUT inventories. Storable goods (mfg/ag/trade) ~ inventory-to-sales stock;
    # utility/transport are short (non-storable). service=90 is NOT literal stockpiling
    # (services can't be warehoused) but a reduced-form COPING/resilience duration: firms
    # keep operating through a service-input disruption via contracts, redundancy, degraded
    # operation and substitution the model under-captures. Tested the storability-literal
    # cut to 7d (2026-07-17): it did NOT improve MMI>7 local severity (acute sales DiD -2.9%
    # vs UQ -9.6%) but doubled the SPURIOUS national cascade (control-zone recovery sales
    # -4.9%->-10.9%), so the longer coping-duration value is retained. This is the single
    # dominant inventory lever -- treat it as a sensitivity axis, not a hard number.
    inventory_duration_targets: dict = field(default_factory=lambda: {
        "definition": "per_input_type",
        "values": {"default": 30, "utility": 3, "agriculture": 15,
                   "manufacturing": 30, "service": 90, "services": 90,
                   "trade": 30, "transport": 5},
        "unit": "day",
    })
    # In TIME STEPS (the config supplies DAYS; build_params divides by
    # days_per_timestep). 4 steps ≈ the 30-day config default at weekly resolution.
    inventory_restoration_time: float = 4.0
    enable_household_inventories: bool = False
    # Household buffers proxy the retail-shelf + home-pantry stock that the IO
    # framework omits (bought-for-resale is netted out, so B2C links run
    # producer->household with no retailer node). Unlike firms, this is calibrated
    # to *final-consumption* storability, not production buffering: non-storable
    # services/utilities/transport get a token buffer (coping/substitution proxy),
    # construction is investment (0), and only physical goods hold real stock.
    # Keyed on sector_table['type']; see configure_household_inventories.
    household_inventory_duration_targets: dict = field(default_factory=lambda: {
        "definition": "per_input_type",
        "values": {"default": 7, "construction": 0,
                   "service": 3, "transport": 3, "utility": 3, "trade": 3, "mining": 3,
                   "agriculture": 7, "manufacturing": 14, "imports": 14},
        "unit": "day",
    })
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
    cost_of_time: float | dict = 0.49  # USD/(ton·hour); dict = per cargo type with 'default'
    name_specific: dict = field(default_factory=dict)
    sector_to_cargo_type: dict = field(default_factory=dict)
