"""Derive the round-4 waterway rate files from round 3's water_by_waterway_v2.yaml (27 Oct 2026):
v3a: the Ruhr canals (Wesel-Datteln, Rhein-Herne, Dortmund-Ems) at the Rhine rate 0.010, because the corridor from the Rhine
     ports to the Ruhr stays at 10 Mt against 27 observed (Wesel-Datteln 1.2 against 16.2) even at 0.013;
v3b: the Dutch waterways off the Rhine chain (IJssel, IJsselmeer, Amsterdam-Rhine canal, Noordzeekanaal, Scheldt-Rhine link,
     Ghent-Terneuzen, Lek) at 0.012, because the Dutch waterway share stays at 53-55 % of inland tkm against 41 observed
     (Dutch domestic manufactured goods 47 % by barge against 26, mining 87 against 70);
v3c: both.
    python studies/rhine2026/calibration/round4/derive_v3.py
"""
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
v2 = yaml.safe_load((HERE.parent / "round3" / "water_by_waterway_v2.yaml").read_text(encoding="utf-8"))


def rate(base: float) -> dict:
    return {"default": base, "dry_bulk": base, "liquid_bulk": round(base * 3.8, 3), "container": round(base * 2.2, 3)}


RUHR = ["Wesel-Datteln-Kanal", "Rhein-Herne-Kanal", "Dortmund-Ems-Kanal"]
NL = ["IJssel", "IJsselmeer", "Amsterdam-Rhine canal", "Noordzeekanaal", "Scheldt-Rhine link", "Ghent-Terneuzen canal", "Lek"]
variants = {
    "v3a": {k: rate(0.010) for k in RUHR},
    "v3b": {k: rate(0.012) for k in NL},
    "v3c": {**{k: rate(0.010) for k in RUHR}, **{k: rate(0.012) for k in NL}},
}
for name, changes in variants.items():
    d = dict(v2); d.update(changes)
    head = f"# logistics.basic_cost.waterways, round 4 {name} (27 Oct 2026): round 3's v2 with " + (
        "the Ruhr canals at 0.010" if name == "v3a" else "the Dutch waterways off the Rhine chain at 0.012" if name == "v3b" else "both changes") + "; see derive_v3.py.\n"
    (HERE / f"water_by_waterway_{name}.yaml").write_text(head + yaml.safe_dump(d, sort_keys=False, default_flow_style=None, width=200), encoding="utf-8")
    print(name, "written;", ", ".join(f"{k}={d[k]['default']}" for k in list(changes)[:3]), "...")
