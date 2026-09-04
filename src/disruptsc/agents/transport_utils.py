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


def _base_route_cost(route: Route,
                     transport_network: TransportNetwork,
                     cargo_type: str) -> float:
    """Return the undisrupted/base cost per ton for a route."""
    return route.sum_indicator(transport_network, f"cost_per_ton_{cargo_type}")


def _delivered_price_threshold(tp: TransportParams, link=None):
    """Give-up threshold on the delivered price for *link*.

    ``delivered_price_increase_threshold`` is a scalar, or a dict keyed by
    product type (the supplier sector's type: mining, agriculture,
    oil_and_gas, manufacturing, ...) and/or cargo type, with ``default``:
    low-value bulk is abandoned at a smaller delivered-price increase than
    feedstocks or manufactured goods (Rhine 2018/2026 evidence).
    """
    value = tp.delivered_price_increase_threshold
    if isinstance(value, dict):
        for key in ((getattr(link, "product_type", None), getattr(link, "cargo_type", None)) if link is not None else ()):
            if key in value:
                return value[key]
        return value.get("default")
    return value


def too_expensive(tp: TransportParams, relative_increase: float, transport_share: float, link=None) -> bool:
    """Give-up rule for a delivery whose transport cost rose by *relative_increase*.

    With ``delivered_price_increase_threshold`` set, the test is on the delivered
    price (transport_share x relative increase); otherwise the legacy test on the
    freight bill (1 + relative increase > price_increase_threshold) applies.
    """
    threshold = _delivered_price_threshold(tp, link)
    if threshold is not None:
        return transport_share * relative_increase > threshold
    return tp.price_increase_threshold is not None and 1.0 + relative_increase > tp.price_increase_threshold


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
    if (main_route and available_transport_network.is_route_available(main_route)
            and link.delivery_in_tons > EPSILON
            and main_route.has_cost_shock(transport_network)):
        # The main route is open but crosses a cost-shocked edge (low water,
        # congestion, toll). Compare the re-priced main route with the best
        # alternative on the shocked network and take the cheaper; then the
        # same pass-through / give-up rules as for a closed edge apply. The
        # closure and shock cases are kept separate so that closures keep
        # their exact previous behaviour.
        shocked_cost = transport_network.compute_route_cost(
            main_route, link.cargo_type, with_capacity=tp.capacity_constraint_enabled,
        )
        alt_route = discover_route(
            od_point, link, transport_network, available_transport_network,
            tp.capacity_constraint_enabled, tp.use_route_cache,
        )
        alt_cost = (transport_network.compute_route_cost(
            alt_route, link.cargo_type, with_capacity=tp.capacity_constraint_enabled)
            if alt_route is not None else float("inf"))
        # The switching penalty (fraction of the normal bill, per cargo type)
        # is part of the alternative's cost when choosing: a bulk shipper whose
        # rerouting is prohibitively expensive stays on the surcharged river
        # instead of giving up.
        switch_frac = (link.calculate_switching_cost_between(main_route, alt_route, tp.switching_costs,
                                                             transport_network)
                       if alt_route is not None else 0.0)
        alt_cost_with_switch = alt_cost + switch_frac * link.route_cost_per_ton
        cap, sub = main_route.shock_ceiling(transport_network)
        if sub >= 1.0:
            # Cost approach (default): all-or-nothing on the cheaper option. The
            # capacity factor only matters under a substitution ceiling; with
            # unlimited substitutes it must not split the tonnage, or a bulk
            # link whose reroute is prohibitive would give up on the split
            # share while the river is open (EU Rhine run, 4 Sep 2026).
            stays_on_main = alt_route is None or alt_cost_with_switch >= shocked_cost
            main_share = 1.0 if stays_on_main else 0.0
            alt_share = 0.0 if stays_on_main else 1.0
        else:
            # substitution ceiling: the shocked mode still carries `cap` of the
            # tonnage at the surcharged cost, the substitutes absorb at most
            # `sub` of the displaced remainder, the rest is not delivered
            main_share = cap
            alt_share = sub * (1.0 - cap) if alt_route is not None else 0.0
        delivered_share = main_share + alt_share
        if delivered_share <= EPSILON:
            link.realized_delivery = 0.0
            link.delivery = 0.0
            link.payment = 0.0
            if routing_event_collector:
                routing_event_collector.record_event(agent_pid, link.buyer_id, "no_route", 0.0)
            return
        weighted_cost = (main_share * shocked_cost + alt_share * (alt_cost if alt_share > 0 else 0.0)) / delivered_share
        chosen = main_route if main_share >= alt_share else alt_route

        link.alternative_route = chosen
        link.alternative_found = True
        link.alternative_route_cost_per_ton = weighted_cost
        relative_increase = link.calculate_relative_increase_in_transport_cost()
        if alt_share > 0:
            relative_increase += (alt_share / delivered_share) * switch_frac

        if too_expensive(tp, relative_increase, transport_share, link):
            link.realized_delivery = 0.0
            link.delivery = 0.0
            link.payment = 0.0
            if routing_event_collector:
                routing_event_collector.record_event(
                    agent_pid, link.buyer_id, "too_expensive", relative_increase,
                )
            return

        link.price = base_price * (1 + transport_share * relative_increase)
        planned = link.delivery
        planned_tons = link.delivery_in_tons
        if delivered_share < 1.0:
            link.delivery = planned * delivered_share
            link.delivery_in_tons = planned_tons * delivered_share
        link.current_route = "main" if main_share >= alt_share else "alternative"
        link.main_route_realized_delivery = planned * main_share
        link.alternative_route_realized_delivery = planned * alt_share
        if routing_event_collector:
            routing_event_collector.record_event(
                agent_pid, link.buyer_id,
                "surcharged" if alt_share == 0 else "rerouted", relative_increase,
            )
        # place both parts (accumulated into one shipment at the destination)
        if planned_tons > EPSILON:
            if main_share > 0:
                transport_network.place_shipment(
                    main_route, link.pid, planned_tons * main_share, link.destination_node,
                    monetary_quantity=planned * main_share, product_type=link.product_type,
                    flow_category=link.category, cargo_type=link.cargo_type,
                    accumulate_at_dest=True, dest_key=link.pid,
                    capacity_constraint=tp.capacity_constraint_enabled,
                    capacity_constraint_mode=tp.capacity_constraint_mode,
                )
            if alt_share > 0:
                transport_network.place_shipment(
                    alt_route, link.pid, planned_tons * alt_share, link.destination_node,
                    monetary_quantity=planned * alt_share, product_type=link.product_type,
                    flow_category=link.category, cargo_type=link.cargo_type,
                    accumulate_at_dest=True, dest_key=link.pid,
                    capacity_constraint=tp.capacity_constraint_enabled,
                    capacity_constraint_mode=tp.capacity_constraint_mode,
                )
        link.realized_delivery = link.delivery
        link.payment = link.delivery * link.price
        if after_shipment:
            after_shipment(link, chosen)
        return
    elif main_route and available_transport_network.is_route_available(main_route):
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

        if too_expensive(tp, relative_increase, transport_share, link):
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
        link.price = base_price * (1 + price_change)
        # substitution ceiling of the closed edge(s): only this share of the
        # tonnage finds a substitute (1.0 = unlimited, legacy)
        sub = main_route.closure_substitution_share(transport_network) if main_route else 1.0
        if sub < 1.0:
            link.delivery = link.delivery * sub
            link.delivery_in_tons = link.delivery_in_tons * sub
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
            if too_expensive(tp, relative_increase, transport_share, link):
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
    """Pop a shipment from the destination node (if present).

    Skips:
      - service products (no shipment was placed on the network),
      - unsited receivers with od_point == -1 (e.g. virtual countries
        without a geojson location — no shipment can have been placed
        there since the node doesn't exist on the network).
    """
    if link.product_type in sectors_no_transport:
        return
    if od_point == -1:
        return
    available = transport_network._node[od_point].get("shipments", {})
    if link.pid in available:
        available.pop(link.pid)
