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
  closures; cargo-type-specific switching costs (tank barges and ore trains have no road/rail
  equivalent at volume, so bulk pays the surcharge while the river is open and gives up when it is
  closed; containers reroute); inventories (30 days for goods, import bundles included), rationing,
  price propagation; partially-binding Leontief with the IHS Markit survey criticality (baseline
  since 4 Sep). No capacity-constrained routing and no quantity cap on substitutes (state why: the
  substitution-ceiling experiment of 3–4 Sep withheld 16 bn USD directly and cascaded to 30 % of a
  quarter — a quantity constraint is not the model's philosophy).
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
- Runs (baseline definition of 4 Sep, user decisions): survey criticality, import bundles by MRIO
  composition, firm inventories by buying industry (Bundesbank stock days), cargo-specific switching
  costs, one delivered-price give-up threshold (5), no quantity cap: `2026_seed42_base`; the 2018
  profile with the same baseline; the cost-only bound (unlimited substitution, 3 Sep) as reference;
  the substitution-ceiling experiments (0.30, 0.70, survey variant) reported as what a quantity cap
  does; sector-specific give-up thresholds evaluated from the 2018/2026 evidence and not adopted;
  no-disruption control (drift check). Closure floors by cargo class (5 Sep: container ≤ 40 cm,
  tank barges ≤ 50 cm, dry bulk ≤ 30 cm; van Dorsser 2020, Contargo): `2026_seed42_floors`,
  `2018_seed42_floors` — results 5 Sep: 2026 DEU 1.20 bn (0.125 % of a quarter, inside IfW's EUR 1–2
  bn), 2018 DEU 2.03 bn (0.21 % of a quarter, peak 0.58 % of a week in late November, about two-thirds
  of the ex-post −0.3/−0.4 % GDP) → candidate final baseline, user decision pending. Sensitivities for the cluster: closure floors ± 10 cm,
  lean-2019 inventories, halved/doubled switching costs, seeds.
- Two modelling decisions to state up front, both forced by the scale of the scope: the
  criticality threshold (2 % cost-share proxy for the partially-binding Leontief; strict
  Leontief let a negligible cross-border service input cascade — KI-29) and the give-up rule on
  the delivered price rather than the freight bill.
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
- Three kinds of production restriction in the evidence, one of which the model resolves:
  (i) physical stoppages where no alternative mode exists at volume (refineries, steel, power,
  agri-food fed by barge) — captured by the switching-cost mechanism, 3.8 % of corridor firms vs
  the survey's 33 % restricting / 6 % stopped; (ii) cost-driven cuts of marginal output at 3–7×
  freight rates (gravel, fertiliser, grain, low-value chemicals) — only through the give-up rule,
  which needs cargo- or margin-specific thresholds; (iii) precautionary throttling to stretch stocks
  under an uncertain closure length (BASF mid-Aug, thyssenkrupp force majeure 16 Jul, Kehl) — NOT
  modelled (firms run at full rate until an input runs out): state this as the main reason why the
  model's direct macro loss is an order of magnitude below the ex-ante estimates, and as the
  natural next mechanism (a stock-stretching rule).

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
| F1 | EU network + firms map | `plots/baseline_figures.py` — DONE (`figures/F1_network_firms.png`) |
| F2 | modal split model vs Eurostat, per country/cargo | `plots/baseline_figures.py` — DONE (`figures/F2_modal_split.*`) |
| F3 | Rhine profile model vs CCNR (Basel → Lobith) | `plots/baseline_figures.py` — DONE (`figures/F3_rhine_profile.*`) |
| F4 | gauge → capacity factor → schedule, closed-for-class panel | `plots/scenario_figures.py` — DONE (`figures/F4_shock_2026.*`, `F4_shock_2018.*`, closure floors 5 Sep) |
| F5 | production-loss map (NUTS2), peak week | `plots/scenario_figures.py --run <run>` (firm_data + nuts2_admin) — after the run |
| F6 | weekly value-added loss by country | `plots/scenario_figures.py --run <run>` — after the run; tiered propagation via the supply-chain edgelist still to do |
| T1 | calibrated parameters | final `config/user_defined_EU.yaml` |
| T2 | validation targets vs model | `evidence/evidence_rhine_literature.md` (b), `validation_targets_2026_surveys.md` |
