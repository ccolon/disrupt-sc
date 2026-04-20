# Input Validation

The v2 validator checks that the configured scope exists and that required
input files referenced by the YAML configuration are present.

## Run Validation

```bash
validate-inputs <scope>
```

Examples:

```bash
validate-inputs Testkistan
validate-inputs Cambodia
```

The command reports:

- resolved data root
- resolved scope data folder
- missing required files

## Required Files

The validator currently checks these required filepaths:

- `mrio`
- `sector_table`
- `households_spatial`
- `countries_spatial`
- `firms_spatial`
- `transport`, when `with_transport: true`

These keys are configured under `filepaths` in:

```text
config/default.yaml
config/user_defined_<scope>.yaml
config/user_defined_<scope>.local.yaml
```

## Data Path Problems

Check what path DisruptSC resolves:

```bash
python -c "from disruptsc.paths import get_data_path; print(get_data_path('Testkistan'))"
```

For `Testkistan`, this should normally point to:

```text
examples/data/Testkistan
```

For private scopes, it should point to either `DISRUPT_SC_DATA_PATH/<scope>` or
`../disrupt-sc-data/<scope>`.

## Validation Scope

This validator is intentionally lightweight. It does not currently perform full
schema, geometry, MRIO balance, or network-connectivity checks.
