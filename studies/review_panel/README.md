# Reviewer panel (5 Nov 2026)

An independent pre-submission review of a manuscript by four referees and an editor, each an LLM agent that sees only
the compiled paper. It complements `studies/rhine2026/paper_gate.py`, which checks the numbers mechanically: the panel
looks for the problems a journal referee would raise (estimands that do not match, results that follow by
construction, validation that cannot fail, claims stronger than the evidence).

## Pieces

| file | role |
|---|---|
| `prepare_bundle.py` | exports a commit of the Overleaf checkout, compiles it with tectonic (local package cache first), writes `paper.txt` (page by page), `figures/*.png` (Ghostscript) with `figures/index.md`, `paper.pdf`. The bundle is all a referee reads. |
| `referee_common.md` | how every referee reads, what every referee checks, severity scale, report format |
| `referees/R1_methods.md` | supply-chain disruption modelling (rules, calibration, validation, uncertainty, reproducibility) |
| `referees/R2_transport.md` | freight transport, inland navigation, hydrology (hazard to capacity, substitution, chronology, levers) |
| `referees/R3_economics.md` | macro and input-output economics (loss metrics, matched estimands, prices, policy statements) |
| `referees/R4_editor.md` | handling editor's reading (significance, novelty, proportionality, clarity, figures, reporting) |
| `editor_synthesis.md` | the editor consolidates the four reports, checks each point against the text (verified / misread / unverifiable), decides |
| `assessor_backtest.md` | scores the panel against a review an earlier version received (strict matching, recall overall and on confirmed points) |
| `audit_independence.py` | reads the subagents' Claude Code transcripts and lists every path they opened and tool they used; exit 1 if a referee left the bundle or used the shell or the web |

The files are plain instructions: they run with Claude subagents (`.claude/skills/review-panel/SKILL.md`, agents
`paper-referee` and `paper-editor` in `.claude/agents/`, both local and gitignored), and the same brief can be pasted
into another model (ChatGPT) with the bundle attached, which is the cheapest way to add a referee from another model
family.

## Rules

- **Independence**: the referees get the bundle and their instructions, nothing else: no code, notes, earlier reviews
  or responses, and nothing from the session that runs them. A referee anchored on the authors' reasoning finds what
  the authors already know.
- **The panel proposes, the author decides**: its points are sorted like any review (confirmed in our data, text fix,
  analysis needed, declined with the reason) in `studies/<study>/review/`; nothing in the model or the manuscript
  changes on its say-so.
- **Trust is measured**: a backtest on a version that received a real review gives the panel's recall, overall and on
  the points the authors confirmed. Instructions written after reading the reference review leak into the test; the
  backtest records say which.

## Running

```
python studies/review_panel/prepare_bundle.py --commit HEAD --out C:/dsc_runs/review_panel/rhine_<sha>
```

then the skill (`/review-panel`, or ask for "the reviewer panel"), which spawns the four referees in parallel and the
editor, and writes to `studies/<study>/review/panel_<date>_<sha>/`. A full run costs about 0.5-1 M tokens.

## Backtests

| date | version | reference | recall (all / confirmed) | record |
|---|---|---|---|---|
| 5 Nov 2026 | Rhine ce22110 (22 Sep 2026) | review of 22 Sep 2026 (ChatGPT, 26 points) | 96 % as scored (24 found, 2 partial); ~90 % counting NS2, OR6, EC4 partial; 9/9 critical, 7/7 confirmed | `studies/rhine2026/review/panel_20261105_ce22110/` |

What the first backtest says (details in its `backtest.md`). The panel finds the problems the manuscript's own text,
numbers and figures expose, including the two confirmed critical points no instruction prompted (throughput not
limited above the sailing floors; crude routed by barge instead of pipeline). Its limits: (1) it repeated the
reference's one false alarm, and the editor put it on the before-submission list; (2) points needing outside sources
(survey contents, a competing model's features) and framing-level requests are missed; (3) the synthesis drops detail
that three referees raised, so read the four reports too; (4) the reference is itself one AI review and two of its
points were prompted by the common checklist, so this is agreement with a strong AI reviewer on what the text exposes,
not a validation against journal referees. The editor instructions gained a materiality test and a no-drop rule after
this backtest (both marked in `editor_synthesis.md`); the next backtest should use a reference the instructions'
author has not read: the record of the 5 October review was opened while the instructions were written, the reviews
of 8 October (d1e453e) and 12 October were not, beyond their mention in the project notes. All referees and the editor passed
the independence audit (bundle and instructions only, no shell or web).
