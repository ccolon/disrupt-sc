"""HS 2017 -> Cambodia MRIO sector concordance, from the HS -> OECD ICIO one of mrio-extractor (11 Nov 2026).

The Cambodian MRIO has 60 sectors close to ISIC Rev.4 divisions (sector_table.csv: CRO, LIV, FOR, FIS, MIN, MFO, MBE,
MTO, MTE, ...). Each ICIO sector maps to one Cambodian sector, except where the Cambodian table is finer (A01 = crops
and livestock; C10T12 = food, beverages, tobacco; C31T33 = furniture and other manufacturing), split here by HS chapter.
Precious metals (7106-7112) are dropped: gold carries a large value on almost no tonnage and would set the density of
basic metals. Used with compute_usd_per_ton_baci.py --concordance <out>.

Usage: python make_khm_concordance.py <hs17_to_icio_concordance.csv> <out.csv>
"""
import sys

import pandas as pd

ICIO_TO_KHM = {
    "A01": "CRO", "A02": "FOR", "A03": "FIS", "B05": "MIN", "B06": "MIN", "B07": "MIN", "B08": "MIN", "B09": "MIN",
    "C10T12": "MFO", "C13T15": "MTE", "C16": "MWO", "C17_18": "MPA", "C19": "MCO", "C20": "MCH", "C21": "MPH",
    "C22": "MRU", "C23": "MNM", "C24A": "MBA", "C24B": "MBA", "C25": "MFA", "C26": "MEL", "C27": "MEL", "C28": "MMA",
    "C29": "MMA", "C301": "MTR", "C302T309": "MTR", "C31T33": "MAO", "DROP": "DROP",
}
# Finer Cambodian sectors, by HS prefix (longest prefix wins in the tool).
OVERRIDES = {
    "01": ("LIV", "live animals"), "0407": ("LIV", "eggs in shell"), "0409": ("LIV", "natural honey"),
    "05": ("LIV", "animal products nes"), "4101": ("LIV", "raw hides (bovine)"), "4102": ("LIV", "raw hides (sheep)"),
    "4103": ("LIV", "raw hides (other)"),
    "22": ("MBE", "beverages"), "24": ("MTO", "tobacco products"), "2401": ("CRO", "unmanufactured tobacco (raw)"),
    "94": ("MFU", "furniture, bedding, prefab buildings"), "9405": ("MEL", "luminaires & lighting"),
    "7106": ("DROP", "silver unwrought"), "7107": ("DROP", "silver-clad"), "7108": ("DROP", "gold unwrought"),
    "7109": ("DROP", "gold-clad"), "7110": ("DROP", "platinum unwrought"), "7111": ("DROP", "platinum-clad"),
    "7112": ("DROP", "precious-metal waste"),
}
src, out = sys.argv[1], sys.argv[2]
c = pd.read_csv(src, dtype={"hs_prefix": str})
unknown = sorted(set(c.sector) - set(ICIO_TO_KHM))
if unknown:
    raise SystemExit(f"ICIO sectors without a Cambodian sector: {unknown}")
c["sector"] = c.sector.map(ICIO_TO_KHM)
for hs, (sec, note) in OVERRIDES.items():
    if hs in set(c.hs_prefix):
        c.loc[c.hs_prefix == hs, ["sector", "note"]] = [sec, note]
    else:
        c = pd.concat([c, pd.DataFrame([{"hs_prefix": hs, "sector": sec, "note": note}])], ignore_index=True)
c.sort_values("hs_prefix", key=lambda s: s.str.len() * 100 + s.str[:2].astype(int)).to_csv(out, index=False)
print(c.sector.value_counts().to_string())
