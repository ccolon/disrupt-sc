"""Build an Ecuador-sector x Ecuador-sector input-criticality matrix from the
Pichler et al. (2022) IHS Markit survey (WIOD-54 resolution).

Their matrix `crit[i, j]` = criticality of input sector i to producing sector j:
  1   = critical      -> hard Leontief bind (output limited by this input)
  0.5 = important     -> soft floor (a depleted important input halves output)
  0   = non-critical  -> never constrains output

We crosswalk each Ecuador trigram sector to one WIOD-54 industry, then look up
crit[wiod(i), wiod(j)]. Output: `_criticality/criticality.csv` (index = input
trigram, columns = buyer trigram) committed in the code repo (small, derived, so
it travels with git to the cluster), plus `_criticality/crosswalk.csv` (audit).

IMP (imports, RoW) is set NON-CRITICAL: imports are globally sourced, not hit by
the domestic capital shock, and absent from the survey — so imported inputs never
halt a domestic firm. Flip IMP_CRITICALITY below to change that assumption.

Run:  python studies/earthquake/build_criticality.py
      python studies/earthquake/build_criticality.py --pichler /path/to/covid19inputoutput
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

# Pichler replication data (Zenodo 10.5281/zenodo.5881855). Override with --pichler
# or $PICHLER_DIR (the covid19inputoutput root) when running off this machine.
_PICHLER_DEFAULT = Path(os.environ.get(
    "PICHLER_DIR", r"C:\Users\Celian\OneDrive\DisruptSC\covid19inputoutput"))
# criticality.csv lives IN the code repo (small, derived, committed) so it travels
# with git to the cluster. Override with --out-dir.
_OUT_DEFAULT = Path(__file__).resolve().parent / "_criticality"

IMP_CRITICALITY = 0.0  # imports as an input: 0 non-critical / 0.5 important / 1 critical

# Ecuador trigram -> WIOD-54 ISIC code. One WIOD industry per Ecuador sector.
# Judgment calls flagged inline; food subsectors all collapse to C10-C12.
ECU_TO_WIOD = {
    "ADM": "N",        # professional/technical/admin -> admin & support services
    "ADP": "O84",      # public administration & defense
    "AGU": "E36",      # water
    "ALD": "C10-C12",  # diverse food products
    "ASO": "R_S",      # associations/leisure/culture -> other services
    "AYG": "C10-C12",  # vegetable/animal oils & fats (food mfg)
    "AZU": "C10-C12",  # sugar
    "BAL": "C10-C12",  # alcoholic beverages
    "BNA": "C10-C12",  # non-alcoholic beverages
    "CAN": "C10-C12",  # prepared animal feed
    "CAR": "C10-C12",  # meat processing
    "CAU": "C22",      # rubber
    "CEM": "C23",      # cement/concrete/stone (non-metallic minerals)
    "CER": "A01",      # cereals cultivation
    "CHO": "C10-C12",  # cacao/chocolate/confectionery
    "CIN": "A01",      # industrial (oilseed) crops
    "COM": "G46",      # wholesale & retail trade
    "CON": "F",        # construction
    "CUE": "C13-C15",  # leather & footwear
    "CUL": "A01",      # crop support activities
    "DEM": "C25",      # fabricated metal products
    "DOM": "R_S",      # private domestic service (WIOD T absent; ~no inputs)
    "EDU": "P85",      # education
    "ELE": "D35",      # electricity
    "FID": "C10-C12",  # noodles/flour products
    "FIN": "K64",      # finance
    "FRT": "A01",      # banana/coffee/cacao cultivation
    "FRV": "A01",      # fruits & vegetables cultivation
    "GAN": "A01",      # livestock
    "HIL": "C13-C15",  # thread & fabrics (textiles)
    "HOT": "I",        # accommodation
    "INM": "L68",      # real estate
    "LAC": "C10-C12",  # dairy
    "MAD": "C16",      # wood & wood products
    "MAN": "C31_C32",  # other manufacturing n.e.c.
    "MAQ": "C28",      # machinery & equipment
    "MET": "C24",      # basic metals
    "MIP": "B",        # mining (non-metallic) & mining support
    "MOL": "C10-C12",  # grain milling
    "MUE": "C31_C32",  # furniture
    "PAN": "C10-C12",  # bread/baking
    "PAP": "C17",      # paper
    "PES": "A03",      # fishing / shrimp aquaculture
    "PLS": "C22",      # plastics
    "POS": "H53",      # postal & courier
    "PPR": "C10-C12",  # processed fish (food mfg)
    "QU1": "C20",      # basic chemicals & fertilizers
    "QU2": "C20",      # other chemical products
    "REF": "C19",      # refined petroleum
    "REP": "G45",      # motor-vehicle repair (WIOD G45 incl. repair)
    "RES": "I",        # restaurants (food service)
    "SAL": "Q",        # health
    "SEG": "K65",      # insurance
    "SIL": "A02",      # forestry & logging
    "TAB": "C10-C12",  # tobacco (WIOD C10-C12 incl. tobacco)
    "TEL": "J61",      # telecommunications & information
    "TRA": "H49",      # transport & storage (land transport dominant)
    "VES": "C13-C15",  # apparel
    "VID": "C23",      # glass & ceramics (non-metallic minerals)
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pichler", type=Path, default=_PICHLER_DEFAULT,
                    help="covid19inputoutput root (or set $PICHLER_DIR)")
    ap.add_argument("--out-dir", type=Path, default=_OUT_DEFAULT,
                    help="where to write criticality.csv + crosswalk.csv")
    args = ap.parse_args()

    pichler_csv = args.pichler / "data" / "IHS_matrices_processed" / "IHS_Markit_results_compact.csv"
    if not pichler_csv.exists():
        raise SystemExit(f"Pichler matrix not found at {pichler_csv} — pass --pichler <covid19inputoutput root>")

    crit = pd.read_csv(pichler_csv, index_col=0)
    crit.index = crit.index.astype(str)
    crit.columns = crit.columns.astype(str)
    # NA in the survey = not rated = treat as non-critical (0).
    crit = crit.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    wiod_codes = set(crit.index) | set(crit.columns)
    bad = {s: w for s, w in ECU_TO_WIOD.items() if w not in wiod_codes}
    if bad:
        raise SystemExit(f"Crosswalk targets not in Pichler matrix: {bad}")

    ecu = list(ECU_TO_WIOD) + ["IMP"]
    M = pd.DataFrame(0.0, index=ecu, columns=ecu, dtype=float)  # index=input, cols=buyer
    for j in ecu:                       # buyer
        for i in ecu:                   # input
            if i == "IMP" or j == "IMP":
                M.loc[i, j] = IMP_CRITICALITY if i == "IMP" else 0.0
                # a firm's own imports use IMP_CRITICALITY; nobody's output feeds
                # "IMP" production (IMP is a source, not a producer) -> col stays 0
                continue
            M.loc[i, j] = float(crit.loc[ECU_TO_WIOD[i], ECU_TO_WIOD[j]])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "criticality.csv"
    M.to_csv(out)
    pd.Series(ECU_TO_WIOD, name="wiod_isic").rename_axis("ecu_sector").to_csv(
        args.out_dir / "crosswalk.csv")

    # Summary
    vals = M.values
    n = vals.size
    print(f"Wrote {out}  ({M.shape[0]}x{M.shape[1]} sectors incl. IMP)")
    print(f"  critical (1.0):     {(vals == 1.0).sum():5d}  ({100*(vals==1.0).mean():.1f}%)")
    print(f"  important (0.5):    {(vals == 0.5).sum():5d}  ({100*(vals==0.5).mean():.1f}%)")
    print(f"  non-critical (0.0): {(vals == 0.0).sum():5d}  ({100*(vals==0.0).mean():.1f}%)")
    frac_bind = (vals >= 0.5).mean()
    print(f"  share of cells that bind (>=0.5): {100*frac_bind:.1f}%  "
          f"(strict Leontief would be ~100% of nonzero tech-coef cells)")


if __name__ == "__main__":
    main()
