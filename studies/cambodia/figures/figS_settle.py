"""SI figure of the Cambodia paper (node E_settle): every run's daily loss falls back below 1 % of its peak before the
run's horizon (9 Nov 2026, draft).

Settling day = last day the daily household loss is above 1 % of its peak (read_batch.py, column settle_day). Horizon
rule (A_settle): a run is long enough when 1.2 x settling day <= horizon; lags above 2d run to day 180.
Inputs: the runs tables of the batches (read_batch.py / read_pairs.py / read_rob.py analysis/runs.csv), given as
label=path. Prints, per batch and horizon, the runs, the latest settling day and its run, the largest daily loss on
the last day in % of the peak, and the runs outside the rule; draws settling day against the run's horizon.

Usage: python studies/cambodia/figures/figS_settle.py --out <folder> grid_d12=<csv> grid_d8=<csv> ...
"""
import argparse
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tables", nargs="+", help="label=path of a runs.csv")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    frames = []
    for item in a.tables:
        lab, _, path = item.partition("=")
        x = pd.read_csv(path)
        frames.append(x.assign(batch=lab))
    R = pd.concat(frames, ignore_index=True)
    R["rule_ok"] = 1.2 * R.settle_day <= R.t_final
    print(f"== {len(R)} runs in {R.batch.nunique()} batches")
    for (b, t), x in R.groupby(["batch", "t_final"]):
        late = x.loc[x.settle_day.idxmax()]
        print(f"  {b:>10} to day {t}: {len(x):4d} runs, latest settling day {int(late.settle_day)} ({late.run}), "
              f"last-day loss at most {x.last_day_pct_peak.max():.3f} % of peak, outside the rule {int((~x.rule_ok).sum())}")
    bad = R[~R.rule_ok]
    for _, r in bad.iterrows():
        print(f"  outside the rule: {r.batch} {r.run}: settles on day {int(r.settle_day)} of {int(r.t_final)}, "
              f"last day {r.last_day_pct_peak:.3f} % of peak")
    print(f"  all runs: every daily loss on the last day below {R.last_day_pct_peak.max():.3f} % of its peak")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    batches = list(dict.fromkeys(R.batch))
    shift = {b: (i - (len(batches) - 1) / 2) * 2.2 for i, b in enumerate(batches)}   # side by side per horizon
    for b in batches:
        x = R[R.batch == b]
        ax.scatter(x.t_final + shift[b], x.settle_day, s=8, alpha=0.5, label=f"{b} ({len(x)} runs)")
    bad = bad.assign(x=bad.t_final + bad.batch.map(shift))
    for t in sorted(R.t_final.unique()):
        ax.hlines(t / 1.2, t - 8, t + 8, color="k", lw=1.2)
        ax.text(t + 9, t / 1.2, f"rule: {t / 1.2:.0f}", va="center", fontsize=8)
    if len(bad):
        ax.scatter(bad.x, bad.settle_day, s=60, facecolor="none", edgecolor="r", label="outside the rule")
    ax.set(xlabel="horizon of the run (day)", ylabel="settling day (daily loss last above 1 % of peak)",
           title="Every run settles before its horizon", xlim=(95, 205))
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(a.out / f"figS_settle.{ext}", dpi=200)
    print("figure:", a.out / "figS_settle.png")


if __name__ == "__main__":
    main()
