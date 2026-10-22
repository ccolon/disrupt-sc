# Response to the review of 8 October 2026 (ChatGPT, four perspectives), on Overleaf commit d1e453e

Record of what the review found, what was verified in the study's own outputs, and what was done. The review's
numbered points are kept (OR = operations research, NS = natural science, E = economics, G = general; the
"confirmed corrections" table of its section 5 is referred to by row). "Done" refers to the Overleaf commits of
9 October 2026 and the code commits of the same day. The checks are in `review_checks_20261008.py`, which writes
`additional_data/review_checks_20261008.txt` (lever ordering by draw, the value-added-weighted industrial series,
the sector shares of the sensitivity runs, the gate ledger by horizon, the forecast by vintage).

## Confirmed in our data and corrected

| Point | Finding | Disposition |
|---|---|---|
| E2, rows 1–3 | The priced river peaks in November at every stock level (2.83 / 1.67 / 1.08 against the record's 1.55); the text said it misses the November trough. At ×2 it undershoots. | True (Table S-representations). The discrimination is now the onset (mid-October against August) and the December tail (half of the November loss kept, against a third in the record); "overshoot" qualified to the evidence value; the onset and shape are called selection evidence. Results, Methods and S6 rewritten. Done. |
| G1, row 4 | "Frozen on 30 September" cannot describe a result whose loading table was rebuilt on 6 October and whose runs are of 7 October. | True. The forecast is now dated by its information: river information of 30 September (observations to 29 September, outlook of 28 September); first issued 30 September on the earlier table at 1.74 % of a quarter (`2026_s30_base`); reissued 7 October on the rebuilt table at 1.54 %; no production statistic used in either. Months classified by their release date (July retrospective, August a nowcast, September–December prospective). Manifest `forecast_manifest.md`. Abstract, Results, Methods, table captions. Done. |
| G3, row 5 | SI S8 said the bounded rail scenario was not run and cited 900 wagons. | Stale. S8 rewritten on the completed runs: the two ceilings and what each is (a transparent scenario from the 400-wagon announcement; an illustrative ceiling at the scale of the Appendix B response, not an operational one), eligibility, allocation, binding, the split by cargo class (liquid bulk three fifths of the relief value), the 2018 integrals. Done. |
| OR2, row 6 | "The order holds on every draw" is contradicted by the run table. | True: stocks beat the fairway in 7 of 10 draws, the fairway in 3; the fleet is last in 9 of 10 and beats the targeted stocks in 1; the targeted week is behind both in 10 of 10; the package beats every single lever in 10 of 10. The Discussion and the introduction now say so, and the ordering is called conditional on the substitution rule. Done. |
| Row 7 | The adaptation caption said the fleet raises the reference peak. | On the reference draw the peak falls 2.62 → 2.45 % of a week; it rises on 6 of 10 further draws. Caption corrected with macros. Done. |
| Row 8 | Main text printed 21 % / 35 % worst-week deliveries against 24 / 37 in the SI and numbers. | Literal numbers of an earlier batch; replaced by the macros. Done. |
| Row 9 | "Two suppliers give a third" of the record: 1.0 / 5.3 is a fifth. | Done. |
| Row 10 | "Both loading variants miss the record on one side": the raised shortfall (6.1) is inside the band. | Reworded: the variants bracket the central estimate, the raised one inside the band, the lowered one below. Done. |
| Rows 11, 12, 13, 15 | Fragments of the previous version left after decimal points (main 145 "1.7 %", main 151 "1.2–2.2", SI S4 channels and flat paragraph). | A patch regex had stopped at the decimal point. Removed; a lint for "word.digit" fragments added to the checks. Done. |
| Row 14 (S3) | Lower rerouting in the trough weeks was attributed to containers having left the river, although containers never use the gated reaches. | Replaced by the measured shares: 11–24 % of the cut finds another route in the profile weeks, 23 % at the margins and 12 % in the troughs because the surcharge has moved the bulk with an own-mode alternative off the river before the gate; two thirds in the recovery weeks. Done. |
| OR4, row 16 | Gate table (23 weeks: 13.4 / 1.8 / 11.6 Mt) against the flat paragraph (16.0 / 3.5 / 12.5). | Different horizons: the table covers the 23 profile weeks; the gate also cuts in 14 recovery weeks (2.6 / 1.7 / 0.9 Mt), when the refill traffic exceeds the reopened capacity; season total 16.0 / 3.5 / 12.5. The caption computes both; the counting convention (totals over rounds; a share re-sent then cut again counts in both) is stated. Done. |
| OR3, rows 17, 18 | Wave caption, figure and Discussion said "same tonnage"; the design equalises the cumulated capacity shortfall; the figure printed 1.41 against the table's 1.42. | Wording corrected everywhere; the figure now annotates the run table's column; the flat annotation moved inside the axes. Done. |
| Row 19 | "96 runs", "batch of 30 September" against 115 rows and October identifiers. | 115 runs in four job lists of 7 October; the run-table caption explains the prefixes (s07, rev, wave07, seedN, invNNN); earlier batches named. Done. |
| Row 20 | S3 "every run uses the rebuilt table" against the old-table runs of S6. | Qualified: every run of the batches of 7 October; the priced-river runs of S6 and Fig. 2 are on the earlier table. S6 also states why the rebuild would not change the priced river's late onset (it changed gauges below 40 cm, four weeks of 2018; closures unchanged). Done. |
| Row 21 | Labels "loading table ×0.85 / ×1.15" versus the shortfall multiplier of Methods. | Figure and table labels now say "shortfall ×". Done. |
| NS3, row 22 | The marginal-quantile paths are stress paths, not bounds. | "Stress paths" in Methods, Results and S3; "bound" removed. Done. |
| Row 23 | "Cuts the loss by −29 %". | `\RevRestFifteenAbs` (29). Done. |
| E1 | The index aggregates sectoral indices with value-added weights; the model's series is production-weighted. | Re-aggregated as the index is (sector shortfall rates weighted by sector value added): 4.6 against 4.6 percent-months in 2018 (no month differs by more than 0.2 points), 5.3 against 5.6 in 2026 (the rebound months deepen). Stated in Methods with the series assumption (the working paper names only "industrial production of the Federal Statistical Office"; taken as the production index of industry, B–D; E carries 4 % of the B–E weight). Done, with the caveat that the exact series of the working paper is not identified. |
| E3 | Report the service and industry shares in the coping and fuel runs. | At 45 days: services 52 % (47 in the reference run), total/industry 3.1 (2.9). Fuel-oil non-critical: utilities 1 % (14), services 54 %, ratio 3.9. Rail 140 kt: construction's share 1 % (14). In S4. Done. |
| OR4 | Non-storable coping and the supplier-weight update need their equations. | Stated: the coping duration is the same state variable and equations as a goods stock with a 90-day target (a reduced form, not a warehouse); the satisfaction EMA (weight ½, started at one, unchanged without an order), renormalised over the pool; the production target of week t is the orders placed in week t−1. Done. |
| NS2 | Fleet normalisation. | Stated: the lever holds the normal-water tonnage and the vessel count fixed and raises the share that passes at a gauge; the increment tapers to zero at 10 and 78 cm (wide variant: 78/100/120); the full-loading capacity of the vessel cited (5,100 t) is not modelled; tanker evidence applied to dry bulk. "A specified loading improvement, not an assessment of the technology." Done. |
| E4 | The zero price-channel result is a property of the closure. | Discussion: the result is that stock depletion dominates under the model's demand and pricing rules, not that freight bills are unimportant; the real resources a surcharge pays for are not counted. Done. |
| E5 | 1.54 % of a quarter is a size, not a quarterly growth effect; stocks within the season versus pre-positioning. | Both stated (Results headline; Discussion: the lever is pre-positioned, a rule acting on the first outlook was not run). Done. |
| G2 | The prospective table is not an evaluation protocol. | Protocol fixed in Methods: index (Destatis production index of industry, B–D, seasonally and calendar adjusted, first releases), comparator (mean of January–June 2026, with the published specification scored alongside as a benchmark carrying the same limitation), months (September–December 2026), score (mean absolute error against the zero path; wrong if worse than zero), separation of the hydrological error by the rerun on observed gauges; sectoral signatures pre-specified in Table S-prospective-sectors (refining and chemicals in August and October, cement and construction in October, every river sector above baseline in December). Draft for the authors' approval. |
| OR1 | The ceilings are assumptions; say what each is. | Done in S8 and Methods (above). The abstract names the rule as restrictive. |
| G4 | Figures. | The wave annotation moved into the axes; the validation legend moved off the two-supplier cross; labels corrected. The suggestion to promote the rail and coping sensitivities into the main uncertainty figure is open (see below). |

## Checked and found overstated, or answered without a change

| Point | Review | Finding |
|---|---|---|
| E2 | The ensemble range 0.2–5.1 lies entirely below the record's 5.3; overlap with the band does not establish an unbiased ensemble. | True as a statement of fact and now plainly in the text (the band's count "describes the ensemble rather than tests it"). The reference draw was fixed beforehand (Methods). No change in the numbers. |
| NS3 | A below-1 % difference in withheld tonnage (daily versus weekly) does not bound the loss difference. | True; the S3 sentence already restricts the claim to the transport metric. No change. |
| OR4 | Order-independence of the gate should be supported by a permutation check. | It is a property of the pro-rata rule (every offered shipment is cut by the same factor); stated as such, not checked by permutation. |
| G5 | Reviewable code and data. | Open (the authors' decision on the release; see below). |
| NS5 | Title. | Open (the authors' decision). |

## Needing the authors' decision (new runs or a release)

| Point | Request | Cost | Note |
|---|---|---|---|
| OR2 | A small crossed comparison: the leading levers (stocks +7 days, fairway +20 cm) under the finite-rail case (50 kt). | 3–4 runs of ~3 h on the cluster (`rail50` × {stock7, deep20, package}). | Without it the ordering is stated as conditional on the substitution rule, which the text now does. |
| OR3 | The gap experiment at another refill time (15 days), to show the memory depends on the replenishment rule. | 2–3 runs (gap 2 and gap 4 at rest15, plus rest15's A and B alone if the interaction is wanted). | The text now calls the four-week memory conditional on the 30-day rule. |
| G2 / E2 | Coefficient covariance of the benchmark for a proper band. | Not in our hands (the working paper does not publish it); the band is labelled indicative. | Could ask the authors of the working paper. |
| G5 | A tagged code version, a reviewer archive, per-run series, figure source data, the prediction-vintage manifest. | A release and a Zenodo (or confidential) deposit; the manifest is written. | Code availability still a `\todo`. |
| G4 | Promote the rail and coping sensitivities into the main uncertainty figure. | A figure change only. | |
| NS5 | Title centred on constrained freight capacity rather than "a river that cannot be sailed". | Wording. | |
| OR5 / E3 | Validate one chain (refined products, chemicals or building materials) on exposure evidence independent of the industrial aggregate; a corridor- and sector-matched survey comparison. | Data work, no runs. | The sectoral signature table makes the chains testable in November. |

## What the review got right about the numbers (no action)

The eleven-draw mean and standard deviation (1.30 ± 0.37), the 2018 dynamic benchmark (0.99 / 1.00 / 1.22 / 1.55 / 0.56 = 5.32), the monthly integrals of the representation table, the 115 run rows, the gate identities and the 37 cited keys were all reproduced by the review from the submitted artefacts; we reproduced its pairwise lever rankings and gate totals from the run tables (`review_checks_20261008.txt`).

## Addendum, 12 October 2026: the two experiments the authors approved (batch of 9 October, `cluster/jobs_20261009_cross.txt`)

| Point | Result | Disposition |
|---|---|---|
| OR2 | The four single levers under the 50 kt rail ceiling (base `2026_rev_rail50`, 1.23 % of a quarter): stocks avoid 48 % (45 without rail), fairway 42 (38), targeted stocks 28 (22), fleet 20 (17), in the same order. The relief serves the bulk the levers do not reach; the two are nearly additive. | Results (levers), Discussion (ordering), Methods (counterfactuals), SI S4 + Table S-cross, run table. Done. |
| OR3 | The gap experiment at a 15-day refill time: A 0.44 + B 0.66 = 1.10 apart, 1.10 in sequence (+0 % against +12 % at 30 days); with 2 and 4 weeks of normal water the sequence costs 10 and 13 % less than the sum (at 30 days +6 and +2 %), because the buyers hit by the first wave have refilled and the plants working off their backlog produce above baseline when the second arrives. The memory the gap experiment measures is the refill time of the stock rule. | Introduction, Discussion (calendar paragraph), Fig. 3b (teal series), Methods, SI S4 + Table S-cross. Done. |

Reader: `read_batch_20261009_cross.py` (writes `additional_data/batch_20261009_cross_summary.txt`); macros `\Cross*`, `\Wave*Rest` in numbers.tex (270 macros). Title changed on 9 October to "Logistics under drought: how the Rhine low water of 2026 propagates through Europe's supply chains" (NS5); the rules of the revision promoted into Fig. 8 (G4). Code release and reviewer archive remain open.


# Response to the review of 12 October 2026 (ChatGPT, four perspectives), on Overleaf commit 2db49a0

## Confirmed in our data and corrected

| Point | Finding | Disposition |
|---|---|---|
| E1 | The loss accounting mapped the scope-wide sector value-added/output ratio (`mrio_by_sector.csv`, summed over the 28 economies) onto every firm; the estimand is the firm's own country-sector ratio (its `target_margin`). For Germany the power sector's ratio is 0.36 against 0.27 scope-wide. | Confirmed in `compare_runs.py` and reproduced: the reference run gives 15,651 mUSD, 1.638 % of a quarter (14,762 / 1.545 before), 2018 0.980 (0.935), the 30 September issue 1.847 (1.74). New module `va_shares.py` (country-sector ratios from the run's firm table, else the study table); every script that aggregated losses switched (compare_runs, analyze_scenario, matched_estimand, the batch readers, review_checks, two plot scripts); `export.py` now writes `mrio_by_region_sector.csv`. The batch tables are recomputed on the cluster from the stored outputs (`cluster/recompare_20261012.sh`), after which every number, table and figure regenerates. Manifest section 7 keeps the forecasts as issued. |
| E2 | The index check weighted German sector rates by scope-wide sector value added; the production index uses German weights, sections B to D. | The record comparison now uses the production-index measure (German MRIO value-added weights, B to D, in `matched_estimand_2018`): 2018 reference 3.9 percent-months (4.6 production-weighted; record 5.3, band 3.6 to 7.1), raised-shortfall table 5.2, lowered 2.7, ensemble about 2.7 +/- 1.4 with 4 of 11 in the band; 2026 forecast 4.5 (5.6). The claim that the table as built is the closest is withdrawn: the record's central estimate lies between the table as built and its raised variant; the table is kept because the ledger gives it, not because it fits best. The prospective table reports the scored measure (and the production-weighted row for continuity). |
| E3 | The protocol scored a different target (index relative to its pre-event mean) from the causal loss; no equation; the comparator received realised gauges. | Score defined (s_m = 100 (1 - I_m / mean over January to June); mean absolute difference over September to December against the zero path); two comparisons on common information (forecasts as issued; conditional responses on realised gauges); stated as predictive performance on a fixed-baseline activity proxy, not a validation of the causal loss. |
| OR4 | Methods gave a uniform freight share 0.2; the implementation uses the supplying agent's MRIO transport share (0 to 0.6, 0.2 as fallback); the own-price rule is a unit-cost pass-through with the input intensity and the equilibrium anchor. | Both rewritten as implemented. |
| OR3 | "Binds in every week" unsupported for 140 kt; the ceilings' derivation repeated in three places. | Week-by-week table (Table S-railweeks, from the logs): 50 kt binds in 23 of 23 profile weeks of 2026 and 21 of 22 of 2018 (5 and 3 recovery weeks); 140 kt in 22 and 17 profile weeks (no recovery week). Text: "nearly every profile week" / "most"; the 140 kt case called an illustrative ceiling at the scale of the econometric response in the Results too. |
| OR1 | A larger share of a smaller base is not additivity; report absolute benefits and interactions. | Macros for the absolute avoided losses (lever alone, rail alone, lever on top of rail) and the overlap (the two together avoid X % less than the sum): stocks about 11 %, fairway 7, fleet 2, targeted 0 on the reference draw; "nearly additive" withdrawn; the ordering stated as reference-draw evidence at one ceiling. |
| OR2 | "The memory is the refill time" over-identifies a parameter. | "Depends on the refill time, jointly with the headroom of the reopened reach and the capacity for catch-up; not a measured time constant" (Discussion, S4, the wave figure's title). |
| G2 | Results line 75 still said timing tests rather than selects; the abstract claimed reproduction; "closest" claims. | Sentence removed; abstract: "selected on the 2018 low water, its monthly path lies within the band of the econometric record"; introduction likewise, with the threefold multiplier called a conditional prediction; "Under the model's demand rules stocks, not freight bills". |
| E4 | Signed calendar-quarter activity against gross event loss; what refilling the virtual service state means. | Macros for the signed Q3/Q4 2026 value-added change against the gross losses (prospective paragraph); the surplus explained as the backlog delivered late, which the accounting still counts as lost for services. |
| NS1 | The 78 cm ledger row claimed bounds from observations of different quantities. | Row relabelled "assumed anchor" with the derivation stated as a reading, not a bound. |
| NS4 | The recovery is generated jointly by the stock rule, capacity and transport headroom. | Stated in the Discussion's calendar paragraph and S4. |
| S3 | "Two bounding profiles". | "Two stress profiles". |
| Prospective tables | B to E production-weighted row (-1.6) against the sectoral table's -1.5. | Both tables now carry the index measure from one function. |
| G4 | Null git SHA in the run fingerprints. | `fingerprint.py` reads `.git/HEAD` when the git binary is absent (the cluster's case); the manifest lists the commits of every batch. Code availability: still the authors' decision. |

## Numbers pending the recompute

The batch tables are recomputed on the cluster (the runs without local firm tables cannot be reaggregated here); until then `numbers.tex` carries the values as issued. The local recompute of the reference runs reproduces the review's figures exactly.


## Numbers after the recompute (cluster recompare of 12 October; Overleaf 2041cd0)

| Quantity | As issued (scope-wide ratios) | Corrected (country-sector ratios) |
|---|---:|---:|
| 2026 forecast, German loss, % of a quarter (reference draw) | 1.54 | 1.64 |
| eleven draws, mean +/- s.d. | 1.30 +/- 0.37 | 1.35 +/- 0.38 (range 0.68 to 1.78) |
| industry part, % of a quarter; share of the loss | 0.54; 35 % | 0.61; 37 % |
| services (G to T) share; construction; utilities (D+E) | 47; 14; 14 % | 44; 16; 17 % |
| EU loss, bn USD | 16.9 | 17.9 |
| 2018 reference; eleven draws | 0.94; 0.80 +/- 0.23 | 0.98; 0.82 +/- 0.24 |
| 2018 industrial integral, percent-months (production-weighted B-E as issued; index measure, German VA weights B-D, corrected); record 5.3, band 3.6 to 7.1 | 4.6 | 3.9 |
| draws inside the record's 16-84 % band; inside the 95 % band | 6 of 11; 9 | 4 of 11; 7 |
| loading table, shortfall x1.15 / x0.85, 2018 integral | 6.1 / 3.2 | 5.2 / 2.7 |
| stock ladder x1.25 / 1.5 / 2 (2018, % of a quarter) | 0.69 / 0.53 / 0.34 | 0.72 / 0.55 / 0.35 |
| levers: stocks / fairway / fleet / targeted / package, % avoided | 45 / 38 / 17 / 22 / 80 | 46 / 39 / 17 / 22 / 80 |
| crossed with rail 50 kt | 48 / 42 / 20 / 28 | 48 / 43 / 20 / 28; overlap with the rail benefit 12 / 8 / 2 / 0 % |
| waves: A + B apart; in sequence; interaction | 1.38; 1.54; +12 % | 1.45; 1.64; +13 % (gap 4: +3 %; at 15 days: +2 %, -9 %, -13 %) |
| flat profile | 1.16 | 1.22 |
| rail 50 kt / 140 kt (2026) | 1.23 / 0.75 | 1.30 / 0.78 |
| 2026 industrial integral on the index measure (record on the same days 6.3) | 5.6 (production-weighted) | 4.5 |
| signed value-added change, Q3 / Q4 2026, % of the quarter (gross 0.80 / 0.88) | - | +0.62 / -0.40 |

The qualitative results are unchanged: the ordering of the levers (stocks ahead of the fairway in 7 of 10 draws, the fleet last in 9 of 10), the sign and decay of the wave interaction, the priced river's late onset, the sector groups' order. What changed in the argument: the 2018 comparison is weaker on the index measure (3.9 against 5.3, four of eleven draws in the band), the claim that the table as built fits best is withdrawn, and the abstract says "lies within the band of the econometric record" instead of "reproduces".


## 20 October: the author's revision applied (Overleaf 201c872, 54 inline CC notes)

The plan validated in the chat (A to E) was applied on top of the author's text, after two clarifications:

- No waterway bypass of Kaub exists in the network (the rhine_* chain is the only water path between the Lower and the Upper Rhine). The only bypass is 89 km of rail between Koblenz and Mainz (plus two connectors). Under the switching rule a bulk shipment may use it at no penalty only if its normal route already carries a main leg by rail (at least 100 km); 15 % of the Kaub-crossing bulk orders have such a route; at a 500 km threshold 97 % give up. We have no data on the share of the Kaub traffic that travels combined rail-barge, so the text states the bypass as an assumption of the routing and a pair of no-rail runs (line-haul threshold 500 km, 2026 and 2018) bounds its effect: cluster/jobs_20261020_norail.txt, to launch with --independent (switching_costs is outside the cache fingerprint).
- The surcharge: delivered price = supplier price x (1 + transport share x cost change); own price = equilibrium price + unit-cost pass-through; no demand response; no refusal at these surcharges. The extra payments over the 2026 run are 1.1 bn USD across the 28 economies (1.0 bn on deliveries to German buyers), passed down the chain in prices, against 15.7 bn of production loss; the surcharge-only run loses nothing.

What changed in the manuscript: abstract; introduction rewritten (the Rhine valley as the industrial core, the four Rhine states at 48 % of German GDP [vgrdl2025], "only 72 %" of normal rainfall, 25 cm against 1.5 m, the four results); Results: the model subsection with the Pichler criticality citation, the Lower Rhine residual explained, the rail-bypass sentence; the 2018 test with the Bundesbank citation, "benchmark" with its one-standard-deviation band, the selection summarized in one paragraph (details in the new SI S9), the corridor-survey comparison on the survey week; the capacity section retitled "Reduced river capacity, not the surcharge, drives the loss" with the surcharge bill and the placeholder todo for the no-rail runs; who-loses in four paragraphs; adaptation rewritten with the inventory-per-loss figures moved there from Methods; Discussion aligned (inventories, episodes, benchmark, the corridor gap); every Methods line note addressed; SI: S9 (selection on 2018) and S10 (implementation conventions, fleet lever, benchmark reconstruction) added; vocabulary: stocks -> inventories, stock-outs -> shortages, troughs -> episodes, record -> benchmark; references vgrdl2025, bundesbank2025, ebv2025 added. Remaining todos: the marker legend, the no-rail placeholder, code availability.

Corridor firms (new macros, base run 2026_s07_base): in week 7 (3-9 August, the week the DIHK survey of 29 July-4 August closed) 13.5 % of the 370 German firms within 50 km of the Rhine produce below 99 % of baseline and 4.3 % below half of it (survey: 33 % production restrictions, 6 % stops); at the autumn peak (week 17) 23.2 and 18.9 %; over all German firms 8.5 and 12.8 %. The text says "only partly reproduced; the model is on the low side" (an earlier draft said "a few percent", which the numbers do not support).

Code: run_rhine.py takes --line-haul-km and --access-km; make_numbers writes SurchargeBillBn (1.1), SurchargeBillDEUBn (1.0), the Corridor* macros, Abs variants of the 2018 rail macros and the RevNoRail* macros when compare_runs_batch_jobs_20261020_norail.csv exists; si_tables says benchmark and inventory and lists the no-rail rows when their table exists; figures F9 (benchmark, inventory multiplier, legend of panel b moved off the data), F10 (episodes), F4c and F7 (inventories) regenerated. Lint clean (macros, labels, citations, braces). Word counts: abstract 192, introduction 1090, Results 4071, Discussion 1778.

Pending: the no-rail runs; then the compare table fills RevNoRail* and the revision table, and the placeholder todo in the capacity section and the limitation sentence of the Discussion are replaced by the result.


## 21 October: the no-rail runs (jobs_20261020_norail.txt)

Both runs used the 500 km main-leg threshold (parameters.yaml: switching_costs.line_haul_km 500.0; the fingerprint records it), so no bulk shipment has a rail alternative around Kaub. Table: additional_data/compare_runs_batch_jobs_20261020_norail.csv (cluster compare_runs, country-sector value-added ratios).

| Run | German loss, % of a quarter | against the base | peak, % of a week (week) | EU loss, bn USD | bulk rerouted over the run, bn USD | bulk blocked, bn USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026 base | 1.64 | - | 2.82 (17) | 17.9 | 21.8 | 16.8 |
| 2026 no rail | 2.02 | +23 % | 3.01 (17) | 21.7 | 18.0 | 19.4 |
| 2018 base | 0.98 | - | 1.16 (21) | 11.0 | 19.3 | 11.1 |
| 2018 no rail | 1.29 | +32 % | 1.54 (21) | 14.2 | 17.2 | 13.2 |

Reading: the rail bypass that the rule grants to bulk with a rail main leg is worth about a quarter of the 2026 loss and a third of the 2018 loss; the peak weeks do not move. The rerouted bulk that remains in the no-rail runs (18 bn USD) is same-mode rerouting on the surcharged Lower Rhine and elsewhere, not a Kaub bypass; the Kaub bypass is the difference between the two runs (about 4 bn USD of bulk over the 2026 season, a tenth of what the river turns away).

Where it goes: the capacity section of Results (replaces the placeholder todo), the uncertainty paragraph and the caption of the uncertainty figure (the rail group now shows none / 50 / 140 kt), the limitations paragraph of the Discussion, SI S8 (the exception in the rule stated, the pair of runs reported), Table S-revision (two rows, generated). The user asked on the evening of 20 Oct not to update the Overleaf copy, so the text changes are held in review/pending_patch_norail_20261021.py; numbers.tex and the tables were generated into a staging folder only, F8 regenerated in the study folder only. Macros ready: RevNoRail 2.02, RevNoRailAbs 23, RevNoRailyy 1.29, RevNoRailyyAbs 32.


## 22 October: the author's 54 notes of 21 Oct and the seven decisions applied (Overleaf b8a2f06)

Decisions (all agreed on 22 Oct): D1b a container sensitivity pair (jobs_20261022_container.txt, see below); D2 headline numbers on the mean of the eleven supplier-buyer networks (decompositions by sector, country and shipment on the reference network, labelled; the issued forecast series of 7 Oct stays the reference network's and the mean is scored alongside it); D3 the rail baseline unchanged (bulk does not switch; the 140 kt ceiling explained as an over-reading of the all-cargo regression); D4 the delay cost dropped from the main text; D5 the uncertainty figure moved to the SI, flipped; D6 the measured-economy paragraph folded into one sentence of the calibration paragraph; D7 the August-2026 test moved to the 2026 section.

New macros: EnsMeanBn 12.9 (bn USD, mean German loss over the eleven networks), EUlossEnsBn 14.4, DEUnetBn 14.2, LevStockAvg 41, LevDeepAvg 38, LevFleetAvg 17, LevStockTAvg 24, LevPackageAvg 80 (means over the eleven paired networks). The text fractions were checked against them (targeted inventories now "a quarter").

Answers written into the text: the 78 cm low-water mark; the GDP effect at the trough of 2018 (Kiel); the loading curve built without fitting and kept as its sources give it; the catch-up mechanism behind "sequence cheaper than the sum" (B's first weeks after an 8-week gap 71/240/411 mUSD vs 221/390/606 alone) and the 15-day case; the fleet's higher single worst week with a lower total; rail as a sensitivity at two ceilings; every Rhine stretch has a capacity, only Kaub's is cut and only Kaub saturates; road never a bulk main leg by construction (25 t vs 2,000 t); the inventory lever applies to every economy; France's food chain = French farm products of the Rhine plain shipped by barge (cost routing, flagged as an upper reading); 800 t vs about 400 t for a standard vessel (the "80" and S10's "a tenth" were wrong); the transport share undefined only for sector T; poolable products = standardised goods; several agents per region-sector. Vocabulary: supplier-buyer network everywhere. References added: eurostat2025regio, spam2020, gem2025, climatetrace2024, fineprint2022. Containers on the Rhine and the port residuals stated in Results, Methods and SI S2 (the port numbers of the September baseline, flagged; a table on the final baseline awaits the flows export of 2026_s07_full from the cluster). Remaining todos: the marker legend, "container runs pending", "port table pending", code availability.

Figures: Fig. 2 is now one file (F4_event_2026: gauge + share passing on one panel, weekly loss as mean/IQR/range of the eleven networks); validation figure with the model as mean + grey IQR/range, one legend entry, jittered points, readable event labels, "(a)" labels; wave figure without the vertical line, the sum curve visible, plain labels, no value labels, the 15-day sum line dropped; lever figure as one row (bars = means over the eleven networks, no value labels); who-loses: countries first, billions throughout, proper legend, map cropped to the France-Germany-Denmark box; schematic redrawn (one loading-curve box feeding surcharge and capacity; "delivered with the surcharge" and "cut share looks for another route" on one row feeding the buyer; containers may switch, most bulk waits with the asterisk); network map with whiter sea lanes, the inset up-left, a boxed legend top-right, "Firm points". All panel labels in the "(a)" style.

Word counts after the pass: abstract 199, introduction 1,080, Results 4,200, Discussion 1,800 (approx.).

### Flow recalibration tooling (for November; agent work of 22 Oct, in onboarding/scripts/)
- tag_network_attributes.py: tags the 462 waterway edges with a waterway/basin from a gazetteer (disrupt-sc-data/EU/validation/waterways_gazetteer.csv, 67 waterways; all edges tagged, 63 tags; Rhine 66 edges) and the sea-port connectors with the Eurostat port (ports_gazetteer.csv, the 60 largest EU ports; 175 connectors / 78 terminals matched to 58 ports; 257 connectors of smaller ports unmatched); writes tagged copies to EU/Transport/tagged/ (untracked, regenerable) and a report.
- flow_score.py: scores a flows export against ports (Eurostat mar_go_aa), the country modal split (tran_hv_frmod), the NST groups (DE, NL), the Rhine profile, the basins (waterway_targets_2023.csv, 3 rows filled with a source, 19 to fill), and the short-sea share (information only). On the September baseline: mean |log10 error| ports 0.39, country split 0.33, NST 0.24, Rhine 0.20, overall 0.30. Strongest lead: below Tiel the Rhine stream goes to Amsterdam (Amsterdam-Rhine canal 104 Mt/yr, Noordzeekanaal 49) instead of the Waal to Rotterdam (Rotterdam at 0.21x Eurostat, Amsterdam 1.8x, Venice 4.3x); transhipment hubs (Piraeus, Algeciras, Gioia Tauro) cannot match Eurostat because sea-to-sea transhipment is not represented; crude ports fall with the pipeline rule; German waterway tkm 2.0x the Eurostat total, NL 0.57x; deep-sea share of port throughput 72 % vs 41.5 % (intra-EU short sea largely missing).
- Export changes that would help the scoring (November rebuild): tonnes per flow category per edge; origin type on maritime edges (deep-sea gateway / intra-EU); carry the tags by building from Transport/tagged/; one country code per edge on border rivers.

### The container sensitivity pair (jobs_20261022_container.txt)
run_rhine.py takes --container-water-cost (0.022 -> 0.015 USD/tkm) and --container-water-vot (0.35 -> 0.15 USD/t.h); the runs carry --cache-isolation (the costs enter the route fingerprint) and the 2026 run --full-export for the flows file; check the Kaub container tonnage at t = 0 (target ~10 Mt/yr) before reading the loss.
