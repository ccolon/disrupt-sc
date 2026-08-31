"""Build the DisruptSC spatial inputs for a scope: households, default firms, countries.

Subcommands:

  admin-fetch    Download geoBoundaries (gbOpen) admin boundaries.
      python build_spatial.py admin-fetch --iso3 KAZ,UZB --level 1 --out <dir>

  households     Admin polygons -> households.geojson (Points at representative points).
      python build_spatial.py households --admin KAZ=<path> --admin UZB=<path> \
          [--pop-field POP] [--pop-csv <csv with name,population>] [--name-field shapeName] \
          --level 1 --out <Scope>/Spatial/households.geojson

  firms-default  households + sector_table -> wide firms.geojson
                 (one column per sector of the point's region, value = population).
      python build_spatial.py firms-default --households <path> \
          --sector-table <Scope>/Economic/sector_table.csv --out <Scope>/Spatial/firms.geojson

  countries      MRIO external blocs + a bloc,lon,lat CSV -> countries.geojson.
      python build_spatial.py countries --mrio <Scope>/Economic/mrio.csv \
          --points <csv: region,lon,lat[,name]> --out <Scope>/Spatial/countries.geojson

The agent must ask the user before admin-fetch downloads.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

import pandas as pd

GB_API = "https://www.geoboundaries.org/api/current/gbOpen/{iso3}/ADM{level}/"
UA = {"User-Agent": "disruptsc-new-scope/1.0"}


def cmd_admin_fetch(args) -> int:
    import geopandas as gpd  # noqa: F401  (validates env early)

    os.makedirs(args.out, exist_ok=True)
    for iso3 in [c.strip().upper() for c in args.iso3.split(",") if c.strip()]:
        api = GB_API.format(iso3=iso3, level=args.level)
        req = urllib.request.Request(api, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            meta = json.load(resp)
        url = meta.get("gjDownloadURL")
        if not url:
            print(f"ERROR: geoBoundaries has no ADM{args.level} for {iso3}", file=sys.stderr)
            return 1
        dest = os.path.join(args.out, f"{iso3}_adm{args.level}.geojson")
        print(f"{iso3}: {url} -> {dest}")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=300) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        print(f"  {os.path.getsize(dest) / 1e6:,.1f} MB")
    return 0


def cmd_households(args) -> int:
    import geopandas as gpd

    frames = []
    for spec in args.admin:
        if "=" not in spec:
            print(f"ERROR: --admin must be ISO3=path, got {spec}", file=sys.stderr)
            return 1
        region, path = spec.split("=", 1)
        gdf = gpd.read_file(path)
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        name_field = args.name_field if args.name_field in gdf.columns else None
        names = gdf[name_field] if name_field else pd.Series([f"{region}_{i}" for i in range(len(gdf))])

        if args.pop_field and args.pop_field in gdf.columns:
            pop = pd.to_numeric(gdf[args.pop_field], errors="coerce")
        elif args.pop_csv:
            lookup = pd.read_csv(args.pop_csv)
            lookup.columns = [c.strip().lower() for c in lookup.columns]
            m = dict(zip(lookup["name"].astype(str).str.strip(), lookup["population"]))
            pop = names.astype(str).str.strip().map(m)
            missing = names[pop.isna()].tolist()
            if missing:
                print(f"WARN: {region}: no population match for {len(missing)} units: {missing[:10]}")
        else:
            pop = pd.Series([None] * len(gdf))

        if pop.isna().all():
            print(f"WARN: {region}: no population data - using uniform weight 1.0 "
                  "(final demand will be split evenly across admin units)")
            pop = pd.Series([1.0] * len(gdf))
        pop = pop.fillna(pop.median())

        out = gpd.GeoDataFrame(
            {
                "region": region.upper(),
                "population": pop.values,
                f"subregion_adm{args.level}": names.values,
            },
            geometry=gdf.geometry.representative_point(),
            crs="EPSG:4326",
        )
        frames.append(out)
        print(f"{region}: {len(out)} household points, total population {out['population'].sum():,.0f}")

    result = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    result.to_file(args.out, driver="GeoJSON")
    print(f"Written {len(result)} points -> {args.out}")
    return 0


def cmd_firms_default(args) -> int:
    import geopandas as gpd

    hh = gpd.read_file(args.households)
    st = pd.read_csv(args.sector_table)
    for col in ("region", "sector"):
        if col not in st.columns:
            print(f"ERROR: sector_table missing column '{col}'", file=sys.stderr)
            return 1

    sectors_by_region = st.groupby("region")["sector"].apply(list).to_dict()
    unknown = sorted(set(hh["region"]) - set(sectors_by_region))
    if unknown:
        print(f"WARN: households regions absent from sector_table (their points get no firms): {unknown}")

    firms = hh.copy()
    for sector in sorted(st["sector"].unique()):
        firms[sector] = pd.NA
    for region, sectors in sectors_by_region.items():
        mask = firms["region"] == region
        for sector in sectors:
            firms.loc[mask, sector] = firms.loc[mask, "population"]

    # pd.NA-seeded columns are object dtype; GeoJSON would serialize the
    # filled values as strings, which breaks DisruptSC's importance filter.
    for sector in sorted(st["sector"].unique()):
        firms[sector] = pd.to_numeric(firms[sector], errors="coerce")

    firms.to_file(args.out, driver="GeoJSON")
    n_cols = len(st["sector"].unique())
    print(f"Written {len(firms)} firm points x {n_cols} sector columns -> {args.out}")
    print("(DisruptSC melts columns matching MRIO sector names; NaN entries are dropped.)")
    return 0


def _external_blocs(mrio_path: str) -> set[str]:
    mrio = pd.read_csv(mrio_path, header=[0, 1], index_col=[0, 1])
    imp = {r0 for r0, r1 in mrio.index if re.search("import", str(r1), re.IGNORECASE)}
    exp = {c0 for c0, c1 in mrio.columns if re.search("export", str(c1), re.IGNORECASE)}
    if imp != exp:
        print(f"WARN: import-row blocs {sorted(imp)} != export-column blocs {sorted(exp)}")
    return imp | exp


def cmd_countries(args) -> int:
    import geopandas as gpd
    from shapely.geometry import Point

    blocs = _external_blocs(args.mrio)
    pts = pd.read_csv(args.points)
    pts.columns = [c.strip().lower() for c in pts.columns]
    for col in ("region", "lon", "lat"):
        if col not in pts.columns:
            print(f"ERROR: points CSV needs columns region,lon,lat (got {list(pts.columns)})", file=sys.stderr)
            return 1

    given = set(pts["region"].astype(str))
    missing = sorted(blocs - given)
    extra = sorted(given - blocs)
    if missing:
        print(f"ERROR: no point for MRIO bloc(s): {missing} - DisruptSC hard-fails on these", file=sys.stderr)
        return 1
    if extra:
        print(f"WARN: points for regions not in the MRIO (ignored by the model): {extra}")

    gdf = gpd.GeoDataFrame(
        {"region": pts["region"].astype(str), "name": pts.get("name", pts["region"]).astype(str)},
        geometry=[Point(xy) for xy in zip(pts["lon"], pts["lat"])],
        crs="EPSG:4326",
    )
    gdf.to_file(args.out, driver="GeoJSON")
    print(f"Written {len(gdf)} country points -> {args.out}")
    print("Reminder: each point should sit near a roads edge (it snaps to the nearest roads node)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("admin-fetch")
    p.add_argument("--iso3", required=True)
    p.add_argument("--level", type=int, default=1)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_admin_fetch)

    p = sub.add_parser("households")
    p.add_argument("--admin", action="append", required=True, help="ISO3=path, repeatable")
    p.add_argument("--level", type=int, default=1)
    p.add_argument("--pop-field")
    p.add_argument("--pop-csv")
    p.add_argument("--name-field", default="shapeName")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_households)

    p = sub.add_parser("firms-default")
    p.add_argument("--households", required=True)
    p.add_argument("--sector-table", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_firms_default)

    p = sub.add_parser("countries")
    p.add_argument("--mrio", required=True)
    p.add_argument("--points", required=True, help="CSV with region,lon,lat[,name]")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_countries)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
