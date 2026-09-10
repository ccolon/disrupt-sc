# Kaub gauge: official outlook and navigation status as of 10 September 2026

Compiled 10 Sep 2026, ~09:30 CEST, from web sources. Observed: PEGELONLINE Kaub 22 cm at 09:00 CEST
(15-min values 22–26 cm between 06:30 and 09:00; 69 cm on 29 Aug), ELWIS 24 cm at 05:00 (trend −2 cm).
Reference values listed by ELWIS: GlW 77 cm, MNW 65 cm, MW 208 cm (NNW still shown as 25 cm of 22.10.2018;
the mid-August 2026 single-digit values, 6–8 cm reported around 14 Aug, are not yet in the statistic).
Rhine at Basel (BAFU station 2289): 457 m³/s at 09:00, 24-h mean 456 m³/s, vs. September mean 975 m³/s (1991–2025).

## 1. Forecasts found

**a. WSV/BfG deterministic 4-day forecast (ELWIS)** — "Vorhersagen und Abschätzungen vom: 10.09.2026 um 07:00 Uhr".
Kaub: 22–23 cm for the rest of 10 Sep; 24–26 cm on 11 Sep; 26–28 cm on 12 Sep; 26–28 cm on 13 Sep;
26–27 cm on 14 Sep (days 3–4 are "Abschätzungen"). No rise above ~28 cm within the horizon.
URL: https://www.elwis.de/DE/dynamisch/Wasserstaende/Pegelvorhersage:KAUB
(Contargo's customer notice of 9 Sep, quoting the previous ELWIS issue, had Kaub "falling to 15–21 cm" on 10–12 Sep,
so the deterministic forecast was revised slightly upward on 10 Sep, but still flat.)

**b. BfG probabilistic 14-day forecast** — "Vorhersage vom: 09.09.2026 00:00 MEZ" (daily means, ECMWF-ENS + ICON).
Quantiles 5 / 25 / 50 / 75 / 95 %, cm:
10 Sep 19/20/21/23/24 · 11 Sep 25/28/30/32/35 · 12 Sep 35/40/43/47/52 · 13 Sep 41/47/52/57/64 · 14 Sep 42/49/54/60/68 ·
15 Sep 38/45/51/57/66 · 16 Sep 32/39/45/51/59 · 17 Sep 27/34/39/44/52 · 18 Sep 22/29/34/39/47 · 19 Sep 18/26/32/38/47 ·
20 Sep 14/24/31/39/51 · 21 Sep 11/21/29/38/52 · 22 Sep 10/21/29/38/53.
Probability of staying below GlW 77 cm: 100 % on every day 9–22 Sep (also 100 % for 97, 117, 137, 157 cm).
URLs: https://vorhersage.bafg.de/14-Tage-Vorhersage/Kaub_14Tage.pdf ; .../Kaub_Quantile_25700100.csv
Caveat: the median hump to 43–54 cm on 12–15 Sep is not supported by the newer 10 Sep 4-day forecast (26–28 cm),
i.e. the ensemble rain of the 9 Sep run appears to have been downgraded. The PDF itself states that the ELWIS
4-day forecast "ist außerhalb von Hochwasser aktuell die beste Wasserstandsabschätzung für die nächsten Tage".
The 10 Sep issue of the 14-day forecast was not yet online at 09:30 CEST.

**c. BfG hydrological 6-week forecast** — "Vorhersage vom: 07.09.2026" (weekly means; ECMWF ENS sub-seasonal, 101 members).
ENS quantiles 5 / 25 / 50 / 75 / 95 %, cm; ESP = climatology-driven median; OBS = observed 1991–2020 median:
| Week | ENS 5/25/50/75/95 | ESP 50 | OBS 50 | P(lowest class) |
|---|---|---|---|---|
| 07–13 Sep | 10 / 13 / 16 / 19 / 23 | 17 | 170 | 100 % (<128 cm) |
| 14–20 Sep | −3 / 6 / 12 / 19 / 30 | 26 | 167 | 90 % (<115 cm) |
| 21–27 Sep | −15 / 5 / 22 / 43 / 77 | 47 | 166 | 80 % (<107 cm) |
| 28 Sep–04 Oct | −16 / 12 / 42 / 78 / 137 | 63 | 166 | 72 % (<105 cm) |
| 05–11 Oct | −12 / 19 / 49 / 85 / 144 | 110 | 162 | 73 % (<107 cm) |
| 12–18 Oct | 5 / 38 / 68 / 102 / 157 | 107 | 165 | 76 % (<111 cm) |
URLs: https://vorhersage.bafg.de/6-Wochen-Vorhersage/Rhein-Kaub_6Wochen_Wasserstand.pdf ;
…/Rhein-Kaub_6Wochen_Wasserstand_QuansBox.csv ; …/Rhein-Kaub_6Wochen_Wasserstand_Pie.csv (copies of 10 Sep in
`scenarios/bfg_6week_kaub_20260907.csv`, `…_classes.csv`; the 14-day quantiles in `scenarios/bfg_14day_kaub_20260909.csv`) ;
https://6wochenvorhersage.bafg.de/ . Issued twice weekly; a 10 Sep issue was not yet online.

**d. BfG Niedrigwasser-Update, 03.09.2026** ("Zum Ende des Sommers: Niedrigwasserlage verschärft sich", period 28.08–03.09).
Kaub held ~MNW 65 cm for about a week at end-August, then fell "von 61 auf 53 cm" in 24 h (7-Uhr values).
Outlook: "Im Süden und Südwesten ist hingegen zunächst kaum Regen in Sicht"; per 14-day and 6-week forecasts levels
"voraussichtlich über den Tiefstwerten aus dem August verbleiben"; levels may rise slightly later in September but
"im Wochenmittel voraussichtlich nicht vor Oktober das Niveau des Gleichwertigen Wasserstands (GlW) erreichen".
Also: "Mit Tiefständen wie im August ist zunächst aber nicht erneut zu rechnen." Previous issue (27 Aug) was titled
"Niedrigwasser: keine weitere Entspannung bis Mitte September absehbar".
URL: https://www.bafg.de/SharedDocs/Downloads/DE/bfg_niedrigwasserbericht/2026/260903_nw_bericht.pdf
(index: https://www.bafg.de/DE/5_Informiert/2_Publikationen/Niedrigwasserbericht/niedrigwasserbericht_node.html ;
the 10 Sep issue returned 404 at 09:30 CEST).

**Comparison with the scenario profile** (45 cm week of 7 Sep, 60 week of 14 Sep, 80 from 21 Sep, 100 from 28 Sep):
BfG ENS medians are 16 / 12 / 22 / 42 cm for the same weeks, and 49 / 68 cm for 5–11 and 12–18 Oct. Even the ENS 95th
percentile reaches only 77 cm in the week of 21–27 Sep. The profile's September recovery is not supported by any current forecast.

## 2. Navigation status and operator decisions (1–10 Sep 2026)

- dpa via Handelsblatt, 3 Sep 11:22: Kaub 73 cm at start of week, 59 cm on Wednesday; BfG/WSV expect "unter 40 Zentimetern"
  by early next week. BDB deputy director Fabian Spieß: "Zwischen St. Goar und Mainz könnten Schiffe nach wie vor nur
  teilbeladen passieren"; most ships need ~150 cm at Kaub to load fully.
  https://www.handelsblatt.com/politik/deutschland/niedrigwasser-wasserpegel-im-rhein-koennte-erneut-sinken/100251751.html
  (same text: https://wirtschaftsticker.com/2026/09/keine-entwarnung-sinkende-pegelstaende-erwartet/ )
- Binnenschifffahrt Online, 4 Sep (on the BfG update): shipping faces "anhaltend niedrige Wasserstände und damit verbundene
  Einschränkungen bei der Abladung". https://binnenschifffahrt-online.de/2026/09/featured/40172/bfg-meldet-erneute-verschaerfung-der-niedrigwasserlage-an-deutschen-wasserstrassen/
- Agency report (Reuters-style, republished by UkrAgroConsult 9 Sep): Kaub "around 34 cm" on 7 Sep (WSV), down ~50 cm in a week;
  barges continue with reduced loads; Rotterdam–Karlsruhe tanker freight €120–125/t vs ~€100/t a week earlier; some cargo
  shifted to rail and road; participants "do not expect the rainfall to allow river transport to quickly return to normal".
  https://ukragroconsult.com/en/news/renewed-low-water-levels-on-the-rhine-push-river-freight-costs-higher-again/
- S&P Global Platts data (seen only in search excerpts of Hellenic Shipping News; page returns 403): ARA→Basel €145/mt on
  2 Sep (€135 on 1 Sep; €276.67 on 14 Aug); Lower Rhine loadables up to 1,000 mt; Upper Rhine loadables "determined by company
  draft restriction, captain's experience and willingness of the barge company".
- Contargo customer notice, 9 Sep: Kaub 26 cm (LWS level 6), Köln 71 cm, Duisburg-Ruhrort 158 cm, Emmerich 8 cm;
  "we may be forced to implement extensive operational measures at short notice"; transport obligation ends at Kaub ≤80 cm;
  services to Upper Rhine, Middle Rhine and Rhine-Main may be temporarily suspended.
  https://www.contargo.net/en/business/business-news/detail-business/current-low-water-levels-important-information-for-our-customers-1/
- Contargo low-water page, 10 Sep: Kaub 24 cm, "rapidly falling water levels"; "Due to the extreme low-water situation,
  free-market agreements apply" (published bands stop at 80 cm). https://www.contargo.net/en/business/auxiliary-conditions/low-water
- Hapag-Lloyd: Central Europe congestion surcharge €50/TEU (DE, FR, AT, CH, CZ, SK, HU) or €50/container (BE, NL, LU) via
  Antwerp/Rotterdam from 1 Sep (non-FMC) and 20 Sep (FMC), citing "low water levels on the Rhine" (Container News, 22 Aug).
  https://container-news.com/hapag-lloyd-introduces-central-europe-congestion-surcharge/
- Standing rule (WSV, dpa explainer 11 Aug): no official navigation ban; "Für die sichere Beladung und Fahrt ist der
  Schiffsführer verantwortlich." https://logistik-heute.de/news/binnenschifffahrt-pegel-kaub-fahrverbot-was-zum-niedrigwasser-wichtig-ist-278329.html
- Vessels still passing Kaub: no 1–10 Sep tonnage figures found. Latest: late Aug (Reuters via portseurope) 700–800 t per vessel
  at higher levels; HGK CEO Steffen Bauer, 18 Aug, "Synthese 18" carrying 485 t at the then-extreme Kaub level
  (https://shippingtelegraph.com/shipping-finance-news/low-rhine-levels-prompt-hgk-to-call-for-e12-5b-shallow-water-inland-vessels/).

## 3. End-of-event expectations (rain outlook)

- BfG, 3 Sep: pronounced low water persists through September; weekly-mean GlW not before October (see 1d). The 31 Aug
  6-week run expected less rain than typical in forecast weeks 2, 5 and 6.
- DWD 10-Tage-Vorhersage, issued Wed 09.09.2026 13:28 (covers 12–19 Sep): Sat 12 Sep "am meisten Sonnenschein im Südwesten
  und Süden"; Sun 13 Sep "im Süden häufig locker bewölkt und trocken"; Mon 14 Sep "meist niederschlagsfrei", up to 28 °C on the
  Upper Rhine; Tue 15 Sep south mostly lightly clouded; Wed 16 Sep south "ebenfalls bewölkt mit Regen", mainly near the Alps;
  Thu–Sat 17–19 Sep south "geringere Niederschlagsneigung und mehr Sonnenanteile", north "leicht unbeständig mit zeitweiligem Regen".
  https://www.dwd.de/DE/wetter/vorhersage_aktuell/10-tage/10tage_node.html
- DWD Wochenvorhersage Wettergefahren, 10.09.2026 05 UTC: "Überwiegend ruhiges Wetter ohne markante Wetterentwicklungen";
  weekend "voraussichtlich keine markanten Wetterereignisse". https://www.dwd.de/DE/wetter/warnungen_aktuell/wochenvorhersage/wochenvorhersage_node.html
- Net: no soaking rain over the Upper Rhine/Neckar/Main catchments in the 10-day window; only a possible Alpine-fringe rain
  event around 16 Sep. Nothing in the official outlooks points to a return above GlW before October.
- Alpine contribution (BAFU, Stand 8 Sep): Rhine at Basel almost continuously below the 1991–2020 seasonal minima since mid-June;
  glacier-fed tributaries (e.g. Massa at Blatten) often above seasonal reference because heat boosted melt; Bodensee at
  extremely low levels for the season at end-August. https://www.bafu.admin.ch/de/sommer-2026-trockenheit-und-hohe-wassertemperaturen
- Non-official weather commentary: leinetal24/echo24, 9 Sep 07:43 (Kaub 29 cm, Worms 7 cm): "Ein flächendeckender Landregen ...
  ist bis weit in den späten September nirgends in Sicht". daswetter.com, 6 Aug (ECMWF/NOAA monthly): September 1–2 °C too warm,
  "keine Hinweise auf Entspannung der Dürrelage".

## 4. What could not be found

- 10 Sep issues of the BfG 14-day forecast, 6-week forecast and Niedrigwasser-Update (not yet published at 09:30 CEST); re-check
  the three URLs above later today.
- ELWIS "10-Tage-Vorhersage" / "Trendvorhersage" pages: no longer exist under those names; ELWIS now links only the 4-day,
  BfG 14-day and BfG 6-week products (old paths return 404). BfG "Aktuelles"/undine "aktuell" pages also 404.
- CCNR/ZKR: no press release since 18 Jun 2026. No WSA Rhein notice on fairway depth for 1–10 Sep found.
- Original Reuters and Bloomberg items of 7–9 Sep (reuters.com not searchable; Bloomberg paywalled); SWR, FAZ, Rheinische Post,
  tagesschau blocked for the search tool; Platts and Loadstar pages 403; Handelsblatt beyond the 3 Sep dpa item.
- Dated 1–10 Sep statements from BASF, Covestro, Evonik, thyssenkrupp or HGK: none found; latest are August (BASF throttled
  some Ludwigshafen units, Covestro Dormagen constraints, thyssenkrupp suspended own barge fleet 15 Jul and trimmed blast-furnace output).
- Quantitative ECMWF/DWD precipitation totals for the Swiss/Alpine Rhine catchment; MeteoSwiss not checked. The BfG 6-week
  product (ECMWF sub-seasonal based) is the best available proxy for the catchment rain outlook.
