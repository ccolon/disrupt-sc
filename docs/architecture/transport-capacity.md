# Transport capacity: review of the code and a way forward

Working design note, 21 Sep 2026. Not in the site nav. It records what the
capacity code does today, the inconsistencies found (with a reproducible probe
on the bundled Testkistan scope, `scripts/capacity_probe_testkistan.py`), and
a proposal that keeps capacity in the agent-based register (individual
behaviour and heuristics, no global optimisation) with a computing cost that
scales with the few capacitated links, not with the whole supply chain.

## Status (21 Sep 2026, evening)

Phases 1 to 3 are implemented on this branch: the retired algorithms are gone
from main (`routing.py` 2 081 -> 489 lines), capacities exist only on named
edges, `cargo_mode_eligibility` replaces `default_transport_capacity`, the
gate runs at step 7g of the time loop with its accounting and exports, the
tests of section 4 pass (`tests/test_capacity_gate.py`, suite 158 green), the
docs and the known-issues register (KI-39 to KI-42, KI-27 and KI-31 closed)
are updated. Phase 4 on the real scopes needs the data repository (EU/Rhine,
Ecuador, Gulf), which this session does not have; it ran the Testkistan and
synthetic checks instead. The `legacy/v2-capacity-routing` branch is to be
created by the maintainer at `2fbb13d` (section 3.5).

Phase 4 on the data repository (22 Sep 2026, in the cloud container, 4 CPUs):

- **Ecuador, transport off (EcuadorEQ as configured: monthly, 12 steps,
  seed 0, the earthquake shock)**, legacy code at `2fbb13d` against the new
  code: firm, household, country, inventory, link, trade, loss and MRIO
  files identical row for row (link_data with its two new columns);
  `transport_edges.geojson` differs only by the placeholder `capacity` column
  the old loader wrote on every edge; `household_data_by_sector.csv` is
  identical once sorted and `loss_summary.csv` agrees to 2e-13 - both vary
  the same way between two runs of the SAME code under different
  `PYTHONHASHSEED` values while `firm_data.csv` stays identical, so they are
  a pre-existing hash-seed order in the household by-sector export (KI-43),
  not the rework.
- **Ecuador, transport on**, 6 986 firms, 95 865 routable links, 1 587
  nodes / 2 023 edges, one cargo type ("any"), monthly steps: 12.1 s per
  step with capacities off, 12.1 s with a slack capacity on the busiest edge
  (the gate scan costs nothing), 16.5-17.4 s with that edge, crossed by
  21 298 links (2.12 Mt/step), cut to half its load: 21 298 shipments cut
  proportionally and re-sent in one round, 16 588 links end with an
  alternative route, nothing blocked. Before the two optimisations below the
  same step cost 43 s cold and 28 s warm.
- The optimisations, bit-identical by construction: the per-route
  quantities that depend on static edge attributes only (km by mode, sea-side
  connectors) are memoised on the shared `Route` objects and the hot loops
  read the adjacency dict instead of networkx views (the capacity-off step
  went from 16.1 to 12.1 s too); and the gate's re-sends run as one scipy
  single-source Dijkstra per origin and search filter
  (`discover_routes_batched`, same candidates and the same choice as
  `discover_route`, cached under the same libraries; exact cost ties can
  resolve differently, as in the initial assignment).
- Synthetic grids after batching (`scripts/capacity_gate_scaling.py`, 900
  nodes, 8 000 shippers, 32 capacitated edges, 2 389 t cut): the gate costs
  1.3 s against 50 s before, placement 0.2 s; two rounds throughout.
- Ecuador's `transport.gpkg` carries no usable edge names (28 edges named
  "None, None"), so a name-keyed override cannot target an Ecuador edge until
  the data names them; the timing runs set the capacity programmatically.
  The Gulf data of the repository names its border crossings, sea lanes,
  airports and pipelines, but not its 113 multimodal connectors: the port
  gateways of the April runs cannot be named from this data either (KI-44).
- The Gulf rebuild itself still needs a v2 scope configuration (the v1 one
  lives on `legacy/v1`).

Phase 4 evidence of 21 Sep 2026 (Testkistan and synthetic, before the
optimisations; the synthetic gate times are superseded by the table above):

- `scripts/capacity_probe_testkistan.py`: trunk capped at a tenth of its load
  on the tree network: 9 links cut to 10.0 % of their offered quantity each
  (proportional), 13 388 t withheld, goods back in the suppliers' stocks; the
  archived bypass scenario (trunk closed, bypass at 1 050 t/step): every one
  of the 9 displaced links delivers 7.1 % of its quantity and the bypass sits
  at 1 050 t, against five links whole, four dropped and 149 % of capacity
  under the retired code. Step time 1.0 ms off, 2.1 ms with the gate.
- `scripts/capacity_gate_scaling.py` (n x n road grids, 1 t shippers on random
  OD pairs, the k busiest edges at half their load): two rounds throughout;
  the placement of 8 000 shipments costs 0.3-0.5 s, the gate 2-50 s, and the
  gate time is the networkx searches of the cut shares (900 nodes, 1 740
  edges, 32 capacitated: 2 389 t cut, 50 s, about 10 ms per search, two
  searches per uncached share: own modes and free). The cost is proportional
  to the cut tonnage as designed; the constant is the per-search cost of
  `nx.shortest_path` on a subgraph view, the same one the closure and
  cost-shock reroutes already pay. Follow-up if a scope needs it: batch the
  free search per (cargo, origin, saturated set) with the scipy
  single-source Dijkstra of `routing.shortest_paths_for`, and run the
  same-mode candidate only for links whose switching penalty is prohibitive.
- Not run: Rhine/EU and Ecuador bit-identity on the real data (the capacity-
  off path is unchanged by construction: same labels, same routes, same
  single-route delivery; the pipeline test and the Testkistan CLI run are
  the evidence available here), and the Gulf rebuild.

## 0. Summary

- Capacity exists in two disconnected layers: an **initial route assignment**
  (three algorithms: chunked candidate heuristic, candidate-path LP, edge LP)
  and a **runtime cost label** (`cost_per_ton_with_capacity_<cargo>`) that only
  agents forced off their main route ever read. A capacity is never binding
  for a shipper on its normal route: with the Testkistan trunk capped at 10 %
  of its baseline load, both `binary` and `gradual` place 1000 % of capacity
  on it and deliveries are bit-identical to `capacity_constraint: off`.
- The initial assignment is what does not scale (KI-27): the candidate
  generator runs two networkx Dijkstras per OD-cargo group whatever the
  capacities (EU: 197k groups, killed after 81 CPU-min), and the LPs are global
  optimisation by construction.
- The `gradual` cost form gives an empty capacitated edge **half** its base
  cost (multiplier 0.5 at zero load, 1.0 only at 80 % utilisation), so under
  `gradual` the give-up rule and the price pass-through compare a discounted
  detour against an undiscounted normal bill. `binary` has no such bias, which
  is why the EU work went for it.
- Per-edge capacities in the transport GeoPackage are silently overwritten by
  `default_transport_capacity`; the only working channel is
  `transport_capacity_overrides` by edge NAME, and a name that matches no edge
  is silently ignored.
- Proposal: capacity as a **local gate** on the capacitated edges (rationing
  of the shipments that actually cross them, after every agent has shipped)
  with **within-step rerouting** of the cut tonnage on the network minus the
  saturated edges, through the existing penalty-aware alternative search and
  give-up rules, iterated until no gate cuts; the loop is bounded by the
  number of capacitated edges. Plain Dijkstra at initialisation (baseline
  capacities must not bind, checked), no candidate generation, no LP; route
  searches only for the cut shipments, cached per saturated set. Cost is
  proportional to the traffic through the capacitated links. On-off only: no
  cost multiplier anywhere, one rationing rule. The last code state carrying
  the Gulf machinery is archived under the repo's `legacy/*` convention
  (`legacy/v2-capacity-routing` at main `2fbb13d`, to be created; `legacy/v1`
  of 18 Apr 2026 already holds the v1 code of the April Gulf runs); main is
  cleaned.

## 1. What the code does today

### 1.1 Where capacities come from (`init_pipeline/transport.py`)

Config (tons/day, converted to tons per step by `time_resolution`):

- `default_transport_capacity` per mode: a number = shared capacity on every
  edge of the mode; a dict = per-cargo capacity, 0 = blocked (no cost label is
  written for that cargo, the edge is invisible to Dijkstra).
- `transport_capacity_overrides` by edge `name`: number or per-cargo dict.
- `capacity` / `capacity_<cargo>` columns of the GeoPackage layers are read and
  scaled by the time factor (`_load_transport_edges`)…

…and then `_apply_default_capacities` (l. 260-310) overwrites `edge["capacity"]`
in each of its three branches (no default → 1e9 × factor; dict → 1e9 × factor
+ per-cargo; number → the default) and pops or overwrites every per-cargo
column. The data columns never survive; the "DISCARDED … add a
default_transport_capacity entry" warning (l. 291-298) recommends something
that would also overwrite them. Probe A: Testkistan `Port Access Road` has
`capacity = 200` t/day in the file and ends up at 100 000 t/day (the road
default). `docs/user-guide/input-data.md` still documents the column.

`_apply_capacity_overrides` (l. 313-346) matches names exactly and applies the
override to every edge carrying the name (both directions and every connector
of a terminal: an override is a two-way throughput). Names in the config that
match no edge produce no message (probe F).

The "unlimited" sentinel is `1e9 × time_factor` on the edge but the tests are
`< 1e8` (`CAPACITY_INF` in routing.py l. 37; `< 1e8` in
`transport_network._refresh_edge_capacity_costs` l. 744-770 and
`compute_logistics_report`). A real capacity of 5 Mt/day (the maritime
default) is 3.5e7 per week (finite) and 1.5e8 per month (unlimited): whether
an edge is capacity-constrained depends on the time resolution (probe G).

### 1.2 Initial route assignment (`init_pipeline/routing.py`, 2 081 lines)

`capacity_constraint: off` → `_precompute_and_assign`: batched scipy Dijkstra
per cargo type, one route per link, `route_plan = [(route, 1.0)]`. This is
the path every current paper run uses (EU/Rhine, Ecuador).

`capacity_constraint: gradual | binary` → one of three algorithms chosen by
`logistics.initial_route_assignment`:

| Mode | Mechanism | Pros | Cons |
|---|---|---|---|
| `heuristic` (default) | OD-cargo groups; hub-based candidates (baseline path forced through each alternative port / border of the same type, ≤ `route_candidate_count`, ≤ `route_candidate_stretch` × baseline cost); tonnage placed chunk by chunk in rounds, each chunk on the cheapest candidate at the live congestion-adjusted cost | closest to an agent heuristic (each shipper picks the cheapest live route) | two networkx Dijkstras per group whatever the capacities (probe E: 32 calls for 21 groups; EU 197k groups → KI-27); the placement order is the dict order, so who gets the cheap gateway is arbitrary; leftover chunks fall back to the primary corridor; `capacity_routing_max_iterations` ignored (l. 289) |
| `lp` | path-flow LP over the same candidates, piecewise-linear surcharge aligned with the runtime multiplier at the breakpoints, overflow beyond `lp_overcapacity_limit` | global optimum over the candidates, splits flows | same candidate generation; system optimum, not individual behaviour; ~350 lines + diagnostics |
| `edge_lp` | multi-commodity min-cost flow, variables per (group, directed arc), flow decomposition into paths | no candidates needed | variables = groups × arcs (memory), system optimum, post-solve costs hard-coded `"gradual"` (l. 985) |

All three end with `transport_network.reset_loads()` (`setup_logistic_routes`
l. 96): the baseline loads they computed are discarded before the simulation
starts. Multi-route plans (`len(route_plan) > 1`) survive and are shipped by
`_send_chunked_shipment` at runtime.

### 1.3 Runtime (`agents/transport_utils.py`, `network/transport_network.py`)

Every shipment placed on the network adds its tons to `current_load_<cargo>`
of the route's edges (`place_shipment` → `update_load_on_route` l. 521-536)
and, when `capacity_constraint` is on, refreshes the edge's
`cost_per_ton_with_capacity_<cargo>` **after** the placement. Loads are reset
at the end of every step (`simulate.py` l. 542): no memory from one step to
the next.

Who reads the congestion-adjusted label:

- `send_shipment` main-route branch (l. 285-289): nobody. A shipper whose
  main route is open ships on it whatever the load. Probe D: trunk capped at
  1 488 t/step, 14 879 t placed, `overused = True`, deliveries identical to
  capacity off, in both modes.
- the closure branch and the cost-shock branch: the alternative search
  (`discover_route`) uses `cost_per_ton_with_capacity` as Dijkstra weight and
  the give-up rule compares the alternative's congestion-adjusted cost with the
  normal route's base cost `link.route_cost_per_ton`.
- `_send_chunked_shipment` (l. 365-496): only closures trigger a search per
  chunk; a cost shock on a planned sub-route is not seen (no surcharge, no
  give-up), and the closure substitution share is not applied. The single-route
  branch handles both.

So at runtime a capacity acts only on shippers already displaced by a
disruption, in the order in which agents deliver (countries first, then
firms in dict order), against the partial loads placed so far in the step.
Probe H (bypass road capped at 1 050 t/step, trunk closed): the four country
links (70 t) and the first firm link (1 491 t) get the bypass, which ends at
149 % of capacity because the check runs after placement; the remaining four
links, including the 11 539 t household link, are dropped in full
(`too_expensive`, +1e10 under binary, ×400 under gradual) although 1 000 t of
capacity was still free before the firm link took it. Nothing is queued or
partially delivered; the goods stay in the supplier's stock.

With `capacity_constraint` on, `discover_route` also disables the route cache
(`effective_cache = use_route_cache and not capacity_constraint`, l. 60):
every rerouting link runs a full Dijkstra every step, because within-step
labels change after each placement. This, not the gate itself, is the runtime
cost driver on a scope with many displaced links.

`_capacity_multiplier` (transport_network.py l. 693-716) is 0.5·(1 + u/0.8)
for u ≤ 0.8: an empty capacitated edge costs half its base cost in the
congestion-adjusted label (probe B: 0.495 vs 0.990). Under `gradual`:
a detour whose base cost is up to twice the normal route shows a relative
increase of 0, a ×1.5 cost shock on the main route shows no increase, the
price pass-through is halved. The LP surcharge table assumes f(u) = 1 on
[0, 0.8] (segment surcharge 0.0), so the two forms are not aligned there
either. `binary` (base + 1e10 when over) is unbiased below capacity.

### 1.4 What the Rhine study did instead (settled rules, unchanged by this note)

Capacity routing was switched off (KI-27) and low water is represented by
`transport_cost_shock` (surcharge, pass-through, penalty-aware reroute,
give-up), closures with class floors, and the per-link **substitution
ceiling** (`capacity_factor`, `substitution_share`), which is a proxy for the
capacity of the substitutes without any edge accounting. Finite substitute
capacities were prepared (`studies/rhine2026/baseline_capacities.py`:
baseline load × headroom per rail/road/waterway edge; `port_capacities.py`:
Eurostat port throughput for the maritime connectors) but not applied.

## 2. Findings

Anchors are to the 21 Sep 2026 tree (commit f349870). Probe letters refer to
`scripts/capacity_probe_testkistan.py`.

| # | Where | Finding | Evidence |
|---|---|---|---|
| C1 | `transport_utils.send_shipment` l. 285-289 | Capacity is never binding on a main route; loads exceed capacity without consequence | probe D: 1000 % of capacity, deliveries = off |
| C2 | `transport_network.update_load_on_route` l. 521-536, `simulate.py` l. 494-542 | Congestion is checked after placement and against the partial load of the step, in agent iteration order; loads reset every step | probe H: edge ends at 149 %, first-come-first-served, big late link dropped in full |
| C3 | `transport_network._capacity_multiplier` l. 709 | 0.5× discount below 80 % utilisation biases the give-up rule and the pass-through under `gradual`; LP table assumes no discount | probe B: 0.495 vs 0.990 |
| C4 | `routing._generate_hub_based_candidates` l. 1242-1248 | Two networkx Dijkstras per OD-cargo group whatever the capacities; the batched scipy Dijkstra of the off path is not reused | probe E: 32 calls for 21 groups; KI-27 |
| C5 | `transport.py _apply_default_capacities` l. 260-310 | GeoPackage `capacity*` columns always overwritten; misleading DISCARDED warning; `input-data.md` documents the column | probe A |
| C6 | `transport.py _apply_capacity_overrides` l. 336 | An override name matching no edge is silently ignored (`validate-inputs` does not check names) | probe F |
| C7 | `routing.CAPACITY_INF` l. 37 vs `1e9 × time_factor` sentinel | "finite" classification depends on time resolution | probe G: 5 Mt/day maritime finite weekly, unlimited monthly |
| C8 | `routing._find_congested_edges` l. 1972 | Division by a zero shared capacity (override 0 on a shared edge) crashes the heuristic | ZeroDivisionError in the first probe run |
| C9 | `transport_utils.discover_route` l. 60 | Route cache disabled whenever capacity is on: a full Dijkstra per displaced link per step | code |
| C10 | `transport_utils._send_chunked_shipment` l. 408 | Multi-route plans ignore cost shocks and the closure substitution share; the single-route branch handles both | code |
| C11 | `routing.py` l. 289, 1140; `config.py`; `parameters.md`; `fingerprint.py` l. 135 | `capacity_routing_max_iterations`, `route_candidate_overlap`, `lp_route_candidate_overlap` are read, documented and fingerprinted but ignored (config-hygiene invariant) | code |
| C12 | `routing.py` l. 576, 985 | Post-LP cost refresh hard-coded `"gradual"`; then `reset_loads` discards it anyway | code |
| C13 | `routing.py` l. 1598-1620, 1942-1953, 1988-2000; `route.py` l. 89; `transport_network.py` l. 509 | Dead code: `_route_edge_keys`, `_strategic_edge_key`, `_accumulate_loads`, `_find_affected_sources`, `Route.has_over_capacity_edges`, `transport_shipment` | no callers |
| C14 | `routing._build_trade_capacity_diagnostic` l. 1684 | "gateway capacity" counts `special == "border"` edges only; ports are not gateways here | code |
| C15 | `run_pipeline/disruption.py` `TransportDisruption`, `transport_network.apply_edge_capacity_factor` l. 200-212 | `capacity_reduction < 1` scales capacities only; with capacity off (every current scope) it is a silent no-op, and with capacity on it acts only through C1/C2 | code; `run_rhine.py` docstring says the same |
| C16 | `transport_network.place_shipment` cost-shock split | main and alternative parts share the key `link.pid` in `edge["shipments"]`; on an edge common to both routes the flow export keeps one part (loads are right) | code |

Documentation that describes behaviour the code does not have: `parameters.md`
("`capacity_routing_max_iterations` bounds the heuristic's re-routing
rounds"), `studies/rhine2026/README.md` row "Transport-disruption mechanics"
("routing sees congestion surcharges when `capacity_constraint: gradual`" —
only displaced shippers do), `input-data.md` (`capacity` column).

## 3. Proposal: capacity as a local gate with within-step rerouting

Decisions taken 21 Sep 2026 (user): drop both LPs, the heuristic, candidate
generation, chunking and multi-route plans; no deprecated modes in the code,
the Gulf-era code is archived in git instead and main is cleaned; cut tonnage
is re-sent within the step on the network minus the saturated edges until it
converges; on-off semantics only (no cost increase with load, no other mode);
one rationing rule; the GeoPackage capacity columns are removed;
`default_transport_capacity` is replaced by a cargo-mode eligibility table
and the named overrides become the only capacities.

### 3.1 Principles

1. A capacity is a physical property of an edge, enforced on the shipments
   that cross it, for everyone, after everyone has shipped. No shipper is
   exempt because it was first in the dict.
2. The allocation at a saturated edge is decided on what is offered, not on
   the order in which agents happened to deliver: proportional within a round
   is order-independent, so no Monte Carlo over the delivery order is needed.
   One rule only.
3. Behaviour is individual: a shipper cut at a gate looks for an alternative
   with the rules that already exist (penalty-aware search on its own modes
   and free, line-haul rule, switching penalty, delivered-price give-up,
   pass-through). Nothing is optimised across shippers.
4. On-off: an edge either has room or it has not. No congestion multiplier,
   no second cost label per edge; the saturated edges are simply excluded
   from the searches of the rest of the step.
5. Cost is spent only where capacity bites: the gate pass is linear in the
   shipments crossing capacitated edges; route searches run only for cut
   shipments, once per saturated set, cached. An edge has a capacity only if
   it is named in the config, so the capacitated set is small by construction.
6. `capacity_constraint: false` scopes stay bit-identical.

### 3.2 Mechanism

**Round 1.** Every agent delivers as today: main route if open, otherwise the
closure / cost-shock branches of `send_shipment`. Shipments are placed on the
network with a reference to their route (the record in `edge["shipments"]`
gets a `route` field; `place_shipment` has it).

**Gate.** After step 7 ("firms deliver") and before step 8 ("collect flows"):
for every capacitated edge, per cargo type (per-cargo capacity) and in total
(shared capacity), offered = accepted load of earlier rounds + placements of
this round. Where offered > capacity, the placements of THIS round are cut
proportionally so that accepted = capacity; earlier rounds are never cut
again (round priority: the shippers whose normal route uses the edge share
the first cut pro rata, diverted traffic takes what is left). A shipment
crossing several over-capacity edges takes the smallest of their factors,
which leaves the less binding edge below capacity and open for the next
round. Every edge cut in a round is saturated (accepted = capacity) and is
EXCLUDED from all searches for the rest of the step. The cut share of a
shipment is removed from every edge of its route and from the destination
node.

**Reroute.** Each cut shipment is offered a route on the available network
minus the saturated edges (`discover_route` with an excluded-edge set in the
subgraph filter of `provide_shortest_route`; own modes and free, switching
penalty, line-haul rule; the alternative library keyed by the saturated set
plus the closures); the give-up rules apply to the cut share (its cost
relative to the normal bill, plus the switching penalty). A shipper that
accepts places the cut share on the alternative (accumulated at the
destination under the link pid, as the substitution-ceiling split does
today) and pays the tonnage-weighted price of its parts. A shipper that
declines or finds no route keeps the goods.

**Convergence.** Repeat gate and reroute. Because accepted loads are frozen
and saturated edges are excluded, the saturated set only grows and each
cutting round saturates at least one new edge (the edge with the smallest
factor is filled exactly): the loop ends after at most |C| + 1 rounds, |C|
the number of capacitated edges, in practice two or three. The bound is the
loop's cap (no knob; a log line if it is ever reached). Only the tonnage
still undelivered then returns to the supplier's `product_stock` (firms) or
is removed from `qty_sold` (countries), so the conservation ledgers of
`tests/test_testkistan_pipeline.py` hold; the buyer's next order is served
from stock next step. Undelivered by capacity and undelivered by refusal are
recorded separately: new link fields `delivery_offered`, `capacity_blocked`,
and `capacity_blocked_usd` in `routing_summary.csv` (the split KI-31 asks
for).

**Prices.** The gate is physical: it changes who moves and by which route.
The rerouted share pays the detour and the switching penalty through the
existing pass-through; nothing else moves a price. No congestion surcharge
(decision 21 Sep 2026: no other mode).

**Initial state.** `setup_logistic_routes` always runs `_precompute_and_assign`
(scipy Dijkstra). It then accumulates the baseline loads (the existing
`_accumulate_loads`) and reports every capacitated edge whose baseline load
exceeds its capacity (the trade-capacity diagnostic, extended from border
edges to all capacitated edges). Nothing else: the gate acts from t = 0 like
at every step, so a scope whose baseline exceeds a capacity starts its run
rationed at that edge, and the warning says so. No warm-up, no raise.

### 3.3 Config surface

```yaml
capacity_constraint: true                 # bool; "gradual" / "binary" raise with a pointer to the archive tag
transport_capacity_overrides:             # the ONLY capacities, by edge name, tons/day
  strait_of_hormuz: 3000000               # shared across cargo types
  port_jebel_ali:                         # per cargo type
    container: 450000
    dry_bulk: 80000
    liquid_bulk: 200000
  oil_terminal_x:
    liquid_bulk: 120000
    container: 0                          # 0 blocks the cargo on this edge; a cargo not listed has no capacity there
cargo_mode_eligibility:                   # which cargo types may travel on which mode; a mode not listed takes everything
  airways: [container]
  pipelines: [liquid_bulk]
```

Why the split. Today's `default_transport_capacity` does two jobs at once:

```yaml
default_transport_capacity:               # today
  roads: 100000        # (b) a capacity on EVERY road edge, chosen so that it never binds
  maritime: 5000000    # (b) idem, every sea lane
  airways:
    container: 5000    # (b) idem
    dry_bulk: 0        # (a) "no bulk by air": an eligibility rule, not a capacity
    liquid_bulk: 0     # (a)
  pipelines:
    container: 0       # (a) "only liquid bulk in pipes"
    dry_bulk: 0        # (a)
    liquid_bulk: 500000  # (b)
```

(a) The zeros say which cargo may use which mode; the code writes no cost
label for that cargo on those edges, so Dijkstra never uses them. That is
the part every scope needs, and it is not a capacity. (b) The numbers put a
capacity on every edge of the mode. They are not data (100 000 t/day on every
road edge is a placeholder chosen not to bind), yet they make every edge
capacitated for the code: every edge would enter the gate's set C, the gate
pass would run over the whole network and the |C| + 1 bound would be the
number of edges. `cargo_mode_eligibility` keeps (a) as what it is; (b) is
dropped: an edge has a capacity only if it is named. A whole mode can still
be capacitated by naming its edges. Config hygiene: a config still carrying
`default_transport_capacity` raises with this explanation; an override name
matching no edge raises; a cargo type outside `sector_to_cargo_type` raises.

Removed: the GeoPackage `capacity` / `capacity_<cargo>` columns (ignored with
one info line and dropped from `input-data.md`), `logistics.initial_route_assignment`,
`chunk_size`, `route_candidate_count/stretch/overlap`, `lp_*`,
`capacity_routing_max_iterations` (all raise as unknown for one release, then
silently ignored like any foreign key), `cost_per_ton_with_capacity_<cargo>`
labels, `overused`, `current_load_<cargo>` (loads are read from the shipment
records). Fingerprint: `cargo_mode_eligibility` joins the `transport_network`
stage keys and `WATERMARKED_CONFIG_KEYS`; `capacity_constraint` and
`transport_capacity_overrides` stay; the `logistic_routes` stage build version
is bumped so that caches holding multi-route plans or the old labels are
refused instead of misread.

### 3.4 Complexity

Per step: at most |C| + 1 rounds; per round a gate pass O(shipments on
capacitated edges) and one route search per distinct (origin, destination,
cargo) among the cut shipments, cached by the saturated set, so a step whose
congestion pattern repeats the previous one pays only the gate passes. A
scope with a handful of capacitated links pays nothing until a disruption
pushes traffic onto them. The Gulf configuration (capacities on ~40 gateways,
Hormuz closed) pays for the cut shipments only, a subset of the displaced
links that already run Dijkstra today under the closure, now cached. Memory:
one cost label per cargo per edge instead of two.

### 3.5 What is retired, what is archived

Retired from main: `_precompute_and_assign_with_capacity`,
`_precompute_and_assign_with_capacity_lp`,
`_precompute_and_assign_with_edge_lp`, the hub index and candidate
generation, chunk rounds, flow decomposition, the LP diagnostics exports, the
dead helpers of C13, `_send_chunked_shipment` and multi-entry `route_plan`
(one route per link; splitting happens at the gate, by tonnage), the
`gradual` / `binary` runtime label machinery (`_capacity_multiplier`,
`_refresh_edge_capacity_costs`, the per-placement refresh in
`update_load_on_route`, the `with_capacity` cost path, the cache-off rule of
`discover_route`), the GeoPackage capacity columns,
`default_transport_capacity`. About 1 300 of the 2 081 lines of routing.py
plus ~150 in transport_network.py and transport_utils.py.

Archived, not deprecated, under the repo's `legacy/*` convention:
`legacy/v2-capacity-routing` at main `2fbb13d`, the last commit carrying all
of the above (to be created by the maintainer, this session's push access is
limited to its working branch: `git branch legacy/v2-capacity-routing 2fbb13d
&& git push origin legacy/v2-capacity-routing`; `git archive
legacy/v2-capacity-routing -o legacy.zip` gives the zip). `legacy/v1`
(18 Apr 2026, `d47cc0f`) already holds the v1 code on which the April 2026
Gulf and Hormuz runs were made, and every exported run records its commit in
`run_fingerprint.json`. On main, `capacity_constraint: gradual | binary`
raise at parse with a message naming `legacy/v2-capacity-routing`.

### 3.6 Relation to the existing mechanisms

- `transport_disruption` with `capacity_reduction < 1` becomes meaningful on
  a capacitated edge: the gate rations at the reduced capacity within the
  step. Closures (reduction 1) keep their current path.
- `transport_cost_shock` is unchanged.
- The substitution ceiling stays for the Rhine rules; with real capacities on
  the substitutes it is redundant and `substitution_share: 1` should be used.
- Line-haul rule, per-cargo line-haul modes, switching penalties, delivered
  price thresholds: unchanged, reused by the reroute of the cut share.

## 4. Implementation plan

Phase 1 — clean main (1 day): delete everything listed in 3.5; the parser
accepts only a bool for `capacity_constraint` and raises on the old strings
and on `default_transport_capacity` with the migration message;
`cargo_mode_eligibility` replaces the zeros in `default.yaml` (airways
containers only, pipelines liquid bulk only) and in `_calculate_cost_per_ton`;
`_apply_capacity_overrides` raises on unknown names and unknown cargo types,
explicit 0 blocks, omitted cargo has no capacity; the loader ignores the
GeoPackage columns; one `math.inf`-free convention (an edge without an entry
has no `capacity` key at all); C13 deleted; C14 extended to all capacitated
edges; bump the `logistic_routes` build version; `validate-inputs` checks the
override names against the GeoPackage. Tests: capacity-off scopes bit-identical
(the Testkistan ledger tests, an EU/Rhine routing checksum if a cached build
is at hand), unknown name, unknown cargo, old strings raise.

Phase 2 — the gate loop (2-3 days): shipment records keep their route;
`TransportNetwork.apply_capacity_gate()` returning the cut shares per
shipment; the reroute of cut shares through `discover_route` with the
saturated set excluded and the alternative library keyed by it; the loop in
`_run_one_time_step` after step 7, capped at |C| + 1; link and supplier
bookkeeping; `delivery_offered` / `capacity_blocked`; routing summary and
logistics report columns (offered, accepted, withheld per capacitated edge).
Tests on Testkistan with an override on the trunk and the bypass network of
the probe: proportional cut and round priority, stock and inventory ledgers,
capacity ≥ load bit-identical to off, two gates on one route, order
independence (permute the firm dict, same deliveries), convergence in
≤ |C| + 1 rounds, Dijkstra call count bounded by the cut shipments.

Phase 3 — docs and provenance (half a day): `parameters.md`,
`architecture/index.md`, `AGENTS.md`, `MIGRATION.md`, the Rhine README row,
`input-data.md`, `README.md` feature list; fingerprint keys; delete `tmp/`
caches of capacity-on scopes.

Phase 4 — validation on real scopes: Rhine/EU and Ecuador runs bit-identical
(capacity off); Gulf rebuilt from its archived config with the gateway
overrides and the eligibility table, Hormuz closure scenario compared with
the archived April 2026 results, timings recorded per step and for the
routing stage; the Rhine substitute capacities
(`scenario_edge_capacities.csv`, port throughputs) tried as a sensitivity on
the calibrated baseline.

## 5. Decisions (all taken 21 Sep 2026)

- LPs, heuristic, candidate generation, chunking and multi-route plans:
  dropped, no benchmark copy.
- Gulf-era code: archived in git under `legacy/*` (`legacy/v2-capacity-routing`
  at `2fbb13d`; `legacy/v1` already holds the April 2026 code), not kept as
  deprecated modes; main cleaned.
- Cut tonnage is re-sent within the step until convergence; the residue waits.
- One rationing rule: proportional within a round, round priority across
  rounds. (The `value` rule that was floated, highest value per ton first as
  a proxy for willingness to pay for the scarce slot, and the seeded
  `random_order` lottery are not implemented.)
- On-off only: no cost increase with load, no surcharge mode, no warm-up, no
  raise on a binding baseline (a warning per edge, the gate acts from t = 0).
- GeoPackage capacity columns: feature removed.
- `default_transport_capacity` replaced by `cargo_mode_eligibility`; the
  named overrides are the only capacities.
