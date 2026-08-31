"""Mode-choice calibration targets from Eurostat NST-level freight data (rec #2).

Fetches, for an EU country, the three modal freight datasets broken down by
NST-2007 commodity group:
    road_go_ta_tg   (road, tonnes + tkm, Romanian-registered hauliers)
    rail_go_grpgood (rail, tonnes + tkm, on-territory)
    iww_go_atygo    (inland waterways, tonnes + tkm, on-territory)
and computes the calibration targets for logistics.basic_cost / dwell_times:
  - per-NST mode shares of tonne-km,
  - shares aggregated to DisruptSC cargo types (dry_bulk / container, with
    GT07 coke+refined petroleum reported separately - see note below),
  - mean haul per mode (tkm/tonnes), a second moment the model should match.

With --compare <transport_edges_with_flows_*.geojson>, also prints the model's
per-cargo-type split from a run's edge flows (tons_dry_bulk / tons_container
columns) next to the targets.

Caveats (print in any report):
  - road_go_ta_tg covers the country's REGISTERED hauliers wherever they drive,
    so the road totals overstate on-territory road work; the per-NST SHARES are
    still the robust calibration target, and rail/IWW are on-territory.
  - GT07 (coke & refined petroleum) rides rail product-trains in reality but
    DisruptSC types C19 as manufacturing -> container; either accept the bias
    or give C19 a bulk cargo type.
  - Non-EU scopes: no Eurostat - use ITF/OECD or national statistics; keep the
    same target structure (mode shares by commodity + mean hauls).

Usage:
    python eurostat_mode_targets.py --geo RO [--year 2023] [--out targets.csv]
                                    [--compare <edges_with_flows.geojson>]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request

import pandas as pd

# NST-2007 main group -> DisruptSC cargo type (edit for scope specifics).
NST_TO_CARGO = {
    "GT01": "dry_bulk",     # agriculture (cereals dominate IWW)
    "GT02": "dry_bulk",     # coal & lignite
    "GT03": "dry_bulk",     # ores & quarrying
    "GT07": "liquid_bulk",  # coke & refined petroleum (rail/pipe in reality)
    # everything else -> container
}

NST_LABELS = {
    "GT01": "agriculture/forestry/fishing products", "GT02": "coal & lignite",
    "GT03": "ores & quarrying", "GT04": "food/beverages/tobacco",
    "GT05": "textiles & leather", "GT06": "wood & paper",
    "GT07": "coke & refined petroleum", "GT08": "chemicals",
    "GT09": "other non-metallic minerals", "GT10": "basic metals",
    "GT11": "machinery & equipment", "GT12": "transport equipment",
    "GT13": "furniture & other manufacturing", "GT14": "secondary raw materials & waste",
    "GT15": "mail & parcels", "GT16": "equipment for goods transport",
    "GT17": "household/office removals", "GT18": "grouped goods",
    "GT19": "unidentifiable goods", "GT20": "other goods nes",
}


def fetch(ds: str, **params) -> dict:
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = (f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
           f"{ds}?format=JSON&lang=EN&{q}")
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read())


def jsonstat_to_df(j: dict) -> pd.DataFrame:
    ids, sizes = j["id"], j["size"]
    cats = []
    for d in ids:
        cat = j["dimension"][d]["category"]
        cats.append(sorted(cat["index"], key=lambda k: cat["index"][k]))
    rows = []
    for lin, val in j["value"].items():
        lin = int(lin)
        coords = []
        for size in reversed(sizes):
            coords.append(lin % size)
            lin //= size
        coords = coords[::-1]
        rows.append({d: cats[i][c] for i, (d, c) in enumerate(zip(ids, coords))}
                    | {"value": val})
    return pd.DataFrame(rows)


def pivot(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    p = df.pivot_table(index="nst07", columns="unit", values="value", aggfunc="sum")
    p.columns = [f"{mode}_{'tkm' if c == 'MIO_TKM' else 'kt'}" for c in p.columns]
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo", required=True, help="Eurostat geo code, e.g. RO")
    ap.add_argument("--year", default="2023")
    ap.add_argument("--out", default=None)
    ap.add_argument("--compare", default=None,
                    help="a run's transport_edges_with_flows_*.geojson")
    args = ap.parse_args()

    road = jsonstat_to_df(fetch("road_go_ta_tg", geo=args.geo, time=args.year))
    rail = jsonstat_to_df(fetch("rail_go_grpgood", geo=args.geo, time=args.year))
    iww = jsonstat_to_df(fetch("iww_go_atygo", geo=args.geo, time=args.year))
    road = road[road.tra_type == "TOTAL"]
    iww = iww[(iww.tra_cov == "TOTAL") & (iww.typpack == "TOTAL")]

    t = (pivot(road, "road").join(pivot(rail, "rail"), how="outer")
         .join(pivot(iww, "iww"), how="outer"))
    main_groups = [f"GT{i:02d}" for i in range(1, 21)] + ["TOTAL"]
    t = t.loc[[i for i in main_groups if i in t.index]].fillna(0)

    tk = t[[c for c in t.columns if c.endswith("_tkm")]]
    shares = (100 * tk.div(tk.sum(axis=1), axis=0)).round(1)
    shares.columns = ["road_pct_tkm", "rail_pct_tkm", "iww_pct_tkm"]
    shares["total_mio_tkm"] = tk.sum(axis=1).round(0)
    shares["label"] = [NST_LABELS.get(i, "TOTAL") for i in shares.index]
    print(f"== per-NST mode shares of tonne-km, {args.geo} {args.year} ==")
    print(shares.to_string())

    body = t.drop(index="TOTAL", errors="ignore").copy()
    body["cargo"] = [NST_TO_CARGO.get(i, "container") for i in body.index]
    agg = body.groupby("cargo")[list(tk.columns)].sum()
    csh = (100 * agg.div(agg.sum(axis=1), axis=0)).round(1)
    print(f"\n== targets by DisruptSC cargo type (% of tkm) ==")
    print(csh.to_string())
    print("total mio tkm:", agg.sum(axis=1).round(0).to_dict())

    tot = t.loc["TOTAL"]
    print("\n== mean haul per mode (km) ==")
    for m in ("road", "rail", "iww"):
        if tot[f"{m}_kt"] > 0:
            print(f"  {m}: {1000 * tot[f'{m}_tkm'] / tot[f'{m}_kt']:.0f}")
    print("\nCAVEAT: road_go_ta_tg = registered hauliers anywhere (totals inflated);"
          " use the SHARES as targets. GT07 (refined petroleum) is rail-heavy in"
          " reality but container-typed in DisruptSC unless overridden.")

    out = args.out or f"mode_split_targets_{args.geo}_{args.year}.csv"
    shares.join(t).to_csv(out)
    print(f"\nsaved {out}")

    if args.compare:
        import geopandas as gpd
        g = gpd.read_file(args.compare)
        print(f"\n== model split by cargo type (from {args.compare}) ==")
        for cargo in ("dry_bulk", "container", "liquid_bulk"):
            col = f"tons_{cargo}"
            if col not in g.columns:
                continue
            d = g.assign(tkm=g[col] * g.km).groupby("type")["tkm"].sum()
            d = d[[m for m in ("roads", "railways", "waterways") if m in d.index]]
            if d.sum() > 0:
                print(f"  {cargo}: " + ", ".join(
                    f"{m} {100 * v / d.sum():.1f}%" for m, v in d.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
