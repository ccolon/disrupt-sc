# Inventory durations by buying industry: evidence dossier (EU scope)

Compiled 4 September 2026 for the whole-EU DisruptSC scope (50 OECD ICIO sectors, weekly
time step). Purpose: replace the input-type-keyed inventory targets
(`config/default.yaml`, `inventory_duration_targets`: agriculture 15 d, manufacturing 30 d,
services 90 d, trade 30 d, transport 5 d, utility 3 d, default 30 d) with targets keyed by
the BUYING industry (and, where the data allow, by input type within the buying industry).

Conventions used throughout:

- "Days" = stock / (annual flow / 365). Where the flow is the buyer's cost of materials,
  the figure is directly comparable to the model's target ("days of consumption of the
  input"). Where the flow is turnover, the figure is a days-of-sales measure and must be
  divided by the material share of turnover to become days of consumption.
- All PDF tables were read with `pdftotext` (raw mode) from the official files and the
  ratios were recomputed with awk; sums were checked against the published totals
  (e.g. chemicals 2023: 14.0 + 10.9 + 17.2 + 0.2 = 42.3 bn EUR vs published Vorräte 42.2,
  rounding). Numbers that come only from search-engine abstracts, not from a fetched
  document, are flagged "(abstract only)".
- Grades in the final table: A = direct balance-sheet measure of raw-material stocks for
  that sector, corroborated by a second source; B = balance-sheet measure that includes
  work in progress or covers a broader sector group, or physical stock evidence for the
  main input; C = indirect (total inventories over turnover) or analogy; D = assumption.

Headline findings:

1. German extrapolated balance sheets (Bundesbank, 2023) give raw materials, consumables
   and supplies ("Roh-, Hilfs- und Betriebsstoffe", RHB) of 33.9 days of cost of materials
   for manufacturing as a whole, ranging from 18 days (food; motor vehicles) to 59 days
   (machinery) and 70 days (electronics/electrical). Outside manufacturing the RHB stock is
   small: construction 9 d, transport 7 d, business services 6 d, energy/water 3 d, trade
   1-3 d (trade holds goods for resale instead: 30-56 days of turnover).
2. The manufacturing RHB duration rose from 21 days (2011-2015) to 25 days (2019) and
   34 days (2022-2023): the post-2021 "just in case" build-up is visible in the aggregates
   and has not reversed by 2023 (2024 aggregate for all enterprises: 12.7 d vs 12.2 d in 2023).
3. Physical stocks of bulk feedstocks are much shorter than the balance-sheet averages:
   German refiners' own crude stocks are about 10 days of intake (EBV strategic stocks
   excluded); coal at German plants was "about one week of full load" on site in 2022 and
   the 2022-2024 reserve rule required 30 days; a Rhine oil mill and a large flour mill hold
   5-14 days of grain/oilseed; compound-feed plants run just-in-time; an integrated
   steelworks holds 1-2 months of ore and coal (design range 7-45 days). Cement plants hold
   7-14 days of clinker (vendor sources).
4. Academic models use a single duration per industry (Pichler et al.: ONS inventory-to-
   turnover x 365, no input split; Inoue & Todo: 9 days for every firm; Hallegatte 2014:
   90 days, 3 days for utilities/transport); none of them separates raw materials from
   finished goods, which is why their values are higher than the RHB-based ones.

---------------------------------------------------------------------------------------

## 1. Deutsche Bundesbank corporate balance-sheet statistics

### 1.1 Sources and definitions

Source A (extrapolated, sector totals in EUR bn): Deutsche Bundesbank, Statistische
Fachreihe "Jahresabschlussstatistik (Hochgerechnete Angaben)", edition December 2025
(closed December 2025; ISSN 2699-8564), successor of Statistische Sonderveroeffentlichung 5
"Hochgerechnete Angaben aus Jahresabschluessen deutscher Unternehmen" (discontinued as a
special publication in April 2020). Years 1997-2024 (2024 = estimate, marked "s"), WZ 2008
classification. Coverage: about 130 000 individual accounts per year in the Bundesbank
data pool, extrapolated to "about 93 % of the turnover of the non-financial corporate
sector"; excludes agriculture/forestry/fishing, real estate, holding companies and
non-business services. Each sector has an "Erfolgsrechnung und Bilanz" table (EUR bn)
and an "Ausgewaehlte Verhaeltniszahlen" table (ratios, incl. "Vorraete in % des Umsatzes").
The annual Monthly Report article "Ertragslage und Finanzierungsverhaeltnisse deutscher
Unternehmen" (December issue) summarises the same data; the December 2023 article (2022
data) attributes the broad-based 2022 inventory build-up to the recovery, price effects and
"possibly also the effort to make value chains more resilient" (p. 66).

Source B (not extrapolated, ratios and quartiles by fine sector): Deutsche Bundesbank,
Statistische Fachreihe "Jahresabschlussstatistik (Verhaeltniszahlen - vorlaeufig)",
edition May 2026, comparable circle of firms 2023/2024, all legal forms, by size class
(turnover < 2, 2-10, 10-50, >= 50 m EUR). It gives "Vorraete in % der Bilanzsumme" with
"darunter: fertige Erzeugnisse und Waren", "Umsatz in % der Bilanzsumme",
"Materialaufwand in % der Gesamtleistung", plus quartiles, turnover and number of firms.
It does NOT split raw materials from work in progress. Not extrapolated, so large firms
are over-represented (the 10-50 and >= 50 m EUR classes dominate the totals).

Balance-sheet items (Source A, "Anmerkungen zu einzelnen Positionen"):

- Vorraete = Roh-, Hilfs- und Betriebsstoffe (raw materials, auxiliary materials,
  operating supplies incl. fuels, lubricants, packaging) + unfertige Erzeugnisse und
  Leistungen (work in progress, unbilled services) + fertige Erzeugnisse und Waren
  (finished goods and merchandise for resale) + geleistete Anzahlungen (payments on
  account for inventories).
- Umsatz = net sales after rebates.
- Materialaufwand = "Aufwendungen fuer Roh-, Hilfs- und Betriebsstoffe sowie fuer bezogene
  Waren und Leistungen" (cost of raw materials, consumables and supplies PLUS purchased
  merchandise and purchased services). This denominator is therefore wider than material
  consumption; RHB/Materialaufwand understates the days of cover of physical materials
  by the share of purchased services and merchandise (not published; for manufacturing
  probably 10-25 % of Materialaufwand, so multiply by roughly 1.1-1.3 for a physical-input
  figure).

### 1.2 Table A: extrapolated balance sheets, 2023 (EUR bn) and derived days

Sector groups are those of the publication (WZ 2008 divisions in brackets). 2023 is the
last year available for sub-sectors; the aggregate "all enterprises" also has a 2024
estimate (RHB 193.4, Materialaufwand 5 556.6, Umsatz 8 481.7 bn -> 12.7 d).

| Sector (WZ 2008) | Umsatz | Material-aufwand | RHB | WIP | Finished goods & merch. | Adv. | RHB / Matl. x 365 (d) | (RHB+WIP) / Matl. (d) | Total inv. / Umsatz (d) | FG / Umsatz (d) |
|---|---|---|---|---|---|---|---|---|---|---|
| All enterprises (B-N excl. K, L) | 8 748.8 | 5 917.0 | 197.5 | 468.7 | 453.8 | 45.4 | 12.2 | 41.1 | 48.6 | 18.9 |
| Produzierendes Gewerbe (B-F) | 4 477.1 | 3 152.1 | 175.3 | 383.1 | 167.8 | 26.8 | 20.3 | 64.7 | 61.4 | 13.7 |
| Manufacturing (C, 10-33) | 2 701.0 | 1 704.5 | 158.4 | 197.4 | 136.8 | 19.4 | 33.9 | 76.2 | 69.2 | 18.5 |
| Food, beverages, tobacco (10-12) | 265.2 | 178.2 | 9.0 | 2.4 | 11.4 | 0.2 | 18.4 | 23.4 | 31.7 | 15.7 |
| Textiles, apparel, leather (13-15) | 26.0 | 14.8 | 1.7 | 0.7 | 3.1 | 0.1 | 41.9 | 59.2 | 78.6 | 43.5 |
| Wood, paper, printing (16-18) | 94.8 | 54.4 | 4.9 | 3.3 | 4.4 | 0.2 | 32.9 | 55.0 | 49.3 | 16.9 |
| Chemicals and pharmaceuticals (20-21) | 281.3 | 166.3 | 14.0 | 10.9 | 17.2 | 0.2 | 30.7 | 54.7 | 54.9 | 22.3 |
| Rubber, plastics, glass, ceramics, minerals (22-23) | 163.7 | 88.3 | 9.4 | 7.1 | 10.9 | 0.4 | 38.9 | 68.2 | 62.0 | 24.3 |
| Basic metals and metal products (24-25) | 333.6 | 209.3 | 20.9 | 33.8 | 17.9 | 1.9 | 36.4 | 95.4 | 81.5 | 19.6 |
| Computers, electronics, optics, electrical equipment (26-27) | 265.3 | 151.5 | 29.2 | 27.2 | 14.4 | 1.9 | 70.3 | 135.9 | 100.0 | 19.8 |
| Machinery (28) | 336.9 | 189.5 | 30.5 | 60.8 | 18.3 | 4.3 | 58.7 | 175.9 | 123.4 | 19.8 |
| Motor vehicles and other transport equipment (29-30) | 703.4 | 501.6 | 25.3 | 41.5 | 27.3 | 9.3 | 18.4 | 48.6 | 53.7 | 14.2 |
| Energy, water supply, waste (D-E, 35-39) | 1 336.4 | 1 210.3 | 9.9 | 6.1 | 17.2 | 0.7 | 3.0 | 4.8 | 9.3 | 4.7 |
| Construction (F) | 413.6 | 225.6 | 5.5 | 179.0 | 12.6 | 6.5 | 8.9 | 298.5 | 179.7 | 11.1 |
| Trade incl. motor trade (G, 45-47) | 2 721.2 | 2 105.9 | 12.6 | 10.5 | 266.2 | 12.6 | 2.2 | 4.0 | 40.5 | 35.7 |
| - Motor vehicle trade and repair (45) | 374.5 | 296.6 | 1.1 | 0.8 | 57.2 | 0.6 | 1.4 | 2.3 | 58.2 | 55.7 |
| - Wholesale (46) | 1 623.1 | 1 329.7 | 9.7 | 7.7 | 130.6 | 11.1 | 2.7 | 4.8 | 35.8 | 29.4 |
| - Retail (47) | 723.6 | 479.6 | 1.8 | 2.0 | 78.4 | 1.0 | 1.4 | 2.9 | 42.0 | 39.5 |
| Transport and storage (H, 49-53) | 419.5 | 219.7 | 4.4 | 2.8 | 2.1 | 0.3 | 7.3 | 12.0 | 8.4 | 1.8 |
| Information and communication (J, 58-63) | 402.6 | 182.7 | 1.1 | 9.9 | 6.8 | 1.3 | 2.2 | 22.0 | 17.3 | 6.2 |
| Business services ("Unternehmensdienstleistungen", M-N) | 608.6 | 225.0 | 3.8 | 62.2 | 9.8 | 4.3 | 6.2 | 107.1 | 48.0 | 5.9 |

Not separately published in Source A: coke and refined petroleum (19), repair and
installation (33), mining (B), agriculture (A). WZ 19 is included in the manufacturing
total only.

### 1.3 Table B: time profile of RHB / Materialaufwand x 365 (days), Source A

| Sector | 2011 | 2015 | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|---|---|
| All enterprises | 9.0 | 8.9 | 9.8 | 10.7 | 12.1 | 11.8 | 12.2 |
| Produzierendes Gewerbe | 15.3 | 15.5 | 17.5 | 20.1 | 21.4 | 19.1 | 20.3 |
| Manufacturing | 21.1 | 20.9 | 24.8 | 29.5 | 32.8 | 33.6 | 33.9 |
| Food, beverages, tobacco | 15.0 | 17.3 | 17.7 | 18.1 | 20.5 | 20.1 | 18.4 |
| Textiles, apparel, leather | 33.0 | 32.5 | 34.9 | 38.9 | 44.9 | 47.2 | 41.9 |
| Wood, paper, printing | 24.8 | 26.7 | 27.5 | 30.6 | 33.6 | 32.0 | 32.9 |
| Chemicals, pharma | 21.4 | 21.8 | 25.9 | 27.9 | 27.8 | 27.6 | 30.7 |
| Rubber, plastics, glass, minerals | 27.9 | 28.2 | 30.9 | 31.5 | 35.8 | 37.3 | 38.9 |
| Basic metals, metal products | 25.5 | 26.7 | 31.1 | 34.2 | 35.3 | 35.3 | 36.4 |
| Electronics, electrical | 28.1 | 30.5 | 36.8 | 60.4 | 62.8 | 68.5 | 70.3 |
| Machinery | 37.4 | 36.8 | 42.8 | 48.1 | 52.4 | 59.8 | 58.7 |
| Motor vehicles, other transport | 10.2 | 9.8 | 12.5 | 15.1 | 17.2 | 19.9 | 18.4 |
| Energy, water, waste | 3.4 | 3.7 | 3.0 | 3.2 | 4.5 | 2.7 | 3.0 |
| Construction | 9.0 | 8.6 | 9.6 | 8.1 | 9.0 | 9.4 | 8.9 |
| Trade | 1.9 | 1.7 | 1.8 | 1.8 | 2.1 | 2.3 | 2.2 |
| Transport and storage | 4.8 | 4.7 | 6.1 | 6.5 | 6.7 | 6.3 | 7.3 |
| Information and communication | 1.8 | 1.6 | 1.8 | 1.5 | 1.9 | 2.2 | 2.2 |
| Business services | 4.5 | 3.7 | 4.6 | 5.2 | 5.1 | 6.0 | 6.2 |

Reading: the pre-pandemic level (2019) is the natural "lean" calibration; 2022-2023 is the
"just-in-case" level. For a 2026 scenario the 2023 values are the better prior (the
Hackett and PwC working-capital surveys in section 4.5 report European inventory days at
ten-year highs in FY2024).

### 1.4 Table C: ratio series by WZ division, 2023 (Source B, "insgesamt" column)

Derived columns: total inventories / turnover = (Vorraete % BS) / (Umsatz % BS) x 365;
"non-finished stock" = Vorraete minus finished goods and merchandise (= raw materials +
work in progress + advances) expressed in days of Materialaufwand
(= (Vorraete - FG) / (Umsatz x Materialaufwand/Gesamtleistung) x 365, Gesamtleistung
taken equal to Umsatz). The WIP component makes the last column an UPPER bound for raw
materials in long-cycle industries (machinery, other transport equipment, construction,
business services).

| WZ 2008 | Sector | Vorraete % BS | of which FG % BS | Umsatz % BS | Material-aufwand % GL | n firms | Total inv. / turnover (d) | Non-finished stock / Matl. (d) |
|---|---|---|---|---|---|---|---|---|
| A | Agriculture, forestry, fishing | 8.4 | 3.9 | 55.5 | 60.0 | 661 | 55 | 49 |
| B | Mining and quarrying | 5.4 | 1.0 | 39.2 | 55.1 | 164 | 50 | 74 |
| C | Manufacturing | 16.4 | 4.6 | 94.7 | 65.9 | > 10 000 | 63 | 69 |
| 10 | Food and feed | 17.7 | 8.8 | 221.3 | 74.4 | 936 | 29 | 20 |
| 11 | Beverages | 12.6 | 5.7 | 119.4 | 50.2 | 138 | 39 | 42 |
| 13 | Textiles | 28.6 | 11.9 | 135.9 | 60.9 | 196 | 77 | 74 |
| 16 | Wood products | 24.6 | 7.0 | 143.0 | 63.6 | 360 | 63 | 71 |
| 17 | Paper | 15.9 | 6.2 | 126.9 | 61.4 | 244 | 46 | 45 |
| 18 | Printing | 10.9 | 3.2 | 135.7 | 48.5 | 238 | 29 | 43 |
| 20 | Chemicals | 9.7 | 4.0 | 72.5 | 66.3 | 599 | 49 | 43 |
| 21 | Pharmaceuticals | 7.2 | 2.4 | 38.5 | 55.3 | 147 | 68 | 82 |
| 22 | Rubber and plastics | 19.7 | 8.0 | 129.1 | 56.4 | 853 | 56 | 59 |
| 23 | Glass, ceramics, non-metallic minerals | 17.2 | 7.0 | 95.5 | 53.8 | 515 | 66 | 73 |
| 24 | Basic metals | 30.2 | 9.1 | 178.0 | 78.3 | 381 | 62 | 55 |
| 25 | Fabricated metal products | 31.9 | 7.4 | 123.6 | 56.7 | > 2 000 | 94 | 128 |
| 26 | Computers, electronics, optics | 19.4 | 4.3 | 85.0 | 51.9 | 843 | 83 | 125 |
| 27 | Electrical equipment | 30.6 | 5.3 | 102.8 | 63.5 | 584 | 109 | 142 |
| 28 | Machinery | 36.6 | 5.7 | 105.9 | 55.6 | > 2 000 | 126 | 192 |
| 29 | Motor vehicles and parts | 7.1 | 3.1 | 78.9 | 71.5 | 340 | 33 | 26 |
| 30 | Other transport equipment | 37.1 | 2.8 | 62.0 | 58.5 | 114 | 218 | 345 |
| 31 | Furniture | 16.6 | 3.0 | 155.7 | 55.6 | 181 | 39 | 57 |
| 32 | Other manufacturing | 18.2 | 8.4 | 99.4 | 46.5 | 451 | 67 | 77 |
| 33 | Repair and installation of machinery | 40.8 | 5.4 | 112.2 | 54.2 | 382 | 133 | 213 |
| D | Energy supply | 4.2 | 2.2 | 200.9 | 91.9 | > 2 000 | 8 | 4 |
| E | Water, sewerage, waste | 3.0 | 0.9 | 56.1 | 62.9 | > 1 000 | 20 | 22 |
| F | Construction | 56.5 | 2.4 | 78.5 | 62.1 | > 6 000 | 263 | 405 (WIP = unfinished buildings) |
| 45 | Motor vehicle trade and repair | 38.2 | 37.1 | 274.3 | 83.6 | > 2 000 | 51 | 2 |
| 46 | Wholesale | 21.7 | 17.9 | 256.7 | 84.9 | > 7 000 | 31 | 6 |
| 47 | Retail | 22.4 | 21.7 | 232.7 | 69.5 | > 2 000 | 35 | 2 |
| H | Transport and storage | 1.8 | 0.4 | 68.8 | 58.0 | > 3 000 | 10 | 13 |
| 49 | Land transport and pipelines | 2.5 | 0.1 | 60.3 | 57.2 | > 1 000 | 15 | 25 |
| 52 | Warehousing and transport services | 2.0 | 1.0 | 87.0 | 54.4 | > 1 000 | 8 | 8 |
| I | Accommodation and food services | 1.8 | 0.9 | 145.2 | 31.2 | > 1 000 | 5 | 7 |
| J | Information and communication | 3.2 | 1.1 | 78.3 | 47.2 | > 2 000 | 15 | 21 |
| 61 | Telecommunications | 3.0 | 1.0 | 57.0 | 45.2 | 167 | 19 | 28 |
| 62-63 | IT and information services | 2.9 | 0.7 | 95.5 | 47.5 | > 2 000 | 11 | 18 |
| L | Real estate | 4.0 | 0.5 | 13.9 | 44.1 | > 7 000 | 105 | 208 (property WIP) |
| M-N | Business services | 15.0 | 2.3 | 99.7 | 41.1 | > 6 000 | 55 | 113 (unbilled WIP) |
| P-Q | Predominantly private services (education, health, homes, social) | 2.1 | 0.2 | 89.8 | 27.9 | > 5 000 | 9 | 28 |
| 86 | Health care | 3.0 | 0.1 | 87.9 | 30.3 | > 1 000 | 13 | 40 |

Firm counts marked "> n" were truncated by the thousands separator in extraction; the
order of magnitude is from the same table.

### 1.5 Caveats (Bundesbank)

- RHB is the only published raw-material stock; it includes operating supplies (fuel,
  packaging), which matters for transport (fuel) and utilities.
- Materialaufwand includes purchased services and merchandise (see 1.1); the physical
  days of cover are somewhat higher than RHB/Materialaufwand.
- Stocks are valued at HGB cost (lower of cost or market); in 2022 (rising prices) the
  ratios are biased down, in 2023 (falling energy prices) biased up. The 2019-2023 range
  in Table B brackets this.
- Sector groups mix industries with very different logistics (e.g. 20-21 chemicals with
  pharma; 29-30 cars with aircraft); Table C separates them but is not extrapolated.
- The extrapolation corrects the over-representation of large firms; Table C and the
  FIBEN quartiles (section 2.2) do not. For a model whose "firms" are regional sector
  aggregates, the value-weighted extrapolated ratios (Table A) are the right concept.

---------------------------------------------------------------------------------------

## 2. BACH (ECCBSO) and Banque de France sector sheets

### 2.1 BACH: variables, ratios, access

BACH (Bank for the Accounts of Companies Harmonized) is run by the European Committee of
Central Balance-Sheet Data Offices and hosted by the Banque de France. Coverage: Austria,
Belgium, Croatia, France, Germany, Hungary, Italy, Luxembourg, Poland, Portugal,
Slovakia, Spain; from 2000; 17 NACE sections and about 80 NACE Rev. 2 divisions; size
classes; weighted means and quartiles (BACH User Guide summary, January 2022; ECB
Statistics Paper 11, 2015).

Variables relevant here (BACH User Guide summary, January 2022):

- A2 Inventories: "Includes raw materials and consumables, goods, work in progress and
  finished products, as well as consumable biological assets." A21 = of which payments
  on account. There is NO raw-material sub-item in BACH.
- I1 Net turnover; I2 Variation in stocks of finished goods and work in progress;
  I5 "Cost of goods sold, materials and consumables: Includes cost of materials and
  consumables used and the cost of goods sold in the period."
- Ratio R51 = Inventories / Net turnover (A2 / I1). Days of inventory = R51 x 365
  (turnover basis); to move to a cost-of-materials basis divide by I5/I1.
- Working-capital ratios R52 (trade receivables/turnover), R53 (trade payables/turnover),
  R54 (operating working capital/turnover); the separate ECCBSO "trade credit" database
  holds DSO/DPO but no inventory days.

Access: https://www.bach.banque-france.fr (the site title is "Connexion a BACH et
ERICA"). The database requires a free registration and login ("CONNECTION / REGISTER
(FREE)"); no anonymous download or API was found, and no account was created for this
dossier. What can be pulled after registration: R51 by country x NACE division x year x
size class, and the weighted-average balance-sheet structure (A2 as % of total assets)
with I5/I1. The ECB SP11 paper and the 2022 user guide contain no inventory tables, and
the "BACH Get Insights 2023" PDF (10 MB) could not be fetched.

### 2.2 Banque de France FIBEN sector sheets ("Fascicules de resultats sectoriels")

Same data office (Direction des Entreprises, Observatoire des entreprises), French legal
units subject to corporate tax, FIBEN database (firms with turnover above the FIBEN
threshold), quartiles across firms (Q1 / median / Q3), ratios only for strictly positive
denominators. Definition (sheet p. 3): "Poids des stocks (j) = (Stocks de marchandises +
produits finis et encours + approvisionnements) / Chiffre d'affaires HT" - total stocks
(merchandise + finished goods and WIP + supplies) in days of turnover excl. VAT (day
basis 360 vs 365 not stated). Editions: 2023 sheets (published Dec 2024, data Oct 2024)
and 2024 sheets (published Nov 2025, data Oct 2025).

| NACE | Sector | Edition | n firms | Q1 | Median | Q3 | Median previous year |
|---|---|---|---|---|---|---|---|
| C | Manufacturing | 2024 | 29 935 | 18.3 | 43.1 | 81.3 | 43.5 (2023, n = 29 972) |
| C | Manufacturing | 2023 | 36 848 | 15.8 | 40.2 | 79.4 | 41.9 (2022) |
| 10 | Food industries | 2024 | 5 194 | 6.4 | 18.4 | 43.2 | 18.7 |
| 11 | Beverages | 2024 | 944 | 57.4 | 174.0 | 406.5 | 168.0 |
| 20 | Chemicals | 2024 | 1 168 | 37.9 | 61.9 | 97.0 | 62.6 |
| 24 | Basic metals (metallurgie) | 2024 | 473 | 36.9 | 62.2 | 95.7 | 60.4 |
| 25 | Fabricated metal products | 2024 | 5 547 | 18.7 | 40.6 | 73.8 | 41.1 |
| 29 | Automotive | 2024 | 694 | 36.0 | 60.1 | 96.4 | 63.5 |
| 46 | Wholesale | 2024 | 26 664 | 15.9 | 43.1 | 82.2 | 42.5 |
| 47 | Retail | 2024 | 38 370 | 18.2 | 28.6 | 49.0 | 29.1 |
| H | Transport and storage | 2024 | 5 220 | 1.3 | 3.0 | 6.1 | 3.1 |
| F | Construction | 2024 | 25 390 | 4.4 | 12.4 | 27.1 | 13.1 |
| B | Mining and quarrying | 2023 | 685 | 22.0 | 49.9 | 93.6 | 49.8 (2022) |

Caveats: medians of firm ratios (SME-dominated, unweighted); total stocks (all stages)
over turnover, so for manufacturing they run 1.5-2x the German RHB-based days; sheets for
coke/refining (19) and pharma (21) were not found on the index page. Other 2024 sheets
(all 62 divisions, incl. 16, 17, 22, 23, 26-28, 30-33) follow the same URL pattern and
can be added the same way.

---------------------------------------------------------------------------------------

## 3. Energy and bulk feedstock stocks (physical evidence)

### 3.1 Crude oil at refineries

Definitions (Eurostat Statistics Explained, "Emergency oil stocks statistics"): emergency
stocks are the Directive 2009/119/EC obligation (at least 90 days of net imports or 61
days of inland consumption); commercial stocks are "stocks held by economic operators in
the national territory for their own operational and commercial needs, which therefore
can be considered available, in addition to the emergency stocks, in case of need".
Datasets: nrg_stk_oilm (tonnes, by product and holder), nrg_stk_oem (days equivalent).

EU totals, May 2025 (Statistics Explained): emergency stocks 108.6 Mt (crude 43.5,
gas/diesel oil 39.0, gasoline 10.4); commercial stocks 45.7 Mt; commercial stocks by
country: Netherlands 9.50 Mt, Germany 9.3 Mt, France 3.6 Mt (all products).

Crude oil by holder, May 2025, closing stocks (Eurostat API, nrg_stk_oilm, siec
O4100_TOT, thousand tonnes):

| Holder (stk_flow) | EU27 | Germany |
|---|---|---|
| Closing stock on national territory (STKCL_NAT) | 57 411 | 17 119 |
| held by stock-holding organisation (STKCL_NAT_SHO; DE = EBV) | 23 631 | 12 596 |
| held by government (STKCL_NAT_GOV) | 1 202 | 0 |
| other held on national territory = economic operators (STKCL_NAT_OTH) | 24 089 | 2 342 |
| of which commercial stocks of economic operators under the Directive (STKCL_EUE_NAT_CEO_DIR) | 15 025 | 2 342 |
| pipeline fill (STKCL_PF) | 1 239 | 100 |

Netherlands and Belgium: holder split confidential/missing in the API.

Flows for the denominator: Germany 2024 primary crude supply ("Primaeraufkommen von
Rohoel", imports + domestic) 85.40 Mt and total refinery feed ("Verarbeitungseinsatz")
102.29 Mt (BAFA, Amtliche Mineraloeldaten Dezember 2024, table 3; BAFA notes that the
publication is currently suspended for quality reasons). EU crude imports 2024: 471.3 Mt;
EU refinery output 543.7 Mtoe (Eurostat, "Oil and petroleum products - a statistical
overview", 2024 data).

Derived days of crude cover:

| Measure | Value |
|---|---|
| Germany, economic operators' crude (refiners, traders, tank farms) / primary crude supply | 2.34 / 85.4 x 365 = 10.0 days |
| Germany, same incl. EBV crude | 14.94 / 85.4 x 365 = 64 days (not operationally available to a given refinery; released by government decision, mostly cavern storage) |
| Germany, BAFA "Eigentumsendbestand Rohoel gesamt, Inland", Dec 2024 (all owners) | 15.38 Mt = 66 days of primary crude supply |
| EU27, economic operators' crude / crude imports | 24.09 / 471.3 x 365 = 18.7 days (upper bound: includes trader and tank-farm stocks and part of the obligation in countries without a central agency) |
| EU27, commercial stocks all products / refinery output | 45.7 / 543.7 x 365 = 31 days (held across the whole distribution chain, not at refineries) |

Reading for the model: a refinery's own crude cover is about 10 days (Germany, where the
EBV holds the entire obligation); 15-20 days is the upper bound from EU data. Product
stocks at refineries are of the same order (US: petroleum and coal products materials
and supplies = 6 days of shipments, section 5).

### 3.2 Coal at power plants

- Legal minimum for German reserve plants (Ersatzkraftwerkebereithaltungsgesetz, new
  section 50b(2) EnWG, Bundestag Drucksache 20/2356, 21 June 2022): operators must hold,
  on 1 November 2022/2023 and 1 February 2023/2024, fuel stocks sufficient "bei Einsatz
  von Kohle zur Erzeugung elektrischer Energie fuer 30 Kalendertage die
  Abgabeverpflichtungen an Elektrizitaet bei Betrieb der Anlage mit der maximal
  moeglichen Nettonennleistung zu decken" (10 calendar days for oil-fired plants);
  section 50b(3): the stocks must be stored at the plant site, or at a supplementary
  store from which transport to the site is guaranteed within ten calendar days.
  Explanatory memorandum: "Volllastbetrieb von 30 Tagen fuer Kohlekraftwerke und
  10 Tagen fuer Oelkraftwerke". The rule was time-limited (to 31 March 2024).
- Actual practice, July 2022 (heise online, 8 July 2022, quoting Steag): "An den meisten
  Kraftwerksstandorten selbst reicht der Kohlevorrat derzeit nur etwa fuer eine Woche
  Volllastbetrieb aus"; Steag had access to hard-coal stocks for about 30 days of
  full-load operation of its whole fleet, largely stored in Rotterdam, with a shortage of
  barges, wagons, locomotives and drivers to move them.
- Balance-sheet cross-check: German energy/water/waste sector RHB = 3.0 days of
  Materialaufwand (Table A), but Materialaufwand there is dominated by purchased
  electricity and gas for resale, so this does not measure coal cover.
- US benchmark (EIA, Today in Energy, 23 July 2025): 124 million short tons on site at
  power plants at end-June 2025 = "about 93 days' worth of fuel on-site" (days of burn =
  inventories / seasonal consumption rate). US plants are rail/mine-mouth supplied and
  stock far more than Rhine-supplied plants.

### 3.3 Iron ore and coking coal at integrated steelworks

- thyssenkrupp Steel Duisburg (Platts via Mining & Metal News, 12 August 2026, quoting a
  German distributor): "the Duisburg plant normally holds inventories sufficient for
  approximately one to two months of production". CFO Axel Hamann (13-14 August 2026):
  the company can adjust production and operating mode "so that we can work longer with
  the inventories we have". Press reports put the daily ore and coal flow from Rotterdam
  to Duisburg at about 50 000 t/day (abstract only; not verified in a primary source).
  Duisburg design capacity: about 11.7 Mt/y pig iron from four blast furnaces (Eurometal,
  17 July 2026).
- Engineering norm (IspatGuru, "Bulk material storage and storage yard machines"): "The
  capacity of the open pile storage normally ranges from 7 days to 45 days requirement of
  the consuming unit of the plant."
- Balance sheets: basic metals (24) non-finished stock 55 days of Materialaufwand (incl.
  WIP), basic metals + metal products RHB 36 days (Tables A, C); French metallurgy median
  total stocks 62 days of turnover (section 2.2).
- Input requirement (for converting days to tonnes): about 1 370 kg iron ore, 780 kg
  metallurgical coal and 270 kg limestone per tonne of crude steel via the blast-furnace
  route (abstract only, worldsteel-type figure).

### 3.4 Chemical feedstocks

- No published days-of-stock figure was found (VCI publishes tonnages, not stock cover).
  Balance sheets: chemicals + pharma RHB 30.7 days of Materialaufwand (2023; 25.9 in
  2019); chemicals (20) alone: non-finished stock 43 days, total inventories 49 days of
  turnover; French chemicals median total stocks 62 days of turnover.
- BASF Ludwigshafen (BASF site page "Logistik Rhein"): about 12 barges per day of about
  2 000 t each, roughly three quarters of them carrying raw materials; 40 % of goods at
  the site move by ship (VCI, 8 August 2026, Process). BASF and BfG operate a low-water
  early-warning system with up to six weeks lead time.
- Rhine 2026: Covestro (Dormagen) declared force majeure and Lanxess stopped a plant at
  Krefeld-Uerdingen for lack of raw materials in mid-August 2026, i.e. a few weeks after
  barge loads collapsed (press, 11-17 August 2026). This is consistent with on-site
  liquid-bulk cover of two to four weeks for the affected units, but no company has
  published a figure. 2018 analogue: German chemicals and pharmaceuticals production fell
  about 10 % between September and November 2018 (CNBC, 2019, abstract only).

### 3.5 Grain, oilseeds and compound feed

- Flour mill (Verband Deutscher Muehlen, site report Roland Mills West): 32 000 t grain
  silo capacity = "zwei Produktionswochen"; about 1 000 t of grain arrive per day, about
  80 % by water, "praktisch jeden Tag ein Schiff" (1 650 t per vessel). UK Flour Millers:
  mills "have limited storage capacity so rely on a constant supply of wheat".
- Oil mill C. Thywissen, Neuss (Wirtschaft und Industrie, 21 August 2026, quoting MD
  Dominik Baum): 2 200-2 300 t/day of oilseeds processed, about 90 % arriving by barge;
  the 12 000 t of extra storage built after 2018 is "eine Reichweite von gut fuenf Tagen";
  with shipping fully stopped the mill "koennte ... nach einer bis anderthalb Wochen nicht
  mehr produzieren".
- Compound feed (BLE, Bericht zur Markt- und Versorgungslage Futtermittel 2025): "Die
  Lagerkapazitaeten, sowohl fuer die Rohstoffe als auch fuer das fertige Mischfutter, bei
  den Mischfutterherstellern sind eher gering. Lagerkapazitaeten haben vor allem die
  Landwirte oder der angeschlossene Landhandel." Production is described as just-in-time
  (abstract only). Example plants: 200 000 t/y output with 20 000 t raw-material storage
  (about five weeks) (abstract only).
- Balance sheets: food and feed (10) non-finished stock 20 days of Materialaufwand,
  RHB for 10-12 = 18 days; French food industries median total stocks 18 days of turnover.
  Grain stocks are held upstream (farms, collectors, wholesale 46), not at processors.

### 3.6 Cement and aggregates

- Vendor/engineering sources only (no official statistics found): clinker silos are sized
  for 7-14 days of cement production (SRON, Flyer Steel Silo, The Cement Institute forum;
  one example 16.5 days); crushed-limestone pre-blending stockpiles of a few days
  (example 3.7 days); plants with an on-site quarry keep 7-14 days of limestone, plants
  depending on external supply 21-30 days; finished cement rarely more than a week
  (abstracts only; the Oxmaint page was not fetchable).
- Balance sheets: glass, ceramics and non-metallic minerals (23): non-finished stock
  73 days of Materialaufwand (incl. WIP), total inventories 66 days of turnover; the
  22-23 group RHB = 39 days. Imported fuels (petcoke, coal) at cement kilns are the
  Rhine-relevant input, not the quarried minerals.

---------------------------------------------------------------------------------------

## 4. Academic calibrations and surveys

### 4.1 Pichler, Pangallo, del Rio-Chanona, Lafond, Farmer (2020; 2022 JEDC)

- Model: each industry i keeps a target inventory n_i x (equilibrium use) of EVERY input;
  n_i is industry-specific but the same for all inputs of that industry ("Considering an
  input-specific target inventory would require generalizing n_i to a matrix", footnote).
  Inventory adjustment time tau = 10 days ("firms aim at filling most of their inventory
  gaps within two weeks", compared with tau = 6 in Inoue & Todo 2019 and 30 in Hallegatte
  2014); the adjustment time is found to be the most sensitive of the fixed parameters.
- Calibration in the JEDC version (arXiv 2102.09608, Appendix B "Inventory data and
  calibration"): ONS Annual Business Survey, 2-digit NACE, 2008-2018: "we take the simple
  average between beginning- and end-of year inventory stock levels; ... we calculate the
  ratio between this average and yearly turnover, and multiply this number by 365";
  exponentially weighted across years (weights 0.95^(2018-X)); aggregated to WIOD sectors;
  K64-66, O84 and T imputed with the service-sector average. "Inventories are much larger
  relative to sales in production, construction and trade, while they are generally lower
  in services". The per-industry values are shown only graphically (Figure 11, log scale
  1-100 days); they were not tabulated in the text and could not be read off reliably.
  The reproduction archive (Zenodo 10.5281/zenodo.5881855, 555 MB) contains the data.
- Earlier version (arXiv 2005.10585, "Production networks and epidemic spreading: How to
  restart the UK economy?", Appendix B): US BEA/NIPA data (tables 4BU1-4BU3 by stage of
  fabrication, 1BU/2BU trade inventories and sales, 5.8.6B other industries, 208 gross
  output), 2019Q4; n_i = inventories / monthly gross output x 30; ratios "remarkably
  stable ... varying by no more than 20 % in the last 10 years", taken as transferable
  across countries. The same BEA/Census stage-of-fabrication data underlie section 5.
- Note: both calibrations use TOTAL inventories (all stages) over sales, i.e. they are the
  analogue of "total inv. / Umsatz" in Table A (49-123 days for German manufacturing
  groups), not of the raw-material stock.

### 4.2 Inoue & Todo (2019, Nature Sustainability; RIETI DP 18-E-013) and (2020, PLoS ONE)

- Firm-level model on Japanese supplier-customer data; each firm holds an inventory of
  each input equal to n_i days of use; n_i is drawn per firm from a Poisson distribution;
  no sector variation; "for simplicity, the model assumes that even service sectors have
  the inventory mechanism".
- Calibration (RIETI DP, section 4): grid search of inventory size 1-20 days, stop day
  0-20, recovery ratio 0.005-0.100 against the monthly industrial production index after
  the 2011 Great East Japan earthquake: "The best parameters are 9 for the inventory size,
  6 for the stop day, and 0.025 for the recovery ratio" (i.e. Poisson mean 9 days; the
  order-adjustment parameter tau = 6 days). No balance-sheet source is cited.
- The companion paper on nation-wide network propagation (Inoue & Todo 2019, PLoS ONE
  14(3): e0213648) uses "the Poisson distribution with a mean of 15" and states "This
  parameter also requires empirical support, if it is possible".
- Inoue & Todo (2020, PLoS ONE, Tokyo lockdown): "we assume that firms aim to keep
  inventories for nine days of production on average", thirty draws of the Poisson targets;
  no sensitivity on the nine days.

### 4.3 Hallegatte (2008; 2012 WPS6047 / 2014 Risk Analysis)

- ARIO 2008 (Katrina): "In its initial version, the model has a one-month time step, and
  has no inventories" (WPS6047, section 3).
- ARIO-inventory (WPS6047 section 3.2, Table 2): "The target inventory measured in days
  of demand (n_ji); in the reference model version, this level is assumed to be 90 days of
  demand, except (i) in the non-stockable-goods sectors (utility and transport), in which
  it is three days; (ii) in the construction sector, in which it is infinite"; restoration
  time s = 30 days (1 day for non-stockable goods); heterogeneity parameter psi = 0.8.
  No data source is given for the 90 days. Sensitivity (section 4.3.2): losses fall with
  n; at n >= 120 days there are no forward ripple effects; "the modeled economy collapses
  if the initial and target inventories are only of 30 days".
- Guan et al. (2020, Nature Human Behaviour), a global ARIO variant: the Methods could not
  be fetched (login redirect); its inventory parameters are therefore not reported here.

### 4.4 Current DisruptSC setting (for reference)

`config/default.yaml`: `inventory_duration_targets` keyed on `sector_table['type']` of the
INPUT: default 30, utility 3, agriculture 15, manufacturing 30, service 90 (a coping
duration, not a stock), trade 30, transport 5; unit day; `inventory_restoration_time` 30
days. `load_inventories` (src/disruptsc/init_pipeline/agents.py) implements only
`definition: per_input_type`; import bundles get the share-weighted mean of their MRIO
composition. A buyer-keyed table therefore needs a new definition mode (see 6.4).

### 4.5 Surveys and working-capital studies

- DIHK / IHK survey of Rhine-corridor firms (29 July - 4 August 2026, n = 170): about a
  quarter of firms plan to adjust (raise) inventories, about a third plan to ship less by
  barge in future (see `validation_targets_2026_surveys.md`, rows 74-77). No days asked.
- ifo Business Survey: reports the share of manufacturers with material shortages (13.7 %
  in July 2026, 17.2 % in June, 5.8 % in January) and the stock-of-finished-goods
  assessment; it has no "days of inventory" variable. The harmonised EU Business and
  Consumer Survey (DG ECFIN) likewise asks only for a qualitative assessment of stocks of
  finished products. Eurostat SBS does not publish inventory levels.
- Hackett Group, 2025 European Working Capital Survey (1 000 largest European-headquartered
  non-financial companies, FY2024): Days Inventory Outstanding "jumped 4 % to 68.9 days -
  its highest level in a decade"; no industry table in the release.
- PwC Working Capital Study 25/26 (abstract only; pages blocked): EU average DIO of
  90.2 days in 2024 "for the most cash-intensive sectors", vs 68.6 in North America and
  62.8 in the UK; DIO in Western economies up 13.6 % (9.0 days) to a ten-year high.
- Efficio, Working Capital Trends in Europe 2023/24: European DIO up 4.5 days in 2023
  (consumer goods +15, electronic equipment +13, pharmaceuticals +9, metals and minerals
  -5); levels not given.
- Caveat for all DIO studies: total inventories over cost of sales, large listed firms.

---------------------------------------------------------------------------------------

## 5. US Census M3 benchmark (materials-and-supplies inventories by industry)

Source: U.S. Census Bureau, Manufacturers' Shipments, Inventories, and Orders (M3),
"Monthly Full Report ... July 2026" (released 2 September 2026), Table 1 (shipments),
Table 4 (inventories), Table 6 (inventories by stage of fabrication: materials and
supplies, work in process, finished goods), Table 7 (inventory/shipments ratio). Values
are seasonally adjusted July 2026 (preliminary), millions of dollars; days = value /
monthly shipments x 30.4. The last column converts days of shipments to approximate days
of material consumption using the German material-cost shares of turnover from Table A
(food 0.67, chemicals 0.59, petroleum about 0.85 assumed, metals 0.63, machinery 0.56,
electronics/electrical 0.57, transport equipment 0.71, wood/paper/printing 0.57,
minerals/plastics 0.54, textiles 0.57); it is an approximation.

| Industry (NAICS group) | Materials & supplies | Shipments (month) | Total inventories | M&S share of inventories | Inventory / shipments (Table 7) | M&S in days of shipments | approx. M&S in days of material cost |
|---|---|---|---|---|---|---|---|
| All manufacturing | 363 362 | 658 833 | 966 871 | 0.38 | 1.47 | 16.8 | ~26 |
| Durable goods | 231 569 | 334 609 | 604 669 | 0.38 | 1.81 | 21.0 | ~35 |
| Wood products | 8 012 | 13 923 | 18 530 | 0.43 | 1.33 | 17.5 | ~31 |
| Nonmetallic mineral products | 8 452 | 14 773 | 20 758 | 0.41 | 1.41 | 17.4 | ~32 |
| Primary metals | 23 536 | 31 273 | 51 987 | 0.45 | 1.66 | 22.9 | ~36 |
| Fabricated metal products | 29 232 | 43 877 | 75 315 | 0.39 | 1.72 | 20.3 | ~32 |
| Machinery | 48 304 | 43 778 | 105 561 | 0.46 | 2.41 | 33.5 | ~60 |
| Computers and electronic products | 32 389 | 34 278 | 68 586 | 0.47 | 2.00 | 28.7 | ~50 |
| Electrical equipment, appliances | 14 294 | 18 511 | 29 561 | 0.48 | 1.60 | 23.5 | ~41 |
| Transportation equipment | 50 464 | 111 605 | 191 377 | 0.26 | 1.71 | 13.7 | ~19 |
| Furniture | 5 624 | 7 699 | 10 760 | 0.52 | 1.40 | 22.2 | ~40 |
| Nondurable goods | 131 793 | 324 224 | 362 202 | 0.36 | 1.12 | 12.4 | ~19 |
| Food products | 30 484 | 90 876 | 74 021 | 0.41 | 0.81 | 10.2 | ~15 |
| Beverage and tobacco | 7 271 | 18 481 | 34 764 | 0.21 | 1.88 | 12.0 | ~24 |
| Textile products | 1 641 | 1 851 | 3 696 | 0.44 | 2.00 | 27.0 | ~47 |
| Apparel | 761 | 812 | 1 985 | 0.38 | 2.44 | 28.5 | ~50 |
| Leather | 353 | 416 | 1 180 | 0.30 | 2.84 | 25.8 | ~45 |
| Paper products | 10 738 | 19 324 | 20 812 | 0.52 | 1.08 | 16.9 | ~30 |
| Printing | 4 433 | 7 363 | 7 676 | 0.58 | 1.04 | 18.3 | ~32 |
| Petroleum and coal products | 14 204 | 69 849 | 47 626 | 0.30 | 0.68 | 6.2 | ~7 |
| Chemical products | 44 779 | 87 081 | 130 893 | 0.34 | 1.50 | 15.6 | ~26 |
| Plastics and rubber products | 15 600 | 26 175 | 36 022 | 0.43 | 1.38 | 18.1 | ~34 |

Caveats: US logistics (rail, domestic feedstocks) differ from Rhine-supplied plants; M&S
excludes materials already in process; the table is a monthly snapshot (July 2026);
the industry-to-ICIO mapping is by NAICS 3-digit group. Agreement with the German RHB
days is good where both exist (food 15 vs 18; chemicals 26 vs 31; primary metals 36 vs
36; machinery 60 vs 59; transport equipment 19 vs 18; electronics 41-50 vs 70; paper 30
vs 33), which supports using the German values for the EU scope.

---------------------------------------------------------------------------------------

## 6. Mapping to the 50 ICIO sectors and recommended table

### 6.1 Source-to-ICIO mapping

| ICIO code | ICIO sector | Bundesbank Table A group | Bundesbank Table C division | FIBEN sheet | Census M3 group | Physical evidence |
|---|---|---|---|---|---|---|
| A01 | Agriculture | not covered | A | (A sheet exists, not fetched) | - | BLE: feed stocks held on farms |
| B05-B09 (as one or several sectors) | Mining and quarrying | in Produzierendes Gewerbe | B | B (2023) | - | - |
| C10T12 | Food, beverages, tobacco | 10-12 | 10, 11 | 10, 11 | Food; Beverage & tobacco | mills, oil mill, feed plants |
| C13T15 | Textiles, apparel, leather | 13-15 | 13 | - | Textile products, Apparel, Leather | - |
| C16 | Wood | 16-18 | 16 | - | Wood products | - |
| C17_18 | Paper, printing | 16-18 | 17, 18 | - | Paper, Printing | - |
| C19 | Coke, refined petroleum | manufacturing total only | not separate | - | Petroleum & coal products | Eurostat/BAFA crude stocks |
| C20 | Chemicals | 20-21 | 20 | 20 | Chemical products | BASF, Covestro, Lanxess 2026 |
| C21 | Pharmaceuticals | 20-21 | 21 | - | (in chemicals) | - |
| C22 | Rubber and plastics | 22-23 | 22 | - | Plastics & rubber | - |
| C23 | Non-metallic minerals | 22-23 | 23 | - | Nonmetallic minerals | cement clinker/limestone/fuels |
| C24A | Iron and steel | 24-25 | 24 | 24 | Primary metals | Duisburg 1-2 months; 7-45 d norm |
| C24B | Non-ferrous metals | 24-25 | 24 | 24 | Primary metals | - |
| C25 | Fabricated metals | 24-25 | 25 | 25 | Fabricated metals | - |
| C26 | Computers, electronics | 26-27 | 26 | - | Computers & electronics | - |
| C27 | Electrical equipment | 26-27 | 27 | - | Electrical equipment | - |
| C28 | Machinery | 28 | 28 | - | Machinery | - |
| C29 | Motor vehicles | 29-30 | 29 | 29 | Transportation equipment | - |
| C301 | Ships and boats | 29-30 | 30 | - | Transportation equipment | - |
| C302T309 | Other transport equipment | 29-30 | 30 | - | Transportation equipment | - |
| C31T33 | Furniture, other, repair | not separate | 31, 32, 33 | - | Furniture, Miscellaneous | - |
| D | Electricity, gas, steam | D-E | D | - | - | EKBG 30 d; Steag 1 week; EIA 93 d (US) |
| E | Water, sewerage, waste | D-E | E | - | - | - |
| F | Construction | F | F (76, 82, 84, 86) | F | - | - |
| G | Wholesale and retail | G (45, 46, 47) | 45, 46, 47 | 46, 47 | (BEA trade tables in Pichler 2020) | - |
| H49-H53 | Transport and storage | H | H, 49, 52 | H | - | fuel tanks (no data) |
| I | Accommodation, food | not covered | I | - | - | - |
| J58T60, J61, J62_63 | Media, telecom, IT | J | J, 61, 62-63 | - | - | - |
| K | Finance | not covered | not covered | - | - | - |
| L | Real estate | not covered | L | - | - | - |
| M, N | Professional, admin services | "Unternehmensdienstleistungen" | M-N | - | - | - |
| O, P, Q, R, S, T | Public, education, health, arts, other, households | not covered | P-Q aggregate, 86 | - | - | - |

### 6.2 Recommended table: buying industry -> days of raw-material (goods-input) inventory

"Days" = days of consumption of purchased GOODS inputs (all input sectors A-F) at the
buyer's equilibrium use, i.e. the quantity the model's `inventory_duration_target` expects.
Non-storable inputs (electricity, gas, water) and service inputs are handled by the
overrides in 6.3, not by this column. "Lean" gives the 2019 (pre-pandemic) German value
where available, for sensitivity runs.

| Buying industry (ICIO) | Recommended days | Lean (2019) | Grade | Basis (data-based unless stated) |
|---|---|---|---|---|
| A01 Agriculture | 30 | - | C | German ratio series A: non-finished stock 49 d of Materialaufwand incl. growing crops/livestock (WIP); feed/fertiliser stocks sit on farms (BLE). Partly assumed. |
| B05-B09 Mining and quarrying | 30 | - | C | Ratio series B: 74 d incl. WIP; FIBEN B median 50 d of turnover; RHB not split. Partly assumed. |
| C10T12 Food, beverages, tobacco | 18 | 18 | A | Bundesbank 10-12 RHB 18.4 d (2019: 17.7); ratio series 10: 20 d; FIBEN 10 median 18 d; Census food ~15 d; mills 14 d, oil mill 5-10 d, feed just-in-time. Beverages are higher (42 d). |
| C13T15 Textiles, apparel, leather | 40 | 35 | A | Bundesbank 13-15 RHB 41.9 d (2019: 34.9); Census textiles/apparel ~45-50 d. |
| C16 Wood | 33 | 28 | B | Bundesbank 16-18 RHB 32.9 d (2019: 27.5); ratio series 16: 71 d incl. WIP; Census wood ~31 d. |
| C17_18 Paper, printing | 33 | 28 | B | Same 16-18 group; ratio series 17: 45 d, 18: 43 d incl. WIP; Census paper ~30 d, printing ~32 d. |
| C19 Coke, refined petroleum | 12 | - | B | German refiners'/operators' crude = 10 d of primary supply (Eurostat holder split, May 2025; BAFA 2024 flows); EU27 operators 18.7 d (upper bound); Census petroleum M&S ~7 d. Strategic (EBV/CSE) stocks excluded. |
| C20 Chemicals | 30 | 26 | A | Bundesbank 20-21 RHB 30.7 d (2019: 25.9); ratio series 20: 43 d incl. WIP; FIBEN 20 median 62 d of turnover; Census chemicals ~26 d. Bulk liquid feedstocks at river sites are shorter (see 6.3). |
| C21 Pharmaceuticals | 60 | - | B | Ratio series 21: 82 d non-finished stock (incl. WIP), 68 d total/turnover; 20-21 group RHB 31 d is dominated by chemicals. |
| C22 Rubber and plastics | 40 | 31 | B | Bundesbank 22-23 RHB 38.9 d (2019: 30.9); ratio series 22: 59 d incl. WIP; Census plastics ~34 d. |
| C23 Non-metallic minerals | 30 | 31 | B | 22-23 group RHB 38.9 d; ratio series 23: 73 d incl. WIP; Census nonmetallic ~32 d; cement: clinker 7-14 d, quarry minerals continuous, imported fuels 21-30 d (vendor sources). Weighted towards purchased fuels/additives: 30. |
| C24A Iron and steel | 40 | 31 | B | Bundesbank 24-25 RHB 36.4 d (2019: 31.1); ratio series 24: 55 d incl. WIP; FIBEN 24 median 62 d; Duisburg "one to two months" (Platts); yard design 7-45 d; Census primary metals ~36 d. |
| C24B Non-ferrous metals | 40 | 31 | C | Same sources as C24A, no separate split. |
| C25 Fabricated metals | 36 | 31 | B | Bundesbank 24-25 RHB 36.4 d; ratio series 25: 128 d incl. WIP (job-shop WIP); FIBEN 25 median 41 d; Census fabricated ~32 d. |
| C26 Computers, electronics, optics | 60 | 37 | B | Bundesbank 26-27 RHB 70.3 d in 2023 vs 36.8 in 2019 (chip-shortage stockpiles); ratio series 26: 125 d incl. WIP; Census computers ~50 d. 60 = between 2019 and 2023. |
| C27 Electrical equipment | 60 | 37 | B | Same 26-27 group; ratio series 27: 142 d incl. WIP; Census electrical ~41 d. |
| C28 Machinery | 55 | 43 | A | Bundesbank 28 RHB 58.7 d (2019: 42.8); Census machinery ~60 d; ratio series 192 d incl. WIP (long cycles). |
| C29 Motor vehicles | 18 | 13 | A | Bundesbank 29-30 RHB 18.4 d (2019: 12.5); ratio series 29: 26 d incl. WIP; FIBEN 29 median 60 d of turnover; Census transport equipment ~19 d. |
| C301 Ships and boats | 60 | - | D | Ratio series 30: 345 d incl. WIP (multi-year builds); RHB not split. Assumed. |
| C302T309 Other transport equipment | 60 | - | D | As C301. Assumed. |
| C31T33 Furniture, other manufacturing, repair | 40 | - | C | Ratio series 31: 57 d, 32: 77 d, 33: 213 d incl. WIP; Census furniture ~40 d. |
| D Electricity, gas, steam | 20 (coal 30, oil 10, gas 2) | - | B | EKBG minimum 30 d on site for coal reserve plants, 10 d oil; Steag 2022: ~1 week on site, 30 d fleet-wide incl. Rotterdam; gas = pipeline/storage operators, not plant stock; Bundesbank D-E RHB 3 d (of a denominator dominated by energy purchases for resale). Sector value 20 = blend; use the input overrides. |
| E Water, sewerage, waste | 10 | - | C | Ratio series E: 22 d non-finished stock, 20 d total/turnover; RHB small. |
| F Construction | 10 | 10 | A | Bundesbank F RHB 8.9 d (stable 8-10 d since 2011); FIBEN F median 12-14 d of turnover; the 179 bn EUR WIP is unfinished buildings, not inputs. |
| G Wholesale and retail | 5 | 5 | B | Bundesbank G RHB 2.2 d of Materialaufwand (45: 1.4, 46: 2.7, 47: 1.4); the goods-for-resale stock (29-56 d of turnover) is not an intermediate input under the ICIO margin treatment - see 6.4. |
| H49-H53 Transport and storage | 7 | 6 | B | Bundesbank H RHB 7.3 d (2019: 6.1) - fuel, tyres, spares; ratio series 49: 25 d incl. WIP, 52: 8 d; FIBEN H median 3 d of turnover. |
| I Accommodation and food | 5 | - | B | Ratio series I: 7 d non-finished stock, 4.5 d total/turnover. |
| J58T60 Publishing, media | 10 | - | C | Bundesbank J RHB 2.2 d; ratio series J: 21 d incl. WIP. |
| J61 Telecommunications | 10 | - | C | Ratio series 61: 28 d incl. WIP, 19 d total/turnover. |
| J62_63 IT services | 10 | - | C | Ratio series 62-63: 18 d incl. WIP, 11 d total/turnover. |
| K Finance and insurance | 7 | - | D | No balance-sheet data (banks excluded); goods inputs negligible. Assumed. |
| L Real estate | 10 | - | D | Ratio series L: 208 d incl. property WIP; goods inputs negligible. Assumed. |
| M Professional services | 10 | - | C | Bundesbank M-N RHB 6.2 d; ratio series 113 d incl. unbilled WIP. |
| N Administrative services | 10 | - | C | As M. |
| O Public administration | 15 | - | D | No data. Assumed (stores of supplies). |
| P Education | 15 | - | D | Ratio series P-Q aggregate 28 d incl. WIP, 9 d total/turnover. Assumed. |
| Q Health and social work | 20 | - | C | Ratio series 86: 40 d non-finished stock, 13 d total/turnover (drugs, consumables). |
| R Arts and recreation | 7 | - | D | Assumed. |
| S Other services | 7 | - | D | Assumed. |
| T Households as employers | 7 | - | D | Assumed. |

Data-based rows (A/B): C10T12, C13T15, C16, C17_18, C19, C20, C21, C22, C23, C24A, C25,
C26, C27, C28, C29, D, F, G, H49-H53, I. Indirect (C): A01, B05-B09, C24B, C31T33, E,
J58T60, J61, J62_63, M, N, Q. Assumed (D): C301, C302T309, K, L, O, P, R, S, T.

### 6.3 Input-type overrides within the buying industry (where the data allow)

| Buyer | Input | Days | Grade | Evidence |
|---|---|---|---|---|
| D | B05 coal (incl. imported coal bundles) | 30 (lean: 7) | B | EKBG 30-day rule; Steag 2022 one week on site. |
| D | B06 gas, D (own sector) | 2 | B | Pipeline supply; Hallegatte non-stockable convention 3 d. |
| D | C19 fuel oil | 10 | B | EKBG 10-day rule for oil plants. |
| C19 | B06 crude oil (and crude import bundles) | 10-12 | B | Section 3.1. |
| C24A | B07 iron ore, B05 coking coal | 40 (range 30-60) | B | Duisburg 1-2 months; design 7-45 d. |
| C20 | C19 / B06 liquid feedstocks (naphtha, LPG) | 14 | C | 2026 force-majeure timing; no published figure. Balance-sheet average for all C20 inputs is 30. |
| C10T12 | A01 grain and oilseeds | 10 | B | Mills 14 d, oil mill 5-10 d; feed plants just-in-time; stocks sit upstream in A01/G46. |
| C23 | B05 coal / C19 petcoke | 25 | C | Vendor figures 21-30 d for externally supplied fuels. |
| H49 | C19 fuel | 7 | B | Bundesbank H RHB 7 d (operating supplies). |
| any buyer | D electricity/gas/steam, E water | 1-2 | B | Non-storable; Bundesbank D-E stocks 3 d; Hallegatte 3 d. |
| any buyer | service inputs (G-T) | keep the model's coping duration (currently 90 d), not an inventory | - | Out of scope of this dossier. |

### 6.4 Implementation and modelling notes

- `load_inventories` only implements `definition: per_input_type`. A `per_buying_sector`
  mode (values keyed on the buyer's ICIO code, with an optional `overrides` block keyed on
  (buyer, input sector or input type)) is needed; import bundles should use the buyer's
  value, with the same overrides applied to the bundle's MRIO composition.
- Trade (G): in the ICIO, wholesale and retail output is the margin and goods bought for
  resale are not intermediate inputs of G, so the 30-56 days of goods-for-resale stock in
  Table A is not represented by G's input inventories. It is the buffer between producers
  and households that the model's household inventory scheme (default 7 d for goods)
  proxies; wholesale (29 d) plus retail (40 d) finished-goods stocks in days of their own
  turnover suggest a consumer-goods pipeline of several weeks. Worth a separate decision;
  not changed here.
- Denominator conversion: the model's target multiplies the buyer's equilibrium use of
  each input; Bundesbank RHB/Materialaufwand is exactly the value-weighted mean of that
  ratio across the buyer's inputs (stocks and flows both at cost), so the recommended days
  apply to every goods input unless overridden.
- Sensitivity axis: use "Lean (2019)" values as the low case and Table C non-finished
  stock (incl. WIP) as the high case; the 2023 Bundesbank values are the central case.

---------------------------------------------------------------------------------------

## 7. Gaps and next steps

1. BACH R51 by country and NACE division (requires free registration on
   bach.banque-france.fr): would give AT/BE/FR/IT/ES/PL/PT medians on the same
   turnover basis as FIBEN; not retrieved here.
2. Destatis Kostenstrukturerhebung (Fachserie 4 Reihe 4.3) publishes "Verbrauch an Roh-,
   Hilfs- und Betriebsstoffen" separately from purchased services by WZ division; using it
   as the denominator instead of Materialaufwand would remove the downward bias noted in
   1.1 and give C19, C21, C24, C25, C26, C27, C30 separately.
3. ONS Annual Business Survey inventory and turnover by 2-digit SIC (the Pichler et al.
   source) and the Zenodo archive of Pichler et al. (2022) for their exact n_i values.
4. Coke/refining (C19) is absent from all balance-sheet tables above; the physical
   Eurostat/BAFA days (10-19) are the only sector-specific evidence.
5. No European statistic separates raw-material stocks by input; the overrides in 6.3
   rest on regulation (coal), physical stock data (crude) and company statements
   (steel, oilseeds, grain, chemicals).
6. Chemical feedstock cover at Rhine sites (BASF, Covestro, Lanxess, Evonik): company
   statements give timing (weeks) but no days figure; VCI has no inventory statistic.

---------------------------------------------------------------------------------------

## 8. Sources

Bundesbank
- Deutsche Bundesbank, Statistische Fachreihe "Jahresabschlussstatistik (Hochgerechnete
  Angaben)", Dezember 2025 (data 1997-2024):
  https://www.bundesbank.de/resource/blob/827826/5339ba185ff3e7ba37087b692a65ef74/472B63F073F071307366337C94F8C870/1-0-jahresabschlussstatistik-hochgerechnete-angaben-data.pdf
- Deutsche Bundesbank, Statistische Fachreihe "Jahresabschlussstatistik (Verhaeltniszahlen
  - vorlaeufig)", Mai 2026 (data 2023/2024):
  https://www.bundesbank.de/resource/blob/827830/319fc1b7d223d1ea29b08af5527f8138/mL/3-0-jahresabschlussstatistik-verhaeltniszahlen-vorlaeufig-data.pdf
- Deutsche Bundesbank, Monatsbericht Dezember 2023, "Ertragslage und
  Finanzierungsverhaeltnisse deutscher Unternehmen 2022":
  https://www.bundesbank.de/resource/blob/920564/8b23a472a652dfc2579009ba9ee9e2b5/mL/2023-12-ertragslage-data.pdf
- Deutsche Bundesbank, Monatsbericht Dezember 2025, "Ertragslage und
  Finanzierungsverhaeltnisse deutscher Unternehmen im Jahr 2024" (web article, not
  fetched in full):
  https://publikationen.bundesbank.de/publikationen-de/berichte-studien/monatsberichte/monatsbericht-dezember-2025-972182?article=ertragslage-und-finanzierungsverhaeltnisse-deutscher-unternehmen-im-jahr-2024-972190
- Deutsche Bundesbank, Erlaeuterungen "Verhaeltniszahlen aus Jahresabschluessen deutscher
  Unternehmen 2015 bis 2016" (definitions, Mai 2019):
  https://www.bundesbank.de/resource/blob/803472/1ab235f820eb3b66ebc392368cc295f9/mL/erlaeuterungen-verhaeltniszahlen-aus-jahresabschluessen-deutscher-unternehmen-data.pdf
- Bundesbank overview page "Unternehmensabschluesse":
  https://www.bundesbank.de/de/statistiken/unternehmen-und-private-haushalte/unternehmensabschluesse-772968

BACH / Banque de France
- ECCBSO, BACH User Guide Summary, January 2022:
  https://www.eccbso.org/system/files/inline-files/BACH_Summary_Userguide.pdf
- BACH Working Group, "The Bank for the Accounts of Companies Harmonized (BACH) database",
  ECB Statistics Paper Series No 11, 2015: https://www.ecb.europa.eu/pub/pdf/scpsps/ecbsp11.en.pdf
- BACH database (login required): https://www.bach.banque-france.fr/?lang=en
- ECCBSO databases page: https://www.eccbso.org/wba/databases
- Banque de France, Fascicules d'indicateurs sectoriels (index, methodology):
  https://www.banque-france.fr/fr/publications-et-statistiques/statistiques/fascicules-dindicateurs-sectoriels
  https://www.banque-france.fr/system/files/2025-11/methodologie-fascicules-sectoriels.pdf
- 2024 sheets (published 2025-11): industrie manufacturiere C, industries alimentaires 10,
  boissons 11, industrie chimique 20, metallurgie 24, produits metalliques 25, automobile
  29, commerce de gros 46, commerce de detail 47, transport-entreposage H, construction F:
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-industrie-manufacturiere-C-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-industries-alim-10-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-boissons-11-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-industrie-chimique-20-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-metallurgie-24-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-prod-metal-25-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-industrie-automobile-29-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-commerce-gros-46-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-commerce-detail-47-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-transport-entreposage-H-2024.pdf
  https://www.banque-france.fr/system/files/2025-11/fascicule-sectoriel-construction-F-2024.pdf
- 2023 sheets (published 2024-12): C, 47, H, F, B:
  https://www.banque-france.fr/system/files/2024-12/fascicule-sectoriel-industrie-manufacturiere-C-2023.pdf
  https://www.banque-france.fr/system/files/2024-12/fascicule-sectoriel-commerce-detail-47-2023.pdf
  https://www.banque-france.fr/system/files/2024-12/fascicule-sectoriel-transport-entreposage-H-2023.pdf
  https://www.banque-france.fr/system/files/2024-12/fascicule-sectoriel-construction-F-2023.pdf
  https://www.banque-france.fr/system/files/2024-12/fascicule-sectoriel-industrie-extractive-B-2023.pdf

Energy and bulk stocks
- Eurostat, Statistics Explained, "Emergency oil stocks statistics" (data to May 2025):
  https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Emergency_oil_stocks_statistics
- Eurostat API, nrg_stk_oilm (crude oil by holder, May 2025), e.g.
  https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_stk_oilm?format=JSON&lang=EN&geo=DE&time=2025-05&siec=O4100_TOT
  and geo=EU27_2020
- Eurostat, Statistics Explained, "Oil and petroleum products - a statistical overview"
  (2024 data): https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Oil_and_petroleum_products_-_a_statistical_overview
- BAFA, Amtliche Mineraloeldaten fuer die Bundesrepublik Deutschland, Dezember 2024
  (report of 16 July 2025):
  https://www.bafa.de/SharedDocs/Downloads/DE/Energie/Mineraloel/moel_amtliche_daten_2024_12.pdf?__blob=publicationFile&v=3
- Deutscher Bundestag, Drucksache 20/2356 (Ersatzkraftwerkebereithaltungsgesetz, 21 June
  2022), section 50b EnWG-E: https://dserver.bundestag.de/btd/20/023/2002356.pdf
- Bundesnetzagentur, EKBG page: https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Kohleausstieg/EKBG/artikel.html
- heise online, "Kohleverstromung stellt Kraftwerksbetreiber vor grosse
  Herausforderungen", 8 July 2022:
  https://www.heise.de/news/Kohleverstromung-stellt-Kraftwerksbetreiber-vor-grosse-Herausforderungen-7165955.html
- EIA, Today in Energy, "Coal-fired power plants are well-stocked this year", 23 July 2025:
  https://www.eia.gov/todayinenergy/detail.php?id=65787
- Mining & Metal News, "Low river water threatens steel supplies to European mills",
  12 August 2026 (Platts): https://www.miningmetalnews.com/20260812/3499/low-river-water-threatens-steel-supplies-european-mills
- Eurometal, "German steelmaker thyssenkrupp reduces production when low Rhine water
  levels disrupt materials supplies", 17 July 2026:
  https://eurometal.net/german-steelmaker-thyssenkrupp-reduces-production-when-low-rhine-water-levels-disrupt-materials-supplies/
- Eurometal, "Thyssenkrupp monitors Rhine levels as steel logistics face strain",
  14 August 2026: https://eurometal.net/thyssenkrupp-monitors-rhine-levels-as-steel-logistics-face-strain/
- Yahoo Finance/AFP, "German steel giant Thyssenkrupp weighs options as Rhine drops",
  13 August 2026: https://finance.yahoo.com/energy/articles/german-steel-giant-thyssenkrupp-weighs-100337641.html
- IspatGuru, "Bulk Material Storage and Storage Yard Machines":
  https://www.ispatguru.com/bulk-material-storage-and-storage-yard-machines/
- BASF, "Logistik Rhein" (Ludwigshafen site page):
  https://www.basf.com/global/de/who-we-are/organization/locations/europe/german-sites/ludwigshafen/the-site/site-logistics/lebensader-rhein/logistik-rhein
- Process (Vogel), "Niedrigwasser im Rhein: Chemiebranche warnt vor Engpaessen",
  8 August 2026: https://www.process.vogel.de/niedrigwasser-rhein-chemiebranche-warnt-lieferketten-a-50f436429915c42a1bb2789625089d1d/
- Logistik Heute, "Chemielogistik: Wie BASF dem Niedrigwasser am Rhein trotzt":
  https://logistik-heute.de/news/chemielogistik-wie-basf-dem-niedrigwasser-am-rhein-trotzt-37696.html
- onvista/dpa, "BASF drosselt wegen Rhein-Niedrigwasser erste Anlagen", 17 August 2026
  and "Industrie warnt: Extrem-Niedrigwasser bringt Lieferketten an Grenzen", 11 August
  2026 (Covestro, Lanxess, Evonik statements; abstracts only):
  https://www.onvista.de/news/2026/08-17-basf-lieferengpaesse-bei-einigen-produkten-wegen-rhein-niedrigwasser-0-20-26543800
  https://www.onvista.de/news/2026/08-11-industrie-warnt-extrem-niedrigwasser-bringt-lieferketten-an-grenzen-0-20-26541908
- Verband Deutscher Muehlen, "Muehlenreportage: Besuch einer Muehle in Westfalen":
  https://www.muehlen.org/technik/moderne-muehle/muehlenreportage-besuch-einer-muehle-in-westfalen
- UK Flour Millers, "Transport and storage": https://ukflourmillers.org/transportstorage
- Wirtschaft und Industrie, "Niedrigwasser am Rhein: Oelmuehle Thywissen kaempft um
  Rohstoffe", 21 August 2026: https://www.wirtschaft-und-industrie.de/niedrigwasser-am-rhein-oelmuehle-thywissen-kaempft-um-rohstoffe/
- BLE, "Bericht zur Markt- und Versorgungslage Futtermittel 2025":
  https://www.ble.de/SharedDocs/Downloads/DE/BZL/Daten-Berichte/Futter/2025BerichtFutter.pdf?__blob=publicationFile&v=2
- Cement storage (vendor/engineering pages, abstracts only): SRON clinker silo
  https://www.sronsilo.com/silo-systems/silo-storage-system/silo-system/clinker-silo.html ;
  The Cement Institute forum, "Basic cement plant layout"
  https://thecementinstitute.com/community/main-forum/basic-cement-plant-layout/ ;
  Oxmaint, "Raw material inventory optimization in cement manufacturing"
  https://oxmaint.com/industries/cement-plant/raw-material-inventory-optimization-cement

Academic
- Pichler, A., Pangallo, M., del Rio-Chanona, R. M., Lafond, F., Farmer, J. D. (2022),
  "Forecasting the propagation of pandemic shocks with a dynamic input-output model",
  Journal of Economic Dynamics and Control 144, 104527, doi:10.1016/j.jedc.2022.104527;
  working-paper version "In and out of lockdown ..." arXiv:2102.09608:
  https://arxiv.org/pdf/2102.09608 ; reproduction data: https://zenodo.org/records/5881855
- Pichler, A. et al. (2020), "Production networks and epidemic spreading: How to restart
  the UK economy?", arXiv:2005.10585: https://arxiv.org/pdf/2005.10585
- Inoue, H., Todo, Y. (2019), "Firm-level propagation of shocks through supply-chain
  networks", Nature Sustainability 2, 841-847, doi:10.1038/s41893-019-0351-x; RIETI
  Discussion Paper 18-E-013: https://www.rieti.go.jp/jp/publications/dp/18e013.pdf
- Inoue, H., Todo, Y. (2019), "Propagation of negative shocks across nation-wide firm
  networks", PLoS ONE 14(3): e0213648: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213648
- Inoue, H., Todo, Y. (2020), "The propagation of economic impacts through supply chains:
  The case of a mega-city lockdown to prevent the spread of COVID-19", PLoS ONE 15(9):
  e0239251: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239251
- Hallegatte, S. (2012), "Modeling the roles of heterogeneity, substitution, and
  inventories in the assessment of natural disaster economic costs", World Bank Policy
  Research Working Paper 6047 (published as Risk Analysis 34(1), 152-167, 2014,
  doi:10.1111/risa.12090): https://documents1.worldbank.org/curated/en/410441468142479058/pdf/WPS6047.pdf
- Hallegatte, S. (2008), "An adaptive regional input-output model and its application to
  the assessment of the economic cost of Katrina", Risk Analysis 28(3), 779-799 (no
  inventories; cited via WPS6047).
- Guan, D. et al. (2020), "Global supply-chain effects of COVID-19 control measures",
  Nature Human Behaviour 4, 577-587 (not fetched): https://www.nature.com/articles/s41562-020-0896-8

Surveys and working capital
- DIHK/IHK Rhine survey, 29 July - 4 August 2026 (n = 170): see
  `studies/rhine2026/evidence/update_20260903_supply_chain_damage.md` and
  https://www.rundschauduisburg.de/2026/08/08/ihks-veroeffentlichen-umfrage-zu-niedrigwasser-auswirkungen
- ifo Institut, Konjunkturumfrage, "Materialversorgung verbessert sich leicht", 31 July
  2026: https://www.ifo.de/fakten/2026-07-31/materialversorgung-verbessert-sich-leicht
- The Hackett Group, "2025 Working Capital Survey: Europe Shows Deterioration in Cash
  Conversion Cycle ...": https://www.thehackettgroup.com/2025-europe-working-capital-survey-cash-cycle-deterioration/
- PwC UK, Working Capital Study 25/26 (page returned HTTP 403; figures from search
  abstract): https://www.pwc.co.uk/services/value-creation/insights/working-capital-study.html
- Efficio, "Working Capital Trends in Europe: 2023/2024 Report":
  https://www.efficioconsulting.com/en-gb/resources/reports/working-capital-trends-in-europe-2023-report/

US Census
- U.S. Census Bureau, Manufacturers' Shipments, Inventories, and Orders (M3), Monthly Full
  Report, July 2026 (released 2 September 2026): https://www.census.gov/manufacturing/m3/prel/pdf/s-i-o.pdf ;
  definitions: https://www.census.gov/manufacturing/m3/definitions/index.html

DisruptSC
- `config/default.yaml` (inventory_duration_targets), `src/disruptsc/params.py`,
  `src/disruptsc/init_pipeline/agents.py` (`load_inventories`).
