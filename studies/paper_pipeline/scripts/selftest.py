"""Self-test of the paper pipeline tools (offline). python studies/paper_pipeline/scripts/selftest.py"""
from __future__ import annotations

import datetime as dt
import sys
import tempfile
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cite_check as cc  # noqa: E402
import pp  # noqa: E402

RESULTS = []


def ok(name, cond):
    RESULTS.append((name, bool(cond)))


def write_graph(proj: Path, nodes):
    (proj / "graph.yaml").write_text(yaml.safe_dump({"nodes": nodes}, sort_keys=False), encoding="utf-8")


def base_nodes():
    return [
        {"id": "C1", "type": "claim", "what": "c", "needs": ["E1"], "status": "todo"},
        {"id": "E1", "type": "evidence", "what": "e", "needs": ["A1", "A2"], "status": "todo", "effort_days": 1},
        {"id": "A1", "type": "analysis", "what": "a1", "needs": ["R1"], "status": "done", "effort_days": 2,
         "inputs": ["in.csv"], "outputs": ["out.csv"]},
        {"id": "A2", "type": "analysis", "what": "a2", "needs": [], "status": "todo", "effort_days": 3},
        {"id": "R1", "type": "run", "what": "r", "needs": [], "status": "done", "effort_days": 5,
         "outputs": ["in.csv"]},
    ]


def test_pp():
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "p"
        pp.init(proj, "T", "the claim", "V", (dt.date.today() + dt.timedelta(days=10)).isoformat(), "", "")
        ok("init creates state, graph, decisions", all((proj / f).exists() for f in
                                                      ("state.yaml", "graph.yaml", "decisions.yaml")))
        (proj / "in.csv").write_text("1", encoding="utf-8")
        (proj / "out.csv").write_text("2", encoding="utf-8")
        write_graph(proj, base_nodes())
        ok("clean graph passes check", pp.check(proj) == [])

        bad = base_nodes() + [{"id": "A2", "type": "analysis", "what": "dup", "status": "todo"},
                              {"id": "X1", "type": "bogus", "what": "x", "status": "maybe", "needs": ["NOPE"]}]
        bad[4]["needs"] = ["E1"]  # E1 -> A1 -> R1 -> E1 cycle
        write_graph(proj, bad)
        probs = " | ".join(pp.check(proj))
        ok("duplicate id caught", "duplicate id" in probs)
        ok("unknown need caught", "unknown id NOPE" in probs)
        ok("bad type and status caught", "type 'bogus'" in probs and "status 'maybe'" in probs)
        ok("cycle caught", "cycle" in probs)

        nodes = base_nodes()
        nodes[2]["outputs"] = ["missing.csv"]
        write_graph(proj, nodes)
        ok("done node with missing output caught", any("output missing" in p for p in pp.check(proj)))

        write_graph(proj, base_nodes())
        txt = pp.status(proj)
        # open nodes under C1: C1, E1, A2 -> effort 1 + 3 = 4; critical path max(E1 1 + max(A1 0, A2 3)) = 4
        ok("remaining effort and critical path", "| C1 | todo | 3/5 | 4 | 0 | 4 |" in txt)
        ok("ready list has A2", "Ready to start" in txt and "A2" in txt.split("Ready to start")[1])

        pp.stamp(proj, ["R1", "A1"])
        g = {n["id"]: n for n in pp.load_graph(proj)}
        st = yaml.safe_load((proj / "stamps.yaml").read_text(encoding="utf-8"))
        ok("fresh stamps are not stale", pp.stale_nodes(proj, g, st) == {})
        (proj / "in.csv").write_text("changed", encoding="utf-8")
        s = pp.stale_nodes(proj, g, st)
        ok("changed input makes producer and consumer stale", "R1" in s and "A1" in s)
        (proj / "in.csv").write_text("1", encoding="utf-8")
        time.sleep(1.1)
        pp.stamp(proj, ["R1"])
        st = yaml.safe_load((proj / "stamps.yaml").read_text(encoding="utf-8"))
        s = pp.stale_nodes(proj, g, st)
        ok("re-accepted dependency makes dependent stale", s.get("A1", "").startswith("R1 re-accepted"))

        dec = {"decisions": [{"id": "Q1", "question": "q", "default": "d", "kind": "default",
                              "deadline": dt.date.today().isoformat(), "status": "open"}]}
        (proj / "decisions.yaml").write_text(yaml.safe_dump(dec), encoding="utf-8")
        ok("due default flagged", "DEFAULT DUE" in pp.status(proj))


def test_cite():
    bib = r"""@article{a_2020, title = {A {Nested} title: with braces}, author = {M{\"u}ller, Jan and Doe, J.},
      year = {2020}, doi = {https://doi.org/10.1/abc}}
    @misc{b, title = "Plain", author = {World Bank}, year = 2019}"""
    r = cc.parse_bib(bib)
    ok("bib: two entries", len(r) == 2)
    ok("bib: nested braces and doi prefix", r[0]["title"].startswith("A {Nested}") and r[0]["doi"] == "10.1/abc")
    ok("bib: first author family", r[0]["first_author"] == "muller" and r[1]["first_author"] == "bank")
    ok("norm unescapes entities", cc.norm("Review article &amp;quot;Assessment&amp;quot;") == "review article assessment")
    ok("title prefix tolerance", cc.title_sim("Assessment of economic flood damage",
                                             "Review article: Assessment of economic flood damage") >= 0.9)
    m = {"title": "Geopolitical disruptions in global supply chains", "years": [2023], "family": "bednarski",
         "names": "lukasz bednarski samuel roscoe"}
    e = {"title": "Geopolitical disruptions in global supply chains", "year": "2024", "first_author": "bednarski"}
    ok("year within one passes", cc.judge(e, m) == [])
    ok("year two off fails", cc.judge(dict(e, year="2026"), m) != [])
    ok("other title fails", cc.judge(dict(e, title="A completely different paper on rice"), m) != [])
    ok("author found among first three", cc.judge(dict(e, first_author="roscoe"), m) == [])
    ok("unknown author fails", cc.judge(dict(e, first_author="smith"), m) != [])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    test_pp()
    test_cite()
    for n, c in RESULTS:
        print(f"{'PASS' if c else 'FAIL'}  {n}")
    bad = sum(1 for _, c in RESULTS if not c)
    print(f"{len(RESULTS) - bad}/{len(RESULTS)} passed")
    sys.exit(1 if bad else 0)
