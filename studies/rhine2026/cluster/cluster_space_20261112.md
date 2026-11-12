# Space on `/projects/disruptsc`, 12 November 2026

Assessment asked by the author on 12 November 2026. Nothing was deleted. Sizes are decimal GB from `ceph.dir.rbytes`
(the inventory of 8 November, `cluster_inventory_20261108.md`, printed GiB; 1 GiB = 1.074 GB).

State at 10:05 UTC: **913.8 of 1,000 GB used, 86 GB free**; 34 Cambodia jobs running and writing.

## Where the space is

| Folder | GB | Owner | Last write | What it is |
|---|---|---|---|---|
| `runs/cambodia` | 124.7 | colon | 12 Nov | 1,735 runs of the Cambodia paper, 6 to 12 November (active) |
| `runs/rhine2026` | 101.0 | colon | 10 Nov | old 2026 runs 41.3, runs of the 7 October reissue 31.3, the 2018 runs of the paper 21.4, 20 archives 7.0 |
| `runs/rhine2026_obs` | 44.9 | colon | 11 Nov | the batch of 11 November: 106 runs, 4 archives, leftovers |
| `disrupt-sc_cambodia_v2` | 165.3 | nobile | Jan 2026 | logs 100.8, caches 48.3, output 15.4 |
| `tariffs_paper_2026` | 135.5 | crescentini | Jun 2026 | Eurostat extracts, a database, MATLAB results (not DisruptSC) |
| `dsc-macromip` | 133.0 | colon | Jun 2026 | seven experiments 126.7, caches 6.2 |
| `disrupt-sc` | 89.4 | colon | 12 Nov | `tmp` 51.3 (caches), `output` 31.7, `eq_paper_results.zip` 5.5 |
| `export-controls` + its tarball | 63.2 | colon | 11 Nov | active study |
| `disrupt-sc-rhine` | 26.2 | colon | 11 Nov | the checkout of the batch of 11 November: its caches |
| `disrupt-sc-cambodia` | 12.0 | colon | 12 Nov | caches of the Cambodia runs (active) |
| `miniforge3` | 11.7 | colon | Oct | Python environments; package cache 8.3 |
| `climada-disruptsc` | 4.1 | nobile | Jul 2026 | |
| the rest | 2.9 | | | |

## 1. Rhine study and caches: assessed in detail, 158 GB

Each tier is a name of `space_free_20261112.sh` (below). The sizes are those of its dry run of 12 November.

| Tier | GB | What | What is lost | My advice |
|---|---|---|---|---|
| `pidcaches` | 45.5 | 386 per-process cache folders in `disrupt-sc/tmp` (`EcuadorEQ_pid_*` 43.1 GB of 20 August, `Ecuador_`, `Armenia_`, `ECA_pid_*`) | Nothing: each belonged to one finished job; none was written since August | Delete |
| `old2026` | 41.6 | The 103 runs of 2026 of the batch of 2 November in `runs/rhine2026`, with their logs, and the x0.75 run of 6 November | The firm files of 81 runs and the link-level files of the old full run (15.2 GB). The paper no longer reads these runs: all 101 that were rerun have their rerun in `rhine2026_obs`; the two others are the stress paths, dropped. The small outputs of all 103 and the firm files of 22 are on the local disk (`C:/dsc_runs/rhine2026_profile0930`) and in the restore archives of 10 November, which stay on the cluster. The control run of 11 November showed that they can be recomputed byte for byte | Delete |
| `reissue` | 31.3 | The 125 runs of the 7 October reissue (`*_s07_*`, `wave07_*`, `*_rev_*`, `wave09_*`) in `runs/rhine2026` | The firm files of 66 runs. Kept on 8 November because the manuscript then documented the forecast as issued; the issue history left the manuscript on 11 November. The small outputs of all 125 and the firm files of 59 are on the local disk; the tables are in git | Delete |
| `rhinecaches` | 21.5 | The caches of the ten further networks and of the sea-rate run in `disrupt-sc-rhine/tmp` (11 × 1.8 GB), and `disrupt-sc/tmp/r6cal` | Rebuild time if those runs are repeated: each base run rebuilds its own cache in about 20 minutes. The cache of the reference network (`disrupt-sc-rhine/tmp/r6cal`) stays, for the rerun planned at revision | Delete |
| `leftovers` | 6.8 | Two per-process caches of the batch (4.7), the reduced package I built and did not use (0.7), the control run and the cache builder (0.3), `EU_logistic_routes_preKI37.pkl` (1.1, superseded on 21 September) | Nothing | Delete |
| `flows` | 5.9 | `transport_edges_with_flows_0/1.geojson` of the runs of 11 November, except the reference, link-level and sea-rate runs | Nothing a reader uses; the files were inputs of the post-processing, which is done | Delete |
| `conda` | 3.1 | `conda clean --all`: 837 package archives and 291 packages that no environment uses | Nothing | Delete |
| `archives11` | 2.5 | The four archives of 11 November on the cluster | Nothing: verified copies are on the local disk and the folders are on the cluster. A later restore would need a new pack | Either way |
| **Total** | **158.2** | | | 914 GB would become about 756 |

Kept in every case: the 2018 runs of the paper (21.4 GB), the 102 runs of 11 November that the paper reads, the
restore archives of 10 November (4.1 GB) and the 15 archives of September (2.9 GB), the default EU caches.

On hold, as on 8 November (regenerable, but a referee may ask for them):

| Item | GB | Note |
|---|---|---|
| `link_data.csv` and `inventory_data.csv` of the two link-level runs the paper reads (`rhine2026_obs/2026_r6_bycargo_full`, `rhine2026/2018_r6_bycargo_full`) | 30.1 | Their derived products are on the cluster and on the local disk. One job each recomputes them |
| `firm_data.csv` of the 83 runs of 11 November that are not on the local disk | 13.0 | No reader opens them. Three hours a run to recompute |

## 2. Other studies of the same account: sizes, and what I can say

I did not study these; the decisions need knowledge I do not have.

| Item | GB | What I see |
|---|---|---|
| `dsc-macromip/runs/macromip`: `link_data.csv` and `inventory_data.csv` of the seven experiments of 26 June | 115.5 | The largest single item of the account. Each experiment keeps its result file (`N-DisruptSC.csv`) and its loss tables. If macroMIP no longer needs link-level outputs, this is regenerable by seven jobs. Its caches: 6.2 GB more |
| `runs/cambodia` (active) | 124.7 | Per run, copies of static tables: `firm_table.geojson` 22.0 GB in all, `transport_edges.geojson` 5.5, `household_table.geojson` 0.7, `transport_nodes.geojson` 0.4; `exp.log` 3.8. In the repository's Cambodia scripts no reader opens `transport_edges.geojson`, `transport_nodes.geojson` or `exp.log`, and `firm_table.geojson` is read by one baseline script, for which one copy per network would do. Also `household_data.csv` 30.5 and the flow maps 18.8, read by the overlap scripts. For the Cambodia work to decide; about 28 GB are copies of static tables |
| `disrupt-sc/output/earthquake_paper/reference` | 21.0 | 50 seeds of August with their link-level files (about 20 GB). Next to it `disrupt-sc/eq_paper_results.zip`, 5.5 GB |
| `export-controls` (active) | 60.2 | 98 `loss_per_region_sector_time.csv` uncompressed, 26.1 GB (the later runs write `.csv.gz`); the delivery tarball `export_controls_cluster_20261023.tar.gz`, 3.0 GB, beside its extracted folder |
| `disrupt-sc/output/Cambodia` | 8.1 | 77 runs of July 2025 |
| `disrupt-sc-cambodia/tmp` (active) | 11.9 | 38 caches of the running study |

## 3. Colleagues' folders: 305 GB, a third of the quota

| Folder | GB | Owner | What I see |
|---|---|---|---|
| `disrupt-sc_cambodia_v2` | 165.3 | nobile | `logs/` 100.8 GB (error logs of up to 0.8 GB each), `tmp/` 48.3 GB of cache files, `output/` 15.4. Last written in January 2026 |
| `tariffs_paper_2026` | 135.5 | crescentini | Last written in June 2026 |
| `climada-disruptsc` | 4.1 | nobile | July 2026 |

The logs and caches of the first folder alone are 149 GB. They are not this account's to delete.

## The script

`space_free_20261112.sh` (this folder; the same file is on the cluster as `~/claude_tmp/space_free_20261112.sh`,
sha256 `de644f66f56dde84...`). Without `--run` it deletes nothing and prints the size of each tier:

    bash ~/claude_tmp/space_free_20261112.sh leftovers pidcaches conda old2026 reissue rhinecaches archives11 flows

With `--run` before the tier names it deletes them and writes each item to `~/claude_tmp/space_free_20261112.log`.
Guards: it touches only `runs/rhine2026`, `runs/rhine2026_obs`, `disrupt-sc-rhine/tmp` and `disrupt-sc/tmp`; the two
families of runs must be exactly the sets listed on 12 November (checked by a hash of their names); each old 2026 run
must have its rerun; the caches are left alone if a job that could use them is running.

Checks behind the table: the names of the 103 old runs and of the 125 runs of the reissue on the cluster are the names
of the folders on the local disk; the 101 reruns each have their `analysis.txt`; no per-process cache in
`disrupt-sc/tmp` was written after 20 August.
