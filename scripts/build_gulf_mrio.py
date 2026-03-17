"""
Extract a Gulf-focused MRIO from the Eora26 Global1 MRIO.

Internal countries (kept individual): ARE, SAU, QAT, KWT, BHR, OMN, IRQ
External countries aggregated into trade blocs:
  - IND (India - major food exporter to Gulf)
  - PAK (Pakistan - food/labor)
  - EAS (East Asia - CHN, JPN, KOR, TWN, SGP, etc. - manufactured goods)
  - EUR (Europe - processed food, machinery)
  - AFR (Africa - some food)
  - ROW (Rest of World - Americas, Oceania, others)

Output: data/Gulf/Economic/mrio.csv  +  sector_table.csv  +  usd_per_ton.csv
"""

import pandas as pd
import numpy as np
import pathlib
import sys

# ── Paths ──
REPO = pathlib.Path(__file__).resolve().parent.parent
# Global1 data lives in the main repo, not the worktree
MAIN_REPO = pathlib.Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc")
GLOBAL1 = MAIN_REPO / "data" / "Global1" / "Network"
OUT_DIR = REPO / "data" / "Gulf" / "Economic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Country groupings ──
GULF = ["ARE", "SAU", "QAT", "KWT", "BHR", "OMN", "IRQ"]

EUR = [
    "AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA",
    "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD",
    "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE",
    "GBR", "CHE", "NOR", "ISL", "SRB", "BIH", "MKD", "MNE", "ALB",
    "UKR", "MDA", "BLR", "RUS",
    "LIE", "MCO", "SMR", "AND",
]

EAS = [
    "CHN", "JPN", "KOR", "TWN", "SGP", "THA", "MYS", "IDN", "VNM", "PHL",
    "KHM", "LAO", "MMR", "BRN", "HKG", "MAC", "MNG", "PRK",
]

AFR = [
    "DZA", "AGO", "BEN", "BWA", "BFA", "BDI", "CMR", "CPV", "CAF",
    "TCD", "COG", "COD", "CIV", "DJI", "EGY", "ERI", "ETH", "GAB",
    "GMB", "GHA", "GIN", "KEN", "LSO", "LBR", "LBY", "MDG", "MWI",
    "MLI", "MRT", "MUS", "MAR", "MOZ", "NAM", "NER", "NGA", "RWA",
    "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SDS", "SUD", "SWZ",
    "TZA", "TGO", "TUN", "UGA", "ZMB", "ZWE",
    "NCL",
]

# Build mapping: ISO3 -> bloc name
BLOC_MAP = {}
for c in GULF:
    BLOC_MAP[c] = c  # keep individual
BLOC_MAP["IND"] = "IND"
BLOC_MAP["PAK"] = "PAK"
for c in EUR:
    BLOC_MAP[c] = "EUR"
for c in EAS:
    BLOC_MAP[c] = "EAS"
for c in AFR:
    BLOC_MAP[c] = "AFR"
# Everything else (Americas, Oceania, Central Asia, etc.) -> ROW

# ── Load Global1 MRIO ──
print("Loading Global1 MRIO...")
mrio_path = GLOBAL1 / "mrio.csv"
df = pd.read_csv(mrio_path, header=[0, 1], index_col=[0, 1])
print(f"  Shape: {df.shape}")

# Get the country and sector labels
row_countries = df.index.get_level_values(0).tolist()
row_sectors = df.index.get_level_values(1).tolist()
col_countries = df.columns.get_level_values(0).tolist()
col_sectors = df.columns.get_level_values(1).tolist()

# Identify unique countries in MRIO
unique_row_countries = list(dict.fromkeys(row_countries))
unique_col_countries = list(dict.fromkeys(col_countries))
print(f"  Row countries: {len(unique_row_countries)}")
print(f"  Col countries: {len(unique_col_countries)}")

# Map any unmapped country to ROW
for c in unique_row_countries:
    if c not in BLOC_MAP and c != "" and c != "ROW":
        BLOC_MAP[c] = "ROW"
for c in unique_col_countries:
    if c not in BLOC_MAP and c != "final_demand" and c != "Exports" and c != "":
        BLOC_MAP[c] = "ROW"

# Also handle ROW from Eora
BLOC_MAP["ROW"] = "ROW"

# ── Map rows and columns to blocs ──
# For rows: map (country, sector) -> (bloc, sector)
# Special rows (like "ROW,Imports") need special handling
new_row_blocs = []
for c, s in zip(row_countries, row_sectors):
    if c in BLOC_MAP:
        new_row_blocs.append(BLOC_MAP[c])
    elif s == "Imports" or s == "import":
        new_row_blocs.append("ROW")
    else:
        new_row_blocs.append("ROW")

# In Eora26, columns are (country, sector) for intermediates and (country, "final_demand")
# for final demand. The last column is (ROW, Exports-like).
# We need to:
#   1. Map intermediate columns: (country, sector) -> (bloc, sector)
#   2. Map final_demand columns: (country, "final_demand") -> (bloc, "final_demand")
#   3. Handle ROW/Exports separately

new_col_blocs = []
new_col_sectors = []
for c, s in zip(col_countries, col_sectors):
    bloc = BLOC_MAP.get(c, "ROW")
    if s == "final_demand":
        new_col_blocs.append(bloc)
        new_col_sectors.append("final_demand")
    else:
        new_col_blocs.append(bloc)
        new_col_sectors.append(s)

# ── Aggregate ──
print("Aggregating into Gulf blocs...")

# Create new multi-index
df_work = df.copy()
df_work.index = pd.MultiIndex.from_arrays([new_row_blocs, row_sectors],
                                           names=["from_country", "from_sector"])
df_work.columns = pd.MultiIndex.from_arrays([new_col_blocs, new_col_sectors],
                                             names=["to_country", "to_sector"])

# Group by (bloc, sector) for both rows and columns
# Sum flows within each bloc-sector pair
agg = df_work.groupby(level=[0, 1], axis=0).sum()
agg = agg.T.groupby(level=[0, 1]).sum().T

print(f"  Aggregated shape: {agg.shape}")

# ── Identify the blocs that ended up in the MRIO ──
result_row_countries = agg.index.get_level_values(0).unique().tolist()
result_col_countries = agg.columns.get_level_values(0).unique().tolist()
print(f"  Row blocs: {result_row_countries}")
print(f"  Col blocs: {result_col_countries}")

# ── Reorder: Gulf first, then external blocs, then special rows ──
bloc_order = GULF + ["IND", "PAK", "EAS", "EUR", "AFR", "ROW"]
# Only include blocs that actually exist in the data
bloc_order = [b for b in bloc_order if b in result_row_countries]

# Separate special rows (Imports from ROW if present)
special_rows = agg.loc[agg.index.get_level_values(1).isin(["Imports"])]
regular_rows = agg.loc[~agg.index.get_level_values(1).isin(["Imports"])]

# Get intermediate sectors (excluding special ones)
all_sectors = [s for s in regular_rows.index.get_level_values(1).unique()
               if s not in ["Imports", "final_demand"]]
print(f"  Sectors: {len(all_sectors)}")

# Build ordered index for regular rows
ordered_idx = []
for bloc in bloc_order:
    for sector in all_sectors:
        if (bloc, sector) in regular_rows.index:
            ordered_idx.append((bloc, sector))

regular_ordered = regular_rows.loc[ordered_idx]

# Reorder columns: intermediate (bloc, sector), then (bloc, final_demand)
ordered_col_idx = []
# First: all intermediate columns
for bloc in bloc_order:
    for sector in all_sectors:
        if (bloc, sector) in agg.columns:
            ordered_col_idx.append((bloc, sector))
# Then: final_demand columns per bloc
for bloc in bloc_order:
    if (bloc, "final_demand") in agg.columns:
        ordered_col_idx.append((bloc, "final_demand"))

# Filter to existing columns
ordered_col_idx = [c for c in ordered_col_idx if c in agg.columns]

# Combine regular + special rows, ordered columns
final = pd.concat([regular_ordered, special_rows])
final = final[ordered_col_idx]

print(f"  Final shape: {final.shape}")

# ── Write MRIO CSV ──
out_mrio = OUT_DIR / "mrio.csv"
final.to_csv(out_mrio)
print(f"Written MRIO to {out_mrio}")

# ── Build sector_table.csv ──
print("\nBuilding sector_table.csv...")

# Load Global1 sector table for reference (type, share_exporting_firms, etc.)
g1_sectors = pd.read_csv(GLOBAL1 / "sector_table.csv")

# Get sector metadata from any country (types are same across countries)
sector_meta = {}
for _, row in g1_sectors.iterrows():
    iso = row["country_ISO"]
    sname = row["sector"].replace(f"{iso}_", "", 1) if isinstance(row["sector"], str) else row["sector"]
    if sname not in sector_meta:
        sector_meta[sname] = {
            "type": row["type"],
            "essential": row.get("essential", True),
        }

# Aggregate share_exporting_firms per bloc-sector
g1_sectors["bloc"] = g1_sectors["country_ISO"].map(BLOC_MAP).fillna("ROW")
g1_sectors["sector_name"] = g1_sectors.apply(
    lambda r: r["sector"].replace(f"{r['country_ISO']}_", "", 1)
    if isinstance(r["sector"], str) else r["sector"], axis=1
)
share_agg = g1_sectors.groupby(["bloc", "sector_name"]).agg({
    "share_exporting_firms": "mean",
    "output": "sum",
    "final_demand": "sum",
}).reset_index()

# Default USD per ton by sector type (rough estimates for physical goods)
# These are order-of-magnitude values; will need refinement
USD_PER_TON_DEFAULTS = {
    "Agriculture": 500,
    "Fishing": 2000,
    "Mining and Quarrying": 100,
    "Food & Beverages": 1500,
    "Textiles and Wearing Apparel": 5000,
    "Wood and Paper": 800,
    "Petroleum, Chemical and Non-Metallic Mineral Products": 600,
    "Metal Products": 2000,
    "Electrical and Machinery": 15000,
    "Transport Equipment": 20000,
    "Other Manufacturing": 5000,
    "Recycling": 300,
    "Electricity, Gas and Water": 50000,  # service-like, high value/ton
    "Construction": 200,
    "Maintenance and Repair": 50000,
    "Wholesale Trade": 10000,
    "Retail Trade": 10000,
    "Hotels and Restraurants": 50000,
    "Transport": 10000,
    "Post and Telecommunications": 50000,
    "Finacial Intermediation and Business Activities": 100000,
    "Public Administration": 100000,
    "Education, Health and Other Services": 100000,
    "Private Households": 100000,
    "Others": 5000,
    "Re-export & Re-import": 5000,
}

# Build sector table rows
st_rows = []
for bloc, sector in final.index:
    if sector == "Imports":
        continue
    label = f"{bloc}_{sector}"
    meta = sector_meta.get(sector, {"type": "service", "essential": True})
    share_row = share_agg[(share_agg["bloc"] == bloc) & (share_agg["sector_name"] == sector)]
    share_exp = share_row["share_exporting_firms"].values[0] if len(share_row) > 0 else 0.1
    output_val = share_row["output"].values[0] if len(share_row) > 0 else 0
    fd_val = share_row["final_demand"].values[0] if len(share_row) > 0 else 0
    usd_val = USD_PER_TON_DEFAULTS.get(sector, 5000)

    st_rows.append({
        "labels": label,
        "sector": label,
        "type": meta["type"],
        "essential": meta.get("essential", True),
        "usd_per_ton": usd_val,
        "output": output_val,
        "final_demand": fd_val,
        "share_exporting_firms": share_exp,
        "cutoff": 0,
        "supply_data": "USD",
        "country": bloc,
        "country_ISO": bloc,
    })

st_df = pd.DataFrame(st_rows)
st_df.to_csv(OUT_DIR / "sector_table.csv", index=False)
print(f"Written sector_table.csv: {len(st_df)} rows")

# ── Build usd_per_ton.csv ──
usd_rows = []
for _, row in st_df.iterrows():
    usd_rows.append({
        "region": row["country_ISO"],
        "sector": row["sector"].replace(f"{row['country_ISO']}_", "", 1),
        "usd_per_ton": row["usd_per_ton"],
    })
usd_df = pd.DataFrame(usd_rows)
usd_df.to_csv(OUT_DIR / "usd_per_ton.csv", index=False)
print(f"Written usd_per_ton.csv: {len(usd_df)} rows")

# ── Summary ──
print("\n=== MRIO Summary ===")
print(f"Internal countries: {[b for b in bloc_order if b in GULF]}")
print(f"External blocs: {[b for b in bloc_order if b not in GULF]}")
print(f"Sectors per country: {len(all_sectors)}")
print(f"Total region-sectors: {len(final.index)}")
print(f"MRIO dimensions: {final.shape}")
