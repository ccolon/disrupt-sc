#!/bin/bash
# Pack the final Rhine runs (r6_bycargo, 129 folders) to restore the local mirror C:/dsc_runs/rhine2026 (10 Nov 2026).
# Same per-run file list as studies/rhine2026/cluster/pack_results.sh; firm files only where the third argument is 1.
# Usage: bash rhine_restore_pack.sh <part> <file with one run name per line> <0|1>
OUT=/projects/disruptsc/runs/rhine2026
part="$1"; runs="$2"; firms="$3"
cd "$OUT" || exit 1
list=$(mktemp)
FILES="transport_edges_with_flows_0.geojson transport_nodes.geojson analysis.txt country_data.csv household_data.csv routing_summary.csv parameters.yaml run_fingerprint.json figures.log mrio_by_sector.csv mrio_by_region.csv mrio_by_country.csv validation_outputs.csv validation_outputs.txt kaub_links_check.csv kaub_links_check.txt link_flows_disrupted.csv.gz price_by_cargo.csv inventory_trace.csv extract_link_flows.txt"
FIRM="firm_data.csv firm_table.geojson household_table.geojson country_table.geojson transport_edges.geojson"
n=0
while read -r d; do
  if [ -z "$d" ]; then continue; fi
  if [ ! -d "$d" ]; then echo "MISSING $d"; continue; fi
  n=$((n+1))
  for f in $FILES; do if [ -f "$d/$f" ]; then echo "$d/$f" >> "$list"; fi; done
  if [ -d "$d/figures" ]; then find "$d/figures" -type f >> "$list"; fi
  if [ -f "$d.log" ]; then echo "$d.log" >> "$list"; fi
  if [ "$firms" = "1" ]; then for f in $FIRM; do if [ -f "$d/$f" ]; then echo "$d/$f" >> "$list"; fi; done; fi
done < "$runs"
sort -u "$list" -o "$list"
arc="rhine_restore_20261110_$part.tgz"
tar czf "$arc.partial" -T "$list"
status=$?
cp "$list" "$HOME/claude_tmp/rhine_restore_20261110_$part.files.txt"
rm -f "$list"
if [ $status -ne 0 ]; then echo "TAR FAILED $part status=$status"; exit $status; fi
mv "$arc.partial" "$arc"
echo "DONE $part runs=$n files=$(wc -l < $HOME/claude_tmp/rhine_restore_20261110_$part.files.txt) bytes=$(stat -c %s $arc) sha256=$(sha256sum $arc | cut -d' ' -f1)"
