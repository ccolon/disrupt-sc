# -*- coding: utf-8 -*-
"""Integrate the extracted Moldova + Ukraine networks (Deliverable 3), v2.

Replaces the hand-drawn UA/MD skeletons (v8) and TEN-T's 1520 mm rail with
coarse OSM-extracted networks (osm-extractor + tnclean + finalize), and joins
the three networks (model / Moldova / Ukraine) ONLY at border crossings that
the WB BCP data lists as open - each crossing created as a named edge
("BCP: <name> (<mode>)") so its flow can be followed directly.

v2 changes over the first pass:
  * joins snap to the nearest point ON an edge (splitting the edge there),
    not only to endpoints - coarse cleaning leaves few endpoints, which
    skipped Ungheni/Sculeni/Isaccea/Criva/Tudora/Reni in pass 1;
  * purges the RO-extract spill-over edges inside MD/UA (Falesti-Sculeni,
    Sculeni-Ungheni, Cahul-frontiera roads; Reni-Giurgiulesti and
    Colibasi-Giurgiulesti/Cahul rail) that share exact OSM coordinates with
    the new MD network and silently bypassed the BCP edges (the 0.0-km
    joins at Oancea and Giurgiulesti CFR in pass 1);
  * if both sides of a crossing resolve to the same node, the foreign side
    is retracted ~2 km so the named BCP edge is the only link;
  * an access-road edge is created for Izmail port (the R33 approach is
    below the trunk cutoff of the UA extraction);
  * restores from the pre-integration backups at start (idempotent);
  * ends with a connectivity audit: with the BCP edges removed, no
    component may contain both RO and UA/MD nodes.

Registry: disrupt-sc-data/Romania/Transport/bcp_registry.csv
  open=1 -> a crossing edge is created; open=0 -> logged, NOT linked.
Friction: crossings on the UA/MD side carry special='border'; the EU-internal
RO-TENT crossing (Curtici) carries none.

Run in the dsc env: python romania_integrate_extracted_networks.py
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import substring

T = Path(r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Transport")
GPKG = T / "transport.gpkg"
MM = T / "multimodal.gpkg"
REGISTRY = T / "bcp_registry.csv"
MD_FINAL = Path(r"C:/Users/Celian/OneDrive/DisruptSC/transport/transnet/data-moldova-v3/moldova_final.gpkg")
UA_FINAL = Path(r"C:/Users/Celian/OneDrive/DisruptSC/transport/transnet/data-ukraine/ukraine_final.gpkg")

SNAP_MAX_KM = {"RO-UA": 35, "RO-MD": 45, "MD-UA": 55, "UA-TENT": 80, "RO-TENT": 100}
CROSS_KM_FACTOR = 1.15
END_SNAP_KM = 0.3       # nearest-on-edge point this close to an endpoint -> no split
COINCIDENT_KM = 0.5     # both sides on (nearly) the same node -> retract foreign side
RETRACT_KM = 2.0

# RO-extract edges that spill across the border into MD/UA (exact OSM nodes
# shared with the new extractions -> silent joins); dropped by (id, token)
SPILLOVER = {
    "roads": [(1352, "Sculeni"), (1353, "Sculeni-Ungheni"), (1962, "Cahul")],
    "railways": [(213, "Reni"), (237, "Coliba")],
}

CONNECTOR_CITIES = {  # road-rail transfer points on the new networks
    "Kyiv": (30.52, 50.45), "Lviv": (24.03, 49.84), "Odesa": (30.73, 46.48),
    "Vinnytsia": (28.47, 49.23), "Dnipro": (35.05, 48.45),
    "Chisinau": (28.86, 47.02), "Balti": (27.92, 47.76),
}
PORT_CONNECTORS = {  # road/rail to the kept Danube waterway links
    "Reni": (28.28, 45.46), "Izmail": (28.83, 45.33), "Giurgiulesti": (28.20, 45.47),
}
# port, mode, side, reach: an access edge from the nearest network point
ACCESS_EDGES = [("Izmail port road", "roads", "UA", (28.83, 45.33), 60)]


def hav(a, b):
    lo1, la1, lo2, la2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def poly_km(geom):
    cs = list(geom.coords)
    return sum(hav(cs[i], cs[i + 1]) for i in range(len(cs) - 1))


def side_mask(g, side):
    f = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
    cc = g["country_code"].astype(str)
    if side == "RO":
        return (f != 1)
    if side in ("UA", "MD"):
        return (f == 1) & (cc == side)
    if side == "TENT":
        return (f == 1) & (~cc.isin(["UA", "MD", "border"]))
    raise ValueError(side)


class Net:
    """Mutable per-mode layer with split-at-point node materialization."""

    def __init__(self, gdf):
        self.g = gdf.reset_index(drop=True)

    def next_id(self):
        return int(pd.to_numeric(self.g["id"], errors="coerce").max()) + 1

    def attach(self, side, pt, lim_km):
        """Nearest point on any edge of `side` within lim_km; splits the edge
        if the point is mid-edge. Returns (node, dist_km) or (None, dist)."""
        sel = side_mask(self.g, side)
        sub = self.g[sel]
        if sub.empty:
            return None, 1e9
        p = Point(pt)
        cand = sub.geometry.distance(p).nsmallest(6)
        best = None
        for idx in cand.index:
            geom = self.g.geometry[idx]
            proj = geom.project(p)
            q = geom.interpolate(proj)
            d = hav((q.x, q.y), pt)
            if best is None or d < best[0]:
                best = (d, idx, proj)
        d, idx, proj = best
        if d > lim_km:
            return None, d
        return self._materialize(idx, proj), d

    def _materialize(self, idx, proj):
        geom = self.g.geometry[idx]
        cs = list(geom.coords)
        q = geom.interpolate(proj)
        if hav((q.x, q.y), cs[0]) < END_SNAP_KM:
            return cs[0]
        if hav((q.x, q.y), cs[-1]) < END_SNAP_KM:
            return cs[-1]
        p1 = substring(geom, 0, proj)
        p2 = substring(geom, proj, geom.length)
        node = list(p1.coords)[-1]
        row = self.g.loc[idx].copy()
        self.g.loc[idx, self.g.geometry.name] = p1
        self.g.loc[idx, "km"] = round(poly_km(p1), 3)
        row[self.g.geometry.name] = p2
        row["km"] = round(poly_km(p2), 3)
        row["id"] = self.next_id()
        self.g = pd.concat([self.g, row.to_frame().T], ignore_index=True)
        self.g = gpd.GeoDataFrame(self.g, geometry=self.g.geometry.name, crs="EPSG:4326")
        return node

    def retract(self, side, node, km_back=RETRACT_KM):
        """Pull all `side` edges off `node` so it belongs only to the other
        network; edges are re-anchored to one common retracted point."""
        sel = side_mask(self.g, side)
        touching = []
        for idx in self.g[sel].index:
            cs = list(self.g.geometry[idx].coords)
            if hav(cs[0], node) < 0.01:
                touching.append((idx, True))
            elif hav(cs[-1], node) < 0.01:
                touching.append((idx, False))
        if not touching:
            return None
        idx0, from_start = touching[0]
        geom = self.g.geometry[idx0]
        ekm = poly_km(geom)
        cut = geom.length * min(0.45, km_back / max(ekm, 0.1))
        ng = substring(geom, cut, geom.length) if from_start else substring(geom, 0, geom.length - cut)
        self.g.loc[idx0, self.g.geometry.name] = ng
        self.g.loc[idx0, "km"] = round(poly_km(ng), 3)
        nb = list(ng.coords)[0] if from_start else list(ng.coords)[-1]
        for idx, at_start in touching[1:]:
            cs = list(self.g.geometry[idx].coords)
            cs[0 if at_start else -1] = nb
            self.g.loc[idx, self.g.geometry.name] = LineString(cs)
            self.g.loc[idx, "km"] = round(poly_km(LineString(cs)), 3)
        return nb

    def add_edge(self, attrs, geom):
        tmpl = {c: None for c in self.g.columns if c != self.g.geometry.name}
        tmpl.update(attrs)
        tmpl["id"] = self.next_id()
        tmpl[self.g.geometry.name] = geom
        self.g = pd.concat([self.g, gpd.GeoDataFrame([tmpl], crs="EPSG:4326")],
                           ignore_index=True)
        self.g = gpd.GeoDataFrame(self.g, geometry=self.g.geometry.name, crs="EPSG:4326")


def drop_foreign_islands(nets, min_nodes=100):
    """Drop small disconnected components made only of UA/MD edges or of
    unnamed eastern stubs (lon > 26): the east-of-Dnipro rail cluster the
    extraction leaves unconnected, and orphan stubs of the old manual edits.
    Pre-existing named TEN-T islets (e.g. BA;HR) are kept."""
    for mode, net in nets.items():
        g = net.g
        parent = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            for c in (a, b):
                parent.setdefault(c, c)
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        R = lambda c: (round(c[0], 6), round(c[1], 6))
        comp_edges = {}
        for i, geom in enumerate(g.geometry):
            cs = list(geom.coords)
            union(R(cs[0]), R(cs[-1]))
        for i, geom in enumerate(g.geometry):
            comp_edges.setdefault(find(R(list(geom.coords)[0])), []).append(i)
        sizes = {r: len({R(c) for i in idxs for c in
                         (list(g.geometry[i].coords)[0], list(g.geometry[i].coords)[-1])})
                 for r, idxs in comp_edges.items()}
        main = max(sizes, key=sizes.get)
        drop = []
        for root, idxs in comp_edges.items():
            if root == main or sizes[root] >= min_nodes:
                continue
            cc = g.loc[idxs, "country_code"].astype(str)
            names = g.loc[idxs, "name"].astype(str)
            lons = [list(g.geometry[i].coords)[0][0] for i in idxs]
            if all((c in ("UA", "MD")) or (n in ("", "None", "nan") and lo > 26)
                   for c, n, lo in zip(cc, names, lons)):
                drop.extend(idxs)
        if drop:
            km = g.loc[drop, "km"].astype(float).sum()
            print(f"{mode}: dropping {len(drop)} disconnected foreign-island "
                  f"edges ({km:,.0f} km)")
            net.g = g.drop(index=drop).reset_index(drop=True)


def audit(nets):
    """Union-find on exact endpoint coords, BCP edges excluded: no component
    may contain both RO and UA/MD nodes."""
    ok = True
    for mode, net in nets.items():
        parent = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            for c in (a, b):
                parent.setdefault(c, c)
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        tag = {}
        g = net.g
        bcp = g["name"].astype(str).str.startswith("BCP: ")
        f = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
        cc = g["country_code"].astype(str)
        for i in g[~bcp].index:
            cs = list(g.geometry[i].coords)
            a = (round(cs[0][0], 6), round(cs[0][1], 6))
            b = (round(cs[-1][0], 6), round(cs[-1][1], 6))
            union(a, b)
            side = ("RO" if f[i] != 1 else
                    cc[i] if cc[i] in ("UA", "MD") else "OTHER")
            for c in (a, b):
                tag.setdefault(c, set()).add(side)
        comp = {}
        for c in parent:
            comp.setdefault(find(c), set()).update(tag.get(c, set()))
        bad = [s for s in comp.values() if "RO" in s and ({"UA", "MD"} & s)]
        n_ua_md = sum(1 for s in comp.values() if {"UA", "MD"} & s)
        print(f"audit {mode}: {len(comp)} components without BCP edges; "
              f"{n_ua_md} contain UA/MD nodes; RO+UA/MD mixed: {len(bad)}")
        if bad:
            ok = False
            print(f"  !! silent RO<->UA/MD join(s) remain in {mode}")
    return ok


def main():
    # restore pristine state (idempotent re-runs)
    for src, bak in [(GPKG, T / "transport_pre_integration.gpkg"),
                     (MM, T / "multimodal_pre_integration.gpkg")]:
        if bak.exists():
            shutil.copy2(bak, src)
            print(f"restored from {bak.name}")
        else:
            shutil.copy2(src, bak)
            print(f"backup: {bak.name}")

    roads = gpd.read_file(GPKG, layer="roads")
    rail = gpd.read_file(GPKG, layer="railways")

    # ---- purge superseded UA/MD content ---------------------------------
    r_names = roads["name"].astype(str)
    drop_roads = r_names.str.startswith("UAMD:") | r_names.str.startswith("manual:")
    print(f"roads: purging {int(drop_roads.sum())} skeleton/manual edges")
    roads = roads[~drop_roads].reset_index(drop=True)

    k_names = rail["name"].astype(str)
    drop_rail = (k_names.str.startswith("UAMD:")
                 | k_names.str.contains("stitch railways @\\(27.81,47.23\\)", regex=True)
                 | k_names.str.contains("stitch railways @\\(28.20,45.47\\)", regex=True)
                 | ((rail["foreign"].fillna(0) == 1)
                    & rail["country_code"].astype(str).str.contains("UA|MD", na=False)))
    print(f"railways: purging {int(drop_rail.sum())} skeleton/TEN-T-1520/old-stitch edges")
    rail = rail[~drop_rail].reset_index(drop=True)

    # spill-over edges of the RO extract inside MD/UA (silent-join risk)
    for mode, gdf in (("roads", roads), ("railways", rail)):
        ids = []
        for eid, token in SPILLOVER[mode]:
            hit = gdf[(pd.to_numeric(gdf["id"], errors="coerce") == eid)
                      & gdf["name"].astype(str).str.contains(token, na=False)]
            if len(hit) == 1:
                ids.append(hit.index[0])
                print(f"{mode}: purging spill-over id={eid} {hit.iloc[0]['name'][:60]!r}")
            else:
                print(f"{mode}: WARNING spill-over id={eid} token {token!r} matched {len(hit)} rows")
        if mode == "roads":
            roads = gdf.drop(index=ids).reset_index(drop=True)
        else:
            rail = gdf.drop(index=ids).reset_index(drop=True)

    # ---- append the extracted networks ----------------------------------
    def prep(path, cc):
        out = {}
        for mode in ("roads", "railways"):
            g = gpd.read_file(path, layer=mode)
            g["foreign"] = 1
            g["country_code"] = cc
            if mode == "railways":
                g = g[g["class"].astype(str) != "narrow_gauge"].reset_index(drop=True)
                g["class"] = "rail_1520"   # UA/MD are broad gauge -> UZ/CFM tariff
            out[mode] = g
        return out

    md = prep(MD_FINAL, "MD")
    ua = prep(UA_FINAL, "UA")
    for mode in ("roads", "railways"):
        base = roads if mode == "roads" else rail
        add = pd.concat([md[mode], ua[mode]], ignore_index=True)
        add = add.reindex(columns=base.columns)
        nid = int(pd.to_numeric(base["id"], errors="coerce").max()) + 1
        add["id"] = range(nid, nid + len(add))
        merged = pd.concat([base, add], ignore_index=True)
        if mode == "roads":
            roads = merged
        else:
            rail = merged
        print(f"{mode}: +{len(add)} extracted edges (MD {len(md[mode])}, UA {len(ua[mode])})")

    nets = {"roads": Net(gpd.GeoDataFrame(roads, crs="EPSG:4326")),
            "railways": Net(gpd.GeoDataFrame(rail, crs="EPSG:4326"))}

    # ---- access edges (ports below the extraction's class cutoff) -------
    for name, mode, side, pt, reach in ACCESS_EDGES:
        node, d = nets[mode].attach(side, pt, reach)
        if node is None:
            print(f"access {name}: SKIPPED (nearest {side} {mode} {d:.0f} km)")
            continue
        km = round(hav(node, pt) * CROSS_KM_FACTOR, 2)
        nets[mode].add_edge({"type": mode, "class": "primary", "name": f"access: {name}",
                             "foreign": 1, "country_code": side, "km": km},
                            LineString([node, pt]))
        print(f"access {name}: linked ({km} km from {side} {mode})")

    # ---- BCP joins ------------------------------------------------------
    reg = pd.read_csv(REGISTRY, comment="#")
    report = []
    for _, r in reg.iterrows():
        mode, join, pt = r["mode"], r["join"], (r["lon"], r["lat"])
        label = f"BCP: {r['name']} ({mode})"
        if not int(r["open"]):
            report.append((label, "NOT LINKED (closed / not in WB data)"))
            continue
        a_side, b_side = join.split("-")
        lim = SNAP_MAX_KM[join]
        A, da = nets[mode].attach(a_side, pt, lim)
        B, db = nets[mode].attach(b_side, pt, lim)
        if A is None or B is None:
            report.append((label, f"SKIPPED: no edge within {lim} km "
                                  f"({a_side} {da:.0f} km, {b_side} {db:.0f} km)"))
            continue
        note = ""
        if hav(A, B) < COINCIDENT_KM:
            nb = nets[mode].retract(b_side, B)
            if nb is not None:
                B = nb
                note = f"; {b_side} retracted {RETRACT_KM} km off the shared node"
        friction = "border" if join in ("RO-UA", "RO-MD", "MD-UA", "UA-TENT") else None
        km = round(hav(A, B) * CROSS_KM_FACTOR, 2)
        nets[mode].add_edge({"type": mode, "class": "bcp", "name": label,
                             "special": friction, "foreign": 1,
                             "country_code": "border", "km": km},
                            LineString([A, B]))
        report.append((label, f"linked ({km} km, {a_side} snap {da:.1f} / "
                              f"{b_side} snap {db:.1f} km{note})"))

    print("\n=== BCP joins ===")
    for label, status in report:
        print(f"  {label:45s} {status}")

    # ---- drop disconnected foreign islands, then audit ------------------
    print()
    drop_foreign_islands(nets)
    audit(nets)

    for mode in ("roads", "railways"):
        out = nets[mode].g
        # concat/split ops leave object dtypes -> GDAL would write id as str
        out["id"] = pd.to_numeric(out["id"], errors="raise").astype("int64")
        out["km"] = pd.to_numeric(out["km"], errors="raise").astype(float)
        out["foreign"] = pd.to_numeric(out["foreign"], errors="coerce")
        out.to_file(GPKG, layer=mode, driver="GPKG")

    # ---- multimodal connectors ------------------------------------------
    mm = gpd.read_file(MM)
    own = mm.get("name", pd.Series("", index=mm.index)).astype(str).str.startswith("UAMD:")
    print(f"\nmultimodal: purging {int(own.sum())} old UAMD connectors")
    mm = mm[~own].reset_index(drop=True)

    def endpoints(gdf):
        pts = []
        for geom in gdf.geometry:
            cs = list(geom.coords)
            pts.append((cs[0][0], cs[0][1]))
            pts.append((cs[-1][0], cs[-1][1]))
        return pts

    def nearest(pts, target):
        if not pts:
            return None, 1e9
        best = min(pts, key=lambda p: hav(p, target))
        return best, hav(best, target)

    fmask = lambda g: (pd.to_numeric(g["foreign"], errors="coerce").fillna(0) == 1) \
        & g["country_code"].astype(str).isin(["UA", "MD"])
    road_f = endpoints(nets["roads"].g[fmask(nets["roads"].g)])
    rail_f = endpoints(nets["railways"].g[fmask(nets["railways"].g)])
    water = gpd.read_file(GPKG, layer="waterways")
    water_pts = endpoints(water)
    next_id = int(mm["id"].max()) + 1
    rows = []

    def connector(cityname, m1, p1, m2, p2, max_km=30):
        nonlocal next_id
        target = CONNECTOR_CITIES.get(cityname) or PORT_CONNECTORS[cityname]
        a, da = nearest(p1, target)
        b, db = nearest(p2, target)
        if da > max_km or db > max_km:
            print(f"  connector {cityname} {m1}-{m2}: skipped ({da:.0f}/{db:.0f} km)")
            return
        d_m = hav(a, b) * 1000
        rows.append({"multimodes": f"{m1}-{m2}", "name": f"UAMD:{m1}-{m2} {cityname}",
                     "distance_m": round(d_m, 1), "km": round(d_m / 1000, 3),
                     "from_mode": m1, "to_mode": m2, "id": next_id, "foreign": 1,
                     "geometry": LineString([a, b])})
        next_id += 1

    for city in CONNECTOR_CITIES:
        connector(city, "roads", road_f, "railways", rail_f)
    for port in PORT_CONNECTORS:
        connector(port, "roads", road_f, "waterways", water_pts, max_km=15)
        connector(port, "railways", rail_f, "waterways", water_pts, max_km=15)
    mm2 = pd.concat([mm, gpd.GeoDataFrame(rows, crs=mm.crs).reindex(columns=mm.columns)],
                    ignore_index=True)
    gpd.GeoDataFrame(mm2, crs="EPSG:4326").to_file(MM, layer="multimodal", driver="GPKG")
    print(f"multimodal: +{len(rows)} connectors on the new networks")


if __name__ == "__main__":
    main()
