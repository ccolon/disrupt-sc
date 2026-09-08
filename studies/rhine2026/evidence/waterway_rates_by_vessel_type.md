# Normal-water waterway freight rates and operator costs by vessel type: evidence dossier (Rhine)

Compiled 8 September 2026 for the whole-EU DisruptSC Rhine study. Purpose: document, per vessel
type / CEMT class and cargo segment, the NORMAL-WATER freight-rate levels (market prices) and the
operator cost levels (what a vessel costs to run) on Rhine lanes, so that the single waterway cost
of the model (`0.010 USD/tkm` plus transfer costs; see `README.md` and the 7 Sep note in the run
log) can be replaced, if the team decides so, by a per-cargo rate set. Nothing in the model was
changed; section 6.3 is a suggestion only.

Tags. [C] official statistics, primary agency/consultant report or primary company statement;
[R] press report or single secondary source; [S] seen only in a search-engine summary (page not
opened); [E] my own estimate or arithmetic (what it rests on is stated each time). Every figure
is labelled COST (operator, ex-VAT) or RATE (market price). Distances used for per-tkm
conversions (Rhine kilometrage from Rotterdam, Maasvlakte ~ Rhine-km 1,030) [E]: Duisburg-Ruhrort
(km 780) 240 km; Cologne (km 688) 320 km; Frankfurt (Main) 560 km; Mannheim/Ludwigshafen
(km 425) 590 km; Karlsruhe (km 360) 650 km (the model uses 650); Strasbourg 720 km; Basel
(km 168) 830 km (INFRAS uses 830). Currency: EUR unless stated; USD/EUR treated as 1:1 +-10 %
in the model comparison [E].

Text extracts used (pdftotext) sit in the session scratchpad `pdftxt/`: CCNR annual reports 2019,
2023, 2025, CCNR Market Insight April 2026, CCNR price-formation report (2024), Insights Global
methodology v3.13, KiM/Panteia "Cost figures for freight transport" (EN and NL, 2023), BALM
Jahresbericht 2023, EC 2005 charging study, INFRAS/PLANCO 2017 (Swiss Rhine costs 2015),
Konings 2009 dissertation. The CBS price-index download is `scratchpad/cbs84050.json`.

Companion files: `giveup_thresholds_by_cargo.md` (normal rates and multiples already collected,
section 1.1), `evidence_rhine2026_timeline.md` (2026 tanker rate track).

---

## 0. Bottom line

1. **No public source prints a full normal-water rate table by vessel class.** The CCNR Market
   Observation publishes only indices (Insights Global/PJK liquid spot index, CITBO index, CBS
   segment indices) and states explicitly that the absolute EUR/t data are transformed into
   indices (annual report 2025, footnote 32) [C]. Panteia's annual "Kostenontwikkeling
   binnenvaart" for KBN is paywalled; only percentage changes are public [C]. BALM reports are
   qualitative on rates [C]. Insights Global's daily ARA/Rhine report is a subscription product.
2. **The best public COST table is Panteia's work for KiM (2023, 2021 price level)** [C]: total
   cost per hour, per km, per tkm and per tonne-hour for a Kempenaar (540 t), a Rijn-Herne
   vessel (1,360 t), a Groot Rijnschip / CEMT Va (2,410 t) and a 4-barge push convoy (11,000 t),
   split by dry bulk / liquid bulk / break bulk / containers. Headline fully-allocated costs
   (fleet average, including empty legs and waiting): Va dry bulk 0.018 EUR/tkm, Va tanker
   0.029, Va container 0.025, push convoy 0.008-0.012 (ores 0.009), Rijn-Herne dry 0.021,
   Kempenaar dry 0.036 EUR/tkm. Cost per hour: Va 134 (dry) / 172 (tanker) / 137 (container),
   push convoy 494, Rijn-Herne 79-118, Kempenaar 47-51 EUR/h.
3. **RATE levels found, normal or near-normal water** (all per tonne, one direction):
   tankers ARA-Cologne 15.0-16.8 (Jun-Jul 2025, Riverlake via OPIS) [R], ARA-Karlsruhe 27.4-29.1
   (Jun-Jul 2025, loads already trimmed) [R] and about 20 (Jun 2022) [S], ARA-Duisburg 17.4 and
   ARA-Basel 42.0 (3 Nov 2023, Refinitiv series shown in the CCNR price-formation report) [C],
   Rotterdam-Basel gasoil CHF 22-28 (normal, TCS/Avenergy 2026) [R]; dry bulk: coal Rotterdam-Basel
   10.5 EUR/t (2015, published rate quoted by INFRAS/BFS, = 0.0127 EUR/tkm) [C], grain southern
   Germany 25-30 EUR/t (2026, agrarheute) [R], "around EUR 20/t" Rotterdam to south of Kaub
   generic (Bloomberg) [R]; containers: Rotterdam-Duisburg 192 EUR/TEU and Rotterdam-Tilburg
   170 EUR/TEU (2006, Policy Research via BVB) [R], Lower Rhine 50-100 and Middle Rhine 125-140
   EUR/TEU (tariffs c. 2005-2008, Konings 2009) [C]; container COST Rotterdam-Basel 162-178 EUR/TEU
   upstream, 122-138 downstream (2015, INFRAS worked example, 192 TEU vessel) [C].
4. **Structure.** Tanker spot rates are per tonne on a standard 2,000 t parcel and include fuel,
   pilotage and dues [C]; across lanes they fit "3-7 EUR/t fixed + 0.037-0.042 EUR/t per km"
   [E]. Operator cost is 75-80 % time-based (capital, insurance, crew) for motor vessels and
   about 50 % fuel for push convoys [C]; the per-tonne cost of a voyage is therefore roughly
   inversely proportional to the load, which is what the low-water surcharge prices. Container
   pricing is per box: 70-80 EUR/TEU of the all-in price is two terminal lifts, sailing on a
   240 km lane is 35-50 EUR/TEU [C, 2009].
5. **Against the model** (0.010 USD/tkm, 6.5 USD/t on Rotterdam-Karlsruhe): push-convoy dry bulk
   matches (0.009-0.010 EUR/tkm); single-vessel dry bulk is 1.3-2 x higher (0.013 rate 2015,
   0.018 cost 2021); tankers are 3-4.5 x higher (0.030-0.045 EUR/tkm observed rates); containers
   are 2-2.5 x higher on line-haul plus 7-8 EUR/t of lifts, but the model's container value of
   time (39 USD/t on the lane) already exceeds the whole observed barge tariff. Section 6.3
   proposes, without applying it, dry bulk convoy 0.010, dry bulk single vessel 0.018-0.020,
   liquid bulk 0.037-0.040 + 4-5 USD/t fixed, containers 0.020-0.025 + 7-8 USD/t fixed.

---

## 1. What the requested sources contain (and do not)

| Source | What it gives | Rate levels in EUR/t? | Tag |
|---|---|---|---|
| CCNR Market Observation annual reports 2019, 2023, 2025; Market Insight Apr 2026 | Insights Global (ex-PJK) liquid spot index ARA-Rhine (2015=100, then 2021=100), split Lower Rhine (Duisburg, Cologne) / Upper Rhine (Karlsruhe, Basel) / Main (Frankfurt); CITBO liquid index FARAG region (Q3 2017=100) by product; CBS dry-cargo spot and contract, liquid and container indices; Panteia cost-component index 2008=100 | No: "the absolute spot market freight rate data (given in Euro per tonnes) were transformed into index figures" (AR 2025 fn 32; AR 2023 fn 29) | [C] |
| CCNR thematic report "Price formation in IWT" (workshop 8 Nov 2023, report Mar 2024) | Price-formation schemes (spot, time charter, voyage charter, long-term, internal), revenue composition (base rate per tonne + low-water surcharge + fuel surcharge + demurrage), cost components, Figure 1 reproduces Refinitiv gasoil freight series for ARA-Basel and ARA-Duisburg with the 3 Nov 2023 values, Figures 4-5 container KWZ volatility at Kaub | Only via Figure 1 (42.00 Basel, 17.36 Duisburg on 03/11/23) | [C] |
| CCNR web chapter "Water levels and freight rates" (AR 2024) | 2023 vs 2022: all segments -11.8 %; dry bulk spot -21.4 %, contract -10.6 %; containers +2.2 % (after +23.6 % in 2022); liquid +3.9 % (after +27.2 %); CITBO: "chemicals have by far the highest spot market freight rates in absolute terms (EUR/tonne), followed by gasoline" | No | [C] |
| Insights Global methodology v3.13 (public PDF) | Route list, units, standard parcel, product differentials (section 2.1) | Sample levels not given | [C] |
| Panteia / KBN "Kostenontwikkeling binnenvaart" (annual, paywalled) | Representative annual accounts for motor dry-cargo, container, tanker, coupled and push units; only the % changes are public (section 3.4) | No | [C] |
| KiM / Panteia "Cost figures for freight transport" (Mar 2023, base year 2021) | Full COST tables per vessel type and cargo (section 3.1) | Costs, not rates | [C] |
| RWS "Kostentool binnenvaart" (2017, zip "Model kostenkengetallen extern", 2018) | Cost per km and per hour per vessel type; the file was not opened here | - | [C] |
| BALM Marktbeobachtung Güterverkehr, Jahresbericht 2023 | Qualitative: spot rates under pressure in 2023, shorter contracts, tankers still slightly above 2022, containers flat; low-water and gasoil surcharges lower than 2022; average gasoil purchase price 121.25 EUR/100 l (2022), 100.60 (2023) | No | [C] |
| CBS StatLine 84050NED "Binnenvaartdiensten; prijsindex 2015=100" (2014-2023) and 85817 (2021=100) | Quarterly and annual indices by segment (section 2.4); model prices on fixed routes surveyed twice a quarter, incl. fuel and low-water surcharges, excl. handling | Index only | [C] |
| "Rheinschifffahrt Frachtenmarkt" reports | Not found in public form | - | - |
| Destatis | Volumes and turnover only; no rates | - | [C] |

---

## 2. Market RATES by segment and lane (normal or near-normal water)

### 2.1 Liquid bulk: ARA-Rhine tanker spot market

Definitions (Insights Global methodology v3.13) [C]: standard routes AR (Amsterdam/Rotterdam)
to Duisburg, Dortmund, Cologne, Frankfurt, Karlsruhe, Strasbourg, Basel; rates in EUR/t
(CHF/t for Basel), for prompt loading, INCLUDING fuel, pilotage, harbour and canal dues;
standard parcel 2,000 t "or water level loading" (parcels shrink with the water level);
separate assessments for "gasoil" (middle distillates) and "gasoline" (light products, naphtha),
with a fixed differential of +0.55 EUR/t (Duisburg, Dortmund, Cologne), +0.80 EUR/t (Frankfurt,
Karlsruhe, Strasbourg) and +CHF 1.50 (Basel) for light products. ARA intra-harbour routes:
parcels above 2,000 t.

| Lane (distance) | RATE, EUR/t | EUR/tkm [E] | Date, water | Source | Tag |
|---|---|---|---|---|---|
| ARA cross-harbour | 3.83 | - | 1-9 Jul 2025 | Riverlake via OPIS 10 Jul 2025 | [R] |
| Rotterdam-Cologne (320 km) | 16.83 (1-9 Jun 2025); 15.00 (1-9 Jul 2025) | 0.047-0.053 | Cologne loads still ~ 1,700 t on 10 Jul | same | [R] |
| Rotterdam-Karlsruhe (650 km) | 29.07 (1-9 Jun 2025); 27.42 (1-9 Jul 2025) | 0.042-0.045 | Maxau loads ~ 1,350 t on 10 Jul 2025 (normal "up to 5,000 t") | same | [R] |
| ARA-Karlsruhe, gasoil | about 20 | 0.031 | June 2022, before the 2022 low water | Handelsblatt/WiWo 18 Aug 2022 | [S] |
| ARA-Karlsruhe | about 45 | 0.069 | end June 2026, Kaub ~ 106 cm, surcharges already in | Reuters 15 Jul 2026 (timeline file) | [R] |
| ARA-Duisburg (240 km), gasoil (Refinitiv GOFRT-DUISBERG) | 17.36 | 0.072 | 3 Nov 2023 (after the autumn 2023 rise; level not verified) | CCNR price-formation report, Fig. 1 (Insights Global data) | [C] |
| ARA-Basel (830 km), gasoil (Refinitiv GOFRT-BASLE) | 42.00 (unit on the chart not stated; Basel is normally quoted in CHF/t) | 0.051 | 3 Nov 2023 | same | [C] |
| Rotterdam-Basel, gasoil | CHF 22-28 "at normal water" | 0.027-0.034 CHF | 2026 statement | swissinfo/SDA 27 Aug 2026 (TCS/Avenergy) | [R] |
| ARA-Basel | EUR 69.30 (1 Jul 2026, already low); 276.67 (14 Aug); 256 (late Aug) | 0.083 (1 Jul) | 2026 | S&P Global Platts via Hellenic Shipping News (page not opened) | [S] |
| Rotterdam to "south of the Kaub chokepoint", generic | "around EUR 20/t" normal | ~ 0.03 | 2026 | Bloomberg opinion via enterpriseam 3 Aug 2026 | [R] |

Reading [E]. The June/July 2025 pairs give a distance structure: (29.07 - 16.83) / (650 - 320)
= 0.037 EUR/t per km with an intercept of about 5 EUR/t (June), 0.038 per km and 3 EUR/t
(July, intercept close to the 3.83 cross-harbour rate); the Nov 2023 pair gives 0.042 per km and
7 EUR/t. So an ARA-Rhine gasoil rate at normal-to-slightly-low water is about
**3-7 EUR/t fixed + 0.037-0.042 EUR/t per km** [E]. Short lanes carry the highest per-tkm
rate (Cologne 0.05, Karlsruhe 0.04, Basel 0.03-0.05). Product differentials are small
(0.55-0.80 EUR/t); chemicals are the most expensive segment per tonne in the CITBO data
(stainless tanks, cleaning, safety) but no level is published [C].

### 2.2 Dry bulk

| Lane / cargo (distance) | RATE, EUR/t | EUR/tkm [E] | Year | Source | Tag |
|---|---|---|---|---|---|
| Rotterdam-Basel, coal, motor vessel class 9 (2,001-2,500 t) or coupled unit (830 km) | 10.5 (published rate; "corresponds roughly to the calculated cost", i.e. barely cost-covering) | 0.0127 | 2015 | INFRAS/PLANCO for BFS 2017, p. 27 | [C] |
| Southern Germany lane (Bayernhof), grain | 25-30 normal (100 in Aug 2026) | 0.04-0.05 if ~ 600 km [E] | 2026 | agrarheute 6 Aug 2026 (companion dossier) | [R] |
| Hengelo-Leverkusen, salt, 1,250 t | 5.20 | - (canal + Rhine, ~ 250 km [E]: 0.021) | 2006 | Policy Research 2006 via Bureau Voorlichting Binnenvaart | [R] |
| Amsterdam-Meppel, fertiliser, 1,250 t | 4.10 | ~ 150 km [E]: 0.027 | 2006 | same | [R] |
| Liège-Nijmegen, raw minerals, 2,500 t | 4.00 | ~ 160 km [E]: 0.025 | 2006 | same | [R] |
| Reims-Den Bosch, grain, 350 t (Freycinet canal barge) | 21 | ~ 400 km [E]: 0.05 | 2006 | same | [R] |
| Rotterdam-Duisburg, ore/coal, 6-barge push convoys (16,000 t) | no published rate found; COST-based estimate 2-4 EUR/t (section 4) | 0.009-0.016 | - | - | [E] |

BVB adds that the 2006 quotes sit "30 % higher in a high-demand period and 30 % lower in a
low-demand period" and that pricing rests on trip duration/distance and the fixed and variable
costs, not on cargo value [R]. The CCNR 2019 report notes that in Oct-Nov 2018 dry-cargo rates
rose more for coal, iron ore and containers than for sand, gravel and agribulk (the low-value
goods cannot bear the same surcharge) [C]. No dry-bulk Kleinwasserzuschlag table (EUR per tonne
per cm below a gauge threshold) was found in public form; BALM confirms such surcharges are
contractually levied per tonne when gauges fall below agreed limits [C].

### 2.3 Containers (per TEU; tonnes per TEU assumption in section 6)

| Lane (distance) | RATE or COST, EUR/TEU | Year | Source | Tag |
|---|---|---|---|---|
| Rotterdam-Duisburg (240 km), 208 TEU vessel | RATE 192 | 2006 | Policy Research 2006 via BVB | [R] |
| Rotterdam-Tilburg, 32 TEU | RATE 170 | 2006 | same | [R] |
| Rotterdam-Lower Rhine destinations (two round trips a week) | RATE 50 (short) to 100 (Bonn etc.) | c. 2005-2008 | Konings 2009, ch. 5 | [C] |
| Rotterdam-Middle Rhine destinations (one round trip a week) | RATE 125-140 | c. 2005-2008 | same | [C] |
| Rotterdam intra-port feeder (Van Uden), incl. two lifts | RATE about 95, of which sailing 15-20 and handling 70-80 (two moves) | c. 2008 | same | [C] |
| Rotterdam-Duisburg, indicative COST by vessel size (90/208/398 TEU) and load, two round trips a week | COST about 50-125 (chart range; doubling vessel size saves 20-30 %) | 2009 | Konings 2009, Fig. 2.7-2.8 | [C] |
| Rotterdam-Basel (830 km), 192 TEU vessel, full, upstream | COST 162 without / 178 with handling (trip cost 31,105 / 34,184 EUR: capital 16,082, crew 9,811, fuel 5,212 at 0.55 EUR/l, handling 3,078; 146 h incl. 10 locks and port time) | 2015 | INFRAS/PLANCO 2017, Table 13 | [C] |
| Basel-Rotterdam, downstream | COST 122 / 138 (trip 23,374 / 26,452 EUR; 126 h) | 2015 | same | [C] |
| Rotterdam-Basel / Upper Rhine | order 150-300 per TEU | - | companion dossier | [E] |

Low-water surcharge structure for containers (structure only, not normal rates):
Contargo 9 Aug 2026 [C]: per 20'/40' box, Kaub gauge 80-71 cm 300/380, 70-61 400/480, 60-51
550/645, 50-41 775/930, <= 40 cm 1,075/1,280 EUR; Cologne gauge 105-96 cm 200/240 up to
45-41 cm 1,010/1,150; Duisburg-Ruhrort 180-171 cm 165/205 up to 130-121 cm 800/900; Emmerich
30-21 cm 80/140 up to -11 to -20 cm 345/475; carriage obligation ends at Kaub <= 80, Cologne
<= 105, Ruhrort <= 180, Emmerich <= 30 cm. In 2019 the ONE surcharge started at Kaub < 150 cm
with 35/45 EUR per 20'/40' and at Ruhrort < 270 cm with 30/40 EUR (THB 4 Mar 2019) [R]. The
CCNR price-formation report (Figs 4-5) documents the volatility of the Kaub surcharge and the
number of days per year with Kaub < 150 cm (149-163 in the years shown) [C].

### 2.4 Index series (for scaling old quotes)

CBS 84050NED, annual index 2015 = 100 [C] (segment codes: A023820 total; A042619, A042620,
A042621 and A023824 are the sub-series; the code-to-label mapping was not retrieved, but the
CCNR chapter identifies the sub-series as dry-cargo spot, dry-cargo contract, liquid cargo and
containers; the most volatile series A042621 (198 in 2022) is consistent with dry-cargo spot):

| Year | Total | A042619 | A042620 | A042621 | A023824 |
|---|---|---|---|---|---|
| 2016 | 91.1 | - | - | - | - |
| 2017 | 108.1 | - | - | - | - |
| 2018 | 128.5 | 105.6 | 142.1 | 145.8 | 107.0 |
| 2019 | 122.6 | 120.5 | 131.3 | 124.9 | 111.7 |
| 2020 | 109.3 | 104.8 | 123.7 | 109.9 | 103.2 |
| 2021 | 116.1 | 99.3 | 129.6 | 125.6 | 107.3 |
| 2022 | 165.3 | 126.4 | 173.1 | 198.2 | 132.6 |
| 2023 | 145.9 | 131.3 | 154.8 | 155.9 | 135.5 |

CCNR: 2022 vs 2021 all segments +42.5 %, 2023 vs 2022 -11.8 %; Q3/Q4 2022 dry-bulk spot
240.9/203.9 (2015=100) [C]. CCNR Market Insight April 2026 (2021 = 100 series): Insights
Global liquid index "on a multiannual average level" in Q1 2025, rising in Q2 2025 with the
tendency towards low water; the absolute rate is "higher, the further away from the ARA region
the destination is located"; CBS dry-cargo spot slightly upward in 2024-2025, contract prices
stagnating, container index stagnating in H1 2025 [C].

---

## 3. Operator COSTS by vessel type

### 3.1 Panteia for KiM, "Cost figures for freight transport" (Mar 2023), price level 2021 [C]

Method: Dutch operators' data (Panteia cost model, BIVAS itineraries), ex-VAT, representative
of western Europe (Dutch fleet 50-60 % of the market); fixed costs = depreciation, interest,
insurance; variable = fuel, lubricants, repair and maintenance; staff per crewing regulation
and exploitation mode (solo 2,496 h/yr, A1 3,360, A2 4,752, B continuous 8,064; weighted
averages used). Vessel types (RWS classes): Small = Kempenaar, CEMT II / M2, 401-650 t, avg 540 t;
Medium = Rijn-Herne, CEMT IVa / M6, 1,251-1,750 t, avg 1,360 t; Large = Groot Rijnschip,
CEMT Va / M8, 2,050-3,300 t, avg 2,410 t, 110 x 11.4 m; Push = 4-barge push convoy with one
pusher, CEMT VIb / BII-4, 7,501-12,000 t, avg 11,000 t. The tables were reconstructed from the
PDF text (columns were shifted in extraction); every block was checked by re-adding its rows.

Annual costs (EUR/yr) and structure:

| Vessel, cargo | Fixed | Variable (fuel etc.) | Staff | Mode-specific | General | Total | Hours/yr |
|---|---|---|---|---|---|---|---|
| Small, dry bulk | 21,965 (12 %) | 27,317 (15 %) | 115,219 (65 %) | 4,402 | 8,860 | 177,763 | 3,830 |
| Small, container | 30,493 | 30,722 | 118,817 | 8,228 | 8,860 | 197,120 | 3,830 |
| Medium, dry bulk | 68,314 (22 %) | 66,357 (21 %) | 155,047 (50 %) | 10,084 | 13,000 | 312,802 | 3,971 |
| Medium, liquid bulk | 214,318 (45 %) | 68,801 (14 %) | 171,195 (36 %) | 9,871 | 13,000 | 477,186 | 3,999 |
| Medium, container | 104,020 | 76,997 | 202,059 | 14,496 | 13,000 | 410,573 | 3,971 |
| Large, dry bulk | 204,325 (35 %) | 128,941 (22 %) | 210,901 (36 %) | 15,845 | 19,767 | 579,779 | 4,318 |
| Large, liquid bulk | 460,205 (43 %) | 163,265 (15 %) | 409,149 (38 %) | 19,936 | 19,767 | 1,072,322 | 4,348 (chemicals 6,224) |
| Large, break bulk | 202,360 | 126,370 | 210,274 | 15,226 | 19,767 | 573,998 | 4,318 |
| Large, container | 253,951 (27 %) | 184,078 (20 %) | 444,264 (48 %) | 31,634 | 19,767 | 933,694 | 4,318 |
| Push convoy (4 barges + pusher), dry bulk | 1,040,639 (26 %) | 1,884,439 (47 %) | 759,407 (19 %) | 98,752 | 202,608 | 3,985,845 | 8,064 |

Unit costs (EUR; per tkm and per tonne-hour are fleet averages that include empty legs and
waiting, i.e. total annual cost divided by loaded tkm or by tonne-hours):

| Vessel, cargo | Per hour sailing | Per km | Per tkm | Per tonne-hour | Waiting / (un)loading, per hour | Implied avg payload, t [E] |
|---|---|---|---|---|---|---|
| Small (540 t), dry bulk | 47.18 | 8.72 | 0.036 | 0.195 | 38.76 | 242 |
| Small, break bulk | 47.26 | 9.01 | 0.043 | 0.228 | 38.97 | 207 |
| Small, container | 51.47 | 8.23 | 0.092 | 0.575 | 41.30 | 90 |
| Medium (1,360 t), dry bulk | 78.63 | 12.27 | 0.021 | 0.135 | 59.42 | 582 |
| Medium, liquid bulk | 117.68 | 17.82 | 0.040 | 0.259 | 98.28 | 454 |
| Medium, break bulk | 78.08 | 12.31 | 0.026 | 0.165 | 59.25 | 473 |
| Medium, container | 87.75 | 12.07 | 0.036 | 0.259 | 68.19 | 339 |
| Large (2,410 t), dry bulk | 134.03 | 17.53 | 0.018 | 0.141 | 100.56 | 950 |
| Large, liquid bulk | 172.29 | 23.06 | 0.029 | 0.215 | 142.85 | 801 |
| Large, break bulk | 132.93 | 17.71 | 0.022 | 0.163 | 100.14 | 815 |
| Large, container | 136.85 | 18.47 | 0.025 | 0.184 | 105.23 | 744 |
| Push convoy (11,000 t), dry bulk (all) | 494.28 | 35.98 | 0.010 | 0.132 | 248.35 | 3,745 |
| Push convoy, agri / coal / ores | 494.28 | 35.09 / 36.68 / 36.22 | 0.012 / 0.008 / 0.009 | 0.167 / 0.114 / 0.125 | 248.35 | 2,960 / 4,335 / 3,954 |

Per-commodity variants for small ships (Table A.1): agri/coal/ores 0.037 EUR/tkm, salt-sand-
gravel 0.032; per hour 47.26 (agri) / 46.92 (salt). The Dutch note gives the same comparison
for 2018: 0.033 EUR/tkm for a medium vessel carrying containers against 0.115 EUR/tkm for a
tractor-semitrailer [C]. Checks [E]: 579,779 / 134.03 = 4,326 h (Table 3.2: 4,318); 579,779 /
17.53 = 33,070 km/yr (Table 3.2: 32,000-34,000 km); 134.03 / 0.141 = 950 t average payload,
i.e. about 40 % of 2,410 t, consistent with the 32-39 % utilisation (loaded-km share x load
factor) reported for large ships.

### 3.2 Cost changes after 2021 (Panteia for KBN, public summaries) [C]

- 2022: strong increases (fuel +67.6 % to 121.25 EUR/100 l on the German market, BALM).
- 2023: fuel back to 100.60 EUR/100 l (BALM); CCNR: all cost components rose except fuel.
- 2024: total cost +0.3 % to +3.7 % by vessel type/area/mode; ex-fuel +4.3 % to +6.0 %; drivers
  capital, insurance, labour, repair and maintenance; large tankers and Rhine container vessels
  (many operating hours) had the lowest increase (Panteia news, 24 Apr 2025).
- 2025: +1.4 % to +4.2 % (ex-fuel +4.4 % to +5.3 %; fuel -1.4 %); building-materials segment
  +2.9 % to +4.2 % (Panteia news 2026).
- 2026 forecast: -1.5 % to +2.3 % (ex-fuel +3.0 % to +4.3 %; fuel -5.9 %) (same).
- Cumulative 2021 -> 2025 [E]: roughly +15-20 % ex-fuel; the 2021 KiM levels should be scaled
  by about 1.15-1.2 for 2025-2026 use (fuel about the 2021 level again).

### 3.3 Other cost benchmarks

| Item | Value | Year, source | Tag |
|---|---|---|---|
| Swiss-Rhine traffic (Basel relations), vehicle + infrastructure cost per tkm | 2.7 Rp/tkm upstream loaded, 4.0 Rp/tkm downstream (lower utilisation); 4.8 Rp/tkm including empty trips and infrastructure (3.9 vehicle + 0.9 infrastructure) | 2015, INFRAS/PLANCO for BFS 2017, Table 26 | [C] |
| Cost per ship movement on Rhine relations to/from Swiss ports (BVWP cost method) | full upstream 25,168 EUR; empty upstream 20,635; full downstream 20,682; empty downstream 17,883; average 22,048 EUR per movement | 2015, same, Table 16 | [C] |
| Same, per tonne for a full 2,300 t upstream load [E] | 10.9 EUR/t (matches the 10.5 EUR/t coal rate above) | 2015 | [E] |
| Transit times Rotterdam-Basel | 103 h pure sailing + 7.5 h (10 locks) upstream, 83 h downstream; 146 h / 126 h including port time (INFRAS); "about 90 h" up, "48 h" down pure travel (Port of Switzerland FAQ) | 2015 / 2026 | [C] |
| Speeds assumed by INFRAS (2,001-2,500 t vessel, 2.5 m draught) | 8 km/h upstream (505 kW), 10 km/h downstream (113 kW); fuel 200 g/kWh; gasoil 0.55 EUR/l | 2015 | [C] |
| Value of vessel time (waiting) used in Dutch/EU appraisal | 78 EUR per vessel-hour for container vessels, 74 for others (Dutch study c. 2004); UNITE: 218 EUR per vessel-hour = 0.20 EUR per tonne-hour | 2001-2005, EC "Charging and pricing in the area of inland waterways" 2005 | [C] |
| Average annual fuel consumption per vessel (fleet families) | dry-cargo motor vessels >= 110 m: 1,449 m3/yr (2,594 kW installed); liquid >= 110 m: 237 m3 (sic, 1,307 kW); 80-109 m dry 240 m3; push boats > 2,000 kW 110 m3 (sic) | 2015 base, CCNR/DST zero-emission study, Table 8 (some cells look mis-ordered in the PDF) | [C] |
| Terminal factor costs (barge container terminals) | fixed and variable cost blocks for small to very large terminals (20,000-200,000 containers/yr), 2011 prices | Wiegmans and Konings, Annex A Table 4 | [C] |

---

## 4. Derived normal-water COST per tonne on standard lanes [E]

All figures 2021 price level from section 3.1 (scale x 1.15-1.2 for 2025-26, section 3.2).
Three attributions are given because backhaul practice differs by trade: (i) fleet-average
per-tkm x distance (includes empty legs and waiting, fully allocated); (ii) one-way voyage
attribution (loaded leg hours x EUR/h / load, i.e. the backhaul is paid by someone else);
(iii) round-trip attribution (loaded leg + empty return charged to the cargo, as in Rhine bulk
trades that return empty). Hours: upstream km / 8.1 km/h + port time (30 h for a 650 km lane,
scaled with distance), downstream km / 10 km/h + 20 h; both from the INFRAS times (Rotterdam-
Basel 146 h up, 126 h down). Loads: Va dry 2,300 t, tanker standard parcel 2,000 t, push
convoy 11,000 t, container vessel 160 TEU each way at 10 t/TEU (assumption, see section 6).

| Segment, vessel | Lane (km) | (i) fleet avg per tkm x km | (ii) one-way | (iii) round trip | Observed RATE for comparison |
|---|---|---|---|---|---|
| Dry bulk, push convoy 4 x 2,750 t | Rotterdam-Duisburg (240) | 2.2 (ores 0.009) | 2.3 (52 h x 494 / 11,000) | 4.0 (88 h) | none public; 6-barge units (16,000 t) about 30 % lower per tonne [E] |
| Dry bulk, push convoy | Rotterdam-Mannheim/Karlsruhe (590-650) | 5.3-6.5 | 5.0-5.5 | 8.5-9.5 | - |
| Dry bulk, Va motor vessel | Rotterdam-Duisburg (240) | 4.3 | 2.9 (50 h x 134 / 2,300) | 5.2 (90 h) | - |
| Dry bulk, Va motor vessel | Rotterdam-Karlsruhe (650) | 11.7 | 6.4 (110 h) | 11.4 (195 h) | grain 25-30 EUR/t (smaller vessels, agri lane, 2026) |
| Dry bulk, Va motor vessel | Rotterdam-Basel (830) | 14.9 | 8.5 (146 h) | 15.9 (272 h) | coal 10.5 EUR/t (2015 rate; 10.9 EUR/t 2015 cost) |
| Liquid bulk, Va tanker | Rotterdam-Cologne (320) | 9.3 | 5.5 (64 h x 172 / 2,000) | 9.6 (112 h) | 15.0-16.8 EUR/t (Jun-Jul 2025) |
| Liquid bulk, Va tanker | Rotterdam-Karlsruhe (650) | 18.9 | 9.5 (110 h) | 16.8 (195 h) | 20 (Jun 2022), 27-29 (Jun-Jul 2025) EUR/t |
| Liquid bulk, Va tanker | Rotterdam-Basel (830) | 24.1 | 12.6 (146 h) | 23.4 (272 h) | CHF 22-28/t normal; 42 (Nov 2023) |
| Containers, Va vessel | Rotterdam-Duisburg (240) | 6.0 EUR/t = 60 EUR/TEU | 36 EUR/TEU line-haul (88 h round trip x 137 / 320 TEU) + 70-80 EUR/TEU two lifts (2009) = 105-115 EUR/TEU | same | RATE 50-100 (Lower Rhine, 2005-08), 192 (2006 quote); COST 50-125 (Konings 2009) |
| Containers, 192 TEU vessel | Rotterdam-Basel (830) | 20.8 EUR/t = 208 EUR/TEU | 162-178 EUR/TEU (INFRAS 2015, full vessel) | - | RATE order 150-300 [E] |

Reading. Fleet-average per-tkm (i) and round-trip attribution (iii) agree within 10-20 % for
motor vessels, and both match the observed dry-bulk rate of 2015 and the tanker rates of
2022-2025 once a 10-40 % margin for cleaning, dues, demurrage and profit is allowed (tanker
rates on short lanes are the exception: 15-17 EUR/t to Cologne against 9-10 EUR/t cost, a
sign of a fixed per-voyage element of 3-7 EUR/t that the per-tkm cost view does not show).
Push convoys are 2-3 x cheaper per tonne than single motor vessels on the same lane.

---

## 5. Fixed versus variable structure

1. **Cost side (KiM 2021)** [C]: for motor vessels, time-based items (capital, insurance, crew,
   general) are 75-80 % of the hourly cost and fuel/maintenance 15-22 %; for push convoys fuel
   is 47 % (large installed power, continuous operation). Cost per voyage is therefore mainly
   hours x hourly cost; cost per tonne = voyage cost / load, so a 50 % load restriction doubles
   the per-tonne cost. Waiting costs 100 EUR/h (Va dry), 143 (Va tanker), 105 (Va container),
   248 (push convoy), 59 (Rijn-Herne), 39 (Kempenaar); per tonne-hour for a full load: 0.044,
   0.071, 0.05 (200 TEU x 10 t), 0.023, 0.044 and 0.072 EUR/t/h respectively [E]; fleet-average
   per tonne-hour (including empty running) 0.13-0.26 EUR/t/h [C].
2. **Tanker rates** [C]: quoted per tonne on a 2,000 t standard parcel, fuel and dues included;
   long-term contracts carry a base rate + gasoil clause + low-water surcharge "as a result of
   reduced loading capacity" + demurrage (CCNR price-formation report). Across lanes the spot
   rate is about 3-7 EUR/t fixed + 0.037-0.042 EUR/t per km [E]; so on ARA-Karlsruhe about
   80-85 % of the normal rate is distance-dependent, on ARA-Cologne about 65-75 %. The
   effective per-voyage revenue is what the market defends: when parcels shrink, the per-tonne
   rate rises roughly in proportion (x4-4.5 in 2018, x5.5 in 2022, x10 in 2026, companion
   dossier), i.e. the rate behaves as "mostly fixed per voyage".
3. **Dry bulk contracts** [C]: base freight per tonne (BALM: shippers pressed for lower
   "Basisfrachten" in 2023; shorter contracts, half-year or quarterly; some switched from
   time- to volume-based contracts) + gasoil surcharge + Kleinwasserzuschlag per tonne below a
   gauge threshold. Rates for low-value goods (sand, gravel, agribulk) rise less in low water
   than for coal, ore and containers (CCNR 2019).
4. **Containers** [C]: price per box; all-in tariff on Rotterdam-Duisburg c. 2005-2008 was
   50-100 EUR/TEU of which two lifts 70-80 EUR/TEU and sailing 15-50; surcharges are stepped
   per box by gauge band (section 2.3); low-water steps of 300-1,075 EUR/TEU at Kaub are
   2-10 x the normal line-haul price. Contargo's carriage obligation ends at Kaub <= 80 cm.

---

## 6. Implications for a per-cargo waterway rate in the model

Model recalled (README, 7 Sep run log): uniform waterway cost 0.010 USD/tkm, i.e. about 6.5
USD/t line-haul on Rotterdam-Karlsruhe (650 km), plus river transfer costs (24 h / 6 USD per
transfer in v12); container value of time on waterways 0.45 USD/t/h at 7 km/h adds about 39
USD/t on that lane; the 7 Sep run found delivered prices capped near +10 % at x2.5 surcharge
because the base freight is so low against tank-barge rates of EUR 20-45/t.

### 6.1 Normal-water levels per segment (EUR/t on Rotterdam-Karlsruhe, 650 km; EUR/tkm)

| Segment | COST 2021 (KiM, fleet avg) | RATE observed | Ratio to model (6.5 USD/t; 0.010/tkm) | Grade |
|---|---|---|---|---|
| Dry bulk in push convoys (ore, coal, aggregates, Lower/Middle Rhine) | 0.008-0.010 EUR/tkm; 2-4 EUR/t on 240 km, 5-9 EUR/t on 650 km | none public | about 1 x | B (cost [C], no rate) |
| Dry bulk, single motor vessel (agri, fertiliser, salt, metals, scrap, building materials on long lanes) | 0.018 (Va) - 0.021 (IVa) - 0.036 (II) EUR/tkm; 11.7 EUR/t Va | 0.0127 EUR/tkm (coal Rotterdam-Basel 2015, cost-covering only); 25-30 EUR/t grain (2026, agri lane) | 1.3-2 x (Va); 3-4 x for grain-type flows | B (cost [C], one 2015 rate [C], one 2026 press rate [R]) |
| Liquid bulk (refined products, chemicals) | 0.029 EUR/tkm; 18.9 EUR/t | 20-29 EUR/t Karlsruhe (0.031-0.045/tkm), 15-17 Cologne (0.047-0.053), 42 Basel (0.051, Nov 2023), CHF 22-28 Basel normal (0.027-0.034) | 3-4.5 x | A- (rates from 3 independent series [R][C][S] + cost [C]) |
| Containers | 0.025 EUR/tkm (16 EUR/t on 650 km) + two lifts 7-8 EUR/t | COST 162-178 EUR/TEU Rotterdam-Basel (2015); RATE 125-140 EUR/TEU Middle Rhine (c. 2008) -> at 10 t/TEU 12-18 EUR/t all-in | 2-2.5 x on line-haul; but model VOT adds 39 USD/t, so the model's all-in container barge cost (45 USD/t = 450 USD/TEU) is already 2-3 x the observed all-in tariff | B- (cost [C] 2015/2021; tariffs [C] but 15-20 years old; t/TEU [E]) |

Tonnes per TEU: no Rhine-specific average was retrieved; 10 t/TEU is assumed (loaded and empty
boxes mixed; the INFRAS example counts 1.3 TEU per box and does not give tonnes) [E]. At
14 t/TEU (loaded boxes only) the container per-tonne figures fall by 30 %.

### 6.2 Structure to represent

- Liquid bulk and containers carry a fixed per-voyage / per-box element (3-7 EUR/t for
  tankers; 7-8 EUR/t of lifts for containers) plus a distance element; dry bulk is closest to a
  pure per-tkm price. If the model keeps a single per-tkm number per cargo, the fixed element
  can be folded into the existing transfer cost (river transfers currently 6 USD per transfer)
  rather than into the tkm rate, which would otherwise over-price long lanes.
- Because operator cost is mostly time, the per-tonne effect of a load restriction is
  1 / (load factor); the observed multiples (x2.5 dry, x4.5-10 liquid) exceed that because
  capacity is auctioned in the spot market. The voyage-level surcharge logic adopted on 7 Sep
  is consistent with this evidence.
- Vessel-side cost of time is 0.02-0.07 EUR/t/h (full loads) or 0.13-0.26 EUR/t/h (fleet
  average); the model's 0.45 USD/t/h for containers is a cargo-side (inventory) value 2-10 x
  the vessel cost and is doing the work of the missing container rate in the mode split.

### 6.3 PROPOSED per-cargo waterway rate set (suggestion only; NOT applied; USD treated as EUR)

| Cargo class in the model | Line-haul, USD/tkm | Fixed per voyage, USD/t | Evidence grade | Rests on |
|---|---|---|---|---|
| Dry bulk moved in push convoys (iron ore, coal, coke, aggregates to Lower/Middle Rhine) | 0.010 (keep) | 1-2 | B | KiM push-convoy cost 0.008-0.010 [C]; no rate; 2015 coal rate 0.0127 on a motor-vessel lane [C] |
| Dry bulk in single motor vessels (agri products, fertiliser, salt, metals, scrap, building materials, Upper Rhine bulk) | 0.018-0.020 | 2-3 | B | KiM Va/IVa cost 0.018-0.021 [C]; 2006 lane quotes 0.02-0.03 [R]; grain 25-30 EUR/t 2026 [R] would imply 0.04, treated as a smaller-vessel/agri premium |
| Liquid bulk (refined products, chemicals, other liquids) | 0.037-0.040 | 4-5 | A- | Riverlake/OPIS Jun-Jul 2025 pairs [R]; Refinitiv Nov 2023 pair [C]; Handelsblatt Jun 2022 [S]; KiM tanker cost 0.029 [C] |
| Containers (containerised manufactures) | 0.020-0.025, and consider lowering the waterway VOT so that the all-in barge cost lands near 150-250 USD/TEU (15-25 USD/t) | 7-8 (two lifts) | B- | INFRAS 2015 cost 162-178 EUR/TEU on 830 km [C]; Konings tariffs 125-140 EUR/TEU Middle Rhine c. 2008 [C]; KiM container cost 0.025 [C]; 10 t/TEU [E] |

Consequence for the price channel [E]: with these rates the freight share `s` of delivered
value on Rotterdam-Karlsruhe becomes about 3-4 % for refined products (25 EUR/t on ~ 700
EUR/t), 10-15 % for grain (25-30 on 200-250), 20-40 % for aggregates (5-6 on 15-25) and
1-2 % for containers (15-25 on 1,000-2,000), so the same x2.5-x4 multiples give delivered-price
rises of +5-10 % (fuels), +15-45 % (grain), +30-120 % (aggregates), +2-5 % (containers), in
line with the thresholds discussed in `giveup_thresholds_by_cargo.md`, section 7.

---

## 7. Gaps and unverified items

- Panteia/KBN cost report tables (EUR per hour/day per vessel type, 2024-2026) are paywalled;
  the KiM 2021 tables are the public substitute. The RWS "Model kostenkengetallen extern"
  (2018 zip) was located but not opened.
- No public normal-water RATE for push-convoy ore/coal Rotterdam-Duisburg; no 2019-2026
  container base tariff per TEU (only 2006-2009 tariffs and the 2015 cost example); no
  dry-bulk Kleinwasserzuschlag table in EUR per tonne per cm.
- The Refinitiv Basel value (42.00 on 3 Nov 2023) may be CHF/t; the Kaub level on that date was
  not verified. The 1 Jul 2026 Platts ARA-Basel value (69.30 EUR/t) and the June 2022 ARA-
  Karlsruhe value (about 20 EUR/t) are search-summary items [S].
- The CBS sub-series codes A042619/20/21 and A023824 were not mapped to their labels.
- Not retrieved: van Dorsser (2015) thesis cost tables; Vinke et al. (2022) cost model;
  "The impact of critical water levels on container inland waterway transport" (2024);
  Al Enezy et al. (2017) cost model; Panteia et al. (2013) EC emissions impact study (the EC
  link resolved to the CE Delft 2019 "Transport taxes and charges in Europe" report, which has
  no cost-per-tkm table); Insights Global blog posts (qualitative only); Argus and Loadstar
  pages (no numbers in text or blocked).

---

## 8. Sources

1. CCNR, Inland Navigation in Europe, Market Observation, Annual report 2025 (Nov 2025), pp. 74-82
   (Insights Global index 2021=100, CITBO indices Q3 2017=100, chemicals highest EUR/t, Panteia
   cost-component index 2008=100). https://inland-navigation-market.org/wp-content/uploads/2025/11/CCNR_annual_report_EN_2025_WEB.pdf
2. CCNR, Annual report 2023 (rev. Jan 2025), pp. 11, 74-78. https://inland-navigation-market.org/wp-content/uploads/2025/01/CCNR_annual_report_EN_2023_WEB_rev.pdf
3. CCNR, Annual report 2019, pp. 68-71 (Panteia dry-cargo index, PJK index x4.5 in Oct-Nov 2018, CITBO EUR/t raw data). https://www.ccr-zkr.org/files/documents/om/om19_II_en.pdf
4. CCNR, Market Insight April 2026, pp. 40-44 (Insights Global and CBS indices, fuel prices). https://www.ccr-zkr.org/files/documents/om/om26_I_en.pdf
5. CCNR, Price formation workshop (8 Nov 2023), report, March 2024, pp. 4-9 (Refinitiv gasoil freight series Basel/Duisburg 3 Nov 2023, revenue and cost components, KWZ Figures 4-5). https://inland-navigation-market.org/wp-content/uploads/2024/03/Price-formation-workshop_report_en_final.pdf (also https://www.ccr-zkr.org/files/documents/omanalysesthematiques/om23_IV_en.pdf); web chapters https://inland-navigation-market.org/chapitre/3-conclusions/?lang=en
6. CCNR web chapter "4. Water levels and freight rates" (annual report 2024): https://inland-navigation-market.org/chapitre/4-niveaux-deau-et-taux-de-fret/?lang=en
7. Insights Global (ex-PJK International), "Methodology barge freight rates", version 3.13 (routes, T&C, differentials). https://www.insights-global.com/wp-content/uploads/2019/02/100_Methodology-PJK-barge-freight-rates_v3.13.pdf
8. OPIS (Dow Jones), "Falling River Rhine levels in Europe impact plant, terminal operations", 10 Jul 2025 (Riverlake broker rates: cross-harbour 3.83, Cologne 16.83/15.00, Karlsruhe 29.07/27.42 EUR/t; Maxau loads 1,350 t). https://www.opis.com/resources/energy-market-news-from-opis/falling-river-rhine-levels-in-europe-impact-plant-terminal-operations/
9. Panteia for KiM, "Cost figures for freight transport - final report" / "Kostenkengetallen voor het goederenvervoer", 30 Mar 2023, base year 2021 (Tables 3.1-3.5, A.1-A.4). EN: https://www.kimnet.nl/site/binaries/site-content/collections/documents/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Cost+figures+for+freight+transport_def.pdf ; NL note: https://www.kimnet.nl/site/binaries/site-content/collections/documents/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/KiM+notitie+update+bedrijfseconomische+kostenkengetallen+goederenvervoer_def.pdf ; landing page https://www.kimnet.nl/documenten/2023/03/30/kostenkengetallen-voor-het-goederenvervoer
10. Panteia news, "Kostenstijging in binnenvaartvervoer in 2025, grote onzekerheid voor 2026" (2026). https://panteia.nl/actueel/nieuws/kostenstijging-in-binnenvaartvervoer-in-2025-grote-onzekerheid-voor-2026/ ; "Kostenstijging in goederenvervoer over water zet door, extremen verleden tijd", 24 Apr 2025. https://panteia.nl/actueel/nieuws/kostenstijging-in-goederenvervoer-over-water-zet-door-extremen-verleden-tijd/ ; webshop "Kostenontwikkeling binnenvaart" https://panteia.nl/webshop/kostenontwikkeling-binnenvaart/ and "Kostenstructuur zand- en grindvaart" https://panteia.nl/webshop/kostenstructuur-zand-en-grindvaart-2023-en-raming-2024/
11. Rijkswaterstaat, "Kostentool binnenvaart" (2017; zip "Model kostenkengetallen extern", 19 Nov 2018). https://www.rwseconomie.nl/kengetallen/kostentool-binnenvaart ; https://www.rwseconomie.nl/documenten/publicaties/2016/februari/kostenbarometer-en-binnenvaarttool/binnenvaarttool
12. BALM, Marktbeobachtung Güterverkehr, Jahresbericht 2023, pp. 55-57 (Binnenschifffahrt: Frachten, Kleinwasserzuschläge, Gasölpreis 121.25 / 100.60 EUR per 100 l). https://www.balm.bund.de/SharedDocs/Downloads/DE/Marktbeobachtung/Jahresberichte/Jahr_2023.pdf?__blob=publicationFile&v=4
13. CBS StatLine 84050NED, "Binnenvaartdiensten; prijsindex 2015=100, 2014-2023" (OData: https://opendata.cbs.nl/ODataApi/odata/84050NED/TypedDataSet); successor table 85817 (2021=100) cited by CCNR. https://www.cbs.nl/nl-nl/cijfers/detail/84050ned
14. INFRAS / PLANCO for the Swiss Federal Statistical Office (BFS), "Statistik der Kosten und Finanzierung des Verkehrs - Integration der Schifffahrt 2015", Schlussbericht, 8 Nov 2017, pp. 20-27 and 48-49 (Rotterdam-Basel worked example, cost per ship movement, 10.5 EUR/t coal rate 2015, Rp/tkm). https://www.infras.ch/media/filer_public/58/df/58df5e97-487a-4809-b1c8-3e717d04005b/2961a_kfv-schifffahrt_schlussbericht_fin.pdf
15. Konings, R. (2009), Intermodal barge transport: network design, nodes and competitiveness, PhD thesis TU Delft (TRAIL T2009/11), Figs 2.7-2.8, ch. 5 (tariffs 50-140 EUR/TEU, feeder 95, sailing 15-20 vs handling 70-80 EUR/TEU). https://www.nginfra.nl/wp-content/uploads/Dissertation_Rob_Konings_13_nov_2009-4.pdf
16. Bureau Voorlichting Binnenvaart, "Kosten" (2006 lane quotes from Policy Research). https://bureauvoorlichtingbinnenvaart.nl/vervoer/logistieke-keten/kosten/
17. European Commission DG TREN, "Charging and pricing in the area of inland waterways" (2005), pp. 119-140 (value of vessel time 74-78 EUR/h; UNITE 218 EUR/h = 0.20 EUR/t/h; TREMOVE vessel classes). https://transport.ec.europa.eu/system/files/2016-09/2005_charging_and_princing_study.pdf
18. Contargo, "Anpassung des Kleinwasserzuschlags (Pegel Emmerich, Duisburg-Ruhrort, Köln, Kaub)", 9 Aug 2026. https://www.contargo.net/de/business/business-news/detail-business/anpassung-des-kleinwasserzuschlags-pegel-emmerich-duisburg-ruhrort-koeln-kaub/
19. THB, "Rhein: Schifffahrt berechnet Kleinwasserzuschlag", 4 Mar 2019 (ONE surcharge 35/45 EUR from Kaub < 150 cm). https://www.thb.info/rubriken/binnenschifffahrt/detail/news/rhein-schifffahrt-berechnet-kleinwasserzuschlag.html
20. agrarheute, "Rhein-Pegel fällt auf 51 Zentimeter - Kosten für Agrartransporte steigen", 17 Jul 2026 (Contargo 550/645 EUR). https://www.agrarheute.com/management/agribusiness/rhein-pegel-faellt-51-zentimeter-kosten-fuer-agrartransporte-steigen-641814 ; grain 25-30 -> 100 EUR/t: agrarheute 6 Aug 2026 (companion dossier).
21. swissinfo/SDA 27 Aug 2026 (CHF 22-28/t Rotterdam-Basel normal); Handelsblatt/WiWo 18 Aug 2022 (about EUR 20/t ARA-Karlsruhe, June 2022) [S]; Bloomberg opinion via enterpriseam 3 Aug 2026 ("around EUR 20/t") - all as cited in `giveup_thresholds_by_cargo.md`, section 1.1.
22. Hellenic Shipping News / S&P Global Platts, "Rhine water levels rebound, easing barge shipping strain" (Aug 2026): ARA-Basel 69.30 EUR/t on 1 Jul, 276.67 on 14 Aug, 256 later [S, page blocked]. https://www.hellenicshippingnews.com/rhine-water-levels-rebound-easing-barge-shipping-strain/
23. Port of Switzerland (Schweizerische Rheinhäfen), FAQ (transit times, 2,500 t / 96-192 TEU vessels). https://port-of-switzerland.ch/rheinhaefen/ueber-uns/faq/
24. Wiegmans, B. and R. Konings, "The performance of intermodal inland waterway transport" (TU Delft repository; Annex A terminal cost factors, 2011). https://repository.tudelft.nl/file/File_b54683cd-3db5-47c5-9e0c-09b629f71638
25. CCNR / DST, "Assessment of technologies in view of zero-emission IWT" (Study on financing the energy transition, Deliverable RQ C, ed. 1), Table 8 fuel consumption per fleet family. https://www.ccr-zkr.org/files/documents/EtudesTransEner/Deliverable_RQ_C_Edition1.pdf
26. Argus Media, "Rhine oil barge rates at record on near-impassable Kaub" (Aug 2026; records since assessments began in 2012; no levels in text). https://www.argusmedia.com/en/news-and-insights/latest-market-news/2858829-rhine-oil-barge-rates-at-record-on-near-impassable-kaub
