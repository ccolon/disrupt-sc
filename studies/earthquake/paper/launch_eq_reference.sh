#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — REFERENCE track (part 2 of 2).
#
# One full-export run per seed at the calibrated CENTRAL config (t_final=13), then
# postprocess: per-seed analyze -> average across seeds -> figures + model table.
# Outputs (all from the SEED AVERAGE, never a single seed):
#   figures/fig_distribution.png  temporal/sectoral + canton choropleth
#   figures/fig_uq.png            model MMI-bin DiD vs UQ TWFE
#   models_table.csv              DisruptSC central household loss = mean [p10-p90] over seeds
#
# This is INDEPENDENT of the sensitivity track (launch_eq_sensitivity.sh); the model
# table is computed from these reference seeds only — no sensitivity values.
#
# Usage:  bash studies/earthquake/paper/launch_eq_reference.sh [--dry-run] [--n-seeds 10] [--skip-existing]
#
# --skip-existing: don't re-run any seed whose reference/seed_*/household_data.csv exists;
#   postprocess still runs, refreshing the averaged figures + model table from all seeds.
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="${SCRIPT_DIR}/output/earthquake_paper"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/eq_reference"
# GADM canton polygons (level-2), UQ TWFE coefs, canton->MMI map: committed in the repo.
GADM="${SCRIPT_DIR}/studies/earthquake/additional_data/gadm41_ECU_2.json"
CANTON_MMI="${SCRIPT_DIR}/studies/earthquake/additional_data/canton_mmi_bin.csv"
UQ_TWFE="${SCRIPT_DIR}/studies/earthquake/additional_data/twfe_event_study_coefs.csv"

N_SEEDS=10                          # <<< reference full-export seeds (10-15 plenty; heavy disk)
T_FINAL=13
TIME_REF="02:00:00";  MEM_REF="6G"
# Postprocess cost scales with N_SEEDS (per-seed distribution.py + uq_did.py, the latter
# parses the big firm_data.csv), so size it for a 50-seed batch, not 10.
TIME_POST="04:00:00"; MEM_POST="8G"
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
REF_ROOT="${OUTPUT_DIR}/reference"
FIG_DIR="${OUTPUT_DIR}/figures"
CRIT_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/input_criticality.csv"
SHOCK_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/earthquake_shock_modelready.csv"
DATA_OVERRIDES="--criticality ${CRIT_CSV} --shock ${SHOCK_CSV}"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"

$DRY_RUN || mkdir -p "$REF_ROOT" "$FIG_DIR" "$SLURM_LOG_DIR"

submit() {
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}";
    else eval "$cmd"; fi
}
add_id() { [[ -z "$2" ]] && return; local cur="${!1}"; printf -v "$1" '%s' "${cur}${cur:+:}$2"; }
submit_if_missing() {
    if [[ "$SKIP_EXISTING" == true && -s "$1" ]]; then echo "  skip ${2} (output exists: $1)" >&2; return; fi
    submit "$2" "$3" "$4" "" "$5"
}

# ---- reference full-export runs (one per seed) ----------------------------
REF_IDS=""
for (( s=0; s<N_SEEDS; s++ )); do
  RP="python ${PAPER}/run_reference.py --seed ${s} --t-final ${T_FINAL} --out-root ${REF_ROOT} --cache-isolation ${DATA_OVERRIDES}"
  add_id REF_IDS "$(submit_if_missing "${REF_ROOT}/seed_${s}/household_data.csv" "ref_s${s}" "$TIME_REF" "$MEM_REF" "$RP")"
done

# ---- postprocess: analyze per seed -> AVERAGE across seeds -> figures + model table ----
# The payload must stay ONE flat command with no quotes, parens or $(...): submit() nests it
# inside --wrap="bash -c '...'" and eval's the result, so any such metacharacter is exposed at
# eval time and breaks the submit. All the logic (per-seed loop, guard, plots) therefore lives
# in postprocess_reference.sh, which is also directly re-runnable by hand when a job dies.
PP="bash ${PAPER}/postprocess_reference.sh ${REF_ROOT} ${FIG_DIR} ${OUTPUT_DIR} ${CANTON_MMI} ${GADM} ${UQ_TWFE}"
PID=$(submit "ref_postprocess" "$TIME_POST" "$MEM_POST" "$REF_IDS" "$PP")

echo
echo "Submitted REFERENCE track: ${N_SEEDS} full-export runs + postprocess ${PID}"
echo "  fig_distribution + fig_uq are plotted from ref_avg (the seed AVERAGE), not a single seed."
echo "  outputs: ${FIG_DIR}/fig_distribution.png, ${FIG_DIR}/fig_uq.png, ${OUTPUT_DIR}/models_table.csv"
$SKIP_EXISTING && echo "  --skip-existing ON: only missing seed runs submitted; postprocess always refreshes."
echo "  change the batch size with --n-seeds."
