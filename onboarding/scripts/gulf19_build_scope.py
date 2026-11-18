"""Build the spatial and transport files of the Gulf19 scope from the Gulf scope (Hormuz paper, node A21).

Gulf19 = the Gulf scope with a 19-region MRIO (JPN, KOR out of EAS; BGD and EUR out of RoW; decision Q15).
The MRIO and sector table come from onboarding/scripts/gloria_extract.py (spec
onboarding/mrio_specs/gulf/gulf19.yaml). This script writes everything else of <data-root>/Gulf19 from
<data-root>/Gulf, which it only reads (the Gulf scope is in use and its transport.gpkg carries the
uncommitted 24 Apr 2026 edit; nothing of it is changed):

- copied byte for byte: Spatial/firms.geojson (oil and gas fields of the Gulf economies only; the firms of
  every other region_sector sit at the centroid of their region's household points),
  Transport/multimodal_config.yml;
- Spatial/households.geojson: the Gulf points + one point each for JPN (Yokohama), KOR (Busan) and BGD
  (Chittagong). EUR already has a point (Frankfurt) in the Gulf file - unused there, as Europe sat in RoW
  in the 15-region table - and keeps it. Population left empty like the other external regions (one point
  per region takes the region's whole final demand);
- Spatial/countries.geojson: the Gulf entries + JPN, KOR, BGD (EUR is already there). The tables are
  closed (every region has firms and households, no country agent), so these entries are not read by the
  model; they keep the file complete like the other external regions;
- Transport/transport.gpkg and multimodal.gpkg: the Gulf layers unchanged (checked row by row) + for each
  of JPN, KOR, BGD the same five pieces as the existing external regions (CHN at Shanghai, EAS at Singapore,
  IND at Mumbai): a road stub (household node -> port-side road node), a roads-maritime connector to a sea
  node, a sea edge (special 'border', tagged with the region) from an existing sea junction of the network,
  a 2 km airport edge with a roads-airways connector, and an air route (special 'border') from the network's
  South-Asian air hub. The new edges go at the end of each layer, so the model's edge ids of the roads
  layer are unchanged and every later layer's ids shift by the number of rows added before it (named edges
  are compared by name). EUR needs nothing: its road stub, connectors, sea edge (Atlantic node -> Frankfurt)
  and airport exist in the Gulf file.

Sea routes (stylised polylines, as the existing ones; length computed by the model from the geometry):
- JPN and KOR leave the Malacca junction (103.9262, 0.92) - the node where the CHN and EAS edges start -
  along the vertices of the CHN edge up to east of Taiwan (122.6507, 25.7603), then to Tokyo Bay (south of
  Kyushu, Shikoku, Kii and Izu) and to Busan (east of Jeju, Korea Strait);
- BGD leaves the junction south of Sri Lanka (84.6444, 4.2802) - where the Malacca edge starts - north
  through the Bay of Bengal to the Karnaphuli mouth at Chittagong.

Run (env dsc):  python onboarding/scripts/gulf19_build_scope.py
Writes <data-root>/Gulf19/{Spatial,Transport}/... and <data-root>/Gulf19/scope_build.json (sha256 of
every input and output, git commit of this script).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

warnings.filterwarnings("ignore", message=".*GDAL_DATA.*")

SRC_SCOPE, DST_SCOPE = "Gulf", "Gulf19"
AIR_HUB = (74.3962, 20.994)          # node of the air network where the CHN and EAS routes start
MALACCA = (103.9262, 0.92)           # sea node where the CHN and EAS edges start
SRI_LANKA_SOUTH = (84.6444, 4.2802)  # sea node where the Malacca edge starts
CHN_EDGE_TO_TAIWAN = [(104.994, 0.7002), (105.8419, 1.0456), (106.6898, 3.5579), (107.5275, 5.6796),
                      (118.385, 18.8438), (122.6507, 23.2794), (122.6507, 25.7603)]  # vertices of the CHN edge

NEW = {
    "JPN": {
        "place": "Yokohama / Tokyo Bay", "country_name": "Japan",
        "household": (139.6400, 35.4500), "road_a": (139.6600, 35.4700), "road_b": (139.7200, 35.5100),
        "sea": (139.7600, 35.4700),
        "sea_route": [MALACCA, *CHN_EDGE_TO_TAIWAN, (128.0, 29.0), (132.5, 31.0), (135.5, 33.2), (138.6, 34.3),
                      (139.75, 35.15)],
        "airport": "HND Tokyo Haneda International", "air_a": (139.7580, 35.5450), "air_b": (139.7800, 35.5450),
        "air_route": [AIR_HUB, (113.7498, 24.7441)],
    },
    "KOR": {
        "place": "Busan", "country_name": "Korea, Republic of",
        "household": (129.0600, 35.1700), "road_a": (129.0400, 35.1500), "road_b": (129.0000, 35.1100),
        "sea": (129.0400, 35.0600),
        "sea_route": [MALACCA, *CHN_EDGE_TO_TAIWAN, (125.5, 30.5), (128.6, 34.4)],
        "airport": "PUS Gimhae International", "air_a": (128.9280, 35.1700), "air_b": (128.9500, 35.1700),
        "air_route": [AIR_HUB, (113.7498, 24.7441)],
    },
    "BGD": {
        "place": "Chittagong", "country_name": "Bangladesh",
        "household": (91.8300, 22.3400), "road_a": (91.8200, 22.3200), "road_b": (91.8100, 22.2800),
        "sea": (91.7600, 22.2200),
        "sea_route": [SRI_LANKA_SOUTH, (86.0, 10.0), (88.5, 17.5), (91.0, 21.2)],
        "airport": "CGP Shah Amanat International", "air_a": (91.7930, 22.2500), "air_b": (91.8150, 22.2500),
        "air_route": [AIR_HUB],
    },
}


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def node_set(gdfs) -> set:
    pts = set()
    for g in gdfs:
        for ls in g.geometry:
            for c in (ls.coords[0], ls.coords[-1]):
                pts.add((round(c[0], 6), round(c[1], 6)))
    return pts


def append(gdf: gpd.GeoDataFrame, rows: list[dict]) -> gpd.GeoDataFrame:
    new = gpd.GeoDataFrame(rows, geometry="geometry", crs=gdf.crs)
    for c in gdf.columns:
        if c not in new.columns:
            new[c] = None
    new = new[gdf.columns]
    for c in gdf.columns:
        if c != "geometry" and str(gdf[c].dtype) != "object":
            new[c] = new[c].astype(gdf[c].dtype)
    return gpd.GeoDataFrame(pd.concat([gdf, new], ignore_index=True), geometry="geometry", crs=gdf.crs)


def same_rows(a: gpd.GeoDataFrame, b: gpd.GeoDataFrame, n: int, what: str) -> None:
    """The first n rows of b must equal a: geometry (exact WKB) and every attribute."""
    assert len(a) == n, what
    bb = b.iloc[:n]
    assert all(x.equals_exact(y, 0.0) for x, y in zip(a.geometry, bb.geometry)), f"{what}: geometry changed"
    for c in a.columns:
        if c == "geometry":
            continue
        x, y = a[c].reset_index(drop=True), bb[c].reset_index(drop=True)
        eq = (x == y) | (x.isna() & y.isna())
        assert eq.all(), f"{what}: column {c} changed"


def main() -> int:
    root = locate.data_root()
    src, dst = root / SRC_SCOPE, root / DST_SCOPE
    (dst / "Spatial").mkdir(parents=True, exist_ok=True)
    (dst / "Transport").mkdir(parents=True, exist_ok=True)
    inputs = {f"{SRC_SCOPE}/{p}": sha256(src / p) for p in
              ["Spatial/firms.geojson", "Spatial/households.geojson", "Spatial/countries.geojson",
               "Transport/transport.gpkg", "Transport/multimodal.gpkg", "Transport/multimodal_config.yml"]}

    for p in ["Spatial/firms.geojson", "Transport/multimodal_config.yml"]:
        shutil.copyfile(src / p, dst / p)

    # ---------------------------------------------------------------- households, countries
    hh = gpd.read_file(src / "Spatial/households.geojson")
    assert not set(NEW) & set(hh["region"]), "a new region already has a household point"
    assert "EUR" in set(hh["region"])
    hh2 = append(hh, [{"region": r, "city": d["place"], "population": np.nan, "geometry": Point(d["household"])}
                      for r, d in NEW.items()])
    same_rows(hh, hh2, len(hh), "households")
    hh2.to_file(dst / "Spatial/households.geojson", driver="GeoJSON")
    co = gpd.read_file(src / "Spatial/countries.geojson")
    assert "EUR" in set(co["region"])
    co2 = append(co, [{"region": r, "name": d["country_name"], "geometry": Point(d["household"])}
                      for r, d in NEW.items()])
    same_rows(co, co2, len(co), "countries")
    co2.to_file(dst / "Spatial/countries.geojson", driver="GeoJSON")

    # ---------------------------------------------------------------- transport
    tp = src / "Transport/transport.gpkg"
    layers = list(gpd.list_layers(tp)["name"])
    assert layers == ["roads", "maritime", "airways", "pipelines"], layers
    g = {lyr: gpd.read_file(tp, layer=lyr) for lyr in layers}
    mm = gpd.read_file(src / "Transport/multimodal.gpkg", layer="multimodal")
    nodes = node_set(list(g.values()) + [mm])
    exact = {}
    for p in (AIR_HUB, MALACCA, SRI_LANKA_SOUTH):   # 4-decimal constants -> the exact node coordinates
        near = [n for n in nodes if abs(n[0] - p[0]) < 1e-3 and abs(n[1] - p[1]) < 1e-3]
        assert len(near) == 1, f"attachment node {p}: {near}"
        exact[p] = near[0]
    for r, d in NEW.items():   # the attachment nodes exist; the new ones do not
        for k in ("sea_route", "air_route"):
            d[k] = [exact[d[k][0]], *d[k][1:]]
            assert d[k][0] in nodes, f"{r} {k} start {d[k][0]} is not a node of the Gulf network"
        for k in ("road_a", "road_b", "sea", "air_a", "air_b"):
            assert (round(d[k][0], 6), round(d[k][1], 6)) not in nodes, f"{r} {k} collides with a node"

    roads, sea, air = [], [], []
    mm_rows = []
    next_id = int(mm["id"].max()) + 1
    for r, d in NEW.items():
        roads.append({"geometry": LineString([d["road_a"], d["road_b"]])})
        sea.append({"special": "border", "region": r, "geometry": LineString([*d["sea_route"], d["sea"]])})
        air.append({"name": d["airport"], "class": "airways", "surface": "airways", "region": r, "km": 2.0,
                    "geometry": LineString([d["air_a"], d["air_b"]])})
        air.append({"special": "border", "region": r, "geometry": LineString([*d["air_route"], d["air_a"]])})
        for to_mode, end in (("maritime", d["sea"]), ("airways", d["air_b"])):
            ls = LineString([d["road_b"], end])
            dist_m = float(gpd.GeoSeries([ls], crs="EPSG:4326").to_crs("EPSG:3857").length.iloc[0])
            mm_rows.append({"multimodes": f"roads-{to_mode}", "distance_m": dist_m, "km": round(dist_m / 1000, 3),
                            "from_mode": "roads", "to_mode": to_mode, "id": next_id, "geometry": ls})
            next_id += 1
    out = {"roads": append(g["roads"], roads), "maritime": append(g["maritime"], sea),
           "airways": append(g["airways"], air), "pipelines": g["pipelines"]}
    for lyr in layers:
        same_rows(g[lyr], out[lyr], len(g[lyr]), lyr)
    mm2 = append(mm, mm_rows)
    same_rows(mm, mm2, len(mm), "multimodal")

    tp_out = dst / "Transport/transport.gpkg"
    if tp_out.exists():
        tp_out.unlink()
    for lyr in layers:
        out[lyr].to_file(tp_out, layer=lyr, driver="GPKG")
    mm_out = dst / "Transport/multimodal.gpkg"
    if mm_out.exists():
        mm_out.unlink()
    mm2.to_file(mm_out, layer="multimodal", driver="GPKG")

    # read back: the written layers equal what was built
    for lyr in layers:
        back = gpd.read_file(tp_out, layer=lyr)
        same_rows(out[lyr], back, len(out[lyr]), f"{lyr} (written)")
    same_rows(mm2, gpd.read_file(mm_out, layer="multimodal"), len(mm2), "multimodal (written)")

    # ---------------------------------------------------------------- report
    rows = []
    for r, d in NEW.items():
        sea_ls = gpd.GeoSeries([LineString([*d["sea_route"], d["sea"]])], crs="EPSG:4326").to_crs(epsg=8857)
        air_ls = gpd.GeoSeries([LineString([*d["air_route"], d["air_a"]])], crs="EPSG:4326").to_crs(epsg=8857)
        rows.append({"region": r, "place": d["place"], "sea_from": d["sea_route"][0],
                     "sea_km": round(float(sea_ls.length.iloc[0]) / 1000), "air_km": round(float(air_ls.length.iloc[0]) / 1000)})
    print(pd.DataFrame(rows).to_string(index=False))
    print("rows added: roads", len(roads), "maritime", len(sea), "airways", len(air), "multimodal", len(mm_rows),
          "households", len(NEW), "countries", len(NEW))
    try:
        head = subprocess.run(["git", "-C", str(locate.find_repo_root()), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        head = None
    outputs = {p: sha256(dst / p) for p in
               ["Spatial/firms.geojson", "Spatial/households.geojson", "Spatial/countries.geojson",
                "Transport/transport.gpkg", "Transport/multimodal.gpkg", "Transport/multimodal_config.yml"]}
    rec = {"scope": DST_SCOPE, "from": SRC_SCOPE, "created": time.strftime("%Y-%m-%d %H:%M:%S"),
           "script": "onboarding/scripts/gulf19_build_scope.py", "script_sha256": sha256(Path(__file__)),
           "git_head": head, "inputs": inputs, "outputs": outputs,
           "added": {r: {k: v for k, v in d.items()} for r, d in NEW.items()},
           "sea_and_air_km_epsg8857": rows,
           "economic": "Economic/ from onboarding/scripts/gloria_extract.py, spec onboarding/mrio_specs/gulf/gulf19.yaml "
                       "(Economic/mrio_full.provenance.json)"}
    (dst / "scope_build.json").write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
