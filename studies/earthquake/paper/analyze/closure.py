"""National-accounting closure check for a DisruptSC run.

Tests, step by step and cumulated, the identity

    VA  =  C + G + I + X - M + dInventories

where every term is measured inside the model rather than imputed:

    VA   true value added: production - inputs actually drawn from inventory
         (firm_data: production, input_consumed)
    C    household consumption as consumed, not as purchased (tot_consumption)
    G,I  government / investment receipts (the two representative buyers)
    I    also includes reconstruction_sales: private capital goods delivered to
         rebuilding, an investment flow funded outside the household budget
    X    goods received by country agents from domestic firms (qty_received)
    M    goods received from country agents, buyer side: firm imports +
         household/government/investment imports
    dInv change in firm input stocks + firm finished-goods stocks + household
         inventories (accumulation positive, as inventory investment)

The one intended exception is the capital account: the publicly-financed share
of reconstruction restores capital directly, with no goods flow, so rebuilt
capital exceeds the reconstruction goods actually produced. The report
quantifies that stock-without-flow entry instead of hiding it in the residual.

Also reported: the fixed-coefficient VA proxy used elsewhere in the paper
(output loss x MRIO value-added share) against the true-VA loss, and the
buyer-side M against the seller-side country qty_sold as a cross-check.

CLI:
    python closure.py <run_dir> [--out closure_table.csv]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def closure_table(run_dir: Path) -> pd.DataFrame:
    fd = pd.read_csv(run_dir / "firm_data.csv")
    hh = pd.read_csv(run_dir / "household_data.csv")
    cd = pd.read_csv(run_dir / "country_data.csv")

    needed = {"input_consumed", "imports", "input_stock", "reconstruction_sales"}
    missing = needed - set(fd.columns)
    if missing:
        raise SystemExit(f"firm_data.csv lacks {sorted(missing)}: re-run with the "
                         "instrumented model (closure fields added 2026-08).")

    f = fd.groupby("time_step").agg(
        production=("production", "sum"),
        input_consumed=("input_consumed", "sum"),
        imports_firms=("imports", "sum"),
        input_stock=("input_stock", "sum"),
        product_stock=("product_stock", "sum"),
        recon_sales=("reconstruction_sales", "sum"),
        capital=("active_capital", "sum"),
        idle=("idle_capital", "sum"),
    )
    f["capital"] += f.pop("idle")

    is_hh = hh.household.str.startswith("hh")
    h = (hh[is_hh].groupby("time_step")
           .agg(C=("tot_consumption", "sum"), imports_hh=("imports", "sum"),
                hh_stock=("inventory_total", "sum")))
    g = (hh[hh.household == "government"].groupby("time_step")
           .agg(G=("tot_consumption", "sum"), imports_gov=("imports", "sum")))
    i = (hh[hh.household == "investment"].groupby("time_step")
           .agg(I=("tot_consumption", "sum"), imports_inv=("imports", "sum")))
    c = cd.groupby("time_step").agg(X=("qty_received", "sum"),
                                    M_seller_side=("qty_sold", "sum"))

    t = pd.concat([f, h, g, i, c], axis=1).fillna(0.0)
    t["VA"] = t.production - t.input_consumed
    t["M"] = t.imports_firms + t.imports_hh + t.imports_gov + t.imports_inv
    t["dInv"] = (t.input_stock + t.product_stock + t.hh_stock).diff()
    t["demand_side"] = t.C + t.G + t.I + t.recon_sales + t.X - t.M + t.dInv
    t["residual"] = t.VA - t.demand_side

    # capital account: rebuilt = dK + destruction; public rebuild = rebuilt - goods flow
    t["dK"] = t.capital.diff()
    t["rebuilt"] = t.dK.clip(lower=0.0)          # destruction step has dK < 0
    t["rebuilt_public"] = (t.rebuilt - t.recon_sales).clip(lower=0.0)
    return t


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    t = closure_table(args.run_dir)
    post = t.loc[t.index >= 1]

    print(f"{'t':>3} {'VA':>9} {'C':>9} {'G':>7} {'I':>7} {'recon':>6} {'X':>8} "
          f"{'M':>8} {'dInv':>8} {'residual':>9}")
    for ts, r in post.iterrows():
        print(f"{ts:>3} {r.VA:>9.1f} {r.C:>9.1f} {r.G:>7.1f} {r.I:>7.1f} "
              f"{r.recon_sales:>6.1f} {r.X:>8.1f} {r.M:>8.1f} {r.dInv:>8.1f} "
              f"{r.residual:>9.4f}")

    cum = post.sum()
    va_scale = max(abs(cum.VA), 1e-9)
    print("\ncumulated over the horizon (model monetary units):")
    print(f"  VA {cum.VA:,.1f} = C {cum.C:,.1f} + G {cum.G:,.1f} + I {cum.I:,.1f} "
          f"+ recon {cum.recon_sales:,.1f} + X {cum.X:,.1f} - M {cum.M:,.1f} "
          f"+ dInv {cum.dInv:,.1f}")
    print(f"  residual: {cum.residual:,.4f}  ({100 * cum.residual / va_scale:.5f}% of VA)")
    print(f"  max |step residual|: {post.residual.abs().max():.4f}")
    print(f"  M buyer-side vs seller-side: {cum.M:,.1f} vs {cum.M_seller_side:,.1f} "
          f"(gap {cum.M - cum.M_seller_side:+.4f})")
    print(f"\ncapital account (the intended stock-without-flow exception):")
    print(f"  rebuilt {cum.rebuilt:,.1f} = private goods {cum.recon_sales:,.1f} "
          f"+ public, no flow {cum.rebuilt_public:,.1f}")

    # loss-form summary against equilibrium (t=0 levels), for the paper
    eq = t.loc[0]
    n = len(post)
    print(f"\nloss form (equilibrium x {n} steps minus realized, cumulated):")
    for name, col in [("VA", "VA"), ("C", "C"), ("G", "G"), ("I", "I"),
                      ("X", "X"), ("M", "M")]:
        print(f"  {name:>2} loss {n * eq[col] - cum[col]:>10.1f}")
    print(f"  recon adds {cum.recon_sales:>8.1f}   inventories release "
          f"{-cum.dInv:>8.1f}   (dInv = {cum.dInv:.1f})")

    if args.out:
        t.to_csv(args.out)
        print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
