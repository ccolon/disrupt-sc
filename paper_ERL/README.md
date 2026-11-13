# paper_ERL — reproducible figures for the ERL manuscript

Notebooks, data and outputs that reproduce the figures of the ERL manuscript
(`phd-thesis/ERL_manuscript/`, main text and supplementary). Notebooks only, no scripts;
all paths are relative, so the folder can be moved, zipped or attached as is.

## Contents

```
paper_ERL/
├── 01_hazard_and_scenario_maps.ipynb    flood hazard, disruption scenarios, road vulnerability   [climada_env]
├── 02_indirect_losses_boxplots.ipynb    single-basin vs multi-basin household losses             [dsc]
├── 03_indirect_losses_cascading.ipynb   losses vs the temporal-ratio parameter τ                 [dsc]
├── 04_indirect_losses_sectors.ipynb     sectoral time series and household-loss maps            [dsc]
├── 05_economic_flow_maps.ipynb          flows of goods on the transport network                 [dsc]
├── 06_sensitivity_inventory.ipynb       sensitivity analysis — inventory multiplier M            [dsc]
├── data/
│   ├── monte_carlo/    Monte Carlo results, one row per simulation run
│   ├── scenarios/      per-scenario model output (4d/8d/12d country-scale runs)
│   ├── reference/      sector table, GADM boundaries, disrupted road network
│   └── climada/        flood-hazard forecasts (HDF5), HydroBASINS, HydroRIVERS, OSM roads
└── figures/
    ├── manuscript/     the 14 PNG files of the manuscript's figures folder (reference)
    └── generated/      what the notebooks write
```

Run each notebook top to bottom from this folder. Every plotting cell is the original
analysis code; the only edits are file paths, one save line per figure, and the label
change noted for Fig. 2(b).

## Getting the data

`data/` is not in the git repository (about 1.3 GB, several files above GitHub's 100 MB
limit). It is shared separately as a single zip, `paper_ERL_data.zip` (220 MB
compressed, 99 files); ask the authors for access.

Unzip it at the repository root; the archive already contains the `paper_ERL/data/` prefix,
so every file lands where the notebooks expect it:

```
cd disrupt-sc
unzip paper_ERL_data.zip
```

`climada/HydroRIVERS_v10_as.gdb` is clipped to a box around Cambodia (the original
covers all of Asia), and `climada/roads_edges_osm.geojson` keeps only the `fclass`
column with coordinates at 5 decimals. Notebook 01 gives the same figures with either
version.

## Figure index

Main text (`main.tex`):

| label | figure file | produced by |
|---|---|---|
| `fig:flowchart` | `DisruptSC+CLIMADA - Flowchart(1).png` | drawn diagram — not code |
| `fig:scenarios` | `fig_multibasin_cambodia_merged.png` | (a) drawn timing schematic; (b) `01` → `fig_multibasin_cambodia_merged_panel_b.png` |
| `fig:res1` | `fig_sectors_time_space.png` | `04` |
| `fig:res2` | `fig_singlevsmulti_short.png` | `02` |
| `fig:res3` | `cascading_multi-basin_scenarios_v2.png` | left panel: `03` → `cascading_multi-basin_scenarios_v2_left_panel`; right panel: drawn timing schematic |

Supplementary (`supplementary.tex`), in order of appearance:

| label | figure file | produced by |
|---|---|---|
| `fig:si_case` | `cambodia_basins_rivers_roads.png` | `01` |
| `fig:si_vuln` | `jrc_vulnerability_function_roads.png` | `01` |
| `fig:si_direct` | `fig_direct_impacts.png` | `01` |
| `fig:si_cumulative` | `fig_sectors_losses_cumulative_errors_labels.png` | `04` (re-implemented — see below) |
| `fig:si_sectors` | `fig_sectors_losses_short.png` | `04` |
| `fig:si_flows` | `fig_flows_full_durations.png` | `05` |
| `fig:si_singlevsmulti` | `fig_singlevsmulti_merge.png` | `02` |

Two files in `figures/manuscript/` are not referenced by the manuscript:
`cambodia_three_scenario.png` (an earlier rendering of the Fig. 2(b) map, with T0/T1/T2
labels) and `multi-basin scenario.png` (drawn schematic).

## How the figures were verified

- `fig_flows_full_durations`, `fig_direct_impacts` and `jrc_vulnerability_function_roads`:
  the manuscript files are byte-identical to outputs of the source notebooks; the
  regenerated files have the same pixel size (2301×2913, 1211×989, 1739×1357).
- `cambodia_basins_rivers_roads` and the Fig. 2(b) map: same pixel size as the manuscript
  files (8363×4068 and 8294×2593, i.e. 300 dpi saves of the source figures).
- Plotly figures (`02`, `03`): the regenerated figures carry the same trace data as the
  stored outputs of the source notebook, and are exported to PNG at the manuscript sizes
  (1800×800 and 1400×1800; 1200×900 for the τ panel, which sits cropped in the composite). For the τ panel, the published values are reproduced from
  the merged 230927 cascading sweeps (e.g. 12-day mean 284 M$ and 8-day mean 91 M$ at τ = 1).
- `04`: the printed summary statistics (sectoral totals 1.194 / 4.339 / 13.759 M$, household
  totals 2.190 / 6.271 / 16.726 M$, top-ten sector ranking) match the source notebook
  character for character.

## Things to know

**Environments.** `dsc` conda env for notebooks 02–06 (pandas, geopandas, matplotlib,
plotly, contextily). `climada_env` for notebook 01 (CLIMADA, climada_petals, rasterio,
fiona). Plotly figures are saved both as interactive HTML and as PNG at the manuscript size
(1800×800, 1400×1800, 1200×900, 900×600) through the `kaleido` package, which is installed in
`dsc` (version 0.2.1; plotly prints a deprecation notice about it, harmless).

**Basemaps.** Maps download OpenStreetMap / CartoDB tiles, so they need internet. OSM's tile
policy requires an identifying User-Agent — with the library default the server returns
"Access blocked" placeholder tiles — so the map notebooks set
`ctx.tile.USER_AGENT` to a descriptive project string. Tile imagery may differ slightly from
the manuscript files over time; all data layers are identical.

**`fig_sectors_time_space` colours.** The manuscript file was made with an earlier version of
the loss files in which the three smallest top-ten sectors ranked MFO ≥ MTO ≥ CON; the current
files rank them MTO ≥ CON ≥ MFO. Colours are assigned by rank, so those three sectors swap
colours relative to the manuscript file; curves, maps and values are unchanged. The
manuscript file is also slightly wider (1849 px vs 1634 px) because of legend layout.

**Representative run vs Monte Carlo.** Figs. 3, S `fig:si_sectors` and S `fig:si_flows`
use a single simulation per duration (the representative realization in `data/scenarios/`),
which is also the source of the numbers in Section 3.1. Monte Carlo ensembles enter only
Fig. 4, Fig. 5 and S `fig:si_singlevsmulti` (plus the bars of `fig:si_cumulative`, below).
`loss_per_region_sector_time.csv` is the representative run's household loss by supplying
sector; the analysis keeps the Cambodian (`KHM_`) sectors, so the 1.194 / 4.339 / 13.759 M$
quoted in the text are household losses on domestically supplied goods (2.18 / 6.22 / 16.59 M$
if the imported-goods sectors are included).

**`fig_sectors_losses_cumulative_errors_labels` (`fig:si_cumulative`) — revised figure.** The
cell that produced the submitted PNG was not preserved. Decoding that PNG (calibrated on its
red-dot labels) showed bars = largest non-outlier realization (2.49 / 6.75 / 41.98 M$) rather
than the ensemble mean stated in the caption, and red dots = the domestic-goods subset
(1.19 / 4.34 / 13.76 M$) while the bars were total household losses. Notebook `04` now produces
a **revised figure**: bars = ensemble mean (2.27 / 5.32 / 18.20 M$) and whiskers = ±1 SD
(0.08 / 0.48 / 8.32 M$) of the non-outlier realizations of the Fig. 4 ensemble; red dots = the
representative run's total household loss (2.18 / 6.22 / 16.59 M$). The switches
`BAR_STATISTIC = 'max'` and `RED_DOTS = 'domestic'` reproduce the submitted version. The
manuscript text must be updated accordingly (Section 3.1 numbers, captions of Fig. 3, S4 and S5).

**Temporal-cascading data.** The τ panel uses the two 230927 cascading sweeps merged
(`cambodia_simulations_results_230927_cascading.csv` + `_v2.csv`). A later sweep run on
2023-10-13 forecasts gives different values and was not used for the manuscript, so it is not
included here. Above τ = 2 the merged 230927 data pool two batches of
runs; this is how the published panel was made and is reproduced as is.

## Data provenance

`data/monte_carlo` and `data/scenarios` come from the DisruptSC Cambodia runs
(`disrupt-sc_cambodia/analysis/`); `data/reference` from the DisruptSC Cambodia inputs and
GADM 4.1; `data/climada` from the climada-disruptsc workflow (CLIMADA river-flood forecasts
for 2023-09-19 / 09-27 / 10-13, HydroBASINS level 6, HydroRIVERS v10 Asia, OpenStreetMap
roads). Household-loss maps aggregate on the GADM `NAME_2` district name, which is not unique
(two names cover several polygons); the effect on the published totals is below 1 % and is
reproduced as is.
