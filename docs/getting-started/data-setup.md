# Data Setup

DisruptSC keeps model code and large input datasets separate. The public
repository contains the model code, configuration, documentation, and a small
bundled `Testkistan` dataset for smoke tests and examples. Full country and
regional datasets should live outside the code repository.

## Data Location Priority

DisruptSC resolves data per scope:

1. If `DISRUPT_SC_DATA_PATH` is set, use that data root for all scopes.
2. Otherwise, if the requested scope is `Testkistan`, use the bundled example
   data at `./examples/data/Testkistan`.
3. Otherwise, use the sibling private data repository at `../disrupt-sc-data`.

If `DISRUPT_SC_DATA_PATH` is set but points to a folder that does not exist,
DisruptSC raises a clear error instead of silently falling back to bundled data.

## Recommended Setup: Sibling Data Repository

If you have access to the private data repository, clone it next to
`disrupt-sc`:

```text
DisruptSC/
+-- disrupt-sc/
+-- disrupt-sc-data/
```

```bash
cd DisruptSC
git clone https://github.com/ccolon/disrupt-sc.git
git clone <private-data-repo-url> disrupt-sc-data
cd disrupt-sc
```

With this layout, no environment variable is needed. DisruptSC automatically
uses `../disrupt-sc-data`.

## Custom Data Location

If your data repository is elsewhere, set `DISRUPT_SC_DATA_PATH` to the folder
that contains scope folders such as `Cambodia`, `Ecuador`, or `Testkistan`.

PowerShell:

```powershell
$env:DISRUPT_SC_DATA_PATH = "C:\path\to\disrupt-sc-data"
```

bash/zsh:

```bash
export DISRUPT_SC_DATA_PATH=/path/to/disrupt-sc-data
```

For a persistent user-level setting on Windows:

```powershell
[Environment]::SetEnvironmentVariable(
    "DISRUPT_SC_DATA_PATH",
    "C:\path\to\disrupt-sc-data",
    "User"
)
```

Open a new terminal after setting a persistent environment variable.

## Bundled Test Data

If `DISRUPT_SC_DATA_PATH` is not set, DisruptSC uses
`./examples/data/Testkistan` for the synthetic `Testkistan` dataset.

```bash
python src/disruptsc/run.py Testkistan
```

## Required Data Structure

Input data must be organized by scope inside the resolved data root:

```text
<data-root>/
+-- <scope>/                  # e.g. Cambodia, Ecuador, Testkistan
    +-- Economic/             # MRIO tables, sector definitions, firm data
    +-- Transport/            # Infrastructure GeoPackage files
    +-- Spatial/              # Geographic disaggregation files
    +-- Disruption/           # Optional scenario files
```

The exact filenames are configured in
`config/parameters/user_defined_<scope>.yaml` under `filepaths`.

## Scope Configuration

Each runnable scope needs:

1. A data folder at `<data-root>/<scope>/`.
2. A parameter file at `config/parameters/user_defined_<scope>.yaml`.

For example, with the sibling data repository:

```text
../disrupt-sc-data/Cambodia/
config/parameters/user_defined_Cambodia.yaml
```

## File Requirements

### Essential Files

- `Economic/mrio.csv` - Input-output table.
- `Economic/sector_table.csv` - Sector definitions.
- `Transport/transport.gpkg` - Transport network GeoPackage.
- `Spatial/households.geojson` - Household locations.

### Transport Networks

At minimum, roads are required. Additional transport modes are optional:

- Maritime networks for international shipping.
- Railways for freight transport.
- Airways for high-value goods.
- Waterways for inland navigation.
- Pipelines for energy and chemicals.

### Data Modes

MRIO mode is the default and uses:

- `Economic/mrio.csv`
- `Economic/sector_table.csv`
- `Spatial/*.geojson`

Supplier-buyer network mode additionally uses:

- `Economic/firm_table.csv`
- `Economic/location_table.csv`
- `Economic/transaction_table.csv`

## Verification

Check which data path DisruptSC resolves:

```bash
python -c "from disruptsc.paths import get_data_path; print(get_data_path('Testkistan'))"
```

Then run a smoke test with bundled data:

```bash
python src/disruptsc/run.py Testkistan
```

## Troubleshooting

### Data Path Not Found

Check the resolved data root:

```bash
python -c "from disruptsc.paths import get_data_root; print(get_data_root())"
```

If using `DISRUPT_SC_DATA_PATH`, verify that it points to the data root, not to
an individual scope folder.

PowerShell:

```powershell
echo $env:DISRUPT_SC_DATA_PATH
Test-Path $env:DISRUPT_SC_DATA_PATH
```

bash/zsh:

```bash
echo "$DISRUPT_SC_DATA_PATH"
test -d "$DISRUPT_SC_DATA_PATH"
```

### Missing Scope

If DisruptSC resolves the data root correctly but a scope fails to load, verify
that the scope folder exists:

```bash
ls ../disrupt-sc-data/Cambodia
```

If you are using only the public repository, use `Testkistan` unless you have
provided another dataset.

### Invalid File Formats

- CSV files should use UTF-8 encoding.
- Transport edges must use LineString geometries.
- Spatial agent files must use Point geometries.
- Required columns must match the parameter file references.

## What's Next?

After setting up data:

1. Read the [Quick Start](quick-start.md).
2. Review [Input Validation](validation.md).
3. Customize [Parameters](../user-guide/parameters.md).
