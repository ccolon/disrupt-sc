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
| `scenarios.py` | single, simultaneous and successive basin closures; footprint by attribute (`flood_v3` = the paper's, `flood_disruption` = v4) with its edge counts checked |
| `run_cambodia.py` | one run through `run.py execute` (not `build.py`: KI-51); one named build cache per seed, so every scenario of a seed runs on the same supply network; `study_run.json` records the git SHA and config hash |
| `add_flood_v3.py` | adds the v3 footprint to `Transport/transport.gpkg` (the v3 file is on the cluster) |
| `cluster/launch_cambodia.sh` | one Slurm job per job-list line; one setup job per seed and cache |

Before any paper run:
1. The KI-53 fix (merged into main on 6 Nov 2026). Without it the undisturbed baseline collapses on day 30.
2. The v3 footprint in the network: `add_flood_v3.py` writes the road attribute `flood_v3` into
   `Transport/transport.gpkg` from `Transport/flood_v3_edges.csv` (the 36 closed edges, extracted on 6 Nov
   2026 from the cluster's v3 geojson, with a hash that ties the file's 2,145 edges to the gpkg's).
3. The network files in the data repository (committed 6 Nov 2026: `transport.gpkg` with `flood_v3`,
   `multimodal.gpkg`, `flood_v3_edges.csv`).
4. On the cluster, the paper runs from its own worktree, `/projects/disruptsc/disrupt-sc-cambodia`, so that
   the shared checkout of the other studies does not move (`CAMBODIA_CODE_DIR` overrides the path).

Example:

    python studies/cambodia/run_cambodia.py --scenario lag13 --duration 12 --seed 1 --t-final 180 --out <folder>
    bash studies/cambodia/cluster/launch_cambodia.sh --jobs <list> --batch <name> --dry-run
