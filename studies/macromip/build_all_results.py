"""Run the macroMIP adapter over every experiment in runs/macromip/.

Equivalent to running, for each run folder that contains a run_metadata.json:

    python -m disruptsc.reporting.macromip --run-dir runs/macromip/<exp>

and, optionally, collecting the per-experiment ``<id>-DisruptSC.csv`` files into a
single submission folder.

    python studies/macromip/build_all_results.py
    python studies/macromip/build_all_results.py --collect runs/macromip/DisruptSC
"""
from __future__ import annotations

import argparse
import shutil
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from disruptsc.reporting.macromip import build_macromip_table, _read_meta  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Build macroMIP result CSVs for all runs")
    p.add_argument("--runs-dir", type=Path, default=ROOT / "runs" / "macromip",
                   help="folder containing the per-experiment run subfolders")
    p.add_argument("--base-year", type=int, default=2017)
    p.add_argument("--model-name", default="DisruptSC")
    p.add_argument("--collect", type=Path, default=None,
                   help="also copy every produced CSV into this folder "
                        "(e.g. runs/macromip/DisruptSC for the submission)")
    args = p.parse_args()

    run_dirs = sorted(d.parent for d in args.runs_dir.glob("*/run_metadata.json"))
    if not run_dirs:
        raise SystemExit(f"No runs found under {args.runs_dir} "
                         f"(expected per-experiment subfolders with run_metadata.json).")

    produced, failed = [], []
    for rd in run_dirs:
        try:
            meta = _read_meta(rd)
            table = build_macromip_table(rd, base_year=args.base_year,
                                         model_name=args.model_name)
            exp_id = meta.get("protocol_identifier", rd.name)
            out = rd / f"{exp_id}-{args.model_name}.csv"
            table.to_csv(out, index=False)
            produced.append(out)
            print(f"[ok]   {rd.name:8} -> {out.name:24} ({len(table):>6} rows)")
        except Exception as exc:  # noqa: BLE001 — keep going on a bad experiment
            failed.append(rd.name)
            print(f"[FAIL] {rd.name:8} : {exc}")
            traceback.print_exc()

    if args.collect and produced:
        args.collect.mkdir(parents=True, exist_ok=True)
        for f in produced:
            shutil.copy2(f, args.collect / f.name)
        print(f"\nCollected {len(produced)} CSV(s) into {args.collect}/")

    print(f"\nDone: {len(produced)} built"
          + (f", {len(failed)} failed ({', '.join(failed)})" if failed else ""))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
