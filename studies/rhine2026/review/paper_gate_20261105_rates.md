# Paper gate: 6aaa98617957ab816097822f at 2107ce5 2026-11-05

| check | status | findings |
|---|---|---|
| static | PASS | 0 |
| pdflatex | PASS | 0 |
| macros | WARN | 1 |
| ledger | PASS | 0 |
| pending | FAIL | 2 |
| bare | PASS | 0 |
| words | PASS | 0 |
| refs | WARN | 18 |
| fresh | PASS | 0 |
| compile | WARN | 1 |

## pdflatex: PASS

          U+00E1 á LATIN SMALL LETTER A WITH ACUTE: 1x (pdfLaTeX T1: fine)
          U+00E8 è LATIN SMALL LETTER E WITH GRAVE: 1x (pdfLaTeX T1: fine)
          U+00F6 ö LATIN SMALL LETTER O WITH DIAERESIS: 1x (pdfLaTeX T1: fine)
          U+00FC ü LATIN SMALL LETTER U WITH DIAERESIS: 1x (pdfLaTeX T1: fine)
          U+2014 — EM DASH: 1x (pdfLaTeX T1: fine)

## macros: WARN

    warn  94 of 507 macros of numbers.tex are never used: ContainerValueShare, CorridorFirmsBelow, CorridorFirmsBelowDEU, CorridorFirmsBelowDEUAug, CrossDeepAloneBn, CrossDeepOnRailBn, CrossFleetAloneBn, CrossFleetOnRailBn, CrossStockTAloneBn, CrossStockTOnRailBn, DEUlossBnyy, DEUpeakWeekyy, DailyLoadingDiff, DelayCost, EnsMaxyy, EnsMedian, EnsMedianyy, EnsMinyy, FRAFoodShare, FRARoadShare, FleetBeatsTargetedDraws, GateResentRec, IndVAMaxDiff, IndVAMaxDiffyy, LevPackage, PriceIntP, PriceIntRawP, PricedDec, PricedDecShare, PricedOnsetLagMonths, RatioRailFifty, RatioRailHundredForty, RecordIntHighW, RecordIntLowW, RecordIntNoLag, RevDeepLocal, RevDeepLocalAbs, RevDeepLocalRel, RevDfuel, RevDfuelAbs, RevFleetWide, RevFleetWideAbs, RevFleetWideRel, RevFloorHigh, RevFloorHighAbs, RevFloorLow, RevFloorLowAbs, RevHeadTen, RevHeadTenAbs, RevHeadTwentyFive, RevHeadTwentyFiveAbs, RevNoRailRel, RevNoRailyyRel, RevQHighAbs, RevQHighRel, RevQLowAbs, RevQLowRel, RevRailFifty, RevRailFiftyyy, RevRailHundredForty, RevRailHundredFortyyy, RevRestFifteen, RevRestSixty, RevRestSixtyAbs, RevServ, RevServAbs, ShareConstructionDfuel, ShareConstructionRailFifty, ShareConstructionServ, ShareIndustryDfuel, ShareIndustryRailFifty, ShareIndustryRailHundredForty, ShareIndustryServ, ShareServicesRailFifty, ShareServicesRailHundredForty, ShareUtilitiesRailFifty, ShareUtilitiesRailHundredForty, ShareUtilitiesServ, StatBelow, StatDrift, StatTotalDevPpm, SupTwoQ, SupTwoQyy, SurchargeBillDEUBn, TableHighQyy, TableLowQyy, TargetedBehindBothDraws, TroughPremium, WaveBratio, WaveGapFourRest, WaveGapTwoRest, WaveInterEight, WaveInterTwo, WorstWeek
          507 macros defined, 413 used

## ledger: PASS

          claim ok: 'would each remove two fifths of it': LevStockAvg = 42 in [36, 44]
          claim ok: 'would each remove two fifths of it': LevDeepAvg = 43 in [36, 44]
          claim ok: 'each remove two fifths of the loss': LevStockAvg = 42 in [36, 44]
          claim ok: 'each remove two fifths of the loss': LevDeepAvg = 43 in [36, 44]
          claim ok: 'when the river still passes two to four fifths of its normal tonnage': KaubPassJul = 51 in [40, 80]
          claim ok: 'inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP)': AugWaveEurBn = 1.1 in [1, 2]
          claim ok: 'inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP)': AugWaveIndQ = 0.13 in [0.1, 0.2]
          claim ok: 'the refill time of inventories and the service rules by up to a third': max(RevRestFifteenAbs, RevRestSixtyAbs, RevServAbs) = 30 in [30, 37]
          claim ok: 'one extra week removes two fifths of the 2026 loss': LevStockAvg = 42 in [36, 44]
          claim ok: 'billion avoided, more than half the effect': 100*StockTAvoidedBn/StockAvoidedBn = 57.69 in [50, 75]
          claim ok: 'each of the four levers removes a slightly larger share of a smaller loss': min(CrossStockRail-LevStock, CrossDeepRail-LevDeep, CrossFleetRail-LevFleet, CrossStockTRail-LevStockT) = 1 in [0, 15]
          claim ok: 'one more week of them removes two fifths of the 2026 loss': LevStockAvg = 42 in [36, 44]
          claim ok: "The model's cumulated loss lies inside its 95\\,\\% band but below its centre": (ModelIntEnsMean - RecordIntLowW)/(RecordInt - RecordIntLowW) = 0.0303 in [0, 0.99]
          claim ok: 'a 15\\,\\% larger shortfall falls just short of its one-standard-deviation band': RecordIntLow - TableLowInt = 0.2 in [0.01, 0.5]
          claim ok: "the model's industrial loss lies within the 95\\,\\% band of their estimate": (ModelIntEnsMean - RecordIntLowW)/(RecordInt - RecordIntLowW) = 0.0303 in [0, 1.0]
          claim ok: "against an eighth of the model's firms near the river producing below their baseline": CorridorFirmsBelowRhineAug = 13 in [11, 14]
          claim ok: 'Industry carries more than a third of it': IndustryShare = 38 in [33.4, 50]
          claim ok: 'draw on the same national pool of fuel, carries over half': ShareRefining+ShareLandTransport+ShareLogistics+SharePower+ShareShipping = 58 in [50, 75]
          claim ok: 'the barge-dependent buyers alone a quarter': LevStockTAvg = 27 in [22, 28]
          claim ok: 'for 28 regions, the 27 member states of the European Union and Switzerland, and 50 sectors': NRegions = 28 in [28, 28]
          claim ok: 'for 28 regions, the 27 member states of the European Union and Switzerland, and 50 sectors': NSectors = 50 in [50, 50]
          claim ok: 'The other 39 sectors are placed on NUTS3 employment': NSectors - 11 = 39 in [39, 39]
          claim ok: 'sea lanes (948) and multimodal connectors at terminals and ports (1,490)': NEdges - 2979 - 4261 - 461 - 948 = 1490 in [1490, 1490]
          claim ok: 'more than two and a half times the industrial loss alone': RatioBase = 2.6 in [2.5, 2.8]
          claim ok: 'leave out an economy-wide loss two and a half times larger': 100/IndustryShareyy = 2.439 in [2.3, 2.7]
          claim ok: 'leave out an economy-wide loss two and a half times larger': RatioBase = 2.6 in [2.3, 2.7]
          claim ok: 'while doubling inventories reduces the loss by almost three quarters': 100*(1-LadderD/DEUlossQyy) = 73.08 in [66, 75]
          claim ok: 'spread evenly would cost two fifths less': 100*(1-FlatQ/DEUlossQ) = 41.44 in [36, 44]
          claim ok: 'cost a sixth more in sequence than apart': WaveInterShare = 16 in [15, 18.5]
          claim ok: 'or a faster refilling of inventories, would largely remove': max(WaveInterFour, WaveInterRest)/WaveInterShare = 0.3125 in [-0.5, 0.4]
          claim ok: 'and a fleet built for low water a fifth': LevFleetAvg = 21 in [17, 23]
          claim ok: 'what the railway can take on at short notice removes a quarter to more than a half': RevRailFiftyAbs = 25 in [22, 28]
          claim ok: 'what the railway can take on at short notice removes a quarter to more than a half': RevRailHundredFortyAbs = 57 in [50.5, 75]
          claim ok: "both below the benchmark's central value": RecordInt - TableLowInt = 1.9 in [0.01, 100]
          claim ok: 'the larger shortfall just short of its one-standard-deviation band': RecordIntLow - TableLowInt = 0.2 in [0.01, 0.6]
          claim ok: 'a loss that builds from July and more than doubles in the autumn': AutumnWaveQ/AugWaveQ = 2.367 in [2.0, 2.8]
          claim ok: 'costs \\finalbatch{\\AutumnWaveQ}\\,\\%, more than twice as much': AutumnWaveQ/AugWaveQ = 2.367 in [2.0, 2.8]
          claim ok: 'about two fifths less than the season as it happened': 100*(1-FlatQ/DEUlossQ) = 41.44 in [35, 45]
          claim ok: 'the loading curve by about a half up or down': 100*(TableLowQ/DEUlossQ-1) = 52.25 in [40, 60]
          claim ok: 'the loading curve by about a half up or down': 100*(1-TableHighQ/DEUlossQ) = 45.05 in [40, 60]
          claim ok: 'two suppliers per input down by nearly a half': 100*(1-SupTwoQ/DEUlossQ) = 45.05 in [44, 50]
          claim ok: 'no pooling up threefold': NoPoolQ/DEUlossQ = 3.063 in [2.7, 3.3]
          claim ok: 'no rail bypass for bulk up by three fifths': RevNoRailAbs = 61 in [56, 64]
          claim ok: 'are less than a third of the deliveries that German buyers miss': TransportWithheldShare = 29 in [25, 33.3]
          claim ok: 'doubling them for every buyer divides the 2018 loss by more than three': DEUlossQyy/LadderD = 3.714 in [3.05, 4.5]
          claim ok: 'doubling them divides the 2018 loss by more than three': DEUlossQyy/LadderD = 3.714 in [3.05, 4.5]
          claim ok: 'Goods producers and construction work off nearly a quarter of their backlog': 100*(100-NetShare)/(100-PerishableShare) = 23.68 in [20.5, 25]
          claim ok: 'it predicts an economy-wide loss two and a half times larger': 100/IndustryShareyy = 2.439 in [2.3, 2.7]
          claim ok: 'and one in fifty below half of it': CorridorStopRhineAug = 1.9 in [1.6, 2.4]
          claim ok: 'and the second costs a quarter more than it would have alone': 100*(WaveBafterAQ/WaveBQ-1) = 25 in [22, 28]
          claim ok: 'spread evenly over the season costs two fifths less': 100*(1-FlatQ/DEUlossQ) = 41.44 in [36, 44]
          claim ok: 'to the construction sites, a sixth': ShareConstruction+ShareCement = 16 in [15, 18.5]
          claim ok: 'make up nearly a quarter of their backlog once the river reopens': 100*(100-NetShare)/(100-PerishableShare) = 23.68 in [20.5, 25]
          claim ok: 'divides the loss by three compared with a model that keys every input to its region': NoPoolQ/DEUlossQ = 3.063 in [2.7, 3.3]
          claim ok: 'A fleet built for low water removes a fifth of the loss': LevFleetAvg = 21 in [17, 23]
          claim ok: 'and a quarter with its gain extended to 100\\,cm': RevFleetWideRemoves = 26 in [22, 28]
          claim ok: 'and the three together more than four fifths': LevPackageAvg = 84 in [80.5, 90]
          claim ok: 'they remove a quarter of the loss, at the scale of the rail response': RevRailFiftyAbs = 25 in [22, 28]
          claim ok: 'of past low waters more than a half': RevRailHundredFortyAbs = 57 in [50.5, 75]
          claim ok: 'removes a quarter to more than a half of the loss': RevRailFiftyAbs = 25 in [22, 28]
          claim ok: 'removes a quarter to more than a half of the loss': RevRailHundredFortyAbs = 57 in [50.5, 75]
          claim ok: 'two and a half months after the benchmark': PricedOnsetLagMonths = 2.7 in [2.25, 2.75]
          claim ok: '\\,\\% with four, and \\finalbatch{\\WaveInterEightAbs}\\,\\% less with eight': WaveInterEight = -0.9 in [-100, -0.05]
          claim ok: 'two thirds in its food chain': FRAFoodShare = 66 in [62, 71]
          claim ok: 'a sixth in road transport': FRARoadShare = 17 in [15, 18.5]
          claim ok: 'which sits below the median of both events': EnsMedian - DEUlossQ = 0.03 in [0.005, 10]
          claim ok: 'which sits below the median of both events': EnsMedianyy - DEUlossQyy = 0.09 in [0.005, 10]
          claim ok: 'nine per region--sector on average': NFirms/(NRegions*NSectors) = 9.085 in [8.5, 9.5]
          claim ok: 'The 39 other sectors are placed on NUTS3 employment': NSectors - 11 = 39 in [39, 39]
          claim ok: 'survey of ref.~\\citep{pichler2022} mapped to the 50 sectors': NSectors = 50 in [50, 50]
          claim ok: 'sea lanes (948) and multimodal connectors at terminals and ports (1,490)': NEdges - 2979 - 4261 - 461 - 948 = 1490 in [1490, 1490]
          claim ok: 'Road is under-represented by construction in Germany, the Netherlands, Belgium, France and Austria': max(ModalDERoad-73, ModalNLRoad-53, ModalBERoad-78, ModalFRRoad-89, ModalATRoad-69) = -8 in [-100, -1]
          claim ok: 'with the waterway share of liquids nearly a third too high': 100*(CargoLiquidIww/30-1) = 30 in [27, 33]
          claim ok: 'a quarter below at D\\"usseldorf and Duisburg': 100*(1-RhineDuisburgMt/110) = 25.45 in [22, 28]
          claim ok: 'above them on the Middle Rhine': min(KaubMt/50, RhineKoblenzMt/55) = 1.2 in [1.0, 1.5]
          claim ok: 'below them from Cologne to Duisburg': max(RhineKoelnMt/80, RhineDuisburgMt/110) = 0.825 in [0, 1.0]
          claim ok: 'within 10\\,\\% at Hamburg': max(abs(PortHamburgMt/99.6-1), abs(PortHavreMt/75.56-1), abs(PortMarseilleMt/67.26-1), abs(PortGenoaMt/46.6-1), abs(PortGothenburgMt/34.98-1), abs(PortBilbaoMt/31.53-1))*100 = 7.047 in [0, 10]
          claim ok: 'within a quarter at Dublin': max(abs(PortDublinMt/24.67-1), abs(PortNantesMt/28.48-1), abs(PortDunkirkMt/35.39-1), abs(PortBremerhavenMt/39.19-1))*100 = 23.45 in [10, 25]
          claim ok: 'a third below at Antwerp-Bruges': max(abs(100*(1-PortAntwerpMt/242.24)-100/3), abs(100*(1-PortAmsterdamMt/80.76)-100/3)) = 0.2092 in [0, 3.7]
          claim ok: 'about two fifths below at Barcelona': max(abs(100*(1-PortBarcelonaMt/51.46)-40), abs(100*(1-PortGhentMt/29.95)-40), abs(100*(1-PortValenciaMt/62.25)-40)) = 4.127 in [0, 5]
          claim ok: 'the preceding paragraph gives these within a third of the observations': max(abs(KaubMt/50-1), abs(KaubContMt/10-1), abs(ModalDERoad/73-1), abs(ModalDERail/21-1), abs(CargoDryRoad/53-1), abs(CargoDryRail/27-1), abs(CargoDryIww/20-1), abs(CargoLiquidRoad/28-1), abs(CargoLiquidRail/42-1), abs(CargoLiquidIww/30-1))*100 = 32.14 in [25, 33.4]
          claim ok: 'where the model is within a third of the counts except at Rotterdam': max(abs(PortHamburgMt/99.6-1), abs(PortBremerhavenMt/39.19-1), abs(PortAmsterdamMt/80.76-1), abs(PortAntwerpMt/242.24-1))*100 = 33.14 in [25, 33.4]
          claim ok: 'is a third of its observed tonne-kilometres': 100*NLTkmBn/110.8 = 35.2 in [30, 37]
          claim ok: 'and its waterways half': 100*NLWaterTkmBn/41.6 = 51.68 in [45, 55]
          claim ok: 'the model carries half to two thirds of the counts': RhineBaselMt/5.5 = 0.4727 in [0.45, 0.55]
          claim ok: 'the model carries half to two thirds of the counts': max(RhineStrasbourgMt/16, RhineKarlsruheMt/22) = 0.625 in [0.58, 0.72]
          claim ok: 'the Mannheim--Mainz reach is above them': RhineMannheimMainzMt/40 = 1.15 in [1.0, 2.0]
          claim ok: 'Rail keeps a higher share than observed in Austria': min(ModalATRail-29, ModalFRRail-9) = 3 in [1, 100]
          claim ok: 'intra-European trade uses the sea less in the model': DeepSeaShare-41.5 = 5.5 in [0.5, 100]
          claim ok: 'where the benchmark keeps a third, because the closures of November': 100*RecDec/RecNov = 36.13 in [30, 37]
          claim ok: 'at higher ones, where the benchmark keeps a third': 100*RecDec/RecNov = 36.13 in [30, 37]
          claim ok: 'from which the shortfall has fallen back by two thirds in December': 100*(1 - RecDec/RecNov) = 63.87 in [63, 70]
          claim ok: 'where the benchmark has nearly a fifth of its loss in each month': 100*RecAug/RecordInt = 18.68 in [17.6, 20]
          claim ok: 'nothing in August and September, where the benchmark has nearly a fifth': 100*RecSep/RecordInt = 18.87 in [17.6, 20]
          claim ok: 'the rerun on common inputs changes the sums by less than a fifth': 100*max(abs(1 - PricedInt/4.11), abs(1 - PricedIntB/2.48), abs(1 - PricedIntC/1.39)) = 13.67 in [0, 20]
          claim ok: 'the restrictive end of a range whose other end removes more than half of the loss': min(RevRailHundredFortyAbs, RevRailHundredFortyyyAbs) = 57 in [50.5, 100]
          claim ok: 'changes the tonnage turned away by less than 1\\,\\% in both years': DailyLoadingDiff = 0.7 in [0, 0.9]
          claim ok: 'when the cut is small, three quarters of it is re-sent': GateResentRec = 75 in [72, 78]
          claim ok: "the first wave does not move orders away from the river's suppliers": SupWeightWaveEnd - SupWeightStart = 0.7 in [0, 100]
          claim ok: 'total production stays within $10^{-6}$ of its initial value': StatTotalDevPpm = 0.65 in [0, 1]
          claim ok: 'USD a week, one is below its target': StatBelow = 1 in [1, 1]
          claim ok: 'Some twenty agents with orders of tens of dollars a week drift': StatDrift = 19 in [15, 25]
          claim ok: 'USD a week but one': StatBelow = 1 in [1, 1]
          claim ok: 'the drifts are confined to some twenty agents': StatDrift = 19 in [15, 25]
          claim ok: "each single lever removes a larger share of a smaller loss than under the paper's rule": min(CrossStockRail - LevStock, CrossDeepRail - LevDeep, CrossStockTRail - LevStockT, CrossFleetRail - LevFleet) = 1 in [1, 100]
          claim ok: 'it keeps in December half of its November loss at the balance-sheet inventories': PricedDecShare = 54 in [45, 55]
          claim ok: "and with a December twice the benchmark's": PricedDec/RecDec = 2.143 in [1.8, 2.2]
          claim ok: 'keep in December half of their November value at the balance-sheet inventories': PricedDecShare = 54 in [45, 55]
          claim ok: "nothing in August and September, a December twice the benchmark's": PricedDec/RecDec = 2.143 in [1.8, 2.2]

## pending: FAIL

    FAIL  sections/si.tex:27  unsure: model output, no macro, a difference between calibration runs (round 5 g04 and the round-6 ladder); calibration_log.md gives 816 -> 685 Mt (131 Mt) on the secondary ports then counted, not 140; not checkable on the base run's flow_score  | the ladder of fees sent 140~Mt back to the large ports
    FAIL  sections/si.tex:124  unsure: source of the weekly rail tonnage not cited (German rail freight about 350 Mt a year? a model figure?); cite it or derive it  | on about 6.7 Mt of rail freight a week, treated as a constant weekly capacity

## bare: PASS

          accepted: 170 years, 88 calendar dates, 569 numbers under ledger entries

## words: PASS

          accepted under ledger entries: 307

## refs: WARN

    warn  refs.bib: ademmer2020 is never cited
    warn  refs.bib: bachmann2022 is never cited
    warn  refs.bib: baqaee2019 is never cited
    warn  refs.bib: barrot2016 is never cited
    warn  refs.bib: basf2019 is never cited
    warn  refs.bib: bedoyamaya2024 is never cited
    warn  refs.bib: bonadio2021 is never cited
    warn  refs.bib: diem2022 is never cited
    warn  refs.bib: gobert2023 is never cited
    warn  refs.bib: koks2016 is never cited
    warn  refs.bib: koks2019 is never cited
    warn  refs.bib: mackenzie2012 is never cited
    warn  refs.bib: scholten2014 is never cited
    warn  refs.bib: turpijn2026 is never cited
    warn  refs.bib: vinke2023 is never cited
    warn  refs.bib: welch2022 is never cited
    warn  refs.bib: wenz2016 is never cited
    warn  26 cited entries have neither DOI nor URL (cannot be verified online): baw2026, bfg2026, bmv2019, bundesbank2025, ccnr2019, ccnr2023, climatetrace2024, contargo2026, dbcargo2026, dihk2026, dwd2026, ebv2025, eurostat2025regio, gem2025, icis2026, icpr2020, ifw2026, jonkeren2007, jonkeren2011, oecd2025icio, pegelonline2026, reuters2026, schuttevaer2026, spam2020, vgrdl2025, wiwo2026
          61 entries, 44 cited

## fresh: PASS

          regenerating with --tag r6_bycargo --lists 20261102
          507 macros and 16 tables regenerated

## compile: WARN

    warn  27 overfull hboxes
          compiled with C:\Users\Celian\.local\bin\tectonic.EXE; pdf written, copied to C:\dsc_runs\rhine2026\paper_gate_20261105_rates.pdf

VERDICT: FAIL
