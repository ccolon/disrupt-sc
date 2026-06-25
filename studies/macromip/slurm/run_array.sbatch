#!/bin/bash
#SBATCH --job-name=macromip-s1
#SBATCH --array=0-6
#SBATCH --time=10:00:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=4
#SBATCH --output=runs/macromip/slurm/logs/%x_%a.out
#SBATCH --error=runs/macromip/slurm/logs/%x_%a.err

# macroMIP s1 experiment matrix on DisruptSC.
#
# One array task per experiment (exp0 baseline + {1,2,3} x {persistent, temporary}).
# Each task builds the world independently; with seed 0 the supply-chain build is
# deterministic, so every experiment shares an identical baseline economy. The
# cache is isolated per task (--cache-isolation) so concurrent builds writing to a
# shared tmp/ on the cluster filesystem don't collide.
#
# Build setting "Option A": flow_coverage 0.9, nb_suppliers 1
#   -> captures ~72% of the MRIO's 13.3% international intermediate trade
#   -> ~80 s/step => ~2.7 h/experiment at t_final=120 (10 years monthly).
#
# Submit from the repo root:
#     sbatch studies/macromip/slurm/run_array.sbatch
# Run a subset (e.g. just the required temporary set):
#     sbatch --array=0,2,4,6 studies/macromip/slurm/run_array.sbatch

set -euo pipefail

# ---- cluster environment (EDIT FOR YOUR CLUSTER) --------------------------
# module load anaconda3
# source activate dsc
: "${DISRUPT_SC_DATA_PATH:?set DISRUPT_SC_DATA_PATH to the data root containing macroMIP/}"
# ---------------------------------------------------------------------------

cd "${SLURM_SUBMIT_DIR:-$PWD}"
mkdir -p runs/macromip/slurm/logs

EXPERIMENTS=(exp0 exp1p exp1t exp2p exp2t exp3p exp3t)
EXP="${EXPERIMENTS[$SLURM_ARRAY_TASK_ID]}"
echo "[$(date)] task ${SLURM_ARRAY_TASK_ID} -> ${EXP} on $(hostname)"

python scripts/run_macromip.py \
    --experiment "${EXP}" \
    --flow-coverage 0.9 --nb-suppliers 1 \
    --time-resolution month --t-final 120 \
    --seed 0 --cache-isolation

# Transform raw output -> macroMIP submission CSV
python -m disruptsc.reporting.macromip --run-dir "runs/macromip/${EXP}"

# link_data.csv is multi-GB at fc 0.9 x 120 steps and redundant once the adapter
# has run (the country-level trade it needs is in the compact trade_data.csv).
# Removed only after the adapter above succeeds (set -e aborts otherwise).
rm -f "runs/macromip/${EXP}/link_data.csv"

echo "[$(date)] done ${EXP}"
