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
    # NOTE on pickling: see __getstate__/__setstate__ at the bottom of this
    # class. The 10 transient fields listed in _TRANSIENT_FIELDS are reset
    # every simulation step by reset_transport_tracking(); excluding them
    # from pickle saves recursion depth and size at scale.

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
    cargo_type: str = "dry_bulk"
    essential: bool = True
    route_plan: list = field(default_factory=list)  # [(Route, fraction), ...]

    # --- Flow state ---
    order: float = 0.0
    # The order this step's delivery is serving. `order` itself is overwritten
    # mid-step with the NEXT step's order (agents send new orders before
    # deliveries execute), so any delivery/order ratio must use served_order —
    # dividing by `order` mixes epochs and mis-measures fill rates exactly when
    # orders are changing, i.e. during disruption transients.
    served_order: float = 0.0
    delivery: float = 0.0
    delivery_in_tons: float = 0.0
    realized_delivery: float = 0.0
    payment: float = 0.0
    eq_price: float = 1.0
    price: float = 1.0
    fulfilment_rate: float = 1.0
    status: str = "ok"
    main_route_realized_delivery: float = 0.0
    alternative_route_realized_delivery: float = 0.0

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
        self.served_order = 0.0
        self.delivery = 0.0
        self.fulfilment_rate = 1.0
        self.price = self.eq_price
        self.status = "ok"
        self.reset_transport_tracking()

    def reset_transport_tracking(self):
        """Reset per-timestep transport execution fields."""
        self.realized_delivery = 0.0
        self.payment = 0.0
        self.price = self.eq_price
        self.status = "ok"
        self.current_route = "main"
        self.alternative_route = None
        self.alternative_route_length = 1.0
        self.alternative_route_cost_per_ton = 0.0
        self.alternative_found = False
        self.main_route_realized_delivery = 0.0
        self.alternative_route_realized_delivery = 0.0

    def determine_cargo_type(self, sector_to_cargo_type: dict):
        self.cargo_type = sector_to_cargo_type.get(
            self.product_type, sector_to_cargo_type.get("default", "container")
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
        # Compare against the order this delivery was serving, not `order`,
        # which already holds the next step's order at receive time.
        if self.served_order < EPSILON:
            self.fulfilment_rate = 1.0
        elif self.delivery > self.served_order + EPSILON:
            self.fulfilment_rate = 1.0
        else:
            self.fulfilment_rate = self.delivery / self.served_order

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
            return 0.0

        result = max(new_bill - normal_bill, 0) / normal_bill
        if isinstance(result, float) and (np.isnan(result) or np.isinf(result)):
            raise ValueError(f"Link {self.supplier_id}→{self.buyer_id}: cost increase is {result}")
        return result

    def has_modal_switch(self) -> bool:
        return self._routes_have_modal_switch(self.route, self.alternative_route)

    def has_port_switch(self, transport_network: TransportNetwork) -> bool:
        return self._routes_have_port_switch(self.route, self.alternative_route, transport_network)

    def calculate_switching_cost(self, switching_costs: dict, transport_network: TransportNetwork) -> float:
        if self.has_modal_switch():
            return switching_costs.get("modal_switch", 0.15)
        elif self.has_port_switch(transport_network):
            return switching_costs.get("port_switch", 0.05)
        return 0.0

    def calculate_switching_cost_between(self, baseline_route: Route | None,
                                         alternative_route: Route | None,
                                         switching_costs: dict,
                                         transport_network: TransportNetwork) -> float:
        if self._routes_have_modal_switch(baseline_route, alternative_route):
            return switching_costs.get("modal_switch", 0.15)
        if self._routes_have_port_switch(baseline_route, alternative_route, transport_network):
            return switching_costs.get("port_switch", 0.05)
        return 0.0

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _routes_have_modal_switch(baseline_route: Route | None,
                                  alternative_route: Route | None) -> bool:
        if baseline_route is None or alternative_route is None:
            return False
        return set(baseline_route.transport_modes) != set(alternative_route.transport_modes)

    @staticmethod
    def _routes_have_port_switch(baseline_route: Route | None,
                                 alternative_route: Route | None,
                                 transport_network: TransportNetwork) -> bool:
        if baseline_route is None or alternative_route is None:
            return False
        baseline_edges = baseline_route.get_maritime_multimodal_edges(transport_network)
        alternative_edges = alternative_route.get_maritime_multimodal_edges(transport_network)
        return (
            len(baseline_edges) > 0
            and len(alternative_edges) > 0
            and baseline_edges != alternative_edges
        )

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

    # ------------------------------------------------------------------
    # Pickle hooks — exclude transient per-timestep fields
    # ------------------------------------------------------------------
    # These fields are reset by reset_transport_tracking() at the start of
    # every simulation step, so persisting them through pickle is wasted
    # work (and adds recursion depth at scale: ~316k links × 10 fields).
    _TRANSIENT_FIELDS = frozenset({
        "served_order",
        "alternative_route",
        "alternative_route_length",
        "alternative_route_cost_per_ton",
        "alternative_found",
        "realized_delivery",
        "payment",
        "main_route_realized_delivery",
        "alternative_route_realized_delivery",
        "status",
        "current_route",
    })

    def __getstate__(self) -> dict:
        return {k: v for k, v in self.__dict__.items()
                if k not in self._TRANSIENT_FIELDS}

    def __setstate__(self, state: dict):
        self.__dict__.update(state)
        # Restore transient fields to the same values reset_transport_tracking()
        # would write at the start of the next step.
        self.served_order = 0.0
        self.alternative_route = None
        self.alternative_route_length = 1.0
        self.alternative_route_cost_per_ton = 0.0
        self.alternative_found = False
        self.realized_delivery = 0.0
        self.payment = 0.0
        self.main_route_realized_delivery = 0.0
        self.alternative_route_realized_delivery = 0.0
        self.status = "ok"
        self.current_route = "main"
