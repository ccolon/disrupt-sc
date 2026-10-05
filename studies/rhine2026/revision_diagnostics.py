"""Diagnostics for the revision of 6 Oct 2026 (review of 5 Oct), from the packed outputs of the batch of 30 Sep.

  1. the German gross loss by mutually exclusive sector group (A, B-E with D+E apart, F, G-T) and, as a separate
     attribute, the share in sectors that cannot catch up (review E4, C04)
  2. the delivered-price statistics with their denominators: the share of the value delivered on the whole network that
     pays more than 1 % above its baseline price, by cargo class and economy-wide, in the worst weeks (E6, C15)
  3. the channel decomposition at the routing level: what the surcharge moves off the river before the gate cuts, by
     cargo class, base against constraint-only and surcharge-only (C05)
  4. the flat profile against the season: capacity-blocked value and gate tonnage (C11)
  5. the horizons: steps of each run, the catch-up production of the goods sectors by week to the end of the run and
     the backlog left (C13, E7)
  6. the supplier weights of the buyers served across Kaub at the start of the second wave, from the link-level run (OR4)
  7. the prospective 2026 path: the model's monthly industrial shortfall, June to December 2026, for the runs that
     carry firm data (NS4)

Usage:
    python studies/rhine2026/revision_diagnostics.py [--runs C:/dsc_runs/rhine2026] [--out additional_data/revision_20261006_diagnostics.txt]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from read_batch_20261007 import firm_losses, table  # noqa: E402
from matched_estimand_2018 import model_path  # noqa: E402

GROUP = {"A": "A agriculture", "B": "B-E industry", "C": "B-E industry", "D": "B-E industry", "E": "B-E industry",
         "F": "F construction"}
RECOVERABLE = ("A", "B", "C", "F")          # the sectors whose lost weeks can be caught up (Methods)
GOODS = ("A", "B", "C", "F")


def group_of(sector: str) -> str:
    return GROUP.get(sector[0], "G-T services")


def sector_groups(runs: Path, run: str, q: float) -> list[str]:
    fd = firm_losses(runs / run); de = fd[fd.region == "DEU"]; tot = de.loss.sum()
    g = de.groupby(de.sector.map(group_of)).loss.sum()
    de_util = de[de.sector.isin(["D", "E"])].loss.sum()
    rec = de[de.sector.str[:1].isin(RECOVERABLE)].loss.sum()
    L = [f"  {run}: gross loss {tot:,.0f} mUSD = {tot / q:.3f} % of a quarter"]
    for k in ("A agriculture", "B-E industry", "F construction", "G-T services"):
        L.append(f"    {k:16s} {100 * g.get(k, 0) / tot:5.1f} %" + (f"   (of which D+E utilities {100 * de_util / tot:.1f} %)" if k.startswith("B-E") else ""))
    L.append(f"    cannot catch up (D, E, G-T): {100 * (tot - rec) / tot:.0f} %; can (A, B, C, F): {100 * rec / tot:.0f} %")
    top = de.groupby("sector").loss.sum().sort_values(ascending=False).head(8)
    L.append("    largest sectors: " + ", ".join(f"{k} {100 * v / tot:.1f}" for k, v in top.items()))
    return L


def price_shares(runs: Path, run: str) -> list[str]:
    p = pd.read_csv(runs / run / "price_by_cargo.csv")
    w = p.groupby("time_step").apply(lambda g: (g.delivered_value * g.share_value_above_1pct).sum() / g.delivered_value.sum(), include_groups=False)
    L = [f"  {run}: share of the value delivered on the network paying > 1 % above its baseline price, economy-wide (value-weighted over the cargo classes)"]
    for t in sorted(w.sort_values(ascending=False).index[:3]):
        g = p[p.time_step == t]
        L.append(f"    week {t}: {100 * w[t]:.2f} %; by class " + ", ".join(f"{c} {100 * s:.1f} %" for c, s in zip(g.cargo_type, g.share_value_above_1pct))
                 + "; value shares " + ", ".join(f"{c} {100 * v / g.delivered_value.sum():.0f} %" for c, v in zip(g.cargo_type, g.delivered_value)))
    return L


def routing(runs: Path, run: str) -> pd.DataFrame:
    return pd.read_csv(runs / run / "routing_summary.csv")


def channels(runs: Path) -> list[str]:
    L = ["  totals over the run, mUSD (routing_summary.csv): what leaves the normal route for an alternative, and what the gate withholds"]
    for run in ("2026_s07_base", "2026_s07_gateonly", "2026_s07_surchargeonly"):
        s = routing(runs, run)
        bulk = s[s.cargo_type.isin(["dry_bulk", "liquid_bulk"])]; cont = s[s.cargo_type == "container"]
        L.append(f"    {run:24s} bulk: alternative {bulk.alternative_usd.sum():8,.0f}, capacity-blocked {bulk.capacity_blocked_usd.sum():8,.0f}, "
                 f"blocked {bulk.blocked_usd.sum():8,.0f} | containers: alternative {cont.alternative_usd.sum():8,.0f}, capacity-blocked {cont.capacity_blocked_usd.sum():6,.0f}")
    b = routing(runs, "2026_s07_base"); g = routing(runs, "2026_s07_gateonly")
    L.append("  by week, bulk alternative value (base / constraint-only) and capacity-blocked (base / constraint-only), mUSD:")
    for t in range(1, 24):
        bb = b[(b.time_step == t) & b.cargo_type.isin(["dry_bulk", "liquid_bulk"])]; gg = g[(g.time_step == t) & g.cargo_type.isin(["dry_bulk", "liquid_bulk"])]
        if bb.capacity_blocked_usd.sum() + gg.capacity_blocked_usd.sum() > 0.5:
            L.append(f"    t={t:2d}: alternative {bb.alternative_usd.sum():6,.0f} / {gg.alternative_usd.sum():6,.0f}; capacity-blocked {bb.capacity_blocked_usd.sum():6,.0f} / {gg.capacity_blocked_usd.sum():6,.0f}")
    return L


def gate_tons(log: Path) -> dict[int, tuple[float, float, float]]:
    out = {}
    if not log.exists():
        return out
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"Capacity gate t=(\d+):.*cut ([\d,]+) t, re-sent ([\d,]+) t, blocked ([\d,]+) t", line)
        if m:
            out[int(m.group(1))] = tuple(float(m.group(i).replace(",", "")) for i in (2, 3, 4))
    return out


def flat(runs: Path) -> list[str]:
    L = []
    for run in ("2026_s07_base", "wave07_flat"):
        s = routing(runs, run); bulk = s[s.cargo_type.isin(["dry_bulk", "liquid_bulk"])]
        gt = gate_tons(runs / f"{run}.log")
        tons = f"; gate (log): cut {sum(v[0] for v in gt.values()):,.0f} t, re-sent {sum(v[1] for v in gt.values()):,.0f} t, blocked {sum(v[2] for v in gt.values()):,.0f} t over {len(gt)} gated weeks" if gt else "; gate tonnage not in the packed log"
        L.append(f"  {run:16s} capacity-blocked value {bulk.capacity_blocked_usd.sum():,.0f} mUSD, alternative {bulk.alternative_usd.sum():,.0f} mUSD{tons}")
    return L


def horizons(runs: Path, run: str, q: float) -> list[str]:
    fd = firm_losses(runs / run); de = fd[fd.region == "DEU"]
    n = int(de.time_step.max())
    goods = de[de.sector.str[:1].isin(GOODS)]
    signed = (goods.base - goods.production) * goods.vs           # + shortfall, - catch-up
    weekly = signed.groupby(goods.time_step).sum()
    catch = (-signed.clip(upper=0)).groupby(goods.time_step).sum()
    backlog = 0.0; B = {}
    for t in range(1, n + 1):
        backlog = max(0.0, backlog + float(weekly.get(t, 0.0))); B[t] = backlog
    gross = float(signed.clip(lower=0).sum())
    L = [f"  {run}: {n} steps after t=0; goods sectors (A, B, C, F) gross shortfall {gross:,.0f} mUSD, backlog left at the end {B[n]:,.0f} ({100 * B[n] / gross:.0f} % of the gross; {100 * (1 - B[n] / gross):.0f} % worked off)",
         "    catch-up production by week (mUSD): " + ", ".join(f"{t}:{catch.get(t, 0):.0f}" for t in range(max(1, n - 23), n + 1)),
         f"    backlog by week (mUSD): " + ", ".join(f"{t}:{B[t]:.0f}" for t in range(max(1, n - 23), n + 1))]
    return L


def supplier_weights(runs: Path, run: str = "2026_s07_full") -> list[str]:
    f = runs / run / "link_flows_disrupted.csv.gz"
    if not f.exists():
        return [f"  {run}: no link table"]
    t = pd.read_csv(f)
    t = t[t.buyer_region == "DEU"]
    key = ["seller_region", "seller_sector", "buyer_region", "buyer_sector"]
    trough = t[t.time_step.isin([7, 8, 9])]
    dep = trough[trough.capacity_blocked > 0].groupby(key).size().index          # supplier pairs cut by the gate in the August trough
    t["kaub"] = t.set_index(key).index.isin(dep)
    buyers = t[t.kaub].groupby(["buyer_region", "buyer_sector"]).size().index
    L = [f"  {run}: German buyers with at least one supplier pair cut at Kaub in the August trough (weeks 7-9): {len(buyers)} region-sectors; "
         f"share of their offered deliveries that comes from those supplier pairs, by week (value-weighted over the buyers):"]
    tb = t.set_index(["buyer_region", "buyer_sector"]); tb = tb[tb.index.isin(buyers)].reset_index()
    for step in (0, 6, 10, 11, 12, 15, 19, 23, 30, 40):
        w = tb[tb.time_step == step]
        if len(w):
            L.append(f"    t={step:2d}: {100 * w[w.kaub].delivery_offered.sum() / w.delivery_offered.sum():.1f} % (offered {w.delivery_offered.sum():,.0f}; from the Kaub pairs {w[w.kaub].delivery_offered.sum():,.0f})")
    return L


def prospective(runs: Path, names: list[str]) -> list[str]:
    L = ["  monthly shortfall of German industrial production, % (months = mean of their days; June covers 22-30 June only):"]
    for r in names:
        if not (runs / r / "firm_data.csv").exists():
            L.append(f"    {r}: no firm data"); continue
        d = model_path(runs / r, 2026)
        labs = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        L.append(f"    {r:22s} " + " ".join(f"{m} {d[f'ind_{m}']:.2f}" for m in labs) + f"  integral Jul-Dec {d['ind_integrated_pct_months']:.2f}  peak {d['peak_month_ind']}")
    return L


def main(runs: Path, out: Path):
    m = table(HERE / "additional_data" / "compare_runs_batch_jobs_20261007_main.csv")
    q26 = m.loc["2026_s07_base", "DEU_cum_mUSD"] / m.loc["2026_s07_base", "DEU_%quarter"]
    q18 = m.loc["2018_s07_base", "DEU_cum_mUSD"] / m.loc["2018_s07_base", "DEU_%quarter"]
    L = ["Revision diagnostics, 6 Oct 2026 (review of 5 Oct), on the packed outputs of the batch of 30 Sep", ""]
    L += ["== 1. German gross loss by sector group (mutually exclusive), and the catch-up attribute apart =="]
    L += sector_groups(runs, "2026_s07_base", q26) + sector_groups(runs, "2018_s07_base", q18)
    L += ["", "== 2. Delivered prices: the share of value paying more than 1 % above baseline, with its denominators =="]
    L += price_shares(runs, "2026_s07_full") + price_shares(runs, "2018_s07_full")
    L += ["", "== 3. Channel decomposition at the routing level =="] + channels(runs)
    L += ["", "== 4. The flat profile against the season =="] + flat(runs)
    L += ["", "== 5. Horizons and the catch-up tail =="] + horizons(runs, "2026_s07_base", q26) + horizons(runs, "2018_s07_base", q18)
    L += ["", "== 6. Supplier weights of the Kaub-served buyers through the season =="] + supplier_weights(runs)
    L += ["", "== 7. The prospective 2026 path =="] + prospective(runs, ["2026_s07_base", "2026_s07_package", "2026_s07_sup2", "2026_s07_gateonly", "2026_s07_surchargeonly"])
    text = "\n".join(L)
    print(text)
    out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="C:/dsc_runs/rhine2026")
    ap.add_argument("--out", default=str(HERE / "additional_data" / "revision_20261006_diagnostics.txt"))
    a = ap.parse_args()
    main(Path(a.runs), Path(a.out))
