"""One-at-a-time (OAT) sensitivity analysis on the c63_r500 flood event.

Baseline = current user_defined_TENT.local.yaml. For each parameter, vary one
value at a time (holding the rest at baseline), rebuild the model, run the event
(full closure, t_final = 2 x duration, no epsilon), and report:

  - household_loss           cumulative household loss (mUSD), summarize_criticality_losses
  - dVA                      cumulative value-added change vs equilibrium (mUSD):
                             VA_t = sum_firms(production - total_input); dVA = sum_t (VA_t - VA_0)
                             (negative = value-added lost over the horizon)
  - dVA_pct                  dVA / (VA_0 * horizon) * 100

Each knob (flow_coverage, time_resolution, nb_suppliers_per_input,
critical_input_threshold, price_increase_threshold) changes the build, so every
point is a fresh build (no snapshot reuse). Runs in-process with writers=None
(no CSV export). Event edges are targeted via disruption_id.

Run:  python studies/TENT/sensitivity_c63_r500.py
"""
from __future__ import annotations

import copy
import dataclasses
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.setrecursionlimit(50000)

import pandas as pd  # noqa: E402

from disruptsc.config import load_config, setup_logging, days_per_timestep   # noqa: E402
from disruptsc.run_pipeline.simulate import (                                 # noqa: E402
    prepare_disruption_baseline, continue_disruption_run)
from disruptsc.run_pipeline.disruption import TransportDisruption, Recovery   # noqa: E402
from disruptsc.run_pipeline.export import summarize_criticality_losses        # noqa: E402

from studies.TENT.run_sweep import build_model, build_disruption_id_map       # noqa: E402
from studies.TENT.events import load_events, DEFAULT_XLSX                      # noqa: E402

CATCHMENT, RETURN_PERIOD = 63, 500
OUT_CSV = ROOT / "runs" / "TENT" / "sensitivity_c63_r500.csv"

# OAT grid. Baseline value of each is taken from the loaded config.
GRID = {
    "flow_coverage": [0.6, 0.8, 0.9, 1.0],
    "time_resolution": ["week", "day"],
    "nb_suppliers_per_input": [1, 2, 4],
    "critical_input_threshold": [0, 0.01, 0.02, 0.05],
    "price_increase_threshold": [2, 5, 10],
}


def _value_added(firms) -> float:
    """Aggregate per-step value added = production - intermediate consumption."""
    return sum(f.production for f in firms.values()) - sum(f.total_input for f in firms.values())


def run_config(config: dict) -> dict:
    """Build the model for *config* and run c63_r500; return metrics."""
    model = build_model(config)
    sc, tn = model["sc"], model["tn"]
    firms, hh, co = model["firms"], model["households"], model["countries"]
    tp = model["tp"]
    sp = dataclasses.replace(model["sp"], epsilon_stop=0.0)   # no early stop

    resolution = config.get("time_resolution", "week")
    dps = days_per_timestep(resolution)
    ev = next(e for e in load_events(DEFAULT_XLSX, days_per_step=dps,
                                     return_periods=[RETURN_PERIOD])
              if e.catchment == CATCHMENT)
    id_map = build_disruption_id_map(model["transport_edges"])
    model_ids = ([id_map[e] for e in ev.edge_ids if e in id_map]
                 if id_map else list(ev.edge_ids))

    all_data, logistics, routing = prepare_disruption_baseline(
        sc, tn, firms, hh, co, tp, sp, writers=None)
    va0 = _value_added(firms)                       # equilibrium value added
    disruption = TransportDisruption(
        description={e: 1.0 for e in model_ids},
        recovery=Recovery(duration=ev.duration_steps, shape="threshold"), start_time=1)

    t_final = 2 * ev.duration_steps
    dva = 0.0
    for t in range(1, t_final + 1):
        continue_disruption_run(sc, tn, firms, hh, co, tp, sp,
                                disruptions=[disruption], t_start=t, t_final=t,
                                all_data=all_data, logistics_reports=logistics,
                                all_routing_summaries=routing, writers=None)
        dva += _value_added(firms) - va0            # cumulative VA change (<0 = loss)

    losses = summarize_criticality_losses(all_data["household"], all_data["country"])
    return {
        "household_loss": losses["total_household_loss"],
        "country_loss": losses["country_loss"],
        "dVA": dva,
        "dVA_pct": (dva / (va0 * t_final) * 100.0) if va0 and t_final else float("nan"),
        "VA0": va0, "t_final": t_final, "duration_steps": ev.duration_steps,
        "resolution": resolution, "n_firms": len(firms),
    }


def main():
    setup_logging("info")
    base = load_config("TENT")
    base["simulation_type"] = "disruption"
    baseline_vals = {p: base.get(p) for p in GRID}
    logging.info(f"Baseline: {baseline_vals}")

    # Build the run list: baseline once + each off-baseline value.
    runs = [("baseline", None, dict(base))]
    for param, values in GRID.items():
        for v in values:
            if v == baseline_vals[param]:
                continue
            cfg = copy.deepcopy(base)
            cfg[param] = v
            runs.append((param, v, cfg))

    logging.info(f"{len(runs)} runs planned (1 baseline + {len(runs)-1} off-baseline)")
    results = {}
    for i, (param, v, cfg) in enumerate(runs):
        label = "baseline" if param == "baseline" else f"{param}={v}"
        logging.disable(logging.INFO)
        t0 = time.time()
        try:
            res = run_config(cfg)
            res["error"] = ""
        except Exception as exc:  # noqa: BLE001
            res = {"error": repr(exc)}
        logging.disable(logging.NOTSET)
        res["seconds"] = round(time.time() - t0, 1)
        key = "baseline" if param == "baseline" else (param, v)
        results[key] = res
        logging.info(f"[{i+1}/{len(runs)}] {label}: "
                     f"hh_loss={res.get('household_loss', float('nan')):,.2f} "
                     f"dVA={res.get('dVA', float('nan')):,.2f} "
                     f"({res.get('dVA_pct', float('nan')):+.2f}%) "
                     f"[{res['seconds']}s]{' ERROR '+res['error'] if res.get('error') else ''}")

    # ---- assemble a tidy table: one row per (param, value), baseline marked ----
    b = results["baseline"]
    rows = []
    for param, values in GRID.items():
        for v in values:
            is_base = (v == baseline_vals[param])
            r = b if is_base else results.get((param, v), {})
            rows.append({
                "parameter": param, "value": v,
                "baseline": "*" if is_base else "",
                "household_loss": r.get("household_loss"),
                "dVA": r.get("dVA"), "dVA_pct": r.get("dVA_pct"),
                "VA0": r.get("VA0"), "t_final": r.get("t_final"),
                "resolution": r.get("resolution"), "n_firms": r.get("n_firms"),
                "seconds": r.get("seconds"), "error": r.get("error", ""),
            })
    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print(f"\n=== OAT sensitivity: c{CATCHMENT}_r{RETURN_PERIOD} "
          f"(baseline hh_loss={b.get('household_loss', float('nan')):,.2f}, "
          f"VA0={b.get('VA0', float('nan')):,.1f} mUSD/step) ===")
    print(df[["parameter", "value", "baseline", "household_loss", "dVA", "dVA_pct",
              "t_final", "n_firms", "seconds"]].to_string(index=False))
    print(f"\nSaved: {OUT_CSV}")


if __name__ == "__main__":
    main()
