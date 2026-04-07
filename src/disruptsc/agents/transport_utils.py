"""Shared transport/routing functions for agents that send shipments (Firm, Country)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from disruptsc.config import EPSILON

if TYPE_CHECKING:
    from disruptsc.network.commercial_link import CommercialLink
    from disruptsc.network.route import Route
    from disruptsc.network.transport_network import TransportNetwork
    from disruptsc.params import TransportParams


# --- DEBUG INSTRUMENTATION ---
import os
_DBG = os.environ.get("DSC_DEBUG_REROUTE") == "1"
_dbg_counts = {"main_ok": 0, "alt_found": 0, "no_route": 0, "too_expensive": 0,
               "alt_cost_max_rel": 0.0}
def _dbg_reset():
    for k in _dbg_counts: _dbg_counts[k] = 0 if isinstance(_dbg_counts[k], int) else 0.0
def _dbg_report():
    print(f"  [DBG send_shipment] {_dbg_counts}", flush=True)
# --- END DEBUG ---


def discover_route(od_point: int,
                   link: CommercialLink,
                   transport_network: TransportNetwork,
                   available_transport_network: TransportNetwork,
                   capacity_constraint: bool,
                   use_route_cache: bool) -> Route | None:
    """Find a shortest-path route from *od_point* to the link's destination."""
    weight = "cost_per_ton"
    if capacity_constraint:
        weight = "cost_per_ton_with_capacity"

    effective_cache = use_route_cache and not capacity_constraint

    if effective_cache:
        cached = transport_network.retrieve_cached_route(
            od_point, link.destination_node,
            "alternative", link.cargo_type,
        )
        if cached:
            return cached

    route = available_transport_network.provide_shortest_route(
        od_point, link.destination_node, link.cargo_type, route_weight=weight,
    )

    if route and effective_cache:
        transport_network.cache_route(
            od_point, link.destination_node,
            "alternative", link.cargo_type, route,
        )

    return route


def _base_route_cost(route: Route,
                     transport_network: TransportNetwork,
                     cargo_type: str) -> float:
    """Return the undisrupted/base cost per ton for a route."""
    return route.sum_indicator(transport_network, f"cost_per_ton_{cargo_type}")


def send_shipment(agent_pid, od_point: int,
                  transport_share: float,
                  link: CommercialLink,
                  transport_network: TransportNetwork,
                  available_transport_network: TransportNetwork,
                  tp: TransportParams,
                  routing_event_collector=None,
                  after_shipment: Callable | None = None,
                  supplier_price: float | None = None):
    """Send a shipment along a transport route, handling disruption rerouting.

    If the link has a multi-entry *route_plan*, the delivery is split
    proportionally across routes.  Each sub-route is independently
    checked for disruption.

    *supplier_price* is the supplier's current output price (firm.price or
    country equivalent). It defaults to link.eq_price for backward
    compatibility. Passing it enables propagation of input-cost-driven
    price changes through the supply chain.

    *after_shipment(link, route)* is called once on successful placement
    for agent-specific bookkeeping (e.g. updating product_stock or qty_sold).
    """
    base_price = supplier_price if supplier_price is not None else link.eq_price

    # --- Multi-route path (chunked delivery) ---
    if len(link.route_plan) > 1:
        _send_chunked_shipment(
            agent_pid, od_point, transport_share,
            link, transport_network, available_transport_network,
            tp, routing_event_collector, after_shipment,
            supplier_price=base_price,
        )
        return

    # --- Single-route path ---
    # Always try the main route first; if available, switch back to it
    main_route = link.route
    if main_route and available_transport_network.is_route_available(main_route):
        if _DBG: _dbg_counts["main_ok"] += 1
        link.current_route = "main"
        link.price = base_price
        link.main_route_realized_delivery = link.delivery
        route = main_route
    else:
        # Main route unavailable — try to find an alternative
        alt_route = discover_route(
            od_point, link,
            transport_network, available_transport_network,
            tp.capacity_constraint_enabled, tp.use_route_cache,
        )
        if alt_route is None:
            if _DBG:
                _dbg_counts["no_route"] += 1
                if _dbg_counts["no_route"] <= 3:
                    print(f"  [DBG no_route] od={od_point} dest={link.destination_node} cargo={link.cargo_type}", flush=True)
            link.realized_delivery = 0.0
            link.delivery = 0.0
            link.payment = 0.0
            if routing_event_collector:
                routing_event_collector.record_event(
                    agent_pid, link.buyer_id, "no_route", 0.0,
                )
            return

        link.alternative_route = alt_route
        link.alternative_found = True
        alt_cost = transport_network.compute_route_cost(
            alt_route, link.cargo_type,
            with_capacity=tp.capacity_constraint_enabled,
        )
        link.alternative_route_cost_per_ton = alt_cost
        relative_increase = link.calculate_relative_increase_in_transport_cost()

        switching_penalty = link.calculate_switching_cost(
            tp.switching_costs, transport_network,
        )
        relative_increase += switching_penalty

        if tp.price_increase_threshold is not None and 1.0 + relative_increase > tp.price_increase_threshold:
            if _DBG:
                _dbg_counts["too_expensive"] += 1
                if _dbg_counts["too_expensive"] <= 3:
                    print(f"  [DBG too_exp] od={od_point} dest={link.destination_node} cargo={link.cargo_type} rel_inc={relative_increase:.2f}", flush=True)
            link.realized_delivery = 0.0
            link.delivery = 0.0
            link.payment = 0.0
            if routing_event_collector:
                routing_event_collector.record_event(
                    agent_pid, link.buyer_id, "too_expensive", relative_increase,
                )
            return
        if _DBG:
            _dbg_counts["alt_found"] += 1
            if relative_increase > _dbg_counts["alt_cost_max_rel"]:
                _dbg_counts["alt_cost_max_rel"] = relative_increase

        link.current_route = "alternative"
        route = alt_route
        price_change = transport_share * relative_increase
        link.price = base_price * (1 + price_change)
        link.alternative_route_realized_delivery = link.delivery
        if routing_event_collector:
            routing_event_collector.record_event(
                agent_pid, link.buyer_id, "rerouted", relative_increase,
            )

    # Place shipment on transport network
    if link.delivery_in_tons > EPSILON:
        transport_network.place_shipment(
            route, link.pid, link.delivery_in_tons, link.destination_node,
            monetary_quantity=link.delivery, product_type=link.product_type,
            flow_category=link.category, cargo_type=link.cargo_type,
            capacity_constraint=tp.capacity_constraint_enabled,
            capacity_constraint_mode=tp.capacity_constraint_mode,
        )

    link.realized_delivery = link.delivery
    link.payment = link.delivery * link.price

    if after_shipment:
        after_shipment(link, route)


def _send_chunked_shipment(
    agent_pid, od_point: int,
    transport_share: float,
    link: CommercialLink,
    transport_network: TransportNetwork,
    available_transport_network: TransportNetwork,
    tp: TransportParams,
    routing_event_collector=None,
    after_shipment: Callable | None = None,
    supplier_price: float | None = None,
):
    base_price = supplier_price if supplier_price is not None else link.eq_price
    """Split a delivery across multiple routes per the link's route_plan."""
    total_tons = link.delivery_in_tons
    total_monetary = link.delivery
    if total_tons < EPSILON:
        link.realized_delivery = link.delivery
        link.payment = link.delivery * link.price
        link.main_route_realized_delivery = link.delivery
        if after_shipment:
            after_shipment(link, link.route)
        return

    any_rerouted = False
    delivered_value = 0.0
    total_payment = 0.0
    main_delivery = 0.0
    rerouted_delivery = 0.0
    rerouted_tons = 0.0
    rerouted_cost_ton_weighted = 0.0
    rerouted_length_weighted = 0.0
    representative_alt_route = None
    representative_alt_tons = 0.0

    for i, (route, fraction) in enumerate(link.route_plan):
        planned_route = route
        sub_tons = total_tons * fraction
        sub_monetary = total_monetary * fraction

        if sub_tons < EPSILON:
            continue

        # Check route availability (disruption)
        if not available_transport_network.is_route_available(planned_route):
            alt_route = discover_route(
                od_point, link,
                transport_network, available_transport_network,
                tp.capacity_constraint_enabled, tp.use_route_cache,
            )
            if alt_route is None:
                # This portion is lost
                if routing_event_collector:
                    routing_event_collector.record_event(
                        agent_pid, link.buyer_id, "no_route", 0.0,
                    )
                continue

            # Check cost of alternative against price_increase_threshold
            alt_cost = transport_network.compute_route_cost(
                alt_route, link.cargo_type,
                with_capacity=tp.capacity_constraint_enabled,
            )
            normal_cost = _base_route_cost(planned_route, transport_network, link.cargo_type)
            relative_increase = 0.0
            if normal_cost > EPSILON:
                relative_increase = max(alt_cost - normal_cost, 0) / normal_cost
            switching_penalty = link.calculate_switching_cost_between(
                planned_route, alt_route, tp.switching_costs, transport_network,
            )
            relative_increase += switching_penalty
            if tp.price_increase_threshold is not None and 1.0 + relative_increase > tp.price_increase_threshold:
                if routing_event_collector:
                    routing_event_collector.record_event(
                        agent_pid, link.buyer_id, "too_expensive",
                        relative_increase,
                    )
                continue

            route = alt_route
            chunk_price = base_price * (1 + transport_share * relative_increase)
            any_rerouted = True
            rerouted_delivery += sub_monetary
            rerouted_tons += sub_tons
            rerouted_cost_ton_weighted += sub_tons * alt_cost
            rerouted_length_weighted += sub_tons * alt_route.length
            if sub_tons > representative_alt_tons:
                representative_alt_route = alt_route
                representative_alt_tons = sub_tons
            if routing_event_collector:
                routing_event_collector.record_event(
                    agent_pid, link.buyer_id, "rerouted", relative_increase,
                )
        else:
            route = planned_route
            chunk_price = base_price
            main_delivery += sub_monetary

        if route is not planned_route:
            link.alternative_found = True

        # Place sub-shipment with unique chunk ID on edges
        chunk_id = f"{link.pid}__r{i}" if i > 0 else link.pid
        transport_network.place_shipment(
            route, chunk_id, sub_tons, link.destination_node,
            monetary_quantity=sub_monetary, product_type=link.product_type,
            flow_category=link.category, cargo_type=link.cargo_type,
            accumulate_at_dest=True,  # merge at destination node under link.pid
            dest_key=link.pid,
            capacity_constraint=tp.capacity_constraint_enabled,
            capacity_constraint_mode=tp.capacity_constraint_mode,
        )
        delivered_value += sub_monetary
        total_payment += sub_monetary * chunk_price

    link.current_route = "alternative" if any_rerouted else "main"
    link.main_route_realized_delivery = main_delivery
    link.alternative_route_realized_delivery = rerouted_delivery
    if any_rerouted and representative_alt_route is not None and rerouted_tons > EPSILON:
        link.alternative_route = representative_alt_route
        link.alternative_route_cost_per_ton = rerouted_cost_ton_weighted / rerouted_tons
        link.alternative_route_length = rerouted_length_weighted / rerouted_tons

    link.realized_delivery = delivered_value
    link.payment = total_payment
    if delivered_value > EPSILON:
        link.price = total_payment / delivered_value
    else:
        link.price = base_price

    if after_shipment and link.route:
        after_shipment(link, link.route)


def deliver_without_transport(link: CommercialLink,
                              after_delivery: Callable | None = None,
                              supplier_price: float | None = None):
    """Direct delivery (services, or when transport is off)."""
    if supplier_price is not None:
        link.price = supplier_price
    link.realized_delivery = link.delivery
    link.payment = link.delivery * link.price
    link.main_route_realized_delivery = link.delivery
    if after_delivery:
        after_delivery(link)


def collect_shipment_from_node(od_point: int, link: CommercialLink,
                               transport_network: TransportNetwork,
                               sectors_no_transport: tuple) -> None:
    """Pop a shipment from the destination node (if present)."""
    if link.product_type not in sectors_no_transport:
        available = transport_network._node[od_point].get("shipments", {})
        if link.pid in available:
            available.pop(link.pid)
