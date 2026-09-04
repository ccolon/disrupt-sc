# Give-up thresholds by cargo class: evidence dossier (Rhine low water 2018 and 2026)

Compiled 4 September 2026 for the whole-EU DisruptSC Rhine study. Purpose: calibrate, per cargo
class or product group, the delivered-price increase at which a shipper stops shipping rather than
paying the freight surcharge or rerouting (`delivered_price_increase_threshold`, currently a single
value; the scenario runs so far used 0.5, see `README.md` section 2.2).

Model rule recalled. For a shipment whose freight rises by a multiple `m` on the disrupted leg, the
delivered price of the goods rises by

    delta = s * (m - 1)      with s = freight cost / delivered value at normal rates,

and the buyer pays if delta is below the threshold, reroutes if a rail/road route is cheaper (rail/road
at 3-7 x the normal barge rate, i.e. delta_alt = s * (m_alt - 1)), and gives up otherwise. The
dossier therefore collects, for each cargo class: (i) the value density (EUR/t), (ii) the normal
barge rate on the relevant lane and hence `s`, (iii) the freight multiples actually reached in 2018,
2022 and 2026, (iv) whether the flow kept moving, was rerouted, deferred or abandoned, and (v)
econometric elasticities. Section 7 gives the recommended thresholds.

Tags. [C] official statistics or primary company/agency statement; [R] press report or single
secondary source; [S] seen only in a search-engine summary (page not opened); [E] my own estimate
or arithmetic. Prices in EUR unless stated; USD figures left in USD (2018 average EUR/USD about
1.18; the 2026 rate is not verified here, so USD-EUR conversions are marked [E]). Numbers that could
not be verified are flagged in the text and listed in section 8.

Companion files: `evidence_rhine2026_timeline.md` (2026 event chronology, freight rate track
day by day), `evidence_rhine_literature.md` (macro-econometric literature, Ademmer et al., Bedoya-
Maya et al., Jonkeren et al.), `update_20260903_supply_chain_damage.md` (DIHK survey, macro
estimates). Text extracts of the CCNR annual reports 2019/2023, CCNR Market Insights April 2019 /
November 2019 / April 2026, the CCNR "Act now!" reflection paper, the ICPR report 263 and the
BfG "Das Niedrigwasser 2018" report sit in the session scratchpad (`pdftxt/`); the Eurostat
extract used in section 2 is `scratchpad/iww_all.csv` (dataset `iww_go_atygo`, downloaded
4 Sep 2026, last update 28 Jul 2026).

---

## 0. Bottom line

1. **The observed volume losses mix four margins**: physical loading limits (the fleet cannot carry
   the cargo whatever the price), paying the surcharge, rerouting to rail/road, and *not shipping*
   (deferral into storage, drawing down stocks, cancelling). Only the last is the model's give-up.
   In 2018 the price channel was the dominant one for four months (Kaub below 78 cm on 107 days,
   dry-cargo rates x2.5, liquid rates x4-4.5, up to x7 to Basel); in 2026 the price channel
   operated in July and again from late August, while 3-23 August was a physical interruption at
   Kaub (loads 10-20 %, then none), so 2026 cancellations in that window say little about
   willingness to pay.
2. **High-value liquids and feedstocks kept moving at any price.** Refined products were shipped
   at freight equal to 35-45 % of the product value (2018: USD 5 to more than 35/bbl Rotterdam-
   Basel; 2026: EUR 215/t ARA-Karlsruhe, EUR 275/t or CHF 240/t ARA-Basel against a normal
   CHF 22-28/t). Naphtha, basic chemicals, coking coal and iron ore were railed and trucked at
   3-7 x the barge rate, i.e. +10-30 % of their delivered value, by BASF, thyssenkrupp, Shell,
   Lanxess, Evonik, Captrain/HKM. Their observed volume losses were capacity-limited (rail terminals
   and wagons, the right-bank Rhine rail line closed until 12 Dec 2026), not price-limited.
   Reading: threshold at or above 0.5 of delivered value.
3. **Low-value dry bulk was rationed by price.** The CCNR notes that in Oct-Nov 2018 freight rates
   for coal, iron ore and containers rose more than for sand, stones, gravel and agribulk (the
   market could not price these goods higher), that "large volumes of sand, stones and gravel were
   lost for German waterway transport, at least temporarily", and the construction industry in
   2026 reports scarcity, longer delivery times and price shocks rather than trucking at 2-3 x.
   With freight at 20-50 % of the ex-works value of sand and gravel, a x2.5 surcharge already adds
   30-75 % to the delivered price. Reading: threshold 0.15-0.3.
4. **Grain, feed, fertiliser and scrap sit in between.** Grain freight went from EUR 25-30/t to
   about EUR 100/t in 2026 (x4, i.e. +35-45 % of the wheat value); traders trucked (about 2 x the
   normal barge rate, +10-15 % of value), stored, and reported that "grain and oilseed shipments
   are increasingly unprofitable"; Switzerland had to release compulsory protein-feed stocks on
   1 Sep 2026 because imports had been insufficient "for weeks". Scrap merchants throttled purchases
   and steelworks cut scrap prices by EUR 5-25/t. Fertiliser volumes were flat in 2018 (+0.1 %
   in Germany) and no 2026 disruption is reported. Reading: thresholds 0.15-0.3.
5. **Containers reroute, they do not give up.** Surcharges of up to EUR 1,335 per 20' box at Kaub
   below 31 cm are 2-4 % of the value of a typical box; rail costs less than that. The Rhine lost
   10 % of its TEU in 2018 and 16 % in H1 2019 (lasting modal shift, CCNR). Reading: threshold
   non-binding (0.3 or higher); the model's reroute branch should carry containers.
6. **Elasticities.** Network-model own-cost elasticities of inland-waterway demand are about
   -0.33 to -0.39 in the normal range (Jourquin 2019), which reproduces the order of magnitude of
   the 2018 declines (-18 % on the traditional Rhine in Q3 2018 at x2.5 dry-cargo rates); Ademmer
   et al. find -0.87 % of German IWW tonnage per low-water day; Jonkeren et al. find the price per
   tonne up to +100 % at the lowest levels of 2003 with a welfare loss of 13 % of turnover.
   Commodity-specific IWW elasticities exist (Beuthe et al. 2001, 10 groups, Belgium; Jourquin and
   Beuthe 2019, NSTR groups, Europe/Benelux; Jourquin 2025) but their tables could not be
   retrieved (section 8).

---

## 1. Freight multiples and normal rates: the `m` and `s` inputs

### 1.1 Normal-water barge rates (denominator of `s`)

| Lane / cargo | Normal rate | Source, date | Tag |
|---|---|---|---|
| ARA - Karlsruhe, gasoil (tanker spot) | about EUR 20/t (June 2022, before the 2022 low water); EUR 27.4/t (1-9 Jul 2025, Maxau loads already cut to 1,350 t); about EUR 45/t at end-June 2026 (Kaub about 106 cm, surcharges already applied) | Handelsblatt/WiWo 18 Aug 2022 [S]; OPIS 10 Jul 2025 [R]; Reuters/freightperspectives 15 Jul 2026 [R] | [R]/[S] |
| ARA - Cologne, gasoil | EUR 16.8/t (1-9 Jun 2025) | OPIS 10 Jul 2025 | [R] |
| ARA cross-harbour | EUR 3.8/t (Jul 2025) | OPIS | [R] |
| Rotterdam - Basel, gasoil | CHF 22-28/t at normal water; USD about 5/bbl (about USD 37/t [E]) in July 2018 | swissinfo/SDA 27 Aug 2026 (TCS/Avenergy); EIA 8 Nov 2018 | [R]/[C] |
| Rotterdam - "south of the Kaub chokepoint", generic | "around EUR 20/t" in normal water | Bloomberg opinion 29 Jul 2026 via enterpriseam 3 Aug 2026 | [R] |
| Grain, southern Germany lane (Bayernhof) | EUR 25-30/t normal | agrarheute 6 Aug 2026 | [R] |
| Rotterdam - Duisburg, iron ore / coal in 6-barge push convoys (16,000 t) | no primary rate found; order of EUR 2-5/t | [E]; convoy size from Port of Rotterdam page via search [S] | [E] |
| Container, Rotterdam - Basel / Upper Rhine | no primary base rate found; order of EUR 150-300 per TEU | [E] | [E] |
| Rail / truck alternative during the event | truck "approximately doubled" the (normal) barge cost for grain; road and rail "two to three times more than usual during this period of high demand"; rail or truck "at a much higher cost" than barge for ore/coal | top agrar 11 Aug 2026; Chemistry World Aug 2026; EUROMETAL 16 Jul 2026 | [R] |

Reading: the model's "rail/road at 3-7 x the barge rate" is consistent with the 2026 agri and
chemicals statements (truck about 2 x normal barge for grain on short lanes, rail/road 2-3 x
their own usual price for chemicals, "much higher" for ore).

### 1.2 Freight multiples reached

| Event, segment, lane | Multiple `m` vs normal | Source | Tag |
|---|---|---|---|
| 2018 Oct-Nov, dry cargo, Rhine basin (Panteia index) | about x2.5; "freight rates for coal, iron ore and containers increased more strongly during the low-water period than for sand, stones, gravel and building materials, as well as agribulk" | CCNR annual report 2019, p. 68 | [C] |
| 2018 Oct-Nov, liquid cargo ARA-Rhine (PJK gasoil index) | "more than four times" (summary), "around 4.5 times higher than normal" (p. 69); Basel "by far the strongest price increase" | CCNR annual report 2019, pp. 11 and 69; CCNR Market Insight Nov 2019, p. 29 | [C] |
| 2018, Rotterdam-Basel distillate | USD about 5/bbl (Jul) to more than USD 35/bbl (late Oct): x7 | EIA, 8 Nov 2018 | [C] |
| 2018, Rotterdam-Duisburg distillate | about USD 1/bbl (Jul) to more than USD 4/bbl | EIA via search summary | [S] |
| 2018 generic | "increase in freight rates (up to seven times higher than at normal water levels)" | CCNR "Act now!" reflection paper, p. 30 | [C] |
| 2022 Aug, ARA-Karlsruhe tanker | EUR about 20/t (Jun) to about EUR 110/t: x5.5 | Handelsblatt/WiWo 18 Aug 2022 | [S] |
| 2022, indices (2015 = 100) | dry bulk spot Q3/Q4 2022 = 240.9/203.9 vs 118.1/159.1 in 2021; liquid 140.7/134.4 vs 92.9/114.2; all segments +42.5 % on average | CCNR annual report 2023, p. 11 | [C] |
| 2026, ARA-Karlsruhe tanker | EUR 45 (end Jun) -> 60-70 (13 Jul) -> 115-125 (17 Jul) -> 150-160 (4 Aug) -> about 200 (6 Aug, AFP) -> 215 assessed (mid Aug) -> 100-110 (28 Aug): x4.8 vs end-June, about x10 vs the EUR 20 normal | timeline file (Reuters, AFP, Bloomberg); Bloomberg/Yahoo Aug 2026 | [R] |
| 2026, ARA-Basel tanker | EUR 275/t mid-Aug; CHF 240/t vs CHF 22-28 normal: x9-10 | Bloomberg/Yahoo Aug 2026; swissinfo 27 Aug 2026 | [R] |
| 2026, Rotterdam to south of Kaub, generic | "nearly EUR 150/t" vs "around EUR 20": x7.5 | enterpriseam 3 Aug 2026 (Bloomberg) | [R] |
| 2026, grain (Bayernhof) | EUR 25-30/t -> about EUR 100/t: x3.5-4 | agrarheute 6 Aug 2026 | [R] |
| 2026, agri, seaports via Rhine | +100-120 %; low-water surcharges +70-80 % (Agravis); "some routes nearly tripled"; RWZ costs "double the normal level" | top agrar 11 Aug; Lebensmittelpraxis Aug; wirtschaft-und-industrie 31 Aug 2026 | [R] |
| 2026, scrap | "three- to fourfold" on individual connections, later stabilised | EU-Recycling scrap market report Aug 2026; Recyclingportal 12 Aug 2026 | [R] |
| 2026, steel raw materials | "at least four times their normal level in some cases" | miningmetalnews 12 Aug 2026 | [R] |
| 2026, container surcharge (Maersk, from 15 Jul 2026) | Kaub below 1.51 m: EUR 45/55/85 per 20'/40'/45'; below 0.31 m: EUR 1,335/1,560/1,670; no loading guarantee below 81 cm Kaub / 181 cm Duisburg-Ruhrort; Cologne below 1.05 m "transport is not guaranteed" | Maersk advisory 9 Jul 2026 | [C] |
| Container surcharge (Contargo standing tariff) | Kaub 150-131 cm EUR 40/50 (20'/40'); 130-111 EUR 55/75; 110-101 EUR 75/90; 100-91 EUR 90/145; 90-81 EUR 120/165; at or below 80 cm "by agreement" (no obligation to transport) | Contargo low-water page | [C] |
| Physical floor 2026 | loads 20 % (mid Jul), 10-15 % (28 Jul), 10-20 % (mid Aug); weekly cargo past Kaub 60 kt dry + 30 kt wet vs 300 + 100 normal (-77 %); CMA CGM: no barge transport possible below 24 cm | timeline file | [R] |

Reading for the model: the surcharge ladder 1.2 x to about 4 x used in the scenario matches the
Contargo ladder (x1.2 at Kaub 150-131 cm to x1.6 at 90-81 cm for a EUR 200/TEU base [E]) and the
tanker track up to early August; the x7-10 multiples of mid-August 2026 and late October 2018
belong to the weeks the model treats as closure (fleet cannot sail), and the stated container
tariffs stop at 80 cm ("by agreement").

---

## 2. What stopped moving: volumes by goods group

### 2.1 Germany 2018 by NST 2007 division (Eurostat `iww_go_atygo`, thousand tonnes, all traffic) [C]

Kaub below the 78 cm reference on 107 days (Aug 30, Sep about 15, Oct 30, Nov 30, Dec 3). The
annual change therefore averages about seven normal months with five disrupted ones; a -15 %
annual figure corresponds to roughly -30 to -35 % over Aug-Dec [E]. Total tonnage -11.1 %
(222.7 -> 197.9 Mt), monthly: H1 -1.1 %; Aug-Nov double-digit declines each month; November
-34 % (Destatis press release 112/2019) or -36.1 % (Destatis monthly, quoted by Verkehrsrundschau);
December -12.4 %. Containers 2.6 -> 2.4 million TEU (-8.3 %, "first decline in many years").

| NST 2007 | Goods | 2017 | 2018 | 2019 | 2018/17 | 2019/18 | Reading |
|---|---|---|---|---|---|---|---|
| GT01 | Agricultural products | 14,856 | 12,914 | 13,359 | -13.1 % | +3.4 % | cereals (GT011) -16.5 %; confounded by the 2018 drought harvest (German grain harvest down about a sixth) |
| GT02 | Coal (GT021 hard coal) | 30,787 | 26,221 | 23,315 | -14.8 % | -11.1 % | 2019 shows the structural decline (-11 % without low water); the low-water part of 2018 is perhaps -5 to -8 pp [E]; CCNR Q3 2018: coal -8 % |
| GT03 | Metal ores and other mining products | 57,066 | 51,967 | 54,802 | -8.9 % | +5.5 % | GT031 metal ores -9.2 %; GT035 sand, gravel, stone, clay -9.3 % then +16.2 % rebound in 2019: the 2018 loss was largely deferred, not lost demand |
| GT04 | Food, beverages, tobacco | 8,475 | 7,554 | 8,121 | -10.9 % | +7.5 % | GT046 grain mill products/feed -6.9 %; GT044 oils and fats -10.8 % |
| GT06 | Wood, paper | 2,939 | 2,717 | 2,916 | -7.6 % | +7.3 % | |
| GT07 | Coke and refined petroleum | 37,986 | 32,885 | 38,093 | -13.4 % | +15.8 % | GT072 refined products -11.7 % then +22.9 %: deferred deliveries (ARA stocks rose, section 4.6); GT071 coke -21.8 % |
| GT08 | Chemicals | 23,547 | 20,786 | 21,844 | -11.7 % | +5.1 % | GT081 basic chemicals -11.3 %; **GT082 fertilisers +0.1 %**; GT083 plastics/rubber in primary form -20.0 %; GT085 other chemical products -23.3 % |
| GT09 | Other non-metallic minerals | 3,443 | 3,289 | 3,245 | -4.5 % | -1.3 % | GT093 (other non-metallic mineral products) -49.6 % on 1 Mt |
| GT10 | Basic metals, fabricated metal products | 12,258 | 10,465 | 10,096 | -14.6 % | -3.5 % | GT101 basic metals -18.3 %: outbound steel (thyssenkrupp force majeure on shipments, section 4.8) |
| GT11 | Machinery | 771 | 667 | 786 | -13.5 % | +17.8 % | small volumes |
| GT14 | Secondary raw materials, wastes | 11,840 | 11,402 | 11,359 | -3.7 % | -0.4 % | scrap and wastes (GT142) -3.6 %: mostly short-haul Lower Rhine / canal flows, little affected |
| GT19 | Unidentifiable goods (GT191 in containers) | 15,246 | 13,828 | 13,401 | -9.3 % | -3.1 % | GT191 +2.8 % while TEU fell 8.3 %: classification of container contents changed, do not use |
| TOTAL | | 222,731 | 197,904 | 205,066 | -11.1 % | +3.6 % | |

Quarterly by segment, Germany, Q3 2018 vs Q3 2017 (CCNR Market Insight April 2019, p. 17, based
on Destatis) [C]: metals -22 %, chemicals -16 %, sand and stones -16 %, agricultural products
-14 %, iron ore -13 %, coal -8 %; export traffic -22 %, import traffic -14 %, national traffic
-7 %. Traditional Rhine Q3 2018: 38.2 Mt, -18 %; containers -20 %, liquid cargo -16 %, dry cargo
-14 % (Middle and Upper Rhine carry 42 % of liquid and 49 % of container transport performance).
Note that Q3 2018 contains only the first two low-water months; Q4 was worse (Destatis November
-34/-36 %) but no Q4 breakdown by segment was retrieved (section 8).

Full-year 2018 on the traditional Rhine (CCNR annual report 2019, pp. 30-31, Destatis-based) [C]:
"The dry cargo segment with the lowest rate of decrease was sand, stones and building materials
(-5 %). Liquid cargo registered falling volumes as well (chemicals: -13 %, mineral oil products:
-14 %). Container transport decreased by 13 % (net weight in containers), compared to -10 % for
the TEU." Rhine total -11.8 % (BDB). The report's chart gives the other segments (coal, iron ore,
agribulk, metals) only graphically; the numbers were not extractable from the PDF (section 8).
Tributaries 2018: Main about -20 %, Moselle -16.4 %, Saar -28 % (GDWS via CCNR April 2019); lock
cargo Iffezheim -23.6 %, Wesel-Datteln canal -24.9 %, Kostheim/Main -21.8 % (WSV via BfG 2018
report); Mannheim port handling -42 % (BfG 2018 report, period not stated) [C].

Ports 2018 [C]: duisport 68.3 -> 65.3 Mt, bulk cargo loading about -10 % attributed to the low
water, mineral oil and chemicals "stable", steel "significant declines", coal structural (Bonapart,
Jan 2019). Port of Rotterdam 2018: agribulk -11.6 % (incoming -13.6 %), iron ore and scrap
-3.6 %, coal +2.3 %, mineral oil products -1.9 %, dry bulk -3.2 % (Port of Rotterdam annual
figures via FreightWaves/safety4sea) [R]. Antwerp inland-waterway traffic 2018: ores and metal
waste 22.1 -> 17.9 Mt (-19 %), petroleum products -8.6 %, chemicals +3.4 %, feed and food +10 %
(CCNR 2019, p. 61) [C]. Netherlands 2018 (Eurostat): total -2.7 %; metal ores -10.9 %, coal
-3.8 %, cereals -6.4 %, refined products -6.6 %, basic chemicals -2.0 %, fertilisers +8.6 %, basic
metals -6.3 %, sand/gravel +4.2 %; Q3 2018 Dutch exports: dry bulk -8 %, liquid -9 %, containers
-6 %, national traffic up (CCNR April 2019). The Dutch side (short hauls in deep water) was barely
affected: the losses are on the German Rhine above Duisburg.

Reading of 2.1. Ranking the 2018 German annual losses net of structure (coal, containers
excluded): plastics and "other chemical products" (-20/-23 %), basic metals (-18 %), cereals
(-17 %), refined products (-12 %), basic chemicals (-11 %), sand/gravel and metal ores (-9 %),
scrap (-4 %), fertilisers (0 %). This ordering is NOT the ordering of value density; it is the
ordering of (a) exposure of the flow to the Middle/Upper Rhine (chemicals, refined products,
cereals to/from the south) and (b) whether the goods have a physical alternative (steel products
and chemicals could not be loaded on the shipper's own fleet). The by-goods statistics therefore
mostly measure the physical channel plus deferral; the price-rationing signal has to be read
from the freight-rate differentiation (CCNR: rates for sand/gravel/agribulk rose less than for
coal/ore/containers) and from the direct statements of section 4.

### 2.2 2022 as a second reference (Kaub below the reference level on 41 days, July-August)

Entire Rhine 2022 vs 2021 (CCNR annual report 2023, p. 11) [C]: coal +10.6 % (energy crisis:
paid whatever the freight), containers -12.2 %, sand/stone/gravel -11.5 % (-12.1 % in the
chapter text), mineral oil products -9.5 %, metals -7.5 %, agri-food -5.9 %, iron ore -2.8 %,
chemicals -1.6 %. Germany 2022 vs 2021 (Eurostat): total -6.5 %; coal +12.0 %; sand/gravel
-8.1 %; cereals -9.6 %; refined products -4.1 %; chemicals -15.8 % (basic -17.7 %, fertilisers
-8.2 %); basic metals -3.3 %; scrap/wastes -16.7 %. Reading: when the margin justifies it (coal
in the 2022 power crisis) a low-value bulk keeps moving through x2 rates; sand/gravel and
containers again lead the losses.

### 2.3 2026 (July-September, event still running): partial evidence

- Mannheim ports, waterside handling, July 2026 vs July 2025 [C] (Hafen Mannheim via
  Binnenschifffahrt Online, Aug 2026): total -31.0 % (330,818 t); coal/crude oil/gas -43.0 %;
  chemicals -56.6 %; metals -50.4 %; containers -24.4 % (4,660 TEU); **ores, stones, earths
  +47.0 %** (local Upper Rhine gravel and stone flows that do not cross Kaub); gauge 1.37 m vs
  2.24 m. January-July -6.2 %.
- Duisburg (duisport, 21 Aug) [C]: vessel loading about one third of usual, 400-450 calls/week vs
  280-300; thyssenkrupp still receiving 50,000-60,000 t/day by ship (13 Aug) [R].
- Kaub cross-section, week to about 13 Aug [R] (KBN/Schuttevaer): 60 kt dry + 30 kt wet vs 300 kt
  + 100 kt normal.
- Containers [R]: Contargo suspended regular services to the Upper Rhine and Rhine-Main (6 Aug);
  Maersk: "most inland ports along the Rhine cannot be reached by barge" (20 Aug); Swiss Rhine
  ports: container ships no longer operating to Basel (20min, Aug); Kombiverkehr raised the
  Cologne-Basel rail shuttle from 3 to 5 weekly round trips from 7 Sep 2026 (+ about two thirds
  capacity) [C].
- Chemicals [R]: European crackers already at about 70 % in July for demand reasons; Rhine-corridor
  cracker run rates expected 65-70 % through early September; ARA naphtha stocks 598 kt mid-August
  (+75 % in a month), "volumes struggle to reach inland crackers" (Bloomberg/Kpler, Aug 2026):
  the cargo existed and could not move.
- Agri [R]: RWZ (Rhein-Main) warehouses filling, about 500 kt of grain per season of which half
  normally by water; storage on farms; Bayernhof "shifting deliveries or switching to trucks";
  BayWa organised full trains (sections 4.4, 4.5).
- Switzerland [C]: 3.8 Mt imported via the Rhine ports in 2025 (10-12 % of Swiss imports): mineral
  oil about 2.0 Mt (53 %, about one third of Swiss fuel demand; Avenergy: 22 % of mineral-oil
  imports come by Rhine, 31 % rail, 41 % pipeline, 6 % road), stones and earths 516 kt, food and
  beverages 288 kt, chemicals 264 kt, metals 239 kt; tankers to Basel at about 25 % load (mid
  July); "some clients have switched to road or rail" (Rhenus Alpina, Aug); compulsory stock
  release for protein feed from 1 Sep 2026 (up to 20 %, about 16,000 t, to end-Feb 2027) because
  imports had been insufficient for weeks; no release of fuel stocks (4.5 months of cover) or
  fertiliser (prices up, no disruption) as of 4 Sep 2026 (BWL).
- German official monthly statistics for July 2026 (Destatis inland shipping by goods) are due
  mid/late September; August in October-November.

---

## 3. Value density, cost shares and the delivered-price increase per class

### 3.1 Value density (EUR or USD per tonne)

| Product | 2018 level | 2026 level | Source | Tag |
|---|---|---|---|---|
| Sand, gravel (ex-works, concrete grades) | order EUR 8-15/t [E] | EUR 14-90/t across grades and regions, concrete sand/gravel at the low end; delivery adds 50-100 % | German 2026 price lists (KSW, Glueck-Kies, Herrmann) via handwerk.cloud/clean-invoice | [R] |
| Thermal coal (S. African FOB, close to API2) | USD 106/98/102/100/92/95 Jul-Dec 2018 | USD 91-94 Jan-Mar 2026; API2 average USD 97 Nov 2025-Jul 2026 | IndexMundi; Investing.com via search | [C]/[S] |
| Iron ore 62 % Fe CFR China | USD 65-73 Jul-Dec 2018 | USD 99-106 Jan-Mar 2026, USD 96 late Aug 2026 | IndexMundi; futures via search | [C]/[S] |
| Wheat (US HRW Gulf; Matif similar order) | USD 204-237 Jul-Dec 2018 | USD 250-276 Jan-Mar 2026 | IndexMundi | [C] |
| Urea (granular) | about USD 250-300 [E] | USD 390-440 Aug 2026 | igrownews / imarc via search | [S] |
| Gasoil / diesel (ICE gasoil) | about USD 600-720 in Q4 2018 [E] | about USD 680 (Sep 2026 quote) | liveoilprices via search | [S] |
| Naphtha FOB Rotterdam | about USD 550-650 [E] | USD 838 (22 Jul 2026, Platts) | S&P Global via search | [S] |
| Hot-rolled coil, N. Europe ex-works | about EUR 550-600 [E] | EUR 716-722 (Aug 2026, Fastmarkets) | via search | [S] |
| Steel scrap | about EUR 250-300 [E] | about EUR 300-350, cut by EUR 5-25/t in Aug 2026 | EU-Recycling Aug 2026 | [R]/[E] |
| Containerised goods | EUR 2,000-5,000 per tonne of goods; EUR 20-50 k per TEU at about 10 t | BACI EU-mix by sector (below) | [E] |

BACI-2023 EU-mix unit values used by the model itself (`disrupt-sc-data/EU/Economic/sector_table.csv`,
USD/t, identical across countries): A01 agriculture 945 (dominated by high-value produce, not
grain), B05 coal 201, B06 crude oil 620, B07 metal ores 283, B08 other mining (sand, gravel,
stone, salt) 81, C10T12 food 2,052, C16 wood 933, C17_18 paper 1,212, C19 refined petroleum 839,
C20 chemicals 2,659, C22 rubber/plastics 3,511, C23 non-metallic minerals 852, C24A basic iron and
steel 1,043, C24B non-ferrous 11,958, C25 fabricated metals 4,808, C28 machinery 18,515, C29
vehicles 13,080. Caveat: these are sector averages of traded goods; the barge-borne part of a
sector is systematically cheaper than its trade average (grain within A01, bulk chemicals within
C20, slabs and coils within C24A).

### 3.2 Cost share `s` and delivered-price increase at the observed multiples

Normal rates from 1.1 (dry-bulk Duisburg and container base rates are estimates [E]); values from
3.1 at 2026 levels unless stated; delta = s (m - 1). "Alt" = rail/truck at 3-7 x the normal barge
rate, or the observed alternative when known.

| Cargo class, lane | Value EUR/t | Normal barge EUR/t | s | m observed | delta at m | delta at alt | Observed behaviour (section 4) |
|---|---|---|---|---|---|---|---|
| Sand, gravel, crushed stone; short/medium haul | 10-20 | 3-6 [E] | 0.2-0.5 | 2.5 (2018 dry) | +30 to +75 % | truck x2-3 barge: +40 to +150 % | rates rose less than for other bulk (demand capped), volumes lost "temporarily", construction shortages 2026, local flows +47 % at Mannheim |
| Thermal coal, Rotterdam-Duisburg/Ruhr | 80-90 | 3-5 [E] | 0.04-0.06 | 2.5-4 | +6 to +18 % | rail EUR 12-20 [E]: +10 to +20 % | 2018: RWE Hamm supply problems, four Rhine coal plants restricted; 2022: coal +10.6 %; 2026: stocks + rail, EnBW low double-digit EUR m hit, Uniper unaffected |
| Thermal coal, Rotterdam-Upper Rhine (Mannheim, Karlsruhe) | 80-90 | 10-12 [E] | 0.12-0.15 | 2.5-5 | +20 to +60 % | rail EUR 25-35 [E]: +20 to +40 % | GKM and RDK supplied by rail at low water (structural rail base load at RDK since block 8) |
| Iron ore and coking coal, Rotterdam-Duisburg | 85-105 (ore), 150-250 (coking coal, [E]) | 3-5 [E] | 0.03-0.06 | 2.5-4 | +5 to +18 % | rail "much higher cost": +10 to +30 % | thyssenkrupp 2018: 60 vessels chartered, DB deal 3,000 t/day coal by rail, still 200 kt production lost; 2026: rail share doubled from about 5 %, hot metal reduced, furnaces kept hot |
| Grain, oilseeds; south Germany <-> seaports | 200-260 | 25-30 | 0.10-0.15 | 3.5-4 (2026) | +30 to +45 % | truck x2 normal barge: +10 to +15 %; rail full trains similar | trucked, railed, stored, deferred; "increasingly unprofitable"; Swiss protein-feed stocks released; Q3 2018 agri -14 %, cereals 2018 -16.5 % (harvest confounded) |
| Feed (soymeal, oil meals) | 300-450 | 25-30 | 0.06-0.10 | 3.5-4 | +18 to +30 % | +8 to +15 % | Agravis: supplementary trucking from mills; Swiss shortfall "for weeks" then stock release |
| Fertiliser (urea, N products) | 350-450 | 25-30 | 0.06-0.09 | 3.5-4 | +17 to +27 % | +8 to +14 % | 2018 volumes flat (+0.1 %); 2026: prices up, no disruption reported; Swiss N-stock release Dec 2018 |
| Crude oil | 450-550 | pipeline-fed refineries (Miro, Shell Rheinland, Bayernoil, Cressier); barge share negligible | n/a | n/a | n/a | n/a | no give-up evidence; not a Rhine barge flow |
| Gasoil/diesel/gasoline, ARA-Karlsruhe | 600-700 | 20 | 0.03 | 10 (2026 peak), 5.5 (2022) | +30 % (2026), +15 % (2022) | rail/road x3-7: +6 to +20 % (capacity-limited) | paid; ADAC "supply secured"; retail +7-8 ct/l regional spread (DE), +12-16 Rp/l (CH); 2018: paid x7 to Basel, still reserve releases and +20 ct/l at the pump |
| Gasoil/diesel, ARA-Basel | 600-700 | 22-28 | 0.035-0.045 | 9-10 | +35 to +45 % | rail (31 % of Swiss imports already rail) | paid; Volenergy 40 % of volume via Rhine kept sourcing; fuel stocks not released (2026), released 2018 and 2022 |
| Naphtha, ARA-Ludwigshafen/Wesseling | 700-800 | 20 [E] | 0.025-0.03 | 10 | +25 to +30 % | rail: +5 to +18 %; 27 railcars per 1.2 kt barge; only 3 ARA block-train terminals, at capacity | paid whatever available; cracker cuts were physical (barge loads 20 %, naphtha piling up in ARA) |
| Basic chemicals (methanol, benzene, acids, glycols) | 400-1,500 | 15-25 [E] | 0.01-0.06 | 5-10 | +5 to +50 % | rail/road x2-3 "usual": +3 to +30 % | Lanxess, Evonik, Covestro, BASF shifted to rail/road; cancellations were on the output side (force majeure) |
| Steel products, slabs, coils | 550-720 | 8-15 [E] | 0.01-0.03 | 4 | +3 to +8 % | rail/truck: +2 to +15 % | thyssenkrupp force majeure Oct 2018 on shipments (own fleet stopped): physical; Q3 2018 metals -22 % |
| Scrap | 300-350 | 8-12 [E] | 0.02-0.04 | 3-4 | +5 to +12 % | truck x2-3: +3 to +10 % | merchants throttled purchases, stocks piled up, mills cut scrap prices EUR 5-25/t: partly deferred |
| Containers, Rotterdam-Basel/Upper Rhine | 20-50 k per TEU | 150-300 per TEU [E] | 0.005-0.01 | surcharge up to 1,335/20' (x5-9 on the leg) | +2.5 to +4 % of box value | rail +EUR 200-400/TEU [E]: +0.5 to +1 % | rerouted to rail; Rhine TEU -10 % (2018), -16 % (H1 2019); Bedoya-Maya: -0.2 %/day |

Reading: for `s` below about 5 % (all liquids, ore, coking coal, steel, containers) even a x10
surcharge stays below +45 % of value and the observed behaviour is to pay or reroute; for `s` of
10-15 % (grain, feed, thermal coal to the Upper Rhine) the x4 surcharge gives +30-60 % and the
observed behaviour is reroute-plus-defer; for `s` above 20 % (sand, gravel, stone, also cement
clinker, salt, recycled aggregates) any multiple above about 2 exceeds half the value and the
flows stop or switch to local sources.

---

## 4. Direct statements: cancellations and demand destruction versus paying any price

### 4.1 Sand, gravel, building materials

- CCNR annual report 2019, p. 68 [C]: in Oct-Nov 2018 "the freight rates for coal, iron ore and
  containers increased more strongly during the low-water period than for sand, stones, gravel and
  building materials, as well as agribulk". The same report, p. 164 [C]: "Large volumes of sand,
  stones and gravel were lost for German waterway transport due to these low water periods, at
  least temporarily" (correlation between construction activity and IWW sand/gravel transport
  broken in autumn 2015, 2016 and H2 2018). Reading: the market could not pass a x2.5 surcharge on
  to gravel shippers; volumes were deferred, and the 2019 rebound of German GT035 (+16 %) shows
  the demand was postponed rather than destroyed.
- Traditional Rhine 2018: sand/stones/building materials -5 %, the smallest dry-cargo decrease
  (CCNR 2019, p. 30) [C]; Germany Q3 2018 sand and stones -16 % (CCNR April 2019) [C]. The two are
  consistent only if the losses concentrated on the Middle/Upper Rhine and on tributaries while
  the Lower Rhine local trade continued.
- 2022: sand/stone/gravel -11.5 % on the Rhine, the second-largest loss after containers (CCNR
  2023) [C].
- 2026 [R]: WirtschaftsWoche 17 Aug (HDB, VBU Hessen): sand and gravel "scarcer and therefore more
  expensive", delivery times longer, suppliers announce bottlenecks for sand, gravel, bitumen,
  split, natural stone if the situation persists; "third price shock within a few years", many
  increases "remain permanent"; diversion to rail and road "only possible to a limited extent and
  usually significantly more expensive". No quantified cancellations. Mannheim July 2026: ores,
  stones, earths +47 % (local flows) [C]. Swiss Rhine ports: 516 kt/yr of stones and earths at
  stake [R].
- No statement of the form "gravel deliveries cancelled at price X" was found for either year;
  the give-up reading rests on the rate differentiation, the temporary loss and the 2026 scarcity
  language (section 8).

### 4.2 Thermal coal to power plants

- 2018 [C]/[R]: BfG "Das Niedrigwasser 2018" (p. 11) and ICPR report 263 (p. 11): "several power
  plants along the Rhine had to throttle electricity production", among them the coal plants
  Bergkamen, Walsum, Mannheim (GKM) and Rheinhafen-Dampfkraftwerk Karlsruhe (RDK); causes given
  as "supply bottlenecks and elevated water temperatures". AFP/phys.org 26 Oct 2018: RWE "struggled
  to supply coal to its Hamm power plant". GKM is supplied by rail during low water (LOK Report;
  ka-news: RDK coal comes "primarily by ship", rail "mainly during restricted shipping, especially
  in winter or at low water", with a year-round rail base quantity planned with block 8) [R].
  Reading: plants with rail sidings paid for rail; plants dependent on barge stocks reduced output
  when stocks ran out. The dark spread, not the transport share, decides whether coal is worth
  moving: at EUR 85/t coal and s of 5-15 %, a x4 surcharge adds EUR 10-40/t of coal, i.e. about
  EUR 4-16/MWh of electricity [E], which is decisive for a marginal plant and irrelevant for a
  must-run one.
- 2022 [C]: coal on the Rhine +10.6 % despite 41 low-water days; Uniper warned in Aug 2022 that
  Staudinger 5 (510 MW) and Datteln 4 might run irregularly for lack of coal; Steag had coal on
  site (Reuters/ZFK 4 Aug 2022) [R].
- 2026 [R]: EnBW: disruption "will reduce its earnings by a low double-digit-million-euro figure"
  (Bloomberg 11-12 Aug); Uniper CEO: "our power plants are not affected", few German coal plants,
  no dependence on coal transport (dpa 11 Aug); energate survey: Steag, Uniper, EnBW, RWE report no
  cuts for cooling water, barge coal "compensated by stocks and rail transport" (Stuttgarter
  Nachrichten 7 Aug); Captrain: 3-4 extra weekly round trips Wilhelmshaven-Ruhr at about 1,900 t
  each, about 4,000 t/week extra on the existing service, coke Germany-France from 4 to 5 round
  trips (Verkehrsrundschau, Aug); RheinCargo added Rotterdam-Duisburg coal trains for HKM
  (railmarket, 2026) [S].
- Reading: coal to steel = paid (see 4.3); coal to power = paid where a rail siding exists and the
  plant is in the money, otherwise stocks are run down and output reduced. Threshold 0.15-0.3.

### 4.3 Iron ore, coking coal, steel

- thyssenkrupp 2018 [C]/[R]: force majeure declared 19 Oct 2018 on steel product shipments
  (Platts); own push-barge fleet could not run for six weeks; up to 60 shallow vessels hired; still
  200,000 t of production lost, only partly recouped; low triple-digit million EUR loss; long-term
  Deutsche Bahn deal for about 3,000 t/day of coal by rail; mid double-digit million EUR
  investment in logistics; normal supply 60,000 t/day from Rotterdam (gcaptain 27 Feb 2019). AFP
  26 Oct 2018: production cut at Duisburg for lack of raw materials. ArcelorMittal declared force
  majeure at Duisburg-Ruhrort (mining.com, 2018; page not opened) [S].
- thyssenkrupp 2026 [R]: push convoys stopped 14 Jul; chartered smaller external vessels; hot
  metal production reduced (EUROMETAL 16 Jul); "transport by rail or truck was at a much higher
  cost"; 50,000-60,000 t/day still arriving by ship, rail share "roughly doubled" from about 5 %,
  "far from letting any blast furnace cool down", "customer supply not at risk" (dpa 13 Aug);
  inventories 1-2 months (miningmetalnews 12 Aug). Badische Stahlwerke Kehl: 60 % of inputs and
  50 % of products by river, about 200 kt/month (DIHK/IHK Aug 2026). German steel industry
  transport split 2024: rail 49.3 %, IWW 31.6 %, truck 19.2 % of 120.7 Mt (WV Stahl via
  Recyclingportal) [C].
- Reading: ore and coking coal are shipped at any freight the alternatives can carry (+10 to +30 %
  of ore value by rail); the shortfall was the rail ceiling, not price. Threshold at or above 0.3.
  Steel products (s of 1-3 %) never give up on price; the 2018 -22 % in metals is the
  physical/fleet channel plus force majeure.

### 4.4 Grain and oilseeds

- 2018 [C]/[R]: German cereals by IWW -16.5 % (annual) and agricultural products -14 % in Q3,
  with the drought harvest as confounder; Port of Rotterdam agribulk -11.6 % (incoming -13.6 %).
  Traders' reaction as reported in 2018 (top agrar / agrarheute archive via search): "trading
  companies responded with increased warehousing and a shift to rail and road", BayWa organised
  full trains for the Lower Rhine and Benelux [S]. Secondary source (ourrhine.eu): "some firms
  stored their grain in Rotterdam for the time being instead of sending it on an expensive trip"
  [S, unverified].
- 2026 [R]: Bayernhof (S. Heinrich): grain freight from EUR 25-30/t to about EUR 100/t, deliveries
  shifted or switched to truck (normally 2-4 shipments/week) (agrarheute 6 Aug). BayWa: three to
  four times the number of vessels for the same cargo, own storage, full trains to Lower Rhine and
  Benelux mills. RWZ (C. Kempkes): costs "double the normal level", about 500 kt of grain per
  season of which about half normally by water, trucks as alternative, warehouses filling; 80 kt
  emergency storage at Worms (wirtschaft-und-industrie 31 Aug; top agrar 11 Aug). AMI/top agrar
  10 Aug: "grain and oilseed shipments increasingly unprofitable", farms with storage keep the
  harvest on site. top agrar 11 Aug: no significant export cancellations reported; Agravis routes
  via the IJsselmeer with "significantly lower surcharges". Lebensmittelpraxis (Aug): Agravis
  surcharges +70-80 %; 21 Mt/yr of agri-food goods by IWW (13 Mt grain and plant products, 8 Mt
  food, feed, oils).
- Reading: at +30-45 % of value on the surcharged barge, shippers reroute to truck (+10-15 %) as
  long as trucks exist, and otherwise defer into storage; deferral is the give-up of a seasonal
  flow with storage. Threshold 0.15-0.3, with the reroute branch active.

### 4.5 Feed and fertiliser

- Feed 2026 [C]/[R]: Agravis: oilseed meals need supplementary trucking from the mills, feed supply
  "no fundamental problems"; Switzerland (almost entirely import-dependent for soymeal): imports
  "insufficient for weeks", compulsory protein-feed stocks opened from 1 Sep 2026 (up to 20 %,
  about 16,000 t, to end-February 2027) (BWL; Blick 1 Sep). Reading: a real shortfall at the end
  of the chain; feed at s of 6-10 % should have been shipped at +20-30 %, so the shortfall is
  capacity (no barges past Kaub, rail to Basel limited until 2030 by the corridor works) more than
  price. Threshold 0.2-0.3.
- Fertiliser [C]/[R]: Germany 2018 GT082 +0.1 % (no decline); Netherlands +8.6 %; Switzerland
  released compulsory stocks of pure nitrogen for fertiliser production (with liquid fuels,
  edible oils and fats, feed) in December 2018 (ICPR 263, p. 11). 2026: DRV (14 Aug): fertiliser
  orders for spring 2027 "partly less than 50 % of last year's quantity" (attributed to prices and
  farmers' hesitation, not to transport); RWZ: fertiliser imports face rising prices (31 Aug);
  BWL (4 Sep): prices up, no supply disruption detected; top agrar: sulphur-based fertilisers
  among the affected products. Reading: a seasonal, storable input with s of 6-9 %: deferral
  within the season, no evidence of cancellation. Threshold 0.2-0.35, low confidence.

### 4.6 Refined products (gasoil, diesel, gasoline, heating oil, jet)

- 2018 [C]: Rotterdam-Basel distillate barge freight from about USD 5/bbl (July) to more than
  USD 35/bbl (late October); rack premia over ARA rose in Duisburg from USD 0.15 to more than
  0.20/gal and in Karlsruhe from about 0.20 to more than 0.40/gal; ARA distillate stocks rose from
  15.7 million bbl (early July, 6.9 million below the 5-year average) to more than 21 million
  (18 Oct, above average): product accumulated in ARA instead of moving upriver (EIA, 8 Nov 2018).
  Germany released strategic reserves of gasoline, diesel and jet on 26 Oct 2018 for Hesse,
  Baden-Wuerttemberg, Rhineland-Palatinate and NRW, the fourth release in 40 years (AFP/phys.org);
  Switzerland drew on compulsory stocks in summer 2018 (BWL, via bzbasel) and released further
  stocks in December (ICPR 263); pump prices rose by about 20 ct/l with shortages at some filling
  stations, while German refineries earned more (ICPR 263, p. 11). CCNR: in 2018 the Swiss
  destination showed by far the strongest price increase (Market Insight Nov 2019, p. 29).
- 2022 [C]: Swiss compulsory stocks: 245,000 m3 (6.5 %) shortfall permitted from 22 Jul 2022 (BWL
  via bzbasel).
- 2026 [R]/[C]: ARA-Karlsruhe EUR 45 -> 215/t, ARA-Basel EUR 275/t or CHF 240/t vs CHF 22-28
  normal; "the benchmark freight rate ... rose about 400 % in two months" (Bloomberg chart via X)
  [S]; AFP 6 Aug: EUR 200/t Karlsruhe-ARA; Argus (late July): rates to Duisburg, Frankfurt and
  Karlsruhe at records since 2012, "very little spare capacity for additional rail shipments",
  gasoline availability deteriorating on spot markets; Miro (310 kb/d) increasingly sourced by
  buyers, Shell "increasing storage use and diverting shipments to rail, road and pipelines";
  ADAC 11 Aug: fuel supply "secured", regional pump-price spread 7-8 ct/l; Switzerland: TCS/
  Avenergy +8.5 Rp/l (mid July) rising to +12-16 Rp/l (late August), rule of thumb CHF 14/t of
  freight = 1 Rp/l; Volenergy keeps 40 % of its volume on the Rhine; fuel compulsory stocks (4.5
  months) not released as of mid-July; BWL 4 Sep: September supply secured provided rail, road,
  pipeline and the Cressier refinery run without interruption.
- Reading: paid at +30-45 % of value; the residual demand was met from strategic and company
  stocks (a drawdown, which the model represents as inventories) and by rail/pipeline. No
  price-based give-up observed even at x7-10. Threshold at or above 0.5.

### 4.7 Naphtha, basic chemicals, intermediates

- BASF 2018 [C]: "nearly impossible to receive deliveries of raw materials via ship at the
  Ludwigshafen site for much of the third and fourth quarter"; capacity utilisation reduced; 2018
  earnings lower by about EUR 250 million (about EUR 200 million in Q4) (BASF news release
  26 Feb 2019); TDI production stopped in Ludwigshafen because of the low water (Reuters 26 Nov
  2018, via BfG report); about 40 % of incoming volumes normally arrive by ship (Chemistry World).
  CCNR "Act now!" Figure 14 reproduces BASF's own 2018 curve of transport volume against freight
  cost (not legible in the PDF extract).
- 2026 [R]: BASF deploys low-water vessels (Stolt Ludwigshafen: about 800 t at Kaub 30 cm, 5,100 t
  max), "making every effort to support the supply of key raw materials by using alternative modes
  of transport such as trucks and rail" (30 % of Ludwigshafen goods already by rail), first plants
  throttled mid-August, surfactant supplies cancelled early August, EUR 100 m+ combined-transport
  terminal expansion decided 14 Aug (to 370,000 loading units by 2028); Covestro: "shipping
  disruptions are affecting supply and production at certain sites", polyether polyol shipments
  from Dormagen cancelled, 60 trucks per 1,500 t barge; LyondellBasell force majeure on butadiene
  from Wesseling; Lanxess and Evonik shift "a part of freight to rail and road where possible";
  Shell Wesseling cracker offline since early July (to end-September), Gelsenkirchen refinery in
  turnaround; naphtha: about 4 Mt/yr to inland crackers by pipeline or barge, 27 railcars replace a
  1.2 kt butane barge, the three ARA block-train terminals "already at maximum capacity"; cracker
  run rates 65-70 % expected through early September, ARA naphtha stocks 598 kt (+75 %). VCI
  (3 Sep): 20 Mt of chemical products moved by inland shipping in 2024; no separate low-water
  figure before Q3 results (BASF 27 Oct 2026).
- Reading: the chemical industry pays any freight the alternatives can carry (s of 1-6 %, so even
  x10 stays below +50 %); its 2018 and 2026 losses came from physical unavailability of barges
  and of rail slots. The output-side cancellations (force majeure) are the downstream propagation
  of that shortfall, not a price decision. Threshold at or above 0.5.

### 4.8 Scrap and secondary raw materials

- 2018 [C]: German secondary raw materials and wastes by IWW -3.7 % (short-haul, Lower Rhine and
  canals, little affected).
- 2026 [R]: bvse/BDSV/VDM (12 Aug): barges limited to about one third of capacity on the affected
  sections, three times the trips for the same tonnage, stockpiles rising, storage costs, flows to
  steelworks interrupted, 760,000 extra truckloads per year if half of the 38 Mt barge volume
  moved to road; EU-Recycling scrap market report (Aug): ships loaded "half or a third of normal
  quantities", freight "three- to fourfold" on some connections, "in some areas low water brings
  freight traffic to a complete standstill", merchants "attempted to throttle scrap purchases"
  because of logistics bottlenecks and financing costs of inventory; steelworks cut scrap prices
  by EUR 5-25/t (West -25, North -5 to -10, East -4, Southwest up to -5).
- Reading: with s of 2-4 %, a x3-4 surcharge is +5-12 % of the scrap value and was partly paid,
  partly absorbed through lower purchase prices upstream, partly deferred (stockpiles). Threshold
  0.10-0.25.

### 4.9 Containers and manufactured goods

- 2018 [C]: Rhine container traffic -10 % in TEU (-13 % net weight), Middle and Upper Rhine
  services "severely curtailed in late autumn"; Contargo suspended its regular services to the
  southern Rhine and Rhine-Main (2018); H1 2019 Rhine container traffic -16 % vs H1 2018, "loss of
  market share for inland waterway transport ... shippers may become more reluctant to choose inland
  waterways" (CCNR "Act now!", p. 30; annual report 2019, p. 11). Swiss Rhine ports: modal shift
  rail-to-barge after the Rastatt rail closure in H1 2018, then barge-to-rail in H2 2018.
- 2026 [R]/[C]: Maersk and Contargo surcharge ladders (section 1.2); Contargo services to the
  Upper Rhine and Rhine-Main suspended (6 Aug); Kombiverkehr Cologne-Basel 3 -> 5 round trips per
  week from 7 Sep; DB Cargo about 400 wagons mobilised, "one freight train replaces up to ten
  barges" at low-water loads, about 100 barges replaceable in total; RailFreight (28 Jul): switch to
  rail "a limited option" because of major German rail works (right-bank Rhine line closed until
  12 Dec 2026, freightperspectives 17 Aug); Bedoya-Maya et al. 2024: -0.2 % of monthly Rhine
  container throughput per disruption day, -5.9 % when the disruption exceeds 24 days, vulnerability
  doubled since 2018.
- Reading: a surcharge of EUR 1,335 per 20' is 2.5-4 % of a EUR 35-50 k box; rail costs less;
  containers reroute and, in part, do not come back. No price give-up. Threshold non-binding
  (0.3 or higher).

### 4.10 Cross-cutting 2026 survey evidence (from `update_20260903_supply_chain_damage.md`)

DIHK/IHK, 170 Rhine-corridor firms, 29 Jul-4 Aug 2026 (Kaub 20-30 cm) [C]: 78 % higher costs,
72 % reorganised logistics, more than half with logistics costs up at least 25 %, about a third
at least 50 %, about a third restricting production, 6 % stopped, a third plan to ship less via
the Rhine, a quarter to raise inventories. SVS Upper Rhine survey (10 Aug) [C]: about 20 % of
firms with logistics costs up 50 % or more, about 14 % with reduced production. IHK Rheinhessen
(1 Sep) [R]: transport cost increases of 50 % or more "no exception", peaks at doubled rates.
Reading: for a firm whose transport bill is 5-10 % of its input value, +25 to +50 % on logistics
is +1 to +5 % on delivered input prices, well below any give-up threshold; the production
restrictions are physical shortfalls (barge loads, rail ceiling), which the model represents
through the closure weeks and the substitution ceiling, not through the give-up rule.

---

## 5. Econometric and modelling estimates of the freight-cost sensitivity of shipments

| Study | What it measures | Result | Use for the thresholds |
|---|---|---|---|
| Jourquin, B. (2019), Estimating elasticities for freight transport using a network model: an applied methodological framework, J. Transportation Technologies 9, 1-13, DOI 10.4236/jtts.2019.91001 [C] | Own generalised-cost (GC) elasticities of mode demand, conditional logit with Box-Cox on a European network (ETISplus O-D by NSTR group) | IWW -0.39 (Europe), -0.33 (Benelux+); rail -0.48/-0.37; road -0.42/-0.42; travel time about half of the GC elasticity; commodity-specific values in Table 3 (not legible in the HTML, section 8) | Aggregate arc elasticity about -0.35: a x2.5 GC gives 2.5^-0.35 = 0.73, i.e. -27 % [E], the order of the Q3-Q4 2018 declines; consistent with a population of shippers whose thresholds straddle the 2018 surcharges |
| Jourquin, B., Beuthe, M. (2019), Cost, transit time and speed elasticity calculations for the European continental freight transport, Transport Policy 83, 1-12, DOI 10.1016/j.tranpol.2019.08.009; open copy hdl.handle.net/2078.1/219132 [C, abstract only] | Own and cross elasticities of road, IWW and rail w.r.t. total cost, transit time and speed, by commodity group, Europe and Benelux | tables not retrieved (section 8) | commodity-level IWW cost elasticities, if retrieved, would refine the ordering of section 7 |
| Jourquin, B. (2025), Direct and cross cost elasticity estimations for freight transport in Europe using constructed dependent variables, Research in Transportation Economics 111, 101566, DOI 10.1016/j.retrec.2025.101566 (CC BY) [C, metadata only] | Same family, newer data | not retrieved | idem |
| Beuthe, M., Jourquin, B., Geerts, J.-F., Koul a Ndjang'Ha, C. (2001), Freight transportation demand elasticities: a geographic multimodal transportation network analysis, Transportation Research E 37(4), 253-266 [C, abstract only] | Direct and cross elasticities for rail, road, IWW, 10 commodity groups, Belgian network, cost-minimisation model | values not retrieved; reviewed in Beuthe et al. (2014), Transport Reviews 34(5), 626-644 (Rhine-area model, 11 commodity groups and distance classes) | idem |
| Jonkeren, O., Rietveld, P., van Ommeren, J. (2007), Climate change and inland waterway transport: welfare effects of low water levels on the river Rhine, JTEP 41(3), 387-411 [C, abstract] | Trip-level data Jan 2003-Jul 2005: effect of Kaub water level on price per tonne, load factor, price per trip | "considerable effect of water levels on freight price per ton and load factor", price per trip about unchanged; price per tonne up to +100 % at the lowest 2003 levels; welfare loss EUR 28 m/yr on average, EUR 91 m in 2003 = 13 % of the turnover of the Rhine segment studied (Jonkeren et al. 2014: NW Europe 2003 loss EUR 480 m) | The pass-through mechanism (price per trip constant, price per tonne = trip price / load) is the model's surcharge; the welfare loss as a share of turnover bounds the deadweight loss but does not identify cancellations |
| Jonkeren, Jourquin, Rietveld (2011), Modal-split effects of climate change, TR-A 45(10), 1007-1019 [C, abstract] | NODUS network model, Rhine area | IWT loses about 5.4 % of current tonnage under the most extreme climate scenario; modal-split effect "limited" | Long-run modal response is small: shippers do not switch mode for the average year, they wait |
| Ademmer, Jannsen, Meuchelboeck (2023), German Economic Review 24(2), 121-144 (Kiel WP 2155) [C] | Monthly 1991-2019, low-water days at Kaub vs German IWW tonnage and industrial production | -0.87 % of IWW tonnage per low-water day (same month), -0.41 % next month; 30 days about -25 %; IP -0.034 %/day; 2SLS: 1 % IWW drop = -0.036 % IP; rail +0.07 %/day, road +0.08 % (n.s.): "impairments ... cannot be compensated by a noticeable shift to road and rail in the short run" | Aggregate volume response per day of disruption; rail/road substitution measured at 5-10 % of the lost tonnage: supports the small substitution share and a large deferred/lost share in the model |
| Bedoya-Maya, Shobayo, Beckers, van Hassel (2024), TR-D 131, 104190 [C, secondary] | Monthly Rhine container throughput 2000-2022 | -0.2 %/disruption day; -5.9 % if longer than 24 days; vulnerability doubled since 2018 | Containers: small loss, mostly modal shift |
| Vinke, van Koningsveld, van Dorsser, Baart, van Gelder, Vellinga (2022), Cascading effects of sustained low water on inland shipping, Climate Risk Management 35, 100400 (CC BY) [C, abstract only] | Simulation of bulk (iron ore, coal) Rotterdam-Duisburg in the 2018 event: fleet composition, trips, seaport congestion, storage at destination | impact "varies between vessel types due to cascading effects on fleet composition, number of trips, congestion in seaports and storage capacity at the destination"; larger modern vessels make the system more vulnerable | Physical channel for ore/coal; full text not retrieved (403 on every host) |
| CCNR annual report 2019 [C] | Freight rate indices by segment | dry x2.5, liquid x4.5 in Oct-Nov 2018; differentiation by cargo (sand/gravel/agribulk lower) | Direct evidence that demand for low-value bulk capped the surcharge |

Reading of the elasticities for a threshold model. An aggregate elasticity of about -0.35 with
respect to generalised cost is what a population of shippers with heterogeneous give-up thresholds
produces: at x2.5 about a quarter to a third of the tonnage drops out, at x4.5 about 40 %
(4.5^-0.35 = 0.59 [E]), close to the German November 2018 figure (-34/-36 %, which also contains
the loading limit). A single deterministic threshold per cargo class in the model is a coarse
version of this; the recommended values in section 7 are set so that the classes for which the
2018 surcharge exceeded the threshold (low-value bulk, part of agribulk) are the ones the CCNR
identifies as price-rationed, while the classes that paid x7-10 stay above it.

---

## 6. Capacity ceilings that limit the reroute branch (why "paid any price" still lost volume)

- Rail: DB Cargo mobilised about 400 wagons (up to 500 more later), one train replaces up to ten
  low-water barges, about 100 barges replaceable in total (14 Aug 2026) [C]; the right-bank Rhine
  rail line was closed for reconstruction until 12 Dec 2026 [R]; the three ARA block-train
  terminals for naphtha/LPG were at capacity [R]; rail into Switzerland limited by the north-south
  corridor works until 2030 [R]; in 2018 Ademmer et al. measure rail at +0.07 % per low-water day.
- Road: about 100,000 missing truck drivers, tank and tipper trailers scarce (BGL, DIHK); 40-80
  trucks per barge (agri), 100-150 per 2,500-3,000 t barge; Sunday and holiday driving bans lifted
  in most states through 31 Aug (RLP and Saarland to 30 Sep) [R].
- Storage: RWZ 80 kt at Worms; farms; ARA product and naphtha tanks (2018: distillate stocks
  +5 million bbl; 2026: naphtha +260 kt); company reserves 1-2 months of ore/coal at thyssenkrupp;
  Swiss compulsory stocks 4.5 months of fuel, 2-4 months of food.

Model reading: the reroute branch should be bounded by these ceilings (the `substitution_share`
mechanism, or the cost-based switching costs adopted on 4 Sep), and the residual should be treated
as deferred demand met from inventories where they exist, and as lost otherwise.

---

## 7. Recommended give-up thresholds (fraction of delivered value)

Definition: the flow is abandoned when `s (m - 1)` on the chosen route (surcharged barge or the
rail/road alternative, whichever is cheaper) exceeds the value below. Central value, plausible
range for sensitivity runs, confidence grade (A = several independent primary sources with
numbers; B = consistent primary and press evidence but partly indirect; C = indirect or single-
source), and the evidence.

| Cargo class / product group | Threshold | Range | Grade | Evidence (sections) |
|---|---|---|---|---|
| Dry bulk, low value: sand, gravel, crushed stone, clay, salt, cement clinker, recycled aggregates (B08, part of C23) | 0.20 | 0.10-0.30 | B/C | rates for these goods rose less than for coal/ore/containers in Oct-Nov 2018 (demand-capped); "large volumes lost, at least temporarily"; 2019 rebound +16 %; 2026 construction scarcity and delays rather than trucking at 2-3 x; local flows continue (Mannheim +47 %) (4.1, 2.1) |
| Thermal coal to power plants (B05 to D) | 0.20 | 0.10-0.30 | B | 2018: four Rhine coal plants throttled, RWE Hamm short; 2022: coal +10.6 % (paid at x2 when in the money); 2026: stocks and rail (Captrain, GKM, RDK), EnBW cost hit, Uniper unaffected (4.2) |
| Iron ore, coking coal, coke to steelworks (B07, B05 to C24A) | 0.35 | 0.25-0.50 | B | thyssenkrupp paid for 60 chartered vessels and 3,000 t/day rail in 2018 and doubled rail in 2026; residual loss capacity-limited; rail at +10-30 % of ore value was paid (4.3) |
| Grain, oilseeds (A01 bulk part) | 0.20 | 0.15-0.30 | B | 2026: x4 freight (+30-45 % of value) not paid on the barge; trucked at +10-15 %, stored, deferred; "increasingly unprofitable"; 2018 cereals -16.5 % (confounded) (4.4) |
| Feed and oil meals (C10T12 feed part) | 0.25 | 0.15-0.35 | B/C | supplementary trucking from mills; Swiss protein-feed shortfall and stock release 1 Sep 2026 (4.5) |
| Fertiliser (C20 fertiliser part) | 0.25 | 0.15-0.35 | C | 2018 volumes flat (+0.1 %); 2026 prices up, no disruption; seasonal deferral possible; Swiss N-stock release Dec 2018 (4.5) |
| Crude oil (B06) | 0.50 | n/a | C | Rhine refineries pipeline-fed; no barge give-up evidence; keep high so that any modelled crude barge flow behaves like products (3.2) |
| Refined petroleum products (C19) | 0.50 | 0.45-0.80 | A | paid x7 (2018) and x9-10 (2026) = +35-45 % of value; remaining gap covered from strategic/company stocks and rail/pipeline; retail pass-through +20 ct/l (2018), +12-16 Rp/l (2026) (4.6) |
| Naphtha, basic chemicals, intermediates (C20 bulk part, C22 primary forms) | 0.50 | 0.40-0.80 | A | BASF, Covestro, Lanxess, Evonik, Shell pay rail/road at 2-7 x; losses physical (barge loads, rail terminals at capacity); output cancellations are propagation, not price (4.7) |
| Steel, slabs, coils, non-ferrous (C24A, C24B) | 0.35 | 0.25-0.50 | B | s of 1-3 %, never price-binding; 2018 metals -22 % from the fleet stoppage and force majeure (4.3) |
| Scrap, secondary raw materials (GT14; C24A input) | 0.15 | 0.10-0.25 | C | merchants throttled purchases, stockpiles, mills cut scrap prices EUR 5-25/t (4.8) |
| Wood, paper, non-metallic mineral products, other mid-value bulk (C16, C17_18, C23 products) | 0.25 | 0.15-0.35 | C | no direct statements; 2018 losses -5 to -8 %; placed between gravel and grain by value density [E] |
| Containers, manufactured goods, food products in boxes (C10T12 packaged, C13-C15, C25-C33) | 0.30 (non-binding) | 0.20-0.50 | A | surcharge 2-4 % of box value; reroute to rail at less than 1 %; Rhine TEU -10 % (2018), -16 % H1 2019 by modal shift; keep the reroute branch open for this class (4.9) |

Suggested mapping to the EU-scope ICIO sectors and the model's cargo classes (`dry_bulk`,
`liquid_bulk`, `containers`): B08, C23 (clinker/cement), GT14-type flows -> 0.15-0.20; B05 -> 0.20
(to power) / 0.35 (to C24A, if the destination sector is known; otherwise 0.25); B07 -> 0.35;
A01, A02 -> 0.20; C10T12 -> 0.25 (bulk feed) / 0.30 (packaged); C20 -> 0.50 (bulk chemicals)
with fertiliser at 0.25 if split; C19, B06 -> 0.50; C24A -> 0.35; C24B -> 0.35; C16, C17_18 ->
0.25; all container/manufacturing sectors -> 0.30. Where a sector mixes cargoes (A01, C20,
C10T12), the barge-borne part is the low-value part, so the lower value should be used for the
`dry_bulk`/`liquid_bulk` cargo class of that sector and the higher one for its container share.

How to use: (i) the thresholds only bite in the surcharge weeks (Kaub below about 80 cm but the
fleet sailing: July and late Aug-Sep 2026; Aug-Dec 2018); in the closure weeks the give-up is
physical and independent of the threshold; (ii) the reroute branch must remain price-based at
3-7 x the barge rate with the capacity ceilings of section 6, otherwise grain and containers would
be rerouted at unlimited scale in the model although rail carried about 10 % of the lost barge
tonnage in reality; (iii) sensitivity: halve and double all thresholds, and run the "value
density" variant in which the barge-borne unit values of A01, C20, C10T12 are replaced by the
commodity prices of 3.1 instead of the BACI sector means.

---

## 8. Gaps and unverified items

1. Traditional-Rhine 2018 changes for coal, iron ore, agribulk and metals are shown only as a
   chart in the CCNR annual report 2019 (p. 31); the Q3-2018 German figures (CCNR April 2019) are
   the closest numbers found. No Q4-2018 breakdown by segment was retrieved. The Destatis monthly
   series by goods division (GENESIS-Online, statistic 46321, Binnenschifffahrt, monthly by
   Gueterabteilung) exists but was not downloaded (the Fachserie 8 Reihe 4 PDFs returned HTML).
2. Normal-water dry-bulk rates Rotterdam-Duisburg and container base rates are estimates [E];
   Insights Global/PJK and Panteia publish them behind subscription.
3. Commodity-level IWW cost elasticities (Beuthe et al. 2001; Beuthe et al. 2014; Jourquin and
   Beuthe 2019 Table; Jourquin 2025) were not retrieved: the UCLouvain, ResearchGate and
   ScienceDirect copies returned 403/404, and the SCIRP HTML renders Table 3 as an image.
4. Vinke et al. 2022 full text (TU Delft, ScienceDirect) returned 403; only the abstract is used.
5. "Some firms stored their grain in Rotterdam rather than shipping it" (2018) is from a secondary
   site (ourrhine.eu) and was not traced to a primary report; the "Port of Switzerland: only goods
   necessary for Swiss imports/exports are shipped, non-essential goods are stored at seaports"
   sentence appeared only in a search-engine summary and could not be found in the fetched SRF,
   Blick, 20min or Badische Zeitung articles: treat both as unverified.
6. The EIA Duisburg rate (USD 1 to more than 4/bbl, 2018), the Handelsblatt 2022 rates (EUR 20 to
   110/t), the RheinCargo/HKM coal trains (2026), the Bloomberg "400 % in two months" chart, and the
   2018 and 2026 price levels of urea, gasoil, naphtha and HRC are from search summaries or single
   quotes; the 2018 values of naphtha, gasoil, urea, HRC and scrap are my approximations [E].
7. No quantified statement of cancelled gravel/sand deliveries in 2026 was found (WiWo, HDB, VBU
   give qualitative language only); the Hafen Mannheim July figures are the only 2026 port
   statistics by goods group found so far; Destatis July 2026 data are due mid/late September.
8. The coal-plant restrictions of 2018 (Bergkamen, Walsum, GKM, RDK) are attributed jointly to
   supply bottlenecks and water temperature by BfG/ICPR; the share due to coal supply is not
   separated.
9. Swiss mineral-oil import share via the Rhine is given as 22 % (Avenergy, mid-July 2026), "one
   fifth" (swissinfo, late August) and 30 % (Bloomberg opinion, 29 July): the Avenergy figure is
   used.

---

## Sources

Official statistics and agency reports
1. Eurostat, dataset `iww_go_atygo` (Inland waterways transport by type of goods, NST 2007),
   SDMX-CSV download 4 Sep 2026, last update 28 Jul 2026 - https://ec.europa.eu/eurostat/databrowser/product/page/iww_go_atygo
2. Destatis, press release 112/2019, 25 Mar 2019, "Niedrigwasser beschert Binnenschifffahrt Rekordminus" - https://www.destatis.de/DE/Presse/Pressemitteilungen/2019/03/PD19_112_463.html
3. BDB (Bundesverband der Deutschen Binnenschifffahrt), "Kennzahlen zum Niedrigwasserjahr 2018", 26 Nov 2019 (Schifffahrtsverein Rhein-Main-Donau) - https://www.schifffahrtsverein.de/2019/11/26/bdb-stellt-kennzahlen-zum-niedrigwasserjahr-2018-vor/
4. Verkehrsrundschau, "Binnenschifffahrt: Niedrigwasser beeinträchtigt den Gütertransport" (Destatis monthly figures 2018) - https://www.verkehrsrundschau.de/nachrichten/transport-logistik/binnenschifffahrt-niedrigwasser-beeintraechtigt-den-guetertransport-3221934
5. CCNR, Market Observation annual report 2019 (on 2018), Sep 2019 - https://www.ccr-zkr.org/files/documents/om/om19_II_en.pdf
6. CCNR, Market Insight April 2019 - https://www.ccr-zkr.org/files/documents/om/om19_I_en.pdf
7. CCNR, Market Insight November 2019 - https://www.ccr-zkr.org/files/documents/om/om19_III_en.pdf
8. CCNR, Market Observation annual report 2023 (on 2022) - https://inland-navigation-market.org/wp-content/uploads/2025/01/CCNR_annual_report_EN_2023_WEB_rev.pdf
9. CCNR, Market Insight April 2026 - https://inland-navigation-market.org (chapter "Freight rates in the Rhine region")
10. CCNR, Reflection paper "Act now!" on low water and effects on Rhine navigation, version 3.0 - https://www.ccr-zkr.org/files/documents/infovoienavigable/Act_now_3_0_en.pdf
11. CCNR web chapter "4. Water levels and freight rates" - https://inland-navigation-market.org/chapitre/4-water-levels-and-freight-rates-2/?lang=en
12. ICPR/IKSR, Bericht Nr. 263, Bericht zum Niedrigwasserereignis Juli-November 2018 - https://www.iksr.org/fileadmin/user_upload/DKDM/Dokumente/Fachberichte/DE/rp_De_0263.pdf
13. BfG, "Das Niedrigwasser 2018", 2019 - https://doi.bafg.de/BfG/2019/Niedrigwasser_2018.pdf
14. BfG UNDINE, "Das Niedrigwasser des Rheins im Sommer und Herbst 2018" - https://undine.bafg.de/rhein/extremereignisse/rhein_nw2018.html
15. EIA, Today in Energy, 8 Nov 2018, "Low Rhine River water levels disrupt petroleum product shipments to parts of Europe" - https://www.eia.gov/todayinenergy/detail.php?id=37414
16. Hafen Mannheim, Umschlag Juli 2026 (via Binnenschifffahrt Online, Aug 2026) - https://binnenschifffahrt-online.de/2026/08/featured/39932/niedrigwasser-belastet-wasserseitigen-gueterumschlag-in-mannheim/ ; https://www.hafen-mannheim.de/umschlag-juli-2026/
17. Bundesamt fuer wirtschaftliche Landesversorgung (BWL), "Versorgungslage", status 4 Sep 2026 - https://www.bwl.admin.ch/de/versorgungslage
18. DB Cargo, 14 Aug 2026, additional capacities - https://www.dbcargo.com/rail-de-de/logistik-news/niedrigwasser-db-cargo-zusaetzliche-kapazitaeten-13998510
19. Kombiverkehr, press release Sep 2026, additional rail capacity - https://media.kombiverkehr.de/de/service/pressemitteilungen/2026/niedrigwasser-im-rhein-kombiverkehr-schafft-kurzfristig-zusaetzliche-kapazitaeten-auf-der-schiene
20. Schifffahrts- und Hafenverband Schweiz (SVS), 10 Aug 2026 - https://svs-ch.ch/rhein-staerken-versorgung-sichern/

Carriers' tariffs
21. Maersk, "Rhine River - Low Water Surcharge", 9 Jul 2026 (effective 15 Jul 2026) - https://www.maersk.com/news/articles/2026/07/09/rhine-river-low-water-surcharge
22. Contargo, Low Water Surcharge information - https://www.contargo.net/en/business/auxiliary-conditions/low-water

Company statements and trade press, 2018
23. BASF, news release 26 Feb 2019 (2018 results; EUR 250 m low-water effect) - https://www.basf.com/global/en/media/news-releases/2019/02/p-19-141
24. gCaptain/Reuters, 27 Feb 2019, "Thyssenkrupp improves logistics after Rhine low water crisis" - https://gcaptain.com/thyssenkrupp-rhine-river-level-plans/
25. S&P Global Platts, 19 Oct 2018, thyssenkrupp force majeure - https://www.spglobal.com/platts/en/market-insights/latest-news/metals/101918-thyssenkrupp-steel-europe-declares-force-majeure-on-steel-product-shipments-due-to-low-rhine-level
26. AFP/phys.org, 26 Oct 2018, "Drought-hit Rhine forces Germany to tap oil reserves" - https://phys.org/news/2018-10-drought-hit-rhine-germany-oil-reserves.html
27. Bonapart, Jan 2019, "Bilanz 2018: Weniger Umschlag im Hafen Duisburg" - https://www.bonapart.de/nachrichten/beitrag/bilanz-2018-weniger-umschlag-im-hafen-duisburg.html
28. FreightWaves, Jan 2019, Port of Rotterdam 2018 throughput by commodity - https://www.freightwaves.com/news/rotterdam-reports-record-breaking-2018-throughput
29. Zukunft Mobilitaet, 1 Nov 2018, Niedrigwasser und Binnenschifffahrt - https://www.zukunft-mobilitaet.net/181101/logistik-gueterverkehr/niedrigwasser-rhein-binnenschifffahrt-risiko-massnahmen/
30. bz Basel, Swiss compulsory stocks 2018/2022 - https://www.bzbasel.ch/news-service/inland-schweiz/niedrigwasser-tiefe-pegel-des-rheins-beeintraechtigen-die-versorgung-der-schweiz-mit-mineraloel-ld.2320511
31. ka-news, RDK Karlsruhe coal by rail - https://www.ka-news.de/region/karlsruhe/rheinhafen-dampfkraftwerk-bald-kommt-die-kohle-haeufiger-mit-der-bahn-art-863787
32. ZFK/Reuters, 4 Aug 2022, Staudinger coal supply - https://www.zfk.de/energie/strom/niedrigwasser-bedroht-kohlenachschub-fuer-kraftwerk-staudinger
33. Handelsblatt/WiWo, 18 Aug 2022, Rotterdam-Karlsruhe EUR 20 to 110/t [S] - https://www.handelsblatt.com/unternehmen/handel-konsumgueter/logistik-transportkosten-auf-dem-rhein-steigen-stark-wegen-niedrigwasser/28588958.html

Trade press and company statements, 2026
34. Reuters via Insurance Journal, 13 Jul 2026 (EUR 45 to 60-70/t) - https://www.insurancejournal.com/news/international/2026/07/13/877317.htm
35. Freight Perspectives, 15 Jul 2026 and 17 Aug 2026 - https://www.freightperspectives.com/p/rhine-water-levels-2026-kaub-forecast ; https://www.freightperspectives.com/p/rhine-water-levels-kaub-road-freight
36. Argus, 23 Jul 2026, "Low Rhine water tightens German fuel supply" - https://www.argusmedia.com/en/news-and-insights/latest-market-news/2857349-low-rhine-water-tightens-german-fuel-supply
37. Argus, late Jul 2026, "Rhine oil barge rates at record on near-impassable Kaub" - https://www.argusmedia.com/en/news-and-insights/latest-market-news/2858829-rhine-oil-barge-rates-at-record-on-near-impassable-kaub
38. S&P Global, 23 Jul 2026, naphtha supply - https://www.spglobal.com/energy/en/news-research/latest-news/chemicals/072326-low-rhine-water-levels-hit-naphtha-supply-disrupting-germanys-petrochemical-output
39. enterpriseam, 3 Aug 2026 (Bloomberg opinion 29 Jul), EUR 150 vs 20 - https://enterpriseam.com/logistics/2026/08/03/low-water-on-the-rhine-drives-up-freight-costs-and-cuts-inland-cargo-capacity/
40. France24/AFP, 6 Aug 2026 - https://www.france24.com/en/live-news/20260806-low-water-on-germany-s-rhine-river-threatens-new-blow-to-economy
41. Bloomberg via Insurance Journal, 12 Aug 2026 - https://www.insurancejournal.com/news/international/2026/08/12/881099.htm
42. Bloomberg via Yahoo Finance, Aug 2026, "Europe dodges a Rhine crisis for the worst possible reason" - https://finance.yahoo.com/energy/articles/europe-dodges-rhine-crisis-worst-230000625.html
43. Kpler, 21 Aug 2026, Rhine water levels and cracker operations - https://www.kpler.com/blog/rhine-river-water-levels-remain-critical-for-european-cracker-operations
44. Chemistry World, Aug 2026 - https://www.chemistryworld.com/news/record-low-european-river-levels-threaten-chemical-freight-and-process-cooling/4024021.article
45. EUROMETAL, 16 Jul 2026, thyssenkrupp reduces production - https://eurometal.net/german-steelmaker-thyssenkrupp-reduces-production-when-low-rhine-water-levels-disrupt-materials-supplies/
46. EUROMETAL, Aug 2026, German steel industry presses for infrastructure action - https://eurometal.net/german-steel-industry-presses-for-infrastructure-action-as-rhine-disruption-persists/
47. miningmetalnews, 12 Aug 2026 - https://www.miningmetalnews.com/20260812/3499/low-river-water-threatens-steel-supplies-european-mills
48. dpa/onvista, 13 Aug 2026, thyssenkrupp keeps production running - https://www.onvista.de/news/2026/08-13-roundup-trotz-niedrigwassers-thyssenkrupp-haelt-produktion-am-laufen-0-10-26542814
49. dpa/onvista, 11 Aug 2026, Uniper not affected - https://www.onvista.de/news/2026/08-11-uniper-sind-vom-niedrigwasser-nicht-betroffen-0-20-26541811
50. Stuttgarter Nachrichten, 7 Aug 2026, energy supply - https://www.stuttgarter-nachrichten.de/inhalt.wassermangel-im-rhein-niedrigwasser-gefaehrdet-energieversorgung.5f922da6-c995-4a98-837a-8e3d926b51b1.html
51. Verkehrsrundschau, Aug 2026, Captrain coal by rail - https://www.verkehrsrundschau.de/nachrichten/transport-logistik/rhein-niedrigwasser-captrain-verlagert-mehr-kohle-auf-die-schiene-3892029
52. Verkehrsrundschau, 11 Aug 2026, fuel prices - https://www.verkehrsrundschau.de/nachrichten/vermischtes/niedrigwasser-am-rhein-verteuert-kraftstoffe-3889269
53. Recyclingportal, 12 Aug 2026, recycling industry warning - https://recyclingportal.eu/archive/97080
54. EU-Recycling, Schrottmarktbericht August 2026 - https://eu-recycling.com/Archive/51213
55. agrarheute, 6 Aug 2026, freight costs for agricultural products - https://www.agrarheute.com/management/historisch-niedrige-pegelstaende-frachtkosten-fuer-agrarprodukte-explodieren-642149
56. top agrar, 10 Aug 2026, "Niedrigwasser wird zum Marktfaktor" - https://www.topagrar.com/markt/news/niedrigwasser-wird-zum-marktfaktor-20028111.html
57. top agrar, 11 Aug 2026, prices for grain, feed, fertiliser, diesel - https://www.topagrar.com/betriebsleitung/news/niedrigwasser-verteuert-agrartransporte-das-sind-die-folgen-fur-landwirte-20028247.html
58. top agrar / DRV, 14 Aug 2026 - https://www.topagrar.com/betriebsleitung/news/raiffeisenverband-warnt-vor-engpassen-bei-logistik-und-dunger-20028214.html ; https://www.agrarwelt.com/niedrige-wasserstaende-gefaehrden-getreidetransport-und-duengerbestellungen/
59. wirtschaft-und-industrie.de, 31 Aug 2026, RWZ and IHK Rheinhessen - https://www.wirtschaft-und-industrie.de/rhein-niedrigwasser-treibt-transportkosten-bremst-agrarlogistik/
60. Lebensmittelpraxis, Aug 2026, food industry freight costs - https://lebensmittelpraxis.de/zentrale-management/49711-niedrigwasser-am-rhein-70-prozent-hoehere-frachtkosten-warum-die-lebensmittelwirtschaft-kaum-ausweichen-kann.html
61. WirtschaftsWoche, 17 Aug 2026, construction - https://www.wiwo.de/unternehmen/industrie/niedrige-pegelstaende-hoehere-preise-und-engpaesse-niedrigwasser-trifft-bauherren/100247649.html ; it-boltwise summary - https://www.it-boltwise.de/rhein-niedrigwasser-bremst-bau-engpaesse-bei-sand-kies-und-baustoffen.html
62. ZDF heute, Aug 2026, rail and truck substitution - https://www.zdfheute.de/wirtschaft/rhein-niedrigwasser-binnenschifffahrt-bahn-lkw-ersatz-100.html
63. RailFreight, 28 Jul 2026 - https://www.railfreight.com/intermodal/2026/07/28/low-water-levels-on-rhine-hit-barge-services-switch-to-rail-a-limited-option/
64. Sxcoal, Jul 2026 - https://en.sxcoal.com/news/detail/2076832219053686785
65. railmarket, 2026, RheinCargo coal trains for HKM [S] - https://railmarket.com/news/freight-rail/61405-rheincargo-adds-rotterdam-duisburg-coal-trains-for-hkm-due-to-low-levels-of-water-in-rhine
66. OPIS, 10 Jul 2025, Rhine barge rates - https://www.opis.com/resources/energy-market-news-from-opis/falling-river-rhine-levels-in-europe-impact-plant-terminal-operations/
67. Insights Global, Rhine freight market commentaries (weekly, no rates in the free text) - https://www.insights-global.com/category/blogs/freight-rates/

Switzerland 2026
68. moneycab/SDA, 16 Jul 2026, "Tiefer Rhein-Pegel: hoehere Treibstoffpreise, aber kein Mangel" - https://www.moneycab.com/schweiz/tiefer-rhein-pegel-hoehere-treibstoffpreise-aber-kein-mangel/
69. swissinfo/SDA, 27 Aug 2026, "Niedrigwasser am Rhein verteuert Benzin deutlich" - https://www.swissinfo.ch/ger/niedrigwasser-am-rhein-verteuert-benzin-deutlich/91890604
70. 20 Minuten, Aug 2026, Swiss firms switch to rail and truck - https://www.20min.ch/story/rhein-niedrigwasser-schweizer-firmen-steigen-auf-zug-und-lastwagen-um-103615555
71. Blick, 1 Sep 2026, feed compulsory stocks opened - https://www.blick.ch/politik/bund-bewilligt-massnahmen-wegen-trockenheit-schweiz-muss-tierfutter-notlager-anzapfen-id22216066.html
72. SRF, Jul 2026, Basel Rhine ports - https://www.srf.ch/news/wirtschaft/basler-rheinhaefen-jeder-tropfen-zaehlt-tiefer-wasserpegel-bremst-die-schifffahrt
73. Blick, Aug 2026, "Der Rhein ist bald zweigeteilt" - https://www.blick.ch/wirtschaft/pegel-sinkt-dramatisch-der-rhein-ist-bald-zweigeteilt-das-sind-die-folgen-id22171200.html

Prices
74. IndexMundi monthly prices: coal (South Africa) - https://www.indexmundi.com/commodities/?commodity=coal-south-african&months=120 ; iron ore - https://www.indexmundi.com/commodities/?commodity=iron-ore&months=120 ; wheat (US HRW) - https://www.indexmundi.com/commodities/?commodity=wheat&months=120
75. German gravel/sand price lists 2026 (KSW Kieswerke, Glueck-Kies, Kieswerk Herrmann; overview handwerk.cloud) - https://www.handwerk.cloud/wissen/allgemein/kies-schotter-kosten
76. Fastmarkets HRC N. Europe Aug 2026 via EUROMETAL [S] - https://eurometal.net/2026/08/24/
77. Urea Aug 2026 [S] - https://igrownews.com/fertilizer-prices-weekly-update/
78. Project unit values: `disrupt-sc-data/EU/Economic/sector_table.csv` (BACI 2023 EU mix)

Academic
79. Jourquin, B. (2019), J. Transportation Technologies 9, 1-13, DOI 10.4236/jtts.2019.91001 - https://file.scirp.org/Html/1-3500440_88340.htm
80. Jourquin, B., Beuthe, M. (2019), Transport Policy 83, 1-12, DOI 10.1016/j.tranpol.2019.08.009 - open copy http://hdl.handle.net/2078.1/219132
81. Jourquin, B. (2025), Research in Transportation Economics 111, 101566, DOI 10.1016/j.retrec.2025.101566 - https://www.sciencedirect.com/science/article/pii/S0739885925000496
82. Beuthe, M., Jourquin, B., Geerts, J.-F., Koul a Ndjang'Ha, C. (2001), Transportation Research E 37(4), 253-266 - https://www.sciencedirect.com/science/article/abs/pii/S1366554500000223 ; Beuthe et al. (2014), Transport Reviews 34(5), 626-644 - https://ideas.repec.org/a/taf/transr/v34y2014i5p626-644.html
83. Jonkeren, O., Rietveld, P., van Ommeren, J. (2007), JTEP 41(3), 387-411 - https://ideas.repec.org/a/tpe/jtecpo/v41y2007i3p387-411.html ; PDF https://research.vu.nl/files/2261098/climatechangeandinlandwaterway.pdf
84. Jonkeren, O., Jourquin, B., Rietveld, P. (2011), TR-A 45(10), 1007-1019 - https://www.sciencedirect.com/science/article/abs/pii/S0965856409000135
85. Ademmer, M., Jannsen, N., Meuchelboeck, S. (2023), German Economic Review 24(2), 121-144; Kiel WP 2155 - https://www.kielinstitut.de/fileadmin/Dateiverwaltung/IfW-Publications/fis-import/d0c53966-8307-4bff-9cf9-13544afe7d80-KWP_2155_low_water_econ_activity.pdf
86. Bedoya-Maya, F., Shobayo, P., Beckers, J., van Hassel, E. (2024), TR-D 131, 104190 - https://www.sciencedirect.com/science/article/pii/S1361920924001470
87. Vinke, F., van Koningsveld, M., van Dorsser, C., Baart, F., van Gelder, P., Vellinga, T. (2022), Climate Risk Management 35, 100400 - https://doi.org/10.1016/j.crm.2022.100400 ; https://research.tudelft.nl/en/publications/cascading-effects-of-sustained-low-water-on-inland-shipping/
88. "50-Years Inland Waterway Freight Data in the Rhine-Alpine Corridor", Scientific Data (2026), s41597-026-06875-3 (IWT volumes by NST 2007 goods type, DE/NL 1992/1970-2023; useful for by-goods validation) - https://www.nature.com/articles/s41597-026-06875-3
