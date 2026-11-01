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
# Usage:  bash studies/rhine2026/cluster/launch_rhine_batch.sh [--dry-run] [--jobs FILE] [--only NAME,NAME] [--independent]
#
# --independent (16 Sep 2026): submit every run at once, no afterok chain on the base. Use it when the
# shared caches are known valid (a run-time or config change that the fingerprints ignore: switching
# costs, inventory targets, disruptions); a job list without a *_base line behaves the same way.
#
# Before the first batch on a new cluster: sync_to_cluster.sh (EU data + caches), git pull to the commit
# named in the jobs file, and check that config/user_defined_EU.yaml resolves its data through
# DISRUPT_SC_DATA_PATH (the EU config uses "repo:" paths and the scope data folder, no absolute paths).
#
# Run log on the node's local disk (1 Nov 2026): the run's stdout and stderr go to /tmp/rhine2026_<name>.log on the
# compute node, a background loop copies that file to <out>.log on the project volume every three minutes, and the
# job copies it once more at the end (five attempts a minute apart) before returning the run's exit status. Reason:
# eleven runs died on two nights (30 Oct 03:09, 31 Oct 22:02-22:07, on four nodes within five minutes) with Python's
# exit status 120 and no traceback: a write to the project volume failed (120 is the status when the final flush of
# stdout fails), the traceback itself was lost on the same file, and other users' jobs on other volumes were not
# touched. A log held open on the project volume for three hours is the one file descriptor the run cannot do
# without; on the local disk it survives a volume hiccup, the copy recovers once the volume is back, and a
# traceback, if the run dies anyway, is preserved. The data export at the end still writes to the project volume.
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/rhine2026"
TIME_RUN="16:00:00";  MEM_RUN="20G";  CPUS_RUN=2      # up to 43 weekly steps at ~10 min (+ build), ~13 GB RAM on the laptop
TIME_POST="02:00:00"; MEM_POST="12G"
# ===========================================================================

COMMON="--profile 2026 --no-open --seed 42 --recovery-weeks 12 --light-export"
JOBS_FILE="${SCRIPT_DIR}/studies/rhine2026/cluster/jobs_20260913.txt"
DRY_RUN=false
ONLY=""
INDEPENDENT=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)     DRY_RUN=true; shift ;;
        --jobs)        JOBS_FILE=$2; shift 2 ;;
        --only)        ONLY=$2; shift 2 ;;
        --independent) INDEPENDENT=true; shift ;;
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
    # --full-export (21 Sep 2026) is a marker for this launcher, not a run_rhine.py flag: --light-export is a store_true
    # switch that a later flag cannot unset, so the marker drops it from the common flags for this job and adds the
    # link-level extraction to the postprocess (Kaub link list checked against the laptop build, then
    # validation_outputs.py). The builder writes into the run folder: writing the tracked list in additional_data
    # would dirty the checkout and block the next git pull.
    # CONSTRAINT: build_kaub_links.py --expect compares with the counts of the EU seed-42 draw (5,746 links). Use
    # --full-export for seed-42 EU runs only; for another seed or scope the extraction would refuse to run (loudly:
    # see kaub_links_check.txt) until --expect is dropped or given that draw's counts. A refusal on a seed-42 run
    # means the cluster's route table differs from the laptop's: a finding about the builds, not a launcher fault.
    # Quoting of the wrapped command is exercised by cluster/check_launcher_quoting.sh (bash only, no sbatch).
    common="$COMMON"; full=false
    if [[ "$flags" == *--full-export* ]]; then full=true; flags="${flags//--full-export/}"; common="${COMMON//--light-export/}"; fi
    # 1 Nov 2026: the log is written on the node's local disk and copied to the project volume (see the header);
    # no shell variable may appear in the payload (eval in submit() would expand it at submission time).
    local_log="/tmp/rhine2026_${name}.log"
    copy_log="for i in 1 2 3 4 5; do cp -f ${local_log} ${out}.log 2>/dev/null && break; sleep 60; done"
    payload="( while sleep 180; do cp -f ${local_log} ${out}.log 2>/dev/null; done ) & if python studies/rhine2026/run_rhine.py ${common} ${flags} --out ${out} > ${local_log} 2>&1; then ${copy_log}; true; else ${copy_log}; false; fi"
    dep=""
    if $INDEPENDENT; then
        dep=""
    elif [[ "$name" == *_base ]]; then
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
    if $full; then
        post="${post}; python studies/rhine2026/build_kaub_links.py --definition any --expect --out ${out}/kaub_links_check.csv > ${out}/kaub_links_check.txt 2>&1 && python studies/rhine2026/validation_outputs.py ${out} --flags ${out}/kaub_links_check.csv --out ${out}/validation_outputs.csv > ${out}/validation_outputs.txt 2>&1; python studies/rhine2026/extract_link_flows.py ${out} > ${out}/extract_link_flows.txt 2>&1"
    fi
    pid=$(submit "post_${name}" "$TIME_POST" "$MEM_POST" 1 "$id" "$post")
    ALL_IDS="${ALL_IDS}${ALL_IDS:+:}${pid}"
    RUN_DIRS="${RUN_DIRS} ${out}"
done < "$JOBS_FILE"

if [[ -n "$ALL_IDS" ]]; then
    # 30 Sep 2026: the table carries the name of the job list, so that two lists launched the same day do not
    # overwrite each other's comparison
    tag=$(basename "$JOBS_FILE" .txt)
    cmp="python studies/rhine2026/compare_runs.py ${RUN_DIRS} --weekly DEU --csv ${OUTPUT_DIR}/compare_runs_batch_${tag}.csv > ${OUTPUT_DIR}/compare_runs_batch_${tag}.txt 2>&1"
    submit "compare_rhine_batch" "00:30:00" "8G" 1 "$ALL_IDS" "$cmp" >/dev/null
    echo "  compare job queued after all postprocess jobs" >&2
fi
echo "submitted from ${JOBS_FILE}; logs in ${SLURM_LOG_DIR}; outputs in ${OUTPUT_DIR}" >&2
