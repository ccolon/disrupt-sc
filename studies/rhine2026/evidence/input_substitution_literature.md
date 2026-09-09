# Substitution of an input across suppliers / regions: model rules and short-run elasticities

Compiled 9 September 2026 for the Rhine 2026 study (DisruptSC: firms with region-by-sector
inputs, Leontief production with survey-based criticality, per-input inventories, weekly steps).
Question: when one source of a product fails, how do propagation models let buyers draw the same
product from another supplier or region, and what does the empirical literature say about the
short-run elasticity of substitution across sourcing regions/suppliers?

Verification key (applies to every number and quote below):
- [V] read in the fetched full text (PDF converted with pdftotext) or replication code;
- [A] abstract / published-page text only, or a secondary source that reports the value;
- [U] not verified within the time budget (stated explicitly; do not cite as fact).
Journal corrections vs. the brief: Inoue & Todo "Firm-level propagation..." is Nature
Sustainability (the 2019 PLOS ONE paper is "Propagation of negative shocks across nation-wide
firm networks"); Diem et al. 2022 is Scientific Reports, not Science Advances; the Koks IO-vs-CGE
comparison is NHESS 2016 (Koks et al. 2019 is the ERL European-flood MRIA paper).

## A. Model rules

### A1. Inoue & Todo (2019 PLOS ONE; 2019 Nature Sustainability; 2020 PLOS ONE COVID)
(a) Rule [V, PLOS ONE 2019 and RIETI DP 18-E-013, identical wording]: "Because we assume that
firms in the same sector produce the same product, shortages of supplies from firm j in sector s
can be compensated for by supplies from firm k in the same sector ... In other words, we do not
assume changes in supply chain ties after the disaster. Thus, the total inventory of product s in
firm i on day t is" the sum over its existing sector-s suppliers (Eq. 5). So: pooling of the same
product across the firm's EXISTING same-sector suppliers, instantaneous (no delay parameter), no
probability, no new links; the only capacity condition is that substitute suppliers must actually
have output/inventory to deliver (proportional rationing otherwise). Inventory target: Poisson,
calibrated mean 9 days (search range 1-20 d), production stops 6 days after damage, recovery
ratio 0.025/day [V, RIETI DP]. COVID version [V]: "customers can procure input from their other
suppliers in the same industry already connected prior to the lockdown if these suppliers have
additional production capacity"; and "we assume that firms cannot find any new suppliers ...
[this] may be too strong, leading to an overestimation of the propagation effect"; inventories
"nine days of production on average".
Sensitivity [V/A]: PLOS ONE 2019: "the propagation of negative shocks is substantially faster
in the latter two cases wherein substitution is more difficult" (synthetic networks with fewer
same-sector alternatives); RIETI DP: with single-firm failures "more than 90% of firms show less
than 0.1 system damage ... the robustness comes from substitutes". Nature Sustainability Fig. 5
("different levels of substitution") exists but its numbers were not extracted [U].
(b) Inoue H., Todo Y. (2019) PLoS ONE 14(3): e0213648, doi:10.1371/journal.pone.0213648;
Inoue H., Todo Y. (2019) Nature Sustainability 2: 841-847, doi:10.1038/s41893-019-0351-x;
Inoue H., Todo Y. (2020) PLoS ONE 15(9): e0239251, doi:10.1371/journal.pone.0239251;
RIETI DP 18-E-013, https://www.rieti.go.jp/jp/publications/dp/18e013.pdf.
(c) Mapping: equivalent to keying inventories by PRODUCT (sector) and letting orders shift among
the firm's current suppliers of that product with zero delay, capped by their spare output.

### A2. Guan et al. (2020, Nature Human Behaviour) - ARIO-inventory on a 140-region MRIO
(a) Rule [V]: rationing "a firm allocates its output in proportion to its orders"; ordering to
restore inventory to "a given number of days, n_i^p, of intermediate consumption" (value of n not
found in the fetched text [U]); substitution across regions: "when a product comes from multiple
suppliers, the allocation of orders is adjusted according to the production capacity of each
supplier". SI [V]: "some inventories of firm i may come from different firms (in practice, in the
MRIO table for example, this refers to the same sector sourced from different regions). When one
type of inventory has multiple suppliers, firm i will consider the order proportion of the
equilibrium period and the current production capacity of each supplier when releases orders to
them (the second improvement of our disaster footprint model on the ARIO model)." Limits: only
suppliers already present in the MRIO trade matrix; reallocation bounded by suppliers' current
capacity; no new trade links; overproduction/inventory parameter values not extracted [U].
(b) Guan D., Wang D., Hallegatte S., et al. (2020) Nat. Hum. Behav. 4: 577-587,
doi:10.1038/s41562-020-0896-8.
(c) Mapping: pool the same sector across source regions in one inventory; split new orders by
baseline share x current capacity of each source; no search delay, existing links only.

### A3. Hallegatte ARIO (2008) and ARIO-inventory (2014)
(a) Rule: there is NO input-side substitution. Koks et al. 2016 [V]: "If less production is
available than required to satisfy all demand, the model will ration the demand. This process of
prioritization and rationing can be interpreted as a form of substitution, as stated in
Hallegatte (2008) ... the ARIO model only substitutes between outputs, whereas the other models
specifically substitute between inputs"; ARIO's "lack of substitution in production, trade, or
products" makes its Italian-flood losses "approximately 3 to 6 times higher" than the CGE. Otto
et al. 2017 [V]: "In the ARIO-inventory model redistribution of demand is not possible".
Adaptation = overproduction of the SAME suppliers plus inventories. Abstracts [A]: 2008 "the
overproduction capacity in the construction sector and the adaptation characteristic time are
the most important" parameters; 2014 "results are extremely sensitive to several uncertain model
parameters. In particular, accounting for heterogeneity within sectors has a large negative
influence on production bottlenecks, and thus increases total economic losses". Default values as
reported by Issa et al. 2025 (R-ARIO) [A]: alpha_max = 125 %, tau_alpha = 12 months, target
inventory n = 90 days (3 days for non-stockable goods), inventory restoration tau_s = 30 days,
heterogeneity psi = 0.8 (a bottleneck starts when an input's stock falls below psi x target;
lower psi = more within-sector substitutability); "the choice of inventory parameters ... can move
predicted changes in value added shortly after the disaster from moderate (< 20%) to economic
collapse (100%) (Hallegatte 2014)". Whether imports may expand beyond their baseline share when
local supply is short was not verifiable (WB and HAL copies blocked) [U].
(b) Hallegatte S. (2008) Risk Analysis 28(3): 779-799, doi:10.1111/j.1539-6924.2008.01046.x;
Hallegatte S. (2014) Risk Analysis 34(1): 152-167, doi:10.1111/risa.12090 (= WB WPS 6047);
Issa et al. (2025) "Refined adaptive regional input-output model", Natural Hazards Review,
https://www.jackwbaker.com/Publications/Issa_et_al_(2025)_R-ARIO,_NHR.pdf.
(c) Mapping: ARIO's "flexibility" is time-to-overproduce and inventory days, not re-sourcing; its
psi is the analogue of a criticality/heterogeneity damping inside one sector aggregate.

### A4. Koks & Thissen (2016, MRIA) and Koks et al. (2016 NHESS; 2019 ERL)
(a) Rule [V, NHESS 2016]: "Industries in the different regions face a short-run maximum
capacity. If the demand exceeds this maximum capacity, imports to this region increase in order
to satisfy demand"; "before imports from other regions increase, first other firms that can
produce comparable products (although less efficiently) and have slack capacity will take over
until they reach their maximum capacity"; "it is assumed that before a region reaches its maximum
regional capacity it will already start importing goods from other regions". ERL 2019 [V]:
"agents in the model attempt to find alternative possibilities to satisfy their demand based on
existing trade relations. More specifically, we do not simulate the creation of new trade
relations." The LP minimises cost with inefficiency (secondary-technology) losses booked
separately. Numeric value of the maximum-capacity/trade-flexibility parameter: not extracted
(ESR full text and ORA copy blocked) [U]. The CGE comparator (IEES) uses GTAP Armington
elasticities; "rigid" = intra-national trade with the same elasticity as international, "flexible"
= higher within-Italy substitution [V]; model spread "up to a factor of 7" [V].
(b) Koks E.E., Thissen M. (2016) Economic Systems Research 28(4): 429-449,
doi:10.1080/09535314.2016.1232701; Koks E.E. et al. (2016) NHESS 16: 1911-1924,
doi:10.5194/nhess-16-1911-2016; Koks E.E. et al. (2019) Environ. Res. Lett. 14: 084042,
doi:10.1088/1748-9326/ab3306.
(c) Mapping: cost-ranked re-sourcing over existing links with a hard capacity cap per
region-sector; instantaneous (annual/quarterly LP), so it is an upper bound for a weekly ABM.

### A5. Otto, Willner, Wenz, Frieler & Levermann (2017, JEDC) - Acclimate
(a) Rule [V]: "the supply network is static, i.e., demand can only be shifted between existing
connections and no new connections can be established"; "All commodity inputs are perfect
complements and therefore substitution is not possible among them - an assumption that is
supported by ... Boehm et al. (2015)". Within a commodity, a buyer chooses "the optimal
distribution of its demand requests among its suppliers by minimizing expected purchasing
costs" given suppliers' communicated expected output and offer prices (Eq. 6, A.4x), with a
quadratic transport penalty that keeps the baseline stable; suppliers ration by reservation price
and may extend production at rising marginal cost ("idle capacities"); "Shifting of demand is
most effective if non-affected suppliers have idle capacities". There is NO parameter called
"supply chain elasticity" in the paper [V]; the only elasticity is the consumers' price
elasticity. Table B.1 values read from the PDF (column alignment uncertain [A]): timestep 1 day,
consumption price elasticity -0.5, storage balance timescale 2 days, upper storage limit 3 x
baseline, production-extension factor 1.1.
(b) Otto C., Willner S.N., Wenz L., Frieler K., Levermann A. (2017) J. Econ. Dyn. Control 83:
232-269, doi:10.1016/j.jedc.2017.08.001; PDF https://pik-potsdam.de/~willner/files/otto-willner17.pdf
(c) Mapping: same as A1/A2 but price-driven: re-sourcing among existing same-commodity suppliers,
limited by their idle capacity and transport time; no cross-commodity substitution.

### A6. Pichler, Pangallo, del Rio-Chanona, Lafond & Farmer (2022, JEDC)
(a) Rule [V, replication code model_functions.R, producing_x(prod.f="leontief.adapted")]: single
country (UK), 55 WIOD industries; an input is indexed by INDUSTRY only, so the same industry from
different suppliers/regions is one pooled input by construction. Output cap per input k:
critical (IHS Markit rating 1): x <= S_k/A_k; important (0.5): x <= 0.5*S_k/A_k + 0.5*x_cap0;
non-critical (0): no constraint. Ratings from an IHS Markit analyst survey (CC BY 4.0), Zenodo
10.5281/zenodo.5881855 (local copy: C:\Users\Celian\OneDrive\DisruptSC\covid19inputoutput).
(b) Pichler A., Pangallo M., del Rio-Chanona R.M., Lafond F., Farmer J.D. (2022) J. Econ. Dyn.
Control 144: 104527, doi:10.1016/j.jedc.2022.104527.
(c) Mapping: already the DisruptSC criticality mechanism; note it implicitly assumes full pooling
across sources of one industry, i.e. regional origin never binds.

### A7. Diem, Borsos, Reisch, Kertesz & Thurner (2022, Scientific Reports) and follow-ups
(a) Rule [V]: generalized Leontief, Eq. (1): x_i = min[ min_{k in I_es} Pi_ik/alpha_ik ,
beta_i + gamma_i * sum_{k in I_ne} Pi_ik/alpha_ik ] - essential inputs bind Leontief-wise,
non-essential inputs enter linearly (beta_i = output possible without them). Essential set: for
NACE 01-45 producers, inputs from NACE 01-45; NACE 46-99 producers have no essential inputs.
"we assume that intermediate inputs can not be substituted in the short-term by simply buying
more of a different input"; systemic-risk index = share of output lost "if firm i fails and its
output and demand is not replaced by other firms"; "the assumption of replacing a failing
supplier by another that can deliver a comparable input, has a strong impact on how shocks are
spreading" (Appendix E, replaceability index: low-market-share suppliers easier to replace).
Follow-up [A]: Zelbi, Ialongo & Thurner (2025, arXiv:2504.12955) - rewiring supplier links within
firm-level production constraints cuts systemic risk by 16-50 % without reducing output.
(b) Diem C., Borsos A., Reisch T., Kertesz J., Thurner S. (2022) Sci. Rep. 12: 7719,
doi:10.1038/s41598-022-11522-z; arXiv:2104.07260.
(c) Mapping: their essential/non-essential split is the criticality switch; their headline
numbers assume NO supplier replacement, which they flag as the dominant uncertainty.

### A8. Colon, Hallegatte & Rozenberg (2021, Nature Sustainability) - DisruptSC v1
(a) Rule [V, Supplementary Information]: Leontief ("strict complementarity between inputs");
network built by "having each firm selecting other firms as suppliers ... Each firm selects one
supplier" per input sector (weighted random choice, size and distance) and one country per
imported input; orders are split across suppliers by the fixed input-output shares; inventories
are fixed durations per (input, buying sector), 88 pairs from a World Bank firm survey; rationing
gives priority to households then proportional. Disruption response = rerouting ("If the route is
impassable, then it looks for an alternative route", at higher cost, passed into prices) or
blocked shipment. No supplier-switching or re-sourcing mechanism is described anywhere in the SI:
supplier substitution does not exist in that model version.
(b) Colon C., Hallegatte S., Rozenberg J. (2021) Nature Sustainability 4: 209-215,
doi:10.1038/s41893-020-00649-4.
(c) Mapping: the current code keeps that lineage (fixed supplier set per region-sector input);
docs/user-guide/parameters.md `substitution_share` is a transport-route ceiling, not re-sourcing.

### A9. Nested CES: Baqaee & Farhi (2019) and Bachmann et al. (2022)
(a) Baqaee & Farhi [V, NBER w23145 text]: three nests - consumption across industries (sigma),
value added vs intermediate bundle (theta), across intermediate inputs (epsilon); "benchmark
calibration, we set (sigma, theta, epsilon) = (0.9, 0.5, 0.001)" (Atalay 2017; Boehm et al.
"close to zero"), alternatives (0.7, 0.3, 0.001), (0.9, 0.6, 0.2), Cobb-Douglas (0.99, 0.99,
0.99); no regional/variety nest (US single-country IO); "we assume that intermediate inputs can
be freely reallocated across producers even in the short run". Bachmann et al. [V]: gas treated
as a separate input; "we will assume a low elasticity of substitution of 0.1 in these sectors.
This is substantially lower than the observed elasticities in the literature" (households 0.2-0.4
short run, Auffhammer & Rubin 2018; UK manufacturing heat "up to 0.5", Steinbuks 2012; chemical
feedstock gas, 11 % of industrial use, "can likely not be substituted at all"); Labandeira et al.
2017 short-run own-price elasticities: energy -0.22, natural gas -0.18, heating oil -0.02.
Results: Baqaee-Farhi model 0.2-0.3 % of GNE for an 8 % energy cut; 30 % gas cut with 0.1 ->
2.2-2.3 % GNE, rounded to 3 %; pure Leontief (zero) judged "inconsistent with empirical evidence".
(b) Baqaee D.R., Farhi E. (2019) Econometrica 87(4): 1155-1203, doi:10.3982/ECTA15202;
Bachmann R., Baqaee D., Bayer C., Kuhn M., Loeschel A., Moll B., Peichl A., Pittel K.,
Schularick M. (2022) ECONtribute Policy Brief 028,
https://www.econtribute.de/RePEc/ajk/ajkpbs/ECONtribute_PB_028_2022.pdf
(c) Mapping: across-product substitution is set near zero (epsilon ~ 0.001-0.2) - consistent
with Leontief-with-criticality; substitution across SOURCES of one product is outside these nests.

## B. Empirical short-run elasticities

### B10. Boehm, Flaaen & Pandalai-Nayar (2019, REStat) - Tohoku, Japanese affiliates in the US
(a) [V] "For Japanese multinationals, the elasticity of substitution across material inputs is
0.2 and the elasticity between material inputs and a capital/labor aggregate is 0.03" (materials
= Japanese vs non-Japanese incl. domestic); non-Japanese firms using Japanese inputs: 0.42-0.62
across materials, ~0.03 vs capital/labor; output "falls roughly one-for-one with declines in
imports"; imports bottom at t = 3 (June 2011) and "do not return back to the pre-shock trend
until month t = 7 (October 2011)"; "uninformative about the elasticity of substitution in the
long run".
(b) Boehm C.E., Flaaen A., Pandalai-Nayar N. (2019) Rev. Econ. Stat. 101(1): 60-75,
doi:10.1162/rest_a_00750.
(c) Mapping: over a 4-7 month horizon, firm-specific imported parts were not replaced by other
sources: sigma_source ~ 0.2 for differentiated manufacturing inputs.

### B11. Barrot & Sauvagnat (2016, QJE) - input specificity
(a) [V, Jan-2015 WP version]: customers of a disaster-hit supplier see "an average drop of 2
percentage points in sales growth" over the following four quarters; hit suppliers -3.6 to -5.4
pp for three quarters. Specificity = (i) differentiated goods (Rauch 1999 / Giannetti et al.
2011), (ii) R&D/sales above median, (iii) patents issued; "Each of these measures is strongly
correlated with the empirical duration of supplier-customer relationships, suggesting that they
capture variations in the cost for customers to switch suppliers". "The effect of non-specific
suppliers is insignificant, whereas the effect of specific suppliers is greater than the
baseline estimates" (Table 9: specific -0.013 (s.e. 0.004) vs non-specific +0.001 (0.003));
stock returns fall only for specific suppliers (-1.3 to -2.6 %).
(b) Barrot J.-N., Sauvagnat J. (2016) Q. J. Econ. 131(3): 1543-1592, doi:10.1093/qje/qjw018.
(c) Mapping: non-specific (commodity-like, Rauch homogeneous/reference-priced) inputs show no
measurable propagation within 4 quarters -> treat as fully re-sourceable; specific inputs not.

### B12. Bonadio, Huo, Levchenko & Pandalai-Nayar (2021, JIE)
(a) [V, NBER w27224 text, Table 1]: final demand across broad groups rho = 0.2; within a group,
Armington across origin-country x sector varieties = 1 (Huo et al. 2020 estimate 1-2.75, "Since
ours is a very short-run application, we take the lower value"); intermediate inputs: one CES over
inputs from every (country, sector), elasticity epsilon = 0.5 (Boehm et al. 2019) - the SAME
value governs substitution across source countries and across sectors; occupations 1; Frisch 2.
"Our baseline calibration to elasticities below 1 is meant to reflect that we are capturing the
very short-run effects ... the elasticity is below 1 in the short run, but above 1 in the long
run" (Boehm, Levchenko & Pandalai-Nayar 2020).
(b) Bonadio B., Huo Z., Levchenko A.A., Pandalai-Nayar N. (2021) J. Int. Econ. 133: 103534,
doi:10.1016/j.jinteco.2021.103534.
(c) Mapping: a weeks-to-months horizon justifies sigma_source <= 1 for inputs in aggregate models;
they do not separate commodity from differentiated inputs.

### B13. Feenstra, Luck, Obstfeld & Russ (2018, REStat)
(a) [V, 2014 WP text]: 109 (98) disaggregate US goods, 1992-2007; micro elasticity (among import
sources), medians: OLS 1.06, TSLS 3.24, 2-step GMM 4.12, LIML 1.54, CUE 1.98; macro elasticity
(home vs imports) median OLS 0.89 (bias toward 1 noted; system-GMM macro medians not extracted
[U]). Published abstract [A]: "for between two-thirds and three-quarters of sample goods, there is
no significant difference between the macro- and microelasticities, but for the rest, the
microelasticity is significantly higher". These are annual (long-run) elasticities.
(b) Feenstra R.C., Luck P., Obstfeld M., Russ K.N. (2018) Rev. Econ. Stat. 100(1): 135-150,
doi:10.1162/REST_a_00696; NBER w20063.
(c) Mapping: even the long-run micro elasticity is only ~2-4 for most goods; a weekly model should
sit well below that unless the good is a fungible commodity with spot markets.

### B14. Carvalho, Nirei, Saito & Tahbaz-Salehi (2021, QJE) - Tohoku, Japanese firm network
(a) [V]: firms with a disaster-hit supplier: sales growth -3.6 pp; with a hit customer: -2.9 pp;
second tier -2.7 pp (downstream) and -2.1 pp (upstream); aggregate -0.47 pp of GDP growth.
Structural estimates (Table 3): "firm-level intermediate inputs are gross substitutes with an
elasticity of substitution = 1.183 (s.e. = 0.034), while primary and intermediate inputs are
gross complements with an elasticity of substitution = 0.593 (s.e. = 0.062)" (annual horizon;
they note the elasticity "is tied to the time horizon" and to aggregation). No estimate of
supplier replacement after the quake in the text (new-link evidence cited only from Bernard et
al. 2019 on the Shinkansen).
(b) Carvalho V.M., Nirei M., Saito Y.U., Tahbaz-Salehi A. (2021) Q. J. Econ. 136(2): 1255-1321,
doi:10.1093/qje/qjaa044.
(c) Mapping: across-input elasticity ~1.2 at ANNUAL horizon and firm level - an upper bound for
weekly cross-supplier pooling of differentiated inputs.

### B15. Commodity-like inputs under logistics limits: Rhine 2018 (and 2022)
(a) Ademmer, Jannsen & Meuchelboeck [V, Kiel WP 2155 text]: low water = Kaub gauge < 78 cm; one
low-water day cuts inland-waterway volume by 0.9 %, "A full month (30 days) of low water ...
about 25 percent"; a 1 % fall in IWT volume lowers industrial production by 0.034-0.036 %; 30
low-water days -> IP "declines by about 1 percent"; peak Nov 2018: IP 1.5 % below counterfactual,
"a decline in GDP of close to 0.4 percent"; modal shift: rail "+0.07 percent" per low-water day,
road "very small"; "we find no evidence for a considerable increase in road and rail
transportation"; IWT carries ~30 % of coal/crude/gas and ~20 % of coke and petroleum products.
EIA 2018 [V]: Rotterdam-Basel distillate barge rate "from about $5 per barrel in July to more than
$35/b in late October"; Duisburg truck-rack distillate premium over ARA from $0.15/gal to
>$0.20/gal; ARA distillate stocks rose 15.7 -> 21.0 mb (product piled up below the bottleneck);
"leaving relatively more expensive transport options such as rail and long-distance trucking as
the only alternatives". Germany released strategic gasoline/diesel/jet stocks on 26 Oct 2018
(fourth time in 40 years; Frankfurt airport, Cologne, Hesse, BW, RP) [A, AFP/phys.org]. Local
dossier (evidence_rhine_literature.md): DB Cargo 900 wagons ~ 200 barges; 60 trucks per 1,500 t
barge. 2022 diesel episode: not researched within budget [U].
(b) Ademmer M., Jannsen N., Meuchelboeck S. (2023) German Economic Review 24(2): 121-144,
doi:10.1515/ger-2022-0077 (Kiel WP 2155, 2020); EIA Today in Energy, 2018,
https://www.eia.gov/todayinenergy/detail.php?id=37414;
https://phys.org/news/2018-10-drought-hit-rhine-germany-oil-reserves.html
(c) Mapping: for fuels/bulk the product IS substitutable across sources, but re-sourcing is
capped by rail/road slot capacity (a few % of barge volume within weeks) and shows up as price.

## Synthesis (what the literature supports)

1. (i) Pooling the same product across regions/suppliers: every firm-level ABM that has it (Inoue
   & Todo, Guan et al., Acclimate) pools ONLY across the buyer's existing suppliers of the same
   sector, with no delay and no search; none creates new links (Koks: "we do not simulate the
   creation of new trade relations"; Otto: "no new connections can be established").
2. Models without any re-sourcing (ARIO 2008/2014, Colon et al. 2021, Diem et al. 2022) are
   flagged by their own authors and by comparisons (Koks 2016: ARIO 3-6x a CGE) as upper bounds.
3. Pichler-type criticality (used in DisruptSC) already assumes full pooling within an industry;
   region-keyed inputs with Leontief binding are stricter than any model reviewed here.
4. (ii) Delays and capacity limits: the binding constraint in all ABMs is the alternative
   supplier's spare capacity (Guan: orders weighted by current capacity; Otto: idle capacity and
   production extension ~10 % at rising cost; Koks: hard regional capacity cap), not a delay.
5. Empirically the re-sourcing horizon for differentiated inputs is months: Tohoku imports needed
   ~7 months to return to trend (Boehm) and customer losses last 3-4 quarters (Barrot, Carvalho).
6. For commodities, re-sourcing is fast but logistics-limited: Rhine 2018 rail absorbed only
   ~0.07 %/day versus a 0.9 %/day barge loss, so the shortfall cleared through price and stocks.
7. A weekly ABM should therefore (a) pool across existing sources with no delay, (b) cap each
   source at spare capacity, and (c) cap total re-routed tonnage by mode capacity (the existing
   `substitution_share` ceiling) - three separate limits, not one elasticity.
8. (iii) Elasticity values, differentiated/specific inputs (machinery, parts, chemicals with
   specs): sigma across sources ~0.2 (Boehm; Bonadio 0.5 at most); Barrot: propagation only via
   specific suppliers. Treat as Leontief with pooling limited to the current supplier set.
9. Commodity-like inputs (fuels, grain, cement, basic chemicals; Rauch homogeneous): Barrot finds
   no measurable propagation; Feenstra micro elasticities 2-4 (annual). Treat as fully poolable
   across regions, with the logistics cap and price effect carrying the loss.
10. Across-PRODUCT substitution stays near zero at all horizons used by these models (Baqaee-Farhi
    epsilon = 0.001-0.2; Bachmann gas 0.1; Carvalho 1.18 only at annual horizon).
11. Sensitivity claims that are verified: Inoue-Todo "propagation substantially faster" when
    same-sector alternatives are scarce; Diem: replaceability "has a strong impact"; Hallegatte:
    inventory/heterogeneity parameters move losses from <20 % to collapse.
12. Numbers NOT verified here (do not cite): Guan's inventory days, MRIA's capacity-cap value,
    ARIO import expansion rule, Acclimate table alignment, Nature Sustainability Fig. 5 values.
13. Nearest template for DisruptSC: Guan et al. (ARIO-inventory on MRIO) - identical data
    structure (sector x region inputs) with capacity-weighted reallocation among existing sources.
14. Recommended parameterisation for the Rhine run: commodity inputs pooled across regions with a
    mode-capacity cap; differentiated inputs pooled only within the existing supplier set.
15. Open empirical gap: no study gives a weekly-horizon cross-source elasticity for bulk goods;
    the Rhine 2018 modal-shift coefficients (rail +0.07 %/day) are the closest available proxy.
