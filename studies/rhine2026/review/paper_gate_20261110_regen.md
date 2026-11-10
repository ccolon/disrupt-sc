# Paper gate: 6aaa98617957ab816097822f at 2591144 2026-11-10

| check | status | findings |
|---|---|---|
| static | PASS | 0 |
| pdflatex | PASS | 0 |
| macros | WARN | 1 |
| ledger | PASS | 0 |
| pending | PASS | 0 |
| bare | PASS | 0 |
| words | WARN | 28 |
| refs | WARN | 15 |
| fresh | PASS | 0 |
| compile | NOT RUN | 0 |

## pdflatex: PASS

          U+00F6 ö LATIN SMALL LETTER O WITH DIAERESIS: 1x (pdfLaTeX T1: fine)
          U+2014 — EM DASH: 1x (pdfLaTeX T1: fine)

## macros: WARN

    warn  196 of 516 macros of numbers.tex are never used: BasinDortmundEmsMt, BasinKuestenMt, BasinMittellandMt, BasinWeselDattelnMt, BasinWeserMt, CargoDryIww, CargoDryRail, CargoDryRoad, CargoGeneralIww, CargoGeneralRail, CargoGeneralRoad, CargoLiquidIww, CargoLiquidRail, CargoLiquidRoad, ConsLossBn, ContainerValueShare, CorridorFirmsBelow, CorridorFirmsBelowDEU, CorridorFirmsBelowDEUAug, CrossDeepAloneBn, CrossDeepOnRailBn, CrossFleetAloneBn, CrossFleetOnRailBn, CrossStockTAloneBn, CrossStockTOnRailBn, DEUlossBnyy, DEUlossQP, DEUlossQyyP, DEUpeakWeekyy, DailyLoadingDiff, DeepSeaShare, DelayCost, DestatisNovyy, EUlossBn, EnsMaxyy, EnsMedian, EnsMedianyy, EnsMinyy, FRAFoodShare, FRARoadShare, FlatCutMt, FlatResentMt, FleetBeatsTargetedDraws, FlowScore, FlowScoreFirst, FuelShareServices, FuelWithheldShare, GateBulkKt, GateFleetKt, GateHeldProfMt, GateHeldRecMt, GateResentEpMax, GateResentEpMin, GateResentFirstMax, GateResentFirstMin, GateResentLastMax, GateResentLastMin, GateResentRec, GateSingleKt, GateWeeks, IndProdInt, IndProdIntyy, IndVAInt, IndVAIntyy, IndVAMaxDiff, IndVAMaxDiffyy, LadderA, LadderB, LadderIntA, LadderIntB, LadderIntD, LadderIntZ, LadderZ, LevFleetP, LevPackage, ModalATIww, ModalATRail, ModalATRoad, ModalBEIww, ModalBERail, ModalBERoad, ModalCHIww, ModalCHRail, ModalCHRoad, ModalDEIww, ModalDERail, ModalDERoad, ModalFRIww, ModalFRRail, ModalFRRoad, ModalITIww, ModalITRail, ModalITRoad, ModalNLIww, ModalNLRail, ModalNLRoad, ModalPLIww, ModalPLRail, ModalPLRoad, NetShare, NonDEshare, PeakBase, PeakFleet, PerishableShareyy, PriceIntP, PriceIntRawP, PriceShareContainer, PriceShareDry, PriceShareLiquid, PricedDec, PricedDecShare, PricedInt, PricedIntB, PricedIntC, PricedNov, PricedNovC, PricedOnsetLagMonths, RatioRailFifty, RatioRailHundredForty, RecordIntHighW, RecordIntLowW, RecordIntNoLag, RecordQHigh, RecordQLow, RevDeepLocal, RevDeepLocalAbs, RevDeepLocalRel, RevDfuel, RevDfuelAbs, RevFleetWide, RevFleetWideAbs, RevFleetWideRel, RevFloorHigh, RevFloorHighAbs, RevFloorLow, RevFloorLowAbs, RevHeadTen, RevHeadTenAbs, RevHeadTwentyFive, RevHeadTwentyFiveAbs, RevNoRailRel, RevNoRailyyRel, RevQHighAbs, RevQHighRel, RevQLowAbs, RevQLowRel, RevRailFifty, RevRailFiftyyy, RevRailHundredForty, RevRailHundredFortyyy, RevRestFifteen, RevRestSixty, RevRestSixtyAbs, RevServ, RevServAbs, ShareConstructionDfuel, ShareConstructionRailFifty, ShareConstructionServ, ShareIndustryDfuel, ShareIndustryRailFifty, ShareIndustryRailHundredForty, ShareIndustryServ, ShareServicesRailFifty, ShareServicesRailHundredForty, ShareServicesyy, ShareUtilitiesRailFifty, ShareUtilitiesRailHundredForty, ShareUtilitiesServ, StatBelow, StatBelowPct, StatDrift, StatFirms, StatStockHigh, StatStockLow, StatTotalDevPpm, SupTwoQ, SupTwoQyy, SupWeightAfter, SupWeightBuyers, SupWeightSecond, SupWeightStart, SupWeightWaveEnd, SurchargeBillDEUBn, TableHighQyy, TableLowQyy, TargetedBehindBothDraws, TroughPremium, UpperRhineShareMax, UpperRhineShareMin, WaveBratio, WaveGapFourRest, WaveGapTwoRest, WaveInterEight, WaveInterTwo, WaveSumRest, WorstWeek
          516 macros defined, 320 used

## ledger: PASS

          claim ok: 'would each remove two fifths of it': LevStockAvg = 42 in [36, 44]
          claim ok: 'would each remove two fifths of it': LevDeepAvg = 43 in [36, 44]
          claim ok: 'each remove two fifths of the loss': LevStockAvg = 42 in [36, 44]
          claim ok: 'each remove two fifths of the loss': LevDeepAvg = 43 in [36, 44]
          claim ok: 'when the river still passes two to four fifths of its normal tonnage': KaubPassJul = 51 in [40, 80]
          claim ok: 'inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP)': AugWaveEurBn = 1.1 in [1, 2]
          claim ok: 'inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP)': AugWaveIndQ = 0.13 in [0.1, 0.2]
          claim ok: 'one extra week removes two fifths of the 2026 loss': LevStockAvg = 42 in [36, 44]
          claim ok: 'billion avoided, more than half the effect': 100*StockTAvoidedBn/StockAvoidedBn = 57.69 in [50, 75]
          claim ok: 'one more week of them removes two fifths of the 2026 loss': LevStockAvg = 42 in [36, 44]
          claim ok: "The model's cumulated loss lies within its 95\\,\\% band but below its center": (ModelIntEnsMean - RecordIntLowW)/(RecordInt - RecordIntLowW) = 0.0303 in [0, 0.99]
          claim ok: "the model's industrial loss lies within the 95\\,\\% band of their estimate": (ModelIntEnsMean - RecordIntLowW)/(RecordInt - RecordIntLowW) = 0.0303 in [0, 1.0]
          claim ok: 'industry carries more than a third of it': IndustryShare = 38 in [33.4, 50]
          claim ok: 'shipping companies, over half': ShareRefining+ShareLandTransport+ShareLogistics+SharePower+ShareShipping = 58 in [50, 75]
          claim ok: 'the barge-dependent buyers alone a quarter': LevStockTAvg = 27 in [22, 28]
          claim ok: 'for 28 regions, the 27 member states of the European Union and Switzerland, and 50 sectors': NRegions = 28 in [28, 28]
          claim ok: 'for 28 regions, the 27 member states of the European Union and Switzerland, and 50 sectors': NSectors = 50 in [50, 50]
          claim ok: 'more than two and a half times the industrial loss alone': RatioBase = 2.6 in [2.5, 2.8]
          claim ok: 'while doubling inventories reduces the loss by almost three quarters': 100*(1-LadderD/DEUlossQyy) = 73.08 in [66, 75]
          claim ok: 'spread evenly would cost two fifths less': 100*(1-FlatQ/DEUlossQ) = 41.44 in [36, 44]
          claim ok: 'cost a sixth more in sequence than apart': WaveInterShare = 16 in [15, 18.5]
          claim ok: 'and a fleet built for low water a fifth': LevFleetAvg = 21 in [17, 23]
          claim ok: 'what the railway can take on at short notice removes a quarter to more than a half': RevRailFiftyAbs = 25 in [22, 28]
          claim ok: 'what the railway can take on at short notice removes a quarter to more than a half': RevRailHundredFortyAbs = 57 in [50.5, 75]
          claim ok: "both below the benchmark's central value": RecordInt - TableLowInt = 1.9 in [0.01, 100]
          claim ok: 'a loss that builds from July and more than doubles in the autumn': AutumnWaveQ/AugWaveQ = 2.367 in [2.0, 2.8]
          claim ok: 'costs \\finalbatch{\\AutumnWaveQ}\\,\\%, more than twice as much': AutumnWaveQ/AugWaveQ = 2.367 in [2.0, 2.8]
          claim ok: 'about two fifths less than the season as it happened': 100*(1-FlatQ/DEUlossQ) = 41.44 in [35, 45]
          claim ok: 'are less than a third of the deliveries that German buyers miss': TransportWithheldShare = 29 in [25, 33.3]
          claim ok: 'doubling them for every buyer divides the 2018 loss by more than three': DEUlossQyy/LadderD = 3.714 in [3.05, 4.5]
          claim ok: 'doubling them divides the 2018 loss by more than three': DEUlossQyy/LadderD = 3.714 in [3.05, 4.5]
          claim ok: 'goods producers and construction work off nearly a quarter of their backlog': 100*(100-NetShare)/(100-PerishableShare) = 23.68 in [20.5, 25]
          claim ok: 'it predicts an economy-wide loss two and a half times larger': 100/IndustryShareyy = 2.439 in [2.3, 2.7]
          claim ok: 'and the second costs a quarter more than it would have alone': 100*(WaveBafterAQ/WaveBQ-1) = 25 in [22, 28]
          claim ok: 'and the building-materials chain a sixth': ShareConstruction+ShareCement = 16 in [15, 18.5]
          claim ok: 'make up nearly a quarter of their backlog once the river reopens': 100*(100-NetShare)/(100-PerishableShare) = 23.68 in [20.5, 25]
          claim ok: 'divides the loss by three compared with a model that keys every input to its region': NoPoolQ/DEUlossQ = 3.063 in [2.7, 3.3]
          claim ok: 'a fleet built for low water a fifth': LevFleetAvg = 21 in [17, 23]
          claim ok: '(a quarter with its gain extended to 100\\,cm)': RevFleetWideRemoves = 26 in [22, 28]
          claim ok: 'the three together more than four fifths': LevPackageAvg = 84 in [80.5, 90]
          claim ok: 'a quarter of the loss at the tonnage the operator offered in August 2026 and more than a half at the': RevRailFiftyAbs = 25 in [22, 28]
          claim ok: 'starts its losses two and a half months late': PricedOnsetLagMonths = 2.7 in [2.25, 2.75]
          claim ok: '\\,\\% with four, and \\finalbatch{\\WaveInterEightAbs}\\,\\% less with eight': WaveInterEight = -0.9 in [-100, -0.05]
          claim ok: 'two thirds in its food chain': FRAFoodShare = 66 in [62, 71]
          claim ok: 'a sixth in road transport': FRARoadShare = 17 in [15, 18.5]
          claim ok: 'which sits below the median of both events': EnsMedian - DEUlossQ = 0.03 in [0.005, 10]
          claim ok: 'which sits below the median of both events': EnsMedianyy - DEUlossQyy = 0.09 in [0.005, 10]
          claim ok: 'the other 39 sectors are placed on NUTS3 employment': NSectors - 11 = 39 in [39, 39]
          claim ok: 'nine per region--sector on average': NFirms/(NRegions*NSectors) = 9.085 in [8.5, 9.5]
          claim ok: 'sea lanes (948) and multimodal connectors at terminals and ports (1,490)': NEdges - 2979 - 4261 - 461 - 948 = 1490 in [1490, 1490]
          claim ok: 'with the waterway share of liquids nearly a third too high': 100*(CargoLiquidIww/30-1) = 30 in [27, 33]
          claim ok: 'within 10\\,\\% at Hamburg': max(abs(PortHamburgMt/99.6-1), abs(PortHavreMt/75.56-1), abs(PortMarseilleMt/67.26-1), abs(PortGenoaMt/46.6-1), abs(PortGothenburgMt/34.98-1), abs(PortBilbaoMt/31.53-1))*100 = 7.047 in [0, 10]
          claim ok: 'within a quarter at Dublin': max(abs(PortDublinMt/24.67-1), abs(PortNantesMt/28.48-1), abs(PortDunkirkMt/35.39-1), abs(PortBremerhavenMt/39.19-1))*100 = 23.45 in [10, 25]
          claim ok: 'a third below at Antwerp-Bruges': max(abs(100*(1-PortAntwerpMt/242.24)-100/3), abs(100*(1-PortAmsterdamMt/80.76)-100/3)) = 0.2092 in [0, 3.7]
          claim ok: 'about two fifths below at Barcelona': max(abs(100*(1-PortBarcelonaMt/51.46)-40), abs(100*(1-PortGhentMt/29.95)-40), abs(100*(1-PortValenciaMt/62.25)-40)) = 4.127 in [0, 5]
          claim ok: 'and its waterways half': 100*NLWaterTkmBn/41.6 = 51.68 in [45, 55]
          claim ok: 'the Mannheim--Mainz reach is above them': RhineMannheimMainzMt/40 = 1.15 in [1.0, 2.0]
          claim ok: 'the refill time of inventories and the service rules by up to a third': max(RevRestFifteenAbs, RevRestSixtyAbs, RevServAbs) = 30 in [30, 37]
          claim ok: 'sea lanes (948) and multimodal connectors at terminals and ports (1,490)': NEdges - 2979 - 4261 - 461 - 948 = 1490 in [1490, 1490]
          claim ok: 'the loading curve by about a half up or down': 100*(TableLowQ/DEUlossQ-1) = 52.25 in [40, 60]
          claim ok: 'the loading curve by about a half up or down': 100*(1-TableHighQ/DEUlossQ) = 45.05 in [40, 60]
          claim ok: 'two suppliers per input down by nearly a half': 100*(1-SupTwoQ/DEUlossQ) = 45.05 in [44, 50]
          claim ok: 'no pooling up threefold': NoPoolQ/DEUlossQ = 3.063 in [2.7, 3.3]
          claim ok: 'no rail bypass for bulk up by three fifths': RevNoRailAbs = 61 in [56, 64]
          claim ok: 'inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP)': AugWaveEurBn = 1.1 in [1, 2]
          claim ok: 'inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP)': AugWaveIndQ = 0.13 in [0.1, 0.2]
          claim ok: 'The 39 other sectors are downscaled using NUTS3 employment': NSectors - 11 = 39 in [39, 39]
          claim ok: 'survey of Pichler et al.~\\citep{pichler2022} mapped to the 50 sectors': NSectors = 50 in [50, 50]
          claim ok: '\\textbf{The criticality survey mapped to the 50 sectors.}': NSectors = 50 in [50, 50]
          claim ok: 'how many of its 50 input sectors the survey rates': NSectors = 50 in [50, 50]
          claim ok: 'where the model is within a third of the counts, except at Rotterdam': max(abs(PortHamburgMt/99.6-1), abs(PortBremerhavenMt/39.19-1), abs(PortAmsterdamMt/80.76-1), abs(PortAntwerpMt/242.24-1))*100 = 33.14 in [25, 33.4]
          claim ok: 'is, in the model, a third of its observed tonne-kilometers': 100*NLTkmBn/110.8 = 35.2 in [30, 37]
          claim ok: 'the model carries half to two-thirds of the counts': RhineBaselMt/5.5 = 0.4727 in [0.45, 0.55]
          claim ok: 'Above Mannheim, the model carries half to two-thirds of the counts': max(RhineStrasbourgMt/16, RhineKarlsruheMt/22) = 0.625 in [0.58, 0.72]
          claim ok: 'the loss of the 28 economies and the consumption loss of each': NRegions = 28 in [28, 28]
          claim ok: "At three quarters of the balance-sheet values the industrial shortfall is nearer the benchmark's": min(abs(RecordInt-ModelInt), abs(RecordInt-LadderIntA), abs(RecordInt-LadderIntB), abs(RecordInt-LadderIntD)) - abs(RecordInt-LadderIntZ) = 1.1 in [0.01, 100]
          claim ok: 'but still below its one-standard-deviation band. The balance-sheet values are kept': RecordIntLow - LadderIntZ = 0.4 in [0.01, 100]
          claim ok: 'Road is below the statistics in Germany, the Netherlands, Belgium, France and Austria': max(ModalDERoad-73, ModalNLRoad-53, ModalBERoad-78, ModalFRRoad-89, ModalATRoad-69) = -8 in [-100, -1]
          claim ok: "Under the ceiling each lever removes a larger share of a smaller loss than under the paper's rule": min(CrossStockRail - LevStock, CrossDeepRail - LevDeep, CrossStockTRail - LevStockT, CrossFleetRail - LevFleet) = 1 in [1, 100]

## bare: PASS

          accepted: 191 years, 69 calendar dates, 507 numbers under ledger entries

## words: WARN

    warn  main.tex:257  'ten'  | eference network and, paired with its own base, on the [[ten]] further networks; the loss avoided is reported as the
    warn  main.tex:257  'two'  | mit alone (no surcharge). The sensitivity runs and the [[two]] crossed experiments (the single levers on top of the 5
    warn  main.tex:257  'two'  | the 2026 profile after its tenth week (30 August) into [[two]] waves, run alone, in sequence with 1, 2, 4 and 8 weeks
    warn  main.tex:263  'eleven'  | e~\ref{tab:prospective} shows?}, and the mean over the [[eleven]] networks alongside it, against the Destatis production
    warn  si.tex:402  'two'  | evers under a rail ceiling, and the interaction of the [[two]] waves at a shorter refill time. It ends with the secto
    warn  si.tex:427  'two'  | apacity and surcharge.} Low water acts on the river in [[two]] ways: the capacity limit caps the tonnage that passes
    warn  si.tex:427  'two'  | passes dearer. Table~\ref{tab:channels} separates the [[two]] with two runs in which one of them is switched off. Wi
    warn  si.tex:427  'two'  | earer. Table~\ref{tab:channels} separates the two with [[two]] runs in which one of them is switched off. With the su
    warn  si.tex:432  'two'  | cargo class, in the reference run and with each of the [[two]] mechanisms alone.}
    warn  si.tex:448  'two'  | ich confirms that the difference in losses between the [[two]] profiles does not come from a difference in the tonnag
    warn  si.tex:497  'four'  | under a rail ceiling.} Table~\ref{tab:cross} gives the [[four]] single levers on top of a rail ceiling of 50 kt a week
    warn  si.tex:524  'two'  | \caption{\textbf{The [[two]] waves of 2026 at two refill times.} German loss (\% of
    warn  si.tex:524  'two'  | \caption{\textbf{The two waves of 2026 at [[two]] refill times.} German loss (\% of a quarter) of the tw
    warn  si.tex:524  'two'  | wo refill times.} German loss (\% of a quarter) of the [[two]] waves alone, of their sum, and of their sequence with
    warn  si.tex:579  'Three'  | itivity} shows the same losses by type of uncertainty. [[Three]] sets of runs are of another kind. Ten further supplier
    warn  si.tex:579  'Ten'  | f uncertainty. Three sets of runs are of another kind. [[Ten]] further supplier--buyer networks, drawn with other see
    warn  si.tex:579  'two'  | n every network, against the base of that network. And [[two]] experiments cross two changes (Section~S5): the levers
    warn  si.tex:579  'two'  | st the base of that network. And two experiments cross [[two]] changes (Section~S5): the levers under a rail ceiling,
    warn  si.tex:579  'two'  | (Section~S5): the levers under a rail ceiling, and the [[two]] waves at a shorter refill time.
    warn  si.tex:663  'Four'  | rule are not tuned. \paragraph{What was not varied.} [[Four]] groups of parameters stay at their reference values in
    warn  si.tex:665  'two'  | s on \NRuns{} runs: \NRunsMain{} in the main list (the [[two]] reference runs, their variants, and the ten further ne
    warn  si.tex:665  'ten'  | list (the two reference runs, their variants, and the [[ten]] further networks of the 2018 event), \NRunsPaired{} le
    warn  si.tex:665  'ten'  | s of the 2018 event), \NRunsPaired{} lever runs on the [[ten]] further networks of 2026, \NRunsRev{} one-at-a-time se
    warn  si.tex:681  'two'  | me peak weeks (Table~\ref{tab:revision}). \item In [[two]] further runs, the bulk that is cut at Kaub may switch
    warn  si.tex:689  'four'  | ution by rail, week by week.} For each run week of the [[four]] rail runs (Supplementary Table~\ref{tab:revision}): th
    warn  si.tex:689  'two'  | without a cut. The offered tonnage differs between the [[two]] ceilings of an event because the runs differ. The 50 k
    warn  si.tex:759  'Two'  | \caption{\textbf{[[Two]] representations of the river on the 2018 event.} Month
    warn  si.tex:759  'five'  | on (\%), August to December 2018, and its sum over the [[five]] months (percent-months): the benchmark, its one-standa
          accepted under ledger entries: 241

## refs: WARN

    warn  refs.bib: bachmann2022 is never cited
    warn  refs.bib: baqaee2019 is never cited
    warn  refs.bib: barrot2016 is never cited
    warn  refs.bib: basf2019 is never cited
    warn  refs.bib: bedoyamaya2024 is never cited
    warn  refs.bib: bonadio2021 is never cited
    warn  refs.bib: gobert2023 is never cited
    warn  refs.bib: koks2019 is never cited
    warn  refs.bib: sun2024heat is never cited
    warn  refs.bib: turpijn2026 is never cited
    warn  refs.bib: verschuur2023systemic is never cited
    warn  refs.bib: vinke2022 is never cited
    warn  refs.bib: welch2022 is never cited
    warn  refs.bib: wenz2016 is never cited
    warn  28 cited entries have neither DOI nor URL (cannot be verified online): ademmer2020, baw2026, bfg2026, bloomberg2026commerzbank, bmv2019, bundesbank2025, ccnr2019, ccnr2023, climatetrace2024, contargo2026, dbcargo2026, dihk2026, dwd2026, ebv2025, eurostat2025regio, gem2025, icis2026, icpr2020, ifw2026, kriedel2019lowwater, oecd2025icio, pegelonline2026, prognos2026rhine, reuters2026, schuttevaer2026, spam2020, vgrdl2025, wiwo2026
          106 entries, 92 cited

## fresh: PASS

          regenerating with --tag r6_bycargo --lists 20261102
          516 macros and 17 tables regenerated

## compile: NOT RUN

          --no-compile

VERDICT: PASS (not run: compile)
