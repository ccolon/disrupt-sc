r"""Build the document that the captions of Supplementary Tables S1, S2, S3 and S7 point to: the four tables in
their detailed form (every figure, date and source), as they stood in the Supplementary Information on 12 November
2026 before their evidence cells were rewritten in plain sentences. The tables are read from
si_tables_detailed_20261112.tex; the numbers that they print from macros and the references come from the manuscript
(numbers.tex and refs.bib of the Overleaf copy).

    python studies/rhine2026/evidence/build_si_tables_detailed.py [--overleaf DIR] [--tex ENGINE]

Output: si_tables_detailed.pdf next to this script. It goes into the data deposit (submission/build_zenodo_package.py).
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
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
SOURCE = HERE / "si_tables_detailed_20261112.tex"
NUMBER = {"si_rates": 1, "si_stocks": 2, "si_stock_overrides": 3, "si_loading_table": 7}     # the numbers of the tables in the SI

PREAMBLE = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=25mm]{geometry}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{xcolor}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\setlength{\LTcapwidth}{\textwidth}
\setlength{\belowcaptionskip}{6pt}
\usepackage[numbers,sort&compress]{natbib}
\usepackage[colorlinks=true,linkcolor=blue!60!black,citecolor=blue!60!black,urlcolor=blue!60!black]{hyperref}
\usepackage{xurl}
\input{numbers}
\renewcommand{\thetable}{S\arabic{table}}\renewcommand{\theHtable}{S\arabic{table}}
\title{\large Detailed evidence behind Supplementary Tables S1, S2, S3 and S7\\[2mm]
\normalsize of ``TITLE''}
\author{}
\date{}
\begin{document}
\maketitle
\noindent The Supplementary Information of the paper gives, for the transport costs, the inventory targets and the loading
curve of the model, a short account of the evidence behind each value. This document gives the same four tables in
their detailed form, with every figure, date and source. The values of the model are the same in both. Sections S2 and
S8 are sections of the Supplementary Information, and the abbreviations are explained in the notes under each table.

"""


def title(overleaf: Path) -> str:
    s = (overleaf / "main.tex").read_text(encoding="utf-8")
    m = re.search(r"\\title\{(.*?)\}\s*\n\\author", s, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else "the paper"


def main(overleaf: Path, tex: str | None):
    text = SOURCE.read_text(encoding="utf-8")
    body = []
    for name, n in NUMBER.items():
        m = re.search(r"^% >>> generated table " + name + r" [^\n]*\n(.*?)^% <<< generated table " + name, text, re.M | re.S)
        if not m:
            sys.exit(f"{SOURCE.name}: no table {name}")
        body.append(f"\\setcounter{{table}}{{{n - 1}}}\n" + m.group(1).strip() + "\n\\clearpage\n")
    doc = PREAMBLE.replace("TITLE", title(overleaf)) + "\n".join(body) + "\n\\bibliographystyle{unsrtnat}\n\\bibliography{refs}\n\\end{document}\n"
    engine = tex or shutil.which("tectonic") or str(Path.home() / ".local/bin/tectonic.exe")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "si_tables_detailed.tex").write_text(doc, encoding="utf-8")
        for f in ("numbers.tex", "refs.bib"):
            shutil.copy(overleaf / f, tmp / f)
        r = subprocess.run([engine, "si_tables_detailed.tex"], cwd=tmp, capture_output=True, text=True, encoding="utf-8", errors="replace")
        log = (r.stdout or "") + (r.stderr or "")
        pdf = tmp / "si_tables_detailed.pdf"
        if r.returncode != 0 or not pdf.exists():
            print(log[-3000:])
            sys.exit("the compile failed")
        bad = [ln for ln in log.splitlines() if "undefined" in ln.lower() and ("citation" in ln.lower() or "reference" in ln.lower())]
        shutil.copy(pdf, HERE / "si_tables_detailed.pdf")
    print(f"written {HERE / 'si_tables_detailed.pdf'}" + (f"; {len(bad)} warning(s) on citations or references:\n  " + "\n  ".join(bad[:8]) if bad else "; no undefined citation or reference"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    ap.add_argument("--tex", default=None, help="the LaTeX engine (default: tectonic)")
    a = ap.parse_args()
    main(Path(a.overleaf), a.tex)
