"""Aggregate GDP / welfare loss from a DisruptSC earthquake run.

GDP loss = cumulative value-added loss (production side):

    va_share(sector) = mrio_va / mrio_output              (mrio_by_sector.csv)
    va_loss(f, t)    = (production(f, 0) - production(f, t)) * va_share(sector(f))
    GDP_loss         = sum over t>=1, over firms, of va_loss

Reported as absolute mUSD, % of annual GDP (annual VA = baseline step VA x
periods_per_year), gross loss (shortfalls only, ignoring recovery over-shoot),
and the model's native household + country final-demand loss (loss_summary.csv,
an expenditure-side cross-check). Emits one tidy row so many runs stack into a
sensitivity table.

CLI:
    python aggregate_gdp.py <run_dir> [--out row.csv] [--label NAME]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

DAYS_PER_STEP = {"day": 1, "week": 7, "month": 30, "year": 365}
SWEEP_KEYS = ["flow_coverage", "utilization_rate", "nb_suppliers_per_input",
              "time_resolution", "t_final", "with_transport", "rationing_mode"]
DISR_KEYS = ["reconstruction_market", "reconstruction_public_share",
             "reconstruction_target_time", "reconstruction_lag"]


def compute_gdp_loss(run_dir: str | Path) -> dict:
    run_dir = Path(run_dir)
    fd = pd.read_csv(run_dir / "firm_data.csv",
                     usecols=["time_step", "firm", "sector", "production", "total_input"])
    mrio = pd.read_csv(run_dir / "mrio_by_sector.csv")
    with open(run_dir / "parameters.yaml") as f:
        params = yaml.unsafe_load(f)

    ppy = 365.0 / DAYS_PER_STEP.get(params.get("time_resolution", "month"), 30)

    # value-added share per sector, mapped onto firms
    va_share = (mrio.mrio_va / mrio.mrio_output.replace(0, np.nan))
    va_share = dict(zip(mrio.sector, va_share))
    fd["va_share"] = fd.sector.map(va_share).fillna(0.0)

    eq = fd.loc[fd.time_step == 0].set_index("firm").production          # baseline output per firm
    fd["eq_prod"] = fd.firm.map(eq)
    fd["va_loss"] = (fd["eq_prod"] - fd["production"]) * fd["va_share"]

    post = fd.loc[fd.time_step >= 1]                                     # exclude the t=0 baseline step
    gdp_loss = float(post.va_loss.sum())                                # net (recovery over-shoot nets off)
    gdp_loss_gross = float(post.va_loss.clip(lower=0).sum())            # shortfalls only

    firms = fd.drop_duplicates("firm")
    baseline_step_va = float((firms["eq_prod"] * firms["va_share"]).sum())
    annual_gdp = baseline_step_va * ppy
    pct = 100.0 * gdp_loss / annual_gdp if annual_gdp else float("nan")
    pct_gross = 100.0 * gdp_loss_gross / annual_gdp if annual_gdp else float("nan")

    # expenditure-side cross-check (model native)
    hh_loss = cty_loss = gov_loss = inv_loss = float("nan")
    ls = run_dir / "loss_summary.csv"
    if ls.exists():
        s = pd.read_csv(ls)
        hh_loss = float(s.get("households", pd.Series([np.nan])).iloc[0])
        cty_loss = float(s.get("countries", pd.Series([np.nan])).iloc[0])
        # Separate national final-demand agents (post C/G/I split); NaN for bundled MRIOs.
        gov_loss = float(s.get("government", pd.Series([np.nan])).iloc[0])
        inv_loss = float(s.get("investment", pd.Series([np.nan])).iloc[0])

    hh_pct = 100.0 * hh_loss / annual_gdp if annual_gdp else float("nan")

    disr = (params.get("disruptions") or [{}])[0]
    row = {"run_id": run_dir.name,
           # headline: household welfare loss as % of annual GDP (private consumption only)
           "household_loss_pct_annual_gdp": round(hh_pct, 4),
           "household_loss_mUSD": round(hh_loss, 3),
           # separate accounting metrics (not welfare): public-service + investment shortfall
           "government_loss_mUSD": round(gov_loss, 3),
           "government_loss_pct_annual_gdp": round(100.0 * gov_loss / annual_gdp, 4) if annual_gdp else float("nan"),
           "investment_loss_mUSD": round(inv_loss, 3),
           "investment_loss_pct_annual_gdp": round(100.0 * inv_loss / annual_gdp, 4) if annual_gdp else float("nan"),
           # production-side value-added loss (cross-check; amplified by the cascade)
           "gdp_loss_pct_annual_gdp": round(pct, 4),
           "gdp_loss_mUSD": round(gdp_loss, 3),
           "gdp_loss_gross_pct": round(pct_gross, 4),
           "annual_gdp_mUSD": round(annual_gdp, 1),
           "country_loss_mUSD": round(cty_loss, 3),
           "n_steps": int(fd.time_step.max())}
    row.update({k: params.get(k) for k in SWEEP_KEYS})
    row.update({k: disr.get(k) for k in DISR_KEYS})
    return row


def main():
    p = argparse.ArgumentParser(description="Aggregate GDP/welfare loss from a run")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--out", type=Path, default=None, help="append the row to this CSV")
    p.add_argument("--label", default=None, help="override run_id label")
    args = p.parse_args()

    row = compute_gdp_loss(args.run_dir)
    if args.label:
        row["run_id"] = args.label
    print(json.dumps(row, indent=2, default=str))

    if args.out:
        df = pd.DataFrame([row])
        header = not args.out.exists()
        args.out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out, mode="a", header=header, index=False)
        print(f"\n-> appended to {args.out}")


if __name__ == "__main__":
    main()
