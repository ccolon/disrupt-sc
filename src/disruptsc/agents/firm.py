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
    capital_destroyed: float = 0.0
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
    reconstruction_demand: float = 0.0

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
        self.current_production_capacity = self.production_capacity
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

    def initialize_finance(self, eq_input_cost: float, eq_transport_cost: float, eq_other_cost: float):
        """Set up financial state from equilibrium values."""
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
        self.capital_initial = self.capital_to_value_added_ratio * (eq_sales - eq_input_cost - eq_transport_cost)

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

    def plan_purchase(self, adaptive_inventories: bool, adaptive_weight: bool):
        """Decide purchase plan per supplier based on inventory needs."""
        self._evaluate_input_needs()
        self._decide_purchase_plan(adaptive_inventories, adaptive_weight)

    def send_purchase_orders(self, sc_network: ScNetwork):
        """Write purchase plan onto incoming commercial links."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            link.order = self.purchase_plan.get(supplier.pid, 0.0)

    # ------------------------------------------------------------------
    # Simulation loop — Phase 2: Produce
    # ------------------------------------------------------------------

    def produce(self):
        """Leontief production: consume inputs, add output to stock."""
        if self.production_target < EPSILON:
            self.production = 0.0
            return

        # Find binding constraint
        max_production = self.current_production_capacity
        for input_id, coef in self.input_mix.items():
            if coef > EPSILON:
                available = self.inventory.get(input_id, 0.0)
                max_production = min(max_production, available / coef)

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
        """Apply a timed productivity/capacity disruption.

        ``reduction`` is the fractional loss of productive capability
        (negative ⇒ a productivity gain). The cap is taken relative to
        *equilibrium output* (bounded above by the physical ceiling
        ``production_capacity``) so that reductions smaller than the
        ``1/utilization_rate`` head-room still constrain output instead of
        being silently absorbed by spare capacity. The disruption lasts
        ``duration`` time steps (``float('inf')`` ⇒ permanent) and is lifted
        by :meth:`update_disrupted_production_capacity`.
        """
        self.production_capacity_reduction = reduction
        self.remaining_disrupted_time = duration
        self.current_production_capacity = min(
            self.production_capacity, self.eq_production * (1.0 - reduction)
        )

    def update_disrupted_production_capacity(self):
        if self.remaining_disrupted_time > 0:
            self.remaining_disrupted_time -= 1
            if self.remaining_disrupted_time <= 0:
                self.production_capacity_reduction = 0.0
                self.current_production_capacity = self.production_capacity

    def incur_capital_destruction(self, amount: float):
        self.capital_destroyed += amount
        reduction = min(self.capital_destroyed / self.capital_initial, 1.0) if self.capital_initial > 0 else 0.0
        self.current_production_capacity = self.production_capacity * (1 - reduction)

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

    def _evaluate_input_needs(self):
        """Calculate how much of each input is needed for production target."""
        self.input_needs = {
            input_id: coef * self.production_target
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
            # household_first could be added here

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
