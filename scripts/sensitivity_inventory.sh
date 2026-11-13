#!/bin/bash
# Local sequential sweep over (M, D, tau) for cascading_hazards_Xd scenarios.
# Produces the data needed to replicate notebook 03's left-panel figure for
# different inventory multipliers M.
#
# Grid:
#   M   ∈ {0.5, 1.0, 2.0}            (inventory multiplier on table S1)
#   D   ∈ {4, 8, 12}                 (disruption duration)
#   tau ∈ {0, 0.5, 1, 1.5, 2}        (basin-lag / duration)
# => 45 combinations total.  All runs use --seed 42 so the SC-network is
# identical across all points: variation in household loss is 100% the
# M / D / tau effect.
#
# T (inventory_restoration_time) is held at baseline T=4 throughout.
#
# Per-run time ≈ 12 min, total ≈ 9 h.  Resume-safe: re-launch to pick up
# where it stopped.

set -euo pipefail

SCOPE="Cambodia"
SEED=42
T=4

INVENTORY_MULTIPLIERS=(0.5 1.0 2.0)
DURATIONS=(4 8 12)
TAUS=(0 0.5 1 1.5 2)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_CSV="${REPO_ROOT}/output/${SCOPE}/sensitivity_inventory.csv"
LOG_DIR="${REPO_ROOT}/logs/${SCOPE}"
mkdir -p "${LOG_DIR}" "$(dirname "${OUTPUT_CSV}")"

TOTAL=$(( ${#INVENTORY_MULTIPLIERS[@]} * ${#DURATIONS[@]} * ${#TAUS[@]} ))
IDX=0
DONE=0
SKIPPED=0
START_ALL=$(date +%s)

# tau * D -> integer time_lag.  (Our tau grid × our D grid always gives integers.)
lag_from_tau_D() {
    python3 -c "import sys; tau=float(sys.argv[1]); D=int(sys.argv[2]); print(int(round(tau*D)))" "$1" "$2"
}

combo_already_done() {
    local sim="$1" dur="$2" mult="$3" rest="$4" seed="$5"
    python3 - <<PYEOF
import csv, sys
from pathlib import Path
p = Path("${OUTPUT_CSV}")
if not p.exists():
    sys.exit(1)
try:
    with open(p, newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("simulation_name") == "${sim}"
                and int(float(row.get("duration", "nan"))) == ${dur}
                and float(row.get("inventory_multiplier", "nan")) == ${mult}
                and float(row.get("inventory_restoration_time", "nan")) == ${rest}
                and str(row.get("seed", "")).strip() == "${seed}"):
                sys.exit(0)
except Exception:
    pass
sys.exit(1)
PYEOF
}

for M in "${INVENTORY_MULTIPLIERS[@]}"; do
    for D in "${DURATIONS[@]}"; do
        for TAU in "${TAUS[@]}"; do
            IDX=$(( IDX + 1 ))
            LAG=$(lag_from_tau_D "${TAU}" "${D}")
            SIM="cascading_hazards_${LAG}d"
            TAG="M${M}_D${D}_tau${TAU}"
            LOG_FILE="${LOG_DIR}/sensitivity_inventory_${TAG}.log"

            if combo_already_done "${SIM}" "${D}" "${M}" "${T}" "${SEED}"; then
                SKIPPED=$(( SKIPPED + 1 ))
                echo "--- [${IDX}/${TOTAL}] ${TAG} (${SIM}) already in CSV, skipping ---"
                continue
            fi

            echo "=== [${IDX}/${TOTAL}] $(date +%H:%M:%S)  ${TAG}  (${SIM}) ==="
            START=$(date +%s)

            python "${REPO_ROOT}/scripts/run_sensitivity_inventory.py" \
                --scope "${SCOPE}" \
                --simulation_name "${SIM}" \
                --duration "${D}" \
                --inventory_multiplier "${M}" \
                --inventory_restoration_time "${T}" \
                --seed "${SEED}" \
                --output_csv "${OUTPUT_CSV}" \
                --cache_isolation \
                2>&1 | tee "${LOG_FILE}"

            DONE=$(( DONE + 1 ))
            ELAPSED=$(( $(date +%s) - START ))
            echo "    done in ${ELAPSED}s -> appended to ${OUTPUT_CSV}"
        done
    done
done

TOTAL_ELAPSED=$(( $(date +%s) - START_ALL ))
echo ""
echo "Finished.  Ran ${DONE} new, skipped ${SKIPPED} already-done.  Wall time ${TOTAL_ELAPSED}s."
echo "Results: ${OUTPUT_CSV}"
