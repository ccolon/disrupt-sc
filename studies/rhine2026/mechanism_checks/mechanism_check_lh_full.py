# Line-haul rule preview over ALL Kaub-crossing bulk OD pairs (week-6 network state), weighted by the
# week-6/7 orders of lrcheck_base. Writes lh_classification.csv (per OD pair) and prints value shares.
import copy, gc, json, pickle, sys, time
import pandas as pd
sys.path.insert(0, "src")
from disruptsc.network.commercial_link import CommercialLink

SC = "C:/Users/Celian/AppData/Local/Temp/claude/C--Users-Celian-OneDrive-DisruptSC-disrupt-sc/4f7de379-fbf0-473c-a0e9-89231404ca2d/scratchpad"
SWITCH = {"modal_switch": {"default": 0.15, "dry_bulk": 1000, "liquid_bulk": 1000}, "port_switch": 0.05, "access_km": 50, "line_haul_km": 100}
THRESHOLD = 5.0
UP = ["rhine_basel", "rhine_basel_strasbourg", "rhine_strasbourg", "rhine_strasbourg_karlsruhe", "rhine_karlsruhe", "rhine_karlsruhe_mannheim"]
LOW = ["rhine_koblenz", "rhine_koblenz_bonn", "rhine_bonn", "rhine_bonn_koeln", "rhine_koeln", "rhine_koeln_duesseldorf"]
t0 = time.time()
with open("tmp/EU_transport_network.pkl", "rb") as f:
    tn0 = pickle.load(f)["data"]["transport_network"]
tn = copy.deepcopy(tn0)
for a, b, e in tn.edges(data=True):
    mult = 4.068 if e.get("name") in UP else (2.023 if e.get("name") in LOW else None)
    if mult:
        for k in list(e):
            if str(k).startswith("cost_per_ton"):
                e[k] = float(e[k]) * mult
for a, b in [(a, b) for a, b, e in tn.edges(data=True) if e.get("name") == "rhine_mainz_koblenz"]:
    tn.start_edge_disruption(tn[a][b], 1.0, 1)
avail = tn.get_undisrupted_network()
ft = json.load(open("C:/dsc_runs/rhine2026/lrcheck_base/firm_table.geojson", encoding="utf-8"))
od = {str(f["properties"]["id"]): (int(f["properties"]["od_point"]), float(f["properties"]["transport_share"])) for f in ft["features"]}
ht = json.load(open("C:/dsc_runs/rhine2026/lrcheck_base/household_table.geojson", encoding="utf-8"))
for f in ht["features"]:
    p = f["properties"]
    hid = str(p["id"])
    od["hh_" + hid if not hid.startswith("hh_") else hid] = (int(p["od_point"]), 0.2)
with open("tmp/EU_agents.pkl", "rb") as f:
    countries = pickle.load(f)["data"]["countries"]
for pid, c in countries.items():
    od[str(pid)] = (int(c.od_point), float(getattr(c, "transport_share", 0.2) or 0.2))
del countries
gc.collect()

flags = pd.read_csv(f"{SC}/link_route_flags.csv", dtype=str)
kb = flags[(flags.crosses_kaub == "True") & (flags.cargo_type.isin(["dry_bulk", "liquid_bulk"]))].copy()
kb["o"] = kb.seller_id.map(lambda s: od.get(s, (None, None))[0])
kb["d"] = kb.buyer_id.map(lambda s: od.get(s, (None, None))[0])
kb["share"] = kb.seller_id.map(lambda s: od.get(s, (None, None))[1])
kb = kb.dropna(subset=["o", "d"])
pairs = kb.drop_duplicates(["o", "d", "cargo_type"])
print(f"{len(kb)} Kaub-crossing bulk links, {len(pairs)} OD pairs; setup {time.time()-t0:.0f}s", flush=True)


def kmm(route):
    return CommercialLink._km_by_mode(route, tn)


def mode_seq(route):
    ms = [tn[a][b].get("type") for a, b in route.transport_edges]
    return "+".join(m for i, m in enumerate(ms) if i == 0 or m != ms[i - 1])


rows = []
for i, (_, r) in enumerate(pairs.iterrows()):
    o, d, cargo, share = int(r.o), int(r.d), r.cargo_type, float(r.share)
    base = tn0.provide_shortest_route(o, d, cargo, "cost_per_ton")
    if base is None:
        rows.append(dict(o=o, d=d, cargo_type=cargo, outcome="no_baseline"))
        continue
    base_cost = tn0.compute_route_cost(base, cargo)
    link = CommercialLink(pid="L", supplier_id="S", buyer_id="B", product="P", product_type="mining", category="domestic_B2B",
                          origin_node=o, destination_node=d, route=base, route_cost_per_ton=base_cost, use_transport_network=True,
                          cargo_type=cargo, delivery=1.0, delivery_in_tons=1.0, eq_price=1.0, price=1.0, route_plan=[(base, 1.0)])
    bkm = kmm(base)
    line_haul = {m for m, km in bkm.items() if km >= 100}
    weights = {m: 1001.0 for m in set(base.transport_modes) if m not in line_haul and m != "multimodal"}
    same = avail.provide_shortest_route(o, d, cargo, "cost_per_ton", allowed_modes=set(base.transport_modes), mode_weights=weights or None)
    free = avail.provide_shortest_route(o, d, cargo, "cost_per_ton")
    best = None
    info = dict(o=o, d=d, cargo_type=cargo, share=share, base_cost=base_cost, base_modes=mode_seq(base),
                base_road=bkm.get("roads", 0), base_rail=bkm.get("railways", 0), base_water=bkm.get("waterways", 0), base_sea=bkm.get("maritime", 0))
    for name, cand in (("same", same), ("free", free)):
        if cand is None:
            info[f"{name}_found"] = False
            continue
        cost = tn.compute_route_cost(cand, cargo)
        pen = link.calculate_switching_cost_between(base, cand, SWITCH, tn)
        total = cost + pen * base_cost
        ckm = kmm(cand)
        info.update({f"{name}_found": True, f"{name}_cost": cost,
                     f"{name}_switch": CommercialLink._routes_have_modal_switch(base, cand, tn, SWITCH),
                     f"{name}_pen": pen, f"{name}_road": ckm.get("roads", 0), f"{name}_rail": ckm.get("railways", 0),
                     f"{name}_water": ckm.get("waterways", 0), f"{name}_sea": ckm.get("maritime", 0), f"{name}_modes": mode_seq(cand)})
        if best is None or total < best[1]:
            best = (name, total, cost, pen)
    if best is None:
        info["outcome"] = "no_route"
    else:
        name, total, cost, pen = best
        rel = cost / base_cost - 1
        info.update(chosen=name, rel=rel, pen=pen, delivered_score=share * (rel + pen))
        info["outcome"] = "gives_up" if share * (rel + pen) > THRESHOLD else f"delivers_{name}"
    rows.append(info)
    if i % 300 == 0:
        print(f"  {i}/{len(pairs)} pairs, {time.time()-t0:.0f}s", flush=True)
cl = pd.DataFrame(rows)
cl.to_csv(f"{SC}/lh_classification.csv", index=False)
print("\nOD-pair outcomes:\n" + cl.outcome.value_counts().to_string(), flush=True)
cl["base_road_class"] = pd.cut(cl.base_road.fillna(0), [-1, 50, 100, 200, 400, 1e9], labels=["<=50", "50-100", "100-200", "200-400", ">400"])
print("\nOD pairs by baseline road km and outcome:\n" + pd.crosstab(cl.base_road_class, cl.outcome).to_string(), flush=True)
dl = cl[cl.outcome.str.startswith("delivers")].copy()
if len(dl):
    dl["extra_road"] = [r[f"{r.chosen}_road"] - r.base_road for _, r in dl.iterrows()]
    print("\ndelivering pairs: extra road km (chosen - base) quantiles:", dl.extra_road.quantile([0.1, 0.5, 0.9]).round(0).to_dict())
    print("delivering pairs: freight increase quantiles:", dl.rel.quantile([0.1, 0.5, 0.9]).round(2).to_dict(), flush=True)

# weight by the orders of lrcheck_base in weeks 6 and 7
links = kb[["seller_id", "buyer_id", "o", "d", "cargo_type"]].merge(cl[["o", "d", "cargo_type", "outcome", "chosen", "rel", "base_road"]], on=["o", "d", "cargo_type"], how="left")
keep = set(zip(links.seller_id, links.buyer_id))
parts = []
cols = ["time_step", "seller_id", "buyer_id", "order", "delivery", "realized_delivery", "cargo_type"]
for chunk in pd.read_csv("C:/dsc_runs/rhine2026/lrcheck_base/link_data.csv", usecols=cols, chunksize=3_000_000, dtype={"seller_id": str, "buyer_id": str}):
    c = chunk[chunk.time_step.isin([6, 7])]
    mask = [(s, b) in keep for s, b in zip(c.seller_id, c.buyer_id)]
    parts.append(c[mask])
ld = pd.concat(parts).merge(links[["seller_id", "buyer_id", "outcome", "chosen", "rel", "base_road"]], on=["seller_id", "buyer_id"], how="left")
ld["undelivered_base"] = (ld.delivery - ld.realized_delivery).clip(lower=0)
for t in (6, 7):
    w = ld[ld.time_step == t]
    print(f"\n==== week {t}: Kaub-crossing bulk links in lrcheck_base: orders {w.order.sum():,.0f}, delivery (after rationing) {w.delivery.sum():,.0f}, realized {w.realized_delivery.sum():,.0f}, undelivered {w.undelivered_base.sum():,.0f} mUSD")
    g = w.groupby("outcome").agg(links=("order", "size"), order=("order", "sum"), delivery=("delivery", "sum"), realized_base=("realized_delivery", "sum"), undelivered_base=("undelivered_base", "sum")).round(0)
    print("by predicted outcome under the line-haul rule:\n" + g.to_string())
    print("by cargo x outcome (delivery after rationing, mUSD):\n" + w.pivot_table(index="cargo_type", columns="outcome", values="delivery", aggfunc="sum").round(0).to_string())
print(f"\ndone {time.time()-t0:.0f}s")
