# New-scope calibration pipeline

Runbook for onboarding DisruptSC to a new scope — written for any AI assistant (or a
careful human) working in this repository. Trigger it whenever the task is "apply
disrupt-sc to country X", "new scope for X", "calibrate the model to X", or "validation
report for scope X".

Goal: take DisruptSC from "I want to model country X (or countries X, Y, Z)" to a passing
`disruptsc <Scope> --simulation_type initial_state` run plus a validation report comparing
model output with real-world data, with the user deciding at explicit checkpoints and every
decision recorded in a resumable per-scope manifest.

## Environment layout (no absolute paths)

Everything is located relative to this repo and its parent folder, written `<parent>`
below. Scripts find the repo by walking upward to `pyproject.toml` + `src/disruptsc`
(`scripts/locate.py`); `python onboarding/scripts/check_env.py` verifies the whole layout
and prints clone commands for anything missing.

| What | Expected location | If missing |
|---|---|---|
| Data root | `<parent>/disrupt-sc-data` (env `DISRUPT_SC_DATA_PATH` overrides) | create it or set the env var |
| MRIO source data | `<parent>/MRIO/{ICIO, EMERGING-E, GLORIA, FIGARO}` | licensed data, **not on GitHub** — the user must obtain it |
| mrio-extractor | `<parent>/MRIO/mrio-extractor` | `git clone https://github.com/ccolon/mrio-extractor` |
| osm-extractor | `<parent>/transport/transnet/osm-extractor` | `git clone https://github.com/ccolon/osm-extractor` + `pip install -e` |
| transnet-simp (CLI `tnclean`) | `<parent>/transport/transnet/transnet-simp` | `git clone https://github.com/ccolon/transnet-simp` + `pip install -e` |
| multitnbuild | `<parent>/transport/transnet/multitnbuild` | `git clone https://github.com/ccolon/multi-tn-build` + `pip install -e` |
| firm-extractor | `<parent>/Firms/firm-extractor` (data library = `<parent>/Firms/`, see its README) | `git clone https://github.com/ccolon/firm-extractor` + `pip install -e` |
| Multimodal builder | `<data-root>/build_transport.py` + per-scope `Transport/multimodal_config.yml` | comes with the data root |

Tool repos are searched in close locations (`<parent>`, `<parent>/MRIO`,
`<parent>/transport[/transnet]`, `<parent>/tools`); when one is not found, **ask the user
to clone it** to the expected location rather than guessing an alternative.

Supporting material in this folder (script commands below are run from `onboarding/`):
- `references/tool-recipes.md` — exact commands, formats, and gotchas per tool. **Read before phases 4–5.**
- `references/failure-triage.md` — runtime error → cause → fix for phase 7.
- `references/validation-report.md` — phase 8 method: model-vs-data comparisons, data sources, report structure. **Read before phase 8.**
- `references/known-issues.md` — register of tool/model defects. Consult at each phase; append when new ones surface.
- `references/firm-data-sources.md` — survey of open plant/grid production datasets for the phase-6 firm-level path.
- `scripts/` — deterministic helpers (`check_env.py`, `mrio_coverage.py`, `geofabrik.py`, `build_spatial.py`, `check_scope.py`, `validation_metrics.py`, `eurostat_mode_targets.py`).

## Standing rules

1. **Manifest.** All state lives in `<data-root>/<Scope>/scope_manifest.yaml`. Create it in phase 1;
   update its `phases:` and `decisions:` blocks at the end of every phase. On invocation, if a
   manifest already exists for the scope, summarize its status and resume at the first incomplete
   phase — do not redo completed phases unless the user asks.
2. **Tool-issue protocol.** When a tool (mrio-extractor, osm-extractor, tnclean, multitnbuild,
   build_transport.py) or disrupt-sc itself shows a bug, an inconsistency, a missing feature, or a
   stale doc that affects the current step:
   - stop before silently working around it;
   - state the issue in one or two sentences with file:line evidence;
   - check `references/known-issues.md` — if it is already listed with an agreed resolution, apply
     that and move on;
   - otherwise ask the user one explicit question with these options: **fix the tool now** /
     **use as-is with a workaround** / **defer** (log only);
   - record the outcome in `references/known-issues.md` AND under `tool_issues:` in the manifest.
   Tool fixes are committed locally in the tool's own repo with a clear message; never push
   (the user handles pushes).
3. **Checkpoints are real.** Never guess the user's answer at a checkpoint marked below; ask
   a single explicit question with labeled options. Between checkpoints, proceed autonomously.
4. **Environment.** All tools run in the conda env where the toolchain is installed
   (miniforge **base** on the main workstation), activated with `conda activate`
   (invoking `python.exe` by full path makes tnclean crash silently). On Windows always pass
   `--no-progress` to tnclean (Rich progress bars raise cp1252 UnicodeEncodeError). mrio-extractor
   scripts must run with cwd = `MRIO\mrio-extractor` (their SOURCE/OUTPUT paths are cwd-relative).
5. **Reproducibility.** mrio-extractor is configured by editing constants in each script's
   CONFIGURATION block. After every extraction, copy the exact block you ran into the manifest
   under `mrio.config_snapshot` — otherwise the selection is unrecoverable (known issue KI-05).
6. **Downloads.** Before downloading anything (Geofabrik PBF, geoBoundaries files), state the
   filename, source, and approximate size, and get the user's go-ahead.

## Naming conventions

- **Scope name**: PascalCase, no spaces, **no underscores** (region codes must never contain `_`
  — DisruptSC splits `region_sector` on the first underscore). E.g. `Uzbekistan`, `CentralAsia`.
- **Regions**: ISO3 trigrams for countries (`UZB`, `KAZ`); short uppercase labels for blocs
  (`EUR`, `ROW`, `EAS`). FIGARO natively uses 2-letter + NUTS2 codes — alias them to ISO3 via
  `REGION_ALIASES` during extraction.
- **Sectors**: keep native MRIO codes (`A01`, `C10T12`) or define 3-letter trigrams for aggregates.
  **Hard rule**: no sector name may match, case-insensitively, any of
  `export`, `import`, `tax`, `va`, `value added`, `capital`, `investment`, `government`,
  `household`, `final demand` — the MRIO loader classifies rows/columns by these regexes
  (`src/disruptsc/network/mrio.py:434`). `check_scope.py` verifies this.

## Phases

### Phase 0 — environment check (silent, fast)

Run `python scripts/check_env.py`. It verifies the data root, the four tool repos (with
clone commands for missing ones — relay those to the user, do not guess locations), the
python packages, the MRIO source data, and osmium. Report anything missing up front; a
missing piece only blocks its own phase (missing MRIO *data* only blocks phase 4 for that
database).

### Phase 1 — scope & transport toggle (workflow A–B)

1. Capture the scope: list of ISO3 countries + a scope name (see naming conventions).
2. **Checkpoint**: with or without transport network (`with_transport`)? Without transport,
   phases 2 and 5 are skipped and no `Transport/` folder is needed.
3. Create `<data-root>/<Scope>/` with subfolders `Economic/`, `Spatial/`, `Transport/` and write
   the initial `scope_manifest.yaml` (schema at the bottom of this file).

### Phase 2 — transport modes (workflow C) — only if with_transport

1. Web-search the modal split of domestic and international freight for the scope (t-km or tonnage
   shares by road / rail / inland waterway / sea / pipeline; note landlocked-ness, main corridors,
   main ports and border crossings — the port/border list is reused in phase 6 for countries.geojson).
2. Propose a mode list among the OSM-extractable modes: `roads`, `railways`, `waterways`,
   `maritime`, `pipelines`. **`airways` cannot be extracted from OSM** (KI-07): offer it only as
   hand-built great-circle links between the main airports, or leave it out.
3. **Checkpoint**: confirm the mode list (and road detail level 1–4; default 1 = motorway+trunk,
   landlocked or sparse-network countries usually need 2–3).

### Phase 3 — trade geography & MRIO selection (workflow D + E + F2)

1. Draft the out-of-scope representation: every neighboring country individually, plus as few
   aggregated blocs as possible, each **directionally coherent** (a bloc's members must lie in
   broadly the same trade direction — e.g. for Central Asia, never merge Europe and China).
   Land-corridor blocs additionally need **corridor-basin coherence**: route choice is
   winner-take-all per OD, so a bloc whose members would use different corridors (or modes —
   e.g. Danube barge vs overland) must be split into sub-blocs, one per corridor bundle
   (recipes §1 "Corridor-basin sub-blocs"; Romania splits EUR five ways). Maritime blocs
   stay whole.
2. Run `python scripts/mrio_coverage.py --countries <scope+neighbors ISO3 list>` to get the
   coverage matrix across the four available databases. Quality order, subject to coverage:
   1. **FIGARO-REG** (2013; EU NUTS2 + 16 non-EU — grade-1 only for EU scopes),
   2. **OECD ICIO** (2016–2022; 80 economies),
   3. **EMERGING-E** (2018; 245 economies),
   4. **GLORIA** (160 regions + 4 continental aggregates).
   **Eora is NOT supported** by mrio-extractor (KI-06) — if the user expects it, apply the
   tool-issue protocol.
3. Present the D↔E trade-off in one table: for each candidate MRIO, which desired individual
   countries fall into ROW, and how blocs would be built from what the MRIO offers.
4. **Checkpoint** (two questions): (a) which MRIO + year; (b) for each out-of-scope country:
   internal region of the MRIO or member of an external trading bloc (workflow F2). Record the
   final `internal_regions`, `external_blocs` (bloc → member codes) in the manifest.

### Phase 4 — sector aggregation & MRIO extraction (workflow F1 + G)

1. Show the chosen MRIO's native sector list (from `references/tool-recipes.md` §sources or by
   reading the source labels). Suggest aggregation options — the usual one: **aggregate all
   service sectors into one**; also mention the shipped mappings (ICIO→15 GLORIA-aligned,
   EMERGING-E `group16`).
2. **Checkpoint**: sector aggregation (none / all-services / shipped mapping / custom), and the
   naming scheme for aggregated sectors (respect the reserved-word rule).
3. Edit the CONFIGURATION block of the relevant `extract_mrio_*.py` (recipes §1), run it from
   `MRIO\mrio-extractor`, then `diagnose_mrio.py` on the output. Snapshot the CONFIGURATION block
   into the manifest.
4. Build the sector table: `init_sector_table_config.py` → review/complete `sector_type` and
   `usd_per_ton` in the YAML (valid types: agriculture, mining, manufacturing, utility,
   construction, trade, transport, services) → `generate_sector_table.py --config`.
5. Copy outputs to `<Scope>/Economic/mrio.csv` and `<Scope>/Economic/sector_table.csv`.
6. Run `python scripts/check_scope.py <Scope> --economic-only` — fix any reserved-word collision
   or squareness error now, not in phase 7.

### Phase 5 — transport network build (workflow H) — only if with_transport

Follow recipes §2–3 exactly. Summary:
1. `python scripts/geofabrik.py list --iso3 <codes>` → pick PBFs; ask before downloading
   (state sizes). Multi-country scopes: prefer one covering Geofabrik region if the countries
   share one; otherwise download per-country and `geofabrik.py merge` (needs osmium on PATH).
2. `osm-extractor extract <pbf> <Scope>_raw.gpkg --modes <modes> --road-level <n> --report ...`
3. Per mode: `tnclean clean raw.gpkg clean.gpkg --input-layer <mode> --output-layer <mode>
   --cluster --cluster-eps 5000 --cluster-position centroid --simplify-tolerance 50
   --no-progress --report report_<mode>.json`
   - Start strong (eps = 5000 m) per the default policy; **pass cluster flags on the CLI, never
     via `--config`** (KI-08).
   - After each run read the report: edge count, and `cluster_max_extent` — DBSCAN clusters chain
     transitively (56 km max extent seen at eps 5 km); if the max extent swallows a structure that
     matters (an isthmus, a border corridor), redo with smaller eps or `--cluster-position medoid`.
   - Budget: tnclean with clustering is slow (~17 min for 10k edges) and fully in-memory.
4. `osm-extractor finalize clean.gpkg <Scope>/Transport/transport.gpkg` (adds the DisruptSC schema:
   id, type, km, name, class, surface, special, disruption).
5. Airways, if chosen: hand-build great-circle LineStrings between the main airports (from phase 2
   research) as an `airways` layer with `id, type, km, geometry`.
6. Multimodal: write `<Scope>/Transport/multimodal_config.yml` (recipes §4; one `networks` entry
   per mode with `anchor_strategy: degree_1_endpoints`, one `connections` entry per meaningful mode
   pair — roads–maritime and roads–railways ~10 km, pipelines ~5 km), then from `disrupt-sc-data`:
   `python build_transport.py <Scope>` → `multimodal.gpkg`. Record the connection pairs in the
   manifest — phase 7 derives the `logistics.dwell_times` / `loading_fees` keys from them.
7. Size gate: total `<Scope>/Transport/` must stay under **50 MB**; warn the user if exceeded and
   propose stronger clustering / higher road level threshold.

### Phase 6 — spatial disaggregation (workflow I + J)

1. **Checkpoint**: use firm/plant/grid-level production data for firms?
   - **Yes** → firm-level path (steps 6–9), which still uses steps 2–3 for admin
     boundaries and households, and falls back to the default per uncovered sector.
   - **No** → default path (steps 2–5 only).
2. Propose an admin level for disaggregation (admin-1 for most countries; admin-2 for small or
   data-rich ones; keep total points ~50–300 per country). **Checkpoint**: confirm level and the
   population source (user-supplied CSV per admin unit / a population field in the boundary file /
   uniform weights as last resort — say so explicitly if uniform).
3. `python scripts/build_spatial.py admin-fetch --iso3 <codes> --level <n> --out <dir>`
   (geoBoundaries gbOpen; ask before downloading), then
   `build_spatial.py households ...` → `<Scope>/Spatial/households.geojson`
   (Points at representative points, properties `region`, `population`, `subregion_admN`).
4. `build_spatial.py firms-default --households ... --sector-table ...` →
   `<Scope>/Spatial/firms.geojson` — the wide format: one column per sector of the point's region,
   value = population (DisruptSC melts columns matching MRIO sector names into firms).
5. **countries.geojson** (not optional — a missing bloc is a hard runtime failure): place one Point
   per external bloc/country of the MRIO, **directionally**: at the border crossing or port through
   which trade with that partner actually flows, and **near a roads edge** (points snap to the
   nearest roads node). Build a `bloc,lon,lat` CSV from phase-2/3 research, then
   `build_spatial.py countries --mrio ... --points ... --out <Scope>/Spatial/countries.geojson`.

**Firm-level path** (tool: `firm-extractor`, data library `<parent>/Firms/` — see its README
and `references/tool-recipes.md` §6):
6. `firm-extractor sources` (adapter/data inventory), then write the per-scope config from
   `firm-extractor/configs/example.yaml` — admin **polygons** from step 3, the scope's
   sector_table, households as fallback — and run `firm-extractor coverage <cfg>`. Present the
   sector×source proposal using the defensibility ladder: facility production > facility
   capacity > modelled activity (Climate TRACE) > sector grid (SPAM, EDGAR) > non-residential
   built volume (GHS NRES) > population fallback.
7. **Checkpoints**: source per sector; grid placement rule (`weighted_centroid` default /
   `max_cell` / `representative_point`); review the concordance CSVs — copy and rewrite their
   `sector` column whenever the scope aggregates or renames sectors (watch jasansky's
   `proc:Processing` hitting the `proc:*` wildcard); approve any dataset fetches (GEM trackers
   are form-gated — the user downloads them into `<parent>/Firms/GEM/`).
8. `firm-extractor build <cfg>` → long-format firms.geojson + `*_coverage.csv`. Copy to
   `<Scope>/Spatial/firms.geojson`; snapshot the config and coverage table into the manifest
   under `firm_level:`.
9. Validate: `check_scope.py` (long form accepted), coverage shares sanity-checked against
   national totals (USGS/FAO/national statistics — web-check), and note the point weights now
   set firm sizes, not just locations (KI-17, disrupt-sc ≥ 2026-08-31).

### Phase 7 — assemble, validate, run (workflow K)

1. Generate `config/user_defined_<Scope>.local.yaml` in the disrupt-sc repo, starting from the
   committed Testkistan template (`config/user_defined_Testkistan.yaml`), setting:
   `scope filepaths` (only real keys: mrio, sector_table, households_spatial, firms_spatial,
   countries_spatial, transport, multimodal), `transport_modes`, `monetary_units_in_data`
   (mUSD for ICIO/EMERGING-E/GLORIA, mEUR for FIGARO), `time_resolution`,
   `simulation_type: initial_state`, `flow_coverage` (start 0.9), `with_transport`, and
   `logistics.speeds` / `logistics.basic_cost` for **every** enabled mode plus
   `logistics.dwell_times` / `loading_fees` for every `multimodes` string produced in phase 5.
2. `python scripts/check_scope.py <Scope>` — deep validation (squareness, reserved words, sector
   types, countries↔MRIO match, per-mode and combined connectivity, config coverage). Fix all
   ERRORs; surface WARNs to the user.
3. `validate-inputs <Scope>` (file-existence only; a spurious warning about the missing committed
   `.yaml` is KI-01).
4. `disruptsc <Scope> --simulation_type initial_state --open` from the disrupt-sc repo.
5. On failure, triage with `references/failure-triage.md` (the most common new-scope blocker is a
   multi-component transport network → unreachable commercial links). Iterate.
6. On success: sanity-report to the user — total output, household consumption, share of flows
   routed per mode — and mark the manifest complete.

### Phase 8 — validation report (model vs data)

Full method in `references/validation-report.md`; Romania
(`disrupt-sc-data/Romania/validation_report.md`) is the worked example.

1. Rerun `initial_state` with `export_files: True` if the phase-7 run didn't export
   (`--open` forces it since KI-15).
2. `python scripts/validation_metrics.py <Scope>` — deterministic model-side numbers:
   model vs MRIO (totals + per-sector outliers), per-partner kept shares (the
   flow_coverage budget distortion shows up here first), gateway shares model vs
   MRIO-implied, modal split in ton-km, connector activity, top throughput nodes.
3. Research the data-side anchors (source table in the reference): national modal split,
   trade by partner/mode, port and border statistics, sub-national GDP. Label
   approximate anchors as anchors. For EU scopes, compute commodity-level mode-choice
   targets with `python scripts/eurostat_mode_targets.py --geo <XX> --year <YYYY>
   --out <data-root>/<Scope>/mode_split_targets_<XX>_<YYYY>.csv --compare <run
   edges_with_flows geojson>` — per-NST and per-cargo-type shares + mean hauls are the
   calibration targets for `logistics.basic_cost`/`dwell_times` (aggregate splits are
   under-identified).
4. Write the report — §1 economic (model vs MRIO, MRIO vs official), §2 flow assignment
   (modal split, import/export gateway %, hubs), §3 **prioritized calibration
   recommendations** (parameter → dataset → expected effect; structural fixes before
   parameter tuning before data upgrades).
5. Deliver `<data-root>/<Scope>/validation_report.md` (plus a shareable rendered page if
   the assistant supports publishing one); record run folder, verdicts, and top
   recommendations under `p8_validation` in the manifest.

## Manifest schema

```yaml
# <data-root>/<Scope>/scope_manifest.yaml
scope: CentralAsia
countries: [KAZ, KGZ, TJK, TKM, UZB]
created: 2026-08-27
phases:            # pending | in_progress | done (+ date)
  p1_scope: done
  p2_modes: done
  p3_trade_geography: in_progress
  p4_mrio: pending
  p5_transport: pending
  p6_spatial: pending
  p7_run: pending
  p8_validation: pending   # validation report; see references/validation-report.md
decisions:
  with_transport: true
  transport_modes: [roads, railways]
  road_level: 2
  mrio: {database: ICIO, year: 2021}
  internal_regions: [KAZ, KGZ, TJK, TKM, UZB, RUS, CHN]
  external_blocs: {EUR: [DEU, FRA, ...], EAS: [JPN, KOR], ROW: [...]}
  sector_aggregation: all_services_into_SER
  cluster_eps_m: 5000
  admin_level: 1
  population_source: "user CSV national stats 2023"
mrio:
  config_snapshot: |
    # exact CONFIGURATION block run in extract_mrio_oecd.py
multimodal_connections: [roads-railways]
tool_issues:
  - id: KI-12
    date: 2026-08-27
    summary: "..."
    decision: fix|workaround|defer
```

## Optional per-machine shim for Claude Code

This runbook is assistant-neutral and fully versioned here. Claude Code users who want
the `/new-scope` slash command and automatic triggering can create the following
(untracked, gitignored) file at `.claude/skills/new-scope/SKILL.md`:

```markdown
---
name: new-scope
description: Semi-automated calibration of DisruptSC to a new scope (a country or group of countries), through MRIO extraction, transport network build, spatial disaggregation, an initial_state run, and a validation report. Trigger when the user wants to apply DisruptSC to a new country or region ("apply disrupt-sc to X", "new scope for X", "onboard country X", "calibrate the model to X") or wants a validation report for an existing scope.
---

Read `onboarding/RUNBOOK.md` at the repo root and follow it. Its references live in
`onboarding/references/`, its helper scripts in `onboarding/scripts/`.
```

Other assistants discover this runbook through `AGENTS.md`.
