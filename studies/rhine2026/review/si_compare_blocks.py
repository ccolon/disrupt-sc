r"""Compare the regenerated reference tables of a folder with the blocks of the manuscript, without writing anything.
python compare_blocks.py <disrupt-sc> <overleaf> <folder with <name>.tex references>"""
import re
import sys
from pathlib import Path

repo, ov, ref = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(repo / "studies/rhine2026"))
import si_tables  # noqa: E402

docs = {q.name: q.read_text(encoding="utf-8").replace("\r\n", "\n") for q in (ov / "main.tex", ov / "si.tex")}
for p in sorted(ref.glob("*.tex")):
    pat = re.compile(r"^% >>> generated table " + re.escape(p.stem) + r"\b[^\n]*\n(.*?)^% <<< generated table " + re.escape(p.stem) + r"[ \t]*$",
                     re.MULTILINE | re.DOTALL)
    hit = None
    for name, text in docs.items():
        m = pat.search(text)
        if m:
            hit = (name, m.group(1))
            break
    if not hit:
        print(f"{p.stem}: no block in the manuscript")
        continue
    problems, changes, _ = si_tables.compare_table(p.stem, p.read_text(encoding="utf-8"), hit[1])
    rows = len(si_tables.body_rows(hit[1]))
    print(f"{p.stem} ({hit[0]}, {rows} body rows): " + ("OK" if not problems and not changes else f"{len(problems)} structure, {len(changes)} cells"))
    for x in (problems + changes)[:8]:
        print("    " + x[:260])
