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


def send_shipment(agent_pid, od_point: int,
                  transport_share: float,
                  link: CommercialLink,
                  transport_network: TransportNetwork,
                  available_transport_network: TransportNetwork,
                  tp: TransportParams,
                  routing_event_collector=None,
                  after_shipment: Callable | None = None):
    """Send a shipment along a transport route, handling disruption rerouting.

    If the link has a multi-entry *route_plan*, the delivery is split
    proportionally across routes.  Each sub-route is independently
    checked for disruption.

    *after_shipment(link, route)* is called once on successful placement
    for agent-specific bookkeeping (e.g. updating product_stock or qty_sold).
    """
    # --- Multi-route path (chunked delivery) ---
    if len(link.route_plan) > 1:
        _send_chunked_shipment(
            agent_pid, od_point, transport_share,
            link, transport_network, available_transport_network,
            tp, routing_event_collector, after_shipment,
        )
        return

    # --- Single-route path ---
    # Always try the main route first; if available, switch back to it
    main_route = link.route
    if main_route and available_transport_network.is_route_available(main_route):
        link.current_route = "main"
        link.price = link.eq_price
        route = main_route
    else:
        # Main route unavailable — try to find an alternative
        alt_route = discover_route(
            od_point, link,
            transport_network, available_transport_network,
            tp.capacity_constraint_enabled, tp.use_route_cache,
        )
        if alt_route is None:
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
        )
        link.alternative_route_cost_per_ton = alt_cost
        relative_increase = link.calculate_relative_increase_in_transport_cost()

        switching_penalty = link.calculate_switching_cost(
            tp.switching_costs, transport_network,
        )
        relative_increase += switching_penalty

        if relative_increase > tp.price_increase_threshold:
            link.realized_delivery = 0.0
            link.delivery = 0.0
            link.payment = 0.0
            if routing_event_collector:
                routing_event_collector.record_event(
                    agent_pid, link.buyer_id, "too_expensive", relative_increase,
                )
            return

        link.current_route = "alternative"
        route = alt_route
        price_change = transport_share * relative_increase
        link.price = link.eq_price * (1 + price_change)
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
):
    """Split a delivery across multiple routes per the link's route_plan."""
    total_tons = link.delivery_in_tons
    total_monetary = link.delivery
    if total_tons < EPSILON:
        link.realized_delivery = link.delivery
        link.payment = link.delivery * link.price
        if after_shipment:
            after_shipment(link, link.route)
        return

    realized_fraction = 0.0

    for i, (route, fraction) in enumerate(link.route_plan):
        sub_tons = total_tons * fraction
        sub_monetary = total_monetary * fraction

        if sub_tons < EPSILON:
            realized_fraction += fraction
            continue

        # Check route availability (disruption)
        if not available_transport_network.is_route_available(route):
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
            route = alt_route

        # Place sub-shipment with unique chunk ID on edges
        chunk_id = f"{link.pid}__r{i}" if i > 0 else link.pid
        transport_network.place_shipment(
            route, chunk_id, sub_tons, link.destination_node,
            monetary_quantity=sub_monetary, product_type=link.product_type,
            flow_category=link.category, cargo_type=link.cargo_type,
            accumulate_at_dest=True,  # merge at destination node under link.pid
            dest_key=link.pid,
        )
        realized_fraction += fraction

    link.realized_delivery = link.delivery * realized_fraction
    link.payment = link.realized_delivery * link.price

    if after_shipment and link.route:
        after_shipment(link, link.route)


def deliver_without_transport(link: CommercialLink,
                              after_delivery: Callable | None = None):
    """Direct delivery (services, or when transport is off)."""
    link.realized_delivery = link.delivery
    link.payment = link.delivery * link.price
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
