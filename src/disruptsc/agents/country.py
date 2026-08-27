"""Country agent — import/export node, transit, delivery."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from disruptsc.config import EPSILON
from disruptsc.agents.transport_utils import (
    send_shipment, deliver_without_transport,
    collect_shipment_from_node,
)

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
    monetary_unit_factor: float = 1.0  # multiplier to convert model monetary units to USD
    transport_share: float = 0.2
    virtual: bool = False  # flows to/from this country bypass the transport network

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
    qty_received: float = 0.0  # goods received from domestic firms this step (exports of the modeled economy)
    generalized_transport_cost: float = 0.0
    usd_transported: float = 0.0
    tons_transported: float = 0.0
    tonkm_transported: float = 0.0
    extra_spending: float = 0.0
    consumption_loss: float = 0.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def id_str(self) -> str:
        return f"Country {self.pid} at node {self.od_point}"

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------

    def reset_variables(self):
        self.qty_sold = 0.0
        self.qty_received = 0.0
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
            link.order = self.purchase_plan.get(supplier.pid, 0.0)

    def deliver(self, sc_network: ScNetwork,
                transport_network: TransportNetwork,
                available_transport_network: TransportNetwork,
                tp: TransportParams,
                routing_event_collector=None):
        """Export/deliver products to firms and households."""
        # Book realized_delivery, not link.delivery: multi-route links can drop
        # blocked chunks, so realized < planned. Tons are scaled accordingly.
        def _realized_tons(link):
            if link.delivery > EPSILON:
                return link.delivery_in_tons * link.realized_delivery / link.delivery
            return 0.0

        def _after_delivery(link):
            self.qty_sold += link.realized_delivery

        def _after_shipment(link, route):
            self.qty_sold += link.realized_delivery
            self.usd_transported += link.realized_delivery
            self.tons_transported += _realized_tons(link)
            if hasattr(route, 'length'):
                self.tonkm_transported += _realized_tons(link) * route.length

        for _, client, data in sc_network.out_edges(self, data=True):
            link: CommercialLink = data["object"]
            # Country delivers whatever was ordered (unlimited supply from outside)
            link.delivery = link.order
            link.served_order = link.order
            link.delivery_in_tons = link.delivery * self.monetary_unit_factor / self.usd_per_ton if self.usd_per_ton > 0 else 0.0
            link.reset_transport_tracking()

            if link.delivery < EPSILON:
                continue

            if link.product_type in tp.sectors_no_transport:
                deliver_without_transport(link, _after_delivery)
            elif getattr(self, "virtual", False) or getattr(client, "virtual", False):
                deliver_without_transport(link, _after_delivery)
            elif not tp.with_transport:
                deliver_without_transport(link, _after_delivery)
            elif client.__class__.__name__ == "Household" and not tp.transport_to_households:
                deliver_without_transport(link, _after_delivery)
            else:
                send_shipment(
                    self.pid, self.od_point, self.transport_share,
                    link, transport_network, available_transport_network, tp,
                    routing_event_collector, _after_shipment,
                )

    def receive_products(self, sc_network: ScNetwork,
                         transport_network: TransportNetwork,
                         sectors_no_transport: tuple,
                         transport_to_households: bool):
        """Receive import shipments (transit goods from other countries/firms)."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            collect_shipment_from_node(self.od_point, link, transport_network, sectors_no_transport)
            quantity_received = link.realized_delivery
            if supplier.__class__.__name__ == "Firm":
                self.qty_received += quantity_received
            # Track losses
            expected = self.purchase_plan.get(supplier.pid, 0.0)
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
            "qty_sold": self.qty_sold,
            "qty_received": self.qty_received,
            "generalized_transport_cost": self.generalized_transport_cost,
            "usd_transported": self.usd_transported,
            "tons_transported": self.tons_transported,
            "tonkm_transported": self.tonkm_transported,
        }

