#!/bin/bash
# Policy scenario: halve every sector's b_{j,k} EXCEPT the identified
# bottleneck sectors (utility, transport) which stay at baseline.
# Tests whether selective inventory reduction can reduce losses relative
# to the uniform M=1 baseline (bullwhip mitigation).
#
# Grid:
#   D   ∈ {4, 8, 12}
#   tau ∈ {0, 0.5, 1, 1.5, 2, 2.5, 3}  (same as sensitivity_inventory sweep)
#   M   = 0.5 applied to all sectors EXCEPT {utility, transport}
# => 3 x 7 = 21 runs, ~4-5 h local.  Seed=42.

set -euo pipefail

SCOPE="Cambodia"
SEED=42
T=4
M_SECTOR=0.5
EXCLUDE="utility,transport"

DURATIONS=(4 8 12)
TAUS=(0 0.5 1 1.5 2 2.5 3)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_CSV="${REPO_ROOT}/output/${SCOPE}/sensitivity_inventory_protect.csv"
LOG_DIR="${REPO_ROOT}/logs/${SCOPE}"
mkdir -p "${LOG_DIR}" "$(dirname "${OUTPUT_CSV}")"

TOTAL=$(( ${#DURATIONS[@]} * ${#TAUS[@]} ))
IDX=0
DONE=0
SKIPPED=0
START_ALL=$(date +%s)

lag_from_tau_D() {
    python3 -c "import sys; tau=float(sys.argv[1]); D=int(sys.argv[2]); print(int(round(tau*D)))" "$1" "$2"
}

combo_already_done() {
    local sim="$1" dur="$2" mult="$3" rest="$4" seed="$5" excl="$6"
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
                and str(row.get("seed", "")).strip() == "${seed}"
                and row.get("excluded_sectors", "") == "${excl}"):
                sys.exit(0)
except Exception:
    pass
sys.exit(1)
PYEOF
}

for D in "${DURATIONS[@]}"; do
    for TAU in "${TAUS[@]}"; do
        IDX=$(( IDX + 1 ))
        LAG=$(lag_from_tau_D "${TAU}" "${D}")
        SIM="cascading_hazards_${LAG}d"
        TAG="D${D}_tau${TAU}"
        LOG_FILE="${LOG_DIR}/sensitivity_inventory_protect_${TAG}.log"

        if combo_already_done "${SIM}" "${D}" "${M_SECTOR}" "${T}" "${SEED}" "${EXCLUDE}"; then
            SKIPPED=$(( SKIPPED + 1 ))
            echo "--- [${IDX}/${TOTAL}] ${TAG} (${SIM}) already in CSV, skipping ---"
            continue
        fi

        echo "=== [${IDX}/${TOTAL}] $(date +%H:%M:%S)  ${TAG}  (${SIM}, M=${M_SECTOR} except ${EXCLUDE}) ==="
        START=$(date +%s)

        python "${REPO_ROOT}/scripts/run_sensitivity_inventory.py" \
            --scope "${SCOPE}" \
            --simulation_name "${SIM}" \
            --duration "${D}" \
            --inventory_multiplier "${M_SECTOR}" \
            --exclude_sectors "${EXCLUDE}" \
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
