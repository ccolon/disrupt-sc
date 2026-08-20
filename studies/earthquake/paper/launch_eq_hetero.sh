#!/bin/bash
#
# DisruptSC 2016 Ecuador earthquake — SHOCK-HETEROGENEITY track (idealized experiments).
#
# Holds the destroyed capital fixed and varies only the resolution at which it is
# concentrated: homogeneous (all cantones and sectors, in proportion to capital), then
# one sector / province / canton / province-sector / canton-sector group per draw. This
# is the experiment behind the paper's title claim, and the figures it feeds are
# fig_hetero_mean and fig_hetero_cv.
#
# The draw list is committed experimental design, not something regenerated per run:
#   studies/earthquake/additional_data/hetero_draws/draws_<resolution>.csv
# Rebuild it only when the capital base changes, with build_hetero_draws.py.
#
# Parameters are the earthquake configuration unchanged (monthly steps, supplier
# substitution on, reconstruction on), so these results and the case study are directly
# comparable. Every draw runs on the SAME seed set — Fig. 6 reports a coefficient of
# variation across draws, and sharing seeds keeps network noise common to all of them
# instead of confounded with genuine draw-to-draw heterogeneity.
#
# This is INDEPENDENT of the reference and sensitivity tracks.
#
# Usage:  bash studies/earthquake/paper/launch_eq_hetero.sh [--dry-run] [--n-seeds 3] [--skip-existing]
#
# --skip-existing: don't re-run a seed whose shard (hetero_shards/hetero_s<seed>.csv)
#   already exists; combine always re-runs and refreshes the summary from all shards.
#   run_hetero.py also resumes WITHIN a shard, so a job killed mid-seed picks up where
#   it stopped rather than restarting the whole seed.
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="${SCRIPT_DIR}/output/earthquake_paper"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/eq_hetero"

# ========================= EXPERIMENT DESIGN ===============================
N_SEEDS=3                   # <<< network realizations; every draw runs on all of them
T_FINAL=12                  # months; horizons reported at 3, 6 and 12
TOTAL=2438.7                # destroyed capital (mUSD) — the modeled earthquake shock
# Idle-capital activation time (DAYS). MUST exceed one time step: at 30d with monthly
# steps the activation fraction is min(1, 30/30) = 1, so idle capital is mobilized inside
# the step the shock lands in, and any destruction below the spare-capacity margin
# (1 - utilization_rate = 20% of capital) produces no output loss at all. Passed
# explicitly because the scope config is gitignored and does not reach the cluster.
TAU_ACTIVATE=90
RESOLUTIONS="sector,province,canton,province_sector,canton_sector"

# ------------------------- SLURM resources --------------------------------
# One job per seed: one agent build (the expensive part) then ~207 short replays,
# so the walltime is dominated by the build plus 207 x 12 monthly steps.
TIME_WORKER="24:00:00"; MEM_WORKER="8G"
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
DRAWS_DIR="${SCRIPT_DIR}/studies/earthquake/additional_data/hetero_draws"
SHARD_DIR="${OUTPUT_DIR}/hetero_shards"
FIG_DIR="${OUTPUT_DIR}/figures"
SUMMARY="${OUTPUT_DIR}/hetero_summary.csv"
RAW="${OUTPUT_DIR}/hetero_all.csv"
CRIT_CSV="${SCRIPT_DIR}/studies/earthquake/additional_data/input_criticality.csv"
DATA_OVERRIDES="--criticality ${CRIT_CSV}"
ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0"

if [[ ! -d "$DRAWS_DIR" ]]; then
    echo "ERROR: draw list not found at ${DRAWS_DIR}" >&2
    echo "  git pull, or regenerate with:" >&2
    echo "    python ${PAPER}/build_hetero_draws.py --run <run_dir> --out ${DRAWS_DIR}" >&2
    exit 1
fi

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

# ---- one worker per seed --------------------------------------------------
WORKER_IDS=""
for (( s=0; s<N_SEEDS; s++ )); do
  SHARD="${SHARD_DIR}/hetero_s${s}.csv"
  if [[ "$SKIP_EXISTING" == true && -s "$SHARD" ]]; then
      echo "  skip hetero_s${s} (shard exists: ${SHARD})" >&2
      continue
  fi
  # --skip-existing is passed through so a requeued job resumes inside the shard
  P="python ${PAPER}/run_hetero.py --draws ${DRAWS_DIR} --seeds ${s} --total ${TOTAL} \
     --t-final ${T_FINAL} --resolutions ${RESOLUTIONS} --tau-activate ${TAU_ACTIVATE} ${DATA_OVERRIDES} \
     --skip-existing --out ${SHARD}"
  add_id WORKER_IDS "$(submit "hetero_s${s}" "$TIME_WORKER" "$MEM_WORKER" "" "$P")"
done

# ---- combine -> summary + raw concat + figures ----------------------------
CP="python ${PAPER}/combine_hetero.py --in ${SHARD_DIR} --out ${SUMMARY} --raw-out ${RAW}"
if [[ -f "${PAPER}/plot/plot_hetero.py" ]]; then
    CP="${CP} && python ${PAPER}/plot/plot_hetero.py ${RAW} --fig-dir ${FIG_DIR}"
fi
CID=$(submit "hetero_combine" "$TIME_POST" "$MEM_POST" "$WORKER_IDS" "$CP")

n_draws=$(( $(cat "${DRAWS_DIR}"/draws_{sector,province,canton,province_sector,canton_sector}.csv 2>/dev/null | grep -cv '^resolution,') ))
echo
echo "Submitted HETEROGENEITY track: ${N_SEEDS} seed jobs + combine ${CID}"
echo "  ${n_draws} draws + 1 homogeneous reference per seed, ${TOTAL} mUSD destroyed, ${T_FINAL} months, tau=${TAU_ACTIVATE}d"
echo "  outputs: ${SUMMARY}, ${RAW}"
if [[ ! -f "${PAPER}/plot/plot_hetero.py" ]]; then
    echo "  NOTE: plot/plot_hetero.py does not exist yet — combine will produce the CSVs only."
fi
$SKIP_EXISTING && echo "  --skip-existing ON: seeds with a shard are skipped; run_hetero.py also resumes within a shard."
echo "  change the batch size with --n-seeds."
