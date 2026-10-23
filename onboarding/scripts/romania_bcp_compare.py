"""Compare modeled UA/MD border-crossing flows with the WB BCP counts.

Reads the newest (or --run) initial-state export, sums flows on the
border-marked crossing edges (special~'border', v8 network), annualizes,
and prints them against the observed 2024 anchors from BCP Counts.xlsx.

Usage: python romania_bcp_compare.py [--run <folder>]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd

REPO = Path(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc")

# observed anchors (2024). UA sheets = UA-exit direction only (tonnage data),
# so both-direction model values should sit somewhat ABOVE the UA anchors.
# MD road rows are TRUCK COUNTS both directions: gross tons = trucks x 12.5 t;
# the model carries CARGO tons only, so the comparable target is the LOADED
# equivalent, gross x (1 - empty). 'empty' defaults to a flat 0.25 - replace
# per crossing when the WB provides BCP-specific loaded/empty splits
# (ValidationNote3 limitation; the mechanism is per-row ready).
TPT = 12.5          # tons per loaded truck
EMPTY_DEFAULT = 0.25
OBSERVED = {
    # name: (mode, Mt/yr tonnage anchor OR {'trucks_pm': n, 'empty': x}, note)
    "Porubne-Siret":        ("road",  1.4, "UA-exits only (260 veh/day)"),
    "Stanca-Costesti":      ("road",  {"trucks_pm": 2400}, "both dir, 2.4k trucks/month"),
    "Radauti-Prut":         ("road",  {"trucks_pm": 170}, "both dir, 170 trucks/month"),
    "Vadul-Siret/Vicsani":  ("rail",  2.0, "UA-exits only (165 kt/month)"),
    "Dyakove-Halmeu":       ("road",  0.45, "UA-exits only (83 veh/day)"),
    "Dyakove/Halmeu rail":  ("rail",  0.44, "UA-exits only (37 kt/month)"),
    "Orlivka-Isaccea ferry": ("road", 0.53, "UA-exits only (97 veh/day)"),
    "Leuseni-Albita":       ("road",  {"trucks_pm": 27000}, "both dir, 27k trucks/month"),
    "Sculeni":              ("road",  {"trucks_pm": 8600}, "both dir, 8.6k trucks/month"),
    "Giurgiulesti-Galati":  ("road",  {"trucks_pm": 8400}, "both dir, 8.4k trucks/month"),
    "Cahul-Oancea":         ("road",  {"trucks_pm": 8000}, "both dir, 8.0k trucks/month"),
    "Ungheni rail":         ("rail",  0.4, "both dir, 10.5k wagons/yr"),
    "Giurgiulesti rail":    ("rail",  0.7, "both dir, 18.3k wagons/yr"),
}


def observed_values(spec):
    """(gross Mt/yr, loaded Mt/yr) from a tonnage anchor or a truck-count spec."""
    if isinstance(spec, dict):
        gross = spec["trucks_pm"] * 12 * TPT / 1e6
        loaded = gross * (1 - spec.get("empty", EMPTY_DEFAULT))
        return gross, loaded
    return spec, None

NAME_MAP = {  # edge-name token -> observed row (v15 'BCP:' naming)
    "BCP: Siret-Porubne (roads)": "Porubne-Siret",
    "BCP: Vicsani-Vadul-Siret (railways)": "Vadul-Siret/Vicsani",
    "BCP: Halmeu-Dyakove (roads)": "Dyakove-Halmeu",
    "BCP: Halmeu-Dyakove (railways)": "Dyakove/Halmeu rail",
    "BCP: Isaccea-Orlivka (roads)": "Orlivka-Isaccea ferry",
    "BCP: Albita-Leuseni (roads)": "Leuseni-Albita",
    "BCP: Sculeni (roads)": "Sculeni",
    "BCP: Giurgiulesti-Galati (roads)": "Giurgiulesti-Galati",
    "BCP: Oancea-Cahul (roads)": "Cahul-Oancea",
    "BCP: Ungheni (railways)": "Ungheni rail",
    "BCP: Giurgiulesti CFR (railways)": "Giurgiulesti rail",
    "BCP: Stanca-Costesti (roads)": "Stanca-Costesti",
    "BCP: Radauti-Prut-Lipcani (roads)": "Radauti-Prut",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None)
    args = ap.parse_args()
    base = REPO / "output" / "Romania"
    run = base / args.run if args.run else sorted(p for p in base.iterdir() if p.is_dir())[-1]
    e = gpd.read_file(run / "transport_edges_with_flows_0.geojson")
    border = e[e["special"].astype(str).str.contains("border", na=False)].copy()
    border["mtyr"] = border["flow_total_tons"].fillna(0) * 52 / 1e6

    model = {}
    for _, r in border.iterrows():
        name = str(r.get("name", ""))
        for token, obs_key in NAME_MAP.items():
            if token in name:
                model[obs_key] = model.get(obs_key, 0.0) + r["mtyr"]
                break
        else:
            if r["mtyr"] > 0.005:
                model.setdefault("(unmapped) " + name, r["mtyr"])

    print(f"run: {run.name}\n")
    print(f"{'crossing':26s} {'mode':5s} {'model Mt/yr':>11s} {'obs loaded':>10s} {'obs gross':>9s}  note")
    for key, (mode, spec, note) in OBSERVED.items():
        m = model.pop(key, 0.0)
        gross, loaded = observed_values(spec)
        flag = "  (model = both directions)" if "UA-exits" in note else ""
        ls = f"{loaded:10.2f}" if loaded is not None else f"{'-':>10s}"
        print(f"{key:26s} {mode:5s} {m:11.2f} {ls} {gross:9.2f}  {note}{flag}")
    print("\n(loaded = gross x (1 - empty), flat 25% empty unless a per-BCP "
          "split is set; the model carries cargo tons, so LOADED is the "
          "comparable target for the truck-count rows)")
    for key, m in sorted(model.items()):
        print(f"{key:26s} {'':5s} {m:11.2f} {'-':>10s} {'-':>9s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
