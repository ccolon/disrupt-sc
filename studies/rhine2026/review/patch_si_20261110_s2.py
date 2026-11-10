r"""SI revision of 10 Nov 2026, section S2 (the author's notes N15-N24 and the direct edits E16-E23).

N15      references for the calibration statistics (Eurostat modal split and ports, Destatis)
N16      Amsterdam's fee stated (0.75 USD per tonne for all cargo, against 0.28 and 0.09 from the formula)
N17      the sentence on what the fee ladder stands for, rewritten in plain words (kept: it is the reason for the fee)
N18 N20  the modal split as a table (si_modal), with the three German cargo classes under Germany
N19      road is below the statistics in five countries, not in all: said, with the general cause
N21      first sentence of 'The gaps' rewritten on what S2 shows (tonnage at Kaub, its composition, the modal split)
N22      the Upper Rhine residual also overstates the exposure of the Rhine-Neckar region: said
N23 N24  seaport table: the 30 largest, then the ports outside the forty with 50 Mt or more
Stage 1 edits the text, empties the block of si_ports and opens the block of si_modal; then
    python studies/rhine2026/si_tables.py --tag r6_bycargo --lists 20261102 --only ports,modal
fills the two blocks; stage 2 sets their captions.

    python patch_si_20261110_s2.py 1|2 [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

stage = sys.argv[1]
ov = Path(sys.argv[2]) if len(sys.argv) > 2 else OVERLEAF
d = Doc(ov / "si.tex")
MARK = "(edit the caption, headers and text cells here; studies/rhine2026/si_tables.py only checks and refreshes the numbers)"

if stage == "1":
    # ---------------------------------------------------------------- the calibration and its four families of parameters
    d.line("The baseline reproduces the input--output accounts by construction.",
           r"The baseline reproduces the input--output accounts by construction. Its transport flows were calibrated against four kinds of statistic: the inland modal split by country in tonne-kilometers (Eurostat 2023~\citep{eurostat2023modal}), the modal split by cargo class in Germany and the Netherlands (Eurostat's road, rail and inland waterway statistics by commodity group, same year), the tonnage along the Rhine (the CCNR cross-section counts at Emmerich and Iffezheim and its estimates between them \citep{ccnr2023}), and the gross weight of goods handled by the forty largest seaports (Eurostat 2023~\citep{eurostat2022ports}) together with the tonnage carried on the German waterway sections (Destatis 2023~\citep{destatis46321}). To match those targets, we adjusted four families of logistic parameters, on top of the base values of Table~\ref{tab:rates}.")
    d.line(r"    \item The baseline waterway rate applies to the Rhine",
           r"    \item \emph{Waterway rates.} The base rate (0.010 USD per tonne-kilometer for dry bulk, 0.038 for liquid bulk, 0.022 for containers) applies to the Rhine and to eight waterways connected to it or to the North Sea ports: the Amsterdam--Rhine canal, the IJssel, the IJsselmeer, the Noordzeekanaal, the Scheldt, the Scheldt--Rhine link, the Ghent--Terneuzen canal and the Kiel canal. The other waterways pay a multiple of it: the Albert canal and the Meuse 1.2, the Main, Moselle, Neckar, Saar, Danube, Seine, Rh\^one, Sa\^one and the Ruhr canals 1.3, the Lek 1.5, the Mittellandkanal, the Elbe lateral canal, the Main--Danube canal, the K\"ustenkanal and the Berlin waterways 2, the Weser 2.2, the Elbe, the Oder and the Vltava 3, the Po system 4, and every waterway not named 1.5.")
    d.line(r"    \item The rail rate is 20\,\% higher in France",
           r"    \item \emph{Rail rates.} The rail rate is 20\,\% higher in France, Italy, Austria, Spain, Poland, Czechia, Hungary, Slovakia, Slovenia and Bulgaria, where a single European rate puts more freight on rail than the statistics show.")
    d.line(r"    \item The loading fee at a seaport follows a ladder",
           r"    \item \emph{Seaport fees.} The loading fee at a seaport falls with the port's observed throughput $T$: it is $3\log_{10}(100\,\mathrm{Mt}/T)$ USD per tonne for containers, kept between 0 and 12, and a third of it for other cargo. Amsterdam is the one exception: its fee is 0.75 USD per tonne for all cargo, where the formula gives 0.28 for containers and 0.09 for other cargo, a value that sets the division of the North Sea traffic between Amsterdam and Rotterdam. The fee stands for the feeder leg of a container landed at a small port. Deep-sea lines call at a few large ports, whereas the sea network of the model serves every coastal port at the same rate, so that without the fee imports land at the port nearest their buyer.")
    d.line(r"    \item The value of time of a container on the waterway is 0.32",
           r"    \item \emph{Value of time of containers on waterways.} It is set at 0.32 USD per tonne-hour. \textit{Ceteris paribus}, at 0.35 no container is put on barges on the Rotterdam--Ruhr corridor, and at 0.30 barge containers overshoot the observed tonnage by three times; 0.32 gives the observed order of magnitude at Kaub.")
    d.sub("No other parameters were adjusted to fit the logistic data.",
          r"No other parameter was adjusted in this calibration. The base road and rail rates, the terminal transfers and the other values of time of Table~\ref{tab:rates} had been set before it, on the same kinds of statistic.")

    # ---------------------------------------------------------------- the fit: the modal split as a table
    d.line(r"\paragraph{The fit.} Figures~S2 and S3 and Table~\ref{tab:ports}.",
           r"\paragraph{The fit.} Table~\ref{tab:modal} and Fig.~S2 compare the inland modal split of the baseline with the statistics, Fig.~S3 the tonnage along the Rhine and Table~\ref{tab:ports} the seaports." + "\n\n"
           + "% >>> generated table si_modal " + MARK + "\n% <<< generated table si_modal")
    d.line("Road is under-represented by construction in Germany, the Netherlands, Belgium, France and Austria",
           r"Road is below the statistics in Germany, the Netherlands, Belgium, France and Austria, by 8 to 14 percentage points, and on them in Poland and Italy (Table~\ref{tab:modal}). One cause applies to every country: agents sit at NUTS2 and NUTS3 points, so the short-haul traffic within a region, most of it by road, does not exist in the model, and the shares of rail and waterway are overstated accordingly. Where the split is nevertheless on the statistics, the rail rate calibrated for the country compensates for it. By cargo class on the German territory, the bulk that the shock concerns travels on the right modes, with the waterway share of liquids nearly a third too high.")

    # ---------------------------------------------------------------- the gaps
    d.line(r"\paragraph{The gaps, and their impacts on the study.}",
           r"\paragraph{The gaps, and their impacts on the study.} What matters for the loss estimates is the tonnage that crosses Kaub, its composition by cargo class and the modes on which the countries along the river move their freight. On these the baseline is close to the statistics: Kaub carries \KaubMt~Mt a year against 50--60 in the counts, the river from Mannheim to the Dutch border is within \RhineDevMaxPct\,\% of them, and bulk travels on the modes it uses in reality (Table~\ref{tab:modal}). The port tonnages are not calibrated: \PortsWithinThirty{} of the forty largest European seaports are within 30\,\% of the Eurostat statistics (Table~\ref{tab:ports}), the largest gaps being crude oil, transshipment and imports landed at the coast nearest their buyer, flows that do not pass Kaub. The residuals fall into four kinds, three of which are off the Kaub path.")
    d.sub("The model does not incorporate crude oil, gas, and transshipments, leading to large gaps in tonnage in several ports:",
          "The model carries neither crude oil nor gas on its network and counts no transshipment, which leaves large gaps in tonnage at several ports:")
    d.sub(r"In the model, flows of traded goods on the Rhine at the Dutch border are \RhineEmmerichMt{} against 118, showing that the hinterland traffic of Rotterdam that matters for the Rhine basin is captured.",
          r"In the model, the traded goods on the Rhine at the Dutch border amount to \RhineEmmerichMt~Mt against 118, which shows that the hinterland traffic of Rotterdam that matters for the Rhine basin is captured.")
    d.line(r"\emph{The nearest-coast landing.}",
           r"\emph{The nearest-coast landing.} The modeling of sea routing is simple: one sea rate, one fee ladder for all ports, all-or-nothing routing on the cheapest path, and neither ship sizes nor port capacities. As a consequence, imports tend to land at the seaport nearest their buyer. The fee ladder returns part of this tonnage to the large ports but is not strong enough to correct the nearest-coast landing, which leaves large discrepancies, such as at Venice and its lagoon (Venice, Chioggia, Monfalcone and Porto Nogaro together \PortLagoonMt~Mt against 28), at Szczecin (\PortSzczecinMt{} against 12, with Gda\'nsk at \PortGdanskMt{} against 80 as the other side of the same coin), Burgas (\PortBurgasMt{} against 17), Oslo (\PortOsloMt{} against 5) and M\'alaga (\PortMalagaMt{} against 2). The \SecPortsN{} ports outside the forty largest carry \SecPortsMt~Mt against \SecPortsObsMt. These are Adriatic, Baltic, Atlantic and Mediterranean seaports whose hinterlands do not touch the Rhine basin, so they do not affect the model's estimates. The Rhine's own imports enter through Rotterdam, Antwerp, Amsterdam, Hamburg and Bremerhaven, where the model is within a third of the counts, except at Rotterdam, where the gap is explained above.")
    d.line(r"\emph{Absence of intra-regional traffic}",
           r"\emph{Absence of intra-regional traffic.} The Netherlands' inland transport is, in the model, a third of its observed tonne-kilometers (\NLTkmBn{} billion against 111) and its waterways half (\NLWaterTkmBn{} against 41.6). A main reason for this gap is that the model abstracts from short-haul traffic: agents are located at NUTS3 points and generate no traffic within their region. For the same reason the Lower Rhine from Duisburg to Nijmegen carries \LowerRhineGapMin{} to \LowerRhineGapMax\,\% less than observed, and the Dutch delta from Tiel to Rotterdam \DeltaGapMin{} to \DeltaGapMax\,\% less: the traffic between the ports of the delta is missing. The same applies to the canals of the Ruhr region.")
    d.line(r"\emph{The Upper Rhine and the rail shares.}",
           r"\emph{The Upper Rhine.} The tonnage at Kaub is close to the counts, but the Rhine's upstream traffic ends too early, in the Rhine--Neckar region. Above Mannheim, the model carries half to two-thirds of the counts (Basel \RhineBaselMt{} against 5.5, Strasbourg \RhineStrasbourgMt{} against 16, Karlsruhe \RhineKarlsruheMt{} against 22), while the Mannheim--Mainz reach is above them (\RhineMannheimMainzMt{} against 40). In the model, Switzerland and Alsace receive by rail what in reality comes up the river. The model therefore understates the exposure of these two regions to Kaub and overstates that of the Rhine--Neckar region, where this tonnage is unloaded instead.")
    d.block("si_ports", "")
elif stage == "2":
    d.sub(r"\caption{\textbf{The seaports of the calibrated baseline.} The 30 largest seaports by gross weight of goods handled (Eurostat 2023, Mt) and the model's tonnage through their connectors; below the line, the ports outside the 40 largest where the model routes 50~Mt",
          r"\caption{\textbf{The seaports of the calibrated baseline.} The 30 largest seaports by gross weight of goods handled (Eurostat 2023~\citep{eurostat2022ports}, Mt) and the model's tonnage through their connectors; below the line, the ports outside the 40 largest where the model routes 50~Mt")
    d.sub(r"in the baseline and in the statistics of 2023; for Germany also by cargo class.}",
          r"in the baseline and in the statistics of 2023 (Eurostat~\citep{eurostat2023modal}; by cargo class, Eurostat's road, rail and inland waterway statistics by commodity group); for Germany also by cargo class.}")
d.save()
