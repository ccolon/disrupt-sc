"""Temporal/sectoral + spatial decomposition of HOUSEHOLD loss (% of annual GDP).

Household consumption loss:
  by sector x time : loss_per_region_sector_time.csv  (region_sector -> ISIC group)
  by province      : household_data.csv consumption_loss, by household province
normalized by annual GDP (production-side VA x periods_per_year), so both the
left-panel area and each province read as % of annual GDP.

Emits (into --out-dir, default <run_dir>):
  loss_by_sector_time.csv    : isic x time_step -> household_loss_mUSD, pct_gdp
  loss_by_province_year.csv  : province -> household_loss_mUSD, pct_gdp, share_pct

CLI:  python distribution.py <run_dir> [--out-dir DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import yaml

DAYS_PER_STEP = {"day": 1, "week": 7, "month": 30, "year": 365}
CROSSWALK = {
    "A": {"BNA","CAN","CER","FRT","FRV","GAN","PES","SIL"},
    "C": {"AYG","AZU","BAL","CAR","CAU","CEM","CHO","CIN","CUE","HIL","LAC","MAD","MAN","MAQ",
          "MET","MOL","MUE","PAN","PAP","PLS","QU1","QU2","TAB","VES","VID","REF","ALD"},
    "DE": {"ELE","AGU"}, "F": {"CON"}, "G": {"COM"}, "H": {"TRA"}, "I": {"HOT","RES"},
    "K": {"FIN","SEG"}, "O": {"ADP"},
}
SEC2ISIC = {s: g for g, ss in CROSSWALK.items() for s in ss}
ISIC_LABEL = {"A": "Agriculture", "C": "Manufacturing", "DE": "Utilities", "F": "Construction",
              "G": "Trade", "H": "Transport", "I": "Accommodation", "K": "Finance",
              "O": "Public admin", "J-U": "Other services", "IMP": "Imports"}


def isic_of_region_sector(rs: str) -> str:
    if str(rs).endswith("_imports"):
        return "IMP"
    tri = rs[4:] if str(rs).startswith("ECU_") else rs
    return SEC2ISIC.get(tri, "J-U")


def annual_gdp_mUSD(run_dir: Path, ppy: float) -> float:
    """Production-side annual GDP = sum(eq_production * va_share) * periods_per_year."""
    fd = pd.read_csv(run_dir / "firm_data.csv", usecols=["time_step", "firm", "sector", "production"])
    mrio = pd.read_csv(run_dir / "mrio_by_sector.csv")
    vs = dict(zip(mrio.sector, mrio.mrio_va / mrio.mrio_output.replace(0, np.nan)))
    eq = fd.loc[fd.time_step == 0].copy()
    eq["va"] = eq.sector.map(vs).fillna(0.0) * eq.production
    return float(eq.va.sum()) * ppy


def main():
    p = argparse.ArgumentParser(description="Household-loss sectoral/temporal + spatial decomposition")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()
    out_dir = args.out_dir or args.run_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.run_dir / "parameters.yaml") as f:
        params = yaml.unsafe_load(f)
    ppy = 365.0 / DAYS_PER_STEP.get(params.get("time_resolution", "month"), 30)
    G = annual_gdp_mUSD(args.run_dir, ppy)

    # --- LEFT: household loss by sector x time ---
    lrst = pd.read_csv(args.run_dir / "loss_per_region_sector_time.csv")
    lrst = lrst.loc[lrst.time_step >= 1].copy()
    lrst["isic"] = lrst.sector.map(isic_of_region_sector)
    st = (lrst.groupby(["isic", "time_step"]).loss.sum().reset_index()
              .rename(columns={"loss": "household_loss_mUSD"}))
    st["pct_gdp"] = 100.0 * st.household_loss_mUSD / G
    st["sector_label"] = st.isic.map(ISIC_LABEL).fillna(st.isic)
    st.to_csv(out_dir / "loss_by_sector_time.csv", index=False)

    # --- MAP: household loss by province AND canton (cumulative) ---
    # The model is one household per canton, so canton is the native resolution and
    # province is an aggregation up. We emit both; plot_distribution uses the canton one.
    hd = pd.read_csv(args.run_dir / "household_data.csv",
                     usecols=lambda c: c in {"time_step", "household", "consumption_loss", "agent_type"})
    hd = hd.loc[hd.time_step >= 1]
    if "agent_type" in hd.columns:  # welfare = households only (exclude gov/investment agents)
        hd = hd.loc[hd.agent_type == "household"]
    ht = gpd.read_file(args.run_dir / "household_table.geojson")[
        ["household", "subregion_province", "subregion_canton", "canton_name"]]
    geo = hd.merge(ht, on="household", how="left")

    pv = (geo.groupby("subregion_province").consumption_loss.sum().reset_index()
              .rename(columns={"subregion_province": "province", "consumption_loss": "household_loss_mUSD"})
              .sort_values("household_loss_mUSD", ascending=False))
    pv["pct_gdp"] = 100.0 * pv.household_loss_mUSD / G
    pv["share_pct"] = 100.0 * pv.household_loss_mUSD / pv.household_loss_mUSD.sum()
    pv.to_csv(out_dir / "loss_by_province_year.csv", index=False)

    # canton: keep province + canton_name so the map can join on (province, canton).
    cv = (geo.groupby(["subregion_canton", "subregion_province", "canton_name"]).consumption_loss.sum()
             .reset_index()
             .rename(columns={"subregion_canton": "canton", "subregion_province": "province",
                              "consumption_loss": "household_loss_mUSD"})
             .sort_values("household_loss_mUSD", ascending=False))
    cv["pct_gdp"] = 100.0 * cv.household_loss_mUSD / G
    cv["share_pct"] = 100.0 * cv.household_loss_mUSD / cv.household_loss_mUSD.sum()
    cv.to_csv(out_dir / "loss_by_canton_year.csv", index=False)

    print(f"annual GDP: {G:,.0f} mUSD")
    print(f"total household loss: {pv.household_loss_mUSD.sum():,.1f} mUSD = {100*pv.household_loss_mUSD.sum()/G:.2f}% of GDP")
    print(f"top cantons:\n{cv.head(6)[['canton','pct_gdp','share_pct']].to_string(index=False)}")
    print(f"\n-> {out_dir/'loss_by_sector_time.csv'}\n-> {out_dir/'loss_by_province_year.csv'}"
          f"\n-> {out_dir/'loss_by_canton_year.csv'}")


if __name__ == "__main__":
    main()
