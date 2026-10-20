# -*- coding: utf-8 -*-
"""CESTRIN 2022 road-level truck-AADT validation of the Romania model flows.

CESTRIN publishes the 2022 census as ROAD-level averages (224 'drum' rows,
each the length-weighted mean AADT over the censused road - the 'ansamblu'
FeatureServer layer; raw CSV committed at
Transport/sources/cestrin_mza2022_roads.csv). The comparison therefore runs
at that same level (user decision, manifest p30 cestrin entry):

  model road average  = sum(edge weekly tons x edge km) / sum(edge km)
                        over all model edges whose OSM ref maps to the drum
  observed            = trucks AADT = autocamioane 2-axle + 3/4-axle +
                        articulated/TIR + truck-with-trailer classes
                        (vans <5t, tractors, buses excluded)

RANK / RATIO basis (user decision, 20 Oct 2026): absolute tons-per-truck is
NOT assumed. Reported instead:
  * Spearman rank correlation of road averages (model tons vs trucks AADT)
  * share ratio per road: (model truck-km share) / (observed truck-km share)
    within the matched set, each side on its own length basis - immune to a
    uniform payload/coverage factor
  * the implied payload (model tkm / observed truck-km) as a sanity number,
    not a target

Caveats (printed with the table):
  * NETWORK VINTAGE: CESTRIN censused the 2022 network; the model runs on
    the current one. Roads whose traffic moved to a motorway/expressway
    opened since (DEx12 vs DN65, A7 vs DN2, A0 vs the Bucharest ring VCB)
    are compared as CORRIDOR sums (groups below), never individually.
  * the model skeleton covers each road partially (coverage column =
    model km / censused km); CESTRIN averages the WHOLE road incl.
    low-traffic tails -> partial coverage biases the model average up
  * model flows are scope freight only; CESTRIN counts all trucks incl.
    empties and out-of-scope traffic - absorbed by the share/rank basis
  * 'Centura'/variant rows (VCB etc.) have no OSM DN/A ref -> unmatched
    (except VCB, folded into the Bucharest-ring corridor group)

Usage: python romania_cestrin_validation.py [--run RUN_ID] [--min-km 20]
       [--min-trucks 500]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DATA = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc-data\Romania")
CESTRIN = DATA / "Transport" / "sources" / "cestrin_mza2022_roads.csv"
TRUCK_COLS = ["autocamioane_derivate_2_axe", "autocamioane_derivate_3_4_axe",
              "autovehicule_articulate_tir_alt", "autocamioane_derivate_mtma__3_5"]
TOKEN = re.compile(r"^(A\d+|DEX\d+[A-Z]?|DN\d+[A-Z]?|DNCB)$")
PRIORITY = {"A": 0, "DEX": 1, "DN": 2}

# post-2022 motorway/expressway openings: the censused road and its new
# bypass are one corridor (model key -> group; obs 'drum' key -> group)
CORRIDOR = {"DN65": "DN65+DEx12", "DEX12": "DN65+DEx12",
            "DN2": "DN2+A7", "A7": "DN2+A7",
            "A0": "Bucharest ring", "DNCB": "Bucharest ring"}
OBS_CORRIDOR = {"DN65": "DN65+DEx12", "DN2": "DN2+A7",
                "VCB(CENTURABUCURESTI)": "Bucharest ring"}


def road_of(ref: str) -> str | None:
    """Best road token of an edge's (possibly chained) OSM ref."""
    best = None
    for tok in str(ref).replace(",", ";").split(";"):
        t = tok.strip().upper().replace(" ", "")
        m = TOKEN.match(t)
        if not m:
            continue
        cls = "DEX" if t.startswith("DEX") else ("A" if t[0] == "A" else "DN")
        if best is None or PRIORITY[cls] < PRIORITY[best[0]]:
            best = (cls, t)
    return best[1] if best else None


def latest_run() -> str:
    runs = sorted(d.name for d in (REPO / "output" / "Romania").iterdir()
                  if re.match(r"^\d{8}_\d{6}$", d.name))
    return runs[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None)
    ap.add_argument("--min-km", type=float, default=20.0,
                    help="min censused km for a road to be a TARGET")
    ap.add_argument("--min-trucks", type=float, default=500.0,
                    help="min observed trucks AADT for a TARGET")
    args = ap.parse_args()
    run = args.run or latest_run()

    obs = pd.read_csv(CESTRIN)
    obs["trucks"] = obs[TRUCK_COLS].sum(axis=1)
    obs["drum_key"] = obs["drum"].str.upper().str.replace(" ", "", regex=False)
    obs["drum_key"] = obs["drum_key"].map(lambda k: OBS_CORRIDOR.get(k, k))
    obs["tkm"] = obs["trucks"] * obs["l_recenzata_km"]
    obs = (obs.groupby("drum_key", as_index=False)
              .agg(drum=("drum", lambda s: " + ".join(s)),
                   l_recenzata_km=("l_recenzata_km", "sum"), tkm=("tkm", "sum")))
    obs["trucks"] = obs["tkm"] / obs["l_recenzata_km"]

    exp = REPO / "output" / "Romania" / run / "transport_edges_with_flows_0.geojson"
    e = gpd.read_file(exp)
    r = e[(e["type"] == "roads") & (e["foreign"].fillna(0) != 1)].copy()
    r["road"] = [road_of(x) for x in r["ref"].fillna("")]
    r["road"] = r["road"].map(lambda k: CORRIDOR.get(k, k) if k else None)
    r["tons"] = r["flow_total_tons"].fillna(0.0)
    m = (r.dropna(subset=["road"])
          .assign(tkm=lambda d: d.tons * d.km)
          .groupby("road").agg(model_km=("km", "sum"), tons_km=("tkm", "sum"),
                               n_edges=("km", "size")))
    m["model_mean_tons_wk"] = m["tons_km"] / m["model_km"]

    j = obs.merge(m, left_on="drum_key", right_index=True, how="left")
    matched = j[j["model_km"].notna() & (j["trucks"] > 0)].copy()
    unm_obs = j[j["model_km"].isna()].nlargest(8, "trucks")
    unm_mod = m[~m.index.isin(set(j["drum_key"]))].nlargest(
        8, "model_mean_tons_wk")

    # share/ratio basis: each side's truck-km share within the matched set
    matched["obs_tkm"] = matched["trucks"] * matched["l_recenzata_km"]
    matched["mod_tkm"] = matched["tons_km"]          # tons x km, own basis
    matched["obs_share"] = matched["obs_tkm"] / matched["obs_tkm"].sum()
    matched["mod_share"] = matched["mod_tkm"] / matched["mod_tkm"].sum()
    matched["share_ratio"] = matched["mod_share"] / matched["obs_share"]
    matched["coverage"] = matched["model_km"] / matched["l_recenzata_km"]

    sp_all = matched["model_mean_tons_wk"].corr(matched["trucks"],
                                                method="spearman")
    # rings/variants: metropolitan distribution traffic, out of model scope
    ring = matched["drum"].str.contains(r"Centura|Varianta|ring|legatura",
                                        case=False, regex=True)
    tgt = matched[(matched["l_recenzata_km"] >= args.min_km)
                  & (matched["trucks"] >= args.min_trucks) & ~ring].copy()
    sp_tgt = tgt["model_mean_tons_wk"].corr(tgt["trucks"], method="spearman")
    implied = matched["mod_tkm"].sum() / (matched["obs_tkm"].sum() * 7)
    inband = tgt["share_ratio"].between(0.5, 2.0)
    wmed = tgt.loc[tgt["share_ratio"] > 0, "share_ratio"]

    print(f"run {run}: {len(m)} model roads, {len(obs)} CESTRIN roads, "
          f"{len(matched)} matched")
    print(f"Spearman(model mean tons/wk, trucks AADT): {sp_all:.3f} all "
          f"matched | {sp_tgt:.3f} on the {len(tgt)} TARGET roads "
          f"(>={args.min_km:.0f} km & >={args.min_trucks:.0f} trucks)")
    print(f"implied payload (model tkm/wk over observed truck-km/wk): "
          f"{implied:.1f} t/truck  [sanity only - scope freight vs all "
          f"trucks incl. empties]")
    import numpy as np
    print(f"share ratios on targets: {int(inband.sum())}/{len(tgt)} within "
          f"[0.5, 2]; median {wmed.median():.2f}; "
          f"median |log2 ratio| {np.abs(np.log2(wmed)).median():.2f}")

    tgt = tgt.sort_values("trucks", ascending=False)
    cols = ["drum", "l_recenzata_km", "trucks", "model_km", "coverage",
            "model_mean_tons_wk", "obs_share", "mod_share", "share_ratio"]
    pd.set_option("display.width", 220)
    print("\nTARGET roads (rank/ratio sheet):")
    print(tgt[cols].round(3).to_string(index=False))
    print("\nbiggest observed roads with NO model match (rings/variants "
          "expected):")
    print(unm_obs[["drum", "l_recenzata_km", "trucks"]].to_string(index=False))
    if len(unm_mod):
        print("\nmodel roads with no CESTRIN row:")
        print(unm_mod[["model_km", "model_mean_tons_wk"]].round(1).to_string())

    out = exp.parent / "cestrin_road_comparison.csv"
    matched["target"] = matched.index.isin(tgt.index)
    matched[["drum"] + cols[1:] + ["target"]].sort_values(
        "trucks", ascending=False).to_csv(out, index=False)
    print(f"\nwritten {out}")
    return 0


if __name__ == "__main__":
    main()
