r"""Second pass of the round of 12 November 2026 on si.tex, after proofreading patch_si_20261112_round.py: the reason of
each of the two restrictions on bulk is given with its restriction (the prohibitive penalty: no road or rail equivalent
at volume, as in Methods; road never a line-haul mode: the size of a truck), and the test of the modal-switch rule is
described as it was run (week 6 of a ten-week run with the reach closed to bulk).

    python studies/rhine2026/review/patch_si_20261112_round_b.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "si.tex")
d.sub(r"For bulk, we add two restrictions, because a truck carries 25 tonnes, against 2,000 and more for a barge or an ore train, so that road cannot replace the river in the time of an event. The penalty is prohibitive, and road is never a line-haul mode: a bulk shipment may not lengthen a road leg beyond the allowance, whatever the length of that leg on its normal route.",
      r"For bulk, we add two restrictions. The penalty is prohibitive, because tank barges and ore trains have no road or rail equivalent at volume in the time of an event. And road is never a line-haul mode, because a truck carries 25 tonnes, against 2,000 and more for a barge or an ore train: a bulk shipment may not lengthen a road leg beyond the allowance, whatever the length of that leg on its normal route.")
d.sub(r"whose bulk crosses Kaub, in a test of September 2026 with the reach closed to bulk for a week, on the baseline before the calibration of Section~S2.",
      r"whose bulk crosses Kaub, in a test of September 2026 with the reach closed to bulk (week 6 of a ten-week run, on the baseline before the calibration of Section~S2).")
d.save()
