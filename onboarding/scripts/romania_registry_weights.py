# -*- coding: utf-8 -*-
"""Business-registry county weights for the Romania firm layer (Deliverable 3).

Input: RO-infra-2023.dta (426,914 firms, county of legal seat, NACE-4,
employment, 2023 sales; see data_profile_RO-infra-2023.md).

DECISIONS (autonomous session 24 Sep 2026 - user to review):
  D1. Registry replaces the Eurostat-NUTS3/population proxies ONLY for
      sectors that are (a) proxied today and (b) dispersed/single-seat
      dominated, where legal-seat county ~ activity county:
        sales-weighted:      B09, C10T12, C13T15, C16, C17_18, C21, C22,
                             C25, C26, C27, C28, C302T309, C31T33, E
        employment-weighted: H49, H50, H51, H52, H53, I, J58T60, J61,
                             J62_63, M, N, R, S
      The profile's cross-check motivates this: the biggest model-vs-
      registry disagreements are exactly C10T12 (0.29), C22 (0.51),
      C27 (0.59) - proxy-weak sectors; while D (0.13), B06 (-0.31),
      C23 (-0.05) show the registry's HQ-booking failure -> facility
      layers KEPT for A01-A03, B05-B08, C19, C20, C23, C24A/B, C29,
      C301, D. F/G/K/L/O/P/Q/T stay on Eurostat/population (chain
      retail, finance, real-estate holdings and the public sector book
      at HQ; the registry barely covers O-Q).
  D2. A01 stays on MapSPAM although the profile flags corr 0.60: freight
      originates at fields/silos, not at agri-holding seats.
  D3. Weight variable: SALES for goods-producing sectors (closer to
      output; missing sales = 8.8% of firms but 2.5% of employment,
      treated as zero contribution), EMPLOYMENT for services (sales
      HQ-book worse there and double-count margins).
  D4. Brasov <-> Braila labels are transposed in the source (profile
      flag #1, verified on known HQs) - swapped back here FIRST.
  D5. The 3 records with >1,000 employees and no sales (one 19,216-emp
      construction SRL) are dropped before employment weighting.
  D6. Registry year is 2023 vs MRIO 2022: only within-sector county
      SHARES are used, so the vintage mismatch is second-order.

Output: Spatial/sources/registry_county_2023.csv (admin_name,sector,value)
        + a trimmed Eurostat copy without the switched sectors (the
        regional_stats adapter concatenates its CSVs without dedup).
Run in dsc env: python romania_registry_weights.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

DTA = Path(r"C:\Users\Celian\OneDrive\WorldBank\Romania\Data\BusinessRegistry\RO-infra-2023.dta")
SRC = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc-data\Romania\Spatial\sources")
OUT = SRC / "registry_county_2023.csv"
EUROSTAT = SRC / "employment_nuts3_2022.csv"
EUROSTAT_TRIM = SRC / "employment_nuts3_2022_nonregistry.csv"

SALES_SECTORS = ["B09", "C10T12", "C13T15", "C16", "C17_18", "C21", "C22",
                 "C25", "C26", "C27", "C28", "C302T309", "C31T33", "E"]
EMP_SECTORS = ["H49", "H50", "H51", "H52", "H53", "I", "J58T60", "J61",
               "J62_63", "M", "N", "R", "S"]


def sector_of(nace: int) -> str | None:
    d = nace // 100
    if d == 9:
        return "B09"
    if 10 <= d <= 12:
        return "C10T12"
    if 13 <= d <= 15:
        return "C13T15"
    if d == 16:
        return "C16"
    if d in (17, 18):
        return "C17_18"
    if d == 21:
        return "C21"
    if d == 22:
        return "C22"
    if d == 25:
        return "C25"
    if d == 26:
        return "C26"
    if d == 27:
        return "C27"
    if d == 28:
        return "C28"
    if d == 30 and nace not in (3011, 3012):
        return "C302T309"
    if 31 <= d <= 33:
        return "C31T33"
    if 36 <= d <= 39:
        return "E"
    if d == 49:
        return "H49"
    if d == 50:
        return "H50"
    if d == 51:
        return "H51"
    if d == 52:
        return "H52"
    if d == 53:
        return "H53"
    if d in (55, 56):
        return "I"
    if 58 <= d <= 60:
        return "J58T60"
    if d == 61:
        return "J61"
    if d in (62, 63):
        return "J62_63"
    if 69 <= d <= 75:
        return "M"
    if 77 <= d <= 82:
        return "N"
    if 90 <= d <= 93:
        return "R"
    if 94 <= d <= 96:
        return "S"
    return None


def main() -> int:
    df = pd.read_stata(DTA)

    # D4: Brasov <-> Braila transposition fix (code AND label are swapped
    # consistently, so swapping the labels back restores the truth)
    swap = {"Braila": "Brasov", "Brasov": "Braila"}
    n_sw = int(df["nuts3_desc"].isin(swap).sum())
    df["county"] = df["nuts3_desc"].replace(swap)
    print(f"D4 swap applied to {n_sw} rows (Brasov<->Braila)")

    # D5: bogus large-employment records
    bogus = df[(df["emp"] > 1000) & (df["sales"].isna())]
    print(f"D5 dropping {len(bogus)} records "
          f"(max emp {bogus['emp'].max() if len(bogus) else 0})")
    df = df.drop(index=bogus.index)

    df["sector"] = [sector_of(int(n)) for n in df["nace4d_num"]]
    df = df.dropna(subset=["sector"])

    rows = []
    for sec in SALES_SECTORS:
        g = df[df["sector"] == sec].groupby("county")["sales"].sum() / 1e6
        for county, v in g.items():
            if v > 0:
                rows.append((county, sec, round(v, 3)))
    for sec in EMP_SECTORS:
        g = df[df["sector"] == sec].groupby("county")["emp"].sum()
        for county, v in g.items():
            if v > 0:
                rows.append((county, sec, int(v)))
    out = pd.DataFrame(rows, columns=["admin_name", "sector", "value"])
    out.to_csv(OUT, index=False)
    ns = out.groupby("sector")["admin_name"].nunique()
    print(f"registry CSV: {len(out)} rows, {ns.index.size} sectors, "
          f"counties per sector min {ns.min()} / max {ns.max()}")
    print(f"written {OUT}")

    # trimmed Eurostat copy: drop the switched sectors (adapter concatenates)
    eu = pd.read_csv(EUROSTAT)
    keep = ~eu["sector"].isin(SALES_SECTORS + EMP_SECTORS)
    eu[keep].to_csv(EUROSTAT_TRIM, index=False)
    print(f"Eurostat trimmed: {len(eu)} -> {int(keep.sum())} rows "
          f"({EUROSTAT_TRIM.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
