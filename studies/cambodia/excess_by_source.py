"""Where and when does a successive-flood run lose more than its single floods (8 Nov 2026)?

For one network and closure length d: the additive counterfactual of lag L is the three single-basin runs, each
shifted to its event's start (Saigon at day 1, Mekong at 1 + L, Tonle Sap at 1 + 2L). The excess = lag run - that
counterfactual, by day (when) and by the loss file's region and sector columns (where).

Usage: python studies/cambodia/excess_by_source.py <grid batch> --seed 17 --d 12 --lag 12 [--top 12]
"""
import argparse
from pathlib import Path

import pandas as pd

ORDER = ("single_saigon", "single_mekong", "single_tonle")


def load(batch: Path, name: str) -> pd.DataFrame:
    hits = [p for p in batch.iterdir() if p.name == name or p.name.startswith(name + "_t")]
    if len(hits) != 1:
        raise SystemExit(f"{name}: {len(hits)} folders")
    return pd.read_csv(hits[0] / "loss_per_region_sector_time.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--d", type=int, required=True)
    ap.add_argument("--lag", type=int, required=True)
    ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()
    lag = load(a.batch, f"lag{a.lag}_d{a.d}_s{a.seed}")
    keys = [c for c in lag.columns if c not in ("time_step", "loss")]
    T = int(lag.time_step.max())
    add = []
    for i, sc in enumerate(ORDER):
        s = load(a.batch, f"{sc}_d{a.d}_s{a.seed}").copy()
        s["time_step"] = s["time_step"] + i * a.lag
        add.append(s[s.time_step <= T])
    add = pd.concat(add).groupby(keys + ["time_step"], as_index=False)["loss"].sum()
    m = lag.merge(add, on=keys + ["time_step"], how="outer", suffixes=("_lag", "_add")).fillna(0.0)
    m["excess"] = m.loss_lag - m.loss_add
    tot_lag, tot_add = m.loss_lag.sum(), m.loss_add.sum()
    print(f"network {a.seed}, d = {a.d}, lag {a.lag}: run {tot_lag / 1e6:.3f} mUSD, shifted singles "
          f"{tot_add / 1e6:.3f} (to day {T}), excess {(tot_lag - tot_add) / 1e6:.3f} mUSD ({100 * (tot_lag / tot_add - 1):.1f} %)")
    starts = [1 + i * a.lag for i in range(3)]
    ends = [s + a.d - 1 for s in starts]
    by_t = m.groupby("time_step")[["loss_lag", "loss_add", "excess"]].sum()
    windows = [("before event 2", 0, starts[1] - 1), ("event 2 to start of event 3", starts[1], starts[2] - 1),
               ("event 3", starts[2], ends[2]), (f"days {ends[2] + 1}-{ends[2] + 30}", ends[2] + 1, ends[2] + 30),
               (f"after day {ends[2] + 30}", ends[2] + 31, T)]
    print("  excess by period (mUSD): " + "; ".join(
        f"{lab} {by_t.loc[(by_t.index >= lo) & (by_t.index <= hi), 'excess'].sum() / 1e6:.3f}" for lab, lo, hi in windows))
    print(f"  keys: {keys}")
    g = m.groupby(keys)[["loss_lag", "loss_add", "excess"]].sum().sort_values("excess", ascending=False) / 1e6
    print(f"  top {a.top} sources of excess (mUSD):")
    print(g.head(a.top).round(3).to_string())
    print(f"  most negative: {g.tail(3).round(3).to_string()}")
    if len(keys) > 1:
        for k in keys:
            gk = m.groupby(k)[["loss_lag", "loss_add", "excess"]].sum().sort_values("excess", ascending=False) / 1e6
            print(f"  by {k}, top 6:")
            print(gk.head(6).round(3).to_string())


if __name__ == "__main__":
    main()
