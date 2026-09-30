"""LaTeX tables of the Supplementary Information, generated from the study's data (30 Sep 2026).

Writes to the Overleaf repository's tables/ folder:
  si_loading_table.tex      the draught table with its anchors (review NS2)
  si_forecast.tex           the 2026 profile: outlook of 7 September against the observations (review NS1)
  si_runs.tex               every run of the batch of 30 Sep: German and EU loss, peak (review S7)
  si_representations.tex    the 2018 monthly industrial path under both representations and stock levels (S6)

Usage:
    python studies/rhine2026/si_tables.py [--overleaf <repo folder>]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "studies/rhine2026"
AD = HERE / "additional_data"
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


def tex(s) -> str:
    return str(s).replace("%", r"\%").replace("&", r"\&").replace("_", r"\_").replace("#", r"\#")


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def loading_table(out: Path):
    d = pd.read_csv(HERE / "scenarios" / "draught_table.csv")
    rows = "\n".join(f"{int(r.kaub_cm)} & {r.load_factor:.2f} & {r.load_factor_vessel_gms:.2f} & {tex(r.anchor)} \\\\" for r in d.itertuples())
    (out / "si_loading_table.tex").write_text(r"""\begin{table}[p]
\centering\small
\caption{\textbf{The loading table.} Share of the normal tonnage that the Kaub reach can pass at a weekly mean gauge (fleet level, the column the model uses) and the load factor of a single large vessel (for comparison), with the evidence behind each anchor. Linear between anchors; below 5\,cm the fleet value is held at 0.05. Sources as noted: KBN and Schuttevaer tonnage counts of August 2026, Argus and Contargo loading reports, van Dorsser et al. (2020), the WSV and GlW conventions, PEGELONLINE gauges.}
\label{tab:loading}
\begin{tabular}{rrrp{95mm}}
\toprule
Kaub (cm) & fleet & vessel & anchor \\
\midrule
""" + rows + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


def forecast_table(out: Path):
    old = pd.read_csv(HERE / "scenarios" / "2026_vintage0910.csv").set_index("week_start")
    new = pd.read_csv(HERE / "scenarios" / "2026.csv").set_index("week_start")
    rows = []
    for w in new.index:
        o = old.kaub_cm.get(w, float("nan")); os_ = old.status.get(w, "")
        n = new.kaub_cm[w]; ns = new.status[w]
        rows.append(f"{w} & {o:.1f} & {tex(os_)} & {n:.1f} & {tex(ns)} \\\\" if pd.notna(o) else f"{w} & -- & -- & {n:.1f} & {tex(ns)} \\\\")
    (out / "si_forecast.tex").write_text(r"""\begin{table}[p]
\centering\small
\caption{\textbf{The two vintages of the 2026 profile.} Weekly mean gauge at Kaub (cm): the vintage of 10 September (observations to 10 September, the BfG six-week outlook of 7 September, assumed values after it) against the vintage of 30 September (observations to 29 September, the outlook of 28 September, assumed recovery). The outlook of 7 September missed the end-of-September trough by 20 to 40\,cm.}
\label{tab:forecast}
\begin{tabular}{lrlrl}
\toprule
week of & vintage 10 Sep & status & vintage 30 Sep & status \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


def runs_table(out: Path):
    m = table(AD / "compare_runs_batch_jobs_20260930_main.csv")
    p = table(AD / "compare_runs_batch_jobs_20260930_paired.csv")
    t = pd.concat([m, p])
    cols = ["DEU_%quarter", "DEU_peak_%week", "DEU_peak_week", "EU_cum_mUSD", "cons_loss_cum_mUSD"]
    rows = "\n".join(f"{tex(r)} & {v['DEU_%quarter']:.2f} & {v['DEU_peak_%week']:.2f} & {int(v['DEU_peak_week'])} & {v['EU_cum_mUSD'] / 1e3:.1f} & {v['cons_loss_cum_mUSD'] / 1e3:.1f} \\\\"
                     for r, v in t[cols].iterrows())
    (out / "si_runs.tex").write_text(r"""\begin{longtable}{lrrrrr}
\caption{\textbf{Every run of the batch of 30 September 2026.} German value-added loss as a share of a quarter, its peak (share of a week's value added, run week), the EU loss and the household consumption loss (billion USD). Names: \texttt{2026\_s30\_*} and \texttt{2018\_s30\_*} the two events on the reference draw and their variants; \texttt{seedN} the further draws; \texttt{wave30\_*} the wave-isolation profiles; \texttt{seedN\_<lever>} a lever paired with the base of the same draw.}
\label{tab:runs} \\
\toprule
run & DEU (\% of a quarter) & peak (\% of a week) & peak week & EU (bn) & consumption (bn) \\
\midrule
\endfirsthead
\toprule
run & DEU (\% of a quarter) & peak (\% of a week) & peak week & EU (bn) & consumption (bn) \\
\midrule
\endhead
""" + rows + r"""
\bottomrule
\end{longtable}
""", encoding="utf-8")


def representations_table(out: Path):
    lines = {}
    for name, f in (("gs", "matched_estimand_2018_gsladder.txt"), ("pipe", "matched_estimand_2018_pipe.txt")):
        for line in (AD / f).read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if parts and parts[0].startswith("2018_") and len(parts) >= 8:
                lines[parts[0]] = parts[1:6] + [parts[6]]
    order = [("2018_gs_inv100", "quantity constraint, stocks $\\times$1"), ("2018_gs_inv125", "quantity constraint, $\\times$1.25"),
             ("2018_gs_inv150", "quantity constraint, $\\times$1.5"), ("2018_gs", "quantity constraint, $\\times$2"),
             ("2018_baseline", "priced river with closures, $\\times$1"), ("2018_pipe", "priced river with closures, $\\times$2")]
    rows = ["record (with the lagged term) & 1.02 & 1.23 & 1.38 & 1.74 & 0.82 & 6.19 \\\\", "record (contemporaneous term) & 1.02 & 0.51 & 1.02 & 1.02 & 0.10 & 3.67 \\\\"]
    for key, lab in order:
        if key in lines:
            v = lines[key]
            rows.append(f"{lab} & " + " & ".join(v[:5]) + f" & {v[5]} \\\\")
    (out / "si_representations.tex").write_text(r"""\begin{table}[p]
\centering\small
\caption{\textbf{Two representations of the river on the 2018 record.} Monthly shortfall of German industrial production (\%), August to December 2018, and its integral (percent-months): the path implied by the published coefficients, the quantity constraint with the surcharge at four stock levels, and the priced river with closures at two. Runs of 22--28 September 2026 on the reference draw; the industrial path is unchanged by the later treatment of construction as a non-storable input.}
\label{tab:representations}
\begin{tabular}{lrrrrrr}
\toprule
 & Aug & Sep & Oct & Nov & Dec & integral \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


def main(overleaf: Path):
    out = overleaf / "tables"; out.mkdir(exist_ok=True)
    loading_table(out); forecast_table(out); runs_table(out); representations_table(out)
    print("tables written to", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    a = ap.parse_args()
    main(Path(a.overleaf))
