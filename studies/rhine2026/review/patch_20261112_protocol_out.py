r"""The author's decision of 12 November 2026 (evening, in chat): the protocol of the 2026 test leaves the paper.
"Do we really need to ship this 2026 protocol? It exposes to more questions, I think the paper is already good without
it. I would remove S6, put the monthly path by sector and the two prospective tables in S5."

What goes: Section S6 of the SI as a section, with its scoring rule (index, comparator, months, score, verdict), the
dates of the protocol, the signed quarterly changes and the paragraph on the estimates of August 2026 (the main text
carries that comparison); the paragraph "Prospective test" of the Methods; the deposit on Zenodo at submission, which
existed to date the forecast; the sentences of the main text that announce a test.
What stays: the two tables, as plain results of the 2026 season, with a paragraph each (the monthly path of industrial
production against the published specification; the monthly path by sector). They join the section on the 2026 season
(S7, which becomes S6), not S5: S5 gives the reasons for the modeling choices made on 2018. One sentence of the
Discussion says that the monthly path can be compared with the production indices and what such a comparison cannot
show. One sentence of the Methods says that the production indices of 2026 entered no choice.
The sections after S6 are renumbered by review/renumber_si_sections.py (S7 to S9 become S6 to S8).

    python studies/rhine2026/review/patch_20261112_protocol_out.py
    python studies/rhine2026/review/renumber_si_sections.py --shift 7 -1
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

# ====================================================================== main.tex
d = Doc(OVERLEAF / "main.tex")
assert r"\paragraph{Prospective test.}" in d.text, "the protocol is not in the copy (already applied?)"

# Introduction
d.sub(r"Ours is, to our knowledge, the first from a model of supply-chain propagation, with a test against statistics that are still to be published (Supplementary Section~S6).",
      r"Ours is, to our knowledge, the first from a model of supply-chain propagation.")
d.sub(r"most of it in services that cannot make up for lost activity, which the statistics of the autumn of 2026 will test.",
      r"most of it in services that cannot make up for lost activity.")
# Results, the survey of August
d.sub(r"which the survey's sample may explain in part (Supplementary Section~S6).", r"which the survey's sample may explain in part.")

# Discussion: the paragraph on the forecast becomes two sentences at the end of the paragraph before
old_a = r"Here the share follows from one rule: services are not stored and are mostly not made up."
old_b = (r"The 2026 results are a forecast that readers can check. The model's monthly path of German industrial production from July to December 2026 was fixed before the statistics of October to December were published (Supplementary Table~\ref{tab:prospective}). As the production indices are released, they can be compared with this path under a scoring rule set in advance (Supplementary Section~S6): the model fails if it does no better than a forecast of no loss. The turnover indices of the services will test the rule on services in the same way. One gap is already known: the model puts fewer firms in difficulty than the business survey of early August 2026 found (Results).")
d.sub(old_a + "\n\n" + old_b,
      old_a + r" Two comparisons with data remain open. The model's monthly path of German industrial production in 2026 was computed before the statistics of October to December were published (Supplementary Table~\ref{tab:prospective}). It can be compared with the production indices as they are released, although these also carry demand, energy prices, and the industrial trend. And the model puts fewer firms in difficulty than the business survey of early August 2026 found (Results).")

# Methods, Scenarios: what the model did not use, without the dates of the protocol
d.sub(r"The model, its parameters, and the loading curve were fixed on 2 November 2026. The production indices of July, August, and September 2026, released on 7 September, 7 October, and 6 November, entered no choice.",
      r"The production indices of 2026 entered no choice of the model, its parameters, or the loading curve.")

# Methods: the paragraph on the prospective test goes
d.line(r"\paragraph{Prospective test.}", None)

# Data availability: no deposit at submission (it dated the forecast)
d.sub(r"The gauge profile, the monthly path of Supplementary Table~\ref{tab:prospective}, and the run tables of this paper are deposited on Zenodo at submission (Methods). The model's scope data package (network, agents, tables, and scenario files) will be deposited on Zenodo upon acceptance; until then, it is available from the corresponding author.",
      r"The gauge profile, the run tables of this paper, and the model's scope data package (network, agents, tables, and scenario files) will be deposited on Zenodo upon acceptance; until then, they are available from the corresponding author.")
d.save()

# ====================================================================== si.tex
s = Doc(OVERLEAF / "si.tex")
t = s.text

# the two table blocks, kept whole
blocks = {}
for name in ("si_prospective", "si_prospective_sectors"):
    m = re.search(r"^% >>> generated table " + name + r" [^\n]*\n.*?^% <<< generated table " + name + r"[ \t]*\n", t, re.M | re.S)
    assert m, name
    blocks[name] = m.group(0)

# Section S6, from its heading to the heading of S7
a = t.index(r"\subsection*{S6 The 2026 test}")
b = t.index(r"\subsection*{S7 The 2026 season in detail}")
t = t[:a] + t[b:]

# captions: plain results, not a pre-specified test
new_p = blocks["si_prospective"].replace(
    r"\caption{\textbf{The prospective test.} Days of low water at Kaub",
    r"\caption{\textbf{The monthly path of German industrial production, 2026.} Days of low water at Kaub")
assert new_p != blocks["si_prospective"]
new_s = blocks["si_prospective_sectors"].replace(
    r"Pre-specified for the prospective test: the production index gives the industrial rows by month, the turnover index of transport and storage the operators' rows.}",
    r"In the statistics, the production index gives the industrial rows by month, and the turnover index of transport and storage the operators' rows.}")
assert new_s != blocks["si_prospective_sectors"]

# the two paragraphs and their tables, at the end of the section on the 2026 season
para_p = (r"\paragraph{The monthly path of industrial production.} Table~\ref{tab:prospective} gives the model's monthly shortfall of German industrial production from July to December 2026, next to the path that the statistical model of ref.~\citep{ademmer2023} implies for the low-water days of the same months (observed to 10 November, forecast after). The two differ in shape. The model is spiky, with episodes in August and October and a partial recovery in September; on the reference network, it is at baseline in November and above it in December, as the backlogs are worked off. The regression path is smooth and does not rebound. Both are shortfalls against a path without low water. The production index itself also carries demand, energy prices, and the industrial trend, so its level cannot be read against these paths without controls.")
para_s = (r"\paragraph{The monthly path by sector.} Table~\ref{tab:prospective_sectors} gives the monthly production shortfall of the German sectors on the river and of the transport operators in the 2026 runs, the sectoral counterpart of Table~\ref{tab:prospective}: the signatures are the depth of refining and chemicals in August and October, the October low of cement and construction, and the return of every sector on the river to its baseline or above it in December.")
anchor = "% <<< generated table si_cross_waves\n\n\\subsection*{S8 Adaptation levers: how each is built}"
assert t.count(anchor) == 1, t.count(anchor)
t = t.replace(anchor, "% <<< generated table si_cross_waves\n\n" + para_p + "\n\n" + new_p + "\n" + para_s + "\n\n" + new_s
              + "\n\\subsection*{S8 Adaptation levers: how each is built}")

# the opening sentence of the section on the season
old_intro = r"the prices and inputs that go missing, and two checks on the season sequence."
assert t.count(old_intro) == 1
t = t.replace(old_intro, r"the prices and inputs that go missing, two checks on the season sequence, and the monthly path of German production, in total and by sector.")

# a pointer of the loading table that the restructuring of 11 November left behind (the sensitivity runs are in S9)
old_cell = r"tested at 0.04 and 0.16 (Section S7)"
assert t.count(old_cell) == 1
t = t.replace(old_cell, r"tested at 0.04 and 0.16 (Section~S9)")

s.text = t
s.done += 6
s.save()
