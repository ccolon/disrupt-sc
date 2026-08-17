#!/bin/bash
#
# TENT flood-event campaign — per-event supply-chain losses.
#
# Flood events (catchments x return periods) from
# <DATA>/TENT/Disruption/results_disrupt_sc_v1.xlsx. Each event closes its flooded
# road edges (100% capacity) for its recovery_duration and runs the economy for
# exactly 2 x that duration (weekly steps, NO epsilon early-stop).
#
# Locked decisions: weekly resolution, full closure, flow_coverage=1.0, all events,
# per-event losses only. (recovery_duration is converted days -> weeks in run_sweep.)
#
# Job graph:
#   (1) one BUILD job    -> build + cache the pre-disruption snapshot once
#   (2) NUM_SHARDS WORKER jobs (afterok build) -> each runs events i%%N==shard
#   (3) one COMBINE job  (afterok all workers) -> merge shard CSVs -> event_losses.csv
#
# Each worker writes its own event_losses_shard{k}of{N}.csv and is independently
# resumable: re-submitting skips events already in its CSV. A crashed worker just
# re-runs its remaining events.
#
# Usage:
#     bash studies/TENT/launch_tent_flood.sh                 # submit build+24 workers+combine
#     bash studies/TENT/launch_tent_flood.sh --dry-run
#     bash studies/TENT/launch_tent_flood.sh --num-shards 12

set -e

# ===================== EDIT THESE FOR YOUR CLUSTER =========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"                       # repo root on the cluster
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"        # conda env with pyarrow+openpyxl
DATA_PATH="/projects/disruptsc/disrupt-sc-data"                   # DISRUPT_SC_DATA_PATH root
OUTPUT_DIR="${SCRIPT_DIR}/output/TENT/flood_sweep"                # shard CSVs + snapshot land here
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/tent_flood"
# ===========================================================================

# flow_coverage=1.0 is the model's configured/validated value for TENT. Lowering
# it changes losses by orders of magnitude (0.8 gave ~2500x smaller losses in
# testing) — it is NOT just a speed knob. Sharding on SLURM makes 1.0 tractable
# (~7 h/shard at NUM_SHARDS=24), so we keep full fidelity.
FLOW_COVERAGE=1.0
NUM_SHARDS=24
TIME_LIMIT_BUILD="01:00:00"
TIME_LIMIT_WORKER="12:00:00"
TIME_LIMIT_COMBINE="00:20:00"
MEM_BUILD="8G"
MEM_WORKER="6G"          # ~1.5 GB snapshot + ~1.5 GB deepcopy per event, with headroom
MEM_COMBINE="2G"

DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)     DRY_RUN=true; shift ;;
        --num-shards)  NUM_SHARDS=$2; shift 2 ;;
        --flow-coverage) FLOW_COVERAGE=$2; shift 2 ;;
        *) shift ;;
    esac
done

XLSX="${DATA_PATH}/TENT/Disruption/results_disrupt_sc_v1.xlsx"
SNAPSHOT="${OUTPUT_DIR}/baseline_snapshot.pkl"
OUT_CSV="${OUTPUT_DIR}/event_losses.csv"
SWEEP="${SCRIPT_DIR}/studies/TENT/run_sweep.py"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH}"

if ! $DRY_RUN; then
    mkdir -p "$OUTPUT_DIR" "$SLURM_LOG_DIR"
fi

submit() {  # echoes the job id (or a fake one under --dry-run)
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""
    [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 \
        --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then
        echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2
        echo "000${RANDOM}"
    else
        eval "$cmd"
    fi
}

# ---- (1) BUILD: cache the pre-disruption snapshot once --------------------
# --rebuild forces a fresh build: the fingerprint keys off config + git SHA, NOT
# the transport.gpkg contents, so a changed network would otherwise be masked by
# a stale cache. The build job runs once (~2 min), so always rebuilding is cheap.
BUILD_PAYLOAD="python ${SWEEP} --build-only --rebuild --flow-coverage ${FLOW_COVERAGE} --snapshot ${SNAPSHOT}"
BUILD_ID=$(submit "tent_build" "$TIME_LIMIT_BUILD" "$MEM_BUILD" "" "$BUILD_PAYLOAD")
echo "[build] job ${BUILD_ID}"

# ---- (2) WORKERS: one shard each, afterok the build ----------------------
WORKER_IDS=""
for (( k=0; k<NUM_SHARDS; k++ )); do
    WP="python ${SWEEP} --shard ${k} --of ${NUM_SHARDS} \
        --flow-coverage ${FLOW_COVERAGE} --snapshot ${SNAPSHOT} \
        --xlsx ${XLSX} --out ${OUT_CSV}"
    WID=$(submit "tent_w${k}of${NUM_SHARDS}" "$TIME_LIMIT_WORKER" "$MEM_WORKER" "$BUILD_ID" "$WP")
    WORKER_IDS="${WORKER_IDS}${WORKER_IDS:+:}${WID}"
    echo "[worker ${k}] job ${WID}"
done

# ---- (3) COMBINE: merge shard CSVs, afterok all workers ------------------
CP="python ${SCRIPT_DIR}/studies/TENT/combine_shards.py \
    --dir ${OUTPUT_DIR} --num-shards ${NUM_SHARDS} --out ${OUT_CSV}"
CID=$(submit "tent_combine" "$TIME_LIMIT_COMBINE" "$MEM_COMBINE" "$WORKER_IDS" "$CP")
echo "[combine] job ${CID}"

echo
echo "Submitted: 1 build + ${NUM_SHARDS} workers + 1 combine"
echo "  flow_coverage=${FLOW_COVERAGE}, ~$((917 / NUM_SHARDS)) events/shard"
echo "  snapshot: ${SNAPSHOT}"
echo "  result:   ${OUT_CSV}"
echo "  logs:     ${SLURM_LOG_DIR}"
