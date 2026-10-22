"""Fill the basin target table of the EU scope from the Destatis inland-waterway statistics (GENESIS table 46321-0014,
tonnes transported by waterway section, NST division and dangerous-goods flag), downloaded as flat CSV into
<data-root>/EU/validation/destatis_46321-0014_<years>.csv (23 Oct 2026; token in ~/.destatis_token, never in the repo).

Each gazetteer waterway of waterways_gazetteer.csv is mapped to its Destatis sections; the target is the tonnage of the
busiest section (metric max_cross_section: Destatis counts a tonne once per section it uses, which is a cross-section count,
not a tonne-km), and the section values are kept in destatis_waterway_sections_2023.csv for reference. The Rhine rows stay
on the CCNR profile (scenarios/rhine_capacities.csv); the Destatis Rhine sections are listed in the sections file only.

Usage:
    python onboarding/scripts/destatis_waterway_targets.py [--year 2023] [--data-root DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

SECTIONS = {   # gazetteer waterway -> Destatis section labels (prefix match on the label)
    "Main": ["Main, Offenbach bis zum Rhein", "Main, Aschaffenburg bis Offenbach", "Main, Würzburg bis Aschaffenburg", "Main, Mündung des Main-Donau-Kanals bis Würzburg"],
    "Moselle": ["Mosel"],
    "Neckar": ["Neckar, Heilbronn bis zum Rhein", "Neckar, Stuttgart bis Heilbronn"],
    "Mittellandkanal": ["Mittellandkanal, Minden bis Braunschweig", "Mittellandkanal, Bergeshövede bis Minden", "Mittellandkanal, Braunschweig bis Elbe"],
    "Dortmund-Ems-Kanal": ["Dortmund-Ems-Kanal, Dortmund bis Datteln", "Dortmund-Ems-Kanal, Datteln bis Bergeshövede", "Dortmund-Ems-Kanal, Bergeshövede bis Herbrum", "Dortmund-Ems-Kanal, Herbrum bis Emden, Unterems"],
    "Wesel-Datteln-Kanal": ["Wesel-Datteln-Kanal"],
    "Rhein-Herne-Kanal": ["Rhein-Herne-Kanal"],
    "Elbe": ["Elbe, Schnackenburg bis Hamburg", "Elbe, Magdeburg bis Schnackenburg", "Elbe bis Magdeburg"],   # the inland Elbe; the estuary below Hamburg is sea-going traffic
    "Elbe-Seitenkanal": ["Elbe-Seitenkanal"],
    "Weser": ["Weser, Minden bis Bremen", "Weser, Hann. Münden bis Minden"],                               # the inland Weser; Bremen to the sea is the estuary
    "Danube": ["Donau, Kelheim bis Regensburg", "Donau, Regensburg bis Vilshofen", "Donau, Vilshofen bis österreichische Grenze"],
    "Main-Donau-Kanal": ["Main-Donau-Kanal"],
    "Saar": ["Saar, Mosel bis Völklingen"],
    "Kuestenkanal-Hunte": ["Küstenkanal", "Hunte"],
    "Nord-Ostsee-Kanal": ["Nord-Ostsee-Kanal"],
    "Havel-Berlin canals": ["Untere Havel Wasserstraße", "Berliner Havel", "Potsdamer Havel", "Teltow-Kanal", "Havel-Oder-Wasserstraße", "Havel-Kanal", "Spree-Oder Wasserstraße"],
    "Oder": ["Oder"],
    "Ruhr": ["Ruhrwasserstraße"],
}
RHINE = ["Rhein, Rheinfelden bis Straßburg", "Rhein, Straßburg bis Neuburgweier", "Rhein, Neuburgweier bis Mannheim", "Rhein, Mannheim bis Bingen",
         "Rhein, Bingen bis Lülsdorf", "Rhein, Lülsdorf bis Orsoy", "Rhein, Orsoy bis niederländische Grenze"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", default="2023")
    ap.add_argument("--data-root", default="C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data")
    a = ap.parse_args()
    V = Path(a.data_root) / "EU" / "validation"
    src = sorted(V.glob("destatis_46321-0014_*.csv"))[-1]
    d = pd.read_csv(src, sep=";", dtype=str)
    d = d[d.time == a.year].copy()
    d["v"] = pd.to_numeric(d["value"].str.replace(",", "."), errors="coerce")
    sec = d.groupby("4_variable_attribute_label").v.sum().sort_values(ascending=False) / 1e6   # Mt, all goods, all dangerous-goods flags
    sec.rename("mt_per_year").to_csv(V / f"destatis_waterway_sections_{a.year}.csv", header=True, index_label="section")
    cite = f"Destatis GENESIS 46321-0014, {a.year}, tonnes transported by waterway section (all goods), via the API on 23 Oct 2026"
    tgt_path = V / "waterway_targets_2023.csv"
    t = pd.read_csv(tgt_path)
    rows = []
    for ww, labels in SECTIONS.items():
        vals = {lab: float(sec.get(lab, float("nan"))) for lab in labels}
        vals = {k: v for k, v in vals.items() if v == v}
        if not vals:
            print(f"{ww}: no Destatis section found"); continue
        best = max(vals, key=vals.get)
        rows.append({"waterway": ww, "country": "DE", "mt_per_year": round(vals[best], 2), "bn_tkm_per_year": "", "metric": "max_cross_section",
                     "source": f"{cite}; busiest section '{best}' of {len(vals)} ({'; '.join(f'{k} {v:.1f}' for k, v in vals.items())})"})
    new = pd.DataFrame(rows)
    keep = t[~((t.waterway.isin(new.waterway)) & (t.country == "DE"))]
    out = pd.concat([keep, new], ignore_index=True)
    out.to_csv(tgt_path, index=False)
    print(f"{len(new)} German waterway targets filled from Destatis; table now {len(out)} rows -> {tgt_path.name}")
    print("Rhine sections (Mt, for the profile check):", {k: round(float(sec.get(k, float('nan'))), 1) for k in RHINE})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
