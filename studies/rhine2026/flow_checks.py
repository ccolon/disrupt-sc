"""Rhine-specific flow checks on an EU run: tonnage per named Rhine segment vs
the normal-year capacities table, per-country modal split vs Eurostat, and
the busiest nodes named by a small gazetteer.

Usage:
    python studies/rhine2026/flow_checks.py [--run <output subfolder>] [--scope EU]
Reads <repo>/output/<scope>/<run>/transport_edges_with_flows_0.geojson and
transport_nodes.geojson; annualises weekly flows (x52).
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

GAZETTEER = {  # lon, lat
    "Rotterdam": (4.33, 51.87), "Antwerp": (4.40, 51.27), "Hamburg": (9.99, 53.53),
    "Bremerhaven": (8.55, 53.55), "Le Havre": (0.13, 49.49), "Marseille-Fos": (4.90, 43.40),
    "Genoa": (8.93, 44.41), "Trieste": (13.76, 45.65), "Koper": (13.73, 45.55),
    "Venice": (12.30, 45.45), "Piraeus": (23.63, 37.94), "Algeciras": (-5.44, 36.13),
    "Valencia": (-0.33, 39.45), "Barcelona": (2.15, 41.35), "Sines": (-8.87, 37.95),
    "Gdansk": (18.65, 54.40), "Constanta": (28.65, 44.17), "Gothenburg": (11.95, 57.70),
    "Zeebrugge": (3.20, 51.33), "Dunkirk": (2.35, 51.04), "Dover": (1.35, 51.12),
    "Gibraltar strait": (-5.6, 35.97), "Suez / Port Said": (32.3, 31.0), "Gulf of Suez": (32.33, 29.64),
    "Atlantic west edge": (-32.0, 50.0), "Duisburg": (6.75, 51.43), "Basel": (7.59, 47.56),
    "Ludwigshafen": (8.44, 49.48), "Karlsruhe": (8.40, 49.01), "Cologne": (6.96, 50.94),
    "Munich": (11.58, 48.14), "Nuremberg": (11.08, 49.45), "Vienna": (16.37, 48.21),
    "Milan": (9.19, 45.46), "Paris": (2.35, 48.86), "Lyon": (4.84, 45.76), "Madrid": (-3.70, 40.42),
    "Warsaw": (21.01, 52.23), "Prague": (14.42, 50.09), "Frankfurt": (8.68, 50.11),
    "Brenner": (11.51, 47.00), "Kufstein": (12.17, 47.58), "Strasbourg": (7.75, 48.58),
    "Adriatic (Ancona-Split lane)": (16.0, 43.0), "Lobith/Emmerich": (6.15, 51.85),
}

EUROSTAT_2023 = {  # % of inland tkm road / rail / IWW (tran_hv_frmod)
    "EU27": (78.1, 16.9, 5.0), "DE": (72.8, 20.6, 6.6), "NL": (52.8, 6.4, 40.9), "BE": (77.6, 11.7, 10.7),
    "FR": (88.9, 9.2, 1.9), "AT": (68.9, 29.3, 1.7), "CH": (65.6, 34.3, 0.1), "PL": (75.8, 24.1, 0.0),
    "IT": (88.0, 12.0, 0.0), "RO": (53.7, 24.0, 22.3),
}


def hav_km(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(math.sin((lat2 - lat1) / 2) ** 2
                                          + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))


def nearest_name(lon, lat):
    best = min(GAZETTEER.items(), key=lambda kv: hav_km((lon, lat), kv[1]))
    d = hav_km((lon, lat), best[1])
    return f"{best[0]} ({d:.0f} km)" if d < 150 else f"({lon:.2f}, {lat:.2f})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="EU")
    ap.add_argument("--run", default=None)
    ap.add_argument("--periods-per-year", type=float, default=52.0)
    args = ap.parse_args()
    out_root = ROOT / "output" / args.scope
    run = args.run or sorted(p.name for p in out_root.iterdir() if p.is_dir())[-1]
    folder = out_root / run
    e = gpd.read_file(folder / "transport_edges_with_flows_0.geojson")
    ppy = args.periods_per_year
    tons_col = next(c for c in e.columns if c in ("flow_total_tons", "flow_tons", "tons"))
    e["tons_yr"] = e[tons_col] * ppy
    e["tkm_yr"] = e["tons_yr"] * e["km"]
    print(f"run {run}: {len(e)} edges; columns with flows: {[c for c in e.columns if c.startswith('flow')][:8]}")

    # 1. Rhine segments vs normal-year capacities
    caps = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv").set_index("name")
    # a named segment may consist of several edges in series, each carrying the
    # whole flow: take the tonnage-weighted mean per km (not the sum over edges)
    rhe = e[e["name"].astype(str).str.startswith("rhine")]
    grp = rhe.groupby("name")
    rh = (grp["tkm_yr"].sum() / grp["km"].sum()) / 1e6
    n_edges = grp.size()
    order = list(caps.index)
    tab = pd.DataFrame({"edges": n_edges.reindex(order), "model_Mt": rh.reindex(order).round(1),
                        "normal_Mt": caps["mt_per_year"]})
    tab["ratio"] = (tab["model_Mt"] / tab["normal_Mt"]).round(2)
    print("\n== 1. RHINE SEGMENTS: model tonnage (Mt/yr, km-weighted over the segment's edges) vs normal-year (CCNR/estimates) ==")
    print(tab.to_string())

    # 2. per-country modal split from the TEN-T country_code of each edge
    # (GeoDataFrame.type is the GEOMETRY type - always index the column)
    inland = e[e["type"].isin(["roads", "railways", "waterways"])].copy()
    inland["cc"] = inland["country_code"].astype(str).str.split(";").str[0].str.strip()
    print("\n== 2. MODAL SPLIT by edge country (% of inland tkm, model vs Eurostat 2023 road/rail/IWW) ==")
    rows = []
    for cc, sub in inland.groupby("cc"):
        tot = sub.tkm_yr.sum()
        if tot <= 0:
            continue
        sh = {m: 100 * sub.loc[sub["type"] == m, "tkm_yr"].sum() / tot for m in ("roads", "railways", "waterways")}
        tgt = EUROSTAT_2023.get(cc)
        rows.append((cc, round(tot / 1e9, 1), round(sh["roads"], 1), round(sh["railways"], 1), round(sh["waterways"], 1),
                     tgt[0] if tgt else None, tgt[1] if tgt else None, tgt[2] if tgt else None))
    df = pd.DataFrame(rows, columns=["cc", "bn_tkm", "road", "rail", "iww", "es_road", "es_rail", "es_iww"]).set_index("cc")
    tot = inland.tkm_yr.sum()
    print(df.sort_values("bn_tkm", ascending=False).head(14).to_string())
    print(f"EU total inland: {tot/1e9:.0f} bn tkm/yr; shares road {100*inland.loc[inland['type']=='roads','tkm_yr'].sum()/tot:.1f} / "
          f"rail {100*inland.loc[inland['type']=='railways','tkm_yr'].sum()/tot:.1f} / IWW {100*inland.loc[inland['type']=='waterways','tkm_yr'].sum()/tot:.1f} "
          f"vs Eurostat EU27 {EUROSTAT_2023['EU27']} (real ~2,400 bn tkm incl. short-haul road)")

    # 3. busiest nodes, named
    nodes_path = folder / "transport_nodes.geojson"
    if nodes_path.exists():
        n = gpd.read_file(nodes_path)
        tcol = next((c for c in n.columns if "throughput" in c or c in ("flow_total", "tons")), None)
        if tcol:
            top = n.nlargest(12, tcol)
            print(f"\n== 3. TOP NODES by {tcol} ==")
            for _, r in top.iterrows():
                print(f"  {r[tcol]:>12,.0f}  {nearest_name(r.geometry.x, r.geometry.y)}")
    # 4. port entries: maritime->land connectors by tons
    mm = e[(e["type"] == "multimodal") & e["multimodes"].astype(str).str.contains("maritime")].copy()
    if len(mm):
        mm["port"] = [nearest_name(g.centroid.x, g.centroid.y) for g in mm.geometry]
        ports = mm.groupby("port")["tons_yr"].sum().sort_values(ascending=False) / 1e6
        print("\n== 4. PORT CONNECTOR TONNAGE (Mt/yr, model) - Eurostat 2023: Rotterdam 402, Antwerp-Bruges 242, Hamburg ~110, Marseille ~70, Algeciras ~95, Valencia ~80, Trieste ~55, Piraeus ~45 ==")
        print(ports.head(15).round(1).to_string())


if __name__ == "__main__":
    main()
