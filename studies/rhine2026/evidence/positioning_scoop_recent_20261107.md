# Positioning: scoop check and recency sweep, 2023 to 7 November 2026

Strand of the Nature Communications positioning work for "Logistics under drought: how the
Rhine low water of 2026 propagates through Europe's supply chains" (C. Colon, IIASA).
Compiled 7 November 2026 from WebSearch/WebFetch, Crossref records, arXiv/SSRN/EconStor
pages and institutional PDFs (text-extracted with pdftotext). Read first: `main.tex`
(Introduction, Discussion), `refs.bib` (22 Oct 2026 version), and the dossiers
`evidence_rhine2026_timeline.md`, `update_20260903_supply_chain_damage.md`,
`validation_targets_2026_surveys.md`, `kaub_september_2026_outlook.md`,
`evidence_rhine_literature.md`.

Conventions. Every item below carries a DOI or URL that was fetched (Crossref record, server
page, publisher page or PDF) unless marked UNVERIFIED. Tags in section 3: [C] official or
primary document fetched, [R] press or secondary source, [F] ex-ante forecast. Numbers are
quoted from the fetched documents; where a number comes from a search snippet only, it says so.

---

## 1. Overall scoop verdict and recommended novelty wording

### 1.1 Verdict by claim

**Claim A: first whole-EU (28-economy), firm-level, spatially explicit supply-chain model with
every shipment routed on the multimodal (road, rail, inland waterway, sea) network.**
Scoop risk: **LOW**. No published paper, preprint or report found (2023 to Nov 2026) that
combines (i) firm-level agents, (ii) continental or multi-country European coverage and
(iii) explicit routing on a transport network. The nearest neighbours, none of which does all
three, are:

- Prognos / R2K-Klim+ (2021 to 2026): Prognos freight-transport models coupled to the
  regional-economic model REGINA for 68 districts along the Rhine (15 regions): transport is
  explicit but the economy is regional-sectoral, not firm-level, and the scope is the corridor,
  not Europe (sections 2A, 3).
- Koks group (VU Amsterdam / PBL): MRIA regional input-output with "logistical constraints
  between regions" (Vanniya Perumal et al. 2025, arXiv) and with infrastructure-failure
  modules (Vanniya Perumal, Koks, de Ruiter, Thissen 2026, Civ. Eng. Env. Syst.): regional
  IO, Netherlands case, no routing of shipments.
- Verschuur, Koks and Hall (NC 2022, NCC 2023, CEE 2023) and Verschuur, Lumma and Hall
  (NC 2025): global port and chokepoint risk through a global transport-flow model at
  country-sector resolution, maritime only; Devetak, Verschuur and Klimek (arXiv June 2026):
  agent-based global shipping fleet, ports only, no production.
- Massoni (CEPREMAP Docweb 2602, July 2026): quantitative spatial production-network model
  with endogenous routing through maritime ports under tropical-cyclone risk; aggregate
  (country-port), trade-theory class, not firm-level, not Europe.
- CSH Vienna / Thurner group (Chakraborty et al. NC 2024; Stangl et al. Nat. Sustain. 2024;
  Tabachova et al. arXiv 2025; Fialkowski et al. arXiv 2026): national (Hungary, Ecuador) or
  global firm-level supply networks; no transport layer.
- PIK Acclimate (Quante et al. Nat. Sustain. 2024; Middelanis et al. ERL 2023): global
  agent-based, country-sector agents, transport as delays, no network routing.
- Bank of Canada (Papadopoulos, Ojea Ferreiro, Panzica, SWP 2026-30, Sept 2026): global
  firm-level agent-based flood stress test; inventories central; no transport network.
- Inoue and Todo (Nat. Sustain. 2019; RIETI DPs to 2024): Japan, ~1 m firms, no transport.
  Nothing from this group 2024 to 2026 on transport-network disruption was found.
- JRC / EU freight models (TRIMODE, ETISplus): no 2024 to 2026 low-water or supply-chain
  study found; JRC's own 2026 output on the Rhine is the drought monitoring of 12 Aug 2026.

One caveat is internal, not external. The sentence "While that work covered a single country
and roads only, we extend the model, DisruptSC, to multiple countries, several transport modes
and cargo types" (Introduction) is accurate relative to Colon et al. 2021 but could read as
if multimodality and multi-country coverage are new to DisruptSC. The public record shows
otherwise: the Zenodo release "v2 - Cambodia" (12 Dec 2022, DOI 10.5281/zenodo.7427207)
describes "roads, railways, waterways, and maritime" networks, and the model's own
applications page lists Cambodia (road, rail, waterway, maritime), Ecuador, an eight-country
Central Asia and South Caucasus model (road, rail, maritime, pipelines) and a global version;
an SSRN working paper "Modeling Supply-Chain and Transport Resilience to Climate Risks:
Lessons from Four Regions" (Colon and Hallegatte, 2026; SSRN 7367518, page not fetched, 403)
is indexed. A referee who finds these will object to "first multimodal" or "first
multi-country". The defensible novelty is **scale and completeness**: first continental
economy (EU-27 plus Switzerland) at firm resolution with full multimodal routing, and the
first such model calibrated on a documented historical event and run as a forecast.

**Claim B: first model-based estimate of the 2026 event.**
Scoop risk for that literal phrase: **MEDIUM to HIGH**. Two model-based estimates were
published during the event, before this manuscript:

1. Prognos for Handelsblatt (page "Stand 06.08.2026"): a scenario run of the R2K-Klim+ models
   (freight models + REGINA) on observed Kaub and Duisburg-Ruhrort levels to 30 July, the
   six-week outlook and a statistical extrapolation to 31 October 2026: production-value loss
   EUR 912.8 million along the Rhine, about 1,900 jobs, chemicals EUR 425 million, refining
   EUR 206 million, Mannheim-Ludwigshafen EUR 494 million of production value and
   EUR 107 million of value added. Grey literature (consultancy page, paywalled newspaper),
   but a model-based estimate of 2026 by any reading.
2. Kiel Institute: the autumn report (Kieler Konjunkturberichte 137, 3 Sept 2026, box) and
   Jannsen and Meuchelboeck (Wirtschaftsdienst 106(9), 705-706, print 1 Sept, online
   11 Oct 2026) apply the 2023 econometric elasticity (0.04 % of producing-sector output per
   low-water day) to the 2026 calendar: producing-sector output -1.2 % in Q3 2026 under a
   scenario ending in late September (GDP -0.3 % ceteris paribus; -0.2 % adopted), or -1 % in
   both Q3 and Q4 under a 2018-type autumn. Statistical, not a propagation model, but
   "model-based" in a referee's vocabulary.

The claim survives if it is narrowed to what is true: the first estimate of the 2026 event
from a **supply-chain propagation model** (shortage mechanism, firm resolution, services
included), and the first **forecast published before the statistics with a documented
forecast evaluation**. Both are supported by the sweep: nothing else of that kind was found
(arXiv, SSRN, EconStor, ResearchSquare, Kiel, Bundesbank, ECB, DIW, ifo, IW, ZEW, RWI, CPB,
CEPII, Banque de France, DNB, OECD/ITF, JRC, EEA, CCNR, Coface, ING, ABN AMRO).

**Three findings that bear on the Introduction regardless of novelty.**

- Kotz, Levermann and Wenz (2024), "The economic commitment of climate change", Nature 628,
  551-557, was **retracted on 3 December 2025** (Crossref record now reads "RETRACTED
  ARTICLE"; retraction note PMC12711553). Do not cite it; the DOSE data paper (Wenz et al.
  2023) and the authors' announced resubmission are not substitutes for the headline number.
- The Kiel authors have revised their own 2018 narrative (Jannsen and Meuchelboeck 2026):
  production dampened by 0.7 % in Q3 2018 and 1 % in Q4 2018, GDP by 0.2 % and 0.3 %
  respectively, about 0.1 % over the year 2018; 30 low-water days cost 1.2 % of
  producing-sector output and 1.5 % per month from the second month. The Introduction's
  "GDP about 0.3-0.4 % below its path at the trough" should become "0.2-0.3 % in the quarters
  of the event" with this citation (the 0.4 % circulating in the press is IW's reading of an
  older Kiel statement).
- Meuchelboeck (RETHINK-GSC Working Paper 08/2025, Aug 2025) is the first firm-level evidence
  that the 2018 low water propagated along supply chains: German firms importing by inland
  waterway reduced the value, variety and geographic scope of their exports, the effect was
  strongest for firms without transport diversification, cannot be explained by demand
  shocks, and firms switched modes persistently. Inland-waterway exports fell by nearly
  20 % and imports by 12 % in 2018. This supports messages (1) and (3) of the paper and must
  be engaged with; it also documents the persistent modal shift that the model does not
  represent (a limitation to state).

### 1.2 Recommended wording of the novelty claim

Introduction (replace the two sentences on the extension of DisruptSC):

> "Supply-chain models of disasters [...]. Our earlier work coupled such a model to a
> country's road network [colon2021]; the model, DisruptSC, has since been applied to
> national and regional multimodal networks. Here we build it for a whole continental
> economy: the EU-27 and Switzerland at the resolution of individual firms, with every
> shipment routed by cargo type on the European road, rail, inland-waterway and sea network.
> To our knowledge no supply-chain model of this scope exists: firm-level models of
> production networks are national or have no transport layer [inoue2019, diem2022,
> chakraborty2024], transport-coupled models of disasters are national or regional
> [colon2021, vanniyaperumal2026], and global models of ports and chokepoints resolve
> countries and sectors rather than firms [verschuur2022, verschuur2023ncc, verschuur2025]."

Introduction or Results (the 2026 estimate):

> "During the event, the estimates available were extrapolations of the 2018 elasticity of
> industrial production to low-water days [jannsen2026, kiel2026autumn, gd2026autumn] and a
> regional freight-economy model of the corridor [prognos2026]. We provide the first estimate
> from a model of supply-chain propagation, published as a forecast before the autumn
> statistics and evaluated against them (Supplementary Section S3)."

Avoid: "first model-based estimate", "first multimodal", "first multi-country". Keep "to our
knowledge" and name the nearest neighbours in the same sentence; this is what survives a
referee who knows one of them.

---

## 2. Table of items

Verdict legend: scoop risk high / medium / low / none (with reason), or "citable context".
"Verified" means the DOI/URL in the row was fetched (Crossref, server page or PDF).

### 2A. Economics of Rhine low water and European inland-waterway disruption, 2023-2026

| # | Authors, date | Title | Venue / server | DOI / URL (verified) | What it does | Key numbers | Verdict |
|---|---|---|---|---|---|---|---|
| A1 | Jannsen, N.; Meuchelboeck, S., Sept 2026 (print 1 Sep, online 11 Oct) | Konjunkturschlaglicht: Wie stark belastet Niedrigwasser die Wirtschaft? | Wirtschaftsdienst 106(9), 705-706 | 10.2478/wd-2026-0170 (Crossref + journal page) | Restates the Kiel econometric elasticity and applies it to 2026 in two calendar scenarios; argues low capacity utilisation dampens, record-low levels amplify | 0.04 %/low-water day; 30 days -1.2 % producing sector, -1.5 %/month from 2nd month; GDP up to -0.5 % in pronounced phases; 2018: production -0.7 % Q3, -1 % Q4, GDP -0.2 %/-0.3 %, year -0.1 %; 2026 scenario I: -1.2 % Q3 then recovery; scenario II: -1 % in Q3 and Q4 | Scoop risk **medium** for "first model-based estimate of 2026" (statistical, not propagation); must be cited; corrects the 2018 numbers in the Introduction |
| A2 | Meuchelboeck, S., Aug 2025 | Navigating Supply Chain Disruptions: How Firms Respond to Low Water Levels | RETHINK-GSC Working Paper 08/2025 (Kiel Institute / Aarhus) | https://www.kielinstitut.de/publications/navigating-supply-chain-disruptions-how-firms-respond-to-low-water-levels-18291/ ; PDF https://rethink-gsc.eu/wp-content/uploads/2025/08/WP_Navigating_Supply_Chain_Dispruptions.pdf (fetched) | Natural experiment on 2018 with monthly German firm-level trade x transport-mode data; event studies of exports of firms importing by inland waterway | IWW exports -~20 %, imports -12 % in 2018; 2,124 firms (1.2 %) import by IWW, 1,324 exporters (0.9 %); exports of dependent firms fell in value, variety, destinations; persistent mode switching | Scoop risk **low** (empirical, 2018, no model) but **essential context**: first firm-level evidence of supply-chain transmission of a Rhine low water; supports messages 1 and 3; documents persistent modal shift the model omits |
| A3 | Boysen-Hogrefe, J.; Groll, D.; Hoffmann, T.; Jannsen, N.; Kooths, S.; Krohn, J.; Mentzer, F., 3 Sept 2026 | Deutsche Wirtschaft im Herbst 2026 (box: Das Niedrigwasser im Rhein wird die Wirtschaftsleistung nur kurzfristig belasten) | Kieler Konjunkturberichte Nr. 137 (2026/Q3) | https://www.kielinstitut.de/fileadmin/Dateiverwaltung/IfW-Publications/fis-import/ac88308d-f129-4265-8c0f-337675fbe3e5-KKB_137_2026-Q3_Deutschland_DE_.pdf (fetched) | Applies the elasticity to a low water assumed to end around end-September | Producing sector -1.2 % in Q3 -> GDP -0.3 % ceteris paribus; adopted -0.2 % of GDP in Q3; no large catch-up expected; firms have made logistics more robust since 2018 | Citable context; the institutional ex-ante anchor for the manuscript's forecast comparison |
| A4 | Projektgruppe Gemeinschaftsdiagnose (DIW, ifo, IfW, IWH, RWI), Sept 2026 | Gemeinschaftsdiagnose Herbst 2026: Aufschwung mit Strukturproblemen - Finanzpolitik auf Abwegen | gemeinschaftsdiagnose.de | https://gemeinschaftsdiagnose.de/wp-content/uploads/2026/09/GD26H_v2_mitSperrfrist.pdf (fetched) | Joint autumn forecast with low-water passages | Q3 2026 GDP +0.1 % q/q; manufacturing value added slightly down in Q3; "30 Niedrigwassertage in einem Monat" -> producing sector -0.7 % to -1.2 % (citing Ademmer et al.); July production -1.1 % m/m; exports -0.2 % and imports -0.3 % in Q3 "belastend ... Niedrigwasser" | Citable context (ex-ante institutional estimate; chemicals named) |
| A5 | Prognos AG (Sander, L.; Norpoth, R.) for Handelsblatt, page dated 6 Aug 2026 | Niedrigwasser am Rhein: Wirtschaftliche Schaeden von ueber 900 Millionen Euro moeglich | prognos.com (project R2K-Klim+, BMFTR/RegIKlim) | https://www.prognos.com/de/wirtschaftliche-schaeden-niedrigwasser-rhein (fetched) | Scenario run of the R2K-Klim+ freight + REGINA regional models for 68 districts/15 regions on Kaub and Duisburg-Ruhrort levels (observed to 30 Jul, 6-week forecast, extrapolation to 31 Oct 2026) | Production value -EUR 912.8 m; ~1,900 jobs; chemicals EUR 425 m; refining EUR 206 m; Mannheim-Ludwigshafen EUR 494 m production value, EUR 107 m value added | Scoop risk **medium-high** for the literal "first model-based estimate of 2026"; **low** for the paper's actual contribution (regional-sectoral, corridor only, grey) |
| A6 | Prognos AG / R2K-Klim+ consortium (FiW RWTH Aachen lead), phase 1 results 2023, project page dated 4 Jan 2023; FONA interview 16 Jul 2026 | Niedrigwasser im Rhein: Die Folgen des Klimawandels (project); R2K-Klim+ | prognos.com; fona.de; r2k-klim.net | https://www.prognos.com/de/projekt/niedrigwasser-im-rhein-die-folgen-des-klimawandels ; https://www.fona.de/de/aktuelles/nachrichten/2026/07/260726_BO_RegIKlim_Interv_Niedrigwasser.php ; https://r2k-klim.net/ (all fetched) | Freight models + REGINA; climate-scenario water levels from a partner; adaptation measures costed; decision-support tool KLAUS | Extreme low-water year: up to 10.2 Mt of barge deliveries lost, production value -EUR 3.4 bn, ~8,000 jobs; moderate year 3.8 Mt; Q4 2018 industrial loss ~EUR 2 bn (ZKR/IfW/Destatis) | Citable context; the only other transport-coupled economic model of the Rhine; no peer-reviewed paper found (a 2021 Internationales Verkehrswesen article, DOI 10.24053/IV-2021-0078, is listed by the publisher but its Crossref record could not be retrieved: UNVERIFIED) |
| A7 | ABN AMRO Group Economics (Jansen, D. et al.), date not retrievable (c. 2023) | Ripple effects - Exploring the impact of low Rhine water levels on the Dutch economy | abnamro.com research | https://www.abnamro.com/research/en/our-research/ripple-effects-exploring-the-impact-of-low-rhine-water-levels-on-the-dutch (page returned 503 on three attempts; content from search excerpts) UNVERIFIED | Regressions of Dutch freight and sectoral output on Kaub low-water days | +1 low-water day -> -0.5 % of tonnage; 30 days -> -24 % over two months; no significant effect on Dutch industrial output or construction | Citable context for message 3 (loss outside the corridor is small in NL on the Dutch side), once the note is fetched and dated |
| A8 | Deidda, C.; Khanna, A. A.; Schade, W.; Smith, C.; Thiery, W., 22 Jul 2026 | Europe's transport infrastructure is not ready to face climate change | Nat. Hazards Earth Syst. Sci. 26(7), 3345-3394 | 10.5194/nhess-26-3345-2026 (journal page) | Review of observed impacts and multi-hazard exposure projections for EU roads, rail, inland waterways, ports, airports under three scenarios; exposure only | 2018 Rhine drought EUR 2.4 bn losses in Germany (abstract; EUR 2.7 bn DE+NL in text); heatwave/drought exposure spreading to >70 % of the network | Citable context (EU-wide transport exposure; no economic model) |
| A9 | Vanniya Perumal, S. R.; Koks, E. E.; de Ruiter, M.; Thissen, M., 1 Jul 2026 | Critical Infrastructure failure escalates the macroeconomic impacts of disasters | Civil Engineering and Environmental Systems, 1-25 | 10.1080/10286608.2026.2664413 (Crossref; PBL summary) | MRIA regional IO + localised infrastructure failure, Zuid-Holland case | Including infrastructure failure raises losses by ~50 % | Citable context (Koks group, nearest regional-IO neighbour; no routing) |
| A10 | Vanniya Perumal, S. R.; Thissen, M.; de Ruiter, M.; Koks, E. E., 1 Aug 2025 | Assessing the Macroeconomic Impacts of Disasters: an Updated Multi-Regional Impact Assessment (MRIA) model | arXiv 2508.00510 (econ.GN) | https://arxiv.org/abs/2508.00510 (fetched) | Updated MRIA with post-disaster trade and logistical constraints between regions; sectoral criticality | None in abstract | Citable context |
| A11 | Campoverde, A. L.; Ehret, U.; Ludwig, P.; Pinto, J. G., 2 Oct 2025 | Drought propagation in the Rhine River basin and its impact on navigation using LAERTES-EU regional climate model dataset | EGUsphere preprint | 10.5194/egusphere-2025-3988 (Crossref) | Meteorological-to-hydrological drought propagation and navigation thresholds (large ensemble) | n/a (hydrology) | Citable context (hazard side) |
| A12 | Jansen op de Haar, M.; Frutos Rodriguez, D., 11 Jun 2026 | Digital Twin-Based Simulation for Predictive Decision-Making in Waterway Logistics | arXiv 2606.13492 (cs.CY), submitted to IEEE Digital Twin 2026 | https://arxiv.org/abs/2606.13492 (fetched) | Time-sliced simulation of freight routing on inland waterways under water-level uncertainty; predictive vs reactive | Fuel-related costs -28.3 % on average; benefits at 70-100 % forecast accuracy | Scoop risk none (operations, no economy) |
| A13 | Duldner-Borca, B.; Putz-Egger, L.-M.; van Hassel, E., 31 Jul 2025 | A modelling approach to calculate economic and social benefits of resolving nautical bottlenecks on inland waterways | European Transport Research Review 17, 39 | 10.1186/s12544-025-00734-9 (Crossref) | KPI-based monetisation of Danube fairway maintenance (2.5 m) | n/a | Citable context (Danube) |
| A14 | Chen, Z.; Rose, A.; Roberts, F.; Tucci, A., Jul/Oct 2025 | Regional supply-chain impacts of Mississippi River fertilizer shipments disrupted by climate change | Risk Analysis 45(10), 3090-3109 | 10.1111/risa.70064 (Crossref) | Empirical barge-rate analysis + CGE (TERM-USA) of low water, lock damage, import disruption | GDP down, inflation up, largest in five Upper Mississippi states | Citable context (US inland-waterway precedent, CGE class) |
| A15 | Jung, P. H.; Kim, K.; Jo, A.-H.; Cho, J. S.-H., Nov 2025 | Panama Canal Drought and Supply Chain Disruptions in Asia-US Trade | ADB Economics Working Paper (WPS250475-2) | 10.22617/WPS250475-2 (ADB page) | Micro shipment and AIS data on the 2022-23 canal drought | Significant delays; largest for metals and light manufactures; none for food | Citable context (drought-driven waterway disruption, maritime) |
| A16 | Barata da Rocha, M.; Grabbe, H.; Poitiers, N., 19 Sep 2025 | Climate risks to global supply chains | Bruegel Working Paper 20/2025 | https://www.bruegel.org/working-paper/climate-risks-global-supply-chains (fetched) | Policy review of three channels (manufacturing, agriculture, infrastructure/trade routes); cites Meuchelboeck 2025 and Ademmer 2020 on the Rhine | Past shocks "measurable but short-lived" | Citable context (the dossier's "Rhine 2018/2022 as case" overstates it: the Rhine appears only via citations) |
| A17 | Science Media Center Germany, 15 Jul 2026 | Niedrige Wasserstaende: Herausforderungen fuer Schifffahrt und Wirtschaft (statements Meuchelboeck, Nilson, Lehmann, Borchardt) | sciencemediacenter.de | https://sciencemediacenter.de/angebote/niedrige-wasserstaende-herausforderungen-fuer-schifffahrt-und-wirtschaft-26168 (in dossier E6) | Expert statements | 2018 IWW exports -~20 %, imports -12 % | Already in dossier; citable |
| A18 | schym.de (independent blog), 22 Aug 2026 | The Rhine Is Low. The Output Effect Is Still Missing. | blog | https://www.schym.de/blog/rhine-low-water-industrial-output | Sector-panel regression of German output on Kaub levels 2010-2026; finds no reliable national penalty | ~0 interaction, wide interval | Not citable (grey, unreviewed); note that it exists |

### 2B. Europe-wide or multi-country spatial supply-chain and production-network models with transport, 2023-2026, and nearest neighbours

| # | Authors, date | Title | Venue / server | DOI / URL (verified) | What it does | Key numbers | Verdict |
|---|---|---|---|---|---|---|---|
| B1 | Verschuur, J.; Lumma, J.; Hall, J. W., 24 Nov 2025 | Systemic impacts of disruptions at maritime chokepoints | Nature Communications 16, 10421 | 10.1038/s41467-025-65403-w (Crossref) | Global transport-flow and trade model of chokepoint closures (Suez, Bab el-Mandeb, Taiwan Strait, ...) | USD 192 bn/yr trade exposed; USD 10.7 bn/yr losses + USD 3.4 bn freight costs | Scoop risk **low** (maritime, country-sector); cite as the venue's own transport-disruption paper |
| B2 | Verschuur, J.; Koks, E. E.; Hall, J. W., 20 Jul 2023 | Systemic risks from climate-related disruptions at ports | Nature Climate Change 13, 804-806 | 10.1038/s41558-023-01754-w (Crossref) | Climate downtime at 1,320 ports x global transport-flow model | USD 81 bn trade and >= USD 122 bn activity at risk per year | Citable context |
| B3 | Verschuur, J.; Koks, E. E.; Hall, J. W., 27 Jul 2022 | Ports' criticality in international trade and global supply-chains | Nature Communications 13, 4351 | 10.1038/s41467-022-32070-0 (Crossref) | Port-level criticality via global maritime flows and MRIO | 40 ports add >10 % of domestic output of their economies (snippet) | Citable context |
| B4 | Verschuur, J.; Koks, E. E.; Li, S.; Hall, J. W., 12 Jan 2023 | Multi-hazard risk to global port infrastructure and resulting trade and logistics losses | Communications Earth & Environment 4, 5 | 10.1038/s43247-022-00656-7 (Crossref) | Multi-hazard port risk with trade/logistics losses | n/a here | Citable context |
| B5 | Devetak, M.; Verschuur, J.; Klimek, P., 11 Jun 2026 | Adaptive rerouting reshapes impacts of maritime chokepoint disruptions | arXiv 2606.13431 (physics.soc-ph) | https://arxiv.org/abs/2606.13431 (fetched) | Empirically calibrated agent-based model of the global commercial fleet (35,954 ships, 1,651 ports); rerouting dynamics | Each closure day -3.0 % global arrivals (Suez), -7.7 % (Suez+Panama+Malacca) | Scoop risk **low** (ports, no production); relevant method precedent for "route switching under uncertainty" and known vs unknown duration |
| B6 | Massoni, H., Jul 2026 | Climate Trade Costs: Extreme Weather, Transportation, and Supply Chains (RIEF Best Paper Prize 2026) | CEPREMAP Docweb 2602 (Univ. Bologna) | https://www.cepremap.fr/depot/docweb/docweb2602.pdf (fetched) | Quantitative spatial production-network model with endogenous routing; port congestion and cyclone risk; firm-to-firm shipment data | Port disruption 1-2 weeks; rerouting 1-4 months; welfare effects mainly distributional | Scoop risk **low**; the closest trade-theory analogue to "routing inside a production network"; cite |
| B7 | Papadopoulos, G.; Ojea Ferreiro, J.; Panzica, R., Sept 2026 | Climate stress test of the global supply chain network: the case of river floods | Bank of Canada Staff Working Paper 2026-30 (SUERF Policy Brief 1143, Apr 2025) | 10.34989/swp-2026-30 (BoC page) | Data-driven agent-based model on global firm-level trade links x flood hazard maps | Lean inventories spread shocks faster and raise losses; link criticality as early warning | Scoop risk **low** (no transport); strong support for message 1 (inventories) |
| B8 | Chakraborty, A.; Reisch, T.; Diem, C.; Astudillo-Estevez, P.; Thurner, S., 18 Apr 2024 | Inequality in economic shock exposures across the global firm-level supply network | Nature Communications 15, 3348 | 10.1038/s41467-024-46126-w (Crossref) | Global firm-level network; country exposure to firm failures abroad | Rich countries expose poor ones more than vice versa | Citable context (venue, firm-level networks, no transport) |
| B9 | Stangl, J.; Borsos, A.; Diem, C.; Reisch, T.; Thurner, S., 15 Apr 2024 | Firm-level supply chains to minimize unemployment and economic losses in rapid decarbonization scenarios | Nature Sustainability 7, 581-589 | 10.1038/s41893-024-01321-x (Crossref) | Hungarian VAT-based firm network; shock propagation | n/a here | Citable context |
| B10 | Tabachova, Z.; Diem, C.; Stangl, J.; Borsos, A.; Thurner, S., 25 Feb 2025 | Combined climate stress testing of supply-chain networks and the financial system with nation-wide firm-level emission estimates | arXiv 2503.10644 | https://arxiv.org/abs/2503.10644 (fetched) | 1:1 ABM of all 410,523 Hungarian firms under carbon pricing | Cascades raise losses by 300-4000 % depending on substitutability | Citable context (substitutability is the pooling question) |
| B11 | Fialkowski, J.; Havlin, S.; Thurner, S., 22 Jul 2026 | Catastrophic disruption cascades driven by the nonlinearity of systemic risk | arXiv 2607.20068 | https://arxiv.org/abs/2607.20068 (fetched) | Ecuador firm-level network; joint failures | Amplification up to 257x; 0.14 % of pairs > 4x | Citable context |
| B12 | Quante, L.; Willner, S. N.; Otto, C.; Levermann, A., 13 Sep 2024 | Global economic impact of weather variability on the rich and the poor | Nature Sustainability 7, 1419-1428 | 10.1038/s41893-024-01430-7 (Crossref) | Acclimate (updated) with consumer quintiles; weather-driven production disruptions through supply chains | Middle-income countries most at risk | Citable context (Acclimate's latest) |
| B13 | Middelanis, R.; Willner, S. N.; Kuhla, K.; Quante, L.; Otto, C.; Levermann, A., 30 Aug 2023 | Stressed economies respond more strongly to climate extremes | Environmental Research Letters 18, 094034 | 10.1088/1748-9326/acec5e (Crossref) | Acclimate; state-dependence of ripple losses | n/a here | Citable context (relevant to the capacity-utilisation argument of A1) |
| B14 | Klimek, P.; Poledna, S.; Thurner, S., 11 Apr 2019 | Quantifying economic resilience from input-output susceptibility to improve predictions of economic growth and recovery | Nature Communications 10, 1677 | 10.1038/s41467-019-09357-w (Crossref) | IO susceptibility and resilience | n/a | Citable context (venue) |
| B15 | Pichler, A.; Diem, C.; Brintrup, A.; Lafond, F.; Magerman, G.; Buiten, G.; Choi, T. Y.; Carvalho, V. M.; Farmer, J. D.; Thurner, S., 20 Oct 2023 | Building an alliance to map global supply networks | Science 382, 270-272 | 10.1126/science.adi7521 (Crossref) | Perspective on firm-level supply-network data | n/a | Citable context (data gap the synthetic network fills) |
| B16 | Dao, D.; Jindal, A.; Shrimali, G., 26 Feb 2026 | Physical Climate Risks, Firm Defaults, and Supply Chain Network Propagation | Oxford Smith School working paper (SSRN) | https://www.smithschool.ox.ac.uk/sites/default/files/2026-03/physical-Climate-Risks-Firm-Defaults-and-Supply-Chain-Network-Propagation.pdf (fetched) | Indian firm-level data; default propagation | Power-sector chain ~1/3 of losses | Low relevance; not needed |
| B17 | Colon, C. (ccolon), 12 Dec 2022 | disrupt-supply-chain-model: v2 - Cambodia | Zenodo | 10.5281/zenodo.7427207 (fetched) | DisruptSC v2: roads, railways, waterways, maritime; admin-unit households | n/a | Own prior work: constrains the wording of the novelty claim (section 1.1) |
| B18 | Colon, C.; Hallegatte, S., 2026 | Modeling Supply-Chain and Transport Resilience to Climate Risks: Lessons from Four Regions | SSRN 7367518 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7367518 (403; title from listing) UNVERIFIED | Four DisruptSC applications (Tanzania, Cambodia, Ecuador, Middle Corridor) | Duration of disruption the main driver of losses (listing) | Own prior work; cite in the sentence that introduces DisruptSC |

Searched without result (2023 to Nov 2026): Inoue/Todo transport-network simulations; IIASA
supply-chain ABMs for Europe; Oxford INET production-network climate papers (Pichler, Lafond,
Farmer); JRC TRIMODE/ETISplus low-water studies; OECD/ITF, IMF, DNB, CPB, CEPII, Banque de
France, Bundesbank, ECB working papers coupling production networks and inland waterways;
Nature Communications 2025-2026 papers on inland waterways or river transport.

### 2C. Analyses of the 2026 event (summary; dates and numbers in section 3)

| # | Source, date | Type | URL (verified) | Key numbers | Verdict |
|---|---|---|---|---|---|
| C1 | Deutsche Bundesbank, Monatsbericht Oktober 2026, Kurzbericht Konjunkturlage, 21 Oct 2026 | [C] | https://publikationen.bundesbank.de/publikationen-de/berichte-studien/monatsberichte/monatsbericht-oktober-2026-1010626?article=kurzbericht-konjunkturlage-1010630 | Q3 GDP "duerfte ... stagniert haben"; "Insbesondere belasteten die niedrigen Pegelstaende am Rhein und die deswegen eingeschraenkte Binnenschifffahrt die Industrie"; energy-intensive branches hit; higher transport costs via modal shift; Rhine "auch im September durchgaengig sehr niedrig"; chemicals and coke/refining named (The Local, 22 Oct) | Citable; supports sector attribution of the model |
| C2 | Destatis PD 381, 30 Oct 2026 | [C] | https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/10/PD26_381_811.html | Q3 GDP +0.2 % q/q, +1.3 % y/y; exports "merklich" weaker; investment down; no mention of low water; details 25 Nov 2026 | Citable; the realised aggregate is above the stagnation expected |
| C3 | Destatis PD 389, 6 Nov 2026 | [C] | https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/11/PD26_389_421.html | Sept 2026 production +0.7 % m/m, +0.4 % y/y; industry +1.7 % m/m; energy-intensive +0.8 % m/m, -1.9 % y/y; construction -2.6 %; energy -1.2 %; Q3 vs Q2 -0.4 %; August revised +2.0 -> +1.0 % | Citable; the first ex-post test the Discussion announces |
| C4 | ECB, Elderson speech, 26 Oct 2026 (Yerevan); 19 Oct 2026 (Manila); Lagarde blog 4 Nov 2026 | [C] | https://www.ecb.europa.eu//press/key/date/2026/html/ecb.sp261026~d903d7ad85.en.html ; https://www.ecb.europa.eu//press/key/date/2026/html/ecb.sp261019~f0a3e053de.en.html ; https://www.ecb.europa.eu/press/blog/date/2026/html/ecb.blog20261104~78299c3eaf.en.html | Rhine "lowest since records began in 1880"; "could also reduce Germany's economic recovery by up to 0.2 percentage points of GDP in the third quarter"; ECB staff: summer weather "only a small and temporary effect on euro area activity"; German Rhine impact "expected to reverse once river flow normalises"; 1-in-100-yr drought exposes up to 24 % of euro-area output (Ceglar et al. 2025, OP 380) | Citable (the venue's macro conversation) |
| C5 | EEA Briefing 22/2026, 3 Nov 2026 | [C] | https://www.eea.europa.eu/en/analysis/publications/europes-critical-infrastructure-under-climate-stress-lessons-from-2026 ; doi 10.2800/2469788 | Rhine case study: Kaub <10 cm on 14 Aug; ~20 % loads (~250 t) late July; tanker Rotterdam-Karlsruhe EUR 45 -> 150-155/t (31 Jul); ARA-Basel EUR ~35 -> 277/t mid-Aug; 150 trucks per barge (construction); Covestro FM, Evonik Marl, RWZ <10 % of usual 50 kt, Salzgitter coal to rail; EU-wide GDP impact "at least around -1 %" (Triodos) | Citable; first EU-agency synthesis of 2026 |
| C6 | CCNR press releases 10 Sep 2026 and 29 Oct 2026 (Annual Report 2026) | [C] | https://www.ccr-zkr.org/files/documents/cpresse/cp20260910en.pdf ; https://www.ccr-zkr.org/files/documents/cpresse/cp20261029en.pdf | "navigation has never been interrupted"; preparedness "significantly higher than 2018"; Masterplan Rhine launched spring 2026; 2025 data: Rhine 281.9 Mt (-0.9 %), EU-27 458.4 Mt (-3.2 %), mineral oil -2.9 %, chemicals -2.0 %, iron ore -14.4 % | Citable (no 2026 volumes yet) |
| C7 | Kiel KKB 137 (A3); Jannsen and Meuchelboeck 2026 (A1); Gemeinschaftsdiagnose Herbst 2026 (A4) | [C][F] | see 2A | see 2A | Citable ex-ante anchors |
| C8 | Prognos for Handelsblatt, 6 Aug 2026 (A5) | [F] | see 2A | EUR 912.8 m production value | see 2A |
| C9 | Coface (Barre, E.), 1 Sep 2026 | [R] | https://www.coface.com/news-economy-and-insights/low-water-levels-on-the-rhine-and-danube-put-the-european-economy-under-pressure | Kaub 8 cm on 18 Aug; barges ~20 %; Rhine 60 % and Danube 12 % of EU IWW; 2018 GDP -0.3 to -0.4 pts; IWW 5.4 % of German freight, 19.2 % Romania; BASF Ludwigshafen ~40 % of freight by barge; German chemical output -20 % since 2018 | Citable context |
| C10 | Bloomberg (Brendel, E.; Martin, M.) via Insurance Journal, 28 Sep 2026 | [R] | https://www.insurancejournal.com/news/international/2026/09/28/886998.htm | Freight ~5x start of summer; 13 low-draft vessels in Germany, 9 HGK; low water >2 months, "could stretch well into October"; BASF: no "acute, major economic damage" expected | Citable (fleet lever) |
| C11 | ITF/OECD factsheet "Droughts and River Transport", Sept 2026 | [R] | https://www.itf-oecd.org/droughts-river-transport (403; content via Down To Earth 28 Sep 2026) partly UNVERIFIED | 2018 -> -0.4 % German GDP; Rhine summer discharge -10 % by 2050; 60 trucks per 1,500 t barge | Citable once fetched |
| C12 | Triodos Bank (Stegeman, H.; de Wilde, J.; Hobma, E.), 4-12 Aug 2026 | [F] | https://www.triodos-im.com/articles/2026/extreme-heat-could-wipe-out-eu-economic-growth-in-2026 (listing; cited by EEA 2026) | EU GDP -~1 % (~EUR 180 bn) in 2026 from heat and drought, four channels incl. transport and logistics; labour productivity ~0.6 pp | Context only (not Rhine-specific) |
| C13 | BASF Quarterly Statement Q3 2026, 28 Oct 2026; analyst speech | [C] | https://www.basf.com/dam/jcr:9d4392ff-1402-43f6-be6e-8055826f4f0a/basf/www/global/documents/en/investor-relations/calendar-and-publications/reports/2026/BASF_Quarterly-Statement_03-2026.pdf (fetched) | Only macro mention: "low water levels on the Rhine dampened industrial production" in Germany; no own cost line; the speech PDF contains no Rhine passage; Reuters via ad-hoc-news: "no significant effects on its 2026 results" [R] | Citable for the absence of a company cost (contrast with EUR 250 m in 2018) |
| C14 | Binnenvaartkrant, 30 Oct 2026 | [R] | https://www.binnenvaartkrant.nl/featured/2026/10/30/laagwater-rijn-duitse-rederijen-opperen-aanleg-sluizen/ | MSG and Bavaria propose locks on the Rhine; low water may last to year-end; 4,600 t Rotterdam-Nuremberg on 21 Sep needed 14 barges instead of 3 | Context (policy response) |
| C15 | BfG Niedrigwasser-Update 15 Oct 2026 | [C] | https://www.bafg.de/SharedDocs/Downloads/DE/bfg_niedrigwasserbericht/2026/261015_nw_bericht.pdf (fetched) | Rain "hat die Lage ... kaum veraendert"; Rhine "historisch niedrige Wasserfuehrung"; below MNW for the next two weeks; no sustainable relief in sight | Citable for the autumn profile |
| C16 | Swiss Federal Council / WBF compulsory-stock releases (protein feed), 31 Aug and 15 Oct 2026 | [R] | derbund.ch, foodaktuell.ch (search snippets) UNVERIFIED | Up to 20 % of stocks (~16,000 t) released from 1 Sep 2026; wider release from 15 Oct 2026; cause stated as Rhine and Danube transport, not world supply | Supports message 3 (loss outside the corridor); verify before citing |

### 2D. High-profile papers on supply-chain propagation of climate hazards, 2018-2026 (venue conversation)

| # | Authors, date | Title | Venue | DOI (verified) | Model class / hazard / transport | Key numbers | Verdict |
|---|---|---|---|---|---|---|---|
| D1 | Willner, S. N.; Otto, C.; Levermann, A., 28 May 2018 | Global economic response to river floods | Nature Climate Change 8, 594-598 | 10.1038/s41558-018-0173-2 | Acclimate, global, river floods, transport as delays | n/a here | Citable context |
| D2 | Shughrue, C.; Werner, B. T.; Seto, K. C., 4 May 2020 | Global spread of local cyclone damages through urban trade networks | Nature Sustainability 3, 606-613 | 10.1038/s41893-020-0523-8 | Urban trade network, cyclones | n/a | Citable context |
| D3 | Wang, D.; Guan, D.; Zhu, S.; et al., 7 Dec 2020 | Economic footprint of California wildfires in 2018 | Nature Sustainability 4, 252-260 | 10.1038/s41893-020-00646-7 | Disaster IO, wildfires | n/a | Citable context |
| D4 | Naumann, G.; Cammalleri, C.; Mentaschi, L.; Feyen, L., 10 May 2021 | Increased economic drought impacts in Europe with anthropogenic warming | Nature Climate Change 11, 485-491 | 10.1038/s41558-021-01044-3 | European drought damage functions (JRC) | n/a | Citable context (Europe, drought) |
| D5 | Kuhla, K.; Willner, S. N.; Otto, C.; Geiger, T.; Levermann, A., 27 Oct 2021 | Ripple resonance amplifies economic welfare loss from weather extremes | Environmental Research Letters 16, 114010 | 10.1088/1748-9326/ac2932 | Acclimate, compound extremes | n/a | Citable context (compound/sequence of events: message 2) |
| D6 | Middelanis, R.; Willner, S. N.; Otto, C.; Kuhla, K.; Quante, L.; Levermann, A., Dec 2021 | Wave-like global economic ripple response to Hurricane Sandy | Environmental Research Letters 16, 124049 | 10.1088/1748-9326/ac39c0 | Acclimate | three-phase ripple | Citable context |
| D7 | Middelanis, R.; Willner, S. N.; Otto, C.; Levermann, A., Oct 2022 | Economic losses from hurricanes cannot be nationally offset under unabated warming | Environmental Research Letters 17, 104013 | 10.1088/1748-9326/ac90d8 | Acclimate | n/a | Citable context |
| D8 | Otto, C.; Kuhla, K.; Geiger, T.; Schewe, J.; Frieler, K., 6 Jan 2023 | Better insurance could effectively mitigate the increase in economic growth losses from U.S. hurricanes under global warming | Science Advances 9, eadd6616 | 10.1126/sciadv.add6616 | Growth-loss model, hurricanes | n/a | Citable context |
| D9 | Sun, Y.; Zhu, S.; Wang, D.; ...; Guan, D., 13 Mar 2024 | Global supply chains amplify economic costs of future extreme heat risk | Nature 627, 797-804 | 10.1038/s41586-024-07147-z | Hybrid IO-CGE trade module, heat | Indirect losses become dominant; 0.6-4.6 % global loss by 2060; China 2.7 %, USA 1.8 % | Citable context (the "Sun et al." paper) |
| D10 | Kotz, M.; Levermann, A.; Wenz, L., 17 Apr 2024 | The economic commitment of climate change | Nature 628, 551-557 | 10.1038/s41586-024-07219-0 | Panel damage functions | 19 % income loss by 2049 (original) | **RETRACTED 3 Dec 2025** (data sensitivity to one country). Do not cite |
| D11 | Fang, D.; Xu, F.; Jin, X.; Song, C.; Gao, P.; Sun, L.; Wang, D.; Feng, K., 19 Jan 2026 | Stress-testing the cascading economic impacts of urban flooding across 306 Chinese cities | Nature Cities 3, 89-101 | 10.1038/s44284-025-00372-1 | Risk-extended MRIO, floods, 6 return periods | Spillovers concentrate in hubs | Citable context (Chinese MRIO school, 2026) |
| D12 | Passos, M. V.; Kan, J.-C.; Destouni, G.; Barquet, K.; Brandimarte, L.; Kalantari, Z., 15 Aug 2025 | Estimation of cascading hydroclimatic hazard impacts on supply systems and associated economic shocks | npj Natural Hazards 2, 81 | 10.1038/s44304-025-00129-9 | Supply-driven IO (FIGARO), Sweden, floods/drought/heat | EUR 8.4 bn 2005-2022 (floods 4.1, drought 2.9, heat 2.3) | Low relevance (Sweden, no transport) |
| D13 | Lenzen, M.; Li, M. (order as in Crossref), 16 Jul 2025 | Climate change triggers supply-chain losses that substantially exceed direct damages | Research Square preprint | 10.21203/rs.3.rs-7012657/v1 | Global MRIO with production flexibility | Indirect up to 5x direct; >5 % world GDP at 3 degC, ~15 % above 4 degC | Preprint; cite only if published |
| D14 | Usman, S.; Gonzalez-Torres Fernandez, G.; Parker, M., Sept 2025 | Going NUTS: The regional impact of extreme climate events over the medium term | European Economic Review 178, 105081 | 10.1016/j.euroecorev.2025.105081 | Regional panel (ECB) | Activity -1.5 % two years after a heatwave, -3 % four years after a drought (as cited by ECB speeches) | Citable context (persistence of regional losses) |
| D15 | Ceglar, A.; Jwaideh, M.; O'Donnell, E.; et al., 2025 | Nature at risk: Implications for the euro area economy and financial stability | ECB Occasional Paper 380 | https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op380.en.pdf (fetched) | Nature value-at-risk with sectoral production functions | Surface-water scarcity: up to 24 % of euro-area output at risk under a 100-yr drought; agriculture 30 %/38 % | Citable context |
| D16 | Already cited in refs.bib: Inoue and Todo 2019; Colon et al. 2021; Guan et al. 2020; Koks et al. 2019; Otto et al. 2017; Wenz and Levermann 2016; Hallegatte 2008, 2014; Pichler et al. 2022; Diem et al. 2022 | | | | | | see section 5 |

---

## 3. The 2026 event: analyses, dates and numbers (addendum to the dossiers of 2-10 Sept 2026)

Items before 10 September 2026 are in `evidence_rhine2026_timeline.md` and
`update_20260903_supply_chain_damage.md` and are only listed where a new primary source was
found. Chronological.

| Date | Source | Statement / numbers | Tag |
|---|---|---|---|
| 16 Jul 2026 | FONA/BMFTR interview with M. Braun (FiW, R2K-Klim+) | Project computes damage scenarios for the Rhine economy (Prognos models); Q4 2018 industrial loss ~EUR 2 bn; low-water years 2018, 2019, 2020, 2022, 2023, 2025 | [C] |
| 4 Aug 2026 | ING THINK (C. Brzeski), "Low water levels are new setback for the German economy" | 2018 cost ~0.3 pp of GDP growth and ~1 % of industrial production in the low-water month; 2026 "at least 0.3 percentage points"; Kaub 24 cm; Rhine ~80 % of German IWW tonnage, ~6 % of total freight | [F] |
| 6 Aug 2026 | Prognos for Handelsblatt | Production value -EUR 912.8 m; ~1,900 jobs; chemicals EUR 425 m; refining EUR 206 m; Mannheim-Ludwigshafen EUR 494 m / EUR 107 m value added; 68 districts, 15 regions; levels to 30 Jul + 6-week outlook + extrapolation to 31 Oct | [F] |
| 4-12 Aug 2026 | Triodos Bank | EU GDP -~1 % (~EUR 180 bn) from heat and drought in 2026; transport and logistics one of four channels | [F] |
| 1 Sep 2026 | Coface (E. Barre) | Kaub 8 cm on 18 Aug; barges ~20 % of load; Rhine 60 % and Danube 12 % of European IWW; 2018 GDP -0.3 to -0.4 pts; BASF Ludwigshafen ~40 % of freight by barge | [R] |
| 1 Sep (print) / 11 Oct 2026 (online) | Jannsen and Meuchelboeck, Wirtschaftsdienst 106(9) | Scenario I (low water to late Sept): producing sector -1.2 % in Q3, recovery in Q4; scenario II (2018-type autumn): -1 % in Q3 and Q4, normalisation 2027; 2018 revised: production -0.7 % Q3, -1 % Q4; GDP -0.2 %/-0.3 %; year -0.1 %; dependent firms cut exports after missing imports; mode switching persistent | [F] |
| 3 Sep 2026 | Kiel Institute, KKB 137 (autumn report) | Box: -1.2 % producing sector in Q3 -> GDP -0.3 % ceteris paribus; adopted -0.2 % of GDP in Q3; low water assumed to end about end-September; capacity utilisation "ausgesprochen niedrig" and logistics made more robust since 2018 argue for smaller effects, record levels for larger; no large catch-up expected | [F] |
| 10 Sep 2026 | CCNR press release | "navigation has never been interrupted"; loading capacities "significantly reduced"; preparedness "significantly higher than it was in 2018"; Masterplan Rhine (spring 2026); market observation monitors impacts | [C] |
| Sept 2026 | Gemeinschaftsdiagnose Herbst 2026 | Q3 GDP +0.1 % q/q; low water since mid-July "behindert insbesondere die chemische Industrie"; 30 low-water days -> producing sector -0.7 to -1.2 %; July production -1.1 % m/m; exports -0.2 % and imports -0.3 % in Q3, low water the main burden; catch-up expected in Q4 with normal levels | [F] |
| 28 Sep 2026 | Bloomberg via Insurance Journal | Freight costs ~5x start of summer; 13 low-draft vessels in Germany (9 HGK); BASF: no "acute, major economic damage" expected; HGK calls for state support for smaller operators | [R] |
| 28 Sep 2026 | ITF/OECD factsheet (via Down To Earth) | 2018 -> -0.4 % German GDP; summer discharge -10 % by 2050; 60 trucks per 1,500 t barge; six-week forecasts cited as the adaptation tool | [R] |
| 26-28 Sep 2026 | Kaub negative for the first time (-3 cm on 26 Sep, TechTimes; Contargo table shows negative readings in early and mid-October) | | [R] |
| 7 Oct 2026 | Destatis PD 355 | August production +2.0 % m/m (revised to +1.0 % on 6 Nov) | [C] |
| 15 Oct 2026 | BfG Niedrigwasser-Update | Rain "kaum veraendert"; Rhine historically low over long stretches; below MNW for two more weeks; "keine nachhaltige Aufloesung ... in Sicht"; precipitation deficit 45-56 % in parts of the Rhine basin (15 Sep-14 Oct) | [C] |
| 15 Oct 2026 | Swiss WBF ordinance | Further release of compulsory protein-feed stocks (first release 1 Sep: up to 20 %, ~16,000 t), cause: Rhine and Danube transport | [R] |
| 19 Oct 2026 | ECB Elderson, Manila | Rivers "exceptionally low ... affecting transport, industry and energy production"; 24 % exposure figure (OP 380) | [C] |
| 21 Oct 2026 | Bundesbank Monatsbericht Oktober | Q3 GDP stagnation expected; Rhine low water and restricted shipping "belasteten ... die Industrie"; energy-intensive branches; modal shift raises transport costs; Rhine very low "auch im September durchgaengig"; external trade via European ports negatively affected | [C] |
| 22 Oct 2026 | The Local (on the Bundesbank report) | "likely contracted in the third quarter"; chemicals and coke/petroleum "particularly hard" hit | [R] |
| 26 Oct 2026 | ECB Elderson, Yerevan | Rhine "lowest since records began in 1880"; "could also reduce Germany's economic recovery by up to 0.2 percentage points of GDP in the third quarter" (footnote 4) | [C] |
| 28 Oct 2026 | BASF Q3 2026 statement and call | Sales EUR 16.36 bn (snippet); statement mentions only that Rhine low water dampened German industrial production; no own low-water cost; Reuters (via ad-hoc-news): no significant effect on 2026 results, risk rising if drought persists | [C]/[R] |
| 29 Oct 2026 | CCNR Annual Report 2026 (2025 data) | Rhine 281.9 Mt (-0.9 %); EU-27 458.4 Mt (-3.2 %); chemicals -2.0 %, mineral oil -2.9 %, iron ore -14.4 %; 67 new tankers in 2025 | [C] |
| 30 Oct 2026 | Destatis PD 381 (flash) | Q3 GDP +0.2 % q/q (price-, season-, calendar-adjusted), +1.3 % y/y; consumption slightly up, investment down, exports "merklich" weaker; Handelsblatt/dpa: "Wachstum trotz Niedrigwasser" | [C] |
| 30 Oct 2026 | Binnenvaartkrant | MSG and Bavaria propose locks; low water may last to year-end; 4,600 t on 14 barges instead of 3 (21 Sep) | [R] |
| 30 Oct - 6 Nov 2026 | Kaub (PEGELONLINE via wetter.net; hochwasser.rlp.de) | 44 cm on 30 Oct after storm rain; 21 cm on 2 Nov; 18 cm on 3 Nov; 21 cm on 6 Nov (forecast 24 cm) | [R] |
| 1 Nov 2026 | Hapag-Lloyd revised Kaub low-water surcharges (Container News) | barge transport could become "operationally unviable" | [R] |
| 3 Nov 2026 | EEA Briefing 22/2026 | Rhine case study (see C5); EU-wide 2026 GDP impact "at least around -1 %" (Triodos); cites Deidda et al. 2026 and Vanniya Perumal et al. 2026 | [C] |
| 3 Nov 2026 | Covestro Q3 2026 results | Scheduled for 3 Nov; the release could not be retrieved (covestro.com TLS failure; no wire coverage indexed). Gap. | - |
| 4 Nov 2026 | ECB Blog, C. Lagarde, "A warning from Europe's hot summer" | Drought "lowered water levels in major rivers such as the Rhine and the Danube, disrupting key shipping routes"; ECB staff: "only a small and temporary effect on euro area activity"; German Rhine effect "expected to reverse once river flow normalises" | [C] |
| 6 Nov 2026 | Destatis PD 389 | September production +0.7 % m/m; industry +1.7 %; energy-intensive +0.8 % m/m, -1.9 % y/y; construction -2.6 %; Q3 production -0.4 % vs Q2; no mention of low water | [C] |
| 11 Nov 2026 (pending) | Sachverstaendigenrat Jahresgutachten 2026/27 | due 11 Nov 2026 | - |
| 25 Nov 2026 (pending) | Destatis detailed Q3 accounts; sectoral value added | | - |

What this means for the manuscript's forecast evaluation. The realised third quarter is
better than every ex-ante estimate (GDP +0.2 % q/q against stagnation expected by the
Bundesbank and +0.1 % by the Gemeinschaftsdiagnose); Kiel's adopted effect was -0.2 % of
GDP and the ECB's -0.2 pp. The industrial production index for Q3 is -0.4 % against Q2 with
energy-intensive output -1.9 % y/y in September. The Discussion's announced tests (September
index, then October and November, services turnover) remain the right ones; the aggregate
GDP print is not a test of a sector-level mechanism and the paper should say so.

Not found (searched): a Kiel Policy Brief on 2026; DIW/ifo/RWI/ZEW low-water notes beyond
the Gemeinschaftsdiagnose; CPB/CBS/TNO Dutch analyses of 2026; a JRC drought report after
12 Aug 2026 with economic numbers; Destatis monthly inland-shipping volumes for July to
September 2026 (the July statistical report exists as xlsx but was not parsed); the CCNR
Market Insight for autumn 2026; Covestro and thyssenkrupp autumn figures.

---

## 4. Mischaracterisations and alignment issues found in main.tex and refs.bib

1. Introduction, "Estimates made during the August closure put the cost to Germany at
   0.1-0.35 percentage points of third-quarter GDP \citep{ifw2026}": the 0.35 is
   Commerzbank's (Solveen, 11 Aug), not the Kiel Institute's. Cite the range to Kiel KKB 137
   (-0.2 % adopted, -0.3 % ceteris paribus), Jannsen and Meuchelboeck 2026 and the ECB
   (0.2 pp), or name Commerzbank via the press item.
2. Introduction, 2018 "left GDP about 0.3-0.4 % below its path at the trough
   \citep{ademmer2023,ademmer2019}": the Kiel authors now give -0.2 % (Q3 2018) and -0.3 %
   (Q4 2018), about -0.1 % over 2018 (A1). Use 0.2-0.3 % and cite A1 alongside ademmer2023.
3. Introduction, "about 1 % of German industrial production for each month of low water":
   A1 gives 1.2 % for a 30-day month and 1.5 % per month from the second month; "about 1 %"
   is defensible but the second-month figure matters for message 2 (sequence of troughs).
4. Introduction, "While that work covered a single country and roads only": true of
   colon2021; add that the model has since been applied to multimodal national and regional
   networks (Zenodo v2 2022; four-regions working paper) so that the novelty rests on the
   continental scale (section 1.2).
5. refs.bib `vinke2023`: key says 2023, entry says 2024, Climate Risk Management 43, 100578
   (online Dec 2023, issue 2024). Harmless but inconsistent.
6. refs.bib `dbcargo2026` note ("400 extra wagons at once, up to 900 (about 200 barge
   loads)") disagrees with `update_20260903_supply_chain_damage.md` ("~400 wagons mobilised
   ad hoc, up to 500 more later; up to ~100 barges replaceable"). Check the DB Cargo page and
   align the Discussion's "tonnage the operator offered in August 2026".
7. Dossier `evidence_rhine_literature.md` F: Bruegel WP 20/2025 "Rhine 2018/2022 as case" is
   an overstatement; the Rhine enters only through citations of Ademmer 2020 and
   Meuchelboeck 2025.
8. Crossref checks of refs.bib entries done in this sweep: turpijn2026 (Sci. Data 13, 472,
   17 Feb 2026) correct; bedoyamaya2024 (TRD 131, 104190, June 2024) correct; gobert2023
   (Front. Clim. 4, 1045466, 10 Jan 2023) correct. Others carry the 6 Oct 2026 check noted in
   the file header.
9. Do not add Kotz, Levermann and Wenz 2024 (retracted; D10).

---

## 5. Already cited in refs.bib (works also surfaced by this sweep)

ademmer2023, ademmer2019, ademmer2020, bedoyamaya2024, jonkeren2007/2011/2014, beuthe2014,
christodoulou2020, scholten2014, vandorsser2020, vinke2022, vinke2023 (year 2024), turpijn2026,
icpr2020, ccnr2019, ccnr2023, gobert2023, colon2021, inoue2019, hallegatte2008, hallegatte2014,
otto2017, wenz2016, guan2020, koks2019, mackenzie2012, welch2022, pichler2022, carvalho2021,
boehm2019, barrot2016, baqaee2019, bonadio2021, diem2022, bachmann2022, koks2016, ifw2026,
dihk2026, contargo2026, dbcargo2026, dwd2026, pegelonline2026, reuters2026, schuttevaer2026,
icis2026, bfg2026, basf2019, wiwo2026. Flags: items 1, 2, 5 and 6 of section 4.

---

## 6. BibTeX of verified entries not in refs.bib

Keys: lower-case first author + year + keyword. Entries whose page could not be fetched
(ABN AMRO, ITF factsheet, Colon and Hallegatte SSRN, Swiss stock releases, Covestro Q3) are
deliberately omitted.

```bibtex
@article{jannsen2026lowwater,
  author  = {Jannsen, Nils and Meuchelb{\"o}ck, Saskia},
  title   = {Konjunkturschlaglicht: Wie stark belastet {Niedrigwasser} die {Wirtschaft}?},
  journal = {Wirtschaftsdienst},
  year    = {2026},
  volume  = {106},
  number  = {9},
  pages   = {705--706},
  doi     = {10.2478/wd-2026-0170}
}

@techreport{meuchelboeck2025navigating,
  author      = {Meuchelb{\"o}ck, Saskia},
  title       = {Navigating Supply Chain Disruptions: How Firms Respond to Low Water Levels},
  institution = {RETHINK-GSC (Horizon Europe GA 101061123); Kiel Institute for the World Economy and Aarhus University},
  type        = {RETHINK-GSC Working Paper},
  number      = {08/2025},
  year        = {2025},
  month       = aug,
  url         = {https://www.kielinstitut.de/publications/navigating-supply-chain-disruptions-how-firms-respond-to-low-water-levels-18291/}
}

@techreport{kiel2026autumn,
  author      = {Boysen-Hogrefe, Jens and Groll, Dominik and Hoffmann, Timo and Jannsen, Nils and Kooths, Stefan and Krohn, Johanna and Mentzer, Finn},
  title       = {Deutsche Wirtschaft im Herbst 2026},
  institution = {Kiel Institut f{\"u}r Weltwirtschaft},
  type        = {Kieler Konjunkturberichte},
  number      = {137 (2026/Q3)},
  year        = {2026},
  note        = {Abgeschlossen am 3 September 2026; box on the Rhine low water},
  url         = {https://www.kielinstitut.de/fileadmin/Dateiverwaltung/IfW-Publications/fis-import/ac88308d-f129-4265-8c0f-337675fbe3e5-KKB_137_2026-Q3_Deutschland_DE_.pdf}
}

@techreport{gd2026autumn,
  author      = {{Projektgruppe Gemeinschaftsdiagnose}},
  title       = {Gemeinschaftsdiagnose Herbst 2026: Aufschwung mit {Strukturproblemen} -- {Finanzpolitik} auf {Abwegen}},
  institution = {DIW Berlin, ifo Institut, Kiel Institut, IWH, RWI},
  year        = {2026},
  month       = sep,
  url         = {https://gemeinschaftsdiagnose.de/wp-content/uploads/2026/09/GD26H_v2_mitSperrfrist.pdf}
}

@misc{prognos2026rhine,
  author       = {{Prognos AG} and Sander, Lukas and Norpoth, Robert},
  title        = {Niedrigwasser am {Rhein}: Wirtschaftliche {Sch{\"a}den} von {\"u}ber 900 {Millionen} {Euro} m{\"o}glich},
  year         = {2026},
  howpublished = {Prognos, analysis for Handelsblatt, page dated 6 August 2026, \url{https://www.prognos.com/de/wirtschaftliche-schaeden-niedrigwasser-rhein}},
  note         = {R2K-Klim+ freight and REGINA models; 68 districts; production value EUR 912.8 million}
}

@misc{prognos2023r2kklim,
  author       = {{Prognos AG}},
  title        = {Niedrigwasser im {Rhein}: Die {Folgen} des {Klimawandels} ({Projekt} {R2K-Klim+}, {Phase} 1)},
  year         = {2023},
  howpublished = {\url{https://www.prognos.com/de/projekt/niedrigwasser-im-rhein-die-folgen-des-klimawandels}; project site \url{https://r2k-klim.net/}},
  note         = {Extreme low-water year: up to 10.2 Mt of barge deliveries lost, production value EUR 3.4 billion, about 8,000 jobs}
}

@misc{bundesbank2026october,
  author       = {{Deutsche Bundesbank}},
  title        = {Monatsbericht {Oktober} 2026: {Kurzbericht} {Konjunkturlage}},
  year         = {2026},
  howpublished = {21 October 2026, \url{https://publikationen.bundesbank.de/publikationen-de/berichte-studien/monatsberichte/monatsbericht-oktober-2026-1010626?article=kurzbericht-konjunkturlage-1010630}}
}

@misc{destatis2026q3gdp,
  author       = {{Statistisches Bundesamt}},
  title        = {Bruttoinlandsprodukt im 3. {Quartal} 2026 um 0,2\,\% h{\"o}her als im {Vorquartal}},
  year         = {2026},
  howpublished = {Pressemitteilung Nr. 381, 30 October 2026, \url{https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/10/PD26_381_811.html}}
}

@misc{destatis2026production,
  author       = {{Statistisches Bundesamt}},
  title        = {Produktion im {September} 2026: +0,7\,\% zum {Vormonat}},
  year         = {2026},
  howpublished = {Pressemitteilung Nr. 389, 6 November 2026, \url{https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/11/PD26_389_421.html}}
}

@misc{elderson2026nature,
  author       = {Elderson, Frank},
  title        = {Taking action for nature -- investing in economic resilience and prosperity},
  year         = {2026},
  howpublished = {Speech at COP17 Finance and Biodiversity Day, Yerevan, 26 October 2026, European Central Bank, \url{https://www.ecb.europa.eu//press/key/date/2026/html/ecb.sp261026~d903d7ad85.en.html}},
  note         = {Footnote 4: Rhine low water could reduce Germany's recovery by up to 0.2 percentage points of GDP in Q3 2026}
}

@misc{lagarde2026summer,
  author       = {Lagarde, Christine},
  title        = {A warning from {Europe}'s hot summer},
  year         = {2026},
  howpublished = {The ECB Blog, 4 November 2026, \url{https://www.ecb.europa.eu/press/blog/date/2026/html/ecb.blog20261104~78299c3eaf.en.html}}
}

@techreport{ceglar2025nature,
  author      = {Ceglar, Andrej and Jwaideh, Mark and O'Donnell, Emma and Danieli, Francesca and Pasqua, Carlo and Hutchinson, John and Cimini, Francesco and Sabuco, Juan and Alvarez, Jimena and Ranger, Nicola and Heemskerk, Irene},
  title       = {Nature at risk: Implications for the euro area economy and financial stability},
  institution = {European Central Bank},
  type        = {Occasional Paper Series},
  number      = {380},
  year        = {2025},
  url         = {https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op380.en.pdf}
}

@techreport{eea2026infrastructure,
  author      = {{European Environment Agency}},
  title       = {Europe's critical infrastructure under climate stress: lessons from 2026},
  institution = {EEA},
  type        = {EEA Briefing},
  number      = {22/2026},
  year        = {2026},
  month       = nov,
  doi         = {10.2800/2469788},
  url         = {https://www.eea.europa.eu/en/analysis/publications/europes-critical-infrastructure-under-climate-stress-lessons-from-2026}
}

@misc{ccnr2026lowwater,
  author       = {{Central Commission for the Navigation of the Rhine}},
  title        = {Low water this summer and autumn on the {Rhine}: the {CCNR} is continuing its efforts to strengthen resilience},
  year         = {2026},
  howpublished = {Press release, Strasbourg, 10 September 2026, \url{https://www.ccr-zkr.org/files/documents/cpresse/cp20260910en.pdf}}
}

@techreport{ccnr2026annual,
  author      = {{Central Commission for the Navigation of the Rhine}},
  title       = {Annual report 2026: Inland navigation in {Europe}, market observation},
  institution = {CCNR, Strasbourg, in partnership with the European Commission},
  year        = {2026},
  note        = {Press release CC/CP (26)08 of 29 October 2026, \url{https://www.ccr-zkr.org/files/documents/cpresse/cp20261029en.pdf}; report at \url{https://inland-navigation-market.org/}}
}

@misc{bfg2026october,
  author       = {{Bundesanstalt f{\"u}r Gew{\"a}sserkunde}},
  title        = {Niedrigwasser-{Update} vom 15. {Oktober} 2026},
  year         = {2026},
  howpublished = {\url{https://www.bafg.de/SharedDocs/Downloads/DE/bfg_niedrigwasserbericht/2026/261015_nw_bericht.pdf}}
}

@misc{coface2026rhine,
  author       = {Barr{\'e}, Eve},
  title        = {Low water levels on the {Rhine} and {Danube} put the {European} economy under pressure},
  year         = {2026},
  howpublished = {Coface Economic Insights, 1 September 2026, \url{https://www.coface.com/news-economy-and-insights/low-water-levels-on-the-rhine-and-danube-put-the-european-economy-under-pressure}}
}

@misc{bloomberg2026rhine,
  author       = {Brendel, Eva and Martin, Marilen},
  title        = {Low {Rhine} levels force companies to adapt to new climate normal},
  year         = {2026},
  howpublished = {Bloomberg, syndicated by Insurance Journal, 28 September 2026, \url{https://www.insurancejournal.com/news/international/2026/09/28/886998.htm}}
}

@misc{basf2026q3,
  author       = {{BASF SE}},
  title        = {Quarterly Statement {Q3} 2026},
  year         = {2026},
  howpublished = {28 October 2026, \url{https://www.basf.com/dam/jcr:9d4392ff-1402-43f6-be6e-8055826f4f0a/basf/www/global/documents/en/investor-relations/calendar-and-publications/reports/2026/BASF_Quarterly-Statement_03-2026.pdf}}
}

@misc{binnenvaartkrant2026sluizen,
  author       = {{Binnenvaartkrant}},
  title        = {Laagwater {Rijn}: {Duitse} rederijen opperen aanleg sluizen},
  year         = {2026},
  howpublished = {30 October 2026, \url{https://www.binnenvaartkrant.nl/featured/2026/10/30/laagwater-rijn-duitse-rederijen-opperen-aanleg-sluizen/}}
}

@misc{triodos2026summer,
  author       = {Stegeman, Hans and de Wilde, Joeri and Hobma, Ernst},
  title        = {Economic effects of the hot {European} summer of 2026},
  year         = {2026},
  howpublished = {Triodos Bank, August 2026; summary \url{https://www.triodos-im.com/articles/2026/extreme-heat-could-wipe-out-eu-economic-growth-in-2026}},
  note         = {Cited by EEA Briefing 22/2026; EU GDP about -1\,\% (about EUR 180 billion)}
}

@article{verschuur2022ports,
  author  = {Verschuur, Jasper and Koks, Elco E. and Hall, Jim W.},
  title   = {Ports' criticality in international trade and global supply-chains},
  journal = {Nature Communications},
  year    = {2022},
  volume  = {13},
  pages   = {4351},
  doi     = {10.1038/s41467-022-32070-0}
}

@article{verschuur2023systemic,
  author  = {Verschuur, Jasper and Koks, Elco E. and Hall, Jim W.},
  title   = {Systemic risks from climate-related disruptions at ports},
  journal = {Nature Climate Change},
  year    = {2023},
  volume  = {13},
  pages   = {804--806},
  doi     = {10.1038/s41558-023-01754-w}
}

@article{verschuur2023multihazard,
  author  = {Verschuur, Jasper and Koks, Elco E. and Li, Sihan and Hall, Jim W.},
  title   = {Multi-hazard risk to global port infrastructure and resulting trade and logistics losses},
  journal = {Communications Earth \& Environment},
  year    = {2023},
  volume  = {4},
  pages   = {5},
  doi     = {10.1038/s43247-022-00656-7}
}

@article{verschuur2025chokepoints,
  author  = {Verschuur, Jasper and Lumma, Johannes and Hall, Jim W.},
  title   = {Systemic impacts of disruptions at maritime chokepoints},
  journal = {Nature Communications},
  year    = {2025},
  volume  = {16},
  pages   = {10421},
  doi     = {10.1038/s41467-025-65403-w}
}

@misc{devetak2026rerouting,
  author        = {Devetak, Mitja and Verschuur, Jasper and Klimek, Peter},
  title         = {Adaptive rerouting reshapes impacts of maritime chokepoint disruptions},
  year          = {2026},
  howpublished  = {arXiv:2606.13431 [physics.soc-ph], 11 June 2026},
  url           = {https://arxiv.org/abs/2606.13431}
}

@techreport{massoni2026climatetrade,
  author      = {Massoni, Hubert},
  title       = {Climate Trade Costs: Extreme Weather, Transportation, and Supply Chains},
  institution = {CEPREMAP},
  type        = {Document de travail (Docweb)},
  number      = {2602},
  year        = {2026},
  month       = jul,
  url         = {https://www.cepremap.fr/depot/docweb/docweb2602.pdf}
}

@techreport{papadopoulos2026floods,
  author      = {Papadopoulos, Georgios and Ojea Ferreiro, Javier and Panzica, Roberto},
  title       = {Climate stress test of the global supply chain network: the case of river floods},
  institution = {Bank of Canada},
  type        = {Staff Working Paper},
  number      = {2026-30},
  year        = {2026},
  month       = sep,
  doi         = {10.34989/swp-2026-30}
}

@article{chakraborty2024inequality,
  author  = {Chakraborty, Abhijit and Reisch, Tobias and Diem, Christian and Astudillo-Est{\'e}vez, Pablo and Thurner, Stefan},
  title   = {Inequality in economic shock exposures across the global firm-level supply network},
  journal = {Nature Communications},
  year    = {2024},
  volume  = {15},
  pages   = {3348},
  doi     = {10.1038/s41467-024-46126-w}
}

@article{stangl2024decarbonization,
  author  = {Stangl, Johannes and Borsos, Andr{\'a}s and Diem, Christian and Reisch, Tobias and Thurner, Stefan},
  title   = {Firm-level supply chains to minimize unemployment and economic losses in rapid decarbonization scenarios},
  journal = {Nature Sustainability},
  year    = {2024},
  volume  = {7},
  pages   = {581--589},
  doi     = {10.1038/s41893-024-01321-x}
}

@misc{tabachova2025stress,
  author       = {Tabachov{\'a}, Zlata and Diem, Christian and Stangl, Johannes and Borsos, Andr{\'a}s and Thurner, Stefan},
  title        = {Combined climate stress testing of supply-chain networks and the financial system with nation-wide firm-level emission estimates},
  year         = {2025},
  howpublished = {arXiv:2503.10644 [q-fin.GN], 25 February 2025},
  url          = {https://arxiv.org/abs/2503.10644}
}

@misc{fialkowski2026cascades,
  author       = {Fialkowski, Jan and Havlin, Shlomo and Thurner, Stefan},
  title        = {Catastrophic disruption cascades driven by the nonlinearity of systemic risk},
  year         = {2026},
  howpublished = {arXiv:2607.20068 [econ.GN], 22 July 2026},
  url          = {https://arxiv.org/abs/2607.20068}
}

@article{quante2024weather,
  author  = {Quante, Lennart and Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Global economic impact of weather variability on the rich and the poor},
  journal = {Nature Sustainability},
  year    = {2024},
  volume  = {7},
  pages   = {1419--1428},
  doi     = {10.1038/s41893-024-01430-7}
}

@article{middelanis2023stressed,
  author  = {Middelanis, Robin and Willner, Sven N. and Kuhla, Kilian and Quante, Lennart and Otto, Christian and Levermann, Anders},
  title   = {Stressed economies respond more strongly to climate extremes},
  journal = {Environmental Research Letters},
  year    = {2023},
  volume  = {18},
  pages   = {094034},
  doi     = {10.1088/1748-9326/acec5e}
}

@article{middelanis2022hurricanes,
  author  = {Middelanis, Robin and Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Economic losses from hurricanes cannot be nationally offset under unabated warming},
  journal = {Environmental Research Letters},
  year    = {2022},
  volume  = {17},
  pages   = {104013},
  doi     = {10.1088/1748-9326/ac90d8}
}

@article{middelanis2021sandy,
  author  = {Middelanis, Robin and Willner, Sven N. and Otto, Christian and Kuhla, Kilian and Quante, Lennart and Levermann, Anders},
  title   = {Wave-like global economic ripple response to {Hurricane} {Sandy}},
  journal = {Environmental Research Letters},
  year    = {2021},
  volume  = {16},
  pages   = {124049},
  doi     = {10.1088/1748-9326/ac39c0}
}

@article{kuhla2021ripple,
  author  = {Kuhla, Kilian and Willner, Sven N. and Otto, Christian and Geiger, Tobias and Levermann, Anders},
  title   = {Ripple resonance amplifies economic welfare loss from weather extremes},
  journal = {Environmental Research Letters},
  year    = {2021},
  volume  = {16},
  pages   = {114010},
  doi     = {10.1088/1748-9326/ac2932}
}

@article{otto2023insurance,
  author  = {Otto, Christian and Kuhla, Kilian and Geiger, Tobias and Schewe, Jacob and Frieler, Katja},
  title   = {Better insurance could effectively mitigate the increase in economic growth losses from {U.S.} hurricanes under global warming},
  journal = {Science Advances},
  year    = {2023},
  volume  = {9},
  pages   = {eadd6616},
  doi     = {10.1126/sciadv.add6616}
}

@article{willner2018floods,
  author  = {Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Global economic response to river floods},
  journal = {Nature Climate Change},
  year    = {2018},
  volume  = {8},
  pages   = {594--598},
  doi     = {10.1038/s41558-018-0173-2}
}

@article{shughrue2020cyclone,
  author  = {Shughrue, Chris and Werner, B. T. and Seto, Karen C.},
  title   = {Global spread of local cyclone damages through urban trade networks},
  journal = {Nature Sustainability},
  year    = {2020},
  volume  = {3},
  pages   = {606--613},
  doi     = {10.1038/s41893-020-0523-8}
}

@article{wang2021wildfires,
  author  = {Wang, Daoping and Guan, Dabo and Zhu, Shupeng and Mac Kinnon, Michael and Geng, Guannan and Zhang, Qiang and Zheng, Heran and Lei, Tianyang and Shao, Shuai and Gong, Peng and Davis, Steven J.},
  title   = {Economic footprint of {California} wildfires in 2018},
  journal = {Nature Sustainability},
  year    = {2021},
  volume  = {4},
  pages   = {252--260},
  doi     = {10.1038/s41893-020-00646-7}
}

@article{sun2024heat,
  author  = {Sun, Yida and Zhu, Shupeng and Wang, Daoping and Duan, Jianping and Lu, Hui and Yin, Hao and Tan, Chang and Zhang, Lingrui and Zhao, Mengzhen and Cai, Wenjia and Wang, Yong and Hu, Yixin and Tao, Shu and Guan, Dabo},
  title   = {Global supply chains amplify economic costs of future extreme heat risk},
  journal = {Nature},
  year    = {2024},
  volume  = {627},
  pages   = {797--804},
  doi     = {10.1038/s41586-024-07147-z}
}

@article{naumann2021drought,
  author  = {Naumann, Gustavo and Cammalleri, Carmelo and Mentaschi, Lorenzo and Feyen, Luc},
  title   = {Increased economic drought impacts in {Europe} with anthropogenic warming},
  journal = {Nature Climate Change},
  year    = {2021},
  volume  = {11},
  pages   = {485--491},
  doi     = {10.1038/s41558-021-01044-3}
}

@article{klimek2019resilience,
  author  = {Klimek, Peter and Poledna, Sebastian and Thurner, Stefan},
  title   = {Quantifying economic resilience from input--output susceptibility to improve predictions of economic growth and recovery},
  journal = {Nature Communications},
  year    = {2019},
  volume  = {10},
  pages   = {1677},
  doi     = {10.1038/s41467-019-09357-w}
}

@article{pichler2023alliance,
  author  = {Pichler, Anton and Diem, Christian and Brintrup, Alexandra and Lafond, Fran{\c{c}}ois and Magerman, Glenn and Buiten, Gert and Choi, Thomas Y. and Carvalho, Vasco M. and Farmer, J. Doyne and Thurner, Stefan},
  title   = {Building an alliance to map global supply networks},
  journal = {Science},
  year    = {2023},
  volume  = {382},
  pages   = {270--272},
  doi     = {10.1126/science.adi7521}
}

@article{fang2026flooding,
  author  = {Fang, Delin and Xu, Fei and Jin, Xuanyi and Song, Changqing and Gao, Peichao and Sun, Laixiang and Wang, Daoping and Feng, Kuishuang},
  title   = {Stress-testing the cascading economic impacts of urban flooding across 306 {Chinese} cities},
  journal = {Nature Cities},
  year    = {2026},
  volume  = {3},
  pages   = {89--101},
  doi     = {10.1038/s44284-025-00372-1}
}

@article{passos2025cascading,
  author  = {Passos, Marlon Vieira and Kan, Jung-Ching and Destouni, Georgia and Barquet, Karina and Brandimarte, Luigia and Kalantari, Zahra},
  title   = {Estimation of cascading hydroclimatic hazard impacts on supply systems and associated economic shocks},
  journal = {npj Natural Hazards},
  year    = {2025},
  volume  = {2},
  pages   = {81},
  doi     = {10.1038/s44304-025-00129-9}
}

@misc{lenzen2025supplychain,
  author       = {Lenzen, Manfred and Li, Mengyu},
  title        = {Climate change triggers supply-chain losses that substantially exceed direct damages},
  year         = {2025},
  howpublished = {Research Square preprint, 16 July 2025},
  doi          = {10.21203/rs.3.rs-7012657/v1},
  note         = {Author order as in the Crossref record; the preprint page may list Li first. Preprint, not peer reviewed}
}

@article{usman2025nuts,
  author  = {Usman, Sehrish and Gonz{\'a}lez-Torres Fern{\'a}ndez, Guzm{\'a}n and Parker, Miles},
  title   = {Going {NUTS}: The regional impact of extreme climate events over the medium term},
  journal = {European Economic Review},
  year    = {2025},
  volume  = {178},
  pages   = {105081},
  doi     = {10.1016/j.euroecorev.2025.105081}
}

@article{deidda2026transport,
  author  = {Deidda, Cristina and Khanna, Arpita Asha and Schade, Wolfgang and Smith, Chris and Thiery, Wim},
  title   = {Europe's transport infrastructure is not ready to face climate change},
  journal = {Natural Hazards and Earth System Sciences},
  year    = {2026},
  volume  = {26},
  pages   = {3345--3394},
  doi     = {10.5194/nhess-26-3345-2026}
}

@article{vanniyaperumal2026infrastructure,
  author  = {Vanniya Perumal, Surender Raj and Koks, Elco E. and de Ruiter, Marleen and Thissen, Mark},
  title   = {Critical infrastructure failure escalates the macroeconomic impacts of disasters},
  journal = {Civil Engineering and Environmental Systems},
  year    = {2026},
  pages   = {1--25},
  doi     = {10.1080/10286608.2026.2664413}
}

@misc{vanniyaperumal2025mria,
  author       = {Vanniya Perumal, Surender Raj and Thissen, Mark and de Ruiter, Marleen and Koks, Elco E.},
  title        = {Assessing the macroeconomic impacts of disasters: an updated {Multi-Regional} {Impact} {Assessment} ({MRIA}) model},
  year         = {2025},
  howpublished = {arXiv:2508.00510 [econ.GN], 1 August 2025},
  url          = {https://arxiv.org/abs/2508.00510}
}

@article{chen2025mississippi,
  author  = {Chen, Zhenhua and Rose, Adam and Roberts, Fred and Tucci, Andrew},
  title   = {Regional supply-chain impacts of {Mississippi} {River} fertilizer shipments disrupted by climate change},
  journal = {Risk Analysis},
  year    = {2025},
  volume  = {45},
  number  = {10},
  pages   = {3090--3109},
  doi     = {10.1111/risa.70064}
}

@techreport{jung2025panama,
  author      = {Jung, Paul H. and Kim, Kijin and Jo, Ah-Hyun and Cho, Joseph Seong-Hyun},
  title       = {Panama {Canal} drought and supply chain disruptions in {Asia}--{US} trade: Evidence from micro-level trade shipments and vessel trajectory data},
  institution = {Asian Development Bank},
  type        = {Economics Working Paper},
  year        = {2025},
  month       = nov,
  doi         = {10.22617/WPS250475-2}
}

@article{duldnerborca2025danube,
  author  = {Duldner-Borca, Bianca and Putz-Egger, Lisa-Maria and van Hassel, Edwin},
  title   = {A modelling approach to calculate economic and social benefits of resolving nautical bottlenecks on inland waterways},
  journal = {European Transport Research Review},
  year    = {2025},
  volume  = {17},
  pages   = {39},
  doi     = {10.1186/s12544-025-00734-9}
}

@misc{campoverde2025drought,
  author       = {Campoverde, Andrea L. and Ehret, Uwe and Ludwig, Patrick and Pinto, Joaquim G.},
  title        = {Drought propagation in the {Rhine} {River} basin and its impact on navigation using {LAERTES-EU} regional climate model dataset},
  year         = {2025},
  howpublished = {EGUsphere preprint, 2 October 2025},
  doi          = {10.5194/egusphere-2025-3988}
}

@misc{jansenopdehaar2026twin,
  author       = {Jansen op de Haar, Matthijs and Frutos Rodriguez, Daniel},
  title        = {Digital twin-based simulation for predictive decision-making in waterway logistics},
  year         = {2026},
  howpublished = {arXiv:2606.13492 [cs.CY], 11 June 2026},
  url          = {https://arxiv.org/abs/2606.13492}
}

@techreport{baratadarocha2025climate,
  author      = {Barata da Rocha, Madalena and Grabbe, Heather and Poitiers, Niclas},
  title       = {Climate risks to global supply chains},
  institution = {Bruegel},
  type        = {Working Paper},
  number      = {20/2025},
  year        = {2025},
  month       = sep,
  url         = {https://www.bruegel.org/working-paper/climate-risks-global-supply-chains}
}

@misc{colon2022disruptsc,
  author       = {Colon, C{\'e}lian},
  title        = {ccolon/disrupt-supply-chain-model: v2 -- {Cambodia}},
  year         = {2022},
  howpublished = {Zenodo, 12 December 2022},
  doi          = {10.5281/zenodo.7427207},
  note         = {Multimodal networks: roads, railways, waterways, maritime}
}
```

Deliberately absent from this block: Kotz, Levermann and Wenz (2024), Nature 628, 551-557,
doi 10.1038/s41586-024-07219-0, retracted 3 December 2025 (section 2D, item D10). Do not
add it to refs.bib.

---

## 7. Sources of this sweep not listed above (for traceability)

- Kiel Institute expert page S. Meuchelboeck (publication list): https://www.kielinstitut.de/experts/saskia-meuchelboeck/
- Kiel Institute autumn forecast news (3 Sep 2026): https://www.kielinstitut.de/publications/news/kiel-institute-autumn-forecast-economy-yet-to-gain-momentum/
- DIW on Gemeinschaftsdiagnose Herbst 2026: https://www.diw.de/de/diw_01.c.1020394.de/gemeinschaftsdiagnose_herbst_2026__aufschwung_mit_strukturproblemen_____finanzpolitik_auf_abwegen.html
- The Local, 22 Oct 2026, on the Bundesbank report: https://www.thelocal.de/20261022/low-water-on-the-rhine-cuts-german-economic-growth
- Handelsblatt/dpa, 30 Oct 2026, "Wachstum trotz Niedrigwasser": https://www.handelsblatt.com/politik/deutschland/konjunktur-wachstum-trotz-niedrigwasser-deutsche-wirtschaft-ueberrascht/100266149.html
- Down To Earth on the ITF factsheet, 28 Sep 2026: https://www.downtoearth.org.in/climate-change/drought-driven-low-river-levels-hit-shipping-and-trade-across-major-routes-itf
- PBL summary of Vanniya Perumal et al. 2026: https://www.pbl.nl/en/publications/critical-infrastructure-failure-escalates-the-macroeconomic-impacts-of-disasters
- Retraction note Kotz et al.: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12711553/
- CCNR press-release index: https://www.ccr-zkr.org/13030000-en.html
- DisruptSC applications page: https://disrupt-sc.io/applications/
- wetter.net on Kaub, early Nov 2026: https://www.wetter.net/wetter-news/niedrigwasser-am-rhein-kaub-faellt-auf-21-cm-kein-regen-in-sicht
- Container News on Hapag-Lloyd Kaub surcharges from 1 Nov 2026: https://container-news.com/hapag-lloyd-revises-rhine-low-water-surcharges/
- JRC drought update, 12 Aug 2026: https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/worsening-drought-and-record-heat-grip-europe-fuelling-extraordinary-wildfires-and-extremely-low-2026-08-12_en
