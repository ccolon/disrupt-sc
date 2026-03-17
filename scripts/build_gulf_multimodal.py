"""
Build multimodal_edges.geojson for the Gulf scenario.

Connectors needed:
  - roads-maritime: at each port, connect nearest road endpoint to nearest maritime endpoint
  - roads-airways: at each airport, connect nearest road endpoint to nearest airway endpoint
  - NO maritime-airways

Endpoints must match EXACTLY with coordinates in the existing transport files.
"""

import json
import math
import pathlib

DATA_DIR = pathlib.Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc\.claude\worktrees\distracted-gould\data\Gulf\Transport")


def load_endpoints(filepath):
    """Extract all unique endpoint coordinates from a GeoJSON file."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    endpoints = set()
    for feat in data['features']:
        coords = feat['geometry']['coordinates']
        endpoints.add((coords[0][0], coords[0][1]))
        endpoints.add((coords[-1][0], coords[-1][1]))
    return endpoints


def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_endpoint(target_lon, target_lat, endpoints):
    """Find the endpoint closest to a target coordinate."""
    best, best_d = None, float('inf')
    for lon, lat in endpoints:
        d = haversine_km(target_lon, target_lat, lon, lat)
        if d < best_d:
            best, best_d = (lon, lat), d
    return best, best_d


# ── Load existing endpoints ─────────────────────────
road_eps = load_endpoints(DATA_DIR / "roads_edges.geojson")
maritime_eps = load_endpoints(DATA_DIR / "maritime_edges.geojson")
airway_eps = load_endpoints(DATA_DIR / "airways_edges.geojson")

print(f"Road endpoints: {len(road_eps)}")
print(f"Maritime endpoints: {len(maritime_eps)}")
print(f"Airway endpoints: {len(airway_eps)}")

# ── Define connection points ────────────────────────
# Ports: approximate location to anchor the search for nearest road & maritime endpoints
PORTS = {
    "Jebel Ali":    (55.06, 25.00),
    "Khalifa Port": (54.60, 24.53),
    "Fujairah":     (56.35, 25.13),
    "Dammam":       (50.19, 26.43),
    "Jubail":       (49.66, 27.01),
    "Jeddah":       (39.17, 21.49),
    "Hamad (Doha)": (51.55, 25.29),
    "Shuaiba":      (48.16, 29.04),
    "Khalifa BHR":  (50.53, 26.00),
    "Sohar":        (56.73, 24.37),
    "Muscat":       (58.57, 23.63),
    "Salalah":      (54.00, 16.95),
    "Umm Qasr":     (47.95, 30.04),
}

# Airports: approximate location to find nearest road endpoint
# (airway endpoints are exact since we defined them)
AIRPORTS = {
    "DXB": (55.36, 25.25),  # nearest road node: Dubai (55.27, 25.20)
    "AUH": (54.65, 24.43),  # nearest road node: Abu Dhabi (54.37, 24.45)
    "DOH": (51.61, 25.26),  # nearest road node: Doha (51.53, 25.29)
    "RUH": (46.70, 24.96),  # nearest road node: Riyadh (46.72, 24.71)
    "JED": (39.16, 21.68),  # nearest road node: Jeddah port (39.17, 21.49)
    "DMM": (49.80, 26.47),  # nearest road node: Dammam port (50.19, 26.43)
    "KWI": (47.97, 29.23),  # nearest road node: Kuwait City (47.98, 29.38)
    "BAH": (50.63, 26.27),  # nearest road node: Manama (50.58, 26.22)
    "MCT": (58.28, 23.59),  # nearest road node: Muscat city (58.41, 23.59)
    "BGW": (44.23, 33.26),  # nearest road node: Baghdad (44.37, 33.31)
}

features = []
edge_id = 0

# ── 1. Roads ↔ Maritime (at ports) ─────────────────
print("\n--- Roads-Maritime connectors ---")
connected_pairs = set()  # avoid duplicates

for port_name, (plon, plat) in PORTS.items():
    road_pt, road_d = nearest_endpoint(plon, plat, road_eps)
    marit_pt, marit_d = nearest_endpoint(plon, plat, maritime_eps)

    # Skip if either is too far (>200 km — e.g., Salalah may not have a nearby road node)
    if road_d > 200 or marit_d > 200:
        print(f"  SKIP {port_name}: road={road_d:.0f}km, maritime={marit_d:.0f}km")
        continue

    # Skip if same point or already connected
    pair = (road_pt, marit_pt)
    if pair in connected_pairs or road_pt == marit_pt:
        print(f"  SKIP {port_name}: duplicate or same point")
        continue
    connected_pairs.add(pair)

    km = round(haversine_km(road_pt[0], road_pt[1], marit_pt[0], marit_pt[1]), 2)
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [list(road_pt), list(marit_pt)],
        },
        "properties": {
            "id": edge_id,
            "name": f"port-{port_name}",
            "class": "multimodal",
            "surface": None,
            "region": "Gulf",
            "special": None,
            "km": km,
            "capacity": None,
            "disruption": None,
            "multimodes": "roads-maritime",
        },
    })
    print(f"  [{edge_id:>3}] {port_name:<16} road({road_pt[0]:.2f},{road_pt[1]:.2f}) <-> marit({marit_pt[0]:.2f},{marit_pt[1]:.2f})  km={km:.1f}")
    edge_id += 1

roads_maritime_count = edge_id

# ── 2. Roads ↔ Airways (at airports) ───────────────
print("\n--- Roads-Airways connectors ---")
for apt_code, (alon, alat) in AIRPORTS.items():
    # Airway endpoint is exact (we defined it)
    air_pt, air_d = nearest_endpoint(alon, alat, airway_eps)
    road_pt, road_d = nearest_endpoint(alon, alat, road_eps)

    if road_d > 200:
        print(f"  SKIP {apt_code}: road={road_d:.0f}km")
        continue
    if road_pt == air_pt:
        print(f"  SKIP {apt_code}: same point")
        continue

    km = round(haversine_km(road_pt[0], road_pt[1], air_pt[0], air_pt[1]), 2)
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [list(road_pt), list(air_pt)],
        },
        "properties": {
            "id": edge_id,
            "name": f"airport-{apt_code}",
            "class": "multimodal",
            "surface": None,
            "region": "Gulf",
            "special": None,
            "km": km,
            "capacity": None,
            "disruption": None,
            "multimodes": "roads-airways",
        },
    })
    print(f"  [{edge_id:>3}] {apt_code:<16} road({road_pt[0]:.2f},{road_pt[1]:.2f}) <-> air({air_pt[0]:.2f},{air_pt[1]:.2f})  km={km:.1f}")
    edge_id += 1

roads_airways_count = edge_id - roads_maritime_count

# ── Write ───────────────────────────────────────────
geojson = {"type": "FeatureCollection", "features": features}
out_path = DATA_DIR / "multimodal_edges.geojson"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"\nTotal: {len(features)} multimodal edges")
print(f"  roads-maritime: {roads_maritime_count}")
print(f"  roads-airways:  {roads_airways_count}")
print(f"Written to {out_path}")
