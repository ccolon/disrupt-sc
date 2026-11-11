r"""Ledger of paper_gate.py after the round of 11 November 2026 (the author's version of that morning, Overleaf 41f0e3c,
and the answers to the open points). Running it again changes nothing.

  1. the entries that quoted the superscript macro lose it, as the manuscript did (\finalbatch{X} -> X);
  2. new entries for the sentences that were reworded;
  3. the entries whose sentence left the manuscript are dropped and listed in ledger_dropped_20261111.txt.

    python studies/rhine2026/review/ledger_20261111.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import LEDGER, Ledger  # noqa: E402
from si_patchlib import OVERLEAF  # noqa: E402

# ---- 1. the superscript macro inside quoted texts --------------------------------------------------------------------
pat = re.compile(r"\\{1,2}finalbatch\{([^{}]*)\}")
n = 0
for p in sorted(LEDGER.glob("*.yaml")):
    raw = p.read_bytes().decode("utf-8")
    new, k = pat.subn(lambda m: m.group(1), raw)
    if k:
        p.write_bytes(new.encode("utf-8"))
        n += k
print(f"superscript macro removed from {n} quoted text(s) of the ledger")

L = Ledger()
SI, MAIN = "si.tex", "main.tex"

# ---- 2. reworded sentences -------------------------------------------------------------------------------------------
# S3 (the author's edits of 11 Nov)
L.allow(SI, "we build two additional profiles from its 25th and 75th percentiles for the forecast weeks",
        "data: the 25-75 % quantiles of the BfG outlook of 28 Sep (scenarios/2026_q25.csv, 2026_q75.csv)")
L.allow(SI, r"are three distinct fleets: $K_{r,c}=\max\!\big(s_{r,c}\,T_r,\;1.02\,F_{r,c}\big)$",
        "design: the capacity per cargo class (anchor_rhine_capacities.py --by-cargo --headroom 0.02: the larger of the counted tonnage "
        "split by the baseline's class shares and the baseline flow of the class plus 2 %)")
L.allow(SI, r"the factor 1.02 leaves a headroom of 2\,\% over the model's own flow",
        "design: the headroom of the anchored capacities (0.02)")
L.allow(SI, "At Kaub, this gives 175,900 t a day in total: 32,400 for container vessels, 62,900 for dry-bulk vessels, and 80,600 for tank barges",
        "data: scenarios/rhine_capacities_anchored_r6_bycargo.csv, reach rhine_mainz_koblenz (per-class capacities and their sum)")
L.allow(SI, "and one third of its excess over 1 on the Lower Rhine reaches. This one-third factor is an assumption",
        "design: lower_rhine_factor = 1/3 (run_rhine.py, DEFAULT_LOWER_RHINE_FACTOR)")
# S8 and the main text: the counts of the former table of rail weeks (note N12)
L.allow(SI, r"The 50 kt ceiling is reached in \RailBindFifty{} of the 23 profile weeks of 2026 and in \RailBindFiftyyy{} of the 22 of 2018, the 140 kt ceiling in",
        "design and data: the two ceilings of the rail runs (50 and 140 kt a week) and the lengths of the two profiles (23 weeks in "
        "scenarios/2026.csv, 22 in scenarios/2018.csv); the counts themselves are macros")
L.claim(SI, "A ceiling of 50 kt a week is reached in nearly every profile week of both events", "min(RailBindFifty/23, RailBindFiftyyy/22)", [0.9, 1.0],
        "result: the 50 kt ceiling is reached in 23 of 23 profile weeks of 2026 and 21 of 22 of 2018")
L.claim(MAIN, "The lower ceiling is reached in nearly every week of both events", "min(RailBindFifty/23, RailBindFiftyyy/22)", [0.9, 1.0],
        "result: the 50 kt ceiling is reached in 23 of 23 profile weeks of 2026 and 21 of 22 of 2018")
L.claim(MAIN, "the higher one in most", "min(RailBindHundredForty/23, RailBindHundredFortyyy/22)", [0.6, 0.95],
        "result: the 140 kt ceiling is reached in 20 of 23 profile weeks of 2026 and 17 of 22 of 2018")

# ---- 3. sentences that left the manuscript -----------------------------------------------------------------------------
dead = L.drop_missing(OVERLEAF)
L.save()
out = Path(__file__).resolve().parent / "ledger_dropped_20261111.txt"
out.write_text("Ledger entries dropped on 11 November 2026: their sentence is no longer in the manuscript (Overleaf 41f0e3c and the "
               "round of that day).\n\n" + "\n".join(sorted(dead)) + "\n", encoding="utf-8")
print(f"{len(dead)} dropped entries listed in {out.name}")
