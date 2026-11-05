# Backtest of the panel on the Rhine 2026 manuscript, Overleaf ce22110 (22 Sep 2026)

Panel: R1_methods, R2_transport, R3_economics, R4_editor and editor_synthesis (P1–P10) in this folder. Reference: the
Nature Communications-style review of 22 Sep 2026 (ChatGPT, four disciplinary passes). The 26 scored points are the ones
the task lists: OR1–OR7, NS1–NS7, EC1–EC8 and G1–G4. G5–G7 and the audit tables A01–A18 are outside the scored set.
Authors' verdicts come from reference_points.md. The manuscript check uses the bundle
C:/dsc_runs/review_panel/rhine_ce22110 (paper.txt with Figs. 1–6). The reference reviewer also saw the macros, the SI
outline source and 12 figure PDFs, including F2_modal_split and F3_rhine_profile, which the panel did not have.

## Recall
| | points | FOUND | PARTIAL | MISSED | recall (FOUND + PARTIAL/2) |
|---|---|---|---|---|---|
| all reference points | 26 | 24 | 2 | 0 | 25/26 = 96 % |
| confirmed by the authors | 7 | 7 | 0 | 0 | 7/7 = 100 % |
| critical in the reference | 9 | 9 | 0 | 0 | 9/9 = 100 % |
| rejected by the authors (found = false alarm shared) | 1 | 1 | 0 | 0 | 1/1: false alarm shared (NS3) |

Without the two prompted points (OR1, EC1; see the leakage note), recall is 23/24 = 96 % overall, 5/5 for the
confirmed points and 7/7 for the critical points.

## Point by point
| reference point | severity | verdict | panel point(s) | evidence |
|---|---|---|---|---|
| OR1 bulk substitution vs rail conclusion (confirmed) | critical | FOUND (prompted) | P7; R1 M4, R2 M6(c), R3 M5(c), R4 M7 | R2 M6(c): "Switching bulk to another mode carries a prohibitive penalty, so no rail tariff can matter." The P7 fix, "test a capped rail-capacity lever", is the same remedy as OR1's. |
| OR2 payload must constrain throughput (confirmed) | critical | FOUND | P3; R2 M1, R4 M2, R1 M4, R3 M3(c) | R2 M1: "Above the floors, partial loads never limit throughput … In open weeks the model moves the full baseline tonnage". It names the same consequences as OR2: the fitted ×2 moves (R2 M1(c)) and the fleet lever is inflated (M1(b)). |
| OR3 missing pipelines vs fuel mechanism (confirmed) | critical | FOUND | P2; R1 M2, R2 M2(a), R3 M1(c), R4 M6 | R2 M2(a): "MiRO Karlsruhe, takes its crude by pipeline (SEPL from Fos, TAL from Trieste)". The P2 test reruns with pipeline crude and recalibrates. This is the refinery example OR3 itself uses. |
| OR4 baseline transport validation overstated | major | FOUND | R1 and R2 internal inconsistencies, R2 M2(a), R3 m8, R4 m8; P2 (test only) | R1: the baseline "'reproduces ... the tonnage profile of the Rhine' vs p.9: 68 Mt against 50–60 Mt". The consequence for exposure appears in R3 m8 and R4 m8 (it "feeds the calibrated buffer"). The panel did not raise the modal-split residuals: Figs. S1–S3 are not in the bundle (R2 m3). The editor kept the point only as a CCNR check inside P2. |
| OR5 synthetic firms and pooling need justification | major | PARTIAL | R3 M1(b)(c), R4 M6, R1 m2, R1 m6 | R3 M1(c): "Fuel is rationed pro rata from a national pool. There are no extra imports". The panel objects that the pool spreads the shortage, not that pooling makes national delivery costless and instant. Agents vs firms comes up only as wording (R1 m6). The panel asks for no convergence test on agent resolution. |
| OR6 inventory and recovery dynamics not reproducible | major | FOUND (editor dropped) | R1 m1, m2, m3; R3 M2(d), m4; R4 M4(d), m11 | R1 m2: "give suppliers per input and region, spare capacity and the refill rule; the one-fifth backlog recovery depends on them". R1 m1: "Call ×2 an effective buffer." The panel does not ask for the full equation set. None of this is in the synthesis. |
| OR7 adaptations need common basis and paired comparisons | major | FOUND | P9; R1 M6, R3 M5, R4 M7 | P9: "run the levers on all draws with paired differences, show efficacy against lever size". |
| NS1 observations, forecasts and assumed recovery (confirmed) | critical | FOUND | P6; R2 M5, R4 M1, R1 M3(c) | R2 M5: "Fig. 2 does not flag the forecast weeks … An ensemble median is not a trajectory the river could follow". The remedy is the same as NS1's: run the ensemble members. |
| NS2 gauge height is not navigable depth or fleet capacity | critical | FOUND | P6; R2 M4(a)(c), R2 m3 | R2 M4: "a floor is an economic threshold, not a hydraulic one … Kaub drives every reach". The remedy is to source the floors and use per-reach gauges. The panel does not raise the gauge datum or the depth mapping, and does not ask for heterogeneous vessel thresholds. |
| NS3 weekly averaging changes closures (rejected) | major | FOUND = false alarm shared | P6 (test), Before submission no. 3; R2 M4(b), R1 M3 | R2 M4(b): "Week 9 starts at 5 cm and averages 27 … Close each class for the share of days below its floor". The editor kept this in the action list. |
| NS4 calendar hypothesis not isolated (confirmed) | major | FOUND | P8; R3 M4, R1 M3(b), R4 M5 | R3 M4: "Run August-only and September–October-only profiles and report the interaction term, which is the calendar effect." P8's test ("second wave alone from steady state") is the run the authors made. |
| NS5 closure and adaptation descriptions inconsistent | major | FOUND | P8, P9; all four referees | P8: "lasts five weeks … not 'seven'". P9: "'The closures disappear' (p. 6) is wrong". The panel missed the third inconsistency, that fairway +20 cm is not the 40-cm tank floor. R2 instead praises "the insight that fairway deepening and a lower tank-barge floor are one lever". |
| NS6 fleet feasibility and environmental trade-offs | major | FOUND | P9; R2 M1(b), R2 M7, R3 M5(a)(f) | R2 M1(b): "With capacity, a low-water fleet still carries only a fraction of normal tonnage at 10–30 cm". R2 M7 scales the lever by fleet share, which matches NS6's penetration rate. The panel does not raise the environmental trade-offs of dredging or fleet renewal. |
| NS7 validation must match quantity and geography | major | FOUND | P5 (Tonnage); R2 M3(a)(b), R3 m6, m7, R4 M4(c) | P5: "The check sets rerouted deliveries (p. 5) against vessels counted past Kaub." R3 m7 sets Kaub against all German waterways and a baseline change against a year-on-year change. R2 M1 proposes the 2022 held-out test. |
| EC1 calibration target vs model outcome (confirmed) | critical | FOUND (prompted) | P1; R1 M1, R3 M1(d), M2(a), R4 M3 | P1: "Calibration target and matched loss are different quantities". R3 M1(d): "The model reaches the right total through the wrong sectors." This is the all-sector vs industry-only mismatch the authors confirmed. |
| EC2 "one parameter" understates assumptions | major | FOUND | P5 (Choices); R4 M4(d), R1 M5(d), R3 m9, R2 Q1 | R4 M4(d): "'One parameter' undercounts the choices made knowing the outcome." R2 makes the compensating-errors argument: "the calibrated buffer nets them out". |
| EC3 validation claims stronger than evidence | critical | FOUND | P5; R4 M4, R1 M5, R3 M2(b)(c); R1 m6 | R4 M4: "'Validated' overstates what are four consistency checks … The August 2026 check is against forecasts, not observations". The panel also raises Q3 vs weeks 7–11, timing used in calibration and the December peak vs the November trough. On the survey it notes only the week (R4 M4(c)) and that "no output-based model reaches it" is unsupported (R1 m6). It misses that the IHK survey itself separates production restrictions from cost effects. |
| EC4 prices, real output and welfare conflated | major | FOUND | P7; R3 M3, R2 M6(b) | R3 M3(a): "Higher freight bills, and the real resource cost of sailing at a third of capacity, cannot register." The panel missed the selection and weighting of delivered prices. R2, R4 and the editor endorse the 1–2 % median instead. |
| EC5 loss and recovery accounting identities | major | FOUND (editor kept A–F only) | R3 m1, m3, m4; R1 m3, m4; R4 m2, m11; synthesis Minor | R3 m4: "The catch-up share ('a fifth') depends on spare capacity, re-ordering rules and run length, none of them stated". The panel also raises NACE A–F vs utilities, the 13 % delay rate and the non-additive household loss. It does not raise the sign of the backlog recursion. |
| EC6 service concentration from aggregation and routing (confirmed) | critical | FOUND | P2, P1; R1 M2, R3 M1, R4 M6 | R1 M2: "Gas-fired plants burn natural gas, not refinery output: the link is the aggregate C19→D35 coefficient rated critical." R3 M1(d) adds that the total is matched through the wrong sectors. |
| EC7 "fleet dominates" is not an investment conclusion | major | FOUND | P9; R3 M5, R4 M7 | R3 M5: "Without costs, 'dominates' is unsupported" and "Compare annualised costs under a stated event frequency." |
| EC8 baseline year and measured economy | major | FOUND | P10, synthesis Minor (Units); R3 M6(a), Q1, m2; R1 m5; R4 m1 | P10: "2022 … was the energy-crisis year". Synthesis Units: "'% of a quarter' spans three quarters; USD and EUR are mixed." The panel does not raise Switzerland being counted in "EU". |
| G1 narrow the novelty claim | major | FOUND | R4 Assessment; synthesis Disagreements (Novelty); R1 m6 | Synthesis: "p. 2 omits that [19] already couples supply chains to transport. Claim the extension". The editor files this under Disagreements, not as a P-point. The panel does not raise Acclimate's supplier reallocation. |
| G2 four rhetorical claims as falsifiable propositions | major | PARTIAL | R1 M4, R4 M2, P7, P5 (failure criteria) | R1 M4: "four abstract claims are assumptions, and the discovered content is smaller than stated". The panel attacks each contrast as built in or untested. It does not ask for each headline to be restated as a hypothesis with a refuting experiment, an observation and its assumptions. It does not ask for a mechanism diagram that separates estimated from assumed links either (R4 m4 asks for a decision schematic only). |
| G3 reproducibility is an outline | critical | FOUND | P4; R1 M7, R4 M1, R3 Assessment | R1 M7: "The results cannot be reproduced from the submission … no reader can rebuild or audit the runs." The panel does not challenge the "reproducible to the last digit" claim (p. 10). |
| G4 treat failed validation as evidence | major | FOUND | P3, P5; R1 M5(a), R4 M2(iv), R2 Q1 | R1 M5(a): "the missed late-summer onset (p.7) is explained away". R4 M2: "The buffer multiplier therefore absorbs the missing mechanism." The panel does not use the survey mismatch as a diagnostic. |

G5–G7 are not scored. G5 is visibly raised anyway (R4 inconsistency "Largest uncertainty"; R1 M6 on the level band vs paired
differences).

## The panel's own findings
None of P1–P10 is outside the reference: each matches at least one reference point. P1 matches EC1 and EC6. P2 matches
OR3, EC6, OR4 and, in part, OR5. P3 matches OR2 and G4. P4 matches G3. P5 matches EC3, EC2, NS7 and G4. P6 matches NS1,
NS2 and NS3. P7 matches OR1, EC4 and, in part, G2. P8 matches NS4 and NS5. P9 matches OR7, EC7, NS6 and NS5. P10 matches
EC8.

The rows below are sub-findings inside those points, plus minor points, that no reference point states. They are listed
because they are the panel's own contribution.

| panel point | checkable in text | note |
|---|---|---|
| P1–P10 as consolidated points | n/a | No unmatched consolidated point. |
| P5 (part): the August 2026 cross-check is not independent | yes | Refs [6]–[8] are all Kiel Institute (pp. 2, 11). ×1.5 (0.28) also lies inside the paper's 0.1–0.35 (p. 4, Fig. 4c). EC3 instead calls it "a forecast by another institution". |
| P5 (part): thyssenkrupp (Duisburg) is outside the modelled closure channel | yes, plus outside geography | The text has closures on the Kaub reach and the Lower Rhine at a third of the surcharge (p. 9). That Duisburg lies below Kaub is outside knowledge. |
| P5 (part): calibrated on the reference draw while the ensemble mean (0.30) sits at the lower edge; an ensemble fit (≈×1.85) gives about 0.6 % for 2026 | yes (premise) | The premise is on p. 3. The ×1.85 and 0.6 % are R1's interpolation from Figs. 4b and 6. |
| P6 (part): about 40 % of the 2026 loss rests on forecast weeks 15–16, at 42 and 49 cm against a 50-cm floor | yes | The 40-cm floor run gives 0.33 % (p. 5). The weeks are the BfG median (p. 9). The gauge values come from Fig. 2. |
| P8 (part): the wave ratio is non-monotone in the buffer: 3.2, 1.9 and 3.2 at ×1, ×1.5 and ×2 | yes | (2.16−0.51)/0.51, (0.82−0.28)/0.28 and (0.54−0.13)/0.13, from Fig. 4c and Fig. 6. The time-window split books the first wave's depletion to the second. |
| P2 (part): haulier and warehouse output is not tied to the shipments carried; the implied 10–20 % weekly falls in power and haulage should show in generation and toll data | yes (absent link); data check external | Methods pp. 8–9 has no such link. The sizes are the referees' arithmetic. |
| P2 (part): fairway +20 cm clears every dry-bulk closure yet adds 2 points over the 40-cm tank floor, so the loss is liquid bulk | yes | p. 6 gives 41 % vs 39 %; Fig. 2 has the gauges and the 30-cm floor. The reference (NS5, A14) reads the same pair the other way, as distinct levers. |
| P7 (part): a freight bill of €0.2–0.4 bn, about the size of the goods-sector loss | partly | The 68 Mt (p. 9) and the Fig. 2 multipliers are in the text. The €15–25/t base rate is not. |
| P9 (part): "pooling halves the loss" compares a calibrated with an uncalibrated model | yes | pp. 5 and 10: the no-pooling run is a sensitivity at ×2. The reference (A04) corrects only the arithmetic. |
| P9 (part): the fairway offset lifts the Kaub gauge that sets surcharges on every reach, while the project covers the Middle Rhine only | yes for the rule | pp. 9–10. The project's extent is outside knowledge. |
| P9 (part): the outlook-triggered stock and reserve rule is recommended but not simulated | yes | pp. 6–7 against the counterfactual list on p. 10. |
| Minor: the Fig. 5 lever runs end at week 31, the base at week 39 | figure only | Fig. 5, plus 19 + 20 weeks on p. 9. |
| Minor: "across the whole country" (p. 5) and "spreads the shortfall nationally" (p. 7) vs the Fig. 3 map concentrated in the south | yes (text and Fig. 3) | Not in the reference. Its F5 note makes a different point. |
| Minor: number-word mismatches | yes | "Record twice" (p. 1) vs "no lower" (p. 4). "Five times" (p. 4) vs Fig. 2 at about 3.2×. "More than doubles" is in fact 2.16 vs 0.54. "Five adaptations" vs six bars. Commerzbank (Fig. 4c) is unreferenced. |

## Reading
Leakage note, copied from reference_points.md: "The panel's common instructions (`studies/review_panel/referee_common.md`)
were written on 5 Nov 2026 by an assistant that had read this review's outline and the project's history. Two of its
generic checks, "like-for-like comparisons" and "finding or assumption", are standard referee practice but correspond to
EC1 and OR1: recall on those two points is prompted, not blind. Two example phrases that pointed at OR1 and OR3 were
removed from the instructions before the run. The referee briefs name the expertise (methods, transport, economics,
editor), which mirrors the reference review's four perspectives."

The panel recovers every critical point and every point the authors confirmed, and touches all 26. What it finds is what
the manuscript's own text, numbers and figures expose: rules that settle a result in advance (OR1, OR2, EC4), estimand
and quantity mismatches (EC1, NS7, EC3), internal inconsistencies (NS5), the draft state (G3) and an untested mechanism
(NS4). For NS4 its proposed test is the run the authors actually made. What it misses are sub-points that need sources
or material outside the bundle, and framing-level asks:
- the content of the IHK survey (EC3);
- Acclimate's supplier reallocation (G1);
- the F2 modal-split residuals (OR4: the SI figure was absent);
- the selection bias in delivered prices (EC4: three panel members endorse the median instead);
- the sign of the backlog recursion (EC5);
- Switzerland counted in "EU" (EC8);
- environmental trade-offs (NS6);
- fairway ≠ tank floor (NS5: R2 praises the equivalence);
- agent resolution (OR5);
- restating the four contrasts as falsifiable propositions (G2).

Four limits bound the result.
- **Shared false alarm.** The panel repeats the reference's one known false alarm (NS3, daily vs weekly < 1 %), and the editor puts it on the action list. The panel does not filter plausible but immaterial checks.
- **Not a blind comparison.** Recall on OR1 and EC1 is prompted. The reference is itself one AI's four passes over the same draft, so part of the agreement is two readers converging on what the text exposes.
- **"Confirmed" covers whole points.** For EC6, the authors' recorded fix (the construction stock rule behind the real-estate loss) is named by neither review.
- **The synthesis loses detail at the margins.** OR6 is raised by three referees but dropped. EC5 survives as one minor inconsistency. OR4's overclaim survives only as a check inside P2. The panel adds no consolidated point beyond the reference; its own contribution is sharper sub-findings and concrete pass/fail tests.

Verdict: on this draft the panel can be trusted to surface the text-visible, high-severity problems (9/9 critical, 7/7
confirmed). It cannot be trusted to reject false alarms or to catch source-dependent and framing-level points. Read the
four reports, not only the synthesis.
