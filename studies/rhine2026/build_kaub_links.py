"""List the commercial links whose baseline route crosses the Kaub reach (edge named rhine_mainz_koblenz).

Input of validation_outputs.py. Replaces the 83 MB link_route_flags.csv of 14 Sep 2026, which lived in a temp
folder, was never committed and was lost (see mechanism_checks/README.md). Reads the routes cache of the scope,
tmp/<cache dir>/<scope>_logistic_routes.pkl, which carries the supply-chain network with every link's routes: the
cache the run used, named by --cache-dir NAME (tmp/NAME) or read from the run's log by --run FOLDER ("Named cache:"
or "Isolated cache:" line of <FOLDER>.log beside the folder, else of FOLDER/exp.log); neither: the default folder
tmp/. KI-49 (2 Nov 2026): until 3 Nov the builder read the default folder's cache whatever cache the run used, so
the lists of the per-class full runs (cache r6cal, containers on the river) were those of the 5 Oct routes.

Until 21 Sep 2026 a link could split its delivery over several routes (route_plan); since then
there is one route per link and both definitions coincide. Both are still counted:
  primary : the link's main route uses the Kaub edge
  any     : any route of its plan does
The list is written for --definition (default: any). The committed extractions are recorded in EXPECTED by cache
name: the default cache's of 17 Sep 2026 (additional_data/validation_outputs_2026_cal_base_full.csv, built on
5,746 links: 3,583 dry bulk, 2,124 liquid bulk, 39 container) and the later ones. --expect checks the chosen
definition against the counts recorded for the run's cache and refuses to write on a mismatch; a cache without
recorded counts (its first build) is written with a notice: add its counts to EXPECTED to make the check binding.

The list is specific to a supply-chain draw (seed) and to the route table of the build. Provenance is written
into the header of the output: cache file, its modification time, and the stage fingerprint if present.

Usage:
    python studies/rhine2026/build_kaub_links.py [--scope EU] [--cache-dir NAME | --run FOLDER] [--definition any|primary] [--expect] [--out FILE]
"""
from __future__ import annotations

import argparse
import datetime as dt
import pickle
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
KAUB_EDGE_NAME = "rhine_mainz_koblenz"
# counts of the committed extractions (definition any), by cache directory name; "" is the default folder tmp/
EXPECTED = {
    "": {"total": 5746, "dry_bulk": 3583, "liquid_bulk": 2124, "container": 39},     # 17 Sep 2026 (routes of 5 Oct)
    "r6cal": {"total": 8176, "dry_bulk": 3562, "liquid_bulk": 2160, "container": 2454},  # 3 Nov 2026 (round 6: containers on the river; 2026 and 2018 full runs alike)
}
CACHE_LINE = re.compile(r"(?:Named|Isolated) cache: (\S+)")


def cache_dir_of_run(run: Path) -> str:
    """The name of the cache directory a run used, from the first log that names one: the launcher's <run>.log
    beside the folder, else the model's exp.log inside it; '' (the default folder) when neither does."""
    for log in (run.parent / f"{run.name}.log", run / "exp.log"):
        if log.exists():
            m = CACHE_LINE.search(log.read_text(encoding="utf-8", errors="replace"))
            if m:
                return Path(m.group(1)).name
    return ""


def main(scope: str, definition: str, expect: bool, out: Path, cache_dir: str = "", run: Path | None = None):
    if run is not None:
        cache_dir = cache_dir_of_run(run)
        print(f"cache of the run {run.name}: {cache_dir or 'the default folder'}")
    cache = ROOT / "tmp" / cache_dir / f"{scope}_logistic_routes.pkl"
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
    known = EXPECTED.get(cache_dir)
    match = (got == known) if known else None
    label = cache_dir or "default"
    print(f"chosen '{definition}': {got} | committed extraction for cache '{label}': {known} | match: {match}")
    if expect and known and not match:
        raise SystemExit("counts differ from the committed extraction: nothing written")
    if expect and not known:
        print(f"no committed counts for cache '{label}' (its first build): written without the check; add the counts to EXPECTED")

    fp = blob.get("fingerprint")
    mtime = dt.datetime.fromtimestamp(cache.stat().st_mtime).isoformat(timespec="seconds")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# links whose baseline route crosses {KAUB_EDGE_NAME}; definition: {definition}\n")
        f.write(f"# built {dt.datetime.now().isoformat(timespec='seconds')} from {cache.relative_to(ROOT).as_posix()} (modified {mtime}); stage fingerprint: {str(fp)[:16] if fp else 'n/a'}\n")
        f.write(f"# counts {got}; committed extraction for cache '{label}': {known}; match: {match}\n")
        f.write("seller_id,buyer_id,cargo_type,n_routes\n")
        for r in sorted(chosen):
            f.write(",".join(map(str, r)) + "\n")
    print("written", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="EU")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--cache-dir", default="", help="name of the cache directory the run used (tmp/<name>); default: tmp/ itself")
    src.add_argument("--run", default=None, help="run folder: the cache directory is read from <folder>.log or <folder>/exp.log")
    ap.add_argument("--definition", choices=["any", "primary"], default="any")
    ap.add_argument("--expect", action="store_true", help="refuse to write unless the counts match the committed extraction of the run's cache")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    main(a.scope, a.definition, a.expect,
         Path(a.out) if a.out else ROOT / "studies" / "rhine2026" / "additional_data" / f"kaub_crossing_links_{a.scope}_seed42.csv",
         cache_dir=a.cache_dir, run=Path(a.run) if a.run else None)
