"""Coarse sweep of utilization_rate on the EcuadorEQ shock (reconstruction @ 730 d).

utilization_rate sets the spare-capacity head-room: production_capacity = eq / util.
It governs (a) how hard small capital shocks bite, and (b) whether CON/MAN firms
have head-room to produce reconstruction goods without rationing their normal
clients. Builds the model ONCE (topology is util-independent), then for each util
runs both no-reconstruction and reconstruction-730 d, resetting state between runs.

Run:  python studies/earthquake/sweep_utilization.py
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
from disruptsc.run_pipeline.export import export_summary                       # noqa: E402

setup_logging("info")
cfg = load_config("EcuadorEQ")
tp, sp, ap, lp = build_params(cfg)
fp = cfg["filepaths"]
disr_cfg = cfg["disruptions"][0]
print(f"BUILD: time_res={sp.time_resolution} t_final={sp.t_final} nb_supp={ap.nb_suppliers_per_input} "
      f"flow_cov={ap.flow_coverage} start_time={disr_cfg['start_time']} "
      f"recon_target={disr_cfg.get('reconstruction_target_time')}d (= {disr_cfg.get('reconstruction_target_time')/30:.1f} months)")

# ---------------- build once (topology independent of utilization_rate) ----------------
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

# ---------------- capacity trajectory capture ----------------
TRAJ = []
_orig = S._run_one_time_step
def traced(time_step, *a, **k):
    r = _orig(time_step, *a, **k)
    fs = a[3]
    cd = sum(getattr(f, "capital_destroyed", 0.0) or 0.0 for f in fs.values())
    cc = sum(f.current_production_capacity for f in fs.values())
    ec = sum(f.eq_production_capacity for f in fs.values())
    TRAJ.append((time_step, cd, cc / ec if ec else 0.0))
    return r
S._run_one_time_step = traced

def reset_disruption_state(fs):
    for f in fs.values():
        f.capital_destroyed = 0.0
        f.reconstruction_demand = 0.0
        f.reconstruction_produced = 0.0
        f.capital_demanded = 0.0
        f.production_capacity_reduction = 0.0
        f.remaining_disrupted_time = 0.0

def run_once(recon: bool):
    reset_disruption_state(firms)
    TRAJ.clear()
    d = dict(disr_cfg)
    d["reconstruction_market"] = recon
    all_data = run_disruption(sc, tn, firms, households, countries, tp, sp, [d], te, firm_table, sp.t_final,
                              export_folder=None)
    L = export_summary(all_data["household"], all_data["country"], household_table, tp.monetary_units, export_folder=None)
    caps = [t[2] for t in TRAJ]
    cds = [t[1] for t in TRAJ]
    cd0 = max(cds) if cds else 0.0
    pct = 100 * (cd0 - cds[-1]) / cd0 if cd0 > 0 else 0.0
    return L["household_loss"], L["country_loss"], min(caps), caps[-1], pct

SWEEP = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
logging.disable(logging.INFO)
print("\n==== utilization_rate sweep (monthly, t_final=12 = 1 yr, shock month 1, reconstruction @ 730 d) ====")
print(f"{'util':>5} | {'hh_noRecon':>10} {'hh_recon730':>11} {'recon_delta':>11} | {'cap@trough':>10} {'cap@end':>8} {'%rebuilt':>8}")
for util in SWEEP:
    for f in firms.values():
        f.utilization_rate = util
    hh_nr, _, _, _, _ = run_once(recon=False)
    hh_r, ctry_r, trough, end, pct = run_once(recon=True)
    delta = hh_r - hh_nr
    print(f"{util:>5.2f} | {hh_nr:>10,.0f} {hh_r:>11,.0f} {delta:>+11,.0f} | {trough:>10.4f} {end:>8.4f} {pct:>7.1f}%")
