r"""Edit the ledger of paper_gate.py for a revision of the manuscript (10 Nov 2026): drop the entries whose sentence left
the text, add entries for new literals. Dropping is textual, so the ledger files keep their comments; additions go to
one file (si_c.yaml by default), written whole. Idempotent: dropping a text that is not there and adding a text that is
already there do nothing.

    from ledger_edit import Ledger
    L = Ledger()
    L.drop("Eleven sectors use facility data", ...)          # by the 'text' field, in any ledger file
    L.allow("si.tex", text, why)                              # a literal that may stay
    L.claim("si.tex", text, expr, [low, high], why)           # words bound to macros
    L.save()
"""
from __future__ import annotations

from pathlib import Path

import yaml

LEDGER = Path(__file__).resolve().parents[1] / "paper_gate_ledger"
HEADER = ("# Ledger of paper_gate.py: entries added with the author's revision of the SI of 10 November 2026 (written by\n"
          "# review/ledger_si_20261110.py through review/ledger_edit.py). Format: see the docstring of paper_gate.py.\n")


class Ledger:
    def __init__(self, folder: Path = LEDGER, new_file: str = "si_c.yaml"):
        self.folder = Path(folder)
        self.new_path = self.folder / new_file
        self.new = {"allowed": [], "claims": [], "pending": []}
        if self.new_path.exists():
            d = yaml.safe_load(self.new_path.read_text(encoding="utf-8")) or {}
            for k in self.new:
                self.new[k] = d.get(k) or []
        self.dropped, self.added = [], 0

    def _texts(self) -> set:
        out = set()
        for p in self.folder.glob("*.yaml"):
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            for k in ("allowed", "claims", "pending"):
                out |= {(e.get("file"), e.get("text")) for e in d.get(k) or []}
        return out

    def drop(self, *texts: str, file: str | None = None) -> None:
        """Drop the entries with these texts; with `file`, only those of that manuscript file."""
        want = set(texts)
        hit = lambda e: isinstance(e, dict) and e.get("text") in want and (file is None or e.get("file") == file)   # noqa: E731
        for k in self.new:                                   # entries of the additions file
            keep = [e for e in self.new[k] if not hit(e)]
            self.dropped += [e["text"] for e in self.new[k] if hit(e)]
            self.new[k] = keep
        for p in sorted(self.folder.glob("*.yaml")):
            if p == self.new_path:
                continue
            raw = p.read_bytes().decode("utf-8")
            crlf = "\r\n" in raw
            lines = raw.replace("\r\n", "\n").split("\n")
            out, i, changed = [], 0, False
            while i < len(lines):
                if lines[i].startswith("  - "):
                    j = i + 1
                    while j < len(lines) and lines[j].startswith("    ") and not lines[j].lstrip().startswith("#"):
                        j += 1
                    entry = yaml.safe_load("\n".join(lines[i:j]))[0]
                    if hit(entry):                                               # an 'ignore' item is a plain string
                        self.dropped.append(entry["text"])
                        changed = True
                    else:
                        out += lines[i:j]
                    i = j
                else:
                    out.append(lines[i])
                    i += 1
            if changed:
                text = "\n".join(out)
                p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))

    def drop_missing(self, repo: Path) -> list:
        """Drop every entry whose text is no longer in its document, read as paper_gate.py reads it (comments stripped,
        table bodies blanked). For the end of a revision, once every reworded sentence has its new entry; returns the
        texts dropped."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import paper_gate
        docs = paper_gate.documents(Path(repo))
        dead = []                                     # (file, text): the same text may live on in the other file
        for p in sorted(self.folder.glob("*.yaml")):
            if p == self.new_path:
                continue
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            for k in ("allowed", "claims", "pending"):
                dead += [(e["file"], e["text"]) for e in d.get(k) or [] if e.get("file") in docs and e["text"] not in docs[e["file"]]]
        for k in self.new:
            dead += [(e["file"], e["text"]) for e in self.new[k] if e.get("file") in docs and e["text"] not in docs[e["file"]]]
        for f in sorted({f for f, _ in dead}):
            self.drop(*[t for g, t in dead if g == f], file=f)
        return [f"{f}: {t}" for f, t in dead]

    def _add(self, kind: str, entry: dict) -> None:
        if (entry["file"], entry["text"]) in self._texts() or any(e["text"] == entry["text"] and e["file"] == entry["file"] for e in self.new[kind]):
            return
        self.new[kind].append(entry)
        self.added += 1

    def allow(self, file: str, text: str, why: str) -> None:
        self._add("allowed", {"file": file, "text": text, "why": why})

    def claim(self, file: str, text: str, expr: str, rng: list, why: str) -> None:
        self._add("claims", {"file": file, "text": text, "expr": expr, "range": rng, "why": why})

    def pending(self, file: str, text: str, note: str) -> None:
        self._add("pending", {"file": file, "text": text, "note": note})

    def save(self) -> None:
        body = yaml.safe_dump(self.new, allow_unicode=True, sort_keys=False, width=10000, default_flow_style=None)
        self.new_path.write_text(HEADER + body, encoding="utf-8")
        print(f"ledger: {len(self.dropped)} entries dropped, {self.added} added ({self.new_path.name}: "
              f"{len(self.new['allowed'])} allowed, {len(self.new['claims'])} claims, {len(self.new['pending'])} pending)")
