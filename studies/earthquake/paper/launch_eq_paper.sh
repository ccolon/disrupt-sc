#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — paper campaign (OAT sensitivity + Monte Carlo).
#
# Strategy = ONE-AT-A-TIME (OAT): vary each parameter across its levels holding the
# others at baseline, x N_SEEDS Monte-Carlo seeds. ~12 configs x N_SEEDS runs (vs a
# full factorial's ~350 x N_SEEDS). Each parameter's sensitivity panel is then a
# clean line from baseline with a pure cross-seed (MC) band.
#
#   (A) OAT + MC: per seed, one baseline build (flow_base x nb_base) runs the runtime
#       variations (utilization / reconstruction on-off / public_share / target_time /
#       lag); separate builds cover the flow_coverage and nb_suppliers variations. A
#       combine job -> sensitivity_summary.csv (mean/p10/p90 across seeds) + model table.
#   (B) REFERENCE: one full-export run per seed at t_final=13; postprocess analyzes each
#       seed, averages across seeds, and renders the distribution + UQ figures.
#
# Usage:  bash studies/earthquake/paper/launch_eq_paper.sh [--dry-run] [--n-seeds 10]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="${SCRIPT_DIR}/output/earthquake_paper"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/eq_paper"
GADM="/projects/disruptsc/WorldBank/Ecuador/Admin/gadm41_ECU_1.json"
CANTON_MMI="${SCRIPT_DIR}/studies/earthquake/_shock/canton_mmi_bin.csv"
UQ_TWFE="/projects/disruptsc/WorldBank/Ecuador/Johannes/twfe_event_study_coefs.csv"

# ========================= SWEEP DESIGN ====================================
N_SEEDS=10                          # <<< Monte-Carlo seeds (first batch: 10)
T_FINAL=13                          # horizon (months); 13 covers UQ tau 0-12

# baseline (central) config + per-parameter levels swept around it (OAT)
FLOW_BASE=0.8;   FLOW_LEVELS=(0.6 0.8 1.0)
NB_BASE=2;       NB_LEVELS=(1 2 4)
UTIL_BASE=0.8;   UTILS="0.6,0.8,1.0"
RECON_BASE=true; RECON="true,false"
PUBLIC_BASE=0.8; PUBLIC_SHARES="0.0,0.8"
TARGET_BASE=730; TARGET_TIMES="365,730"
LAG_BASE=60;     RECON_LAGS="30,60,90"

# ------------------------- SLURM resources --------------------------------
TIME_WORKER="04:00:00"; MEM_WORKER="6G"
TIME_REF="02:00:00";    MEM_REF="6G"
TIME_POST="00:30:00";   MEM_POST="4G"
# ===========================================================================

DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)  DRY_RUN=true; shift ;;
        --n-seeds)  N_SEEDS=$2; shift 2 ;;
        *) shift ;;
    esac
done

PAPER="${SCRIPT_DIR}/studies/earthquake/paper"
SHARD_DIR="${OUTPUT_DIR}/sensitivity_shards"
REF_ROOT="${OUTPUT_DIR}/reference"
FIG_DIR="${OUTPUT_DIR}/figures"
SUMMARY="${OUTPUT_DIR}/sensitivity_summary.csv"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"
BASE_RT="--util-base ${UTIL_BASE} --recon-base ${RECON_BASE} --public-base ${PUBLIC_BASE} --target-base ${TARGET_BASE} --lag-base ${LAG_BASE}"

$DRY_RUN || mkdir -p "$SHARD_DIR" "$REF_ROOT" "$FIG_DIR" "$SLURM_LOG_DIR"

submit() {  # echoes the job id (or a fake one under --dry-run); deps are ':'-joined
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}";
    else eval "$cmd"; fi
}

# ---- (A) OAT + MC workers -------------------------------------------------
WORKER_IDS=""
for (( s=0; s<N_SEEDS; s++ )); do
  # baseline build -> runtime OAT (util / recon / public / target / lag from baseline)
  P="python ${PAPER}/run_grid.py --oat --flow-coverage ${FLOW_BASE} --nb-suppliers ${NB_BASE} \
     --t-final ${T_FINAL} --seeds ${s} --utils ${UTILS} --recon ${RECON} \
     --public-shares ${PUBLIC_SHARES} --target-times ${TARGET_TIMES} --recon-lags ${RECON_LAGS} \
     ${BASE_RT} --out ${SHARD_DIR}/oat_base_s${s}.csv"
  WID=$(submit "oat_base_s${s}" "$TIME_WORKER" "$MEM_WORKER" "" "$P")
  WORKER_IDS="${WORKER_IDS}${WORKER_IDS:+:}${WID}"
  # flow_coverage variations (build param) -> baseline runtime, tagged flow_coverage
  for flow in "${FLOW_LEVELS[@]}"; do
    [[ "$flow" == "$FLOW_BASE" ]] && continue
    P="python ${PAPER}/run_grid.py --oat-tag flow_coverage --flow-coverage ${flow} --nb-suppliers ${NB_BASE} \
       --t-final ${T_FINAL} --seeds ${s} --utils ${UTIL_BASE} --recon ${RECON_BASE} \
       --public-shares ${PUBLIC_BASE} --target-times ${TARGET_BASE} --recon-lags ${LAG_BASE} \
       ${BASE_RT} --out ${SHARD_DIR}/oat_flow${flow}_s${s}.csv"
    WID=$(submit "oat_flow${flow}_s${s}" "$TIME_WORKER" "$MEM_WORKER" "" "$P")
    WORKER_IDS="${WORKER_IDS}:${WID}"
  done
  # nb_suppliers variations
  for nb in "${NB_LEVELS[@]}"; do
    [[ "$nb" == "$NB_BASE" ]] && continue
    P="python ${PAPER}/run_grid.py --oat-tag nb_suppliers_per_input --flow-coverage ${FLOW_BASE} --nb-suppliers ${nb} \
       --t-final ${T_FINAL} --seeds ${s} --utils ${UTIL_BASE} --recon ${RECON_BASE} \
       --public-shares ${PUBLIC_BASE} --target-times ${TARGET_BASE} --recon-lags ${LAG_BASE} \
       ${BASE_RT} --out ${SHARD_DIR}/oat_nb${nb}_s${s}.csv"
    WID=$(submit "oat_nb${nb}_s${s}" "$TIME_WORKER" "$MEM_WORKER" "" "$P")
    WORKER_IDS="${WORKER_IDS}:${WID}"
  done
done

# ---- (A) combine -> summary + sensitivity figure + model table ------------
CENTRAL="flow_coverage=${FLOW_BASE} nb_suppliers_per_input=${NB_BASE} utilization_rate=${UTIL_BASE} \
reconstruction_market=True reconstruction_public_share=${PUBLIC_BASE} \
reconstruction_target_time=${TARGET_BASE} reconstruction_lag=${LAG_BASE}"
CP="python ${PAPER}/combine.py --in ${SHARD_DIR} --out ${SUMMARY} && \
    cat ${SHARD_DIR}/*.csv > ${OUTPUT_DIR}/sensitivity_all.csv 2>/dev/null; \
    python ${PAPER}/plot/plot_sensitivity.py ${SHARD_DIR}/oat_base_s0.csv --fig ${FIG_DIR}/fig_sensitivity.png || true; \
    python ${PAPER}/plot/plot_model_table.py --summary ${SUMMARY} --out ${OUTPUT_DIR}/models_table.csv --central ${CENTRAL}"
CID=$(submit "sens_combine" "$TIME_POST" "$MEM_POST" "$WORKER_IDS" "$CP")

# ---- (B) reference runs + postprocess (analyze -> average -> plot) ---------
REF_IDS=""
for (( s=0; s<N_SEEDS; s++ )); do
  RP="python ${PAPER}/run_reference.py --seed ${s} --t-final ${T_FINAL} --out-root ${REF_ROOT} --cache-isolation"
  RID=$(submit "ref_s${s}" "$TIME_REF" "$MEM_REF" "" "$RP")
  REF_IDS="${REF_IDS}${REF_IDS:+:}${RID}"
done
PP="for d in ${REF_ROOT}/seed_*; do \
      python ${PAPER}/analyze/distribution.py \$d --out-dir \$d; \
      python ${PAPER}/analyze/uq_did.py \$d --canton-mmi ${CANTON_MMI} --out-dir \$d; \
    done; \
    python ${PAPER}/average_runs.py --glob '${REF_ROOT}/seed_*' --out-dir ${FIG_DIR}/ref_avg; \
    python ${PAPER}/plot/plot_distribution.py ${FIG_DIR}/ref_avg --gadm ${GADM} --fig ${FIG_DIR}/fig_distribution.png; \
    python ${PAPER}/plot/plot_uq.py ${FIG_DIR}/ref_avg/uq_eventstudy.csv --uq ${UQ_TWFE} --fig ${FIG_DIR}/fig_uq.png"
PID=$(submit "ref_postprocess" "$TIME_POST" "$MEM_POST" "$REF_IDS" "$PP")

n_workers=$(( N_SEEDS * (1 + (${#FLOW_LEVELS[@]}-1) + (${#NB_LEVELS[@]}-1)) ))
echo
echo "Submitted paper campaign (OAT sensitivity + MC):"
echo "  (A) ${n_workers} sweep jobs (${N_SEEDS} seeds x [1 baseline + flow/nb variations]) + combine ${CID}"
echo "  (B) ${N_SEEDS} reference runs + postprocess ${PID}"
echo "  baseline: flow=${FLOW_BASE} nb=${NB_BASE} util=${UTIL_BASE} recon=${RECON_BASE} public=${PUBLIC_BASE} target=${TARGET_BASE} lag=${LAG_BASE}"
echo "  outputs: ${OUTPUT_DIR}  (sensitivity_summary, models_table, figures/)"
echo "  change the batch size by editing N_SEEDS at the top."
