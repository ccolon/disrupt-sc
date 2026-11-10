r"""Ledger of paper_gate.py after the author's revision of the SI of 10 November 2026, section by section (the sections
are added to this script as they are answered; running it again changes nothing).

    python studies/rhine2026/review/ledger_si_20261110.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402

L = Ledger()
SI, MAIN = "si.tex", "main.tex"

# ---------------------------------------------------------------- main.tex (the author's edits of 10 Nov)
L.allow(MAIN, "Anthropic Fable 5.1 was used", "count: a product version in the author's AI disclosure")

# ---------------------------------------------------------------- S1 Scope and data
L.drop("Eleven sectors use facility data",
       "roads (2,979 edges), railways (4,261), inland waterways (461, the Rhine",
       "as a chain of thirty named reaches",
       "eighteen commodity-like products are pooled across regions",
       "The 39 other sectors are placed on NUTS3 employment",
       r"survey of ref.~\citep{pichler2022} mapped to the 50 sectors")
L.allow(SI, "Ten sectors use facility data. Nine keep their facilities as points",
        "count: the ten facility sectors of the sentence (B05, B06, B07, C19, C20, C17-18, C24B, C23, C24A kept as points; D aggregated "
        "to NUTS2 capacity); crops (A01) use a gridded source and are named before")
L.claim(SI, "The 39 other sectors are downscaled using NUTS3 employment", "NSectors - 11", [39, 39],
        r"data bound to the macro: \NSectors less crops (A01) and the ten facility sectors")
L.allow(SI, "roads (2,979 edges), railways (4,261), inland waterways (461, including 30 for the Rhine from Basel to Rotterdam)",
        "data: edge counts by mode of the TEN-T extraction of 29 August 2026; the Rhine is a chain of 30 named reaches")
L.claim(SI, r"survey of Pichler et al.~\citep{pichler2022} mapped to the 50 sectors", "NSectors", [50, 50],
        r"data bound to the macro: the literal 50 is \NSectors")
L.allow(SI, "We assume that 18 commodity-like products are pooled across regions",
        "count: the eighteen pooled products listed in the sentence (the pooled sectors of the configuration)")
L.claim(SI, r"\textbf{The criticality survey mapped to the 50 sectors.}", "NSectors", [50, 50],
        r"data bound to the macro: the literal 50 is \NSectors (caption of Table S-criticality)")
L.allow(SI, r"whose industries are the 55 of the World Input--Output Database (NACE Rev.~2)",
        "data: the 55 industries of the World Input-Output Database in which the survey is expressed (pichler2022); NACE revision 2")
L.claim(SI, "how many of its 50 input sectors the survey rates", "NSectors", [50, 50],
        r"data bound to the macro: the literal 50 is \NSectors")
L.allow(SI, "(a depleted input halves output)", "design: the rule of an important input in the production function (Methods)")
L.allow(SI, r"an input below 2\,\% of the buyer's input costs is considered non-critical",
        "design: the 2 % threshold of the critical-input rule (Methods)")
L.allow(SI, r"Over the 2,500 sector-to-sector pairs, 18\,\% of the inputs are critical, 9\,\% important and 73\,\% non-critical",
        "data: shares of the 50 x 50 cells of additional_data/input_criticality.csv (si_tables.criticality_table computes 18 / 9 / 73)")

# ---------------------------------------------------------------- S2 Baseline calibration
EUROSTAT_PORTS = "evidence: Eurostat mar_go_aa 2023, gross weight of goods handled (Table S-ports)"
CCNR = "evidence: ccnr2023 (the counts at Emmerich and Iffezheim and the estimates between them, scenarios/rhine_capacities.csv)"
L.allow(SI, "To match those targets, we adjusted four families of logistic parameters",
        "count: the four families of the list that follows (waterway rates, rail rates, seaport fees, value of time of containers on waterways)")
L.allow(SI, "applies to the Rhine and to eight waterways connected to it or to the North Sea ports",
        "count: the eight waterways named in the sentence, which carry the Rhine's rates in the run parameters (basic_cost.waterways)")
L.allow(SI, r"the Albert canal and the Meuse 1.2, the Main, Moselle, Neckar, Saar, Danube, Seine, Rh\^one, Sa\^one and the Ruhr canals 1.3, the Lek 1.5, the Mittellandkanal, the Elbe lateral canal, the Main--Danube canal, the K\"ustenkanal and the Berlin waterways 2, the Weser 2.2, the Elbe, the Oder and the Vltava 3, the Po system 4, and every waterway not named 1.5",
        "design: waterway rates by waterway as multiples of the Rhine's (parameters.yaml of the reference run, basic_cost.waterways: 0.012, 0.013, 0.015, 0.020, 0.022, 0.030, 0.040 against 0.010 for dry bulk; default 0.015)")
L.allow(SI, r"it is $3\log_{10}(100\,\mathrm{Mt}/T)$ USD per tonne for containers, kept between 0 and 12, and a third of it for other cargo",
        "design: the fee ladder of the calibration (calibration/round6/derive_feeder_ladder.py: a = 3, T_ref = 100 Mt, cap 12, other cargo a third)")
L.allow(SI, "its fee is 0.75 USD per tonne for all cargo, where the formula gives 0.28 for containers and 0.09 for other cargo",
        "design and data: Amsterdam in port_fees_feeder_a3.yaml (0.75); Eurostat 2023 throughput 80.8 Mt gives 3 log10(100/80.8) = 0.28 and a third of it, 0.09")
L.allow(SI, r"It is set at 0.32 USD per tonne-hour. \textit{Ceteris paribus}, at 0.35 no container is put on barges on the Rotterdam--Ruhr corridor, and at 0.30 barge containers overshoot the observed tonnage by three times; 0.32 gives the observed order of magnitude at Kaub",
        "design and result of the calibration: the value of time of containers on waterways (job-list override 0.32; the runs at 0.35 and 0.30 of the calibration rounds, as the sentence of the earlier version)")
L.allow(SI, "by 8 to 15 percentage points",
        "data: road share of tonne-km, Eurostat 2023 minus model, as rounded in Table S-modal (France 8, Germany 11, Austria 13, Netherlands 14, Belgium 15; 8.3 to 14.2 unrounded in country_modal_split.csv of the base run)")
L.allow(SI, r"Kaub carries \KaubMt~Mt a year against 50--60 in the counts", CCNR + "; about 50 Mt past Kaub, 55-60 up to Koblenz-Bonn")
L.allow(SI, r"of the forty largest European seaports are within 30\,\% of the Eurostat statistics",
        "design: the 30 % band of the count \\PortsWithinThirty; forty = the seaports of the calibration")
L.allow(SI, "The residuals fall into four kinds, three of which are off the Kaub path", "count: the four residuals described in the paragraphs that follow")
L.allow(SI, r"amount to \RhineEmmerichMt~Mt against 118", CCNR + "; Emmerich 118 Mt")
L.allow(SI, r"Oslo (\PortOsloMt{} against 5) and M\'alaga (\PortMalagaMt{} against 2)", EUROSTAT_PORTS + ": Oslo 5.3, Malaga 2.1 Mt")
L.allow(SI, r"ports outside the forty largest carry \SecPortsMt~Mt against \SecPortsObsMt", "count: forty = the seaports of the calibration")
L.allow(SI, r"(Basel \RhineBaselMt{} against 5.5, Strasbourg \RhineStrasbourgMt{} against 16, Karlsruhe \RhineKarlsruheMt{} against 22), while the Mannheim--Mainz reach is above them (\RhineMannheimMainzMt{} against 40)",
        CCNR + ": Basel 5.5, Strasbourg 16, Karlsruhe 22, Mannheim-Mainz 40 Mt")
L.allow(SI, "The model therefore understates the exposure of these two regions to Kaub", "count: Switzerland and Alsace, named in the sentence before")
L.allow(SI, "The 30 largest seaports by gross weight of goods handled", "count: the rows of Table S-ports above the line (si_tables.ports_table, top_n = 30)")
L.allow(SI, r"the ports outside the 40 largest where the model routes 50~Mt or more", "design: the selection of the rows below the line (si_tables.ports_table, outside_mt = 50)")
L.claim(SI, "where the model is within a third of the counts, except at Rotterdam",
        "max(abs(PortHamburgMt/99.6-1), abs(PortBremerhavenMt/39.19-1), abs(PortAmsterdamMt/80.76-1), abs(PortAntwerpMt/242.24-1))*100", [25, 33.4],
        "result: Hamburg -4, Bremerhaven -24, Amsterdam -33, Antwerp-Bruges -33 % against Eurostat 2023 gross weight; within a third = up to 33.4")
L.claim(SI, "is, in the model, a third of its observed tonne-kilometers", "100*NLTkmBn/110.8", [30, 37],
        "result: Dutch inland tkm 39 against 110.8 bn = 35 %; a third = 30-37")
L.claim(SI, "the model carries half to two-thirds of the counts", "RhineBaselMt/5.5", [0.45, 0.55],
        "result: the lower end, Basel 2.6 against 5.5 = 0.47; half = 0.45-0.55")
L.claim(SI, "Above Mannheim, the model carries half to two-thirds of the counts", "max(RhineStrasbourgMt/16, RhineKarlsruheMt/22)", [0.58, 0.72],
        "result: the upper end, Strasbourg 10 against 16 = 0.62 (Karlsruhe 0.59); two thirds = 0.58-0.72")

# ---------------------------------------------------------------- S3 Scenario construction
L.drop("from the raw 15-minute values of PEGELONLINE")   # reworded the same day (an overfull line)
L.allow(SI, "four kinds of statistic", "count: the four kinds of statistic listed in the sentence")
L.allow(SI, "(raw 15-minute values)", "data: resolution of the gauge record (pegelonline2026) behind scenarios/2026.csv")
L.allow(SI, "the six-week outlook of the same institute of 28 September", "data: horizon of the BfG outlook (bfg2026)")
L.allow(SI, r"had put the weeks of 14, 21 and 28 September at 12, 22 and 42\,cm; the observed means were 25, 7 and about $-2$ (the last from two observed days and the outlook of 28 September)",
        "data: BfG outlook of 7 Sep, medians of the weeks of 14/21/28 Sep (scenarios/bfg_6week_kaub_20260907.csv), against the 2026 profile of 30 Sep (scenarios/2026.csv: 25.2, 6.6 and -1.7 cm)")
L.allow(SI, "Two stress profiles therefore take the outlook's 25th and 75th percentile for the forecast weeks",
        "data: the 25-75 % quantiles of the BfG outlook of 28 Sep (scenarios/2026_q25.csv, 2026_q75.csv)")
L.allow(SI, r"stays at 0.08 below 5\,cm", "data: floor of the loading table (scenarios/draught_table.csv, row 5 cm)")
L.allow(SI, r"are three fleets: $K_{r,c}=\max\!\big(s_{r,c}\,T_r,\;1.02\,F_{r,c}\big)$",
        "design: the capacity per cargo class (anchor_rhine_capacities.py --by-cargo --headroom 0.02: the larger of the counted tonnage split by the baseline's class shares and the baseline flow of the class plus 2 %)")
L.allow(SI, r"and the model's own flow plus 2\,\% elsewhere", "design: the headroom of the anchored capacities (0.02)")
L.allow(SI, "At Kaub this gives 175,900 t a day in total, against 137,000 in the counts: 32,400 for the container vessels, 62,900 for the dry-bulk vessels and 80,600 for the tank barges",
        "data: scenarios/rhine_capacities_anchored_r6_bycargo.csv, reach rhine_mainz_koblenz (per-class capacities and their sum), against scenarios/rhine_capacities.csv (137,000 t a day)")
L.allow(SI, r"Headrooms of 10 and 25\,\% instead of 2 are tested in Section", "design: the two headroom runs of the sensitivity list (2026_r6_bycargo_head10, _head25)")
L.allow(SI, "and one third of its excess over 1 on the Lower Rhine reaches. This factor of one third is an assumption",
        "design: lower_rhine_factor = 1/3 (run_rhine.py, DEFAULT_LOWER_RHINE_FACTOR)")
L.allow(SI, "runs with a factor of zero and of one gave the same loss",
        "history: the runs of 15 September 2026 with the factor at 0 and at 1 (2026_fc0910_lr0, 2026_fc0910_lr1; additional_data/compare_runs_batch_20260915.csv)")

# ---------------------------------------------------------------- S4 Mechanism tests
CLASSIF = "data: the offline classification of the Kaub-crossing bulk pairs in the ten-week test run of 14-15 September 2026 (si_tables.thresholds_table; evidence/giveup_thresholds_by_cargo.md)"
L.allow(SI, "a truck carries 25 tonnes, against 2,000 and more for a barge or an ore train", "convention: orders of magnitude of the payloads (the sentence of the earlier S3)")
L.allow(SI, r"when it carries 100\,km or more of it (the line-haul threshold)", "design: the line-haul threshold of the modal-switch rule (run_rhine.py --line-haul-km 100)")
L.allow(SI, "on the 2,831 origin--destination pairs (5,707 links) whose bulk crosses Kaub, in a ten-week test run", CLASSIF)
L.allow(SI, "Under the kilometer thresholds alone, 1,553 pairs find no acceptable route (833 million USD of the week's orders), 1,224 deliver on their own modes (385 million) and 54 on a path without penalty (24 million)", CLASSIF)
L.allow(SI, r"for nine tenths of the pairs without a route, the alternative is a barge to Koblenz, 88\,km of truck around the reach and a barge again, at a median surcharge of 49\,\% on the freight; it is refused because 88\,km exceeds the allowance", CLASSIF)
L.allow(SI, r"already has 100\,km or more of road (35\,\%)", CLASSIF)
L.allow(SI, "summed over the 43 weeks of the 2026 run", "design: the horizon of the 2026 run (23 profile weeks and 20 recovery weeks)")
L.allow(SI, "stays flat at the 2026 season's mean (0.40) for the twenty-three weeks", "design: the flat profile of the wave experiment (scenarios, wave_*_flat): the mean loading share of the 23 profile weeks")
L.allow(SI, "The table covers the 23 weeks of the profile", "count: the profile weeks of scenarios/2026.csv, the rows of Table S-gate")
L.allow(SI, "on top of a rail ceiling of 50 kt a week", "design: the rail ceiling of the crossed runs (jobs_20261102_cross.txt)")
L.allow(SI, "under a rail ceiling of 50 kt a week", "design: the rail ceiling of the crossed runs (jobs_20261102_cross.txt)")
L.allow(SI, "The two waves at a 15-day refill time", "design: the refill time of the crossed wave runs (jobs_20261102_cross.txt, *_rest15)")
L.allow(SI, "with a refill time of 15 days instead of 30. At 15 days the two waves", "design: refill times of the inventory rule, 30 days in the paper and 15 in the crossed runs")
L.allow(SI, "and of their sequence with 0, 2 and 4 weeks of normal water between them, at the refill time of 30 days of the paper and at 15 days",
        "design: the gaps of the wave-isolation profiles and the two refill times")

# ---------------------------------------------------------------- S5 What crosses Kaub
L.allow(SI, r"costs more than 1\,\% above its baseline price", "design: the 1 % threshold of the share PriceShareEconomy (the macro)")

# ---------------------------------------------------------------- S6 Two representations (merged into the section on the 2018 event)
L.allow(SI, "Choice 1: how low water limits transport", "count: the numbering of the choice")
L.allow(SI, "Two representations of the river were compared on the 2018 event", "count: the two representations of the paragraph")
L.allow(SI, "the capacity limit at five inventory levels; the floor representation at three", "count: the model rows of Table S-representations (five and three)")

# ---------------------------------------------------------------- S7 Sensitivity analysis
L.allow(SI, "A ceiling of 50 kt a week is reached in nearly every profile week of both events",
        "design and result: the rail ceiling of 50 kt a week; it binds in 23 of 23 profile weeks of 2026 and 21 of 22 of 2018 (Table S-railweeks, si_tables.rail_weeks_table)")
L.drop("at half and twice its value, moves it by")
L.allow(SI, r"The loading share below 5\,cm, at half and twice its value, moves it by", "design: the loading share below 5 cm at 0.04 and 0.16 instead of 0.08 (runs floor04, floor16)")
L.allow(SI, "At 45 days the services' share of the German loss is", "design: the 45-day coping duration of the run serv45")
L.claim(SI, "the loss of the 28 economies and the consumption loss of each", "NRegions", [28, 28], "data bound to the macro: the 28 economies of the model")

# ---------------------------------------------------------------- S8 Rail
L.allow(SI, r"a shipment whose normal route already has a leg of 100\,km or more by rail may be rerouted entirely by rail, at no penalty. About 15\,\% of the bulk orders that cross Kaub have such a route",
        "design: the line-haul threshold of 100 km (run_rhine.py); data: 15 % of the Kaub-crossing bulk orders in the offline classification (si_tables.thresholds_table)")
L.allow(SI, r"so we test the 100\,km threshold", "design: the line-haul threshold of the modal-switch rule")
L.allow(SI, r"Raising the threshold from 100 to 500\,km leaves no bulk shipment a rail alternative", "design: the no-rail runs (--line-haul-km 500; jobs_20261102_norail.txt)")
L.allow(SI, "A ceiling of 50 kt approximates the 400 wagons that the national rail freight operator said it could add at short notice in August 2026, at two rotations a week and 62.5 t per wagon",
        "evidence: dbcargo2026 (about 400 wagons at short notice); design: two rotations a week and 62.5 t per wagon give 50 kt a week")
L.allow(SI, "A higher ceiling of 140 kt follows the response of rail freight to past low waters", "design: the second rail ceiling (jobs_20261102_rev.txt, rail140)")
L.allow(SI, r"that a day of low water raises rail tonnage by 0.07\,\%, that is about 2\,\% over a low-water month of 30 days. Applied to about 6.7 Mt of rail freight a week, the order of the German total (362 Mt in 2024, or 7.0 Mt a week",
        "evidence: Kiel Working Paper 2155, Appendix B, Table B1 (+0.071 % of rail tonnage per low-water day, monthly data 2005-2019); Destatis, rail freight 362.3 Mt in 2024 (destatis2026gueterbefoerderung); 6.7 Mt a week is the base of the 140 kt ceiling (0.0007 x 30 x 6.7 Mt = 141 kt), see evidence/si_evidence_sea_vot_rail_20261110.md")
L.allow(SI, "this gives about 140 kt a week", "design: the second rail ceiling")
L.allow(SI, "so 140 kt for bulk alone is likely more than rail can take on", "design: the second rail ceiling")
L.allow(SI, "The 50 kt ceiling binds (the placed tonnage reaches the ceiling) in 23 of the 23 profile weeks of 2026 and 21 of the 22 of 2018, and in 3 and 0 of the recovery weeks in which bulk is still cut; the 140 kt ceiling in 20 and 17 profile weeks and 0 and 0 recovery weeks",
        "result: counts computed by si_tables.rail_weeks_table from the logs of the four rail runs of the batch of 2 November 2026 (the caption of Table S-railweeks as generated on 3 November)")

# ---------------------------------------------------------------- S9 The 2018 event (and the two paragraphs moved to S7)
L.drop("Choice 1: how low water limits transport")
ADEMMER = "evidence: ademmer2023, Table 2, column 1 (the regression of monthly growth of industrial production on the change in low-water days; benchmark_ademmer.py)"
L.allow(SI, r"(column~1 of their Table~2)", ADEMMER)
L.allow(SI, r"on which the Kaub gauge is below 78\,cm", ADEMMER + "; 78 cm is the equivalent low water level of the Kaub gauge")
L.allow(SI, r"y_t = a + \beta_0\,\Delta d_t + \beta_1\,\Delta d_{t-1} + \rho\,y_{t-1} + \text{controls} + \varepsilon_t", "convention: indices of the equation")
L.allow(SI, r"with $\beta_0=-0.034$ (standard error 0.012), $\beta_1=-0.024$ (0.014) and $\rho=-0.172$ (0.119)", ADEMMER)
L.allow(SI, r"$g_t=\beta_0\,\Delta d_t+\beta_1\,\Delta d_{t-1}+\rho\,g_{t-1}$", "convention: indices of the equation")
L.allow(SI, r"29, 14, 31, 30 and 3 days below 78\,cm from August to December 2018", "data: days below 78 cm in the daily record of the Kaub gauge, August to December 2018 (scenarios/kaub_daily_2018.csv; benchmark_ademmer.py)")
L.allow(SI, "Every inventory target was multiplied by 0.75, 1.25, 1.5 and 2", "design: the inventory levels of the 2018 runs (jobs_20261102_ladder.txt, jobs_20261106_inv075.txt)")
L.claim(SI, "At three quarters of the balance-sheet values the industrial shortfall is nearer the benchmark's",
        "min(abs(RecordInt-ModelInt), abs(RecordInt-LadderIntA), abs(RecordInt-LadderIntB), abs(RecordInt-LadderIntD)) - abs(RecordInt-LadderIntZ)", [0.01, 100],
        "result: the level x0.75 (3.2 percent-months) is nearer the benchmark (5.3) than the four others")
L.claim(SI, "but still below its one-standard-deviation band. The balance-sheet values are kept", "RecordIntLow - LadderIntZ", [0.01, 100],
        "result: 3.2 percent-months at x0.75 is below the lower edge of the band (3.6)")

# ---------------------------------------------------------------- reworded claims carried over; the renumbered pointer of main.tex
L.claim(SI, "Road is below the statistics in Germany, the Netherlands, Belgium, France and Austria",
        "max(ModalDERoad-73, ModalNLRoad-53, ModalBERoad-78, ModalFRRoad-89, ModalATRoad-69)", [-100, -1],
        "result: the model's road share below Eurostat's in each of the five (gaps 8-15 points, the smallest France 81 against 89)")
L.claim(SI, "Under the ceiling each lever removes a larger share of a smaller loss than under the paper's rule",
        "min(CrossStockRail - LevStock, CrossDeepRail - LevDeep, CrossStockTRail - LevStockT, CrossFleetRail - LevFleet)", [1, 100],
        "result: every single lever avoids a larger share of the rail-50 base than of the reference base")
L.allow(MAIN, r"two stress paths (Supplementary Section~S7), not bounds", "design: the two quantile paths (q25, q75)")

# ---------------------------------------------------------------- the entries of sentences that left the text (end of the revision)
from si_patchlib import OVERLEAF  # noqa: E402
dead = L.drop_missing(OVERLEAF)
# the list of what was dropped is review/ledger_dropped_20261110.txt (written once, from git, at the end of the revision)
print(f"{len(dead)} dead entries dropped")

L.save()
