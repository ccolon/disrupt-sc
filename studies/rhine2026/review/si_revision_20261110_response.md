# The author's revision of the SI (Overleaf 675722a, 10 November 2026): what was done, note by note

The author revised the Supplementary Information in Overleaf on 10 November 2026: `sections/si.tex` moved to `si.tex` at
the project root, about 50 direct text edits (S1 to S10) and 61 inline notes (`\todo{...}`), numbered N01 to N61 here in
file order (S1: N01-N14, S2: N15-N24, S3: N25-N33, S4: N34-N45, S5: N46, S6: N47, S7: N48, S8: N49-N50, S9: N51-N59,
S10: N60-N61). The extraction (each note with its context, and the word-level edits) is
`review/si_revision_20261110_notes.md`, written from the author's version (Overleaf 675722a) by `review/si_notes_extract.py`.

The blocks below carry the section numbers of the author's version, one block per version pushed to Overleaf. The
numbers after the revision are in the table of the last block; the open points for the author and the state of the
checks close the file.

## How the revision is handled

1. Pull the Overleaf git bridge (fetch, fast-forward). The author's version is the baseline: their wording stays.
2. Compare it with the last version pushed (fc30932): the direct edits on one side, the notes on the other.
3. Direct edits are kept. Each is read for what it may have broken: LaTeX (a `#`, a `\~`), facts (a number, a reversed
   statement), macros, cross-references, typos. Corrections of that kind are listed below under "direct edits corrected".
4. Each note is answered in the text and then removed. A note that needs a decision only the author can take stays in
   place, reworded as an open question.
5. Numbers never go in by hand: they are macros of `numbers.tex` (written by `make_numbers.py` from the runs) or cells
   that `si_tables.py` checks against the runs. A reworded sentence that carries a claim has its entry in the ledger
   (`paper_gate_ledger/`) updated, and `paper_gate.py` is run before each push (lint, numbers, ledger, compile).
6. New references are verified before they enter `refs.bib` (`cite_check.py`); none is written from memory.
7. One commit and one push per SI section, so the Overleaf history shows one version per section. The commit message
   lists the notes it answers.
8. Nothing is posted or resolved in Overleaf's review panel.

New on 10 November, from the author's comment in the rates table ("consider using the .tex as the source of truth"):
the text of every table (caption, headers, row labels, notes, evidence cells) now belongs to `si.tex`; `si_tables.py`
no longer rewrites a table, it compares the numeric cells with the runs and refreshes only those.

## Step 0 (Overleaf 5b4cbb3)

`main.tex` line 51 still read `\input{sections/si}` in the stand-alone SI build: now `\input{si}`. The tooling
(`si_tables.py`, `paper_gate.py`, `lint_manuscript.py`, `submission/wordcount.py`, the ledger files) reads `si.tex`.
The gate on the revision as received: static 1 FAIL (`Choice #1`, an unescaped `#`), ledger 93 entries whose sentence
was reworded or removed, 64 numbers and 24 number words without a ledger entry; these are cleared section by section.

## Step 1 (Overleaf dffd083): the tables' text belongs to si.tex

The author's comment in the rates table asked what the generator adds and whether the .tex could be the source of
truth. Answer: the generator guarantees that every table number equals the run outputs and the configuration, and
refreshes them in one command after a batch; its cost was that captions and labels could not be edited in Overleaf.
From now on `si_tables.py` leaves a table that exists in `si.tex` alone and only compares its numeric cells with the
runs (`--check`), refreshing a cell that differs; captions, headers, row labels, notes and evidence cells are edited in
`si.tex`. A change of structure (a column removed, a table split) still needs the generator brought in line, which is
done here for each such note. The gate now reads the captions as prose.

## S1 Scope and data (Overleaf 85d4323)

| Note | Answer |
|---|---|
| N01, N02 | Sources cited in the Agents paragraph: SPAM 2020, the GEM trackers, Climate TRACE, FINEPRINT, the Eurostat regional accounts (keys already in refs.bib). The Bundesbank statistics are cited in the Inventories paragraph. |
| N03 | A household agent sits at an interior point of its NUTS2 region, near the geometric center (`representative_point` of the polygon in `eurostat_nuts_households.py`); it is not a population-weighted centroid and not the largest city. The sentence now says so. |
| N04 | TENtec cited (new key tentec2026: the Commission's TENtec information system and its public map services). |
| N05 | Rates table: the caption names the main sources in two lines; the general remarks (EUR = USD, what operator costs are, ARA, TEU, vessel classes) are notes under the table. |
| N06 | "The Panteia comparison" is now "the operator cost of a tractor-semitrailer at fleet average, empty legs included, 0.115 EUR per tonne-kilometer in 2018", cited (kim2023). |
| N07 | Yes, the liquid-bulk road and rail values are set on the German split alone; the cell says so. New and worth knowing: the Dutch operator cost of a liquid-bulk charter train is 0.018 EUR per tonne-kilometer (KiM 2023, Table 6.2), 4.7 times below the model's 0.085, so the cell calls the value an effective cost, not a tariff. |
| N08, N10 | Every number of the evidence column carries its source (kim2023, infras2017, konings2009, opis2025riverlake, handelsblatt2022rhine, ccnr2024price, ecorys2005). |
| N09 | Sea rate: KiM 2023, Table 5.5 gives 0.0014 EUR per tonne-kilometer for container carriers, 0.0034 for bulk carriers and 0.0051 for tankers. The model's 0.0015 matches containers and is two to three times too low for bulk; the cell says both. "Do not influence the results" was not kept: no run tests it. The cell says that sea lanes carry no capacity limit and that the rate bears on the port of landing. |
| N11 | Value of time: no commodity-specific value exists in what was found. The meta-analysis of Binsuwadan et al. (2022) gives, for shippers in Germany, 1.59 (road), 0.27 (rail), 0.19 (sea) and 0.09 (inland waterway) USD per tonne-hour. The model's road and sea values for containers and its 0.08 for bulk are in line; its 1.00 on rail and 0.32 on waterways are three to four times higher. The cells say so. |
| N12 | Inventory table: the "lean" column is removed (the 2019 values are in the evidence cells); grades and acronyms are notes under the table. |
| N13 | The input-specific targets are a table of their own (Table S3, label tab:stockoverrides) with the columns buyer, input, days, grade, evidence and modeling reason. |
| N14 | Criticality table: the note column is replaced by lettered notes under the table. |

Not asked but changed with these notes: the rail cell said "within the range of block-train and intermodal rates in
Europe (0.02-0.04)"; no source states that range (KiM 2023: 0.014 for a dry-bulk charter train, 0.045 for a container
shuttle; IRG-Rail: average revenue 0.036 in 2019, 0.047 in 2024), so the cell now gives these figures. In the two
inventory tables, pointers to the evidence dossier ("see 6.3", "see 6.4"), German terms and dates of development runs
were replaced by plain statements. "Stock targets" reads "Inventory targets" in the two captions.

Direct edits corrected: "frm"; "is clipped NUTS3"; "Pichler et al. (2022)~citet" and "Rauch (1999).~citep" (the name
was printed twice); "Facility statuses are taken from the 2022 accounts" (the accounts hold no statuses: now "those of
2022, the reference year of the input-output table"); the sentence without a verb on the number of agents; power plants
were listed among the facilities "kept as points" while they are aggregated to NUTS2; straight quotes in the criticality
caption.

References: 19 entries added to refs.bib from two dossiers written the same day, every source opened
(`evidence/si_refs_datasources_20261110.md`, `evidence/si_evidence_sea_vot_rail_20261110.md`). To confirm by the author:
the title of Destatis table 46321-0014 (the page could not be read by the search), and the June figures of the OPIS
article (the July figures were read, the June ones follow from stated differences).

## S2 Baseline calibration (Overleaf 9df097a)

| Note | Answer |
|---|---|
| N15 | Cited: the Eurostat modal split (eurostat2023modal), the Eurostat port statistics (eurostat2022ports; the table used is mar_go_aa) and Destatis table 46321-0014 (destatis46321). The split by cargo class comes from Eurostat's road, rail and waterway statistics by commodity group (tables road_go_ta_tg, rail_go_grpgood, iww_go_atygo), named in words. |
| N16 | Amsterdam's fee is stated: 0.75 USD per tonne for all cargo, where the formula gives 0.28 (containers) and 0.09 (other cargo) at its 80.8 Mt; the value sets the division of the North Sea traffic between Amsterdam and Rotterdam (`calibration/round6/derive_feeder_ladder.py`). |
| N17 | Removing the sentence would remove the reason for the fee. It is rewritten in plain words: the fee stands for the feeder leg of a container landed at a small port; deep-sea lines call at a few large ports, the model's sea network serves every port at one rate, so without the fee imports land at the port nearest their buyer. |
| N18, N20 | New table of the modal split (label tab:modal, generator `modal_table`): eight countries, model against Eurostat 2023, with the three German cargo classes under Germany. The list of 33 numbers left the text. |
| N19 | The cause (no traffic within a region) applies everywhere, but the road share is not low everywhere: 8 to 15 points below the statistics in Germany, the Netherlands, Belgium, France and Austria, on them in Poland and Italy. The paragraph now says both, and that the rail rate calibrated by country compensates where the split is on the statistics. |
| N21 | First sentence rewritten on what S2 shows: the tonnage at Kaub (63 Mt against 50-60), the Rhine from Mannheim to the border within 26 % of the counts, bulk on the right modes. "Industrial users" and "alternatives" are gone. |
| N22 | Added: the model understates the exposure of Switzerland and Alsace to Kaub and overstates that of the Rhine-Neckar region, where the tonnage is unloaded instead. |
| N23, N24 | Seaport table: the 30 largest (the two ports without a connector rank below them), then the ports outside the forty where the model routes 50 Mt or more (two rows). The calibration statistics of the text still cover the forty. |

Direct edits corrected: "the Rhine and its Dutch branches (Scheldt and the Kiel canals)" (the run parameters give the
Rhine's rate to eight named waterways, now listed; the waterways not named pay 1.5 times it, which was missing);
"No other parameters were adjusted to fit the logistic data" (the base road and rail rates, transfers and values of time
had been set before on the same kinds of statistic: said); the Amsterdam sentence; "The loss estimated by the model are",
"these flow", "nearest its buyer unless.", "yet,", a fee ladder "proportional to port throughput" (it falls with it),
"tonnages at Kaub matches"; the sub-heading "The Upper Rhine and the rail shares" (the rail shares were deleted).

Dropped: "the fee ladder sent 140 Mt back to the large ports". The number could not be traced to a pair of runs: against
the round before the ladder the secondary ports lose 30 Mt, against round 3 138 Mt, against round 4 215 Mt. The sentence
now says that the ladder returns part of the tonnage to the large ports and does not correct the nearest-coast landing.
This clears one of the two findings the gate had carried since 5 November.

## S3 Scenario construction (Overleaf 8812f58)

| Note | Answer |
|---|---|
| N25 | The profile built on the outlook of 7 September is no longer described and its table (tab:forecast) is removed, in the generator too. One sentence stays on that outlook's miss (12, 22, 42 cm forecast against 25, 7, -2 observed): the Discussion cites it and it is the reason for the two stress profiles. Delete it and the Discussion clause together if it should go. In main.tex the Methods no longer point to that profile. |
| N26 | "Under the 2026 profile". |
| N27 | Sources named and cited: operators' surcharge tables and notices (contargo2026), the weekly count of the Dutch association (schuttevaer2026), single-vessel payloads (wiwo2026, ifw2026), the literature on 2018 (vandorsser2020, ademmer2023). |
| N28 | One name, "loading share", in the paragraph, the header and the cells of the table. |
| N29, N30 | Loading table without the columns "vessel" and "nature" (five columns; the generator follows). |
| N31 | Formula: K = max(s T, 1.02 F), with F the baseline flow of the class on the reach, s its share of the reach's traffic and T the counted tonnage (`anchor_rhine_capacities.py --by-cargo --headroom 0.02`). The pointer to S2, which no longer discusses capacities, is removed. |
| N32 | No: the loading share applies to the Kaub reach alone. The other reaches keep their normal capacity (baseline flow plus 2 %), which the catch-up traffic of the recovery weeks exceeds. The paragraph says so. |
| N33 | The sentence claimed that Lower Rhine rates are "typically three times lower" with the Contargo notice as source, which that notice does not show. Now: the factor of one third is an assumption; operators set the surcharge by gauge and the Lower Rhine, with its own gauges, is less restricted; runs with a factor of zero and of one gave the same loss. |

Found while answering N25 (important). The Gauges paragraph said the forecast was "reissued on 7 October ... at
DEUlossQ %", but that macro is the loss of the batch of 2 November (1.11 %); the reissue of 7 October gave 1.54 %
(forecast manifest). Every number of the manuscript comes from the rerun of 2 November (baseline calibrated in October,
one capacity per cargo class), on the hydrological information of 30 September. S3 now states the three versions and
that the first release for September (6 November) came after the last one. Two things remain the author's: the Methods
still call the reissue of 7 October "the batches of this paper" and score "the series as issued on 7 October", while
the prospective table shows the rerun's series (two notes placed in main.tex); and the forecast manifest listed only
two issues (a row for the rerun and a dated paragraph were added, to be checked).

Direct edits corrected: "We built weekly means ... from PEGELONLINE, which provide", "stay at 0.08", "comes from various
quantity", "inSection", "is repeated until all flows are reassigned, if possible" (now: until no reach is over its
capacity; a cut share without a route returns to the supplier's inventory), a macro without its braces before "to".
In the loading table: the history of the 15 cm row ("the earlier version of the table took 0.12 here ... rebuilt 6 Oct")
is removed and four sources are cited.

## S4 Mechanism tests (Overleaf 3b6c165)

| Note | Answer |
|---|---|
| N34 | An introductory sentence lists what the section checks. |
| N35 | The caption of the modal-switch table is one sentence. Its content is a paragraph, "The modal-switch rule", which states the rule (access allowance of 50 km, line-haul threshold of 100 km, road never a main-leg mode for bulk), the reason for it (a truck carries 25 tonnes against 2,000 and more for a barge or an ore train, the sentence deleted from S3), the classification of the 2,831 pairs and the reading of the table. It says that the test dates from September 2026, on the baseline before the calibration. |
| N36 | "Capacity and surcharge" in plain terms, with the three losses: surcharge alone, nothing blocked, no loss; capacity limit alone, 11.7 billion USD of bulk blocked, 1.60 % of a quarter; both, 10.3 billion blocked, 1.11 %. The capacity limit produces the loss and the surcharge reduces it. No mention of an earlier version. |
| N37 | Paragraph on supplier weights removed. |
| N38 | Heading and caption share one title, "Weekly flows turned away at Kaub" (the table holds what the limit turns away, not what passes). |
| N39 | A header spans the three flow columns. It reads "flows turned away (kt)": the columns are tonnages from the run log, not million USD. |
| N40 | "cut" is renamed "total" (it is the sum of rerouted and blocked). The tonnage that passes Kaub each week is not in the run log; if that is what "total flow" meant, it needs the link-level export of the run. |
| N41 | Paragraph "Conservation and stationarity" removed. |
| N42 | Paragraph and table moved to S7 and rewritten there. |
| N43, N44 | Two paragraphs and two tables: the levers under a rail ceiling (tab:cross) and the two waves at two refill times (new label tab:crosswaves; main.tex updated). |
| N45 | The reference column is named in both tables ("no rail substitution (reference)", "refill time 30 days (reference)"). |

Direct edits corrected: "surchage" (twice); "blocked in the baseline" (it is the reference run); the row label "(the paper)".

## S5 What crosses Kaub (Overleaf 5f5c5af)

| Note | Answer |
|---|---|
| N46 | Checked: the main text describes the French chain in words and points to this section for the figures, which are only here. The paragraph is kept, cut to the two amounts and to where the German inputs go; the clause on the haulers' fuel, which the main text has, is removed. To remove it entirely, remove the pointer in the main text too. |

Direct edit corrected: the price sentence gave the same share twice. "Constraint" reads "capacity limit".

## S6 Two representations of the river (Overleaf 2283201)

| Note | Answer |
|---|---|
| N47 | Section removed. Its message is one paragraph under "Choice 1" of the section on the 2018 event, where the note says it was repeated, rather than in S5, whose subject is prices at Kaub. The table moved there with a short caption. Everything else (the history of the representation, the first version's runs, the 2026 results of the floor representation) is gone from the SI. |
| N56 | The paragraph stops at the onset; the two options are named as in the main text: the capacity limit and the floor representation (table rows renamed too). |

Direct edit corrected: the draft read "Option (i) [binary thresholds] captures the right onset, whereas, with option (ii)
[loading curve], losses only start mid-October". It is the reverse: the capacity limit starts in August, the floors in the
week of 22 October. Also "see able", and "Choice #1", whose unescaped "#" stopped the compile.

## S7 Sensitivity analysis (Overleaf 22088a2)

| Note | Answer |
|---|---|
| N48 | The 129-run table is replaced by one sensitivity table (tab:revision, 33 rows: rule or parameter, reference value, alternatives tested, loss of 2026 and of 2018, change against the reference run), generated from the comparison tables by `si_tables.revision_table`. The text has four short paragraphs: the approach (one change at a time on the same network, and the three sets of runs of another kind), the reading of the table, what was not varied and why, and the count of runs by list. The list of runs is `additional_data/runs_20261102.csv` (written by `si_tables.runs_table`); it is in the code repository, which the Code availability statement archives on Zenodo. main.tex points to the file. |
| N42 | No mention of a revision remains in the paragraph, the table or the figure caption. |

## S8 Rail (Overleaf aca31c7)

| Note | Answer |
|---|---|
| N49 | The section opened with "Rail is a bounded substitute in this study, not a lever", which the note found hard to follow and which contradicted the main text ("Rail is a lever whose size the model cannot set"). It now opens as the main text does: what limits rail is not the price of a train but the number of trains that can be added at short notice, which is not known, so rail is reported as a sensitivity and not as a sized lever. |
| N50 | The 6.7 Mt of rail freight a week had no source. The item now gives the estimate the figure is applied to (Kiel Working Paper 2155, Appendix B: a day of low water raises rail tonnage by 0.07 %, about 2 % over a low-water month), says that 6.7 Mt a week is the order of the German total, and cites the nearest official figure (362 Mt in 2024, 7.0 Mt a week; new key destatis2026gueterbefoerderung). Where 6.7 itself came from is not documented in the study's files; it is close to the 2025 total (350.9 Mt, a figure read on a mirror of the official series and not cited). |

Direct edits corrected: "eligigle", "the tonnage of bulk can be rerouted" (a sentence without "that"), percentages without their sign.
main.tex: "The ceiling is reached in nearly every week of both events" cited the table of the crossed levers; it now cites the
week-by-week table of the rail runs (tab:railweeks).

## S9 The 2018 event (Overleaf 9751f59)

| Note | Answer |
|---|---|
| N51 | The regression of the benchmark is written as an equation (monthly growth of the production index on the change in the number of days below 78 cm, its lag and the lagged growth), followed by the growth that low water induces and its cumulation, which is the shortfall. The three coefficients and their standard errors are those of column 1 of Table 2 of the cited study. |
| N52 | "Why daily?": the regressor counts the days of a month on which the gauge is below 78 cm, so the daily record is needed. The sentence says so and gives the five counts (29, 14, 31, 30 and 3 days from August to December 2018). |
| N53, N54 | The benchmark and its band are those of the validation figure of the main text: referenced. |
| N55 | "Check it is correct": it was not. The model's counterpart is aggregated as the production index is (the shortfall rate of each sector weighted by its value added in the German input-output table, over sections B to D; a day takes the value of its model week, a month is the mean of its days, the event is the sum of the months), not "as done in" the benchmark study, and it is a weighted mean of rates, not a sum of weekly losses. Rewritten from `matched_estimand_2018.py`, which computes it. |
| N57, N58 | The paragraph on the level of the inventories is in the sensitivity section (S7), with its values in a small table (new label tab:ladder; every cell is a macro of `numbers.tex`). |
| N59 | The paragraph on the supplier networks, the loading curve and the number of suppliers is in S7 too. |

Direct edits corrected: the numbers of low-water days were written in centimeters with a tilde accent (`29\~cm`); they are
days. "See Table 2, column 1" pointed to this paper's Table 2 instead of the cited study's.
The section now holds the benchmark and the one choice made on it, the representation of the river; its first sentence
says where the two other comparisons are. main.tex: three pointers follow the moved paragraphs, and a note marks the
sentence of the Methods that still counts three choices made on the 2018 benchmark (open point 2 below).
Tooling: the lint skips the lines of a displayed equation (the SI has its first one); the hand-written table sits between
table markers so that the lint and the gate read it as a table.

## S10 Weekly sequence and model specifications, now S4 (Overleaf 2591144)

| Note | Answer |
|---|---|
| N60 | The section is not a result: it moves up, after Scenario construction, and becomes S4, as the note names it. The sections after it shift by one. It could also precede S3; it follows it because S3 defines the capacities and the surcharge that the weekly sequence then uses. |
| N61 | The paragraph on the fleet lever joins the rail section, renamed "S8 Rail and the low-water fleet". |

Direct edits checked: punctuation of the two paragraphs the author wrote in this section.
Every pointer to a section was updated to where its content now is, one by one (8 in si.tex, 15 in main.tex). The sensitivity
runs that sat in the former S4 are in S7 (stress paths, headroom, floor of the loading curve), so a pointer to "S4" became
S5, S7 or S8 according to what it points to.

| Author's version | After the revision |
|---|---|
| S1 Scope and data | S1 |
| S2 Baseline calibration | S2 |
| S3 Scenario construction | S3 |
| S4 Mechanism tests | S5 |
| S5 What crosses Kaub, and at what price | S6 |
| S6 Two representations of the river | merged into S9 |
| S7 Sensitivity analysis | S7 |
| S8 Rail | S8 Rail and the low-water fleet |
| S9 Selecting the representation of the river on the 2018 low water | S9 |
| S10 Weekly sequence and model specifications | S4 |

## Open points for the author

Decisions the revision could not take. The first two are marked by notes in `main.tex`.

1. **Which forecast the paper reports and scores.** Every number of the manuscript comes from the rerun of 2 November 2026
   (calibrated baseline, one capacity per cargo class). The Methods still call the reissue of 7 October "the batches of this
   paper" and say that the scoring uses "the series as issued on 7 October". The 7 October issue gave a German loss of
   1.54 % of a quarter; the paper prints 1.11 %. S3 now states the three versions (28 September, 7 October, 2 November) and
   `forecast_manifest.md` has a row for the rerun. To decide: score the series issued on 7 October, with the rerun as the
   paper's analysis, or score the rerun and say that it was produced after part of the season was observed.
2. **"Three modeling choices were made on the 2018 benchmark"** (Methods). The SI, as revised, presents one choice made on
   2018 (the representation of the river) and two sensitivities kept at their reference values (level of the inventories,
   number of suppliers). The Methods sentence should follow, or the SI should go back to three choices.
3. **Sea rate.** The author's cell said that the sea rate does "not influence the results". No run tests it, so the cell
   says instead that sea lanes carry no capacity limit and what the rate bears on. A run with the bulk rate (0.0034 to
   0.0051) would allow the sentence.
4. **N40, "total flow".** Read as the sum of the flows turned away. If the tonnage that passes Kaub each week was meant, it
   is not in the run logs and needs the link-level export of the run.
5. **N25, the 7 September vintage.** The paragraph and the table are removed; one sentence on the outlook's miss is kept
   because the Discussion cites it.
6. **N46, the French chain.** Kept, shortened, because the main text points to it for the figures. To drop it, drop the
   pointer too.
7. **N60.** S4 follows S3; it could precede it.
8. **Two sources to confirm by eye**: the title of the Destatis table 46321-0014 (modal split) and the OPIS figures for
   June 2025 in the tanker-rate cell; both were read on pages that could not be opened in full.
9. **Evidence worth knowing before a referee finds it** (S1 block): the operator cost of a liquid-bulk train is 0.018 EUR
   per tonne-kilometer against the model's 0.085, which the cell now calls an effective cost; the sea rate matches container
   carriers and is two to three times too low for bulk; the values of time on rail and on waterways for containers are three
   to four times above the meta-analysis of Binsuwadan et al. (2022).
10. **AI disclosure.** `main.tex` line 306 names one model version (Fable 5.1); this round ran on Fable 5.2. The paragraph
    "Use of AI tools" names no version. The same line is the one overfull line of the compile (6.9 pt).

## State of the checks at the end (10 November 2026, evening)

- `si.tex` has no note left. `main.tex` has seven: four older ones (email, a placeholder, the AI statement to confirm, the
  Zenodo DOI) and the three of this round (open points 1 and 2).
- `paper_gate.py` on the version pushed last (Overleaf 2591144): PASS. No failure in the lint, the numbers, the ledger and
  the compile. Warnings: 196 of 516 macros of `numbers.tex` are not used; 28 number words to read by eye; 14 entries of
  `refs.bib` are not cited (none added in this round) and 28 cited entries have neither DOI nor URL (none added in this
  round); one overfull line (open point 10). Report: `review/paper_gate_20261110.md`.
- Ledger: the 171 entries whose sentence left the manuscript are dropped and listed in `review/ledger_dropped_20261110.txt`;
  the reworded claims have new entries in `paper_gate_ledger/si_c.yaml` (74 allowed literals, 13 claims bound to macros).
- Tables: `si_tables.py --check` on the final file finds the numbers of 13 tables equal to the run outputs (criticality,
  cross, cross_waves, gate, loading, modal, ports, rail weeks, representations, sensitivity, stock overrides, stocks,
  thresholds). Four tables cannot be recomputed on this machine any more (rates, channels, the sector table of the forecast
  and the forecast table of the main text): they need the folders of the final runs, see below. Their cells equal the tables
  generated from those folders at 17:20 the same day, before the folders went; the two value-of-time cells of the rates
  table, whose form changed afterwards, were checked against the job lists (0.32 on the waterway in each of the 129 jobs of the
  batch's lists) and the configuration. No table number was typed by hand.
- `numbers.tex` is unchanged by the revision.
- **The local copy of the final runs is gone.** `C:/dsc_runs/rhine2026` lost the folders of the batch of 2 November (every
  `*_r6_bycargo*` folder, 129 runs) and of the calibration rounds at 17:54 on 10 November; their logs remain, and the
  folders of the 7 October batch remain. No deletion was run there by this session. The cluster still holds the 129 runs
  (`/projects/disruptsc/runs/rhine2026`), but their batch archives were deleted in the clean-up of 8 November, so a
  restore means packing them again (`pack_results.sh`) and downloading them. Until then `make_numbers.py`, the gate's
  `--regen` and the four tables above cannot be regenerated locally.
- Two tool traps found and closed on the way: `si_tables.py` fell back on the scope's configuration, without a word, when
  the reference run's `parameters.yaml` was missing, so a check compared the rates table with values the batch did not use
  (it now skips the table, as the others that need a run folder); the gate's reference check did not read the citations
  inside table cells and called 13 cited references "never cited".

## Addendum, 10 November 2026, 20:55: the local copy of the final runs is restored

On the author's request the 129 folders of the final batch were packed again on the cluster, downloaded and extracted
into `C:/dsc_runs/rhine2026` (record: `cluster/restore_20261110/README.md`). The checks that could not run above have
run since:

- `si_tables.py --check`: the 17 tables are recomputed and agree with the manuscript, the four of the list above
  included (rates, channels, the forecast table of the main text and its table by sector).
- `paper_gate.py --regen`: PASS. The 516 macros of `numbers.tex` and the 17 tables regenerated from the runs equal the
  version on Overleaf (2591144). Report: `review/paper_gate_20261110_regen.md`.

No number of the manuscript changed, and nothing was pushed to Overleaf for this.
