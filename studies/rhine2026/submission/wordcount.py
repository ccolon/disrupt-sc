"""Word counts of the Rhine 2026 manuscript against the Nature Communications guide (Article page, read 7 Nov 2026:
main text ideally <= 5,000 words excluding abstract, Methods, references and legends; title <= 15 words; abstract
<= 200 words; Methods typically < 3,000; legends <= 350 each; references as a guide <= 70; up to 10 display items),
from the LaTeX source with the numbers.tex macros expanded.

    python studies/rhine2026/submission/wordcount.py [<overleaf dir>]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
GUIDE = {"title": 15, "abstract": 200, "main": 5000, "methods": 3000, "legend": 350, "refs": 70, "display": 10}


def _macros(nums: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in
            re.finditer(r"\\(?:re)?newcommand\{\\([A-Za-z]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", nums)}


def _clean(s: str, macros: dict[str, str]) -> str:
    s = re.sub(r"(?<!\\)%.*", "", s)
    for _ in range(3):
        s = re.sub(r"\\([A-Za-z]+)(?:\{\})?", lambda m: macros.get(m.group(1), m.group(0)), s)
    for env in ("figure", "table"):
        s = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", " ", s, flags=re.S)
    s = re.sub(r"\\(?:citep|citet|cite|ref|label|eqref|autoref|todo|input|include|bibliography|bibliographystyle|url)\*?\{[^{}]*\}", " ", s)
    s = re.sub(r"\\(?:section|subsection|subsubsection)\*?\{[^{}]*\}", " ", s)
    for _ in range(3):
        s = re.sub(r"\\(?:finalbatch|textbf|emph|textit|texttt|paragraph|textcolor\{[^{}]*\}|mbox|text|small|normalsize|noindent)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\$[^$]*\$", " MATH ", s)
    s = re.sub(r"\\[,;:!]", " ", s)
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)
    s = re.sub(r"[{}~]", " ", s)
    return s.replace("--", " ")


def _words(s: str) -> int:
    return len([w for w in re.split(r"\s+", s) if re.search(r"[A-Za-z0-9]", w)])


def counts(ov: Path) -> dict:
    main = (ov / "main.tex").read_text(encoding="utf-8").replace("\r\n", "\n")
    macros = _macros((ov / "numbers.tex").read_text(encoding="utf-8").replace("\r\n", "\n"))
    body = main[main.index(r"\begin{document}"):]

    def section(start, end=None):
        i = body.index(start)
        j = body.index(end, i) if end else len(body)
        return body[i:j]

    stop = next(m for m in (r"\section*{Data availability}", r"\section*{Acknowledgements}", r"\bibliographystyle") if m in body)
    parts = {"abstract": re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S).group(1),
             "introduction": section(r"\section*{Introduction}", r"\section*{Results}"),
             "results": section(r"\section*{Results}", r"\section*{Discussion}"),
             "discussion": section(r"\section*{Discussion}", r"\section*{Methods}"),
             "methods": section(r"\section*{Methods}", stop)}
    c = {k: _words(_clean(v, macros)) for k, v in parts.items()}
    c["main"] = c["introduction"] + c["results"] + c["discussion"]
    title = re.search(r"\\title\{(.*?)\}\n", main, re.S).group(1)
    c["title"] = _words(_clean(title, macros))
    main_body = section(r"\section*{Introduction}", stop)
    c["figures"] = main_body.count(r"\begin{figure}")
    c["tables"] = main_body.count(r"\begin{table}")
    caps = re.findall(r"\\caption\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", main_body, re.S)
    c["legends"] = [_words(_clean(x, macros)) for x in caps]
    keys = set()
    for f in [main] + [q.read_text(encoding="utf-8") for q in sorted((ov / "sections").glob("*.tex"))]:
        for grp in re.findall(r"\\cite[pt]?\{([^{}]*)\}", f):
            keys.update(k.strip() for k in grp.split(","))
    c["cited"] = len(keys)
    c["bib_entries"] = len(re.findall(r"^@", (ov / "refs.bib").read_text(encoding="utf-8"), re.M))
    return c


def report(ov: Path = OVERLEAF) -> str:
    c = counts(ov)

    def flag(v, lim):
        return "ok" if v <= lim else f"OVER by {v - lim}"
    lines = [f"title: {c['title']} words (guide {GUIDE['title']}; {flag(c['title'], GUIDE['title'])})",
             f"abstract: {c['abstract']} words (guide {GUIDE['abstract']}; {flag(c['abstract'], GUIDE['abstract'])})",
             f"main text: {c['main']} words = introduction {c['introduction']} + results {c['results']} + discussion {c['discussion']} "
             f"(guide {GUIDE['main']}; {flag(c['main'], GUIDE['main'])})",
             f"methods: {c['methods']} words (guide {GUIDE['methods']}; {flag(c['methods'], GUIDE['methods'])})",
             f"display items: {c['figures']} figures + {c['tables']} tables = {c['figures'] + c['tables']} (guide {GUIDE['display']}; "
             f"{flag(c['figures'] + c['tables'], GUIDE['display'])})",
             f"legends: {c['legends']} words (guide {GUIDE['legend']} each; {'ok' if max(c['legends']) <= GUIDE['legend'] else 'OVER'})",
             f"references cited: {c['cited']} of {c['bib_entries']} bib entries (guide {GUIDE['refs']}; {flag(c['cited'], GUIDE['refs'])})"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF))
