# Positioning: European transport-disruption modelling and the economics of Rhine low water

Strand of the literature positioning for "Logistics under drought: how the Rhine low water of
2026 propagates through Europe's supply chains" (Nature Communications draft, 7 November 2026).

Scope of this file. Part A: Europe-wide transport-network and freight models, climate risk to
European transport infrastructure, transport vulnerability studies, each with whether and how it
reaches the economy. Part B: the economics of Rhine and inland-waterway low water, from the
Jonkeren/Beuthe/JRC line to the ex-post statistics of 2018, the thin record of 2022 and the
ex-ante and realised numbers of 2026. The sibling files cover the rest and are not repeated:
`positioning_model_state_of_art_20261107.md` (supply-chain propagation models, US inland-waterway
economic models, Verschuur/Koks/NISMOD, Meuchelboeck 2025, Horst and Mueller 2024) and
`positioning_scoop_recent_20261107.md` (recency sweep 2023-2026, the 2026 timeline, Kiel KKB 137,
Gemeinschaftsdiagnose, Bundesbank October 2026, Destatis, ECB speeches and blog, ECB OP 380).

Verification. Every work below was checked today against its Crossref record [CR], its DataCite
record [DC] or its publisher or institutional landing page or PDF [LP]; items known only through
a news report are tagged [S]; anything not verified is tagged [U] and is not in the BibTeX block.
Numbers quoted from reports were read in the PDFs (Kiel Box 2018.17, Kriedel 2019, Streng et al.
2020, KKB 137, Gemeinschaftsdiagnose Herbst 2026, DIW Wochenbericht 36/2026, KfW notes, Bundesbank
Monthly Reports of November and December 2018 and October 2022, Meuchelboeck 2025) or on the
cited pages. No file other than this one was modified.

---

## 0. Already cited in refs.bib (not re-reported) and flags

Already cited in main.tex or si.tex and in scope here: jonkeren2007, jonkeren2011, jonkeren2014,
beuthe2014, christodoulou2020, vandorsser2020, vinke2022, ademmer2019, ademmer2023, ccnr2019,
ccnr2023, icpr2020, dihk2026, ifw2026, bfg2026, contargo2026, dbcargo2026, baw2026, bmv2019,
pichler2022, colon2021, hallegatte2008, hallegatte2014, otto2017, inoue2019, guan2020.

In refs.bib but cited nowhere (main.tex and si.tex checked): ademmer2020, bedoyamaya2024,
gobert2023, koks2016, koks2019, mackenzie2012, scholten2014, turpijn2026, vinke2023, welch2022
(and, outside this strand, bachmann2022, baqaee2019, barrot2016, basf2019, bonadio2021, diem2022,
wenz2016).

Flags for the manuscript (line numbers of main.tex as read today):

1. Line 50, "Statistical studies made after the event put the cost at about 1% of German
   industrial production for each month of low water, which left GDP about 0.3-0.4% below its
   path at the trough \citep{ademmer2023,ademmer2019}". The 1 % per month is Ademmer et al.;
   the GDP figure in Ademmer et al. (2023) is about 0.4 % (described there as a lower bound).
   The 0.3 comes from the ING note of 4 August 2026 and from Coface, not from the two cited
   works; either write "about 0.4%" or add the ING note as the source of the lower figure.
   Kriedel (CCNR, 2019) gives a third ex-post number, EUR 4.68 bn or 0.63 % of German
   industrial production over the second half of 2018, and Streng et al. (2020) EUR 2.4 bn for
   Germany; both are usable as the "ex-post band" and neither is in the paper.
2. Line 48, vinke2022: the cascade in Vinke et al. (2022) is simulated for the Rotterdam-Duisburg
   (Lower Rhine) container fleet, not for the Kaub reach; the sentence should not imply a Kaub
   study. vinke2023 (Climate Risk Management 43, 2024: ten years of Rhine fleet response to
   discharge extremes) is the better source for "how the fleet responds at Kaub" and is in the
   bib unused.
3. Line 54, "Transport economics ... evaluates extra freight costs and the shift between rail and
   road \citep{jonkeren2007,jonkeren2011,jonkeren2014,beuthe2014,christodoulou2020}": accurate.
   Jonkeren et al. (2007) is a welfare (freight-price) study, Jonkeren et al. (2011) and Beuthe
   et al. (2014) are NODUS modal-split studies, Christodoulou et al. (2020) a JRC LISFLOOD-based
   projection of low-water days and transport costs; the sentence could say "freight prices,
   loading restrictions and modal shift" to cover all five.
4. scholten2014 (Scholten, Rothstein and Baumhauer, Climatic Change 122, 2014: vulnerability of
   bulk-cargo companies along the Rhine to low water, including their stockholding and switching
   options) is in the bib, unused, and is the one published study that frames the firm-level
   inventory question the paper makes central; worth citing in the Methods or Discussion.
5. jonkeren2007 and jonkeren2011 have no doi field; verified DOIs are 10.3828/jtep.2007.41.3.387
   and 10.1016/j.tra.2009.01.004.
6. ademmer2020 (Kiel Working Paper 2155) is the working-paper version of ademmer2023; keep one.
7. Across the three strand files the same work appears under two keys; reconcile before import:
   meuchelboeck2025lowwater (state of the art) and meuchelboeck2025navigating (scoop);
   verschuur2022criticality and verschuur2022ports; quante2024variability and quante2024weather;
   kuhla2021resonance and kuhla2021ripple. Keys in this file were chosen not to collide.
8. No Rhine-specific Pichler paper exists; the Pichler et al. (2022) production-function paper is
   already cited (pichler2022). Nothing to add.

---

## 1. One-page synthesis

### Part A. Europe-wide transport models and climate risk to European transport

The European transport-model family was built for policy appraisal and forecasting, not for
hazards. NODUS (Jourquin and Beuthe 1996; Jourquin and Limbourg 2006) assigns multimodal freight
on a "virtual network" by generalised cost; TRANS-TOOLS (Nielsen and Burgess 2008; Hansen and Rich
2010) and its successor TRIMODE (Fiorello et al. 2018; Siskos et al. 2019) are the Commission's
EU-wide passenger and freight models, with an economic module that serves policy scenarios
(pricing, infrastructure, technology); ETISplus (FP7 project 233596, 2009-2012) is the origin-
destination and network database behind them; RHOMOLO (Brandsma et al. 2015) is the spatial CGE
at NUTS-2 level into which transport enters as a cost (Persyn et al. 2022). None of these has a
hazard module. The disruption uses that exist are: NODUS applied to Rhine and Danube low water
(Jonkeren et al. 2011; Beuthe et al. 2014, both cited), which stop at transport costs and modal
shift; and van der Tuin and Pel (2020), who run infrastructure-failure scenarios on a European
multimodal network and report user delays. The FP7 projects WEATHER and EWENT (Michaelides et al.
2014; Doll et al. 2014; Schweighofer 2014; Leviaekangas and Michaelides 2014) costed weather
extremes for European transport by mode, including inland waterways, as direct damage, delay and
operating cost; no production or trade propagation.

The climate-risk literature on European transport infrastructure is an exposure and direct-damage
literature: Forzieri et al. (2018) for all critical infrastructure (expected annual damage about
tenfold by the 2080s from EUR 3.4 bn per year), Bubeck et al. (2019) for railways and floods,
van Ginkel et al. (2021, 2022) for the road network and floods, Mulholland and Feyen (2021) for
heat on roads and railways, the JRC reports of Nemry and Demirel (2012), Demirel et al. (2015),
Christodoulou and Demirel (2018), Christodoulou et al. (2019, 2020), the Commission's TEN-T
adaptation study (Schade et al. 2024: about EUR 71 bn of adaptation investment to mid-century),
and the 2026 review by Deidda et al. The economy enters this literature in three ways only:
(i) multiregional input-output propagation of flood damage (Koks and Thissen 2016; Koks et al.
2019 ERL, both MRIA at NUTS-2, annual, no transport network); (ii) spatial CGE for policy, not for
events (RHOMOLO); (iii) static trade or input-output dependence at ports (Verschuur et al. 2022,
2023; Izaguirre et al. 2021; covered in the state-of-the-art file). Transport vulnerability
analysis (Jenelius et al. 2006; Jenelius and Mattsson 2012, 2015; Mattsson and Jenelius 2015;
Besinovic 2020 for rail) ranks links by generalised-cost or delay consequences and has no
economic layer at all. Koks et al. (2022) on the July 2021 flood shows the same: infrastructure
impacts documented, economy not propagated.

What is therefore absent in the European literature is a model in which the shipment is the unit:
every firm-to-firm flow routed on the real multimodal network, a hazard that changes link capacity
or cost, and production that falls when inputs do not arrive and inventories run out. The paper's
claim "first to route every EU shipment and let stock-outs propagate" is consistent with this
record; the nearest European relatives are the two NODUS low-water studies (transport only) and the
MRIA flood studies (economy only, annual, no routing).

### Part B. Rhine and inland-waterway economics: the benchmark

Transport economics of Rhine low water. Jonkeren, Rietveld and van Ommeren (2007, 2008) priced
low water through the freight-rate response at Kaub (welfare loss); Jonkeren et al. (2011) and
Beuthe et al. (2014) put it in NODUS (modal shift, transport cost); Jonkeren et al. (2014)
projected economic consequences under climate scenarios; Hendrickx and Breemersch (2012, ECCONET)
built the impact chain; Riquelme-Solar et al. (2015) and van Slobbe et al. (2016) turned it into
adaptation turning points; Scholten et al. (2014) surveyed the exposed bulk-cargo firms; Scholten,
Rothstein and Pistocchi (2017) did the Danube equivalent for the JRC; van Dorsser et al. (2020),
Vinke et al. (2022, 2024), Bedoya-Maya et al. (2023, 2024) and Turpijn et al. (2026) supply the
loading-capacity, fleet-response and freight-data physics. Hydrology and forecasting that this
economics rests on: Goergen et al. (2010, RheinBlick2050), Nilson et al. (2014, KLIWAS 4.01),
Meissner et al. (2017), Ionita and Nagavciuc (2020), van Tiel et al. (2023), Christodoulou et al.
(2020). All of this stops at the waterway: freight rates, loading factors, modal shift, transport
cost. None follows the missing cargo into production.

Ex-post statistics for 2018 (the benchmark the paper validates against). Kiel Box 2018.17
(Ademmer, Jannsen, Kooths and Moesle, December 2018): one low-water day lowers monthly inland-
waterway tonnage by 0.76 % and the growth of producing-sector output by just under 0.04
percentage points; the low water alone took more than 0.5 pp off production growth in Q3 2018 and
just under 0.5 pp in Q4. Ademmer, Jannsen and Meuchelboeck (2020 WP; 2023 German Economic Review,
cited): 30 low-water days cost about 1 % of industrial production; 2018 as a whole about 1.5 % of
industrial production at the trough and about 0.4 % of GDP, a lower bound. Kriedel (CCNR, 26
November 2019): 0.039 pp of industrial-production growth per low-water day at Kaub (lag 0.032),
EUR 4.68 bn in Q3-Q4 2018, 0.63 % of German industrial production in that half-year. Streng, van
Saase and Kuipers (Erasmus UPT, April 2020, for CBRB and BLN-Schuttevaer): financial impact of
2018 about EUR 2.4 bn in Germany (of which EUR 2.1 bn lost production) and about EUR 0.3 bn in the
Netherlands, EUR 2.7-2.8 bn in total; indirect effects explicitly not quantified. Meuchelboeck
(2025): inland-waterway exports -18.5 % and imports -12 % during the episode; exposed firms'
exports -3.6 %; the import modal shift persisted (details in the state-of-the-art file). The
Bundesbank published no 2018 box: the Monthly Reports of November and December 2018 do not treat
the low water (the dossier's "-0.2 pp Q3 2018" attribution remains untraceable); the October 2022
report notes that chemicals and coke/refining output in August 2022 was held back by the strong
low water on the Rhine. No ECB Economic Bulletin box on the Rhine was found for 2018 or 2022, and
no ex-post estimate exists for 2022 at all.

2026. Ex-ante estimates cluster tightly: ING (4 August) at least -0.3 pp of 2026 GDP growth; IW
(Schaefer, 4 August, via Bild/ZDF) -0.4 pp; KfW (12 August) industrial production -1 % in the
quarter, GDP growth -0.2 %; Kiel KKB 137 (completed 2 September) producing sector -1.2 % in Q3,
GDP -0.3 % ceteris paribus, -0.2 pp adopted; Gemeinschaftsdiagnose (17 September) 30 low-water
days = -0.7 to -1.2 % of producing-sector output, Q3 GDP +0.1 %, exports -0.2 %; DIW (September)
and Bundesbank (21 October) Q3 stagnation; ECB (Elderson, 14 and 26 October) "up to 0.2
percentage points of GDP in the third quarter"; Lagarde (4 November) "small and temporary". The
outcome: Destatis flash of 30 October, Q3 GDP +0.2 % q/q (+1.3 % y/y), with exports markedly
weaker and investment down; production of 6 November, Q3 -0.4 % against Q2 and energy-intensive
branches -3.5 % against Q2 (-1.9 % y/y in September), September +0.7 % m/m. Every published
estimate is a reduced-form elasticity of aggregate output to low-water days; none is sectoral,
regional or cross-border, and none says where the loss landed or why 2026 differed from 2018.
That is the gap between the benchmark literature and the paper.

---

## 2. Table of works

Columns: work | venue, identifier, verification | region and scale | hazard | method class |
economy represented how (none / transport cost or trade model / IO or CGE) | key numbers |
one-line relevance to the positioning.

### A1. European freight and transport models

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Jourquin and Beuthe 1996, Transportation policy analysis with a GIS: the virtual network of freight transportation in Europe | Transp. Res. C 4(6):359-371; doi 10.1016/s0968-090x(96)00019-8 [CR] | Europe, multimodal freight network | none | NODUS virtual-network assignment, generalised cost | none (fixed OD demand) | - | Origin of the model later used for Rhine low water (Jonkeren 2011, Beuthe 2014): transport cost and mode only |
| Jourquin and Limbourg 2006, Equilibrium traffic assignment on large virtual networks | EJTIR 6(3); doi 10.18757/ejtir.2006.6.3.3446 [CR] | Europe | none | equilibrium assignment, multimodal freight | none | - | Shows the assignment class our routing is compared with: no shipper, no inventory |
| Beuthe, Jourquin, Geerts and Koul a Ndjang' Ha 2001, Freight transportation demand elasticities | Transp. Res. E 37(4):253-266; doi 10.1016/s1366-5545(00)00022-3 [CR] | Belgium, multimodal | none | NODUS, cost elasticities | transport cost | - | Elasticity tradition behind modal-shift estimates |
| de Jong et al. 2004, A meta-model for passenger and freight transport in Europe | Transport Policy 11; doi 10.1016/s0967-070x(04)00017-4 [CR] | Europe | none | meta-model (policy response surfaces) | none | - | Pre-TRANS-TOOLS generation of EU models: policy, not events |
| Nielsen and Burgess 2008, The European TRANS-TOOLS transport model | TRB Annual Meeting; DTU Orbit record [LP] | EU, TEN-T | none | network model, passenger and freight, with regional-economic module | IO/CGE-type module for policy appraisal | - | The Commission's reference model until TRIMODE; never run for hazards |
| Hansen and Rich 2010, Trans-Tools | in FREIGHTVISION (Springer), pp. 43-62; doi 10.1007/978-3-642-13371-8_4 [CR] | EU | none | model description | as above | - | Documentation of TRANS-TOOLS freight side |
| Fiorello, Noekel and Martino 2018, The TRIMODE integrated model for Europe | Transp. Res. Procedia 31:88-98; doi 10.1016/j.trpro.2018.09.048 [CR] | EU27+, NUTS-3 | none | integrated transport-energy-economy model for policy scenarios | macro module for policy (not events) | - | Current EU model: still no disruption or inventory logic |
| Siskos, Capros, Zazias, Fiorello and Noekel 2019, Energy and fleet modelling within TRIMODE | Transp. Res. Procedia 37:369-376; doi 10.1016/j.trpro.2018.12.205 [CR] | EU | none | fleet and energy module | via macro module | - | Confirms the policy orientation of TRIMODE |
| ETISplus (FP7 grant 233596, Panteia, 2009-2012) | CORDIS project page [LP]; deliverable reports [U] | EU | none | OD and network database for EU transport modelling | none | - | Data layer of the EU models; no disruption use found |
| Brandsma, Kancs, Monfort and Rillaers 2015, RHOMOLO: a dynamic spatial general equilibrium model | Papers in Regional Science 94:S197-S222; doi 10.1111/pirs.12162 [CR] | EU NUTS-2 | none | spatial CGE | CGE (prices clear markets) | - | The EU economy-wide model; transport is a cost parameter, no network, no rationing |
| Persyn, Diaz-Lanchas and Barbero 2022, Estimating road transport costs between and within EU regions | Transport Policy 124:33-42; doi 10.1016/j.tranpol.2020.04.006 [CR] | EU NUTS-2 | none | network-based transport-cost matrix for RHOMOLO | feeds CGE | - | How transport enters RHOMOLO: cost, not capacity |
| van der Tuin and Pel 2020, The disruption transport model: computing user delays from infrastructure failures | Eur. Transp. Res. Rev. 12:8; doi 10.1186/s12544-020-0398-9 [CR] | Europe, multimodal passenger and freight | infrastructure failure (generic) | network assignment under link failure | none (user delays) | - | Closest European "disruption" transport model: outputs delays, not production |

### A2. Extreme-weather cost projects for European transport (WEATHER, EWENT, ECCONET)

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Michaelides, Leviaekangas, Doll and Heyndrickx 2014, Foreword: EU-funded projects on extreme weather challenging European transport systems | Natural Hazards 72:5-22; doi 10.1007/s11069-013-1007-1 [CR] | EU | all weather extremes | synthesis of WEATHER, EWENT, ECCONET and others | cost accounting | - | Maps the FP7 generation: costs by mode, no propagation |
| Doll, Klug and Enei 2014, Large and small numbers: costs of extremes on transport now and in 40 years | Natural Hazards 72:211-239; doi 10.1007/s11069-013-0821-9 [CR] | EU-27, by mode | heat, cold, floods, storms, low water | bottom-up cost accounting (damage, delay, accidents) | cost model only | - | The "transport-only" cost benchmark; explicitly excludes indirect production losses |
| Schweighofer 2014, The impact of extreme weather and climate change on inland waterway transport | Natural Hazards 72:23-40; doi 10.1007/s11069-012-0541-6 [CR] | Rhine, Danube, EU waterways | low water, ice, floods | impact chains, adaptation options | none | - | Transport-side review of IWT and low water; no economy |
| Leviaekangas and Michaelides 2014, Transport system management under extreme weather risks | Natural Hazards 72:263-286; doi 10.1007/s11069-013-0970-x [CR] | EU | weather extremes | appraisal and asset-management framing | cost | - | Management view; no supply chain |
| Hendrickx and Breemersch 2012, The effect of climate change on inland waterway transport (ECCONET) | Procedia Soc. Behav. Sci. 48:1837-1847; doi 10.1016/j.sbspro.2012.06.1158 [CR] | Rhine-Main-Danube | low water (climate scenarios) | impact chain, transport cost | transport cost | - | ECCONET impact chain used by Beuthe 2014 |
| Koetse and Rietveld 2009, The impact of climate change and weather on transport: an overview of empirical findings | Transp. Res. D 14(3):205-221; doi 10.1016/j.trd.2008.12.004 [CR] | global, review | weather | review | transport cost | - | Standard review; IWT low water via Jonkeren |
| Koetse and Rietveld 2012, Adaptation to climate change in the transport sector | Transport Reviews 32(3):267-286; doi 10.1080/01441647.2012.657716 [CR] | review | climate | review | transport cost | - | Frames adaptation as a transport-cost problem |

### A3. Climate risk to European transport infrastructure (exposure and direct damage)

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Forzieri et al. 2018, Escalating impacts of climate extremes on critical infrastructures in Europe | Global Environ. Change 48:97-107; doi 10.1016/j.gloenvcha.2017.11.007 [CR] | EU+, all critical infrastructure incl. transport | seven hazards (incl. drought) | multi-hazard expected annual damage | none (direct damage) | EAD about tenfold by 2080s from EUR 3.4 bn/yr (abstract) | Reference exposure study; no supply-chain propagation |
| Bubeck, Dillenardt, Alfieri, Feyen, Thieken and Kellermann 2019, Global warming to increase flood risk on European railways | Climatic Change 155:19-36; doi 10.1007/s10584-019-02434-5 [CR] | EU rail | river floods | damage functions on rail assets | none | EAD of order EUR 0.6 bn/yr today, rising strongly with warming [check figures in paper] | Rail-flood counterpart; direct damage only |
| van Ginkel, Dottori, Alfieri, Feyen and Koks 2021, Flood risk assessment of the European road network | NHESS 21:1011-1027; doi 10.5194/nhess-21-1011-2021 [CR] | EU roads (OSM) | river floods | object-based damage | none | EAD of order EUR 0.2 bn/yr [check] | Road-flood counterpart |
| van Ginkel, Koks, de Groen, Nguyen and Alfieri 2022, Will river floods "tip" European road networks? | Transp. Res. D 108:103332; doi 10.1016/j.trd.2022.103332 [CR] | EU roads | river floods | network robustness (detour, disconnection) | none | - | Network consequence without economy; nearest to a "criticality" analysis in Europe |
| Mulholland and Feyen 2021, Increased risk of extreme heat to European roads and railways | Climate Risk Management 34:100365; doi 10.1016/j.crm.2021.100365 [CR] | EU roads and rail | heat | damage functions | none | - | Heat counterpart |
| Nemry and Demirel 2012, Impacts of climate change on transport: road and rail infrastructures | JRC EUR 25553 EN, JRC72217; doi 10.2791/15504 [LP, DOI not in Crossref] | EU | heat, floods, precipitation | infrastructure deterioration and damage costs | none | - | First JRC transport-climate report |
| Demirel, Kompil and Nemry 2015, Vulnerability of European road networks to sea-level rise and storm surges | Transp. Res. A 81:62-76; doi 10.1016/j.tra.2015.05.002 [CR] | EU coasts | SLR, surge | exposure framework | none | - | JRC exposure line |
| Christodoulou and Demirel 2018, Impacts of climate change on transport: airports, seaports and inland waterways | JRC EUR 28896 EN, JRC108865; doi 10.2760/378464 [LP, DOI not in Crossref] | EU | floods, droughts, SLR | exposure and cost | transport cost | - | JRC report that precedes christodoulou2020 (cited) |
| Christodoulou, Christidis and Demirel 2019, Sea-level rise in ports: a wider focus on impacts | Maritime Econ. Logist. 21:482-496; doi 10.1057/s41278-018-0114-z [CR] | EU ports | SLR | exposure, hinterland | trade exposure (static) | - | Port counterpart |
| Schade et al. 2024, Support study on the climate adaptation and cross-border investment needs to realise the TEN-T network | Publications Office, DG MOVE; doi 10.2832/7839720 [LP] | TEN-T | heat, river and coastal floods, wildfire | asset exposure and investment needs | none | about EUR 71 bn adaptation investment to mid-century (2023 prices) | Policy reference for TEN-T climate risk; infrastructure, not flows |
| Deidda et al. 2026, Europe's transport infrastructure is not ready to face climate change | NHESS 26:3345-3394; doi 10.5194/nhess-26-3345-2026 [CR]; BibTeX in scoop file (deidda2026transport) | Europe | multi-hazard | review | none | - | Latest review; confirms the field stops at infrastructure |
| Koks, van Ginkel, van Marle and Lemnitzer 2022, Critical infrastructure impacts of the 2021 mid-July western European flood | NHESS 22:3831-3838; doi 10.5194/nhess-22-3831-2022 [CR] | DE, BE, NL | flood | event documentation | none | - | Shows the event literature is descriptive on infrastructure |
| Koks et al. 2019, A global multi-hazard risk analysis of road and railway infrastructure assets | Nature Communications 10:2677; in bib (koks2019), uncited | global | multi-hazard | asset EAD | none | - | Already in bib; cite if the Introduction names the exposure literature |
| Izaguirre, Losada, Camus, Vigh and Stenek 2021, Climate change risk to global port operations | Nature Climate Change 11:14-20; doi 10.1038/s41558-020-00937-z [CR] | global ports | multi-hazard | operational risk index | none | - | Port exposure without trade propagation |

### A4. Where the economy enters: MRIA, CGE, port-trade dependence

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Koks and Thissen 2016, A multiregional impact assessment model for disaster analysis | Econ. Syst. Res. 28(4):429-449; in bib (koks2016), uncited | EU NUTS-2 | floods | MRIA (IO with substitution, LP) | IO | - | The European IO propagation model; annual, no transport network |
| Koks, Thissen, Alfieri, De Moel, Feyen, Jongman and Aerts 2019, The macroeconomic impacts of future river flooding in Europe | Environ. Res. Lett. 14:084042; doi 10.1088/1748-9326/ab3306 [CR] | EU NUTS-2 | river floods, climate scenarios | MRIA | IO | - | Only EU-wide hazard-to-economy propagation study; floods, annual, no routing or inventories |
| Verschuur, Koks and Hall 2022; Verschuur et al. 2023 (Commun. Earth Environ.; Nature Climate Change) | see state-of-the-art file (verschuur2022criticality etc.) | global ports | multi-hazard | port-level trade dependence, IO | static trade/IO | - | Port-side analogue of our chokepoint, at annual and national resolution |
| Hallegatte, Rentschler and Rozenberg 2019, Lifelines | World Bank; in state-of-the-art file (hallegatte2019lifelines) | global | multi-hazard | firm surveys, network criticality | partial | - | Frames infrastructure disruption as a firm-level cost |

### A5. Transport network vulnerability

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Jenelius, Petersen and Mattsson 2006, Importance and exposure in road network vulnerability analysis | Transp. Res. A 40(7):537-560; doi 10.1016/j.tra.2005.11.003 [CR] | Sweden roads | link closure | generalised-cost increase per closed link | none | - | Defines link importance by user cost; our criticality is by lost production (colon2021 lineage) |
| Jenelius and Mattsson 2012, Road network vulnerability analysis of area-covering disruptions | Transp. Res. A 46(5):746-760; doi 10.1016/j.tra.2012.02.003 [CR] | Sweden | area-wide disruption (e.g. flood, storm) | grid-based closure scenarios | none | - | Method for spatially extended hazards; still user cost |
| Jenelius and Mattsson 2015, Road network vulnerability analysis: conceptualization, implementation and application | Comput. Environ. Urban Syst. 49:136-147; doi 10.1016/j.compenvurbsys.2014.02.003 [CR] | Sweden | closures | framework | none | - | Consolidated method |
| Mattsson and Jenelius 2015, Vulnerability and resilience of transport systems: a discussion of recent research | Transp. Res. A 81:16-34; doi 10.1016/j.tra.2015.06.002 [CR] | review | all | review | none (notes the absence of economic layers) | - | The review itself names the gap between vulnerability analysis and economic impact |
| Besinovic 2020, Resilience in railway transport systems: a literature review and research agenda | Transport Reviews 40(4):457-478; doi 10.1080/01441647.2020.1728419 [CR] | rail, review | disruptions | review | none | - | Rail resilience literature: operations, not economy |

### B1. Transport economics of Rhine and inland-waterway low water

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Jonkeren, van Ommeren and Rietveld 2008, Effects of low water levels on the river Rhine on the inland waterway transport sector | in Economics and Management of Climate Change (Springer), pp. 53-64; doi 10.1007/978-0-387-77353-7_5 [CR; year from the book] | Kaub market | low water | freight-rate regression, welfare | transport price | - | Chapter version of jonkeren2007 (cited); nothing new to cite |
| Riquelme-Solar, van Slobbe and Werners 2015, Adaptation turning points on inland waterway transport in the Rhine River | J. Water Clim. Change 6(4):670-682; doi 10.2166/wcc.2014.091 [CR] | Rhine | low water (climate scenarios) | adaptation turning points, stakeholder thresholds | transport cost | - | Thresholds at which barge transport stops being viable; no production |
| van Slobbe, Werners, Riquelme-Solar, Boelscher and van Vliet 2016, The future of the Rhine: stranded ships and no more salmon? | Reg. Environ. Change 16:31-41; doi 10.1007/s10113-014-0683-z [CR] | Rhine | low water, temperature | turning points | none | - | Same line, broader |
| Scholten, Rothstein and Pistocchi 2017, Navigation on the Danube: limitations by low water levels and their impacts | JRC EUR 28374 EN, JRC104224; doi 10.2788/236234 [LP, DOI not in Crossref]; the dossier lists it as 2016 with two authors | Danube | low water | threshold and price regressions, transport cost | transport cost | - | Danube counterpart; same stopping point |
| Bedoya-Maya, Beckers and van Hassel 2023, Spillover effects from inland waterway transport development: Rhine-Alpine corridor | J. Transp. Geogr. 113:103721; doi 10.1016/j.jtrangeo.2023.103721 [CR] | Rhine-Alpine corridor, NUTS-3 | none (development) | spatial econometrics | regional growth | - | Only regional-economic study of the corridor; not a disruption study |
| Bedoya-Maya et al. 2024 (bib bedoyamaya2024); Vinke et al. 2024 (bib vinke2023); Turpijn et al. 2026 (bib turpijn2026); van Dorsser et al. 2020 (cited); Scholten et al. 2014 (bib scholten2014); Gobert and Rudolf 2023 (bib gobert2023) | in refs.bib | Rhine | low water | loading physics, fleet response, freight data, firm survey, governance | none to transport cost | - | Already in bib; see flags 2 and 4 |

### B2. Hydrology and forecasting used by the economics

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Goergen et al. 2010, Assessment of climate change impacts on discharge in the Rhine River Basin: results of the RheinBlick2050 project | CHR report I-23, Lelystad; KNMI publication page [LP] | Rhine basin | low and high flows | ensemble hydrological projections | none | - | Source of the "more frequent summer low flows late century" statement |
| Nilson et al. 2014, Auswirkungen des Klimawandels auf das Abflussgeschehen und die Binnenschifffahrt in Deutschland (KLIWAS 4.01) | BfG KLIWAS-43/2014; doi 10.5675/Kliwas_43/2014_4.01 [DC] | German waterways | low water | discharge projections, navigation indicators | none | - | BfG reference for low-water days under climate change |
| Meissner, Klein and Ionita 2017, A monthly to seasonal forecast framework tailored to inland waterway transport in central Europe | HESS 21:6401-6423; doi 10.5194/hess-21-6401-2017 [CR] | Rhine, Elbe, Danube | low water | seasonal forecasting | none | - | Basis of the BfG six-week product the paper uses (bfg2026) |
| Ionita and Nagavciuc 2020, Forecasting low flow conditions months in advance, with a special focus on summer 2018 | Scientific Reports 10:13258; doi 10.1038/s41598-020-70060-8 [CR] | central Europe | low flow 2018 | teleconnection forecasting | none | - | Predictability of 2018 |
| van Tiel et al. 2023, Melting Alpine water towers aggravate downstream low flows: a stress-test storyline approach | Earth's Future 11:e2022EF003408; doi 10.1029/2022ef003408 [CR] | Rhine (Basel to Kaub) | low flow 1976, 2003, 2018 storylines under warming | storylines | none | - | Why future low waters are deeper: glacier buffer loss |
| Campoverde et al. 2025, Drought propagation in the Rhine basin and its impact on navigation | EGUsphere preprint; doi 10.5194/egusphere-2025-3988 [CR]; BibTeX in scoop file | Rhine | drought | regional climate model dataset | none | - | Newest hydrology-to-navigation link |

### B3. Ex-post statistics of 2018

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Ademmer, Jannsen, Kooths and Moesle 2018, Zum Einfluss des Niedrigwassers auf die Konjunktur | IfW-Box 2018.17, Kiel Institute; PDF [LP] | Germany, monthly | low-water days at Kaub (< 78 cm) | distributed-lag regressions on tonnage and production | reduced-form macro | one low-water day: inland-waterway tonnage -0.76 % in the month; producing-sector growth just under -0.04 pp; Q3 2018 > -0.5 pp, Q4 2018 just under -0.5 pp | The first ex-post elasticity; the paper's 1 %/month descends from it |
| Ademmer, Jannsen, Kooths and Moesle 2019, Niedrigwasser bremst Produktion | Wirtschaftsdienst 99(1):79-80; doi 10.1007/s10273-019-2399-7 [CR]; cited (ademmer2019) | Germany | 2018 | as above | reduced-form | as above | Already cited |
| Ademmer, Jannsen and Meuchelboeck 2020 (KWP 2155) and 2023 (German Economic Review 24(2):121-144; doi 10.1515/ger-2022-0077) | in bib (ademmer2020 uncited; ademmer2023 cited) | Germany, monthly | low-water days | local projections | reduced-form | 30 days of low water: industrial production about -1 %; 2018: about -1.5 % of industrial production at the trough and about -0.4 % of GDP (lower bound) | The validation target; see flag 1 |
| Kriedel 2019, Macroeconomic effects of low water levels on the Rhine: a statistical analysis | CCNR presentation, BMVI workshop "Low waters and consequences on navigation of the Rhine", Bonn, 26 Nov 2019; PDF [LP] | Germany | low-water days at Kaub | regression on industrial production | reduced-form | -0.039 pp of production growth per low-water day (lag -0.032); index effect -0.02 pp per day; total Q3-Q4 2018 EUR 4.68 bn = 0.63 % of German industrial production in H2 2018 | Independent ex-post number of the same order; not in the paper |
| Streng, van Saase and Kuipers 2020, Economische impact laagwater | Erasmus UPT final report, April 2020, for CBRB and Koninklijke BLN-Schuttevaer; PDF [LP] | Netherlands and Germany, 2018 | low water | interviews and sector accounts (financial impact) | partial-equilibrium accounting; indirect effects not quantified | Germany about -EUR 2.4 bn (of which -2.1 bn lost production); Netherlands about -0.3 bn; total about -2.7 to -2.8 bn; barge-sector revenue up | Only Dutch-German cross-border estimate; explicitly stops before propagation |
| Meuchelboeck 2025, Navigating supply chain disruptions: how firms respond to low water levels | Kiel Working Paper; in both sibling files | German firms, customs data | 2018 | difference-in-differences | firm-level trade | inland-waterway exports -18.5 %, imports -12 %; highly exposed firms' exports -3.6 %; persistent import modal shift | Firm-level evidence that the shock reaches output and trade; the paper's mechanism at the micro level |
| Horst and Mueller 2024 | SSRN; state-of-the-art file (partially verified) | Germany | 2018 | - | - | - | See sibling file |
| CCNR 2019 Market observation (bib ccnr2019); ICPR 2020 (bib icpr2020) | cited | Rhine | 2018 | statistics | none | - | Already cited |

### B4. Central banks

| Work | Venue; identifier | Region/scale | Hazard | Method | Economy | Key numbers | Relevance |
|---|---|---|---|---|---|---|---|
| Deutsche Bundesbank, Monatsbericht November 2018 | PDF [LP] | Germany | - | - | - | no mention of Niedrigwasser or Pegelstaende | No 2018 box exists; the dossier's "-0.2 pp Q3 2018 (Bundesbank)" is untraceable |
| Deutsche Bundesbank, Monatsbericht Dezember 2018 | PDF [LP] | Germany | - | - | - | no low-water assessment (at most a passing remark) | Same |
| Deutsche Bundesbank, Monatsbericht Oktober 2022 | PDF [LP] | Germany | 2022 low water | narrative | - | August 2022 chemicals and coke/refining output "wohl zudem durch das starke Niedrigwasser unter anderem am Rhein" held back | Only Bundesbank statement on 2022; qualitative |
| Deutsche Bundesbank, Deutsche Wirtschaft auf Erholungskurs (Kurzbericht, Monatsbericht September 2026) | topic page, 21 Sep 2026 [LP] | Germany | 2026 | narrative | - | low water made transport harder, transport costs "kraeftig gestiegen" | Qualitative |
| Deutsche Bundesbank, Monatsbericht Oktober 2026, Kurzbericht Konjunkturlage | 21 Oct 2026 [LP]; BibTeX in scoop file (bundesbank2026october) | Germany | 2026 | narrative | - | Q3 2026 GDP "duerfte ... stagniert haben"; low Rhine levels and restricted shipping burdened industry, chemicals and coke/refining in particular; Rhine very low throughout September | The central bank's ex-ante Q3 call, later beaten by +0.2 % |
| ECB, Elderson, Ensuring resilience in the face of uncertainty (Frankfurt, 14 Oct 2026) | speech page [LP] | Germany/euro area | 2026 | - | - | footnote 6: Rhine "lowest since records began in 1880"; "could also reduce Germany's economic recovery by up to 0.2 percentage points of GDP in the third quarter" (no source given) | ECB's number |
| ECB, Elderson, Taking action for nature (Yerevan, 26 Oct 2026) | speech page [LP]; scoop file (elderson2026nature) | as above | 2026 | - | - | footnote 4, same sentence; 24 % of euro-area output at risk in a 1-in-100 drought (OP 380) | Same |
| ECB, Lagarde, A warning from Europe's hot summer (ECB Blog, 4 Nov 2026) | blog page [LP]; scoop file (lagarde2026summer) | euro area | 2026 | - | - | Rhine and Danube shipping disrupted; effect on euro-area activity small and temporary | Same |
| Ceglar et al. 2025, Nature at risk (ECB Occasional Paper 380) | RePEc record and ECB PDF [LP]; scoop file (ceglar2025nature) | euro area | drought | nature value-at-risk | sectoral production functions | surface-water scarcity: up to 24 % of euro-area output exposed under a 100-year drought | Exposure, not propagation; the number behind the ECB speeches |
| ECB Economic Bulletin boxes on the Rhine, 2018 and 2022 | searched, none found [U] | - | - | - | - | - | Gap confirmed |

### B5. 2022

| Work | Venue; identifier | Key content | Relevance |
|---|---|---|---|
| Bundesbank Monatsbericht Oktober 2022 | as above | August 2022 production in chemicals and refining held back by low water | Only official statement |
| ING THINK 2022, Record low Rhine levels another warning that supply chains must adapt | think.ing.com/opinions/... [LP] | commentary, no estimate | - |
| Ex-post statistical estimate for 2022 | none found [U] | - | The paper cannot be validated against 2022; say so |

### B6. 2026: ex-ante estimates and outcomes (numbers checked today; chronology in the scoop file)

| Date | Work | Identifier | Key numbers | Economy representation |
|---|---|---|---|---|
| 4 Aug 2026 | ING, Brzeski, Low water levels are new setback for the German economy | think.ing.com article [LP] | 2018: about -0.3 pp of GDP growth, -1 % industrial production per low-water month; 2026: "at least 0.3 percentage points" of GDP growth | Kiel elasticity times duration |
| 4 Aug 2026 | IW (Schaefer) via Bild, reported by ZDF | zdfheute article [S] | GDP growth 2026 could be 0.4 pp lower than expected | Statement; no method given |
| 12 Aug 2026 | KfW Research, Scheuermeyer, Konjunktur droht auf Grund zu laufen | KfW PDF [LP] | Kaub about 20 cm, record since 1969; 30 low-water days = -1 % industrial production (Kiel); a full quarter likely; GDP growth about -0.2 %; catch-up later | Kiel elasticity |
| 25 Aug 2026 | KfW-Konjunkturkompass August 2026 (Koerner, Schoenwald, Wanke) | KfW PDF [LP] | low water "the next damper"; no separate number | - |
| 2-3 Sep 2026 | Kiel Institute, Deutsche Wirtschaft im Herbst 2026 (KKB 137) | PDF [LP]; scoop file (kiel2026autumn) | 0.04 % production per low-water day (Ademmer 2023); producing sector -1.2 % in Q3; GDP -0.3 % ceteris paribus, -0.2 pp adopted; low water assumed over by end-September | Kiel elasticity |
| 3 Sep 2026 | RWI Konjunkturbericht press release | rwi-essen.de [LP] | "Niedrigwasser belastet Industrie und Bauwirtschaft"; 2026 GDP +1.3 %; no low-water number | - |
| 3 Sep 2026 | ifo Konjunkturprognose Herbst 2026 (Wollmershaeuser et al.), ifo Schnelldienst digital 7(15):1-19, box pp. 8ff | landing page [LP]; box content not retrieved (PDF served as stub); the Gemeinschaftsdiagnose cites it for the 0.7-1.2 % range; a search snippet gives about -0.1 pp for H2 [U] | see left | Kiel elasticity (per GD footnote) |
| Sep 2026 | DIW Wochenbericht 36/2026, Deutsche Wirtschaft waechst, aber nicht aus eigener Kraft | PDF [LP] | Q3 GDP stagnation expected; low water hampers production through input shortages and onward transport, above all export goods of chemicals and metals | Narrative |
| 17 Sep 2026 | Gemeinschaftsdiagnose Herbst 2026, Aufschwung mit Strukturproblemen | PDF [LP]; scoop file (gd2026autumn) | 30 low-water days in a month = producing-sector output -0.7 to -1.2 % (citing Ademmer 2023 and the ifo box); July production -1.1 % m/m; Q3 GDP +0.1 %; Q3 exports -0.2 % | Kiel elasticity |
| 21 Sep, 21 Oct 2026 | Bundesbank | see B4 | Q3 stagnation expected | Narrative |
| 14 and 26 Oct 2026 | ECB Elderson | see B4 | up to -0.2 pp of GDP in Q3 | - |
| 30 Oct 2026 | Destatis press release 381, BIP im 3. Quartal 2026 | [LP]; scoop file (destatis2026q3gdp) | Q3 GDP +0.2 % q/q (price-, season-, calendar-adjusted); +1.3 % y/y (+1.2 % calendar-adjusted); exports "merklich" weaker; investment down | Outcome |
| 4 Nov 2026 | ECB Lagarde blog | see B4 | small and temporary | - |
| 6 Nov 2026 | Destatis press release 389, Produktion im September 2026 | [LP]; scoop file (destatis2026production) | September +0.7 % m/m (industry excl. energy and construction +1.7 %); Q3 vs Q2 -0.4 %; energy-intensive branches Q3 vs Q2 -3.5 %, September -1.9 % y/y; no mention of low water | Outcome |
| 14 Aug 2026 | Tooze, Chartbook 466: The straits of Kaub | substack [LP] | Rhine about 80 % of the 223 Mt moved by inland shipping in Germany, about 5 % of all freight; Kaub channel 20 cm shallower; rock removal "about eight months" of works, planned by 2033 | Commentary; no estimate |
| 29 Jul-4 Aug 2026 | DIHK Blitzumfrage (n = 170) | cited (dihk2026) | 33 % restrict production, 6 % stopped (dossier) | Survey |

### B7. Not reachable or not found

| Item | Status |
|---|---|
| ABN AMRO, "SustainaWeekly: the impact of low Rhine water levels on the Dutch economy" and "Ripple effects: exploring the impact of low Rhine water levels on the Dutch economy" | pages returned 503/timeout twice; known only from search summaries [U]; the only Dutch macro treatment of 2026 found, so worth a retry |
| Schymura blog post (22 Aug 2026, sector-panel analysis finding no stable output penalty) | known from a search snippet only; a targeted search today did not find the post [U]; not reported |
| ETISplus deliverables (final report, database documentation) | not located; only the CORDIS record [U] |
| Burgess et al. 2008 TRANS-TOOLS final report | not located; the DTU record (Nielsen and Burgess 2008) and Hansen and Rich 2010 stand in |
| van Dalen 2023 (Supply Chain Management) | no Crossref match; dropped |
| Bundesbank 2018 box; ECB Economic Bulletin boxes 2018/2022 | do not exist as far as the reports and searches show |
| ifo autumn 2026 box content | partially verified (see B6) |

---

## 3. Gaps our paper fills and does not fill

Fills (relative to Parts A and B):

1. Shipment-level routing of the whole EU27+CH economy on the real multimodal network with a
   hazard that changes waterway capacity: no European transport model (NODUS, TRANS-TOOLS,
   TRIMODE, RHOMOLO, the disruption transport model) carries production or inventories, and no
   European economic propagation model (MRIA, RHOMOLO) carries a network or sub-annual time.
2. Production losses from missing inputs rather than from transport cost: the entire Rhine
   transport-economics line (Jonkeren to Bedoya-Maya) measures freight prices, loading factors and
   modal shift; the paper is the first to convert them into stock-outs and lost output firm by
   firm, week by week, which is exactly the "indirect effects not quantified" of Streng et al.
   (2020) and the mechanism that Ademmer et al. and Kriedel estimate only in reduced form.
3. Decomposition that the reduced-form benchmarks cannot give: which sectors and countries bear
   the loss, how much lands outside Germany, the share in services, the dependence on the
   calendar and on the water-level profile, and the ranking of levers (inventories, modal
   capacity, loading rules), none of which any 2018 or 2026 estimate addresses.
4. A validated link to the ex-post benchmark: the paper reproduces the 2018 order of magnitude
   (1 % of industrial production per month; 0.4 % of GDP) and can be compared with three
   independent ex-post numbers (Ademmer, Kriedel, Streng), which should all be named.
5. A forecast made before the outcome: the 2026 ex-ante literature is a single elasticity applied
   to an assumed duration; the paper's distribution over hydrological ensembles is a different
   object, and the realised Q3 (+0.2 % GDP; production -0.4 % q/q; energy-intensive -3.5 % q/q)
   can be set against both.

Does not fill (state in the Discussion or Methods):

1. No 2022 benchmark exists, so the model's second historical check cannot be an ex-post
   macro number; only the Bundesbank's qualitative statement.
2. No Dutch, Belgian or Swiss ex-post economic estimate beyond Streng et al. (NL about EUR 0.3 bn
   in 2018); the paper's cross-border shares cannot be validated against data.
3. Persistence: Meuchelboeck (2025) shows modal shifts that outlast the event; the model's
   agents return to baseline routing, so long-run adaptation and competitiveness effects (also
   Scholten et al. 2014, Riquelme-Solar et al. 2015) are out of scope.
4. Prices: freight-rate surcharges (Jonkeren 2007; contargo2026) and CGE-type price adjustment
   (RHOMOLO) are not modelled; the paper's losses are quantity rationing. Say that the welfare
   loss of transport economics and the output loss here are different objects.
5. Hydrology: the paper takes BfG forecasts as given and does not couple the climate projections
   of low-water frequency (Nilson 2014; Christodoulou 2020; van Tiel 2023), so it says nothing
   about future return periods.
6. Infrastructure damage and the other hazards in the Forzieri/Deidda line (floods, heat on rail)
   are not in the model; the Rhine is a capacity shock on an intact network.
7. Transport-side physics is simpler than van Dorsser (2020) and Vinke (2022, 2024): loading
   factors by vessel class and fleet repositioning are parameterised, not simulated.

---

## 4. BibTeX block: verified entries not in refs.bib

Entries already provided by the sibling files are not repeated; reuse their keys:
deidda2026transport, campoverde2025drought, vanniyaperumal2026infrastructure, kiel2026autumn,
gd2026autumn, bundesbank2026october, destatis2026q3gdp, destatis2026production,
elderson2026nature, lagarde2026summer, ceglar2025nature, jannsen2026lowwater, prognos2026rhine,
ccnr2026lowwater, ccnr2026annual, bfg2026october (scoop file); verschuur2022criticality,
verschuur2023multihazard, verschuur2023systemic, hallegatte2019lifelines, koks2019floods,
meuchelboeck2025lowwater, horst2024rhine (state-of-the-art file). Note that koks2019floods in the
state-of-the-art file is the ERL paper also given here as koks2019flooding; keep one.

```bibtex
% ---------- A1. European freight and transport models ----------

@article{jourquin1996nodus,
  author  = {Jourquin, Bart and Beuthe, Michel},
  title   = {Transportation policy analysis with a geographic information system: the virtual network of freight transportation in {Europe}},
  journal = {Transportation Research Part C: Emerging Technologies},
  year    = {1996},
  volume  = {4},
  number  = {6},
  pages   = {359--371},
  doi     = {10.1016/s0968-090x(96)00019-8}
}

@article{jourquin2006assignment,
  author  = {Jourquin, Bart and Limbourg, Sabine},
  title   = {Equilibrium traffic assignment on large virtual networks: implementation issues and limits for multi-modal freight transport},
  journal = {European Journal of Transport and Infrastructure Research},
  year    = {2006},
  volume  = {6},
  number  = {3},
  doi     = {10.18757/ejtir.2006.6.3.3446}
}

@article{beuthe2001elasticities,
  author  = {Beuthe, Michel and Jourquin, Bart and Geerts, Jean-Fran{\c{c}}ois and {Koul {\`a} Ndjang' Ha}, Christian},
  title   = {Freight transportation demand elasticities: a geographic multimodal transportation network analysis},
  journal = {Transportation Research Part E: Logistics and Transportation Review},
  year    = {2001},
  volume  = {37},
  number  = {4},
  pages   = {253--266},
  doi     = {10.1016/s1366-5545(00)00022-3}
}

@article{dejong2004metamodel,
  author  = {de Jong, G.},
  title   = {A meta-model for passenger and freight transport in {Europe}},
  journal = {Transport Policy},
  year    = {2004},
  doi     = {10.1016/s0967-070x(04)00017-4},
  note    = {The Crossref record carries a single author and no volume or pages; complete from the journal issue before import}
}

@misc{nielsen2008transtools,
  author       = {Nielsen, Otto Anker and Burgess, Arnaud},
  title        = {The {European} {TRANS-TOOLS} transport model},
  year         = {2008},
  howpublished = {Transportation Research Board Annual Meeting, session 248; record at \url{https://orbit.dtu.dk/en/publications/the-european-trans-tools-transport-model/}; model page \url{https://www.tmleuven.be/en/navigation/TRANS-TOOLS}}
}

@incollection{hansen2010transtools,
  author    = {Hansen, Christian O. and Rich, Jeppe},
  title     = {{Trans-Tools}},
  booktitle = {{FREIGHTVISION} -- Sustainable {European} Freight Transport 2050},
  publisher = {Springer},
  address   = {Berlin, Heidelberg},
  year      = {2010},
  pages     = {43--62},
  doi       = {10.1007/978-3-642-13371-8_4}
}

@article{fiorello2018trimode,
  author  = {Fiorello, Davide and N{\"o}kel, Klaus and Martino, Angelo},
  title   = {The {TRIMODE} integrated model for {Europe}},
  journal = {Transportation Research Procedia},
  year    = {2018},
  volume  = {31},
  pages   = {88--98},
  doi     = {10.1016/j.trpro.2018.09.048}
}

@article{siskos2019trimode,
  author  = {Siskos, Pelopidas and Capros, Pantelis and Zazias, Georgios and Fiorello, Davide and N{\"o}kel, Klaus},
  title   = {Energy and fleet modelling within the {TRIMODE} integrated transport model framework for {Europe}},
  journal = {Transportation Research Procedia},
  year    = {2019},
  volume  = {37},
  pages   = {369--376},
  doi     = {10.1016/j.trpro.2018.12.205}
}

@misc{etisplus2012cordis,
  author       = {{Panteia and the ETISplus consortium}},
  title        = {{ETISplus}: {European} transport policy information system -- development and implementation of data collection methodology for {EU} transport modelling},
  year         = {2012},
  howpublished = {FP7-TRANSPORT grant 233596, 1 September 2009 -- 31 December 2012, CORDIS, \url{https://cordis.europa.eu/project/id/233596}}
}

@article{brandsma2015rhomolo,
  author  = {Brandsma, Andries and Kancs, d'Artis and Monfort, Philippe and Rillaers, Alexandra},
  title   = {{RHOMOLO}: a dynamic spatial general equilibrium model for assessing the impact of cohesion policy},
  journal = {Papers in Regional Science},
  year    = {2015},
  volume  = {94},
  number  = {S1},
  pages   = {S197--S222},
  doi     = {10.1111/pirs.12162}
}

@article{persyn2022transportcosts,
  author  = {Persyn, Damiaan and D{\'i}az-Lanchas, Jorge and Barbero, Javier},
  title   = {Estimating road transport costs between and within {European Union} regions},
  journal = {Transport Policy},
  year    = {2022},
  volume  = {124},
  pages   = {33--42},
  doi     = {10.1016/j.tranpol.2020.04.006}
}

@article{vandertuin2020disruption,
  author  = {van der Tuin, Marieke S. and Pel, Adam J.},
  title   = {The disruption transport model: computing user delays resulting from infrastructure failures for multi-modal passenger and freight traffic},
  journal = {European Transport Research Review},
  year    = {2020},
  volume  = {12},
  pages   = {8},
  doi     = {10.1186/s12544-020-0398-9}
}

% ---------- A2. Extreme-weather cost projects ----------

@article{michaelides2014foreword,
  author  = {Michaelides, S. and Levi{\"a}kangas, P. and Doll, C. and Heyndrickx, C.},
  title   = {Foreword: {EU}-funded projects on extreme and high-impact weather challenging {European} transport systems},
  journal = {Natural Hazards},
  year    = {2014},
  volume  = {72},
  number  = {1},
  pages   = {5--22},
  doi     = {10.1007/s11069-013-1007-1}
}

@article{doll2014costs,
  author  = {Doll, Claus and Klug, Stefan and Enei, Riccardo},
  title   = {Large and small numbers: options for quantifying the costs of extremes on transport now and in 40 years},
  journal = {Natural Hazards},
  year    = {2014},
  volume  = {72},
  number  = {1},
  pages   = {211--239},
  doi     = {10.1007/s11069-013-0821-9}
}

@article{schweighofer2014waterway,
  author  = {Schweighofer, Juha},
  title   = {The impact of extreme weather and climate change on inland waterway transport},
  journal = {Natural Hazards},
  year    = {2014},
  volume  = {72},
  number  = {1},
  pages   = {23--40},
  doi     = {10.1007/s11069-012-0541-6}
}

@article{leviakangas2014management,
  author  = {Levi{\"a}kangas, P. and Michaelides, S.},
  title   = {Transport system management under extreme weather risks: views to project appraisal, asset value protection and risk-aware system management},
  journal = {Natural Hazards},
  year    = {2014},
  volume  = {72},
  number  = {1},
  pages   = {263--286},
  doi     = {10.1007/s11069-013-0970-x}
}

@article{hendrickx2012ecconet,
  author  = {Hendrickx, Christophe and Breemersch, Tim},
  title   = {The effect of climate change on inland waterway transport},
  journal = {Procedia -- Social and Behavioral Sciences},
  year    = {2012},
  volume  = {48},
  pages   = {1837--1847},
  doi     = {10.1016/j.sbspro.2012.06.1158}
}

@article{koetse2009weather,
  author  = {Koetse, Mark J. and Rietveld, Piet},
  title   = {The impact of climate change and weather on transport: an overview of empirical findings},
  journal = {Transportation Research Part D: Transport and Environment},
  year    = {2009},
  volume  = {14},
  number  = {3},
  pages   = {205--221},
  doi     = {10.1016/j.trd.2008.12.004}
}

@article{koetse2012adaptation,
  author  = {Koetse, Mark J. and Rietveld, Piet},
  title   = {Adaptation to climate change in the transport sector},
  journal = {Transport Reviews},
  year    = {2012},
  volume  = {32},
  number  = {3},
  pages   = {267--286},
  doi     = {10.1080/01441647.2012.657716}
}

% ---------- A3. Climate risk to European transport infrastructure ----------

@article{forzieri2018infrastructures,
  author  = {Forzieri, Giovanni and Bianchi, Alessandra and Batista e Silva, Filipe and Marin Herrera, Mario A. and Leblois, Antoine and Lavalle, Carlo and Aerts, Jeroen C. J. H. and Feyen, Luc},
  title   = {Escalating impacts of climate extremes on critical infrastructures in {Europe}},
  journal = {Global Environmental Change},
  year    = {2018},
  volume  = {48},
  pages   = {97--107},
  doi     = {10.1016/j.gloenvcha.2017.11.007}
}

@article{bubeck2019railways,
  author  = {Bubeck, Philip and Dillenardt, Lisa and Alfieri, Lorenzo and Feyen, Luc and Thieken, Annegret H. and Kellermann, Patric},
  title   = {Global warming to increase flood risk on {European} railways},
  journal = {Climatic Change},
  year    = {2019},
  volume  = {155},
  number  = {1},
  pages   = {19--36},
  doi     = {10.1007/s10584-019-02434-5}
}

@article{vanginkel2021roads,
  author  = {van Ginkel, Kees C. H. and Dottori, Francesco and Alfieri, Lorenzo and Feyen, Luc and Koks, Elco E.},
  title   = {Flood risk assessment of the {European} road network},
  journal = {Natural Hazards and Earth System Sciences},
  year    = {2021},
  volume  = {21},
  number  = {3},
  pages   = {1011--1027},
  doi     = {10.5194/nhess-21-1011-2021}
}

@article{vanginkel2022tipping,
  author  = {van Ginkel, Kees C. H. and Koks, Elco E. and de Groen, Frederique and Nguyen, Viet Dung and Alfieri, Lorenzo},
  title   = {Will river floods `tip' {European} road networks? {A} robustness assessment},
  journal = {Transportation Research Part D: Transport and Environment},
  year    = {2022},
  volume  = {108},
  pages   = {103332},
  doi     = {10.1016/j.trd.2022.103332}
}

@article{mulholland2021heat,
  author  = {Mulholland, Eamonn and Feyen, Luc},
  title   = {Increased risk of extreme heat to {European} roads and railways with global warming},
  journal = {Climate Risk Management},
  year    = {2021},
  volume  = {34},
  pages   = {100365},
  doi     = {10.1016/j.crm.2021.100365}
}

@techreport{nemry2012jrc,
  author      = {Nemry, Fran{\c{c}}oise and Demirel, Hande},
  title       = {Impacts of climate change on transport: a focus on road and rail transport infrastructures},
  institution = {European Commission, Joint Research Centre},
  year        = {2012},
  number      = {EUR 25553 EN (JRC72217)},
  doi         = {10.2791/15504},
  url         = {https://publications.jrc.ec.europa.eu/repository/handle/JRC72217}
}

@article{demirel2015sealevel,
  author  = {Demirel, Hande and Kompil, Mert and Nemry, Fran{\c{c}}oise},
  title   = {A framework to analyze the vulnerability of {European} road networks due to sea-level rise ({SLR}) and sea storm surges},
  journal = {Transportation Research Part A: Policy and Practice},
  year    = {2015},
  volume  = {81},
  pages   = {62--76},
  doi     = {10.1016/j.tra.2015.05.002}
}

@techreport{christodoulou2018jrc,
  author      = {Christodoulou, Aris and Demirel, Hande},
  title       = {Impacts of climate change on transport: a focus on airports, seaports and inland waterways},
  institution = {European Commission, Joint Research Centre},
  year        = {2018},
  number      = {EUR 28896 EN (JRC108865)},
  doi         = {10.2760/378464},
  url         = {https://publications.jrc.ec.europa.eu/repository/handle/JRC108865}
}

@article{christodoulou2019ports,
  author  = {Christodoulou, Aris and Christidis, Panayotis and Demirel, Hande},
  title   = {Sea-level rise in ports: a wider focus on impacts},
  journal = {Maritime Economics \& Logistics},
  year    = {2019},
  volume  = {21},
  number  = {4},
  pages   = {482--496},
  doi     = {10.1057/s41278-018-0114-z}
}

@techreport{schade2024tent,
  author      = {Schade, W. and Khanna, A. A. and Mader, S. and Streif, M. and Abkai, T. and de Stasio, C. and Fermi, F. and Bielanska, D. and Deidda, C. and Thiery, W. and Maatsch, S.},
  title       = {Support study on the climate adaptation and cross-border investment needs to realise the {TEN-T} network},
  institution = {European Commission, Directorate-General for Mobility and Transport; Publications Office of the European Union},
  year        = {2024},
  doi         = {10.2832/7839720},
  url         = {https://op.europa.eu/en/publication-detail/-/publication/26731a63-b904-11ef-91ed-01aa75ed71a1/language-en},
  note        = {Catalogue number MI-01-24-000-EN-N; authors as initialled on the Publications Office record}
}

@article{koks2022flood,
  author  = {Koks, Elco E. and van Ginkel, Kees C. H. and van Marle, Margreet J. E. and Lemnitzer, Anne},
  title   = {Brief communication: critical infrastructure impacts of the 2021 mid-{July} western {European} flood event},
  journal = {Natural Hazards and Earth System Sciences},
  year    = {2022},
  volume  = {22},
  number  = {12},
  pages   = {3831--3838},
  doi     = {10.5194/nhess-22-3831-2022}
}

@article{izaguirre2021ports,
  author  = {Izaguirre, C. and Losada, I. J. and Camus, P. and Vigh, J. L. and Stenek, V.},
  title   = {Climate change risk to global port operations},
  journal = {Nature Climate Change},
  year    = {2021},
  volume  = {11},
  number  = {1},
  pages   = {14--20},
  doi     = {10.1038/s41558-020-00937-z}
}

% ---------- A4. Economy via MRIA ----------

@article{koks2019flooding,
  author  = {Koks, E. E. and Thissen, M. and Alfieri, L. and De Moel, H. and Feyen, L. and Jongman, B. and Aerts, J. C. J. H.},
  title   = {The macroeconomic impacts of future river flooding in {Europe}},
  journal = {Environmental Research Letters},
  year    = {2019},
  volume  = {14},
  number  = {8},
  pages   = {084042},
  doi     = {10.1088/1748-9326/ab3306}
}

% ---------- A5. Transport network vulnerability ----------

@article{jenelius2006vulnerability,
  author  = {Jenelius, Erik and Petersen, Tom and Mattsson, Lars-G{\"o}ran},
  title   = {Importance and exposure in road network vulnerability analysis},
  journal = {Transportation Research Part A: Policy and Practice},
  year    = {2006},
  volume  = {40},
  number  = {7},
  pages   = {537--560},
  doi     = {10.1016/j.tra.2005.11.003}
}

@article{jenelius2012areacovering,
  author  = {Jenelius, Erik and Mattsson, Lars-G{\"o}ran},
  title   = {Road network vulnerability analysis of area-covering disruptions: a grid-based approach with case study},
  journal = {Transportation Research Part A: Policy and Practice},
  year    = {2012},
  volume  = {46},
  number  = {5},
  pages   = {746--760},
  doi     = {10.1016/j.tra.2012.02.003}
}

@article{jenelius2015vulnerability,
  author  = {Jenelius, Erik and Mattsson, Lars-G{\"o}ran},
  title   = {Road network vulnerability analysis: conceptualization, implementation and application},
  journal = {Computers, Environment and Urban Systems},
  year    = {2015},
  volume  = {49},
  pages   = {136--147},
  doi     = {10.1016/j.compenvurbsys.2014.02.003}
}

@article{mattsson2015resilience,
  author  = {Mattsson, Lars-G{\"o}ran and Jenelius, Erik},
  title   = {Vulnerability and resilience of transport systems -- a discussion of recent research},
  journal = {Transportation Research Part A: Policy and Practice},
  year    = {2015},
  volume  = {81},
  pages   = {16--34},
  doi     = {10.1016/j.tra.2015.06.002}
}

@article{besinovic2020railway,
  author  = {Be{\v{s}}inovi{\'c}, Nikola},
  title   = {Resilience in railway transport systems: a literature review and research agenda},
  journal = {Transport Reviews},
  year    = {2020},
  volume  = {40},
  number  = {4},
  pages   = {457--478},
  doi     = {10.1080/01441647.2020.1728419}
}

% ---------- B1. Rhine transport economics ----------

@incollection{jonkeren2008chapter,
  author    = {Jonkeren, Olaf and van Ommeren, Jos and Rietveld, Piet},
  title     = {Effects of low water levels on the river {Rhine} on the inland waterway transport sector},
  booktitle = {Economics and Management of Climate Change: Risks, Mitigation and Adaptation},
  publisher = {Springer},
  address   = {New York},
  year      = {2008},
  pages     = {53--64},
  doi       = {10.1007/978-0-387-77353-7_5},
  note      = {Year from the book edition; the Crossref record carries no year}
}

@article{riquelmesolar2015turningpoints,
  author  = {Riquelme-Solar, M. and van Slobbe, E. and Werners, S. E.},
  title   = {Adaptation turning points on inland waterway transport in the {Rhine River}},
  journal = {Journal of Water and Climate Change},
  year    = {2015},
  volume  = {6},
  number  = {4},
  pages   = {670--682},
  doi     = {10.2166/wcc.2014.091}
}

@article{vanslobbe2016rhine,
  author  = {van Slobbe, Erik and Werners, Saskia E. and Riquelme-Solar, Marcela and B{\"o}lscher, Tobias and van Vliet, Michelle T. H.},
  title   = {The future of the {Rhine}: stranded ships and no more salmon?},
  journal = {Regional Environmental Change},
  year    = {2016},
  volume  = {16},
  number  = {1},
  pages   = {31--41},
  doi     = {10.1007/s10113-014-0683-z}
}

@techreport{scholten2017danube,
  author      = {Scholten, Anja and Rothstein, Benno and Pistocchi, Alberto},
  title       = {Navigation on the {Danube} -- limitations by low water levels and their impacts},
  institution = {European Commission, Joint Research Centre},
  year        = {2017},
  number      = {EUR 28374 EN (JRC104224)},
  doi         = {10.2788/236234},
  url         = {https://publications.jrc.ec.europa.eu/repository/handle/JRC104224}
}

@article{bedoyamaya2023spillover,
  author  = {Bedoya-Maya, Felipe and Beckers, Joris and van Hassel, Edwin},
  title   = {Spillover effects from inland waterway transport development: spatial assessment of the {Rhine-Alpine} corridor},
  journal = {Journal of Transport Geography},
  year    = {2023},
  volume  = {113},
  pages   = {103721},
  doi     = {10.1016/j.jtrangeo.2023.103721}
}

% ---------- B2. Hydrology and forecasting ----------

@techreport{gorgen2010rheinblick,
  author      = {G{\"o}rgen, K. and Beersma, J. and Brahmer, G. and Buiteveld, H. and Carambia, M. and de Keizer, O. and Krahe, P. and Nilson, E. and Lammersen, R. and Perrin, C. and Volken, D.},
  title       = {Assessment of climate change impacts on discharge in the {Rhine River Basin}: results of the {RheinBlick2050} project},
  institution = {International Commission for the Hydrology of the Rhine Basin (CHR)},
  address     = {Lelystad},
  year        = {2010},
  number      = {CHR report I-23},
  url         = {https://knmi.nl/research/publications/assessment-of-climate-change-impacts-on-discharge-in-the-rhine-river-basin-results-of-the-rheinblick-2050-project},
  note        = {ISBN 978-90-70980-35-1; authors as initialled on the KNMI record; the report number is inferred from the PDF file name}
}

@techreport{nilson2014kliwas,
  author      = {Nilson, Enno and others},
  title       = {Auswirkungen des {Klimawandels} auf das {Abflussgeschehen} und die {Binnenschifffahrt} in {Deutschland}: {Schlussbericht} {KLIWAS}-{Projekt} 4.01},
  institution = {Bundesanstalt f{\"u}r Gew{\"a}sserkunde},
  address     = {Koblenz},
  year        = {2014},
  number      = {KLIWAS-Schriftenreihe 43/2014},
  doi         = {10.5675/Kliwas_43/2014_4.01},
  note        = {DataCite lists Nilson as sole creator; the report cover names further BfG authors}
}

@article{meissner2017forecast,
  author  = {Mei{\ss}ner, Dennis and Klein, Bastian and Ionita, Monica},
  title   = {Development of a monthly to seasonal forecast framework tailored to inland waterway transport in central {Europe}},
  journal = {Hydrology and Earth System Sciences},
  year    = {2017},
  volume  = {21},
  number  = {12},
  pages   = {6401--6423},
  doi     = {10.5194/hess-21-6401-2017}
}

@article{ionita2020lowflow,
  author  = {Ionita, M. and Nagavciuc, V.},
  title   = {Forecasting low flow conditions months in advance through teleconnection patterns, with a special focus on summer 2018},
  journal = {Scientific Reports},
  year    = {2020},
  volume  = {10},
  pages   = {13258},
  doi     = {10.1038/s41598-020-70060-8}
}

@article{vantiel2023watertowers,
  author  = {van Tiel, Marit and Weiler, Markus and Freudiger, Daphn{\'e} and Moretti, Greta and Kohn, Irene and Gerlinger, Kai and Stahl, Kerstin},
  title   = {Melting {Alpine} water towers aggravate downstream low flows: a stress-test storyline approach},
  journal = {Earth's Future},
  year    = {2023},
  volume  = {11},
  number  = {3},
  pages   = {e2022EF003408},
  doi     = {10.1029/2022ef003408}
}

% ---------- B3. Ex-post statistics of 2018 ----------

@techreport{ademmer2018box,
  author      = {Ademmer, Martin and Jannsen, Nils and Kooths, Stefan and M{\"o}sle, Saskia},
  title       = {Zum {Einfluss} des {Niedrigwassers} auf die {Konjunktur}},
  institution = {Kiel Institute for the World Economy},
  year        = {2018},
  number      = {IfW-Box 2018.17},
  url         = {https://www.ifw-kiel.de/fileadmin/Dateiverwaltung/IfW-Publications/-ifw/IfW_Box/2018/box_2018-17_niedrigwasser.pdf}
}

@misc{kriedel2019lowwater,
  author       = {Kriedel, Norbert},
  title        = {Macroeconomic effects of low water levels on the {Rhine} -- a statistical analysis},
  year         = {2019},
  howpublished = {Central Commission for the Navigation of the Rhine, presentation at the workshop ``Low waters and consequences on navigation of the Rhine'', Federal Ministry of Transport and Digital Infrastructure, Bonn, 26 November 2019, \url{https://www.ccr-zkr.org/files/documents/workshops/wrshp261119/03_Kriedel_en.pdf}}
}

@techreport{streng2020laagwater,
  author      = {Streng, Martijn and van Saase, Niels and Kuipers, Bart},
  title       = {Economische impact laagwater: een analyse van de effecten van laagwater op de binnenvaartsector en de {Nederlandse} en {Duitse} economie},
  institution = {Erasmus Centre for Urban, Port and Transport Economics (Erasmus UPT), for CBRB and Koninklijke BLN-Schuttevaer},
  address     = {Rotterdam},
  year        = {2020},
  month       = apr,
  url         = {https://www.eur.nl/en/upt/media/87563}
}

% ---------- B4-B6. Central banks, institutes and press, 2018-2026 ----------

@techreport{bundesbank2018november,
  author      = {{Deutsche Bundesbank}},
  title       = {Monatsbericht {November} 2018},
  institution = {Deutsche Bundesbank},
  year        = {2018},
  url         = {https://www.bundesbank.de/resource/blob/767336/cf8bde887ae06b7800bd566db4874e23/472B63F073F071307366337C94F8C870/2018-11-monatsbericht-data.pdf},
  note        = {No treatment of the Rhine low water}
}

@techreport{bundesbank2018december,
  author      = {{Deutsche Bundesbank}},
  title       = {Monatsbericht {Dezember} 2018},
  institution = {Deutsche Bundesbank},
  year        = {2018},
  url         = {https://www.bundesbank.de/resource/blob/770494/3f0847f16b8cf2406f7d6522191c50d6/mL/2018-12-monatsbericht-data.pdf},
  note        = {No assessment of the Rhine low water}
}

@techreport{bundesbank2022october,
  author      = {{Deutsche Bundesbank}},
  title       = {Monatsbericht {Oktober} 2022},
  institution = {Deutsche Bundesbank},
  year        = {2022},
  url         = {https://www.bundesbank.de/resource/blob/898714/3c4c020b2005b766f6b5bd4aa10304b6/472B63F073F071307366337C94F8C870/2022-10-monatsbericht-data.pdf},
  note        = {Chemicals and coke/refining output in August 2022 held back by the strong low water on the Rhine}
}

@misc{bundesbank2026september,
  author       = {{Deutsche Bundesbank}},
  title        = {Deutsche {Wirtschaft} auf {Erholungskurs}: {Kurzbericht} zur {Konjunkturlage}, {Monatsbericht} {September} 2026},
  year         = {2026},
  howpublished = {21 September 2026, \url{https://www.bundesbank.de/de/aufgaben/themen/deutsche-wirtschaft-auf-erholungskurs-1009002}}
}

@misc{elderson2026resilience,
  author       = {Elderson, Frank},
  title        = {Ensuring resilience in the face of uncertainty},
  year         = {2026},
  howpublished = {Speech, Frankfurt am Main, 14 October 2026, European Central Bank, \url{https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp261014~e4ca33588e.en.html}},
  note         = {Footnote 6: Rhine low water ``could also reduce Germany's economic recovery by up to 0.2 percentage points of GDP in the third quarter''}
}

@misc{ing2026lowwater,
  author       = {Brzeski, Carsten},
  title        = {Low water levels are new setback for the {German} economy},
  year         = {2026},
  howpublished = {ING THINK, 4 August 2026, \url{https://think.ing.com/articles/low-water-levels-and-the-german-economy/}}
}

@misc{zdf2026niedrigwasser,
  author       = {{ZDFheute}},
  title        = {Niedrigwasser im {Rhein}: {Pegel} teils weiter auf {Tiefststand}},
  year         = {2026},
  howpublished = {4 August 2026, \url{https://www.zdfheute.de/panorama/niedrigwasser-rhein-pegel-stand-sprit-wirtschaft-100.html}},
  note         = {Reports the IW (Thilo Sch{\"a}fer, to Bild): GDP growth 2026 could be 0.4 percentage points lower because of the low water}
}

@misc{kfw2026pegelstand,
  author       = {Scheuermeyer, Philipp},
  title        = {Konjunktur droht auf {Grund} zu laufen},
  year         = {2026},
  howpublished = {KfW Research, Auf einen Blick, 12 August 2026, \url{https://www.kfw.de/PDF/Download-Center/Konzernthemen/Research/PDF-Auf-einen-Blick/2026-08-12-AEB-Pegelstand.pdf}}
}

@misc{kfw2026kompass,
  author       = {K{\"o}rner, Jenny and Schoenwald, Stephanie and Wanke, Sebastian},
  title        = {{KfW}-{Konjunkturkompass} {August} 2026: {Wachstum} wider alle {Belastungen}},
  year         = {2026},
  howpublished = {KfW Research, 25 August 2026, \url{https://www.kfw.de/PDF/Download-Center/Konzernthemen/Research/PDF-Dokumente-KfW-Konjunkturkompass/KfW-Konjunkturkompass-August-2026.pdf}}
}

@misc{rwi2026konjunkturbericht,
  author       = {{RWI -- Leibniz-Institut f{\"u}r Wirtschaftsforschung}},
  title        = {{RWI}-{Konjunkturbericht}: {Kr{\"a}ftige} {Exporte} treiben {Erholung} -- strukturelle {Probleme} bleiben},
  year         = {2026},
  howpublished = {Press release, 3 September 2026, \url{https://www.rwi-essen.de/presse/wissenschaftskommunikation/pressemitteilungen/detail/rwi-konjunkturbericht-kraeftige-exporte-treiben-erholung-strukturelle-probleme-bleiben}}
}

@article{ifo2026herbst,
  author  = {Wollmersh{\"a}user, T. and Best, L. and Ederer, S. and Fell, M. and H{\"a}slinger, E. and Koch, F. and Lay, M. and Lehmann, R. and Link, S. and Ruffert, A. and Schasching, M. and Wibault, T.},
  title   = {ifo {Konjunkturprognose} {Herbst} 2026: {Erholungskr{\"a}fte} gewinnen {Oberhand}},
  journal = {ifo Schnelldienst digital},
  year    = {2026},
  volume  = {7},
  number  = {15},
  pages   = {1--19},
  url     = {https://www.ifo.de/en/publications/2026/article-journal/ifo-konjunkturprognose-herbst-2026},
  note    = {Box on the Rhine low water, pp. 8ff, cited by the Gemeinschaftsdiagnose Herbst 2026 (footnote 7) for the 0.7--1.2 \% range; authors as initialled there; the box itself could not be retrieved}
}

@article{diw2026wochenbericht36,
  author  = {{DIW Berlin Konjunkturforscher*innen}},
  title   = {Deutsche {Wirtschaft} w{\"a}chst, aber nicht aus eigener {Kraft} -- {Weltwirtschaft} bleibt auf {Kurs}},
  journal = {DIW Wochenbericht},
  year    = {2026},
  number  = {36},
  url     = {https://www.diw.de/documents/publikationen/73/diw_01.c.1018523.de/26-36-2.pdf}
}

@misc{tooze2026kaub,
  author       = {Tooze, Adam},
  title        = {Chartbook 466: the straits of {Kaub} and seven centuries of {German} political economy},
  year         = {2026},
  howpublished = {Substack, 14 August 2026, \url{https://adamtooze.substack.com/p/chartbook-466-the-straits-of-kaub}}
}
```

Two entries above carry details beyond what the identifier record shows and are marked in
their note fields: dejong2004metamodel (co-authors and pages) and ifo2026herbst (co-authors'
first names). The verified facts for both are the DOI or landing page, title, first author and
year; drop the unverified fields if they are not checked before import.

---

## 5. Method of this pass

Sources read first: main.tex, sections/si.tex, refs.bib (Overleaf checkout), the dossiers
evidence_rhine_literature.md, waterway_rates_by_vessel_type.md,
update_20260903_supply_chain_damage.md, validation_targets_2026_surveys.md. Searches: Crossref
REST (query.bibliographic and /works/DOI), DataCite REST, WebSearch, publisher and institutional
pages; PDFs of the German and Dutch reports downloaded to the session scratchpad and read with
pdftotext. About 75 works verified; items that could not be verified are listed in B7 and are
absent from the BibTeX block. Browser tools were not used; no repository file other than this one
was created or changed.
