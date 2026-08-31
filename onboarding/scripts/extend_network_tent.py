"""Extend a scope's transport network with TEN-T European corridors.

Purpose: let external gateway blocs sit at their TRUE locations (Vienna,
Frankfurt, Milan, ...) so the international leg of import/export flows is
routed on real corridors and the model chooses the Romanian border crossing
and mode endogenously. Foreign detail stays minimal: only the TEN-T trunk
network of a country whitelist is added, flagged `foreign=1` so domestic
statistics can exclude it.

Steps
  1. load the scope's transport.gpkg (backed up to transport_domestic.gpkg)
  2. filter TEN-T layers by country whitelist (any token of country_code);
     pure-scope-country edges are dropped (domestic detail already exists)
  3. schema-normalize foreign edges (id, type, km in EPSG:8857, foreign=1)
  4. stitch foreign networks to the domestic ones: for each mode, bridge
     foreign endpoints near a domestic node (greedy, spatially deduped)
  5. optional hand bridges (e.g. the Serbian Danube stretch absent from the
     EU-only TEN-T data) from BRIDGES below
  6. append TEN-T multimodal connectors (endpoints snapped to node set;
     unmatched connectors dropped)
  7. keep only the network component reachable from the domestic scope
  8. write transport.gpkg + multimodal.gpkg

Usage:
    python extend_network_tent.py <Scope> --tent <tent_plain.gpkg> [--dry-run]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# Countries whose TEN-T edges are kept (any token of country_code matches).
# Chosen for Romania: the corridor region between the gateway cities and the
# Romanian border. West of the gateways (FR, Benelux, Iberia, Nordics) is NOT
# needed - those partners are represented AT the gateways.
WHITELIST = {"DE", "AT", "CZ", "SK", "PL", "HU", "SI", "HR", "IT", "BG", "EL",
             "RS", "UA", "MD", "TR", "CH", "RO"}
SCOPE_CC = "RO"          # pure-scope edges dropped (domestic network exists)
STITCH_MAX_KM = 40.0     # foreign endpoint -> nearest domestic node
STITCH_DEDUPE_KM = 35.0  # min spacing between stitches (one per crossing)
CONNECTOR_SNAP_KM = 2.0  # connector endpoint -> nearest network node
# Hand bridges for gaps in the source data: (mode, lon1, lat1, lon2, lat2,
# km_override or None, note). The Serbian Danube (Novi Sad -> Ram) is real
# navigable river missing from the EU-only TEN-T extract.
BRIDGES = [
    ("waterways", 19.42236, 45.23441, 21.35849, 44.82164, 230.0,
     "Serbian Danube (Novi Sad-Ram), absent from EU TEN-T data"),
]
MODES = ("roads", "railways", "waterways")


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scope")
    ap.add_argument("--tent", required=True)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data_root = Path(args.data_root) if args.data_root else locate.data_root()
    tdir = data_root / args.scope / "Transport"
    dom_path = tdir / "transport_domestic.gpkg"
    if not dom_path.exists():
        # first run: back up the domestic-only network
        import shutil
        shutil.copy(tdir / "transport.gpkg", dom_path)
        shutil.copy(tdir / "multimodal.gpkg", tdir / "multimodal_domestic.gpkg")
        print(f"backed up domestic network -> {dom_path.name}, multimodal_domestic.gpkg")

    def wl(cc):
        toks = {t.strip() for t in str(cc).split(";")}
        # Drop ANY edge touching the scope country: pure-scope edges duplicate
        # the domestic network, and mixed cross-border edges would sit in the
        # foreign layer PARALLEL to domestic geometry (double-representing
        # e.g. the shared lower Danube, and pulling territorial tkm out of
        # the domestic statistics). The neighbor-side approach plus a stitch
        # carries the crossing instead.
        return bool(toks & WHITELIST) and SCOPE_CC not in toks

    merged_layers = {}
    node_sets = {m: set() for m in MODES}
    for mode in MODES:
        dom = gpd.read_file(dom_path, layer=mode)
        if "foreign" not in dom.columns:
            dom["foreign"] = 0
        try:
            ten = gpd.read_file(args.tent, layer=mode)
        except Exception:
            merged_layers[mode] = dom
            continue
        ten = ten[ten.country_code.apply(wl)].copy()
        ten = ten[ten.geometry.type == "LineString"]
        max_id = int(dom["id"].max()) + 1
        for_gdf = gpd.GeoDataFrame({
            "id": range(max_id, max_id + len(ten)),
            "type": mode,
            "km": km_col(ten).values,
            "name": ("TEN-T " + ten["country_code"].astype(str)).values,
            "class": ten.get("type", pd.Series(index=ten.index, dtype=object)).values
                     if "type" in ten.columns else None,
            "surface": None, "special": "tent", "disruption": None,
            "foreign": 1,
            "country_code": ten["country_code"].values,
        }, geometry=ten.geometry.values, crs=dom.crs)

        # --- stitches: bridge foreign endpoints to nearby domestic nodes ---
        dom_nodes = set()
        for geom in dom.geometry:
            a, b = ends(geom)
            dom_nodes.add(a); dom_nodes.add(b)
        node_sets[mode] |= dom_nodes
        for_nodes = set()
        for geom in for_gdf.geometry:
            a, b = ends(geom)
            for_nodes.add(a); for_nodes.add(b)
        node_sets[mode] |= for_nodes
        dom_list = list(dom_nodes)
        cands = []
        for fn in for_nodes:
            best = min(dom_list, key=lambda dnode: hav_km(fn, dnode))
            d = hav_km(fn, best)
            if d <= STITCH_MAX_KM:
                cands.append((d, fn, best))
        cands.sort()
        stitches, placed = [], []
        for d, fn, dn in cands:
            if any(hav_km(fn, p) < STITCH_DEDUPE_KM for p in placed):
                continue
            placed.append(fn)
            stitches.append((fn, dn, d))
        srows = []
        for i, (fn, dn, d) in enumerate(stitches):
            srows.append({
                "id": max_id + len(ten) + i, "type": mode,
                "km": hav_km(fn, dn) * 1.2,
                "name": f"stitch {mode} @({fn[0]:.2f},{fn[1]:.2f})",
                "class": "stitch", "surface": None, "special": "stitch",
                "disruption": None, "foreign": 1, "country_code": "border",
                "geometry": LineString([fn, dn]),
            })
        sgdf = gpd.GeoDataFrame(srows, crs=dom.crs) if srows else None
        parts = [dom, for_gdf] + ([sgdf] if sgdf is not None else [])
        merged_layers[mode] = gpd.GeoDataFrame(
            pd.concat(parts, ignore_index=True), crs=dom.crs)
        print(f"{mode}: domestic {len(dom)} + tent {len(for_gdf)} + stitches {len(srows)}")

    # maritime: domestic (Jasper) only, TEN-T maritime skipped
    mar = gpd.read_file(dom_path, layer="maritime")
    if "foreign" not in mar.columns:
        mar["foreign"] = 0
    merged_layers["maritime"] = mar

    # --- hand bridges ---
    # Endpoints snap to the nearest existing node of the mode (within 100 km)
    # so a bridge always lands on live topology - coordinates in BRIDGES may
    # reference nodes that pruning removed.
    for mode, lon1, lat1, lon2, lat2, km_o, note in BRIDGES:
        g = merged_layers[mode]
        pts = []
        node_list = list(node_sets[mode])
        for pt in ((lon1, lat1), (lon2, lat2)):
            best = min(node_list, key=lambda n: hav_km(pt, n))
            if hav_km(pt, best) <= 100:
                pts.append(best)
            else:
                pts.append((round(pt[0], 6), round(pt[1], 6)))
                print(f"WARN bridge endpoint {pt} has no {mode} node within 100 km - kept as-is")
        row = {
            "id": int(g["id"].max()) + 1, "type": mode,
            "km": km_o or hav_km(pts[0], pts[1]) * 1.3,
            "name": f"bridge: {note}", "class": "bridge", "surface": None,
            "special": "bridge", "disruption": None, "foreign": 1,
            "country_code": "bridge",
            "geometry": LineString(pts),
        }
        merged_layers[mode] = gpd.GeoDataFrame(
            pd.concat([g, gpd.GeoDataFrame([row], crs=g.crs)], ignore_index=True), crs=g.crs)
        node_sets[mode] |= {(round(lon1, 6), round(lat1, 6)), (round(lon2, 6), round(lat2, 6))}
        print(f"bridge added on {mode}: {note}")

    # --- TEN-T multimodal connectors ---
    dom_mm = gpd.read_file(tdir / "multimodal_domestic.gpkg")
    if "foreign" not in dom_mm.columns:
        dom_mm["foreign"] = 0
    tmm = gpd.read_file(args.tent, layer="multimodal")
    tmm = tmm[tmm.country_code.isin(WHITELIST - {SCOPE_CC})].copy()
    all_nodes = set().union(*node_sets.values())
    all_list = list(all_nodes)
    kept, snapped, dropped = [], 0, 0
    for _, r in tmm.iterrows():
        cs = list(r.geometry.coords)
        newpts = []
        ok = True
        for pt in (cs[0], cs[-1]):
            p6 = (round(pt[0], 6), round(pt[1], 6))
            if p6 in all_nodes:
                newpts.append(p6)
                continue
            best = min(all_list, key=lambda n: hav_km(p6, n))
            if hav_km(p6, best) <= CONNECTOR_SNAP_KM:
                newpts.append(best); snapped += 1
            else:
                ok = False; break
        if not ok:
            dropped += 1
            continue
        kept.append({
            "multimodes": r["multimodes"], "distance_m": float(r.get("km", 0)) * 1000,
            "km": float(r.get("km", 0)) or hav_km(newpts[0], newpts[1]),
            "from_mode": r["from_mode"], "to_mode": r["to_mode"],
            "id": 0, "foreign": 1,
            "geometry": LineString(newpts),
        })
    mm_new = gpd.GeoDataFrame(kept, crs=dom_mm.crs)
    mm = gpd.GeoDataFrame(pd.concat([dom_mm, mm_new], ignore_index=True), crs=dom_mm.crs)
    mm["id"] = range(len(mm))
    print(f"connectors: domestic {len(dom_mm)} + tent kept {len(kept)} "
          f"(snapped {snapped} endpoints, dropped {dropped})")

    # --- keep only the component reachable from the domestic network ---
    G = nx.Graph()
    for mode, g in merged_layers.items():
        for i, geom in zip(g.index, g.geometry):
            a, b = ends(geom)
            G.add_edge(a, b)
    for geom in mm.geometry:
        a, b = ends(geom)
        G.add_edge(a, b)
    dom_seed = ends(merged_layers["roads"][merged_layers["roads"].foreign == 0].geometry.iloc[0])[0]
    main_comp = nx.node_connected_component(G, dom_seed)
    total_drop = 0
    for mode in list(merged_layers):
        g = merged_layers[mode]
        keep_mask = [ends(geom)[0] in main_comp or ends(geom)[1] in main_comp
                     for geom in g.geometry]
        dropped_n = len(g) - sum(keep_mask)
        total_drop += dropped_n
        merged_layers[mode] = g[keep_mask]
        if dropped_n:
            print(f"{mode}: dropped {dropped_n} edges unreachable from the scope")
    mm = mm[[ends(geom)[0] in main_comp for geom in mm.geometry]]

    if args.dry_run:
        print("dry-run: not writing")
        return 0

    out = tdir / "transport.gpkg"
    if out.exists():
        out.unlink()
    for mode, g in merged_layers.items():
        g.to_file(out, layer=mode, driver="GPKG")
    mm_out = tdir / "multimodal.gpkg"
    if mm_out.exists():
        mm_out.unlink()
    mm.to_file(mm_out, layer="multimodal", driver="GPKG")
    tot = sum(len(g) for g in merged_layers.values())
    print(f"written: transport.gpkg ({tot} edges) + multimodal.gpkg ({len(mm)} connectors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
