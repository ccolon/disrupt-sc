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

## Output Switches

Read only when `export_files: true`. None of them changes a result: they choose
which files a run writes from the state each step leaves.

```yaml
export_link_data: true                 # link_data.csv, one row per commercial link and step (GBs on large scopes, KI-33)
export_inventory_data: true            # inventory_data.csv, one row per firm input and step
export_trade_by_region_sector: false   # trade_by_region_sector.csv (below)
export_logistics_every_step: false     # logistics report and per-edge flow files at every step (below)
monitored_edges: []                    # edge names the logistics report covers without a capacity (below)
```

**`export_trade_by_region_sector`** (18 Nov 2026) writes `trade_by_region_sector.csv`
next to `trade_data.csv`: per step, the deliveries between regions summed by
seller region, seller sector and buyer region, with the columns `time_step,
seller_region, seller_sector, buyer_region, quantity, tons`. It covers the links
`trade_data.csv` sums (seller and buyer in different regions, a delivery this
step): `quantity` is `realized_delivery` (model monetary units, as in
`trade_data.csv`) and `tons` is `delivery_in_tons` (the tonnage placed on the
network; a pipelined part has none). The seller sector is the firm's sector, or
`imports` for a country seller, as in `link_data.csv`. Only rows with a delivery
are written. Summed over `seller_sector` and `buyer_region` it gives the
`exports` of `trade_data.csv`, over `seller_region` and `seller_sector` its
`imports` (to rounding). It is the bilateral, by-sector split that otherwise
needs `link_data.csv`.

**`monitored_edges`** (18 Nov 2026): a list of edge names (the `name` column of
the GeoPackage layers, spelt exactly). `logistics_report.csv` covers the edges
named in `transport_capacity_overrides` and, on top, these edges - one row per
edge carrying the name and per reported step, with its tons and value in total
(`flow_tons`, `flow_usd`) and per cargo type (`tons_<cargo>`, `usd_<cargo>`).
No capacity is set on them: their `capacity_<cargo>` columns stay empty and the
gate never acts there. A name that matches no edge raises, at build time and in
`validate-inputs`. Several edges may carry one name (a pipeline in segments, a
lane with two legs): each gets its own row (`edge_id`). The config files are
read in the locale's encoding, so a name with a non-ASCII character (an en dash)
is safest written with a YAML escape: `"Kirkuk–Ceyhan"`.

**`export_logistics_every_step`** (18 Nov 2026; KI-73): the logistics report of the
monitored edges (`logistics_report.csv`, `logistics_summary.csv`,
`logistics_top_utilized.csv`) and the per-edge flow files
(`transport_edges_with_flows_<t>.geojson`) are written for every step of a
disruption run instead of steps 0 and 1 only. The report needs monitored edges
(a capacity override or `monitored_edges`); without them there is none, as
before. Each flow file is the whole network with that step's flows, so the
files grow with the network and the horizon (about 1 MB a step on the Gulf
scope).

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

### Region-specific stock depths

Stocks of some inputs differ by country, not by sector alone (strategic oil
reserves: days of net imports by country). `inventory_duration_targets_by_region`
(18 Nov 2026) overrides the targets above for the agents **located** in a region
(`firm.region`, `household.region`); absent or `{}`, nothing changes. Values in
days (the ones below are placeholders):

```yaml
inventory_duration_targets_by_region:
  JPN: {B06: 60, C19: 45}        # keys: an input id (SAU_B06), an input sector (B06) or a type (mining)
  KOR: {mining: 50}
```

- **Key precedence** for one input: its full id, then its sector, then its sector
  type (`sector_table`). Inputs the entry does not name keep their target.
- **Import bundles** (`{BLOC}_imports`): named by their id, by `imports` or by the
  type of `imports`, they take the days whole; otherwise, when their MRIO
  composition is known (firms), the sectors the entry names take its days and the
  others keep their base value, weighted by the composition (the crude inside a
  bundle gets the region's crude cover).
- **Firms and households**: the same entry applies to the firms of the region and,
  if `enable_household_inventories` is true, to its households (key: the consumed
  product); households hold no stocks otherwise, and the national government /
  investment agents never do. Country agents (outside the scope) hold none.
- Applied with the firm targets on every cache load (not a cache key; recorded in
  the run fingerprint). The log prints, per region, the entry and how many input
  targets of how many agents it changed, and warns about a region or a key that
  matched nothing.

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
not depend on the order in which agents deliver. The report covers the edges
named here; `monitored_edges` adds edges without a capacity, and
`export_logistics_every_step` writes it at every step (see Output Switches).

A `transport_disruption` with `capacity_reduction` below 1 scales the capacity
of a named capacitated edge (the gate then rations it); on an edge without a
capacity only a full reduction, a closure, has an effect.

`capacity_reduction` may also be **per cargo type** (18 Nov 2026), for a shock
that does not hit every cargo alike (a strait where container transits fall
further than tanker transits). The values below are placeholders:

```yaml
transport_capacity_overrides:
  strait_x: {container: 100000, dry_bulk: 100000, liquid_bulk: 100000}   # per-cargo capacities, t/day
disruptions:
  - type: transport_disruption
    attribute: name
    values: [strait_x]
    capacity_reduction: {container: 0.8, liquid_bulk: 0.4, default: 0.6}   # fraction lost, per cargo type
    start_time: 1
    duration: 4
```

Each cargo type takes its own fraction, a cargo type not listed takes
`default`, and with no `default` it is not reduced; every value is in [0, 1] and
a key that is not a cargo type of the scope (`logistics.sector_to_cargo_type`)
raises. The fraction scales the edge's `capacity_<cargo>` (the gate then rations
each cargo at its own reduced capacity), and every cargo recovers on the same
`recovery_shape` curve. A per-cargo cut binds only through a capacity:

- on an edge with **per-cargo capacities** each cargo is cut by its own fraction;
- on an edge with **one shared capacity** the dict works only if the cargo types
  that may use the edge get the same fraction (the shared capacity is then scaled
  by it); different fractions raise, because one capacity for all cargo cannot cut
  one cargo more than another - give the edge per-cargo capacities;
- on an edge with **no capacity** for a cargo the cut cannot bind (a warning names
  the edges), as for a partial scalar reduction; the edge is closed, for every
  cargo, only when every cargo type that may use it loses 100 %.

A number keeps the previous behaviour exactly.

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
`productivity_shock`, `stock_injection` and `export_ban`.

`stock_injection` (18 Nov 2026) is a dated, one-off addition to stocks, for a
strategic release (the IEA collective action of March 2026) that larger initial
stocks would move in time (placeholder values):

```yaml
  - type: stock_injection
    region: JPN          # the agents located in this region
    input: B06           # an input sector code, or a full input id (SAU_B06); import bundles by id or "imports"
    days: 15             # days of the agents' usual use of that input
    start_time: 3        # the time step (the week at weekly resolution) at whose start it is added, once
```

All four keys are required. At the start of step `start_time`, before orders
and production, every agent of the region that uses the input gets
`days / days_per_step x` its **equilibrium** use per step of it: the region
receives `days` of its usual daily use, shared among its users in proportion to
their usual use. Equilibrium, not current, use: a release is a fixed volume quoted
in days of normal demand, while current use falls exactly where the shortage bites.
Firms use the input when it is in their input mix; households only if they hold
stocks (`enable_household_inventories`); government / investment and country
agents receive nothing. The stock enters like a delivery (the next order covers
less of the gap) and is not removed afterwards: stocks above target are never sold
back, so an injection beyond the gap stays in stock. A sector-resolved import
folded into a `{BLOC}_imports` bundle is reached only through the bundle (its id or
`imports`), which then takes the whole bundle's use. The log reports the agents
reached and the quantity; an injection that reaches no agent warns. A run with
early stopping does not stop before the last `start_time`.

`export_ban` withholds a fraction of the foreign deliveries of the firms of an
exporting region (and sector), per destination region, over a window. It is the
`export_stop` rule of J. Seidler's MSc thesis (export controls, 2026) with the
corrections audited on `codex/export-controls-fixes`, shared by the Hormuz 2026
paper and `studies/export_controls`:

```yaml
  - type: export_ban               # illustrative codes and values
    regions: [AAA]                 # exporting region(s); required
    sectors: [CHE]                 # exporting sector(s); omit for every sector of the regions
    destinations: {BBB: 0.3, CCC: 0.2, default: 0.1}   # withheld fraction per destination region;
                                   # `default` = the other foreign regions (0 if absent)
    # fraction: 0.1                # or one fraction for every foreign destination (not both)
    product: acid                  # optional label of the banned good (see overlaps)
    start_time: 5                  # first banned step (>= 1)
    duration: 10                   # steps; or end_time: 14 (last banned step); neither = open-ended
```

- Times are in **time steps** (weeks at weekly resolution), like every disruption
  type; start `s` and duration `d` ban steps `s .. s+d-1` and reopen at `s+d`.
- The fraction applies to what the exporter's rationing allotted to each buyer in
  the destination region (firms, households and Country agents alike), so a 5 %
  ban withholds exactly 5 % of those deliveries. Buyers in the exporter's own
  region are never withheld from, and keep their rationed share.
- What is withheld stays in the exporter's product stock: its next production
  target (orders minus stock) falls by what it could not ship. The buyer's
  `served_order` is unchanged, so its fill rate (and `adaptive_supplier_weight`)
  and the routing summary's `blocked_usd` see the ban; `link.export_withheld`
  holds the withheld quantity of the step for observers.
- Overlaps: bans with the same `product` label on the same exporter are one
  restriction - while they overlap the larger fraction applies, and it lasts
  until the later expiry, whatever their order in the file. A relaxation is
  encoded by ending the earlier window (no rescission). Bans with different
  labels are different goods of the sector: their fractions add, capped at 1.
  No label = the sector as a whole.
- No early stop (`epsilon_stop`) while a ban is active: buyers' input stocks can
  hide its losses for several steps.
- Exporters are firms: Country agents (rest-of-world suppliers) are not covered.
  Unknown keys and fractions outside [0, 1] raise; a selection matching no firm
  logs a warning and is a no-op. Export bans are recorded in
  `run_fingerprint.json` (`export_bans`, only when present) and are not a cache key.

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
`capacity_factor` may be per cargo type like `cost_multiplier`
(`{dry_bulk: 0.22, default: 0.5}`, values in [0, 1], a cargo not listed takes
`default`, else 1); each link uses the value of its own cargo type. Omitted, it is
`1 / cost_multiplier` for a number and 1 for a per-cargo multiplier.
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
