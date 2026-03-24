# MRIO File Specification for DisruptSC

This document specifies how to build the `mrio.csv` file consumed by the DisruptSC model. It is intended for both human and AI readers.

## Overview

The MRIO (Multi-Regional Input-Output) table describes monetary flows between economic sectors across regions. In DisruptSC, it serves three purposes:

1. **Firm creation**: Each (region, sector) pair in the intermediary matrix becomes a firm agent.
2. **Supply chain construction**: Technical coefficients derived from the intermediary matrix determine supplier-buyer relationships.
3. **External trade**: Import rows and Export columns define how external trade partners (Country agents) interact with domestic firms.

## Architecture: Internal vs External Regions

The MRIO distinguishes two types of regions:

- **Internal regions**: Fully modeled with firms, households, and transport networks. They appear in the **intermediary matrix** (both rows and columns) and in **final_demand** columns.
- **External regions** (countries/trade blocs): Modeled as Country agents that import from and export to internal firms. They appear only in **Imports** rows and **Exports** columns.

This separation is fundamental. A region cannot be both internal and external.

## CSV Structure

The file is read with `pd.read_csv(filepath, header=[0, 1], index_col=[0, 1])`, producing a DataFrame with 2-level MultiIndex for both rows and columns.

### Header (first 2 rows of CSV)

```
row 1 (level 0): region codes    →  ARE, ARE, ..., SAU, SAU, ..., IND, EUR, ..., ARE, SAU, ...
row 2 (level 1): sector names    →  Agriculture, Construction, ..., Agriculture, ..., Exports, Exports, ..., final_demand, final_demand, ...
```

### Index (first 2 columns of CSV)

```
col 1 (level 0): region codes    →  ARE, ARE, ..., SAU, ..., IND, EUR, ...
col 2 (level 1): sector names    →  Agriculture, Construction, ..., ..., Imports, Imports, ...
```

### Matrix Layout

```
                          ┌─────────────────────────┬──────────────┬────────────────┐
                          │   Internal Sectors       │   Exports    │  final_demand  │
                          │  (region, sector) cols   │  (ext, Exp)  │  (int, fd)     │
┌─────────────────────────┼─────────────────────────┼──────────────┼────────────────┤
│ Internal Sectors        │                         │              │                │
│ (region, sector) rows   │   INTERMEDIARY MATRIX   │  EXPORT cols │  FINAL DEMAND  │
│                         │   (must be square)      │              │                │
├─────────────────────────┼─────────────────────────┼──────────────┼────────────────┤
│ Imports                 │                         │              │                │
│ (ext_region, Imports)   │   IMPORT ROWS           │  TRANSIT     │   (ignored)    │
├─────────────────────────┼─────────────────────────┼──────────────┼────────────────┤
│ value_added (optional)  │   VALUE ADDED           │              │                │
├─────────────────────────┼─────────────────────────┼──────────────┼────────────────┤
│ tax (optional)          │   TAX                   │              │                │
└─────────────────────────┴─────────────────────────┴──────────────┴────────────────┘
```

## Label Detection (Critical)

The model auto-detects special row/column labels using **case-insensitive regex** on the level-1 index/column values. The first match is used.

| Label | Axis | Regex Pattern | Typical Value |
|-------|------|---------------|---------------|
| `export_label` | columns (axis=1) | `export` | `Exports` |
| `final_demand_label` | columns (axis=1) | `final.?demand` | `final_demand` |
| `capital_label` | columns (axis=1) | `capital` | `capital` |
| `import_label` | rows (axis=0) | `import` | `Imports` |
| `value_added_label` | rows (axis=0) | `value.?added\|va` | `value_added` |
| `tax_label` | rows (axis=0) | `tax` | `tax` |

### Naming Pitfalls

Because regex matching is greedy and case-insensitive, sector names must **not** accidentally match these patterns:

| Problematic Name | Matches | Fix |
|---|---|---|
| `Re-export & Re-import` | matches `export` AND `import` | Rename to `Others` |
| `Private Households` | matches `va` (in "Pri**va**te") | Rename to `Households` |
| `Taxes on products` | matches `tax` | Rename to `Product levies` |
| `Value chains` | matches `value.?added\|va` | Rename to `Supply chains` |
| `Excavation` | matches `va` | Safe (the `va` pattern requires word boundary in practice, but be cautious) |

**Rule of thumb**: No sector name should contain the substrings `export`, `import`, `tax`, `va`, `capital`, or `final demand` (case-insensitive).

### Missing Labels

| Label | If Missing | Impact |
|-------|-----------|--------|
| `Exports` | `external_buying_countries = []` | No Country agents created as buyers. Model may still run if there are selling countries. |
| `final_demand` | `region_households = []` | No household demand. Model will fail. |
| `Imports` | `external_selling_countries = []` | No Country agents created as sellers. |
| `value_added` | Defaults to **20% margin** for all industries | Acceptable approximation. |
| `tax` | Ignored | No impact. |
| `capital` | Ignored | No impact. |

## Required Sections

### 1. Intermediary Matrix (required)

- **Rows**: `(internal_region, sector)` tuples
- **Columns**: Same `(internal_region, sector)` tuples, in the same order
- **Must be square**: The set of (region, sector) pairs in rows must exactly equal the set in columns
- **Values**: Monetary flows in the unit specified by `monetary_units_in_data` in the YAML config (typically `mUSD` or `USD` per year)
- **No negative values**

### 2. Final Demand Columns (required)

- **Column level-0**: Internal region code (one per internal region)
- **Column level-1**: Must match the `final_demand` regex (use `final_demand`)
- **Rows**: Same as intermediary matrix rows
- **Values**: Household consumption per (region, sector)

### 3. Export Columns (required for external trade)

- **Column level-0**: External region/bloc code (e.g., `EUR`, `CHN`, `AFR`)
- **Column level-1**: Must match the `export` regex (use `Exports`)
- **Rows**: Same as intermediary matrix rows
- **Values**: Total exports from each internal (region, sector) to each external bloc
- **These define `external_buying_countries`**: Each unique level-0 value in Export columns becomes a Country agent that buys from internal firms

### 4. Import Rows (required for external trade)

- **Row level-0**: External region/bloc code (must match the ones used in Export columns if the same bloc both sells and buys)
- **Row level-1**: Must match the `import` regex (use `Imports`)
- **Columns**: Same as intermediary matrix columns
- **Values**: Total imports from each external bloc to each internal (region, sector)
- **These define `external_selling_countries`**: Each unique level-0 value in Import rows becomes a Country agent that sells to internal firms

### 5. Transit Submatrix (derived)

- Located at the intersection of Import rows and Export columns
- Represents goods that pass through the modeled region (imported then re-exported)
- Can be zero if transit trade is not relevant

### 6. Value Added Row (optional)

- **Row level-0**: Empty string or `NaN`
- **Row level-1**: Must match `value.?added|va` (use `value_added`)
- **Values**: Value added per (region, sector)
- Used to compute **profit margins** (value_added / total_output)
- If missing: all industries default to 20% margin

### 7. Tax Row (optional)

- Same structure as value_added
- Currently unused by the model

## Minimal Working Example

A minimal MRIO with 2 internal regions (A, B), 2 sectors (Agri, Mfg), and 1 external bloc (EXT):

```csv
,,A,A,B,B,EXT,A,B
,,Agri,Mfg,Agri,Mfg,Exports,final_demand,final_demand
A,Agri,10,20,5,3,8,50,2
A,Mfg,5,15,2,10,12,30,5
B,Agri,3,1,8,15,4,1,40
B,Mfg,2,8,6,12,6,3,25
EXT,Imports,7,4,3,2,0,0,0
```

This produces:
- 4 firms: A_Agri, A_Mfg, B_Agri, B_Mfg
- 2 households: A, B (from final_demand)
- 1 country: EXT (appears in both Exports and Imports)

## Building from Eora26

When extracting from the Eora26 MRIO database (190 countries, 26 sectors):

### Step 1: Define internal and external regions

```python
INTERNAL = ['ARE', 'SAU', 'QAT', 'KWT', 'BHR', 'OMN', 'IRQ']
EXTERNAL = ['IND', 'PAK', 'EAS', 'EUR', 'AFR', 'ROW']
```

Some external blocs may be aggregations of multiple Eora countries (e.g., `EUR` = all EU countries, `EAS` = East/Southeast Asian countries, `AFR` = African countries).

### Step 2: Extract the intermediary matrix

Select only rows and columns where both region and sector belong to internal regions. Exclude Eora's special sectors:
- `Private Households` (rename to `Households` or exclude)
- `Re-export & Re-import` (rename to `Others` or exclude)
- `Others` (can be kept or excluded)

### Step 3: Build final_demand columns

For each internal region, sum the household/final demand columns from Eora.

### Step 4: Build Exports columns

For each external bloc, sum ALL purchases by that bloc from internal sectors:
- Sum across all sectors of the external bloc in the original Eora intermediary
- Optionally include the external bloc's final demand from internal sectors

This gives one `Exports` column per external bloc.

### Step 5: Build Imports rows

For each external bloc, sum ALL sales by that bloc to internal sectors:
- Sum across all sectors of the external bloc in the original Eora intermediary

This gives one `Imports` row per external bloc.

### Step 6: Rename problematic sectors

Apply the renaming rules from the "Naming Pitfalls" section above.

### Step 7: Validate

1. Intermediary matrix is square
2. No negative values
3. Row sums (total output) approximately equal column sums (total input) for each (region, sector)
4. No sector name accidentally matches the regex patterns

## Companion Files

### sector_table.csv

One row per (region, sector) pair that appears in the intermediary matrix.

Required columns:
- `region_sector`: String `"{region}_{sector}"` (e.g., `ARE_Agriculture`)
- `sector`: Sector name (e.g., `Agriculture`)
- `type`: Sector type, one of: `agriculture`, `mining`, `manufacturing`, `transport`, `trade`, `service`, `utility`, `construction`
- `region`: Region code (e.g., `ARE`)
- `share_exporting_firms`: Float 0-1, share of firms that export
- `usd_per_ton`: Float, monetary value per physical ton (used for logistics costing)

The `sector` to `type` mapping must be consistent across all regions (same sector name always maps to the same type).

### usd_per_ton.csv

Required columns: `region`, `sector`, `usd_per_ton`

One row per (region, sector). Values represent the average USD value per metric ton of output for that sector in that region.

## Configuration (YAML)

```yaml
filepaths:
  mrio: "Economic/mrio.csv"
  sector_table: "Economic/sector_table.csv"
  usd_per_ton: "Economic/usd_per_ton.csv"

monetary_units_in_data: "mUSD"   # or "USD", "kUSD"
```

The `monetary_units_in_data` parameter tells the model what unit the MRIO values are in. Eora26 uses millions of USD (`mUSD`). The model internally converts to the appropriate time resolution.

## Validation Checklist

- [ ] CSV loads correctly with `pd.read_csv(path, header=[0,1], index_col=[0,1])`
- [ ] Intermediary matrix is square (same region-sectors in rows and columns)
- [ ] No sector name matches `export`, `import`, `va`, `tax`, `capital`, or `final.?demand` patterns
- [ ] `Exports` column label detected correctly
- [ ] `final_demand` column label detected correctly
- [ ] `Imports` row label detected correctly
- [ ] All values are non-negative
- [ ] Each Export column level-0 region has a matching entry in `countries.geojson`
- [ ] Each Import row level-0 region has a matching entry in `countries.geojson`
- [ ] Each internal region has a `final_demand` column
- [ ] `monetary_units_in_data` in YAML matches actual units in the CSV
- [ ] `sector_table.csv` covers all (region, sector) pairs in the intermediary matrix
- [ ] `usd_per_ton.csv` covers all (region, sector) pairs in the intermediary matrix
