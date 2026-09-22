# Parameters

DisruptSC v2 uses YAML configuration files in `config/`.

## Load Order

1. `config/default.yaml` (shipped)
2. `config/user_defined_<scope>.yaml` (optional, committed — the scope's shared configuration)
3. `config/user_defined_<scope>.local.yaml` (optional, gitignored — machine-specific overrides)
4. Supported CLI overrides

Keep science parameters in the committed scope file so they travel with git;
use the `.local` file for absolute paths and personal experiments.

Supported CLI overrides are:

```bash
disruptsc Cambodia --simulation_type disruption --duration 90 --flow_coverage 0.95 --seed 42
```

## Core Parameters

```yaml
simulation_type: "initial_state"
t_final: 10                 # in time_resolution units
time_resolution: "week"     # day | week | month | year
export_files: false
seed: null                  # integer -> reproducible supplier selection + MC draws
```

Supported `simulation_type` values in the current v2 runtime:

| Type | Purpose |
|------|---------|
| `initial_state` | Baseline run without configured disruptions. |
| `disruption` | Run configured transport, capital, or productivity disruptions. |
| `criticality` | Run infrastructure criticality scenarios. |

## Data Parameters

```yaml
firm_data_type: "mrio"
monetary_units_in_model: "mUSD"
monetary_units_in_data: "mUSD"
```

The current v2 runtime supports MRIO mode. Transaction-based firm creation is
not implemented.

File paths are relative to the scope folder in the resolved data root. A
`repo:<relpath>` value resolves against the **code repository** instead — use
it for inputs committed with the code (e.g. an input-criticality matrix under
`studies/`). Absolute paths pass through unchanged.

```yaml
filepaths:
  transport: "Transport/transport.gpkg"
  multimodal: "Transport/multimodal.gpkg"
  mrio: "Economic/mrio.csv"            # .csv or .parquet
  sector_table: "Economic/sector_table.csv"
  households_spatial: "Spatial/households.geojson"
  countries_spatial: "Spatial/countries.geojson"
  firms_spatial: "Spatial/firms.geojson"
  # Optional: adapted-Leontief criticality matrix (see production function)
  input_criticality: "repo:studies/earthquake/additional_data/input_criticality.csv"
```

## Agent And Supply Chain Parameters

Agent and link filtering is controlled by **one knob**:

```yaml
flow_coverage: 0.95
```

For each MRIO buyer column *and* each supplier row, cells are kept largest-first
until their cumulative share reaches `flow_coverage`; the union of the two kept
sets defines which region-sectors, external countries, and bilateral flows are
modeled. Every kept agent retains at least this fraction of both its in-flows
and its out-flows. Range `(0, 1]`; typical values 0.7 (sparse, fast) to 0.99
(dense, slow). It replaces the legacy `input_coverage` / `cutoff_*` knobs,
which are ignored with a warning.

```yaml
nb_suppliers_per_input: 1      # 1, 2, or a fraction in (1,2) = stochastic 1-or-2 mix
weight_localization_firm: 1    # supplier choice ~ importance / distance^w
weight_localization_household: 4
utilization_rate: 0.8          # eq output / production capacity; sets the idle-capital buffer
time_to_activate_idle_capital: 30   # DAYS to mobilize idle capital (must exceed one time step)
capital_to_value_added_ratio: 3     # capital stock = ratio x annual value added
critical_input_threshold: 0.0  # Partially-Binding Leontief materiality floor (0 = strict)
sectors_to_include: "all"
sectors_to_exclude: null
```

## Inventory Parameters

All durations are in **days** and converted to time steps internally.

```yaml
inventory_duration_targets:      # firm input buffers, keyed on sector_table 'type'
  definition: "per_input_type"
  unit: "day"
  values:
    default: 30
inventory_restoration_time: 30   # DAYS to close the inventory gap (smaller = more aggressive)
enable_household_inventories: false
household_inventory_duration_target:   # separate retail/pantry scheme; see default.yaml
  definition: "per_input_type"
  unit: "day"
  values:
    default: 7
adaptive_inventories: false      # true -> targets track current orders instead of equilibrium
adaptive_supplier_weight: false  # true -> orders shift toward suppliers that deliver
capacity_constrained_orders: false  # true -> capacity-hit firms stop over-ordering inputs
```

## Transport Parameters

```yaml
with_transport: true
transport_modes: ["roads", "maritime"]
transport_to_households: true
use_route_cache: true
use_cargo_types: true            # false -> one "any" cargo bucket, ~N x faster routing
capacity_constraint: false       # true: the within-step capacity gate on the edges named in transport_capacity_overrides
price_increase_threshold: 2      # give up delivery if rerouting cost rises beyond this factor
delivered_price_increase_threshold: null   # if set (e.g. 0.5): give up only when transport_share x relative
                                           # cost increase exceeds it (delivered price +50%); replaces the rule above
sectors_no_transport_network: ['utility', 'transport', 'trade', 'services', 'service', 'construction']
countries_no_transport: []       # country pids whose flows bypass the network entirely
country_attachment: roads        # roads (nearest road node) | any (sea-placed blocs attach to maritime nodes)
agent_attachment: any            # firms/households: any (legacy, nearest node of any mode) | roads (first/last mile by road)
```

`logistics.cost_of_time` (USD per ton-hour) is a scalar, a per-cargo dict
(`{container: 1.6, dry_bulk: 0.08, default: 2.0}`), or per cargo **and per mode**
(`{container: {default: 1.6, maritime: 0.15}, ...}`): the inland value stands in
for service quality and separates road from rail; the sea leg gets its own, lower
value so that a longer voyage to a bigger port is not priced like a slow inland mode.

```yaml
pipelined_flows:                 # optional: products that reach their buyers by pipeline
  products: [B06]                # sector codes (crude oil and natural gas)
  # buyer_sectors: [C19, D]      # optional: restrict the rule to these buyers
```

`pipelined_flows` marks the share of every commercial link that travels by
pipeline, which the transport network does not carry: 1 for a link whose product
is one of `products`, the products' MRIO composition share for an import bundle
(`{BLOC}_imports`). That share is delivered without transport at the supplier's
price whatever the network does to the rest (a pipeline is neither disrupted nor
a back-up); the routed remainder follows the usual rules. The rule is applied on
every cache load, not baked into the caches. The routing summary reports the
pipelined value (`pipelined_usd`) and the link table the pipelined part of each
delivery (`pipelined_delivery`); `delivery_in_tons` is the tonnage actually
placed on the network.

Transport networks are loaded from a GeoPackage configured by
`filepaths.transport`. Layer names should match `transport_modes`.

### Edge capacities and the capacity gate

```yaml
capacity_constraint: true
transport_capacity_overrides:        # tons per DAY, by edge NAME (the 'name' column of the GeoPackage layers)
  strait_of_hormuz: 3000000          # shared across cargo types
  port_jebel_ali: {container: 450000, dry_bulk: 80000, liquid_bulk: 200000}
  oil_terminal_x: {liquid_bulk: 120000, container: 0}   # 0 blocks the cargo; a cargo not listed has no capacity there
cargo_mode_eligibility:              # which cargo types may use which mode; a mode not listed takes every cargo
  airways: [container]
  pipelines: [liquid_bulk]
```

An edge has a capacity **only if `transport_capacity_overrides` names it**; every
other edge is unconstrained (there are no per-mode default capacities since
21 Sep 2026). Every edge carrying the name gets the value (a terminal usually has
a road and a rail connector), two-way. A name that matches no edge, an unknown
cargo type or a negative value raises, at build time and in `validate-inputs`.
`cargo_mode_eligibility` is the eligibility part of the former
`default_transport_capacity` block: a cargo that may not use a mode gets no cost
label on its edges, so routing never uses them for it.

With `capacity_constraint: true` the capacities act through the **within-step
capacity gate** (`run_pipeline/capacity_gate.py`; design and review in
`docs/architecture/transport-capacity.md`). The initial routes are the plain
cheapest paths (a capacity below an edge's baseline load is reported per edge
and in `baseline_capacity_check.csv`; the gate rations that edge from t = 0).
In every step, after all agents have shipped: a saturated edge cuts the
shipments placed in the current round proportionally so that it is exactly
full, shipments accepted in earlier rounds keep their allocation (existing
customers before diverted traffic), the saturated edge is excluded from the
rest of the step's searches, and each cut share looks for a route avoiding the
saturated edges with the usual rules (own modes first, switching penalty,
`price_increase_threshold` / `delivered_price_increase_threshold` on that
share). Rounds repeat until no gate cuts, at most one more than the number of
capacitated edges. What finds no acceptable route stays in the supplier's stock
and is reported as `capacity_blocked` on the link (`capacity_blocked_usd` in
`routing_summary.csv`, `offered_tons` / `withheld_tons` per monitored edge in
`logistics_report.csv`). On-off: no cost depends on load, and the outcome does
not depend on the order in which agents deliver.

A `transport_disruption` with `capacity_reduction` below 1 scales the capacity
of a named capacitated edge (the gate then rations it); on an edge without a
capacity only a full reduction, a closure, has an effect.

The former `capacity_constraint: gradual | binary` modes, the capacity-aware
initial assignments (`logistics.initial_route_assignment`, `chunk_size`,
`route_candidate_*`, `lp_*`, `capacity_routing_max_iterations`) and
`default_transport_capacity` raise with a pointer to the
`legacy/v2-capacity-routing` branch, where that code is archived.

## Disruptions

```yaml
simulation_type: "disruption"
disruptions:
  - type: "transport_disruption"
    attribute: "name"
    values: ["road_1"]
    start_time: 1
    duration: 4
```

Types: `transport_disruption`, `transport_disruption_probability`,
`transport_cost_shock`, `capital_destruction` (uniform via `filter:`, or
absolute per canton x sector via `description_type: subregion_file` + `file:`),
and `productivity_shock`.

`transport_cost_shock` keeps the edges open but multiplies their cost labels
(`cost_multiplier`: a number or `{cargo_type: m, default: m}`) for `duration`
steps: buyers whose route crosses a shocked edge pay the surcharge (passed into
the price via `transport_share`), reroute when an alternative is cheaper (with
the switching penalty), or give up beyond `price_increase_threshold`. With
`delivered_price_increase_threshold` set, the give-up test is on the delivered price
(transport share x relative cost increase); it is a scalar or a dict keyed by product type
(the supplier sector's type) and/or cargo type with `default`, e.g. `{mining: 0.3, default: 5}`:
low-value bulk is abandoned at a smaller increase than feedstocks or manufactured goods. The switching
penalty `logistics.switching_costs.modal_switch` is a scalar or a per-cargo-type dict
(`{default: 0.15, liquid_bulk: 1000}`): a prohibitive value for a cargo class says that its
alternative mode does not exist at volume, so that class pays the surcharge while the shocked
edge is open and gives up only when it is closed, whatever the price threshold. This is
the representation of low water, congestion or tolls that does NOT need
capacity-constrained routing; combine with a `transport_disruption` for the
steps where the edge is de facto closed.

```yaml
  - type: transport_cost_shock
    attribute: name
    values: [rhine_mainz_koblenz]
    cost_multiplier: 4.5      # barges at 22% load -> 1/0.22
    capacity_factor: 0.22     # optional (default 1/cost_multiplier): share still carried by the shocked mode
    substitution_share: 0.3   # optional (default 1.0 = unlimited substitutes): share of the displaced
                              # remainder that the alternative route absorbs; the rest is not delivered
    start_time: 7
    duration: 1
```

Both `transport_disruption` and `transport_cost_shock` accept `substitution_share`
(the *substitution ceiling*). With it below 1, a link whose main route is hit
delivers `capacity_factor + substitution_share x (1 - capacity_factor)` of its
planned quantity (closures: `substitution_share`), pays the tonnage-weighted
cost of the two routes, and the shortfall is counted as blocked. Without it the
substitutes are unlimited and a closure costs nothing but the detour price.
Filters accept firm attributes and `subregion_*` keys, and log how many firms
they matched. Firm-side recovery is threshold-only (`recovery_shape` is
ignored with a warning); absolute capital destruction recovers only through
the reconstruction market (`reconstruction_market: true` + its
`reconstruction_*` settings). The legacy key `events` is accepted for backward
compatibility, but new files should use `disruptions`.

## Criticality

Each scenario is a **list of edge names** (one run per inner list):

```yaml
simulation_type: "criticality"
criticality:
  duration: 4
  scenarios:
    - ["road_1"]
    - ["road_1", "port_main"]
```

See [Criticality Analysis](criticality.md) for the legacy per-edge loop,
`top_n`, and resumable runs.

## Performance Workflow

Use cache presets from the CLI while iterating:

```bash
disruptsc Cambodia --cache same_transport_network_new_agents
disruptsc Cambodia --cache same_logistic_routes
```

Caches are keyed by scope and validated against a per-stage fingerprint of the
configuration: a cache built under different watermarked settings is refused
with a key-level diff instead of silently reused. Runtime knobs (`t_final`,
disruptions, `time_to_activate_idle_capital`, …) do not invalidate caches, so
sweeps over them can safely reuse one build. Use `--cache_isolation` for
concurrent runs that should not share pickle cache files.

Every exporting run writes `parameters.yaml` (full config snapshot),
`run_fingerprint.json` (code version, git SHA, watermarked keys), and
`exp.log` next to its outputs.
