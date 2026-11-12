r"""Ledger of paper_gate.py after the protocol of the 2026 test left the paper (12 November 2026, evening;
patch_20261112_protocol_out.py): the entries of the sentences of the former Section S6 are dropped and appended to
ledger_dropped_20261112.txt. No entry is added: the text that stays was already covered. Running it again changes
nothing.

    python studies/rhine2026/review/ledger_20261112_protocol_out.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402
from si_patchlib import OVERLEAF  # noqa: E402

L = Ledger()
dropped = L.drop_missing(OVERLEAF)
L.save()
if dropped:
    log = Path(__file__).resolve().parent / "ledger_dropped_20261112.txt"
    with log.open("a", encoding="utf-8") as f:
        f.write("\nDropped in the evening of 12 November 2026, with the protocol of the 2026 test (the former Section S6 of the SI):\n"
                + "\n".join(dropped) + "\n")
    print(f"{len(dropped)} dropped, appended to {log.name}")
