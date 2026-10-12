#!/bin/bash
#
# Rhine 2026 — recompute the batch tables with the country-sector value-added ratios (12 Oct 2026, review E1).
#
# No simulation is rerun: compare_runs.py is rerun on the existing run folders of every job list, exactly as the
# launcher's compare job does, and the resulting csv/txt are packed. Run on the cluster after `git pull` to the commit
# that carries studies/rhine2026/va_shares.py (the ratio of each firm's own country-sector, read from the run's
# firm_table.geojson, else from additional_data/va_share_by_region_sector.csv).
#
#     bash studies/rhine2026/cluster/recompare_20261012.sh            # all lists below
#     bash studies/rhine2026/cluster/recompare_20261012.sh jobs_20261007_main.txt   # one list
#
# Then download rhine_compare_20261012.tgz from OUTPUT_DIR and extract it into C:\dsc_runs\rhine2026.
set -e

# ========================= EDIT FOR YOUR CLUSTER (same as launch_rhine_batch.sh) ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
# ===========================================================================================================

cd "$SCRIPT_DIR"
export PYTHONPATH=src
PY="${PYTHON_ENV}/bin/python"
LISTS=("$@")
if [[ ${#LISTS[@]} -eq 0 ]]; then
    LISTS=(jobs_20261007_main.txt jobs_20261007_paired.txt jobs_20261007_rev.txt jobs_20261007_ladder.txt jobs_20261009_cross.txt
           jobs_20260930_main.txt jobs_20260930_paired.txt)
fi
for L in "${LISTS[@]}"; do
    tag=$(basename "$L" .txt)
    dirs=""
    while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        name=$(echo "$line" | cut -d'|' -f1 | xargs)
        [[ -d "${OUTPUT_DIR}/${name}" ]] && dirs="${dirs} ${OUTPUT_DIR}/${name}"
    done < "studies/rhine2026/cluster/${L}"
    echo "== ${tag}: $(echo $dirs | wc -w) run folders"
    $PY studies/rhine2026/compare_runs.py ${dirs} --weekly DEU --csv "${OUTPUT_DIR}/compare_runs_batch_${tag}.csv" > "${OUTPUT_DIR}/compare_runs_batch_${tag}.txt" 2>&1
    tail -2 "${OUTPUT_DIR}/compare_runs_batch_${tag}.txt"
done
cd "$OUTPUT_DIR"
tar czf rhine_compare_20261012.tgz compare_runs_batch_jobs_*.csv compare_runs_batch_jobs_*.txt
echo "packed ${OUTPUT_DIR}/rhine_compare_20261012.tgz"
