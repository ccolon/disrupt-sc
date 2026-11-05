# Reference for the backtest of 5 Nov 2026: the review of 22 September 2026 on Overleaf ce22110

Reference review: `C:/Users/Celian/Downloads/Nature_Communications_review_2026-09-22.md` (ChatGPT, "four disciplinary
reading passes by one AI reviewer", on Overleaf commit ce22110617da6744bf1f57b6fba8b5d466764966). Not committed here:
it lives in the author's Downloads folder.

Verdicts are taken from the project's records (the session memory of the Rhine paper, the review responses of
October, the calibration log); `confirmed` = verified in the study's own outputs and acted on (model, analysis or
text), `rejected` = checked and found not to hold, blank = no recorded verdict. The author may correct them.

| point | title (short) | severity | verdict | record |
|---|---|---|---|---|
| OR1 | bulk substitution and the rail conclusion inseparable by construction | critical | confirmed | bounded rail substitution sensitivities (50 / 140 kt) and no-rail runs added; "rail inert" dropped |
| OR2 | reduced payload must constrain throughput before closure | critical | confirmed | capacity gate adopted 22-23 Sep (the gate fixes the onset) |
| OR3 | missing pipelines compromise the fuel mechanism | critical | confirmed | pipeline audit 22 Sep; `pipelined_flows` rule (crude by pipeline) |
| OR4 | baseline transport validation overstated | major | | baseline residuals reported (SI S2) |
| OR5 | synthetic firms and pooling need justification | major | | |
| OR6 | inventory and recovery dynamics not reproducible from Methods | major | | |
| OR7 | adaptations need a common feasible basis and paired comparisons | major | | paired lever ensembles added (T8) |
| NS1 | observations, forecasts and assumed recovery must be separated | critical | confirmed | the September forecast proved wrong; forecast flagged and frozen on 30 Sep |
| NS2 | gauge height is not navigable depth or fleet capacity | critical | | loading table provenance rebuilt later (6 Oct) |
| NS3 | weekly averaging can change closures | major | rejected | daily vs weekly < 1 % (29 Sep) |
| NS4 | calendar hypothesis not isolated by comparing the two waves | major | confirmed | wave isolation runs: the second wave alone costs less than the first; text corrected |
| NS5 | closure and adaptation descriptions internally inconsistent | major | | |
| NS6 | fleet feasibility and environmental trade-offs | major | | |
| NS7 | independent validation must match the physical quantity and geography | major | | Kaub tonnage vs Destatis compared |
| EC1 | calibration target has no demonstrated mapping to the model outcome | critical | confirmed | matched estimand 22 Sep: the 2018 match was coincidental (all-sector vs industry-only) |
| EC2 | "one parameter" understates influential assumptions | major | | |
| EC3 | validation claims stronger than the evidence | critical | | |
| EC4 | prices, real output and welfare conflated | major | | |
| EC5 | loss and recovery accounting needs identities | major | | horizon checked: converged |
| EC6 | service concentration may be driven by aggregation and routing | critical | confirmed | real-estate loss was the construction stock rule; construction made non-storable (30 Sep) |
| EC7 | "fleet dominates" is not an investment conclusion | major | | efficacy vs cost wording |
| EC8 | baseline year and measured economy must be explicit | major | | |
| G1 | narrow and substantiate the novelty claim | major | | |
| G2 | convert four rhetorical claims into falsifiable propositions | major | | |
| G3 | reproducibility is an outline | critical | | code release still open |
| G4 | treat failed validation as evidence | major | | |

## Leakage note

The panel's common instructions (`studies/review_panel/referee_common.md`) were written on 5 Nov 2026 by an assistant
that had read this review's outline and the project's history. Two of its generic checks, "like-for-like
comparisons" and "finding or assumption", are standard referee practice but correspond to EC1 and OR1: recall on
those two points is prompted, not blind. Two example phrases that pointed at OR1 and OR3 were removed from the
instructions before the run. The referee briefs name the expertise (methods, transport, economics, editor), which
mirrors the reference review's four perspectives.
