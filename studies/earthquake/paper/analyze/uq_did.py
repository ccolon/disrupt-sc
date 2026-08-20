"""MMI-bin event study vs the UQ firm-level study, from one run.

Reads firm_data + firm_table (canton) + canton_mmi_bin.csv. Excludes ISIC K/O
(FIN, SEG, ADP) to match UQ's bilateral filter. For each (mmi_bin, tau) computes
sales and purchases % change vs pre-shock (t=0), where tau = time_step - 1
(shock at step 1).

Two measures are emitted, distinguished by the ``measure`` column:

  b2b    domestic firm-to-firm flows only, taken from link_data.csv. This is the
         like-for-like measure: UQ observes transactions between Ecuadorian firms
         and nothing else.
  total  production and total_input, i.e. every buyer and every supplier. Roughly
         two thirds of firm output goes to households, government, investment and
         exports, and those channels are exogenous here -- they do not fall with
         the shock, so they dilute the measured drop toward zero.

``b2b`` is only available when link_data.csv was exported; otherwise just ``total``
is written, and downstream consumers fall back to it.

On the UQ targets: the acute window is a genuine calibration target. The recovery
window is NOT -- UQ's post-shock rebound is driven by central-government fiscal
and financial stimulus, which this model does not represent, so no parameter
setting should be expected to reproduce it.

  uq_eventstudy.csv : measure x outcome x mmi_bin x tau -> pct_change
  uq_did.csv        : measure x outcome -> acute (tau 0,1) / recovery (tau 2-12) DiD

CLI:
  python uq_did.py <run_dir> --canton-mmi <canton_mmi_bin.csv> [--out-dir DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

EXCLUDED = {"FIN", "SEG", "ADP"}                    # ISIC K + O, as in UQ's panel
BINS = ["control", "bin_56", "bin_67", "bin_7p"]
ACUTE = [0, 1]
RECOVERY = list(range(2, 13))


def b2b_aggregate(run_dir: Path, bin_of: dict, sector_of: dict) -> pd.DataFrame | None:
    """Domestic firm-to-firm sales and purchases per (mmi_bin, time_step).

    A link counts when the buyer is a firm and the seller is a modeled firm, which
    drops household, government, investment and export sales on one side and imports
    on the other -- leaving what UQ actually observes. Sales are attributed to the
    seller's canton and purchases to the buyer's, and the sector exclusion is applied
    to whichever firm the flow is attributed to.

    Returns None when link_data.csv is absent, so older runs still analyze.
    """
    path = run_dir / "link_data.csv"
    if not path.exists():
        return None
    ld = pd.read_csv(path, low_memory=False,
                     usecols=["time_step", "seller_id", "buyer_id", "buyer_type",
                              "realized_delivery"])
    ld["seller_id"] = ld.seller_id.astype(str)
    ld["buyer_id"] = ld.buyer_id.astype(str)
    ld = ld[(ld.buyer_type == "Firm") & ld.seller_id.isin(bin_of) & ld.buyer_id.isin(bin_of)]
    if ld.empty:
        return None

    def side(id_col: str, name: str) -> pd.DataFrame:
        keep = ld[~ld[id_col].map(sector_of).isin(EXCLUDED)]
        return (keep.assign(mmi_bin=keep[id_col].map(bin_of))
                    .groupby(["mmi_bin", "time_step"]).realized_delivery.sum()
                    .rename(name).reset_index())

    sales, purch = side("seller_id", "sales"), side("buyer_id", "purchases")
    return sales.merge(purch, on=["mmi_bin", "time_step"], how="outer").fillna(0.0)


def event_study(agg: pd.DataFrame, measure: str) -> pd.DataFrame:
    """Percent change vs each bin's own t=0, long by outcome x bin x tau."""
    rows = []
    for outcome in ("sales", "purchases"):
        base = agg[agg.time_step == 0].set_index("mmi_bin")[outcome]
        for b in BINS:
            b0 = base.get(b, np.nan)
            for _, r in agg[agg.mmi_bin == b].sort_values("time_step").iterrows():
                pct = 100.0 * (r[outcome] / b0 - 1.0) if b0 and b0 > 1e-9 else np.nan
                rows.append({"measure": measure, "outcome": outcome, "mmi_bin": b,
                             "time_step": int(r.time_step), "tau": int(r.time_step) - 1,
                             "pct_change": pct})
    return pd.DataFrame(rows)


def did_table(es: pd.DataFrame) -> pd.DataFrame:
    """Acute and recovery DiD (bin_7p - control) for every measure and outcome."""
    rows = []
    for (measure, outcome), g in es.groupby(["measure", "outcome"]):
        piv = g.pivot_table(index="tau", columns="mmi_bin", values="pct_change")
        for window, taus in (("acute", ACUTE), ("recovery", RECOVERY)):
            taus = [t for t in taus if t in piv.index]
            if not taus:
                continue
            m7 = piv.loc[taus, "bin_7p"].mean() if "bin_7p" in piv else np.nan
            ct = piv.loc[taus, "control"].mean() if "control" in piv else np.nan
            rows.append({"measure": measure, "outcome": outcome, "window": window,
                         "mmi7_pct": round(m7, 2), "control_pct": round(ct, 2),
                         "did": round(m7 - ct, 2)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="MMI-bin event study / DiD vs UQ")
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--canton-mmi", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()
    out_dir = args.out_dir or args.run_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    fd = pd.read_csv(args.run_dir / "firm_data.csv",
                     usecols=["time_step", "firm", "sector", "production", "total_input"])
    fd = fd[~fd.sector.isin(EXCLUDED)]

    ft = gpd.read_file(args.run_dir / "firm_table.geojson")[["id", "subregion_canton", "sector"]]
    cbin = pd.read_csv(args.canton_mmi)
    canton2bin = dict(zip(cbin.subregion_canton, cbin.mmi_bin))
    ft["mmi_bin"] = ft.subregion_canton.map(canton2bin).fillna("control")
    fd = fd.merge(ft[["id", "mmi_bin"]], left_on="firm", right_on="id", how="left")

    agg = (fd.groupby(["mmi_bin", "time_step"])[["production", "total_input"]].sum()
             .rename(columns={"production": "sales", "total_input": "purchases"}).reset_index())

    frames = [event_study(agg, "total")]

    bin_of = dict(zip(ft.id.astype(str), ft.mmi_bin))
    sector_of = dict(zip(ft.id.astype(str), ft.sector)) if "sector" in ft.columns else {}
    b2b = b2b_aggregate(args.run_dir, bin_of, sector_of)
    if b2b is None:
        print("note: no link_data.csv — writing the 'total' measure only. UQ observes "
              "firm-to-firm flows, so the like-for-like comparison is unavailable here.")
    else:
        frames.append(event_study(b2b, "b2b"))

    es = pd.concat(frames, ignore_index=True)
    es.to_csv(out_dir / "uq_eventstudy.csv", index=False)
    did = did_table(es)
    did.to_csv(out_dir / "uq_did.csv", index=False)

    # Acute is a real calibration target. Recovery is not: UQ's rebound is driven by
    # central-government fiscal and financial stimulus, which this model does not
    # represent, so the gap there is structural rather than a mis-set parameter.
    UQ = {("sales", "acute"): -9.6, ("sales", "recovery"): 10.8,
          ("purchases", "acute"): -14.3, ("purchases", "recovery"): 5.7}
    did["uq_did"] = [UQ.get((o, w)) for o, w in zip(did.outcome, did.window)]
    did["comparable"] = ["yes" if w == "acute" else "no (stimulus not modeled)"
                         for w in did.window]
    print(did.to_string(index=False))
    if "b2b" in set(did.measure):
        print("\n'b2b' is the like-for-like measure; 'total' includes households, government, "
              "investment and exports, which are exogenous here and dilute the drop.")
    print(f"\n-> {out_dir/'uq_eventstudy.csv'}\n-> {out_dir/'uq_did.csv'}")


if __name__ == "__main__":
    main()
