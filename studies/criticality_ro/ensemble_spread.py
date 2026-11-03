# -*- coding: utf-8 -*-
"""Per-edge spread of the tier-2 criticality losses across supply-chain
draws (user decision 3 Nov 2026: t2 top-150 x 5 extra seeds).

Reads the baseline ranking results/t2_merged/criticality_ranked.csv (seed
42) and every results/e<seed>_merged/criticality_ranked.csv produced by
``launch_criticality.sh --seeds ...`` (extract each criticality_e<S>_results
.zip at studies/criticality_ro/ first, like the t1/t2 zips). Writes
results/ensemble/criticality_t2_ensemble.csv: one row per edge with the
seed-42 value, the across-seed mean, sd, min, max of total/household/country
loss, and the rank range. The spread measures SUPPLIER-MATCHING uncertainty
(who buys from whom at equal data and parameters), not data uncertainty.

Usage: python studies/criticality_ro/ensemble_spread.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
COLS = ["household_loss", "country_loss", "total_loss"]


def main() -> int:
    runs: dict[str, pd.DataFrame] = {}
    base = RES / "t2_merged" / "criticality_ranked.csv"
    if base.exists():
        runs["s42"] = pd.read_csv(base)
    for p in sorted(RES.glob("e*_merged/criticality_ranked.csv")):
        m = re.fullmatch(r"e(\d+)_merged", p.parent.name)
        if m:
            runs[f"s{m.group(1)}"] = pd.read_csv(p)
    if len(runs) < 2:
        raise SystemExit(f"need the baseline t2 merge plus at least one e<seed> "
                         f"merge under {RES} (found: {sorted(runs)})")
    print(f"{len(runs)} draws: {', '.join(sorted(runs))}")

    long = pd.concat(
        [df.assign(draw=tag)[["draw", "id", "type", "name", "flow_total_tons"]
                             + COLS]
         for tag, df in runs.items()], ignore_index=True)
    long["rank"] = long.groupby("draw")["total_loss"].rank(ascending=False,
                                                           method="min")

    g = long.groupby("id")
    out = g.agg(type=("type", "first"), name=("name", "first"),
                flow_total_tons=("flow_total_tons", "first"),
                n_draws=("draw", "nunique"),
                rank_best=("rank", "min"), rank_worst=("rank", "max"))
    for c in COLS:
        out[f"{c}_mean"] = g[c].mean()
        out[f"{c}_sd"] = g[c].std(ddof=1)
        out[f"{c}_min"] = g[c].min()
        out[f"{c}_max"] = g[c].max()
    if "s42" in runs:
        out = out.join(runs["s42"].set_index("id")[COLS].add_suffix("_s42"))
    out["total_cv"] = out["total_loss_sd"] / out["total_loss_mean"].clip(lower=1e-9)
    out = out.sort_values("total_loss_mean", ascending=False).reset_index()

    dest = RES / "ensemble"
    dest.mkdir(parents=True, exist_ok=True)
    out.to_csv(dest / "criticality_t2_ensemble.csv", index=False)
    print(f"written {dest / 'criticality_t2_ensemble.csv'} ({len(out)} edges)")
    show = out.head(12)[["id", "type", "name", "total_loss_s42",
                         "total_loss_mean", "total_loss_sd", "total_loss_min",
                         "total_loss_max", "rank_best", "rank_worst"]]
    pd.set_option("display.width", 200)
    print("\ntop 12 by mean total loss (mUSD per 4-week closure):")
    print(show.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
