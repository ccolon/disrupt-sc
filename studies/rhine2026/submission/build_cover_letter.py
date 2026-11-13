r"""Build the cover letter as a Word file from cover_letter.md (the text between its two '---' lines).

    python studies/rhine2026/submission/build_cover_letter.py --out DIR [--orcid ID] [--overleaf DIR]

[email] is read from the correspondence line of main.tex of the Overleaf copy (it is not stored in this repository),
[ORCID] from --orcid (left as it is when absent) and [date] is today's date. Other square brackets are left for the
author. The heading "Information removed from the manuscript ..." starts a new page and is set in bold.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Pt

HERE = Path(__file__).resolve().parent
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--orcid", default=None)
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    a = ap.parse_args()
    text = (HERE / "cover_letter.md").read_text(encoding="utf-8")
    body = text.split("\n---\n")[1].strip()
    m = re.search(r"Correspondence:\s*([^\s}]+)", (Path(a.overleaf) / "main.tex").read_text(encoding="utf-8"))
    if m:
        body = body.replace("[email]", m.group(1))
    if a.orcid:
        body = body.replace("[ORCID]", a.orcid)
    today = dt.date.today()
    body = body.replace("[date]", f"{today.day} {today.strftime('%B %Y')}")

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    for block in re.split(r"\n\s*\n", body):
        lines = block.split("\n")
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        heading = lines[0].startswith("Information removed from the manuscript")
        if heading:
            p.add_run().add_break(WD_BREAK.PAGE)
        for i, ln in enumerate(lines):
            run = p.add_run(ln)
            run.bold = heading
            if i < len(lines) - 1:
                run.add_break()
    core = doc.core_properties
    core.author = ""
    core.last_modified_by = ""
    core.title = "Cover letter"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    doc.save(out / "cover_letter.docx")
    left = sorted(set(re.findall(r"\[[^\]]{3,60}", body)))
    print(f"written {out / 'cover_letter.docx'}; {len(body.split())} words; brackets left for the author: {[x[:45] for x in left]}")


if __name__ == "__main__":
    main()
