# Firm Table GeoJSON Format (Transaction-Based Mode)

## Overview
The `firms.geojson` file defines firms directly for the transaction-based data ingestion mode. Each firm is a geographic point feature with comprehensive economic and operational attributes.

## File Structure

### GeoJSON Format
```json
{
  "type": "FeatureCollection",
  "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
      "properties": {
        "id": 0,
        "sector": "A0116",
        "final_demand": 10.0,
        "imports": 1.0,
        "exports": 2.0,
        "usd_per_ton": 1000.0,
        "sector_type": "agriculture",
        "margin": 0.2,
        "transport_share": 0.1,
        "adminunit": 20104
      }
    }
  ]
}
```

## Required Attributes

| Attribute | Type | Range/Format | Description |
|-----------|------|--------------|-------------|
| `id` | int | Unique | Firm identifier (must be unique across all firms) |
| `sector` | string | Sector codes | Economic sector classification (e.g., "A0116", "C2211") |
| `final_demand` | float | ≥ 0 | Value of final demand for this firm's output |
| `imports` | float | ≥ 0 | Value of imports by this firm |
| `exports` | float | ≥ 0 | Value of exports by this firm |
| `total_output` | float | > 0 | Total output value (used for input mix calculation) |
| `usd_per_ton` | float | > 0 | Unit value conversion factor (USD per ton) |
| `sector_type` | string | Categories | Sector type (agriculture, manufacturing, service, etc.) |
| `margin` | float | [0, 1] | Profit margin as proportion of revenue |
| `transport_share` | float | [0, 1] | Share of transport costs in total costs |

## Optional Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `adminunit` | int | Administrative unit code for spatial disaggregation |

## Geometry Requirements

- **Type**: Point geometry required
- **Coordinates**: [longitude, latitude] in EPSG:4326 (WGS84)
- **Bounds**: Longitude [-180, 180], Latitude [-90, 90]
- **Completeness**: All firms must have valid geometry

## Data Validation Rules

### Economic Values
- All economic values (`final_demand`, `imports`, `exports`, `usd_per_ton`) must be non-negative
- `usd_per_ton` must be positive (cannot be zero)

### Proportions
- `margin` and `transport_share` must be between 0 and 1 (inclusive)
- Values outside [0, 1] indicate data errors

### Identifiers
- `id` values must be unique integers
- No duplicate firm IDs allowed
- IDs should be sequential for optimal performance

### Spatial
- All firms must have Point geometry
- Coordinates should be within reasonable geographic bounds
- Missing geometry will cause validation errors

## Usage in Transaction-Based Mode

1. **Direct Firm Creation**: Firms are created directly from this file, not derived from MRIO
2. **Spatial Placement**: Coordinates determine firm locations on transport network
3. **Economic Initialization**: Attributes initialize firm economic state
4. **Transaction Integration**: Firm IDs link to transaction_table.csv for supply relationships

## Comparison to MRIO Mode

| Aspect | MRIO Mode | Transaction Mode |
|--------|-----------|------------------|
| Firm Definition | Generated from MRIO disaggregation | Direct from firms.geojson |
| Spatial Data | Uses separate firms_spatial.geojson | Integrated geometry in firms.geojson |
| Economic Data | Derived from IO coefficients | Explicit firm-level attributes |
| Supply Relationships | Random selection from MRIO | Predefined in transaction_table.csv |

## Example Data

The Ecuador example contains 10 firms across different sectors:
- Agriculture: A0116, A0161, A0220
- Manufacturing: C2211, C2513
- Trade: G4721
- Transport: H4923
- Services: J6130, K6511

Each firm has standardized test values:
- `final_demand`: 10
- `imports`: 1
- `exports`: 2
- `usd_per_ton`: 1000
- `margin`: 0.2
- `transport_share`: 0.1