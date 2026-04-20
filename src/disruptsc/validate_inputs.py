"""Lightweight input-file validation for the v2 runtime."""

from __future__ import annotations

import argparse
from pathlib import Path

from disruptsc import paths
from disruptsc.config import load_config

ALWAYS_REQUIRED_FILEPATHS = (
    "mrio",
    "sector_table",
    "households_spatial",
    "countries_spatial",
    "firms_spatial",
)


def validate_scope(scope: str) -> tuple[bool, list[str], list[str]]:
    """Validate that the configured input files for a scope exist."""
    errors: list[str] = []
    warnings: list[str] = []

    parameter_file = paths.PARAMETER_FOLDER / f"user_defined_{scope}.yaml"
    if not parameter_file.exists():
        warnings.append(f"No scope-specific parameter file found: {parameter_file}")

    data_path = paths.get_data_path(scope)
    if not data_path.exists():
        errors.append(f"Data folder not found: {data_path}")

    try:
        config = load_config(scope)
    except Exception as exc:
        return False, [f"Could not load configuration for '{scope}': {exc}"], warnings

    filepaths = config.get("filepaths", {})
    required = list(ALWAYS_REQUIRED_FILEPATHS)
    if config.get("with_transport", True):
        required.append("transport")

    for key in required:
        path = filepaths.get(key)
        if path is None:
            errors.append(f"Missing required filepaths entry: {key}")
        elif not Path(path).exists():
            errors.append(f"Missing required file for '{key}': {path}")

    return not errors, errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate DisruptSC input files")
    parser.add_argument("scope", help="Scope to validate, e.g. Testkistan or Cambodia")
    args = parser.parse_args(argv)

    ok, errors, warnings = validate_scope(args.scope)
    print(f"Default data root: {paths.get_data_root()}")
    print(f"Scope data: {paths.get_data_path(args.scope)}")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"\nValidation passed for {args.scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
