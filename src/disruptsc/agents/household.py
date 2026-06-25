"""Household agent — consumption, purchasing, welfare tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from disruptsc.config import EPSILON
from disruptsc.agents.transport_utils import collect_shipment_from_node

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
    use_inventories: bool = False
    inventory: dict[str, float] = field(default_factory=dict)
    inventory_duration_target: dict[str, float] = field(default_factory=dict)
    inventory_restoration_time: float = 1.0
    eq_needs: dict[str, float] = field(default_factory=dict)

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
        self.consumption_per_sector = {}
        self.spending_per_sector = {}
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

    def initialize_inventory(self):
        """Set up household inventories from equilibrium consumption targets."""
        self.eq_needs = dict(self.sector_consumption)
        if not self.use_inventories:
            self.inventory = {}
            return

        self.inventory = {
            sector: need * max(self.inventory_duration_target.get(sector, 1.0), 1.0)
            for sector, need in self.eq_needs.items()
        }

    def set_equilibrium_purchase_plan(self):
        """Reset household orders to equilibrium consumption needs."""
        self._set_purchase_plan_from_sector_totals(self.sector_consumption)

    def plan_purchase(self):
        """Order enough to cover consumption and optionally restore inventories."""
        if not self.use_inventories:
            self.set_equilibrium_purchase_plan()
            return

        sector_totals = {}
        for sector, need in self.sector_consumption.items():
            eq_need = self.eq_needs.get(sector, need)
            target_inventory = eq_need * max(self.inventory_duration_target.get(sector, 1.0), 1.0)
            current_inv = self.inventory.get(sector, 0.0)
            restoration = max(0.0, target_inventory - current_inv) / max(self.inventory_restoration_time, 1.0)
            sector_totals[sector] = need + restoration

        self._set_purchase_plan_from_sector_totals(sector_totals)

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
            link.order = self.purchase_plan.get(supplier.pid, 0.0)

    def receive_products(self, sc_network: ScNetwork,
                         transport_network: TransportNetwork,
                         sectors_no_transport: tuple,
                         transport_to_households: bool):
        """Receive products from all suppliers."""
        for supplier, _, data in sc_network.in_edges(self, data=True):
            link: CommercialLink = data["object"]
            supplier_id = supplier.pid
            if transport_to_households:
                collect_shipment_from_node(self.od_point, link, transport_network, sectors_no_transport)
            quantity_received = link.realized_delivery
            price = link.price

            # Track purchases and replenish inventory if enabled.
            sector = link.product
            self.spending_per_retailer[supplier_id] = quantity_received * price
            self.spending_per_sector[sector] = self.spending_per_sector.get(sector, 0.0) + quantity_received * price
            self.tot_spending += quantity_received * price

            if self.use_inventories:
                self.inventory[sector] = self.inventory.get(sector, 0.0) + quantity_received
            else:
                self.consumption_per_retailer[supplier_id] = quantity_received
                self.consumption_per_sector[sector] = self.consumption_per_sector.get(sector, 0.0) + quantity_received
                self.tot_consumption += quantity_received

                expected = self.purchase_plan.get(supplier_id, 0.0)
                loss = max(0.0, expected - quantity_received)
                self.consumption_loss_per_sector[sector] = self.consumption_loss_per_sector.get(sector, 0.0) + loss
                self.consumption_loss += loss

            # Track extra spending (price increase)
            expected = self.purchase_plan.get(supplier_id, 0.0)
            eq_spending = expected * link.eq_price
            actual_spending = quantity_received * price
            extra = max(0.0, actual_spending - eq_spending)
            self.extra_spending_per_sector[sector] = self.extra_spending_per_sector.get(sector, 0.0) + extra
            self.extra_spending += extra

            link.update_indicator(quantity_received)

    def consume(self):
        """Consume from inventory when household inventories are enabled."""
        if not self.use_inventories:
            return

        for sector, need in self.sector_consumption.items():
            available = self.inventory.get(sector, 0.0)
            consumed = min(need, available)
            self.inventory[sector] = max(0.0, available - consumed)
            self.consumption_per_sector[sector] = self.consumption_per_sector.get(sector, 0.0) + consumed
            self.tot_consumption += consumed

            loss = max(0.0, need - consumed)
            self.consumption_loss_per_sector[sector] = self.consumption_loss_per_sector.get(sector, 0.0) + loss
            self.consumption_loss += loss

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def collect_data(self, time_step: int) -> dict:
        return {
            "time_step": time_step,
            "household": self.pid,
            "region": self.region,
            "tot_consumption": self.tot_consumption,
            "tot_spending": self.tot_spending,
            "consumption_loss": self.consumption_loss,
            "extra_spending": self.extra_spending,
            "consumption_per_sector": dict(self.consumption_per_sector),
            "spending_per_sector": dict(self.spending_per_sector),
            "consumption_loss_per_sector": dict(self.consumption_loss_per_sector),
            "extra_spending_per_sector": dict(self.extra_spending_per_sector),
        }

    def _set_purchase_plan_from_sector_totals(self, sector_totals: dict[str, float]):
        """Distribute sector-level purchases across retailers using existing weights."""
        self.purchase_plan = {}
        for sector, amount in sector_totals.items():
            retailer_ids = [
                sid for sid, info in self.retailers.items()
                if info.get("sector") == sector
            ]
            if not retailer_ids:
                continue

            total_weight = sum(self.retailers[sid].get("weight", 1.0) for sid in retailer_ids)
            for sid in retailer_ids:
                weight = self.retailers[sid].get("weight", 1.0)
                share = weight / total_weight if total_weight > EPSILON else 0.0
                self.purchase_plan[sid] = amount * share
