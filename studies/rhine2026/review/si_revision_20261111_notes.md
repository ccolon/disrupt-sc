# The author's revision of si.tex (675722a against fc30932)

Notes: 12; new file 780 lines, old 781 lines.

## Inline notes
### N01 [S1] line 37
NOTE: add evidence
BEFORE: ...road--rail & containers 3 h / 2; dry bulk 4 h / 3; liquid bulk 1 h / 1 & Intermodal terminals and bulk sidings at both ends of a rail trip
AFTER: . \\...

### N02 [S1] line 39
NOTE: add evidence
BEFORE: ...waterway--sea & 8 h / 2 & Port handling
AFTER: . \\...

### N03 [S1] line 46
NOTE: can be easily criticized, it would not cost much to add a conversation factor, e.g., 2022 average?
BEFORE: ...\multicolumn{3}{L{150mm}}{\emph{Notes.} USD and EUR are treated as equal
AFTER: . Operator costs are fleet averages that include empty legs and waiting, at 2021 price levels~\citep{kim2023}; rates are spot quotes and published tariffs. No p...

### N04 [S1] line 46
NOTE: add table note with superscript for this acronym
BEFORE: ...lticolumn{3}{L{150mm}}{\emph{Notes.} USD and EUR are treated as equal. Operator costs are fleet averages that include empty legs and waiting, at 2021 price levels~\citep{kim2023}; rates are spot quotes and published tariffs. No public source gives a full rate table by vessel class at normal water; the CCNR publishes indices. ARA
AFTER: : Amsterdam--Rotterdam--Antwerp. TEU: twenty-foot equivalent unit. CEMT Va and Kempenaar: classes of motor vessels.} \\...

### N05 [S1] line 46
NOTE: same: add note
BEFORE: ...e fleet averages that include empty legs and waiting, at 2021 price levels~\citep{kim2023}; rates are spot quotes and published tariffs. No public source gives a full rate table by vessel class at normal water; the CCNR publishes indices. ARA: Amsterdam--Rotterdam--Antwerp. TEU: twenty-foot equivalent unit. CEMT Va and Kempenaar
AFTER: : classes of motor vessels.} \\...

### N06 [S1] line 56
NOTE: add here the main source: Bundesbank, complemented by Banque de France and US Census Bureau
BEFORE: ...\caption{\textbf{Inventory targets by buying industry.} Days of consumption of purchased goods inputs that each industry holds at the baseline, with evidence from 
AFTER:  with the grade of the evidence (author's judgment). Input-specific targets are given in in Table~\ref{tab:stockoverrides}.}...

### N07 [S1] line 59
NOTE: add superscript to explain the grade levels
BEFORE: ...industry & & days & grade
AFTER:  & evidence \\...

### N08 [S1] line 66
NOTE: what is WIP? how you go from 49 to 30? add superscript table note at first use of the acronyms, also for some concepts such as "ratio series"
BEFORE: ...A01 & Crop and animal production & 30 & C & German ratio series A: non-finished stock 49 d of material costs incl. growing crops and livestock (WIP)
AFTER: ; feed/fertilizer stocks sit on farms (BLE). Partly assumed. \\...

### N09 [S2] line 218
NOTE: define somewhere CCNR in the main text and in the SI
BEFORE: ...ere calibrated against four kinds of statistic: the inland modal split by country in tonne-kilometers (Eurostat 2023~\citep{eurostat2023modal}), the modal split by cargo class in Germany and the Netherlands (Eurostat's road, rail and inland waterway statistics by commodity group, same year), the tonnage along the Rhine (the CCNR
AFTER:  cross-section counts at Emmerich and Iffezheim and its estimates between them \citep{ccnr2023}), and the gross weight of goods handled by the forty largest sea...

### N10 [S7] line 579
NOTE: this is not really about sensitivity here, it is just how the lever study was made
BEFORE: ...vity} shows the same losses by type of uncertainty. Three sets of runs are of another kind. Ten further supplier--buyer networks, drawn with other seeds, sample the random component of the model (the rows on the supplier--buyer network). The levers of the main text are each run on every network, against the base of that network 
AFTER: . And two experiments cross two changes (Section~S5): the levers under a rail ceiling, and the two waves at a shorter refill time . In all, the paper rests on \...

### N11 [S7] line 579
NOTE: are those runs really needed to show?
BEFORE: ...drawn with other seeds, sample the random component of the model (the rows on the supplier--buyer network). The levers of the main text are each run on every network, against the base of that network . And two experiments cross two changes (Section~S5): the levers under a rail ceiling, and the two waves at a shorter refill time 
AFTER: . In all, the paper rests on \NRuns{} runs. The list of these runs with their main outputs is in the code repository....

### N12 [S8] line 688
NOTE: remove this table, too much details
BEFORE: ...\caption{\textbf{
AFTER: The bounded substitution by rail, week by week.} For each run week of the four rail runs (Supplementary Table~\ref{tab:revision}): the cut bulk that found an el...

## Text edits (notes stripped), by line
### E01 [S1] old 5-5 -> new 5-5 (replace)
line 5: \paragraph{Agents.} Firm agents are [-the-]{+built from a+} disaggregation of each region--sector's output into [-its -]{++}plant and employment [-locations, by the \texttt{firm-extractor} package of the model.-]{+locations.+} Sectors use different source data for this spatial downscaling. For c [...] st city. Every agent attaches to the nearest road node of the network.

### E02 [S1] old 7-7 -> new 7-7 (replace)
line 7: \paragraph{Network.} The trans-European transport network (TEN-T, extracted from the TENtec services of the European Commission[- on 29 August 2026-]{++} \citep{tentec2026}) with \NEdges{} edges and \NNodes{} nodes: roads ( [...]  crude oil and natural gas travel by pipeline, not explicitly modeled.

### E03 [S1] old 33-34 -> new 33-34 (replace)
line 33: containers & 1.00 (road and rail); 0.32 (waterways); 0.15 (sea) &[- A cargo-side value, the shipper's cost of an hour in transit.-]{++} A meta-analysis of freight studies gives, for shippers in Germany and [...] and 0.20 in a study for the European Commission~\citep{ecorys2005}. \\
line 34: dry and liquid bulk & 0.08 (all modes) & No value by commodity was fou [...] the value of time of a freight movement~\citep{dejong2014freightvot}. [-At 0.08 a day in transit costs 1.9 USD per tonne: time hardly weighs on the routing of bulk, which follows the freight cost. -]{++}\\

### E04 [S1] old 37-37 -> new 37-37 (replace)
line 37: road--rail & containers 3 h / 2; dry bulk 4 h / 3; liquid bulk 1 h / 1 & Intermodal terminals and bulk sidings at both ends of a rail [-trip; tank cars are loaded at the shipper's siding.-]{+trip.+} \\

### E05 [S1] old 41-41 -> new 41-41 (replace)
line 41: seaport fee, by port & containers 0.29--8.43, other cargo 0.1--2.81 US [...] orts & On top of the transfer above: a fee that falls with the port's [-tonnage-]{+tonnage;+} [-(the-]{+see the+} fee ladder [-of-]{+in+} [-Section~S2), so that small ports do not draw the cargo of the large ones.-]{+Section~S2.+} \\

### E06 [S1] old 46-46 -> new 46-46 (replace)
line 46: \multicolumn{3}{L{150mm}}{\emph{Notes.} USD and EUR are treated as equal. Operator costs are fleet averages that include empty legs and waiting, at [-the-]{+2021+} price [-level of 2021~\citep{kim2023};-]{+levels~\citep{kim2023};+} rates are spot quotes and published tariffs. No public source gives a full rate table by vessel class at normal [-water-]{+water;+} [-(the-]{+the+} CCNR publishes [-indices), so the waterway values rest on operator costs and on the quoted lanes.-]{+indices.+} ARA: Amsterdam--Rotterdam--Antwerp. TEU: twenty-foot equivalent unit. CEMT Va and Kempenaar: classes of motor vessels.} \\

### E07 [S1] old 56-56 -> new 56-56 (replace)
line 56: \caption{\textbf{Inventory targets by buying industry.} Days of consumption of purchased goods inputs that each industry holds at the baseline, with [--]{+evidence from  with +}the grade of the evidence [-and-]{+(author's+} [-the-]{+judgment).+} [-evidence. The notes follow the table; the-]{+Input-specific+} targets [-set-]{+are+} [-for-]{+given+} [-one input of an industry are-]{+in+} in Table~\ref{tab:stockoverrides}.}

### E08 [S2] old 217-217 -> new 217-217 (replace)
line 217: [--]{+\paragraph{Calibration procedure}+}

### E09 [S2] old 227-227 -> new 227-227 (replace)
line 227: [-\paragraph{The-]{+\paragraph{Fit+} [-fit.}-]{+evaluation.}+} Table~\ref{tab:modal} and Fig.~S2 compare the inland modal split of t [...] S3 the tonnage along the Rhine and Table~\ref{tab:ports} the seaports.

### E10 [S2] old 264-264 -> new 264-264 (replace)
line 264: [-\paragraph{The gaps,-]{+\paragraph{Gaps+} and their [-impacts on the study.}-]{+impacts.}+} What matters for the loss estimates is the tonnage that crosses Kaub, its [-composition by cargo class-]{+composition,+} and the modes on which the countries along the river move their freig [...] er from Mannheim to the Dutch border is within \RhineDevMaxPct\,\% of [-them,-]{+them (Fig.~S3),+} and bulk travels on the modes it uses in reality (Table~\ref{tab:moda [...] ed at the coast nearest their buyer, flows that do not pass Kaub. The [-residuals-]{+next+} [-fall-]{+paragraphs+} [-into-]{+detail the+} four [-kinds,-]{+main+} [-three-]{+gaps+} [-of-]{+and+} [-which-]{+their+} [-are-]{+impacts+} [-off-]{+on+} the [-Kaub path.-]{+results.+}

### E11 [S2] old 266-266 -> new 266-266 (replace)
line 266: \emph{Crude, gas and transshipment.} The model carries neither crude o [...] ortWilhelmshavenMt{} against 30, Zeeland \PortZeelandMt{} against 37. [-The gross weight-]{+Port+} statistics cover crude oil and its products, gas and coal, and sea-to [...] which they reach their buyer; therefore, no transshipment is counted. [-The-]{+This absence is particularly marked at+} transshipment [-hubs-]{+hubs,+} [-are-]{+such+} [-the same residual at its extreme:-]{+as+} Algeciras \PortAlgecirasMt{} against 79, Piraeus \PortPiraeusMt{} aga [...] and traffic of Rotterdam that matters for the Rhine basin is captured.

### E12 [S2] old 268-268 -> new 268-268 (replace)
line 268: \emph{The nearest-coast landing.} The modeling of sea routing is simple: one sea rate, one fee ladder for all ports, all-or-nothing routing on the cheapest [-path, and-]{+path;+} neither ship sizes nor port [-capacities.-]{+capacities are modeled.+} As a consequence, imports tend to land at the seaport nearest their [--]{+final +}buyer. The fee ladder [-returns-]{+redirects+} part of [-this-]{+those+} [-tonnage-]{+flows+} to[- the-]{++} large ports but is not strong enough to correct [-the-]{+this+} nearest-coast [-landing,-]{+effect,+} which leaves large discrepancies, such as at Venice and its lagoon (V [...]  Baltic, Atlantic and Mediterranean seaports whose hinterlands do not [-touch-]{+affect+} the Rhine basin, so they do [-not-]{+have+} [-affect-]{+no impact on+} the model's estimates. The Rhine's own imports enter through Rotterda [...]  of the counts, except at Rotterdam, where the gap is explained above.

### E13 [S2] old 270-270 -> new 270-270 (replace)
line 270: \emph{Absence of intra-regional traffic.} The Netherlands' inland tran [...] UTS3 points and generate no traffic within their region. For the same [-reason-]{+reason,+} the Lower Rhine from Duisburg to Nijmegen carries \LowerRhineGapMin{} [...] e delta is missing. The same applies to the canals of the Ruhr region.

### E14 [S2] old 272-272 -> new 272-272 (replace)
line 272: \emph{The Upper Rhine.} The tonnage at Kaub is close to the counts, bu [...] of these two regions to Kaub and overstates that of the Rhine--Neckar [-region, where this tonnage is unloaded instead.-]{+region.+}

### E15 [S3] old 343-343 -> new 343-343 (replace)
line 343: \paragraph{Gauges.} We built weekly means of the Kaub gauge from the P [...] ute of 28 September \citep{bfg2026} and an assumed recovery after it. [-Such-]{+To+} [-an-]{+account+} [-outlook can miss an episode: the one of 7 September had put the weeks of 14, 21 and 28 September at 12, 22 and 42\,cm; the observed means were 25, 7 and about $-2$ (the last from two observed days and the outlook of 28 September). Two stress profiles therefore take-]{+for+} the outlook's[--]{+ uncertainty, we build two additional profiles from its+} 25th and 75th [-percentile-]{+percentiles+} for the forecast weeks [-and shift the assumed recovery by the last forecast week's offset (\texttt{2026\_q25.csv}, \texttt{2026\_q75.csv}); they are marginal quantiles week by week, not trajectories of the ensemble, and are run -]{++}as [-two stress paths of the forecast, not as bounds-]{+sensitivities+} (Section~S7).[- The forecast was first issued on 30 September 2026 on an earlier loading curve, at \ForecastSepQ\,\% of a quarter, and reissued on 7 October 2026 on the loading curve of Table~\ref{tab:loading}. The batch of this paper, run on 2 November 2026, keeps the hydrological information of 30 September and uses the baseline calibrated as in Section~S2 and one capacity per cargo class (Capacities, below); it gives \DEUlossQ\,\%. No production statistic of the event entered any of these versions. By the outcome publication dates, July 2026 (production index released on 7 September) is retrospective; August (released on 7 October and not used) is a nowcast; September to December is prospective, the first release for September having come on 6 November 2026, after the last version. The manifest of these versions (profile files, loading curves, code commits, run lists, issue dates) is \texttt{studies/\allowbreak rhine2026/\allowbreak forecast\_manifest.md} in the code repository.-]{++}

### E16 [S3] old 345-347 -> new 345-345 (replace)
- \paragraph{Monthly loading shares.} Under the 2026 profile, the Kaub reach passes on average \KaubPassJun\,\% of its normal tonnage in June 2026, \KaubPassJul\,\% in July, \KaubPassAug\,\% in August, \KaubPassSep\,\% in September, \KaubPassOct\,\% in October and \KaubPassNov\,\% in November, with a minimum of \KaubMinWeek\,\% in the week of 28 September (below 5\,cm the loading curve is held at its lowest value, 8\,\%, an assumption); in 2018, \KaubPassJulyy\,\% in July, \KaubPassAugyy\,\% in August, \KaubPassSepyy\,\% in September, \KaubPassOctyy\,\% in October, \KaubPassNovyy\,\% in November and \KaubPassDecyy\,\% in December. If we compute the loading share day by day and average it over the week, rather than applying the table to the weekly mean gauge, the tonnage turned away changes by \DailyTurnedAwayyy\,\% in 2018 and \DailyTurnedAway\,\% over the observed weeks of 2026.
- 
- \paragraph{Loading table.} Table~\ref{tab:loading} describes how the loading curve is built. We gathered evidence from operators' surcharge tables and notices \citep{contargo2026}, the weekly tonnage count of the Dutch inland navigation association \citep{schuttevaer2026}, reports on the payloads of single vessels \citep{wiwo2026,ifw2026} and the literature on the low water of 2018 \citep{vandorsser2020,ademmer2023}, to link gauge values to the share of the normal tonnage that the Kaub reach can pass, the loading share. The model interpolates linearly between those values and stays at 0.08 below 5\,cm. The evidence measures different quantities: single-vessel payloads, a weekly count, operators' thresholds. The resulting loading share is the authors' reading of them.
+ \paragraph{Loading table.} Table~\ref{tab:loading} describes how the loading curve is built. We gathered evidence from operators' surcharge tables and notices \citep{contargo2026}, the weekly tonnage count of the Dutch inland navigation association \citep{schuttevaer2026}, reports on the payloads of single vessels \citep{wiwo2026,ifw2026} and the literature on the low water of 2018 \citep{vandorsser2020,ademmer2023}, to link gauge values to the share of the normal tonnage that the Kaub reach can pass, which we call the \textit{loading share}. The model interpolates linearly between those values and stays at 0.08 below 5\,cm. The set of evidence is heterogeneous; therefore, the loading shares chosen are one possible treatment of those data.

### E17 [S3] old 355-355 -> new 353-353 (replace)
line 353: cm & loading share & source & [--]{+what it +}measures & treatment \\

### E18 [S3] old 359-359 -> new 357-357 (replace)
line 357: cm & loading share & source & [--]{+what it +}measures & treatment \\

### E19 [S3] old 363-363 -> new 361-360 (delete)
- 10 & 0.18 & as the rows above and below & none at this gauge & interpolated between the 5 cm assumption and the count at about 12 cm \\

### E20 [S3] old 378-378 -> new 375-374 (delete)
- \paragraph{Capacities.} Every Rhine reach $r$ has a normal capacity for each cargo class $c$, since container vessels, dry-bulk vessels and tank barges are three fleets: $K_{r,c}=\max\!\big(s_{r,c}\,T_r,\;1.02\,F_{r,c}\big)$, where $F_{r,c}$ is the model's baseline flow of the class on the reach, $s_{r,c}=F_{r,c}/\sum_{c'}F_{r,c'}$ its share of the reach's traffic, and $T_r$ the tonnage of the reach in the CCNR cross-section counts \citep{ccnr202 [...] al, against 137,000 in the counts: 32,400 for the container vessels, 62,900 for the dry-bulk vessels and 80,600 for the tank barges. Each week, the capacity of the Kaub reach for a class is its normal capacity times the loading share. Headrooms of 10 and 25\,\% instead of 2 are tested in Section~S7.

### E21 [S3] old 380-380 -> new 376-376 (replace)
line 376: [-\paragraph{Rerouting-]{+\paragraph{Monthly+} [-around-]{+loading+} [-a-]{+shares.}+} [-saturated reach.} After every agent has delivered, each reach compares its load with its capacity. If-]{+Under+} the [-load-]{+2026+} [-exceeds the capacity, the shipments are cut in proportion, so that the reach is exactly full. A saturated reach is then excluded for the rest of the week, and each cut share looks for a route on the remaining network. The procedure is repeated until no reach is over its capacity; it does not depend on the order of the deliveries. A cut share that finds no acceptable route returns to its supplier's inventory. In the reference run, \GateResentMin{} to \GateResentMax\,\% of the tonnage cut at Kaub finds another route (Table~\ref{tab:gate}). Containers always find a rail or road alternative; only bulk is withheld (Table~\ref{tab:channels}). The loading share applies to-]{+profile,+} the Kaub reach [-alone:-]{+passes on average \KaubPassJun\,\% of its normal tonnage in June 2026, \KaubPassJul\,\% in July, \KaubPassAug\,\% in August, \KaubPassSep\,\% in September, \KaubPassOct\,\% in October and \KaubPassNov\,\% in November, with a minimum of \KaubMinWeek\,\% in+} the [-other-]{+week+} [-reaches-]{+of+} [-keep-]{+28+} [-their-]{+September+} [-normal-]{+(below+} [-capacity all year. During-]{+5\,cm+} the [-low-water-]{+loading curve is held at its lowest value, 8\,\%, an assumption); in 2018, \KaubPassJulyy\,\% in July, \KaubPassAugyy\,\% in August, \KaubPassSepyy\,\% in September, \KaubPassOctyy\,\% in October, \KaubPassNovyy\,\% in November and \KaubPassDecyy\,\% in December. If we compute the loading share day by day and average it over the week, rather than applying the table to the weekly mean gauge, the tonnage turned away changes by \DailyTurnedAwayyy\,\% in 2018 and \DailyTurnedAway\,\% over the observed+} weeks [-only Kaub saturates. In the recovery weeks the catch-up traffic, which is above the baseline, also exceeds the normal capacity -]{++}of [-several other reaches, which delays part of the backlog and of the refill of inventories.-]{+2026.+}

### E22 [S3] old 382-382 -> new 378-382 (replace)
- \paragraph{Surcharge.} The week's multiplier $1/\text{loading share}$, capped at 20, is applied on every reach from Koblenz upstream, and one third of its excess over 1 on the Lower Rhine reaches. This factor of one third is an assumption: operators set the low-water surcharge by gauge \citep{contargo2026}, and the Lower Rhine, with its own gauges, is less restricted than the reach through Kaub. It has a negligible effect on the results: runs with a factor of zero and of one gave the same loss.
+ \paragraph{Capacities.} Every Rhine reach $r$ has a normal capacity for each cargo class $c$, since container vessels, dry-bulk vessels and tank barges are three distinct fleets: $K_{r,c}=\max\!\big(s_{r,c}\,T_r,\;1.02\,F_{r,c}\big)$, where $F_{r,c}$ is the model's baseline flow of the class on the reach, $s_{r,c}=F_{r,c}/\sum_{c'}F_{r,c'}$ its share of the reach's traffic, and $T_r$ the tonnage of the reach in the CCNR cross-section counts \citep{ccnr2023}, with a 2\% headroom. At Kaub, this gives 175,900 t a day in total: 32,400 for container vessels, 62,900 for dry-bulk vessels, and 80,600 for tank barges. Each week, the capacity of the Kaub reach for a class is its normal capacity times the loading share from Table~\ref{tab:loading}. Headrooms of 10 and 25\,\% instead of 2 are tested in Section~S7.
+ 
+ \paragraph{Rerouting around a saturated reach.} After every agent has delivered, each reach compares its load with its capacity. If the load exceeds the capacity, the shipments are cut in proportion, so that the reach is exactly full. A saturated reach is then excluded for the rest of the week, and each cut share looks for a route on the remaining network. The procedure is repeated until no reach is over its capacity; it does not depend on the or [...]  the other reaches keep their normal capacity all year. During the low-water weeks only Kaub saturates. In the recovery weeks, the catch-up traffic, which is above the baseline, also exceeds the normal capacity of several other reaches, which delays part of the backlog and the refill of inventories.
+ 
+ \paragraph{Surcharge.} The week's multiplier $1/\text{loading share}$, capped at 20, is applied on every reach from Koblenz upstream, and one third of its excess over 1 on the Lower Rhine reaches. This one-third factor is an assumption: operators set the low-water surcharge by gauge \citep{contargo2026}, and the Lower Rhine, with its own gauges, is less restricted than the reach through Kaub. It has a negligible effect on the results: runs with a factor of zero and of one gave the same loss.

### E23 [S7] old 579-579 -> new 579-579 (replace)
line 579: [-\paragraph{Approach.} -]{++}A sensitivity run changes one rule or parameter of the reference run a [...] the main text are each run on every network, against the base of that [-network.-]{+network .+} And two experiments cross two changes (Section~S5): the levers under a rail ceiling, and the two waves at a shorter refill [-time.-]{+time . In all, the paper rests on \NRuns{} runs. The list of these runs with their main outputs is in the code repository.+}

### E24 [S7] old 637-637 -> new 637-637 (replace)
line 637: [-\paragraph{Reading the table.} -]{++}The rule on rail moves the loss most (Section~S8). A ceiling of 50 kt  [...] s and the service rules by up to a third (Fig.~\ref{fig:sensitivity}).

### E25 [S7] old 665-665 -> new 665-664 (delete)
- \paragraph{The runs.} In all, the paper rests on \NRuns{} runs: \NRunsMain{} in the main list (the two reference runs, their variants, and the ten further networks of the 2018 event), \NRunsPaired{} lever runs on the ten further networks of 2026, \NRunsRev{} one-at-a-time sensitivities, \NRunsLadder{} inventory levels, \NRunsCross{} crossed runs, \NRunsNoRail{} runs without rail substitution and \NRunsAlt{} runs of the floor representation. The list of these runs, with the German loss, its peak, the loss of the 28 economies and the consumption loss of each, is the file \texttt{additional\_data/\allowbreak runs\_20261102.csv} of the study folder in the code repository, with the job lists (\texttt{cluster/\allowbreak jobs\_20261102\_*.txt}, \texttt{jobs\_20261103\_altriver.txt}, \texttt{jobs\_20261106\_inv075.txt}).

Text edit hunks: 25