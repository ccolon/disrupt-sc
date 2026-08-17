#!/bin/bash
#
# Reference-track postprocess: per-seed analyze -> average across seeds -> figures + table.
#
# Split out of launch_eq_reference.sh on purpose. That launcher builds its sbatch command as
# a string and eval's it, with the payload nested inside --wrap="bash -c '...'", so ANY
# double quote, paren or $(...) in the payload gets exposed at eval time and breaks the
# submit (a literal "seed(s)" in an echo was enough: syntax error near unexpected token '(').
# Keeping the logic here means the payload stays one flat command with no metacharacters.
#
# Usage:
#   bash postprocess_reference.sh REF_ROOT FIG_DIR OUTPUT_DIR CANTON_MMI GADM UQ_TWFE
#
# Safe to re-run by hand (per-seed analysis is idempotent -- it overwrites in place), which
# is also how you recover when the chained SLURM job dies.
set -uo pipefail

REF_ROOT=${1:?REF_ROOT (dir holding seed_*/)}
FIG_DIR=${2:?FIG_DIR}
OUTPUT_DIR=${3:?OUTPUT_DIR}
CANTON_MMI=${4:?canton_mmi_bin.csv}
GADM=${5:?gadm41_ECU_2.json}
UQ_TWFE=${6:?twfe_event_study_coefs.csv}

PAPER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$FIG_DIR"

# ---- per-seed analyze ------------------------------------------------------
# Deliberately NOT fail-fast: one bad seed must not cost us the other 49.
n_dirs=0
n_fail=0
for d in "$REF_ROOT"/seed_*; do
    [ -d "$d" ] || continue
    n_dirs=$((n_dirs + 1))
    if ! python "$PAPER/analyze/distribution.py" "$d" --out-dir "$d"; then
        echo "WARN: distribution.py failed for $d" >&2
        n_fail=$((n_fail + 1))
    fi
    if ! python "$PAPER/analyze/uq_did.py" "$d" --canton-mmi "$CANTON_MMI" --out-dir "$d"; then
        echo "WARN: uq_did.py failed for $d" >&2
        n_fail=$((n_fail + 1))
    fi
done

n_ok=$(ls "$REF_ROOT"/seed_*/uq_eventstudy.csv 2>/dev/null | wc -l)
echo "per-seed analyze: $n_dirs seed dirs, $n_ok with uq_eventstudy.csv, $n_fail script failures"

# Guard: averaging/plotting on nothing produces confusing downstream errors instead of
# pointing at the real problem (a 50-seed run once yielded zero outputs and only surfaced
# as a bare exit code).
if [ "$n_ok" -eq 0 ]; then
    echo "ERROR: per-seed analyze produced NO uq_eventstudy.csv -- aborting before average/plot." >&2
    echo "       Run one seed by hand to see the traceback:" >&2
    echo "       python $PAPER/analyze/uq_did.py $REF_ROOT/seed_0 --canton-mmi $CANTON_MMI --out-dir $REF_ROOT/seed_0" >&2
    exit 1
fi

# ---- average across seeds -> figures + model table -------------------------
# From here a failure is real, so stop at the first one. NB the seed_* globs are quoted:
# average_runs.py / plot_model_table.py expand them themselves.
set -e
python "$PAPER/average_runs.py" --glob "$REF_ROOT/seed_*" --out-dir "$FIG_DIR/ref_avg"
python "$PAPER/plot/plot_distribution.py" "$FIG_DIR/ref_avg" --gadm "$GADM" --fig "$FIG_DIR/fig_distribution.png"
python "$PAPER/plot/plot_uq.py" "$FIG_DIR/ref_avg/uq_eventstudy.csv" --uq "$UQ_TWFE" --fig "$FIG_DIR/fig_uq.png"
python "$PAPER/plot/plot_model_table.py" --ref-glob "$REF_ROOT/seed_*" --out "$OUTPUT_DIR/models_table.csv"

echo "postprocess done:"
echo "  $FIG_DIR/fig_distribution.png"
echo "  $FIG_DIR/fig_uq.png"
echo "  $OUTPUT_DIR/models_table.csv"
