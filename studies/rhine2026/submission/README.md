# Submission package: Rhine 2026 paper, Nature Communications

Started 7 November 2026 (phase 6 of the paper pipeline: venue checks, scoop search, cover letter, statements,
reviewers). The manuscript lives in Overleaf (git bridge working copy
`C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f`); this folder holds what
the submission needs besides the manuscript, and the scripts that build the files to upload.

## Contents

| File | What it is |
|---|---|
| `natcomms_requirements_20261107.md` | every requirement of the journal's pages (quoted, with the URL) against the manuscript: status PASS / ACTION / DECISION / LATER, and the order of the final steps |
| `cover_letter.md` | the cover letter (final text of 13 November, for double-anonymised review: it carries the author information removed from the manuscript); brackets for what only the author can settle |
| `build_cover_letter.py` | builds `cover_letter.docx` from `cover_letter.md` (e-mail read from the Overleaf copy, ORCID from `--orcid`, today's date) |
| `build_review_code_archive.py` | builds `code_for_review_anonymous.zip`, the code for the reviewers under double-anonymised review (model, tests and study scripts; text files only; identifying strings replaced), and searches the archive for what is left |
| `suggested_reviewers.md` | reviewer candidates by expertise and exclusions to consider, for the author to vet |
| `reporting_summary_notes.md` | drafted answers for the Nature Portfolio reporting summary, if the editor asks for it |
| `build_submission.py` | with `--anonymous`: `main_text_anonymous.pdf` and `supplementary_information_anonymous.pdf` (no author block, funding or author contributions, no repository address, earlier work in the third person; metadata removed; searched for identifying strings). Without: builds `main_text.pdf` (manuscript without the SI), `supplementary_information.pdf` (the SI as its own document, own reference list) and `combined.pdf` in a temporary copy of the Overleaf folder; prints the word counts and the page counts; fails on an engine error or an unresolved reference |
| `wordcount.py` | the counts against the journal's guide (title 15, abstract 200, main text 5,000, Methods 3,000, legends 350, references 70, display items 10), macros expanded |
| `build_zenodo_package.py` | builds the Zenodo deposit of the EU data package (zip, README with provenance and licences, sha256 manifest, metadata draft, build report) in `C:/dsc_runs/rhine2026/zenodo/`; uploads nothing |

The split build rests on three additions to the Overleaf copy (7 November 2026): `xr-hyper` in the preamble of
`main.tex` with two `\externaldocument` lines placed after `\input{numbers}`, a `\standalonesi` / `\nosupplement`
switch around the document body (lower-case names: the gate reads every upper-case `\Name` as a numbers.tex macro),
and the one-line wrappers `maintext.tex` and `supplement.tex` (no underscores: the lint). Overleaf keeps compiling
`main.tex` as before (main text followed by the SI), and `paper_gate.py` is unchanged.

```
python studies/rhine2026/submission/build_submission.py              # -> C:/dsc_runs/rhine2026/submission/
python studies/rhine2026/submission/wordcount.py                     # counts only
python studies/rhine2026/submission/build_zenodo_package.py          # -> C:/dsc_runs/rhine2026/zenodo/ (not uploaded)
```

## Status on 7 November 2026

Built and checked: `main_text.pdf` 30 pages (4.7 MB), `supplementary_information.pdf` 38 pages (4.6 MB), no
unresolved reference in either. Within the guide: title (15 words), abstract (186), legends (74 to 194), display
items (7), references (44 cited). Over the guide: main text 6,773 words against 5,000, Methods 4,784 against 3,000
(the journal: "within reason, style and length will not directly influence consideration"; see the requirements
file for the trimming options). Statements added to the manuscript: Code availability (written), Author
contributions, Competing interests, Funding (placeholder), Acknowledgements (placeholder), the affiliation line, and
an AI-use paragraph in Methods for the author to confirm.

Positioning review (same day, evening): the dossiers `../evidence/positioning_eu_econ_models_20261107.md` (EU-wide
economic models), `positioning_model_state_of_art_20261107.md` (the model's relatives), `positioning_scoop_recent_20261107.md`
(scoop search and the 2026 analyses) and `positioning_transport_rhine_20261107.md` (transport models and the Rhine),
with the synthesis `positioning_synthesis_20261107.md`. The manuscript took the edits the same evening
(Overleaf): the Introduction's state-of-the-art paragraph and novelty claim, the ex-ante estimates of 2026 (Kiel,
Commerzbank, Prognos), the 2018 GDP figure (about 0.4 % at the trough after Ademmer et al. 2023, 0.2 to 0.3 % over the two quarters after
Jannsen and Meuchelboeck 2026), the Kaub and transport-economics citations, and five Discussion sentences; the bibliography grew from 61 to 85 entries (69 cited, DOIs verified on Crossref or DataCite). The main
text is now 7,181 words (Introduction 1,323), which adds to the length decision above.

Trim (7 November, night): the main text went from 7,190 to 5,473 words (Introduction 1,225, Results 2,750, Discussion
1,498) and the Methods from 4,784 to 3,115, in three passes that removed the restatements between the sections and moved
the detail to the Supplementary Information with its ledger entries: S2 the residual tonnages of the Rhine stations and
the port tonnages; S3 the issue history of the forecast, the monthly loading shares, which reaches saturate, the full
prospective-test protocol and the comparison with the estimates of August 2026; S5 the surcharge maximum and the French
chain; S7 the list of sensitivity runs and crossed experiments; S8 the coverage of the rail regression; S10 the equations
of the weekly sequence, the run horizon and the mechanics of the fleet's peak week. Same night: the funding statement
(main.tex and the cover letter), Kriedel 2019, Streng 2020 and Scholten 2014 cited (87 entries, 72 cited), the Discussion
sentence on the September production index (published on 6 November, after the forecast was frozen; scored at revision),
the dbcargo2026 note corrected (about 400 wagons at short notice; the larger figures came from the trade press), and the
Zenodo package built (`build_zenodo_package.py`). `paper_gate.py` is green except the two pending SI items it has carried
since 5 November (the 140 Mt of the port ladder, the 6.7 Mt a week of rail freight).

Open before upload (the author): acknowledgements, the e-mail, the AI-use wording, the Zenodo upload (data package ready;
ORCID, release tag and DOIs to add) and the code release, the November batch on the observed season (daggers and todos
removed), the reviewer list with contact details, the preprint decision, the APC arrangement. Details and the order
of operations: `natcomms_requirements_20261107.md`, section 5.

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

## Status on 12 November 2026, evening (the author's round on Overleaf)

The author revised `main.tex` and `si.tex` on Overleaf (commit 4dfe508); the round is answered note by note in
`../review/revision_20261112_response.md`. What changes for the package:

- The table of the prospective test is Supplementary Table S10 (Section S6). The main text has 6 figures and no table.
- Counts by `wordcount.py` on the text of this round: abstract 167 words (guide 200), main text 5,334 (guide 5,000),
  Methods 3,066 (guide 3,000), legends 60 to 150, 97 references cited (guide 70).
- `natcomms_requirements_20261107.md` is the state of 7 November and still reads "6 figures + 1 table"; its other checks
  were not redone.
- The cover letter was not changed by this round.

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

## Status on 13 November 2026 (the evidence tables of the SI)

Tables S1, S2, S3 and S7 of the SI are rewritten in plain sentences (record: `../review/revision_20261113_tables_response.md`).
Their captions point to the detailed evidence in the data deposit, and the data statement of the main text names it.
For the package:

- `../evidence/si_tables_detailed.pdf` (the four tables in their detailed form, 10 pages) and its LaTeX source are
  listed in `build_zenodo_package.py`, folder `evidence`. Rebuild the document with
  `../evidence/build_si_tables_detailed.py` if `numbers.tex` or `refs.bib` change, then rebuild the package.
- The SI has eight sections and the PDF 60 pages.

## Status on 13 November 2026, afternoon (the submission form; the author submits)

The author opened the submission at Nature Communications and chose double-anonymised peer review, no Zenodo deposit before acceptance, and to upload the files and submit alone.

Manuscript (Overleaf 3cd6f17): the title page has no "Draft of" date and the red note of Code availability is gone
(`../review/patch_main_20261113_submission.py`). No `\todo` is left in `main.tex` or `si.tex`.

Files to upload, built in `local/rhine2026_submission/` of the repository (ignored by git):

```
python studies/rhine2026/submission/build_submission.py --out local/rhine2026_submission               # named PDFs, combined.pdf
python studies/rhine2026/submission/build_submission.py --out local/rhine2026_submission --anonymous   # the two anonymous PDFs
python studies/rhine2026/submission/build_cover_letter.py --out local/rhine2026_submission --orcid <id>
python studies/rhine2026/submission/build_review_code_archive.py --out local/rhine2026_submission
```

- `main_text_anonymous.pdf` (27 pages) and `supplementary_information_anonymous.pdf` (35 pages): the author's surname
  appears only in the reference list; no author in the metadata.
- `cover_letter.docx`: names the Collection, gives the author, affiliation, funding, author contributions, competing
  interests and the address of the code (the journal's checklist for double-anonymised review moves them there). Two
  brackets are the author's: the preprint sentence and the suggested reviewers (to be checked for conflicts of interest).
- `code_for_review_anonymous.zip` (438 files, 2.2 MB): the journal asks for the code when a manuscript goes out to
  review, and the public repository names its author. Left out: `review/`, `submission/`, `figures/`, `evidence/`, the
  records of cluster operations, binary files. Checked: no name, address, institution, account or local folder left.

Filled in the form (saved, not submitted): title and abstract; subject terms (Industry and Natural hazards, the author's,
plus Economics, Climate-change impacts and Complex networks); Collection "Managing cascading and non-linear climate
risks" (open until 17 April 2027; "Drought" is closed); not a clinical trial; code developed: yes, no Code Ocean
capsule, code submitted as a supplementary software file, with a note on the repository and the data; no figshare
upload. The author's own answers were left as found: no competing interests, no dual publication, double-anonymised
review, previous interactions "None of the above".

Left to the author (the Validate step lists the first five as errors): gender identity and the authorship declaration
(Authors tab); the consent to the Research Square dashboard; In Review yes or no; the transparent-peer-review
statement; the APC waiver box (optional; a request is only considered at submission); the upload of the files; the
push of this repository, which the Code availability statement points to.
