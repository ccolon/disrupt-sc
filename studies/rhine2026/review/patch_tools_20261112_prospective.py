r"""si_tables.py for the author's round of 12 November 2026 (notes N01 and N09). Applied once.

    python studies/rhine2026/review/patch_tools_20261112_prospective.py

N09: the table of the prospective test leaves the main text for Section S6 of the SI. Its block is now `si_prospective`
     and holds the whole table (caption and label inside, as the other tables of the SI). Rows: the low-water days first,
     the published specification, its band, then the model (reference network, mean, lowest and highest of the eleven
     networks). The two loading-curve rows are gone; every row has its sum. The sums of the three network rows are the
     mean, the lowest and the highest of the eleven networks' own sums (each cell of those rows is a statistic of its
     column), written to additional_data/prospective_band_2026_<TAG>.csv in a row 'Jul-Dec'.
     The row of the mean is an addition: the protocol scores the mean of the eleven networks, and its path was printed
     nowhere.
N01: 'loading curve, capacity reduction' for the row of Table S-revision (it was 'loading curve, shortfall').
"""
import re
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "si_tables.py"
raw = P.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
s = raw.replace("\r\n", "\n")

NEW = r'''def prospective_table(out: Path):
    """The prospective test (review NS4, E3): the path that the published specification implies for the low-water days
    of 2026, and the model's monthly industrial shortfall on the reference network, with the mean, the lowest and the
    highest of the eleven networks. 12 Nov 2026 (the author's note): a table of Section S6 of the SI (it was the table
    of the main text); the low-water days first, then the published specification and its band, then the model; the
    two loading-curve rows are gone (their runs are in Table S-revision); every row has its sum. In the three rows on
    the eleven networks each cell is a statistic of its column, the sum included (the lowest sum of a network, not the
    sum of the lowest months)."""
    from matched_estimand_2018 import model_path
    from benchmark_ademmer import record, EVENT_MONTHS
    labs = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    SUM = "Jul-Dec"                                       # the row of the band file that holds the networks' sums
    d = model_path(RUNS / B26, 2026)
    t, s = record(2026, 1)
    ev = t[t.month.isin(EVENT_MONTHS[2026])]

    def cell(v) -> str:
        v = 0.0 if abs(v) < 0.05 else float(v)
        return f"{v:.1f}".replace("-", "$-$")

    def rng(a, b) -> str:
        return f"{cell(a)}--{cell(b)}" if a >= 0 and b >= 0 else f"{cell(a)} to {cell(b)}"

    days = [int(v) for v in ev.low_water_days]
    rows = ["low-water days (observed to 10 November, then the forecasts) & " + " & ".join(str(v) for v in days) + f" & {sum(days)} \\\\",
            "published specification, same low-water days & " + " & ".join(cell(v) for v in ev.central) + f" & {cell(s['integral'])} \\\\",
            "its 16--84\\,\\% band & " + " & ".join(rng(a, b) for a, b in zip(ev.p16, ev.p84)) + f" & {rng(s['p16'], s['p84'])} \\\\",
            "\\midrule",
            "model, reference network & " + " & ".join(cell(d[f"ind_{m}"]) for m in labs) + f" & {cell(d['ind_integrated_pct_months'])} \\\\"]
    seeds = [RUNS / B26] + [RUNS / f"2026_{TAG}_seed{k}_base" for k in range(1, 11)]
    band = AD / ("prospective_band_2026.csv" if TAG == "s07" else f"prospective_band_2026_{TAG}.csv")   # the 7 Oct file was written by read_batch_20261007_rev.py
    if all((r_ / "firm_data.csv").exists() for r_ in seeds):
        import numpy as np
        paths = [d] + [model_path(r_, 2026) for r_ in seeds[1:]]
        a = np.array([[p_[f"ind_{m}"] for m in labs] + [p_["ind_integrated_pct_months"]] for p_ in paths])
        pd.DataFrame({"month": labs + [SUM], "min": a.min(axis=0), "max": a.max(axis=0), "mean": a.mean(axis=0)}).to_csv(band, index=False)
    if band.exists():
        bd = pd.read_csv(band).set_index("month")
        if SUM in bd.index:
            for col, lab in (("mean", "model, mean of the eleven networks"), ("min", "model, lowest of the eleven networks"),
                             ("max", "model, highest of the eleven networks")):
                rows.append(f"{lab} & " + " & ".join(cell(bd.loc[m, col]) for m in labs) + f" & {cell(bd.loc[SUM, col])} \\\\")
    (out / "si_prospective.tex").write_text(r"""\begin{table}[tbp]
\centering\footnotesize\setlength{\tabcolsep}{4pt}
\caption{\textbf{The prospective test.} Days of low water at Kaub (below 78\,cm) and monthly shortfall of German industrial production in 2026 (\%; the production-index measure, each sector's shortfall rate weighted by its German value added, sections B--D): the path that the published specification of ref.~\citep{ademmer2023} implies for these days, with its band, and the model on the river as observed to 10 November 2026, on the reference network and across the eleven networks. In the three rows on the eleven networks, each cell is the mean, the lowest or the highest of the eleven for that column. Negative values are production above the no-event baseline. The last column is the sum of the months (days; percent-months).}
\label{tab:prospective}
\begin{tabular}{L{62mm}rrrrrrr}
\toprule
 & Jul & Aug & Sep & Oct & Nov & Dec & Jul--Dec \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


'''

m = re.search(r"^def prospective_table\(out: Path\):\n.*?(?=^def prospective_sectors_table\(out: Path\):)", s, re.MULTILINE | re.DOTALL)
assert m, "prospective_table not found"
assert "si_prospective.tex" not in s, "already applied"
s = s[:m.start()] + NEW + s[m.end():]

old = 'row("loading curve, shortfall", "as built", "raised by 15" + pc, "tablelow", "tablelow"),'
assert s.count(old) == 1
s = s.replace(old, 'row("loading curve, capacity reduction", "as built", "raised by 15" + pc, "tablelow", "tablelow"),   # 12 Nov 2026: it was "shortfall", the word of the production loss')

P.write_bytes(s.replace("\n", nl).encode("utf-8"))
print("si_tables.py: prospective_table rewritten (block si_prospective), the row of the loading curve renamed")
