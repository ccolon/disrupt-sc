"""
Build airways_edges.geojson for the Gulf scenario.

Strategy:
  - Full mesh between major Gulf airports (direct flights exist between all)
  - One link from each Gulf airport to one representative airport per external trade bloc
  - Straight-line geometry (great circle approximated as LineString)
"""

import json
import math
import pathlib
from itertools import combinations

# ── Gulf airports ───────────────────────────────────
GULF_AIRPORTS = {
    "DXB": {"lon": 55.36, "lat": 25.25, "label": "Dubai Intl (DXB)",          "region": "UAE"},
    "AUH": {"lon": 54.65, "lat": 24.43, "label": "Abu Dhabi Intl (AUH)",      "region": "UAE"},
    "DOH": {"lon": 51.61, "lat": 25.26, "label": "Hamad Intl (DOH)",          "region": "QAT"},
    "RUH": {"lon": 46.70, "lat": 24.96, "label": "King Khalid Intl (RUH)",    "region": "SAU"},
    "JED": {"lon": 39.16, "lat": 21.68, "label": "King Abdulaziz Intl (JED)", "region": "SAU"},
    "DMM": {"lon": 49.80, "lat": 26.47, "label": "King Fahd Intl (DMM)",      "region": "SAU"},
    "KWI": {"lon": 47.97, "lat": 29.23, "label": "Kuwait Intl (KWI)",         "region": "KWT"},
    "BAH": {"lon": 50.63, "lat": 26.27, "label": "Bahrain Intl (BAH)",        "region": "BHR"},
    "MCT": {"lon": 58.28, "lat": 23.59, "label": "Muscat Intl (MCT)",         "region": "OMN"},
    "BGW": {"lon": 44.23, "lat": 33.26, "label": "Baghdad Intl (BGW)",        "region": "IRQ"},
}

# ── External trade bloc representative airports ────
EXTERNAL_AIRPORTS = {
    "FRA": {"lon":  8.57, "lat": 50.03, "label": "Frankfurt (FRA)",    "bloc": "EU"},
    "IST": {"lon": 28.81, "lat": 41.26, "label": "Istanbul (IST)",     "bloc": "Turkey"},
    "BOM": {"lon": 72.87, "lat": 19.09, "label": "Mumbai (BOM)",       "bloc": "India"},
    "PVG": {"lon": 121.81,"lat": 31.14, "label": "Shanghai (PVG)",     "bloc": "China"},
    "SIN": {"lon": 103.99,"lat": 1.35,  "label": "Singapore (SIN)",    "bloc": "SE Asia"},
    "JFK": {"lon": -73.78,"lat": 40.64, "label": "New York (JFK)",     "bloc": "N. America"},
    "GRU": {"lon": -46.47,"lat": -23.43,"label": "Sao Paulo (GRU)",    "bloc": "S. America"},
    "NBO": {"lon": 36.93, "lat": -1.32, "label": "Nairobi (NBO)",      "bloc": "E. Africa"},
    "SYD": {"lon": 151.18,"lat": -33.95,"label": "Sydney (SYD)",       "bloc": "Australia"},
    "NRT": {"lon": 140.39,"lat": 35.77, "label": "Tokyo (NRT)",        "bloc": "Japan/Korea"},
}


def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


features = []
edge_id = 0

# ── 1. Full mesh between Gulf airports ─────────────
for (code1, a1), (code2, a2) in combinations(GULF_AIRPORTS.items(), 2):
    km = round(haversine_km(a1["lon"], a1["lat"], a2["lon"], a2["lat"]), 2)
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[a1["lon"], a1["lat"]], [a2["lon"], a2["lat"]]],
        },
        "properties": {
            "id": edge_id,
            "name": f"{code1}-{code2}",
            "class": "airway",
            "surface": "air",
            "region": f"{a1['region']}-{a2['region']}",
            "special": None,
            "km": km,
            "capacity": None,
            "disruption": None,
        },
    })
    edge_id += 1

gulf_internal = edge_id
print(f"Gulf internal (full mesh): {gulf_internal} edges")

# ── 2. Gulf airports <-> External bloc airports ────
for g_code, ga in GULF_AIRPORTS.items():
    for e_code, ea in EXTERNAL_AIRPORTS.items():
        km = round(haversine_km(ga["lon"], ga["lat"], ea["lon"], ea["lat"]), 2)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[ga["lon"], ga["lat"]], [ea["lon"], ea["lat"]]],
            },
            "properties": {
                "id": edge_id,
                "name": f"{g_code}-{e_code}",
                "class": "airway",
                "surface": "air",
                "region": f"{ga['region']}-{ea['bloc']}",
                "special": None,
                "km": km,
                "capacity": None,
                "disruption": None,
            },
        })
        edge_id += 1

gulf_external = edge_id - gulf_internal
print(f"Gulf-External links: {gulf_external} edges ({len(GULF_AIRPORTS)} airports x {len(EXTERNAL_AIRPORTS)} blocs)")
print(f"Total: {len(features)} edges")

# ── Write ───────────────────────────────────────────
out_dir = pathlib.Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc\.claude\worktrees\distracted-gould\data\Gulf\Transport")
out_dir.mkdir(parents=True, exist_ok=True)

geojson = {"type": "FeatureCollection", "features": features}
out_path = out_dir / "airways_edges.geojson"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"\nWritten to {out_path}")

# Summary
print(f"\nGulf airports ({len(GULF_AIRPORTS)}):")
for code, a in GULF_AIRPORTS.items():
    print(f"  {code} - {a['label']}")
print(f"\nExternal blocs ({len(EXTERNAL_AIRPORTS)}):")
for code, a in EXTERNAL_AIRPORTS.items():
    print(f"  {code} - {a['label']} [{a['bloc']}]")
