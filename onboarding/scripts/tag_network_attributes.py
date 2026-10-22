"""Tag the EU scope transport network with waterway names and Eurostat port codes.

Purpose
-------
The TEN-T source of the EU network carries no waterway names or CEMT classes
(only objectid, country_code, core_network, corridors, region) and the port
terminals are hashed ids without names. Scoring a baseline against Eurostat
(ports), CCNR/Destatis (waterway basins) therefore needs two tags that this
script derives from gazetteers kept under <data-root>/<scope>/validation/:

  waterways_gazetteer.csv  columns waterway, country_codes, seq, lat, lon, note
      point sequences along the main European waterways; rows of one waterway
      ordered by seq form a polyline, and a seq that restarts (seq <= previous)
      opens a new branch polyline of the same waterway.
  ports_gazetteer.csv      columns eurostat_port, port_name, country, lat, lon,
      confidence, note - the largest EU ports by 2023 gross weight (Eurostat
      mar_go_aa); merged port authorities (Antwerp-Bruges, HAROPA, Marseille-
      Fos, ...) carry one row per location sharing the eurostat_port code.

Tags (all distances in EPSG:3035)
  waterways layer  -> waterway, waterway_dist_km
      edges named rhine_* (the Basel-Rotterdam chain) are forced to "Rhine";
      every other edge takes the gazetteer waterway whose polyline is nearest
      to the edge midpoint if that distance is below --waterway-km (20 km),
      otherwise other_<country_code>.
  multimodal layer, sea-port connectors (multimodes contains "maritime")
      -> port_name, eurostat_port, port_dist_km: nearest gazetteer port
      within --port-km (25 km) of the connector's maritime-side endpoint
      (the endpoint on the side whose mode is maritime, i.e. the last vertex
      when to_mode == maritime).
  multimodal layer, river-port connectors (waterways without maritime)
      -> waterway: the tag of the nearest tagged waterway edge.

Outputs (originals are never touched)
  <data-root>/<scope>/Transport/tagged/transport.gpkg   (all four mode layers)
  <data-root>/<scope>/Transport/tagged/multimodal.gpkg
  <data-root>/<scope>/Transport/tagged/tagging_report.csv  long-format report:
      section, key, country_code, n_edges, km, detail - sections waterway_edges,
      sea_port_connectors, unmatched_sea_connectors, ports_without_connector,
      river_port_connectors.

Usage
-----
    python onboarding/scripts/tag_network_attributes.py [EU] [--data-root DIR]
        [--out DIR] [--waterway-km 20] [--port-km 25]

The tagging functions are importable: flow_score.py calls tag_waterways /
tag_sea_ports / tag_river_ports to tag a flow export on the fly when the
exported edges carry no waterway / eurostat_port columns.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

CRS_M = "EPSG:3035"
MODE_LAYERS = ("roads", "railways", "waterways", "maritime")


# ----------------------------------------------------------------------------
# gazetteers
# ----------------------------------------------------------------------------
def default_gazetteer_dir(scope: str, data_root: Path | None = None) -> Path:
    return (data_root or locate.data_root()) / scope / "validation"


def load_waterway_gazetteer(path: Path) -> gpd.GeoDataFrame:
    """One row per polyline branch: waterway, branch, country_codes, geometry (3035)."""
    df = pd.read_csv(path)
    rows = []
    for name, grp in df.groupby("waterway", sort=False):
        pts, prev, branch = [], -1, 0
        for _, r in grp.iterrows():
            if r["seq"] <= prev and pts:          # seq restart -> new branch
                rows.append((name, branch, grp["country_codes"].iloc[0], pts))
                pts, branch = [], branch + 1
            pts.append((float(r["lon"]), float(r["lat"])))
            prev = r["seq"]
        rows.append((name, branch, grp["country_codes"].iloc[0], pts))
    geoms = [LineString(p) if len(p) > 1 else Point(p[0]) for *_, p in rows]
    gdf = gpd.GeoDataFrame([r[:3] for r in rows], columns=["waterway", "branch", "country_codes"],
                           geometry=geoms, crs="EPSG:4326")
    return gdf.to_crs(CRS_M)


def load_ports_gazetteer(path: Path) -> gpd.GeoDataFrame:
    df = pd.read_csv(path)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326")
    return gdf.to_crs(CRS_M)


# ----------------------------------------------------------------------------
# tagging
# ----------------------------------------------------------------------------
def _first_cc(value) -> str:
    s = str(value) if value is not None and not (isinstance(value, float) and np.isnan(value)) else ""
    s = s.split(";")[0].strip().upper()
    return s if len(s) == 2 else "XX"


def _nearest(points: gpd.GeoSeries, targets: gpd.GeoSeries) -> tuple[np.ndarray, np.ndarray]:
    """Index into `targets` of the nearest geometry and the distance in km (brute force)."""
    tg = list(targets.geometry)
    idx, dist = np.empty(len(points), dtype=int), np.empty(len(points))
    for i, p in enumerate(points.geometry):
        d = np.array([p.distance(t) for t in tg])
        idx[i], dist[i] = int(d.argmin()), d.min() / 1000.0
    return idx, dist


def tag_waterways(edges: gpd.GeoDataFrame, gaz: gpd.GeoDataFrame, max_km: float = 20.0) -> pd.DataFrame:
    """Return a DataFrame (index = edges.index) with waterway and waterway_dist_km."""
    e = edges.to_crs(CRS_M)
    mids = e.geometry.interpolate(0.5, normalized=True)
    idx, dist = _nearest(mids, gaz.geometry)
    names = gaz["waterway"].to_numpy()[idx]
    cc = e["country_code"].map(_first_cc) if "country_code" in e.columns else pd.Series("XX", index=e.index)
    out = pd.DataFrame({"waterway": np.where(dist <= max_km, names, "other_" + cc.to_numpy()),
                        "waterway_dist_km": np.round(dist, 1)}, index=edges.index)
    named = e["name"].astype(str).str.lower().str.startswith("rhine") if "name" in e.columns else None
    if named is not None and named.any():
        out.loc[named, "waterway"] = "Rhine"
        out.loc[named, "waterway_dist_km"] = 0.0
    return out


def _side_points(mm: gpd.GeoDataFrame, mode: str) -> gpd.GeoSeries:
    """Endpoint of each connector on the side whose mode is `mode` (last vertex if to_mode)."""
    pts = []
    to_modes = mm["to_mode"] if "to_mode" in mm.columns else pd.Series(mode, index=mm.index)
    for geom, to_mode in zip(mm.geometry, to_modes):
        c = geom.coords
        pts.append(Point(c[-1]) if str(to_mode) == mode else Point(c[0]))
    return gpd.GeoSeries(pts, index=mm.index, crs=mm.crs).to_crs(CRS_M)


def sea_connector_mask(mm: pd.DataFrame) -> pd.Series:
    return mm["multimodes"].astype(str).str.contains("maritime")


def river_connector_mask(mm: pd.DataFrame) -> pd.Series:
    m = mm["multimodes"].astype(str)
    return m.str.contains("waterways") & ~m.str.contains("maritime")


def tag_sea_ports(mm: gpd.GeoDataFrame, ports: gpd.GeoDataFrame, max_km: float = 25.0) -> pd.DataFrame:
    """Sea-port connectors only (index = their index): port_name, eurostat_port,
    port_dist_km, nearest_port, nearest_port_km (the last two also for unmatched)."""
    sea = mm[sea_connector_mask(mm)]
    pts = _side_points(sea, "maritime")
    idx, dist = _nearest(pts, ports.geometry)
    ok = dist <= max_km
    return pd.DataFrame({
        "port_name": np.where(ok, ports["port_name"].to_numpy()[idx], None),
        "eurostat_port": np.where(ok, ports["eurostat_port"].to_numpy()[idx], None),
        "port_dist_km": np.where(ok, np.round(dist, 1), np.nan),
        "nearest_port": ports["port_name"].to_numpy()[idx],
        "nearest_port_km": np.round(dist, 1),
        "lon": pts.to_crs("EPSG:4326").x.round(3).to_numpy(),
        "lat": pts.to_crs("EPSG:4326").y.round(3).to_numpy(),
    }, index=sea.index)


def tag_river_ports(mm: gpd.GeoDataFrame, waterways: gpd.GeoDataFrame, max_km: float = 20.0) -> pd.DataFrame:
    """River-port connectors only: waterway of the nearest tagged waterway edge."""
    riv = mm[river_connector_mask(mm)]
    pts = _side_points(riv, "waterways")
    ww = waterways.to_crs(CRS_M)
    idx, dist = _nearest(pts, ww.geometry)
    tags = ww["waterway"].to_numpy()[idx]
    cc = riv["country_code"].map(_first_cc) if "country_code" in riv.columns else pd.Series("XX", index=riv.index)
    return pd.DataFrame({"waterway": np.where(dist <= max_km, tags, "other_" + cc.to_numpy()),
                         "waterway_dist_km": np.round(dist, 1)}, index=riv.index)


def tag_edges_frame(edges: gpd.GeoDataFrame, gaz_dir: Path, waterway_km: float = 20.0,
                    port_km: float = 25.0) -> gpd.GeoDataFrame:
    """Tag a combined edge table (e.g. a flow export with a `type` column) in place
    of the missing columns; returns a copy with waterway / port_name / eurostat_port."""
    e = edges.copy()
    for col in ("waterway", "waterway_dist_km", "port_name", "eurostat_port", "port_dist_km"):
        if col not in e.columns:
            e[col] = np.nan if col.endswith("_km") else None
    ww = e["type"] == "waterways"
    wt = tag_waterways(e[ww], load_waterway_gazetteer(gaz_dir / "waterways_gazetteer.csv"), waterway_km)
    e.loc[wt.index, ["waterway", "waterway_dist_km"]] = wt[["waterway", "waterway_dist_km"]].to_numpy()
    mm = e[e["type"] == "multimodal"]
    if len(mm):
        pt = tag_sea_ports(mm, load_ports_gazetteer(gaz_dir / "ports_gazetteer.csv"), port_km)
        e.loc[pt.index, ["port_name", "eurostat_port", "port_dist_km"]] = \
            pt[["port_name", "eurostat_port", "port_dist_km"]].to_numpy()
        rt = tag_river_ports(mm, e.loc[wt.index], waterway_km)
        e.loc[rt.index, ["waterway", "waterway_dist_km"]] = rt[["waterway", "waterway_dist_km"]].to_numpy()
    return e


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def _write_gpkg(path: Path, layers: dict[str, gpd.GeoDataFrame]) -> None:
    if path.exists():
        path.unlink()
    for name, gdf in layers.items():
        gdf.to_file(path, layer=name, driver="GPKG")
    written = set(gpd.list_layers(path)["name"])
    missing = set(layers) - written
    if missing:
        sys.exit(f"ERROR: layers {sorted(missing)} missing from {path} after write (engine={gpd.options.io_engine})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("scope", nargs="?", default="EU")
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--out", default=None, help="output folder (default <scope>/Transport/tagged)")
    ap.add_argument("--waterway-km", type=float, default=20.0)
    ap.add_argument("--port-km", type=float, default=25.0)
    args = ap.parse_args()

    data_root = Path(args.data_root) if args.data_root else locate.data_root()
    tdir = data_root / args.scope / "Transport"
    gaz_dir = default_gazetteer_dir(args.scope, data_root)
    out = Path(args.out) if args.out else tdir / "tagged"
    out.mkdir(parents=True, exist_ok=True)
    if out.resolve() == tdir.resolve():
        sys.exit("ERROR: refusing to overwrite the original Transport folder")

    layers = {m: gpd.read_file(tdir / "transport.gpkg", layer=m) for m in MODE_LAYERS}
    mm = gpd.read_file(tdir / "multimodal.gpkg", layer="multimodal")
    gaz = load_waterway_gazetteer(gaz_dir / "waterways_gazetteer.csv")
    ports = load_ports_gazetteer(gaz_dir / "ports_gazetteer.csv")
    print(f"waterway gazetteer: {gaz['waterway'].nunique()} waterways, {len(gaz)} polylines; "
          f"ports gazetteer: {ports['eurostat_port'].nunique()} ports, {len(ports)} locations")

    # 1. waterway edges
    ww = layers["waterways"]
    wt = tag_waterways(ww, gaz, args.waterway_km)
    ww["waterway"], ww["waterway_dist_km"] = wt["waterway"], wt["waterway_dist_km"]
    ww["cc"] = ww["country_code"].map(_first_cc)
    report = []
    cover = ww.groupby(["waterway", "cc"]).agg(n_edges=("id", "size"), km=("km", "sum"),
                                               maxd=("waterway_dist_km", "max")).reset_index()
    for _, r in cover.iterrows():
        report.append(("waterway_edges", r["waterway"], r["cc"], int(r["n_edges"]), round(r["km"], 1),
                       f"max midpoint distance {r['maxd']:.1f} km"))
    n_other = int(ww["waterway"].str.startswith("other_").sum())
    print(f"\nwaterways: {len(ww)} edges, {ww['waterway'].nunique()} tags, "
          f"{n_other} edges left as other_<cc> ({ww.loc[ww['waterway'].str.startswith('other_'), 'km'].sum():.0f} km)")
    by_ww = ww.groupby("waterway").agg(n=("id", "size"), km=("km", "sum")).sort_values("km", ascending=False)
    print(by_ww.round(0).to_string())
    layers["waterways"] = ww.drop(columns=["cc"])

    # 2. sea-port connectors
    pt = tag_sea_ports(mm, ports, args.port_km)
    for col in ("port_name", "eurostat_port", "port_dist_km"):
        mm[col] = np.nan if col == "port_dist_km" else None
        mm.loc[pt.index, col] = pt[col]
    matched = pt[pt["eurostat_port"].notna()]
    unmatched = pt[pt["eurostat_port"].isna()]
    sea = mm.loc[pt.index]
    print(f"\nsea-port connectors: {len(pt)} ({sea['terminal_id'].nunique()} terminals); matched "
          f"{len(matched)} connectors / {sea.loc[matched.index, 'terminal_id'].nunique()} terminals to "
          f"{matched['eurostat_port'].nunique()} Eurostat ports; unmatched {len(unmatched)} connectors / "
          f"{sea.loc[unmatched.index, 'terminal_id'].nunique()} terminals")
    grp = sea.loc[matched.index].groupby("eurostat_port")
    for code, g in grp:
        report.append(("sea_port_connectors", code, g["country_code"].iloc[0], len(g),
                       g["terminal_id"].nunique(),
                       f"{g['port_name'].iloc[0]}; terminals {','.join(sorted(g['terminal_id'].unique()))}"))
    for tid, g in sea.loc[unmatched.index].groupby("terminal_id"):
        u = unmatched.loc[g.index[0]]
        report.append(("unmatched_sea_connectors", tid, g["country_code"].iloc[0], len(g), np.nan,
                       f"({u['lon']}, {u['lat']}) nearest {u['nearest_port']} {u['nearest_port_km']} km"))
    missing_ports = ports[~ports["eurostat_port"].isin(matched["eurostat_port"])]
    for _, r in missing_ports.drop_duplicates("eurostat_port").iterrows():
        report.append(("ports_without_connector", r["eurostat_port"], r["country"], 0, np.nan, r["port_name"]))
    print(f"gazetteer ports without any connector: {missing_ports['eurostat_port'].nunique()} "
          f"({', '.join(missing_ports.drop_duplicates('eurostat_port')['port_name'])})")
    um = sea.loc[unmatched.index].drop_duplicates("terminal_id")
    print("unmatched sea terminals by country: " + str(um["country_code"].value_counts().to_dict()))

    # 3. river-port connectors
    rt = tag_river_ports(mm, ww, args.waterway_km)
    mm["waterway"] = None
    mm.loc[rt.index, "waterway"] = rt["waterway"]
    riv = mm.loc[rt.index]
    for (w, cc), g in riv.groupby(["waterway", "country_code"]):
        report.append(("river_port_connectors", w, cc, len(g), g["terminal_id"].nunique(), ""))
    print(f"\nriver-port connectors: {len(riv)} ({riv['terminal_id'].nunique()} terminals) tagged; by waterway:")
    print(riv.groupby("waterway")["terminal_id"].nunique().sort_values(ascending=False).to_string())

    # 4. write
    _write_gpkg(out / "transport.gpkg", layers)
    _write_gpkg(out / "multimodal.gpkg", {"multimodal": mm})
    rep = pd.DataFrame(report, columns=["section", "key", "country_code", "n_edges", "km", "detail"])
    rep.to_csv(out / "tagging_report.csv", index=False)
    print(f"\nwritten: {out / 'transport.gpkg'}, {out / 'multimodal.gpkg'}, {out / 'tagging_report.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
