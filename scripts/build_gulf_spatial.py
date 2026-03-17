"""
Build countries.geojson and households.geojson for the Gulf scenario.

countries.geojson: One Point per region (Gulf countries + external trade blocs).
  - Gulf countries: centroid of country
  - External blocs: representative point (capital of largest economy or geographic center)

households.geojson: Main cities in the 7 Gulf countries with population.
"""

import json
import pathlib

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "Gulf" / "Spatial"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────
# 1. Countries / trade blocs — one point each
# ──────────────────────────────────────────────────

countries = [
    # Gulf states (approximate centroid)
    {"region": "ARE", "name": "United Arab Emirates",  "lon": 54.5,  "lat": 24.5},
    {"region": "SAU", "name": "Saudi Arabia",          "lon": 45.0,  "lat": 24.0},
    {"region": "QAT", "name": "Qatar",                 "lon": 51.5,  "lat": 25.3},
    {"region": "KWT", "name": "Kuwait",                "lon": 47.5,  "lat": 29.3},
    {"region": "BHR", "name": "Bahrain",               "lon": 50.5,  "lat": 26.0},
    {"region": "OMN", "name": "Oman",                  "lon": 57.0,  "lat": 21.5},
    {"region": "IRQ", "name": "Iraq",                  "lon": 44.0,  "lat": 33.0},
    # External trade blocs (representative points — capital of dominant economy)
    {"region": "CHN",      "name": "China",            "lon": 116.4, "lat": 39.9},   # Beijing
    {"region": "IND",      "name": "India",            "lon": 77.2,  "lat": 28.6},   # Delhi
    {"region": "Europe",   "name": "Europe",           "lon": 10.0,  "lat": 50.0},   # Central Europe
    {"region": "East_Asia", "name": "East Asia",       "lon": 135.0, "lat": 35.0},   # Tokyo area
    {"region": "Americas", "name": "Americas",         "lon": -77.0, "lat": 39.0},   # Washington DC area
    {"region": "Africa",   "name": "Africa",           "lon": 30.0,  "lat": 0.0},    # Central Africa
    {"region": "Oceania",  "name": "Oceania",          "lon": 149.1, "lat": -35.3},  # Canberra
    {"region": "ROW",      "name": "Rest of World",    "lon": 70.0,  "lat": 30.0},   # Central Asia
]

countries_features = []
for c in countries:
    countries_features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
        "properties": {"region": c["region"], "name": c["name"]},
    })

countries_geojson = {"type": "FeatureCollection", "features": countries_features}

out_countries = OUT_DIR / "countries.geojson"
with open(out_countries, "w", encoding="utf-8") as f:
    json.dump(countries_geojson, f, indent=2, ensure_ascii=False)
print(f"Written {len(countries_features)} countries to {out_countries}")

# ──────────────────────────────────────────────────
# 2. Households — main cities in Gulf countries
# ──────────────────────────────────────────────────

# Sources: approximate 2023-2025 metro populations
# Only Gulf countries get household points (internal demand nodes)
# External blocs do NOT need household points — they interact via final_demand/exports

households = [
    # UAE — total ~10M
    {"region": "ARE", "city": "Dubai",         "lon": 55.27, "lat": 25.20, "population": 3500000},
    {"region": "ARE", "city": "Abu Dhabi",     "lon": 54.37, "lat": 24.45, "population": 1800000},
    {"region": "ARE", "city": "Sharjah",       "lon": 55.39, "lat": 25.34, "population": 1700000},
    {"region": "ARE", "city": "Al Ain",        "lon": 55.76, "lat": 24.21, "population":  800000},
    {"region": "ARE", "city": "Ajman",         "lon": 55.44, "lat": 25.41, "population":  500000},
    {"region": "ARE", "city": "Ras Al Khaimah","lon": 55.98, "lat": 25.79, "population":  400000},
    {"region": "ARE", "city": "Fujairah",      "lon": 56.33, "lat": 25.13, "population":  250000},

    # SAU — total ~36M
    {"region": "SAU", "city": "Riyadh",        "lon": 46.72, "lat": 24.71, "population": 7500000},
    {"region": "SAU", "city": "Jeddah",        "lon": 39.17, "lat": 21.49, "population": 4600000},
    {"region": "SAU", "city": "Mecca",         "lon": 39.83, "lat": 21.43, "population": 2100000},
    {"region": "SAU", "city": "Medina",        "lon": 39.61, "lat": 24.47, "population": 1500000},
    {"region": "SAU", "city": "Dammam",        "lon": 50.10, "lat": 26.43, "population": 2300000},
    {"region": "SAU", "city": "Khobar",        "lon": 50.21, "lat": 26.28, "population":  500000},
    {"region": "SAU", "city": "Jubail",        "lon": 49.66, "lat": 27.01, "population":  400000},
    {"region": "SAU", "city": "Hofuf",         "lon": 49.59, "lat": 25.38, "population":  700000},
    {"region": "SAU", "city": "Tabuk",         "lon": 36.57, "lat": 28.38, "population":  600000},
    {"region": "SAU", "city": "Abha",          "lon": 42.50, "lat": 18.22, "population":  500000},

    # QAT — total ~3M
    {"region": "QAT", "city": "Doha",          "lon": 51.53, "lat": 25.29, "population": 2400000},
    {"region": "QAT", "city": "Al Wakrah",     "lon": 51.60, "lat": 25.17, "population":  350000},
    {"region": "QAT", "city": "Al Khor",       "lon": 51.50, "lat": 25.68, "population":  200000},

    # KWT — total ~4.5M
    {"region": "KWT", "city": "Kuwait City",   "lon": 47.98, "lat": 29.38, "population": 3000000},
    {"region": "KWT", "city": "Hawalli",       "lon": 48.03, "lat": 29.33, "population":  900000},
    {"region": "KWT", "city": "Ahmadi",        "lon": 48.08, "lat": 29.08, "population":  600000},

    # BHR — total ~1.5M
    {"region": "BHR", "city": "Manama",        "lon": 50.58, "lat": 26.22, "population":  700000},
    {"region": "BHR", "city": "Muharraq",      "lon": 50.62, "lat": 26.26, "population":  300000},
    {"region": "BHR", "city": "Riffa",         "lon": 50.56, "lat": 26.13, "population":  250000},
    {"region": "BHR", "city": "Hamad Town",    "lon": 50.47, "lat": 26.12, "population":  200000},

    # OMN — total ~5M
    {"region": "OMN", "city": "Muscat",        "lon": 58.41, "lat": 23.59, "population": 1500000},
    {"region": "OMN", "city": "Sohar",         "lon": 56.73, "lat": 24.37, "population":  300000},
    {"region": "OMN", "city": "Salalah",       "lon": 54.09, "lat": 17.02, "population":  400000},
    {"region": "OMN", "city": "Nizwa",         "lon": 57.53, "lat": 22.93, "population":  200000},
    {"region": "OMN", "city": "Sur",           "lon": 59.53, "lat": 22.57, "population":  150000},

    # IRQ — total ~43M (but focused on southern/Gulf-connected cities)
    {"region": "IRQ", "city": "Baghdad",       "lon": 44.37, "lat": 33.31, "population": 8500000},
    {"region": "IRQ", "city": "Basra",         "lon": 47.78, "lat": 30.51, "population": 2800000},
    {"region": "IRQ", "city": "Erbil",         "lon": 44.01, "lat": 36.19, "population": 1500000},
    {"region": "IRQ", "city": "Mosul",         "lon": 43.14, "lat": 36.34, "population": 1800000},
    {"region": "IRQ", "city": "Najaf",         "lon": 44.35, "lat": 32.00, "population":  700000},
    {"region": "IRQ", "city": "Karbala",       "lon": 44.02, "lat": 32.62, "population":  600000},
]

hh_features = []
for h in households:
    hh_features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [h["lon"], h["lat"]]},
        "properties": {
            "region": h["region"],
            "city": h["city"],
            "population": h["population"],
        },
    })

hh_geojson = {"type": "FeatureCollection", "features": hh_features}

out_hh = OUT_DIR / "households.geojson"
with open(out_hh, "w", encoding="utf-8") as f:
    json.dump(hh_geojson, f, indent=2, ensure_ascii=False)

print(f"Written {len(hh_features)} household points to {out_hh}")

# Summary
print("\n=== Spatial Summary ===")
for region in ["ARE", "SAU", "QAT", "KWT", "BHR", "OMN", "IRQ"]:
    cities = [h for h in households if h["region"] == region]
    total_pop = sum(h["population"] for h in cities)
    print(f"  {region}: {len(cities)} cities, pop {total_pop:,}")
total = sum(h["population"] for h in households)
print(f"  TOTAL: {len(households)} cities, pop {total:,}")
