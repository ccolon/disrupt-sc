r"""make_numbers.py after the batch of 11 November 2026: the header comment of numbers.tex no longer names the profile of
30 September nor the \finalbatch mark (removed from the manuscript on 11 November). Exact anchor.

    python patch_tools_20261111_header.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

m = Doc(HERE.parent / "make_numbers.py")
m.sub('''             "% non-storable input, the loading table rebuilt on its ledger (6 Oct 2026); the 2026 profile of 30 Sep (observations to 29 Sep,",
             "% the BfG outlook of 28 Sep, 23 weeks). Do not edit by hand: rerun the script after a batch.",
             "% \\\\finalbatch{} in the text marks the 2026 numbers of the forecast that the revision after the event replaces."]''',
      '''             "% non-storable input, the loading table rebuilt on its ledger (6 Oct 2026); the 2026 profile is scenarios/2026.csv (from the batch",
             "% of 20261111: the river as observed to 10 Nov 2026, 23 weeks). Do not edit by hand: rerun the script after a batch."]''')
m.save()
