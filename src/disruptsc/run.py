"""CLI entry point for DisruptSC v2."""

from __future__ import annotations

import argparse
import logging
import sys
import threading
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ---------------------------------------------------------------------------
# Scaling guards for large MRIOs (see also: pickle hooks in network/route.py
# and network/commercial_link.py, sparse Leontief in run_pipeline/simulate.py)
# ---------------------------------------------------------------------------
# Caching the routes/sc_network on a large scope (e.g. ~316k Route objects on
# the China scope) recurses deeper than Python's default 1000-frame limit.
# 50000 frames at ~300 bytes of C stack each ≈ 15 MB, which sits comfortably
# inside the 64 MB thread stack we allocate below on Windows (and inside the
# default 8 MB main-thread stack on Linux/macOS).
sys.setrecursionlimit(50000)

# Windows main threads default to a 1–4 MB C stack, which Python can exhaust
# during deep pickle traversals even before Python's own recursion guard
# fires. On Windows we therefore re-enter main() in a worker thread with an
# explicit large stack. On other platforms the default 8 MB main-thread stack
# is sufficient after the pickle hooks above.
_LARGE_STACK_SIZE = 64 * 1024 * 1024  # 64 MB
_NEEDS_LARGE_STACK = sys.platform == "win32"

from disruptsc import paths
from disruptsc.config import load_config, build_params, setup_output, setup_logging

from disruptsc.init_pipeline.load_data import (
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors,
)
from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.init_pipeline.agents import (
    create_firm_table, create_firms, load_tech_coefs, load_input_criticality,
    load_inventories, configure_household_inventories,
    create_household_table, create_households, create_countries,
)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network
from disruptsc.init_pipeline.routing import setup_logistic_routes

from disruptsc.run_pipeline.cache import (
    setup_cache_isolation,
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
    export_criticality_geojson, CRITICALITY_RESULT_COLUMNS,
)


def main():
    """Entry point. On Windows, re-spawn in a 64 MB-stack thread to avoid
    STATUS_STACK_OVERFLOW during pickle of large logistic-route caches."""
    if not _NEEDS_LARGE_STACK or getattr(threading.current_thread(),
                                          "_disruptsc_large_stack", False):
        return _main_impl()

    captured_exc: list[BaseException] = []
    captured_exit: list = [None]

    def _run():
        threading.current_thread()._disruptsc_large_stack = True
        try:
            _main_impl()
        except SystemExit as e:
            captured_exit[0] = e.code
        except BaseException as e:  # noqa: BLE001
            captured_exc.append(e)

    prev = threading.stack_size(_LARGE_STACK_SIZE)
    try:
        t = threading.Thread(target=_run, name="disruptsc-main", daemon=True)
        t.start()
        t.join()
    finally:
        threading.stack_size(prev or 0)

    if captured_exc:
        raise captured_exc[0]
    if captured_exit[0] is not None:
        sys.exit(captured_exit[0])


def _main_impl():
    args = _parse_args()
    scope = args.scope

    setup_logging(args.log_level)

    # Load config, apply CLI overrides, then hand off to execute().
    config = load_config(scope)
    if args.simulation_type:
        config["simulation_type"] = args.simulation_type
    if args.duration is not None:
        config["t_final"] = args.duration
    if args.flow_coverage is not None:
        config["flow_coverage"] = args.flow_coverage
    if args.seed is not None:
        config["seed"] = args.seed

    return execute(config, cache=args.cache,
                   cache_isolation=args.cache_isolation, open_report=args.open)


def execute(config: dict, *, cache: str | None = None,
            cache_isolation: bool = False, open_report: bool = False,
            export_folder: Path | str | None = None):
    """Run the full pipeline for a (already-loaded, already-overridden) config.

    Shared by the CLI (``_main_impl``) and programmatic drivers (e.g. the
    earthquake ensemble). When *export_folder* is given, it is used verbatim
    (created if needed, with a parameters.yaml snapshot) instead of the
    timestamped folder ``setup_output`` would create — this is how a driver
    routes each (variant, seed) run to ``runs/earthquake/<variant>/<seed>/``.
    """
    scope = config["scope"]
    logging.info(f"DisruptSC v2 — scope={scope}")

    tp, sp, ap, lp = build_params(config)
    cache_flags = parse_cache_arg(cache)
    if cache_isolation:
        setup_cache_isolation(scope)
    if export_folder is None:
        export_folder = setup_output(config, sp)
    else:
        export_folder = Path(export_folder)
        export_folder.mkdir(parents=True, exist_ok=True)
        with open(export_folder / "parameters.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)

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
            use_cargo_types=tp.use_cargo_types,
        )
        cache_transport_network(transport_network, transport_edges, transport_nodes)

    # ------------------------------------------------------------------
    # Stage 2: Agents
    # ------------------------------------------------------------------
    selection = None  # flow-coverage Selection (set when building fresh)
    if cache_flags["agents"]:
        logging.info("Loading agents from cache")
        mrio, sector_table, firms, firm_table, households, household_table, countries = load_cached_agents()
        _configure_households(households)
    else:
        logging.info("Building agents")
        mrio = load_mrio(filepaths.get("mrio"), ap.monetary_units_in_data)
        sector_table = load_sector_table(filepaths.get("sector_table"))
        usd_per_ton = load_usd_per_ton(sector_table)

        # Filter MRIO via flow_coverage (one knob, replaces the old cutoffs)
        selection = filter_sectors(
            mrio, ap.flow_coverage,
            ap.sectors_to_include, ap.sectors_to_exclude,
        )

        # Firms
        firm_table = create_firm_table(
            mrio, sector_table, filepaths.get("firms_spatial"),
            filepaths.get("households_spatial"), usd_per_ton,
            transport_nodes, ap, selection,
        )
        firms = create_firms(firm_table, ap)
        load_tech_coefs(firms, mrio, selection)
        crit_path = filepaths.get("input_criticality")
        if crit_path and Path(crit_path).exists():
            load_input_criticality(firms, pd.read_csv(crit_path, index_col=0))
        load_inventories(firms, ap.inventory_duration_targets,
                         sp.time_resolution, sector_table)

        # Households
        household_table, consumption = create_household_table(
            mrio, filepaths.get("households_spatial"), transport_nodes,
            selection, ap, time_resolution=sp.time_resolution,
        )
        households = create_households(household_table, consumption)
        _configure_households(households)

        # Countries
        countries = create_countries(
            mrio, transport_nodes, filepaths.get("countries_spatial"),
            usd_per_ton, sp.time_resolution, ap, selection,
            transport_edges=transport_edges,
            countries_no_transport=tp.countries_no_transport,
        )

        cache_agents(firms, households, countries, mrio, sector_table, firm_table, household_table)

    # Export MRIO summary (for reporting comparison)
    if export_folder:
        kept_rs = list(selection.region_sectors) if selection is not None else None
        export_mrio_summary(mrio, kept_rs, export_folder)

    # ------------------------------------------------------------------
    # Stage 3: Supply chain network
    # ------------------------------------------------------------------
    if cache_flags["sc_network"]:
        logging.info("Loading SC network from cache")
        sc_network, firms, households, countries = load_cached_sc_network()
        _configure_households(households)
    else:
        logging.info("Building supply chain network")
        # Seed Python's `random` and numpy.random for reproducible
        # supplier-selection draws. This is the *only* RNG-driven stage
        # in the model (besides Monte-Carlo disruption arrival). When
        # sp.seed is None we leave the global RNGs alone (legacy
        # non-reproducible behavior).
        if sp.seed is not None:
            import random as _random
            _random.seed(sp.seed)
            np.random.seed(sp.seed)
            logging.info(f"Seeded RNGs with seed={sp.seed} before supply-chain build")
        # When cargo types are disabled, force every commercial link to use
        # the single "any" bucket — so the routing pipeline runs Dijkstra/LP
        # once instead of once per cargo type.
        effective_cargo_mapping = (
            lp.sector_to_cargo_type if tp.use_cargo_types else {"default": "any"}
        )
        sc_network = build_supply_chain_network(
            firms, households, countries, mrio, sector_table,
            ap.nb_suppliers_per_input, ap.weight_localization_firm,
            ap.weight_localization_household,
            effective_cargo_mapping, transport_network,
        )
        cache_sc_network(sc_network, firms, households, countries)

    # Auto-shrink: prune transport-network cargo types to those actually used
    # by the supply chain. No-op when only one cargo type is present. Done
    # before the logistic-route stage so Dijkstra/LP runs N× fewer times.
    used_cargo = {
        getattr(data["object"], "cargo_type", None)
        for _, _, data in sc_network.edges(data=True)
    }
    used_cargo.discard(None)
    used_cargo.discard("")
    if used_cargo:
        transport_network.shrink_cargo_types_to(used_cargo)

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
        from disruptsc.run_pipeline.fingerprint import (
            build_fingerprint, fingerprint_hash, save_fingerprint,
            load_fingerprint, diff_fingerprints,
        )
        crit_cfg = config.get("criticality", {})
        duration = crit_cfg.get("duration", 4)
        t_final = sp.t_final if sp.t_final else duration + 2
        skip_zero_flow = bool(crit_cfg.get("skip_zero_flow", True))
        top_n = crit_cfg.get("top_n")
        if top_n is not None:
            top_n = int(top_n)
        crit_sp = _replace_frozen(sp, epsilon_stop=0.0)
        scenarios = crit_cfg.get("scenarios")

        # --- Fingerprint + per-run subfolder + resume detection ---------------
        fp_payload = build_fingerprint(config, criticality_duration=duration)
        current_hash = fingerprint_hash(fp_payload)
        subfolder = _resolve_criticality_subfolder(crit_cfg, current_hash)
        run_id_explicit = bool(crit_cfg.get("run_id"))
        csv_path, geojson_path, sidecar_path = _get_criticality_output_paths(scope, subfolder)
        logging.info(
            f"Criticality output → {csv_path.parent} "
            f"(subfolder='{subfolder}', "
            f"{'user-supplied run_id' if run_id_explicit else 'auto from fingerprint'})"
        )

        prev_fp = load_fingerprint(sidecar_path)
        resume = False
        done_keys: set = set()
        if prev_fp is not None and csv_path.exists():
            if prev_fp.get("hash") != current_hash:
                # This can only happen with a user-supplied run_id that
                # collides between different parameter sets (auto subfolders
                # are hash-derived, so they can't collide).
                raise RuntimeError(
                    f"Cannot resume criticality results at {csv_path}: the "
                    f"current run's fingerprint differs from the previous one "
                    f"in subfolder '{subfolder}'.\n"
                    f"Either pick a different criticality.run_id, delete "
                    f"{csv_path.parent} to start fresh, or revert config/data "
                    f"to match. Changed keys:\n"
                    f"{diff_fingerprints(prev_fp, fp_payload)}"
                )
            done_keys = _load_done_criticality_keys(csv_path, is_scenario_mode=bool(scenarios))
            if done_keys:
                resume = True
                logging.info(
                    f"Resuming criticality from {csv_path.name}: "
                    f"{len(done_keys)} scenario(s) already complete"
                )
        # Always (re)write the sidecar so it reflects the current run, and
        # append/update a row in the top-level runs.csv index.
        save_fingerprint(fp_payload, sidecar_path)
        _update_criticality_index(
            scope, subfolder, fp_payload, current_hash,
            mode=("scenarios" if scenarios else "edges"),
            top_n=top_n, run_id_explicit=run_id_explicit,
        )

        # --- Baseline pass: produces per-edge flow for ranking/filtering ------
        logging.info("Running baseline (no disruption) to rank edges by flow")
        baseline_all_data, baseline_logistics, baseline_routing = prepare_disruption_baseline(
            sc_network, transport_network, firms, households, countries,
            tp, crit_sp, writers=None, monitored_edges=None,
        )
        baseline_flows = {
            row["id"]: float(row.get("flow_total_tons") or 0.0)
            for row in baseline_all_data["transport_flow"]
            if row.get("time_step") == 0
        }

        if scenarios:
            logging.info(f"Running scenario-based criticality for {len(scenarios)} scenario(s)")
            baseline_snapshot = {
                "sc": sc_network, "tn": transport_network,
                "firms": firms, "hh": households, "countries": countries,
                "all_data": baseline_all_data,
                "logistics_reports": baseline_logistics,
                "routing_summaries": baseline_routing,
            }
            with CsvWriter(
                csv_path, CRITICALITY_RESULT_COLUMNS,
                flush_each_write=True, append=resume,
            ) as csv_writer:
                scenario_results = _run_criticality_scenarios(
                    scenarios, transport_edges, firm_table,
                    baseline_snapshot, tp, crit_sp, duration, t_final,
                    done_keys=done_keys, csv_writer=csv_writer,
                )
            export_criticality_geojson(scenario_results, transport_edges, geojson_path)
            logging.info(f"Criticality results saved to {csv_path}")
            logging.info(f"Criticality geodata saved to {geojson_path}")
        else:
            edges_to_test = _select_legacy_criticality_edges(
                transport_edges, crit_cfg, baseline_flows,
                skip_zero_flow=skip_zero_flow, top_n=top_n,
            )
            remaining = [e for e in edges_to_test if e not in done_keys]
            logging.info(
                f"Running criticality for {len(remaining)} edge(s) "
                f"(of {len(edges_to_test)} selected, {len(done_keys)} already done)"
            )
            with CsvWriter(
                csv_path, ["household_loss", "country_loss", "edge_id"],
                flush_each_write=True, append=resume,
            ) as csv_writer:
                for i, edge_id in enumerate(remaining, start=1):
                    logging.info(
                        f"Criticality edge {i}/{len(remaining)}: id={edge_id} "
                        f"(baseline tons={baseline_flows.get(edge_id, 0):,.1f})"
                    )
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
                    csv_writer.write_row(losses)
            logging.info(f"Criticality results saved to {csv_path}")

    else:
        raise ValueError(f"Unknown simulation_type: {sim_type}")

    # ------------------------------------------------------------------
    # Stage 6: Export static tables
    # ------------------------------------------------------------------
    if export_folder:
        export_static_tables(
            firm_table, household_table, transport_edges, transport_nodes,
            export_folder,
            countries_spatial_path=filepaths.get("countries_spatial"),
        )
        logging.info(f"Results exported to {export_folder}")

    # ------------------------------------------------------------------
    # Stage 7: Generate report (optional)
    # ------------------------------------------------------------------
    if export_folder and open_report:
        _generate_and_open_report(sim_type, export_folder)

    logging.info("Done.")
    return export_folder


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
def _run_criticality_scenarios(scenarios, transport_edges, firm_table,
                               baseline_snapshot, tp, sp, duration, t_final,
                               *, done_keys: set | None = None, csv_writer=None):
    """Run scenario-mode criticality. Caller supplies a baseline snapshot
    (already advanced through ``prepare_disruption_baseline``) so we never
    re-run the baseline and can resume cheaply via *done_keys*.
    """
    import copy

    normalized_scenarios = _normalize_criticality_scenarios(scenarios, transport_edges)
    done_keys = done_keys or set()
    results = []
    skipped = 0
    for i, edge_names in enumerate(normalized_scenarios, start=1):
        key = _scenario_key(edge_names)
        if key in done_keys:
            skipped += 1
            continue
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
            time_resolution=sp.time_resolution,
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
    if skipped:
        logging.info(f"Skipped {skipped} scenario(s) already present in the CSV")
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


_EPSILON_TONS = 1e-6


def _scenario_key(edge_names) -> str:
    """Order-independent key for a multi-edge scenario."""
    return "|".join(sorted(str(n) for n in edge_names))


def _select_legacy_criticality_edges(transport_edges, crit_cfg, baseline_flows,
                                     *, skip_zero_flow: bool, top_n: int | None):
    """Pick which edges to test in legacy (one-edge-at-a-time) criticality mode.

    Order of operations:
      1. Apply ``criticality.attribute`` + ``criticality.edges`` filter (if set).
      2. Drop edges whose baseline tons flow is ≤ ε (when *skip_zero_flow*).
      3. Sort by descending baseline flow.
      4. Truncate to *top_n* (when set).
    """
    attr_filter = crit_cfg.get("attribute")
    edge_values = crit_cfg.get("edges", []) or []
    if attr_filter and edge_values:
        mask = transport_edges[attr_filter].isin(edge_values)
        edge_ids = transport_edges.loc[mask, "id"].tolist()
        logging.info(
            f"Criticality attribute filter ({attr_filter}∈{edge_values}): "
            f"{len(edge_ids)} edges"
        )
    else:
        edge_ids = transport_edges["id"].tolist()

    if skip_zero_flow:
        before = len(edge_ids)
        edge_ids = [e for e in edge_ids if baseline_flows.get(e, 0.0) > _EPSILON_TONS]
        if before > len(edge_ids):
            logging.info(f"Skipped {before - len(edge_ids)} zero-flow edges")

    edge_ids.sort(key=lambda e: baseline_flows.get(e, 0.0), reverse=True)

    if top_n is not None and top_n > 0 and top_n < len(edge_ids):
        edge_ids = edge_ids[:top_n]
        logging.info(f"Restricted to top {top_n} edges by baseline flow")
    return edge_ids


def _load_done_criticality_keys(csv_path, *, is_scenario_mode: bool) -> set:
    """Read an existing criticality_results.csv and return the set of
    scenario keys already present. Scenario mode keys are
    ``|``-joined-sorted edge-name strings; legacy mode keys are integer
    edge ids."""
    import csv as _csv
    import json as _json
    keys: set = set()
    if not Path(csv_path).exists():
        return keys
    with open(csv_path, newline="") as f:
        reader = _csv.DictReader(f)
        for row in reader:
            if is_scenario_mode:
                raw = row.get("edge") or "[]"
                try:
                    names = _json.loads(raw)
                except _json.JSONDecodeError:
                    continue
                keys.add(_scenario_key(names))
            else:
                eid = row.get("edge_id")
                if eid is None or eid == "":
                    continue
                try:
                    keys.add(int(eid))
                except ValueError:
                    continue
    return keys


def _get_criticality_output_paths(scope: str, subfolder: str):
    """Return (csv, geojson, fingerprint) paths inside a per-run subfolder.

    Each unique parameter combination lands in its own subfolder under
    ``output/<scope>/criticality/`` so distinct sweeps coexist without
    collision. The subfolder is either the user's ``criticality.run_id``
    or the first eight hex chars of the fingerprint hash (see
    ``_resolve_criticality_subfolder``).
    """
    run_dir = paths.OUTPUT_FOLDER / scope / "criticality" / subfolder
    run_dir.mkdir(parents=True, exist_ok=True)
    return (
        run_dir / "criticality_results.csv",
        run_dir / "criticality_results.geojson",
        run_dir / "criticality_results.fingerprint.json",
    )


def _resolve_criticality_subfolder(crit_cfg: dict, fingerprint_hash: str) -> str:
    """Pick the per-run subfolder name.

    User-supplied ``criticality.run_id`` wins (sanitized for filesystem
    safety). Otherwise we use the first eight hex chars of the
    fingerprint — distinct parameter combos automatically land in
    distinct folders.
    """
    raw = crit_cfg.get("run_id")
    if raw:
        # Keep only filename-safe characters
        safe = "".join(c if (c.isalnum() or c in "-_.") else "_"
                       for c in str(raw).strip())
        if safe:
            return safe
    return fingerprint_hash[:8]


def _update_criticality_index(scope: str, subfolder: str, fp_payload: dict,
                              fp_hash: str, mode: str, top_n, run_id_explicit: bool):
    """Upsert one row in ``output/<scope>/criticality/runs.csv``.

    Lightweight directory of all criticality runs in this scope so the
    user can browse hash-named subfolders without opening each sidecar.
    """
    import csv as _csv
    from datetime import datetime as _dt

    index_path = paths.OUTPUT_FOLDER / scope / "criticality" / "runs.csv"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = fp_payload.get("config") or {}
    now = _dt.now().isoformat(timespec="seconds")
    columns = [
        "subfolder", "run_id_explicit", "fingerprint", "mode",
        "duration", "top_n", "seed",
        "flow_coverage", "use_cargo_types",
        "version", "git_sha", "first_seen", "last_run",
    ]
    new_row = {
        "subfolder": subfolder,
        "run_id_explicit": "yes" if run_id_explicit else "",
        "fingerprint": fp_hash,
        "mode": mode,
        "duration": fp_payload.get("criticality_duration"),
        "top_n": top_n if top_n is not None else "",
        "seed": cfg.get("seed") if cfg.get("seed") is not None else "",
        "flow_coverage": cfg.get("flow_coverage"),
        "use_cargo_types": cfg.get("use_cargo_types"),
        "version": fp_payload.get("version"),
        "git_sha": (fp_payload.get("git_sha") or "")[:12],
        "first_seen": now,
        "last_run": now,
    }
    rows = []
    if index_path.exists():
        with open(index_path, newline="", encoding="utf-8") as f:
            for r in _csv.DictReader(f):
                if r.get("subfolder") == subfolder:
                    # Preserve original first_seen, update last_run
                    new_row["first_seen"] = r.get("first_seen") or now
                    continue
                rows.append(r)
    rows.append(new_row)
    with open(index_path, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in columns})


def _replace_frozen(dc, **overrides):
    """Return a copy of a frozen dataclass with some fields replaced."""
    from dataclasses import asdict
    d = asdict(dc)
    d.update(overrides)
    return type(dc)(**d)


def _parse_args():
    from disruptsc._version import __version__

    parser = argparse.ArgumentParser(description="DisruptSC v2")
    parser.add_argument("scope", help="Region scope (e.g. ECA, Gulf, Armenia)")
    parser.add_argument("--cache", default=None,
                        help="Cache preset (same_transport_network_new_agents, etc.)")
    parser.add_argument("--simulation_type", choices=["initial_state", "disruption", "criticality"],
                        help="Override simulation_type from the YAML configuration")
    parser.add_argument("--duration", type=int, default=None,
                        help="Override t_final")
    parser.add_argument("--flow_coverage", type=float, default=None,
                        help="Override flow_coverage (cumulative flow-coverage fraction in (0, 1])")
    parser.add_argument("--seed", type=int, default=None,
                        help="Override the RNG seed for reproducible supplier selection")
    parser.add_argument("--log_level", default="info", choices=["info", "debug"])
    parser.add_argument("--verbose", action="store_true",
                        help="Alias for --log_level debug")
    parser.add_argument("--cache_isolation", action="store_true",
                        help="Isolate cache per process")
    parser.add_argument("--open", action="store_true",
                        help="Generate report and open it in browser after simulation")
    parser.add_argument("--version", action="version", version=f"DisruptSC {__version__}")
    args = parser.parse_args()
    if args.verbose:
        args.log_level = "debug"
    return args


if __name__ == "__main__":
    main()
