# Basic Usage

This guide covers the current v2 command-line interface.

## Command Line Interface

After installing the package with `pip install -e .`, run simulations with:

```bash
disruptsc <scope> [options]
```

You can also run the module directly from the repository:

```bash
python -m disruptsc.run <scope> [options]
```

## Common Commands

```bash
# Run the bundled demo dataset
disruptsc Testkistan

# Override the simulation type from the YAML configuration
disruptsc Testkistan --simulation_type disruption

# Reuse cached components
disruptsc Cambodia --cache same_transport_network_new_agents

# Override selected runtime parameters
disruptsc Cambodia --duration 90 --io_cutoff 0.5

# Use a process-specific cache folder
disruptsc Cambodia --cache_isolation

# Show version and help
disruptsc --version
disruptsc Testkistan --help
```

## Scope Argument

The `scope` argument identifies the case study:

- It must have a parameter file at `config/user_defined_<scope>.yaml` or `config/user_defined_<scope>.local.yaml`.
- It must have a matching data folder under the resolved data location.
- `Testkistan` is bundled at `examples/data/Testkistan`.
- Other scopes are loaded from `DISRUPT_SC_DATA_PATH` when set, otherwise from `../disrupt-sc-data`.

## Supported CLI Options

| Option | Description |
|--------|-------------|
| `--simulation_type` | Override YAML `simulation_type`. Choices: `initial_state`, `disruption`, `criticality`. |
| `--cache` | Reuse cached initialization stages. |
| `--duration` | Override `t_final`. |
| `--io_cutoff` | Override the input-output cutoff. |
| `--log_level` | Set logging level: `info` or `debug`. |
| `--verbose` | Alias for `--log_level debug`. |
| `--cache_isolation` | Use a process-private cache directory. |
| `--open` | Generate and open the report after simulation. |
| `--version` | Print the package version. |

## Cache Presets

| Preset | Reused Components |
|--------|-------------------|
| `same_transport_network_new_agents` | Transport network only. |
| `same_agents_new_sc_network` | Transport network and agents. |
| `same_sc_network_new_logistic_routes` | Transport network, agents, and supply-chain network. |
| `same_logistic_routes` | Transport network, agents, supply-chain network, and routes. |

## Configuration Files

DisruptSC loads configuration in this order:

1. `config/default.yaml` (shipped)
2. `config/user_defined_<scope>.local.yaml` (optional, gitignored — your personal tweaks)
3. Supported CLI overrides

File paths in the YAML are relative to the scope folder in the resolved data root.

Example:

```yaml
simulation_type: "disruption"
t_final: 12
time_resolution: "week"

filepaths:
  transport: "Transport/transport.gpkg"
  multimodal: "Transport/multimodal.gpkg"
  mrio: "Economic/mrio.csv"
  sector_table: "Economic/sector_table.csv"
  households_spatial: "Spatial/households.geojson"
  firms_spatial: "Spatial/firms.geojson"
  countries_spatial: "Spatial/countries.geojson"
```

## Simulation Types

### `initial_state`

Runs the baseline model without applying a disruption scenario.

### `disruption`

Runs a disruption scenario configured under `disruptions`:

```yaml
simulation_type: "disruption"
disruptions:
  - type: "transport_disruption"
    description_type: "edge_attributes"
    attribute: "name"
    values: ["bridge_1", "road_42"]
    start_time: 1
    duration: 4
```

The legacy key `events` is accepted for backward compatibility, but new
configuration should use `disruptions`.

### `criticality`

Runs infrastructure criticality scenarios configured under `criticality`:

```yaml
simulation_type: "criticality"
criticality:
  duration: 4
  scenarios:
    - name: bridge_1
      edges: ["bridge_1"]
```

## Validation

Use the lightweight validator to check that required configured files exist:

```bash
validate-inputs Testkistan
validate-inputs Cambodia
```

## Output

When `export_files: true`, results are written to:

```text
output/<scope>/<timestamp>/
```

Typical exported files include:

- `parameters.yaml`
- `firm_table.geojson`
- `household_table.geojson`
- `transport_edges_with_flows_*.geojson`
- `summary.csv`
- `exp.log`

## Practical Workflow

```bash
validate-inputs Testkistan
disruptsc Testkistan
disruptsc Testkistan --simulation_type disruption --duration 12
```
