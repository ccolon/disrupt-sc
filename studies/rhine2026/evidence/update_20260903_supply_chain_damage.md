# Update 3 September 2026 — supply-chain disruption and damage evaluations of the 2026 Rhine low water

Sweep of 3 Sep 2026 for evidence not captured in `evidence_rhine2026_timeline.md`
(compiled 2 Sep): firm surveys, damage estimates, official indicators. Tags as in
that file ([C] confirmed/official, [R] press or single source, [F] forecast/estimate).
Nothing ex post exists yet: Destatis production (July) is due about 8 Sep, inland-shipping
volumes for July mid/late Sep, company Q3 figures late Oct.

## 1. Firm surveys — the only broad-based micro evidence so far

| Source | Sample / date | Finding |
|---|---|---|
| **DIHK / IHK nationwide survey** [C] (published 6 Aug 2026: nrwz.de, Schwarzwälder Bote; Rundschau Duisburg 8 Aug; dpa/onvista 31 Jul) | 170 logistics and industrial firms along the Rhine corridor, 29 Jul–4 Aug 2026 (Kaub ≈ 20–30 cm) | three quarters affected, "rising tendency"; **78 %** report higher costs; **72 %** had to reorganise logistics; more than half saw logistics costs rise **≥ 25 %**, about a third **≥ 50 %**; **almost one in three firms already restricts production**, **6 % have stopped** production processes; **13 %** see their site's existence threatened; about a third plan to ship less via the Rhine in future, about a quarter will raise inventories. DIHK: barges carry up to 75 % less. Example: Badische Stahlwerke Kehl receives ≈ 60 % of raw materials and ships ≈ 50 % of products by river (≈ 200,000 t/month); Kehl port congested. |
| **IHK Rheinhessen survey** [R] (Wochenzeitung Verkehr, 1 Sep 2026) | Rheinhessen firms (Mainz/Worms), August 2026 | almost three quarters of firms suffer from the low water; many report transport cost increases **> 50 %**, peaks at doubled freight rates. |
| marktundmittelstand / Verkehrsrundschau (Aug) [R] | — | binding constraint on road substitution = ≈ 100,000 missing truck drivers and specialised tank/silo equipment, not truck numbers. |

## 2. Damage and macro evaluations (all ex ante, [F])

| Institution | Date | Estimate |
|---|---|---|
| IfW Kiel (S. Kooths) | 28 Jul | Q3 GDP −0.1 to −0.2 pp; value-added loss EUR 1–2 bn (restated by VCI 6 Aug, BVR 18 Aug) |
| IW Köln (Thilo Schaefer) | 4 Aug (t-online) | "about 0.4 % of growth affected" if the shipping stoppage lasts, by analogy with IW's 2018 calculation; the press figure "almost EUR 18 bn" is 0.4 % × ≈ EUR 4.4 tn GDP, not an IW computation |
| Oxford Economics | quoted 1 Sep (Wochenzeitung Verkehr) | Q3 German growth −0.2 pp |
| Commerzbank (R. Solveen) | 11 Aug | −0.35 pp of Q3 GDP if critical levels persist to mid-September |
| BVR (A. Bley) | 18 Aug | 2026 GDP forecast RAISED 0.5 → 1.0 % (Q1–Q2 revisions, orders); the low water is a "brief growth pause" in Q3, "temporary"; 2027 unchanged at 1.3 % |
| Bundesbank Monthly Report | 20 Aug | Q3 "at best slight growth"; low water and transport costs "noticeably burden" industrial production and exports |
| VCI quarterly report (W. Große Entrup) | 3 Sep | 2026 chemical-pharma production −1.5 % (sales +2.5 % on prices); Q2 capacity utilisation 73.2 %; June already down in many segments; 20 Mt of chemical products moved by inland shipping in 2024; the low water is "pushing logistics and supply chains to their limits"; no separate Q3 low-water number yet |
| Moody's via Reuters (16 Aug) | context | Europe's **2025** heatwaves ≈ EUR 43 bn lost output, EUR 0.5 bn insured — no 2026 event figure; Swiss Re / Munich Re H1-2026 reviews predate the trough; Swiss Re (11 Aug): chemicals, metals, construction most at risk from the Rhine, effect inflationary |
| Allianz (cited by t-online) | context | EUR 112 bn water-scarcity cost to 2030 — structural study, not the event |

## 3. Official indicators available on 3 Sep

- Destatis **truck-toll mileage index** (Lkw-Maut-Fahrleistungsindex), July 2026: **+0.8 % m/m** (seasonally adjusted), **−0.5 % y/y** (press release 280/26) [C]. No visible modal-shift signal in July motorway truck-km; the August value (≈ 10 Sep) is the one to watch.
- Destatis production index July 2026: due ≈ 8 Sep. Inland-shipping monthly volumes for July: due mid/late Sep; August: Oct–Nov.
- duisport (harbour master D. Bours, 21 Aug): vessel loading ≈ one third of usual; 400–450 calls/week vs 280–300 [C].
- DB Cargo (14 Aug): ≈ 400 wagons mobilised ad hoc, up to 500 more later; "one freight train replaces up to ten barges" at low-water loads; up to ≈ 100 barges replaceable in total [C].
- BASF: first plants throttled (mid-Aug press), EBITDA guidance EUR 6.9–7.7 bn kept; the low-water cost will first be quantified with the Q3 results on **27 Oct 2026** [R].
- Construction (WiWo 17 Aug, HDB/VBU Hessen): sand and gravel "scarcer and more expensive", delivery times longer — no percentages.
- ABN AMRO's notes on the Dutch economy remained unreachable (timeouts, as on 2 Sep).

## 4. What this adds for the validation of the model

1. **Firm-level extensive margin**: ≈ 30 % of exposed firms cut production and 6 % stopped within
   4–5 weeks of Kaub falling below GlW (survey window 29 Jul–4 Aug) — a target for the share
   of Rhine-corridor firms producing below equilibrium at scenario weeks 5–6, and for the
   inventory-depletion timing.
2. **Cost pass-through**: logistics costs +25 % for half of the exposed firms, +50 % for a
   third; freight rates ×2–5 on the affected legs — targets for the distribution of delivered-
   price increases (link `price` vs `eq_price`).
3. **Adaptation**: a quarter of firms raise inventories, a third shift modes durably —
   qualitative support for adaptive inventories / supplier switching; the DB Cargo ceiling
   (≈ 100 barges) bounds rail substitution at roughly a tenth of Rhine capacity.
4. **Macro**: the ex ante range is −0.1 to −0.4 pp of German quarterly/annual GDP; the
   model's German value-added loss over the 15-week profile should land in that band
   (2018 ex post: −0.4 % GDP at the peak, −1.5 % industrial production in the worst month).
5. **Pending ex post anchors**: Destatis July/August production and inland-shipping volumes,
   truck-toll index August, BASF/Covestro/thyssenkrupp Q3 (late Oct), CCNR Q3 market insight,
   Kiel autumn forecast (≈ 10 Sep).

## Sources

- Wochenzeitung Verkehr, 1 Sep 2026 — https://www.verkehr.co.at/rhein-niedrigwasser-kostet-die-wirtschaft-milliarden/
- t-online, 4 Aug 2026 (IW Köln, Thilo Schaefer) — https://www.t-online.de/nachrichten/deutschland/innenpolitik/id_101373406/niedriger-rheinpegel-hitzewelle-kostet-deutschland-0-4-prozent-wachstum-.html
- nrwz.de, 6 Aug 2026 (DIHK survey) — https://www.nrwz.de/wirtschaft/historisches-niedrigwasser-auf-dem-rhein-trifft-die-wirtschaft-mit-voller-wucht-574863.html
- Schwarzwälder Bote, 6 Aug 2026 (IHK survey, Kehl) — https://www.schwarzwaelder-bote.de/lokales/ortenau/ihk-veroeffentlicht-umfrage-niedrigwasser-im-rhein-bremst-auch-ortenauer-wirtschaft-aus-79363901.html
- Rundschau Duisburg, 8 Aug 2026 — https://www.rundschauduisburg.de/2026/08/08/ihks-veroeffentlichen-umfrage-zu-niedrigwasser-auswirkungen
- dpa/onvista, 31 Jul 2026 (DIHK) — https://www.onvista.de/news/2026/07-31-dihk-niedrigwasser-bremst-guetertransport-auf-dem-rhein-massiv-aus-0-20-26538389
- verbandsbuero.de, 18 Aug 2026 (BVR) — https://www.verbandsbuero.de/bvr-bip-prognose-2026-niedrigwasser-rhein/
- it-boltwise, 6 Aug 2026 (VCI) — https://www.it-boltwise.de/niedrigwasser-im-rhein-vci-warnt-vor-produktionskuerzungen-und-milliardenkosten.html
- finanzen.at, 3 Sep 2026 (VCI quarterly report) — https://www.finanzen.at/nachrichten/aktien/vci-sieht-2026-preisbedingt-steigende-umsatze-aber-weiter-ruecklaufige-produktion-1036518421
- Destatis, truck-toll mileage index July 2026 — https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/08/PD26_280_421.html
- DB Cargo, 14 Aug 2026 — https://www.dbcargo.com/rail-de-de/logistik-news/niedrigwasser-db-cargo-zusaetzliche-kapazitaeten-13998510
- boerse-express, 15 Aug 2026 (BASF) — https://www.boerse-express.com/news/articles/basf-vor-dem-herbst-niedrigwasser-trifft-auf-angehobene-prognose-938794
- WiWo, 17 Aug 2026 (construction) — https://www.wiwo.de/unternehmen/industrie/niedrige-pegelstaende-hoehere-preise-und-engpaesse-niedrigwasser-trifft-bauherren/100247649.html
- ibtimes, 16 Aug 2026 (Moody's) — https://www.ibtimes.sg/43-billion-lost-heat-wave-just-500-million-insured-europes-climate-coverage-gap-widens-92278
- Insurance Journal, 11 Aug 2026 (Swiss Re) — https://www.insurancejournal.com/news/international/2026/08/11/881006.htm
- ING THINK, R. Luman, 3 Aug 2026 — https://think.ing.com/opinions/record-low-rhine-levels-another-warning-supply-chains-must-adapt/
- Logistik Heute (duisport) — https://logistik-heute.de/en/news/rhine-shipping-low-water-levels-increase-pressure-cargo-handling-port-duisburg-279982.html
