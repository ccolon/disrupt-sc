"""Reference full-export run for the paper figures (distribution + UQ DiD).

Runs the calibrated EcuadorEQ config at monthly t_final=13 (covers UQ's recovery
window tau 0-12) for one seed, exporting full firm/household data into
<out-root>/seed_<seed>/. One run per seed; the distribution and UQ figures average
the per-seed analyzer outputs (average_runs.py).

CLI:
    python run_reference.py --seed 0 --t-final 13 --out-root output/earthquake_paper/reference
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, setup_logging  # noqa: E402
from disruptsc.run import execute                        # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Reference full-export earthquake run (one seed)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--t-final", type=int, default=13)
    ap.add_argument("--out-root", type=Path, default=ROOT / "output" / "earthquake_paper" / "reference")
    ap.add_argument("--cache-isolation", action="store_true",
                    help="private per-process cache dir (avoids cross-scope clobbering on a cluster)")
    ap.add_argument("--shock", type=Path, default=None,
                    help="override disruptions[0].file (capital-destruction shock CSV)")
    ap.add_argument("--criticality", type=Path, default=None,
                    help="override filepaths.input_criticality (criticality matrix CSV)")
    args = ap.parse_args()

    setup_logging("info")
    cfg = load_config("EcuadorEQ")
    cfg["t_final"] = args.t_final          # 13 -> months 0..13 = tau -1..12
    cfg["seed"] = args.seed
    cfg["rationing_mode"] = "equal"
    cfg["export_files"] = True
    cfg["mc_repetitions"] = 0
    if args.shock:                         # keep data paths independent of the (cluster) config
        cfg["disruptions"][0]["file"] = str(args.shock)
    if args.criticality:
        cfg["filepaths"]["input_criticality"] = str(args.criticality)

    out = args.out_root / f"seed_{args.seed}"
    out.mkdir(parents=True, exist_ok=True)
    execute(cfg, export_folder=out, cache_isolation=args.cache_isolation)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
