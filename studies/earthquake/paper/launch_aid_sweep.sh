#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — FOREIGN-AID 2D sweep.
#
#   reconstruction_public_share {0.0, 0.8}  x  capital_input_mix {domestic, mixed, import}
#   = 6 points x N_SEEDS, with mechanism diagnostics (capital recovery speed, CON/MAN
#   crowding-out, domestic reconstruction activity). See sweep_aid.py header.
#
# public_share = aid FUNDING dimension (external/direct rebuild); mix IMP fraction =
# aid IN-KIND / import sourcing. The grid shows the mix only has leverage when
# public_share is low (the challenge's key point).
#
# The whole grid runs in ONE process (builds once per seed, loops the 6 points), so
# this is a single job. Data files are the committed additional_data/ copies.
#
# Usage:  bash studies/earthquake/paper/launch_aid_sweep.sh [--dry-run] [--n-seeds 5]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="${SCRIPT_DIR}/output/earthquake_aid"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/eq_aid"

N_SEEDS=5
T_FINAL=13
TIME_JOB="04:00:00"; MEM_JOB="6G"
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
AD="${SCRIPT_DIR}/studies/earthquake/additional_data"
CRIT_CSV="${AD}/input_criticality.csv"
SHOCK_CSV="${AD}/earthquake_shock_modelready.csv"
RAW="${OUTPUT_DIR}/aid_all.csv"
FIG="${OUTPUT_DIR}/fig_aid.png"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"

if ! $DRY_RUN; then
  for f in "$CRIT_CSV" "$SHOCK_CSV"; do
    [[ -f "$f" ]] || { echo "ERROR: missing data file $f" >&2; exit 1; }
  done
fi
$DRY_RUN || mkdir -p "$OUTPUT_DIR" "$SLURM_LOG_DIR"
$DRY_RUN || rm -f "$RAW"    # fresh (sweep_aid appends)

P="python ${PAPER}/sweep_aid.py --n-seeds ${N_SEEDS} --t-final ${T_FINAL} \
   --criticality ${CRIT_CSV} --shock ${SHOCK_CSV} --out ${RAW} && \
   python ${PAPER}/plot/plot_aid.py ${RAW} --fig ${FIG}"

CMD="sbatch --parsable --nodes=1 --ntasks=1 --time=${TIME_JOB} --mem=${MEM_JOB} \
     --job-name=eq_aid --output=${SLURM_LOG_DIR}/eq_aid.%j.out \
     --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${P}'\""
if $DRY_RUN; then echo "DRYRUN[eq_aid]: ${P}"; else eval "$CMD"; fi

echo
echo "Submitted foreign-aid 2D sweep: public_share {0,0.8} x mix {domestic,mixed,import} x ${N_SEEDS} seeds"
echo "  outputs: ${RAW}, ${FIG}"
