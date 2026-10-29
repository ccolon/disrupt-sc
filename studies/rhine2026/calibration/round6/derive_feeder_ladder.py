"""Derive the round-6 port-fee files (29 Oct 2026): the FEEDER LADDER, a port surcharge that falls with the port's size.

Rounds 4-5 hand-picked ports for a +0.75/+1.5 USD/t fee and found the elasticity low: at +1.5 the north-Adriatic lagoon ports
(Venice, Chioggia, Porto Nogaro, Monfalcone) still land 208 Mt against 28 observed, Szczecin 97 against 12 (plus Swinoujscie),
and the secondary ports as a group 816 Mt against 598. The overshoot is containers (Venice 96 of 110 Mt, Szczecin 71 of 97,
Porto Nogaro 52 of 55, Monfalcone 40 of 41, Burgas 36 of 48): the model's maritime network calls at every coast point with a
deep-sea ship, so the port nearest the destination wins; in reality deep-sea container lines call at a few hubs and a container
landed at a secondary port carries a feeder leg (100-200 USD/TEU, 10-20 USD/t) that bulk in a small ship does not. The ladder
is that cost, as a smooth rule rather than a list of ports:

    fee_container(T) = a * log10(T_ref / T)  clipped to [0, cap],   fee_other = fee_container / 3

with T the port's Eurostat 2023 throughput (IN+OUT, Mt), T_ref = 100 Mt (the deep-sea gateway scale: Rotterdam, Antwerp-Bruges
and Hamburg pay nothing), cap = 12 USD/t, and a in {3, 5, 7} the three rungs (Szczecin 11.8 Mt: 2.8 / 4.6 / 6.5 on containers;
Venice 22.5: 1.9 / 3.2 / 4.5; Porto Nogaro 0.9: 6.1 / 10.2 / 12). Ports in the gazetteer without a 2023 value take a nominal
throughput (OVERRIDES, else 0.5 Mt). Amsterdam keeps the +0.75 scalar of round 4 (it pins the Rotterdam/Amsterdam split, a
different role) wherever the ladder would give it less. The a5_wm35 variant adds the sea-barge transfer at 3.5 USD/t (the
waterways-maritime fee, 2 in the paper): with 2 + 4 for a container's sea-barge-road chain against 7 for sea-road, every port
with a waterway connector lands its goods on a barge first (Rotterdam 131 of 131 Mt, Hamburg 78 of 82, Bremerhaven 27.5 of 27.6),
which is harmless where the barge hop is intra-port but puts 21 Mt on the Weser between Bremerhaven and Oldenburg (3 observed)
once the Bremen junction is dear; at 3.5 the chain is never cheaper than the direct transfer and barges win only on line-haul.

    python studies/rhine2026/calibration/round6/derive_feeder_ladder.py [--data-root DIR]
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
T_REF, CAP, OTHER_SHARE, MIN_FEE = 100.0, 12.0, 1 / 3, 0.05
OVERRIDES = {"Malmo": 8.0, "Nynashamn": 3.0, "Lappeenranta": 1.0, "Joensuu": 0.3, "Portimao": 0.3}
STANDARD = {
    "roads-railways": {"default": 3, "container": 2, "dry_bulk": 3, "liquid_bulk": 1},
    "roads-waterways": {"default": 6, "container": 4, "dry_bulk": 5, "liquid_bulk": 3.5},
    "roads-maritime": 7,
    "railways-waterways": {"default": 6, "container": 4, "dry_bulk": 5, "liquid_bulk": 3.5},
    "railways-maritime": 7,
    "waterways-maritime": 2,
}
SHOW = ["Rotterdam", "Antwerp", "Hamburg", "Amsterdam", "Gdansk", "Marseille", "Valencia", "Goteborg", "Trieste", "Venezia", "Koper",
        "Bremerhaven", "Szczecin", "Bremen", "Burgas", "Malaga", "Vasteras", "Catania", "Dublin", "Waterford", "Monfalcone", "Porto Nogaro",
        "Chioggia", "Oslo", "Malmo", "Emden"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=str(HERE.parents[4] / "disrupt-sc-data"))
    args = ap.parse_args()
    vdir = Path(args.data_root) / "EU" / "validation"
    m = pd.read_csv(vdir / "eurostat_mar_go_aa_2023.csv")
    m = m[m["direct"].isin(["IN", "OUT"]) & (m["rep_mar"].str.len() > 4)]
    mt = m.groupby("rep_mar")["value"].sum() / 1000
    gaz = pd.read_csv(vdir / "ports_gazetteer.csv")
    gaz["T"] = gaz["eurostat_port"].map(mt)
    gaz.loc[gaz["T"].isna() | (gaz["T"] <= 0), "T"] = gaz["port_name"].map(OVERRIDES).fillna(0.5)
    gaz = gaz.drop_duplicates("port_name").set_index("port_name")
    table = gaz[["eurostat_port", "T"]].copy()
    for a in (3, 5, 7):
        fee_c = np.clip(a * np.log10(T_REF / gaz["T"]), 0, CAP)
        table[f"a{a}"] = fee_c.round(2)
        by_port = {}
        for port, fc in fee_c.items():
            if fc < MIN_FEE:
                continue
            by_port[port] = {"container": round(float(fc), 2), "default": round(float(fc) * OTHER_SHARE, 2)}
        if by_port.get("Amsterdam", {"container": 0})["container"] <= 0.75:
            by_port["Amsterdam"] = 0.75
        for wm, suffix in ((2, ""), (3.5, "_wm35")):
            if wm != 2 and a != 5:
                continue
            fees = dict(STANDARD); fees["waterways-maritime"] = wm; fees["by_port"] = dict(sorted(by_port.items()))
            head = (f"# logistics.loading_fees, round 6 (29 Oct 2026): the feeder ladder a={a} (fee_container = {a} x log10({T_REF:.0f} Mt / T), "
                    f"clipped to [0, {CAP:.0f}]; other cargo a third of it; Amsterdam keeps +0.75 where the ladder gives less)"
                    + (f"; waterways-maritime at {wm} (sea-barge transfer no cheaper than sea-road)" if wm != 2 else "")
                    + "; derived by derive_feeder_ladder.py from Eurostat 2023 port throughput and the gazetteer.\n")
            out = HERE / f"port_fees_feeder_a{a}{suffix}.yaml"
            out.write_text(head + yaml.safe_dump(fees, sort_keys=False, default_flow_style=None, width=200), encoding="utf-8")
            print(f"{out.name}: {len(by_port)} ports with a fee")
    pd.set_option("display.width", 200)
    print(table.loc[[p for p in SHOW if p in table.index]].round(2).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
