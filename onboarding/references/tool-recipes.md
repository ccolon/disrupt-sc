# Tool recipes — exact commands, formats, gotchas

All commands assume the conda env with the toolchain installed is activated
(`conda activate`; miniforge **base** on the main workstation). Never call `python.exe`
by full path (tnclean crashes silently). Windows: always `--no-progress` for tnclean.
`<parent>` = the folder containing the disrupt-sc repo (see RUNBOOK.md §Environment
layout for locations and clone URLs).

---

## 1. mrio-extractor  (`<parent>/MRIO/mrio-extractor`)

**Not a CLI.** Flat directory of standalone scripts, each configured by editing the
`# CONFIGURATION` block of module-level constants at its top. `SOURCE`/`OUTPUT` are
**cwd-relative** — always run from inside `mrio-extractor`. Output goes to `output/` (gitignored).

| Database | Script | Source on disk | Years |
|---|---|---|---|
| OECD ICIO | `extract_mrio_oecd.py` | `../ICIO/2025_ed_reg/<year>_SML.csv` (ext edition in `2025_ed_ext/`) | 2016–2022 |
| FIGARO-REG | `extract_mrio_figaro.py` | `../FIGARO/FIGARO-REG/2013_io/io_unstack.feather` | 2013 only wired up |
| EMERGING-E | `extract_mrio_emerging_e.py` | `../EMERGING-E/EMERGING_E_2018.mat` (970 MB HDF5, streamed) | 2018 |
| GLORIA | `extract_mrio_gloria.py` | `../GLORIA/mrio_va_fd.pkl` (3.4 GB pickle) | single unlabelled vintage |

Selection constants (same semantics in every extractor; precedence EXTERNAL > INTERNAL > RoW):
- `INTERNAL_REGIONS`: `"all"` or list of codes — kept as full (region × sector) blocks.
- `EXTERNAL_REGIONS`: dict `bloc_label -> [source codes]` — each bloc becomes ONE aggregated
  `imports` row + ONE `exports` column. A code in both lists is externalized. Unclaimed → `"RoW"`.
- `REGION_ALIASES`: `source_code -> target_label`, internal mapping only (e.g. FIGARO NUTS2→ISO3:
  `{"FR10": "FRA", ...}`; ICIO ext: `{"CN1": "CHN", "CN2": "CHN"}`).
- `SECTOR_AGGREGATION`: `None`/`"all"` = native codes; else dict. Convention differs:
  OECD/FIGARO/EMERGING-E use `{source: target}`, GLORIA uses `{target: [sources]}`. Shipped
  mappings: `SECTOR_AGGREGATION_GLORIA` in the OECD script (50→15), `SECTOR_AGGREGATION_16 =
  "group16"` for EMERGING-E (146→16 via `emerging_e_sectors.csv`).
- `AGGREGATE_FINAL_DEMAND` / `AGGREGATE_VALUE_ADDED`: keep `True` for DisruptSC.
- `ZERO_EXTERNAL_TO_EXTERNAL` (OECD script; port to others when needed): keep `True` —
  zeroes the bloc-to-bloc imports×exports block. DisruptSC v2 never uses those cells but
  they dominate the flow_coverage value budget (Romania: $199T of $208T) and silently
  starve real partner→scope import cells (phase 8 finding, validation rec #1).
- `SECTOR_RESOLVED_IMPORTS` (OECD script): keep `True` — external blocs get
  (BLOC, sector) import rows instead of one aggregated "imports" row, preserving the
  product dimension so DisruptSC cargo-types import flows (grain by barge, machinery by
  truck; needs disrupt-sc ≥ the 2026-08-28 commit). Exports column stays aggregated.
- **Corridor-basin sub-blocs**: split any *land-corridor* aggregate bloc (like "rest of
  Europe") by which corridor bundle its members can physically use — route assignment is
  winner-take-all per OD, so one gateway point picks ONE corridor for the whole bloc.
  Romania EUR → EURDAN (Danube basin: barge+rail+road), EURCE (overland via HU), EURNW
  (incl. Rhine–Main–Danube), EURS (Mediterranean), EURSE (via BGR). Maritime blocs
  (ASI/AME/ROW) stay whole — their port-of-entry choice is a routing question, not bloc
  structure. Geographic splits preserve mode substitution; modal splits (EUR-road/-iww)
  would kill it.

Run sequence:
```bash
cd <parent>/MRIO/mrio-extractor
# 1. edit CONFIGURATION block of the chosen extractor, then:
python extract_mrio_oecd.py                      # -> output/<OUTPUT>.csv
python diagnose_mrio.py output/<name>.csv        # regions, sectors, blocs, labels
# 2. sector table
python init_sector_table_config.py --mrio output/<name>.csv --out output/sector_table_config.yml
#    edit sector_type / usd_per_ton in the YAML (types: agriculture mining manufacturing
#    utility construction trade transport services; usd_per_ton only for physical types)
# 2b. usd_per_ton from BACI unit values (preferred over guessing; ~3 min over 12M rows):
python compute_usd_per_ton_baci.py --scope <ISO3[,ISO3]> \
    --baci <path>/BACI_HS17_Y2023_V202501.csv --patch-config output/sector_table_config.yml
#    HS->ICIO mapping in hs17_to_icio_concordance.csv (editable, longest-prefix match;
#    validated 100% of Romania's trade value). Reports scope-mix density per sector
#    (world fallback below --min-tons), drops per-HS6 unit-value outliers, flags 'mixed'
#    sectors where tonnage and value concentrate on different products.
python generate_sector_table.py output/<name>.csv --config output/sector_table_config.yml
#    -> output/<name>_sector_table.csv
# 3. copy to the scope
cp output/<name>.csv               <data-root>/<Scope>/Economic/mrio.csv
cp output/<name>_sector_table.csv  <data-root>/<Scope>/Economic/sector_table.csv
```

Output contract (matches DisruptSC's `Mrio.load`): CSV with 2 header rows + 2 index columns;
row blocks = internal (region, sector), then (bloc, `imports`), then (`ALL`, `Value added`);
column blocks = internal (region, sector), then (region, `Final demand`), then (bloc, `exports`).
Units: **millions** USD (EUR for FIGARO), 2 decimals.

Gotchas:
- Region codes: ISO3 everywhere except FIGARO (2-letter + NUTS2, Greece = `EL`) — alias to ISO3.
- `INTERNAL_REGIONS = "all"` on FIGARO/EMERGING-E → multi-GB output; never needed for a scope.
- Snapshot the CONFIGURATION block into the manifest after each run (KI-05).
- Companion spatial scripts exist (`extract_households_oecd.py`, `extract_firms_oecd.py`) using
  `../Spatial/sources/households_world.geojson` — a quick-start alternative to phase 6 defaults.

---

## 2. osm-extractor  (`transport\transnet\osm-extractor`)

Extraction from a **local Geofabrik PBF** (no download/clip capability — use `scripts/geofabrik.py`).

```bash
osm-extractor info <file>.osm.pbf                      # per-tag feature counts
osm-extractor extract <file>.osm.pbf raw.gpkg \
    --modes roads,railways,waterways,maritime,pipelines \
    --road-level 2 --report extract_report.json
```
- Modes = DisruptSC mode names. **No airways** (KI-07).
- `--road-level`: 1 = motorway+trunk (default), 2 = +primary, 3 = +secondary, 4 = +tertiary.
- Output: one GPKG, one layer per mode, EPSG:4326, LineStrings; columns `osm_id, class, <attrs>`.

Finalization (AFTER tnclean) writes the DisruptSC schema
(`id, type, km, name, class, surface, special, disruption`, unique ids per layer):
```bash
osm-extractor finalize clean.gpkg <Scope>/Transport/transport.gpkg \
    [--keep-extra] [--osm-id-report osm_ids.csv --raw raw.gpkg] [--report finalize_report.json]
```

---

## 3. tnclean  (`transport\transnet\transnet-simp`, package/CLI = `tnclean`)

Pipeline: explode → snap → split → de-overlap → merge-degree-2 → **DBSCAN cluster contraction**
→ remove-small-components → simplify → export. The contraction (`--cluster --cluster-eps`) is the
simplification-strength knob; everything else only trims vertices.

```bash
tnclean clean raw.gpkg clean.gpkg --input-layer roads --output-layer roads \
    --cluster --cluster-eps 5000 --cluster-position centroid \
    --simplify-tolerance 50 --no-progress --report report_roads.json
```
Run once **per mode layer** (input-layer/output-layer = the mode name).

Calibration facts (Moldova roads, 9 717 edges, 7 401 km):
| eps | edges out | runtime | cluster_max_extent |
|---|---|---|---|
| no cluster | 4 334 | 56 s | — |
| 2 000 m (medoid) | 531 | ~17 min | 26.7 km |
| 5 000 m (centroid) | 339 | ~17 min | 56.2 km |

Gotchas:
- **Cluster flags must be on the CLI**: any `cluster_*` key in a `--config` YAML is silently
  overwritten by CLI defaults (KI-08).
- DBSCAN clusters chain transitively — always read `cluster_max_extent` in the report and check it
  doesn't erase geography that matters (isthmus, corridor, border area).
- `--cluster-position medoid` keeps nodes on the network; `centroid` may move them off it.
- Fully in-memory (no tiling). CLI defaults ≠ dataclass defaults (CLI: overlap 20 m, simplify 50 m,
  min-component 5 features / 50 km).
- `tnclean validate input -v` gives data-driven parameter ranges; out-of-range values auto-clamp.

---

## 4. Multimodal — multitnbuild via build_transport.py

`disrupt-sc-data\build_transport.py <Scope>` reads all layers of
`<Scope>/Transport/transport.gpkg` (except `multimodal`) + `<Scope>/Transport/multimodal_config.yml`,
writes `<Scope>/Transport/multimodal.gpkg` (transport.gpkg untouched). Needs `multitnbuild`
pip-installed. `--dry-run` available.

Template (`Gulf` is the committed example):
```yaml
networks:
  - {mode: roads,    anchor_strategy: degree_1_endpoints}
  - {mode: maritime, anchor_strategy: degree_1_endpoints}
connections:
  - {from_mode: roads, to_mode: maritime, max_distance_km: 10.0}
options: {max_distance_km: 5.0, target_crs: EPSG:3857, split_edges: false, deduplicate: false}
output_dir: .
merge_outputs: true
```
Connectors carry `multimodes` strings like `roads-maritime` — each one needs a matching key under
`logistics.dwell_times` and `logistics.loading_fees` in the scope config.

---

## 4b. European network extension — `scripts/extend_network_tent.py`

For scopes whose external gateways should sit at TRUE partner locations (Vienna,
Frankfurt, ...) so border crossing and mode of entry are chosen by routing:

```bash
python scripts/extend_network_tent.py <Scope> --tent <tent_plain.gpkg>
```
Appends TEN-T trunk edges for the CONFIG whitelist countries, flagged `foreign=1`;
stitches them to the domestic border nodes (~1 stitch per crossing and mode); appends
TEN-T multimodal connectors (endpoint-snapped). Rules learned on Romania:
- **Drop every TEN-T edge touching the scope country** (mixed cross-border codes too) —
  they double-represent domestic geometry (the shared lower Danube!) and leak
  territorial tkm into the excluded foreign layer. Stitches carry the crossing.
- Hand `BRIDGES` fill real gaps in the EU-only data (Serbian Danube); endpoints snap
  to live nodes.
- Domestic originals are backed up as `transport_domestic.gpkg` /
  `multimodal_domestic.gpkg`; re-runs must restore them first.
- `validation_metrics.py` excludes `foreign=1` from domestic stats and reports
  stitch/bridge flows as the **border-crossing assignment** (§4b) — validate against
  Eurostat INTL tonnages by mode. Known interpretation limits: transit is not modeled
  (`transit_from` empty by design) and partners hidden in ROW enter at the wrong
  gateway, so real border tonnage anchors are upper bounds.

## 5. DisruptSC assembly facts

- Config resolution: `config/default.yaml` ← `config/user_defined_<Scope>.yaml` ←
  `config/user_defined_<Scope>.local.yaml` (recursive merge, later wins; `.local.yaml` gitignored).
  Template: `config/user_defined_Testkistan.yaml`.
- Data path: `DISRUPT_SC_DATA_PATH/<Scope>` if set, else `../disrupt-sc-data/<Scope>`.
- Live `filepaths` keys: `mrio`, `sector_table`, `households_spatial`, `firms_spatial`,
  `countries_spatial`, `transport`, `multimodal` (+ optional `input_criticality`).
  `usd_per_ton`, `inventory_duration_targets`, `admin` are **dead keys** (KI-03).
- `transport_modes` never lists `multimodal` (loaded separately). Every enabled mode needs
  `logistics.speeds` (missing → silent 50 km/h) and `logistics.basic_cost` (missing → 0.01/t-km).
- `logistics.cost_of_time` accepts a scalar (USD/t·h) or a per-cargo-type dict with
  `default` — the per-cargo form is required for commodity-differentiated mode choice
  (see validation-report.md, rec-2 calibration). Sector types beyond the classic eight
  are legal in sector_table (`oil_and_gas` → liquid_bulk cargo via `sector_to_cargo_type`).
- Transport gpkg: one LineString layer per mode, EPSG:4326. Nodes are derived from endpoints
  rounded to 6 decimals — edges connect only if endpoints match at 1e-6°.
- `countries.geojson`: one Point per external bloc, `region` property = bloc label exactly as in
  the MRIO; missing bloc = hard ValueError; points snap to the nearest **roads** node.
- `households.geojson`: Points, `region` (∈ MRIO internal regions; non-matching rows silently
  dropped), `population`, optional `subregion_*`. Also the region-centroid source for firms.
- `firms.geojson` wide form: `region` + one column per exact MRIO sector name → melted to
  (location × sector) with the value as importance; zero/NaN dropped.
- Run: `validate-inputs <Scope>` then `disruptsc <Scope> --simulation_type initial_state --open`.
  The flag is `--flow_coverage` (docs mentioning `--input_coverage` are stale, KI-04).

---

## 6. firm-extractor  (`<parent>/Firms/firm-extractor`, data library `<parent>/Firms/`)

Per-scope YAML config, never edit-in-place (see `configs/example.yaml`). Long-format
output: `region, sector, importance, name, source` — consumed by DisruptSC's long-form
firms branch; after KI-17 the importance values set firm sizes proportionally.

```bash
cd <parent>/Firms/firm-extractor && pip install -e .
firm-extractor sources            # adapters, data presence, fetch hints
firm-extractor coverage cfg.yaml  # dry-run: sector -> source proposal
firm-extractor build cfg.yaml     # firms.geojson + *_coverage.csv
```

Key rules baked into the tool:
- ONE source per sector (ordered preference list): importance is relative within a
  region_sector, so units cancel — but only if bases are never mixed there.
- Grid sources (mapspam) are zonal-aggregated to the scope's admin POLYGONS (the
  geoBoundaries files from phase 6 step 3, not the household points), then placed at
  `weighted_centroid` (default) / `max_cell` / `representative_point`.
- Concordances in `<repo>/concordance/*_to_icio.csv` target ICIO 2025 native codes
  (A01 crops, B05 coal, B07 metal ores, C24A/C24B basic metals, D power). Copy +
  rewrite the `sector` column for aggregated schemes; `mine:*`/`proc:*`/`*` wildcards
  are matched after exact codes.
- Adapters: `jasansky` (weight = latest-year production, then capacity, then presence;
  Region/Company pseudo-facilities dropped), `mapspam` (`_A` rasters only),
  `gem_power` (the 8 per-technology GEM power trackers in `<parent>/Firms/GEM/`;
  operating units, MW; validated on Romania 2026-08-31: 639 units, 20.8 GW ≈ national
  total, Cernavodă/Iron-Gate shares exact; small-hydro under tracker thresholds missing),
  `gem_steel` (GIST plant-level; reported production > capacity), `gem_cement` (GCCT;
  production > cement > clinker capacity; Romania: 9 plants / 15.4 Mtpa = the full industry).
- **Vintage trap**: GEM status is "today", the MRIO is usually 2020–2022. Set
  `source_options: {gem_steel: {statuses: [... mothballed...], reference_year: <MRIO yr>}}`
  or plants idled since the MRIO year vanish — Romania: default 3 mills/1.0 Mt vs vintage
  5 mills/3.5 Mt with Liberty Galați restored at its 2022-era 1.6 Mt (≈ national output).
  Decide at the phase-6 checkpoint, per scope.
- Data caveats live in `Firms/README.md` and KI-18/19/20 — CEADS swapped lat/lon +
  suspect units, GID no-coordinates/licensing, Maus payload not downloaded.
- `manual` adapter: per-scope CSV of hand-curated anchor facilities
  (`source_options: {manual: {csv: <Scope>/Spatial/sources/manual_firms.csv}}`,
  columns `sector,name,lon,lat,weight[,iso3,unit,note]`; sector used as-is, no
  concordance). Use for flagship few-plant sectors no database sees (automotive,
  shipyards, a mis-weighted chemicals anchor); every row's figure needs a source in
  `note`, and the CSV is a **user checkpoint** — the human vouches for the rows.
- `climatetrace` adapter (API, no download): facility points + MODELLED activity/capacity
  per year 2021–2026 from api.climatetrace.org (CC-BY-4.0), 23 default subsectors spanning
  most manufacturing/mining/fossil ICIO sectors; set `source_options: {climatetrace:
  {reference_year: <MRIO yr>, subsectors: [...]}}` — the year matters (Alro Slatina 2022:
  105 kt vs 2024: 59 kt). Country-aggregate pseudo-assets are auto-dropped. Romania check:
  closes C24B (Slatina + Tulcea alumina) and C19 (all 4 refineries, plausible crude-run
  ranking) in one source; per-facility confidence is often "low" — use for relative
  within-sector weights, verify totals nationally.
- `gem_coalmine` adapter: Coal Mine Tracker "Non-closed mines" + built-in "Historic
  Production (2018-2025)" sheet - `reference_year` gives exact-year reported output per
  mine (Romania 2022: 7 mines, 16.7 Mt = national lignite). NOTE the tracker's 'ISO Code'
  column is NUMERIC ISO 3166-1; countries are matched by name via the shared GEM map.
  Prefer over climatetrace for B05.
- `gem_goget` adapter: GOGET "Field-level main data" + long production table
  ("Quantity (converted)" per Unit ID x Data Year); weight = reference_year production,
  else the field's latest year, else presence. Covers only large fields (Romania: ~half
  of national gas output) - still far better than population for B06.
- `regional_stats` adapter: any (admin x sector) table (employment, GVA) -> one point per
  admin unit per sector at the polygon's representative point. IDENTITY_CONCORDANCE: the
  CSV carries scope sector codes; section->sectors expansion happens at CSV build where it
  is reviewable. Admin names matched after case/diacritic normalization, unmatched names
  fail loudly. For EU scopes `scripts/eurostat_nuts3_employment.py` fetches NUTS3
  employment (nama_10r_3empers) and applies the expansion map in one command - this is the
  systematic replacement of population weights for services + dispersed manufacturing.
- Romania-style extras for `regional_stats`: its `csv` option accepts a LIST of long-format
  files (e.g. Eurostat employment + an INS table). `scripts/ins_tempo_fetch.py` pulls any
  county-level INS Tempo (Romania) matrix into that format with zero manual download - the
  pivot endpoint needs the `encQuery` form (colon-separated dims, comma-separated
  nomItemIds); the JSON `arr` form silently returns an empty pivot. Forestry example:
  AGR306A (harvested wood by county) -> A02 weights; the script strips "Municipiul "
  prefixes so Bucharest matches the polygon names.
- `osm_landuse` adapter: extraction-site footprints (B08) without the Copernicus-gated
  CLC download - reads `landuse=quarry` multipolygons from the scope's Geofabrik PBF
  (usually already on disk from phase 5), area-weighted (km2, EPSG:8857). CRITICAL:
  the largest OSM "quarries" are open-pit coal/metal mines (Romania: Jilt 16.6 km2) -
  always set `exclude_from` (drops polygons within radius_km of another source's mine
  points; tag/name filters alone are insufficient, only 2/782 Romanian pits carried a
  resource tag). Romania after exclusion: 743 quarries, 125 km2, max 3.7 km2.
