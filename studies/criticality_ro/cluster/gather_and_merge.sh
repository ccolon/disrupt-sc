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

cd "${REPO}"
git add studies/criticality_ro/results studies/criticality_ro/chunks
git commit -m "Romania criticality ${PREFIX}: ${n} chunk results gathered + merged (cluster)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" || echo "nothing new to commit"
echo "results committed on the cluster - push to bring them back to the laptop"
