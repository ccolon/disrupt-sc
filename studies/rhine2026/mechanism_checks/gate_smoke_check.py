"""Smoke check of the capacity gate on the Rhine (22 Sep 2026): the ten-week laptop run `smoke_gate10`
(2026_first10, --constraint-mode on --closure-threshold -1: Kaub's capacity = load factor x its anchored
baseline flow every week, no closure and no surcharge, rail and road unlimited) against the price-with-closures
reference. Reads the gate's log lines (cut / re-sent / blocked tons per step), the routing summary by cargo class,
the weekly German value-added loss of both runs and the firms below 99 % of their baseline.

Usage:
    python studies/rhine2026/mechanism_checks/gate_smoke_check.py [--run smoke_gate10] [--ref 2026_cal_base_full]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

RUNS = Path("C:/dsc_runs/rhine2026")
GATE = re.compile(r"Capacity gate t=(\d+): (\d+) round\(s\), (\d+) saturated edge\(s\), cut ([\d,]+) t, re-sent ([\d,]+) t, blocked ([\d,]+) t")


def weekly_loss(run: Path, region: str = "DEU") -> pd.Series:
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm").production
    fd["base"] = fd.firm.map(b0)
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    fd["va_share"] = fd.sector.map((va.mrio_va / va.mrio_output).to_dict()).fillna(0.3)
    fd["va_loss"] = (fd.base - fd.production).clip(lower=0) * fd.va_share
    fd["low"] = fd.production < 0.99 * fd.base
    d = fd[fd.region == region]
    out = d.groupby("time_step").agg(loss_mUSD=("va_loss", "sum"), firms_below99_pct=("low", lambda s: 100 * s.mean()))
    weekly_va = pd.read_csv(run / "mrio_by_region.csv").set_index("region").mrio_va[region] / 52.0
    out["loss_%week"] = 100 * out.loss_mUSD / weekly_va
    return out


def main(run: Path, ref: Path):
    log = (run / "exp.log").read_text(encoding="utf-8", errors="replace")
    print(f"gate run {run.name}: completed {'Done.' in log}")
    rows = [dict(t=int(m[1]), rounds=int(m[2]), saturated=int(m[3]), cut_kt=int(m[4].replace(',', '')) / 1e3,
                 resent_kt=int(m[5].replace(',', '')) / 1e3, blocked_kt=int(m[6].replace(',', '')) / 1e3)
            for m in GATE.finditer(log)]
    print("\nGate per step (tons cut at the saturated edges, re-sent elsewhere, blocked = returned to stock):")
    print(pd.DataFrame(rows).round(1).to_string(index=False) if rows else "  no gate line (nothing cut)")
    rs = pd.read_csv(run / "routing_summary.csv")
    rs = rs[rs.cargo_type.isin(["container", "dry_bulk", "liquid_bulk"])]
    piv = rs.pivot_table(index="time_step", columns="cargo_type",
                         values=["alternative_usd", "capacity_blocked_usd", "blocked_usd"]).round(0)
    print("\nRouting summary by cargo class (mUSD/week):")
    print(piv.to_string())
    print("\nWeekly German value-added loss (mUSD and % of a week's value added) and firms below 99 % of baseline:")
    g = weekly_loss(run); r = weekly_loss(ref).reindex(g.index)
    t = pd.DataFrame({"gate_loss": g.loss_mUSD, "gate_%wk": g["loss_%week"], "gate_firms<99%": g.firms_below99_pct,
                      "ref_loss": r.loss_mUSD, "ref_%wk": r["loss_%week"], "ref_firms<99%": r.firms_below99_pct})
    print(t.round(2).to_string())
    print(f"\ncumulated DEU loss over the {int(g.index.max())} weeks: gate {g.loss_mUSD.sum():,.0f} mUSD vs reference "
          f"{r.loss_mUSD.sum():,.0f} (price with closures, without the pipeline rule)")
    lr = run / "logistics_report.csv"
    if lr.exists():
        d = pd.read_csv(lr)
        cols = [c for c in d.columns if c in ("time_step", "name", "type", "tons", "capacity", "utilization_pct", "load_tons", "capacity_tons")]
        print("\nMonitored edges (steps 0-1):")
        print(d[d.name.astype(str).str.contains("mainz_koblenz|koblenz$|mainz$", regex=True)][cols].to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="smoke_gate10")
    ap.add_argument("--ref", default="2026_cal_base_full")
    a = ap.parse_args()
    main(RUNS / a.run, RUNS / a.ref)
