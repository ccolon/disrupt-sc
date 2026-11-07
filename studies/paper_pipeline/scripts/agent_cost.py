"""Tokens billed to Claude Code agents, and their cost at list prices, from the transcripts (7 Nov 2026).

    python studies/paper_pipeline/scripts/agent_cost.py <agent id | transcript .jsonl | subagents folder> ... [--out FILE]

Agent ids are those the Agent tool returns (transcripts under ~/.claude/projects/*/*/subagents/agent-<id>.jsonl); a
folder means every agent-*.jsonl in it; a main session's own <session>.jsonl works too. Per transcript: the model it
ran on, the four billed categories (uncached input, cache writes by TTL, cache reads, output; one API response written
over several transcript lines is counted once, by message id), the wall-clock span, the start of its first prompt, and
the cost of the SAME token counts at the list prices of each model below.

Only the column of the model an agent ran on is a measurement. The other columns reprice its token counts: another
model takes another path through the task and tokenizes the same text differently, so they are first-order estimates.

Prices: API list prices in $ per million tokens, from the claude-api skill's model table (cached 6 Oct 2026); update
them when they change. Cache writes cost 1.25x input (5-minute TTL) or 2x (1-hour). Haiku 5.5 has a long-prompt rate
above 100K prompt tokens (input + cache write + cache read); its cache-read rate is taken as 0.1x input, the general
ratio the skill gives (Opus 5.5 0.05x and Fable 5.1 0.025x are quoted), and its long-prompt rates as 5x all round.
See ../model_tiers_20261107.md for what the pipeline uses this for.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

PRICES = {  # $/MTok: input, output, cache read; "long" applies when the prompt exceeds 100K tokens
    "opus-5.5": {"i": 4.0, "o": 20.0, "cr": 0.20},
    "sonnet-5.5": {"i": 2.0, "o": 10.0, "cr": 0.20},
    "haiku-5.5": {"i": 0.10, "o": 0.50, "cr": 0.01, "long": {"i": 0.50, "o": 2.50, "cr": 0.05}},
    "fable-5.1": {"i": 10.0, "o": 50.0, "cr": 0.25},
}
LONG_PROMPT = 100_000


def resolve(arg: str) -> list[Path]:
    p = Path(arg)
    if p.is_file():
        return [p]
    if p.is_dir():
        return sorted(p.glob("agent-*.jsonl"), key=lambda q: q.stat().st_mtime)
    hits = list((Path.home() / ".claude" / "projects").glob(f"*/*/subagents/agent-{arg}.jsonl"))
    if not hits:
        sys.exit(f"no transcript for {arg}")
    return hits[:1]


def read(path: Path) -> dict:
    """Billed usage per API response (last record of each message id), models, time span, first prompt."""
    calls, models, prompt, t0, t1 = {}, set(), None, None, None
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = r.get("timestamp")
            if ts:
                t0, t1 = t0 or ts, ts
            m = r.get("message")
            if not isinstance(m, dict):
                continue
            if r.get("type") == "user" and prompt is None:
                c = m.get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                prompt = " ".join(str(c or "").split())
            if r.get("type") == "assistant" and m.get("usage"):
                calls[m.get("id") or r.get("uuid")] = m["usage"]
                if m.get("model") and not str(m["model"]).startswith("<"):
                    models.add(m["model"])
    return {"calls": list(calls.values()), "models": sorted(models), "prompt": prompt or "", "t0": t0, "t1": t1}


def split(u: dict) -> dict:
    """The billed categories of one response; cache writes by TTL (all 5-minute when usage does not split them)."""
    cw = u.get("cache_creation_input_tokens") or 0
    cc = u.get("cache_creation") or {}
    w5, w1 = cc.get("ephemeral_5m_input_tokens"), cc.get("ephemeral_1h_input_tokens")
    if w5 is None and w1 is None:
        w5, w1 = cw, 0
    return {"in": u.get("input_tokens") or 0, "w5": w5 or 0, "w1": w1 or 0, "cw": cw,
            "cr": u.get("cache_read_input_tokens") or 0, "out": u.get("output_tokens") or 0}


def cost(u: dict, price: dict) -> float:
    s = split(u)
    pr = price["long"] if "long" in price and s["in"] + s["cw"] + s["cr"] > LONG_PROMPT else price
    return (s["in"] * pr["i"] + s["w5"] * 1.25 * pr["i"] + s["w1"] * 2.0 * pr["i"] + s["cr"] * pr["cr"]
            + s["out"] * pr["o"]) / 1e6


def summarize(path: Path) -> dict:
    t = read(path)
    tot = {k: 0 for k in ("in", "w5", "w1", "cw", "cr", "out")}
    for u in t["calls"]:
        for k, v in split(u).items():
            tot[k] += v
    minutes = None
    if t["t0"] and t["t1"]:
        a, b = (dt.datetime.fromisoformat(x.replace("Z", "+00:00")) for x in (t["t0"], t["t1"]))
        minutes = (b - a).total_seconds() / 60
    return {"name": path.stem, "models": t["models"], "n": len(t["calls"]), **tot, "minutes": minutes,
            "prompt": t["prompt"], "cost": {m: sum(cost(u, p) for u in t["calls"]) for m, p in PRICES.items()}}


def table(rows: list[dict]) -> str:
    head = ["transcript", "ran on", "calls", "min", "input", "cache write (5m/1h)", "cache read", "output"]
    lines = ["| " + " | ".join(head + [f"${m}" for m in PRICES]) + " |",
             "|" + "---|" * (len(head) + len(PRICES))]
    for r in rows + [total(rows)] if len(rows) > 1 else rows:
        lines.append("| " + " | ".join([
            r["name"], ",".join(r["models"]), str(r["n"]), "" if r["minutes"] is None else f"{r['minutes']:.0f}",
            f"{r['in']:,}", f"{r['cw']:,} ({r['w5']:,}/{r['w1']:,})", f"{r['cr']:,}", f"{r['out']:,}"]
            + [f"{r['cost'][m]:.2f}" for m in PRICES]) + " |")
    lines.append("")
    for r in rows:
        lines.append(f"- `{r['name']}`: {r['prompt'][:110].replace('|', '/')}")
    return "\n".join(lines) + "\n"


def total(rows: list[dict]) -> dict:
    t = {"name": "total", "models": [], "n": sum(r["n"] for r in rows), "minutes": None, "prompt": ""}
    for k in ("in", "w5", "w1", "cw", "cr", "out"):
        t[k] = sum(r[k] for r in rows)
    t["cost"] = {m: sum(r["cost"][m] for r in rows) for m in PRICES}
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="+", help="agent ids, transcript files or subagents folders")
    ap.add_argument("--out", help="write the Markdown table here too")
    a = ap.parse_args()
    rows = [summarize(p) for it in a.items for p in resolve(it)]
    txt = table(rows)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(txt)
    if a.out:
        Path(a.out).write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    main()
