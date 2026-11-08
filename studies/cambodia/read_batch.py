"""Read a batch of Cambodia paper runs (one folder per run, as copied by cluster/launch_cambodia.sh).

Per run: the total household loss (loss_summary.csv), the daily loss (loss_per_region_sector_time.csv summed over
sectors), the cumulative loss at fixed horizons, the peak, the settling day (last day the daily loss is above 1 % of
its peak, the E_settle criterion) and the share of the loss after day 120. Then the pilot's checks: lag0 == simul
(determinism), simultaneous / sum of singles per network (H1), the lag curve per network (H2), restoration 4 vs 30
days on lags d and d + 1 (back-to-back and a one-day gap). The closure length d and the lags are read from the batch
(one d per batch), so the same reader serves the d = 12 pilot and the d = 8 settling runs.

Usage: python studies/cambodia/read_batch.py <batch folder> [--out <folder>] [--no-figure]
Writes <out>/runs.csv (one row per run), <out>/daily.csv (daily loss, one column per run) and <out>/pilot_read.png;
<out> defaults to <batch folder>/analysis.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HORIZONS = (30, 60, 90, 120, 150, 180)
SINGLES = ("single_saigon", "single_mekong", "single_tonle")


def restoration_of(folder: Path) -> float:
    text = (folder / "parameters.yaml").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^inventory_restoration_time:\s*([0-9.]+)", text, re.M)
    return float(m.group(1)) if m else float("nan")


def read_run(folder: Path):
    sr = json.loads((folder / "study_run.json").read_text(encoding="utf-8"))
    total = pd.read_csv(folder / "loss_summary.csv").iloc[0]
    lt = pd.read_csv(folder / "loss_per_region_sector_time.csv")
    daily = lt.groupby("time_step")["loss"].sum().sort_index()
    cum = daily.cumsum()
    peak = float(daily.max())
    above = daily[daily > 0.01 * peak]
    rec = dict(run=folder.name, scenario=sr["scenario"], seed=int(sr["seed"]), duration=int(sr["duration"]),
               restoration=restoration_of(folder), t_final=int(sr["t_final"]), sha=str(sr.get("sha", ""))[:7],
               starts=",".join(str(d["start_time"]) for d in sr.get("disruptions", [])),
               loss_households=float(total["households"]), loss_countries=float(total["countries"]),
               loss_daily_sum=float(daily.sum()), peak=peak, t_peak=int(daily.idxmax()),
               settle_day=int(above.index.max()) if peak > 0 else 0,
               last_day_pct_peak=100 * float(daily.iloc[-1]) / peak if peak > 0 else 0.0,
               share_after_120=float(daily[daily.index > 120].sum() / daily.sum()) if daily.sum() else 0.0,
               min_daily=float(daily.min()))
    for h in HORIZONS:
        rec[f"cum_{h}"] = float(cum[cum.index <= h].iloc[-1])
    return rec, daily


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--out")
    ap.add_argument("--no-figure", action="store_true")
    a = ap.parse_args()
    batch = Path(a.batch)
    out = Path(a.out) if a.out else batch / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    recs, dailies = [], {}
    for f in sorted(p for p in batch.iterdir() if (p / "study_run.json").exists()):
        rec, daily = read_run(f)
        recs.append(rec)
        dailies[f.name] = daily
    df = pd.DataFrame(recs)
    D = pd.DataFrame(dailies)
    df.to_csv(out / "runs.csv", index=False)
    D.to_csv(out / "daily.csv", index_label="time_step")
    pd.set_option("display.width", 200)
    m = 1e6  # model units are USD (paper_config monetary_units_in_model); tables in million USD

    print(f"{len(df)} runs; code {sorted(df.sha.unique())}; t_final {sorted(df.t_final.unique())}; "
          f"restoration {sorted(df.restoration.unique())}")
    rel = (df.loss_households - df.loss_daily_sum).abs() / df.loss_households.abs().clip(lower=1e-9)
    print(f"loss_summary households vs sum of daily losses: max relative difference {rel.max():.2e}")
    print(f"negative daily losses: {int((df.min_daily < 0).sum())} runs (lowest {df.min_daily.min():.3g} USD)")

    base = df[df.restoration == 30].set_index(["scenario", "seed"])
    seeds = sorted(df.seed.unique())
    durations = sorted(df.duration.unique())
    if len(durations) != 1:
        raise SystemExit(f"one closure length per batch expected, found {durations}")
    d = int(durations[0])
    LAGS = sorted(int(s[3:]) for s in df.scenario.unique() if s.startswith("lag"))
    print(f"closure length d = {d}; lags {LAGS}")
    # The grid has no "simul" runs: lag0 is the same scenario (identical daily losses in every pilot network).
    SIM = "simul" if "simul" in set(df.scenario) else "lag0"
    if SIM == "lag0":
        print("no simul runs in this batch: lag0 stands for the simultaneous scenario")
    else:
        print("\n== Determinism: lag0 vs simul (daily series, restoration 30)")
        for s in seeds:
            r0 = base.loc[("lag0", s), "run"]
            rs = base.loc[("simul", s), "run"]
            diff = (D[r0] - D[rs]).abs().max()
            print(f"  seed {s}: total lag0 {base.loc[('lag0', s), 'loss_households'] / m:.4f} vs simul "
                  f"{base.loc[('simul', s), 'loss_households'] / m:.4f} mUSD; max daily |diff| {diff:.3g} USD")

    print("\n== Settling (restoration 30): last day above 1 % of peak; daily loss on day 180 in % of peak; "
          "share of the loss after day 120")
    st = df[df.restoration == 30].groupby("scenario")[["settle_day", "last_day_pct_peak", "share_after_120"]]
    print(st.agg(["min", "max"]).round(3).to_string())
    late = df[(df.settle_day > 150)]
    print(f"  runs still above 1 % of peak after day 150: {len(late)}"
          + ("" if late.empty else " -> " + ", ".join(late.run)))

    print("\n== H1: simultaneous / sum of the three singles, by horizon (restoration 30)")
    for h in ("cum_60", "cum_90", "cum_120", "loss_households"):
        rat = [base.loc[(SIM, s), h] / sum(base.loc[(x, s), h] for x in SINGLES) for s in seeds]
        print(f"  {h:16s} per seed {np.round(rat, 3).tolist()} mean {np.mean(rat):.3f} "
              f"min {np.min(rat):.3f} max {np.max(rat):.3f}")
    for s in seeds:
        print(f"  seed {s}: singles " + ", ".join(f"{x[7:]} {base.loc[(x, s), 'loss_households'] / m:.3f}"
                                                  for x in SINGLES)
              + f"; sum {sum(base.loc[(x, s), 'loss_households'] for x in SINGLES) / m:.3f}; "
              f"{SIM} {base.loc[(SIM, s), 'loss_households'] / m:.3f} mUSD")

    print(f"\n== H2: lag curve, total household loss over the run (t_final {sorted(int(x) for x in df.t_final.unique())}; mUSD, "
          f"restoration 30); lag = days between event starts, d = {d} (lag {d} = back-to-back)")
    tab = pd.DataFrame({L: [base.loc[(f"lag{L}", s), "loss_households"] / m for s in seeds] for L in LAGS},
                       index=[f"seed {s}" for s in seeds])
    tab["singles sum"] = [sum(base.loc[(x, s), "loss_households"] for x in SINGLES) / m for s in seeds]
    print(tab.round(3).to_string())
    norm = tab[list(LAGS)].div(tab["singles sum"], axis=0)
    print("  as a ratio to the sum of singles:")
    print(norm.round(3).to_string())
    print("  mean ratio " + ", ".join(f"lag {L}: {norm[L].mean():.3f}" for L in LAGS))
    if d in tab and d + 1 in tab:
        gap1 = 100 * (tab[d + 1] / tab[d] - 1)
        print(f"  lag{d + 1} vs lag{d} (paired, %): {np.round(gap1.values, 2).tolist()}")

    r4 = df[df.restoration == 4].set_index(["scenario", "seed"])
    if not r4.empty:
        print(f"\n== Restoration 4 days vs 30 days, lags {d} and {d + 1} (mUSD)")
        for L in (d, d + 1):
            print(f"  lag{L}: r30 {[round(float(base.loc[(f'lag{L}', s), 'loss_households']) / m, 3) for s in seeds]}"
                  f"  r4 {[round(float(r4.loc[(f'lag{L}', s), 'loss_households']) / m, 3) for s in seeds if (f'lag{L}', s) in r4.index]}")
        d4 = [100 * (r4.loc[(f'lag{d + 1}', s), 'loss_households'] / r4.loc[(f'lag{d}', s), 'loss_households'] - 1)
              for s in seeds if (f'lag{d + 1}', s) in r4.index and (f'lag{d}', s) in r4.index]
        print(f"  restoration 4: lag{d + 1} vs lag{d} (paired, %): {np.round(d4, 2).tolist()}")
        print("  restoration 4 settling: " + ", ".join(f"{r.run}: day {r.settle_day}, day-180 {r.last_day_pct_peak:.2f} % of peak"
                                                         for r in df[df.restoration == 4].itertuples()))

    if a.no_figure:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for s in seeds:
        ax[0].plot(LAGS, tab.loc[f"seed {s}", list(LAGS)], color="0.7", lw=0.8, marker="o", ms=3)
    ax[0].plot(LAGS, tab[list(LAGS)].mean(), color="C0", lw=2, marker="o", label="mean of 5 networks")
    ax[0].axhline(tab["singles sum"].mean(), color="C3", ls="--", label="sum of single-basin losses (mean)")
    ax[0].axvline(d, color="0.5", ls=":", lw=0.8)
    ax[0].set(xlabel=f"days between event starts (d = {d})", ylabel="household loss to day 180 (mUSD)",
              title="Lag curve (grey: networks)")
    ax[0].legend(fontsize=8)
    present = set(df[df.restoration == 30].scenario)
    for sc in [x for x in (SIM, f"lag{d // 2}", f"lag{d}", f"lag{d + 1}", f"lag{2 * d}", f"lag{3 * d}")
               if x in present]:
        cols = [base.loc[(sc, s), "run"] for s in seeds]
        ax[1].plot(D.index, D[cols].mean(axis=1) / 1e3, lw=1, label=sc)
    ax[1].set(xlabel="day", ylabel="daily household loss (kUSD, mean of networks)", title="Daily loss")
    ax[1].legend(fontsize=8)
    for sc in [x for x in (SIM, f"lag{d}", f"lag{max(LAGS)}", "single_tonle") if x in present]:
        cols = [base.loc[(sc, s), "run"] for s in seeds]
        c = D[cols].cumsum()
        ax[2].plot(D.index, (c / c.iloc[-1]).mean(axis=1), lw=1, label=sc)
    ax[2].set(xlabel="day", ylabel="share of the day-180 loss", title="Cumulative loss")
    ax[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "pilot_read.png", dpi=110)
    print(f"\nfigure: {out / 'pilot_read.png'}")


if __name__ == "__main__":
    main()
