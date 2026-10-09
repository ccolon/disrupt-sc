"""Read the batch of 9 October 2026 (cluster/jobs_20261009_cross.txt): the levers crossed with the finite-rail case
(review OR2) and the wave-isolation gap experiment at the 15-day refill time (review OR3).

Inputs: additional_data/compare_runs_batch_jobs_20261009_cross.csv (from compare_runs.py on the packed runs), and the
tables of 7 October for the bases (2026_s07_base, the levers without rail, 2026_rev_rail50, 2026_rev_rest15, the waves
at 30 days). Writes additional_data/batch_20261009_cross_summary.txt.

Run:  python studies/rhine2026/read_batch_20261009_cross.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
AD = HERE / "additional_data"
LEVERS = [("stock7", "stocks +7 days"), ("deep20", "fairway +20 cm"), ("fleet", "low-water fleet"), ("stock7t", "targeted stocks")]


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def main() -> None:
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    r = table(AD / "compare_runs_batch_jobs_20261007_rev.csv")
    c = table(AD / "compare_runs_batch_jobs_20261009_cross.csv")
    L = ["Batch of 9 October 2026: levers x finite rail (OR2) and the gap experiment at 15 days (OR3)", ""]
    # ---- block 1: levers under no rail (base 2026_s07_base) and under 50 kt a week (base 2026_rev_rail50)
    b0, b50 = m.loc["2026_s07_base", "DEU_cum_mUSD"], r.loc["2026_rev_rail50", "DEU_cum_mUSD"]
    L.append("== 1. Loss avoided by each lever against its own base (% of the base's cumulated German loss) ==")
    L.append(f"   bases: no rail {b0:,.0f} mUSD ({m.loc['2026_s07_base', 'DEU_%quarter']:.3f} % of a quarter), rail 50 kt {b50:,.0f} ({r.loc['2026_rev_rail50', 'DEU_%quarter']:.3f})")
    rows = []
    for key, name in LEVERS:
        a0 = 100 * (1 - m.loc[f"2026_s07_{key}", "DEU_cum_mUSD"] / b0)
        run = f"2026_rev_rail50_{key}"
        a50 = 100 * (1 - c.loc[run, "DEU_cum_mUSD"] / b50) if run in c.index else float("nan")
        rows.append((name, a0, a50, c.loc[run, "DEU_%quarter"] if run in c.index else float("nan")))
        L.append(f"   {name:18s} no rail {a0:5.1f} %   rail 50 kt {a50:5.1f} %   (loss under rail 50 kt {rows[-1][3]:.3f} % of a quarter)")
    d = pd.DataFrame(rows, columns=["lever", "no_rail", "rail50", "loss_rail50"]).set_index("lever")
    order0, order50 = d.no_rail.sort_values(ascending=False).index.tolist(), d.rail50.sort_values(ascending=False).index.tolist()
    L.append(f"   ordering without rail: {' > '.join(order0)}")
    L.append(f"   ordering under 50 kt:  {' > '.join(order50)}   ({'the same' if order0 == order50 else 'DIFFERENT'})")
    L.append("")
    # ---- block 2: the gap experiment at 15 days against 30 days
    L.append("== 2. The interaction of the two waves and its decay with the gap, at 30 and 15 days of refill time (% of a quarter) ==")
    q = "DEU_%quarter"
    a30, b30 = m.loc["wave07_A", q], m.loc["wave07_B", q]
    seq30 = {0: m.loc["2026_s07_base", q], 1: m.loc["wave07_AB_gap1", q], 2: m.loc["wave07_AB_gap2", q], 4: m.loc["wave07_AB_gap4", q], 8: m.loc["wave07_AB_gap8", q]}
    L.append(f"   30 days: A {a30:.3f} + B {b30:.3f} = {a30 + b30:.3f}; sequence " + ", ".join(f"gap {g}: {v:.3f} ({100 * (v / (a30 + b30) - 1):+.0f} %)" for g, v in seq30.items()))
    have = all(k in c.index for k in ("wave09_A_rest15", "wave09_B_rest15", "wave09_AB_gap2_rest15", "wave09_AB_gap4_rest15"))
    if have:
        a15, b15 = c.loc["wave09_A_rest15", q], c.loc["wave09_B_rest15", q]
        seq15 = {0: r.loc["2026_rev_rest15", q], 2: c.loc["wave09_AB_gap2_rest15", q], 4: c.loc["wave09_AB_gap4_rest15", q]}
        L.append(f"   15 days: A {a15:.3f} + B {b15:.3f} = {a15 + b15:.3f}; sequence " + ", ".join(f"gap {g}: {v:.3f} ({100 * (v / (a15 + b15) - 1):+.0f} %)" for g, v in seq15.items()))
        L.append("   interaction (sequence minus the sum), 30 vs 15 days: " + ", ".join(f"gap {g}: {seq30[g] - a30 - b30:+.3f} vs {seq15[g] - a15 - b15:+.3f}" for g in (0, 2, 4)))
    else:
        L.append("   15-day runs not all present: " + ", ".join(k for k in ("wave09_A_rest15", "wave09_B_rest15", "wave09_AB_gap2_rest15", "wave09_AB_gap4_rest15") if k not in c.index))
    out = AD / "batch_20261009_cross_summary.txt"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L)); print("written", out)


if __name__ == "__main__":
    main()
