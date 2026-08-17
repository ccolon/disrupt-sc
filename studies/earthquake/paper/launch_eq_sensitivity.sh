#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — SENSITIVITY track (part 1 of 2).
#
# OAT (one-at-a-time) sensitivity x Monte-Carlo seeds. Per seed: one baseline build
# runs the runtime variations (utilization / reconstruction on-off / public_share /
# target_time / lag / criticality); separate builds cover the flow_coverage and
# nb_suppliers variations. A combine job -> sensitivity_summary.csv + sensitivity_all.csv
# + fig_sensitivity.png.
#
# This is INDEPENDENT of the reference track (launch_eq_reference.sh) — no distribution/
# UQ figures, no models_table here.
#
# Usage:  bash studies/earthquake/paper/launch_eq_sensitivity.sh [--dry-run] [--n-seeds 50] [--skip-existing]
#
# --skip-existing: don't re-run any worker whose shard (sensitivity_shards/oat_*.csv)
#   already exists; combine still runs, refreshing the summary/figure from all shards.
#   To refresh one axis, delete its shards and re-run with the flag, e.g.:
#     rm ${OUTPUT_DIR}/sensitivity_shards/oat_base_s*.csv && bash ... --skip-existing
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="${SCRIPT_DIR}/output/earthquake_paper"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/eq_sensitivity"

# ========================= SWEEP DESIGN ====================================
N_SEEDS=10                          # <<< Monte-Carlo seeds
T_FINAL=13                          # horizon (months); 13 covers UQ tau 0-12

# baseline (central) config + per-parameter levels swept around it (OAT)
FLOW_BASE=0.8;   FLOW_LEVELS=(0.6 0.7 0.8 0.9 1.0)
# nb_suppliers is the DOMINANT lever and its whole effect is a cliff between 1 and 2, so the
# 1-2 range is resolved with the stochastic 1-or-2 mix (fractional values), plus 3/6 above.
NB_BASE=2;       NB_LEVELS=(1 1.25 1.5 1.75 2 3 6)
UTIL_BASE=0.8;   UTILS="0.6,0.8,1.0"
RECON_BASE=true; RECON="true,false"
PUBLIC_BASE=0.8; PUBLIC_SHARES="0.0,0.5,0.8,1.0"   # reconstruction funded externally (aid) share
TARGET_BASE=730; TARGET_TIMES="365,730"
LAG_BASE=60;     RECON_LAGS="30,60,90"
CRIT_BASE=0.02;  CRIT_THRESHOLDS="0.0,0.01,0.02,0.05"   # 0.01 = the "too-low" (non-saturating) point

# ------------------------- SLURM resources --------------------------------
# The oat_base job runs every runtime config in one build (~60 after the mechanism/severity
# axes were added, up from ~34), so it needs more headroom than the build-variation jobs.
TIME_WORKER="10:00:00"; MEM_WORKER="6G"
TIME_POST="00:30:00";   MEM_POST="4G"
# ===========================================================================

DRY_RUN=false
SKIP_EXISTING=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)       DRY_RUN=true; shift ;;
        --skip-existing) SKIP_EXISTING=true; shift ;;
        --n-seeds)       N_SEEDS=$2; shift 2 ;;
        *) shift ;;
    esac
done

PAPER="${SCRIPT_DIR}/studies/earthquake/paper"
SHARD_DIR="${OUTPUT_DIR}/sensitivity_shards"
FIG_DIR="${OUTPUT_DIR}/figures"
SUMMARY="${OUTPUT_DIR}/sensitivity_summary.csv"
CRIT_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/input_criticality.csv"
SHOCK_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/earthquake_shock_modelready.csv"
CANTON_MMI="${SCRIPT_DIR}/studies/earthquake/additional_data/canton_mmi_bin.csv"
# --canton-mmi makes every config also report the MMI>7 vs control DiD (the UQ validation
# target), so the sweep doubles as a calibration search, not just a robustness check.
DATA_OVERRIDES="--criticality ${CRIT_CSV} --shock ${SHOCK_CSV} --canton-mmi ${CANTON_MMI}"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"
BASE_RT="--util-base ${UTIL_BASE} --recon-base ${RECON_BASE} --public-base ${PUBLIC_BASE} --target-base ${TARGET_BASE} --lag-base ${LAG_BASE} --crit-base ${CRIT_BASE}"

$DRY_RUN || mkdir -p "$SHARD_DIR" "$FIG_DIR" "$SLURM_LOG_DIR"

submit() {  # echoes the job id (or a fake one under --dry-run); deps are ':'-joined
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}";
    else eval "$cmd"; fi
}
add_id() {  # append a (possibly empty) job id to a ':'-joined list variable, safely
    [[ -z "$2" ]] && return
    local cur="${!1}"; printf -v "$1" '%s' "${cur}${cur:+:}$2"
}
submit_if_missing() {  # $1=output_path $2=job $3=time $4=mem $5=payload ; skip if --skip-existing and output exists
    if [[ "$SKIP_EXISTING" == true && -s "$1" ]]; then echo "  skip ${2} (output exists: $1)" >&2; return; fi
    submit "$2" "$3" "$4" "" "$5"
}

# ---- OAT + MC workers -----------------------------------------------------
WORKER_IDS=""
for (( s=0; s<N_SEEDS; s++ )); do
  # baseline build -> runtime OAT (util / recon / public / target / lag / crit from baseline)
  P="python ${PAPER}/run_grid.py --oat --flow-coverage ${FLOW_BASE} --nb-suppliers ${NB_BASE} \
     --t-final ${T_FINAL} --seeds ${s} --utils ${UTILS} --recon ${RECON} \
     --public-shares ${PUBLIC_SHARES} --target-times ${TARGET_TIMES} --recon-lags ${RECON_LAGS} \
     --crit-thresholds ${CRIT_THRESHOLDS} ${BASE_RT} ${DATA_OVERRIDES} --out ${SHARD_DIR}/oat_base_s${s}.csv"
  add_id WORKER_IDS "$(submit_if_missing "${SHARD_DIR}/oat_base_s${s}.csv" "oat_base_s${s}" "$TIME_WORKER" "$MEM_WORKER" "$P")"
  for flow in "${FLOW_LEVELS[@]}"; do
    [[ "$flow" == "$FLOW_BASE" ]] && continue
    P="python ${PAPER}/run_grid.py --oat-tag flow_coverage --flow-coverage ${flow} --nb-suppliers ${NB_BASE} \
       --t-final ${T_FINAL} --seeds ${s} --utils ${UTIL_BASE} --recon ${RECON_BASE} \
       --public-shares ${PUBLIC_BASE} --target-times ${TARGET_BASE} --recon-lags ${LAG_BASE} \
       ${BASE_RT} ${DATA_OVERRIDES} --out ${SHARD_DIR}/oat_flow${flow}_s${s}.csv"
    add_id WORKER_IDS "$(submit_if_missing "${SHARD_DIR}/oat_flow${flow}_s${s}.csv" "oat_flow${flow}_s${s}" "$TIME_WORKER" "$MEM_WORKER" "$P")"
  done
  for nb in "${NB_LEVELS[@]}"; do
    [[ "$nb" == "$NB_BASE" ]] && continue
    P="python ${PAPER}/run_grid.py --oat-tag nb_suppliers_per_input --flow-coverage ${FLOW_BASE} --nb-suppliers ${nb} \
       --t-final ${T_FINAL} --seeds ${s} --utils ${UTIL_BASE} --recon ${RECON_BASE} \
       --public-shares ${PUBLIC_BASE} --target-times ${TARGET_BASE} --recon-lags ${LAG_BASE} \
       ${BASE_RT} ${DATA_OVERRIDES} --out ${SHARD_DIR}/oat_nb${nb}_s${s}.csv"
    add_id WORKER_IDS "$(submit_if_missing "${SHARD_DIR}/oat_nb${nb}_s${s}.csv" "oat_nb${nb}_s${s}" "$TIME_WORKER" "$MEM_WORKER" "$P")"
  done
done

# ---- combine -> summary + raw concat + sensitivity figure -----------------
CP="python ${PAPER}/combine.py --in ${SHARD_DIR} --out ${SUMMARY} --raw-out ${OUTPUT_DIR}/sensitivity_all.csv && \
    python ${PAPER}/plot/plot_sensitivity.py ${OUTPUT_DIR}/sensitivity_all.csv --fig ${FIG_DIR}/fig_sensitivity.png"
CID=$(submit "sens_combine" "$TIME_POST" "$MEM_POST" "$WORKER_IDS" "$CP")

n_workers=$(( N_SEEDS * (1 + (${#FLOW_LEVELS[@]}-1) + (${#NB_LEVELS[@]}-1)) ))
echo
echo "Submitted SENSITIVITY track: ${n_workers} sweep jobs (${N_SEEDS} seeds) + combine ${CID}"
echo "  outputs: ${SUMMARY}, ${OUTPUT_DIR}/sensitivity_all.csv, ${FIG_DIR}/fig_sensitivity.png"
$SKIP_EXISTING && echo "  --skip-existing ON: only missing shards submitted; combine always refreshes."
echo "  change the batch size with --n-seeds."
