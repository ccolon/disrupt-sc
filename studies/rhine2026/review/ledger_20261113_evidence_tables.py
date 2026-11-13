r"""Ledger of paper_gate.py for the sentence added before the loading curve on 13 November 2026
(patch_si_20261113_evidence_tables.py). Running it again changes nothing.

    python studies/rhine2026/review/ledger_20261113_evidence_tables.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402

L = Ledger()
LEDGER = "scenarios/draught_table_ledger.csv"
L.allow("si.tex", "from reports of about twice as many vessels at moderate low water",
        f"evidence: {LEDGER}, row of 55 cm (trade press of 2026: twice the number of vessels deployed for the same cargo at moderate low water)")
L.allow("si.tex", r"only one count of tonnage exists, at a gauge of about 12\,cm",
        f"evidence: {LEDGER}, row of 15 cm (count of the Dutch inland navigation association for the week to about 13 August 2026, mean gauge about 12 cm)")
L.save()
