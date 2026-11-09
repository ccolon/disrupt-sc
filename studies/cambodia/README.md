# Cambodia compound floods (Nobile & Colon) - v2 runs

The paper: "When timing matters: compounding floods and supply-chain losses in Cambodia". It targets the
Economic Modelling special issue on physical and transition risks, with a 30 Nov 2026 deadline. Its claim
is that interactions between flood events matter. The project folder, with the plan, evidence graph,
decisions and reports, is outside the repository: `../Paper_Cambodia/pipeline`.

The 2025 runs used a July 2025 checkout on the cluster (`disrupt-sc_cambodia_v2`). On 5 Nov 2026 the user
decided to port the study to v2. This folder holds the v2 runs.

| file | role |
|---|---|
| `paper_config.yaml` | base configuration of every run, on top of `config/default.yaml` only (the machine's `user_defined_Cambodia*.yaml` is ignored: KI-52) |
| `scenarios.py` | single, simultaneous and successive basin closures, and two-basin pairs at a lag of either sign (`pair_<a>_<b>_tau<T>`, 8 Nov 2026); footprint by attribute (`flood_v3` = the paper's, `flood_disruption` = v4) with its edge counts checked |
| `run_cambodia.py` | one run through `run.py execute` (not `build.py`: KI-51); one named build cache per seed, so every scenario of a seed runs on the same supply network; `study_run.json` records the git SHA and config hash; `--inventory-scale X` multiplies every inventory target |
| `add_flood_v3.py` | adds the v3 footprint to `Transport/transport.gpkg` (the v3 file is on the cluster) |
| `sea_gateways.py` | overseas partners at sea, Sihanoukville - Singapore lane, named crossings, port tags, 21 false `border` stubs untagged (Q17, 7 Nov 2026) |
| `route_calibration.py` | re-routes one seed's cached supply chain with the paper config and overrides (~25 s) and prints the gateway split against the 2015 anchors |
| `read_batch.py` | reads a batch into analysis/runs.csv and daily.csv; d and lags from the batch; prints the pilot's checks (determinism, settling, H1, lag curve) |
| `compare_horizons.py` | checks day by day that a run's path does not depend on its horizon (116- vs 180-day runs) |
| `excess_by_source.py` | a successive-flood run against its singles shifted to each event's start: the excess by period and sector |
| `mech_firms.py` | the same comparison firm by firm (runs with `--keep-firm-data` and `export_inventory_data=true`): sectors and firms with the largest excess production shortfall, and the inputs whose stock ran out; `--pair TAU` reads a two-basin pair run instead of a lag run; the shortfall split into fewer orders, unsold stock, capacity and missing inputs (exact, from the production rule) |
| `read_pairs.py` | reads a two-flood batch (`pair_<a>_<b>_tau<T>` runs) into `analysis/runs.csv` and `daily.csv` |
| `overlap_excess.py` | the overlap interaction (Q22): a pair run at tau 0 against its two singles - household loss split into unmet consumption and extra spending by period, by sector and by province; routing outcomes (main, alternative, blocked) over the closure; production shortfall by sector |
| `overlap_flows.py` | day-1 edge flows of the same three runs: each closure's traffic on the other closure's edges, and tonnage and ton-km on the network |
| `read_rob.py` | reads the robustness batches (variants `inv<X>` from `--inventory-scale`, `rest<N>` from the restoration time): settling by variant, two-flood ratio per variant |
| `cluster/launch_cambodia.sh` | one Slurm job per job-list line; one setup job per seed and cache; a run is written on the node's disk and copied at the end, and a job whose copy fails 20 times ends with status 75 and a `COPY_FAILED` file in the run folder (KI-56) |
| `cluster/check_launcher_copy.sh` | checks the launcher's copy step with a fake model and destination (bash only, no sbatch) |

Before any paper run:
1. The KI-53 fix (merged into main on 6 Nov 2026). Without it the undisturbed baseline collapses on day 30.
2. The v3 footprint in the network: `add_flood_v3.py` writes the road attribute `flood_v3` into
   `Transport/transport.gpkg` from `Transport/flood_v3_edges.csv` (the 36 closed edges, extracted on 6 Nov
   2026 from the cluster's v3 geojson, with a hash that ties the file's 2,145 edges to the gpkg's).
3. The network files in the data repository (committed 6 Nov 2026: `transport.gpkg` with `flood_v3`,
   `multimodal.gpkg`, `flood_v3_edges.csv`).
4. The sea gateways (7 Nov 2026): `sea_gateways.py --write` applied to the data repository, with
   `country_attachment: any` and the calibrated route costs in `paper_config.yaml`. Validation and calibration:
   `../Paper_Cambodia/pipeline/reports/05_flow_validation.md`. Runs made before this (batch pilot_20261106b) used
   the old gateways.
5. On the cluster, the paper runs from its own worktree, `/projects/disruptsc/disrupt-sc-cambodia`, so that
   the shared checkout of the other studies does not move (`CAMBODIA_CODE_DIR` overrides the path).

Example:

    python studies/cambodia/run_cambodia.py --scenario lag13 --duration 12 --seed 1 --t-final 180 --out <folder>
    bash studies/cambodia/cluster/launch_cambodia.sh --jobs <list> --batch <name> --dry-run
