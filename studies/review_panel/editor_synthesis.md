# The editor's synthesis of the panel

You are the handling editor. Four independent referees have reported on a manuscript; you write the decision letter
the authors will work from. You may read the reading bundle (`paper.txt`, `figures/`) to check what the referees
say, and the four reports named in your task. Do not open anything else on this machine and do not search the web.

## What to do

1. Read the four reports in full.
2. **Consolidate** their major issues into distinct points: merge the ones that describe the same problem (same
   mechanism or quantity, same consequence), keep apart the ones that only share a topic. Record who raised each.
3. **Check each consolidated point against the manuscript** (`paper.txt`): is the referee right about what the paper
   says? Mark each point `verified` (the text shows the problem), `misread` (the paper already does or says what the
   referee asks; give the page) or `unverifiable from the text` (needs the authors' data or code). Referees misread;
   your check is what makes the letter worth acting on.
4. Note where referees **disagree** (one sees a strength where another sees a flaw) and say which reading the text
   supports.
5. **Materiality.** For each point, say whether fixing it could plausibly change a headline number or a conclusion,
   and by how much if the text lets you judge. A check that is cheap but likely immaterial (a robustness test the
   paper's own numbers suggest will move little) goes in the letter as "check, likely immaterial", never on the
   before-submission list. (Added after the first backtest, 5 Nov 2026: the panel repeated a reference false alarm,
   a daily-vs-weekly averaging test the authors had found to move the loss by less than 1 %.)
6. **Do not drop a shared point.** A problem raised as a major issue or a recurring minor issue by two or more referees
   is a consolidated point, even when you rate it lower. (Added after the first backtest: three referees asked for the
   inventory and recovery rules to be specified and the synthesis dropped it.)
7. Decide: accept, minor revision, major revision or reject.

## The letter

Markdown, at most **2,000 words**, to the path given in your task:

```
# Editor's synthesis

## Decision
(decision, and two or three sentences on why)

## Consolidated points
| ID | Point | Raised by | Severity | Check | Material | Type | Where |
|---|---|---|---|---|---|---|---|
| P1 | ... | R1, R3 | critical | verified | yes: headline | analysis | p. 4, Fig. 2 |
(severity = the highest any referee gave it, unless your check changes it; material = yes (what it could change) /
likely not (why) / unclear; type = text / analysis / both)

### P1. <title>
What is wrong, why it matters for which conclusion, and the specific change or test that would settle it (the
falsifiable version: what result would show the authors right or wrong).
(repeat for every point, most consequential first)

## Disagreements between referees

## Before submission
(at most 8 items, ordered by consequence: what must be done before this goes to a journal)

## Minor points
(grouped by kind: consistency of numbers and words, presentation, references, figures)
```

Your final reply in the conversation is at most 120 words: the decision and the IDs and titles of the critical points.
