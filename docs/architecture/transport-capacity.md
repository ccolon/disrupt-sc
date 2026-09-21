# Transport capacity: review of the code and a way forward

Working design note, 21 Sep 2026. Not in the site nav. It records what the
capacity code does today, the inconsistencies found (with a reproducible probe
on the bundled Testkistan scope, `scripts/capacity_probe_testkistan.py`), and
a proposal that keeps capacity in the agent-based register (individual
behaviour and heuristics, no global optimisation) with a computing cost that
scales with the few capacitated links, not with the whole supply chain.

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
  proportional to the traffic through the capacitated links. The `gradual` and
  `binary` runtime modes of the Gulf runs stay as deprecated aliases.

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
generation, chunking and multi-route plans; keep the Gulf runtime modes as
deprecated; cut tonnage is re-sent within the step on the network minus the
saturated edges until it converges, and only what still finds no acceptable
route waits for the next step.

### 3.1 Principles

1. A capacity is a physical property of an edge, enforced on the shipments
   that cross it, for everyone, after everyone has shipped. No shipper is
   exempt because it was first in the dict.
2. The allocation at a saturated edge is decided on what is offered, not on
   the order in which agents happened to deliver: proportional within a round
   is order-independent. Sequential all-or-nothing commitment is the one
   design that needs a Monte Carlo over the delivery order to mean anything;
   it stays available as a named rule (`random_order`), not as the default.
3. Behaviour is individual: a shipper cut at a gate looks for an alternative
   with the rules that already exist (penalty-aware search on its own modes
   and free, line-haul rule, switching penalty, delivered-price give-up,
   pass-through). Nothing is optimised across shippers.
4. Cost is spent only where capacity bites: the gate pass is linear in the
   shipments crossing capacitated edges; route searches run only for cut
   shipments, once per saturated set, cached.
5. Baseline capacities do not bind. The initial state is the plain Dijkstra
   assignment; a capacity below the baseline load is a calibration error
   (reported), not something an assignment algorithm should hide. Capacity
   effects appear when a disruption moves traffic onto the capacitated
   substitutes (the Gulf case: gateways have headroom in the baseline and
   saturate once Hormuz closes).
6. `capacity_constraint: off` scopes stay bit-identical.

### 3.2 Mechanism

**Round 1.** Every agent delivers as today: main route if open, otherwise the
closure / cost-shock branches of `send_shipment`. Shipments are placed on the
network with a reference to their route (the record in `edge["shipments"]`
gets a `route` field; `place_shipment` has it).

**Gate.** After step 7 ("firms deliver") and before step 8 ("collect flows"):
for every capacitated edge, per cargo type (per-cargo capacity) and in total
(shared capacity), offered = accepted load of earlier rounds + placements of
this round. Where offered > capacity, the placements of THIS round are cut so
that accepted = capacity; earlier rounds are never cut again (round
priority). Within the round the cut is proportional (default) or by a named
rule (`random_order`: a seeded permutation, all or nothing in that order;
`value`: highest value per ton first). A shipment crossing several
over-capacity edges takes the smallest of their factors, which leaves the
less binding edge below capacity and open for the next round. Every edge cut
in a round is saturated (accepted = capacity) and is EXCLUDED from all
searches for the rest of the step. The cut share of a shipment is removed
from every edge of its route and from the destination node.

**Reroute.** Each cut shipment is offered a route on the available network
minus the saturated edges (`discover_route`, own modes and free, switching
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
the number of capacitated edges, in practice two or three. Only the tonnage
still undelivered then returns to the supplier's `product_stock` (firms) or
is removed from `qty_sold` (countries), so the conservation ledgers of
`tests/test_testkistan_pipeline.py` hold; the buyer's next order is served
from stock next step. Undelivered by capacity and undelivered by refusal are
recorded separately: new link fields `delivery_offered`, `capacity_blocked`,
and `capacity_blocked_usd` in `routing_summary.csv` (the split KI-31 asks
for).

**Prices.** Within the step a gate is physical: it changes who moves and by
which route, and the rerouted share pays the detour and the switching
penalty through the existing pass-through. An optional congestion surcharge
from the previous step's utilisation (`capacity.surcharge`, off by default)
can be added later for the freight-rate story of Hormuz; it reuses the
cost-shock branch and is not needed for the loop to work.

**Initial state.** `setup_logistic_routes` always runs `_precompute_and_assign`
(scipy Dijkstra). It then accumulates the baseline loads (the existing
`_accumulate_loads`) and extends the trade-capacity diagnostic to every
capacitated edge: baseline load > capacity is reported per edge and, by
default, raises (`capacity.baseline: raise | warn`). Optional
`capacity.warmup_steps: k` runs k undisrupted steps with the gate, without
RNG, and freezes the resulting routes for scopes whose baseline is meant to
be congested; the routes cache holds the result.

### 3.3 Config surface (proposal)

```yaml
capacity_constraint: off | gate | gradual | binary   # gradual/binary: DEPRECATED Gulf semantics, warned at parse
transport_capacity_overrides: {...}      # unchanged: name -> tons/day or {cargo: tons/day}; unknown names raise
capacity:
  priority: proportional | random_order | value   # rule at a saturated gate within a round
  max_rounds: 10                          # safety cap on the within-step loop (|C| + 1 suffices)
  baseline: raise | warn                  # baseline load above capacity
  warmup_steps: 0
  surcharge: off                          # optional next-step congestion pricing (later)
cargo_mode_eligibility:                   # replaces the 0-entries of default_transport_capacity (blocking)
  airways: {dry_bulk: no, liquid_bulk: no}
  pipelines: {container: no, dry_bulk: no}
```

`default_transport_capacity` today mixes two things: cargo-mode eligibility
(the zeros) and per-mode capacities that are never meant to bind (roads
100 000 t/day on every edge). Splitting them makes "no capacity unless
stated" the default, so the capacitated set is exactly the named edges.
Retired keys: `logistics.initial_route_assignment`, `chunk_size`,
`route_candidate_count/stretch/overlap`, `lp_*`,
`capacity_routing_max_iterations` (warned as inert for one release).
Fingerprint: `capacity.*` and `cargo_mode_eligibility` join the
`transport_network` stage keys and `WATERMARKED_CONFIG_KEYS`; the
`logistic_routes` stage build version is bumped so that caches holding
multi-route plans are refused instead of misread.

### 3.4 Complexity

Per step: at most |C| + 1 rounds; per round a gate pass O(shipments on
capacitated edges) and one route search per distinct (origin, destination,
cargo) among the cut shipments, cached by the saturated set, so a step whose
congestion pattern repeats the previous one pays only the gate passes. A
scope with a handful of capacitated links pays nothing until a disruption
pushes traffic onto them. The Gulf configuration (capacities on ~40 gateways,
Hormuz closed) pays for the cut shipments only, a subset of the displaced
links that already run Dijkstra today under the closure, now cached.

### 3.5 What is retired, what is kept as deprecated

Retired: `_precompute_and_assign_with_capacity`,
`_precompute_and_assign_with_capacity_lp`,
`_precompute_and_assign_with_edge_lp`, the hub index and candidate
generation, chunk rounds, flow decomposition, the LP diagnostics exports, the
dead helpers of C13, `_send_chunked_shipment` and multi-entry `route_plan`
(one route per link; splitting happens at the gate, by tonnage). About 1 200
of the 2 081 lines of routing.py. The LPs are deleted, not kept as a
benchmark (decision 21 Sep 2026).

Kept as deprecated, so that the Gulf configurations still run:
`capacity_constraint: gradual | binary` with their runtime semantics
unchanged (label refreshed after each placement, in delivery order, reroute
only for displaced shippers, main routes exempt, route cache off, the
`_capacity_multiplier` of C3 as it is), on top of the plain Dijkstra initial
assignment; a parse-time warning names the successor and this note; a
Testkistan regression test pins today's numbers (probe H: five links on the
bypass, four dropped, 1 561 t on a 1 050 t edge) so the path cannot rot
silently. What a Gulf rerun in these modes will NOT reproduce is the archived
initial assignment (heuristic or LP), i.e. baseline flows through gateways
whose capacity bound at baseline. Removal after the Gulf rebuild under `gate`
is validated.

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

Phase 0 — hygiene, no result change for capacity-off scopes (half a day):
C6 (unknown override names raise in `_apply_capacity_overrides` and in
`validate-inputs`), C7 (one `math.inf` sentinel, `math.isfinite` tests), C8
(guard), C11 (retire the inert knobs; fingerprint key), C13 (delete), C14
(all capacitated edges), C5 (decide: honour data columns with precedence
override > data > mode default, or drop them from the loader and the docs).
C3 stays inside the deprecated modes. Tests: unknown name, resolution-
independent finiteness, `pytest` green.

Phase 1 — retirement and deprecation (1 day): delete the three assignment
algorithms, candidate generation, chunking, `_send_chunked_shipment` and
multi-route plans; `capacity_constraint: gradual | binary` become deprecated
aliases over the Dijkstra assignment with a parse-time warning; bump the
`logistic_routes` build version; the Testkistan regression test on probe H
pins the deprecated semantics; `_INERT_KEYS` warnings for the retired keys.

Phase 2 — the gate loop (2-3 days): shipment records keep their route;
`TransportNetwork.apply_capacity_gate(priority)` returning the cut shares per
shipment; the reroute of cut shares through `discover_route` with the
saturated set excluded and the alternative library keyed by it; the loop in
`_run_one_time_step` after step 7 with `max_rounds`; link and supplier
bookkeeping; `delivery_offered` / `capacity_blocked`; routing summary and
logistics report columns; `capacity_constraint: gate`. Tests on Testkistan
with an override on the trunk and the bypass network of the probe:
proportional cut and round priority, stock and inventory ledgers, capacity ≥
load bit-identical to off, two gates on one route, order independence
(permute the firm dict, same deliveries), convergence in ≤ |C| + 1 rounds,
Dijkstra call count bounded by the cut shipments, `random_order` reproducible
under the run seed.

Phase 3 — initial state, config, docs (1 day): baseline check (raise/warn),
optional warm-up, `capacity.*` keys and `cargo_mode_eligibility`, fingerprint
keys, `parameters.md`, `architecture/index.md`, `AGENTS.md`, the Rhine README
row, `input-data.md`. Delete `tmp/` caches of capacity-on scopes.

Phase 4 — validation on real scopes: Rhine/EU and Ecuador runs bit-identical
(capacity off); Gulf rebuilt with the gateway overrides under `gate`, Hormuz
closure scenario compared with the archived results and with the deprecated
modes, timings recorded per step and for the routing stage; the Rhine
substitute capacities (`scenario_edge_capacities.csv`, port throughputs)
tried as a sensitivity on the calibrated baseline.

Later, optional: the next-step congestion surcharge (`capacity.surcharge`)
for congestion pricing, reusing the cost-shock branch.

## 5. Decisions

Taken 21 Sep 2026: LPs, heuristic, candidate generation, chunking and
multi-route plans are dropped (no benchmark copy); `gradual` / `binary`
stay as deprecated aliases; cut tonnage is re-sent within the step until
convergence; proportional within a round with round priority is the default
rule, `random_order` the Monte-Carlo alternative.

Open:

1. Baseline rule: raise when a baseline load exceeds a capacity (recommended)
   or warm-up steps by default.
2. GeoPackage capacity columns: honour (override > data > mode default) or
   drop.
3. Split `default_transport_capacity` into `cargo_mode_eligibility` plus
   optional per-mode capacities (recommended), or keep the key.
4. Whether the `value` priority rule (highest value per ton first) is wanted
   at all, or proportional and `random_order` suffice.
