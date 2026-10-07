# Romania per-edge criticality sweep (manifest p29)

One-week closure of every domestic road / railway / waterway edge that
carries baseline flow (1,680 of 2,345 edges — zero-flow closures provably
cause zero loss), then a 4-week re-run of the top 150. Loss metric:
household + country loss relative to the no-disruption reference (the raw
columns carry a constant offset that `merge_results.py` subtracts).
Reference baseline: run `20260928_142628` (v21), slimmed into
`reference_edges.geojson` so every step works from the git checkout alone.

Everything travels by git — no ssh/rsync (same flow as the Rhine study).

## Laptop (once)

```bash
git push                      # disrupt-sc (this folder, incl. chunks/)
cd ../disrupt-sc-data && git push    # Romania data (committed 94b02d5)
```

## Cluster

```bash
cd /projects/disruptsc/disrupt-sc        && git pull
cd /projects/disruptsc/disrupt-sc-data   && git pull
cd /projects/disruptsc/disrupt-sc
bash studies/criticality_ro/cluster/launch_criticality.sh
```

This submits: one **setup job** that builds the stage caches (seed 42,
PYTHONHASHSEED=0 — deterministic build), then **40 chunk jobs** (afterok,
~42 edges each, ≈7 h at the smoke-measured ~10 min/edge), then one
**gather job** that collects the chunk CSVs into
`studies/criticality_ro/results/t1_chunks/`, merges them
(`results/t1_merged/criticality_ranked.csv` + `criticality_map.geojson`),
generates `chunks/t2_chunk_*.yaml` (top 150, duration 4) and **commits**.

Then, still on the cluster:

```bash
git push                                             # bring tier-1 back
bash studies/criticality_ro/cluster/launch_criticality.sh --tier2
# ... 15 jobs + gather (commits results/t2_merged/) ...
git push
```

On the laptop: `git pull` → `results/t1_merged/criticality_map.geojson`
is the QGIS layer (columns: household/country/total loss in mUSD per
closure event, loss_per_kt, loss_per_km).

## Notes

- A failed/preempted chunk is **resume-safe**: re-submit it alone with
  `launch_criticality.sh --only NN` (its CSV continues where it stopped).
- The per-task chunk configs are injected through `DISRUPT_SC_EXTRA_CONFIG`
  (config.py overlay); proven fingerprint-neutral, so all tasks share the
  setup job's caches.
- `t_final: 3` is pinned in the chunk configs — the scope config's own
  `t_final` would otherwise override the criticality horizon and triple
  the cost (smoke-test lesson).
- Edit the `EDIT FOR YOUR CLUSTER` block in `cluster/launch_criticality.sh`
  (paths, env) before the first launch.
