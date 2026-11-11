r"""Repair of cluster/merge_cluster_tables_20261111.py after patch_tools_20261111_provenance.py (11 Nov 2026): the patch was
written through a shell heredoc that collapsed the doubled backslashes, so the "\n" of the inserted line became real line
breaks. The broken block is replaced by the intended line; the same repair is made in the patch script so that it can be
read as what was meant. Run once.

    python fix_merge_newlines_20261111.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOOD = ('        txt = "\\n".join(header(ref.with_suffix(".txt"))) + "\\n" + new_csv.loc[[inv], cols].T.to_string() + "\\n\\n" + MARK + "\\n" '
        '+ new_wk[[inv]].dropna().to_string() + "\\n\\n" + f"# {note}\\n"\n')

for p, indent in ((HERE.parent / "cluster" / "merge_cluster_tables_20261111.py", "        "), (HERE / "patch_tools_20261111_provenance.py", "        ")):
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.replace("\r\n", "\n").split("\n")
    start = [i for i, l in enumerate(lines) if l == indent + 'txt = "']
    if not start:
        print(f"{p.name}: no broken block (already repaired?)")
        continue
    assert len(start) == 1, (p.name, start)
    i = start[0]
    j = next(k for k in range(i, len(lines)) if lines[k].startswith(indent + "out.with_suffix(\".txt\")"))
    good = GOOD.rstrip("\n")
    if p.name.startswith("patch_"):
        good = good.replace("\\n", "\\\\n")        # in the patch script the line sits inside a string literal
    lines[i:j] = [good]
    p.write_bytes("\n".join(lines).replace("\n", nl).encode("utf-8"))
    print(f"{p.name}: lines {i + 1} to {j} replaced by one line")
