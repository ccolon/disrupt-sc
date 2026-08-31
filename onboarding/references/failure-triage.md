# initial_state failure triage (in pipeline order)

Stages: transport network → agents (MRIO, sector table, firms, households, countries) →
supply-chain network → logistic routes → one t=0 step.

| Error / symptom | Source | Cause → fix |
|---|---|---|
| `DISRUPT_SC_DATA_PATH points to '…', but that folder does not exist` (at import) | `paths.py:28` | Stale env var → unset it or fix the path. |
| Log: `No user-defined or local parameter file for <Scope>` then run uses pure defaults | `config.py:55` | Config filename mismatch (`user_defined_<Scope>.local.yaml`, scope spelled exactly). |
| `The following config keys are no longer used (replaced by flow_coverage)` | `config.py:107` | Legacy `io_cutoff` / `cutoff_*` / `input_coverage` keys copied from an old scope config → replace with `flow_coverage`. |
| `FileNotFoundError: Transport GeoPackage not found` | `transport.py:34` | `filepaths.transport` wrong or file not copied. |
| `ValueError: No transport edges loaded` | `transport.py:78` | Every layer name mismatched `transport_modes` → layer names must equal mode strings exactly. |
| `N duplicate edge IDs found — reassigning all IDs sequentially` (warning) | `transport.py:87` | Ids collide across layers (hand-added layer?) → re-run `osm-extractor finalize`, or accept (breaks disruption-by-id configs only). |
| `ValueError: Edge N (<mode>): km is nan` / `speed is 0 or nan` | `transport_network.py:722` | NaN km → geometry problem in that edge; speed 0 → explicit 0 in `logistics.speeds` → set a real speed. |
| `ValueError: Intermediary matrix not square: (m, n)` | `mrio.py:445` | A region_sector present on one axis only — usually a zero row/col was dropped on one side, or a label regex misclassified a sector (check reserved words). Run `check_scope.py --economic-only`. |
| `No label matching 'final.?demand\|household' in MRIO` → zero demand, degenerate model | `mrio.py:438` | Final-demand column label wrong → keep `Final demand`. |
| Sector columns silently misclassified (weird region/sector counts in log) | `mrio.py:434` | Sector name matches a reserved regex (`export/import/tax/va/capital/government/investment/household/final demand`) → rename the sector. |
| `N region_sectors with input > output, adjusting export` (silent) | `mrio.py:452` | MRIO internally inconsistent; small N is tolerable, large N → check aggregation weights. |
| `ValueError: Sector table missing column: region\|sector\|type` | `load_data.py:21` | Regenerate sector table via `generate_sector_table.py`. |
| `sector_table is missing the 'type' entry for N MRIO sector(s)` | `agents.py:118` | Sector table not regenerated after re-aggregation → regenerate; type must be consistent across regions. |
| `Spatial firms file has no columns matching MRIO sectors` → all firms at region centroids | `agents.py:819` | Wide firms.geojson column names ≠ MRIO sector names (case/spacing) → rebuild with `build_spatial.py firms-default`. |
| `NotImplementedError: Transaction-based firm creation not yet implemented in v2` | `agents.py:57` | `firm_data_type: transaction_based` in config → use default mode. |
| `ValueError: Country 'XXX' is present in the MRIO but missing from countries.geojson` | `agents.py:679` | Add a Point feature for that bloc (or list it in `countries_no_transport`). |
| `ValueError: <buyer>: no supplier for <region_sector>` | `supply_chain.py:276` | flow_coverage filtered a sector someone still buys from, or a region has no firm for it → raise `flow_coverage`, check firms.geojson covers all region_sectors. |
| `RuntimeError: Cannot initialize: N commercial links have no route. M transport nodes are unreachable. … K connected component(s).` | `routing.py:1862` | **The #1 new-scope blocker.** Transport graph is multi-component: endpoints don't coincide at 1e-6°, a mode island has no multimodal connector, or a country point snapped to an isolated roads fragment. Log lists up to 20 offending node pairs (lat/lon) — inspect those in QGIS. Fixes: re-run tnclean (snapping), add multimodal connections, raise `max_distance_km`, remove islands (`--min-component-*`), move country points. `check_scope.py` reports components before you ever run. |
| `LP routing cannot start: no candidate routes` / `OD-cargo group N has no candidate route` / `LP routing failed to find a feasible initial-state assignment` | `routing.py:353/420/473` | Over-tight `transport_capacity_overrides` or a cargo type with capacity 0 on every viable mode → relax capacities, check `sector_to_cargo_type` vs available modes, or set `use_cargo_types: False`. |
| `ValueError: Link A→B: delivery_in_tons is 0` / `is nan` | `commercial_link.py:130` | usd_per_ton missing/zero for a physical sector → fix sector_table `usd_per_ton`. |

General debugging aids: `--log_level debug`, `--flow_coverage 0.5` (smaller problem to isolate),
`--cache same_transport_network_new_agents` (skip network rebuild while iterating on agents).
