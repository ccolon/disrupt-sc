"""Port throughput capacities for the EU scope's maritime connectors.

The unconstrained model lets any port absorb any tonnage, so Asian imports
pile into the Adriatic (Trieste 183 Mt/yr modelled vs 55 real) while Antwerp
carries 55 Mt (real 242). The physical fix is a per-terminal capacity: each
TEN-T port connector (multimodal edge named by its terminal_id) gets the
real annual throughput of the port it serves (Eurostat mar_go_aa, gross
weight handled, 2023) x a peak factor, as tons/day, to be applied through
``transport_capacity_overrides`` with ``capacity_constraint: binary`` (no
cost distortion below capacity; over-capacity edges are simply not routed).

Ports are matched by name from Eurostat's rep_mar labels to a gazetteer of
port coordinates, then to every maritime connector within ``--radius-km``;
a port with several connectors shares its throughput across them (equal
split). Connectors serving no listed port keep the default capacity.

Usage:
    python studies/rhine2026/port_capacities.py [--radius-km 12] [--peak 1.3]
Writes disrupt-sc-data/EU/Transport/port_capacities.csv and prints the YAML
block for transport_capacity_overrides.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT.parent / "disrupt-sc-data" / "EU"

# name fragment (lower-case, matched against the Eurostat label) -> lon, lat
PORTS = {
    "rotterdam": (4.20, 51.93), "antwerp": (4.33, 51.28), "hamburg": (9.93, 53.53), "amsterdam": (4.80, 52.41),
    "algeciras": (-5.43, 36.13), "marseille": (4.95, 43.40), "valencia": (-0.32, 39.44), "bremerhaven": (8.53, 53.57),
    "bremen": (8.53, 53.57), "le havre": (0.15, 49.48), "piraeus": (23.62, 37.94), "genova": (8.92, 44.41),
    "genoa": (8.92, 44.41), "barcelona": (2.16, 41.34), "trieste": (13.75, 45.63), "gdańsk": (18.68, 54.40),
    "gdansk": (18.68, 54.40), "dunkerque": (2.35, 51.03), "dunkirk": (2.35, 51.03), "zeebrugge": (3.20, 51.33),
    "brugge": (3.20, 51.33), "göteborg": (11.93, 57.70), "goteborg": (11.93, 57.70), "constanţa": (28.65, 44.15),
    "constanta": (28.65, 44.15), "sines": (-8.87, 37.95), "gioia tauro": (15.90, 38.45), "livorno": (10.30, 43.55),
    "la spezia": (9.83, 44.10), "venezia": (12.25, 45.45), "venice": (12.25, 45.45), "ravenna": (12.25, 44.47),
    "taranto": (17.20, 40.48), "koper": (13.73, 45.55), "rijeka": (14.43, 45.33), "bilbao": (-3.03, 43.35),
    "tarragona": (1.23, 41.10), "cartagena": (-0.98, 37.59), "huelva": (-6.93, 37.20), "las palmas": (-15.41, 28.14),
    "lisboa": (-9.13, 38.70), "lisbon": (-9.13, 38.70), "leixões": (-8.70, 41.18), "leixoes": (-8.70, 41.18),
    "dublin": (-6.20, 53.35), "cork": (-8.30, 51.85), "aarhus": (10.22, 56.15), "københavn": (12.60, 55.69),
    "copenhagen": (12.60, 55.69), "helsinki": (24.95, 60.17), "kotka": (26.93, 60.46), "rīga": (24.09, 57.04),
    "riga": (24.09, 57.04), "klaipėda": (21.13, 55.70), "klaipeda": (21.13, 55.70), "tallinn": (24.75, 59.44),
    "szczecin": (14.58, 53.43), "gdynia": (18.53, 54.53), "wilhelmshaven": (8.15, 53.58), "rostock": (12.10, 54.15),
    "lübeck": (10.85, 53.90), "lubeck": (10.85, 53.90), "kiel": (10.15, 54.32), "gent": (3.75, 51.12), "ghent": (3.75, 51.12),
    "nantes": (-2.20, 47.28), "bordeaux": (-0.55, 44.95), "calais": (1.85, 50.97), "rouen": (1.05, 49.45),
    "thessaloniki": (22.93, 40.63), "limassol": (33.02, 34.65), "marsaxlokk": (14.54, 35.83), "valletta": (14.51, 35.90),
    "burgas": (27.50, 42.49), "varna": (27.92, 43.19), "split": (16.44, 43.51), "ploče": (17.43, 43.05), "ploce": (17.43, 43.05),
    "brindisi": (17.95, 40.65), "napoli": (14.27, 40.84), "naples": (14.27, 40.84), "salerno": (14.75, 40.67),
    "cagliari": (9.10, 39.20), "augusta": (15.22, 37.20), "milazzo": (15.25, 38.22), "ancona": (13.50, 43.62),
    "vlissingen": (3.70, 51.45), "terneuzen": (3.83, 51.33), "moerdijk": (4.60, 51.70), "delfzijl": (6.95, 53.33),
    "brest": (-4.48, 48.39), "la rochelle": (-1.22, 46.15), "sète": (3.70, 43.40), "sete": (3.70, 43.40),
    "gijón": (-5.68, 43.56), "gijon": (-5.68, 43.56), "ferrol": (-8.25, 43.47), "castellón": (0.02, 39.96),
    "málaga": (-4.42, 36.71), "palma": (2.63, 39.56), "santander": (-3.80, 43.45), "a coruña": (-8.40, 43.37),
    "trelleborg": (13.15, 55.37), "malmö": (13.00, 55.61), "helsingborg": (12.70, 56.04), "luleå": (22.20, 65.55),
    "oulu": (25.40, 65.00), "turku": (22.25, 60.43), "hamina": (27.20, 60.55), "rauma": (21.50, 61.13), "naantali": (22.02, 60.47),
    "fredericia": (9.75, 55.56), "esbjerg": (8.44, 55.47), "aalborg": (9.92, 57.05), "heraklion": (25.14, 35.34),
    "eleusina": (23.53, 38.04), "elefsina": (23.53, 38.04), "agioi theodoroi": (23.10, 37.93), "volos": (22.95, 39.36),
    "świnoujście": (14.27, 53.91), "swinoujscie": (14.27, 53.91), "police": (14.58, 53.55),
    "zeeland": (3.72, 51.44), "sköldvik": (25.55, 60.31), "skoldvik": (25.55, 60.31), "porto foxi": (9.05, 39.20),
    "porto torres": (8.40, 40.84), "monfalcone": (13.53, 45.79), "chioggia": (12.28, 45.22), "marghera": (12.25, 45.45),
    "gijon": (-5.68, 43.56), "avilés": (-5.93, 43.58), "aviles": (-5.93, 43.58), "sagunto": (-0.22, 39.65),
    "motril": (-3.52, 36.72), "almería": (-2.46, 36.83), "almeria": (-2.46, 36.83), "vigo": (-8.73, 42.24),
    "brunsbüttel": (9.13, 53.90), "brunsbuttel": (9.13, 53.90), "emden": (7.19, 53.34), "cuxhaven": (8.70, 53.87),
    "sassnitz": (13.65, 54.52), "wismar": (11.45, 53.90), "puttgarden": (11.22, 54.50), "rødby": (11.35, 54.65),
    "rodby": (11.35, 54.65), "frederikshavn": (10.55, 57.44), "hirtshals": (9.96, 57.59), "kalundborg": (11.09, 55.68),
    "porvoo": (25.55, 60.31), "pori": (21.48, 61.58), "vaasa": (21.58, 63.10), "kokkola": (23.02, 63.85),
    "ventspils": (21.53, 57.40), "liepāja": (21.00, 56.51), "liepaja": (21.00, 56.51), "muuga": (24.95, 59.50),
    "paldiski": (24.05, 59.35), "sillamäe": (27.75, 59.40), "sillamae": (27.75, 59.40), "oxelösund": (17.10, 58.67),
    "oxelosund": (17.10, 58.67), "karlshamn": (14.86, 56.16), "norrköping": (16.20, 58.60), "norrkoping": (16.20, 58.60),
    "brofjorden": (11.42, 58.35), "stenungsund": (11.83, 58.07), "nynäshamn": (17.95, 58.90), "nynashamn": (17.95, 58.90),
    "stockholm": (18.10, 59.32), "kapellskär": (19.07, 59.72), "ystad": (13.83, 55.42), "halmstad": (12.85, 56.65),
    "ravenna": (12.25, 44.47), "savona": (8.48, 44.30), "vado": (8.44, 44.27), "civitavecchia": (11.78, 42.09),
    "piombino": (10.50, 42.93), "olbia": (9.53, 40.92), "messina": (15.56, 38.19), "palermo": (13.37, 38.12),
    "catania": (15.10, 37.50), "bari": (16.87, 41.14), "monopoli": (17.30, 40.95), "marghera": (12.25, 45.45),
    "portoscuso": (8.38, 39.20), "sarroch": (9.02, 39.07), "marseille-fos": (4.95, 43.40), "fos": (4.95, 43.40),
    "lorient": (-3.35, 47.73), "cherbourg": (-1.62, 49.65), "caen": (-0.23, 49.35), "toulon": (5.93, 43.12),
    "bayonne": (-1.52, 43.53), "port-la-nouvelle": (3.05, 43.02), "calais": (1.85, 50.97), "boulogne": (1.60, 50.73),
    "vlissingen": (3.70, 51.45), "terneuzen": (3.83, 51.33), "den helder": (4.75, 52.96), "eemshaven": (6.83, 53.45),
    "harlingen": (5.42, 53.17), "scheveningen": (4.27, 52.10), "moerdijk": (4.60, 51.70), "dordrecht": (4.67, 51.81),
    "rosslare": (-6.34, 52.25), "waterford": (-6.95, 52.26), "shannon": (-8.95, 52.65), "foynes": (-9.10, 52.61),
    "drogheda": (-6.35, 53.72), "galway": (-9.05, 53.27), "larnaca": (33.62, 34.92), "vasilikos": (33.30, 34.72),
    "alexandroupolis": (25.88, 40.84), "kavala": (24.42, 40.93), "patra": (21.73, 38.25), "patras": (21.73, 38.25),
    "igoumenitsa": (20.25, 39.50), "lavrio": (24.06, 37.71), "chalkida": (23.60, 38.46), "megara": (23.35, 37.98),
    "aspropyrgos": (23.58, 38.03), "corinth": (22.93, 37.94), "korinthos": (22.93, 37.94), "rhodes": (28.23, 36.45),
    "mytilini": (26.55, 39.10), "chania": (24.02, 35.52), "souda": (24.10, 35.49), "midia": (28.68, 44.33),
    "midia (navodari)": (28.68, 44.33), "mangalia": (28.58, 43.80), "galați": (28.05, 45.43), "galati": (28.05, 45.43),
    "brăila": (27.97, 45.27), "braila": (27.97, 45.27), "tulcea": (28.80, 45.18), "sulina": (29.65, 45.15),
}


def hav_km(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(math.sin((lat2 - lat1) / 2) ** 2
                                          + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius-km", type=float, default=12.0)
    ap.add_argument("--peak", type=float, default=1.3, help="peak-day factor on the annual mean")
    ap.add_argument("--min-mt", type=float, default=1.0, help="ignore ports below this Mt/yr")
    ap.add_argument("--floor-mt", type=float, default=1.0,
                    help="capacity (Mt/yr) given to every maritime connector matched to NO listed port, "
                         "so flows displaced from a saturated port cannot leak into an unlisted one")
    args = ap.parse_args()

    es = pd.read_csv(DATA / "validation" / "eurostat_mar_go_aa_2023.csv")
    es = es[(es["direct"] == "TOTAL") & es["rep_mar"].str.contains("_", regex=False)]  # port rows only
    es = es[["rep_mar", "rep_mar_label", "value"]].dropna()
    es["mt"] = es["value"] / 1000.0
    es = es[es["mt"] >= args.min_mt].sort_values("mt", ascending=False)

    mm = gpd.read_file(DATA / "Transport" / "multimodal.gpkg")
    mm = mm[mm["multimodes"].astype(str).str.contains("maritime")].copy()
    mm["lon"] = mm.geometry.centroid.x
    mm["lat"] = mm.geometry.centroid.y

    rows, unmatched = [], []
    for _, p in es.iterrows():
        label = str(p["rep_mar_label"]).lower()
        if ":" in label or "unspecified" in label or "other ports" in label or label.startswith("european union"):
            continue  # national / coastal aggregates, not ports
        key = next((k for k in sorted(PORTS, key=len, reverse=True) if k in label), None)
        if key is None:
            unmatched.append((p["rep_mar"], p["rep_mar_label"], round(p["mt"], 1), ""))
            continue
        lon, lat = PORTS[key]
        dists = [hav_km((lon, lat), (x, y)) for x, y in zip(mm["lon"], mm["lat"])]
        near = mm[[d <= args.radius_km for d in dists]]
        if near.empty:
            unmatched.append((p["rep_mar"], p["rep_mar_label"] + " (no connector)", round(p["mt"], 1),
                              f"nearest connector {min(dists):.0f} km"))
            continue
        share = 1.0 / len(near)
        for _, c in near.iterrows():
            rows.append({"port": p["rep_mar_label"], "rep_mar": p["rep_mar"], "port_mt": round(p["mt"], 2),
                         "connector": c["name"], "multimodes": c["multimodes"],
                         "tons_per_day": round(p["mt"] * 1e6 / 365 * args.peak * share)})
    df = pd.DataFrame(rows)
    # a connector serving several listed ports gets the sum
    caps = df.groupby("connector", as_index=False).agg(tons_per_day=("tons_per_day", "sum"),
                                                        ports=("port", lambda s: "; ".join(sorted(set(s)))))
    # every other maritime connector: floor capacity (small/unlisted port)
    floor = round(args.floor_mt * 1e6 / 365 * args.peak)
    others = mm[~mm["name"].isin(caps["connector"])]
    caps = pd.concat([caps, pd.DataFrame({"connector": others["name"].values, "tons_per_day": floor,
                                          "ports": f"(unlisted port, floor {args.floor_mt} Mt/yr)"})],
                     ignore_index=True)
    out = DATA / "Transport" / "port_capacities.csv"
    df.to_csv(out, index=False)
    caps.to_csv(DATA / "Transport" / "port_capacity_overrides.csv", index=False)
    print(f"{len(es)} Eurostat port rows >= {args.min_mt} Mt; matched {df.port.nunique()} ports to "
          f"{df.connector.nunique()} connectors; {len(others)} other maritime connectors at the floor; unmatched: {len(unmatched)}")
    for u in unmatched[:30]:
        print("   unmatched:", u)
    print(df.groupby("port")["port_mt"].first().sort_values(ascending=False).head(12).to_string())
    matched_mt = df.groupby("port")["port_mt"].first().sum()
    print(f"\nmatched port throughput {matched_mt:,.0f} Mt/yr of EU27 total 3,363 Mt (gross weight, all directions)")
    print(f"written {out} and port_capacity_overrides.csv (all {len(caps)} maritime connectors)")
    print(f"\n# transport_capacity_overrides (tons/day, shared; peak factor {args.peak}) - top 12:")
    for _, r in caps.sort_values("tons_per_day", ascending=False).head(12).iterrows():
        print(f"  {r['connector']}: {int(r['tons_per_day'])}   # {r['ports']}")


if __name__ == "__main__":
    main()
