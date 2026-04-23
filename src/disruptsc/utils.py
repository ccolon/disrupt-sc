"""Shared utility helpers."""

from __future__ import annotations

import sys
from typing import Iterable


def progress(iterable: Iterable, desc: str, total: int | None = None) -> Iterable:
    """Wrap *iterable* with a tqdm bar when stderr is a TTY, else return as-is.

    Piped / CI runs see the original iterable so logs stay clean; interactive
    terminals get a live progress indicator. Cost when disabled is a single
    isatty() check; cost when enabled is ~1–10 microseconds per iteration.
    """
    if not sys.stderr.isatty():
        return iterable
    from tqdm import tqdm
    return tqdm(iterable, desc=desc, total=total, leave=False, mininterval=0.2)
