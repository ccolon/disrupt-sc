#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — flow_coverage SATURATION sweep.
#
# Purpose: show that under the gated IHS-criticality production function, household
# loss is (nearly) invariant to flow_coverage — i.e. flow_coverage behaves as a pure
# SPEED cutoff, not a cascade-intensity knob. We sweep two materiality floors that
# gate the criticality matrix against three flow_coverage levels, x N_SEEDS.
#
#   grid = critical_input_threshold {0.01, 0.02}  x  flow_coverage {0.6, 0.8, 1.0}  x  N_SEEDS
#   flow_coverage changes the BUILD, so each (flow, seed) is its own job; the two
#   criticality floors are runtime variations WITHIN each build (OAT: base 0.02 + 0.01).
#   -> combine.py aggregates across seeds; plot_saturation.py draws loss-vs-flow_coverage,
#      one line per floor (flat line = saturated).
#
# The criticality matrix (studies/earthquake/additional_data/input_criticality.csv) is committed
# in the repo and passed explicitly with --criticality, so this needs no data-repo or
# config changes on the cluster.
#
# Usage:  bash studies/earthquake/paper/launch_saturation_sweep.sh [--dry-run] [--n-seeds 5]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="${SCRIPT_DIR}/output/earthquake_saturation"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/eq_saturation"

# ========================= SWEEP DESIGN ====================================
N_SEEDS=5                            # <<< Monte-Carlo seeds
T_FINAL=13                           # horizon (months)
NB=2                                 # nb_suppliers_per_input (baseline)
FLOW_LEVELS=(0.6 0.8 1.0)            # flow_coverage (BUILD param) — the x-axis
CRIT_BASE=0.02                       # OAT baseline floor
CRIT_FLOORS="0.01,0.02"              # materiality floors swept within each build
# other params fixed at the paper baseline
UTIL_BASE=0.8; RECON_BASE=true; PUBLIC_BASE=0.8; TARGET_BASE=730; LAG_BASE=60

# ------------------------- SLURM resources --------------------------------
TIME_WORKER="04:00:00"; MEM_WORKER="6G"
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
CRIT_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/input_criticality.csv"
SHOCK_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/earthquake_shock_modelready.csv"
SHARD_DIR="${OUTPUT_DIR}/shards"
FIG="${OUTPUT_DIR}/fig_saturation.png"
SUMMARY="${OUTPUT_DIR}/saturation_summary.csv"
RAW="${OUTPUT_DIR}/saturation_all.csv"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"

for f in "$CRIT_CSV" "$SHOCK_CSV"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: required data file not found at ${f}" >&2
    echo "  (both live in studies/earthquake/additional_data/ and are committed in the repo)" >&2
    exit 1
  fi
done
$DRY_RUN || mkdir -p "$SHARD_DIR" "$SLURM_LOG_DIR"

submit() {  # echoes the job id (or a fake one under --dry-run); deps are ':'-joined
    local job=$1 timelimit=$2 mem=$3 dep=$4 payload=$5
    local depflag=""; [[ -n "$dep" ]] && depflag="--dependency=afterok:${dep}"
    local cmd="sbatch --parsable --nodes=1 --ntasks=1 --time=${timelimit} --mem=${mem} ${depflag} \
        --job-name=${job} --output=${SLURM_LOG_DIR}/${job}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    if $DRY_RUN; then echo "DRYRUN[$job]${dep:+ (afterok:$dep)}: ${payload}" >&2; echo "000${RANDOM}";
    else eval "$cmd"; fi
}

# ---- (A) one job per (flow_coverage, seed); each sweeps the two criticality floors ----
WORKER_IDS=""
for flow in "${FLOW_LEVELS[@]}"; do
  for (( s=0; s<N_SEEDS; s++ )); do
    P="python ${PAPER}/run_grid.py --oat --flow-coverage ${flow} --nb-suppliers ${NB} \
       --t-final ${T_FINAL} --seeds ${s} --criticality ${CRIT_CSV} --shock ${SHOCK_CSV} \
       --utils ${UTIL_BASE} --recon ${RECON_BASE} --public-shares ${PUBLIC_BASE} \
       --target-times ${TARGET_BASE} --recon-lags ${LAG_BASE} --crit-thresholds ${CRIT_FLOORS} \
       --util-base ${UTIL_BASE} --recon-base ${RECON_BASE} --public-base ${PUBLIC_BASE} \
       --target-base ${TARGET_BASE} --lag-base ${LAG_BASE} --crit-base ${CRIT_BASE} \
       --out ${SHARD_DIR}/sat_fc${flow}_s${s}.csv"
    WID=$(submit "sat_fc${flow}_s${s}" "$TIME_WORKER" "$MEM_WORKER" "" "$P")
    WORKER_IDS="${WORKER_IDS}${WORKER_IDS:+:}${WID}"
  done
done

# ---- (B) combine across seeds -> summary + raw concat -> saturation figure ----
CP="python ${PAPER}/combine.py --in ${SHARD_DIR} --out ${SUMMARY} --raw-out ${RAW} && \
    python ${PAPER}/plot/plot_saturation.py ${RAW} --fig ${FIG}"
CID=$(submit "sat_combine" "$TIME_POST" "$MEM_POST" "$WORKER_IDS" "$CP")

n_workers=$(( ${#FLOW_LEVELS[@]} * N_SEEDS ))
echo
echo "Submitted saturation sweep:"
echo "  (A) ${n_workers} jobs = ${#FLOW_LEVELS[@]} flow_coverage x ${N_SEEDS} seeds (each sweeps floors ${CRIT_FLOORS})"
echo "  (B) combine + saturation figure: ${CID}"
echo "  floors=${CRIT_FLOORS}  flow=${FLOW_LEVELS[*]}  nb=${NB}  t_final=${T_FINAL}"
echo "  outputs: ${SUMMARY}, ${RAW}, ${FIG}"
echo "  change the batch size by editing N_SEEDS at the top (or --n-seeds)."
