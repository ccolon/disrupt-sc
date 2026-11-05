# Report of Referee R2: freight transport, inland navigation and hydrology

## Summary of the claims
The authors simulate the 2018 and 2026 Rhine low-water events with a firm-level, EU-wide agent-based supply-chain model that routes every shipment by cargo class on the TEN-T network. A weekly Kaub gauge sets a voyage surcharge (the inverse of the load factor). It also closes a vessel class whenever the gauge is below that class's floor (containers 40 cm, tank barges 50 cm, dry bulk 30 cm). With one parameter calibrated on 2018 (input stocks ×2), they report that 2026 cost Germany 0.54 % of a quarter's value added, and that stock-outs rather than freight bills drive the loss. The September–October trough cost three times the August closure because buffers could not refill, and four fuel-fed service sectors carry four fifths of the loss. A low-water fleet removes 95 % of the loss, fairway deepening or extra stocks about 40 %, and cheaper rail nothing.

## Assessment
The question matters, and putting mode, route and closure decisions inside a firm-level supply-chain model is new: the transport-economics literature prices freight and modal shift but not propagation. Several parts are sound:
- the draught-table route from gauge to load factor;
- the one-change counterfactuals;
- the insight that fairway deepening and a lower tank-barge floor are one lever;
- the point that freight is a small share of bulk cargo value;
- candour about several residuals.

But three features of the transport layer shape the headline results more than the paper says. Throughput is unconstrained whenever a class is open (M1). The loss is almost entirely a liquid-bulk fuel chain whose routing the paper itself flags as wrong (M2). About 40 % of the 2026 loss rests on two forecast weeks within 8 cm of an unsourced floor (M5).

On the three questions in my brief:
1. **Past events.** Closure-week tonnage drops match in number but measure another quantity, and the surcharge-month drops and the 2018 onset are missed. Model rates (at most 3.2×) sit below the observed tanker multiples. These biases run both ways and the calibrated buffer nets them out: the total may be right while the weekly profile, the sectoral anatomy and the lever ranking are biased (M1, M3, M4).
2. **Flows through the bottleneck.** Crude for inland refineries is routed through Kaub although it arrives by pipeline. In the other direction, Rhine containers, Lower Rhine ore and coal, and the other waterways are missing (M2, M4).
3. **Adaptation levers.** The fairway lever is plausible in kind. The fleet lever replaces the whole fleet in a model without capacity, and the rail lever is inert by construction (M6, M7).

## Major issues

### M1. Above the floors, partial loads never limit throughput — critical
- Where: p. 9 (Transport layer; Disruption and response), p. 5; Fig. 2b; Fig. 5.
- Text: "Capacity constraints on links and ports are not used." (p. 9)
- Problem: The draught table sets prices and closures only. In open weeks the model moves the full baseline tonnage, and more to refill stocks: "with the river open at half loads, deliveries return to their baseline" (p. 5).
  - The paper's own Fig. 2b puts fleet capacity past Kaub at about 50 % and 38 % in the two weeks between the waves, 40–62 % in the three weeks before the first closure, and 31–51 % in weeks 15–17. Moving 100 % or more would take two to three times the voyages.
  - Conversely, in "closed" weeks the same table gives 9–25 % capacity, and 20–30 % of the cargo did pass in August 2026. The model passes nothing on the water.
- Why it matters:
  - (a) The paper says the second wave cost three times the first because buffers refilled for two weeks. The fleet could not carry that refill. With a capacity limit, stocks keep draining through weeks 10–11, the waves probably merge into one trough that starts before 27 July, and both the ratio and its explanation change.
  - (b) The fleet lever's 95 % comes from closures disappearing. With capacity, a low-water fleet still carries only a fraction of normal tonnage at 10–30 cm.
  - (c) The ×2 buffer is fitted to a model that loses nothing in August to mid-October 2018. Adding the missing drawdown moves the multiplier, and with it every 2026 number.
  - (d) The observed 3–10× rate multiples (p. 5), well above the inverse load factor, are scarcity prices rationing that capacity.
- Resolution: [analysis]
  - Replace the binary floors with a weekly throughput cap per class: draught-table capacity times a fleet-mobilisation factor (idle vessels, extra voyages, lightering) estimated from the 2018 monthly Kaub tonnage, with rationing among shippers.
  - Recalibrate on 2018 and report the 2018 onset, the stocks between the 2026 waves, the wave ratio and the levers.
  - Test out of sample on August 2022 (Kaub in the low 30s of cm, no closure in reality).

### M2. The loss is a liquid-bulk fuel chain on routes it does not use — critical
- Where: pp. 5, 7, 9; Figs 3, 5.
- Text: "routes crude to inland refineries by barge for want of a pipeline mode" (p. 7)
- Problem: Fig. 5 shows the loss is almost entirely the tank-barge channel. Fairway +20 cm lifts the first-wave gauges (29, 23, 11, 27 cm) above the dry-bulk floor in at least three of the four weeks, yet the first-wave loss is unchanged, and the fairway and 40-cm tank-floor curves coincide. Ore, coal and grain contribute next to nothing. The liquid-bulk channel has three problems:
  - (a) **Crude.** The large German refinery upstream of Kaub, MiRO Karlsruhe, takes its crude by pipeline (SEPL from Fos, TAL from Trieste), and so do the Bavarian refineries. Yet Fig. 3 shows some of the heaviest peak-week losses east of the Rhine, apparently in Bavaria. The Kaub excess fits crude routed through Kaub: 68 Mt in the model against 50–60 Mt observed, with no containers, so bulk is overstated by roughly a quarter to a half.
  - (b) **Products.** Product pipelines into Rhine-Main (RMR, CEPS) are absent.
  - (c) **Substitution.** "road is never a line-haul mode for bulk" (p. 9), and switching bulk to rail carries a prohibitive penalty. That is right for ore, not for refined products, which were railed and trucked south in 2018. The national fuel pool then turns a refinery shortfall into a shortage for "every transport operator and gas-fired plant in the country" (p. 5). Gas plants do not burn barge-borne fuel.
- Why it matters: This chain produces the abstract's "lasting loss in services that cannot catch up", the four-fifths share of fuel-fed sectors, and the lever ranking. A critical input held in 7-day stocks responds nonlinearly, so even modest product substitution could remove much of the loss.
- Resolution: [analysis]
  1. Tabulate the model's Kaub tonnage by commodity group, direction and origin–destination for all eleven draws, against CCNR/Destatis counts by goods group (ref. 2).
  2. Supply inland refineries through their pipelines; an exogenous link suffices.
  3. Allow rail and road transport of refined products up to observed volumes.
  4. Decompose the German loss by the input that runs short first.

  Constraining the supply-chain draws to the Kaub commodity counts would also likely narrow the ±0.14 band.

### M3. The throughput and timing checks compare different quantities — major
- Where: pp. 4–5; Fig. 4a; SI outline S5.
- Text: "In a closure week the tonnage of dry bulk that crosses Kaub falls by 81 %" (p. 5)
- Problem:
  - (a) **August 2026.** No vessel passes Kaub in a model closure week, so the 19–30 % that "crosses Kaub" is deliveries of Kaub-linked flows by other routes. The operators' count measures cargo carried past Kaub by vessels at partial loads.
  - (b) **November 2018.** The model's weekly Kaub tonnage against its own baseline, with only tank barges closed, is set against the Destatis monthly year-on-year tonnage of all German waterways, including the Lower Rhine and the Elbe, which were also low.
  - (c) **Timing.** thyssenkrupp's force majeure concerned ore for Duisburg via the Lower Rhine, which in the model gets a third of the surcharge and never closes. The model's mechanism cannot produce that event. Its peak (early December) also falls after the observed November trough.
  - (d) **Target.** The 2018 target is an industrial-production effect (p. 2), but 85 % of the model's 2018 loss is in services.
- Why it matters: The paper offers these as two facts the calibration did not use, yet they do not single out the model's mechanism over alternatives.
- Resolution:
  - [analysis] Report water tonnage on the Kaub edge separately from deliveries of Kaub-linked flows. Compare monthly model tonnage on the Kaub and Lower Rhine reaches with the August–December 2018 cross-section counts, and monthly manufacturing loss with the estimates of ref. 6.
  - [text] Drop thyssenkrupp as evidence unless the Lower Rhine is modelled.

### M4. One weekly gauge and unsourced floors set on a knife-edge — major
- Where: pp. 3, 9; Figs 2, 6.
- Text: "below the sailing floor of a class ... the reach is closed to it" (p. 9)
- Problem:
  - (a) **Unsourced floors.** The floors have no source, and ±10 cm on the tank floor moves the loss by ±39 % (Fig. 6). The paper's own count has 30 % of liquid cargo passing in the week of 13 August, at a gauge near 10 cm, 40 cm below the tank floor. At EUR 200 a tonne, sailing at a fifth of capacity still pays: a floor is an economic threshold, not a hydraulic one.
  - (b) **Weekly means at the threshold.** Closures turn on weekly means within 1–3 cm of a floor: week 16 at 49 cm is closed, week 11 at 52 is open, weeks 6, 9 and 12 at 27–29 cm are closed. Week 9 starts at 5 cm and averages 27, so vessels sailed again within the week. Daily gauge data exist.
  - (c) **One gauge for the corridor.** Kaub drives every reach, and the paper does not say whether a closure applies to one reach or to the whole chain. The Lower Rhine has its own low-water regime and carries about three times the Kaub tonnage. The Elbe and the Danube were also low in 2018.
  - (d) **Calibration.** A model of Kaub alone, calibrated to a national estimate covering all waterways, attributes those other effects to Kaub, and so inflates what Middle-Rhine levers remove.
- Resolution:
  - [analysis] Source the floors. Close each class for the share of days below its floor. Use gauges per reach (Maxau, Kaub, Ruhrort/Emmerich).
  - [text] State which reaches close.

### M5. The 2026 numbers rest on forecast weeks presented as observed — major
- Where: pp. 2, 6–7, 9; Figs 2, 5.
- Text: "which in September 2026 correctly predicted that the river would not recover before October" (p. 7)
- Problem: From 10 September the series is the median of the BfG ensemble of 7 September, and the last two weeks are assumed values.
  - Page 2 narrates the mid-September fall as an event, and p. 7 calls the outlook correct, which needs observations the paper lacks.
  - Fig. 2 does not flag the forecast weeks, although its caption says it does.
  - The forecast tank-only closure weeks 15–16 (42 and 49 cm) carry about 40 % of the German loss: the fairway and 40-cm floor levers act only there (Fig. 5). The peak week is also a forecast week.
  - An ensemble median is not a trajectory the river could follow.
- Why it matters: The 0.54 %, the 3× ratio, the peak and three of the five lever values depend materially on these weeks.
- Resolution:
  - [analysis] Use the observed daily series to the end of the event. Until then, run the ensemble members and report the resulting band.
  - [text] Separate observed, forecast and assumed weeks.

### M6. Three findings hold by construction — major
- Where: abstract; pp. 4–6, 9; SI outline S8.
- Text: "Why cheaper rail is inert by construction" (p. 20)
- Problem:
  - (a) Shippers give up only when a route closes and the only alternative is a forbidden mode switch. "No shipper ... gives up a delivery on price" (p. 4) is therefore the rule, not a result.
  - (b) The loss counts production shortfall only, and surcharges never enter it, so "stock-outs, not freight bills" follows partly from the metric.
  - (c) Switching bulk to another mode carries a prohibitive penalty, so no rail tariff can matter. The stated reason, the "absence of tank-car and ore-train capacity" (p. 6), invokes a capacity that the model lacks (p. 9). The supporting arithmetic compares a stock of wagons (900 wagons, about 200 barge loads) with a monthly flow of barges.
- Why it matters: Two of the four headline findings and one lever conclusion are presented as discoveries.
- Resolution:
  - [text] Present these as consequences of the model's rules.
  - [analysis] Report the weekly extra freight bill (surcharge × tonnage) next to the value-added loss and against the welfare estimates of refs 9–11. Replace the rail-tariff lever with a rail-capacity lever: bulk and fuel may switch up to X kt a week, with Germany's 2022 rail priority for energy freight as precedent. Give the wagon figure in tonnes per month.

### M7. The adaptation levers have no stated physical scale — major
- Where: pp. 5–7, 10; Fig. 5.
- Text: "the closures disappear and only the surcharges remain" (p. 6)
- Problem:
  - **Fleet.** The fleet lever lowers the floor of every tank and dry-bulk vessel, which amounts to replacing fleets that number in the thousands. Page 7 calls nine built and seven planned tankers "the fleet lever taking shape", with no cost or time scale. Without capacity (M1), the low-water loading table cannot affect throughput. Weeks 8 and 13 (11 and 12 cm) stay closed under a 20-cm floor, so the residual 5 % comes from closures, not surcharges.
  - **Fairway.** Fairway +20 cm is added to the Kaub gauge, which also drives the surcharges on the other reaches, whereas the project deepens the river between Mainz and St. Goar only.
  - **Stocks.** The stock levers are not expressed in tonnes, and the targeted run is still pending. The reserve-release rule that the Discussion recommends is not evaluated.
- Resolution: [analysis] Once M1 is in place:
  - Scale the fleet lever by fleet share (e.g. sixteen tankers as a share of tank capacity past Kaub).
  - Apply the fairway offset to the Middle Rhine only.
  - Give the stock levers in tonnes.
  - Run an outlook-triggered reserve release.

## Minor issues
m1. p. 1 — "below about 77 cm" load restrictions begin: they begin far above the equivalent low water (Fig. 2b shows 72–80 % capacity at 92–101 cm), and Fig. 2 gives that mark as 78 cm. Reword.
m2. p. 2 — "EUR 45 to over EUR 200": give dates and source; EUR 45 looks high for a normal-water rate.
m3. pp. 9–10 — The draught table, Lower Rhine factor, rate tables and low-water loading table are placeholders. The SI is an outline, Supplementary Figs S1–S3 are absent, and code and data are placeholders, so the baseline modal split and Rhine profile cannot be checked.
m4. p. 10 vs SI S4/S6 — The floors and switching rule are said to be "not tuned", yet the SI cites a "calibration log" and a "tanker-floor cross-check". Give each transport parameter's source and the date it was fixed relative to the 2018 runs.
m5. p. 9 — Routing is all-or-nothing: report the share of Kaub tonnage whose best alternative costs within 10 % of its route.
m6. p. 4 — Kiel's 0.1–0.2 is for third-quarter GDP and is dated 28 July. The 0.1–0.35 spread of estimates also admits ×1.5 (0.28, Fig. 4c), so it does not single out ×2.
m7. p. 3 — The 2018 reserve release is folded into ×2; say whether reserves were released in 2026.
m8. Figures — Fig. 1: Kaub is not marked. Fig. 2: the caption describes panels (a)–(c) with floors and a loss panel; the figure shows neither. Fig. 3(b) and the Fig. 5 targeted run are missing.

## Internal inconsistencies
- p. 2, p. 4 "tank barges for seven" (weeks) vs p. 9 schedule and Fig. 2: weeks 12–16, five weeks.
- p. 6 "the closures disappear and only the surcharges remain" vs Fig. 2 (11 and 12 cm, below the 20-cm floor) and Fig. 5 (fleet-lever losses in weeks 9–10 and 14).
- p. 5 "every transport operator ... in the country ... runs short at once" and p. 7 "spreads the shortfall nationally" vs Fig. 3: the loss is confined to southern Germany.
- p. 6 "the constraint is not the price of rail but the absence of ... capacity" vs p. 9 "Capacity constraints on links and ports are not used."
- p. 1 "the river does not close; it thins" vs the binary closures of p. 9.
- p. 4 "surcharge reaches five times the normal rate" vs p. 6 "barge rate triples" vs Fig. 2c (maximum about 3.2×).
- p. 5 "halving the buffer more than doubles the loss" vs Fig. 6 (+299 %) and p. 6 "four times more".
- p. 3 "reproduces ... the tonnage profile of the Rhine" vs p. 9 "68 Mt ... against 50–60 Mt", all bulk.
- p. 4 "the five weeks of the August wave" vs four closure weeks from 27 July and Fig. 4c "weeks 7–11": define the window.

## Recommendation
Major revision; confidence 4 (higher on transport and hydrology than on the econometric targets). The changes that would most change my view:
1. A capacity limit on partial-load throughput in place of binary floors, recalibrated, with a 2022 out-of-sample test.
2. Corrected liquid-bulk routing and substitution (pipelines, product transport up to capacity), with Kaub flows by commodity checked against counts.
3. Observed daily gauges to the end of the event, per-reach gauges, and sourced floors.
