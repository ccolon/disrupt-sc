# Threshold sensitivity of the line-haul rule on the stored candidates (lh_classification.csv), weighted by the
# week-6 orders of lrcheck_base. Candidates are the ones found with access 50 / line-haul 100; the verdict is
# re-applied with other thresholds (approximation: the same-mode search itself would change with the weights).
import pandas as pd

SC = "C:/Users/Celian/AppData/Local/Temp/claude/C--Users-Celian-OneDrive-DisruptSC-disrupt-sc/4f7de379-fbf0-473c-a0e9-89231404ca2d/scratchpad"
THRESHOLD = 5.0
MODES = ["road", "rail", "water", "sea"]
cl = pd.read_csv(f"{SC}/lh_classification.csv")
cl = cl[cl.outcome != "no_baseline"].copy()


def switch(row, cand, access_km, line_haul_km, road_never_line_haul=False):
    for m in MODES:
        b = row[f"base_{m}"]
        k = row.get(f"{cand}_{m}", 0.0)
        if pd.isna(k):
            k = 0.0
        lh = line_haul_km if not (road_never_line_haul and m == "road") else float("inf")
        if b < lh and k - b > access_km:
            return True
    return False


def verdict(row, access_km, line_haul_km, road_never=False):
    best = None
    for cand in ("same", "free"):
        if not row.get(f"{cand}_found", False):
            continue
        cost = row[f"{cand}_cost"]
        pen = 1000.0 if switch(row, cand, access_km, line_haul_km, road_never) else 0.0
        pen += 0.05 if (row[f"{cand}_pen"] % 1000) >= 0.05 else 0.0     # keep the port-switch part as found
        total = cost + pen * row.base_cost
        if best is None or total < best[0]:
            best = (total, cost, pen)
    if best is None:
        return "no_route"
    total, cost, pen = best
    rel = cost / row.base_cost - 1
    return "gives_up" if row.share * (rel + pen) > THRESHOLD else "delivers"


links = pd.read_csv(f"{SC}/lh_links.csv", dtype={"seller_id": str, "buyer_id": str})
keep = set(zip(links.seller_id, links.buyer_id))
parts = []
for chunk in pd.read_csv("C:/dsc_runs/rhine2026/lrcheck_base/link_data.csv", usecols=["time_step", "seller_id", "buyer_id", "order", "cargo_type"],
                         chunksize=3_000_000, dtype={"seller_id": str, "buyer_id": str}):
    c = chunk[chunk.time_step == 6]
    parts.append(c[[(s, b) in keep for s, b in zip(c.seller_id, c.buyer_id)]])
w6 = pd.concat(parts).merge(links[["seller_id", "buyer_id", "o", "d"]], on=["seller_id", "buyer_id"], how="left")
orders = w6.groupby(["o", "d", "cargo_type"])["order"].sum().rename("order6").reset_index()
cl = cl.merge(orders, on=["o", "d", "cargo_type"], how="left")
cl["order6"] = cl.order6.fillna(0)
print(f"{len(cl)} OD pairs, week-6 orders {cl.order6.sum():,.0f} mUSD")
variants = [("current: access 50, line-haul 100", 50, 100, False),
            ("access 90, line-haul 100 (88 km Kaub bypass passes)", 90, 100, False),
            ("access 100, line-haul 100", 100, 100, False),
            ("access 50, line-haul 200", 50, 200, False),
            ("access 50, line-haul 500", 50, 500, False),
            ("access 50, road never line haul for bulk", 50, 100, True),
            ("access 100, road never line haul for bulk", 100, 100, True)]
rows = []
for name, acc, lh, rn in variants:
    v = cl.apply(lambda r: verdict(r, acc, lh, rn), axis=1)
    rows.append(dict(variant=name, pairs_deliver=int((v == "delivers").sum()), pairs_give_up=int((v == "gives_up").sum()),
                     order_delivered=round(cl.order6[v == "delivers"].sum()), order_given_up=round(cl.order6[v == "gives_up"].sum()),
                     share_given_up=round(cl.order6[v == "gives_up"].sum() / cl.order6.sum(), 2)))
print(pd.DataFrame(rows).to_string(index=False))
print("\nold code (penalty-blind free search, set equality): week-6 Kaub bulk undelivered 1,004 of 1,243 mUSD (81 %)")
