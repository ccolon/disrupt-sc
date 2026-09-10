#!/bin/bash
#
# Pack the small outputs of a Rhine batch into one archive for download through the portal's file
# browser (no ssh needed): per run analysis.txt, figures/, country_data.csv, household_data.csv,
# routing_summary.csv, parameters.yaml, run_fingerprint.json, the .log, plus the batch comparison.
# firm_data.csv (35-100 MB per run) is packed only for the runs named with --with-firms.
#
# Usage (on the cluster):  bash studies/rhine2026/cluster/pack_results.sh [--with-firms base,package]
#
set -e
# ========================= EDIT FOR YOUR CLUSTER ===========================
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
# ===========================================================================
WITH_FIRMS=""
[[ "${1:-}" == "--with-firms" ]] && WITH_FIRMS="${2:-}"
cd "$OUTPUT_DIR"
stamp=$(date +%Y%m%d_%H%M)
list=$(mktemp)
for d in 2026_fc0910_*/; do
    d=${d%/}
    for f in analysis.txt country_data.csv household_data.csv routing_summary.csv parameters.yaml run_fingerprint.json figures.log; do
        [[ -f "$d/$f" ]] && echo "$d/$f" >> "$list"
    done
    [[ -d "$d/figures" ]] && find "$d/figures" -type f >> "$list"
    [[ -f "$d.log" ]] && echo "$d.log" >> "$list"
    if [[ -n "$WITH_FIRMS" && ",${WITH_FIRMS}," == *",${d#2026_fc0910_},"* && -f "$d/firm_data.csv" ]]; then
        echo "$d/firm_data.csv" >> "$list"
    fi
done
ls compare_runs_batch.* >> "$list" 2>/dev/null || true
tar czf "rhine_batch_${stamp}.tgz" -T "$list"
rm -f "$list"
du -h "rhine_batch_${stamp}.tgz"
echo "download ${OUTPUT_DIR}/rhine_batch_${stamp}.tgz through the portal and unpack it into C:\\dsc_runs\\rhine2026"
