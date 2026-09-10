#!/bin/bash
#
# Copy what a Rhine 2026 batch needs to the cluster: the EU scope data (33 MB) and the stage caches
# (tmp/EU_*.pkl + .fp.json, ~1.7 GB, so that jobs do not rebuild the network, agents, supply chain and
# routes: ~45 min and 13 GB each). The code travels by git (pull to the commit named in the jobs file).
# The run outputs come back with collect_from_cluster.sh.
#
# Usage (from the laptop, Git Bash or WSL with rsync; fall back to scp -r for the two folders):
#     bash studies/rhine2026/cluster/sync_to_cluster.sh [--dry-run]
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

rsync -av ${DRY} --exclude 'runs/' --exclude '*.log' "${LOCAL_DATA}/EU/" "${CLUSTER}:${DATA_PATH}/EU/"
rsync -av ${DRY} "${LOCAL_CODE}/tmp/"EU_agents.pkl "${LOCAL_CODE}/tmp/"EU_agents.fp.json \
    "${LOCAL_CODE}/tmp/"EU_sc_network.pkl "${LOCAL_CODE}/tmp/"EU_sc_network.fp.json \
    "${LOCAL_CODE}/tmp/"EU_logistic_routes.pkl "${LOCAL_CODE}/tmp/"EU_logistic_routes.fp.json \
    "${LOCAL_CODE}/tmp/"EU_transport_network.pkl "${LOCAL_CODE}/tmp/"EU_transport_network.fp.json \
    "${CLUSTER}:${SCRIPT_DIR}/tmp/"
echo "synced EU data and caches to ${CLUSTER}; now: ssh ${CLUSTER} 'cd ${SCRIPT_DIR} && git pull && git log -1 --oneline'"
