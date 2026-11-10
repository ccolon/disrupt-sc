"""SI figure of the Cambodia paper (evidence E_settle): every run's daily loss falls back below 1 % of its peak before
the run's horizon (9 Nov 2026 draft; paper style 10 Nov).

Settling day = last day the daily household loss is above 1 % of its peak (read_batch.py / read_pairs.py / read_rob.py,
column settle_day). Horizon rule (A_settle): a run is long enough when 1.2 x settling day <= horizon; lags above 2d run
to day 180. Inputs: the runs tables of the grid, pair, robustness and transition batches. Puts the numbers of the
settling paragraph; draws settling day against the run's horizon, one column of points per batch.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from paper import BASIN_COLOR, DUR_COLOR, GRID, INK, PAIR, ROB, TAX, TRANS, WIDTH, count, num, save

BATCHES = [  # label, table, colour
    ("grid, 4-day closures", GRID[4], DUR_COLOR[4]),
    ("grid, 8-day closures", GRID[8], DUR_COLOR[8]),
    ("grid, 12-day closures", GRID[12], DUR_COLOR[12]),
    ("two floods", PAIR, INK),
    ("robustness", ROB, BASIN_COLOR["saigon"]),   # aqua: the grid takes the blue ramp
    ("carbon tax", TRANS, TAX),
]


def make(I, out, N):
    R = pd.concat([I.csv(f).assign(batch=lab) for lab, f, _ in BATCHES], ignore_index=True)
    R["rule_ok"] = 1.2 * R.settle_day <= R.t_final
    short = R[R.t_final == R.t_final.min()]
    late = short.loc[short.settle_day.idxmax()]
    N.put("SettleRuns", count(len(R)), "runs checked for settling (grid, two-flood, robustness and transition batches)")
    N.put("Horizon", str(int(R.t_final.min())), "days, horizon of the runs (A_settle)")
    N.put("HorizonLong", str(int(R.t_final.max())), "days, horizon of the runs whose lags exceed twice the closure")
    N.put("SettleLatest", str(int(late.settle_day)), f"latest settling day of a {int(late.t_final)}-day run ({late.run})")
    N.put("SettleRuleDay", num(R.t_final.min() / 1.2, 0), "the rule's latest settling day for that horizon (1/1.2)")
    N.put("SettleOutside", str(int((~R.rule_ok).sum())), "runs settling later than the rule allows")
    N.put("SettleLastDayMax", num(R.last_day_pct_peak.max(), 2), "% of its peak: the largest daily loss on a run's "
          "last day")

    fig, ax = plt.subplots(figsize=(WIDTH["onehalf"], 70 / 25.4))
    labs = [b[0] for b in BATCHES]
    shift = {lab: (i - (len(labs) - 1) / 2) * 3.0 for i, lab in enumerate(labs)}
    for lab, _, col in BATCHES:
        x = R[R.batch == lab]
        ax.scatter(x.t_final + shift[lab], x.settle_day, s=5, color=col, alpha=0.6, linewidths=0,
                   label=f"{lab} ({len(x)} runs)")
    for t in sorted(R.t_final.unique()):
        ax.hlines(t / 1.2, t - 10, t + 10, color=INK, lw=0.9)
        ax.text(t + 11, t / 1.2, f"limit {t / 1.2:.0f}", va="center", fontsize=6.5)
    bad = R[~R.rule_ok]
    if len(bad):
        ax.scatter(bad.t_final + bad.batch.map(shift), bad.settle_day, s=30, facecolor="none", edgecolor=INK, lw=0.8,
                   label="later than the limit")
    ax.set(xlabel="horizon of the run (days)", ylabel="settling day", xticks=sorted(R.t_final.unique()),
           xlim=(95, 210), ylim=(0, None))
    ax.legend(loc="upper left", fontsize=6.5, ncol=2)
    ax.set_title("Day after which the daily loss stays below 1 % of its peak", loc="left", fontsize=8)
    fig.tight_layout()
    return save(fig, out, "figS_settle")
