"""Append verified BibTeX entries of a positioning dossier to the manuscript's refs.bib.

    python studies/rhine2026/evidence/add_refs_from_dossier.py <dossier.md> <refs.bib> key1 key2 ...

The dossier's BibTeX block (entries '@type{key,' ... '}' at column 0) is parsed; the requested keys that refs.bib
does not hold yet are appended under a dated comment, with the file's line endings. Missing keys are listed and
exit 1. Run studies/paper_pipeline/scripts/cite_check.py on a copy of refs.bib afterwards (it writes a cache next
to its input).
"""
import re
import sys
from pathlib import Path

dossier, bib, keys = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
text = dossier.read_text(encoding="utf-8").replace("\r\n", "\n")
entries = {}
for m in re.finditer(r"^@(\w+)\{([^,\s]+),\n(.*?)^\}\s*$", text, re.M | re.S):
    entries[m.group(2)] = f"@{m.group(1)}{{{m.group(2)},\n{m.group(3)}}}"
with open(bib, encoding="utf-8", newline="") as f:
    cur = f.read()
nl = "\r\n" if "\r\n" in cur else "\n"
have = set(re.findall(r"^@\w+\{([^,\s]+),", cur.replace("\r\n", "\n"), re.M))
missing = [k for k in keys if k not in entries]
add = [k for k in keys if k in entries and k not in have]
skip = [k for k in keys if k in have]
block = ""
if add:
    block = nl + f"% ---- positioning review of 7 November 2026 ({dossier.name}); DOIs verified on Crossref by the review" + nl
    block += (nl + nl).join(entries[k].replace("\n", nl) for k in add) + nl
    with open(bib, "a", encoding="utf-8", newline="") as f:
        f.write(block)
print(f"added {len(add)}: {' '.join(add)}")
if skip:
    print(f"already present {len(skip)}: {' '.join(skip)}")
if missing:
    print(f"MISSING in the dossier {len(missing)}: {' '.join(missing)}")
    sys.exit(1)
