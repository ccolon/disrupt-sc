"""Load economic input data: MRIO, sector table, USD per ton."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from disruptsc.network.mrio import Mrio, Selection, rescale_monetary_values


def load_sector_table(filepath: Path) -> pd.DataFrame:
    """Load sector table with columns: region, sector, type."""
    if filepath is None:
        return None
    table = pd.read_csv(filepath)
    # Standardize columns
    for col in ("region", "sector", "type"):
        if col not in table.columns:
            raise ValueError(f"Sector table missing column: {col}")
    if "region_sector" not in table.columns:
        table["region_sector"] = table["region"] + "_" + table["sector"]
    return table


def load_usd_per_ton(sector_table: pd.DataFrame) -> dict:
    """Extract USD-per-ton from sector_table. Returns dict keyed by region_sector."""
    if sector_table is None or "usd_per_ton" not in sector_table.columns:
        return {}
    sub = sector_table.dropna(subset=["usd_per_ton"])
    return dict(zip(sub["region_sector"], sub["usd_per_ton"]))


def load_mrio(filepath: Path, monetary_units: str) -> Mrio:
    """Load MRIO from CSV."""
    logging.info(f"Loading MRIO from {filepath}")
    return Mrio.load(filepath, monetary_units=monetary_units)


def filter_sectors(mrio: Mrio,
                   flow_coverage: float,
                   sectors_to_include,
                   sectors_to_exclude: tuple) -> Selection:
    """Compute the agent + cell selection from the MRIO via flow coverage.

    A single quantile-style knob (`flow_coverage` ∈ (0, 1]) decides which
    region_sectors, external countries, and bilateral cells survive.
    The rule is symmetric: per-buyer top inputs and per-supplier top
    buyers are unioned (see ``Mrio.filter_by_flow_coverage``).

    `sectors_to_include` / `sectors_to_exclude` are then applied as
    explicit overrides on the kept region_sectors, and the kept cells
    are restricted to whatever remains.
    """
    selection = mrio.filter_by_flow_coverage(flow_coverage)

    # Apply explicit include/exclude overrides on kept region_sectors
    include_active = (sectors_to_include != "all"
                      and isinstance(sectors_to_include, (list, tuple)))
    if not include_active and not sectors_to_exclude:
        return selection

    def _sector_ok(rs):
        if include_active and rs[1] not in sectors_to_include:
            return False
        if sectors_to_exclude and rs[1] in sectors_to_exclude:
            return False
        return True

    kept_rs = tuple(rs for rs in selection.region_sectors if _sector_ok(rs))
    kept_rs_set = set(kept_rs)
    # Drop cells whose model-side endpoint is no longer kept. External
    # buyer/seller endpoints are always retained.
    kept_cells = frozenset(
        (row, col) for (row, col) in selection.kept_cells
        if (row not in set(mrio.region_sectors) or row in kept_rs_set)
        and (col not in set(mrio.region_sectors) or col in kept_rs_set)
    )

    # Re-derive kept external countries after the include/exclude filter
    cols_present = {col for (_, col) in kept_cells}
    rows_present = {row for (row, _) in kept_cells}
    kept_ext_buying = tuple(
        c for c in selection.external_buying_countries
        if any(col[0] == c and col[1] == mrio.export_label for col in cols_present)
    )
    kept_ext_selling = tuple(
        c for c in selection.external_selling_countries
        if any(row[0] == c for row in rows_present)
    )

    dropped_rs = len(selection.region_sectors) - len(kept_rs)
    if dropped_rs:
        logging.info(
            f"sectors_to_include/exclude dropped {dropped_rs} region_sectors "
            f"and {len(selection.kept_cells) - len(kept_cells)} cells"
        )

    return Selection(
        flow_coverage=selection.flow_coverage,
        region_sectors=kept_rs,
        external_buying_countries=kept_ext_buying,
        external_selling_countries=kept_ext_selling,
        kept_cells=kept_cells,
    )
