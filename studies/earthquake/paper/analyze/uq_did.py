"""MMI-bin event study vs the UQ firm-level study, from one run.

Reads firm_data + firm_table (canton) + canton_mmi_bin.csv. Excludes ISIC K/O
(FIN, SEG, ADP) to match UQ's bilateral filter. For each (mmi_bin, tau) computes
sales (production) and purchases (total_input) % change vs pre-shock (t=0), where
tau = time_step - 1 (shock at step 1). Emits:
  uq_eventstudy.csv : mmi_bin x tau x outcome -> pct_change (+ raw + control DiD)
  uq_did.csv        : acute (tau 0,1) / recovery (tau 2-12) DiD (bin_7p - control)

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

    ft = gpd.read_file(args.run_dir / "firm_table.geojson")[["id", "subregion_canton"]]
    cbin = pd.read_csv(args.canton_mmi)
    canton2bin = dict(zip(cbin.subregion_canton, cbin.mmi_bin))
    ft["mmi_bin"] = ft.subregion_canton.map(canton2bin).fillna("control")
    fd = fd.merge(ft[["id", "mmi_bin"]], left_on="firm", right_on="id", how="left")

    agg = (fd.groupby(["mmi_bin", "time_step"])[["production", "total_input"]].sum()
             .rename(columns={"production": "sales", "total_input": "purchases"}).reset_index())

    rows = []
    for outcome in ("sales", "purchases"):
        base = agg[agg.time_step == 0].set_index("mmi_bin")[outcome]
        for b in BINS:
            b0 = base.get(b, np.nan)
            sub = agg[agg.mmi_bin == b].sort_values("time_step")
            for _, r in sub.iterrows():
                pct = 100.0 * (r[outcome] / b0 - 1.0) if b0 and b0 > 1e-9 else np.nan
                rows.append({"outcome": outcome, "mmi_bin": b,
                             "time_step": int(r.time_step), "tau": int(r.time_step) - 1,
                             "pct_change": pct})
    es = pd.DataFrame(rows)
    es.to_csv(out_dir / "uq_eventstudy.csv", index=False)

    # acute / recovery DiD (bin_7p - control)
    did_rows = []
    for outcome in ("sales", "purchases"):
        piv = es[es.outcome == outcome].pivot_table(index="tau", columns="mmi_bin", values="pct_change")
        for window, taus in [("acute", ACUTE), ("recovery", RECOVERY)]:
            taus = [t for t in taus if t in piv.index]
            if not taus:
                continue
            m7 = piv.loc[taus, "bin_7p"].mean() if "bin_7p" in piv else np.nan
            ct = piv.loc[taus, "control"].mean() if "control" in piv else np.nan
            did_rows.append({"outcome": outcome, "window": window,
                             "mmi7_pct": round(m7, 2), "control_pct": round(ct, 2),
                             "did": round(m7 - ct, 2)})
    did = pd.DataFrame(did_rows)
    did.to_csv(out_dir / "uq_did.csv", index=False)

    UQ = {("sales", "acute"): -9.6, ("sales", "recovery"): 10.8,
          ("purchases", "acute"): -14.3, ("purchases", "recovery"): 5.7}
    did["uq_did"] = [UQ.get((o, w)) for o, w in zip(did.outcome, did.window)]
    print(did.to_string(index=False))
    print(f"\n-> {out_dir/'uq_eventstudy.csv'}\n-> {out_dir/'uq_did.csv'}")


if __name__ == "__main__":
    main()
