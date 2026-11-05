# Editor's synthesis

## Decision

**Major revision; not ready for a journal.** The headline runs through mechanisms the paper itself calls wrong or missing: crude delivered by barge into a national fuel pool, and unlimited throughput while the river is open. The calibration target, an industrial-production effect, is matched by a 2018 loss that is 85 % services. Each fix is a specified rerun, so I do not follow R4's reject. But the draft state (P4) alone would bring the paper back from any journal.

## Consolidated points

| ID | Point | Raised by | Severity | Check | Type | Where |
|---|---|---|---|---|---|---|
| P1 | Calibration target (industrial) vs matched loss (85 % services) | R1, R3, R4, R2 | critical | verified | both | pp. 2–3, 5; Fig. 4 |
| P2 | Services loss runs through a fuel chain the paper admits is wrong | R1, R2, R3, R4 | critical | verified | analysis | pp. 5, 7, 9; Fig. 5 |
| P3 | No throughput limit above the sailing floors | R2, R4, R1, R3 | critical | verified | analysis | pp. 4–5, 9; Fig. 2 |
| P4 | Internal draft, not reviewable | R4, R1, R2, R3 | critical | verified | both | pp. 1–20 |
| P5 | Validation could not reject the model | R1, R2, R3, R4 | major | verified | both | pp. 3–4, 10; Fig. 4 |
| P6 | 2026 gauge rests on forecasts and threshold weeks | R2, R1, R4 | major | verified | both | pp. 2, 9; Fig. 2 |
| P7 | Results set by the rules presented as findings | R1, R2, R3, R4 | major | verified | both | pp. 4–6, 9–10; SI S8 |
| P8 | Calendar result untested | R1, R3, R4, R2 | major | verified | both | pp. 2, 4; Figs. 2, 5 |
| P9 | Levers without scale, cost or ensemble | R1, R2, R3, R4 | major | verified | both | pp. 5–7, 10; Fig. 5 |
| P10 | 2022 ICIO base year | R3 | major | unverifiable from the text | analysis | p. 8 |

### P1. Calibration target and matched loss are different quantities
Page 2 cites about 1 % of industrial production per low-water month and "a GDP effect of the order of 0.3–0.4 %" without a base; p. 3 reads it as "% of a quarter". The model matches it with a 2018 loss that is 85 % in perishable sectors (p. 5). Its goods loss is therefore ≈0.05 % of a quarter (R1: 2.5–8 times too small).

In Fig. 4a the model's November mean (≈0.4 % of weekly value added) is close to the November trough in total value added (1.5 % × industry's ~¼). R3's "three times deeper" compares a weekly peak with a monthly mean. The gap is in sector composition and onset, not depth. It carries the multiplier, "validated" and "who loses".

Test: compare the model's monthly 2018 loss for NACE B–D at index weights, August–December, with ref. [6]'s monthly estimates and band, and define the 0.3–0.4 %. Inside the band, the authors are right. More than a factor of two below, recalibrate on that quantity.

### P2. The services loss runs through a fuel chain the paper admits is wrong
Four fuel-fed service sectors carry four fifths of the German loss (p. 5). In the chain behind them:
- crude reaches inland refineries "by barge for want of a pipeline mode" (p. 7);
- "every … gas-fired plant" draws on the refinery pool (p. 5);
- products cannot switch to rail or road (p. 9);
- no haulier's output is tied to the shipments it carries.

Figs. 2 and 5 confirm the loss is liquid bulk. Fairway +20 cm clears all seven dry-bulk closure weeks, yet it removes only 2 points more than the 40-cm tank floor.

Test: rerun both years with pipeline crude, D35's critical inputs limited to the fuels it burns, and products on rail or road up to observed volumes, then recalibrate. Report the total, the anatomy, the ranking, and Kaub tonnage by commodity against CCNR counts (model 68 Mt vs 50–60 Mt). If Q4 2018 generation, toll-mileage and transport-turnover data lack the weekly falls the model implies, the channel is an artefact.

### P3. No throughput limit above the sailing floors
Links have no capacity limits (p. 9), so open weeks move the full tonnage. Between the 2026 waves, refill lifts tonnage above baseline (p. 5) while fleet capacity is 38–50 % (Fig. 2b). The paper's own count contradicts the cliff: in the week of 13 August, 30 % of liquid cargo still passed Kaub (p. 5). The weekly mean gauge was 11 cm, 39 cm below the tank floor.

The refill (P8), the fleet's 95 % (P9) and the 2018 fit all depend on this. The fit loads onto the closures a loss that began under surcharges (p. 7).

Test: cap weekly throughput per class at draught-table capacity times a mobilisation factor fitted to 2018 Kaub tonnage, then recalibrate. Report the 2018 onset, the stocks between the 2026 waves, the wave ratio and the levers, and test out of sample on August 2022. If these move less than the draw band, binary closures suffice.

### P4. The submission is an internal draft
The draft has daggered numbers, ten "[cite …]" placeholders, eight "VERIFY" references, notes to self (p. 5) and an SI that is only an outline. Figs. 2c, 3b and S1–S3 are missing, the code and data statements are blank, and the second-wave gauge values are forecasts (p. 9). R2 misreads Fig. 5: the targeted-stocks run is plotted (29 %).

### P5. The validation could not have rejected the model
- **Timing.** It does not move with the parameter (p. 3) and enters the calibration (p. 10). The model peaks after the November trough (Fig. 4a) and misses the onset (p. 7). thyssenkrupp (Duisburg, below Kaub) lies outside the modelled channel.
- **August 2026.** The check uses ex-ante estimates from the institute behind the target ([6–8]) and compares Q3 with weeks 7–11. ×1.5 (0.28) fails Kiel's 0.1–0.2 but passes the paper's 0.1–0.35.
- **Tonnage.** The check sets rerouted deliveries (p. 5) against vessels counted past Kaub.
- **Choices.** The materiality floor (p. 8), switching thresholds (SI S4) and tank floor (SI S6) were also set with 2018 in view.

Fix: call these consistency checks and calibrate on the ensemble; R1's ensemble fit (≈×1.85) gives ≈0.6 % for 2026. State the 2026 failure criteria now: the monthly NACE B–D loss for September–November, and Q3 against Q3.

### P6. The 2026 input rests on forecasts and threshold weeks
From 10 September the gauge is the BfG median plus assumed values (p. 9). Yet p. 2 narrates those weeks as observed, and Fig. 2 does not flag them. The 39 % that the 40-cm floor removes sits on weeks 15–16 (42 and 49 cm, against a 50-cm floor). R1's "1–2 cm moves ~40 %" overstates, because only week 16 is that close. The floors are unsourced, and the paper does not say which reaches close.

Test: use observed daily gauges, close each class for the share of days below its floor, source the floors, use per-reach gauges, and report the band.

### P7. Results set by the model's rules are presented as findings
- Surcharged shippers must pay or reroute (p. 9).
- The loss metric cannot register freight bills (p. 10).
- Bulk switching is prohibitive, so rail is "inert by construction" (SI S8), yet the abstract ranks it.

R2's "capacity" inconsistency partly misreads p. 6. But the 900-wagon argument sets a stock of wagons against a monthly flow of barges. R3's freight bill of €0.2–0.4 bn (the multiplier-weeks check out in Fig. 2) is a tenth of the headline but equals the goods loss. R4's critical rating attaches to P3.

Fix: label these as model properties, report the freight bill and test a capped rail-capacity lever. If the freight bill exceeds the stock-out loss after the P2–P3 fixes, finding 1 reverses.

### P8. "Priced by its calendar" is untested
The second tank-barge closure lasts five weeks (p. 9, Fig. 2), not "seven" (pp. 2, 4). The ratio of the second wave to the first is 3.2 at ×1, 1.9 at ×1.5 and 3.2 at ×2 (Figs. 4c, 6), so it does not track buffer size. By the 40-cm run, the extra tank-barge weeks carry about half the second wave. Splitting the waves by time window books the first wave's depletion to the second.

Test: run the second wave alone from steady state, and the two waves six open weeks apart. Equalise the tank-closure lengths and report the ratio over the eleven draws. If the second wave from steady state still costs near 0.41 %, refill explains little.

### P9. Levers without scale, cost or ensemble
- **Fleet.** The lever converts every tank and dry-bulk vessel (p. 10), against sixteen tankers built or planned (p. 7). "The closures disappear" (p. 6) is wrong: weeks 8 and 13 (11–12 cm) stay closed, as Fig. 5's residual shows.
- **Draws.** The levers use only the reference draw, and the draw band exceeds the gaps between them.
- **Other levers.** The fairway offset lifts every reach, and the outlook-triggered stock rule (p. 7) is not run.
- **Pooling.** "Halves the loss" (−37 %) compares a calibrated model with an uncalibrated one.

Fix: run the levers on all draws with paired differences, show efficacy against lever size, and give costs or call the results efficacy.

### P10. The 2022 input–output base
2022 (p. 8) was the energy-crisis year, and refining, power and fuel-fed transport carry ~90 % of the loss. Rerun on 2019 or 2021 coefficients.

## Disagreements between referees
- **Decision.** R4 would return the paper unreviewed; R1–R3 ask for major revision. The text supports R4 on readiness and R1–R3 on reparability.
- **Novelty.** R1–R3 see an advance; R4 sees an overclaim given refs. [15] and [19]. The paper credits [15] (p. 6), but p. 2 omits that [19] already couples supply chains to transport. Claim the extension: cargo-class mode choice at EU scale.
- **Freight.** R2 and R4 praise the delivered-price analysis; R1 and R3 call the conclusion built in. Both hold: the 1–2 % median price rise is sound, but quantities never responding to price is a rule.
- **Fig. 3.** R3 says the map cannot average the 1.4 % peak; R1 says its scale may saturate. This is unverifiable, but "across the whole country" (p. 5) contradicts the map either way.
- **Counterfactuals.** R2 calls one-change runs sound; R1 faults uncalibrated variants. R2 is right for levers, R1 for structural variants.

## Before submission
1. Rerun 2018 and 2026 with the fuel-chain corrections and a throughput cap, then recalibrate (P2, P3).
2. Add a table of targets and the monthly NACE B–D comparison, and propagate the ensemble calibration (P1, P5).
3. Use observed daily gauges and sourced floors (P6).
4. Run the calendar decomposition (P8).
5. Run the levers on all draws, with a capped rail lever and costs (P9).
6. Report the freight bill, relabel by-construction results and rewrite the abstract (P7).
7. Set the 2026 failure criteria (P5).
8. Complete the SI, figures, references, data and code (P4).

## Minor points
**Numbers and words.** "Record twice" (abstract) vs "no lower" (p. 4). "Five times the normal rate" (p. 4) vs Fig. 2's ≈3.2. "More than doubles" (p. 5) is a quadrupling; "doubling it removes three quarters" is the same pair of runs, not a missing ×4 run (R1). Pooling "halves" vs −37 %. NACE A–F counted as recoverable (p. 10) vs power "lost for good" (p. 5). "Five adaptations" vs six bars.

**Units.** "% of a quarter" spans three quarters; USD and EUR are mixed.

**Presentation.** Define the jargon.

**References.** Commerzbank is unreferenced; resolve the VERIFY notes.

**Figures.** Fig. 1 does not mark Kaub; Fig. 2 lacks the floors and forecast flags; Fig. 5's lever runs end at week 31, the base at 39.
