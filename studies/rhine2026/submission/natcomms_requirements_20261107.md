# Nature Communications requirements vs the manuscript (7 November 2026)

Read on 7 November 2026 from the journal's own pages, through the browser (the pages redirect automated fetchers
to a cookie gate, so quotes below are from the rendered pages): the Article page
(https://www.nature.com/ncomms/submit/article), How to submit (https://www.nature.com/ncomms/submit/how-to-submit),
the Policy Guide of initial screening (https://www.nature.com/ncomms/submit/policy), the transparent peer review FAQ
(https://www.nature.com/ncomms/submit/tpr-faq), and the Nature Portfolio policies on reporting standards and data,
code and materials (https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards) and on AI
(https://www.nature.com/nature-portfolio/editorial-policies/ai). Counts are from `submission/wordcount.py` on the
Overleaf copy of 7 November (after the x0.75 rung). Status: PASS, ACTION (something to do before submission),
DECISION (the author's call), LATER (asked at revision or acceptance, not at first submission).

## 1. Format and length ("flexible ... within reason, style and length will not directly influence consideration")

| Requirement (quoted) | Manuscript | Status |
|---|---|---|
| "the main text (not including Abstract, Methods, References and Figure legends) should be limited to 5,000 words" (ideally) | 5,473 words: Introduction 1,225, Results 2,750, Discussion 1,498 (trimmed on 7 November 2026 from 7,190 in three passes: restatements between the sections removed, detail moved to Supplementary Sections S2, S3, S5, S7, S8 and S10 with its ledger entries) | PASS at the 5,500-word level the author set (9 % over the 5,000 guide, which the journal says does not decide consideration); the November batch changes numbers, not length |
| "The maximum title length should be 15 words" | 15 words | PASS (no room for a longer title) |
| "The abstract ... should be no more than 200 words long and contain no references" | 186 words, no references | PASS (the orange daggers and the dagger footnote must go after the November batch) |
| Sections "Introduction ... Results, Discussion (if appropriate) and Methods"; "Results and Methods sections should be divided by topical subheadings; the Discussion should be succinct and may not contain subheadings" | Introduction, Results (five subsections), Discussion (no subheadings, 1,498 words), Methods (paragraph headings) | PASS |
| "Methods are typically less than 3000 words" | 3,115 words (trimmed on 7 November 2026 from 4,784: the weekly-sequence equations, the prospective-test protocol, the monthly loading shares, the forecast issue history and the sensitivity-run list moved to Supplementary Sections S3, S7 and S10; the Methods keep a summary of each) | PASS (typical, not a limit; 4 % over) |
| "Figure legends are limited to 350 words each" | 74 to 194 words | PASS |
| "references should not exceed 70" (as a guide) | 72 cited (87 entries in refs.bib, 15 uncited) | PASS as a guide (2 over 70 after the positioning review and the three 2018 sources added on 7 November: Kriedel 2019, Streng 2020, Scholten 2014); drop the uncited entries from the submitted .bbl |
| "Articles may have up to 10 display items (figures and/or tables)" | 6 figures + 1 table = 7 | PASS |
| "Footnotes are not used" | none in the text; the dagger note under the abstract is a draft device | ACTION: remove the dagger device with the November batch |
| Figures: "lower-case bold a, b", "Figure lettering ... sans-serif", colour-blind safe, vector for line art, 88 mm / 180 mm widths | panels labelled (a), (b) in captions; figure files are PDF (vector) from matplotlib; Fig. 1 and Fig. 5 are each two PDF files composed in LaTeX | LATER (acceptance): one file per figure (compose Fig. 1 and Fig. 5), bold lower-case panel letters, check the colour pairs (the validation figure uses green and gray, the map a sequential palette) |
| Equations numbered "(1)" when referred to | the Methods equations are inline and unnumbered, never referred to by number | PASS |
| Single-file first submission: "incorporate the manuscript text and figures into a single file (Microsoft Word, TeX/LaTeX or PDF) up to 30 MB"; "Supplementary Information should be combined and supplied as a separate file" | `build_submission.py` writes `main_text.pdf` (figures in place) and `supplementary_information.pdf` (the SI as its own document with its own reference list, cross-references resolved through xr-hyper) | PASS once built (sizes printed by the script) |
| Revision format: "All textual content ... in a single file"; LaTeX "include the references within the manuscript file itself ... copy the reference list from the .bbl file"; "remove all personal macros"; figures as individual files | numbers.tex macros, BibTeX, two-file figures | LATER (revision): a flattening step (inline numbers.tex and the .bbl, one PDF per figure) to add to `build_submission.py` when the editor asks |

## 2. Statements the initial screening checks ("must be met at initial submission")

| Requirement (quoted) | Manuscript | Status |
|---|---|---|
| "An Author Contributions Statement must be included in the manuscript and entered into the online system" | added 7 Nov: "C.C. conceived the study, developed the model and the European scope, designed and ran the simulations, analysed the results and wrote the paper." | PASS (single author; adjust if co-authors join) |
| "A Competing interests statement must be included ... If there is no conflict of interest ...: The author(s) declare no competing interests." | added 7 Nov, the journal's wording | PASS (author to confirm) |
| "A Funding statement must be included in the manuscript and entered into the online system that declares whether the work described received funding or not" | written 7 Nov: "This work was financially supported by the Jubiläumsfonds of the Austrian Central Bank (OeNB) as part of the FutureGVC project (2024--2028)" (Funding section of main.tex and the cover letter) | PASS (enter it in the online system too) |
| "A Data Availability statement must be included ... specifying conditions of access to the minimum dataset(s) necessary to interpret, verify and extend the research"; "Data availability statements ... Where data are publicly available, accession codes or other unique identifiers"; repositories "like Figshare, Zenodo and Dryad"; datasets deposited should be cited in the reference list with their DOI as a URL | present: sources named; "will be deposited on Zenodo upon acceptance; until then, available from the corresponding author" | ACTION (recommended): reserve a Zenodo DOI now (Zenodo reserves one before publishing), deposit the scope data package and the run tables with the submission, cite the deposit in the reference list. "Upon acceptance" is tolerated but weaker, and reviewers may ask for the files. The EU scope package is exported by `build_zenodo_package.py` (7 Nov: zip of 10.9 MB, README with the provenance commits and the licence of each source, sha256 manifest, metadata draft, build report, in `C:/dsc_runs/rhine2026/zenodo/`); the GISCO boundary files stay out (EuroGeographics copyright, non-commercial terms), the other third-party inputs are redistributable with attribution, the items to confirm are listed in the build report. Left to the author: upload, reserve the DOI, write it into the statement and the reference list. |
| "A Code Availability statement must be included ... how the code or algorithm can be accessed, including its use licenses and any restrictions"; "previously unreported custom computer code ... central to the main claims must be made available to editors and reviewers at submission"; best practice "deposited in a DOI-minting repository such as Zenodo or Code Ocean and cited in the reference list" | written 7 Nov: public GitHub repository (GPL-3.0), commits recorded in the forecast manifest, study scripts in studies/rhine2026; release tag and Zenodo DOI to add | ACTION: tag the release (`v2.1.0-rhine2026` or similar) at the commit of the final batch, archive it on Zenodo (GitHub integration), write the DOI into the statement and the reference list. The repository being public already satisfies "available to editors and reviewers at submission". |
| Ethics statement "if your work reports research involving human participants, their data, and/or biological materials, or animal subjects" | none involved (the DIHK survey is cited as a published aggregate) | PASS (not applicable) |
| "Authors ... who have related material under consideration or in press elsewhere should upload a clearly marked copy at the time of submission and declare this in the cover letter" | none known | ACTION: confirm in the cover letter (template says none) |
| Third-party materials: "any work that you have not created yourself and which you have reproduced or adapted from other sources" | all figures are the study's own; the Pichler et al. criticality survey is used as data, not reproduced | PASS (declare "no third-party material" in the online form) |
| AI: "Use of an LLM should be properly documented in the Methods section"; the risk framework marks "Extensive copy editing or writing support", "Comparing results to existing literature", "Suggesting ... methodological approaches" as amber, "Permitted with human oversight, verification, and transparency through disclosure"; AI cannot be an author; no AI-generated images | a "Use of AI tools" paragraph added to Methods on 7 Nov, marked for the author's confirmation | DECISION: the author confirms or rewrites the wording. The statement must be true to the process; the drafted text describes code, runs, literature, drafting, editing and number checks done with the assistant under the author's direction. |
| "ORCID ... corresponding authors ... before resubmitting the final version" | not in the manuscript | LATER (acceptance): link the ORCID in the manuscript tracking system |
| Acknowledgements "optionally"; "should not be used to declare competing interests"; permission from the people named | placeholder added | DECISION: fill or delete |
| Affiliation: "the institution where the majority of their work was done"; corresponding author "identified with an asterisk" | IIASA line and asterisk added 7 Nov; email placeholder | ACTION: email (and postal address in the cover letter) |

## 3. Reporting summary and source data

| Requirement (quoted) | Status |
|---|---|
| "Authors of research articles in the life sciences, behavioural & social sciences and ecology, evolution & environmental sciences are required to provide ... a reporting summary that will be made available to editors and reviewers during manuscript assessment" ("Where relevant, manuscripts sent for review must include completed reporting summary documents") | DECISION at submission: the paper is an economic model of a climate hazard; the editor decides whether it falls under behavioural & social sciences or environmental sciences. Prepare the form (Adobe Reader, https://www.nature.com/documents/nr-reporting-summary.pdf) with the answers drafted in `reporting_summary_notes.md`, so it can be uploaded if asked at submission or at the first revision. |
| Source data: "For relevant manuscripts, we may request a source data file in Microsoft Excel format or a zipped folder ... the numerical data underlying any graphs and charts ... each figure or table ... represented by a single sheet" | LATER (likely at revision, possible at submission): add a `--source-data` option to the figure scripts (validation_figure.py, scenario_figures.py, wave_isolation.py, lever_figures.py, the map) that writes one CSV per panel, then assemble `source_data.xlsx` with one sheet per figure (main and SI). Most panels plot the run tables already in `additional_data/`, so the data exist; the work is the export. |

## 4. Peer review and publishing conditions

| Point (quoted) | Implication |
|---|---|
| "All primary research papers published in Nature Communications that are submitted from November 1st, 2022 will have a corresponding peer review file containing the reviewer comments to the authors and the author rebuttal letters published alongside the article" | no opt-out: the response letters will be public; write them accordingly |
| Double-anonymized peer review is optional ("tick the appropriate box") | DECISION: the paper's single author, the public repository and the forecast's dated Overleaf history make anonymity impractical; recommend single-anonymized (default) |
| "Abstracts or unrefereed web preprints do not compromise novelty"; preprints may be cited | DECISION: posting a preprint (arXiv econ.GN or physics.soc-ph, or SSRN) at submission is allowed and would date-stamp the forecast publicly before the autumn statistics appear; note it in the cover letter if done |
| "we do not consider pre-submission enquiries" | submit the full manuscript |
| APC: "authors ... are required to publish their work open access, through payment of an article processing charge (APC), in the case of eventual acceptance" | check the institution's agreement with Springer Nature (IIASA) or the fee-support service |
| Cover letter: "affiliation and contact information for the corresponding author", "briefly discuss the work's importance and explain why the work is considered appropriate for the diverse readership", "names and contact information for qualified scientific reviewers", may "request the exclusion of certain referees", "indicate whether they have had any prior discussions with a Nature Communications editor" | `cover_letter.md` follows this list; reviewers in `suggested_reviewers.md` |

## 5. Before the files are uploaded (the order that avoids rework)

1. November batch on the observed season: `make_numbers.py`, `si_tables.py`, figures; remove the `\finalbatch` daggers,
   the dagger footnote and the `\todo` marks; `paper_gate.py --regen` green.
2. Length: done on 7 November (main text 5,473 words, Methods 3,115; `wordcount.py`); the positioning paragraphs of the Introduction in their final form.
3. Statements completed (funding done 7 November; acknowledgements, email, AI-use wording to confirm); release tagged,
   Zenodo DOIs (code, data) reserved (the data package is built: `build_zenodo_package.py`, `C:/dsc_runs/rhine2026/zenodo/`)
   and written into the statements and the reference list; uncited bib entries dropped.
4. `python studies/rhine2026/submission/build_submission.py` : `main_text.pdf`, `supplementary_information.pdf`,
   word counts; read both PDFs once more (Supplementary references resolved, no "??").
5. Cover letter dated and signed; reviewers' contact details filled in; related-manuscripts declaration.
6. Online system (https://mts-ncomms.nature.com): upload the two PDFs and the cover letter; enter the statements,
   the reviewer suggestions and exclusions; answer the third-party-material and dual-publication questions; choose
   single- or double-anonymized review; reporting summary if asked.
