r"""Manuscript, batch of 11 November 2026: the rewording for the season as observed (the author's decisions of 11 November:
one profile, the river as observed; the issue history out of the manuscript; the superscript already gone).

WRITTEN BEFORE THE RUNS WERE READ. It holds only the edits that do not depend on the new numbers: where the river comes
from, what was fixed and when, what is tested on which statistics. The sentences that describe results (the shape of the
monthly path, the weeks of the episodes, the worst week, the order of the sensitivity list) are re-read against the new
numbers after this script, by hand.

To run after review/patch_tools_20261111_reading.py and before si_tables.py refreshes the tables (the table of the test
loses a row here, as in the generator). Exact anchors: nothing is written if one is missing.
    python patch_20261111_observed.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

# =====================================================================================================================
m = Doc(OVERLEAF / "main.tex")

# ---- abstract and introduction ----------------------------------------------------------------------------------------
m.sub("For 2026 it forecast, before the autumn's statistics, a loss of",
      "For the 2026 season as observed, it gives, ahead of the production statistics of the last quarter, a loss of")
m.sub("(Methods); the model then forecast the cost of the 2026 event before the autumn statistics were published.",
      "(Methods); the model is then run on the 2026 season as observed, before the production statistics of the last quarter were published.")
m.sub("the first from a model of supply-chain propagation, issued as a forecast and kept for evaluation against the statistics (Supplementary Section~S6).",
      "the first from a model of supply-chain propagation, with a test against statistics that are still to be published (Supplementary Section~S6).")

# ---- Results: the river of 2026 as observed ---------------------------------------------------------------------------
m.sub(r"fell again through September, and in the week of 28 September reached the gauge zero, a conventional datum above the river bed: two "
      r"observed days at 2\,cm, and $-3$\,cm for the rest of the week in the six-week outlook of the Federal Institute of Hydrology, which "
      r"kept Kaub below 60\,cm through the end of October. Everything below for 2026 is a forecast on the river information of 30 September, "
      r"issued on 7 October: fourteen weeks observed, one partly, five from the outlook, and three assumed (Methods).",
      r"fell again through September, and at the turn of October reached the gauge zero, a conventional datum above the river bed: the "
      r"weekly mean was 2\,cm in the week of 28 September, and the daily mean $-5$\,cm on 1 October. It stayed below 25\,cm until late "
      r"October, rose to 45\,cm in the week of 26 October and fell back to 18\,cm in the first week of November. The record ends on "
      r"10 November; for the days after it the profile follows the forecasts of the Federal Institute of Hydrology, which have the river "
      r"above 130\,cm from 16 November (Methods).")
m.sub("with the observed weeks, the partly observed week of 28 September, the six-week outlook of 28 September and the assumed recovery "
      "shaded, and the share",
      "with the weeks that rest on forecasts shaded (from 9 November), and the share")

# ---- Discussion ------------------------------------------------------------------------------------------------------
m.sub("the production indices for September 2026 (published on 6 November 2026, after the forecast was frozen), October and November, "
      "scored at revision under the protocol of Supplementary Section~S6, and the turnover indices of the services;",
      "the production indices for September 2026 (published on 6 November 2026, after the model was fixed), October, November and "
      "December, scored under the protocol of Supplementary Section~S6 as they are released, and the turnover indices of the services;")
m.sub(r" The 2026 season is a forecast (Results), whose 25th- and 75th-percentile stress paths give \RevQLow{} and \RevQHigh\,\% of a "
      r"quarter. And the transport channel", " And the transport channel")
m.sub("Five limitations bound the reading.", "Four limitations bound the reading.")

# ---- Methods: scenarios ----------------------------------------------------------------------------------------------
m.line(r"\paragraph{Scenarios.}",
       r"\paragraph{Scenarios.} The 2026 weekly profile of the Kaub gauge (23 weeks from 22 June, followed by 20 weeks of recovery) is the "
       r"river as observed: the weekly mean of the PEGELONLINE record of the German waterway administration \citep{pegelonline2026} for "
       r"the 20 weeks from 22 June to 8 November 2026. The last three weeks rest in part on the forecasts of the Federal Institute of "
       r"Hydrology (BfG): the week of 9 November takes two observed days and, for the five others, the daily medians of the 14-day "
       r"forecast of 11 November \citep{bfg2026fourteen}; the week of 16 November takes the same forecast, and the week of 23 November the "
       r"median of the six-week outlook of 9 November \citep{bfg2026}. These forecasts have the river above 130\,cm from 16 November "
       r"(weeks flagged in Fig.~\ref{fig:event}). The model, its parameters and the loading curve were fixed on 2 November 2026. The "
       r"production indices of July, August and September 2026, released on 7 September, 7 October and 6 November, entered no choice.")

# ---- Methods: the test on the production statistics -------------------------------------------------------------------
m.line(r"\paragraph{Prospective test.}",
       r"\paragraph{Prospective test.} The 2026 results can be proved wrong by statistics that were not published when this estimate was "
       r"made. Table~\ref{tab:prospective} gives the model's monthly shortfall of German industrial production from July to December 2026 "
       r"on the reference network, with the range of the eleven networks and of the two loading curves, against the path that the "
       r"published specification implies for the same months and the same low-water days. The protocol, fixed on 9 October 2026 and "
       r"detailed in Supplementary Section~S6, scores the reference network's series, and the mean over the eleven networks alongside it, "
       r"against the Destatis production index of industry (sections B to D, seasonally and calendar adjusted, first release) for "
       r"September to December 2026, each month's shortfall relative to the index's mean over January to June 2026, by the mean absolute "
       r"error over the four months against the same score for a zero path and for the published specification; the model is judged "
       r"wrong if its score exceeds the zero path's. The index of September was released on 6 November 2026, after the model was fixed "
       r"and before the runs of this paper; those of October, November and December are released after submission, and the score over "
       r"these three months is reported alongside. The index relative to its pre-event level carries demand, energy prices and the "
       r"industrial trend as well as the low water, so the score measures predictive performance on a fixed-baseline proxy and does not "
       r"validate the causal loss, which no single realization can. The sectoral signatures and the signed quarterly changes the model "
       r"implies are given in Supplementary Section~S6 and Table~\ref{tab:prospective_sectors}.")
m.sub(r"(\%; the production-index measure, each sector's shortfall rate weighted by its German value added, sections B--D, with the "
      r"production-weighted B--E series of the earlier version for comparison): the model on the reference network (river information of "
      r"30 September, issued 7 October, rerun on 2 November on the capacities per cargo class), and the path",
      r"(\%; the production-index measure, each sector's shortfall rate weighted by its German value added, sections B--D): the model on "
      r"the reference network, on the river as observed to 10 November 2026, and the path")
inner = m.block("prospective")
if inner:
    rows = inner.split("\n")
    drop = [i for i, ln in enumerate(rows) if ln.startswith("model, reference network, production-weighted B--E (the earlier version's measure) &")]
    first = [i for i, ln in enumerate(rows) if ln.startswith("model, reference network, index measure &")]
    days = [i for i, ln in enumerate(rows) if ln.startswith("low-water days (observed to 29 September, then the profile) &")]
    if (len(drop), len(first), len(days)) == (1, 1, 1):
        rows[first[0]] = rows[first[0]].replace("model, reference network, index measure &", "model, reference network &", 1)
        rows[days[0]] = rows[days[0]].replace("low-water days (observed to 29 September, then the profile) &",
                                              "low-water days (observed to 10 November, then the forecasts) &", 1)
        del rows[drop[0]]
        m.block("prospective", "\n".join(rows))
    elif any(ln.startswith("low-water days (observed to 10 November, then the forecasts) &") for ln in rows):
        print("   already applied: the table of the test")
    else:
        m.fails.append(f"table of the test: rows found {len(drop)}, {len(first)}, {len(days)} (expected one each)")

# ---- Data and code availability --------------------------------------------------------------------------------------
m.sub(r"and the six-week outlooks from the Federal Institute of Hydrology \citep{bfg2026};",
      r"and the forecasts from the Federal Institute of Hydrology \citep{bfg2026fourteen,bfg2026};")
m.sub(r"; the runs of this paper use the versions recorded, commit by commit, in the forecast manifest of that repository "
      r"(\texttt{studies/\allowbreak rhine2026/\allowbreak forecast\_manifest.md}), and the study scripts",
      "; the study scripts")
m.save()

# =====================================================================================================================
s = Doc(OVERLEAF / "si.tex")

# ---- S3: the gauges --------------------------------------------------------------------------------------------------
s.sub(r"The 2026 profile (Table~\ref{tab:gate}) takes the observations to 29 September, the six-week outlook of the same institute of "
      r"28 September \citep{bfg2026} and an assumed recovery after it. To account for the outlook's uncertainty, we build two additional "
      r"profiles from its 25th and 75th percentiles for the forecast weeks as sensitivities (Section~S9).",
      r"The 2026 profile (Table~\ref{tab:gate}) is observed for its first 20 weeks, to 8 November. The week of 9 November takes its two "
      r"observed days and, for the five others, the daily medians of the institute's 14-day forecast of 11 November "
      r"\citep{bfg2026fourteen}; the week of 16 November is the mean of the daily medians of the same forecast, and the week of 23 November "
      r"the median of the six-week outlook of 9 November \citep{bfg2026}.")

# ---- S6: the protocol ------------------------------------------------------------------------------------------------
s.sub(r"\paragraph{The prospective test: protocol.} ", r"\paragraph{The protocol.} ")
s.sub("(observed to 29 September, the outlook and the assumed recovery after;", "(observed to 10 November, the forecasts after;")
s.sub("The protocol is fixed here; the series scored is the reference network's, as issued on 7 October, and the mean over the eleven "
      "networks, the headline of this paper, is scored alongside it.",
      "The protocol was fixed on 9 October 2026. The series scored is the reference network's, and the mean over the eleven networks, the "
      "headline of this paper, is scored alongside it.")
s.sub("Months: September to December 2026; the first release for September was published on 6 November 2026, after the forecast was "
      "frozen, October's is due in the second week of December and November's in January 2027 (July and August are retrospective, "
      "released on 7 September and 7 October).",
      "Months: September to December 2026. The first release for September was published on 6 November 2026, after the model was fixed "
      "on 2 November and before the runs of this paper; those for October, November and December are due in December 2026, January and "
      "February 2027, after submission, and the score over these three months is reported alongside (the releases for July and August, of "
      "7 September and 7 October, are not scored).")
s.sub("and the published specification; the forecast is judged wrong if its score exceeds the zero path's.",
      "and the published specification; the model is judged wrong if its score exceeds the zero path's.")
s.sub("Two comparisons are made on common information: the forecasts as issued, the model on the outlook of 28 September and the published "
      "specification on the low-water days of the same profile; and the conditional responses once the season is over, the model rerun on "
      "the observed gauges and the specification on the realized days. The first scores the forecast, the second the response; their "
      "difference is not an additive decomposition of the error in a nonlinear model.",
      "The model and the published specification are compared on the same river: the profile of this paper and its low-water days. The "
      "days after 10 November rest on forecasts and are replaced by the observed record at revision.")
s.sub(r"\paragraph{Sectoral signatures of the forecast.} ", r"\paragraph{The monthly path by sector.} ")
s.sub("of the transport operators in the 2026 forecast, the sectoral counterpart", "of the transport operators in the 2026 runs, the sectoral counterpart")
s.sub(r"\caption{\textbf{Sectoral signatures of the 2026 forecast.}", r"\caption{\textbf{The monthly path of the sectors on the river, 2026.}")
s.sub("of the transport operators, reference network, river information of 30 September; rerun on 2 November on the capacities per cargo "
      "class; the last column", "of the transport operators, reference network; the last column")

# ---- S7: the status of the weeks in the weekly table of Kaub ---------------------------------------------------------
inner = s.block("si_gate")
if inner:
    status = {**{w: "observed" for w in range(15, 21)}, 21: "observed+forecast", 22: "forecast", 23: "forecast"}
    n = 0

    def fix(mo):
        global n
        w = int(mo.group(1))
        if w in status and mo.group(3) != status[w]:
            n += 1
            return f"{mo.group(1)} & {mo.group(2)} & {status[w]} &"
        return mo.group(0)
    new = re.sub(r"^(\d+) & (\d{4}-\d{2}-\d{2}) & ([a-z+ ]+) &", fix, inner, flags=re.M)
    if n:
        s.block("si_gate", new)
        print(f"   status of {n} weeks updated in the weekly table of Kaub")

# ---- S9: the stress paths on the outlook are gone --------------------------------------------------------------------
s.sub("    \\item \\emph{The gauge of the forecast weeks.} The outlook's 25th and 75th percentile paths give \\RevQLow{} and \\RevQHigh\\,\\% "
      "of a quarter against \\DEUlossQ{} for the median path.\n", "")
inner = s.block("si_revision")
if inner:
    rows = inner.split("\n")
    g = [i for i, ln in enumerate(rows) if ln.startswith("gauge of the forecast weeks & outlook's median & 25th percentile &")]
    if len(g) == 1 and rows[g[0] + 1].startswith(" &  & 75th percentile &"):
        del rows[g[0]:g[0] + 2]
        s.block("si_revision", "\n".join(rows))
    elif not g:
        print("   already applied: the rows on the gauge of the forecast weeks")
    else:
        s.fails.append("sensitivity table: the two rows on the gauge of the forecast weeks are not as expected")
s.save()

# =====================================================================================================================
# refs.bib: the record and the forecasts used by the profile of 11 November
p = OVERLEAF / "refs.bib"
raw = p.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
changed = 0
OLD_P = r"howpublished = {\url{https://www.pegelonline.wsv.de/}, REST API, data retrieved 10 and 30 September 2026 (DL-DE->Zero-2.0)}"
NEW_P = r"howpublished = {\url{https://www.pegelonline.wsv.de/}, REST API and long-term download, data retrieved to 11 November 2026 (DL-DE->Zero-2.0)}"
OLD_B = r"howpublished = {Vintages of 7 and 28 September 2026, \url{https://vorhersage.bafg.de/6-Wochen-Vorhersage/Rhein-Kaub_6Wochen_Wasserstand_QuansBox.csv}}"
NEW_B = r"howpublished = {Issues of 7 and 28 September and of 9 November 2026, \url{https://vorhersage.bafg.de/6-Wochen-Vorhersage/Rhein-Kaub_6Wochen_Wasserstand_QuansBox.csv}}"
for old, new in ((OLD_P, NEW_P), (OLD_B, NEW_B)):
    if t.count(old) == 1:
        t = t.replace(old, new); changed += 1
    elif new not in t:
        sys.exit(f"refs.bib: anchor not found: {old[:70]}")
if "{bfg2026fourteen," not in t:
    t = t.rstrip("\n") + "\n" + r"""
@misc{bfg2026fourteen,
  author       = {{Bundesanstalt f{\"u}r Gew{\"a}sserkunde}},
  title        = {14-{Tage}-{Vorhersage} {Kaub}: probabilistic forecast of the daily mean water level},
  year         = {2026},
  howpublished = {Issue of 11 November 2026, \url{https://vorhersage.bafg.de/14-Tage-Vorhersage/Kaub_Quantile_25700100.csv}}
}
"""
    changed += 1
if changed:
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
print(f"refs.bib: {changed} change(s)")
