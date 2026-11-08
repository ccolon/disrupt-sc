"""Read a two-flood batch (pair_<a>_<b>_tau<T> runs) into <batch>/analysis/runs.csv and daily.csv (8 Nov 2026).

Per run the same record as read_batch.py (total household loss, settling day, cumulative loss at fixed horizons...),
plus the pair's basins and tau = start of b - start of a (tau < 0: b first). The additive baseline, the single-basin
runs, is in the grid batch of the same networks and closure length (grid_d12_20261108).

Usage: python studies/cambodia/read_pairs.py <pair batch> [--out <folder>]
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from read_batch import read_run  # noqa: E402
from scenarios import parse_pair  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    out = a.out or a.batch / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    recs, dailies = [], {}
    for f in sorted(p for p in a.batch.iterdir() if (p / "study_run.json").exists()):
        rec, daily = read_run(f)
        rec["basin_a"], rec["basin_b"], rec["tau"] = parse_pair(rec["scenario"])
        recs.append(rec)
        dailies[f.name] = daily
    df = pd.DataFrame(recs)
    df.to_csv(out / "runs.csv", index=False)
    pd.DataFrame(dailies).to_csv(out / "daily.csv", index_label="time_step")
    rel = (df.loss_households - df.loss_daily_sum).abs() / df.loss_households.abs().clip(lower=1e-9)
    print(f"{len(df)} runs; networks {sorted(df.seed.unique())}; d {sorted(df.duration.unique())}; "
          f"tau {sorted(df.tau.unique())}; t_final {sorted(int(x) for x in df.t_final.unique())}")
    print(f"accounting: max relative difference {rel.max():.2e}; negative daily losses {int((df.min_daily < 0).sum())}")
    for t in sorted(df.t_final.unique()):
        x = df[df.t_final == t]
        print(f"runs to day {t}: latest settling day {x.settle_day.max()} ({x.loc[x.settle_day.idxmax(), 'run']}); "
              f"daily loss on the last day max {x.last_day_pct_peak.max():.3f} % of peak")
    print(f"written: {out / 'runs.csv'}, {out / 'daily.csv'}")


if __name__ == "__main__":
    main()
