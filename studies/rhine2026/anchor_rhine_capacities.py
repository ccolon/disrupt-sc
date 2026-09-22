"""Anchor the Rhine cross-section capacities to the model's own baseline flow (22 Sep 2026).

scenarios/rhine_capacities.csv holds normal-year cross-section tonnages from the CCNR statistics
(about 60 % of its rows are estimates). The capacity gate compares the load of an edge with its
capacity every step, so wherever the calibrated baseline already moves more than the file says
(Kaub 148 vs 137 kt/day, Mainz, Koblenz: 4-8 % above, inside the file's stated uncertainty) the
gate would bind at normal water and cut traffic that the calibration put there. This script sets
every Rhine section's capacity to max(file, modelled baseline flow) - the largest per-segment flow
of the section's edges in the baseline week of a run (several edges share a section name) - so
the gate is inert at full load and Kaub's weekly capacity is the draught table's load factor times
its own baseline flow.

--headroom adds a margin above the modelled flow (the smoke run of 22 Sep used 0: the gate then cut 0.7 % of the
Kaub load at t=0 from run-to-run differences in the placed tonnage; 0.02 makes it inert at full load).

Usage:
    python studies/rhine2026/anchor_rhine_capacities.py <run_folder> [--headroom 0.02] [--out scenarios/rhine_capacities_anchored.csv]
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
PERIODS_PER_YEAR = 52.0


def main(run: Path, out: Path, headroom: float = 0.0):
    caps = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv")
    g = json.load(open(run / "transport_edges_with_flows_0.geojson", encoding="utf-8"))
    seg = defaultdict(list)
    for f in g["features"]:
        p = f["properties"]
        name = str(p.get("name") or "")
        if name.startswith("rhine"):
            seg[name].append((p.get("flow_total_tons") or 0.0) * PERIODS_PER_YEAR / 365.0)
    rows = []
    for _, r in caps.iterrows():
        model = max(seg.get(r["name"], [0.0]))
        anchored = max(float(r["tons_per_day"]), math.ceil(model * (1.0 + headroom) / 100.0) * 100.0)
        note = (f"anchored to the modelled baseline ({model:,.0f} t/day in {run.name}, headroom {headroom:.0%}, file {r['tons_per_day']:,.0f})"
                if anchored > r["tons_per_day"] else f"file value (modelled baseline {model:,.0f} t/day)")
        rows.append({"name": r["name"], "mt_per_year": round(anchored * 365 / 1e6, 1), "tons_per_day": int(anchored),
                     "basis": note})
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    raised = df[df.basis.str.startswith("anchored")]
    print(f"{len(df)} sections -> {out}; raised above the file: {len(raised)}")
    print(raised[["name", "tons_per_day", "basis"]].to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--headroom", type=float, default=0.0)
    ap.add_argument("--out", default=str(HERE / "scenarios" / "rhine_capacities_anchored.csv"))
    a = ap.parse_args()
    main(Path(a.run), Path(a.out), a.headroom)
