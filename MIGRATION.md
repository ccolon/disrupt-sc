# Migrating from DisruptSC v1 to v2

v2.0.0 is a major release with breaking changes in the CLI, module layout, configuration schema, and data layout. This page lists what changed and how to adapt.

If you prefer not to migrate, the v1 line is preserved unchanged at:

- Branch: [`legacy/v1`](https://github.com/ccolon/disrupt-sc/tree/legacy/v1)
- Tag: [`v1-last-submodule`](https://github.com/ccolon/disrupt-sc/releases/tag/v1-last-submodule)

---

## CLI entry points

The console scripts keep the same names but now point to new modules.

| Script            | v1 target                                | v2 target                           |
| ----------------- | ---------------------------------------- | ----------------------------------- |
| `disruptsc`       | `disruptsc.main:main`                    | `disruptsc.run:main`                |
| `validate-inputs` | `disruptsc.model.input_validation:main`  | `disruptsc.validate_inputs:main`    |

**Impact:** If you installed v1 in editable mode and upgrade in place, reinstall with `pip install -e .` so entry points pick up the new targets.

CLI flags are largely the same (`--cache`, `--simulation_type`, `--duration`, `--io_cutoff`, `--cache_isolation`, `--version`). New in v2: `--log_level`, `--verbose`, `--open`.

---

## Python API / module layout

v1's `Model`/`Parameters` orchestration is gone. v2 is pipeline-style: explicit stages for data loading, agent building, network building, routing, caching, and simulation.

| v1 import                                           | v2 equivalent                                              |
| --------------------------------------------------- | ---------------------------------------------------------- |
| `from disruptsc.model.model import Model`           | removed; compose the pipeline directly via `disruptsc.run` or the `init_pipeline` / `run_pipeline` modules |
| `from disruptsc.parameters import Parameters`       | `from disruptsc.config import load_config, build_params` returning flat config dict + `TransportParams`/`SimParams`/`AgentParams`/`LogisticsParams` dataclasses from `disruptsc.params` |
| `disruptsc.model.agent_builders.{firm,household,country}` | `disruptsc.init_pipeline.agents` (consolidated)       |
| `disruptsc.model.network_builders.transport`        | `disruptsc.init_pipeline.transport`                        |
| `disruptsc.model.network_builders.supply_chain`     | `disruptsc.init_pipeline.supply_chain`                     |
| `disruptsc.model.utils.caching`                     | `disruptsc.run_pipeline.cache`                             |
| `disruptsc.model.validation.inputs`                 | `disruptsc.validate_inputs`                                |
| `disruptsc.simulation.factory.ExecutorFactory`      | functions in `disruptsc.run_pipeline.simulate` (`run_initial_state`, `run_disruption`, `run_criticality`) |
| `disruptsc.agents.transport_mixin`                  | `disruptsc.agents.transport_utils`                         |

The `Model` class is not replaced with a new class. If you were embedding DisruptSC as a library, the canonical entry point is now `disruptsc.run.main()` (read it top-to-bottom to see the pipeline stages) or call `disruptsc.run_pipeline.*` functions directly.

---

## Configuration changes

### Transport file paths

v1 had one GeoJSON per transport mode under `filepaths`. v2 consolidates them into two GeoPackage layers.

**v1:**
```yaml
filepaths:
  transport_modes: "Transport/transport_modes.csv"
  roads_edges:      "Transport/roads_edges.geojson"
  multimodal_edges: "Transport/multimodal_edges.geojson"
  maritime_edges:   "Transport/maritime_edges.geojson"
  airways_edges:    "Transport/airways_edges.geojson"
  railways_edges:   "Transport/railways_edges.geojson"
  waterways_edges:  "Transport/waterways_edges.geojson"
  pipelines_edges:  "Transport/pipelines_edges.geojson"
```

**v2:**
```yaml
filepaths:
  transport:  "Transport/transport.gpkg"
  multimodal: "Transport/multimodal.gpkg"
```

The GeoPackages carry per-mode layers internally. v1 per-mode GeoJSONs are no longer read.

### Logistics

- `shipment_methods_to_transport_modes` and `sector_types_to_shipment_method` are replaced by a single `logistics.sector_to_cargo_type` mapping with cargo types `dry_bulk`, `liquid_bulk`, `container`.
- New `logistics.dwell_times` and `logistics.loading_fees` are supported per multimodal transition.

### New top-level keys

- `capacity_routing_max_iterations` — number of capacity-aware routing iterations
- `default_transport_capacity` — fallback capacity per mode
- `enable_household_inventories` — households can now hold inventories
- `firm_transport_share`, `country_transport_share` — uniform transport-share defaults

### Changed defaults

- `io_cutoff`: **0.01 → 0.95**. v2 uses a stricter input-mix filter by default. If you want v1 behavior, set `io_cutoff: 0.01` in your scope file.

### Deprecations

- `events` is still read but deprecated in favor of `disruptions`. v2 logs a warning and maps `events` → `disruptions`.

### Local overrides (new)

v2 reads `user_defined_<scope>.local.yaml` on top of the committed scope file. The local file is gitignored. Use it for personal tweaks (short `t_final`, local `DISRUPT_SC_DATA_PATH`, etc.) without modifying the shared config.

---

## Data layout

- The `data/` git submodule is removed. Bundled demo data for `Testkistan` is committed under `examples/data/Testkistan/`.
- For full regional scopes, clone the data repo alongside this repo (`../disrupt-sc-data`) or set `DISRUPT_SC_DATA_PATH`.
- Resolution order: `DISRUPT_SC_DATA_PATH` → sibling `../disrupt-sc-data` → bundled `examples/data/`.

If you had local edits inside the old `data/` submodule, move them into a cloned `disrupt-sc-data` or into the bundled example folder, and remove any `.gitmodules`/`data` submodule references from your working copy.

---

## Monte Carlo and simulation types

No breaking changes. `mc_repetitions`, `simulation_type` (`initial_state`, `disruption`, `criticality`), and the disruption factory pattern continue to work. Internally they were reorganized into `run_pipeline/simulate.py`, `run_pipeline/disruption.py`, and `disruption/`.

---

## Upgrade checklist

1. `git fetch && git checkout main` (v2 is now on `main`).
2. Reinstall: `pip install -e .` (picks up new console script targets).
3. Remove any `data/` submodule entry from your clone; either point `DISRUPT_SC_DATA_PATH` at your existing data folder or clone the data repo as `../disrupt-sc-data`.
4. Rewrite your scope's `filepaths` block to use `transport.gpkg` + `multimodal.gpkg` (or re-run against a freshly prepared data folder).
5. Update any direct Python imports per the table above.
6. Scan your scope YAML for `io_cutoff`, `events` → `disruptions`, and removed `shipment_methods_to_transport_modes` keys.
7. `validate-inputs <scope>` to confirm the config is still readable.

If you hit something not covered here, open an issue; cite the v1 commit or behavior you're comparing against.
