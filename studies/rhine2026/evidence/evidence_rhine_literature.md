# Validation evidence base: Rhine low-water events and inland-waterway disruption

Compiled 2 September 2026 for the EU-wide DisruptSC paper (2026 Rhine low-water case study).
Scope: quantified empirical findings from the 2018, 2022 (and 2003/2011/2015) Rhine low-water
episodes plus the academic literature on inland-waterway (IWW) disruption, organised as
(a) annotated bibliography, (b) validation-target table, (c) open questions/gaps.

Conventions. "Kaub" = Kaub gauge (Middle Rhine, the binding bottleneck). "EWL/GlW" = equivalent
water level (Gleichwertiger Wasserstand), the reference low-water level undercut on average 20
days/yr: 78 cm at Kaub on the 2012 reference (used by all 2018/2022 statistics), 77 cm since
1 Jan 2023. Available fairway depth at Kaub = 1.90 m + gauge − 0.78 m (i.e. gauge + 1.12 m).
Numbers marked [derived] are my arithmetic; [secondary] means taken from a citing source, not the
original. Where a source could only be reached through a search-engine summary this is flagged
[search summary]. Primary texts (Kiel WP 2155, CCNR annual reports 2019 and 2023, CCNR Market
Insight Nov 2019, ICPR reports 248 and 263, Bundestag Drucksache 19/9524, van Dorsser et al. 2020,
Bundesbank Monthly Reports Nov/Dec 2018 and Sep 2022) were downloaded and text-extracted; their
extracted text sits in `scratchpad/pdftxt/`.

---

## (a) Annotated bibliography

### A. Macro-econometric impact studies

**A1. Ademmer, M., Jannsen, N., Meuchelböck (née Mösle), S. (2023). Extreme weather events and
economic activity: the case of low water levels on the Rhine river. German Economic Review 24(2),
121–144. DOI 10.1515/ger-2022-0077. Working-paper version: Kiel Working Paper 2155, April 2020.**
URL: https://www.degruyterbrill.com/document/doi/10.1515/ger-2022-0077/html ;
WP: https://www.kielinstitut.de/fileadmin/Dateiverwaltung/IfW-Publications/fis-import/d0c53966-8307-4bff-9cf9-13544afe7d80-KWP_2155_low_water_econ_activity.pdf
- Data: monthly, Jan 1991–Mar 2019 (337 obs.). Low-water variable = number of days per month
  with Kaub < 78 cm (BfG data); robustness with Duisburg-Ruhrort gauge. Outcomes: German IWW
  tonnage (Destatis, X-12 seasonally adjusted) and German industrial production; controls: global
  trade / global industrial production. Method: distributed-lag regressions in first differences
  (change in low-water days → growth rates), plus 2SLS using low-water days as an instrument for
  IWW volume.
- IWW volume: one extra low-water day → −0.87 % (same month, s.e. 0.093, 1 % level) and
  −0.41 % (next month). A month with 30 low-water days → about −25 % IWW tonnage.
- Industrial production (IP): one extra low-water day → −0.034 % (same month; s.e. 0.012) and
  −0.024 % (next month, 10 % level). 30 days → about −1 % IP, ceteris paribus (contemporaneous);
  about −1.7 % including the lag [derived: 30 × (0.034+0.024)].
- 2SLS elasticity: a 1 % drop in IWW volume → −0.036 % IP in the same month (s.e. 0.014) and
  about −0.03 % in the following month. Hence a 10 % IWW drop → about −0.4 % IP → about −0.1 %
  GDP (industry ≈ 25 % of GVA), even though IWW is < 0.2 % of German GVA.
- 2018 counterfactual: peak effect in November 2018, IP 1.5 % below the no-low-water
  counterfactual, "corresponding to a decline in GDP of close to 0.4 percent"; authors call this a
  lower bound (excludes IWW-sector value added and spillovers to services).
- Modal substitution (Appendix B): rail volume +0.07 % per low-water day (significant, 2005–2019
  sample), road +0.08 % (not significant). "Impairments in inland water shipping cannot be
  compensated by a noticeable shift to road and rail transportation in the short run."
- Structural facts used: Rhine ≈ 80 % of German IWW freight (BDB); IWW ≈ 6 % of German freight
  volume; ≈ 30 % of coal/crude oil/natural gas and ≈ 20 % of coke-oven and petroleum products
  moved by IWW; at 78 cm about four times as many ships are needed as at 250 cm (Contargo 2017).

**A2. Ademmer, M., Jannsen, N., Kooths, S., Mösle, S. (2019). Niedrigwasser bremst Produktion.
Wirtschaftsdienst 99(1), 79–80.** URL: https://www.wirtschaftsdienst.eu/inhalt/jahr/2019/heft/1/beitrag/niedrigwasser-bremst-produktion.html
- Earlier version of A1 with the 2018 event decomposition: one low-water day → −0.76 pp IWW
  volume growth, −0.04 pp IP growth; a full month → IWW growth −20 pp or more.
- Kaub days < 78 cm in 2018: Aug 30, Sep ≈ 15, Oct 30, Nov 30, Dec 3 (≈ 108; CCNR counts 107).
- Effect on German IP growth: −0.8 pp in Q3 2018, −0.4 pp in Q4 2018; IP level ≈ 1.7 % below
  counterfactual in November 2018 (peak).
- As reported by CCNR (2019, p. 67, citing this note): IP loss ≈ EUR 1.9 bn in Q3 2018 and
  EUR 2.9 bn in Q4 2018 (EUR 1.0 bn lagged effect + EUR 1.9 bn contemporaneous) → ≈ EUR 4.8 bn
  for H2 2018 [derived]. Modal split 2017: IWW "knapp 6 %", road ≈ 78 %, rail ≈ 9 %, sea ≈ 7 %.

**A3. Bedoya-Maya, F., Shobayo, P., Beckers, J., van Hassel, E. (2024). The impact of critical
water levels on container inland waterway transport. Transportation Research Part D 131, 104190.
DOI 10.1016/j.trd.2024.104190.** URL: https://www.sciencedirect.com/science/article/pii/S1361920924001470
- Monthly container throughput on the Rhine, 2000–2022, time-series econometrics on all episodes
  of low or high water. Average impact −0.2 % of monthly throughput per disruption day, and
  −5.9 % when the disruption lasts more than 24 days; vulnerability to critical water levels has
  doubled since 2018; strongest (and lagged) effects from localised low-water incidents.
  Projected potential loss 7–20 % of annual container throughput by 2050 without adaptation
  [search summary]. Reportedly also: Nijmegen gauge 136 days below reference low-water mark in
  2018 vs 37 days/yr average 2016–2023 [search summary; verify in paper].

**A4. Deutsche Bundesbank, Monthly Reports November 2018, December 2018, September 2022.**
URLs: https://www.bundesbank.de/resource/blob/767336/cf8bde887ae06b7800bd566db4874e23/472B63F073F071307366337C94F8C870/2018-11-monatsbericht-data.pdf ;
https://www.bundesbank.de/resource/blob/770494/3f0847f16b8cf2406f7d6522191c50d6/mL/2018-12-monatsbericht-data.pdf ;
https://www.bundesbank.de/resource/blob/897000/34dc1f4e894de531e3e4e7d071e5ccac/mL/2022-09-monatsbericht-data.pdf
- Full-text search of the English and German November 2018 and English December 2018 editions
  found NO box or estimate on Rhine low water; the only mention is a price remark (Dec 2018, p. 8:
  energy prices rose "because transport costs were higher due to low water levels in rivers").
  The English September 2022 report likewise contains no low-water passage. The widely reported
  "Bundesbank: −0.2 pp of Q3 2018 GDP" (e.g. CNBC 31 Jul 2019; Insurance Journal 20 Jul 2022) could
  not be traced to a primary Bundesbank text and may conflate Kiel Institute figures. The
  Bundesbank's August 2026 Monthly Report (per Handelsblatt/verkehrsrundschau, Aug 2026) states
  that low water "noticeably burdens" Q3 2026 activity, without a number. Treat as a GAP.

**A5. Kiel Institute statements and secondary macro estimates.**
- Kiel Institute news, 12 Aug 2022 (https://www.kielinstitut.de/de/publikationen/aktuelles/niedrigwasser-vor-allem-rohstoffe-und-gueter-am-anfang-der-produktionskette-verzoegert/):
  restates A1 (−1 % IP per 30 low-water days; peak −1.5 %; ≈ −0.4 % GDP); IWW 10–30 % of tonnage
  for coal/crude/gas, refinery products and chemicals; IWW ≈ 6 % of freight (2017), < 0.2 % of GVA;
  in 2022 IP was already ≈ 7 % below the level implied by orders because of supply bottlenecks.
- Kooths (Kiel), 28 Jul 2026 (Handelsblatt/onvista): 2026 low water could cut Q3 2026 GDP by
  0.1–0.2 %, ≈ EUR 1–2 bn of value added.
- Solveen (Commerzbank), Bloomberg 11 Aug 2026 (https://www.swissinfo.ch/eng/rhine-river-shipping-stalls-as-water-level-hits-record-low/91879987):
  −0.35 pp of Q3 2026 GDP if critically low water persists to mid-September.
- Fiedler (Berenberg), Bloomberg/Insurance Journal 20 Jul 2022 (https://www.insurancejournal.com/news/international/2022/07/20/676658.htm):
  IP about 1 % lower in months with Kaub < 78 cm; ≈ 1.5 % including delayed effects. Belz (BfG),
  same article: barge transport becomes uneconomic if Kaub drops a further 37+ cm from 77 cm
  (≈ 40 cm).
- Deutsche Bank Research, 23 Jun 2023 (Schattenberg; https://www.dbresearch.com/PROD/IE-PROD/PROD0000000000528728/Current_water_level_of_the_Rhine_brings_back_memor.xhtml):
  Kaub averaged 40 cm on 7–19 Aug 2022; recap of Destatis 2018/2022 figures.
- CNBC 31 Jul 2019 [search summary]: chemicals + pharmaceuticals = 8.3 % of German industrial
  output and ≈ 2 % of GVA; a 10 % fall of that sector for a full quarter ≈ −0.2 pp quarterly GDP.

### B. Transport-economics, welfare and climate-scenario studies

**B1. Jonkeren, O., Rietveld, P., van Ommeren, J. (2007). Climate change and inland waterway
transport: welfare effects of low water levels on the river Rhine. Journal of Transport Economics
and Policy 41(3), 387–411.** URL: https://www.liverpooluniversitypress.co.uk/doi/10.3828/jtep.2007.41.3.387
- > 3,000 vessel journeys in 2003 (700 usable). Water level strongly affects price per tonne and
  load factor, not price per trip. Freight price per tonne up to +100 % at the lowest water levels
  vs normal. Average annual welfare loss ≈ EUR 28 m (≈ 20-year water-level record); in 2003
  ≈ EUR 91 m, ≈ 13 % of turnover of the Rhine market segment considered.

**B2. Jonkeren, O., Jourquin, B., Rietveld, P. (2011). Modal-split effects of climate change: the
effect of low water levels on the competitive position of inland waterway transport in the river
Rhine area. Transportation Research Part A 45(10), 1007–1019.** URL: https://www.sciencedirect.com/science/article/abs/pii/S0965856409000135
- NODUS multimodal network model; modal-split effect limited: IWT loses ≈ 5.4 % of currently
  transported quantities under the most extreme climate scenario.

**B3. Jonkeren, O., Rietveld, P., van Ommeren, J., te Linde, A. (2014). Climate change and economic
consequences for inland waterway transport in Europe. Regional Environmental Change 14, 953–965.
DOI 10.1007/s10113-013-0441-7.** URL: https://link.springer.com/article/10.1007/s10113-013-0441-7
- At extremely low water the price per tonne in the Rhine area almost doubles; welfare loss for
  North-West Europe in the dry summer of 2003 ≈ EUR 480 m.

**B4. Beuthe, M., Jourquin, B., Urbain, N., Lingemann, I., Ubbels, B. (2014). Climate change impacts
on transport on the Rhine and Danube: a multimodal approach. Transportation Research Part D 27,
6–11. DOI 10.1016/j.trd.2013.11.002.** URL: https://www.sciencedirect.com/science/article/abs/pii/S1361920913001442
- NODUS network analysis 2005–2050 of water-depth scenarios on transport costs and modal split
  (IWW, rail, road); impact of climate change to 2050 "should be limited"; climate-driven
  water-level change not strong enough to alter modal shares (ECCONET project). No headline
  percentages retrievable (paywalled).

**B5. Christodoulou, A., Christidis, P., Bisselink, B. (2020). Forecasting the impacts of climate
change on inland waterways. Transportation Research Part D 82, 102159. DOI 10.1016/j.trd.2019.10.012.**
URL: https://www.sciencedirect.com/science/article/pii/S136192091930149X (open access)
- JRC (PESETA-linked LISFLOOD hydrology), 11 climate-model runs, four locations on Rhine and
  Danube. For most cases/scenarios a DECREASE in low-water days is projected; average economic
  benefit from fewer low-water days ≈ EUR 8 m/yr by end of century. Note: PESETA IV has no
  inland-waterway task; the PESETA III transport report is Demirel, H., Christodoulou, A. (2018),
  Impacts of climate change on transport: a focus on airports, seaports and inland waterways,
  JRC108865, EUR 28896 EN (https://publications.jrc.ec.europa.eu/repository/bitstream/JRC108865/jrc108865_final.pdf).

**B6. Scholten, A., Rothstein, B., Baumhauer, R. (2014). Mass-cargo-affine industries and climate
change: the vulnerability of bulk cargo companies along the River Rhine to low water periods.
Climatic Change 122, 111–125. DOI 10.1007/s10584-013-0968-0.** URL: https://link.springer.com/article/10.1007/s10584-013-0968-0
- Company-level storage model applied to three (anonymous) iron & steel companies on the Rhine:
  +1 to +5 additional days/yr of empty storage in 2021–2050 and up to +9 days in 2071–2100
  depending on scenario; required storage capacity +2.5 % (2021–2050) and +25 % (2071–2100).
  Directly comparable to DisruptSC inventory-depletion dynamics.

**B7. Scholten, A., Rothstein, B. (2016). Navigation on the Danube: limitations by low water levels
and their impacts. JRC Technical Report EUR 28374 EN (JRC104224).** URL: https://publications.jrc.ec.europa.eu/repository/handle/JRC104224
- Load factor vs water level by vessel size on the Danube: at the lowest recorded level (177 cm
  gauge) small vessels ≈ 50 % load factor, large vessels 20–30 % [search summary].

**B8. Riquelme-Solar, M., van Slobbe, E., Werners, S.E. (2015). Adaptation turning points on inland
waterway transport in the Rhine River. Journal of Water and Climate Change 6(4), 670–682.
DOI 10.2166/wcc.2014.091.** Adaptation-turning-point method; when do dry periods stop IWT
operators from guaranteeing reliable service. Related: van Slobbe et al. (2016) The future of the
Rhine: stranded ships and no more salmon? Reg. Env. Change, DOI 10.1007/s10113-014-0683-z.

**B9. Koetse, M.J., Rietveld, P. (2009). The impact of climate change and weather on transport: an
overview of empirical findings. Transportation Research Part D 14(3), 205–221.** Survey; IWT
section: more frequent low water may "considerably increase" IWT costs via load-factor cuts.

**B10. Hendrickx, C., Breemersch, T. (2012). The effect of climate change on inland waterway
transport. Procedia – Social and Behavioral Sciences 48, 1837–1847. DOI 10.1016/j.sbspro.2012.06.1158.**
ECCONET impact chain (navigation conditions → cost advantage → reliability); quantified results
not retrievable (403).

**B11. Nilson, E., Krahe, P., Lingemann, I., Horsten, T., Klein, B., Carambia, M., Larina, M.
(2014). Auswirkungen des Klimawandels auf das Abflussgeschehen und die Binnenschifffahrt in
Deutschland. KLIWAS-Schriftenreihe 43/2014, BfG Koblenz. DOI 10.5675/Kliwas_43/2014_4.01.**
Near future (2021–2050): number of days below the 1961–1990 low-flow threshold at Kaub remains
within the range observed since the 1950s in all but one projection; far future: south of the
Main increases in low flows are mitigated, north of it a slight decline in low-flow extremes
[search summary]. Also EU-ECCONET Report 1.4 (Nilson et al. 2013) and the Copernicus SWICCA
"Inland navigation (Rhine)" technical report (https://climate.copernicus.eu/sites/default/files/2021-02/D2.1%20SWICCA_Workflows_Final_Inland%20navigation-Rhine%20river.pdf),
which builds Kaub water-depth thresholds per vessel type from ELWIS data.

**B12. Wanders, N., Wada, Y. (2015). Human and climate impacts on the 21st century hydrological
drought. Journal of Hydrology 526, 208–220. DOI 10.1016/j.jhydrol.2014.10.047.** Global; human
water use significantly worsens future low flows. Background only. ("Klein Tank" reference not
identified; see gaps.)

### C. Engineering / hydrology of the Rhine bottleneck

**C1. van Dorsser, C., Vinke, F., Hekkenberg, R., van Koningsveld, M. (2020). The effect of low
water on loading capacity of inland ships. EJTIR 20(3), 47–70. DOI 10.18757/ejtir.2020.20.3.3981.**
URL: https://journals.open.tudelft.nl/ejtir/article/view/3981 (open access)
- General model of deadweight/payload vs available depth needing only vessel type, length, beam.
- Table 1 minimum operational draught: Class II/III 1.20 m; IV 1.30 m; V 1.40 m; VI 1.50 m;
  pusher barge 1.70 m. Default under-keel clearance (UKC): 10 cm (sand) / 20 cm (stone) for dry
  bulk and containers; 20 cm / 30 cm for tankers and pusher barges; in extreme 2018 conditions
  operators went down to 15–20 cm UKC.
- Kaub depth formula: depth = 1.90 m + gauge − 0.78 m. 16 Oct 2018, Kaub 42 cm → depth 1.54 m:
  only 5 of Contargo's 40 container ships still ran between Neuss and Ginsheim (≈ 200 km); i.e.
  most Class V+ motor ships stop at ≈ 1.5 m depth. Rotterdam–Duisburg continued at 1.60 m
  reported depth (24–31 Oct, 21 Nov–3 Dec 2018). 22 Oct 2018, Kaub 25 cm → depth 1.37 m: only
  Class II/III ships (draught ≈ 1.20 m) still sailed. Consumables 4–8 % of design DWT. BIVAS
  (Dutch model) default low-water load 50 % (Meijeren 2011) or 67 % (Prins 2017) of max load.

**C2. Vinke, F.R.S., van Koningsveld, M., van Dorsser, C., Baart, F., van Gelder, P.H.A.J.M.,
Vellinga, T. (2022). Cascading effects of sustained low water on inland shipping. Climate Risk
Management 35, 100400. DOI 10.1016/j.crm.2022.100400.** URL: https://www.sciencedirect.com/science/article/pii/S2212096322000079
- Discrete-event simulation of bulk transport Rotterdam–Duisburg during the 2018 event; impact
  varies by vessel type through cascading effects on fleet composition, number of trips, seaport
  congestion and destination storage. As cited by Campoverde et al. (2025): the 2018 discharge
  reduction required ≈ 3× more trips to keep volumes, an additional transport cost of ≈ EUR 5 m
  per week by the end of 2018 [secondary; verify].

**C3. Vinke, F., Turpijn, B., van Gelder, P., van Koningsveld, M. (2023). Inland shipping response
to discharge extremes: a 10 years case study of the Rhine. Climate Risk Management 43, 100578.
DOI 10.1016/j.crm.2023.100578.** Ten years of Rhine-corridor trip data (Rotterdam–Germany/
Switzerland); fleet composition and vessel deployment change during low and high discharge;
2018, 2019 and 2022 droughts. Quantities (trips, TEU per trip per discharge class) are in the
paper's figures; not extracted (paywalled).

**C4. ICPR (IKSR) Report 263 (2020). Bericht zum Niedrigwasserereignis Juli–November 2018.**
URL: https://www.iksr.org/fileadmin/user_upload/DKDM/Dokumente/Fachberichte/DE/rp_De_0263.pdf
- Kaub 2018: MNM7Q (1961–2010) 851 m³/s; maximum continuous shortfall of MNM7Q 131 days;
  Worms–Kaub ≈ 120 low-water days of which ≈ 20 in class 4 ("very rare", > 20-yr); lower Rhine
  (Andernach, Cologne, Lobith) ≈ 130 days. Return period of the DURATION: > 50 yr from the Upper
  Rhine to Kaub, ≈ 100 yr on the Lower Rhine; of the minimum discharges: 35–40 yr from Worms
  downstream, 10–15 yr upstream of Maxau. Largest event of the last 50 years from Maxau down;
  comparable to the 1921 and 1940s events. Navigation: on the Middle Rhine in October 2018 vessels
  could load only ≈ 20 %; passenger shipping loss ≈ EUR 1 m on the Middle Rhine. Cites Kiel IP
  losses. (Campoverde et al. 2025 cite "IKSR 2020" for "over 2 billion euros in manufacturing
  losses".)

**C5. ICPR Report 248 (2018). Inventory of low-water conditions on the Rhine (Bestandsaufnahme zu
den Niedrigwasserverhältnissen am Rhein).** URL: https://www.iksr.org/fileadmin/user_upload/DKDM/Dokumente/Fachberichte/DE/rp_De_0248.pdf
- Mean annual low-water days at Kaub (class 1 = below MNM7Q): 17.9 (1921–2010), 20.4 (1921–60),
  15.9 (1961–2010), 9.4 (1991–2000), 12.0 (2001–2010); class 4/5 days essentially zero since 1981.
  Maximum shortfall durations ≈ 80 days (1921), up to 138 days (late 1940s); since 1972 typically
  ≈ 20 days, max 38 days (before 2018). No trend towards intensification detected.
- Near-future projection (COSMO-CLM 4.8 A1B, 2021–2050, three runs): low-water discharges at Kaub
  −5 to −10 %; shortfall durations +5 to +17 days/yr (NM7Q summer half-year −5 to −13 %).

**C6. Campoverde, A.L., Ehret, U., Ludwig, P., Pinto, J.G. (2025). Drought propagation in the
Rhine River basin and its impact on navigation using LAERTES-EU regional climate model dataset.
EGUsphere preprint 2025-3988. DOI 10.5194/egusphere-2025-3988.** In 2018 the average duration below
GlQ20 across Rhine gauges was 93 days (140–150 days at the worst gauges); BAW uses GlQ20 −30 % as
the severe threshold (the 2018 case); the most severe simulated event in a 1,000+-year ensemble
gives ≈ 115 days below GlQ20.

**C7. Turpijn, B., Baart, F., Tavasszy, L., van Koningsveld, M. (2026). 50-Years Inland Waterway
Freight Data in the Rhine-Alpine Corridor. Scientific Data 13, 472. DOI 10.1038/s41597-026-06875-3.**
Open dataset 1970–2023 (tonnes, tonne-km, NST-R/NST2007/CCR commodity groups, NL NUTS-2 O-D
1988–2023; sources CBS, Rijkswaterstaat, Destatis, Eurostat, ITF). Rhine-Alpine corridor ≈ 70 % of
European IWT. Best single source for building monthly/annual validation series by commodity.

**C8. Kaub gauge reference facts (Wikipedia EN/DE; WSV/BfG).** URLs: https://en.wikipedia.org/wiki/Kaub_gauging_station ; https://de.wikipedia.org/wiki/Pegel_Kaub
- GlW 0.77 m (from 1 Jan 2023; 0.78 m before); guaranteed fairway depth 1.90 m below GlW; depth
  at gauge 0 cm = 1.13 m (DE wiki) / formula gauge + 1.12 m (CCNR). Mean level 2.08 m (2010–2020).
- Record lows: 54 cm (5 Nov 1947); 35 cm (28 Sep 2003); 25 cm (22 Oct 2018; DE wiki 24 cm);
  ≈ 30–32 cm (15–17 Aug 2022; Bloomberg: briefly 30 cm on 15 Aug; Reuters: 32 cm); 5–6 cm
  (14–17 Aug 2026, first single-digit reading since 1880). 2011: ≈ 55 cm (23 Nov 2011); 2015:
  51–56 cm (Nov 2015) [search summaries].
- Container-vessel load vs Kaub level (Contargo-based): 250 cm 100 %; 135 cm 50 %; 75 cm 25 %
  (four times as many barges); 55 cm 16 %; 40 cm "freight navigation practically impossible";
  35 cm minimum for special low-draught vessels. Full loading of a large vessel needs ≈ 150 cm.

### D. Official statistics and market reports

**D1. Destatis press release 112/2019 (25 Mar 2019). Niedrigwasser beschert Binnenschifffahrt
Rekordminus.** URL: https://www.destatis.de/DE/Presse/Pressemitteilungen/2019/03/PD19_112_463.html
- 2018: 198.0 Mt (−11.1 % vs 222.7 Mt in 2017), the largest fall on record. H1 2018 −1.1 %;
  Aug–Nov 2018 each double-digit y/y declines, November −34 % (largest), December −12.4 %.
  Domestic 52.1 Mt (−6.0 %), exports 44.3 Mt (−13.5 %), imports 90.2 Mt (−11.1 %), transit
  11.4 Mt (−22.4 %); containers 2.4 m TEU (−8.3 %).

**D2. BDB – Bundesverband der Deutschen Binnenschifffahrt (Nov 2019). Kennzahlen zum
Niedrigwasserjahr 2018.** URL: https://www.schifffahrtsverein.de/2019/11/26/bdb-stellt-kennzahlen-zum-niedrigwasserjahr-2018-vor/
- 2018 transport performance 46.9 bn tkm (−15.5 % vs 55.5 bn tkm in 2017). Declines by waterway:
  Rhine area −11.8 %, Moselle −18.4 %, West-German canals −13.1 %, Main-Danube canal −33.3 %,
  Danube −32.8 %. Composition 2018: ores/stones/earths 26.3 % (52.0 Mt), refinery/mineral-oil
  products 16.6 % (32.9 Mt), coal/crude/gas 13.2 % (26.2 Mt), chemicals 10.5 % (20.8 Mt); IWW share
  of German freight performance fell to 6.8 % (from 8.2 %); fleet 1,980 vessels, 2.53 Mt capacity.

**D3. Destatis press release 119/2023 (Mar 2023). Gütertransport in der Binnenschifffahrt 2022 so
niedrig wie noch nie seit der deutschen Vereinigung.** URL: https://www.destatis.de/DE/Presse/Pressemitteilungen/2023/03/PD23_119_463.html
- 2022: 182 Mt (−6.4 % vs 2021; −11.0 % vs 2019). August 2022: 11.7 Mt (−26.8 % y/y), lowest
  month since reunification. Commodities 2022: mineral-oil products 27.0 Mt (−4.1 %), coal 25.6 Mt
  (+12.1 %, gas substitution), stones/earths 22.7 Mt (−8.1 %), iron ore 19.7 Mt (−5.7 %), basic
  chemicals 13.0 Mt (−14.1 %), containerised goods 11.9 Mt (−11.2 %). Imports 84.9 Mt (−3.8 %),
  exports 43.7 Mt (−12.1 %), domestic 44.6 Mt (−3.8 %). Dry bulk 58.5 %, liquid bulk 24.7 %,
  containers 10.0 % of tonnage; 92.2 % of imported coal came via the Netherlands.
- Destatis N053/2022: 86 % of German IWW tonnage Jan–May 2022 was carried on the Rhine.
- Destatis 2016 (PD16_116): 2015 IWW tonnage −3.1 %, attributed to prolonged low water.
- 2025: 171.6 Mt, lowest since 1990 (press, 2026).

**D4. CCNR Market Observation, Annual Report 2019 (data 2018).** URL: https://www.ccr-zkr.org/files/documents/om/om19_II_en.pdf
- Traditional Rhine (Basel–NL border) 165 Mt in 2018, −11 % vs 2017, "mainly" low water, business
  cycle a "much smaller" role. Segments 2018: chemicals −13 %, mineral-oil products −14 %,
  containers −13 % (net weight) / −10 % TEU (2.13 m TEU), sand/stones/building materials −5 %
  (smallest drop); container TEU Germany −8 %, NL −3 %, France −5 %.
- Freight rates: dry-cargo rates in the Rhine basin ≈ 2.5× normal in Oct–Nov 2018 (Panteia
  index; coal, iron ore and containers rose most, agribulk and sand least); liquid-cargo (gasoil
  ARA→Rhine) spot rates ≈ 4.5× normal (PJK index; "more than four times" in the summary).
  Dutch small-vessel operators moved to the Rhine to capture high rates; Dutch IWW turnover rose
  in 2018 despite lower volumes.
- Kaub days with Q < 783 m³/s (≈ 78 cm): 107 in 2018 vs 171 (1857), 173 (1949), 156 (1921),
  146 (1971); impact on volumes was smaller historically because of smaller vessels.
- Rhine ports waterside traffic −10.3 % on average (Kehl, Ludwigshafen up). Port of Strasbourg:
  low water mid-July to late December 2018, container ships stopped for two months, containerised
  rail traffic +19 %. Rotterdam IWW hinterland volume −4 %. Fleet capacity utilisation rose;
  shortages of vessels in H2 2018. Reproduces Kiel's EUR 1.9 bn (Q3) / EUR 2.9 bn (Q4) IP losses.

**D5. CCNR Market Insight November 2019.** URL: https://www.ccr-zkr.org/files/documents/om/om19_III_en.pdf
- EU IWW performance Q1 2019 37.5 bn tkm, +30 % vs Q4 2018 (rebound within one quarter); Rhine
  dry bulk Q1 2019 +3.9 % vs Q1 2018. Rhine container traffic H1 2019 −16 % vs H1 2018: a
  persistent modal-share LOSS after the 2018 event (shippers "more reluctant"). PJK liquid index
  fell strongly in Dec 2018–Q1 2019 but did not fully revert to pre-2018 levels.

**D6. CCNR Market Observation, Annual Report 2023 (data 2022).** URL: https://inland-navigation-market.org/wp-content/uploads/2025/01/CCNR_annual_report_EN_2023_WEB_rev.pdf
- Kaub days below EWL: 107 (2018), 10 (2021), 41 (2022); 2022 low water July–August only vs
  August–November 2018; 2018 had many more days with available draught < 1.80 m.
- Traditional Rhine 155.5 Mt in 2022 (−7.8 % vs 168.6 Mt); entire Rhine 292 Mt (−6.8 % vs 314 Mt).
  Segments (entire Rhine, 2022 vs 2021): coal +10.6 % (+27 % in H1), containers −12.2 %,
  sand/stones −11.5 %, mineral-oil products −9.5 %, metals −7.5 %, agri-food −5.9 %, iron ore
  −2.8 %, chemicals −1.6 %, fertilisers −26 %. Europe (EU-27+CH+RS+MD): 485.4 Mt (−5.5 %),
  122.0 bn tkm (−10.6 %).
- Freight rates 2022 +42.5 % on average vs 2021 (all segments; low water, coal boom, capacity
  moved to the Danube). Dry-bulk spot index Q3/Q4 2022 = 240.9/203.9 vs 118.1/159.1 in 2021;
  liquid index 140.7/134.4 vs 92.9/114.2 (i.e. Q3 2022 ≈ 2.0× and 1.5× the year-earlier level).
- Loading degree of laden dry-cargo vessels at Iffezheim lock (Upper Rhine): 31.3 % in August 2022
  vs 60.7 % in February and 49.8 % annual average (tankers 48.7 %); 47 % of passages empty.
- Rhine container transport "has never been the same" since 2018 (modal-share loss); IWW
  employment low point in 2018.

**D7. CCNR Market Insight April 2026.** URL: https://ccnr.eu (extracted text in pdftxt/). 2025:
Kaub 12 days below EWL in Q1–Q3 2025 (0 in 2024); low point 79 cm on 13 Apr 2025; Rhine transport
decoupled from industrial production after the 2015–2018 low-water years.

**D8. Eurostat, Statistics Explained: Inland waterway freight transport – quarterly and annual
data (2026).** URL: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Inland_waterway_freight_transport_-_quarterly_and_annual_data
- EU IWW tonne-km: 2018 −10.9 %, 2019 +6.6 %, 2022 −9.8 %, 2023 lowest since 2005, 2024 +4.5 %,
  2025 −3.0 %. Germany + Netherlands = 71.9 % of EU tkm (2025). (Another summary quotes −8.6 % for
  2018 and "Rhine traffic −11.9 %" [search summary; probably tonnes vs tkm].)

**D9. US EIA, Today in Energy, 5 Nov 2018: Low Rhine River water levels disrupt petroleum product
shipments to parts of Europe.** URL: https://www.eia.gov/todayinenergy/detail.php?id=37414
- Kaub October 2018 average 1.7 ft (≈ 52 cm) vs 5-yr average 4.8 ft (≈ 146 cm). Barge freight
  Rotterdam→Basel for distillate: ≈ $5/bbl (July) → > $35/bbl (late Oct 2018), ≈ 7×; Rotterdam→
  Duisburg ≈ $1 → > $4/bbl. [derived: 1 t diesel ≈ 7.45 bbl → ≈ $37/t → ≈ $260/t; at 1.14 $/EUR
  ≈ EUR 33/t → EUR 230/t.] Rack-price premiums: Duisburg $0.15 → > $0.20/gal, Karlsruhe $0.20 →
  > $0.40/gal (June → Oct 2018). ARA distillate stocks 15.7 → 21.0 m bbl (backing up at the coast).

**D10. Contargo, Kleinwasserzuschlag Pegel Kaub (2026 notice) and Low-water info 2017.**
URL: https://www.contargo.net/de/business/business-news/detail-business/anpassung-des-kleinwasserzuschlags-pegel-kaub/
- Surcharge per container for terminals south of Koblenz when Kaub < 81 cm: 80–71 cm EUR 300 (20')
  / 380 (40'); 70–61 cm 400/480; 60–51 cm 550/645; 50–41 cm 775/930; ≤ 40 cm 1,075/1,280.
  Transport obligation ends at Kaub ≤ 80 cm. Earlier (2018) schedule reported by agrarheute: 120/165
  at a mild level and 550/645 at the low level. Contargo (2017): at 78 cm four times as many ships
  as at 250 cm.

**D11. Deutscher Bundestag, Drucksache 19/9524 (2019), answer on the release of strategic oil
reserves.** URL: https://dserver.bundestag.de/btd/19/095/1909524.pdf
- Release ordinance of 24 Oct 2018 because of supply bottlenecks due to low river levels
  (especially the Rhine); regionally limited to fuel depots in Hesse, Rhineland-Palatinate,
  Baden-Württemberg, Cologne district, Lower Franconia (jet fuel: Hesse, NRW). Gross proceeds of
  the released stocks EUR 246.8 m (gasoline 69.9, diesel 150.5, jet A-1 26.4); net EUR 207.4 m.
  Fourth release since 1978 (1991, 2005, 2011, 2018); France and Switzerland also released
  reserves. Klimareporter (25 Jul 2022) adds that some NRW filling stations temporarily ran dry
  in 2018 because too few trucks were available.

### E. Firm- and sector-level evidence

**E1. BASF (26 Feb 2019), press release P-19-141.** URL: https://www.basf.com/global/en/media/news-releases/2019/02/p-19-141
- Ludwigshafen: for much of Q3 and Q4 2018 raw-material deliveries by ship were nearly
  impossible; plant utilisation reduced; 2018 earnings (EBIT) lowered by ≈ EUR 250 m. (C&EN,
  Aug 2026: BASF has since chartered low-water vessels; Aug 2026 statement: isolated bottlenecks.)

**E2. thyssenkrupp Steel force majeure (Platts via EUROMETAL, 22 Oct 2018).** URL: https://eurometal.net/tk-declares-force-majeure-on-low-rhine-river-levels/
- Push-tow traffic Rotterdam→Duisburg halted; customers supplied pro rata. Duisburg-Ruhrort
  167 cm (forecast 152 cm), lowest since 2014; barge loads cut from ≈ 2,000 t to ≈ 700 t (35 %);
  suppliers shifted to truck/rail at higher cost amid rail capacity and driver shortages.
  ArcelorMittal (Duisburg-Ruhrort), Ineos, Solvay also declared force majeure in 2018 [search
  summary]. 2026: force majeure again (16 Jul 2026); hot-metal output reduced.

**E3. VCI (Verband der Chemischen Industrie), Q4 2018 report "Rückschlag für das Chemiegeschäft".**
[search summary; page now 404] Chemical-pharmaceutical production −10 % q/q in Q4 2018 and −6.3 %
y/y; chemicals excluding pharma −3.2 % q/q; sector sales −3.1 % q/q (EUR 46.5 bn); 2018 sales
−2.5 % (EUR 198.5 bn). VCI attributed the fall mainly to weak demand; the low-water logistics
disruption is documented separately (VCI 8-point plan with BMVI, 2019).

**E4. Power sector.** Reuters 4 Aug 2022 (https://uk.investing.com/news/stock-market-news/low-rhine-water-level-to-hit-output-at-staudinger-5-coal-plant-2709550):
Uniper Staudinger 5 (510 MW, on the Main) "irregular operation" to 7 Sep 2022 due to limited coal
on site; barge deliveries to the plant stop at Kaub < 40 cm; EnBW (Karlsruhe RDK, coal from
Rotterdam) also affected; "similar conditions caused a fall in output at power stations in 2018".
Klimareporter (2022): coal barges could take only 30–40 % of normal loads (Verein der
Kohlenimporteure). Bloomberg Aug 2026: EnBW expects a "low double-digit-million-euro" earnings
hit. No plant-level MWh loss for 2018 found.

**E5. Gobert, J., Rudolf, F. (2023). Rhine low water crisis: from individual adaptation
possibilities to strategical pathways. Frontiers in Climate 4, 1045466. DOI 10.3389/fclim.2022.1045466.**
Qualitative port/firm study (Upper Rhine): Port of Strasbourg had its lowest tonnage in half a
century in 2018; French Upper-Rhine ports −35 % in transported commodities during the crisis.

**E6. Science Media Center Germany (15 Jul 2026), expert statements (Meuchelböck/Kiel, Nilson/BfG,
Lehmann/TU Darmstadt, Borchardt/UFZ).** URL: https://sciencemediacenter.de/angebote/niedrige-wasserstaende-herausforderungen-fuer-schifffahrt-und-wirtschaft-26168
- 2018: IWW exports −≈ 20 %, imports −12 %. IWW share of German freight 4.7 % (2017) → 4.1 %
  (2024); IWW tonnage −49 Mt (−22 %) since 2017; Rhine ≈ 70 % of IWW volume; rail share rose from
  16.5 % to 21 %. Severe low water halves cargo per ship → twice the number of vessels.

**E7. 2026 event snapshot (context for the case study).** Bloomberg/swissinfo 11 Aug 2026; Argus
5 Aug 2026 (https://www.argusmedia.com/de/news-and-insights/latest-market-news/2861391-historischer-tiefstand-beim-pegel-kaub);
Reuters/MercoPress 3 Aug 2026; The Rail Agenda 18 Aug 2026; DE Wikipedia.
- Kaub 25 cm (31 Jul), 23 cm (5 Aug), 14 cm (11 Aug), 6 cm (14 Aug), 5 cm (17 Aug 2026).
  Cologne 55 cm (12 Aug; previous record 69 cm Oct 2018; mean 2.97 m); Lobith 6.47 m below the
  Aug 2022 low; Rhine inflow ≈ 692 m³/s vs ≈ 1,900 typical.
- Load factors: at Kaub 40–50 cm vessels carry ≈ 20 % (WSV); a 1,200 t vessel loads 180 t to
  Karlsruhe at Kaub 23 cm (15 %), special low-draught ships max 700 t; 110-m ships at Ruhrort
  154 cm ≈ 25 % of ≈ 2,000 t.
- Rates: Rotterdam→southern Germany ≈ EUR 45/t (June) → ≈ EUR 150/t (July 2026); ARA→Karlsruhe
  ≈ EUR 215/t (five-fold from ≈ EUR 45/t at end-June), ARA→Basel EUR 275/t mid-August 2026 [search
  summary, Argus]; rates to Duisburg/Frankfurt/Karlsruhe at records since Argus assessments began
  (2012); Cologne and Basel rates were higher in August 2022.
- Substitution: DB Cargo mobilises 900 wagons (300 immediately) ≈ 200 barges; Covestro: 60 trucks
  to replace one 1,500 t barge; twelve Länder suspended Sunday truck bans; thyssenkrupp force
  majeure; Kooths (Kiel) −0.1 to −0.2 % Q3 GDP; Solveen (Commerzbank) −0.35 pp Q3 GDP if it lasts
  to mid-September.

### F. Modelling precedents (IO / CGE / ABM / network) for citation and cross-checks

- **Colon, C., Hallegatte, S., Rozenberg, J. (2021).** Criticality analysis of a country's transport
  network via an agent-based supply chain model. Nature Sustainability 4, 209–215.
  DOI 10.1038/s41893-020-00649-4. DisruptSC origin (Tanzania roads); code Zenodo 7401053.
- **Inoue, H., Todo, Y. (2019).** Firm-level propagation of shocks through supply-chain networks.
  Nature Sustainability 2, 841–847. DOI 10.1038/s41893-019-0351-x. ~1 m Japanese firms; Nankai
  earthquake indirect losses 10.6 % of GDP vs 0.5 % direct — benchmark for indirect/direct ratios.
- **Hallegatte, S. (2008).** An adaptive regional input-output model and its application to the
  assessment of the economic cost of Katrina. Risk Analysis 28(3), 779–799.
  DOI 10.1111/j.1539-6924.2008.01046.x; and Hallegatte (2014) Modeling the role of inventories and
  heterogeneity..., Risk Analysis 34(1), 152–167 (inventory dynamics — the mechanism at stake here).
- **Otto, C., Willner, S.N., Wenz, L., Frieler, K., Levermann, A. (2017).** Modeling loss-propagation
  in the global supply network: the dynamic agent-based model Acclimate. JEDC 83, 232–269.
  DOI 10.1016/j.jedc.2017.08.001.
- **Wenz, L., Levermann, A. (2016).** Enhanced economic connectivity to foster heat stress-related
  losses. Science Advances 2(6), e1501026. DOI 10.1126/sciadv.1501026.
- **Guan, D., Wang, D., Hallegatte, S., et al. (2020).** Global supply-chain effects of COVID-19
  control measures. Nature Human Behaviour 4, 577–587. DOI 10.1038/s41562-020-0896-8 (losses more
  sensitive to duration than to strictness — analogous to low-water duration effects).
- **Koks, E.E., Rozenberg, J., Zorn, C., Tariverdi, M., Vousdoukas, M., Fraser, S.A., Hall, J.W.,
  Hallegatte, S. (2019).** A global multi-hazard risk analysis of road and railway infrastructure
  assets. Nature Communications 10, 2677. DOI 10.1038/s41467-019-10442-3.
- **MacKenzie, C.A., Barker, K., Grant, F.H. (2012).** Evaluating the consequences of an inland
  waterway port closure with a dynamic multiregional interdependence model. IEEE Trans. SMC-A
  42(2). DOI 10.1109/TSMCA.2011.2164065. **Oztanriseven, F., Nachtmann, H. (2017).** Economic impact
  analysis of inland waterway disruption response. The Engineering Economist 62(1), 73–89.
  DOI 10.1080/0013791X.2016.1163627. **Welch, K., Lambert, L.H., Lambert, D.M., Kenkel, P. (2022).**
  Flood-induced disruption of an inland waterway transportation system and regional economic
  impacts. Water 14(5), 753. DOI 10.3390/w14050753 (MRIO, Oklahoma 2019: 63–750 jobs,
  $14.5–165 m output, $5.7–68.7 m value added depending on closure length). US IWW precedents.
- **Jansen op de Haar, M., Frutos Rodriguez, D. (2026).** Digital twin-based simulation for
  predictive decision-making in waterway logistics. arXiv:2606.13492 (predictive routing under
  water-level uncertainty; −28.3 % fuel costs).
- **Barata da Rocha, M., Grabbe, H., Poitiers, N. (2025).** Climate risks to global supply chains.
  Bruegel Working Paper 20/2025 (policy framing; Rhine 2018/2022 as case).
- **Schweikert, A., Chinowsky, P., Espinet, X., Tarbert, M. (2014).** Climate change and
  infrastructure impacts: comparing the impact on roads in ten countries through 2100. Procedia
  Engineering 78, 306–316 (infrastructure stressor-response; peripheral).

---

## (b) Validation targets

| # | Quantity (unit) | Value | Event / year | Source |
|---|---|---|---|---|
| **Exposure / hydrology** | | | | |
| 1 | Kaub minimum level (cm) | 25 (22 Oct 2018) | 2018 | WSV/BfG via Wikipedia; van Dorsser 2020 |
| 2 | Kaub minimum level (cm) | ≈ 30–32 (15–17 Aug 2022) | 2022 | Bloomberg/Reuters; DB Research |
| 3 | Kaub minimum level (cm) | 35 (28 Sep 2003); ≈ 55 (Nov 2011); 51–56 (Nov 2015); 54 (1947) | 2003/2011/2015/1947 | DE Wikipedia; press |
| 4 | Kaub minimum level (cm) | 5–6 (14–17 Aug 2026) | 2026 | Bloomberg; DE Wikipedia |
| 5 | Days Kaub < EWL (78 cm) per year | 107 (2018); 41 (2022); 10 (2021); 0 (2024); 12 (Q1–Q3 2025) | — | CCNR 2019, 2023, Apr 2026 |
| 6 | Kaub low-water days by month 2018 | Aug 30, Sep ≈ 15, Oct 30, Nov 30, Dec 3 | 2018 | Ademmer et al. 2019 |
| 7 | Kaub average level Aug 7–19 2022 (cm) | 40 | 2022 | Deutsche Bank Research 2023 |
| 8 | Historical maxima of days Q < 783 m³/s at Kaub | 171 (1857), 173 (1949), 156 (1921), 146 (1971) | — | CCNR 2019 |
| 9 | Longest continuous shortfall of MNM7Q at Kaub (days) | 131 (2018); ≤ 38 typical 1972–2017; 138 (1940s) | 2018 | ICPR 263; ICPR 248 |
| 10 | Return period of 2018 duration | > 50 yr (Kaub); ≈ 100 yr (Lower Rhine); min. discharge 35–40 yr | 2018 | ICPR 263 |
| 11 | Mean annual days below MNM7Q at Kaub | 17.9 (1921–2010); 12.0 (2001–2010) | climatology | ICPR 248 |
| 12 | Near-future change (2021–2050) | low flows −5 to −10 %; +5 to +17 shortfall days/yr | projection | ICPR 248 (COSMO-CLM A1B) |
| **Vessel capacity vs water level** | | | | |
| 13 | Fairway depth at Kaub (m) | 1.90 + gauge − 0.78 (→ 1.54 m at 42 cm; 1.37 m at 25 cm) | — | van Dorsser 2020; CCNR |
| 14 | Load factor of large container vessels vs Kaub | 250 cm 100 %; 135 cm 50 %; 75–78 cm 25 %; 55 cm 16 %; 40 cm ≈ 0 | — | Contargo 2017 via Wikipedia/Kiel |
| 15 | Minimum operational draught by CEMT class (m) | II/III 1.20; IV 1.30; V 1.40; VI 1.50; pusher barge 1.70; UKC 10–30 cm | — | van Dorsser 2020, Table 1 |
| 16 | Share of container fleet still operating at Kaub 42 cm | 5 of 40 Contargo ships (Neuss–Ginsheim) | 16 Oct 2018 | van Dorsser 2020 |
| 17 | Loadable share, Middle Rhine, Oct 2018 | ≈ 20 % | 2018 | ICPR 263 |
| 18 | Barge payload to Duisburg (Ruhrort 167 cm) | 2,000 t → 700 t (35 %) | 22 Oct 2018 | thyssenkrupp/Platts |
| 19 | Coal-barge loads (share of normal) | 30–40 % | Aug 2022 | Verein der Kohlenimporteure |
| 20 | Dry-cargo loading degree, Iffezheim lock | 31.3 % (Aug 2022) vs 49.8 % annual | 2022 | CCNR 2023 |
| 21 | Load at Kaub 40–50 cm; at 23 cm | ≈ 20 % (WSV); 180 t of 1,200 t (15 %) | 2026 | Reuters; Argus |
| **Transport volumes** | | | | |
| 22 | German IWW tonnage, annual change | −11.1 % (198.0 Mt) | 2018 | Destatis 2019 |
| 23 | German IWW tonnage, monthly y/y | Aug–Nov double-digit; Nov −34 %; Dec −12.4 %; H1 −1.1 % | 2018 | Destatis 2019 |
| 24 | German IWW tonne-km | 46.9 bn (−15.5 %) | 2018 | BDB 2019 |
| 25 | German IWW by flow | domestic −6.0 %; exports −13.5 %; imports −11.1 %; transit −22.4 %; TEU −8.3 % | 2018 | Destatis 2019 |
| 26 | Traditional Rhine tonnage | 165 Mt (−11 %) | 2018 | CCNR 2019 |
| 27 | Traditional Rhine by segment | chemicals −13 %; mineral oil −14 %; containers −13 % (t) / −10 % TEU; sand/stones −5 % | 2018 | CCNR 2019 |
| 28 | Rhine area vs other waterways | Rhine −11.8 %; Moselle −18.4 %; canals −13.1 %; Danube −32.8 % | 2018 | BDB 2019 |
| 29 | Rhine ports waterside traffic | −10.3 % average; Upper-Rhine French ports −35 % | 2018 | CCNR 2019; Gobert & Rudolf 2023 |
| 30 | EU IWW tonne-km | −10.9 % (2018); +6.6 % (2019); −9.8 % (2022) | — | Eurostat |
| 31 | Rebound after event | EU tkm Q1 2019 +30 % vs Q4 2018 | 2019 | CCNR Nov 2019 |
| 32 | Persistent container loss | Rhine containers H1 2019 −16 % vs H1 2018 | 2019 | CCNR Nov 2019 |
| 33 | German IWW tonnage | 182 Mt (−6.4 %); Aug 2022 11.7 Mt (−26.8 % y/y) | 2022 | Destatis 2023 |
| 34 | Traditional / entire Rhine tonnage | 155.5 Mt (−7.8 %) / 292 Mt (−6.8 %) | 2022 | CCNR 2023 |
| 35 | Entire Rhine by segment | coal +10.6 %; containers −12.2 %; sand −11.5 %; mineral oil −9.5 %; metals −7.5 %; ore −2.8 %; chemicals −1.6 % | 2022 | CCNR 2023 |
| 36 | German IWW tonnage | −3.1 % | 2015 | Destatis 2016 |
| 37 | Econometric: IWW volume per low-water day | −0.87 % (t), −0.41 % (t−1); 30 days ≈ −25 % | 1991–2019 | Ademmer et al. 2020/2023 |
| 38 | Container throughput per disruption day | −0.2 %/day; −5.9 % if > 24 days | 2000–2022 | Bedoya-Maya et al. 2024 |
| 39 | Trips needed to keep volume, Rotterdam–Duisburg | ≈ 3× | 2018 | Vinke et al. 2022 [secondary] |
| **Freight prices** | | | | |
| 40 | Liquid-cargo spot rate ARA→Rhine (PJK index) | ≈ 4.5× normal, Oct–Nov 2018 | 2018 | CCNR 2019 |
| 41 | Dry-cargo rates Rhine basin (Panteia) | ≈ 2.5× normal, Oct–Nov 2018 (coal/ore/containers highest) | 2018 | CCNR 2019 |
| 42 | Barge rate Rotterdam→Basel distillate | ≈ $5/bbl (Jul) → > $35/bbl (late Oct) [≈ EUR 33 → 230/t derived] | 2018 | EIA 2018 |
| 43 | Barge rate Rotterdam→Duisburg | ≈ $1 → > $4/bbl | 2018 | EIA 2018 |
| 44 | Rack-price premium Karlsruhe / Duisburg | $0.20 → > $0.40/gal; $0.15 → > $0.20/gal | 2018 | EIA 2018 |
| 45 | Additional transport cost Rotterdam–Duisburg bulk | ≈ EUR 5 m/week (end 2018) | 2018 | Vinke et al. 2022 [secondary] |
| 46 | Average Rhine freight rates, all segments | +42.5 % vs 2021 | 2022 | CCNR 2023 |
| 47 | Spot indices Q3 2022 vs Q3 2021 | dry bulk 240.9 vs 118.1 (≈ 2.0×); liquid 140.7 vs 92.9 (≈ 1.5×) | 2022 | CCNR 2023 |
| 48 | Container low-water surcharge (EUR per 20'/40') | 300/380 at 80–71 cm … 1,075/1,280 at ≤ 40 cm | 2026 schedule | Contargo |
| 49 | Price per tonne at lowest water vs normal | up to +100 % (≈ ×2) | 2003 | Jonkeren et al. 2007/2014 |
| 50 | Barge rates 2026 | ARA→Karlsruhe ≈ EUR 45 → 215/t; ARA→Basel 275/t; Rotterdam→S. Germany 45 → 150/t | 2026 | Argus/Reuters [search summary] |
| **Industrial production / GDP** | | | | |
| 51 | German IP per low-water day | −0.034 % (t), −0.024 % (t−1) → ≈ −1 % per 30 days | 1991–2019 | Ademmer et al. 2020/2023 |
| 52 | Elasticity of IP to IWW volume | 0.036 (same month) + ≈ 0.03 (next month) | 1991–2019 | Ademmer et al. (2SLS) |
| 53 | Peak IP effect, Nov 2018 | −1.5 % (GER 2023) / −1.7 % (Wirtschaftsdienst 2019) below counterfactual | 2018 | Ademmer et al. |
| 54 | German IP growth effect | −0.8 pp (Q3 2018); −0.4 pp (Q4 2018) | 2018 | Ademmer et al. 2019 |
| 55 | German IP loss in euro | EUR 1.9 bn (Q3); EUR 2.9 bn (Q4, incl. 1.0 bn lag) | 2018 | Kiel via CCNR 2019 |
| 56 | German GDP effect | ≈ −0.4 % at peak (lower bound); press: −0.2 pp Q3 / −0.1 pp Q4 | 2018 | Ademmer et al.; VCI/press |
| 57 | 10 % exogenous IWW drop → IP / GDP | −0.4 % IP; ≈ −0.1 % GDP | generic | Ademmer et al. |
| 58 | Chemical-pharma production Q4 2018 | −10 % q/q (−6.3 % y/y); chemicals ex-pharma −3.2 % q/q | 2018 | VCI [search summary] |
| 59 | BASF EBIT loss | ≈ EUR 250 m | 2018 | BASF 2019 |
| 60 | Ex-ante 2026 GDP estimates | −0.1 to −0.2 % Q3 (Kiel); −0.35 pp Q3 (Commerzbank) | 2026 | Kooths; Solveen |
| 61 | Welfare loss IWT market | EUR 91 m (2003, ≈ 13 % turnover); EUR 28 m/yr avg; EUR 480 m NW-Europe 2003 | 2003 | Jonkeren et al. 2007, 2014 |
| **Structure / substitution** | | | | |
| 62 | Rhine share of German IWW | ≈ 80 % (BDB); 86 % (Jan–May 2022); ≈ 70 % (2026 statement) | — | Kiel; Destatis; SMC |
| 63 | IWW share of German freight | ≈ 6 % tonnes (2017); 6.8 % tkm (2018); 4.7 % (2017) → 4.1 % (2024) | — | Kiel; BDB; SMC |
| 64 | IWW share of German GVA | < 0.2 % | — | Ademmer et al. |
| 65 | IWW share by commodity | ≈ 30 % coal/crude/gas; ≈ 20 % coke & petroleum products; 10–30 % chemicals | 2017 | Ademmer et al.; Kiel 2022 |
| 66 | German IWW commodity mix (t) | ores/stones 26.3 %; mineral oil 16.6 %; coal/crude/gas 13.2 %; chemicals 10.5 % | 2018 | BDB 2019 |
| 67 | German IWW cargo type mix | dry bulk 58.5 %; liquid 24.7 %; containers 10.0 % | 2022 | Destatis 2023 |
| 68 | Rhine-Alpine corridor share of European IWT | ≈ 70 % | — | Turpijn et al. 2026 |
| 69 | Rail response per low-water day | +0.07 % rail tonnage (road +0.08 %, n.s.) | 1997/2005–2019 | Ademmer et al. App. B |
| 70 | Rail substitution capacity | 900 wagons ≈ 200 barges (DB Cargo); 1 train ≈ up to 10 barges (turnover); 60 trucks per 1,500 t barge | 2026 | Rail Agenda; ZDF; Covestro |
| 71 | Strasbourg containerised rail traffic | +19 % (container barges stopped 2 months) | 2018 | CCNR 2019 |
| 72 | Storage-days / capacity needed (steel firms) | +1–5 empty-storage days (2021–50), +9 (2071–2100); storage +2.5 % / +25 % | projection | Scholten et al. 2014 |
| 73 | Strategic fuel reserve release | 24 Oct 2018; ≈ EUR 247 m of gasoline/diesel/jet released (SW Germany); FR & CH also | 2018 | Bundestag 19/9524 |

---

## (c) Open questions and gaps

1. **Bundesbank primary source.** The "−0.2 pp Q3 2018" figure attributed to the Bundesbank in
   the press is not in the November or December 2018 Monthly Reports (English or German full
   text); nor does the September 2022 report contain a low-water passage. Check the Bundesbank
   December 2018 projection, February 2019 Monthly Report, or the August 2022/2026 German editions
   before citing the Bundesbank for a number. Likewise no "Kiel Policy Brief" and no ifo/RWI/
   DIW/ZEW estimates were found; the Kiel Institute (Wirtschaftsdienst 2019; WP 2155; GER 2023)
   is the only peer-reviewed macro estimate.
2. **No ex-post econometric estimate for 2022.** Only ex-ante statements exist. Using the Kiel
   coefficients with 41 low-water days (July–Aug 2022) gives an implied peak IP effect of roughly
   −1.1 to −1.4 % in August 2022 [derived]; this should be computed explicitly as a target.
3. **Euro-per-tonne spot-rate series for 2018 and 2022** (PJK/Insights Global, Argus) are
   paywalled; only indices (liquid ≈ 4.5×, dry ≈ 2.5× in Oct–Nov 2018; +42.5 % average 2022) and
   EIA's $/bbl Rotterdam–Basel series are public. The Rhine "Rotterdam–Basel × 5–10" claim is
   consistent with EIA (≈ 7×) but no official EUR/t peak was found; the EUR 130/t 2022 record and
   EUR 215–275/t 2026 values come from search summaries of Argus reporting.
4. **Vinke et al. (2022) quantities** (3× trips, EUR 5 m/week) are taken from a citing preprint
   (Campoverde et al. 2025); the paper itself (ScienceDirect) could not be accessed. Vinke et al.
   (2023) trip/TEU statistics likewise not extracted.
5. **Monthly commodity-level Rhine volumes** for 2018 and 2022 (Destatis GENESIS table 46321,
   Turpijn et al. 2026 dataset) were not pulled; they are the natural validation series for a
   spatial model (by commodity, by direction, by port).
6. **Sectoral production indices** (Destatis chemicals, coke/refining, steel; Oct–Nov 2018) not
   extracted; VCI's Q4 2018 numbers are demand-attributed and include volatile pharma.
7. **Damage totals are inconsistent and mostly unsourced**: EUR 2.8 bn (ourrhine.eu), EUR 5 bn
   (iwd), "> EUR 2 bn manufacturing losses" (IKSR 2020 via Campoverde), EUR 4.8 bn H2-2018 IP loss
   (Kiel via CCNR). Use the Kiel decomposition and state scope.
8. **Firm-level 2018 losses beyond BASF** (thyssenkrupp, Evonik, Lanxess, Covestro, Uniper/EnBW/
   Steag, refineries) not quantified; only force-majeure and output-cut notices.
9. **Power-sector effects 2018** (plant-level output cuts; coal stocks) not found; 2022 Uniper
   Staudinger case is qualitative. Gasoline shortages 2018: documented qualitatively (NRW stations,
   reserve release) but no volume of lost sales.
10. **Modal shift** is quantified only weakly (Kiel: rail +0.07 %/day; Strasbourg +19 % rail;
    Rhine containers −16 % in H1 2019). No DB Cargo tonnage actually shifted in 2018/2022/2026 was
    published.
11. **Precise official 2022 Kaub minimum** (daily mean) and per-gauge day counts for 2022 (Cologne,
    Duisburg, Maxau) are in CCNR 2023 figures but not machine-readable; BfG "extreme event" page
    for 2022 does not exist (only 2003 and 2018).
12. **2003 and 2011 German IWW annual declines** (Destatis) were not retrieved (2015: −3.1 %).
13. **Dutch/Belgian/Swiss/French macro effects**: ABN AMRO's Dutch-economy note was unreachable
    (503); CBS reports Dutch IWW turnover rose in 2018 (price effect > volume effect). Swiss fuel
    supply (Basel) relies on the Rhine; Switzerland released reserves in 2018 — no quantification.
14. **Beuthe et al. (2014), Hendrickx & Breemersch (2012)** headline cost/modal-shift percentages
    not accessible (paywall); Jonkeren (2011) 5.4 % maximum modal loss is the usable figure.
15. **"Klein Tank"** could not be matched to a Rhine-navigation paper (likely a European climate
    extremes/E-OBS reference); clarify.
16. **PESETA IV** has no inland-waterway task; cite PESETA III (Demirel & Christodoulou 2018) and
    Christodoulou et al. (2020).
17. **Inventory/buffer evidence**: apart from Scholten et al. (2014) (steel storage days) and the
    EIA ARA stock build-up, no data on firm inventory coverage days during 2018 were found; these
    would be key parameters for DisruptSC's inventory targets.
