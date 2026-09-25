# -*- coding: utf-8 -*-
"""Clean the manual Sculeni BCP reshape (25 Sep 2026) and complete it.

What the diff against the last-used network (run 20260924_235138) shows:
only road id 3584 'BCP: Sculeni (roads)' changed - moved from the 45-km
straight line to the actual river crossing at Sculeni village (1.24 km).
Railways identical; no other road edge moved (the user's reported edits at
Albita/Leuseni/Giurgiulesti/Lipcani are NOT in the saved file).

Cleaning:
  1. Sculeni BCP km recomputed (was stale 45.18); all bcp-class edges'
     km refreshed as geometry x 1.15 for consistency.
  2. The reshape left the BCP's Moldovan end dangling (nearest MD node
     ~42 km: the extraction's primary network never reached Sculeni, the
     old long line was the reach). An MD ACCESS EDGE is added along the
     R16 corridor: nearest point ON the MD network (edge split there,
     same machinery as the integration script) -> the BCP end; class
     primary, no border friction (friction belongs on the 1.4-km BCP).
     Straight-line km x 1.2 sinuosity (p18 convention).
  3. id 1904 (Leuseni approach, east of the Prut) relabeled foreign=1,
     country_code='MD' (an RO-extract spill-over that survived p19).
  4. Union-find audit: BCP edges remain the only RO<->MD/UA links and no
     BCP endpoint dangles.

Run in dsc env. Idempotent-ish: skips steps whose effect is present.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import substring

T = Path(r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Transport")
GPKG = T / "transport.gpkg"


def hav(a, b):
    lo1, la1, lo2, la2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def poly_km(geom):
    cs = list(geom.coords)
    return sum(hav(cs[i], cs[i + 1]) for i in range(len(cs) - 1))


def main() -> int:
    roads = gpd.read_file(GPKG, layer="roads")
    rail = gpd.read_file(GPKG, layer="railways")

    # 1. refresh km on all bcp-class edges (geometry x 1.15)
    for name, g in (("roads", roads), ("railways", rail)):
        m = g["class"].astype(str) == "bcp"
        for i in g[m].index:
            old = float(g.loc[i, "km"])
            new = round(poly_km(g.geometry[i]) * 1.15, 2)
            if abs(old - new) > 0.05:
                print(f"{name} km fix: {g.loc[i, 'name']}: {old} -> {new}")
                g.loc[i, "km"] = new

    # 3. Leuseni approach spill-over: relabel the WHOLE connected chain of
    # RO-labeled edges hanging east of the Prut off id 1904 (BFS over shared
    # endpoints, BCP edges excluded; guard: every node must sit east of the
    # river at Albita, lon > 28.10)
    R6 = lambda c: (round(c[0], 6), round(c[1], 6))
    fnum = pd.to_numeric(roads["foreign"], errors="coerce").fillna(0)
    non_bcp = roads["class"].astype(str) != "bcp"
    node2edges: dict = {}
    for i in roads.index[non_bcp]:
        cs = list(roads.geometry[i].coords)
        for c in (R6(cs[0]), R6(cs[-1])):
            node2edges.setdefault(c, []).append(i)
    seed = roads.index[roads["id"] == 1904]
    if len(seed):
        seen, todo = set(), [seed[0]]
        while todo:
            i = todo.pop()
            if i in seen:
                continue
            seen.add(i)
            cs = list(roads.geometry[i].coords)
            for c in (R6(cs[0]), R6(cs[-1])):
                for j in node2edges.get(c, []):
                    if j not in seen and fnum[j] != 1:
                        todo.append(j)
        chain = [i for i in seen if fnum[i] != 1]
        lons = [x for i in chain for x in
                (roads.geometry[i].coords[0][0], roads.geometry[i].coords[-1][0])]
        if chain and min(lons) > 28.10:
            roads.loc[chain, "foreign"] = 1
            roads.loc[chain, "country_code"] = "MD"
            print(f"Leuseni spill-over chain relabeled MD: "
                  f"{[int(roads.loc[i, 'id']) for i in chain]}")
        elif chain:
            print(f"WARNING: chain from 1904 reaches lon {min(lons):.3f} < 28.10 "
                  f"- not relabeling, inspect manually")

    # 2. Sculeni MD access edge (skip if one already touches the BCP end)
    sc = roads[roads["name"].astype(str) == "BCP: Sculeni (roads)"]
    cs_sc = list(sc.geometry.iloc[0].coords)
    # the MD-side endpoint is the eastern one
    SCULENI_MD_END = max((cs_sc[0], cs_sc[-1]), key=lambda c: c[0])
    print(f"Sculeni BCP MD endpoint (exact): {SCULENI_MD_END}")
    touch = False
    for i, geom in zip(roads.index, roads.geometry):
        if roads.loc[i, "id"] == 3584:
            continue
        cs = list(geom.coords)
        if hav(cs[0], SCULENI_MD_END) < 0.05 or hav(cs[-1], SCULENI_MD_END) < 0.05:
            touch = True
    if not touch:
        f = pd.to_numeric(roads["foreign"], errors="coerce").fillna(0)
        md = roads[(f == 1) & (roads["country_code"].astype(str) == "MD")]
        p = Point(SCULENI_MD_END)
        cand = md.geometry.distance(p).nsmallest(6)
        best = None
        for idx in cand.index:
            geom = roads.geometry[idx]
            proj = geom.project(p)
            q = geom.interpolate(proj)
            d = hav((q.x, q.y), SCULENI_MD_END)
            if best is None or d < best[0]:
                best = (d, idx, proj)
        d, idx, proj = best
        geom = roads.geometry[idx]
        cs = list(geom.coords)
        q = geom.interpolate(proj)
        if hav((q.x, q.y), cs[0]) < 0.3:
            node = cs[0]
        elif hav((q.x, q.y), cs[-1]) < 0.3:
            node = cs[-1]
        else:  # split the MD edge at the attach point
            p1 = substring(geom, 0, proj)
            p2 = substring(geom, proj, geom.length)
            node = list(p1.coords)[-1]
            row = roads.loc[idx].copy()
            roads.loc[idx, roads.geometry.name] = p1
            roads.loc[idx, "km"] = round(poly_km(p1), 3)
            row[roads.geometry.name] = p2
            row["km"] = round(poly_km(p2), 3)
            row["id"] = int(pd.to_numeric(roads["id"], errors="coerce").max()) + 1
            roads = pd.concat([roads, row.to_frame().T], ignore_index=True)
            roads = gpd.GeoDataFrame(roads, geometry=roads.geometry.name,
                                     crs="EPSG:4326")
        km = round(hav(node, SCULENI_MD_END) * 1.2, 2)
        tmpl = {c: None for c in roads.columns if c != roads.geometry.name}
        tmpl.update({"type": "roads", "class": "primary",
                     "name": "access: Sculeni-Falesti (R16)", "foreign": 1,
                     "country_code": "MD", "km": km,
                     "id": int(pd.to_numeric(roads["id"], errors="coerce").max()) + 1,
                     roads.geometry.name: LineString([node, SCULENI_MD_END])})
        roads = pd.concat([roads, gpd.GeoDataFrame([tmpl], crs="EPSG:4326")],
                          ignore_index=True)
        roads = gpd.GeoDataFrame(roads, geometry=roads.geometry.name, crs="EPSG:4326")
        print(f"Sculeni MD access edge added: {km} km from ({node[0]:.4f},{node[1]:.4f})"
              f" (attach dist {d:.1f} km, split={'yes' if len(cs) else 'n'})")
    else:
        print("Sculeni MD end already connected")

    # 4. audit
    for name, g in (("roads", roads), ("railways", rail)):
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
        tag = {}
        bcp = g["class"].astype(str) == "bcp"
        f = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
        cc = g["country_code"].astype(str)
        node_deg = {}
        for i in g.index:
            cs = list(g.geometry[i].coords)
            a, b = R(cs[0]), R(cs[-1])
            for c in (a, b):
                node_deg[c] = node_deg.get(c, 0) + 1
            if bcp[i]:
                continue
            union(a, b)
            side = "RO" if f[i] != 1 else (cc[i] if cc[i] in ("UA", "MD") else "OTHER")
            for c in (a, b):
                tag.setdefault(c, set()).add(side)
        comp = {}
        for c in parent:
            comp.setdefault(find(c), set()).update(tag.get(c, set()))
        bad = [s for s in comp.values() if "RO" in s and ({"UA", "MD"} & s)]
        dangling = []
        for i in g[bcp].index:
            cs = list(g.geometry[i].coords)
            for c in (R(cs[0]), R(cs[-1])):
                if node_deg.get(c, 0) < 2:
                    dangling.append((g.loc[i, "name"], c))
        print(f"audit {name}: RO+UA/MD mixed comps: {len(bad)}; "
              f"dangling BCP ends: {dangling if dangling else 'none'}")
        if bad or dangling:
            print("  !! FIX REQUIRED - not writing")
            return 1

    for name, out in (("roads", roads), ("railways", rail)):
        out["id"] = pd.to_numeric(out["id"], errors="raise").astype("int64")
        out["km"] = pd.to_numeric(out["km"], errors="raise").astype(float)
        out["foreign"] = pd.to_numeric(out["foreign"], errors="coerce")
        out.to_file(GPKG, layer=name, driver="GPKG")
    print("written transport.gpkg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
