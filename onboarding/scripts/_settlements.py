"""Settlement gazetteer helpers (v26 decision D14).

Every admin-derived demand/firm point must sit at the *seat settlement* of
its admin unit, not at the admin polygon's representative point: for
mountain or elongated units the representative point can fall tens of km
from the built-up area (Arad county 65 km, Municipiul Baia Mare 11 km up
the Firiza valley), which fabricates "critical" access edges in the
criticality sweep and distorts haul lengths.

Source: Spatial/sources/geonames_ro_places.csv - GeoNames RO populated
places (download.geonames.org/export/dump/RO.zip, CC-BY 4.0), slimmed to
feature class P. Seat choice inside each polygon: feature-code priority
PPLC (capital) > PPLA (county seat) > PPLA2 (commune seat) > rest, then
population. Polygons containing no gazetteer place keep their
representative point (caller-side fallback).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

_PRIO = {"PPLC": 5, "PPLA": 4, "PPLA2": 3}


def load_places(src_dir) -> gpd.GeoDataFrame:
    df = pd.read_csv(Path(src_dir) / "geonames_ro_places.csv")
    g = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326")
    g["prio"] = g["fcode"].map(_PRIO).fillna(0).astype(int)
    return g


def seat_points(polys: gpd.GeoDataFrame, places: gpd.GeoDataFrame) -> dict:
    """Map each polygon's index to its seat-settlement Point.

    Polygons without any contained place are absent from the result -
    callers fall back to representative_point() and should report it.
    """
    j = gpd.sjoin(places[["prio", "population", "geometry"]],
                  polys[["geometry"]], how="inner", predicate="within")
    j = j.sort_values(["index_right", "prio", "population"],
                      ascending=[True, False, False])
    best = j.drop_duplicates("index_right").set_index("index_right")
    return dict(best.geometry.items())
