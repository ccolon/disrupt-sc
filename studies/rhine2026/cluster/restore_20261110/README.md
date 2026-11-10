# Restore of the local copy of the final runs, 10 November 2026

The folders of the final batch (`*_r6_bycargo*`, the 129 runs of `additional_data/runs_20261102.csv`) had gone from
`C:/dsc_runs/rhine2026` at 17:54 on 10 November 2026; their logs were still there. The cluster held the 129 runs in
`/projects/disruptsc/runs/rhine2026`, but the batch archives had been deleted in the clean-up of 8 November
(`../cluster_inventory_20261108.md`), so the runs were packed again and downloaded.

## What was restored

The local copy as it stood before the loss: for every run the small outputs that `pack_results.sh` takes (analysis,
country and household series, routing summary, parameters, fingerprint, the baseline flows, figures, the log), and the
firm-level files (`firm_data.csv` and the four tables `firm_table`, `household_table`, `country_table`,
`transport_edges`) for the 46 runs that had them locally. Which runs those are comes from the size record of the local
folders of 6 November (45 folders of about 200 MB against 83 of about 32 MB) plus the x0.75 inventory run of 7 November:

- 2018: the reference run, the four inventory levels (`inv075`, `inv125`, `inv150`, `inv200`), the three priced runs,
  `rail50`, `rail140`, the ten draws `seed1` to `seed10`, `tablelow`, `tablehigh`, `sup2`, `full` (24 runs);
- 2026: the reference run, `deep20`, `dfuel0`, `fleet`, `fleetwide`, `rail50`, `rail140`, the ten bases
  `seed1_base` to `seed10_base`, `serv45`, `stock7`, `tablelow`, `tablehigh`, `full` (22 runs).

On the cluster the two reference runs carry their first names, `2018_r6_bycargo` and `2026_r6_bycargo`. The names the
scripts read, `2018_r6_bycargo_base` and `2026_r6_bycargo_base`, are directory junctions to them on the local disk, as
before (recreated with `New-Item -ItemType Junction`).

Not restored: the folders of the calibration rounds and of the earlier `r6` hindcasts, which went from the local disk
at the same time. They cannot be: the clean-up of 8 November removed them from the cluster, which keeps the 129 final
runs and the 125 runs of the 7 October reissue. No script behind the paper's numbers and tables reads them: the
regeneration below passes without them.

## The five archives

Packed on the cluster by `../restore_pack.sh` (same file list per run as `pack_results.sh`), one process per part,
three minutes in all. Lists of runs: `rhine_restore_20261110_<part>.runs.txt` in this folder (same sha256 as the lists
used on the cluster).

| Part | Runs | Firm files | Files | Bytes | sha256 |
|---|---|---|---|---|---|
| A | 83 | no | 1,577 | 690,142,169 | f3d3b683d3d1d3ac7854b7a6f6243b045129391f0f0b8763fece002b928029b7 |
| B | 12 | yes | 296 | 868,373,800 | e2282ed60de3fef136800ecf4ae409f4f66f94b841cef69f0167739523f2a3ef |
| C | 12 | yes | 288 | 873,090,668 | 19ee90c904310263e36384ce73e8b709c0d3f7ed3c8c2f61bceccc8f278d397c |
| D | 11 | yes | 272 | 817,627,534 | f51cc7659914741050759d10ad62f8348b92ccf7147f704df3e4249fe395afd7 |
| E | 11 | yes | 264 | 814,622,099 | 097ceeed471d2b3de28ec74c71841b1343e474c6372a5ef4ae2da87635e41fc7 |

Total 4.06 GB, 2,697 files. The archives are `rhine_restore_20261110_<part>.tgz` in
`/projects/disruptsc/runs/rhine2026` on the cluster and, after the download, in
`C:/dsc_runs/rhine2026_restore_20261110/`. Both copies can be deleted once this restore is no longer needed; keeping
the cluster copy makes the next restore a download only.

Download: from the JupyterLab page of the portal, one anchor per archive to
`/user/colon/files/dsc/runs/rhine2026/<archive>` with a `download` attribute, the five in parallel, about 12 MB per
second in all (five minutes). The files land in the Downloads folder under names of the form `<uuid>.tmp`; each is
recognized by its size and moved to a folder of its own.

## Extraction and checks

`../restore_extract.py` (run with `python -I`) checks the sha256 of an archive against the cluster's, takes only
regular files under `<run>/` or `<run>.log` for the runs of the list, overwrites nothing and keeps the modification
times of the cluster.

    python -I studies/rhine2026/cluster/restore_extract.py C:/dsc_runs/rhine2026_restore_20261110/rhine_restore_20261110_A.tgz <sha256> studies/rhine2026/cluster/restore_20261110/rhine_restore_20261110_A.runs.txt

Result: 2,568 files written (12.3 GB), the 129 logs already on disk had the same size as in the archives, no file
differed, none was left out. 129 folders, 46 with `firm_data.csv`, 11.7 GiB.

Checks after the restore:

- `si_tables.py --check --tag r6_bycargo --lists 20261102`: the 17 tables are recomputed and their numbers agree with
  the manuscript (Overleaf 2591144), including the four that could not be recomputed while the folders were gone
  (rates, channels, the forecast table of the main text and its table by sector).
- `paper_gate.py --regen --no-compile`: PASS. The 516 macros of `numbers.tex` and the 17 tables, regenerated from the
  restored folders, equal the manuscript; no input is reported missing. Report: `../../review/paper_gate_20261110_regen.md`.
- Every folder recorded on 6 November has its size of that day within 1 MiB.
