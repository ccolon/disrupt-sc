# Backtest: how much of an earlier review did the panel find?

You compare the panel's output on an earlier version of a manuscript with a review that version actually received.
You read: the panel's four reports and the editor's synthesis (paths in your task), the reference review (path in
your task), and the list of reference points with the authors' verdict where known (in your task: `confirmed` = the
authors verified it and changed the model, the analysis or the text; `rejected` = checked and found not to hold;
unlabelled = no recorded verdict). Do not open anything else.

## Matching rule (strict)

For every point of the reference review, find the panel point(s) that raise **the same problem**: the same mechanism,
quantity or comparison, and the same consequence for a conclusion. Then classify:

- **FOUND**: a panel point states the same problem; wording may differ. Example: reference "the calibration target
  is not the same quantity as the model output" and panel "the model's all-sector loss is compared with an
  industry-only statistic": FOUND.
- **PARTIAL**: the panel touches the same area but states a vaguer or different problem, or names the problem without
  its consequence. Example: reference as above, panel "the validation is weak and needs more benchmarks": PARTIAL.
- **MISSED**: nothing in the panel's reports raises it.

Topic overlap alone is not a match. Quote the panel's words (at most 20) that justify FOUND or PARTIAL, with the
report and issue ID (e.g. R3 M2, synthesis P4). A point found by a single referee but dropped by the editor still
counts as FOUND, and you note that the editor dropped it.

## The other direction

List the panel's consolidated points (synthesis P1, P2, ...) that match **no** reference point: these are the
panel's own findings. For each, say whether the manuscript text in the bundle supports it (`checkable in text: yes /
no`), without judging whether the authors would agree.

## Report

Markdown, to the path in your task:

```
# Backtest of the panel on <version>

## Recall
| | points | FOUND | PARTIAL | MISSED | recall (FOUND + PARTIAL/2) |
|---|---|---|---|---|---|
| all reference points | | | | | |
| confirmed by the authors | | | | | |
| critical in the reference | | | | | |
| rejected by the authors (found = false alarm shared) | | | | | |

## Point by point
| reference point | severity | verdict | panel point(s) | evidence |
|---|---|---|---|---|

## The panel's own findings
| panel point | checkable in text | note |
|---|---|---|

## Reading
(one paragraph: what kinds of problem the panel finds and misses; what the result says about trusting it)
```

Your final reply in the conversation is at most 100 words: the recall figures.
