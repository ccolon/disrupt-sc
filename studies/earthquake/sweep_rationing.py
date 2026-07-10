"""Compare rationing_mode = 'equal' vs 'household_first' over 48 months.

Same build, reconstruction on (target from config), util from config. rationing_mode
only changes how a firm splits scarce output between household and firm clients,
so we build once and run both modes in one process (clean within-build compare).

Run:  python studies/earthquake/sweep_rationing.py
"""
from __future__ import annotations

import logging
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, build_params, setup_logging          # noqa: E402
from disruptsc.init_pipeline.transport import build_transport_network          # noqa: E402
from disruptsc.init_pipeline.load_data import (                                # noqa: E402
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors)
from disruptsc.init_pipeline.agents import (                                   # noqa: E402
    create_firm_table, create_firms, load_tech_coefs, load_inventories,
    configure_household_inventories, create_household_table, create_households,
    create_countries)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network    # noqa: E402
import disruptsc.run_pipeline.simulate as S                                    # noqa: E402
from disruptsc.run_pipeline.simulate import run_disruption                     # noqa: E402

setup_logging("info")
cfg = load_config("EcuadorEQ")
cfg["t_final"] = 48
tp, sp, ap, lp = build_params(cfg)
fp = cfg["filepaths"]
disr_cfg = cfg["disruptions"][0]
tp_equal = build_params({**cfg, "rationing_mode": "equal"})[0]
tp_hh = build_params({**cfg, "rationing_mode": "household_first"})[0]
print(f"BUILD: util={ap.utilization_rate} recon_target={disr_cfg.get('reconstruction_target_time')}d "
      f"recon={disr_cfg.get('reconstruction_market')} t_final={sp.t_final}")

# build once (rationing_mode does not affect the build)
tn, te, tnodes = build_transport_network(
    cfg.get("transport_modes", ["roads"]), fp, cfg.get("logistics", {}), sp.time_resolution,
    capacity_overrides=cfg.get("transport_capacity_overrides"),
    default_transport_capacity=cfg.get("default_transport_capacity"), use_cargo_types=tp.use_cargo_types)
mrio = load_mrio(fp.get("mrio"), ap.monetary_units_in_data)
sector_table = load_sector_table(fp.get("sector_table"))
usd_per_ton = load_usd_per_ton(sector_table)
selection = filter_sectors(mrio, ap.flow_coverage, ap.sectors_to_include, ap.sectors_to_exclude)
firm_table = create_firm_table(mrio, sector_table, fp.get("firms_spatial"), fp.get("households_spatial"),
                               usd_per_ton, tnodes, ap, selection)
firms = create_firms(firm_table, ap)
load_tech_coefs(firms, mrio, selection)
load_inventories(firms, ap.inventory_duration_targets, sp.time_resolution, sector_table)
household_table, consumption = create_household_table(mrio, fp.get("households_spatial"), tnodes, selection, ap,
                                                      time_resolution=sp.time_resolution)
households = create_households(household_table, consumption)
configure_household_inventories(households, ap.enable_household_inventories, ap.inventory_duration_targets,
                                ap.inventory_restoration_time, sp.time_resolution, sector_table)
countries = create_countries(mrio, tnodes, fp.get("countries_spatial"), usd_per_ton, sp.time_resolution, ap, selection,
                             transport_edges=te, countries_no_transport=tp.countries_no_transport)
if sp.seed is not None:
    random.seed(sp.seed); np.random.seed(sp.seed)
cargo_map = lp.sector_to_cargo_type if tp.use_cargo_types else {"default": "any"}
sc = build_supply_chain_network(firms, households, countries, mrio, sector_table, ap.nb_suppliers_per_input,
                                ap.weight_localization_firm, ap.weight_localization_household, cargo_map, tn)

TRAJ = []
_orig = S._run_one_time_step
def traced(time_step, *a, **k):
    r = _orig(time_step, *a, **k)
    fs, hh, co = a[3], a[4], a[5]
    cd = sum(getattr(f, "capital_destroyed", 0.0) or 0.0 for f in fs.values())
    hl = sum((h.consumption_loss or 0.0) + (h.extra_spending or 0.0) for h in hh.values())
    cl = sum((c.consumption_loss or 0.0) + (c.extra_spending or 0.0) for c in co.values())
    TRAJ.append((time_step, cd, hl, cl))
    return r
S._run_one_time_step = traced

def reset_disruption_state(fs):
    for f in fs.values():
        f.capital_destroyed = 0.0; f.reconstruction_demand = 0.0; f.reconstruction_produced = 0.0
        f.capital_demanded = 0.0; f.production_capacity_reduction = 0.0; f.remaining_disrupted_time = 0.0

def run(tp_x):
    reset_disruption_state(firms)
    TRAJ.clear()
    d = dict(disr_cfg)
    run_disruption(sc, tn, firms, households, countries, tp_x, sp, [d], te, firm_table, sp.t_final, export_folder=None)
    return list(TRAJ)

logging.disable(logging.INFO)
eq = run(tp_equal)
hf = run(tp_hh)

print("\n==== rationing_mode: equal vs household_first (util 0.8, recon 730d, 48 months) ====")
print(f"{'month':>5} | {'hh_loss/step':>22} | {'country_loss/step':>22} | {'cap_destroyed':>16}")
print(f"{'':>5} | {'equal':>10} {'hh_first':>11} | {'equal':>10} {'hh_first':>11} | {'equal':>7} {'hh_first':>8}")
for i in range(len(eq)):
    t = eq[i][0]
    if t == 0 or t % 3 == 0 or t == eq[-1][0]:
        print(f"{t:>5} | {eq[i][2]:>10,.0f} {hf[i][2]:>11,.0f} | {eq[i][3]:>10,.0f} {hf[i][3]:>11,.0f} | "
              f"{eq[i][1]:>7,.0f} {hf[i][1]:>8,.0f}")
hh_eq = sum(s[2] for s in eq); hh_hf = sum(s[2] for s in hf)
co_eq = sum(s[3] for s in eq); co_hf = sum(s[3] for s in hf)
print(f"\nCUMULATIVE over 48 months:")
print(f"  household loss:  equal={hh_eq:,.0f}   household_first={hh_hf:,.0f}   delta={hh_hf-hh_eq:+,.0f} ({100*(hh_hf-hh_eq)/hh_eq:+.1f}%)")
print(f"  country  loss:   equal={co_eq:,.0f}   household_first={co_hf:,.0f}   delta={co_hf-co_eq:+,.0f} ({100*(co_hf-co_eq)/co_eq:+.1f}%)")
