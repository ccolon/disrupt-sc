r"""The evidence cells of Tables S1, S2, S3 and S7 of the SI in plain sentences (13 November 2026, the author's request:
"very compact ... the goal is not that readers understand exactly how we extracted the information, but rather get a
sense of the evidence"). si_tables.py prints these texts; the numbers of the value columns still come from the
configuration of the runs.

Rules of the rewriting: full sentences that start with how the value was obtained; two or three figures per cell (the
one that supports the value, and one that shows agreement or disagreement); no abbreviation that needs a footnote; the
unit once, in the heading or the notes. Every statement is taken from the detailed version of the tables, which stays
in evidence/si_tables_detailed_20261112.tex (the four tables as they were on 12 November 2026), in
evidence/inventory_durations_by_industry.md and in scenarios/draught_table_ledger.csv.

LaTeX strings: they are written into the tables as they are (no escaping).
"""

# 13 Nov 2026 (the author's choice): each caption tells the reader where the figures and sources that left the cells are
DETAIL = "The detailed evidence, with every figure and source, is in the data deposit (Data availability of the main text)."

# ------------------------------------------------------------------------------------------------ Table S1: transport costs
RATES_CAPTION = (r"\textbf{Transport cost parameters:} the baseline values and the evidence behind them. Most of the evidence comes "
                 r"from the operator costs compiled for the Netherlands Institute for Transport Policy Analysis (KiM)~\citep{kim2023}, "
                 r"from quoted and published freight rates of the Rhine trades, and from the Eurostat modal split~\citep{eurostat2023modal}, "
                 r"on which the road and rail values are calibrated (Section~S2). " + DETAIL + " Notes follow the table.")

RATES_TEXT = {
    "road": (r"Calibrated so that the model reproduces each country's split of freight between modes~\citep{eurostat2023modal}. No series "
             r"of road rates was collected. The value stands for a full truck on a long haul; averaged over all trips, empty ones included, "
             r"a truck costs its operator 0.115 EUR~\citep{kim2023}."),
    "road_liquid": (r"No rate evidence was collected. Set together with the rail value so that the model reproduces the German split of "
                    r"liquid bulk between modes (Section~S2)."),
    "rail": (r"Calibrated so that the model reproduces each country's split of freight between modes~\citep{eurostat2023modal}. Published "
             r"costs and revenues of rail freight range from 0.014 to 0.047 EUR~\citep{kim2023,irgrail2026mm14}. The value is 20\,\% higher "
             r"in <<n_countries>> countries where the model otherwise put too much freight on rail (Section~S2)."),
    "rail_liquid": (r"Set with the road value so that the model reproduces the German split of liquid bulk between modes (Section~S2). It is "
                    r"a calibrated value, well above the 0.018 EUR that a train of liquid bulk costs its operator~\citep{kim2023}."),
    "water_dry": (r"A pushed convoy of barges costs its operator 0.008 to 0.012 EUR~\citep{kim2023}, and a published rate for coal from "
                  r"Rotterdam to Basel works out at 0.013~\citep{infras2017}. Single vessels cost more, 0.018 to 0.036~\citep{kim2023}, so "
                  r"cargo that travels in single vessels, such as grain, is under-priced in the model. The Rhine value also holds on "
                  r"<<n_waterways>> other waterways$^{b}$; elsewhere the value is up to <<times>> times higher (Section~S2)."),
    "water_liquid": (r"Quoted tanker rates from the seaports to Cologne, Karlsruhe and Basel between 2022 and 2025 work out at 0.03 to 0.05 "
                     r"EUR~\citep{opis2025riverlake,handelsblatt2022rhine,ccnr2024price}. The operator's own cost is about "
                     r"0.03~\citep{kim2023}."),
    "water_container": (r"A container vessel costs its operator 0.025 EUR~\citep{kim2023}. Published tariffs on the Rhine are 125 to 178 EUR "
                        r"per twenty-foot container~\citep{infras2017,konings2009}, about 12 to 18 EUR per tonne. In the model, "
                        r"\KaubContMt~Mt of containers a year pass Kaub, against about 10 in the counts (Section~S2)."),
    "sea": (r"What a container ship costs its operator on ocean routes, 0.0014 EUR~\citep{kim2023}. Bulk carriers and tankers cost two to "
            r"three times more (0.0034 and 0.0051), so the sea leg of bulk is under-priced; a run at these two rates changes the 2026 loss "
            r"by \RevSeaRateRelOne\,\% (Section~S8). Sea lanes have no capacity limit, and the rate matters only for the port at which "
            r"imports land (Section~S2)."),
    "vot_container": (r"The road and sea values are close to those of a review of freight studies for shippers in Germany (1.59 and "
                      r"0.19)~\citep{binsuwadan2022vfts}. The rail and waterway values are three to four times higher than in that review "
                      r"(0.27 and 0.09). The waterway value was calibrated on the container tonnage of the Rhine (Section~S2); it is of "
                      r"the order of what an hour of a vessel costs per tonne carried (0.13 to 0.26 EUR)~\citep{kim2023,ecorys2005}."),
    "vot_bulk": (r"No value by type of cargo was found. The same review gives 0.09 for shippers on inland waterways, all "
                 r"cargo~\citep{binsuwadan2022vfts}; the cargo itself accounts for about a fifth of the value of time of a "
                 r"shipment~\citep{dejong2014freightvot}."),
    "transfer_road_rail": (r"A transfer at each end of a rail trip. The costs for containers and dry bulk are close to the transfer rates of "
                           r"the German federal appraisal method (2.1 and 2.6 EUR per tonne)~\citep{planco2015bvwp}; two terminal operators "
                           r"charge about 3 EUR per tonne in 2026~\citep{duss2026price,dbis2026price}. The cost for liquid bulk is a third of "
                           r"the appraisal rate. The hours are assumptions: no published figure was found."),
    "transfer_land_water": (r"The part of a barge rate that does not depend on distance: 3 to 7 EUR per tonne for tankers, from the quotes "
                            r"above, and 7 to 8 EUR per tonne for the two lifts of a container~\citep{konings2009}. The values for liquid "
                            r"bulk were set in the calibration of the German split of liquid bulk between modes."),
    "transfer_water_sea": (r"Handling in the seaport. Lifting a container costs 3.5 to 4 EUR per tonne in Rotterdam, about twice the model's "
                           r"value, and a barge spends about 8 hours between the terminals of that port~\citep{konings2009}. No published "
                           r"figure was found for bulk."),
    "transfer_land_sea": r"Handling in the seaport.",
    "port_fee": r"Added to the transfer above. The fee falls as the tonnage of the port rises (Section~S2).",
    "speed": r"Trucks on motorways; freight trains; barges on the Rhine (about 10 upstream and 15 downstream); short-sea shipping.",
}

RATES_NOTES = (r"\emph{Notes.} The model is in US dollars of 2022. The evidence is in euros, as the sources give it, in the unit of each "
               r"heading unless another is named; one euro was worth 1.05 US dollars on average in 2022~\citep{ecb2026exrusd}. Operator "
               r"costs are averages over a fleet, with empty trips and waiting, at 2021 prices~\citep{kim2023}. No public source gives a "
               r"full table of freight rates on the Rhine at normal water. $^{a}$<<countries>>. $^{b}$<<waterways>>.")

# the eight waterways that carry the Rhine's values, as the manuscript names them (the configuration names them in Dutch and German)
SAME_WATERWAYS = ("Amsterdam--Rhine canal, Ghent--Terneuzen canal, IJssel, IJsselmeer, Noordzeekanaal, Nord-Ostsee-Kanal, Scheldt and "
                  "Scheldt--Rhine link")
COUNTRY = {"AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany",
           "DK": "Denmark", "EE": "Estonia", "ES": "Spain", "FI": "Finland", "FR": "France", "GR": "Greece", "EL": "Greece", "HR": "Croatia",
           "HU": "Hungary", "IE": "Ireland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MT": "Malta",
           "NL": "the Netherlands", "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia"}
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


def word(n) -> str:
    """A small count as a word (ten countries, eight waterways), a larger one in digits."""
    return WORDS.get(int(n), str(int(n)))


# ------------------------------------------------------------------------------------------------ Table S2: inventories by industry
STOCKS_CAPTION = (r"\textbf{Inventory targets by buying industry.} Days of consumption of purchased goods inputs that each industry holds at "
                  r"the baseline. Unless a row says otherwise, the evidence is the stock of raw materials and supplies that German firms of "
                  r"the industry held in 2023, in days of their purchases of materials~\citep{bundesbank2025}; French~\citep{banquefrance2025fiben} "
                  r"and US~\citep{census2026m3} firm statistics serve as a comparison. Each value carries a grade for its evidence (author's "
                  r"judgment). Input-specific targets are given in Table~\ref{tab:stockoverrides}. " + DETAIL)

# (codes as printed, name or None for the name of the single code, codes of the configuration, grade, evidence)
STOCK_ROWS = [
    ("A01", None, ["A01"], "C",
     r"German farm accounts show 49 days, but they count growing crops and livestock, so this is an upper bound; 30 days is assumed below "
     r"it. Feed and fertilizer are stored on farms."),
    ("B05--B09", "Mining and quarrying", ["B05", "B06", "B07", "B08", "B09"], "C",
     r"No figure for raw materials alone. German accounts show 74 days with unfinished products included; French firms hold 50 days of "
     r"turnover. Partly assumed."),
    ("C10T12", None, ["C10T12"], "A", r"German food manufacturers hold 18 days. French and US data are close (15 to 18 days)."),
    ("C13T15", None, ["C13T15"], "A", r"German manufacturers hold 42 days; US data give 45 to 50."),
    ("C16", None, ["C16"], "B", r"The German group of wood, paper and printing holds 33 days; US data give 31 for wood."),
    (r"C17\_18", None, ["C17_18"], "B", r"The same German group (33 days); US data give 30 to 32."),
    ("C19", None, ["C19"], "B",
     r"German refiners hold about 10 days of crude oil of their own, EU refiners up to 19 and US refiners about 7 (official statistics). "
     r"The emergency stocks required by law are not counted (Table~\ref{tab:stockoverrides})."),
    ("C20", None, ["C20"], "A",
     r"German chemical and pharmaceutical manufacturers hold 31 days; US data give 26. Liquid feedstocks at plants on the river last less "
     r"(Table~\ref{tab:stockoverrides})."),
    ("C21", None, ["C21"], "B",
     r"No separate figure for raw materials. German accounts show 82 days with unfinished products included; the 31 days of the group of "
     r"chemicals and pharmaceuticals mostly reflect chemicals. The value lies between the two."),
    ("C22", None, ["C22"], "B", r"The German group of rubber, plastics and mineral products holds 39 days; US data give 34 for plastics."),
    ("C23", None, ["C23"], "B",
     r"The same German group (39 days); US data give 32. Cement plants hold 21 to 30 days of purchased fuels and quarry their own "
     r"minerals. The value leans towards the purchased fuels."),
    ("C24A", None, ["C24A"], "B",
     r"The German group of metals and metal products holds 36 days, as US producers of primary metals do. The Duisburg steelworks normally "
     r"hold one to two months of ore and coal (trade press)."),
    ("C24B", None, ["C24B"], "C", r"As basic iron and steel; no separate figure."),
    ("C25", None, ["C25"], "B", r"The German group of metals and metal products holds 36 days; US data give 32."),
    ("C26", None, ["C26"], "B",
     r"The German group of electronics and electrical equipment held 70 days in 2023, against 37 in 2019, before the chip shortage; US "
     r"data give 50. The value is set between the two years."),
    ("C27", None, ["C27"], "B", r"The same German group; US data give 41."),
    ("C28", None, ["C28"], "A", r"German manufacturers hold 59 days; US data give 60."),
    ("C29", None, ["C29"], "A", r"German vehicle manufacturers hold 18 days; US data give 19."),
    ("C301--C309", "Ships, boats and other transport equipment", ["C301", "C302T309"], "D",
     r"Assumed. The accounts do not separate purchased inputs from the ships and vehicles under construction."),
    ("C31T33", None, ["C31T33"], "C",
     r"US data give 40 days for furniture. German accounts show 57 days and more with unfinished products included."),
    ("D", None, ["D"], "B",
     r"A blend across fuels. German law requires reserve plants to hold 30 days of coal or 10 days of oil~\citep{ekbg2022}; one operator "
     r"reported about a week of coal on site in 2022. Gas comes by pipeline and is not stocked at plants. The targets by fuel are in "
     r"Table~\ref{tab:stockoverrides}."),
    ("E", None, ["E"], "C", r"German accounts show about 20 days of stocks of all kinds; raw materials are a small part of them."),
    ("F", None, ["F"], "A", r"German construction firms hold 9 days, a level stable since 2011; French data give 12 to 14."),
    ("G", None, ["G"], "B",
     r"German traders hold 2 days of materials. Their goods for resale, one to two months of sales, are not an input: the input--output "
     r"table records trade as a margin."),
    ("H49--H53", "Transport and storage", ["H49", "H50", "H51", "H52", "H53"], "B",
     r"German transport firms hold 7 days of fuel, tires and spare parts; French data give 3."),
    ("I", None, ["I"], "B", r"German accounts show 5 to 7 days of stocks."),
    ("J58--J63", "Publishing, telecommunications and IT services", ["J58T60", "J61", "J62_63"], "C",
     r"German firms of these industries hold 2 days of raw materials, and 18 to 28 days of stocks once unfinished work is counted. The "
     r"value lies between the two."),
    ("K, R, S, T", "Finance, arts and recreation, other services, households as employers", ["K", "R", "S", "T"], "D", r"Assumed; no data."),
    ("L", None, ["L"], "D", r"Assumed; this industry buys few goods."),
    ("M, N", "Professional, scientific and administrative services", ["M", "N"], "C",
     r"German firms of these industries hold 6 days of raw materials. Their accounts also carry much unbilled work, which is not an input."),
    ("O, P", "Public administration and education", ["O", "P"], "D",
     r"Assumed. German accounts for education and health together show 9 to 28 days of stocks."),
    ("Q", None, ["Q"], "C", r"German accounts for health care show 13 to 40 days of stocks, mostly drugs and consumables."),
]

STOCKS_NOTES = (r"\emph{Notes.} $^{a}$Grade of the evidence: A, balance-sheet data for the industry itself; B, data for a group of "
                r"industries, or physical stock data; C, indirect evidence; D, assumed. German accounts: the statistics that the Bundesbank "
                r"draws from the annual accounts of firms~\citep{bundesbank2025}. Where they do not report raw materials separately, they "
                r"give stocks that include unfinished products, an upper bound for purchased inputs. French data: median stocks, in days "
                r"of turnover~\citep{banquefrance2025fiben}. US data: stocks of materials and supplies, in days of the cost of "
                r"materials~\citep{census2026m3}. The German statistics for 2019 give lower values in every industry where both years are "
                r"reported, by up to a fifth in most and by a quarter to a half in machinery, motor vehicles and electronics.")

# ------------------------------------------------------------------------------------------------ Table S3: inventories by input
# (buyer code, input code, 'buyer: input' label, grade, evidence and modeling reason); the order and the keys are those of the configuration
OVERRIDES = [
    ("*", "D", "any buyer: electricity, gas and steam (D), water (E)", "B",
     r"Users cannot store these inputs for more than a few days. In reality, the grid replaces a plant that reduces output. The model has no "
     r"such substitution, and a buffer of two days would spread any plant stoppage to the whole economy. The input is therefore given the "
     r"90 days of coping time of the services. This is a limitation of the model."),
    ("D", "B05", "power plants: coal", "B",
     r"German law requires reserve plants to hold 30 days of coal~\citep{ekbg2022}. One operator reported about a week of coal on site in "
     r"2022, and 30 days with its stocks in the port of Rotterdam."),
    ("D", "B06", "power plants: gas", "B",
     r"Gas comes by pipeline, outside the transport network of the model. The 90 days stand for the storage of the gas system, not for a "
     r"stock at the plant."),
    ("D", "C19", "power plants: fuel oil", "B", r"The same law requires 10 days at oil-fired plants."),
    ("C19", "B06", "refineries: crude oil", "B",
     r"Crude oil reaches the refineries by pipeline, so the river does not interrupt it. The 90 days are the emergency stocks that EU law "
     r"requires~\citep{council2009oilstocks}; refiners themselves hold 10 to 12 days. Crude never stops a refinery in the runs: refineries "
     r"matter through the refined products that they cannot deliver."),
    ("C24A", "B07", "steelworks: iron ore", "B",
     r"The Duisburg steelworks normally hold one to two months of ore and coal (trade press, August 2026)."),
    ("C24A", "B05", "steelworks: coking coal", "B", r"As iron ore."),
    ("C20", "C19", "chemical plants: liquid feedstocks (naphtha, LPG)", "C",
     r"No published figure. The value is inferred from how soon chemical plants warned of force majeure in July 2026~\citep{icis2026}; the "
     r"industry holds 30 days of inputs on average."),
    ("C20", "B06", "chemical plants: gas and condensate", "C", r"As the liquid feedstocks."),
    ("C10T12", "A01", "mills: grain and oilseeds", "B",
     r"Flour mills can store the grain of two weeks of production (millers' association) and oil mills that of 5 to 10 days; feed plants "
     r"receive their grain as they use it. The grain is stored upstream, on farms and by traders."),
    ("C23", "B05", "cement plants: coal", "C",
     r"Cement plants hold 21 to 30 days of purchased fuels, according to equipment suppliers and engineering sources."),
    ("C23", "C19", "cement plants: petroleum coke", "C", r"As coal."),
    ("H49", "C19", "haulers: fuel", "B", r"German transport firms hold 7 days of fuel, tires and spare parts~\citep{bundesbank2025}."),
]
OVERRIDES_SERVICES = (r"These inputs cannot be stored. The buyer manages without them for {days} days, the coping duration of the model "
                      r"(Methods).")
OVERRIDES_CAPTION = (r"\textbf{Input-specific inventory targets.} Targets that replace the industry value of Table~\ref{tab:stocks} for one "
                     r"input, with the evidence and, where the model departs from the physical figure, the modeling reason. Grades as in "
                     r"Table~\ref{tab:stocks}. " + DETAIL)

# ------------------------------------------------------------------------------------------------ Table S7: the loading curve
LOADING_CAPTION = (r"\textbf{The loading curve at Kaub.} Share of the normal tonnage that the Kaub reach can pass at a weekly mean gauge, "
                   r"with the evidence for each value and how the value is set. " + DETAIL)

# gauge (cm) -> (evidence, how the value is set)
LOADING_TEXT = {
    5: (r"No tonnage was counted at this gauge. The gauge stood at 5 to 6\,cm in mid-August 2026~\citep{pegelonline2026}, when the press "
        r"reported that shipping past Kaub had stopped; nine tankers built for low water were in service~\citep{wiwo2026}.",
        r"Assumed: the low-water tankers and small dry-cargo vessels still sail. The count at about 12\,cm (0.22, two rows below) is an upper "
        r"bound. The value is kept below 5\,cm and tested at 0.04 and 0.16 (Section~S8)."),
    10: (r"No measurement at this gauge.", r"On the line between the value at 5\,cm and the count at about 12\,cm."),
    15: (r"The only count of tonnage. The Dutch inland navigation association reported that its members moved 90\,kt past the Middle Rhine in "
         r"a week of August 2026, against 400\,kt in a normal week~\citep{schuttevaer2026}. The gauge fell from 23 to 6\,cm during that week.",
         r"The count gives 0.22 at a mean gauge of about 12\,cm; the curve takes 0.24 at 15\,cm."),
    25: (r"At 23 to 30\,cm, a tanker loads about 15\,\% of its capacity, whether standard or built for low water (trade press, August "
         r"2026)~\citep{wiwo2026}.",
         r"Assuming that nearly twice as many vessels sail for the same cargo, 0.28 of the normal tonnage passes."),
    30: (r"At about 30\,cm, vessels load 10 to 15\,\% of their capacity~\citep{ifw2026}. At the 2018 record of 25\,cm, only the smaller "
         r"classes of vessels still sailed~\citep{vandorsser2020}.",
         r"Assuming that two to two and a half times as many vessels sail, 0.30 of the normal tonnage passes."),
    40: (r"At 40 to 50\,cm, a standard vessel carries about 20\,\% of its capacity (rule of the waterway administration). A container "
         r"operator states that large container vessels can practically no longer sail at 40\,cm~\citep{contargo2026}.",
         r"Assuming that 1.65 times as many vessels sail, 0.33 of the normal tonnage passes."),
    55: (r"At 55\,cm, a large container vessel loads 16\,\% of its capacity~\citep{contargo2026}. The trade press reports twice as many "
         r"vessels for the same cargo at moderate low water.",
         r"Assuming that two and a half times as many vessels sail, 0.40 of the normal tonnage passes."),
    78: (r"Two indications of different kinds. A container operator loads 25\,\% per vessel at this gauge and sails four times as many "
         r"ships. Across Germany, a month of low water lowers the tonnage carried by inland waterways by about 25\,\%~\citep{ademmer2023}.",
         r"Assumed: 0.60, between the two. Neither measures the share that passes Kaub at 78\,cm."),
    100: (r"A container line charges a low-water surcharge below 91\,cm.", r"Assumed: a mild restriction, 0.80."),
    120: (r"Normal loading was reported at 120 to 125\,cm in late April 2026 (press).", r"Assumed: nearly normal loading, 0.90."),
    150: (r"A standard vessel needs about 150\,cm at Kaub to load fully (Kiel Institute).", r"Full loading from 150\,cm."),
    250: (r"The largest vessels load fully at 250\,cm (container operator, 2017).", r"Full loading."),
}
