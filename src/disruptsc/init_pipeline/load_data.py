"""Load economic input data: MRIO, sector table, USD per ton."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from disruptsc.network.mrio import Mrio, rescale_monetary_values


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


def load_usd_per_ton(filepath: Path) -> dict:
    """Load USD-per-ton conversion factors. Returns dict keyed by region_sector."""
    if filepath is None or not Path(filepath).exists():
        return {}
    df = pd.read_csv(filepath)
    result = {}
    for _, row in df.iterrows():
        key = f"{row['region']}_{row['sector']}"
        result[key] = row["usd_per_ton"]
    return result


def load_mrio(filepath: Path, monetary_units: str) -> Mrio:
    """Load MRIO from CSV."""
    logging.info(f"Loading MRIO from {filepath}")
    return Mrio.load(filepath, monetary_units=monetary_units)


def filter_sectors(mrio: Mrio,
                   cutoff_sector_output: dict,
                   cutoff_sector_demand: dict,
                   combine: str,
                   sectors_to_include,
                   sectors_to_exclude: tuple,
                   monetary_units_in_data: str) -> list:
    """Filter MRIO industries by output and/or demand cutoffs."""
    # Filter by output
    out_cutoff = cutoff_sector_output
    industries_by_output = mrio.filter_by_output(
        out_cutoff["value"], out_cutoff["type"], out_cutoff.get("unit", "mUSD"), monetary_units_in_data
    )

    # Filter by demand
    dem_cutoff = cutoff_sector_demand
    industries_by_demand = mrio.filter_by_final_demand(
        dem_cutoff["value"], dem_cutoff["type"], dem_cutoff.get("unit", "mUSD"), monetary_units_in_data
    )

    # Combine
    if combine == "and":
        filtered = list(set(industries_by_output) & set(industries_by_demand))
    else:
        filtered = list(set(industries_by_output) | set(industries_by_demand))

    # Apply include/exclude
    if sectors_to_include != "all" and isinstance(sectors_to_include, list):
        filtered = [rs for rs in filtered if rs[1] in sectors_to_include]

    if sectors_to_exclude:
        filtered = [rs for rs in filtered if rs[1] not in sectors_to_exclude]

    logging.info(f"Filtered to {len(filtered)} industries")
    return sorted(filtered, key=lambda x: "_".join(x))
