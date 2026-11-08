# Cluster inventory of the Rhine 2026 study, 8 November 2026

Inventory of `/projects/disruptsc/runs/rhine2026` on the IIASA cluster (CephFS, sizes from `ceph.dir.rbytes`),
taken before the clean-up of 8 November 2026. The volume `/projects` (59 TB) was 77 % full (15 TB free);
`/projects/disruptsc` held 931 GB, of which `runs/` 378 GB (rhine2026 287 GB, cambodia 91 GB).

`runs/rhine2026`: 286.8 GB = 528 run folders (274.0 GB) + 53 archives `rhine_batch_*.tgz` (12.3 GB) + 528 `<run>.log`
(4 MB). Every run folder belongs to one of the 43 job lists `cluster/jobs_*.txt`. The local mirror
`C:/dsc_runs/rhine2026` (34 GB, 345 run folders) holds the small outputs of every run from 29 September onwards
and the firm-level file of about 136 runs; it holds nothing of the September calibration runs or of the batch of
30 September, whose tables are in `additional_data/` (git) and whose packed outputs are in the archives.

Per-run sizes with family, mirror status and job lists: `~/claude_tmp/inv_rhine_runs.csv` on the cluster
(written by `~/claude_tmp/inv_analysis.py` from `inv_rhine_dirs.txt`, `local_runs.txt`, `inv_tgz_contents.txt`).

## Run families

| Family | Runs | GB | link+inventory GB | firm_data GB | rest GB | Dates | Mirrored locally | Job lists |
|---|---|---|---|---|---|---|---|---|
| F0 flows run `2026_s07_flows` | 1 | 1.0 | 0.9 | 0.0 | 0.1 | 22 Oct | 1/1 | 20261023_flows |
| F1 rounds `r1_*` … `r6_h*` (modal calibration) | 46 | 45.7 | 41.9 | 0.4 | 3.3 | 22–29 Oct | 46/46 | 20261023_round1 … 20261029_round6 |
| F2 `2026_fc0910_*` (first forecast) | 27 | 5.2 | 0 | 2.9 | 2.3 | 15 Sep | 0/27 | 20260910, 20260911, 20260913 |
| F3 `*_cal_*`, `2018_baseline/nopool`, `2018_inv*` | 37 | 7.8 | 0 | 4.6 | 3.2 | 15–16 Sep | 2/37 | 20260911, 20260913, 20260916_cal2018/ens2018/paper |
| F4 `2018_inv200_full` | 1 | 6.7 | 6.5 | 0.1 | 0.1 | 21 Sep | 0/1 | 20260921_full2018 |
| F5 `2018_pipe`, `2026_pipe_base` | 2 | 0.5 | 0 | 0.3 | 0.2 | 22 Sep | 0/2 | 20260922_pipe |
| F6 `2018_gs1c`, `2026_gs1c_base` | 2 | 0.5 | 0 | 0.3 | 0.2 | 29 Sep | 2/2 | 20260929_constr |
| F7 `*_gs1_*` | 28 | 5.8 | 0 | 3.4 | 2.4 | 28 Sep | 0/28 | 20260928_gs1paper |
| F8 `2018_gs*`, `2026_gs_base` | 5 | 1.1 | 0 | 0.7 | 0.4 | 22–24 Sep | 0/5 | 20260923_gs, 20260924_gsladder |
| F9 `wave_A/B/AB_gap*/flat` | 7 | 1.5 | 0 | 0.9 | 0.6 | 29 Sep | 7/7 | 20260929_waves |
| G1 `*_s30_*`, `wave30_*` (first issue) | 96 | 50.1 | 28.0 | 14.0 | 8.1 | 29–30 Sep | 0/96 | 20260930_main, 20260930_paired |
| G2 `*_s07_*`, `wave07_*`, `*_rev_*`, `wave09_*` (frozen reissue) | 125 | 56.7 | 28.0 | 18.2 | 10.5 | 5–20 Oct | 125/125 | 20261007_ladder/main/paired/rev, 20261009_cross, 20261020_norail |
| G3 `2018_cont`, `2026_cont_full` | 2 | 14.7 | 14.2 | 0.3 | 0.2 | 23 Oct | 2/2 | 20261022_container |
| G4 `2018_r6_*` (hindcast before by-cargo) | 20 | 18.5 | 13.8 | 2.9 | 1.7 | 30 Oct–1 Nov | 20/20 | 20261029_hindcast_r6, 20261031_hindcast_diag, 20261031_hindcast_r6_rerun |
| K1 `*_r6_bycargo_*`, `wave_r6_bycargo_*` (FINAL) | 129 | 58.6 | 28.0 | 18.8 | 11.8 | 1–7 Nov | 129/129 | 20261101_bycargo_ens, 20261101_hindcast_bycargo, 20261102_*, 20261103_altriver, 20261106_inv075 |
| Total | 528 | 274.0 | 161.3 | 67.8 | 44.9 | | | |

Bulk files: `link_data.csv` (10.6 GB) and `inventory_data.csv` (3.9 GB) in each of the eight `*_full` runs, 0.67 + 0.26 GB
in each round run; `firm_data.csv` about 150 MB in every run. Every `*_full` run already carries its derived products
(`kaub_links_check.csv`, `link_flows_disrupted.csv.gz`, `inventory_trace.csv`, `validation_outputs.csv`), which the
local mirror has too.

## Archives

53 files, 12.3 GB, all made by `pack_results.sh` (small outputs of one job list, firm files only with `--with-firms`).
Every run packed in an archive still exists as a folder on the cluster. The 37 archives from `rhine_batch_20260929_1207`
to `rhine_batch_20261107_1443` plus `ki49_outputs_20261103.tgz` and `rhine_compare_20261012.tgz` (9.5 GB) pack runs that
are also in the local mirror; `rhine_batch_20260922_1910-Copy1.tgz` duplicates `rhine_batch_20260922_1910.tgz`. The
13 September archives (1.5 GB: 20260910_2120/2121, 20260912_1556, 20260914_0858, 20260915_1904, 20260916_0812/1248/2026,
20260922_0800, 20260922_1910, 20260923_0827, 20260928_1333, 20260929_0718) and the two of 30 September
(20260930_0730 1.2 GB with the firm files of 19 main runs, 20260930_0736 74 MB) are the only compact copies of runs absent from the mirror.

## Other folders seen (not this study)

`disrupt-sc/tmp` 47.7 GB: 320 `EcuadorEQ_pid_*` cache folders of 20 August 2026 (40.1 GB), 28 `Ecuador_pid_*` (1.4 GB),
24 `Armenia_pid_*` (0.2 GB), 14 `ECA_pid_*`; EU caches `EU_logistic_routes.pkl` (1.0 GB, 5 Oct), `EU_sc_network.pkl`
(0.5 GB), `r6cal/` (1.7 GB, 6 Nov) and the superseded `EU_logistic_routes_preKI37.pkl` (1.0 GB, 21 Sep); Romania caches
(0.9 GB). `disrupt-sc/output` 29.5 GB (earthquake_paper 19.5, Cambodia 7.5, Romania 2.0). Other studies:
`disrupt-sc_cambodia_v2` 154 GB, `tariffs_paper_2026` 126 GB, `dsc-macromip` 124 GB, `runs/cambodia` 91 GB,
`export-controls` 38 GB + `export_controls_cluster_20261023.tar.gz` 2.8 GB, `ac.zip` 0.3 GB.

## Clean-up tiers proposed on 8 November 2026

| Tier | Scope | Frees | Why it is safe |
|---|---|---|---|
| T1 | 38 archives: the 37 from 29 Sep (waves) to 7 Nov, `ki49_outputs`, `rhine_compare_20261012`, and the `-Copy1` duplicate | 9.6 GB | every packed run exists as a folder on the cluster and in the local mirror |
| T2 | whole folders of F0, F1, F6, F9, G3, G4 (78 runs) | 81.9 GB | superseded by the r6 by-cargo configuration; small outputs mirrored locally; tables in `additional_data/` |
| T3 | whole folders of F2, F3, F4, F5, F7, F8 (100 runs of 15–28 Sep); keep their 13 archives (1.5 GB) | 27.1 GB | superseded calibration; packed small outputs stay in the archives; batch tables in git |
| T4 | whole folders of G1 (96 runs of the 30 Sep issue); keep its 2 archives (1.3 GB), download them first | 50.1 GB | the first issue is documented by its tables in git (`compare_runs_batch_jobs_20260930_*`, `batch_20260930_summary.txt`) and its packed outputs |
| T5 | `link_data.csv` and `inventory_data.csv` of `2026_s07_full` and `2018_s07_full` | 28.0 GB | the frozen reissue keeps its small outputs and derived products; bulk regenerable by re-running two jobs |
| T6 (hold) | `link_data.csv` and `inventory_data.csv` of `2026_r6_bycargo_full` and `2018_r6_bycargo_full` | 28.0 GB | regenerable, but a revision may want link-level detail; decide after acceptance |
| T7 (hold) | `firm_data.csv` of G2 (18.2 GB) and K1 (18.8 GB) | 37.0 GB | the SI tables are read from these files; about 95 of the 254 are mirrored locally |

T1–T5 free 196.7 GB and leave about 90 GB (K1 58.6 GB, G2 28.7 GB, 15 archives 2.8 GB).

## Deletion log

(filled in when the approved tiers are executed)
