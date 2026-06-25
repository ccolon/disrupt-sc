"""Generate the macroMIP space + sector remapping CSVs for the DisruptSC submission.

The MacroMIP harmonizer (resultsProcessing/process_generic.py) renames our
columns via mappings-DisruptSC.yaml, then remaps the Region/Sector values to the
common macroMIP taxonomy using these CSVs (with aggregation to EU27 / mid-level
sectors / whole-economy). This builds them from the macroMIP scope sector table.

    python runs/macromip/submission/build_mappings.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from disruptsc import paths  # noqa: E402

SCOPE = "macroMIP"
OUT = Path(__file__).resolve().parent
SECTOR_TABLE = (paths.get_data_path(SCOPE) / "Economic"
                / "mrio_oecd_2017_all_countries_all_sectors_sector_table.csv")

EU27 = {"AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA",
        "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD",
        "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"}

# OECD ICIO (ISIC rev.4) code -> (harmonized fine sector "to", mid-level "aggregate_to").
# Mid-level groups follow the labels in mappings_sectors_combined.csv.
SECTOR_MAP: dict[str, tuple[str, str]] = {
    "A01": ("agriculture - crops", "Agriculture"),
    "A02": ("agriculture - forestry and fishing", "Agriculture"),
    "A03": ("agriculture - forestry and fishing", "Agriculture"),
    "B05": ("energy - coal", "Mining"),
    "B06": ("energy - crude oil and gas", "Mining"),
    "B07": ("mining", "Mining"),
    "B08": ("mining", "Mining"),
    "B09": ("mining", "Mining"),
    "C10T12": ("food processing", "Food processing"),
    "C19": ("energy - petroleum products", "Manufacturing"),
    "D": ("utilities - electricity", "Utilities"),
    "E": ("utilities - water", "Utilities"),
    "F": ("construction", "Construction"),
    "G": ("trade", "Trade and services"),
    "H49": ("transport", "Transport"),
    "H50": ("transport", "Transport"),
    "H51": ("transport", "Transport"),
    "H52": ("transport", "Transport"),
    "H53": ("transport", "Transport"),
    "I": ("accommodation and food services", "Trade and services"),
    "K": ("finance and real estate", "Trade and services"),
    "L": ("finance and real estate", "Trade and services"),
    "O": ("public services", "Public services"),
    "P": ("public services - education", "Public services"),
    "Q": ("public services - health", "Public services"),
}


def map_sector(code: str) -> tuple[str, str]:
    if code in SECTOR_MAP:
        return SECTOR_MAP[code]
    if code.startswith("C"):                       # all other manufacturing
        return ("manufacturing", "Manufacturing")
    if code.startswith("J"):                       # info & communication
        return ("information and communication", "Trade and services")
    if code in ("M", "N", "R", "S", "T"):          # business / other services
        return ("other services", "Trade and services")
    return ("other services", "Trade and services")


def main():
    st = pd.read_csv(SECTOR_TABLE)

    # --- space: ISO3 country -> itself, with EU27 aggregate ---
    space = pd.DataFrame({"from": sorted(st["region"].unique())})
    space["to"] = space["from"]                                   # already ISO-3166 alpha-3
    space["aggregate_to"] = space["from"].map(lambda r: "EU27" if r in EU27 else "")
    space.to_csv(OUT / "mappings-DisruptSC-space.csv", index=False)

    # --- sector: OECD code -> harmonized 'to' + mid-level 'aggregate_to' ---
    sectors = sorted(st["sector"].unique())
    rows = [{"from": s, "to": map_sector(s)[0], "aggregate_to": map_sector(s)[1]}
            for s in sectors]
    # whole-economy row: the adapter emits Sector="TOTAL" carrying the
    # country-level variables (GDP, trade, CPI, PPI) that cannot be summed from
    # sectors. Map it straight to "whole economy" (no double-count with sectors).
    rows.append({"from": "TOTAL", "to": "whole economy", "aggregate_to": "Whole economy"})
    pd.DataFrame(rows).to_csv(OUT / "mappings-DisruptSC-sector.csv", index=False)

    print(f"Wrote {OUT/'mappings-DisruptSC-space.csv'} ({len(space)} regions)")
    print(f"Wrote {OUT/'mappings-DisruptSC-sector.csv'} ({len(rows)} sector rows)")


if __name__ == "__main__":
    main()
