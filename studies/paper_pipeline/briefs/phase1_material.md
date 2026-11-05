# Phase 1 - material audit

Goal: what the existing material supports, how solid it is, and what reusable pieces exist.

Read: the manuscript (all `.tex`, the `.bib`, the figure list), any SI, the code/config/scripts and run listings
named in `state.yaml` (or copies in `<project>/gap/`), and model documentation where needed.

Write `<project>/gap/material.md` with these sections:

1. **Claims the draft makes.** Numbered list: the claim as written (`file:line`), its kind (headline / supporting /
   context), and the figure, table or number that supports it.
2. **Evidence and provenance.** For each figure and table: what it shows, which runs/config/script produced it if
   identifiable, whether that can be reproduced from what exists (config + code + outputs), and gaps in provenance.
3. **Defects and risks.** Inconsistencies between text, figures, config and scripts (wrong parameters, scenarios
   that do not do what the text says, horizon truncation, typed numbers that disagree, missing robustness, units).
   For each: evidence, consequence for the claims, severity (critical / major / minor), the fix and its effort.
4. **What is reusable.** Runs, figures, text sections, code, data that a revised paper can use as they are.
5. **Numbers typed in the text.** A count, and the ten most important ones with their source if known.

Standard checks for simulation results (each found a critical defect in the Cambodia pilot): read the run outputs,
not only the configs; check that all runs pooled in one figure share horizon, seeds and configuration; check that
the losses of every simulated shock settle within the horizon (daily loss back near zero after the shock ends);
check that the scenario definitions actually run are the ones the text describes (look in the run logs).

Also write `<project>/gap/graph_seed.yaml`: the current draft as an evidence graph (format in RUNBOOK.md), with
statuses reflecting what actually exists (`done` only if the output exists and is reproducible).
