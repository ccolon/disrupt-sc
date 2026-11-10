r"""SI revision of 10 Nov 2026, section S1 (the author's notes N01-N14 and the direct edits E01-E15).

N01 N02 N04  references for the data sources of the Agents and Network paragraphs
N03          where a household agent sits (an interior point of the NUTS2 region, not a population centroid)
N05          rates table: short caption, the general remarks as notes under the table
N06 N08 N10  every number of the evidence column carries its source
N07          the liquid-bulk rail and road values are calibrated on the German split alone (said in the cell)
N09 N11      evidence for the sea rate and for the value of time (dossier si_evidence_sea_vot_rail_20261110.md)
N12 N13      inventory table without the 'lean' column, acronyms as notes, input-specific targets in their own table
N14          criticality table: the note column becomes lettered notes under the table
The tables si_stocks, si_stock_overrides and si_criticality were first regenerated in their new shape
(si_tables.py --only stocks,criticality into emptied blocks); this script then edits their text.

    python patch_si_20261110_s1.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")

# ------------------------------------------------------------------ paragraphs
d.line(r"\paragraph{Agents.}", r"\paragraph{Agents.} Firm agents are the disaggregation of each region--sector's output into its plant and employment locations, by the \texttt{firm-extractor} package of the model. Sectors use different source data for this spatial downscaling. For crops (A01), the SPAM 2020 crop-production grid \citep{spam2020} is aggregated to NUTS3 regions, and each region's production is placed at the production-weighted centroid of its grid cells. Ten sectors use facility data. Nine keep their facilities as points: coal mines (B05) from the Global Energy Monitor (GEM) coal-mine tracker \citep{gem2025} with Climate TRACE \citep{climatetrace2024}, oil and gas fields (B06) from the GEM oil and gas extraction tracker, metal-ore mines (B07) from Climate TRACE and the FINEPRINT mine database \citep{fineprint2022}, refineries (C19), chemical plants (C20), pulp and paper mills (C17--18) and aluminum smelters (C24B) from Climate TRACE's 2022 facility activity, cement plants (C23) from the GEM cement tracker and steel mills (C24A) from the GEM steel tracker. Power plants (D), from the GEM power trackers, are aggregated to NUTS2 capacity. The 39 other sectors are downscaled using NUTS3 employment in the Eurostat regional accounts \citep{eurostat2025regio}. Facility statuses are those of 2022, the reference year of the input--output table. This gives \NFirms{} firm agents once the disconnected ones are removed, nine per region--sector on average. Households are one agent per NUTS2 region (251), which carries the region's population \citep{eurostat2025regio}. It sits at a point inside the region's boundary, near its geometric center; this point is neither a population-weighted centroid nor the region's largest city. Every agent attaches to the nearest road node of the network.")
d.sub(r"extracted from the TENtec services of the European Commission on 29 August 2026\todo{add ref})",
      r"extracted from the TENtec services of the European Commission on 29 August 2026 \citep{tentec2026})")
d.sub(r"from the raw-material inventories of the Bundesbank corporate balance-sheet statistics (raw materials, consumables and supplies over material costs)",
      r"from the raw-material inventories of the Bundesbank corporate balance-sheet statistics \citep{bundesbank2025} (raw materials, consumables and supplies over material costs)")
d.sub(r"(coal at power plants 30 days, crude at refineries 90, cement inputs 25; Table~\ref{tab:stocks})",
      r"(coal at power plants 30 days, crude at refineries 90, cement inputs 25; Tables~\ref{tab:stocks} and~\ref{tab:stockoverrides})")
d.sub(r"The critical-input weights are the survey of Pichler et al. (2022)~\citet{pichler2022} mapped to the 50 sectors",
      r"The critical-input weights are the survey of Pichler et al.~\citep{pichler2022} mapped to the 50 sectors")
d.sub(r"which is based on the classification of Rauch (1999).~\citep{rauch1999}: crops",
      r"following the classification of Rauch~\citep{rauch1999}: crops")

# ------------------------------------------------------------------ rates table (text; the value column is checked by si_tables.py)
TEN = "AT, BG, CZ, ES, FR, HU, IT, PL, SI, SK"
d.block("si_rates", r"""\begingroup\footnotesize\setlength{\tabcolsep}{4pt}
\begin{longtable}{L{27mm}L{30mm}L{91mm}}
\caption{\textbf{Transport cost parameters:} the baseline values and the evidence behind them. Most of the evidence comes from the operator costs compiled for the Netherlands Institute for Transport Policy Analysis (KiM)~\citep{kim2023}, from quoted and published freight rates of the Rhine trades, and from the Eurostat modal split~\citep{eurostat2023modal}, on which the road and rail values are calibrated (Section~S2). Notes follow the table.}
\label{tab:rates} \\
\toprule
mode, cargo class & value & evidence \\
\midrule
\endfirsthead
\toprule
mode, cargo class & value & evidence \\
\midrule
\endhead
\multicolumn{3}{l}{\emph{Line haul, USD per tonne-kilometer}} \\
road, containers and dry bulk & 0.050 & A full-load long-haul rate; no rate series was collected. For comparison, the operator cost of a tractor--semitrailer at fleet average, empty legs included, was 0.115 EUR per tonne-kilometer in 2018~\citep{kim2023}. Calibrated on the modal split by country~\citep{eurostat2023modal}. \\
road, liquid bulk & 0.130 & No rate evidence was collected. Set together with the rail value so that the German split of liquid bulk by mode matches the statistics (Section~S2). \\
rail, containers and dry bulk & 0.032 (0.038 in 10 countries: """ + TEN + r""") & Between the operator costs of a dry-bulk charter train (0.014 EUR per tonne-kilometer) and of a container shuttle (0.045) in the Netherlands in 2021~\citep{kim2023}; the average freight revenue of European railway undertakings was 0.036 EUR per tonne-kilometer in 2019 and 0.047 in 2024~\citep{irgrail2026mm14}. Calibrated on the modal split by country~\citep{eurostat2023modal}; 20\,\% higher in the ten countries named, where the model otherwise carries too much by rail (Section~S2). \\
rail, liquid bulk & 0.085 (0.100 in 10 countries: """ + TEN + r""") & Set with the road value on the German split of liquid bulk alone (Section~S2). It is an effective cost, not a tariff: the operator cost of a liquid-bulk charter train is 0.018 EUR per tonne-kilometer~\citep{kim2023}. \\
inland waterway, dry bulk & 0.010 on the Rhine, 0.010--0.040 on the other waterways & Push-convoy cost 0.008--0.012 EUR per tonne-kilometer (ores 0.009, coal 0.008; 2021 prices)~\citep{kim2023}; the published coal rate Rotterdam--Basel of 2015, 10.5 EUR per tonne (0.013 per tonne-kilometer)~\citep{infras2017}. Single motor vessels cost 0.018 (CEMT class Va) to 0.036 (Kempenaar)~\citep{kim2023}, so grain-type flows in single vessels are under-priced in the model. The same values hold on eight other waterways (Amsterdam--Rhine canal, Ghent--Terneuzen canal, IJssel, IJsselmeer, Noordzeekanaal, Nord-Ostsee-Kanal, Scheldt, Scheldt--Rhine link); on the other waterways they are up to four times higher (Section~S2). \\
inland waterway, liquid bulk & 0.038 on the Rhine, 0.038--0.152 on the other waterways & Tanker spot rates: ARA--Karlsruhe 27--29 EUR per tonne in June--July 2025 (0.042--0.045 per tonne-kilometer) and ARA--Cologne 15--17 (0.047--0.053)~\citep{opis2025riverlake}; ARA--Karlsruhe about 20 in June 2022 (0.031)~\citep{handelsblatt2022rhine}; ARA--Basel 42 in November 2023 (0.051)~\citep{ccnr2024price}; operator cost 0.029~\citep{kim2023}. \\
inland waterway, containers & 0.022 on the Rhine, 0.022--0.088 on the other waterways & Operator cost 0.025~\citep{kim2023}; Rotterdam--Basel 162--178 EUR per TEU upstream in 2015~\citep{infras2017}; Middle Rhine tariffs of 125--140 EUR per TEU~\citep{konings2009}, that is 12--18 EUR per tonne all-in at 10 tonnes per TEU. In the model \KaubContMt~Mt of containers a year pass Kaub, against about 10 in the counts (Section~S2). \\
sea & 0.0015 & Operator cost of container carriers on deep-sea itineraries, 0.0014 EUR per tonne-kilometer in 2021~\citep{kim2023}. Bulk carriers cost 0.0034 and tankers 0.0051 in the same source, so the sea leg of bulk is under-priced two- to threefold. Sea lanes carry no capacity limit in this study; the rate bears on the port at which imports land (Section~S2). \\
\midrule
\multicolumn{3}{l}{\emph{Value of time, USD per tonne-hour}} \\
containers & 1.00 (road and rail); 0.32 (waterways); 0.15 (sea) & A cargo-side value, the shipper's cost of an hour in transit. A meta-analysis of freight studies gives, for shippers in Germany and all commodities, 1.59 on road, 0.27 on rail, 0.19 at sea and 0.09 on inland waterways (2017 prices)~\citep{binsuwadan2022vfts}: the road and sea values are in line with it, the rail and waterway values three to four times higher. The waterway value is calibrated on the container tonnage of the Rhine (Section~S2). For comparison, the vessel-side cost of time on inland waterways is 0.02--0.07 EUR per tonne-hour at full load and 0.13--0.26 at fleet average~\citep{kim2023}, and 0.20 in a study for the European Commission~\citep{ecorys2005}. \\
dry and liquid bulk & 0.08 (all modes) & No value by commodity was found. The same meta-analysis gives 0.09 for shippers on inland waterways, all commodities~\citep{binsuwadan2022vfts}, and the cargo component is about a fifth of the value of time of a freight movement~\citep{dejong2014freightvot}. At 0.08 a day in transit costs 1.9 USD per tonne: time hardly weighs on the routing of bulk, which follows the freight cost. \\
\midrule
\multicolumn{3}{l}{\emph{Terminal transfer, hours of dwell time / USD per tonne}} \\
road--rail & containers 3 h / 2; dry bulk 4 h / 3; liquid bulk 1 h / 1 & Intermodal terminals and bulk sidings at both ends of a rail trip; tank cars are loaded at the shipper's siding. \\
road-- or rail--waterway & containers 4 h / 4; dry bulk 20 h / 5; liquid bulk 8 h / 3.5 & The fixed per-voyage element of the rates: tankers 3--7 EUR per tonne across lanes (fitted to the spot quotes above), two container lifts 70--80 EUR per TEU~\citep{konings2009} (7--8 EUR per tonne at 10 tonnes per TEU); the liquid-bulk terminal is set at 8 h and 3.5 USD in the calibration of the German liquid-bulk split. \\
waterway--sea & 8 h / 2 & Port handling. \\
road-- or rail--sea & 24 h / 7 & Port handling. \\
seaport fee, by port & containers 0.29--8.43, other cargo 0.1--2.81 USD per tonne at 140 ports & On top of the transfer above: a fee that falls with the port's tonnage (the fee ladder of Section~S2), so that small ports do not draw the cargo of the large ones. \\
\midrule
\multicolumn{3}{l}{\emph{Speed, kilometers per hour}} \\
road / rail / inland waterway / sea & 60 / 45 / 12 / 35 & Motorway line haul; freight trains; Rhine barges (about 10 upstream, 15 downstream); short sea. \\
\bottomrule
\multicolumn{3}{L{150mm}}{\emph{Notes.} USD and EUR are treated as equal. Operator costs are fleet averages that include empty legs and waiting, at the price level of 2021~\citep{kim2023}; rates are spot quotes and published tariffs. No public source gives a full rate table by vessel class at normal water (the CCNR publishes indices), so the waterway values rest on operator costs and on the quoted lanes. ARA: Amsterdam--Rotterdam--Antwerp. TEU: twenty-foot equivalent unit. CEMT Va and Kempenaar: classes of motor vessels.} \\
\end{longtable}
\endgroup
""")

# ------------------------------------------------------------------ inventory table: notes, internal pointers
d.sub(r"""T & Households as employers & 7 & D & Assumed. \\
\bottomrule
""", r"""T & Households as employers & 7 & D & Assumed. \\
\bottomrule
\multicolumn{5}{L{150mm}}{\emph{Notes.} d: days. Grade A: balance-sheet data for the industry itself; B: data for a group of industries, or physical stock data; C: indirect evidence; D: assumed. RHB: raw materials, consumables and supplies over material costs, times 365, from the extrapolated corporate balance sheets of the Bundesbank~\citep{bundesbank2025}, for 2023, with the 2019 value in brackets. Ratio series: the Bundesbank ratio statistics by division (non-finished stock over material costs, which includes work in progress, WIP). FIBEN: the sector sheets of the Banque de France~\citep{banquefrance2025fiben} (median stocks over turnover). Census: the M3 survey of the US Census Bureau~\citep{census2026m3} (materials-and-supplies inventories over the cost of materials). EKBG: the German reserve-plant act of 2022~\citep{ekbg2022}.} \\
""")
d.sub(r"Bulk liquid feedstocks at river sites are shorter (see 6.3).", r"Bulk liquid feedstocks at river sites are shorter (Table~\ref{tab:stockoverrides}).")
d.sub(r"is not an intermediate input under the ICIO margin treatment - see 6.4.", r"is not an intermediate input, since the input--output table records trade as a margin.")
d.sub(r"Sector value 20 = blend; use the input overrides.", r"The sector value of 20 is a blend; the targets by input are in Table~\ref{tab:stockoverrides}.")
d.sub(r"49 d of Materialaufwand incl. growing crops/livestock (WIP)", r"49 d of material costs incl. growing crops and livestock (WIP)")
d.sub(r"Bundesbank G RHB 2.2 d of Materialaufwand (45: 1.4, 46: 2.7, 47: 1.4)", r"Bundesbank G RHB 2.2 d of material costs (divisions 45: 1.4, 46: 2.7, 47: 1.4)")

# ------------------------------------------------------------------ input-specific targets: wording of the cells
d.sub(r"The model has no grid substitution between plants, so a 2-day buffer turned any plant cut into an economy-wide cascade (run of 4 September 2026); kept at the coping duration of the services, a stated limitation of the transport representation.",
      r"The model has no grid substitution between plants, so a 2-day buffer would turn any plant cut into an economy-wide cascade; the input is kept at the coping duration of the services, a limitation of the model.")
d.sub(r"Reserve plants must hold 30 days of coal (Energy Industry Act, section 50b, inserted by the reserve-plant act of 2022); Steag 2022",
      r"Reserve plants must hold 30 days of coal (Energy Industry Act, section 50b, inserted by the reserve-plant act of 2022~\citep{ekbg2022}); Steag 2022")
d.sub(r"Pipeline-fed: the pipelined-flows rule delivers B06 outside the network, and the 90 days stand for the storage of the gas system, not for a plant stock.",
      r"Pipeline-fed: gas is delivered outside the transport network, and the 90 days stand for the storage of the gas system, not for a plant stock.")
d.sub(r"refineries (C19) & crude oil (and crude import bundles) (B06) &", r"refineries (C19) & crude oil (B06) &")
d.sub(r"are the stockholding obligation of Directive 2009/119/EC (90 days of net imports) carried by the pipeline system; crude never stops a refinery in the runs, and the refinery pathway of the German loss is refined products.",
      r"are the stockholding obligation of Directive 2009/119/EC~\citep{council2009oilstocks} (90 days of net imports) carried by the pipeline system; crude never stops a refinery in the runs, and refineries enter the German loss through their refined products.")
d.sub(r"the timing of the force-majeure warnings of July 2026 (ICIS) against the balance-sheet average",
      r"the timing of the force-majeure warnings of July 2026~\citep{icis2026} against the balance-sheet average")
d.sub(r"Non-storable inputs (types service, services, trade, transport, construction): the buyer copes for 90 days without an inventory, the model's coping duration.",
      r"Non-storable inputs (services, trade, transport and construction): the buyer copes for 90 days without an inventory, the model's coping duration.")

# ------------------------------------------------------------------ criticality table: the author's caption, notes under the table
d.sub(r"\caption{\textbf{The criticality survey mapped to the 50 sectors.} Each sector of the input--output table is matched to one industry of the survey of Pichler et al.~\citep{pichler2022}; the letters refer to the notes under the table, which give the judgment where the match is not one to one.}",
      r"\caption{\textbf{The criticality survey mapped to the 50 sectors.} Each sector of the input--output table (OECD ICIO, 2025 edition) is matched to one industry of the survey of Pichler et al.~\citep{pichler2022}, whose industries are the 55 of the World Input--Output Database (NACE Rev.~2); the letters refer to the notes under the table, which give the judgment where the match is not one-to-one. The counts are, for the sector as a buyer, how many of its 50 input sectors the survey rates ``critical'' (output limited by the input), ``important'' (a depleted input halves output) and non-critical (``other''), and, for the sector as an input, how many buyers rate it critical (``critical for''). In the model, an input below 2\,\% of the buyer's input costs is considered non-critical. Over the 2,500 sector-to-sector pairs, 18\,\% of the inputs are critical, 9\,\% important and 73\,\% non-critical.}")
d.sub(r"$^{b}$~Paper, the larger of the two and the one with physical inputs.", r"$^{b}$~Paper is the larger of the two and the one with physical inputs.")
d.save()
