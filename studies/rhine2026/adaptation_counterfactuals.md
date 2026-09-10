# Adaptation counterfactuals for the Nature Communications paper (plan, 10 Sep 2026)

Target journal decided 10 Sep: Nature Communications (event paper; the modelling contribution goes to
Methods/SI or a JEDC companion). The counterfactuals answer "what would have blunted the 2026 losses":
each lever has a real-world counterpart in the 2026 debate, one implementable switch in the model, and a
paired run against the baseline it is compared with. Levers act on the physical channel (who can sail,
with what load, what buffers exist, what the alternative modes offer); they do not touch demand.

## Levers

| # | lever | real-world counterpart | model implementation | runs |
|---|---|---|---|---|
| A | fairway deepening | Abladeoptimierung Mittelrhein (WSV): +20 cm fairway depth Budenheim–St. Goar, planned for the 2030s | evaluate the draught table and the class floors at gauge + 20 cm: new driver flag `--gauge-offset 20` (`--gauge-offset 10` as the half-built variant if wanted) | 1 (+1) |
| B | low-water fleet | purpose-built shallow-draught tankers and bulkers (Stolt Ludwigshafen ~800 t at 30 cm, 9 such ships in Aug 2026; HGK's EUR 12.5 bn fleet call) | tank-barge floor 50 → 40 cm (fleet partly renewed: the 42–49 cm tail weeks open) and a renewed bulk fleet sailing to 20 cm (`liquid_bulk=20,dry_bulk=20`, containers unchanged) with the low-water draught table `draught_table_lowwater.csv` (+0.10 load factor in the 15–55 cm band): the 22–29 cm weeks become surcharge weeks for bulk, the 11–12 cm weeks stay closed. A 30 cm floor would change nothing at 27–29 cm (dry-run check) | 2 |
| C | input stocks | one more week of raw-material stock (strategic fuel stocks for hauliers and power plants; refinery and chemical feedstock) | `--inventory-add-days 7` on every goods input (new flag; global variant) and a targeted YAML variant: buyers of barge-borne fuel, feedstock and cement (H49/H50/H52, D, C20, C23, C24A) +7 d only | 2 |
| D | rail relief | tank-car trains and extra paths on the Rhine valley lines (DB Cargo's ≈ 100-barge ceiling; the second track debate) | DECIDED 10 Sep: the cost version. `--rail-relief 0.4` = a `transport_cost_shock` × 0.4 on every rail edge for liquid and dry bulk in every shock week (tank-car rail at the bulk rate, 0.085 → 0.034 USD/tkm), containers unchanged. Code check: `send_shipment` searches the alternative route on the network with the current cost labels (`provide_shortest_route`, `start_edge_cost_shock` rewrites `cost_per_ton_<cargo>`), so a Rhine link facing a closure sees the cheaper rail and gives up less. The capacity version (`--constraint-mode gradual`, headroom 1.3 vs 1.8) is not run: a quantity cap, outside the baseline's philosophy | 1 |
| E | package | A + B (renewed fleet, 20 cm) + C (global) | all three switches | 1 |

Expected direction: A and B shorten the closure spells (the 27–42 cm weeks become surcharge weeks for the
classes concerned), C moves the fuel-driven losses of the first closure weeks later or removes them,
D lowers the give-up of bulk in closure weeks, E shows complementarity (package vs sum of parts).

## Runs and pairing

- Profile: the same as the baseline they are compared with. Now: the forecast-based 2026 profile
  (`2026_seed42_pool_fc0910`, 19 weeks); the whole set is rerun on the final observed profile when the
  event is over (November), when the paper's numbers are frozen. The September pairs serve the draft.
- Settings: the confirmed baseline (v13 rates, closure floors, voyage surcharge, input pooling, seed 42),
  light exports, 12 recovery weeks (the tail of the pooled runs ends 4–6 weeks after the last shock; the
  net/delay accounting is reported on the 20-week baseline run and on the counterfactuals at 12 weeks).
- Metrics per pair: DEU and EU value-added loss (gross, net, delay), peak week and its level, weeks with
  losses, corridor firms below 99 % of baseline at the peak, household consumption loss, Kaub tonnage
  by week (A and B also change the physical throughput — the ex post consistency check).
- Names: `2026_fc0910_<lever>` with lever ∈ {base, deep20, fleet40, fleet20, stock7, stock7t, rail04, package}
  and the grid runs (`cluster/jobs_20260910.txt`).
- Cost: 32 steps ≈ 5 h each on the laptop (one run at a time, ≈ 12.6 GB RAM) → 7–8 runs ≈ 4 nights;
  on the cluster all pairs in one batch of ≈ 6 h. The sensitivity grid for the uncertainty band (seeds
  × 3, tanker floor ± 10 cm, inventories ± 50 %, Lower Rhine factor 0 and 1, no pooling, v12 rates)
  belongs in the same batch: ≈ 8 more runs.

## Status (10 Sep, 11:30)

Implemented and tested (driver commit of 10 Sep): `--gauge-offset`, `--inventory-add-days D[:SECTORS]`,
`--inventory-scale`, `--rail-relief`, `--cache-isolation`; `scenarios/draught_table_lowwater.csv`. Cluster batch:
`cluster/jobs_20260910.txt` (1 base + 7 counterfactuals + 10 grid runs), `cluster/launch_rhine_batch.sh` (Slurm,
`--wrap` jobs, base first then afterok; postprocess per run; compare job at the end), `cluster/sync_to_cluster.sh`,
`cluster/collect_from_cluster.sh`. 12 recovery weeks (user decision). The user submits on the cluster.

## Code changes (small, driver-side)

1. `run_rhine.py --gauge-offset <cm>`: added to every weekly gauge before the draught table and the
   floors (the profile file stays the observed record). Test: the 2026 schedule at +20 cm.
2. `run_rhine.py --inventory-add-days <d>` (and `--inventory-scale <f>`): applied to the goods entries of
   the loaded inventory YAML, service days untouched. Test: the loaded targets.
3. `scenarios/draught_table_lowwater.csv`: the central table with the load factor raised by 0.10 between
   15 and 55 cm (a fleet in which low-water vessels carry a tenth of the normal tonnage at those gauges),
   anchors documented in the file.
4. Rail relief: `run_rhine.py --rail-relief <multiplier>`: a `transport_cost_shock` on every rail edge for
   liquid and dry bulk in every shock week. Verified by code reading (the alternative-route search uses the
   current cost labels), not yet by a run: the `rail04` pair must show a lower blocked share and give-up in
   closure weeks than `base` (routing_summary / section 6 of the analysis); if it does not, the lever is inert
   and the reason must be found before the paper uses it.
5. Queue v17 (laptop) or a cluster job list; the watcher analyses each run; `compare_runs.py` on the pairs;
   a figure "avoided loss by lever" (`plots/scenario_figures.py`, new panel).

## Paper use

Figure: avoided German and EU value-added loss by lever (gross and net), with the package; table of the
lever definitions and their real-world anchors; one paragraph on complementarity and on what the model
cannot say (pipeline mode absent, no rationing of trucks and drivers, no demand-side throttling).
