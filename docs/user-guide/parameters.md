# Parameters

DisruptSC v2 uses YAML configuration files in `config/`.

## Load Order

1. `config/default.yaml` (shipped)
2. `config/user_defined_<scope>.yaml` (optional, shipped for bundled demos only)
3. `config/user_defined_<scope>.local.yaml` (optional, gitignored — your personal tweaks)
4. Supported CLI overrides

Supported CLI overrides are:

```bash
disruptsc Cambodia --simulation_type disruption --duration 90 --io_cutoff 0.95
```

## Core Parameters

```yaml
simulation_type: "initial_state"
t_final: 10
time_resolution: "week"
export_files: false
logging_level: "info"
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

File paths are relative to the scope folder in the resolved data root:

```yaml
filepaths:
  transport: "Transport/transport.gpkg"
  multimodal: "Transport/multimodal.gpkg"
  mrio: "Economic/mrio.csv"
  sector_table: "Economic/sector_table.csv"
  usd_per_ton: "Economic/usd_per_ton.csv"
  households_spatial: "Spatial/households.geojson"
  countries_spatial: "Spatial/countries.geojson"
  firms_spatial: "Spatial/firms.geojson"
  inventory_duration_targets: "Economic/inventory_targets.csv"
  admin: "Spatial/admin.geojson"
```

## Transport Parameters

```yaml
with_transport: true
transport_modes: ["roads", "maritime"]
capacity_constraint: "off"
transport_to_households: true
use_route_cache: true
route_optimization_weight: "cost_per_ton"
```

Transport networks are loaded from a GeoPackage configured by
`filepaths.transport`. Layer names should match `transport_modes`.

## Agent And Supply Chain Parameters

```yaml
io_cutoff: 0.95
cutoff_sector_output:
  type: "absolute"
  value: 1.0
  unit: "mUSD"
cutoff_firm_output:
  type: "absolute"
  value: 10
  unit: "kUSD"
nb_suppliers_per_input: 1
weight_localization_firm: 1
weight_localization_household: 4
utilization_rate: 0.8
```

## Inventory Parameters

```yaml
inventory_duration_targets:
  definition: "per_input_type"
  unit: "day"
  values:
    default: 30
inventory_restoration_time: 4
enable_household_inventories: false
adaptive_inventories: false
```

## Disruptions

Use the `disruptions` key for new configuration:

```yaml
simulation_type: "disruption"
disruptions:
  - type: "transport_disruption"
    description_type: "edge_attributes"
    attribute: "name"
    values: ["road_1"]
    start_time: 1
    duration: 4
```

The legacy key `events` is accepted for backward compatibility, but new files
should use `disruptions`.

## Criticality

```yaml
simulation_type: "criticality"
criticality:
  duration: 4
  scenarios:
    - name: road_1
      edges: ["road_1"]
```

## Performance Workflow

Use cache presets from the CLI while iterating:

```bash
disruptsc Cambodia --cache same_transport_network_new_agents
disruptsc Cambodia --cache same_logistic_routes
```

Use `--cache_isolation` for concurrent runs that should not share pickle cache
files.
