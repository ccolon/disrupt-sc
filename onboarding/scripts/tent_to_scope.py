"""Build a scope's transport.gpkg + multimodal.gpkg directly from the TEN-T
network (``tent_plain.gpkg``: roads, railways, waterways, maritime, multimodal).

For continental scopes (the EU) the TEN-T trunk network IS the domestic
network, so phase 5 of the runbook (OSM extraction + tnclean) is replaced by
this schema-normalizing copy:

  1. keep only edges whose ``country_code`` has at least one token in the
     country whitelist (cross-border edges are kept when any side is in);
     maritime edges (no country_code) are always kept;
  2. write the DisruptSC edge schema per mode layer (id, type=mode, km in
     EPSG:8857, name, class, surface, special, disruption) and carry the
     TEN-T attributes (country_code, corridors, core_network);
  3. name river chains: for each entry of RIVER_CHAINS the shortest waterway
     path between two anchor points is traced and its edges receive
     ``name = <river>_<from>_<to>`` (nearest riverside towns), ``special =
     <river>`` and a ``disruption`` tag ``<river>;<segment>`` — the strings a
     ``transport_disruption`` scenario targets with ``attribute: name`` or
     ``attribute: disruption`` (substring match);
  4. keep only the largest connected component of the combined network
     (all modes + connectors), reporting what was dropped;
  5. write ``<Scope>/Transport/transport.gpkg`` (one layer per mode) and
     ``<Scope>/Transport/multimodal.gpkg`` (connectors, endpoint-snapped).

Usage:
    python tent_to_scope.py <Scope> --tent <tent_plain.gpkg> [--dry-run]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import LineString, Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# EU27 + EFTA (Eurostat 2-letter codes as used by TENtec; EL = Greece).
WHITELIST = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL", "HU",
    "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES",
    "SE",
    "CH", "NO", "IS", "LI",
}
MODES = ("roads", "railways", "waterways", "maritime")
CONNECTOR_SNAP_KM = 2.0

# River chains to name: (river, [(town, lon, lat), ...]) — the chain is the
# shortest waterway path from the first to the last town; intermediate towns
# only label segments (nearest town to each edge midpoint). Coordinates are
# river-side points. Rhine-km (official kilometrage from Konstanz) for the
# disruption tags come from RIVER_KM below.
RIVER_CHAINS = {
    "rhine": [
        ("basel", 7.590, 47.565), ("strasbourg", 7.800, 48.579),
        ("karlsruhe", 8.305, 49.042), ("mannheim", 8.450, 49.503),
        ("mainz", 8.288, 49.995), ("kaub", 7.764, 50.086),
        ("koblenz", 7.597, 50.342), ("bonn", 7.112, 50.735),
        ("koeln", 6.981, 50.957), ("duesseldorf", 6.726, 51.216),
        ("duisburg", 6.726, 51.430), ("wesel", 6.604, 51.648),
        ("emmerich", 6.245, 51.831), ("nijmegen", 5.866, 51.757),
        ("tiel", 5.461, 51.889), ("dordrecht", 4.666, 51.722),
        ("rotterdam", 4.333, 51.867),
    ],
}
# Official Rhine kilometrage at the chain towns (for the disruption tag).
RIVER_KM = {
    "rhine": {"basel": 170, "strasbourg": 294, "karlsruhe": 360, "mannheim": 425,
              "mainz": 498, "kaub": 546, "koblenz": 592, "bonn": 655,
              "koeln": 688, "duesseldorf": 744, "duisburg": 780, "wesel": 814,
              "emmerich": 852, "nijmegen": 885, "tiel": 915, "dordrecht": 975,
              "rotterdam": 1000},
}


def hav_km(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))


def ends(geom, nd=6):
    cs = list(geom.coords)
    return ((round(cs[0][0], nd), round(cs[0][1], nd)),
            (round(cs[-1][0], nd), round(cs[-1][1], nd)))


def km_col(gdf):
    return gdf.geometry.to_crs("EPSG:8857").length / 1000.0


def in_whitelist(cc) -> bool:
    if cc is None or (isinstance(cc, float) and math.isnan(cc)):
        return True  # maritime / untagged edges
    toks = {t.strip() for t in str(cc).split(";")}
    return bool(toks & WHITELIST)


def normalize(ten: gpd.GeoDataFrame, mode: str, id_start: int) -> gpd.GeoDataFrame:
    ten = ten[ten.geometry.type == "LineString"].copy()
    cls = ten["type"].values if "type" in ten.columns else [None] * len(ten)
    out = gpd.GeoDataFrame({
        "id": range(id_start, id_start + len(ten)),
        "type": mode,
        "km": km_col(ten).values,
        "name": "",
        "class": cls,
        "surface": None,
        "special": None,
        "disruption": None,
        "country_code": ten["country_code"].values if "country_code" in ten.columns else None,
        "corridors": ten["corridors"].values if "corridors" in ten.columns else None,
        "core_network": ten["core_network"].astype(str).values if "core_network" in ten.columns else None,
        "tent_objectid": ten["objectid"].values if "objectid" in ten.columns else None,
    }, geometry=ten.geometry.values, crs=ten.crs)
    return out


def name_river_chains(ww: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Trace each river chain on the waterway graph and tag its edges."""
    G = nx.Graph()
    for idx, geom, km in zip(ww.index, ww.geometry, ww["km"]):
        a, b = ends(geom)
        if G.has_edge(a, b):
            if km < G[a][b]["km"]:
                G[a][b].update(km=km, idx=idx)
        else:
            G.add_edge(a, b, km=km, idx=idx)
    nodes = list(G.nodes)
    for river, towns in RIVER_CHAINS.items():
        src = min(nodes, key=lambda n: hav_km(n, towns[0][1:]))
        dst = min(nodes, key=lambda n: hav_km(n, towns[-1][1:]))
        d_src, d_dst = hav_km(src, towns[0][1:]), hav_km(dst, towns[-1][1:])
        try:
            path = nx.shortest_path(G, src, dst, weight="km")
        except nx.NetworkXNoPath:
            print(f"WARN {river}: no waterway path {towns[0][0]} -> {towns[-1][0]}")
            continue
        chain_idx = [G[u][v]["idx"] for u, v in zip(path[:-1], path[1:])]
        total = 0.0
        for u, v in zip(path[:-1], path[1:]):
            idx = G[u][v]["idx"]
            geom = ww.at[idx, "geometry"]
            a, b = ends(geom)
            # nearest towns to each endpoint -> segment label (ordered by river km)
            ta = min(towns, key=lambda t: hav_km(a, t[1:]))[0]
            tb = min(towns, key=lambda t: hav_km(b, t[1:]))[0]
            kms = RIVER_KM.get(river, {})
            if kms.get(ta, 0) > kms.get(tb, 0):
                ta, tb = tb, ta
            seg = f"{ta}_{tb}" if ta != tb else ta
            ww.at[idx, "name"] = f"{river}_{seg}"
            ww.at[idx, "special"] = river
            # a segment covers river-km [min, max] of its two towns; edges whose
            # endpoints are nearest to the same town get that town's km
            lo, hi = kms.get(ta, 0), kms.get(tb, 0)
            ww.at[idx, "disruption"] = f"{river};{seg};km{lo}-{hi}"
            total += G[u][v]["km"]
        print(f"{river}: {len(chain_idx)} edges, {total:.0f} km path "
              f"(anchors snapped {d_src:.1f} km / {d_dst:.1f} km from "
              f"{towns[0][0]} / {towns[-1][0]})")
        segs = ww.loc[chain_idx, ["name", "km"]].groupby("name")["km"].sum().round(1)
        print("  " + ", ".join(f"{n}={k}" for n, k in segs.items()))
    return ww


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scope")
    ap.add_argument("--tent", required=True)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data_root = Path(args.data_root) if args.data_root else locate.data_root()
    tdir = data_root / args.scope / "Transport"
    tdir.mkdir(parents=True, exist_ok=True)

    layers = {}
    id_start = 0
    node_sets = {m: set() for m in MODES}
    for mode in MODES:
        ten = gpd.read_file(args.tent, layer=mode)
        n0 = len(ten)
        if "country_code" in ten.columns:
            ten = ten[ten["country_code"].apply(in_whitelist)]
        g = normalize(ten, mode, id_start)
        id_start = int(g["id"].max()) + 1 if len(g) else id_start
        if mode == "waterways":
            g = name_river_chains(g)
        for geom in g.geometry:
            a, b = ends(geom)
            node_sets[mode].add(a); node_sets[mode].add(b)
        layers[mode] = g
        print(f"{mode}: {n0} -> {len(g)} edges kept ({g['km'].sum():,.0f} km)")

    # connectors: snap endpoints to live nodes
    tmm = gpd.read_file(args.tent, layer="multimodal")
    all_nodes = set().union(*node_sets.values())
    all_list = list(all_nodes)
    kept, snapped, dropped = [], 0, 0
    for _, r in tmm.iterrows():
        cs = list(r.geometry.coords)
        newpts, ok = [], True
        for pt in (cs[0], cs[-1]):
            p6 = (round(pt[0], 6), round(pt[1], 6))
            if p6 in all_nodes:
                newpts.append(p6); continue
            best = min(all_list, key=lambda n: hav_km(p6, n))
            if hav_km(p6, best) <= CONNECTOR_SNAP_KM:
                newpts.append(best); snapped += 1
            else:
                ok = False; break
        if not ok or newpts[0] == newpts[1]:
            dropped += 1; continue
        kept.append({
            "multimodes": r["multimodes"], "from_mode": r["from_mode"],
            "to_mode": r["to_mode"], "km": float(r.get("km", 0)) or hav_km(newpts[0], newpts[1]),
            "name": r.get("name"), "terminal_id": r.get("terminal_id"),
            "terminal_type": r.get("terminal_type"), "country_code": r.get("country_code"),
            "id": 0, "geometry": LineString(newpts),
        })
    mm = gpd.GeoDataFrame(kept, crs=tmm.crs)
    mm["id"] = range(len(mm))
    print(f"connectors: {len(tmm)} -> kept {len(mm)} (snapped {snapped} endpoints, dropped {dropped})")

    # largest connected component of the combined network
    G = nx.Graph()
    for mode, g in layers.items():
        for geom in g.geometry:
            a, b = ends(geom); G.add_edge(a, b)
    for geom in mm.geometry:
        a, b = ends(geom); G.add_edge(a, b)
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    main_comp = comps[0]
    print(f"combined network: {len(comps)} components; largest {len(main_comp)} of {G.number_of_nodes()} nodes")
    for mode in list(layers):
        g = layers[mode]
        keep = [ends(geom)[0] in main_comp for geom in g.geometry]
        n_drop = len(g) - sum(keep)
        if n_drop:
            km_drop = g.loc[[not k for k in keep], "km"].sum()
            print(f"  {mode}: dropping {n_drop} edges / {km_drop:,.0f} km outside the main component")
        layers[mode] = g[keep]
    mm = mm[[ends(geom)[0] in main_comp for geom in mm.geometry]]
    # per-mode component report (a mode may legitimately be multi-component
    # when it is only reachable through connectors, e.g. islands' roads)
    for mode, g in layers.items():
        Gm = nx.Graph()
        for geom in g.geometry:
            a, b = ends(geom); Gm.add_edge(a, b)
        cc = sorted((len(c) for c in nx.connected_components(Gm)), reverse=True)
        print(f"  {mode}: {len(g)} edges, {len(cc)} own components (largest {cc[0] if cc else 0} nodes)")

    if args.dry_run:
        print("dry-run: not writing"); return 0
    out = tdir / "transport.gpkg"
    if out.exists():
        out.unlink()
    for mode, g in layers.items():
        g.to_file(out, layer=mode, driver="GPKG")
    mm_out = tdir / "multimodal.gpkg"
    if mm_out.exists():
        mm_out.unlink()
    mm.to_file(mm_out, layer="multimodal", driver="GPKG")
    tot = sum(len(g) for g in layers.values())
    print(f"written: {out} ({tot} edges) + {mm_out} ({len(mm)} connectors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
