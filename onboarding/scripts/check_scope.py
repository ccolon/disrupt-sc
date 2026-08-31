"""Deep validation of a DisruptSC scope - the checks `validate-inputs` does NOT do.

Usage:
    python check_scope.py <Scope> [--economic-only] [--data-root <path>]

Checks: MRIO squareness and label classification, reserved-word collisions in sector
names, sector-table completeness and type consistency, countries.geojson <-> MRIO bloc
match, per-mode and combined transport connectivity, config coverage (speeds, costs,
dwell times), Transport folder size budget.

Exit code 0 = no errors (warnings possible), 1 = at least one ERROR.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import pandas as pd

try:
    import yaml
except ImportError:
    yaml = None

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import locate  # noqa: E402

REPO_ROOT = str(locate.find_repo_root())
DISRUPTSC_PARENT = str(locate.disruptsc_parent())

# Same regexes as src/disruptsc/network/mrio.py:434 (_detect_label), case-insensitive search
LABEL_REGEXES = {
    "export": r"export",
    "final demand": r"final.?demand|household",
    "government": r"government",
    "capital": r"capital|investment",
    "import": r"import",
    "value added": r"value.?added|va",
    "tax": r"tax",
}
COL_LABELS = ("export", "final demand", "government", "capital")
ROW_LABELS = ("import", "value added", "tax")

VALID_TYPES = {"agriculture", "mining", "oil_and_gas", "manufacturing", "utility",
               "transport", "trade", "service", "services", "construction"}
PHYSICAL_TYPES = {"agriculture", "mining", "oil_and_gas", "manufacturing"}

MESSAGES: list[tuple[str, str]] = []


def note(level: str, msg: str) -> None:
    MESSAGES.append((level, msg))
    print(f"{level}: {msg}")


def classify(label: str, candidates: tuple[str, ...]) -> str | None:
    for name in candidates:
        if re.search(LABEL_REGEXES[name], str(label), re.IGNORECASE):
            return name
    return None


def merge_dicts(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        out[k] = merge_dicts(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(scope: str) -> dict:
    if yaml is None:
        note("WARN", "PyYAML unavailable - config-dependent checks skipped")
        return {}
    cfg: dict = {}
    for name in ("default.yaml", f"user_defined_{scope}.yaml", f"user_defined_{scope}.local.yaml"):
        path = os.path.join(REPO_ROOT, "config", name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cfg = merge_dicts(cfg, yaml.safe_load(f) or {})
        elif name == "default.yaml":
            note("WARN", f"config/default.yaml not found at {path}")
    if not any(os.path.exists(os.path.join(REPO_ROOT, "config", n))
               for n in (f"user_defined_{scope}.yaml", f"user_defined_{scope}.local.yaml")):
        note("WARN", f"no user_defined_{scope}[.local].yaml - the model would run on pure defaults")
    return cfg


def check_economic(paths: dict):
    """Returns (internal_regions, blocs, sector_names) or (None, None, None)."""
    mrio_path = paths["mrio"]
    st_path = paths["sector_table"]
    if not os.path.exists(mrio_path):
        note("ERROR", f"missing {mrio_path}")
        return None, None, None

    mrio = pd.read_csv(mrio_path, header=[0, 1], index_col=[0, 1])
    sector_cols = [(a, b) for a, b in mrio.columns if classify(b, COL_LABELS) is None]
    export_cols = [(a, b) for a, b in mrio.columns if classify(b, COL_LABELS) == "export"]
    fd_cols = [(a, b) for a, b in mrio.columns if classify(b, COL_LABELS) in ("final demand", "government", "capital")]
    # External blocs own an exports column; their rows are import-supply rows
    # in BOTH formats (legacy single (BLOC, "imports") row, or sector-resolved
    # (BLOC, sector) rows) and must not count as intermediary sector rows.
    ext_regions = {a for a, _ in export_cols}
    sector_rows = [(a, b) for a, b in mrio.index
                   if classify(b, ROW_LABELS) is None and a not in ext_regions]
    import_rows = [(a, b) for a, b in mrio.index
                   if classify(b, ROW_LABELS) == "import"
                   or (a in ext_regions and classify(b, ROW_LABELS) is None)]
    va_rows = [(a, b) for a, b in mrio.index if classify(b, ROW_LABELS) == "value added"]

    internal = sorted({a for a, _ in sector_cols})
    blocs = sorted({a for a, _ in export_cols} | {a for a, _ in import_rows})
    sectors = sorted({b for _, b in sector_cols})
    print(f"MRIO: {len(internal)} internal regions {internal}, {len(sectors)} sectors, "
          f"{len(blocs)} external blocs {blocs}")

    if sorted(sector_rows) != sorted(sector_cols):
        only_rows = sorted(set(sector_rows) - set(sector_cols))[:10]
        only_cols = sorted(set(sector_cols) - set(sector_rows))[:10]
        note("ERROR", f"intermediary not square: {len(sector_rows)} sector rows vs {len(sector_cols)} "
                      f"cols; row-only {only_rows}, col-only {only_cols}")
    if not fd_cols:
        note("ERROR", "no final-demand column detected - zero household demand, degenerate model")
    else:
        fd_regions = {a for a, _ in fd_cols}
        missing_fd = sorted(set(internal) - fd_regions)
        if missing_fd:
            note("WARN", f"internal regions without a final-demand column: {missing_fd}")
    imp_set, exp_set = {a for a, _ in import_rows}, {a for a, _ in export_cols}
    if imp_set != exp_set:
        note("WARN", f"import-row blocs {sorted(imp_set)} != export-col blocs {sorted(exp_set)}")
    if not va_rows:
        note("WARN", "no value-added row detected")
    if any("_" in r for r in internal):
        note("ERROR", f"region codes containing '_' (breaks region_sector split): "
                      f"{[r for r in internal if '_' in r]}")

    inter = mrio.loc[sector_rows, sector_cols]
    n_neg = int((inter.to_numpy() < 0).sum())
    if n_neg:
        note("WARN", f"{n_neg} negative cells in the intermediary matrix")

    # Reserved-word collisions: every intended sector name vs every loader regex
    for s in sectors:
        for name, rx in LABEL_REGEXES.items():
            if re.search(rx, s, re.IGNORECASE):
                note("ERROR", f"sector name '{s}' matches the loader's '{name}' regex ('{rx}') - "
                              "it will be misclassified; rename the sector (KI-12)")

    if not os.path.exists(st_path):
        note("ERROR", f"missing {st_path}")
        return internal, blocs, sectors
    st = pd.read_csv(st_path)
    for col in ("region", "sector", "type"):
        if col not in st.columns:
            note("ERROR", f"sector_table missing required column '{col}'")
            return internal, blocs, sectors
    mrio_rs = {(a, b) for a, b in sector_cols}
    st_rs = set(zip(st["region"], st["sector"]))
    missing = sorted(mrio_rs - st_rs)
    extra = sorted(st_rs - mrio_rs)
    if missing:
        note("ERROR", f"sector_table lacks {len(missing)} MRIO region_sectors, e.g. {missing[:5]}")
    if extra:
        note("WARN", f"sector_table has {len(extra)} rows absent from the MRIO, e.g. {extra[:5]}")
    conflicts = st.groupby("sector")["type"].nunique()
    conflicts = conflicts[conflicts > 1].index.tolist()
    if conflicts:
        note("ERROR", f"sector type differs across regions for: {conflicts} "
                      "(the model keeps the first occurrence)")
    bad_types = sorted(set(st["type"].dropna()) - VALID_TYPES)
    if bad_types:
        note("WARN", f"unrecognized sector types: {bad_types} (valid: {sorted(VALID_TYPES)})")
    if "usd_per_ton" in st.columns:
        phys = st[st["type"].isin(PHYSICAL_TYPES)]
        n_missing = int(phys["usd_per_ton"].isna().sum())
        if n_missing:
            note("WARN", f"{n_missing} physical-type sectors without usd_per_ton "
                         "(model falls back to 2864 USD/ton)")
    else:
        note("WARN", "sector_table has no usd_per_ton column - all tonnages use the 2864 default")
    return internal, blocs, sectors


def check_spatial(paths: dict, internal, blocs, sectors):
    import geopandas as gpd

    cpath = paths["countries_spatial"]
    if blocs is not None and not blocs:
        print("MRIO has no external blocs (closed world) - countries.geojson not required")
    elif not os.path.exists(cpath):
        note("ERROR", f"missing {cpath}")
    elif blocs is not None:
        c = gpd.read_file(cpath)
        if "region" not in c.columns:
            note("ERROR", "countries.geojson has no 'region' property")
        else:
            got = set(c["region"].astype(str))
            missing = sorted(set(blocs) - got)
            extra = sorted(got - set(blocs))
            if missing:
                note("ERROR", f"countries.geojson lacks MRIO bloc(s) {missing} - hard runtime failure")
            if extra:
                note("WARN", f"countries.geojson has non-MRIO regions {extra} (ignored)")

    hpath = paths["households_spatial"]
    if not os.path.exists(hpath):
        note("ERROR", f"missing {hpath}")
    else:
        h = gpd.read_file(hpath)
        if "region" not in h.columns:
            note("ERROR", "households.geojson has no 'region' property")
        elif internal is not None:
            stray = sorted(set(h["region"].astype(str)) - set(internal))
            if stray:
                note("WARN", f"households with regions not in the MRIO (silently dropped): {stray}")
            missing = sorted(set(internal) - set(h["region"].astype(str)))
            if missing:
                note("ERROR", f"internal regions with no household point: {missing}")
        if "population" not in h.columns:
            note("WARN", "households.geojson has no 'population' - demand split defaults to uniform")

    fpath = paths["firms_spatial"]
    if not os.path.exists(fpath):
        note("ERROR", f"missing {fpath}")
    elif sectors is not None:
        fgdf = gpd.read_file(fpath)
        wide = set(fgdf.columns) & set(sectors)
        long_form = {"region", "sector"} <= set(fgdf.columns) or "region_sector" in fgdf.columns
        if wide:
            print(f"firms.geojson: wide form, {len(wide)}/{len(sectors)} sector columns match the MRIO")
            if len(wide) < len(sectors):
                note("WARN", f"MRIO sectors with no firms column: {sorted(set(sectors) - wide)[:10]}")
        elif long_form:
            print("firms.geojson: long form (region+sector)")
        else:
            note("ERROR", "firms.geojson matches neither wide (sector columns) nor long "
                          "(region+sector) form - all firms would collapse to region centroids")


class UnionFind:
    def __init__(self):
        self.parent: dict = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def _endpoints(gdf) -> list[tuple]:
    pairs = []
    for geom in gdf.geometry:
        if geom is None or geom.geom_type != "LineString":
            continue
        c0, c1 = geom.coords[0], geom.coords[-1]
        pairs.append(((round(c0[0], 6), round(c0[1], 6)), (round(c1[0], 6), round(c1[1], 6))))
    return pairs


def _components(edge_pairs: list[tuple]) -> list[int]:
    uf = UnionFind()
    for a, b in edge_pairs:
        uf.union(a, b)
    sizes: dict = {}
    for node in list(uf.parent):
        root = uf.find(node)
        sizes[root] = sizes.get(root, 0) + 1
    return sorted(sizes.values(), reverse=True)


def check_transport(scope_dir: str, cfg: dict, paths: dict):
    import geopandas as gpd

    modes = cfg.get("transport_modes", ["roads", "maritime"])
    tpath = paths["transport"]
    if not os.path.exists(tpath):
        note("ERROR", f"missing {tpath}")
        return
    layers = set(gpd.list_layers(tpath)["name"])
    print(f"transport.gpkg layers: {sorted(layers)}; configured modes: {modes}")

    all_pairs = []
    for mode in modes:
        if mode not in layers:
            note("WARN", f"mode '{mode}' has no layer in transport.gpkg (model skips it silently)")
            continue
        gdf = gpd.read_file(tpath, layer=mode)
        non_ls = int((gdf.geometry.geom_type != "LineString").sum())
        if non_ls:
            note("ERROR", f"layer '{mode}': {non_ls} non-LineString geometries")
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            note("ERROR", f"layer '{mode}': CRS is {gdf.crs}, expected EPSG:4326")
        pairs = _endpoints(gdf)
        comp = _components(pairs)
        if len(comp) > 1:
            note("WARN", f"layer '{mode}': {len(comp)} connected components "
                         f"(node counts {comp[:5]}{'...' if len(comp) > 5 else ''})")
        else:
            print(f"layer '{mode}': {len(gdf)} edges, single connected component")
        all_pairs.extend(pairs)

    mm_path = paths["multimodal"]
    mm = None
    if os.path.exists(mm_path):
        mm = gpd.read_file(mm_path, layer="multimodal")
    elif "multimodal" in layers:
        mm = gpd.read_file(tpath, layer="multimodal")
    elif len([m for m in modes if m in layers]) > 1:
        note("ERROR", "multiple modes enabled but no multimodal layer/file - modes cannot interconnect")

    if mm is not None:
        all_pairs.extend(_endpoints(mm))
        if "multimodes" in mm.columns:
            mm_strings = sorted(set(mm["multimodes"].dropna().astype(str)))
            dwell = (cfg.get("logistics") or {}).get("dwell_times") or {}
            fees = (cfg.get("logistics") or {}).get("loading_fees") or {}
            for s in mm_strings:
                if s not in dwell:
                    note("WARN", f"multimodes '{s}' has no logistics.dwell_times entry")
                if s not in fees:
                    note("WARN", f"multimodes '{s}' has no logistics.loading_fees entry")
                # qualifiers like 'roads-maritime-fujairah' are fine; the model keeps a
                # connector as long as its string references at least one enabled mode
                tokens = [t for t in s.split("-") if t]
                if not any(t in modes or t == "roads" for t in tokens):
                    note("WARN", f"multimodes '{s}' references no enabled mode - "
                                 "connector dropped by the model")
        else:
            note("ERROR", "multimodal layer has no 'multimodes' column - all connectors filtered out")

    comp = _components(all_pairs)
    if len(comp) > 1:
        share = comp[0] / sum(comp)
        detail = (f"combined network (all modes + multimodal) has {len(comp)} components "
                  f"(node counts {comp[:5]}{'...' if len(comp) > 5 else ''})")
        if share < 0.9:
            note("ERROR", detail + " - the network is badly split; routing will fail")
        else:
            note("WARN", detail + " - small islands are only fatal if an agent or "
                                  "country point snaps onto one")
    elif comp:
        print(f"combined network: single connected component ({comp[0]} nodes)")

    logistics = cfg.get("logistics") or {}
    for mode in modes:
        if mode not in (logistics.get("speeds") or {}):
            note("WARN", f"no logistics.speeds entry for '{mode}' (silent default 50 km/h)")
        if mode not in (logistics.get("basic_cost") or {}):
            note("WARN", f"no logistics.basic_cost entry for '{mode}' (silent default 0.01/t-km)")

    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, files in os.walk(os.path.join(scope_dir, "Transport")) for f in files)
    line = f"Transport folder size: {total / 1e6:,.1f} MB"
    if total > 50e6:
        note("WARN", line + " - exceeds the 50 MB budget; consider stronger clustering "
                            "or a higher road-level threshold")
    else:
        print(line + " (within the 50 MB budget)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scope")
    ap.add_argument("--economic-only", action="store_true")
    ap.add_argument("--data-root", default=os.environ.get(
        "DISRUPT_SC_DATA_PATH", os.path.join(DISRUPTSC_PARENT, "disrupt-sc-data")))
    args = ap.parse_args()

    scope_dir = os.path.join(args.data_root, args.scope)
    if not os.path.isdir(scope_dir):
        print(f"ERROR: scope folder not found: {scope_dir}", file=sys.stderr)
        return 1
    print(f"Checking scope '{args.scope}' at {scope_dir}\n")

    cfg = load_config(args.scope)
    defaults = {
        "mrio": "Economic/mrio.csv",
        "sector_table": "Economic/sector_table.csv",
        "households_spatial": "Spatial/households.geojson",
        "firms_spatial": "Spatial/firms.geojson",
        "countries_spatial": "Spatial/countries.geojson",
        "transport": "Transport/transport.gpkg",
        "multimodal": "Transport/multimodal.gpkg",
    }
    fp = cfg.get("filepaths") or {}
    paths = {}
    for key, default_rel in defaults.items():
        rel = fp.get(key)
        rel = default_rel if rel in (None, "None") else rel
        paths[key] = os.path.join(scope_dir, rel)

    internal, blocs, sectors = check_economic(paths)
    if not args.economic_only:
        check_spatial(paths, internal, blocs, sectors)
        if cfg.get("with_transport", True):
            check_transport(scope_dir, cfg, paths)
        else:
            print("with_transport: false - transport checks skipped")

    n_err = sum(1 for lvl, _ in MESSAGES if lvl == "ERROR")
    n_warn = sum(1 for lvl, _ in MESSAGES if lvl == "WARN")
    print(f"\nSummary: {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
