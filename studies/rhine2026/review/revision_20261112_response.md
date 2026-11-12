# Round of 12 November 2026: the author's version of that evening

Base: Overleaf `4dfe508` (the author's version of 12 November, 17:02 UTC; `main.tex` changed in 43 places and `si.tex`
in 15, with 14 inline notes). Result: Overleaf `b3ddc6e`, one push. This file is the record of the round.

Everything the notes asked for is applied. Three notes said "to discuss" or "consider" (N03, N06, N14, all on the
refill time). I applied the direction they lean to, with one safeguard, and the reasons are in section 2; open point 1
says how to reverse it.

Contents: 1. Method. 2. The fourteen notes. 3. Direct edits that had to be corrected. 4. Found on the way.
5. Long sentences and removed details (N07). 6. For the author. 7. State of the checks. 8. Scripts.

## 1. Method (unchanged)

- The author's version is the baseline. Direct edits are kept; they are only checked for breakage.
- Each inline note is answered in the text and removed. The two notes on the Zenodo DOIs stay.
- No number is typed by hand: numbers are macros of `numbers.tex` or cells of tables checked against the run outputs.
- The gate (`paper_gate.py --regen`) runs before the push.
- Nothing is posted in the review panel of Overleaf.

## 2. The fourteen notes

Notes are numbered in file order: N01 to N09 in `main.tex`, N10 to N14 in `si.tex`.

| Note | Where | The note | Answer |
|---|---|---|---|
| N01 | Fig. 2, caption (b) | "shortfall" is used for two different things; is it a threshold? | It is not a threshold. It is the share of the normal tonnage that the loading curve keeps off the river at each gauge (one minus the loading share). The two variants multiply it by 1.15 and 0.85 at every gauge. It is now called the **capacity reduction** everywhere: Fig. 2 (caption and legend), Results, the caption of Fig. 4, Table S-revision, S9, the caption of Fig. S4. "Shortfall" is kept for production. The flat profile is "the same reduction of river capacity spread evenly". The Methods now say "loading share" where they said "loading factor". If you prefer "loading-curve shortfall", it is one replacement. |
| N02 | Fig. 2, panel (b) | Merge the legend entries of the model and its range; remove the alternative river; remove "(statistics)"; centre the range on ×1; two markers for the loading curve | Done. One entry for the model, drawn as in (a). The alternative river is gone from (b); it stays in (a). The gray range of the eleven networks sits on ×1. The loading-curve variants are two blue triangles on ×1. One deviation: the entry reads "model (reference network; at ×1: interquartile and min–max of the 11 networks)", not "model (mean, ...)", because the line of (b) is the reference network: the inventory levels were run on it alone. In (a) the entry is "model (mean, interquartile, min–max of 11 networks)". The caption follows. |
| N03 | Results, the memory of the season | Drop the refill-time test from the main figure? With 15 days it also depends on the suppliers' ability to raise production. To discuss | Applied: Fig. 4b shows the 30-day curve only. Your reason is right, and the model confirms it (see N14): at 15 days the result depends on three settings at once, the refill time, the suppliers' spare capacity (25 %) and the headroom of the reopened river (2 %), and only the first was varied. A curve for one of the three in the main figure invites the question you expect. The safeguard: the Results keep one sentence, "How fast this memory fades depends on the refill time of the inventory rule, 30 days, and on what suppliers and the reopened river can deliver during the recovery (Supplementary Section S7)". Without it, a reader who finds in the SI that the +12 % disappears at 15 days would see nothing of it in the main text. |
| N04 | Fig. 4 | Make the plot slightly larger; remove "(no gap)" | Done. The figure is taller (3.6 against 3.1 inches at text width) and panel (b) is wider (43 % of the width against 41 %). "(no gap)" is removed. The x label of (b) is on two lines; it was wider than its panel. |
| N05 | Discussion, the test | What is the reader supposed to do with this test? | Reframed as a short paragraph of its own: "The 2026 results are a forecast that readers can check." It says what was fixed before the statistics (the monthly path, Supplementary Table S10), what the reader compares it with (the production indices as they are released), by which rule (set in advance, S6), and what failure means ("the model fails if it does no better than a forecast of no loss"). The turnover indices test the rule on services. The gap on the share of firms affected stays as the last sentence. |
| N06 | Discussion, the refill time as an uncertainty | Keep in the SI only? | Applied. The sentence "The refill time is one of the largest single uncertainties ..." is gone from the Discussion. The numbers are in S9 (−30 and +32 %), in Table S-revision and in Fig. S4. The Discussion keeps "with the 30-day refill time of the model ... and a faster refill shortens it further (Supplementary Section S7)". |
| N07 | End of the Discussion | Sentences too long, many clauses joined by ";"; remove small clauses of detail | Done on the whole of `main.tex`, Methods included. Section 5 gives the counts and the list of what was removed. |
| N08 | Methods, Prospective test | I do not understand this section, how it is used, where the scores are | There is no score in this version, and the paragraph now says so first: the indices of October to December are not published. The paragraph is cut from 317 to 195 words and says in order: the results are a forecast; no score yet; where the path is (Table S10) and where the rule is (S6); the rule in two sentences; what the score does not prove; the deposit that dates the forecast. The protocol in full stays in S6, which also says now "No score is given in this version: it will be computed when the four months are published". The test is used in three places of the main text: the Introduction (two mentions) and the new paragraph of the Discussion (N05). |
| N09 | Table of the prospective test | Move it to S6; low-water days first, then the published specification and its band, then the model; remove the loading-curve rows; sums for all rows | Done. It is Supplementary Table S10, after the protocol. Rows in your order, a rule between the statistics and the model, the two loading-curve rows removed (their runs are in Table S-revision), a sum in every row (126 low-water days). Two choices of mine. (a) The sums of the rows "lowest" and "highest of the eleven networks" are the lowest and the highest sum of a network (0.0 and 5.8), not the sum of the months printed in the row; the caption says that each cell of these rows is a statistic of its column. (b) I added one row, "model, mean of the eleven networks": the protocol scores this series, and it was printed nowhere. The main text now has six figures and no table. |
| N10 | S5, the modal-switch rule | "... such that that mode pass the 100 km threshold": is that correct? | No. The rule has no such condition. A route changes mode when it adds more than 50 km on a mode that is not a line-haul mode of the normal route, whatever length that mode then reaches (model code: `commercial_link.py`, `_routes_have_modal_switch`). The 88 km of truck around the reach is a change of mode although the road total stays under 100 km. The paragraph is rewritten on your plan (line-haul and access modes, the example, the two thresholds, the penalty, the restrictions for bulk). |
| N11 | S5, "54 on a path without penalty" | If it is without penalty, it is "own modes", no? | Yes. The two groups differed only by which of the model's two route searches found the route. All 54 have a main leg by rail on their normal route, and 51 of them use no new mode at all. They are merged: "1,278 deliver on a route that is not a change of mode (409 million)". |
| N12 | S5, end of the paragraph | Check the consistency of what I write | One sentence said the opposite of the adopted rule. "For routes that already have 100 km or more of road ... a longer road leg to pass the reach is allowed" is true under the kilometer thresholds alone. The adopted rule forbids it, because road is never a line-haul mode for bulk; this is what raises the share without an alternative from 67 to 85 %. The text now says both. The sentence on the 88 km of truck is also corrected (section 4, item 4). |
| N13 | Table S-thresholds | Are these indicators compared with evidence to set the baseline? | No, and the text now says so: "No observation gives this share: the reach has never been closed, and the freight statistics do not record which shipments combine modes. The thresholds are therefore conventions, not values fitted to evidence." The table shows how much they matter. Their effect on the loss is tested in full runs through the amount of bulk that may go by rail (S8: none, 50 kt, 140 kt). |
| N14 | S7, the two episodes at a 15-day refill time | Keep this? A faster refill should be bounded by the suppliers' overproduction capacity; is it captured? | It is captured. A supplier produces at most 125 % of its baseline output (utilization rate 0.8, S4) and rations its clients beyond that. The reopened Kaub reach passes at most 102 % of its normal tonnage (headroom 2 %). A buyer that refills in 15 days orders twice as large a part of its inventory gap each week, but receives only what these two bounds let through. Neither bound was varied with the refill time. The paragraph now says this in four sentences. I kept the paragraph and its table: once the 15-day curve leaves the main figure, this is the only place where the reader finds it. The Methods also give the 125 % now. |

## 3. Direct edits that had to be corrected

All other direct edits are kept as written.

| Where | The edit | What was wrong | Now |
|---|---|---|---|
| Introduction, literature | "do not capture supply chains" | Too strong: the studies of ports and of trade between regions follow supply chains through input--output tables. What they lack is firms | "do not capture firm-level supply chains" |
| Introduction, literature | "A recent general-equilibrium economic assessment ... treats" | Three works are cited, and one is an input--output study of 2012 on a port closure | "Economic assessments of waterway disruptions in the Mississippi basin, input--output or general-equilibrium, treat" |
| Introduction, literature | "disrupted\citep" | No space before the citation | Space added |
| Fig. 1, caption (b) | The note on the asterisk removed | The figure still carried "bulk*" | The asterisk is removed from the figure |
| Fig. 2, caption | (b) and (c) shortened | (b) had lost the colon of its list; (c) had an open bracket; the range of (b) and the bands of (c) were no longer explained | (b) "... on the reference network against the inventory multiplier, with the eleven networks at ×1 (gray), the benchmark (green), ..."; (c) "(line and bands as in a)", bracket closed |
| Results, 2018 | "losses starts"; "navigation association" | Grammar | "losses start"; "an inland-navigation association" |
| Results, the two episodes | "(the backlog. After"; "drained by the first event" | Open bracket; "event" is the whole season in the paragraph before | "(the backlog). After"; "drained by the first" |
| Results, August estimates | "Our model estimates X % of a quarter" | The object was missing | "Our model gives an industrial loss of X % of a quarter over the five weeks of the August episode". "Inside the EUR 1--2 billion" stays out, as you cut it; S6 still says it |
| Results, reduced capacity | "no buyer cuts its orders ... and no delivery is refused, because freight cost is only about 5 %" | The first part is a rule of the model (demand does not respond to prices), not a consequence of the freight share | "In the model, no buyer cuts its orders when its inputs cost more, and with this level of surcharge no delivery is refused (Methods): freight cost is only about 5 % ..." |
| Results, rail | "except for shipments that already travel a significant route by rail to reach a Rhine terminal" | The rule is about a rail leg of 100 km or more, in either direction | "except for shipments whose normal route already includes a main leg by rail" |
| Results, rail | "of to 140 kt"; "an all-cargo response implied by [6] in 2018" | Typo; the estimate is the response of rail freight to past low waters, not a figure for 2018 | "With a higher ceiling of 140 kt a week, the response of all rail freight to past low waters estimated by ref. [6]" |
| Discussion, ranking | "and when the railway can take on 50 kt a week" removed | "although the benefits then overlap (Table S-cross)" was left without its subject | The clause follows the rail sentence: "Inventories or the fairway still come first under this ceiling, although the benefits then overlap" |
| Discussion, ranking | "Deepening the Middle Rhine fairway is in discussion" | Results and Methods say it is a project of the federal transport plan since 2016 | "is planned but will take a decade to materialize" |
| Discussion, pooling | "no shortages are happening there"; "Next"; "specific per origin region" | Wording | "no shortage arises there"; "Second"; "specific to its region of origin" |
| Discussion, limitations | "In 2018, ... shifted to rail and road in 2018" | The year twice | Once |
| Methods, Prospective test | "indices were released after submission" | They are not released yet | The paragraph is rewritten (N08) |
| S6, the protocol | "whereas the reference network is at baseline in November" | The reference network is the model; there is no contrast | "; on the reference network, it is at baseline in November and above it in December" |
| S6, the protocol | "the statistical model of [6]"; "forecasted" | A bare number as a noun; verb form | "of ref. [6]"; "forecast" |
| S8, the fleet | "The central table with its loading is raised by 0.10"; "It loads more" | Grammar; "it" had no clear subject | "The loading share of the central table is raised by 0.10"; "This fleet loads more" |
| S8, rail | "Rail is a lever based on the number of trains" | Wording | "whose size depends on the number of trains" |

## 4. Found on the way

1. **Numbers glued to the next word in the PDF, five places.** A number macro followed by a space swallows it. The PDF
   read "between the weeks of 5 Octoberand 19 Octoberin every version", "0.2and 0.1 billion USD", "the week of
   19 October2026", "between 0.65and 1.86 %". These were there before this round. Fixed. The
   gate now fails on such a place (`paper_gate.py`, check "macros"; tested on a copy with one of them put back), and
   `review/check_macro_spaces.py` lists them.
2. **"The loss falls by −13 %".** In the fuel chain paragraph the signed macro followed "falls by". It now reads
   "falls by 13 %".
3. **The Methods named the run list of 2 November.** The list of the 128 runs is `runs_20261111.csv`.
4. **The 88 km of truck.** S5 said that for nine-tenths of the pairs without an alternative the bypass is 88 km of
   truck. The archived classification gives: nine-tenths have a bypass by land; it is 88 km of truck for two-thirds of
   the pairs (65 %), a shorter truck leg for 13 %, and a train for 12 %. The text says so.
5. **The test of S5 is dated again.** You removed its parenthesis. I kept a short form, "(week 6 of a ten-week run, on
   the baseline before the calibration of Section S2)", because the counts (2,831 pairs, 1,243 million USD) are those
   of the earlier baseline and a reader could not otherwise tell.
6. **The ledger of the gate.** Your edits had detached 46 of its entries from their sentences (numbers and fractions no
   longer tied to their source). All are entered again on the new wording; with the sentences cut in this round, 98
   entries were replaced by 83.
7. **"ton-kilometer" in the Methods.** Now "tonne-kilometer", as in the rest of the paper.
8. **The modal-switch rule in the Methods** now has its clause on road: "for bulk, road always counts as such a mode
   (Supplementary Section S5)".

## 5. Long sentences and removed details (N07)

Sentences joined by ";" or by a colon are cut where each part stands alone. No number and no claim changed.

| | Before this round | After |
|---|---|---|
| Main text, sentences | 160 | 227 |
| Main text, semicolons | 38 | 4 |
| Main text, mean length (words) | 33 | 24 |
| Main text, sentences over 40 words | 47 | 17 |
| Methods, sentences | 81 | 125 |
| Methods, semicolons | 36 | 6 |
| Methods, mean length (words) | 38 | 24 |

Four semicolons are left in the main text: two in your list of the Discussion ("industry ...; the fuel chain ...; and
the building-materials chain"), one in the second limitation, and one inside a bracket of references. The sentences
still over 40 words are mostly lists of numbers.

Clauses removed as detail:

1. Introduction: "placed where plants and jobs are" (said in the Results and in the caption of Fig. 1).
2. Results, the model: "the rest dry and liquid bulk".
3. Discussion, ranking: "(a quarter with its gain extended to 100 cm)" (in the Results with its number).

Candidates I left, for you to judge:

4. Introduction: "After the second-warmest summer on record [ref]".
5. Results, 2018: "The GDP effect of 0.3--0.4 % reported for 2018 is this path's November value times industry's share
   of the economy." It ties the benchmark to the GDP figure of the Introduction; it is not needed for the test.
6. Results, building materials: "The 2018 run has the same anatomy."
7. Results, adaptation: the amounts of inventory in billion USD (26 and 4.5).

Two matters of form follow your edits and are applied through `main.tex`: fractions are hyphenated as your
"three-quarters" (two-fifths, two-thirds, four-fifths), and lists take the serial comma that you added in a dozen
places. `si.tex` is not harmonized.

## 6. For the author

Answer by number; no answer means "leave as it is".

1. **The refill time (N03, N06, N14).** Applied as you lean: out of Fig. 4b and out of the Discussion, kept in S7 and
   S9 with what bounds the refill. One sentence in the Results and one clause in the Discussion still say that the
   memory depends on the refill time. To reverse: the figure script draws the 15-day curve again with one block
   restored (`plots/wave_figure.py`).
2. **Fig. 2b legend.** "reference network", not "mean" (N02). The mean of the eleven networks and the reference
   network both round to 2.1 percent-months at ×1, so the point would not move visibly if you prefer the mean there.
3. **Table S10.** One row added (mean of the eleven networks) and the meaning of the sums of the two range rows (N09).
4. **The candidates 4 to 7 of section 5.**
5. **The heading "The 2026, two-episode event".** I did not touch it. "The two-episode event of 2026" would avoid the
   comma.
6. **"waves" in the SI.** S7 and its table now say "episodes", as the main text. The labels and the run names keep
   "wave".
7. **Length.** Main text 5,338 words (guide 5,000; it was 5,448), Methods 3,066 (guide 3,000), abstract 167 (it was
   197).
8. **Still open from before:** the Zenodo deposit and its two DOIs; "Calibrated on the 2018 low water" in the
   abstract; the cover letter.

## 7. State of the checks

`paper_gate.py --regen`: **PASS** (`review/paper_gate_20261112_round.md`). The 519 macros and the 16 tables regenerate
from the runs and equal the manuscript; the ledger, the bare numbers and the compile pass (63 pages, no undefined
reference, one overfull box). Warnings as before: 50 number words, 14 uncited bibliography entries, 194 unused macros.
`check_macro_spaces.py`: no place left. The pages of Fig. 2, Fig. 4 and Table S10 were looked at in the compiled PDF.

Not done: the review panel was not run on this version; the submission package was not rebuilt.

## 8. Scripts (all in `studies/rhine2026/review/` unless said)

| Script | What it does |
|---|---|
| `patch_main_20261112_round.py`, `patch_main_20261112_round_b.py` | The changes of `main.tex`, paragraph by paragraph |
| `patch_si_20261112_round.py`, `patch_si_20261112_round_b.py` | The changes of `si.tex` |
| `patch_figures_20261112.py` | `plots/validation_figure.py`, `plots/wave_figure.py`, `plots/decision_figure.py` |
| `patch_tools_20261112_prospective.py` | `si_tables.py`: the table of the prospective test as a table of the SI |
| `ledger_20261112_round.py` | The ledger of the gate; `ledger_dropped_20261112.txt` lists what left |
| `check_macro_spaces.py` | A number macro followed by a space |
| `check_prose.py` | Open brackets, a word twice, punctuation |

## 9. Late evening: the protocol of the 2026 test leaves the paper

The author's question in chat, after reading the round: "do we really need to ship this 2026 protocol? It exposes to
more questions, I think the paper is already good without it. I would remove S6, put the monthly path by sector and
the two prospective tables in S5. What do you think?"

My answer was yes, and it is applied (Overleaf `69660ff`, one push). The reasons:

1. **The test could not show much, and it could fail for the wrong reason.** The score compared the model with the
   production index measured against its level of January to June. That index also carries demand, energy prices and
   the industrial trend, and the paper itself said that the score "does not validate the causal loss". The verdict rule
   ("judged wrong if its score exceeds the zero path's") then turned mostly on whether German industry as a whole ended
   2026 above or below its first half. A pass would have proved little; a fail could have come from the business cycle.
2. **It needed a story of dates that a referee cannot verify:** the model fixed on 2 November, the index of September
   released on 6 November and left unopened, the runs of 11 November.
3. **The four results do not rest on it.**
4. **Removing it now is clean.** No index has been scored, nothing was deposited and nothing was submitted, so this is
   a choice of design, not an answer to a result.

What went and what stayed:

| | Before | Now |
|---|---|---|
| SI, Section S6 "The 2026 test" | The protocol (index, comparator, months, score, verdict, dates), the signed quarterly changes, the two tables, the estimates of August | Removed as a section. The two tables stay, each with a paragraph, as results of the 2026 season |
| Where the two tables are | S6 | At the end of "The 2026 season in detail", which is now S6. Not in S5: see below |
| Table of the monthly path of industry | "The prospective test" | "The monthly path of German industrial production, 2026" (Table S13 in the PDF); same rows |
| Table of the sectors | "Pre-specified for the prospective test: ..." | "In the statistics, the production index gives the industrial rows by month, and the turnover index of transport and storage the operators' rows" (Table S14) |
| SI sections | S1 to S9 | S1 to S8: the former S7, S8 and S9 are S6, S7 and S8. 32 section numbers changed in the two files |
| Methods, "Prospective test" | A paragraph of 195 words | Removed |
| Methods, Scenarios | "The model, its parameters, and the loading curve were fixed on 2 November 2026. The production indices of July, August, and September 2026, released on ..., entered no choice." | "The production indices of 2026 entered no choice of the model, its parameters, or the loading curve." |
| Introduction | "... the first from a model of supply-chain propagation, with a test against statistics that are still to be published"; "..., which the statistics of the autumn of 2026 will test" | Both clauses removed |
| Discussion | A paragraph, "The 2026 results are a forecast that readers can check ..." | Two sentences at the end of the paragraph on services: the monthly path was computed before the statistics of October to December and can be compared with them, "although these also carry demand, energy prices, and the industrial trend" |
| Results, survey of August | "(Supplementary Section S6)" | Pointer removed; the SI paragraph only repeated the main text |
| Data availability | Gauge profile, monthly path and run tables "deposited on Zenodo at submission" | Everything "upon acceptance; until then, available from the corresponding author" |
| Cover letter | "The study contains a test that is still open ... During review we will score each index ..." | Rewritten without the test. It keeps the replacement of the three forecast weeks of the river at revision |

**Where the tables are.** You named S5. I put them in the section on the 2026 season instead: S5 gives the reasons for
the two choices made on 2018, and these tables are results of 2026. If you prefer S5, it is one block to move.

**What you may still want to reverse or cut:**

1. The deposit on Zenodo at submission is gone with the protocol: it existed to give the forecast a public date. The
   date of receipt of the manuscript now plays that part. One red note is left in `main.tex` (the DOI of the code).
2. The abstract and the Introduction still say that the estimate comes before the production statistics of October to
   December. This is what will make a referee ask how the model compares once they are out. Table S13 is there to
   answer; the two sentences of the Discussion say what such a comparison cannot show.
3. No longer printed anywhere: the signed quarterly changes (+0.39 and −0.23 % of a quarter) and the share of firms
   below baseline at the autumn peak (22.2 and 13.5 %). The macros stay in `numbers.tex`.
4. The row "mean of the eleven networks" of Table S13 was there because the protocol scored it. It can stay as
   information or go.

**Numbers in the earlier sections of this file.** Sections 2 to 6 name the SI sections and the table as they were
before this step: S7, S8 and S9 there are now S6, S7 and S8, and "Table S10" is Table S13. Open point 3 of section 6
still stands for that table; the notes N05, N08 and N09 are superseded by this section.

**Checks.** `paper_gate.py --regen`: PASS (`review/paper_gate_20261112_protocol_out.md`); 61 pages, no undefined
reference. Counts: abstract 167 words, main text 5,270 (guide 5,000), Methods 2,860 (guide 3,000, now within it).
Thirteen entries of the ledger left with the section.

**Scripts.** `patch_20261112_protocol_out.py` (both files), `renumber_si_sections.py` (lists or shifts the hard-coded
section numbers), `patch_tools_20261112_protocol_out.py` (`si_tables.py`, the loading-table ledger),
`ledger_20261112_protocol_out.py`, `patch_submission_20261112_protocol_out.py` (cover letter, reporting notes, README).
