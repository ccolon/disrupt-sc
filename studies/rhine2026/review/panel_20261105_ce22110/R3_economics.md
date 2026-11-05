# Report of Referee R3: macroeconomics and input-output economics

## Summary of the claims
The paper simulates the 2026 Rhine low-water event with a firm-level supply-chain model of 28 European economies with an explicit transport network, built on the 2022 OECD ICIO. One parameter, a ×2 multiplier on raw-material stock targets, is fitted to an ex-post estimate of the 2018 loss (0.3–0.4 % of a quarter of German value added). The fit is cross-checked against the 2018 timing and against ex-ante estimates for August 2026. The paper reports that the 2026 event costs Germany 0.54 % of a quarter (USD 5.2 bn), driven by stock-outs rather than freight costs. It finds that the September–October trough cost three times the August closure and that four fifths of the loss falls in fuel-fed services that cannot catch up. It reports that a low-water fleet removes 95 % of the loss, fairway deepening or extra stocks about 40 %, and cheaper rail nothing.

## Assessment
The question matters, and modelling individual firms and the routes their goods take is a real advance on input–output disaster models keyed by region. Several things are sound: weighting losses by value-added share (no double counting across stages), the gross vs net (backlog) distinction, the transparent stock ladder (Fig. 4b), the ensemble of network draws, and the frank remark that the buffer result is "partly built into the fit". My concerns are about what the numbers are.

- (Q1) No headline number is yet in the units of an official statistic:
  - the 0.54 % is a loss cumulated over 39 weeks that span three calendar quarters;
  - the 2018 target appears to be an industrial-production estimate, matched with a loss that is 85 % services;
  - the August 2026 test compares a five-week window with third-quarter GDP.
- (Q2) These omitted channels could change the size of the loss, and even which is larger, transport costs or shortages:
  - capacity lost when barges sail at partial loads;
  - substitution in the fuel market and the power merit order;
  - the real resource cost of the surcharges, which the loss metric cannot register.
- (Q3) The adaptation results are efficacy at lever sizes that cannot be compared with each other, but the text slides into recommendation ("dominates", "should act").

The manuscript is also incomplete for review. The SI is an outline, Figs. 2c, 3b and S1–S3 are missing, the † numbers are pending, references are marked VERIFY, and the code and data are not available to referees.

## Major issues

### M1. The loss anatomy (four fifths in fuel-fed services) is probably an artefact and does not match the 2018 evidence — critical
- Where: p. 5 ("Who loses"), p. 7, pp. 8–9; abstract.
- Text: "four of them, all fed by fuel, carry four fifths of the total"
- Problem:
  - (a) Land transport (22 %), warehousing (29 %) and water transport (9 %) lose output for want of fuel. But nothing in Methods links a haulier's output to the shipments routed on the transport layer, which keep moving on cost. Their customers feel nothing either, because service inputs carry a 90-day coping duration. The lost value added therefore has no physical counterpart.
  - (b) Electricity and gas (20 %): other plants and imports replace a fuel-short plant in the merit order, so national supply need not fall. Whether other suppliers in the pool can expand is not stated. If they cannot, a reallocation between plants is booked as a national loss.
  - (c) Fuel is rationed pro rata from a national pool. There are no extra imports from Antwerp–Rotterdam, no allocation by price, and no 2026 reserve release. Crude also reaches inland refineries by barge, which the authors concede overstates their exposure (p. 7). Each choice pushes the shortfall into sectors where net loss equals gross loss.
  - (d) The calibration target is an industrial-production effect: about 1 % per month of low water, with a trough of 1.5 % in November [6]. With industry about a quarter of German value added, four months at 1 % is about 0.3 % of a quarter. The target thus looks almost entirely like an industry loss. The model's 2018 goods-sector loss is at most 15 % of 0.32 %, about 0.05 % of a quarter. The model reaches the right total through the wrong sectors.
  - (e) By my rough reckoning, each of the three largest service sectors loses about a full week of its national value added. A fall of that size would be visible in monthly statistics.
- Why it matters: the anatomy is an abstract-level claim, and it also sets the size of the loss. If the services loss shrinks, recalibration moves the multiplier, which changes the 2026 headline, the net/gross ratio (97 %) and the lever ranking.
- Resolution:
  - [analysis] Report the model's monthly 2018 loss for NACE B–D against the monthly estimates of [6].
  - [analysis] Check the model's Q4 2018 losses in transport, warehousing and power against three series: the truck-toll mileage index, Destatis turnover in transport and storage, and monthly electricity generation.
  - [analysis] Rerun with crude to Rhine refineries unaffected (pipelines), spare capacity for other suppliers of pooled products, and a priority rationing rule. Then recalibrate.
  - [text] State which losses have a physical counterpart.

### M2. The calibration and validation targets are not the same estimand as the model output — major
- Where: pp. 2–4, p. 10, Fig. 4.
- Text: "compared the cumulated German value-added loss with the ex-post estimates of 0.3–0.4 %"
- Problem:
  - (a) The 0.3–0.4 % "GDP effect" on p. 2 becomes "% of a quarter" on p. 3 without definition. It could be a one-quarter level effect, a cumulated half-year loss, or a scaled IP elasticity. It may also include the August–September surcharge months, which the model cannot produce (p. 7). Fitting a total that contains a missing channel biases the buffer down and loads that loss onto the closure weeks.
  - (b) In Fig. 4a about half of the model's 2018 loss falls in December, after the river reopened. The peak is ≈1.25 % of a week's total value added. The econometric trough, 1.5 % of industrial production in November, is ≈0.4 % of total value added. The model's loss is three times deeper, a month later, and lasts six weeks rather than four months. "The peak in the observed week" (p. 3) compares a weekly model peak with a monthly trough.
  - (c) Refs. [6]–[8] all come from the Kiel Institute, so the ex-ante estimate [8] plausibly scales the same 2018 elasticity used as the calibration target. If so, the August 2026 check is not independent.
    - The windows differ: "points of third-quarter GDP" against model weeks 7–11. Read from Fig. 5, the model's Q3 loss, including the start of the second closure, is about 0.2 %.
    - The check barely discriminates: ×1.5 (0.28) is also inside 0.1–0.35 (Fig. 4c).
  - (d) Reading ×2 as "all inventories" conflicts with the paper's statement that raw materials are a third of inventories, which implies ×3. Finished goods held by suppliers on the far side of a closed reach do not buffer the buyer. The multiplier also absorbs the 2018 reserve release and carries it into 2026.
  - (e) The ladder stops at the adopted value, and the ensemble mean at ×2 (0.30) sits on the lower edge of the target range.
- Why it matters: the abstract's claim that the model "reproduces the timing of the 2018 losses and the ex-ante estimates" is not supported as stated.
- Resolution:
  - [text] Add a table of targets giving variable, sectors, period, level or growth, and counterfactual, and say how [8] was produced.
  - [analysis] Report model losses by calendar month and quarter, in each target's units.
  - [analysis] Extend the ladder above ×2, calibrate on the ensemble mean, and propagate the admissible multiplier range to 2026.

### M3. "Stock-outs, not freight bills" is largely built into the loss metric and the decision rules — major
- Where: pp. 4–6, pp. 8–10.
- Text: "no shipper in the model gives up a delivery on price"
- Problem:
  - (a) The loss is the production shortfall times a fixed value-added share at baseline prices (p. 10). Higher freight bills, and the real resource cost of sailing at a third of capacity, cannot register.
  - (b) Shippers on surcharged routes always pay (p. 9) and no demand is price-elastic, so by construction no quantity responds to price.
  - (c) Surcharge weeks carry the full tonnage (p. 7). That is the omitted capacity channel the 2018 record shows in August–September.
  - (d) Prices pass through freight only, so the model cannot produce the regional scarcity pricing of fuel seen in 2018.
- Why it matters: a rough size for the freight channel is €0.2–0.4 bn:
  - Kaub flow in the model: 68 Mt/yr, about 1.3 Mt/week;
  - sum of the weekly cost multipliers above one in Fig. 2: about 12;
  - base freight rate: €15–25/t;
  - plus the Lower Rhine, at a third of the surcharge, on top.

  That is a tenth of the headline, but of the same order as the model's goods-sector loss (≈0.09 % of a quarter). If M1 removes much of the services loss, the freight channel is not small. Point (c) also inflates the fleet lever, since the surcharges that remain cost nothing in the model.
- Resolution:
  - [analysis] Report the extra transport cost: the resource cost at 1/load factor, and the scarcity premium separately.
  - [analysis] Run a recalibrated sensitivity with surcharge-week tonnage capped at load factor × fleet capacity.
  - [analysis] Compare modelled refined-product prices with observed regional fuel prices.
  - [text] Label (a) and (b) as assumptions.

### M4. The "calendar, not depth" result lacks a counterfactual decomposition — major
- Where: abstract, pp. 2, 4, 6.
- Text: "A low-water season is priced by its calendar, not by its minimum gauge."
- Problem:
  - The waves are split by a time window (weeks 7–11 against the rest), so the depletion left by the first wave is booked to the second.
  - The second tank-barge closure is longer (five weeks by Methods and Fig. 2, not "seven") and is followed by the highest surcharges.
  - Insensitivity to depth below the floor holds by construction, because closures are binary.
- Resolution:
  - [analysis] Run August-only and September–October-only profiles and report the interaction term, which is the calendar effect.
  - [analysis] Add a variant with six open weeks between the troughs.
  - [text] Correct "seven".

### M5. The levers are efficacy at lever sizes that cannot be compared, not a policy ranking — major
- Where: abstract, p. 3, pp. 5–7, p. 10, Fig. 5.
- Text: "a low-water fleet dominates fairway deepening and extra stocks"
- Problem:
  - (a) The levers differ enormously in size and cost:
    - the fleet lever converts the whole tank and dry-bulk fleet (p. 10), against nine tankers built and seven planned (p. 7);
    - +7 days of stocks for every buyer is a carrying cost paid every year, for an event of unstated frequency;
    - the fairway is "a decade away".

    Without costs, "dominates" is unsupported.
  - (b) "The closures disappear" is wrong. The weekly means of ≈11 and 12 cm (weeks 8 and 13) stay below the fleet's 20 cm floor, and Fig. 5c shows the residual loss.
  - (c) "Cheaper rail nothing" follows from the prohibitive bulk switching penalty and the absence of link capacities (SI S8: "inert by construction"), yet the abstract reports it as a finding. The policy question is rail capacity, which a capped switch could represent (e.g. the 900 wagons).
  - (d) The levers are run on one draw and one calendar, although the range across draws exceeds most lever effects.
  - (e) Stock rules acting on BfG outlooks (p. 7) are recommended but not simulated.
  - (f) General-equilibrium effects are omitted: the demand to build up stocks before the event, and the extra normal-water cost of low-water vessels.
- Resolution:
  - [text] Present the results as efficacy at stated sizes.
  - [analysis] Show efficacy against lever size: fleet share converted; +10/20/30 cm of fairway; +3/7/14 days of stocks.
  - [analysis] Run the levers on ≥5 draws and on the 2018 profile.
  - [analysis] Add a capped rail-capacity lever.
  - [analysis] Compare annualised costs under a stated event frequency.

### M6. Economic data base and uncertainty — major
- Where: p. 8, p. 2, Figs. 5–6.
- Text: "The economy is the 2022 OECD inter-country input–output table"
- Problem:
  - (a) 2022 was the energy-crisis year, so the cost shares of fuels, coal and gas, and the value added of refining and power, are atypical. The 2018 calibration, the 2026 event, the 2 % materiality floor and the critical-input set all rest on that structure. Since refining, power and fuel-fed transport carry about 90 % of the loss, the base year matters.
  - (b) The calibration range is not propagated. The 2026/2018 ratio per draw (≈1.7 for the reference draw) would be more robust than the level.
  - (c) "Every result is reported over an ensemble" (p. 2), yet the anatomy, the levers and the sensitivities use a single draw.
- Resolution:
  - [analysis] Rerun on a 2019 or 2021 table, or with energy coefficients rescaled.
  - [analysis] Report the 2026/2018 ratio per draw.
  - [analysis] Run the anatomy and the levers on several draws.

## Minor issues
- m1. p. 10 — "Goods and construction (NACE A–F)" includes utilities (D–E), which the paper treats as perishable. Fix: write A–C and F.
- m2. p. 4 — 2022 USD and 2026 EUR are mixed ("about EUR 1.2 billion"). Fix: apply the shares to 2026 nominal value added, and note GDP vs GVA.
- m3. p. 4 — "Households lose 5.4 billion USD": the households (Germany or EU) and the prices are not stated, and this loss overlaps with the value-added loss, so the two must not be added. Fix: state both and the overlap.
- m4. pp. 5, 10 — The catch-up share ("a fifth") depends on spare capacity, re-ordering rules and run length, none of them stated, and the 13 % delay-cost rate is unsourced. In Fig. 5c the lever runs appear to end at week 31 and the base at week 39, so the net losses are not comparable. Fix: state the rules and source the rate; use equal run lengths.
- m5. p. 5 — "Halving the buffer more than doubles the loss": it actually quadruples (2.16 vs 0.54). Fix: say "quadruples".
- m6. p. 5 — The operators' count (−80/−70 %) is physical tonnage past Kaub. The model's figure is delivered tonnage on Kaub-crossing links, whereas in an all-class closure no tonnes pass Kaub in the model. Fix: compare the same quantity.
- m7. p. 4 — The Destatis −34 % is national waterway tonnage, year on year. The model's −31 % is Kaub against a no-shock baseline. Fix: report the model's tonnage on all German waterways.
- m8. p. 9 — The model sends 68 Mt through Kaub, all of it bulk, against CCNR counts of 50–60 Mt that include containers. Bulk exposure is overstated and containers are absent. Fix: show the headline with bulk flows rescaled.
- m9. p. 8 — The 2 % materiality floor and the 90-day service coping duration were set to stop cascades, so they are degrees of freedom. Fix: report the headline under alternative values.
- m10. p. 2 — The Kiel statement of 28 July [8] was not "issued during the August closure". Fix: correct the date.

## Internal inconsistencies
- p. 4: "every class closed for three weeks, tank barges for seven" (also p. 2) vs p. 9 (weeks 12–16) and Fig. 2, which give five weeks.
- p. 3: "raw materials are about a third of manufacturing inventories" vs the adopted multiplier of 2.
- p. 4: "Two facts the calibration did not use" (timing first) vs p. 10, where calibration is compared "with the peak of the losses in late November or early December".
- p. 10: "the switching rule are not tuned" vs p. 20: "threshold sensitivity table (from the calibration log".
- p. 6: "the closures disappear" vs the weekly means in Fig. 2a (≈11 and 12 cm, below the 20 cm floor).
- p. 4: "when the surcharge reaches five times the normal rate" vs Fig. 2c, where the multiplier peaks at ≈3.2.
- p. 4: national peak "1.4 % of a week's value added" vs Fig. 3, where most German regions are below 0.13 % and the scale stops at 1.6 %. That map cannot average 1.4 %. Likewise, p. 7 "spreads the shortfall nationally" vs a map that concentrates the loss in the south.
- p. 2: "every result is reported over an ensemble" vs Figs. 5–6, which use one draw.
- p. 10: NACE A–F counted as recoverable vs p. 5, where electricity and gas are "lost for good".

## Recommendation
Major revision; confidence 4. Three changes would most change my recommendation:
1. Test the sectoral anatomy against 2018 sector statistics and remove the transport, electricity and refinery artefacts, then recalibrate.
2. Add a table of estimands and give the model's numbers in each target's units (the monthly industrial path; calendar quarters), with the calibration range propagated to 2026.
3. Quantify the freight resource cost, label the by-construction results (no shipper gives up on price, rail is inert, closures are binary), and present the levers as efficacy at stated sizes.
