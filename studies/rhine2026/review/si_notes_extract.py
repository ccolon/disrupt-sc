r"""Extract the author's revision of si.tex (Overleaf 675722a against fc30932): the inline todo notes with their
context, and the word-level text edits once the notes are stripped. Usage:
    python si_notes_extract.py <overleaf repo> <old ref:path> <new path> <out.md>
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

repo, old_spec, new_path, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
old = subprocess.run(["git", "-C", str(repo), "show", old_spec], capture_output=True, check=True).stdout.decode("utf-8")
new = (repo / new_path).read_text(encoding="utf-8")


def find_todos(text):
    """Yield (start, end, note) of every \\todo{...} with balanced braces."""
    i = 0
    while True:
        j = text.find("\\todo{", i)
        if j < 0:
            return
        k, depth = j + 6, 1
        while k < len(text) and depth:
            c = text[k]
            if c == "\\":
                k += 2
                continue
            depth += (c == "{") - (c == "}")
            k += 1
        yield j, k, text[j + 6:k - 1]
        i = k


def strip_todos(text):
    parts, last = [], 0
    for a, b, _ in find_todos(text):
        parts.append(text[last:a])
        last = b
    parts.append(text[last:])
    return "".join(parts)


def section_of(lines):
    """Map line index -> section label (S1..S10)."""
    lab, res = "S0", []
    for ln in lines:
        m = re.match(r"\\subsection\*\{(S\d+)", ln)
        if m:
            lab = m.group(1)
        res.append(lab)
    return res


new_lines = new.split("\n")
sec = section_of(new_lines)
notes = []
for li, ln in enumerate(new_lines):
    for a, b, note in find_todos(ln):
        before = strip_todos(ln[:a])[-330:]
        after = strip_todos(ln[b:])[:160]
        notes.append((sec[li], li + 1, note, before, after))

md = ["# The author's revision of si.tex (675722a against fc30932)", ""]
md.append(f"Notes: {len(notes)}; new file {len(new_lines)} lines, old {len(old.split(chr(10)))} lines.")
md.append("")
md.append("## Inline notes")
n = 0
for s, li, note, before, after in notes:
    n += 1
    md.append(f"### N{n:02d} [{s}] line {li}")
    md.append(f"NOTE: {note}")
    md.append(f"BEFORE: ...{before}")
    md.append(f"AFTER: {after}...")
    md.append("")

# text edits, notes stripped
new_clean = [strip_todos(ln) for ln in new_lines]
old_lines = old.split("\n")
sm = difflib.SequenceMatcher(a=old_lines, b=new_clean, autojunk=False)
md.append("## Text edits (notes stripped), by line")
ne = 0
tok = re.compile(r"\s+|[^\s]+")
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    olds, news = old_lines[i1:i2], new_clean[j1:j2]
    if [x.rstrip() for x in olds] == [x.rstrip() for x in news]:
        continue
    ne += 1
    s = sec[j1] if j1 < len(sec) else "end"
    md.append(f"### E{ne:02d} [{s}] old {i1 + 1}-{i2} -> new {j1 + 1}-{j2} ({tag})")
    if tag == "replace" and len(olds) == len(news):
        for k, (o, w) in enumerate(zip(olds, news)):
            if o.rstrip() == w.rstrip():
                continue
            ow, nw = tok.findall(o), tok.findall(w)
            wm = difflib.SequenceMatcher(a=ow, b=nw, autojunk=False)
            chunks = []
            for t, a1, a2, b1, b2 in wm.get_opcodes():
                if t == "equal":
                    seg = "".join(ow[a1:a2])
                    chunks.append(seg if len(seg) < 160 else seg[:70] + " [...] " + seg[-70:])
                else:
                    d, a = "".join(ow[a1:a2]), "".join(nw[b1:b2])
                    chunks.append("[-" + d + "-]{+" + a + "+}")
            md.append(f"line {j1 + 1 + k}: " + "".join(chunks))
    else:
        for o in olds:
            md.append("- " + (o if len(o) < 900 else o[:450] + " [...] " + o[-300:]))
        for w in news:
            md.append("+ " + (w if len(w) < 900 else w[:450] + " [...] " + w[-300:]))
    md.append("")
md.append(f"Text edit hunks: {ne}")
out.write_text("\n".join(md), encoding="utf-8")
print(f"notes {len(notes)}; edit hunks {ne}; written {out} ({out.stat().st_size} bytes)")
by = {}
for s, *_ in notes:
    by[s] = by.get(s, 0) + 1
print("notes by section:", by)
