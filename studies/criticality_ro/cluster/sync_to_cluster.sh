#!/bin/bash
#
# Romania criticality sweep - sync data and caches to the cluster.
#
# The Romania scope data ALSO lives in the disrupt-sc-data git repo (committed
# 7 Oct 2026), so `git pull` on the cluster is the primary channel; this rsync
# is the belt-and-braces direct copy (and the only channel for the stage
# caches, which never enter git). Caches travel from the laptop so every array
# task loads the SAME world (tmp/Romania_*.pkl, ~hundreds of MB) instead of
# rebuilding it.
#
# Usage (Git Bash / WSL): bash studies/criticality_ro/cluster/sync_to_cluster.sh [--dry-run]
#
set -e
# ========================= EDIT FOR YOUR CLUSTER ===========================
CLUSTER="user@cluster"                                   # ssh target
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
LOCAL_CODE="/c/Users/Celian/OneDrive/DisruptSC/disrupt-sc"
LOCAL_DATA="/c/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data"
# ===========================================================================
DRY=""; [[ "${1:-}" == "--dry-run" ]] && DRY="--dry-run"

rsync -av ${DRY} --exclude 'runs/' --exclude '*.log' --exclude '*pre_*' \
    --exclude 'crossval/' --exclude '*.docx' --exclude '*.png' --exclude '*.qgz' \
    "${LOCAL_DATA}/Romania/" "${CLUSTER}:${DATA_PATH}/Romania/"

rsync -av ${DRY} \
    "${LOCAL_CODE}/tmp/"Romania_agents.pkl        "${LOCAL_CODE}/tmp/"Romania_agents.fp.json \
    "${LOCAL_CODE}/tmp/"Romania_sc_network.pkl    "${LOCAL_CODE}/tmp/"Romania_sc_network.fp.json \
    "${LOCAL_CODE}/tmp/"Romania_logistic_routes.pkl "${LOCAL_CODE}/tmp/"Romania_logistic_routes.fp.json \
    "${LOCAL_CODE}/tmp/"Romania_transport_network.pkl "${LOCAL_CODE}/tmp/"Romania_transport_network.fp.json \
    "${CLUSTER}:${SCRIPT_DIR}/tmp/"

echo "synced Romania data and caches to ${CLUSTER}"
echo "now: ssh ${CLUSTER} 'cd ${SCRIPT_DIR} && git pull && git log -1 --oneline'"
echo "     (code commit must include the DISRUPT_SC_EXTRA_CONFIG overlay and config/user_defined_Romania.yaml)"
