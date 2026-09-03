# Paper outline — "A spatial supply-chain model of the European Union: the Rhine low-water summer of 2026"

Working title and skeleton (3 Sep 2026). Every figure/table names the model output or
data file it comes from, so the pipeline can produce it without re-deciding.

## 1. Introduction
- Inland waterways carry 5 % of EU inland tonne-km but a third of the bulk feedstock of the
  Rhine industrial belt (chemicals, steel, refining, power, agri-food); the Rhine alone ≈ 150 Mt/yr
  at the Dutch–German border.
- 2018 and 2022 showed the macro footprint of a river that cannot be sailed (Ademmer et al. 2023:
  −1 % industrial production per 30 days of Kaub < 78 cm; ≈ −0.4 % GDP in 2018). 2026 broke the
  record: Kaub 8–11 cm in mid-August, three weeks de facto closed, force majeure across the
  chemical belt (evidence dossiers, §2 and §11 of `evidence/`).
- Gap: existing evaluations are ex post econometrics (national IP) or single-firm accounts; no
  model resolves *which* firms, *through which* transport substitutions, *how far* down the
  supply chain. Contribution: first whole-EU spatial agent-based supply-chain model (28 countries,
  50 sectors, 13k firm points, TEN-T multimodal network with 10k edges), and its application to the
  2026 event with a weekly gauge-driven scenario validated against firm surveys, freight statistics
  and macro estimates.

## 2. Model (DisruptSC v2, EU scope)
- Agents and network: firms placed by plant/employment data (firm-extractor), households at NUTS2,
  external partners at sea/border nodes; OECD ICIO 2022 technical coefficients; commercial links
  with cargo types; TEN-T roads/rail/waterways/maritime + terminal connectors.
- Transport costs and mode choice: per-mode USD/tkm, per-cargo (and per-mode) value of time,
  per-cargo terminal transfer costs; winner-take-all routing per OD pair. Table: calibrated
  parameters (final config).
- Disruption mechanics used here: cost shocks (surcharge → pass-through / reroute / give-up) and
  closures; inventories, rationing, price propagation. No capacity-constrained routing (state why).
- Figure 1: the network and the firm geography (map; Rhine chain highlighted, Kaub edge).

## 3. Calibration and validation of the baseline
- Economics: output/exports/imports vs the MRIO (Table: 93.6 % / 98 % / 89 %; 49/50 sectors).
- Flow assignment vs Eurostat 2023: inland modal split per country and per cargo class
  (Figure 2: model vs data bars, road/rail/IWW, DE NL FR BE AT PL IT + EU); port entries vs
  `mar_go_aa`; Rhine profile Basel→Rotterdam vs CCNR cross-sections (Figure 3: tonnage along
  the river, model vs data, with Kaub and Emmerich marked).
- Honest residuals: short-haul road traffic absent by construction (NUTS2/3 geometry), ore/coal
  reach Upper-Rhine electric-arc mills because national coefficients ignore the process route,
  port shares depend on the sea-leg value of time.
- Source: `disrupt-sc-data/EU/calibration_log.md` (v1→v5), `flow_checks.py`, `validation_metrics.py`.

## 4. The 2026 scenario
- Inputs: weekly Kaub gauge (PEGELONLINE/BfG) → draught table → capacity factor → cost multiplier
  or closure (Figure 4: gauge, capacity factor and schedule, 22 Jun – 5 Oct 2026).
- Runs: baseline; 2026 profile; counterfactuals (2018 profile; 3-week closure only; no closure);
  sensitivities (price threshold; container/liquid transfer costs; seed).
- Outputs: Rhine tonnage by week vs physical fleet capacity (the ex post consistency check);
  modal substitution (rail/road tonnage gained vs DB Cargo's ~100-barge ceiling); price
  surcharges on Rhine-dependent links vs observed freight-rate multiples; firm production losses
  by sector and NUTS2 (Figure 5: map of production loss, week of 10 Aug); share of Rhine-corridor
  firms producing below equilibrium vs the DIHK survey (33 % restricting, 6 % stopped, 29 Jul–4 Aug);
  value-added loss for DE and the EU vs the ex ante macro range (−0.1 to −0.4 pp of quarterly GDP)
  and the ex post Destatis production indices when they land (Sep–Nov 2026).
- Propagation: where losses land beyond the corridor (Figure 6: first-, second-, third-tier
  losses by country); role of inventories (sensitivity on `inventory_duration_targets`).

## 5. Discussion
- What the model adds to the ex post econometrics: spatial and sectoral incidence, the
  substitution margins and their limits, the price channel.
- Limits: winner-take-all routing, no capacity rationing on the substitutes (rail slots, trucks/
  drivers) except through costs, annual MRIO vintage (2022) for a 2026 event, plant process routes.
- Policy: fleet adaptation (low-water vessels), Abladeoptimierung Mittelrhein, inventories,
  the value of the second rail track on the Rhine valley.

## 6. Data and code availability
- disrupt-sc (git SHA of the final runs), disrupt-sc-data/EU (inputs, calibration log), evidence
  dossiers with sources, run folders with `parameters.yaml` and `run_fingerprint.json`.

## Figures/tables checklist (producer)
| # | Content | Producer |
|---|---|---|
| F1 | EU network + firms map | new `plots/network_map.py` (transport.gpkg, firms.geojson) |
| F2 | modal split model vs Eurostat, per country/cargo | `flow_checks.py` §2 + `mode_split_targets_*.csv` |
| F3 | Rhine profile model vs CCNR | `flow_checks.py` §1 |
| F4 | gauge → schedule | `scenarios/2026.csv`, `draught_table.csv`, `run_rhine.py --dry-run` |
| F5 | production-loss map, peak week | scenario run `loss_per_region_sector_time.csv` + NUTS2 polygons |
| F6 | tiered propagation by country | scenario run `firm_data.csv` + supply-chain edgelist |
| T1 | calibrated parameters | final `config/user_defined_EU.yaml` |
| T2 | validation targets vs model | `evidence/evidence_rhine_literature.md` (b), `validation_targets_2026_surveys.md` |
