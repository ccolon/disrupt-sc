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

L.save()
