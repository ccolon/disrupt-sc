r"""Extract a restore archive of Rhine runs into the local mirror of the run folders (written 10 Nov 2026, when the
folders of the final batch had gone from C:/dsc_runs/rhine2026 and were packed again on the cluster by
restore_pack.sh).

    python -I restore_extract.py <archive.tgz> <sha256 of the archive on the cluster> <runs file> [--target DIR] [--dry-run]

The archive is read as data, never trusted: its sha256 must equal the one computed on the cluster; only regular files
are taken, under <run>/ or as <run>.log, for the runs named in <runs file> (one name per line), with a known data
extension; absolute paths, '..', links and anything else are listed and left out. Nothing that exists is overwritten:
an existing file of the same size is counted as already there, one of another size is reported. Modification times
are those of the cluster. Run it with -I and keep the archive in a folder of its own.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tarfile
from pathlib import Path, PurePosixPath

TARGET = Path("C:/dsc_runs/rhine2026")
OK_EXT = {".csv", ".geojson", ".txt", ".yaml", ".json", ".log", ".png", ".pdf", ".gz", ".svg"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("sha256")
    ap.add_argument("runs")
    ap.add_argument("--target", default=str(TARGET))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--flows-for", default=None,
                    help="comma-separated run names: transport_edges_with_flows_0.geojson (30 MB a run) is taken for these "
                         "runs only; the readers use the one of the reference run or of the link-level run")
    a = ap.parse_args()
    arc, target = Path(a.archive), Path(a.target)
    runs = {line.strip() for line in Path(a.runs).read_text(encoding="utf-8").splitlines() if line.strip()}
    got = sha256(arc)
    if got != a.sha256.lower():
        print(f"{arc.name}: sha256 {got} is not the cluster's {a.sha256}: nothing extracted")
        return 2
    flows_for = None if a.flows_for is None else {r.strip() for r in a.flows_for.split(",") if r.strip()}
    written = same = skipped = 0
    nbytes = 0
    left_out, differ, seen_runs = [], [], set()
    with tarfile.open(arc, "r:gz") as t:
        for m in t:
            p = PurePosixPath(m.name)
            if m.isdir():
                continue
            if not m.isfile() or p.is_absolute() or ".." in p.parts or not p.parts:
                left_out.append(m.name)
                continue
            top = p.parts[0]
            is_log = len(p.parts) == 1 and top.endswith(".log")
            run = top[:-4] if is_log else top
            if run not in runs or (len(p.parts) == 1 and not is_log) or p.suffix.lower() not in OK_EXT:
                left_out.append(m.name)
                continue
            seen_runs.add(run)
            if flows_for is not None and p.name == "transport_edges_with_flows_0.geojson" and run not in flows_for:
                skipped += 1
                continue
            dest = target.joinpath(*p.parts)
            if dest.exists():
                if dest.stat().st_size == m.size:
                    same += 1
                else:
                    differ.append(f"{m.name}: {dest.stat().st_size} bytes on disk, {m.size} in the archive")
                continue
            nbytes += m.size
            written += 1
            if a.dry_run:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            src = t.extractfile(m)
            tmp = dest.with_name(dest.name + ".part")
            with open(tmp, "wb") as out:
                shutil.copyfileobj(src, out, 1 << 22)
            if tmp.stat().st_size != m.size:
                print(f"{m.name}: {tmp.stat().st_size} bytes written, {m.size} expected: stopped")
                return 3
            os.replace(tmp, dest)
            os.utime(dest, (m.mtime, m.mtime))
    verb = "would be written" if a.dry_run else "written"
    print(f"{arc.name}: sha256 ok; {written} files {verb} ({nbytes / 1e6:.0f} MB), {same} already there with the same size, "
          f"{len(differ)} existing with another size, {len(left_out)} left out; runs {len(seen_runs)} of {len(runs)} named"
          + (f"; {skipped} baseline flow files not taken (--flows-for)" if flows_for is not None else ""))
    for x in differ[:20]:
        print("  DIFFERS " + x)
    for x in left_out[:20]:
        print("  LEFT OUT " + x)
    missing = sorted(runs - seen_runs)
    if missing:
        print("  runs named but not in the archive: " + ", ".join(missing))
    return 1 if (differ or left_out or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
