r"""Negative tests of paper_gate.py (5 Nov 2026): every failure mode must fire on a copy of the manuscript with planted
faults (stale ledger entry, claim out of range, claim on an unknown macro, pending entry present and resolved, bare
number, undefined citation/reference/macro in the source and in the compile log). Rerun after any change to the gate:

    python studies/rhine2026/paper_gate_selftest.py [--repo <overleaf checkout>] [--no-compile]

The copies go to a temporary folder; the Overleaf checkout is only read. With the compile (tectonic) it takes ~2 min.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "paper_gate.py"
REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")

LEDGER = r"""
ignore:
  - 'of a quarter'
allowed:
  - file: main.tex
    text: 'this sentence was never in the paper 123'
    why: 'design: planted stale entry'
claims:
  - file: main.tex
    text: 'nearly three times the industrial loss alone'
    expr: 'EnsMean'
    range: [5, 6]
    why: 'planted: out of range'
  - file: main.tex
    text: 'Calibrated on the 2018 low water'
    expr: 'NoSuchMacro * 2'
    range: [0, 1]
    why: 'planted: unknown macro'
  - file: main.tex
    text: 'would each remove two fifths of it'
    expr: 'LevStock'
    range: [0, 100]
    why: 'planted: in range'
pending:
  - file: main.tex
    text: 'About 10\% of the tonnage that is cut is rerouted'
    note: 'planted pending: use \ResentShare'
  - file: main.tex
    text: 'a pending sentence that is gone 7'
    note: 'planted resolved pending'
"""


def make_copy(src: Path, root: Path, extra: str) -> Path:
    """The manuscript without .git, the planted sentence at the end of the abstract, the planted ledger."""
    shutil.copytree(src, root / "paper", ignore=shutil.ignore_patterns(".git"))
    (root / "ledger").mkdir()
    (root / "ledger" / "test.yaml").write_text(LEDGER, encoding="utf-8")
    m = root / "paper" / "main.tex"
    m.write_text(m.read_text(encoding="utf-8").replace("\\end{abstract}", extra + "\n\\end{abstract}", 1), encoding="utf-8")
    return root


def run(root: Path, compile_: bool):
    rep = root / "report.md"
    cmd = [sys.executable, str(GATE), "--repo", str(root / "paper"), "--ledger", str(root / "ledger"), "--report", str(rep)]
    if not compile_:
        cmd.append("--no-compile")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE.parents[1])
    return r.returncode, rep.read_text(encoding="utf-8")


def main(src: Path, compile_: bool) -> int:
    results = []

    def expect(label, ok):
        print(("PASS  " if ok else "FAIL  ") + label)
        results.append(bool(ok))

    with tempfile.TemporaryDirectory() as a_dir, tempfile.TemporaryDirectory() as b_dir:
        # A: ledger faults, a bare number, an undefined reference and citation (compiles, with warnings)
        a = make_copy(src, Path(a_dir), "The planted loss is 42.7 per cent, see Fig.~\\ref{fig:doesnotexist} and "
                                         "\\citep{nokey2099}, at ≈ the planted level.")
        code, rep = run(a, compile_)
        expect("exit code 1", code == 1)
        expect("static: citation key not in refs.bib", "citation key not in refs.bib: nokey2099" in rep)
        expect("static: \\ref to undefined label", "undefined label fig:doesnotexist" in rep)
        expect("ledger: stale allowed entry", "text no longer in main.tex" in rep and "never in the paper 123" in rep)
        expect("ledger: claim out of range", re.search(r"EnsMean = [\d.]+, outside \[5, 6\]", rep) is not None)
        expect("ledger: claim with unknown macro", "NoSuchMacro" in rep)
        expect("ledger: claim in range accepted", "claim ok: 'would each remove two fifths of it'" in rep)
        expect("pending: present entry fails with its note", "planted pending: use \\ResentShare" in rep)
        expect("pending: resolved entry warns", "pending entry no longer in main.tex" in rep)
        expect("bare: planted 42.7 flagged", "  42.7  |" in rep)
        expect("pdflatex: planted U+2248 flagged", "U+2248" in rep and "pdfLaTeX on Overleaf will stop" in rep)
        expect("bare: a number inside a pending snippet is not reported again",
               not re.search(r"main\.tex:\d+  10  \| .*tonnage that is cut", rep))
        if compile_:
            expect("compile: undefined citation", "undefined citation: nokey2099" in rep)
            expect("compile: undefined reference", "undefined reference: fig:doesnotexist" in rep)
        # B: an undefined control sequence fails the macro check and the compile
        b = make_copy(src, Path(b_dir), r"The planted macro \NotAMacro{} breaks the build.")
        code, rep = run(b, compile_)
        expect("macros: \\NotAMacro used but defined nowhere", "\\NotAMacro is used but defined nowhere" in rep)
        if compile_:
            expect("compile: LaTeX error reported", re.search(r"(LaTeX error: ! Undefined control sequence|exited [1-9])", rep) is not None)
    print(f"{sum(results)}/{len(results)} expectations met")
    return 0 if all(results) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--no-compile", action="store_true")
    a = ap.parse_args()
    sys.exit(main(Path(a.repo), not a.no_compile))
