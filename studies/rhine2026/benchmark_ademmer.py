"""The ex-post benchmark rebuilt from the published specification (6 Oct 2026, review of 5 Oct, point E1).

Ademmer, Jannsen and Meuchelboeck (Kiel Working Paper 2155, 2020; German Economic Review 2023) estimate, on monthly
data from January 1991 to March 2019,

    y_t = a + b0 dLW_t + b1 dLW_{t-1} + rho y_{t-1} + controls + e_t            (their equation 2)

with y_t the month-on-month growth rate of German industrial production (Destatis index, NACE B-E, in %) and dLW_t the
CHANGE in the number of days of month t with the Kaub gauge below 78 cm. Table 2 of the working paper (robust
standard errors in brackets):

    column 1  baseline                 b0 -0.034 (0.012)   b1 -0.024 (0.014)   rho -0.172 (0.119)
    column 2  with global production   b0 -0.038 (0.012)   b1 -0.026 (0.014)   rho -0.357 (0.043)
    column 3  contemporaneous only     b0 -0.029 (0.013)   b1  --              rho -0.346 (0.044)
    column 4  sample to 2017           b0 -0.041 (0.017)   b1 -0.036 (0.019)   rho -0.360 (0.044)

The effect on the LEVEL of production is the paper's "dynamic counterfactual": the growth that the low water induces,
g_t = b0 dLW_t + b1 dLW_{t-1} + rho g_{t-1}, cumulated over the months, L_t = sum_{s <= t} g_s (log approximation, in
%). Because the regressor is the change in the days, a low-water month lowers the level and the return to normal
water raises it back: the effect is temporary by construction (the paper's footnote 7 and Appendix A). With the 2018
days of the daily gauge record (29, 14, 31, 30 and 3 from August to December, none before or after) column 1 gives
1.0, 1.0, 1.2, 1.5 and 0.6 % below the counterfactual, the November peak of 1.5 % that the paper reports, and zero by
January. The earlier construction of this study (level = b0 LW_t + b1 LW_{t-1}: 1.02, 1.23, 1.38, 1.74, 0.82) applied
the coefficients as level effects of the days themselves and overstated the path.

Uncertainty: the covariance of the estimates is not published. The band is a Monte Carlo over independent normal
draws of (b0, b1, rho) at the reported standard errors: the 16-84 % interval (about one standard error) and the
2.5-97.5 % interval, month by month and for the integral over the event months (August to December 2018; July to
December 2026). Independence is an assumption; the band is indicative, not an exact confidence interval.

2026: the low-water days of June to September are observed (PEGELONLINE daily means to 29 September); from 30
September the days follow the weekly means of the profile (the BfG outlook of 28 September and the assumed
recovery), a week below 78 cm counting for all its days. The result is what the published regression implies for
2026 under the same outlook, the comparison line of the prospective test.

Usage:
    python studies/rhine2026/benchmark_ademmer.py [--out-dir studies/rhine2026/additional_data] [--draws 20000]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = HERE / "scenarios"
THRESHOLD_CM = 78.0

# column -> (b0, se0, b1, se1, rho, se_rho); working paper Table 2
COLUMNS = {
    1: (-0.034, 0.012, -0.024, 0.014, -0.172, 0.119),
    2: (-0.038, 0.012, -0.026, 0.014, -0.357, 0.043),
    3: (-0.029, 0.013, 0.0, 0.0, -0.346, 0.044),
    4: (-0.041, 0.017, -0.036, 0.019, -0.360, 0.044),
}
LABELS = {1: "baseline (column 1)", 2: "with global production (column 2)",
          3: "contemporaneous term only (column 3)", 4: "sample to 2017 (column 4)"}
EVENT_MONTHS = {2018: ["2018-08", "2018-09", "2018-10", "2018-11", "2018-12"],
                2026: ["2026-07", "2026-08", "2026-09", "2026-10", "2026-11", "2026-12"]}
# the months computed: two normal months before the event (the change in days needs them) and two after
WINDOW = {2018: pd.period_range("2018-06", "2019-02", freq="M"), 2026: pd.period_range("2026-05", "2027-02", freq="M")}


def daily_gauge(year: int) -> pd.Series:
    """Daily mean at Kaub (cm), the observed record extended by the profile's weekly means where no daily value
    exists (2026: the outlook and the assumed recovery); beyond the profile the gauge is taken as normal."""
    d = pd.read_csv(SCEN / f"kaub_daily_{year}.csv")
    s = pd.Series(d["kaub_cm"].astype(float).values, index=pd.to_datetime(d["date"]))
    prof = pd.read_csv(SCEN / f"{year}.csv")
    days = {}
    for _, r in prof.iterrows():
        w0 = pd.Timestamp(r["week_start"])
        for k in range(7):
            days[w0 + pd.Timedelta(days=k)] = float(r["kaub_cm"])
    ext = pd.Series(days)
    full = pd.concat([s, ext[~ext.index.isin(s.index)]]).sort_index()
    return full


def low_water_days(year: int) -> dict[str, int]:
    g = daily_gauge(year)
    below = (g < THRESHOLD_CM).groupby(g.index.to_period("M")).sum()
    return {str(p): int(below.get(p, 0)) for p in WINDOW[year]}


def induced_shortfall(days: list[int], b0: float, b1: float, rho: float) -> np.ndarray:
    """Level shortfall (%, positive = below the counterfactual) month by month for a sequence of low-water day
    counts, from the dynamic counterfactual of equation 2 (growth induced by the change in the days, with the
    autoregressive term, cumulated)."""
    d = np.asarray(days, dtype=float)
    dd = np.diff(np.concatenate([[0.0], d]))          # change in the days; nothing before the window
    g_prev, dd_prev, level, out = 0.0, 0.0, 0.0, []
    for x in dd:
        g = b0 * x + b1 * dd_prev + rho * g_prev
        level += g
        out.append(-level)
        g_prev, dd_prev = g, x
    return np.array(out)


def record(year: int, column: int = 1, draws: int = 20000, seed: int = 0) -> tuple[pd.DataFrame, dict]:
    """Monthly shortfall path with its Monte Carlo band, and the integral over the event months."""
    days = low_water_days(year)
    months = list(days)
    b0, s0, b1, s1, rho, sr = COLUMNS[column]
    central = induced_shortfall(list(days.values()), b0, b1, rho)
    rng = np.random.default_rng(seed)
    sims = np.array([induced_shortfall(list(days.values()), rng.normal(b0, s0), rng.normal(b1, s1) if s1 > 0 else b1,
                                       rng.normal(rho, sr)) for _ in range(draws)])
    q = lambda p: np.percentile(sims, p, axis=0)
    t = pd.DataFrame({"month": months, "low_water_days": list(days.values()), "central": central.round(3),
                      "p16": q(16).round(3), "p84": q(84).round(3), "p2_5": q(2.5).round(3), "p97_5": q(97.5).round(3)})
    ev = [months.index(m) for m in EVENT_MONTHS[year]]
    integ = sims[:, ev].sum(axis=1)
    summary = {"integral": float(central[ev].sum()), "p16": float(np.percentile(integ, 16)), "p84": float(np.percentile(integ, 84)),
               "p2_5": float(np.percentile(integ, 2.5)), "p97_5": float(np.percentile(integ, 97.5)),
               "peak_month": months[ev[int(np.argmax(central[ev]))]], "peak": float(central[ev].max())}
    return t, summary


def central_path(year: int, column: int = 1) -> dict[str, float]:
    """{month: shortfall %} over the event months, central estimate."""
    t, _ = record(year, column, draws=1)
    return {m: float(t.set_index("month").central[m]) for m in EVENT_MONTHS[year]}


def main(out_dir: Path, draws: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    for year in (2018, 2026):
        lines = [f"Ex-post benchmark for {year}: the published dynamic specification (Kiel WP 2155, Table 2) applied to the "
                 f"low-water days at Kaub (< {THRESHOLD_CM:.0f} cm)", f"  days by month: {low_water_days(year)}"]
        frames = []
        for col in COLUMNS:
            t, s = record(year, col, draws)
            t.insert(0, "column", col); frames.append(t)
            ev = t[t.month.isin(EVENT_MONTHS[year])]
            lines.append(f"  {LABELS[col]:38s} " + " ".join(f"{m[5:]}={v:.2f}" for m, v in zip(ev.month, ev.central))
                         + f"  integral {s['integral']:.2f} (16-84 % {s['p16']:.2f}-{s['p84']:.2f}; 2.5-97.5 % {s['p2_5']:.2f}-{s['p97_5']:.2f})"
                         + f"  peak {s['peak_month'][5:]} {s['peak']:.2f}")
        pd.concat(frames).to_csv(out_dir / f"benchmark_ademmer_{year}.csv", index=False)
        text = "\n".join(lines)
        (out_dir / f"benchmark_ademmer_{year}.txt").write_text(text + "\n", encoding="utf-8")
        print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(HERE / "additional_data"))
    ap.add_argument("--draws", type=int, default=20000)
    a = ap.parse_args()
    main(Path(a.out_dir), a.draws)
