# Architecture

How the v2 runtime is organized and what happens in a run. This page
describes the code as it is — module paths are real and clickable in the
repository.

!!! note
    The former multi-page architecture section described the v1 codebase
    (`Model` class, `DisruptionFactory`, `simulation/` package) and was
    removed rather than left to mislead. This page is the v2 reference.

## Module layout

```text
src/disruptsc/
├── run.py                 # CLI entry point + execute(): the cached, exporting pipeline
├── build.py               # no-cache builder for programmatic drivers (studies, tests)
├── config.py              # YAML loading (default → scope → .local → CLI), param building
├── params.py              # frozen dataclasses: TransportParams, SimParams, AgentParams, LogisticsParams
├── paths.py               # data-root resolution (env var → sibling repo → bundled examples)
├── validate_inputs.py     # `validate-inputs <scope>` content checks
├── init_pipeline/         # build stages
│   ├── load_data.py       #   MRIO, sector table, flow-coverage Selection
│   ├── transport.py       #   transport.gpkg + multimodal.gpkg → TransportNetwork
│   ├── agents.py          #   firm/household/country creation + spatial disaggregation
│   ├── supply_chain.py    #   supplier selection → ScNetwork (the RNG-driven stage)
│   └── routing.py         #   initial route assignment (heuristic / candidate-path LP / edge LP)
├── run_pipeline/          # execution stages
│   ├── simulate.py        #   set_initial_conditions + the time-step loop
│   ├── disruption.py      #   disruption parsing/applying + reconstruction market
│   ├── cache.py           #   scope-keyed, fingerprint-validated pickle caches
│   ├── fingerprint.py     #   run provenance + per-stage cache fingerprints
│   └── export.py          #   CSV/GeoJSON writers, loss summaries
├── agents/                # Firm, Household (+ Government/Investment), Country, transport_utils
├── network/               # Mrio, ScNetwork, TransportNetwork, CommercialLink, Route
└── reporting/             # HTML reports (initial_state, disruption)
```

## A run, end to end

`execute()` in `run.py` orchestrates five stages, each cacheable
(`--cache` presets) and each validated against a per-stage configuration
fingerprint on reload:

1. **Transport network** — build the multimodal graph from the GeoPackage,
   ingest per-edge costs and capacities.
2. **Agents** — filter the MRIO with `flow_coverage` (a symmetric
   per-buyer/per-supplier top-cells rule producing a `Selection`), create
   firms (spatially disaggregated where `firms_spatial` provides locations),
   households (population-weighted final demand), single national
   government/investment agents, and country agents for external trade.
3. **Supply-chain network** — every buyer selects suppliers per input with
   probability ∝ importance / distance^w. This is the seeded, RNG-driven
   stage: same `seed` → same network.
4. **Initial conditions + routes** — solve the sparse Leontief system for
   equilibrium production, initialize inventories, capital (split
   active/idle by `utilization_rate`), finance, and orders; then assign
   logistic routes (Dijkstra, or capacity-aware LP when
   `capacity_constraint` is on).
5. **Simulation** — the time-step loop below, for `initial_state`,
   `disruption`, or `criticality`.

Programmatic drivers (the studies, the tests) use `disruptsc.build`
(`build_common` + `build_agents`) instead of `execute()` and can trace every
step through the `observer` callback that all simulate runners accept.

## The time step

Each step in `run_pipeline/simulate.py::_run_one_time_step`:

1. apply disruptions starting this step; place reconstruction demand;
2. firms retrieve the orders placed **last** step (the order book);
3. firms plan production (target = orders − stock) and prices;
4. idle capital is mobilized toward the target (rate-limited by
   `time_to_activate_idle_capital`);
5. all agents send **next** step's purchase orders;
6. firms produce under Partially-Binding Leontief: critical inputs bind
   output hard, "important" inputs bind softly, immaterial inputs
   (cost share below `critical_input_threshold`) never bind;
7. countries then firms deliver against the retrieved order book, rationing
   when stock is short (`equal` or `household_first`); shipments traverse
   the transport network (or bypass it for service sectors / transport-off
   runs), rerouting around disrupted edges when an acceptable alternative
   exists;
8. reconstruction converts leftover capital-good output into rebuilt
   capital; supplier satisfaction (delivery / served order) updates for
   adaptive substitution;
9. agents receive products; households consume; losses (consumption loss +
   extra spending) accumulate;
10. transport loads reset; profits are evaluated; disruption recovery ticks.

Two timing facts worth knowing when reading results: domestic supply
responds to orders with a one-step lag (order placed at *t* is delivered at
*t+1*), while country agents — unlimited external supply — deliver the order
placed in the same step; and welfare is households only — the national
government and investment agents share the household machinery but are
excluded from the headline loss.

## Disruptions and recovery

`run_pipeline/disruption.py` parses the `disruptions:` block into objects:

- **transport_disruption** — closes/derates edges by id or attribute, with
  threshold/linear/exponential capacity recovery;
- **transport_disruption_probability** — probabilistic arrivals over a
  scenario horizon (drawn from the seeded RNG);
- **capital_destruction** — fractional (via `filter:`) or absolute per
  canton × sector (`description_type: subregion_file`), destroying active
  and idle capital alike. Absolute shocks recover only through the
  **reconstruction market**: damaged firms demand capital-good output
  (split CON/MAN/IMP by `capital_input_mix`, localized by
  `reconstruction_locality`, partly public via
  `reconstruction_public_share`), and delivered output rebuilds capital
  over `reconstruction_target_time`;
- **productivity_shock** — a temporary TFP-style capacity reduction.

Firm-side timed recovery is threshold-only (full restoration when the
duration elapses); transport-edge recovery supports shapes.

## Reproducibility

- `seed` drives supplier selection and Monte-Carlo disruption arrivals;
  MC repetition *i* re-seeds with `seed + i`.
- Every exporting run writes `parameters.yaml`, `run_fingerprint.json`
  (version + git SHA + watermarked config keys), and `exp.log`.
- Pickle caches are keyed `<scope>_<stage>.pkl` and store a per-stage
  fingerprint; a cache built under different watermarked settings is
  refused with a key-level diff.
- `set_initial_conditions` fully resets a build between runs (link state,
  learned supplier satisfaction, disruption and reconstruction leftovers,
  prices), so one build can host many runs.

## See also

- [Parameters](../user-guide/parameters.md) — every knob with defaults
- [MRIO Specification](../MRIO_SPECIFICATION.md) — the input-table format
- [Criticality Analysis](../user-guide/criticality.md) — resumable edge sweeps
