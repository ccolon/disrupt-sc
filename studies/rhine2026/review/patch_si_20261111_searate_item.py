r"""SI, batch of 11 November 2026: the item of the sea rate in the ranked list says where the two rates come from and
that the source gives them in euros (the run entered the figures as dollars). Exact anchor.

    python patch_si_20261111_searate_item.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

s = Doc(OVERLEAF / "si.tex")
s.sub(r"With dry bulk at 0.0034 and liquid bulk at 0.0051 USD per tonne-kilometer, the costs of bulk carriers and tankers in the same source "
      r"\citep{kim2023}, and the capacities of the Rhine set again on the baseline that these rates give,",
      r"With dry bulk at 0.0034 and liquid bulk at 0.0051 USD per tonne-kilometer, the values that the source of the container rate gives "
      r"in euros for bulk carriers and tankers \citep{kim2023}, and with the capacities of the Rhine set again on the baseline that these "
      r"rates give,")
s.save()
