"""Disruption parsing, application, and recovery."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import geopandas as gpd


# ------------------------------------------------------------------
# Recovery
# ------------------------------------------------------------------

@dataclass
class Recovery:
    duration: int = 1
    shape: str = "threshold"  # "threshold", "linear", "exponential"
    rate: float = 1.0

    def factor(self, time_since_start: int) -> float:
        """0 = full disruption, 1 = fully recovered."""
        if time_since_start >= self.duration:
            return 1.0
        progress = time_since_start / self.duration
        if self.shape == "threshold":
            return 0.0
        elif self.shape == "linear":
            return progress * self.rate
        elif self.shape == "exponential":
            return (1 - np.exp(-self.rate * progress)) / (1 - np.exp(-self.rate))
        raise ValueError(f"Unknown recovery shape: {self.shape}")


# ------------------------------------------------------------------
# Transport disruption
# ------------------------------------------------------------------

@dataclass
class TransportDisruption:
    """Disrupts transport edges by reducing capacity.

    description: {edge_id: fraction_of_capacity_lost}  (0-1)
    """
    description: dict[int, float] = field(default_factory=dict)
    recovery: Recovery | None = None
    start_time: int = 1

    def implement(self, transport_network):
        duration = self.recovery.duration if self.recovery else float("inf")
        recovery_shape = self.recovery.shape if self.recovery else "threshold"
        recovery_rate = self.recovery.rate if self.recovery else 1.0
        for edge in transport_network.edges:
            edata = transport_network[edge[0]][edge[1]]
            eid = edata["id"]
            if eid in self.description:
                reduction = self.description[eid]
                transport_network.start_edge_disruption(
                    edata, reduction, duration,
                    recovery_shape=recovery_shape,
                    recovery_rate=recovery_rate,
                )
                logging.debug(f"Disrupted edge {eid}: {reduction:.0%} capacity loss for {duration} steps")

    def log_info(self):
        rec = f"{self.recovery.shape} recovery over {self.recovery.duration}" if self.recovery else "no recovery"
        logging.info(f"TransportDisruption: {len(self.description)} edges at t={self.start_time}, {rec}")

    @classmethod
    def from_edge_attributes(cls, edges: gpd.GeoDataFrame, attribute: str,
                             values: list, reduction: float = 1.0):
        if attribute == "disruption":
            mask = pd.concat(
                [edges[attribute].str.contains(v, na=False) for v in values], axis=1
            ).any(axis=1)
        else:
            mask = edges[attribute].isin(values)
        ids = edges.loc[mask, "id"].tolist()
        return cls(description={eid: reduction for eid in ids})


# ------------------------------------------------------------------
# Capital destruction
# ------------------------------------------------------------------

@dataclass
class CapitalDestruction:
    """Destroys firm production capacity.

    description: {firm_pid: fraction_destroyed}  (0-1)
    """
    description: dict = field(default_factory=dict)
    recovery: Recovery | None = None
    start_time: int = 1
    reconstruction_market: bool = False
    reconstruction_target_time: int = 52
    capital_input_mix: dict = field(default_factory=dict)

    def implement(self, firms):
        for pid, fraction in self.description.items():
            if pid in firms:
                firm = firms[pid]
                firm.disruption_duration = self.recovery.duration if self.recovery else float("inf")
                firm.disruption_reduction = fraction
                firm.current_production_capacity *= (1 - fraction)
                logging.debug(f"Capital destruction: firm {pid} lost {fraction:.0%}")

    def log_info(self):
        rec = f"{self.recovery.shape} recovery over {self.recovery.duration}" if self.recovery else "no recovery"
        logging.info(f"CapitalDestruction: {len(self.description)} firms at t={self.start_time}, {rec}")

    @classmethod
    def from_firms_attributes(cls, destroyed_fraction, filters: dict, firms: dict,
                              input_units: str = "mUSD", target_units: str = "mUSD"):
        """Select firms matching filters and apply uniform destruction."""
        matched = []
        for pid, firm in firms.items():
            match = True
            for attr, values in filters.items():
                if attr.startswith("subregion_"):
                    sub_key = attr.replace("subregion_", "")
                    if getattr(firm, "subregions", {}).get(sub_key) not in values:
                        match = False
                        break
                elif getattr(firm, attr, None) not in values:
                    match = False
                    break
            if match:
                matched.append(pid)
        logging.info(f"CapitalDestruction filter matched {len(matched)} firms")
        return cls(description={pid: destroyed_fraction for pid in matched})


# ------------------------------------------------------------------
# Productivity shock
# ------------------------------------------------------------------

@dataclass
class ProductivityShock:
    """Temporary reduction in firm productivity (not capacity).

    description: {firm_pid: reduction_fraction}
    """
    description: dict = field(default_factory=dict)
    recovery: Recovery | None = None
    start_time: int = 1

    def implement(self, firms):
        for pid, fraction in self.description.items():
            if pid in firms:
                firm = firms[pid]
                firm.disruption_duration = self.recovery.duration if self.recovery else float("inf")
                firm.disruption_reduction = fraction
                firm.current_production_capacity *= (1 - fraction)

    def log_info(self):
        rec = f"{self.recovery.shape} recovery over {self.recovery.duration}" if self.recovery else "no recovery"
        logging.info(f"ProductivityShock: {len(self.description)} firms at t={self.start_time}, {rec}")

    @classmethod
    def from_firms_attributes(cls, reduction, filters: dict, firms: dict):
        matched = [pid for pid, f in firms.items()
                   if all(getattr(f, a, None) in v for a, v in filters.items())]
        return cls(description={pid: reduction for pid in matched})


# ------------------------------------------------------------------
# Disruption list: parse from YAML config
# ------------------------------------------------------------------

def parse_disruptions(config_list: list | None,
                      transport_edges: gpd.GeoDataFrame,
                      firm_table: pd.DataFrame | None,
                      firms: dict,
                      monetary_units: str) -> list:
    """Parse the ``disruptions`` key from YAML into disruption objects.

    Returns a flat list of disruption objects (TransportDisruption, CapitalDestruction, etc.).
    """
    if not config_list:
        return []

    disruptions = []
    for cfg in config_list:
        dtype = cfg.get("type", "")

        if dtype == "transport_disruption":
            reduction = cfg.get("capacity_reduction", cfg.get("fraction_capacity_lost", 1.0))
            d = TransportDisruption.from_edge_attributes(
                transport_edges, cfg["attribute"], cfg["values"], reduction=reduction,
            )
            d.start_time = cfg.get("start_time", 1)
            if "duration" in cfg:
                d.recovery = Recovery(
                    duration=cfg["duration"],
                    shape=cfg.get("recovery_shape", "threshold"),
                    rate=cfg.get("recovery_rate", 1.0),
                )
            disruptions.append(d)

        elif dtype == "transport_disruption_probability":
            reduction = cfg.get("capacity_reduction", cfg.get("fraction_capacity_lost", 1.0))
            base = TransportDisruption.from_edge_attributes(
                transport_edges, cfg["attribute"], cfg["values"], reduction=reduction,
            )
            starts, durations = _generate_probabilistic_disruptions(
                cfg["scenario_duration"], cfg["probability_duration_pairs"],
            )
            for s, dur in zip(starts, durations):
                d = TransportDisruption(
                    description=dict(base.description),
                    start_time=s,
                    recovery=Recovery(
                        duration=dur,
                        shape=cfg.get("recovery_shape", "threshold"),
                        rate=cfg.get("recovery_rate", 1.0),
                    ),
                )
                disruptions.append(d)

        elif dtype == "capital_destruction":
            desc_type = cfg.get("description_type", "filter")
            if desc_type == "filter":
                d = CapitalDestruction.from_firms_attributes(
                    cfg["destroyed_capital"], cfg["filter"], firms,
                )
            else:
                raise ValueError(f"Unsupported capital_destruction description_type: {desc_type}")
            d.start_time = cfg.get("start_time", 1)
            if "duration" in cfg:
                d.recovery = Recovery(
                    duration=cfg["duration"],
                    shape=cfg.get("recovery_shape", "threshold"),
                    rate=cfg.get("recovery_rate", 1.0),
                )
            d.reconstruction_market = cfg.get("reconstruction_market", False)
            d.reconstruction_target_time = cfg.get("reconstruction_target_time", 52)
            d.capital_input_mix = cfg.get("capital_input_mix", {})
            disruptions.append(d)

        elif dtype == "productivity_shock":
            desc_type = cfg.get("description_type", "filter")
            if desc_type == "filter":
                d = ProductivityShock.from_firms_attributes(
                    cfg["productivity_reduction"], cfg["filter"], firms,
                )
            else:
                raise ValueError(f"Unsupported productivity_shock description_type: {desc_type}")
            d.start_time = cfg.get("start_time", 1)
            if "duration" in cfg:
                d.recovery = Recovery(
                    duration=cfg["duration"],
                    shape=cfg.get("recovery_shape", "threshold"),
                    rate=cfg.get("recovery_rate", 1.0),
                )
            disruptions.append(d)

        else:
            raise ValueError(f"Unknown disruption type: {dtype}")

    return disruptions


def apply_disruptions(disruptions: list, time_step: int,
                      transport_network, firms: dict):
    """Apply disruptions whose start_time matches *time_step*.

    Returns the available (undisrupted) transport network view.
    """
    for d in disruptions:
        if d.start_time != time_step:
            continue
        if isinstance(d, TransportDisruption):
            d.implement(transport_network)
        elif isinstance(d, (CapitalDestruction, ProductivityShock)):
            d.implement(firms)

    return transport_network.get_undisrupted_network()


# ------------------------------------------------------------------
# Probabilistic disruption generator
# ------------------------------------------------------------------

def _generate_probabilistic_disruptions(scenario_duration: int,
                                        probability_duration_pairs: list) -> tuple[list, list]:
    """Generate random disruption start-times and durations from probability pairs.

    Each pair is {probability: p, duration: d}.  At every time step we draw
    whether a new disruption starts (if none currently active).
    """
    starts, durations = [], []
    t = 1
    active_end = 0
    while t <= scenario_duration:
        if t >= active_end:
            for pair in probability_duration_pairs:
                # pair can be [probability, duration] list or {"probability": p, "duration": d} dict
                if isinstance(pair, (list, tuple)):
                    prob, dur = pair[0], pair[1]
                else:
                    prob, dur = pair["probability"], pair["duration"]
                if np.random.random() < prob:
                    starts.append(t)
                    durations.append(dur)
                    active_end = t + dur
                    break
        t += 1
    return starts, durations
