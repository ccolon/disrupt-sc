# Paper pipeline

Background material + a main claim + a target journal -> a manuscript ready to submit, with the verification
automated and the user's decisions at four gates. Generic: nothing here imports DisruptSC; the model enters through
the project's runs and figures. Read [RUNBOOK.md](RUNBOOK.md) for the phases, the evidence graph and the decision
rules.

```
studies/paper_pipeline/
  RUNBOOK.md            phases, project folder, evidence graph, decisions, the analysis-loop tick, reports
  templates/            state.yaml, graph.yaml, decisions.yaml, report.md (copied by `pp.py init`)
  briefs/               role briefs (phase 1: material, literature, scoop, venue, options; common rules)
  scripts/pp.py         init | check | status | stamp - the graph, staleness, distance to completion
  scripts/cite_check.py citation gate: DOIs resolve, title/year/first author match (Crossref, OpenAlex)
  scripts/selftest.py   offline tests of both tools (23 checks)
```

Related tools: `studies/rhine2026/paper_gate.py` (numbers gate: every number in the text is a macro or a ledger
entry) and `studies/review_panel/` (independent referee panel with a backtest). Phases 4 and 5 use them.

## Start a project

```bash
python studies/paper_pipeline/scripts/pp.py init <project> --title "..." --claim "..." --venue "..." \
    --deadline YYYY-MM-DD --manuscript <overleaf clone> --code <repo or cluster path>
python studies/paper_pipeline/scripts/pp.py status <project>
python studies/paper_pipeline/scripts/cite_check.py <project>/lit/refs.yaml
```

Keep `<project>` next to the manuscript, outside the Overleaf clone. Phase 1 runs the five briefs as independent
agents (four in parallel, then the options synthesis) and ends with report `reports/01_gap.md` and gate A.

Claude Code: the local skill `.claude/skills/paper-pipeline/SKILL.md` (gitignored, per machine) routes a session
to the current phase of a project folder.

## Pilot

Phase 1 was piloted on 5 Nov 2026 on the Cambodia compound-flood paper (Nobile and Colon), target Economic
Modelling special issue on coupling physical and transition risks (deadline 30 Nov 2026). Project folder:
`C:/Users/Celian/OneDrive/DisruptSC/Paper_Cambodia/pipeline`. The citation gate on the draft's 134 references:
114 verified, 2 Crossref metadata errors confirmed by hand (`lit/cite_exceptions.yaml`), 3 DOIs to add, 15 grey
references without DOI.
