"""
Fix connectivity gaps:
1. Add road edges so all household cities are within 50km of a road node.
2. Move external bloc points in countries.geojson to be near their
   representative airport or port in the transport network.
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
# 1. Add missing road edges
# ──────────────────────────────────────────────────

with open(DATA / "Transport" / "roads_edges.geojson") as f:
    roads = json.load(f)

# Current max edge ID
max_id = max(feat["properties"]["id"] for feat in roads["features"])

# New road edges to add
# Format: (from_coords, to_coords, name, region)
new_roads = [
    # UAE: Ras Al Khaimah ↔ Sharjah
    ([55.98, 25.79], [55.39, 25.34], "E311 - Sharjah-Ras Al Khaimah", "UAE"),

    # SAU: Jeddah ↔ Mecca
    ([39.17, 21.49], [39.83, 21.43], "Route 40 - Jeddah-Mecca", "SAU"),
    # SAU: Jeddah ↔ Medina (via highway)
    ([39.17, 21.49], [39.61, 24.47], "Route 15 - Jeddah-Medina", "SAU"),
    # SAU: Medina ↔ Tabuk
    ([39.61, 24.47], [36.57, 28.38], "Route 15 - Medina-Tabuk", "SAU"),
    # SAU: Riyadh ↔ Abha (via highway to south)
    ([46.72, 24.71], [42.50, 18.22], "Route 15 - Riyadh-Abha", "SAU"),

    # OMN: Muscat ↔ Nizwa
    ([58.41, 23.59], [57.53, 22.93], "Route 15 - Muscat-Nizwa", "OMN"),
    # OMN: Muscat ↔ Sur
    ([58.41, 23.59], [59.53, 22.57], "Route 17 - Muscat-Sur", "OMN"),

    # IRQ: Baghdad ↔ Erbil
    ([44.37, 33.31], [44.01, 36.19], "Route 2 - Baghdad-Erbil", "IRQ"),
    # IRQ: Erbil ↔ Mosul
    ([44.01, 36.19], [43.14, 36.34], "Route 2 - Erbil-Mosul", "IRQ"),
    # IRQ: Baghdad ↔ Najaf
    ([44.37, 33.31], [44.35, 32.00], "Route 8 - Baghdad-Najaf", "IRQ"),
    # IRQ: Baghdad ↔ Karbala
    ([44.37, 33.31], [44.02, 32.62], "Route 9 - Baghdad-Karbala", "IRQ"),
]

for i, (from_c, to_c, name, region) in enumerate(new_roads):
    edge_id = max_id + 1 + i
    km = round(haversine(from_c[0], from_c[1], to_c[0], to_c[1]), 2)
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [from_c, to_c],
        },
        "properties": {
            "id": edge_id,
            "name": name,
            "class": "primary",
            "surface": "paved",
            "region": region,
            "special": None,
            "end1": None,  # will be assigned by model
            "end2": None,
            "km": km,
            "capacity": None,
            "disruption": None,
        },
    }
    roads["features"].append(feature)

with open(DATA / "Transport" / "roads_edges.geojson", "w", encoding="utf-8") as f:
    json.dump(roads, f, indent=2, ensure_ascii=False)
print(f"Roads: added {len(new_roads)} edges (total: {len(roads['features'])})")

# ──────────────────────────────────────────────────
# 2. Fix external bloc positions in countries.geojson
# ──────────────────────────────────────────────────

# Move external blocs near their representative airport/port
# so the model snaps them to a reachable transport node.
BLOC_POSITIONS = {
    # Move to near representative airport that exists in airways_edges.geojson
    "CHN":      (121.5, 31.2, "China (near Shanghai/PVG)"),
    "IND":      (72.9,  19.1, "India (near Mumbai/BOM)"),
    "Europe":   (8.6,   50.0, "Europe (near Frankfurt/FRA)"),
    "East_Asia":(140.4, 35.8, "East Asia (near Tokyo/NRT)"),
    "Americas": (-73.8, 40.6, "Americas (near New York/JFK)"),
    "Africa":   (36.9,  -1.3, "Africa (near Nairobi/NBO)"),
    "Oceania":  (151.2, -34.0,"Oceania (near Sydney/SYD)"),
    "ROW":      (67.0,  24.8, "Rest of World (near Gwadar/Makran coast)"),
}

with open(DATA / "Spatial" / "countries.geojson") as f:
    countries = json.load(f)

moved = 0
for feat in countries["features"]:
    region = feat["properties"]["region"]
    if region in BLOC_POSITIONS:
        lon, lat, name = BLOC_POSITIONS[region]
        old_lon, old_lat = feat["geometry"]["coordinates"]
        feat["geometry"]["coordinates"] = [lon, lat]
        feat["properties"]["name"] = name
        dist = haversine(old_lon, old_lat, lon, lat)
        print(f"  Moved {region}: ({old_lon},{old_lat}) -> ({lon},{lat}) [{dist:.0f} km]")
        moved += 1

with open(DATA / "Spatial" / "countries.geojson", "w", encoding="utf-8") as f:
    json.dump(countries, f, indent=2, ensure_ascii=False)
print(f"Countries: moved {moved} external blocs")

# ──────────────────────────────────────────────────
# 3. Verify — recheck distances
# ──────────────────────────────────────────────────

# Reload
with open(DATA / "Spatial" / "households.geojson") as f:
    hh = json.load(f)
with open(DATA / "Transport" / "roads_edges.geojson") as f:
    roads = json.load(f)
with open(DATA / "Transport" / "maritime_edges.geojson") as f:
    maritime = json.load(f)
with open(DATA / "Transport" / "airways_edges.geojson") as f:
    airways = json.load(f)

road_nodes = set()
for feat in roads["features"]:
    for coord in feat["geometry"]["coordinates"]:
        road_nodes.add(tuple(coord))

print("\n=== VERIFICATION: Households vs Road Edges ===")
all_ok = True
for feat in hh["features"]:
    lon, lat = feat["geometry"]["coordinates"]
    city = feat["properties"]["city"]
    region = feat["properties"]["region"]
    min_dist = min(haversine(lon, lat, rlon, rlat) for rlon, rlat in road_nodes)
    if min_dist > 50:
        print(f"  STILL FAR: {region}/{city}: {min_dist:.0f} km")
        all_ok = False
if all_ok:
    print("  All cities within 50km of a road node!")

# Check external blocs vs airways + maritime
all_transport_nodes = set()
for feat in maritime["features"]:
    for coord in feat["geometry"]["coordinates"]:
        all_transport_nodes.add(tuple(coord))
for feat in airways["features"]:
    for coord in feat["geometry"]["coordinates"]:
        all_transport_nodes.add(tuple(coord))
for feat in roads["features"]:
    for coord in feat["geometry"]["coordinates"]:
        all_transport_nodes.add(tuple(coord))

GULF = ["ARE", "SAU", "QAT", "KWT", "BHR", "OMN", "IRQ"]
with open(DATA / "Spatial" / "countries.geojson") as f:
    countries = json.load(f)

print("\n=== VERIFICATION: External blocs vs any transport node ===")
for feat in countries["features"]:
    region = feat["properties"]["region"]
    if region in GULF:
        continue
    lon, lat = feat["geometry"]["coordinates"]
    min_dist = min(haversine(lon, lat, tlon, tlat) for tlon, tlat in all_transport_nodes)
    status = "OK" if min_dist < 100 else "FAR"
    print(f"  {region}: nearest transport node = {min_dist:.0f} km [{status}]")
