"""Input validation for the v2 runtime.

Checks the *content* of a scope's inputs, not just their existence: config
consistency, sector-table columns and values, MRIO structure and labels,
spatial-file geometry and cross-references, transport layers, and the
disruption block. Every check is independent — one broken file doesn't hide
the others — and each returns errors (would break or silently corrupt a
run) or warnings (suspicious but survivable).

CLI:  validate-inputs <scope>
"""

from __future__ import annotations

import argparse
from pathlib import Path

from disruptsc import paths
from disruptsc.config import load_config, build_params, resolve_repo_prefix

ALWAYS_REQUIRED_FILEPATHS = (
    "mrio",
    "sector_table",
    "households_spatial",
    "countries_spatial",
    "firms_spatial",
)

_VALID_UNITS = ("USD", "kUSD", "mUSD")
_VALID_TIME_RESOLUTIONS = ("day", "week", "month", "year")
_KNOWN_DISRUPTION_TYPES = (
    "transport_disruption", "transport_disruption_probability",
    "capital_destruction", "productivity_shock",
)


def validate_scope(scope: str) -> tuple[bool, list[str], list[str]]:
    """Validate the configured inputs for *scope*. Returns (ok, errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    shared = paths.PARAMETER_FOLDER / f"user_defined_{scope}.yaml"
    local = paths.PARAMETER_FOLDER / f"user_defined_{scope}.local.yaml"
    if not shared.exists() and not local.exists():
        warnings.append(
            f"No scope parameter file found ({shared.name} or {local.name}); "
            f"defaults only."
        )

    # A missing scope folder is only a WARNING: some scopes (e.g. EcuadorEQ)
    # deliberately point every filepath into a sibling scope's folder. The
    # real signal is whether the configured files resolve (_check_files_exist).
    data_path = paths.get_data_path(scope)
    if not data_path.exists():
        warnings.append(
            f"Scope data folder not found ({data_path}) — fine if every "
            f"configured filepath resolves elsewhere (relative ../ or repo: paths)"
        )

    try:
        config = load_config(scope)
    except Exception as exc:
        return False, [f"Could not load configuration for '{scope}': {exc}"], warnings

    _check_config(config, errors, warnings)
    _check_files_exist(config, errors)

    filepaths = config.get("filepaths", {})
    sector_table = _check_sector_table(filepaths.get("sector_table"), errors, warnings)
    mrio = _check_mrio(filepaths.get("mrio"), config, errors, warnings)
    _check_spatial(filepaths, config, mrio, errors, warnings)
    if config.get("with_transport", True):
        _check_transport(filepaths, config, errors, warnings)
    _check_input_criticality(filepaths.get("input_criticality"), sector_table,
                             errors, warnings)
    _check_disruptions(config, errors, warnings)

    return not errors, errors, warnings


# ----------------------------------------------------------------------
# Individual checks (each swallows its own unexpected exceptions into errors)
# ----------------------------------------------------------------------

def _check_config(config: dict, errors: list, warnings: list) -> None:
    try:
        build_params(config)   # raises on bad capacity_constraint, rationing_mode, flow_coverage…
    except Exception as exc:
        errors.append(f"Config does not build valid parameters: {exc}")
    for key in ("monetary_units_in_model", "monetary_units_in_data"):
        val = config.get(key, "mUSD")
        if val not in _VALID_UNITS:
            errors.append(f"{key}={val!r} is not one of {_VALID_UNITS}")
    tr = config.get("time_resolution", "week")
    if tr not in _VALID_TIME_RESOLUTIONS:
        errors.append(f"time_resolution={tr!r} is not one of {_VALID_TIME_RESOLUTIONS}")


def _check_files_exist(config: dict, errors: list) -> None:
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


def _check_sector_table(path, errors: list, warnings: list):
    if not path or not Path(path).exists():
        return None
    import pandas as pd
    try:
        table = pd.read_csv(path)
    except Exception as exc:
        errors.append(f"sector_table unreadable: {exc}")
        return None
    for col in ("region", "sector", "type"):
        if col not in table.columns:
            errors.append(f"sector_table missing required column '{col}'")
    if {"region", "sector"} <= set(table.columns):
        dups = table.duplicated(["region", "sector"]).sum()
        if dups:
            warnings.append(f"sector_table has {dups} duplicated (region, sector) rows")
    if "usd_per_ton" not in table.columns:
        warnings.append(
            "sector_table has no 'usd_per_ton' column — tons conversions fall "
            "back to the 2864 USD/ton default everywhere"
        )
    else:
        bad = (table["usd_per_ton"].dropna() <= 0).sum()
        if bad:
            errors.append(f"sector_table: {bad} usd_per_ton value(s) are <= 0")
    return table


def _check_mrio(path, config: dict, errors: list, warnings: list):
    if not path or not Path(path).exists():
        return None
    from disruptsc.network.mrio import Mrio
    try:
        mrio = Mrio.load(path, monetary_units=config.get("monetary_units_in_data", "mUSD"))
    except Exception as exc:
        errors.append(f"MRIO failed to load/parse (structure problem?): {exc}")
        return None
    if not mrio.import_label and not mrio.external_selling_countries:
        errors.append("MRIO: no import supply detected (neither an 'imports' row label "
                      "nor sector-resolved external-region rows)")
    if not mrio.export_label:
        errors.append("MRIO: no export column label detected (level-1 matching 'export')")
    if not mrio.final_demand_label:
        errors.append("MRIO: no final-demand column label detected "
                      "(level-1 matching 'final_demand' or 'household')")
    if not mrio.value_added_label:
        warnings.append("MRIO: no value-added row — margins default to 20% uniformly")
    try:
        n_neg = int((mrio.values < 0).sum())
        if n_neg:
            warnings.append(f"MRIO contains {n_neg} negative cell(s)")
        output = mrio.get_total_output()
        inp = mrio.get_total_input()
        unbalanced = int((inp > output + 1e-9).sum())
        if unbalanced:
            warnings.append(
                f"MRIO: {unbalanced} region_sector(s) have input > output — "
                f"the model will silently pad their exports to balance "
                f"(Mrio._adjust_output)"
            )
    except Exception as exc:
        warnings.append(f"MRIO balance checks skipped: {exc}")
    return mrio


def _check_spatial(filepaths: dict, config: dict, mrio, errors: list, warnings: list) -> None:
    import geopandas as gpd

    def _load(key):
        path = filepaths.get(key)
        if not path or not Path(path).exists():
            return None
        try:
            return gpd.read_file(path)
        except Exception as exc:
            errors.append(f"{key} unreadable: {exc}")
            return None

    hh = _load("households_spatial")
    if hh is not None:
        if "region" not in hh.columns:
            errors.append("households_spatial missing 'region' column")
        non_point = (~hh.geometry.geom_type.isin(["Point"])).sum()
        if non_point:
            errors.append(
                f"households_spatial: {non_point} non-Point geometrie(s) — "
                f"nearest-node assignment needs point locations"
            )
        if mrio is not None and "region" in hh.columns:
            hh_regions = set(hh["region"])
            overlap = hh_regions & set(mrio.regions)
            if not overlap:
                errors.append("households_spatial regions share NO region code with the MRIO")
            dropped = hh_regions - set(mrio.regions)
            if dropped:
                warnings.append(
                    f"households_spatial: {len(dropped)} region(s) absent from the "
                    f"MRIO are dropped: {sorted(dropped)[:5]}…"
                )

    firms = _load("firms_spatial")
    if firms is not None:
        non_point = (~firms.geometry.geom_type.isin(["Point"])).sum()
        if non_point:
            errors.append(f"firms_spatial: {non_point} non-Point geometrie(s)")
        long_ok = ("region_sector" in firms.columns
                   or {"region", "sector"} <= set(firms.columns))
        wide_ok = (mrio is not None and "region" in firms.columns
                   and any(c in set(mrio.sectors) for c in firms.columns))
        if not long_ok and not wide_ok:
            warnings.append(
                "firms_spatial has neither region_sector / region+sector columns "
                "nor wide-format sector columns matching the MRIO — spatial "
                "disaggregation will be skipped"
            )

    countries = _load("countries_spatial")
    if countries is not None and mrio is not None:
        if "region" not in countries.columns:
            errors.append("countries_spatial missing 'region' column")
        else:
            present = set(countries["region"])
            virtual = set(config.get("countries_no_transport") or ())
            mrio_countries = set(mrio.external_buying_countries) | set(mrio.external_selling_countries)
            missing = sorted(mrio_countries - present - virtual)
            if missing:
                errors.append(
                    f"Countries in the MRIO but absent from countries_spatial and "
                    f"not listed in countries_no_transport: {missing} — "
                    f"create_countries will raise"
                )


def _check_transport(filepaths: dict, config: dict, errors: list, warnings: list) -> None:
    import geopandas as gpd
    path = filepaths.get("transport")
    if not path or not Path(path).exists():
        return
    try:
        layers = set(gpd.list_layers(path)["name"])
    except Exception as exc:
        errors.append(f"transport gpkg unreadable: {exc}")
        return
    modes = [m for m in config.get("transport_modes", ["roads"]) if m != "multimodal"]
    missing = [m for m in modes if m not in layers]
    if missing:
        warnings.append(
            f"transport gpkg lacks layer(s) for configured mode(s) {missing} "
            f"(available: {sorted(layers)})"
        )
    for mode in modes[:1]:  # geometry spot-check on the first present mode
        if mode not in layers:
            continue
        try:
            gdf = gpd.read_file(path, layer=mode, rows=200)
            bad = (~gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])).sum()
            if bad:
                errors.append(f"transport layer '{mode}': {bad} non-LineString geometrie(s) in sample")
        except Exception as exc:
            warnings.append(f"transport layer '{mode}' spot-check skipped: {exc}")


def _check_input_criticality(path, sector_table, errors: list, warnings: list) -> None:
    if not path or not Path(path).exists():
        return
    import pandas as pd
    try:
        crit = pd.read_csv(path, index_col=0)
    except Exception as exc:
        errors.append(f"input_criticality unreadable: {exc}")
        return
    vals = set(crit.values.ravel())
    unexpected = {v for v in vals if v not in (0.0, 0.5, 1.0)}
    if unexpected:
        warnings.append(
            f"input_criticality contains values outside {{0, 0.5, 1}}: "
            f"{sorted(unexpected)[:5]}"
        )
    if sector_table is not None and "sector" in sector_table.columns:
        sectors = set(sector_table["sector"])
        unknown = sorted(set(crit.columns) - sectors)
        if unknown:
            warnings.append(
                f"input_criticality: {len(unknown)} column sector(s) not in the "
                f"sector_table: {unknown[:5]}…"
            )


def _check_disruptions(config: dict, errors: list, warnings: list) -> None:
    disruptions = config.get("disruptions") or []
    for i, cfg in enumerate(disruptions):
        dtype = cfg.get("type", "")
        if dtype not in _KNOWN_DISRUPTION_TYPES:
            errors.append(f"disruptions[{i}]: unknown type {dtype!r}")
            continue
        if dtype == "capital_destruction" and cfg.get("description_type") in ("subregion_file", "file"):
            shock = resolve_repo_prefix(cfg.get("file", ""))
            if not shock or not Path(shock).exists():
                errors.append(f"disruptions[{i}]: shock file not found: {shock}")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

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
