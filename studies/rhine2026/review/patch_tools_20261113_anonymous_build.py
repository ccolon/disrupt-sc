r"""submission/build_submission.py for double-anonymised peer review (13 November 2026: the author chose that option in
the submission form of Nature Communications). Applied once.

    python studies/rhine2026/review/patch_tools_20261113_anonymous_build.py

New option --anonymous: in the temporary copy, main.tex loses what the journal's checklist asks to remove (author,
affiliation and address; funding and author contributions, which go to the cover letter; the address of the code
repository; the first-person reference to the author's earlier work), the two documents are built, the result is
checked for identifying strings, and the PDFs are written as main_text_anonymous.pdf and
supplementary_information_anonymous.pdf. Both builds now strip the metadata of the PDFs. Nothing in the Overleaf
folder is modified.
"""
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "submission" / "build_submission.py"
raw = P.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
s = raw.replace("\r\n", "\n")
assert "--anonymous" not in s, "already applied"


def sub(old: str, new: str) -> None:
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)


sub('''The two split documents read each other's labels through xr-hyper''',
    '''With --anonymous (double-anonymised peer review, 13 Nov 2026) the temporary copy of main.tex loses the author block,
the funding and author-contribution sections (they go to the cover letter), the address of the code repository and the
first-person reference to earlier work; the PDFs are main_text_anonymous.pdf and
supplementary_information_anonymous.pdf, and they are searched for identifying strings. The metadata of every PDF is
removed.

The two split documents read each other's labels through xr-hyper''')

sub('''def undefined_refs(work: Path, job: str) -> list[str]:''',
    '''# what must not be read in an anonymised manuscript (the reference list may name the author as any other author)
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

    rsub(r"\\\\author\\{.*?\\}(\\r?\\n)\\\\date\\{", "\\\\author{}\\n\\\\date{", "the author block", re.S)
    rsub(r"Our earlier work coupled a firm-level supply-chain model to national road and multimodal networks "
         r"(\\\\citep\\{colon2021,colon2022disruptsc\\})\\. Here we build it for a whole continental economy\\.",
         "Earlier work coupled a firm-level supply-chain model to national road and multimodal networks "
         "\\\\citep{colon2021,colon2022disruptsc}. Here such a model is built for a whole continental economy.",
         "the sentence on earlier work")
    rsub(r" at \\\\url\\{https://github\\.com/[^}]*\\}\\. The study scripts", "; the address of the repository is withheld for "
         "double-anonymized peer review and given to the editors. The study scripts", "the address of the code repository")
    rsub(r"\\\\section\\*\\{Funding\\}.*?(?=\\\\section\\*\\{Competing interests\\})", "", "the funding and author-contribution sections", re.S)
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
        text = "\\n".join(p.get_text() for p in d)
        meta = " ".join(str(v) for v in (d.metadata or {}).values() if v)
    return [w for w in IDENTIFYING if w in text or w in meta]


def undefined_refs(work: Path, job: str) -> list[str]:''')

sub('''    ap.add_argument("--tex", default=None)
    a = ap.parse_args()''',
    '''    ap.add_argument("--tex", default=None)
    ap.add_argument("--anonymous", action="store_true", help="the files for double-anonymised peer review (see the module's docstring)")
    a = ap.parse_args()''')

sub('''        shutil.copytree(ov, work, ignore=shutil.ignore_patterns(".git"))
        # SI first (its labels), then the main text (reads them), then the SI again (reads the main text's labels)
        for job in ("supplement", "maintext", "supplement", "main"):
            if not run_engine(engine, job, work, log):
                failures.append(f"{job}: the engine exited with an error (see build.log)")
        for job, name in (("maintext", "main_text.pdf"), ("supplement", "supplementary_information.pdf"), ("main", "combined.pdf")):
            pdf = work / f"{job}.pdf"
            if pdf.exists():
                shutil.copy2(pdf, out / name)
            else:
                failures.append(f"{job}.pdf not produced")''',
    '''        shutil.copytree(ov, work, ignore=shutil.ignore_patterns(".git"))
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
                failures.append(f"{job}.pdf not produced")''')

sub('''    (out / "build.log").write_text("\\n".join(log), encoding="utf-8")''',
    '''    (out / ("build_anonymous.log" if a.anonymous else "build.log")).write_text("\\n".join(log), encoding="utf-8")''')

sub('''        for name in ("main_text.pdf", "supplementary_information.pdf", "combined.pdf"):''',
    '''        for name in (("main_text_anonymous.pdf", "supplementary_information_anonymous.pdf") if a.anonymous else
                     ("main_text.pdf", "supplementary_information.pdf", "combined.pdf")):''')

P.write_bytes(s.replace("\n", nl).encode("utf-8"))
print("build_submission.py: --anonymous added, metadata stripped from every PDF")
