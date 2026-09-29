"""Profiles of the wave-isolation experiment (29 Sep 2026; review point NS4, test T5).

The 2026 season has two troughs. That the second costs twice the first is a comparison of two different
waves (length, depth), not a test of the claim that a low-water season is priced by its calendar. The
experiment isolates the memory of the stocks:

    A alone          weeks 1-10 of the 2026 profile (22 June - 30 August: the descent and the August trough)
    B alone          weeks 11 to the end of the profile (from 31 August: the autumn trough and the recovery)
    A, gap g, B      A, then g weeks of normal water, then B, for g = 1, 2, 4, 8
                     (g = 0 is the 2026 profile itself, run 2026_gs1_base)
    flat             the whole profile at its mean load factor: the same tonnage turned away,
                     spread evenly, no trough

Statistic: the interaction I(g) = L(A, gap g, B) - L(A) - L(B), with L the cumulated German value-added
loss. Stocks that remember the first wave give I(0) > 0 and I(g) falling to zero as the gap lets them
refill. Wave shapes are preserved; every run has the same recovery horizon after its last profile week.

Normal water is 200 cm at Kaub (full loading, no surcharge). Writes scenarios/2026_wave*.csv.

Usage:
    python studies/rhine2026/build_wave_profiles.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = HERE / "scenarios"
NORMAL_CM = 200.0
SPLIT = 10                     # wave A = profile weeks 1..10, wave B = weeks 11..19
GAPS = (1, 2, 4, 8)
FIRST = pd.Timestamp("2026-06-22")


def curve():
    t = pd.read_csv(SCEN / "draught_table.csv").sort_values("kaub_cm")
    x, y = t["kaub_cm"].to_numpy(float), t["load_factor"].to_numpy(float)
    return (lambda cm: float(np.interp(cm, x, y, left=y[0], right=y[-1]))), x, y


def write(name: str, gauges: list[float], parts: list[str], note: str):
    weeks = [FIRST + pd.Timedelta(weeks=i) for i in range(len(gauges))]
    df = pd.DataFrame({"week_start": [w.strftime("%Y-%m-%d") for w in weeks], "kaub_cm": [round(g, 1) for g in gauges],
                       "status": parts, "note": note})
    df.to_csv(SCEN / f"{name}.csv", index=False)
    return df


def main():
    prof = pd.read_csv(SCEN / "2026.csv")
    g = prof["kaub_cm"].astype(float).tolist()
    a, b = g[:SPLIT], g[SPLIT:]
    lf, x, y = curve()
    rows = []
    write("2026_waveA", a, ["wave A"] * len(a), "wave isolation: weeks 1-10 of the 2026 profile, then normal water")
    rows.append(("2026_waveA", len(a), sum(1 - lf(v) for v in a)))
    write("2026_waveB", b, ["wave B"] * len(b), "wave isolation: weeks 11-19 of the 2026 profile, from normal water")
    rows.append(("2026_waveB", len(b), sum(1 - lf(v) for v in b)))
    for gap in GAPS:
        seq = a + [NORMAL_CM] * gap + b
        parts = ["wave A"] * len(a) + ["gap (normal water)"] * gap + ["wave B"] * len(b)
        write(f"2026_waveAB_gap{gap}", seq, parts, f"wave isolation: A, {gap} week(s) of normal water, B")
        rows.append((f"2026_waveAB_gap{gap}", len(seq), sum(1 - lf(v) for v in seq)))
    mean_lf = float(np.mean([lf(v) for v in g]))
    flat_cm = float(np.interp(mean_lf, y, x))                     # the draught table is increasing: invert it
    write("2026_waveflat", [flat_cm] * len(g), ["flat"] * len(g),
          f"wave isolation: {len(g)} weeks at the mean load factor of the 2026 profile ({mean_lf:.3f}, Kaub {flat_cm:.1f} cm)")
    rows.append(("2026_waveflat", len(g), sum(1 - lf(flat_cm) for _ in g)))
    rows.append(("2026 (gap 0)", len(g), sum(1 - lf(v) for v in g)))
    t = pd.DataFrame(rows, columns=["profile", "weeks", "tonnage_turned_away_week_equivalents"]).round(2)
    print(t.to_string(index=False))
    print(f"mean load factor of the 2026 profile {mean_lf:.3f} -> flat gauge {flat_cm:.1f} cm")


if __name__ == "__main__":
    main()
