# Nature Portfolio reporting summary: drafted answers (7 November 2026)

The reporting summary is required for "life sciences, behavioural & social sciences and ecology, evolution &
environmental sciences" research articles and is "made available to editors and reviewers during manuscript
assessment" and published with the paper (Nature Portfolio reporting standards, read 7 November 2026). Whether the
editor asks for it on an economic model of a climate hazard is their call; the answers below let the form be filled
in a few minutes if they do (Adobe Reader form: https://www.nature.com/documents/nr-reporting-summary.pdf; a flat
reference copy is linked from the policy page). The form's field names are in bold; the paper's wording is to be
kept consistent with Methods.

## Statistics

**For all statistical analyses, confirm that the following items are present...** Not applicable to most items: the
paper reports simulation results, not hypothesis tests on samples. Fill as follows.
- Exact sample size (n): the sample is the set of eleven supplier–buyer networks (seeds) per scenario; the headline is
  their mean with standard deviation and range (Methods, "Economic layer"; Fig. 2d).
- Statement on whether measurements were taken from distinct samples or repeatedly: distinct network draws, each run
  once (the model is deterministic given its seed).
- Statistical tests: none (no inferential test is made; the comparison with the 2018 benchmark is a check against the
  benchmark's published one-standard-deviation and 95 % bands, built by a Monte Carlo over the regression
  coefficients, Methods "Calibration, selection and validation").
- Description of effect sizes, confidence intervals, variation: means, standard deviations and ranges across the
  eleven networks; the benchmark's 16th–84th and 2.5th–97.5th percentile bands.
- Multiple comparisons, Bayesian analysis, hierarchical models: not applicable.

## Software and code

**Data collection.** Public data were downloaded with the study's scripts (Python 3.10; `onboarding/scripts/` and
`studies/rhine2026/` of the repository): PEGELONLINE and BfG gauge data (`fetch_kaub.py`), OECD ICIO 2025, Eurostat
regional accounts, TENtec (TEN-T network), Global Energy Monitor and Climate TRACE facility trackers, SPAM 2020,
Bundesbank balance-sheet statistics. No instrument software.

**Data analysis.** DisruptSC v2 (Python 3.10; GPL-3.0; https://github.com/ccolon/disrupt-sc, the version of the runs recorded in
`studies/rhine2026/cluster/batch_20261111.md`; release tag and Zenodo DOI to be added), with NumPy, pandas, GeoPandas,
NetworkX and Matplotlib; the analysis and figure scripts of `studies/rhine2026`. State the exact versions from the
environment file at submission (`conda list` of the `dsc` environment).

## Data

**Policy information about availability of data.** Paste the manuscript's Data availability statement. Add: the
scope data package (agents, network, tables, scenario files) and every run table are deposited on Zenodo [DOI], the
third-party inputs are listed with their access conditions (OECD ICIO: free with registration; Eurostat, TENtec,
PEGELONLINE, BfG: open; Global Energy Monitor, Climate TRACE, SPAM 2020: open with attribution; Bundesbank statistics:
open publication).

## Field-specific reporting

Tick **Behavioural & social sciences** (an economic model) unless the editor assigns **Ecological, evolutionary &
environmental sciences**; the answers are the same in substance.

**Study description.** Quantitative modelling study: a spatial agent-based model of the supply chains of 28 European
economies on the trans-European transport network, run on two historical low-water seasons of the Rhine (2018, 2026)
and on counterfactual and adaptation scenarios; outcomes are value-added and consumption losses by week, sector,
region and country.

**Research sample.** No human or biological sample. The economic data are the 2022 OECD inter-country input–output
table (28 economies, 50 sectors), disaggregated into [NFirms] firm agents at plant and employment locations; the
hydrological data are the daily Kaub gauge records of 2018 and 2026.

**Sampling strategy.** The supplier–buyer network is a seeded random draw with gravity weights; eleven draws are used
(the reference network and ten further seeds), a number set by the computing budget (about three hours per run on one
core) and sufficient for the spread to be reported as mean, standard deviation and range; no power calculation.

**Data collection.** Public statistical and geospatial sources downloaded by script between September and November
2026 (dates in Supplementary Section S1 and in the provenance files next to each data set); no field data.

**Timing.** Simulated weeks: 22 June to 23 November 2026 plus 20 recovery weeks; 16 July to 16 December 2018 plus 20
recovery weeks. The model and its parameters were fixed on 2 November 2026. The 2026 runs of 11 November use the Kaub
gauge as observed to 10 November 2026; the last three weeks of the profile rest on the forecasts of the Federal
Institute of Hydrology of 9 and 11 November and are replaced by the observed record at revision.

**Data exclusions.** None of the economic data; in the transport network, edges outside the EU-27 and Switzerland
are kept only as sea lanes and gateway connectors (Supplementary Section S1). Pre-established.

**Non-participation.** Not applicable.

**Randomization.** The seed of the network draw is the only random element; the reference seed was fixed before any
run of the study and not selected on the results (Methods, "Economic layer").

**Reproducibility.** All runs are deterministic given the seed and the recorded inputs (`run_fingerprint.json` in
every run folder); the paper's 128 runs are listed in `additional_data/runs_20261111.csv` with their job lists; regeneration of
every number and table of the manuscript is scripted (`make_numbers.py`, `si_tables.py`, `paper_gate.py --regen`).

**Blinding.** Not applicable (no human raters). The test on the production index is pre-specified: the scoring protocol
was fixed on 9 October 2026 and the model on 2 November, before the indices of October to December 2026 were
published; the index of September, published on 6 November, entered no choice (Methods, "Prospective test").

**Did the study involve field work?** No.

## Reporting for specific materials, systems and methods

Tick "not involved" for every item (antibodies, cell lines, palaeontology, animals, human participants, clinical
data, dual-use research, plants, ChIP-seq, flow cytometry, MRI).
