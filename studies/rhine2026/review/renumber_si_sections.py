r"""List, or shift, the hard-coded numbers of the SI sections in main.tex and si.tex of the Overleaf copy. The sections
are numbered by hand ('\subsection*{S7 ...}', 'Supplementary Section~S7', 'Sections~S7 to S9'), so removing a section
means renumbering the ones after it everywhere. Written for 12 November 2026, when Section S6 left the SI.

    python studies/rhine2026/review/renumber_si_sections.py                  # lists every 'S<n>' that names a section
    python studies/rhine2026/review/renumber_si_sections.py --shift 7 -1     # S7 and above become one less

A token counts as a section number when it follows 'Section', 'Sections', a connective inside such a list ('and', 'to',
a comma) or opens a '\subsection*{'. Figure and table numbers ('Fig.~S3'), file names (S1_network_firms) and anything
else are left alone and listed as 'not a section' so that they can be read.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF  # noqa: E402

TOKEN = re.compile(r"(?<![A-Za-z0-9_/.])S(\d{1,2})(?![A-Za-z0-9_])")
SECTION_BEFORE = re.compile(r"(?:Sections?[~ ]|\\subsection\*\{|Sections?[~ ]S\d{1,2}(?:, S\d{1,2})* (?:and|to) |Sections?[~ ]S\d{1,2}, )$")


def scan(text: str):
    for m in TOKEN.finditer(text):
        before = text[max(0, m.start() - 40):m.start()]
        yield m, bool(SECTION_BEFORE.search(before))


def main(argv):
    shift = None
    if "--shift" in argv:
        i = argv.index("--shift")
        shift = (int(argv[i + 1]), int(argv[i + 2]))
    total = 0
    for name in ("main.tex", "si.tex"):
        p = OVERLEAF / name
        raw = p.read_bytes().decode("utf-8")
        hits = list(scan(raw))
        out, last = [], 0
        for m, is_sec in hits:
            n = int(m.group(1))
            line = raw.count("\n", 0, m.start()) + 1
            ctx = raw[max(0, m.start() - 38):m.end() + 18].replace("\n", " ").replace("\r", "")
            if not is_sec:
                print(f"  not a section  {name}:{line}  ...{ctx}...")
                continue
            if shift and n >= shift[0]:
                out.append(raw[last:m.start()] + f"S{n + shift[1]}")
                last = m.end()
                total += 1
                print(f"  S{n} -> S{n + shift[1]}  {name}:{line}  ...{ctx}...")
            elif not shift:
                print(f"  S{n}  {name}:{line}  ...{ctx}...")
        if shift and out:
            p.write_bytes(("".join(out) + raw[last:]).encode("utf-8"))
    if shift:
        print(f"{total} section number(s) shifted")


if __name__ == "__main__":
    main(sys.argv[1:])
