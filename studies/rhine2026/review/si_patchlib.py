r"""Helpers of the patch scripts that answer the author's revision of the SI (10 Nov 2026). Every edit of the Overleaf
copy is exact and anchored: an anchor that is missing or repeated stops the script before anything is written, and a
script that has already been applied says so instead of failing. Line endings of the file are kept.

    from si_patchlib import Doc
    d = Doc(overleaf / "si.tex")
    d.sub(old, new)                 # one exact replacement
    d.line(prefix, new_line)        # the one line that starts with prefix
    d.block("si_stocks", inner)     # the inside of a '% >>> generated table <name>' block
    d.save()
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


class Doc:
    def __init__(self, path: Path):
        self.path = Path(path)
        raw = self.path.read_bytes().decode("utf-8")
        self.crlf = "\r\n" in raw
        self.text = raw.replace("\r\n", "\n")
        self.fails: list[str] = []
        self.done = 0

    def sub(self, old: str, new: str, count: int = 1) -> None:
        c = self.text.count(old)
        if c == count:
            self.text = self.text.replace(old, new)
            self.done += 1
        elif c == 0 and new and new in self.text:
            print(f"   already applied: {old[:60]!r}")
        else:
            self.fails.append(f"found {c} (expected {count}): {old[:110]!r}")

    def line(self, prefix: str, new: str | None) -> None:
        """Replace the one line that starts with `prefix` (new=None deletes it, with the blank line that follows)."""
        lines = self.text.split("\n")
        hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
        if len(hits) != 1:
            if new is not None and any(ln == new for ln in lines):
                print(f"   already applied: line {prefix[:50]!r}")
            elif new is None and not hits:
                print(f"   already removed: line {prefix[:50]!r}")
            else:
                self.fails.append(f"{len(hits)} lines start with {prefix[:90]!r}")
            return
        i = hits[0]
        if new is None:
            del lines[i]
            if i < len(lines) and lines[i].strip() == "" and i > 0 and lines[i - 1].strip() == "":
                del lines[i]
        else:
            lines[i] = new
        self.text = "\n".join(lines)
        self.done += 1

    def get_line(self, prefix: str) -> str:
        hits = [ln for ln in self.text.split("\n") if ln.startswith(prefix)]
        if len(hits) != 1:
            self.fails.append(f"{len(hits)} lines start with {prefix[:90]!r}")
            return ""
        return hits[0]

    def _block(self, name: str):
        return re.search(r"^(% >>> generated table " + re.escape(name) + r"\b[^\n]*\n)(.*?)(^% <<< generated table " + re.escape(name) + r"[ \t]*$)",
                         self.text, re.MULTILINE | re.DOTALL)

    def block(self, name: str, inner: str | None = None) -> str:
        """The inside of the block of table `name`; with `inner`, replace it."""
        m = self._block(name)
        if not m:
            self.fails.append(f"no block {name}")
            return ""
        if inner is not None:
            self.text = self.text[:m.start(2)] + inner + self.text[m.end(2):]
            self.done += 1
        return m.group(2)

    def remove_block(self, name: str) -> str:
        """Remove the block of table `name` with its markers (and one blank line after it); returns its inside."""
        m = self._block(name)
        if not m:
            print(f"   already removed: block {name}")
            return ""
        end = m.end()
        if self.text[end:end + 2] == "\n\n":
            end += 1
        self.text = self.text[:m.start()] + self.text[end + 1:] if self.text[end:end + 1] == "\n" else self.text[:m.start()] + self.text[end:]
        self.done += 1
        return m.group(2)

    def save(self) -> None:
        if self.fails:
            print(f"NOT SAVED {self.path.name}: {len(self.fails)} anchor(s) failed")
            for f in self.fails:
                print("   " + f)
            sys.exit(1)
        self.path.write_bytes((self.text.replace("\n", "\r\n") if self.crlf else self.text).encode("utf-8"))
        print(f"saved {self.path.name}: {self.done} edit(s)")
