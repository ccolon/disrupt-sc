"""Citation gate: every reference must exist and its metadata must match what we say it is.

    python studies/paper_pipeline/scripts/cite_check.py <refs.yaml | file.bib> [--out report.md] [--workers 4]

refs.yaml: a list (or {refs: [...]}) of entries with key, doi, title, first_author, year.
.bib: parsed with a small BibTeX reader (title, author, year, doi).

For an entry with a DOI: Crossref (then DataCite for Zenodo and other data/software DOIs, then OpenAlex) metadata;
title similarity, year (+-1) and first author's family name are compared. Without a DOI: a Crossref bibliographic search proposes the best match. Status per entry:
  ok         DOI resolves and title/year/author agree
  mismatch   DOI resolves to a different work (or year/author disagree): the reference is wrong
  not_found  DOI does not resolve anywhere
  found_doi  no DOI given; a confident match exists (DOI proposed)
  unverified no DOI and no confident match
  excepted   a mismatch listed in cite_exceptions.yaml ({key, why}) after a person or agent checked it
Exit 1 if any mismatch or not_found. Responses are cached in .cite_cache.json next to the input.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import difflib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

UA = {"User-Agent": "paper-pipeline-citecheck/0.1"}
TITLE_OK = 0.90


# ------------------------------------------------------------------ text helpers
def norm(s: str) -> str:
    s = html.unescape(html.unescape(s or ""))         # Crossref titles carry &amp;quot; etc.
    s = re.sub(r"<[^>]+>", " ", s)                    # JATS/HTML tags in titles
    s = re.sub(r"\\[\"'`^~=.]\s*\{?\\([ij])\}?", r"\1", s)   # accents on dotless i/j: {\'\i}, \'\j
    s = re.sub(r"\\[\"'`^~=.]\s*\{?([a-zA-Z])\}?", r"\1", s)   # LaTeX accents: \"u, \'{e}
    s = re.sub(r"\\[cvuHkr]\s*\{([a-zA-Z])\}", r"\1", s)        # \c{c}, \v{s}
    s = re.sub(r"\\(ss|ae|oe|aa|o|l)(?![a-zA-Z])", r"\1", s)    # \ss, \o, \l
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)            # other LaTeX commands
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    r = difflib.SequenceMatcher(None, a, b).ratio()
    # subtitle/prefix tolerance: one title contains the other ("Review article: ...", dropped subtitles)
    short, long_ = sorted((a, b), key=len)
    if len(short) >= 25 and short in long_:
        r = max(r, 0.95)
    return r


def family(author: str) -> str:
    """First author's family name from 'Last, First and ...' or 'First Last and ...' or 'Last'."""
    a = re.split(r"\s+and\s+", author or "", maxsplit=1)[0].strip()
    a = a.replace("{", "").replace("}", "")
    if "," in a:
        fam = a.split(",")[0]
    else:
        parts = a.split()
        fam = parts[-1] if parts else ""
    return norm(fam)


# ------------------------------------------------------------------ inputs
def parse_bib(text: str) -> list[dict]:
    out = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[m.end():i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            j = fm.end()
            if j >= len(body):
                continue
            if body[j] == "{":
                d, k = 1, j + 1
                while k < len(body) and d:
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                val = body[j + 1:k - 1]
            elif body[j] == '"':
                k = body.find('"', j + 1)
                val = body[j + 1:k]
            else:
                val = re.match(r"[^,\n]*", body[j:]).group(0)
            fields.setdefault(fm.group(1).lower(), val.strip())
        doi = fields.get("doi", "")
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I).strip()
        out.append({"key": m.group(2), "type": m.group(1).lower(), "title": fields.get("title", ""),
                    "first_author": family(fields.get("author", "")), "year": fields.get("year", ""),
                    "doi": doi, "url": fields.get("url", "")})
    return out


def load_refs(path: Path) -> list[dict]:
    if path.suffix.lower() == ".bib":
        return parse_bib(path.read_text(encoding="utf-8", errors="replace"))
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if isinstance(data, dict):
        data = data.get("refs") or data.get("references") or []
    out = []
    for e in data:
        doi = str(e.get("doi") or "").strip()
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
        out.append({"key": e.get("key", ""), "title": e.get("title", ""),
                    "first_author": family(str(e.get("first_author") or e.get("author") or "")),
                    "year": str(e.get("year") or ""), "doi": doi, "url": e.get("url", "")})
    return out


# ------------------------------------------------------------------ lookups
class Cache:
    def __init__(self, path: Path):
        self.path = path
        self.d = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def get(self, url: str):
        if url in self.d:
            return self.d[url]
        val = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=25) as r:
                    val = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    val = {"_status": 404}
                    break
                time.sleep(1.5 * (attempt + 1))
            except Exception:
                time.sleep(1.5 * (attempt + 1))
        if val is not None:
            self.d[url] = val
        return val

    def save(self):
        self.path.write_text(json.dumps(self.d), encoding="utf-8")


def crossref_meta(msg: dict) -> dict:
    t = (msg.get("title") or [""])[0]
    sub = (msg.get("subtitle") or [""])
    if sub and sub[0]:
        t = f"{t}: {sub[0]}"
    years = []
    for k in ("published-print", "published-online", "issued", "published", "created"):
        dp = (msg.get(k) or {}).get("date-parts") or [[None]]
        if dp[0] and dp[0][0]:
            years.append(int(dp[0][0]))
    au = msg.get("author") or []
    fam = norm(au[0].get("family", "") or au[0].get("name", "")) if au else ""
    names = " ".join(norm(f"{x.get('given', '')} {x.get('family', '')} {x.get('name', '')}") for x in au[:3])
    return {"title": t, "year": years[0] if years else None, "years": sorted(set(years)), "family": fam,
            "names": names, "venue": (msg.get("container-title") or [""])[0], "doi": msg.get("DOI", "")}


def openalex_meta(w: dict) -> dict:
    au = w.get("authorships") or []
    fam = ""
    if au:
        name = (au[0].get("author") or {}).get("display_name", "")
        fam = norm(name.split()[-1]) if name else ""
    names = " ".join(norm((x.get("author") or {}).get("display_name", "")) for x in au[:3])
    y = w.get("publication_year")
    return {"title": w.get("title") or "", "year": y, "years": [y] if y else [], "family": fam, "names": names,
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
            "doi": (w.get("doi") or "").replace("https://doi.org/", "")}


def datacite_meta(a: dict) -> dict:
    t = ((a.get("titles") or [{}])[0]).get("title", "")
    y = a.get("publicationYear")
    au = a.get("creators") or []
    fam = norm(au[0].get("familyName") or au[0].get("name", "")) if au else ""
    names = " ".join(norm(f"{x.get('givenName', '')} {x.get('familyName', '')} {x.get('name', '')}") for x in au[:3])
    return {"title": t, "year": y, "years": [y] if y else [], "family": fam, "names": names,
            "venue": a.get("publisher", ""), "doi": a.get("doi", "")}


def lookup_doi(cache: Cache, doi: str) -> dict | None:
    j = cache.get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    if j and j.get("message"):
        return crossref_meta(j["message"])
    j = cache.get("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/"))
    if j and (j.get("data") or {}).get("attributes"):
        return datacite_meta(j["data"]["attributes"])
    j = cache.get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/"))
    if j and j.get("id"):
        return openalex_meta(j)
    return None


def search(cache: Cache, e: dict) -> tuple[dict | None, float]:
    q = " ".join(x for x in (e.get("title"), e.get("first_author"), str(e.get("year") or "")) if x)
    if not q.strip():
        return None, 0.0
    j = cache.get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q))
    best, bs = None, 0.0
    for it in ((j or {}).get("message") or {}).get("items") or []:
        m = crossref_meta(it)
        s = title_sim(e.get("title", ""), m["title"])
        if s > bs:
            best, bs = m, s
    return best, bs


def judge(e: dict, m: dict) -> list[str]:
    probs = []
    s = title_sim(e.get("title", ""), m["title"])
    if e.get("title") and s < TITLE_OK:
        probs.append(f"title {s:.2f}: '{m['title'][:90]}'")
    try:
        ys = m.get("years") or ([m["year"]] if m.get("year") else [])
        # online-first vs print: accept the entry's year if it is within 1 of any recorded date
        if e.get("year") and ys and min(abs(int(str(e["year"])[:4]) - y) for y in ys) > 1:
            probs.append(f"year {e['year']} vs {'/'.join(map(str, ys))}")
    except ValueError:
        pass
    fa = e.get("first_author") or ""
    names = m.get("names") or m.get("family") or ""
    # family names are matched against the first three authors' full names (given/family splits vary)
    flat = names.replace(" ", "")
    if fa and names and fa not in names.split() and not (len(fa) >= 4 and fa.replace(" ", "") in flat):
        probs.append(f"first author {fa} vs {m.get('family')}")
    return probs


def check_one(cache: Cache, e: dict) -> dict:
    r = {"key": e.get("key"), "doi": e.get("doi"), "title": e.get("title", "")}
    if e.get("doi"):
        m = lookup_doi(cache, e["doi"])
        if m is None:
            r["status"], r["note"] = "not_found", "DOI resolves in none of Crossref, DataCite and OpenAlex"
            return r
        probs = judge(e, m)
        r["status"] = "mismatch" if probs else "ok"
        r["note"] = "; ".join(probs)
        r["found"] = m
        return r
    m, s = search(cache, e)
    if m and s >= TITLE_OK:
        r["status"], r["note"], r["found"] = "found_doi", f"proposed DOI {m['doi']} (title {s:.2f})", m
    else:
        r["status"] = "unverified"
        r["note"] = "no DOI; " + (f"best match {s:.2f}: '{m['title'][:80]}'" if m else "no match")
        if e.get("url"):
            r["note"] += f"; url {e['url']}"
    return r


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("refs")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--exceptions", help="YAML list of {key, why}; default cite_exceptions.yaml next to the input")
    a = ap.parse_args()
    path = Path(a.refs)
    refs = load_refs(path)
    cache = Cache(path.parent / ".cite_cache.json")
    with cf.ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda e: check_one(cache, e), refs))
    cache.save()
    # verified exceptions (Crossref metadata errors, print vs online years): {key, why} checked by a person/agent
    exc_path = Path(a.exceptions) if a.exceptions else path.parent / "cite_exceptions.yaml"
    exc = {}
    if exc_path.exists():
        exc = {e["key"]: e.get("why", "") for e in (yaml.safe_load(exc_path.read_text(encoding="utf-8")) or [])}
    for r in res:
        if r["status"] == "mismatch" and r["key"] in exc:
            r["status"], r["note"] = "excepted", f"{r['note']} - verified: {exc[r['key']]}"
    order = ["not_found", "mismatch", "unverified", "found_doi", "excepted", "ok"]
    counts = {k: sum(1 for r in res if r["status"] == k) for k in order}
    fail = counts["not_found"] + counts["mismatch"]
    lines = [f"# Citation gate: {path.name}", "",
             f"{len(res)} references: " + ", ".join(f"{counts[k]} {k}" for k in order if counts[k]),
             f"Result: {'FAIL' if fail else 'PASS'} ({fail} wrong or unresolvable)", ""]
    for k in order[:-1]:
        rows = [r for r in res if r["status"] == k]
        if rows:
            lines += [f"## {k} ({len(rows)})", ""]
            lines += [f"- `{r['key']}` {('doi ' + r['doi']) if r.get('doi') else ''} - {r.get('note', '')}"
                      for r in rows]
            lines.append("")
    lines += [f"## ok ({counts['ok']})", "", ", ".join(f"`{r['key']}`" for r in res if r["status"] == "ok"), ""]
    out = Path(a.out) if a.out else path.parent / f"cite_check_{path.stem}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:4]))
    print(f"report: {out}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
