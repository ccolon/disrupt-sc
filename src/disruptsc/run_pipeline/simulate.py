"""Time-step simulation loop for disruption, initial_state, and criticality runs."""

from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx
import numpy as np
import scipy.sparse as sp_sparse
import scipy.sparse.linalg as sp_linalg

from disruptsc.config import EPSILON
from disruptsc.params import TransportParams, SimParams
from disruptsc.run_pipeline.disruption import (
    parse_disruptions, apply_disruptions,
    TransportDisruption, CapitalDestruction, Recovery,
    place_reconstruction_demand, rebuild_from_reconstruction,
    DEFAULT_CAPITAL_INPUT_MIX,
)
from disruptsc.run_pipeline.export import (
    collect_firm_data, collect_household_data, collect_country_data,
    AgentWriters,
)


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def run_initial_state(sc_network, transport_network, firms, households, countries,
                      tp: TransportParams, sp: SimParams,
                      export_folder: Path | None = None,
                      monitored_edges: list[str] | None = None):
    """Single-timestep equilibrium run.  Returns collected data dicts."""
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)

    # Run t=0
    flow_data, logistics_report, _ = _run_one_time_step(
        0, sc_network, transport_network, transport_network,
        firms, households, countries, tp, sp, disruptions=[],
        monitored_edges=monitored_edges,
    )

    # Write CSVs if exporting
    if export_folder:
        with AgentWriters(export_folder, _days_per_timestep(sp.time_resolution)) as writers:
            writers.write_step(firms, households, countries, 0)

    # Still return in-memory data for callers that need it
    result = {
        "firm": collect_firm_data(firms, 0),
        "household": collect_household_data(households, 0),
        "country": collect_country_data(countries, 0),
        "flow": flow_data,
    }
    if logistics_report is not None:
        result["logistics_reports"] = [logistics_report]
    return result


def run_disruption(sc_network, transport_network, firms, households, countries,
                   tp: TransportParams, sp: SimParams,
                   disruption_config: list | None,
                   transport_edges, firm_table,
                   t_final: int,
                   export_folder: Path | None = None,
                   monitored_edges: list[str] | None = None):
    """Full disruption simulation.  Returns lists of per-timestep data."""
    writers = AgentWriters(export_folder, _days_per_timestep(sp.time_resolution)) if export_folder else None

    try:
        all_data, logistics_reports, all_routing_summaries = prepare_disruption_baseline(
            sc_network, transport_network, firms, households, countries,
            tp, sp, writers=writers, monitored_edges=monitored_edges,
        )

        # Parse disruptions
        disruptions = parse_disruptions(
            disruption_config, transport_edges, firm_table, firms, tp.monetary_units,
        )
        if not disruptions:
            logging.info("No disruptions — running one baseline step and returning")
            all_data, logistics_reports, all_routing_summaries = continue_disruption_run(
                sc_network, transport_network, firms, households, countries,
                tp, sp, disruptions=[], t_start=1, t_final=1,
                all_data=all_data,
                logistics_reports=logistics_reports,
                all_routing_summaries=all_routing_summaries,
                writers=writers,
                monitored_edges=monitored_edges,
            )
            all_data["logistics_reports"] = logistics_reports
            _export_routing_summary(all_routing_summaries, export_folder)
            return all_data

        logging.info(f"{len(disruptions)} disruption(s) parsed")
        for d in disruptions:
            d.log_info()

        all_data, logistics_reports, all_routing_summaries = continue_disruption_run(
            sc_network, transport_network, firms, households, countries,
            tp, sp, disruptions=disruptions, t_start=1, t_final=t_final,
            all_data=all_data,
            logistics_reports=logistics_reports,
            all_routing_summaries=all_routing_summaries,
            writers=writers,
            monitored_edges=monitored_edges,
        )

    finally:
        if writers:
            writers.close()

    all_data["logistics_reports"] = logistics_reports
    _export_routing_summary(all_routing_summaries, export_folder)
    return all_data


def prepare_disruption_baseline(sc_network, transport_network, firms, households, countries,
                                tp: TransportParams, sp: SimParams,
                                writers: AgentWriters | None = None,
                                monitored_edges: list[str] | None = None):
    """Reset to equilibrium and execute the shared, undisrupted t=0 baseline."""
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)

    all_data = {"firm": [], "household": [], "country": [], "transport_flow": []}
    logistics_reports = []
    all_routing_summaries = []

    mon = monitored_edges if 0 in _report_timesteps() else None
    flow_data, lr, rs = _run_one_time_step(
        0, sc_network, transport_network, transport_network,
        firms, households, countries, tp, sp, disruptions=[],
        monitored_edges=mon,
    )
    _accumulate_and_write(all_data, firms, households, countries, 0,
                          flow_data, writers, collect_flows=True,
                          sc_network=sc_network)
    if lr is not None:
        logistics_reports.append(lr)
    all_routing_summaries.extend(rs)

    return all_data, logistics_reports, all_routing_summaries


def continue_disruption_run(sc_network, transport_network, firms, households, countries,
                            tp: TransportParams, sp: SimParams,
                            disruptions: list,
                            t_start: int, t_final: int,
                            all_data: dict,
                            logistics_reports: list,
                            all_routing_summaries: list,
                            writers: AgentWriters | None = None,
                            monitored_edges: list[str] | None = None):
    """Continue a disruption run from an existing simulation state."""
    for t in range(t_start, t_final + 1):
        mon = monitored_edges if t in _report_timesteps() else None
        flow_data, lr, rs = _run_one_time_step(
            t, sc_network, transport_network, transport_network,
            firms, households, countries, tp, sp, disruptions=disruptions,
            monitored_edges=mon,
        )
        _accumulate_and_write(all_data, firms, households, countries, t,
                              flow_data, writers, collect_flows=(t <= 1),
                              sc_network=sc_network)
        if lr is not None:
            logistics_reports.append(lr)
        all_routing_summaries.extend(rs)

        if disruptions and sp.epsilon_stop and t > max(d.start_time for d in disruptions):
            if _is_back_to_equilibrium(households, countries, sp.epsilon_stop):
                logging.info(f"Back to equilibrium at t={t}, stopping")
                break

    return all_data, logistics_reports, all_routing_summaries


def run_criticality(sc_network, transport_network, firms, households, countries,
                    tp: TransportParams, sp: SimParams,
                    edge_id: int, duration: int, t_final: int):
    """Criticality analysis for a single transport edge."""
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)

    disruptions = [TransportDisruption(
        description={edge_id: 1.0},
        recovery=Recovery(duration=duration, shape="threshold"),
        start_time=1,
    )]

    all_data = {"firm": [], "household": [], "country": [], "transport_flow": []}

    for t in range(0, t_final + 1):
        flow_data, _, _ = _run_one_time_step(
            t, sc_network, transport_network, transport_network,
            firms, households, countries, tp, sp, disruptions=disruptions,
        )
        _accumulate_and_write(all_data, firms, households, countries, t,
                              flow_data, writers=None, collect_flows=True)

        if t > duration + 1 and sp.epsilon_stop:
            if _is_back_to_equilibrium(households, countries, sp.epsilon_stop):
                break

    return all_data


# ------------------------------------------------------------------
# Set initial conditions (IO equilibrium)
# ------------------------------------------------------------------

def set_initial_conditions(sc_network, firms, households, countries,
                           tp: TransportParams, sp: SimParams):
    """Initialize agents at input-output equilibrium."""
    logging.info("Setting initial conditions (IO equilibrium)")

    # Reset commercial link variables
    for u, v in sc_network.edges():
        sc_network[u][v]["object"].reset()

    for hh in households.values():
        hh.set_equilibrium_purchase_plan()

    # Build firm connectivity matrix
    firm_list = list(firms.values())
    n = len(firm_list)
    pid_to_idx = {f.pid: i for i, f in enumerate(firm_list)}

    # Sparse representation: W is the firm-by-firm intermediate-input matrix.
    # For large MRIOs (n > ~3000) the dense (I-W) blows past available RAM and
    # the BLAS solver's recursive block algorithm overflows the C stack on
    # Windows. The supply-chain network is naturally sparse (typically <1 %
    # fill), so CSR + scipy.sparse.linalg.spsolve gives the same answer in
    # O(nnz) memory.
    W = nx.adjacency_matrix(sc_network, weight="weight", nodelist=firm_list).tocsr()
    logging.info(f"  Leontief matrix: {n}x{n} sparse, {W.nnz} non-zeros")

    # Import weight per firm
    import_weights = np.zeros(n)
    for i, firm in enumerate(firm_list):
        for u, v in sc_network.in_edges(firm):
            link = sc_network[u][v]["object"]
            if link.category == "import":
                import_weights[i] += sc_network[u][v]["weight"]

    transport_shares = np.array([f.transport_share for f in firm_list])

    # Final demand vector = household demand + country demand (only from firms)
    fd = np.zeros(n)  # 1-D for spsolve
    for hh in households.values():
        for sid, qty in hh.purchase_plan.items():
            if sid in pid_to_idx:
                fd[pid_to_idx[sid]] += qty
    for c in countries.values():
        for sid, qty in c.purchase_plan.items():
            if sid in pid_to_idx:
                fd[pid_to_idx[sid]] += qty

    # Solve Leontief: (I - W) X = FD  →  X = (I - W)^{-1} FD
    IminusW = sp_sparse.eye(n, format="csr") - W
    eq_production = sp_linalg.spsolve(IminusW, fd).reshape((n, 1))

    # Cost decomposition
    w_col_sum = np.asarray(W.sum(axis=0)).ravel().reshape((n, 1))
    domestic_input_cost = w_col_sum * eq_production
    import_input_cost = np.multiply(import_weights.reshape((n, 1)), eq_production)
    input_cost = domestic_input_cost + import_input_cost
    transport_cost = np.multiply(eq_production, transport_shares.reshape((n, 1)))
    margins = np.array([f.target_margin for f in firm_list]).reshape((n, 1))
    other_cost = np.multiply(eq_production, (1 - margins)) - input_cost - transport_cost

    # Initialize firms. Capital is sized on *annual* value added, so convert the
    # per-time-step VA to annual using the run's time resolution.
    periods_per_year = 365.0 / _days_per_timestep(sp.time_resolution)
    for firm in firm_list:
        i = pid_to_idx[firm.pid]
        eq_prod = float(eq_production[i, 0])
        firm.initialize_production(eq_prod)
        firm.initialize_inventory(sp.time_resolution)
        firm.initialize_finance(
            eq_input_cost=float(input_cost[i, 0]),
            eq_transport_cost=float(transport_cost[i, 0]),
            eq_other_cost=float(other_cost[i, 0]),
            periods_per_year=periods_per_year,
        )

    # Initialize households
    for hh in households.values():
        hh.initialize_inventory()
        hh.plan_purchase()
        hh.initialize_from_purchase_plan()

    # Set orders on commercial links
    for hh in households.values():
        hh.send_purchase_orders(sc_network)
    for c in countries.values():
        c.send_purchase_orders(sc_network)

    # Firms: evaluate needs → purchase plan → send orders
    for firm in firm_list:
        firm._evaluate_input_needs()
        firm._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=False)
    for firm in firm_list:
        firm.send_purchase_orders(sc_network)

    # Set equilibrium total_input (= sum of realized deliveries from suppliers)
    for firm in firm_list:
        firm.total_input = sum(firm.eq_needs.values())

    # Set client shares
    for firm in firm_list:
        firm.retrieve_orders(sc_network)
        firm.eq_total_order = firm.total_order
        # Calculate client share
        if firm.total_order > EPSILON:
            for cid in firm.clients:
                if cid in firm.order_book:
                    firm.clients[cid]["share"] = firm.order_book[cid] / firm.total_order

    # Reset prices to 1
    for u, v in sc_network.edges():
        sc_network[u][v]["object"].price = 1.0
        sc_network[u][v]["object"].eq_price = 1.0


# ------------------------------------------------------------------
# Single time step
# ------------------------------------------------------------------

def _run_one_time_step(time_step, sc_network, transport_network,
                       available_transport_network,
                       firms, households, countries,
                       tp, sp, disruptions,
                       monitored_edges: list[str] | None = None):
    """Execute one simulation time step.

    Returns (flow_data, logistics_report).  *logistics_report* is ``None``
    unless *monitored_edges* is provided.
    """
    logging.info(f"--- Time step {time_step} ---")

    # Reset per-timestep tracking on households and countries
    for hh in households.values():
        hh.reset_variables()
    for c in countries.values():
        c.reset_variables()

    # Apply disruptions starting this step
    if disruptions:
        available_transport_network = apply_disruptions(
            disruptions, time_step, transport_network, firms,
        )

    # Reconstruction demand (ARIO-style): when a reconstruction-enabled capital
    # destruction is active, firms request capital-good output to rebuild. Set
    # before retrieve_orders so it enters total_order and propagates to inputs.
    recon = _active_reconstruction(disruptions, time_step)
    if recon is not None:
        place_reconstruction_demand(firms, recon[0], recon[1])

    # 1. Firms retrieve orders from previous step
    for firm in firms.values():
        firm.retrieve_orders(sc_network)

    # 2. Production planning
    for firm in firms.values():
        firm.plan_production(sc_network, sp.propagate_input_price_change)

    # 3. Purchase planning
    for firm in firms.values():
        firm.plan_purchase(sp.adaptive_inventories, sp.adaptive_supplier_weight)

    # 4. All agents send purchase orders
    for hh in households.values():
        hh.plan_purchase()
        hh.send_purchase_orders(sc_network)
    for c in countries.values():
        c.send_purchase_orders(sc_network)
    for firm in firms.values():
        firm.send_purchase_orders(sc_network)

    # 5. Firms produce
    for firm in firms.values():
        firm.produce()

    # 6. Countries deliver (transit + import supply)
    for c in countries.values():
        c.deliver(sc_network, transport_network, available_transport_network, tp)

    # 7. Firms deliver
    for firm in firms.values():
        firm.deliver(sc_network, transport_network, available_transport_network, tp)

    # 7r. Reconstruction: convert capital-good output that competed for delivery
    # into restored capital, lifting capacity for subsequent steps (the V-shape).
    if recon is not None:
        rebuild_from_reconstruction(firms, recon[1])

    # 7b. Collect routing summary from commercial links
    routing_summary = _collect_routing_summary(sc_network, time_step)

    # 8. Collect flow data while shipments are still on edges
    flow_data = transport_network.compute_flow_per_segment(time_step)

    # 8b. Logistics report (while shipments are still on edges)
    logistics_report = None
    if monitored_edges is not None:
        logistics_report = transport_network.compute_logistics_report(
            time_step, monitored_edges,
        )

    # 9. All agents receive products (clears shipments from nodes)
    for hh in households.values():
        hh.receive_products(sc_network, transport_network, tp.sectors_no_transport,
                            tp.transport_to_households)
    for c in countries.values():
        c.receive_products(sc_network, transport_network, tp.sectors_no_transport,
                           tp.transport_to_households)
    for firm in firms.values():
        firm.receive_products(sc_network, transport_network, tp.sectors_no_transport,
                              tp.with_transport)
    for hh in households.values():
        hh.consume()

    # 10. Reset loads (clears remaining shipments from edges)
    transport_network.reset_loads()

    # 11. Firms evaluate profit
    for firm in firms.values():
        firm.evaluate_profit(sc_network)

    # 12. Update disruption state
    transport_network.update_road_disruption_state()
    for firm in firms.values():
        firm.update_disrupted_production_capacity()

    return flow_data, logistics_report, routing_summary


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _accumulate_and_write(all_data, firms, households, countries, time_step,
                          flow_data, writers: AgentWriters | None,
                          collect_flows=True, sc_network=None):
    """Accumulate in-memory data AND write CSV rows if writers are open."""
    all_data["firm"].extend(collect_firm_data(firms, time_step))
    all_data["household"].extend(collect_household_data(households, time_step))
    all_data["country"].extend(collect_country_data(countries, time_step))
    if collect_flows and flow_data:
        all_data["transport_flow"].extend(flow_data)

    if writers:
        writers.write_step(firms, households, countries, time_step)
        if sc_network is not None:
            writers.write_links(sc_network, time_step)
            writers.write_trade(sc_network, time_step)


def _is_back_to_equilibrium(households, countries, epsilon):
    hh_extra = sum(hh.extra_spending for hh in households.values())
    hh_loss = sum(hh.consumption_loss for hh in households.values())
    c_extra = sum(c.extra_spending for c in countries.values())
    c_loss = sum(c.consumption_loss for c in countries.values())
    return all(v <= epsilon for v in (hh_extra, hh_loss, c_extra, c_loss))


def _active_reconstruction(disruptions, time_step):
    """Return ``(reconstruction_target_time, capital_input_mix)`` if a
    reconstruction-enabled capital destruction has started by *time_step*,
    else ``None``."""
    for d in disruptions or []:
        if (isinstance(d, CapitalDestruction)
                and getattr(d, "reconstruction_market", False)
                and d.start_time <= time_step):
            return d.reconstruction_target_time, (d.capital_input_mix or DEFAULT_CAPITAL_INPUT_MIX)
    return None


def _report_timesteps() -> set[int]:
    return {0, 1}


def _days_per_timestep(time_resolution: str) -> float:
    return {"day": 1, "week": 7, "month": 30, "year": 365}.get(time_resolution, 7)


def _collect_routing_summary(sc_network, time_step: int) -> list[dict]:
    """Aggregate commercial-link routing outcomes into reporting buckets.

    Buckets are:
      - each cargo type for links that use the transport network and have
        different origin/destination OD points
      - ``transport_same_od_point`` for links that use the transport network
        but have the same origin/destination OD point
      - ``no_transport_network`` for links that do not use the transport network
    """
    from collections import defaultdict

    buckets = defaultdict(lambda: {
        "total_usd": 0.0,
        "main_usd": 0.0,
        "alternative_usd": 0.0,
        "blocked_usd": 0.0,
    })

    for u, v, data in sc_network.edges(data=True):
        link = data["object"]
        if link.order < EPSILON:
            continue

        if not link.use_transport_network:
            bucket = "no_transport_network"
        elif link.origin_node == link.destination_node:
            bucket = "transport_same_od_point"
        else:
            bucket = getattr(link, "cargo_type", "unknown")

        order_value = link.order * link.eq_price
        buckets[bucket]["total_usd"] += order_value

        main_delivery = link.main_route_realized_delivery
        alternative_delivery = link.alternative_route_realized_delivery
        tracked_total = main_delivery + alternative_delivery
        if tracked_total <= EPSILON and link.realized_delivery > EPSILON:
            if link.current_route == "alternative":
                alternative_delivery = link.realized_delivery
            else:
                main_delivery = link.realized_delivery

        buckets[bucket]["main_usd"] += main_delivery * link.eq_price
        buckets[bucket]["alternative_usd"] += alternative_delivery * link.eq_price

        # Blocked = ordered but not delivered
        blocked = max(0.0, link.order - link.realized_delivery) * link.eq_price
        buckets[bucket]["blocked_usd"] += blocked

    rows = []
    for bucket, vals in sorted(buckets.items()):
        rows.append({"time_step": time_step, "cargo_type": bucket, **vals})
    return rows


def _export_routing_summary(rows: list[dict], export_folder):
    if not export_folder or not rows:
        return
    import pandas as pd
    pd.DataFrame(rows).to_csv(export_folder / "routing_summary.csv", index=False)
    logging.info(f"Routing summary: {len(rows)} rows → routing_summary.csv")
