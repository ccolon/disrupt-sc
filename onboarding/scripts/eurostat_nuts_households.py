"""EU scopes: households.geojson + admin polygons from GISCO NUTS and Eurostat population.

Replaces the geoBoundaries path of ``build_spatial.py`` for European scopes,
where the NUTS classification is the natural (and Eurostat-consistent) admin
grid: households live at NUTS2 (or NUTS3) representative points with the
Eurostat population, and the NUTS3 polygons serve as the firm-extractor's
admin boundaries (``regional_stats`` employment weights are published per NUTS3).

Steps (each a subcommand, so the download can be approved separately):

  fetch      download the GISCO NUTS 2021 polygons (public, EU copyright notice
             applies: "© EuroGeographics for the administrative boundaries").
                 python eurostat_nuts_households.py fetch --out <dir> [--levels 2,3]
             Files: NUTS_RG_20M_2021_4326_LEVL_<n>.json (~3 MB for level 2,
             ~6 MB for level 3) from
             https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/

  households NUTS polygons + population CSV -> households.geojson
                 python eurostat_nuts_households.py households \
                     --nuts <dir>/NUTS_RG_20M_2021_4326_LEVL_2.json \
                     --population <population_nuts_2023.csv> \
                     --countries AUT,BEL,...,CHE --out <Scope>/Spatial/households.geojson
             Points at representative points; properties: region (ISO3 of the
             internal MRIO region), population, subregion_nuts<n>, name.

  admin      NUTS3 polygons -> one admin GeoJSON with region (ISO3) + shapeName
             for firm-extractor (``region_property: region``).
                 python eurostat_nuts_households.py admin \
                     --nuts <dir>/NUTS_RG_20M_2021_4326_LEVL_3.json \
                     --countries ... --out <Scope>/Spatial/sources/nuts3_admin.geojson

The population CSV is the Eurostat ``demo_r_pjanaggr3`` extract written by the
onboarding session (columns geo, label, population_2023, level); any CSV with a
``geo`` column and one population column works (``--pop-field``).
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iso_codes import ISO2_TO_ISO3  # noqa: E402

GISCO = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
FILE = "NUTS_RG_20M_2021_4326_LEVL_{level}.json"
EUROSTAT_TO_ISO2 = {"EL": "GR", "UK": "GB"}


def cntr_to_iso3(cntr: str) -> str | None:
    iso2 = EUROSTAT_TO_ISO2.get(cntr, cntr)
    return ISO2_TO_ISO3.get(iso2)


def cmd_fetch(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for lvl in [int(x) for x in args.levels.split(",")]:
        name = FILE.format(level=lvl)
        dest = out / name
        if dest.exists() and not args.force:
            print(f"exists: {dest}")
            continue
        url = GISCO + name
        print(f"downloading {url} -> {dest}")
        req = urllib.request.Request(url, headers={"User-Agent": "disruptsc-onboarding/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
            f.write(r.read())
        print(f"  {dest.stat().st_size / 1e6:.1f} MB")
    return 0


def _load_nuts(path: str, countries: list[str]) -> gpd.GeoDataFrame:
    g = gpd.read_file(path)
    g["region"] = g["CNTR_CODE"].map(cntr_to_iso3)
    keep = set(countries)
    g = g[g["region"].isin(keep)].copy()
    missing = keep - set(g["region"])
    if missing:
        print(f"WARN no NUTS polygons for: {sorted(missing)}")
    return g


def cmd_households(args) -> int:
    countries = [c.strip().upper() for c in args.countries.split(",")]
    g = _load_nuts(args.nuts, countries)
    level = int(g["LEVL_CODE"].iloc[0])
    pop = pd.read_csv(args.population)
    pop = pop.set_index("geo")[args.pop_field]
    g["population"] = g["NUTS_ID"].map(pop)
    n_missing = int(g["population"].isna().sum())
    if n_missing:
        print(f"WARN {n_missing} NUTS{level} units without population "
              f"({', '.join(g.loc[g.population.isna(), 'NUTS_ID'].head(12))}...) "
              f"-> filled with their country's median unit population")
        med = g.groupby("region")["population"].transform("median")
        g["population"] = g["population"].fillna(med).fillna(g["population"].median())
    pts = g.geometry.representative_point()
    out = gpd.GeoDataFrame({
        "region": g["region"].values,
        "population": g["population"].round().astype(int).values,
        f"subregion_nuts{level}": g["NUTS_ID"].values,
        "name": g["NUTS_NAME"].values,
    }, geometry=pts.values, crs="EPSG:4326")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_file(args.out, driver="GeoJSON")
    per = out.groupby("region")["population"].agg(["count", "sum"])
    print(f"written {args.out}: {len(out)} NUTS{level} household points, "
          f"{out.population.sum() / 1e6:.1f} M people")
    print(per.to_string())
    return 0


def cmd_admin(args) -> int:
    countries = [c.strip().upper() for c in args.countries.split(",")]
    g = _load_nuts(args.nuts, countries)
    out = gpd.GeoDataFrame({
        "region": g["region"].values,
        "shapeName": g["NUTS_NAME"].values,
        "nuts_id": g["NUTS_ID"].values,
        "level": g["LEVL_CODE"].values,
    }, geometry=g.geometry.values, crs="EPSG:4326")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_file(args.out, driver="GeoJSON")
    print(f"written {args.out}: {len(out)} polygons, {out.region.nunique()} countries")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--out", required=True)
    f.add_argument("--levels", default="2,3"); f.add_argument("--force", action="store_true")
    h = sub.add_parser("households"); h.add_argument("--nuts", required=True)
    h.add_argument("--population", required=True); h.add_argument("--pop-field", default="population_2023")
    h.add_argument("--countries", required=True); h.add_argument("--out", required=True)
    a = sub.add_parser("admin"); a.add_argument("--nuts", required=True)
    a.add_argument("--countries", required=True); a.add_argument("--out", required=True)
    args = ap.parse_args()
    return {"fetch": cmd_fetch, "households": cmd_households, "admin": cmd_admin}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
