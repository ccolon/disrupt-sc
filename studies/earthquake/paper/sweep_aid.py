"""Foreign-aid 2D sweep: reconstruction_public_share x capital_input_mix.

Two aid dimensions (see the 'challenge' discussion):
  * public_share  = fraction of reconstruction rebuilt directly/externally (aid FUNDING);
  * capital_input_mix IMP fraction = reconstruction goods sourced abroad vs from
    domestic construction/manufacturing (aid IN-KIND / import content).

Grid: public_share {0.0, 0.8} x mix {domestic, mixed, import} = 6 points, x N seeds.
Mechanism diagnostics per run (do imports relieve the domestic bottleneck / crowding-out?):
  * household_loss_pct          headline welfare loss
  * household_loss_conman_pct   welfare loss on CON+MAN goods (crowding-out proxy)
  * conman_production_cum       cumulative domestic CON+MAN output (reconstruction activity)
  * capital_recovery_pct        (peak destroyed - end destroyed) / peak destroyed (rebuild speed)

Expectation: with public_share=0.8 the mix barely matters (only 20% is B2B); with
public_share=0.0 the mix has full leverage — more IMP => faster capital recovery, less
CON/MAN crowding-out, but no domestic reconstruction activity.

Run:  python studies/earthquake/paper/sweep_aid.py --n-seeds 5 \
        --criticality studies/earthquake/additional_data/input_criticality.csv \
        --shock studies/earthquake/additional_data/earthquake_shock_modelready.csv \
        --out output/earthquake_aid/aid_all.csv
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # import run_grid helpers
sys.setrecursionlimit(50000)

from disruptsc.config import load_config, build_params, setup_logging               # noqa: E402
from disruptsc.build import build_common, build_agents, firm_va_shares              # noqa: E402
from disruptsc.run_pipeline.simulate import run_disruption                          # noqa: E402
from run_grid import _floats, _seeds, DAYS_PER_STEP                                 # noqa: E402

# capital_input_mix presets: {name: (mix, imp_fraction)}
MIXES = [("domestic", {"CON": 0.7, "MAN": 0.2, "IMP": 0.1}, 0.10),
         ("mixed",    {"CON": 0.35, "MAN": 0.1, "IMP": 0.55}, 0.55),
         ("import",   {"CON": 0.0, "MAN": 0.0, "IMP": 1.0}, 1.00)]
PUBLIC_SHARES = [0.0, 0.8]


def main():
    ap = argparse.ArgumentParser(description="Foreign-aid 2D sweep (public_share x capital_input_mix)")
    ap.add_argument("--flow-coverage", type=float, default=0.8)
    ap.add_argument("--nb-suppliers", type=int, default=2)
    ap.add_argument("--t-final", type=int, default=13)
    ap.add_argument("--seeds", type=_seeds, default=None)
    ap.add_argument("--n-seeds", type=int, default=5)
    ap.add_argument("--util-base", type=float, default=0.8)
    ap.add_argument("--crit-base", type=float, default=0.02)
    ap.add_argument("--target-time", type=float, default=730.0)
    ap.add_argument("--recon-lag", type=float, default=60.0)
    ap.add_argument("--public-shares", type=_floats, default=PUBLIC_SHARES)
    ap.add_argument("--criticality", type=Path, default=None)
    ap.add_argument("--shock", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    seeds = args.seeds if args.seeds is not None else list(range(args.n_seeds))

    setup_logging("info")
    cfg = load_config("EcuadorEQ")
    cfg["t_final"] = args.t_final
    cfg["rationing_mode"] = "equal"
    cfg["flow_coverage"] = args.flow_coverage
    cfg["nb_suppliers_per_input"] = args.nb_suppliers
    tp, sp, ap_, lp = build_params(cfg)
    disr = cfg["disruptions"][0]
    if args.shock:
        if not Path(args.shock).exists():
            raise SystemExit(f"--shock not found: {args.shock}")
        disr = dict(disr, file=str(args.shock))
    ppy = 365.0 / DAYS_PER_STEP.get(sp.time_resolution, 30)

    # ---- seed-independent build (shared core builder) ----
    common = build_common(cfg, tp, sp, ap_, lp, input_criticality=args.criticality)
    tn, te = common["tn"], common["te"]
    firm_table = common["firm_table"]

    # ---- trace: VA (for GDP), household loss (total + CON/MAN), CON/MAN production, capital destroyed ----
    # Supported observer hook (called at the end of every simulated step) —
    # replaces the old monkeypatch of _run_one_time_step.
    state = {"firm_va": {}, "cm_rs": set()}
    T_VA, T_HH, T_HHCM, T_PROD, T_KD = [], [], [], [], []

    def observer(time_step, firms, households, **_):
        fv, cm = state["firm_va"], state["cm_rs"]
        T_VA.append(sum(f.production * fv.get(pid, 0.0) for pid, f in firms.items()))
        T_HH.append(sum(h.consumption_loss for h in households.values()))
        T_HHCM.append(sum(sum(h.consumption_loss_per_sector.get(rs, 0.0) for rs in cm) for h in households.values()))
        T_PROD.append(sum(f.production for f in firms.values() if f.sector in ("CON", "MAN")))
        T_KD.append(sum(f.capital_destroyed for f in firms.values()))

    print(f"aid sweep: flow={args.flow_coverage} nb={args.nb_suppliers} t_final={sp.t_final} "
          f"seeds={seeds} public={args.public_shares} mixes={[m[0] for m in MIXES]}")
    rows = []
    for seed in seeds:
        print(f"[seed {seed}] building ...")
        sc, firms, households, countries = build_agents(common, ap_, sp, tp, seed)
        state["firm_va"] = firm_va_shares(firms)
        state["cm_rs"] = {f.region_sector for f in firms.values() if f.sector in ("CON", "MAN")}
        for f in firms.values():
            f.utilization_rate = args.util_base
            f.critical_input_threshold = args.crit_base
        for public in args.public_shares:
            for mixname, mix, imp_frac in MIXES:
                for tr in (T_VA, T_HH, T_HHCM, T_PROD, T_KD):
                    tr.clear()
                d = dict(disr)
                d.update(reconstruction_market=True, reconstruction_public_share=public,
                         reconstruction_target_time=args.target_time, reconstruction_lag=args.recon_lag,
                         capital_input_mix=dict(mix))
                logging.disable(logging.INFO)
                run_disruption(sc, tn, firms, households, countries, tp, sp, [d], te, firm_table, sp.t_final,
                               export_folder=None, observer=observer)
                logging.disable(logging.NOTSET)
                annual_gdp = T_VA[0] * ppy
                hh = sum(T_HH); hh_cm = sum(T_HHCM)
                kd_peak = max(T_KD) if T_KD else 0.0
                recov = 100.0 * (kd_peak - T_KD[-1]) / kd_peak if kd_peak > 0 else 0.0
                rows.append({
                    "seed": seed, "reconstruction_public_share": public, "mix": mixname,
                    "imp_fraction": imp_frac,
                    "household_loss_pct_annual_gdp": round(100.0 * hh / annual_gdp, 4),
                    "household_loss_conman_pct": round(100.0 * hh_cm / annual_gdp, 4),
                    "conman_production_cum": round(float(sum(T_PROD)), 2),
                    "capital_recovery_pct": round(recov, 2),
                })
                print(f"    seed={seed} public={public} mix={mixname:>8} (IMP {imp_frac:.0%}): "
                      f"hh {rows[-1]['household_loss_pct_annual_gdp']:.2f}%  "
                      f"recovery {recov:.0f}%  CON/MAN loss {rows[-1]['household_loss_conman_pct']:.3f}%")

    df = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, mode="a", header=not args.out.exists(), index=False)
    print(f"\n-> appended {len(df)} rows ({len(seeds)} seeds x {len(args.public_shares)}x{len(MIXES)}) to {args.out}")


if __name__ == "__main__":
    main()
