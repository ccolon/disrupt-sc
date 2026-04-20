#!/usr/bin/env python3
"""Compatibility wrapper for the v2 input validator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from disruptsc.validate_inputs import main


if __name__ == "__main__":
    raise SystemExit(main())
