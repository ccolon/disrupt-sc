"""Compute the model-side numbers for a scope validation report (phase 8).

Reads the newest initial_state export folder (run with `export_files: True`)
plus the scope's inputs, and prints every model-side metric the validation
report needs. The agent supplies the data-side comparisons (Eurostat, national
statistics, port authorities) and writes the report — see
references/validation-report.md.

Usage:
    python validation_metrics.py <Scope> [--run <output subfolder>]
                                 [--repo <disrupt-sc repo>] [--data-root <dir>]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402


def _latest_run(repo: Path, scope: str) -> Path:
    base = repo / "output" / scope
    runs = sorted([p for p in base.iterdir() if p.is_dir()]) if base.exists() else []
    if not runs:
        sys.exit(f"ERROR: no export folder under {base} - run disruptsc with export_files: True")
    return runs[-1]


def _hav_km(a, b) -> float:
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))


def _gateway_groups(countries_gdf) -> dict[str, str]:
    """country region -> gateway label, clustering points within ~20 km."""
    rows = [(r["region"], (r.geometry.x, r.geometry.y), str(r.get("name", r["region"])))
            for _, r in countries_gdf.iterrows()]
    groups: list[dict] = []
    for region, pt, name in rows:
        for grp in groups:
            if _hav_km(pt, grp["pt"]) < 20:
                grp["members"].append(region)
                break
        else:
            groups.append({"pt": pt, "members": [region], "label": name})
    out = {}
    for grp in groups:
        label = grp["label"].split(",")[0][:40]
        for region in grp["members"]:
            out[region] = f"{label} [{'+'.join(grp['members'])}]"
    return out


def _per_year(weekly: float, time_resolution: str) -> float:
    return weekly * {"day": 365, "week": 52, "month": 12, "year": 1}.get(time_resolution, 52)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scope")
    ap.add_argument("--run", default=None, help="output subfolder name (default: newest)")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--time-resolution", default="week",
                    help="time_resolution of the run (converts flows to /yr)")
    args = ap.parse_args()

    repo = Path(args.repo) if args.repo else locate.find_repo_root()
    data_root = Path(args.data_root) if args.data_root else locate.data_root()
    run = (repo / "output" / args.scope / args.run) if args.run else _latest_run(repo, args.scope)
    scope_dir = data_root / args.scope
    tr = args.time_resolution
    print(f"run folder: {run}\n")

    # ---- 1. economic: model vs MRIO --------------------------------------
    ms = pd.read_csv(run / "mrio_by_sector.csv").set_index("sector")
    fd = pd.read_csv(run / "firm_data.csv")
    ms["model_output"] = fd.groupby("sector")["production"].sum().map(lambda v: _per_year(v, tr))
    ms["ratio"] = ms["model_output"] / ms["mrio_output"]
    print("== 1. ECONOMIC: model vs MRIO (per year, MRIO units) ==")
    print(f"gross output: model {ms['model_output'].sum():,.0f} vs MRIO {ms['mrio_output'].sum():,.0f}"
          f"  ({100 * ms['model_output'].sum() / ms['mrio_output'].sum():.1f}%)")
    print(f"MRIO VA {ms['mrio_va'].sum():,.0f} | MRIO final demand {ms['mrio_final_demand'].sum():,.0f}")
    bad = ms[(ms["ratio"] < 0.85) | (ms["ratio"] > 1.15)].sort_values("ratio")
    print(f"sectors within +/-15% of MRIO output: {len(ms) - len(bad)}/{len(ms)}")
    if len(bad):
        print(bad[["mrio_output", "model_output", "ratio"]].round(2).to_string())

    # ---- 2. trade: per-partner kept shares -------------------------------
    # Imports have two channels that must be compared like-for-like:
    #   - final-demand imports: delivered by countries to households; visible as
    #     the country's 'exports' in trade_data (its sales INTO the scope);
    #   - intermediate imports: delivered by countries to firms (KI-16 fix);
    #     visible as firm_data['imports'].
    # mrio_by_country's mrio_imports is intermediates-only - do NOT divide the
    # trade_data number by it (the pre-fix Romania report made that mistake).
    td = pd.read_csv(run / "trade_data.csv")
    td = td[td["time_step"] == td["time_step"].min()]
    mc = pd.read_csv(run / "mrio_by_country.csv").set_index("country")
    ext = td[td["country"].isin(mc.index)].set_index("country")
    mrio = pd.read_csv(scope_dir / "Economic" / "mrio.csv", header=[0, 1], index_col=[0, 1])
    # Import rows: legacy (BLOC, "imports") or sector-resolved (BLOC, sector) —
    # external blocs are the regions that own an "exports" column.
    ext_regions = {t[0] for t in mrio.columns if str(t[1]).lower() == "exports"}
    imp_rows = [t for t in mrio.index
                if str(t[1]).lower() == "imports" or t[0] in ext_regions]
    fd_cols = [t for t in mrio.columns if "final" in str(t[1]).lower()]
    sec_cols = [t for t in mrio.columns
                if t not in fd_cols and str(t[1]).lower() != "exports"]
    mrio_fd_imp = mrio.loc[imp_rows, fd_cols].sum(axis=1).groupby(level=0).sum()
    mrio_int_imp = mrio.loc[imp_rows, sec_cols].sum(axis=1).groupby(level=0).sum()
    firm_imp_total = _per_year(fd["imports"].sum(), tr)
    print("\n== 2. TRADE: kept share per partner (model/yr vs MRIO) ==")
    print("NOTE trade_data semantics: a country's 'exports' = its sales INTO the scope"
          " (scope imports); its 'imports' = its purchases FROM the scope (scope exports).")
    for c in mc.index:
        me = mc.loc[c, "mrio_exports"]
        m_fd = float(mrio_fd_imp.get(c, 0.0))
        yi = _per_year(ext.loc[c, "exports_value"], tr) if c in ext.index else 0.0
        ye = _per_year(ext.loc[c, "imports_value"], tr) if c in ext.index else 0.0
        print(f"  {c}: sales into scope {yi:,.0f} (FD-imp {m_fd:,.0f},"
              f" intermed {float(mrio_int_imp.get(c, 0.0)):,.0f})"
              f" | purchases from scope {ye:,.0f}/{me:,.0f} ({100 * ye / me if me else 0:.0f}%)")
    tot_i, tot_e = ext["exports_value"].sum(), ext["imports_value"].sum()
    mrio_imp_total = mrio_fd_imp.sum() + mrio_int_imp.sum()
    print(f"scope TOTAL imports (countries' sales = FD + firm deliveries): model "
          f"{_per_year(tot_i, tr):,.0f} vs MRIO {mrio_imp_total:,.0f}"
          f" ({100 * _per_year(tot_i, tr) / mrio_imp_total:.0f}%)"
          f"  [MRIO split: FD {mrio_fd_imp.sum():,.0f} + intermediates {mrio_int_imp.sum():,.0f}]")
    print(f"  of which firm intermediate imports: model {firm_imp_total:,.0f} vs MRIO "
          f"{mrio_int_imp.sum():,.0f} ({100 * firm_imp_total / mrio_int_imp.sum():.0f}%)"
          + ("  << ZERO: firms receive no imported inputs (KI-16 unfixed?)"
             if firm_imp_total == 0 else ""))
    print(f"scope exports: model {_per_year(tot_e, tr):,.0f} vs MRIO {mc['mrio_exports'].sum():,.0f}"
          f" ({100 * _per_year(tot_e, tr) / mc['mrio_exports'].sum():.0f}%)")

    # ---- 3. gateway shares ----------------------------------------------
    import geopandas as gpd
    cg = gpd.read_file(scope_dir / "Spatial" / "countries.geojson")
    gw = _gateway_groups(cg)
    ext2 = ext.copy()
    ext2["gateway"] = [gw.get(c, c) for c in ext2.index]
    print("\n== 3. GATEWAYS: % of trade value ==")
    gi = ext2.groupby("gateway")["exports_value"].sum()
    ge = ext2.groupby("gateway")["imports_value"].sum()
    for name in sorted(set(gi.index) | set(ge.index)):
        print(f"  {name}: imports {100 * gi.get(name, 0) / (gi.sum() or 1):.1f}%"
              f" | exports {100 * ge.get(name, 0) / (ge.sum() or 1):.1f}%")
    mc2 = mc.copy()
    mc2["gateway"] = [gw.get(c, c) for c in mc2.index]
    mgi = mc2.groupby("gateway")["mrio_imports"].sum()
    mge = mc2.groupby("gateway")["mrio_exports"].sum()
    print("  -- MRIO-implied (pre-flow_coverage) --")
    for name in sorted(set(mgi.index)):
        print(f"  {name}: imports {100 * mgi.get(name, 0) / (mgi.sum() or 1):.1f}%"
              f" | exports {100 * mge.get(name, 0) / (mge.sum() or 1):.1f}%")

    # ---- 4. modal split from edge flows ----------------------------------
    flow_files = sorted(run.glob("transport_edges_with_flows_*.geojson"))
    if not flow_files:
        print("\nWARN: no transport_edges_with_flows_*.geojson - skipping flow metrics")
        return 0
    g_all = gpd.read_file(flow_files[0])
    # Foreign (TEN-T extension) edges carry foreign=1: exclude them from the
    # DOMESTIC modal split - Eurostat inland splits are on-territory.
    if "foreign" in g_all.columns:
        g = g_all[g_all["foreign"].fillna(0) != 1].copy()
        print(f"\n(excluding {len(g_all) - len(g)} foreign/TEN-T edges from domestic stats)")
    else:
        g = g_all
    g["tonkm"] = g["flow_total_tons"] * g["km"]
    agg = g.groupby("type")[["flow_total", "flow_total_tons", "tonkm"]].sum()
    inland_modes = [m for m in ("roads", "railways", "waterways") if m in agg.index]
    inland = agg.loc[inland_modes]
    print("\n== 4. MODAL SPLIT ==")
    print("per-mode totals (value/period, tons/period, ton-km/period):")
    print(agg.round(0).to_string())
    print("inland split (ton-km): "
          + ", ".join(f"{m} {100 * v / inland['tonkm'].sum():.1f}%"
                      for m, v in inland["tonkm"].items()))
    print("annualized bn ton-km: "
          + ", ".join(f"{m} {_per_year(v, tr) / 1e9:.1f}" for m, v in agg["tonkm"].items()))
    if "multimodal" in g["type"].values:
        mm = g[g["type"] == "multimodal"]
        active = mm[mm["flow_total"] > 0]
        print(f"connectors active: {len(active)}/{len(mm)}; value by pair: "
              + str(active.groupby("multimodes")["flow_total"].sum().round(0).to_dict()))

    # ---- 4b. border crossings (TEN-T-extended networks) ------------------
    # Stitch edges bridge the foreign network to the domestic one - exactly
    # one per crossing and mode, so their flows ARE the border assignment.
    if "special" in g_all.columns:
        st = g_all[g_all["special"].isin(["stitch", "bridge"])]
        if len(st):
            GAZ = {"Nadlac/Curtici": (20.9, 46.2), "Bors/Episcopia": (21.9, 47.1),
                   "Petea/Halmeu": (23.1, 47.9), "Siret/Vicsani": (26.1, 47.9),
                   "Albita/Galati-MD": (28.1, 45.8), "Giurgiu-Ruse": (25.9, 43.8),
                   "Calafat-Vidin": (22.9, 44.0), "Moravita/Stamora": (21.3, 45.3),
                   "Danube@PortileDeFier": (21.8, 44.7), "Negru Voda/Durankulak": (28.2, 43.8),
                   "Danube upstream (Iron Gates)": (20.4, 45.0)}
            def _gz(geom):
                c = geom.centroid
                best = min(GAZ, key=lambda k: (GAZ[k][0]-c.x)**2 + (GAZ[k][1]-c.y)**2)
                d2 = (GAZ[best][0]-c.x)**2 + (GAZ[best][1]-c.y)**2
                return best if d2 < 1.0 else f"({c.x:.1f},{c.y:.1f})"
            st = st.assign(crossing=[_gz(x) for x in st.geometry])
            agg = st.groupby(["crossing", "type"])[["flow_total", "flow_total_tons"]].sum()
            agg = agg[agg["flow_total"] > 0]
            print("\n== 4b. BORDER-CROSSING ASSIGNMENT (flows on stitch/bridge edges) ==")
            print(agg.round(0).to_string())
            bym = st.groupby("type")[["flow_total", "flow_total_tons"]].sum()
            print("cross-border mode split (value): "
                  + ", ".join(f"{m} {100*v/bym['flow_total'].sum():.1f}%"
                              for m, v in bym["flow_total"].items() if bym['flow_total'].sum() > 0))
            print("cross-border mode split (tons):  "
                  + ", ".join(f"{m} {100*v/bym['flow_total_tons'].sum():.1f}%"
                              for m, v in bym["flow_total_tons"].items() if bym['flow_total_tons'].sum() > 0))

    # ---- 5. hub nodes by throughput --------------------------------------
    thr: dict = {}
    for _, r in g.iterrows():
        for e in (r["end1"], r["end2"]):
            thr[e] = thr.get(e, 0.0) + r["flow_total"]
    nodes = gpd.read_file(run / "transport_nodes.geojson")
    key = "id" if "id" in nodes.columns else None
    nodes["throughput"] = (nodes[key] if key else nodes.index).map(thr)
    top = nodes.nlargest(12, "throughput")
    print("\n== 5. TOP NODES BY THROUGHPUT (name them by nearest city/port) ==")
    for _, r in top.iterrows():
        print(f"  {r['throughput']:10.0f}  ({r.geometry.x:.3f}, {r.geometry.y:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
