# Paper gate: 6aaa98617957ab816097822f at 991f01c 2026-11-03

| check | status | findings |
|---|---|---|
| static | PASS | 0 |
| pdflatex | PASS | 0 |
| macros | WARN | 1 |
| ledger | PASS | 0 |
| pending | FAIL | 117 |
| bare | PASS | 0 |
| words | PASS | 0 |
| refs | WARN | 18 |
| fresh | NOT RUN | 0 |
| compile | WARN | 1 |

## pdflatex: PASS

          U+00E1 á LATIN SMALL LETTER A WITH ACUTE: 1x (pdfLaTeX T1: fine)
          U+00E8 è LATIN SMALL LETTER E WITH GRAVE: 1x (pdfLaTeX T1: fine)
          U+00F6 ö LATIN SMALL LETTER O WITH DIAERESIS: 1x (pdfLaTeX T1: fine)
          U+00FC ü LATIN SMALL LETTER U WITH DIAERESIS: 1x (pdfLaTeX T1: fine)
          U+2014 — EM DASH: 1x (pdfLaTeX T1: fine)

## macros: WARN

    warn  85 of 319 macros of numbers.tex are never used: ContainerValueShare, CorridorFirmsBelow, CorridorFirmsBelowDEU, CorridorFirmsBelowDEUAug, CrossDeepAloneBn, CrossDeepOnRailBn, CrossFleetAloneBn, CrossFleetOnRailBn, CrossStockTAloneBn, CrossStockTOnRailBn, DEUlossBnyy, DEUpeakWeekyy, DelayCost, DestatisNovyy, EnsMaxyy, EnsMinyy, FleetBeatsTargetedDraws, FleetLastDraws, IndVAMaxDiff, IndVAMaxDiffyy, LevPackage, PriceIntP, PriceIntRawP, RatioRailFifty, RatioRailHundredForty, RecordIntHighW, RecordIntLowW, RecordIntNoLag, ResentShare, RevDeepLocal, RevDeepLocalAbs, RevDeepLocalRel, RevDfuel, RevDfuelAbs, RevFleetWide, RevFleetWideAbs, RevFleetWideRel, RevFloorHigh, RevFloorHighAbs, RevFloorLow, RevFloorLowAbs, RevHeadTen, RevHeadTenAbs, RevHeadTwentyFive, RevHeadTwentyFiveAbs, RevNoRailRel, RevNoRailyyRel, RevQHighAbs, RevQHighRel, RevQLowAbs, RevQLowRel, RevRailFifty, RevRailFiftyyy, RevRailHundredForty, RevRailHundredFortyyy, RevRestFifteen, RevRestSixty, RevRestSixtyAbs, RevServ, RevServAbs, ShareConstructionDfuel, ShareConstructionRailFifty, ShareConstructionServ, ShareIndustryDfuel, ShareIndustryRailFifty, ShareIndustryRailHundredForty, ShareIndustryServ, ShareServicesRailFifty, ShareServicesRailHundredForty, ShareUtilitiesRailFifty, ShareUtilitiesRailHundredForty, ShareUtilitiesServ, SupTwoQ, SupTwoQyy, SurchargeBillDEUBn, TableHighQyy, TableLowQyy, TargetedBehindBothDraws, TroughPremium, WaveBratio, WaveGapFourRest, WaveGapTwoRest, WaveInterEight, WaveInterTwo, WorstWeek
          319 macros defined, 234 used

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
          claim ok: 'nine per region--sector on average': NFirms/(NRegions*NSectors) = 9.085 in [8.5, 9.5]
          claim ok: 'The 39 other sectors are placed on NUTS3 employment': NSectors - 11 = 39 in [39, 39]
          claim ok: 'survey of ref.~\\citep{pichler2022} mapped to the 50 sectors': NSectors = 50 in [50, 50]
          claim ok: 'sea lanes (948) and multimodal connectors at terminals and ports (1,490)': NEdges - 2979 - 4261 - 461 - 948 = 1490 in [1490, 1490]
          claim ok: 'where the benchmark keeps a third, because the closures of November': 100*RecDec/RecNov = 36.13 in [30, 37]
          claim ok: 'at higher ones, where the benchmark keeps a third': 100*RecDec/RecNov = 36.13 in [30, 37]
          claim ok: 'from which the shortfall has fallen back by two thirds in December': 100*(1 - RecDec/RecNov) = 63.87 in [63, 70]
          claim ok: 'where the benchmark has nearly a fifth of its loss in each month': 100*RecAug/RecordInt = 18.68 in [17.6, 20]
          claim ok: 'nothing in August and September, where the benchmark has nearly a fifth': 100*RecSep/RecordInt = 18.87 in [17.6, 20]
          claim ok: 'the rerun on common inputs changes the sums by less than a fifth': 100*max(abs(1 - PricedInt/4.11), abs(1 - PricedIntB/2.48), abs(1 - PricedIntC/1.39)) = 13.67 in [0, 20]
          claim ok: 'the restrictive end of a range whose other end removes more than half of the loss': min(RevRailHundredFortyAbs, RevRailHundredFortyyyAbs) = 57 in [50.5, 100]

## pending: FAIL

    FAIL  main.tex:64  model output, no macro: add to make_numbers.py (source: baseline Rhine flows vs CCNR counts, SI S2); also inconsistent with SI S2, where the Waal at Tiel is 84 vs 125 Mt (-33 %) and the delta below Dordrecht 102 vs 140 (-27 %)  | The Lower Rhine north of Duisburg and the Dutch delta carry 10 to 25\,\% less than observed
    FAIL  main.tex:64  model output, no macro: add to make_numbers.py (source: SI S2 Basel 2.6/5.5, Strasbourg 10/16, Karlsruhe 13/22 = 47-62 %)  | the Upper Rhine above Mannheim carries half to two thirds of the counts
    FAIL  main.tex:85  model output, no macro: onset of the loss in the floor (priced river with closures) representation, late October 2018 vs August (SI S9); add the onset week to make_numbers.py  | two and a half months after the benchmark
    FAIL  main.tex:93  model output, no macro; inconsistent with the batch: the reference run peaks in run week 18 (DEU_peak_week, tables/si_runs, the comment of \DEUpeakWeek), the week of 19 October when week 1 = 22 June as make_numbers.py states; only the ten further networks peak in weeks 16-17 (5 and 12 October)  | with the peak in the week of 5 or 12 October in every version
    FAIL  main.tex:93  inconsistent: the peak of \DEUpeakWeek is run week 18 = week of 19 October (week 1 = 22 June), not 12 October; model output (a date) with no macro  | of a week's value added in the week of 12 October
    FAIL  main.tex:106  model output hard-coded: use \WaveInterEight (value -0.9: about 1 % less, not 3 %); four and eight are the gap design  | \,\% with four, and 3\,\% less with eight
    FAIL  main.tex:121  unsure: twentyfold matches neither the model's largest surcharge (1/0.08 = 12.5 at the loading floor, less on the Lower Rhine) nor the multiples the paper cites (2.5x dry cargo in 2018, EUR 45 -> 200 = 4.4x for tankers in 2026)  | even when its rate rises twentyfold
    FAIL  main.tex:123  model output hard-coded: use \ResentShare (value 7: % of the tonnage cut at the gates that finds another route, weeks 12-19)  | About 10\% of the tonnage that is cut is rerouted
    FAIL  main.tex:138  model output, no macro: add France's loss by sector chain to make_numbers.py (source: firm losses of 2026_r6_bycargo_base)  | three-fifths in its food chain and a fifth in road transport
    FAIL  main.tex:138  model output, no macro; the batch table compare_runs_batch_jobs_20261102_main.csv gives AUT 218 but NLD 107 mUSD (0.1 bn); Spain not in the table  | Spain, Austria, and the Netherlands lose about 0.2~billion each
    FAIL  main.tex:138  inconsistent: SI S5 lists German inputs (1.2 bn) next to the farm products (0.5 bn) as the largest missing deliveries of French buyers  | French households among them; German inputs play no part in it
    FAIL  main.tex:157  model output hard-coded: use \FleetLastDraws (value seven)  | and the fleet last in nine of ten
    FAIL  main.tex:180  model output hard-coded: use \FleetLastDraws (value seven)  | and the fleet last on nine of ten
    FAIL  main.tex:182  inconsistent: Methods (l. 223) gives the 7 Sep outlook at 22 and 42 cm against observed 7 and -2 for the weeks of 21 and 28 September, misses of 15 and 44 cm (data: scenarios/2026.csv previous values)  | missed the end-of-September episode by 20 to 40\,cm
    FAIL  main.tex:197  model output, no macro; inconsistent with the batch of 2 Nov (tables/si_runs): the reference network ranks 5th of 11 in 2026 (1.11, median 1.14) and 3rd of 11 in 2018 (0.52, median 0.61), the lower half  | which sits in the upper half of the distribution of both events
    FAIL  main.tex:215  model output, no macro (port residuals, SI S2 / tab:ports); also inconsistent with SI S2: Hamburg (North Sea) within 10 %, the Venice lagoon (205 vs 28 Mt) and Malaga (26 vs 2) far outside 30 %  | the Mediterranean and Atlantic ports are within 30\,\% of the Eurostat counts while the North Sea ports are not
    FAIL  main.tex:225  unsure: daily vs weekly loading share; computed from the profiles and the table (data) or from runs? no macro  | changes the tonnage turned away by less than 1\,\% in both years
    FAIL  main.tex:229  model output, no macro: add to make_numbers.py (source: catch-up production of goods and construction, 2026_r6_bycargo_base)  | decays from 300 million USD a week in week 24 to 5 million in week 43, by about a fifth a week
    FAIL  main.tex:229  model output, no macro: add to make_numbers.py (source: the same catch-up series)  | the catch-up that a longer run would add is about 1\,\% of the backlog left at the end
    FAIL  main.tex:245  model output, no macro: from tables/si_prospective_sectors (si_tables.py: refining 12.1/14.9, chemicals 8.8/11.6 in Aug/Oct); bind to macros  | the model puts refining about 15\,\% and chemicals about 10\,\% below baseline in August and October
    FAIL  sections/si.tex:7  inconsistent: every run of the batch uses 0.32 for containers on the waterway (S2 line 19; jobs_20261102_main.txt), but S1 and Table tab:rates (whose caption says "the values used by every run") give the first version's 0.35  | containers 1.0 USD per ton-hour on road and rail, 0.35 on the waterway
    FAIL  sections/si.tex:11  inconsistent: the manufacturing targets of Table tab:stocks run 18-60 days (C10T12 and C29 18; C21, C26, C27, C30 60); 70 is the Bundesbank 2023 figure for divisions 26-27 (70.3 d), which the model sets at 60  | 18--70 days across manufacturing industries
    FAIL  sections/si.tex:19  model output, no macro: calibration round 3, about 30 Mt of containers through Kaub at a value of time of 0.30 against about 10 observed (calibration_log.md, 27 Oct)  | at 0.30 three times the observed tonnage does
    FAIL  sections/si.tex:19  model output, no macro: flow_score OVERALL 0.359 (2026_s07_flows) and 0.285 (r6_h01_feeder3): add to make_numbers.py  | fell from 0.36 for the first version to 0.29
    FAIL  sections/si.tex:21  model output, no macro: modal split by country of the calibrated baseline (flow_score/country_modal_split.csv of r6_h01_feeder3; values match); the Eurostat shares beside them are evidence: add to make_numbers.py or a generated table  | Germany 62 / 26 / 13 against 73 / 21 / 7, the Netherlands 39 / 6 / 55 against 53 / 6 / 41
    FAIL  sections/si.tex:21  model output, no macro: country_modal_split.csv of r6_h01_feeder3 (values match)  | Belgium 63 / 13 / 23 against 78 / 12 / 11, France 81 / 12 / 7 against 89 / 9 / 2
    FAIL  sections/si.tex:21  model output, no macro: country_modal_split.csv of r6_h01_feeder3 (values match)  | Austria 56 / 40 / 4 against 69 / 29 / 2, Switzerland 70 / 30 / 0 against 66 / 34 / 0
    FAIL  sections/si.tex:21  model output, no macro: country_modal_split.csv of r6_h01_feeder3 (values match)  | Poland 75 / 25 / 0 against 76 / 24 / 0, Italy 88 / 12 / 0 against 88 / 12 / 0
    FAIL  sections/si.tex:21  inconsistent: Switzerland is 70 against 66, so the model's road share is above Eurostat there (and Italy is 88 against 88)  | Road is under-represented everywhere by construction
    FAIL  sections/si.tex:21  model output, no macro: nst_modal_split.csv (DE manufacturing); inconsistent: the Eurostat rail share is 27.5 %, which rounds to 27 (68 / 27 / 5), not 28  | general cargo 77 / 19 / 4 against 68 / 28 / 5
    FAIL  sections/si.tex:21  model output, no macro: nst_modal_split.csv (DE agriculture + mining, oil and gas; values match)  | dry bulk 45 / 33 / 22 against 53 / 27 / 20 and liquid bulk 19 / 42 / 39 against 28 / 42 / 30
    FAIL  sections/si.tex:21  model output, no macro: 39.1 against 30.2 = +29 %, just below the 30-37 of "a third" ("nearly a third" is honest)  | with the waterway share of liquids a third too high
    FAIL  sections/si.tex:21  model output hard-coded: use \KaubMt (63) and \KaubContMt (11.6); 50--60 and about 10 are CCNR evidence  | Kaub carries 63~Mt a year against the 50--60 of the counts, of which 11.6 of containers against about 10
    FAIL  sections/si.tex:21  model output hard-coded: use \KaubDryMt (22.5, written 22) and \KaubLiquidMt (28.8, written 29)  | 22 of dry bulk and 29 of liquid bulk
    FAIL  sections/si.tex:21  model output, no macro: rhine.csv of r6_h01_feeder3 (values match); counts are CCNR evidence  | Koblenz 66 against 55--60, Bonn 65 against 65, Cologne 66 against 80, Duisburg 82 against 110
    FAIL  sections/si.tex:21  model output, no macro: rhine.csv of r6_h01_feeder3 (values match)  | Emmerich 106 against 118, the Waal at Tiel 84 against 125, the delta below Dordrecht 102 against 140
    FAIL  sections/si.tex:21  model output, no macro: rhine.csv of r6_h01_feeder3 (values match)  | the Upper Rhine at Basel 2.6 against 5.5, Strasbourg 10 against 16 and Karlsruhe 13 against 22
    FAIL  sections/si.tex:21  model output, no macro: first version (2026_s07_flows rhine.csv: Lower Rhine 0.64-0.74 of the counts, Tiel 12 against 125)  | a quarter less than observed on the Lower Rhine and a tenth of the Waal's tonnage
    FAIL  sections/si.tex:21  inconsistent: Cologne 66 against 80 (-18 %) and Cologne-Duesseldorf (-20 %) fall outside 15 % but are not named as exceptions; Mannheim-Mainz is +16 %. Model output, no macro (rhine.csv; Duesseldorf -23 %, Duisburg -25 %)  | is now within 15\,\% of the counts except at D\"usseldorf and Duisburg (a quarter below)
    FAIL  sections/si.tex:21  model output, no macro: basins.csv ALL DE 42.76 bn tkm (Eurostat 41.5)  | The German waterways as a whole carry 42.8 billion tonne-kilometres against 41.5 observed
    FAIL  sections/si.tex:21  model output, no macro: basins.csv of r6_h01_feeder3 (values match; Destatis 46321-0014 evidence)  | by section, the Rhine at the border 106 against 118~Mt, the Main 15 against 12, the Neckar 7 against 4
    FAIL  sections/si.tex:21  model output, no macro: basins.csv of r6_h01_feeder3 (values match)  | the Danube 4 against 3, the Rhine--Herne canal 9 against 11, the Elbe 10 against 5 and the Moselle 2 against 6
    FAIL  sections/si.tex:21  model output, no macro: model port tonnage against Eurostat 2023 (evidence); cite the generated table si_ports or add to make_numbers.py (values match si_ports)  | within 10\,\% at Hamburg (96~Mt against 100), Le Havre--Rouen (80 against 76), Marseille (72 against 67)
    FAIL  sections/si.tex:21  inconsistent: Dublin is 27.4 against 24.7, ratio 1.11 in si_ports, outside "within 10 %". Model output, no macro  | Genoa (48 against 47), Gothenburg (34 against 35), Bilbao (32 against 32) and Dublin (27 against 25)
    FAIL  sections/si.tex:21  model output, no macro: si_ports (Antwerp 0.67, Amsterdam 0.67, Bremerhaven 0.76)  | within a third at Antwerp-Bruges (162 against 242), Amsterdam (54 against 81), Bremerhaven (30 against 39)
    FAIL  sections/si.tex:21  inconsistent: Ghent is at 0.61 in si_ports, 39 % below, outside "within a third". Model output, no macro  | Dunkirk (29 against 35), Nantes (25 against 28), Ghent (18 against 30)
    FAIL  sections/si.tex:21  inconsistent: Barcelona 0.64 and Valencia 0.59 in si_ports are 36 % and 41 % below, outside "within a third". Model output, no macro  | Barcelona (33 against 51) and Valencia (37 against 62)
    FAIL  sections/si.tex:23  unsure: model-result summary with no macro; Kaub 63 against 50-60 is +5 to +26 %, the German waterway share 13 against 7  | the preceding paragraph gives these within 10 to 25\,\% of the observations
    FAIL  sections/si.tex:25  model output hard-coded (model port tonnage; 402 and 242 = Eurostat evidence): no macro, add to make_numbers.py or cite the generated table si_ports  | Rotterdam carries 131~Mt in the model against 402 handled, Antwerp-Bruges 162 against 242
    FAIL  sections/si.tex:25  model output, no macro: si_ports (values match)  | Trieste 6 against 51, Sines 11 against 40, Wilhelmshaven 2 against 30, Zeeland 6 against 37
    FAIL  sections/si.tex:25  model output, no macro: rhine.csv Emmerich 105.7 (CCNR 117.9)  | and the Rhine at the Dutch border, 106 against 118, shows
    FAIL  sections/si.tex:25  model output, no macro: si_ports (values match)  | Algeciras 7 against 79, Piraeus 8 against 45, Gioia Tauro 11 against 35
    FAIL  sections/si.tex:27  unsure: model output, no macro, a difference between calibration runs (round 5 g04 and the round-6 ladder); calibration_log.md gives 816 -> 685 Mt (131 Mt) on the secondary ports then counted, not 140; not checkable on the base run's flow_score  | the ladder of fees sent 140~Mt back to the large ports
    FAIL  sections/si.tex:27  model output, no macro: ports.csv (125.7 + 0.0 + 73.3 + 6.1 = 205 against 28.1; Szczecin 95.2 against 11.8)  | (Venice, Chioggia, Monfalcone and Porto Nogaro together 205~Mt against 28), at Szczecin (95 against 12
    FAIL  sections/si.tex:27  model output, no macro: ports.csv (values match)  | with Gda\'nsk at 33 against 80 as the other side of the same coin), Burgas (47 against 17)
    FAIL  sections/si.tex:27  model output, no macro: ports.csv (values match)  | Oslo (29 against 5), M\'alaga (26 against 2)
    FAIL  sections/si.tex:27  model output, no macro: flow_score summary.csv (secondary ports 786 Mt against Eurostat 634, 98 gazetteer ports)  | the 98 ports outside the top forty carry 786~Mt against 634
    FAIL  sections/si.tex:27  unsure: model-result summary with no macro; si_ports gives Hamburg -4 %, Bremerhaven -24 %, Amsterdam and Antwerp -33 %; Rotterdam net of crude and transhipment is not computed anywhere  | where the model is within 10 to 35\,\% of the counts once crude and transhipment are set aside
    FAIL  sections/si.tex:29  model output, no macro: country_modal_split / nst_modal_split NL (39.2 against 110.8 bn tkm = 35 %; waterways 21.5 against 41.6 = 52 %)  | is a third of its observed tonne-kilometres (39 billion against 111) and its waterways half (21.5 against 41.6)
    FAIL  sections/si.tex:29  model output, no macro: rhine.csv (Tiel 83.7, Dordrecht-Rotterdam 101.8)  | carry 84 and 102~Mt against 125 and 140 for the same reason
    FAIL  sections/si.tex:29  model output, no macro: basins.csv (values match)  | the Wesel--Datteln canal carries 3.5~Mt against 16, the Dortmund--Ems canal 4 against 15
    FAIL  sections/si.tex:29  model output, no macro: basins.csv (6.3 against 12.2)  | and the Mittellandkanal 6 against 12
    FAIL  sections/si.tex:29  model output, no macro: basins.csv (23.8 and 22.8 against 3.0)  | The Weser and the K\"ustenkanal, on the contrary, carry 24 and 23~Mt against 3
    FAIL  sections/si.tex:31  model output, no macro: rhine.csv (Basel 0.47, Strasbourg 0.62, Karlsruhe 0.61: Basel just under half)  | the model carries half to two thirds of the counts (Basel 2.6 against 5.5
    FAIL  sections/si.tex:31  model output, no macro: rhine.csv (values match)  | Strasbourg 10 against 16, Karlsruhe 13 against 22) while the Mannheim--Mainz reach is above them (46 against 40)
    FAIL  sections/si.tex:31  model output, no macro: add to make_numbers.py (source: Kaub reach of scenarios/rhine_capacities_anchored_r6_bycargo.csv x 7 days x load factor 0.30: total 175,900 t/day -> 369 kt; 290 = the CCNR file capacity 137,000 t/day -> 288 kt)  | the bulk through at 369 kt a week in the trough of 2018, where the fleet carries 290
    FAIL  sections/si.tex:31  model output, no macro: (62,900 + 80,600) t/day x 7 x 0.30 = 301 kt, anchored on the model baseline  | per class the bulk is allowed 301
    FAIL  sections/si.tex:31  model output, no macro: country_modal_split.csv (values match)  | Rail keeps a higher share than observed in Austria (40 against 29\,\%) and France (12 against 9)
    FAIL  sections/si.tex:31  model output, no macro: country_modal_split.csv DE (25.6 against 20.6)  | the German rail share, 26 against 21, carries the short-haul correction above
    FAIL  sections/si.tex:31  model output, no macro: flow_score summary.csv short_sea (47.2 % against Eurostat EU27 41.5 %)  | The share of deep-sea shipping in the maritime tonnage is 47\,\% against 41.5 observed
    FAIL  sections/si.tex:55  unsure: offline check on the inputs (disrupt-sc-data/EU/calibration_log.md, 30 Sep: 2018 10.18 vs 10.26 week-equivalents) made on the September loading table, not redone on the table rebuilt on 6 Oct; no macro  | changes the tonnage turned away by less than 1\,\% in both years
    FAIL  sections/si.tex:62  model output hard-coded, no macro (Table si_gate, re-sent/cut per profile week): add to make_numbers.py from the gate log of 2026_r6_bycargo_base  | in the profile weeks of the reference run, 7--34\,\% finds another route
    FAIL  sections/si.tex:62  model output hard-coded, no macro; \ResentShare (7, unused) is the trough-week share. inconsistent: Table si_gate gives 39/191, 60/177, 52/277 = 19-34 % in the first three weeks, not 20-34  | 20--34\,\% in the first three weeks and 13--29\,\% in the last three, 7--8\,\% in the episode weeks
    FAIL  sections/si.tex:62  model output, no macro: re-sent share of the recovery weeks (si_gate caption 2.0 of 2.6 Mt = 77 %); add to make_numbers.py and bind as a claim (72-78)  | when the cut is small, three quarters of it is re-sent
    FAIL  sections/si.tex:72  model output hard-coded, no macro (Table si_channels): add to make_numbers.py (source: routing_summary.csv of 2026_r6_bycargo_base and _gateonly, as si_tables.py channels_table)  | worth 22.4 billion USD in the reference run and 4.0 billion in the constraint-only run
    FAIL  sections/si.tex:72  model output hard-coded, no macro (Table si_channels): add to make_numbers.py (routing_summary.csv)  | while the capacity limit withholds 10.3 and 11.7 billion of bulk
    FAIL  sections/si.tex:72  model output hard-coded, no macro (Table si_channels): add to make_numbers.py (routing_summary.csv)  | 45.4 billion of them over the season, 45.2 under the surcharge alone and 13.4 when only the gate acts
    FAIL  sections/si.tex:72  model output hard-coded, no macro (Table si_channels, 2026_r6_bycargo_surchargeonly): add to make_numbers.py  | reroutes 26.7 billion of bulk and withholds nothing
    FAIL  sections/si.tex:76  model output hard-coded, no macro (gate log of 2026_r6_bycargo_base; si_gate caption): add to make_numbers.py  | The capacity limits withhold 10.8~Mt over the 36 gated weeks of the season as it happened
    FAIL  sections/si.tex:76  model output hard-coded, no macro (si_gate caption: withheld 10.1 Mt, 13 recovery weeks with a cut; 23 is the profile length)  | (the 23 profile weeks of Table~\ref{tab:gate}, 10.1~Mt, and the 13 recovery weeks
    FAIL  sections/si.tex:76  model output hard-coded, no macro (gate logs of 2026_r6_bycargo_base and wave_r6_bycargo_flat): add to make_numbers.py  | exceeds the reopened capacity, 0.7~Mt) and 10.2~Mt under the flat profile
    FAIL  sections/si.tex:76  model output hard-coded, no macro (gate logs of 2026_r6_bycargo_base and wave_r6_bycargo_flat): add to make_numbers.py  | (cut 13.8 and 12.4~Mt, re-sent 3.1 and 2.2~Mt): the realised tonnage withheld differs by 6\,\%
    FAIL  sections/si.tex:78  model output, no macro, first version: 2026_s07_full of 7 Oct (additional_data/revision_20261006_diagnostics.txt section 6), not redone on the per-class runs; add to make_numbers.py from 2026_r6_bycargo_full  | 48 German buyer region--sectors with at least one supplier pair cut at Kaub in the August episode (weeks 7--9)
    FAIL  sections/si.tex:78  model output, no macro, first version (2026_s07_full, revision_20261006_diagnostics.txt section 6): rerun on 2026_r6_bycargo_full  | keep 13.4\,\% of their offered deliveries with those pairs at the start of the season, 14.2\,\%
    FAIL  sections/si.tex:78  model output, no macro, first version (2026_s07_full, revision_20261006_diagnostics.txt section 6): rerun on 2026_r6_bycargo_full  | 14.6\,\% in the second episode and 13.4\,\% after the recovery
    FAIL  sections/si.tex:84  model output hard-coded, no macro (si_gate caption: 13 recovery weeks with a cut)  | the season's totals of the text add the 13 recovery weeks in which the gate still cuts
    FAIL  sections/si.tex:84  model output of the check run stationarity6w (additional_data/stationarity_20261005.txt, 5 Oct, before the per-class calibration), no macro: add to make_numbers.py or rerun on the r6cal caches  | total production stays within $10^{-6}$ of its initial value
    FAIL  sections/si.tex:84  model output of stationarity6w (stationarity_20261005.txt: 12,429 material firms, min production 0.979), no macro  | of the 12,429 firms producing more than 10,000 USD a week, one is below its target (by 2\,\%, from the first week
    FAIL  sections/si.tex:84  model output of stationarity6w (stationarity_20261005.txt week 6: 0.99880 to 1.00290), no macro  | their input inventories stay within $-0.1$ to $+0.3$\,\% of their targets by week six
    FAIL  sections/si.tex:84  model output of stationarity6w (20 firms below target in week 6), no macro  | Some twenty agents with orders of tens of dollars a week drift
    FAIL  sections/si.tex:140  model output of stationarity6w (S10 repeats S4), no macro  | every firm producing more than 10,000 USD a week but one (2\,\% below target, from the first week)
    FAIL  sections/si.tex:140  model output of stationarity6w (S10 repeats S4), no macro  | the inventories of these firms stay within $-0.1$ to $+0.3$\,\% of theirs
    FAIL  sections/si.tex:140  model output of stationarity6w (S10 repeats S4), no macro  | the drifts are confined to some twenty agents
    FAIL  sections/si.tex:86  inconsistent: model output hard-coded from an earlier batch; Table si_rail_weeks gives 40 to 586 kt in the profile weeks at 50 kt (28 to 568 at 140 kt) and S8 says 40 to 590; no macro  | the cut bulk that finds a rail route is 100 to 650 kt a week
    FAIL  sections/si.tex:90  inconsistent: the cross table and the Cross*/Wave*Rest macros come from the batch of 2 November 2026 (jobs_20261102_cross.txt, caption of si_cross); 9 October is the first version  | gives the two crossed experiments of 9 October 2026
    FAIL  sections/si.tex:90  unsure: \CrossStockTRail 36 against \LevStockT 28 (+8 points, +29 % relative) is more than slightly; stocks +4, fairway +1, fleet +5  | each single lever removes a slightly larger share of a smaller loss than under the paper's rule
    FAIL  sections/si.tex:101  inconsistent, stale model output, no macro: 5,746 is the first version's Kaub list (5 Oct routes, KI-49); the r6cal list of the per-class runs has 8,176 links (3,562 dry, 2,160 liquid, 2,454 container); 1.04 Mt is the first version's 1,036 kt, the per-class baseline is 1,210 kt a week (si_gate caption; \KaubMt/52); add to make_numbers.py  | 5,746 commercial links cross Kaub on their normal route, 1.04~Mt a week
    FAIL  sections/si.tex:101  model output, no macro: split of the services' missing refined fuel (extract_link_flows.py tables of 2026_r6_bycargo_full); add a macro and bind as a claim  | of which about half is withheld at the river and half rationed by refineries
    FAIL  sections/si.tex:101  model output hard-coded, no macro: French buyers' missing deliveries (link_flows_disrupted.csv.gz of 2026_r6_bycargo_full); add to make_numbers.py  | withheld at the river (0.5~billion), and German inputs (1.2~billion)
    FAIL  sections/si.tex:105  model output hard-coded, no macro: November of the priced river x2 (0.58, matched_estimand_2018_r6_bycargo.txt, 2018_r6_bycargo_priced_inv200); add PricedNovC to make_numbers.py  | and below it at twice the inventories (0.6)
    FAIL  sections/si.tex:105  model output, no macro: priced river x1 December/November = 1.20/2.22 = 54 %; add PricedDec to make_numbers.py and bind as a claim (100*PricedDec/PricedNov, 45-55)  | it keeps in December half of its November loss at the balance-sheet inventories
    FAIL  sections/si.tex:105  model output, no macro: priced river x1 December 1.20 against \RecDec 0.56 = 2.1x; add PricedDec and bind as a claim (PricedDec/RecDec, 1.8-2.2)  | and with a December twice the benchmark's
    FAIL  sections/si.tex:132  model output, no macro (S9 repeats S6): priced river x1 December/November = 1.20/2.22 = 54 %; add PricedDec and bind as a claim  | keep in December half of their November value at the balance-sheet inventories
    FAIL  sections/si.tex:132  model output, no macro (S9 repeats S6): priced river x1 December 1.20 against \RecDec 0.56 = 2.1x; add PricedDec and bind as a claim  | nothing in August and September, a December twice the benchmark's
    FAIL  sections/si.tex:105  first version's model outputs (2018_baseline, 2018_inv150, 2018_pipe of 22-28 Sep), frozen history, no macro: add as constants to make_numbers.py (like DEUlossQP) or accept as history  | gave 4.1, 2.5 and 1.4 percent-months at the three inventory levels
    FAIL  sections/si.tex:105  unsure: 1.7 is the earlier version's level-effect path (no record found); 'the published 1.5' is the benchmark's November, \RecNov = 1.55 (which rounds to 1.6), or a figure of ademmer2023? use \RecNov or cite  | (1.7\,\% in November against the published 1.5)
    FAIL  sections/si.tex:105  first version's model output (priced river with closures, runs of September), frozen history, no macro  | the tonnage past Kaub fell 81\,\% (dry bulk) and 70\,\% (liquid) in a closure week
    FAIL  sections/si.tex:105  first version's model output (priced river with closures), frozen history, no macro  | and 31\,\% in the tank-barge closure weeks of November 2018
    FAIL  sections/si.tex:105  evidence hard-coded: use \DestatisNovyy (34, defined in numbers.tex and never used)  | against 34\,\% year on year in the Destatis series
    FAIL  sections/si.tex:105  first version's model output (tanker-floor band, priced river), frozen history, no macro (40/60 cm are design)  | and the tanker floor at 40 or 60\,cm moved the loss by a factor of two
    FAIL  sections/si.tex:111  run counts that change with every batch (125 -> 128 on 3 Nov): add NRuns and the per-list counts to make_numbers.py from the job lists (si_tables.py runs_table); 2 is a date  | lists the 128 runs of the batches of 2 and 3 November 2026 on the capacities per cargo class (the paper set of 36,
    FAIL  sections/si.tex:111  run counts of the batch (jobs_20261102_paired/rev/ladder): add to make_numbers.py  | the paired levers of 60, the sensitivities of the revision of 16, the inventory ladder of 3,
    FAIL  sections/si.tex:111  run counts of the batch (jobs_20261102_cross/norail): add to make_numbers.py (15 days is design)  | rail ceiling and the wave-isolation profiles at a 15-day refill time, 8, the no-rail pair, 2,
    FAIL  sections/si.tex:111  run count of the batch (jobs_20261103_altriver): add to make_numbers.py  | and the priced river with closures at three inventory levels, 3;
    FAIL  sections/si.tex:124  model output, no macro: offline classification on the first version's Kaub list (jobs_20261020_norail.txt header; 100 - 85 % of Table si_thresholds?), not redone on the r6cal list; add to make_numbers.py  | 15\,\% of the bulk orders that cross Kaub have such a route
    FAIL  sections/si.tex:124  unsure: source of the weekly rail tonnage not cited (German rail freight about 350 Mt a year? a model figure?); cite it or derive it  | on about 6.7 Mt of rail freight a week, treated as a constant weekly capacity
    FAIL  sections/si.tex:124  model output hard-coded, no macro (Table si_rail_weeks: 40 to 586 kt offered in the profile weeks at 50 kt; 28 at 140 kt in 2018): add to make_numbers.py  | the cut bulk that finds a rail route is 40 to 590 kt a week

## bare: PASS

          accepted: 167 years, 90 calendar dates, 754 numbers under ledger entries

## words: PASS

          accepted under ledger entries: 311

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

## fresh: NOT RUN

          rerun with --regen (needs the run folders)

## compile: WARN

    warn  27 overfull hboxes
          compiled with C:\Users\Celian\.local\bin\tectonic.EXE; pdf written, copied to C:\dsc_runs\rhine2026\paper_gate_20261105_after.pdf

VERDICT: FAIL (not run: fresh)
