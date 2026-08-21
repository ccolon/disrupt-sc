"""Sensitivity summary: every swept parameter ranked by how far it moves the loss.

The small-multiples figure shows each parameter's response in full but gives every
panel its own axis, so effect sizes cannot be compared by eye -- one panel spans a
factor of thirteen and the next a few percent. This ranks them on one axis instead:
a line per parameter from the lowest to the highest mean across its levels, dots at
the levels, ordered by span, with the baseline marked.

The axis is logarithmic because the effects differ by two orders of magnitude, and a
linear axis would compress everything below the largest lever into a single tick.

Reads sensitivity_all.csv (run_grid.py / combine.py).

CLI: python plot_sensitivity_tornado.py <sensitivity_all.csv> [--fig PATH]
     [--metric household_loss_pct_annual_gdp] [--top N]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

NOT_PARAM = {"seed", "oat_param", "household_loss_pct_annual_gdp", "household_loss_mUSD",
             "gdp_loss_pct_annual_gdp", "did_sales_acute", "did_sales_recovery",
             "did_purchases_acute", "did_purchases_recovery"}

NICE = {
    "nb_suppliers_per_input": "suppliers per input",
    "rationing_mode": "rationing rule",
    "shock_scale": "shock size (x baseline)",
    "capital_to_value_added_ratio": "capital/value-added ratio",
    "critical_input_threshold": "materiality floor",
    "firm_inventory_scale": "firm inventories (x)",
    "utilization_rate": "utilization rate",
    "flow_coverage": "network coverage",
    "adaptive_supplier_weight": "supplier reweighting",
    "household_inventory_scale": "household inventories (x)",
    "inventory_restoration_scale": "restocking horizon (x)",
    "time_to_activate_idle_capital": "idle-capital activation (d)",
    "reconstruction_target_time": "reconstruction target (d)",
    "reconstruction_market": "reconstruction on",
    "reconstruction_lag": "reconstruction lag (d)",
    "reconstruction_public_share": "public share of rebuild",
    "reconstruction_locality": "rebuild localization",
    "capacity_constrained_orders": "capacity-capped orders",
    "adaptive_inventories": "adaptive inventories",
    "price_increase_threshold": "price threshold",
    "firm_utility_buffer_days": "buffer: utilities (d)",
    "firm_agriculture_buffer_days": "buffer: agriculture (d)",
    "firm_manufacturing_buffer_days": "buffer: manufacturing (d)",
    "firm_trade_buffer_days": "buffer: trade (d)",
    "firm_transport_buffer_days": "buffer: transport (d)",
    "firm_service_buffer_days": "buffer: services (d)",
}


def oat_rows(df: pd.DataFrame, metric: str):
    """Baseline config and, per parameter, the mean at each of its levels."""
    params = [c for c in df.columns if c not in NOT_PARAM and c != metric]
    grouped = df.groupby(params, dropna=False)[metric].mean().reset_index()
    mode = {p: grouped[p].mode().iloc[0] for p in params}
    grouped["_ndiff"] = sum((grouped[p] != mode[p]).astype(int) for p in params)
    base = grouped.loc[grouped._ndiff.idxmin()]

    out = []
    for p in params:
        others = [q for q in params if q != p]
        sub = grouped.loc[(grouped[others] == base[others]).all(axis=1), [p, metric]]
        if sub[p].nunique() < 2:
            continue
        sub = sub.groupby(p, dropna=False)[metric].mean().sort_index()
        out.append((p, sub))
    return float(base[metric]), out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path)
    ap.add_argument("--metric", default="household_loss_pct_annual_gdp")
    ap.add_argument("--fig", type=Path, default=None)
    ap.add_argument("--top", type=int, default=None, help="keep only the N largest levers")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    baseline, series = oat_rows(df, args.metric)

    series.sort(key=lambda kv: kv[1].max() / max(kv[1].min(), 1e-9))
    if args.top:
        series = series[-args.top:]

    fig, ax = plt.subplots(figsize=(9.5, 0.42 * len(series) + 1.6))
    for i, (p, s) in enumerate(series):
        lo, hi = s.min(), s.max()
        colour = "#b2182b" if hi / max(lo, 1e-9) > 3 else "#4393c3" if hi / max(lo, 1e-9) > 1.3 else "#bdbdbd"
        ax.plot([lo, hi], [i, i], color=colour, lw=2.6, solid_capstyle="round", zorder=2)
        ax.scatter(s.values, [i] * len(s), s=22, color=colour, zorder=3,
                   edgecolors="white", linewidths=0.6)
        ax.annotate(f"{hi / max(lo, 1e-9):.1f}×", xy=(hi, i), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8, color=colour)
        # label the extreme levels so the reader can read the direction
        ax.annotate(f"{s.idxmin()}", xy=(lo, i), xytext=(-6, 0), textcoords="offset points",
                    va="center", ha="right", fontsize=7, color="0.35")

    ax.axvline(baseline, color="0.25", ls="--", lw=1.2, zorder=1)
    ax.annotate(f"baseline {baseline:.2f}%", xy=(baseline, len(series) - 0.3),
                xytext=(4, 0), textcoords="offset points", fontsize=8.5, color="0.25")
    ax.set_yticks(range(len(series)))
    ax.set_yticklabels([NICE.get(p, p.replace("_", " ")) for p, _ in series], fontsize=8.5)
    ax.set_xscale("log")
    ax.set_xlabel("household loss, % of annual GDP (log scale)")
    ax.set_title("Sensitivity of the earthquake household loss to each parameter, "
                 "one at a time from the baseline", loc="left", fontsize=11)
    ax.grid(axis="x", ls=":", color="0.85")
    ax.set_axisbelow(True)
    ax.set_ylim(-0.8, len(series) - 0.2)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()

    out = args.fig or (args.csv.parent / "fig_sensitivity_tornado.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(f"wrote {out}   baseline {baseline:.3f}%   {len(series)} parameters")
    for p, s in reversed(series):
        print(f"  {NICE.get(p, p):<32} {s.min():>7.2f} - {s.max():>7.2f}   "
              f"x{s.max() / max(s.min(), 1e-9):>5.1f}")


if __name__ == "__main__":
    main()
