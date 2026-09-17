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

# observed anchors, Mt/yr (2024; UA sheets = UA-exit direction only, so both-
# direction model values should sit somewhat ABOVE the UA anchors; MD road
# counts are trucks both directions incl. empties, converted at 10-15 t)
OBSERVED = {
    "Porubne-Siret":        ("road",  1.4, "UA-exits only (260 veh/day)"),
    "Vadul-Siret/Vicsani":  ("rail",  2.0, "UA-exits only (165 kt/month)"),
    "Dyakove-Halmeu":       ("road",  0.45, "UA-exits only (83 veh/day)"),
    "Dyakove/Halmeu rail":  ("rail",  0.44, "UA-exits only (37 kt/month)"),
    "Orlivka-Isaccea ferry": ("road", 0.53, "UA-exits only (97 veh/day)"),
    "Leuseni-Albita":       ("road",  4.0, "both dir, 27k trucks/month at ~12.5 t"),
    "Sculeni":              ("road",  1.3, "both dir, 8.6k trucks/month"),
    "Giurgiulesti-Galati":  ("road",  1.3, "both dir, 8.4k trucks/month"),
    "Cahul-Oancea":         ("road",  1.2, "both dir, 8.0k trucks/month"),
    "Ungheni rail":         ("rail",  0.4, "both dir, 10.5k wagons/yr"),
    "Giurgiulesti rail":    ("rail",  0.7, "both dir, 18.3k wagons/yr"),
}

NAME_MAP = {  # edge-name token -> observed row
    "Porubne-Siret": "Porubne-Siret",
    "Vadul-Siret/Vicsani": "Vadul-Siret/Vicsani",
    "Dyakove-Halmeu": "Dyakove-Halmeu",
    "gauge break Dyakove/Halmeu": "Dyakove/Halmeu rail",
    "Orlivka-Isaccea": "Orlivka-Isaccea ferry",
    "Leuseni-Albita": "Leuseni-Albita",
    "Sculeni": "Sculeni",
    "Giurgiulesti-Galati": "Giurgiulesti-Galati",
    "Cahul-Oancea": "Cahul-Oancea",
    "stitch railways @(27.81,47.23)": "Ungheni rail",
    "stitch railways @(28.20,45.47)": "Giurgiulesti rail",
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
    print(f"{'crossing':26s} {'mode':5s} {'model Mt/yr':>11s} {'observed':>9s}  note")
    for key, (mode, obs, note) in OBSERVED.items():
        m = model.pop(key, 0.0)
        flag = ""
        if "UA-exits" in note:
            flag = "  (model = both directions)"
        print(f"{key:26s} {mode:5s} {m:11.2f} {obs:9.2f}  {note}{flag}")
    for key, m in sorted(model.items()):
        print(f"{key:26s} {'':5s} {m:11.2f} {'-':>9s}")
    ua = sum(v for k, v in
             [(k, model.get(k, 0)) for k in []] ) # placeholder
    return 0


if __name__ == "__main__":
    sys.exit(main())
