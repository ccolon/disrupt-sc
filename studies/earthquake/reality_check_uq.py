"""Three-way comparison of public-reconstruction mechanics vs UQ's MMI-bin DiD.

Real treatment: canton_mmi_bin.csv (control / bin_56 / bin_67 / bin_7p). Metrics
exclude ISIC K (FIN, SEG) and O (ADP) firms to match UQ's bilateral filter (exact
for the ACUTE window; the private<->ADP ripple only bites in recovery).

Variants (all: util=0.8, tau=15d, EQUAL rationing, CON-local private recon, 180d):
  A-external   : 80% public rebuilt externally (black box, no footprint) + 20% private CON/MAN
  B-prod-ADP   : reconstruction routed through the ADP sector (produced, ripples to services,
                 capacity-limited); ADP excluded from metric
  B-financier  : government-financed construction (CON/MAN produce), gov-facing reconstruction
                 sales excluded from the metric (ripple lands on construction)

Compare acute (months 1-2 = tau 0,1) sales/purchases DiD (bin_7p - control) to UQ
(acute sales -9.6, purchases -14.3); recovery shown as a consistency check only.

Run:  python studies/earthquake/reality_check_uq.py
"""
from __future__ import annotations

import dataclasses
import logging
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

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

CROSSWALK = {
    "A": {"BNA","CAN","CER","FRT","FRV","GAN","PES","SIL"},
    "C": {"AYG","AZU","BAL","CAR","CAU","CEM","CHO","CIN","CUE","HIL","LAC","MAD","MAN","MAQ",
          "MET","MOL","MUE","PAN","PAP","PLS","QU1","QU2","TAB","VES","VID","REF","ALD"},
    "DE": {"ELE","AGU"}, "F": {"CON"}, "G": {"COM"}, "H": {"TRA"}, "I": {"HOT","RES"},
    "K": {"FIN","SEG"}, "O": {"ADP"},
}
SEC2ISIC = {s: g for g, ss in CROSSWALK.items() for s in ss}
def isic(sec): return SEC2ISIC.get(sec, "J-U")
EXCLUDED = {"FIN", "SEG", "ADP"}                       # ISIC K + O, dropped from metrics (as in UQ)

# real canton -> MMI bin
cbin = pd.read_csv(ROOT / "studies/earthquake/_shock/canton_mmi_bin.csv")
CANTON_BIN = dict(zip(cbin.subregion_canton, cbin.mmi_bin))

# ---- build once -----------------------------------------------------------
setup_logging("info")
cfg = load_config("EcuadorEQ")
cfg["t_final"] = 13
cfg["rationing_mode"] = "equal"
cfg["utilization_rate"] = 0.8
tp, sp, ap, lp = build_params(cfg)
sp = dataclasses.replace(sp, time_to_activate_idle_capital=15)
fp = cfg["filepaths"]
disr = cfg["disruptions"][0]
print(f"BUILD: monthly t_final={sp.t_final} util=0.8 tau=15d nb_supp={ap.nb_suppliers_per_input} rationing=equal")

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

BIN = {}; FISIC = {}; INCL = {}; nADP = 0
for pid, f in firms.items():
    BIN[pid] = CANTON_BIN.get((f.subregions or {}).get("subregion_canton"), "control")
    FISIC[pid] = isic(f.sector)
    INCL[pid] = f.sector not in EXCLUDED
    if f.sector == "ADP": nADP += 1
from collections import Counter
print(f"firms: {len(firms)}  bins={dict(Counter(BIN.values()))}  ADP firms={nADP}  "
      f"excluded firms={sum(1 for v in INCL.values() if not v)}\n")

# ---- trace ----------------------------------------------------------------
TRAJ: list = []
_orig = S._run_one_time_step
def traced(time_step, *a, **k):
    r = _orig(time_step, *a, **k)
    fs = a[3]
    prod = defaultdict(float); inp = defaultdict(float); rec = defaultdict(float)
    prod_si = defaultdict(float)
    for pid, f in fs.items():
        if not INCL[pid]:
            continue
        b = BIN[pid]
        prod[b] += f.production; inp[b] += f.total_input; rec[b] += f.reconstruction_produced
        prod_si[(b, FISIC[pid])] += f.production
    TRAJ.append((time_step, dict(prod), dict(inp), dict(rec), dict(prod_si)))
    return r
S._run_one_time_step = traced

ACUTE = [1, 2]; RECOV = list(range(3, 14)); BINS = ["control", "bin_56", "bin_67", "bin_7p"]
def _wpct(traj, key_fn, months):
    b0 = key_fn(traj[0])
    if b0 <= 1e-9: return float("nan")
    return float(np.mean([100.0 * (key_fn(traj[m]) / b0 - 1.0) for m in months]))

def run_variant(label, mix, public_share, recon_excl):
    for f in firms.values():
        f.utilization_rate = 0.8
    TRAJ.clear()
    d = dict(disr)
    d.update(reconstruction_market=True, capital_input_mix=mix, reconstruction_public_share=public_share,
             reconstruction_locality={"CON": 0.8}, reconstruction_region_key="subregion_canton",
             reconstruction_target_time=180)
    logging.disable(logging.INFO)
    run_disruption(sc, tn, firms, households, countries, tp, sp, [d], te, firm_table, sp.t_final, export_folder=None)
    logging.disable(logging.NOTSET)
    traj = list(TRAJ)
    # sales = production (minus gov-facing reconstruction if recon_excl); purchases = total_input
    def sales(row, b): return row[1].get(b, 0.0) - (row[3].get(b, 0.0) if recon_excl else 0.0)
    def purch(row, b): return row[2].get(b, 0.0)
    def did(fn, months): return _wpct(traj, lambda r: fn(r, "bin_7p"), months) - _wpct(traj, lambda r: fn(r, "control"), months)
    res = {"s_ac": did(sales, ACUTE), "s_rec": did(sales, RECOV),
           "p_ac": did(purch, ACUTE), "p_rec": did(purch, RECOV)}
    for b in BINS:                                    # per-bin acute sales (gradient)
        res[("grad", b)] = _wpct(traj, lambda r, b=b: sales(r, b), ACUTE)
    for ig in ("F", "G", "I", "C"):                   # sector acute DiD (bin_7p - control)
        res[("sec", ig)] = (_wpct(traj, lambda r, ig=ig: r[4].get(("bin_7p", ig), 0.0), ACUTE)
                            - _wpct(traj, lambda r, ig=ig: r[4].get(("control", ig), 0.0), ACUTE))
    print(f"  ran {label}")
    return res

VARIANTS = [
    ("A-external",  {"CON": 0.7, "MAN": 0.2, "IMP": 0.1},               0.8, False),
    ("B-prod-ADP",  {"ADP": 0.8, "CON": 0.14, "MAN": 0.04, "IMP": 0.02}, 0.0, False),
    ("B-financier", {"CON": 0.7, "MAN": 0.2, "IMP": 0.1},               0.0, True),
]
print("RUNNING 3 variants ...")
R = {lab: run_variant(lab, mix, ps, rx) for lab, mix, ps, rx in VARIANTS}
labs = [v[0] for v in VARIANTS]

print("\n==== MMI>7 DiD (bin_7p - control), ISIC K+O excluded ====")
print(f"{'outcome':>10} {'window':>8} | {'UQ':>6} | " + "  ".join(f"{l:>12}" for l in labs))
UQ = {("sales","acute"):-9.6, ("sales","recovery"):10.8, ("purchases","acute"):-14.3, ("purchases","recovery"):5.7}
for oc, key in [("sales","s"), ("purchases","p")]:
    for w in ("acute", "recovery"):
        cells = "  ".join(f"{R[l][key+'_'+('ac' if w=='acute' else 'rec')]:>11.1f}%" for l in labs)
        tag = "" if w == "acute" else "  (policy gap)"
        print(f"{oc:>10} {w:>8} | {UQ[(oc,w)]:>5.1f}% | {cells}{tag}")

print("\n==== spatial gradient — acute sales %change by MMI bin (should steepen control->7p) ====")
print(f"{'bin':>8} | " + "  ".join(f"{l:>12}" for l in labs))
for b in BINS:
    print(f"{b:>8} | " + "  ".join(f"{R[l][('grad',b)]:>11.1f}%" for l in labs))

print("\n==== sector acute DiD (bin_7p - control), sales — UQ tau0 in comment ====")
print(f"{'sector':>10} | " + "  ".join(f"{l:>12}" for l in labs))
for ig, name in (("F","Construct"), ("G","Trade"), ("I","Accommod"), ("C","Manuf")):
    print(f"{name:>10} | " + "  ".join(f"{R[l][('sec',ig)]:>11.1f}%" for l in labs))
print("UQ acute sales tau0: F -14.7 | G -11.7 | I -14.2 | C -14.9")
