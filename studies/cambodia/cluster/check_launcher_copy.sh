#!/bin/bash
#
# Checks the copy step of a launch_cambodia.sh job (8 Nov 2026, KI-56): bash only, no sbatch, no model. The command
# of one job is taken from a dry run and run with a fake model (writes one file, returns a chosen status) and a fake
# destination (a local folder, or a path whose parent is a file, so that every copy attempt fails).
# Expected: the run's own status when the copy succeeds; when every attempt fails, 75 if the run succeeded and the
# run's status otherwise, with the message in the job's stderr.
#
# Usage (from the repository root): bash studies/cambodia/cluster/check_launcher_copy.sh
#
set -u
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
printf '3 lag13 12 --t-final 116\n' > "$work/jobs.txt"
line=$(CAMBODIA_CODE_DIR="$here/../../.." bash "$here/launch_cambodia.sh" --jobs "$work/jobs.txt" --batch chk \
    --dry-run 2>&1 >/dev/null | grep '^DRYRUN\[cam_lag13')
payload=$(sed 's/^DRYRUN\[[^]]*\]\( (afterok:[0-9]*)\)\{0,1\}: //' <<< "$line")
dest=/projects/disruptsc/runs/cambodia/chk
runner="python studies/cambodia/run_cambodia.py"
[[ "$payload" == *"$dest/"* && "$payload" == *"$runner"* ]] || { echo "FAIL: unexpected job command: $payload"; exit 1; }
# submit() wraps the command in bash -c '...' inside sbatch --wrap: a single quote in it would break the job.
[[ "$payload" != *"'"* ]] || { echo "FAIL: single quote in the job command"; exit 1; }

fake_run() {   # writes loss_summary.csv into --out and returns $FAKE_RC
    local out=""
    while [[ $# -gt 0 ]]; do [[ $1 == --out ]] && out=$2; shift; done
    echo ok > "$out/loss_summary.csv"
    return "$FAKE_RC"
}
sleep() { :; }   # the 20 attempts without the 90 s waits
export -f fake_run sleep

fails=0
check() {   # label, run status, destination (ok | blocked), expected job status
    local label=$1 rc=$2 kind=$3 want=$4 d p got
    rm -rf "$work/tmp" "$work/out" "$work/blocked"; mkdir -p "$work/tmp" "$work/out"; : > "$work/blocked"
    if [[ $kind == ok ]]; then d="$work/out"; else d="$work/blocked/chk"; fi
    p=${payload//"$runner"/fake_run}
    p=${p//"$dest"/"$d"}
    TMPDIR="$work/tmp" FAKE_RC=$rc bash -c "$p" 2> "$work/err"; got=$?
    if [[ $got == "$want" ]]; then echo "ok   $label: status $got"; else echo "FAIL $label: status $got, expected $want"; fails=$((fails + 1)); fi
    if [[ $kind == ok && ! -s "$d/lag13_d12_s3_t116/loss_summary.csv" ]]; then echo "FAIL $label: run folder not copied"; fails=$((fails + 1)); fi
    if [[ $kind == blocked ]] && ! grep -q "failed 20 times" "$work/err"; then echo "FAIL $label: no message in stderr"; fails=$((fails + 1)); fi
}
check "run ok, copy ok" 0 ok 0
check "run failed (3), copy ok" 3 ok 3
check "run ok, copy fails" 0 blocked 75
check "run failed (3), copy fails" 3 blocked 3
[[ $fails == 0 ]] && echo "all 4 cases pass" || echo "$fails failure(s)"
exit $fails
