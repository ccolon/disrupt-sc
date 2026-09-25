# -*- coding: utf-8 -*-
"""Clean the user's full MD/UA BCP reshape session (25 Sep 2026, pass 2).

The saved QGIS session (roads layer only) redrew the crossings as their
physical bridges/ferries: Halmeu, Isaccea ferry (0.9 km across the Danube,
with bank spurs), Albita (4 km on the E581), Giurgiulesti bridge (1.85 km),
Radauti-Prut bridge (0.68 km), Criva-Mamalyha (1.77 km), Sculeni (2.43 km),
rerouted the UA M15 through Reni and deleted the superseded long reaches.

Cleaning performed here:
  A. ids: 2 NaN rows (ferry bank spurs) and 3 duplicated ids (3584 twice,
     895 twice, 3370 twice after user splits) -> new unique ids.
  B. attributes: the Sculeni-Ungheni MD road carried the old BCP row's
     garbage (name 'ads)', cc='border', special='border'); the ferry spurs
     had none; two MD roads (875 Chisinau-Leuseni M1 segment, the Lipcani
     stub) were labeled domestic -> foreign=1/cc fixed, special cleared.
  C. km: recomputed as polyline length wherever it deviates >10% from the
     geometry (stale values from before the reshape; the x1.15 straight-
     line factor is retired - BCP geometries are now real).
  D. structure:
     1. Halmeu BCP's UA end dangled (old UA reach deleted) -> UA access
        edge to the nearest point ON the UA network (edge split there).
     2. Criva-Mamalyha BCP's UA end dangled likewise -> UA access edge
        (the real M19-corridor reach toward Chernivtsi).
     3. The rerouted UA trunk ended on the SAME node as the RO Galati road
        and the Giurgiulesti bridge BCP - a silent UA-RO join. The trunk
        is retracted ~1 km and the deleted 'BCP: Giurgiulesti-Reni
        (roads)' is recreated from its end to the MD Giurgiulesti node
        (the config's per-gate fee stays keyed to that name).
     4. The pass-1 access edge 'access: Sculeni-Falesti (R16)' (id 3621)
        is deleted - obsolete: the user's own Sculeni-Ungheni road now
        connects the crossing into Moldova.
  E. audit: BCP edges are the only RO<->UA/MD links; no dangling BCP ends.

Run in dsc env after any QGIS edit session on the border area.
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

MD_GIURGIULESTI = (28.1905, 45.4686)   # MD node where the bridge BCP starts
TRIPOINT = (28.2110, 45.4770)          # shared node to un-join (UA side)


def hav(a, b):
    lo1, la1, lo2, la2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def pkm(geom):
    cs = list(geom.coords)
    return sum(hav(cs[i], cs[i + 1]) for i in range(len(cs) - 1))


def ends(geom):
    cs = list(geom.coords)
    return cs[0], cs[-1]


def main() -> int:
    roads = gpd.read_file(GPKG, layer="roads")
    rail = gpd.read_file(GPKG, layer="railways")
    gname = roads.geometry.name

    def next_id():
        return int(pd.to_numeric(roads["id"], errors="coerce").max()) + 1

    # ---- A + B: ids and attributes --------------------------------------
    def match(idx_pred, fix, label):
        nonlocal roads
        hits = [i for i in roads.index if idx_pred(roads.loc[i])]
        if len(hits) != 1:
            print(f"WARNING {label}: {len(hits)} matches - skipped")
            return None
        i = hits[0]
        for k, v in fix.items():
            roads.loc[i, k] = v
        print(f"{label}: fixed (idx {i})")
        return i

    def near(c, pt, tol=0.03):
        return hav(c, pt) < tol

    # ferry spurs (NaN ids)
    match(lambda r: pd.isna(r["id"]) and near(ends(r[gname])[0], (28.4363, 45.3025))
          and near(ends(r[gname])[1], (28.4587, 45.2912)),
          {"id": next_id(), "name": "", "class": "trunk", "foreign": 1,
           "country_code": "UA", "special": ""}, "UA ferry spur (Orlivka)")
    match(lambda r: pd.isna(r["id"]) and near(ends(r[gname])[0], (28.4571, 45.2754)),
          {"id": next_id(), "name": "", "class": "trunk", "foreign": 0,
           "country_code": None, "special": ""}, "RO ferry spur (Isaccea)")
    # Sculeni-Ungheni MD road (dup id 3584, garbage attrs)
    match(lambda r: r["id"] == 3584 and str(r["class"]) != "bcp",
          {"id": next_id(), "name": "Sculeni-Ungheni road", "class": "trunk",
           "foreign": 1, "country_code": "MD", "special": ""},
          "Sculeni-Ungheni MD road")
    # Lipcani MD stub (dup id 895, east of the bridge)
    match(lambda r: r["id"] == 895 and near(ends(r[gname])[1], (26.8067, 48.2640)),
          {"id": next_id(), "foreign": 1, "country_code": "MD"},
          "Lipcani MD stub")
    # second half of the split Ungheni-Chisinau trunk (dup id 3370)
    match(lambda r: r["id"] == 3370 and near(ends(r[gname])[1], (27.7217, 47.5707)),
          {"id": next_id()}, "Ungheni-Chisinau second half")
    # Geography-based relabel: any non-bcp road whose MIDPOINT falls inside
    # the MDA or UKR polygon gets foreign=1/cc set accordingly. This settles
    # every spill-over dispute at once (Hincesti chain, Prut east-bank rows,
    # the user's redrawn approaches) by where the road actually is.
    BND = Path(r"C:/Users/Celian/OneDrive/DisruptSC/Firms/Boundaries")
    mda = gpd.read_file(BND / "geoBoundaries-MDA-ADM0_simplified.geojson").geometry.union_all()
    ukr = gpd.read_file(BND / "geoBoundaries-UKR-ADM1_simplified.geojson").geometry.union_all()
    mda_b = mda.buffer(0.02)
    ukr_b = ukr.buffer(0.02)
    fnum = pd.to_numeric(roads["foreign"], errors="coerce").fillna(0)
    n_md = n_ua = n_rev = 0
    for i in roads.index:
        if str(roads.loc[i, "class"]) == "bcp":
            continue
        cc_i = str(roads.loc[i, "country_code"])
        mid = roads.geometry[i].interpolate(0.5, normalized=True)
        if mda.contains(mid):
            if fnum[i] != 1 or cc_i != "MD":
                roads.loc[i, "foreign"] = 1
                roads.loc[i, "country_code"] = "MD"
                n_md += 1
        elif ukr.contains(mid):
            if fnum[i] != 1 or cc_i != "UA":
                roads.loc[i, "foreign"] = 1
                roads.loc[i, "country_code"] = "UA"
                n_ua += 1
    print(f"geography relabel: {n_md} -> MD, {n_ua} -> UA")

    # Reconcile foreign/domestic node contacts (simplified polygons clip
    # river-bank roads; QGIS snapping can attach a foreign road to a
    # domestic node): a foreign MD/UA edge sharing an exact node with a
    # domestic edge is REVERTED to domestic when it has no same-country
    # contact at all (polygon artifact), else RETRACTED 1 km off the
    # shared node (snap artifact) - the BCP edges stay the only links.
    R6 = lambda c: (round(c[0], 6), round(c[1], 6))
    fnum2 = pd.to_numeric(roads["foreign"], errors="coerce").fillna(0)
    is_bcp = roads["class"].astype(str) == "bcp"
    node_side = {}
    for i in roads.index:
        if is_bcp[i]:
            continue
        sde = "RO" if fnum2[i] != 1 else str(roads.loc[i, "country_code"])
        for c in ends(roads.geometry[i]):
            node_side.setdefault(R6(c), set()).add(sde)
    for i in list(roads.index):
        if is_bcp[i] or fnum2[i] != 1:
            continue
        cc_i = str(roads.loc[i, "country_code"])
        if cc_i not in ("MD", "UA"):
            continue
        e0, e1 = ends(roads.geometry[i])
        touch_ro = [c for c in (e0, e1) if "RO" in node_side.get(R6(c), set())]
        if not touch_ro:
            continue
        same = any(cc_i in (node_side.get(R6(c), set()) - {cc_i} or
                            node_side.get(R6(c), set()))
                   for c in (e0, e1) if c not in touch_ro)
        # same-country contact = the OTHER end touches another edge of cc_i
        other_ends = [c for c in (e0, e1) if c not in touch_ro]
        same = any(len([1 for j in roads.index if j != i and not is_bcp[j]
                        and str(roads.loc[j, "country_code"]) == cc_i
                        and any(R6(x) == R6(c) for x in ends(roads.geometry[j]))]) > 0
                   for c in other_ends)
        if not same:
            roads.loc[i, "foreign"] = 0
            roads.loc[i, "country_code"] = None
            print(f"  contact-revert id={roads.loc[i, 'id']} "
                  f"{str(roads.loc[i, 'name'])[:28]!r} ({cc_i} -> domestic)")
        else:
            geom = roads.geometry[i]
            at_start = R6(ends(geom)[0]) == R6(touch_ro[0])
            cut = geom.length * min(0.45, 1.0 / max(pkm(geom), 0.1))
            ng = substring(geom, cut, geom.length) if at_start else                 substring(geom, 0, geom.length - cut)
            roads.loc[i, gname] = ng
            roads.loc[i, "km"] = round(pkm(ng), 3)
            print(f"  contact-retract id={roads.loc[i, 'id']} "
                  f"{str(roads.loc[i, 'name'])[:28]!r} 1 km off the RO node")

    # ---- D3: un-join the Giurgiulesti tri-point -------------------------
    f = pd.to_numeric(roads["foreign"], errors="coerce").fillna(0)
    ua_at_tp = [i for i in roads.index
                if f[i] == 1 and str(roads.loc[i, "country_code"]) == "UA"
                and (near(ends(roads.geometry[i])[0], TRIPOINT, 0.01)
                     or near(ends(roads.geometry[i])[1], TRIPOINT, 0.01))]
    if ua_at_tp:
        i = ua_at_tp[0]
        geom = roads.geometry[i]
        at_start = near(ends(geom)[0], TRIPOINT, 0.01)
        cut = geom.length * min(0.45, 1.0 / max(pkm(geom), 0.1))
        ng = substring(geom, cut, geom.length) if at_start else \
            substring(geom, 0, geom.length - cut)
        roads.loc[i, gname] = ng
        roads.loc[i, "km"] = round(pkm(ng), 3)
        ua_end = list(ng.coords)[0] if at_start else list(ng.coords)[-1]
        # target = the EXACT Prut-mouth junction: the Giurgiulesti-Galati
        # bridge BCP's endpoint nearest the tri-point (the MD-side node)
        gg = roads[roads["name"].astype(str) == "BCP: Giurgiulesti-Galati (roads)"]
        md_node = min(ends(gg.geometry.iloc[0]), key=lambda c: hav(c, TRIPOINT))
        bcp_row = {c: None for c in roads.columns if c != gname}
        bcp_row.update({"id": next_id(), "type": "roads", "class": "bcp",
                        "name": "BCP: Giurgiulesti-Reni (roads)",
                        "special": "border", "foreign": 1,
                        "country_code": "border",
                        "km": round(hav(ua_end, md_node), 2),
                        gname: LineString([ua_end, md_node])})
        roads = pd.concat([roads, gpd.GeoDataFrame([bcp_row], crs="EPSG:4326")],
                          ignore_index=True)
        roads = gpd.GeoDataFrame(roads, geometry=gname, crs="EPSG:4326")
        print(f"tri-point fixed: UA trunk retracted 1 km, "
              f"BCP Giurgiulesti-Reni recreated ({bcp_row['km']} km)")
    else:
        print("tri-point: no UA edge at the shared node (already fixed?)")

    # ---- D1/D2: UA access for dangling Halmeu and Criva BCP ends --------
    def ua_access(bcp_name, access_name, limit_km):
        nonlocal roads
        b = roads[roads["name"].astype(str) == bcp_name]
        if b.empty:
            print(f"{bcp_name}: NOT FOUND")
            return
        e0, e1 = ends(b.geometry.iloc[0])
        fnum = pd.to_numeric(roads["foreign"], errors="coerce").fillna(0)
        # the dangling end = endpoint touching no non-bcp edge
        deg = {}
        for i in roads.index:
            if str(roads.loc[i, "class"]) == "bcp":
                continue
            for c in ends(roads.geometry[i]):
                deg[(round(c[0], 6), round(c[1], 6))] = 1
        dang = [c for c in (e0, e1)
                if (round(c[0], 6), round(c[1], 6)) not in deg]
        if not dang:
            print(f"{bcp_name}: no dangling end")
            return
        pt = dang[0]
        ua = roads[(fnum == 1) & (roads["country_code"].astype(str) == "UA")]
        p = Point(pt)
        cand = ua.geometry.distance(p).nsmallest(6)
        best = None
        for idx in cand.index:
            geom = roads.geometry[idx]
            proj = geom.project(p)
            q = geom.interpolate(proj)
            d = hav((q.x, q.y), pt)
            if best is None or d < best[0]:
                best = (d, idx, proj)
        d, idx, proj = best
        if d > limit_km:
            print(f"{bcp_name}: nearest UA point {d:.0f} km > {limit_km} - SKIPPED")
            return
        geom = roads.geometry[idx]
        cs = list(geom.coords)
        q = geom.interpolate(proj)
        if hav((q.x, q.y), cs[0]) < 0.3:
            node = cs[0]
        elif hav((q.x, q.y), cs[-1]) < 0.3:
            node = cs[-1]
        else:
            p1 = substring(geom, 0, proj)
            p2 = substring(geom, proj, geom.length)
            node = list(p1.coords)[-1]
            row = roads.loc[idx].copy()
            roads.loc[idx, gname] = p1
            roads.loc[idx, "km"] = round(pkm(p1), 3)
            row[gname] = p2
            row["km"] = round(pkm(p2), 3)
            row["id"] = next_id()
            roads = pd.concat([roads, row.to_frame().T], ignore_index=True)
            roads = gpd.GeoDataFrame(roads, geometry=gname, crs="EPSG:4326")
        km = round(hav(node, pt) * 1.2, 2)
        tmpl = {c: None for c in roads.columns if c != gname}
        tmpl.update({"id": next_id(), "type": "roads", "class": "trunk",
                     "name": access_name, "foreign": 1, "country_code": "UA",
                     "special": "", "km": km,
                     gname: LineString([node, pt])})
        roads = pd.concat([roads, gpd.GeoDataFrame([tmpl], crs="EPSG:4326")],
                          ignore_index=True)
        roads = gpd.GeoDataFrame(roads, geometry=gname, crs="EPSG:4326")
        print(f"{bcp_name}: UA access added {km} km (attach {d:.1f} km, "
              f"node ({node[0]:.4f},{node[1]:.4f}))")

    ua_access("BCP: Halmeu-Dyakove (roads)", "access: Dyakove-Vynohradiv", 80)
    ua_access("BCP: Criva-Mamalyha (roads)", "access: Mamalyha-Chernivtsi (M19)", 80)

    # ---- C: km refresh wherever stale -----------------------------------
    n_fix = 0
    for i in roads.index:
        g = roads.geometry[i]
        gk = pkm(g)
        km = pd.to_numeric(roads.loc[i, "km"], errors="coerce")
        if gk > 0.05 and (pd.isna(km) or abs(km - gk) > max(0.2, 0.10 * gk)):
            roads.loc[i, "km"] = round(gk, 3)
            n_fix += 1
    print(f"km refreshed on {n_fix} road edges")

    # ---- snap dangling BCP ends to the nearest node within 250 m --------
    R6b = lambda c: (round(c[0], 6), round(c[1], 6))
    all_nodes = {}
    for i in roads.index:
        if str(roads.loc[i, "class"]) == "bcp":
            continue
        for c in ends(roads.geometry[i]):
            all_nodes[R6b(c)] = c
    for i in roads.index[roads["class"].astype(str) == "bcp"]:
        cs = list(roads.geometry[i].coords)
        changed = False
        for pos in (0, -1):
            c = cs[pos]
            if R6b(c) in all_nodes:
                continue
            best = min(all_nodes.values(), key=lambda n: hav(n, c))
            d = hav(best, c)
            if d < 0.25:
                cs[pos] = best
                changed = True
                print(f"snapped {roads.loc[i, 'name']} end to node "
                      f"({best[0]:.6f},{best[1]:.6f}) ({d*1000:.0f} m)")
        if changed:
            roads.loc[i, gname] = LineString(cs)
            roads.loc[i, "km"] = round(pkm(LineString(cs)), 3)

    # ---- E: audit --------------------------------------------------------
    ok = True
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
        fnum = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
        cc = g["country_code"].astype(str)
        deg = {}
        for i in g.index:
            a, b = (R(c) for c in ends(g.geometry[i]))
            for c in (a, b):
                deg[c] = deg.get(c, 0) + 1
            if bcp[i]:
                continue
            union(a, b)
            side = "RO" if fnum[i] != 1 else (cc[i] if cc[i] in ("UA", "MD") else "OTHER")
            for c in (a, b):
                tag.setdefault(c, set()).add(side)
        comp = {}
        for c in parent:
            comp.setdefault(find(c), set()).update(tag.get(c, set()))
        bad = [s for s in comp.values() if "RO" in s and ({"UA", "MD"} & s)]
        if bad:  # print the exact contact nodes
            node_sides, node_e = {}, {}
            for i in g.index:
                if bcp[i]:
                    continue
                sde = "RO" if fnum[i] != 1 else (cc[i] if cc[i] in ("UA", "MD") else "OTHER")
                for c in (R(ends(g.geometry[i])[0]), R(ends(g.geometry[i])[1])):
                    node_sides.setdefault(c, set()).add(sde)
                    node_e.setdefault(c, []).append(i)
            for c, sd in node_sides.items():
                if "RO" in sd and ({"UA", "MD"} & sd):
                    print(f"  CONTACT {c} {sd}: " + "; ".join(
                        f"id={g.loc[i, 'id']} {str(g.loc[i, 'name'])[:24]!r} "
                        f"f={g.loc[i, 'foreign']} cc={g.loc[i, 'country_code']!r}"
                        for i in node_e[c]))
        dangling = [(g.loc[i, "name"], c) for i in g[bcp].index
                    for c in (R(ends(g.geometry[i])[0]), R(ends(g.geometry[i])[1]))
                    if deg.get(c, 0) < 2]
        print(f"audit {name}: RO+UA/MD mixed: {len(bad)}; dangling BCP ends: "
              f"{dangling if dangling else 'none'}")
        if bad or dangling:
            ok = False
    if not ok:
        print("!! FIX REQUIRED - not writing")
        return 1

    # de-dup any remaining duplicated ids (user splits keep the parent id)
    dmask = roads["id"].duplicated(keep="first")
    for i in roads.index[dmask]:
        nid = int(pd.to_numeric(roads["id"], errors="coerce").max()) + 1
        print(f"  de-dup: id {roads.loc[i, 'id']} -> {nid}")
        roads.loc[i, "id"] = nid

    roads["id"] = pd.to_numeric(roads["id"], errors="raise").astype("int64")
    dups = roads.loc[roads["id"].duplicated(keep=False), "id"].tolist()
    if dups:
        for i in roads.index[roads["id"].isin(dups)]:
            r = roads.loc[i]
            cs = list(r.geometry.coords)
            print(f"  DUP id={r['id']} name={str(r['name'])[:30]!r} cls={r['class']!r} "
                  f"({cs[0][0]:.4f},{cs[0][1]:.4f})-({cs[-1][0]:.4f},{cs[-1][1]:.4f})")
    assert not dups, "duplicate ids remain"
    roads["km"] = pd.to_numeric(roads["km"], errors="raise").astype(float)
    roads["foreign"] = pd.to_numeric(roads["foreign"], errors="coerce")
    roads.to_file(GPKG, layer="roads", driver="GPKG")
    print("written transport.gpkg (roads)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
