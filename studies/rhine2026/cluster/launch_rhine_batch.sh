#!/bin/bash
#
# DisruptSC Rhine 2026 — cluster batch of scenario runs (adaptation counterfactuals + sensitivity grid).
#
# One Slurm job per line of the jobs file (default cluster/jobs_20260910.txt): the base run is submitted
# first and validates or builds the shared caches (tmp/EU_*.pkl); every other run depends on it
# (afterok) so that no two jobs build the same cache, except runs that carry --cache-isolation (they
# rebuild in a private cache). A postprocess job (analyze_scenario.py --no-links + figures) follows each
# run, and one compare_runs.py job follows the whole batch.
#
# Usage:  bash studies/rhine2026/cluster/launch_rhine_batch.sh [--dry-run] [--jobs FILE] [--only NAME,NAME]
#
# Before the first batch on a new cluster: sync_to_cluster.sh (EU data + caches), git pull to the commit
# named in the jobs file, and check that config/user_defined_EU.yaml resolves its data through
# DISRUPT_SC_DATA_PATH (the EU config uses "repo:" paths and the scope data folder, no absolute paths).
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/rhine2026"
TIME_RUN="16:00:00";  MEM_RUN="20G";  CPUS_RUN=2      # up to 43 weekly steps at ~10 min (+ build), ~13 GB RAM on the laptop
TIME_POST="01:00:00"; MEM_POST="12G"
# ===========================================================================

COMMON="--profile 2026 --no-open --seed 42 --recovery-weeks 12 --light-export"
JOBS_FILE="${SCRIPT_DIR}/studies/rhine2026/cluster/jobs_20260913.txt"
DRY_RUN=false
ONLY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --jobs)    JOBS_FILE=$2; shift 2 ;;
        --only)    ONLY=$2; shift 2 ;;
        *) shift ;;
    esac
done

ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0 && export PYTHONIOENCODING=utf-8 && cd ${SCRIPT_DIR}"
$DRY_RUN || mkdir -p "$OUTPUT_DIR" "$SLURM_LOG_DIR"

submit() {   # job time mem cpus dependency payload -> job id
    local job=$1 timelimit=$2 mem=$3 cpus=$4 dep=$5 payload=$6
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 --cpus-per-task=${cpus} --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}";
    else eval "$cmd"; fi
}

wanted() {   # --only filter
    [[ -z "$ONLY" ]] && return 0
    [[ ",${ONLY}," == *",$1,"* ]]
}

BASE_ID=""
ALL_IDS=""
RUN_DIRS=""
while IFS='|' read -r name flags; do
    # trim with parameter expansion (xargs would choke on quotes in comment lines)
    name="${name#"${name%%[![:space:]]*}"}"; name="${name%"${name##*[![:space:]]}"}"
    flags="${flags:-}"; flags="${flags#"${flags%%[![:space:]]*}"}"; flags="${flags%"${flags##*[![:space:]]}"}"
    [[ -z "$name" || "$name" == \#* ]] && continue
    wanted "$name" || continue
    out="${OUTPUT_DIR}/${name}"
    payload="python studies/rhine2026/run_rhine.py ${COMMON} ${flags} --out ${out} > ${out}.log 2>&1"
    dep=""
    if [[ "$name" == *_base ]]; then
        dep=""
    elif [[ "$flags" == *--cache-isolation* ]]; then
        dep=""
    else
        dep="$BASE_ID"
    fi
    profile="2026"
    if [[ "$flags" =~ --profile[[:space:]]+([^[:space:]]+) ]]; then profile="${BASH_REMATCH[1]}"; fi
    id=$(submit "$name" "$TIME_RUN" "$MEM_RUN" "$CPUS_RUN" "$dep" "$payload")
    [[ "$name" == *_base ]] && BASE_ID="$id"
    echo "  ${name}: job ${id}${dep:+ (afterok:$dep)}" >&2
    post="python studies/rhine2026/analyze_scenario.py ${out} --profile ${profile} --no-links > ${out}/analysis.txt 2>&1; \
python studies/rhine2026/plots/scenario_figures.py --profile ${profile} --run ${out} --out ${out}/figures > ${out}/figures.log 2>&1; \
rm -f ${out}/household_data_by_sector.csv"
    pid=$(submit "post_${name}" "$TIME_POST" "$MEM_POST" 1 "$id" "$post")
    ALL_IDS="${ALL_IDS}${ALL_IDS:+:}${pid}"
    RUN_DIRS="${RUN_DIRS} ${out}"
done < "$JOBS_FILE"

if [[ -n "$ALL_IDS" ]]; then
    cmp="python studies/rhine2026/compare_runs.py ${RUN_DIRS} --weekly DEU --csv ${OUTPUT_DIR}/compare_runs_batch.csv > ${OUTPUT_DIR}/compare_runs_batch.txt 2>&1"
    submit "compare_rhine_batch" "00:30:00" "8G" 1 "$ALL_IDS" "$cmp" >/dev/null
    echo "  compare job queued after all postprocess jobs" >&2
fi
echo "submitted from ${JOBS_FILE}; logs in ${SLURM_LOG_DIR}; outputs in ${OUTPUT_DIR}" >&2
