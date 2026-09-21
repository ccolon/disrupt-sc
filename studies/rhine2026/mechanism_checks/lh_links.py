# Per-link table of the predicted line-haul outcome: lh_classification.csv (per OD pair) -> lh_links.csv.
import gc, json, pickle, sys
import pandas as pd
sys.path.insert(0, "src")
SC = "C:/Users/Celian/AppData/Local/Temp/claude/C--Users-Celian-OneDrive-DisruptSC-disrupt-sc/4f7de379-fbf0-473c-a0e9-89231404ca2d/scratchpad"
ft = json.load(open("C:/dsc_runs/rhine2026/lrcheck_base/firm_table.geojson", encoding="utf-8"))
od = {str(f["properties"]["id"]): int(f["properties"]["od_point"]) for f in ft["features"]}
ht = json.load(open("C:/dsc_runs/rhine2026/lrcheck_base/household_table.geojson", encoding="utf-8"))
for f in ht["features"]:
    p = f["properties"]
    hid = str(p["id"])
    od["hh_" + hid if not hid.startswith("hh_") else hid] = int(p["od_point"])
with open("tmp/EU_agents.pkl", "rb") as f:
    countries = pickle.load(f)["data"]["countries"]
for pid, c in countries.items():
    od[str(pid)] = int(c.od_point)
del countries
gc.collect()
flags = pd.read_csv(f"{SC}/link_route_flags.csv", dtype=str)
kb = flags[(flags.crosses_kaub == "True") & (flags.cargo_type.isin(["dry_bulk", "liquid_bulk"]))].copy()
kb["o"] = kb.seller_id.map(od)
kb["d"] = kb.buyer_id.map(od)
kb = kb.dropna(subset=["o", "d"])
kb["o"] = kb.o.astype(int)
kb["d"] = kb.d.astype(int)
cl = pd.read_csv(f"{SC}/lh_classification.csv")
links = kb[["seller_id", "buyer_id", "o", "d", "cargo_type"]].merge(
    cl[["o", "d", "cargo_type", "outcome", "chosen", "rel", "base_road", "base_modes", "same_modes", "free_modes"]],
    on=["o", "d", "cargo_type"], how="left")
links.to_csv(f"{SC}/lh_links.csv", index=False)
print(len(links), "links written;", links.outcome.value_counts().to_dict())
