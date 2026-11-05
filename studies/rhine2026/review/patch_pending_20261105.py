r"""Apply the reviewed fixes of the gate's pending literals (5 Nov 2026): model outputs that the manuscript still wrote
as numbers, and the inconsistencies found with them. The fixes are a reviewed YAML (pending_fixes_20261105.yaml next
to this script, merged from the three section drafts), one entry per pending ledger entry:

  kind use_macro / new_macro / correct: replace `old` by `new` in the manuscript (exact, once);
  kind allow: the literal is legitimate (evidence, design, history kept on purpose): an allowed ledger entry;
  kind keep: unresolved, the pending entry stays;
  every entry except keep drops its pending ledger entry; `ledger` lists the allowed / claims entries the new text needs.

New macros are computed by make_numbers.py (section 'the pending literals of the gate'): regenerate numbers.tex
BEFORE applying the text, or the new \Macro names are undefined.

Dry run by default; --apply writes; --repo / --ledger point at copies for a verification run; --markdown writes the
review table.

    python studies/rhine2026/review/patch_pending_20261105.py [--fixes <yaml>] [--repo <overleaf>] [--ledger <folder>] [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
LEDGER = HERE.parent / "paper_gate_ledger"
FIXES = HERE / "pending_fixes_20261105.yaml"
EDIT_KINDS = {"use_macro", "new_macro", "correct"}
WHY = "5 Nov 2026 pending fix (patch_pending_20261105.py); "


def q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def drop_entry(text: str, snippet: str, section: str, file: str) -> tuple[str, int]:
    """Remove the entries ('  - file: <file>' + '    text: <snippet>' + indented lines) inside the given section. The
    file must match too: the same snippet can be pending for main.tex and for the SI (5 Nov 2026)."""
    lines, out, i, n, cur = text.split("\n"), [], 0, 0, None
    target = f"    text: {q(snippet)}"
    while i < len(lines):
        if lines[i] and not lines[i].startswith(" ") and lines[i].endswith(":"):
            cur = lines[i][:-1]
        if (cur == section and lines[i].strip() in (f"- file: {file}", f"- file: {q(file)}") and i + 1 < len(lines)
                and lines[i + 1] == target):
            j = i + 2
            while j < len(lines) and lines[j].startswith("    "):
                j += 1
            n += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), n


def insert_before(text: str, marker: str, block: str) -> str:
    k = text.index(f"\n{marker}\n")
    return text[:k + 1] + block + text[k + 1:]


def entry_yaml(kind: str, f: str, e: dict) -> str:
    if kind == "allowed":
        return f"  - file: {f}\n    text: {q(e['text'])}\n    why: {q(WHY + e['why'])}\n"
    lo, hi = e["range"]
    return (f"  - file: {f}\n    text: {q(e['text'])}\n    expr: {q(e['expr'])}\n    range: [{lo}, {hi}]\n"
            f"    why: {q(WHY + e.get('why', ''))}\n")


def main(fixes_path: Path, repo: Path, ledger: Path, apply: bool, markdown: Path | None):
    fixes = yaml.safe_load(fixes_path.read_text(encoding="utf-8"))
    docs = {f: (repo / f).read_text(encoding="utf-8") for f in ("main.tex", "sections/si.tex")}
    led = {p.name: p.read_text(encoding="utf-8") for p in sorted(ledger.glob("*.yaml"))}
    add = {name: {"allowed": "", "claims": ""} for name in led}
    rows = ["| file | kind | old | new | evidence | decision |", "|---|---|---|---|---|---|"]
    counts = {}
    for fx in fixes:
        kind, f = fx["kind"], fx.get("file", "")
        counts[kind] = counts.get(kind, 0) + 1
        if kind == "keep":
            rows.append(f"| {f} | keep | {fx['pending'][:90]} | | {fx.get('evidence', '')} | {fx.get('decision', '')} |")
            continue
        if kind in EDIT_KINDS and not fx.get("merged_into"):     # merged_into: another fix rewrites its sentence
            n = docs[f].count(fx["old"])
            if n != 1:
                sys.exit(f"{f}: expected the old text once, found {n}: {fx['old'][:90]!r}")
            docs[f] = docs[f].replace(fx["old"], fx["new"])
        if not fx.get("pending"):           # an extra edit found on the way (no pending entry to drop)
            rows.append(f"| {f} | {kind} (extra) | {fx.get('old', '')} | {fx.get('new', '')} | {fx.get('evidence', '')} | "
                        f"{fx.get('decision', '')} |")
            continue
        # the pending entry leaves whichever ledger file holds it (for this manuscript file)
        home = None
        for name in led:
            led[name], n = drop_entry(led[name], fx["pending"], "pending", f)
            if n:
                home = name
        if home is None:
            sys.exit(f"pending entry not found in any ledger file: {fx['pending'][:90]!r}")
        for e in fx.get("ledger") or []:
            k = "allowed" if e["kind"] == "allowed" else "claims"
            add[home][k] += entry_yaml(k, f, e)
        if kind == "allow" and not fx.get("ledger"):
            sys.exit(f"allow without a ledger entry: {fx['pending'][:90]!r}")
        cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")
        rows.append(f"| {f} | {kind} | {cell(fx.get('old', fx['pending']))} | {cell(fx.get('new', ''))} | "
                    f"{cell(fx.get('evidence', ''))} | {cell(fx.get('decision', ''))} |")
    for name, parts in add.items():
        if parts["allowed"]:
            led[name] = insert_before(led[name], "claims:", f"  # {WHY}literals the fixed text keeps\n" + parts["allowed"])
        if parts["claims"]:
            led[name] = insert_before(led[name], "pending:", f"  # {WHY}words bound to the new macros\n" + parts["claims"])
    print(f"{len(fixes)} fixes: {counts}")
    if markdown:
        markdown.write_text("\n".join(rows) + "\n", encoding="utf-8")
    if apply:
        for f, t in docs.items():
            (repo / f).write_text(t, encoding="utf-8")
        for name, t in led.items():
            (ledger / name).write_text(t, encoding="utf-8")
        print(f"written: main.tex, sections/si.tex in {repo}; ledger in {ledger}")
    else:
        print("dry run: nothing written (--apply to write)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixes", default=str(FIXES))
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--markdown", default=None)
    a = ap.parse_args()
    main(Path(a.fixes), Path(a.repo), Path(a.ledger), a.apply, Path(a.markdown) if a.markdown else None)
