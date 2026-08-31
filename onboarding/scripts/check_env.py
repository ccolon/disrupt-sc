"""Phase-0 environment check for the new-scope pipeline (see RUNBOOK.md).

Verifies, without changing anything:
  - the disrupt-sc repo root and the data root resolve
  - the four toolchain repos exist in a close location (clone commands otherwise)
  - the toolchain python packages import in the current env
  - the MRIO source data files are on disk (licensed - NOT on GitHub)
  - osmium availability (needed only to merge multiple PBFs)

Usage:
    python check_env.py

Exit code 0 = complete, 1 = something required is missing.
"""

from __future__ import annotations

import importlib
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402


def main() -> int:
    ok = True
    try:
        repo = locate.find_repo_root()
        print(f"OK: repo root {repo}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    dr = locate.data_root()
    if dr.is_dir():
        print(f"OK: data root {dr}")
    else:
        ok = False
        print(f"MISSING: data root {dr}")
        print("         set DISRUPT_SC_DATA_PATH, or clone/create the disrupt-sc-data "
              "folder next to the repo")

    for name in locate.TOOL_REPOS:
        p = locate.find_tool_repo(name)
        if p:
            print(f"OK: {name} at {p}")
        else:
            ok = False
            print(f"MISSING: {name} - ask the user to run:")
            print(f"         {locate.clone_hint(name)}")
            print('         then: pip install -e "<cloned path>"')

    for mod in ("geopandas", "osm_extractor", "tnclean", "multitnbuild"):
        try:
            importlib.import_module(mod)
            print(f"OK: import {mod}")
        except ImportError:
            ok = False
            print(f"MISSING: python package '{mod}' in this env - pip install -e "
                  "the corresponding repo above (activate the toolchain conda env first)")

    mr = locate.mrio_root()
    sources = {
        "ICIO": mr / "ICIO" / "2025_ed_reg",
        "EMERGING-E": mr / "EMERGING-E" / "EMERGING_E_2018.mat",
        "GLORIA": mr / "GLORIA" / "mrio_va_fd.pkl",
        "FIGARO-REG": mr / "FIGARO" / "FIGARO-REG",
    }
    for name, p in sources.items():
        if p.exists():
            print(f"OK: {name} source data ({p})")
        else:
            # data, not code: only blocks extractions from that database
            print(f"note: {name} source data absent ({p}) - licensed data, not on "
                  f"GitHub; blocks phase 4 only if {name} is the chosen database")

    if shutil.which("osmium"):
        print("OK: osmium on PATH")
    else:
        print("note: osmium not on PATH (only needed to merge multiple country PBFs)")

    print("\nEnvironment " + ("OK" if ok else "INCOMPLETE - fix the MISSING lines above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
