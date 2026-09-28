# -*- coding: utf-8 -*-
"""Clean the user's Budjak railway realignment (28 Sep 2026, pass 3).

User edits (railways layer): the two fictitious straight diagonals to the
Izmail line (old 'BCP: Etulia' 38 km and 'BCP: Giurgiulesti-Reni' 53 km)
are DELETED and replaced by the real corridor traced from OpenRailwayMap:
Giurgiulesti yard -> through UA Reni territory -> border hop at Etulia ->
the full 127-km weaving line Vulcanesti-Bolhrad-Taraclia-Basarabeasca.
The Giurgiulesti CFR bridge is shrunk to the physical 0.6-km Prut crossing.

Cleaning:
  1. Four rows share id 2617 -> de-dup; km recomputed on all touched rows.
  2. The user's 'BCP: Etulia' hop gets class='bcp' and country_code='border'
     but DELIBERATELY special='' (no border friction): it is an internal
     weave of one corridor that already pays full friction at its
     endpoints (Giurgiulesti-Reni and Basarabeasca-Serpneve); the WB
     counts it, so the name stays for flow tracking. DECISION - review.
  3. The Giurgiulesti->Etulia segment crosses OUT of Moldova into UA Reni
     territory unnamed; it is split at the exact MDA boundary and a 0.5-km
     piece is named 'BCP: Giurgiulesti-Reni (railways)' (class bcp,
     special='border' - the corridor's real MD->UA gate, WB-counted,
     with the calibrated name); the Reni-territory remainder is labeled UA.
  4. Geography relabel (MDA/UKR polygons, midpoint rule) + audit as in
     pass 2, extended to railways.
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
BND = Path(r"C:/Users/Celian/OneDrive/DisruptSC/Firms/Boundaries")


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
    g = gpd.read_file(GPKG, layer="railways")
    gname = g.geometry.name
    mda = gpd.read_file(BND / "geoBoundaries-MDA-ADM0_simplified.geojson").geometry.union_all()
    ukr = gpd.read_file(BND / "geoBoundaries-UKR-ADM1_simplified.geojson").geometry.union_all()

    def next_id():
        return int(pd.to_numeric(g["id"], errors="coerce").max()) + 1

    # ---- 2: Etulia hop attributes ---------------------------------------
    m = g["name"].astype(str) == "BCP: Etulia (railways)"
    if m.sum() == 1:
        i = g.index[m][0]
        g.loc[i, ["class", "country_code", "special", "foreign"]] = \
            ["bcp", "border", "", 1]
        print("Etulia hop: class=bcp, cc=border, special='' (no extra friction)")

    # ---- 3: split the Giurgiulesti segment at the MDA exit --------------
    if not (g["name"].astype(str) == "BCP: Giurgiulesti-Reni (railways)").any():
        # the segment: starts at the yard (28.2009,45.4721), ends at the
        # Etulia hop start (28.4117,45.5110)
        cand = [i for i in g.index
                if hav(ends(g.geometry[i])[0], (28.2009, 45.4721)) < 0.05
                and hav(ends(g.geometry[i])[1], (28.4117, 45.5110)) < 0.05]
        assert len(cand) == 1, f"Giurgiulesti->Etulia segment: {len(cand)} matches"
        i = cand[0]
        geom = g.geometry[i]
        # walk to the first vertex outside MDA
        cs = list(geom.coords)
        k_exit = next(k for k, c in enumerate(cs) if not mda.contains(Point(c)))
        # boundary crossing between k_exit-1 and k_exit
        seg = LineString([cs[k_exit - 1], cs[k_exit]])
        x = seg.intersection(mda.boundary)
        px = x if x.geom_type == "Point" else list(x.geoms)[0]
        proj = geom.project(px)
        hop_len = geom.length * (0.5 / max(pkm(geom), 0.1))
        p1 = substring(geom, 0, proj)                      # MD: yard -> border
        hop = substring(geom, proj, proj + hop_len)        # the BCP hop
        p3 = substring(geom, proj + hop_len, geom.length)  # UA Reni territory
        base = g.loc[i].copy()
        g.loc[i, gname] = p1
        g.loc[i, "km"] = round(pkm(p1), 3)
        g.loc[i, ["foreign", "country_code"]] = [1, "MD"]
        rows = []
        r = base.copy()
        r[gname] = hop
        r["km"] = round(pkm(hop), 3)
        r["name"] = "BCP: Giurgiulesti-Reni (railways)"
        r["class"] = "bcp"
        r["special"] = "border"
        r["foreign"] = 1
        r["country_code"] = "border"
        r["id"] = next_id()
        rows.append(r)
        r2 = base.copy()
        r2[gname] = p3
        r2["km"] = round(pkm(p3), 3)
        r2["foreign"] = 1
        r2["country_code"] = "UA"
        r2["id"] = next_id() + 1
        rows.append(r2)
        g = pd.concat([g] + [x.to_frame().T for x in rows], ignore_index=True)
        g = gpd.GeoDataFrame(g, geometry=gname, crs="EPSG:4326")
        print(f"Giurgiulesti-Reni BCP inserted at the MDA boundary "
              f"({rows[0]['km']} km hop; MD part {g.loc[i, 'km']} km, "
              f"UA part {rows[1]['km']} km)")

    # ---- 1: de-dup ids, km refresh --------------------------------------
    dmask = g["id"].duplicated(keep="first") | g["id"].isna()
    for i in g.index[dmask]:
        nid = next_id()
        print(f"  id fix: {g.loc[i, 'id']} -> {nid} ({str(g.loc[i, 'name'])[:30]!r})")
        g.loc[i, "id"] = nid
    n_fix = 0
    for i in g.index:
        gk = pkm(g.geometry[i])
        km = pd.to_numeric(g.loc[i, "km"], errors="coerce")
        if gk > 0.05 and (pd.isna(km) or abs(km - gk) > max(0.2, 0.10 * gk)):
            g.loc[i, "km"] = round(gk, 3)
            n_fix += 1
    print(f"km refreshed on {n_fix} rail edges")

    # ---- 4: geography relabel (non-bcp) + audit -------------------------
    fnum = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
    n_md = n_ua = 0
    for i in g.index:
        if str(g.loc[i, "class"]) == "bcp":
            continue
        mid = g.geometry[i].interpolate(0.5, normalized=True)
        cc_i = str(g.loc[i, "country_code"])
        if mda.contains(mid) and (fnum[i] != 1 or cc_i != "MD"):
            g.loc[i, ["foreign", "country_code"]] = [1, "MD"]
            n_md += 1
        elif ukr.contains(mid) and (fnum[i] != 1 or cc_i != "UA"):
            g.loc[i, ["foreign", "country_code"]] = [1, "UA"]
            n_ua += 1
    print(f"geography relabel: {n_md} -> MD, {n_ua} -> UA")

    # contact reconciliation (as in pass 2): a foreign MD/UA edge sharing an
    # exact node with a domestic edge is REVERTED to domestic when its other
    # end has no same-country neighbor, else RETRACTED 1 km off the node
    R0 = lambda c: (round(c[0], 6), round(c[1], 6))
    fnum = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
    is_b = g["class"].astype(str) == "bcp"
    nsd = {}
    for i in g.index:
        if is_b[i]:
            continue
        sde = "RO" if fnum[i] != 1 else str(g.loc[i, "country_code"])
        for c in ends(g.geometry[i]):
            nsd.setdefault(R0(c), set()).add(sde)
    for i in list(g.index):
        if is_b[i] or fnum[i] != 1:
            continue
        cc_i = str(g.loc[i, "country_code"])
        if cc_i not in ("MD", "UA"):
            continue
        e0, e1 = ends(g.geometry[i])
        touch_ro = [c for c in (e0, e1) if "RO" in nsd.get(R0(c), set())]
        if not touch_ro:
            continue
        other = [c for c in (e0, e1) if c not in touch_ro]
        same = any(any(j != i and not is_b[j]
                       and str(g.loc[j, "country_code"]) == cc_i
                       and any(R0(x) == R0(c) for x in ends(g.geometry[j]))
                       for j in g.index)
                   for c in other)
        if not same:
            g.loc[i, ["foreign", "country_code"]] = [0, None]
            print(f"  contact-revert id={g.loc[i, 'id']} "
                  f"{str(g.loc[i, 'name'])[:26]!r} ({cc_i} -> domestic)")
        else:
            geom = g.geometry[i]
            at_start = R0(ends(geom)[0]) == R0(touch_ro[0])
            cut = geom.length * min(0.45, 1.0 / max(pkm(geom), 0.1))
            ng = substring(geom, cut, geom.length) if at_start else                 substring(geom, 0, geom.length - cut)
            g.loc[i, gname] = ng
            g.loc[i, "km"] = round(pkm(ng), 3)
            print(f"  contact-retract id={g.loc[i, 'id']} "
                  f"{str(g.loc[i, 'name'])[:26]!r} 1 km off the RO node")

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
    fnum = pd.to_numeric(g["foreign"], errors="coerce").fillna(0)
    cc = g["country_code"].astype(str)
    bcp = g["class"].astype(str) == "bcp"
    tag, deg = {}, {}
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
    if bad:
        ns, ne = {}, {}
        for i in g.index:
            if bcp[i]:
                continue
            side = "RO" if fnum[i] != 1 else (cc[i] if cc[i] in ("UA", "MD") else "OTHER")
            for c in (R(ends(g.geometry[i])[0]), R(ends(g.geometry[i])[1])):
                ns.setdefault(c, set()).add(side)
                ne.setdefault(c, []).append(i)
        for c, sd in ns.items():
            if "RO" in sd and ({"UA", "MD"} & sd):
                print(f"  CONTACT {c} {sd}: " + "; ".join(
                    f"id={g.loc[i, 'id']} {str(g.loc[i, 'name'])[:26]!r} "
                    f"f={g.loc[i, 'foreign']} cc={g.loc[i, 'country_code']!r}"
                    for i in ne[c]))
    dangling = [(g.loc[i, "name"], c) for i in g[bcp].index
                for c in (R(ends(g.geometry[i])[0]), R(ends(g.geometry[i])[1]))
                if deg.get(c, 0) < 2]
    print(f"audit railways: RO+UA/MD mixed: {len(bad)}; dangling BCP ends: "
          f"{dangling if dangling else 'none'}")
    if bad or dangling:
        print("!! FIX REQUIRED - not writing")
        return 1

    g["id"] = pd.to_numeric(g["id"], errors="raise").astype("int64")
    assert not g["id"].duplicated().any()
    g["km"] = pd.to_numeric(g["km"], errors="raise").astype(float)
    g["foreign"] = pd.to_numeric(g["foreign"], errors="coerce")
    g.to_file(GPKG, layer="railways", driver="GPKG")
    print("written transport.gpkg (railways)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
