# Input Validation

The validator checks a scope's configuration and input files **before** a
run — both that they exist and that their content is usable.

## Run Validation

```bash
validate-inputs <scope>
```

Examples:

```bash
validate-inputs Testkistan
validate-inputs Cambodia
```

The command reports the resolved data root and scope folder, then:

- **Config**: the YAML builds valid parameters (bad `capacity_constraint`,
  `rationing_mode`, `flow_coverage`, monetary units, or `time_resolution`
  surface here);
- **Sector table**: required columns (`region`, `sector`, `type`), duplicate
  rows, positive `usd_per_ton` values;
- **MRIO**: parses with a square intermediate block, detects its import /
  export / final-demand labels, reports negative cells and region-sectors
  with input > output (which the model silently balances by padding exports);
- **Spatial files**: required columns, Point geometry (nearest-node
  assignment needs points), household regions intersect the MRIO, and every
  MRIO country appears in `countries_spatial` or `countries_no_transport`;
- **Transport**: the GeoPackage has a layer per configured mode, with a
  LineString geometry spot-check;
- **Disruptions**: known types and resolvable shock files (`repo:` paths
  included), plus the input-criticality matrix when configured.

Errors mean a run would fail or silently mis-build; warnings are suspicious
but survivable. Checks are independent — one broken file does not hide the
others.

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
