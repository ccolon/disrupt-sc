r"""The submission folder after the protocol of the 2026 test left the paper (12 November 2026, evening): the cover
letter no longer announces a test that will be scored during review, the note on blinding of the reporting summary
follows the Methods, and the README records the state. Applied once.

    python studies/rhine2026/review/patch_submission_20261112_protocol_out.py
"""
from pathlib import Path

SUB = Path(__file__).resolve().parents[1] / "submission"


def edit(name: str, pairs) -> None:
    p = SUB / name
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    s = raw.replace("\r\n", "\n")
    for old, new in pairs:
        assert s.count(old) == 1, (name, s.count(old), old[:70])
        s = s.replace(old, new)
    p.write_bytes(s.replace("\n", nl).encode("utf-8"))
    print(f"{name}: {len(pairs)} edit(s)")


edit("cover_letter.md", [
    ("""The study contains a test that is still open. Every parameter is set from external evidence or calibrated on normal
traffic; one modeling choice, the representation of the river, was made on the 2018 event, whose published statistical
estimate the model reproduces within the estimate's uncertainty band. The model and its parameters were fixed on
2 November 2026, and the simulations use the Rhine as observed to 10 November. The German production indices of
October, November and December are due after submission; the monthly path that the model implies for them and the
scoring rule are in the manuscript and deposited at [DOI]. During review we will score each index on its first
release and report the result, whatever it is. We will also replace the last three weeks of the river profile, which
rest on official forecasts, with the observed record and rerun the reference simulation; if the results vary
significantly, we will rerun all simulations of 2026 and update every number, and otherwise report the comparison in
the Supplementary Information. We will not change the model in response to the statistics. The code is open
(GPL-3.0, github.com/ccolon/disrupt-sc) and every number in the text is generated from the run outputs. The estimates of the 2026 event made during the summer extrapolated the 2018 statistics or ran a regional
model of the Rhine corridor; this is the first from a model of supply-chain propagation.""",
     """Every parameter is set from external evidence or calibrated on normal traffic; one modeling choice, the
representation of the river, was made on the 2018 event, whose published statistical estimate the model reproduces
within the estimate's uncertainty band. The simulations use the Rhine as observed to 10 November 2026. The last three
weeks of the river profile rest on official forecasts. During review we will replace them with the observed record and
rerun the reference simulation; if the results vary significantly, we will rerun all simulations of 2026 and update
every number, and otherwise report the comparison in the Supplementary Information. The estimate was made before the
German production statistics of October to December 2026 were published; the monthly path that the model implies is
given in the Supplementary Information. The code is open (GPL-3.0, github.com/ccolon/disrupt-sc) and every number in
the text is generated from the run outputs. The estimates of the 2026 event made during the summer extrapolated the
2018 statistics or ran a regional model of the Rhine corridor; this is the first from a model of supply-chain
propagation."""),
    ("""mechanism-level answer that statistics alone cannot give, and with a benchmark on 2018 and a test on statistics still
to be published that readers can follow and check.""",
     """mechanism-level answer that statistics alone cannot give, and with a benchmark on the 2018 event."""),
])

edit("reporting_summary_notes.md", [
    ("""**Blinding.** Not applicable (no human raters). The test on the production index is pre-specified: the scoring protocol
was fixed on 9 October 2026 and the model on 2 November, before the indices of October to December 2026 were
published; the index of September, published on 6 November, entered no choice (Methods, "Prospective test").""",
     """**Blinding.** Not applicable (no human raters). The production indices of 2026 entered no choice of the model, its
parameters or the loading curve (Methods, "Scenarios"); the indices of October to December 2026 were not published when
the runs were made."""),
])

p = SUB / "README.md"
raw = p.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
s = raw.replace("\r\n", "\n").rstrip("\n") + "\n"
assert "the protocol of the 2026 test left the paper" not in s
s += """
## Status on 12 November 2026, late evening (the protocol of the 2026 test left the paper)

The author's decision in chat, after the round above: the paper does not ship the protocol of the 2026 test. Record:
`../review/revision_20261112_response.md`, section 9. What changes for the package:

- The SI has eight sections. The former S6 ("The 2026 test") is gone; S7 to S9 are now S6 to S8. The two monthly tables
  (industrial production against the published specification; the sectors on the river) are results of Section S6,
  "The 2026 season in detail".
- The Methods have no paragraph "Prospective test". Nothing is deposited on Zenodo at submission: the data statement
  says "upon acceptance" for the gauge profile, the run tables and the scope data package. One red note is left in
  `main.tex`, for the DOI of the code release.
- `cover_letter.md`: the paragraph that announced a test scored during review is rewritten. It keeps the replacement of
  the three forecast weeks of the river profile at revision.
- `reporting_summary_notes.md`: the note on blinding follows the Methods.
- Counts by `wordcount.py`: abstract 167 words, main text 5,270 (guide 5,000), Methods 2,860 (guide 3,000).
- The older lines of this file that name sections of the SI (S4 to S10) describe earlier states.
"""
p.write_bytes(s.replace("\n", nl).encode("utf-8"))
print("README.md: status added")
