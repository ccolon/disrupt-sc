# Data Modes

The current v2 runtime supports MRIO-based model construction.

## MRIO Mode

MRIO mode uses multi-regional input-output data, sector metadata, spatial
household data, spatial firm data, and country entry points to create the model.

Configure it with:

```yaml
firm_data_type: "mrio"
```

This is also the default when `firm_data_type` is omitted.

## Required Files

```text
<data-root>/<scope>/
+-- Economic/
    +-- mrio.csv
    +-- sector_table.csv
+-- Spatial/
    +-- households.geojson
    +-- countries.geojson
    +-- firms.geojson
+-- Transport/
    +-- transport.gpkg
```

The exact filenames are configured under `filepaths` in the YAML parameter
files.

## How MRIO Mode Works

1. The MRIO table provides output, input requirements, final demand, and trade flows.
2. The sector table provides sector metadata such as type and transport intensity.
3. Spatial files place firms, households, and countries on the transport network.
4. The model builds synthetic commercial links from technical coefficients and supplier-selection weights.
5. Logistics routes are assigned over the transport network.

## Transaction-Based Mode

Transaction or supplier-buyer network mode is not implemented in the current v2
runtime. If `firm_data_type: "transaction_based"` is used, firm creation raises
`NotImplementedError`.

Keep transaction-specific input files in private data repositories if they are
useful for future development, but do not rely on them for current v2 runs.
