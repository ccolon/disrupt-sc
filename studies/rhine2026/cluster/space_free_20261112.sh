#!/bin/bash
# Free space on /projects/disruptsc: the tiers of the assessment of 12 November 2026 (studies/rhine2026/cluster/cluster_space_20261112.md).
# Usage:  bash space_free_20261112.sh TIER [TIER ...]          prints the number of items and the size of each tier (nothing is deleted)
#         bash space_free_20261112.sh --run TIER [TIER ...]    deletes, and logs each item to ~/claude_tmp/space_free_20261112.log
# Tiers:  leftovers pidcaches conda old2026 reissue rhinecaches archives11 flows
set -u
P=/projects/disruptsc; R=$P/runs/rhine2026; O=$P/runs/rhine2026_obs; W=$P/disrupt-sc-rhine/tmp; M=$P/disrupt-sc/tmp
LOG=~/claude_tmp/space_free_20261112.log; RUN=0; TOTAL=0
[ "${1:-}" = "--run" ] && { RUN=1; shift; }
size() { if [ -d "$1" ]; then getfattr --only-values -n ceph.dir.rbytes "$1" 2>/dev/null; else stat -c %s "$1" 2>/dev/null; fi; }
item() {   # one path: checked, sized, listed or deleted
  local p="$1"
  case "$p" in $P/runs/rhine2026/*|$P/runs/rhine2026_obs/*|$P/disrupt-sc-rhine/tmp/*|$P/disrupt-sc/tmp/*) ;; *) echo "REFUSED (outside the assessed folders): $p"; return;; esac
  [ -e "$p" ] || return 0
  [ -L "$p" ] && { echo "REFUSED (a link): $p"; return; }
  local b; b=$(size "$p"); b=${b:-0}; TIER_B=$((TIER_B + b)); TIER_N=$((TIER_N + 1))
  if [ $RUN -eq 1 ]; then rm -rf --one-file-system -- "$p" && echo "$(date -u +%FT%T) deleted $b $p" >> $LOG; fi
}
names() {  # the run folders of a family in runs/rhine2026, checked against the list assessed on 12 November
  local got; got=$(cd $R && ls -d $1 2>/dev/null | tr -d / | LC_ALL=C sort)
  if [ "$(echo "$got" | sha1sum | cut -c1-40)" != "$2" ]; then echo "REFUSED: the folders matching [$1] are not the set assessed on 12 November" >&2; return 1; fi
  echo "$got"
}
for T in "$@"; do
  TIER_B=0; TIER_N=0
  case "$T" in
    leftovers)
      item $O/_lean_20261111; item $O/rhine_obs_20261111_lean.txz
      for d in $W/EU_pid_*; do item "$d"; done
      item $O/2026_r6_bycargo_profile0930; item $O/2026_r6_bycargo_profile0930.log; item $O/cachebuild_r6cal_base; item $O/cachebuild_r6cal_base.log
      item $M/EU_logistic_routes_preKI37.pkl ;;
    pidcaches)
      if squeue -u colon -h -o "%j" | grep -qv "^cam_"; then echo "REFUSED: a job other than the Cambodia ones is running"; continue; fi
      if [ -n "$(find $M -maxdepth 1 -name "*_pid_*" -newermt "$(date -u -d "7 days ago" +%F)" | head -1)" ]; then echo "REFUSED: a per-process cache was written in the last 7 days"; continue; fi
      for d in $M/EcuadorEQ_pid_* $M/Ecuador_pid_* $M/Armenia_pid_* $M/ECA_pid_*; do item "$d"; done ;;
    conda)
      if [ $RUN -eq 1 ]; then conda clean --all -y; else conda clean --all --dry-run 2>&1 | grep -i "will remove"; fi; continue ;;
    old2026)
      L=$(names "2026_r6_bycargo*/ wave_r6_bycargo*/" df6ad732d4f1f92d92a22632c90a1e650c222a02) || continue
      for n in $L; do case "$n" in *_q25|*_q75) ;; *) [ -f $O/$n/analysis.txt ] || { echo "REFUSED: $n has no rerun in rhine2026_obs"; continue 2; };; esac; done
      for n in $L; do item $R/$n; item $R/$n.log; done
      [ -f $O/2018_r6_bycargo_inv075/analysis.txt ] && { item $R/2018_r6_bycargo_inv075; item $R/2018_r6_bycargo_inv075.log; } ;;
    reissue)
      L=$(names "*_s07*/ wave07*/ *_rev_*/ wave09*/" bca511123f8b59f1f8228a2135cdfb24abf52cf0) || continue
      for n in $L; do item $R/$n; item $R/$n.log; done ;;
    rhinecaches)
      if squeue -u colon -h -o "%j" | grep -q "r6_bycargo"; then echo "REFUSED: a Rhine job is running"; continue; fi
      for i in 1 2 3 4 5 6 7 8 9 10; do item $W/r6bc_seed$i; done; item $W/r6sea; item $M/r6cal ;;
    archives11)
      for a in ref paired searate_b tables; do item $O/rhine_obs_20261111_$a.tgz; done ;;
    flows)
      for d in $O/*/; do n=$(basename $d); case "$n" in 2026_r6_bycargo|2026_r6_bycargo_full|2026_r6_bycargo_searate|searate_flows_base) continue;; esac; item $d/transport_edges_with_flows_0.geojson; item $d/transport_edges_with_flows_1.geojson; done ;;
    *) echo "unknown tier $T"; continue ;;
  esac
  echo "$T: $TIER_N items, $(awk -v b=$TIER_B "BEGIN {printf \"%.1f\", b/1e9}") GB $([ $RUN -eq 1 ] && echo deleted || echo "would be deleted")"
  TOTAL=$((TOTAL + TIER_B))
done
echo "total: $(awk -v b=$TOTAL "BEGIN {printf \"%.1f\", b/1e9}") GB; used now $(getfattr --only-values -n ceph.dir.rbytes $P 2>/dev/null | awk "{printf \"%.1f\", \$1/1e9}") of 1000.0 GB"
