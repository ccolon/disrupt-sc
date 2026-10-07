# -*- coding: utf-8 -*-
"""Generate the Tier-1 criticality chunk configs for the Romania sweep.

Design (manifest p29, user decisions 7 Oct 2026: duration 1, tier-2 top 150):
  * Edge set: domestic (foreign != 1) roads / railways / waterways with
    baseline flow > 1 t/wk in the reference run - closing a zero-flow edge
    provably causes zero loss, so the rest are skipped exactly (the model's
    skip_zero_flow would drop them anyway; filtering here keeps chunks even).
  * Edges are sorted by baseline flow and dealt round-robin into N chunks so
    every task gets a similar mix of heavy (slow) and light (fast) edges.
  * One YAML per chunk, injected per task through DISRUPT_SC_EXTRA_CONFIG:
      simulation_type: criticality, export_files: False,
      criticality: {duration: 1, attribute: id, edges: [...],
                    run_id: t1_chunk_NN}
    -> results in output/Romania/criticality/t1_chunk_NN/ (resume-safe).
  * Edge ids are the MODEL ids (mode offsets included), read from the
    reference run's flow export - the cluster must run on the same data
    state (the fingerprint sidecar enforces it).

Usage: python studies/criticality_ro/make_chunks.py [--ref RUN_ID] [--n 40]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REF_DEFAULT = "20260928_142628"   # v21 baseline (manifest p28)
MIN_FLOW_T = 1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=REF_DEFAULT)
    ap.add_argument("--n", type=int, default=40)
    args = ap.parse_args()

    exp = REPO / "output" / "Romania" / args.ref / "transport_edges_with_flows_0.geojson"
    e = gpd.read_file(exp)
    dom = e[(e["foreign"].fillna(0) != 1)
            & e["type"].isin(["roads", "railways", "waterways"])].copy()
    dom["flow"] = dom["flow_total_tons"].fillna(0.0)
    sel = dom[dom["flow"] > MIN_FLOW_T].sort_values("flow", ascending=False)
    print(f"reference {args.ref}: {len(dom)} domestic edges, "
          f"{len(sel)} with flow > {MIN_FLOW_T} t/wk "
          f"({sel.groupby('type').size().to_dict()})")

    chunks: list[list[int]] = [[] for _ in range(args.n)]
    for k, eid in enumerate(sel["id"].astype(int)):
        chunks[k % args.n].append(eid)

    out = HERE / "chunks"
    out.mkdir(exist_ok=True)
    for old in out.glob("t1_chunk_*.yaml"):
        old.unlink()
    for k, ids in enumerate(chunks):
        name = f"t1_chunk_{k:02d}"
        with open(out / f"{name}.yaml", "w") as f:
            f.write("simulation_type: criticality\n")
            f.write("export_files: False\n")
            # CRITICAL: the scope config's t_final takes precedence over the
            # criticality default duration+2 - without this line each edge
            # simulates the full disruption horizon (smoke test: ~14 steps,
            # 32 min/edge instead of ~10)
            f.write("t_final: 3\n")
            f.write("criticality:\n")
            f.write("  duration: 1\n")
            f.write(f"  run_id: {name}\n")
            f.write("  attribute: id\n")
            f.write("  edges: [" + ", ".join(str(i) for i in ids) + "]\n")
    sizes = [len(c) for c in chunks]
    print(f"wrote {args.n} chunk configs to {out} "
          f"({min(sizes)}-{max(sizes)} edges each)")
    (out / "REFERENCE_RUN.txt").write_text(args.ref + "\n")
    return 0


if __name__ == "__main__":
    main()
