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
