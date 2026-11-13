"""Read the R2 pilots (13 Nov 2026; Paper_Cambodia/pipeline/reports/18-19): one row per run of the given batches.

Per run: household and foreign-buyer losses (loss_summary.csv), the daily household loss (loss_per_region_sector_time
summed by day) with its peak, settling day (last day above 1 % of the peak, as read_batch.py) and the last day's loss
in % of the peak, households' stocks on day 0 (household_data.csv inventory_total: > 0 only when households hold
stocks), and the value-added loss as in va_loss.py (firm_daily.csv, MRIO value-added shares).

Usage (cluster): python read_pilot_r2.py <out.csv> <batch_dir> [<batch_dir> ...]
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd

OUT = Path(sys.argv[1])
rows = []
for batch in (Path(b) for b in sys.argv[2:]):
    for d in sorted(p for p in batch.iterdir() if p.is_dir()):
        if not (d / "loss_summary.csv").exists():
            print("missing loss_summary:", d)
            continue
        loss = pd.read_csv(d / "loss_summary.csv").iloc[0]
        lt = pd.read_csv(d / "loss_per_region_sector_time.csv")
        daily = lt.groupby("time_step")["loss"].sum().sort_index()
        peak = float(daily.max()) if len(daily) else 0.0
        above = daily[daily > 0.01 * peak] if peak > 0 else daily.iloc[0:0]
        hh = pd.read_csv(d / "household_data.csv", usecols=["time_step", "inventory_total"])
        inv0 = float(hh[hh.time_step == 0].inventory_total.sum())
        fd = pd.read_csv(d / "firm_daily.csv", usecols=["time_step", "sector", "production"])
        mrio = pd.read_csv(d / "mrio_by_sector.csv").set_index("sector")
        share = (mrio.mrio_va / mrio.mrio_output).where(mrio.mrio_output > 0, 0.0)
        p = fd.pivot(index="time_step", columns="sector", values="production").fillna(0.0)
        va = float(((p.loc[0] - p.loc[p.index >= 1]) * share.reindex(p.columns)).sum(axis=1).sum())
        rows.append({"batch": batch.name, "run": d.name, "loss_households": float(loss["households"]),
                     "loss_countries": float(loss["countries"]), "loss_va": va, "peak": peak,
                     "settle_day": int(above.index.max()) if len(above) else 0,
                     "last_day": int(daily.index.max()) if len(daily) else 0,
                     "last_day_pct_peak": float(100 * daily.iloc[-1] / peak) if peak > 0 else 0.0,
                     "hh_inventory_day0": inv0})
t = pd.DataFrame(rows)
t.to_csv(OUT, index=False)
pd.set_option("display.width", 250)
print(t.drop(columns=["batch"]).round(1).to_string(index=False))
print("sha256", hashlib.sha256(OUT.read_bytes()).hexdigest(), OUT)
