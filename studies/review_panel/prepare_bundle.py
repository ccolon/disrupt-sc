r"""Build the reading bundle of the reviewer panel (5 Nov 2026): what an outside referee would receive, and nothing else.

From an Overleaf checkout at a given commit:
  paper.pdf          the manuscript compiled with tectonic (line numbers switched off: pypdf glues them to the text)
  paper.txt          its text, page by page ('=== page N ==='), the only text the referees read
  figures/           every figure of the main text and the SI rendered to PNG (Ghostscript), figures/index.md maps
                     'Figure 3' / 'Supplementary Figure S2' to the files
  BUNDLE.md          the commit, its date, the page count and the list above

The referees never see the repository, the code, the notes or earlier reviews: independence is the point of the panel.

Usage:
    python studies/review_panel/prepare_bundle.py --repo <overleaf checkout> --commit <sha> --out <folder>
e.g.
    python studies/review_panel/prepare_bundle.py --commit ce22110 --out C:/dsc_runs/review_panel/rhine_ce22110
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


def tool(*names: str) -> str:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    home = Path.home() / ".local" / "bin" / f"{names[0]}.exe"
    if home.exists():
        return str(home)
    sys.exit(f"none of {names} found on PATH")


def export(repo: Path, commit: str, dest: Path) -> str:
    """The tree of the commit (not the working copy): git archive into dest. Returns 'sha date'."""
    data = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        t.extractall(dest, filter="data")
    return subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%H %cd", "--date=iso", commit],
                          capture_output=True, text=True, check=True).stdout.strip()


def inline(src: Path, rel: str, depth: int = 0) -> str:
    """The document with every \\input / \\include expanded, comments stripped (figures may live in section files)."""
    p = src / rel if (src / rel).exists() else src / (rel + ".tex")
    if not p.exists() or depth > 8:
        return ""
    text = re.sub(r"(?<!\\)%.*$", "", p.read_text(encoding="utf-8"), flags=re.MULTILINE)
    return re.sub(r"\\(?:input|include)\{([^}]*)\}", lambda mm: inline(src, mm.group(1), depth + 1), text)


def figures_of(src: Path):
    """[(label for the reader, tex label, [included files])] in source order; the figures after the switch to
    S-numbering (\\renewcommand{\\thefigure}{S...}) are the Supplementary Figures S1.."""
    doc = inline(src, "main.tex")
    m = re.search(r"\\renewcommand\{\\thefigure\}\{S", doc)
    parts = [("", doc[:m.start()]), ("S", doc[m.start():])] if m else [("", doc)]
    out = []
    for prefix, text in parts:
        for n, block in enumerate(re.findall(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", text, flags=re.DOTALL), 1):
            files = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", block)
            lab = re.search(r"\\label\{([^}]*)\}", block)
            name = f"Supplementary Figure S{n}" if prefix else f"Figure {n}"
            out.append((name, lab.group(1) if lab else "", files))
    return out


def main(repo: Path, commit: str, out: Path):
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} exists and is not empty: choose a new folder (bundles are kept as the record of what was read)")
    out.mkdir(parents=True, exist_ok=True)
    src = out / "src"
    head = export(repo, commit, src)
    # line numbers off: pypdf glues them to the line ends ('supply chains,8'); referees cite pages and sections
    m = src / "main.tex"
    m.write_text(re.sub(r"^\\linenumbers\s*$", "", m.read_text(encoding="utf-8"), flags=re.MULTILINE), encoding="utf-8")
    # the local package cache first (seconds); online only when a package is missing (the bundle server can stall minutes)
    r = subprocess.run([tool("tectonic"), "--only-cached", "--outdir", str(out), str(m)], capture_output=True, text=True)
    if not (out / "main.pdf").exists():
        r = subprocess.run([tool("tectonic"), "--outdir", str(out), str(m)], capture_output=True, text=True)
    if not (out / "main.pdf").exists():
        sys.exit(f"tectonic failed:\n{r.stderr[-2000:]}")
    (out / "main.pdf").replace(out / "paper.pdf")

    from pypdf import PdfReader
    reader = PdfReader(out / "paper.pdf")
    pages = [f"=== page {i} ===\n{p.extract_text() or ''}" for i, p in enumerate(reader.pages, 1)]
    (out / "paper.txt").write_text("\n\n".join(pages) + "\n", encoding="utf-8")

    gs = tool("gswin64c", "gswin32c", "gs")
    fig_dir = out / "figures"; fig_dir.mkdir()
    index = ["# Figures of the manuscript", "", "| figure | label | files |", "|---|---|---|"]
    for name, lab, files in figures_of(src):
        made = []
        for k, f in enumerate(files):
            stem = re.sub(r"\W+", "_", name.replace("Supplementary Figure ", "SFig").replace("Figure ", "Fig")) + (f"_{chr(97 + k)}" if len(files) > 1 else "")
            p = src / f
            p = p if p.exists() else next((src / (f + e) for e in (".pdf", ".png", ".jpg") if (src / (f + e)).exists()), None)
            if p is None:
                continue
            target = fig_dir / f"{stem}.png"
            if p.suffix.lower() == ".pdf":
                subprocess.run([gs, "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dQUIET", "-sDEVICE=png16m", "-r130",
                                "-dFirstPage=1", "-dLastPage=1", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
                                f"-sOutputFile={target}", str(p)], check=True)
            else:
                shutil.copy2(p, target.with_suffix(p.suffix.lower()))
                target = target.with_suffix(p.suffix.lower())
            made.append(target.name)
        index.append(f"| {name} | {lab} | {', '.join(made) or '(not found)'} |")
    (fig_dir / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    shutil.rmtree(src, ignore_errors=True)       # the referees get the compiled paper, not the source
    (out / "BUNDLE.md").write_text(
        f"# Reading bundle\n\nManuscript at commit {head}, compiled with tectonic: {len(reader.pages)} pages.\n\n"
        "- paper.txt: the text, page by page (read this)\n- figures/: the figures as images, figures/index.md maps them\n"
        "- paper.pdf: the compiled PDF (same content)\n", encoding="utf-8")
    print(f"bundle written to {out}: {len(reader.pages)} pages, {len(index) - 4} figures")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    main(Path(a.repo), a.commit, Path(a.out))
