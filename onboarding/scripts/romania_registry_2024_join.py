# -*- coding: utf-8 -*-
"""CUI-join of the 2024 INS active-units file with the 2023 registry, and
UAT-level (SIRUTA) weights for the 14 registry goods sectors (Deliverable 3).

Inputs:
  world_bank_2024.xlsx / active_units_2024_BH.csv  (INS via WB, sections
      B/C/D/E/G/H, 311,419 firms, CUI + NACE4 + employees + turnover +
      HQ locality name + locality SIRUTA + county)  [EXTERNAL, confidential]
  RO-infra-2023.dta                                (v19 source; fuid = CUI)
  Spatial/sources/siruta_register.csv              (INS SIRUTA nomenclature,
      data.gov.ro, cp1250 ;-separated: locality NIV 3 -> SIRSUP -> UAT NIV 2)
  Spatial/sources/EU-27-LAU-2022-NUTS-2021.xlsx    (RO LAU CODE = UAT SIRUTA)
  Spatial/sources/ROU_adm1.geojson, ROU_adm2.geojson

DECISIONS (20 Oct 2026, continuing D1-D6 of romania_registry_weights.py -
user to review):
  D7.  (REVISED after D12) The 2024 registry sets the FULL within-sector
       geography - county AND locality - for the 14 goods sectors; only the
       national sector total stays anchored to the MRIO importance scale.
       Keeping v19 county totals would cancel the cross-county plant
       overrides (D12). The 2023->2024 county drift is small (share corr
       0.955 sales-weighted) except where the overrides deliberately move
       weight (Michelin Ilfov->Salaj/Prahova, breweries Bucharest->plants).
       The v19 layer is kept on disk for A/B.
  D8.  Within-county weight = 2024 turnover, localities collapsed to their
       UAT (SIRSUP walk), placed at the UAT polygon representative point.
       Locality-vs-UAT error is a few km, immaterial vs the county centroid.
  D9.  The county used is the SIRUTA-derived one (register JUD), not the
       file's county label - immune to label transpositions like D4's
       Brasov<->Braila. Disagreements are counted and printed.
  D10. The committed artifact (registry_uat_2024.csv) holds UAT x sector
       AGGREGATES only - no CUI, no names (microdata stays in the external
       WorldBank folder). NOTE: a UAT x sector cell can still be a single
       identifiable firm; same precedent as the committed county file,
       flagged for the user's data-agreement judgment.
  D11. UAT without geometry match / SIRUTA missing from the register ->
       county representative point fallback, counted and printed.
  D12. Heavy-tail plant overrides (sources/registry_plant_overrides.csv,
       public plant locations, shares employee/capacity-based or marked
       ESTIMATE): six multi-plant/HQ-booked firms (Michelin, Coca-Cola HBC,
       Ursus, Heineken, Quadrant-PepsiCo, De'Longhi) have their 2024
       turnover reallocated from the HQ UAT to plant UATs before
       aggregation. All other top-100 firms hand-checked 20 Oct 2026:
       HQ locality = plant locality (single-site or same-county).

Outputs:
  Spatial/sources/registry_uat_2024.csv            [COMMITTED]
      sector, county (adm1 spelling), lau_code, uat_name, lon, lat,
      value (2024 turnover, M RON) - 14 goods sectors only
  <BusinessRegistry>/registry_bh_2023_2024_joined.csv   [EXTERNAL]
  <BusinessRegistry>/heavy_tail_top100_2023sales.csv    [EXTERNAL]

Run in dsc env: python romania_registry_2024_join.py
"""

from __future__ import annotations

import difflib
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

EXT = Path(r"C:\Users\Celian\OneDrive\WorldBank\Romania\Data\BusinessRegistry")
SRC = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc-data\Romania\Spatial\sources")
CSV24 = EXT / "active_units_2024_BH.csv"
DTA23 = EXT / "RO-infra-2023.dta"
OUT_UAT = SRC / "registry_uat_2024.csv"
OUT_JOIN = EXT / "registry_bh_2023_2024_joined.csv"
OUT_TAIL = EXT / "heavy_tail_top100_2023sales.csv"

SALES_SECTORS = ["B09", "C10T12", "C13T15", "C16", "C17_18", "C21", "C22",
                 "C25", "C26", "C27", "C28", "C302T309", "C31T33", "E"]


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
    return None


def norm(s: str) -> str:
    # fold diacritics BEFORE stripping prefixes: 'ORAŞ UNGHENI' must become
    # 'UNGHENI', not keep its prefix because 'ORAŞ ' != 'ORAS ' (v25 fix)
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    for pre in ("MUNICIPIUL ", "ORASUL ", "ORAS "):
        if s.startswith(pre):
            s = s[len(pre):]
    return " ".join(s.replace("-", " ").split())


def main() -> int:
    # ---- SIRUTA register: locality -> UAT -> county name -------------------
    reg = pd.read_csv(SRC / "siruta_register.csv", sep=";", encoding="cp1250",
                      decimal=",")
    for c in ("SIRUTA", "SIRSUP", "NIV", "JUD"):
        reg[c] = pd.to_numeric(reg[c], errors="coerce").astype("Int64")
    jud_name = {int(r.JUD): norm(str(r.DENLOC).replace("JUDE", "").split(" ", 1)[-1])
                for r in reg[reg.NIV == 1].itertuples()}
    jud_name[40] = "BUCURESTI"
    niv = reg.set_index("SIRUTA")
    to_uat = {}
    for r in reg.itertuples():
        s = int(r.SIRUTA)
        if r.NIV == 3:
            to_uat[s] = int(r.SIRSUP)
        elif r.NIV == 2:
            to_uat[s] = s
    uat_jud = {int(r.SIRUTA): int(r.JUD) for r in reg[reg.NIV == 2].itertuples()}
    uat_name = {int(r.SIRUTA): str(r.DENLOC) for r in reg[reg.NIV == 2].itertuples()}

    # ---- 2024 file ----------------------------------------------------------
    f24 = pd.read_csv(CSV24)
    f24["uat"] = f24["siruta"].map(to_uat)
    n_nouat = int(f24["uat"].isna().sum())
    f24["county_reg"] = f24["uat"].map(uat_jud).map(jud_name)
    mism = f24[f24["county_reg"].notna()
               & (f24["county_reg"] != f24["county"].map(norm))]
    print(f"2024 file: {len(f24)} rows; SIRUTA not in register: {n_nouat}; "
          f"county label vs SIRUTA-derived disagreements: {len(mism)}")
    if len(mism):
        print(mism.groupby(["county", "county_reg"]).size().nlargest(8).to_string())
    f24["county_use"] = f24["county_reg"].fillna(f24["county"].map(norm))

    # ---- 2023 registry (D4 swap + D5 drop replicated) -----------------------
    f23 = pd.read_stata(DTA23, columns=["fuid", "name", "nace4d_num", "emp",
                                        "sales", "nuts3_desc"])
    f23["county23"] = f23["nuts3_desc"].replace({"Braila": "Brasov",
                                                 "Brasov": "Braila"}).map(norm)
    f23 = f23[~((f23["emp"] > 1000) & (f23["sales"].isna()))]
    f23 = f23.rename(columns={"fuid": "cui", "name": "name23",
                              "nace4d_num": "nace23", "emp": "emp23",
                              "sales": "sales23"})

    # ---- CUI join -----------------------------------------------------------
    j = f24.merge(f23[["cui", "name23", "nace23", "emp23", "sales23", "county23"]],
                  on="cui", how="left")
    j["sec24"] = [sector_of(int(n)) if pd.notna(n) else None for n in j["nace4"]]
    div = (j["nace4"] // 100)
    j["section"] = pd.cut(div, bins=[4, 9, 33, 35, 39, 47, 53],
                          labels=["B", "C", "D", "E", "G", "H"])
    m = j["name23"].notna()
    print(f"\nCUI join: {m.sum()}/{len(j)} 2024 rows matched to 2023 "
          f"({m.mean():.1%} of rows, "
          f"{j.loc[m,'turnover'].sum()/j['turnover'].sum():.1%} of 2024 turnover)")
    print(j.groupby("section", observed=True)
           .apply(lambda g: pd.Series({"rows_matched": g['name23'].notna().mean(),
                                       "turnover_matched": g.loc[g['name23'].notna(), 'turnover'].sum()
                                                           / max(g['turnover'].sum(), 1)}),
                  include_groups=False).round(3).to_string())
    # reverse coverage: 2023 B-H firms found in 2024
    f23["sec"] = [sector_of(int(n)) for n in f23["nace23"]]
    bh23 = f23[f23["nace23"].between(500, 5399) & ~f23["nace23"].between(4000, 4499)]
    in24 = bh23["cui"].isin(set(f24["cui"]))
    print(f"reverse: {in24.mean():.1%} of 2023 B-H firms present in 2024 "
          f"({bh23.loc[in24,'sales23'].sum()/bh23['sales23'].sum():.1%} of their 2023 sales)")

    # ---- UAT geometry (LAU code = UAT SIRUTA; adm2 polygons by name) --------
    lau = pd.read_excel(SRC / "EU-27-LAU-2022-NUTS-2021.xlsx", sheet_name="RO")
    lau["lau_code"] = pd.to_numeric(lau["LAU CODE"], errors="coerce").astype("Int64")
    lau["county"] = lau["lau_code"].map(uat_jud).map(jud_name)
    lau["key"] = lau["LAU NAME LATIN"].map(norm)

    adm1 = gpd.read_file(SRC / "ROU_adm1.geojson")
    adm2 = gpd.read_file(SRC / "ROU_adm2.geojson")
    cent = adm2.copy()
    cent["geometry"] = adm2.geometry.representative_point()
    sj = gpd.sjoin(cent[["shapeName", "geometry"]],
                   adm1[["shapeName", "geometry"]].rename(
                       columns={"shapeName": "county"}),
                   how="inner", predicate="within", lsuffix="2", rsuffix="1")
    adm2["county"] = None
    adm2.loc[sj.index, "county"] = sj["county"].values
    adm2["key"] = adm2["shapeName"].map(norm)
    adm2d = adm2[adm2.county.notna()].dissolve(["county", "key"], as_index=False)
    poly = {(r.county, r.key): r.geometry for r in adm2d.itertuples()}
    by_cty = {}
    for (c, k) in poly:
        by_cty.setdefault(c, []).append(k)

    pts, miss = {}, 0
    cty_pt = {r.shapeName: r.geometry.representative_point()
              for r in adm1.itertuples()}
    for r in lau.itertuples():
        if pd.isna(r.lau_code) or r.county is None:
            continue
        g = poly.get((r.county, r.key))
        if g is None:
            cand = difflib.get_close_matches(r.key, by_cty.get(r.county, []),
                                             n=1, cutoff=0.82)
            g = poly[(r.county, cand[0])] if cand else None
        if g is None:
            miss += 1
            g = cty_pt.get(r.county)
        if g is not None:
            p = g.representative_point() if g.geom_type != "Point" else g
            pts[int(r.lau_code)] = (p.x, p.y)
    print(f"\nUAT geometry: {len(pts)} LAUs placed, {miss} fell back to "
          f"county point")

    # ---- committed artifact: UAT x sector aggregates, 14 goods sectors ------
    w = j[j["sec24"].isin(SALES_SECTORS) & j["uat"].notna()].copy()
    w["uat"] = w["uat"].astype(int)

    # D12: heavy-tail plant overrides - reallocate listed firms' turnover
    # from the HQ UAT to plant UATs (resolved by county + UAT name)
    ov = pd.read_csv(SRC / "registry_plant_overrides.csv")
    uat_by_cty = {}
    for u, jd in uat_jud.items():
        uat_by_cty.setdefault(jud_name.get(jd), {})[norm(uat_name[u])] = u
    rows_ov = []
    named_rows = []   # D13: overrides with explicit lon/lat become their own
    # NAMED rows in the committed artifact (exact plant placement) instead of
    # merging into a UAT aggregate; the refine step then names the point.
    has_coords = {"lon", "lat"}.issubset(ov.columns)
    for cui, g in ov.groupby("cui", sort=False):
        base = w[w["cui"] == cui]
        if base.empty:
            print(f"D12 WARNING: override cui {cui} not in weights frame - skipped")
            continue
        assert abs(g["share"].sum() - 1.0) < 1e-6, f"shares of {cui} != 1"
        b = base.iloc[0]
        for r in g.itertuples():
            cty = norm(r.county)
            if has_coords and pd.notna(getattr(r, "lon", None)):
                named_rows.append({"sector": r.sector, "county": cty,
                                   "lau_code": 0, "uat_name": r.firm,
                                   "lon": float(r.lon), "lat": float(r.lat),
                                   "value": b["turnover"] * r.share / 1e6})
                continue
            cand = uat_by_cty.get(cty, {})
            code = cand.get(norm(r.uat))
            if code is None:
                m2 = difflib.get_close_matches(norm(r.uat), list(cand), n=1,
                                               cutoff=0.82)
                code = cand[m2[0]] if m2 else None
            assert code is not None, f"override UAT not resolved: {r.uat} ({r.county})"
            nb = b.copy()
            nb["turnover"] = b["turnover"] * r.share
            nb["uat"], nb["county_use"] = code, cty
            rows_ov.append(nb)
        w = w[w["cui"] != cui]
    if rows_ov:
        w = pd.concat([w, pd.DataFrame(rows_ov)], ignore_index=True)
    print(f"D12/D13 overrides: {ov['cui'].nunique()} firms -> "
          f"{len(rows_ov)} UAT-level + {len(named_rows)} named exact-coordinate rows")
    grp = (w.groupby(["sec24", "county_use", "uat"])["turnover"].sum()
            .div(1e6).reset_index())
    grp = grp[grp["turnover"] > 0]
    grp["lon"] = grp["uat"].map(lambda u: pts.get(u, (None, None))[0])
    grp["lat"] = grp["uat"].map(lambda u: pts.get(u, (None, None))[1])
    n_nopt = int(grp["lon"].isna().sum())
    for i in grp.index[grp["lon"].isna()]:
        p = cty_pt.get(grp.at[i, "county_use"])
        if p is not None:
            grp.at[i, "lon"], grp.at[i, "lat"] = p.x, p.y
    grp["uat_name"] = grp["uat"].map(uat_name)
    out = grp.rename(columns={"sec24": "sector", "county_use": "county",
                              "uat": "lau_code", "turnover": "value"})
    out = out[["sector", "county", "lau_code", "uat_name", "lon", "lat", "value"]]
    out = out[out["lon"].notna()]
    if named_rows:
        out = pd.concat([out, pd.DataFrame(named_rows)[out.columns.tolist()]],
                        ignore_index=True)
    out.to_csv(OUT_UAT, index=False, float_format="%.6f")
    print(f"registry_uat_2024.csv: {len(out)} rows, "
          f"{out['sector'].nunique()} sectors, {out['lau_code'].nunique()} UATs "
          f"({n_nopt} rows county-fallback); total {out['value'].sum():,.0f} M RON")

    # ---- 2023 vs 2024 county-share drift (information only) -----------------
    f23c = f23[f23["sec"].isin(SALES_SECTORS)].groupby(["sec", "county23"])["sales23"].sum()
    f24c = w.groupby(["sec24", "county_use"])["turnover"].sum()
    corrs = []
    for s in SALES_SECTORS:
        a = f23c.get(s, pd.Series(dtype=float))
        b = f24c.get(s, pd.Series(dtype=float))
        ab = pd.concat([a / a.sum(), b / b.sum()], axis=1).fillna(0.0)
        if len(ab) > 2:
            corrs.append((s, ab.corr().iloc[0, 1], a.sum() / 1e9))
    cdf = pd.DataFrame(corrs, columns=["sector", "share_corr_23v24", "sales23_bnRON"])
    wavg = (cdf["share_corr_23v24"] * cdf["sales23_bnRON"]).sum() / cdf["sales23_bnRON"].sum()
    print(f"\ncounty-share 2023 vs 2024 correlation (sales-weighted mean "
          f"{wavg:.3f}):")
    print(cdf.round(3).to_string(index=False))

    # ---- external outputs ----------------------------------------------------
    j.drop(columns=["county_reg"]).to_csv(OUT_JOIN, index=False)
    tail = (j[j["sec24"].isin(SALES_SECTORS) & j["sales23"].notna()]
            .sort_values("sales23", ascending=False).head(100).copy())
    sect_tot = f23[f23["sec"].isin(SALES_SECTORS)].groupby("sec")["sales23"].sum()
    tail["share_of_sector_2023"] = [r.sales23 / sect_tot[r.sec24]
                                    for r in tail.itertuples()]
    tail["uat_name"] = tail["uat"].map(uat_name)
    tail[["cui", "name23", "sec24", "nace4", "emp23", "sales23", "turnover",
          "location", "uat_name", "county_use",
          "share_of_sector_2023"]].to_csv(OUT_TAIL, index=False)
    print(f"\nexternal: {OUT_JOIN.name} ({len(j)} rows), {OUT_TAIL.name} "
          f"(top {len(tail)}, {tail['share_of_sector_2023'].sum():.0f} "
          f"summed sector-shares)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
