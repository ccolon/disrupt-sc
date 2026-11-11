r"""Manuscript, batch of 11 November 2026: the sentences bound to numbers, re-read after the runs on the river as observed
were read (paper_gate.py lists them: eight claims out of their range, two fraction words). To run after
patch_20261111_observed.py and after make_numbers.py has the macros FlatLess, RevSeaRateThree, DEUlossQThree and
RevSeaRateRelOne. Exact anchors: nothing is written if one is missing.

main.tex
  abstract          the record lows are of the summer and the autumn; "the last quarter" named as October to December
  introduction      the flat profile and the interaction as numbers (45 % and 12 %; they were "two fifths" and "a sixth");
                    the fleet "more than a fifth" (23 %)
  Results           the heading (the autumn costs 2.9 times August, it was 2.4), the episode sentence on the observed weeks
                    (ten weeks below 50 cm from 7 September, eight below 30 cm), the flat profile as a number
  Discussion        "a fifth more" (19 %; it was a quarter), the September outlooks cited, pooling divides the loss by about
                    three and a half (3.4; it was three), the fleet "more than a fifth"
si.tex
  S6                November is at the baseline on the reference network (it was a rebound); chemicals are at their baseline
                    in December, the other sectors above
  S8                the no-rail runs do not keep the peak weeks (they did not on 2 November either); under the rail ceiling
                    the fairway removes the same share, the others more, and the targeted inventories pass the fleet
  S9, table S1      the sea rate to one decimal
    python patch_20261111_results.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

m = Doc(OVERLEAF / "main.tex")
# ---- abstract
m.sub("and in the summer of 2026 the Rhine fell to its lowest levels on record.",
      "and in the summer and autumn of 2026 the Rhine fell to its lowest levels on record.")
m.sub("it gives, ahead of the production statistics of the last quarter, a loss of",
      "it gives, ahead of the production statistics of October to December, a loss of")
# ---- introduction
m.sub("before the production statistics of the last quarter were published.",
      "before the production statistics of October to December were published.")
m.sub("the same shortfall of river capacity spread evenly would cost two fifths less, and the two low-water episodes of 2026 cost a sixth "
      "more in sequence than apart.",
      r"the same shortfall of river capacity spread evenly would cost \FlatLess\,\% less, and the two low-water episodes of 2026 cost "
      r"\WaveInterShare\,\% more in sequence than apart.")
m.sub("each remove two fifths of the loss and a fleet built for low water a fifth;",
      "each remove two fifths of the loss and a fleet built for low water more than a fifth;")
# ---- Results
m.sub(r"\subsection*{The 2026 event: a loss that builds from July and more than doubles in the autumn}",
      r"\subsection*{The 2026 event: a loss that builds from July and nearly triples in the autumn}")
m.sub(r"the autumn episode, seven weeks at or below 36\,cm from 7 September, costs \AutumnWaveQ\,\%, more than twice as much, because",
      r"the autumn episode, ten weeks below 50\,cm from 7 September, eight of them below 30\,cm, costs \AutumnWaveQ\,\%, nearly three "
      r"times as much, because")
m.sub(r"costs \FlatQ\,\%, about two fifths less than the season as it happened,",
      r"costs \FlatQ\,\%, \FlatLess\,\% less than the season as it happened,")
# ---- Discussion
m.sub("and the second costs a quarter more than it would have alone,",
      "and the second costs a fifth more than it would have alone,")
m.sub("The six-week outlooks of the Federal Institute of Hydrology, which in September 2026 correctly predicted",
      r"The six-week outlooks of the Federal Institute of Hydrology \citep{bfg2026}, which in September 2026 correctly predicted")
m.sub("divides the loss by three compared with a model that keys every input to its region",
      "divides the loss by about three and a half compared with a model that keys every input to its region")
m.save()

s = Doc(OVERLEAF / "si.tex")
# ---- S6
s.sub("and it rebounds above the baseline in November and December as the backlogs are worked off; the regression path is smooth and does "
      "not rebound.",
      "and on the reference network it is at the baseline in November and above it in December, as the backlogs are worked off; the "
      "regression path is smooth and does not rebound.")
s.sub("cement and construction at their deepest in October, and every sector on the river above baseline in December.",
      "cement and construction at their deepest in October, and every sector on the river at or above its baseline in December.")
s.sub("and the rebound of every sector on the river above its baseline in December.",
      "and the return of every sector on the river to its baseline or above it in December.")
# ---- S8
s.sub(r"(\RevNoRailyyAbs\,\% more), with the same peak weeks (Table~\ref{tab:revision}).",
      r"(\RevNoRailyyAbs\,\% more; Table~\ref{tab:revision}).")
s.sub(r"Under the ceiling each lever removes a larger share of a smaller loss than under the paper's rule (inventories \CrossStockRail\,\% "
      r"against \LevStock, fairway \CrossDeepRail{} against \LevDeep, targeted inventories \CrossStockTRail{} against \LevStockT, fleet "
      r"\CrossFleetRail{} against \LevFleet), in the same order.",
      r"Under the ceiling the levers remove the same or a larger share of a smaller loss than under the paper's rule (inventories "
      r"\CrossStockRail\,\% against \LevStock, fairway \CrossDeepRail{} against \LevDeep, targeted inventories \CrossStockTRail{} against "
      r"\LevStockT, fleet \CrossFleetRail{} against \LevFleet); the targeted inventories gain the most and pass the fleet.")
# ---- S9 and the table of the transport costs: the sea rate to one decimal
s.sub(r"the 2026 loss is \RevSeaRate\,\% of a quarter instead of \DEUlossQ{} (\RevSeaRateRel\,\%). The smallest effect of the table.",
      r"the 2026 loss is \RevSeaRateThree\,\% of a quarter instead of \DEUlossQThree{} (\RevSeaRateRelOne\,\%). The smallest effect of "
      r"the table.")
s.sub(r"a run with bulk at these two rates changes the 2026 loss by \RevSeaRateRel\,\% (Section~S9).",
      r"a run with bulk at these two rates changes the 2026 loss by \RevSeaRateRelOne\,\% (Section~S9).")
s.save()
