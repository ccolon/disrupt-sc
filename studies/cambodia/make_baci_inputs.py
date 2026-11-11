"""New sector table and countries file of the recalibrated Cambodia base (11 Nov 2026, decision Q31, report 17).

- Economic/sector_table_baci2023.csv: Economic/sector_table.csv with
  * usd_per_ton of the goods sectors from BACI 2023 (Cambodia's own trade mix; compute_usd_per_ton_baci.py of
    mrio-extractor with studies/cambodia/hs17_to_khm_concordance.csv; table baci2023/usd_per_ton_KHM.csv);
  * MCO (coke and refined petroleum) typed oil_and_gas, as C19 in the Rhine 2026 EU table, so that it travels as
    liquid bulk (logistics.sector_to_cargo_type of config/default.yaml). Every other type is unchanged.
  Sectors without a BACI density (services, utilities, construction, trade, transport, the IMP row) keep their value.
- Spatial/countries_baci2023.geojson: Spatial/countries.geojson (geometry untouched) with a usd_per_ton property per
  partner bloc: the density of Cambodia's 2023 imports from that bloc (baci2023/baci_khm_imports.csv, made by
  studies/cambodia/baci_khm_imports.py). The model reads it as a per-country override (init_pipeline/agents.py).
  ROW has no import row in the MRIO and gets no value.

Usage: python make_baci_inputs.py <data>/Cambodia
"""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

D = Path(sys.argv[1])
st = pd.read_csv(D / "Economic" / "sector_table.csv")
baci = pd.read_csv(D / "Economic" / "baci2023" / "usd_per_ton_KHM.csv")
key = "sector" if "sector" in baci.columns else baci.columns[0]
dens = dict(zip(baci[key], baci.usd_per_ton))
missing = sorted(s for s in dens if s not in set(st.sector))
assert not missing, f"BACI sectors not in the sector table: {missing}"
new = st.copy()
new["usd_per_ton"] = [dens.get(s, v) for s, v in zip(st.sector, st.usd_per_ton)]
assert (st.loc[st.sector == "MCO", "type"] == "manufacturing").all()
new.loc[new.sector == "MCO", "type"] = "oil_and_gas"
out = D / "Economic" / "sector_table_baci2023.csv"
new.to_csv(out, index=False)
ch = new.merge(st[["sector", "usd_per_ton", "type"]], on="sector", suffixes=("", "_old"))
ch = ch[(ch.usd_per_ton != ch.usd_per_ton_old) | (ch.type != ch.type_old)]
print(ch[["sector", "type_old", "type", "usd_per_ton_old", "usd_per_ton"]].round(1).to_string(index=False))

imp = pd.read_csv(D / "Economic" / "baci2023" / "baci_khm_imports.csv").set_index("bloc")
g = json.loads((D / "Spatial" / "countries.geojson").read_text(encoding="utf-8"))
for f in g["features"]:
    r = f["properties"]["region"]
    if r in imp.index and r not in ("ROW", "all"):
        f["properties"]["usd_per_ton"] = round(float(imp.loc[r, "usd_per_ton"]), 1)
outc = D / "Spatial" / "countries_baci2023.geojson"
outc.write_text(json.dumps(g, ensure_ascii=False, indent=0), encoding="utf-8")
print({f["properties"]["region"]: f["properties"].get("usd_per_ton") for f in g["features"]})
for p in (out, outc):
    print("sha256", hashlib.sha256(p.read_bytes()).hexdigest(), p.name)
