"""The loading table rebuilt on its source ledger (6 Oct 2026, user decision after the review of 5 Oct, point NS1), and
its derived variants.

The central table (scenarios/draught_table.csv) is rebuilt at the low end, where the one weekly tonnage count
available (KBN, the week to 13 August 2026: 22 % of normal at a mean gauge of about 12 cm) sat above the earlier
values (0.12 at 15 cm, 0.08 at 10, 0.05 at 5), and where the single-vessel evidence (Argus, the low-water tankers,
the Kiel Institute statement: 0.10-0.15 per vessel at 23-30 cm) times the fleet's redeployment (1.9-2.5) gives
0.28-0.30 rather than 0.22-0.25. From 55 cm up the anchors are unchanged. The earlier table is kept as
draught_table_v1.csv (the runs of 22-30 September 2026 used it).

    cm    v1    rebuilt   anchor
     5   0.05   0.08      assumed: the low-water tankers and the small units (the press reports shipping stopped at 6 cm,
                          but the count of the week at 23 -> 6 cm gave 0.22); held below 5 cm
    10   0.08   0.18      interpolated towards the count
    15   0.12   0.24      KBN count 0.22 at about 12 cm
    25   0.22   0.28      Argus, low-water tankers: 0.15 per vessel at 23 cm, times 1.9
    30   0.25   0.30      Kiel Institute: 0.10-0.15 per vessel, times 2-2.5; 2018: class II-III only
    40   0.30   0.33      WSV: 0.20 per vessel at 40-50 cm, times 1.65; Contargo: large container vessels stop at 40
    55   0.40   0.40      Contargo 0.16 per large container vessel, times 2.5 (unchanged)
    78+  unchanged

Derived variants written here, all from the central table:
    draught_table_low.csv / _high.csv     the shortfall (1 - load factor) times 1.15 / 0.85 (the loading-table band)
    draught_table_floor04.csv / _floor16.csv   the 5 cm row (the floor held below 5 cm) at half and twice its value
    draught_table_lowwater.csv            the low-water fleet lever: +0.10 between 15 and 55 cm
    draught_table_lowwater_wide.csv       the same gain carried to 100 cm (+0.10 at 78, +0.08 at 100, +0.03 at 120)

Usage:
    python studies/rhine2026/build_draught_variants.py [--rebuild]   (--rebuild writes the central table from REBUILT)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = HERE / "scenarios"

REBUILT = {5: 0.08, 10: 0.18, 15: 0.24, 25: 0.28, 30: 0.30, 40: 0.33, 55: 0.40, 78: 0.60, 100: 0.80, 120: 0.90, 150: 1.00, 250: 1.00}
ANCHORS = {
    5: "assumed: the low-water tankers (Stolt Ludwigshafen ~800 t at 30 cm; nine such ships Aug 2026) and the small units; the press reports shipping past Kaub stopped at 6 cm (14 Aug 2026), but the KBN count of the week at 23 -> 6 cm gave 0.22; held below 5 cm",
    10: "interpolated towards the KBN count of the week to 13 Aug 2026 (0.22 at a mean gauge of about 12 cm)",
    15: "KBN week to ~13 Aug 2026 (Kaub 23 -> 6 cm, mean about 12): 60 kt dry + 30 kt wet vs normal 300 + 100 kt = 22%; partly small Class II-IV units",
    25: "Argus: 1,200 t tanker loads 180 t (15%) at 23 cm; low-water tankers 700-800 t of 5,100 t (15%); times a redeployment of 1.9",
    30: "IfW 28 Jul 2026: loads 10-15% per vessel; 2018 record 25 cm: only Class II/III vessels sailed (van Dorsser 2020); times a redeployment of 2-2.5",
    40: "WSV: at 40-50 cm vessels carry ~20%; Contargo 40 cm 'freight navigation practically impossible' (large container vessels); times a redeployment of 1.65",
    55: "Contargo: 55 cm = 16% for large container vessels; fleet redeployment x2-2.5 (twice the number of vessels, SMC 2026)",
    78: "GlW: Contargo 25% per vessel = 4x ships; Ademmer et al. 2023: a full month <78 cm = -25% German IWW tonnage (Kaub usually far below in those months)",
    100: "mild surcharge band (Maersk EUR 100/20' <91 cm)",
    120: "Kaub 120-125 cm late April 2026: normal loading reported",
    150: "full loading of standard vessels needs ~150 cm (hydrostatus/Kiel); fleet slack absorbs the residual",
    250: "Contargo 2017: 250 cm = 100%",
}


def rebuild_central():
    v1 = pd.read_csv(SCEN / "draught_table.csv")
    if not (SCEN / "draught_table_v1.csv").exists():
        v1.to_csv(SCEN / "draught_table_v1.csv", index=False)
    assert list(v1.kaub_cm.astype(int)) == list(REBUILT)
    new = v1.copy()
    new["load_factor"] = [REBUILT[int(c)] for c in new.kaub_cm]
    new["anchor"] = [ANCHORS[int(c)] for c in new.kaub_cm]
    new.to_csv(SCEN / "draught_table.csv", index=False)
    print("central table rebuilt:", dict(zip(new.kaub_cm.astype(int), new.load_factor)))


def variants():
    t = pd.read_csv(SCEN / "draught_table.csv")
    lf = t.load_factor.astype(float)
    for k, name in ((1.15, "low"), (0.85, "high")):
        v = t.copy(); v["load_factor"] = (1 - k * (1 - lf)).clip(0, 1).round(3)
        v["anchor"] = f"band: the central table's shortfall x {k:.2f} (6 Oct 2026)"
        v.to_csv(SCEN / f"draught_table_{name}.csv", index=False)
    floor = float(lf.iloc[0])
    for mult, name in ((0.5, "floor04"), (2.0, "floor16")):
        v = t.copy(); v.loc[0, "load_factor"] = round(floor * mult, 3)
        v.loc[0, "anchor"] = f"sensitivity (6 Oct 2026): the floor below 5 cm at {floor * mult:.2f} instead of {floor:.2f}; the other rows unchanged"
        v.to_csv(SCEN / f"draught_table_{name}.csv", index=False)
    low = t.copy()
    low["load_factor"] = [round(min(1.0, f + 0.10), 3) if 15 <= c <= 55 else f for c, f in zip(t.kaub_cm, lf)]
    low["anchor"] = "low-water fleet lever: the central table + 0.10 between 15 and 55 cm (6 Oct 2026)"
    low[["kaub_cm", "load_factor", "load_factor_vessel_gms"]].to_csv(SCEN / "draught_table_lowwater.csv", index=False)
    wide = low.copy()
    gain = {78: 0.10, 100: 0.08, 120: 0.03}
    wide["load_factor"] = [round(min(1.0, f + gain.get(int(c), 0.0)), 3) for c, f in zip(wide.kaub_cm, wide.load_factor)]
    wide[["kaub_cm", "load_factor", "load_factor_vessel_gms"]].to_csv(SCEN / "draught_table_lowwater_wide.csv", index=False)
    for name in ("low", "high", "floor04", "floor16", "lowwater", "lowwater_wide"):
        d = pd.read_csv(SCEN / f"draught_table_{name}.csv")
        print(f"{name:14s}", [f"{int(c)}:{v:.2f}" for c, v in zip(d.kaub_cm, d.load_factor)])
    for stale in ("draught_table_floor02.csv", "draught_table_floor10.csv"):
        p = SCEN / stale
        if p.exists():
            p.unlink(); print("removed", stale)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="write the central table from REBUILT (keeps draught_table_v1.csv)")
    a = ap.parse_args()
    if a.rebuild:
        rebuild_central()
    variants()
