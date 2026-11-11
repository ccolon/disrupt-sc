#!/bin/bash
# Pack the batch of 11 November 2026 (written by the session of 11 Nov 2026, evening): one archive per job list, renamed, plus the compare tables
# Copy of the script run on the cluster as ~/claude_tmp/pack_20261111.sh; the checkout's pack_results.sh has OUTPUT_DIR set to the folder below.
set -e
cd /projects/disruptsc/disrupt-sc-rhine
OUT=/projects/disruptsc/runs/rhine2026_obs
pack() {
  ls $OUT | grep rhine_batch_ | sort > ~/claude_tmp/pack_before.txt || true
  bash studies/rhine2026/cluster/pack_results.sh --jobs studies/rhine2026/cluster/jobs_20261111_$1.txt --with-firms $2
  ls $OUT | grep rhine_batch_ | sort > ~/claude_tmp/pack_after.txt
  new=$(comm -13 ~/claude_tmp/pack_before.txt ~/claude_tmp/pack_after.txt)
  mv $OUT/$new $OUT/rhine_obs_20261111_$1.tgz
}
pack ref 2026_r6_bycargo,2026_r6_bycargo_deep20,2026_r6_bycargo_dfuel0,2026_r6_bycargo_fleet,2026_r6_bycargo_fleetwide,2026_r6_bycargo_rail50,2026_r6_bycargo_rail140,2026_r6_bycargo_serv45,2026_r6_bycargo_stock7,2026_r6_bycargo_tablelow,2026_r6_bycargo_tablehigh,2026_r6_bycargo_full,2018_r6_bycargo_inv075
pack paired 2026_r6_bycargo_seed1_base,2026_r6_bycargo_seed2_base,2026_r6_bycargo_seed3_base,2026_r6_bycargo_seed4_base,2026_r6_bycargo_seed5_base,2026_r6_bycargo_seed6_base,2026_r6_bycargo_seed7_base,2026_r6_bycargo_seed8_base,2026_r6_bycargo_seed9_base,2026_r6_bycargo_seed10_base
pack searate_b 2026_r6_bycargo_searate
cd $OUT
tar czf rhine_obs_20261111_tables.tgz compare_runs_batch_jobs_20261111_ref.csv compare_runs_batch_jobs_20261111_ref.txt compare_runs_batch_jobs_20261111_paired.csv compare_runs_batch_jobs_20261111_paired.txt compare_runs_batch_jobs_20261111_searate_b.csv compare_runs_batch_jobs_20261111_searate_b.txt
sha256sum rhine_obs_20261111_*.tgz > ~/claude_tmp/pack_20261111.sha256
ls -l rhine_obs_20261111_*.tgz >> ~/claude_tmp/pack_20261111.sha256
echo PACKDONE >> ~/claude_tmp/pack_20261111.sha256
