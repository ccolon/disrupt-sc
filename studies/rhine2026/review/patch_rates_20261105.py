r"""SI S1 text with the rates table of the batch's own parameters (5 Nov 2026). The table (si_tables.rates_table) now
reads the reference run's parameters.yaml, which carries the job lists' overrides: rail costs by country, waterway
costs by waterway, a fee by seaport. S1 gave the base values as if they held everywhere; it now says they are the base
values and names the variants, which the table lists. No number changes.

    python studies/rhine2026/review/patch_rates_20261105.py [--repo <overleaf>] [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
EDITS = [
    ("sections/si.tex", r"sea lanes 0.0015; a value of time per cargo class",
     r"sea lanes 0.0015, the base values (rail costs vary by country and waterway costs by waterway, Table~\ref{tab:rates}); a value of time per cargo class"),
    ("sections/si.tex", r"and transfer costs at terminals by pair of modes and cargo class (Table~\ref{tab:rates})",
     r"and transfer costs at terminals by pair of modes and cargo class, with a fee by seaport (Table~\ref{tab:rates})"),
]


def main(repo: Path, apply: bool):
    docs = {}
    for f, old, new in EDITS:
        t = docs.setdefault(f, (repo / f).read_text(encoding="utf-8"))
        n = t.count(old)
        if n != 1:
            sys.exit(f"{f}: expected the old text once, found {n}: {old[:80]!r}")
        docs[f] = t.replace(old, new)
        print(f"{f}\n  - {old}\n  + {new}")
    if apply:
        for f, t in docs.items():
            (repo / f).write_text(t, encoding="utf-8")
        print("written")
    else:
        print("dry run")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    main(Path(a.repo), a.apply)
