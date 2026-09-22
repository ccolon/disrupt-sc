"""Pipeline audit (22 Sep 2026, review point OR3): what the model ships across Kaub that a pipeline carries in reality.

Reads the baseline week (t = 0) of a full-export run's link table, restricted to the links whose normal route crosses
Kaub (additional_data/kaub_crossing_links_<scope>_seed42.csv), and lists the imported inputs that reach refineries
(buyer sector C19) and utilities (D) by refinery agent, origin and cargo class. Imports from external partners carry
the seller sector "imports" in link_data.csv, not the product code; the refinery input from abroad is crude.

Usage:
    python studies/rhine2026/audit_kaub_imports.py <run_folder> [--links FILE] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COLS = ["time_step", "seller_id", "buyer_id", "seller_sector", "buyer_region", "buyer_sector", "order", "delivery_in_tons", "cargo_type"]
# known crude supply of the inland refineries the model places on the Rhine's upstream side (public operator information)
REALITY = {
    (48.99, 8.44): "MiRO Karlsruhe: crude by the TAL pipeline (Trieste) and the SPSE pipeline (Fos); no crude by barge",
    (48.58, 11.59): "Bayernoil Vohburg/Neustadt: crude by the TAL pipeline",
    (47.82, 13.01): "OMV Burghausen: crude by the TAL pipeline",
    (48.15, 16.49): "OMV Schwechat: crude by the AWP pipeline from the TAL system and Austrian fields",
    (46.95, 7.41): "Cressier (agent at the Swiss centroid): crude by pipeline from the SPSE system",
}


def main(run: Path, links: Path, out: Path | None):
    kaub = pd.read_csv(links, comment="#", dtype=str)
    keep = set(zip(kaub.seller_id, kaub.buyer_id))
    ft = json.load(open(run / "firm_table.geojson", encoding="utf-8"))
    firms = {str(f["properties"]["id"]): f["properties"] for f in ft["features"]}
    parts = []
    for ch in pd.read_csv(run / "link_data.csv", usecols=COLS, dtype={"seller_id": str, "buyer_id": str}, chunksize=1_000_000):
        z = ch[ch.time_step == 0]
        if len(z):
            parts.append(z[[(s, b) in keep for s, b in zip(z.seller_id, z.buyer_id)]])
        if (ch.time_step > 0).all():
            break
    d = pd.concat(parts)
    L = [f"Kaub-crossing links at t=0: {len(d):,}; value {d.order.sum():,.0f} mUSD/week; {d.delivery_in_tons.sum()/1e3:,.0f} kt/week"]
    imp = d[d.seller_sector == "imports"]
    L.append(f"imports across Kaub: {imp.order.sum():,.0f} mUSD/week = {100*imp.order.sum()/d.order.sum():.0f} % of the value across Kaub; by buyer sector (mUSD/week):")
    L.append(imp.groupby("buyer_sector").order.sum().sort_values(ascending=False).head(10).round(1).to_string())
    for sec, label in [("C19", "REFINERIES"), ("D", "ELECTRICITY AND GAS")]:
        g = imp[imp.buyer_sector == sec]
        L.append(f"\n{label}: imported inputs across Kaub {g.order.sum():,.0f} mUSD/week, {g.delivery_in_tons.sum()/1e3:,.0f} kt/week, cargo classes {sorted(set(g.cargo_type))}")
        for b, gg in g.groupby("buyer_id"):
            p = firms.get(b, {})
            key = (round(float(p.get("lat", 0)), 2), round(float(p.get("long", 0)), 2))
            real = REALITY.get(key, "")
            L.append(f"  {b:>6s} {p.get('name','?'):11s} {p.get('region','?')} lat {key[0]:.2f} lon {key[1]:.2f} importance {float(p.get('importance',0)):7.0f}: "
                     f"{gg.order.sum():6.1f} mUSD/wk {gg.delivery_in_tons.sum()/1e3:6.1f} kt/wk from {','.join(sorted(set(gg.seller_id)))}  {real}")
    ref = d[d.buyer_sector == "C19"]
    L.append(f"\nall deliveries TO refineries across Kaub by seller sector and cargo class (mUSD/week):")
    L.append(ref.groupby(["seller_sector", "cargo_type"]).agg(mUSD=("order", "sum"), kt=("delivery_in_tons", lambda s: s.sum()/1e3), links=("order", "size")).round(1).to_string())
    prod = d[d.seller_sector == "C19"]
    L.append(f"\nrefined products FROM refineries across Kaub (real tank-barge traffic): {prod.order.sum():,.0f} mUSD/week, {prod.delivery_in_tons.sum()/1e3:,.0f} kt/week; buyers: "
             f"{prod.groupby('buyer_sector').order.sum().sort_values(ascending=False).round(0).head(8).to_dict()}")
    text = "\n".join(L)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8"); print("written", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--links", default=str(ROOT / "studies/rhine2026/additional_data/kaub_crossing_links_EU_seed42.csv"))
    ap.add_argument("--out", default=str(ROOT / "studies/rhine2026/additional_data/audit_kaub_imports_2026_cal_base_full.txt"))
    a = ap.parse_args()
    main(Path(a.run), Path(a.links), Path(a.out) if a.out else None)
