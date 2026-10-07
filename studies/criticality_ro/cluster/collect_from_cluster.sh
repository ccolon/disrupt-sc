#!/bin/bash
#
# Pull the Romania criticality results back from the cluster (CSV +
# fingerprints only - a few KB per chunk; nothing heavy is exported).
#
# Usage: bash studies/criticality_ro/cluster/collect_from_cluster.sh [--dry-run]
#
set -e
# ========================= EDIT FOR YOUR CLUSTER ===========================
CLUSTER="user@cluster"
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
LOCAL_CODE="/c/Users/Celian/OneDrive/DisruptSC/disrupt-sc"
# ===========================================================================
DRY=""; [[ "${1:-}" == "--dry-run" ]] && DRY="--dry-run"

rsync -av ${DRY} \
    "${CLUSTER}:${SCRIPT_DIR}/output/Romania/criticality/" \
    "${LOCAL_CODE}/output/Romania/criticality/"

echo "collected; next: python studies/criticality_ro/merge_results.py --prefix t1"
