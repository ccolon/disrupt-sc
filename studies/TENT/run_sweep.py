"""TENT flood-event sweep: per-event supply-chain losses.

Builds the TENT model ONCE, advances the shared no-disruption baseline to t=0,
and **pickles that pre-disruption state to disk** (like a criticality baseline).
Every subsequent run/worker loads the snapshot (fast) instead of rebuilding.
For each flood event it deep-copies the snapshot, closes the flooded road edges
at 100% capacity for the event's recovery duration, runs for exactly
``2 x duration_steps`` steps (NO epsilon early-stop), and appends the cumulative
household + country loss to a resumable CSV.

Design decisions (locked):
  - daily time resolution
  - full closure (100%) of every flooded edge
  - t_final = 2 * recovery duration, no epsilon_stop
  - all 917 events, output = per-event losses only

Usage:
  python studies/TENT/run_sweep.py --build-only          # build + cache snapshot
  python studies/TENT/run_sweep.py --limit 1             # one-event smoke test
  python studies/TENT/run_sweep.py                       # full sweep (single proc)
  python studies/TENT/run_sweep.py --shard 0 --of 8      # worker 0 of 8 (parallel)
Resumable: re-running skips events already present in the output CSV.
"""
from __future__ import annotations

import argparse
import copy
import csv
import dataclasses
import hashlib
import json
import logging
import pickle
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, build_params, setup_logging, days_per_timestep  # noqa: E402
from disruptsc.init_pipeline.transport import build_transport_network          # noqa: E402
from disruptsc.init_pipeline.load_data import (                                # noqa: E402
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors)
from disruptsc.init_pipeline.agents import (                                   # noqa: E402
    create_firm_table, create_firms, load_tech_coefs, load_input_criticality,
    load_inventories, configure_household_inventories, create_household_table,
    create_households, create_countries)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network    # noqa: E402
from disruptsc.init_pipeline.routing import setup_logistic_routes              # noqa: E402
from disruptsc.run_pipeline.simulate import (                                  # noqa: E402
    prepare_disruption_baseline, continue_disruption_run, set_initial_conditions)
from disruptsc.run_pipeline.disruption import TransportDisruption, Recovery    # noqa: E402
from disruptsc.run_pipeline.export import summarize_criticality_losses         # noqa: E402

from studies.TENT.events import load_events, DEFAULT_XLSX, all_flooded_edge_ids  # noqa: E402

OUT_DIR = ROOT / "output" / "TENT" / "flood_sweep"
OUT_DEFAULT = OUT_DIR / "event_losses.csv"
SNAPSHOT_DEFAULT = OUT_DIR / "baseline_snapshot.pkl"
COLUMNS = ["catchment", "return_period", "n_edges", "duration_days",
           "duration_steps", "t_final", "household_loss", "country_loss",
           "wall_seconds"]

# Config knobs that would invalidate a cached snapshot if changed.
_FINGERPRINT_KEYS = ["time_resolution", "flow_coverage", "nb_suppliers_per_input",
                     "seed", "transport_modes", "use_cargo_types", "capacity_constraint",
                     "weight_localization_firm", "weight_localization_household"]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _fingerprint(config: dict) -> str:
    payload = {k: config.get(k) for k in _FINGERPRINT_KEYS}
    payload["git_sha"] = _git_sha()
    # The input-criticality matrix (Partially-Binding Leontief) changes the built
    # firms, so fold its path + mtime into the fingerprint: swapping/editing it (or
    # this being the first build that loads it) invalidates a stale snapshot.
    crit = (config.get("filepaths") or {}).get("input_criticality")
    payload["input_criticality"] = str(crit) if crit else None
    payload["input_criticality_mtime"] = (
        Path(crit).stat().st_mtime if crit and Path(crit).exists() else None)
    blob = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Build the model once (mirrors disruptsc.run.execute stages 1-4)
# ---------------------------------------------------------------------------
def build_model(config: dict):
    tp, sp, ap, lp = build_params(config)
    fp = config["filepaths"]

    logging.info("Building transport network")
    tn, transport_edges, transport_nodes = build_transport_network(
        config.get("transport_modes", ["roads"]), fp, config.get("logistics", {}),
        sp.time_resolution,
        capacity_overrides=config.get("transport_capacity_overrides"),
        default_transport_capacity=config.get("default_transport_capacity"),
        use_cargo_types=tp.use_cargo_types)

    logging.info("Building agents")
    mrio = load_mrio(fp.get("mrio"), ap.monetary_units_in_data)
    sector_table = load_sector_table(fp.get("sector_table"))
    usd_per_ton = load_usd_per_ton(sector_table)
    selection = filter_sectors(mrio, ap.flow_coverage, ap.sectors_to_include,
                               ap.sectors_to_exclude)
    firm_table = create_firm_table(mrio, sector_table, fp.get("firms_spatial"),
                                   fp.get("households_spatial"), usd_per_ton,
                                   transport_nodes, ap, selection)
    firms = create_firms(firm_table, ap)
    load_tech_coefs(firms, mrio, selection)
    # Partially-Binding Leontief: load the IHS-Markit input-criticality matrix when
    # configured (mirrors disruptsc.run.execute; without it firms fall back to strict
    # Leontief, which would diverge from run_single_event's native run).
    crit_path = fp.get("input_criticality")
    if crit_path and Path(crit_path).exists():
        load_input_criticality(firms, pd.read_csv(crit_path, index_col=0))
        logging.info(f"Loaded input_criticality from {crit_path}")
    load_inventories(firms, ap.inventory_duration_targets, sp.time_resolution, sector_table)
    household_table, consumption = create_household_table(
        mrio, fp.get("households_spatial"), transport_nodes, selection, ap,
        time_resolution=sp.time_resolution)
    households = create_households(household_table, consumption)
    configure_household_inventories(households, ap.enable_household_inventories,
                                    ap.inventory_duration_targets,
                                    ap.inventory_restoration_time, sp.time_resolution,
                                    sector_table)
    countries = create_countries(mrio, transport_nodes, fp.get("countries_spatial"),
                                 usd_per_ton, sp.time_resolution, ap, selection,
                                 transport_edges=transport_edges,
                                 countries_no_transport=tp.countries_no_transport)

    logging.info("Building supply-chain network")
    if sp.seed is not None:
        random.seed(sp.seed)
        np.random.seed(sp.seed)
    cargo_map = lp.sector_to_cargo_type if tp.use_cargo_types else {"default": "any"}
    sc = build_supply_chain_network(firms, households, countries, mrio, sector_table,
                                    ap.nb_suppliers_per_input, ap.weight_localization_firm,
                                    ap.weight_localization_household, cargo_map, tn)

    used_cargo = {getattr(d["object"], "cargo_type", None)
                  for _, _, d in sc.edges(data=True)}
    used_cargo.discard(None); used_cargo.discard("")
    if used_cargo:
        tn.shrink_cargo_types_to(used_cargo)

    set_initial_conditions(sc, firms, households, countries, tp, sp)
    if tp.with_transport:
        logging.info("Setting up logistic routes")
        setup_logistic_routes(sc, tn, firms, countries, tp,
                              max_capacity_iterations=config.get("capacity_routing_max_iterations", 10),
                              export_folder=None)

    return dict(sc=sc, tn=tn, firms=firms, households=households, countries=countries,
                transport_edges=transport_edges, tp=tp, sp=sp)


def make_baseline_snapshot(model):
    """Advance the shared t=0 baseline once; return a deep-copyable state dict."""
    all_data, logistics_reports, routing = prepare_disruption_baseline(
        model["sc"], model["tn"], model["firms"], model["households"],
        model["countries"], model["tp"], model["sp"], writers=None)
    return dict(sc=model["sc"], tn=model["tn"], firms=model["firms"],
                households=model["households"], countries=model["countries"],
                transport_edges=model["transport_edges"], tp=model["tp"], sp=model["sp"],
                all_data=all_data, logistics_reports=logistics_reports, routing=routing)


def build_or_load_snapshot(config: dict, snapshot_path: Path, rebuild: bool = False):
    """Load the cached pre-disruption snapshot, or build it (once) and cache it."""
    fp = _fingerprint(config)
    meta_path = snapshot_path.with_suffix(".meta.json")
    if snapshot_path.exists() and meta_path.exists() and not rebuild:
        meta = json.loads(meta_path.read_text())
        if meta.get("fingerprint") == fp:
            t0 = time.time()
            logging.info(f"Loading cached baseline snapshot {snapshot_path.name} …")
            with open(snapshot_path, "rb") as f:
                snap = pickle.load(f)
            logging.info(f"Snapshot loaded in {time.time()-t0:.0f}s (fingerprint {fp})")
            return snap
        logging.warning(f"Snapshot fingerprint {meta.get('fingerprint')} != current {fp}; rebuilding")

    t0 = time.time()
    logging.info("Building TENT model (daily resolution) — this happens once…")
    model = build_model(config)
    snap = make_baseline_snapshot(model)
    logging.info(f"Model built + baseline prepared in {time.time()-t0:.0f}s; caching snapshot…")
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with open(snapshot_path, "wb") as f:
        pickle.dump(snap, f, protocol=pickle.HIGHEST_PROTOCOL)
    meta_path.write_text(json.dumps({"fingerprint": fp, "git_sha": _git_sha(),
                                     "config_keys": {k: config.get(k) for k in _FINGERPRINT_KEYS}},
                                    indent=2))
    logging.info(f"Snapshot cached to {snapshot_path} in {time.time()-t0:.0f}s")
    return snap


# Column on transport_edges carrying the stable flood-scenario id (== xlsx edge_id).
DISRUPTION_ID_COL = "disruption_id"


def build_disruption_id_map(transport_edges) -> dict[int, int] | None:
    """Map flood ``disruption_id`` -> the model's internal edge ``id``.

    The flood table's ``edge_id`` refers to ``disruption_id`` (preserved from the
    gpkg ``fid``), but ``TransportDisruption`` targets the model's row-order
    ``id``. Returns the mapping, or None if the network predates the
    ``disruption_id`` column (then callers fall back to treating edge_id as the
    model id directly).
    """
    if DISRUPTION_ID_COL not in transport_edges.columns:
        return None
    te = transport_edges[[DISRUPTION_ID_COL, "id"]].dropna(subset=[DISRUPTION_ID_COL])
    return {int(d): int(i) for d, i in zip(te[DISRUPTION_ID_COL], te["id"])}


# ---------------------------------------------------------------------------
def run_one_event(snapshot, event, tp, sp, id_map: dict[int, int] | None):
    """Deep-copy the baseline, close flooded edges, run 2 x duration steps.

    *id_map* translates flood disruption_ids to model edge ids. When None (old
    network without a disruption_id column), edge_ids are used as model ids.
    """
    if id_map is None:
        model_ids = list(event.edge_ids)
    else:
        model_ids = [id_map[e] for e in event.edge_ids if e in id_map]
    state = copy.deepcopy(snapshot)
    disruption = TransportDisruption(
        description={eid: 1.0 for eid in model_ids},
        recovery=Recovery(duration=event.duration_steps, shape="threshold"),
        start_time=1)
    t_final = 2 * event.duration_steps          # run exactly twice the recovery time
    all_data, _, _ = continue_disruption_run(
        state["sc"], state["tn"], state["firms"], state["households"], state["countries"],
        tp, sp, disruptions=[disruption], t_start=1, t_final=t_final,
        all_data=state["all_data"], logistics_reports=state["logistics_reports"],
        all_routing_summaries=state["routing"], writers=None)
    losses = summarize_criticality_losses(all_data["household"], all_data["country"])
    return losses, t_final


def _done_keys(out_path: Path) -> set[tuple[int, int]]:
    if not out_path.exists():
        return set()
    done = set()
    with open(out_path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                done.add((int(row["catchment"]), int(row["return_period"])))
            except (KeyError, ValueError):
                continue
    return done


def main():
    ap = argparse.ArgumentParser(description="TENT flood-event loss sweep")
    ap.add_argument("--xlsx", default=str(DEFAULT_XLSX), help="event table path")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output CSV path")
    ap.add_argument("--snapshot", default=str(SNAPSHOT_DEFAULT), help="cached baseline pickle")
    ap.add_argument("--rebuild", action="store_true", help="force rebuild of the snapshot")
    ap.add_argument("--build-only", action="store_true", help="build + cache snapshot, then exit")
    ap.add_argument("--return-periods", type=int, nargs="+", default=None,
                    help="restrict to these return periods (e.g. 100)")
    ap.add_argument("--limit", type=int, default=None, help="run only first N pending events")
    ap.add_argument("--shard", type=int, default=None, help="worker index (0-based)")
    ap.add_argument("--of", type=int, default=None, help="total number of shards")
    ap.add_argument("--flow-coverage", type=float, default=None,
                    help="override MRIO flow_coverage (e.g. 0.8); smaller = faster steps")
    ap.add_argument("--log-level", default="info", choices=["info", "debug"])
    args = ap.parse_args()

    setup_logging(args.log_level)

    config = load_config("TENT")
    # time_resolution comes from the TENT config file (user_defined_TENT.local.yaml):
    # set it to 'day' or 'week' there and BOTH the model step and the day->step
    # duration conversion below follow it. It also feeds the snapshot fingerprint,
    # so switching resolutions auto-invalidates a stale snapshot.
    config["simulation_type"] = "disruption"
    if args.flow_coverage is not None:
        config["flow_coverage"] = args.flow_coverage   # feeds the snapshot fingerprint
    resolution = config.get("time_resolution", "week")
    days_per_step = days_per_timestep(resolution)   # xlsx day-durations -> steps
    logging.info(f"time_resolution={resolution} (days_per_step={days_per_step})")

    snapshot = build_or_load_snapshot(config, Path(args.snapshot), rebuild=args.rebuild)
    # No epsilon early-stop: run the full 2 x duration horizon.
    tp = snapshot["tp"]
    sp = dataclasses.replace(snapshot["sp"], epsilon_stop=0.0)

    # Flood edge_id targets the stable disruption_id; map it to the model's id.
    id_map = build_disruption_id_map(snapshot["transport_edges"])
    if id_map is None:
        logging.warning(f"transport_edges has no '{DISRUPTION_ID_COL}' column — "
                        f"treating flood edge_id as the model's row-order id "
                        f"(rebuild the snapshot from the updated transport.gpkg).")
        valid_ids = set(snapshot["transport_edges"]["id"].tolist())
    else:
        valid_ids = set(id_map)

    if args.build_only:
        logging.info("Snapshot ready (build-only). Exiting.")
        return

    events = load_events(args.xlsx, days_per_step=days_per_step, return_periods=args.return_periods)
    missing = sorted(all_flooded_edge_ids(args.xlsx) - valid_ids)
    if missing:
        logging.warning(f"{len(missing)} flooded {DISRUPTION_ID_COL}(s) absent from the "
                        f"network (e.g. {missing[:10]}) — those edges will be skipped.")

    # Per-shard output so parallel workers never contend on one CSV.
    out_path = Path(args.out)
    if args.shard is not None and args.of:
        events = [e for i, e in enumerate(events) if i % args.of == args.shard]
        out_path = out_path.with_name(f"{out_path.stem}_shard{args.shard}of{args.of}{out_path.suffix}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = _done_keys(out_path)
    pending = [e for e in events if (e.catchment, e.return_period) not in done]
    if args.limit is not None:
        pending = pending[:args.limit]
    logging.info(f"{len(events)} events assigned, {len(done)} done, {len(pending)} to run")

    write_header = not out_path.exists()
    with open(out_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        for i, ev in enumerate(pending, 1):
            logging.disable(logging.INFO)
            t_ev = time.time()
            losses, t_final = run_one_event(snapshot, ev, tp, sp, id_map)
            dt = time.time() - t_ev
            logging.disable(logging.NOTSET)
            writer.writerow({
                "catchment": ev.catchment, "return_period": ev.return_period,
                "n_edges": len(ev.edge_ids), "duration_days": round(ev.duration_days, 3),
                "duration_steps": ev.duration_steps, "t_final": t_final,
                "household_loss": losses["total_household_loss"],
                "country_loss": losses["country_loss"], "wall_seconds": round(dt, 1)})
            f.flush()
            logging.info(f"[{i}/{len(pending)}] {ev.key}: "
                         f"hh={losses['total_household_loss']:,.1f} "
                         f"country={losses['country_loss']:,.1f} "
                         f"(dur={ev.duration_steps}d, t_final={t_final}, {dt:.1f}s)")
    logging.info(f"Done → {out_path}")


if __name__ == "__main__":
    main()
