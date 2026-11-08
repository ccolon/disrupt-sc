"""Which firms and inputs make a successive-flood run lose more than its single floods (A_mech, 8 Nov 2026)?

Needs runs made with --keep-firm-data and export_inventory_data=true (batch mech_20261108). For one network: the lag
run against its three single-basin runs, each shifted to its event's start (as in excess_by_source.py), firm by firm.
Production shortfall of a firm = sum over days of (its production on day 0 - its production). Excess = lag run -
shifted singles. Prints the sectors and the firms with the largest excess shortfall, the daily path of the top
sectors in the lag run, and for the top firms the inputs whose stock ran lowest in the lag run, against the singles.

Usage: python studies/cambodia/mech_firms.py <batch> --seed 17 --d 12 --lag 12 [--top 8]
"""
import argparse
from pathlib import Path

import pandas as pd

ORDER = ("single_saigon", "single_mekong", "single_tonle")
FCOLS = ["time_step", "firm", "sector", "production", "production_capacity", "total_order", "rationing",
         "product_stock", "price"]


def folder(batch: Path, name: str) -> Path:
    hits = [p for p in batch.iterdir() if p.name == name or p.name.startswith(name + "_t")]
    if len(hits) != 1:
        raise SystemExit(f"{name}: {len(hits)} folders")
    return hits[0]


def firms(path: Path, shift: int, T: float) -> pd.DataFrame:
    f = pd.read_csv(path / "firm_data.csv", usecols=FCOLS, dtype={"sector": "category"})
    p0 = f[f.time_step == 0].set_index("firm").production
    f["p0"] = p0.reindex(f.firm).to_numpy()
    f["short"] = f.p0 - f.production
    f["time_step"] += shift
    return f[f.time_step <= T]


def inventories(path: Path, shift: int, T: float, keep: set) -> pd.DataFrame:
    out = []
    for c in pd.read_csv(path / "inventory_data.csv", usecols=["time_step", "firm", "input_sector", "inventory_days"],
                         chunksize=5_000_000):
        out.append(c[c.firm.isin(keep)])
    f = pd.concat(out)
    f["time_step"] += shift
    return f[f.time_step <= T]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--d", type=int, required=True)
    ap.add_argument("--lag", type=int, required=True)
    ap.add_argument("--top", type=int, default=8)
    a = ap.parse_args()
    lag_dir = folder(a.batch, f"lag{a.lag}_d{a.d}_s{a.seed}")
    lag = firms(lag_dir, 0, float("inf"))
    T = int(lag.time_step.max())
    single_dirs = [folder(a.batch, f"{sc}_d{a.d}_s{a.seed}") for sc in ORDER]
    singles = [firms(p, i * a.lag, T) for i, p in enumerate(single_dirs)]
    sector = lag.drop_duplicates("firm").set_index("firm").sector
    by = pd.DataFrame({"lag": lag.groupby("firm").short.sum()})
    by["add"] = sum(s.groupby("firm").short.sum() for s in singles).reindex(by.index).fillna(0.0)
    by["excess"] = by["lag"] - by["add"]
    by["sector"] = sector
    by["p0"] = lag[lag.time_step == 0].set_index("firm").production
    print(f"network {a.seed}, d = {a.d}, lag {a.lag}: {len(by)} firms; production shortfall over days 0-{T}: lag run "
          f"{by['lag'].sum() / 1e6:.3f} m, shifted singles {by['add'].sum() / 1e6:.3f} m, excess {by.excess.sum() / 1e6:.3f} m")
    sec = by.groupby("sector", observed=True).agg(firms=("p0", "size"), p0=("p0", "sum"), lag=("lag", "sum"),
                                                 add=("add", "sum"), excess=("excess", "sum"))
    sec["excess_days"] = sec.excess / sec.p0
    sec = sec.sort_values("excess", ascending=False)
    print("\n== sectors by excess shortfall (m; excess_days = excess / sector daily output on day 0)")
    print((sec.assign(p0=sec.p0 / 1e6, lag=sec["lag"] / 1e6, add=sec["add"] / 1e6, excess=sec.excess / 1e6)
           .head(10).round(3).to_string()))
    top_sec = list(sec.index[:4])
    days = [0, 12, 24, 26, 28, 30, 32, 34, 36, 38, 40, 44, 48, 52, 56, 60, 66, 72]
    for s in top_sec:
        x = lag[lag.sector == s].groupby("time_step")[["production", "production_capacity", "total_order",
                                                       "product_stock", "p0"]].sum()
        r = lag[lag.sector == s].groupby("time_step")[["rationing", "price"]].mean()
        t = pd.DataFrame({"prod": x.production / x.p0, "capacity": x.production_capacity / x.p0,
                          "orders": x.total_order / x.p0, "stock_days": x.product_stock / x.p0,
                          "rationing": r.rationing, "price": r.price})
        print(f"\n== {s} in the lag run, ratios to day-0 output (rationing and price: mean over firms)")
        print(t.reindex([d for d in days if d <= T]).round(3).to_string())
    top = by.sort_values("excess", ascending=False).head(a.top)
    print(f"\n== top {a.top} firms by excess shortfall (m)")
    print(top.assign(p0=top.p0 / 1e6, lag=top["lag"] / 1e6, add=top["add"] / 1e6, excess=top.excess / 1e6)
          .round(4).to_string())
    print(f"  share of the total excess: {top.excess.sum() / by.excess.sum():.1%}")
    keep = set(top.index)
    inv_lag = inventories(lag_dir, 0, T, keep)
    inv_add = pd.concat([inventories(p, i * a.lag, T, keep) for i, p in enumerate(single_dirs)])
    lo_lag = inv_lag.loc[inv_lag.groupby(["firm", "input_sector"]).inventory_days.idxmin()]
    lo_add = inv_add.groupby(["firm", "input_sector"]).inventory_days.min().rename("min_days_singles")
    lo = lo_lag.set_index(["firm", "input_sector"]).rename(columns={"inventory_days": "min_days_lag",
                                                                    "time_step": "day_of_min"})
    lo = lo.join(lo_add)
    print("\n== top firms: the 3 inputs with the lowest stock (days of use) in the lag run, against the shifted singles")
    for f in top.index:
        print(f"  firm {f} ({sector[f]}):")
        print(lo.loc[f].sort_values("min_days_lag").head(3).round(3).to_string())
        p = lag[lag.firm == f].set_index("time_step").production / top.p0[f]
        print("    production / day 0 on days " + ", ".join(f"{d}: {p.get(d, float('nan')):.2f}" for d in days if d <= T))


if __name__ == "__main__":
    main()
