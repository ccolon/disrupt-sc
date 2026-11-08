"""Read the robustness batches of the Cambodia paper (R_rob, Q21, 8 Nov 2026) into runs.csv and daily.csv.

Per run the record of read_batch.py, plus the variant read from study_run.json and, for pair runs, the basins and
tau. Variant names:
  - inv<X> for --inventory-scale X;
  - rest<N> for --set inventory_restoration_time=N;
  - base when neither is set.
Prints the checks (accounting, settling by variant and horizon). Then, per variant, the two-flood ratio to the sum of
the two single-basin runs of the same network and variant: mean and 95 % interval, t over the networks.

Usage: python studies/cambodia/read_rob.py <batch> [<batch> ...] [--out <folder>]   (default: <first batch>/analysis)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from read_batch import read_run  # noqa: E402
from scenarios import parse_pair  # noqa: E402

IGNORED = ("export_inventory_data",)   # output switches, not variants


def variant(sr: dict) -> str:
    parts = []
    scale = sr.get("inventory_scale")
    if scale not in (None, 1, 1.0):
        parts.append(f"inv{float(scale):g}")
    for item in sr.get("overrides", []):
        key, _, value = item.partition("=")
        if key == "inventory_restoration_time":
            parts.append(f"rest{float(value):g}")
        elif key not in IGNORED:
            parts.append(item)
    return "+".join(parts) or "base"


def ci(x) -> str:
    x = np.asarray(x, float)
    if len(x) < 2:
        return f"{x.mean():.3f} (n = {len(x)})"
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return f"{x.mean():.3f} [{x.mean() - h:.3f}, {x.mean() + h:.3f}] (n = {len(x)})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batches", type=Path, nargs="+")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    out = a.out or a.batches[0] / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    recs, dailies = [], {}
    for batch in a.batches:
        for f in sorted(p for p in batch.iterdir() if (p / "study_run.json").exists()):
            rec, daily = read_run(f)
            sr = json.loads((f / "study_run.json").read_text(encoding="utf-8"))
            rec["batch"] = batch.name
            rec["variant"] = variant(sr)
            if rec["scenario"].startswith("pair_"):
                rec["basin_a"], rec["basin_b"], rec["tau"] = parse_pair(rec["scenario"])
            recs.append(rec)
            dailies[f.name] = daily
    df = pd.DataFrame(recs)
    df.to_csv(out / "runs.csv", index=False)
    pd.DataFrame(dailies).to_csv(out / "daily.csv", index_label="time_step")
    rel = (df.loss_households - df.loss_daily_sum).abs() / df.loss_households.abs().clip(lower=1e-9)
    print(f"{len(df)} runs in {len(a.batches)} batch(es); code {sorted(df.sha.unique())}; networks "
          f"{sorted(int(s) for s in df.seed.unique())}; d {sorted(int(d) for d in df.duration.unique())}")
    print(f"accounting: max relative difference {rel.max():.2e}; negative daily losses {int((df.min_daily < 0).sum())}")
    print("\n== Settling by variant and horizon (latest settling day; last-day loss in % of peak, max)")
    for (v, t), x in df.groupby(["variant", "t_final"]):
        late = x.loc[x.settle_day.idxmax()]
        print(f"  {v:>8} to day {t}: {len(x)} runs, latest settling day {x.settle_day.max()} ({late.run}), "
              f"last day {x.last_day_pct_peak.max():.3f} %, rule {'ok' if 1.2 * x.settle_day.max() <= t else 'NOT MET'}")
    pairs = df[df.scenario.str.startswith("pair_")]
    if pairs.empty:
        return
    print("\n== Two-flood ratio to the sum of the two singles, per variant (same network, same variant)")
    for v, x in df.groupby("variant"):
        s = x[x.scenario.isin(["single_mekong", "single_tonle"])].pivot(index="seed", columns="scenario",
                                                                         values="loss_households")
        if s.shape[1] < 2:
            continue
        base = s.sum(axis=1)
        print(f"  {v}: singles Mekong {s['single_mekong'].mean() / 1e6:.2f}, Tonle Sap "
              f"{s['single_tonle'].mean() / 1e6:.2f} mUSD")
        p = x[x.scenario.str.startswith("pair_")].pivot(index="seed", columns="tau", values="loss_households")
        for tau in sorted(p.columns):
            r = (p[tau] / base).dropna()
            print(f"    tau {int(tau):+d}: {ci(r)}")
    print(f"\nwritten: {out / 'runs.csv'}, {out / 'daily.csv'}")


if __name__ == "__main__":
    main()
