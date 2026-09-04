"""Re-stamp the stage fingerprints of existing cache pickles after a fingerprint-key change.

When a config key is REMOVED from a stage's cache fingerprint (because it turned out not to
shape what the stage builds - e.g. `critical_input_threshold`, re-applied on every load), the
stored hashes no longer match and `--cache auto` rebuilds everything once. If the pickles'
content is known to be valid for the current config, this script rewrites their stored
fingerprint (and the .fp.json sidecar) with the current one instead of rebuilding.

Only use it when you can argue that the cached content is unaffected by the key change; the
script cannot check that. It re-pickles each stage (a few minutes for the EU routes pickle).

Usage:  python onboarding/scripts/restamp_caches.py EU --seed 42 [--stages agents,sc_network,logistic_routes]
"""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from disruptsc.config import load_config  # noqa: E402
from disruptsc.run_pipeline.cache import CACHE_LEVELS, _pkl, save_cache  # noqa: E402
from disruptsc.run_pipeline.fingerprint import build_stage_fingerprint  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scope")
    ap.add_argument("--seed", type=int, default=None, help="seed the runs use (part of the sc_network fingerprint)")
    ap.add_argument("--stages", default=",".join(CACHE_LEVELS))
    args = ap.parse_args()

    config = load_config(args.scope)
    if args.seed is not None:
        config["seed"] = args.seed
    for stage in args.stages.split(","):
        path = _pkl(stage, args.scope)
        if not path.exists():
            print(f"{stage}: no pickle at {path} - skipped")
            continue
        new_fp = build_stage_fingerprint(config, stage)
        with open(path, "rb") as f:
            raw = pickle.load(f)
        if isinstance(raw, dict) and raw.get("__cache_format__") == 2:
            data, stored = raw["data"], raw.get("fingerprint") or {}
        else:
            data, stored = raw, {}
        if stored.get("hash") == new_fp["hash"]:
            print(f"{stage}: fingerprint already current ({new_fp['hash'][:8]})")
            continue
        save_cache(stage, data, scope=args.scope, stage_fp=new_fp)
        print(f"{stage}: {str(stored.get('hash', '?'))[:8]} -> {new_fp['hash'][:8]} re-stamped ({path.stat().st_size/1e6:,.0f} MB)")


if __name__ == "__main__":
    main()
