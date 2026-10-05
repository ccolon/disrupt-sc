# Response to the review of 5 October 2026 (ChatGPT, four perspectives), on Overleaf commit daa869b

Record of what the review found, what was verified in the study's own outputs, and what was done. The review's
numbered points are kept (OR = operations research, NS = natural science, E = economics, G = general, C = the
corrections table). "Done" refers to the Overleaf commits of 6 October 2026 and the code commits of the same day;
"batch" refers to the runs of `cluster/jobs_20261006_rev.txt`, which fill the `\todo{rev batch}` markers.

## Confirmed in our data and corrected

| Point | Finding | Disposition |
|---|---|---|
| E2 / C02 | The model's industrial integral weighted months by run weeks over 4.345; the record's was a plain sum. Not the same quantity. | One rule for both (months = mean of their days, integral = plain sum): `matched_estimand_2018.py`; every path, the ladder, the ensemble and the SI table recomputed. Reference draw 4.98, ensemble 3.59 +/- 1.90. Done. |
| E1 / C01 | The record applied the two coefficients as level effects of the days; the published specification is in changes with an autoregressive term, and its dynamic counterfactual peaks at 1.5 % as the paper says. | `benchmark_ademmer.py`: the published specification (WP 2155 Table 2, four columns) on the daily low-water days, with a Monte Carlo band on the coefficients. Record 0.99/1.00/1.22/1.55/0.56 = 5.32 percent-months, 16-84 % band 3.59-7.11. Seven of eleven draws in the band, nine in the 95 % band. Done. |
| E4 / C04 | "Most of the loss falls on services" was wrong by the paper's own numbers. | Mutually exclusive groups: A 3.6, B-E 34.2 (D+E 13.4), F 16.2, G-T 46.0 %; "the largest part". The 59 % that cannot catch up is a separate attribute. Done. |
| C05 | "The surcharge moves the containers to rail before the reach saturates" could not be right: no container is ever gate-cut. | Routing-level diagnostic: the surcharge moves bulk with an own-mode alternative off the river before the cut (22.3 bn against 3.8 bn in the constraint-only run). Sentence and SI table (tab:channels). Done. |
| C15 / E6 | The 6 % economy-wide price share was the liquid-bulk share. | 2.8 % value-weighted over all cargo (containers 85 % of the value at 2.4 %); denominators stated. Done. |
| C07 | DB Cargo offered 400 wagons at short notice, up to 500 more later; "900 mobilised" and "200 barge loads" unsupported. | Sentence rewritten; the figures now anchor the bounded-substitution ceilings (50 kt and 140 kt a week). Done; results from the batch. |
| C18 / OR5 | The fleet lever raises the peak week (2.84 to 3.02 % on the reference draw, nine of ten draws). | Reported in Results and the Fig. 7 caption; the weekly series of the lever runs are requested from the cluster (repack with firm data). Done pending diagnosis. |
| C08 / C09 / NS4 | Fourteen weeks observed, one partly, five forecast, three assumed; "last five weeks" and "observed weekly mean below zero" overstated. | The 2026 result is framed as a forecast frozen on 30 September, with a prospective test (Methods paragraph and Table of monthly predictions), the status breakdown everywhere, and the outlook's 25th/75th percentile paths as bounds (batch). Done. |
| C13 / E7 | Runs are 43 and 42 steps; "39 weeks" stale; the tail-decay statement recomputed at the real end. | Done (catch-up 340 to 7 mUSD a week, about a fifth a week; about 1 % of the backlog left). |
| C16 | Which targets the stock lever moves. | Stated: every target below the 90-day coping duration, the input-specific ones included. Done. |
| C19, C10, C12, C20, C22 | Rounding and wording. | Done (C19 moot after E2; C10 "falls to 2 %"; C12 intro design; C20 the construction note's vintage; C22 "the 28 economies"). |
| E3 / C03 / G2 | "No parameter is calibrated" untenable. | Calibration (rail and road costs on the modal split), selection on 2018 (representation, stock level, suppliers) and validation (onset and trough month, ex-ante 2026, prospective 2026) stated apart in the introduction, Results, Discussion and Methods. Done. |
| OR3 / C14 | Weekly-sequence conventions. | From the code: targets floored at one week (trade and hospitality hold 7 days, not 5), receipts after production, consumption bounded by availability, no negative stocks or orders, orders recomputed weekly, refill gap over 30 days. Written in Methods; the undisturbed stationarity run is pending (laptop). |
| NS3 | The fairway lever is a global gauge proxy. | Stated; the local-reach variant (`--gauge-offset-scope kaub`) in the batch. |
| NS1 | The loading table mixes evidence types; the 15 cm and 25 cm rows both cited one KBN count. | Source ledger (Table S-loading rebuilt with nature, source, measures, transformation). The count belongs near 12 cm and sits above the table's 0.12: recorded as a discrepancy, the table conservative there; the floor sensitivity (0.02, 0.10) in the batch. **Decision pending: keep the table as built or rebuild it on the ledger (full rerun).** |
| G3 | Figures. | Kaub labelled with a corridor inset (Fig. 1); panels a-d and the last observed week (Fig. 2); signed interaction (Fig. 7 waves); both sector classifications and a point plot for countries (Fig. 5); the validation figure on the rebuilt record. Done. |
| G1 | Novelty claim too broad. | Bounded to the combination of features; the earlier DisruptSC study's transport-duration result acknowledged. Done. |
| E5 | The lower bound was the authors' own statement. | Reworded as the model's quantification of the omitted part, conditional on its propagation rules. Done. |
| E8 | Efficacy, not an investment ordering. | Stated; the inventory-per-loss comparison added; break-even outside the paper. Done. |
| G4 | Reproducibility. | The cross-machine claim withdrawn (same-machine, same-cache reproducibility; provenance across machines). Code availability and the reviewer package remain for the submission step. |

## Not a misreading but overstated by the reviewer

- C06: Methods was right (the fleet increment is 15 to 55 cm); the "every gauge" sentences in Results and Discussion were leftovers and are rewritten.
- NS1 on the 25 cm row: the two rows cite one count; the ledger assigns it to the gauge it measured.
- OR2: the threshold table is read correctly; it is why the bounded substitution is run.

## Sensitivities run in the batch of 6 October (`jobs_20261006_rev.txt`)

headroom 10 and 25 % (OR1); bounded substitution by rail, 50 and 140 kt a week, both events (OR2); refill time 15 and
60 days (OR4); the floor below 5 cm at 0.02 and 0.10 (NS1); the fairway on the Kaub reach alone (NS3); the fleet gain
carried to 100 cm (NS2); the power sector's fuel-oil input non-critical and a 45-day coping duration (E4); the
outlook's 25th and 75th percentile paths (NS4). Plus a base run that must reproduce 1.739 % to the digit after the
fingerprint change, and the repack of the lever and seed runs with firm data (fleet peak diagnosis, the prospective
band).

## Left for the submission step

Code availability and the reviewer package (code revision, environment, input manifests, archived forecast vintages,
weekly outputs, figure scripts); the remaining VERIFY notes in the bibliography; the Overleaf compile; the observed
season in the revision after the event.
