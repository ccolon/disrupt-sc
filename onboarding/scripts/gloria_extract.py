"""Extract a closed region x sector table from GLORIA, driven by committed tables (KI-05).

Until 18 Nov 2026 a GLORIA extraction was an edit-in-place of the constants of
mrio-extractor/extract_mrio_gloria.py, so past selections could not be re-run
(KI-05: the Gulf selection was said lost). Here the selection is data: a YAML
spec (see onboarding/mrio_specs/gulf/*.yaml) points to

- a region membership table (one row per GLORIA region, one column per
  selection: the model region of each GLORIA code - every code assigned,
  nothing implicit),
- a sector concordance table (one row per GLORIA sector -> model sector),
- a model-sector table (type and usd_per_ton per model sector),

and the script writes, into --out-dir,

- the MRIO in the layout of the extractor (two header rows region / sector,
  two index columns; one "Final demand" column per region; one value-added
  row over all regions; values in kUSD, GLORIA's unit, rounded),
- the sector table (share_exporting_firms = output sold outside the region /
  output, from the rounded table, as generate_sector_table.py computes it;
  type and usd_per_ton from the model-sector table),
- a balance table (per region_sector: sales + final demand vs inputs + value
  added), and
- a provenance JSON (sha256 of the source pickle, of every table, of this
  script and of the outputs; git commit; package versions).

The arithmetic is that of extract_mrio_gloria.py (pandas groupby-sum over
rows, then over columns, then round), done over column chunks so that the
3.4 GB pickle is not copied whole; per-column sums do not depend on the
chunking, so the result is the same as the extractor's.

Source: <MRIO root>/GLORIA/mrio_va_fd.pkl (licensed data, not on GitHub; the
MRIO root is <parent of disrupt-sc>/MRIO, see locate.py). The pickle is the
product-by-industry use table of GLORIA (product rows x industry columns of
every region) with the value-added rows below and the final-demand columns
to the right, built by the prep scripts of the thesis-gloria repo
(jakobs_scripts/prep 01-03); its year and release are stated in the spec.

Run (env dsc), from the repo root:
    python onboarding/scripts/gloria_extract.py onboarding/mrio_specs/gulf/gulf19.yaml --out-dir <dir>
    [--compare-dir <folder with a reference mrio/sector table of the same names>]
--out-dir is required: the script never writes into a scope folder by default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate  # noqa: E402

VALUE_ADDED = [
    "Compensation of employees D.1", "Taxes on production D.29", "Subsidies on production D.39",
    "Net operating surplus B.2n", "Net mixed income B.3n", "Consumption of fixed capital K.1",
]
FINAL_DEMAND = [
    "Household final consumption P.3h", "Non-profit institutions serving households P.3n",
    "Government final consumption P.3g", "Gross fixed capital formation P.51",
    "Changes in inventories P.52", "Acquisitions less disposals of valuables P.53",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def git_state(path: Path) -> dict:
    root = locate.find_repo_root()
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", str(path)],
                               capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return {"git_head": None, "script_dirty": None}
    return {"git_head": head, "script_dirty": bool(dirty)}


def load_spec(spec_path: Path) -> dict:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    spec["_regions_table"] = base / spec["regions"]["table"]
    spec["_sectors_table"] = base / spec["sectors"]["table"]
    spec["_sectors_meta"] = base / spec["sectors"]["meta"]
    return spec


def build_maps(spec: dict, gloria_regions: list, gloria_sectors: list):
    reg = pd.read_csv(spec["_regions_table"], keep_default_na=False)
    col = spec["regions"]["column"]
    rmap = dict(zip(reg["gloria_code"], reg[col]))
    missing = [c for c in gloria_regions if c not in rmap or not rmap[c]]
    unknown = sorted(set(reg["gloria_code"]) - set(gloria_regions))
    if missing or unknown:
        raise ValueError(f"region table {col}: GLORIA codes without a model region {missing}; "
                         f"codes not in the source {unknown}")
    rorder = list(spec["regions"]["order"])
    if set(rorder) != set(rmap.values()):
        raise ValueError(f"regions.order {sorted(rorder)} != model regions of the table {sorted(set(rmap.values()))}")

    sec = pd.read_csv(spec["_sectors_table"], keep_default_na=False)
    scol = spec["sectors"]["column"]
    smap = dict(zip(sec["gloria_sector"], sec[scol]))
    missing = [s for s in gloria_sectors if s not in smap or not smap[s]]
    unknown = sorted(set(sec["gloria_sector"]) - set(gloria_sectors))
    if missing or unknown:
        raise ValueError(f"sector table: GLORIA sectors without a model sector {missing}; "
                         f"labels not in the source {unknown}")
    sorder = list(spec["sectors"]["order"])
    if set(sorder) != set(smap.values()):
        raise ValueError(f"sectors.order {sorted(sorder)} != model sectors of the table {sorted(set(smap.values()))}")
    return rmap, rorder, smap, sorder


def aggregate(df: pd.DataFrame, rmap: dict, rorder: list, smap: dict, sorder: list,
              va_row: tuple, fd_label: str, decimals: int, chunk: int = 1500) -> pd.DataFrame:
    rr = df.index.get_level_values(0)
    rs = df.index.get_level_values(1)
    cr = df.columns.get_level_values(0)
    cs = df.columns.get_level_values(1)
    is_va = rs.isin(VALUE_ADDED)
    is_fd = cs.isin(FINAL_DEMAND)
    bad_rows = sorted(set(rs[~is_va]) - set(smap))
    bad_cols = sorted(set(cs[~is_fd]) - set(smap))
    if bad_rows or bad_cols:
        raise ValueError(f"unmapped source labels: rows {bad_rows[:5]} cols {bad_cols[:5]}")
    row_reg = np.where(is_va, va_row[0], rr.map(rmap))
    row_sec = np.where(is_va, va_row[1], rs.map(smap))
    col_reg = np.asarray(cr.map(rmap))
    col_sec = np.where(is_fd, fd_label, cs.map(smap))
    df.index = pd.MultiIndex.from_arrays([row_reg, row_sec])

    parts = []
    for c0 in range(0, df.shape[1], chunk):
        sub = df.iloc[:, c0:c0 + chunk]
        parts.append(sub.groupby(level=[0, 1], sort=False).sum())
    rows_agg = pd.concat(parts, axis=1)
    rows_agg.columns = pd.MultiIndex.from_arrays([col_reg, col_sec])
    out = rows_agg.T.groupby(level=[0, 1], sort=False).sum().T

    row_idx = [(r, s) for r in rorder for s in sorder] + [tuple(va_row)]
    col_idx = [(r, s) for r in rorder for s in sorder] + [(r, fd_label) for r in rorder]
    out = out.reindex(index=pd.MultiIndex.from_tuples(row_idx), columns=pd.MultiIndex.from_tuples(col_idx),
                      fill_value=0.0)
    return out.round(decimals)


def sector_table(mrio: pd.DataFrame, rorder: list, sorder: list, meta: pd.DataFrame) -> pd.DataFrame:
    meta = meta.set_index("model_sector")
    rows = []
    for r in rorder:
        for s in sorder:
            row = mrio.loc[(r, s)]
            total = row.sum()
            domestic = row.loc[r].sum()
            share = round((total - domestic) / total, 4) if total > 0 else 0.0
            sec_type = meta.loc[s, "type"]
            usd = meta.loc[s, "usd_per_ton"]
            rows.append({"region_sector": f"{r}_{s}", "region": r, "sector": s, "share_exporting_firms": share,
                         "usd_per_ton": usd, "type": sec_type})
    out = pd.DataFrame(rows)
    out["usd_per_ton"] = out["usd_per_ton"].astype("Int64")
    return out


def balance(mrio: pd.DataFrame, rorder: list, sorder: list, va_row: tuple) -> pd.DataFrame:
    keys = [(r, s) for r in rorder for s in sorder]
    z = mrio.loc[keys, keys]
    sales = mrio.loc[keys].sum(axis=1)                  # intermediate sales + final demand
    inputs = z.sum(axis=0)                              # intermediate inputs
    va = mrio.loc[tuple(va_row), keys]
    cost = inputs + va                                  # inputs + value added
    b = pd.DataFrame({"region_sector": [f"{r}_{s}" for r, s in keys], "output_sales": sales.values,
                      "inputs": inputs.values, "value_added": va.values, "output_costs": cost.values})
    b["diff"] = b["output_sales"] - b["output_costs"]
    b["rel_diff"] = b["diff"] / b[["output_sales", "output_costs"]].abs().max(axis=1).replace(0, np.nan)
    b["inputs_gt_sales"] = b["inputs"] > b["output_sales"]
    return b


def compare(new: Path, ref: Path, kind: str) -> dict:
    res = {"reference": str(ref), "reference_sha256": sha256(ref), "output_sha256": sha256(new)}
    res["byte_identical"] = res["reference_sha256"] == res["output_sha256"]
    if kind == "mrio":
        a = pd.read_csv(new, header=[0, 1], index_col=[0, 1])
        b = pd.read_csv(ref, header=[0, 1], index_col=[0, 1])
        res["same_labels_and_order"] = bool(a.index.equals(b.index) and a.columns.equals(b.columns))
        if not res["same_labels_and_order"]:
            b = b.reindex(index=a.index, columns=a.columns)
        d = (a - b).abs()
        res["max_abs_diff_kUSD"] = float(np.nanmax(d.values))
        res["cells"] = int(d.size)
        res["cells_differing"] = int((d.values > 0).sum())
        res["cells_differing_gt_0.01"] = int((d.values > 0.010001).sum())
        tot_a, tot_b = float(np.nansum(a.values)), float(np.nansum(b.values))
        res["grand_total_new"], res["grand_total_ref"] = tot_a, tot_b
    else:
        a = pd.read_csv(new)
        b = pd.read_csv(ref)
        res["same_rows"] = bool(a["region_sector"].equals(b["region_sector"]))
        for c in ("share_exporting_firms", "usd_per_ton"):
            res[f"{c}_max_abs_diff"] = float((a[c] - b[c]).abs().max())
            res[f"{c}_rows_differing"] = int(((a[c] - b[c]).abs() > 0).sum())
        res["type_rows_differing"] = int((a["type"] != b["type"]).sum())
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--compare-dir", type=Path, default=None)
    ap.add_argument("--source", type=Path, default=None, help="override the spec's source pickle")
    args = ap.parse_args()

    t0 = time.time()
    spec = load_spec(args.spec)
    src = args.source or (locate.mrio_root() / spec["source"])
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    mrio_path = out_dir / spec["outputs"]["mrio"]
    st_path = out_dir / spec["outputs"]["sector_table"]
    stem = mrio_path.with_suffix("")
    va_row = tuple(spec["value_added_row"])
    fd_label = spec["final_demand_label"]

    print(f"spec {args.spec} ({spec['scope']}); source {src}")
    src_sha = sha256(src)
    print(f"  source sha256 {src_sha} ({src.stat().st_size:,} bytes)")
    df = pd.read_pickle(src)
    print(f"  loaded {df.shape} in {time.time() - t0:.0f}s")
    gloria_regions = list(pd.unique(df.index.get_level_values(0)))
    gloria_sectors = [s for s in pd.unique(df.index.get_level_values(1)) if s not in VALUE_ADDED]
    if list(pd.unique(df.columns.get_level_values(0))) != gloria_regions:
        raise ValueError("row and column region lists differ")
    rmap, rorder, smap, sorder = build_maps(spec, gloria_regions, gloria_sectors)
    print(f"  {len(gloria_regions)} GLORIA regions -> {len(rorder)} model regions; "
          f"{len(gloria_sectors)} GLORIA sectors -> {len(sorder)} model sectors")

    mrio = aggregate(df, rmap, rorder, smap, sorder, va_row, fd_label, int(spec["decimals"]))
    del df
    mrio.to_csv(mrio_path)
    print(f"  wrote {mrio_path} {mrio.shape} in {time.time() - t0:.0f}s")

    meta = pd.read_csv(spec["_sectors_meta"])
    mrio_rounded = pd.read_csv(mrio_path, header=[0, 1], index_col=[0, 1])  # as generate_sector_table.py reads it
    st = sector_table(mrio_rounded, rorder, sorder, meta)
    st.to_csv(st_path, index=False)
    bal = balance(mrio, rorder, sorder, va_row)
    bal_path = stem.parent / (stem.name + ".balance.csv")
    bal.to_csv(bal_path, index=False)

    world_sales, world_cost = bal["output_sales"].sum(), bal["output_costs"].sum()
    summary = {
        "region_sectors": len(bal),
        "world_output_sales_kUSD": float(world_sales),
        "world_output_costs_kUSD": float(world_cost),
        "world_rel_diff": float((world_sales - world_cost) / world_cost),
        "max_abs_rel_diff": float(bal["rel_diff"].abs().max()),
        "region_sector_max_abs_rel_diff": bal.loc[bal["rel_diff"].abs().idxmax(), "region_sector"],
        "n_abs_rel_diff_gt_1e-6": int((bal["rel_diff"].abs() > 1e-6).sum()),
        "n_abs_rel_diff_gt_1pct": int((bal["rel_diff"].abs() > 0.01).sum()),
        "n_inputs_gt_sales": int(bal["inputs_gt_sales"].sum()),
        "n_zero_output": int(((bal["output_sales"] == 0) & (bal["output_costs"] == 0)).sum()),
        "negative_cells": int((mrio.values < 0).sum()),
    }
    print("  balance (sales + final demand vs inputs + value added):")
    for k, v in summary.items():
        print(f"    {k}: {v:.6g}" if isinstance(v, float) else f"    {k}: {v}")

    prov = {
        "scope": spec["scope"],
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "script": str(Path(__file__).resolve().relative_to(locate.find_repo_root())).replace("\\", "/"),
        "script_sha256": sha256(Path(__file__)),
        **git_state(Path(__file__)),
        "spec": str(args.spec).replace("\\", "/"), "spec_sha256": sha256(args.spec),
        "source": str(spec["source"]), "source_sha256": src_sha, "source_bytes": src.stat().st_size,
        "source_lineage": spec.get("source_lineage"),
        "tables": {p.name: sha256(p) for p in (spec["_regions_table"], spec["_sectors_table"], spec["_sectors_meta"])},
        "outputs": {p.name: sha256(p) for p in (mrio_path, st_path, bal_path)},
        "units": "kUSD (GLORIA), rounded to %d decimals" % int(spec["decimals"]),
        "balance": summary,
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
    }
    if args.compare_dir:
        prov["comparison"] = {
            "mrio": compare(mrio_path, args.compare_dir / spec["outputs"]["mrio"], "mrio"),
            "sector_table": compare(st_path, args.compare_dir / spec["outputs"]["sector_table"], "sector_table"),
        }
        print("  comparison with", args.compare_dir)
        for k, d in prov["comparison"].items():
            print(f"    {k}: " + "; ".join(f"{a}={b}" for a, b in d.items() if "sha256" not in a and a != "reference"))
    prov_path = stem.parent / (stem.name + ".provenance.json")
    prov_path.write_text(json.dumps(prov, indent=2), encoding="utf-8")
    print(f"  wrote {st_path.name}, {bal_path.name}, {prov_path.name}; done in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
