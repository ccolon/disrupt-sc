"""Report which MRIO databases cover which countries as individual regions.

Usage:
    python mrio_coverage.py --countries KAZ,KGZ,TJK,TKM,UZB,RUS,CHN
    python mrio_coverage.py --countries ECU,COL,PER --mrio-root <path>

Sources checked (all on local disk, see tool-recipes.md):
  ICIO       header of the newest ICIO/2025_ed_reg/<year>_SML.csv
  EMERGING-E mrio-extractor/emerging_e_regions.csv
  GLORIA     GLORIA/USD_per_ton.csv (region column)
  FIGARO-REG hardcoded: EU27 (NUTS2 detail) + 16 non-EU countries, year 2013
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import locate  # noqa: E402
from iso_codes import iso3_to_eurostat  # noqa: E402

DEFAULT_MRIO_ROOT = str(locate.mrio_root())

FIGARO_NON_EU = {"US", "CH", "RU", "TR", "CA", "MX", "AR", "BR", "ZA", "AU", "SA", "ID", "CN", "IN", "JP", "KR"}
FIGARO_EU = {  # Eurostat codes; NUTS2 sub-national detail available for these
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL", "HU", "IE",
    "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
}


def icio_regions(mrio_root: str) -> tuple[set[str], list[str]]:
    files = sorted(glob.glob(os.path.join(mrio_root, "ICIO", "2025_ed_reg", "*_SML.csv")))
    if not files:
        return set(), []
    years = [os.path.basename(f).split("_")[0] for f in files]
    with open(files[-1], encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    codes = set()
    for cell in header:
        prefix = cell.split("_", 1)[0].strip().strip('"')
        if re.fullmatch(r"[A-Z]{3}", prefix) and prefix not in {"OUT", "TLS", "ROW"}:
            codes.add(prefix)
    return codes, years


def emerging_regions(mrio_root: str) -> set[str]:
    path = os.path.join(mrio_root, "mrio-extractor", "emerging_e_regions.csv")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {row["code"].strip() for row in csv.DictReader(f) if row.get("code")}


def gloria_regions(mrio_root: str) -> set[str]:
    path = os.path.join(mrio_root, "GLORIA", "USD_per_ton.csv")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {row[0].strip() for row in csv.reader(f) if row and re.fullmatch(r"[A-Z]{3}", row[0].strip())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--countries", required=True, help="comma-separated ISO3 codes")
    ap.add_argument("--mrio-root", default=DEFAULT_MRIO_ROOT)
    args = ap.parse_args()

    countries = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    icio, icio_years = icio_regions(args.mrio_root)
    emerging = emerging_regions(args.mrio_root)
    gloria = gloria_regions(args.mrio_root)

    for name, present in [("ICIO", icio), ("EMERGING-E", emerging), ("GLORIA", gloria)]:
        if not present:
            print(f"WARN: {name} source not found under {args.mrio_root} - column will read 'unknown'")

    header = ["country", "FIGARO-2013", f"ICIO-{icio_years[0]}..{icio_years[-1]}" if icio_years else "ICIO",
              "EMERGING-E-2018", "GLORIA"]
    rows = []
    for c in countries:
        eurostat = iso3_to_eurostat(c)
        if eurostat in FIGARO_EU:
            fig = "internal (NUTS2 detail)"
        elif eurostat in FIGARO_NON_EU:
            fig = "internal"
        else:
            fig = "-"
        rows.append([
            c,
            fig,
            ("internal" if c in icio else "-") if icio else "unknown",
            ("internal" if c in emerging else "-") if emerging else "unknown",
            ("internal" if c in gloria else "-") if gloria else "unknown",
        ])

    widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    for r in [header] + rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(r, widths)))

    print()
    print("Notes: '-' means the country falls into ROW for that database.")
    print("       FIGARO uses Eurostat 2-letter codes natively (alias to ISO3 at extraction).")
    print("       Eora is not supported by mrio-extractor (known issue KI-06).")
    n_missing_everywhere = sum(1 for r in rows if all(v in ("-", "unknown") for v in r[1:]))
    if n_missing_everywhere:
        print(f"WARN: {n_missing_everywhere} countr{'y is' if n_missing_everywhere == 1 else 'ies are'} "
              "not individually covered by any database.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
