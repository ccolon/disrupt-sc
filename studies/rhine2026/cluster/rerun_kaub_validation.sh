#!/bin/bash
#
# Rebuild the Kaub-crossing link list of full-export runs on the cache they used and recompute their
# validation outputs (KI-49, 3 Nov 2026): one Slurm job per run, build_kaub_links.py --run <folder> --expect then
# validation_outputs.py, as the launcher's postprocess does since the fix. The outputs the run already holds
# (kaub_links_check.csv/.txt, validation_outputs.csv/.txt) are kept beside the new ones as *_oldlinks.* (not
# overwritten twice: an existing *_oldlinks.* copy is left alone). extract_link_flows.py does not read the list and
# is not rerun. No model rerun: the run folder's link_data.csv is read.
#
# Usage (on the cluster):  bash studies/rhine2026/cluster/rerun_kaub_validation.sh RUN_NAME [RUN_NAME ...]
#
set -e

# ========================= EDIT FOR YOUR CLUSTER ===========================
SCRIPT_DIR="/projects/disruptsc/disrupt-sc"
PYTHON_ENV="/projects/disruptsc/miniforge3/envs/dsc"
DATA_PATH="/projects/disruptsc/disrupt-sc-data"
OUTPUT_DIR="/projects/disruptsc/runs/rhine2026"
SLURM_LOG_DIR="${SCRIPT_DIR}/slurm_logs/rhine2026"
TIME_POST="02:00:00"; MEM_POST="12G"
# ===========================================================================

ACTIVATE="source $(dirname "$(dirname "${PYTHON_ENV}")")/bin/activate ${PYTHON_ENV}"
EXPORTS="export DISRUPT_SC_DATA_PATH=${DATA_PATH} && export PYTHONHASHSEED=0 && export PYTHONIOENCODING=utf-8 && cd ${SCRIPT_DIR}"
mkdir -p "$SLURM_LOG_DIR"

[[ $# -ge 1 ]] || { echo "usage: $0 RUN_NAME [RUN_NAME ...]" >&2; exit 1; }
for name in "$@"; do
    out="${OUTPUT_DIR}/${name}"
    if [[ ! -f "${out}/link_data.csv" ]]; then
        echo "  ${name}: no link_data.csv in ${out} (not a full-export run): skipped" >&2
        continue
    fi
    for f in kaub_links_check.csv kaub_links_check.txt validation_outputs.csv validation_outputs.txt; do
        old="${out}/${f%.*}_oldlinks.${f##*.}"
        [[ -f "${out}/${f}" && ! -f "${old}" ]] && cp -p "${out}/${f}" "${old}"
    done
    payload="python studies/rhine2026/build_kaub_links.py --run ${out} --definition any --expect --out ${out}/kaub_links_check.csv > ${out}/kaub_links_check.txt 2>&1 && python studies/rhine2026/validation_outputs.py ${out} --flags ${out}/kaub_links_check.csv --out ${out}/validation_outputs.csv > ${out}/validation_outputs.txt 2>&1"
    cmd="sbatch --parsable --nodes=1 --ntasks=1 --cpus-per-task=1 --time=${TIME_POST} --mem=${MEM_POST} \
        --job-name=kaub_${name} --output=${SLURM_LOG_DIR}/kaub_${name}.%j.out \
        --wrap=\"bash -c '${EXPORTS} && ${ACTIVATE} && ${payload}'\""
    id=$(eval "$cmd")
    echo "  ${name}: job ${id} (old outputs kept as *_oldlinks.*)" >&2
done
