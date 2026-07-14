"""Adapter: canonical canton x IO-sector capital-destruction shock -> DisruptSC model-ready shock.

The canonical shock (canton_io_destroyed_capital.csv) keys cantones by *numeric DPA code*
(e.g. 1301 = Manabi-Portoviejo) and IO sectors by trigram (INM, EDU, ...). The DisruptSC
Ecuador model keys firms by the *string* `subregion_canton` = "PROVINCE - CANTON" (e.g.
"MANABI - PORTOVIEJO") and `sector` = trigram.

This script reconciles the two canton namespaces (including the fact that the model still
files Santo Domingo under the pre-2007 "PICHINCHA - SANTO DOMINGO", and minor spelling
differences like RIOVERDE -> RIO VERDE), and emits a model-ready long CSV:

    subregion_canton, sector, destroyed_capital_mUSD     (exact model strings)

All name reconciliation lives HERE (offline + auditable). The model core then does a trivial
exact (subregion_canton, sector) match against live firms.

It does NOT modify the canonical CSV. Run with the dsc env python.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

# --- Paths (edit if the machine layout changes) -----------------------------
DAMAGES = Path(r"C:\Users\Celian\OneDrive\WorldBank\Ecuador\Analysis\Earthquake\Damages")
DATA = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc-data\Ecuador")
OUT_DIR = Path(__file__).resolve().parent / "additional_data"

SHOCK_CSV = DAMAGES / "canton_io_destroyed_capital.csv"      # region(code), io_sector, destroyed_capital_M_USD
CANTON_TOTALS = DAMAGES / "canton_totals.csv"                # region(code), canton_name, province
FIRMS_GEOJSON = DATA / "Spatial" / "firms.geojson"           # subregion_canton, canton_name, subregion_province, <sector outputs>

PREFIX_MIN_LEN = 6  # minimum normalized length for a prefix/contains canton match


def norm(x: object) -> str:
    """Uppercase, de-accent, fix the latin-1 n-tilde mojibake, drop non-alphanumerics.

    Spaces are removed so "RIO VERDE" and "RIOVERDE" collapse to the same key.
    Used ONLY for matching; outputs always use the exact model string.
    """
    if x is None:
        return ""
    s = str(x).replace("�", "N")  # mojibake n-tilde (CA?AR -> CANAR)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def build_model_canton_index(firms: gpd.GeoDataFrame) -> dict:
    """Return matcher structures keyed off the model's exact subregion_canton strings."""
    rows = firms[["subregion_canton", "canton_name", "subregion_province"]].drop_duplicates()
    by_pc = {}        # (norm_province, norm_canton) -> exact subregion_canton
    by_canton = {}    # norm_canton -> set of exact subregion_canton
    exact_strings = set()
    for r in rows.itertuples():
        exact = r.subregion_canton
        exact_strings.add(exact)
        nprov, ncant = norm(r.subregion_province), norm(r.canton_name)
        by_pc[(nprov, ncant)] = exact
        by_canton.setdefault(ncant, set()).add(exact)
    return {"by_pc": by_pc, "by_canton": by_canton, "exact": exact_strings}


def match_canton(province: str, canton: str, idx: dict) -> tuple[str | None, str]:
    """Map a shock (province, canton_name) to an exact model subregion_canton.

    Returns (exact_string_or_None, method). Staged: province+canton exact ->
    canton-only (unique) -> prefix/contains (unique). Ambiguous or no match -> None.
    """
    nprov, ncant = norm(province), norm(canton)

    # 1. exact province + canton
    if (nprov, ncant) in idx["by_pc"]:
        return idx["by_pc"][(nprov, ncant)], "exact"

    # 2. canton name only (handles admin reassignment, e.g. Santo Domingo under Pichincha)
    cands = idx["by_canton"].get(ncant)
    if cands and len(cands) == 1:
        return next(iter(cands)), "canton_only"
    if cands and len(cands) > 1:
        return None, f"ambiguous_canton({len(cands)})"

    # 3. prefix / contains (handles "SANTO DOMINGO" vs "SANTO DOMINGO DE LOS TSACHILAS")
    if len(ncant) >= PREFIX_MIN_LEN:
        hits = []
        for mcant, exacts in idx["by_canton"].items():
            if len(mcant) < PREFIX_MIN_LEN:
                continue
            if mcant.startswith(ncant) or ncant.startswith(mcant):
                hits.extend(exacts)
        hits = sorted(set(hits))
        if len(hits) == 1:
            return hits[0], "prefix"
        if len(hits) > 1:
            return None, f"ambiguous_prefix({len(hits)})"

    return None, "no_match"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shock = pd.read_csv(SHOCK_CSV)
    totals = pd.read_csv(CANTON_TOTALS)
    firms = gpd.read_file(FIRMS_GEOJSON)

    grand_total = float(shock["destroyed_capital_M_USD"].sum())

    # model sector availability per canton (output > 0 in the geojson)
    mrio_sectors = [c for c in firms.columns if isinstance(c, str) and len(c) == 3 and c.isupper()]
    cell = firms.melt(id_vars=["subregion_canton"], value_vars=mrio_sectors,
                      var_name="sector", value_name="out")
    cell = cell[(cell["out"].notna()) & (cell["out"] > 0)]
    model_cells = set(zip(cell["subregion_canton"], cell["sector"]))
    model_sectors = set(mrio_sectors)

    idx = build_model_canton_index(firms)

    # crosswalk: shock region code -> (exact model canton, method)
    code2pc = {int(r.region): (r.province, r.canton_name) for r in totals.itertuples()}
    region2canton, region2method = {}, {}
    for code, (prov, cant) in code2pc.items():
        exact, method = match_canton(prov, cant, idx)
        region2canton[code] = exact
        region2method[code] = method

    shock = shock.copy()
    shock["region"] = shock["region"].astype(int)
    shock["subregion_canton"] = shock["region"].map(region2canton)
    shock["sector"] = shock["io_sector"]
    shock["method"] = shock["region"].map(region2method)

    # --- diagnostics ---
    mapped = shock[shock["subregion_canton"].notna()].copy()
    canton_mapped_usd = float(mapped["destroyed_capital_M_USD"].sum())

    mapped["cell_ok"] = [(c, s) in model_cells for c, s in zip(mapped["subregion_canton"], mapped["sector"])]
    cell_usd = float(mapped.loc[mapped["cell_ok"], "destroyed_capital_M_USD"].sum())

    sector_missing = sorted(set(shock["sector"]) - model_sectors)

    # unmapped cantones (no model canton)
    unmapped = (shock[shock["subregion_canton"].isna()]
                .groupby("region")["destroyed_capital_M_USD"].sum().sort_values(ascending=False))
    unmapped_names = {int(c): code2pc[int(c)] for c in unmapped.index}

    # mapped-but-no-firm-cell (canton in model, sector has no output there)
    no_cell = (mapped[~mapped["cell_ok"]].groupby("sector")["destroyed_capital_M_USD"]
               .sum().sort_values(ascending=False))

    # which shock cantones used a non-exact method (audit)
    nonexact = {int(c): {"canton": code2pc[int(c)], "method": m, "matched_to": region2canton[int(c)]}
                for c, m in region2method.items() if m not in ("exact",) and region2canton.get(int(c))}

    # --- write model-ready shock (only rows that map to a model canton) ---
    out = (mapped.groupby(["subregion_canton", "sector"], as_index=False)["destroyed_capital_M_USD"]
           .sum().rename(columns={"destroyed_capital_M_USD": "destroyed_capital_mUSD"}))
    out = out.sort_values(["subregion_canton", "sector"]).reset_index(drop=True)
    out_path = OUT_DIR / "earthquake_shock_modelready.csv"
    out.to_csv(out_path, index=False)

    report = {
        "grand_total_mUSD": round(grand_total, 2),
        "canton_mapped_mUSD": round(canton_mapped_usd, 2),
        "canton_mapped_pct": round(100 * canton_mapped_usd / grand_total, 2),
        "firm_cell_available_mUSD": round(cell_usd, 2),
        "firm_cell_available_pct": round(100 * cell_usd / grand_total, 2),
        "n_model_ready_rows": int(len(out)),
        "n_cantones_mapped": int(mapped["subregion_canton"].nunique()),
        "sectors_in_shock_not_in_model": sector_missing,
        "unmapped_canton_total_mUSD": round(float(unmapped.sum()), 2),
        "unmapped_top": {f"{unmapped_names[c][1]} ({unmapped_names[c][0]})": round(float(v), 2)
                         for c, v in unmapped.head(8).items()},
        "mapped_no_firm_cell_total_mUSD": round(float(no_cell.sum()), 2),
        "mapped_no_firm_cell_top_sectors": {s: round(float(v), 2) for s, v in no_cell.head(8).items()},
        "non_exact_canton_matches": nonexact,
        "output_csv": str(out_path),
    }
    with open(OUT_DIR / "shock_adapter_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # --- console summary ---
    print(f"Grand total shock:                 ${grand_total:,.1f}M")
    print(f"Mapped to a model canton:          ${canton_mapped_usd:,.1f}M  ({report['canton_mapped_pct']}%)")
    print(f"Lands on a firm cell (pre-filter): ${cell_usd:,.1f}M  ({report['firm_cell_available_pct']}%)")
    print(f"Model-ready rows:                  {len(out)}  across {report['n_cantones_mapped']} cantones")
    print(f"\nUnmapped (canton not in model):    ${unmapped.sum():,.1f}M")
    for c, v in unmapped.head(6).items():
        nm = unmapped_names[int(c)]
        print(f"    {nm[1]} ({nm[0]}) [{region2method[int(c)]}]: ${v:,.2f}M")
    print(f"\nMapped but no firm cell:           ${no_cell.sum():,.1f}M  (top sectors)")
    for s, v in no_cell.head(6).items():
        print(f"    {s}: ${v:,.2f}M")
    if nonexact:
        print(f"\nNon-exact canton matches ({len(nonexact)}) [audit]:")
        for c, d in list(nonexact.items())[:12]:
            print(f"    {d['canton'][1]} ({d['canton'][0]}) --{d['method']}--> {d['matched_to']}")
    if sector_missing:
        print(f"\nWARNING shock sectors absent from model: {sector_missing}")
    print(f"\nWrote {out_path}")
    print(f"Wrote {OUT_DIR / 'shock_adapter_report.json'}")


if __name__ == "__main__":
    main()
