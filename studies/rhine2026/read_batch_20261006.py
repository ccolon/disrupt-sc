"""Read the revision batch of 6 Oct 2026 (cluster/jobs_20261006_rev.txt) once its results are extracted in C:/dsc_runs/rhine2026.

Prints, against the reference run 2026_s30_base (and 2018_s30_base), each sensitivity's German loss, peak and EU loss;
the bounded-substitution runs with the relief value and tonnage per week; the fleet lever's weekly path against the base
(from the repacked firm data); the prospective band of the 2026 industrial path across the seed bases and the loading
tables; and the determinism check of 2026_rev_base. Writes additional_data/batch_20261006_summary.txt.

Usage:
    python studies/rhine2026/read_batch_20261006.py [--runs C:/dsc_runs/rhine2026]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "studies/rhine2026/additional_data"
sys.path.insert(0, str(ROOT / "studies/rhine2026"))
from read_batch_20260930 import table, firm_losses  # noqa: E402
from matched_estimand_2018 import model_path  # noqa: E402

PAIRS = [  # (run, label, base)
    ("2026_rev_base", "the reference run repeated after the fingerprint change (must equal 2026_s30_base)", "2026_s30_base"),
    ("2026_rev_rail50", "bounded substitution by rail, 50 kt a week", "2026_s30_base"),
    ("2026_rev_rail140", "bounded substitution by rail, 140 kt a week", "2026_s30_base"),
    ("2018_rev_rail50", "2018, bounded substitution 50 kt a week", "2018_s30_base"),
    ("2018_rev_rail140", "2018, bounded substitution 140 kt a week", "2018_s30_base"),
    ("2026_rev_head10", "capacity headroom 10 % (private caches)", "2026_s30_base"),
    ("2026_rev_head25", "capacity headroom 25 % (private caches)", "2026_s30_base"),
    ("2026_rev_rest15", "refill time 15 days", "2026_s30_base"),
    ("2026_rev_rest60", "refill time 60 days", "2026_s30_base"),
    ("2026_rev_floor02", "loading-table floor below 5 cm at 0.02", "2026_s30_base"),
    ("2026_rev_floor10", "loading-table floor below 5 cm at 0.10", "2026_s30_base"),
    ("2026_rev_deeplocal", "fairway +20 cm on the Kaub reach alone", "2026_s30_base"),
    ("2026_rev_fleetwide", "low-water fleet with its gain carried to 100 cm", "2026_s30_base"),
    ("2026_rev_dfuel0", "power sector's fuel-oil input non-critical", "2026_s30_base"),
    ("2026_rev_serv45", "45-day coping duration for the non-storable inputs", "2026_s30_base"),
    ("2026_rev_q25", "outlook's 25th percentile path", "2026_s30_base"),
    ("2026_rev_q75", "outlook's 75th percentile path", "2026_s30_base"),
]


def load_tables() -> pd.DataFrame:
    frames = [table(AD / f) for f in ("compare_runs_batch_jobs_20260930_main.csv", "compare_runs_batch_jobs_20260930_paired.csv")]
    rev = AD / "compare_runs_batch_jobs_20261006_rev.csv"
    if rev.exists():
        frames.append(table(rev))
    return pd.concat(frames)


def relief_by_week(runs: Path, run: str) -> list[str]:
    f = runs / run / "routing_summary.csv"
    if not f.exists():
        return [f"    {run}: no routing summary"]
    s = pd.read_csv(f)
    if "relief_usd" not in s.columns:
        return [f"    {run}: no relief column"]
    b = s[s.cargo_type.isin(["dry_bulk", "liquid_bulk"])].groupby("time_step")[["relief_usd", "capacity_blocked_usd", "alternative_usd"]].sum()
    tot = b.sum()
    L = [f"    {run}: relief {tot.relief_usd:,.0f} mUSD over the run, capacity-blocked {tot.capacity_blocked_usd:,.0f} (base 12,096), "
         f"by week (relief / blocked): " + ", ".join(f"{t}:{r.relief_usd:.0f}/{r.capacity_blocked_usd:.0f}" for t, r in b.iterrows() if t <= 23)]
    gt = {}
    log = runs / f"{run}.log"
    if log.exists():
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"Capacity gate t=(\d+):.*blocked ([\d,]+) t(?:, relief ([\d,]+) t of ([\d,]+) t offered)?", line)
            if m:
                gt[int(m.group(1))] = (float(m.group(2).replace(",", "")), float((m.group(3) or "0").replace(",", "")), float((m.group(4) or "0").replace(",", "")))
        if gt:
            L.append("      tonnage by week (withheld / relief placed / relief offered, kt): " + ", ".join(f"{t}:{v[0] / 1e3:.0f}/{v[1] / 1e3:.0f}/{v[2] / 1e3:.0f}" for t, v in sorted(gt.items()) if t <= 23))
    return L


def main(runs: Path):
    t = load_tables()
    L = ["Revision batch of 6 Oct 2026 (jobs_20261006_rev.txt): sensitivities against the reference runs", ""]
    L.append("== German loss (% of a quarter), peak (% of a week, week), EU loss (bn); change against the base ==")
    for run, lab, base in PAIRS:
        if run not in t.index:
            L.append(f"  {run:20s} (not in the tables yet)"); continue
        r, b = t.loc[run], t.loc[base]
        L.append(f"  {run:20s} {r['DEU_%quarter']:.3f} % (base {b['DEU_%quarter']:.3f}, {100 * (r['DEU_%quarter'] / b['DEU_%quarter'] - 1):+.0f} %), "
                 f"peak {r['DEU_peak_%week']:.2f} % wk {int(r['DEU_peak_week'])} (base {b['DEU_peak_%week']:.2f} wk {int(b['DEU_peak_week'])}), "
                 f"EU {r['EU_cum_mUSD'] / 1e3:.1f} bn (base {b['EU_cum_mUSD'] / 1e3:.1f})   {lab}")
    if "2026_rev_base" in t.index:
        d = abs(t.loc["2026_rev_base", "DEU_cum_mUSD"] - t.loc["2026_s30_base", "DEU_cum_mUSD"])
        L.append(f"  determinism: 2026_rev_base differs from 2026_s30_base by {d:.3f} mUSD" + (" (identical)" if d < 0.5 else " (NOT identical: investigate)"))

    L.append("\n== Bounded substitution: relief value and tonnage by week ==")
    for run in ("2026_rev_rail50", "2026_rev_rail140", "2018_rev_rail50", "2018_rev_rail140"):
        L += relief_by_week(runs, run)

    L.append("\n== The fleet lever's weekly path against the base (repacked firm data) ==")
    for run in ("2026_s30_base", "2026_s30_fleet", "2026_rev_fleetwide", "2026_s30_stock7", "2026_s30_deep20"):
        if (runs / run / "firm_data.csv").exists():
            fd = firm_losses(runs / run); w = fd[fd.region == "DEU"].groupby("time_step").loss.sum()
            L.append(f"  {run:20s} weeks 12-22 (mUSD): " + ", ".join(f"{int(w.get(k, 0))}" for k in range(12, 23)) + f"; sum 1-11 {w.loc[1:11].sum():,.0f}, 12-19 {w.loc[12:19].sum():,.0f}, 20+ {w.loc[20:].sum():,.0f}, peak wk {int(w.idxmax())} {w.max():,.0f}")
        else:
            L.append(f"  {run:20s} no firm data")

    L.append("\n== Prospective 2026 path: the band across the seed bases and the loading tables (monthly industrial shortfall, %) ==")
    labs = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    paths = {}
    for run in ["2026_s30_base"] + [f"2026_s30_seed{s}_base" for s in range(1, 11)] + ["2026_s30_tablelow", "2026_s30_tablehigh", "2026_rev_q25", "2026_rev_q75"]:
        if (runs / run / "firm_data.csv").exists():
            d = model_path(runs / run, 2026); paths[run] = [d[f"ind_{m}"] for m in labs]
            L.append(f"  {run:22s} " + " ".join(f"{m} {v:5.2f}" for m, v in zip(labs, paths[run])) + f"  integral {d['ind_integrated_pct_months']:.2f} peak {d['peak_month_ind']}")
    draws = [paths[r] for r in paths if "seed" in r or r == "2026_s30_base"]
    if len(draws) > 1:
        a = np.array(draws)
        L.append("  eleven draws, min-max by month: " + " ".join(f"{m} {a[:, i].min():.2f}-{a[:, i].max():.2f}" for i, m in enumerate(labs)))
        pd.DataFrame({"month": labs, "min": a.min(axis=0), "max": a.max(axis=0), "mean": a.mean(axis=0)}).to_csv(AD / "prospective_band_2026.csv", index=False)
    text = "\n".join(L)
    print(text)
    (AD / "batch_20261006_summary.txt").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="C:/dsc_runs/rhine2026")
    a = ap.parse_args()
    main(Path(a.runs))
