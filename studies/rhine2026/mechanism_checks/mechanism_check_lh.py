# Mechanism preview of the line-haul rule on the real EU network (read-only, transport cache only).
# Week-6 state of the 2026 profile: Kaub edge closed, upstream x4.068, Lower Rhine x2.023.
# For a sample of Kaub-crossing bulk OD pairs: baseline route, same-mode candidate (access modes
# weighted 1+penalty), free candidate, line-haul verdicts, chosen route and the give-up decision.
import copy, json, pickle, random, sys
import pandas as pd
sys.path.insert(0, "src")
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route

SC = "C:/Users/Celian/AppData/Local/Temp/claude/C--Users-Celian-OneDrive-DisruptSC-disrupt-sc/4f7de379-fbf0-473c-a0e9-89231404ca2d/scratchpad"
SWITCH = {"modal_switch": {"default": 0.15, "dry_bulk": 1000, "liquid_bulk": 1000}, "port_switch": 0.05,
          "access_km": 50, "line_haul_km": 100}
THRESHOLD = 5.0
UP = ["rhine_basel", "rhine_basel_strasbourg", "rhine_strasbourg", "rhine_strasbourg_karlsruhe", "rhine_karlsruhe", "rhine_karlsruhe_mannheim"]
LOW = ["rhine_koblenz", "rhine_koblenz_bonn", "rhine_bonn", "rhine_bonn_koeln", "rhine_koeln", "rhine_koeln_duesseldorf"]

with open("tmp/EU_transport_network.pkl", "rb") as f:
    tn0 = pickle.load(f)["data"]["transport_network"]
tn = copy.deepcopy(tn0)
for a, b, e in tn.edges(data=True):
    mult = 4.068 if e.get("name") in UP else (2.023 if e.get("name") in LOW else None)
    if mult:
        for k in list(e):
            if str(k).startswith("cost_per_ton"):
                e[k] = float(e[k]) * mult
kaub = [(a, b) for a, b, e in tn.edges(data=True) if e.get("name") == "rhine_mainz_koblenz"]
for a, b in kaub:
    tn.start_edge_disruption(tn[a][b], 1.0, 1)
avail = tn.get_undisrupted_network()
print("Kaub edges closed:", kaub, "| available edges", avail.number_of_edges(), "of", tn.number_of_edges())

# od points
ft = json.load(open("C:/dsc_runs/rhine2026/lrcheck_base/firm_table.geojson", encoding="utf-8"))
od = {str(f["properties"]["id"]): (int(f["properties"]["od_point"]), float(f["properties"]["transport_share"])) for f in ft["features"]}
ht = json.load(open("C:/dsc_runs/rhine2026/lrcheck_base/household_table.geojson", encoding="utf-8"))
hprops = ht["features"][0]["properties"]
for f in ht["features"]:
    p = f["properties"]
    hid = str(p.get("id", p.get("pid", "")))
    if "od_point" in p:
        od["hh_" + hid if not hid.startswith("hh_") else hid] = (int(p["od_point"]), 0.2)
with open("tmp/EU_agents.pkl", "rb") as f:
    countries = pickle.load(f)["data"]["countries"]
for pid, c in countries.items():
    od[str(pid)] = (int(c.od_point), float(getattr(c, "transport_share", 0.2) or 0.2))
print("od points known for", len(od), "agents; household props:", list(hprops.keys())[:8])

flags = pd.read_csv(f"{SC}/link_route_flags.csv", dtype=str)
kb = flags[(flags.crosses_kaub == "True") & (flags.cargo_type.isin(["dry_bulk", "liquid_bulk"]))].copy()
print("Kaub-crossing bulk links:", len(kb), "| by cargo:", kb.cargo_type.value_counts().to_dict(), "| modes:", kb.modes.value_counts().head(6).to_dict())
kb["o"] = kb.seller_id.map(lambda s: od.get(s, (None, None))[0]); kb["d"] = kb.buyer_id.map(lambda s: od.get(s, (None, None))[0])
kb = kb.dropna(subset=["o", "d"])
pairs = kb.drop_duplicates(["o", "d", "cargo_type"])
print("unique OD pairs:", len(pairs))
named = [("AFR", "2121"), ("AFR", "2128"), ("NOR", "2720"), ("2720", "2733")]
rows = [r for _, r in pairs.iterrows() if (r.seller_id, r.buyer_id) in named]
rest = [r for _, r in pairs.iterrows() if (r.seller_id, r.buyer_id) not in named]
random.seed(7); random.shuffle(rest)
sample = rows + rest[:36]

def km_by_mode(route):
    return {m: round(v, 0) for m, v in CommercialLink._km_by_mode(route, tn).items()}

def _nodes(route):
    es = list(route.transport_edges)
    return [a for a, b in es] + [es[-1][1]] if es else []

def bbox(route):
    lons = [float(tn.nodes[n]["long"]) for n in _nodes(route)]; lats = [float(tn.nodes[n]["lat"]) for n in _nodes(route)]
    return f"lon {min(lons):.1f}..{max(lons):.1f} lat {min(lats):.1f}..{max(lats):.1f}"

def mode_seq(route):
    ms = [tn[a][b].get("type") for a, b in route.transport_edges]
    return "+".join(m for i, m in enumerate(ms) if i == 0 or m != ms[i - 1])

def link_for(o, d, cargo, base):
    return CommercialLink(pid="L", supplier_id="S", buyer_id="B", product="P", product_type="mining", category="domestic_B2B",
                          origin_node=o, destination_node=d, route=base, route_cost_per_ton=tn0.compute_route_cost(base, cargo),
                          use_transport_network=True, cargo_type=cargo, delivery=1.0, delivery_in_tons=1.0, eq_price=1.0, price=1.0,
                          route_plan=[(base, 1.0)])

summary = []
for r in sample:
    o, d, cargo = int(r.o), int(r.d), r.cargo_type
    share = od[r.seller_id][1]
    base = tn0.provide_shortest_route(o, d, cargo, "cost_per_ton")
    if base is None:
        print(f"\n{r.seller_id}->{r.buyer_id} {cargo}: no baseline route"); continue
    link = link_for(o, d, cargo, base)
    base_km = CommercialLink._km_by_mode(base, tn)
    line_haul = {m for m, km in base_km.items() if km >= 100}
    weights = {m: 1001.0 for m in set(base.transport_modes) if m not in line_haul and m != "multimodal"}
    same = avail.provide_shortest_route(o, d, cargo, "cost_per_ton", allowed_modes=set(base.transport_modes), mode_weights=weights or None)
    free = avail.provide_shortest_route(o, d, cargo, "cost_per_ton")
    print(f"\n== {r.seller_id}->{r.buyer_id} {cargo} (share {share:.3f}); baseline {mode_seq(base)} km {km_by_mode(base)} cost {link.route_cost_per_ton:.1f}; line-haul modes {sorted(line_haul)}")
    best, best_total = None, None
    for name, cand in (("same", same), ("free", free)):
        if cand is None:
            print(f"   {name}: none"); continue
        cost = tn.compute_route_cost(cand, cargo)
        pen = link.calculate_switching_cost_between(base, cand, SWITCH, tn)
        switch = CommercialLink._routes_have_modal_switch(base, cand, tn, SWITCH)
        total = cost + pen * link.route_cost_per_ton
        print(f"   {name}: {mode_seq(cand)} km {km_by_mode(cand)} cost {cost:.1f} (+{100*(cost/link.route_cost_per_ton-1):.0f} %) switch={switch} pen={pen} total={total:.1f} [{bbox(cand)}]")
        if best_total is None or total < best_total:
            best, best_total, best_name, best_cost, best_pen = cand, total, name, cost, pen
    if best is None:
        summary.append((r.seller_id, r.buyer_id, cargo, "no_route", None)); continue
    rel = best_cost / link.route_cost_per_ton - 1
    give_up = share * (rel + best_pen) > THRESHOLD
    print(f"   -> chosen {best_name}: share x (rel {rel:.2f} + pen {best_pen}) = {share*(rel+best_pen):.2f} -> {'GIVES UP' if give_up else 'DELIVERS'}")
    summary.append((r.seller_id, r.buyer_id, cargo, "gives_up" if give_up else f"delivers_{best_name}", round(rel, 2)))
s = pd.DataFrame(summary, columns=["seller", "buyer", "cargo", "outcome", "rel"])
print("\n==== SUMMARY over", len(s), "sampled Kaub-crossing bulk OD pairs ====")
print(s.outcome.value_counts().to_string())
print(s[s.outcome.str.startswith("delivers")].to_string())
