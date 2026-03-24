"""Country agent — import/export node, transit, delivery."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from disruptsc.config import EPSILON

if TYPE_CHECKING:
    from disruptsc.network.commercial_link import CommercialLink
    from disruptsc.network.sc_network import ScNetwork
    from disruptsc.network.transport_network import TransportNetwork
    from disruptsc.params import TransportParams


@dataclass(eq=False)
class Country:
    # --- Identity ---
    pid: str  # Country code, e.g. "TZ"
    region: str
    od_point: int = 0
    name: str = "noname"
    long: float | None = None
    lat: float | None = None
    sector: str = "IMP"
    region_sector: str = ""
    usd_per_ton: float = 2864.0

    # --- Trade structure (set during init_pipeline) ---
    supply_importance: float | None = None
    transit_from: dict = field(default_factory=dict)
    transit_to: dict = field(default_factory=dict)
    clients: dict = field(default_factory=dict)
    purchase_plan: dict = field(default_factory=dict)
    qty_purchased: dict = field(default_factory=dict)
    qty_purchased_perfirm: dict = field(default_factory=dict)

    # --- Per-timestep tracking ---
    qty_sold: float = 0.0
    generalized_transport_cost: float = 0.0
    usd_transported: float = 0.0
    tons_transported: float = 0.0
    tonkm_transported: float = 0.0
    extra_spending: float = 0.0
    consumption_loss: float = 0.0

    # --- Routing ---
    cost_profile: int = 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def id_str(self) -> str:
        return f"Country {self.pid} at node {self.od_point}"

    def assign_cost_profile(self, nb_cost_profiles: int):
        if nb_cost_profiles > 0:
            self.cost_profile = random.randint(0, nb_cost_profiles - 1)

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------

    def reset_variables(self):
        self.qty_sold = 0.0
        self.generalized_transport_cost = 0.0
        self.usd_transported = 0.0
        self.tons_transported = 0.0
        self.tonkm_transported = 0.0
        self.extra_spending = 0.0
        self.consumption_loss = 0.0

    def send_purchase_orders(self, sc_network: ScNetwork):
        """Set order quantities for imports."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            link.order = self.purchase_plan.get(supplier, 0.0)

    def deliver(self, sc_network: ScNetwork,
                transport_network: TransportNetwork,
                available_transport_network: TransportNetwork,
                tp: TransportParams,
                routing_event_collector=None):
        """Export/deliver products to firms and households."""
        for _, client, data in sc_network.out_edges(self, data=True):
            link: CommercialLink = data["object"]
            # Country delivers whatever was ordered (unlimited supply from outside)
            link.delivery = link.order
            link.delivery_in_tons = link.delivery / self.usd_per_ton if self.usd_per_ton > 0 else 0.0

            if link.delivery < EPSILON:
                continue

            if link.product_type in tp.sectors_no_transport:
                self._deliver_without_transport(link)
            elif not tp.with_transport:
                self._deliver_without_transport(link)
            elif client.__class__.__name__ == "Household" and not tp.transport_to_households:
                self._deliver_without_transport(link)
            else:
                self._send_shipment(
                    link, transport_network, available_transport_network, tp,
                    routing_event_collector,
                )

    def receive_products(self, sc_network: ScNetwork,
                         transport_network: TransportNetwork,
                         sectors_no_transport: tuple,
                         transport_to_households: bool):
        """Receive import shipments (transit goods from other countries/firms)."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            quantity_received = link.realized_delivery
            # Track losses
            expected = self.purchase_plan.get(supplier, 0.0)
            if expected > EPSILON and quantity_received < expected - EPSILON:
                self.consumption_loss += expected - quantity_received
            # Track extra spending
            extra = max(0.0, quantity_received * link.price - expected * link.eq_price)
            self.extra_spending += extra
            link.update_indicator(quantity_received)

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def collect_data(self, time_step: int) -> dict:
        return {
            "time_step": time_step,
            "country": self.pid,
            "extra_spending": self.extra_spending,
            "consumption_loss": self.consumption_loss,
            "generalized_transport_cost": self.generalized_transport_cost,
            "usd_transported": self.usd_transported,
            "tons_transported": self.tons_transported,
            "tonkm_transported": self.tonkm_transported,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _deliver_without_transport(self, link: CommercialLink):
        link.realized_delivery = link.delivery
        link.payment = link.delivery * link.price
        self.qty_sold += link.delivery

    def _send_shipment(self, link: CommercialLink,
                       transport_network: TransportNetwork,
                       available_transport_network: TransportNetwork,
                       tp: TransportParams,
                       routing_event_collector=None):
        """Send shipment along transport route, handling disrupted routes."""
        route = link.get_current_route()

        if route is None or not route:
            route = self._discover_route(
                link, transport_network, available_transport_network,
                tp.capacity_constraint_enabled, tp.use_route_cache,
            )
            if route is None:
                link.realized_delivery = 0.0
                link.delivery = 0.0
                link.payment = 0.0
                return

        # Check if main route is disrupted
        if link.current_route == "main" and not available_transport_network.is_route_available(route):
            alt_route = self._discover_route(
                link, transport_network, available_transport_network,
                tp.capacity_constraint_enabled, tp.use_route_cache,
            )
            if alt_route is not None:
                link.alternative_route = alt_route
                link.alternative_found = True
                alt_cost = transport_network.compute_route_cost(alt_route, link.shipment_method, self.cost_profile)
                link.alternative_route_cost_per_ton = alt_cost
                relative_increase = link.calculate_relative_increase_in_transport_cost()
                switching_penalty = link.calculate_switching_cost(tp.switching_costs, transport_network)
                relative_increase += switching_penalty

                if relative_increase > tp.price_increase_threshold:
                    link.realized_delivery = 0.0
                    link.delivery = 0.0
                    link.payment = 0.0
                    if routing_event_collector:
                        routing_event_collector.record_event(
                            self.pid, link.buyer_id, "too_expensive", relative_increase
                        )
                    return

                link.current_route = "alternative"
                route = alt_route
                # Country uses fixed 20% transport cost passthrough
                price_change = 0.2 * relative_increase
                link.price = link.eq_price * (1 + price_change)
                if routing_event_collector:
                    routing_event_collector.record_event(
                        self.pid, link.buyer_id, "rerouted", relative_increase
                    )
            else:
                link.realized_delivery = 0.0
                link.delivery = 0.0
                link.payment = 0.0
                if routing_event_collector:
                    routing_event_collector.record_event(
                        self.pid, link.buyer_id, "no_route", 0.0
                    )
                return

        # Place shipment on transport network
        if link.delivery_in_tons > EPSILON:
            transport_network.place_shipment(
                route, link.pid, link.delivery_in_tons, link.destination_node
            )

        link.realized_delivery = link.delivery
        link.payment = link.delivery * link.price
        self.qty_sold += link.delivery

        # Track transport metrics
        self.usd_transported += link.delivery
        self.tons_transported += link.delivery_in_tons
        if hasattr(route, 'length'):
            self.tonkm_transported += link.delivery_in_tons * route.length

    def _discover_route(self, link: CommercialLink,
                        transport_network: TransportNetwork,
                        available_transport_network: TransportNetwork,
                        capacity_constraint: bool,
                        use_route_cache: bool):
        weight = "cost_per_ton_" + str(self.cost_profile)
        if capacity_constraint:
            weight = "cost_per_ton_with_capacity_" + str(self.cost_profile)

        effective_cache = use_route_cache and not capacity_constraint

        if effective_cache:
            cached = transport_network.retrieve_cached_route(
                self.od_point, link.destination_node, self.cost_profile, "disrupted", link.shipment_method
            )
            if cached:
                return cached

        route = available_transport_network.provide_shortest_route(
            self.od_point, link.destination_node, link.shipment_method, route_weight=weight
        )

        if route and effective_cache:
            transport_network.cache_route(
                self.od_point, link.destination_node, self.cost_profile, "disrupted", link.shipment_method, route
            )

        return route
