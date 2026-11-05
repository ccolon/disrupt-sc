# Phase 1 - options synthesis

Read `state.yaml`, `gap/material.md`, `gap/graph_seed.yaml`, `lit/review.md`, `lit/refs.yaml` (and the citation
gate report `lit/cite_check.md`), `gap/scoop.md`, `gap/venue.md`.

Write `<project>/gap/options.md`:

1. **Situation in five lines**: the claim, what the material supports today, the novelty verdict, the venue fit,
   the time left before the deadline.
2. **Option list.** Generate 5-7 candidate options (claim refinement x venue), then keep the **three most
   promising**. For each of the three:
   - draft title and a mock abstract (at most 150 words, numbers as `[X]` where results are not yet known);
   - the main figures (3-5), one line each;
   - what is missing: the new evidence/analysis/run nodes, each with effort (person-days, CPU hours) and the
     risk that it fails; total effort and whether it fits the deadline with margin;
   - novelty: the delta against the three closest works (keys), and its weakest point;
   - venue: fit, prestige, speed; why this venue for this framing;
   - what could kill it, and the fallback;
   - a score out of 5 on novelty, feasibility before the deadline, venue fit, and expected acceptance chance, with
     one line of justification each.
3. **Comparison table** of the three, and a recommendation (one paragraph).
4. **Decisions for the user**: what must be decided at gate A, with the default.
5. **Rejected options**: one line each, why.

For each option's headline, check in the model code whether the effect could hold or vanish by construction
(relative thresholds, quantities that rescale with the baseline, parameters that cancel); if so, add a cheap pilot
with its acceptance rule written before the run, and make it part of the go/no-go. (Cambodia pilot: a carbon price set
in the config becomes the baseline, and the give-up rule is relative, so a uniform multiplier gives the
proportional null by construction.)

Effort estimates: base them on the material audit (what exists) and on the run times visible in the material, not
on optimism; state the assumption (e.g. one researcher full time, cluster available).
