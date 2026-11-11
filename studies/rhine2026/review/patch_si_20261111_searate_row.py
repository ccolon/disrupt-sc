r"""SI, batch of 11 November 2026: the sea-rate run in the sensitivity section (open point 3 of the round of 10 November).
One row in the table of the sensitivity runs (the numbers are refreshed by si_tables.py), one item in the ranked list, one
sentence in the cell of the sea rate in the table of the transport costs. Exact anchors; nothing is written if one is missing.

    python patch_si_20261111_searate_row.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

s = Doc(OVERLEAF / "si.tex")

# ---- the row of the table (before the row of the mechanisms; the generator has it at the same place)
s.sub("mechanisms & capacity limit and surcharge & capacity limit alone &",
      "sea rate of bulk cargo, USD per tonne-kilometer & 0.0015 & 0.0034 for dry bulk, 0.0051 for liquid bulk & 1.22 & $-$0.5 & -- &  \\\\\n"
      "mechanisms & capacity limit and surcharge & capacity limit alone &")

# ---- the item of the ranked list (after the two rules on energy and services, before the variants of the levers)
s.sub(r"    \item \emph{Variants of two levers.}",
      r"    \item \emph{The sea rate of bulk cargo.} The runs price sea transport at one rate, that of container carriers. With dry bulk "
      r"at 0.0034 and liquid bulk at 0.0051 USD per tonne-kilometer, the costs of bulk carriers and tankers in the same source "
      r"\citep{kim2023}, and the capacities of the Rhine set again on the baseline that these rates give, the 2026 loss is "
      r"\RevSeaRate\,\% of a quarter instead of \DEUlossQ{} (\RevSeaRateRel\,\%). The smallest effect of the table." "\n"
      r"    \item \emph{Variants of two levers.}")

# ---- the cell of the sea rate in the table of the transport costs
s.sub(r"so the sea leg of bulk is under-priced two- to threefold. Sea lanes carry no capacity limit in this study;",
      r"so the sea leg of bulk is under-priced two- to threefold; a run with bulk at these two rates changes the 2026 loss by "
      r"\RevSeaRateRel\,\% (Section~S9). Sea lanes carry no capacity limit in this study;")
s.save()
