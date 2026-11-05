#!/bin/bash
#
# Cambodia compound-flood paper (5 Nov 2026): one Slurm job per line of a job list, through
# studies/cambodia/run_cambodia.py (standard pipeline, paper_config.yaml, one named build cache per seed).
#
# Job list: one run per line, "#" comments allowed:
#     <seed> <scenario> <duration> [run_cambodia.py options...]
# e.g.  3 lag13 12
#       3 lag13 12 --set inventory_restoration_time=4
#       3 simul 12 --cache-dir cam_fc07_s3 --set flow_coverage=0.7
# A line whose options change the BUILD (flow_coverage, nb_suppliers_per_input, use_route_cache, logistics
# costs, capacities, ...) must name its own --cache-dir: the launcher submits one setup job per distinct
# (seed, cache dir), with that pair's first line's options, and every run of the pair waits for it (afterok),
# so that two jobs never build the same cache at once. Runtime switches (restoration time, inventories,
# behavioural options, disruptions) reuse the seed's cache.
#
# Runs write on the node's local disk (TMPDIR) and are copied to OUTPUT_DIR/<batch>/<run name> when they end
# (the Rhine lesson of 1 Nov 2026: writes to the project volume failed mid-run with exit status 120).
#
# Usage: bash studies/cambodia/cluster/launch_cambodia.sh --jobs FILE --batch NAME [--dry-run]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="/projects/disruptsc/runs/cambodia"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/cambodia"
TIME_RUN="08:00:00"; MEM_RUN="8G"           # 180 daily steps at ~20-35 s (laptop, 5 Nov), ~3 GB RAM
TIME_SETUP="01:00:00"; MEM_SETUP="8G"
# ===========================================================================

JOBS_FILE=""; BATCH=""; DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --jobs)    JOBS_FILE=$2; shift 2 ;;
        --batch)   BATCH=$2; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        *) echo "unknown option $1" >&2; exit 2 ;;
    esac
done
[[ -f "$JOBS_FILE" && -n "$BATCH" ]] || { echo "usage: $0 --jobs FILE --batch NAME [--dry-run]" >&2; exit 2; }

ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0 && export PYTHONIOENCODING=utf-8 && cd ${SCRIPT_DIR}"
RUNNER="python studies/cambodia/run_cambodia.py"
DEST="${OUTPUT_DIR}/${BATCH}"
$DRY_RUN || mkdir -p "$DEST" "$SLURM_LOG_DIR"

submit() {   # name time mem dependency payload -> job id
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}"; return; fi
    sbatch --parsable --nodes=1 --ntasks=1 --cpus-per-task=1 --time="${timelimit}" --mem="${mem}" ${depflag} \
        --job-name="${job}" --output="${SLURM_LOG_DIR}/${job}.%j.out" \
        --wrap="bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'"
}

declare -A SETUP_ID
n=0
while read -r seed scenario duration opts; do
    [[ -z "$seed" || "$seed" == \#* ]] && continue
    cache=$(sed -n 's/.*--cache-dir[ =]\([^ ]*\).*/\1/p' <<< "$opts"); cache=${cache:-cam_s${seed}}
    key="${seed}:${cache}"
    if [[ -z "${SETUP_ID[$key]}" ]]; then
        SETUP_ID[$key]=$(submit "cam_setup_${cache}" "$TIME_SETUP" "$MEM_SETUP" "" \
            "${RUNNER} --setup --seed ${seed} --cache-dir ${cache} ${opts}")
    fi
    tag=$(sed -e 's/--cache-dir[ =][^ ]*//' -e 's/--set //g' -e 's/[^A-Za-z0-9.=_-]\+/_/g' -e 's/^_//;s/_$//' <<< "$opts")
    name="${scenario}_d${duration}_s${seed}${tag:+_${tag}}"
    payload="out=\${TMPDIR:-/tmp}/${name} && mkdir -p \$out && ${RUNNER} --seed ${seed} --scenario ${scenario} --duration ${duration} --cache-dir ${cache} ${opts} --out \$out; rc=\$?; for i in \$(seq 20); do cp -r \$out ${DEST}/ && break; sleep 90; done; exit \$rc"
    submit "cam_${name}" "$TIME_RUN" "$MEM_RUN" "${SETUP_ID[$key]}" "$payload" > /dev/null
    n=$((n + 1))
done < "$JOBS_FILE"
echo "${n} runs submitted for batch ${BATCH} (${#SETUP_ID[@]} setup jobs); outputs in ${DEST}"
