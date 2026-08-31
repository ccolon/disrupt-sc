# Firm/plant/grid production data sources — survey (verified 2026-08)

Open datasets usable as spatial weights to allocate MRIO sectoral output to
subnational locations (phase 6 firm-level path). Local holdings live in
`<parent>/Firms/` (see its README); this file is the wider menu. "GEM" =
Global Energy Monitor: all its trackers are CC-BY-4.0, form-gated xlsx/GeoJSON
downloads, refreshed 1-2x/yr.

Defensibility ladder (use the highest rung available per sector):
facility production > facility capacity > modelled facility activity
(Climate TRACE) > sector grid (SPAM, EDGAR) > non-residential built volume
(GHS NRES) > population.

## Top picks by sector family

| Sector family | Dataset | Variable (point/grid) | Latest | Access | URL |
|---|---|---|---|---|---|
| Power | GEM Global Integrated Power Tracker | capacity MW, point | 2026, 2x/yr | CC-BY, form | https://globalenergymonitor.org/projects/global-integrated-power-tracker/ |
| Steel | GEM Global Iron & Steel Tracker (≥500 ktpa) | capacity ttpa by route, point | 2026 | CC-BY, form | https://globalenergymonitor.org/projects/global-iron-and-steel-tracker/ |
| Cement | GEM Global Cement & Concrete Tracker | capacity Mtpa, point | 2026 | CC-BY, form | https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/ |
| Oil & gas upstream | GEM GOGET | **production Mboe/y** per field, point | 2026 | CC-BY, form | https://globalenergymonitor.org/projects/global-oil-gas-extraction-tracker/ |
| Refineries, LNG, pipelines | OGIM v2.7 (EDF); GEM GGIT/GOIT | facility points + capacity where reported | 2025 | CC-BY | https://zenodo.org/records/13259749/latest |
| Mining | FINEPRINT/Jasansky (LOCAL) + GEM Coal Mine Tracker (production Mtpa) | production t, point | 2021 / 2026 | CC-BY | https://doi.org/10.5281/zenodo.7369478 ; https://globalenergymonitor.org/projects/global-coal-mine-tracker/ |
| Crops | SPAM 2020 v2r2 (LOCAL) | production t / 10 km cell, 46 crops | 2020 (r2 2026) | CC-BY, direct | https://www.mapspam.info/data/ |
| Livestock | FAO GLW4 | head / 1-10 km cell | 2020 | CC-BY, direct | https://data.apps.fao.org/catalog/iso/9d1e149b-d63f-4213-978b-317a8eb42d02 |
| Fisheries | Global Fishing Watch effort | fishing hours / 0.01° cell | 2012-2024 | free, registration; CC-BY-SA/NC per product | https://globalfishingwatch.org/dataset-and-code-fishing-effort/ |
| Pulp-paper, petrochem | SFI/CGFI GeoAsset (3,403 pulp-paper; 342 ethylene crackers; also cement/steel/aquaculture) | location + capacity where known, point | 2024 | CC-BY, direct | https://cgfi.ac.uk/spatial-finance-initiative/geoasset-project/geoasset-databases/ |
| Cross-sector gap filler | Climate TRACE source-level (steel, cement, aluminium, chemicals, refining, pulp-paper, glass, mines...) | modelled monthly activity + emissions, point | monthly, 2021- | CC-BY, direct | https://climatetrace.org/data |
| Residual manufacturing | GHS-BUILT-V NRES | non-res built volume m3 / 100 m cell | 2030 epochs | open, direct | https://human-settlement.emergency.copernicus.eu/ghs_buV2023.php |
| Gazetteer / residual | OSM industrial tags; Overture places (GeoParquet+DuckDB) | presence/area | continuous | ODbL / CDLA-P | https://docs.overturemaps.org/guides/places/ |

## Notes and second choices

- **Power**: WRI Global Power Plant Database v1.3 (2021) adds modelled GWh but is
  frozen/unmaintained — use GIPT; Climate TRACE for actual-generation weights.
- **Aluminium / fertilizer**: no dedicated open tracker. Climate TRACE subsectors;
  407 geocoded ammonia plants in the Nature Food supplements
  (https://www.nature.com/articles/s43016-024-00979-y); USGS Mineral Commodity
  Summaries for country totals.
- **Mining fallbacks**: Maus et al. polygons = area proxy, no commodity attribution
  (KI-20, CC-BY-SA); USGS MRDS = huge but frozen-2011 gazetteer.
- **Agriculture**: GAEZ v5 (2025) is attainable/potential yield — for shift scenarios,
  not weights; EarthStat is circa-2000, superseded by SPAM.
- **EDGAR 2025** 0.1° sector emission grids: activity proxy for energy-intensive
  industry where no facility data exists (https://edgar.jrc.ec.europa.eu/).
- **VIIRS nighttime lights** (https://eogdata.mines.edu/products/vnl/): aggregate
  activity only — weak sector attribution, last resort above population.
- **Registries**: GLEIF LEI (CC0, HQ addresses — ownership linking, not plants);
  national geocoded business registers (FR SIRENE, UK Companies House...) are
  excellent where they exist but per-country; OpenCorporates/ORBIS effectively
  commercial.

## Cross-cutting caveats

1. Nearly all facility trackers give **capacity, not output** — assume uniform
   within-country utilization or blend with Climate TRACE activity.
2. Tracker size thresholds drop small plants: check the tracked share of national
   capacity (USGS/FAO totals) before treating points as exhaustive weights —
   the firm-extractor coverage report is where this check lands.
3. Grid products are model allocations benchmarked to admin statistics: safe to
   aggregate to admin units, unsafe cell-by-cell — hence zonal + placement, never
   raw cell points.
