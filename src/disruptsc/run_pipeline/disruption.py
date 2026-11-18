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

def _parse_per_cargo_fraction(value, label: str):
    """A fraction that may be per cargo type: a number passes through unchanged (the
    scalar path stays bit-identical); a dict ({cargo_type: x, "default": x}) is checked
    here - every value a number in [0, 1] - and its cargo-type keys against the network
    when the disruption is implemented (_check_cargo_keys)."""
    if not isinstance(value, dict):
        return value
    if not value:
        raise ValueError(f"{label}: an empty per-cargo dict; give a number or {{cargo_type: x, default: x}}")
    out = {}
    for key, val in value.items():
        if isinstance(val, bool) or not isinstance(val, (int, float)) or not (0.0 <= float(val) <= 1.0):
            raise ValueError(f"{label}['{key}'] must be a number in [0, 1] (got {val!r})")
        out[str(key)] = float(val)
    return out


def _check_cargo_keys(value, transport_network, label: str):
    """Raise when a per-cargo dict names a cargo type the network does not have."""
    if not isinstance(value, dict):
        return
    known = set(transport_network.cargo_types or [])
    unknown = sorted(k for k in value if k != "default" and k not in known)
    if unknown:
        raise ValueError(f"{label} names unknown cargo type(s) {unknown}; the cargo types of this scope are "
                         f"{sorted(known)} (from logistics.sector_to_cargo_type)")


def _fmt_fraction(value) -> str:
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {float(v):.0%}" for k, v in value.items()) + "}"
    return f"{float(value):.0%}"


@dataclass
class TransportDisruption:
    """Disrupts transport edges by reducing capacity.

    description: {edge_id: fraction_of_capacity_lost}  (0-1), the fraction a
    number or a per-cargo dict ({cargo_type: fraction, "default": fraction};
    a cargo type not listed takes "default", and is untouched without one).
    A per-cargo cut binds through the edge's per-cargo capacities (the gate);
    see TransportNetwork._apply_edge_capacity_factors_per_cargo.
    """
    description: dict[int, object] = field(default_factory=dict)
    recovery: Recovery | None = None
    start_time: int = 1
    # Share of a closed edge's traffic that the substitutes can absorb
    # (1.0 = unlimited, the legacy behaviour); the rest is not delivered.
    substitution_share: float = 1.0

    def implement(self, transport_network):
        duration = self.recovery.duration if self.recovery else float("inf")
        recovery_shape = self.recovery.shape if self.recovery else "threshold"
        recovery_rate = self.recovery.rate if self.recovery else 1.0
        started = False
        unbound: dict = {}
        for edge in transport_network.edges:
            edata = transport_network[edge[0]][edge[1]]
            eid = edata["id"]
            if eid in self.description:
                reduction = self.description[eid]
                if isinstance(reduction, dict):
                    _check_cargo_keys(reduction, transport_network, "transport_disruption capacity_reduction")
                    factors = {k: 1.0 - v for k, v in reduction.items()}
                    for ct in transport_network.unbound_cargo_reductions(edata, factors):
                        unbound.setdefault(ct, []).append(eid)
                transport_network.start_edge_disruption(
                    edata, reduction, duration,
                    recovery_shape=recovery_shape,
                    recovery_rate=recovery_rate,
                )
                edata["closure_substitution_share"] = float(self.substitution_share)
                started = True
                logging.debug(f"Disrupted edge {eid}: {_fmt_fraction(reduction)} capacity loss for {duration} steps")
        for ct, eids in sorted(unbound.items()):
            # the scalar analogue (a partial cut on an uncapacitated edge) is a documented no-op;
            # a per-cargo cut that cannot bind is said out loud, it is usually a missing capacity
            logging.warning(
                f"transport_disruption: the {ct} cut cannot bind on {len(eids)} edge(s) without a capacity "
                f"for {ct} (ids {eids[:10]}{'...' if len(eids) > 10 else ''}); only a closure of every cargo "
                f"acts there. Name the edge in transport_capacity_overrides to make the cut bind.")
        if started:
            # KI-50: detours cached under the previous closure set are reused while open (KI-42) even when they
            # are no longer the cheapest - successive closures would reuse the first event's detours.
            transport_network.invalidate_alternative_routes()

    def log_info(self):
        rec = f"{self.recovery.shape} recovery over {self.recovery.duration}" if self.recovery else "no recovery"
        logging.info(f"TransportDisruption: {len(self.description)} edges at t={self.start_time}, {rec}")

    @classmethod
    def from_edge_attributes(cls, edges: gpd.GeoDataFrame, attribute: str,
                             values: list, reduction=1.0):
        if attribute == "disruption":
            mask = pd.concat(
                [edges[attribute].str.contains(v, na=False) for v in values], axis=1
            ).any(axis=1)
        else:
            mask = edges[attribute].isin(values)
        ids = edges.loc[mask, "id"].tolist()
        return cls(description={eid: reduction for eid in ids})


# ------------------------------------------------------------------
# Transport cost shock
# ------------------------------------------------------------------

@dataclass
class TransportCostShock:
    """Multiplies the cost of transport edges without closing them.

    description: {edge_id: multiplier} where multiplier is a number or a
    per-cargo dict ({cargo_type: m, "default": m}); duration in time steps
    (inf = permanent). A low-water river is the archetype: barges sail at a
    third of their load, so every ton costs three times more, buyers pay the
    surcharge, reroute where rail or road is cheaper, or give up beyond
    ``price_increase_threshold``. Pairs with ``transport_disruption`` for the
    weeks where the edge is de facto closed.
    """
    description: dict[int, object] = field(default_factory=dict)
    duration: float = 1
    start_time: int = 1
    # Substitution ceiling (default = unlimited substitutes, the legacy
    # behaviour): the shocked mode still carries capacity_factor of each
    # link's tonnage (at the surcharged cost) and the substitutes absorb at
    # most substitution_share of the displaced remainder; the rest is not
    # delivered. capacity_factor None = 1/multiplier for a scalar multiplier
    # (1.0 for a per-cargo multiplier). capacity_factor may itself be per cargo
    # ({cargo_type: f, "default": f}, resolved with the link's cargo type).
    capacity_factor: float | dict | None = None
    substitution_share: float = 1.0

    def implement(self, transport_network):
        n = 0
        _check_cargo_keys(self.capacity_factor, transport_network, "transport_cost_shock capacity_factor")
        for edge in transport_network.edges:
            edata = transport_network[edge[0]][edge[1]]
            eid = edata["id"]
            if eid in self.description:
                mult = self.description[eid]
                cap = self.capacity_factor
                if cap is None:
                    cap = 1.0 / float(mult) if not isinstance(mult, dict) else 1.0
                transport_network.start_edge_cost_shock(
                    edata, mult, self.duration,
                    capacity_factor=cap, substitution_share=self.substitution_share)
                n += 1
        # (until 18 Nov 2026 this line formatted capacity_factor with :.2f, which raised a
        # TypeError when substitution_share < 1 came without capacity_factor)
        cap_txt = (_fmt_fraction(self.capacity_factor) if isinstance(self.capacity_factor, dict)
                   else f"{self.capacity_factor:.2f}" if self.capacity_factor is not None else "1/multiplier")
        logging.info(f"Cost shock applied to {n} edge(s) for {self.duration} step(s)"
                     + (f" (capacity {cap_txt}, substitution {self.substitution_share:.2f})"
                        if self.substitution_share < 1.0 else ""))

    def log_info(self):
        mults = {str(m) for m in self.description.values()}
        logging.info(f"TransportCostShock: {len(self.description)} edges at t={self.start_time}, "
                     f"x{'/'.join(sorted(mults))} for {self.duration} step(s)")

    @classmethod
    def from_edge_attributes(cls, edges: gpd.GeoDataFrame, attribute: str,
                             values: list, multiplier, duration: float = 1):
        if attribute == "disruption":
            mask = pd.concat(
                [edges[attribute].str.contains(v, na=False) for v in values], axis=1
            ).any(axis=1)
        else:
            mask = edges[attribute].isin(values)
        ids = edges.loc[mask, "id"].tolist()
        if not ids:
            logging.warning(f"transport_cost_shock: no edge matched {attribute} in {values} - no-op")
        return cls(description={eid: multiplier for eid in ids}, duration=duration)


# ------------------------------------------------------------------
# Capital destruction
# ------------------------------------------------------------------

_MONETARY_UNITS = {"USD": 1.0, "kUSD": 1e3, "mUSD": 1e6}


def _match_firms_by_filters(filters: dict, firms: dict, label: str) -> list:
    """Return the pids of firms matching an attribute filter dict.

    Keys are firm attributes (``sector``, ``region``, ...); a ``subregion_*``
    key matches against ``firm.subregions`` (e.g. ``subregion_province``).
    Shared by every filter-based disruption so they all support subregions
    and all LOG their match count — a filter that matches zero firms is a
    silent no-op shock otherwise.
    """
    matched = []
    for pid, firm in firms.items():
        ok = True
        for attr, values in filters.items():
            if attr.startswith("subregion_"):
                sub_key = attr.replace("subregion_", "")
                if (getattr(firm, "subregions", {}) or {}).get(sub_key) not in values:
                    ok = False
                    break
            elif getattr(firm, attr, None) not in values:
                ok = False
                break
        if ok:
            matched.append(pid)
    logging.info(f"{label} filter matched {len(matched)} firms")
    if not matched:
        logging.warning(
            f"{label} filter {filters} matched NO firm — this disruption "
            f"is a no-op. Check attribute names and values."
        )
    return matched


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
    reconstruction_lag: float = 0.0         # steps after start_time before reconstruction begins (days at parse)
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
        matched = _match_firms_by_filters(filters, firms, "CapitalDestruction")
        return cls(description={pid: destroyed_fraction for pid in matched})

    @classmethod
    def from_subregion_file(cls, path, firms: dict, *,
                            monetary_units: str = "mUSD",
                            canton_key: str = "subregion_canton",
                            unit: str = "mUSD",
                            amount_scale: float = 1.0,
                            overflow_policy: str = "discard"):
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

        # amount_scale multiplies every destroyed-capital cell, so shock SEVERITY can be swept
        # (x0.5 .. x2) without editing the shock file. Locations and the sector/canton pattern
        # are unchanged -- only the magnitude scales.
        factor = _unit_factor(unit, monetary_units) * float(amount_scale)

        by_cs: dict[tuple, list] = defaultdict(list)
        by_canton: dict[str, list] = defaultdict(list)
        for pid, firm in firms.items():
            canton = (getattr(firm, "subregions", None) or {}).get(canton_key)
            if canton is not None:
                by_cs[(canton, firm.sector)].append(pid)
                by_canton[canton].append(pid)

        spill = str(overflow_policy).lower() == "spill_canton"
        description: dict = defaultdict(float)
        leftover: dict = defaultdict(float)          # canton -> capital that found no home in its own cell
        no_cell = cell_overflow = 0.0                # why it had no home (diagnostics)
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
                # no firm of that sector in that canton
                leftover[row.subregion_canton] += amount
                no_cell += amount
                n_unmatched += 1
                continue
            n_matched += 1
            if amount > total_cap:
                leftover[row.subregion_canton] += amount - total_cap
                cell_overflow += amount - total_cap
                amount = total_cap                   # the cell can absorb no more
            for pid, cap in caps:
                if cap > 0:
                    description[pid] += amount * cap / total_cap

        # ---- overflow policy -------------------------------------------------
        # The canton TOTAL is the quantity the damage assessment measures most reliably (the
        # sector split within a canton is the uncertain part, and the model's sector coverage is
        # incomplete -- e.g. 94% of ELE capital sits in Cuenca/Guayaquil/Quito, so Manabi's
        # electricity damage has almost nowhere to land). Spilling the residue onto other firms
        # in the SAME canton preserves the geography at the cost of the within-canton sectoral
        # split; discarding it silently shrinks the shock exactly where it is largest.
        placed = 0.0
        if spill:
            for canton, amount in leftover.items():
                if amount <= 0:
                    continue
                room = [(pid, max(firms[pid].capital_initial - description.get(pid, 0.0), 0.0))
                        for pid in by_canton.get(canton, [])]
                total_room = sum(r for _, r in room)
                if total_room <= 0:
                    continue                         # the whole canton is already written off
                take = min(amount, total_room)
                for pid, r in room:
                    if r > 0:
                        description[pid] += take * r / total_room
                placed += take
        # Keep the reported fields meaning what they always meant: `unmatched` is damage with no
        # firm of that sector in that canton, `overflow` is damage exceeding available capital.
        # Under spill_canton whatever was re-placed is no longer lost, so only the residue counts.
        if spill:
            residual = (no_cell + cell_overflow) - placed
            unmatched = min(no_cell, residual)
            overflow = max(residual - unmatched, 0.0)
        else:
            unmatched = no_cell
            overflow = cell_overflow

        applied = sum(min(v, max(firms[pid].capital_initial, 0.0)) for pid, v in description.items())

        logging.info(
            f"CapitalDestruction(file): {n_matched} cells -> {len(description)} firms, "
            f"applied ~{applied:,.1f} {monetary_units} of capital "
            f"[unplaced in own cell: {no_cell:,.1f} no-firm + {cell_overflow:,.1f} over-capacity; "
            f"policy={'spill_canton' if spill else 'discard'} -> "
            f"discarded {unmatched:,.1f}, still-unplaceable {overflow:,.1f}]"
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
            f.reconstruction_sales = 0.0
            continue
        produced = min(f.product_stock, f.reconstruction_demand)
        f.reconstruction_produced = produced
        # Revenue for the capital goods sold to reconstruction (investment demand, funded
        # externally). evaluate_profit adds this so the firm's VA/profit isn't understated.
        f.reconstruction_sales = produced * f.price
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
        matched = _match_firms_by_filters(filters, firms, "ProductivityShock")
        return cls(description={pid: reduction for pid in matched})


# ------------------------------------------------------------------
# Stock injection (a dated strategic release)
# ------------------------------------------------------------------

def _input_matches(input_id: str, key: str) -> bool:
    """An input id (``SAU_B06``, ``ROW_imports``) matches its full id or its sector part."""
    return input_id == key or (input_id.split("_", 1)[-1] if "_" in input_id else input_id) == key


@dataclass
class StockInjection:
    """A one-off addition to the input stocks of the agents of a region (MC1, Hormuz 2026).

    The IEA collective release of March 2026 put oil from strategic reserves into the
    market at a date; giving the importers larger stocks from t = 0 instead would move
    its effect in time (decision Q17, 18 Nov 2026). At the start of step ``start_time``,
    once, every agent located in ``region`` (``agent.region``) that uses ``input`` gets
    ``days`` days of its usual use of that input added to its stock:

        added = eq_use_per_step x days / days_per_step

    i.e. the region receives ``days`` x its usual daily use, shared among its users in
    proportion to their usual use. "Usual use" is the equilibrium use (``eq_needs``),
    not the current one: a release is a fixed volume quoted in days of normal demand,
    and the current use is depressed exactly where the shortage bites (a stopped
    refinery would get nothing), which would also make the injected total depend on
    the simulated state. Firms use an input when it is in their input mix (``input``
    = its sector code, e.g. B06, or a full input id, e.g. SAU_B06; an import bundle by
    its id or ``imports``); households receive it only if they hold stocks
    (``enable_household_inventories``); the national government / investment agents
    and the country agents hold no stocks and receive nothing. The stock enters the
    buyers' inventories like a delivery, so the next order covers less of the gap; it
    is not removed afterwards (stocks above target are not sold back).
    """
    region: str = ""
    input: str = ""
    days: float = 0.0
    start_time: int = 1
    days_per_step: float = 7.0
    # diagnostics of the last implement (model monetary units)
    injected: float = 0.0
    n_agents: int = 0

    def implement(self, firms: dict, households: dict | None = None):
        steps = self.days / self.days_per_step
        total, agents = 0.0, 0
        for firm in firms.values():
            if firm.region != self.region:
                continue
            got = False
            for input_id, coef in firm.input_mix.items():
                if coef <= 0 or not _input_matches(input_id, self.input):
                    continue
                q = firm.eq_needs.get(input_id, 0.0) * steps
                if q <= 0:
                    continue
                firm.inventory[input_id] = firm.inventory.get(input_id, 0.0) + q
                total += q
                got = True
            agents += got
        for hh in (households or {}).values():
            if (hh.region != self.region or not hh.use_inventories
                    or getattr(hh, "agent_type", "household") != "household"):
                continue
            got = False
            for sector_id, use in hh.eq_needs.items():
                if use <= 0 or not _input_matches(sector_id, self.input):
                    continue
                q = use * steps
                hh.inventory[sector_id] = hh.inventory.get(sector_id, 0.0) + q
                total += q
                got = True
            agents += got
        self.injected, self.n_agents = total, agents
        if agents:
            logging.info(f"StockInjection t={self.start_time}: {self.days:g} days of {self.input} to {agents} "
                         f"agent(s) in {self.region}, {total:,.6g} model units added to their stocks")
        else:
            logging.warning(f"StockInjection t={self.start_time}: no agent in region '{self.region}' uses "
                            f"input '{self.input}' (or holds stocks) - this injection is a no-op")

    def log_info(self):
        logging.info(f"StockInjection: {self.days:g} days of {self.input} in {self.region} at t={self.start_time}")


def _parse_stock_injection(cfg: dict, time_resolution: str) -> StockInjection:
    missing = [k for k in ("region", "input", "days", "start_time") if k not in cfg]
    if missing:
        raise ValueError(f"stock_injection needs {missing} (region, input sector, days of use, start_time step)")
    days, start = cfg["days"], cfg["start_time"]
    if isinstance(days, bool) or not isinstance(days, (int, float)) or not days >= 0:
        raise ValueError(f"stock_injection days must be a number >= 0 (got {days!r})")
    if isinstance(start, bool) or not isinstance(start, int) or start < 1:
        raise ValueError(f"stock_injection start_time must be an integer step >= 1 (got {start!r}); "
                         f"step 0 is the undisturbed baseline")
    from disruptsc.config import days_per_timestep
    return StockInjection(region=str(cfg["region"]), input=str(cfg["input"]), days=float(days),
                          start_time=start, days_per_step=days_per_timestep(time_resolution))


# ------------------------------------------------------------------
# Export ban
# ------------------------------------------------------------------
# Port of the ``export_stop`` rule of J. Seidler's MSc thesis (jsei6020/
# disrupt-sc_Gloria at d8e91438, branch gloria) with the corrections audited on
# the local branch codex/export-controls-fixes (Oct 2026): the semantics are
# ported, not the code (that branch runs on the pre-v2 engine). Thesis rule: a
# controlled exporter delivers nothing to buyers outside its region; domestic
# buyers keep their rationed share; the blocked goods stay in the exporter's
# stock (no destruction, no re-allocation), so its next production target
# (orders minus stock) falls by what it could not ship. Generalized here
# (Hormuz 2026, decisions Q7/Q13, 18 Nov 2026) to a fraction per destination
# region - the banned product's share of the sector's bilateral exports - and
# to a window. Overlapping bans keep the later expiry (thesis fix 1eedfe6);
# per-step evaluation from the windows makes that order-independent and
# idempotent by construction, and leaves no countdown on the firms to reset.

_EXPORT_BAN_KEYS = frozenset({
    "type", "regions", "sectors", "fraction", "destinations", "product",
    "start_time", "duration", "end_time",
})


def _as_str_list(value, key: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, int)):
        return [str(value)]
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    raise ValueError(f"export_ban: '{key}' must be a code or a list of codes (got {value!r})")


def _check_fraction(value, where: str) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"export_ban: {where} must be a number in [0, 1] (got {value!r})")
    if not (0.0 <= f <= 1.0):
        raise ValueError(f"export_ban: {where} must be in [0, 1] (got {f})")
    return f


def _check_step(value, key: str) -> int:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not np.isfinite(value) or float(value) != int(value)):
        raise ValueError(f"export_ban: '{key}' must be a whole number of time steps (got {value!r}); "
                         f"omit 'duration' and 'end_time' for an open-ended ban")
    return int(value)


@dataclass
class ExportBan:
    """Withholds a fraction of the foreign deliveries of exporting firms.

    The exporters are the firms of ``regions`` (x ``sectors``; all sectors if
    none given). In every step of the window ``start_time``..``end_time``
    (inclusive, time steps; ``end_time`` inf = open-ended) each exporter
    withholds ``fractions[r]`` of what its rationing allotted to every buyer in
    region ``r`` (firms, households and Country agents alike), and
    ``default_fraction`` for the foreign regions not named. Deliveries to buyers
    of the exporter's own region are never withheld. What is withheld stays in
    the exporter's product stock (thesis rule, verification case V06).

    ``product`` labels the good a fraction refers to. Bans with the same label
    on the same exporter are one restriction: while they overlap the larger
    fraction applies and the restriction lasts until the later expiry (thesis
    fix 1eedfe6; no rescission - a relaxation is encoded by ending the earlier
    window). Bans with different labels are different goods: their fractions
    add, capped at 1. The default label "" covers the sector as a whole.
    """
    firm_pids: list = field(default_factory=list)
    fractions: dict = field(default_factory=dict)   # destination region -> withheld fraction
    default_fraction: float = 0.0                   # every other foreign destination
    product: str = ""
    start_time: int = 1
    end_time: float = float("inf")                  # last banned step, inclusive
    regions: list = field(default_factory=list)     # for the log only
    sectors: list = field(default_factory=list)

    def is_active(self, time_step: int) -> bool:
        return self.start_time <= time_step <= self.end_time

    def log_info(self):
        window = (f"steps {self.start_time}-{self.end_time}" if self.end_time != float("inf")
                  else f"from step {self.start_time}, open-ended")
        dest = ", ".join(f"{r}: {f:g}" for r, f in sorted(self.fractions.items()))
        dest = (dest + ", " if dest else "") + f"other foreign: {self.default_fraction:g}"
        label = f" product {self.product!r}" if self.product else ""
        logging.info(f"ExportBan: {len(self.firm_pids)} exporting firms of {self.regions} x "
                     f"{self.sectors or 'all sectors'}{label}, {window}, withheld {{{dest}}}")

    @classmethod
    def from_config(cls, cfg: dict, firms: dict) -> "ExportBan":
        unknown = sorted(set(cfg) - _EXPORT_BAN_KEYS)
        if unknown:
            raise ValueError(f"export_ban: unknown key(s) {unknown}; expected {sorted(_EXPORT_BAN_KEYS)}")
        regions = _as_str_list(cfg.get("regions"), "regions")
        if not regions:
            raise ValueError("export_ban needs 'regions': the exporting region(s)")
        sectors = _as_str_list(cfg.get("sectors"), "sectors")

        if ("fraction" in cfg) == ("destinations" in cfg):
            raise ValueError("export_ban needs exactly one of 'fraction' (every foreign destination) "
                             "or 'destinations' ({region: fraction, default: fraction})")
        if "fraction" in cfg:
            fractions, default = {}, _check_fraction(cfg["fraction"], "'fraction'")
        else:
            dest = cfg["destinations"]
            if not isinstance(dest, dict) or not dest:
                raise ValueError(f"export_ban: 'destinations' must be a non-empty mapping (got {dest!r})")
            fractions, default = {}, 0.0
            for region, value in dest.items():
                if str(region) == "default":
                    default = _check_fraction(value, "destinations.default")
                else:
                    fractions[str(region)] = _check_fraction(value, f"destinations.{region}")

        start = _check_step(cfg.get("start_time", 1), "start_time")
        if start < 1:
            raise ValueError(f"export_ban: 'start_time' must be >= 1 (t=0 is the undisturbed baseline; got {start})")
        if "duration" in cfg and "end_time" in cfg:
            raise ValueError("export_ban takes 'duration' or 'end_time', not both")
        if "duration" in cfg:
            duration = _check_step(cfg["duration"], "duration")
            if duration < 1:
                raise ValueError(f"export_ban: 'duration' must be >= 1 step (got {duration})")
            end = start + duration - 1          # thesis convention: start s, duration d -> s..s+d-1
        elif "end_time" in cfg:
            end = _check_step(cfg["end_time"], "end_time")
            if end < start:
                raise ValueError(f"export_ban: 'end_time' {end} is before 'start_time' {start}")
        else:
            end = float("inf")

        domestic = sorted(set(fractions) & set(regions))
        if domestic:
            logging.warning(f"export_ban: destination(s) {domestic} are exporting regions; deliveries "
                            f"inside an exporter's own region are never withheld")

        filters = {"region": regions}
        if sectors:
            filters["sector"] = sectors
        pids = _match_firms_by_filters(filters, firms, "ExportBan")
        return cls(firm_pids=pids, fractions=fractions, default_fraction=default,
                   product=str(cfg.get("product", "")), start_time=start, end_time=end,
                   regions=regions, sectors=sectors)


def update_export_bans(disruptions: list, time_step: int, firms: dict) -> None:
    """Set each exporter's withheld shares for *time_step* from the active bans.

    Called every step (from :func:`apply_disruptions`). Every firm a ban names
    is cleared first, so a ban stops exactly after its last step. Shares per
    firm: ``{destination region: share, None: share for the other foreign
    regions}``; same product label -> max, different labels -> sum capped at 1.
    """
    bans = [d for d in disruptions if isinstance(d, ExportBan)]
    if not bans:
        return
    for d in bans:
        for pid in d.firm_pids:
            if pid in firms:
                firms[pid].export_ban_shares = {}
    active: dict = {}
    for d in bans:
        if d.is_active(time_step):
            for pid in d.firm_pids:
                if pid in firms:
                    active.setdefault(pid, {}).setdefault(d.product, []).append(d)
    for pid, by_product in active.items():
        named = set()
        for group in by_product.values():
            for d in group:
                named.update(d.fractions)

        def combined(region):
            total = sum(max((d.fractions.get(region, d.default_fraction) if region is not None
                             else d.default_fraction) for d in group)
                        for group in by_product.values())
            return min(1.0, total)

        shares = {region: combined(region) for region in named}
        shares[None] = combined(None)
        firms[pid].export_ban_shares = shares


def export_ban_holds(disruptions: list, time_step: int) -> bool:
    """True while an export ban is active at or after *time_step*.

    The early stop must not end a run inside a ban window: buyers' input
    stocks can hide a ban's losses for several steps (thesis audit V04, Oct
    2026). Steps run before the check, so a ban whose last step is
    *time_step* also holds the run for one more step.
    """
    return any(isinstance(d, ExportBan) and time_step <= d.end_time for d in disruptions or [])


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
            reduction = _parse_per_cargo_fraction(
                cfg.get("capacity_reduction", cfg.get("fraction_capacity_lost", 1.0)),
                "transport_disruption capacity_reduction")
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
            d.substitution_share = float(cfg.get("substitution_share", 1.0))
            disruptions.append(d)

        elif dtype == "transport_cost_shock":
            mult = cfg.get("cost_multiplier", cfg.get("multiplier"))
            if mult is None:
                raise ValueError("transport_cost_shock needs 'cost_multiplier' (number or per-cargo dict)")
            d = TransportCostShock.from_edge_attributes(
                transport_edges, cfg["attribute"], cfg["values"], mult,
                duration=cfg.get("duration", 1),
            )
            d.start_time = cfg.get("start_time", 1)
            d.capacity_factor = _parse_per_cargo_fraction(cfg.get("capacity_factor"),
                                                          "transport_cost_shock capacity_factor")
            d.substitution_share = float(cfg.get("substitution_share", 1.0))
            disruptions.append(d)

        elif dtype == "transport_disruption_probability":
            reduction = _parse_per_cargo_fraction(
                cfg.get("capacity_reduction", cfg.get("fraction_capacity_lost", 1.0)),
                "transport_disruption_probability capacity_reduction")
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
                # "repo:<relpath>" / "studies:<relpath>" resolve against the code or studies repo, so a
                # tracked scope config can reference a shock file committed
                # under studies/ without machine-specific absolute paths.
                from disruptsc.config import resolve_repo_prefix
                d = CapitalDestruction.from_subregion_file(
                    resolve_repo_prefix(cfg["file"]), firms,
                    monetary_units=monetary_units,
                    canton_key=cfg.get("canton_key", "subregion_canton"),
                    unit=cfg.get("unit", "mUSD"),
                    amount_scale=cfg.get("amount_scale", 1.0),
                    overflow_policy=cfg.get("overflow_policy", "discard"),
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
            # Loud no-op warnings: firm-side recovery is threshold-only, and
            # absolute (file-based) destruction has no timed recovery at all —
            # capital returns only via the reconstruction market.
            if d.absolute and ("duration" in cfg or "recovery_shape" in cfg):
                logging.warning(
                    "capital_destruction with description_type=file is an absolute, "
                    "permanent capital loss: 'duration'/'recovery_shape' are IGNORED "
                    "(rebuild happens via reconstruction_market)."
                )
            elif cfg.get("recovery_shape", "threshold") != "threshold":
                logging.warning(
                    f"capital_destruction: firm-side recovery is threshold-only; "
                    f"recovery_shape={cfg['recovery_shape']!r} is IGNORED "
                    f"(capacity is restored in full when 'duration' elapses)."
                )
            d.reconstruction_market = cfg.get("reconstruction_market", False)
            # reconstruction_target_time is given in DAYS in config; convert to time steps.
            from disruptsc.config import days_per_timestep
            d.reconstruction_target_time = (
                cfg.get("reconstruction_target_time", 365) / days_per_timestep(time_resolution)
            )
            # reconstruction_lag is given in DAYS in config; convert to time steps.
            d.reconstruction_lag = (
                cfg.get("reconstruction_lag", 0) / days_per_timestep(time_resolution)
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
            if cfg.get("recovery_shape", "threshold") != "threshold":
                logging.warning(
                    f"productivity_shock: firm-side recovery is threshold-only; "
                    f"recovery_shape={cfg['recovery_shape']!r} is IGNORED "
                    f"(capacity is restored in full when 'duration' elapses)."
                )
            disruptions.append(d)

        elif dtype == "stock_injection":
            disruptions.append(_parse_stock_injection(cfg, time_resolution))
        elif dtype == "export_ban":
            disruptions.append(ExportBan.from_config(cfg, firms))

        else:
            raise ValueError(f"Unknown disruption type: {dtype}")

    return disruptions


def apply_disruptions(disruptions: list, time_step: int,
                      transport_network, firms: dict, households: dict | None = None):
    """Apply disruptions whose start_time matches *time_step*.

    Export bans act over a window rather than at one step: their withheld
    shares are re-evaluated every step (:func:`update_export_bans`).

    Returns the available (undisrupted) transport network view.
    """
    for d in disruptions:
        if d.start_time != time_step:
            continue
        if isinstance(d, (TransportDisruption, TransportCostShock)):
            d.implement(transport_network)
        elif isinstance(d, (CapitalDestruction, ProductivityShock)):
            d.implement(firms)
        elif isinstance(d, StockInjection):
            d.implement(firms, households)
    update_export_bans(disruptions, time_step, firms)

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
