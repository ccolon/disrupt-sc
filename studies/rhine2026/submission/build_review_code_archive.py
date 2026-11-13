r"""Anonymised archive of the code, for double-anonymised peer review (13 November 2026).

    python studies/rhine2026/submission/build_review_code_archive.py --report          # what would identify the author
    python studies/rhine2026/submission/build_review_code_archive.py --out DIR         # write the archive and check it

Nature Communications asks for the code when a manuscript goes out to review. The public repository names its author,
so under double-anonymised review the reviewers get this archive instead: the model (src, tests, config, scripts) and
the scripts of the Rhine study, as text files only, with every string that identifies the author replaced by
"[anonymised]". It holds tracked files only (git ls-files), read from the working tree. Left out: the revision and
submission folders of the study (they are about the manuscript, not the model), figures and other binary files, the
documentation site, and the files over 2 MB. The archive is not meant to run from the paths it contains: local paths
are anonymised too.

After writing, the archive is read back and searched for the identifying patterns (RESIDUAL); any hit is a failure.
Citations of published work in the third person ("Colon et al.", the bibliography keys) are not identifying under the
journal's checklist and are left.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
NAME = "code_for_review_anonymous.zip"
ROOT_IN_ZIP = "code_for_review"

INCLUDE = ["src", "tests", "config", "scripts", "pyproject.toml", "LICENSE", "dsc-environment.yml", "MANIFEST.in",
           "studies/rhine2026"]
EXCLUDE_PREFIX = ("studies/rhine2026/review/", "studies/rhine2026/submission/", "studies/rhine2026/figures/",
                  "studies/rhine2026/evidence/",
                  # records of the operations on the computing cluster (accounts, volumes, restores): not code
                  "studies/rhine2026/cluster/batch_", "studies/rhine2026/cluster/cluster_inventory_",
                  "studies/rhine2026/cluster/cluster_space_", "studies/rhine2026/cluster/restore_",
                  "studies/rhine2026/cluster/space_free_")
TEXT_EXT = {".py", ".md", ".txt", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".json", ".csv", ".sh", ".in", ".tex",
            ".geojson", ".bib", ""}
MAX_BYTES = 2_000_000
MARK = "[anonymised]"

# what to look for in the report (wide on purpose: the report is read by a person)
DETECT = [
    ("first name", r"c[eé]lian"),
    ("surname", r"colon(?![a-z])"),
    ("institution", r"iiasa|laxenburg|polytechnique|applied systems analysis|\.ac\.at"),
    ("funding", r"oenb|futuregvc|jubil[aä]um"),
    ("e-mail", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z][A-Za-z.]+"),
    ("user path", r"users[/\\]+[A-Za-z0-9_.-]+|/home/[A-Za-z0-9_.-]+|onedrive"),
    ("repository", r"github\.com/[A-Za-z0-9_-]+|github\.io"),
    ("orcid", r"orcid|0000-000\d-\d{4}-\d{3}[\dX]"),
    ("overleaf", r"overleaf|[0-9a-f]{24}"),
]

# the replacements, in order (regex, replacement); case-insensitive unless the pattern says otherwise
REPLACE = [
    (r"https?://(www\.)?github\.com/ccolon[A-Za-z0-9_./#-]*", "[repository address withheld]"),
    (r"https?://ccolon\.github\.io[A-Za-z0-9_./#-]*", "[documentation address withheld]"),
    (r"github\.com/ccolon[A-Za-z0-9_./#-]*", "[repository address withheld]"),
    (r"ccolon\.github\.io[A-Za-z0-9_./#-]*", "[documentation address withheld]"),
    (r"[A-Za-z0-9._%+-]*c[eé]lian[A-Za-z0-9._%+-]*@[A-Za-z0-9-]+\.[A-Za-z][A-Za-z.]+", MARK),
    (r"[A-Za-z0-9._%+-]*colon[A-Za-z0-9._%+-]*@[A-Za-z0-9-]+\.[A-Za-z][A-Za-z.]+", MARK),
    (r"[A-Za-z0-9._%+-]+@iiasa\.ac\.at", MARK),
    (r"[A-Za-z]:[/\\]+Users[/\\]+[A-Za-z0-9_.-]+([/\\]+OneDrive)?", "[local folder]"),
    (r"/home/[A-Za-z0-9_.-]+", "/home/[user]"),
    (r"git-overleaf[/\\]+[0-9a-f]{24}", "git-overleaf/[project]"),
    (r"6aaa98617957ab816097822f", "[project]"),
    # the account name on the computing cluster
    (r"(-u\s+)colon\b", r"\1[user]"),
    (r"/user/colon\b", "/user/[user]"),
    (r"\|\s*colon\s*\|", "| [user] |"),
    (r"C[eé]lian\s+Colon", MARK),
    (r"Colon,?\s+C[eé]lian", MARK),
    (r"c[eé]lian", MARK),
    (r"ccolon", MARK),
    (r"International Institute for Applied Systems Analysis", MARK),
    (r"iiasa(\.ac\.at)?", MARK),
    (r"laxenburg", MARK),
    (r"polytechnique", MARK),
    (r"futuregvc", MARK),
    (r"oenb", MARK),
    (r"jubil[aä]umsfonds", MARK),
    (r"0000-000\d-\d{4}-\d{3}[\dX]", MARK),
]
REPLACE = [(re.compile(p, re.I), r) for p, r in REPLACE]

# what must not be left in the archive ("Colon" alone stays allowed only as a third-person citation, checked apart)
RESIDUAL = re.compile(
    r"c[eé]lian|ccolon|iiasa|laxenburg|polytechnique|futuregvc|oenb|jubil[aä]um|applied systems analysis"
    r"|users[/\\]+(?!\[)[A-Za-z0-9_.-]+|0000-000\d-\d{4}-\d{3}[\dX]|[0-9a-f]{24}(?=[/\\]+main\.tex)|6aaa98617957ab816097822f",
    re.I)
SURNAME = re.compile(r"colon(?![a-z])", re.I)
# a surname that is a citation of published work, a bibliography key, or the punctuation mark
SURNAME_OK = re.compile(
    r"colon\s+et\s+al|colon\s*\(?(19|20)\d\d|colon(19|20)\d\d\w*|colon,?\s+(c\.|hallegatte|and\s)|colon\s*&"
    r"|(semi|a|the|with|after|before|trailing|leading|double|by|one|no|per)[ -]?colon|colon[- ](separated|delimited)"
    r"|colon\s+(character|sign|after|before|in |is |as |separat|delimit)|\bcolons\b", re.I)

README = """# Code for review (anonymised)

This archive holds the code of the manuscript under double-anonymised peer review: the supply-chain model
(`src`, with its tests, default parameters in `config` and helper scripts) and the scripts of the study
(`studies/rhine2026`: scenario driver, batch job lists, calibration and mechanism checks, analysis and figure
scripts, and the generators of the manuscript's numbers and tables).

It is a copy of the public repository named in the cover letter, in which every string that identifies the
authors was replaced by `[anonymised]`, including local folder names; some scripts therefore need their paths
set before they run. Text files only: figures, documents and the files over 2 MB are left out, and so are the
folders of the study that concern the manuscript's revision and submission.

The model is open source under the GPL-3.0 license (file `LICENSE`). The input data of the European scope
(transport network, agents, tables and scenario files) are too large for this archive; they are available
through the editors during review and will be deposited with a DOI upon acceptance.

Files: {n_files}; replaced strings: {n_repl}.
"""


def tracked() -> list[str]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "--", *INCLUDE], capture_output=True, check=True).stdout
    files = [f for f in out.decode("utf-8").split("\0") if f]
    keep = []
    for f in files:
        if f.startswith(EXCLUDE_PREFIX) or f == "README.md":
            continue
        p = REPO / f
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT or p.stat().st_size > MAX_BYTES:
            continue
        keep.append(f)
    return keep


def read_text(p: Path) -> str | None:
    raw = p.read_bytes()
    if b"\0" in raw[:8000]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def scrub(text: str) -> tuple[str, int]:
    n = 0
    for rx, rep in REPLACE:
        text, k = rx.subn(rep, text)
        n += k
    return text, n


def surname_problems(text: str) -> list[str]:
    bad = []
    for line in text.splitlines():
        for m in SURNAME.finditer(line):
            ctx = line[max(0, m.start() - 12): m.end() + 22]
            if not SURNAME_OK.search(ctx):
                bad.append(line.strip()[:160])
                break
    return bad


def report(files: list[str], out: Path | None) -> None:
    lines = []
    for label, pat in DETECT:
        rx = re.compile(pat, re.I)
        found: Counter = Counter()
        where = defaultdict(set)
        for f in files:
            text = read_text(REPO / f)
            if text is None:
                continue
            for m in rx.finditer(text):
                s = text[max(0, m.start() - 25): m.end() + 25].replace("\n", " ")
                key = m.group(0) if label not in ("surname",) else s
                found[key] += 1
                where[key].add(f)
        lines.append(f"## {label}: {sum(found.values())} matches, {len(found)} distinct")
        for key, k in found.most_common(60):
            fs = sorted(where[key])
            lines.append(f"  {k:5d}  {key!r}  in {len(fs)} file(s), e.g. {fs[0]}")
    text = "\n".join(lines)
    if out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "code_archive_report.txt").write_text(text, encoding="utf-8")
        print(f"report written to {out / 'code_archive_report.txt'} ({len(lines)} lines)")
    else:
        sys.stdout.buffer.write(text.encode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    files = tracked()
    out = Path(a.out) if a.out else None
    if a.report:
        report(files, out)
        return
    assert out, "--out DIR"
    out.mkdir(parents=True, exist_ok=True)
    target = out / NAME
    n_repl, skipped, problems = 0, [], []
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        written = 0
        for f in files:
            text = read_text(REPO / f)
            if text is None:
                skipped.append(f)
                continue
            if RESIDUAL.search(f) or SURNAME.search(f):
                problems.append(f"file name: {f}")
                continue
            new, k = scrub(text)
            n_repl += k
            info = zipfile.ZipInfo(f"{ROOT_IN_ZIP}/{f}", date_time=(2026, 11, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, new.encode("utf-8"))
            written += 1
        info = zipfile.ZipInfo(f"{ROOT_IN_ZIP}/README_FOR_REVIEWERS.md", date_time=(2026, 11, 13, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, README.format(n_files=written, n_repl=n_repl).encode("utf-8"))
    # read the archive back and search it
    with zipfile.ZipFile(target) as z:
        for name in z.namelist():
            text = z.read(name).decode("utf-8")
            for m in RESIDUAL.finditer(text):
                problems.append(f"{name}: {text[max(0, m.start() - 30): m.end() + 30]!r}")
            for line in surname_problems(text):
                problems.append(f"{name}: surname outside a citation: {line!r}")
    size = target.stat().st_size
    log = [f"{written} files, {n_repl} strings replaced, {size / 1e6:.2f} MB, {len(skipped)} binary files skipped",
           *[f"PROBLEM {p}" for p in problems]]
    (out / "code_archive_build.log").write_text("\n".join(log), encoding="utf-8")
    print(log[0])
    print(f"problems: {len(problems)} (see {out / 'code_archive_build.log'})" if problems else "no identifying string left")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
