"""
Build a simplified road network for the Gulf states (Hormuz scenario).

Requirements:
  1. Very simplified: only major highway corridors
  2. Cross-border edges flagged with special="border"
  3. All main ports connected to the road network

Countries: UAE, SAU, QAT, KWT, BHR, OMN, IRQ
"""

import json
import math

# ──────────────────────────────────────────────────
# 1. Define nodes (ports, cities, border crossings)
# ──────────────────────────────────────────────────

nodes = {
    # === PORTS ===
    # UAE
    "jebel_ali":       {"lon": 55.06, "lat": 25.00, "type": "port", "region": "UAE", "label": "Jebel Ali Port"},
    "khalifa_port":    {"lon": 54.60, "lat": 24.53, "type": "port", "region": "UAE", "label": "Khalifa Port"},
    "fujairah_port":   {"lon": 56.35, "lat": 25.13, "type": "port", "region": "UAE", "label": "Fujairah Port"},
    # SAU
    "dammam_port":     {"lon": 50.19, "lat": 26.43, "type": "port", "region": "SAU", "label": "King Abdulaziz Port (Dammam)"},
    "jubail_port":     {"lon": 49.66, "lat": 27.01, "type": "port", "region": "SAU", "label": "Jubail Commercial Port"},
    "jeddah_port":     {"lon": 39.17, "lat": 21.49, "type": "port", "region": "SAU", "label": "Jeddah Islamic Port"},
    # QAT
    "hamad_port":      {"lon": 51.55, "lat": 25.29, "type": "port", "region": "QAT", "label": "Hamad Port (Doha)"},
    # KWT
    "shuaiba_port":    {"lon": 48.16, "lat": 29.04, "type": "port", "region": "KWT", "label": "Shuaiba Port"},
    # BHR
    "khalifa_bhr":     {"lon": 50.53, "lat": 26.00, "type": "port", "region": "BHR", "label": "Khalifa bin Salman Port"},
    # OMN
    "sohar_port":      {"lon": 56.73, "lat": 24.37, "type": "port", "region": "OMN", "label": "Sohar Port"},
    "muscat_port":     {"lon": 58.57, "lat": 23.63, "type": "port", "region": "OMN", "label": "Sultan Qaboos Port"},
    "salalah_port":    {"lon": 54.00, "lat": 16.95, "type": "port", "region": "OMN", "label": "Salalah Port"},
    # IRQ
    "umm_qasr":        {"lon": 47.95, "lat": 30.04, "type": "port", "region": "IRQ", "label": "Umm Qasr Port"},

    # === CITIES (inland hubs) ===
    "dubai":           {"lon": 55.27, "lat": 25.20, "type": "city", "region": "UAE", "label": "Dubai"},
    "abu_dhabi":       {"lon": 54.37, "lat": 24.45, "type": "city", "region": "UAE", "label": "Abu Dhabi"},
    "al_ain":          {"lon": 55.76, "lat": 24.21, "type": "city", "region": "UAE", "label": "Al Ain"},
    "sharjah":         {"lon": 55.39, "lat": 25.34, "type": "city", "region": "UAE", "label": "Sharjah"},
    "riyadh":          {"lon": 46.72, "lat": 24.71, "type": "city", "region": "SAU", "label": "Riyadh"},
    "hofuf":           {"lon": 49.59, "lat": 25.38, "type": "city", "region": "SAU", "label": "Al Hofuf"},
    "kuwait_city":     {"lon": 47.98, "lat": 29.38, "type": "city", "region": "KWT", "label": "Kuwait City"},
    "manama":          {"lon": 50.58, "lat": 26.22, "type": "city", "region": "BHR", "label": "Manama"},
    "doha":            {"lon": 51.53, "lat": 25.29, "type": "city", "region": "QAT", "label": "Doha"},
    "basra":           {"lon": 47.78, "lat": 30.51, "type": "city", "region": "IRQ", "label": "Basra"},
    "baghdad":         {"lon": 44.37, "lat": 33.31, "type": "city", "region": "IRQ", "label": "Baghdad"},
    "muscat_city":     {"lon": 58.41, "lat": 23.59, "type": "city", "region": "OMN", "label": "Muscat"},

    # === BORDER CROSSINGS ===
    "ghweifat":        {"lon": 51.58, "lat": 24.24, "type": "border", "region": "UAE-SAU", "label": "Ghweifat (UAE-SAU)"},
    "buraimi":         {"lon": 55.79, "lat": 24.24, "type": "border", "region": "UAE-OMN", "label": "Al Buraimi (UAE-OMN)"},
    "abu_samra":       {"lon": 50.77, "lat": 24.68, "type": "border", "region": "QAT-SAU", "label": "Abu Samra (QAT-SAU)"},
    "nuwaiseeb":       {"lon": 47.97, "lat": 28.59, "type": "border", "region": "KWT-SAU", "label": "Nuwaiseeb (KWT-SAU)"},
    "safwan":          {"lon": 47.73, "lat": 30.07, "type": "border", "region": "KWT-IRQ", "label": "Safwan (KWT-IRQ)"},
    "causeway_mid":    {"lon": 50.34, "lat": 26.10, "type": "border", "region": "BHR-SAU", "label": "King Fahd Causeway"},
}

# ──────────────────────────────────────────────────
# 2. Define edges (highway corridors)
# ──────────────────────────────────────────────────

# Each edge: (from_node, to_node, name, asset_class, region, special)
# special = "border" for cross-border edges, null otherwise

edges_def = [
    # === UAE internal ===
    ("khalifa_port", "abu_dhabi",   "E10 - Abu Dhabi port road",  "primary", "UAE", None),
    ("abu_dhabi",    "dubai",       "E11 - Abu Dhabi-Dubai",      "primary", "UAE", None),
    ("dubai",        "jebel_ali",   "E11 - Dubai-Jebel Ali",      "primary", "UAE", None),
    ("dubai",        "sharjah",     "E11 - Dubai-Sharjah",         "primary", "UAE", None),
    ("sharjah",      "fujairah_port","E88 - Sharjah-Fujairah",    "primary", "UAE", None),
    ("abu_dhabi",    "al_ain",      "E22 - Abu Dhabi-Al Ain",      "primary", "UAE", None),
    ("abu_dhabi",    "ghweifat",    "E11 - Abu Dhabi-Ghweifat",    "primary", "UAE", None),
    ("al_ain",       "buraimi",     "Al Ain-Buraimi road",         "primary", "UAE", None),

    # === UAE cross-border ===
    ("ghweifat",     "hofuf",       "Ghweifat-Hofuf highway",     "primary", "UAE-SAU", "border"),
    ("buraimi",      "sohar_port",  "Buraimi-Sohar highway",      "primary", "UAE-OMN", "border"),

    # === SAU internal ===
    ("dammam_port",  "hofuf",       "Route 95 - Dammam-Hofuf",    "primary", "SAU", None),
    ("dammam_port",  "jubail_port", "Route 615 - Dammam-Jubail",  "primary", "SAU", None),
    ("hofuf",        "riyadh",      "Route 40 - Hofuf-Riyadh",    "primary", "SAU", None),
    ("riyadh",       "jeddah_port", "Route 40 - Riyadh-Jeddah",   "primary", "SAU", None),
    ("hofuf",        "abu_samra",   "Route 95 - Hofuf-Salwa",     "primary", "SAU", None),
    ("dammam_port",  "nuwaiseeb",   "Route 95 - Dammam-Khafji",   "primary", "SAU", None),
    ("dammam_port",  "causeway_mid","Route 605 - Dammam-Causeway", "primary", "SAU", None),

    # === SAU cross-border ===
    ("abu_samra",    "doha",        "Salwa Rd - border to Doha",   "primary", "QAT-SAU", "border"),
    ("nuwaiseeb",    "kuwait_city", "Route 80 - border to Kuwait", "primary", "KWT-SAU", "border"),
    ("causeway_mid", "manama",      "King Fahd Causeway - to BHR", "primary", "BHR-SAU", "border"),

    # === QAT internal ===
    ("doha",         "hamad_port",  "Hamad Port road",             "primary", "QAT", None),

    # === KWT internal ===
    ("kuwait_city",  "shuaiba_port","Route 40 - Kuwait-Shuaiba",  "primary", "KWT", None),
    ("kuwait_city",  "safwan",      "Route 80 - Kuwait-Safwan",   "primary", "KWT", None),

    # === KWT-IRQ cross-border ===
    ("safwan",       "umm_qasr",    "Safwan-Umm Qasr road",       "primary", "KWT-IRQ", "border"),

    # === BHR internal ===
    ("manama",       "khalifa_bhr", "Manama-Khalifa Port road",   "primary", "BHR", None),

    # === OMN internal ===
    ("sohar_port",   "muscat_city", "Route 1 - Sohar-Muscat",     "primary", "OMN", None),
    ("muscat_city",  "muscat_port", "Muscat port road",            "primary", "OMN", None),
    ("muscat_city",  "salalah_port","Route 31 - Muscat-Salalah",  "primary", "OMN", None),

    # === IRQ internal ===
    ("umm_qasr",     "basra",       "Basra-Umm Qasr highway",     "primary", "IRQ", None),
    ("basra",        "baghdad",     "Route 1 - Basra-Baghdad",    "primary", "IRQ", None),
]


# ──────────────────────────────────────────────────
# 3. Build GeoJSON
# ──────────────────────────────────────────────────

def haversine_km(lon1, lat1, lon2, lat2):
    """Great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Assign integer IDs to nodes
node_ids = {name: idx for idx, name in enumerate(nodes.keys())}

features = []
for edge_id, (n1, n2, name, asset, region, special) in enumerate(edges_def):
    p1 = nodes[n1]
    p2 = nodes[n2]
    km = round(haversine_km(p1["lon"], p1["lat"], p2["lon"], p2["lat"]), 2)

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [p1["lon"], p1["lat"]],
                [p2["lon"], p2["lat"]],
            ],
        },
        "properties": {
            "id": edge_id,
            "name": name,
            "class": asset,
            "surface": "paved",
            "region": region,
            "special": special,
            "end1": node_ids[n1],
            "end2": node_ids[n2],
            "km": km,
            "capacity": None,
            "disruption": None,
        },
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features,
}

# ──────────────────────────────────────────────────
# 4. Write output
# ──────────────────────────────────────────────────

import pathlib
import os

# Determine output path
script_dir = pathlib.Path(__file__).resolve().parent
repo_root = script_dir.parent
out_dir = repo_root / "data" / "Gulf" / "Transport"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "roads_edges.geojson"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"Written {len(features)} road edges to {out_path}")
print(f"  Nodes: {len(nodes)}")
print(f"  Border edges: {sum(1 for e in edges_def if e[5] == 'border')}")
print(f"  Port nodes: {sum(1 for n in nodes.values() if n['type'] == 'port')}")
print()

# Summary table
print(f"{'ID':>3}  {'From':>18} → {'To':<18}  {'km':>7}  {'Region':<10}  {'Special'}")
print("-" * 90)
for edge_id, (n1, n2, name, asset, region, special) in enumerate(edges_def):
    p1, p2 = nodes[n1], nodes[n2]
    km = round(haversine_km(p1["lon"], p1["lat"], p2["lon"], p2["lat"]), 1)
    sp = special or ""
    print(f"{edge_id:>3}  {n1:>18} → {n2:<18}  {km:>6.1f}  {region:<10}  {sp}")
