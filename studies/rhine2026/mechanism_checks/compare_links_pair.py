"""Link-level comparison of two ten-week runs with full exports (14 Sep 2026).

usage: python compare_links_pair.py <runA> <runB> [weeks, default 5,6,7,8,9] [links table, default lh_links.csv]

Per week and link: order, delivery (after the supplier's rationing), realized delivery (after transport).
Routing loss = delivery - realized; rationing = order - delivery. Links are flagged by their baseline route
(crosses Kaub / Lower Rhine / upstream Rhine) from link_route_flags.csv; when lh_links.csv exists the
predicted outcome of the line-haul rule (gives_up / delivers_same / delivers_free) is added for the
Kaub-crossing bulk links.
"""
import os
import sys

import pandas as pd

pd.set_option("display.width", 250)
RUNS = "C:/dsc_runs/rhine2026"
SC = "C:/Users/Celian/AppData/Local/Temp/claude/C--Users-Celian-OneDrive-DisruptSC-disrupt-sc/4f7de379-fbf0-473c-a0e9-89231404ca2d/scratchpad"
run_a, run_b = sys.argv[1], sys.argv[2]
weeks = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "5,6,7,8,9").split(",")]

cols = ["time_step", "seller_id", "buyer_id", "seller_region", "seller_sector", "buyer_region", "buyer_sector",
        "order", "delivery", "realized_delivery", "cargo_type", "price", "eq_price"]
dt = {"seller_id": str, "buyer_id": str}


def load(run):
    parts = []
    for chunk in pd.read_csv(f"{RUNS}/{run}/link_data.csv", usecols=cols, dtype=dt, chunksize=3_000_000):
        parts.append(chunk[chunk.time_step.isin(weeks)])
    d = pd.concat(parts)
    d["routing_loss"] = (d["delivery"] - d["realized_delivery"]).clip(lower=0)
    d["rationing"] = (d["order"] - d["delivery"]).clip(lower=0)
    return d


a = load(run_a)
b = load(run_b)
flags = pd.read_csv(f"{SC}/link_route_flags.csv", dtype=str).drop_duplicates(["seller_id", "buyer_id"])
key = ["time_step", "seller_id", "buyer_id"]
m = a.merge(b, on=key, suffixes=("_a", "_b"), how="outer")
m = m.merge(flags[["seller_id", "buyer_id", "crosses_kaub", "uses_lower_rhine", "uses_upstream_rhine"]], on=["seller_id", "buyer_id"], how="left")
m["group"] = "other"
m.loc[m["uses_lower_rhine"] == "True", "group"] = "lower_rhine_only"
m.loc[m["uses_upstream_rhine"] == "True", "group"] = "upstream_only"
m.loc[m["crosses_kaub"] == "True", "group"] = "crosses_kaub"
lh_path = sys.argv[4] if len(sys.argv) > 4 else f"{SC}/lh_links.csv"
if os.path.exists(lh_path):
    lh = pd.read_csv(lh_path, dtype=str).drop_duplicates(["seller_id", "buyer_id"])
    m = m.merge(lh[["seller_id", "buyer_id", "outcome", "base_road"]], on=["seller_id", "buyer_id"], how="left")
    m["outcome"] = m["outcome"].fillna("-")
else:
    m["outcome"] = "-"

print(f"A = {run_a}, B = {run_b}")
for t in weeks:
    w = m[m.time_step == t]
    print(f"\n==================== week {t} ====================")
    tot = pd.DataFrame({
        "order_A": w.groupby("group")["order_a"].sum(), "realized_A": w.groupby("group")["realized_delivery_a"].sum(),
        "realized_B": w.groupby("group")["realized_delivery_b"].sum(),
        "routing_loss_A": w.groupby("group")["routing_loss_a"].sum(), "routing_loss_B": w.groupby("group")["routing_loss_b"].sum(),
        "rationing_A": w.groupby("group")["rationing_a"].sum(), "rationing_B": w.groupby("group")["rationing_b"].sum(),
    }).round(0)
    print(tot.to_string())
    cb = w[w.cargo_type_a.isin(["liquid_bulk", "dry_bulk"]) & (w.group == "crosses_kaub")]
    by = pd.DataFrame({"delivery_A": cb.groupby(["cargo_type_a", "outcome"])["delivery_a"].sum(),
                       "routing_loss_A": cb.groupby(["cargo_type_a", "outcome"])["routing_loss_a"].sum(),
                       "delivery_B": cb.groupby(["cargo_type_a", "outcome"])["delivery_b"].sum(),
                       "routing_loss_B": cb.groupby(["cargo_type_a", "outcome"])["routing_loss_b"].sum(),
                       "n_links": cb.groupby(["cargo_type_a", "outcome"])["order_a"].size()}).round(0)
    print("-- Kaub-crossing bulk by cargo and predicted line-haul outcome --")
    print(by.to_string())
    d = w.assign(d_rl=w["routing_loss_a"] - w["routing_loss_b"])
    worse = d[d.d_rl > 1e-6]
    print(f"-- links with MORE routing loss in A than B: {len(worse)} links, {worse.d_rl.sum():,.0f} mUSD; by group: "
          f"{worse.groupby('group')['d_rl'].sum().round(0).to_dict()}; by cargo: {worse.groupby('cargo_type_a')['d_rl'].sum().round(0).to_dict()}")
    better = d[d.d_rl < -1e-6]
    print(f"-- links with LESS routing loss in A than B: {len(better)} links, {-better.d_rl.sum():,.0f} mUSD; by group: "
          f"{better.groupby('group')['d_rl'].sum().round(0).to_dict()}; by cargo: {better.groupby('cargo_type_a')['d_rl'].sum().round(0).to_dict()}")
    print(better.sort_values("d_rl").head(6)[["seller_id", "seller_region_a", "seller_sector_a", "buyer_region_a", "buyer_sector_a", "cargo_type_a", "group", "outcome", "order_a", "delivery_a", "realized_delivery_a", "realized_delivery_b", "price_a", "price_b"]].to_string())
    pr = w[(w.price_a - w.price_b).abs() > 1e-9]
    if len(pr):
        print(f"-- links with different prices: {len(pr)}; mean price ratio A/B on them {(pr.price_a / pr.price_b).mean():.3f}")
    # delivered Kaub-crossing bulk in B: price increase distribution (freight passed into the price)
    db = cb[cb.realized_delivery_b > 1e-9]
    if len(db):
        ratio = (db.price_b / db.eq_price_b)
        print(f"-- Kaub-crossing bulk delivered in B: {len(db)} links, {db.realized_delivery_b.sum():,.0f} mUSD; price/eq_price quantiles "
              f"{ratio.quantile([0.1, 0.5, 0.9]).round(3).to_dict()}; by outcome: {db.groupby('outcome')['realized_delivery_b'].sum().round(0).to_dict()}")
