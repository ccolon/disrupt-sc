"""Paper pipeline: project state, evidence graph, staleness and distance to completion.

    python studies/paper_pipeline/scripts/pp.py init <project> --title T --claim C --venue V [--deadline YYYY-MM-DD]
                                                  [--manuscript PATH] [--code PATH]
    python studies/paper_pipeline/scripts/pp.py check <project>          # schema, ids, cycles, outputs of done nodes
    python studies/paper_pipeline/scripts/pp.py status <project> [--out FILE]   # the report's "distance" block
    python studies/paper_pipeline/scripts/pp.py stamp <project> ID [ID ...]     # record input/output hashes

See ../RUNBOOK.md. graph.yaml is written by people and agents (comments kept); stamps.yaml only by this tool.
Exit code of check: 0 clean, 1 problems.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
TYPES = {"claim", "evidence", "analysis", "run", "data", "text"}
STATUSES = {"todo", "running", "done", "failed", "blocked", "dropped"}
CLOSED = {"done", "dropped"}
KINDS = {"log", "default", "block"}
DSTATUS = {"open", "answered", "defaulted"}


def _load(p: Path, default=None):
    if not p.exists():
        return default
    with p.open(encoding="utf-8") as f:
        v = yaml.safe_load(f)
    return default if v is None else v


def _today() -> dt.date:
    return dt.date.today()


# ---------------------------------------------------------------- init
def init(project: Path, title: str, claim: str, venue: str, deadline: str, manuscript: str, code: str):
    if (project / "state.yaml").exists():
        sys.exit(f"{project / 'state.yaml'} exists; refusing to overwrite")
    for sub in ("gap", "lit", "journal", "reports", "runs"):
        (project / sub).mkdir(parents=True, exist_ok=True)
    rep = {"@TITLE@": title, "@CLAIM@": claim.replace('"', "'"), "@VENUE@": venue, "@DEADLINE@": deadline or "",
           "@TODAY@": _today().isoformat()}
    for name in ("state.yaml", "graph.yaml", "decisions.yaml"):
        t = (TEMPLATES / name).read_text(encoding="utf-8")
        for k, v in rep.items():
            t = t.replace(k, v)
        (project / name).write_text(t, encoding="utf-8")
    st = _load(project / "state.yaml")
    st["material"]["manuscript"] = manuscript or ""
    st["material"]["code"] = code or ""
    st["log"] = [f"{_today().isoformat()} init: phase 1"]
    _dump_state(project, st)
    (project / "runs" / "registry.yaml").write_text("runs: []\n", encoding="utf-8")
    print(f"initialised {project}")


def _dump_state(project: Path, st: dict):
    head = "# Project state - read first by every session, written last by every phase.\n"
    (project / "state.yaml").write_text(head + yaml.safe_dump(st, sort_keys=False, allow_unicode=True, width=110),
                                        encoding="utf-8")


# ---------------------------------------------------------------- graph
def load_graph(project: Path) -> list[dict]:
    g = _load(project / "graph.yaml", {}) or {}
    return list(g.get("nodes") or [])


def check(project: Path) -> list[str]:
    probs = []
    nodes = load_graph(project)
    ids = {}
    for i, n in enumerate(nodes):
        nid = n.get("id")
        if not nid:
            probs.append(f"node #{i}: no id")
            continue
        if nid in ids:
            probs.append(f"{nid}: duplicate id")
        ids[nid] = n
        if n.get("type") not in TYPES:
            probs.append(f"{nid}: type {n.get('type')!r} not in {sorted(TYPES)}")
        if n.get("status") not in STATUSES:
            probs.append(f"{nid}: status {n.get('status')!r} not in {sorted(STATUSES)}")
        if not n.get("what"):
            probs.append(f"{nid}: no 'what'")
    for nid, n in ids.items():
        for d in n.get("needs") or []:
            if d not in ids:
                probs.append(f"{nid}: needs unknown id {d}")
        if n.get("type") == "claim" and not n.get("needs") and n.get("status") not in CLOSED:
            probs.append(f"{nid}: open claim with no evidence")
        if n.get("status") == "done":
            for p in n.get("outputs") or []:
                if _resolve(project, p) is None or not _resolve(project, p).exists():
                    probs.append(f"{nid}: done but output missing: {p}")
    # cycles
    state = {}

    def visit(u, path):
        state[u] = 1
        for v in ids.get(u, {}).get("needs") or []:
            if v not in ids:
                continue
            if state.get(v) == 1:
                probs.append("cycle: " + " -> ".join(path + [v]))
            elif not state.get(v):
                visit(v, path + [v])
        state[u] = 2

    for u in ids:
        if not state.get(u):
            visit(u, [u])
    dec = (_load(project / "decisions.yaml", {}) or {}).get("decisions") or []
    for d in dec:
        if d.get("kind") not in KINDS:
            probs.append(f"decision {d.get('id')}: kind {d.get('kind')!r} not in {sorted(KINDS)}")
        if d.get("status") not in DSTATUS:
            probs.append(f"decision {d.get('id')}: status {d.get('status')!r} not in {sorted(DSTATUS)}")
    return probs


def _resolve(project: Path, p: str) -> Path | None:
    if not p:
        return None
    q = Path(p)
    return q if q.is_absolute() else project / q


def _hash(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    files = [path] if path.is_file() else sorted(x for x in path.rglob("*") if x.is_file())
    for f in files:
        h.update(str(f.relative_to(path) if path.is_dir() else f.name).encode())
        with f.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()[:16]


def stamp(project: Path, ids: list[str]):
    nodes = {n["id"]: n for n in load_graph(project) if n.get("id")}
    st = _load(project / "stamps.yaml", {}) or {}
    now = dt.datetime.now().isoformat(timespec="seconds")
    for i in ids:
        if i not in nodes:
            sys.exit(f"unknown node {i}")
        n = nodes[i]
        files = {}
        for p in (n.get("inputs") or []) + (n.get("outputs") or []):
            files[p] = _hash(_resolve(project, p))
        st[i] = {"at": now, "files": files}
        print(f"stamped {i}: {len(files)} files")
    (project / "stamps.yaml").write_text("# written by pp.py stamp - do not edit\n" +
                                         yaml.safe_dump(st, sort_keys=True), encoding="utf-8")


def stale_nodes(project: Path, nodes: dict, stamps: dict) -> dict[str, str]:
    """id -> reason. Direct: a stamped file changed. Upstream: a dependency is stale or was re-stamped later."""
    out = {}
    for i, n in nodes.items():
        s = stamps.get(i)
        if not s or n.get("status") != "done":
            continue
        for p, h in (s.get("files") or {}).items():
            cur = _hash(_resolve(project, p))
            if cur != h:
                out[i] = f"{p} changed since stamp" if cur else f"{p} missing since stamp"
                break
        if i in out:
            continue
        for d in n.get("needs") or []:
            sd = stamps.get(d)
            if sd and sd["at"] > s["at"]:
                out[i] = f"{d} re-accepted after {i}"
                break
    changed = True
    while changed:
        changed = False
        for i, n in nodes.items():
            if i in out or n.get("status") != "done":
                continue
            for d in n.get("needs") or []:
                if d in out:
                    out[i] = f"upstream {d} stale"
                    changed = True
                    break
    return out


def closure(nodes: dict, root: str) -> set[str]:
    seen, todo = set(), [root]
    while todo:
        u = todo.pop()
        if u in seen or u not in nodes:
            continue
        seen.add(u)
        todo.extend(nodes[u].get("needs") or [])
    return seen


def critical_path(nodes: dict, root: str, memo: dict) -> float:
    """Longest chain of remaining effort below root (lower bound on calendar days with unlimited parallelism)."""
    if root in memo:
        return memo[root]
    n = nodes.get(root, {})
    own = 0.0 if n.get("status") in CLOSED else float(n.get("effort_days") or 0)
    memo[root] = own + max([critical_path(nodes, d, memo) for d in n.get("needs") or [] if d in nodes] or [0.0])
    return memo[root]


def status(project: Path) -> str:
    st = _load(project / "state.yaml", {}) or {}
    nodes = {n["id"]: n for n in load_graph(project) if n.get("id")}
    stamps = _load(project / "stamps.yaml", {}) or {}
    stale = stale_nodes(project, nodes, stamps)
    lines = [f"## Status of {st.get('title', project.name)} ({_today().isoformat()})", ""]
    dl = st.get("deadline")
    days_left = None
    if dl:
        try:
            days_left = (dt.date.fromisoformat(str(dl)) - _today()).days
        except ValueError:
            pass
    lines.append(f"Phase {st.get('phase')}; venue: {st.get('venue')}; deadline {dl or '-'}"
                 + (f" ({days_left} days left)" if days_left is not None else ""))
    by = {}
    for n in nodes.values():
        by.setdefault(n.get("type"), {}).setdefault(n.get("status"), 0)
        by[n.get("type")][n.get("status")] += 1
    lines.append("")
    lines.append("| type | " + " | ".join(sorted(STATUSES)) + " |")
    lines.append("|---|" + "---|" * len(STATUSES))
    for t in ["claim", "evidence", "analysis", "run", "data", "text"]:
        if t in by:
            lines.append(f"| {t} | " + " | ".join(str(by[t].get(s, 0)) for s in sorted(STATUSES)) + " |")
    claims = [i for i, n in nodes.items() if n.get("type") == "claim" and n.get("status") != "dropped"]
    heads = [i for i in claims if nodes[i].get("level", "headline") == "headline"] or claims
    lines += ["", "| claim | status | open nodes | remaining effort (d) | unknown effort | critical path (d) |",
              "|---|---|---|---|---|---|"]
    memo = {}
    for c in heads:
        cl = closure(nodes, c)
        open_ = [i for i in cl if nodes[i].get("status") not in CLOSED]
        eff = sum(float(nodes[i].get("effort_days") or 0) for i in open_)
        unk = sum(1 for i in open_ if nodes[i].get("effort_days") is None and nodes[i].get("type") != "claim")
        lines.append(f"| {c} | {nodes[c].get('status')} | {len(open_)}/{len(cl)} | {eff:g} | {unk} | "
                     f"{critical_path(nodes, c, memo):g} |")
    union = set().union(*[closure(nodes, c) for c in heads]) if heads else set()
    tot = sum(float(nodes[i].get("effort_days") or 0) for i in union if nodes[i].get("status") not in CLOSED)
    cp = max([critical_path(nodes, c, memo) for c in heads] or [0])
    lines.append("")
    lines.append(f"Remaining effort on the headline claims: {tot:g} person-days; critical path {cp:g} days"
                 + (f"; {days_left} calendar days to the deadline" if days_left is not None else "") + ".")
    if stale:
        lines += ["", "Stale (rerun or re-check before relying on them):"]
        lines += [f"- {i}: {r}" for i, r in sorted(stale.items())]
    bad = [i for i, n in nodes.items() if n.get("status") in ("failed", "blocked")]
    if bad:
        lines += ["", "Failed or blocked: " + ", ".join(f"{i} ({nodes[i]['status']})" for i in sorted(bad))]
    ready = [i for i, n in nodes.items() if n.get("status") == "todo" and n.get("type") != "claim"
             and all(nodes.get(d, {}).get("status") in CLOSED for d in n.get("needs") or [])]
    ready.sort(key=lambda i: -critical_path(nodes, i, memo))
    if ready:
        lines += ["", "Ready to start (longest chain first): " + ", ".join(ready[:12])]
    dec = (_load(project / "decisions.yaml", {}) or {}).get("decisions") or []
    open_dec = [d for d in dec if d.get("status") == "open"]
    if open_dec:
        lines += ["", "Open decisions:"]
        for d in open_dec:
            due = d.get("deadline")
            over = ""
            if due and d.get("kind") == "default" and str(due) <= _today().isoformat():
                over = " - DEFAULT DUE"
            lines.append(f"- {d.get('id')} [{d.get('kind')}] {d.get('question')} (default: {d.get('default')}; "
                         f"by {due or '-'}){over}")
    return "\n".join(lines) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("init")
    a.add_argument("project")
    a.add_argument("--title", required=True)
    a.add_argument("--claim", required=True)
    a.add_argument("--venue", required=True)
    a.add_argument("--deadline", default="")
    a.add_argument("--manuscript", default="")
    a.add_argument("--code", default="")
    c = sub.add_parser("check")
    c.add_argument("project")
    s = sub.add_parser("status")
    s.add_argument("project")
    s.add_argument("--out")
    m = sub.add_parser("stamp")
    m.add_argument("project")
    m.add_argument("ids", nargs="+")
    args = ap.parse_args()
    p = Path(args.project)
    if args.cmd == "init":
        init(p, args.title, args.claim, args.venue, args.deadline, args.manuscript, args.code)
    elif args.cmd == "check":
        probs = check(p)
        print("\n".join(probs) if probs else "graph and decisions: OK")
        sys.exit(1 if probs else 0)
    elif args.cmd == "status":
        txt = status(p)
        if args.out:
            Path(args.out).write_text(txt, encoding="utf-8")
        print(txt)
    elif args.cmd == "stamp":
        stamp(p, args.ids)


if __name__ == "__main__":
    main()
