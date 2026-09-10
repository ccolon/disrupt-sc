#!/bin/bash
#
# Bring the batch outputs back to the laptop's run folder (C:\dsc_runs\rhine2026, outside OneDrive):
# firm/household/country series, analysis.txt, figures, the batch comparison. household_data_by_sector.csv
# is dropped on the cluster by the postprocess job; link/inventory data are not written (light exports).
#
# Usage:  bash studies/rhine2026/cluster/collect_from_cluster.sh [--dry-run]
#
set -e
# ========================= EDIT FOR YOUR CLUSTER ===========================
CLUSTER="user@cluster"
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
LOCAL_RUNS="/c/dsc_runs/rhine2026"
# ===========================================================================
DRY=""; [[ "${1:-}" == "--dry-run" ]] && DRY="--dry-run"
rsync -av ${DRY} --exclude 'household_data_by_sector.csv' --exclude '*.geojson' "${CLUSTER}:${OUTPUT_DIR}/" "${LOCAL_RUNS}/"
echo "collected into ${LOCAL_RUNS}; compare with: python studies/rhine2026/compare_runs.py ${LOCAL_RUNS}/2026_fc0910_* --weekly DEU"
