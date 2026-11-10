r"""Ledger of paper_gate.py after the author's revision of the SI of 10 November 2026, section by section (the sections
are added to this script as they are answered; running it again changes nothing).

    python studies/rhine2026/review/ledger_si_20261110.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402

L = Ledger()
SI, MAIN = "si.tex", "main.tex"

# ---------------------------------------------------------------- main.tex (the author's edits of 10 Nov)
L.allow(MAIN, "Anthropic Fable 5.1 was used", "count: a product version in the author's AI disclosure")

# ---------------------------------------------------------------- S1 Scope and data
L.drop("Eleven sectors use facility data",
       "roads (2,979 edges), railways (4,261), inland waterways (461, the Rhine",
       "as a chain of thirty named reaches",
       "eighteen commodity-like products are pooled across regions",
       "The 39 other sectors are placed on NUTS3 employment",
       r"survey of ref.~\citep{pichler2022} mapped to the 50 sectors")
L.allow(SI, "Ten sectors use facility data. Nine keep their facilities as points",
        "count: the ten facility sectors of the sentence (B05, B06, B07, C19, C20, C17-18, C24B, C23, C24A kept as points; D aggregated "
        "to NUTS2 capacity); crops (A01) use a gridded source and are named before")
L.claim(SI, "The 39 other sectors are downscaled using NUTS3 employment", "NSectors - 11", [39, 39],
        r"data bound to the macro: \NSectors less crops (A01) and the ten facility sectors")
L.allow(SI, "roads (2,979 edges), railways (4,261), inland waterways (461, including 30 for the Rhine from Basel to Rotterdam)",
        "data: edge counts by mode of the TEN-T extraction of 29 August 2026; the Rhine is a chain of 30 named reaches")
L.claim(SI, r"survey of Pichler et al.~\citep{pichler2022} mapped to the 50 sectors", "NSectors", [50, 50],
        r"data bound to the macro: the literal 50 is \NSectors")
L.allow(SI, "We assume that 18 commodity-like products are pooled across regions",
        "count: the eighteen pooled products listed in the sentence (the pooled sectors of the configuration)")
L.claim(SI, r"\textbf{The criticality survey mapped to the 50 sectors.}", "NSectors", [50, 50],
        r"data bound to the macro: the literal 50 is \NSectors (caption of Table S-criticality)")
L.allow(SI, r"whose industries are the 55 of the World Input--Output Database (NACE Rev.~2)",
        "data: the 55 industries of the World Input-Output Database in which the survey is expressed (pichler2022); NACE revision 2")
L.claim(SI, "how many of its 50 input sectors the survey rates", "NSectors", [50, 50],
        r"data bound to the macro: the literal 50 is \NSectors")
L.allow(SI, "(a depleted input halves output)", "design: the rule of an important input in the production function (Methods)")
L.allow(SI, r"an input below 2\,\% of the buyer's input costs is considered non-critical",
        "design: the 2 % threshold of the critical-input rule (Methods)")
L.allow(SI, r"Over the 2,500 sector-to-sector pairs, 18\,\% of the inputs are critical, 9\,\% important and 73\,\% non-critical",
        "data: shares of the 50 x 50 cells of additional_data/input_criticality.csv (si_tables.criticality_table computes 18 / 9 / 73)")

L.save()
