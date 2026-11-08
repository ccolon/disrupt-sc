"""Check that the horizon does not change a run's path: the grid's runs (116 days, or 180 for lags above 2d) against
the same scenario, network and closure length in the 180-day pilot batches (8 Nov 2026).

For every pair found, the daily household loss (loss_per_region_sector_time.csv summed over sectors) is compared
day by day up to the shorter run's last day. Expected: identical series (the model's state before day t does not
depend on t_final), so the grid's networks 1-5 need no separate treatment.

Usage: python studies/cambodia/compare_horizons.py --grid <grid batch> --ref <180-day batch> [--out <csv>]
"""
import argparse
import json
from pathlib import Path

import pandas as pd


def daily(folder: Path) -> pd.Series:
    lt = pd.read_csv(folder / "loss_per_region_sector_time.csv")
    return lt.groupby("time_step")["loss"].sum().sort_index()


def key(folder: Path):
    sr = json.loads((folder / "study_run.json").read_text(encoding="utf-8"))
    sc = "lag0" if sr["scenario"] == "simul" else sr["scenario"]
    return (sc, int(sr["seed"]), int(sr["duration"]), tuple(sr.get("overrides") or [])), int(sr["t_final"])


def runs(batch: Path):
    out = {}
    for f in sorted(p for p in batch.iterdir() if (p / "study_run.json").exists()):
        k, t = key(f)
        if k[0] == "lag0" and k in out:   # keep the lag0 run when a batch has both lag0 and simul
            if not f.name.startswith("lag0"):
                continue
        out[k] = (f, t)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", required=True, type=Path)
    ap.add_argument("--ref", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    g, r = runs(a.grid), runs(a.ref)
    rows = []
    for k in sorted(set(g) & set(r)):
        (fg, tg), (fr, tr) = g[k], r[k]
        dg, dr = daily(fg), daily(fr)
        T = min(tg, tr)
        dg, dr = dg[dg.index <= T], dr[dr.index <= T]
        diff = (dg - dr).abs()
        rows.append(dict(grid_run=fg.name, ref_run=fr.name, t_grid=tg, t_ref=tr, days=len(diff),
                         max_abs_diff=float(diff.max()), cum_grid=float(dg.sum()), cum_ref=float(dr.sum()),
                         rel_cum_diff=float(abs(dg.sum() - dr.sum()) / max(abs(dr.sum()), 1e-9))))
    df = pd.DataFrame(rows)
    if a.out:
        df.to_csv(a.out, index=False)
    print(f"{len(df)} pairs ({len(g)} grid runs read, {len(r)} reference runs)")
    if df.empty:
        return
    print(f"max daily |diff| over all pairs: {df.max_abs_diff.max():.3g} USD; pairs with any difference: "
          f"{int((df.max_abs_diff > 0).sum())}; max relative difference of the cumulative loss {df.rel_cum_diff.max():.2e}")
    if (df.max_abs_diff > 0).any():
        print(df[df.max_abs_diff > 0].sort_values("max_abs_diff", ascending=False).head(10).to_string(index=False))


if __name__ == "__main__":
    main()
