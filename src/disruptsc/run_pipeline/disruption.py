"""Disruption parsing, application, and recovery."""

from __future__ import annotations

import logging
from collections import defaultdict
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

_MONETARY_UNITS = {"USD": 1.0, "kUSD": 1e3, "mUSD": 1e6}


def _unit_factor(from_unit: str, to_unit: str) -> float:
    """Multiplier converting a value in *from_unit* into *to_unit*."""
    try:
        return _MONETARY_UNITS[from_unit] / _MONETARY_UNITS[to_unit]
    except KeyError as exc:
        raise ValueError(f"Unknown monetary unit {exc}; expected one of {list(_MONETARY_UNITS)}")


@dataclass
class CapitalDestruction:
    """Destroys firm production capacity.

    description: {firm_pid: value}. When ``absolute`` is False (default) the
    value is a fraction of capacity destroyed (0-1, applied via
    ``disrupt_production_capacity``). When ``absolute`` is True the value is an
    absolute amount of built capital in model monetary units (applied via
    ``incur_capital_destruction``, which converts it to a capacity reduction
    using each firm's initial capital).
    """
    description: dict = field(default_factory=dict)
    recovery: Recovery | None = None
    start_time: int = 1
    absolute: bool = False
    reconstruction_market: bool = False
    reconstruction_target_time: float = 52  # in time steps (config supplies days, converted at parse)
    capital_input_mix: dict = field(default_factory=dict)
    # Localized reconstruction: route rebuild demand toward capital-good firms
    # near the damage. locality in [0,1] (scalar or per-sector dict) blends the
    # national-by-size split (0) with a damage-proximity split (1).
    reconstruction_locality: float | dict = 0.0
    reconstruction_region_key: str = "subregion_province"
    damage_by_region: dict = field(default_factory=dict)
    # Fraction of reconstruction met publicly (rebuilt directly, no B2B trace).
    reconstruction_public_share: float = 0.0
    # diagnostics populated by from_subregion_file (model monetary units)
    applied_capital: float = 0.0
    unmatched_capital: float = 0.0
    overflow_capital: float = 0.0

    def implement(self, firms):
        duration = self.recovery.duration if self.recovery else float("inf")
        for pid, value in self.description.items():
            if pid not in firms:
                continue
            if self.absolute:
                firms[pid].incur_capital_destruction(value)
                logging.debug(f"Capital destruction: firm {pid} lost {value:,.3f} (abs)")
            else:
                firms[pid].disrupt_production_capacity(duration, value)
                logging.debug(f"Capital destruction: firm {pid} lost {value:.0%}")

    def log_info(self):
        rec = f"{self.recovery.shape} recovery over {self.recovery.duration}" if self.recovery else "no recovery"
        extra = (f", {self.applied_capital:,.1f} capital destroyed (absolute), "
                 f"{self.unmatched_capital:,.1f} unmatched") if self.absolute else ""
        logging.info(
            f"CapitalDestruction: {len(self.description)} firms at t={self.start_time}, {rec}{extra}"
        )

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

    @classmethod
    def from_subregion_file(cls, path, firms: dict, *,
                            monetary_units: str = "mUSD",
                            canton_key: str = "subregion_canton",
                            unit: str = "mUSD"):
        """Build a heterogeneous, absolute capital-destruction shock from a CSV.

        The CSV is long format with columns ``subregion_canton, sector,
        destroyed_capital_mUSD`` (see runs/earthquake/build_model_shock.py). Each
        (canton, sector) cell is matched to the firm(s) whose
        ``subregions[canton_key]`` and ``sector`` equal that cell, and the cell's
        absolute destroyed capital is split across them in proportion to each
        firm's ``capital_initial`` (so every firm in the cell loses the same
        share of its capital). Cells with no matching firm — or whose firms have
        zero modeled capital — are skipped and tallied as *unmatched*. When a
        cell's destroyed capital exceeds the firms' total capital, the excess is
        tallied as *overflow* (capacity cannot fall below zero).

        Must be called after ``set_initial_conditions`` so ``capital_initial`` is set.
        """
        df = pd.read_csv(path)
        required = {"subregion_canton", "sector", "destroyed_capital_mUSD"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}; have {list(df.columns)}")

        factor = _unit_factor(unit, monetary_units)

        by_cs: dict[tuple, list] = defaultdict(list)
        for pid, firm in firms.items():
            canton = (getattr(firm, "subregions", None) or {}).get(canton_key)
            if canton is not None:
                by_cs[(canton, firm.sector)].append(pid)

        description: dict = defaultdict(float)
        applied = unmatched = overflow = 0.0
        n_matched = n_unmatched = 0
        for row in df.itertuples(index=False):
            amount = float(row.destroyed_capital_mUSD) * factor
            if amount <= 0:
                continue
            pids = by_cs.get((row.subregion_canton, row.sector), [])
            caps = [(pid, max(firms[pid].capital_initial, 0.0)) for pid in pids]
            total_cap = sum(c for _, c in caps)
            if not pids or total_cap <= 0:
                unmatched += amount
                n_unmatched += 1
                continue
            n_matched += 1
            applied += min(amount, total_cap)
            if amount > total_cap:
                overflow += amount - total_cap
            for pid, cap in caps:
                if cap > 0:
                    description[pid] += amount * cap / total_cap

        logging.info(
            f"CapitalDestruction(file): {n_matched} cells -> {len(description)} firms, "
            f"applied ~{applied:,.1f} {monetary_units} of capital; "
            f"unmatched {n_unmatched} cells ({unmatched:,.1f}); "
            f"capacity-capped overflow {overflow:,.1f}"
        )
        if n_matched == 0 and len(df) > 0:
            logging.warning(
                f"CapitalDestruction(file): matched 0 firms for {len(df)} shock rows from {path}. "
                f"Check that firms carry subregions['{canton_key}'] and sector codes that match "
                f"the CSV's subregion_canton/sector values."
            )
        obj = cls(description=dict(description), absolute=True)
        obj.applied_capital = applied
        obj.unmatched_capital = unmatched
        obj.overflow_capital = overflow
        return obj


# ------------------------------------------------------------------
# Reconstruction (ARIO-style) — lean functional port of v1.1.6's
# ReconstructionMarket. No stateful object: the only persistent state is
# firm.capital_destroyed (which decays as capital is rebuilt). The two
# functions below are called from the simulation loop when a
# capital_destruction disruption has reconstruction_market=True.
# ------------------------------------------------------------------

# Bill-of-materials to rebuild one unit of capital (v1.1.6 default):
# 70% construction, 20% manufacturing, 10% imports. Sectors with no modeled
# firm (e.g. the import code) are assumed met externally / unconstrained.
DEFAULT_CAPITAL_INPUT_MIX = {"CON": 0.7, "MAN": 0.2, "IMP": 0.1}


def place_reconstruction_demand(firms: dict, reconstruction_target_time: float,
                                capital_input_mix: dict,
                                locality: float | dict = 0.0,
                                damage_by_region: dict | None = None,
                                region_key: str = "subregion_province",
                                public_share: float = 0.0) -> float:
    """Set per-firm ``reconstruction_demand`` for one time step.

    Each damaged firm wants ``capital_destroyed / reconstruction_target_time`` of
    its capital rebuilt. A ``public_share`` fraction is rebuilt publicly (directly,
    outside the modeled firm network — see ``rebuild_public_capital``) and leaves
    no B2B trace; only the private remainder ``(1-public_share)`` becomes B2B
    demand here. The private aggregate is split across capital-good sectors by
    ``capital_input_mix`` and, within each sector, across firms by a blend of two
    rules controlled by ``locality`` (lambda in [0,1], scalar or per-sector dict):

        share = (1-lambda) * eq_production-share        (national, by size)
              +    lambda  * (eq_production * local_damage)-share  (damage-proximity)

    where ``local_damage`` is the destroyed capital in the firm's region
    (``damage_by_region[firm.subregions[region_key]]``). lambda=0 reproduces the
    pure national-by-size split; lambda=1 routes the sector's rebuild demand only
    to firms in damaged regions (the local construction boom). If a sector has no
    capacity in any damaged region, it falls back to national so the Leontief
    rebuild is never starved. Sectors in the mix with no modeled firm (imports)
    place no order — they are supplied externally in the rebuild step.

    Call BEFORE ``firm.retrieve_orders`` so the demand enters ``total_order`` and
    propagates to inputs. Returns the aggregate capital demand (model units).
    """
    public_share = max(0.0, min(1.0, float(public_share)))
    for f in firms.values():
        f.reconstruction_demand = 0.0
        total_rate = (f.capital_destroyed / reconstruction_target_time
                      if reconstruction_target_time > 0 else 0.0)
        f.public_capital_demanded = public_share * total_rate          # rebuilt directly (external)
        f.capital_demanded = (1.0 - public_share) * total_rate         # drives private B2B rebuild
    aggregate = sum(f.capital_demanded for f in firms.values())
    if aggregate <= 0:
        return 0.0

    damage_by_region = damage_by_region or {}

    def _lambda_for(sector: str) -> float:
        lam = locality.get(sector, 0.0) if isinstance(locality, dict) else locality
        return max(0.0, min(1.0, float(lam)))

    firms_by_sector: dict = {}
    for f in firms.values():
        firms_by_sector.setdefault(f.sector, []).append(f)

    for sector, weight in capital_input_mix.items():
        if weight <= 0:
            continue
        sector_firms = firms_by_sector.get(sector)
        if not sector_firms:
            continue  # imported / not modeled -> met externally in rebuild step
        nat = {f.pid: max(f.eq_production, 0.0) for f in sector_firms}
        nat_tot = sum(nat.values())
        if nat_tot <= 0:
            continue
        loc = {f.pid: max(f.eq_production, 0.0)
               * damage_by_region.get((f.subregions or {}).get(region_key), 0.0)
               for f in sector_firms}
        loc_tot = sum(loc.values())
        lam = _lambda_for(sector)
        if loc_tot <= 0:
            lam = 0.0  # no local supply in damaged regions -> fall back to national
        sector_demand = weight * aggregate
        for f in sector_firms:
            s_nat = nat[f.pid] / nat_tot
            s_loc = (loc[f.pid] / loc_tot) if loc_tot > 0 else 0.0
            f.reconstruction_demand += sector_demand * ((1.0 - lam) * s_nat + lam * s_loc)
    return aggregate


def rebuild_from_reconstruction(firms: dict, capital_input_mix: dict) -> float:
    """Convert reconstruction output into restored capital, lifting capacity.

    A capital-good firm's reconstruction output is the product still in stock
    after it has rationed its real clients (reconstruction competes equally for
    output, so the leftover equals ``reconstruction_demand × rationing``). New
    composite capital is Leontief-limited by the scarcest input in
    ``capital_input_mix``; mix sectors with no modeled firm (imports) are
    unconstrained. The new capital is distributed back to damaged firms in
    proportion to their demand. Call AFTER ``firm.deliver``. Returns new capital.
    """
    modeled_sectors = {f.sector for f in firms.values()}

    produced_per_sector: dict = {}
    for f in firms.values():
        if f.reconstruction_demand <= 0:
            f.reconstruction_produced = 0.0
            continue
        produced = min(f.product_stock, f.reconstruction_demand)
        f.reconstruction_produced = produced
        f.product_stock = max(0.0, f.product_stock - produced)
        produced_per_sector[f.sector] = produced_per_sector.get(f.sector, 0.0) + produced

    aggregate = sum(f.capital_demanded for f in firms.values())
    if aggregate <= 0:
        return 0.0

    # Leontief: new composite capital limited by the scarcest required input.
    ratios = []
    for sector, weight in capital_input_mix.items():
        if weight <= 0:
            continue
        if sector in modeled_sectors:
            ratios.append(produced_per_sector.get(sector, 0.0) / weight)
        else:
            ratios.append(aggregate)  # imports unconstrained (produced = weight*aggregate)
    new_capital = min(ratios) if ratios else 0.0
    if new_capital <= 0:
        return 0.0

    for f in firms.values():
        if f.capital_demanded > 0:
            f.rebuild_capital(f.capital_demanded / aggregate * new_capital)
    return new_capital


def rebuild_public_capital(firms: dict) -> float:
    """Publicly-funded reconstruction: restore each firm's ``public_capital_demanded``
    directly (government / external supply), bypassing the private firm network so it
    lifts capacity without leaving any B2B trace in firm sales. This is the invisible
    (public-sector) share of reconstruction. Call once per step, alongside the private
    :func:`rebuild_from_reconstruction`. Returns the total capital rebuilt publicly.
    """
    total = 0.0
    for f in firms.values():
        amount = getattr(f, "public_capital_demanded", 0.0)
        if amount > 0:
            f.rebuild_capital(amount)
            total += amount
    return total


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
        duration = self.recovery.duration if self.recovery else float("inf")
        for pid, fraction in self.description.items():
            if pid in firms:
                firms[pid].disrupt_production_capacity(duration, fraction)

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
                      monetary_units: str,
                      time_resolution: str = "day") -> list:
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
            elif desc_type in ("subregion_file", "file"):
                d = CapitalDestruction.from_subregion_file(
                    cfg["file"], firms,
                    monetary_units=monetary_units,
                    canton_key=cfg.get("canton_key", "subregion_canton"),
                    unit=cfg.get("unit", "mUSD"),
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
            # reconstruction_target_time is given in DAYS in config; convert to time steps.
            from disruptsc.config import days_per_timestep
            d.reconstruction_target_time = (
                cfg.get("reconstruction_target_time", 365) / days_per_timestep(time_resolution)
            )
            d.capital_input_mix = cfg.get("capital_input_mix", {})
            # Localized reconstruction: route rebuild demand toward firms near the
            # damage. Precompute destroyed capital per region from the shock itself.
            d.reconstruction_locality = cfg.get("reconstruction_locality", 0.0)
            d.reconstruction_region_key = cfg.get("reconstruction_region_key", "subregion_province")
            d.reconstruction_public_share = cfg.get("reconstruction_public_share", 0.0)
            damage_by_region: dict = defaultdict(float)
            for pid, amount in d.description.items():
                firm = firms.get(pid)
                if firm is None:
                    continue
                region = (getattr(firm, "subregions", None) or {}).get(d.reconstruction_region_key)
                if region is not None:
                    damage_by_region[region] += amount
            d.damage_by_region = dict(damage_by_region)
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
