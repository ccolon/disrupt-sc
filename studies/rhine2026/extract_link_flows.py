"""Compact tables from a link-level (full-export) run, written on the cluster so that the 8-10 GB link table and
the 2-3 GB inventory table can stay there (30 Sep 2026; review points EC6, EC4 and the French chains).

1. link_flows_disrupted.csv.gz - deliveries by week and by chain (seller region and sector -> buyer region and
   sector, cargo class) for the buyers of the countries of interest, restricted to the chains that lose more than
   1 % of their baseline delivery in at least one week: realized delivery, what the supplier offered (the gap to the
   baseline offer is rationing by a supplier that lost inputs or output), what transport withheld (offered minus
   realized), the capacity gate's part, the pipelined part, and the delivered-value weighted price ratio.
2. price_by_cargo.csv - delivered-price ratio (price over baseline price) of the routed deliveries, by week and
   cargo class, all buyers: value-weighted mean, median, ninth decile and maximum, and the share of the delivered
   value that pays more than 1 % above its baseline price.
3. inventory_trace.csv - days of cover by week, buying sector and input product for the firms of --stock-region
   (need-weighted mean of inventory_days), for the stock level at the onset of each wave.

Usage (postprocess of a --full-export job, see cluster/launch_rhine_batch.sh):
    python studies/rhine2026/extract_link_flows.py <run_folder> [--buyers DEU,FRA,NLD,AUT,CHE,BEL,ESP,CZE]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

KEY = ["seller_region", "seller_sector", "buyer_region", "buyer_sector", "cargo_type"]
COLS = ["time_step"] + KEY + ["buyer_type", "realized_delivery", "delivery_offered", "capacity_blocked",
                              "pipelined_delivery", "eq_price", "price"]
CHUNK = 2_000_000


def link_tables(run: Path, buyers: set[str]):
    flows = None
    prices = []            # per chunk: (time_step, cargo, ratio, value) of routed deliveries, thinned
    have = pd.read_csv(run / "link_data.csv", nrows=1).columns
    cols = [c for c in COLS if c in have]
    for ch in pd.read_csv(run / "link_data.csv", usecols=cols, chunksize=CHUNK,
                          dtype={"seller_region": str, "seller_sector": str, "buyer_region": str, "buyer_sector": str,
                                 "cargo_type": str}):
        for c in ("capacity_blocked", "pipelined_delivery", "delivery_offered"):
            if c not in ch:
                ch[c] = 0.0
        ch["cargo_type"] = ch["cargo_type"].fillna("")
        ch["buyer_sector"] = ch["buyer_sector"].fillna(ch.get("buyer_type", "")).replace("", "final")
        ch["value"] = ch["realized_delivery"] * ch["eq_price"]
        ch["paid"] = ch["realized_delivery"] * ch["price"]
        routed = ch[(ch["cargo_type"] != "") & (ch["realized_delivery"] > ch["pipelined_delivery"] + 1e-9)]
        if len(routed):
            r = pd.DataFrame({"time_step": routed["time_step"].to_numpy(), "cargo_type": routed["cargo_type"].to_numpy(),
                              "ratio": (routed["price"] / routed["eq_price"]).to_numpy(), "value": routed["value"].to_numpy()})
            prices.append(r[r["value"] > 1e-4])
        sub = ch[ch["buyer_region"].isin(buyers)]
        g = sub.groupby(["time_step"] + KEY, observed=True)[["realized_delivery", "delivery_offered", "capacity_blocked",
                                                              "pipelined_delivery", "value", "paid"]].sum()
        flows = g if flows is None else flows.add(g, fill_value=0.0)
    return flows.reset_index(), pd.concat(prices, ignore_index=True)


def weighted_quantile(x: np.ndarray, w: np.ndarray, q: float) -> float:
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return float(x[o][np.searchsorted(cw, q * cw[-1])])


def main(run: Path, buyers: set[str], stock_region: str):
    flows, prices = link_tables(run, buyers)
    base = flows[flows.time_step == 0].set_index(KEY)[["realized_delivery", "delivery_offered"]]
    base.columns = ["base_realized", "base_offered"]
    f = flows.join(base, on=KEY)
    f = f[f["base_realized"] > 0.05]
    f["shortfall_share"] = (f["base_realized"] - f["realized_delivery"]) / f["base_realized"]
    hit = f.groupby(KEY)["shortfall_share"].max()
    keep = hit[hit > 0.01].index
    f = f.set_index(KEY).loc[lambda d: d.index.isin(keep)].reset_index()
    f["withheld_by_transport"] = (f["delivery_offered"] - f["realized_delivery"]).clip(lower=0)
    f["price_ratio"] = np.where(f["value"] > 0, f["paid"] / f["value"], np.nan)
    out = f[["time_step"] + KEY + ["base_realized", "realized_delivery", "delivery_offered", "withheld_by_transport",
                                   "capacity_blocked", "pipelined_delivery", "price_ratio"]].round(4)
    out.to_csv(run / "link_flows_disrupted.csv.gz", index=False, compression="gzip")
    print(f"link_flows_disrupted.csv.gz: {len(out):,} rows, {len(keep):,} disrupted chains of {len(hit):,} "
          f"for buyers in {sorted(buyers)}")

    rows = []
    for (t, ct), g in prices.groupby(["time_step", "cargo_type"]):
        x, w = g["ratio"].to_numpy(), g["value"].to_numpy()
        rows.append({"time_step": t, "cargo_type": ct, "delivered_value": w.sum(),
                     "ratio_mean": float(np.average(x, weights=w)), "ratio_median": weighted_quantile(x, w, 0.5),
                     "ratio_p90": weighted_quantile(x, w, 0.9), "ratio_max": float(x.max()),
                     "share_value_above_1pct": float(w[x > 1.01].sum() / w.sum())})
    pd.DataFrame(rows).round(4).to_csv(run / "price_by_cargo.csv", index=False)
    print(f"price_by_cargo.csv: {len(rows)} rows")

    inv = run / "inventory_data.csv"
    if inv.exists():
        ft = json.load(open(run / "firm_table.geojson", encoding="utf-8"))
        meta = pd.DataFrame([{"firm": f_["properties"]["id"], "region": f_["properties"].get("region"),
                              "sector": f_["properties"].get("sector")} for f_ in ft["features"]]).set_index("firm")
        ids = set(meta[meta.region == stock_region].index)
        acc = None
        for ch in pd.read_csv(inv, chunksize=CHUNK):
            ch = ch[ch["firm"].isin(ids)]
            if ch.empty:
                continue
            ch["buyer_sector"] = ch["firm"].map(meta["sector"])
            ch["input"] = ch["input_sector"].astype(str).str.split("_", n=1).str[-1]
            ch["need_days"] = ch["eq_need"] * ch["inventory_days"]
            g = ch.groupby(["time_step", "buyer_sector", "input"])[["eq_need", "need_days", "inventory_qty"]].sum()
            acc = g if acc is None else acc.add(g, fill_value=0.0)
        acc = acc.reset_index()
        acc["days_of_cover"] = np.where(acc["eq_need"] > 0, acc["need_days"] / acc["eq_need"], np.nan)
        acc[["time_step", "buyer_sector", "input", "eq_need", "inventory_qty", "days_of_cover"]].round(4).to_csv(
            run / "inventory_trace.csv", index=False)
        print(f"inventory_trace.csv: {len(acc):,} rows for the firms of {stock_region}")
    else:
        print("no inventory_data.csv in the run: inventory_trace.csv not written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--buyers", default="DEU,FRA,NLD,AUT,CHE,BEL,ESP,CZE")
    ap.add_argument("--stock-region", default="DEU")
    a = ap.parse_args()
    main(Path(a.run), set(a.buyers.split(",")), a.stock_region)
