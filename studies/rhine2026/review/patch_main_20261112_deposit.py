r"""main.tex, 12 November 2026: the deposit that dates the test. The plan of 11 November (response file, section 5, "Public
date") and the cover letter say that the monthly path, the gauge profile and the run tables are deposited on Zenodo on
the day of submission; the manuscript said "upon acceptance" for every data set. The Methods and the Data availability
statement now say it, with a note for the DOI, which only the author can obtain. Exact anchors.

    python patch_main_20261112_deposit.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

m = Doc(OVERLEAF / "main.tex")
m.sub(r"those of October, November and December are released after submission, and the score over these three months is reported "
      r"alongside. The index relative to its pre-event level",
      r"those of October, November and December are released after submission, and the score over these three months is reported "
      r"alongside. The monthly path of Table~\ref{tab:prospective}, the gauge profile and the run tables are deposited on Zenodo on the "
      r"day of submission (\todo{deposit them and write the DOI here}), which gives the estimate a public date. The index relative to "
      r"its pre-event level")
m.sub(r"The model's scope data package (network, agents, tables, and scenario files) and every run table in this paper will be deposited "
      r"on Zenodo upon acceptance; until then, they are available from the corresponding author.",
      r"The gauge profile, the monthly path of Table~\ref{tab:prospective} and the run tables of this paper are deposited on Zenodo at "
      r"submission (Methods). The model's scope data package (network, agents, tables, and scenario files) will be deposited on Zenodo "
      r"upon acceptance; until then, it is available from the corresponding author.")
m.save()
