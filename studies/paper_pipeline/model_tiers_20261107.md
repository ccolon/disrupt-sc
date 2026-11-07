# Model tiers: what the agents cost, what tiering saves, what to measure (7 Nov 2026)

The tier table and the delegation rule are in [RUNBOOK.md](RUNBOOK.md#model-tiers). This note gives the numbers behind
them and two measurements proposed to the user, not run (they cost tokens).

## How the numbers were made

`scripts/agent_cost.py` on the Claude Code transcripts of the agents (usage records, one per API response). Prices are
API list prices from the claude-api skill (table cached 6 Oct 2026), $ per million tokens:

| model | input | output | cache read | cache write (5 min / 1 h) |
|---|---|---|---|---|
| Opus 5.5 | 4.00 | 20.00 | 0.20 | 5.00 / 8.00 |
| Sonnet 5.5 | 2.00 | 10.00 | 0.20 | 2.50 / 4.00 |
| Haiku 5.5 (prompt up to 100K tokens) | 0.10 | 0.50 | 0.01 (assumed 0.1x input) | 0.125 / 0.20 |
| Fable 5.1 | 10.00 | 50.00 | 0.25 | 12.50 / 20.00 |

Haiku 5.5 costs $0.50 / $2.50 above 100K prompt tokens, which most calls of these agents exceed (the tool applies it
per call). Only the column of the model an agent ran on is a measurement; the others reprice the same token counts,
whereas another model takes another path through the task and may tokenize the same text differently. They are
first-order estimates. Under a subscription, read the ratios, not the dollars.

## Phase-1 baseline (pilot of 5 Nov 2026, Cambodia, all five roles on Opus 5.5)

| role | minutes | cache read | cache write | output | Opus 5.5 (as run) | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|---|---|---|
| material audit | 26 | 16.32 M | 315 k | 88 k | 6.61 | 4.94 | 1.19 |
| literature | 30 | 14.59 M | 267 k | 80 k | 5.85 | 4.38 | 1.01 |
| scoop | 19 | 10.33 M | 268 k | 46 k | 4.33 | 3.20 | 0.72 |
| venue | 18 | 7.18 M | 199 k | 44 k | 3.31 | 2.37 | 0.52 |
| options synthesis | 21 | 8.91 M | 245 k | 116 k | 5.34 | 3.56 | 0.85 |
| total | | 57.33 M | 1.29 M | 375 k | 25.43 | 18.45 | 4.30 |

Uncached input is 616 tokens in all. Agents `a75028747a7b367f0` (venue), `a83e50e3c5f7d693a` (scoop),
`ac15904a3e2074feb` (material), `aa438163af460cf6b` (literature), `a17edf9b3a10012e1` (options), session
`e14b89b0`. Quality markers of the same run, for a comparison: the literature role's `refs.yaml` passed the citation
gate with 60 entries, 59 `ok`, 1 `unverified` (an NGFS report without DOI), no `mismatch` or `not_found`; the scoop
role found the self-pre-emption (the CESifo working paper and the SSRN posting); the material audit found the pooled
horizons and the losses that do not settle.

At Opus 5.5 prices the bill splits into cache reads 45 %, output 29 %, cache writes 25 %. Cache reads are the context
re-read at every call (here 303 calls on contexts averaging about 190 K tokens), and Sonnet 5.5 bills them at the same
$0.20 as Opus 5.5. That is why Sonnet saves only 27 % on these long loops, against the halving the list prices suggest.

## Other agent runs, for scale

| run | agents | ran on | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 | Fable 5.1 |
|---|---|---|---|---|---|---|
| review panel backtest, 5 Nov: four referees | 4 | Opus 5.5 | 11.60 | 6.13 | 1.08 | 28.17 |
| same: editor and backtest assessor | 2 | Opus 5.5 | 5.41 | 2.90 | 0.46 | 13.03 |
| numbers-gate ledger and pending-literal fixes, 5 Nov | 6 | Opus 5.5 | 41.12 | 26.93 | 6.35 | 86.87 |
| Rhine positioning sweep, 7 Nov (as read at 21:19; one agent was still being continued) | 4 | Fable 5.1 | 26.66 | 14.65 | 3.40 | 63.35 |
| orchestrating session `e14b89b0` (5-7 Nov, as read 7 Nov) | main | Opus 5.5 | 110.91 | 87.65 | 21.70 | 196.81 |

Referees are short loops (read the bundle, write a report: about 10 calls each), so output and cache writes dominate
and Sonnet would cut their cost by 47 %. The orchestrating session cost more than all 17 agents it spawned ($84 at
Opus 5.5 prices): keeping large tool output out of the main thread is the first lever, before any tier.

## Expected savings of the tiers as configured

- **Phase 1**: literature and venue move to Sonnet: $9.16 -> about $6.75, about $2.4 of $25.4 (9 %). The material,
  scoop and options roles stay on the main model: 64 % of the phase-1 cost, and the roles that found what mattered.
- **Phase 4**: gate ledger and literal-to-macro fixes on Sonnet: about $41 -> $27 for a round like 5 Nov's (-35 %).
- **Routine sweeps under a Fable 5.1 orchestrator**: pinning `sonnet` instead of inheriting takes the 7 Nov
  positioning sweep from $63 to about $15 (-77 %). The largest saving here comes from pinning, not from the tier.
- **Referees**: about $5.5 per panel run (-47 % of the referee cost, -36 % of a panel run with the editor), if and
  only if measurement 1 supports it. Until then they inherit.
- **Not touched by tiers**: the orchestrator's own context; the delegation rule in the runbook is what addresses it.

## Measurement 1 (proposed, not run): Sonnet referees against the current panel

- **Reference**: the review of 8 Oct 2026 on Rhine `d1e453e`, with the authors' verdicts in
  `studies/rhine2026/review/review_20261008_response.md`. The panel instructions' author has not read it (review_panel
  README), unlike the 22 Sep reference of the first backtest (~90 % recall), so it is also the clean rerun that README
  asks for. This note's author did not open it either.
- **Design**: one bundle (`prepare_bundle.py --commit d1e453e`), two arms, the referees' model the only difference:
  arm A referees on `opus` (the model of the 5 Nov panel), arm B on `sonnet`, same briefs and task text. Editor
  (`editor_synthesis.md`) and assessor (`assessor_backtest.md`) on Opus 5.5 in both arms. Output folders `..._A` and
  `..._B` with nothing in them naming the model, so the assessor scores each arm without knowing which it is. Both arms
  go through `audit_independence.py`; costs with `agent_cost.py`.
- **Measures**: recall overall and on confirmed points (the assessor's strict matching), critical points found, false
  alarms carried to the before-submission list, cost and wall-clock per arm.
- **Rule, fixed before the run**: switch the referees to Sonnet (`model: sonnet` in `paper-referee.md`) if arm B finds
  every confirmed and every critical reference point that arm A finds, and its overall recall is at most two points
  below A's; otherwise they keep `inherit`. If B's losses all come from one referee, that referee keeps the main model
  (per-spawn `model`) and the others switch. One run per arm detects only large losses: if B passes with a margin of
  one point or less on confirmed points, run B once more before switching.
- **Cost**: from the 5 Nov backtest (another version of the paper, so give or take the bundle size): arm A about $17
  at list prices (referees $11.6, editor $3.7, assessor $1.7), arm B about $11.5 (referees repriced at Sonnet, $6.1),
  about $29 together, plus the orchestrator's reading of the results.
- **Limits**: agreement with one earlier review, not with journal referees. A third arm, the referees on the same
  model at lower effort, would test the other cheap option; its cost is unknown until run.

## Measurement 2 (proposed, not run): the two downgraded phase-1 roles on Sonnet, same task

- Rerun the literature and venue roles on Sonnet on the Cambodia project as it stood for the pilot, into a scratch copy
  of the project folder (the pilot's files stay untouched), with the current briefs (any change since the pilot is
  recorded with the result).
- Compare with the pilot: citation-gate counts (pilot: 60, 59 ok, 1 unverified, 0 wrong); overlap of `refs.yaml` and
  of the must-cite list with the pilot's; every venue fact that differs from `gap/venue.md`, checked at its source;
  cost against the baseline above ($9.16 for the two roles as run, about $6.75 expected).
- Rule: the Sonnet tier stays if the gate shows no `mismatch` or `not_found`, the must-cite differences judged by the
  orchestrator lose nothing the options synthesis relied on, and no fact that decided gate A is wrong; otherwise the
  role goes back to `inherit`.
- Cost: about $7 at list prices.
