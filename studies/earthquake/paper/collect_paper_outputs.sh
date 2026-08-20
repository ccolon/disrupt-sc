#!/bin/bash
#
# Bundle everything the manuscript needs into one zip, small enough to move off the cluster.
#
# The bulk of a reference run is the per-seed firm-level exports (firm_data.csv is tens of MB
# per seed). Almost none of that is needed to write the paper: the figures and tables are
# already aggregated across seeds. So this takes the aggregates in full, plus exactly one
# seed's firm_data.csv for the agent counts quoted in Sec. 2.6, and leaves the rest behind.
#
# The small per-seed analysis CSVs are taken from every seed, so across-seed spread
# remains computable for disaggregated quantities, not just for the headline.
#
# It also captures the reference run LOG, which is the only place two Sec. 2.6 numbers exist:
# household inventories as a share of GDP, and the shock-placement diagnostics behind the
# "damage that failed to land" discussion. Neither is written to any CSV.
#
# Usage:
#   bash studies/earthquake/paper/collect_paper_outputs.sh [OUTPUT_DIR] [ZIP_PATH] [SEED]
#
# Defaults resolve to the standard repo layout, seed 0, and a timestamped zip in $HOME.
# Extract into your local output/ folder:
#   unzip -o paper_outputs_<stamp>.zip -d /path/to/disrupt-sc/output
#
set -uo pipefail

PAPER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$PAPER/../../.." && pwd)"

OUTPUT_DIR=${1:-$REPO/output/earthquake_paper}
ZIP_PATH=${2:-$HOME/paper_outputs_$(date +%Y%m%d_%H%M).zip}
SEED=${3:-0}

[ -d "$OUTPUT_DIR" ] || { echo "ERROR: no output dir at $OUTPUT_DIR" >&2; exit 1; }

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
DEST="$STAGE/earthquake_paper"
mkdir -p "$DEST/figures" "$DEST/reference/seed_${SEED}" "$DEST/logs"

n_have=0
n_miss=0
take() {  # take <src> <dest-relative-dir> ; missing files are reported, not fatal
    local src=$1 rel=$2
    if [ -e "$src" ]; then
        mkdir -p "$DEST/$rel"
        cp -r "$src" "$DEST/$rel/" && n_have=$((n_have + 1))
    else
        echo "  MISSING: ${src#$OUTPUT_DIR/}" >&2
        n_miss=$((n_miss + 1))
    fi
}

echo "collecting from $OUTPUT_DIR (seed $SEED)"

# ---- headline tables ------------------------------------------------------
take "$OUTPUT_DIR/models_table.csv"        "."
take "$OUTPUT_DIR/gdp_by_seed.csv"         "."
take "$OUTPUT_DIR/sensitivity_summary.csv" "."
take "$OUTPUT_DIR/sensitivity_all.csv"     "."
take "$OUTPUT_DIR/hetero_summary.csv"      "."
take "$OUTPUT_DIR/hetero_all.csv"          "."

# ---- figures --------------------------------------------------------------
for f in fig_distribution.png fig_uq.png fig_sensitivity.png fig_hetero.png; do
    take "$OUTPUT_DIR/figures/$f" "figures"
done

# ---- seed-averaged analysis (what the figures are actually drawn from) -----
# Small CSVs; taken whole so any number quoted in the text can be traced back.
take "$OUTPUT_DIR/figures/ref_avg" "figures"

# ---- per-seed analysis CSVs, from EVERY seed ------------------------------
# distribution.py and uq_did.py write into each seed dir, and average_runs.py then
# collapses them into figures/ref_avg. Taking only the average would leave no way to put
# an across-seed band on anything disaggregated -- models_table.csv carries the spread of
# the headline household loss and nothing else. These files are a few kB each, unlike the
# firm-level exports below, so all seeds are cheap to carry.
n_seed_dirs=0
for d in "$OUTPUT_DIR"/reference/seed_*; do
    [ -d "$d" ] || continue
    n_seed_dirs=$((n_seed_dirs + 1))
    sd=$(basename "$d")
    for f in loss_by_sector_time.csv loss_by_province_year.csv loss_by_canton_year.csv \
             uq_eventstudy.csv uq_did.csv; do
        [ -e "$d/$f" ] && { mkdir -p "$DEST/reference/$sd"; cp "$d/$f" "$DEST/reference/$sd/"; \
                            n_have=$((n_have + 1)); }
    done
done
echo "  per-seed analysis CSVs from $n_seed_dirs seed dir(s)"

# ---- one seed's firm-level export, for the Sec. 2.6 agent counts ----------
# These are the bulk of a reference run (tens of MB each), so only the chosen seed.
take "$OUTPUT_DIR/reference/seed_${SEED}/firm_data.csv"       "reference/seed_${SEED}"
take "$OUTPUT_DIR/reference/seed_${SEED}/household_data.csv"  "reference/seed_${SEED}"
take "$OUTPUT_DIR/reference/seed_${SEED}/firm_table.geojson"  "reference/seed_${SEED}"

# ---- run logs: the only source for two Sec. 2.6 numbers -------------------
# Inventory-to-GDP and the capital-destruction placement diagnostics are logged, never
# written to CSV. Grab the newest log per track rather than every rotation.
for pat in "$REPO/slurm_logs/eq_reference/ref_s${SEED}".*.out \
           "$REPO/slurm_logs/eq_hetero/hetero_s${SEED}".*.out \
           "$REPO/slurm_logs/eq_sensitivity/oat_base_s${SEED}".*.out; do
    newest=$(ls -t $pat 2>/dev/null | head -1)
    [ -n "$newest" ] && take "$newest" "logs"
done

# ---- provenance: what produced all this -----------------------------------
{
    echo "collected      : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "host           : $(hostname)"
    echo "output_dir     : $OUTPUT_DIR"
    echo "seed exported  : $SEED"
    echo "git commit     : $(cd "$REPO" && git rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "git status     : $(cd "$REPO" && git status --porcelain 2>/dev/null | wc -l) modified files"
    echo
    echo "shard counts:"
    echo "  reference seeds : $(ls -d "$OUTPUT_DIR"/reference/seed_* 2>/dev/null | wc -l)"
    echo "  hetero shards   : $(ls "$OUTPUT_DIR"/hetero_shards/hetero_s*.csv 2>/dev/null | wc -l)"
    echo "  sensitivity     : $(ls "$OUTPUT_DIR"/sensitivity_shards/*.csv 2>/dev/null | wc -l)"
} > "$DEST/MANIFEST.txt"

echo
echo "$n_have items collected, $n_miss missing"

# zip if available, otherwise tar.gz -- some cluster images ship without zip, and the
# staging dir is removed on exit, so falling back has to happen here rather than in a hint.
# The archive is written from inside its own directory with a bare filename: an absolute
# Windows-style path (C:/...) would be read by tar as a remote host spec because of the colon.
OUTDIR=$(cd "$(dirname "$ZIP_PATH")" && pwd)
if command -v zip >/dev/null 2>&1; then
    ARCHIVE="$OUTDIR/$(basename "$ZIP_PATH")"
    ( cd "$STAGE" && zip -qr "$ARCHIVE" earthquake_paper ) \
        || { echo "ERROR: zip failed" >&2; exit 1; }
    EXTRACT="unzip -o $(basename "$ARCHIVE") -d <repo>/output"
else
    echo "note: zip not found, writing a tar.gz instead" >&2
    NAME="$(basename "${ZIP_PATH%.zip}").tgz"
    ( cd "$OUTDIR" && tar czf "$NAME" -C "$STAGE" earthquake_paper ) \
        || { echo "ERROR: tar failed" >&2; exit 1; }
    ARCHIVE="$OUTDIR/$NAME"
    EXTRACT="tar xzf $NAME -C <repo>/output"
fi

echo "wrote $ARCHIVE  ($(du -h "$ARCHIVE" | cut -f1))"
echo
echo "extract locally with:"
echo "  $EXTRACT"
[ "$n_miss" -gt 0 ] && echo "NOTE: $n_miss expected items were missing -- see MISSING lines above."
exit 0
