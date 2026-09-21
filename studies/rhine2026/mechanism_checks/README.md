# Mechanism checks of the modal-switch rule (14-15 Sep 2026): archived evidence

Archived on 21 Sep 2026 from the session scratch folder under the Windows Temp directory, which Windows
clears by age. Everything older than the evening of 14 Sep had already been lost when this copy was made.

## What is here

Outputs, verified on 21 Sep against the numbers quoted in `disrupt-sc-data/EU/calibration_log.md`:

| file | content | check |
|---|---|---|
| `lh_classification.csv` | the 2,831 Kaub-crossing bulk OD pairs under the kilometre rule (access 50 km, line haul 100 km) | 1,553 give up, 1,224 deliver on own modes, 54 on the free path |
| `lh_classification_bulk.csv` | same pairs under the adopted rule (road never a line-haul mode for bulk) | 2,328 / 425 / 78 |
| `lh_links.csv`, `lh_links_bulk.csv` | the per-link version of the two tables (5,707 links) | |
| `lh_sensitivity.txt` | threshold sensitivity of the give-up share (5 % to 97 %) | |
| `mechanism_check_lh*.txt` | printed reports of the classification runs | |
| `compare_links_base_vs_lh.txt`, `compare_links_lh_vs_lhb.txt` | link-level comparison of the ten-week runs, weeks 6-7 | run = offline prediction, link by link |

Scripts that produced them: `mechanism_check_lh.py`, `mechanism_check_lh_full.py`,
`mechanism_check_lhb_full.py`, `lh_links.py`, `lh_sensitivity.py`, `compare_links_pair.py`.

## What this archive is not

**The scripts do not run as they stand.** They are kept as a record of the method, unedited.

1. Each hard-codes the Temp scratch path.
2. Four of them read `link_route_flags.csv` (the baseline route flags of all 1.38 M links: crosses Kaub,
   uses the Lower Rhine, uses the upstream Rhine). That 83 MB table was built on 14 Sep from the routes
   cache and was lost in the Temp cleanup. Its builder was never committed. It has to be rebuilt from
   `tmp/EU_logistic_routes.pkl` with a committed script before the classification can be rerun.
3. `compare_links_pair.py` and the order-weighting step of the mechanism scripts read the ten-week
   diagnostic runs (`lrcheck_base`, `lrcheck_base_lh`, `lrcheck_base_lhb`, ...) under
   `C:\dsc_runs\rhine2026`. Those folders were deleted on 16 Sep to free disk. Their results are in the
   calibration log; rerunning these scripts needs the runs regenerated (about 2.5 h each, full exports,
   `EU/runs/lowerrhine_linehaul_check.ps1` and `lowerrhine_linehaul_bulk_check.ps1`).

The offline route classification (no run data needed) is the part that can be made reproducible once
item 2 is done. Until then, section S4 of the SI rests on archived outputs, not on a rerunnable pipeline.

Note on the routes cache: it was rebuilt on 17 Sep after KI-37 (edge costs no longer scale with the time
step; stage versions bumped). At weekly resolution the removed factor was exactly 1, so costs are
bit-identical for this scope, and the set of links whose price moves in a surcharge week is identical
before and after (13,113 links, checked 21 Sep on the two full-export twins).
