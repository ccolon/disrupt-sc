"""Stationarity of the undisturbed baseline (6 Oct 2026, review OR3): the run `stationarity6w` (profile flat6w, six weeks
at 250 cm, constraint off, --no-early-stop) must keep every firm at its target production and every stock at its target
week after week. Reports, per week: firms below their production target, the extreme production and stock ratios to
t = 0 (all firms, and the material firms producing more than 10,000 USD a week), total production, the minimum fill
ratio, the household consumption loss and the tonnage transported.

Usage:
    python studies/rhine2026/stationarity_check.py [--run C:/dsc_runs/rhine2026/stationarity6w]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def main(run: Path, out: Path):
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "production", "production_target", "input_stock", "rationing"])
    b = fd[fd.time_step == 0].set_index("firm")
    material = b.index[b.production > 0.01]
    hh = pd.read_csv(run / "household_data.csv").groupby("time_step").consumption_loss.sum()
    cd = pd.read_csv(run / "country_data.csv").groupby("time_step").tons_transported.sum()
    L = [f"Stationarity of the undisturbed baseline: {run.name}, {int(fd.time_step.max())} weeks at 250 cm, constraint off, early stop off",
         f"  {len(b)} firms, of which {len(material)} material (> 0.01 mUSD a week at t = 0)", ""]
    for t in sorted(fd.time_step.unique()):
        x = fd[fd.time_step == t].set_index("firm")
        gap = (x.production_target - x.production) / x.production_target.clip(lower=1e-12)
        rel = (x.production / b.production).replace([np.inf, -np.inf], np.nan)
        st = (x.input_stock / b.input_stock).replace([np.inf, -np.inf], np.nan)
        m = x.index.isin(material)
        L.append(f"  week {int(t)}: below target {(gap > 1e-6).sum()} firms (material {(gap[m] > 1e-6).sum()}); production / t0: min {rel[m].min():.5f} max {rel[m].max():.5f} (material), "
                 f"total {x.production.sum() / b.production.sum():.6f}; input stock / t0: min {st[m].min():.5f} max {st[m].max():.5f} (material), min {st.min():.4f} all; "
                 f"fill ratio min {x.rationing.min():.4f}; household consumption loss {hh.get(t, 0.0):.6f} mUSD; tons transported {cd.get(t, float('nan')):,.0f}")
    text = "\n".join(L)
    print(text)
    out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="C:/dsc_runs/rhine2026/stationarity6w")
    ap.add_argument("--out", default=str(HERE / "additional_data" / "stationarity_20261005.txt"))
    a = ap.parse_args()
    main(Path(a.run), Path(a.out))
