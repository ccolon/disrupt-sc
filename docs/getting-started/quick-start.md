# Quick Start

This page uses the bundled `Testkistan` dataset so it works without access to
the private data repository.

## Prerequisites

- Install DisruptSC with `pip install -e .`.
- Activate the environment, for example `conda activate dsc`.
- Leave `DISRUPT_SC_DATA_PATH` unset if you want to use bundled `Testkistan`.

## 1. Validate Inputs

```bash
validate-inputs Testkistan
```

The validator checks that the configured scope folder and required files exist.

## 2. Run A Baseline Simulation

```bash
disruptsc Testkistan
```

The default `Testkistan` configuration runs the simulation type configured in
`config/user_defined_Testkistan.yaml`.

## 3. Override Runtime Options

```bash
# Run a disruption scenario
disruptsc Testkistan --simulation_type disruption

# Override duration and input coverage
disruptsc Testkistan --duration 12 --input_coverage 0.95

# Reuse all cached initialization stages
disruptsc Testkistan --cache same_logistic_routes

# Show all CLI options
disruptsc Testkistan --help
```

## 4. Configure A Disruption

Disruptions are configured in the scope YAML file:

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

Use `disruptions`, not `events`, for new configuration. The legacy `events`
key is still accepted for compatibility.

## 5. Check Outputs

If `export_files: true`, results are saved under:

```text
output/<scope>/<timestamp>/
```

Useful outputs include:

- `parameters.yaml` - resolved configuration snapshot.
- `firm_table.geojson` - firm locations and attributes.
- `household_table.geojson` - household locations and attributes.
- `transport_edges_with_flows_*.geojson` - transport flows.
- `summary.csv` - aggregate loss summary when available.

## Full Data Scopes

For scopes such as `Cambodia`, `Ecuador`, or `Gulf`, clone the private data repo
as a sibling folder:

```text
DisruptSC/
+-- disrupt-sc/
+-- disrupt-sc-data/
```

Then run:

```bash
validate-inputs Cambodia
disruptsc Cambodia
```
