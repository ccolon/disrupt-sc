# Positioning strand: Europe-wide ECONOMIC modelling of disasters and disruptions (economy-only models, transport absent or implicit)

Compiled 7 November 2026 for the Nature Communications manuscript "Logistics under drought: how the Rhine low
water of 2026 propagates through Europe's supply chains" (DisruptSC v2, EU27+CH, ~12,000 firm agents, 1.3 M links,
TEN-T routing, weekly step). Question of the strand: what has been done in multi-country or EU-scale economic
modelling of natural hazards, pandemics and energy/trade shocks with multiregional input-output (MRIO), CGE,
ARIO/inventory and agent-based/production-network models, and which of their gaps does the paper fill.

Companion dossier: `positioning_model_state_of_art_20261107.md` (the model-lineage strand, about 95 works:
DisruptSC, Acclimate, Inoue-Todo, ARIO, Thurner/Oxford firm networks, Pichler-Farmer, MRIA, US waterway
models). Works it already verified are cited here by its BibTeX key as "SoA `key`", are not re-described in
detail, and are NOT repeated in the BibTeX block of section 4, so that the two blocks can be merged into
refs.bib without key clashes or duplicate references.

Verification key (every work below carries one or more tags):
- [C] Crossref record fetched by DOI or bibliographic query (title, authors, venue, year, volume, pages confirmed);
- [P] publisher or repository landing page read (abstract and numbers taken from it);
- [OP] EU Publications Office record reached through the DOI (JRC reports are not in Crossref);
- [A] arXiv abstract page read; [R] RePEc/IDEAS listing read (ECB working papers, no DOI exposed);
- [S] number taken from a search-engine snippet or a citing source, not from the work itself;
- [U] could not be verified; stated as such.

Inputs read first: main.tex (Introduction, Results, Discussion, Methods), refs.bib, sections/si.tex (grep),
evidence_rhine_literature.md, input_substitution_literature.md, then section 2 of the companion dossier.

---

## 0. Already cited in refs.bib (not repeated in the table or the BibTeX block), with flags

Works of this strand already in refs.bib: hallegatte2008 (ARIO, Katrina), hallegatte2014 (ARIO-inventory),
otto2017 (Acclimate), wenz2016 (heat stress through trade), guan2020 (COVID, 140-region MRIO ARIO), koks2016
(Koks & Thissen, MRIA), koks2019 (Koks et al., Nature Communications: global multi-hazard road and rail asset
risk), pichler2022 (UK Covid, partially binding Leontief), diem2022 (Hungarian firm network), bachmann2022
(ECONtribute policy brief), inoue2019, colon2021, mackenzie2012, welch2022, carvalho2021, boehm2019, barrot2016,
baqaee2019, bonadio2021. Of these only hallegatte2008, hallegatte2014, otto2017, inoue2019, guan2020, colon2021,
pichler2022, carvalho2021 and boehm2019 are cited in main.tex or the SI; koks2016, koks2019, diem2022,
bachmann2022, wenz2016, barrot2016, baqaee2019, bonadio2021, mackenzie2012 and welch2022 sit in the .bib unused.

Flags (nothing in refs.bib is wrong as a record; the flags concern use and labelling):
1. `koks2019` is the Nature Communications infrastructure-asset paper, not the ERL 2019 MRIA flood paper
   ("The macroeconomic impacts of future river flooding in Europe", doi 10.1088/1748-9326/ab3306). The brief for
   this strand treats "Koks et al. 2019 ERL" as a candidate; it is absent from refs.bib and is the single closest
   EU-wide precedent (270 NUTS2 regions, indirect flood losses). The companion dossier adds it as `koks2019floods`.
2. `diem2022` (Diem, Borsos, Reisch, Kertesz, Thurner, Sci. Rep. 12:7719) uses the Hungarian VAT network
   (91,595 firms; "fully anonymized VAT micro data of the Hungarian Central Bank"), not Austrian data as the
   brief says. The Austrian firm network of the same group is reconstructed from mobile-phone data (Reisch et
   al. 2022; the paper itself says only "a medium-sized European country").
3. `bachmann2022` is the policy brief; the peer-reviewed version is Bachmann et al. (2024), Economica 91(364),
   1157-1200, doi 10.1111/ecca.12546, with a different title ("...macroeconomic and distributional effects...")
   and the headline "0.5 % to 3 % of GDP" in the short run. Added as `bachmann2024whatif`.
4. Discussion, paragraph 1: "a lesson of the disaster literature on inventories \citep{hallegatte2014,
   carvalho2021,boehm2019}". Hallegatte (2014) is about inventories; Carvalho et al. (2021) and Boehm et al.
   (2019) are empirical papers on propagation and input complementarity after Tohoku and say nothing about
   inventory buffers. Same finding as flag 1 of the companion dossier, whose rewording ("short-run substitution
   is weak \citep{boehm2019,carvalho2021}, so inventories carry the response \citep{hallegatte2014}") is the
   better fix.
5. Introduction, paragraph 6: the models cited for "supply-chain models of disasters" (Hallegatte 2008, 2014;
   Otto 2017; Inoue & Todo 2019; Guan 2020) are all non-European applications (US, global, Japan). No European
   economic-model precedent is cited anywhere in the manuscript. The natural additions are Koks & Thissen 2016
   (already in the .bib, MRIA demonstrated on Rotterdam floods at pan-European scale), Koks et al. 2019 (ERL, the
   EU-wide flood application), Pichler & Farmer 2022 (Germany, Italy, Spain) and, for the Austrian CGE + ABM
   line, Bachner et al. 2024. For the drought itself, Naumann et al. 2021 and Cammalleri et al. 2020 are the
   EU-wide costings the paper should position against (direct losses only; inland waterway transport about
   1.5 % of them).

---

## 1. Synthesis (one page)

**Four families of Europe-wide or multi-country economic models have been applied to disasters and disruptions;
none routes goods on a transport network, none has firm agents at EU scale, and none has a weekly stock-out
mechanism.**

**(A) EU-scale CGE and integrated assessment of climate impacts (JRC PESETA line and its descendants).**
PESETA I-IV feed biophysical damages (river and coastal floods, agriculture, energy, drought, heat, mortality)
into a European CGE (GEM-E3 in PESETA I-II; the PESETA IV Task 14 report does not name the model) and report
welfare losses: 0.2-1 % of annual household welfare if the 2080s climate occurred today (Ciscar et al. 2011,
PNAS); about EUR 190 bn, almost 2 % of EU GDP, in PESETA II, more than half of it mortality; a 2 C world halving
the loss of a 3 C world and 1.5 C cutting it by 75 % in PESETA IV. Dottori et al. (2018, NCC) attach welfare
losses of 0.23-0.29 % (1.5 C) and 0.4 % (2 C) to river-flood damage. Heat enters as labour productivity in a
GTAP-based regional CGE with 274 regions (NUTS2 where available): the hot years 2003, 2010, 2015 and 2018 cost
0.3-0.5 % of European GDP, some southern regions above 1 % (Garcia-Leon et al. 2021, Nat. Commun.). Drought is
costed with damage functions without any propagation: EUR 9 bn a year for the EU and UK today, above EUR 65 bn
at 4 C (Naumann et al. 2021, NCC); in that accounting, inland waterway transport is about 1.5 % of direct drought
losses (Cammalleri et al. 2020, PESETA IV Task 7), agriculture 39-60 %, energy 22-48 %. Newer EU-wide CGEs put
NUTS2 regions in recursive dynamics: Knittel et al. (2024, ESR) find river-flood risk in 2050 lowering regional
GDP by up to 0.5 % and welfare by up to 1 % under current insurance systems; Dunne et al. (2026, Sci. Rep.;
EU-EMS, 234 NUTS2 regions, 5-year steps to 2100) find EUR 826 bn to 1.41 tn of damages by 2100 and up to -51 %
of GDP in one region; Mongelli et al. (2023) find coastal floods costing 0.25-0.91 % of EU27+UK output a year by
2100, about twice the direct damage. In all of these, transport is a service sector or a trade margin, the time
step is a year or longer, inventories do not exist, and the shock is a loss of capital or of productivity.
Austrian national CGE work (Steininger et al. 2016; Bachner 2017) shows macroeconomic feedback magnifying
sectoral damages up to fourfold and indirect costs of land-transport damage more than doubling direct costs.

**(B) Multiregional input-output, supply-use and programming models of specific events.** The only continent-
scale indirect-loss model of a hazard is MRIA (Koks & Thissen 2016; Koks et al. 2019, ERL): a recursive-dynamic
multiregional supply-use model with linear programming over 270 NUTS2 regions, recovery within about a year,
substitution only along existing trade links ("we do not simulate the creation of new trade relations"), no
transport cost and no inventories. It finds that up to 60 % of indirect flood losses can be offset through
alternative suppliers, that indirect losses rise 65 % more than direct damages as events grow, and expected annual
indirect losses of EUR 0.3 bn rising to 1.2 bn at 3 C against direct damages of 1.6 bn rising to 5.5 bn. Its 2026
extension adds inter-regional trade-capacity constraints (Vanniya Perumal et al. 2026, ESR; SoA
`vanniyaperumal2026mria`), the closest an EU MRIO has come to a capacity gate, still annual and without a
network. The model comparison of Koks et al. (2016, NHESS) on two Po-basin flood scenarios shows two hybrid IO
models and a CGE (Carrera et al. 2015) disagreeing by up to a factor of 7. German and Central European floods
were costed with MRIO and flood-footprint models (Schulte in den Baeumen et al. 2015; Mendoza-Tinoco et al.
2020: indirect losses 65 % of the total for the 2009 Central European floods), with a supply-side Ghosh model
(Sieg et al. 2019: indirect EUR 1.1-1.6 bn against direct 1.5-2.1 bn for 2013) and with the Groningen non-linear
programming model (Oosterhaven & Toebben 2017), whose authors argue that fixed-share MRIO models give implausibly
large indirect losses. The same programming model applied to Russian gas cut-offs on a 6-region, 6-sector table
finds negligible macro effects for Europe (Bouwmeester & Oosterhaven 2017). Pandemic and energy shocks were run
on dynamic IO models at national or three-country scale: Pichler & Farmer (2022) show that rationing rules and
input bottlenecks decide the outcome for Germany, Italy and Spain; Reissl et al. (2022) reproduce Italy's 2020
path with an interregional computational IO model; the Austrian gas shock was run on a dynamic out-of-equilibrium
IO model at industry level even by the firm-network group (Pichler et al. 2024, JEBO); Bachmann et al. (2024)
put a Russian energy stop at 0.5-3 % of German GDP; the IMF's EU-wide gas models put the Hungarian, Slovak and
Czech shortages at up to 40 % of consumption and GDP at up to -6 % (Di Bella et al. 2022). The JRC's RHOMOLO CGE
produced the NUTS2 map of COVID-19 (Conte et al. 2020; Sakkas et al. 2021). The ECB's production-network paper on
physical climate risk is a global IO exercise (Fahr et al. 2024: euro-area losses up to 30 times the direct
impact through trade), and its weather work is econometric (Andersson et al. 2026, SVAR).

**(C) Global agent-based loss propagation (Acclimate) with European results.** Covered in the companion dossier
(section B there). For this strand the relevant points are that Acclimate runs daily on region-sector agents
with storages and a transport time penalty but no network, that the EU appears only as a region "better
positioned to absorb imported production losses" from projected floods (Willner et al. 2018, NCC; SoA
`willner2018floods`), and that consecutive extremes amplify welfare losses by 21 % on average (Kuhla et al. 2021,
ERL; SoA `kuhla2021resonance`), the sector-level analogue of our two-trough result. No European event has been
simulated on it with an explicit transport constraint.

**(D) Firm-level production networks and national ABMs in Europe (Thurner group, IIASA, Dutch data).** Nation-
wide firm networks exist for Hungary (VAT data: Diem et al. 2022; Stangl et al. 2024; Diem et al. 2024), for an
unnamed "medium-sized European country" from mobile-phone data (Reisch et al. 2022) and for the Netherlands by
reconstruction (Ialongo et al. 2022). Their shock model is a generalized Leontief cascade without inventories,
iterated to a fixed point in steps that are not real time, on a static network: 32 Hungarian firms each put about
23 % of national production at risk; aggregating to industries understates losses by up to 37 %. The Austrian
flood work combines a CGE and the IIASA/CSH macroeconomic ABM of millions of households and firms fed with sector
capital damages (Bachner et al. 2024, Risk Analysis; Poledna et al. 2018 preprint; Hochrainer-Stigler et al.
2024), giving distributional indirect risks but no spatial transport channel. These are single-country models; no
firm-level model spans the EU, and none has been applied to a drought or a transport disruption.

**What no Europe-wide economic model has done so far**: (i) routed shipments on the physical multimodal network
with capacities, mode switching and route-specific surcharges (all EU-wide models move goods as trade flows,
Armington shares or transport margins; MRIA has no transport cost at all, its 2026 extension a trade-capacity
bound; Acclimate has a time penalty); (ii) represented firms as located agents across the whole EU (firm networks
are national and mostly static); (iii) run at weekly resolution on an event calendar (CGEs annual or 5-yearly,
MRIA an equilibrium within a year, Acclimate daily but on sector agents); (iv) generated losses through a
stock-out mechanism, i.e. per-input inventories with survey-based criticality that let production fall only when
a critical input runs out (ARIO, Acclimate and Pichler et al. 2022 have inventories at sector level; the
Hungarian cascades have none); (v) costed a drought or low-water event through the transport channel at all, let
alone separated the freight-bill channel from the shortage channel (PESETA treats inland waterway losses as
1.5 % of direct drought damage and does not propagate them; the Rhine 2018 economics is statistical or
transport-economic; the only other economic model of a low-water event is a static CGE of the 2022-23
Mississippi low water with a barge-rate channel only, Chen et al. 2025, SoA `chen2025mississippi`); (vi) tested
the modelled indirect loss against an observed event benchmark (Koks et al. 2019 note that wider economic
impacts are poorly documented in Europe [S]; the European exception is Reissl et al. 2022 on Italy 2020).

---

## 2. Table of works

Columns: authors; year; short title; venue; DOI (with verification tags, or "SoA `key`" when the companion
dossier verified the record); region/scale; hazard; method class; spatial unit; transport representation;
inventories/dynamics (yes-no; time step); key finding with numbers; one-line relevance to our positioning.

### A. EU-scale CGE / integrated assessment of climate impacts (none in the companion dossier)

| Authors | Year | Short title | Venue | DOI [tags] | Region/scale | Hazard | Method class | Spatial unit | Transport | Inventories / dynamics | Key finding (numbers) | Relevance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ciscar, Iglesias, Feyen et al. | 2011 | Physical and economic consequences of climate change in Europe (PESETA I) | PNAS 108(7):2678-2683 | 10.1073/pnas.1011612108 [C] | EU | floods, coasts, agriculture, tourism, health | CGE (GEM-E3) with bottom-up damage models | EU macro-regions (5) | service sector / trade margins | no / comparative static (2080s climate on today's economy) | household welfare loss 0.2-1 % per year for the four market impacts; Northern Europe the only net gainer | the canonical EU-wide economic assessment: annual, aggregate, no propagation dynamics |
| Ciscar (ed.), JRC | 2014 | Climate impacts in Europe: PESETA II | JRC report EUR 26586 EN | 10.2791/7409 [OP] | EU | ten impact areas, eight fed to the macro model | CGE (GEM-E3 per PESETA documentation) | EU regions | implicit | no / static | EUR 190 bn welfare loss, almost 2 % of EU GDP (2080s climate today, no adaptation); EUR 120 bn of it premature mortality; 2 C cuts it to EUR 120 bn (1.2 %) | shows what "EU-wide economic model of climate hazards" has meant: capital/productivity shocks, no logistics |
| Soria (ed.), JRC | 2018 | Climate impacts in Europe: PESETA III final report | JRC report EUR 29427 EN | 10.2760/93257 [OP] | EU | eleven impact areas, six with welfare losses | CGE + sector models | EU regions | implicit (the separate PESETA III inland-waterway task is Christodoulou et al. 2020, already cited) | no / static | north-south divide; most welfare losses greatly reduced at 2 C (no figures on the OP page) | the economic module of PESETA III never saw the river |
| Szewczyk, Feyen, Ciscar, Matei, Mulholland, Soria | 2020 | Economic analysis of selected climate impacts (PESETA IV Task 14) | JRC report EUR 30199 EN | 10.2760/845605 [OP] | EU | river floods, coastal floods, agriculture, energy supply, droughts, windstorms, mortality | CGE welfare analysis | EU regions | implicit | no / static | mortality dominates; southern regions several times northern; 2 C halves impacts vs 3 C; 1.5 C lowers welfare loss by 75 % | the latest EU-wide economic synthesis of hazards; drought enters as sector damage, not as a logistics shock |
| Feyen, Ciscar, Gosling, Ibarreta, Soria (eds), JRC | 2020 | Climate change impacts and adaptation in Europe (PESETA IV final) | JRC report EUR 30180 EN | 10.2760/171121 [OP] | EU | heat, water scarcity, drought, fires, floods, agriculture | synthesis | EU regions | implicit | no | southern regions much more affected; adaptation cost-effective (no numbers on the OP page) | umbrella reference for the JRC line |
| Cammalleri, Naumann, Mentaschi et al. | 2020 | Global warming and drought impacts in the EU (PESETA IV Task 7) | JRC report EUR 29956 EN | 10.2760/597045 [OP] | EU+UK | drought | damage functions by sector | NUTS2/3 regions | none (inland waterway transport is one damage category) | no / annual expected loss | EUR 9 bn/yr today (ES 1.5, IT 1.4, FR 1.2 bn); about 5x at 3 C; agriculture 39-60 %, energy 22-48 %, public water 9-20 %, inland waterway transport about 1.5 %, infrastructure subsidence 8 % | the only EU-wide costing of drought that includes inland navigation: 1.5 % of direct loss, no propagation. Our mechanism starts where this stops |
| Naumann, Cammalleri, Mentaschi, Feyen | 2021 | Increased economic drought impacts in Europe with anthropogenic warming | Nat. Clim. Change 11:485-491 | 10.1038/s41558-021-01044-3 [C][P] | EU+UK | drought | damage functions, no economic model for indirect effects | regions | none | no / annual | EUR 9 bn/yr today, above EUR 65 bn/yr at 4 C without adaptation; about 2x relative to GDP; agriculture output -10 % in S/W Europe at 4 C; below 2 C avoids most impacts | the headline EU drought economics is direct-loss accounting; nothing on supply chains or low water |
| Motta, Naumann, Gomez, Formetta, Feyen | 2025 | Assessing the economic impact of droughts in Europe in a changing climate: multi-sectoral regional analysis | J. Hydrol.: Reg. Stud. 59:102296 | 10.1016/j.ejrh.2025.102296 [C][P via OpenAlex] | EU+UK+NO+CH | drought | hazard x exposure x vulnerability | 1,366 territorial units | none | no / annual | losses up to 1-2 % of GDP in the most affected regions; agriculture could lose about 15 % of GVA at high warming | finest-resolution EU drought costing; still no transport or propagation |
| Dottori, Szewczyk, Ciscar et al. | 2018 | Increased human and economic losses from river flooding with anthropogenic warming | Nat. Clim. Change 8:781-786 | 10.1038/s41558-018-0257-z [C][P] | global, EU detail | river floods | hydrological ensemble + damage + macroeconomic welfare (model not named in the abstract) | countries | implicit | no / static | at 1.5 C: deaths +70-83 %, direct damage +160-240 %, welfare -0.23 to -0.29 %; at 2 C welfare -0.4 % | the JRC flood-to-welfare chain: direct damage to a macro model, no event dynamics |
| Garcia-Leon, Casanueva, Standardi, Burgstall, Flouris, Nybo | 2021 | Current and projected regional economic impacts of heatwaves in Europe | Nat. Commun. 12:5807 | 10.1038/s41467-021-26050-z [C][P] | EU27+UK+EFTA | heat (labour productivity) | regional CGE (GTAP-based, GTAP 8, 2007 base) | 274 regions, NUTS2 where available | transport only as a service sector | no / comparative static by year | 2003/2010/2015/2018 heatwaves cost 0.3-0.5 % of European GDP vs 0.2 % average 1981-2010; some regions above 1 %, a few above 2 %; about 5x by 2055-2064 (about 1.1 % of GDP) under RCP8.5 | the closest EU-wide, NUTS2 economic study of a weather extreme in Nature Communications: productivity shock, no logistics, no weekly dynamics |
| Szewczyk, Mongelli, Ciscar | 2021 | Heat stress, labour productivity and adaptation in Europe | ERL 16:105002 | 10.1088/1748-9326/ac24cf [C] | EU | heat | regional/occupational productivity analysis | NUTS2 | none | no | productivity 1.6 % lower in the 2080s; up to 5.4 % in Greece; wearable robotics cut damages 30-40 % | heat economics at regional level; direct channel only |
| Orlov, Sillmann, Aaheim, Aunan, Mistry | 2019 | Economic losses of heat-induced reductions in outdoor worker productivity: Europe | Econ. Disasters Clim. Change 3:191-211 | 10.1007/s41885-019-00044-0 [C][P] | Europe (10 most affected countries) | heat waves 2003, 2010, 2015 | meteorological-epidemiological costing (GTAP wage data; CGE use not confirmed from the abstract) | countries | none | no | direct losses USD 59-90 per worker in agriculture and 41-72 in construction; social costs USD 2-3 per capita | event-based heat costing; no propagation |
| Knittel, Jury, Bednar-Friedl, Bachner, Steiner | 2020 | Global heat-related labour productivity losses: implications for Germany's foreign trade | Climatic Change 160:251-269 | 10.1007/s10584-020-02661-1 [C] | global, Germany focus | heat | CGE with trade | countries | implicit (trade) | no | productivity -31 % (RCP4.5) to -38 % (RCP8.5) in SE Asia and Middle East by 2050; Germany GDP up to -0.41 %, welfare -0.46 % through trade | the trade-channel logic for Germany at annual CGE resolution |
| Bosello, Nicholls, Richards, Roson, Tol | 2012 | Economic impacts of climate change in Europe: sea-level rise | Climatic Change 112:63-81 | 10.1007/s10584-011-0340-1 [C][P] | Europe | sea-level rise | DIVA + GTAP-EF CGE | countries | implicit | no / 2020s, 2080s | Malta loses 12 % of land, Greece 3.5 %; largest losses Poland (USD 483 M) and Germany (391 M); max GDP effect -0.046 % (Poland); protection above 85 % when optimal | typical CGE result: tiny GDP effects once substitution and trade adjust |
| Knittel, Tesselaar, Botzen, Bachner, Tiggeloven | 2024 | Who bears the indirect costs of flood risk? Insurance systems in Europe under climate change | Econ. Syst. Res. 36(1):131-160 | 10.1080/09535314.2023.2272211 [C][P via OpenAlex] | EU | river floods | multi-regional CGE for 2050 | countries/regions | implicit | no / 2050 snapshot | flood risk lowers regional GDP by up to 0.5 %, welfare up to 1 %, private consumption 0.5 %, public consumption 2.4 %; risk-sharing, mandatory purchase and public reinsurance ease the losses | EU-wide indirect flood costs via public budgets and insurance: a dimension we do not model |
| Dunne, Chatzivasileiadis, Ivanova, Filatova et al. | 2026 | Climate-driven flooding widens economic inequalities across EU regions | Sci. Rep. 16:28049 | 10.1038/s41598-026-58068-y [C][P] | EU27 | river and coastal floods | recursive-dynamic CGE (EU-EMS, PBL) | 234 NUTS2, 63 sectors aggregated to 8 | implicit | no / 5-year steps 2025-2100 | damages EUR 826 bn (2 C) to 1.41 tn (3 C) by 2100; Latvia -51 % GDP (3 C); low-income regions -4.5 % vs very-high-income -0.8 %; Theil inequality +65 % | the newest EU NUTS2 dynamic CGE of a hazard: 5-year steps, no event calendar, no logistics |
| Mongelli, Vousdoukas, Feyen et al. | 2023 | Long-term economic impacts of coastal floods in Europe: a probabilistic analysis | AIMS Environ. Sci. 10(5):593-608 | 10.3934/environsci.2023033 [C] | EU27+UK | coastal floods | dynamic stochastic economic model | countries | implicit | no / to 2100 | under RCP8.5, 0.25-0.91 % of output lost every year by 2100, about twice the direct damages | indirect-to-direct ratio of about 2 at EU scale for coastal floods |
| Steininger, Bednar-Friedl, Formayer, Koenig | 2016 | Consistent economic cross-sectoral climate change impact scenario analysis: Austria | Climate Services 1:39-52 | 10.1016/j.cliser.2016.02.003 [C][P via S2] | Austria | eleven impact fields | eleven impact models linked to a multi-sectoral CGE | national | implicit | no / mid-century | macroeconomic feedbacks magnify sectoral damages up to fourfold; net costs 2-4x current damage levels by mid-century | national CGE benchmark for "indirect multiplies direct" |
| Bachner | 2017 | Economy-wide effects of climate change adaptation options of land transport systems in Austria | Reg. Environ. Change 17:929-940 | 10.1007/s10113-016-1089-x [C][P via S2] | Austria | climate damage to road and rail | CGE | national | transport as damaged capital and service sector, no network | no / annual | indirect costs more than double direct costs; with adaptation GDP and welfare losses fall 55 % and 34 %; rail adaptation pays off directly, road only once indirect effects count | the one European CGE on transport-system damage: no routing, no shipments, annual |

### B. Multiregional IO, supply-use, programming and dynamic IO models of specific European events (floods, pandemics, energy)

| Authors | Year | Short title | Venue | DOI [tags] | Region/scale | Hazard | Method class | Spatial unit | Transport | Inventories / dynamics | Key finding (numbers) | Relevance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Koks, Thissen | 2016 | A Multiregional Impact Assessment Model for disaster analysis (MRIA) | Econ. Syst. Res. 28(4):429-449 | 10.1080/09535314.2016.1232701 [C][P]; refs.bib `koks2016` | pan-European | floods (three Rotterdam events) | recursive-dynamic multiregional supply-use model with linear programming | NUTS2 regions | trade flows; no transport cost or network | no inventories / recursive dynamic, short run | most neighbouring regions gain from reconstruction demand while the hit region's capacity binds; distant regions lose a little through production inefficiencies | the first EU-wide disaster model; in refs.bib and uncited |
| Koks, Thissen, Alfieri, de Moel, Feyen, Jongman, Aerts | 2019 | The macroeconomic impacts of future river flooding in Europe | ERL 14:084042 | 10.1088/1748-9326/ab3306 [C][P]; SoA `koks2019floods` | EU (continent-scale) | river floods (6,885 events, LISFLOOD, 7 climate projections) | MRIA | 270 NUTS2 regions (2013 data) | bilateral trade flows between regions; substitution only along existing links; no transport cost | no inventories / equilibrium within about one year, annual expected losses | indirect losses offset by up to 60 % through alternative suppliers; losses up to +350 % with warming; indirect rise 65 % more than direct; commercial services about +980 %, utilities +580 %; EAD direct EUR 1.6 bn to 5.5 bn (3 C), indirect 0.3 bn to 1.2 bn | the direct EU-wide precedent for indirect hazard losses: our paper differs on every axis (firm agents, network routing, weekly, inventories, drought) |
| Vanniya Perumal, Thissen, de Ruiter, Koks | 2026 | Trade capacity constraints in MRIA | Econ. Syst. Res. online | 10.1080/09535314.2026.2728049; SoA `vanniyaperumal2026mria` (not re-verified here) | multi-regional, generic | generic disasters | MRIA with inter-regional trade-capacity (logistic) constraints | regions | capacity bound on trade between regions; no network | no / annual | raising production capacity alone is insufficient; trade flexibility needed | the closest an EU MRIO has come to a logistics constraint; still annual, no routing, no modes |
| Koks, Carrera, Jonkeren, Aerts, Husby, Thissen, Standardi, Mysiak | 2016 | Regional disaster impact analysis: comparing IO and CGE models | NHESS 16:1911-1924 | 10.5194/nhess-16-1911-2016 [C]; SoA `koks2016comparing` | Italy (Po basin), national losses | floods (two scenarios) | two hybrid IO models and one CGE | Italian regions | implicit | varies / short vs long recovery | total national losses and their regional distribution differ by up to a factor of 7 across models | the model-dependence problem that our event-specific benchmark (2018) addresses |
| Carrera, Standardi, Bosello, Mysiak | 2015 | Direct and indirect economic impacts of a flood event: spatial + CGE modelling | Environ. Model. Softw. 63:109-122 | 10.1016/j.envsoft.2014.09.016 [C]; SoA `carrera2015flood` | Italy (Po River basin flood) | flood | spatial damage assessment coupled to a sub-national CGE | Italian regions | implicit | no / annual | numbers not retrieved [U] | the CGE side of the Koks et al. 2016 comparison |
| Mendoza-Tinoco, Hu, Zeng, Chalvatzis, Zhang, Steenge, Guan | 2020 | Flood footprint assessment: 2009 Central European floods | Risk Analysis 40(8):1612-1631 | 10.1111/risa.13497 [C]; SoA `mendozatinoco2020flood` | Central Europe (multiregional) | floods 2009 | flood-footprint (ARIO-type) multiregional IO | countries/regions | implicit | yes (ARIO lineage) / recovery dynamics | indirect losses 65 % of the total; 70 % of indirect losses in four industries | a multi-country European ARIO-type application; sector agents, no transport |
| Oosterhaven, Toebben | 2017 | Wider economic impacts of heavy flooding in Germany: non-linear programming | Spatial Econ. Anal. 12(4):404-428 | 10.1080/17421772.2017.1300680 [C][P via S2]; SoA `oosterhaven2017flooding` | Germany | 2013 flood | interregional non-linear programming (minimum information gain) | German regions x industries | implicit (trade pattern) | no / short run | government support of local final demand substantially reduces indirect losses; disaster at the top of the cycle increases them; fixed-share MRIO gives implausibly large indirect losses; nationwide gross output -EUR 3.27 bn [S] | the main methodological critique of MRIO disaster estimates in Europe (method paper: Oosterhaven & Bouwmeester 2016, SoA `oosterhaven2016disruptive`) |
| Bouwmeester, Oosterhaven | 2017 | Economic impacts of natural gas flow disruptions between Russia and the EU | Energy Policy 106:288-297 | 10.1016/j.enpol.2017.03.030 [C][P] | EU + Russia | gas cut-off (four scenarios) | non-linear programming on an international IO table | 6 regions x 6 sectors | implicit | no / short run | negligible effects at the whole-economy level for Europe; GDP mostly positive for European regions, welfare slightly negative | an EU-wide energy-disruption IO exercise at very coarse resolution |
| Schulte in den Baeumen, Toebben, Lenzen | 2015 | Labour forced impacts and production losses due to the 2013 flood in Germany | J. Hydrol. 527:142-150 | 10.1016/j.jhydrol.2015.04.030 [C] | Germany | 2013 flood | high-resolution IO model; labour-forced production losses from short-time-work data | German regions | implicit | no | economic damages about EUR 10 bn [S]; production-capacity losses reused by Oosterhaven & Toebben 2017 | German flood IO precedent |
| Sieg, Schinko, Vogel, Mechler, Merz, Kreibich | 2019 | Integrated assessment of short-term direct and indirect economic flood impacts with uncertainty | PLoS ONE 14(4):e0212932 | 10.1371/journal.pone.0212932 [C][P] | Germany (8 Laender) | 2013 flood (Elbe, Danube) | object-level direct damage + supply-side (Ghosh price) IO | 8 federal states x 19 sectors | none | no / static | direct EUR 1.5-2.1 bn, indirect 1.1-1.6 bn (90 % intervals); indirect/direct 0.7-0.9, above 1 in manufacturing | indirect-to-direct ratios for a German flood |
| Koks, Bockarjova, de Moel, Aerts | 2015 | Integrated direct and indirect flood risk modeling | Risk Analysis 35(5):882-900 | 10.1111/risa.12300 [C][P via S2] | Netherlands (Rotterdam port region) | floods (1/10 to 1/10,000) | Cobb-Douglas production loss + hybrid IO recovery | regional | implicit | recovery dynamics, no inventories | direct EAD about 50 % larger than indirect; indirect exceeds direct for low-probability events | regional IO precedent at a European port |
| Koks, Pant, Thacker, Hall | 2019 | Business disruption and economic losses due to electricity failures and flooding | Int. J. Disaster Risk Sci. 10:421-438 | 10.1007/s13753-019-00236-y [C]; SoA `koks2019electricity` | UK | flood + power failure | MRIA-type with infrastructure | 37 subnational regions | electricity network explicit, no freight | no / annual | compound failure raises total losses by up to 300 % | infrastructure-coupled IO in Europe, no freight routing |
| Hallegatte, Ranger, Mestre, Dumas, Corfee-Morlot, Herweijer, Wood | 2011 | Climate change, sea level rise and storm surge risk in port cities: Copenhagen | Climatic Change 104:113-137 | 10.1007/s10584-010-9978-3 [C][P] | Copenhagen | storm surge | catastrophe risk assessment + IO model (ARIO lineage) | city | none | ARIO-type dynamics | direct and indirect losses, jobs and reconstruction time; value of higher sea defences (no numbers in abstract) | the only ARIO application to a European city found |
| Jongman, Hochrainer-Stigler, Feyen, Aerts, Mechler, Botzen, Bouwer, Pflug, Rojas, Ward | 2014 | Increasing stress on disaster-risk finance due to large floods | Nat. Clim. Change 4:264-268 | 10.1038/nclimate2124 [C][P] | pan-European | river floods | probabilistic loss modelling with copula dependence; risk finance | basins/countries | none | no | extreme discharges strongly correlated across European basins; extreme loss events could more than double in frequency by 2050 | the IIASA systemic-risk line for Europe: correlated direct losses, no propagation |
| Pichler, Farmer | 2022 | Simultaneous supply and demand constraints in input-output networks: Covid-19 in Germany, Italy and Spain | Econ. Syst. Res. 34(3):273-293 | 10.1080/09535314.2021.1926934 [C][A]; SoA `pichler2022simultaneous` | three EU countries | pandemic | dynamic IO with rationing rules; lower bound on propagation | national x industries | none | no inventories in the bound; rationing dynamics | network effects substantially amplify the initial shocks even in the best case; input bottlenecks and the rationing rule decide the outcome | nearest multi-country European dynamic IO of a shock; industries, not firms; no transport |
| Reissl, Caiani, Lamperti, Guerini, Vanni, Fagiolo, Ferraresi, Ghezzi, Napoletano, Roventini | 2022 | Assessing the economic impact of lockdowns in Italy: a computational input-output approach | Ind. Corp. Change 31(2):358-409 | 10.1093/icc/dtac003 [C][P via OpenAlex] | Italy | pandemic (labour-supply shock) | interregional computational IO, dynamic | Italian regions x sectors | implicit | yes (per model class) / sub-annual dynamics | reproduces the observed spring-2020 dynamics in-sample and autumn-winter 2020 out of sample | a European dynamic IO validated on an observed path, at regional scale |
| Conte, Lecca, Sakkas, Salotti | 2020 | The territorial economic impact of COVID-19 in the EU: a RHOMOLO analysis | JRC policy insight JRC121261 | no DOI [P JRC repository] | EU | pandemic | spatial CGE (RHOMOLO) | NUTS2 | implicit | no / annual | supported the Commission's recovery plan of 27 May 2020 (no regional numbers on the page) | the JRC's EU-wide NUTS2 CGE applied to a shock; no hazard application found |
| Sakkas, Crucitti, Conte, Salotti | 2021 | The 2020 territorial impact of COVID-19 in the EU: a RHOMOLO update | JRC policy insight JRC125536 | no DOI [P JRC repository] | EU | pandemic | spatial CGE (RHOMOLO) | NUTS2 | implicit | no / annual | regional results consistent with Eurostat country totals; considerable regional differences | same |
| Bachmann, Baqaee, Bayer, Kuhn, Loeschel, Moll, Peichl, Pittel, Schularick | 2024 | What if? Macroeconomic and distributional effects for Germany of a stop of energy imports from Russia | Economica 91(364):1157-1200 | 10.1111/ecca.12546 [C] (policy-brief version in refs.bib as `bachmann2022`) | Germany | energy import stop | multi-sector open-economy production-network model (Baqaee-Farhi) + aggregate production function | national x sectors | none | no / comparative static | short-run output loss 0.5-3 % of GDP; substitution and reallocation along supply chains make it "substantial but manageable" | the peer-reviewed energy-shock benchmark for Germany; nested-CES, no dynamics |
| Pichler, Hurt, Reisch, Stangl, Thurner | 2024 | Economic impacts of a drastic gas supply shock and short-term mitigation strategies | J. Econ. Behav. Organ. 227:106750 | 10.1016/j.jebo.2024.106750 [C][A] | Austria | gas supply cut (Russian imports) | techno-economic mapping + dynamic out-of-equilibrium IO model (industry level) | national x industries | none | sector inventories (per model class); dynamic | outcomes range from mild to severe with mitigation; levers: alternative imports, storage management, fuel switching; a CSH release quotes several hundred million EUR per month of GVA [S] | even the firm-network group ran the gas shock at industry level: no firm-level shock model exists in Europe for an energy or logistics event |
| Di Bella, Flanagan, Foda et al. | 2022 | Natural gas in Europe: the potential impact of disruptions to supply | IMF WP 22/145 | 10.5089/9798400215292.001 [C] | EU | gas cut-off | gas-balance + multi-sector/CGE-type assessment | countries | pipelines implicit (infrastructure bottlenecks discussed) | no | alternative sources replace up to 70 % of Russian gas; HU, SK, CZ shortages up to 40 % of consumption and GDP up to -6 %; most others under 1 % | EU-wide energy-shock reference with national resolution |
| Lan, Sher, Zhou | 2022 | The economic impacts on Germany of a potential Russian gas shutoff | IMF WP 22/144 | 10.5089/9798400215285.001 [C] | Germany | gas cut-off | multi-sector model | national | none | no / annual | German GDP -1.5 % (2022), -2.7 % (2023), -0.4 % (2024) vs baseline; inflation +2 pp | national energy-shock benchmark |
| Fahr, Senner, Vismara | 2024 | The globalization of climate change: amplification of physical risks through input-output linkages | ECB Working Paper 2942 | no DOI exposed [R] | global, euro-area results | climate-related physical risks (GDP-at-risk) | global IO propagation | countries x sectors | none | no / static | trade can make euro-area losses up to 30 times higher than direct impacts; substitution across country-sectors can also reduce losses | the ECB's model-based physical-risk paper: static IO, no logistics |
| Andersson, Battistini, Bobasu | 2026 | Heatwaves, coldwaves, floods, and droughts: short-term impact of extreme weather on activity | ECB Working Paper 3203 | no DOI exposed [R] | DE, FR, IT, ES | temperature and precipitation extremes | structural Bayesian VAR (econometric, not a structural model) | countries | none | no / 12-month horizon | temperature extremes hit industry and energy (Germany most exposed to heatwaves); precipitation extremes hit construction and mining (Spain most exposed to floods and droughts) | central-bank weather work is econometric; it cannot say where a loss is generated, which is our argument against the Ademmer-type statistics |

### C. Global agent-based loss propagation with European results (Acclimate)

All Acclimate papers are tabulated in the companion dossier (section B there). The two with European results
used in this strand: Willner, Otto & Levermann 2018, Nat. Clim. Change 8:594-598, 10.1038/s41558-018-0173-2
(SoA `willner2018floods`): global flood losses +17 % over 20 years, EU "better positioned to absorb imported
production losses"; Kuhla et al. 2021, ERL 16:114010, 10.1088/1748-9326/ac2932 (SoA `kuhla2021resonance`):
consecutive extremes amplify welfare loss by 21 % on average across more than 7,000 regional sectors and 1.8 M
trade relations. Both daily, sector-region agents, storages, transport as a time penalty, no network, no
European event with a transport constraint.

### D. Firm-level production networks and national ABM/CGE work in Europe

| Authors | Year | Short title | Venue | DOI [tags] | Region/scale | Hazard | Method class | Spatial unit | Transport | Inventories / dynamics | Key finding (numbers) | Relevance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reisch, Heiler, Diem, Klimek, Thurner | 2022 | Monitoring supply networks from mobile phone data for estimating the systemic risk of an economy | Sci. Rep. 12:13347 | 10.1038/s41598-022-13104-5 [C][P]; SoA `reisch2022mobile` | one "medium-sized European country" (not named; Austria per the group's communication) | firm defaults | firm-level network from call records (125 days, autumn 2020) + generalized Leontief cascade | firms | none | no inventories / iterative cascade | strong communication link implies about 90 % probability of a supply link; about 65 firms across 22 sectors could cause massive damage | national firm network, static cascade, no logistics |
| Stangl, Borsos, Diem, Reisch, Thurner | 2024 | Firm-level supply chains to minimize unemployment and economic losses in rapid decarbonization | Nat. Sustain. 7:581-589 | 10.1038/s41893-024-01321-x [C][P]; SoA `stangl2024decarbonization` | Hungary | policy shock (removal of emitting firms) | firm-level network cascade | firms (Hungarian VAT network) | none | no | for a 20 % emissions cut, the optimal strategy loses about 2 % of jobs and output; targeting the largest emitters first loses 28 % of jobs and 33 % of output | firm-level European network used for counterfactual shocks; no hazards, no transport |
| Diem, Borsos, Reisch, Kertesz, Thurner | 2024 | Loss of economic predictability from aggregating firm-level production networks | PNAS Nexus 3(3):pgae064 | 10.1093/pnasnexus/pgae064 [C]; SoA `diem2024aggregation` | Hungary | firm failures | firm vs industry network cascades | firms vs industries | none | no | industry-level networks understate losses by up to 37 %; firms sell only 23.5 % to and buy 19.3 % from their own industry | the argument for firm resolution that our EU-wide design rests on |
| Ialongo, de Valk, Marchese, Jansen, Zmarrou, Squartini, Garlaschelli | 2022 | Reconstructing firm-level interactions in the Dutch input-output network from production constraints | Sci. Rep. 12:11847 | 10.1038/s41598-022-13996-3 [C]; SoA `ialongo2022reconstructing` | Netherlands | none (reconstruction) | maximum-entropy network reconstruction from two transaction datasets | firms | none | no | method preserving each firm's in/out flows by product type | the data route to observed Dutch firm networks that our synthetic draw does not use |
| Bachner, Knittel, Poledna, Hochrainer-Stigler, Reiter, Pflug | 2024 | Revealing indirect risks in complex socioeconomic systems: multi-model analysis of flood events in Austria | Risk Analysis 44(1):229-243 | 10.1111/risa.14144 [C] | Austria | floods (sector-specific capital damages) | CGE + macroeconomic ABM | national, sectors, household groups | none | ABM dynamic; CGE static | flood damages pose very different indirect risks to sectors and household groups, short and long term | the European multi-model (CGE vs ABM) flood study; no spatial logistics |
| Poledna, Hochrainer-Stigler, Miess, Klimek, Schmelzer, Sorger, Shchekinova, Rovenskaya, Linnerooth-Bayer, Dieckmann, Thurner | 2018 | When does a disaster become a systemic event? Indirect economic losses from natural disasters | arXiv 1801.09740 (preprint, no journal version found) | 10.48550/arXiv.1801.09740 [A] | Austria | floods (probabilistic damage model with copulas) | 1:1 macroeconomic ABM (millions of households and firms) | national | none | yes (firm stocks per ABM) / monthly-quarterly | moderate disasters: small short-term gains and long-term losses; large ones: immediate lasting losses; a critical disaster size beyond which rebuilding capacity is exceeded | the only large-scale ABM of a European hazard; aggregate agents without location or shipments |
| Poledna, Miess, Hommes, Rabitsch | 2023 | Economic forecasting with an agent-based model | Eur. Econ. Rev. 151:104306 | 10.1016/j.euroecorev.2022.104306 [C][P via OpenAlex] | Austria | COVID-19 lockdown (application) | macroeconomic ABM | national, sectors | none | yes / quarterly | first ABM competitive with VAR and DSGE out of sample, outperforming them at long horizons; used for lockdown effects | European ABMs are macro-forecasting tools, not logistics models |
| Reiter, Knittel, Bachner, Hochrainer-Stigler | 2022 | Barriers to climate risk management against indirect effects of natural disasters: flood risk in Austria | Clim. Risk Manag. 36:100431 | 10.1016/j.crm.2022.100431 [C][P via OpenAlex] | Austria | floods | stakeholder analysis | national | none | no | Austria manages indirect flood risks only marginally; barriers and ways forward listed | governance side of the Austrian indirect-risk programme |
| Hochrainer-Stigler et al. | 2024 | Risk management against indirect risks from disasters: multi-model and participatory framework, flood risk in Austria | Int. J. Disaster Risk Reduct. 106:104425 | 10.1016/j.ijdrr.2024.104425 [C][P via OpenAlex] | Austria | floods | multi-model (IO, CGE, ABM) + participatory process | national | none | mixed | linking indirect and direct risk management is achievable with modest effort | same |

Also in the companion dossier and not repeated: Diem et al. 2022 (refs.bib `diem2022`), Chakraborty et al.
2024 (global firm network, SoA `chakraborty2024inequality`), Pichler et al. 2023 Science policy forum (SoA
`pichler2023alliance`), Bacilieri et al. 2026 (SoA `bacilieri2026networks`), Hurt, Thurner & Klimek 2025
(agent-based extension of IO recovery models on WIOD regions, SoA `hurt2025agentbased`), Fialkowski, Havlin &
Thurner 2026 (Ecuador, SoA `fialkowski2026cascades`).

Boundary notes (searched, nothing found): no published E3ME application to European disaster shocks (COACCH used
the ICES CGE; its synthesis quotes a median EU GDP loss of 2.2 % by 2070 [S, unverified]); no RHOMOLO flood or
climate-hazard application; no Bundesbank model-based flood or low-water analysis (the Rhine dossier already
records that the "Bundesbank -0.2 pp" figure has no primary source); no application of the Inoue-Todo code to a
European firm network; no MRIO or CGE study of the 2018 Rhine low water (the 2018 economics is econometric:
Ademmer et al., already cited; Meuchelboeck 2025 and Horst & Mueller 2024 in the companion dossier).

---

## 3. Gaps our paper fills / does not fill

**Fills (no Europe-wide economic model has done these):**
1. Explicit routing of every shipment on the TEN-T multimodal network with per-class capacities on the Rhine,
   route and mode switching under switching costs, and gauge-dependent surcharges. Every EU-wide model above
   moves goods as trade coefficients, Armington shares or transport margins (CGE, RHOMOLO, EU-EMS), as trade
   flows without cost (MRIA; its 2026 extension adds an inter-regional trade-capacity bound, still annual and
   without a network) or as a time penalty (Acclimate). The one European CGE on transport damage (Bachner 2017)
   treats the network as damaged capital.
2. Firm agents with locations across 28 economies (about 12,000 agents, 1.3 M links). Firm-level networks exist
   for Hungary, Austria (mobile-phone proxy) and the Netherlands only, are static, and have never been joined
   across borders; Diem et al. (2024) quantify why firm resolution matters (losses understated by up to 37 %
   at industry level).
3. Weekly dynamics on an observed event calendar, so that the order and spacing of the troughs can be costed
   (our 1/6 interaction of the two 2026 episodes; the Acclimate "ripple resonance" of 21 % is the sector-level,
   daily analogue on synthetic sequences).
4. A stock-out mechanism: per-input inventories set from balance-sheet statistics, survey-based criticality
   (Pichler et al. 2022) and pooling across regions, so that the loss arises from an empty tank or yard and not
   from a higher freight bill. ARIO, Acclimate and the UK Covid model carry sector-level inventories; the
   Hungarian cascades carry none; no EU-wide model separates the price channel from the quantity channel.
5. A drought costed through the transport channel. The JRC accounting puts inland waterway transport at about
   1.5 % of direct drought losses and does not propagate it; Naumann et al. (2021) include no indirect effects;
   the Rhine 2018 economics is a regression (Ademmer et al.) or transport-economics (Jonkeren et al.); the only
   other economic model of a low-water event is the static CGE of the 2022-23 Mississippi low water with a
   barge-rate channel only (Chen et al. 2025, outside Europe).
6. An event-specific benchmark of the indirect loss (German industrial production, 2018) and a pre-registered
   prospective test. Koks et al. (2019) state that wider economic impacts are poorly documented in Europe [S];
   the European exception is Reissl et al. (2022), who validate an Italian regional dynamic IO on 2020.

**Does not fill (where the other families remain stronger, to be said in the Discussion):**
1. No price-driven demand response, factor reallocation or wage adjustment: CGEs (PESETA, EU-EMS, Knittel 2024)
   capture these and typically find small GDP effects; our fixed-order, pass-through pricing is a short-run
   assumption and should be presented as such (the manuscript already does, Methods and Discussion).
2. No fiscal, insurance or distributional channel (Knittel et al. 2024; Bachner et al. 2024; Jongman et al.
   2014 on risk finance).
3. The supplier-buyer network is synthetic (gravity draw from the ICIO), not an observed VAT network as in
   Hungary; the eleven seeds measure this sampling uncertainty but not the bias.
4. No creation of new trade links, like every model reviewed (Koks 2019; Otto 2017).
5. Single hazard channel: cooling-water, agricultural and energy-price effects of the same drought, which the
   PESETA chain covers, are outside the model.
6. Long-run competitiveness and relocation effects of repeated low waters, a CGE question.
7. "First" claims should be scoped: Koks et al. (2019) is the first continent-scale indirect flood-loss model;
   Dunne et al. (2026) the first EU NUTS2 dynamic CGE of floods; firm-level ABMs exist nationally. Our claim is
   the combination: whole-EU scope, firm agents, explicit network routing with capacities, weekly step,
   inventory/criticality stock-outs, and an event benchmark (same conclusion as the companion dossier's note on
   the "first" claim). Acclimate (daily, global) and Pichler et al. (2022; daily, UK industries) should be
   acknowledged as the finer-time-step precedents.

---

## 4. BibTeX (verified entries not in refs.bib and not in the companion dossier's block; keys lower-case firstauthorYEARkeyword)

Take from the companion dossier's block, not duplicated here: `koks2019floods`, `koks2016comparing`,
`carrera2015flood`, `mendozatinoco2020flood`, `oosterhaven2017flooding`, `oosterhaven2016disruptive`,
`koks2019electricity`, `vanniyaperumal2026mria`, `pichler2022simultaneous`, `willner2018floods`,
`kuhla2021resonance`, `reisch2022mobile`, `stangl2024decarbonization`, `diem2024aggregation`,
`ialongo2022reconstructing`, `chakraborty2024inequality`, `pichler2023alliance`, `chen2025mississippi`.

```bibtex
@article{ciscar2011peseta,
  author  = {Ciscar, Juan-Carlos and Iglesias, Ana and Feyen, Luc and Szab{\'o}, L{\'a}szl{\'o} and Van Regemorter, Denise and Amelung, Bas and Nicholls, Robert and Watkiss, Paul and Christensen, Ole B. and Dankers, Rutger and Garrote, Luis and Goodess, Clare M. and Hunt, Alistair and Moreno, Alvaro and Richards, Julie and Soria, Antonio},
  title   = {Physical and economic consequences of climate change in {Europe}},
  journal = {Proceedings of the National Academy of Sciences},
  year    = {2011},
  volume  = {108},
  number  = {7},
  pages   = {2678--2683},
  doi     = {10.1073/pnas.1011612108}
}

@techreport{ciscar2014peseta2,
  editor      = {C{\'\i}scar, Juan-Carlos},
  author      = {{Joint Research Centre, Institute for Prospective Technological Studies}},
  title       = {Climate impacts in {Europe}: the {JRC} {PESETA} {II} project},
  institution = {Publications Office of the European Union},
  type        = {JRC Scientific and Policy Report},
  number      = {EUR 26586 EN},
  year        = {2014},
  doi         = {10.2791/7409}
}

@techreport{soria2018peseta3,
  editor      = {Soria, Antonio},
  author      = {{Joint Research Centre}},
  title       = {Climate impacts in {Europe}: final report of the {JRC} {PESETA} {III} project},
  institution = {Publications Office of the European Union},
  type        = {JRC Science for Policy Report},
  number      = {EUR 29427 EN},
  year        = {2018},
  doi         = {10.2760/93257}
}

@techreport{szewczyk2020peseta4,
  author      = {Szewczyk, Wojciech and Feyen, Luc and Ciscar, Juan-Carlos and Matei, Alexandra and Mulholland, Eamonn and Soria, Antonio},
  title       = {Economic analysis of selected climate impacts: {JRC} {PESETA} {IV} project, {Task} 14},
  institution = {Publications Office of the European Union},
  type        = {JRC Technical Report},
  number      = {EUR 30199 EN},
  year        = {2020},
  doi         = {10.2760/845605}
}

@techreport{feyen2020peseta4,
  editor      = {Ibarreta, Dolores and Soria, Antonio},
  author      = {{Joint Research Centre}},
  title       = {Climate change impacts and adaptation in {Europe}: {JRC} {PESETA} {IV} final report},
  institution = {Publications Office of the European Union},
  type        = {JRC Science for Policy Report},
  number      = {EUR 30180 EN},
  year        = {2020},
  doi         = {10.2760/171121},
  note        = {The Publications Office record lists Ibarreta and Soria as editors; the JRC citation lists Feyen, Ciscar, Gosling, Ibarreta and Soria}
}

@techreport{cammalleri2020drought,
  author      = {Cammalleri, Carmelo and Naumann, Gustavo and Mentaschi, Lorenzo and Formetta, Giuseppe and Forzieri, Giovanni and Gosling, Simon and Bisselink, Bernard and De Roo, Ad and Feyen, Luc},
  title       = {Global warming and drought impacts in the {EU}: {JRC} {PESETA} {IV} project, {Task} 7},
  institution = {Publications Office of the European Union},
  type        = {JRC Technical Report},
  number      = {EUR 29956 EN},
  year        = {2020},
  doi         = {10.2760/597045}
}

@article{naumann2021drought,
  author  = {Naumann, Gustavo and Cammalleri, Carmelo and Mentaschi, Lorenzo and Feyen, Luc},
  title   = {Increased economic drought impacts in {Europe} with anthropogenic warming},
  journal = {Nature Climate Change},
  year    = {2021},
  volume  = {11},
  number  = {6},
  pages   = {485--491},
  doi     = {10.1038/s41558-021-01044-3}
}

@article{motta2025drought,
  author  = {Motta, Corrado and Naumann, Gustavo and Gomez, Diego and Formetta, Giuseppe and Feyen, Luc},
  title   = {Assessing the economic impact of droughts in {Europe} in a changing climate: a multi-sectoral analysis at regional scale},
  journal = {Journal of Hydrology: Regional Studies},
  year    = {2025},
  volume  = {59},
  pages   = {102296},
  doi     = {10.1016/j.ejrh.2025.102296}
}

@article{dottori2018flood,
  author  = {Dottori, Francesco and Szewczyk, Wojciech and Ciscar, Juan-Carlos and Zhao, Fang and Alfieri, Lorenzo and Hirabayashi, Yukiko and Bianchi, Alessandra and Mongelli, Ignazio and Frieler, Katja and Betts, Richard A. and Feyen, Luc},
  title   = {Increased human and economic losses from river flooding with anthropogenic warming},
  journal = {Nature Climate Change},
  year    = {2018},
  volume  = {8},
  number  = {9},
  pages   = {781--786},
  doi     = {10.1038/s41558-018-0257-z}
}

@article{garcialeon2021heat,
  author  = {Garc{\'\i}a-Le{\'o}n, David and Casanueva, Ana and Standardi, Gabriele and Burgstall, Annkatrin and Flouris, Andreas D. and Nybo, Lars},
  title   = {Current and projected regional economic impacts of heatwaves in {Europe}},
  journal = {Nature Communications},
  year    = {2021},
  volume  = {12},
  pages   = {5807},
  doi     = {10.1038/s41467-021-26050-z}
}

@article{szewczyk2021heat,
  author  = {Szewczyk, Wojciech and Mongelli, Ignazio and Ciscar, Juan-Carlos},
  title   = {Heat stress, labour productivity and adaptation in {Europe}---a regional and occupational analysis},
  journal = {Environmental Research Letters},
  year    = {2021},
  volume  = {16},
  number  = {10},
  pages   = {105002},
  doi     = {10.1088/1748-9326/ac24cf}
}

@article{orlov2019heat,
  author  = {Orlov, Anton and Sillmann, Jana and Aaheim, Asbj{\o}rn and Aunan, Kristin and Mistry, Malcolm},
  title   = {Economic losses of heat-induced reductions in outdoor worker productivity: a case study of {Europe}},
  journal = {Economics of Disasters and Climate Change},
  year    = {2019},
  volume  = {3},
  number  = {3},
  pages   = {191--211},
  doi     = {10.1007/s41885-019-00044-0}
}

@article{knittel2020heat,
  author  = {Knittel, Nina and Jury, Martin W. and Bednar-Friedl, Birgit and Bachner, Gabriel and Steiner, Andrea K.},
  title   = {A global analysis of heat-related labour productivity losses under climate change---implications for {Germany}'s foreign trade},
  journal = {Climatic Change},
  year    = {2020},
  volume  = {160},
  number  = {2},
  pages   = {251--269},
  doi     = {10.1007/s10584-020-02661-1}
}

@article{bosello2012slr,
  author  = {Bosello, Francesco and Nicholls, Robert J. and Richards, Julie and Roson, Roberto and Tol, Richard S. J.},
  title   = {Economic impacts of climate change in {Europe}: sea-level rise},
  journal = {Climatic Change},
  year    = {2012},
  volume  = {112},
  number  = {1},
  pages   = {63--81},
  doi     = {10.1007/s10584-011-0340-1}
}

@article{knittel2024insurance,
  author  = {Knittel, Nina and Tesselaar, Max and Botzen, W. J. Wouter and Bachner, Gabriel and Tiggeloven, Timothy},
  title   = {Who bears the indirect costs of flood risk? {An} economy-wide assessment of different insurance systems in {Europe} under climate change},
  journal = {Economic Systems Research},
  year    = {2024},
  volume  = {36},
  number  = {1},
  pages   = {131--160},
  doi     = {10.1080/09535314.2023.2272211}
}

@article{dunne2026floods,
  author  = {Dunne, Shane M. and Chatzivasileiadis, Theodoros and Ivanova, Olga and Filatova, Tatiana and others},
  title   = {Climate-driven flooding widens economic inequalities across {EU} regions},
  journal = {Scientific Reports},
  year    = {2026},
  volume  = {16},
  pages   = {28049},
  doi     = {10.1038/s41598-026-58068-y}
}

@article{mongelli2023coastal,
  author  = {Mongelli, Ignazio and Vousdoukas, Michalis and Feyen, Luc and others},
  title   = {Long-term economic impacts of coastal floods in {Europe}: a probabilistic analysis},
  journal = {AIMS Environmental Science},
  year    = {2023},
  volume  = {10},
  number  = {5},
  pages   = {593--608},
  doi     = {10.3934/environsci.2023033}
}

@article{steininger2016austria,
  author  = {Steininger, Karl W. and Bednar-Friedl, Birgit and Formayer, Herbert and K{\"o}nig, Martin},
  title   = {Consistent economic cross-sectoral climate change impact scenario analysis: method and application to {Austria}},
  journal = {Climate Services},
  year    = {2016},
  volume  = {1},
  pages   = {39--52},
  doi     = {10.1016/j.cliser.2016.02.003}
}

@article{bachner2017transport,
  author  = {Bachner, Gabriel},
  title   = {Assessing the economy-wide effects of climate change adaptation options of land transport systems in {Austria}},
  journal = {Regional Environmental Change},
  year    = {2017},
  volume  = {17},
  number  = {3},
  pages   = {929--940},
  doi     = {10.1007/s10113-016-1089-x}
}

@article{bouwmeester2017gas,
  author  = {Bouwmeester, Maaike C. and Oosterhaven, Jan},
  title   = {Economic impacts of natural gas flow disruptions between {Russia} and the {EU}},
  journal = {Energy Policy},
  year    = {2017},
  volume  = {106},
  pages   = {288--297},
  doi     = {10.1016/j.enpol.2017.03.030}
}

@article{schulteindenbaumen2015flood,
  author  = {Schulte in den B{\"a}umen, Hagen and T{\"o}bben, Johannes and Lenzen, Manfred},
  title   = {Labour forced impacts and production losses due to the 2013 flood in {Germany}},
  journal = {Journal of Hydrology},
  year    = {2015},
  volume  = {527},
  pages   = {142--150},
  doi     = {10.1016/j.jhydrol.2015.04.030}
}

@article{sieg2019flood,
  author  = {Sieg, Tobias and Schinko, Thomas and Vogel, Kristin and Mechler, Reinhard and Merz, Bruno and Kreibich, Heidi},
  title   = {Integrated assessment of short-term direct and indirect economic flood impacts including uncertainty quantification},
  journal = {PLOS ONE},
  year    = {2019},
  volume  = {14},
  number  = {4},
  pages   = {e0212932},
  doi     = {10.1371/journal.pone.0212932}
}

@article{koks2015rotterdam,
  author  = {Koks, Elco E. and Bo{\v{c}}karjova, Marija and de Moel, Hans and Aerts, Jeroen C. J. H.},
  title   = {Integrated direct and indirect flood risk modeling: development and sensitivity analysis},
  journal = {Risk Analysis},
  year    = {2015},
  volume  = {35},
  number  = {5},
  pages   = {882--900},
  doi     = {10.1111/risa.12300}
}

@article{hallegatte2011copenhagen,
  author  = {Hallegatte, St{\'e}phane and Ranger, Nicola and Mestre, Olivier and Dumas, Patrice and Corfee-Morlot, Jan and Herweijer, Celine and Wood, Robert Muir},
  title   = {Assessing climate change impacts, sea level rise and storm surge risk in port cities: a case study on {Copenhagen}},
  journal = {Climatic Change},
  year    = {2011},
  volume  = {104},
  number  = {1},
  pages   = {113--137},
  doi     = {10.1007/s10584-010-9978-3}
}

@article{jongman2014floodfinance,
  author  = {Jongman, Brenden and Hochrainer-Stigler, Stefan and Feyen, Luc and Aerts, Jeroen C. J. H. and Mechler, Reinhard and Botzen, W. J. Wouter and Bouwer, Laurens M. and Pflug, Georg and Rojas, Rodrigo and Ward, Philip J.},
  title   = {Increasing stress on disaster-risk finance due to large floods},
  journal = {Nature Climate Change},
  year    = {2014},
  volume  = {4},
  number  = {4},
  pages   = {264--268},
  doi     = {10.1038/nclimate2124}
}

@article{reissl2022lockdowns,
  author  = {Reissl, Severin and Caiani, Alessandro and Lamperti, Francesco and Guerini, Mattia and Vanni, Fabio and Fagiolo, Giorgio and Ferraresi, Tommaso and Ghezzi, Leonardo and Napoletano, Mauro and Roventini, Andrea},
  title   = {Assessing the economic impact of lockdowns in {Italy}: a computational input--output approach},
  journal = {Industrial and Corporate Change},
  year    = {2022},
  volume  = {31},
  number  = {2},
  pages   = {358--409},
  doi     = {10.1093/icc/dtac003}
}

@techreport{conte2020rhomolo,
  author      = {Conte, Andrea and Lecca, Patrizio and Sakkas, Stylianos and Salotti, Simone},
  title       = {The territorial economic impact of {COVID-19} in the {EU}: a {RHOMOLO} analysis},
  institution = {European Commission, Joint Research Centre},
  type        = {JRC Policy Insight},
  number      = {JRC121261},
  year        = {2020},
  url         = {https://publications.jrc.ec.europa.eu/repository/handle/JRC121261}
}

@techreport{sakkas2021rhomolo,
  author      = {Sakkas, Stylianos and Crucitti, Francesca and Conte, Andrea and Salotti, Simone},
  title       = {The 2020 territorial impact of {COVID-19} in the {EU}: a {RHOMOLO} update},
  institution = {European Commission, Joint Research Centre},
  type        = {JRC Policy Insight},
  number      = {JRC125536},
  year        = {2021},
  url         = {https://publications.jrc.ec.europa.eu/repository/handle/JRC125536}
}

@article{bachmann2024whatif,
  author  = {Bachmann, R{\"u}diger and Baqaee, David and Bayer, Christian and Kuhn, Moritz and L{\"o}schel, Andreas and Moll, Benjamin and Peichl, Andreas and Pittel, Karen and Schularick, Moritz},
  title   = {What if? {The} macroeconomic and distributional effects for {Germany} of a stop of energy imports from {Russia}},
  journal = {Economica},
  year    = {2024},
  volume  = {91},
  number  = {364},
  pages   = {1157--1200},
  doi     = {10.1111/ecca.12546}
}

@article{pichler2024gas,
  author  = {Pichler, Anton and Hurt, Jan and Reisch, Tobias and Stangl, Johannes and Thurner, Stefan},
  title   = {Economic impacts of a drastic gas supply shock and short-term mitigation strategies},
  journal = {Journal of Economic Behavior \& Organization},
  year    = {2024},
  volume  = {227},
  pages   = {106750},
  doi     = {10.1016/j.jebo.2024.106750}
}

@techreport{dibella2022gas,
  author      = {Di Bella, Gabriel and Flanagan, Mark J. and Foda, Karim and others},
  title       = {Natural gas in {Europe}: the potential impact of disruptions to supply},
  institution = {International Monetary Fund},
  type        = {IMF Working Paper},
  number      = {WP/22/145},
  year        = {2022},
  doi         = {10.5089/9798400215292.001}
}

@techreport{lan2022gas,
  author      = {Lan, Ting and Sher, Galen and Zhou, Jing},
  title       = {The economic impacts on {Germany} of a potential {Russian} gas shutoff},
  institution = {International Monetary Fund},
  type        = {IMF Working Paper},
  number      = {WP/22/144},
  year        = {2022},
  doi         = {10.5089/9798400215285.001}
}

@techreport{fahr2024ecb,
  author      = {Fahr, Stephan and Senner, Richard and Vismara, Andrea},
  title       = {The globalization of climate change: amplification of climate-related physical risks through input-output linkages},
  institution = {European Central Bank},
  type        = {ECB Working Paper},
  number      = {2942},
  year        = {2024},
  url         = {https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2942~6734242a0b.en.pdf},
  note        = {Verified on the RePEc listing; no DOI exposed}
}

@techreport{andersson2026ecb,
  author      = {Andersson, Malin and Battistini, Niccol{\`o} and Bobasu, Alina},
  title       = {Heatwaves, coldwaves, floods, and droughts: the short-term impact of extreme weather events on economic activity},
  institution = {European Central Bank},
  type        = {ECB Working Paper},
  number      = {3203},
  year        = {2026},
  url         = {https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3203~063779fe18.en.pdf},
  note        = {Verified on the RePEc listing; no DOI exposed}
}

@article{bachner2024multimodel,
  author  = {Bachner, Gabriel and Knittel, Nina and Poledna, Sebastian and Hochrainer-Stigler, Stefan and Reiter, Karina and Pflug, Georg},
  title   = {Revealing indirect risks in complex socioeconomic systems: a highly detailed multi-model analysis of flood events in {Austria}},
  journal = {Risk Analysis},
  year    = {2024},
  volume  = {44},
  number  = {1},
  pages   = {229--243},
  doi     = {10.1111/risa.14144}
}

@misc{poledna2018systemic,
  author       = {Poledna, Sebastian and Hochrainer-Stigler, Stefan and Miess, Michael Gregor and Klimek, Peter and Schmelzer, Stefan and Sorger, Johannes and Shchekinova, Elena and Rovenskaya, Elena and Linnerooth-Bayer, JoAnne and Dieckmann, Ulf and Thurner, Stefan},
  title        = {When does a disaster become a systemic event? {Estimating} indirect economic losses from natural disasters},
  year         = {2018},
  howpublished = {arXiv:1801.09740 [econ.GN]},
  doi          = {10.48550/arXiv.1801.09740},
  note         = {Preprint; no journal version found}
}

@article{poledna2023forecasting,
  author  = {Poledna, Sebastian and Miess, Michael Gregor and Hommes, Cars and Rabitsch, Katrin},
  title   = {Economic forecasting with an agent-based model},
  journal = {European Economic Review},
  year    = {2023},
  volume  = {151},
  pages   = {104306},
  doi     = {10.1016/j.euroecorev.2022.104306}
}

@article{reiter2022barriers,
  author  = {Reiter, Karina and Knittel, Nina and Bachner, Gabriel and Hochrainer-Stigler, Stefan},
  title   = {Barriers and ways forward to climate risk management against indirect effects of natural disasters: a case study on flood risk in {Austria}},
  journal = {Climate Risk Management},
  year    = {2022},
  volume  = {36},
  pages   = {100431},
  doi     = {10.1016/j.crm.2022.100431}
}

@article{hochrainerstigler2024indirect,
  author  = {Hochrainer-Stigler, Stefan and others},
  title   = {Risk management against indirect risks from disasters: a multi-model and participatory governance framework applied to flood risk in {Austria}},
  journal = {International Journal of Disaster Risk Reduction},
  year    = {2024},
  volume  = {106},
  pages   = {104425},
  doi     = {10.1016/j.ijdrr.2024.104425}
}
```

Author lists: given in full where read from the record or page; "and others" where Crossref returned only the
first names (Dunne 2026, Mongelli 2023, Di Bella 2022, Hochrainer-Stigler 2024). The Ciscar 2011 author list
beyond the first three is from the authors' standard citation and should be checked against the PDF before use.
