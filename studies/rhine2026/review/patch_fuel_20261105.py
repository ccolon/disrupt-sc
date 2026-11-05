r"""SI S5: what the fuel-fed service sectors miss (5 Nov 2026). The text said that for hauliers, logistics operators,
power plants and shipping companies the largest missing input is refined fuel. On the per-class batch (2026 link-level
run, German buyers) refined fuel is the largest missing input of the shipping companies only (\FuelShareShipping %),
the second of the hauliers (\FuelShareHauliers %, after logistics services at \LogisticsShareHauliers %); logistics
operators and power plants miss mostly their own sectors' deliveries (79 and 59 %); over the four sectors fuel is
\FuelShareServices % of what they miss. Even the batch of 7 October had it first for two of the four. The new macros
are computed by make_numbers.py (block '_missing_inputs'); regenerate numbers.tex before applying.

    python studies/rhine2026/review/patch_fuel_20261105.py [--repo <overleaf>] [--ledger <folder>] [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
LEDGER = HERE.parent / "paper_gate_ledger"
OLD = (r"What the service sectors miss is fuel: for hauliers, logistics operators, power plants and shipping companies the "
       r"largest missing input is refined fuel, of which \FuelWithheldShare\,\% is withheld at the river and the rest "
       r"rationed by refineries short of their own inputs; the service sectors then ration each other.")
NEW = (r"What the service sectors miss is fuel and each other's services: refined fuel is the largest missing input of the "
       r"shipping companies (\FuelShareShipping\,\% of what they miss) and the second of the hauliers "
       r"(\FuelShareHauliers\,\%, after logistics services at \LogisticsShareHauliers\,\%), while logistics operators and "
       r"power plants miss mostly the deliveries of their own sectors; over the four sectors, fuel is \FuelShareServices\,\% "
       r"of what they miss. Of that fuel, \FuelWithheldShare\,\% is withheld at the river and the rest rationed by "
       r"refineries short of their own inputs.")
ALLOWED = ("  - file: sections/si.tex\n"
           "    text: 'over the four sectors, fuel is'\n"
           "    why: '5 Nov 2026 (patch_fuel_20261105.py); count: the four fuel-fed service sectors named in the sentence "
           "(H49, H52, D, H50)'\n")


def main(repo: Path, ledger: Path, apply: bool):
    f = repo / "sections" / "si.tex"
    t = f.read_text(encoding="utf-8")
    if t.count(OLD) != 1:
        sys.exit(f"expected the old sentence once, found {t.count(OLD)}")
    y = ledger / "si_b.yaml"
    led = y.read_text(encoding="utf-8")
    k = led.index("\nclaims:\n")
    print(f"- {OLD}\n+ {NEW}\nledger si_b.yaml: + allowed 'over the four sectors, fuel is'")
    if apply:
        f.write_text(t.replace(OLD, NEW), encoding="utf-8")
        y.write_text(led[:k + 1] + ALLOWED + led[k + 1:], encoding="utf-8")
        print("written")
    else:
        print("dry run")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    main(Path(a.repo), Path(a.ledger), a.apply)
