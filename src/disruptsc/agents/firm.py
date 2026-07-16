"""Firm agent — production, inventory, purchasing, delivery, finance."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from disruptsc.config import EPSILON
from disruptsc.agents.transport_utils import (
    send_shipment, deliver_without_transport,
)

if TYPE_CHECKING:
    from disruptsc.network.commercial_link import CommercialLink
    from disruptsc.network.sc_network import ScNetwork
    from disruptsc.network.transport_network import TransportNetwork
    from disruptsc.params import TransportParams

# EMA weight for supplier satisfaction (delivery/order fill rate). New signal gets
# this weight, prior satisfaction (1-this). 0.5 ⇒ converges in ~3-4 steps; damps the
# order/deliver oscillation a raw per-step ratio would cause.
SATISFACTION_SMOOTHING = 0.5


@dataclass(eq=False)
class Firm:
    # --- Identity ---
    pid: str
    region: str
    sector: str
    sector_type: str
    region_sector: str
    od_point: int = 0
    name: str = "noname"
    long: float | None = None
    lat: float | None = None
    geometry: object = None
    subregion: str | None = None
    subregions: dict = field(default_factory=dict)
    importance: float = 1.0
    usd_per_ton: float = 2864.0
    monetary_unit_factor: float = 1.0  # multiplier to convert model monetary units to USD
    input_mix: dict[str, float] = field(default_factory=dict)

    # --- Production state ---
    production_capacity: float = 0.0
    current_production_capacity: float = 0.0
    eq_production_capacity: float = 0.0
    utilization_rate: float = 0.8
    # Partially-Binding Leontief: inputs whose share of the firm's total intermediate
    # cost is below this threshold are non-critical and do NOT constrain production
    # (they are still consumed if available). 0.0 = strict Leontief (all inputs bind).
    # Ignored when input_criticality is populated (the survey matrix takes over).
    critical_input_threshold: float = 0.0
    # Per-input criticality weight (Pichler et al. 2022 adapted Leontief), keyed by
    # input_id: 1.0 = critical (hard Leontief bind), 0.5 = important (soft floor at
    # half of eq output), 0.0 = non-critical (never binds). Empty ⇒ fall back to
    # critical_input_threshold / strict Leontief. Missing key defaults to 1.0.
    input_criticality: dict[str, float] = field(default_factory=dict)
    production: float = 0.0
    production_target: float = 0.0
    product_stock: float = 0.0
    eq_production: float = 0.0

    # Production disruption
    production_capacity_reduction: float = 0.0
    remaining_disrupted_time: float = 0.0

    # --- Inventory state ---
    inventory: dict[str, float] = field(default_factory=dict)
    inventory_duration_target: dict[str, float] = field(default_factory=dict)
    inventory_restoration_time: float = 1.0
    input_needs: dict[str, float] = field(default_factory=dict)
    eq_needs: dict[str, float] = field(default_factory=dict)
    purchase_plan: dict[str, float] = field(default_factory=dict)
    purchase_plan_per_input: dict[str, float] = field(default_factory=dict)

    # --- Financial state ---
    eq_price: float = 1.0
    price: float = 1.0
    target_margin: float = 0.2
    transport_share: float = 0.2
    capital_to_value_added_ratio: float = 4.0
    capital_initial: float = 0.0
    active_capital: float = 0.0      # utilized capital -> supports current output
    idle_capital: float = 0.0        # spare capital -> mobilizable (over tau) to boom above eq
    eq_finance: dict = field(default_factory=dict)
    finance: dict = field(default_factory=dict)
    eq_profit: float = 0.0
    profit: float = 0.0
    delta_price_input: float = 0.0

    # --- Order / delivery ---
    order_book: dict[str, float] = field(default_factory=dict)
    total_order: float = 0.0
    eq_total_order: float = 0.0
    total_input: float = 0.0  # sum of realized deliveries from all suppliers
    rationing: float = 1.0
    reconstruction_demand: float = 0.0       # capital-good output requested for rebuilding this step
    reconstruction_produced: float = 0.0     # output actually allocated to rebuilding this step
    capital_demanded: float = 0.0            # own capital the firm wants rebuilt (privately) this step
    public_capital_demanded: float = 0.0     # own capital rebuilt publicly (directly) this step

    # --- Supplier / client maps (set during init_pipeline) ---
    suppliers: dict = field(default_factory=dict)
    clients: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def id_str(self) -> str:
        return f"Firm {self.pid} in {self.region} sector {self.sector}"

    # ------------------------------------------------------------------
    # Initialization (called once after agent creation)
    # ------------------------------------------------------------------

    def initialize_production(self, eq_production: float):
        """Set up production state from equilibrium output."""
        self.eq_production = eq_production
        self.production = eq_production
        self.production_target = eq_production
        self.product_stock = 0.0
        self.production_capacity = eq_production / self.utilization_rate if self.utilization_rate > 0 else eq_production
        # Rest at operating capacity (eq). The spare head-room up to
        # production_capacity is held as idle_capital and only reachable by
        # mobilizing it over tau (see adjust_active_capital). The active/idle
        # split is sized in initialize_capital once capital_initial is known.
        self.current_production_capacity = eq_production
        self.eq_production_capacity = self.production_capacity

    def initialize_inventory(self, time_resolution: str):
        """Set up inventory from equilibrium needs and targets."""
        self.eq_needs = {
            input_id: self.input_mix[input_id] * self.eq_production
            for input_id in self.input_mix
        }
        self.input_needs = dict(self.eq_needs)
        # Inventory = needs_per_step * target_duration_in_steps
        # (inventory_duration_target is already in model time-step units)
        # Clamp to at least 1 step so firms can produce at full capacity
        # from t=0 (sub-step targets can't be represented within one step).
        self.inventory = {
            input_id: need * max(self.inventory_duration_target.get(input_id, 1), 1.0)
            for input_id, need in self.eq_needs.items()
        }

    def initialize_finance(self, eq_input_cost: float, eq_transport_cost: float, eq_other_cost: float,
                           periods_per_year: float = 1.0):
        """Set up financial state from equilibrium values.

        ``periods_per_year`` annualizes the per-time-step value added when sizing
        the capital stock (see ``capital_initial`` below).
        """
        eq_sales = self.eq_production
        self.eq_finance = {
            "sales": eq_sales,
            "costs": {
                "input": eq_input_cost,
                "transport": eq_transport_cost,
                "other": eq_other_cost,
            },
        }
        self.finance = {
            "sales": eq_sales,
            "costs": {
                "input": eq_input_cost,
                "transport": eq_transport_cost,
                "other": eq_other_cost,
            },
        }
        self.eq_profit = eq_sales - eq_input_cost - eq_transport_cost - eq_other_cost
        self.profit = self.eq_profit
        # Capital is a *stock*: the capital-to-value-added ratio is an annual ratio,
        # but value added here is a per-time-step flow. Annualize VA so capital_initial
        # is a realistic stock comparable to absolute capital-destruction shocks
        # (e.g. with daily steps, periods_per_year=365).
        annual_value_added = (eq_sales - eq_input_cost - eq_transport_cost) * periods_per_year
        self.capital_initial = self.capital_to_value_added_ratio * annual_value_added
        self.initialize_capital()

    def initialize_capital(self):
        """Split capital_initial into active (utilized) and idle (spare) stocks.

        active/idle = utilization_rate : (1 - utilization_rate), so at rest
        current_production_capacity = (active/capital_initial)*production_capacity
        = eq_production. Firms with no modeled capital keep an inert split.
        """
        u = self.utilization_rate
        if self.capital_initial > 0:
            self.active_capital = u * self.capital_initial
            self.idle_capital = (1.0 - u) * self.capital_initial
        else:
            self.active_capital = 0.0
            self.idle_capital = 0.0
        self._recompute_capacity_from_active()

    # ------------------------------------------------------------------
    # Simulation loop — Phase 1: Retrieve orders & plan
    # ------------------------------------------------------------------

    def retrieve_orders(self, sc_network: ScNetwork):
        """Extract orders placed by all clients from the SC network."""
        self.order_book = {}
        self.total_order = 0.0
        for _, client, data in sc_network.out_edges(self, data=True):
            link: CommercialLink = data["object"]
            self.order_book[client.pid] = link.order
            self.total_order += link.order
        if self.reconstruction_demand > 0:
            self.total_order += self.reconstruction_demand

    def plan_production(self, sc_network: ScNetwork, propagate_price: bool):
        """Decide production target based on orders and stock."""
        self.production_target = max(0.0, self.total_order - self.product_stock)
        if propagate_price:
            self._calculate_price(sc_network)

    def plan_purchase(self, adaptive_inventories: bool, adaptive_weight: bool,
                      capacity_constrained: bool = False):
        """Decide purchase plan per supplier based on inventory needs."""
        self._evaluate_input_needs(capacity_constrained)
        self._decide_purchase_plan(adaptive_inventories, adaptive_weight)

    def send_purchase_orders(self, sc_network: ScNetwork):
        """Write purchase plan onto incoming commercial links."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            link.order = self.purchase_plan.get(supplier.pid, 0.0)

    def update_supplier_satisfaction(self, sc_network: ScNetwork,
                                     smoothing: float = SATISFACTION_SMOOTHING):
        """Update each supplier's satisfaction = EMA of its realized fill rate
        (delivery / order on that link). This feeds the NEXT step's adaptive
        supplier-weight substitution: a supplier that persistently under-delivers
        loses weight, so buyers shift orders toward reliable suppliers of the same
        input. Call AFTER deliver(). Suppliers not ordered from this step keep their
        prior satisfaction (no order ⇒ no new signal, avoids recovery oscillation)."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            info = self.suppliers.get(supplier.pid)
            if info is None:
                continue
            link: CommercialLink = data["object"]
            if link.order < EPSILON:
                continue
            rate = min(1.0, link.delivery / link.order)
            info["satisfaction"] = smoothing * rate + (1.0 - smoothing) * info.get("satisfaction", 1.0)

    # ------------------------------------------------------------------
    # Simulation loop — Phase 2: Produce
    # ------------------------------------------------------------------

    def produce(self):
        """Partially-Binding ("adapted") Leontief production (Pichler et al. 2022).

        Each input gets a criticality weight that decides how it constrains output:
          * critical (>=1.0): hard Leontief bind — output ≤ inventory/coef;
          * important (0.5): soft floor — output ≤ 0.5·(inventory/coef) + 0.5·eq,
            so a fully depleted important input caps output at half of eq, not zero;
          * non-critical (<0.5): never constrains output (still consumed if present).

        The weight comes from two composable knobs:
          * ``input_criticality`` — the IHS Markit survey weight per input (if set);
          * ``critical_input_threshold`` — a *materiality floor*: any input whose
            cost share is below it is forced non-critical. This makes the binding
            set invariant to tiny links, so results saturate in flow_coverage.

        Combinations: matrix only ⇒ survey weights (can over-bind on tiny links);
        matrix + threshold ⇒ survey weights among material inputs only (saturates);
        threshold only ⇒ cost-share proxy (material ⇒ critical); neither ⇒ strict
        Leontief (every input binds). Inputs are consumed in proportion to output."""
        if self.production_target < EPSILON:
            self.production = 0.0
            return

        max_production = self.current_production_capacity
        use_matrix = bool(self.input_criticality)
        thr = self.critical_input_threshold
        need_share = thr > 0.0
        total_coef = (sum(c for c in self.input_mix.values() if c > EPSILON)
                      if need_share else 0.0)
        for input_id, coef in self.input_mix.items():
            if coef <= EPSILON:
                continue
            if need_share and (coef / total_coef if total_coef > 0 else 1.0) < thr:
                weight = 0.0                                   # immaterial ⇒ non-critical
            elif use_matrix:
                weight = self.input_criticality.get(input_id, 1.0)
            else:
                weight = 1.0                                   # material (or strict): binds
            available = self.inventory.get(input_id, 0.0)
            if weight >= 1.0:                                  # critical: hard bind
                max_production = min(max_production, available / coef)
            elif weight >= 0.5:                                # important: soft floor
                soft = 0.5 * (available / coef) + 0.5 * self.eq_production
                max_production = min(max_production, soft)
            # else non-critical: no production constraint

        self.production = max(0.0, min(self.production_target, max_production))

        # Consume inputs
        for input_id, coef in self.input_mix.items():
            consumed = coef * self.production
            self.inventory[input_id] = max(0.0, self.inventory.get(input_id, 0.0) - consumed)

        self.product_stock += self.production

    # ------------------------------------------------------------------
    # Simulation loop — Phase 3: Deliver
    # ------------------------------------------------------------------

    def deliver(self, sc_network: ScNetwork,
                transport_network: TransportNetwork,
                available_transport_network: TransportNetwork,
                tp: TransportParams,
                routing_event_collector=None):
        """Ration and deliver to all clients."""
        def _after_delivery(link):
            self.product_stock = max(0.0, self.product_stock - link.delivery)

        def _after_shipment(link, route):
            self.product_stock = max(0.0, self.product_stock - link.delivery)

        self._evaluate_quantities_to_deliver(sc_network, tp.rationing_mode)
        for _, client, data in sc_network.out_edges(self, data=True):
            link: CommercialLink = data["object"]
            link.reset_transport_tracking()
            if link.delivery < EPSILON:
                continue

            # Check if this link needs the transport network
            if link.product_type in tp.sectors_no_transport:
                deliver_without_transport(link, _after_delivery, supplier_price=self.price)
            elif getattr(client, "virtual", False):
                deliver_without_transport(link, _after_delivery, supplier_price=self.price)
            elif not tp.with_transport:
                deliver_without_transport(link, _after_delivery, supplier_price=self.price)
            elif client.__class__.__name__ == "Household" and not tp.transport_to_households:
                deliver_without_transport(link, _after_delivery, supplier_price=self.price)
            else:
                send_shipment(
                    self.pid, self.od_point, self.transport_share,
                    link, transport_network, available_transport_network, tp,
                    routing_event_collector, _after_shipment,
                    supplier_price=self.price,
                )

    # ------------------------------------------------------------------
    # Simulation loop — Phase 4: Receive inputs
    # ------------------------------------------------------------------

    def receive_products(self, sc_network: ScNetwork,
                         transport_network: TransportNetwork,
                         sectors_no_transport: tuple,
                         with_transport: bool = True):
        """Receive all shipments from suppliers.

        Mirrors the routing in :meth:`deliver`: a link is received as a
        direct (no-transport) delivery when transport is globally off
        (``with_transport`` False), when the product is a non-transported
        sector, or when the supplier is virtual; otherwise it is collected
        from the transport network. Without the ``with_transport`` guard,
        transportable inputs delivered via ``deliver_without_transport``
        would be looked up as transport-network shipments that were never
        placed, and silently received as zero.
        """
        self.total_input = 0.0
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            if (not with_transport
                    or link.product_type in sectors_no_transport
                    or getattr(supplier, "virtual", False)):
                qty = self._receive_service(link)
            else:
                qty = self._receive_shipment(link, transport_network)
            self.total_input += qty

    # ------------------------------------------------------------------
    # Simulation loop — Phase 5: Finance
    # ------------------------------------------------------------------

    def evaluate_profit(self, sc_network: ScNetwork):
        """Calculate profit from current sales and costs."""
        sales = sum(
            data["object"].payment
            for _, _, data in sc_network.out_edges(self, data=True)
        )
        input_cost = sum(
            data["object"].payment
            for _, _, data in sc_network.in_edges(self, data=True)
        )
        transport_cost = self.finance["costs"]["transport"]
        self.finance["sales"] = sales
        self.finance["costs"]["input"] = input_cost
        self.profit = sales - input_cost - transport_cost - self.finance["costs"]["other"]

    # ------------------------------------------------------------------
    # Disruption
    # ------------------------------------------------------------------

    def disrupt_production_capacity(self, duration: float, reduction: float):
        """Apply a timed productivity/capacity shock.

        ``reduction`` is a temporary multiplicative hit (negative ⇒ a gain) to the
        capacity that active capital yields — a TFP-style shock affecting active
        and idle capital alike, so it scales the whole capacity curve:
        ``current = (active/capital_initial)*production_capacity*(1-reduction)``.
        It lasts ``duration`` time steps (``float('inf')`` ⇒ permanent) and is
        lifted by :meth:`update_disrupted_production_capacity`.
        """
        self.production_capacity_reduction = reduction
        self.remaining_disrupted_time = duration
        self._recompute_capacity_from_active()

    def update_disrupted_production_capacity(self):
        if self.remaining_disrupted_time > 0:
            self.remaining_disrupted_time -= 1
            if self.remaining_disrupted_time <= 0:
                self.production_capacity_reduction = 0.0
                self._recompute_capacity_from_active()

    @property
    def capital_destroyed(self) -> float:
        """Capital still missing (destroyed and not yet rebuilt), model units.

        Derived from the stocks: ``capital_initial - active - idle``. Drives
        reconstruction demand, which stops once the stocks are fully restored.
        """
        return max(0.0, self.capital_initial - self.active_capital - self.idle_capital)

    def incur_capital_destruction(self, amount: float):
        """Destroy ``amount`` (model monetary units) of built capital.

        The quake hits active and idle capital alike: both stocks are scaled by
        ``(1 - amount/capital_initial)``. On impact this reproduces
        ``current = eq*(1-destruction_rate)``. The loss is permanent until
        :meth:`rebuild_capital` restores it.
        """
        if amount <= 0 or self.capital_initial <= 0:
            return
        survival = max(0.0, 1.0 - amount / self.capital_initial)
        self.active_capital *= survival
        self.idle_capital *= survival
        self._recompute_capacity_from_active()

    def rebuild_capital(self, amount: float):
        """Restore ``amount`` of destroyed capital (reconstruction), lifting capacity.

        New capital refills the *original* split: active up to
        ``utilization_rate*capital_initial`` first (restoring operating
        capacity), then idle up to the remainder (rebuilding the spare buffer).
        A fully-rebuilt firm rests back at eq with its idle head-room intact.
        """
        if amount <= 0 or self.capital_initial <= 0:
            return
        u = self.utilization_rate
        add_active = min(amount, max(0.0, u * self.capital_initial - self.active_capital))
        self.active_capital += add_active
        amount -= add_active
        if amount > 0:
            add_idle = min(amount, max(0.0, (1.0 - u) * self.capital_initial - self.idle_capital))
            self.idle_capital += add_idle
        self._recompute_capacity_from_active()

    def adjust_active_capital(self, activation_fraction: float):
        """Move capital between idle and active to track the production target.

        If the target needs more capacity than active capital yields, mobilize
        idle -> active; if it needs less, mothball active -> idle. Each step at
        most ``activation_fraction`` (= min(1, days_per_step/tau)) of the source
        stock moves, so full mobilization takes ~tau (geometric approach). Total
        capital is conserved here (only destruction/rebuild change it).
        """
        if self.capital_initial <= 0 or self.production_capacity <= 0:
            return
        effective_max = self.production_capacity * (1.0 - self.production_capacity_reduction)
        if effective_max <= 0:
            return
        active_need = min(self.capital_initial,
                          self.production_target / effective_max * self.capital_initial)
        gap = active_need - self.active_capital
        if gap > 0:                                   # bring idle capacity online
            move = min(gap, activation_fraction * self.idle_capital)
        elif gap < 0:                                 # mothball unused capacity
            move = -min(-gap, activation_fraction * self.active_capital)
        else:
            return
        if move == 0.0:
            return
        self.active_capital += move
        self.idle_capital -= move
        self._recompute_capacity_from_active()

    def _recompute_capacity_from_active(self):
        """Current capacity = active share of the physical ceiling, net of any
        temporary productivity shock. At rest (active = u*capital_initial) this is
        eq_production; fully mobilizing idle reaches production_capacity."""
        if self.capital_initial > 0:
            base = self.active_capital / self.capital_initial * self.production_capacity
        else:
            base = self.eq_production
        self.current_production_capacity = max(0.0, base * (1.0 - self.production_capacity_reduction))

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def collect_data(self, time_step: int) -> dict:
        return {
            "time_step": time_step,
            "firm": self.pid,
            "region": self.region,
            "sector": self.sector,
            "production": self.production,
            "production_target": self.production_target,
            "production_capacity": self.current_production_capacity,
            "active_capital": self.active_capital,
            "idle_capital": self.idle_capital,
            "product_stock": self.product_stock,
            "total_order": self.total_order,
            "total_input": self.total_input,
            "rationing": self.rationing,
            "profit": self.profit,
            "price": self.price,
            "delta_price_input": self.delta_price_input,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _evaluate_input_needs(self, capacity_constrained: bool = False):
        """Calculate how much of each input is needed. By default needs track the
        production *target* (demand). With ``capacity_constrained`` they are capped at
        the firm's current production capacity, so a capacity-limited firm (e.g. one
        whose capital was destroyed) orders inputs only for the output it can actually
        make — instead of over-ordering inputs it cannot process (which otherwise pile
        into inventory and inflate the value-added loss)."""
        planned = self.production_target
        if capacity_constrained:
            planned = min(planned, self.current_production_capacity)
        self.input_needs = {
            input_id: coef * planned
            for input_id, coef in self.input_mix.items()
        }

    def _decide_purchase_plan(self, adaptive_inventories: bool, adaptive_weight: bool):
        """Compute purchase_plan per supplier, accounting for inventory targets."""
        self.purchase_plan = {}
        self.purchase_plan_per_input = {}

        for input_id, coef in self.input_mix.items():
            if coef < EPSILON:
                continue
            # Target = needs + inventory restoration
            target_inventory = self.eq_needs.get(input_id, 0.0) * self.inventory_duration_target.get(input_id, 1)
            current_inv = self.inventory.get(input_id, 0.0)
            need = self.input_needs.get(input_id, 0.0)

            if adaptive_inventories:
                desired_inventory = need * self.inventory_duration_target.get(input_id, 1)
            else:
                desired_inventory = target_inventory

            restoration = max(0.0, desired_inventory - current_inv) / max(self.inventory_restoration_time, 1.0)
            total_purchase = need + restoration
            self.purchase_plan_per_input[input_id] = total_purchase

        # Distribute across suppliers (weighted by supplier weights)
        for supplier_id, supplier_info in self.suppliers.items():
            input_id = supplier_info["sector"]
            weight = supplier_info.get("weight", 1.0)
            if adaptive_weight:
                satisfaction = supplier_info.get("satisfaction", 1.0)
                weight *= satisfaction
            total_for_input = self.purchase_plan_per_input.get(input_id, 0.0)
            # Get total weight for this input
            total_weight = sum(
                self.suppliers[sid].get("weight", 1.0) * (
                    self.suppliers[sid].get("satisfaction", 1.0) if adaptive_weight else 1.0)
                for sid in self.suppliers
                if self.suppliers[sid]["sector"] == input_id
            )
            share = weight / total_weight if total_weight > EPSILON else 0.0
            self.purchase_plan[supplier_id] = total_for_input * share

    def _calculate_price(self, sc_network: ScNetwork):
        """Adjust price based on input cost changes."""
        if not self.eq_finance or self.eq_finance.get("sales", 0) < EPSILON:
            return
        current_input_cost = sum(
            data["object"].price * data["object"].order
            for _, _, data in sc_network.in_edges(self, data=True)
            if data["object"].order > EPSILON
        )
        eq_input_cost = self.eq_finance["costs"]["input"]
        if eq_input_cost > EPSILON:
            self.delta_price_input = max(0.0, (current_input_cost - eq_input_cost) / self.eq_finance["sales"])
        else:
            self.delta_price_input = 0.0
        self.price = self.eq_price + self.delta_price_input

    def _evaluate_quantities_to_deliver(self, sc_network: ScNetwork, rationing_mode: str):
        """Determine delivery quantities, applying rationing if needed."""
        if self.total_order < EPSILON:
            self.rationing = 1.0
            return

        available = self.product_stock
        if available >= self.total_order - EPSILON:
            self.rationing = 1.0
            for _, client, data in sc_network.out_edges(self, data=True):
                link: CommercialLink = data["object"]
                link.delivery = link.order
                link.delivery_in_tons = link.delivery * self.monetary_unit_factor / self.usd_per_ton if self.usd_per_ton > 0 else 0.0
        else:
            self.rationing = available / self.total_order
            if rationing_mode == "equal":
                for _, client, data in sc_network.out_edges(self, data=True):
                    link: CommercialLink = data["object"]
                    link.delivery = link.order * self.rationing
                    link.delivery_in_tons = link.delivery * self.monetary_unit_factor / self.usd_per_ton if self.usd_per_ton > 0 else 0.0
            elif rationing_mode == "household_first":
                # Serve household clients first, then ration firm/country clients
                # with the remainder. Any stock left after the graph clients flows
                # to the reconstruction pseudo-client downstream (rebuilt capital is
                # taken from leftover product_stock), so reconstruction is served last.
                hh_links, other_links = [], []
                hh_demand = other_demand = 0.0
                for _, client, data in sc_network.out_edges(self, data=True):
                    link: CommercialLink = data["object"]
                    if client.__class__.__name__ == "Household":
                        hh_links.append(link)
                        hh_demand += link.order
                    else:
                        other_links.append(link)
                        other_demand += link.order
                hh_ration = min(1.0, available / hh_demand) if hh_demand > EPSILON else 1.0
                remainder = max(0.0, available - hh_demand * hh_ration)
                other_ration = min(1.0, remainder / other_demand) if other_demand > EPSILON else 1.0
                for link in hh_links:
                    link.delivery = link.order * hh_ration
                    link.delivery_in_tons = link.delivery * self.monetary_unit_factor / self.usd_per_ton if self.usd_per_ton > 0 else 0.0
                for link in other_links:
                    link.delivery = link.order * other_ration
                    link.delivery_in_tons = link.delivery * self.monetary_unit_factor / self.usd_per_ton if self.usd_per_ton > 0 else 0.0
            else:
                raise ValueError(
                    f"Unknown rationing_mode {rationing_mode!r}; expected 'equal' or 'household_first'"
                )

    def _receive_shipment(self, link: CommercialLink, transport_network: TransportNetwork) -> float:
        """Receive a shipment from the transport network. Returns quantity received."""
        available_shipments = transport_network._node[self.od_point].get("shipments", {})
        if link.pid in available_shipments:
            shipment = available_shipments.pop(link.pid)
            quantity_received = shipment["quantity"]
            self.inventory[link.product] = self.inventory.get(link.product, 0.0) + quantity_received
            link.payment = quantity_received * link.price
        else:
            # No shipment arrived
            quantity_received = 0.0

        link.update_indicator(quantity_received)
        return quantity_received

    def _receive_service(self, link: CommercialLink) -> float:
        """Receive a service (no transport needed). Returns quantity received."""
        quantity_received = link.realized_delivery
        self.inventory[link.product] = self.inventory.get(link.product, 0.0) + quantity_received
        link.payment = quantity_received * link.price
        link.update_indicator(quantity_received)
        return quantity_received
