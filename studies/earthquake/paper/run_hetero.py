"""Run the shock-heterogeneity draws for the idealized experiments (Sec. 3.5).

Takes the draw list produced by ``build_hetero_draws.py`` and runs each draw as a
capital-destruction disruption, holding the destroyed amount fixed and varying only
the resolution at which it is concentrated. Reports the household consumption loss
accumulated by 3, 6 and 12 months, plus the government and investment shortfalls and
the production-side value-added loss.

Parameters are the earthquake configuration unchanged -- monthly steps, supplier
substitution and reconstruction on -- so the idealized results and the case study are
directly comparable. The homogeneous reference (the destroyed capital spread over
every canton and sector in proportion to capital) is run as one extra draw per seed,
and is what the concentrated draws are measured against.

Every draw runs on the same set of network seeds. That is deliberate: Fig. 6 reports
a coefficient of variation *across draws*, and sharing the seed set keeps that
statistic interpretable -- network noise is common to all draws and can be separated
out, instead of being confounded with genuine draw-to-draw heterogeneity.

Within a draw, the destroyed capital is allocated across the group's units in
proportion to their capital, so every unit in the group loses the same fraction. That
is what makes ``destroyed_fraction`` a property of the draw, and it makes the
homogeneous reference the limiting case of the same rule applied to the whole economy.

CLI:
    python run_hetero.py --draws _out/draws --seeds 0-2 \\
        --out _out/hetero_losses.csv
"""
from __future__ import annotations

import argparse
import logging
import random
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, build_params, setup_logging          # noqa: E402
from disruptsc.init_pipeline.transport import build_transport_network          # noqa: E402
from disruptsc.init_pipeline.load_data import (                                # noqa: E402
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors)
from disruptsc.init_pipeline.agents import (                                   # noqa: E402
    create_firm_table, create_firms, load_tech_coefs, load_input_criticality,
    load_inventories, configure_household_inventories, create_household_table,
    create_households, create_countries, add_representative_demand_agents)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network    # noqa: E402
import disruptsc.run_pipeline.simulate as S                                    # noqa: E402
from disruptsc.run_pipeline.simulate import run_disruption, set_initial_conditions  # noqa: E402

DAYS_PER_STEP = {"day": 1, "week": 7, "month": 30, "year": 365}
RESOLUTIONS = ("sector", "province", "canton", "province_sector", "canton_sector")
HORIZONS_MONTHS = (3, 6, 12)


def _seeds(s: str) -> list[int]:
    s = str(s)
    if "-" in s and "," not in s:
        a, b = s.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in s.split(",")]


# --------------------------------------------------------------------------
# draws -> per-cell destroyed capital
# --------------------------------------------------------------------------
def parse_units(resolution: str, units: str) -> list:
    """Split the ``units`` field of a draw row into its unit identifiers."""
    parts = units.split("|")
    if resolution in ("sector", "province", "canton"):
        return parts
    return [tuple(p.rsplit("_", 1)) for p in parts]      # (place, sector)


def allocate(resolution: str, units: list, capital: pd.Series, total: float) -> pd.DataFrame:
    """Spread ``total`` over the draw's (canton, sector) cells, proportionally to capital.

    Every cell of the group loses the same fraction of its capital, so the draw is
    characterised by one destroyed fraction rather than by an arbitrary within-group
    allocation. Returns the model-ready long form the disruption loader expects.
    """
    idx = capital.index
    if resolution == "sector":
        sel = capital[idx.get_level_values("sector").isin(units)]
    elif resolution == "province":
        sel = capital[idx.get_level_values("province").isin(units)]
    elif resolution == "canton":
        sel = capital[idx.get_level_values("canton").isin(units)]
    else:
        level = "province" if resolution.startswith("province") else "canton"
        wanted = set(units)
        keep = [(c, p, s) for c, p, s in idx
                if ((p if level == "province" else c), s) in wanted]
        sel = capital.loc[keep]

    sel = sel[sel > 0]
    if sel.empty or sel.sum() <= 0:
        raise ValueError(f"draw selects no capital: {resolution} {units[:3]}")
    amounts = sel * (total / sel.sum())
    out = amounts.reset_index()
    out.columns = ["subregion_canton", "province", "sector", "destroyed_capital_mUSD"]
    return out[["subregion_canton", "sector", "destroyed_capital_mUSD"]]


def load_draws(draws_dir: Path, resolutions: tuple) -> pd.DataFrame:
    frames = []
    for res in resolutions:
        f = draws_dir / f"draws_{res}.csv"
        if not f.exists():
            logging.warning("missing %s -- skipped", f.name)
            continue
        frames.append(pd.read_csv(f))
    if not frames:
        raise SystemExit(f"no draw files found in {draws_dir}")
    return pd.concat(frames, ignore_index=True)


# --------------------------------------------------------------------------
def build_agents(common, ap_, sp, tp, seed):
    """Fresh agents + seeded supply-chain network for one Monte-Carlo seed."""
    firms = create_firms(common["firm_table"], ap_)
    load_tech_coefs(firms, common["mrio"], common["selection"])
    if common.get("crit_df") is not None:
        load_input_criticality(firms, common["crit_df"])
    load_inventories(firms, ap_.inventory_duration_targets, sp.time_resolution, common["sector_table"])
    households = create_households(common["household_table"], common["consumption"])
    households = add_representative_demand_agents(households, common["mrio"], common["selection"],
                                                  ap_, sp.time_resolution)
    configure_household_inventories(households, ap_.enable_household_inventories,
                                    ap_.household_inventory_duration_targets,
                                    ap_.inventory_restoration_time, sp.time_resolution,
                                    common["sector_table"])
    countries = create_countries(common["mrio"], common["tnodes"], common["countries_path"],
                                 common["usd_per_ton"], sp.time_resolution, ap_, common["selection"],
                                 transport_edges=common["te"],
                                 countries_no_transport=tp.countries_no_transport)
    random.seed(seed)
    np.random.seed(seed)
    sc = build_supply_chain_network(firms, households, countries, common["mrio"], common["sector_table"],
                                    ap_.nb_suppliers_per_input, ap_.weight_localization_firm,
                                    ap_.weight_localization_household, common["cargo_map"], common["tn"])
    set_initial_conditions(sc, firms, households, countries, tp, sp)

    def _va(f):
        ef = getattr(f, "eq_finance", None) or {}
        s = ef.get("sales", 0.0)
        c = ef.get("costs", {})
        return (s - c.get("input", 0.0) - c.get("transport", 0.0)) / s if s > 1e-12 else 0.0

    return sc, firms, households, countries, {pid: _va(f) for pid, f in firms.items()}


def model_capital(firms) -> pd.Series:
    """(canton, province, sector) -> capital, straight from the built firms.

    Using the live agents rather than a reconstruction guarantees the draws are sized
    on exactly the capital the run will destroy.
    """
    rows = {}
    for f in firms.values():
        sub = getattr(f, "subregions", None) or {}
        key = (sub.get("subregion_canton"), sub.get("subregion_province"), f.sector)
        rows[key] = rows.get(key, 0.0) + float(f.active_capital + f.idle_capital)
    s = pd.Series(rows)
    s.index = pd.MultiIndex.from_tuples(s.index, names=["canton", "province", "sector"])
    return s


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", type=Path, required=True, help="dir holding draws_<resolution>.csv")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seeds", type=_seeds, default=[0, 1, 2])
    ap.add_argument("--total", type=float, default=2438.7, help="destroyed capital, mUSD")
    ap.add_argument("--t-final", type=int, default=12, help="months")
    ap.add_argument("--resolutions", default=",".join(RESOLUTIONS))
    ap.add_argument("--criticality", type=Path, default=None)
    ap.add_argument("--skip-existing", action="store_true",
                    help="resume: keep rows already in --out and run only what is missing")
    args = ap.parse_args()

    setup_logging("info")
    cfg = load_config("EcuadorEQ")
    cfg["t_final"] = args.t_final
    tp, sp, ap_, lp = build_params(cfg)
    fp = cfg["filepaths"]
    disr = cfg["disruptions"][0]
    step_days = DAYS_PER_STEP.get(sp.time_resolution, 30)
    ppy = 365.0 / step_days
    horizons = {m: max(1, round(m * 30.0 / step_days)) for m in HORIZONS_MONTHS}
    print(f"time step = {sp.time_resolution} ({step_days}d), t_final={sp.t_final}, "
          f"horizons(steps)={horizons}, seeds={args.seeds}")

    resolutions = tuple(r.strip() for r in args.resolutions.split(",") if r.strip())
    draws = load_draws(args.draws, resolutions)
    print(f"{len(draws)} draws over {draws.resolution.nunique()} resolutions")

    done = set()
    if args.skip_existing and args.out.exists():
        prev = pd.read_csv(args.out)
        done = set(zip(prev.seed, prev.resolution, prev.draw_id))
        print(f"resuming: {len(done)} rows already present")

    # ---- seed-independent build ----
    tn, te, tnodes = build_transport_network(
        cfg.get("transport_modes", ["roads"]), fp, cfg.get("logistics", {}), sp.time_resolution,
        capacity_overrides=cfg.get("transport_capacity_overrides"),
        default_transport_capacity=cfg.get("default_transport_capacity"),
        use_cargo_types=tp.use_cargo_types)
    mrio = load_mrio(fp.get("mrio"), ap_.monetary_units_in_data)
    sector_table = load_sector_table(fp.get("sector_table"))
    usd_per_ton = load_usd_per_ton(sector_table)
    selection = filter_sectors(mrio, ap_.flow_coverage, ap_.sectors_to_include, ap_.sectors_to_exclude)
    firm_table = create_firm_table(mrio, sector_table, fp.get("firms_spatial"),
                                   fp.get("households_spatial"), usd_per_ton, tnodes, ap_, selection)
    household_table, consumption = create_household_table(mrio, fp.get("households_spatial"), tnodes,
                                                          selection, ap_,
                                                          time_resolution=sp.time_resolution)
    cargo_map = lp.sector_to_cargo_type if tp.use_cargo_types else {"default": "any"}
    crit_path = args.criticality or fp.get("input_criticality")
    crit_df = pd.read_csv(crit_path, index_col=0) if crit_path and Path(crit_path).exists() else None
    if crit_df is None:
        print(f"WARNING: no criticality matrix at {crit_path} -- strict Leontief")
    common = dict(tn=tn, te=te, tnodes=tnodes, mrio=mrio, sector_table=sector_table,
                  usd_per_ton=usd_per_ton, selection=selection, firm_table=firm_table,
                  household_table=household_table, consumption=consumption, cargo_map=cargo_map,
                  countries_path=fp.get("countries_spatial"), crit_df=crit_df)

    # ---- in-process trace: household / government / investment / value added ----
    state = {"firm_va": {}}
    TRACE = {"va": [], "hh": [], "gov": [], "inv": []}
    _orig = S._run_one_time_step

    def traced(time_step, *a, **k):
        r = _orig(time_step, *a, **k)
        fs, hh = a[3], a[4]
        fv = state["firm_va"]
        TRACE["va"].append(sum(f.production * fv.get(pid, 0.0) for pid, f in fs.items()))
        # the national government and investment agents live in the household dict but
        # are separate accounting agents -- keep them out of the welfare headline
        for key, want in (("hh", "household"), ("gov", "government"), ("inv", "investment")):
            TRACE[key].append(sum(h.consumption_loss for h in hh.values()
                                  if getattr(h, "agent_type", "household") == want))
        return r

    S._run_one_time_step = traced

    rows: list[dict] = []
    tmpdir = Path(tempfile.mkdtemp(prefix="hetero_shock_"))
    for seed in args.seeds:
        print(f"[seed {seed}] building agents ...")
        sc, firms, households, countries, firm_va = build_agents(common, ap_, sp, tp, seed)
        state["firm_va"] = firm_va
        capital = model_capital(firms)
        print(f"[seed {seed}] model capital ${capital.sum():,.0f}M over {len(capital)} cells")

        # homogeneous reference + every concentrated draw
        jobs = [("homogeneous", -1, None)]
        jobs += [(r.resolution, int(r.draw_id), r.units) for r in draws.itertuples()]

        for n, (res, draw_id, units) in enumerate(jobs, 1):
            if (seed, res, draw_id) in done:
                continue
            if res == "homogeneous":
                sel = capital[capital > 0]
                alloc = (sel * (args.total / sel.sum())).reset_index()
                alloc.columns = ["subregion_canton", "province", "sector", "destroyed_capital_mUSD"]
                alloc = alloc[["subregion_canton", "sector", "destroyed_capital_mUSD"]]
                group_capital = float(capital.sum())
            else:
                try:
                    alloc = allocate(res, parse_units(res, units), capital, args.total)
                except ValueError as exc:
                    logging.warning("seed %s %s#%s skipped: %s", seed, res, draw_id, exc)
                    continue
                group_capital = _group_capital(res, units, capital)

            shock_csv = tmpdir / f"shock_{seed}_{res}_{draw_id}.csv"
            alloc.to_csv(shock_csv, index=False)
            d = dict(disr, file=str(shock_csv), description_type="subregion_file", unit="mUSD")

            for v in TRACE.values():
                v.clear()
            logging.disable(logging.INFO)
            run_disruption(sc, tn, firms, households, countries, tp, sp, [d], te, firm_table,
                           sp.t_final, export_folder=None)
            logging.disable(logging.NOTSET)

            annual_gdp = TRACE["va"][0] * ppy
            row = {"seed": seed, "resolution": res, "draw_id": draw_id,
                   "n_units": (0 if res == "homogeneous" else len(parse_units(res, units))),
                   "group_capital_mUSD": round(group_capital, 2),
                   "destroyed_fraction": round(args.total / group_capital, 5) if group_capital else float("nan"),
                   "total_destroyed_mUSD": round(float(alloc.destroyed_capital_mUSD.sum()), 2),
                   "annual_gdp_mUSD": round(annual_gdp, 2)}
            for m, steps in horizons.items():
                row[f"household_loss_pct_gdp_{m}m"] = round(
                    100.0 * float(sum(TRACE["hh"][:steps])) / annual_gdp, 5)
                row[f"government_loss_pct_gdp_{m}m"] = round(
                    100.0 * float(sum(TRACE["gov"][:steps])) / annual_gdp, 5)
                row[f"investment_loss_pct_gdp_{m}m"] = round(
                    100.0 * float(sum(TRACE["inv"][:steps])) / annual_gdp, 5)
                row[f"va_loss_pct_gdp_{m}m"] = round(
                    100.0 * float(sum(TRACE["va"][0] - v for v in TRACE["va"][1:steps + 1])) / annual_gdp, 5)
            row["units"] = "" if res == "homogeneous" else units
            rows.append(row)

            if n % 10 == 0 or n == len(jobs):
                print(f"  [seed {seed}] {n}/{len(jobs)}  {res}#{draw_id}  "
                      f"hh12m={row['household_loss_pct_gdp_12m']:.3f}%")
                args.out.parent.mkdir(parents=True, exist_ok=True)
                _flush(rows, args.out, args.skip_existing)

    _flush(rows, args.out, args.skip_existing)
    print(f"wrote {args.out}")


def _group_capital(resolution: str, units: str, capital: pd.Series) -> float:
    idx = capital.index
    us = parse_units(resolution, units)
    if resolution == "sector":
        return float(capital[idx.get_level_values("sector").isin(us)].sum())
    if resolution == "province":
        return float(capital[idx.get_level_values("province").isin(us)].sum())
    if resolution == "canton":
        return float(capital[idx.get_level_values("canton").isin(us)].sum())
    level = "province" if resolution.startswith("province") else "canton"
    wanted = set(us)
    keep = [(c, p, s) for c, p, s in idx if ((p if level == "province" else c), s) in wanted]
    return float(capital.loc[keep].sum()) if keep else 0.0


def _flush(rows: list[dict], out: Path, append: bool) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    if append and out.exists():
        df = pd.concat([pd.read_csv(out), df], ignore_index=True)
        df = df.drop_duplicates(["seed", "resolution", "draw_id"], keep="last")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)


if __name__ == "__main__":
    main()
