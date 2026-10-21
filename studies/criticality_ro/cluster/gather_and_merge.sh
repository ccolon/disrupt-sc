#!/bin/bash
#
# Gather the Romania criticality chunk CSVs into the committed results folder,
# merge (+ generate the Tier-2 chunks after Tier 1), and commit on the cluster
# so the results travel back by git. Runs as the dependent Slurm job queued by
# launch_criticality.sh (or by hand: bash gather_and_merge.sh t1|t2).
#
set -e
PREFIX="${1:-t1}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"     # studies/criticality_ro
REPO="$(cd "${HERE}/../.." && pwd)"
CRIT="${REPO}/output/Romania/criticality"

mkdir -p "${HERE}/results/${PREFIX}_chunks"
n=0
for d in "${CRIT}/${PREFIX}_chunk_"*/; do
    [[ -f "${d}criticality_results.csv" ]] || continue
    nn=$(basename "$d")
    cp "${d}criticality_results.csv" "${HERE}/results/${PREFIX}_chunks/${nn}.csv"
    cp "${d}criticality_results.fingerprint.json" \
       "${HERE}/results/${PREFIX}_chunks/${nn}.fingerprint.json" 2>/dev/null || true
    n=$((n+1))
done
echo "gathered ${n} ${PREFIX} chunk CSVs into studies/criticality_ro/results/${PREFIX}_chunks/"

python "${HERE}/merge_results.py" --prefix "${PREFIX}"

# Package for download instead of committing (user preference, 21 Oct 2026:
# results stay OUT of git - and git is not on PATH in batch jobs anyway).
# Download the zip via the cluster file manager (as for rhine-2026) and
# extract it at studies/criticality_ro/ on the laptop.
( cd "${HERE}" && python -m zipfile -c "criticality_${PREFIX}_results.zip" \
      "results/${PREFIX}_chunks" "results/${PREFIX}_merged" chunks )
echo "packaged ${HERE}/criticality_${PREFIX}_results.zip - download it via the"
echo "cluster file manager and extract at studies/criticality_ro/ locally"
