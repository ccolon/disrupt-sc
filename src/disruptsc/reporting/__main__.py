"""CLI entry point: python -m disruptsc.reporting initial_state output/Gulf/20260401_095732"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate analysis reports from DisruptSC output folders",
    )
    sub = parser.add_subparsers(dest="report_type", required=True)

    # --- initial_state ---
    p_init = sub.add_parser("initial_state", help="Initial-state equilibrium report")
    p_init.add_argument("output_folder", type=Path, help="Path to a run output folder")
    p_init.add_argument("--open", action="store_true", help="Open report in browser")

    # --- disruption ---
    p_dis = sub.add_parser("disruption", help="Disruption scenario report")
    p_dis.add_argument("output_folder", type=Path, help="Path to a run output folder")
    p_dis.add_argument("--open", action="store_true", help="Open report in browser")

    args = parser.parse_args()

    if args.report_type == "initial_state":
        from disruptsc.reporting.initial_state import generate_report
    elif args.report_type == "disruption":
        from disruptsc.reporting.disruption import generate_report
    else:
        print(f"Unknown report type: {args.report_type}", file=sys.stderr)
        sys.exit(1)

    html_path = generate_report(args.output_folder)
    print(f"Report: {html_path}")
    if args.open:
        import webbrowser
        webbrowser.open(str(html_path))


if __name__ == "__main__":
    main()
