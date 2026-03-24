"""Household agent — consumption, purchasing, welfare tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from disruptsc.config import EPSILON

if TYPE_CHECKING:
    from disruptsc.network.commercial_link import CommercialLink
    from disruptsc.network.sc_network import ScNetwork
    from disruptsc.network.transport_network import TransportNetwork


@dataclass(eq=False)
class Household:
    # --- Identity ---
    pid: str
    region: str
    od_point: int = 0
    name: str = "noname"
    long: float | None = None
    lat: float | None = None
    population: float = 0.0
    subregion: str | None = None
    subregions: dict = field(default_factory=dict)

    # --- Consumption structure (set during init_pipeline) ---
    sector_consumption: dict[str, float] = field(default_factory=dict)
    retailers: dict = field(default_factory=dict)  # supplier_id -> {sector, weight}
    purchase_plan: dict[str, float] = field(default_factory=dict)

    # --- Per-timestep tracking ---
    consumption_per_retailer: dict[str, float] = field(default_factory=dict)
    consumption_per_sector: dict[str, float] = field(default_factory=dict)
    consumption_loss_per_sector: dict[str, float] = field(default_factory=dict)
    spending_per_retailer: dict[str, float] = field(default_factory=dict)
    spending_per_sector: dict[str, float] = field(default_factory=dict)
    extra_spending_per_sector: dict[str, float] = field(default_factory=dict)
    tot_consumption: float = 0.0
    tot_spending: float = 0.0
    consumption_loss: float = 0.0
    extra_spending: float = 0.0

    # --- Routing ---
    cost_profile: int = 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def id_str(self) -> str:
        return f"Household {self.pid} in {self.region}"

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize_from_purchase_plan(self):
        """Initialize tracking variables from purchase plan."""
        self.consumption_per_retailer = {sid: qty for sid, qty in self.purchase_plan.items()}
        self.spending_per_retailer = {sid: qty for sid, qty in self.purchase_plan.items()}
        self.tot_consumption = sum(self.purchase_plan.values())
        self.tot_spending = self.tot_consumption
        # Per-sector aggregation
        for sid, qty in self.purchase_plan.items():
            sector = self.retailers[sid]["sector"]
            self.consumption_per_sector[sector] = self.consumption_per_sector.get(sector, 0.0) + qty
            self.spending_per_sector[sector] = self.spending_per_sector.get(sector, 0.0) + qty
        self.consumption_loss_per_sector = {s: 0.0 for s in self.sector_consumption}
        self.extra_spending_per_sector = {s: 0.0 for s in self.sector_consumption}

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------

    def reset_variables(self):
        """Reset per-timestep tracking."""
        self.consumption_per_retailer = {}
        self.consumption_per_sector = {s: 0.0 for s in self.sector_consumption}
        self.consumption_loss_per_sector = {s: 0.0 for s in self.sector_consumption}
        self.spending_per_retailer = {}
        self.spending_per_sector = {s: 0.0 for s in self.sector_consumption}
        self.extra_spending_per_sector = {s: 0.0 for s in self.sector_consumption}
        self.tot_consumption = 0.0
        self.tot_spending = 0.0
        self.consumption_loss = 0.0
        self.extra_spending = 0.0

    def send_purchase_orders(self, sc_network: ScNetwork):
        """Set order quantities on all incoming commercial links."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            link.order = self.purchase_plan.get(supplier, 0.0)

    def receive_products(self, sc_network: ScNetwork,
                         transport_network: TransportNetwork,
                         sectors_no_transport: tuple,
                         transport_to_households: bool):
        """Receive products from all suppliers."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            # Households receive via direct delivery (placed by supplier's deliver)
            quantity_received = link.realized_delivery
            price = link.price

            # Track consumption
            sector = link.product
            self.consumption_per_retailer[supplier] = quantity_received
            self.spending_per_retailer[supplier] = quantity_received * price
            self.consumption_per_sector[sector] = self.consumption_per_sector.get(sector, 0.0) + quantity_received
            self.spending_per_sector[sector] = self.spending_per_sector.get(sector, 0.0) + quantity_received * price
            self.tot_consumption += quantity_received
            self.tot_spending += quantity_received * price

            # Track losses
            expected = self.purchase_plan.get(supplier, 0.0)
            loss = max(0.0, expected - quantity_received)
            self.consumption_loss_per_sector[sector] = self.consumption_loss_per_sector.get(sector, 0.0) + loss
            self.consumption_loss += loss

            # Track extra spending (price increase)
            eq_spending = expected * link.eq_price
            actual_spending = quantity_received * price
            extra = max(0.0, actual_spending - eq_spending)
            self.extra_spending_per_sector[sector] = self.extra_spending_per_sector.get(sector, 0.0) + extra
            self.extra_spending += extra

            link.update_indicator(quantity_received)

    def consume(self):
        """Consume received products (placeholder for inventory-based consumption)."""
        # In the basic model, consumption = what was received (tracked above)
        pass

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def collect_data(self, time_step: int) -> dict:
        return {
            "time_step": time_step,
            "household": self.pid,
            "region": self.region,
            "consumption_loss": self.consumption_loss,
            "extra_spending": self.extra_spending,
            "consumption_loss_per_sector": dict(self.consumption_loss_per_sector),
            "extra_spending_per_sector": dict(self.extra_spending_per_sector),
        }
