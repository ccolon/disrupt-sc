"""CLI entry point for DisruptSC v2."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from disruptsc import paths
from disruptsc.config import load_config, build_params, setup_output, setup_logging

from disruptsc.init_pipeline.load_data import (
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors,
)
from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.init_pipeline.agents import (
    create_firm_table, create_firms, load_tech_coefs, load_inventories,
    create_household_table, create_households, create_countries,
)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network
from disruptsc.init_pipeline.routing import setup_logistic_routes

from disruptsc.run_pipeline.cache import (
    parse_cache_arg,
    cache_transport_network, load_cached_transport_network,
    cache_agents, load_cached_agents,
    cache_sc_network, load_cached_sc_network,
    cache_logistic_routes, load_cached_logistic_routes,
)
from disruptsc.run_pipeline.simulate import (
    run_initial_state, run_disruption, run_criticality,
    set_initial_conditions,
)
from disruptsc.run_pipeline.export import (
    export_transport_flows, export_summary, export_logistics_report,
    export_initial_state, export_static_tables, MCWriter,
)


def main():
    args = _parse_args()
    scope = args.scope

    setup_logging(args.log_level)
    logging.info(f"DisruptSC v2 — scope={scope}")

    # Load config + build params
    config = load_config(scope)
    tp, sp, ap, lp = build_params(config)
    cache_flags = parse_cache_arg(args.cache)
    export_folder = setup_output(config, sp)

    # Override t_final / io_cutoff from CLI if given
    if args.duration:
        sp = _replace_frozen(sp, t_final=args.duration)
    if args.io_cutoff is not None:
        ap = _replace_frozen(ap, io_cutoff=args.io_cutoff)

    filepaths = config.get("filepaths", {})
    transport_modes = config.get("transport_modes", ["roads"])
    logistics_raw = config.get("logistics", {})

    # ------------------------------------------------------------------
    # Stage 1: Transport network
    # ------------------------------------------------------------------
    if cache_flags["transport_network"]:
        logging.info("Loading transport network from cache")
        transport_network, transport_edges, transport_nodes = load_cached_transport_network()
    else:
        logging.info("Building transport network")
        transport_network, transport_edges, transport_nodes = build_transport_network(
            transport_modes, filepaths, logistics_raw, sp.time_resolution,
            capacity_overrides=config.get("transport_capacity_overrides"),
            default_transport_capacity=config.get("default_transport_capacity"),
        )
        cache_transport_network(transport_network, transport_edges, transport_nodes)

    # ------------------------------------------------------------------
    # Stage 2: Agents
    # ------------------------------------------------------------------
    if cache_flags["agents"]:
        logging.info("Loading agents from cache")
        mrio, sector_table, firms, firm_table, households, household_table, countries = load_cached_agents()
    else:
        logging.info("Building agents")
        mrio = load_mrio(filepaths.get("mrio"), ap.monetary_units_in_data)
        sector_table = load_sector_table(filepaths.get("sector_table"))
        usd_per_ton = load_usd_per_ton(filepaths.get("usd_per_ton"))

        # Filter sectors
        selected = filter_sectors(
            mrio, ap.cutoff_sector_output, ap.cutoff_sector_demand,
            ap.combine_sector_cutoff, ap.sectors_to_include,
            ap.sectors_to_exclude, ap.monetary_units_in_data,
        )

        # Firms
        firm_table = create_firm_table(
            mrio, sector_table, filepaths.get("firms_spatial"),
            filepaths.get("households_spatial"), usd_per_ton,
            transport_nodes, ap,
        )
        firms = create_firms(firm_table, ap)
        load_tech_coefs(firms, mrio, ap.io_cutoff)
        load_inventories(firms, ap.inventory_duration_targets,
                         sp.time_resolution, sector_table)

        # Households
        present_rs = [f"{rs[0]}_{rs[1]}" for rs in selected]
        household_table, consumption = create_household_table(
            mrio, filepaths.get("households_spatial"), transport_nodes,
            present_rs, ap,
        )
        households = create_households(household_table, consumption)

        # Countries
        countries = create_countries(
            mrio, transport_nodes, filepaths.get("countries_spatial"),
            usd_per_ton, sp.time_resolution, ap,
            transport_edges=transport_edges,
        )

        cache_agents(firms, households, countries, mrio, sector_table, firm_table, household_table)

    # ------------------------------------------------------------------
    # Stage 3: Supply chain network
    # ------------------------------------------------------------------
    if cache_flags["sc_network"]:
        logging.info("Loading SC network from cache")
        sc_network, firms, households, countries = load_cached_sc_network()
    else:
        logging.info("Building supply chain network")
        sc_network = build_supply_chain_network(
            firms, households, countries, mrio, sector_table,
            ap.nb_suppliers_per_input, ap.weight_localization_firm,
            ap.weight_localization_household,
            lp.sector_to_cargo_type, transport_network,
        )
        cache_sc_network(sc_network, firms, households, countries)

    # ------------------------------------------------------------------
    # Stage 3b: Set initial conditions (before routing, so links have
    #           equilibrium orders for capacity-aware route assignment)
    # ------------------------------------------------------------------
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)

    # ------------------------------------------------------------------
    # Stage 4: Logistic routes
    # ------------------------------------------------------------------
    if cache_flags["logistic_routes"]:
        logging.info("Loading logistic routes from cache")
        sc_network, transport_network, cl_table, firms, households, countries = load_cached_logistic_routes()
    else:
        if tp.with_transport:
            logging.info("Setting up logistic routes")
            cl_table = setup_logistic_routes(
                sc_network, transport_network, firms, countries,
                tp, lp.nb_cost_profiles,
                max_capacity_iterations=config.get("capacity_routing_max_iterations", 3),
            )
        else:
            cl_table = None
        cache_logistic_routes(sc_network, transport_network, cl_table, firms, households, countries)

    # ------------------------------------------------------------------
    # Stage 5: Run simulation
    # ------------------------------------------------------------------
    sim_type = sp.simulation_type

    # Extract monitored edge names from capacity overrides (if any)
    capacity_overrides = config.get("transport_capacity_overrides", {})
    monitored_edges = list(capacity_overrides.keys()) if capacity_overrides else None

    if sim_type == "initial_state":
        logging.info("Running initial state simulation")
        data = run_initial_state(
            sc_network, transport_network, firms, households, countries, tp, sp,
            export_folder=export_folder,
            monitored_edges=monitored_edges,
        )
        if export_folder:
            export_transport_flows(data["flow"], transport_edges, export_folder)
            export_initial_state(sc_network, export_folder)
            if data.get("logistics_reports"):
                export_logistics_report(data["logistics_reports"], export_folder, tp.monetary_units)

    elif sim_type == "disruption":
        if sp.is_monte_carlo:
            _run_monte_carlo(sc_network, transport_network, firms, households, countries,
                             tp, sp, config, transport_edges, firm_table, household_table)
        else:
            logging.info(f"Running disruption simulation (t_final={sp.t_final})")
            all_data = run_disruption(
                sc_network, transport_network, firms, households, countries,
                tp, sp, config.get("disruptions"), transport_edges, firm_table, sp.t_final,
                export_folder=export_folder,
                monitored_edges=monitored_edges,
            )
            if export_folder:
                export_transport_flows(all_data["transport_flow"], transport_edges, export_folder)
                export_summary(all_data["household"], all_data["country"],
                               household_table if not isinstance(household_table, type(None)) else None,
                               tp.monetary_units, export_folder)
                if all_data.get("logistics_reports"):
                    export_logistics_report(all_data["logistics_reports"], export_folder, tp.monetary_units)

    elif sim_type == "criticality":
        import copy
        crit_cfg = config.get("criticality", {})
        duration = crit_cfg.get("duration", 4)
        t_final = sp.t_final if sp.t_final else duration + 2

        # Filter edges to test
        attr_filter = crit_cfg.get("attribute")
        edge_values = crit_cfg.get("edges", [])
        if attr_filter and edge_values:
            mask = transport_edges[attr_filter].isin(edge_values)
            edges_to_test = transport_edges.loc[mask, "id"].tolist()
        else:
            edges_to_test = transport_edges["id"].tolist()

        logging.info(f"Running criticality for {len(edges_to_test)} edges")
        all_results = []
        for i, edge_id in enumerate(edges_to_test):
            logging.info(f"Criticality edge {i+1}/{len(edges_to_test)}: {edge_id}")
            # Deep-copy everything together so internal references are preserved
            state = copy.deepcopy({
                "sc": sc_network, "tn": transport_network,
                "firms": firms, "hh": households, "countries": countries,
            })
            all_data = run_criticality(
                state["sc"], state["tn"], state["firms"], state["hh"], state["countries"],
                tp, sp, edge_id, duration, t_final,
            )
            losses = export_summary(all_data["household"], all_data["country"],
                                     monetary_units=tp.monetary_units)
            losses["edge_id"] = edge_id
            all_results.append(losses)

        # Export criticality results
        if export_folder and all_results:
            import pandas as pd
            crit_df = pd.DataFrame(all_results)
            crit_path = export_folder / "criticality_results.csv"
            crit_df.to_csv(crit_path, index=False)
            logging.info(f"Criticality results saved to {crit_path}")

    else:
        raise ValueError(f"Unknown simulation_type: {sim_type}")

    # ------------------------------------------------------------------
    # Stage 6: Export static tables
    # ------------------------------------------------------------------
    if export_folder:
        export_static_tables(firm_table, household_table, transport_edges, transport_nodes, export_folder)
        logging.info(f"Results exported to {export_folder}")

    logging.info("Done.")


# ------------------------------------------------------------------
# Monte Carlo
# ------------------------------------------------------------------

def _run_monte_carlo(sc_network, transport_network, firms, households, countries,
                     tp, sp, config, transport_edges, firm_table, household_table):
    from datetime import datetime
    import os

    scope = config["scope"]
    out_dir = paths.OUTPUT_FOLDER / scope
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    mc_path = out_dir / f"disruption_{ts}_pid{os.getpid()}.csv"
    writer = MCWriter(mc_path)

    logging.info(f"Monte Carlo: {sp.mc_repetitions} repetitions")
    for i in range(sp.mc_repetitions):
        logging.info(f"--- MC iteration {i + 1}/{sp.mc_repetitions} ---")
        all_data = run_disruption(
            sc_network, transport_network, firms, households, countries,
            tp, sp, config.get("disruptions"), transport_edges, firm_table, sp.t_final,
        )
        losses = export_summary(
            all_data["household"], all_data["country"],
            household_table, tp.monetary_units, export_folder=None,
        )
        writer.add_iteration(i, losses["household_loss"], losses["country_loss"])

    writer.save()
    logging.info(f"MC results: {mc_path}")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _replace_frozen(dc, **overrides):
    """Return a copy of a frozen dataclass with some fields replaced."""
    from dataclasses import fields as dc_fields, asdict
    d = asdict(dc)
    d.update(overrides)
    return type(dc)(**d)


def _parse_args():
    parser = argparse.ArgumentParser(description="DisruptSC v2")
    parser.add_argument("scope", help="Region scope (e.g. ECA, Gulf, Armenia)")
    parser.add_argument("--cache", default=None,
                        help="Cache preset (same_transport_network_new_agents, etc.)")
    parser.add_argument("--duration", type=int, default=None,
                        help="Override t_final")
    parser.add_argument("--io_cutoff", type=float, default=None,
                        help="Override IO cutoff")
    parser.add_argument("--log_level", default="info", choices=["info", "debug"])
    parser.add_argument("--cache_isolation", action="store_true",
                        help="Isolate cache per process")
    return parser.parse_args()


if __name__ == "__main__":
    main()
