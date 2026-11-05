"""Independence audit of a panel run (5 Nov 2026): every file the referee and editor subagents opened, and every tool
they used, read from their Claude Code transcripts. Exit 1 when one of them touched a path outside the allowed
prefixes or used a tool that reaches outside the bundle (shell, web).

    python studies/review_panel/audit_independence.py --allow C:/dsc_runs/review_panel/rhine_ce22110 \
        --allow studies/review_panel --allow studies/rhine2026/review/panel_20261105_ce22110 <agent id> [<agent id> ...]

Agent ids are those the Agent tool returns; the transcripts are found under ~/.claude/projects/*/*/subagents/.
Relative --allow prefixes are taken from the repository root.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_TOOLS = {"Bash", "PowerShell", "WebSearch", "WebFetch", "Agent"}
PATH_KEYS = ("file_path", "path", "notebook_path")


def norm(p: str) -> str:
    return str(Path(p)).replace("\\", "/").lower()


def transcript(aid: str) -> Path:
    hits = list((Path.home() / ".claude" / "projects").glob(f"*/*/subagents/agent-{aid}.jsonl"))
    if not hits:
        sys.exit(f"no transcript for agent {aid}")
    return hits[0]


def main(agent_ids, allow):
    allowed = [norm(a if Path(a).is_absolute() else ROOT / a) for a in allow]
    bad = 0
    for aid in agent_ids:
        tools, paths = Counter(), Counter()
        for line in transcript(aid).read_text(encoding="utf-8").splitlines():
            try:
                content = (json.loads(line).get("message") or {}).get("content")
            except json.JSONDecodeError:
                continue
            for c in content if isinstance(content, list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tools[c.get("name")] += 1
                    for k in PATH_KEYS:
                        if k in (c.get("input") or {}):
                            paths[str(c["input"][k])] += 1
        outside = sorted(p for p in paths if not any(norm(p).startswith(a) for a in allowed))
        used_bad = sorted(t for t in tools if t in FORBIDDEN_TOOLS)
        status = "OK" if not outside and not used_bad else "VIOLATION"
        bad += status != "OK"
        print(f"{aid}: {status}; tools {dict(tools)}; {len(paths)} distinct paths")
        for p in outside:
            print(f"   outside the allowed prefixes: {p}")
        for t in used_bad:
            print(f"   forbidden tool used: {t} x{tools[t]}")
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow", action="append", required=True)
    ap.add_argument("agent_ids", nargs="+")
    a = ap.parse_args()
    sys.exit(main(a.agent_ids, a.allow))
