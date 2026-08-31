"""Find, download, and merge Geofabrik OSM PBF extracts for a set of countries.

Usage:
    python geofabrik.py list --iso3 KAZ,KGZ,UZB          # show matching extracts + sizes
    python geofabrik.py download --iso3 KAZ --out <dir>  # download country PBF(s)
    python geofabrik.py download --url <pbf-url> --out <dir>
    python geofabrik.py merge --inputs a.pbf,b.pbf --out merged.pbf   # needs osmium on PATH

The agent must ask the user before downloading (state filename, source, size).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso_codes import iso3_to_iso2  # noqa: E402

INDEX_URL = "https://download.geofabrik.de/index-v1-nogeom.json"
UA = {"User-Agent": "disruptsc-new-scope/1.0"}


def _fetch_index() -> list[dict]:
    req = urllib.request.Request(INDEX_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data.get("features", [])


def _matches_for_iso3(features: list[dict], iso3: str) -> list[dict]:
    iso2 = iso3_to_iso2(iso3)
    out = []
    for feat in features:
        props = feat.get("properties", {})
        alpha2 = props.get("iso3166-1:alpha2") or []
        if iso2 and iso2 in alpha2:
            out.append(props)
    return out


def _head_size(url: str) -> str:
    try:
        req = urllib.request.Request(url, method="HEAD", headers=UA)
        with urllib.request.urlopen(req, timeout=30) as resp:
            n = int(resp.headers.get("Content-Length", 0))
        return f"{n / 1e6:,.0f} MB" if n else "size unknown"
    except Exception:
        return "size unknown"


def cmd_list(args) -> int:
    features = _fetch_index()
    for iso3 in [c.strip().upper() for c in args.iso3.split(",") if c.strip()]:
        matches = _matches_for_iso3(features, iso3)
        if not matches:
            print(f"{iso3}: no Geofabrik extract found (check the country manually on download.geofabrik.de)")
            continue
        for props in matches:
            url = (props.get("urls") or {}).get("pbf", "?")
            print(f"{iso3}: {props.get('id')}  (parent: {props.get('parent', '-')})")
            print(f"      {url}  [{_head_size(url)}]")
    return 0


def _download(url: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, url.rsplit("/", 1)[-1])
    print(f"Downloading {url} -> {dest}")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        total = int(resp.headers.get("Content-Length", 0))
        done = 0
        while True:
            chunk = resp.read(1 << 22)  # 4 MB
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if total and done % (1 << 26) < (1 << 22):  # ~every 64 MB
                print(f"  {done / 1e6:,.0f} / {total / 1e6:,.0f} MB")
    print(f"Done: {dest} ({os.path.getsize(dest) / 1e6:,.0f} MB)")
    return dest


def cmd_download(args) -> int:
    urls = []
    if args.url:
        urls.append(args.url)
    if args.iso3:
        features = _fetch_index()
        for iso3 in [c.strip().upper() for c in args.iso3.split(",") if c.strip()]:
            matches = _matches_for_iso3(features, iso3)
            if not matches:
                print(f"ERROR: no Geofabrik extract for {iso3}", file=sys.stderr)
                return 1
            # prefer the smallest-scope match (a country, not its continent)
            props = sorted(matches, key=lambda p: 0 if p.get("parent") else 1)[0]
            urls.append(props["urls"]["pbf"])
    if not urls:
        print("ERROR: provide --iso3 or --url", file=sys.stderr)
        return 1
    for url in urls:
        _download(url, args.out)
    return 0


def cmd_merge(args) -> int:
    if not shutil.which("osmium"):
        print("ERROR: osmium not found on PATH (conda install -c conda-forge osmium-tool)", file=sys.stderr)
        return 1
    inputs = [p.strip() for p in args.inputs.split(",") if p.strip()]
    for p in inputs:
        if not os.path.exists(p):
            print(f"ERROR: missing input {p}", file=sys.stderr)
            return 1
    cmd = ["osmium", "merge", *inputs, "-o", args.out, "--overwrite"]
    print(" ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="show extract URLs + sizes for countries")
    p.add_argument("--iso3", required=True)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("download", help="download PBF(s)")
    p.add_argument("--iso3")
    p.add_argument("--url")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_download)

    p = sub.add_parser("merge", help="merge PBFs with osmium")
    p.add_argument("--inputs", required=True, help="comma-separated PBF paths")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_merge)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
