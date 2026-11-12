r"""Second pass of the round of 12 November 2026 on main.tex (note N07): the three longest sentences left after
patch_main_20261112_round.py are cut in two.

    python studies/rhine2026/review/patch_main_20261112_round_b.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "main.tex")
d.sub(r"reached the gauge zero (a conventional datum above the river bed): the weekly mean was 2\,cm",
      r"reached the gauge zero (a conventional datum above the river bed). The weekly mean was 2\,cm")
d.sub(r"and its memory is short: with the 30-day refill time of the model,", r"and its memory is short. With the 30-day refill time of the model,")
d.sub(r"that it keeps off the river at each gauge: raised and lowered by 15\,\%, it gives \TableLowInt{}",
      r"that it keeps off the river at each gauge. With this reduction raised and lowered by 15\,\%, the model gives \TableLowInt{}")
d.save()
