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
3. Check the output with a separate pass against the node's `accept` criterion: the run reader (a routine role, see
   Model tiers) turns the outputs into a table with a script and hashes; a script applies `accept` when it is a
   formula, the orchestrator when it needs judgment.
4. Update `graph.yaml`, `pp.py stamp`, `decisions.yaml`; apply the node's `rule` if the result triggers it.
5. Append to the current report: what changed, why, what is next, decisions.

Budgets (tokens, CPU hours) and the deadline live in `state.yaml`; a tick that would exceed them asks first.

## Model tiers

A role runs on a cheaper model only when a check that does not rely on that model's judgment catches its errors
(routine). Everything else is judgment and stays on the strongest model in use. Measured costs, expected savings and
the measurements proposed before changing a tier: `model_tiers_20261107.md`.

**When to delegate at all.** Hand a step to a subagent only when its tool output is large (many files, web pages,
run outputs, cluster plumbing) and the main thread needs only the conclusion (a table, a file, a verdict with
locations). A lookup of a few tool calls stays inline, whatever its tier: a subagent starts from an empty context,
rereads its brief and files, and its result still has to be checked. In a long agent loop the bill is mostly the
context re-read at every call (cache reads: 98 % of the input-side tokens of the phase-1 pilot), so a script that
does the reading and prints a compact table saves more than a cheaper model, on every model.

**Which model.** A judgment role inherits the orchestrator's model (`model: inherit`); run the orchestrating session
on the strongest model you use. A routine role pins its model: on `inherit` it follows the orchestrator up (the
positioning sweep of 7 Nov 2026 ran on Fable 5.1 because its session did, at about four times its Sonnet price).
Haiku only for pure extraction where every item carries a verbatim quote and its location that a string search
confirms; no recurring step qualifies today.

| Role or step | Phase | Tier | Model | What catches a cheap model's errors |
|---|---|---|---|---|
| Material audit | 1 | judgment | inherit | none: it is the check of the draft; the orchestrator re-verifies its consequential findings. A batch of runs can go through the run reader first, so the audit reads a table instead of the outputs |
| Literature sweep (`lit/refs.yaml`, `lit/review.md`) | 1 | routine | sonnet (`lit-scout`) | `cite_check.py` exit 0 (no `mismatch`/`not_found`; `unverified` listed). Not caught: a missed work or a wrong `shows` line; novelty is re-judged by the scoop and options roles, and the orchestrator re-reads the `shows` lines it leans on |
| Scoop finder | 1 | judgment | inherit | none: its result is a negative (nobody made the claim) and a miss costs the paper. The pilot's self-pre-emption finding came from this role |
| Venue facts, `journal/requirements.yaml` | 1 | routine | sonnet | each fact and rule carries its URL, the date read and the source sentence verbatim; the orchestrator re-fetches the facts that decide gate A; phase 6 runs each rule's `check`. Fit and alternatives are re-judged by the options role |
| Options synthesis | 1 | judgment | inherit | none |
| Plan: mock abstract, figures, `accept`, `rule`, budget | 2 | judgment | inherit | none |
| Referees (plan review, review panel) | 2, 5 | judgment until measured | inherit | the review-panel backtest; a Sonnet tier waits on it (proposal in the note) |
| Editor synthesis, backtest assessor | 5 | judgment | inherit | none; the assessor is the yardstick of any model comparison, so it stays fixed across arms |
| Run reader: run outputs to a table with sha256 | 1, 3 | routine | sonnet (`run-reader`) | numbers come from a script, never transcribed; script, inputs and table are hashed; the orchestrator recomputes a cell or two from the raw outputs; `pp.py stamp` records the hashes. It never applies `accept` or `rule` |
| Applying `accept` and `rule`, interpreting results | 3 | judgment | orchestrator (a script when `accept` is a formula) | none |
| Bookkeeping: job submission, `runs/registry.yaml`, `graph.yaml`, `decisions.yaml`, `state.yaml` | all | routine, small | inline | `pp.py check` |
| Numbers-gate ledger entries, literal-to-macro fixes | 4 | routine | sonnet | the gate rerun (ledger, bare, words, fresh PASS) and each macro equal to the literal it replaces; a sentence whose wording changes goes to the orchestrator |
| Outline, prose, title and abstract, claims and their wording, cover letter, triage of review points | 4-6 | judgment | inherit | none |
| Final scoop search: the search log rerun for new items | 6 | routine | sonnet (`lit-scout`) | `cite_check.py`; any hit close to the claim goes to the orchestrator |
| Suggested reviewers: candidates and their recent papers | 6 | routine sweep | sonnet (`lit-scout`) | `cite_check.py` on the papers listed; the choice and the conflict-of-interest calls are the orchestrator's and the user's |
| Status, staleness, stamps, citation and numbers gates, compile, bundle, independence audit, word counts, `agent_cost.py` | all | script | no model | |

Claude wiring (local, gitignored): agents `run-reader` and `lit-scout` (`model: sonnet`), `paper-referee` and
`paper-editor` (`model: inherit`); the other roles take `model` per spawn in `.claude/skills/paper-pipeline/SKILL.md`.
With another assistant, give the role its brief and pick the model from this table. A tier changes only after a
measurement, recorded in the note.

## Reports to the user

Template `templates/report.md`. Short: where we stand (does the headline hold?), distance to completion (from
`pp.py status`), what changed and why, what is next, decisions (with defaults and deadlines), budget used. One page.

## Status of this runbook

Built 5 Nov 2026. Phases 2-3 are specified, not yet piloted; phase 4 reuses the Rhine numbers gate; phase 5 is
`studies/review_panel`.

Phase 1 pilot, 5 Nov 2026 (Cambodia compound-flood paper; target Economic Modelling special issue, 25 days to the
deadline): five agents, ~1.45 M tokens, ~2 h wall-clock (roles 18-30 min each, in parallel). (The 1.45 M is not
the billed volume: the transcripts bill 57.3 M cache-read, 1.3 M cache-write and 0.37 M output tokens, $25 at Opus
5.5 list prices: `model_tiers_20261107.md`.) Findings the user had
not seen: the headline figure pooled 30/60/90-day horizons; the model did not return to equilibrium after a cascade
(verified by the orchestrator); the headline wording contradicted the figure; the result was already in the second
author's working paper; the special issue's main criterion was not met. Lessons, now in the briefs: give the material
role read access to run outputs and the standard settling/pooling checks; search the authors' own output for
pre-emption; check whether an option's headline holds by construction and pilot it before committing; the
orchestrator must check the roles' most consequential claims itself (it confirmed the post-cascade rise and the venue
facts, and found the mechanical-interaction risk the synthesis had missed).
