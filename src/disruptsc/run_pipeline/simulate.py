"""Time-step simulation loop for disruption, initial_state, and criticality runs."""

from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx
import numpy as np

from disruptsc.config import EPSILON
from disruptsc.params import TransportParams, SimParams
from disruptsc.run_pipeline.disruption import (
    parse_disruptions, apply_disruptions,
    TransportDisruption, CapitalDestruction, Recovery,
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
    flow_data, logistics_report = _run_one_time_step(
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
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)

    all_data = {"firm": [], "household": [], "country": [], "transport_flow": []}
    logistics_reports = []
    writers = AgentWriters(export_folder, _days_per_timestep(sp.time_resolution)) if export_folder else None

    # Collect logistics report at t=0 and t=1
    def _report_timesteps():
        return {0, 1}

    try:
        # Time step 0: equilibrium snapshot
        mon = monitored_edges if 0 in _report_timesteps() else None
        flow_data, lr = _run_one_time_step(
            0, sc_network, transport_network, transport_network,
            firms, households, countries, tp, sp, disruptions=[],
            monitored_edges=mon,
        )
        _accumulate_and_write(all_data, firms, households, countries, 0,
                              flow_data, writers, collect_flows=True)
        if lr is not None:
            logistics_reports.append(lr)

        # Parse disruptions
        disruptions = parse_disruptions(
            disruption_config, transport_edges, firm_table, firms, tp.monetary_units,
        )
        if not disruptions:
            logging.info("No disruptions — running one baseline step and returning")
            mon = monitored_edges if 1 in _report_timesteps() else None
            flow_data, lr = _run_one_time_step(
                1, sc_network, transport_network, transport_network,
                firms, households, countries, tp, sp, disruptions=[],
                monitored_edges=mon,
            )
            _accumulate_and_write(all_data, firms, households, countries, 1,
                                  flow_data, writers, collect_flows=True)
            if lr is not None:
                logistics_reports.append(lr)
            all_data["logistics_reports"] = logistics_reports
            return all_data

        logging.info(f"{len(disruptions)} disruption(s) parsed")
        for d in disruptions:
            d.log_info()

        # Time loop
        for t in range(1, t_final + 1):
            mon = monitored_edges if t in _report_timesteps() else None
            flow_data, lr = _run_one_time_step(
                t, sc_network, transport_network, transport_network,
                firms, households, countries, tp, sp, disruptions=disruptions,
                monitored_edges=mon,
            )
            _accumulate_and_write(all_data, firms, households, countries, t,
                                  flow_data, writers, collect_flows=(t <= 1))
            if lr is not None:
                logistics_reports.append(lr)

            # Early stop
            if sp.epsilon_stop and t > max(d.start_time for d in disruptions):
                if _is_back_to_equilibrium(households, countries, sp.epsilon_stop):
                    logging.info(f"Back to equilibrium at t={t}, stopping")
                    break

    finally:
        if writers:
            writers.close()

    all_data["logistics_reports"] = logistics_reports
    return all_data


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
        flow_data, _ = _run_one_time_step(
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

    # Build firm connectivity matrix
    firm_list = list(firms.values())
    n = len(firm_list)
    pid_to_idx = {f.pid: i for i, f in enumerate(firm_list)}

    W = nx.adjacency_matrix(sc_network, weight="weight", nodelist=firm_list).todense()

    # Import weight per firm
    import_weights = np.zeros(n)
    for i, firm in enumerate(firm_list):
        for u, v in sc_network.in_edges(firm):
            link = sc_network[u][v]["object"]
            if link.category == "import":
                import_weights[i] += sc_network[u][v]["weight"]

    transport_shares = np.array([f.transport_share for f in firm_list])

    # Final demand vector = household demand + country demand (only from firms)
    fd = np.zeros((n, 1))
    for hh in households.values():
        for sid, qty in hh.purchase_plan.items():
            if sid in pid_to_idx:
                fd[pid_to_idx[sid], 0] += qty
    for c in countries.values():
        for sid, qty in c.purchase_plan.items():
            if sid in pid_to_idx:
                fd[pid_to_idx[sid], 0] += qty

    # Solve Leontief: (I - A) X = FD  →  X = (I - A)^{-1} FD
    eq_production = np.linalg.solve(np.eye(n) - W, fd)

    # Cost decomposition
    domestic_input_cost = np.multiply(W.sum(axis=0).reshape((n, 1)), eq_production)
    import_input_cost = np.multiply(import_weights.reshape((n, 1)), eq_production)
    input_cost = domestic_input_cost + import_input_cost
    transport_cost = np.multiply(eq_production, transport_shares.reshape((n, 1)))
    margins = np.array([f.target_margin for f in firm_list]).reshape((n, 1))
    other_cost = np.multiply(eq_production, (1 - margins)) - input_cost - transport_cost

    # Initialize firms
    for firm in firm_list:
        i = pid_to_idx[firm.pid]
        eq_prod = float(eq_production[i, 0])
        firm.initialize_production(eq_prod)
        firm.initialize_inventory(sp.time_resolution)
        firm.initialize_finance(
            eq_input_cost=float(input_cost[i, 0]),
            eq_transport_cost=float(transport_cost[i, 0]),
            eq_other_cost=float(other_cost[i, 0]),
        )

    # Initialize households
    for hh in households.values():
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
                              tp.transport_to_households)

    # 10. Reset loads (clears remaining shipments from edges)
    transport_network.reset_loads()

    # 11. Firms evaluate profit
    for firm in firms.values():
        firm.evaluate_profit(sc_network)

    # 12. Update disruption state
    transport_network.update_road_disruption_state()
    for firm in firms.values():
        firm.update_disrupted_production_capacity()

    return flow_data, logistics_report


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _accumulate_and_write(all_data, firms, households, countries, time_step,
                          flow_data, writers: AgentWriters | None,
                          collect_flows=True):
    """Accumulate in-memory data AND write CSV rows if writers are open."""
    all_data["firm"].extend(collect_firm_data(firms, time_step))
    all_data["household"].extend(collect_household_data(households, time_step))
    all_data["country"].extend(collect_country_data(countries, time_step))
    if collect_flows and flow_data:
        all_data["transport_flow"].extend(flow_data)

    if writers:
        writers.write_step(firms, households, countries, time_step)


def _is_back_to_equilibrium(households, countries, epsilon):
    hh_extra = sum(hh.extra_spending for hh in households.values())
    hh_loss = sum(hh.consumption_loss for hh in households.values())
    c_extra = sum(c.extra_spending for c in countries.values())
    c_loss = sum(c.consumption_loss for c in countries.values())
    return all(v <= epsilon for v in (hh_extra, hh_loss, c_extra, c_loss))


def _days_per_timestep(time_resolution: str) -> float:
    return {"day": 1, "week": 7, "month": 30, "year": 365}.get(time_resolution, 7)
