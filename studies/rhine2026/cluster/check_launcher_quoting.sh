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
# case C (1 Nov 2026): the run payload with the log on the node's local disk: a background copier, the run inside
# if/else, a final copy with retries, the run's own exit status returned to Slurm. The copier is bounded here
# (on the cluster the end of the job kills it); a stand-in run writes its log and succeeds or fails.
copy1="for i in 1 2 3; do cp -f ${tmp}/local1.log ${tmp}/out1.log 2>/dev/null && break; sleep 1; done"
copy2="for i in 1 2 3; do cp -f ${tmp}/local2.log ${tmp}/out2.log 2>/dev/null && break; sleep 1; done"
run_wrapped "( for n in 1 2; do sleep 1; cp -f ${tmp}/local1.log ${tmp}/out1.log 2>/dev/null; done ) & if echo run-ok > ${tmp}/local1.log 2>&1; then ${copy1}; true; else ${copy1}; false; fi"
rc_ok=$?
run_wrapped "( for n in 1 2; do sleep 1; cp -f ${tmp}/local2.log ${tmp}/out2.log 2>/dev/null; done ) & if { echo run-fail > ${tmp}/local2.log 2>&1; false; }; then ${copy2}; true; else ${copy2}; false; fi"
rc_fail=$?
sleep 3   # let the bounded copiers finish before the directory goes
pass=true
[[ -f ${tmp}/a.txt && -f ${tmp}/f.txt && -f ${tmp}/v_ok.txt ]]   || { echo "FAIL case A: extraction did not run after a successful builder"; pass=false; }
[[ -f ${tmp}/a2.txt && -f ${tmp}/f2.txt ]]                        || { echo "FAIL case B: earlier steps did not run"; pass=false; }
[[ ! -f ${tmp}/v_fail.txt ]]                                      || { echo "FAIL case B: extraction ran although the builder failed"; pass=false; }
[[ $rc_ok -eq 0 && -f ${tmp}/out1.log && "$(cat "${tmp}/out1.log")" == run-ok ]] || { echo "FAIL case C: a successful run did not return 0 with its log copied"; pass=false; }
[[ $rc_fail -ne 0 && -f ${tmp}/out2.log && "$(cat "${tmp}/out2.log")" == run-fail ]] || { echo "FAIL case C: a failing run did not return non-zero with its log copied"; pass=false; }
$pass && echo "PASS: inside the wrapped command ';' sequences and '&&' short-circuits as written; the local-log payload returns the run's status with the log copied"
rm -rf "$tmp"
