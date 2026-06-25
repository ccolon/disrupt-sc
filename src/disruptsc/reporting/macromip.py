"""Adapter: DisruptSC run output -> macroMIP s1 submission CSV.

Transforms one experiment's raw per-step output (``firm_data.csv``,
``household_data.csv``, ``trade_data.csv`` and the run's ``parameters.yaml`` /
``run_metadata.json``) into the macroMIP long-format table: the required
variables by country x sector x year, as a real *quantity* effect and a
*monetary* equivalent, aggregated from the model's monthly steps to annual.

Variable mapping
----------------
- Output            : firm production by (country, sector). monetary = production x price.
- Value Added       : Output x VA-coefficient (1 - intermediate-input share, from the MRIO).
- GDP               : sum of Value Added over a country's sectors (whole-economy row).
- Imports / Exports : per-country cross-border flows from trade_data.csv.
- HouseholdConsumption : household tot_consumption (quantity) / tot_spending (monetary).
- Investment        : no model counterpart -> reported NA.
- PPI               : output-weighted producer price index per country (annual value/volume).
- CPI               : consumption-weighted consumer price index per country (annual value/volume).

Time: model step ``s`` (1..t_final) maps to macroMIP year ``t = (s-1)//periods_per_year``,
calendar year ``base_year + t``. ``t = 0`` is the unforced year; forcing starts at ``t = 1``.
Values are absolute (the macroMIP team derives relatives against the baseline, exp0).

Usage:
    python -m disruptsc.reporting.macromip --run-dir runs/macromip/exp3t
    python -m disruptsc.reporting.macromip --run-dir runs/macromip/exp1p --base-year 2017
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

_PERIODS_PER_YEAR = {"day": 365, "week": 52, "month": 12, "year": 1}
WHOLE_ECONOMY = "TOTAL"


# ------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------

def _read_meta(run_dir: Path) -> dict:
    mp = run_dir / "run_metadata.json"
    if not mp.exists():
        raise FileNotFoundError(f"run_metadata.json not found in {run_dir}")
    return json.loads(mp.read_text(encoding="utf-8"))


def _resolve_mrio(meta: dict) -> tuple[str, str]:
    """Return (mrio_path, monetary_units), preferring the run metadata and
    falling back to the scope config (so the adapter also works on runs whose
    metadata predates the mrio_path field)."""
    if meta.get("mrio_path"):
        return meta["mrio_path"], meta.get("monetary_units", "mUSD")
    from disruptsc import paths
    from disruptsc.config import load_config
    scope = meta.get("scope", "macroMIP")
    cfg = load_config(scope)
    return (str(paths.get_data_path(scope) / cfg["filepaths"]["mrio"]),
            cfg.get("monetary_units_in_data", "mUSD"))


def va_coefficients(meta: dict) -> dict[tuple[str, str], float]:
    """Value-added coefficient (1 - intermediate input share) per (region, sector).

    Computed from the MRIO's gross output and intermediate input, so it reflects
    the true technical structure independent of flow_coverage filtering.
    """
    from disruptsc.init_pipeline.load_data import load_mrio
    mrio_path, units = _resolve_mrio(meta)
    mrio = load_mrio(str(mrio_path), units)
    rs = list(mrio.region_sectors)
    output = mrio.get_total_output(rs).astype(float)
    inp = mrio.get_total_input(rs).astype(float)
    va = 1.0 - (inp / output.replace(0.0, np.nan))
    va = va.clip(lower=0.0, upper=1.0).fillna(0.0)
    return {(r, s): float(va.loc[(r, s)]) for (r, s) in rs}


# ------------------------------------------------------------------
# Annual aggregation helpers
# ------------------------------------------------------------------

def _year_of_step(step: pd.Series, ppy: int) -> pd.Series:
    """macroMIP year index t for model steps (1-based); step 0 (eq) -> -1."""
    return ((step - 1) // ppy).astype(int)


def build_macromip_table(run_dir: Path, base_year: int = 2017,
                         model_name: str = "DisruptSC") -> pd.DataFrame:
    run_dir = Path(run_dir)
    meta = _read_meta(run_dir)
    time_resolution = meta.get("time_resolution", "month")
    ppy = _PERIODS_PER_YEAR[time_resolution]
    exp_id = meta.get("protocol_identifier", run_dir.name)

    va_coef = va_coefficients(meta)

    # --- Firm output -> Output, Value Added, PPI ---
    firm = pd.read_csv(run_dir / "firm_data.csv")
    firm = firm[firm.time_step >= 1].copy()
    firm["year"] = _year_of_step(firm.time_step, ppy)
    firm["out_q"] = firm["production"]
    firm["out_m"] = firm["production"] * firm["price"]
    firm["vac"] = [va_coef.get((r, s), 0.0) for r, s in zip(firm.region, firm.sector)]
    firm["va_q"] = firm["out_q"] * firm["vac"]
    firm["va_m"] = firm["out_m"] * firm["vac"]

    # Sectoral rows: Output + Value Added by (country, sector, year)
    sect = (firm.groupby(["region", "sector", "year"], as_index=False)
            [["out_q", "out_m", "va_q", "va_m"]].sum())
    sect_rows = pd.DataFrame({
        "Region": sect.region, "Sector": sect.sector, "Time": sect.year,
        "Output_quantity": sect.out_q, "Output_monetary": sect.out_m,
        "ValueAdded_quantity": sect.va_q, "ValueAdded_monetary": sect.va_m,
    })

    # Country-year aggregates: GDP (= sum VA), total output, PPI
    cy = (firm.groupby(["region", "year"], as_index=False)
          [["out_q", "out_m", "va_q", "va_m"]].sum())
    cy["PPI"] = cy["out_m"] / cy["out_q"].replace(0.0, np.nan)
    country = cy.rename(columns={"region": "Region", "year": "Time"})[
        ["Region", "Time", "va_q", "va_m", "out_q", "out_m", "PPI"]]
    country = country.rename(columns={
        "va_q": "GDP_quantity", "va_m": "GDP_monetary",
        "out_q": "Output_quantity", "out_m": "Output_monetary"})

    # --- Household consumption + CPI ---
    hh = pd.read_csv(run_dir / "household_data.csv")
    hh = hh[hh.time_step >= 1].copy()
    if "region" not in hh.columns:
        hh["region"] = hh.get("household")
    hh["year"] = _year_of_step(hh.time_step, ppy)
    cons = (hh.groupby(["region", "year"], as_index=False)
            .agg(cons_q=("tot_consumption", "sum"), cons_m=("tot_spending", "sum")))
    cons["CPI"] = cons["cons_m"] / cons["cons_q"].replace(0.0, np.nan)
    country = country.merge(
        cons.rename(columns={"region": "Region", "year": "Time"}),
        on=["Region", "Time"], how="left")
    country = country.rename(columns={
        "cons_q": "HouseholdConsumption_quantity", "cons_m": "HouseholdConsumption_monetary"})

    # --- Imports / Exports ---
    trade_path = run_dir / "trade_data.csv"
    if trade_path.exists():
        tr = pd.read_csv(trade_path)
        tr = tr[tr.time_step >= 1].copy()
        tr["year"] = _year_of_step(tr.time_step, ppy)
        tr = (tr.groupby(["country", "year"], as_index=False)
              [["exports", "exports_value", "imports", "imports_value"]].sum())
        country = country.merge(
            tr.rename(columns={"country": "Region", "year": "Time",
                               "exports": "Exports_quantity", "exports_value": "Exports_monetary",
                               "imports": "Imports_quantity", "imports_value": "Imports_monetary"}),
            on=["Region", "Time"], how="left")
    else:
        logging.warning("trade_data.csv missing — Imports/Exports left blank")

    # Investment has no model counterpart.
    country["Investment_quantity"] = np.nan
    country["Investment_monetary"] = np.nan
    country["Sector"] = WHOLE_ECONOMY

    # --- Assemble long table ---
    out = pd.concat([country, sect_rows], ignore_index=True)
    out.insert(0, "Experiment", exp_id)
    out["Ensemble"] = "NA"
    out["Time"] = out["Time"].astype(int)
    out["Year"] = base_year + out["Time"]

    var_cols = [
        "GDP_quantity", "GDP_monetary",
        "Output_quantity", "Output_monetary",
        "ValueAdded_quantity", "ValueAdded_monetary",
        "Imports_quantity", "Imports_monetary",
        "Exports_quantity", "Exports_monetary",
        "HouseholdConsumption_quantity", "HouseholdConsumption_monetary",
        "Investment_quantity", "Investment_monetary",
        "CPI", "PPI",
    ]
    for c in var_cols:
        if c not in out.columns:
            out[c] = np.nan
    cols = ["Experiment", "Time", "Year", "Region", "Sector", "Ensemble"] + var_cols
    out = out[cols].sort_values(["Region", "Sector", "Time"]).reset_index(drop=True)
    return out


def main():
    p = argparse.ArgumentParser(description="DisruptSC -> macroMIP s1 submission adapter")
    p.add_argument("--run-dir", required=True, type=Path, help="experiment output folder")
    p.add_argument("--out", type=Path, default=None, help="output CSV (default: <run-dir>/<id>-DisruptSC.csv)")
    p.add_argument("--base-year", type=int, default=2017)
    p.add_argument("--model-name", default="DisruptSC")
    p.add_argument("--log-level", default="info", choices=["info", "debug"])
    args = p.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format="%(asctime)s - %(levelname)s - %(message)s")

    table = build_macromip_table(args.run_dir, base_year=args.base_year,
                                 model_name=args.model_name)
    meta = _read_meta(args.run_dir)
    exp_id = meta.get("protocol_identifier", args.run_dir.name)
    out_path = args.out or (args.run_dir / f"{exp_id}-{args.model_name}.csv")
    table.to_csv(out_path, index=False)
    logging.info(f"Wrote {len(table)} rows -> {out_path}")


if __name__ == "__main__":
    main()
