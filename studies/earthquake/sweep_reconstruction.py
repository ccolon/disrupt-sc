"""Coarse sweep of reconstruction_target_time on the EcuadorEQ shock.

Builds the model ONCE (target_time affects only the disruption + loop, not the
supply-chain build), then re-runs the disruption for each target value, resetting
firm disruption state between runs. Reports household/country loss and the
capital-driven capacity trajectory (trough, end, % of capital rebuilt).

Run:  python studies/earthquake/sweep_reconstruction.py
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
print(f"BUILD: time_res={sp.time_resolution} t_final={sp.t_final} nb_supp={ap.nb_suppliers_per_input} "
      f"adaptive={sp.adaptive_supplier_weight} flow_cov={ap.flow_coverage} start_time={cfg['disruptions'][0]['start_time']}")

# ---------------- build once ----------------
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

# ---------------- per-step capacity trajectory capture ----------------
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

base = dict(type="capital_destruction", description_type="subregion_file",
            file=cfg["disruptions"][0]["file"], unit="mUSD", start_time=1,
            capital_input_mix={"CON": 0.7, "MAN": 0.2, "IMP": 0.1})

SWEEP = [("no-recon", None), ("90d", 90), ("180d", 180), ("365d", 365), ("730d", 730), ("1825d", 1825)]

logging.disable(logging.INFO)  # quiet the per-step logs during the sweep
print("\n==== reconstruction_target_time sweep (monthly steps, t_final=12 = 1 year, shock at month 1) ====")
print(f"{'target':>9} | {'hh_loss':>9} {'ctry_loss':>9} | {'cap@trough':>10} {'cap@end':>8} | {'%capital_rebuilt':>16} | cap_ratio path (m1..m12)")
for label, tt in SWEEP:
    reset_disruption_state(firms)
    TRAJ.clear()
    d = dict(base)
    d["reconstruction_market"] = tt is not None
    if tt is not None:
        d["reconstruction_target_time"] = tt
    all_data = run_disruption(sc, tn, firms, households, countries, tp, sp, [d], te, firm_table, sp.t_final,
                              export_folder=None)
    L = export_summary(all_data["household"], all_data["country"], household_table, tp.monetary_units, export_folder=None)
    caps = [t[2] for t in TRAJ]
    cds = [t[1] for t in TRAJ]
    cd0 = max(cds) if cds else 0.0
    pct = 100 * (cd0 - cds[-1]) / cd0 if cd0 > 0 else 0.0
    path = " ".join(f"{c:.2f}" for c in caps[1:])  # from shock month onward
    print(f"{label:>9} | {L['household_loss']:>9,.0f} {L['country_loss']:>9,.0f} | "
          f"{min(caps):>10.4f} {caps[-1]:>8.4f} | {pct:>15.1f}% | {path}")
