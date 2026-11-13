"""Build the submission files of the Rhine 2026 paper from the Overleaf working copy, in a temporary copy:

    python studies/rhine2026/submission/build_submission.py --overleaf <dir> --out <dir> [--tex <engine>]

Outputs (in --out, default C:/dsc_runs/rhine2026/submission):
    main_text.pdf                 the manuscript without the SI (main_text.tex defines \\NoSupplement)
    supplementary_information.pdf the SI as a separate document (si_standalone.tex defines \\StandaloneSI)
    combined.pdf                  the Overleaf build (main.tex), for reading
    wordcount.txt                 the counts against the journal's guide (also printed)
    build.log                     the engines' output

With --anonymous (double-anonymised peer review, 13 Nov 2026) the temporary copy of main.tex loses the author block,
the funding and author-contribution sections (they go to the cover letter), the address of the code repository and the
first-person reference to earlier work; the PDFs are main_text_anonymous.pdf and
supplementary_information_anonymous.pdf, and they are searched for identifying strings. The metadata of every PDF is
removed.

The two split documents read each other's labels through xr-hyper (preamble of main.tex), so the order is SI, main, SI.
Undefined references left after that are listed as a failure. The engine is latexmk, tectonic or pdflatex on PATH,
else ~/.local/bin/tectonic.exe (as paper_gate.py). Nothing in the Overleaf folder is modified.
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
sys.path.insert(0, str(HERE))
from wordcount import report as wordcount_report  # noqa: E402

OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
OUT = Path("C:/dsc_runs/rhine2026/submission")


def find_engine(tex: str | None) -> Path | None:
    if tex:
        return Path(tex)
    for e in ("latexmk", "tectonic", "pdflatex"):
        if shutil.which(e):
            return Path(shutil.which(e))
    home = Path.home() / ".local" / "bin" / "tectonic.exe"
    return home if home.exists() else None


def run_engine(engine: Path, job: str, work: Path, log: list[str]) -> bool:
    kind = next(k for k in ("latexmk", "tectonic", "pdflatex") if k in engine.name.lower())
    e = str(engine)
    cmds = {"latexmk": [[e, "-pdf", "-interaction=nonstopmode", f"{job}.tex"]],
            "tectonic": [[e, "--only-cached", "--keep-logs", "--keep-intermediates", f"{job}.tex"]],
            "pdflatex": [[e, "-interaction=nonstopmode", f"{job}.tex"], ["bibtex", job],
                         [e, "-interaction=nonstopmode", f"{job}.tex"], [e, "-interaction=nonstopmode", f"{job}.tex"]]}[kind]
    ok = True
    for c in cmds:
        r = subprocess.run(c, cwd=work, capture_output=True, text=True, timeout=1800)
        if r.returncode and kind == "tectonic":
            log.append(f"[{job}] tectonic --only-cached failed: retrying online")
            r = subprocess.run([x for x in c if x != "--only-cached"], cwd=work, capture_output=True, text=True, timeout=1800)
        log.append(f"[{job}] $ {' '.join(c)}\n{r.stdout}\n{r.stderr}")
        if r.returncode:
            ok = False
    return ok


# what must not be read in an anonymised manuscript (the reference list may name the author as any other author)
IDENTIFYING = ("polytechnique", "IIASA", "Applied Systems Analysis", "Laxenburg", "github.com/ccolon", "FutureGVC", "OeNB", "Jubil",
               "Our earlier work", "C.C. conceived")


def anonymise(main: Path) -> list[str]:
    """main.tex of the temporary copy without what identifies the author (the journal's checklist for double-anonymised
    peer review); returns what could not be done."""
    s = main.read_bytes().decode("utf-8")
    problems = []

    def rsub(pattern: str, repl: str, what: str, flags=0):
        nonlocal s
        new, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
        if n != 1:
            problems.append(f"anonymise: {what} not found")
        s = new

    rsub(r"\\author\{.*?\}(\r?\n)\\date\{", "\\author{}\n\\date{", "the author block", re.S)
    rsub(r"Our earlier work coupled a firm-level supply-chain model to national road and multimodal networks "
         r"(\\citep\{colon2021,colon2022disruptsc\})\. Here we build it for a whole continental economy\.",
         "Earlier work coupled a firm-level supply-chain model to national road and multimodal networks "
         "\\citep{colon2021,colon2022disruptsc}. Here such a model is built for a whole continental economy.",
         "the sentence on earlier work")
    rsub(r" at \\url\{https://github\.com/[^}]*\}\. The study scripts", "; the address of the repository is withheld for "
         "double-anonymized peer review and given to the editors. The study scripts", "the address of the code repository")
    rsub(r"\\section\*\{Funding\}.*?(?=\\section\*\{Competing interests\})", "", "the funding and author-contribution sections", re.S)
    main.write_bytes(s.encode("utf-8"))
    body = re.sub(r"(?m)^%.*$", "", s)
    problems += [f"anonymise: main.tex still reads {w!r}" for w in IDENTIFYING if w in body]
    return problems


def strip_metadata(pdf: Path) -> None:
    """No title, author, creator or XMP packet in the PDF (the checklist: 'remove any author information from all
    submitted files' metadata')."""
    import pymupdf
    tmp = pdf.with_suffix(".clean.pdf")
    with pymupdf.open(pdf) as d:
        d.set_metadata({})
        d.del_xml_metadata()
        d.save(tmp, garbage=3, deflate=True)
    tmp.replace(pdf)


def identifying_in_pdf(pdf: Path) -> list[str]:
    import pymupdf
    with pymupdf.open(pdf) as d:
        text = "\n".join(p.get_text() for p in d)
        meta = " ".join(str(v) for v in (d.metadata or {}).values() if v)
    return [w for w in IDENTIFYING if w in text or w in meta]


def undefined_refs(work: Path, job: str) -> list[str]:
    logf = work / f"{job}.log"
    if not logf.exists():
        return []
    txt = logf.read_text(encoding="utf-8", errors="replace")
    return sorted(set(re.findall(r"Reference `([^']+)' on page", txt)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--tex", default=None)
    ap.add_argument("--anonymous", action="store_true", help="the files for double-anonymised peer review (see the module's docstring)")
    a = ap.parse_args()
    ov, out = Path(a.overleaf), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    engine = find_engine(a.tex)
    if engine is None:
        sys.exit("no TeX engine found (latexmk / tectonic / pdflatex on PATH, or ~/.local/bin/tectonic.exe)")
    for w in ("maintext.tex", "supplement.tex"):
        if not (ov / w).exists():
            sys.exit(f"{w} missing in the Overleaf copy (the split-build wrappers of 7 Nov 2026)")
    log: list[str] = []
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "paper"
        shutil.copytree(ov, work, ignore=shutil.ignore_patterns(".git"))
        if a.anonymous:
            failures += anonymise(work / "main.tex")
        # SI first (its labels), then the main text (reads them), then the SI again (reads the main text's labels)
        jobs = ("supplement", "maintext", "supplement") + (() if a.anonymous else ("main",))
        for job in jobs:
            if not run_engine(engine, job, work, log):
                failures.append(f"{job}: the engine exited with an error (see build.log)")
        names = ((("maintext", "main_text_anonymous.pdf"), ("supplement", "supplementary_information_anonymous.pdf")) if a.anonymous else
                 (("maintext", "main_text.pdf"), ("supplement", "supplementary_information.pdf"), ("main", "combined.pdf")))
        for job, name in names:
            pdf = work / f"{job}.pdf"
            if pdf.exists():
                shutil.copy2(pdf, out / name)
                strip_metadata(out / name)
                if a.anonymous:
                    found = identifying_in_pdf(out / name)
                    if found:
                        failures.append(f"{name}: identifying text left: {found}")
            else:
                failures.append(f"{job}.pdf not produced")
            und = undefined_refs(work, job)
            if und:
                failures.append(f"{job}: undefined references {und}")
    (out / ("build_anonymous.log" if a.anonymous else "build.log")).write_text("\n".join(log), encoding="utf-8")
    wc = wordcount_report(ov)
    (out / "wordcount.txt").write_text(wc, encoding="utf-8")
    print(wc)
    try:
        import pymupdf
        for name in (("main_text_anonymous.pdf", "supplementary_information_anonymous.pdf") if a.anonymous else
                     ("main_text.pdf", "supplementary_information.pdf", "combined.pdf")):
            f = out / name
            if f.exists():
                with pymupdf.open(f) as d:
                    print(f"{name}: {d.page_count} pages, {f.stat().st_size / 1e6:.1f} MB")
    except ImportError:
        pass
    if failures:
        print("FAILURES:")
        for x in failures:
            print(" -", x)
        sys.exit(1)
    print(f"submission files written to {out}")


if __name__ == "__main__":
    main()
