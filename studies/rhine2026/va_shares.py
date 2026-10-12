"""Country-sector value-added ratios for the loss accounting (12 Oct 2026, review of 12 Oct, point E1).

A firm's value-added loss is its production shortfall times the value-added/output ratio of its OWN country-sector
(the firm's ``target_margin`` in the model, taken from the MRIO at construction). Until 12 October the study scripts
mapped the scope-wide ratio of the sector (``mrio_by_sector.csv``, summed over the 28 economies) onto every firm,
which is a different estimand: for Germany it understated the power sector (0.27 against 0.36) and the loss by about
6 %. This module gives every script one source:

  1. ``<run>/mrio_by_region_sector.csv`` (written by export.py from 12 Oct 2026 on),
  2. else ``<run>/firm_table.geojson`` (``target_margin`` per firm, identical within a country-sector),
  3. else the study-level table ``additional_data/va_share_by_region_sector.csv`` (built from the reference run's
     firm table; the MRIO is the same for every run of the study),
with the scope-wide sector ratio as the fallback for a key none of them has.

    python studies/rhine2026/va_shares.py            # (re)build the study-level table from 2026_s07_base
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
AD = HERE / "additional_data"
TABLE = AD / "va_share_by_region_sector.csv"
RUNS = Path("C:/dsc_runs/rhine2026")


def _from_region_sector_csv(path: Path) -> dict:
    t = pd.read_csv(path)
    return {(r, s): v / o for r, s, v, o in zip(t.region, t.sector, t.mrio_va, t.mrio_output) if o > 0}


def _from_firm_table(path: Path) -> dict:
    g = json.load(open(path, encoding="utf-8"))
    out = {}
    for f in g["features"]:
        p = f["properties"]
        if "target_margin" in p and p.get("region") and p.get("sector"):
            out.setdefault((p["region"], p["sector"]), float(p["target_margin"]))
    return out


def va_share_map(run: Path | None = None) -> dict:
    """{(region, sector): value-added/output ratio} for *run* (see the module docstring for the sources)."""
    if run is not None:
        run = Path(run)
        if (run / "mrio_by_region_sector.csv").exists():
            return _from_region_sector_csv(run / "mrio_by_region_sector.csv")
        if (run / "firm_table.geojson").exists():
            return _from_firm_table(run / "firm_table.geojson")
    if TABLE.exists():
        return _from_region_sector_csv(TABLE)
    raise FileNotFoundError(f"no country-sector value-added table: {TABLE} (run `python studies/rhine2026/va_shares.py`)")


def sector_fallback(run: Path) -> dict:
    """The scope-wide ratio by sector (the pre-12-October estimand), used only for a key the country-sector table lacks."""
    p = Path(run) / "mrio_by_sector.csv"
    if not p.exists():
        return {}
    va = pd.read_csv(p).set_index("sector")
    return (va["mrio_va"] / va["mrio_output"]).to_dict()


def add_va_share(fd: pd.DataFrame, run: Path, col: str = "va_share") -> pd.DataFrame:
    """Add the country-sector value-added ratio of each firm to a frame with ``region`` and ``sector`` columns."""
    m = va_share_map(run)
    fb = sector_fallback(run)
    keys = list(zip(fd["region"], fd["sector"]))
    fd[col] = [m.get(k, fb.get(k[1], 0.3)) for k in keys]
    return fd


def build_table(run: Path = RUNS / "2026_s07_base") -> Path:
    m = _from_firm_table(Path(run) / "firm_table.geojson")
    t = pd.DataFrame([(r, s, v) for (r, s), v in sorted(m.items())], columns=["region", "sector", "va_share"])
    # keep the output and VA columns the region-sector export uses, so the two files read the same way
    t["mrio_output"] = 1.0
    t["mrio_va"] = t["va_share"]
    t[["region", "sector", "mrio_output", "mrio_va", "va_share"]].to_csv(TABLE, index=False)
    return TABLE


if __name__ == "__main__":
    p = build_table()
    t = pd.read_csv(p)
    print(f"written {p}: {len(t)} country-sectors; DEU D {t[(t.region == 'DEU') & (t.sector == 'D')].va_share.iloc[0]:.3f}, "
          f"DEU C20 {t[(t.region == 'DEU') & (t.sector == 'C20')].va_share.iloc[0]:.3f}")
