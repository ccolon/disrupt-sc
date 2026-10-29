"""Derive the round-5 waterway rate files from round 3's water_by_waterway_v2.yaml (29 Oct 2026):
v4: the Lek (Nederrijn-Lek, three weirs with locks: Driel, Amerongen, Hagestein) at the locked-tributary rate 0.015 instead of
    0.012, because the Rotterdam-Rhine stream still took it for 37 Mt in e05 (observed Lek traffic is a few Mt) while the Waal at
    Tiel read 97 against 125; round 4's f03 showed the stream moves to the Waal when the Lek route is dearer (Dordrecht-Rotterdam
    115 against 140), but f03 also priced the Amsterdam-Rhine canal and emptied Amsterdam (27 Mt) - the Lek alone is the lever;
v5: v4 with the Po system (Po, Fissero-Tartaro-Canalbianco, Litoranea Veneta, Idrovia Ferrarese) at 0.040, i.e. effectively closed
    to through traffic: class IV-V waterways carrying about 1 Mt/yr in reality, 35 Mt/yr of containers in the model, the artefact
    that makes the north-Adriatic lagoon junctions (Venice, Chioggia, Porto Nogaro, Monfalcone: 234 Mt landed against 105) the
    cheapest gateways for the Po valley.
    python studies/rhine2026/calibration/round5/derive_v4v5.py
"""
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
v2 = yaml.safe_load((HERE.parent / "round3" / "water_by_waterway_v2.yaml").read_text(encoding="utf-8"))


def rate(base: float) -> dict:
    return {"default": base, "dry_bulk": base, "liquid_bulk": round(base * 3.8, 3), "container": round(base * 2.2, 3)}


PO = ["Po", "Fissero-Tartaro-Canalbianco", "Litoranea Veneta", "Idrovia Ferrarese"]
variants = {
    "v4": {"Lek": rate(0.015)},
    "v5": {"Lek": rate(0.015), **{k: rate(0.040) for k in PO}},
}
for name, changes in variants.items():
    d = dict(v2); d.update(changes)
    head = f"# logistics.basic_cost.waterways, round 5 {name} (29 Oct 2026): round 3's v2 with " + (
        "the Lek at the locked rate 0.015" if name == "v4" else "the Lek at 0.015 and the Po system at 0.040") + "; see derive_v4v5.py.\n"
    (HERE / f"water_by_waterway_{name}.yaml").write_text(head + yaml.safe_dump(d, sort_keys=False, default_flow_style=None, width=200), encoding="utf-8")
    print(name, "written;", ", ".join(f"{k}={d[k]['default']}" for k in changes), f"({len(d)} keys)")
