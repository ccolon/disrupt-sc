# Line-haul rule WITH per-cargo line-haul modes (road never line haul for bulk) over ALL Kaub-crossing bulk OD
# pairs (week-6 network state), weighted by the week-6/7 orders of lrcheck_base_lh. Writes lh_classification_bulk.csv
# and lh_links_bulk.csv (per link) and prints value shares. Same functions as the model (commit 8d26c6c).
import copy, gc, json, pickle, sys, time
import pandas as pd
sys.path.insert(0, "src")
from disruptsc.network.commercial_link import CommercialLink

SC = "C:/Users/Celian/AppData/Local/Temp/claude/C--Users-Celian-OneDrive-DisruptSC-disrupt-sc/4f7de379-fbf0-473c-a0e9-89231404ca2d/scratchpad"
SWITCH = {"modal_switch": {"default": 0.15, "dry_bulk": 1000, "liquid_bulk": 1000}, "port_switch": 0.05,
          "access_km": 50, "line_haul_km": 100,
          "line_haul_modes": {"default": ["roads", "railways", "waterways", "maritime"],
                              "dry_bulk": ["railways", "waterways", "maritime"], "liquid_bulk": ["railways", "waterways", "maritime"]}}
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
    line_haul = link._line_haul_of(bkm, SWITCH, cargo)                       # as discover_route does
    penalty = link._switching_penalty(SWITCH, "modal_switch", 0.15)
    weights = {m: 1.0 + penalty for m in set(base.transport_modes) if m not in line_haul and m != "multimodal"}
    same = avail.provide_shortest_route(o, d, cargo, "cost_per_ton", allowed_modes=set(base.transport_modes), mode_weights=weights or None)
    free = avail.provide_shortest_route(o, d, cargo, "cost_per_ton")
    best = None
    info = dict(o=o, d=d, cargo_type=cargo, share=share, base_cost=base_cost, base_modes=mode_seq(base), line_haul="+".join(sorted(line_haul)),
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
                     f"{name}_switch": CommercialLink._routes_have_modal_switch(base, cand, tn, SWITCH, cargo),
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
cl.to_csv(f"{SC}/lh_classification_bulk.csv", index=False)
print("\nOD-pair outcomes:\n" + cl.outcome.value_counts().to_string(), flush=True)
cl["base_road_class"] = pd.cut(cl.base_road.fillna(0), [-1, 50, 100, 200, 400, 1e9], labels=["<=50", "50-100", "100-200", "200-400", ">400"])
print("\nOD pairs by baseline road km and outcome:\n" + pd.crosstab(cl.base_road_class, cl.outcome).to_string(), flush=True)
dl = cl[cl.outcome.str.startswith("delivers")].copy()
if len(dl):
    dl["extra_road"] = [r[f"{r.chosen}_road"] - r.base_road for _, r in dl.iterrows()]
    dl["extra_water"] = [r[f"{r.chosen}_water"] - r.base_water for _, r in dl.iterrows()]
    print("\ndelivering pairs: extra road km quantiles:", dl.extra_road.quantile([0.1, 0.5, 0.9]).round(0).to_dict(),
          "| extra water km quantiles:", dl.extra_water.quantile([0.1, 0.5, 0.9]).round(0).to_dict())
    print("delivering pairs: freight increase quantiles:", dl.rel.quantile([0.1, 0.5, 0.9]).round(2).to_dict())
    print("delivering pairs by chosen modes:\n" + dl.apply(lambda r: r[f"{r.chosen}_modes"], axis=1).value_counts().head(8).to_string(), flush=True)

links = kb[["seller_id", "buyer_id", "o", "d", "cargo_type"]].merge(
    cl[["o", "d", "cargo_type", "outcome", "chosen", "rel", "base_road", "line_haul"]], on=["o", "d", "cargo_type"], how="left")
links.to_csv(f"{SC}/lh_links_bulk.csv", index=False)
keep = set(zip(links.seller_id, links.buyer_id))
parts = []
cols = ["time_step", "seller_id", "buyer_id", "order", "delivery", "realized_delivery", "cargo_type"]
for chunk in pd.read_csv("C:/dsc_runs/rhine2026/lrcheck_base_lh/link_data.csv", usecols=cols, chunksize=3_000_000, dtype={"seller_id": str, "buyer_id": str}):
    c = chunk[chunk.time_step.isin([6, 7])]
    mask = [(s, b) in keep for s, b in zip(c.seller_id, c.buyer_id)]
    parts.append(c[mask])
ld = pd.concat(parts).merge(links[["seller_id", "buyer_id", "outcome", "chosen", "rel", "base_road"]], on=["seller_id", "buyer_id"], how="left")
for t in (6, 7):
    w = ld[ld.time_step == t]
    print(f"\n==== week {t}: Kaub-crossing bulk links in lrcheck_base_lh: orders {w.order.sum():,.0f}, realized {w.realized_delivery.sum():,.0f} mUSD")
    g = w.groupby("outcome").agg(links=("order", "size"), order=("order", "sum"), realized_lh=("realized_delivery", "sum")).round(0)
    print("by predicted outcome under the bulk line-haul-modes rule:\n" + g.to_string())
    print("by cargo x outcome (orders, mUSD):\n" + w.pivot_table(index="cargo_type", columns="outcome", values="order", aggfunc="sum").round(0).to_string())
print(f"\ndone {time.time()-t0:.0f}s")
