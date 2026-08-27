# AGENTS.md

Briefing for AI assistants (and new collaborators) working in this repository.
It describes the **v2** codebase; if something here disagrees with the code,
the code wins — and this file should be fixed in the same commit.

## What this is

DisruptSC is a **research model**, not a software product: a spatial
agent-based model of supply-chain disruptions (firms, households, countries
on a multimodal transport network, calibrated from MRIO tables). Correctness
of results, reproducibility, and provenance outrank software polish. Do not
"improve" model behavior without being asked — a changed number is a changed
scientific result.

## Running

```bash
disruptsc <scope>                          # or: python -m disruptsc.run <scope>
disruptsc Testkistan                       # bundled demo (examples/data/Testkistan)
disruptsc <scope> --simulation_type disruption --duration 12 --seed 42
disruptsc <scope> --cache same_logistic_routes --cache_isolation
validate-inputs <scope>                    # content checks before a run
pytest                                     # works from a bare clone (53 tests)
```

Scopes are configured in `config/`: `default.yaml` → committed
`user_defined_<scope>.yaml` → gitignored `user_defined_<scope>.local.yaml`
(machine-specific overrides) → CLI flags. Data lives in a separate repo,
resolved `DISRUPT_SC_DATA_PATH` → sibling `../disrupt-sc-data` → bundled
`examples/data/`. Filepaths resolve against `<data-root>/<scope>/`; a
`repo:<relpath>` value resolves against this code repo instead.

## Layout (src/disruptsc/)

| Module | Role |
|---|---|
| `run.py` | CLI + `execute()`: the cached, exporting pipeline |
| `build.py` | no-cache builder for programmatic drivers (`build_common` + `build_agents`) |
| `config.py`, `params.py` | YAML loading; frozen param dataclasses (Transport/Sim/Agent/Logistics) |
| `init_pipeline/` | load_data (MRIO + `flow_coverage` Selection), transport, agents, supply_chain (the RNG stage), routing (LP/heuristic route assignment) |
| `run_pipeline/` | simulate (time loop + `set_initial_conditions`), disruption (+ reconstruction market), cache, fingerprint, export |
| `agents/` | `Firm`, `Household` (+ national Government/Investment agents), `Country`, shared transport utils |
| `network/` | `Mrio`, `ScNetwork`, `TransportNetwork`, `CommercialLink`, `Route` |
| `reporting/` | HTML reports (`--open`) |

Simulation types: `initial_state`, `disruption`, `criticality` (resumable,
fingerprint-keyed subfolders). Docs: `docs/architecture/index.md` for the
run/time-step walkthrough, `docs/user-guide/parameters.md` for every knob,
`docs/MRIO_SPECIFICATION.md` for the input format.

## Invariants to preserve (the load-bearing ones)

- **Reproducibility**: `seed` is applied once at the top of `execute()` (or in
  `build_agents`); the only RNG stages are supplier selection and Monte-Carlo
  disruption arrival. MC repetition *i* re-seeds with `seed + i`. Never add
  RNG consumption before the supply-chain build — it would shift every
  seeded network.
- **Conservation**: deliveries are computed against the **order book**
  retrieved at the start of the step (`link.served_order`), never against
  `link.order`, which mid-step already holds the *next* step's order. Stock
  deductions use `realized_delivery`. `tests/test_testkistan_pipeline.py`
  pins these ledgers — keep it passing.
- **Reset between runs**: `set_initial_conditions` must restore a build to
  the exact fixed point (link state, supplier satisfaction, disruption and
  reconstruction leftovers, prices). Anything a run mutates on agents must be
  reset there.
- **Caches** (`tmp/<scope>_<stage>.pkl`) store per-stage config fingerprints
  and are refused on mismatch. If you add a config key that changes what a
  build stage produces, add it to `_STAGE_CONFIG_KEYS` in
  `run_pipeline/fingerprint.py` (and to `WATERMARKED_CONFIG_KEYS` if it
  belongs in run provenance).
- **Welfare vs accounting**: the national government/investment agents live
  in the household dict but carry `agent_type != "household"` and are
  excluded from the household-loss headline. Keep that filter everywhere
  losses are aggregated.
- **Config hygiene**: every YAML key must be consumed by `build_params` or
  warned about (`_INERT_KEYS`); unknown values of scientific switches raise.
  Don't add silently-defaulting keys.
- **Units**: config durations (`inventory_restoration_time`,
  `time_to_activate_idle_capital`, `reconstruction_*`) are in **days**,
  converted to time steps via `time_resolution`. Monetary units are set by
  `monetary_units_in_data` / `_in_model`.

## Studies (`studies/`)

Paper pipelines drive the model programmatically: build once via
`disruptsc.build`, run many `run_disruption` calls, trace per-step state via
the `observer` callback every simulate runner accepts (never monkeypatch
`_run_one_time_step`). The active earthquake paper lives in
`studies/earthquake/paper/` (SLURM launchers + runners + analyze/plot);
its scope config is the committed `config/user_defined_EcuadorEQ.yaml`.
The heterogeneity draw list under `studies/earthquake/additional_data/`
is **committed experimental design**: `run_hetero.py` derives the destroyed
total from it and refuses a mismatching `--total`.

## Conventions for changes

- Ask before substantial changes to model logic or architecture; bug fixes
  and small features are fine. When the user says "think", "assess", or
  "investigate": analyze and report, do **not** implement.
- Commit messages state what changed *and why it matters for results*
  (see `git log` for the house style). The user pushes; you commit locally.
- Comments carry economic rationale and provenance (dates, magnitudes,
  rejected alternatives) — match that standard; don't strip it.
- Every exporting run writes `parameters.yaml`, `run_fingerprint.json`
  (git SHA), and `exp.log`. Don't break these provenance channels.
- Tests: `pytest` from the repo root. Leaf-unit tests plus the Testkistan
  pipeline tests; anything touching production/delivery/reset logic should
  keep or extend the ledger tests.
