"""Value-added loss of Cambodia's firms in the paper runs (11 Nov 2026, user: "national VA & international buyer
losses ... they come out of the box so no rerun?").

The runs keep firm_daily.csv: production by day and sector, summed over firms (run_cambodia.summarise_firm_data).
Closures start on day 1, so day 0 is the undisturbed state (the none runs are exactly stationary, report 04). With
fixed technical coefficients, a sector's value added is a fixed share of its output, taken from the run's own
mrio_by_sector.csv (mrio_va / mrio_output). The value-added loss of a run is

    sum over days t >= 1 and sectors s of  va_share_s * (production_s(0) - production_s(t)),

at baseline prices; output above the baseline after the reopening (backlog) counts as a negative loss. The foreign
buyers' loss is read from loss_summary.csv (countries) for comparison.

Usage (cluster): python va_loss.py <out.csv> <batch_dir> [<batch_dir> ...]
    python va_loss.py va_loss.csv /projects/disruptsc/runs/cambodia/grid_d12_20261108 /projects/disruptsc/runs/cambodia/pair_d12_20261108
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd

OUT = Path(sys.argv[1])


def settle_day(daily: pd.Series) -> int:
    """Last day whose |daily value-added loss| exceeds 1 % of the peak daily loss (the household settling rule)."""
    big = daily.index[daily.abs() > 0.01 * daily.abs().max()]
    return int(big.max()) if len(big) else 0


rows, missing = [], []
for batch in (Path(b) for b in sys.argv[2:]):
    for d in sorted(p for p in batch.iterdir() if p.is_dir() and not p.name.startswith(("_", "analysis"))):
        f = d / "firm_daily.csv"
        if not f.exists() or not (d / "loss_summary.csv").exists():
            missing.append(str(d))
            continue
        fd = pd.read_csv(f, usecols=["time_step", "sector", "production"])
        mrio = pd.read_csv(d / "mrio_by_sector.csv").set_index("sector")
        share = (mrio.mrio_va / mrio.mrio_output).where(mrio.mrio_output > 0, 0.0)
        p = fd.pivot(index="time_step", columns="sector", values="production").fillna(0.0)
        unknown = sorted(set(p.columns) - set(share.index))
        if unknown:
            raise SystemExit(f"{d.name}: sectors without an MRIO value-added share: {unknown}")
        s = share.reindex(p.columns)
        base = p.loc[0]
        gap = base - p.loc[p.index >= 1]                       # output lost, by day and sector (USD)
        va_daily = (gap * s).sum(axis=1)
        loss = pd.read_csv(d / "loss_summary.csv").iloc[0]
        rows.append({"batch": batch.name, "run": d.name,
                     "va_day0_usd": float((base * s).sum()), "output_day0_usd": float(base.sum()),
                     "va_loss_usd": float(va_daily.sum()), "output_loss_usd": float(gap.to_numpy().sum()),
                     "va_loss_after_90_usd": float(va_daily[va_daily.index > 90].sum()),
                     "va_loss_min_daily_usd": float(va_daily.min()), "last_day": int(p.index.max()),
                     "va_loss_peak_daily_usd": float(va_daily.max()), "va_loss_last_day_usd": float(va_daily.iloc[-1]),
                     "va_loss_to_116_usd": float(va_daily[va_daily.index <= 116].sum()),
                     "va_settle_day": settle_day(va_daily),
                     "loss_households_usd": float(loss["households"]), "loss_countries_usd": float(loss["countries"])})
t = pd.DataFrame(rows)
t.to_csv(OUT, index=False)
print(f"{len(t)} runs read, {len(missing)} without firm_daily.csv or loss_summary.csv")
for m in missing[:20]:
    print("  missing:", m)
print("sha256", hashlib.sha256(OUT.read_bytes()).hexdigest(), OUT)
