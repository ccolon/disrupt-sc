# Positioning of the Rhine 2026 paper: synthesis of the literature review of 7 November 2026

Two questions were asked on 7 November 2026: what has been done so far in Europe-wide economic modelling of
disasters (economy-only models, transport-only models), and what is the state of the art of the kind of model the
paper uses. Four strands were searched in parallel; each wrote a dossier in this folder, and this file is the
synthesis that the manuscript edits of the same evening rest on.

| Strand | Dossier | Status |
|---|---|---|
| A. Europe-wide economic models of disasters and disruptions (CGE, MRIO, dynamic IO, ABM) | `positioning_eu_econ_models_20261107.md` | done (about 55 works, 39 BibTeX entries) |
| B. Transport models of disasters and the Rhine (network models, freight models, inland-waterway economics) | `positioning_transport_rhine_20261107.md` | pending at the time of writing; to be appended to section 2 when it lands |
| C. State of the art of spatial supply-chain models of disasters (the model's relatives, ranked) | `positioning_model_state_of_art_20261107.md` | done (table of about 60 works, five relatives ranked, draft paragraph) |
| D. Scoop search 2023 to November 2026 and the analyses of the 2026 event | `positioning_scoop_recent_20261107.md` | done (verdict by claim, 2026 chronology, mischaracterisations, 59 BibTeX entries) |

Standard: every work cited below was verified by its DOI on Crossref (or DataCite for Zenodo), by the publisher's
page or by the PDF; the dossiers tag the few exceptions as unverified and this file repeats the tag. Numbers are
quoted from the works as the dossiers report them, not recomputed.

---

## 1. Europe-wide economic modelling of disasters: what exists

Four families of models have been applied to disasters and disruptions at the scale of the European Union or of
several European countries. None routes goods on a transport network, none has firm agents across the EU, none runs
on a weekly event calendar, and none generates losses through a stock-out mechanism (dossier A, section 1).

**(a) EU-scale computable general equilibrium and integrated assessment (the JRC PESETA line and its descendants).**
PESETA I to IV feed biophysical damages (river and coastal floods, agriculture, energy, drought, heat, mortality)
into a European CGE and report welfare losses by scenario (Ciscar et al. 2011, PNAS; PESETA II to IV reports;
Dottori et al. 2018, Nature Climate Change, for river floods). Heatwaves enter as labour productivity in a
274-region CGE: the hot years 2003, 2010, 2015 and 2018 cost 0.3 to 0.5 % of European GDP (Garcia-Leon et al. 2021,
Nature Communications). Drought is costed with damage functions and no propagation: EUR 9 billion a year for the EU
and UK today, above EUR 65 billion at 4 degrees (Naumann et al. 2021, Nature Climate Change); in that accounting
inland waterway transport is about 1.5 % of the direct drought loss (Cammalleri et al. 2020, PESETA IV Task 7).
Newer regional CGEs put NUTS2 regions in recursive dynamics (Knittel et al. 2024; Dunne et al. 2026; Mongelli et al.
2023). In all of these, transport is a service sector or a trade margin, the time step is a year or longer,
inventories do not exist, and the shock is a loss of capital or productivity.

**(b) Multiregional input-output, supply-use and programming models of specific events.** The only continent-scale
indirect-loss model of a hazard is MRIA (Koks and Thissen 2016; Koks et al. 2019, Environmental Research Letters):
a recursive-dynamic multiregional supply-use model with linear programming over 270 NUTS2 regions, recovery within
about a year, substitution only along existing trade links, no transport cost and no inventories; up to 60 % of the
indirect flood loss can be offset through alternative suppliers, and services and utilities are the sectors whose
indirect losses rise most. Its 2026 extension adds capacity constraints on trade between regions (Vanniya Perumal et
al. 2026, Economic Systems Research), the closest an EU-wide model has come to a capacity gate, still annual and
without a network. Floods in Germany and Central Europe were costed with flood-footprint and MRIO models
(Mendoza-Tinoco et al. 2020: indirect losses 65 % of the total of the 2009 floods, with business services,
manufacturing, construction and commerce carrying most of them; Sieg et al. 2019; Schulte in den Baeumen et al.
2015; Oosterhaven and Toebben 2017). The pandemic and the energy shocks were run on dynamic IO models at national or
three-country scale (Pichler and Farmer 2022 for Germany, Italy and Spain; Reissl et al. 2022, validated on the
observed 2020 path of Italy; Pichler et al. 2024 for the Austrian gas shock; Bachmann et al. 2024 for a Russian
energy stop), on the JRC's RHOMOLO CGE (Conte et al. 2020) and in the IMF's gas models (Di Bella et al. 2022). The
ECB's production-network work on physical climate risk is a static global IO exercise (Fahr et al. 2024) and its
weather work is econometric (Andersson et al. 2026).

**(c) Global agent-based loss propagation with European results (Acclimate, PIK).** Daily, global, about 7,000
region-sector agents with storages, rationing and price-based reallocation of demand among existing suppliers;
transport is a delivery delay, there is no network, no routing and no mode (Otto et al. 2017; Willner et al. 2018;
Quante et al. 2024). The EU appears as a region, never as an event with a transport constraint. Two results
anticipate the paper's second message: consecutive or overlapping extremes amplify welfare losses by 21 % on average
("ripple resonance", Kuhla et al. 2021) and stressed economies respond more strongly to extremes (Middelanis et al.
2023).

**(d) Firm-level production networks and national agent-based models in Europe.** Nation-wide firm networks exist
for Hungary from VAT data (Diem et al. 2022; Stangl et al. 2024; Diem et al. 2024: aggregating to industries
understates losses by up to 37 %), for an unnamed medium-sized country from mobile-phone data (Reisch et al. 2022)
and for the Netherlands by reconstruction (Ialongo et al. 2022). Their shock model is a static Leontief cascade
without inventories or real time. The Austrian flood work couples a CGE and the IIASA/CSH macroeconomic ABM fed with
sector capital damages (Bachner et al. 2024; Poledna et al. 2018 preprint). These are single-country models; none
has been applied to a drought or to a transport disruption.

**Not found (searched):** an E3ME disaster application, a RHOMOLO flood or hazard application, a Bundesbank
model-based weather analysis, the Inoue-Todo code transposed to a European network, any MRIO or CGE study of the
2018 Rhine low water. The 2018 economics is econometric (section 2).

**What no Europe-wide economic model has done so far, and the paper does** (dossier A, section 3): routed every
shipment on the physical multimodal network with per-class capacities, mode switching and gauge-dependent
surcharges; placed firm agents across 28 economies; run weekly on an observed event calendar so that the order and
spacing of the troughs can be costed; generated losses from per-input inventories with survey-based criticality and
pooling, which separates the freight-bill channel from the shortage channel; costed a drought through the transport
channel at all; and set an event-specific benchmark (German industrial production, 2018) next to a prospective test.
The only European dynamic model validated on an observed path is Reissl et al. (2022) for Italy in 2020.

---

## 2. Transport-only work on the Rhine and inland waterways

This section rests on dossiers C and D; dossier B (transport models of disasters and the Rhine) is pending and will
be appended here.

**Inland-waterway economics of the Rhine.** The welfare cost of low water and the modal shift it causes were
estimated by Jonkeren et al. (2007, 2011, 2014), Beuthe et al. (2014), Scholten and Rothstein (2014), van Dorsser
et al. (2020) and the PESETA III inland-waterway task (Christodoulou et al. 2020); fleet and loading behaviour by
Vinke et al. (2022, 2024). These evaluate freight costs and the shift between rail and road, not the wider supply
chain (already cited in the manuscript).

**Econometrics of the 2018 event.** Ademmer, Jannsen and Meuchelboeck (2023, German Economic Review) relate the
industrial production index to low-water days; Jannsen and Meuchelboeck (2026, Wirtschaftsdienst 106(9)) restate
the 2018 effect as production dampened by 0.7 % in the third and 1 % in the fourth quarter of 2018, GDP by 0.2 % and
0.3 %, about 0.1 % over the year, and give 1.2 % of producing-sector output for a month of 30 low-water days and
1.5 % a month from the second month. Meuchelboeck (2025, RETHINK-GSC Working Paper 08/2025) is the first firm-level
evidence that the 2018 low water propagated along supply chains: German firms importing by inland waterway reduced
the value, variety and geographic scope of their exports, the effect was strongest for firms without transport
diversification, inland-waterway exports fell by nearly 20 % and imports by 12 %, and firms switched modes
persistently. Horst and Mueller (2024, SSRN) and ABN AMRO (c. 2023, page unavailable) are partially verified and not
cited.

**The only other transport-coupled economic model of the Rhine** is Prognos's R2K-Klim+ work: freight-transport
models coupled to the regional-economic model REGINA for 68 districts along the river. Its 2023 phase-1 results give
up to 10.2 Mt of barge deliveries lost and EUR 3.4 billion of production value in an extreme low-water year, and its
scenario run for Handelsblatt (page dated 6 August 2026) put the 2026 production-value loss along the Rhine at
EUR 912.8 million. Grey literature, corridor only, regional-sectoral; no peer-reviewed paper found.

**Inland waterways elsewhere** have been costed with inoperability, Monte-Carlo and CGE models of US systems
(MacKenzie et al. 2012; Welch et al. 2022; Chen and Cheng 2024: a barge-to-rail shift cuts the regional GDP loss by
6.6 to 24.2 % and needs added rail capacity; Chen, Rose, Roberts and Tucci 2025 on the 2022-23 Mississippi low water,
with barge rates up to +400 %), in which the river is a price shock or a lost flow rather than a route. No
propagation model of a Rhine low water exists.

**Exposure, not economics.** Deidda et al. (2026, NHESS) review the climate exposure of EU roads, rail, inland
waterways, ports and airports (the 2018 Rhine drought at EUR 2.4 billion of losses in Germany); the EEA briefing of
3 November 2026 uses the 2026 Rhine as a case study. The maritime side is covered by the Oxford port and chokepoint
models (Verschuur et al. 2022, 2023, 2025) and by an agent-based model of the global fleet (Devetak et al. 2026,
preprint), all at the resolution of countries and sectors and without production.

---

## 3. State of the art of spatial supply-chain models of disasters

Dossier C scores about 60 works on five criteria (firm-level agents, transport network, dynamics with inventories,
multi-country scope, test on an observed episode; the paper's model scores 5 of 5) and finds four lineages with a
gap in the middle:

1. **ARIO and disaster-footprint input-output** (Hallegatte 2008, 2014; Guan et al. 2020; Wang et al. 2021;
   Mendoza-Tinoco et al. 2020; Sun et al. 2024; Fang et al. 2026). Sector or region-sector dynamics with
   inventories, overproduction and rationing; transport absent; validation loose. Their robust findings (indirect
   losses rival direct ones; duration matters more than intensity; inventories and heterogeneity dominate) are the
   backdrop to the paper's first two messages. Score 1.5 to 2.
2. **Acclimate** (above). Closest in dynamics; transport a delay; no firms, no network; score 2.
3. **Firm-level agent-based models on observed networks** (Inoue and Todo 2019, about one million Japanese firms,
   daily, nine-day inventories, compared with the post-Tohoku production index; the Thurner group's Hungarian
   network). What they have and the paper lacks: the real network. What the paper has and they lack: geography of
   flows, modes, capacity, multi-country scope. Score 3.
4. **Infrastructure-economy coupling of the Oxford and VU groups** (Thacker et al. 2017; Koks et al. 2019, IJDRS;
   Verschuur et al. 2022, 2023, 2025; MRIA). Explicit networks and continental or global scope, static or annual
   economics, no firms. Score 1 to 1.5.

**The five nearest relatives, ranked** (dossier C, section 3): DisruptSC v1 and its national applications (Colon et
al. 2021, Tanzania, roads only, strict Leontief, no ex-post test; the Cambodia applications added rail, waterway and
sea within one country and are not in a journal), the Inoue-Todo lineage, Acclimate, ARIO on multiregional tables,
and the Oxford/VU coupling. Honourable mentions: Pichler et al. 2022 (production rule and the only other ex-post
validated dynamic model besides Inoue-Todo and Reissl), Diem et al. 2022/2024 (size of the aggregation bias), Chen
et al. 2025 and Chen and Cheng 2024 (the only other economic models of a low-water event).

**Where the paper sits.** DisruptSC v2 is the only model found that combines firm-level agents for all sectors,
every shipment routed on a multimodal network with cargo classes, surcharges, capacity and mode switching, weekly
dynamics with per-input inventories and survey-based criticality, 28 economies, and a test on an observed episode.

**What reviewers will most likely raise, and the relatives to cite in reply** (dossier C): the synthetic
supplier-buyer network against observed networks (cite Diem et al. 2024 for the aggregation bias, report the
eleven-network spread as sampling uncertainty); no price-responsive demand (Acclimate has it; the Discussion states
the assumption and the 2018 and 2026 records behind it); validation on one episode (Inoue-Todo and Pichler et al.
2022 are the only other ex-post tests; the prospective test goes beyond both); "rail is inert" against Meuchelboeck
2025 (her firms are traders, mostly of containerisable goods, which the model lets switch; the inertia reported is
for tank and ore cargo at volume, which Chen and Cheng 2024 also find needs added rail capacity).

---

## 4. Scoop verdict and the wording of the novelty claim

Dossier D swept arXiv, SSRN, EconStor, Research Square, the Kiel Institute, Bundesbank, ECB, DIW, ifo, IW, ZEW,
RWI, CPB, CEPII, Banque de France, DNB, OECD/ITF, JRC, EEA, CCNR and the banks' research pages for 2023 to
November 2026.

- **"First whole-EU firm-level supply-chain model with every shipment routed on the multimodal network": scoop risk
  low.** No work combines firm-level agents, continental coverage and explicit routing. Nearest neighbours:
  Prognos/R2K-Klim+ (corridor, regional-sectoral), the Koks group's MRIA with trade constraints (regional IO, no
  routing), the Verschuur port and chokepoint models (maritime, country-sector), Massoni (2026, CEPREMAP: spatial
  production-network model with endogenous routing through ports, aggregate, not Europe), the CSH Vienna firm
  networks (national, no transport), Acclimate, the Bank of Canada's global firm-level flood stress test
  (Papadopoulos et al. 2026, no transport network), Inoue and Todo (Japan, no transport).
- **"First model-based estimate of the 2026 event": do not write it.** Two model-based estimates preceded the
  manuscript: Prognos for Handelsblatt (6 August 2026, R2K-Klim+ scenario run) and the Kiel Institute's application
  of its 2018 elasticity to the 2026 calendar (autumn report of 3 September 2026; Jannsen and Meuchelboeck 2026).
  What survives: the first estimate from a supply-chain propagation model, issued as a forecast before the
  statistics and kept for evaluation against them.
- **Own prior work constrains "first multimodal" and "first multi-country".** The Zenodo release "v2 - Cambodia"
  of 12 December 2022 already describes roads, railways, waterways and maritime networks, and the model's
  applications page lists multimodal and multi-country applications. The defensible novelty is scale and
  completeness: a whole continental economy at firm resolution with full multimodal routing, calibrated on a
  documented historical event and run as a forecast.
- **Kotz, Levermann and Wenz (2024, Nature) was retracted on 3 December 2025.** Never cite it.

Wording adopted in the Introduction: "To our knowledge no supply-chain model of this scope exists: one in which
every shipment between the firms of 28 economies is routed by cargo type on a shared multimodal network, and in
which the agents that reroute, switch mode, wait or stop are firms rather than sectors." And on 2026: "ours is, to
our knowledge, the first from a model of supply-chain propagation, issued as a forecast and kept for evaluation
against the statistics."

---

## 5. What changed in the manuscript (Overleaf commit of 7 November 2026, evening)

1. Introduction, 2018 paragraph: GDP "0.2--0.3 % below its path in the quarters of the episode" (was 0.3--0.4 % at
   the trough; the 0.4 is IW's reading of an older Kiel statement), cited to Ademmer et al. 2023 and Jannsen and
   Meuchelboeck 2026.
2. Introduction, 2026 paragraph: the ex-ante range split by source: 0.1--0.2 points (Kiel, 28 July) and up to 0.35
   points if the closure lasted into September (Commerzbank, Bloomberg of 11 August, new entry
   `bloomberg2026commerzbank`). The 0.35 had been attributed to the Kiel Institute.
3. Introduction, "a low river is a transport shock" paragraph: European drought costings count direct losses, of
   which inland navigation is a small share, and do not propagate them (Naumann 2021; Cammalleri 2020).
4. Introduction, state-of-the-art paragraph rewritten (European IO and CGE applications; firm-level networks;
   Acclimate's transport as delay; transport-coupled models without firm-level supply chains; the Mississippi
   models; DisruptSC v1 and the Zenodo v2 release; the novelty claim as above).
5. Introduction, last paragraph: the other 2026 estimates named (Kiel 28 July, Kiel autumn report, Jannsen and
   Meuchelboeck, Prognos) and the "first from a supply-chain propagation model" sentence.
6. Results, second test: the 0.2--0.35 range now cited to Commerzbank, the Kiel autumn report and Jannsen and
   Meuchelboeck; the Kiel 28 July statement cited at its own number.
7. Discussion, first paragraph: Boehm 2019 and Carvalho 2021 cited as evidence that inputs are hard to replace in
   the short run, Hallegatte 2014 and Inoue 2019 for inventories setting the delay (they had all been cited as an
   "inventories literature").
8. Discussion, two-trough paragraph: ripple resonance and stressed economies (Kuhla 2021; Middelanis 2023) named as
   the global analogue, with the inventories as the single carrier here.
9. Discussion, services paragraph: European flood IO models also place much of the indirect loss in services
   (Mendoza-Tinoco 2020; Koks 2019 ERL).
10. Discussion, adaptations: the Upper Mississippi barge-to-rail result (Chen and Cheng 2024) as the one other
    quantified rail result for a low water.
11. Discussion, limitations: the persistent modal shift of 2018 (Meuchelboeck 2025) as a lasting adjustment the
    model does not represent.

References: 24 entries added to refs.bib (61 to 85; 69 cited of the journal's guide of 70), all DOIs verified by
`studies/paper_pipeline/scripts/cite_check.py` (Crossref; DataCite for the Zenodo record, support added today); the
two Chen entries' author names completed from Crossref; DOIs of Jonkeren 2007 and 2011 added. The gate
(`paper_gate.py --regen`) passes every check except the two pending findings known since 5 November; the submission
PDFs were rebuilt (main text 33 pages, SI 38 pages). Counts after the edits: main text 7,181 words (Introduction
1,323, Results 3,851, Discussion 2,007), Methods 4,784, against the journal's guides of 5,000 and 3,000.

---

## 6. Open items for the author

- **Length.** The positioning added about 400 words to an Introduction already over the guide; the trimming options
  are in `../submission/natcomms_requirements_20261107.md`.
- **DB Cargo wagon numbers.** The `dbcargo2026` note (400 extra wagons at once, up to 900) disagrees with the
  September dossier (about 400 mobilised, up to 500 more later); the Discussion's "tonnage the operator offered in
  August 2026" rests on it. Check the DB Cargo page before the November batch.
- **`vinke2023`** is a 2024 issue (Climate Risk Management 43, 100578, online December 2023): key and year
  inconsistent, harmless.
- **Not cited pending verification:** Horst and Mueller 2024 (SSRN), ABN AMRO's Dutch note (page unavailable), the
  ITF/OECD factsheet of September 2026 (403), the Swiss compulsory-stock releases (search snippets only).
- **For the post-event revision** (dossier D, section 3): Destatis Q3 GDP +0.2 % q/q (30 October), September
  production +0.7 % m/m, industry +1.7 %, energy-intensive output -1.9 % y/y, Q3 production -0.4 % against Q2
  (6 November); the Bundesbank's October report (Rhine low water weighed on industry, energy-intensive branches);
  the ECB's "up to 0.2 percentage points" (26 October); the Kiel Institute's adopted -0.2 % of Q3 GDP; the detailed
  Q3 accounts due 25 November and the Sachverstaendigenrat report due 11 November. The aggregate GDP print is not a
  test of a sector-level mechanism; the production index and the services turnover indices are.
- **Dossier B** (transport models and the Rhine): append to section 2 and check whether it changes any Introduction
  sentence on transport economics or the Prognos characterisation.
