"""Romania mixed-resolution mesh: urban-LAU households + refined firm layer.

Rebuilds (deterministically) the two v7 spatial inputs:
  Spatial/households_fine.geojson   123 urban-locality points in NE/NV/SE
                                    (rural folded to nearest urban within
                                    county, county totals rescaled to the
                                    2021 census) + 24 county points elsewhere
  Spatial/firms_firmlevel_fine.geojson
                                    county-clipped firm rows (sources
                                    regional_stats / households_fallback) in
                                    the 18 fine counties re-disaggregated on
                                    the urban mesh, 0.1%-of-sector cutoff

Inputs (all in Spatial/sources or Spatial/):
  ROU_adm1.geojson, ROU_adm2.geojson          geoBoundaries gbOpen
  EU-27-LAU-2022-NUTS-2021.xlsx               Eurostat LAU list ('RO' sheet:
      NUTS3=county, 'Municipiul/Orasul' name prefix = urban status, POPULATION
      = DOMICILE-based -> rescaled to census; LAU NAME LATIN for matching)
  county_population_2021.csv                  census resident totals
  households.geojson, firms_firmlevel.geojson previous county-resolution files

Usage: python romania_refine_mesh_urban.py
"""

from __future__ import annotations

import difflib
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd

SRC = r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Spatial/sources"
SPA = r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Spatial"
NUTS3_COUNTY = {
    "RO111": "BIHOR", "RO112": "BISTRITA-NASAUD", "RO113": "CLUJ", "RO114": "MARAMURES",
    "RO115": "SATU MARE", "RO116": "SALAJ",
    "RO211": "BACAU", "RO212": "BOTOSANI", "RO213": "IASI", "RO214": "NEAMT",
    "RO215": "SUCEAVA", "RO216": "VASLUI",
    "RO221": "BRAILA", "RO222": "BUZAU", "RO223": "CONSTANTA", "RO224": "GALATI",
    "RO225": "TULCEA", "RO226": "VRANCEA",
}
FINE = set(NUTS3_COUNTY.values())
CUTOFF = 0.001  # refined firm rows below this share of their sector are dropped


def norm(s: str) -> str:
    s = str(s)
    for pre in ("Municipiul ", "Orasul ", "Oras "):
        if s.startswith(pre):
            s = s[len(pre):]
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return " ".join(s.replace("-", " ").split())


def build_urban_points() -> gpd.GeoDataFrame:
    lau = pd.read_excel(SRC + "/EU-27-LAU-2022-NUTS-2021.xlsx", sheet_name="RO")
    lau = lau[lau["NUTS3"].astype(str).str.startswith(("RO11", "RO21", "RO22"))].copy()
    lau["county"] = lau["NUTS3"].map(NUTS3_COUNTY)
    lau["urban"] = lau["LAU NAME NATIONAL"].astype(str).str.match(
        r"^(Municipiul|Ora[sșş]ul|Ora[sșş] )", case=False)
    lau["key"] = (lau["LAU NAME LATIN"].map(norm)
                  .str.replace("IRLAD", "ARLAD").str.replace("TIRGU", "TARGU"))

    adm1 = gpd.read_file(SRC + "/ROU_adm1.geojson")
    adm2 = gpd.read_file(SRC + "/ROU_adm2.geojson")
    adm1f = adm1[adm1.shapeName.isin(FINE)]
    adm2["key0"] = (adm2["shapeName"].str.upper().str.replace("-", " ")
                    .str.replace("TIRGU", "TARGU").str.replace("IRLAD", "ARLAD")
                    .map(lambda s: " ".join(s.split())))
    cent = adm2.copy()
    cent["geometry"] = adm2.geometry.representative_point()
    j = gpd.sjoin(cent[["key0", "geometry"]],
                  adm1f[["shapeName", "geometry"]].rename(columns={"shapeName": "county"}),
                  how="inner", predicate="within")
    adm2["county"] = None
    adm2.loc[j.index, "county"] = j["county"].values
    adm2f = adm2[adm2.county.notna()].dissolve(by=["county", "key0"], as_index=False)

    poly = {(r.county, r.key0): r.geometry for r in adm2f.itertuples()}
    by_county = {c: [k for (cc, k) in poly if cc == c] for c in FINE}
    geoms = []
    for r in lau.itertuples():
        g = poly.get((r.county, r.key))
        if g is None:
            cand = difflib.get_close_matches(r.key, by_county.get(r.county, []), n=1, cutoff=0.82)
            g = poly[(r.county, cand[0])] if cand else None
        geoms.append(g)
    lau["geometry"] = geoms
    assert not (lau.urban & lau.geometry.isna()).any(), "unmatched urban LAU"

    g = gpd.GeoDataFrame(lau[lau.geometry.notna()].copy(), geometry="geometry", crs=adm1.crs)
    g["pt"] = g.geometry.representative_point()
    urban, rural = g[g.urban].copy(), g[~g.urban].copy()
    add: dict = {}
    for county, ru in rural.groupby("county"):
        ub = urban[urban.county == county]
        ux = np.array([p.x for p in ub.pt]); uy = np.array([p.y for p in ub.pt])
        for r in ru.itertuples():
            tgt = ub.index[int(np.argmin((ux - r.pt.x) ** 2 + (uy - r.pt.y) ** 2))]
            add[tgt] = add.get(tgt, 0.0) + float(r.POPULATION or 0)
    urban["population"] = urban["POPULATION"].astype(float) + urban.index.map(lambda i: add.get(i, 0.0))
    lost = lau[lau.geometry.isna()].groupby("county")["POPULATION"].sum()
    for county, pop in lost.items():
        ub = urban[urban.county == county]
        urban.loc[ub.index, "population"] += (float(pop) * ub["POPULATION"].astype(float)
                                              / ub["POPULATION"].sum())
    census = pd.read_csv(SPA + "/county_population_2021.csv").set_index("name")["population"]
    for county, ub in urban.groupby("county"):
        urban.loc[ub.index, "population"] *= census[county] / urban.loc[ub.index, "population"].sum()
    return urban


def main() -> None:
    urban = build_urban_points()
    adm1_crs = "EPSG:4326"

    hh_old = gpd.read_file(SPA + "/households.geojson")
    keep = hh_old[~hh_old["subregion_adm1"].isin(FINE)][
        ["region", "population", "subregion_adm1", "geometry"]].copy()
    keep["subregion_lau"] = None
    fine = gpd.GeoDataFrame({
        "region": "ROU", "population": urban["population"].values,
        "subregion_adm1": urban["county"].values,
        "subregion_lau": urban["LAU NAME LATIN"].values,
        "geometry": [p for p in urban["pt"]]}, crs=adm1_crs)
    out = gpd.GeoDataFrame(pd.concat([keep, fine], ignore_index=True), crs=adm1_crs)
    out.to_file(SPA + "/households_fine.geojson", driver="GeoJSON")
    print(f"households_fine: {len(out)} pts, total pop {out.population.sum():,.0f}")

    firms = gpd.read_file(SPA + "/firms_firmlevel.geojson")
    adm1 = gpd.read_file(SRC + "/ROU_adm1.geojson")
    fj = gpd.sjoin(firms, adm1[["shapeName", "geometry"]].rename(columns={"shapeName": "county"}),
                   how="left", predicate="within").drop(columns="index_right")
    target = fj["source"].isin(["regional_stats", "households_fallback"]) & fj["county"].isin(FINE)
    keep_f = fj[~target].drop(columns="county")
    rows = []
    for (county, sector), grp in fj[target].groupby(["county", "sector"]):
        tot = grp["importance"].sum()
        ub = fine[fine.subregion_adm1 == county]
        shares = ub["population"] / ub["population"].sum()
        for (_, u), sh in zip(ub.iterrows(), shares):
            rows.append({"region": "ROU", "sector": sector, "importance": tot * sh,
                         "name": f"{sector}_{u.subregion_lau}",
                         "source": "regional_stats_fine", "geometry": u.geometry})
    ref = gpd.GeoDataFrame(rows, crs=firms.crs)
    sec_tot = pd.concat([keep_f, ref]).groupby("sector")["importance"].sum()
    ref = ref[ref.apply(lambda r: r["importance"] >= CUTOFF * sec_tot[r["sector"]], axis=1)]
    out_f = gpd.GeoDataFrame(pd.concat([keep_f, ref], ignore_index=True), crs=firms.crs)
    out_f.to_file(SPA + "/firms_firmlevel_fine.geojson", driver="GeoJSON")
    print(f"firms_firmlevel_fine: {len(out_f)} rows "
          f"(importance {out_f['importance'].sum():,.0f} vs {firms['importance'].sum():,.0f})")


if __name__ == "__main__":
    main()
