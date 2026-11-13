r"""Tables S1, S2, S3 and S7 of the SI in plain sentences (13 November 2026, the author's request: "I found the text hard
to read, very compact ... the goal is not that readers understand exactly how we extracted the information, but rather
get a sense of the evidence"). The author approved the level on two sample rows per table, the merging of rows of S2
that share a value, and two text columns in S7.

    python studies/rhine2026/review/patch_tools_20261113_evidence_tables.py     # the generator, once
    python studies/rhine2026/review/patch_si_20261113_evidence_tables.py        # this script
    python studies/rhine2026/si_tables.py --tag r6_bycargo --lists 20261111 --only rates,stocks,loading

This script (1) keeps the four tables as they were, whole, in evidence/si_tables_detailed_20261112.tex, (2) empties their
blocks in si.tex, which the generator then fills with the new tables, and (3) adds to the paragraph before the loading
curve the two kinds of evidence that the table rests on. Running it again changes nothing.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
BLOCKS = ("si_rates", "si_stocks", "si_stock_overrides", "si_loading_table")
KEEP = HERE / "evidence" / "si_tables_detailed_20261112.tex"

d = Doc(OVERLEAF / "si.tex")
t = d.text
kept = []
for name in BLOCKS:
    m = re.search(r"^(% >>> generated table " + name + r" [^\n]*\n)(.*?)(^% <<< generated table " + name + r"[ \t]*\n)", t, re.M | re.S)
    assert m, name
    if "\\begin{" in m.group(2):
        kept.append(m.group(1) + m.group(2) + m.group(3))
        t = t[:m.start(2)] + t[m.end(2):]
        d.done += 1
if kept and not KEEP.exists():
    KEEP.write_text("% Tables S1 (transport costs), S2 (inventories by industry), S3 (inventories by input) and S7 (loading curve) of the\n"
                    "% Supplementary Information as they stood on 12 November 2026 (Overleaf 69660ff), before their evidence cells were\n"
                    "% rewritten in plain sentences on 13 November 2026. This is the detailed record: every figure, date and source.\n"
                    "% The citation keys are those of refs.bib of the manuscript.\n\n" + "\n".join(kept), encoding="utf-8")
    print(f"kept the detailed tables in {KEEP.relative_to(HERE)}")
d.text = t

old = (r"to link gauge values to the share of the normal tonnage that the Kaub reach can pass, which we call the \textit{loading share}. "
       r"The model interpolates linearly between those values and stays at 0.08 below 5\,cm.")
new = (r"to link gauge values to the share of the normal tonnage that the Kaub reach can pass, which we call the \textit{loading share}. "
       r"Most of this evidence says what one vessel can load at a given gauge. Operators then put more vessels on the route for the same "
       r"cargo, and the loading share is the product of the two. The number of extra vessels is assumed at each gauge, from reports of "
       r"about twice as many vessels at moderate low water; only one count of tonnage exists, at a gauge of about 12\,cm. "
       r"The model interpolates linearly between those values and stays at 0.08 below 5\,cm.")
d.sub(old, new)
d.save()
