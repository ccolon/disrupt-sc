"""
Extract Gulf maritime network from Global2 maritime_edges.geojson.

Strategy:
  1. Keep all edges where at least one vertex is inside the study region
     (lon 30-75, lat -5 to 35) — covers Red Sea, Persian Gulf, Arabian Sea, W. Indian Ocean
  2. Name key edges and chokepoints
  3. Flag the Hormuz strait edge with special="HORMUZ"
  4. Identify port-connector edges (edges whose endpoints are near known ports)
"""

import json
import math
import pathlib

# ── Config ──────────────────────────────────────────
STUDY_BBOX = (30, -5, 75, 35)  # lon_min, lat_min, lon_max, lat_max

# Known ports with (lon, lat) — same as roads script
PORTS = {
    "Jebel Ali":       (55.06, 25.00),
    "Khalifa Port":    (54.60, 24.53),
    "Fujairah":        (56.35, 25.13),
    "Dammam":          (50.19, 26.43),
    "Jubail":          (49.66, 27.01),
    "Jeddah":          (39.17, 21.49),
    "Hamad (Doha)":    (51.55, 25.29),
    "Shuaiba (Kuwait)":(48.16, 29.04),
    "Khalifa (BHR)":   (50.53, 26.00),
    "Sohar":           (56.73, 24.37),
    "Muscat":          (58.57, 23.63),
    "Salalah":         (54.00, 16.95),
    "Umm Qasr":        (47.95, 30.04),
    # Regional connections
    "Aden":            (45.00, 12.80),
    "Djibouti":        (43.14, 11.59),
    "Karachi":         (66.98, 24.85),
    "Mumbai":          (72.85, 18.92),
    "Suez":            (32.55, 29.95),
}

# Named nodes (network vertices near known landmarks)
# Identified from the Global2 edge inspection
NODE_NAMES = {
    # Persian Gulf
    (55.20, 25.60): "Dubai hub",
    (51.60, 26.30): "Qatar-Bahrain hub",
    (56.40, 26.40): "Hormuz north",
    (57.10, 25.50): "Hormuz south",
    (48.30, 29.10): "Kuwait approach",
    (48.90, 30.10): "Umm Qasr approach",
    (50.12, 26.97): "Dammam approach",
    (50.50, 26.50): "Bahrain approach",
    (52.10, 24.70): "Abu Dhabi approach",
    (53.80, 24.70): "UAE central",
    (54.07, 24.88): "Khalifa Port approach",
    (50.10, 28.60): "NW Gulf",
    (51.88, 25.40): "Qatar approach",
    (50.66, 26.47): "Bahrain east",
    # Strait & Gulf of Oman
    (58.96, 24.03): "Muscat approach N",
    (59.00, 24.00): "Muscat approach S",
    (60.40, 22.70): "Gulf of Oman",
    # Arabian Sea
    (63.30, 24.60): "Gwadar approach",
    (59.00, 20.00): "Arabian Sea NW",
    (54.20, 16.20): "Salalah approach",
    (70.00, 20.00): "Arabian Sea NE",
    (66.60, 24.30): "Makran coast",
    (67.00, 22.30): "Arabian Sea central",
    (72.40, 19.00): "Mumbai approach",
    # Red Sea & Gulf of Aden
    (38.90, 20.75): "Red Sea central",
    (37.00, 23.60): "Red Sea north",
    (39.40, 19.84): "Red Sea S-central",
    (41.20, 16.30): "Bab el-Mandeb N",
    (41.17, 16.37): "Bab el-Mandeb",
    (42.00, 15.00): "Bab el-Mandeb S",
    (43.30, 12.70): "Djibouti approach",
    (45.00, 12.00): "Gulf of Aden W",
    (51.00, 13.00): "Gulf of Aden E",
    (52.30, 11.60): "Socotra",
    # Suez
    (34.50, 27.00): "Hurghada / Red Sea mouth",
    (32.60, 29.70): "Suez south",
    (34.96, 29.45): "Suez east",
    # Indian Ocean
    (60.00, 10.00): "Indian Ocean NW",
    (70.00, 10.00): "Indian Ocean NE",
    (60.00, 0.00):  "Indian Ocean W",
    (49.40, 5.00):  "Somali Basin",
}

# Edges to flag as Hormuz chokepoint
# The strait is between (56.40, 26.40) "Hormuz north" and (57.10, 25.50) "Hormuz south"
HORMUZ_NODES = {(56.40, 26.40), (57.10, 25.50)}


def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def point_in_bbox(lon, lat, bbox):
    return bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]


def edge_touches_bbox(coords, bbox):
    return any(point_in_bbox(c[0], c[1], bbox) for c in coords)


def nearest_node_name(lon, lat, tol=0.5):
    """Find the named node nearest to (lon, lat), within tolerance."""
    best, best_d = None, tol
    for (nlon, nlat), name in NODE_NAMES.items():
        d = math.sqrt((lon - nlon) ** 2 + (lat - nlat) ** 2)
        if d < best_d:
            best, best_d = name, d
    return best


def nearest_port(lon, lat, tol=0.6):
    """Find the port nearest to (lon, lat), within tolerance."""
    best, best_d = None, tol
    for name, (plon, plat) in PORTS.items():
        d = math.sqrt((lon - plon) ** 2 + (lat - plat) ** 2)
        if d < best_d:
            best, best_d = name, d
    return best


def is_hormuz_edge(coords):
    """Check if this edge connects the two Hormuz nodes."""
    start = (round(coords[0][0], 1), round(coords[0][1], 1))
    end = (round(coords[-1][0], 1), round(coords[-1][1], 1))
    # Check if start-end pair matches HORMUZ_NODES (in either direction)
    if {start, end} == {(56.4, 26.4), (57.1, 25.5)}:
        return True
    # Also check exact values
    s = (round(coords[0][0], 2), round(coords[0][1], 2))
    e = (round(coords[-1][0], 2), round(coords[-1][1], 2))
    return ({s, e} == {(56.40, 26.40), (57.10, 25.50)})


# ── Main ────────────────────────────────────────────
src = pathlib.Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc\data\Global2\Transport\maritime_edges.geojson")
with open(src, encoding="utf-8") as f:
    data = json.load(f)

print(f"Source: {len(data['features'])} features")

# Filter to study region
features = []
hormuz_count = 0

for feat in data['features']:
    coords = feat['geometry']['coordinates']
    if not edge_touches_bbox(coords, STUDY_BBOX):
        continue

    props = feat['properties']
    start_lon, start_lat = coords[0][0], coords[0][1]
    end_lon, end_lat = coords[-1][0], coords[-1][1]

    # Build edge name from node names
    sname = nearest_node_name(start_lon, start_lat) or f"({start_lon:.1f}, {start_lat:.1f})"
    ename = nearest_node_name(end_lon, end_lat) or f"({end_lon:.1f}, {end_lat:.1f})"
    edge_name = f"{sname} - {ename}"

    # Check for Hormuz
    special = None
    if is_hormuz_edge(coords):
        special = "HORMUZ"
        edge_name = "Strait of Hormuz"
        hormuz_count += 1

    # Check if this is a port-connector edge
    sp = nearest_port(start_lon, start_lat)
    ep = nearest_port(end_lon, end_lat)
    port_note = None
    if sp:
        port_note = f"port:{sp}"
    if ep:
        port_note = f"port:{ep}" if not port_note else f"{port_note}|port:{ep}"

    new_props = {
        "id": len(features),
        "name": edge_name,
        "km": round(props.get("km", props.get("distance", 0)), 2),
        "capacity": props.get("capacity"),
        "special": special,
        "surface": "water",
        "class": "maritime",
        "region": "Gulf",
        "disruption": None,
        "port_connector": port_note,
    }

    new_feat = {
        "type": "Feature",
        "geometry": feat['geometry'],
        "properties": new_props,
    }
    features.append(new_feat)

print(f"Extracted: {len(features)} features for Gulf study area")
print(f"Hormuz strait edges flagged: {hormuz_count}")

# Count port connectors
port_edges = sum(1 for f in features if f['properties']['port_connector'])
print(f"Port-connector edges: {port_edges}")

# ── Write output ────────────────────────────────────
out_dir = pathlib.Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc\.claude\worktrees\distracted-gould\data\Gulf\Transport")
out_dir.mkdir(parents=True, exist_ok=True)

geojson = {
    "type": "FeatureCollection",
    "features": features,
}

out_path = out_dir / "maritime_edges.geojson"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"\nWritten to {out_path}")

# Print Hormuz and nearby edges for verification
print("\n--- Hormuz and nearby strait edges ---")
for feat in features:
    p = feat['properties']
    c = feat['geometry']['coordinates']
    s, e = c[0], c[-1]
    if any(56 <= c_[0] <= 58 and 25 <= c_[1] <= 27 for c_ in [s, e]):
        flag = " *** HORMUZ ***" if p['special'] == 'HORMUZ' else ""
        print(f"  [{p['id']:>3}] {p['name']:<45} km={p['km']:>7.0f}{flag}")
