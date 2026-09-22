"""Within-step capacity gate: the physical enforcement of edge capacities.

Design (docs/architecture/transport-capacity.md, decisions of 21 Sep 2026):
after every agent has delivered, each capacitated edge (the edges named in
``transport_capacity_overrides``) compares what is on it with its capacity.
Where the load exceeds it, the shipments placed in the CURRENT round are cut
proportionally so that the edge is exactly full; shipments accepted in earlier
rounds are never cut again (round priority: the shippers whose normal route
uses the edge share the first cut pro rata, diverted traffic takes what is
left). A saturated edge is then excluded from every search of the rest of the
step, and each cut share looks for a route on the network minus the saturated
edges through the existing penalty-aware alternative search, with the
switching penalty and the give-up rules applied to that share. Rounds repeat
until no gate cuts. Because accepted loads are frozen and saturated edges
excluded, the saturated set only grows and each cutting round fills at least
one new edge exactly (the one with the smallest factor), so the loop ends
after at most |C| + 1 rounds, |C| the number of capacitated edges. What still
finds no acceptable route returns to the supplier's stock and is counted as
``capacity_blocked`` on the link.

On-off: no cost multiplier anywhere. The allocation depends on what is
offered in a round, not on the order in which agents delivered, so the
outcome is independent of that order (no Monte Carlo over it is needed).
"""

from __future__ import annotations

import hashlib
import logging
import math
from collections import defaultdict

from disruptsc.agents.transport_utils import discover_routes_batched, too_expensive
from disruptsc.config import EPSILON

TON_TOL = 1e-9   # tons; below this a load or a difference is zero


def run_capacity_gate(transport_network, available_transport_network, firms: dict,
                      countries: dict, tp, time_step: int,
                      routing_event_collector=None) -> dict:
    """Ration the capacitated edges and re-send the cut shares until convergence.

    Runs after every agent has placed its shipments. Returns a summary
    ``{"rounds", "n_saturated", "cut_tons", "resent_tons", "blocked_tons",
    "edges": {edge id: {...}}}`` - cut and re-sent tons are gross over the
    rounds (a re-sent share cut again at a later gate counts in both), blocked
    is their difference, the tonnage that ended undelivered - and stores the
    per-edge part on ``transport_network.capacity_gate_stats`` for the
    logistics report.
    """
    tn = transport_network
    cap_edges = tn.capacitated_edges()
    tn.capacity_gate_stats = {}
    if not cap_edges:
        return {"rounds": 0, "n_saturated": 0, "cut_tons": 0.0, "resent_tons": 0.0,
                "blocked_tons": 0.0, "edges": {}}

    cargo_types = tn.cargo_types or []
    stats = {tn[u][v].get("id"): {"offered_tons": 0.0, "accepted_tons": 0.0,
                                  "withheld_tons": 0.0, "rounds": 0, "saturated": False}
             for u, v in cap_edges}
    saturated: set[tuple] = set()
    max_rounds = len(cap_edges) + 1
    cut_tons_total = resent_total = 0.0
    rnd = 0
    while rnd < max_rounds:
        rnd += 1
        cuts: dict[int, list] = {}       # id(record) -> [record, factor]
        over: list[tuple] = []
        for u, v in cap_edges:
            key = (min(u, v), max(u, v))
            if key in saturated:
                continue                  # frozen at capacity, closed to new flow
            edge = tn[u][v]
            records = [r for r in edge["shipments"].values() if r["tons"] > TON_TOL]
            if not records:
                continue
            factors, offered_now = _gate_factors(edge, records, cargo_types, rnd)
            st = stats[edge.get("id")]
            st["offered_tons"] += offered_now
            if not factors:
                continue
            over.append((u, v))
            st["rounds"] += 1
            by_id = {id(r): r for r in records}
            for rid, f in factors.items():
                if rid in cuts:
                    cuts[rid][1] = min(cuts[rid][1], f)
                else:
                    cuts[rid] = [by_id[rid], f]
        if not cuts:
            break

        # 1. cut: the record is one object on every edge of its route, so scaling
        #    it once updates the whole route; the destination is adjusted apart
        cut_parts = []
        for rec, f in cuts.values():
            cut_tons = rec["tons"] * (1.0 - f)
            cut_qty = rec["quantity"] * (1.0 - f)
            rec["tons"] *= f
            rec["quantity"] *= f
            tn.adjust_destination_shipment(rec["destination"], rec["dest_key"], -cut_qty, -cut_tons)
            _book_cut(rec, cut_qty, cut_tons, firms, countries)
            cut_parts.append((rec, cut_tons, cut_qty))
            cut_tons_total += cut_tons

        # 2. saturate: an over edge whose accepted load now reaches a capacity is
        #    closed to further flow; one that keeps slack (its shipments were cut
        #    harder by another gate) stays open for the next round
        for u, v in over:
            edge = tn[u][v]
            if _is_saturated(edge, cargo_types):
                saturated.add((min(u, v), max(u, v)))
                stats[edge.get("id")]["saturated"] = True

        # 3. re-send the cut shares on the network minus the saturated edges: one
        #    batched search per origin and search filter, then the usual choice
        tag = _exclusion_tag(saturated)
        excluded = frozenset(saturated)
        requests = [(rec["origin"] if rec.get("origin") is not None else rec["link"].origin_node, rec["link"])
                    for rec, _, _ in cut_parts]
        alternatives = discover_routes_batched(requests, tn, available_transport_network, tp.use_route_cache,
                                               switching_costs=tp.switching_costs,
                                               excluded_edges=excluded, exclusion_tag=tag)
        for (rec, cut_tons, cut_qty), alt in zip(cut_parts, alternatives):
            resent_total += _resend(rec, cut_tons, cut_qty, rnd + 1, alt, tn, tp, firms, countries,
                                    routing_event_collector)
    else:
        logging.warning(f"Capacity gate t={time_step}: {max_rounds} rounds without convergence "
                        f"(the bound is |C| + 1 = {max_rounds}); the remaining cuts are blocked")

    # accepted loads and the per-edge report
    for u, v in cap_edges:
        edge = tn[u][v]
        st = stats[edge.get("id")]
        st["accepted_tons"] = math.fsum(r["tons"] for r in edge["shipments"].values())
        st["withheld_tons"] = max(0.0, st["offered_tons"] - st["accepted_tons"])
    tn.capacity_gate_stats = stats
    blocked = max(0.0, cut_tons_total - resent_total)
    n_sat = len(saturated)
    if cut_tons_total > TON_TOL:
        logging.info(f"Capacity gate t={time_step}: {rnd} round(s), {n_sat} saturated edge(s), "
                     f"cut {cut_tons_total:,.0f} t, re-sent {resent_total:,.0f} t, "
                     f"blocked {blocked:,.0f} t")
    return {"rounds": rnd, "n_saturated": n_sat, "cut_tons": cut_tons_total,
            "resent_tons": resent_total, "blocked_tons": blocked, "edges": stats}


# ------------------------------------------------------------------
# Gate arithmetic
# ------------------------------------------------------------------

def _constraints(edge: dict, cargo_types: list) -> list[tuple[float, object]]:
    """(capacity, member test) for every capacity the edge carries: one per cargo
    type with a ``capacity_<cargo>`` key, one for all cargo together with ``capacity``."""
    out = []
    for ct in cargo_types:
        key = f"capacity_{ct}"
        if key in edge:
            out.append((float(edge[key]), (lambda r, _ct=ct: r["cargo_type"] == _ct)))
    if "capacity" in edge:
        out.append((float(edge["capacity"]), (lambda r: True)))
    return out


def _gate_factors(edge: dict, records: list, cargo_types: list, rnd: int) -> tuple[dict, float]:
    """Cut factors for the current-round records of an over-capacity edge.

    Returns ({id(record): factor}, tons offered in this round). Sums use fsum so
    the factors do not depend on the order of the records (agent delivery order).
    """
    factors: dict[int, float] = {}
    offered_now = math.fsum(r["tons"] for r in records if r["round"] == rnd)
    for cap, member in _constraints(edge, cargo_types):
        current = [r for r in records if r["round"] == rnd and member(r)]
        if not current:
            continue
        cur_tons = math.fsum(r["tons"] for r in current)
        if cur_tons <= TON_TOL:
            continue
        prev_tons = math.fsum(r["tons"] for r in records if r["round"] < rnd and member(r))
        if prev_tons + cur_tons > cap + TON_TOL:
            room = max(cap - prev_tons, 0.0)
            f = room / cur_tons
            for r in current:
                factors[id(r)] = min(factors.get(id(r), 1.0), f)
    return factors, offered_now


def _is_saturated(edge: dict, cargo_types: list) -> bool:
    records = [r for r in edge["shipments"].values() if r["tons"] > TON_TOL]
    for cap, member in _constraints(edge, cargo_types):
        total = math.fsum(r["tons"] for r in records if member(r))
        if total >= cap - max(TON_TOL, 1e-9 * cap):
            return True
    return False


def _exclusion_tag(saturated: set) -> str:
    """A short name for a saturated set, for the alternative-route cache libraries."""
    if not saturated:
        return ""
    blob = ",".join(f"{a}-{b}" for a, b in sorted(saturated)).encode()
    return "gate" + hashlib.blake2b(blob, digest_size=6).hexdigest()


# ------------------------------------------------------------------
# Bookkeeping on the link and its supplier
# ------------------------------------------------------------------

def _supplier(rec: dict, firms: dict, countries: dict):
    pid = rec.get("agent_pid")
    if pid in firms:
        return firms[pid]
    return countries.get(pid)


def _book_cut(rec: dict, cut_qty: float, cut_tons: float, firms: dict, countries: dict):
    """Take a cut share off the link and give the goods back to the supplier."""
    link = rec["link"]
    link.delivery = max(0.0, link.delivery - cut_qty)
    link.delivery_in_tons = max(0.0, link.delivery_in_tons - cut_tons)
    link.realized_delivery = max(0.0, link.realized_delivery - cut_qty)
    link.payment = max(0.0, link.payment - cut_qty * rec["price"])
    if rec.get("leg") == "alternative":
        link.alternative_route_realized_delivery = max(0.0, link.alternative_route_realized_delivery - cut_qty)
    else:
        link.main_route_realized_delivery = max(0.0, link.main_route_realized_delivery - cut_qty)
    link.capacity_blocked += cut_qty
    if link.delivery > EPSILON:
        link.price = link.payment / link.delivery      # the weighted price of what is left
    supplier = _supplier(rec, firms, countries)
    if supplier is None:
        return
    if hasattr(supplier, "product_stock"):            # a firm: the goods stay in stock
        supplier.product_stock += cut_qty
    elif hasattr(supplier, "qty_sold"):               # a country: unsold, untransported
        supplier.qty_sold -= cut_qty
        supplier.usd_transported -= cut_qty
        supplier.tons_transported -= cut_tons
        supplier.tonkm_transported -= cut_tons * getattr(rec["route"], "length", 0.0)


def _resend(rec: dict, cut_tons: float, cut_qty: float, next_round: int, alt,
            transport_network, tp, firms: dict, countries: dict, routing_event_collector=None) -> float:
    """Place a cut share on *alt* (its route avoiding the saturated edges, found by
    the batched search) if the shipper accepts the price. Returns the tons re-sent
    (0 when blocked: no route, or too expensive)."""
    link = rec["link"]
    origin = rec["origin"] if rec.get("origin") is not None else link.origin_node
    if alt is None:
        if routing_event_collector:
            routing_event_collector.record_event(rec.get("agent_pid"), link.buyer_id, "no_route", 0.0)
        return 0.0
    normal_cost = float(link.route_cost_per_ton or 0.0)
    alt_cost = transport_network.compute_route_cost(alt, link.cargo_type)
    relative_increase = max(alt_cost - normal_cost, 0.0) / normal_cost if normal_cost > EPSILON else 0.0
    relative_increase += link.calculate_switching_cost_between(link.route, alt, tp.switching_costs,
                                                               transport_network)
    transport_share = float(rec.get("transport_share", 0.0))
    if too_expensive(tp, relative_increase, transport_share, link):
        if routing_event_collector:
            routing_event_collector.record_event(rec.get("agent_pid"), link.buyer_id,
                                                 "too_expensive", relative_increase)
        return 0.0
    price = rec["base_price"] * (1.0 + transport_share * relative_increase)
    transport_network.place_shipment(
        alt, link.pid, cut_tons, rec["destination"],
        monetary_quantity=cut_qty, product_type=rec["product_type"],
        flow_category=rec["flow_category"], cargo_type=rec["cargo_type"],
        accumulate_at_dest=True, dest_key=rec["dest_key"],
        edge_key=f"{rec['edge_key']}__g{next_round}", link=link, origin=origin,
        leg="alternative", round_no=next_round, agent_pid=rec.get("agent_pid"),
        transport_share=transport_share, price=price, base_price=rec["base_price"],
    )
    link.delivery += cut_qty
    link.delivery_in_tons += cut_tons
    link.realized_delivery += cut_qty
    link.payment += cut_qty * price
    link.alternative_route_realized_delivery += cut_qty
    link.capacity_blocked = max(0.0, link.capacity_blocked - cut_qty)
    link.price = link.payment / link.delivery if link.delivery > EPSILON else rec["base_price"]
    link.alternative_route = alt
    link.alternative_found = True
    link.alternative_route_cost_per_ton = alt_cost
    supplier = _supplier(rec, firms, countries)
    if supplier is not None:
        if hasattr(supplier, "product_stock"):
            supplier.product_stock = max(0.0, supplier.product_stock - cut_qty)
        elif hasattr(supplier, "qty_sold"):
            supplier.qty_sold += cut_qty
            supplier.usd_transported += cut_qty
            supplier.tons_transported += cut_tons
            supplier.tonkm_transported += cut_tons * getattr(alt, "length", 0.0)
    if routing_event_collector:
        routing_event_collector.record_event(rec.get("agent_pid"), link.buyer_id, "rerouted",
                                             relative_increase)
    return cut_tons
