"""Post-processing for the 2016 Ecuador earthquake ensemble.

Reads per-(variant, seed) run folders produced by scripts/run_earthquake.py and
emits two CSV families per variant:

  Phase 3 (canton view):
    <variant>/aggregates.csv      - per-seed totals/peak/timing + across-seed mean & quantiles
    <variant>/loss_by_canton.csv  - per-canton mean & 25/50/75 loss across seeds

  Phase 4 (UQ-aligned view):
    <variant>/uq_aligned.csv      - mmi_bin x isic_group x outcome x window
                                    with mean/q25/q50/q75 across seeds, in both
                                    percent and log-points vs the pre-shock state.

Mappings (documented so they can be revisited):
  * "sales"     <- firm production (output)        [firm_data.csv: production]
  * "purchases" <- firm realized input deliveries  [firm_data.csv: total_input]
  * isic_group  <- IO-59 trigram via CROSSWALK below (task Table A.2 draft)
  * mmi_bin     <- per-canton MMI from canton_mmi_bin.csv if present, else "unknown"
  * % change / log-points are relative to each firm's own t=0 (pre-shock) value.

Windows (shock at day 1): acute = days 1..60, recovery = days 61..365. Clipped to
the available horizon (smoke runs are shorter), and reported only if non-empty.

Usage:
    python runs/earthquake/postprocess.py V1            # one variant
    python runs/earthquake/postprocess.py V1 V2 V3 V4   # several
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent       # studies/earthquake (study code + shock data)
REPO_ROOT = STUDY_DIR.parents[1]                  # repo root
RUNS_ROOT = REPO_ROOT / "runs" / "earthquake"     # run OUTPUTS live here (the driver writes them)
# Optional UQ input: region (model subregion_canton or canton code), mmi_bin.
CANTON_MMI = STUDY_DIR / "_shock" / "canton_mmi_bin.csv"

SHOCK_DAY = 1
ACUTE = (1, 60)
RECOVERY = (61, 365)

# IO-59 trigram -> ISIC-10 group (draft crosswalk from the task; revisit as needed).
CROSSWALK = {
    "A": ["BNA", "CAN", "CER", "FRT", "FRV", "GAN", "PES", "SIL"],
    "C": ["AYG", "AZU", "BAL", "CAR", "CAU", "CEM", "CHO", "CIN", "CUE", "HIL",
          "LAC", "MAD", "MAN", "MAQ", "MET", "MOL", "MUE", "PAN", "PAP", "PLS",
          "QU1", "QU2", "TAB", "VES", "VID", "REF", "ALD"],
    "DE": ["ELE", "AGU"],
    "F": ["CON"],
    "G": ["COM"],
    "H": ["TRA"],
    "I": ["HOT", "RES"],
    "J-U": ["EDU", "SAL", "CUL", "TEL", "INM", "FIN", "SEG", "ADM", "ADP", "ASO",
            "POS", "REP", "DOM", "MIP", "PPR", "FID", "DEM"],
}
SECTOR_TO_ISIC = {s: g for g, secs in CROSSWALK.items() for s in secs}


def sector_to_isic(sec: str) -> str:
    return SECTOR_TO_ISIC.get(sec, "J-U")  # default remaining services to other


def _seed_dirs(variant_dir: Path) -> list[Path]:
    return sorted(d for d in variant_dir.glob("seed_*") if (d / "firm_data.csv").exists())


def load_firm_ts(run_dir: Path) -> pd.DataFrame:
    """Firm time series joined with canton + ISIC group; adds pct/log vs t=0."""
    df = pd.read_csv(run_dir / "firm_data.csv")
    ft = gpd.read_file(run_dir / "firm_table.geojson")
    ft = pd.DataFrame(ft.drop(columns=[c for c in ["geometry"] if c in ft.columns]))
    cols = [c for c in ["id", "subregion_canton", "subregion_province", "sector"] if c in ft.columns]
    ft = ft[cols].rename(columns={"sector": "sector_tbl"})
    df = df.merge(ft, left_on="firm", right_on="id", how="left")
    df["sector"] = df["sector"].fillna(df.get("sector_tbl"))
    df["isic_group"] = df["sector"].map(sector_to_isic)
    base = (df[df["time_step"] == 0]
            .set_index("firm")[["production", "total_input"]]
            .rename(columns={"production": "prod0", "total_input": "inp0"}))
    df = df.merge(base, on="firm", how="left")
    return df


def load_hh_ts(run_dir: Path) -> pd.DataFrame:
    hh = pd.read_csv(run_dir / "household_data.csv")
    ht = gpd.read_file(run_dir / "household_table.geojson")
    ht = pd.DataFrame(ht.drop(columns=[c for c in ["geometry"] if c in ht.columns]))
    ht["household"] = "hh_" + ht["id"].astype(str)
    keep = [c for c in ["household", "subregion_canton", "subregion_province", "population"] if c in ht.columns]
    hh = hh.merge(ht[keep], on="household", how="left")
    hh["loss"] = hh["consumption_loss"].fillna(0.0) + hh["extra_spending"].fillna(0.0)
    return hh


def load_canton_mmi() -> dict:
    if CANTON_MMI.exists():
        m = pd.read_csv(CANTON_MMI)
        key = "subregion_canton" if "subregion_canton" in m.columns else m.columns[0]
        return dict(zip(m[key], m["mmi_bin"]))
    return {}


# ---------------------------------------------------------------------------
# Phase 3 — canton view
# ---------------------------------------------------------------------------

def seed_aggregate(run_dir: Path) -> dict:
    hh = load_hh_ts(run_dir)
    per_t = hh.groupby("time_step")["loss"].sum().sort_index()
    post = per_t[per_t.index >= SHOCK_DAY]
    total = float(hh["loss"].sum())
    peak = float(post.max()) if len(post) else 0.0
    t_peak = int(post.idxmax()) if len(post) else -1
    # time-to-recovery: first day after peak where daily loss <= 5% of peak
    t_rec = -1
    if len(post) and peak > 0:
        after = post[post.index >= t_peak]
        rec = after[after <= 0.05 * peak]
        t_rec = int(rec.index[0]) if len(rec) else -1
    return {"total_loss_mUSD": total, "peak_daily_loss_mUSD": peak,
            "time_to_peak_day": t_peak, "time_to_recovery_day": t_rec,
            "t_final": int(per_t.index.max())}


def phase3(variant_dir: Path) -> None:
    seeds = _seed_dirs(variant_dir)
    if not seeds:
        print(f"  [phase3] no seed runs in {variant_dir}")
        return
    rows = []
    canton_frames = []
    for d in seeds:
        agg = seed_aggregate(d)
        agg["seed"] = int(d.name.split("_")[1])
        rows.append(agg)
        hh = load_hh_ts(d)
        cf = hh.groupby("subregion_canton")["loss"].sum().rename(agg["seed"])
        canton_frames.append(cf)
    per_seed = pd.DataFrame(rows).set_index("seed").sort_index()

    # across-seed mean + quantiles
    summary = {}
    for col in ["total_loss_mUSD", "peak_daily_loss_mUSD", "time_to_peak_day", "time_to_recovery_day"]:
        summary[f"{col}_mean"] = per_seed[col].mean()
        for q in (0.25, 0.5, 0.75):
            summary[f"{col}_q{int(q*100)}"] = per_seed[col].quantile(q)
    summary["n_seeds"] = len(seeds)
    out = pd.concat([per_seed, pd.DataFrame([summary], index=["__across_seeds__"])], axis=0)
    out.to_csv(variant_dir / "aggregates.csv")

    # canton-level loss: mean + quantiles across seeds
    cf = pd.concat(canton_frames, axis=1)
    canton = pd.DataFrame({
        "mean_loss_mUSD": cf.mean(axis=1),
        "q25": cf.quantile(0.25, axis=1),
        "q50": cf.quantile(0.50, axis=1),
        "q75": cf.quantile(0.75, axis=1),
    }).sort_values("mean_loss_mUSD", ascending=False)
    canton.to_csv(variant_dir / "loss_by_canton.csv")
    print(f"  [phase3] {variant_dir.name}: {len(seeds)} seed(s); "
          f"mean total loss {summary['total_loss_mUSD_mean']:,.1f} mUSD -> aggregates.csv, loss_by_canton.csv")


# ---------------------------------------------------------------------------
# Phase 4 — UQ-aligned view
# ---------------------------------------------------------------------------

def _window_mask(ts: pd.Series, lo: int, hi: int) -> pd.Series:
    return (ts >= lo) & (ts <= hi)


def seed_uq_table(run_dir: Path, mmi: dict) -> pd.DataFrame:
    df = load_firm_ts(run_dir)
    t_max = int(df["time_step"].max())
    df["mmi_bin"] = df["subregion_canton"].map(mmi).fillna("unknown")
    # outcome ratios vs t=0 (guard zero baselines)
    df["sales_ratio"] = np.where(df["prod0"] > 1e-9, df["production"] / df["prod0"], np.nan)
    df["purch_ratio"] = np.where(df["inp0"] > 1e-9, df["total_input"] / df["inp0"], np.nan)

    windows = {"acute": ACUTE, "recovery": (RECOVERY[0], min(RECOVERY[1], t_max))}
    recs = []
    for wname, (lo, hi) in windows.items():
        if lo > t_max:
            continue
        w = df[_window_mask(df["time_step"], lo, hi)]
        if w.empty:
            continue
        for (mb, ig), g in w.groupby(["mmi_bin", "isic_group"]):
            for outcome, ratio_col, wcol in (("sales", "sales_ratio", "prod0"),
                                             ("purchases", "purch_ratio", "inp0")):
                r = g[ratio_col].to_numpy()
                wt = g[wcol].to_numpy()
                ok = np.isfinite(r) & (wt > 0)
                if ok.sum() == 0:
                    continue
                # output-weighted mean ratio over firm-days in the window
                mean_ratio = np.average(r[ok], weights=wt[ok])
                recs.append({"mmi_bin": mb, "isic_group": ig, "outcome": outcome,
                             "window": wname,
                             "pct_change": 100.0 * (mean_ratio - 1.0),
                             "log_points": 100.0 * np.log(mean_ratio) if mean_ratio > 0 else np.nan})
    return pd.DataFrame(recs)


def phase4(variant_dir: Path, mmi: dict) -> None:
    seeds = _seed_dirs(variant_dir)
    if not seeds:
        print(f"  [phase4] no seed runs in {variant_dir}")
        return
    per_seed = []
    for d in seeds:
        t = seed_uq_table(d, mmi)
        t["seed"] = int(d.name.split("_")[1])
        per_seed.append(t)
    allt = pd.concat(per_seed, ignore_index=True)
    keys = ["mmi_bin", "isic_group", "outcome", "window"]
    agg = allt.groupby(keys).agg(
        mean_pct_change=("pct_change", "mean"),
        q25=("pct_change", lambda s: s.quantile(0.25)),
        q50=("pct_change", lambda s: s.quantile(0.50)),
        q75=("pct_change", lambda s: s.quantile(0.75)),
        mean_log_points=("log_points", "mean"),
        n_seeds=("seed", "nunique"),
    ).reset_index()
    agg.to_csv(variant_dir / "uq_aligned.csv", index=False)
    placeholder = "(placeholder MMI)" if not mmi else ""
    print(f"  [phase4] {variant_dir.name}: {len(agg)} rows -> uq_aligned.csv {placeholder}")


def main():
    variants = sys.argv[1:] or ["V1"]
    mmi = load_canton_mmi()
    if not mmi:
        print("NOTE: no canton_mmi_bin.csv found -> mmi_bin='unknown' (Phase 4 placeholder).")
    for v in variants:
        vd = RUNS_ROOT / v
        if not vd.exists():
            print(f"skip {v}: {vd} not found")
            continue
        print(f"== {v} ==")
        phase3(vd)
        phase4(vd, mmi)


if __name__ == "__main__":
    main()
