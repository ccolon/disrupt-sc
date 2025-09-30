# Transaction Table CSV Format

## Overview
The `transaction_table.csv` file defines firm-to-firm commercial transactions for the transaction-based data ingestion mode. This file specifies predefined supply chain relationships rather than generating them from MRIO coefficients.

## File Structure

### Required Columns
| Column | Type | Description |
|--------|------|-------------|
| `buyer_firm_id` | int | ID of the purchasing firm (must exist in firms.geojson) |
| `seller_firm_id` | int | ID of the selling firm (must exist in firms.geojson) |
| `transaction_value` | float | Value of transaction in data currency units |

### Optional Columns
| Column | Type | Description |
|--------|------|-------------|
| `import_value` | float | Import value for the buyer firm (if seller is foreign) |
| `export_value` | float | Export value for the seller firm (if buyer is foreign) |
| `sector` | string | Sector code for validation purposes |
| `commodity` | string | Specific commodity being traded |

## Input Mix Calculation Logic

For each firm, the input mix is calculated as:
```
total_output = sum(all transactions where firm is seller) + export_value
total_input = sum(all transactions where firm is buyer) + import_value

input_mix = {
    supplier_firm_id: transaction_value / total_output,
    imports: import_value / total_output
}
```

## Data Validation Rules

1. **Referential Integrity**: All `buyer_firm_id` and `seller_firm_id` must exist in the firms.geojson file
2. **Positive Values**: All transaction values must be positive
3. **Balance Check**: For each firm, total inputs should approximately equal total outputs
4. **No Self-Transactions**: `buyer_firm_id` ≠ `seller_firm_id`

## Example Format

```csv
buyer_firm_id,seller_firm_id,transaction_value,import_value,export_value
0,1,1000.5,0,0
0,2,500.0,0,0
1,3,750.25,0,0
2,imports,300.0,300.0,0
3,exports,450.0,0,450.0
```

## Usage with Firms Data

This format works in conjunction with `Economic/firms.geojson` where:
- Firms are directly defined with their properties (id, sector, location, etc.)
- Transaction table defines the interconnections between these predefined firms
- No MRIO disaggregation is needed - firms and relationships are explicit

### Required Firm Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | int | Unique firm identifier |
| `sector` | string | Sector code (e.g., "A0116", "C2211") |
| `final_demand` | float | Final demand value |
| `imports` | float | Import value |
| `exports` | float | Export value |
| `usd_per_ton` | float | Unit value conversion factor |
| `sector_type` | string | Sector type category |
| `margin` | float | Profit margin (0.0-1.0) |
| `transport_share` | float | Share of transport costs (0.0-1.0) |

## Comparison to MRIO Mode

| Aspect | MRIO Mode | Transaction Mode |
|--------|-----------|------------------|
| Firm Creation | Generated from MRIO disaggregation | Direct from firms.geojson |
| Supply Relationships | Random selection from coefficients | Predefined in transaction_table.csv |
| Input Mix | Derived from MRIO technical coefficients | Calculated from actual transactions |
| Data Size | Compact (MRIO matrix) | Potentially large (all transactions) |