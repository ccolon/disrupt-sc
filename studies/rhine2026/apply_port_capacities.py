"""Write the per-port capacity overrides into the EU scope config.

Takes disrupt-sc-data/EU/Transport/port_capacity_overrides.csv (from
port_capacities.py) and (re)writes the block between the markers
``# BEGIN port capacities`` / ``# END port capacities`` in
config/user_defined_EU.local.yaml as a ``transport_capacity_overrides``
mapping (connector name -> tons/day). Also sets ``capacity_constraint``
to the requested mode (default binary: over-capacity terminals are not
routed, no re-pricing of edges below capacity).

Usage:
    python studies/rhine2026/apply_port_capacities.py [--mode binary|gradual|off] [--config <path>]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT.parent / "disrupt-sc-data" / "EU"
BEGIN, END = "# BEGIN port capacities", "# END port capacities"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "user_defined_EU.local.yaml"))
    ap.add_argument("--csv", default=str(DATA / "Transport" / "port_capacity_overrides.csv"))
    ap.add_argument("--mode", choices=["binary", "gradual", "off"], default="binary")
    args = ap.parse_args()

    caps = pd.read_csv(args.csv).sort_values("tons_per_day", ascending=False)
    lines = [BEGIN,
             "# Per-port throughput capacities (tons/day, shared across cargo types) for the",
             "# TEN-T maritime connectors: Eurostat mar_go_aa 2023 gross weight x 1.3 peak",
             "# factor, unlisted ports floored at 1 Mt/yr (studies/rhine2026/port_capacities.py).",
             f"# Generated {pd.Timestamp.today():%Y-%m-%d}; regenerate, do not hand-edit.",
             f"capacity_constraint: {args.mode}",
             "transport_capacity_overrides:"]
    for _, r in caps.iterrows():
        lines.append(f"  {r['connector']}: {int(r['tons_per_day'])}   # {r['ports']}")
    lines.append(END)
    block = "\n".join(lines) + "\n"

    p = Path(args.config)
    txt = p.read_text(encoding="utf-8")
    pat = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
    if pat.search(txt):
        txt = pat.sub(block, txt)
        action = "replaced"
    else:
        txt = txt.rstrip("\n") + "\n\n" + block
        action = "appended"
    p.write_text(txt, encoding="utf-8")
    print(f"{action} port-capacity block ({len(caps)} connectors, capacity_constraint: {args.mode}) in {p}")


if __name__ == "__main__":
    main()
