"""Score a DisruptSC baseline flow export of the EU scope against freight targets.

Usage
-----
    python onboarding/scripts/flow_score.py EU --run <folder> [--periods-per-year 52]
        [--top-ports 40] [--data-root DIR] [--repo DIR] [--verbose]

<folder> is an export folder (absolute path, or a subfolder name under
<repo>/output/<scope>/) holding transport_edges_with_flows_0.geojson (edges with
weekly flows: flow_total_tons, tons_<cargo class>, flow_<category> values) and
transport_nodes.geojson. Weekly flows are annualised (x periods-per-year).
If the exported edges carry no waterway / eurostat_port columns, the edges are
tagged on the fly with the gazetteers under <data-root>/<scope>/validation/
(functions imported from tag_network_attributes.py).

Target blocks (targets live in <data-root>/<scope>/validation/ unless stated)
  (a) country_modal_split  inland tonne-km shares road/rail/IWW by edge country
      (first code of country_code) vs eurostat_tran_hv_frmod_2022_2023.csv (2023).
  (b) ports   annual tonnes through the sea-port connectors of each tagged
      Eurostat port vs eurostat_mar_go_aa_2023.csv IN+OUT (Mt), top-N ports.
      Eurostat includes transhipment and crude; the model counts a connector
      passage per port visit (no transhipment), and crude moves by pipeline.
  (c) rhine   tonnage on each rhine_* segment (km-weighted mean over its edges)
      vs studies/rhine2026/scenarios/rhine_capacities.csv (mt_per_year).
  (d) basins  tonne-km and tonnes by waterway tag and country vs
      waterway_targets_2023.csv (rows with an empty value are skipped; the
      model counterpart of mt_per_year is the km-weighted mean tonnage, or the
      busiest edge when metric == max_cross_section; bn_tkm_per_year compares
      tonne-km; waterway ALL = all waterway edges of the country).
  (e) nst_modal_split  DE and NL modal split of tonne-km per flow category
      (agriculture, mining, oil_and_gas, manufacturing) vs the tkm-weighted
      aggregate of the NST-2007 groups of mode_split_targets_<CC>_2023.csv
      (GT01 -> agriculture; GT02, GT03 -> mining; GT07 -> oil_and_gas; rest ->
      manufacturing). Model tonnes per category come from tons_<category>
      columns when exported, else from the cargo classes: liquid_bulk ->
      oil_and_gas, container -> manufacturing, dry_bulk split between
      agriculture and mining by their value shares on the edge.
  (f) short_sea  Eurostat deep-sea share (eurostat_mar_sg_am_cw_2023.csv) vs
      the model's EU-level share = tonnes on the maritime edges incident to the
      deep-sea gateway nodes (USA/AME/AFR/CHN/ASI/MEA/ROW points of
      Spatial/countries.geojson) / tonnes through all sea-port connectors; a
      per-country split is not derivable from edge flows (no origin on edges),
      so only the external-trade share of each country's port throughput
      (value) is printed as an upper bound.
  (g) summary.csv  per block the item count and mean |log10(model/target)|,
      plus the weighted score (ports 0.3, country modal split 0.25, NST 0.2,
      Rhine 0.15, basins 0.1; weights renormalised over scored blocks).

Outputs: one summary table on stdout (all tables with --verbose) and CSVs in
<folder>/flow_score/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402
import tag_network_attributes as tna  # noqa: E402

CATS = ["agriculture", "mining", "oil_and_gas", "manufacturing"]
NST_TO_CAT = {"GT01": "agriculture", "GT02": "mining", "GT03": "mining", "GT07": "oil_and_gas"}
MODES = {"roads": "ROAD", "railways": "RAIL", "waterways": "IWW"}
EU27 = "BE BG CY CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK AT".split()
WEIGHTS = {"ports": 0.30, "country_modal_split": 0.25, "nst_modal_split": 0.20, "rhine": 0.15, "basins": 0.10}
DEEP_SEA = {"USA", "AME", "AFR", "CHN", "ASI", "MEA", "ROW"}
SHARE_FLOOR_PCT = 0.1


def log_err(model, target, floor):
    """|log10(model/target)| with the model floored (zero flows stay finite)."""
    m = np.maximum(np.asarray(model, dtype=float), floor)
    return np.abs(np.log10(m / np.asarray(target, dtype=float)))


# ----------------------------------------------------------------------------
def load_export(folder: Path, ppy: float, gaz_dir: Path) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, list[str]]:
    notes = []
    e = gpd.read_file(folder / "transport_edges_with_flows_0.geojson")
    n = gpd.read_file(folder / "transport_nodes.geojson")
    if "foreign" in e.columns:
        e = e[e["foreign"].fillna(0) != 1].copy()
    e["tons_yr"] = e["flow_total_tons"].fillna(0) * ppy
    e["tkm_yr"] = e["tons_yr"] * e["km"]
    e["cc"] = e["country_code"].map(tna._first_cc)
    if all(f"tons_{c}" in e.columns for c in CATS):
        notes.append("category tonnes taken from exported tons_<category> columns")
    else:
        va, vm = e["flow_agriculture"].fillna(0), e["flow_mining"].fillna(0)
        share = (va / (va + vm).replace(0, np.nan)).fillna(0.5)
        dry = e["tons_dry_bulk"].fillna(0)
        e["tons_agriculture"], e["tons_mining"] = dry * share, dry * (1 - share)
        e["tons_oil_and_gas"], e["tons_manufacturing"] = e["tons_liquid_bulk"].fillna(0), e["tons_container"].fillna(0)
        notes.append("category tonnes derived from cargo classes (dry_bulk split agriculture/mining by value shares)")
    for c in CATS:
        e[f"tkm_{c}"] = e[f"tons_{c}"].fillna(0) * ppy * e["km"]
    need = "waterway" not in e.columns or e.loc[e["type"] == "waterways", "waterway"].isna().all() \
        or "eurostat_port" not in e.columns or e["eurostat_port"].notna().sum() == 0
    if need:
        e = tna.tag_edges_frame(e, gaz_dir)
        notes.append("export carried no waterway/eurostat_port tags: tagged on the fly from the gazetteers")
    return e, n, notes


# ----------------------------------------------------------------------------
def block_modal_split(e, vdir):
    es = pd.read_csv(vdir / "eurostat_tran_hv_frmod_2022_2023.csv")
    es = es[(es["time"] == 2023) & es["tra_mode"].isin(MODES.values())].pivot(index="geo", columns="tra_mode", values="value")
    inland = e[e["type"].isin(MODES)].copy()
    inland.loc[inland["cc"].isin(EU27), "eu"] = "EU27_2020"
    rows = []
    for key, sub in list(inland.groupby("cc")) + list(inland.groupby("eu")):
        tot = sub["tkm_yr"].sum()
        if tot <= 0:
            continue
        r = {"geo": key, "model_bn_tkm": tot / 1e9}
        for mode, es_mode in MODES.items():
            r[f"model_{es_mode}"] = 100 * sub.loc[sub["type"] == mode, "tkm_yr"].sum() / tot
            r[f"target_{es_mode}"] = es[es_mode].get(key, np.nan) if key in es.index else np.nan
        rows.append(r)
    df = pd.DataFrame(rows).set_index("geo")
    for m in MODES.values():
        ok = df[f"target_{m}"] >= 0.5
        df[f"err_{m}"] = np.where(ok, log_err(df[f"model_{m}"], df[f"target_{m}"].where(ok, 1), SHARE_FLOOR_PCT), np.nan)
    df["scored"] = df.index != "EU27_2020"
    return df.sort_values("model_bn_tkm", ascending=False).round(2)


def block_ports(e, vdir, top_n):
    m = pd.read_csv(vdir / "eurostat_mar_go_aa_2023.csv")
    m = m[m["direct"].isin(["IN", "OUT"]) & (m["rep_mar"].str.len() > 4)]
    tgt = m.groupby("rep_mar").agg(eurostat_mt=("value", lambda v: v.sum() / 1000), label=("rep_mar_label", "first"))
    sea = e[(e["type"] == "multimodal") & tna.sea_connector_mask(e) & e["eurostat_port"].notna()]
    mod = sea.groupby("eurostat_port").agg(model_mt=("tons_yr", lambda v: v.sum() / 1e6),
                                           n_terminals=("terminal_id", "nunique"), port_name=("port_name", "first"))
    gaz = pd.read_csv(vdir / "ports_gazetteer.csv").drop_duplicates("eurostat_port").set_index("eurostat_port")
    df = tgt.loc[tgt.index.isin(gaz.index)].nlargest(top_n, "eurostat_mt").join(mod, how="left")
    df["cc"] = df.index.str[:2]
    df["ratio"] = df["model_mt"] / df["eurostat_mt"]
    df["log10_err"] = log_err(df["model_mt"].fillna(0), df["eurostat_mt"], 0.01)
    df["scored"] = df["n_terminals"].notna()
    df.loc[~df["scored"], "log10_err"] = np.nan
    cols = ["label", "cc", "eurostat_mt", "model_mt", "ratio", "log10_err", "n_terminals", "scored"]
    return df[cols].round(2), sea["tons_yr"].sum() / 1e6


def block_rhine(e, repo):
    caps = pd.read_csv(repo / "studies" / "rhine2026" / "scenarios" / "rhine_capacities.csv").set_index("name")
    target = caps["mt_per_year"] if "mt_per_year" in caps.columns else caps["tons_per_day"] * 365 / 1e6
    rhe = e[e["name"].astype(str).str.startswith("rhine")]
    grp = rhe.groupby("name")
    df = pd.DataFrame({"edges": grp.size(), "model_mt": grp["tkm_yr"].sum() / grp["km"].sum() / 1e6}).reindex(caps.index)
    df["normal_mt"] = target
    df["ratio"] = df["model_mt"] / df["normal_mt"]
    df["log10_err"] = log_err(df["model_mt"].fillna(0), df["normal_mt"], 0.1)
    df["scored"] = df["edges"].notna() & df["normal_mt"].notna()
    return df.round(2)


def block_basins(e, vdir):
    ww = e[e["type"] == "waterways"]
    g = ww.groupby(["waterway", "cc"]).agg(edges=("id", "size"), km=("km", "sum"), bn_tkm=("tkm_yr", lambda v: v.sum() / 1e9),
                                           max_mt=("tons_yr", lambda v: v.max() / 1e6))
    g["mean_mt"] = g["bn_tkm"] * 1e3 / g["km"]
    allc = ww.groupby("cc").agg(edges=("id", "size"), km=("km", "sum"), bn_tkm=("tkm_yr", lambda v: v.sum() / 1e9),
                                max_mt=("tons_yr", lambda v: v.max() / 1e6))
    allc["mean_mt"] = allc["bn_tkm"] * 1e3 / allc["km"]
    allc.index = pd.MultiIndex.from_tuples([("ALL", c) for c in allc.index], names=["waterway", "cc"])
    df = pd.concat([g, allc])
    t = pd.read_csv(vdir / "waterway_targets_2023.csv").rename(columns={"country": "cc"}).set_index(["waterway", "cc"])
    df = df.join(t[["mt_per_year", "bn_tkm_per_year", "metric", "source"]], how="left")
    model_mt = np.where(df["metric"] == "max_cross_section", df["max_mt"], df["mean_mt"])
    err_t = log_err(df["bn_tkm"].fillna(0), df["bn_tkm_per_year"].fillna(1), 0.01)
    err_m = log_err(np.nan_to_num(model_mt), df["mt_per_year"].fillna(1), 0.01)
    df["log10_err"] = np.where(df["bn_tkm_per_year"].notna(), err_t, np.where(df["mt_per_year"].notna(), err_m, np.nan))
    df["scored"] = df["log10_err"].notna()
    return df.sort_values("bn_tkm", ascending=False).round(2)


def block_nst(e, vdir):
    rows = []
    for cc in ("DE", "NL"):
        p = vdir / f"mode_split_targets_{cc}_2023.csv"
        if not p.exists():
            continue
        t = pd.read_csv(p)
        t["category"] = t["nst07"].map(lambda g: "TOTAL" if g == "TOTAL" else NST_TO_CAT.get(g, "manufacturing"))
        tk = t.groupby("category")[["road_tkm", "rail_tkm", "iww_tkm"]].sum()
        sub = e[(e["cc"] == cc) & e["type"].isin(MODES)]
        for cat in CATS + ["TOTAL"]:
            col = "tkm_yr" if cat == "TOTAL" else f"tkm_{cat}"
            mt = {mode: sub.loc[sub["type"] == mode, col].sum() for mode in MODES}
            mtot, ttot = sum(mt.values()), tk.loc[cat].sum() if cat in tk.index else 0
            for mode, tcol in zip(MODES, ["road_tkm", "rail_tkm", "iww_tkm"]):
                tp = 100 * tk.loc[cat, tcol] / ttot if ttot else np.nan
                rows.append({"cc": cc, "category": cat, "mode": mode, "model_pct": 100 * mt[mode] / mtot if mtot else np.nan,
                             "target_pct": tp, "model_bn_tkm": mt[mode] / 1e9, "target_bn_tkm": tk.loc[cat, tcol] / 1e3 if ttot else np.nan})
    df = pd.DataFrame(rows)
    ok = (df["target_pct"] >= 0.5) & df["model_pct"].notna()
    df["log10_err"] = np.where(ok, log_err(df["model_pct"].fillna(0), df["target_pct"].where(ok, 1), SHARE_FLOOR_PCT), np.nan)
    df["scored"] = ok
    return df.round(2)


def block_short_sea(e, nodes, vdir, scope_dir, port_total_mt):
    ss = pd.read_csv(vdir / "eurostat_mar_sg_am_cw_2023.csv")
    dss = ss[(ss["seaship"] == "DSS") & (ss["unit"] == "PC_TOT")].drop_duplicates("rep_mar").set_index("rep_mar")["value"]
    gw = gpd.read_file(scope_dir / "Spatial" / "countries.geojson")
    nid = "id" if "id" in nodes.columns else None
    nxy = np.c_[nodes.geometry.x, nodes.geometry.y]
    gw["node"] = [int((nodes[nid] if nid else nodes.index).iloc[int(np.argmin((nxy[:, 0] - p.x) ** 2 + (nxy[:, 1] - p.y) ** 2))])
                  for p in gw.geometry]
    mar = e[e["type"] == "maritime"]
    deg = pd.concat([mar["end1"], mar["end2"]]).value_counts()
    gnodes = set(gw["node"])
    rows = []
    for node, g in gw.groupby("node"):
        inc = mar[(mar["end1"] == node) | (mar["end2"] == node)]
        other = np.where(inc["end1"] == node, inc["end2"], inc["end1"])
        to_leaf_gw = inc["tons_yr"][[o in gnodes and deg.get(o, 0) == 1 for o in other]].sum()
        own = inc["tons_yr"].sum() - 2 * to_leaf_gw
        rows.append({"gateways": "+".join(g["region"]), "node": node, "degree": int(deg.get(node, 0)),
                     "deep_sea": all(r in DEEP_SEA for r in g["region"]), "incident_mt": inc["tons_yr"].sum() / 1e6,
                     "own_mt": own / 1e6, "leaf": deg.get(node, 0) == 1})
    gdf = pd.DataFrame(rows)
    deep = gdf.loc[gdf["deep_sea"], "own_mt"].sum()
    model_dss = 100 * deep / port_total_mt if port_total_mt else np.nan
    sea = e[(e["type"] == "multimodal") & tna.sea_connector_mask(e)]
    agg = sea.groupby("cc")[["flow_import", "flow_export", "flow_total"]].sum().fillna(0)
    ext = 100 * (agg["flow_import"] + agg["flow_export"]) / agg["flow_total"].replace(0, np.nan)
    cdf = pd.DataFrame({"eurostat_dss_pct": dss, "model_external_share_pct_value": ext}).dropna(how="all")
    cdf.loc["EU27_2020", "model_dss_pct_from_gateways"] = model_dss
    cdf["scored"] = False
    return gdf.round(2), cdf.round(1), model_dss


# ----------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="score a baseline flow export against freight targets")
    ap.add_argument("scope")
    ap.add_argument("--run", required=True, help="export folder (path) or subfolder name under output/<scope>/")
    ap.add_argument("--periods-per-year", type=float, default=52.0)
    ap.add_argument("--top-ports", type=int, default=40)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--repo", default=None)
    ap.add_argument("--verbose", action="store_true", help="print every block table, not just the summary")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else locate.find_repo_root()
    data_root = Path(args.data_root) if args.data_root else locate.data_root()
    run = Path(args.run)
    if not run.is_absolute() and not run.exists():
        run = repo / "output" / args.scope / args.run
    vdir, scope_dir = data_root / args.scope / "validation", data_root / args.scope
    out = run / "flow_score"
    out.mkdir(exist_ok=True)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 500)

    e, nodes, notes = load_export(run, args.periods_per_year, vdir)
    print(f"run {run}: {len(e)} edges; " + "; ".join(notes))
    blocks = {}
    blocks["country_modal_split"] = block_modal_split(e, vdir)
    blocks["ports"], port_total = block_ports(e, vdir, args.top_ports)
    blocks["rhine"] = block_rhine(e, repo)
    blocks["basins"] = block_basins(e, vdir)
    blocks["nst_modal_split"] = block_nst(e, vdir)
    try:
        gw, short_sea, model_dss = block_short_sea(e, nodes, vdir, scope_dir, port_total)
        blocks["short_sea"] = short_sea
        gw.to_csv(out / "gateways.csv", index=False)
    except Exception as exc:  # the block is informative only; never block the score
        print(f"short-sea block skipped: {exc}")
        model_dss = np.nan
    for name, df in blocks.items():
        df.to_csv(out / f"{name}.csv")
        if args.verbose:
            print(f"\n== {name} ==")
            print(df.to_string())

    # summary
    rows = []
    err_cols = {"country_modal_split": [f"err_{m}" for m in MODES.values()], "ports": ["log10_err"],
                "rhine": ["log10_err"], "basins": ["log10_err"], "nst_modal_split": ["log10_err"]}
    for name, cols in err_cols.items():
        df = blocks[name]
        vals = pd.concat([df.loc[df["scored"], c] for c in cols]).dropna()
        rows.append({"block": name, "n_items": len(vals), "mean_abs_log10": vals.mean() if len(vals) else np.nan,
                     "median_abs_log10": vals.median() if len(vals) else np.nan, "weight": WEIGHTS[name]})
    summ = pd.DataFrame(rows).set_index("block")
    ok = summ["n_items"] > 0
    score = (summ.loc[ok, "mean_abs_log10"] * summ.loc[ok, "weight"]).sum() / summ.loc[ok, "weight"].sum()
    summ.loc["OVERALL", ["n_items", "mean_abs_log10", "weight"]] = [summ["n_items"].sum(), score, summ.loc[ok, "weight"].sum()]
    summ.loc["short_sea (info)", ["n_items", "mean_abs_log10"]] = [0, np.nan]
    summ["note"] = ["(cc, mode) shares with target >= 0.5 %, model floored at 0.1 %",
                    f"top-{args.top_ports} Eurostat ports with >= 1 connector; model floored at 0.01 Mt",
                    "rhine_* segments vs normal-year Mt (km-weighted mean per segment), floor 0.1 Mt",
                    "waterway x country rows of waterway_targets_2023.csv with a value (tkm if given, else Mt)",
                    "(cc, category, mode) shares DE/NL with target >= 0.5 %, model floored at 0.1 %",
                    "weighted mean of mean_abs_log10 over scored blocks (weights renormalised)",
                    f"EU-level model deep-sea share from gateways {model_dss:.1f} % vs Eurostat EU27 "
                    f"{blocks.get('short_sea', pd.DataFrame()).get('eurostat_dss_pct', pd.Series(dtype=float)).get('EU27_2020', np.nan)} %"]
    summ.to_csv(out / "summary.csv")
    print("\n== SUMMARY (mean |log10(model/target)|; 0 = perfect, 0.3 = factor 2, 1 = factor 10) ==")
    print(summ.round(3).to_string())
    print(f"\nCSVs written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
