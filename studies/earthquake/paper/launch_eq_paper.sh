#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — paper campaign (sensitivity + Monte Carlo).
#
# (A) SENSITIVITY + MC sweep: for each (flow_coverage x nb_suppliers x seed) one
#     run_grid job builds once (seed drives supplier selection) and sweeps the
#     runtime params (utilization x reconstruction on/off x public_share x
#     target_time) -> a shard CSV. A combine job merges shards ->
#     sensitivity_summary.csv (mean / p10 / p90 across seeds) and the model table.
# (B) REFERENCE runs (for the distribution + UQ figures): one full-export run per
#     seed at t_final=13; a postprocess job runs the analyzers per seed, averages
#     across seeds, and renders the figures.
#
# Usage:
#     bash studies/earthquake/paper/launch_eq_paper.sh              # submit everything
#     bash studies/earthquake/paper/launch_eq_paper.sh --dry-run
#     bash studies/earthquake/paper/launch_eq_paper.sh --n-seeds 10
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

# ========================= SWEEP DESIGN (edit freely) ======================
N_SEEDS=10                          # <<< number of Monte-Carlo seeds (first batch: 10)
FLOW_COVERAGES=(0.6 0.8 1.0)        # build param -> one build per value
NB_SUPPLIERS=(1 2 4)               # build param -> one build per value
T_FINAL=12                          # sweep horizon (months)
UTILS="0.6,0.8,1.0"
RECON="true,false"                  # reconstruction on/off (does reconstruction matter?)
PUBLIC_SHARES="0.0,0.8"
TARGET_TIMES="365,730"
REF_T_FINAL=13                      # reference-run horizon (covers UQ tau 0-12)

# ------------------------- SLURM resources --------------------------------
TIME_WORKER="06:00:00"; MEM_WORKER="6G"
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
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"

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

# ---- (A) sensitivity + MC workers: one per (flow x nb x seed) -------------
WORKER_IDS=""
for flow in "${FLOW_COVERAGES[@]}"; do
  for nb in "${NB_SUPPLIERS[@]}"; do
    for (( s=0; s<N_SEEDS; s++ )); do
      OUT="${SHARD_DIR}/sens_f${flow}_nb${nb}_s${s}.csv"
      P="python ${PAPER}/run_grid.py --flow-coverage ${flow} --nb-suppliers ${nb} \
         --t-final ${T_FINAL} --seeds ${s} --utils ${UTILS} --recon ${RECON} \
         --public-shares ${PUBLIC_SHARES} --target-times ${TARGET_TIMES} --out ${OUT}"
      WID=$(submit "sens_f${flow}_nb${nb}_s${s}" "$TIME_WORKER" "$MEM_WORKER" "" "$P")
      WORKER_IDS="${WORKER_IDS}${WORKER_IDS:+:}${WID}"
    done
  done
done
n_workers=$(( ${#FLOW_COVERAGES[@]} * ${#NB_SUPPLIERS[@]} * N_SEEDS ))

# ---- (A) combine shards -> summary + model table -------------------------
CP="python ${PAPER}/combine.py --in ${SHARD_DIR} --out ${OUTPUT_DIR}/sensitivity_summary.csv && \
    python ${PAPER}/plot/plot_sensitivity.py ${SHARD_DIR}/../sensitivity_summary.csv --fig ${FIG_DIR}/fig_sensitivity.png \
      2>/dev/null || python ${PAPER}/plot/plot_sensitivity.py ${OUTPUT_DIR}/sensitivity_summary.csv --fig ${FIG_DIR}/fig_sensitivity.png; \
    python ${PAPER}/plot/plot_model_table.py --summary ${OUTPUT_DIR}/sensitivity_summary.csv \
      --out ${OUTPUT_DIR}/models_table.csv --central utilization_rate=0.8 reconstruction_market=True reconstruction_public_share=0.8"
CID=$(submit "sens_combine" "$TIME_POST" "$MEM_POST" "$WORKER_IDS" "$CP")

# ---- (B) reference runs: one full-export run per seed ---------------------
REF_IDS=""
for (( s=0; s<N_SEEDS; s++ )); do
  RP="python ${PAPER}/run_reference.py --seed ${s} --t-final ${REF_T_FINAL} \
      --out-root ${REF_ROOT} --cache-isolation"
  RID=$(submit "ref_s${s}" "$TIME_REF" "$MEM_REF" "" "$RP")
  REF_IDS="${REF_IDS}${REF_IDS:+:}${RID}"
done

# ---- (B) postprocess: analyze each seed, average, plot --------------------
PP="for d in ${REF_ROOT}/seed_*; do \
      python ${PAPER}/analyze/distribution.py \$d --out-dir \$d; \
      python ${PAPER}/analyze/uq_did.py \$d --canton-mmi ${CANTON_MMI} --out-dir \$d; \
    done; \
    python ${PAPER}/average_runs.py --glob '${REF_ROOT}/seed_*' --out-dir ${FIG_DIR}/ref_avg; \
    python ${PAPER}/plot/plot_distribution.py ${FIG_DIR}/ref_avg --gadm ${GADM} --fig ${FIG_DIR}/fig_distribution.png; \
    python ${PAPER}/plot/plot_uq.py ${FIG_DIR}/ref_avg/uq_eventstudy.csv --uq ${UQ_TWFE} --fig ${FIG_DIR}/fig_uq.png; \
    python ${PAPER}/analyze/aggregate_gdp.py ${REF_ROOT}/seed_0 --out ${OUTPUT_DIR}/aggregate_seed0.csv"
PID=$(submit "ref_postprocess" "$TIME_POST" "$MEM_POST" "$REF_IDS" "$PP")

echo
echo "Submitted paper campaign:"
echo "  (A) ${n_workers} sensitivity workers (${#FLOW_COVERAGES[@]} flow x ${#NB_SUPPLIERS[@]} nb x ${N_SEEDS} seeds) + combine ${CID}"
echo "  (B) ${N_SEEDS} reference runs + postprocess ${PID}"
echo "  outputs: ${OUTPUT_DIR}  (summary, models_table, figures/)"
echo "  edit N_SEEDS at the top of this script to change the batch size."
