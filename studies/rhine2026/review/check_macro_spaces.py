r"""A number macro followed directly by a space swallows it: `\PeakDateFirst and` prints '5 Octoberand'. Lists every
such place in main.tex and si.tex of the Overleaf copy (found on 12 Nov 2026 while checking the author's round).

    python studies/rhine2026/review/check_macro_spaces.py [--fix]

With --fix, `{}` is put after the macro. Exit code 1 when a place is found and not fixed.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF  # noqa: E402

fix = "--fix" in sys.argv
macros = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", (OVERLEAF / "numbers.tex").read_text(encoding="utf-8")))
found = 0
for name in ("main.tex", "si.tex"):
    p = OVERLEAF / name
    raw = p.read_bytes().decode("utf-8")
    hits = [m for m in re.finditer(r"\\([A-Za-z]+)( +)(?=[A-Za-z0-9(])", raw) if m.group(1) in macros]
    for m in hits:
        line = raw.count("\n", 0, m.start()) + 1
        print(f"{name}:{line}  ...{raw[max(0, m.start() - 35):m.end() + 25]!r}")
    found += len(hits)
    if fix and hits:
        for m in reversed(hits):
            raw = raw[:m.end(1)] + "{}" + raw[m.end(1):]
        p.write_bytes(raw.encode("utf-8"))
        print(f"{name}: {len(hits)} place(s) fixed")
print(f"{found} place(s)" + (" fixed" if fix else ""))
sys.exit(1 if found and not fix else 0)
