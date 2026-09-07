"""Cross-validate model interregional/EU trade structure against FIGARO-REG 2013."""
import sys
import geopandas as gpd
import numpy as np
import pandas as pd

RUN = sys.argv[1]
OUT = rf"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/output/Romania/{RUN}"
SPA = r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Spatial"

NUTS2 = {
 "RO11": ["BIHOR","BISTRITA-NASAUD","CLUJ","MARAMURES","SATU MARE","SALAJ"],
 "RO12": ["ALBA","BRASOV","COVASNA","HARGHITA","MURES","SIBIU"],
 "RO21": ["BACAU","BOTOSANI","IASI","NEAMT","SUCEAVA","VASLUI"],
 "RO22": ["BRAILA","BUZAU","CONSTANTA","GALATI","TULCEA","VRANCEA"],
 "RO31": ["ARGES","CALARASI","DAMBOVITA","GIURGIU","IALOMITA","PRAHOVA","TELEORMAN"],
 "RO32": ["BUCURESTI","ILFOV"],
 "RO41": ["DOLJ","GORJ","MEHEDINTI","OLT","VALCEA"],
 "RO42": ["ARAD","CARAS-SEVERIN","HUNEDOARA","TIMIS"],
}
C2N = {c: n for n, cs in NUTS2.items() for c in cs}
CC2BLOC = {"DE":"DEU","HU":"HUN","BG":"BGR","AT":"EURDAN","SI":"EURDAN","HR":"EURDAN","CH":"EURDAN",
 "PL":"EURCE","CZ":"EURCE","SK":"EURCE","EE":"EURCE","LV":"EURCE","LT":"EURCE",
 "FR":"EURNW","BE":"EURNW","NL":"EURNW","LU":"EURNW","IE":"EURNW","DK":"EURNW","SE":"EURNW",
 "FI":"EURNW","NO":"EURNW","UK":"EURNW","IS":"EURNW","GB":"EURNW",
 "IT":"EURS","ES":"EURS","PT":"EURS","MT":"EURS","EL":"EURSE","CY":"EURSE"}
BLOCS = ["DEU","HUN","BGR","EURDAN","EURCE","EURNW","EURS","EURSE"]
RO = list(NUTS2)
FOCUS = ["RO21","RO11","RO22"]

# ---- model side -------------------------------------------------------
ft = gpd.read_file(OUT + "/firm_table.geojson")
adm1 = gpd.read_file(SPA + "/sources/ROU_adm1.geojson")
fj = gpd.sjoin(ft, adm1[["shapeName","geometry"]], how="left", predicate="within")
ft["nuts2"] = fj["shapeName"].map(C2N)
# firms exactly on a border may miss 'within' - nearest fallback
miss = ft["nuts2"].isna()
if miss.any():
    near = gpd.sjoin_nearest(ft[miss], adm1[["shapeName","geometry"]], how="left")
    ft.loc[miss, "nuts2"] = near["shapeName"].map(C2N).values
firm_reg = dict(zip(ft["name"], ft["nuts2"]))  # link seller_id is the firm name/pid
firm_reg_by_id = dict(zip(ft["id"].astype(str), ft["nuts2"]))

ht = gpd.read_file(OUT + "/household_table.geojson")
hh_reg = dict(zip(ht["household"], ht["subregion_adm1"].map(C2N)))

ld = pd.read_csv(OUT + "/link_data.csv")
print(f"link rows: {len(ld):,}")

def agent_region(aid, atype_hint=None):
    aid = str(aid)
    if aid in firm_reg_by_id: return firm_reg_by_id[aid]
    if aid in firm_reg: return firm_reg[aid]
    if aid in hh_reg: return hh_reg[aid]
    if aid in BLOCS: return aid
    if aid in ("ASI","AME","ROW","TUR","UKR","DEU","HUN","BGR"): return aid
    return None

ld["from"] = ld["seller_id"].map(agent_region)
ld["to"] = ld["buyer_id"].map(agent_region)
bad = ld["from"].isna() | ld["to"].isna()
print("unmapped link rows:", int(bad.sum()), "| sample:",
      ld.loc[bad, ["seller_id","buyer_id"]].head(3).to_dict("records"))
ld = ld[~bad]
Mm = ld.groupby(["from","to"])["delivery"].sum().unstack(fill_value=0.0)
Mm = Mm.reindex(index=RO + BLOCS + ["TUR","UKR","ASI","AME","ROW"], fill_value=0.0)\
       .reindex(columns=RO + BLOCS + ["TUR","UKR","ASI","AME","ROW"], fill_value=0.0)
Mm.to_csv("model_region_flows.csv")

# ---- figaro side ------------------------------------------------------
F = pd.read_parquet("figaro_region_flows.parquet")
def to_group(code):
    if code in RO: return code
    cc = code[:2]
    if cc == "RO": return None          # other RO labels (none expected)
    return CC2BLOC.get(cc)              # None for non-EU / ROW / overseas
gmap = {c: to_group(c) for c in F.columns}
Fg = F.copy()
Fg.columns = [gmap.get(c) for c in F.columns]
Fg = Fg.T.groupby(level=0).sum().T
Fg.index = [gmap.get(r) for r in F.index]
Fg = Fg.groupby(level=0).sum()
Fg = Fg.reindex(index=RO + BLOCS, fill_value=0.0).reindex(columns=RO + BLOCS, fill_value=0.0)
Fg.to_csv("figaro_region_flows_grouped.csv")

# ---- metrics ----------------------------------------------------------
UNIV = RO + BLOCS   # common universe: RO regions + covered EU blocs

def orientation(M, region, axis):
    """sales (axis=0: region row) or purchases (axis=1) split: intra / other RO / EU."""
    v = M.loc[region, UNIV] if axis == 0 else M.loc[UNIV, region]
    intra = v[region]
    other_ro = v[[r for r in RO if r != region]].sum()
    eu = v[BLOCS].sum()
    tot = intra + other_ro + eu
    return np.array([intra, other_ro, eu]) / tot

rows = []
for r in FOCUS:
    for name, M in (("model", Mm), ("FIGARO", Fg)):
        s = orientation(M, r, 0); p = orientation(M, r, 1)
        rows.append([r, name, *s, *p])
ori = pd.DataFrame(rows, columns=["region","source","s_intra","s_otherRO","s_EU","p_intra","p_otherRO","p_EU"])
print("\n== trade orientation (shares of total, common universe) ==")
print(ori.round(3).to_string(index=False))

# interregional RO matrix: row shares (excl. diagonal), correlation
def row_shares(M):
    X = M.loc[RO, RO].copy().astype(float)
    np.fill_diagonal(X.values, 0.0)
    return X.div(X.sum(axis=1), axis=0)
Sm, Sf = row_shares(Mm), row_shares(Fg)
mask = ~np.eye(8, dtype=bool)
corr = np.corrcoef(Sm.values[mask], Sf.values[mask])[0, 1]
from scipy.stats import spearmanr
rho = spearmanr(Sm.values[mask], Sf.values[mask]).statistic
print(f"\nRO 8x8 interregional destination shares: Pearson r={corr:.2f}, Spearman rho={rho:.2f}")

# EU partner mix per focus region (exports + imports shares over blocs)
part_rows = []
for r in FOCUS:
    for name, M in (("model", Mm), ("FIGARO", Fg)):
        ex = M.loc[r, BLOCS] / max(M.loc[r, BLOCS].sum(), 1e-9)
        im = M.loc[BLOCS, r] / max(M.loc[BLOCS, r].sum(), 1e-9)
        part_rows.append([r, name, "exports", *ex.values])
        part_rows.append([r, name, "imports", *im.values])
part = pd.DataFrame(part_rows, columns=["region","source","dir"] + BLOCS)
print("\n== EU partner mix per focus region ==")
print(part.round(3).to_string(index=False))
for r in FOCUS:
    a = part[(part.region==r) & (part.source=="model")][BLOCS].values.ravel()
    b = part[(part.region==r) & (part.source=="FIGARO")][BLOCS].values.ravel()
    print(f"{r}: partner-mix Pearson r={np.corrcoef(a,b)[0,1]:.2f}, Spearman={spearmanr(a,b).statistic:.2f}")
ori.to_csv("crossval_orientation.csv", index=False)
part.to_csv("crossval_partner_mix.csv", index=False)
Sm.to_csv("crossval_ro_shares_model.csv"); Sf.to_csv("crossval_ro_shares_figaro.csv")
