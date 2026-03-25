"""Collects and exports routing events during simulation for diagnostics."""

import csv
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RoutingEventCollector:
    """Records routing decisions made by agents during simulation time steps.

    Tracks four event types:
    - main_route_used: shipment sent via the main (equilibrium) route
    - price_threshold_exceeded: alternative route found but too expensive
    - no_route_available: no usable route exists
    - alternative_route_found: shipment rerouted via an alternative
    """

    def __init__(self):
        self._current_timestep = None
        self._events: list[dict] = []
        self._timestep_summary: dict[str, int] = defaultdict(int)

    def set_timestep(self, timestep: int):
        """Set current timestep for subsequent event records."""
        self._current_timestep = timestep
        self._timestep_summary = defaultdict(int)

    def record_main_route_used(self, supplier_id: str, buyer_id: str, agent_type: str):
        self._events.append({
            "timestep": self._current_timestep,
            "event": "main_route_used",
            "supplier": supplier_id,
            "buyer": buyer_id,
            "agent_type": agent_type,
            "cost_increase_pct": 0.0,
            "reason": "",
        })
        self._timestep_summary["main_route_used"] += 1

    def record_price_threshold_exceeded(
        self, supplier_id: str, buyer_id: str, agent_type: str, cost_increase_pct: float
    ):
        self._events.append({
            "timestep": self._current_timestep,
            "event": "price_threshold_exceeded",
            "supplier": supplier_id,
            "buyer": buyer_id,
            "agent_type": agent_type,
            "cost_increase_pct": cost_increase_pct,
            "reason": "price_threshold_exceeded",
        })
        self._timestep_summary["price_threshold_exceeded"] += 1

    def record_no_route_available(
        self, supplier_id: str, buyer_id: str, agent_type: str, reason: str
    ):
        self._events.append({
            "timestep": self._current_timestep,
            "event": "no_route_available",
            "supplier": supplier_id,
            "buyer": buyer_id,
            "agent_type": agent_type,
            "cost_increase_pct": 0.0,
            "reason": reason,
        })
        self._timestep_summary["no_route_available"] += 1

    def record_alternative_route_found(
        self, supplier_id: str, buyer_id: str, agent_type: str,
        cost_increase_pct: float, reason: str
    ):
        self._events.append({
            "timestep": self._current_timestep,
            "event": "alternative_route_found",
            "supplier": supplier_id,
            "buyer": buyer_id,
            "agent_type": agent_type,
            "cost_increase_pct": cost_increase_pct,
            "reason": reason,
        })
        self._timestep_summary["alternative_route_found"] += 1

    def log_timestep_summary(self):
        """Log a summary of routing events for the current timestep."""
        if not self._timestep_summary:
            return
        parts = [f"{k}: {v}" for k, v in sorted(self._timestep_summary.items())]
        logger.info(f"Routing events t={self._current_timestep}: {', '.join(parts)}")

    def export_to_csv(self, filepath: str):
        """Export all collected events to a CSV file."""
        if not self._events:
            logger.info("No routing events to export.")
            return

        fieldnames = ["timestep", "event", "supplier", "buyer",
                       "agent_type", "cost_increase_pct", "reason"]
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._events)
        logger.info(f"Exported {len(self._events)} routing events to {filepath}")
