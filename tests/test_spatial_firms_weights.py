"""Spatial firms integration must distribute MRIO output across a region_sector's
points in proportion to the file's per-point values (population, plant capacity,
production tonnage) - not equally. Equal split (the pre-KI-17 behavior) made
supplier choice distance-only within a region_sector and defeats plant-level
calibration. Files without usable values keep the equal-split fallback."""

import geopandas as gpd
import pytest
from shapely.geometry import Point

from disruptsc.init_pipeline.agents import _integrate_spatial_firms


class _StubMrio:
    sectors = ["CAR", "FRV"]

    def get_total_output(self):
        return {("ECU", "CAR"): 100.0, ("ECU", "FRV"): 40.0}


def _base_ft():
    # MRIO-derived firm table: one firm per region_sector at the region centroid.
    return gpd.GeoDataFrame(
        {
            "region_sector": ["ECU_CAR", "ECU_FRV"],
            "region": ["ECU", "ECU"],
            "sector": ["CAR", "FRV"],
            "importance": [100.0, 40.0],
        },
        geometry=[Point(0, 0), Point(0, 0)],
        crs="EPSG:4326",
    )


def test_wide_file_values_become_proportional_weights(tmp_path):
    # Two CAR plants with weights 3:1 -> 75/25 of the 100 MRIO output.
    wide = gpd.GeoDataFrame(
        {"region": ["ECU", "ECU"], "CAR": [3.0, 1.0]},
        geometry=[Point(-79, -1), Point(-78, -2)],
        crs="EPSG:4326",
    )
    path = tmp_path / "firms.geojson"
    wide.to_file(path, driver="GeoJSON")

    result = _integrate_spatial_firms(_base_ft(), path, _StubMrio())
    car = result[result["region_sector"] == "ECU_CAR"].sort_values("importance", ascending=False)
    assert list(car["importance"]) == pytest.approx([75.0, 25.0])
    assert car["importance"].sum() == pytest.approx(100.0)
    # FRV has no spatial data -> the MRIO-derived firm survives untouched.
    frv = result[result["region_sector"] == "ECU_FRV"]
    assert len(frv) == 1 and frv["importance"].iloc[0] == pytest.approx(40.0)


def test_long_file_without_values_keeps_equal_split(tmp_path):
    long = gpd.GeoDataFrame(
        {"region": ["ECU", "ECU"], "sector": ["CAR", "CAR"]},
        geometry=[Point(-79, -1), Point(-78, -2)],
        crs="EPSG:4326",
    )
    path = tmp_path / "firms.geojson"
    long.to_file(path, driver="GeoJSON")

    result = _integrate_spatial_firms(_base_ft(), path, _StubMrio())
    car = result[result["region_sector"] == "ECU_CAR"]
    assert list(car["importance"]) == pytest.approx([50.0, 50.0])
