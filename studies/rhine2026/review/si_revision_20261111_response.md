# Round of 11 November 2026: the author's version of that morning and the answers to the open points

Base: Overleaf `41f0e3c` (the author's version of 11 November, 09:18; `si.tex` only: 12 inline notes, 25 direct edits).
Result: Overleaf `dabc92f`, one push, as asked ("No need to do section-by-section push, your response MD is enough").
This file is the record of the round. The notes and edits as extracted are in `si_revision_20261111_notes.md`.

Two things wait for the author's decision and are **not** applied yet: the plan for the 2026 test (open point 1) and the
new structure of the SI. Both proposals are below. Everything else the author asked for is applied.

Contents: 1. Method. 2. The answers to the open points. 3. The twelve inline notes. 4. Direct edits. 5. Proposal: the
2026 test. 6. Proposal: the structure of the SI. 7. For the author. 8. State of the checks. 9. Scripts.

## 1. Method (unchanged)

- The author's version is the baseline. Direct edits are kept; they are only checked for breakage.
- Each inline note is answered in the text and removed. A note that needs a decision stays in the file.
- No number is typed by hand: numbers are macros of `numbers.tex` or cells of tables checked against the run outputs.
- The gate (`paper_gate.py`) runs before the push: lint, numbers, ledger, references, regeneration, compile.
- Nothing is posted in the review panel of Overleaf.

## 2. The author's answers to the open points of 10 November

| Point | The author's answer | What was done |
|---|---|---|
| 1 | Settle the 2026 test; one profile; remove the superscript; say in the cover letter what happens when new values come; propose a plan | The superscript is removed: the macro, its 94 uses and the note under the abstract. The plan is section 5. Nothing else is changed until it is agreed. |
| 2 | One choice made on 2018; align the Methods | Done in five places of `main.tex`. Methods, "Calibration, selection and validation": one choice, the representation of the river; the level of the inventories and the number of suppliers are sensitivities kept at their reference values. Methods, "Economic layer": the number of suppliers is "one in the reference runs; a run with two is reported as a sensitivity". Introduction and Discussion: "one choice" instead of "three choices". Results: "the model's rules and parameters move it further" instead of "the model's rules, selected on the 2018 episode". Not changed: the abstract's "Calibrated on the 2018 low water" (section 7, point 2). |
| 3 | OK for a small run on the sea rate | The run joins the rerun of 2026 (section 5, step 3). Not launched. |
| 4 | Drop the column | Done. The weekly table of flows turned away at Kaub has no column "total" any more; caption and sentence adjusted; the generator follows. The tonnage that passes Kaub each week is indeed not in the outputs: the log gives what is turned away, not what passes. If the column is wanted later, the rerun can log it. |
| 5 | Remove it and adjust the Discussion | The author had already removed the sentence of S3. The clause of the Discussion on the outlook of 7 September is removed. The rest of that sentence, on the two stress paths, waits for the plan (the paths are dropped in the proposal). |
| 6 | Drop, and drop the pointer | Done. The paragraph on French buyers is removed from S6; its last sentence, on the tables of disrupted chains, joins the paragraph before. The pointer of the main text to S6 is removed; the description of the French chain in the main text stays. |
| 7 | Fine like that | Nothing to do. |
| 8 | Will do later | Still to confirm by eye: the title of the Destatis table 46321-0014 and the OPIS figures for June 2025. |
| 9 | OK | Nothing to do. |
| 10 | Simplify the disclosure | One statement, in the Methods: "A large language model (Claude, Anthropic) was used to collect data, to write code, including the scripts that draw the figures, and to draft the manuscript. The author directed and checked this work and is responsible for the content." No model version. The separate section "AI disclosure" is removed (section 7, point 4, says why). The overfull line is gone with it. |

## 3. The twelve inline notes of 11 November

| Note | Where | The note | Answer |
|---|---|---|---|
| N01 | S1, transport costs, road--rail transfer | add evidence | Added. German appraisal rates for a transfer between road, rail and inland vessel: 20.80 EUR per container, 2.60 EUR per tonne of dry bulk, 2.90 of liquid bulk (2012 prices; Planco et al. 2015, Table 8-25). Two German terminal operators charge 30.50 EUR per loading unit in 2026 (DUSS, DB Intermodal Services). The cell says how the model sits: container and dry-bulk values close to the appraisal rates, liquid-bulk value a third of its rate. No published dwell time was found; the cell says the hours are assumptions. |
| N02 | S1, waterway--sea transfer | add evidence | Added, for containers only. A container lift costs 35 to 40 EUR per TEU in the port of Rotterdam (Konings 2009, already cited in the row above); the model's value is about half. A barge spends about 8 hours sailing between the terminals of that port and about one hour waiting at each (same source). No published figure was found for bulk; the cell says so. |
| N03 | S1, table note | "USD and EUR are treated as equal": add a conversion factor, e.g. 2022 average | The sentence is replaced: "The model is in US dollars of 2022. Values in euros are quoted as their sources give them, at the price level of the year named; one euro was worth 1.05 US dollars on average in 2022." The rate is the ECB annual average, 1.0530. The euro values of the table are not converted one by one: they come from years between 2012 and 2026 and stay traceable to their sources this way. See section 7, point 3, for the one conversion of the main text. |
| N04 | S1, table note | superscript note for "ARA" | Done: ARA$^{b}$ at its first use in the table; note b. |
| N05 | S1, table note | same for "Kempenaar" | Done: CEMT class Va$^{a}$ and Kempenaar$^{a}$ at their first use; note a gives what the classes carry (1,500 to 3,000 tonnes; 400 to 650). TEU$^{c}$ likewise. |
| N06 | S1, inventory table, caption | name the main source: Bundesbank, complemented by Banque de France and US Census Bureau | Done, with the three citations. The doubled "in" is corrected. |
| N07 | S1, inventory table, header | superscript to explain the grade levels | Done: grade$^{a}$ in both headers; note a defines A to D. |
| N08 | S1, inventory table, row A01 | what is WIP? how do 49 days become 30? superscript notes at first use of acronyms and of concepts such as "ratio series" | Done. Row A01 now reads: the ratio series gives 49 days of non-finished stock, which counts growing crops and livestock as work in progress, so it is an upper bound; 30 days is assumed below it (grade C). Notes b to i, each with a superscript at first use: ratio series and work in progress, BLE, FIBEN, RHB, Census, BAFA, EBV and CSE, EKBG. |
| N09 | S2 | define CCNR in the main text and in the SI | Done in the SI at the two first uses (the note of the transport-cost table, the calibration paragraph): Central Commission for the Navigation of the Rhine. The main text does not use the acronym; nothing to define there. |
| N10 | S7, opening | "not really about sensitivity, it is how the lever study was made" | Agreed. The sentence moves to the section on the levers in the proposed structure (section 6). The note stays in the file until the structure is applied. |
| N11 | S7, opening | "are those runs really needed to show?" | Proposal in section 6: keep both small tables, each under the result it backs. The note stays in the file until then. |
| N12 | S8 | remove the table of rail weeks | Done. Its counts stay in one sentence of S8, as macros: the 50 kt ceiling is reached in 23 of the 23 profile weeks of 2026 and 21 of the 22 of 2018, the 140 kt ceiling in 20 and 17. The main text said "nearly every week" for both ceilings and pointed to the table; it now says "The lower ceiling is reached in nearly every week of both events, the higher one in most." |

New references, each opened on 11 November (dossier `evidence/si_evidence_transfers_fx_20261111.md`): `planco2015bvwp`,
`duss2026price`, `dbis2026price`, `ecb2026exrusd`.

## 4. Direct edits

The 25 edits are kept as written, except four.

| Where | The edit | Correction and reason |
|---|---|---|
| S1, caption of the inventory table | "are given in in Table" | One "in". |
| S2 | `\paragraph{Calibration procedure}` | Period added, as the other paragraph titles. |
| S3, Capacities | "... the CCNR cross-section counts, with a 2\% headroom." | "... counts; the factor 1.02 leaves a headroom of 2 % over the model's own flow." The headroom applies to the model's flow, not to the counts. |
| S3, loading curve | The row at 10 cm (0.18) was deleted | **Restored.** The row is an anchor of the curve that the model uses, not a redundant line: between 0.08 at 5 cm and 0.24 at 15 cm a straight line gives 0.16 at 10 cm, the model uses 0.18. Without the row the sentence "The model interpolates linearly between those values" would be wrong for weeks between 5 and 15 cm, and 2026 has several. Its text now says what it is: "an anchor of the curve, on the line between the value at 5 cm and the count at about 12 cm". To drop it for good, the curve itself would have to change, which is a change of the model (section 5 keeps the model fixed). |

## 5. Proposal: the 2026 test (open point 1)

### What I found

The profile of the paper no longer matches the river. The record was fetched on 11 November at 10:24 from PEGELONLINE.
Kaub stood at 16 cm that morning. The profile of the paper recovers to 75, 90 and 105 cm in the three weeks to
29 November.

| Week starting | Profile of the paper (cm) | Observed (cm) | Loading share, profile | Loading share, observed |
|---|---|---|---|---|
| 28 Sep | -1.7, two observed days and the outlook | not yet downloaded | 0.08 | |
| 5 Oct | 6, outlook | not yet downloaded | 0.10 | |
| 12 Oct | 24, outlook | 13.5 | 0.28 | 0.22 |
| 19 Oct | 36, outlook | 21.0 | 0.32 | 0.26 |
| 26 Oct | 43, outlook | 45.3 | 0.34 | 0.35 |
| 2 Nov | 58, outlook | 18.0 | 0.43 | 0.25 |
| 9 Nov | 75, assumed | 12.3 and 13.5 on 9 and 10 November | 0.57 | 0.21 so far |
| 16 Nov | 90, assumed | outlook of 9 November: 81 (61 to 104) | 0.71 | |
| 23 Nov | 105, assumed | outlook of 9 November: 134 (100 to 173) | 0.83 | |

- The outlook of 9 November puts the current week at 41 cm (36 to 47). The first two days were at 12 and 13 cm.
- In three of the four weeks that can be checked, the outlook of 28 September was 11 to 40 cm above the river.
- The days from 30 September to 10 October are not served any more by the public service, which keeps 31 days. They come
  from the long-term download of the station page, which is a form.
- The nearest existing run is the stress path on the outlook's 25th percentile: 1.30 % of a quarter against 1.11 %. The
  observed November is below that path. No run exists on the observed river.
- Saved in the study folder so that nothing is lost when the 31 days roll on: `scenarios/staging_20261111/` (the raw
  15-minute values from 11 October to 11 November and their daily means) and `scenarios/bfg_6week_kaub_20261109.csv`.

### Recommendation

One profile, the river as observed, and a full rerun of the runs that read the 2026 profile.

1. **Profile.** Observed weekly means from 22 June to Sunday 15 November, built on Monday 16 November. The last two weeks
   of the 23, 16 to 29 November, come from the six-week outlook then current. The present `scenarios/2026.csv` is kept
   under another name.
2. **Model.** Unchanged since the batch of 2 November: same code, same parameters, same loading curve, same networks. Only
   the gauge file changes. Two facts to handle:
   - The repository has moved since 2 November. Fixes of 3 and 6 November from other studies touch the model code
     (KI-47 cache signatures, KI-50 route cache after closures, KI-53 deliveries below one gram, KI-54 memory).
   - The cluster checkout is at `9ff8c8f` of 6 November, which contains them. The run at 0.75 times the inventories
     (6 November) therefore ran on that code; the 128 other runs ran on the code of 2 and 3 November.
   - So: one control run of the 2026 reference on the old profile with the cluster's current code. If it returns 1.110
     to the last digit, the fixes do not touch the Rhine runs and the rerun uses the current code. If not, the rerun is
     pinned to the code of 2 November and the 0.75 run is repeated on it.
3. **Runs.** The 103 runs that read the 2026 profile: 92 of the season and 11 of the wave experiment. Less the two stress
   paths on the outlook's quartiles, which lose their object. Plus the sea-rate run of open point 3. The 26 runs of 2018
   stand. On 2 November, 110 runs took about twelve hours on the cluster. Disk: about 40 to 60 GB; 160 GB are free
   (839.5 of 1,000 GB used on 11 November).
4. **Calendar.** Launch on Monday 16 November in the morning. Numbers, tables and figures on Tuesday. The author's
   reading on Wednesday. Submission on Wednesday 18 or Thursday 19 November.
5. **Pilot, as soon as agreed.** Two runs, three hours: the control run of step 2, and the reference network on the river
   observed to 10 November. They give the size of the change and test the chain before Monday.

Alternative, not recommended: wait for the fully observed season and submit about 3 December. It removes the two
outlook weeks. It leaves five days before the October index, and the recovery has slipped several times this season.

### What the paper then claims

An estimate of the season as observed, made before the production statistics of the fourth quarter. It is no longer a
forecast of the river.

| Item | Date | Status |
|---|---|---|
| Model, parameters, loading curve fixed | 2 November 2026 | no change after |
| Production index, July | released 7 September | published before; not used |
| Production index, August | released 7 October | published before; not used |
| Production index, September | released 6 November | published after the model was fixed, before submission; not used; not opened by me |
| River record in the runs | to 15 November | observed |
| Submission and public deposit | 18 or 19 November | fixes the monthly path publicly |
| Production index, October | expected early December | released after submission |
| Production index, November | expected early January 2027 | released after submission |
| Production index, December | expected early February 2027 | released after submission |

- **Protocol.** Unchanged: September to December, as fixed on 9 October. Added: the score over October to December alone,
  the months released after submission.
- **Built-in check.** The weeks to 27 September are observed in the old and the new profile. The model's values for July
  and August cannot change, and September's can move only through its last three days. If they move, something else
  has changed.
- **Public date.** A deposit on Zenodo, on the day of submission, of the monthly path, the profile and the run tables.
  The package script exists (`submission/build_zenodo_package.py`). The upload is the author's.
- **History.** The earlier versions (1.74, 1.54 and 1.11 % on the river information of 30 September) leave the
  manuscript. They stay in `forecast_manifest.md` of the repository, which gets a section for the new batch.

### Cover letter (draft paragraph)

> The study contains a test that is still open. The model and its parameters were fixed on 2 November 2026, and the
> simulations use the river as observed to 15 November. The German production indices of October, November and December
> are due after submission; the monthly path that the model implies for them and the scoring rule are in the manuscript
> and deposited at [DOI]. During review we will score each index on its first release and report the result, whatever it
> is. We will replace the last two weeks of the river profile, taken from the official outlook, with the observed record
> and rerun the reference simulation. If the German loss moves by more than 5 %, we will rerun all simulations of 2026
> and update every number; otherwise we will report the comparison in the Supplementary Information. We will not change
> the model in response to the statistics.

The 5 % is a proposal. For scale: the spread across the eleven networks is 37 % of the mean, and the two stress paths
moved the loss by +17 and -14 %.

### Implications for the main text

- Abstract: "For 2026 it forecast, before the autumn's statistics" becomes an estimate made ahead of the fourth-quarter
  statistics. The numbers change.
- Introduction: "the model then forecast the cost of the 2026 event before the autumn statistics were published" and
  "issued as a forecast and kept for evaluation" are reworded the same way.
- Results, "The 2026 event": the first paragraph is rewritten on the observed autumn (the gauge zero of late September,
  the rise to 57 cm on 27 and 28 October, the fall back to 18 cm). The sentence "Everything below for 2026 is a forecast
  on the river information of 30 September, issued on 7 October" goes. The figure of the event loses its shading of
  forecast weeks, except for the last two.
- Every 2026 number, six figures and the tables regenerate. The sentences bound to numbers in the ledger are re-read:
  "more than doubles in the autumn", "two fifths", "a sixth more in sequence" and the like may change.
- The table of the prospective test: the row "production-weighted B-E (the earlier version's measure)" goes; the caption
  loses its three dates; the row of low-water days is observed to 15 November.
- Methods, "Scenarios": the profile in two sentences, no issue history. "Prospective test": one series, the dates of the
  table above, the deposit.
- Discussion: the sentence on the tests to come is reworded with the release dates. The sentence "The 2026 season is a
  forecast, whose 25th- and 75th-percentile stress paths give ..." goes; the limitations become four.
- Code availability: one tagged version instead of "the versions recorded, commit by commit, in the forecast manifest".

### Implications for the SI

- A section of its own, "The 2026 test" (section 6 below).
- S3, Gauges: observed to 15 November; the sentence on the two additional profiles goes.
- The sensitivity table loses the two rows "gauge of the forecast weeks".
- The weekly table of Kaub and every 2026 number regenerate.

## 6. Proposal: the structure of the SI

| New | Title | Holds | From |
|---|---|---|---|
| S1 | Scope and data | unchanged | S1 |
| S2 | Baseline calibration | unchanged | S2 |
| S3 | Scenario construction | gauges, loading curve, monthly loading shares, capacities, rerouting around a saturated reach, surcharge | S3 without its two last paragraphs |
| S4 | Weekly sequence and model specifications | unchanged | S4 |
| S5 | Modeling choices for the low water | (a) capacity limit or floors: the 2018 benchmark and the one choice made on it, with the table of the two representations; (b) bulk does not change mode: the modal-switch rule and the table of its thresholds | S9; first paragraph of S5 |
| S6 | The 2026 test | what was fixed and when; the protocol; the monthly path by sector, with its table; the estimates made during the event in August and the business survey; the calendar of releases and what is done at each | the two last paragraphs of S3; the last paragraph and table of S5 |
| S7 | The 2026 season in detail | (a) at Kaub, week by week, with the table; (b) capacity against surcharge: what is blocked, what is rerouted, at what price, with the table of the two mechanisms; (c) which inputs go missing, the fuel chain; (d) the even-spread profile; (e) the two episodes at a shorter refill time, with its table | S5 except its first and last paragraphs; S6 |
| S8 | Adaptation levers: how each is built | inventories, fairway, low-water fleet, rail as a bounded substitute; how a lever is measured, on each of the eleven networks against that network's base; the levers under a rail ceiling, with its table | S8; one paragraph of S5; two sentences of S7 |
| S9 | Sensitivity analysis | one table, one figure, a ranked list, what was not varied | S7 |

- **Roles.** S1 to S4 say what the model is. S5 says why its two low-water rules are what they are. S6 is the
  out-of-sample test. S7 and S8 hold the results and definitions that back a sentence of the main text, in the order of
  the Results. S9 is robustness. Each section opens with one sentence that states its role.
- **Order.** S5 to S9 follow the Results: the 2018 event, the 2026 test, the mechanism and who loses, the levers.
- **S5 or S4 for the river choice.** The author suggested S4. The weekly sequence is kept as S4 because S1 to S4 were
  found logical as they are; swapping S4 and S5 is a small change.
- **The former S6**, "What crosses Kaub, and at what price", was floating. It becomes parts (b) and (c) of S7: the support
  of the two Results subsections on the mechanism and on who loses.
- **S9 (the former S7).** The opening keeps two sentences. The paragraph that read the table becomes a list ranked by
  size of effect, in plain words, about eight items; the two paragraphs on the inventories and on the suppliers on 2018
  are merged into it. "What was not varied" stays.
- **Tables.** The table of the inventory levels on 2018 goes: its losses are already rows of the sensitivity table, and
  its one extra column, the industrial shortfall against the benchmark, goes into a list item. The table of rail weeks
  is already gone (N12). Fifteen tables remain.
- **Note N10.** The sentence on the levers run on every network moves to S8, "how a lever is measured".
- **Note N11, "are those runs really needed to show?"** Proposal: keep both. The levers under a rail ceiling answer the
  question a referee will ask, whether the levers still work when rail helps; one small table in S8. The two episodes
  at a 15-day refill back one sentence of the main text; one small table in S7. To cut one, cut its sentence in the
  main text with it.
- **What is lost.** No text beyond what the author already cut: the French chain (point 6) and the two tables.
- **Main text.** About fifteen pointers to SI sections are updated, one by one, as on 10 November.

## 7. For the author

Decisions that block the next step:

1. The profile on 16 November and the submission on 18 or 19 November, or the alternative.
2. The pilot of two runs now. It needs the portal session, which was open at 11:25 on 11 November.
3. The days from 30 September to 10 October: the long-term download is a form on the station page of PEGELONLINE. Either
   the author downloads the file, or agrees that I submit the form in the browser pane.
4. The issue history out of the manuscript.
5. The 5 % rule of the cover letter.
6. The structure, and S4 or S5 for the river choice.

Points to know, none blocking:

1. **The 10 cm row of the loading curve is restored** (section 4).
2. **Abstract, "Calibrated on the 2018 low water".** With one choice made on 2018 and nothing fitted to the events, the
   word says more than the Methods. Not changed, since the abstract is rewritten with the 2026 test. Suggestion: "Tested
   on the 2018 low water".
3. **One conversion in the main text.** "About EUR 1.1 billion" for the industrial loss of August converts the model's
   1.23 billion USD at 0.92 EUR per USD. At the 2022 average, 0.95, it prints 1.2. Proposal: switch with the rerun, so
   that the note of the SI table and the main text use the same rate. Not changed now.
4. **AI statement.** The journal asks for it in the Methods, so the single statement is there and the separate section
   is removed. "The scripts that draw the figures" is there because the journal does not accept AI-generated images and
   "produce figures" could be read that way. To restore the section, say so.
5. **Sources to confirm by eye**, added to the two of point 8: the ECB rate was read on a mirror (DBnomics; the ECB
   portal and the Eurostat service could not be reached that day; the Federal Reserve's own table gives 1.0534); the
   report of Planco et al. is read from a copy on a TU Berlin server; the two price lists are web documents whose
   addresses may move.
6. **Evidence found and not used.** For the transfer between road or rail and sea, the only tariff found is that of one
   break-bulk terminal in Hamburg, 2 to 10 times the model's 7 USD per tonne; it is not a bulk terminal, so the cell is
   left as it is. A study for the European Commission on transhipment technologies (2022, DOI 10.2832/205486) could
   not be opened and is the best lead for costs per lift. No published dwell time was found for any transfer.
7. **No bibliography entry** for two sources named in the notes of the inventory table: the Bundesbank ratio statistics
   (edition of May 2026) and the BLE report on the feed market, which was read as an abstract only.
8. **`main.tex` keeps five notes**: the e-mail, the placeholder under the abstract, the two notes on the forecast in the
   Methods (they go with the plan), the Zenodo DOI. `si.tex` keeps two: N10 and N11.

## 8. State of the checks

- `paper_gate.py --regen` on the version committed (Overleaf `dabc92f`): **PASS**. Report: `review/paper_gate_20261111.md`.
  - Regeneration: the 520 macros of `numbers.tex` and the 16 generated tables, recomputed from the run folders, equal the
    manuscript. `numbers.tex` gains four macros (`RailBind*`); no value changes.
  - Compile: no error and no overfull line. The overfull line of 10 November went with the AI section. The superscript
    in the header of the inventory table made that table 2 pt too wide; its last column is 1 mm narrower.
  - Ledger: 18 entries dropped (`ledger_dropped_20261111.txt`), 8 added.
  - Warnings, none new in kind: 206 of 520 macros are not used (ten more than on 10 November, all from text removed
    this round: seven run counts, the first issue's loss and the two French amounts); 26 number words to read by eye;
    14 bibliography entries are not cited; 28 cited entries have neither DOI nor URL (none added: the four new entries
    carry a URL).
- `si_tables.py --check`: the 16 tables agree with the run outputs.
- The edited pages were read in the compiled PDF: the notes of the two tables with their superscripts, and the weekly
  table of Kaub with its two columns.
- Notes left: `si.tex` 2 (N10, N11); `main.tex` 5 (section 7).
- Not run: the split builds of the submission package (`submission/build_submission.py`); they are rebuilt with the
  final version.
- Push: pushed to Overleaf on 11 November at 11:45, after two retries (the git service of Overleaf answered 503 for a few minutes); origin and local copy are at `dabc92f`, the working copy is clean.

## 9. Scripts of the round (all in `review/`)

- `patch_main_20261111.py`: the main text.
- `patch_si_20261111_a.py`, `patch_si_20261111_b.py`: the SI.
- `patch_tools_20261111.py`: `si_tables.py` (no column "total"; the table of rail weeks is no longer generated) and
  `make_numbers.py` (four macros `RailBind*`).
- `ledger_20261111.py`: the ledger of the gate; the 18 entries dropped are listed in `ledger_dropped_20261111.txt`.
- `si_notes_extract.py` (of 10 November) produced `si_revision_20261111_notes.md`.
