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
#       3 lag13 12 --t-final 116          (run name lag13_d12_s3_t116)
#       3 lag13 12 --inventory-scale 2 --t-final 116   (run name lag13_d12_s3_inv2_t116)
# A line whose options change the BUILD (flow_coverage, nb_suppliers_per_input, use_route_cache, logistics
# costs, capacities, ...) must name its own --cache-dir: the launcher submits one setup job per distinct
# (seed, cache dir), with that pair's first line's options, and every run of the pair waits for it (afterok),
# so that two jobs never build the same cache at once. Runtime switches (restoration time, inventories,
# behavioural options, disruptions) reuse the seed's cache.
#
# Runs write on the node's local disk (TMPDIR) and are copied to OUTPUT_DIR/<batch>/<run name> when they end
# (the Rhine lesson of 1 Nov 2026: writes to the project volume failed mid-run with exit status 120).
# The copy is tried 20 times, 90 s apart. If every attempt fails, the job ends with status 75 (or the run's own
# status if the run failed), prints a message to its log and leaves an empty COPY_FAILED file in the run folder when
# it can: a copy cut short by a full volume (KI-56, 8 Nov 2026) otherwise ended COMPLETED with empty or partial files.
# Check: bash studies/cambodia/cluster/check_launcher_copy.sh (bash only, no sbatch, no model).
#
# Usage: bash studies/cambodia/cluster/launch_cambodia.sh --jobs FILE --batch NAME [--dry-run]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
# The paper's own checkout (a git worktree of the cluster repo at the paper's commit), not the shared
# /projects/disruptsc/disrupt-sc that other studies' jobs run from: moving that one would change their code.
SCRIPT_DIR="${CAMBODIA_CODE_DIR:-/projects/disruptsc/disrupt-sc-cambodia}"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="/projects/disruptsc/runs/cambodia"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/cambodia"
# Cluster pilot (6 Nov 2026): ~50 s to load, 22-23 s a day undisturbed, 28-31 s a flooded day (~75 min a 180-day
# run). Memory: before the KI-54 fix a run grew 40-60 MB a simulated day (~11-16 GB at day 180; the first pilot
# submission was cancelled); with it ~10 MB a day, ~4.3 GB at day 180 (30-day local run, 2.89 GB peak). 6 GB = that
# + ~40 %; the cluster is memory-bound. Check the resubmitted pilot's MaxRSS (sacct) before the grid.
TIME_RUN="08:00:00"; MEM_RUN="6G"
TIME_SETUP="01:00:00"; MEM_SETUP="8G"
# Either partition, whichever starts the job first (6 Nov 2026, the user's choice): generic_plus = the generic
# nodes + compute9, same limits, open to all groups.
PARTITION="${CAMBODIA_PARTITION:-generic,generic_plus}"
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
# The compute nodes have no git (6 Nov 2026): the checkout's state is taken here, at submit time, passed to every
# job (run_cambodia.py records it in study_run.json) and written to the batch folder. The checkout must not move
# until the batch has run - jobs read the code when they start, not when they are submitted.
GIT_SHA=$(git -C "${SCRIPT_DIR}" rev-parse HEAD 2>/dev/null || echo unknown)
GIT_DIRTY=$(git -C "${SCRIPT_DIR}" status --porcelain --untracked-files=no -- src studies/cambodia 2>/dev/null | wc -l)
[[ "$GIT_DIRTY" == "0" ]] || echo "WARNING: ${SCRIPT_DIR} has ${GIT_DIRTY} modified tracked file(s) in src/ or studies/cambodia/" >&2
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0 && export PYTHONIOENCODING=utf-8 && export CAMBODIA_GIT_SHA=${GIT_SHA} && export CAMBODIA_GIT_DIRTY=${GIT_DIRTY} && cd ${SCRIPT_DIR}"
RUNNER="python studies/cambodia/run_cambodia.py"
DEST="${OUTPUT_DIR}/${BATCH}"
if ! $DRY_RUN; then
    mkdir -p "$DEST" "$SLURM_LOG_DIR"
    {
        echo "# batch ${BATCH}, submitted $(date -u +%FT%TZ) by launch_cambodia.sh"
        echo "code_worktree: ${SCRIPT_DIR}"
        echo "code_sha: ${GIT_SHA}"
        echo "code_modified_tracked_files: ${GIT_DIRTY}"
        echo "data_path: ${DATA_PATH} (repo HEAD $(git -C "${DATA_PATH}" rev-parse HEAD 2>/dev/null))"
        (cd "${DATA_PATH}" && sha256sum Cambodia/Transport/transport.gpkg Cambodia/Transport/multimodal.gpkg \
            Cambodia/Transport/flood_v3_edges.csv Cambodia/Economic/mrio.csv Cambodia/Spatial/firms.geojson \
            Cambodia/Spatial/households.geojson 2>&1)
        echo "job_list: ${JOBS_FILE}"
    } > "${DEST}/CODE_VERSION.txt"
    cp "$JOBS_FILE" "$DEST/"
fi

submit() {   # name time mem dependency payload -> job id
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}"; return; fi
    sbatch --parsable --partition="${PARTITION}" --nodes=1 --ntasks=1 --cpus-per-task=1 --time="${timelimit}" --mem="${mem}" ${depflag} \
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
    tag=$(sed -e 's/--cache-dir[ =][^ ]*//' -e 's/--t-final[ =]\([0-9]*\)/t\1/' -e 's/--set //g' \
        -e 's/--inventory-scale[ =]\([0-9.]*\)/inv\1/' \
        -e 's/[^A-Za-z0-9.=_-]\+/_/g' -e 's/^_//;s/_$//' <<< "$opts")
    name="${scenario}_d${duration}_s${seed}${tag:+_${tag}}"
    payload="out=\${TMPDIR:-/tmp}/${name} && mkdir -p \$out && ${RUNNER} --seed ${seed} --scenario ${scenario} --duration ${duration} --cache-dir ${cache} ${opts} --out \$out; rc=\$?; copied=0; for i in \$(seq 20); do if cp -r \$out ${DEST}/; then copied=1; break; fi; sleep 90; done; if [ \$copied = 0 ]; then echo \"copy of ${name} to ${DEST} failed 20 times (KI-56)\" >&2; touch ${DEST}/${name}/COPY_FAILED 2>/dev/null; [ \$rc = 0 ] && rc=75; fi; exit \$rc"
    submit "cam_${name}" "$TIME_RUN" "$MEM_RUN" "${SETUP_ID[$key]}" "$payload" > /dev/null
    n=$((n + 1))
done < "$JOBS_FILE"
echo "${n} runs submitted for batch ${BATCH} (${#SETUP_ID[@]} setup jobs); outputs in ${DEST}"
