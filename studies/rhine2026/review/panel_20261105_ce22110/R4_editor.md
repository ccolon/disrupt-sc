# Report of Referee R4: handling editor's reading (Nature Communications), generalist

## Summary of the claims

The paper simulates the 2026 Rhine low-water season with a firm-level agent-based supply-chain model of the EU. Shipments are routed on the TEN-T multimodal network, and a weekly Kaub gauge sets surcharges and closures by vessel class. One parameter, a multiplier on input-stock targets, is calibrated on the 2018 low water. The model is then said to reproduce the 2018 timing and the ex-ante estimates of the August 2026 closure. It puts the 2026 cost at 0.54 % of a quarter of German value added (USD 5.2 bn) and makes four claims:
- losses come from stock-outs, not freight costs;
- the September–October trough cost three times the August one because buffers could not refill;
- most of the lasting loss falls in fuel-dependent services;
- a low-water bulk fleet removes 95 % of the loss, fairway deepening or extra stocks about 40 %, and cheaper rail nothing.

## Assessment

Rhine low water is a recurrent threat to Europe's industrial core, and climate change makes it more likely. The paper follows a gauge reading through vessel classes, routes, stocks and firms to national value added, at EU scale and within weeks of the event. That would interest readers well beyond the field.

What is strong:
- the mechanism is explained in plain causal language;
- the paper admits the buffer result is "partly built into the fit" (p.6);
- it reports an ensemble of supply-chain networks;
- Figs. 4b and 5 are clear;
- the delivered-price analysis (pp.4–5) is evidence a reader can check.

The novelty claim goes further than it can defend. Supply-chain models with a transport layer already exist: the authors' own ref. [19], and port-disruption studies that couple transport and trade networks. "Inventories, not freight costs" restates ref. [15] and the modest freight-cost losses found in refs. [9–11]. The genuinely new parts, the calendar effect and the sector breakdown, are also the most fragile (M2, M3, M5, M6).

A broad reader should take away one sentence: Rhine bulk cargo has no rail or road substitute at volume, so a low-water season costs whatever inventories cannot cover, and the spacing of closures and vessels that can still sail matter more than how low the river falls. The abstract does not deliver that sentence:
- it opens with model counts;
- it carries daggers marking provisional numbers;
- it uses an unfamiliar unit with no money figure;
- it presents results that follow from the model's structure as findings.

## Major issues

### M1. The submission is an internal draft, not a manuscript ready for review — critical
- Where: abstract (p.1); pp.2, 5, 9–10; figure legends pp.14–19; SI p.20; references pp.11–13.
- Text: "† marks a 2026 number that the final batch (event end, November 2026) refreshes"
- Problem:
  - The headline numbers are declared provisional.
  - The second wave is simulated on the 7 September outlook median plus assumed values (p.9).
  - Figs. 2c and 3b and the Fig. 1 inset are placeholders.
  - The SI is only an outline. It cites internal files ("validation_outputs.py", "compare_runs_batch_…csv", a "calibration log").
  - Supplementary Figs. S1–S3, on which the baseline validation rests (p.3), are missing.
  - About ten "[cite …]" placeholders and as many other bracketed gaps remain. Eight references carry "VERIFY", and refs. [8] and [20] contain internal file paths.
  - The data and code statements, the release tag, the run count and the author list are blank.
  - The Results contain notes to self (p.5).
- Why it matters: no conclusion can be checked. The central novelty, the second wave, has not yet been simulated on observations.
- Resolution:
  - [analysis] Rerun on the observed gauge to the end of the event.
  - [text] Complete the figures, the SI (parameter tables with sources, S1–S3, mechanism tests), the references, and the data and code statements, with a tagged release and archived inputs.

### M2. Closures are the only way quantities can fall, so three of the four findings follow from model structure — critical
- Where: pp.4–6 ("Stock-outs", "Adaptation"); p.7; Methods p.9; Fig. 2b.
- Text: "a surcharged week moves the full tonnage at a higher price"
- Problem:
  - Quantities fall only when a vessel class is closed. Partial loads do not limit throughput, and links have no capacity limits (p.9).
  - Between the closures, refill "lifts dry-bulk tonnage above" baseline (p.5). In those weeks Fig. 2b puts fleet capacity at 38–50 % of normal.
  - Consequences:
    - (i) "Stock-outs, not freight bills" is an assumption, not a finding.
    - (ii) "Calendar, not depth" is largely built in. Below a class's sailing floor, 25 cm and 5 cm are identical, and at that capacity refilling between the troughs is physically impossible.
    - (iii) The fleet's 95 % simply removes the only way losses enter the model.
    - (iv) The 2018 calibration attributes to the October–December closures a loss that began under surcharges in August (p.7). The buffer multiplier therefore absorbs the missing mechanism.
  - The limitation is stated (p.7), but its effect on the findings is not evaluated.
- Why it matters: findings 1, 2 and 4 may change in size or rank.
- Resolution:
  - [analysis] Cap weekly Kaub throughput per class at the draught-table capacity, recalibrate on 2018, and report the four findings under the cap.
  - [text] Label finding 1 and the rail result as properties of the model.

### M3. The model matches the 2018 target with a sector mix that contradicts the evidence behind it — critical
- Where: pp.2, 3, 5, 10; Fig. 4b.
- Text: "about 1 % of German industrial production per month of low water"
- Problem:
  - By the paper's own account, the ex-post evidence is an effect on industrial production (trough 1.5 % in November).
  - It is translated into a GDP effect "of the order of 0.3–0.4 %", with no period or base given (p.2). Page 3 reads it as "% of a quarter".
  - The model matches that total with a loss that is 85 % services (2018, p.5). Its goods-sector loss is therefore about 0.05 % of a quarter, several times below what a 1 %-per-month industrial loss implies.
- Why it matters: one of two things must be true.
  - The buffer is mis-calibrated. Matching industrial output needs smaller buffers and a larger total, and that would fail the August 2026 check (×1 gives 0.51).
  - Or the services headline contradicts the evidence the target comes from.
  - Either way, both the level and the sector headline are at stake.
- Resolution:
  - [analysis] Compare the model's monthly industrial loss (NACE B–D, with the production index's weights) with the monthly estimates of Ademmer et al. for 2018.
  - State the period and base of the 0.3–0.4 % and compute the model's equivalent on the same base.
  - Test the 2026 run against the Destatis August–November 2026 production indices, the out-of-sample test the Discussion announces.

### M4. "Validated" overstates what are four consistency checks — major
- Where: pp.3–4, 6, 10; Fig. 4; SI S5.
- Text: "the peak stays in the first week of December at every multiplier"
- Problem:
  - (a) Timing does not depend on the parameter, so it cannot validate it; it reflects the input closure schedule.
    - Model losses start in mid-October, although production fell from late summer (p.7).
    - The model's peak comes after the observed November trough, and the target was widened to "late November or early December" (p.10).
    - A weekly peak is being compared with a monthly trough.
  - (b) The August 2026 check is against forecasts, not observations.
    - The Kiel estimate dates from 28 July, before the record low, and comes from the same institute whose 2018 estimates define the target (refs. [7], [8]).
    - It cannot tell ×1.5 (0.28) from ×2 (0.13): both fall within the 0.1–0.35 range on p.2.
  - (c) The tonnage matches compare different quantities.
    - Kaub is closed to every class in the comparison week, so the model's −81 % and −70 % are the delivered share of Kaub-route flows, rerouted ones included. Operators counted barges that actually passed a low but open river.
    - The 2018 check sets Kaub against all German waterway tonnage, year on year.
    - The survey comparison uses the model's peak week, not the survey week.
  - (d) "One parameter" undercounts the choices made knowing the outcome.
    - The ladder stops at ×2, although raw materials are "about a third" of inventories, so all inventories would be about ×3.
    - The 2 % materiality floor was added because inputs "cascade".
    - SI S4 cites a "calibration log" for the switching thresholds.
- Resolution:
  - [text] Call these consistency checks, and tabulate every parameter with its source and whether it was set before or after the 2018 runs.
  - [analysis] Add ×3 to the ladder, and redo (a)–(c) on matching quantities: calendar months, barges that physically pass Kaub, the same base.

### M5. The "three times" second wave rests on forecast weeks, a 1-cm margin and an explanation that is not tested — major
- Where: abstract; pp.2, 4, 6, 9; Figs. 2 and 5.
- Text: "A low-water season is priced by its calendar, not by its minimum gauge."
- Problem:
  - Every second-wave gauge value is forecast or assumed (p.9).
  - The costliest weeks (16–17, Fig. 5) follow the closure of weeks 15–16, which applies to tank barges only. Week 16 reads about 49 cm (Fig. 2) against a 50-cm floor, and the 40-cm floor alone removes 39 % of the loss.
  - The factor of three is attributed to two causes, short refill and a longer tank-barge closure, without separating them.
  - The closure length is stated inconsistently (see Internal inconsistencies).
- Resolution: [analysis]
  - Use the observed gauge.
  - Use the BfG ensemble quantiles rather than the median.
  - Add two decomposition runs: the same second trough shifted later, and equal tank-barge closure lengths. Together they apportion the ratio between refill and duration.
  - Report the ratio between the two waves across the eleven draws.

### M6. The fuel chain behind the services result rests on representations the paper admits are wrong — major
- Where: pp.5, 7–9; Fig. 3.
- Text: "routes crude to inland refineries by barge for want of a pipeline mode"
- Problem:
  - The services' four fifths follow from refineries upstream of Kaub stopping and from a single national fuel pool. In reality those refineries are fed by pipeline.
  - "Every … gas-fired plant" is said to run short of refinery output (p.5).
  - Power output is treated as tied to the individual plant, although the grid substitutes other generation.
  - Warehousing's 29 % share is not explained.
  - The text's geography also conflicts with Fig. 3 (see Internal inconsistencies).
- Why it matters: the third headline and the regional results.
- Resolution:
  - [analysis] Add two runs: inland refineries supplied with crude by pipeline (product flows still on barges), and regional fuel pools. Report the German total and the sector shares.
  - [text] Show the input coefficients and criticality ratings that make warehousing and power lose.

### M7. The adaptation ranking is presented as policy without costs, scale or uncertainty — major
- Where: abstract; pp.5–7; Fig. 5; SI S8.
- Text: "a low-water bulk fleet removes 95 %"
- Problem:
  - The fleet lever converts the entire tank and dry-bulk fleet to vessels that sail to 20 cm. The real lever the paper cites is nine tankers plus seven planned (p.7).
  - No lever has a cost.
  - Rail is inert by construction (SI S8), yet "cheaper rail nothing" appears in the abstract as a finding and is missing from Fig. 5.
  - The levers are run on the reference draw only. The draw-to-draw range (0.31–0.76 %) is wider than the gaps between fairway, stocks and tank barges (41, 39 and 39 %).
- Resolution:
  - [text] Give each lever's scale and an indicative cost, or call this an effectiveness ranking. Present rail as a model property, or test a rail-capacity lever instead.
  - [analysis] Run the levers on all eleven draws and report paired differences.

## Minor issues

m1. pp.1, 4 — "% of a quarter's value added" is an unfamiliar unit, and the currencies mix (USD 2022, EUR 2026). Use one currency and give % of annual GDP alongside.

m2. p.4 — "Households lose 5.4 billion USD": say whose households, and that this loss cannot be added to the value-added loss.

m3. pp.2–9 — Several terms are undefined for a broad reader: partially-binding Leontief, pooling, region-keyed, line haul, sailing floor, GlW, materiality floor, coping duration, "perishable" sectors, extensive margin, "draw". Define them; translate "Abladeoptimierung Mittelrhein".

m4. Fig. 1 — The Kaub marker and inset named in the caption are missing, and the network map adds little. Replace it with a schematic of the shipment decision plus a Rhine inset.

m5. Fig. 2 — The panels are not lettered. The caption promises sailing floors and forecast flags that are not drawn. The capacity panel has no caption. The date labels overlap.

m6. Fig. 3 — The title says "t = 16", the caption "mid-October" (week 16 is 5–11 October). Add place names.

m7. Fig. 6 — It mixes ensemble draws with parameter sensitivities; show them separately. Page 4 cites it for peak weeks it does not show.

m8. p.9 — The model's Kaub carries 68 Mt, all bulk, against 50–60 Mt observed, containers included. Discuss how this overstatement feeds the calibrated buffer.

m9. p.5 — "halving the buffer more than doubles the loss": it quadruples it (2.16 vs 0.54 %).

m10. p.5 — Water transport loses because of the closure itself; "all fed by fuel" misclassifies it.

m11. p.10 — Justify the 13 % delay-cost rate and the 90-day coping duration for services.

m12. Title — "cannot be sailed" contradicts p.1, "the river does not close; it thins".

## Internal inconsistencies

- **Record in September.** p.1 "set a new low-water record at Kaub twice, in August and again in September" vs p.4 "for a gauge that was no lower than in August" and p.6 "the second trough was not deeper than the first".
- **Length of the tank-barge closure.** p.2 "the tank barges stayed closed for seven" and p.4 "lasted seven weeks instead of four" vs p.9: closures in weeks 12–14 and 15–16, i.e. five weeks, as Fig. 2 shows.
- **2018 timing.** p.1 "reproduces the timing of the 2018 losses" vs p.7 "its 2018 losses start only in mid-October".
- **2018 peak.** p.3 "with the peak in the observed week" vs p.4 "the industrial-production trough was in November", while the model peaks in the first week of December.
- **What ×2 represents.** p.3 "raw materials are about a third of manufacturing inventories" vs ×2 read as "all inventories" (p.3) and as "the total inventories that the balance sheets record" (p.6).
- **Effect of pooling.** p.7 pooling "halves the loss" vs p.5: 0.86 → 0.54 % (−37 %), and 2018 0.45 → 0.32 % (−29 %).
- **Ensemble coverage.** p.2 "every result is reported over an ensemble" vs levers, sector shares and sensitivities run on the reference draw only.
- **Geography of the loss.** p.5 "across the whole country in the transport and power sectors" and p.7 the model "spreads the shortfall nationally" vs Fig. 3, where the loss is concentrated in the south and south-west and most of Germany is near zero.
- **Largest uncertainty.** p.7 the draw band "is the largest uncertainty of the result" vs the tank-floor band of 0.33–0.75 % (the same width) and ×1.5 at 0.82 % (Fig. 6).
- **Rail in Fig. 5.** p.5 discusses rail among the adaptations of Fig. 5, but Fig. 5 has no rail lever.
- **Rail as a finding.** The abstract states "cheaper rail nothing" as a result vs SI S8 "Why cheaper rail is inert by construction".
- **Fixed mechanisms.** p.3 "Every mechanism above is fixed at its evidence value" vs SI S4 "threshold sensitivity table (from the calibration log of 14–16 Sep)".
- **Low-water mark.** p.1 "below about 77 cm" vs Fig. 2 "GlW 78 cm", and Fig. 2b shows only 72–80 % capacity at 92–101 cm.
- **Observed or forecast.** p.2 "the gauge fell back below 15 cm in mid-September" is stated as observed vs p.9: those weeks are the outlook median.
- **Refill capacity.** p.5 refill at "half loads" lifts tonnage above baseline vs Fig. 2b capacity of 38–50 % in those weeks.

## Recommendation

**Reject in the present form: return to the authors without review, with encouragement to resubmit. Confidence 4/5.**

**Would I send it out now?** No. The draft state alone (M1) would bring it back from referees, and the main novelty, the second wave, has not yet been run on observations. The science is promising and the problems can be fixed.

**What specialists would attack first:**
- that freight costs do not matter and that the calendar beats depth (M2);
- the calibration on an industrial-production target met by service-sector losses, and the "validated" language (M3, M4);
- the fuel chain built on crude delivered by barge and a national fuel pool (M6);
- the 95 % fleet and 0 % rail presented as policy (M7).

**The changes that would most change my recommendation:**
1. A complete manuscript on observed gauges to the end of the event, with SI, data and code.
2. A recalibrated run with Kaub throughput capped at fleet capacity, showing which findings survive, and with the results that follow from model structure labelled as such.
3. A comparison with monthly industrial production, matched by sector and period, for 2018 and, if possible, 2026.
