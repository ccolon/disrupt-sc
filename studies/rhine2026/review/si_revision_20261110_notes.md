# The author's revision of si.tex (675722a against fc30932)

Notes: 61; new file 885 lines, old 847 lines.

## Inline notes
### N01 [S1] line 5
NOTE: add ref, also for all the other data source in this section
BEFORE: ...\paragraph{Agents.} Firm agents are the disaggregation of each region--sector's output into its plant and employment locations, by the \texttt{firm-extractor} package of the model. Sectors use different source data for this spatial downscaling procedure. For crops (A01), the SPAM 2020 crop-production grid 
AFTER: is clipped NUTS3 and placed at the weighted centroid. Ten sectors use facility data, kept explicitly as points: coal mines (B05) frm the Global Energy Monitor (...

### N02 [S1] line 5
NOTE: cite data source
BEFORE: ...C17--18) and aluminum smelters (C24B) from Climate TRACE's 2022 facility activity, cement plants (C23) from the GEM cement tracker, steel mills (C24A) from the GEM steel tracker; power (D) from the GEM power trackers aggregated to NUTS2 capacity. The 39 other sectors are downscaled using NUTS3 employment in the regional accounts
AFTER: . Facility statuses are taken from the 2022 accounts. \NFirms{} agents after removing disconnected ones, nine per region--sector on average. Households are one ...

### N03 [S1] line 5
NOTE: what is the region population centroid? same as region centroid? or region's most populated city?
BEFORE: ...TS2 capacity. The 39 other sectors are downscaled using NUTS3 employment in the regional accounts. Facility statuses are taken from the 2022 accounts. \NFirms{} agents after removing disconnected ones, nine per region--sector on average. Households are one agent per NUTS2 region (251), located at the region's population centroid
AFTER: . Every agent attaches to the nearest road node of the network....

### N04 [S1] line 7
NOTE: add ref
BEFORE: ...\paragraph{Network.} The trans-European transport network (TEN-T, extracted from the TENtec services of the European Commission on 29 August 2026
AFTER: ) with \NEdges{} edges and \NNodes{} nodes: roads (2,979 edges), railways (4,261), inland waterways (461, including 30 for the Rhine from Basel to Rotterdam), s...

### N05 [S1] line 13
NOTE: all the remainder of the caption: are all this information really useful as a general caption? isn't the "evidence" column enough? I would instead use the "notes" of the longtable class. In the main caption, maybe just state the main source: Eurostat, KiM, etc., "most evidence come from..."
BEFORE: ...\caption{\textbf{Transport cost parameters:} the baseline values and the evidence behind them. 
AFTER: Operator costs are the Panteia cost figures for the Netherlands Institute for Transport Policy Analysis (KiM, 2023; price level 2021), fleet averages that inclu...

### N06 [S1] line 24
NOTE: what is the "panteia" comparison? readers will not know. Give ref.
BEFORE: ...road, containers and dry bulk & 0.050 & A full-load long-haul rate. No rate series was collected; the Panteia comparison
AFTER:  for 2018 gives 0.115 EUR per tonne-kilometer for a tractor-semitrailer at fleet average, empty legs included. Calibrated. \\...

### N07 [S1] line 27
NOTE: calibrate to German split only?
BEFORE: ...rail, liquid bulk & 0.085 (0.100 in 10 countries: AT, BG, CZ, ES, FR, HU, IT, PL, SI, SK) & As road, liquid bulk: so that the German liquid-bulk split by mode matches Eurostat 2023
AFTER: . \\...

### N08 [S1] line 28
NOTE: for every number there should be a ref
BEFORE: ...inland waterway, dry bulk & 0.010 on the Rhine, 0.010--0.040 on the other waterways & Collected evidence: Push-convoy cost 0.008--0.012 EUR per tonne-kilometer (ores 0.009, coal 0.008; Panteia for KiM 2023, 2021 prices
AFTER: ); the published coal rate Rotterdam--Basel of 2015, 10.5 EUR per tonne (0.013; INFRAS for the Swiss Federal Statistical Office). Single motor vessels cost 0.01...

### N09 [S1] line 31
NOTE: we still need to provide an evidence here, look for some
BEFORE: ...sea & 0.0015 & 
AFTER: , do not influence the results. \\...

### N10 [S1] line 34
NOTE: again, cite every number
BEFORE: ...containers & 1.00 (road and rail); 0.32 (waterways); 0.15 (sea) & A cargo-side (inventory) value: the vessel-side cost of time is 0.02--0.07 EUR per tonne-hour at full load and 0.13--0.26 at fleet average (Panteia for KiM); 0.20 in the European Commission's charging study of 2005.
AFTER:  \\...

### N11 [S1] line 35
NOTE: what are the pieces of evidence?
BEFORE: ...dry and liquid bulk & 0.08 (all modes)& 
AFTER: . \\...

### N12 [S1] line 56
NOTE: I would remove the "lean" column. Somehow already included in the "basis" (which I renamed "evidence"). Put the acronym in longtable note structure
BEFORE: ...\caption{\textbf{Stock targets by buying industry.} Days of consumption of purchased goods inputs that each buying industry holds at the baseline (the model's value) and the evidence: 
AFTER: the lean value of 2019 where the series exists, the grade (A: balance-sheet data for the industry itself; B: data for a group of industries, or physical stock d...

### N13 [S1] line 56
NOTE: I don't understand the two first columns, it seems that they repeat themselves. I would rather have a separate table for this block
BEFORE: ...ries: the Bundesbank ratio statistics by division (non-finished stock over material costs, which includes work in progress); FIBEN: the Banque de France sector sheets (median stocks over turnover); Census: the US Census M3 materials-and-supplies inventories over the cost of materials; EKBG: the German reserve-plant act of 2022. 
AFTER:  The lower block gives the input-specific targets that override the industry value, with the modeling reason where the model departs from the physical figure.}...

### N14 [S1] line 129
NOTE: instead of this note column, I would have the end-of-table notes with superscript, I think offered in the longtable format. This will lightened the table.
BEFORE: ...lves output) and non-critical ("other"), and, for the sector as an input, how many buyers rate it critical ("critical for"). In the model, an input below 2\,\% of the buyer's input costs is considered non-critical. Over the 2,500 sector-to-sector pairs: 18\,\% of input are critical, 9\,\% are important, and 73\,\% non-critical.}
AFTER: ...

### N15 [S2] line 201
NOTE: add ref
BEFORE: ...The baseline reproduces the input--output accounts by construction. Its transport flows were calibrated against four kinds of statistic: the inland modal split by country in tonne-kilometers (Eurostat 2023)
AFTER: , the modal split by cargo class in Germany and the Netherlands (the NST divisions of the same source), the tonnage along the Rhine (the CCNR cross-section coun...

### N16 [S2] line 205
NOTE: but there is only 3 values for this port, so we could state directly how much it is
BEFORE: ...    \item The loading fee at a seaport follows a ladder in the port's observed throughput $T$: $3\log_{10}(100\,\mathrm{Mt}/T)$ USD per tonne for containers, clipped to 0--12, and a third of it for other cargo. One exception is Amsterdam, were low values are the minimal rate is 0.75 where the ladder gives less 
AFTER: . The ladder stands in for liner and feeder services that call at large ports, not small ones, which a network that reaches every coastal node at one sea tariff...

### N17 [S2] line 205
NOTE: cryptic last sentence, do we loose sth if we remove it?
BEFORE: ...ed to 0--12, and a third of it for other cargo. One exception is Amsterdam, were low values are the minimal rate is 0.75 where the ladder gives less . The ladder stands in for liner and feeder services that call at large ports, not small ones, which a network that reaches every coastal node at one sea tariff does not represent. 
AFTER: ...

### N18 [S2] line 210
NOTE: unreadable, make a two-col table with country in row and model vs. data in columns
BEFORE: ...} against 89 / 9 / 2, Austria \ModalATRoad{} / \ModalATRail{} / \ModalATIww{} against 69 / 29 / 2, Switzerland \ModalCHRoad{} / \ModalCHRail{} / \ModalCHIww{} against 66 / 34 / 0, Poland \ModalPLRoad{} / \ModalPLRail{} / \ModalPLIww{} against 76 / 24 / 0, Italy \ModalITRoad{} / \ModalITRail{} / \ModalITIww{} against 88 / 12 / 0 
AFTER: ....

### N19 [S2] line 212
NOTE: why only in those countries? following this argument of intra-reg flows, it should be under rep everywhere
BEFORE: ...Road is under-represented by construction in Germany, the Netherlands, Belgium, France and Austria
AFTER: : agents sit at NUTS2 and NUTS3 points, so the intra-regional traffic that the statistics count does not exist in the model, and the shares of rail and waterway...

### N20 [S2] line 212
NOTE: add these 3 rows under the Germany row of the new table
BEFORE: ...y by cargo class, on the German edges, the model gives general cargo \CargoGeneralRoad{} / \CargoGeneralRail{} / \CargoGeneralIww{} against 68 / 27 / 5, dry bulk \CargoDryRoad{} / \CargoDryRail{} / \CargoDryIww{} against 53 / 27 / 20 and liquid bulk \CargoLiquidRoad{} / \CargoLiquidRail{} / \CargoLiquidIww{} against 28 / 42 / 30
AFTER: : the bulk that the shock concerns travels on the right modes, with the waterway share of liquids nearly a third too high....

### N21 [S2] line 220
NOTE: don't understand. we don't show observations of "industrial users" nor about the alternative. A bit cryptic
BEFORE: ...\paragraph{The gaps, and their impacts on the study.} The loss estimated by the model are generated from the disrupted tonnage that crosses Kaub and its composition, from the rail and road alternatives and on the location of the German industrial users; the preceding paragraph gives these within a third of the observations
AFTER: . The port tonnages are not calibrated: \PortsWithinThirty{} of the forty largest European seaports are within 30\,\% of the Eurostat statistics (Table~\ref{tab...

### N22 [S2] line 228
NOTE: but overstate that of other regions then, since in absolute number we are good
BEFORE: ...aselMt{} against 5.5, Strasbourg \RhineStrasbourgMt{} against 16, Karlsruhe \RhineKarlsruheMt{} against 22), while the Mannheim--Mainz reach is above them (\RhineMannheimMainzMt{} against 40). The model carries the flows that Switzerland and Alsace receive by rail; therefore, it understates the exposure of those regions to Kaub 
AFTER: ....

### N23 [S2] line 233
NOTE: put only 20 or 30 to reduce size
BEFORE: ...\caption{\textbf{The seaports of the calibrated baseline.} The 40
AFTER:  largest seaports by gross weight of goods handled (Eurostat 2023, Mt) and the model's tonnage through their connectors; below the line, the ports outside the 4...

### N24 [S2] line 233
NOTE: put 50 to reduce size
BEFORE: ...\caption{\textbf{The seaports of the calibrated baseline.} The 40 largest seaports by gross weight of goods handled (Eurostat 2023, Mt) and the model's tonnage through their connectors; below the line, the ports outside the 40 where the model route 20~Mt 
AFTER:  or more..}...

### N25 [S3] line 313
NOTE: why keeping the 7 Sept vintage? ,remove it.
BEFORE: ...ptember) is retrospective at both dates; August (released on 7 October, the batch date, and not used) is a nowcast; September to December is prospective. The manifest of these vintages (profile files, loading curves, code commits, run lists, issue dates) is \texttt{studies/rhine2026/forecast\_manifest.md} in the code repository.
AFTER: ...

### N26 [S3] line 315
NOTE: which profile?
BEFORE: ...\paragraph{Monthly loading shares.} Under the profiles
AFTER:  the Kaub reach passes on average \KaubPassJun\,\% of its normal tonnage in June 2026, \KaubPassJul\,\% in July, \KaubPassAug\,\% in August, \KaubPassSep\,\% in...

### N27 [S3] line 317
NOTE: replace XXX accordingly
BEFORE: ...\paragraph{Loading table.} Table~\ref{tab:loading} describes how the loading curve is built. We gather evidence from various sources, such as XXX
AFTER: , to link gauge values to the shares of normal tonnage the Kaub reach can pass, called \textit{fleet value} here. The model interpolates linearly between those ...

### N28 [S3] line 317
NOTE: why not "traffic rate", or "loading share"?
BEFORE: ...\paragraph{Loading table.} Table~\ref{tab:loading} describes how the loading curve is built. We gather evidence from various sources, such as XXX, to link gauge values to the shares of normal tonnage the Kaub reach can pass, called \textit{fleet value} here
AFTER: . The model interpolates linearly between those values and stay at 0.08 below 5\,cm. The evidence comes from various quantity: single-vessel payloads, weekly co...

### N29 [S3] line 325
NOTE: I would remove this columns
BEFORE: ...cm & traffic rate & vessel 
AFTER: & nature & source & measures & treatment \\...

### N30 [S3] line 325
NOTE: also remove this columns, info is in "treatment" already
BEFORE: ...cm & traffic rate & vessel & nature
AFTER:  & source & measures & treatment \\...

### N31 [S3] line 385
NOTE: I don't understand "the larger of its share of the CCNR cross-section tonnage", larger than what?
BEFORE: ...\paragraph{Capacities.} The normal capacity of every Rhine reach is set per cargo class (Section~S2): for each class the larger of its share of the CCNR cross-section tonnage 
AFTER: and the model's own baseline flow of the class on the reach plus 2\,\%, so that the constraint is inert at full loading: at Kaub 175,900 t a day in total agains...

### N32 [S3] line 387
NOTE: that means that the loading curve is also applied to the other reach?
BEFORE: ..., \GateResentMin to \GateResentMax\,\% of the tonnage cut at Kaub finds another route (Table~\ref{tab:gate}). Containers always find rail or road alternatives; only bulk is withheld (Table~\ref{tab:channels}). During the low-water weeks, only Kaub saturates; in the recovery weeks, catch-up traffic saturates several other reaches
AFTER: , delaying part of the backlog and inventory refill....

### N33 [S3] line 389
NOTE: correct sentence
BEFORE: ...\paragraph{Surcharge.} The week's multiplier $1/\text{loading share}$, capped at 20, is applied on every reach from Koblenz upstream and at one third of its excess on the Lower Rhine reaches. This Lower Rhine factor is an assumption from the observed rates, which are typically three times lower than the Upper Rhine rates 
AFTER:   \citep{contargo2026}, and has negligible impact on the results....

### N34 [S4] line 397
NOTE: give one introductory sentence to this section
BEFORE: ...
AFTER: ...

### N35 [S4] line 404
NOTE: this caption is too long, move to the SI text with dedicated paragraph. Unclear why we choose the baseline rule.
BEFORE: ... up the alternative is barge to Koblenz, 88\,km of truck around the reach and barge again at a median surcharge of 49\,\% on the freight, rejected because 88\,km exceeds the allowance; the pairs whose normal route already has 100\,km or more of road (35\,\%) lengthen that road leg instead, which is what the adopted rule forbids.
AFTER: }...

### N36 [S4] line 422
NOTE: unclear what is meant here. Do not comment on an "earlier version of the paper". I think here we should, in very simple terms, say what are the consequence of capacity oalone and surchage alone
BEFORE: ...\paragraph{Capacity and surchage.} 
AFTER: Over the 2026 run, the bulk shipments that leave their normal route for an alternative on their own modes are worth \ChanBulkAltBn{} billion USD in the referenc...

### N37 [S4] line 445
NOTE: I don't understand what this paragraph bring. Consider removing?
BEFORE: ...\paragraph{Supplier weights through the season.}
AFTER:  In the link-level run, the \SupWeightBuyers{} German buyer region--sectors with at least one supplier pair cut at Kaub in the August episode (weeks 7--9) keep ...

### N38 [S4] line 447
NOTE: align with table caption
BEFORE: ...\paragraph{The gate week by week.} 
AFTER: Table~\ref{tab:gate} gives, for every profile week of the reference run, the gauge, the loading share and the tonnage that the capacity limits of the Rhine chai...

### N39 [S4] line 452
NOTE: add cell above the last 3 headers with "Flows (mUSD)"
BEFORE: ...\caption{\textbf{Weekly flow through Kaub, 2026 reference run.} For each week: the status of the gauge, its weekly mean (cm), the corresponding loading share, and the tonnage (kt) that the gates of the Rhine chain cut, re-sent on another route and withheld (returned to the supplier's inventory)}
AFTER: ...

### N40 [S4] line 455
NOTE: replace by total flow
BEFORE: ...week & start & status & Kaub gauge (cm) & loading share & cut 
AFTER:  & rerouted & blocked \\...

### N41 [S4] line 490
NOTE: simply remove this paragraph
BEFORE: ...\paragraph{Conservation and stationarity.} 
AFTER:  A cut flow is either rerouted or blocked, that is, formally returned to the supplier's inventory, so the tonnage leaving Kaub equals the tonnage entering it.  ...

### N42 [S4] line 492
NOTE: we don't need to explain this revision. Consider removing.
BEFORE: ...\paragraph{Sensitivities of the revision.}
AFTER:  Table~\ref{tab:revision} gives the runs made after the review of 5 October 2026 on the rebuilt loading curve. The bounded substitution by rail is the largest: ...

### N43 [S4] line 530
NOTE: do 2 paragraphs, these are different things
BEFORE: ...\paragraph{The levers under finite rail, and the memory at a 15-day refill time.}
AFTER:  Table~\ref{tab:cross} gives the two crossed experiments of 2 November 2026. Under the 50 kt rail ceiling each single lever removes a larger share of a smaller ...

### N44 [S4] line 535
NOTE: I would do two tables insteand of two blocks, these are different things.
BEFORE: ...\caption{\textbf{The levers under finite rail, and the memory of the season at a 15-day refill time.
AFTER: } Batch of 2 November 2026 (\texttt{jobs\_20261102\_cross.txt}). Upper block: German loss (\% of a quarter) with each single lever, and the share of its base's ...

### N45 [S4] line 548
NOTE: what is the baseline?
BEFORE: ... & \multicolumn{2}{c}{\textit{refill time 30 days}} & \multicolumn{2}{c}{\textit{refill time 15 days
AFTER: }} \\...

### N46 [S5] line 595
NOTE: this paragraph could be removed, this is already described in main text, no? douyble check
BEFORE: ...e go to households and to chemical and power plants whose output barely moves, but the fuel that the French haulers run short of comes in part from German refineries. Tables of the disrupted chains by buyer country and input are generated by \texttt{extract\_link\_flows.py} and deposited with the run tables (Data availability). 
AFTER: ...

### N47 [S6] line 597
NOTE: do we really need to extend on that? I would reduce this section to a paragrah in the previous section and just give the main message - sounds repeating S8 choice 1
BEFORE: ...\subsection*{S6 Two representations of the river} 
AFTER: ...

### N48 [S7] line 629
NOTE: I wouldn't list all of that. The list can be a CSV in Zenodo. Just replace by a more standard table which list what parameter with change, what are the alternative value tested, with a short description in the text of the approach (one at a time, etc.), and which part of the paramter we did not touch and why
BEFORE: ...Table~\ref{tab:runs}
AFTER:  lists the \NRuns{} runs of the batches of 2, 3 and 6 November 2026 on the capacities per cargo class (the paper set of \NRunsMain, the paired levers of \NRunsP...

### N49 [S8] line 791
NOTE: this is hard to understand... One could argue that it is a lever, as much as updating the barge fleet is
BEFORE: ...Rail is a bounded substitute in this study, not a lever
AFTER: . In the model, container freights can reroute via rail and road without a limit, but bulk cannot switch. This assumption reflects that tank barges and ore trai...

### N50 [S8] line 797
NOTE: where does this 6.7 Mt come from?
BEFORE: ...    \item A higher ceiling of 140 kt is analyzed, loosely based on Appendix B of Ademmer (2023)'s working paper, which estimated +0.07\,\% of rail tonnage per low-water day over a 30-day low-water, applied to 6.7 Mt of rail freight a week
AFTER: . This estimate covers all cargo types, including containers, which we already allow to switch and are not counted on this ceiling, so the value of 140 kt appli...

### N51 [S9] line 855
NOTE: maybe clearer to put the equation
BEFORE: ...calibrated regression model of this event; see Table~2, column~1. This regression models the growth of the German production index based on the change in the number of days of the month with Kaub below 78\,cm, with coefficients $-0.034$ (standard error 0.012), $-0.024$ (0.014) on its lag and $-0.172$ (0.119) on the lagged growth
AFTER: ....

### N52 [S9] line 857
NOTE: why daily?
BEFORE: ...Applied to the low-water days of the daily 
AFTER: gauge record (29\~cm, 14\~cm, 31\~cm, 30\~cm and 3\~cm from August to December 2018), this equation produces an induced loss of cumulated growth, which is used ...

### N53 [S9] line 857
NOTE: maybe add the figure nb
BEFORE: ...Applied to the low-water days of the daily gauge record (29\~cm, 14\~cm, 31\~cm, 30\~cm and 3\~cm from August to December 2018), this equation produces an induced loss of cumulated growth, which is used as the losses shown in the Results
AFTER: . The band shown on FiguresXXX is a Monte Carlo over independent normal draws of the three coefficients at their standard errors (the covariance is not publishe...

### N54 [S9] line 857
NOTE: add references
BEFORE: ...Applied to the low-water days of the daily gauge record (29\~cm, 14\~cm, 31\~cm, 30\~cm and 3\~cm from August to December 2018), this equation produces an induced loss of cumulated growth, which is used as the losses shown in the Results. The band shown on FiguresXXX
AFTER:  is a Monte Carlo over independent normal draws of the three coefficients at their standard errors (the covariance is not published, so the band is indicative)....

### N55 [S9] line 859
NOTE: check it is correct
BEFORE: ...The model's counterpart is the loss of German industrial production, which we build from the same aggregation as done in~\citep{ademmer2023}: sum each sector's weekly loss from August to December, weighted by its value added in the German input--output table, over sections B to D (the index's coverage)
AFTER: ....

### N56 [S9] line 861
NOTE: I think this is enough, no? the peak november month is actually not useful on top. Consider realigning the terminology of the two options. Find better wording if needed.
BEFORE: ...y proportional to the loading factor. We observed that the industrial production index was already falling in August 2018, two months before the first week in which any vessel class stopped sailing. Option (i) captures the right onset, whereas, with option (ii), losses only start mid-October; see able~\ref{tab:representations}. 
AFTER: ...

### N57 [S9] line 866
NOTE: but those values in a small tables
BEFORE: ...iplied by 0.75, 1.25, 1.5 and 2.  the industrial shortfall is \LadderIntA, \LadderIntB{} and \LadderIntD{} percent-months and the total loss \LadderA, \LadderB{} and \LadderD\,\% of a quarter; at three quarters of the balance-sheet value (run of 6 November 2026) they are \LadderIntZ{} percent-months and \LadderZ\,\% of a quarter
AFTER: , nearer the benchmark's \RecordInt{} than any other rung but still below its one-standard-deviation band. The balance-sheet value is kept: it is the level the ...

### N58 [S9] line 866
NOTE: so it shouldn't be in a section that is about modeling choice, rather in sensitivity!
BEFORE: ...et value (run of 6 November 2026) they are \LadderIntZ{} percent-months and \LadderZ\,\% of a quarter, nearer the benchmark's \RecordInt{} than any other rung but still below its one-standard-deviation band. The balance-sheet value is kept: it is the level the accounts document, and the ladder is a sensitivity, not a calibration
AFTER: ; on the index measure it gives \ModelInt{} percent-months, below the benchmark's one-standard-deviation band and inside its 95\,\% band....

### N59 [S9] line 868
NOTE: it is not modeling choice but sensitivity
BEFORE: ...\paragraph{The supplier networks, the loading curve and the number of suppliers.
AFTER: } Across ten further versions of the supplier network the deepest month is November in every one, and the cumulated industrial shortfall is \ModelIntEnsMean\,$\...

### N60 [S10] line 871
NOTE: this should go much earlier as these are not results, I suggest S4 after calibration
BEFORE: ...\subsection*{S10 Weekly sequence and model specifications
AFTER: }...

### N61 [S10] line 883
NOTE: this paragraph is misplaced, consider groupping that with "S8 rail"
BEFORE: ...\paragraph{The fleet lever.
AFTER: } The low-water fleet replaces the loading curve by that of a fleet of shallow-draft vessels: the central table with its loading raised by 0.10 between 15 and 5...

## Text edits (notes stripped), by line
### E01 [S1] old 5-5 -> new 5-5 (replace)
line 5: \paragraph{Agents.} Firm agents are the disaggregation of each region- [...] d employment locations, by the \texttt{firm-extractor} package of the [-model-]{+model.+} [-(one-]{+Sectors use different+} source [-per-]{+data+} [-sector-]{+for+} [-in-]{+this+} [-an-]{+spatial+} [-ordered-]{+downscaling+} [-preference,-]{+procedure.+} [-facility-]{+For+} [-points-]{+crops+} [-kept,-]{+(A01),+} [-gridded-]{+the+} [-sources-]{+SPAM+} [-aggregated-]{+2020+} [-to-]{+crop-production grid is clipped+} NUTS3 and placed at the weighted [-centroid,-]{+centroid.+} [-population as the last fallback). Eleven-]{+Ten+} sectors use facility [-data:-]{+data,+} [-crops-]{+kept+} [-(A01)-]{+explicitly+} [-the-]{+as+} [-SPAM 2020 crop-production grid;-]{+points:+} coal mines (B05)[--]{+ frm+} the Global Energy Monitor [--]{+(GEM) +}coal-mine tracker with Climate [-TRACE;-]{+TRACE,+} oil and gas fields (B06) [--]{+from +}the [-Global Energy Monitor-]{+GEM+} oil and gas extraction [-tracker;-]{+tracker,+} metal-ore mines (B07)[--]{+ from+} Climate TRACE and the FINEPRINT mine [-database;-]{+database,+} refineries (C19), chemical plants (C20), pulp and paper mills (C17--18) and aluminum smelters (C24B) [--]{+from +}Climate TRACE's 2022 facility [-activity;-]{+activity,+} cement plants (C23) [--]{+from +}the [-Global Energy Monitor-]{+GEM+} cement [-tracker;-]{+tracker,+} steel mills (C24A) [--]{+from +}the [-Global Energy Monitor-]{+GEM+} steel tracker; power (D) [--]{+from +}the [-Global Energy Monitor-]{+GEM+} power trackers aggregated to NUTS2 capacity. The 39 other sectors are [-placed-]{+downscaled+} [-on-]{+using+} NUTS3 employment [-of-]{+in+} the regional accounts. Facility statuses are taken [-at-]{+from+} the 2022 [-reference year of the accounts, so that plants idled since are kept;-]{+accounts.+} \NFirms{} agents after [-the removal of-]{+removing+} disconnected ones, nine per region--sector on average. Households are [...] entroid. Every agent attaches to the nearest road node of the network.

### E02 [S1] old 7-7 -> new 7-7 (replace)
line 7: \paragraph{Network.} The trans-European transport network (TEN-T, extr [...]  nodes: roads (2,979 edges), railways (4,261), inland waterways (461, [--]{+including 30 for +}the Rhine from Basel to [-Rotterdam as a chain of thirty named reaches),-]{+Rotterdam),+} sea lanes (948) and multimodal connectors at terminals and ports (1,4 [...] modes and cargo class, with a fee by seaport (Table~\ref{tab:rates}). [-Cargo classes follow the-]{+Each+} supplying [-sector:-]{+sector uses one cargo class:+} agriculture and mining products are dry bulk, fuels and basic chemicals [--]{+are +}liquid bulk, everything else [-containers;-]{+is containerized;+} crude oil and natural gas travel by [-pipeline-]{+pipeline,+} [-outside-]{+not+} [-the-]{+explicitly+} [-network.-]{+modeled.+}

### E03 [S1] old 10-9 -> new 10-10 (insert)
+ % I have done edits here directly. Would be better that caption, at least, are hard coded in the .tex as the source. What's the value added of using the py generator? Makes things harder to update. Consider using the .tex as source of the truth.

### E04 [S1] old 12-12 -> new 13-13 (replace)
line 13: \caption{\textbf{Transport cost [-parameters and-]{+parameters:}+} the [-rate evidence.} The-]{+baseline+} values[- used by every run of this paper (as the reference run of the batch of 2 November 2026 records them: the scope's configuration with the overrides of the job lists, which set rail costs by country, waterway costs by waterway, seaport fees by port and the containers' value of time on the waterway)-]{++} and the evidence behind them. Operator costs are the Panteia cost fig [...] ted on the modal split (Fig.~S2). ARA: Amsterdam--Rotterdam--Antwerp.}

### E05 [S1] old 23-27 -> new 24-28 (replace)
line 24: road, containers and dry bulk & 0.050 & A full-load long-haul rate. No [...] eter for a tractor-semitrailer at fleet average, empty legs included. [-Road is never a line-haul mode for bulk (Methods). -]{++}Calibrated. \\
line 25: road, liquid bulk & 0.130 & [-Road tankers: dedicated equipment and cleaning. -]{++}No [-rate-]{+direct+} [-evidence;-]{+evidence,+} set[--]{+ together+} with the rail value so that the German liquid-bulk split by mode matches Eurostat [-2023 (28 / 42 / 30 road / rail / waterway). Calibrated.-]{+2023.+} \\
line 26: rail, containers and dry bulk & 0.032 (0.038 in 10 countries: AT, BG,  [...]  SK) & Within the range of block-train and intermodal rates in Europe [-(0.02--0.04);-]{+(0.02--0.04),+} [-lowered-]{+calibrated+} [-from 0.044 in-]{+to+} the [-calibration of the-]{+Eurostat+} modal [-split (Fig.~S2). Calibrated. Dearer in the countries named, where the model over-used rail (calibration round 2, Section~S2).-]{+split.+} \\
line 27: rail, liquid bulk & 0.085 (0.100 in 10 countries: AT, BG, CZ, ES, FR, HU, IT, PL, SI, SK) & [-Tank-]{+As+} [-cars:-]{+road,+} [-as-]{+liquid bulk: so that+} the [-road-]{+German+} [-tankers.-]{+liquid-bulk+} [-Calibrated.-]{+split by mode matches Eurostat 2023.+} \\
line 28: inland waterway, dry bulk & 0.010 on the Rhine, 0.010--0.040 on the other waterways &[--]{+ Collected evidence:+} Push-convoy cost 0.008--0.012 EUR per tonne-kilometer (ores 0.009, co [...]  so grain-type flows in single vessels are under-priced in the model. [-Set by waterway in calibration round 5 (Section~S2): the Rhine's-]{+Same+} values [-hold on-]{+for+} 8 other[- named-]{++} waterways (Amsterdam-Rhine canal, Ghent-Terneuzen canal, IJssel, IJsselmeer, Noordzeekanaal, Nord-Ostsee-Kanal, Scheldt, Scheldt-Rhine [-link),-]{+link).+} [-the-]{+Values+} [-others-]{+for other waterways+} are up to 4 times [-dearer (about the same factors for every cargo class).-]{+higher.+} \\

### E06 [S1] old 30-30 -> new 31-31 (replace)
line 31: sea & 0.0015 & [-The-]{+,+} [-prior-]{+do+} [-of-]{+not influence+} the [-scope; sea lanes are unconstrained in this study.-]{+results.+} \\

### E07 [S1] old 33-34 -> new 34-35 (replace)
line 34: containers & 1.00 [-& On road-]{+(road+} and [-rail;-]{+rail);+} 0.32 [-on the waterway and-]{+(waterways);+} 0.15 [-at-]{+(sea)+} [-sea.-]{+&+} A cargo-side (inventory) value: the vessel-side cost of time is 0.02- [...] for KiM); 0.20 in the European Commission's charging study of 2005. \\
line 35: dry and liquid bulk & 0.08 [-&-]{+(all+} [-All-]{+modes)&+} [-modes.-]{+.+} \\

### E08 [S1] old 50-50 -> new 51-51 (replace)
line 51: \paragraph{Inventories.} The inventory targets are days of goods input [...] ather than an inventory. The critical-input weights are the survey of [-ref.~\citep{pichler2022}-]{+Pichler et al. (2022)~\citet{pichler2022}+} mapped to the 50 sectors [-(Table~\ref{tab:criticality});-]{+(Table~\ref{tab:criticality}).+} [-eighteen-]{+We assume that 18+} commodity-like products are pooled across regions, [-the-]{+which+} [-homogeneous-]{+is+} [-or-]{+based+} [-reference-priced products of-]{+on+} the classification of [-ref.~\citep{rauch1999}:-]{+Rauch (1999).~\citep{rauch1999}:+} crops and livestock products (A01), forestry products (A02), fish (A0 [...] on-ferrous metals (C24B), electricity and gas (D) and water and waste [-(E);-]{+(E).+} [-the-]{+The+} differentiated products (machinery, vehicles, electronics, pharmaceuticals, construction, real estate and [-the -]{++}services) [-stay-]{+are+} [-keyed-]{+region-specific+} [-by-]{+and+} [-region.-]{+cannot be substituted.+}

### E09 [S1] old 55-55 -> new 56-56 (replace)
line 56: \caption{\textbf{Stock targets by buying industry.} Days of consumptio [...] ver the cost of materials; EKBG: the German reserve-plant act of 2022.[- -]{+  +}The lower block gives the input-specific targets that override the industry value, with the modeling reason where the model departs from the physical figure.}

### E10 [S1] old 58-58 -> new 59-59 (replace)
line 59: industry & & days & lean & grade & [-basis-]{+evidence+} \\

### E11 [S1] old 62-62 -> new 63-63 (replace)
line 63: industry & & days & lean & grade & [-basis-]{+evidence+} \\

### E12 [S1] old 128-128 -> new 129-129 (replace)
line 129: \caption{\textbf{The criticality survey mapped to the 50 sectors.} Eac [...] le (OECD ICIO, 2025 edition) is matched to one industry of the survey [-used-]{+of+} [-by-]{+Pichler+} [-ref.~\citep{pichler2022}-]{+et+} [-(55-]{+al. (2022)~\citep{pichler2022}, which are the 55+} industries of the World Input--Output [-Database,-]{+Database+} [-NACE-]{+(NACE+} Rev.~2); the note gives the judgment where the match is not [-one to one.-]{+one-to-one.+} The counts are, for the sector as a buyer, how many of its 50 input sectors the survey rates [-critical-]{+"critical"+} (output limited by the input), [-important-]{+"important"+} (a depleted input halves output) and non-critical [-(other),-]{+("other"),+} and, for the sector as an input, how many buyers rate it critical [-(critical-]{+("critical+} [-for).-]{+for").+} [-Imports carry-]{+In+} the [-sector of the exporting bloc, so an imported chemical is as critical as a domestic one; an unrated pair is treated as critical; in the model-]{+model,+} an input [-also has to exceed-]{+below+} 2\,\% of the buyer's input costs [-to-]{+is+} [-bind-]{+considered+} [-(Methods).-]{+non-critical.+} Over the 2,500 [-cells:-]{+sector-to-sector pairs:+} 18\,\%[--]{+ of input are+} critical, 9\,\% [--]{+are +}important,[--]{+ and+} 73\,\% non-critical.}

### E13 [S1] old 131-131 -> new 132-132 (replace)
line 132: [--]{+model's +}sector & [-survey-]{+survey's sector+} & note & \multicolumn{3}{c}{inputs rated} & critical \\

### E14 [S1] old 145-145 -> new 146-146 (replace)
line 146: B05 Mining of coal and lignite & B & the [-survey's-]{+survey has only+} one mining industry & 11 & 2 & 37 & 12 \\

### E15 [S1] old 153-153 -> new 154-154 (replace)
line 154: C17\_18 Paper products and printing & C17 & [-paper,-]{+paper is+} the [-larger-]{+largest+} of the two and the one with physical inputs & 11 & 11 & 28 & 4 \\

### E16 [S2] old 200-200 -> new 201-208 (replace)
- The baseline reproduces the input--output accounts by construction. Its transport flows were calibrated in six rounds in October 2026, after the first version of this paper, against four kinds of statistic: the inland modal split by country in tonne-kilometers (Eurostat 2023), the modal split by cargo class in Germany and the Netherlands (the NST divisions of the same source), the tonnage along the Rhine (the CCNR cross-section counts at Emmerich [...] observation over 187 items (the seaports weighted 0.30, the modal split by country 0.25 and by cargo class 0.20, the Rhine 0.15, the German waterway sections 0.10), fell from \FlowScoreFirst{} for the first version to \FlowScore; it served to compare the candidates of each round and is not a result.
+ The baseline reproduces the input--output accounts by construction. Its transport flows were calibrated against four kinds of statistic: the inland modal split by country in tonne-kilometers (Eurostat 2023), the modal split by cargo class in Germany and the Netherlands (the NST divisions of the same source), the tonnage along the Rhine (the CCNR cross-section counts at Emmerich and Iffezheim and its estimates between them \citep{ccnr2023}), and the gross weight of goods handled by the forty largest seaports (Eurostat 2023) together with the tonnage carried on the German waterway sections (Destatis, table 46321-0014, 2023). To match those targets, we adjusted four main families of logistic parameters.
+ \begin{itemize}
+     \item The baseline waterway rate applies to the Rhine and its Dutch branches (Scheldt and the Kiel canals) per cargo type: 0.010 USD per tonne-kilometer for dry bulk, 0.038 for liquid bulk, 0.022 for containers. We applied multipliers to other waterways: the Albert canal and the Meuse pay 1.2 times it, the Main, Moselle, Neckar, Saar, Danube, Seine, Rh\^one, Sa\^one and the Ruhr canals 1.3, the Lek 1.5, the Mittellandkanal, the Elbe lateral canal, the Main--Danube canal, the K\"ustenkanal and the Berlin waterways 2, the Weser 2.2, the Elbe, the Oder and the Vltava 3, and the Po system 4. 
+     \item The rail rate is 20\,\% higher in France, Italy, Austria, Spain, Poland, Czechia, Hungary, Slovakia, Slovenia and Bulgaria.
+     \item The loading fee at a seaport follows a ladder in the port's observed throughput $T$: $3\log_{10}(100\,\mathrm{Mt}/T)$ USD per tonne for containers, clipped to 0--12, and a third of it for other cargo. One exception is Amsterdam, were low values are the minimal rate is 0.75 where the ladder gives less . The ladder stands in for liner and feeder services that call at large ports, not small ones, which a network that reaches every coastal node at one sea tariff does not represent. 
+     \item The value of time of a container on the waterway is 0.32 instead of 0.35 USD per tonne-hour. \textit{Ceteris paribus}, at 0.35 no container is put on barges on the Rotterdam--Ruhr corridor; at 0.30 barge containers overshoot the observed tonnage by three times. A value of 0.32 USD per tonne-hour gives the observed order of magnitude at Kaub. 
+ \end{itemize}
+ No other parameters were adjusted to fit the logistic data.

### E17 [S2] old 202-202 -> new 210-210 (replace)
line 210: \paragraph{The fit.} Figures~S2 and S3 and Table~\ref{tab:ports}. The  [...] aly \ModalITRoad{} / \ModalITRail{} / \ModalITIww{} against 88 / 12 / [-0.-]{+0+} [-Road is under-represented by construction in Germany, the Netherlands, Belgium, France and Austria: agents sit at NUTS2 and NUTS3 points, so the intra-regional haulage that the statistics count does not exist in the model, and the shares of rail and waterway are overstated by as much. In Germany by cargo class, on the German edges, the model gives general cargo \CargoGeneralRoad{} / \CargoGeneralRail{} / \CargoGeneralIww{} against 68 / 27 / 5, dry bulk \CargoDryRoad{} / \CargoDryRail{} / \CargoDryIww{} against 53 / 27 / 20 and liquid bulk \CargoLiquidRoad{} / \CargoLiquidRail{} / \CargoLiquidIww{} against 28 / 42 / 30: the bulk that the shock concerns travels on the right modes, with the waterway share of liquids nearly a third too high. On the Rhine (Fig.~S3), Kaub carries \KaubMt~Mt a year against the 50--60 of the counts, of which \KaubContMt{} of containers against about 10 \citep{ccnr2023}, \KaubDryMt{} of dry bulk and \KaubLiquidMt{} of liquid bulk; Koblenz \RhineKoblenzMt{} against 55--60, Bonn \RhineBonnMt{} against 65, Cologne \RhineKoelnMt{} against 80, Duisburg \RhineDuisburgMt{} against 110, Emmerich \RhineEmmerichMt{} against 118, the Waal at Tiel \RhineTielMt{} against 125, the delta below Dordrecht \RhineDordrechtRotterdamMt{} against 140, and the Upper Rhine at Basel \RhineBaselMt{} against 5.5, Strasbourg \RhineStrasbourgMt{} against 16 and Karlsruhe \RhineKarlsruheMt{} against 22. The first version carried no container past Kaub, a quarter less than observed on the Lower Rhine and a tenth of the Waal's tonnage; the river from Mannheim to the border is now within \RhineDevMaxPct\,\% of the counts, above them on the Middle Rhine and below them from Cologne to Duisburg (a quarter below at D\"usseldorf and Duisburg), where the missing tonnage is the Ruhr's canal-side traffic (below). The German waterways as a whole carry \DEWaterTkmBn{} billion tonne-kilometers against 41.5 observed; by section, the Rhine at the border \BasinRhineMt{} against 118~Mt, the Main \BasinMainMt{} against 12, the Neckar \BasinNeckarMt{} against 4, the Danube \BasinDanubeMt{} against 3, the Rhine--Herne canal \BasinRheinHerneMt{} against 11, the Elbe \BasinElbeMt{} against 5 and the Moselle \BasinMoselleMt{} against 6. The seaports (Table~\ref{tab:ports}): within 10\,\% at Hamburg (\PortHamburgMt~Mt against 100), Le Havre--Rouen (\PortHavreMt{} against 76), Marseille (\PortMarseilleMt{} against 67), Genoa (\PortGenoaMt{} against 47), Gothenburg (\PortGothenburgMt{} against 35) and Bilbao (\PortBilbaoMt{} against 32); within a quarter at Dublin (\PortDublinMt{} against 25), Nantes (\PortNantesMt{} against 28), Dunkirk (\PortDunkirkMt{} against 35) and Bremerhaven (\PortBremerhavenMt{} against 39); a third below at Antwerp-Bruges (\PortAntwerpMt{} against 242) and Amsterdam (\PortAmsterdamMt{} against 81); about two fifths below at Barcelona (\PortBarcelonaMt{} against 51), Ghent (\PortGhentMt{} against 30) and Valencia (\PortValenciaMt{} against 62); and the gaps listed next.-]{+.+}

### E18 [S2] old 204-204 -> new 212-212 (replace)
line 212: [-\paragraph{The-]{+Road+} [-gaps,-]{+is under-represented by construction in Germany, the Netherlands, Belgium, France+} and [-why-]{+Austria:+} [-they-]{+agents+} [-do-]{+sit at NUTS2 and NUTS3 points, so the intra-regional traffic that the statistics count does+} not [-bear-]{+exist in the model, and the shares of rail and waterway are overstated by as much. In Germany by cargo class,+} on the [-study.}-]{+German+} [-The-]{+edges,+} [-loss-]{+the+} [-of-]{+model+} [-this-]{+gives+} [-study-]{+general+} [-rests-]{+cargo \CargoGeneralRoad{} / \CargoGeneralRail{} / \CargoGeneralIww{} against 68 / 27 / 5, dry bulk \CargoDryRoad{} / \CargoDryRail{} / \CargoDryIww{} against 53 / 27 / 20 and liquid bulk \CargoLiquidRoad{} / \CargoLiquidRail{} / \CargoLiquidIww{} against 28 / 42 / 30: the bulk that the shock concerns travels+} on the [-tonnage-]{+right+} [-that-]{+modes,+} [-crosses Kaub and its composition, on-]{+with+} the [-rail-]{+waterway+} [-and road alternatives-]{+share+} of [-the-]{+liquids+} [-Rhine's shippers and on the location of the German industrial users; the preceding paragraph gives these within-]{+nearly+} a third [-of-]{+too+} [-the observations. The port tonnages are not calibrated: \PortsWithinThirty{} of the forty largest seaports are within 30\,\% of the Eurostat counts (Table~\ref{tab:ports}), the largest gaps being crude oil, transshipment and imports landed at the coast nearest their buyer, which do not cross Kaub. The residuals are of four kinds, three of them off the Kaub path.-]{+high.+}

### E19 [S2] old 206-206 -> new 214-214 (replace)
line 214: [-\emph{Crude,-]{+On+} [-gas-]{+the+} [-and-]{+Rhine+} [-transshipment.}-]{+(Fig.~S3),+} [-Rotterdam-]{+Kaub+} carries [-\PortRotterdamMt~Mt-]{+\KaubMt~Mt+} [-in-]{+a year against+} the [-model against 402 handled, Antwerp-Bruges \PortAntwerpMt{} against 242, Trieste \PortTriesteMt{} against 51, Sines \PortSinesMt{} against 40, Wilhelmshaven \PortWilhelmshavenMt{} against 30, Zeeland \PortZeelandMt{} against 37. The gross weight-]{+50--60+} of the [-statistics-]{+counts,+} [-counts-]{+of+} [-crude-]{+which+} [-oil-]{+\KaubContMt{} of containers against about 10 \citep{ccnr2023}, \KaubDryMt{} of dry bulk+} and [-its products, gas and coal, and the sea-to-sea transshipment-]{+\KaubLiquidMt{}+} of [-containers;-]{+liquid+} [-the-]{+bulk;+} [-model's-]{+Koblenz+} [-flows-]{+\RhineKoblenzMt{}+} [-are-]{+against+} [-the-]{+55--60,+} [-traded-]{+Bonn+} [-goods-]{+\RhineBonnMt{}+} [-of-]{+against+} [-the-]{+65,+} [-input--output-]{+Cologne+} [-table-]{+\RhineKoelnMt{}+} [-converted-]{+against+} [-to-]{+80,+} [-tonnes,-]{+Duisburg+} [-crude-]{+\RhineDuisburgMt{}+} [-and-]{+against+} [-gas-]{+110,+} [-are pipelined out of the network by construction (Methods), and a cargo lands once, at the port from which it reaches its buyer. Rotterdam's model tonnage is its hinterland traffic in traded goods, and the Rhine at the Dutch border,-]{+Emmerich+} \RhineEmmerichMt{} against 118, [-shows-]{+the+} [-that-]{+Waal at Tiel \RhineTielMt{} against 125,+} the [-part-]{+delta+} [-of-]{+below+} [-it-]{+Dordrecht+} [-bound-]{+\RhineDordrechtRotterdamMt{}+} [-for-]{+against 140, and+} the [--]{+Upper +}Rhine[- basin is there. The transshipment hubs are the same residual-]{++} at [-its-]{+Basel+} [-extreme: Algeciras \PortAlgecirasMt{}-]{+\RhineBaselMt{}+} against [-79,-]{+5.5,+} [-Piraeus-]{+Strasbourg+} [-\PortPiraeusMt{}-]{+\RhineStrasbourgMt{}+} against [-45,-]{+16+} [-Gioia-]{+and+} [-Tauro-]{+Karlsruhe+} [-\PortGioiaTauroMt{}-]{+\RhineKarlsruheMt{}+} against [-35. None of this tonnage enters Germany by the river.-]{+22.+}

### E20 [S2] old 208-208 -> new 216-216 (replace)
line 216: [-\emph{The nearest-coast landing.} -]{++}The [-maritime-]{+German+} [-network-]{+waterways+} [-reaches every coastal node at one sea tariff and without-]{+as+} a [-limit-]{+whole+} [-on-]{+carry+} [-ship-]{+\DEWaterTkmBn{}+} [-size,-]{+billion+} [-so-]{+tonne-kilometers+} [-an-]{+against+} [-import-]{+41.5+} [-lands-]{+observed; by section, the Rhine+} at the [-node-]{+border+} [-nearest-]{+\BasinRhineMt{}+} [-its-]{+against+} [-buyer unless a fee turns it away;-]{+118~Mt,+} the [-ladder-]{+Main+} [-of fees sent 140~Mt back to the large ports but did not remove the mechanism. It remains at Venice and its lagoon (Venice, Chioggia, Monfalcone and Porto Nogaro together \PortLagoonMt~Mt against 28), at Szczecin (\PortSzczecinMt{}-]{+\BasinMainMt{}+} against 12, [-with-]{+the+} [-Gda\'nsk-]{+Neckar+} [-at \PortGdanskMt{}-]{+\BasinNeckarMt{}+} against [-80 as-]{+4,+} the [-other-]{+Danube+} [-side-]{+\BasinDanubeMt{}+} [-of-]{+against 3,+} the [-same-]{+Rhine--Herne+} [-coin),-]{+canal+} [-Burgas (\PortBurgasMt{}-]{+\BasinRheinHerneMt{}+} against [-17),-]{+11,+} [-Oslo-]{+the+} [-(\PortOsloMt{}-]{+Elbe \BasinElbeMt{}+} against [-5), M\'alaga (\PortMalagaMt{} against 2), S\`ete, Bordeaux, Lorient, Waterford-]{+5+} and the [-Swedish-]{+Moselle+} [-lake ports; the \SecPortsN{} ports outside the top forty carry \SecPortsMt~Mt-]{+\BasinMoselleMt{}+} against [-\SecPortsObsMt. These are Adriatic, Baltic, Atlantic and Mediterranean landings whose hinterlands do not touch the Rhine basin. The Rhine's own imports enter through Rotterdam, Antwerp, Amsterdam, Hamburg and Bremerhaven, where the model is within a third of the counts except at Rotterdam, whose gap is crude and transshipment (above), and the one North Sea choice this mechanism moved during the calibration, Amsterdam against Rotterdam, changes the fee a cargo pays and not whether it crosses Kaub.-]{+6.+}

### E21 [S2] old 210-210 -> new 218-218 (replace)
line 218: [-\emph{The-]{+The+} [-Dutch-]{+seaports+} [-delta-]{+(Table~\ref{tab:ports}): within 10\,\% at Hamburg (\PortHamburgMt~Mt against 100), Le Havre--Rouen (\PortHavreMt{} against 76), Marseille (\PortMarseilleMt{} against 67), Genoa (\PortGenoaMt{} against 47), Gothenburg (\PortGothenburgMt{} against 35) and Bilbao (\PortBilbaoMt{} against 32); within a quarter at Dublin (\PortDublinMt{} against 25), Nantes (\PortNantesMt{} against 28), Dunkirk (\PortDunkirkMt{} against 35) and Bremerhaven (\PortBremerhavenMt{} against 39); a third below at Antwerp-Bruges (\PortAntwerpMt{} against 242) and Amsterdam (\PortAmsterdamMt{} against 81); about two fifths below at Barcelona (\PortBarcelonaMt{} against 51), Ghent (\PortGhentMt{} against 30) and Valencia (\PortValenciaMt{} against 62);+} and the [-Ruhr-]{+gaps+} [-canals.}-]{+listed+} [-The Netherlands' inland transport is a third of its observed tonne-kilometers (\NLTkmBn{} billion against 111) and its waterways half (\NLWaterTkmBn{} against 41.6): the country's transport work is short-haul and port-related, the haulage between the terminals of the delta and the intra-regional traffic that agents at NUTS3 points do not generate. The Waal and the delta below Dordrecht carry \RhineTielMt{} and \RhineDordrechtRotterdamMt~Mt against 125 and 140 for the same reason, the traffic between Rotterdam, Antwerp, Amsterdam and the Meuse. In all, the Lower Rhine from Duisburg to Nijmegen carries \LowerRhineGapMin{} to \LowerRhineGapMax\,\% less than observed and the Dutch delta from Tiel to Rotterdam \DeltaGapMin{} to \DeltaGapMax\,\% less, due to missing short-haul traffic between the ports of the delta that agents placed at regional points do not generate. In the Ruhr the Wesel--Datteln canal carries \BasinWeselDattelnMt~Mt against 16, the Dortmund--Ems canal \BasinDortmundEmsMt{} against 15 and the Mittellandkanal \BasinMittellandMt{} against 12: the canal-side plants of Marl, Gelsenkirchen and Dortmund are, in the model, regional points a few kilometers from the Rhine ports, served from them over land, and the canal that reaches them in reality has no demand placed on its banks. The Weser and the K\"ustenkanal, on the contrary, carry \BasinWeserMt{} and \BasinKuestenMt~Mt against 3: the landings at Bremerhaven travel inland by barge, because a sea-to-barge transfer costs less than a sea-to-road one in the model's transfer fees, whereas Bremerhaven's hinterland is served by rail. All of these waterways branch off the Rhine below Kaub or belong to other basins; what moves on them does not pass the Middle Rhine.-]{+next.+}

### E22 [S2] old 212-212 -> new 220-228 (replace)
- \emph{The Upper Rhine and the rail shares.} Above Mannheim the model carries half to two thirds of the counts (Basel \RhineBaselMt{} against 5.5, Strasbourg \RhineStrasbourgMt{} against 16, Karlsruhe \RhineKarlsruheMt{} against 22) while the Mannheim--Mainz reach is above them (\RhineMannheimMainzMt{} against 40): the Rhine's upstream traffic ends too early, in the Rhine--Neckar region, and the Swiss and Alsatian part of it arrives by rail (\Uppe [...] ) after the 20\,\% surcharge, and the German rail share, \ModalDERail{} against 21, carries the short-haul correction above. The share of deep-sea shipping in the maritime tonnage is \DeepSeaShare\,\% against 41.5 observed: intra-European trade uses the sea less in the model than it does in reality.
+ \paragraph{The gaps, and their impacts on the study.} The loss estimated by the model are generated from the disrupted tonnage that crosses Kaub and its composition, from the rail and road alternatives and on the location of the German industrial users; the preceding paragraph gives these within a third of the observations. The port tonnages are not calibrated: \PortsWithinThirty{} of the forty largest European seaports are within 30\,\% of the Eurostat statistics (Table~\ref{tab:ports}), the largest gaps being crude oil, transshipment and imports---these flow do not affect Kaub. The residuals fall into four kinds, three of which are off the Kaub path.
+ 
+ \emph{Crude, gas and transshipment.} The model does not incorporate crude oil, gas, and transshipments, leading to large gaps in tonnage in several ports: Rotterdam carries \PortRotterdamMt~Mt in the model against 402 handled, Antwerp-Bruges \PortAntwerpMt{} against 242, Trieste \PortTriesteMt{} against 51, Sines \PortSinesMt{} against 40, Wilhelmshaven \PortWilhelmshavenMt{} against 30, Zeeland \PortZeelandMt{} against 37. The gross weight stati [...] rasMt{} against 79, Piraeus \PortPiraeusMt{} against 45, Gioia Tauro \PortGioiaTauroMt{} against 35. In the model, flows of traded goods on the Rhine at the Dutch border are \RhineEmmerichMt{} against 118, showing that the hinterland traffic of Rotterdam that matters for the Rhine basin is captured.
+ 
+ \emph{The nearest-coast landing.} The modeling of sea routing is very simple, with a single fee ladder for all ports with cheaper-takes-all routing. There is no modeling of ship size nor capacity. As a consequence, imports tend to land at the seaport nearest its buyer unless. Compared to uniform port fees, the fee ladder proportional to port throughput sent 140~Mt back to the large ports. yet, this allocation rule is not strong enough to correct  [...] n seaports whose hinterlands do not touch the Rhine basin, so they do not impact the model estimates. The Rhine's own imports enter through Rotterdam, Antwerp, Amsterdam, Hamburg, and Bremerhaven, where the model is within a third of the counts, except at Rotterdam, where the gap is explained above.
+ 
+ \emph{Absence of intra-regional traffic} The Netherlands' inland transport is, in the model, a third of its observed tonne-kilometers (\NLTkmBn{} billion against 111) and its waterways half (\NLWaterTkmBn{} against 41.6). A main reason for this gap is that the model abstracts from short-haul, intra-regional traffic, because agents are located at NUTS3 points and do not generate traffic. The Lower Rhine from Duisburg to Nijmegen carries \LowerRhineGapMin{} to \LowerRhineGapMax\,\% less than observed, and the Dutch delta from Tiel to Rotterdam \DeltaGapMin{} to \DeltaGapMax\,\% less, due to missing short-haul traffic between the ports of the delta that agents placed at regional points do not generate. The same applies to the Ruhr region.
+ 
+ \emph{The Upper Rhine and the rail shares.} Even though the tonnages at Kaub matches the observation, the Rhine's upstream traffic ends too early, in the Rhine--Neckar region. Above Mannheim, the model carries half to two-thirds of the counts (Basel \RhineBaselMt{} against 5.5, Strasbourg \RhineStrasbourgMt{} against 16, Karlsruhe \RhineKarlsruheMt{} against 22), while the Mannheim--Mainz reach is above them (\RhineMannheimMainzMt{} against 40). The model carries the flows that Switzerland and Alsace receive by rail; therefore, it understates the exposure of those regions to Kaub .

### E23 [S2] old 217-217 -> new 233-233 (replace)
line 233: \caption{\textbf{The seaports of the calibrated baseline.} The [-forty-]{+40+} largest seaports by gross weight of goods handled (Eurostat 2023, Mt) and the model's tonnage through their connectors; below the line, the ports outside the [-forty-]{+40+} where the model [-lands-]{+route+} 20~Mt[- -]{+  +}or [-more. The note names the mechanism of a gap: crude, gas and sea-to-sea transshipment are counted by the statistics but are not transport flows of the model (crude and gas are pipelined by construction, a cargo lands once); a transshipment hub has no hinterland flow; a nearest-coast landing is an import landed at the coastal node nearest its buyer under the uniform sea tariff. Two of the forty (Sk\"oldvik, Las Palmas) have no connector in the network and are not shown.}-]{+more..}+}

### E24 [S3] old 297-297 -> new 313-313 (replace)
line 313: \paragraph{Gauges.} [-Weekly-]{+We built weekly+} means of the Kaub gauge [-(PEGELONLINE,-]{+from PEGELONLINE, which provide+} raw 15-minute values, [-daily-]{+and+} [-means-]{+records+} [-in legal time; the long-term record of-]{+from+} the Federal Institute of Hydrology for [-2018).-]{+2018.+} The 2026 profile has two vintages (Table~\ref{tab:forecast}): the ver [...] exttt{studies/rhine2026/forecast\_manifest.md} in the code repository.

### E25 [S3] old 299-299 -> new 315-315 (replace)
line 315: \paragraph{Monthly loading shares.} Under the profiles the Kaub reach  [...] r, \KaubPassNovyy\,\% in November and \KaubPassDecyy\,\% in December. [-Computing-]{+If we compute+} the loading share day by day and [-averaging-]{+average+} it over the week, [-instead-]{+rather+} [-of-]{+than+} applying the table to the weekly mean gauge, [-changes -]{++}the tonnage turned away[--]{+ changes+} by \DailyTurnedAwayyy\,\% in 2018 and \DailyTurnedAway\,\% over the observed weeks of 2026.

### E26 [S3] old 301-301 -> new 317-317 (replace)
line 317: \paragraph{Loading table.} Table~\ref{tab:loading} [-is-]{+describes+} [-the source ledger of-]{+how+} the loading [-curve:-]{+curve+} [-for-]{+is+} [-each-]{+built.+} [-anchor,-]{+We gather evidence from various sources, such as XXX, to link gauge values to+} the [-share-]{+shares+} of[- the-]{++} normal tonnage[- that-]{++} the Kaub reach can [-pass-]{+pass,+} [-at-]{+called+} [-that-]{+\textit{fleet+} [-weekly-]{+value}+} [-mean-]{+here.+} [-gauge, the nature of the anchor (a measured count, a vessel payload, a convention, an interpolation or an assumption), its source and date, what the source measures (reach, cargo class, period, denominator) and the transformation to the fleet value; the-]{+The+} model interpolates linearly between [-anchors-]{+those values+} and [-holds the value-]{+stay+} at 0.08 below 5\,cm. The [-anchors-]{+evidence+} [-do-]{+comes+} [-not-]{+from+} [-measure one-]{+various+} quantity: single-vessel payloads, [-an association's -]{++}weekly [-count, a national monthly response and-]{+counts,+} operators' [-thresholds-]{+thresholds.+} [-enter-]{+The+} [-together,-]{+resulting+} [-and-]{+traffic+} [-the fleet value-]{+rate+} is the authors' reading [-of them. The table was rebuilt on the ledger on 6 October 2026: the one weekly count available (KBN, the week to 13 August 2026, 22\,\% of the association's normal at a mean gauge of about 12\,cm) had been attributed to the 25\,cm row of the earlier version, whose values at the lowest gauges (0.05 below 5\,cm, 0.12 at 15\,cm) sat below it; the rebuilt table takes 0.24 at 15\,cm, 0.28 at 25 and 0.30 at 30 (single-vessel loads times the fleet's redeployment) and 0.08 below 5\,cm, and is unchanged -]{++}from [-55\,cm-]{+those+} [-up. Every run of the batches of 7 October 2026 (Table~\ref{tab:runs}) uses the rebuilt table; the priced-river runs of Section~S6 and of Fig.~\ref{fig:validation}, which predate the rebuild, are on the earlier table, kept in the code repository (\texttt{draught\_table\_v1.csv}) with the runs of September that used it. Computing the loading share day by day and averaging over the week changes the tonnage turned away by less than 1\,\% in both years.-]{+values.+}

### E27 [S3] old 306-306 -> new 322-322 (replace)
line 322: \caption{\textbf{The loading curve [-as-]{+at+} [-a source ledger.}-]{+Kaub.}+} Share of the normal tonnage that the Kaub reach can pass at a weekly mean [-gauge (fleet, the column the model uses) and the loading share of a single large vessel (for comparison),-]{+gauge,+} with, for each [-anchor,-]{+value,+} [-its-]{+the+} [-nature-]{+data+} [-(measured,-]{+source,+} [-a-]{+what+} [-convention,-]{+it+} [-interpolated-]{+originally+} [-or assumed), its source-]{+measures,+} and [-date,-]{+how+} [-what the source measures (reach, cargo class, period, denominator) and the transformation to the fleet value. Linear between anchors; below 5\,cm the fleet value-]{+it+} is [-held at 0.08. The anchors mix single-vessel payloads, an association's weekly count, a national monthly response and operators' thresholds; they do not measure one quantity, and the table is the authors' reading of them. The table was rebuilt on this ledger on 6 October 2026 (the low end lifted to the weekly count and the single-vessel loads times the fleet's redeployment; unchanged from 55\,cm up); the band of $\pm$15\,\% on the shortfall and the sensitivity on the floor below 5\,cm (Section~S4) bound the result on either side.}-]{+treated.}+}

### E28 [S3] old 309-309 -> new 325-325 (replace)
line 325: cm & [-fleet-]{+traffic rate+} & vessel & nature & source & measures & [-transformation-]{+treatment+} \\

### E29 [S3] old 369-369 -> new 385-385 (replace)
line 385: \paragraph{Capacities.} The normal capacity of every Rhine reach is se [...] r each class the larger of its share of the CCNR cross-section tonnage[- (\texttt{rhine\_capacities.csv}, about 60\,\% of whose rows are estimates between the counted cross-sections; the file's total is split in the proportions of the model's baseline)-]{++} and the model's own baseline flow of the class on the reach plus 2\,\ [...] sels, 62,900 for the dry-bulk vessels and 80,600 for the tank barges. [-Each week the Kaub reach's capacity for each class is its normal capacity times the loading share. The normal capacity is a reduced-form ceiling, the realized baseline flow-]{+Headrooms+} of[- the class at full loading, not a count of the fleet's carrying capacity; the loading curve already contains the fleet's redeployment at moderate low water. Table~\ref{tab:gate} reports, week by week, what the gates cut, re-sent and withheld in the reference run; the headroom at normal water is tested at-]{++} 10 and 25\,\% [-(Section~S4).-]{+are tested inSection~S4.+}

### E30 [S3] old 371-371 -> new 387-387 (replace)
line 387: [-\paragraph{Allocation-]{+\paragraph{Rerouting+} [-at-]{+around+} a saturated reach.} After every agent has delivered, each [-capacitated -]{++}reach compares its load with its [-capacity;-]{+capacity.+} [-where-]{+If+} the load exceeds [-it, the-]{+capacity,+} shipments[- placed in the current round-]{++} are cut in proportion so [-that -]{++}the reach is exactly [-full;-]{+full.+} [-a-]{+Saturated+} [-saturated-]{+reaches+} [-reach-]{+are+} [-is-]{+then+} excluded [-from every search of-]{+for+} the rest of the [-step,-]{+week,+} and each cut share looks for a route on the [-network-]{+remaining+} [-minus-]{+network. This procedure, which does not depend on+} the [-saturated reaches with the penalty-aware search-]{+ordering+} of the [-main-]{+deliveries,+} [-text;-]{+is+} [-rounds repeat-]{+repeated+} until [-no-]{+all+} [-reach-]{+flows+} [-cuts.-]{+are+} [-The-]{+reassigned,+} [-allocation-]{+if+} [-depends-]{+possible.+} [-on what is offered in a round, not on-]{+In+} the [-order-]{+reference+} [-in-]{+run,+} [-which-]{+\GateResentMin+} [-agents-]{+to+} [-delivered.-]{+\GateResentMax\,\%+} [-Of-]{+of+} the tonnage cut at Kaub [-in the profile weeks of the reference run, \GateResentMin--\GateResentMax\,\% -]{++}finds another route [-(Table~\ref{tab:gate}):-]{+(Table~\ref{tab:gate}).+} [-\GateResentFirstMin--\GateResentFirstMax\,\% in the first three weeks and \GateResentLastMin--\GateResentLastMax\,\% in the last three, \GateResentEpMin--\GateResentEpMax\,\% in the episode weeks, because the surcharge has already moved off the river, before the gate, the shipments that have an alternative on their own modes, and what the gate cuts at the bottom of the season is the bulk that has none; in the recovery weeks, when the cut is small, three quarters of it is re-sent. The containers are rationed by their own class's capacity and, when cut,-]{+Containers+} always find rail or road [-(Table~\ref{tab:channels}),-]{+alternatives;+} [-so-]{+only bulk is withheld (Table~\ref{tab:channels}). During+} the [-tonnage-]{+low-water+} [-withheld-]{+weeks,+} [-is-]{+only+} [-bulk.-]{+Kaub saturates; in the recovery weeks, catch-up traffic saturates several other reaches, delaying part of the backlog and inventory refill.+}

### E31 [S3] old 373-375 -> new 389-389 (replace)
- \paragraph{Which reaches saturate.} During the low-water weeks, only Kaub saturates; in the recovery weeks, catch-up traffic saturates several reaches at their normal-tonnage capacity, delaying part of the refill and costing almost no output. By construction, road never carries the main leg of a bulk shipment: a truck carries 25 tonnes against 2,000 and more for a barge or an ore train, so road is not a substitute for bulk at the river scale during an event.
- 
- \paragraph{Surcharge.} The week's multiplier $1/\text{loading share}$, capped at 20, is applied on every reach from Koblenz upstream and at one third of its excess on the Lower Rhine reaches; the Lower Rhine factor is an assumption from the observed rate schedules \citep{contargo2026}, and the runs of 15 September showed the loss insensitive to it (factor 0 and factor 1 gave the same loss as the base).
+ \paragraph{Surcharge.} The week's multiplier $1/\text{loading share}$, capped at 20, is applied on every reach from Koblenz upstream and at one third of its excess on the Lower Rhine reaches. This Lower Rhine factor is an assumption from the observed rates, which are typically three times lower than the Upper Rhine rates   \citep{contargo2026}, and has negligible impact on the results.

### E32 [S4] old 382-381 -> new 396-397 (insert)
+ 
+ 

### E33 [S4] old 406-406 -> new 422-422 (replace)
line 422: [-\paragraph{The-]{+\paragraph{Capacity+} [-two-]{+and+} [-channels at the routing level.}-]{+surchage.}+} Over the 2026 run, the bulk shipments that leave their normal route f [...] e, reroutes \ChanBulkAltSurBn{} billion of bulk and withholds nothing.

### E34 [S4] old 411-411 -> new 427-427 (replace)
line 427: [-\caption{\textbf{The-]{+\caption{\textbf{Capacity+} [-two-]{+and+} [-channels-]{+surchage.}+} [-at-]{+Rerouted+} [-the-]{+and+} [-routing-]{+blocked+} [-level.} Value-]{+flows+} (billion USD, summed over the 43 weeks of the 2026 [-run) that leaves its normal route for an alternative, and value that the capacity gate withholds,-]{+run),+} by cargo class, in the reference [-run and with each channel alone. In the per-class representation of 2 November 2026 the containers sail the Rhine and are rationed by their own class's capacity (Methods); the surcharge moves the shipments with an alternative on their own modes off the river before the cut.}-]{+run.}+}

### E35 [S4] old 417-417 -> new 433-433 (replace)
line 433:  & [-alternative-]{+rerouted+} & [-withheld-]{+blocked+} & [-alternative-]{+rerouted+} & [-withheld-]{+blocked+} \\

### E36 [S4] old 419-420 -> new 435-436 (replace)
line 435: [-constraint-]{+capacity+} and surcharge (the paper) & 22.4 & 10.3 & 45.4 & 0.0 \\
line 436: [-constraint-]{+capacity+} alone & 4.0 & 11.7 & 13.4 & 0.0 \\

### E37 [S4] old 427-427 -> new 443-443 (replace)
line 443: \paragraph{The flat profile.} [-The-]{+We+} [-control-]{+built+} [-of-]{+a+} [-the-]{+counterfactual+} [-wave-]{+in+} [-experiment holds-]{+which+} the loading share [--]{+remains flat +}at the[--]{+ 2026+} season's mean (0.40) for the twenty-three [-weeks:-]{+weeks.+} [-equal-]{+About+} [-cumulated-]{+\GateHeldMt~Mt+} [-capacity-]{+of+} [-shortfall-]{+flows+} [-against-]{+are blocked in+} the [-fixed baseline, not, by construction, equal realized tonnage. The capacity limits withhold \GateHeldMt~Mt-]{+baseline+} over the [-\GateWeeks{} gated weeks of the season as it happened (the 23 profile weeks of Table~\ref{tab:gate}, \GateHeldProfMt~Mt, and the \GateRecWeeks{} recovery weeks, in which the refill traffic exceeds the reopened capacity, \GateHeldRecMt~Mt)-]{+season,+} and \FlatHeldMt~Mt under the flat [-profile-]{+profile.+} [-(cut \GateCutMt{} and \FlatCutMt~Mt, re-sent \GateResentMt{} and \FlatResentMt~Mt): the-]{+The+} realized tonnage withheld differs by [-\FlatHeldDiff\,\%.-]{+\FlatHeldDiff\,\%, confirming that the diverging results are not linked to aggregate throughput change.+}

### E38 [S4] old 436-436 -> new 452-452 (replace)
line 452: [-\caption{\textbf{The-]{+\caption{\textbf{Weekly+} [-gate-]{+flow+} [-week-]{+through+} [-by week,-]{+Kaub,+} 2026 reference run.} For each[- profile-]{++} week: the status of the gauge, its weekly mean (cm), the [-loading share of the-]{+corresponding+} loading [-curve,-]{+share,+} and the tonnage (kt) that the gates of the Rhine chain cut, re-sent on another route and withheld (returned to the supplier's [-inventory), from the run's log. The cut tonnage is the offered load above capacity; the withheld tonnage is what found no acceptable route. The baseline flow at Kaub is 1,210 kt a week. The table covers the 23 profile weeks (cut 11.2~Mt, re-sent 1.1, withheld 10.1); the gate also cuts in the 13 recovery weeks in which the refill traffic exceeds the reopened capacity (2.6, 2.0 and 0.7~Mt), for a season total of 13.8, 3.1 and 10.8~Mt, the totals of the text. The totals of a week sum over its rounds, so a share re-sent in one round and cut again at another reach in the next counts in both.}-]{+inventory)}+}

### E39 [S4] old 439-439 -> new 455-455 (replace)
line 455: week & start & status & Kaub [--]{+gauge (cm) +}& loading share & cut[--]{+  & rerouted+} & [-re-sent & withheld-]{+blocked+} \\

### E40 [S4] old 474-474 -> new 490-490 (replace)
line 490: \paragraph{Conservation and stationarity.}[- -]{+  +}A cut [-share-]{+flow+} is either [-re-sent on another route-]{+rerouted+} or[--]{+ blocked, that is, formally+} returned to the supplier's inventory, so the tonnage leaving [-the gate-]{+Kaub+} equals the tonnage entering [-it (cut = re-sent + withheld in Table~\ref{tab:gate}, whose rows cover the 23 profile weeks; the season's totals of the text add the \GateRecWeeks{} recovery weeks in which the gate still cuts, and the totals of a week sum over its rounds, a share re-sent in one round and cut again at another reach in the next being counted in both); -]{+it.  +}inventories and orders are floored at zero in the production and order [...] tationarity6w} of 5 October 2026, on the inputs of the first version).

### E41 [S4] old 523-523 -> new 539-539 (replace)
line 539:  & [-\multicolumn{2}{c}{no-]{+\multicolumn{2}{c}{\textit{no+} [-substitution}-]{+substitution}}+} & [-\multicolumn{2}{c}{rail-]{+\multicolumn{2}{c}{\textit{rail+} 50 kt a [-week}-]{+week}}+} \\

### E42 [S4] old 532-532 -> new 548-548 (replace)
line 548:  & [-\multicolumn{2}{c}{refill-]{+\multicolumn{2}{c}{\textit{refill+} time 30 [-days}-]{+days}}+} & [-\multicolumn{2}{c}{refill-]{+\multicolumn{2}{c}{\textit{refill+} time 15 [-days}-]{+days}}+} \\

### E43 [S5] old 575-575 -> new 591-591 (replace)
line 591: \KaubLinks{} commercial links cross Kaub on their normal route, \KaubW [...] iveredWet\,\% (liquid bulk) of their baseline tonnage, rerouted cargo [-included,-]{+included.+} [-and the-]{+The+} delivered price[- of what they deliver-]{++} rises by \PriceMedianDry{} and \PriceMedianWet\,\% at the median, \Pr [...] hWet\,\% at the ninth decile, with a maximum of \PriceMax{} times the [-baseline;-]{+baseline.+} [-across-]{+Across+} everything delivered on the network in the week of the widest price rise, [-\PriceShareDry\,\%-]{+\PriceShareEconomy\,\%+} of the [-dry-bulk value, \PriceShareLiquid\,\% of the liquid-bulk-]{+flow+} value [-and \PriceShareContainer\,\% of the container value pays more than-]{+increases+} 1\,\% above its baseline price, \PriceShareEconomy\,\% of the whole: freight is a few percent of the value of most cargo even when its rate is multiplied by [-\SurchargeMax, the model's surcharge at the lowest loading. The channel decomposition of the main text (surcharge alone: no loss; constraint alone: \GateOnlyQ\,\% of a quarter) is the direct evidence that the price channel has no output effect at these magnitudes in the model. Over the event, German buyers miss \DEUmissBn~billion USD of deliveries; \DEUwithheldBn~billion of it (\TransportWithheldShare\,\%) is withheld at the river, the rest is rationing along the chains. What the service sectors miss is fuel and each other's services: refined fuel is the largest missing input of the shipping companies (\FuelShareShipping\,\% of what they miss) and the second of the haulers (\FuelShareHauliers\,\%, after logistics services at \LogisticsShareHauliers\,\%), while logistics operators and power plants miss mostly the deliveries of their own sectors; over the four sectors, fuel is \FuelShareServices\,\% of what they miss. Of that fuel, \FuelWithheldShare\,\% is withheld at the river and the rest rationed by refineries short of their own inputs. For French buyers the largest missing deliveries are farm products to the food industry, withheld at the river (\FRAFarmWithheldBn~billion), and German inputs (\FRAfromDEUBn~billion), especially chemicals and power; most of these go to households and to chemical and power plants whose output barely moves, but the fuel that the French haulers run short of comes in part from German refineries. Tables of the disrupted chains by buyer country and input are generated by \texttt{extract\_link\_flows.py} and deposited with the run tables (Data availability).-]{+\SurchargeMax.+}

### E44 [S5] old 577-577 -> new 593-597 (replace)
- \subsection*{S6 Two representations of the river}
+ The channel decomposition of the main text (surcharge alone: no loss; constraint alone: \GateOnlyQ\,\% of a quarter) is the direct evidence that the price channel has no output effect at these magnitudes in the model. Over the event, German buyers miss \DEUmissBn~billion USD of deliveries; \DEUwithheldBn~billion of it (\TransportWithheldShare\,\%) is withheld at the river, and the rest is rationed along the chains. What the service sectors miss is fuel and each other's services: refined fuel is the largest missing input of the shipping companies (\FuelShareShipping\,\% of what they miss) and the second of the haulers (\FuelShareHauliers\,\%, after logistics services at \LogisticsShareHauliers\,\%), while logistics operators and power plants miss mostly the deliveries of their own sectors.
+ 
+ For French buyers, the largest missing deliveries are farm products to the food industry, withheld at the river (\FRAFarmWithheldBn~billion), and German inputs (\FRAfromDEUBn~billion), especially chemicals and power; most of these go to households and to chemical and power plants whose output barely moves, but the fuel that the French haulers run short of comes in part from German refineries. Tables of the disrupted chains by buyer country and input are generated by \texttt{extract\_link\_flows.py} and deposited with the run tables (Data availability). 
+ 
+ \subsection*{S6 Two representations of the river} 

### E45 [S8] old 771-771 -> new 791-799 (replace)
- Rail is a bounded substitute in this study, not a lever. Under the paper's rule the tonnage that leaves the river finds rail and road without a limit if it is containerized, and bulk cannot switch, the representation of the fact that tank barges and ore trains have no road or rail equivalent at volume in the time of an event, except for the shipments whose normal route already carries a main leg by rail (100\,km or more), which may go around a st [...]  tonnage that rail can take on in a low-water month, not the price of rail, is the question for the railway. Under the earlier priced river a run with rail tariffs for tank-car and ore trains at the level of bulk wagons changed nothing, by construction, since the prohibitive switching penalty stood.
+ Rail is a bounded substitute in this study, not a lever. In the model, container freights can reroute via rail and road without a limit, but bulk cannot switch. This assumption reflects that tank barges and ore trains have no road or rail equivalent at volume during an event. We add an exception to this strict rule: shipments whose normal route already carries a significant leg by rail (100\,km or more) may be fully rerouted by rail at no penalty. About 15\,\% of the bulk orders that cross Kaub have such a route.
+ 
+ We have no data on the share of the Kaub traffic that travels on a combined rail--barge route, so we run sensitivity analysis on this 100-km-threshold---i.e., how much bulk flows are eligigle to rerouting---and on a ceiling on the quantity of bulk rerouted.
+ \begin{itemize}
+     \item Raising the 100-km-threshold to 500\,km leaves no bulk shipment a rail alternative: the 2026 loss rises from \DEUlossQ{} to \RevNoRail\,\% of a quarter (\RevNoRailAbs\,\% more) and the 2018 loss from \DEUlossQyy{} to \RevNoRailyy\,\% (\RevNoRailyyAbs\,\% more), with the same peak weeks (Table~\ref{tab:revision}).
+     \item We test a ceiling on the tonnage of bulk can be rerouted per rail per week. A 50 kt ceiling approximates the 400 wagons the national rail freight operator said it could add at short notice in August 2026, at two rotations a week and 62.5 t per wagon \citep{dbcargo2026}. It reduces the 2026 losses by \RevRailFiftyAbs{} and the 2018 losses by \RevRailFiftyyyAbs{}, where it reduces the industrial shortfall to \RevRailFiftyInt{} percent-months against the benchmark's \RecordInt{} (band \RecordIntLow--\RecordIntHigh).
+     \item A higher ceiling of 140 kt is analyzed, loosely based on Appendix B of Ademmer (2023)'s working paper, which estimated +0.07\,\% of rail tonnage per low-water day over a 30-day low-water, applied to 6.7 Mt of rail freight a week. This estimate covers all cargo types, including containers, which we already allow to switch and are not counted on this ceiling, so the value of 140 kt applied to bulk is likely an overestimate of what rail can take on. It reduces the 2026 losses by \RevRailHundredFortyAbs{} and the 2018 losses by \RevRailHundredFortyyyAbs{}, where it reduces the industrial shortfall to \RevRailHundredFortyInt{} percent-months against the benchmark's \RecordInt{} (band \RecordIntLow--\RecordIntHigh).
+ \end{itemize}
+ The closer fit of the no-substitution rule does not establish that the emergency capacity of 2018 was zero.

### E46 [S9] old 827-827 -> new 855-855 (replace)
line 855: [-Three-]{+This section documents three modeling+} choices [-of the model-]{+that+} were [-made-]{+informed+} [-on-]{+by+} the 2018 [-benchmark-]{+event.+} [-among-]{+We+} [-a-]{+first+} [-few-]{+consolidated+} [-candidates-]{+an+} [-each,-]{+industrial+} [-and-]{+production time series from the study of~\citep{ademmer2023}, which publishes an empirically calibrated regression model of+} this [-section-]{+event;+} [-documents-]{+see+} [-them;-]{+Table~2,+} [-no-]{+column~1.+} [-parameter was fitted. The benchmark is the production path implied by the published-]{+This+} regression [-of ref.~\citep{ademmer2023} (its Table~2, column~1):-]{+models+} the growth of the German production index [-regressed-]{+based+} on the change in the number of days of the month with Kaub below 78\,cm, with coefficients $-0.034$ [-(s.e.-]{+(standard error+} 0.012), $-0.024$ (0.014) on its lag and $-0.172$ (0.119) on the lagged growth.[- Applied to the low-water days of the daily gauge record (29, 14, 31, 30 and 3 from August to December 2018, none before or after), the induced growth, cumulated, gives the monthly shortfall of Results; the band is a Monte Carlo over independent normal draws of the three coefficients at their standard errors (the covariance is not published, so the band is indicative: it approximates the uncertainty of the coefficients, not that of the counterfactual, and the count of networks inside it describes the set of networks rather than tests it). The model's counterpart is the shortfall of German industrial production aggregated as the production index is: each sector's shortfall rate weighted by the sector's German value added in the input--output table, over sections B to D (the index's coverage; its division E36 is not separable here), each day of a month taking the value of the model week it belongs to, the month being the mean of its days and the integral over August to December the plain sum of the months. The working paper identifies its series only as the industrial production of the Federal Statistical Office, which we take as this index; its weighting vintage is not reproduced (the weights are those of the 2022 table). The measure matters: the production-weighted B--E series of an earlier version of this paper gave \IndProdIntyy{} percent-months in 2018 against \IndVAIntyy{} on the index measure, and \IndProdInt{} against \IndVAInt{} in 2026.-]{++}

### E47 [S9] old 829-829 -> new 857-857 (replace)
line 857: [-\paragraph{The-]{+Applied+} [-representation-]{+to the low-water days+} of the [-river.}-]{+daily+} [-Two-]{+gauge+} [-features-]{+record (29\~cm, 14\~cm, 31\~cm, 30\~cm and 3\~cm from August to December 2018), this equation produces an induced loss of cumulated growth, which is used as the losses shown in the Results. The band shown on FiguresXXX is a Monte Carlo over independent normal draws+} of the [-benchmark-]{+three+} [-decide-]{+coefficients+} [-it.-]{+at+} [-The-]{+their+} [-onset:-]{+standard+} [-industrial-]{+errors+} [-production-]{+(the+} [-was-]{+covariance+} [-already-]{+is+} [-falling-]{+not+} [-in-]{+published,+} [-August 2018, two months before-]{+so+} the [-first week in which any vessel class stopped sailing. And the shape of the path: a deepest month in November from which the shortfall has fallen back by two thirds in December. A representation in which low water only makes the river dearer, with a closure of each vessel class below its own water level, misses the onset at every inventory level, because a dearer week moves the full tonnage at a higher price until the closure stops it: its losses start in the week of 22 October, when the gauge falls below the last sailing floor, peak in November like the benchmark (\PricedNov\,\% against the benchmark's \RecNov{} at the balance-sheet inventories, an overshoot that turns into an undershoot at twice the inventories; rerun on the flows, loading curve and inventories of the capacity limit, Section~S6) and keep in December half of their November value at the balance-sheet inventories and nearly all of it at higher ones, where the benchmark keeps a third. Its sum over the five months at the balance-sheet inventories, \PricedInt{} percent-months,-]{+band+} is [-nearer the benchmark's \RecordInt{} than the capacity limit's \ModelInt, but it is made of the wrong months: nothing in August and September, a December twice the benchmark's. The capacity limit starts in August, more weakly than the benchmark, and has its shape: \KaubPassAugyy\,\% of the normal tonnage passes Kaub in August 2018 and \KaubPassNovyy\,\% in November, and the buyers of bulk run down their inventories from the first month. Under the capacity limit with the surcharge the onset, the deepest month, the fall-back in December and, within the benchmark's 95\,\% band, the size at the balance-sheet inventories are reproduced (Table~\ref{tab:representations}).-]{+indicative).+}

### E48 [S9] old 831-831 -> new 859-866 (replace)
- \paragraph{The level of the inventories.} With the inventory targets multiplied by 1.25, 1.5 and 2 the industrial shortfall is \LadderIntA, \LadderIntB{} and \LadderIntD{} percent-months and the total loss \LadderA, \LadderB{} and \LadderD\,\% of a quarter; at three quarters of the balance-sheet value (run of 6 November 2026) they are \LadderIntZ{} percent-months and \LadderZ\,\% of a quarter, nearer the benchmark's \RecordInt{} than any other rung but still below its one-standard-deviation band. The balance-sheet value is kept: it is the level the accounts document, and the ladder is a sensitivity, not a calibration; on the index measure it gives \ModelInt{} percent-months, below the benchmark's one-standard-deviation band and inside its 95\,\% band.
+ The model's counterpart is the loss of German industrial production, which we build from the same aggregation as done in~\citep{ademmer2023}: sum each sector's weekly loss from August to December, weighted by its value added in the German input--output table, over sections B to D (the index's coverage).
+ 
+ \paragraph{Choice #1: low water impacts on transport capacity.} There were two options: (i) \textit{binary thresholds}: lower water makes transport more expensive, and, when it goes below a threshold, a whole class of vessels cannot move at all, with multiple vessel classes; (ii) \textit{loading curve}: a loading curve for each cargo type, with surcharge inversely proportional to the loading factor. We observed that the industrial production index was already falling in August 2018, two months before the first week in which any vessel class stopped sailing. Option (i) captures the right onset, whereas, with option (ii), losses only start mid-October; see able~\ref{tab:representations}. 
+ 
+ 
+ %And the shape of the path: a deepest month in November from which the shortfall has fallen back by two thirds in December. A representation in which low water only makes the river dearer, with a closure of each vessel class below its own water level, misses the onset at every inventory level, because a dearer week moves the full tonnage at a higher price until the closure stops it: its losses start in the week of 22 October, when the gauge falls [...] the buyers of bulk run down their inventories from the first month. Under the capacity limit with the surcharge the onset, the deepest month, the fall-back in December and, within the benchmark's 95\,\% band, the size at the balance-sheet inventories are reproduced (Table~\ref{tab:representations}).
+ 
+ \paragraph{Inventory levels.} We assessed different inventory values: targets multiplied by 0.75, 1.25, 1.5 and 2.  the industrial shortfall is \LadderIntA, \LadderIntB{} and \LadderIntD{} percent-months and the total loss \LadderA, \LadderB{} and \LadderD\,\% of a quarter; at three quarters of the balance-sheet value (run of 6 November 2026) they are \LadderIntZ{} percent-months and \LadderZ\,\% of a quarter, nearer the benchmark's \RecordInt{} than any other rung but still below its one-standard-deviation band. The balance-sheet value is kept: it is the level the accounts document, and the ladder is a sensitivity, not a calibration; on the index measure it gives \ModelInt{} percent-months, below the benchmark's one-standard-deviation band and inside its 95\,\% band.

### E49 [S9] old 835-835 -> new 870-871 (replace)
- \subsection*{S10 Implementation conventions and the fleet lever}
+ 
+ \subsection*{S10 Weekly sequence and model specifications}

### E50 [S10] old 841-841 -> new 877-877 (replace)
line 877: Shipments are then [-routed (Disruption and response).-]{+routed.+} If river capacity is reached, shipments that are turned away, and tho [...] to outputs down the chain; only transport can trigger price movements.

### E51 [S10] old 843-843 -> new 879-881 (replace)
- \paragraph{Conventions.} There are no lead times beyond the weekly step, no order cancellation and no price response of demand. Conventions: the inventory days $d_{ik}$ are converted to weeks and floored at one week, the smallest inventory the weekly step can represent, so that the trade and hospitality buyers hold seven days rather than five; $\tau$ is 30 days, 4.3 steps; receipts arrive at the end of the week, after production, so that producti [...] tle: in the 2026 run the catch-up production of goods and construction decays from \CatchUpFirstM~million USD a week in week 24 to \CatchUpLastM~million in week 43, by \CatchUpDecay\,\% a week, so the catch-up that a longer run would add is about \CatchUpTailShare\,\% of the backlog left at the end.
+ \paragraph{A few specifications} There are no lead times beyond the weekly step, no order cancellation and no price response of demand. The inventory days $d_{ik}$ are converted to weeks and floored at one week, the smallest inventory the weekly step can represent. An unfilled order is not carried over as such, next week's order is recomputed from the target and the gap it left, so an unfilled order raises the next. The suppliers' weights start at the baseline shares and the inventories at their targets.
+ 
+ \paragraph{Stationarity, conservation, and time horizon} Undisrupted runs are stationary. Rejected shipments are conserved, a cut share returns to the supplier's inventory or is delivered on another route, and rerouting does not depend on the order in which agents deliver. The run horizon, 43 weeks for 2026 and 42 for 2018, is long enough for the loss measurement to settle: in the 2026 run the catch-up production of goods and construction decays from \CatchUpFirstM~million USD a week in week 24 to \CatchUpLastM~million in week 43, by \CatchUpDecay\,\% a week, so the catch-up that a longer run would add is about \CatchUpTailShare\,\% of the backlog left at the end.

Text edit hunks: 51