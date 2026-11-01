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

--by-cargo (1 Nov 2026): one capacity per cargo class (container, dry_bulk, liquid_bulk) instead of one for all
cargo together. The container vessels, the tank barges and the dry-bulk vessels are three fleets, and the room one
of them leaves at low water is not available to the others. Each class is anchored to its own modelled baseline
flow on the section (the largest tons_<class> of the section's edges in the flows export), with the file's section
total split across the classes in the proportions of that baseline as the floor, so that a section the file puts
above the model keeps the file's total as before; a class absent from a section's baseline gets a blank (no capacity
for it there: an explicit 0 would block it). Written as columns tons_per_day_<class>, which run_rhine.py passes to
transport_capacity_overrides as a per-class dict; tons_per_day keeps the sum for the readers of the total. Reason: on
the recalibrated flows the Middle Rhine carries 11.6 Mt/yr of containers (none in the first version) that leave at the
first low-water surcharge, and a single anchored capacity then rations the remaining bulk by that much less: the 2018
hindcast on the recalibrated flows gave half the first version's loss (review_20261008_response.md, 1 Nov 2026).

Usage:
    python studies/rhine2026/anchor_rhine_capacities.py <run_folder> [--headroom 0.02] [--by-cargo] [--out scenarios/rhine_capacities_anchored.csv]
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
CARGO_CLASSES = ("container", "dry_bulk", "liquid_bulk")   # the tons_<class> fields of the flows export


def _round_up(x: float) -> float:
    return math.ceil(x / 100.0) * 100.0


def main(run: Path, out: Path, headroom: float = 0.0, by_cargo: bool = False):
    caps = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv")
    g = json.load(open(run / "transport_edges_with_flows_0.geojson", encoding="utf-8"))
    seg = defaultdict(list)
    seg_ct = {ct: defaultdict(list) for ct in CARGO_CLASSES}
    for f in g["features"]:
        p = f["properties"]
        name = str(p.get("name") or "")
        if name.startswith("rhine"):
            seg[name].append((p.get("flow_total_tons") or 0.0) * PERIODS_PER_YEAR / 365.0)
            for ct in CARGO_CLASSES:
                seg_ct[ct][name].append((p.get(f"tons_{ct}") or 0.0) * PERIODS_PER_YEAR / 365.0)
    rows = []
    for _, r in caps.iterrows():
        file_total = float(r["tons_per_day"])
        model = max(seg.get(r["name"], [0.0]))
        if not by_cargo:
            anchored = max(file_total, _round_up(model * (1.0 + headroom)))
            note = (f"anchored to the modelled baseline ({model:,.0f} t/day in {run.name}, headroom {headroom:.0%}, file {file_total:,.0f})"
                    if anchored > file_total else f"file value (modelled baseline {model:,.0f} t/day)")
            rows.append({"name": r["name"], "mt_per_year": round(anchored * 365 / 1e6, 1), "tons_per_day": int(anchored),
                         "basis": note})
            continue
        m = {ct: max(seg_ct[ct].get(r["name"], [0.0])) for ct in CARGO_CLASSES}
        tot = sum(m.values())
        row = {"name": r["name"]}
        total, parts = 0.0, []
        for ct in CARGO_CLASSES:
            if m[ct] <= 0.0 or tot <= 0.0:
                row[f"tons_per_day_{ct}"] = None   # blank: the baseline moves none of this class here
                parts.append(f"{ct} none")
                continue
            floor = file_total * m[ct] / tot
            anchored = max(floor, _round_up(m[ct] * (1.0 + headroom)))
            row[f"tons_per_day_{ct}"] = int(round(anchored))
            total += anchored
            parts.append(f"{ct} {anchored:,.0f} ({'model' if anchored > floor + 0.5 else 'file share'}; baseline {m[ct]:,.0f})")
        row["mt_per_year"] = round(total * 365 / 1e6, 1)
        row["tons_per_day"] = int(round(total))
        row["basis"] = (f"per cargo class: max(file total {file_total:,.0f} split by the baseline's class shares, "
                        f"modelled baseline of {run.name} x {1.0 + headroom:.2f}): " + "; ".join(parts))
        rows.append(row)
    cols = (["name", "mt_per_year", "tons_per_day"] + [f"tons_per_day_{ct}" for ct in CARGO_CLASSES] + ["basis"]
            if by_cargo else ["name", "mt_per_year", "tons_per_day", "basis"])
    df = pd.DataFrame(rows)[cols]
    df.to_csv(out, index=False)
    if by_cargo:
        raised = df[df.basis.str.contains("(model;", regex=False)]
        print(f"{len(df)} sections -> {out}; sections with a class anchored above its file share: {len(raised)}")
        show = ["name", "tons_per_day"] + [f"tons_per_day_{ct}" for ct in CARGO_CLASSES]
        print(raised[show].to_string(index=False))
    else:
        raised = df[df.basis.str.startswith("anchored")]
        print(f"{len(df)} sections -> {out}; raised above the file: {len(raised)}")
        print(raised[["name", "tons_per_day", "basis"]].to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--headroom", type=float, default=0.0)
    ap.add_argument("--by-cargo", action="store_true", help="one capacity per cargo class (columns tons_per_day_<class>)")
    ap.add_argument("--out", default=str(HERE / "scenarios" / "rhine_capacities_anchored.csv"))
    a = ap.parse_args()
    main(Path(a.run), Path(a.out), a.headroom, a.by_cargo)
