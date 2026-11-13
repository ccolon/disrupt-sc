r"""The last two edits of main.tex before submission (13 November 2026): the title page no longer says "Draft of
<date>", and the red note of Code availability goes (the sentence already says that the release is archived upon
acceptance; the author chose not to deposit on Zenodo before submission).

    python studies/rhine2026/review/patch_main_20261113_submission.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "main.tex")
d.sub(r"\date{Draft of \today}", r"\date{}")
d.sub(r"will be tagged and archived on Zenodo with a DOI upon acceptance (\todo{tag the release, reserve the Zenodo DOI and write it here}). Until then,",
      r"will be tagged and archived on Zenodo with a DOI upon acceptance. Until then,")
d.save()
