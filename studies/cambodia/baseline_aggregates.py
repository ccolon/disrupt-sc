"""Baseline aggregates of the paper's networks, for the macros that scale the losses (10 Nov 2026, gate C).

For each network (seed) of a batch, from one run folder per seed: the households' consumption on day 0 (USD a day,
all sectors, imports included), the number of firms and household points, the model's value added (MRIO, mUSD a
year) and the run's household loss (USD). One row per seed; the paper's figure code reads the table.

Usage (cluster): python baseline_aggregates.py <batch_dir> <run_pattern with {seed}> <seeds, e.g. 1-20> <out.csv>
    python baseline_aggregates.py /projects/disruptsc/runs/cambodia/grid_d12_20261108 lag0_d12_s{seed}_t116 1-20 baseline_d12.csv
"""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

BATCH, PATTERN, SEEDS, OUT = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
a, b = (int(x) for x in SEEDS.split("-"))
rows = []
for s in range(a, b + 1):
    d = BATCH / PATTERN.format(seed=s)
    h = pd.read_csv(d / "household_daily_by_sector.csv")
    day0 = h[h.time_step == 0]
    firms = len(json.loads((d / "firm_table.geojson").read_text())["features"])
    hh = len(json.loads((d / "household_table.geojson").read_text())["features"])
    va = pd.read_csv(d / "mrio_by_region.csv").set_index("region").loc["KHM", "mrio_va"]
    loss = pd.read_csv(d / "loss_summary.csv")["households"].iloc[0]
    rows.append({"seed": s, "run": d.name, "hh_consumption_day_usd": day0.consumption.sum(),
                 "hh_consumption_day_khm_usd": day0[day0.sector.str.startswith("KHM_")].consumption.sum(),
                 "firms": firms, "household_points": hh, "mrio_va_musd": va, "loss_households_usd": loss})
t = pd.DataFrame(rows)
t.to_csv(OUT, index=False)
print(t.to_string(index=False))
print("distinct per seed:", {c: t[c].nunique() for c in ("hh_consumption_day_usd", "firms", "household_points", "mrio_va_musd")})
print("sha256", hashlib.sha256(open(OUT, "rb").read()).hexdigest(), OUT)
