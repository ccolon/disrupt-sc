"""Light Ukraine + Moldova network so UKR/MDA attach at Kyiv/Chisinau (v8).

Rationale (WB BCP counts, Sep 2026): one road node per country cannot
reproduce the observed crossing/mode split at the RO-UA and RO-MD borders
(half the UA flow is rail; four MD road crossings). Same cure as the EUR
gateway problem: attach the country at its economic center and let per-cargo
routing choose the crossing.

What exists already: TEN-T rail covers UA and MD (Kyiv, Odesa, Chisinau,
all four RO rail crossings, one connected component) - it only lacks rail
stitches at Vicsani and Halmeu and gauge-break marking. TEN-T has NO UA/MD
roads and no Danube-port waterway links.

This script (idempotent - reruns replace its own rows):
  roads     hand-built skeleton along the corridors of the WB maps
            (class 'foreign_skeleton' -> default speed), final crossing
            edges end exactly on a RO road node and carry special='border'
  railways  2 new stitches (Vicsani, Halmeu); special='border' stamped on
            the four 1520<->1435 gauge-break crossings (also Ungheni,
            Giurgiulesti stitches)
  waterways Reni + Izmail port links to the maritime Danube
  multimodal road-rail connectors at Kyiv/Vinnytsia/Odesa/Chisinau, and
            road-water + rail-water at Reni and Izmail

Border costs are then driven by logistics.border_crossing_times/fees
(edges whose `special` contains 'border'), the calibration lever for the
rail/road split at the border.

Run in the dsc env: python romania_add_ua_md_network.py
"""

from __future__ import annotations

import math

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

T = r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Transport"
GPKG = T + "/transport.gpkg"
MM = T + "/multimodal.gpkg"
MARK = "UAMD:"          # name prefix marking rows owned by this script
ROAD_KM_FACTOR = 1.25   # straight line -> road distance
WATER_KM_FACTOR = 1.15

NODES = {
    # Ukraine
    "Kyiv": (30.52, 50.45), "Zhytomyr": (28.66, 50.25), "Rivne": (26.25, 50.62),
    "Lviv": (24.03, 49.84), "Mukachevo": (22.72, 48.44), "Dyakove": (23.03, 47.99),
    "Vinnytsia": (28.47, 49.23), "Chernivtsi": (25.93, 48.29), "Porubne": (25.99, 48.10),
    "MohylivP": (27.79, 48.44), "Uman": (30.22, 48.75), "Odesa": (30.73, 46.48),
    "VadulSiretUA": (26.07, 47.99),
    "Orlivka": (28.41, 45.25), "Izmail": (28.83, 45.33), "Reni": (28.28, 45.46),
    # Moldova
    "Chisinau": (28.86, 47.02), "Leuseni": (28.15, 46.57), "SculeniMD": (27.32, 47.33),
    "Balti": (27.92, 47.76), "Comrat": (28.65, 46.30), "CahulMD": (28.20, 45.90),
    "Basarabeasca": (28.96, 46.33), "Giurgiulesti": (28.20, 45.47),
}

# (from, to, country_code, border?)  border edges end on a snapped RO road node
ROADS = [
    ("Kyiv", "Zhytomyr", "UA", None), ("Zhytomyr", "Rivne", "UA", None),
    ("Rivne", "Lviv", "UA", None), ("Lviv", "Mukachevo", "UA", None),
    ("Mukachevo", "Dyakove", "UA", None),
    ("Dyakove", "RO@Halmeu", "UA", "Dyakove-Halmeu"),
    ("Zhytomyr", "Vinnytsia", "UA", None), ("Vinnytsia", "Chernivtsi", "UA", None),
    ("Chernivtsi", "Porubne", "UA", None),
    ("Porubne", "RO@Siret", "UA", "Porubne-Siret"),
    ("Vinnytsia", "MohylivP", "UA", None),
    ("Kyiv", "Uman", "UA", None), ("Uman", "Odesa", "UA", None),
    ("Odesa", "Orlivka", "UA", None),
    ("Orlivka", "RO@Isaccea", "UA", "Orlivka-Isaccea ferry"),
    ("Odesa", "Izmail", "UA", None), ("Izmail", "Reni", "UA", None),
    ("Reni", "Giurgiulesti", "UA; MD", None),
    ("Chisinau", "Leuseni", "MD", None),
    ("Leuseni", "RO@Albita", "MD", "Leuseni-Albita"),
    ("Chisinau", "SculeniMD", "MD", None),
    ("SculeniMD", "RO@Sculeni", "MD", "Sculeni"),
    ("Chisinau", "Balti", "MD", None), ("Balti", "MohylivP", "MD; UA", None),
    ("Balti", "SculeniMD", "MD", None),
    ("Chisinau", "Comrat", "MD", None), ("Comrat", "CahulMD", "MD", None),
    ("CahulMD", "RO@Oancea", "MD", "Cahul-Oancea"),
    ("Comrat", "Giurgiulesti", "MD", None),
    ("Giurgiulesti", "RO@GalatiRoad", "MD", "Giurgiulesti-Galati"),
]

# RO-side snap targets: nearest DOMESTIC node of the mode to these points
RO_SNAPS = {
    "RO@Halmeu": ("roads", (23.02, 47.97)),
    "RO@Siret": ("roads", (26.06, 47.95)),
    "RO@Isaccea": ("roads", (28.42, 45.27)),
    "RO@Albita": ("roads", (28.10, 46.55)),
    "RO@Sculeni": ("roads", (27.30, 47.32)),
    "RO@Oancea": ("roads", (28.05, 45.92)),
    "RO@GalatiRoad": ("roads", (28.05, 45.44)),
}

# TEN-T rail lacks the Ternopil-Chernivtsi-Vadul-Siret line: build it as a
# skeleton branch from the nearest true TEN-T rail node, then stitch to RO.
RAIL_SKELETON = [
    # (anchor: TEN-T rail node nearest this point, to NODES key)
    ((25.601, 49.554), "Chernivtsi", "TernopilTENT-Chernivtsi rail"),
]
RAIL_SKELETON_EDGES = [("Chernivtsi", "VadulSiretUA", "Chernivtsi-VadulSiret rail")]
RAIL_STITCHES = [  # (UA-side NODES key or point, RO-side point, name)
    ("VadulSiretUA", (26.03, 47.88), "rail gauge break Vadul-Siret/Vicsani"),
    ((23.03, 47.99), (23.02, 47.96), "rail gauge break Dyakove/Halmeu"),
]
GAUGE_BREAK_EXISTING = [(27.80, 47.21), (28.20, 45.47)]  # Ungheni, Giurgiulesti stitches

WATER_LINKS = [("Reni", "Reni-Danube link"), ("Izmail", "Izmail-Danube link")]
ROAD_RAIL_CONNECTORS = ["Kyiv", "Vinnytsia", "Odesa", "Chisinau"]
PORT_CONNECTORS = ["Reni", "Izmail"]  # road-water and rail-water


def hav_km(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))


def endpoints(gdf):
    pts = set()
    for geom in gdf.geometry:
        cs = list(geom.coords)
        pts.add((round(cs[0][0], 6), round(cs[0][1], 6)))
        pts.add((round(cs[-1][0], 6), round(cs[-1][1], 6)))
    return pts


def nearest(pts, target):
    return min(pts, key=lambda p: hav_km(p, target))


def main():
    layers = {lay: gpd.read_file(GPKG, layer=lay) for lay in ("roads", "railways", "waterways")}
    mm = gpd.read_file(MM)

    # ---- idempotency: drop rows this script added before -----------------
    for lay in layers:
        g = layers[lay]
        own = g["name"].astype(str).str.startswith(MARK)
        if own.any():
            print(f"{lay}: removing {own.sum()} previous {MARK} rows")
            layers[lay] = g[~own].reset_index(drop=True)
    own_mm = mm["multimodes"].astype(str).str.startswith(MARK)
    if "name" in mm.columns:
        own_mm |= mm["name"].astype(str).str.startswith(MARK)
    if own_mm.any():
        mm = mm[~own_mm].reset_index(drop=True)

    # sanity: border-cost marker must not already exist elsewhere
    for lay, g in layers.items():
        pre = g["special"].astype(str).str.contains("border|custom", na=False) & \
              ~g["name"].astype(str).str.startswith(MARK)
        pre &= ~g["name"].astype(str).str.contains("gauge break", na=False)
        if pre.any():
            print(f"WARNING: {lay} has {pre.sum()} pre-existing special~border edges")

    dom_nodes = {lay: endpoints(layers[lay][layers[lay]["foreign"].fillna(0) != 1])
                 for lay in layers}
    rail_foreign_nodes = endpoints(layers["railways"][layers["railways"]["foreign"].fillna(0) == 1])

    def resolve(name):
        if name in NODES:
            return NODES[name]
        mode, pt = RO_SNAPS[name]
        return nearest(dom_nodes[mode], pt)

    template = {c: None for c in layers["roads"].columns if c != "geometry"}

    # ---- roads skeleton --------------------------------------------------
    new_roads = []
    for a, b, cc, border in ROADS:
        pa, pb = resolve(a), resolve(b)
        row = dict(template)
        row.update({
            "type": "roads", "class": "foreign_skeleton",
            "km": round(hav_km(pa, pb) * ROAD_KM_FACTOR, 2),
            "name": f"{MARK}{border or f'{a}-{b}'}",
            "special": "border" if border else None,
            "foreign": 1, "country_code": cc,
        })
        row["geometry"] = LineString([pa, pb])
        new_roads.append(row)
    layers["roads"] = pd.concat(
        [layers["roads"], gpd.GeoDataFrame(new_roads, crs=layers["roads"].crs)],
        ignore_index=True)
    print(f"roads: +{len(new_roads)} skeleton edges")

    # ---- rail stitches + gauge-break marking -----------------------------
    rtempl = {c: None for c in layers["railways"].columns if c != "geometry"}
    new_rail = []

    def rail_edge(a, b, name, special=None, cls="foreign_skeleton", factor=1.15):
        row = dict(rtempl)
        row.update({
            "type": "railways", "class": cls,
            "km": round(hav_km(a, b) * factor, 2),
            "name": f"{MARK}{name}", "special": special,
            "foreign": 1, "country_code": "UA" if special is None else "border",
        })
        row["geometry"] = LineString([a, b])
        new_rail.append(row)

    for anchor_pt, to_key, name in RAIL_SKELETON:
        a = nearest(rail_foreign_nodes, anchor_pt)
        if hav_km(a, anchor_pt) > 30:
            raise SystemExit(f"{name}: TEN-T anchor {a} is {hav_km(a, anchor_pt):.0f} km "
                             f"from expected {anchor_pt} - check the TEN-T rail layer")
        rail_edge(a, NODES[to_key], name)
        print(f"railways: skeleton {name}: {hav_km(a, NODES[to_key]):.0f} km")
    for a_key, b_key, name in RAIL_SKELETON_EDGES:
        rail_edge(NODES[a_key], NODES[b_key], name)
        print(f"railways: skeleton {name}: {hav_km(NODES[a_key], NODES[b_key]):.0f} km")

    for ua_pt, ro_pt, name in RAIL_STITCHES:
        a = NODES[ua_pt] if isinstance(ua_pt, str) else nearest(rail_foreign_nodes, ua_pt)
        b = nearest(dom_nodes["railways"], ro_pt)
        if hav_km(a, b) < 0.05:
            raise SystemExit(f"stitch {name}: endpoints coincide - check node sets")
        row = dict(rtempl)
        row.update({
            "type": "railways", "class": "stitch",
            "km": round(hav_km(a, b) * 1.1, 2),
            "name": f"{MARK}{name}", "special": "border",
            "foreign": 1, "country_code": "border",
        })
        row["geometry"] = LineString([a, b])
        new_rail.append(row)
        print(f"railways: stitch {name}: {hav_km(a, b):.1f} km")
    layers["railways"] = pd.concat(
        [layers["railways"], gpd.GeoDataFrame(new_rail, crs=layers["railways"].crs)],
        ignore_index=True)
    g = layers["railways"]
    for pt in GAUGE_BREAK_EXISTING:
        cent = g.geometry.centroid
        d = [hav_km((x, y), pt) for x, y in zip(cent.x, cent.y)]
        i = int(pd.Series(d).idxmin())
        if str(g.at[i, "class"]) == "stitch":
            g.at[i, "special"] = "border"
            print(f"railways: marked existing stitch at {pt} as gauge break")

    # ---- waterway port links --------------------------------------------
    wtempl = {c: None for c in layers["waterways"].columns if c != "geometry"}
    new_water = []
    for port, name in WATER_LINKS:
        a = NODES[port]
        b = nearest(dom_nodes["waterways"], a)
        row = dict(wtempl)
        row.update({
            "type": "waterways", "class": "foreign_skeleton",
            "km": round(hav_km(a, b) * WATER_KM_FACTOR, 2),
            "name": f"{MARK}{name}", "foreign": 1, "country_code": "UA",
        })
        row["geometry"] = LineString([a, b])
        new_water.append(row)
        print(f"waterways: {name}: {hav_km(a, b):.1f} km to domestic node")
    layers["waterways"] = pd.concat(
        [layers["waterways"], gpd.GeoDataFrame(new_water, crs=layers["waterways"].crs)],
        ignore_index=True)

    # ---- multimodal connectors ------------------------------------------
    road_nodes = endpoints(layers["roads"])
    rail_nodes = endpoints(layers["railways"])
    water_nodes = endpoints(layers["waterways"])
    next_id = int(mm["id"].max()) + 1
    new_mm = []

    def connector(city, m1, nodes1, m2, nodes2):
        nonlocal next_id
        a, b = nearest(nodes1, NODES[city]), nearest(nodes2, NODES[city])
        d_m = hav_km(a, b) * 1000
        new_mm.append({
            "multimodes": f"{m1}-{m2}", "name": f"{MARK}{m1}-{m2} {city}",
            "distance_m": round(d_m, 1),
            "km": round(d_m / 1000, 3), "from_mode": m1, "to_mode": m2,
            "id": next_id, "foreign": 1, "geometry": LineString([a, b]),
        })
        next_id += 1

    for city in ROAD_RAIL_CONNECTORS:
        connector(city, "roads", road_nodes, "railways", rail_nodes)
    for city in PORT_CONNECTORS:
        connector(city, "roads", road_nodes, "waterways", water_nodes)
        connector(city, "railways", rail_nodes, "waterways", water_nodes)
    mm = pd.concat([mm, gpd.GeoDataFrame(new_mm, crs=mm.crs)], ignore_index=True)
    print(f"multimodal: +{len(new_mm)} connectors")

    # ---- write -----------------------------------------------------------
    for lay, g in layers.items():
        ids = pd.to_numeric(g["id"], errors="coerce")
        n_missing = ids.isna().sum()
        if n_missing:
            start = int(ids.max()) + 1
            ids.loc[ids.isna()] = range(start, start + n_missing)
        g["id"] = ids.astype("int64")
        gpd.GeoDataFrame(g, crs=layers[lay].crs).to_file(GPKG, layer=lay, driver="GPKG")
    # keep untouched layers by rewriting them (GPKG to_file replaces one layer)
    mm.to_file(MM, layer="multimodal", driver="GPKG")
    print("written transport.gpkg / multimodal.gpkg")


if __name__ == "__main__":
    main()
