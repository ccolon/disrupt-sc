"""Write the `.fp.json` sidecars that `--cache auto` needs next to cache pickles
written before that feature existed (disrupt-sc < 7445edb).

The sidecar carries the stage hash of the configuration the pickle was built
under. This script TRUSTS that the pickles on disk were built with the CURRENT
configuration of the scope (plus --seed) and stamps them with the current
stage hashes - use it once, right after a full run of that configuration.
Pickles whose embedded fingerprint disagrees are refused at load time anyway.

Usage:
    python cache_sidecars.py <Scope> [--seed 42]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

sys.path.insert(0, str(locate.find_repo_root() / "src"))

from disruptsc.config import load_config  # noqa: E402
from disruptsc.run_pipeline.cache import CACHE_LEVELS, _pkl, _sidecar  # noqa: E402
from disruptsc.run_pipeline.fingerprint import build_stage_fingerprint  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scope")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    config = load_config(args.scope)
    if args.seed is not None:
        config["seed"] = args.seed
    for level in CACHE_LEVELS:
        path = _pkl(level, args.scope)
        if not path.exists():
            print(f"{level}: no pickle at {path.name}")
            continue
        fp = build_stage_fingerprint(config, level)
        with open(_sidecar(path), "w", encoding="utf-8") as f:
            json.dump({"hash": fp["hash"], "stage": level, "trusted_backfill": True}, f)
        print(f"{level}: sidecar written ({fp['hash'][:10]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
