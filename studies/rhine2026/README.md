# Rhine 2026 low-water paper — whole-EU DisruptSC

Working plan (started 2026-09-02). Two parallel tracks: **(1)** calibrate DisruptSC
to the whole EU as a new scope `EU` (data in `disrupt-sc-data/EU/`, runbook
`onboarding/RUNBOOK.md`, manifest `disrupt-sc-data/EU/scope_manifest.yaml`);
**(2)** assemble the empirical evidence on the summer-2026 Rhine low-water event
(and its 2018/2022 precedents) that the model run will be validated against
(`evidence/`).

## 0. What exists already (2026-09-02 inventory)

| Piece | Status | Where |
|---|---|---|
| TEN-T multimodal network (roads, rail, waterways, maritime + 1,490 terminal connectors) | built 2026-08-30, converted to the EU scope schema 2026-09-02 | `disrupt-sc-data/EU/Transport/{transport,multimodal}.gpkg` via `onboarding/scripts/tent_to_scope.py` |
| Rhine chain Basel→Rotterdam (55 waterway edges, 840 km) | named (`rhine_<town>_<town>`, `special=rhine`, `disruption='rhine;<segment>;km<a>-<b>'`) | same file; **Kaub (Rhine-km 546) is on `rhine_mainz_koblenz`** (85 km, TEN-T objectid 46) |
| MRIO sources on disk | OECD ICIO 2016–2022 (81 economies, 50 sectors); FIGARO-REG 2013 (288 NUTS2 incl. UK+NO, CH national, 55 NACE); EMERGING-E 2018; GLORIA | `MRIO/` |
| Onboarding toolchain (Romania = worked example, 8 phases, firm-level path, mode calibration) | proven 2026-08-27 → 09-02 | `onboarding/`, `disrupt-sc-data/Romania/` |
| Firm/plant data library (GEM steel/cement/power/coal/chemicals inventory, Climate TRACE API, SPAM, Jasansky) | on disk | `Firms/` |
| Eurostat NST-2007 mode-split targets | DE, NL fetched (EU27 aggregate not in `rail_go_grpgood`) | `disrupt-sc-data/EU/mode_split_targets_{DE,NL}_2023.csv` |
| Eurostat population by NUTS (2023, all levels) | fetched | `disrupt-sc-data/EU/Spatial/sources/population_nuts_2023.csv` |
| Transport-disruption mechanics | `TransportDisruption` = per-edge **capacity reduction** (0–1) with `Recovery` (threshold/linear/exponential); routing sees congestion surcharges when `capacity_constraint: gradual` (×2 at 100 % utilisation, ×5 at 105 %, ×10 at 110 %); `price_increase_threshold` makes buyers give up when the rerouted cost explodes | `src/disruptsc/run_pipeline/disruption.py`, `network/transport_network.py` |

## 1. Track 1 — the EU scope (calibration)

### 1.1 Design proposal (checkpoints for the user, RUNBOOK rule 3)

**Q1 — MRIO.** Recommended: **OECD ICIO 2022**, internal regions = EU27 + CHE
(28 country regions × 50 native sectors), external partners as blocs (Q2).
Rationale: 2022 vintage (the case study is 2026), the whole Romania toolchain
(extractor with `SECTOR_RESOLVED_IMPORTS` + `ZERO_EXTERNAL_TO_EXTERNAL`,
`compute_usd_per_ton_baci.py`, `check_scope.py`, `validation_metrics.py`,
`eurostat_mode_targets.py`) runs unchanged; sub-national geography comes from
firm placement (§1.3), which is how DisruptSC has always resolved space.
Alternative: **FIGARO-REG 2013** (288 NUTS2 regions with data-based inter-regional
flows — the only inter-regional IO of the EU, but 13 years old and 15.8k
region-sectors; JRC estimated its regional trade with gravity models anyway).
Third option: **FIGARO national 2022/2023** (Eurostat's own 46 × 64 table, EUR):
needs a download (~0.5 GB) and a new extractor script (1 day).

**Q2 — external blocs and gateways.** Singletons: GBR, NOR, TUR, UKR, RUS, USA,
CHN. Directional blocs: MEA (Gulf + Levant + North Africa: SAU ARE ISR JOR EGY
MAR TUN), ASI (rest of Asia-Pacific), AME (rest of Americas), AFR (sub-Saharan),
ROW (ICIO ROW, which hides the Western Balkans + MDA + BLR + Central Asia).
Gateways: **maritime blocs attached at SEA nodes** (Atlantic edge of the maritime
layer at 32°W for AME/USA/AFR-Atlantic, the Suez approach at 32.3°E/29.6°N for
ASI/CHN/MEA-east, Gibraltar strait for AFR-west/MAR) so that the *port of entry
is chosen by routing per OD pair* — Rotterdam/Antwerp for the Rhine basin, Hamburg
for the north, Genoa/Trieste for the Po, Piraeus for Greece. This needs a small
model change: `init_pipeline/agents.py` snaps countries to **road** nodes only;
add a config switch (`country_attachment: roads | any`) so a Point at sea snaps
to the nearest maritime node. Land partners at their real crossings: GBR at the
Channel (sea node off Dover, or the Calais road node if the switch is refused),
NOR at Svinesund, RUS at the Baltic sea node (Primorsk/Ust-Luga lane) — 2022
trade was fuels by sea/pipeline, UKR at Medyka/Dorohusk (PL border), TUR at
Kapitan Andreevo (BG border; TR roads are absent from TEN-T).

**Q3 — sectors.** Keep the 50 native ICIO codes (no aggregation; services do
not use the transport network anyway), retype `C19` as `oil_and_gas` so refined
petroleum moves as liquid bulk (Romania lesson), `usd_per_ton` from BACI 2023
EU-wide trade mix.

**Q4 — spatial resolution.** Households at **NUTS2** (301 EU/EFTA regions with
2023 population; region = ISO3, `subregion_nuts2` = code). Firms via the
firm-extractor: plant-level for the Rhine-critical concentrated sectors (C19
refineries and C20 chemicals from Climate TRACE + GEM chemicals inventory, C24A
steel from GIST, C23 cement from GCCT, D power from the 8 GEM trackers, B05/B07
mines), **NUTS3 employment** (`nama_10r_3empers`, 2022) for dispersed
manufacturing and services, population fallback. Expected size ≈ 28 regions ×
50 sectors × (NUTS2/3 points) ≈ 10–15 k firms, ~200 k links — 5–7× Romania
(Romania: build 2 min, one weekly step ≈ 15 s → EU ≈ 15–30 min build, a
26-week run ≈ 1–2 h). NUTS3 everywhere (≈ 50 k firms) is possible but not
needed for the paper.

**Q5 — downloads to approve.** GISCO NUTS 2021 polygons (`NUTS_RG_20M_2021_4326.geojson`,
~25 MB, public), BACI HS17 2023 if not on disk (~1 GB), Climate TRACE API pulls
(no download), GEM trackers already on disk.

### 1.2 Phase plan (runbook phases → EU specifics)

| Phase | EU specifics | Deliverable |
|---|---|---|
| 3 trade geography | blocs of Q2; `countries.geojson` points at sea/border nodes | manifest `decisions` |
| 4 MRIO extraction | `extract_mrio_oecd.py`: `INTERNAL_REGIONS` = 28 codes, blocs as Q2, `SECTOR_RESOLVED_IMPORTS`, `ZERO_EXTERNAL_TO_EXTERNAL`; `init_sector_table_config.py` + `compute_usd_per_ton_baci.py --scope <28 ISO3>`; `check_scope.py EU --economic-only` | `EU/Economic/{mrio.csv,sector_table.csv}` |
| 5 transport | **done provisionally** (`tent_to_scope.py`); add per-edge waterway **capacities** (tons/day) for the Rhine chain from CCNR/Destatis tonnages (scenario needs them), rail corridor capacities from RFC data; `default_transport_capacity` for the rest | `EU/Transport/*` + `transport_capacity_overrides` in the config |
| 6 spatial | NUTS2 households from GISCO + `population_nuts_2023.csv`; firm-extractor config `EU/firm_extractor_config.yaml` (28 countries) | `EU/Spatial/*` |
| 7 run | `config/user_defined_EU.local.yaml` (draft committed alongside this README, Romania-calibrated logistics as the prior); `initial_state` with `--seed 42` | run folder + sanity report |
| 8 validation | `validation_metrics.py EU`; modal split vs Eurostat `tran_hv_frmod` per country and per NST (DE, NL, BE, FR, AT, PL, IT…); port shares vs Eurostat `mar_go_aa`; Rhine tonnage vs CCNR/Destatis (Emmerich–Lobith cross-section ≈ 150 Mt/yr); trade by partner vs Comext | `EU/validation_report.md` |

### 1.2b Status 2026-09-03 and the calibration plan

Built and committed: ICIO 2022 extraction (28 × 50, 12 blocs), sector table with
EU-mix BACI 2023 unit values, 251 NUTS2 households, 12,874 firm-extractor firm points,
12 gateway points on sea/border nodes (`country_attachment: any`, disrupt-sc 1ab423d).
Two bugs found on the way and fixed in disrupt-sc: `sectors_to_exclude: None` excluded
sector N from every ICIO scope (KI-24, 0bf2124); the route cache deep-copied every
reversed route (92 of 130 build minutes on the EU scope, 7363ad4).

**Smoke run** (population-weighted firms, `output/EU/20260903_072310`): output 92 % of
MRIO, exports 98 %, imports 87 %, gateway shares = MRIO-implied. Flow assignment is
far off and is the calibration job (`studies/rhine2026/flow_checks.py`):

| Check | Model | Real | Lever |
|---|---|---|---|
| inland tkm split EU (road/rail/IWW) | 46.5 / 40.1 / 13.4 | 78.1 / 16.9 / 5.0 (Eurostat 2023) | mode costs, transfer costs, VOT (per cargo) |
| DE split | 41 / 30 / 29 | 73 / 21 / 7 | idem; IWW ×4 too high |
| Rhine at Kaub (`rhine_mainz_koblenz`) | 182 Mt/yr | ≈ 50 | waterway cost / transfers |
| Rhine at Emmerich | 203 Mt/yr | 118 | idem |
| Antwerp / Trieste / Venice port entries | 55 / 183 / 150 Mt | 242 / 51 / 25 | **port capacities** (binary constraint, `port_capacities.py`) |

Plan: (1) firm-level baseline — done (`20260903_094137`, 42 min; economics 93.6 % / 98 % /
89 %; flow fit unchanged in structure: Kaub 132 Mt, Antwerp 53 Mt, rail 40 %); (2) v2 =
per-port throughput capacities (Eurostat 2023 × 1.3 peak) through
`transport_capacity_overrides` with `capacity_constraint: binary`, which blocks
over-capacity terminals without re-pricing every edge, plus a first cost move (waterways
0.0045 → 0.010, rail 0.040 → 0.044, roads 0.055 → 0.050 USD/tkm, river transfers 24 h/6 USD
with container 12 h/4 and liquid 16 h/4, rail transfers 8 h/5) — running; (3) refit per
cargo class against the DE/NL/EU NST targets (Romania procedure: scalars in range first,
then per-cargo transfer costs, always with `--seed 42`); (4) check the Rhine profile
against `scenarios/rhine_capacities.csv`. Every iteration is logged in
`disrupt-sc-data/EU/calibration_log.md`. Runtime: ≈ 42 min per full rebuild, 7 min per
weekly step (12.6 GB RAM).

Scenario side (independent of the calibration): `baseline_capacities.py` derives finite
capacities for every rail/road/waterway edge from the calibrated baseline (baseline load ×
headroom, rail 1.3 / road 1.5 as stated assumptions to sweep) and gives the Rhine edges
their normal-year cross-sections; `run_rhine.py` merges that CSV and the port capacities
into the scenario run's overrides, so rail can absorb only its headroom (DB Cargo's
≈ 100-barge ceiling) instead of the whole Rhine traffic.

### 1.3 Calibration targets specific to the Rhine study

- **Rhine cross-section tonnage** (Emmerich/Lobith ≈ 140–160 Mt/yr; Kaub ≈ 50–60
  Mt/yr; Basel ≈ 5–6 Mt/yr) — the model's edge flows on `rhine_*` must reproduce
  the profile down the river; commodity mix (ores/coal to Duisburg, oil products
  and chemicals to Ludwigshafen/Karlsruhe, containers Rotterdam–Basel).
- **Modal split of DE/NL** by NST cargo class (fetched targets): DE total
  62/28/9 road/rail/IWW, NL 57/6/38; dry bulk DE 53/27/20, liquid DE 28/42/30,
  NL liquid 8/2/90.
- **Port shares** of EU maritime imports (Rotterdam ≈ 440 Mt, Antwerp ≈ 270,
  Hamburg ≈ 110, Marseille, Algeciras, Valencia, Genoa, Piraeus…).

## 2. Track 2 — case-study evidence (validation)

Files in `evidence/` (web-collected 2026-09-02/03, every fact dated and sourced):
- `evidence_rhine2026_timeline.md` — what happened in summer 2026 (Kaub gauge
  trajectory day by day, freight, surcharges, industrial statements, macro estimates,
  policy, other rivers, meteorology, confounders; ~150 sources).
- `evidence_rhine_literature.md` — annotated bibliography of 2018/2022/2003 and
  the academic literature + a 73-row **validation-targets table** + 17 open gaps.
- `evidence_rhine_datasources.md` — machine-readable sources (PEGELONLINE,
  Destatis 46321, Eurostat iww_*, CCNR market observation, production indices,
  barge freight indices, Kleinwasserzuschlag tables) — partial (gauges complete).
- `update_20260903_supply_chain_damage.md` — 3 Sep sweep for supply-chain disruption and
  damage evaluations: the DIHK survey (n = 170, 29 Jul–4 Aug: 78 % higher costs, 72 %
  reorganised logistics, ≈ 33 % restricting production, 6 % stopped, 13 % site at risk),
  IHK Rheinhessen, the ex ante macro range (IfW −0.1/−0.2 pp Q3, Oxford Economics −0.2,
  Commerzbank −0.35, IW −0.4 pp p.a.; BVR nevertheless raised its 2026 forecast to 1.0 %),
  VCI's 3 Sep quarterly report, DB Cargo's substitution ceiling, the July truck-toll index,
  and the list of ex post anchors still to come (Destatis July IP ≈ 8 Sep, BASF Q3 27 Oct).
- `validation_targets_2026_surveys.md` — rows 74–83 of the validation-targets table
  (firm-level extensive margin, cost pass-through distribution, adaptation shares).

**The 2026 event in one paragraph.** After the least snowy Alpine winter since
1991 and a Rhine basin below normal precipitation every month from February, the
Kaub gauge (Rhine-km 546, the Middle Rhine bottleneck) fell below the reference
low-water level GlW (77 cm) around 8–12 July, was last above it on 20–22 July,
equalled the 2018 record (25 cm) on 31 July, set a new all-time low on 4 August
and reached **5 cm on 17 August** (series since 1880; Cologne 44 cm, Duisburg-
Ruhrort 126 cm, Emmerich −28 cm, Lobith 565 m³/s — all records). There was no
formal closure, but the river was "de facto divided" at Kaub from ~11 August:
standard vessels loaded 10–20 %, only nine purpose-built low-water tankers kept
moving 250–800 t parcels, KBN counted 90 kt/week past the bottleneck instead of
400 kt (−77 %), ARA→Karlsruhe tanker rates rose from EUR 45/t (June) to EUR
215/t (mid-August, ARA→Basel 275/t), container surcharges reached EUR 1,335/20'.
Rain from 18 August lifted Kaub to 77 cm on 29 August (never above GlW); on
2 September it was falling again (54 cm) with the BfG forecasting 37–40 cm by
6 September. Named impacts: LyondellBasell (butadiene FM 16 Jul), Covestro
(polyether polyols FM 7 Aug), BASF (isolated bottlenecks, plasticiser FM,
"reduced capacity"), Evonik, Lanxess, thyssenkrupp (own push convoys stopped
14 Jul, furnace output "moderately" reduced, rail share doubled), MiRO Karlsruhe
(tankers at 1/3, 50 % of usual rail capacity because the right-bank Rhine railway
is closed until 12 Dec 2026), EnBW/Uniper. Macro: IfW −0.1/−0.2 pp Q3 GDP,
Commerzbank −0.35 pp, IW up to −0.4 pp p.a., Bundesbank "at best slight growth".
Confounders: Hormuz-driven oil prices, weak cracker demand (65–70 %), the rail
line closure, Dutch port strikes.

**Ten numbers the model must reproduce (2018 as the calibrated precedent):**

| # | Target | Value | Source |
|---|---|---|---|
| 1 | German IWW tonnage per Kaub day < 78 cm | −0.87 % (t), −0.41 % (t−1); 30 days ≈ −25 % | Ademmer et al. 2023 |
| 2 | German industrial production per low-water day | −0.034 % (t), −0.024 % (t−1); ≈ −1 % per 30 days; peak −1.5 % (Nov 2018) | Ademmer et al. 2023 |
| 3 | Elasticity of IP to IWW volume | 0.036 (+0.03 lagged): −10 % IWW → −0.4 % IP → −0.1 % GDP | Ademmer et al. 2023 |
| 4 | German IWW 2018 | 198.0 Mt (−11.1 %); Nov 2018 −34 % y/y; tkm −15.5 % | Destatis; BDB |
| 5 | Traditional Rhine 2018 / 2022 | 165 Mt (−11 %) / 155.5 Mt (−7.8 %) | CCNR |
| 6 | Freight rates 2018 | liquid spot ≈ 4.5× normal, dry ≈ 2.5× (Oct–Nov); Rotterdam→Basel distillate $5 → $35/bbl | CCNR; EIA |
| 7 | Load factors vs Kaub | 78 cm 25 %; 55 cm 16 %; 40 cm ≈ 20 % (WSV); 25 cm 15 %; 2018 Duisburg barges 2,000 → 700 t | Contargo; van Dorsser; Platts |
| 8 | Modal substitution | rail +0.07 % per low-water day (weak); 2026: DB Cargo 400–900 wagons ≈ 200 barges, Kombiverkehr +2,000 TEU | Ademmer; DB Cargo |
| 9 | Firm level 2018 | BASF EBIT −EUR 250 m; chem-pharma production Q4 2018 −10 % q/q | BASF; VCI |
| 10 | 2026 throughput at Kaub | 60+30 kt/week vs 300+100 normal (−77 %) at Kaub 10–17 cm; rates 45 → 215 EUR/t | KBN; Argus |

Scenario tables built from this evidence (in `scenarios/`): `2026.csv` (weekly
Kaub profile 22 Jun → 28 Sep, observed/press/forecast/assumption flagged),
`draught_table.csv` (Kaub cm → aggregate capacity factor past Kaub, with the
per-vessel GMS load factor and the anchoring source per row);
`rhine_capacities.csv` (normal-year Mt/yr and tons/day per named segment: CCNR
cross-sections at Emmerich 117.9 Mt and Iffezheim 16.0 Mt for 2023, Kaub ≈ 50 Mt and the
rest interpolated from port volumes, all interpolations marked ESTIMATE).
`python studies/rhine2026/run_rhine.py --profile 2026 --dry-run` prints the weekly
schedule: 15 disrupted weeks from 22 June, capacity −18 % (105 cm) to −91 % (11 cm, week
of 10 August), −77 % on the 17 August week, −50 % after the rain, 8 recovery weeks.

### 2.1 Observable ↔ model output mapping

| Empirical observable | Model quantity | Where in the output |
|---|---|---|
| Kaub gauge → max draught → load factor (weekly) | scenario input: `capacity_reduction` on `rhine_mainz_koblenz` (and `rhine_koblenz_bonn`…) per week | `disruptions:` list, one entry per week with `duration: 1` and the week's reduction, or a `Recovery` curve |
| Rhine tonnage at Kaub / Emmerich (Destatis monthly, CCNR) | edge tons on `rhine_*` per step | `transport_edges_with_flows_<t>.geojson`, logistics report |
| Modal shift to rail/road (DB Cargo, Destatis rail/road monthly) | tons on parallel rail (Rhine valley lines) and road edges | same |
| Barge spot rate × 5–10, Kleinwasserzuschlag | congestion multiplier on the constrained edge; share of links rerouted; delivered-price increase | `link.cost_per_ton` change, price indices in `firm_data.csv` |
| Industrial production dip (Destatis by WZ: C19, C20, C24; Kiel: −1 % IP per 30 days < 78 cm) | firm production loss by sector/region | `firm_data.csv`, household-loss headline |
| Named-firm impacts (BASF Ludwigshafen, ThyssenKrupp Duisburg, refineries) | production of the plant-level firms placed by firm-extractor | firm-level rows |
| Macro (GDP effect 2018 ≈ −0.3 %, Bundesbank) | total value-added loss, EU-wide and DE | aggregate loss series |

### 2.2 Scenario construction

1. Weekly Kaub levels (`scenarios/2026.csv`, PEGELONLINE daily means for
   August–September, press readings for June–July, BfG forecast beyond) →
   `scenarios/draught_table.csv` (aggregate capacity factor past Kaub: 0.60 at GlW,
   0.30 at 40 cm, 0.22 at 25 cm, 0.05 at 5 cm) → weekly `capacity_reduction` on
   `rhine_mainz_koblenz` via `run_rhine.py`.
2. Waterway capacities in tons/day for the Rhine chain (`scenarios/rhine_capacities.csv`,
   CCNR cross-sections Emmerich 117.9 Mt and Iffezheim 16.0 Mt in 2023, Kaub ≈ 50 Mt
   estimated) so that a 70 % capacity loss actually binds. **Open design point**: the
   gradual congestion multiplier is 0.5 at zero load and 1.0 only at 80 % utilisation,
   so switching `capacity_constraint` on re-prices every edge relative to the
   calibrated (unconstrained) baseline. Candidate fix for the scenario runs: derive
   per-edge capacities from the baseline flows (capacity = 1.25 × baseline load,
   floored) for all modes so that the baseline sits at u ≈ 0.8 (multiplier ≈ 1)
   everywhere, and only the Rhine edges get the real (lower, low-water) capacities.
3. Rail alternative capacity (Rhine valley lines, DB Cargo statements) bounds the
   modal shift — `default_transport_capacity.railways` per corridor via
   `transport_capacity_overrides` on the named rail edges.
4. Runs: baseline; 2026 observed profile; counterfactuals (2018 profile,
   full closure 8 weeks, "Abladeoptimierung" +20 cm); sensitivities (rail
   capacity, inventories, `price_increase_threshold`).

## 3. Open decisions / questions for the user

See §1.1 Q1–Q5. Everything not depending on them proceeds: evidence curation,
scenario mechanics, network capacities, config draft.
