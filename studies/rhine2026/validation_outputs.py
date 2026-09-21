"""Validation outputs of a full-export Rhine run (17 Sep 2026): what crosses Kaub, what is delivered, at what price.

Reads link_data.csv in chunks (4-8 GB) and the list of links whose baseline route crosses Kaub
(additional_data/kaub_crossing_links_<scope>_seed42.csv, built by build_kaub_links.py from the routes cache; the
list belongs to one supply-chain draw), and writes per week and cargo class, for those links:
  - ordered and delivered tonnage and value (delivered = realized after rationing and transport),
  - the delivered-price ratio (price / equilibrium price) at the median, ninth decile and maximum,
and for all routed links the same totals as context. The baseline week (t = 0) annualised gives the model's
Kaub throughput against the CCNR cross-section (50-60 Mt/yr at Kaub).

Usage:
    python studies/rhine2026/validation_outputs.py <run_folder> --flags additional_data/kaub_crossing_links_EU_seed42.csv [--out out.csv]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

COLS = ["time_step", "seller_id", "buyer_id", "order", "delivery", "realized_delivery", "delivery_in_tons",
        "cargo_type", "price", "eq_price"]


def main(run: Path, flags_path: Path, out: Path | None):
    # either the committed list of Kaub-crossing links (build_kaub_links.py; header lines start with #) or the
    # legacy all-links flag table with a crosses_kaub column
    flags = pd.read_csv(flags_path, dtype=str, comment="#").drop_duplicates(["seller_id", "buyer_id"])
    if "crosses_kaub" in flags.columns:
        flags = flags[flags.crosses_kaub == "True"]
    kaub = set(zip(flags.seller_id, flags.buyer_id))
    print(f"{len(kaub):,} links cross Kaub on their normal route")
    agg = {}          # (t, cargo, group) -> dict of sums
    ratios = {}       # (t, cargo) -> list of arrays of price ratios (Kaub links only, delivered > 0)
    n = 0
    for chunk in pd.read_csv(run / "link_data.csv", usecols=COLS, dtype={"seller_id": str, "buyer_id": str}, chunksize=3_000_000):
        n += len(chunk)
        chunk = chunk[chunk.cargo_type.isin(["container", "dry_bulk", "liquid_bulk"])]
        key = list(zip(chunk.seller_id, chunk.buyer_id))
        chunk = chunk.assign(kaub=[k in kaub for k in key])
        # tons delivered: delivery_in_tons is the shipped tonnage; scale by realized/delivery for the realized part
        with np.errstate(divide="ignore", invalid="ignore"):
            fill = np.where(chunk.delivery > 0, chunk.realized_delivery / chunk.delivery, 0.0)
        chunk = chunk.assign(realized_tons=chunk.delivery_in_tons * fill,
                             order_tons=np.where(chunk.delivery > 0, chunk.delivery_in_tons * chunk.order / chunk.delivery, 0.0))
        for (t, cargo, kb), g in chunk.groupby(["time_step", "cargo_type", "kaub"]):
            d = agg.setdefault((int(t), cargo, "kaub" if kb else "other"), dict(order_usd=0.0, delivery_usd=0.0, realized_usd=0.0, order_tons=0.0, delivered_tons=0.0, n=0))
            d["order_usd"] += g.order.sum(); d["delivery_usd"] += g.delivery.sum(); d["realized_usd"] += g.realized_delivery.sum()
            d["order_tons"] += g.order_tons.sum(); d["delivered_tons"] += g.realized_tons.sum(); d["n"] += len(g)
            if kb:
                dl = g[g.realized_delivery > 1e-9]
                if len(dl):
                    ratios.setdefault((int(t), cargo), []).append((dl.price / dl.eq_price).to_numpy())
        print(f"  {n/1e6:.0f} M rows", flush=True)
    rows = []
    for (t, cargo, grp), d in sorted(agg.items()):
        r = dict(time_step=t, cargo_type=cargo, group=grp, **{k: round(v, 1) for k, v in d.items()})
        r["undelivered_usd"] = round(d["order_usd"] - d["realized_usd"], 1)
        r["delivered_share"] = round(d["realized_usd"] / d["order_usd"], 4) if d["order_usd"] > 0 else np.nan
        if grp == "kaub" and (t, cargo) in ratios:
            x = np.concatenate(ratios[(t, cargo)])
            r["price_ratio_p50"] = round(float(np.median(x)), 4); r["price_ratio_p90"] = round(float(np.quantile(x, 0.9)), 4); r["price_ratio_max"] = round(float(x.max()), 4)
        rows.append(r)
    tab = pd.DataFrame(rows)
    if out:
        tab.to_csv(out, index=False); print("written", out)
    k = tab[tab.group == "kaub"]
    base = k[k.time_step == 0].set_index("cargo_type")
    print("\n== Kaub-crossing links at t=0: weekly tons and annualised Mt ==")
    for c, r in base.iterrows():
        print(f"  {c:12s} {r.order_tons:12,.0f} t/week -> {r.order_tons*52/1e6:6.1f} Mt/yr; value {r.order_usd:8,.0f} mUSD/week")
    print(f"  total        {base.order_tons.sum():12,.0f} t/week -> {base.order_tons.sum()*52/1e6:6.1f} Mt/yr (CCNR Kaub cross-section: about 50-60 Mt/yr)")
    print("\n== Kaub-crossing links by week: delivered share of ordered value, delivered tons vs t=0, price ratio (p50 / p90 / max) ==")
    piv = k.pivot_table(index="time_step", columns="cargo_type", values=["delivered_share", "delivered_tons", "price_ratio_p50", "price_ratio_p90", "price_ratio_max"])
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(piv.round(3).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--flags", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    main(Path(a.run), Path(a.flags), Path(a.out) if a.out else None)
