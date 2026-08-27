# Parameters

DisruptSC v2 uses YAML configuration files in `config/`.

## Load Order

1. `config/default.yaml` (shipped)
2. `config/user_defined_<scope>.yaml` (optional, committed — the scope's shared configuration)
3. `config/user_defined_<scope>.local.yaml` (optional, gitignored — machine-specific overrides)
4. Supported CLI overrides

Keep science parameters in the committed scope file so they travel with git;
use the `.local` file for absolute paths and personal experiments.

Supported CLI overrides are:

```bash
disruptsc Cambodia --simulation_type disruption --duration 90 --flow_coverage 0.95 --seed 42
```

## Core Parameters

```yaml
simulation_type: "initial_state"
t_final: 10                 # in time_resolution units
time_resolution: "week"     # day | week | month | year
export_files: false
seed: null                  # integer -> reproducible supplier selection + MC draws
```

Supported `simulation_type` values in the current v2 runtime:

| Type | Purpose |
|------|---------|
| `initial_state` | Baseline run without configured disruptions. |
| `disruption` | Run configured transport, capital, or productivity disruptions. |
| `criticality` | Run infrastructure criticality scenarios. |

## Data Parameters

```yaml
firm_data_type: "mrio"
monetary_units_in_model: "mUSD"
monetary_units_in_data: "mUSD"
```

The current v2 runtime supports MRIO mode. Transaction-based firm creation is
not implemented.

File paths are relative to the scope folder in the resolved data root. A
`repo:<relpath>` value resolves against the **code repository** instead — use
it for inputs committed with the code (e.g. an input-criticality matrix under
`studies/`). Absolute paths pass through unchanged.

```yaml
filepaths:
  transport: "Transport/transport.gpkg"
  multimodal: "Transport/multimodal.gpkg"
  mrio: "Economic/mrio.csv"            # .csv or .parquet
  sector_table: "Economic/sector_table.csv"
  households_spatial: "Spatial/households.geojson"
  countries_spatial: "Spatial/countries.geojson"
  firms_spatial: "Spatial/firms.geojson"
  # Optional: adapted-Leontief criticality matrix (see production function)
  input_criticality: "repo:studies/earthquake/additional_data/input_criticality.csv"
```

## Agent And Supply Chain Parameters

Agent and link filtering is controlled by **one knob**:

```yaml
flow_coverage: 0.95
```

For each MRIO buyer column *and* each supplier row, cells are kept largest-first
until their cumulative share reaches `flow_coverage`; the union of the two kept
sets defines which region-sectors, external countries, and bilateral flows are
modeled. Every kept agent retains at least this fraction of both its in-flows
and its out-flows. Range `(0, 1]`; typical values 0.7 (sparse, fast) to 0.99
(dense, slow). It replaces the legacy `input_coverage` / `cutoff_*` knobs,
which are ignored with a warning.

```yaml
nb_suppliers_per_input: 1      # 1, 2, or a fraction in (1,2) = stochastic 1-or-2 mix
weight_localization_firm: 1    # supplier choice ~ importance / distance^w
weight_localization_household: 4
utilization_rate: 0.8          # eq output / production capacity; sets the idle-capital buffer
time_to_activate_idle_capital: 30   # DAYS to mobilize idle capital (must exceed one time step)
capital_to_value_added_ratio: 3     # capital stock = ratio x annual value added
critical_input_threshold: 0.0  # Partially-Binding Leontief materiality floor (0 = strict)
sectors_to_include: "all"
sectors_to_exclude: null
```

## Inventory Parameters

All durations are in **days** and converted to time steps internally.

```yaml
inventory_duration_targets:      # firm input buffers, keyed on sector_table 'type'
  definition: "per_input_type"
  unit: "day"
  values:
    default: 30
inventory_restoration_time: 30   # DAYS to close the inventory gap (smaller = more aggressive)
enable_household_inventories: false
household_inventory_duration_target:   # separate retail/pantry scheme; see default.yaml
  definition: "per_input_type"
  unit: "day"
  values:
    default: 7
adaptive_inventories: false      # true -> targets track current orders instead of equilibrium
adaptive_supplier_weight: false  # true -> orders shift toward suppliers that deliver
capacity_constrained_orders: false  # true -> capacity-hit firms stop over-ordering inputs
```

## Transport Parameters

```yaml
with_transport: true
transport_modes: ["roads", "maritime"]
transport_to_households: true
use_route_cache: true
use_cargo_types: true            # false -> one "any" cargo bucket, ~N x faster routing
capacity_constraint: "off"       # off | gradual | binary  (typos raise an error)
price_increase_threshold: 2      # give up delivery if rerouting cost rises beyond this factor
sectors_no_transport_network: ['utility', 'transport', 'trade', 'services', 'service', 'construction']
countries_no_transport: []       # country pids whose flows bypass the network entirely
```

Transport networks are loaded from a GeoPackage configured by
`filepaths.transport`. Layer names should match `transport_modes`.

### Routing knobs (under `logistics:`)

These govern the initial route assignment when `capacity_constraint` is on.
Defaults are in code; set them under the `logistics:` block.

| Key | Default | Meaning |
|-----|---------|---------|
| `initial_route_assignment` | `heuristic` | `heuristic` (chunked candidate routing), `lp` (candidate-path LP), or `edge_lp` (multi-commodity edge-flow LP) |
| `chunk_size` | very large | tons/day granularity for splitting flows across routes |
| `route_candidate_count` / `route_candidate_stretch` | 4 / 3.0 | heuristic candidate routes per OD group and max cost stretch vs the best |
| `lp_route_candidate_count` / `lp_route_candidate_stretch` | 20 / 4.0 | same, for the candidate-path LP |
| `lp_overcapacity_limit` | 1.1 | utilization beyond which the LP overflow penalty applies |

Top-level: `capacity_routing_max_iterations` (default 3) bounds the heuristic's
re-routing rounds; `default_transport_capacity` and
`transport_capacity_overrides` set per-mode / per-edge capacities in tons/day
(a dict override **blocks** any cargo type it does not list — a warning says so).

## Disruptions

```yaml
simulation_type: "disruption"
disruptions:
  - type: "transport_disruption"
    attribute: "name"
    values: ["road_1"]
    start_time: 1
    duration: 4
```

Types: `transport_disruption`, `transport_disruption_probability`,
`capital_destruction` (uniform via `filter:`, or absolute per canton x sector
via `description_type: subregion_file` + `file:`), and `productivity_shock`.
Filters accept firm attributes and `subregion_*` keys, and log how many firms
they matched. Firm-side recovery is threshold-only (`recovery_shape` is
ignored with a warning); absolute capital destruction recovers only through
the reconstruction market (`reconstruction_market: true` + its
`reconstruction_*` settings). The legacy key `events` is accepted for backward
compatibility, but new files should use `disruptions`.

## Criticality

Each scenario is a **list of edge names** (one run per inner list):

```yaml
simulation_type: "criticality"
criticality:
  duration: 4
  scenarios:
    - ["road_1"]
    - ["road_1", "port_main"]
```

See [Criticality Analysis](criticality.md) for the legacy per-edge loop,
`top_n`, and resumable runs.

## Performance Workflow

Use cache presets from the CLI while iterating:

```bash
disruptsc Cambodia --cache same_transport_network_new_agents
disruptsc Cambodia --cache same_logistic_routes
```

Caches are keyed by scope and validated against a per-stage fingerprint of the
configuration: a cache built under different watermarked settings is refused
with a key-level diff instead of silently reused. Runtime knobs (`t_final`,
disruptions, `time_to_activate_idle_capital`, …) do not invalidate caches, so
sweeps over them can safely reuse one build. Use `--cache_isolation` for
concurrent runs that should not share pickle cache files.

Every exporting run writes `parameters.yaml` (full config snapshot),
`run_fingerprint.json` (code version, git SHA, watermarked keys), and
`exp.log` next to its outputs.
