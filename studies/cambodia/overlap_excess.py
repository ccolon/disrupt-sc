"""The overlap interaction (Q22, 9 Nov 2026): where and how the loss of simultaneous Mekong + Tonle Sap closures exceeds
the sum of the two single closures.

For each network, the pair run at tau 0 against single Mekong + single Tonle Sap; all three close their basins on day
1 for d days, so no shifting is needed. Excess = pair - Mekong - Tonle Sap. Prints, as the mean over networks (and
per network where useful):
1. the household loss split into consumption loss (unmet demand) and extra spending (higher prices), by period;
2. the household loss by sector (loss_per_region_sector_time.csv, households only);
3. the household loss by province: the first two digits of the household's subregion code (household_table.geojson),
   with the province's population-weighted centre;
4. routing (routing_summary.csv): order value served this step by the main route, by an alternative route, or blocked
   (no acceptable route), by cargo type, summed over the closure days;
5. firm production below its day-0 level, by sector (firm_daily.csv), by period.
Writes the per-network tables to --out.

Usage:
  python studies/cambodia/overlap_excess.py --pairs <batch> [--singles <batch>] --seeds 1-10 --d 12
         [--suffix _t116] [--out <folder>]
The pair run is <pairs>/pair_mekong_tonle_tau0_d<d>_s<seed><suffix>; the singles are
<singles>/single_<basin>_d<d>_s<seed><suffix> (default: the pairs batch).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RUNS = {"pair": "pair_mekong_tonle_tau0", "mekong": "single_mekong", "tonle": "single_tonle"}


def ci(x) -> str:
    x = np.asarray(x, float)
    if len(x) < 2:
        return f"{x.mean():.3f}"
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return f"{x.mean():.3f} [{x.mean() - h:.3f}, {x.mean() + h:.3f}]"


def seeds_of(text: str) -> list[int]:
    out = []
    for part in text.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def periods(d: int) -> list[tuple[str, int, int]]:
    return [(f"days 1-{d} (closed)", 1, d), (f"days {d + 1}-{d + 30}", d + 1, d + 30),
            (f"days {d + 31} on", d + 31, 10 ** 6)]


def by_period(s: pd.Series, d: int) -> dict:
    return {lab: float(s.loc[lo:hi].sum()) for lab, lo, hi in periods(d)}


def read_run(folder: Path, provinces: dict | None):
    """The tables of one run, in mUSD (the exports are in USD)."""
    hd = pd.read_csv(folder / "household_data.csv",
                     usecols=["time_step", "household", "consumption_loss", "extra_spending"])
    hd = hd[hd.household.str.startswith("hh_")]
    hd[["consumption_loss", "extra_spending"]] /= 1e6
    loss_total = float(pd.read_csv(folder / "loss_summary.csv").households.iloc[0]) / 1e6
    hh_daily = hd.groupby("time_step")[["consumption_loss", "extra_spending"]].sum()
    if provinces is not None:
        hd = hd.assign(province=hd.household.map(provinces))
        hh_prov = (hd.consumption_loss + hd.extra_spending).groupby(hd.province).sum()
    else:
        hh_prov = None
    lt = pd.read_csv(folder / "loss_per_region_sector_time.csv")
    hh_sector = lt.groupby("sector").loss.sum() / 1e6
    rs = pd.read_csv(folder / "routing_summary.csv")
    usd = [c for c in rs.columns if c.endswith("_usd")]
    rs[usd] /= 1e6
    fd = pd.read_csv(folder / "firm_daily.csv", usecols=["time_step", "sector", "production"])
    prod = fd.pivot(index="time_step", columns="sector", values="production") / 1e6
    shortfall = (prod.loc[0] - prod).clip(lower=0)      # production below day 0, per day and sector
    return dict(loss_total=loss_total, hh_daily=hh_daily, hh_prov=hh_prov, hh_sector=hh_sector, rs=rs,
                shortfall=shortfall)


def provinces_of(folder: Path) -> tuple[dict, pd.DataFrame]:
    feats = json.loads((folder / "household_table.geojson").read_text(encoding="utf-8"))["features"]
    rows = [dict(household=f["properties"]["household"], province=str(f["properties"]["subregion"])[:2],
                 population=f["properties"]["population"], lon=f["geometry"]["coordinates"][0],
                 lat=f["geometry"]["coordinates"][1]) for f in feats]
    t = pd.DataFrame(rows)
    w = t.groupby("province").apply(lambda g: pd.Series({
        "households": len(g), "population": g.population.sum(),
        "lat": np.average(g.lat, weights=g.population), "lon": np.average(g.lon, weights=g.population)}))
    return dict(zip(t.household, t.province)), w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=Path, required=True)
    ap.add_argument("--singles", type=Path)
    ap.add_argument("--seeds", default="1-10")
    ap.add_argument("--d", type=int, default=12)
    ap.add_argument("--suffix", default="_t116")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    singles = a.singles or a.pairs
    seeds = seeds_of(a.seeds)
    out = a.out or a.pairs / "analysis" / "overlap"
    out.mkdir(parents=True, exist_ok=True)

    def folder(kind, s):
        batch = a.pairs if kind == "pair" else singles
        f = batch / f"{RUNS[kind]}_d{a.d}_s{s}{a.suffix}"
        if not (f / "loss_summary.csv").exists():
            raise SystemExit(f"missing run: {f}")
        return f

    prov_map, prov_table = provinces_of(folder("pair", seeds[0]))
    R = {(k, s): read_run(folder(k, s), prov_map) for s in seeds for k in RUNS}

    def excess(get):
        return {s: get(R[("pair", s)]) - get(R[("mekong", s)]) - get(R[("tonle", s)]) for s in seeds}

    print(f"== Overlap interaction: {a.pairs.name} (pairs) and {singles.name} (singles), networks {seeds}, d = {a.d}, "
          f"suffix {a.suffix!r}")
    chk = max(abs(R[(k, s)]["hh_daily"].sum().sum() - R[(k, s)]["loss_total"]) / R[(k, s)]["loss_total"]
              for k in RUNS for s in seeds)
    print(f"  household_data.csv (households only) against loss_summary: max relative difference {chk:.1e}")
    tot = {k: [R[(k, s)]["loss_total"] for s in seeds] for k in RUNS}
    ex = np.array(tot["pair"]) - np.array(tot["mekong"]) - np.array(tot["tonle"])
    base = np.array(tot["mekong"]) + np.array(tot["tonle"])
    print(f"  household loss (mUSD): pair {ci(tot['pair'])}, Mekong {ci(tot['mekong'])}, Tonle Sap {ci(tot['tonle'])}; "
          f"excess {ci(ex)}; ratio {ci((ex + base) / base)}")

    print("\n== 1. Household loss: consumption loss and extra spending, by period (mUSD, mean over networks)")
    rows = []
    for s in seeds:
        for comp in ("consumption_loss", "extra_spending"):
            for k in RUNS:
                for lab, v in by_period(R[(k, s)]["hh_daily"][comp], a.d).items():
                    rows.append(dict(seed=s, component=comp, run=k, period=lab, loss=v))
    T = pd.DataFrame(rows)
    T.to_csv(out / "household_components.csv", index=False)
    P = T.pivot_table(index=["seed", "component", "period"], columns="run", values="loss")
    P["excess"] = P.pair - P.mekong - P.tonle
    for comp in ("consumption_loss", "extra_spending"):
        line = []
        for lab, _, _ in periods(a.d):
            x = P.xs((comp, lab), level=("component", "period"))
            line.append(f"{lab}: pair {x.pair.mean():.2f}, M {x.mekong.mean():.2f}, T {x.tonle.mean():.2f}, "
                        f"excess {ci(x.excess)}")
        print(f"  {comp}:\n    " + "\n    ".join(line))
    xs = P.excess.groupby(level=["seed", "component"]).sum().unstack()
    print(f"  share of the excess that is consumption loss: {ci(xs.consumption_loss / xs.sum(axis=1))}")

    print("\n== 2. Household loss by sector: excess (mUSD, mean over networks), top 12, with the singles' loss")
    S = pd.DataFrame(excess(lambda r: r["hh_sector"])).fillna(0.0)
    S.to_csv(out / "excess_by_household_sector.csv")
    sing = pd.DataFrame({s: R[("mekong", s)]["hh_sector"] + R[("tonle", s)]["hh_sector"] for s in seeds}).fillna(0.0)
    m = S.mean(axis=1).sort_values(ascending=False)
    for sec in m.index[:12]:
        print(f"  {sec:>16}: excess {ci(S.loc[sec])}; singles' sum {sing.loc[sec].mean():.3f}; "
              f"share of the excess {S.loc[sec].sum() / S.sum().sum():.1%}")
    print(f"  sectors with a negative mean excess: {int((m < 0).sum())} (sum {m[m < 0].sum():.3f})")

    print("\n== 3. Household loss by province (code = first two digits of subregion): excess and the singles' sum")
    Q = pd.DataFrame(excess(lambda r: r["hh_prov"])).fillna(0.0)
    Q.to_csv(out / "excess_by_province.csv")
    qs = pd.DataFrame({s: R[("mekong", s)]["hh_prov"] + R[("tonle", s)]["hh_prov"] for s in seeds}).fillna(0.0)
    qp = pd.DataFrame({s: R[("pair", s)]["hh_prov"] for s in seeds}).fillna(0.0)
    pop_share = prov_table.population / prov_table.population.sum()
    order = Q.mean(axis=1).sort_values(ascending=False).index
    for p in order:
        print(f"  {p} ({prov_table.loc[p, 'lat']:.2f} N, {prov_table.loc[p, 'lon']:.2f} E; {int(prov_table.loc[p, 'households'])} "
              f"households, {pop_share[p]:.1%} of population): excess {ci(Q.loc[p])} = "
              f"{Q.loc[p].sum() / Q.sum().sum():.1%} of the excess; pair {qp.loc[p].mean():.2f}, singles {qs.loc[p].mean():.2f}, "
              f"ratio {(qp.loc[p].sum() / qs.loc[p].sum()) if qs.loc[p].sum() > 0 else float('nan'):.2f}")

    print("\n== 4. Routing over the closure days 1-%d (order value served, mUSD summed over days; mean over networks)" % a.d)
    rows = []
    for s in seeds:
        for k in RUNS:
            rs = R[(k, s)]["rs"]
            w = rs[(rs.time_step >= 1) & (rs.time_step <= a.d)].groupby("cargo_type")[
                ["total_usd", "main_usd", "alternative_usd", "blocked_usd", "capacity_blocked_usd"]].sum()
            for cargo, row in w.iterrows():
                rows.append(dict(seed=s, run=k, cargo=cargo, **row.to_dict()))
    G = pd.DataFrame(rows)
    G.to_csv(out / "routing_closure_days.csv", index=False)
    for col in ("alternative_usd", "blocked_usd", "capacity_blocked_usd"):
        g = G.pivot_table(index=["seed", "cargo"], columns="run", values=col, aggfunc="sum").fillna(0.0)
        g["excess"] = g.pair - g.mekong - g.tonle
        print(f"  {col}:")
        for cargo, x in g.groupby(level="cargo"):
            print(f"    {cargo:>24}: pair {x.pair.mean():9.2f}, Mekong {x.mekong.mean():9.2f}, Tonle Sap "
                  f"{x.tonle.mean():9.2f}; pair - singles {ci(x.excess)}")
    tot0 = G[G.run == "pair"].groupby("seed").total_usd.sum().mean()
    print(f"  order value served over the closure days, all cargo, pair run: {tot0:.1f}")

    print("\n== 5. Firm production below day 0, by sector: excess (mUSD, mean over networks), top 12, by period")
    rows = []
    for s in seeds:
        for k in RUNS:
            sf = R[(k, s)]["shortfall"]
            for lab, lo, hi in periods(a.d):
                for sec, v in sf.loc[lo:hi].sum().items():
                    rows.append(dict(seed=s, run=k, period=lab, sector=sec, shortfall=v))
    F = pd.DataFrame(rows)
    F.to_csv(out / "production_shortfall.csv", index=False)
    f = F.pivot_table(index=["seed", "sector", "period"], columns="run", values="shortfall").fillna(0.0)
    f["excess"] = f.pair - f.mekong - f.tonle
    tot_sec = f.excess.groupby(level=["seed", "sector"]).sum().unstack()
    print(f"  total excess shortfall {ci(tot_sec.sum(axis=1))}; singles' sum "
          f"{(f.mekong + f.tonle).groupby(level='seed').sum().mean():.2f}")
    for sec in tot_sec.mean().sort_values(ascending=False).index[:12]:
        parts = "; ".join(f"{lab} {f.excess.xs((sec, lab), level=('sector', 'period')).mean():.3f}"
                          for lab, _, _ in periods(a.d))
        print(f"  {sec:>8}: {ci(tot_sec[sec])} ({parts})")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
