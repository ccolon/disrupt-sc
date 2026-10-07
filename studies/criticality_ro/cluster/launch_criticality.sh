#!/bin/bash
#
# Romania per-edge criticality sweep (manifest p29) - Slurm launcher.
#
# Tier 1: 40 chunk jobs (studies/criticality_ro/chunks/t1_chunk_*.yaml,
#         ~42 edges each, duration 1 week, t_final 3). Each task injects its
#         chunk through DISRUPT_SC_EXTRA_CONFIG and writes resume-safe
#         results to output/Romania/criticality/t1_chunk_NN/. A parity job
#         runs FIRST: it validates the synced caches by checking that a
#         seed-42 baseline reproduces the laptop fingerprints (the chunk
#         jobs depend on it with afterok).
# Tier 2: after merging tier 1 on the laptop (merge_results.py writes
#         chunks/t2_top150.yaml), launch with --tier2 (single job,
#         150 edges, duration 4, t_final 6).
#
# Usage:  bash studies/criticality_ro/cluster/launch_criticality.sh [--dry-run] [--tier2] [--only NN,NN]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/criticality_ro"
TIME_CHUNK="12:00:00"; MEM_CHUNK="16G"; CPUS_CHUNK=2   # smoke: ~10 min/edge at t_final 3 -> 42 edges = 7 h + margin
TIME_T2="12:00:00";    MEM_T2="16G"                    # ~10 heavy edges x ~40 min (t_final 6) + margin
TIME_PARITY="01:00:00"; MEM_PARITY="16G"
# ===========================================================================

ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0 && export PYTHONIOENCODING=utf-8 && cd ${SCRIPT_DIR}"
CHUNK_DIR="${SCRIPT_DIR}/studies/criticality_ro/chunks"

DRY_RUN=false; TIER2=false; ONLY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --tier2)   TIER2=true; shift ;;
        --only)    ONLY=$2; shift 2 ;;
        *) shift ;;
    esac
done
$DRY_RUN || mkdir -p "$SLURM_LOG_DIR"

submit() {   # job time mem dep payload -> job id
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 --cpus-per-task=${CPUS_CHUNK} --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}";
    else eval "$cmd"; fi
}

if $TIER2; then
    ls "${CHUNK_DIR}"/t2_chunk_*.yaml >/dev/null 2>&1 || { echo "t2 chunks missing - run merge_results.py --prefix t1 first and git pull"; exit 1; }
    for yml in "${CHUNK_DIR}"/t2_chunk_*.yaml; do
        nn=$(basename "$yml" .yaml | sed 's/t2_chunk_//')
        submit "crit_t2_${nn}" "$TIME_T2" "$MEM_T2" "" \
            "export DISRUPT_SC_EXTRA_CONFIG=${yml} && python -m disruptsc.run Romania --seed 42 --cache auto"
    done
    echo "tier-2 chunk jobs submitted"
    exit 0
fi

# Parity gate: an initial_state on the synced caches must COME UP from cache
# (a cache rebuild here means the data/code on the cluster differ from the
# laptop - investigate before burning 40 jobs). grep is the assertion.
PARITY=$(submit "crit_parity" "$TIME_PARITY" "$MEM_PARITY" "" \
    "python -m disruptsc.run Romania --simulation_type initial_state --seed 42 --cache auto 2>&1 | tee /tmp/crit_parity.log && grep -q 'Loaded cache agents' /tmp/crit_parity.log && grep -q 'Loading logistic routes from cache' /tmp/crit_parity.log")
echo "parity job: ${PARITY}"

for yml in "${CHUNK_DIR}"/t1_chunk_*.yaml; do
    nn=$(basename "$yml" .yaml | sed 's/t1_chunk_//')
    if [[ -n "$ONLY" && ",$ONLY," != *",$nn,"* ]]; then continue; fi
    submit "crit_t1_${nn}" "$TIME_CHUNK" "$MEM_CHUNK" "$PARITY" \
        "export DISRUPT_SC_EXTRA_CONFIG=${yml} && python -m disruptsc.run Romania --seed 42 --cache auto"
done
echo "tier-1 chunk jobs submitted (afterok:${PARITY})"
echo "collect with: studies/criticality_ro/cluster/collect_from_cluster.sh, then merge_results.py --prefix t1"
