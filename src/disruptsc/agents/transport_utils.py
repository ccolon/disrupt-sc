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


def _discover(od_point: int, link: CommercialLink, transport_network: TransportNetwork,
              available_transport_network: TransportNetwork, weight: str, use_cache: bool,
              library: str, allowed_modes=None, mode_weights=None,
              excluded_edges=None) -> Route | None:
    """One shortest-path search (optionally restricted to *allowed_modes*, with *mode_weights*
    scaling modes in the search and *excluded_edges* removed), cached under *library*.

    A cached route is used only while every edge of it is still open on the available
    network: the alternative libraries persist across steps, and a route found under one
    set of closures could cross an edge closed since (21 Sep 2026; the Rhine runs close
    the same edge week after week, so they never met the case)."""
    if use_cache:
        cached = transport_network.retrieve_cached_route(
            od_point, link.destination_node, library, link.cargo_type,
        )
        if cached and available_transport_network.is_route_available(cached):
            return cached
    route = available_transport_network.provide_shortest_route(
        od_point, link.destination_node, link.cargo_type, route_weight=weight,
        allowed_modes=allowed_modes, mode_weights=mode_weights, excluded_edges=excluded_edges,
    )
    if route and use_cache:
        transport_network.cache_route(
            od_point, link.destination_node, library, link.cargo_type, route,
        )
    return route


def discover_route(od_point: int,
                   link: CommercialLink,
                   transport_network: TransportNetwork,
                   available_transport_network: TransportNetwork,
                   use_route_cache: bool,
                   switching_costs: dict | None = None,
                   *,
                   excluded_edges=None,
                   exclusion_tag: str = "") -> Route | None:
    """Find the best alternative route from *od_point* to the link's destination.

    Penalty-aware (14 Sep 2026): the cheapest path by transport cost alone can introduce a
    mode the shipper does not use - on the Rhine, a rail leg replacing surcharged river km -
    which the modal-switch penalty then rejects, although a detour on the shipper's own modes
    (barge to the next port, road for the rest) exists and would pass. With *switching_costs*
    two candidates are searched, one restricted to the modes of the link's normal route and
    one free, and the cheaper INCLUDING the switching penalty (a fraction of the normal bill)
    is returned. Without *switching_costs* (or without a normal route) the free search is used.

    *excluded_edges* (keys ``(min(u, v), max(u, v))``) are removed from the search - the
    capacity gate passes the edges saturated earlier in the step - and *exclusion_tag* names
    that set in the cache libraries, so that routes found under different exclusions are
    never confused (the libraries are all 'alternative*' and are forgotten together when a
    cost shock starts or ends).
    """
    weight = "cost_per_ton"
    suffix = f":{exclusion_tag}" if exclusion_tag else ""
    baseline = getattr(link, "route", None)
    free = _discover(od_point, link, transport_network, available_transport_network, weight,
                     use_route_cache, "alternative" + suffix, excluded_edges=excluded_edges)
    if switching_costs is None or baseline is None or not getattr(baseline, "transport_modes", None):
        return free
    # Same-mode candidate: the shipper's own modes only, and within them the modes that carry
    # no line haul for it (access legs; road always, for bulk) weighted by 1 + penalty in the
    # search, so that the path keeps to the line-haul mode wherever one exists (a canal
    # detour) and uses the access modes only where unavoidable. The line-haul rule then
    # judges the result like any other candidate.
    costs = switching_costs or {}
    base_km = link._km_by_mode(baseline, transport_network)
    line_haul = link._line_haul_of(base_km, costs, link.cargo_type)   # km rule x per-cargo line-haul modes
    penalty = link._switching_penalty(costs, "modal_switch", 0.15)
    baseline_modes = set(baseline.transport_modes)
    weights = {m: 1.0 + penalty for m in baseline_modes if m not in line_haul and m != "multimodal"}
    library = "alternative_same_modes:" + "+".join(sorted(line_haul)) + f":{penalty:g}" + suffix
    same = _discover(od_point, link, transport_network, available_transport_network, weight,
                     use_route_cache, library, allowed_modes=baseline_modes, mode_weights=weights or None,
                     excluded_edges=excluded_edges)
    candidates = [r for r in (same, free) if r is not None]
    if not candidates:
        return None
    normal_cost = float(getattr(link, "route_cost_per_ton", 0.0) or 0.0)

    def total_cost(route: Route) -> float:
        cost = transport_network.compute_route_cost(route, link.cargo_type)
        penalty = link.calculate_switching_cost_between(baseline, route, switching_costs, transport_network)
        return cost + penalty * normal_cost

    return min(candidates, key=total_cost)


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
        if link is not None:
            product = getattr(link, "product", "") or ""
            sector = product.split("_", 1)[-1] if "_" in product else product   # "DEU_C17_18" -> "C17_18"
            cargo = getattr(link, "cargo_type", None)
            # most specific first: "<sector>:<cargo>", sector, product type, cargo type
            for key in (f"{sector}:{cargo}", sector, getattr(link, "product_type", None), cargo):
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

    *supplier_price* is the supplier's current output price (firm.price or
    country equivalent). It defaults to link.eq_price for backward
    compatibility. Passing it enables propagation of input-cost-driven
    price changes through the supply chain.

    *after_shipment(link, route)* is called once on successful placement
    for agent-specific bookkeeping (e.g. updating product_stock or qty_sold).

    The shipment records placed here carry the link, the route, the origin and
    the sender's transport share, so that the capacity gate
    (run_pipeline/capacity_gate.py) can cut them and re-send the cut share
    after every agent has delivered.
    """
    base_price = supplier_price if supplier_price is not None else link.eq_price
    link.delivery_offered = link.delivery

    def _place(route, key, tons, quantity, leg):
        transport_network.place_shipment(
            route, link.pid, tons, link.destination_node,
            monetary_quantity=quantity, product_type=link.product_type,
            flow_category=link.category, cargo_type=link.cargo_type,
            accumulate_at_dest=True, dest_key=link.pid,
            edge_key=key, link=link, origin=od_point, leg=leg,
            agent_pid=agent_pid, transport_share=transport_share,
            price=link.price, base_price=base_price,
        )

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
        shocked_cost = transport_network.compute_route_cost(main_route, link.cargo_type)
        alt_route = discover_route(
            od_point, link, transport_network, available_transport_network,
            tp.use_route_cache, switching_costs=tp.switching_costs,
        )
        alt_cost = (transport_network.compute_route_cost(alt_route, link.cargo_type)
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
        # place both parts (accumulated into one shipment at the destination;
        # distinct keys on the edges so that a shared edge counts both)
        if planned_tons > EPSILON:
            if main_share > 0:
                _place(main_route, link.pid, planned_tons * main_share, planned * main_share, "main")
            if alt_share > 0:
                _place(alt_route, f"{link.pid}__alt", planned_tons * alt_share, planned * alt_share,
                       "alternative")
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
        leg = "main"
    else:
        # Main route unavailable — try to find an alternative
        alt_route = discover_route(
            od_point, link,
            transport_network, available_transport_network,
            tp.use_route_cache, switching_costs=tp.switching_costs,
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
        alt_cost = transport_network.compute_route_cost(alt_route, link.cargo_type)
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
        leg = "alternative"
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
        _place(route, link.pid, link.delivery_in_tons, link.delivery, leg)

    link.realized_delivery = link.delivery
    link.payment = link.delivery * link.price

    if after_shipment:
        after_shipment(link, route)


def deliver_without_transport(link: CommercialLink,
                              after_delivery: Callable | None = None,
                              supplier_price: float | None = None):
    """Direct delivery (services, or when transport is off)."""
    if supplier_price is not None:
        link.price = supplier_price
    link.delivery_offered = link.delivery
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
