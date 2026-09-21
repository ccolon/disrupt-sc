#!/bin/bash
# Execution test of the quoting that launch_rhine_batch.sh hands to Slurm (21 Sep 2026).
# The launcher builds:  sbatch ... --wrap="bash -c '<exports> && <activate> && <payload>'"  and runs it through eval.
# This script reproduces that construction with stand-in commands and no sbatch, to check that ';' and '&&' inside
# the payload behave as written: a failing builder must skip the extraction and leave the rest untouched.
# It tests the bash mechanics only. It does not test sbatch, memory, paths or the python scripts on the cluster.
set -u
tmp=$(mktemp -d)
run_wrapped() {   # same nesting as submit(): eval of a double-quoted string holding bash -c '...'
    local payload=$1
    local cmd="bash -c 'export X=1 && cd ${tmp} && ${payload}'"
    eval "$cmd"
}
# case A: builder succeeds -> extraction runs
run_wrapped "echo analysis > a.txt 2>&1; echo figures > f.txt 2>&1; rm -f none.csv; true > b_ok.txt 2>&1 && echo extraction > v_ok.txt 2>&1"
# case B: builder fails -> extraction must NOT run, earlier steps must still have run
run_wrapped "echo analysis > a2.txt 2>&1; echo figures > f2.txt 2>&1; rm -f none.csv; false > b_fail.txt 2>&1 && echo extraction > v_fail.txt 2>&1"
pass=true
[[ -f ${tmp}/a.txt && -f ${tmp}/f.txt && -f ${tmp}/v_ok.txt ]]   || { echo "FAIL case A: extraction did not run after a successful builder"; pass=false; }
[[ -f ${tmp}/a2.txt && -f ${tmp}/f2.txt ]]                        || { echo "FAIL case B: earlier steps did not run"; pass=false; }
[[ ! -f ${tmp}/v_fail.txt ]]                                      || { echo "FAIL case B: extraction ran although the builder failed"; pass=false; }
$pass && echo "PASS: inside the wrapped command ';' sequences and '&&' short-circuits as written"
rm -rf "$tmp"
