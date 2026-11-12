r"""Mechanical checks of the prose of main.tex and si.tex in the Overleaf copy (12 Nov 2026): unbalanced round brackets
in a paragraph, a word typed twice, doubled or misplaced punctuation, a citation glued to the word before it. It reads
the text outside the generated tables and the equations; it does not judge style.

    python studies/rhine2026/review/check_prose.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF  # noqa: E402

found = 0
for name in ("main.tex", "si.tex"):
    raw = (OVERLEAF / name).read_bytes().decode("utf-8").replace("\r\n", "\n")
    raw = re.sub(r"^% >>> generated table.*?^% <<< generated table[^\n]*$", lambda m: "\n" * m.group(0).count("\n"), raw, flags=re.M | re.S)
    for n, line in enumerate(raw.split("\n"), 1):
        s = line.split("%")[0] if line.lstrip().startswith("%") else line
        if not s.strip() or s.lstrip().startswith("\\begin") or s.lstrip().startswith("\\end"):
            continue
        prose = re.sub(r"\$[^$]*\$", "MATH", s)
        issues = []
        if prose.count("(") != prose.count(")"):
            issues.append(f"round brackets: {prose.count('(')} open, {prose.count(')')} closed")
        for m in re.finditer(r"\b([A-Za-z]{2,})\s+\1\b", prose):
            if m.group(1).lower() not in ("that", "had"):
                issues.append(f"word twice: '{m.group(0)}'")
        for pat, what in ((r"\.\.(?!\.)", "two full stops"), (r",,", "two commas"), (r" [,.;:](?![0-9])", "space before punctuation"),
                          (r"[a-z]\\cite", "citation glued to a word"), (r"  +\S", "two spaces"), (r"[;:,] *\.", "punctuation before a full stop"),
                          (r"\.\s+[a-z](?![.)])", "small letter after a full stop")):
            for m in re.finditer(pat, prose):
                ctx = prose[max(0, m.start() - 30):m.end() + 20]
                if what == "small letter after a full stop" and re.search(r"(i\.e|e\.g|refs?|Fig|et al|vs|St|cf)\.\s*[a-z]?$", prose[max(0, m.start() - 6):m.start() + 1]):
                    continue
                issues.append(f"{what}: ...{ctx}...")
        for i in issues:
            found += 1
            print(f"{name}:{n}  {i}")
print(f"{found} finding(s)")
