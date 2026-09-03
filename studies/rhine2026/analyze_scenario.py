"""Scenario analysis for a Rhine low-water run against the evidence targets.

Reads a disruption-run export folder (run_rhine.py) and prints, per week:
  1. Rhine tonnage at Kaub vs the fleet's physical capacity at that week's gauge
     (the ex post consistency check of the cost-shock multipliers);
  2. tonnage on the Rhine valley rail and road corridors (substitution) and the
     rail/road/barge tons on the Kaub-parallel corridor vs DB Cargo's ~100-barge ceiling;
  3. share of Rhine-corridor firms (within --corridor-km of the Rhine chain)
     producing below 99 % / 90 % / at 0 % of their baseline (DIHK survey 29 Jul–4 Aug:
     ~33 % restricting, 6 % stopped);
  4. price surcharges on links (price / eq_price − 1): share of links above +10 % /
     +25 % / +50 % and the maximum (observed freight rates ×2–5, logistics costs
     +25 % for half of the exposed firms, +50 % for a third);
  5. weekly production and value-added loss by country (VA share by sector from
     mrio_by_sector.csv), cumulated, vs the ex ante range −0.1 to −0.4 pp of quarterly
     German GDP;
  6. routing summary (main / rerouted / blocked value by cargo type).

Usage:
    python studies/rhine2026/analyze_scenario.py <run folder> [--profile 2026] [--corridor-km 40]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
KAUB_EDGE = "rhine_mainz_koblenz"


def weekly_edge_tons(run: Path, names: set[str]) -> pd.DataFrame:
    """tons per week (period) on the named edges, from transport_edges_with_flows_<t>.geojson."""
    rows = []
    for f in sorted(run.glob("transport_edges_with_flows_*.geojson"), key=lambda p: int(p.stem.split("_")[-1])):
        t = int(f.stem.split("_")[-1])
        g = gpd.read_file(f, columns=["id", "name", "type", "km", "country_code", "flow_total_tons", "geometry"])
        sub = g[g["name"].isin(names)]
        for _, r in sub.iterrows():
            rows.append({"time_step": t, "name": r["name"], "type": r["type"], "tons": r["flow_total_tons"]})
        # corridor totals by mode within the Rhine bbox (DE/NL, lon 5.5-9.5, lat 47.5-52.2)
        bb = g.cx[5.5:9.5, 47.5:52.2]
        for mode in ("roads", "railways", "waterways"):
            rows.append({"time_step": t, "name": f"corridor_{mode}_tkm", "type": mode,
                         "tons": float((bb.loc[bb["type"] == mode, "flow_total_tons"] * bb.loc[bb["type"] == mode, "km"]).sum())})
    return pd.DataFrame(rows)


def fleet_capacity(profile: str, kaub_tpd: float) -> pd.DataFrame:
    prof = pd.read_csv(HERE / "scenarios" / f"{profile}.csv")
    dt = pd.read_csv(HERE / "scenarios" / "draught_table.csv").sort_values("kaub_cm")
    if "load_factor" in prof.columns:
        lf = prof["load_factor"].astype(float).clip(0, 1).to_numpy()
    else:
        lf = np.interp(prof["kaub_cm"].astype(float), dt["kaub_cm"], dt["load_factor"],
                       left=dt["load_factor"].iloc[0], right=dt["load_factor"].iloc[-1])
    out = pd.DataFrame({"time_step": range(1, len(prof) + 1), "week_start": prof.get("week_start", ""),
                        "kaub_cm": prof.get("kaub_cm", np.nan), "capacity_factor": lf,
                        "fleet_capacity_t_per_week": lf * kaub_tpd * 7})
    return out



def _price_section(run: Path) -> None:
    ld = pd.read_csv(run / "link_data.csv", usecols=["time_step", "seller_region", "buyer_region", "order", "realized_delivery",
                                                     "delivery_in_tons", "cargo_type", "eq_price", "price"])
    ld["surcharge"] = ld["price"] / ld["eq_price"] - 1
    active = ld[ld["order"] > 0]
    ps = active.groupby("time_step")["surcharge"].agg(
        links="size", above_10pct=lambda s: (100 * (s > 0.10).mean()).round(1),
        above_25pct=lambda s: (100 * (s > 0.25).mean()).round(1), above_50pct=lambda s: (100 * (s > 0.50).mean()).round(1),
        max=lambda s: round(100 * s.max(), 0))
    fill = active.groupby("time_step").apply(lambda d: round(100 * d["realized_delivery"].sum() / d["order"].sum(), 2))
    ps["fill_rate_%"] = fill
    print("\n== 4. LINK PRICES: % of active links with delivered-price surcharge above thresholds; max (%); fill rate ==")
    print("   (2026: logistics costs +25 % for half of the exposed firms, +50 % for a third; freight rates x2-5)")
    print(ps.to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--profile", default="2026")
    ap.add_argument("--no-links", action="store_true", help="skip the link_data.csv section (multi-GB file)")
    ap.add_argument("--corridor-km", type=float, default=40.0)
    args = ap.parse_args()
    run = Path(args.run)
    if not run.exists():
        run = ROOT / "runs" / "rhine2026" / args.run
    print(f"run: {run}")

    # --- 1. Kaub tonnage vs fleet capacity ---
    caps = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv").set_index("name")
    kaub_tpd = float(caps.loc[KAUB_EDGE, "tons_per_day"])
    rhine_names = set(caps.index)
    have_flows = any(run.glob("transport_edges_with_flows_*.geojson"))
    if have_flows:
        et = weekly_edge_tons(run, rhine_names | set())
        kaub = et[et["name"] == KAUB_EDGE].set_index("time_step")["tons"]
        fc = fleet_capacity(args.profile, kaub_tpd).set_index("time_step")
        tab = pd.DataFrame({"week_start": fc["week_start"], "kaub_cm": fc["kaub_cm"],
                            "capacity_factor": fc["capacity_factor"].round(2),
                            "fleet_cap_kt": (fc["fleet_capacity_t_per_week"] / 1e3).round(0),
                            "model_kt": (kaub.reindex(fc.index) / 1e3).round(0)})
        tab["model/fleet"] = (tab["model_kt"] / tab["fleet_cap_kt"]).round(2)
        base = kaub.get(0, np.nan)
        print(f"\n== 1. KAUB EDGE: weekly tons (kt) vs fleet capacity at the gauge; baseline t=0 = {base/1e3:,.0f} kt/week ==")
        print(tab.to_string())
        over = tab[tab["model/fleet"] > 1.0]
        if len(over):
            print(f"  WEEKS ABOVE PHYSICAL CAPACITY: {list(over.index)} -> multipliers too low there")

        # --- 2. corridor substitution ---
        corr = et[et["name"].str.startswith("corridor_")].pivot(index="time_step", columns="name", values="tons")
        corr = corr / 1e6
        corr.columns = [c.replace("corridor_", "").replace("_tkm", " Mtkm") for c in corr.columns]
        rel = (corr / corr.iloc[0] * 100).round(1)
        print("\n== 2. RHINE-BASIN CORRIDOR (lon 5.5-9.5, lat 47.5-52.2): weekly tkm by mode, % of baseline ==")
        print(rel.to_string())
    else:
        print("\n== 1-2. no transport_edges_with_flows_*.geojson (flows are exported at the end of a run) - skipped ==")

    # --- 3. corridor firms below baseline ---
    ft = gpd.read_file(run / "firm_table.geojson")
    edges = gpd.read_file(run / "transport_edges.geojson")
    rhine = edges[edges["name"].isin(rhine_names)].to_crs(3035)
    corridor = rhine.buffer(args.corridor_km * 1000).unary_union
    ft_m = ft.to_crs(3035)
    ft["corridor"] = ft_m.geometry.within(corridor)
    ft["firm"] = ft.index if "id" not in ft.columns else ft["id"]
    fd = pd.read_csv(run / "firm_data.csv")
    base_prod = fd[fd["time_step"] == 0].set_index("firm")["production"]
    fd["base"] = fd["firm"].map(base_prod)
    fd["ratio"] = fd["production"] / fd["base"].replace(0, np.nan)
    corridor_ids = set(ft.loc[ft["corridor"], "firm"].astype(fd["firm"].dtype, errors="ignore"))
    fdc = fd[fd["firm"].isin(corridor_ids) & (fd["base"] > 0)]
    if fdc.empty:  # firm ids may be strings vs ints - retry on names
        name_col = "name" if "name" in ft.columns else None
        print("  (corridor firm matching by id failed; check firm id fields)")
    g = fdc.groupby("time_step")["ratio"]
    share = pd.DataFrame({"n_firms": g.size(), "below_99%": (100 * g.apply(lambda s: (s < 0.99).mean())).round(1),
                          "below_90%": (100 * g.apply(lambda s: (s < 0.90).mean())).round(1),
                          "stopped(<1%)": (100 * g.apply(lambda s: (s < 0.01).mean())).round(1),
                          "mean_ratio": (100 * g.mean()).round(1)})
    print(f"\n== 3. FIRMS WITHIN {args.corridor_km:.0f} KM OF THE RHINE ({len(corridor_ids)} firms): % below baseline production ==")
    print("   (DIHK survey 29 Jul-4 Aug 2026, Kaub 20-30 cm: ~33 % restricting production, 6 % stopped)")
    print(share.to_string())

    # --- 3b. cascade signature: firms at (near) zero output with full order books ---
    fd_all = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production",
                                                          "production_target", "total_order"])
    b0 = fd_all[fd_all["time_step"] == 0].set_index("firm")["production"]
    fd_all["base"] = fd_all["firm"].map(b0)
    live = fd_all[fd_all["base"] > 1.0]
    coll = live[(live["production"] < 0.01 * live["base"]) & (live["total_order"] > 0.5 * live["base"])]
    sig = coll.groupby("time_step").agg(firms=("firm", "size"), lost_output=("base", "sum"))
    sig["lost_output_%_of_EU"] = (100 * sig["lost_output"] / b0[b0 > 1.0].sum()).round(3)
    print("\n== 3b. CASCADE SIGNATURE: firms (baseline > 1 mUSD/week) producing < 1 % of baseline with orders > 50 % of baseline ==")
    print("   (run 1 of 3 Sep: hundreds of service firms by week 3 under strict Leontief — an artefact, see KI-29)")
    print(sig.to_string() if len(sig) else "   none")
    if len(coll):
        print("   by sector (all weeks):", coll.groupby("sector").size().sort_values(ascending=False).head(8).to_dict())

    # --- 4. price surcharges ---
    if args.no_links:
        print("\n== 4. link prices skipped (--no-links) ==")
    else:
        _price_section(run)

    # --- 5. production / value-added loss by country ---
    va = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    va_share = (va["mrio_va"] / va["mrio_output"]).to_dict()
    fd["va_share"] = fd["sector"].map(va_share).fillna(0.3)
    fd["loss"] = (fd["base"] - fd["production"]).clip(lower=0)
    fd["va_loss"] = fd["loss"] * fd["va_share"]
    by = fd.groupby(["time_step", "region"])["va_loss"].sum().unstack("region")
    va_region = pd.read_csv(run / "mrio_by_region.csv").set_index("region")["mrio_va"]
    weekly_va = va_region / 52.0
    pct = (100 * by / weekly_va).round(2)
    keep = [c for c in ["DEU", "NLD", "CHE", "FRA", "BEL", "AUT", "ITA", "POL"] if c in pct.columns]
    print("\n== 5. VALUE-ADDED LOSS as % of the country's weekly value added (production shortfall x sector VA share) ==")
    print(pct[keep].to_string())
    tot = by.sum(axis=1)
    eu_weekly = weekly_va.sum()
    print(f"   EU total: cumulated VA loss over the run {tot.sum():,.0f} mUSD = {100*tot.sum()/(eu_weekly*13):.2f} % of one quarter of EU VA")
    if "DEU" in by.columns:
        de = by["DEU"].sum()
        print(f"   DEU: cumulated {de:,.0f} mUSD = {100*de/(weekly_va['DEU']*13):.2f} % of one quarter of German VA "
              f"(ex ante estimates: -0.1 to -0.4 pp of Q3 GDP)")

    # --- 6. routing summary ---
    if not (run / "routing_summary.csv").exists():
        print("\n== 6. no routing_summary.csv yet (written at the end of a run) - skipped ==")
        return
    rs = pd.read_csv(run / "routing_summary.csv")
    piv = rs.pivot_table(index="time_step", columns="cargo_type", values=["alternative_usd", "blocked_usd"], aggfunc="sum")
    tot_usd = rs.groupby("time_step")["total_usd"].sum()
    print("\n== 6. ROUTING: rerouted and blocked value (% of routed value) ==")
    out = pd.DataFrame({"rerouted_%": (100 * rs.groupby("time_step")["alternative_usd"].sum() / tot_usd).round(2),
                        "blocked_%": (100 * rs.groupby("time_step")["blocked_usd"].sum() / tot_usd).round(2)})
    print(out.to_string())


if __name__ == "__main__":
    main()
