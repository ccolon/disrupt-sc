#!/bin/bash
#
# Pack the small outputs of a Rhine batch into one archive for download through the portal's file
# browser (no ssh needed): per run analysis.txt, figures/, country_data.csv, household_data.csv,
# routing_summary.csv, parameters.yaml, run_fingerprint.json, the .log, plus the batch comparison.
# firm_data.csv (35-100 MB per run) is packed only for the runs named with --with-firms.
#
# Usage (on the cluster):  bash studies/rhine2026/cluster/pack_results.sh [--jobs jobs_YYYYMMDD.txt] [--with-firms name1,name2]
#   --jobs: pack the runs named in that job list (default: every run folder holding an exp.log)
#   --with-firms: full run names whose firm_data.csv is packed too (35-140 MB each)
#
set -e
# ========================= EDIT FOR YOUR CLUSTER ===========================
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
# ===========================================================================
WITH_FIRMS=""; JOBS=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --with-firms) WITH_FIRMS="$2"; shift 2 ;;
        --jobs) JOBS="$2"; shift 2 ;;
        *) echo "unknown argument $1" >&2; exit 1 ;;
    esac
done
if [[ -n "$JOBS" ]]; then
    RUNS=$(grep -vE '^\s*#|^\s*$' "$JOBS" | cut -d'|' -f1 | xargs -n1 echo)
else
    RUNS=$(cd "$OUTPUT_DIR" && for d in */; do [[ -f "$d/exp.log" ]] && echo "${d%/}"; done)
fi
cd "$OUTPUT_DIR"
stamp=$(date +%Y%m%d_%H%M)
list=$(mktemp)
for d in $RUNS; do
    [[ -d "$d" ]] || continue
    for f in analysis.txt country_data.csv household_data.csv routing_summary.csv parameters.yaml run_fingerprint.json figures.log mrio_by_sector.csv mrio_by_region.csv mrio_by_country.csv; do
        [[ -f "$d/$f" ]] && echo "$d/$f" >> "$list"
    done
    [[ -d "$d/figures" ]] && find "$d/figures" -type f >> "$list"
    [[ -f "$d.log" ]] && echo "$d.log" >> "$list"
    if [[ -n "$WITH_FIRMS" && ",${WITH_FIRMS}," == *",${d},"* && -f "$d/firm_data.csv" ]]; then
        echo "$d/firm_data.csv" >> "$list"
        # the geojson tables scenario_figures.py needs (F5 draws the network; 16 Sep: transport_edges/nodes and
        # country_table were missing from the 15-16 Sep archives and had to be copied from an older run)
        for g in firm_table.geojson household_table.geojson country_table.geojson transport_edges.geojson transport_nodes.geojson; do
            [[ -f "$d/$g" ]] && echo "$d/$g" >> "$list"
        done
    fi
done
ls compare_runs_batch.* >> "$list" 2>/dev/null || true
tar czf "rhine_batch_${stamp}.tgz" -T "$list"
rm -f "$list"
du -h "rhine_batch_${stamp}.tgz"
echo "download ${OUTPUT_DIR}/rhine_batch_${stamp}.tgz through the portal and unpack it into C:\\dsc_runs\\rhine2026"
