# Submission package: Rhine 2026 paper, Nature Communications

Started 7 November 2026 (phase 6 of the paper pipeline: venue checks, scoop search, cover letter, statements,
reviewers). The manuscript lives in Overleaf (git bridge working copy
`C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f`); this folder holds what
the submission needs besides the manuscript, and the scripts that build the files to upload.

## Contents

| File | What it is |
|---|---|
| `natcomms_requirements_20261107.md` | every requirement of the journal's pages (quoted, with the URL) against the manuscript: status PASS / ACTION / DECISION / LATER, and the order of the final steps |
| `cover_letter.md` | the cover letter draft, following the journal's list of contents; brackets for what only the author can fill |
| `suggested_reviewers.md` | reviewer candidates by expertise and exclusions to consider, for the author to vet |
| `reporting_summary_notes.md` | drafted answers for the Nature Portfolio reporting summary, if the editor asks for it |
| `build_submission.py` | builds `main_text.pdf` (manuscript without the SI), `supplementary_information.pdf` (the SI as its own document, own reference list) and `combined.pdf` in a temporary copy of the Overleaf folder; prints the word counts and the page counts; fails on an engine error or an unresolved reference |
| `wordcount.py` | the counts against the journal's guide (title 15, abstract 200, main text 5,000, Methods 3,000, legends 350, references 70, display items 10), macros expanded |

The split build rests on three additions to the Overleaf copy (7 November 2026): `xr-hyper` in the preamble of
`main.tex` with two `\externaldocument` lines placed after `\input{numbers}`, a `\standalonesi` / `\nosupplement`
switch around the document body (lower-case names: the gate reads every upper-case `\Name` as a numbers.tex macro),
and the one-line wrappers `maintext.tex` and `supplement.tex` (no underscores: the lint). Overleaf keeps compiling
`main.tex` as before (main text followed by the SI), and `paper_gate.py` is unchanged.

```
python studies/rhine2026/submission/build_submission.py              # -> C:/dsc_runs/rhine2026/submission/
python studies/rhine2026/submission/wordcount.py                     # counts only
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
(scoop search and the 2026 analyses) and, when it lands, `positioning_transport_rhine_20261107.md` (transport models
and the Rhine), with the synthesis `positioning_synthesis_20261107.md`. The manuscript took the edits the same evening
(Overleaf): the Introduction's state-of-the-art paragraph and novelty claim, the ex-ante estimates of 2026 (Kiel,
Commerzbank, Prognos), the 2018 GDP figure (0.2 to 0.3 % after Jannsen and Meuchelboeck 2026) and five Discussion
sentences; the bibliography grew from 61 to 85 entries (69 cited, DOIs verified on Crossref or DataCite). The main
text is now 7,181 words (Introduction 1,323), which adds to the length decision above.

Open before upload (the author): funding and acknowledgements, the e-mail, the AI-use wording, the length decision,
the release tag and the Zenodo DOIs for code and data, the November batch on the observed season (daggers and todos
removed), the reviewer list with contact details, the preprint decision, the APC arrangement. Details and the order
of operations: `natcomms_requirements_20261107.md`, section 5.
