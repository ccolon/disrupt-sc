"""CommercialLink — a buyer-supplier trade relationship."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from disruptsc.config import EPSILON

if TYPE_CHECKING:
    from disruptsc.network.route import Route
    from disruptsc.network.transport_network import TransportNetwork


@dataclass
class CommercialLink:
    # --- Identity ---
    pid: str = ""
    supplier_id: str = ""
    buyer_id: str = ""
    product: str = ""
    product_type: str = ""
    category: str = ""  # domestic_B2B, B2C, import, export, transit
    origin_node: int = 0
    destination_node: int = 0

    # --- Route state ---
    route: Route | None = None
    alternative_route: Route | None = None
    route_length: float = 1.0
    route_cost_per_ton: float = 0.0
    alternative_route_length: float = 1.0
    alternative_route_cost_per_ton: float = 0.0
    current_route: str = "main"
    alternative_found: bool = False
    use_transport_network: bool = False
    shipment_method: str = "solid_bulk"
    essential: bool = True

    # --- Flow state ---
    order: float = 0.0
    delivery: float = 0.0
    delivery_in_tons: float = 0.0
    realized_delivery: float = 0.0
    payment: float = 0.0
    eq_price: float = 1.0
    price: float = 1.0
    fulfilment_rate: float = 1.0
    status: str = "ok"

    # ------------------------------------------------------------------

    def get_current_route(self):
        if self.current_route == "main":
            return self.route
        elif self.current_route == "alternative":
            return self.alternative_route
        return None

    def reset(self):
        self.current_route = "main"
        self.order = 0.0
        self.delivery = 0.0
        self.payment = 0.0
        self.fulfilment_rate = 1.0
        self.alternative_route = None
        self.alternative_route_cost_per_ton = 0.0
        self.price = self.eq_price
        self.alternative_found = False
        self.status = "ok"

    def determine_shipment_method(self, sector_types_to_shipment_method: dict):
        self.shipment_method = sector_types_to_shipment_method.get(
            self.product_type, sector_types_to_shipment_method.get("default", "solid_bulk")
        )

    def store_route_information(self, route: Route, main_or_alternative: str, cost_per_ton: float):
        self.use_transport_network = True
        if main_or_alternative == "main":
            self.route = route
            self.route_length = route.length
            self.route_cost_per_ton = cost_per_ton
        elif main_or_alternative == "alternative":
            self.alternative_found = True
            self.alternative_route = route
            self.alternative_route_length = route.length
            self.alternative_route_cost_per_ton = cost_per_ton

    def calculate_fulfilment_rate(self):
        if self.order < EPSILON:
            self.fulfilment_rate = 1.0
        elif self.delivery > self.order + EPSILON:
            self.fulfilment_rate = 1.0
        else:
            self.fulfilment_rate = self.delivery / self.order

    def update_indicator(self, quantity_delivered: float):
        if abs(self.delivery - quantity_delivered) > EPSILON:
            logging.debug(
                f"Delivery mismatch {self.supplier_id}→{self.buyer_id}: "
                f"expected {self.delivery:.4f}, got {quantity_delivered:.4f}"
            )
        self.calculate_fulfilment_rate()
        self._update_status()

    def calculate_relative_increase_in_transport_cost(self) -> float:
        if self.delivery_in_tons == 0:
            raise ValueError(f"Link {self.supplier_id}→{self.buyer_id}: delivery_in_tons is 0")
        for label, val in [("route_cost_per_ton", self.route_cost_per_ton),
                           ("alt_route_cost_per_ton", self.alternative_route_cost_per_ton)]:
            if isinstance(val, float) and np.isnan(val):
                raise ValueError(f"Link {self.supplier_id}→{self.buyer_id}: {label} is nan")

        normal_bill = self.delivery_in_tons * self.route_cost_per_ton
        new_bill = self.delivery_in_tons * self.alternative_route_cost_per_ton

        if normal_bill == 0:
            raise ValueError(f"Link {self.supplier_id}→{self.buyer_id}: normal_transport_bill is 0")

        result = max(new_bill - normal_bill, 0) / normal_bill
        if isinstance(result, float) and (np.isnan(result) or np.isinf(result)):
            raise ValueError(f"Link {self.supplier_id}→{self.buyer_id}: cost increase is {result}")
        return result

    def has_modal_switch(self) -> bool:
        if not self.alternative_found or not self.route or not self.alternative_route:
            return False
        return set(self.route.transport_modes) != set(self.alternative_route.transport_modes)

    def has_port_switch(self, transport_network: TransportNetwork) -> bool:
        if not self.alternative_found or not self.route or not self.alternative_route:
            return False
        main_edges = self.route.get_maritime_multimodal_edges(transport_network)
        alt_edges = self.alternative_route.get_maritime_multimodal_edges(transport_network)
        return len(main_edges) > 0 and len(alt_edges) > 0 and main_edges != alt_edges

    def calculate_switching_cost(self, switching_costs: dict, transport_network: TransportNetwork) -> float:
        if self.has_modal_switch():
            return switching_costs.get("modal_switch", 0.15)
        elif self.has_port_switch(transport_network):
            return switching_costs.get("port_switch", 0.05)
        return 0.0

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _update_status(self):
        delivery_status = "ok"
        price_status = "ok"
        if abs(self.price - self.eq_price) > EPSILON:
            price_status = "more expensive"
        if EPSILON < self.fulfilment_rate < 1 - EPSILON:
            delivery_status = "partial"
        elif self.fulfilment_rate < EPSILON:
            delivery_status = "no delivery"

        if delivery_status == "ok" and price_status == "ok":
            self.status = "ok"
        else:
            self.status = f"delivery: {delivery_status}, price: {price_status}"
