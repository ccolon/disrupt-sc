r"""Ledger of paper_gate.py after the author's round of 12 November 2026 (Overleaf 4dfe508, then
patch_main_20261112_round.py and patch_si_20261112_round.py): the entries of the sentences that the author or the round
reworded are entered again on their new wording, with the reason they had; then the entries whose sentence left the
manuscript are dropped and appended to ledger_dropped_20261112.txt. Running it again changes nothing.

    python studies/rhine2026/review/ledger_20261112_round.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402
from si_patchlib import OVERLEAF  # noqa: E402

MAIN, SI = "main.tex", "si.tex"
L = Ledger()
A, C = L.allow, L.claim
PROFILE = "scenarios/2026.csv (built 11 Nov 2026 by fetch_kaub.py; cluster/batch_20261111.md)"
LH = "mechanism_checks/lh_classification.csv and lh_sensitivity.txt (the offline classification of 14-15 September 2026, read again on 12 Nov 2026)"

# ------------------------------------------------------------------ main.tex: literals that may stay
A(MAIN, "Barge freight rates rose two and a half times on dry cargo", "evidence: ccnr2019 (2018 freight rates)")
A(MAIN, r"set a new one on 4 August, and fell to 5\,cm on 17 August. The tonnage passing the stretch fell by three-quarters",
  "evidence: pegelonline2026 (gauge), reuters2026/schuttevaer2026 (tonnage; the KBN count of the week to 13 Aug, 22 % of normal, in the loading-table ledger)")
A(MAIN, "firm agents, 251 regional household agents, and twelve external trading partners", "design: 251 household agents (NUTS2), twelve external partners")
A(MAIN, r"lowered by 15\,\% (blue triangles), and two suppliers per input (cross)", "design: loading-curve capacity reduction +-15 % and the two-supplier variant")
A(MAIN, r"with the eleven networks at $\times$1 (gray)", "design: number of networks; x1 is the balance-sheet level of the inventories, F9 (b) caption")
A(MAIN, "one supplier per input are not fitted to the benchmark", "design: suppliers per input (one or two)")
A(MAIN, r"After the August 2026 record (11\,cm in the week of 10 August), the river recovered to 67\,cm",
  f"data: {PROFILE}: week of 10 August 11.0 cm, week of 24 August 67.0 cm")
A(MAIN, "the loss cumulated over the 43 weeks of the run, divided by thirteen weeks", "design: run length 43 weeks (23 profile + 20 recovery); convention: a quarter = 13 weeks")
A(MAIN, "over the five weeks of the August episode", "convention: the August trough = run weeks 7-11 (make_numbers.py, AugWaveIndQ)")
A(MAIN, r"estimated in late July EUR 1--2 billion of industrial loss over five weeks (0.1--0.2 percentage points of third-quarter GDP)",
  "evidence: ifw2026 (statement of 28 July 2026: EUR 1-2 billion, 0.1-0.2 points of third-quarter GDP, five weeks)")
A(MAIN, "other estimates made in August and September gave 0.2--0.35 points",
  "evidence: bloomberg2026commerzbank (Commerzbank 0.35, 11 Aug), kiel2026autumn (0.2 adopted, 0.3 ceteris paribus, 3 Sept), jannsen2026lowwater (the same, Wirtschaftsdienst 106(9))")
A(MAIN, r"33\,\% of the Rhine-corridor firms reported production restrictions and 6\,\% a stop", "evidence: dihk2026 (survey of 29 July - 4 August)")
A(MAIN, "In counterfactual runs with normal water between the two episodes", "count: the two episodes of the wave-isolation design")
A(MAIN, "depends on the refill time of the inventory rule, 30 days,", "design: inventory restoration time tau = 30 days")
A(MAIN, "Low water has two direct effects", "count: the two channels")
A(MAIN, "even more than with the two together", "count: the two channels")
A(MAIN, r"freight cost is only about 5\,\% of the input bill of the median firm, and a quarter to a half for transport operators",
  "data: transport intensity theta_j of the agents from the OECD ICIO (inputs, Methods: 0 to 0.6 across agents), not a run output; no macro")
A(MAIN, "Across all deliveries in the 28 economies, only", "design: scope of 28 economies")
A(MAIN, "chemical companies built nine shallow-draft tankers", "evidence: wiwo2026")
A(MAIN, r"can still carry about 800 tonnes at a gauge of 30\,cm, compared with about 400 for a standard vessel", "evidence: wiwo2026, contargo2026")
A(MAIN, "It is the same for the 28 economies as a whole", "design: scope of 28 economies")
A(MAIN, "using two capacity levels for bulk-barge-to-wagon transfer", "design: two rail ceilings (50 and 140 kt)")
A(MAIN, "up to 50 kt a week, a ceiling calibrated on the 400 wagons that the national rail operator could add at short notice in August 2026 at two rotations a week",
  "design: rail ceiling 50 kt + evidence: dbcargo2026 (400 wagons, two rotations a week)")
A(MAIN, "With a higher ceiling of 140 kt a week, the response of all rail freight to past low waters", "design: rail ceiling 140 kt + evidence: ademmer2023 (derivation in Supplementary Section S8)")
A(MAIN, "With the 30-day refill time of the model, four weeks of normal water between the episodes", "design: restoration time 30 days, gap of four weeks (wave isolation)")
A(MAIN, "put nine low-water tankers into service since 2018, and seven more are planned", "evidence: wiwo2026")
A(MAIN, r"Raising or lowering the share of the normal tonnage it keeps off the river by 15\,\%", "design: loading-curve capacity reduction +-15 % (tablelow, tablehigh)")
A(MAIN, "18 products are poolable, standardized goods", "design: list of poolable products (SI S1)")
A(MAIN, r"divided by a utilization rate $u=0.8$, that is 125\,\% of the baseline", "design: capacity utilization rate u = 0.8, so capacity = 1/0.8 = 125 % of the baseline output")
A(MAIN, "The loading share acts in two ways", "count: capacity and surcharge")
A(MAIN, "The three classes are three fleets", "design: three cargo classes")
A(MAIN, r"adds more than 50\,km on a mode that carried less than 100\,km of the normal route", "design: mode-switch rule (access_km 50, line_haul_km 100)")
A(MAIN, r"For containers, the penalty of a switch is 15\,\% of the normal freight bill", "design: container mode-switch penalty")
A(MAIN, r"a week at 11\,cm passes a fifth of the normal tonnage, and a week below 5\,cm, 8\,\%",
  "data: loading table (scenarios/draught_table.csv: 0.19 at 11 cm, floor 0.08 below 5 cm)")
A(MAIN, "Losses are expressed as a share of a quarter (13 weeks)", "convention: a quarter = 13 weeks")
A(MAIN, "the loading-curve variants, and two suppliers per input", "design: loading-curve variants and the two-supplier run")
A(MAIN, r"A local variant adds the 20\,cm on the Kaub stretch only", "design: deeplocal variant")
A(MAIN, r"in sequence with 1, 2, 4, and 8 weeks of normal water (200\,cm at Kaub)", "design: wave-isolation gaps")
A(MAIN, "the sum of the losses of the two episodes alone", "count: two episodes")
A(MAIN, "The transport network is the TEN-T network of the European Commission", "convention: TEN-T is the network's name (the gate reads TEN as the number word ten)")
A(MAIN, r"raised and lowered by 15\,\%, the model gives", "design: loading-curve variants with the capacity reduction +-15 % (tablelow / tablehigh)")
A(MAIN, r"and the fleet comes last in \FleetLastDraws{} of ten", "design: ten further networks")
A(MAIN, "the single levers on top of the 50 kt rail ceiling; the two episodes at a refill time of 15 days",
  "design: the crossed experiments of 2 November 2026 (Methods; the list itself is in Supplementary Section S7)")
A(MAIN, "with a 50-kt barge-to-rail capacity", "design: the rail ceiling of 50 kt a week (the author's wording of 12 Nov 2026)")
A(MAIN, r"German firms within 50\,km of the Rhine produce below 99\,\% of their baseline and \CorridorStopRhineAug\,\% below half of it",
  "design: the survey comparison of early August 2026, thresholds of the firm counts (Results; the full comparison is in Supplementary Section S6)")
A(MAIN, r"It stayed below 25\,cm until late October, rose to 45\,cm in the week of 26 October, and fell back to 18\,cm in the first week of November",
  f"data: {PROFILE}, weeks of 5, 12 and 19 October 5.8, 13.5 and 21.0 cm; 26 October 45.3; 2 November 18.0")
A(MAIN, r"which show the river above 130\,cm from 16 November",
  f"data: {PROFILE}, weeks of 16 and 23 November 133.3 and 134.0 cm (BfG 14-day forecast of 11 November, six-week outlook of 9 November)")

# ------------------------------------------------------------------ main.tex: words bound to macros
C(MAIN, "would each remove two-fifths of it", "LevStockAvg", [36, 44], "result: % of the German loss avoided by one week of inventories, mean of the eleven networks; two-fifths = 36-44")
C(MAIN, "would each remove two-fifths of it", "LevDeepAvg", [36, 44], "result: % of the German loss avoided by the 20 cm deeper fairway, mean of the eleven networks; two-fifths = 36-44")
for text in ("each removes two-fifths of the loss", "each remove two-fifths of the loss"):          # Introduction; Discussion
    C(MAIN, text, "LevStockAvg", [36, 44], "result: % of the German loss avoided by one week of inventories, mean of the eleven networks; two-fifths = 36-44")
    C(MAIN, text, "LevDeepAvg", [36, 44], "result: % of the German loss avoided by the deeper fairway, mean of the eleven networks; two-fifths = 36-44")
C(MAIN, "one extra week removes two-fifths of the 2026 loss", "LevStockAvg", [36, 44],
  "result: % avoided by one week of inventories, mean of the eleven networks (the reference draw \\LevStock would read a half); two-fifths = 36-44")
C(MAIN, "one more week of them removes two-fifths of the 2026 loss", "LevStockAvg", [36, 44], "result: % avoided by one week of inventories, mean of the eleven networks; two-fifths = 36-44")
C(MAIN, "The same week held by the barge-dependent buyers alone removes a quarter", "LevStockTAvg", [22, 28], "result: % avoided by the targeted week, mean of the eleven networks; a quarter = 22-28")
C(MAIN, "while doubling inventories reduces the loss by almost three-quarters", "100*(1-LadderD/DEUlossQyy)", [66, 75], "result: % of the 2018 loss removed by inventories x2; almost three-quarters = 66-75")
C(MAIN, "What the railway can take on at short notice removes a quarter to more than a half", "RevRailFiftyAbs", [22, 28], "result: rail 50 kt (lower end); a quarter = 22-28")
C(MAIN, "What the railway can take on at short notice removes a quarter to more than a half", "RevRailHundredFortyAbs", [50.5, 75], "result: rail 140 kt (upper end); more than a half = 50.5-75")
C(MAIN, "Goods producers and construction work off nearly a quarter of their backlog", "100*(100-NetShare)/(100-PerishableShare)", [20.5, 25],
  "result: backlog worked off by the catch-up sectors; nearly a quarter = 20.5-25")
C(MAIN, "The model predicts an economy-wide loss two and a half times larger", "100/IndustryShareyy", [2.3, 2.7], "result: 2018 loss over its industrial part (Introduction; the Discussion repeats the sentence); 2.3-2.7")
C(MAIN, "The model predicts an economy-wide loss two and a half times larger", "RatioBase", [2.3, 2.8], "result: 2026 loss over its industrial part, reference network (the Discussion's sentence); 2.3-2.8")
C(MAIN, "and the building-materials chain, a sixth", "ShareConstruction+ShareCement", [15, 18.5], "result: building-materials chain, % of the German gross loss; a sixth = 15-18.5")
C(MAIN, "The three together remove more than four-fifths", "LevPackageAvg", [80.5, 90], "result: package, mean of the eleven networks; more than four-fifths = 80.5-90")
C(MAIN, "It can decrease the loss by a quarter with a 50-kt barge-to-rail capacity", "RevRailFiftyAbs", [22, 28], "result: rail 50 kt; a quarter = 22-28")
C(MAIN, "losses start two and a half months later", "PricedOnsetLagMonths", [2.25, 2.75],
  "result: priced river with closures (2018_r6_bycargo_priced), first week of German loss against the first day of the benchmark's first month of shortfall (August; the benchmark is monthly); two and a half months = 2.25-2.75")
C(MAIN, "two-thirds in its food chain", "FRAFoodShare", [62, 71], "result: France's gross loss in crops (A01) and the food industry (C10-12), % of its loss, reference network; two-thirds = 62-71")
C(MAIN, "The other 39 sectors are placed on NUTS3 employment", "NSectors - 11", [39, 39], "Methods: the sectors placed on employment")
C(MAIN, "divides the loss by about three and a half compared with a model in which every input is specific to its region of origin", "NoPoolQ/DEUlossQ", [3.25, 3.75],
  "result: the run without pooling over the reference run; about three and a half = 3.25-3.75")

# ------------------------------------------------------------------ si.tex
A(SI, r"adds more than 50\,km (the access allowance) on a mode", "design: access allowance of the modal-switch rule (50 km)")
A(SI, "With two and four weeks of normal water between them", "design: gaps of the wave experiment (scenarios/2026_waveAB_gap2/gap4.csv)")
A(SI, "at 15 days, the buyers hit by the first episode", "design: refill time 15 days")
A(SI, r"the loading curve with its capacity reduction raised and lowered by 15\,\%; two suppliers per input",
  "design: loading-table band x1.15 / x0.85 (draught_table_low/high.csv); two suppliers per input")
A(SI, r"The loading share of the central table is raised by 0.10 between 15 and 55\,cm", "design: the fleet lever (scenarios/draught_table_lowwater.csv)")
A(SI, "against about half of that for a standard vessel", "evidence: single-vessel loads at 30 cm (contargo2026; loading table, vessel column)")
A(SI, r"This fleet loads more at every gauge between 15 and 55\,cm", "design: the fleet lever")
A(SI, "The two differ in shape. The model is spiky", "count: model and regression paths")
A(SI, "on the 2,831 origin--destination pairs (5,707 links) whose bulk crosses Kaub, in a test of September 2026 with the reach closed to bulk (week 6 of a ten-week run",
  f"data: {LH}: 2,831 pairs, 5,707 links (lh_links.csv); the classification rests on week 6 of the ten-week test run")
A(SI, "Under the kilometer thresholds alone, 1,553 pairs find no alternative (833 million USD of the week's orders) and 1,278 deliver on a route that is not a change of mode (409 million)",
  f"data: {LH}: 1,553 give up; 1,224 deliver on the own-modes search and 54 on the free search, none of them a change of mode by the rule (1,278); orders 833 and 409 million USD")
A(SI, r"For nine-tenths of the pairs without an alternative, the cheapest route would leave the river at Koblenz, pass the reach by land, and return to a barge. The land leg is 88\,km of truck for two-thirds of the pairs without an alternative, and a shorter truck leg or a train for the others",
  f"data: {LH}: of the 1,553 pairs without an alternative, 1,400 (90 %) have a candidate on their own modes; its added road leg is 87.5-89 km for 1,008 (65 %) and 50-87.5 km for 199; for 193 an 86 km rail leg replaces it")
A(SI, r"already has 100\,km or more of road (35\,\% of all pairs)", f"data: {LH}: 980 of the 2,831 pairs (34.6 %)")
A(SI, r"rises from 67 to 85\,\%", f"data: {LH}: share of the week's orders given up, 0.67 under the kilometer rule and 0.85 with road never a line-haul mode for bulk (Table S-thresholds)")
A(SI, "The two episodes at a 15-day refill time", "design: the refill time of the crossed runs (jobs_20261102_cross.txt, *_rest15)")
A(SI, "with a refill time of 15 days instead of 30. At 15 days, the two episodes", "design: refill times of the inventory rule, 30 days in the paper and 15 in the crossed runs")
A(SI, "A buyer that refills in 15 days orders, each week, twice as large a part of its inventory gap",
  "design: the order adds (target - inventory)/tau to the needs (Section S4); tau = 15 days against 30 doubles that part")
A(SI, r"A supplier produces at most 125\,\% of its baseline output (the utilization rate of 0.8, Section~S4)", "design: capacity = baseline output / u, u = 0.8 (Section S4)")
A(SI, r"passes at most 102\,\% of its normal tonnage", "design: the capacity of a reach is its baseline flow plus a 2 % headroom (Section S3)")
A(SI, r"that it keeps off the river, raised or lowered by 15\,\%", "design: the two variants of the loading curve (draught_table_low.csv, draught_table_high.csv: capacity reduction x1.15 and x0.85)")

dropped = L.drop_missing(OVERLEAF)
L.save()
if dropped:
    print(f"{len(dropped)} dropped (the list of the round is review/ledger_dropped_20261112.txt, rebuilt from the ledger files against the commit before the round)")

# ---- added after the first pass of the gate: the caption of the table that came from the main text
L2 = Ledger()
L2.allow(SI, r"Days of low water at Kaub (below 78\,cm)","convention: the low-water mark of the Kaub gauge (GlW, 78 cm), the threshold of the regression's day count")
L2.save()

# ---- second pass (patch_main_20261112_round_b.py): a sentence of the 2026 Results now starts at 'The weekly mean'
L3 = Ledger()
L3.allow(MAIN, r"The weekly mean was 2\,cm in the week of 28 September, and the daily mean $-5$\,cm on 1 October",
         f"data: {PROFILE}, week of 28 September 1.8 cm; scenarios/kaub_daily_2026.csv, 1 October -4.8 cm")
dropped3 = L3.drop_missing(OVERLEAF)
L3.save()
