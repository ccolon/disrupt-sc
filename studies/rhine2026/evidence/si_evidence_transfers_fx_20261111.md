# SI evidence: terminal transfer cost and dwell time, and the USD per EUR conversion (11 Nov 2026)

Scope: the table "Transport cost parameters", block "Terminal transfer", cells road-rail, waterway-sea, road- or rail-sea (the road- or rail-waterway cell is already sourced), plus the exchange rate for the table note.
Every figure below was read in the source named, on 11 Nov 2026, unless marked "not opened". Conversions are shown. Inferences are marked "inference".
Grades: A = read in the source itself; B = read in an official mirror or summary; C = secondary or search snippet only.
Conversion convention used here: 1 TEU or 1 loading unit (LU) = 10 t (the table's own convention); model USD converted to EUR by dividing by 1.053 (ECB 2022 average, section 3). Per-tonne figure of a per-unit tariff = tariff / 10.

## 0. Check on the lead given in the task

The KiM / Panteia cost-figures report (kim2023, 2023) has NO transhipment cost figure. I converted the whole PDF to text and searched for transhipment, transfer, terminal, handling and lift: the only hits are generic (line "Port dues may vary considerably per harbour ... tonnage and the quantity of transhipment", section on seaports, and one mention of "outsourced cargo handling"). The sea table 5.5 and rail table 6.2 already used in the SI contain no per-lift or per-tonne transfer cost. So kim2023 cannot be cited for these cells. INFRAS/PLANCO 2017 (infras2017) does have transfer costs (Table 18, section 3 below) and Konings 2009 does (below).

## 1. Summary table

Model values in the first column; EUR equivalents at 1.053 USD per EUR.

| Item | Figure found | Source (key; DOI or URL) | Where | Grade | Model vs source |
|---|---|---|---|---|---|
| Road-rail, dry bulk (model 3 USD/t = 2.85 EUR/t) | 2.60 EUR/t (dry bulk), 2.30 (agri "Sauggut"), price level 2012 | planco2015bvwp; URL in bibtex | sect. 8.1.5.6, Table 8-25, p. 270; text: costs apply to "intermodal Umladungen" between rail, road and inland vessel | A | model +10 % (inside) |
| Road-rail, liquid bulk (model 1 USD/t = 0.95 EUR/t) | 2.90 EUR/t, price level 2012 | planco2015bvwp | Table 8-25, p. 270 | A | model about 3 times below (0.33x) |
| Road-rail, containers (model 2 USD/t x 10 t = 20 USD = 19 EUR per unit) | 20.80 EUR per loading unit (container or swap body), price level 2012 = 2.08 EUR/t at 10 t | planco2015bvwp | Table 8-25, p. 270 | A | model 9 % below (0.91x) |
| Road-rail, containers, operator price lists | Rail/road and road/rail, entry - intermediate storage - exit, per load unit: 30.50 EUR (35.40 at Landshut and Hannover-Lehrte) in the DUSS list valid from 1 Jan 2026; 30.50 EUR in the DB Intermodal Services list valid from 1 Jan 2026. = 3.05 EUR/t at 10 t = 3.2 USD/t at 1.053 (3.45 at the 2025 rate 1.130) | duss2026price; dbis2026price | DUSS sect. 1 "Standard services"; DBIS sect. 1 | A (price lists, not costs) | model about 40 % below (0.6x) |
| Road-rail, containers, older list | 25.55 EUR per load unit, DUSS list 1 Jan 2023 | (search snippet only; the PDF link returned 404) | - | C, not used | - |
| Road-rail, dwell time (model 3 h, 4 h, 1 h) | none found | - | - | - | no evidence; hours are assumptions |
| Road- or rail-waterway, comparison only (model 4 / 5 / 3.5 USD/t = 3.8 / 4.75 / 3.3 EUR/t) | BVWP 2.60 dry, 2.90 liquid, 20.80 per container unit (2012), i.e. 2.08 EUR/t | planco2015bvwp | Table 8-25 | A | model 1.8x (containers), 1.8x (dry), 1.15x (liquid) |
| Same, INFRAS update | 2.83 "CHF/t" dry bulk, 3.15 liquid bulk, 2.50 agri bulk, 22.6 per loading unit | infras2017 | Table 18, p. 38; footnote 35 | A | see note A below: same numbers as BVWP x 1.087, not independent |
| Waterway-sea, containers (model 2 USD/t = 1.9 EUR/t = 19 EUR per TEU) | Feeder barge service in the Rotterdam port: handling about 70-80 EUR per unit for two moves (load and unload), sailing 15-20 EUR; = 35-40 EUR per move = 3.5-4 EUR/t. Container move at barge is "about 30 % more costly" than for a truck (citing Macharis and Verbeke 2004) | konings2009 | ch. 5, p. 97 (70-80 EUR; "board-to-board transhipment" would save one move); ch. 6.2.1, p. 108 (30 %) | A (thesis; data c. 2008, from the author's own earlier work) | model about half (0.5x) |
| Waterway-sea, containers, inland-terminal reference | handling tariff of 16 EUR per move assumed for break-even of a small inland barge terminal (Van Klink 2004, quoted) | konings2009 | ch. 6.2.2, p. 110 | A as a quotation, C as evidence | model 1.2x |
| Waterway-sea, dry and liquid bulk | no seaport tariff or study found (see section 4) | - | - | - | no evidence |
| Waterway-sea, general cargo (Hamburg terminal) | Weight dues 6.60 EUR/t "for cargo delivered from the quay into watercraft ... to the quay from watercraft", plus handling charge per tonne by commodity (section 2, below) | steinweg2022tariff | sect. I (1), p. 3; list p. 15-16 | A (published tariff, one conventional break-bulk terminal; 2022-23) | model 0.3x of the dues alone |
| Waterway-sea, time | Barge visiting ten terminals in Rotterdam: about 8 h sailing in the port plus about 1 h average wait per terminal (2003 survey of bargemen), about 18 h in total for the port rotation; waits "sometimes more than 24 hours" in summer 2004; full exchange of a 208 TEU barge takes 6-8 h | konings2009 | p. 90 (8 h, 1 h, 18 h); p. 83 (>24 h); p. 74 (6-8 h) | A | model 8 h: inside (above the 1 h wait per terminal, below the 18 h port rotation) |
| Road- or rail-sea, general cargo and containers (model 7 USD/t = 6.65 EUR/t) | Hamburg terminal, handling via quay, shore delivery by truck or wagon: steel 14.75-19.50 EUR/t; general cargo 36.50-65 EUR/t; chemicals (dangerous goods) 57-63 EUR/t; ISO container main move 145 EUR (14.5 EUR/t at 10 t); plus ship dues 6.60 EUR/t and a security charge of 14 EUR per container; valid 1 Sep 2022 - 31 Aug 2023 | steinweg2022tariff | p. 3-4 (dues, security), p. 15-16 (list) | A (published tariff) | model 2 to 10 times lower than these break-bulk and box tariffs |
| Road- or rail-sea, bulk | no bulk terminal tariff found | - | - | - | no evidence |
| Road- or rail-sea, time | Hamburg terminal: free quay storage 3 calendar days for imports, 5 for exports (a free period, not a dwell time) | steinweg2022tariff | sect. III (1), p. 6 | A, weak relevance | no usable dwell figure |
| USD per EUR, annual average | see section 3 | ECB via DBnomics; Eurostat via DBnomics; Fed G.5A | - | B (ECB, Eurostat), A (Fed) | - |

Note A (inference). INFRAS Table 18 values (2.83, 3.15, 2.50 "CHF/t"; 22.6 per loading unit) are the BVWP Table 8-25 values (2.60, 2.90, 2.30, 20.80) multiplied by 1.087 to 1.089 in every row. INFRAS names BVWP 2015 (S. 269f) as its source. So they are the same data at a later price level, not a second observation, and I could not tell why the unit is printed CHF. Do not count them as independent. INFRAS Table 13 (worked example Rotterdam-Basel) counts 3,078 EUR handling per trip = 16 EUR per TEU, which is not reconciled with 22.6 per loading unit x 1.3 units per TEU; I did not use Table 13 for this reason.

## 2. What each source is (so the cell can be worded honestly)

- planco2015bvwp: methodology report of the German federal transport plan appraisal (BVWP 2030), final report 24 March 2015, Planco, Intraplan, TUBS. Table 8-25 gives unit cost rates for intermodal transhipment, taken from the BVU/TNS Infratest transport cost model (price level 2010) and updated to the 2012 price level. Rates: dry bulk 2.60 EUR/t, agri bulk 2.30, liquid bulk 2.90, pallets 7.80, general cargo 14.60, container or swap body 20.80 EUR per loading unit. The text says they apply to intermodal transfers between rail, road and inland vessel, and that loading at the origin or destination is assumed equal across modes. These are appraisal cost rates, not market tariffs, and no time or dwell is given. They are the only rates I found that cover dry bulk, liquid bulk and containers in one table.
- duss2026price and dbis2026price: published 2026 price lists (EUR, per load unit, all load units incl. containers, semitrailers, swap bodies) of the main German road-rail terminal network (DUSS) and of DB Intermodal Services. They are prices charged to customers; the unit weight is not stated, so the per-tonne figure rests on the 10 t convention. They include intermediate storage. Rail/rail costs 56.00 (DUSS) or 61.00 (DBIS), run through without crane 11.80 (DUSS).
- konings2009: PhD thesis, TU Delft. The 70-80 EUR per unit is the handling share of feeder barge services between Rotterdam terminals, two moves; the thesis says board-to-board transhipment would save one move. The 8 h, 1 h and 18 h come from a 2003 bargemen survey (Koenis 2003) quoted on p. 90. Data are 2003-2008.
- steinweg2022tariff: tariff of one Hamburg break-bulk terminal (C. Steinweg Süd-West Terminal), not a bulk or container-specialist terminal, not Rotterdam. Used only as an upper reference. Pages as printed: p. 3 weight dues (6.60 EUR per 1,000 kg, also for cargo moved between quay and watercraft or by floating crane between sea vessel and quay), p. 4 security charge, p. 6 storage, p. 15-16 handling lists (export/import columns; I give the range).

## 3. Exchange rate, USD per EUR, annual average

Sources used: (1) ECB euro foreign exchange reference rates, series EXR.A.USD.EUR.SP00.A, read through the DBnomics mirror of the ECB (api.db.nomics.world, series indexed 2026-11-11; grade B because it is a mirror); (2) Eurostat table ert_bil_eur_a (A.AVG.NAC.USD), read through the DBnomics mirror (indexed 2026-01-22; B); (3) Federal Reserve G.5A Annual, page opened directly (release 5 Jan 2026; A, but a different series, New York noon buying rates, so it differs slightly). The ECB Data Portal, data-api.ecb.europa.eu (HTTP 503) and the Eurostat API (redirect to a "sorry" page) were not reachable from here; the ECB reference-rate page (eurofxref-graph-usd) shows only daily rates.

| Year | ECB (via DBnomics) | Eurostat (via DBnomics) | Fed G.5A |
|---|---|---|---|
| 2012 | 1.2848 | not read | not read |
| 2015 | 1.1095 | 1.1095 | not read |
| 2018 | 1.1810 | 1.1810 | not read |
| 2019 | 1.1195 | 1.1195 | not read |
| 2021 | 1.1827 | 1.1827 | not read |
| 2022 | 1.0530 | 1.0530 | 1.0534 |
| 2023 | 1.0813 | 1.0813 | 1.0817 |
| 2024 | 1.0824 | 1.0824 | 1.0820 |
| 2025 | 1.1300 | 1.1300 | 1.1306 |

2022 = 1.053 (ECB 1.05305, Eurostat 1.053): confirmed, as expected. 2025 is published (full year). The 2026 annual average is not yet available (daily rate 1.117 on 30 Oct 2026, ECB via DBnomics). CHF per EUR 2015 (ECB via DBnomics) = 1.0679, for reading INFRAS.
Effect of the SI treating EUR and USD as equal (inference, arithmetic): a euro figure is understated in USD by 5 % at the 2022 rate, 8 % (2023, 2024), 11-12 % (2015, 2019, 2025), 18 % (2018, 2021).

## 4. Proposed evidence sentences for the table cells (plain English)

Road-rail (cell "Intermodal terminals and bulk sidings at both ends of a rail trip"):
"German appraisal rates for a road-rail or waterway transfer are 2.60 EUR per tonne for dry bulk, 2.90 for liquid bulk and 20.80 EUR per container or swap body (2012 prices; Planco et al. 2015, Table 8-25), and 2026 price lists of two German terminal operators charge 30.50 EUR per load unit (DUSS 2026; DB Intermodal Services 2026); our dry-bulk value is within 10 % of the appraisal rate, the container value is 9 % below it and about 40 % below the price lists (10 t per unit), and the liquid-bulk value is about a third of it. We found no published dwell times, so the hours are assumptions."

Waterway-sea (cell "Port handling", 8 h and 2 USD per tonne):
"For containers, Konings (2009, p. 97) reports about 70-80 EUR per unit for two moves in feeder barge services of the Rotterdam port (c. 2008), that is 3.5-4 EUR per tonne per move at 10 t per TEU, so our 2 USD is about half of it; barges spend about 8 h sailing and about 1 h waiting per terminal in the port (p. 90), so 8 h is within the range. We found no published figure for dry or liquid bulk."

Road- or rail-sea (cell "Port handling", 24 h and 7 USD per tonne):
"A published 2022-23 tariff of one Hamburg break-bulk terminal charges 6.60 EUR per tonne in quay dues plus 14.75-65 EUR per tonne handling by cargo type and 145 EUR per container move, which is 2 to 10 times our 7 USD; we found no bulk-terminal tariff and no dwell-time figure, so for bulk and for the 24 h this value rests on calibration, not on a source."

Exchange rate (table note):
"EUR-denominated sources are compared with the model without conversion; the ECB annual average was 1.053 USD per EUR in 2022 (1.110 in 2015, 1.181 in 2018, 1.120 in 2019, 1.183 in 2021, 1.081 in 2023, 1.082 in 2024, 1.130 in 2025), so a euro figure read as dollars is understated by 5 % at the 2022 rate and by up to 18 % in the highest years."

(Optional addition to the already-sourced road- or rail-waterway cell: "The German appraisal rates, which apply to transfers between rail, road and inland vessel, are 2.60 EUR per tonne for dry bulk, 2.90 for liquid bulk and 20.80 EUR per container unit (2012 prices; Planco et al. 2015), so our 5, 3.5 and 4 USD per tonne are 1.8, 1.15 and 1.8 times higher." Arithmetic: dry 5/1.053 = 4.75 vs 2.60 = 1.83; liquid 3.5/1.053 = 3.32 vs 2.90 = 1.15; containers 4/1.053 = 3.80 EUR/t vs 2.08 = 1.83.)

## 5. BibTeX for new sources

Keys do not collide with refs.bib (checked against `kim2023`, `infras2017`, `konings2009`, which exist and are reused: konings2009 p. 74, 83, 90, 97, 108, 110; infras2017 Table 18 p. 38). Verified: all seven opened by URL on 11 Nov 2026; none has a DOI, so the gate marks them unverified. The Steinweg tariff and the two price lists are dated documents of their issuers; the two exchange-rate mirrors carry the ECB and Eurostat series.

```bibtex
@techreport{planco2015bvwp,
  author      = {{Planco Consulting GmbH} and {Intraplan Consult GmbH} and {TUBS GmbH}},
  title       = {Grunds{\"a}tzliche {\"U}berpr{\"u}fung und Weiterentwicklung der Nutzen-Kosten-Analyse im Bewertungsverfahren der Bundesverkehrswegeplanung, Endbericht},
  institution = {Bundesministerium f{\"u}r Verkehr und digitale Infrastruktur},
  address     = {Essen, Berlin, M{\"u}nchen},
  year        = {2015},
  url         = {https://svn.vsp.tu-berlin.de/repos/public-svn/publications/vspwp/2014/14-12/PlancoItpTubs2015FeBerichtBvwpMethodik.pdf},
  note        = {FE-Projekt 960974/2011, 24 March 2015; section 8.1.5.6 and Table 8-25, p. 270 (price level 2012). Opened 2026-11-11}
}
@misc{duss2026price,
  author = {{Deutsche Umschlaggesellschaft Schiene--Stra{\ss}e (DUSS) mbH}},
  title  = {{DUSS} 2026 Price List},
  year   = {2026},
  url    = {https://duss-terminal.deutschebahn.com/resource/blob/13623682/2bf0e1730edda72f9e02e7f890817b3b/2026-DUSS-price-list_EN-1-1-2026-data.pdf},
  note   = {Valid from 1 January 2026; section 1. Opened 2026-11-11}
}
@misc{dbis2026price,
  author = {{DB Intermodal Services GmbH}},
  title  = {Price list for terminal services},
  year   = {2026},
  url    = {https://www.dbcargo.com/resource/blob/13691804/120457d5f820ef173f07a30fa4f67fe3/EN-Price-list-Terminal-Services-2026-data.pdf},
  note   = {Valid from 1 January 2026; section 1. Opened 2026-11-11}
}
@misc{steinweg2022tariff,
  author = {{C. Steinweg (S{\"u}d-West Terminal) GmbH \& Co. KG}},
  title  = {Tariff, Quay Handling Services at the terminal (Hamburg)},
  year   = {2022},
  url    = {https://www.steinweg.com/wp-content/uploads/2022/08/quay-tarif-C.-Steinweg-valid-until-31.08.2023.pdf},
  note   = {Valid 1 September 2022 to 31 August 2023; pp. 3, 6, 15-16. Opened 2026-11-11}
}
@misc{ecb2026exrusd,
  author = {{European Central Bank}},
  title  = {Euro foreign exchange reference rates, US dollar, annual average (series EXR.A.USD.EUR.SP00.A), via DBnomics},
  year   = {2026},
  url    = {https://db.nomics.world/ECB/EXR/A.USD.EUR.SP00.A},
  note   = {Mirror of the ECB Data Portal, indexed 2026-11-11; read through api.db.nomics.world}
}
@misc{eurostat2026ertbileura,
  author = {{Eurostat}},
  title  = {Euro/ECU exchange rates, annual data (ert\_bil\_eur\_a), US dollar, annual average, via DBnomics},
  year   = {2026},
  url    = {https://db.nomics.world/Eurostat/ert_bil_eur_a},
  note   = {Mirror, indexed 2026-01-22; series A.AVG.NAC.USD}
}
@misc{fed2026g5a,
  author = {{Board of Governors of the Federal Reserve System}},
  title  = {Foreign Exchange Rates -- G.5A Annual},
  year   = {2026},
  url    = {https://www.federalreserve.gov/releases/g5a/current/default.htm},
  note   = {Release of 5 January 2026; Euro Area, US dollars per euro. Opened 2026-11-11}
}
```

Citation gate (cite_check.py on the file with these seven entries, copy at scratchpad/transfers.bib): 7 references, 7 unverified (no DOI; each opened by URL), 0 mismatch, 0 not_found. Result PASS. No Crossref metadata error to report.

## 6. What I looked for and could not find or open

- Wiegmans and Behdani (2018), Transport Reviews 38(1) 33-51, DOI 10.1080/01441647.2017.1297867 (Crossref record confirmed: title, authors, year, volume, pages). Only the abstract was read (via TU Delft research portal and Wageningen portal): handling costs vary widely, extra-large terminals have the lowest average cost per handling. The full text (TU Delft repository, Taylor and Francis) returned 403 or could not be connected; no per-lift figure from it. Not cited.
- Wiegmans and Konings (2015), Asian J. Shipping and Logistics 31(2) 273-294, DOI 10.1016/j.ajsl.2015.06.006 (Crossref record exists; title and authors from the search result): full text 403. Not read; terminal cost tables not seen.
- Janic (2007), Transp. Res. D 12(1) 33-44, "Modelling the full costs of an intermodal and road freight transport network": abstract-level only; no transhipment figures seen. Not cited.
- European Commission study "Comparative evaluation of transhipment technologies for intermodal transport and their cost" (PwC, KombiConsult, 2022; the Publications Office page gives DOI 10.2832/205486, released 2022-04-08): only the metadata page was read; the PDF could not be downloaded (empty responses). This is the best lead for per-lift costs by technology; worth opening by hand.
- RECORDIT (Ricci 2003, EJTIR 3(4), 351-370): opened; it gives corridor totals and shows terminal costs only in a figure, no per-lift value. Not used.
- Notteboom (2007), J. Maritime Research 4(2): opened; no cost figures. Not used.
- European Court of Auditors special report 08/2023 (intermodal freight): opened; qualitative on handling cost, no figure. Not used.
- A "20-25 EUR per move in road-rail terminals, 18-25 in inland ports, 80-125 in seaports" statement appeared in a search result from a Scribd upload ("2008 12 Logistics", uploader only, no author or date visible; 335 pages). I could not open the text or identify the original document, so it is NOT used. It is consistent in size with the BVWP and DUSS figures (20.80 and 25.55-30.50) but unverified.
- DUSS 2023 and 2024 price lists and the DUSS storage conditions: links returned 404; the 25.55 EUR (2023) is from a search snippet only.
- Dry bulk and liquid bulk: any seaport stevedoring or terminal tariff per tonne (Rotterdam, Antwerp, Amsterdam, Zeebrugge): none found open. The Zeebrugge (Wallenius Wilhelmsen) and Thessaloniki tariffs seen in search results were not opened (the first is a ro-ro and vehicle terminal, the second outside the study area). Board-to-board (ship to barge) bulk rates: none found. Rotterdam barge handling charge per container: not found.
- Cost and time of loading or unloading rail wagons at a bulk siding: no published figure found (BVWP Table 8-25 is the nearest).
- Road-rail terminal dwell or handling times, and seaport dwell for cargo leaving by truck or train: none from a primary source. A port-statistics aggregator (Cogoport, rail imports 6.8 days in Feb 2026, imports 3.8 days) and a gCaptain item (Rotterdam deep-sea terminals, average dwell four days before the pandemic and ten later) were seen in search snippets only, not opened, and are not used.
- Exchange rates: the ECB Data Portal and the Eurostat dissemination API could not be reached from this machine (503 and redirect). The ECB and Eurostat values come from their DBnomics mirrors; the Fed G.5A page gives a second, independent official check for 2022-2025 only. Fed older years and the ECB's own page were not read.
- KiM 2023 (kim2023): no transhipment cost (section 0).
