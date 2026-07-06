"""Validate the cached snapshot: confirm flooded edges bite, losses are non-zero
on flow-exposed events, and measure real per-event wall time at 2x duration.
Prints directly (no pipe buffering). Run: python studies/TENT/validate.py --xlsx <path>
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, setup_logging
from studies.TENT.run_sweep import build_or_load_snapshot, run_one_event, SNAPSHOT_DEFAULT
from studies.TENT.events import load_events
import dataclasses, logging

ap = argparse.ArgumentParser()
ap.add_argument("--xlsx", required=True)
ap.add_argument("--n", type=int, default=3, help="how many top-exposed events to run")
args = ap.parse_args()
setup_logging("info")

config = load_config("TENT"); config["time_resolution"] = "day"; config["simulation_type"] = "disruption"
snap = build_or_load_snapshot(config, SNAPSHOT_DEFAULT)
tp = snap["tp"]; sp = dataclasses.replace(snap["sp"], epsilon_stop=0.0)

events = load_events(args.xlsx, days_per_step=1.0)
flow0 = {r["id"]: float(r.get("flow_total_tons") or 0.0)
         for r in snap["all_data"]["transport_flow"] if r.get("time_step") == 0}
def exposure(ev): return sum(flow0.get(e, 0.0) for e in ev.edge_ids)
ranked = sorted(events, key=exposure, reverse=True)

print(f"\nbaseline edges with flow: {sum(1 for v in flow0.values() if v>0)} / {len(flow0)}")
print("Top exposed events:")
for ev in ranked[:args.n]:
    print(f"  {ev.key}: {len(ev.edge_ids)} edges dur={ev.duration_steps}d exposure={exposure(ev):,.0f} tons")

logging.disable(logging.INFO)
print("\nRunning events (2x duration, no epsilon):")
probe = ranked[:args.n] + [e for e in events if e.key == "c0_rp10"]
for ev in probe:
    t0 = time.time()
    losses, t_final = run_one_event(snap, ev, tp, sp)
    dt = time.time() - t0
    print(f"  {ev.key}: dur={ev.duration_steps}d t_final={t_final} "
          f"hh_loss={losses['total_household_loss']:,.3f} country={losses['country_loss']:,.3f} "
          f"exposure={exposure(ev):,.0f}  wall={dt:.1f}s ({dt/t_final:.1f}s/step)")
