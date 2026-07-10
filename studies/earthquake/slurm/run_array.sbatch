#!/bin/bash
#SBATCH --job-name=ecuador-eq
#SBATCH --array=0-199
#SBATCH --time=03:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --output=studies/earthquake/slurm/logs/%x_%a.out
#SBATCH --error=studies/earthquake/slurm/logs/%x_%a.err

# 2016 Ecuador earthquake ensemble on DisruptSC.
#
# 200 array tasks = 4 variants x 50 seeds. Task index -> (variant, seed):
#     variant = VARIANTS[ task / 50 ],  seed = task % 50
#   V1 substitution off / reconstruction off    tasks   0- 49
#   V2 substitution on  / reconstruction off    tasks  50- 99
#   V3 substitution off / reconstruction on     tasks 100-149
#   V4 substitution on  / reconstruction on     tasks 150-199
#
# Transport is OFF (driver default): the capital-destruction shock propagates
# through supply chains, not the physical network (~6 s/step, ~7,300 firms).
# Horizon: 365 days (V1/V2) or 730 days (V3/V4, to capture the recovery tail).
# Each task is cache-isolated (--cache-isolation) so concurrent builds writing to
# a shared tmp/ on the cluster filesystem don't collide; with a fixed seed the
# supply-chain build is deterministic per seed.
#
# Submit from the repo root (ecuador branch):
#     sbatch studies/earthquake/slurm/run_array.sbatch
# Subsets, e.g. just V1+V3 (no-recon + recon) for seed 0..9:
#     sbatch --array=0-9,100-109 studies/earthquake/slurm/run_array.sbatch
# Aggregate after the array completes (Phase 3/4):
#     python studies/earthquake/postprocess.py V1 V2 V3 V4

set -euo pipefail

# ---- cluster environment (EDIT FOR YOUR CLUSTER) --------------------------
# module load anaconda3
# source activate dsc
: "${DISRUPT_SC_DATA_PATH:?set DISRUPT_SC_DATA_PATH to the data root containing Ecuador/}"
PY="${PY:-python}"   # override with the env's python if needed
# ---------------------------------------------------------------------------

cd "${SLURM_SUBMIT_DIR:-$PWD}"
mkdir -p studies/earthquake/slurm/logs

VARIANTS=(V1 V2 V3 V4)
SEEDS_PER_VARIANT="${SEEDS_PER_VARIANT:-50}"
vi=$(( SLURM_ARRAY_TASK_ID / SEEDS_PER_VARIANT ))
SEED=$(( SLURM_ARRAY_TASK_ID % SEEDS_PER_VARIANT ))
VARIANT="${VARIANTS[$vi]}"
case "$VARIANT" in
  V1|V2) TFINAL=365 ;;   # no reconstruction
  V3|V4) TFINAL=730 ;;   # reconstruction: capture the recovery tail
esac

echo "[$(date)] task ${SLURM_ARRAY_TASK_ID} -> ${VARIANT} seed ${SEED} (t_final=${TFINAL}) on $(hostname)"

"$PY" scripts/run_earthquake.py \
    --variant "$VARIANT" --seed "$SEED" --t-final "$TFINAL" \
    --cache-isolation

# link_data.csv is large and not needed for the canton/UQ post-processing
# (which uses firm_data.csv + household_data.csv). Drop it to save space.
rm -f "runs/earthquake/${VARIANT}/seed_${SEED}/link_data.csv"

echo "[$(date)] done ${VARIANT} seed ${SEED}"
