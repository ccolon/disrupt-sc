r"""Pre-submission gate of the Rhine 2026 manuscript (5 Nov 2026): the checks a copy must pass before it is pushed to
Overleaf or submitted. Every number the paper states either comes from numbers.tex (written by make_numbers.py from the
batch) or is listed in the ledger with the reason it may stay a literal; every verbal quantity that paraphrases a model
result ('two fifths', 'nearly three times', 'one in twenty-five') is bound in the ledger to the macros it paraphrases and
to a range. A batch that moves a macro out of the range, a sentence rewritten under a ledger entry, or a new hard-coded
number fails the gate instead of going stale in the text.

Checks, each PASS / WARN / FAIL / NOT RUN (exit code 1 when any check FAILS):
  static   lint_manuscript.py: citation keys, inputs, figures, braces, math, escapes, labels, table cells
  pdflatex non-ASCII characters outside what pdfLaTeX reads with inputenc utf8 + T1 (Latin-1, dashes, quotes, euro):
           Overleaf compiles with pdfLaTeX, the local compile with tectonic (XeTeX), which accepts any Unicode (FAIL)
  macros   numbers.tex: duplicate definitions, empty or nan values, uppercase commands used in the text and defined
           nowhere (FAIL); macros of numbers.tex never used (WARN)
  bare     digits in the prose of main.tex and si.tex (the generated-table blocks are checked by --regen) that are not
           a year, a calendar date, inside a citation, reference or layout argument, or covered by a ledger entry (FAIL)
  words    fraction and multiple words (half, two fifths, nearly three times, one in twenty-five, fourfold) not covered by
           a ledger entry (FAIL); number words (eleven, fourteen) not covered (WARN)
  ledger   entries whose text no longer occurs in the manuscript, claims whose expression left its range or names an
           unknown macro (FAIL)
  pending  known findings recorded in the ledger with their proposed fix (FAIL while the text is there; WARN once the
           text is gone: remove the entry)
  refs     refs.bib: duplicate keys (FAIL); entries never cited, entries with neither DOI nor URL (WARN)
  fresh    (--regen) make_numbers.py and si_tables.py rerun into a temporary folder with the tag and list date of the
           numbers.tex header: any macro or table that differs from the Overleaf copy FAILS (the copy is behind the batch
           or was edited by hand); needs the run folders under C:/dsc_runs/rhine2026
  compile  --tex, else latexmk / tectonic / pdflatex on PATH (tectonic 0.17 in ~/.local/bin since 5 Nov 2026; its
           package cache is filled, a compile takes ~1 min): LaTeX errors, undefined citations and references, no PDF
           FAIL; overfull boxes WARN; --pdf keeps the PDF. Tectonic is XeTeX, Overleaf pdfLaTeX: see 'pdflatex'

Ledger (the folder paper_gate_ledger/ next to this script, one YAML per manuscript file, read together):
  ignore:  regexes blanked before the scans (units and fixed expressions: 'of a quarter', 'third-quarter')
  allowed: {file, text, why}: a snippet of the comment-stripped LaTeX source; every number and number word inside
           any occurrence of the snippet is accepted. 'why' says what kind of literal it is: evidence (an external
           figure with its citation), design (a setting of the experiment), data (a fact of the inputs), count (a
           description of the paper itself)
  claims:  {file, text, expr, range, why}: a verbal quantity; expr is a Python expression over the macro values of
           numbers.tex (EnsMean, 100*IndQ/DEUlossQ), range the inclusive [low, high] the words stay true for
  pending: {file, text, note}: a model output written as a literal, with the fix (the macro to use or to add); it keeps
           failing until the text changes, without repeating its numbers under 'bare'
Snippets match the raw LaTeX of the file with comments stripped (\, and ~ included), anywhere in the file; keep them
short enough to survive unrelated edits and long enough to be unique in meaning.

Usage:
    python studies/rhine2026/paper_gate.py [--repo <overleaf checkout>] [--ledger <folder or yaml>] [--regen]
                                           [--report <md>] [--no-compile] [--tex <engine>] [--pdf <out.pdf>]
Self-test of the failure modes: studies/rhine2026/paper_gate_selftest.py.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # si_tables.compare_table (10 Nov 2026)

import yaml

HERE = Path(__file__).resolve().parent
REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
LEDGER = HERE / "paper_gate_ledger"         # one YAML per manuscript file (common.yaml, main.yaml, si.yaml)
sys.path.insert(0, str(HERE))

MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December")
NUMBER = re.compile(r"(?<![A-Za-z0-9\\])\d+(?:(?:\{,\}|[.,])\d+)*")
# a day before its month, also inside a range or a list ('29 July--4 August', '14, 21 and 28 September', '2 and 3 November')
DATE_AFTER = re.compile(r"(?:\s*--\s*\d{1,2}|,\s*\d{1,2})*(?:,?\s+(?:and|or|to)\s+\d{1,2})?(?:\s|~|\\,)+(?:" + MONTHS + r")\b")
# Dates are accepted without a check: a date that is a model output (the peak week) must be a pending or claim entry.
DATE_BEFORE = re.compile(r"\b(?:" + MONTHS + r")(?:\s|~)+$")
# fractions and multiples: paraphrases of a result, FAIL when no ledger entry covers them
FRACTION_WORDS = re.compile(
    r"\b(?:(?:one|two|three|four|five|seven|nine)[- ]+)?(?:half|halves|halved|halve|halving|thirds?|quarters?|fifths?|sixths?|"
    r"eighths?|tenths?)\b|\b(?:twice|double[sd]?|doubling|triple[sd]?|tripling|\w+fold)\b|"
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|twenty|a hundred)(?:\s|~)+times\b|"
    r"\bone in (?:(?:twenty|thirty|forty|fifty)[- ])?(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"fifteen|twenty|thirty|forty|fifty|a hundred|a thousand)\b",
    re.IGNORECASE)
NUMBER_WORDS = re.compile(
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|dozen)\b", re.IGNORECASE)
# layout and reference arguments whose digits are not statements (blanked, offsets kept)
LAYOUT = [
    r"\\(?:setcounter|addtocounter)\{[^}]*\}\{[^}]*\}",
    r"\\(?:cite[a-zA-Z]*|ref|eqref|autoref|cref|Cref|pageref|label|input|include|url|href|bibliography|bibliographystyle|"
    r"usepackage|documentclass|setcounter|addtocounter|texttt)\*?(?:\[[^\]]*\])*\{[^}]*\}",
    r"\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}",
    r"\\\\\[[^\]]*\]",
    r"\\(?:vspace|hspace|vskip|hskip)\*?\{[^}]*\}",
    r"\\setlength\{[^}]*\}\{[^}]*\}",
    r"\\begin\{(?:tabular\*?|longtable|tabularx)\}(?:\{[^{}]*\})?\{(?:[^{}]|\{[^{}]*\})*\}",
    r"\\begin\{[a-z*]+\}\[[^\]]*\]",
    r"\\(?:re)?newcommand\{?\\\w+\}?(?:\[\d\])?\{.*$",
    r"-?[\d.]+(?:pt|mm|em|ex)\b",
    r"[\d.]+\\(?:textwidth|linewidth|columnwidth|textheight)",
    r"\\(?:arabic|Alph|alph|roman|Roman)\{[^}]*\}",
    r"\b[a-z]+!\d+(?:![a-z]+)?\b",                     # xcolor mixes: orange!80!black
    r"\b[A-Z]\d+(?:--\d+)+",                            # sector-code ranges: C10--12 (the codes themselves are skipped)
    r"TEN-T",                                           # the network's name, not the number word 'ten'
]
BUILTIN = {"LaTeX", "TeX", "Large", "LARGE", "Huge", "Big", "Bigl", "Bigr", "Delta", "Gamma", "Lambda", "Omega", "Phi",
           "Pi", "Psi", "Sigma", "Theta", "Xi", "Upsilon", "S", "P", "AA", "AE", "OE", "O", "L"}


@dataclass
class Check:
    name: str
    status: str = "PASS"            # PASS / WARN / FAIL / NOT RUN
    lines: list = field(default_factory=list)

    def fail(self, msg):
        self.status = "FAIL"; self.lines.append(f"FAIL  {msg}")

    def warn(self, msg):
        if self.status == "PASS":
            self.status = "WARN"
        self.lines.append(f"warn  {msg}")

    def info(self, msg):
        self.lines.append(f"      {msg}")


def blank(text: str, pattern: str, flags=re.MULTILINE) -> str:
    """Replace every match by spaces of the same length (newlines kept): offsets and line numbers survive."""
    return re.sub(pattern, lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=flags)


def strip_comments(text: str) -> str:
    return blank(text, r"(?<!\\)%.*$")


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def context(text: str, start: int, end: int, width: int = 55) -> str:
    a, b = max(0, start - width), min(len(text), end + width)
    s = text[a:start] + "[[" + text[start:end] + "]]" + text[end:b]
    return re.sub(r"\s+", " ", s).strip()


def parse_numbers(path: Path):
    """numbers.tex -> ({name: value string}, [duplicate names])."""
    vals, dups = {}, []
    pat = re.compile(r"^\\newcommand\{\\(\w+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", re.MULTILINE)
    for m in pat.finditer(path.read_text(encoding="utf-8")):
        if m.group(1) in vals:
            dups.append(m.group(1))
        vals[m.group(1)] = m.group(2)
    return vals, dups


WORD_VALUES = {"none": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
               "nine": 9, "ten": 10, "eleven": 11}


def numeric(v: str):
    s = v.replace("{,}", "").replace("$-$", "-").replace(",", "").strip()
    if s in WORD_VALUES:
        return float(WORD_VALUES[s])
    try:
        return float(s)
    except ValueError:
        return None                 # ranges ('13--33') and text stay out of the expressions


GEN_BLOCK = re.compile(r"^% >>> generated table (\S+)\b[^\n]*\n.*?^% <<< generated table \1[ \t]*$", re.MULTILINE | re.DOTALL)


def blank_generated(raw: str) -> str:
    """6 Nov 2026 (the author's review: the SI in one file): si_tables.py writes the generated tables into the documents
    between '% >>> generated table <name> ...' and '% <<< generated table <name>' markers. Those blocks are checked
    against the regenerated tables by --regen, not by the prose scans: blanked here, line count kept."""
    def sub(m):
        block = m.group(0)
        out = re.sub(r"[^\n]", " ", block)
        i = block.find("\\caption{")      # 10 Nov 2026: the caption is the author's prose and is read by the scans
        if i >= 0:
            k, depth = i + 9, 1
            while k < len(block) and depth:
                if block[k] == "\\":
                    k += 2
                    continue
                depth += (block[k] == "{") - (block[k] == "}")
                k += 1
            out = out[:i] + block[i:k] + out[k:]
        return out
    return GEN_BLOCK.sub(sub, raw)


def generated_block(raw: str, name: str) -> str | None:
    """The lines between the markers of the generated table <name> in a document, or None."""
    m = re.search(r"^% >>> generated table " + re.escape(name) + r"\b[^\n]*\n(.*?)^% <<< generated table " + re.escape(name) + r"[ \t]*$",
                  raw, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def documents(repo: Path):
    """The prose files the scans read: main.tex from \\begin{document}, si.tex at the root (sections/*.tex before 10 Nov 2026), the generated-table blocks blanked."""
    out = {}
    for p in [repo / "main.tex"] + [q for q in [repo / "si.tex"] if q.exists()] + sorted((repo / "sections").glob("*.tex")):
        raw = blank_generated(p.read_text(encoding="utf-8"))
        t = strip_comments(raw)
        i = t.find("\\begin{document}")
        if i >= 0:
            t = re.sub(r"[^\n]", " ", t[:i]) + t[i:]
        out[p.relative_to(repo).as_posix()] = t
    return out


def load_ledger(path: Path) -> dict:
    """One YAML file, or every *.yaml of a folder (lists concatenated): one ledger file per manuscript file."""
    files = sorted(path.glob("*.yaml")) if path.is_dir() else ([path] if path.exists() else [])
    out = {"ignore": [], "allowed": [], "claims": [], "pending": []}
    for p in files:
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for k in out:
            out[k] += d.get(k) or []
    return out


def coverage(docs: dict, ledger: dict, values: dict, ck_ledger: Check, ck_pending: Check):
    """Spans covered by the ledger per file; claims evaluated against the macro values; pending entries reported."""
    spans = {f: [] for f in docs}
    env = {k: v for k, v in ((k, numeric(s)) for k, s in values.items()) if v is not None}
    for kind in ("allowed", "claims", "pending"):
        for e in ledger.get(kind) or []:
            f, snip = e.get("file"), e.get("text", "")
            if f not in docs:
                ck_ledger.fail(f"{kind}: file {f!r} not in the manuscript (entry {snip[:60]!r})"); continue
            hits = [m.start() for m in re.finditer(re.escape(snip), docs[f])]
            if not hits:
                if kind == "pending":
                    ck_pending.warn(f"pending entry no longer in {f} (fixed? remove it from the ledger): {snip!r}")
                else:
                    ck_ledger.fail(f"{kind}: text no longer in {f} (rewritten? re-check the numbers and update the entry): {snip!r}")
                continue
            if kind == "pending":
                ck_pending.fail(f"{f}:{line_of(docs[f], hits[0])}  {e.get('note', '')}  | {snip}")
                spans[f] += [(h, h + len(snip)) for h in hits]
                continue
            ok = True
            if kind == "claims":
                try:
                    val = eval(e["expr"], {"__builtins__": {}, "min": min, "max": max, "abs": abs}, dict(env))  # noqa: S307
                except NameError as err:
                    ck_ledger.fail(f"claim {snip!r}: {err} (macro missing from numbers.tex or not numeric)"); ok = False
                else:
                    lo, hi = e["range"]
                    if not (lo <= val <= hi):
                        # reported here once; its span stays covered so the words scan does not report it again
                        ck_ledger.fail(f"claim {snip!r} in {f}:{line_of(docs[f], hits[0])}: {e['expr']} = {val:.4g}, "
                                       f"outside [{lo}, {hi}] the words are true for: rewrite the words or the range")
                    else:
                        ck_ledger.info(f"claim ok: {snip[:100]!r}: {e['expr']} = {val:.4g} in [{lo}, {hi}]")
            if ok:
                spans[f] += [(h, h + len(snip)) for h in hits]
    return spans


def covered(spans, a, b):
    return any(s <= a and b <= e for s, e in spans)


def macro_hint(tok: str, values: dict, used: set) -> str:
    """The macros whose value equals a hard-coded number (unused macros first): the likely source of the literal."""
    v = numeric(tok)
    if v is None:
        return ""
    hits = [k for k, s in values.items() if numeric(s) is not None and abs(abs(numeric(s)) - v) < 1e-9]
    hits.sort(key=lambda k: (k in used, k))
    names = ", ".join(chr(92) + k + ("" if k in used else " (unused)") for k in hits[:4]) + (" ..." if len(hits) > 4 else "")
    return f"  [= {names}]" if hits else ""


def scan_bare(docs, spans, ignore, ck: Check, values: dict, used: set):
    n_ok = {"year": 0, "date": 0, "ledger": 0}
    for f, t in docs.items():
        s = t
        for pat in LAYOUT + list(ignore):
            s = blank(s, pat)
        for m in NUMBER.finditer(s):
            tok, a, b = m.group(0), m.start(), m.end()
            if re.fullmatch(r"(?:19|20)\d\d", tok):
                n_ok["year"] += 1; continue
            if tok.isdigit() and 1 <= int(tok) <= 31 and (DATE_AFTER.match(s, b) or DATE_BEFORE.search(s[max(0, a - 12):a])):
                n_ok["date"] += 1; continue
            if covered(spans[f], a, b):
                n_ok["ledger"] += 1; continue
            ck.fail(f"{f}:{line_of(t, a)}  {tok}  | {context(t, a, b)}{macro_hint(tok, values, used)}")
    ck.info(f"accepted: {n_ok['year']} years, {n_ok['date']} calendar dates, {n_ok['ledger']} numbers under ledger entries")


def scan_words(docs, spans, ignore, ck: Check):
    n_ok = 0
    for f, t in docs.items():
        s = t
        for pat in LAYOUT + list(ignore):
            s = blank(s, pat)
        taken = []
        for m in FRACTION_WORDS.finditer(s):
            taken.append((m.start(), m.end()))
            if covered(spans[f], m.start(), m.end()):
                n_ok += 1; continue
            ck.fail(f"{f}:{line_of(t, m.start())}  '{m.group(0)}'  | {context(t, m.start(), m.end())}")
        for m in NUMBER_WORDS.finditer(s):
            if any(a <= m.start() < b for a, b in taken):
                continue
            if covered(spans[f], m.start(), m.end()):
                n_ok += 1; continue
            ck.warn(f"{f}:{line_of(t, m.start())}  '{m.group(0)}'  | {context(t, m.start(), m.end())}")
    ck.info(f"accepted under ledger entries: {n_ok}")


def check_macros(repo, docs, values, dups, ck: Check):
    for d in dups:
        ck.fail(f"numbers.tex defines \\{d} twice")
    for k, v in values.items():
        if not v.strip() or "nan" in v.lower():
            ck.fail(f"\\{k} has the value {v!r}")
    alltext = "\n".join(docs.values()) + "\n" + "\n".join(
        strip_comments(p.read_text(encoding="utf-8")) for p in sorted((repo / "tables").glob("*.tex")))
    pre = strip_comments((repo / "main.tex").read_text(encoding="utf-8"))
    defined = set(values) | set(re.findall(r"\\(?:re)?newcommand\{?\\(\w+)\}?", pre)) | set(re.findall(r"\\(?:re)?newcommand\{?\\(\w+)\}?", alltext))
    used = set(re.findall(r"\\([A-Za-z]+)", alltext))
    for u in sorted(u for u in used - defined - BUILTIN if u[0].isupper()):
        ck.fail(f"\\{u} is used but defined nowhere")
    unused = sorted(set(values) - used)
    if unused:
        ck.warn(f"{len(unused)} of {len(values)} macros of numbers.tex are never used: {', '.join(unused)}")
    ck.info(f"{len(values)} macros defined, {len(set(values) & used)} used")
    return used


def check_refs(repo, docs, ck: Check):
    bib = (repo / "refs.bib").read_text(encoding="utf-8")
    entries = re.split(r"(?=^@\w+\s*\{)", bib, flags=re.MULTILINE)
    keys, seen = {}, set()
    for e in entries:
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", e)
        if not m or m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        k = m.group(2)
        if k in seen:
            ck.fail(f"refs.bib: key {k} defined twice")
        seen.add(k)
        keys[k] = bool(re.search(r"^\s*(doi|url)\s*=", e, re.MULTILINE | re.IGNORECASE))
    # 10 Nov 2026: the tables are blocks of the documents, blanked in `docs`; their cells cite too (the evidence columns),
    # so the scan for citations reads the files whole
    text = "\n".join(strip_comments((repo / name).read_text(encoding="utf-8")) for name in docs) + "\n".join(
        strip_comments(p.read_text(encoding="utf-8")) for p in sorted((repo / "tables").glob("*.tex")))
    cited = set()
    for c in re.findall(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", text):
        cited |= {k.strip() for k in c.split(",") if k.strip()}
    for k in sorted(set(keys) - cited):
        ck.warn(f"refs.bib: {k} is never cited")
    nolink = sorted(k for k in cited & set(keys) if not keys[k])
    if nolink:
        ck.warn(f"{len(nolink)} cited entries have neither DOI nor URL (cannot be verified online): {', '.join(nolink)}")
    ck.info(f"{len(keys)} entries, {len(cited)} cited")


def check_static(repo, ck: Check):
    import lint_manuscript
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        problems = lint_manuscript.main(repo)
    for p in problems:
        ck.fail(p)


def check_fresh(repo, values, ck: Check):
    head = (repo / "numbers.tex").read_text(encoding="utf-8")[:600]
    m = re.search(r"from the batch of (\d{8}) \(run names (\w+)\)", head)
    if not m:
        ck.fail("numbers.tex header names no batch ('from the batch of <date> (run names <tag>)')"); return
    lists, tag = m.groups()
    ck.info(f"regenerating with --tag {tag} --lists {lists}")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for script in ("make_numbers.py", "si_tables.py"):
            r = subprocess.run([sys.executable, str(HERE / script), "--tag", tag, "--lists", lists, "--overleaf", str(tmp)],
                               capture_output=True, text=True, cwd=HERE.parents[1], timeout=3600)
            if r.returncode:
                ck.fail(f"{script} failed: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}"); return
            for line in r.stdout.splitlines():
                if "skipped" in line:
                    ck.warn(f"{script}: {line.strip()}")
        new, _ = parse_numbers(tmp / "numbers.tex")
        for k in sorted(set(values) | set(new)):
            if values.get(k) != new.get(k):
                ck.fail(f"\\{k}: Overleaf {values.get(k)!r}, batch {new.get(k)!r}")
        # a table lives either in a generated-table block of a document (6 Nov 2026, the SI in one file) or in tables/
        docs_raw = {q: q.read_text(encoding="utf-8") for q in [repo / "main.tex"] + [q for q in [repo / "si.tex"] if q.exists()] + sorted((repo / "sections").glob("*.tex"))}
        for p in sorted((tmp / "tables").glob("*.tex")):
            b = p.read_text(encoding="utf-8").splitlines()
            a, where = None, f"tables/{p.name}"
            for q, raw in docs_raw.items():
                block = generated_block(raw, p.stem)
                if block is not None:
                    a, where = block.splitlines(), f"{q.relative_to(repo).as_posix()}, block '{p.stem}'"
                    break
            if a is None:
                old = repo / "tables" / p.name
                a = old.read_text(encoding="utf-8").splitlines() if old.exists() else []
            if where != f"tables/{p.name}":      # 10 Nov 2026: a block keeps the author's text; its numbers are compared
                import si_tables
                problems, changes, _ = si_tables.compare_table(p.stem, "\n".join(b), "\n".join(a))
                for msg in problems + changes:
                    ck.fail(f"{where}: {msg}")
                continue
            if a != b:
                i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                ck.fail(f"{where} differs from the regenerated table from line {i + 1}: "
                        f"{(a[i] if i < len(a) else '<end>')[:80]!r} vs {(b[i] if i < len(b) else '<end>')[:80]!r}")
        ck.info(f"{len(new)} macros and {len(list((tmp / 'tables').glob('*.tex')))} tables regenerated")


def find_engine(tex: str | None):
    """--tex path, else latexmk / tectonic / pdflatex on PATH, else ~/.local/bin/tectonic.exe (where tectonic lives
    since 5 Nov 2026: that folder is on the user PATH, but a process started with another environment may miss it)."""
    if tex:
        return Path(tex)
    for e in ("latexmk", "tectonic", "pdflatex"):
        if shutil.which(e):
            return Path(shutil.which(e))
    home = Path.home() / ".local" / "bin" / "tectonic.exe"
    return home if home.exists() else None


# characters pdfLaTeX reads with inputenc utf8 + fontenc T1 (+ the TS1 symbols of the kernel): Latin-1, the dashes,
# curly quotes, ellipsis and the euro sign. Tectonic (XeTeX) accepts any Unicode character, Overleaf's pdfLaTeX does not
# ('Unicode character ≈ not set up for use with LaTeX'), so a clean tectonic build does not clear these.
PDFLATEX_SAFE = set(chr(c) for c in range(0xA0, 0x100)) | set("–—‘’“”…€")


def check_pdflatex(repo: Path, ck: Check):
    files = [repo / "main.tex", repo / "numbers.tex", repo / "refs.bib"] + [q for q in [repo / "si.tex"] if q.exists()] + sorted((repo / "sections").glob("*.tex")) \
        + sorted((repo / "tables").glob("*.tex"))
    seen = {}
    for p in files:
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for ch in line:
                if ord(ch) > 127:
                    seen.setdefault(ch, []).append(f"{p.relative_to(repo).as_posix()}:{i}")
    import unicodedata
    for ch, where in sorted(seen.items()):
        name = unicodedata.name(ch, "?")
        if ch in PDFLATEX_SAFE:
            ck.info(f"U+{ord(ch):04X} {ch} {name}: {len(where)}x (pdfLaTeX T1: fine)")
        else:
            ck.fail(f"U+{ord(ch):04X} {ch} {name}: {len(where)}x, first {where[0]}: pdfLaTeX on Overleaf will stop "
                    f"('not set up for use with LaTeX'); write it as a LaTeX command")


def check_compile(repo, ck: Check, tex: str | None = None, pdf_out: Path | None = None):
    engine = find_engine(tex)
    if engine is None:
        ck.status = "NOT RUN"
        ck.info("no TeX engine (--tex, latexmk/tectonic/pdflatex on PATH, ~/tectonic.exe): the copy has not been compiled")
        return
    kind = next(k for k in ("latexmk", "tectonic", "pdflatex") if k in engine.name.lower())
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "paper"
        shutil.copytree(repo, work, ignore=shutil.ignore_patterns(".git"))
        e = str(engine)
        # tectonic from its local package cache first (16 s on 5 Nov 2026; online it waited ~12 min on the bundle
        # server), online only when a package is missing from the cache
        cmds = {"latexmk": [[e, "-pdf", "-interaction=nonstopmode", "main.tex"]],
                "tectonic": [[e, "--only-cached", "--keep-logs", "--keep-intermediates", "main.tex"]],
                "pdflatex": [[e, "-interaction=nonstopmode", "main.tex"], ["bibtex", "main"],
                             [e, "-interaction=nonstopmode", "main.tex"], [e, "-interaction=nonstopmode", "main.tex"]]}[kind]
        errs = ""
        for c in cmds:
            r = subprocess.run(c, cwd=work, capture_output=True, text=True, timeout=1800)
            if r.returncode and kind == "tectonic":
                ck.info("tectonic --only-cached failed (a package missing from the cache?): retrying online")
                r = subprocess.run([x for x in c if x != "--only-cached"], cwd=work, capture_output=True, text=True, timeout=1800)
            errs += (r.stderr or "") + (r.stdout or "")
            if r.returncode:
                tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
                ck.fail(f"{Path(c[0]).name} exited {r.returncode}: {' / '.join(tail)}")
        # duplicate hyperref anchors: the SI resets the figure/table counters, so 'figure.4' names Fig. 4 and Fig. S4
        # and a link to one may land on the other (5 Nov 2026); fix: \renewcommand{\theHfigure}{S\arabic{figure}}
        dup = sorted(set(re.findall(r"Object @([\w.]+) already defined", errs))
                     | set(re.findall(r"destination with the same identifier \(name\{([^}]+)\}\)", errs)))
        if dup:
            ck.warn(f"{len(dup)} duplicate PDF anchors ({', '.join(dup[:6])}{' ...' if len(dup) > 6 else ''}): links may jump "
                    "to the wrong figure/table; after the SI counter reset add \\renewcommand{\\theHfigure}{S\\arabic{figure}} "
                    "(and \\theHtable)")
        if pdf_out and (work / "main.pdf").exists():
            shutil.copy2(work / "main.pdf", pdf_out)
        log = work / "main.log"
        if not log.exists():
            ck.fail(f"{engine} wrote no main.log"); return
        txt = log.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"^! .*$", txt, re.MULTILINE):
            ck.fail(f"LaTeX error: {m.group(0)}")
        for m in sorted(set(re.findall(r"(Citation|Reference) `([^']+)' .*undefined", txt))):
            ck.fail(f"undefined {m[0].lower()}: {m[1]}")
        n_over = len(re.findall(r"^Overfull \\hbox", txt, re.MULTILINE))
        if n_over:
            ck.warn(f"{n_over} overfull hboxes")
        if not (work / "main.pdf").exists():
            ck.fail("no main.pdf written")
        ck.info(f"compiled with {engine}; pdf {'written' if (work / 'main.pdf').exists() else 'MISSING'}"
                + (f", copied to {pdf_out}" if pdf_out and (work / 'main.pdf').exists() else ""))


def main(repo: Path, ledger_path: Path, regen: bool, report: Path | None, tex: str | None = None, pdf_out: Path | None = None,
         compile_: bool = True):
    ledger = load_ledger(ledger_path)
    values, dups = parse_numbers(repo / "numbers.tex")
    docs = documents(repo)
    checks = {n: Check(n) for n in ("static", "pdflatex", "macros", "ledger", "pending", "bare", "words", "refs", "fresh",
                                    "compile")}
    check_static(repo, checks["static"])
    check_pdflatex(repo, checks["pdflatex"])
    used = check_macros(repo, docs, values, dups, checks["macros"])
    spans = coverage(docs, ledger, values, checks["ledger"], checks["pending"])
    ignore = ledger.get("ignore") or []
    scan_bare(docs, spans, ignore, checks["bare"], values, used)
    scan_words(docs, spans, ignore, checks["words"])
    check_refs(repo, docs, checks["refs"])
    if regen:
        check_fresh(repo, values, checks["fresh"])
    else:
        checks["fresh"].status = "NOT RUN"; checks["fresh"].info("rerun with --regen (needs the run folders)")
    if compile_:
        check_compile(repo, checks["compile"], tex, pdf_out)
    else:
        checks["compile"].status = "NOT RUN"; checks["compile"].info("--no-compile")
    head = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h %cd", "--date=short"], capture_output=True, text=True).stdout.strip()
    out = [f"# Paper gate: {repo.name} at {head}", ""]
    out += [f"| check | status | findings |", "|---|---|---|"]
    for c in checks.values():
        n = sum(1 for line in c.lines if not line.startswith("      "))
        out.append(f"| {c.name} | {c.status} | {n} |")
    for c in checks.values():
        if c.lines:
            out += ["", f"## {c.name}: {c.status}", ""] + [f"    {line}" for line in c.lines]
    verdict = "FAIL" if any(c.status == "FAIL" for c in checks.values()) else "PASS"
    not_run = [c.name for c in checks.values() if c.status == "NOT RUN"]
    out += ["", f"VERDICT: {verdict}" + (f" (not run: {', '.join(not_run)})" if not_run else "")]
    text = "\n".join(out)
    if report:
        report.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    # the report quotes the manuscript (accents, and the characters the pdflatex check flags): a Windows console or pipe
    # in cp1252 would raise on them (5 Nov 2026)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--regen", action="store_true", help="rerun make_numbers.py and si_tables.py into a temporary folder and diff")
    ap.add_argument("--report", default=None, help="also write the report to this markdown file")
    ap.add_argument("--tex", default=None, help="TeX engine (latexmk, tectonic or pdflatex executable); default: PATH, then ~/tectonic.exe")
    ap.add_argument("--pdf", default=None, help="copy the compiled main.pdf here")
    ap.add_argument("--no-compile", action="store_true", help="skip the compile (seconds instead of a minute; for ledger work)")
    a = ap.parse_args()
    sys.exit(main(Path(a.repo), Path(a.ledger), a.regen, Path(a.report) if a.report else None, a.tex,
                  Path(a.pdf) if a.pdf else None, not a.no_compile))
