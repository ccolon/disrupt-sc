"""Locate the disrupt-sc repo, the data root, and the sibling tool repos.

All onboarding scripts resolve paths through this module, so the folder can
move freely inside the repo: the repo root is found by walking upward from
this file to a directory containing both `pyproject.toml` and `src/disruptsc`.

The toolchain lives in separate git repos expected in "close locations"
relative to the repo's parent folder. When one is missing, do not guess -
ask the user to clone it (see TOOL_REPOS for URLs and suggested locations).
The MRIO *source data* (ICIO, EMERGING-E, GLORIA, FIGARO) is licensed and NOT
on GitHub; it must be obtained separately.
"""

from __future__ import annotations

import os
from pathlib import Path

# repo name -> GitHub URL, suggested location relative to the repo's parent,
# and alternative local folder names to search for
TOOL_REPOS = {
    "mrio-extractor": {
        "url": "https://github.com/ccolon/mrio-extractor",
        "suggest": "MRIO/mrio-extractor",
        "aliases": [],
    },
    "osm-extractor": {
        "url": "https://github.com/ccolon/osm-extractor",
        "suggest": "transport/transnet/osm-extractor",
        "aliases": [],
    },
    "transnet-simp": {
        "url": "https://github.com/ccolon/transnet-simp",
        "suggest": "transport/transnet/transnet-simp",
        "aliases": [],
    },
    "multi-tn-build": {
        "url": "https://github.com/ccolon/multi-tn-build",
        "suggest": "transport/transnet/multitnbuild",
        "aliases": ["multitnbuild"],
    },
}


def find_repo_root(start: Path | None = None) -> Path:
    p = (start or Path(__file__)).resolve()
    for cand in [p, *p.parents]:
        if (cand / "pyproject.toml").exists() and (cand / "src" / "disruptsc").is_dir():
            return cand
    raise FileNotFoundError(f"disrupt-sc repo root not found above {p}")


def disruptsc_parent() -> Path:
    return find_repo_root().parent


def data_root() -> Path:
    env = os.environ.get("DISRUPT_SC_DATA_PATH")
    return Path(env) if env else disruptsc_parent() / "disrupt-sc-data"


def mrio_root() -> Path:
    return disruptsc_parent() / "MRIO"


def find_tool_repo(name: str) -> Path | None:
    """Search close locations for a tool repo; None if absent (then clone_hint)."""
    spec = TOOL_REPOS[name]
    parent = disruptsc_parent()
    names = [name] + spec["aliases"]
    bases = [parent, parent / "MRIO", parent / "transport",
             parent / "transport" / "transnet", parent / "tools"]
    for base in bases:
        for n in names:
            p = base / n
            if p.is_dir():
                return p
    return None


def clone_hint(name: str) -> str:
    spec = TOOL_REPOS[name]
    dest = disruptsc_parent() / spec["suggest"]
    return f'git clone {spec["url"]} "{dest}"'
