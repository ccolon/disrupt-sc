"""Validate a Phase-1 earthquake run against the smoke-test criteria.

Checks:
  1. Total household consumption loss is non-zero and order-of-magnitude sane
     (the idealized homogeneous run used a ~$2.51B shock; ours is $2.44B).
  2. Losses concentrate in the affected provinces (Manabi, Esmeraldas, and the
     model's Santo Domingo canton, which it files under PICHINCHA).
  3. The per-step household-loss trajectory is monotonic (no reconstruction ->
     losses grow to a plateau, they don't oscillate or recover).

Also emits a per-canton loss CSV and a 2-panel sanity figure.

Usage:
    python runs/earthquake/validate_phase1.py runs/earthquake/V1/seed_0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

AFFECTED_PROVINCES = {"MANABI", "ESMERALDAS"}          # + model's PICHINCHA-Santo Domingo
SANTO_DOMINGO_CANTON = "PICHINCHA - SANTO DOMINGO"


def load_run(run_dir: Path):
    hh = pd.read_csv(run_dir / "household_data.csv")
    ht = gpd.read_file(run_dir / "household_table.geojson")
    ht = pd.DataFrame(ht.drop(columns=[c for c in ["geometry"] if c in ht.columns]))
    # household pid in data is "hh_<id>"
    ht["household"] = "hh_" + ht["id"].astype(str)
    keep = [c for c in ["household", "subregion_canton", "subregion_province", "population"] if c in ht.columns]
    hh = hh.merge(ht[keep], on="household", how="left")
    hh["loss"] = hh["consumption_loss"].fillna(0.0) + hh["extra_spending"].fillna(0.0)
    return hh


def main():
    run_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/earthquake/V1/seed_0")
    out = {}

    # --- headline totals -----------------------------------------------------
    ls_path = run_dir / "loss_summary.csv"
    if ls_path.exists():
        ls = pd.read_csv(ls_path)
        out["household_loss_total_mUSD"] = round(float(ls["households"].iloc[0]), 2)
        out["country_loss_total_mUSD"] = round(float(ls["countries"].iloc[0]), 2)

    hh = load_run(run_dir)
    t_max = int(hh["time_step"].max())
    out["t_final"] = t_max

    cl_total = float(hh["consumption_loss"].sum())
    es_total = float(hh["extra_spending"].sum())
    out["cumulative_consumption_loss_mUSD"] = round(cl_total, 2)
    out["cumulative_extra_spending_mUSD"] = round(es_total, 2)
    out["cumulative_total_loss_mUSD"] = round(cl_total + es_total, 2)

    # --- (2) spatial concentration ------------------------------------------
    by_prov = (hh.groupby("subregion_province")["loss"].sum().sort_values(ascending=False))
    tot = by_prov.sum()
    out["loss_by_province_top"] = {k: round(float(v), 2) for k, v in by_prov.head(8).items()}
    affected = by_prov[by_prov.index.isin(AFFECTED_PROVINCES)].sum()
    sd = float(hh.loc[hh["subregion_canton"] == SANTO_DOMINGO_CANTON, "loss"].sum())
    out["affected_share_pct"] = round(100 * (affected + sd) / tot, 2) if tot else 0.0
    out["manabi_share_pct"] = round(100 * float(by_prov.get("MANABI", 0.0)) / tot, 2) if tot else 0.0

    by_canton = (hh.groupby(["subregion_province", "subregion_canton"])["loss"].sum()
                 .sort_values(ascending=False))
    out["loss_by_canton_top10"] = {f"{c}": round(float(v), 2) for (_, c), v in by_canton.head(10).items()}

    # per-canton CSV
    by_canton.reset_index().rename(columns={"loss": "cumulative_loss_mUSD"}).to_csv(
        run_dir / "loss_by_canton.csv", index=False)

    # --- (3) monotonicity ----------------------------------------------------
    per_t = hh.groupby("time_step")["loss"].sum().sort_index()
    post = per_t[per_t.index >= 1]
    diffs = post.diff().dropna()
    # allow tiny numerical wiggle relative to the peak step
    tol = 1e-6 * max(abs(post.max()), 1.0)
    n_decreasing = int((diffs < -tol).sum())
    out["per_step_loss_first"] = round(float(post.iloc[0]), 4) if len(post) else 0.0
    out["per_step_loss_last"] = round(float(post.iloc[-1]), 4) if len(post) else 0.0
    out["per_step_loss_max"] = round(float(post.max()), 4) if len(post) else 0.0
    out["monotonic_nondecreasing"] = bool(n_decreasing == 0)
    out["n_steps_decreasing"] = n_decreasing

    # --- verdicts ------------------------------------------------------------
    out["CHECK_loss_nonzero"] = bool((cl_total + es_total) > 0)
    out["CHECK_loss_order_of_magnitude_billions"] = bool(1e2 <= (cl_total + es_total) <= 1e5)
    out["CHECK_concentrated_in_affected"] = bool(out["affected_share_pct"] >= 50.0)
    out["CHECK_monotonic"] = out["monotonic_nondecreasing"]

    print(json.dumps(out, indent=2))
    with open(run_dir / "phase1_validation.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    # --- figure --------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
        axes[0].plot(per_t.index, per_t.values, color="#b2182b")
        axes[0].set_title("Household loss per day (V1: no substitution, no reconstruction)")
        axes[0].set_xlabel("day"); axes[0].set_ylabel("loss (mUSD/day)")
        axes[0].axvline(1, color="grey", ls="--", lw=0.8)

        top = by_prov.head(8)[::-1]
        axes[1].barh(top.index, top.values, color="#2166ac")
        axes[1].set_title("Cumulative household loss by province")
        axes[1].set_xlabel("loss (mUSD)")
        fig.tight_layout()
        fig.savefig(run_dir / "phase1_sanity.png", dpi=120)
        print(f"\nWrote {run_dir/'phase1_sanity.png'}")
    except Exception as exc:  # noqa: BLE001
        print(f"(figure skipped: {exc})")

    print(f"Wrote {run_dir/'loss_by_canton.csv'} and {run_dir/'phase1_validation.json'}")


if __name__ == "__main__":
    main()
