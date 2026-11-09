"""Day-1 flows of the overlap interaction (Q22, 9 Nov 2026): does each single closure send traffic over the edges the
other closure cuts, and what happens to the routes when both are closed?

For each network, from transport_edges_with_flows_{0,1}.geojson of single Mekong, single Tonle Sap and the pair at tau 0
(all close on day 1): tons and ton-km on the edges each flood closes (attribute flood_v3) and on the whole network, on
day 0 and day 1. Day 0 is the same undisturbed state in the three runs (checked).

Usage: python studies/cambodia/overlap_flows.py --pairs <batch> [--singles <batch>] --seeds 1-10 [--d 12]
       [--suffix _t116]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

RUNS = {"pair": "pair_mekong_tonle_tau0", "mekong": "single_mekong", "tonle": "single_tonle"}
GROUP = {"Siem Bok (Mekong)": "mekong_edges", "St. Sen (Tonlè Sap)": "tonle_edges", "Saigon": "saigon_edges"}


def edges(path: Path) -> pd.DataFrame:
    feats = json.loads(path.read_text(encoding="utf-8"))["features"]
    rows = [{k: f["properties"].get(k) for k in ("id", "km", "flood_v3", "flow_total_tons", "flow_total")}
            for f in feats]
    df = pd.DataFrame(rows).fillna({"flow_total_tons": 0.0, "flow_total": 0.0})
    df["group"] = df.flood_v3.map(GROUP).fillna("other")
    df["tkm"] = df.flow_total_tons * df.km
    return df


def summary(df: pd.DataFrame) -> dict:
    out = {"tons_all": df.flow_total_tons.sum(), "tkm_all": df.tkm.sum(), "edges_with_flow": int((df.flow_total_tons > 0).sum())}
    for g in GROUP.values():
        x = df[df.group == g]
        out[f"tons_{g}"] = x.flow_total_tons.sum()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=Path, required=True)
    ap.add_argument("--singles", type=Path)
    ap.add_argument("--seeds", default="1-10")
    ap.add_argument("--d", type=int, default=12)
    ap.add_argument("--suffix", default="_t116")
    a = ap.parse_args()
    singles = a.singles or a.pairs
    lo, _, hi = a.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    rows = []
    for s in seeds:
        day0 = None
        for k, name in RUNS.items():
            f = (a.pairs if k == "pair" else singles) / f"{name}_d{a.d}_s{s}{a.suffix}"
            e0, e1 = edges(f / "transport_edges_with_flows_0.geojson"), edges(f / "transport_edges_with_flows_1.geojson")
            if day0 is None:
                day0 = e0
            else:
                diff = np.abs(e0.set_index("id").flow_total_tons - day0.set_index("id").flow_total_tons).max()
                assert diff < 1e-6, f"day 0 differs in {f}: {diff}"
            rows.append(dict(seed=s, run=k, day=1, **summary(e1)))
        rows.append(dict(seed=s, run="day0", day=0, **summary(day0)))
    T = pd.DataFrame(rows)
    m = T.groupby("run").mean(numeric_only=True)
    print(f"== Day-1 flows, {a.pairs.name} / {singles.name}, networks {seeds}: mean over networks "
          "(tons a day; ton-km a day)")
    cols = ["tons_all", "tkm_all", "edges_with_flow", "tons_mekong_edges", "tons_tonle_edges", "tons_saigon_edges"]
    print(m.loc[["day0", "mekong", "tonle", "pair"], cols].round(1).to_string())
    P = T.pivot(index="seed", columns="run")
    print("\n== Each closure's traffic on the other closure's edges (day 1 against day 0, tons a day)")
    for k, other in (("mekong", "tonle_edges"), ("tonle", "mekong_edges")):
        d = P[f"tons_{other}"][k] - P[f"tons_{other}"]["day0"]
        print(f"  single {k}: on the {other.replace('_', ' ')} {P[f'tons_{other}'][k].mean():.1f} against "
              f"{P[f'tons_{other}']['day0'].mean():.1f} on day 0: change {d.mean():+.1f} "
              f"({int((d > 0).sum())} of {len(d)} networks up)")
    print("\n== Ton-km and tons moved on day 1, relative to day 0 (detours lengthen routes; blocked shipments drop out)")
    for k in ("mekong", "tonle", "pair"):
        print(f"  {k:>6}: tons {(P.tons_all[k] / P.tons_all.day0 - 1).mean():+.2%}, "
              f"ton-km {(P.tkm_all[k] / P.tkm_all.day0 - 1).mean():+.2%}")
    for col in ("tons_all", "tkm_all"):
        x = (P[col].pair - P[col].day0) - (P[col].mekong - P[col].day0) - (P[col].tonle - P[col].day0)
        print(f"  pair - (Mekong + Tonle Sap) change in {col}: {x.mean():+.1f} a day "
              f"({100 * x.mean() / P[col].day0.mean():+.2f} % of day 0; {int((x < 0).sum())} of {len(x)} networks < 0)")


if __name__ == "__main__":
    main()
