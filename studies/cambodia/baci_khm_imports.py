"""Cambodia's imports by partner bloc from BACI 2023: tonnes, value, density and cargo-class mix (11 Nov 2026).

The Cambodian MRIO has one import row per partner bloc (VNM, THA, LAO, AFR, AME, ASI, EUR, OCE) and no product
dimension, so the model gives each bloc one density (usd_per_ton, overridable per country in countries.geojson) and
one cargo class. This table gives, per bloc, the observed density (tonnage-weighted mean unit value, 1000 * sum v /
sum q) and the share of tonnes and value by cargo class, with the class of each HS6 from its Cambodian sector and the
Rhine 2026 rule (sector type: agriculture and mining -> dry_bulk; refined petroleum, C19/MCO -> liquid_bulk; other
manufacturing -> container), plus cement (HS 2523) and mineral fuels (HS 27) as their own columns.

Unit-value outliers are dropped as in mrio-extractor/compute_usd_per_ton_baci.py: flows outside the world per-HS6
[P0.5, P99.5] band. Blocs: THA, VNM, LAO by ISO3; others by Natural Earth region_un (disruptsc-dataprep
dataprep/data/countries.geojson): Africa AFR, Americas AME, Asia ASI, Europe EUR, Oceania OCE; unmatched ROW.

Usage: python baci_khm_imports.py <BACI_HS17_Y2023.csv> <country_codes.csv> <hs17_to_khm_concordance.csv>
                                  <naturalearth countries.geojson> <out.csv>
"""
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

BACI, CC, CONC, NE, OUT = sys.argv[1:6]
KHM = 116
TYPE = {"CRO": "agriculture", "LIV": "agriculture", "FOR": "agriculture", "FIS": "agriculture", "MIN": "mining",
        "MCO": "oil_and_gas"}
CARGO = {"agriculture": "dry_bulk", "mining": "dry_bulk", "oil_and_gas": "liquid_bulk"}

b = pd.read_csv(BACI, usecols=["i", "j", "k", "v", "q"], dtype={"k": str})
b = b[(b.v > 0) & (b.q > 0)].copy()
b["uv"] = 1000 * b.v / b.q
band = b.groupby("k").uv.quantile([0.005, 0.995]).unstack()
b = b[b.j == KHM].join(band, on="k")
n0 = len(b)
b = b[(b.uv >= b[0.005]) & (b.uv <= b[0.995])].copy()
print(f"KHM import flows: {n0}, kept {len(b)} inside the per-HS6 bands")

conc = pd.read_csv(CONC, dtype={"hs_prefix": str})
by = {n: conc[conc.hs_prefix.str.len() == n].set_index("hs_prefix").sector.to_dict() for n in (2, 4, 6)}
k6 = b.k.str.zfill(6)
b["sector"] = k6.map(by[6]).fillna(k6.str[:4].map(by[4])).fillna(k6.str[:2].map(by[2]))
b = b[b.sector.notna() & (b.sector != "DROP")]
b["cargo"] = b.sector.map(TYPE).map(CARGO).fillna("container")
b["cement"] = k6.str[:4] == "2523"
b["fuel"] = k6.str[:2] == "27"

cc = pd.read_csv(CC)
ne = gpd.read_file(NE)[["iso_a3_eh", "region_un"]]
reg = dict(zip(ne.iso_a3_eh, ne.region_un))
BLOC = {"Africa": "AFR", "Americas": "AME", "Asia": "ASI", "Europe": "EUR", "Oceania": "OCE"}
iso = dict(zip(cc.country_code, cc.country_iso3))


def bloc(code):
    a = iso.get(code)
    if a in ("THA", "VNM", "LAO"):
        return a
    if a == "S19":          # BACI "Other Asia, nes" (Taiwan)
        return "ASI"
    return BLOC.get(reg.get(a), "ROW")


b["bloc"] = b.i.map(bloc)
rows = []
for name, g in list(b.groupby("bloc")) + [("all", b)]:
    t, v = g.q.sum(), g.v.sum()
    r = {"bloc": name, "kt": t / 1e3, "musd": v / 1e3, "usd_per_ton": 1000 * v / t}
    for c in ("container", "dry_bulk", "liquid_bulk"):
        r[f"t_{c}_pct"] = 100 * g.q[g.cargo == c].sum() / t
        r[f"v_{c}_pct"] = 100 * g.v[g.cargo == c].sum() / v
    r["t_cement_pct"] = 100 * g.q[g.cement].sum() / t
    r["t_fuel_pct"] = 100 * g.q[g.fuel].sum() / t
    for c in ("container", "dry_bulk", "liquid_bulk"):
        s = g[g.cargo == c]
        r[f"upt_{c}"] = 1000 * s.v.sum() / s.q.sum() if len(s) else np.nan
    rows.append(r)
t = pd.DataFrame(rows)
t.to_csv(OUT, index=False)
pd.set_option("display.width", 250)
print(t.round(1).to_string(index=False))
unm = b[b.bloc == "ROW"].i.map(iso).value_counts().head(10)
print("partners mapped to ROW:", unm.to_dict())
