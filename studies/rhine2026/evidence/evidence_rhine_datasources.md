# Evidence inventory: quantitative data sources for the summer-2026 Rhine low-water freight disruption

Compiled 2026-09-03 for the DisruptSC EU-scope Rhine study. Each row: name | what it contains | resolution | coverage/latency | access (URL/API/example) | verified? | notes.
"Verified" = endpoint or documentation page actually fetched on 2026-09-03 (Y), only documentation/secondary page fetched (D), or from search snippets only (S).

## 1. River gauges and low-water forecasts (scenario construction)

### 1.1 Datasets

| name | what it contains | resolution | coverage / latency | access (URL / API / example) | verified? | notes |
|---|---|---|---|---|---|---|
| WSV PEGELONLINE REST API v2 (Wasserstraßen- und Schifffahrtsverwaltung des Bundes) | Raw water level W (cm above gauge zero) and, for main gauges, discharge Q (m³/s) for ~700 federal-waterway gauges; station master data (uuid, shortname, number, river-km, gauge zero PNP in m NHN, lat/lon, agency); current value with state flags (`stateMnwMhw`: low/normal/high; `stateNswHsw`) | 15-min (Rhine gauges; Lobith/Pannerdense Kop 10-min) | Rolling window only: documentation says "Es können Daten für die letzten 31 Tage bezogen werden". Verified 2026-09-03: `start=P30D` gives 2,880 points from 2026-08-04 07:15; `start=P31D` gives 2,976 points from 2026-08-03 07:15; any longer `start` (P45D, P60D, 2026-06-01) is silently capped at 3,000 points beginning 2026-08-03 01:15. Latency about 15-60 min. | Base `https://www.pegelonline.wsv.de/webservices/rest-api/v2/`. Stations: `stations.json?waters=RHEIN&includeTimeseries=true&includeCurrentMeasurement=true` (36 Rhine stations incl. Basel-Rheinhalle [BAFU] and Lobith [RWS]). Measurements: `stations/KAUB/W/measurements.json?start=P30D` (shortname or uuid; `start`/`end` as ISO-8601 datetime or ISO period); CSV: `stations/KAUB/W/measurements.csv?start=P1D` (semicolon-separated `timestamp;value`, verified). Discharge: `stations/KAUB/Q/measurements.json?start=P7D`. Docs: https://www.pegelonline.wsv.de/webservice/dokuRestapi | Y (endpoints fetched and parsed 2026-09-03) | No authentication, gzip + ETag; JSON default, CSV and PNG variants. Shortnames with umlauts must be URL-encoded (KÖLN = `K%C3%96LN`), safer to use the uuid. Licence: WSV open data (Datenlizenz Deutschland - Namensnennung 2.0, see Nutzungsbedingungen page). Because of the 31-day cap the June-July 2026 history must come from the PEGELONLINE file archive (next row), a BfG/WSA request, or from a scraper that ran since June. |
| PEGELONLINE file archive ("Freier Download gewässerkundlicher Daten") | Daily files of the last 31 days plus older unchecked raw W and Q data from 1 Jan 2000 onward, per gauge | 15-min raw | 2000-present (unchecked raw data) | https://www.pegelonline.wsv.de/webservices/files/Wasserstand+Rohdaten/RHEIN/KAUB (directory listing per parameter/river/gauge; also `Abfluss+Rohdaten`) | S (URL and description from search; listing fetch pending, see 1.4) | If confirmed, this closes the 31-day gap and gives the full June-September 2026 hydrograph at 15-min resolution for every Rhine gauge. |
| BfG/WSV 6-Wochen-Vorhersage (6-week probabilistic forecast) | Weekly-mean water level and discharge forecasts for shipping-relevant gauges: Rhine Maxau, Kaub, Köln, Duisburg-Ruhrort; Elbe Dresden, Barby, Neu Darchau; Danube Pfelling, Hofkirchen (since July 2026). Ensemble percentiles (5/25/75/95 %) from a water-balance model driven by the ECMWF extended-range ensemble (101 members) plus statistical post-processing | weekly means, 6-week horizon | Issued twice a week (Tue and Fri, late morning) since July 2022 | ELWIS page https://www.elwis.de/DE/Service/Wasserstaende/6-Wochen-Vorhersage-Rhein-Elbe-Donau/6-Wochen-Vorhersage-Rhein-Elbe-Donau-node.html ; per-gauge PDFs (verified links): https://vorhersage.bafg.de/6-Wochen-Vorhersage/Rhein-Kaub_6Wochen_Wasserstand.pdf , `Rhein-Kaub_6Wochen_Abfluss.pdf`, `Rhein-Koeln_6Wochen_Wasserstand.pdf`, `Rhein-Duisburg-Ruhrort_6Wochen_Wasserstand.pdf`, `Rhein-Maxau_6Wochen_Wasserstand.pdf` (CSV numeric download announced on the BfG product page); interactive app https://6wochenvorhersage.bafg.de/ ; product page https://www.bafg.de/DE/5_Informiert/1_Portale_Dienste/6wochenvorhersage/6wochenvorhersage_node.html ; GDI-DE metadata record d55154b2-8031-4ccb-bc60-766d0306f439 | D (BfG product page and ELWIS page fetched; PDF links listed) | No archive of past issues is advertised; for a forecast-skill or "expected duration" analysis request the archive from BfG (Referat M2). For the scenario, the forecast issued in late June / early July 2026 is the information set firms had when they started re-routing. |
| ELWIS 14-day water-level forecast and 05:00 gauge readings (WSV/BfG "Wasserstandsvorhersage") | Deterministic 4-day plus ensemble 14-day forecast of W for Rhine gauges; the ELWIS "Pegelstände" pages carry the 05:00 reading that carriers use as the contractual trigger for low-water surcharges | daily issues | daily | https://www.elwis.de/DE/Service/Wasserstaende/ ; single gauge page https://www.elwis.de/DE/dynamisch/Wasserstaende/Pegeleinzeln:KAUB ; UNDINE Kaub page links directly to the 14-day and 6-week PDFs | D (linked from BfG/UNDINE pages) | Contargo/HGK tariffs reference "Pegel 05:00 Uhr laut ELWIS": ELWIS 05:00 values are the tariff trigger, PEGELONLINE 15-min values are the physical series. |
| BfG UNDINE information platform - Pegel Kaub | Gauge history and characteristic values: observations since 1856, recording gauge since 18.05.1905; PNP NHN +67.67 m (since 1 Nov 2019, DHHN2016); MNQ 769, MQ 1,640, MHQ 4,260 m³/s; lowest discharges 482 m³/s (03.11.1947) and 544 m³/s (22.10.2018); links to Gewässerkundliches Jahrbuch pages, 14-day and 6-week forecast PDFs, extreme-event dossiers (1920/21, 2018), IKSR low-water monitoring | daily (yearbook) | long-term | https://undine.bafg.de/rhein/pegel/rhein_pegel_kaub.html ; other gauges `rhein_pegel_<name>.html`; IKSR low-water monitoring https://undine.bafg.de/rhein/zustand-aktuell/rhein_nw_mon.html | Y (page fetched) | No machine-readable download on the page; it points to the yearbook (PDF) and the data holders. BfG Datenstelle (Datenstelle-M1@bafg.de) holds the daily mean discharge series 1 Nov 1930 - 31 Dec 2025 for Kaub. Useful for the record-low framing (2026-08-17 = 5 cm vs 25 cm on 22.10.2018). |
| GRDC - Global Runoff Data Centre (hosted at BfG) | Mean daily and monthly discharge for >10,000 stations; Rhine at Kaub = GRDC no. 6335100 (other Rhine stations: Rees, Köln, Mainz, Worms, Maxau, Basel-Rheinhalle, Lobith - look up ids in the portal) | daily Q (m³/s) | multi-decade (Kaub daily from 1930s); typical lag 1-3 years, so 2026 will not be there | Portal https://grdc.bafg.de/data/data_portal/ (map/table selection, download form, CSV/ASCII per station with metadata header; free after accepting GRDC terms); station page mirrored at https://www.compositerunoff.sr.unh.edu/html/Polygons/P6335100.html | D (portal and station id confirmed via search) | Use for the baseline hydrology (normal-year distribution of Kaub levels, return period of 2026) and for a Q-W rating relation; not for the 2026 event itself. |
| Rijkswaterstaat WaterWebservices (DDL 2.0) - Lobith | Water level (WATHTE, cm NAP) and discharge at Lobith (Rhine km 862) and all Dutch stations; measurements, forecasts (`verwachting`) and astronomical series | 10-min; daily | Lobith water level since 1901 (daily), gap-free; near-real-time | JSON POST endpoints: catalogue `https://ddapi20-waterwebservices.rijkswaterstaat.nl/METADATASERVICES/OphalenCatalogus`; observations `https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen`; latest `.../OphalenLaatsteWaarnemingen`; Swagger https://ddapi20-waterwebservices.rijkswaterstaat.nl/swagger-ui/index.html ; bulk e-mail download https://waterinfo.rws.nl/#/nav/bulkdownload ; Python `ddlpy` (Deltares, GitHub) or `rws-waterinfo` (PyPI); portal https://waterinfo.rws.nl/publiek/waterhoogte/Lobith(LOBI)/details ; project page https://rijkswaterstaatdata.nl/waterdata/ | D (API doc page fetched, endpoints quoted; no live call yet) | Licence CC0. Location code in Waterinfo = `LOBI`; in the DDL catalogue use compartment `OW`, grootheid `WATHTE`, procestype `meting` (confirm the exact location code in the catalogue). Limit 160,000 observations per request. Lobith is also mirrored in PEGELONLINE (uuid efe13a3d-f239-4655-9c13-4ac56dfa4478, 10-min, last 31 days). |
| BfG Niedrigwasser-Update (2026 weekly low-water reports) | Situation reports: gauge status vs GlW/NNW, discharge, 6-week outlook, navigation notes. 2026 issues (verified list): 25.06 "Hitze verschärft Situation an Flüssen"; 02.07; 09.07; 14.07 "Das Niedrigwasser schreitet voran"; 23.07; 30.07 "Niedrigwasser verschärft sich"; 06.08 "Niedrigwasser wird immer extremer"; 13.08 "Wasserstände an wichtigen Pegeln unterschreiten niedrigste bekannte Werte"; 20.08 "Regen lindert Niedrigwasser etwas"; 27.08 "keine weitere Entspannung bis Mitte September absehbar" | weekly (event-driven) | 2026 series online | Index https://www.bafg.de/DE/5_Informiert/2_Publikationen/Niedrigwasserbericht/niedrigwasserbericht_node.html ; example PDF https://www.bafg.de/SharedDocs/Downloads/DE/bfg_niedrigwasserbericht/2026/260625_nw_bericht.pdf | Y (index page fetched) | Dated narrative anchors for the scenario timeline (when Kaub crossed GlW, when NNW was broken, when the 6-week outlook turned). |
| Historical daily W series for German Rhine gauges (beyond the file archive) | Daily mean/min water levels in the Deutsches Gewässerkundliches Jahrbuch (DGJ, Rheingebiet Teil III); checked series held by WSA Rhein / BfG | daily (yearbook), 15-min (on request) | 1900s-present; yearbook lag 1-2 years | (1) data request to the responsible WSA (Wasserstraßen- und Schifffahrtsamt Rhein, Standort Bingen for Kaub) or BfG Datenstelle; free, DL-DE-BY-2.0; (2) DGJ yearbook PDFs (linked from UNDINE "Jahrbuchseite"); (3) LfU Rheinland-Pfalz https://www.hochwasser.rlp.de/flussgebiet/mittelrhein/kaub (recent window only) | S | Only needed if the 2000+ file archive turns out not to cover checked daily values. |

### 1.2 Kaub (Rhine-km 546.23, uuid 1d26e504-7f9e-480a-b52c-5932be6549ab), last 30 days from the REST API

Fetched 2026-09-03 about 07:10 CEST: `.../stations/KAUB/W/measurements.json?start=P30D` returned 2,880 15-min values, 2026-08-04 07:15 to 2026-09-03 07:00 CEST.

| statistic | value | timestamp(s) (CEST) |
|---|---|---|
| **Minimum** | **5 cm** | 2026-08-17 05:45 - 09:15 (plateau; new all-time record, previous record 25 cm on 22.10.2018) |
| **Maximum** | **77 cm** (= GlW 2022 exactly) | 2026-08-29 18:45 - 22:00 |
| **Current** | **53 cm** (state flag `low`) | 2026-09-03 07:00; discharge Q = 664 m³/s at 06:45 (MNQ 769 m³/s) |
| Mean of window | 36.2 cm | - |

Daily min / mean / max (cm) at Kaub from the same request:

| date | min | mean | max | | date | min | mean | max |
|---|---|---|---|---|---|---|---|---|
| 08-04* | 24 | 25.6 | 28 | | 08-20 | 23 | 34.8 | 43 |
| 08-05 | 17 | 20.2 | 25 | | 08-21 | 42 | 44.6 | 47 |
| 08-06 | 18 | 20.3 | 24 | | 08-22 | 34 | 37.0 | 42 |
| 08-07 | 23 | 24.2 | 27 | | 08-23 | 37 | 44.6 | 52 |
| 08-08 | 24 | 25.7 | 28 | | 08-24 | 51 | 67.8 | 75 |
| 08-09 | 19 | 21.1 | 25 | | 08-25 | 67 | 72.0 | 76 |
| 08-10 | 15 | 16.5 | 19 | | 08-26 | 63 | 65.4 | 68 |
| 08-11 | 13 | 14.6 | 17 | | 08-27 | 57 | 60.0 | 64 |
| 08-12 | 10 | 11.3 | 13 | | 08-28 | 59 | 60.6 | 63 |
| 08-13 | 10 | 11.9 | 14 | | 08-29 | 62 | 70.5 | 77 |
| 08-14 | 6 | 8.1 | 12 | | 08-30 | 70 | 72.4 | 75 |
| 08-15 | 6 | 8.1 | 11 | | 08-31 | 71 | 72.9 | 75 |
| 08-16 | 6 | 6.7 | 8 | | 09-01 | 64 | 68.1 | 72 |
| 08-17 | 5 | 6.4 | 9 | | 09-02 | 52 | 59.2 | 64 |
| 08-18 | 9 | 12.0 | 15 | | 09-03* | 52 | 52.5 | 54 |
| 08-19 | 11 | 13.9 | 22 | | | | | |

(* partial days.) Reading: the trough lasted 10-19 Aug (daily means below 15 cm), a rain-driven recovery on 20-31 Aug peaked exactly at GlW (77 cm) on 29 Aug, and levels are falling again in early September (53 cm on 3 Sep, and the BfG update of 27 Aug expects no relief before mid-September). Raw file kept at `scratchpad/kaub_W_P30D.json`.

### 1.3 Other Rhine gauges, same 30-day window (min / max / current, cm; PEGELONLINE, 2026-09-03 07:00 CEST)

| gauge (Rhine-km) | uuid | 30-d min (date) | 30-d max (date) | current | gauge zero (m NHN) |
|---|---|---|---|---|---|
| IFFEZHEIM (336.2) | b02be240-1364-4c97-8bb6-675d7d842332 | 43 (08-12) | 190 (08-22) | 78 | 110.019 |
| MAXAU (362.3) | b6c6d5c8-e2d5-4469-8dd8-fa972ef7eaea | 292 (08-12) | 421 (08-22) | 333 | 97.721 |
| SPEYER (400.6) | 2cb8ae5b-c5c9-4fa8-bac0-bb724f2754f4 | 156 (08-13/14) | 262 (08-23) | 200 | 88.467 |
| MANNHEIM (424.7) | 57090802-c51a-4d09-8340-b4453cd0e1f5 | 66 (08-14) | 163 (08-23) | 111 | 85.117 |
| WORMS (443.4) | 844a620f-f3b8-4b6b-8e3c-783ae2aa232a | -19 (08-14) | 70 (08-24) | 28 | 84.112 |
| MAINZ (498.3) | a37a9aa3-45e9-4d90-9df6-109f3a28a5af | 103 (08-15) | 179 (08-29) | 147 | 78.373 |
| OESTRICH (518.1) | 665be0fe-5e38-43f6-8b04-02a93bdbeeb4 | 32 (08-14 to 08-17) | 92 (08-29) | 71 | 77.562 |
| BINGEN (528.4) | 0309cd61-90c9-470e-99d4-2ee4fb2c5f84 | n/c | n/c | 78 | 76.185 |
| KAUB (546.2) | 1d26e504-7f9e-480a-b52c-5932be6549ab | 5 (08-17) | 77 (08-29) | 53 | 67.669 |
| SANKT GOAR (556.4) | 550eb7e9-172e-48e4-ae1e-d1b761b42223 | n/c | n/c | 141 | 63.751 |
| KOBLENZ (591.5) | 4c7d796a-39f2-4f26-97a9-3aad01713e29 | -5 (08-15 to 08-17) | 79 (08-31) | 52 | 57.692 |
| ANDERNACH (613.8) | 5735892a-ec65-4b29-97c5-50939aa9584e | 0 (08-17) | 88 (08-31) | 61 | 51.504 |
| BONN (654.8) | 593647aa-9fea-43ec-a7d6-6476a76ae868 | 62 (08-17/18) | 130 (09-01) | 114 | 42.713 |
| KÖLN (688.0) | a6ee8177-107b-47dd-bcfd-30960ccc6e9c | 44 (08-17/18) | 122 (09-01) | 107 | 35.038 |
| DÜSSELDORF (744.2) | 8f7e5f92-1153-4f93-acba-ca48670c8ca9 | -5 (08-16) | 75 (09-01/02) | 65 | 24.529 |
| DUISBURG-RUHRORT (780.8) | c0f51e35-d0e8-4318-afaf-c5fcbc29f4c1 | 126 (08-17) | 208 (09-02) | 198 | 16.106 |
| WESEL (814.0) | f33c3cc9-dc4b-4b77-baa9-5a5f10704398 | 62 (08-17) | 148 (09-01) | 138 | 11.206 |
| REES (837.4) | 2f025389-fac8-4557-94d3-7d0428878c86 | 11 (08-16 to 08-18) | 92 (09-02) | 84 | 8.743 |
| EMMERICH (851.9) | 9598e4cb-0849-401e-bba0-689234b27644 | -28 (08-17) | 49 (09-02) | 45 | 7.998 |
| LOBITH (862.0, RWS, cm NAP) | efe13a3d-f239-4655-9c13-4ac56dfa4478 | n/c | n/c | 692 | - |
| Basel-Rheinhalle (164.3, BAFU CH) | 94f6eff1-4f3f-4850-82e0-a086198e9ffd | n/c | n/c | 495 | 240 m ü.M. |

(n/c = not computed.) Station master file kept at `scratchpad/pegel_stations_rhein.json`. The trough is nearly synchronous along the German Rhine (Kaub 17 Aug 05:45; Koblenz/Andernach 15-17 Aug; Köln/Düsseldorf/Duisburg/Emmerich 16-18 Aug; Upper Rhine Maxau/Speyer 12-14 Aug), so a scenario can treat the whole German Rhine as one low-water episode with at most a one-day lag between sections.

---

## Status note (2026-09-03)

PARTIAL: the collecting agent stalled after section 1 (gauges, forecasts, the
30-day PEGELONLINE extract for every Rhine gauge). Sections still to compile:
2 vessel loading vs Kaub (covered meanwhile by `evidence_rhine_literature.md`
C1/C8 and `scenarios/draught_table.csv`), 3 freight statistics (see literature
D1-D8; CCNR market observation ch. 2 gives the cross-sections Emmerich 117.9 Mt
and Iffezheim 16.0 Mt for 2023, Traditional Rhine 146.1 Mt, entire Rhine
276.5 Mt, Rhine delta 227.2 Mt - used in `scenarios/rhine_capacities.csv`),
4 production indices, 5 price indices, 6 network geometry, 7 scenario precedents.
