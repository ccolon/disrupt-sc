# Criticality Analysis

Criticality analysis tests how much economic loss a disruption to specific
transport infrastructure would inflict. DisruptSC runs one disruption
*scenario* at a time — shutting down one or more edges for a fixed
duration — and records the cumulated household and country losses.

You can run it in two flavours:

1. **Scenario list** — you list the scenarios explicitly; one scenario can
   shut down one edge or many edges at once.
2. **Flow-ranked edge loop** — for a quick sweep, the model ranks every
   transport edge by baseline flow and shuts each one in turn. You can
   filter (by attribute, by zero-flow, by top-N) before the loop runs.

Both modes share the same output schema, fingerprint, and resume
behavior — they only differ in which edges they iterate over.

## Quick start

```yaml
# config/user_defined_<scope>.local.yaml
simulation_type: criticality
t_final: 12              # how long each scenario simulates (time steps)

criticality:
  duration: 4            # how long each disruption lasts
  scenarios: []          # leave empty for flow-ranked mode
  skip_zero_flow: true   # drop edges with no baseline traffic
  top_n: 50              # null = all surviving edges

seed: 42                 # optional but recommended (see below)
```

```bash
disruptsc <scope> --simulation_type criticality
```

## Mode A — scenario list (recommended for targeted studies)

When you know which edges you want to test (a port, a strait, a corridor),
list them explicitly. Each inner list is **one scenario** — every edge in
that list is shut down together:

```yaml
simulation_type: criticality
t_final: 12

criticality:
  duration: 4
  scenarios:
    - ["Strait of Hormuz"]
    - ["port_fujairah"]
    - ["Strait of Hormuz", "port_fujairah"]   # both shut simultaneously
```

Edge names are matched against the `name` column of the transport edges
GeoPackage. Unknown names raise an error at startup so you don't waste a
multi-hour run on a typo.

In scenario mode, the flow-ranking knobs (`skip_zero_flow`, `top_n`,
`attribute`, `edges`) are **ignored** — your list is your list.

## Mode B — flow-ranked edge loop (sweep mode)

Leave `scenarios: []` (or omit it) to enter the loop. The model:

1. Optionally **pre-filters** edges via `attribute` + `edges`:
   ```yaml
   criticality:
     attribute: "type"
     edges: ["maritime"]   # test only maritime edges
   ```
2. Runs the baseline (no disruption) and reads each edge's tons flow.
3. **Drops zero-flow edges** when `skip_zero_flow: true` (default) — no
   point disrupting an edge nobody uses.
4. **Sorts descending by baseline flow.**
5. Truncates to `top_n` when set (default `null` = keep all).

Then it loops, shutting each surviving edge in turn for `duration` time
steps, and writing one CSV row per edge.

Typical workflow for a large network:

```yaml
simulation_type: criticality
t_final: 8
criticality:
  duration: 4
  skip_zero_flow: true
  top_n: 100               # focus on the 100 highest-tonnage edges
```

You'll see lines like:

```
Skipped 4 813 zero-flow edges
Restricted to top 100 edges by baseline flow
Running criticality for 100 edge(s) (of 100 selected, 0 already done)
Criticality edge 1/100: id=2734 (baseline tons=1 247 562.4)
…
```

## How long does each scenario run?

For each scenario:

1. The model resets to IO equilibrium.
2. At `t = 0` it runs the baseline (undisrupted) step.
3. At `t = 1` the disruption starts; it lasts for `duration` time steps.
4. The simulation continues until `t = t_final`.

`t_final` should be **larger than `duration`** so the economy has time to
recover — otherwise you only see the immediate hit, not the recovery
cost. A common pattern is `t_final = 2 × duration` (or larger for sectors
with long inventory targets).

!!! note "Epsilon-stop is disabled in criticality mode"
    For [disruption mode](basic-usage.md#disruption), the simulation can
    cut short via `epsilon_stop_condition` once households and countries
    return to equilibrium. **In criticality mode this is disabled by
    design** — every scenario runs the full `t_final` steps so losses
    are comparable across edges.

## Output files

Results are written to a **stable** per-scope folder (no timestamp):

```
output/<scope>/criticality/
├── criticality_results.csv             # one row per scenario / edge
├── criticality_results.geojson         # scenario mode only: edges with loss attributes
└── criticality_results.fingerprint.json  # state watermark for resume
```

**CSV schema (scenario mode):**

| Column | Meaning |
|---|---|
| `edge` | JSON list of edge names in the scenario |
| `total_household_loss` | Sum of household extra-spending + consumption-loss (mUSD) |
| `household_loss_per_region` | JSON dict of region → loss |

**CSV schema (flow-ranked mode):**

| Column | Meaning |
|---|---|
| `edge_id` | Integer id from `transport_edges` |
| `household_loss` | Cumulated household loss (mUSD) |
| `country_loss` | Cumulated country loss (mUSD) |

To archive a finished study, **rename or copy the folder** before the
next launch (e.g. `mv criticality criticality_2026-06-baseline`). The
next run will then start fresh in `criticality/`.

## Reproducibility — seed + fingerprint

The supply-chain network is the only part of the model that uses
randomness (firms picking suppliers, countries picking exporters). Two
runs with the same MRIO+config but no seed will produce slightly
different criticality results because they'll have slightly different
supply chains.

**Set `seed:` to make the run deterministic** — the same MRIO+config
will produce the exact same agent set, supply chain, and criticality
losses every time. This is essential for resumable sweeps:

```yaml
seed: 42                 # any integer; null disables seeding (legacy behavior)
```

## Resume — picking up after a crash

DisruptSC writes one CSV row per completed scenario. If a long sweep
crashes (out of memory, killed by your scheduler, laptop closed), just
relaunch with the same config — the model:

1. Computes the current **fingerprint** (a hash of code version, seed,
   filepaths, and the config keys that affect model state).
2. Compares it against `criticality_results.fingerprint.json` from the
   prior run.
3. **If the fingerprints match**, reads the existing CSV, builds the
   set of already-completed scenarios, skips those, and appends new
   rows for the rest:
   ```
   Resuming criticality from criticality_results.csv: 47 scenario(s) already complete
   Running criticality for 53 edge(s) (of 100 selected, 47 already done)
   ```
4. **If they don't match**, the run aborts with a hard error and a
   precise diff:
   ```
   RuntimeError: Cannot resume criticality results at .../criticality_results.csv:
   the current run's fingerprint differs from the previous one.
   Either delete .../criticality to start fresh, or revert config/data to match.
   Changed keys:
     config.seed: was=42  now=43
   ```
   Two ways to recover:
     - Revert the config/data change.
     - Delete the `criticality/` folder to start over.

### What's in the fingerprint?

The fingerprint hashes:

- Code version (`disruptsc.__version__` + git SHA when available).
- The `seed` value.
- All config keys that change the agent set or routing problem:
  `flow_coverage`, `sectors_to_include`, `sectors_to_exclude`,
  `countries_no_transport`, `use_cargo_types`, `transport_modes`,
  `capacity_constraint`, `time_resolution`, `monetary_units_*`,
  `nb_suppliers_per_input`, the full `logistics` block, etc.
- The **filepaths** of input data (MRIO, transport, spatial files) —
  **not** their contents. If you change a data file's contents without
  renaming it, the model won't notice. *Rename the file* when you
  produce a new version (e.g. `mrio_v1.csv` → `mrio_v2.csv`).
- The `criticality.duration` (because loss numbers depend on it).

The sidecar JSON is human-readable — open it to see exactly what was
recorded.

### What is **not** in the fingerprint?

- The list of scenarios or edges. You can extend `criticality.scenarios`
  between runs — the model will just run the new entries and append.
  Similarly, raising `top_n` from 50 to 100 will run the 50 extra edges
  without re-running the first 50.
- The simulation length `t_final`. Be careful here — if you change
  `t_final`, the existing rows were computed with the old value and
  won't match new rows. The fingerprint doesn't catch this. Stick to a
  consistent `t_final` per study.

## Caching

Criticality respects the standard `--cache` presets just like the other
simulation types. For a typical workflow:

```bash
# First run: build everything fresh, run criticality
disruptsc <scope> --simulation_type criticality

# Tweak only the criticality config (e.g. raise top_n) → reuse cached agents,
# SC network, and routes
disruptsc <scope> --simulation_type criticality --cache same_logistic_routes
```

The cached `tmp/` artefacts (transport network, agents, SC network,
logistic routes) are written *before* the criticality loop starts, so a
mid-loop crash leaves them intact — the next launch loads them
instantly. Combined with resume, you can interrupt and continue a
multi-hour sweep with zero rebuilt setup.

!!! warning "Cache is not the same as fingerprint"
    `--cache` controls *which initialization stages are skipped*. The
    fingerprint controls *whether the existing criticality_results.csv
    can be trusted*. They're independent — a fingerprint mismatch will
    still abort even if you used `--cache same_logistic_routes`.

## Practical example: a global maritime sweep

```yaml
# user_defined_World.local.yaml
simulation_type: criticality
t_final: 8
seed: 42

criticality:
  duration: 4
  attribute: type
  edges: [maritime]      # only maritime edges
  skip_zero_flow: true
  top_n: 200             # the 200 busiest maritime edges
```

```bash
disruptsc World --simulation_type criticality
# Crashes after 73 edges? Just relaunch:
disruptsc World --simulation_type criticality --cache same_logistic_routes
# Picks up at edge 74, finishes the remaining 127.
```

Final outputs live at
`output/World/criticality/criticality_results.csv` — one row per edge,
sorted descending by baseline tonnage.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `RuntimeError: Cannot resume … fingerprint differs` | A config key, seed, or input filepath changed. Read the `Changed keys:` block and either revert or delete `criticality/`. |
| `criticality.scenarios[i] contains unknown edge name(s): [...]` | Typo in an edge name, or the transport gpkg doesn't carry the `name` column for that edge. |
| Every scenario shows `household_loss = 0` | Your `duration` is too short or `t_final - duration` leaves no time for downstream effects. Try `duration: 4, t_final: 12`. |
| `Skipped N zero-flow edges` where N is huge | The baseline routing decided most edges carry no flow. Sanity-check your transport network for disconnected components or wrong capacities. |
| Resume isn't kicking in | Check that `output/<scope>/criticality/criticality_results.fingerprint.json` exists. If absent, the prior run died before writing it. |
