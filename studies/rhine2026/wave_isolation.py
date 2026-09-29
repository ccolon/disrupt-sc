"""Reading of the wave-isolation experiment (review point NS4, test T5; profiles: build_wave_profiles.py).

L = cumulated German value-added loss of a run (mUSD and % of a quarter). Interaction of the two waves at gap g:
    I(g) = L(A, gap g, B) - L(A) - L(B)
I(g) > 0 means that the second wave costs more because the first one came before it (stocks had no time to
refill); I(g) -> 0 as the gap grows means that the memory is that of the stocks. The flat profile turns the
same tonnage away, spread evenly: its loss against L(gap 0) separates the calendar from the total.

Usage:
    python studies/rhine2026/wave_isolation.py [--batch C:/dsc_runs/rhine2026/compare_runs_batch.csv]
        [--base-table studies/rhine2026/additional_data/compare_runs_batch_20260929_gs1paper.csv] [--out FILE]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "studies/rhine2026/additional_data"


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def main(batch: Path, base_table: Path, out: Path | None):
    t = table(batch)
    base = table(base_table).loc["2026_gs1_base"]
    q = base["DEU_cum_mUSD"] / base["DEU_%quarter"]                    # mUSD per 1 % of a quarter
    L = {"A": t.loc["wave_A", "DEU_cum_mUSD"], "B": t.loc["wave_B", "DEU_cum_mUSD"], 0: base["DEU_cum_mUSD"]}
    for g in (1, 2, 4, 8):
        L[g] = t.loc[f"wave_AB_gap{g}", "DEU_cum_mUSD"]
    lines = [f"L(A alone) = {L['A']:,.0f} mUSD = {L['A'] / q:.3f} % of a quarter; L(B alone) = {L['B']:,.0f} = {L['B'] / q:.3f} %; "
             f"sum {L['A'] + L['B']:,.0f} = {(L['A'] + L['B']) / q:.3f} %", "",
             "gap (weeks of normal water)   L(A, gap, B) mUSD   % of a quarter   interaction I(g) mUSD   I(g) / (L(A)+L(B))"]
    for g in (0, 1, 2, 4, 8):
        i = L[g] - L["A"] - L["B"]
        lines.append(f"{g:>10d} {L[g]:>28,.0f} {L[g] / q:>16.3f} {i:>22,.0f} {100 * i / (L['A'] + L['B']):>18.0f} %")
    if "wave_flat" in t.index:
        f = t.loc["wave_flat", "DEU_cum_mUSD"]
        lines += ["", f"flat profile (same tonnage turned away, spread evenly): {f:,.0f} mUSD = {f / q:.3f} % of a quarter, "
                      f"{100 * (f / L[0] - 1):+.0f} % against the 2026 profile"]
    peaks = {r: (t.loc[r, "DEU_peak_%week"], int(t.loc[r, "DEU_peak_week"])) for r in t.index if r.startswith("wave_")}
    lines += ["", "peak week (% of a week's value added, run week): " + ", ".join(f"{r} {v:.2f} (wk {w})" for r, (v, w) in peaks.items())]
    text = "\n".join(lines)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8"); print("written", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="C:/dsc_runs/rhine2026/compare_runs_batch.csv")
    ap.add_argument("--base-table", default=str(AD / "compare_runs_batch_20260929_gs1paper.csv"))
    ap.add_argument("--out", default=str(AD / "wave_isolation.txt"))
    a = ap.parse_args()
    main(Path(a.batch), Path(a.base_table), Path(a.out) if a.out else None)
