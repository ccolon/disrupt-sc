"""CLI entry point for DisruptSC v2."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from disruptsc import paths
from disruptsc.config import load_config, build_params, setup_output, setup_logging

from disruptsc.init_pipeline.load_data import (
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors,
)
from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.init_pipeline.agents import (
    create_firm_table, create_firms, load_tech_coefs, load_inventories,
    configure_household_inventories,
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
    set_initial_conditions, prepare_disruption_baseline, continue_disruption_run,
)
from disruptsc.run_pipeline.disruption import parse_disruptions
from disruptsc.run_pipeline.export import (
    export_transport_flows, export_summary, export_logistics_report,
    export_initial_state, export_static_tables, export_mrio_summary,
    MCWriter, CsvWriter, summarize_criticality_losses,
    create_criticality_results_writer, criticality_result_to_row,
    export_criticality_geojson,
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

    def _configure_households(households):
        configure_household_inventories(
            households,
            ap.enable_household_inventories,
            ap.inventory_duration_targets,
            ap.inventory_restoration_time,
            sp.time_resolution,
            sector_table,
        )

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
    selected = None  # filtered MRIO sectors (set when building fresh)
    if cache_flags["agents"]:
        logging.info("Loading agents from cache")
        mrio, sector_table, firms, firm_table, households, household_table, countries = load_cached_agents()
        _configure_households(households)
    else:
        logging.info("Building agents")
        mrio = load_mrio(filepaths.get("mrio"), ap.monetary_units_in_data)
        sector_table = load_sector_table(filepaths.get("sector_table"))
        usd_per_ton = load_usd_per_ton(sector_table)

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
            present_rs, ap, time_resolution=sp.time_resolution,
        )
        households = create_households(household_table, consumption)
        _configure_households(households)

        # Countries
        countries = create_countries(
            mrio, transport_nodes, filepaths.get("countries_spatial"),
            usd_per_ton, sp.time_resolution, ap,
            transport_edges=transport_edges,
        )

        cache_agents(firms, households, countries, mrio, sector_table, firm_table, household_table)

    # Export MRIO summary (for reporting comparison)
    if export_folder:
        export_mrio_summary(mrio, selected, export_folder)

    # ------------------------------------------------------------------
    # Stage 3: Supply chain network
    # ------------------------------------------------------------------
    if cache_flags["sc_network"]:
        logging.info("Loading SC network from cache")
        sc_network, firms, households, countries = load_cached_sc_network()
        _configure_households(households)
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
        _configure_households(households)
    else:
        if tp.with_transport:
            logging.info("Setting up logistic routes")
            cl_table = setup_logistic_routes(
                sc_network, transport_network, firms, countries,
                tp,
                max_capacity_iterations=config.get("capacity_routing_max_iterations", 10),
                export_folder=export_folder,
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
        crit_sp = _replace_frozen(sp, epsilon_stop=0.0)
        scenarios = crit_cfg.get("scenarios")

        if scenarios:
            logging.info(f"Running scenario-based criticality for {len(scenarios)} scenario(s)")
            csv_path, geojson_path = _get_criticality_output_paths(scope)
            with create_criticality_results_writer(csv_path) as csv_writer:
                scenario_results = _run_criticality_scenarios(
                    scenarios, sc_network, transport_network, firms, households, countries,
                    tp, crit_sp, transport_edges, firm_table, duration, t_final,
                    csv_writer=csv_writer,
                )
            export_criticality_geojson(scenario_results, transport_edges, geojson_path)
            logging.info(f"Criticality results saved to {csv_path}")
            logging.info(f"Criticality geodata saved to {geojson_path}")
        else:
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
            csv_path, _ = _get_criticality_output_paths(scope)
            with CsvWriter(
                csv_path, ["household_loss", "country_loss", "edge_id"], flush_each_write=True,
            ) as csv_writer:
                for i, edge_id in enumerate(edges_to_test):
                    logging.info(f"Criticality edge {i+1}/{len(edges_to_test)}: {edge_id}")
                    # Deep-copy everything together so internal references are preserved
                    state = copy.deepcopy({
                        "sc": sc_network, "tn": transport_network,
                        "firms": firms, "hh": households, "countries": countries,
                    })
                    all_data = run_criticality(
                        state["sc"], state["tn"], state["firms"], state["hh"], state["countries"],
                        tp, crit_sp, edge_id, duration, t_final,
                    )
                    losses = export_summary(
                        all_data["household"], all_data["country"],
                        monetary_units=tp.monetary_units,
                    )
                    losses["edge_id"] = edge_id
                    all_results.append(losses)
                    csv_writer.write_row(losses)

            if all_results:
                logging.info(f"Criticality results saved to {csv_path}")

    else:
        raise ValueError(f"Unknown simulation_type: {sim_type}")

    # ------------------------------------------------------------------
    # Stage 6: Export static tables
    # ------------------------------------------------------------------
    if export_folder:
        export_static_tables(firm_table, household_table, transport_edges, transport_nodes, export_folder)
        logging.info(f"Results exported to {export_folder}")

    # ------------------------------------------------------------------
    # Stage 7: Generate report (optional)
    # ------------------------------------------------------------------
    if export_folder and args.open:
        _generate_and_open_report(sim_type, export_folder)

    logging.info("Done.")


# ------------------------------------------------------------------
# Report generation
# ------------------------------------------------------------------

def _generate_and_open_report(sim_type: str, export_folder):
    """Generate the appropriate HTML report and open it in the browser."""
    import webbrowser

    report_map = {
        "initial_state": "disruptsc.reporting.initial_state",
        "disruption": "disruptsc.reporting.disruption",
    }
    module_name = report_map.get(sim_type)
    if not module_name:
        logging.info(f"No report template for simulation_type={sim_type}")
        return

    try:
        from importlib import import_module
        mod = import_module(module_name)
        html_path = mod.generate_report(export_folder)
        logging.info(f"Report generated: {html_path}")
        webbrowser.open(str(html_path))
    except Exception as exc:
        logging.warning(f"Report generation failed: {exc}")


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
def _run_criticality_scenarios(scenarios, sc_network, transport_network, firms,
                               households, countries, tp, sp, transport_edges,
                               firm_table, duration, t_final, csv_writer=None):
    import copy

    normalized_scenarios = _normalize_criticality_scenarios(scenarios, transport_edges)
    baseline_all_data, baseline_logistics_reports, baseline_routing_summaries = prepare_disruption_baseline(
        sc_network, transport_network, firms, households, countries,
        tp, sp, writers=None, monitored_edges=None,
    )
    baseline_snapshot = {
        "sc": sc_network,
        "tn": transport_network,
        "firms": firms,
        "hh": households,
        "countries": countries,
        "all_data": baseline_all_data,
        "logistics_reports": baseline_logistics_reports,
        "routing_summaries": baseline_routing_summaries,
    }
    results = []
    for i, edge_names in enumerate(normalized_scenarios, start=1):
        logging.info(
            "Criticality scenario %s/%s: %s",
            i, len(normalized_scenarios), ", ".join(edge_names),
        )
        disruptions = [{
            "type": "transport_disruption",
            "attribute": "name",
            "values": edge_names,
            "capacity_reduction": 1.0,
            "start_time": 1,
            "duration": duration,
        }]
        state = copy.deepcopy(baseline_snapshot)
        parsed_disruptions = parse_disruptions(
            disruptions, transport_edges, firm_table, state["firms"], tp.monetary_units,
        )
        for disruption in parsed_disruptions:
            disruption.log_info()

        all_data, logistics_reports, routing_summaries = continue_disruption_run(
            state["sc"], state["tn"], state["firms"], state["hh"], state["countries"],
            tp, sp, disruptions=parsed_disruptions, t_start=1, t_final=t_final,
            all_data=state["all_data"],
            logistics_reports=state["logistics_reports"],
            all_routing_summaries=state["routing_summaries"],
            writers=None,
            monitored_edges=None,
        )
        all_data["logistics_reports"] = logistics_reports
        losses = summarize_criticality_losses(all_data["household"], all_data["country"])
        losses["edge_names"] = edge_names
        results.append(losses)
        if csv_writer is not None:
            csv_writer.write_row(criticality_result_to_row(losses))
    return results


def _normalize_criticality_scenarios(scenarios, transport_edges):
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("criticality.scenarios must be a non-empty list of edge-name lists")

    available_names = set(transport_edges["name"].dropna().astype(str))
    normalized = []
    for i, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, list) or not scenario:
            raise ValueError(
                f"criticality.scenarios[{i - 1}] must be a non-empty list of edge names"
            )
        edge_names = list(dict.fromkeys(str(name) for name in scenario))
        missing = [name for name in edge_names if name not in available_names]
        if missing:
            raise ValueError(
                f"criticality.scenarios[{i - 1}] contains unknown edge name(s): {missing}"
            )
        normalized.append(edge_names)
    return normalized


def _get_criticality_output_paths(scope: str):
    from datetime import datetime

    scope_dir = paths.OUTPUT_FOLDER / scope
    scope_dir.mkdir(parents=True, exist_ok=True)
    run_dir = scope_dir / f"criticality_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir / "criticality_results.csv", run_dir / "criticality_results.geojson"


def _replace_frozen(dc, **overrides):
    """Return a copy of a frozen dataclass with some fields replaced."""
    from dataclasses import asdict
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
    parser.add_argument("--open", action="store_true",
                        help="Generate report and open it in browser after simulation")
    return parser.parse_args()


if __name__ == "__main__":
    main()
