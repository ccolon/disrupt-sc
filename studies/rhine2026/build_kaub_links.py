"""List the commercial links whose baseline route crosses the Kaub reach (edge named rhine_mainz_koblenz).

Input of validation_outputs.py. Replaces the 83 MB link_route_flags.csv of 14 Sep 2026, which lived in a temp
folder, was never committed and was lost (see mechanism_checks/README.md). Reads the routes cache of the scope
(tmp/<scope>_logistic_routes.pkl), which carries the supply-chain network with every link's routes.

Until 21 Sep 2026 a link could split its delivery over several routes (route_plan); since then
there is one route per link and both definitions coincide. Both are still counted:
  primary : the link's main route uses the Kaub edge
  any     : any route of its plan does
The list is written for --definition (default: any). The committed extraction of 17 Sep
(additional_data/validation_outputs_2026_cal_base_full.csv) was built on 5,746 links: 3,583 dry bulk, 2,124 liquid
bulk, 39 container. --expect checks the chosen definition against those counts and refuses to write on a mismatch.

The list is specific to a supply-chain draw (seed) and to the route table of the build. Provenance is written
into the header of the output: cache file, its modification time, and the stage fingerprint if present.

Usage:
    python studies/rhine2026/build_kaub_links.py [--scope EU] [--definition any|primary] [--expect]
"""
from __future__ import annotations

import argparse
import datetime as dt
import pickle
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
KAUB_EDGE_NAME = "rhine_mainz_koblenz"
EXPECTED = {"total": 5746, "dry_bulk": 3583, "liquid_bulk": 2124, "container": 39}


def main(scope: str, definition: str, expect: bool, out: Path):
    cache = ROOT / "tmp" / f"{scope}_logistic_routes.pkl"
    with open(cache, "rb") as f:
        blob = pickle.load(f)
    data = blob["data"]
    tn, g = data["transport_network"], data["sc_network"]
    kaub = {frozenset((u, v)) for u, v, e in tn.edges(data=True) if e.get("name") == KAUB_EDGE_NAME}
    if not kaub:
        raise SystemExit(f"no edge named {KAUB_EDGE_NAME} in the network")
    print(f"Kaub edge(s): {[tuple(k) for k in kaub]}")

    def crosses(route) -> bool:
        if route is None:
            return False
        return any(frozenset(e) in kaub for e in route.transport_edges)

    rows = {"primary": [], "any": []}
    n_links = n_routed = 0
    for u, v, d in g.edges(data=True):
        link = d["object"]
        n_links += 1
        # one route per link since 21 Sep 2026 (multi-route plans retired); the
        # "any" table keeps its column for the archived 2026 extraction
        routes = [link.route] if link.route is not None else []
        if not routes:
            continue
        n_routed += 1
        rec = (str(getattr(u, "pid", u)), str(getattr(v, "pid", v)), link.cargo_type, len(routes))
        if crosses(link.route):
            rows["primary"].append(rec)
        if any(crosses(r) for r in routes):
            rows["any"].append(rec)
    print(f"{n_links:,} links, {n_routed:,} routed")
    for k, rr in rows.items():
        c = Counter(r[2] for r in rr)
        print(f"  definition '{k}': {len(rr):,} links cross Kaub {dict(c)}; multi-route among them: {sum(1 for r in rr if r[3] > 1):,}")

    chosen = rows[definition]
    counts = Counter(r[2] for r in chosen)
    got = {"total": len(chosen), **{k: counts.get(k, 0) for k in ("dry_bulk", "liquid_bulk", "container")}}
    match = got == EXPECTED
    print(f"chosen '{definition}': {got} | committed extraction: {EXPECTED} | match: {match}")
    if expect and not match:
        raise SystemExit("counts differ from the committed extraction: nothing written")

    fp = blob.get("fingerprint")
    mtime = dt.datetime.fromtimestamp(cache.stat().st_mtime).isoformat(timespec="seconds")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# links whose baseline route crosses {KAUB_EDGE_NAME}; definition: {definition}\n")
        f.write(f"# built {dt.datetime.now().isoformat(timespec='seconds')} from {cache.name} (modified {mtime}); stage fingerprint: {str(fp)[:16] if fp else 'n/a'}\n")
        f.write(f"# counts {got}; matches the extraction of 17 Sep 2026: {match}\n")
        f.write("seller_id,buyer_id,cargo_type,n_routes\n")
        for r in sorted(chosen):
            f.write(",".join(map(str, r)) + "\n")
    print("written", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="EU")
    ap.add_argument("--definition", choices=["any", "primary"], default="any")
    ap.add_argument("--expect", action="store_true", help="refuse to write unless the counts match the committed extraction")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    main(a.scope, a.definition, a.expect,
         Path(a.out) if a.out else ROOT / "studies" / "rhine2026" / "additional_data" / f"kaub_crossing_links_{a.scope}_seed42.csv")
