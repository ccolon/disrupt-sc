r"""SI revision of 10 Nov 2026, step 1: the author's comment in the rates table ("Would be better that caption, at least,
are hard coded in the .tex as the source ... Consider using the .tex as source of the truth"). The marker line of every
table block now says that the text is edited in the manuscript and that si_tables.py only checks and refreshes the
numbers; the comment line itself is removed (answered).   python patch_si_20261110_s0_markers.py [overleaf]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
OLD = "(written by studies/rhine2026/si_tables.py from the run tables; edit the generator, not this block)"
NEW = "(edit the caption, headers and text cells here; studies/rhine2026/si_tables.py only checks and refreshes the numbers)"
for name, n in (("si.tex", 15), ("main.tex", 1)):
    d = Doc(ov / name)
    d.sub(OLD, NEW, n)
    if name == "si.tex":
        d.line("% I have done edits here directly. Would be better that caption", None)
    d.save()
