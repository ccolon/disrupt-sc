r"""Static checks of the Overleaf manuscript before a compile (30 Sep 2026): citation keys against refs.bib, inputs and
figures that exist, brace and math-mode balance, unescaped _ & # outside math and \texttt, \ref against \label, and
the cell counts of the generated tables.

Usage:
    python studies/rhine2026/lint_manuscript.py [--repo <overleaf checkout>]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("%"):
            out.append("")
            continue
        # a % not preceded by a backslash starts a comment
        m = re.search(r"(?<!\\)%", line)
        out.append(line[:m.start()] if m else line)
    return "\n".join(out)


def main(repo: Path):
    files = [repo / "main.tex", repo / "numbers.tex"] + sorted((repo / "sections").glob("*.tex")) + sorted((repo / "tables").glob("*.tex"))
    keys = set(re.findall(r"@\w+\{([^,]+),", (repo / "refs.bib").read_text(encoding="utf-8")))
    problems, labels, refs = [], set(), set()
    for f in files:
        rel = f.relative_to(repo).as_posix()
        body = strip_comments(f.read_text(encoding="utf-8"))
        for c in re.findall(r"\\cite[pt]?\{([^}]*)\}", body):
            for k in c.split(","):
                if k.strip() and k.strip() not in keys:
                    problems.append(f"{rel}: citation key not in refs.bib: {k.strip()}")
        for inc in re.findall(r"\\input\{([^}]*)\}", body):
            if not (repo / (inc if inc.endswith(".tex") else inc + ".tex")).exists():
                problems.append(f"{rel}: missing input {inc}")
        for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", body):
            if not (repo / g).exists():
                problems.append(f"{rel}: missing figure {g}")
        if body.count("{") != body.count("}"):
            problems.append(f"{rel}: braces {body.count('{')} open vs {body.count('}')} close")
        for i, line in enumerate(body.splitlines(), 1):
            if line.count("$") % 2:
                problems.append(f"{rel}:{i}: odd number of $")
            clean = re.sub(r"\$[^$]*\$", "", line)
            clean = re.sub(r"\\(texttt|url|href|label|ref|input|includegraphics|bibliography|bibliographystyle|usepackage)(?:\[[^\]]*\])?\{[^}]*\}", "", clean)
            if re.search(r"(?<!\\)_", clean):
                problems.append(f"{rel}:{i}: unescaped _ : {clean.strip()[:90]}")
            if re.search(r"(?<!\\)&", clean) and not rel.startswith("tables"):
                problems.append(f"{rel}:{i}: unescaped & : {clean.strip()[:90]}")
            if re.search(r"(?<!\\)#", clean) and "newcommand" not in clean:
                problems.append(f"{rel}:{i}: unescaped # : {clean.strip()[:90]}")
        labels |= set(re.findall(r"\\label\{([^}]*)\}", body))
        refs |= set(re.findall(r"\\ref\{([^}]*)\}", body))
    for r in sorted(refs - labels):
        problems.append(f"\\ref to undefined label {r}")
    for f in sorted((repo / "tables").glob("*.tex")):
        t = f.read_text(encoding="utf-8")
        spec = re.search(r"\\begin\{(?:tabular|longtable)\}\{((?:[^{}]|\{[^{}]*\})*)\}", t).group(1)
        ncol = len(re.findall(r"[lrc]|p\{[^}]*\}", spec))
        for i, line in enumerate(t.splitlines(), 1):
            if line.rstrip().endswith("\\\\") and "&" in line and line.count("&") + 1 != ncol:
                problems.append(f"{f.name}:{i}: {line.count('&') + 1} cells for {ncol} columns")
    print("\n".join(problems) if problems else "no static problems found")
    print(f"checked {len(files)} files, {len(keys)} bib keys")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    a = ap.parse_args()
    main(Path(a.repo))
