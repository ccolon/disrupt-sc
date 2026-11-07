# Positioning: state of the art of spatially explicit, dynamic supply-chain models of disaster propagation

Compiled 7 November 2026 for the Nature Communications submission "Logistics under drought: how the Rhine
low water of 2026 propagates through Europe's supply chains" (DisruptSC v2, EU27+CH, Kaub 2018/2026).

Scope of this strand: models that propagate a disaster through a production network over time, with
special attention to firm-level agents, explicit transport networks and inventories; the equilibrium
literature (production-network theory, quantitative spatial economics) as the alternative; reviews.

Verification key. Every work below was checked on 7 Nov 2026 against its Crossref DOI record
(`api.crossref.org/works/<doi>`), or, for preprints and reports, the arXiv / publisher / repository
page; abstracts came from Crossref, OpenAlex, publisher pages or press records. "n.v." in a table cell
means that detail (e.g. a time step) was not re-verified today and is given from memory or from the
local dossiers (`input_substitution_literature.md`, which verified the Inoue-Todo, Guan, ARIO, Koks,
Acclimate, Pichler and Diem rules from full texts). Works marked UNVERIFIED could not be reached.

Read first: `main.tex` (Introduction, Discussion, Methods), `sections/si.tex`, `refs.bib`,
`evidence_rhine_literature.md` (section F "Modelling precedents"), `input_substitution_literature.md`,
`AGENTS.md`.

---

## 0. What is already cited, and three flags

**Model-literature keys already in `refs.bib`** (do not re-add): `colon2021`, `inoue2019`, `hallegatte2008`,
`hallegatte2014`, `otto2017`, `wenz2016`, `guan2020`, `pichler2022`, `diem2022`, `koks2016` (MRIA),
`koks2019` (global multi-hazard road/rail assets, Nat. Commun.), `mackenzie2012`, `welch2022`,
`carvalho2021`, `boehm2019`, `barrot2016`, `baqaee2019`, `bonadio2021`, `bachmann2022`, `rauch1999`.

Of these, the text (main + SI) cites only `colon2021`, `inoue2019`, `hallegatte2008`, `hallegatte2014`,
`otto2017`, `guan2020`, `pichler2022`, `carvalho2021`, `boehm2019`, `rauch1999`. Defined but never cited:
`wenz2016`, `koks2016`, `koks2019`, `mackenzie2012`, `welch2022`, `barrot2016`, `baqaee2019`,
`bonadio2021`, `diem2022`, `bachmann2022` (and, outside this strand, `ademmer2020`, `basf2019`,
`bedoyamaya2024`, `gobert2023`, `scholten2014`, `turpijn2026`, `vinke2023`). The draft paragraph in
section 4 uses several of them, so they would stop being orphans.

**Flag 1 (characterisation, soft).** Discussion, line 178: "This sharpens a lesson of the disaster
literature on inventories \citep{hallegatte2014,carvalho2021,boehm2019}". Hallegatte 2014 is indeed about
inventories; Carvalho et al. 2021 and Boehm et al. 2019 are empirical propagation studies of Tohoku whose
lesson is that short-run substitution across inputs and sources is weak (elasticities 0.03-0.2 in Boehm;
~1.2 only at annual horizon in Carvalho). Suggested wording: "a lesson of the disaster literature: short-run
substitution is weak \citep{boehm2019,carvalho2021}, so inventories carry the response \citep{hallegatte2014}".

**Flag 2 (characterisation, confirmed correct).** Introduction, line 56: Colon et al. 2021 "covered a single
country and roads only". Confirmed: the published abstract applies the model "to Tanzanian roads" and the
model's own applications page lists "Transport: roads only" for Tanzania. No change needed.

**Flag 3 (do not cite).** Kotz, Levermann & Wenz 2024, "The economic commitment of climate change",
Nature 628:551-557 (DOI 10.1038/s41586-024-07219-0) was **retracted on 3 December 2025** (retraction
notice DOI 10.1038/s41586-025-09726-0, per the Crossref record). It is not in `refs.bib`; keep it out.

**Note on the "first" claim.** Nothing found today contradicts "the first continental-scale model in which
every shipment between firm-level agents is routed on a multimodal network with mode and route switching,
run at a weekly step and tested on an observed episode". Two caveats for the wording: (i) the agents are a
spatial disaggregation of national accounts, not observed firms (Inoue-Todo, Diem et al. have observed
networks); (ii) spatially explicit firm-level models with hazard coupling exist at national scale (Tanzania,
Cambodia; Japan with establishment geography) and a 2025 preprint offers a generic spatial ABM with flood
hazard but no transport network. Safer phrasing: "to our knowledge the first whole-EU supply-chain model
with explicit multimodal routing of every shipment" rather than "the first firm-level ABM of the EU".

---

## 1. One-page synthesis

**The field has four lineages and a gap in the middle.**

1. *Dynamic input-output (ARIO) and "disaster footprint" models.* Hallegatte's ARIO (2008) and
   ARIO-inventory (2014) follow production, orders, rationing and inventories for the sectors of one
   region at a monthly-to-weekly step; the Guan/Tsinghua-UCL line runs the same dynamics on multiregional
   tables (Guan et al. 2020, 140 regions; Wang et al. 2021 California wildfires; Mendoza-Tinoco et al.
   2020 Central European floods; Sun et al. 2024 heat, Nature; Fang et al. 2026, 306 Chinese cities).
   Transport is absent; agents are sectors or region-sectors; validation is loose. Their robust findings
   (indirect losses rival direct ones; duration matters more than intensity; inventories and heterogeneity
   dominate the outcome) are the backdrop to our messages (1) and (2).
2. *Acclimate (PIK).* A daily, global, price-mediated agent-based model of ~7,000 region-sectors and 1.8
   million trade links (Otto et al. 2017), applied to heat, floods, hurricanes, typhoons and the pandemic
   (Willner et al. 2018; Kuhla et al. 2021, 2023; Middelanis et al. 2021-2023; Quante et al. 2024).
   Transport enters as a delivery delay; there is no network, no routing, no mode. It is the closest in
   *dynamics* (storages, rationing, demand reallocation among existing suppliers) and it has two results
   that anticipate ours: "ripple resonance", consecutive or overlapping extremes amplify losses by 21 % on
   average (Kuhla et al. 2021), and "stressed economies respond more strongly" (Middelanis et al. 2023).
   Our finding that the second 2026 trough costs a quarter more because it meets drained inventories is the
   same mechanism at the scale of one river, and should be framed as such.
3. *Firm-level agent-based models on observed networks.* Inoue & Todo (2019, Nature Sustainability; ~1
   million Japanese firms, daily step, ~9-day inventories, calibrated on the Tohoku production index) and
   the Thurner group's Hungarian VAT network (Diem et al. 2022, ~243,000 firms) show that industry-level
   aggregation understates losses by up to 37 % (Diem et al. 2024) and that product-level definition of
   inputs raises propagation further (Inoue & Todo 2024 preprint). None has a transport layer; observed
   networks exist for a handful of countries (Pichler et al. 2023, Science; Bacilieri et al. 2026).
   What they have and we lack: the real network. What we have and they lack: geography of flows, modes,
   capacity, and a multi-country scope.
4. *Infrastructure-economy coupling (Oxford).* NISMOD-type system-of-systems models (Thacker et al. 2017;
   Koks et al. 2019 IJDRS: power outages triple UK flood losses), global port and shipping-lane models
   (Verschuur et al. 2022 Nat. Commun.; 2023 Nat. Clim. Change: US$81 bn of trade at risk per year), and the
   EU-wide MRIA (Koks et al. 2019 ERL; Vanniya Perumal et al. 2026 add trade-capacity constraints). These
   have explicit networks and continental or global scope but static or annual economics and no firms.

**Inland waterways specifically** have only been costed with inoperability, Monte-Carlo and CGE models of
US systems (Pant et al. 2011, 2015; MacKenzie et al. 2012; Oztanriseven & Nachtmann 2017; Welch et al.
2022; Chen & Cheng 2024; Chen et al. 2025 on the 2022-23 Mississippi low water), in which the river is a
price shock or a lost flow. No propagation model of a Rhine low water exists; the Rhine evidence is
econometric (Ademmer et al. 2023; the new Meuchelboeck 2025 and Horst & Mueller 2024 firm- and
region-level papers, which find persistent modal shifts and a 2018 production shock of the same size as
the Kiel regression).

**Where we sit.** DisruptSC v2 is the only model that combines (a) firm-level agents for all sectors,
(b) every shipment routed on a multimodal network with cargo classes, surcharges, capacity and mode
switching, (c) weekly dynamics with per-input inventories and survey-based criticality, (d) 28 economies,
and (e) a test on an observed episode. Its direct ancestor is the Tanzania model (Colon et al. 2021,
roads only, one country, strict Leontief, no ex-post test); the Cambodia applications (Wang & Colon 2024,
World Bank; Nobile & Colon 2025, EGU) extended it to rail, waterways and sea within one country.

**What reviewers will most likely raise, and the relatives to cite in reply.** (i) Synthetic
supplier-buyer network vs observed networks: cite Diem et al. 2024 and Inoue & Todo 2024 for the size of
the aggregation bias, Bacilieri et al. 2026 and Ialongo et al. 2022 for reconstruction, and report the
eleven-network spread as the sampling uncertainty it is. (ii) No price-responsive demand: Acclimate and
the Hurt-Thurner-Klimek 2025 extension have it; our Discussion already states the assumption and the
2018/2026 records that support it. (iii) Validation on one episode: Inoue & Todo (Tohoku) and Pichler et
al. 2022 (UK Covid) are the only other dynamic models tested ex post; our prospective test is a step
beyond both. (iv) "Rail is inert" vs Meuchelboeck 2025 (firms shifted to rail and road persistently after
2018): her firms are traders, mostly of containerisable goods, which the model lets switch; the inertia we
report is for tank and ore cargo at volume, which Chen & Cheng 2024 also find needs added rail capacity.

**Equilibrium alternative.** Production-network theory (Acemoglu et al. 2012; Baqaee & Farhi 2019, 2022;
Carvalho & Tahbaz-Salehi 2019) and quantitative spatial economics with transport networks (Allen &
Arkolakis 2022; Fajgelbaum & Schaal 2020; Redding & Turner 2015; Redding & Rossi-Hansberg 2017) give the
long-run benchmark with prices and welfare; their elasticities are not those of a season, which is the
case for a weekly, out-of-equilibrium model (Bonadio et al. 2021 use 0.5 for the same reason).

---

## 2. Table of works

Columns: Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / time step | Validation
| Key finding | Distance. Distance = score on five criteria (1 point each; 0.5 partial): **F** firm-level agents,
**T** explicit transport network with routing/modes, **D** sub-monthly dynamics with inventories, **C**
continental multi-country scale, **V** test on an observed episode. Our model: F1 T1 D1 C1 V1.

### A. DisruptSC lineage

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Colon, Hallegatte & Rozenberg 2021 (`colon2021`, in bib) | Nat. Sustain. 4:209-215, 10.1038/s41893-020-00649-4 | Tanzania; floods on roads; disruption duration | Firm agents disaggregated from the national IO table at business-registry/census locations; households; countries | Road network only, shortest-path routing, rerouting under closure, cost passed to prices | Per-input fixed inventory durations (WB firm survey); weekly step (n.v.) | None ex post; criticality ranking | Critical roads differ by supply chain; losses non-linear in duration; sourcing/inventory levers | F1 T0.5 D1 C0 V0 = 2.5. Direct ancestor: lacks modes, cargo classes, capacity, criticality, pooling, multi-country, ex-post test |
| Hallegatte, Rentschler & Rozenberg 2019 (`hallegatte2019lifelines`) | World Bank, 10.1596/978-1-4648-1430-3 | Global policy synthesis | - | - | - | - | Infrastructure disruption costs; reports the Tanzania supply-chain application (as recalled; not re-read) | context |
| Wang & Colon 2024 (`wang2024cambodia`) | World Bank Resilient Transport Series, 10.1596/41974 | Cambodia; 50-year flood on rural roads | DisruptSC firms/households/countries | Roads (rail, waterway, sea in the scope data per model site); rerouting, blocked flows, price rises | As v1/v2 (n.v.) | None | Criticality ranking of rural road sections for investment | 2.5-3; same family, one country |
| Nobile & Colon 2025 (`nobile2025cambodia`) | EGU General Assembly 2025, abstract EGU25-19090 (DOI not verified) | Cambodia; compound riverine flood + tropical cyclone | DisruptSC (CLIMADA for direct damage) | Transport and supply-chain networks, rerouting | n.v. | None stated | Framework identifies infrastructure whose failure in compound events has country-wide effects | 3; same family, one country |
| Colon & Nobile, "When timing matters: compounding floods and supply-chain losses in Cambodia" | SSRN 7077698 - **UNVERIFIED** (page blocked; seen only in a search listing) | Cambodia; 2023 wet season what-ifs | DisruptSC + CLIMADA | multimodal (per listing) | n.v. | n.v. | Compound floods cause system-wide losses with limited physical damage (per listing) | 3; working paper |
| Colon & Hochrainer-Stigler 2023 (`colon2023systemic`) | Supply Chain Management: An Int. J. 28(4):682-694, 10.1108/SCM-03-2022-0101 | Perspective | - | - | - | - | Case for system-level governance of supply-chain systemic risk | context (not a model) |
| Model site (disrupt-sc.io/applications) | - | Ecuador (floods; 2016 earthquake intercomparison), Central Asia & S. Caucasus, Armenia, Gulf/Hormuz 2026 briefs, global | | | | | No peer-reviewed article beyond 2021 found today | context |

### B. Acclimate (PIK)

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Bierkandt, Wenz, Willner & Levermann 2014 (`bierkandt2014acclimate`) | Environ. Syst. Decis. 34:507-524, 10.1007/s10669-014-9523-4 | Global; generic production failure | Region-sectors (EORA) | None (delays) | Storages; daily | None | Forward damage transfer, damage-conserving dynamics | F0 T0 D1 C1 V0 = 2 |
| Wenz, Willner, Bierkandt & Levermann 2014 (`wenz2014acclimate`) | Environ. Syst. Decis. 34:525-539, 10.1007/s10669-014-9521-6 | idem | idem | None | idem | None | Backward (demand) effects added | 2 |
| Wenz & Levermann 2016 (`wenz2016`, in bib) | Sci. Adv. 2:e1501026 | Global; heat stress | Region-sectors | None | Storages; daily | None | Rising connectivity made the economy more sensitive to heat-stress losses | 2 |
| Otto, Willner, Wenz, Frieler & Levermann 2017 (`otto2017`, in bib) | JEDC 83:232-269 | Global; model paper | Region-sectors, price-setting, myopic optimisation | Transport as time delay with quadratic penalty; no network | Storage target 2 d balance, 3x cap; daily; consumption elasticity -0.5 | None | Demand reallocation among existing suppliers by expected price; idle capacity ~10 % | 2. Has prices and price-elastic demand (we lack); lacks firms, network, routing, modes, validation |
| Willner, Otto & Levermann 2018 (`willner2018floods`) | Nat. Clim. Change 8:594-598, 10.1038/s41558-018-0173-2 | Global; projected river floods to ~2035 | Region-sectors | None | daily | None | Flood losses +17 % globally in 20 years; China +82 % direct; US hit indirectly via trade; EU absorbs better; assumes quick supplier shifts | 2 |
| Kuhla, Willner, Otto, Geiger & Levermann 2021 (`kuhla2021resonance`) | ERL 16:114010, 10.1088/1748-9326/ac2932 | Global; heat, river floods, cyclones | ~7,000 regional sectors, 1.8 M trade relations | None | daily | None | **Ripple resonance**: consecutive/overlapping extremes amplify welfare loss by 21 % on average; strongest in high-income economies | 2. Precedent for our message (2) |
| Kuhla, Willner, Otto, Wenz & Levermann 2021 (`kuhla2021heat`) | PLOS ONE 16:e0251210, 10.1371/journal.pone.0251210 | Global; heat stress | idem | None | daily | None | Heat-stress output losses +24 % in 20 years; purchasing-power losses | 2 |
| Middelanis et al. 2021 (`middelanis2021sandy`) | ERL 16:124049, 10.1088/1748-9326/ac39c0 | Global; Hurricane Sandy 2012 | idem | None | daily | Qualitative | Three-phase ripple: demand drop, supply shortage with price rise, recovery | 2 |
| Middelanis, Willner, Otto & Levermann 2022 (`middelanis2022hurricanes`) | ERL 17:104013, 10.1088/1748-9326/ac90d8 | Global; Hurricane Harvey 2017 under warming | >7,000 regional sectors | None | daily | None | US cannot offset hurricane losses nationally under unabated warming | 2 |
| Middelanis et al. 2023 (`middelanis2023stressed`) | ERL 18:094034, 10.1088/1748-9326/acec5e | Global; cyclones, floods, heat during Covid stress | idem | None | daily | None | Consumption losses from extremes double (US) and triple (China) in a pre-stressed economy | 2. Precedent for "the second trough meets drained inventories" |
| Kuhla, Willner, Otto & Levermann 2023 (`kuhla2023typhoon`) | JEDC 151:104663, 10.1016/j.jedc.2023.104663 | Global; typhoons 2000-2016 | idem | None | daily | None | Export resilience to typhoon disruptions rose in China, ASEAN, East Asia, Europe | 2 |
| Quante, Willner, Otto & Levermann 2024 (`quante2024variability`) | Nat. Sustain. 7:1419-1428, 10.1038/s41893-024-01430-7 | Global; weather variability | idem | None | daily | None | Consumption risk highest for middle-income countries; rises with warming | 2 |

### C. Firm-level agent-based models on observed networks (Japan)

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Inoue & Todo 2019 (`inoue2019plos`) | PLOS ONE 14:e0213648, 10.1371/journal.pone.0213648 | Japan; synthetic single-firm failures | ~1 M firms (TSR data) | None | Poisson inventories; daily | - | Propagation faster when same-sector substitutes are scarce; network structure drives it | F1 T0 D1 C0 V0 = 2 |
| Inoue & Todo 2019 (`inoue2019`, in bib) | Nat. Sustain. 2:841-847 | Japan; Tohoku 2011 and predicted Nankai | ~1 M firms | None | Mean 9 d; daily; production stops 6 d after damage | Calibrated/compared to the Tohoku production index | Indirect loss 10.6 % of GDP vs 0.5 % direct (Nankai); very fast propagation | F1 T0 D1 C0 V1 = 3. Has observed network; lacks transport, modes, multi-country |
| Hallegatte 2019 (`hallegatte2019disasters`) | Nat. Sustain. 2:791-792, 10.1038/s41893-019-0380-5 | News & Views on the above | - | - | - | - | Why firm-level networks matter for disaster losses | context |
| Inoue & Todo 2020 (`inoue2020lockdown`) | PLOS ONE 15:e0239251, 10.1371/journal.pone.0239251 | Japan; Tokyo lockdown | 1.6 M firms | None | 9 d; daily | None (ex ante) | Month-long Tokyo lockdown costs ~86 % of a month of national output (as recalled; n.v.) | 2 |
| Inoue, Murase & Todo 2021 (`inoue2021lockdowns`) | PLOS ONE 16:e0255031, 10.1371/journal.pone.0255031 | Japan; regional lockdowns | 1.6 M firms | None | daily | None | Upstreamness, loops and substitutability of a region's suppliers set its lockdown cost; coordination pays | 2 |
| Inoue, Okumura, Torayashiki & Todo 2023 (`inoue2023establishments`) | PLOS ONE 18:e0288062, 10.1371/journal.pone.0288062 | Japan; Tohoku 2011 with tsunami GIS and power outages | Firms + establishments | None | daily | Improved fit to post-quake production | Establishment damage, non-HQ links and outages improve prediction; sector parameters do not | 3 |
| Inoue & Todo 2023 (`inoue2023trade`) | PLOS ONE 18:e0294574, 10.1371/journal.pone.0294574 | Japan; import disruption | ~1 M firms | None | daily | None | Foreign trade shocks propagate through domestic firm chains | 2 |
| Inoue & Todo 2024, v4 Dec 2025 (`inoue2024establishment`) | arXiv:2410.05595 (preprint) | Japan; generic shocks | Establishments, product-level links | None | daily | None | Product-defined inputs give much larger propagation than industry-defined; establishment geography matters for regional shocks | 2.5 |
| Kashiwagi, Todo & Matous 2021 (`kashiwagi2021sandy`) | Rev. Int. Econ. 29:1186-1220, 10.1111/roie.12541 | Global firms; Hurricane Sandy | Empirical (firm network) | - | - | Econometric | Propagation within the US only; input specificity and network density matter | empirical |
| Rolf, Inoue & Lang 2026 (`rolf2026automotive`) | arXiv:2611.01706 (preprint) | Global automotive; hub failure, Tohoku-like scenario | ~77,000 firms, 197,000 links (MarkLines) | None | Calibrated inventories; n.v. | Imputation test only | Product-specific substitution makes cascades 4-5x larger than portfolio-overlap rule | 2 |

### D. ARIO / multiregional "disaster footprint" lineage

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Hallegatte 2008 (`hallegatte2008`, in bib) | Risk Analysis 28:779-799 | Louisiana; Katrina | Sectors of one region | None | Overproduction, adaptation time; monthly | Loose | Indirect losses large; construction overcapacity and adaptation time key | F0 T0 D1 C0 V0.5 = 1.5 |
| Hallegatte 2014 (`hallegatte2014`, in bib) | Risk Analysis 34:152-167 | Louisiana; Katrina | Sectors | None | Inventory targets (90 d; 3 d non-stockable), heterogeneity psi; sub-monthly (n.v.) | Loose | Inventory/heterogeneity parameters move losses from <20 % to collapse | 1.5 |
| Henriet, Hallegatte & Tabourier 2012 (`henriet2012network`) | JEDC 36:150-167, 10.1016/j.jedc.2011.10.001 | Theoretical firm networks | Firms (synthetic) | None | ARIO-type | None | Robustness depends on concentration and clustering of the firm network | 1.5 (firm-level ARIO precursor) |
| Guan et al. 2020 (`guan2020`, in bib) | Nat. Hum. Behav. 4:577-587 | Global, 140 regions; Covid lockdowns | Region-sectors | None | Inventory days; sub-monthly (n.v.) | None (ex ante) | Duration of lockdowns matters more than strictness; capacity-weighted reallocation among existing sources | 2 |
| Wang et al. 2021 (`wang2021wildfires`) | Nat. Sustain. 4:252-260, 10.1038/s41893-020-00646-7 | US multiregional; California wildfires 2018 | Region-sectors | None | ARIO-type; n.v. | None | Economic footprint far beyond direct damage; losses spread across US states | 1.5 |
| Mendoza-Tinoco et al. 2020 (`mendozatinoco2020flood`) | Risk Analysis 40:1612-1631, 10.1111/risa.13497 | Central Europe; 2009 floods | Region-sectors | None | Flood footprint IO; n.v. | None | Indirect losses ~65 % of total; business services, manufacturing, construction, commerce carry 70 % | 1.5. Precedent for message (3) |
| Sun et al. 2024 (`sun2024heat`) | Nature 627:797-804, 10.1038/s41586-024-07147-z | Global; future heat | Region-sectors + CGE trade | None | n.v. | None | Supply chains amplify heat costs; cumulative 0.6-4.6 % by 2060 | 2 |
| Fang et al. 2026 (`fang2026urban`) | Nature Cities 3:89-101, 10.1038/s44284-025-00372-1 | 306 Chinese cities; urban floods | City-sectors | None | n.v. | None | Losses rise non-linearly; shift from direct capital to local indirect losses; spillovers concentrate in hubs | 1.5 |
| Lenzen et al. 2019 (`lenzen2019cyclone`) | NHESS 19:137-151, 10.5194/nhess-19-137-2019 | Australia; Cyclone Debbie 2017 | Region-sectors (IELab MRIO) | None | Static | None | Indirect job losses 3,685 vs 4,802 direct; spillovers to undamaged regions | 1 |
| Shughrue, Werner & Seto 2020 (`shughrue2020cyclone`) | Nat. Sustain. 3:606-613, 10.1038/s41893-020-0523-8 | World cities; tropical cyclones | ~1,500 cities trading (dynamical model) | None (trade network) | n.v. | None | Secondary impacts up to three quarters of the damage of the largest storms; cities with few suppliers most exposed | 2 |
| Oosterhaven & Toebben 2017 (`oosterhaven2017flooding`) | Spatial Econ. Anal. 12:404-428, 10.1080/17421772.2017.1300680 | Germany; 2013 floods | Region-sectors (NLP) | None | Static | None | Wider impacts small relative to direct damages under flexible substitution | 1 |
| Oosterhaven & Bouwmeester 2016 (`oosterhaven2016disruptive`) | J. Reg. Sci. 56:583-595, 10.1111/jors.12262 | Method | - | - | - | - | Non-linear programming alternative to IO for disruptive events | method |

### E. Firm-level network science (Thurner / Oxford) and network reconstruction

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Diem, Borsos, Reisch, Kertesz & Thurner 2022 (`diem2022`, in bib) | Sci. Rep. 12:7719 | Hungary; single-firm failures | ~91,000-243,000 firms (VAT data) | None | Static cascade (generalized Leontief) | None | Systemic-risk index; 32 firms could trigger loss of 23 % of output (as recalled; n.v.) | F1 T0 D0 C0 V0 = 1 |
| Diem et al. 2024 (`diem2024aggregation`) | PNAS Nexus 3:pgae064, 10.1093/pnasnexus/pgae064 | Hungary | ~243,000 firms vs industry IO | None | Static | None | Industry-level models underestimate losses by up to 37 % | 1. Supports our firm-level choice; warns on synthetic networks |
| Chakraborty, Reisch, Diem, Astudillo-Estevez & Thurner 2024 (`chakraborty2024inequality`) | Nat. Commun. 15:3348, 10.1038/s41467-024-46126-w | Global firm-level network | Firms (commercial data) | None | Static | None | Rich countries expose poor ones to systemic risk more than vice versa | 1 |
| Stangl, Borsos, Diem, Reisch & Thurner 2024 (`stangl2024decarbonization`) | Nat. Sustain. 7:581-589, 10.1038/s41893-024-01321-x | Hungary; decarbonisation shutdowns | Firms | None | Static | None | Network-aware firm selection minimises job and output losses | 1 |
| Reisch, Heiler, Diem, Klimek & Thurner 2022 (`reisch2022mobile`) | Sci. Rep. 12:13347, 10.1038/s41598-022-13104-5 | Austria | Firms (phone metadata) | None | Static | Link inference ~90 % | Near-real-time national supply network; ~65 systemically critical firms | 1 |
| Pichler et al. 2023 (`pichler2023alliance`) | Science 382:270-272, 10.1126/science.adi7521 | Policy forum | - | - | - | - | Call to map global supply networks at firm level | context |
| Bacilieri, Borsos, Astudillo-Estevez, Hoefer & Lafond 2026 (`bacilieri2026networks`) | JEDC 187:105313, 10.1016/j.jedc.2026.105313 | Ecuador, Hungary, FactSet | - | - | - | - | Admin datasets without thresholds agree; commercial data biased | context |
| Ialongo et al. 2022 (`ialongo2022reconstructing`) | Sci. Rep. 12:11847, 10.1038/s41598-022-13996-3 | Netherlands | Firms | - | - | - | Max-entropy reconstruction by product improves with product resolution | method for our synthetic network |
| Mungo, Lafond, Astudillo-Estevez & Farmer 2023 (`mungo2023reconstructing`) | JEDC 148:104607, 10.1016/j.jedc.2023.104607 | Method | - | - | - | - | Machine-learning reconstruction of production networks | method |
| Fialkowski, Havlin & Thurner 2026 (`fialkowski2026cascades`) | arXiv:2607.20068 (preprint) | Ecuador; joint firm failures | Firms (national reconstruction) | None | Static | None | Combined failures amplify up to 257x; driven by loss of substitutability | 1 |
| Hurt, Thurner & Klimek 2025 (`hurt2025agentbased`) | arXiv:2505.10146 (preprint) | WIOD regions; generic shocks | Sectors with price/quantity adjustment | None | Dynamic IO | None | Agent-based price-quantity extension of IO recovery models | 1.5 |

### F. Sector-level dynamic input-output with inventories (Pichler-Farmer and relatives)

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Pichler, Pangallo, del Rio-Chanona, Lafond & Farmer 2022 (`pichler2022`, in bib) | JEDC 144:104527 | UK, 55 industries; Covid | Industries | None | Inventories; daily; partially binding Leontief with IHS Markit criticality | **Ex-post** against UK GDP and sectoral output | Criticality ratings forecast the pandemic shock well | F0 T0 D1 C0 V1 = 2. Source of our production rule |
| Pichler & Farmer 2022 (`pichler2022simultaneous`) | Econ. Syst. Res. 34:273-293, 10.1080/09535314.2021.1926934 | Germany, Italy, Spain; Covid | Industries | None | Static with constraints | None | Simultaneous supply and demand constraints; rationing rules matter | 1 |
| del Rio-Chanona, Mealy, Pichler, Lafond & Farmer 2020 (`delriochanona2020shocks`) | Oxf. Rev. Econ. Policy 36:S94-S137, 10.1093/oxrep/graa033 | US; Covid | Industries, occupations | None | Static | None | First-order supply and demand shocks by industry | 1 |
| Mandel & Veetil 2020 (`mandel2020lockdowns`) | Econ. Disasters Clim. Change 4:431-451, 10.1007/s41885-020-00066-z | 56 sectors x 44 countries (WIOD); Covid | Sectors, out-of-equilibrium prices | None | Dynamic; n.v. | None | Lockdown costs of ~9 % of GDP for uncoordinated lockdowns (as recalled; n.v.) | 2 |
| Baqaee & Farhi 2022 (`baqaee2022keynesian`) | AER 112:1397-1436, 10.1257/aer.20201229 | US; Covid | Sectors, nested CES, Keynesian | None | Static equilibrium | None | Supply and demand shocks in disaggregated economies | equilibrium alternative |

### G. Infrastructure-economy coupling, ports, EU MRIA (Oxford / VU Amsterdam)

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Thacker, Pant & Hall 2017 (`thacker2017systems`) | Reliab. Eng. Syst. Saf. 167:30-41, 10.1016/j.ress.2017.04.023 | Great Britain; infrastructure failures | Infrastructure assets, customers | Networks of energy, transport, water (system-of-systems) | Static | None | Multi-scale disruption analysis of national infrastructure (NISMOD) | F0 T0.5 D0 C0 V0 = 0.5 |
| Pant, Hall & Blainey 2016 (`pant2016rail`) | EJTIR 16(1), 10.18757/ejtir.2016.16.1.3120 | Great Britain; rail + power | Rail network, passengers | Rail network explicit | Static | None | Vulnerability of rail to interdependent failures | 0.5 |
| Koks, Pant, Thacker & Hall 2019 (`koks2019electricity`) | Int. J. Disaster Risk Sci. 10:421-438, 10.1007/s13753-019-00236-y | UK, 37 regions; flooding + power outages | Businesses by industrial area; MRIO regions | Electricity network explicit; no transport | Annual MRIA | None | Including outages raises losses up to 300 % | F0.5 T0.5 D0 C0 V0 = 1 |
| Koks et al. 2019 (`koks2019floods`) | ERL 14:084042, 10.1088/1748-9326/ab3306 | EU NUTS2; present and future river floods | Region-sectors (MRIA) | None | Annual LP | None | Up to 60 % of indirect losses offset by alternative suppliers; future losses +350 %; services and utilities rise most | F0 T0 D0 C1 V0 = 1. The whole-EU precedent |
| Koks et al. 2016 (`koks2016comparing`) | NHESS 16:1911-1924, 10.5194/nhess-16-1911-2016 | Po basin, Italy; floods | Region-sectors; IO vs CGE | None | Static | None | Model spread up to a factor of 7; ARIO 3-6x the CGE | method |
| Koks & Thissen 2016 (`koks2016`, in bib) | Econ. Syst. Res. 28:429-449 | Method (MRIA) | Region-sectors | None | Annual LP | - | Cost-minimising reallocation over existing trade links | method |
| Vanniya Perumal, Thissen, de Ruiter & Koks 2026 (`vanniyaperumal2026mria`) | Econ. Syst. Res. (online, 1-24), 10.1080/09535314.2026.2728049; arXiv:2508.00510 | Multi-regional; generic disasters | Region-sectors | **Trade-capacity (logistic) constraints between regions**; no network | Annual | None | Raising production capacity alone is insufficient; trade flexibility needed; sectoral criticality | 1.5. Closest MRIO move toward our capacity gate |
| Verschuur, Koks & Hall 2020 (`verschuur2020ports`) | Transp. Res. D 85:102393, 10.1016/j.trd.2020.102393 | Global ports; natural disasters | Ports (empirical downtime) | Ports | - | Observed events | Port and logistics resilience from observed disruptions | empirical |
| Verschuur, Koks & Hall 2022 (`verschuur2022criticality`) | Nat. Commun. 13:4351, 10.1038/s41467-022-32070-0 | 1,300 ports; criticality | Countries/sectors via supply-chain database | Global maritime network, trade-flow allocation (routing) | Static | Calibrated on trade flows | Five largest ports embody >1.4 % of global output; cross-border dependencies | F0 T0.5 D0 C1 V0 = 1.5 |
| Verschuur, Koks, Li & Hall 2023 (`verschuur2023multihazard`) | Commun. Earth Environ. 4:5, 10.1038/s43247-022-00656-7 | Global ports; multi-hazard | Ports, trade | Maritime | Static | None | US$7.5 bn/yr port losses, US$63 bn/yr trade at risk | 1.5 |
| Verschuur, Koks & Hall 2023 (`verschuur2023systemic`) | Nat. Clim. Change 13:804-806, 10.1038/s41558-023-01754-w | 1,320 ports; climate downtime | Trade flows | Global transport-flow model | Static | None | US$81 bn trade and US$122 bn activity at risk per year | 1.5 |
| Koks et al. 2019 (`koks2019`, in bib) | Nat. Commun. 10:2677 | Global road and rail assets; multi-hazard | Assets | Asset exposure, no flows | - | - | Global asset-level risk of roads and railways | context |

### H. Inland waterway and transport-disruption economics (inoperability, CGE, SCGE)

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Pant, Barker, Grant & Landers 2011 (`pant2011terminals`) | Transp. Res. E 47:722-737, 10.1016/j.tre.2011.02.009 | US; multimodal container terminal inoperability | Sectors (IIM) | Terminal commodity flows | Static/dynamic IIM | None | Interdependent sector losses from terminal closure | 0.5 |
| Pant, Barker & Landers 2015 (`pant2015waterway`) | Comput. Ind. Eng. 89:137-149, 10.1016/j.cie.2014.11.016 | US inland waterway (Arkansas River system) | Sectors (dynamic IIM) | Commodity flows on waterway | Dynamic; n.v. | None | Dynamic losses of commodity-flow disruptions on an inland waterway | 1 |
| MacKenzie, Barker & Grant 2012 (`mackenzie2012`, in bib) | IEEE Trans. SMC-A 42(2) | US; inland port closure | Sectors (multiregional IIM) | Port flows | Dynamic | None | Regional interdependence losses of a port closure | 1 |
| Oztanriseven & Nachtmann 2017 (`oztanriseven2017waterway`) | Eng. Econ. 62:73-89, 10.1080/0013791X.2016.1163627 | US inland waterway; closures | Monte Carlo of response | Waterway | - | None | Losses under short/medium/long disruptions | 0.5 |
| Welch, Lambert, Lambert & Kenkel 2022 (`welch2022`, in bib) | Water 14:753 | Oklahoma; 2019 flood closure | Sectors (MRIO) | Waterway | Static | None | Jobs/output losses by closure length | 0.5 |
| Chen & Cheng 2024 (`chen2024mississippi`) | Ann. Reg. Sci. 73:757-794, 10.1007/s00168-024-01283-0 | Upper Mississippi-Illinois; lock closures, climate | Sectors (multiregional CGE) + spatial econometrics, weekly data | Barge vs rail at aggregate level | Static CGE | Econometric link | **Barge-to-rail shift cuts GDP loss by 6.6-24.2 % in region** | 1. Only other quantified rail-substitution result for a waterway |
| Chen, Rose, Roberts & Tucci 2025 (`chen2025mississippi`) | Risk Analysis 45:3090-3109, 10.1111/risa.70064 | Mississippi; 2022-23 low water, lock damage, import disruption | Sectors (CGE) | Barge rates (empirical, up to +400 %) | Static CGE | Econometric link | GDP loss and inflation; five Upper Mississippi states hit hardest; compound vulnerability | 1. **The only other economic model of a low-water event**; price channel only |
| Rose & Wei 2013 (`rose2013port`) | Econ. Syst. Res. 25:212-232, 10.1080/09535314.2012.731379 | Texas; port shutdown | Sectors (CGE) | Port | Static | None | Resilience (inventories, rerouting, substitution) cuts losses sharply | 0.5 |
| Tsuchiya, Tatano & Okada 2007 (`tsuchiya2007disruptions`) | Econ. Syst. Res. 19:147-162, 10.1080/09535310701328567 | Japan; rail and highway disruptions | Regions (SCGE) | Transport cost changes from network disruption | Static | None | Classic spatial CGE of transport-link disruptions | F0 T0.5 D0 C0 V0 = 0.5 |
| Kajitani & Tatano 2018 (`kajitani2018scge`) | Econ. Syst. Res. 30:289-312, 10.1080/09535314.2017.1369010 | Japan; disasters, short term | Regions (SCGE) | Transport costs | Static | Compared to observed | Applicability of SCGE to short-term disaster impacts | 0.5 |
| Carrera, Standardi, Bosello & Mysiak 2015 (`carrera2015flood`) | Environ. Model. Softw. 63:109-122, 10.1016/j.envsoft.2014.09.016 | Po basin; flood | Regions (CGE) | None | Static | None | Spatial + CGE integration of direct and indirect losses | 0.5 |
| Haraguchi & Lall 2015 (`haraguchi2015thailand`) | Int. J. Disaster Risk Reduct. 14:256-272, 10.1016/j.ijdrr.2014.09.005 | Thailand; 2011 floods | Case study | - | - | - | Supply-chain research questions from the 2011 floods | empirical |

### I. Operations research and digital twins

| Ref (key) | Venue, DOI | Region/scale; hazard | Agents | Transport | Inventories / step | Validation | Key finding | Distance |
|---|---|---|---|---|---|---|---|---|
| Snyder et al. 2016 (`snyder2016review`) | IIE Trans. 48:89-109, 10.1080/0740817X.2015.1067735 | Review | Facilities of one chain | Lanes | Inventory models | - | OR/MS models of disruptions: inventory, sourcing, network design | review |
| Dolgui, Ivanov & Sokolov 2018 (`dolgui2018ripple`) | Int. J. Prod. Res. 56:414-430, 10.1080/00207543.2017.1387680 | Review | idem | - | - | - | "Ripple effect" literature | review |
| Ivanov 2020 (`ivanov2020epidemic`) | Transp. Res. E 136:101922, 10.1016/j.tre.2020.101922 | Global single supply chain; Covid | Facilities (anyLogistix discrete-event) | Shipping lanes, lead times | Inventories; daily | None | Timing of closures and recovery drives impact | F0.5 T0.5 D1 C0.5 V0 = 2.5 but one firm's chain, not an economy |
| Ivanov & Dolgui 2021 (`ivanov2021twin`) | Prod. Plan. Control 32:775-788, 10.1080/09537287.2020.1768450 | Concept | idem | idem | idem | - | Digital supply chain twin for disruption management | concept |
| Simchi-Levi et al. 2015 (`simchilevi2015automotive`) | Interfaces 45:375-390, 10.1287/inte.2015.0804 | Ford global chain | Suppliers, plants | Time-to-recover | Inventories | Practice | Risk exposure index from TTR | firm practice |

### J. Equilibrium alternatives: production-network theory and quantitative spatial economics

| Ref (key) | Venue, DOI | What it offers | Distance |
|---|---|---|---|
| Acemoglu, Carvalho, Ozdaglar & Tahbaz-Salehi 2012 (`acemoglu2012network`) | Econometrica 80:1977-2016, 10.3982/ECTA9623 | Network origins of aggregate fluctuations (Cobb-Douglas) | theory |
| Baqaee & Farhi 2019 (`baqaee2019`, in bib) | Econometrica 87:1155-1203 | Non-linear propagation with nested CES; benchmark elasticities (0.9, 0.5, 0.001) | theory; our Leontief-with-criticality sits at its low-elasticity end |
| Baqaee & Farhi 2022 (`baqaee2022keynesian`) | AER 112:1397-1436, 10.1257/aer.20201229 | Supply and demand shocks with nominal rigidities | theory |
| Carvalho & Tahbaz-Salehi 2019 (`carvalho2019primer`) | Annu. Rev. Econ. 11:635-663, 10.1146/annurev-economics-080218-030212 | Primer on production networks | review |
| Bonadio, Huo, Levchenko & Pandalai-Nayar 2021 (`bonadio2021`, in bib) | J. Int. Econ. 133:103534 | 64-country quantitative model of the pandemic; short-run elasticities 0.5 | equilibrium benchmark |
| Allen & Arkolakis 2022 (`allen2022transportation`) | Rev. Econ. Stud. 89:2911-2957, 10.1093/restud/rdac001 | Welfare effects of transport improvements with endogenous routing and congestion | equilibrium benchmark for transport |
| Fajgelbaum & Schaal 2020 (`fajgelbaum2020networks`) | Econometrica 88:1411-1452, 10.3982/ECTA15213 | Optimal transport networks in spatial equilibrium | idem |
| Redding & Turner 2015 (`redding2015transportation`) | Handb. Reg. Urban Econ. 5:1339-1398, 10.1016/B978-0-444-59531-7.00020-X | Transport costs and the spatial organisation of activity | review |
| Redding & Rossi-Hansberg 2017 (`redding2017quantitative`) | Annu. Rev. Econ. 9:21-58, 10.1146/annurev-economics-063016-103713 | Quantitative spatial economics | review |

### K. Empirical propagation and Rhine firm-level evidence (new items only; Carvalho/Boehm/Barrot are in bib)

| Ref (key) | Venue, DOI | Content | Use |
|---|---|---|---|
| Pankratz & Schiller 2024 (`pankratz2024climate`) | Rev. Financ. Stud. 37:1729-1777, 10.1093/rfs/hhad093 | Heat/flood exposure of suppliers; customers 7 % more likely to drop over-exposed suppliers | adaptation by re-sourcing is slow and partial |
| Meuchelboeck 2025 (`meuchelboeck2025lowwater`) | Kiel Institute / RETHINK-GSC Working Paper, Aug 2025 (no DOI; publisher page verified) | 2018 low water as natural experiment on monthly German firm trade-transport data: inland-waterway exports -20 %, imports -12 %; import-dependent firms cut exports ~4 %; persistent switch to rail/road | Rhine evidence not in the dossier; tension with "rail is inert" to be addressed (containerisable trade vs bulk) |
| Horst & Mueller 2024 (`horst2024rhine`) | SSRN 4818090 - **partially verified** (index listing only; SSRN page blocked) | Regional propagation of Rhine waterway shocks in Germany; firms shift to suppliers off the river (per listing) | Rhine evidence not in the dossier; verify before citing |

### L. Reviews

| Ref (key) | Venue, DOI | Content |
|---|---|---|
| Okuyama & Santos 2014 (`okuyama2014disaster`) | Econ. Syst. Res. 26:1-12, 10.1080/09535314.2013.871505 | Disaster impact and IO analysis (special issue introduction) |
| Botzen, Deschenes & Sanders 2019 (`botzen2019review`) | Rev. Environ. Econ. Policy 13:167-188, 10.1093/reep/rez004 | Models and empirical studies of disaster impacts |
| Galbusera & Giannopoulos 2018 (`galbusera2018inputoutput`) | Int. J. Disaster Risk Reduct. 30:186-198, 10.1016/j.ijdrr.2018.04.030 | IO models in disaster impact assessment |
| Hallegatte 2019 (`hallegatte2019disasters`) | Nat. Sustain. 2:791-792 | Firm-level propagation (News & Views) |
| Kotz, Levermann & Wenz 2024 | Nature 628:551-557 | **RETRACTED 3 Dec 2025** - do not cite |

### M. Other recent spatial agent-based frameworks

| Ref (key) | Venue | Content | Distance |
|---|---|---|---|
| Mohajerani 2025, v4 Apr 2026 (`mohajerani2025cascading`) | arXiv:2509.18633 (preprint) | Open Python spatial ABM: geospatial flood hazard + firms and households; capital hardening (-26 % direct loss) and backup-supplier search (-48 % supplier disruption) on an illustrative global network; no transport network | F1 T0 D1 C0.5 V0 = 2.5; illustrative, not applied to an event |

---

## 3. The five closest relatives, ranked

Scores are the F/T/D/C/V points of section 2 (ours: 5/5). Ties are broken by architectural kinship.

**1. DisruptSC v1 and its national applications - Colon, Hallegatte & Rozenberg 2021 (Tanzania); Wang &
Colon 2024 and Nobile & Colon 2025 (Cambodia).** Score 2.5-3. Same architecture: firm agents disaggregated
from national accounts at plant/registry locations, households, countries, every shipment routed on a
network, rerouting under closure, per-input inventories, weekly steps. *Lacks relative to ours:* one country;
roads only in the published paper (Cambodia adds rail, waterway, sea but is unpublished in a journal); strict
Leontief with no criticality and no pooling; no capacity on edges; no cargo classes or surcharges; no test on
an observed episode. *Has that we lack:* a criticality analysis over every link of the network (we disrupt
one reach); a hazard model coupled upstream (CLIMADA) in the Cambodia work.

**2. Inoue & Todo lineage (2019 Nature Sustainability; 2020-2023 PLOS ONE; 2024 preprint).** Score 3.
Firm-level ABM on the observed network of ~1 million Japanese firms, daily step, inventories of ~9 days,
substitution among existing same-sector suppliers, calibrated and compared against the post-Tohoku production
index; later versions add establishments, tsunami GIS, power outages and product-level inputs. *Lacks:* any
transport network, modes or capacity (the shock is a direct production loss by location); single country;
no transport-induced price. *Has that we lack:* the observed network (no sampling uncertainty across network
versions), establishment geography, product-level input definitions, and the demonstration that both raise
propagation.

**3. Acclimate (Otto et al. 2017; Willner et al. 2018; Kuhla et al. 2021, 2023; Middelanis et al. 2021,
2022, 2023; Quante et al. 2024).** Score 2. Daily, global, out-of-equilibrium, ~7,000 region-sectors and 1.8
million trade links, storages, rationing, price-based reallocation of demand among existing suppliers,
price-elastic consumption. *Lacks:* firm agents, any transport network (transport is a delay), modes,
capacity, validation on an observed episode. *Has that we lack:* global coverage, endogenous prices and
price-responsive demand, and the two compound-event results (ripple resonance; stressed economies) that our
two-trough finding should be related to.

**4. ARIO-inventory on multiregional tables / "disaster footprint" (Hallegatte 2008, 2014; Guan et al.
2020; Wang et al. 2021; Mendoza-Tinoco et al. 2020; Sun et al. 2024; Fang et al. 2026).** Score 1.5-2.
Region-sector dynamics with inventories, overproduction and proportional rationing; the rule family our
ordering and rationing descend from (Guan: orders weighted by baseline share and current capacity, the
template for our pooling). *Lacks:* firms, transport, ex-post tests. *Has that we lack:* multiregional to
global coverage, labour and capital channels, CGE trade in Sun et al. 2024, and a long record of
applications that readers know.

**5. Infrastructure-economy coupling of the Oxford/VU group - Verschuur, Koks & Hall 2022, 2023 (ports and
shipping lanes); Thacker, Pant & Hall 2017 and Koks, Pant, Thacker & Hall 2019 (NISMOD); Koks et al. 2019
ERL and Vanniya Perumal et al. 2026 (EU MRIA with trade-capacity constraints).** Score 1-1.5. Explicit
infrastructure or maritime networks with flow allocation at national to global scale, hazard-asset risk
integration, EU-wide regional accounts, and, since 2026, logistic capacity constraints on inter-regional
trade. *Lacks:* dynamics and inventories (static or annual), firms, modes on land, validation. *Has that we
lack:* calibrated global trade-flow allocation across 1,300 ports, asset-level multi-hazard risk, and the EU
regional accounts at NUTS2.

*Honourable mentions.* Pichler et al. 2022 (production rule and the only other ex-post validated dynamic
model); Diem et al. 2022/2024 (observed national network; size of the aggregation bias); Chen et al. 2025
and Chen & Cheng 2024 (the only other economic models of a low-water event, CGE with barge rates and a
barge-to-rail result); Mohajerani 2025 (generic spatial ABM with hazard coupling and adaptive firms, no
transport); Ivanov 2020 (discrete-event digital twin with lanes and inventories, for one firm's chain).

---

## 4. Draft state-of-the-art paragraph for the Introduction

Replace the current paragraph at main.tex line 56 (or insert before it). Keys: existing `refs.bib` keys where
they exist, otherwise the keys of the BibTeX block in section 5.

Models of disaster propagation through production networks have grown along three lines. Dynamic
input--output models descended from ARIO follow production, orders and inventories for the sectors or
region--sectors of an economy over weeks and months, and have been applied to hurricanes, floods, heat and
the pandemic from the regional to the global scale \citep{hallegatte2008,hallegatte2014,guan2020,wang2021wildfires,mendozatinoco2020flood,sun2024heat};
the Acclimate family adds endogenous prices and the reallocation of demand among the sectors of some 190
countries, with transport entering as a delivery delay \citep{otto2017,willner2018floods,kuhla2021resonance,middelanis2023stressed}.
Firm-level agent-based models run the same dynamics on observed buyer--supplier networks of a quarter of a
million to over a million firms, in Japan and Hungary, and show that aggregation to industries understates
losses and overstates substitution \citep{inoue2019,inoue2023establishments,diem2022,diem2024aggregation};
they have no geography of transport, and such networks exist for a handful of countries \citep{pichler2023alliance,bacilieri2026networks}.
A third line couples hazard and infrastructure networks to regional economic models---power and transport
in Britain \citep{thacker2017systems,koks2019electricity}, ports and shipping lanes worldwide \citep{verschuur2022criticality,verschuur2023systemic},
river floods across the regions of Europe \citep{koks2019floods,vanniyaperumal2026mria}---with static or
annual economics and without firms. Inland waterways in particular have been costed with inoperability and
general-equilibrium models of the Mississippi and Arkansas systems \citep{mackenzie2012,pant2015waterway,welch2022,chen2025mississippi},
in which the river enters as a price or a lost flow rather than as a capacity that shipments compete for
week after week. Our earlier work closed part of this gap by routing every shipment of a firm-level model on
a national road network \citep{colon2021}; here we extend it to a continent, to several modes, cargo classes
and the capacity of a waterway, and we test it on an observed episode. The equilibrium literature on
production networks and on transport in spatial economies \citep{acemoglu2012network,baqaee2019,carvalho2019primer,allen2022transportation,fajgelbaum2020networks}
provides the long-run benchmark; the short-run elasticities it needs for a season are not those it estimates
over years \citep{boehm2019,bonadio2021}.

(About 290 words; trim the last two sentences if the Introduction is tight. For the Discussion, the two-trough
result should cite \citep{kuhla2021resonance,middelanis2023stressed}, the services result \citep{mendozatinoco2020flood,koks2019floods},
and the rail result \citep{chen2024mississippi,meuchelboeck2025lowwater}.)

---

## 5. BibTeX block (verified entries not already in refs.bib)

Given names are from the Crossref/OpenAlex records where present, otherwise from the publisher page or
the author's known full name; entries whose author list could not be completed carry a `note`. Preprints are
`@misc`; reports `@techreport`/`@book`. Excluded on purpose: Kotz et al. 2024 (retracted), the SSRN items
(unverified or only index-listed; see `horst2024rhine` note), the disrupt-sc.io applications page.

```bibtex
@article{bierkandt2014acclimate,
  author  = {Bierkandt, Robert and Wenz, Leonie and Willner, Sven N. and Levermann, Anders},
  title   = {Acclimate---a model for economic damage propagation. {Part} 1: basic formulation of damage transfer within a global supply network and damage conserving dynamics},
  journal = {Environment Systems and Decisions},
  volume  = {34},
  number  = {4},
  pages   = {507--524},
  year    = {2014},
  doi     = {10.1007/s10669-014-9523-4}
}

@article{wenz2014acclimate,
  author  = {Wenz, Leonie and Willner, Sven N. and Bierkandt, Robert and Levermann, Anders},
  title   = {Acclimate---a model for economic damage propagation. {Part} {II}: a dynamic formulation of the backward effects of disaster-induced production failures in the global supply network},
  journal = {Environment Systems and Decisions},
  volume  = {34},
  number  = {4},
  pages   = {525--539},
  year    = {2014},
  doi     = {10.1007/s10669-014-9521-6}
}

@article{willner2018floods,
  author  = {Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Global economic response to river floods},
  journal = {Nature Climate Change},
  volume  = {8},
  number  = {7},
  pages   = {594--598},
  year    = {2018},
  doi     = {10.1038/s41558-018-0173-2}
}

@article{kuhla2021resonance,
  author  = {Kuhla, Kilian and Willner, Sven N. and Otto, Christian and Geiger, Tobias and Levermann, Anders},
  title   = {Ripple resonance amplifies economic welfare loss from weather extremes},
  journal = {Environmental Research Letters},
  volume  = {16},
  number  = {11},
  pages   = {114010},
  year    = {2021},
  doi     = {10.1088/1748-9326/ac2932}
}

@article{kuhla2021heat,
  author  = {Kuhla, Kilian and Willner, Sven N. and Otto, Christian and Wenz, Leonie and Levermann, Anders},
  title   = {Future heat stress to reduce people's purchasing power},
  journal = {PLOS ONE},
  volume  = {16},
  number  = {6},
  pages   = {e0251210},
  year    = {2021},
  doi     = {10.1371/journal.pone.0251210}
}

@article{middelanis2021sandy,
  author  = {Middelanis, Robin and Willner, Sven N. and Otto, Christian and Kuhla, Kilian and Quante, Lennart and Levermann, Anders},
  title   = {Wave-like global economic ripple response to {Hurricane} {Sandy}},
  journal = {Environmental Research Letters},
  volume  = {16},
  number  = {12},
  pages   = {124049},
  year    = {2021},
  doi     = {10.1088/1748-9326/ac39c0}
}

@article{middelanis2022hurricanes,
  author  = {Middelanis, Robin and Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Economic losses from hurricanes cannot be nationally offset under unabated warming},
  journal = {Environmental Research Letters},
  volume  = {17},
  number  = {10},
  pages   = {104013},
  year    = {2022},
  doi     = {10.1088/1748-9326/ac90d8}
}

@article{middelanis2023stressed,
  author  = {Middelanis, Robin and Willner, Sven N. and Kuhla, Kilian and Quante, Lennart and Otto, Christian and Levermann, Anders},
  title   = {Stressed economies respond more strongly to climate extremes},
  journal = {Environmental Research Letters},
  volume  = {18},
  number  = {9},
  pages   = {094034},
  year    = {2023},
  doi     = {10.1088/1748-9326/acec5e}
}

@article{kuhla2023typhoon,
  author  = {Kuhla, Kilian and Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Resilience of international trade to typhoon-related supply disruptions},
  journal = {Journal of Economic Dynamics and Control},
  volume  = {151},
  pages   = {104663},
  year    = {2023},
  doi     = {10.1016/j.jedc.2023.104663}
}

@article{quante2024variability,
  author  = {Quante, Lennart and Willner, Sven N. and Otto, Christian and Levermann, Anders},
  title   = {Global economic impact of weather variability on the rich and the poor},
  journal = {Nature Sustainability},
  volume  = {7},
  number  = {11},
  pages   = {1419--1428},
  year    = {2024},
  doi     = {10.1038/s41893-024-01430-7}
}

@article{inoue2019plos,
  author  = {Inoue, Hiroyasu and Todo, Yasuyuki},
  title   = {Propagation of negative shocks across nation-wide firm networks},
  journal = {PLOS ONE},
  volume  = {14},
  number  = {3},
  pages   = {e0213648},
  year    = {2019},
  doi     = {10.1371/journal.pone.0213648}
}

@article{hallegatte2019disasters,
  author  = {Hallegatte, St{\'e}phane},
  title   = {Disasters' impacts on supply chains},
  journal = {Nature Sustainability},
  volume  = {2},
  number  = {9},
  pages   = {791--792},
  year    = {2019},
  doi     = {10.1038/s41893-019-0380-5}
}

@article{inoue2020lockdown,
  author  = {Inoue, Hiroyasu and Todo, Yasuyuki},
  title   = {The propagation of economic impacts through supply chains: the case of a mega-city lockdown to prevent the spread of {COVID-19}},
  journal = {PLOS ONE},
  volume  = {15},
  number  = {9},
  pages   = {e0239251},
  year    = {2020},
  doi     = {10.1371/journal.pone.0239251}
}

@article{inoue2021lockdowns,
  author  = {Inoue, Hiroyasu and Murase, Yohsuke and Todo, Yasuyuki},
  title   = {Do economic effects of the anti-{COVID-19} lockdowns in different regions interact through supply chains?},
  journal = {PLOS ONE},
  volume  = {16},
  number  = {7},
  pages   = {e0255031},
  year    = {2021},
  doi     = {10.1371/journal.pone.0255031}
}

@article{inoue2023establishments,
  author  = {Inoue, Hiroyasu and Okumura, Yoshiyuki and Torayashiki, Tetsuya and Todo, Yasuyuki},
  title   = {Simulation of supply chain disruptions considering establishments and power outages},
  journal = {PLOS ONE},
  volume  = {18},
  number  = {7},
  pages   = {e0288062},
  year    = {2023},
  doi     = {10.1371/journal.pone.0288062}
}

@article{inoue2023trade,
  author  = {Inoue, Hiroyasu and Todo, Yasuyuki},
  title   = {Disruption of international trade and its propagation through firm-level domestic supply chains: a case of {Japan}},
  journal = {PLOS ONE},
  volume  = {18},
  pages   = {e0294574},
  year    = {2023},
  doi     = {10.1371/journal.pone.0294574}
}

@misc{inoue2024establishment,
  author       = {Inoue, Hiroyasu and Todo, Yasuyuki},
  title        = {Beyond firms and industries: shock propagation through establishment- and product-level supply chains},
  year         = {2024},
  howpublished = {arXiv:2410.05595, v4 (December 2025)},
  doi          = {10.48550/arXiv.2410.05595}
}

@article{kashiwagi2021sandy,
  author  = {Kashiwagi, Yuzuka and Todo, Yasuyuki and Matous, Petr},
  title   = {Propagation of economic shocks through global supply chains---evidence from {Hurricane} {Sandy}},
  journal = {Review of International Economics},
  volume  = {29},
  number  = {5},
  pages   = {1186--1220},
  year    = {2021},
  doi     = {10.1111/roie.12541}
}

@misc{rolf2026automotive,
  author       = {Rolf, Benjamin and Inoue, Hiroyasu and Lang, Sebastian},
  title        = {Agent-based disruption simulation on an edge-level product-annotated supply network of the automotive industry},
  year         = {2026},
  howpublished = {arXiv:2611.01706},
  doi          = {10.48550/arXiv.2611.01706}
}

@article{henriet2012network,
  author  = {Henriet, Fanny and Hallegatte, St{\'e}phane and Tabourier, Lionel},
  title   = {Firm-network characteristics and economic robustness to natural disasters},
  journal = {Journal of Economic Dynamics and Control},
  volume  = {36},
  number  = {1},
  pages   = {150--167},
  year    = {2012},
  doi     = {10.1016/j.jedc.2011.10.001}
}

@article{wang2021wildfires,
  author  = {Wang, Daoping and Guan, Dabo and Zhu, Shupeng and Mac Kinnon, Michael and Geng, Guannan and Zhang, Qiang and Zheng, Heran and Lei, Tianyang and Shao, Shuai and Gong, Peng and Davis, Steven J.},
  title   = {Economic footprint of {California} wildfires in 2018},
  journal = {Nature Sustainability},
  volume  = {4},
  number  = {3},
  pages   = {252--260},
  year    = {2021},
  doi     = {10.1038/s41893-020-00646-7}
}

@article{mendozatinoco2020flood,
  author  = {Mendoza-Tinoco, David and Hu, Yixin and Zeng, Zhao and Chalvatzis, Konstantinos J. and Zhang, Ning and Steenge, Albert E. and Guan, Dabo},
  title   = {Flood footprint assessment: a multiregional case of 2009 {Central} {European} floods},
  journal = {Risk Analysis},
  volume  = {40},
  number  = {8},
  pages   = {1612--1631},
  year    = {2020},
  doi     = {10.1111/risa.13497}
}

@article{sun2024heat,
  author  = {Sun, Yida and Zhu, Shupeng and Wang, Daoping and Duan, Jianping and Lu, Hui and Yin, Hao and Tan, Chang and Zhang, Lingrui and Zhao, Mengzhen and Cai, Wenjia and Wang, Yong and Hu, Yixin and Tao, Shu and Guan, Dabo},
  title   = {Global supply chains amplify economic costs of future extreme heat risk},
  journal = {Nature},
  volume  = {627},
  number  = {8005},
  pages   = {797--804},
  year    = {2024},
  doi     = {10.1038/s41586-024-07147-z}
}

@article{fang2026urban,
  author  = {Fang and Xu and Jin and Song and Gao and Sun and Wang and Feng},
  title   = {Stress-testing the cascading economic impacts of urban flooding across 306 {Chinese} cities},
  journal = {Nature Cities},
  volume  = {3},
  number  = {1},
  pages   = {89--101},
  year    = {2026},
  doi     = {10.1038/s44284-025-00372-1},
  note    = {Author given names to be completed from the publisher page (Crossref record lists surnames only in the fetched summary)}
}

@article{lenzen2019cyclone,
  author  = {Lenzen, Manfred and Malik, Arunima and Kenway, Steven and Daniels, Peter and Lam, Ka Leung and Geschke, Arne},
  title   = {Economic damage and spillovers from a tropical cyclone},
  journal = {Natural Hazards and Earth System Sciences},
  volume  = {19},
  number  = {1},
  pages   = {137--151},
  year    = {2019},
  doi     = {10.5194/nhess-19-137-2019}
}

@article{shughrue2020cyclone,
  author  = {Shughrue, Chris and Werner, B. T. and Seto, Karen C.},
  title   = {Global spread of local cyclone damages through urban trade networks},
  journal = {Nature Sustainability},
  volume  = {3},
  number  = {8},
  pages   = {606--613},
  year    = {2020},
  doi     = {10.1038/s41893-020-0523-8}
}

@article{oosterhaven2017flooding,
  author  = {Oosterhaven, Jan and T{\"o}bben, Johannes},
  title   = {Wider economic impacts of heavy flooding in {Germany}: a non-linear programming approach},
  journal = {Spatial Economic Analysis},
  volume  = {12},
  number  = {4},
  pages   = {404--428},
  year    = {2017},
  doi     = {10.1080/17421772.2017.1300680}
}

@article{oosterhaven2016disruptive,
  author  = {Oosterhaven, Jan and Bouwmeester, Maaike C.},
  title   = {A new approach to modeling the impact of disruptive events},
  journal = {Journal of Regional Science},
  volume  = {56},
  number  = {4},
  pages   = {583--595},
  year    = {2016},
  doi     = {10.1111/jors.12262}
}

@article{diem2024aggregation,
  author  = {Diem, Christian and Borsos, Andr{\'a}s and Reisch, Tobias and Kert{\'e}sz, J{\'a}nos and Thurner, Stefan},
  title   = {Estimating the loss of economic predictability from aggregating firm-level production networks},
  journal = {PNAS Nexus},
  volume  = {3},
  number  = {3},
  pages   = {pgae064},
  year    = {2024},
  doi     = {10.1093/pnasnexus/pgae064}
}

@article{chakraborty2024inequality,
  author  = {Chakraborty, Abhijit and Reisch, Tobias and Diem, Christian and Astudillo-Est{\'e}vez, Pablo and Thurner, Stefan},
  title   = {Inequality in economic shock exposures across the global firm-level supply network},
  journal = {Nature Communications},
  volume  = {15},
  pages   = {3348},
  year    = {2024},
  doi     = {10.1038/s41467-024-46126-w}
}

@article{stangl2024decarbonization,
  author  = {Stangl, Johannes and Borsos, Andr{\'a}s and Diem, Christian and Reisch, Tobias and Thurner, Stefan},
  title   = {Firm-level supply chains to minimize unemployment and economic losses in rapid decarbonization scenarios},
  journal = {Nature Sustainability},
  volume  = {7},
  number  = {5},
  pages   = {581--589},
  year    = {2024},
  doi     = {10.1038/s41893-024-01321-x}
}

@article{reisch2022mobile,
  author  = {Reisch, Tobias and Heiler, Georg and Diem, Christian and Klimek, Peter and Thurner, Stefan},
  title   = {Monitoring supply networks from mobile phone data for estimating the systemic risk of an economy},
  journal = {Scientific Reports},
  volume  = {12},
  pages   = {13347},
  year    = {2022},
  doi     = {10.1038/s41598-022-13104-5}
}

@article{pichler2023alliance,
  author  = {Pichler, Anton and Diem, Christian and Brintrup, Alexandra and Lafond, Fran{\c{c}}ois and Magerman, Glenn and Buiten, Gert and Choi, Thomas Y. and Carvalho, Vasco M. and Farmer, J. Doyne and Thurner, Stefan},
  title   = {Building an alliance to map global supply networks},
  journal = {Science},
  volume  = {382},
  number  = {6668},
  pages   = {270--272},
  year    = {2023},
  doi     = {10.1126/science.adi7521}
}

@article{bacilieri2026networks,
  author  = {Bacilieri, Andrea and Borsos, Andr{\'a}s and Astudillo-Est{\'e}vez, Pablo and Hoefer, Mads and Lafond, Fran{\c{c}}ois},
  title   = {Firm-level production networks: what do we (really) know?},
  journal = {Journal of Economic Dynamics and Control},
  volume  = {187},
  pages   = {105313},
  year    = {2026},
  doi     = {10.1016/j.jedc.2026.105313}
}

@article{ialongo2022reconstructing,
  author  = {Ialongo, Leonardo Niccol{\`o} and de Valk, Camille and Marchese, Emiliano and Jansen, Fabian and Zmarrou, Hicham and Squartini, Tiziano and Garlaschelli, Diego},
  title   = {Reconstructing firm-level interactions in the {Dutch} input--output network from production constraints},
  journal = {Scientific Reports},
  volume  = {12},
  pages   = {11847},
  year    = {2022},
  doi     = {10.1038/s41598-022-13996-3}
}

@article{mungo2023reconstructing,
  author  = {Mungo, Luca and Lafond, Fran{\c{c}}ois and Astudillo-Est{\'e}vez, Pablo and Farmer, J. Doyne},
  title   = {Reconstructing production networks using machine learning},
  journal = {Journal of Economic Dynamics and Control},
  volume  = {148},
  pages   = {104607},
  year    = {2023},
  doi     = {10.1016/j.jedc.2023.104607}
}

@misc{fialkowski2026cascades,
  author       = {Fialkowski, Jan and Havlin, Shlomo and Thurner, Stefan},
  title        = {Catastrophic disruption cascades driven by the nonlinearity of systemic risk},
  year         = {2026},
  howpublished = {arXiv:2607.20068},
  doi          = {10.48550/arXiv.2607.20068}
}

@misc{hurt2025agentbased,
  author       = {Hurt, Jan and Thurner, Stefan and Klimek, Peter},
  title        = {An agent-based extension to sector-wise input-output recovery models},
  year         = {2025},
  howpublished = {arXiv:2505.10146},
  doi          = {10.48550/arXiv.2505.10146}
}

@article{pichler2022simultaneous,
  author  = {Pichler, Anton and Farmer, J. Doyne},
  title   = {Simultaneous supply and demand constraints in input--output networks: the case of {Covid-19} in {Germany}, {Italy}, and {Spain}},
  journal = {Economic Systems Research},
  volume  = {34},
  number  = {3},
  pages   = {273--293},
  year    = {2022},
  doi     = {10.1080/09535314.2021.1926934}
}

@article{delriochanona2020shocks,
  author  = {del Rio-Chanona, R. Maria and Mealy, Penny and Pichler, Anton and Lafond, Fran{\c{c}}ois and Farmer, J. Doyne},
  title   = {Supply and demand shocks in the {COVID-19} pandemic: an industry and occupation perspective},
  journal = {Oxford Review of Economic Policy},
  volume  = {36},
  number  = {Supplement_1},
  pages   = {S94--S137},
  year    = {2020},
  doi     = {10.1093/oxrep/graa033}
}

@article{mandel2020lockdowns,
  author  = {Mandel, Antoine and Veetil, Vipin},
  title   = {The economic cost of {COVID} lockdowns: an out-of-equilibrium analysis},
  journal = {Economics of Disasters and Climate Change},
  volume  = {4},
  number  = {3},
  pages   = {431--451},
  year    = {2020},
  doi     = {10.1007/s41885-020-00066-z}
}

@article{baqaee2022keynesian,
  author  = {Baqaee, David and Farhi, Emmanuel},
  title   = {Supply and demand in disaggregated {Keynesian} economies with an application to the {COVID-19} crisis},
  journal = {American Economic Review},
  volume  = {112},
  number  = {5},
  pages   = {1397--1436},
  year    = {2022},
  doi     = {10.1257/aer.20201229}
}

@article{thacker2017systems,
  author  = {Thacker, Scott and Pant, Raghav and Hall, Jim W.},
  title   = {System-of-systems formulation and disruption analysis for multi-scale critical national infrastructures},
  journal = {Reliability Engineering \& System Safety},
  volume  = {167},
  pages   = {30--41},
  year    = {2017},
  doi     = {10.1016/j.ress.2017.04.023}
}

@article{pant2016rail,
  author  = {Pant, Raghav and Hall, Jim W. and Blainey, Simon P.},
  title   = {Vulnerability assessment framework for interdependent critical infrastructures: case-study for {Great Britain}'s rail network},
  journal = {European Journal of Transport and Infrastructure Research},
  volume  = {16},
  number  = {1},
  year    = {2016},
  doi     = {10.18757/ejtir.2016.16.1.3120}
}

@article{koks2019electricity,
  author  = {Koks, Elco E. and Pant, Raghav and Thacker, Scott and Hall, Jim W.},
  title   = {Understanding business disruption and economic losses due to electricity failures and flooding},
  journal = {International Journal of Disaster Risk Science},
  volume  = {10},
  number  = {4},
  pages   = {421--438},
  year    = {2019},
  doi     = {10.1007/s13753-019-00236-y}
}

@article{koks2019floods,
  author  = {Koks, Elco E. and Thissen, Mark and Alfieri, Lorenzo and de Moel, Hans and Feyen, Luc and Jongman, Brenden and Aerts, Jeroen C. J. H.},
  title   = {The macroeconomic impacts of future river flooding in {Europe}},
  journal = {Environmental Research Letters},
  volume  = {14},
  number  = {8},
  pages   = {084042},
  year    = {2019},
  doi     = {10.1088/1748-9326/ab3306}
}

@article{koks2016comparing,
  author  = {Koks, Elco E. and Carrera, Lorenzo and Jonkeren, Olaf and Aerts, Jeroen C. J. H. and Husby, Trond G. and Thissen, Mark and Standardi, Gabriele and Mysiak, Jaroslav},
  title   = {Regional disaster impact analysis: comparing input--output and computable general equilibrium models},
  journal = {Natural Hazards and Earth System Sciences},
  volume  = {16},
  number  = {8},
  pages   = {1911--1924},
  year    = {2016},
  doi     = {10.5194/nhess-16-1911-2016}
}

@article{vanniyaperumal2026mria,
  author  = {Vanniya Perumal, Surender Raj and Thissen, Mark and de Ruiter, Marleen and Koks, Elco E.},
  title   = {The effect of trade capacity constraints on disaster impacts: extending the {Multi-Regional} {Impact} {Assessment} ({MRIA}) model},
  journal = {Economic Systems Research},
  pages   = {1--24},
  year    = {2026},
  doi     = {10.1080/09535314.2026.2728049},
  note    = {Online first; preprint arXiv:2508.00510}
}

@article{verschuur2020ports,
  author  = {Verschuur, Jasper and Koks, Elco E. and Hall, Jim W.},
  title   = {Port disruptions due to natural disasters: insights into port and logistics resilience},
  journal = {Transportation Research Part D: Transport and Environment},
  volume  = {85},
  pages   = {102393},
  year    = {2020},
  doi     = {10.1016/j.trd.2020.102393}
}

@article{verschuur2022criticality,
  author  = {Verschuur, Jasper and Koks, Elco E. and Hall, Jim W.},
  title   = {Ports' criticality in international trade and global supply-chains},
  journal = {Nature Communications},
  volume  = {13},
  pages   = {4351},
  year    = {2022},
  doi     = {10.1038/s41467-022-32070-0}
}

@article{verschuur2023multihazard,
  author  = {Verschuur, Jasper and Koks, Elco E. and Li, Sihan and Hall, Jim W.},
  title   = {Multi-hazard risk to global port infrastructure and resulting trade and logistics losses},
  journal = {Communications Earth \& Environment},
  volume  = {4},
  pages   = {5},
  year    = {2023},
  doi     = {10.1038/s43247-022-00656-7}
}

@article{verschuur2023systemic,
  author  = {Verschuur, Jasper and Koks, Elco E. and Hall, Jim W.},
  title   = {Systemic risks from climate-related disruptions at ports},
  journal = {Nature Climate Change},
  volume  = {13},
  number  = {8},
  pages   = {804--806},
  year    = {2023},
  doi     = {10.1038/s41558-023-01754-w}
}

@article{pant2011terminals,
  author  = {Pant, Raghav and Barker, Kash and Grant, F. Hank and Landers, Thomas L.},
  title   = {Interdependent impacts of inoperability at multi-modal transportation container terminals},
  journal = {Transportation Research Part E: Logistics and Transportation Review},
  volume  = {47},
  number  = {5},
  pages   = {722--737},
  year    = {2011},
  doi     = {10.1016/j.tre.2011.02.009}
}

@article{pant2015waterway,
  author  = {Pant, Raghav and Barker, Kash and Landers, Thomas L.},
  title   = {Dynamic impacts of commodity flow disruptions in inland waterway networks},
  journal = {Computers \& Industrial Engineering},
  volume  = {89},
  pages   = {137--149},
  year    = {2015},
  doi     = {10.1016/j.cie.2014.11.016}
}

@article{oztanriseven2017waterway,
  author  = {Oztanriseven, Furkan and Nachtmann, Heather},
  title   = {Economic impact analysis of inland waterway disruption response},
  journal = {The Engineering Economist},
  volume  = {62},
  number  = {1},
  pages   = {73--89},
  year    = {2017},
  doi     = {10.1080/0013791X.2016.1163627}
}

@article{chen2024mississippi,
  author  = {Chen and Cheng},
  title   = {Economic consequences of inland waterway disruptions in the {Upper} {Mississippi} {River} region in a changing climate},
  journal = {The Annals of Regional Science},
  volume  = {73},
  number  = {2},
  pages   = {757--794},
  year    = {2024},
  doi     = {10.1007/s00168-024-01283-0},
  note    = {Author given names to be completed from the publisher page}
}

@article{chen2025mississippi,
  author  = {Chen and Rose and Roberts and Tucci},
  title   = {Regional supply-chain impacts of {Mississippi} {River} fertilizer shipments disrupted by climate change},
  journal = {Risk Analysis},
  volume  = {45},
  number  = {10},
  pages   = {3090--3109},
  year    = {2025},
  doi     = {10.1111/risa.70064},
  note    = {Author given names to be completed from the publisher page}
}

@article{rose2013port,
  author  = {Rose, Adam and Wei, Dan},
  title   = {Estimating the economic consequences of a port shutdown: the special role of resilience},
  journal = {Economic Systems Research},
  volume  = {25},
  number  = {2},
  pages   = {212--232},
  year    = {2013},
  doi     = {10.1080/09535314.2012.731379}
}

@article{tsuchiya2007disruptions,
  author  = {Tsuchiya, Satoshi and Tatano, Hirokazu and Okada, Norio},
  title   = {Economic loss assessment due to railroad and highway disruptions},
  journal = {Economic Systems Research},
  volume  = {19},
  number  = {2},
  pages   = {147--162},
  year    = {2007},
  doi     = {10.1080/09535310701328567}
}

@article{kajitani2018scge,
  author  = {Kajitani, Yoshio and Tatano, Hirokazu},
  title   = {Applicability of a spatial computable general equilibrium model to assess the short-term economic impact of natural disasters},
  journal = {Economic Systems Research},
  volume  = {30},
  number  = {3},
  pages   = {289--312},
  year    = {2018},
  doi     = {10.1080/09535314.2017.1369010}
}

@article{carrera2015flood,
  author  = {Carrera, Lorenzo and Standardi, Gabriele and Bosello, Francesco and Mysiak, Jaroslav},
  title   = {Assessing direct and indirect economic impacts of a flood event through the integration of spatial and computable general equilibrium modelling},
  journal = {Environmental Modelling \& Software},
  volume  = {63},
  pages   = {109--122},
  year    = {2015},
  doi     = {10.1016/j.envsoft.2014.09.016}
}

@article{haraguchi2015thailand,
  author  = {Haraguchi, Masahiko and Lall, Upmanu},
  title   = {Flood risks and impacts: a case study of {Thailand}'s floods in 2011 and research questions for supply chain decision making},
  journal = {International Journal of Disaster Risk Reduction},
  volume  = {14},
  pages   = {256--272},
  year    = {2015},
  doi     = {10.1016/j.ijdrr.2014.09.005}
}

@article{snyder2016review,
  author  = {Snyder, Lawrence V. and Atan, Z{\"u}mb{\"u}l and Peng, Peng and Rong, Ying and Schmitt, Amanda J. and Sinsoysal, Burcu},
  title   = {{OR/MS} models for supply chain disruptions: a review},
  journal = {IIE Transactions},
  volume  = {48},
  number  = {2},
  pages   = {89--109},
  year    = {2016},
  doi     = {10.1080/0740817X.2015.1067735}
}

@article{dolgui2018ripple,
  author  = {Dolgui, Alexandre and Ivanov, Dmitry and Sokolov, Boris},
  title   = {Ripple effect in the supply chain: an analysis and recent literature},
  journal = {International Journal of Production Research},
  volume  = {56},
  number  = {1-2},
  pages   = {414--430},
  year    = {2018},
  doi     = {10.1080/00207543.2017.1387680}
}

@article{ivanov2020epidemic,
  author  = {Ivanov, Dmitry},
  title   = {Predicting the impacts of epidemic outbreaks on global supply chains: a simulation-based analysis on the coronavirus outbreak ({COVID-19/SARS-CoV-2}) case},
  journal = {Transportation Research Part E: Logistics and Transportation Review},
  volume  = {136},
  pages   = {101922},
  year    = {2020},
  doi     = {10.1016/j.tre.2020.101922}
}

@article{ivanov2021twin,
  author  = {Ivanov, Dmitry and Dolgui, Alexandre},
  title   = {A digital supply chain twin for managing the disruption risks and resilience in the era of {Industry} 4.0},
  journal = {Production Planning \& Control},
  volume  = {32},
  number  = {9},
  pages   = {775--788},
  year    = {2021},
  doi     = {10.1080/09537287.2020.1768450}
}

@article{simchilevi2015automotive,
  author  = {Simchi-Levi, David and Schmidt, William and Wei, Yehua and Zhang, Peter Yun and Combs, Keith and Ge, Yao and Gusikhin, Oleg and Sanders, Michael and Zhang, Don},
  title   = {Identifying risks and mitigating disruptions in the automotive supply chain},
  journal = {Interfaces},
  volume  = {45},
  number  = {5},
  pages   = {375--390},
  year    = {2015},
  doi     = {10.1287/inte.2015.0804}
}

@article{acemoglu2012network,
  author  = {Acemoglu, Daron and Carvalho, Vasco M. and Ozdaglar, Asuman and Tahbaz-Salehi, Alireza},
  title   = {The network origins of aggregate fluctuations},
  journal = {Econometrica},
  volume  = {80},
  number  = {5},
  pages   = {1977--2016},
  year    = {2012},
  doi     = {10.3982/ECTA9623}
}

@article{carvalho2019primer,
  author  = {Carvalho, Vasco M. and Tahbaz-Salehi, Alireza},
  title   = {Production networks: a primer},
  journal = {Annual Review of Economics},
  volume  = {11},
  pages   = {635--663},
  year    = {2019},
  doi     = {10.1146/annurev-economics-080218-030212}
}

@article{allen2022transportation,
  author  = {Allen, Treb and Arkolakis, Costas},
  title   = {The welfare effects of transportation infrastructure improvements},
  journal = {The Review of Economic Studies},
  volume  = {89},
  number  = {6},
  pages   = {2911--2957},
  year    = {2022},
  doi     = {10.1093/restud/rdac001}
}

@article{fajgelbaum2020networks,
  author  = {Fajgelbaum, Pablo D. and Schaal, Edouard},
  title   = {Optimal transport networks in spatial equilibrium},
  journal = {Econometrica},
  volume  = {88},
  number  = {4},
  pages   = {1411--1452},
  year    = {2020},
  doi     = {10.3982/ECTA15213}
}

@incollection{redding2015transportation,
  author    = {Redding, Stephen J. and Turner, Matthew A.},
  title     = {Transportation costs and the spatial organization of economic activity},
  booktitle = {Handbook of Regional and Urban Economics},
  volume    = {5},
  pages     = {1339--1398},
  publisher = {Elsevier},
  year      = {2015},
  doi       = {10.1016/B978-0-444-59531-7.00020-X}
}

@article{redding2017quantitative,
  author  = {Redding, Stephen J. and Rossi-Hansberg, Esteban},
  title   = {Quantitative spatial economics},
  journal = {Annual Review of Economics},
  volume  = {9},
  pages   = {21--58},
  year    = {2017},
  doi     = {10.1146/annurev-economics-063016-103713}
}

@article{okuyama2014disaster,
  author  = {Okuyama, Yasuhide and Santos, Joost R.},
  title   = {Disaster impact and input--output analysis},
  journal = {Economic Systems Research},
  volume  = {26},
  number  = {1},
  pages   = {1--12},
  year    = {2014},
  doi     = {10.1080/09535314.2013.871505}
}

@article{botzen2019review,
  author  = {Botzen, W. J. Wouter and Deschenes, Olivier and Sanders, Mark},
  title   = {The economic impacts of natural disasters: a review of models and empirical studies},
  journal = {Review of Environmental Economics and Policy},
  volume  = {13},
  number  = {2},
  pages   = {167--188},
  year    = {2019},
  doi     = {10.1093/reep/rez004}
}

@article{galbusera2018inputoutput,
  author  = {Galbusera, Luca and Giannopoulos, Georgios},
  title   = {On input-output economic models in disaster impact assessment},
  journal = {International Journal of Disaster Risk Reduction},
  volume  = {30},
  pages   = {186--198},
  year    = {2018},
  doi     = {10.1016/j.ijdrr.2018.04.030}
}

@article{colon2023systemic,
  author  = {Colon, C{\'e}lian and Hochrainer-Stigler, Stefan},
  title   = {Systemic risks in supply chains: a need for system-level governance},
  journal = {Supply Chain Management: An International Journal},
  volume  = {28},
  number  = {4},
  pages   = {682--694},
  year    = {2023},
  doi     = {10.1108/SCM-03-2022-0101}
}

@article{pankratz2024climate,
  author  = {Pankratz, Nora M. C. and Schiller, Christoph M.},
  title   = {Climate change and adaptation in global supply-chain networks},
  journal = {The Review of Financial Studies},
  volume  = {37},
  number  = {6},
  pages   = {1729--1777},
  year    = {2024},
  doi     = {10.1093/rfs/hhad093}
}

@book{hallegatte2019lifelines,
  author    = {Hallegatte, St{\'e}phane and Rentschler, Jun and Rozenberg, Julie},
  title     = {Lifelines: the resilient infrastructure opportunity},
  publisher = {World Bank},
  address   = {Washington, DC},
  year      = {2019},
  doi       = {10.1596/978-1-4648-1430-3}
}

@book{wang2024cambodia,
  author    = {Wang, B. and Colon, C{\'e}lian},
  title     = {Cambodia: geospatial analysis for resilient road accessibility for human development and logistic supply},
  publisher = {World Bank},
  address   = {Washington, DC},
  series    = {Resilient Transport Series},
  year      = {2024},
  doi       = {10.1596/41974}
}

@misc{nobile2025cambodia,
  author       = {Nobile, Elisa Grazia Lucia and Colon, C{\'e}lian},
  title        = {Assessing the cascading economic impacts of critical infrastructure failures on supply-chains: a case study of {Cambodia} floods},
  year         = {2025},
  howpublished = {EGU General Assembly 2025, Vienna, abstract EGU25-19090, \url{https://meetingorganizer.copernicus.org/EGU25/EGU25-19090.html}},
  note         = {Abstract DOI not verified}
}

@techreport{meuchelboeck2025lowwater,
  author      = {Meuchelb{\"o}ck, Saskia},
  title       = {Navigating supply chain disruptions: how firms respond to low water levels},
  institution = {Kiel Institute for the World Economy (RETHINK-GSC working paper)},
  year        = {2025},
  month       = aug,
  url         = {https://www.kielinstitut.de/publications/navigating-supply-chain-disruptions-how-firms-respond-to-low-water-levels-34581}
}

@misc{horst2024rhine,
  author       = {Horst, Bjarne and M{\"u}ller, Yann},
  title        = {Quantifying waterway supply chain shocks: regional propagation in the {Rhine} area},
  year         = {2024},
  howpublished = {SSRN 4818090},
  note         = {Seen only in an index listing (OUCI); SSRN page not fetched - verify before citing}
}

@misc{mohajerani2025cascading,
  author       = {Mohajerani, Yara},
  title        = {Modelling cascading physical climate risk in supply chains with adaptive firms: a spatial agent-based framework},
  year         = {2025},
  howpublished = {arXiv:2509.18633, v4 (April 2026)},
  doi          = {10.48550/arXiv.2509.18633}
}
```

---

## 6. Method and limits of this pass

Sources: Crossref DOI records for every DOI above (fetched 7 Nov 2026); arXiv abstract pages for the five
preprints; publisher/institutional pages for the Kiel working paper, the World Bank report (via Crossref),
the EGU abstract and the DisruptSC applications page; OpenAlex for abstracts Crossref lacked; web search
(standard/extended) for discovery. SSRN (403) and IIASA PURE (bot wall) could not be fetched; nature.com
redirects to a login, so Nature-family abstracts came from Crossref, OpenAlex, PIK records or press
releases. Time steps and inventory rules marked n.v. are from memory or the local dossiers, not re-read
today. No file other than this one was modified; nothing was committed.
