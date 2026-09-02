# Phase 8 — validation report (model vs data)

Goal: a report that compares the passing `initial_state` run against real-world data on
two fronts — (1) economics, (2) flow assignment — and ends with prioritized calibration
recommendations (which parameter, which data). First produced for Romania
(`disrupt-sc-data/Romania/validation_report.md`); use that as the worked example.

## Prerequisites

- Phase 7 complete; rerun with `export_files: True` so the output folder holds
  `mrio_by_sector.csv`, `mrio_by_country.csv`, `trade_data.csv`, `firm_data.csv`,
  `transport_edges_with_flows_0.geojson`, `transport_nodes.geojson`.
- `--open` forces `export_files: True` since the KI-15 fix; older checkouts silently
  export nothing.

## Step 1 — model-side numbers (deterministic)

```bash
python scripts/validation_metrics.py <Scope> [--time-resolution week]
```

Prints: model-vs-MRIO output totals and per-sector outliers; per-partner kept shares of
imports/exports; gateway shares (countries clustered within ~20 km, model vs
MRIO-implied); modal split in ton-km + annualized bn tkm; active multimodal connectors;
top-12 nodes by throughput (coordinates — name them by nearest city/port yourself).

Interpretation traps, learned on Romania:

- **`trade_data.csv` semantics**: a country's `exports` = its sales INTO the scope
  (= scope imports); its `imports` = its purchases FROM the scope (= scope exports).
- **Model ≈ MRIO is expected for output/exports** (any gap = flow_coverage cuts, cache
  staleness, or dropped sectors). The interesting comparisons are (a) which cells the
  coverage filter killed, (b) MRIO vs official statistics.
- **flow_coverage budget distortion (structural, any lean bloc design)**: the coverage
  quantile is computed over ALL MRIO cells, and bloc-to-bloc cells (each bloc's internal
  economy — hundreds of $T) dominate the value budget while being economically inert in
  v2 (skipped at supplier selection; `transit_from` never populated). Result: small but
  real partner→scope import cells die; partners can go silent entirely (Romania: BGR,
  TUR, UKR, AME imports = 0 at q=0.9). Check section 2 of the script output FIRST — it
  explains most gateway and import anomalies downstream.
- **Maritime = 0 flows is structural**, not a bug: country od_points snap to road nodes
  (`agents.py:577`), so no baseline route needs a sea edge.
- **Hub list reads as a transit-corridor map**: throughput counts pass-through, and
  population-weighted firms understate metro hubs (Bucharest: 12% of population, ~27%
  of GDP). Compare against the country's real logistics geography, and say which kind
  of map the model is drawing.

## Step 2 — data-side anchors (research)

| Dimension | Sources (EU scopes) | Sources (non-EU) |
|---|---|---|
| Modal split, inland tkm | Eurostat `tran_hv_frmod` + *Freight transport statistics — modal split*; INS/national tkm series (`road_go_ta_tott`, `rail_go_total`, `iww_go_atygo`) | ITF/OECD transport statistics; national statistical office; World Bank LPI context |
| Trade by partner | Eurostat Comext; WITS/World Bank; UN Comtrade | WITS / UN Comtrade |
| Trade by transport mode | Eurostat `ext_lt_intratrd` variants / national customs "trade by mode" | customs statistics where published |
| Ports / gateways | port authority annual traffic; border crossing counts (road administration) | port authorities; corridor observatories |
| Economic totals | Eurostat national accounts; World Bank GDP | World Bank; IMF |
| Sub-national weights | Eurostat NUTS3 GDP / national county GDP & employment | subnational accounts, census employment |

Label every anchor that is approximate or vintage-mismatched as an anchor, not a target.
MRIO totals can legitimately differ from customs data (basic vs CIF prices, processing
trade, services coverage) — flag, don't force.

## Step 3 — write the report

Structure (mirror the Romania example):

1. **Economic validation** — model vs MRIO table (output, exports, imports, ratio +
   verdict), per-sector outliers, per-partner kept shares with the root cause; then MRIO
   vs official statistics (VA vs GDP, final demand, trade totals).
2. **Flow assignment** — modal split table+chart (model vs national data, shares AND
   absolute tkm/yr); gateway table (imports% and exports%, model vs MRIO-implied vs data
   anchors); hubs (model top nodes, named, vs the country's real logistics geography);
   connector activity.
3. **Calibration recommendations** — priority-ordered; each row names the parameter or
   structure to change, the dataset to calibrate against, and the expected effect.
   Structural fixes (flow_coverage budget, extraction choices) before parameter tuning
   (basic_cost, dwell, usd_per_ton) before data upgrades (GDP firm weights, gateway
   splits).

Deliverables: `<data-root>/<Scope>/validation_report.md` (durable copy, next to the
manifest) + an Artifact page for sharing. Record the run folder, verdicts, and top
recommendations in the manifest under `p8_validation`.

## Recurring recommendation patterns

These came out of Romania and will likely recur; check each against the new scope
instead of copying blindly:

1. Zero bloc-to-bloc cells at extraction — **implemented** as
   `ZERO_EXTERNAL_TO_EXTERNAL = True` in `extract_mrio_oecd.py` (port to the other
   extractors when first used). On Romania it revived all silenced partners and moved
   imports 61%→70% of MRIO (exports 93%→98%); the residual gap is the genuine q tail,
   so `flow_coverage` becomes a meaningful knob afterwards.
2. Rebalance `logistics.basic_cost`/`dwell_times` against **commodity-level** modal
   splits — the aggregate split is under-identified (many cost combinations reproduce
   it). **Tool available**: `scripts/eurostat_mode_targets.py --geo <XX> --year <YYYY>
   [--compare <run>/transport_edges_with_flows_0.geojson]` fetches Eurostat
   `road_go_ta_tg` + `rail_go_grpgood` + `iww_go_atygo` (NST-2007 breakdown) and
   computes per-NST and per-cargo-type mode-share targets plus mean haul per mode
   (a second moment the model must also match). EU scopes only; for others keep the
   same target structure from ITF/OECD or national statistics.
   Interpretation guide from Romania: dry_bulk target 35/23/42 road/rail/IWW vs model
   56/41/3 → the missing waterway traffic is all bulk (cut river-port dwell/fees for
   bulk); container target 89/6.5/4.3 vs model 65/32/2 → the rail excess is container
   cargo (raise rail cost or dwell for containerizable goods). Caveats printed by the
   tool: road_go covers registered hauliers anywhere (use shares, not road totals);
   GT07 refined petroleum is rail-heavy in reality but container-typed in DisruptSC
   unless C19 gets a bulk cargo type.

   **Calibration procedure (executed on Romania 2026-08-27, 5 iterations):**
   - The load-bearing lever is **per-cargo-type `cost_of_time`** (freight value of
     time; supported since the same-day disrupt-sc commit — dict form
     `{container: 1.6, dry_bulk: 0.10, liquid_bulk: 0.10, default: 2.0}` USD/t·h).
     Without it every cargo class gets identical edge costs and per-commodity splits
     cannot differ. VOT separates fast-vs-slow (road vs rail+IWW) per cargo; it CANNOT
     separate rail from IWW (both slow) — that balance comes from relative
     `basic_cost` and connector dwell/fees (Danube access ended at 3 h + $1/t).
   - Ground `basic_cost` in price data and stay in-range while iterating (Romania
     final: road 0.06 / rail 0.042 / IWW 0.0035 USD/tkm — CNR trucking, CFR access
     charges, CCNR/viadonau rates). Roughly one run per parameter change; compare with
     the per-cargo block of `eurostat_mode_targets.py --compare`.
   - Retype refined petroleum (C19) as `oil_and_gas` in the sector table (add
     `oil_and_gas` to `physical_types` in the sector-table config) so it gets
     liquid_bulk cargo.

   **v6/v6.1 supplement (Romania 2026-09-02, after the firm-level geography):**
   refit whenever the firm geography changes materially — the v5 fit did not survive
   real refinery/plant placement. Procedure and laws that transfer to any scope:
   - **Always calibrate with `--seed`**: unseeded runs wobble ±2–4 pp from supplier
     RNG; you cannot attribute a 3 pp move to a parameter without it.
   - **Two-stage**: (1) rebalance the scalars inside their grounded ranges — the
     honest levels matter (optimistic port handling of 3 h/$1 alone gave barges 50%
     of liquid tkm; realistic is ~16 h/$3.5); (2) express infrastructure with
     **per-cargo `dwell_times`/`loading_fees`** (dict form
     `{default: 6, liquid_bulk: 0.5}`, disrupt-sc ≥ fa4a39f) — refinery sidings =
     near-free rail transfer for liquid, no fuel river terminals = prohibitive barge
     transfer. On Romania this took liquid rail from 11% to 57% with dry bulk and
     containers undisturbed; it removed what v5 had to document as a structural
     ceiling.
   - **Empirical sensitivity laws** (signs, verified by sweeps): raising a bulk
     cargo's VOT moves it barge→rail, never rail→road (barge is slowest); rail
     `basic_cost` trades dry-rail against liquid-rail with NO joint scalar solution
     (Romania: 0.032 → 49/51% dry/liquid rail, 0.046 → 31/16%) — that conflict is
     exactly what per-cargo transfer costs resolve; barge suppression is transfer-
     cost work, not VOT work.
   - **Expect knife edges**: routing is winner-take-all per OD, so one fee step can
     flip a whole OD block (Romania: liquid barge fee $24→$28 moved ~16% of liquid
     tkm). Bracket the flip point and stay on the safe side; document it in the
     config.
   - **Judge the fit per-cargo, dominant-mode-first**: for disruption analysis the
     right dominant mode per cargo class beats a cosmetically closer aggregate —
     and the aggregate road target is inflated anyway (registered-hauliers-anywhere
     bias the tool prints).
   - **Import flows only get cargo-typed with `SECTOR_RESOLVED_IMPORTS` extraction**
     (recipes §1) + corridor-basin sub-blocs: on Romania this lifted the Danube from
     13.6% to 17.9% of inland tkm (target 19.2) with no cost changes at all — imported
     bulk finally rides road→barge transfers. Check this before pushing cost parameters
     to their range limits; the legacy single-imports-row format caps IWW structurally.
   - Expect **structural ceilings** and stop tuning when you hit them instead of
     pushing costs out of range: (a) international trade legs on waterways cannot
     exist when all gateways sit on road nodes (Romania: ~3.8 bn tkm/yr of
     upstream-Danube bulk → IWW plateaus ~8 pp below target; fix = waterway-attached
     gateway, a model+scope change); (b) mean hauls cannot be checked from edge-sum
     tons (edge-crossing counts, not OD tons).
3. Ground `usd_per_ton` in trade unit values — **tool available**:
   `compute_usd_per_ton_baci.py` in mrio-extractor (BACI value+tons per HS6 flow →
   sector densities via `hs17_to_icio_concordance.csv`; `--patch-config` updates the
   sector-table YAML directly). Literature guesses ran ~2–3× low on high-value
   manufacturing for Romania; bulk sectors were roughly right.
4. Weight firms by real data instead of population — **implemented as the
   firm-extractor toolchain** (recipes §6): plant trackers and production grids for
   concentrated sectors, `regional_stats` (Eurostat NUTS3 employment / any national
   county×sector table) for services and dispersed manufacturing, `manual` anchors
   for flagship few-plant sectors, with the KI-17 fix making weights set firm sizes.
   Fixes hub geography (Romania: Pitești = Dacia entered the top-4 throughput nodes)
   and is a PREREQUISITE for meaningful mode calibration — refit costs after it.
5. Split aggregate gateways (e.g. one EUR point) across the real crossings once
   per-crossing scenarios matter.
6. Maritime activation is a model-level change (country→maritime attachment), not a
   calibration knob; recommend only if port-disruption scenarios are on the agenda.
