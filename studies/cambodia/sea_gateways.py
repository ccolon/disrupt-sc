"""Sea gateways for the Cambodia scope: overseas partners at sea, the port of entry chosen by routing (7 Nov 2026).

Why. Flow validation against the 2016 JICA brochure (Paper_Cambodia/pipeline/validation/logistics2016_flows.md, GDCE
2015) found the v2 scope sending trade through the wrong gateways. With `country_attachment: roads` a partner bloc
attaches to the road node nearest to its point, and the road network runs past the borders: AFR, AME, EUR, ROW and
THA entered at Bangkok via Poipet, ASI and LAO at Vientiane via NR7, OCE and VNM at Ho Chi Minh City via Bavet, and
Sihanoukville carried nothing. In 2015 Sihanoukville handled 37 % of import tonnes and ~58 % of gateway TEU.

What this script changes in disrupt-sc-data/Cambodia (the paper sets `country_attachment: any` in paper_config.yaml):
  1. Spatial/countries.geojson: the overseas blocs (AFR, AME, ASI, EUR, OCE, ROW) are placed on the end node of their
     sea lane in the maritime layer (Marseille, US east coast, Dar es Salaam, South China, north of Australia), so
     that each attaches to the maritime layer and reaches Cambodia through Sihanoukville or through Cai Mep / Ho Chi
     Minh City (barge on the Mekong, or road via Bavet), whichever routing finds cheaper. VNM is placed on the Ho Chi
     Minh City road node (its own point lay 0.004 deg closer to the maritime node there). THA and LAO are unchanged
     (Bangkok, Vientiane: land partners).
  2. Transport/transport.gpkg, maritime layer: one edge from the Sihanoukville anchorage to the Singapore Strait
     approach node. Without it the only sea lane out of Sihanoukville ran east of Vietnam to a hub at 111.1 E and
     back to Singapore (~1,500 km more than the direct route) for every Europe-, America-, Africa- or Oceania-bound
     ship.
  3. Transport/transport.gpkg, roads layer: names for the Poipet and NR7 (Laos) crossings (for capacities and
     name-specific costs), and `custom` added to the NR7 crossing's special (border time and fee now apply, as at
     Poipet and Bavet; it had none).
     The 21 road stubs of 60 m tagged `border` inside Preah Sihanouk, Kampot and Koh Kong provinces (joins of a
     provincial network, not international crossings) become `provincial_stitch`: they charged the road border
     time and fee on every route into or out of the Sihanoukville area.
  4. Transport/transport.gpkg, waterways layer: the Mekong border edge (Kaam Samnor / Vinh Xuong) named.
  5. Transport/multimodal.gpkg: `port_name` on the port connectors (Sihanoukville, Phnom Penh, Cai Mep, Ho Chi Minh
     City), for the per-port extras of `logistics.dwell_times.by_port` / `loading_fees.by_port`.

Usage:
    python studies/cambodia/sea_gateways.py            # report only
    python studies/cambodia/sea_gateways.py --write    # write (backups *_before_sea_gateways.*), idempotent
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import pyogrio
from shapely.geometry import LineString, Point

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1].parent / "disrupt-sc-data" / "Cambodia"
TOL = 2e-3  # deg: a target is matched to the network endpoint within this distance

# Sea-lane end nodes of the maritime layer (approximate; matched to the exact endpoint)
BLOC_NODE = {"EUR": (6.007, 43.170), "AME": (-76.663, 34.718), "AFR": (39.461, -6.961),
             "ROW": (39.461, -6.961), "ASI": (113.260, 19.977), "OCE": (138.575, -11.106)}
VNM_ROAD_NODE = (106.743, 10.718)          # Ho Chi Minh City end of the Bavet road edge
SHV_ANCHORAGE = (103.395, 10.627)
SINGAPORE_APPROACH = (104.27625, 1.52375)  # north end of the Singapore Strait border edge, where the Vung Tau lane joins
PORTS = {  # connector id in multimodal.gpkg: (multimodes, sea/river-side end near, port_name)
    0: ("roads-maritime", (103.515, 10.651), "Sihanoukville"), 3: ("roads-maritime", (103.516, 10.651), "Sihanoukville"),
    2: ("roads-maritime", (103.395, 10.627), "Sihanoukville"), 11: ("railways-maritime", (103.515, 10.651), "Sihanoukville"),
    12: ("railways-maritime", (103.395, 10.627), "Sihanoukville"), 13: ("railways-maritime", (103.516, 10.651), "Sihanoukville"),
    1: ("roads-maritime", (106.747, 10.719), "HoChiMinh"), 14: ("waterways-maritime", (107.023, 10.534), "CaiMep"),
    7: ("roads-waterways", (104.922, 11.583), "PhnomPenh"), 8: ("roads-waterways", (105.143, 11.475), "PhnomPenh"),
    10: ("railways-waterways", (104.922, 11.583), "PhnomPenh"),
}


def endpoints(gdf):
    out = []
    for i, g in zip(gdf.index, gdf.geometry):
        cs = list(g.coords) if g.geom_type == "LineString" else [c for ln in g.geoms for c in ln.coords]
        out += [(i, cs[0][:2]), (i, cs[-1][:2])]
    return out


def find(gdf, xy, what, tol=TOL):
    hits = {(round(c[0], 6), round(c[1], 6)) for _, c in endpoints(gdf)
            if abs(c[0] - xy[0]) < tol and abs(c[1] - xy[1]) < tol}
    if len(hits) != 1:
        raise SystemExit(f"{what}: {len(hits)} endpoints within {TOL} deg of {xy}: {sorted(hits)}")
    return hits.pop()


def degree(gdf, xy):
    return sum(1 for _, c in endpoints(gdf) if (round(c[0], 6), round(c[1], 6)) == xy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    gpkg, mm_path, cpath = DATA / "Transport" / "transport.gpkg", DATA / "Transport" / "multimodal.gpkg", \
        DATA / "Spatial" / "countries.geojson"
    layers = [l[0] for l in pyogrio.list_layers(gpkg)]
    sea = gpd.read_file(gpkg, layer="maritime")
    roads = gpd.read_file(gpkg, layer="roads")
    ww = gpd.read_file(gpkg, layer="waterways")
    mm = gpd.read_file(mm_path, layer="multimodal")
    cg = gpd.read_file(cpath)

    # 1. countries
    for bloc, xy in BLOC_NODE.items():
        node = find(sea, xy, f"{bloc} sea-lane end")
        if degree(sea, node) != 1:
            raise SystemExit(f"{bloc}: {node} is not a sea-lane end (degree {degree(sea, node)})")
        cg.loc[cg["region"] == bloc, "geometry"] = Point(node)
        print(f"countries: {bloc} -> maritime end node {node}")
    vnm = find(roads, VNM_ROAD_NODE, "VNM road node")
    cg.loc[cg["region"] == "VNM", "geometry"] = Point(vnm)
    print(f"countries: VNM -> road node {vnm}")

    # 2. Sihanoukville - Singapore sea lane
    anch, sgp = find(sea, SHV_ANCHORAGE, "SHV anchorage"), find(sea, SINGAPORE_APPROACH, "Singapore approach", 1e-4)
    lane = LineString([anch, sgp])
    exists = any(g.equals(lane) or g.equals(LineString([sgp, anch])) for g in sea.geometry)
    if not exists:
        km = gpd.GeoSeries([lane], crs=sea.crs).to_crs(epsg=8857).length.iloc[0] / 1000
        row = {c: None for c in sea.columns}
        row.update({"id": int(sea["id"].max()) + 1, "km": km, "geometry": lane})
        sea = gpd.GeoDataFrame(pd_concat(sea, row), geometry="geometry", crs=sea.crs)
        print(f"maritime: + Sihanoukville anchorage {anch} -> Singapore approach {sgp}, {km:.0f} km")
    else:
        print("maritime: Sihanoukville - Singapore lane already present")

    # 3. road crossings
    def set_road(mask_fn, name, special=None, what=""):
        m = roads.apply(mask_fn, axis=1)
        if m.sum() != 1:
            raise SystemExit(f"roads: {what} matches {int(m.sum())} edges")
        roads.loc[m, "name"] = name
        if special is not None:
            roads.loc[m, "special"] = special
        print(f"roads: {what} -> name {name!r}" + (f", special {special!r}" if special else ""))
    set_road(lambda r: "poipet" in str(r["special"]), "poipet_border_crossing", what="Poipet crossing")
    set_road(lambda r: r["name"] == "nr7_laos_border"
             or (str(r["special"]) == "international" and "National Road 7" in str(r["name"])),
             "nr7_laos_border", "custom, nr7, international", what="NR7 crossing to Laos")

    # 3b. the 60 m road stubs tagged `border` are not international crossings: 21 joins inside Preah Sihanouk,
    # Kampot and Koh Kong provinces (where a provincial network was stitched to the national one). With the tag,
    # every road route into or out of the Sihanoukville area paid the road border time and fee.
    stub = (roads["special"].astype(str) == "border") & (roads["km"] < 0.1)
    if stub.any():
        roads.loc[stub, "special"] = "provincial_stitch"
    print(f"roads: {int(stub.sum())} 'border' stubs -> 'provincial_stitch' "
          f"({int((roads['special'] == 'provincial_stitch').sum())} in the layer)")

    # 4. Mekong border
    m = ww["special"].astype(str).str.contains("vinh")
    if m.sum() != 1:
        raise SystemExit(f"waterways: Mekong border matches {int(m.sum())} edges")
    ww.loc[m, "name"] = "mekong_border"
    print("waterways: Kaam Samnor / Vinh Xuong edge -> name 'mekong_border'")

    # 5. port names on connectors
    if "port_name" not in mm.columns:
        mm["port_name"] = None
    for cid, (modes, xy, port) in PORTS.items():
        rows = mm.index[mm["id"] == cid]
        if len(rows) != 1 or mm.loc[rows[0], "multimodes"] != modes:
            raise SystemExit(f"multimodal: connector id {cid} is not one {modes} connector")
        cs = [c for _, c in endpoints(mm.loc[rows])]
        if not any(abs(c[0] - xy[0]) < TOL and abs(c[1] - xy[1]) < TOL for c in cs):
            raise SystemExit(f"multimodal: connector id {cid} does not end near {xy}: {cs}")
        mm.loc[rows[0], "port_name"] = port
    print("multimodal: port_name ->", mm.groupby("port_name")["multimodes"].apply(list).to_dict())

    if not a.write:
        print("report only (--write to update the files)")
        return
    for p in (gpkg, mm_path, cpath):
        b = p.with_name(p.stem + "_before_sea_gateways" + p.suffix)
        if not b.exists():
            shutil.copy(p, b)
    for lyr, df in (("maritime", sea), ("roads", roads), ("waterways", ww)):
        pyogrio.write_dataframe(df, gpkg, layer=lyr, driver="GPKG")
    pyogrio.write_dataframe(mm, mm_path, layer="multimodal", driver="GPKG")
    cg.to_file(cpath, driver="GeoJSON")
    after = [l[0] for l in pyogrio.list_layers(gpkg)]
    if sorted(after) != sorted(layers):
        shutil.copy(gpkg.with_name(gpkg.stem + "_before_sea_gateways.gpkg"), gpkg)
        raise SystemExit(f"layers changed {layers} -> {after}: gpkg restored from the backup")
    print(f"written: {gpkg.name} (maritime, roads, waterways), {mm_path.name}, {cpath.name}")


def pd_concat(gdf, row):
    import pandas as pd
    return pd.concat([gdf, gpd.GeoDataFrame([row], geometry="geometry", crs=gdf.crs)], ignore_index=True)


if __name__ == "__main__":
    main()
