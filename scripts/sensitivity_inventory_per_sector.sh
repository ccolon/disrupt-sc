#!/bin/bash
# Per-sector inventory sensitivity (D-scan) at tau=0 (simultaneous cascade).
# For each (D, sector): halve ONLY that sector's b_{j,k}, others at baseline.
# Identifies whether the inventory bottleneck depends on disruption length.
#
# Grid:
#   D      ∈ {4, 8, 12}
#   sector ∈ {utility, agriculture, manufacturing, service, trade,
#             construction, transport}
#   M_sector = 0.5
#   tau = 0, T = 4, seed = 42
# => 3 x 7 = 21 runs total, ~5 h locally.
#
# Baseline rows (all M=1) at (D, tau=0) are already in sensitivity_inventory.csv
# and get picked up by the notebook.  Resume-safe.

set -euo pipefail

SCOPE="Cambodia"
SEED=42
T=4
TAU=0
SIM="cascading_hazards_0d"
M_SECTOR=0.5

DURATIONS=(4 8 12)
SECTORS=(utility agriculture manufacturing service trade construction transport)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_CSV="${REPO_ROOT}/output/${SCOPE}/sensitivity_inventory_per_sector.csv"
LOG_DIR="${REPO_ROOT}/logs/${SCOPE}"
mkdir -p "${LOG_DIR}" "$(dirname "${OUTPUT_CSV}")"

TOTAL=$(( ${#DURATIONS[@]} * ${#SECTORS[@]} ))
IDX=0
DONE=0
SKIPPED=0
START_ALL=$(date +%s)

combo_already_done() {
    local sim="$1" dur="$2" mult="$3" sector="$4" rest="$5" seed="$6"
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
                and row.get("target_sector", "") == "${sector}"
                and float(row.get("inventory_restoration_time", "nan")) == ${rest}
                and str(row.get("seed", "")).strip() == "${seed}"):
                sys.exit(0)
except Exception:
    pass
sys.exit(1)
PYEOF
}

for D in "${DURATIONS[@]}"; do
    for SECTOR in "${SECTORS[@]}"; do
        IDX=$(( IDX + 1 ))
        TAG="D${D}_halve_${SECTOR}"
        LOG_FILE="${LOG_DIR}/sensitivity_inventory_${TAG}.log"

        if combo_already_done "${SIM}" "${D}" "${M_SECTOR}" "${SECTOR}" "${T}" "${SEED}"; then
            SKIPPED=$(( SKIPPED + 1 ))
            echo "--- [${IDX}/${TOTAL}] ${TAG} already in CSV, skipping ---"
            continue
        fi

        echo "=== [${IDX}/${TOTAL}] $(date +%H:%M:%S)  ${TAG}  (M_${SECTOR}=${M_SECTOR}, D=${D}, tau=${TAU}) ==="
        START=$(date +%s)

        python "${REPO_ROOT}/scripts/run_sensitivity_inventory.py" \
            --scope "${SCOPE}" \
            --simulation_name "${SIM}" \
            --duration "${D}" \
            --inventory_multiplier "${M_SECTOR}" \
            --target_sector "${SECTOR}" \
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

TOTAL_ELAPSED=$(( $(date +%s) - START_ALL ))
echo ""
echo "Finished.  Ran ${DONE} new, skipped ${SKIPPED} already-done.  Wall time ${TOTAL_ELAPSED}s."
echo "Results: ${OUTPUT_CSV}"
