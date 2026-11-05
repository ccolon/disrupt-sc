# Report of Referee R1: supply-chain disruption modelling (agent-based and input-output dynamics)

## Summary of the claims
The paper simulates the 2026 Rhine low water with an EU-wide agent-based supply-chain model with cargo-class routing on TEN-T, in which a weekly Kaub gauge sets surcharges and closes vessel classes below fixed floors. One parameter, a stock-target multiplier, is calibrated on 2018; 2018 timing and ex-ante estimates of August 2026 serve as validation. It claims that losses come from stock-outs, not freight costs; that the second wave cost three times the first because buffers could not refill; that most lasting loss falls on fuel-fed services; and that a low-water fleet beats fairway deepening and stocks while cheaper rail does nothing. The German loss is 0.54 % of a quarter's value added (draws 0.31–0.76).

## Assessment
Putting mode choice, rerouting and give-up decisions by cargo class inside a firm-level propagation model at EU scale is a real advance on region-keyed ARIO/MRIO treatments, and the paper is frank about several limits (binary closures, crude by barge, a calibration that builds in the buffer result). The arithmetic I could check holds (ensemble mean and sd from Fig. 6, sector and EU shares, lever percentages). The chain of evidence does not yet hold, for five reasons. The calibration target and the model's matched loss are different quantities. The loss runs through a refinery-to-services channel that the missing pipeline mode may create. Several abstract-level "findings" restate the rules. The validation could not have rejected the model. And the ranking rests on one draw under one rule set.

## Major issues

### M1. The calibration target and the model's matched loss are different quantities — critical
- Where: p.2 (refs 6–7), p.3, p.5 "Who loses", p.10 Calibration; Fig. 4b.
- Text: "about 1 % of German industrial production per month of low water" (p.2)
- Problem: The ex-post evidence is an industrial-production response; the "0.3–0.4 %" GDP effect is presumably its translation into GDP. The paper does not say whether it is a share of annual GDP, of Q4 or a cumulated loss, nor how it became "% of a quarter". The model hits it with a 2018 loss of which 85 % lies in services and utilities (p.5). Its goods-sector loss is therefore about 0.15 × 0.32 ≈ 0.05 % of a quarter of total VA, roughly 0.6 % of one month of industrial output cumulated over the whole event (industry ≈ a quarter of GVA). Ref. [6] implies about 3–5 month-percent (≈1 % per low-water month, 1.5 % in November). By my rough arithmetic the model under-predicts the measured variable by a factor of ~2.5–4 if energy is in the index, ~5–8 if not.
- Why it matters: the total is matched through a sectoral composition the evidence does not show. The calibrated multiplier, the "validated" claim of the abstract and the "who loses" result all rest on it.
- Resolution: [analysis] Report the model's monthly 2018 production loss over the sector coverage of ref. [6]'s index, August–December, against the estimated response and its confidence band; state exactly what 0.3–0.4 % measures and show the conversion; recalibrate on the like-for-like quantity. Show evidence for the service-sector losses (M2).

### M2. The loss runs through a refinery channel the model may create — critical
- Where: p.5, p.7; Figs. 3, 5.
- Text: "every transport operator and gas-fired plant in the country ... runs short at once" (p.5)
- Problem: Four fuel-fed service sectors carry four fifths of the German loss after inland refineries stop. The paper concedes it routes crude "by barge for want of a pipeline mode"; to my knowledge the large refineries upstream of Kaub are pipeline-fed. Gas-fired plants burn natural gas, not refinery output: the link is the aggregate C19→D35 coefficient rated critical. The loss is almost all liquid bulk. Fairway +20 cm, which by Fig. 2 also lifts every dry-bulk week above the 30 cm floor, removes 41 %; tank barges to 40 cm, which only remove the weeks 15–16 tank closure, remove 39 %. Seven dry-bulk closure weeks are thus worth ~2 %. At the peak (1.4 % of weekly VA) the p.5 shares imply weekly output falls of roughly 10–20 % in German power generation, road haulage and warehousing (each ~2 % of GVA). Generation data and the truck-toll index would show such falls; I know of none in late 2018.
- Why it matters: the anatomy, the 83 % "lost for good", the total and the lever ranking all pass through this channel.
- Resolution: [analysis] Rerun 2018 and 2026 with pipeline-fed refineries off the river and D35's critical inputs restricted to fuels it burns; recalibrate; report total, anatomy and ranking. [analysis] Compare the implied weekly falls in D35, H49 and H52 with ENTSO-E generation and the Lkw-Maut index for Oct–Dec 2018 and Sep–Oct 2026.

### M3. The "calendar" result: miscounted closures, untested attribution, forecast inputs on a threshold — major
- Where: abstract; p.2; p.4; p.9 Scenarios; Figs. 2, 4c, 5, 6.
- Text: "the tank-barge closure ... lasted seven weeks instead of four" (p.4)
- Problem: (a) Methods and Fig. 2 give tank-barge closure in weeks 12–16, five weeks, not seven. (b) The refill explanation is untested. The second-to-first wave ratio is 3.2 at ×1 (2.16 vs 0.51), 1.9 at ×1.5 (0.82 vs 0.28) and 3.2 at ×2. That is non-monotone in buffer size, which a refill mechanism does not obviously predict. The tank-barge-to-40 cm run shows weeks 15–16 alone carry ~40 % of the total: duration, not refill, may do most of the work. (c) Those weeks (42 and 49 cm against a 50 cm floor) come from the median BfG outlook. Week 16 is 1 cm from the threshold on a weekly mean, so a 1–2 cm error can move the headline by ~40 %. (d) Between the waves the river carries 38–50 % of normal capacity (Fig. 2b), yet the model refills above baseline tonnage (p.5): the refill is optimistic.
- Why it matters: "priced by its calendar" is an abstract claim.
- Resolution: [analysis] Decompose: the second wave alone from steady state; both waves with a longer gap; the first wave with a five-week tank closure. Use observed gauges and the BfG ensemble members rather than the median, and daily gauges (share of days below the floor) rather than weekly means. [text] Correct "seven".

### M4. Several headline findings follow from the rules — major
- Where: abstract; pp.4–6; p.9; p.10; SI S8.
- Text: "no shipper in the model gives up a delivery on price" (p.4)
- Problem: Under the p.9 rules a surcharged shipper pays or reroutes and cannot give up. Capacity is not modelled, so surcharged weeks move full tonnage: 29 cm (24 % capacity, Fig. 2b) counts as zero, 52 cm (38 %) as 100 %. The loss metric (p.10) counts production shortfalls only, so freight costs cannot enter it. "Stock-outs, not freight bills" is therefore built in. Cheaper rail cannot act because a bulk modal switch is prohibitive (SI S8: "inert by construction"), yet the abstract ranks it. Removing closures removes all loss by construction, which drives the fleet and package results. The "lost for good" service share is an accounting convention.
- Why it matters: four abstract claims are assumptions, and the discovered content is smaller than stated.
- Resolution: [text] Label these as consequences of the rules. [analysis] Compute the extra freight bill (Δcost × tonnage, same USD) beside the stock-out loss. Replace the rail lever with a capacity-limited partial switch (e.g. DB Cargo's ~200 barge loads, ref. 22) and report what it removes.

### M5. The validation could not have rejected the model, and the degrees of freedom are undercounted — major
- Where: pp.3–4, p.7, p.10; Fig. 4; SI S4, S6.
- Text: "Two facts the calibration did not use support it." (p.4)
- Problem: (a) The 2018 peak falls in the same week at every multiplier (p.3), so timing does not test the parameter: the input closure schedule plus a buffer lag sets it. p.10 lists peak timing in the calibration comparison, no failure criterion is stated, and the missed late-summer onset (p.7) is explained away. The thyssenkrupp marker (Duisburg, below Kaub) is a channel the model lacks: the Lower Rhine never closes. (b) The August 2026 ex-ante figures are model projections, partly from the institute whose 2018 estimate is the target. ×1.5 (0.28) also lies in 0.1–0.35, so the check rejects only ×1, which 2018 already rejects. They concern Q3 GDP, while the model window (weeks 7–11) omits September. (c) The tonnage checks set national monthly year-on-year tonnage against weekly Kaub flows, and delivered tonnage of baseline Kaub links against physical passages; the real reach thinned, it did not close. (d) Also set with 2018 in view: the materiality floor ("without which negligible cross-border service inputs cascade"), the switching thresholds (SI S4 "calibration log"), the tank floor (SI S6 "cross-check") and ×2 at the grid's top. (e) Calibration uses the reference draw (0.32) while the ensemble mean (0.30) sits at the lower edge. Fitting the midpoint on the ensemble gives ≈×1.85 and, interpolating Fig. 6, a 2026 loss of ~0.6–0.7 %, a band that is not propagated.
- Resolution: [analysis] State failure criteria now for the 2026 ex-post data (e.g. monthly industrial loss, Sep–Nov); compare Q3 with Q3; calibrate on the ensemble or per draw and propagate the band; report the 2018–2026 correlation across draws. [text] List every choice made against 2018.

### M6. The adaptation ranking rests on one draw and one rule set — major
- Where: pp.5–7; Figs. 5–6; p.2.
- Text: "every result is reported over an ensemble of independent draws" (p.2)
- Problem: The levers are run on the reference draw only, and "wider than the effect of every adaptation" sets an unconditional level band against paired differences. Structural variants are not recalibrated, so "pooling halves the loss" compares a calibrated model with an uncalibrated one. Under capacity thinning (deliveries capped at load factor × fleet capacity), the fairway, which raises capacity in every week (Fig. 2b: ~9 % to ~25 % for 11→31 cm), would gain on the fleet; with pipelines every lever shrinks. The fleet lever is the whole bulk fleet and is uncosted, so the levers are not "priced against each other" (p.7).
- Resolution: [analysis] Run all levers on all eleven draws and report paired effects with ranges and rank frequencies. Recalibrate each structural variant on 2018 (thinning, no pooling, "important" inputs binding at half weight, materiality floor 1 % and 5 %, pipelines) and report the 2026 total and ranking under each.

### M7. The results cannot be reproduced from the submission — major
- Where: pp.8–10, 20; references.
- Text: "Runs, job lists and analysis scripts are in studies/rhine2026" (p.10)
- Problem: The SI is an outline. Rates, stock targets, the poolable list, firm sources, the low-water loading table and the run count are placeholders. The code tag and data package are missing, references carry "VERIFY" notes and internal file names, Fig. 2c, Fig. 3b and the Fig. 1 inset are missing, and † numbers are still to be refreshed.
- Why it matters: no reader can rebuild or audit the runs.
- Resolution: [text] Provide the full SI, the tagged code, the configurations and the data package.

## Minor issues
m1. p.3 — ×2 is read as "all inventories" while raw materials are "about a third" (implying ×3). Suppliers' finished goods sit beyond a closed reach, and the 2018 reserve release is folded into ×2 (was there one in 2026?). Call ×2 an effective buffer.
m2. p.8 — give suppliers per input and region, spare capacity and the refill rule; the one-fifth backlog recovery depends on them.
m3. p.10 — is above-baseline output by substitute suppliers netted? Justify the 13 % delay rate.
m4. p.4 — the households' 5.4 bn and the VA's 5.2 bn are not additive; say so.
m5. pp.4, 8 — USD (2022 ICIO) and EUR (2026) are mixed; compare shares and state the price base.
m6. pp.4, 6 — a share of agents (~9 per region-sector) is not a share of firms; "no output-based model reaches it" is unsupported.
m7. p.5 — the Dutch refinery loss assumes output cannot be redirected by sea.
m8. Figs. 2b, 3 — Fig. 2b shows a capacity the model does not use; Fig. 3's colour scale appears to saturate at 1.6 %.
m9. p.8 — "important" inputs (21 %) are non-binding; Pichler et al. offer a half-weight variant.

## Internal inconsistencies
- pp.2, 4 "tank barges for seven" vs p.9 "tank barges in weeks 15–16" after the weeks 12–14 closures, and Fig. 2: five weeks.
- p.10 calibration compared "with the peak of the losses in late November or early December" vs p.4, where timing is a fact "the calibration did not use".
- Abstract "reproduces the timing of the 2018 losses" vs p.7 "losses start only in mid-October while the production index was already falling".
- p.10 switching rule and Lower Rhine factor "reported as sensitivity" vs Fig. 6, which has neither.
- p.7 pooling "halves the loss" vs p.5 0.86→0.54 (−37 %); in 2018 0.45→0.32 (−29 %).
- pp.5–6 fleet "the closures disappear and only the surcharges remain" vs Fig. 2 weekly means of 11 and 12 cm, below the 20 cm floor; Fig. 5 shows residual fleet losses in weeks 9–10 and 14.
- p.5 "five adaptations (Fig. 5)" vs six bars plus an unplotted rail run.
- p.5 "doubling it removes three quarters": no ×4 run appears on p.10 or in Fig. 6.
- p.3 the baseline "reproduces ... the tonnage profile of the Rhine" vs p.9: 68 Mt against 50–60 Mt, containers by rail.
- p.5 loss "across the whole country" and p.7 pooling "spreads the shortfall nationally" vs Fig. 3: the loss sits in the south, most of Germany is in the lowest bin, hard to square with a 1.4 % national peak.
- p.4 "peak always in weeks 15–17 (Fig. 6)": Fig. 6 has no timing. The Fig. 2 caption's floors, forecast flags and panel (c) are absent from the figure.
- Fig. 5: the lever runs end at week 31, the base at 39 (p.9), so net losses are taken at different horizons.
- p.4 "other ex-ante estimates of 0.2–0.35 points [8, 20]": ref. 20 is the DIHK survey; Commerzbank (Fig. 4c) has no reference.

## Recommendation
Major revision; confidence 4.

Answers to the brief:
1. Two assumptions drive the numbers: binary closure with a prohibitive bulk modal switch (no thinning, no pipelines), and the stock rule (industry days ×2, short buffers for fuel-fed services, fuel critical and pooled nationally). No run removes either.
2. As designed, the validation could not reject the model. It would fail on a monthly industrial loss outside ref. [6]'s band, on power or haulage data without weekly falls, or on a Q3 2026 loss outside 0.1–0.35.
3. The ranking is robust to neither: it is shown on one draw, and fleet ≫ fairway and rail = 0 follow from the binary closures.

The changes that would most move my recommendation:
1. The like-for-like sectoral comparison with 2018, plus a pipeline-corrected, recalibrated rerun.
2. A recalibrated thinning variant, with the levers run on all draws.
3. The calendar decomposition on observed gauges.
