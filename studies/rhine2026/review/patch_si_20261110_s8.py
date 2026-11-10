r"""SI revision of 10 Nov 2026, section S8 Rail (the author's notes N49-N50 and the direct edit E45).

N49  The opening said 'Rail is a bounded substitute in this study, not a lever', which the author found hard to
     follow, and which contradicted the main text ('Rail is a lever whose size the model cannot set'). The section
     now opens as the main text does and says why rail is reported as a sensitivity.
N50  The 6.7 Mt of rail freight a week had no source. The sentence gives the estimate it is applied to (Kiel Working
     Paper 2155, Appendix B: +0.07 % of rail tonnage per low-water day), says that 6.7 Mt a week is the order of the
     German total, and cites the official figure nearest to it (362 Mt in 2024, 7.0 Mt a week).
E45  Typos and units of the rewritten list ('eligigle', a sentence without 'that', percentages without their sign).
main.tex: 'The ceiling is reached in nearly every week of both events' cited the table of the crossed levers; it now
cites the week-by-week table of the rail runs (tab:railweeks).

    python patch_si_20261110_s8.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")
d.line("Rail is a bounded substitute in this study, not a lever",
       r"Rail is a lever whose size the model cannot set: what limits it is not the price of a train but the number of trains that can be added at short notice, which is not known. It is therefore reported as a sensitivity, not as a sized lever like those of the main text. In the model, containers can reroute by rail and road without a limit, but bulk cannot switch mode: tank barges and ore trains have no road or rail equivalent at volume during an event (Section~S4). There is one exception: a shipment whose normal route already has a leg of 100\,km or more by rail may be rerouted entirely by rail, at no penalty. About 15\,\% of the bulk orders that cross Kaub have such a route.")
d.line("We have no data on the share of the Kaub traffic that travels on a combined rail--barge route",
       r"We have no data on the share of the Kaub traffic that travels on a combined rail--barge route, so we test the 100\,km threshold, which decides how much bulk is eligible, and a ceiling on the tonnage of bulk that may switch to rail.")
d.line(r"    \item Raising the 100-km-threshold to 500\,km leaves no bulk shipment a rail alternative",
       r"    \item Raising the threshold from 100 to 500\,km leaves no bulk shipment a rail alternative: the 2026 loss rises from \DEUlossQ{} to \RevNoRail\,\% of a quarter (\RevNoRailAbs\,\% more) and the 2018 loss from \DEUlossQyy{} to \RevNoRailyy\,\% (\RevNoRailyyAbs\,\% more), with the same peak weeks (Table~\ref{tab:revision}).")
d.line(r"    \item We test a ceiling on the tonnage of bulk can be rerouted per rail per week.",
       r"    \item In two further runs, the bulk that is cut at Kaub may switch to rail up to a weekly ceiling. A ceiling of 50 kt approximates the 400 wagons that the national rail freight operator said it could add at short notice in August 2026, at two rotations a week and 62.5 t per wagon \citep{dbcargo2026}. It reduces the 2026 loss by \RevRailFiftyAbs\,\% and the 2018 loss by \RevRailFiftyyyAbs\,\%; in 2018 the industrial shortfall falls to \RevRailFiftyInt{} percent-months, against \RecordInt{} for the benchmark (band \RecordIntLow--\RecordIntHigh).")
d.line(r"    \item A higher ceiling of 140 kt is analyzed, loosely based on Appendix B",
       r"    \item A higher ceiling of 140 kt follows the response of rail freight to past low waters. The working-paper version of the study of Ademmer et al.~\citep{ademmer2020} estimates, in its Appendix B, that a day of low water raises rail tonnage by 0.07\,\%, that is about 2\,\% over a low-water month of 30 days. Applied to about 6.7 Mt of rail freight a week, the order of the German total (362 Mt in 2024, or 7.0 Mt a week \citep{destatis2026gueterbefoerderung}), this gives about 140 kt a week. The estimate covers all cargo, including the containers that the model already lets switch and that do not count against the ceiling, so 140 kt for bulk alone is likely more than rail can take on. This ceiling reduces the 2026 loss by \RevRailHundredFortyAbs\,\% and the 2018 loss by \RevRailHundredFortyyyAbs\,\%; in 2018 the industrial shortfall falls to \RevRailHundredFortyInt{} percent-months.")
d.save()

m = Doc(ov / "main.tex")
m.sub(r"The ceiling is reached in nearly every week of both events (Supplementary Table~\ref{tab:cross}).",
      r"The ceiling is reached in nearly every week of both events (Supplementary Table~\ref{tab:railweeks}).")
m.save()
