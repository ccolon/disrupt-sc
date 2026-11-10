# SI evidence: sea freight rate, cargo value of time, German rail tonnage (10 Nov 2026)

Scope: the three unsourced numbers in the rates table of si.tex (lines 31, 35, and the 6.7 Mt a week behind the rail ceiling of 140 kt).
Every source below was opened on 10 Nov 2026 unless marked "not verified". Conversions are shown; assumptions are marked "assumption".
Inland waterway rates are not repeated (see waterway_rates_by_vessel_type.md).

## Q1. Sea transport cost per tonne-kilometer (model: 0.0015 USD/tkm, all cargo classes)

| Source | Figure | Unit | Year / price level | Where | Verified |
|---|---|---|---|---|---|
| Panteia for KiM, Cost figures for freight transport (2023) | bulk carrier 0.0034; tanker 0.0051; container carrier 0.0014 (total costs per tonne-km) | EUR per tkm | 2021 | Table 5.5, report p. 47 | yes (table read from the rendered page) |
| same | bulk carrier 0.055; tanker 0.099; container carrier 0.027 (total costs per tonne per hour, vessel side) | EUR per tonne-hour | 2021 | Table 5.5, p. 47 | yes |
| same, routes behind the figures | bulker Ponta da Madeira (BR) - Rotterdam 7,608 km; tanker Congo - Rotterdam 8,873 km; container carrier Baltimore - New York - Rotterdam - Hamburg - Gdansk - Antwerp - Baltimore 16,996 km | km | 2021 | Table 5.2, p. 42 | yes |
| same, scope | "Because we use averages from UNCTAD database, the analysis ... includes both deep-sea and short-sea itineraries and ships" | text | - | section 5.1, p. 40 | yes |

Where 0.0015 sits (EUR and USD treated as equal, as the SI does): inside the KiM figure for container carriers (0.0014, +7 %), below the bulk carrier (0.0034; the model is 2.3 times lower) and far below the tanker (0.0051; 3.4 times lower). KiM orders the cargo classes container < dry bulk < liquid bulk per tkm; the model uses one value for all three. The KiM routes are mainly deep-sea or transatlantic; KiM gives no separate short-sea figure. A short-sea leg of a few hundred km carries fixed port and waiting costs that make its per-tkm cost higher than these long-haul averages (inference; the model charges port handling separately as terminal transfer plus seaport fee, which partly covers this).

Searched and not usable (opened, no per-tkm sea cost in them): TOI "Cost models for transport and logistics, base year 2023" (English summary lists ship types, no per-tkm figure); World Bank PRWP 9992 "Fathoming Shipping Costs" (freight-rate ratios only: per-kilo dry bulk up to 10 times lower than containerized, Stylized Fact 15); Ramalho and Santos 2021 (J. Mar. Sci. Eng. 9, 959; external costs, no internal per-tkm cost); Notteboom 2020 (Ro-Ro vs trucking, absolute costs only in images). A trade-press quote exists (Tubarao-Qingdao iron ore 30.55 USD per tonne on 27 March 2026, Kallanish via GMK Center, 29 Mar 2026) but I found no reliable distance for the same port pair (the one distance found, Ponta da Madeira-Qingdao 14,800 nm, FreightWaves 2019, is for another port), so no per-tkm figure follows: not used.

Conclusion for the SI: "KiM/Panteia operator costs for seagoing ships (2021 prices) are 0.0014 EUR per tonne-kilometer for container carriers, 0.0034 for bulk carriers and 0.0051 for tankers on deep-sea and transatlantic itineraries (Panteia for KiM 2023, Table 5.5), so the model's 0.0015 matches containers and is two to three times lower for bulk. Sea legs carry no capacity constraint in this study and the value is below the road, rail and waterway rates by an order of magnitude, as in the literature."
(The last clause on "no influence on results" is the author's own statement in the table; I did not test it.)

## Q2. Value of time of cargo, per tonne-hour (model: bulk 0.08 all modes; containers 1.00 road and rail, 0.32 waterway, 0.15 sea)

| Source | Figure | Unit | Year / price level | Where | Verified |
|---|---|---|---|---|---|
| Binsuwadan, de Jong, Batley, Wheat (Transportation 2022), meta-analysis, 106 values from 56 studies | Germany, shippers (cargo side), all commodities: road 1.59; rail 0.27; air 23.01; sea 0.19; inland waterway 0.09 | USD per tonne-hour | 2017 incomes and prices | Table 7, p. 1199 (rendered page read) | yes |
| same | Germany, carriers (vehicle side): road 10.44; rail 1.78; sea 1.24; inland 0.59 | USD per tonne-hour | 2017 | Table 7, p. 1199 | yes |
| same | sample of 106 values: median 1.14, mean 7.29 USD per tonne-hour, minimum 0.00018, maximum 351 | USD per tonne-hour | 2017 | Table 1, p. 1189 | yes |
| de Jong et al. (TR-E 64, 2014), Dutch SP study of 812 interviews | VOT = transport cost component (about 80 % on average) + cargo component (about 20 % on average); road about 5 and rail about 1.2 "euro per tonne" (as printed; unit presumably per tonne-hour, not checkable in the accepted manuscript) | share; EUR | price level 2010 | section 5.1 (accepted manuscript) | yes |
| same | on cargo: "For most commodities however, deterioration, interest and safety stocks will be very limited"; for rail, waterway and sea "the cargo component in the VOT will be relatively small" | text | - | section 5.2 | yes |
| same | Table 5 gives values per vehicle or vessel, not per tonne (road 2-40 t truck all cargo 38 EUR/h; sea ship waiting at quay 820 EUR/h; full train 1,100 EUR/h) | EUR per hour | 2010 | Table 5 | yes; not convertible without payloads |
| Arup/Significance for National Highways (2023), Freight VoT and VoR, literature review | Norway 2018 study (Halse et al. 2019): "13 NOK/tonne-hour (cargo component only)", all modes; "from 2 (timber) to 194 (fresh fish) NOK/tonne-hour". Typical split of studies: 85 % carrier, 15 % cargo | NOK per tonne-hour | 2018 | p. 52-53 | yes (secondary: Halse et al. 2019 itself not opened) |
| Panteia for KiM (2023) | vessel-side time cost at sea: bulk carrier 0.055, tanker 0.099, container carrier 0.027 | EUR per tonne-hour | 2021 | Table 5.5, p. 47 | yes |

Conversions. NOK to USD: assumption of 0.10-0.11 USD per NOK (2018-19; not from the sources), so 13 NOK is about 1.3-1.4 USD and 2 NOK (timber) about 0.2 USD per tonne-hour. Binsuwadan figures are all-commodity averages: the paper excluded studies reporting only specific commodities (p. 1188-89), so no bulk-specific value is available there.

Where the model sits.
- Containers on road, 1.00: below the German shipper-side road value (1.59, all commodities) and the Norwegian cargo average (about 1.3). Same order of magnitude.
- Containers on rail, 1.00: about 4 times above the German shipper-side rail value (0.27). The model gives road and rail the same value; the literature gives rail about one sixth of road.
- Containers on waterways, 0.32: about 3.5 times above the shipper-side inland value (0.09), but equal to the carrier-side rail value order; the model's 0.32 is above all cargo-side evidence found.
- Containers at sea, 0.15: close to the shipper-side sea value (0.19).
- Bulk, 0.08: the literature has no bulk-specific per-tonne-hour figure I could open. It is 2.5 times below the Norwegian timber value (about 0.2) and of the same size as the all-commodity shipper values for waterway (0.09) and sea (0.19). It is also in the middle of the vessel-side sea cost per tonne-hour for bulk carriers and tankers (0.055-0.099, KiM), so the number resembles a vessel-side cost more than a cargo-side one (inference).
- Direction of de Jong et al.: the cargo component is about 15-20 % of the total VOT, and most of the Dutch VOT is the carrier's cost. The SI table currently cites vessel-side costs (0.02-0.07 and 0.13-0.26 EUR per tonne-hour, Panteia) to support a cargo-side value; that is the wrong side of the split and should be reworded.

Interest derivation (cargo value times annual capital cost over 8,760 h). Formula: VOT = V x r / 8,760, V = value in USD per tonne, r = annual cost of capital. Assumption r = 8 % per year: V = 100 USD/t gives 0.0009; V = 1,000 gives 0.009 USD per tonne-hour. To reach 0.08 the cargo must be worth about 8,800 USD per tonne; to reach 1.00, about 110,000 USD per tonne. I did not find a source for typical bulk and container cargo values per tonne that I opened, so no cargo values are cited. The pure capital-cost derivation therefore gives values one to two orders of magnitude below the model for bulk (coal, ore, grain, fuel). De Jong et al. say the same in words (deterioration, interest and safety stock are small for most commodities). The model's 0.08 and 1.00 can only be defended as including reliability, safety-stock and deterioration costs, or as calibrated values, not as capital cost.

Conclusion for the SI: "Cargo-side values of time in the literature are far below the vehicle's own time cost: in the Dutch stated-preference study the cargo component is about one fifth of the value of time (de Jong et al. 2014), and the meta-analysis of Binsuwadan et al. (2022) gives, for Germany and all commodities, 1.59, 0.27, 0.19 and 0.09 USD per tonne-hour for shippers on road, rail, sea and inland waterway (2017 prices). Our 1.00 for containers on road, 0.15 at sea and 0.08 for bulk are within an order of magnitude of these, while 1.00 on rail and 0.32 on waterways are three to four times higher, and we found no commodity-specific bulk value."

## Q3. German rail freight tonnage

(a) Destatis, goods carried by rail (Eisenbahnverkehr), Beförderungsmenge in 1,000 tonnes. 2017-2024 from the Destatis table "Beförderungsmenge und Beförderungsleistung nach Verkehrsträgern" (Stand 20 April 2026; footnote: from 2016 Jahreserhebung der Schienen-Güterverkehrsstatistik, Vollerhebung). 2025 is "..." ("Angabe fällt später an") on that page. The DBnomics mirror of Destatis table 46132-BJ001, updated 15 Oct 2026 and read through its API, reproduces 2017-2024 exactly and adds 2025.

| Year | Mt per year | Mt per week (/52) | Source |
|---|---|---|---|
| 2017 | 400.2 | 7.70 | Destatis table; DBnomics |
| 2018 | 402.3 | 7.74 | same |
| 2019 | 390.8 | 7.51 | same |
| 2020 | 358.8 | 6.90 | same |
| 2021 | 387.7 | 7.46 | same |
| 2022 | 386.2 | 7.43 | same |
| 2023 | 366.9 | 7.06 | same |
| 2024 | 362.3 | 6.97 | same |
| 2025 | 350.9 (350,869,206 t) | 6.75 (6.73 on 52.14 weeks) | DBnomics only (Destatis page not yet updated; no Destatis press release found: not verified at the Destatis source) |

6.7 Mt a week x 52 = 348.4 Mt a year. It corresponds to no year from 2017 to 2024 (those give 6.9-7.7 Mt a week); it is within 1 % of 2025 (350.9 Mt, 6.73-6.75 a week), the latest year. So 6.7 Mt is consistent with the 2025 annual total, but I cannot prove that was how it was derived. Using 2024 (362.3 Mt, 6.97 a week) the ceiling would be 0.0007 x 30 x 6.97 = 146 kt instead of 141 kt. A trade-press note (IHK Ostwestfalen on BALM, volume -2.8 % in 2025; logistik-heute, VDV 133.9 billion tkm) appeared in search results but was not opened: not verified. Transport performance in the mirror: 127.5 billion tkm in 2025, 133.3 in 2024 (differs from the VDV preliminary 133.9 for 2025; not reconciled).

(b) Ademmer, Jannsen and Mösle, Kiel Working Paper 2155 (April 2020), Appendix B, pp. 14-15, Table B1 (opened; the German Economic Review 24(2) version is paywalled: not verified, the published Appendix may differ).
- Dependent variable: growth in the volume of goods transported by rail, in tonnes (monthly, rate of growth; the main text takes volumes from the Federal Statistical Office). The appendix does not name the rail table or say whether the series is seasonally adjusted; the paper does not describe the rail series beyond "volume of goods transported by road and rail" and "due to data availability reasons, the regressions are based on a sample period that starts in 1997 and 2005, respectively".
- Sample: rail 2005-2019 (171 observations, adj. R2 0.269 in column 4; 0.244 for the lagged global-trade term is a coefficient, not R2); road 1997-2019 (262 observations).
- Estimate: days of low water at Kaub (gauge below 78 cm), rail: 0.071 (s.e. 0.029, significant at 5 %) in column (3); 0.067 (0.030) in column (4), which adds growth in global trade; the lag t-1 is -0.007 (0.082), not significant. Road: 0.081 (0.066) and 0.073 (0.053), not significant. Text: "one additional day of low water causes rail transportation to increase only by about 0.07 percent."
- The authors add: "Given that the overall volume of goods transported by rail is only slightly higher than the volume of goods transported on inland waterways, this small increase can therefore barely compensate for the decline in inland water transportation." Their conclusion (p. 8): no evidence for a considerable shift to road and rail in the short run.
- Reading for the SI: the coefficient is a response of monthly growth to a count of low-water days in the same month, estimated on 2005-2019 volumes of about 360-400 Mt a year. Scaling it by 30 days gives +2.1 % of a month's rail tonnage; applying it to the 2025 weekly tonnage is a reasonable choice, with the caveat that rail was about 15 % larger in 2017-2018.

Conclusion for the SI: "Rail freight in Germany carried 350.9 Mt in 2025 (6.7 Mt a week; Destatis, Eisenbahnverkehr, Beförderungsmenge) and 362 Mt in 2024. Ademmer et al. (2023, Appendix B) estimate that each day of low water at Kaub raises the monthly growth of rail tonnage by 0.07 % (2005-2019, 171 monthly observations, significant at 5 %), which gives 0.0007 x 30 x 6.7 Mt = 141 kt a week."

## Q4. Rail freight cost or revenue per tonne-kilometer in Europe (model: 0.032 USD/tkm containers and dry bulk, 0.038 in ten countries; SI says "within the range of block-train and intermodal rates in Europe (0.02-0.04)")

| Source | Figure | Unit | Year / price level | Where | Verified |
|---|---|---|---|---|---|
| Panteia for KiM (2023), operator costs, Dutch network, charter (block) train, dry bulk | 0.014 | EUR per tkm | 2021 | Table 6.2, report p. 55 (rendered page read) | yes |
| same, charter train, liquid bulk | 0.018 | EUR per tkm | 2021 | Table 6.2, p. 55 | yes |
| same, shuttle train, containers (intermodal) | 0.045 | EUR per tkm | 2021 | Table 6.2, p. 55 | yes |
| same, wagonload train, break bulk | 0.047 | EUR per tkm | 2021 | Table 6.2, p. 55 | yes |
| IRG-Rail, 14th Annual Market Monitoring Report (March 2026): revenue of railway undertakings per net tonne-km, all freight, 22 countries | 3.61 (2019), 3.53 (2020), 3.58 (2021), 3.99 (2022), 4.55 (2023), 4.71 (2024) | Eurocent per net tkm | current prices of each year | Figure 18, PDF p. 16 (the page footer reads "13th", a template slip in the report) | yes |
| same, text | revenue per tonne-km +3 % in 2024; "price levels have gone up by more than 20% over the 2020-2024 period" | text | - | p. 16 | yes |

Reading. KiM costs are operator costs (including net track access) for Dutch trains at fleet averages, so they exclude the shipper's terminal, drayage and margin; the IRG-Rail figure is average revenue over all freight (bulk, wagonload and intermodal) and operators, not a block-train or intermodal rate. Neither source is a quoted block-train or intermodal tariff.
- Containers and intermodal: KiM shuttle 0.045 EUR per tkm is above the SI's 0.02-0.04 range and above the model's 0.032 (the model is 29 % lower).
- Dry bulk, block (charter) train: KiM 0.014 is below the range and 2.3 times below the model's 0.032 (2.7 times below 0.038).
- Liquid bulk, charter train: KiM 0.018; the model's 0.085 (0.100) is 4.7 times higher; the SI says it is set by calibration on the German liquid-bulk split.
- Average revenue: 0.036 EUR in 2019-2021, 0.040 in 2022, 0.046-0.047 in 2023-2024 across 22 countries; inside 0.02-0.04 until 2022 and above it since 2023.
- Verdict on "0.02-0.04": not supported as a sourced range. The two sources I opened bracket it from both sides by cargo class (0.014 dry-bulk block train below, 0.045 container shuttle above) and recent average revenue is at or above its top. It is too narrow if it is meant to cover both bulk block trains and intermodal; as a single value for the model's container and dry-bulk rail rate, 0.032 sits between the two KiM figures and just below the 2019-2022 average revenue (0.036-0.040). I found no source that states 0.02-0.04 itself.
- A UIC report (2022 Report on Combined Transport in Europe, Jan 2023) was returned by search as quoting the KiM total rail cost of 0.017 EUR per tkm; not opened, not verified.

Conclusion for the SI: "Dutch operator costs for freight trains in 2021 are 0.014 EUR per tonne-kilometer for charter (block) trains with dry bulk, 0.018 with liquid bulk and 0.045 for container shuttles (Panteia for KiM 2023, Table 6.2), and the average freight revenue of European railway undertakings rose from 0.036 EUR per tonne-kilometer in 2019 to 0.047 in 2024 (IRG-Rail 2026, Figure 18). Our 0.032 lies between the bulk and container operator costs and just below the 2019-2022 average revenue."

## BibTeX (keys do not collide with refs.bib; ademmer2023 and ademmer2020 already exist there and are reused as is)

```bibtex
@techreport{panteia2023kim,
  author      = {{Panteia}},
  title       = {Cost Figures for Freight Transport -- final report},
  institution = {KiM Netherlands Institute for Transport Policy Analysis},
  year        = {2023},
  url         = {https://www.kimnet.nl/site/binaries/site-content/collections/documents/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Cost+figures+for+freight+transport_def.pdf},
  note        = {Price level 2021; Table 5.5 maritime transport}
}
@article{dejong2014freightvot,
  author  = {de Jong, Gerard and Kouwenhoven, Marco and Bates, John and Koster, Paul and Verhoef, Erik and Tavasszy, Lori and Warffemius, Pim},
  title   = {New {SP}-values of time and reliability for freight transport in the {Netherlands}},
  journal = {Transportation Research Part E: Logistics and Transportation Review},
  year    = {2014},
  volume  = {64},
  pages   = {71--87},
  doi     = {10.1016/j.tre.2014.01.008}
}
@article{binsuwadan2022vfts,
  author  = {Binsuwadan, Jawaher and de Jong, Gerard and Batley, Richard and Wheat, Phill},
  title   = {The value of travel time savings in freight transport: a meta-analysis},
  journal = {Transportation},
  year    = {2022},
  volume  = {49},
  pages   = {1183--1209},
  doi     = {10.1007/s11116-021-10207-2}
}
@techreport{arup2023freightvot,
  author      = {{Ove Arup \& Partners} and {Significance}},
  title       = {Freight value of time and value of reliability -- final report},
  institution = {National Highways},
  year        = {2023},
  url         = {https://assets.publishing.service.gov.uk/media/68f21191f5d433238a14c70f/freight-value-time-value-reliability.pdf},
  note        = {PIN 603776, issue of 16 June 2023}
}
@misc{destatis2026gueterbefoerderung,
  author = {{Statistisches Bundesamt (Destatis)}},
  title  = {Beförderungsmenge und Beförderungsleistung nach Verkehrsträgern (Güterverkehr)},
  year   = {2026},
  url    = {https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Transport-Verkehr/Gueterverkehr/Tabellen/gueterbefoerderung-lr.html},
  note   = {Stand 20 April 2026; rail: Jahreserhebung der Schienen-Güterverkehrsstatistik}
}
@misc{destatis2026rail46132,
  author = {{Statistisches Bundesamt (Destatis)}},
  title  = {Annual statistics of freight transport by rail, goods carried, Germany (table 46132-BJ001), via DBnomics},
  year   = {2026},
  url    = {https://db.nomics.world/DESTATIS/46132BJ001},
  note   = {Mirror, updated by provider 15 October 2026; accessed 10 November 2026}
}
@techreport{irgrail2026mm14,
  author      = {{IRG-Rail}},
  title       = {14th Annual Market Monitoring Report},
  institution = {Independent Regulators' Group -- Rail},
  year        = {2026},
  url         = {https://www.amt-autoridade.pt/media/5839/2026_irg-rail_14th_mm_report_-_main_report.pdf},
  note        = {March 2026; Figure 18}
}
```

Authorship note: the Arup report's author list on its cover includes Gerard de Jong; the entry uses the company authors as printed on the cover.

## cite_check summary

Run on scratchpad/si_evidence.bib (same entries as above): 7 references, 2 ok (dejong2014freightvot, binsuwadan2022vfts), 5 unverified (no DOI: panteia2023kim, arup2023freightvot, destatis2026gueterbefoerderung, destatis2026rail46132, irgrail2026mm14; each opened by URL), 0 mismatch, 0 not_found. Result: PASS. Crossref metadata errors to report: none.

## Not verified / could not access

- Destatis annual 2025 rail tonnage at the Destatis source (page not yet updated; no press release found); the 350.9 Mt comes from the DBnomics mirror only. The BALM/IHK -2.8 % and VDV 133.9 billion tkm for 2025 were seen in search snippets only.
- German Economic Review 24(2) version of Ademmer et al. (paywalled); only Kiel WP 2155 Appendix B read. The WP does not describe the rail series further.
- Halse et al. (2019) Norwegian freight VOT study (in Norwegian): cited only through the Arup report. KiM 2013 report "Values of time and reliability" (189 pp.) not opened; de Jong et al. text "about 5 euro per tonne" unit unclear.
- Feo-Valero et al. (2011, Transport Reviews 31(5)) and Zamparini and Reggiani (2007, Transport Reviews 27(5)): bibliographic records seen, full text paywalled, not cited. HEATCO not searched.
- Q4: no quoted block-train or intermodal tariff per tkm found (the 0.02-0.04 range has no source); EC Rail Market Monitoring reports not opened (IRG-Rail used instead); UIC combined transport report 2022 not opened.
- No second or third citable per-tkm sea figure found: the evidence for Q1 rests on one source (KiM/Panteia 2023). No source for typical cargo value per tonne was opened.
- The KiM sea Table 5.5 was read from the rendered page (text extraction of that table is scrambled).
