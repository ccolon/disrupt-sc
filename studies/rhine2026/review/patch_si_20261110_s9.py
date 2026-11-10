r"""SI revision of 10 Nov 2026, section S9 on the 2018 event (the author's notes N51-N55 and N57-N59; N56 was answered
with S6).

N51      the regression of the benchmark is written as an equation, with the induced growth and its cumulation
N52      'why daily?': the regressor counts the days of a month below 78 cm, hence the daily record; said
N53 N54  the benchmark and its band are those of Fig. validation of the main text: referenced
N55      'check it is correct': it was not. The model's counterpart is aggregated as the production index is
         (shortfall rates weighted by value added over sections B to D, weeks turned into months by their days), not
         'as done in' the benchmark study, and it is a weighted mean of rates, not a sum of weekly losses. Rewritten.
N57 N58  the paragraph on the level of the inventories moves to the sensitivity section, with its values in a small table
N59      the paragraph on the supplier networks, the loading curve and the number of suppliers moves there too
Direct edits corrected: the numbers of low-water days were given in centimeters, with a tilde accent ('29\~cm');
'see Table 2, column 1' pointed to a table of this paper instead of the cited study's.
The section now holds the benchmark and the one choice made on it; its first sentence says where the two other
comparisons are. main.tex: three pointers follow the moved paragraphs, and a note for the author marks the sentence of
the Methods that still counts three choices made on the 2018 benchmark.

    python patch_si_20261110_s9.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")

# ------------------------------------------------------------------ the benchmark and the model's counterpart
d.line("This section documents three modeling choices that were informed by the 2018 event.",
       r"This section documents the benchmark built for the 2018 event and the one choice made against it, the representation of the river. The level of the inventories and the number of suppliers per input were also compared with the benchmark; both stay at their reference values, and the comparison is reported with the sensitivities (Section~S7)."
       + "\n\n"
       + r"\paragraph{The benchmark.} The benchmark is the path of German industrial production that the regression of Ademmer et al.~\citep{ademmer2023} implies for 2018 (column~1 of their Table~2). The regression explains the monthly growth $y_t$ of the production index, in percent, by the change $\Delta d_t$ in the number of days of the month on which the Kaub gauge is below 78\,cm:"
       + "\n" + r"\begin{linenomath*}" + "\n" + r"\begin{equation*}" + "\n"
       + r"y_t = a + \beta_0\,\Delta d_t + \beta_1\,\Delta d_{t-1} + \rho\,y_{t-1} + \text{controls} + \varepsilon_t ,"
       + "\n" + r"\end{equation*}" + "\n" + r"\end{linenomath*}" + "\n"
       + r"with $\beta_0=-0.034$ (standard error 0.012), $\beta_1=-0.024$ (0.014) and $\rho=-0.172$ (0.119). The growth that low water induces is $g_t=\beta_0\,\Delta d_t+\beta_1\,\Delta d_{t-1}+\rho\,g_{t-1}$, and the shortfall of production in month $t$ is its cumulation, $\sum_{s\le t} g_s$. The regressor counts days, which is why the daily record of the gauge is used: 29, 14, 31, 30 and 3 days below 78\,cm from August to December 2018. The monthly shortfall that results is the benchmark of the Results (Fig.~\ref{fig:validation}). The band of that figure is a Monte Carlo over independent normal draws of the three coefficients at their standard errors; their covariance is not published, so the band is indicative.")
d.line("Applied to the low-water days of the daily", None)
d.line("The model's counterpart is the loss of German industrial production, which we build",
       r"The model's counterpart is the shortfall of German industrial production, aggregated as the production index is: the shortfall rate of each sector, weighted by the sector's value added in the German input--output table, over sections B to D (the coverage of the index). Each day takes the value of the model week it belongs to, a month is the mean of its days, and the cumulated shortfall of the event is the sum of the months from August to December, in percent-months.")
d.sub(r"\paragraph{Choice 1: how low water limits transport.}", r"\paragraph{The choice made on the 2018 event: how low water limits transport.}")

# ------------------------------------------------------------------ the two paragraphs that are sensitivities
net = d.get_line(r"\paragraph{The supplier networks, the loading curve and the number of suppliers.")
head = r"\paragraph{The supplier networks, the loading curve and the number of suppliers.\todo{it is not modeling choice but sensitivity}}"
if not net.startswith(head):
    d.fails.append("the paragraph on the supplier networks does not start as expected")
net = r"\paragraph{Supplier networks, loading curve and number of suppliers on the 2018 event.}" + net[len(head):]
d.line(r"\paragraph{The supplier networks, the loading curve and the number of suppliers.", None)
d.line(r"\paragraph{Inventory levels.}", None)
LADDER = (r"\paragraph{The level of the inventories on the 2018 event.} Every inventory target was multiplied by 0.75, 1.25, 1.5 and 2 (Table~\ref{tab:ladder}). The loss falls as the inventories rise. At three quarters of the balance-sheet values the industrial shortfall is nearer the benchmark's \RecordInt{} percent-months than at any other level, but still below its one-standard-deviation band. The balance-sheet values are kept: they are the level that the accounts document, and these runs are a sensitivity, not a calibration. At the balance-sheet values the shortfall is below the benchmark's one-standard-deviation band and inside its 95\,\% band."
          + "\n\n" + "% >>> generated table si_ladder (a table written by hand: its numbers are macros of numbers.tex; the markers let the lint and the gate read it as a table)\n"
          + r"\begin{table}[tbp]" + "\n" + r"\centering\footnotesize" + "\n"
          + r"\caption{\textbf{The level of the inventories on the 2018 event.} Industrial shortfall cumulated from August to December 2018 (percent-months) and German loss (\% of a quarter) when every inventory target is multiplied by a factor. The cumulated shortfall of the benchmark is \RecordInt{} percent-months (one-standard-deviation band \RecordIntLow--\RecordIntHigh).}" + "\n"
          + r"\label{tab:ladder}" + "\n" + r"\begin{tabular}{lrr}" + "\n" + r"\toprule" + "\n"
          + r"inventory targets & industrial shortfall & German loss \\" + "\n"
          + r" & (percent-months) & (\% of a quarter) \\" + "\n" + r"\midrule" + "\n"
          + r"$\times$0.75 & \LadderIntZ & \LadderZ \\" + "\n"
          + r"$\times$1, the balance-sheet values (reference) & \ModelInt & \DEUlossQyy \\" + "\n"
          + r"$\times$1.25 & \LadderIntA & \LadderA \\" + "\n"
          + r"$\times$1.5 & \LadderIntB & \LadderB \\" + "\n"
          + r"$\times$2 & \LadderIntD & \LadderD \\" + "\n"
          + r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"\end{table}" + "\n% <<< generated table si_ladder")
anchor = r"\paragraph{What was not varied.}"
d.sub(anchor, LADDER + "\n\n" + net + "\n\n" + anchor)
d.save()

m = Doc(ov / "main.tex")
m.sub(r"Multiples of these targets are tested in Supplementary Section~S9.", r"Multiples of these targets are tested in Supplementary Section~S7.")
m.sub(r"both below the benchmark's central value (Fig.~\ref{fig:validation}b, Supplementary Section~S9)",
      r"both below the benchmark's central value (Fig.~\ref{fig:validation}b, Supplementary Section~S7)")
m.sub(r"as Supplementary Section~S9 documents; the 2018 comparison as a whole",
      r"as Supplementary Sections~S7 and S9 document\todo{the SI now reports the level of the inventories and the number of suppliers as sensitivities kept at their reference values (Section~S7), and one choice made on 2018, the representation of the river (Section~S9): align this sentence}; the 2018 comparison as a whole")
m.save()
