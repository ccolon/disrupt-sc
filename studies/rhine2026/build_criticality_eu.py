"""Build the EU-scope input-criticality matrix from the IHS Markit survey (Pichler et al. 2022).

The survey (Zenodo 10.5281/zenodo.5881855, CC BY 4.0) rates, for each of 55 WIOD industries
(NACE Rev. 2), whether an input industry is critical (1: output limited by that input, hard
Leontief), important (0.5: a depleted important input halves output) or non-critical (0: never
binds). DisruptSC reads such a matrix through `filepaths.input_criticality` (index = input sector,
columns = buyer sector) and applies it in the partially-binding Leontief production function
(`firm.input_criticality`), which replaces the cost-share proxy `critical_input_threshold`.

The EU scope uses the 50 OECD ICIO 2022 sectors; every ICIO sector maps to exactly one WIOD
industry (both are ISIC Rev. 4 groupings; judgment calls are flagged). Imports carry the sector
of the exporting bloc (e.g. `CHN_C20` -> C20), so an imported chemical is as critical as a
domestic one - the right assumption for an EU-wide scope.

Output: studies/rhine2026/additional_data/input_criticality.csv (committed, derived) and the
crosswalk next to it for audit.

Run:  python studies/rhine2026/build_criticality_eu.py [--pichler <covid19inputoutput root>]
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

_PICHLER_DEFAULT = Path(os.environ.get(
    "PICHLER_DIR", r"C:\Users\Celian\OneDrive\DisruptSC\covid19inputoutput"))
_OUT_DEFAULT = Path(__file__).resolve().parent / "additional_data"
_SECTOR_TABLE = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc-data\EU\Economic\sector_table.csv")

# ICIO 2022 sector code -> WIOD-54 industry (IHS matrix labels). One industry per sector.
ICIO_TO_WIOD = {
    "A01": "A01", "A02": "A02", "A03": "A03",
    "B05": "B", "B06": "B", "B07": "B", "B08": "B", "B09": "B",   # mining sub-sectors -> mining
    "C10T12": "C10-C12", "C13T15": "C13-C15", "C16": "C16",
    "C17_18": "C17",       # paper + printing -> paper (the larger, and the one with physical inputs)
    "C19": "C19", "C20": "C20", "C21": "C21", "C22": "C22", "C23": "C23",
    "C24A": "C24", "C24B": "C24",   # iron & steel / non-ferrous -> basic metals
    "C25": "C25", "C26": "C26", "C27": "C27", "C28": "C28", "C29": "C29",
    "C301": "C30", "C302T309": "C30",   # ships / other transport equipment
    "C31T33": "C31_C32",   # furniture, other manufacturing, repair -> furniture & other mfg
    "D": "D35",
    "E": "E36",            # water supply, sewerage, waste -> water supply (critical utility input)
    "F": "F",
    "G": "G46",            # trade -> wholesale (trade margins are a non-critical input in the survey)
    "H49": "H49", "H50": "H50", "H51": "H51", "H52": "H52", "H53": "H53",
    "I": "I",
    "J58T60": "J58",       # publishing, audiovisual, broadcasting -> publishing
    "J61": "J61", "J62_63": "J62_J63",
    "K": "K64",            # financial & insurance -> financial services
    "L": "L68",
    "M": "M69_M70",        # professional, scientific, technical -> legal, accounting, head offices
    "N": "N", "O": "O84", "P": "P85", "Q": "Q",
    "R": "R_S", "S": "R_S", "T": "T",
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pichler", type=Path, default=_PICHLER_DEFAULT)
    ap.add_argument("--out-dir", type=Path, default=_OUT_DEFAULT)
    ap.add_argument("--sector-table", type=Path, default=_SECTOR_TABLE)
    args = ap.parse_args()

    ihs = pd.read_csv(args.pichler / "data" / "IHS_matrices_processed" / "IHS_Markit_results_compact.csv", index_col=0)
    sectors = sorted(pd.read_csv(args.sector_table)["sector"].unique())
    missing = [s for s in sectors if s not in ICIO_TO_WIOD]
    if missing:
        raise SystemExit(f"no WIOD mapping for sectors: {missing}")
    # T (households as employers) is not rated as a buyer: it has no real inputs -> non-critical.
    unrated = sorted({w for w in ICIO_TO_WIOD.values() if w not in ihs.index or w not in ihs.columns})
    if unrated:
        print(f"WIOD labels not rated on both axes (their pairs set non-critical): {unrated}")

    crit = pd.DataFrame(index=sectors, columns=sectors, dtype=float)
    for i in sectors:            # input sector
        for j in sectors:        # buyer sector
            wi, wj = ICIO_TO_WIOD[i], ICIO_TO_WIOD[j]
            if wi not in ihs.index or wj not in ihs.columns:
                crit.at[i, j] = 0.0
                continue
            v = ihs.at[wi, wj]
            crit.at[i, j] = 1.0 if pd.isna(v) else float(v)   # unrated pair -> critical (conservative)
    crit.index.name = ""

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "input_criticality.csv"
    crit.to_csv(out)
    pd.DataFrame({"icio_sector": list(ICIO_TO_WIOD), "wiod_industry": list(ICIO_TO_WIOD.values())}).to_csv(
        args.out_dir / "wiod_correspondence.csv", index=False)

    vals = crit.values.ravel()
    n = len(vals)
    print(f"{out}: {crit.shape[0]}x{crit.shape[1]} matrix; critical {100*(vals >= 1).mean():.0f} % / "
          f"important {100*((vals >= 0.5) & (vals < 1)).mean():.0f} % / non-critical {100*(vals < 0.5).mean():.0f} % of the {n} cells")
    # the pairs that matter for the Rhine case: chemicals, metals, refining as inputs
    for inp in ("C20", "C24A", "C19", "B05", "H50"):
        row = crit.loc[inp]
        print(f"  input {inp}: critical for {int((row >= 1).sum())} buyer sectors, important for "
              f"{int(((row >= 0.5) & (row < 1)).sum())}, non-critical for {int((row < 0.5).sum())}")


if __name__ == "__main__":
    main()
