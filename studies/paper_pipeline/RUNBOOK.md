# Paper pipeline runbook

From background material + a main claim + a target journal to a manuscript ready to submit. Written for any
assistant (Claude, Codex, a human); the Claude wiring is a thin shim (`.claude/skills/paper-pipeline/SKILL.md`).

The pipeline is a state machine over files. Every phase reads the project folder, does its work, and writes back
before it ends; nothing that matters lives only in a conversation. A session that loses its context (compaction,
crash, next day) resumes from `state.yaml`.

## Project folder

Created by `python studies/paper_pipeline/scripts/pp.py init <folder> ...`. Keep it next to the manuscript, outside
the Overleaf clone (so it never reaches co-authors by accident).

| File | Written by | Holds |
|---|---|---|
| `state.yaml` | every phase | phase, gates passed, venue, deadline, budgets, pointers to the manuscript and code |
| `graph.yaml` | phases 1-5 | the evidence graph: claims -> evidence -> analyses -> runs/data (see below) |
| `stamps.yaml` | `pp.py stamp` only | content hashes of each node's inputs/outputs when it was accepted (staleness) |
| `decisions.yaml` | everyone | decision log and queue (see Decisions) |
| `reports/NN_<phase>.md` | end of each phase or tick | the report to the user (template in `templates/report.md`) |
| `gap/` | phase 1 | material audit, scoop search, venue assessment, options |
| `lit/refs.yaml`, `lit/review.md` | phase 1, updated later | verified references with what each one shows |
| `journal/requirements.yaml` | phase 1 | the venue's checkable rules (word counts, sections, statements) |
| `runs/registry.yaml` | phase 3 | every run: id, config, code commit, where outputs are, status, used for |

## The evidence graph (`graph.yaml`)

One list of nodes. Each node: `id`, `type` (claim | evidence | analysis | run | data | text), `what`, `needs`
(ids it depends on), `status` (todo | running | done | failed | blocked | dropped), and as relevant `accept` (the
criterion that makes it done, written before the result is known), `inputs`/`outputs` (file paths, for staleness),
`effort_days`, `cpu_hours`, `owner` (agent | user), `risk`, `rule` (pre-registered decision rule: what result
changes the claim, and what happens then).

- A claim is supported when all the evidence it needs is done. Distance to completion = remaining effort in the
  dependency closure of the headline claims (`pp.py status`).
- When an input file changes after a node was accepted, the node and everything downstream is **stale**
  (`pp.py status` reports it). This is the lesson of the Rhine 2026 paper: almost all of its late defects were claims
  left behind when the analysis was rerun.
- The numbers gate (`studies/rhine2026/paper_gate.py`) is the graph's last form: each number in the text is a macro
  produced by an analysis node.

## Decisions (`decisions.yaml`)

Each entry: `id`, `asked` (date), `question`, `options`, `default`, `kind`, `deadline`, `status` (open | answered |
defaulted), `answer`, `by`.

| kind | Meaning | Agent behaviour |
|---|---|---|
| `log` | reversible, inside the approved plan | decide, record, continue |
| `default` | reversible but costly, or a matter of judgement | propose a default and a deadline, continue on unblocked nodes; apply the default at the deadline unless answered |
| `block` | changes the claim, the model logic, the venue, the budget, data purchases, anything outside the plan | stop the affected nodes, ask, continue elsewhere |

Standing rules (from the user): commit locally, the user pushes code repositories (Overleaf pushes are allowed);
model-logic changes need the user's approval; never invent numbers, references, run results or hashes.

## Phases

| # | Phase | Output | Done when | Gate (user) |
|---|---|---|---|---|
| 1 | Gap analysis | `gap/material.md`, `lit/`, `gap/scoop.md`, `gap/venue.md`, `journal/requirements.yaml`, `gap/options.md`, seed `graph.yaml`, report 01 | three options, each with mock abstract, missing evidence, effort, novelty, risk, venue | A: choose an option and venue |
| 2 | Paper-shaped plan | mock abstract + figure list with placeholder macros; full graph with `accept` and `rule`; run list; budget; plan review by the panel (results-blind) | every headline claim has evidence nodes with acceptance criteria; panel's plan review triaged | B: approve plan and budget |
| 3 | Analysis loop | runs, analyses, figures, macros; a report per tick | headline claims done or explicitly weakened/dropped; no stale nodes | queued decisions |
| 4 | Writing | outline, figures, then prose; numbers only as macros; gate green | gate passes; every paragraph maps to graph nodes | C: outline, figures, title/abstract |
| 5 | Review panel | `studies/review_panel` run + triage | no new critical points, or 2 rounds done | major revisions back to phase 3 |
| 6 | Submission package | venue checks, final scoop search, cover letter, statements (data/code, AI use, competing interests), suggested reviewers | `journal/requirements.yaml` all satisfied | D: submit |
| 7 | Retrospective | real reviews vs panel backtest; effort estimated vs actual; lessons into the briefs | | |

Phases 1, 2 and 5 are fan-outs of independent roles (briefs in `briefs/`); 3 is a loop; 4 and 6 are sequential.

### Phase 1 roles (run in parallel, then the synthesis)

`briefs/phase1_material.md`, `phase1_literature.md`, `phase1_scoop.md`, `phase1_venue.md`, then
`phase1_options.md` once the four are written. Each role writes only its own files. After the literature role,
run the citation gate: `python studies/paper_pipeline/scripts/cite_check.py <project>/lit/refs.yaml` (and on the
draft's `.bib` if there is one). Unverified references are flagged in the options report, never silently kept.

### Phase 3 tick (the overnight unit)

1. `pp.py status <project>`: stale nodes first, then the next unblocked `todo` node on the critical path.
2. Run it, or submit the cluster job and record it in `runs/registry.yaml`; if waiting, sleep until the expected
   end (do not poll faster than the job can change).
3. Check the output with a separate pass (a verifier agent or a script) against the node's `accept` criterion.
4. Update `graph.yaml`, `pp.py stamp`, `decisions.yaml`; apply the node's `rule` if the result triggers it.
5. Append to the current report: what changed, why, what is next, decisions.

Budgets (tokens, CPU hours) and the deadline live in `state.yaml`; a tick that would exceed them asks first.

## Reports to the user

Template `templates/report.md`. Short: where we stand (does the headline hold?), distance to completion (from
`pp.py status`), what changed and why, what is next, decisions (with defaults and deadlines), budget used. One page.

## Status of this runbook

Built 5 Nov 2026. Phases 2-3 are specified, not yet piloted; phase 4 reuses the Rhine numbers gate; phase 5 is
`studies/review_panel`.

Phase 1 pilot, 5 Nov 2026 (Cambodia compound-flood paper; target Economic Modelling special issue, 25 days to the
deadline): five agents, ~1.45 M tokens, ~2 h wall-clock (roles 18-30 min each, in parallel). Findings the user had
not seen: the headline figure pooled 30/60/90-day horizons; the model did not return to equilibrium after a cascade
(verified by the orchestrator); the headline wording contradicted the figure; the result was already in the second
author's working paper; the special issue's main criterion was not met. Lessons, now in the briefs: give the material
role read access to run outputs and the standard settling/pooling checks; search the authors' own output for
pre-emption; check whether an option's headline holds by construction and pilot it before committing; the
orchestrator must check the roles' most consequential claims itself (it confirmed the post-cascade rise and the venue
facts, and found the mechanical-interaction risk the synthesis had missed).
