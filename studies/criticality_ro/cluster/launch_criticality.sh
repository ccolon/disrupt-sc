#!/bin/bash
#
# Romania per-edge criticality sweep (manifest p29) - Slurm launcher.
# GIT-ONLY workflow (no ssh/rsync from the laptop, as for the Rhine study):
#   laptop:  git push (disrupt-sc AND disrupt-sc-data)
#   cluster: git pull both repos, then
#            bash studies/criticality_ro/cluster/launch_criticality.sh
#   ... jobs run; the final job gathers results into
#   studies/criticality_ro/results/ , merges, generates the Tier-2 chunks and
#   COMMITS on the cluster -> git push there (or however Rhine results come
#   back), git pull on the laptop.
#   cluster: bash studies/criticality_ro/cluster/launch_criticality.sh --tier2
#
# Tier 1: setup job BUILDS the stage caches on the cluster (seed 42,
#   PYTHONHASHSEED=0 - the KI-34 determinism fix makes the build reproducible),
#   then 40 chunk jobs (42 edges each, duration 1, t_final 3) run afterok on
#   it, each injecting its chunk via DISRUPT_SC_EXTRA_CONFIG; per-chunk
#   results are resume-safe (re-submitting a failed chunk continues it).
# Tier 2: 15 chunk jobs over the top 150 (duration 4, t_final 6), generated
#   by the Tier-1 gather job.
#
# Usage:  bash launch_criticality.sh [--dry-run] [--tier2] [--only NN,NN] [--no-gather]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/criticality_ro"
TIME_SETUP="02:00:00"; MEM_SETUP="16G"
TIME_CHUNK="12:00:00"; MEM_CHUNK="16G"; CPUS_CHUNK=2   # smoke: ~10 min/edge at t_final 3 -> 42 edges = 7 h + margin
TIME_T2="12:00:00";    MEM_T2="16G"                    # ~10 heavy edges x ~40 min (t_final 6) + margin
TIME_GATHER="00:30:00"; MEM_GATHER="8G"
# ===========================================================================

ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
# PYTHONPATH: the cluster dsc env does not have disrupt-sc pip-installed
# (run_rhine.py sys.path-inserts src/ itself; `python -m disruptsc.run`
# needs the path exported instead)
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONPATH=${SCRIPT_DIR}/src && export PYTHONHASHSEED=0 && export PYTHONIOENCODING=utf-8 && cd ${SCRIPT_DIR}"
CHUNK_DIR="${SCRIPT_DIR}/studies/criticality_ro/chunks"
GATHER_SH="${SCRIPT_DIR}/studies/criticality_ro/cluster/gather_and_merge.sh"

DRY_RUN=false; TIER2=false; ONLY=""; GATHER=true
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)   DRY_RUN=true; shift ;;
        --tier2)     TIER2=true; shift ;;
        --only)      ONLY=$2; shift 2 ;;
        --no-gather) GATHER=false; shift ;;
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
    ls "${CHUNK_DIR}"/t2_chunk_*.yaml >/dev/null 2>&1 || { echo "t2 chunks missing - the tier-1 gather job generates them; git pull first"; exit 1; }
    T2IDS=""
    for yml in "${CHUNK_DIR}"/t2_chunk_*.yaml; do
        nn=$(basename "$yml" .yaml | sed 's/t2_chunk_//')
        jid=$(submit "crit_t2_${nn}" "$TIME_T2" "$MEM_T2" "" \
            "export DISRUPT_SC_EXTRA_CONFIG=${yml} && python -m disruptsc.run Romania --seed 42 --cache auto")
        T2IDS="${T2IDS}:${jid}"
    done
    if $GATHER; then
        submit "crit_gather_t2" "$TIME_GATHER" "$MEM_GATHER" "${T2IDS#:}" \
            "bash ${GATHER_SH} t2"
    fi
    echo "tier-2 jobs submitted"
    exit 0
fi

# Setup: build (or validate) the stage caches once, so the 40 chunk jobs load
# the same world instead of racing to rebuild it into the shared tmp/.
SETUP=$(submit "crit_setup" "$TIME_SETUP" "$MEM_SETUP" "" \
    "python -m disruptsc.run Romania --simulation_type initial_state --seed 42 --cache auto")
echo "setup (cache build) job: ${SETUP}"

T1IDS=""
for yml in "${CHUNK_DIR}"/t1_chunk_*.yaml; do
    nn=$(basename "$yml" .yaml | sed 's/t1_chunk_//')
    if [[ -n "$ONLY" && ",$ONLY," != *",$nn,"* ]]; then continue; fi
    jid=$(submit "crit_t1_${nn}" "$TIME_CHUNK" "$MEM_CHUNK" "$SETUP" \
        "export DISRUPT_SC_EXTRA_CONFIG=${yml} && python -m disruptsc.run Romania --seed 42 --cache auto")
    T1IDS="${T1IDS}:${jid}"
done
echo "tier-1 chunk jobs submitted (afterok:${SETUP})"
if $GATHER && [[ -z "$ONLY" ]]; then
    submit "crit_gather_t1" "$TIME_GATHER" "$MEM_GATHER" "${T1IDS#:}" \
        "bash ${GATHER_SH} t1"
    echo "gather+merge job queued after all chunks; it COMMITS the results -"
    echo "push from the cluster (or your usual channel), git pull on the laptop,"
    echo "then: bash studies/criticality_ro/cluster/launch_criticality.sh --tier2"
fi
