# Forecast manifest: the 2026 Rhine low-water forecast, by vintage

The prediction of the paper ("A river that cannot be sailed", Nature Communications submission) is a forecast of the
German value-added loss of the 2026 low-water season, conditional on a Kaub gauge profile. This manifest separates, as
the review of 8 October 2026 asked (point G1), the hydrological information set, the physical parameter tables, the
model version, the completed prediction and its issue date, so that the forecast can be evaluated against the
production statistics of the autumn (Methods, "Prospective test") with its information history known.

## 1. Hydrological information set (unchanged between the two issues)

| Item | File (this folder) | Content |
|---|---|---|
| Kaub profile, vintage of 30 September 2026 | `scenarios/2026.csv` | 23 weekly means from 22 June 2026: 14 weeks observed (PEGELONLINE daily means, raw 15-minute data, to 27 September), the week of 28 September from two observed days and the outlook's median, 5 weeks from the ENS median of the BfG six-week outlook of 28 September (to 8 November), 3 assumed weeks (75, 90, 105 cm) |
| BfG outlook used | `scenarios/bfg_6week_kaub_20260930.csv` | The six-week outlook of 28 September 2026 (ENS median and quantiles), fetched 30 September |
| Stress paths | `scenarios/2026_q25.csv`, `scenarios/2026_q75.csv` | The outlook's 25th and 75th percentile for the forecast weeks, the assumed recovery shifted by the last forecast week's offset (marginal quantiles, not trajectories) |
| Earlier vintage (kept for the forecast evaluation) | `scenarios/2026_vintage0910.csv`, `scenarios/bfg_6week_kaub_20260907.csv` | Observations to 10 September, the outlook of 7 September, assumed values after |
| 2018 profile (selection) | `scenarios/2018.csv`, `scenarios/kaub_daily_2018.csv` | BfG daily record, weekly means 16 July to 16 December 2018 |

Observed weeks will replace the forecast and assumed weeks in the revision after the event; the profile file carries
a `status` column (observed / partly observed / forecast / assumption) per week.

## 2. Physical parameter tables

| Item | File | Vintage |
|---|---|---|
| Loading table, version 1 | `scenarios/draught_table_v1.csv` | Used by every run to 5 October 2026 (the batch of 30 September) |
| Loading table, rebuilt on its source ledger | `scenarios/draught_table.csv`, ledger `scenarios/draught_table_ledger.csv` | Rebuilt 6 October 2026 (`build_draught_variants.py --rebuild`; the KBN count of the week to 13 August moved from the 25 cm row to the gauge it was observed at; 0.24 at 15 cm, 0.28 at 25, 0.30 at 30, 0.08 below 5 cm; unchanged from 55 cm up). Used by every run of the batches of 7 October |
| Variants | `scenarios/draught_table_{low,high,floor04,floor16,lowwater,lowwater_wide}.csv` | Shortfall ×1.15 / ×0.85, the floor below 5 cm at 0.04 / 0.16, the low-water fleet (+0.10 at 15–55 cm) and its wide variant (to 120 cm) |
| Capacities | `scenarios/rhine_capacities_anchored.csv` (+ `_h10`, `_h25`) | Baseline flow at full loading plus 2 % headroom (10 and 25 % in the sensitivity) |
| Stock targets, criticality, rates | `config/user_defined_EU.yaml`, `additional_data/input_criticality.csv`, `additional_data/inventory_targets_by_buyer.yaml` | Unchanged since the batch of 30 September |

## 3. Model version, run lists and completed predictions

| Issue | Code commit (disrupt-sc) | Run lists | Prediction (German loss, % of a quarter; reference draw) | Issue date (Overleaf commit) |
|---|---|---|---|---|
| First issue, 30 September 2026 | `f9bc2dd` (29 Sep: the lists and the profile of 30 Sep; batch read in `36fb2c0`) | `cluster/jobs_20260930_main.txt`, `cluster/jobs_20260930_paired.txt` (96 runs; results `additional_data/compare_runs_batch_jobs_20260930_*.csv`) | **1.74** (`2026_s30_base`; peak 2.84 % of a week in run week 17; 28 economies 18.9 bn USD); loading table v1 | 30 September 2026, Overleaf `10d629e` (rewrite on the batch of 30 Sep), `b34a1ef` (SI) |
| Reissue, 7 October 2026 | `a0ca0d2` (5 Oct: the loading table rebuilt, the lists of 7 Oct), `13a8cc4` (bounded rail substitution, a sensitivity only), `0c999bc` (7 Oct: the ladder list, batch read), `d576bc1` | `cluster/jobs_20261007_{main,paired,rev,ladder}.txt` (115 runs; results `additional_data/compare_runs_batch_jobs_20261007_*.csv`) | **1.54** (`2026_s07_base`; peak 2.62 in week 17; 16.9 bn); eleven draws 1.30 ± 0.37; monthly industrial path Jul 0.5 / Aug 2.5 / Sep 1.7 / Oct 2.7 / Nov −0.3 / Dec −1.6 (`tables/prospective.tex`); sectoral signatures `tables/si_prospective_sectors.tex` | 7 October 2026, Overleaf `cc34ca7` (batch of 7 Oct written in), `d1e453e` (ladder); text revised 9 October (`17b3aa4`), numbers unchanged |

Both issues use the same hydrological information set (section 1) and the same economy (OECD ICIO 2025, 2022 tables).
The difference between them is the loading table (section 2) and the cache rebuild that the fingerprint change of
5 October (`inventory_restoration_time` moved out of the agents stage) required; the run fingerprints
(`run_fingerprint.json` in every run folder) record every input hash. No production statistic of the 2026 season
entered either issue.

## 4. Outcome releases known at each issue (Destatis, production in industry)

| Month | Release | Status at the first issue (30 Sep) | Status at the reissue (7 Oct) |
|---|---|---|---|
| July 2026 | 7 September 2026 (−1.1 % on the month) | retrospective (released, not used) | retrospective |
| August 2026 | 7 October 2026 (+2.0 % on the month) | prospective | nowcast (released the day of the batch, not used) |
| September 2026 | first week of November 2026 (expected) | prospective | prospective |
| October 2026 | second week of December 2026 (expected) | prospective | prospective |
| November 2026 | January 2027 (expected) | prospective | prospective |

The month-on-month headlines are not the quantity the forecast predicts (the shortfall against a no-event
counterfactual); the evaluation protocol (Methods) scores the index relative to its January–June 2026 mean.

## 5. Evaluation protocol (fixed 9 October 2026, Methods "Prospective test")

Index: the Destatis production index of industry (sections B to D, seasonally and calendar adjusted), first release
of each month. Comparator: the mean of the index over January to June 2026. Months scored: September to December 2026.
Score: mean absolute error, in index points, of the model's monthly shortfall on the reference draw, next to the
published specification of Ademmer et al. on the realised low-water days and a zero path; the forecast is judged wrong
if its error exceeds the zero path's. The hydrological part of the error is separated by the rerun on observed gauges.
Sectoral signatures: `tables/si_prospective_sectors.tex` (refining and chemicals about 15 and 10 % below baseline in
August and October, cement and construction deepest in October, every river sector above baseline in December).

## 6. How to reproduce an issue

```
python studies/rhine2026/run_rhine.py --profile 2026 --constraint-mode on --closure-threshold -1 ...   # as in the job list
python studies/rhine2026/compare_runs.py ...                                                           # the batch tables
python studies/rhine2026/make_numbers.py --tag s07 --lists 20261007                                     # numbers.tex
python studies/rhine2026/si_tables.py                                                                   # the SI tables
```

The exact command lines are in the job lists; the caches are rebuilt from the fingerprints on another machine
(reproducible to the last digit on the same machine; provenance of every input across machines).
