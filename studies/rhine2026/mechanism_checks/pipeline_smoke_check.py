"""Smoke check of the pipelined-flows rule (22 Sep 2026) on the two-step laptop run (scenarios/smoke2w.csv).

Compares the baseline week of the smoke run with the reference run without the rule (2026_cal_base_full,
same build rules, same seed): the value and tonnage across Kaub by flow class, the routing summary's
pipelined bucket, and the closure week (t = 2, every class closed at Kaub): what the pipelined links still
deliver, what the crude exporters sell, and that no shipment was left uncollected (exp.log "Done.").

Usage:
    python studies/rhine2026/mechanism_checks/pipeline_smoke_check.py [--run C:/dsc_runs/rhine2026/smoke_pipeline]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

RUNS = Path("C:/dsc_runs/rhine2026")
KAUB = "rhine_mainz_koblenz"
KEYS = ["flow_total", "flow_total_tons", "tons_dry_bulk", "tons_liquid_bulk", "tons_container",
        "flow_import", "flow_import_mining", "flow_import_oil_and_gas", "flow_mining", "flow_oil_and_gas",
        "flow_domestic_B2B_mining", "flow_domestic_B2B_oil_and_gas"]


def kaub(run: Path, t: int) -> dict:
    g = json.load(open(run / f"transport_edges_with_flows_{t}.geojson", encoding="utf-8"))
    (f,) = [x for x in g["features"] if x["properties"].get("name") == KAUB]
    return {k: (f["properties"].get(k) or 0.0) for k in KEYS}


def main(run: Path, ref: Path):
    print(f"smoke run {run.name} vs reference {ref.name}\n")
    log = (run / "exp.log").read_text(encoding="utf-8", errors="replace")
    rule = [l for l in log.splitlines() if "pipelined_flows:" in l]
    print("rule:", rule[-1].split(" - ")[-1] if rule else "NOT LOGGED")
    print("completed:", "Done." in log, "\n")
    a, b = kaub(ref, 0), kaub(run, 0)
    t = pd.DataFrame({"reference": a, "smoke": b})
    t["diff"] = t.smoke - t.reference
    t["diff_%"] = (100 * t["diff"] / t.reference.replace(0, float("nan"))).round(1)
    print("Kaub, baseline week (mUSD/week; tons/week):")
    print(t.round(1).to_string(), "\n")
    print(f"Kaub tonnage, Mt/yr: reference {a['flow_total_tons'] * 52 / 1e6:.1f} -> smoke {b['flow_total_tons'] * 52 / 1e6:.1f}\n")
    rs = pd.read_csv(run / "routing_summary.csv")
    cols = [c for c in ["time_step", "cargo_type", "total_usd", "main_usd", "alternative_usd", "pipelined_usd", "blocked_usd"] if c in rs]
    print("routing summary of the smoke run (mUSD/week):")
    print(rs[cols].round(0).to_string(index=False), "\n")
    tot = rs.groupby("time_step")[["total_usd", "pipelined_usd", "blocked_usd"]].sum()
    print("share of served value delivered by pipeline, per step:")
    print((100 * tot.pipelined_usd / tot.total_usd).round(2).to_string(), "\n")
    cd = pd.read_csv(run / "country_data.csv")
    cols = [c for c in ["qty_sold", "usd_transported", "tons_transported"] if c in cd.columns]
    if cols:
        crude = cd[cd.country.isin(["NOR", "MEA", "RUS", "GBR", "USA", "AFR", "ROW"])].pivot_table(index="country", columns="time_step", values=cols[0])
        print(f"crude exporters, {cols[0]} by step (closure at t=2):")
        print(crude.round(0).to_string(), "\n")
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    ref_prod = fd[fd.time_step == 0].set_index("firm").production
    for t_ in sorted(fd.time_step.unique()):
        w = fd[fd.time_step == t_]
        loss = (w.firm.map(ref_prod) - w.production).clip(lower=0).sum()
        print(f"t={t_}: production shortfall vs t=0, all firms: {loss:,.0f} mUSD; "
              f"refineries (C19) {(w[w.sector == 'C19'].firm.map(ref_prod) - w[w.sector == 'C19'].production).clip(lower=0).sum():,.1f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(RUNS / "smoke_pipeline"))
    ap.add_argument("--ref", default=str(RUNS / "2026_cal_base_full"))
    a = ap.parse_args()
    main(Path(a.run), Path(a.ref))
