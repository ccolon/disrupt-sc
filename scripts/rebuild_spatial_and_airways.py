"""
Rebuild countries.geojson and airways_edges.geojson to match the new 6 external blocs:
IND, PAK, EAS, EUR, AFR, ROW
"""

import json
import math
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "Gulf"

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ──────────────────────────────────────────────────
# 1. Rebuild countries.geojson
# ──────────────────────────────────────────────────

countries = [
    # Gulf states
    {"region": "ARE", "name": "United Arab Emirates",  "lon": 54.5,  "lat": 24.5},
    {"region": "SAU", "name": "Saudi Arabia",          "lon": 45.0,  "lat": 24.0},
    {"region": "QAT", "name": "Qatar",                 "lon": 51.5,  "lat": 25.3},
    {"region": "KWT", "name": "Kuwait",                "lon": 47.5,  "lat": 29.3},
    {"region": "BHR", "name": "Bahrain",               "lon": 50.5,  "lat": 26.0},
    {"region": "OMN", "name": "Oman",                  "lon": 57.0,  "lat": 21.5},
    {"region": "IRQ", "name": "Iraq",                  "lon": 44.0,  "lat": 33.0},
    # External blocs — positioned near their representative airport/port
    {"region": "IND", "name": "India",                 "lon": 72.9,  "lat": 19.1},   # Mumbai/BOM
    {"region": "PAK", "name": "Pakistan",              "lon": 67.0,  "lat": 24.8},   # Karachi/near Gwadar
    {"region": "EAS", "name": "East Asia",             "lon": 104.0, "lat": 1.4},    # Singapore/SIN
    {"region": "EUR", "name": "Europe",                "lon": 8.6,   "lat": 50.0},   # Frankfurt/FRA
    {"region": "AFR", "name": "Africa",                "lon": 36.9,  "lat": -1.3},   # Nairobi/NBO
    {"region": "ROW", "name": "Rest of World",         "lon": -73.8, "lat": 40.6},   # New York/JFK
]

features = []
for c in countries:
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
        "properties": {"region": c["region"], "name": c["name"]},
    })

with open(DATA / "Spatial" / "countries.geojson", "w", encoding="utf-8") as f:
    json.dump({"type": "FeatureCollection", "features": features}, f, indent=2, ensure_ascii=False)
print(f"Written {len(features)} countries")

# ──────────────────────────────────────────────────
# 2. Rebuild airways_edges.geojson
# ──────────────────────────────────────────────────

# Gulf airports
gulf_airports = {
    "DXB": {"lon": 55.4, "lat": 25.2, "region": "ARE", "name": "Dubai Intl"},
    "AUH": {"lon": 54.6, "lat": 24.4, "region": "ARE", "name": "Abu Dhabi Intl"},
    "DOH": {"lon": 51.6, "lat": 25.3, "region": "QAT", "name": "Hamad Intl"},
    "RUH": {"lon": 46.7, "lat": 25.0, "region": "SAU", "name": "King Khalid Intl"},
    "JED": {"lon": 39.2, "lat": 21.7, "region": "SAU", "name": "King Abdulaziz Intl"},
    "DMM": {"lon": 49.8, "lat": 26.5, "region": "SAU", "name": "King Fahd Intl"},
    "KWI": {"lon": 48.0, "lat": 29.2, "region": "KWT", "name": "Kuwait Intl"},
    "BAH": {"lon": 50.6, "lat": 26.3, "region": "BHR", "name": "Bahrain Intl"},
    "MCT": {"lon": 58.3, "lat": 23.6, "region": "OMN", "name": "Muscat Intl"},
    "BGW": {"lon": 44.2, "lat": 33.3, "region": "IRQ", "name": "Baghdad Intl"},
}

# External airports — one per bloc, positioned to match countries.geojson
external_airports = {
    "BOM": {"lon": 72.9,  "lat": 19.1,  "region": "IND", "name": "Mumbai"},
    "KHI": {"lon": 67.2,  "lat": 24.9,  "region": "PAK", "name": "Karachi"},
    "SIN": {"lon": 104.0, "lat": 1.4,   "region": "EAS", "name": "Singapore"},
    "FRA": {"lon": 8.6,   "lat": 50.0,  "region": "EUR", "name": "Frankfurt"},
    "NBO": {"lon": 36.9,  "lat": -1.3,  "region": "AFR", "name": "Nairobi"},
    "JFK": {"lon": -73.8, "lat": 40.6,  "region": "ROW", "name": "New York"},
}

features = []
edge_id = 0

# Intra-Gulf flights (all pairs)
gulf_codes = list(gulf_airports.keys())
for i in range(len(gulf_codes)):
    for j in range(i + 1, len(gulf_codes)):
        a1, a2 = gulf_airports[gulf_codes[i]], gulf_airports[gulf_codes[j]]
        km = round(haversine(a1["lon"], a1["lat"], a2["lon"], a2["lat"]), 2)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[a1["lon"], a1["lat"]], [a2["lon"], a2["lat"]]],
            },
            "properties": {
                "id": edge_id,
                "name": f"{gulf_codes[i]}-{gulf_codes[j]}",
                "class": "airways",
                "surface": "airways",
                "region": f"{a1['region']}-{a2['region']}",
                "special": None,
                "km": km,
                "capacity": None,
                "disruption": None,
            },
        })
        edge_id += 1

# Gulf ↔ External flights (each Gulf airport to each external airport)
for gc in gulf_codes:
    for ec, ea in external_airports.items():
        ga = gulf_airports[gc]
        km = round(haversine(ga["lon"], ga["lat"], ea["lon"], ea["lat"]), 2)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[ga["lon"], ga["lat"]], [ea["lon"], ea["lat"]]],
            },
            "properties": {
                "id": edge_id,
                "name": f"{gc}-{ec}",
                "class": "airways",
                "surface": "airways",
                "region": f"{ga['region']}-{ea['region']}",
                "special": None,
                "km": km,
                "capacity": None,
                "disruption": None,
            },
        })
        edge_id += 1

with open(DATA / "Transport" / "airways_edges.geojson", "w", encoding="utf-8") as f:
    json.dump({"type": "FeatureCollection", "features": features}, f, indent=2, ensure_ascii=False)
print(f"Written {len(features)} airways edges ({len(gulf_codes)}C2 intra-Gulf + {len(gulf_codes)}x{len(external_airports)} external)")

# ──────────────────────────────────────────────────
# 3. Verify connectivity
# ──────────────────────────────────────────────────

with open(DATA / "Spatial" / "households.geojson") as f:
    hh = json.load(f)
with open(DATA / "Transport" / "roads_edges.geojson") as f:
    roads = json.load(f)
with open(DATA / "Transport" / "maritime_edges.geojson") as f:
    maritime = json.load(f)
with open(DATA / "Transport" / "airways_edges.geojson") as f:
    airways = json.load(f)

# All transport nodes
all_nodes = set()
for layer in [roads, maritime, airways]:
    for feat in layer["features"]:
        for coord in feat["geometry"]["coordinates"]:
            all_nodes.add(tuple(coord))

road_nodes = set()
for feat in roads["features"]:
    for coord in feat["geometry"]["coordinates"]:
        road_nodes.add(tuple(coord))

GULF = ["ARE", "SAU", "QAT", "KWT", "BHR", "OMN", "IRQ"]

print("\n=== Households vs roads (>50km) ===")
ok = True
for feat in hh["features"]:
    lon, lat = feat["geometry"]["coordinates"]
    d = min(haversine(lon, lat, n[0], n[1]) for n in road_nodes)
    if d > 50:
        print(f"  {feat['properties']['region']}/{feat['properties']['city']}: {d:.0f} km")
        ok = False
if ok:
    print("  All OK!")

print("\n=== External blocs vs transport ===")
with open(DATA / "Spatial" / "countries.geojson") as f:
    ctrs = json.load(f)
for feat in ctrs["features"]:
    r = feat["properties"]["region"]
    if r in GULF:
        continue
    lon, lat = feat["geometry"]["coordinates"]
    d = min(haversine(lon, lat, n[0], n[1]) for n in all_nodes)
    status = "OK" if d < 100 else "FAR"
    print(f"  {r}: {d:.0f} km [{status}]")
