r"""Submission files after the batch of 11 November 2026 (the 2026 runs on the river as observed): the cover letter says
what is tested, on which statistics, and what will be done when they are released (the author's decision of 11 November:
no numeric threshold, "if the results vary significantly"); the reporting notes follow the manuscript; the README of the
submission folder gets a dated entry. Exact anchors; nothing is written if one is missing.

    python patch_submission_20261111_letter.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

SUB = HERE.parent / "submission"

c = Doc(SUB / "cover_letter.md")
c.sub("# Cover letter (draft of 7 November 2026, for the author's revision)",
      "# Cover letter (draft of 7 November 2026, revised 11 November for the runs on the river as observed; for the author's revision)")
c.sub("""In the summer of 2026 the Rhine, which carries the fuel, ore and building materials of Europe's industrial core,
fell to its lowest levels on record, twice.""",
      """In the summer and autumn of 2026 the Rhine, which carries the fuel, ore and building materials of Europe's industrial
core, fell to its lowest levels on record, twice.""")
c.sub("""low-water season matters more than its depth: the same tonnage turned away in one acute episode costs two fifths more
than spread over the season, and two episodes in sequence cost more than the sum of the two apart because the second
meets inventories the first has drained.""",
      """low-water season matters more than its depth: the same tonnage turned away evenly over the season would cost 45 % less,
and two episodes in sequence cost more than the sum of the two apart because the second meets inventories the first
has drained.""")
c.sub("""The study is designed to be tested. The model was selected on the 2018 event against the published statistical
estimate, which it reproduces within the estimate's uncertainty band, and its 2026 forecast was issued on 7 October
2026, before the production statistics of the autumn, with a pre-specified scoring protocol against the monthly
production index; the hydrological information, code versions and issue dates are recorded in a public manifest.
The code is open (GPL-3.0, github.com/ccolon/disrupt-sc) and every number in the text is generated from the run
outputs.""",
      """The study contains a test that is still open. Every parameter is set from external evidence or calibrated on normal
traffic; one modeling choice, the representation of the river, was made on the 2018 event, whose published statistical
estimate the model reproduces within the estimate's uncertainty band. The model and its parameters were fixed on
2 November 2026, and the simulations use the Rhine as observed to 10 November. The German production indices of
October, November and December are due after submission; the monthly path that the model implies for them and the
scoring rule are in the manuscript and deposited at [DOI]. During review we will score each index on its first
release and report the result, whatever it is. We will also replace the last three weeks of the river profile, which
rest on official forecasts, with the observed record and rerun the reference simulation; if the results vary
significantly, we will rerun all simulations of 2026 and update every number, and otherwise report the comparison in
the Supplementary Information. We will not change the model in response to the statistics. The code is open
(GPL-3.0, github.com/ccolon/disrupt-sc) and every number in the text is generated from the run outputs.""")
c.sub("""mechanism-level answer that statistics alone cannot give, and with a validation and a prospective test that readers
can follow and check.""",
      """mechanism-level answer that statistics alone cannot give, and with a benchmark on 2018 and a test on statistics still
to be published that readers can follow and check.""")
c.save()

r = Doc(SUB / "reporting_summary_notes.md")
r.sub("""recovery weeks. The 2026 forecast was issued on 7 October 2026 on hydrological information to 30 September; the
submitted version uses the observed season [to be stated after the November batch].""",
      """recovery weeks. The model and its parameters were fixed on 2 November 2026. The 2026 runs of 11 November use the Kaub
gauge as observed to 10 November 2026; the last three weeks of the profile rest on the forecasts of the Federal
Institute of Hydrology of 9 and 11 November and are replaced by the observed record at revision.""")
r.sub("""every run folder); the paper's 129 runs are listed in Supplementary Table S[n] with their job lists; regeneration of""",
      """every run folder); the paper's 128 runs are listed in `additional_data/runs_20261111.csv` with their job lists; regeneration of""")
r.sub("""**Blinding.** Not applicable (no human raters). The prospective test is pre-specified: the scoring protocol and the
forecast were fixed before the outcome statistics were published (Methods, "Prospective test").""",
      """**Blinding.** Not applicable (no human raters). The test on the production index is pre-specified: the scoring protocol
was fixed on 9 October 2026 and the model on 2 November, before the indices of October to December 2026 were
published; the index of September, published on 6 November, entered no choice (Methods, "Prospective test").""")
r.save()

d = Doc(SUB / "README.md")
SECTION = """
## Status on 12 November 2026 (the runs on the river as observed)

The 2026 runs were repeated on 11 November on the Kaub gauge as observed to 10 November (record:
`../cluster/batch_20261111.md`; response to the author: `../review/si_revision_20261111_response.md`, sections 10 to 12).
What changes for the package:

- The manuscript no longer presents a forecast with an issue history. It gives an estimate of the season as observed,
  made before the production statistics of October to December. `forecast_manifest.md` has left the repository.
- The headline is 1.22 ± 0.43 % of a quarter of German value added over the eleven networks (it was 1.12 ± 0.41).
- The paper rests on 128 runs, listed in `../additional_data/runs_20261111.csv` with the job list each was launched from.
- `cover_letter.md`: the paragraph on the test says what will be done when the indices of October to December are
  released, without a numeric threshold.
- `reporting_summary_notes.md`: timing, reproducibility and blinding follow the manuscript.
- `build_zenodo_package.py`: no pointer to the manifest. The package leaves out the gauge profiles of earlier states
  of the season (`2026_vintage*.csv`, `2026_q25.csv`, `2026_q75.csv`) and keeps the six-week outlooks of September,
  which the Discussion cites. The package has not been rebuilt: run the script before the upload.
- Not redone on the new text: the word counts and the checks of `natcomms_requirements_20261107.md`.
"""
if "## Status on 12 November 2026" in d.text:
    print("   already applied: README section")
else:
    d.text = d.text.rstrip("\n") + "\n" + SECTION
    d.done += 1
d.save()
