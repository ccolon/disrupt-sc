"""The author's 54 notes of 21 Oct and the seven decisions of 22 Oct applied to main.tex (Overleaf cd91c65 + 21fdac2).

Decisions: D2 headline numbers on the mean of the eleven supplier-buyer networks (decompositions on the reference network,
labelled); D4 the delay cost dropped from the main text; D5 the uncertainty figure moved to the SI; D6 the measured-economy
paragraph dropped for one sentence; D7 the August-2026 test moved to the 2026 section. Run with DRY=1 to list missing anchors.
"""
import os
import re
from pathlib import Path

O = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
DRY = os.environ.get("DRY") == "1"
MISSES = []
KEEP_NOTES = ("...", "DisruptSC v2", "container")   # the marker legend, code availability, my pending markers


def miss(what):
    MISSES.append(what)
    if not DRY:
        raise AssertionError(what)


def span(s, start, end):
    i = s.find(start)
    if i < 0:
        miss(f"start not found: {start[:90]!r}"); return None
    j = s.find(end, i + len(start))
    if j < 0:
        miss(f"end not found after {start[:40]!r}: {end[:60]!r}"); return None
    return i, j


def block(s, start, end, new):
    sp = span(s, start, end)
    return s if sp is None else s[:sp[0]] + new + s[sp[1]:]


def sub1(s, old, new):
    n = s.count(old)
    if n != 1:
        miss(f"{n} occurrences of {old[:100]!r}"); return s
    return s.replace(old, new)


def strip_notes(s, keep=KEEP_NOTES):
    out = []; i = 0; n = 0
    while True:
        k = s.find("\\todo{", i)
        if k < 0:
            out.append(s[i:]); break
        depth = 0; j = k + len("\\todo")
        while j < len(s):
            if s[j] == "{": depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0: break
            j += 1
        body = s[k + 6:j]
        if body.startswith(keep):
            out.append(s[i:j + 1]); i = j + 1; continue
        out.append(s[i:k].rstrip(" ")); n += 1
        i = j + 1
        prev = "".join(out)[-1:]; nxt = s[i:i + 1]
        if prev.isalnum() and nxt.isalnum():
            out.append(" ")
    return "".join(out), n


raw = (O / "main.tex").read_text(encoding="utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
m = raw.replace("\r\n", "\n")

# ------------------------------------------------------------------ abstract and introduction
m = sub1(m, r"""a loss of \finalbatch{\DEUlossQ}\,\% of a quarter of German value added, nearly three times the industrial loss alone""",
         r"""a loss of \finalbatch{\EnsMean}\,\% of a quarter of German value added (\finalbatch{\EnsMin}--\finalbatch{\EnsMax} across eleven versions of the supplier--buyer network), nearly three times the industrial loss alone""")
m = sub1(m, r"""Kaub stayed below the low-water mark\todo{what is this mark?} for four months""",
         r"""Kaub stayed below the 78\,cm low-water mark (the equivalent water level, below which the fairway depth is no longer guaranteed) for four months""")
m = sub1(m, r"""put the cost at about 1\,\% of German industrial production per month of low water, with a GDP effect of the order of 0.3--0.4\,\% \citep{ademmer2023,ademmer2019}\todo{per month or for the whole episode? ambiguous}.""",
         r"""put the cost at about 1\,\% of German industrial production for each month of low water, which left GDP about 0.3--0.4\,\% below its path at the trough of the episode \citep{ademmer2023,ademmer2019}.""")
m = sub1(m, r"""After the second-warmest summer on record with only 72\,\% of normal rainfall \citep{dwd2026}\todo{somehow 72pc of rainfall does not sound that terrible. I would consider dropping this figure}, Kaub""",
         r"""After the second-warmest summer on record \citep{dwd2026}, Kaub""")
m = sub1(m, r"""doubling inventories reduces the loss by almost three-quarters""", r"""doubling inventories reduces the loss by almost two thirds""")
m = sub1(m, r"""This explicit representation of the transport network \todo{""", r"""Representing the transport network explicitly is what makes these levers visible: the model \todo{""")
m = sub1(m, r"""adds to supply-chain models the traffic a reopened river must carry while inventories refill, the dependence of repeated episodes on that refill, and the spread of the loss far beyond the plants on the river.""",
         r"""shows where a shortage starts, how far it travels and which logistic lever curbs it.""")

# ------------------------------------------------------------------ Results: the model
m = sub1(m, r"""The baseline reproduces the national input--output accounts and approximates the shares of road, rail and waterway by country and cargo type, the entry ports of EU imports and the tonnage along the Rhine from Basel to Rotterdam, with residuals that we report (Supplementary Figs.~S1--S3): the Kaub stretch carries \KaubMt~Mt a year against 50--60 in the counts; the Lower Rhine, North of Cologne, carries a quarter less than observed, because the containers that in reality sail between Rotterdam and the Ruhr travel by rail in the model\todo{we could say: why not adjusting container cost to fix that?} and part of the Rotterdam--Ruhr bulk takes other paths\todo{such as what?}, a residual that does not touch Kaub.""",
         r"""The baseline reproduces the national input--output accounts and approximates the shares of road, rail and waterway by country and cargo type and the tonnage along the Rhine from Basel to Rotterdam, with residuals that we report (Supplementary Section~S2): the Kaub stretch carries \KaubMt~Mt a year against 50--60 in the counts, all of it bulk, whereas roughly 10~Mt a year of containers also pass Kaub in reality, about a sixth of its tonnage \citep{ccnr2023}. The model routes the Rhine's containers by rail, because its container costs put the barge behind the train on the Rotterdam--Ruhr run, which is why the Lower Rhine, north of Cologne, carries a quarter less than observed. Containers may switch to rail and road without limit in the model, so this residual bears on the surcharge they would pay and the river capacity they would take, not on the bulk shortage that drives the loss; a sensitivity pair with the containers on the river bounds it (Supplementary Section~S4)\todo{container runs pending}. The port tonnages are not calibrated and are reported with their errors in Supplementary Section~S2.""")
m = sub1(m, r"""A sensitivity analysis tests looser assumptions on bulk switching to rail (Supplementary Section~S4).""",
         r"""Sensitivity runs test the rule both ways, with no rail for any bulk and with a weekly ceiling for all of it (Supplementary Sections~S4 and S8).""")
m = sub1(m, r"""(b) What happens to a shipment in a low-water week: it pays the surcharge on its normal route or takes a cheaper one; if the reach is full, shipments are cut in proportion and look for a route around it; a container finds rail, bulk cargo has no alternative at volume and returns to the supplier; the buyer draws on its inventory, and loses output when a critical input runs out.}""",
         r"""(b) What happens to a shipment in a low-water week: it is delivered with the surcharge or, when the reach is full, its cut share looks for another route; containers may switch to rail or road, most bulk cargo cannot and waits at the supplier$^{*}$; the buyer draws on its inventory and loses output when a critical input runs out. $^{*}$Bulk whose normal route already carries a main leg by rail may go around the stretch by rail; sensitivity runs relax and tighten the rule (Supplementary Section~S4).}""")

# ------------------------------------------------------------------ Results: 2018
m = sub1(m, r"""We set every mechanism above to its evidence value""", r"""We set every mechanism above to the value that external evidence gives""")
m = sub1(m, r"""The published\todo{where published? published as such? give ref} GDP effect of \ExPostLow--\ExPostHigh\,\% is""",
         r"""The GDP effect of \ExPostLow--\ExPostHigh\,\% that the Kiel Institute reported \citep{ademmer2019,ademmer2023} is""")
m = sub1(m, r"""The model's German loss over the whole 2018 event is \DEUlossQyy\,\% of a quarter of national value added, of which \IndustryShareyy\,\% in industry: \IndQyy\,\% of a quarter, against \RecordQ\,\% (band \RecordQLow--\RecordQHigh) for the benchmark's industry channel.""",
         r"""The model's German loss over the whole 2018 event is \EnsMeanyy\,$\pm$\,\EnsSdyy\,\% of a quarter of national value added across the eleven supplier--buyer networks (\DEUlossQyy\,\% on the reference network, whose link-level export gives the decompositions below), of which \IndustryShareyy\,\% in industry: \IndQyy\,\% of a quarter, against \RecordQ\,\% (band \RecordQLow--\RecordQHigh) for the benchmark's industry channel; the peak falls between late October and the first week of December (Fig.~\ref{fig:validation}c).""")
m = block(m, r"""\caption{\textbf{The 2018 test.}""", r"""\label{fig:validation}""",
          r"""\caption{\textbf{The 2018 test.} (a) Monthly shortfall of German industrial production in 2018: the statistical benchmark with its one-standard-deviation band (green), the model as the mean of the eleven supplier--buyer networks with their range (grey), and the alternative representation of the river, surcharge and closures, at the same inventories (dashed). (b) The same shortfall summed from August to December, in percent-months, against the inventory multiplier, for both representations (the alternative on the earlier loading curve, Supplementary Section~S9): the benchmark with its band (line and shading), the eleven networks at the balance-sheet inventories (points), the loading curve with its shortfall raised and lowered by 15\,\% (green bar) and two suppliers per input (cross). (c) Weekly German value-added loss in 2018, all sectors: mean, interquartile range and range of the eleven networks, with the observed events: force majeure at thyssenkrupp (22 October), strategic fuel-reserve release (24--26 October), the deepest month of industrial production (November). (d) The spread across the eleven networks for each event, with mean and standard deviation.}
""")
m = sub1(m, r"""In our baseline representation of the logistic impact of the low-water episode, river capacity is continuously adjusted to the Kaub gauge through a loading curve \todo{where do this curve come from, were there some fitting on it?}, which also set the surcharge. With it, losses starts in August, like in the statistical benchmark. We tested an alternative "floor" representation, in which lower gauge only creates a surchage, until each vessel class stops sailing below its own water level (Supplementary Section~S9). With it, \todo{what does it mean "dearer"?}, losses only start in mid-October, two months after the benchmark, because a dearer week still moves the full tonnage.""",
         r"""In our baseline representation of the logistic impact of the low-water episode, river capacity is continuously adjusted to the Kaub gauge through a loading curve, which also sets the surcharge. The curve is built from vessel loading rules, single-vessel loads, operators' thresholds and one tonnage count, without fitting (Supplementary Table~\ref{tab:loading}). With it, losses start in August, as in the statistical benchmark. We tested an alternative ``floor'' representation, in which a lower gauge only creates a surcharge, until each vessel class stops sailing below its own water level (Supplementary Section~S9). With it, losses only start in mid-October, two months after the benchmark, because a more expensive week still moves the full tonnage.""")
m = sub1(m, r"""Across ten versions of the supplier--buyer network (Methods), November always exhibits the highest losses;""",
         r"""Across ten further versions of the supplier--buyer network (Methods), November is always the deepest month;""")
m = sub1(m, r"""This comparison is a consistency check rather than a tight fit; raising the loading curve shortfall by 15\,\% puts the model at the benchmark's central value (Fig.~\ref{fig:validation}b, Supplementary Section~S9)\todo{why not doing it? I am against overfitting, so if there are good, ideally external reasons behind the loading curve, keep it like that}. Overall, the 2018 loss is \EnsMeanyy\,$\pm$\,\EnsSdyy\,\% of a quarter across the eleven networks, with the peak between late October and the first week of December (Fig.~\ref{fig:validation}c).\todo{didn't we already comment the overall loss figure in the first paragraph of the esction?}""",
         r"""This comparison is a consistency check rather than a tight fit: the loading curve is kept as its sources give it, and its variants with the shortfall raised and lowered by 15\,\% bracket the benchmark's central value (Fig.~\ref{fig:validation}b, Supplementary Section~S9).""")
# D7: the August-2026 test moves to the 2026 section
sp = span(m, r"""The estimates from the August 2026 closure, which the comparison above did not use, provide a second test.""", r"""\subsection*{The 2026 event""")
if sp:
    m = m[:sp[0]] + m[sp[1]:]
august = r"""The estimates made during the August 2026 closure, which the selection on 2018 did not use, are a second test. The model's industrial loss over the five weeks of the August episode is \finalbatch{\AugWaveIndQ}\,\% of a quarter, about EUR~\finalbatch{\AugWaveEurBn}~billion, inside the EUR 1--2 billion (0.1--0.2 percentage points of third-quarter GDP) estimated in late July by the Kiel Institute, with other estimates made in August of 0.2--0.35 points \citep{ifw2026,dihk2026}; the model's total over those weeks, services included, is \finalbatch{\AugWaveQ}\,\%. The share of firms affected, as the business surveys report it, is only partly reproduced: 33\,\% of the surveyed Rhine-corridor firms reported production restrictions and 6\,\% a stop in the survey of 29 July--4 August \citep{dihk2026}; in the week that survey closed, \finalbatch{\CorridorFirmsBelowRhineAug}\,\% of the model's German firms within 50\,km of the Rhine produce below 99\,\% of their baseline and \finalbatch{\CorridorStopRhineAug}\,\% below half of it (\finalbatch{\CorridorFirmsBelowRhine} and \finalbatch{\CorridorStopRhine}\,\% at the autumn peak). The model is on the low side, which the survey's sample may explain in part.

"""

# ------------------------------------------------------------------ Results: 2026
m = sub1(m, r"""The 2026 event is made of two low-water episode. After the August 2026 record""", r"""The 2026 event is made of two low-water episodes (Fig.~\ref{fig:event}a). After the August 2026 record""")
m = sub1(m, r"""The low water costs Germany \finalbatch{\DEUlossBn}~billion USD of value added, \finalbatch{\DEUlossQ}\,\% of a quarter (the loss cumulated over the 43 weeks of the run divided by thirteen weeks of baseline value added: a size, not the growth of any quarter), of which \finalbatch{\IndQ}\,\% in industry, with a peak of \finalbatch{\DEUpeakWeek}\,\% of a week's value added in the week of 12 October. The loss builds from July, when the river still passes two to four fifths fifths of its normal tonnage""",
         r"""The low water costs Germany \finalbatch{\EnsMean}\,$\pm$\,\finalbatch{\EnsSd}\,\% of a quarter of value added across the eleven supplier--buyer networks (range \finalbatch{\EnsMin}--\finalbatch{\EnsMax}; about \finalbatch{\EnsMeanBn}~billion USD; the loss cumulated over the 43 weeks of the run divided by thirteen weeks of baseline value added: a size, not the growth of any quarter), with the peak in the week of 5 or 12 October in every version. The decompositions that follow are on the reference network, the only one with a link-level export, which loses \finalbatch{\DEUlossQ}\,\% (\finalbatch{\DEUlossBn}~billion USD), \finalbatch{\IndQ}\,\% of it in industry, with a peak of \finalbatch{\DEUpeakWeek}\,\% of a week's value added in the week of 12 October. The loss builds from July, when the river still passes two to four fifths of its normal tonnage""")
m = sub1(m, r"""because inventories were already lower because of the August episode.

""", r"""because inventories were already lower because of the August episode.

""" + august)
m = sub1(m, r"""\includegraphics[width=\textwidth]{figures/F4_shock_2026.pdf}\\[2mm]
\includegraphics[width=\textwidth]{figures/F4c_loss_2026.pdf}""", r"""\includegraphics[width=\textwidth]{figures/F4_event_2026.pdf}""")
m = block(m, r"""\caption{\textbf{The 2026 event.}""", r"""\label{fig:event}""",
          r"""\caption{\textbf{The 2026 event.} (a) Weekly mean gauge at Kaub, 22 June--23 November 2026 (left axis), with the observed weeks, the partly observed week of 28 September, the six-week outlook of 28 September and the assumed recovery shaded, and the share of its normal tonnage that the Kaub reach passes each week (right axis). (b) Weekly German value-added loss: mean of the eleven supplier--buyer networks (line), interquartile range and range (bands), on the same calendar; the two episodes. The vertical line marks the last observed week.}
""")
m = sub1(m, r"""To separate each episode's cost from the cost of their sequence, we ran them apart (Fig.~\ref{fig:waves}).""",
         r"""To separate each episode's cost from the cost of their sequence, we ran them apart on the reference network (Fig.~\ref{fig:waves}).""")
m = block(m, r"""The interaction fades as inventories refill. We test counterfactual scenarios""", r"""\begin{figure}""",
          r"""The depth of the episodes counts more than their sequence. The same shortfall of river capacity spread evenly over the twenty-three weeks costs \finalbatch{\FlatQ}\,\%, about a quarter less than the season as it happened: an acute low water empties the yards that a longer, shallower one would keep fed. The sequence counts too, through the inventories. In the model, firms do not change suppliers between the episodes; what the first leaves to the second is drained inventories and backlog, and the interaction fades as they refill. In counterfactual runs with normal water between the two episodes, the sequence costs \finalbatch{\WaveInterOne}\,\% more than the sum with one week in between, \finalbatch{\WaveInterFour}\,\% with four, and 3\,\% less with eight: by then the plants are working off the backlog of the first episode, producing above their normal rate, and the second episode meets them above baseline, so the shortfall counted against baseline is smaller. The refill time sets how fast this happens: at 15 days instead of the model's 30, inventories are back before the first episode ends, the penalty disappears at gap zero and the catch-up gain appears with any gap (Supplementary Section~S4). A low-water season is priced by how acute its episodes are and how closely they follow each other, not by the tonnage it turns away in total.

""")
m = block(m, r"""\caption{\textbf{The memory of a low-water season.}""", r"""\label{fig:waves}""",
          r"""\caption{\textbf{The memory of a low-water season.} (a) Weekly German loss of the 2026 season (black), of its first episode alone (blue, 22 June--30 August), of its second episode alone (green, from 31 August) and of their sum (dashed); the shaded area is what the sequence adds. (b) Cumulated German loss of the two episodes in sequence against the weeks of normal water between them, with the sum of the two episodes alone (dashed) and the flat profile with the same cumulated capacity shortfall (dotted); in teal, the same experiment at a refill time of 15 days instead of 30. Reference network.}
""")
m = sub1(m, r"""Households lose \finalbatch{\ConsLossBn}~billion USD of consumption, and the 28 modeled economies as a whole \finalbatch{\EUlossBn}~billion of value added, \finalbatch{\NonDEshare}\,\% of it outside Germany, mostly in France\todo{maybe a few words about why France? Which industrial linkages?}.""",
         r"""Households lose \finalbatch{\ConsLossBn}~billion USD of consumption on the reference network, and the 28 modelled economies as a whole \finalbatch{\EUlossEnsBn}~billion of value added across the eleven networks (\finalbatch{\EUlossBn} on the reference network), \finalbatch{\NonDEshare}\,\% of it outside Germany, mostly in France, where farm products of the Rhine plain travel by barge down the Rhine to the food industry and the hauliers run short of fuel (Who loses).""")
m = block(m, r"""Across the eleven versions of the supplier--buyer\todo{always use this term} network, the loss is""", r"""\subsection*{Reduced capacity""",
          r"""The spread across the eleven networks, \finalbatch{\EnsSd}\,\% of a quarter around \finalbatch{\EnsMean}, is the sampling uncertainty of the result. The model's specifications are those selected on the 2018 episode; alternative choices move the result further, in both directions: the loading curve by about a quarter up or down, two suppliers per input down by more than a half, no pooling up fourfold, no rail bypass for bulk up by a quarter, and the refill time of inventories and the service rules by up to a third (Supplementary Fig.~\ref{fig:sensitivity}; Supplementary Sections~S4, S7 and S8).

""")

# ------------------------------------------------------------------ Results: capacity, who loses
m = sub1(m, r"""The two can be run apart. With the surcharge alone""", r"""The two can be run apart on the reference network. With the surcharge alone""")
m = sub1(m, r"""no delivery is refused at these surcharges (Methods)\todo{""",
         r"""no delivery is refused at these surcharges (Methods). This is a modelling choice: in the model no buyer cuts its orders when its inputs cost more, which holds in the short run for moderate increases, freight being about 5\,\% of the input bill of the median firm and a quarter to a half for transport operators; over repeated seasons the surcharges would weigh on the competitiveness of the valley's industry, a longer-run effect outside a weekly model of one season (Discussion)\todo{""")
m = sub1(m, r"""This counterintuitive result is linked to the price-signaling effect of the surchages, which allocates capacity better:""",
         r"""This counterintuitive result comes from the price signal of the surcharge, which allocates the capacity better:""")
m = sub1(m, r"""These figures only represent a fifth of the missed deliveries in Germany over the XX weeks of the event; the other four fifths are cascading effects (\finalbatch{\TransportWithheldShare}\,\% withheld, Supplementary Section~S5).""",
         r"""The deliveries withheld at the river are only a fifth of the deliveries that German buyers miss over the event; the other four fifths are rationing along the chains that start there (\finalbatch{\TransportWithheldShare}\,\% withheld, Supplementary Section~S5).""")
m = sub1(m, r"""doubling them for every buyer reduces the 2018 loss by almost three (\LadderD{} instead of \DEUlossQyy\,\% of a quarter)""",
         r"""doubling them for every buyer divides the 2018 loss by almost three (\LadderD{} instead of \DEUlossQyy\,\% of a quarter on the reference network)""")
m = sub1(m, r"""Most of the loss lies outside the Rhine industrial zones. Of the German gross loss, industry""",
         r"""Most of the loss lies outside the Rhine industrial zones. On the reference network, of the German gross loss, industry""")
m = sub1(m, r"""Goods producers and construction work off a fifth of their backlog by the end of the run, resulting in a net loss of XXX (\finalbatch{\NetShare}\,\% of gross), with delay cost of \finalbatch{\DelayCost}~million USD \todo{recall what is the delay cost}(Methods).""",
         r"""Goods producers and construction work off a fifth of their backlog by the end of the run, which leaves a net loss of \finalbatch{\DEUnetBn}~billion USD, \finalbatch{\NetShare}\,\% of the gross loss (Methods).""")
m = sub1(m, r"""France loses \finalbatch{\FRAlossBn}~billion USD, three-fifths in its food chain and a fifth in road transport: barge-delivered farm products \todo{French farm products or German one?}are withheld at the river, German inputs fall short, and the food industry rations households\todo{where, in France? this sentence is not so clear}.""",
         r"""France loses \finalbatch{\FRAlossBn}~billion USD, three-fifths in its food chain and a fifth in road transport: in the model, farm products of eastern France travel by barge down the Rhine to the French food industry and are withheld at Kaub, French hauliers run short of fuel, and the food industry rations its clients, French households among them; German inputs play no part in it. The model's cost-based routing sends this domestic grain by the Rhine, which likely overstates the real barge share, so France's loss reads as an upper bound.""")
m = sub1(m, r"""Fig.~\ref{fig:who}b--c give the cumulated loss by sector and by country.""", r"""Fig.~\ref{fig:who}b--c give the cumulated loss by country and by sector.""")
m = block(m, r"""\caption{\textbf{Who loses.}""", r"""\label{fig:who}""",
          r"""\caption{\textbf{Who loses.} (a) Production loss by NUTS2 region in the peak week (mid-October 2026), share of the region's weekly value added, reference network. (b) Cumulated value-added loss by country, billion USD (log scale). (c) Cumulated German loss by sector, billion USD: gross (bars; the goods and construction sectors that can catch up, the services that cannot) and net of the backlog worked off by the end of the run (dots).}
""")

# ------------------------------------------------------------------ Results: adaptation
m = sub1(m, r"""We rerun the event under five adaptation scenarios (Fig.~\ref{fig:levers}). One extra week of inventories for every buyer removes \finalbatch{\LevStock}\,\% of the German loss (\finalbatch{\LevStockRange}\,\% across the networks). The same week for the barge-dependent buyers alone (transport operators, utilities, chemicals, cement and basic metals) removes \finalbatch{\LevStockT}\,\% (\finalbatch{\LevStockTRange}). In absolute terms: seven days of inputs for every German buyer is about 26 billion USD of goods, which avoid about 7 billion of loss in this event. Those extra inventories costs 4.5 billion for  barge-dependent buyers alone, avoiding for 3.3 billion: roughly half the effect for a sixth of the inventory.""",
         r"""We rerun the event under five adaptation scenarios, each paired with its own base on each of the eleven supplier--buyer networks (Fig.~\ref{fig:levers}). One extra week of inventories for every buyer in the 28 economies removes \finalbatch{\LevStockAvg}\,\% of the German loss on average (\finalbatch{\LevStockRange}\,\% across the networks). The same week for the barge-dependent buyers alone (transport operators, utilities, chemicals, cement and basic metals) removes \finalbatch{\LevStockTAvg}\,\% (\finalbatch{\LevStockTRange}). In absolute terms, seven days of inputs for every German buyer is about 26 billion USD of goods, which avoid about 7 billion of loss in this event; the same week for the barge-dependent buyers alone is 4.5 billion of inventory for 3.3 billion avoided, roughly half the effect for a sixth of the inventory.""")
m = sub1(m, r"""removes \finalbatch{\LevDeep}\,\% of the loss (\finalbatch{\LevDeepRange}).""", r"""removes \finalbatch{\LevDeepAvg}\,\% of the loss (\finalbatch{\LevDeepRange}).""")
m = sub1(m, r"""A fleet built for low water removes \finalbatch{\LevFleet}\,\% (\finalbatch{\LevFleetRange}) of losses. After 2018 the chemical companies had nine shallow-draught tankers built that can still carry about 800 tonnes at a gauge of 30\,cm, against 80\todo{80 tonnes at 30cm or 800 tonnes at 80cm?} for a standard vessel \citep{wiwo2026,contargo2026}.""",
         r"""A fleet built for low water removes \finalbatch{\LevFleetAvg}\,\% (\finalbatch{\LevFleetRange}) of the loss. After 2018 the chemical companies had nine shallow-draught tankers built that can still carry about 800 tonnes at a gauge of 30\,cm, against about 400 for a standard vessel at the same gauge \citep{wiwo2026,contargo2026}.""")
m = sub1(m, r"""and rises in \FleetPeakUpDraws{} of the ten further ones, because a fleet that carries more in the shoulder weeks keeps more buyers producing into the episode\todo{I don't understand this, you mean that it can be worse to have a better fleet?};""",
         r"""and rises on \FleetPeakUpDraws{} of the ten further ones. The cumulated loss falls on every network, but a fleet that carries more in the shoulder weeks keeps more plants running into the deepest weeks, where it carries nothing more, so more of them stop in the same week: a lower total and a higher single worst week;""")
m = sub1(m, r"""The three together remove \finalbatch{\LevPackage}\,\% (\finalbatch{\LevPackageRange}).""", r"""The three together remove \finalbatch{\LevPackageAvg}\,\% (\finalbatch{\LevPackageRange}).""")
m = sub1(m, r"""and it is the same for the 28 economies as a whole (inventories \finalbatch{\LevEUStock}\,\%""", r"""and it is the same for the 28 economies as a whole (on the reference network: inventories \finalbatch{\LevEUStock}\,\%""")
m = sub1(m, r"""Rail is a substitute rather than a lever at the river's scale\todo{why boosting rail transshipment is not a lever?}, and its size is the one quantity the model cannot set:""",
         r"""Rail is a lever whose size the model cannot set, so we report it as a sensitivity at two ceilings rather than as a lever of a stated size:""")
m = sub1(m, r"""Supplementary Section~S8)\todo{if it is the response evidenced by some statistical analysis, why shouldn't we use it as baseline?}.""",
         r"""Supplementary Section~S8). The regression's response covers all cargo and mostly containers, which the model already lets switch, so applied to bulk alone it overstates what rail can take on; the 50 kt reading is the one with evidence from 2026 behind it, and bulk does not switch in the main runs because no evidence supports more.""")
m = block(m, r"""\caption{\textbf{Adaptation.}""", r"""\label{fig:levers}""",
          r"""\caption{\textbf{Adaptation.} (a) Loss avoided by each lever in Germany, as a share of the base: mean over the eleven supplier--buyer networks (bars), each lever paired with its own base on the same network (dots). The inventory levers apply to every buyer in the 28 economies, the targeted one to the barge-dependent buyers; ``all three together'' combines the fairway, the fleet and the general inventory lever. (b) Weekly German loss of the base and of each lever on the reference network; the fleet lowers the cumulated loss and, on this network, the peak (\PeakBase{} to \PeakFleet\,\% of a week), which it raises on \FleetPeakUpDraws{} of the ten further networks.}
""")

# ------------------------------------------------------------------ Discussion
m = sub1(m, r"""and it does not count the real resources that the extra journeys, fuel and delays consume.""",
         r"""and it does not count the real resources that the extra journeys, fuel and delays consume. Over repeated seasons the surcharges and the delays would also weigh on the competitiveness of the valley's industry, a longer-run effect that a weekly model of one season does not capture.""")
m = sub1(m, r"""Run apart, the two episodes of 2026 cost \finalbatch{\WaveSumQ}\,\% of a quarter; in sequence they cost \finalbatch{\DEUlossQ}\,\%,""",
         r"""Run apart on the reference network, the two episodes of 2026 cost \finalbatch{\WaveSumQ}\,\% of a quarter; in sequence they cost \finalbatch{\DEUlossQ}\,\%,""")

# ------------------------------------------------------------------ Methods
m = sub1(m, r"""a partially-binding production function, inpuand t pooling across regions""", r"""a partially-binding production function, and input pooling across regions""")
m = sub1(m, r"""The other 39 sectors are placed on NUTS3 employment from the regional accounts (Supplementary Section~S1)\todo{we need to cite the data somewhere for each source, add bibtex ref. here probably is the most adequate}.""",
         r"""The other 39 sectors are placed on NUTS3 employment from the Eurostat regional accounts \citep{eurostat2025regio} (Supplementary Section~S1; the facility datasets are refs.~\citep{spam2020,gem2025,climatetrace2024,fineprint2022}).""")
m = sub1(m, r"""This draw is seeded and deterministic; the eleven network versions vary the seed. The reference network is the model's default seed, fixed before any run of this study and not selected on its results; it sits in the upper half of the 2018 result distribution (see Results)\todo{fine to have a ref run, but I would find it more logical to show the mean when plotting indicators or citing figures}. A supplier size corresponds to an output share """,
         r"""This draw is seeded and deterministic; the eleven versions of the supplier--buyer network vary the seed. Headline numbers are means over the eleven versions; the decompositions by sector, country and shipment, which need the link-level export, are on the reference network, the model's default seed, fixed before any run of this study and not selected on its results, which sits in the upper half of the distribution of both events. Several agents share a region--sector, so a supplier's size is its share of the output """)
m = sub1(m, r"""of the region--sector it belongs to, weighted by employment or production capacity.""", r"""of the region--sector it belongs to, allocated by employment or production capacity.""")
m = sub1(m, r"""(18 commodity-like products are poolable""", r"""(18 products are poolable, standardised goods for which the same product from different regions is interchangeable, such as fuels, grain, cement, steel and basic chemicals""")
m = sub1(m, r"""; Supplementary Section~S1 lists them). """, r"""; Supplementary Section~S1 lists them, and the no-pooling run bounds the choice). """)
m = sub1(m, r"""with $\theta_j$ the share of transport in the output of the supplying agent $j$, calculated as the transport entries of its country-sector intermediary inputs over its output in the MRIO (0 to 0.6 across agents; 0.2 for the few sectors whose row of the table has no transport inputs""",
         r"""with $\theta_j$ the transport intensity of the supplying agent $j$, the transport services among its country-sector's intermediate purchases over those purchases in the MRIO (0 to 0.6 across agents; undefined for one sector, households as employers, whose output is never shipped, and set to 0.2 there without effect""")
m = sub1(m, r"""with a value of time per cargo class and transfer costs at terminals. \todo{if we do use official source, would be good to mention them}""",
         r"""with a value of time per cargo class and transfer costs at terminals; the sources of the rates are listed in Supplementary Table~\ref{tab:rates}.""")
m = sub1(m, r"""which approximates the inland modal split of Germany and the Netherlands by cargo class, the entry ports of EU imports, and the tonnage along the Rhine. Supplementary Section~S2 shows the calibration results.""",
         r"""which approximates the inland modal split of Germany and the Netherlands by cargo class and the tonnage along the Rhine; the port tonnages are not calibrated, and the Mediterranean and Atlantic ports are within 30\,\% of the Eurostat counts while the North Sea ports are not (Supplementary Section~S2 reports the residuals).""")
m = sub1(m, r"""All this tonnage is bulk; the model assigns containers via rail. In reality, containers also pass Kaub""",
         r"""All this tonnage is bulk: the model assigns the Rhine's containers to rail, whereas roughly 10~Mt a year of containers pass Kaub in reality, about a sixth of its tonnage \citep{ccnr2023}; Results states what this residual bears on and the sensitivity that bounds it""")
m = sub1(m, r"""listed with their nature and transformation in Supplementary Table~\ref{tab:loading}""", r"""listed with their nature, transformation and source in Supplementary Table~\ref{tab:loading} \citep{vandorsser2020,contargo2026,bfg2026}""")
m = sub1(m, r"""If this assignment leads a reach""", r"""Every stretch of the Rhine carries a capacity, its normal tonnage plus 2\,\%, and the gauge lowers Kaub's; if this assignment leads a stretch (in these runs only Kaub)""")
m = sub1(m, r""" to go over-capacity, all shipments going through it are cut in proportion so that the reach is exactly full""", r""" to go over capacity, all shipments through it are cut in proportion so that it is exactly full""")
m = sub1(m, r"""Road never carries the main leg of a bulk shipment""", r"""By construction, road never carries the main leg of a bulk shipment: a truck carries 25 tonnes against 2,000 and more for a barge or an ore train, so road is not a substitute for bulk at the river's scale in the time of an event""")
sp = span(m, r"""\paragraph{The measured economy.}""", r"""\paragraph{Loss accounting.}""")
if sp:
    m = m[:sp[0]] + m[sp[1]:]
m = sub1(m, r"""We report as net loss the backlog left at the end of the run, and as delay cost the backlog carried while outstanding at 13\,\% a year, an assumed carrying rate of the delayed output\todo{looks super arbitrary, we need to justify. Did someone did sth similar?} (the cost of capital plus storage; the delay cost is reported apart and never added to the lost production); for every other sector""",
         r"""We report as net loss the backlog left at the end of the run; for every other sector""")
m = sub1(m, r"""the 2018 comparison as a whole is therefore an in-sample check of consistency, not a validation.""",
         r"""the 2018 comparison as a whole is therefore an in-sample check of consistency, not a validation. The economy is the 2022 accounts for both events, in 2022 prices and US dollars: the 2018 test uses the river of 2018 on the economy of 2022, as a benchmark under the assumption that the same sectors depend on the river in similar ways, not as a reconstruction of 2018.""")
m = sub1(m, r"""\textit{Inventories +7 days} adds seven days to every inventory target below the 90-day coping duration\todo{Germany only or all economy?}.""",
         r"""\textit{Inventories +7 days} adds seven days to every inventory target below the 90-day coping duration, for every buyer in the 28 economies (the targets are set per buying industry, not per country).""")
m = sub1(m, r"""Every adaptation is run on the reference network and, paired with its own base, on ten further versions of the supplier network, each with its own cached network.""",
         r"""Every adaptation is run on the reference network and, paired with its own base, on ten further versions of the supplier--buyer network, each with its own cached network; the loss avoided is reported as the mean over the eleven, with their range.""")
m = sub1(m, r"""The protocol is fixed here. Index:""", r"""The protocol is fixed here; the series scored is the reference network's, as issued on 7 October, and the mean over the eleven networks, the headline of this paper, is scored alongside it. Index:""")

# ------------------------------------------------------------------ D5: the uncertainty figure leaves the main text (to the SI)
# (the figure environment of F8 sat inside the uncertainty paragraph's block above and left with it)
if "F8_sensitivity" in m:
    miss("F8 figure still in main.tex")
m = sub1(m, r"""\setcounter{figure}{0}""", r"""\setcounter{figure}{0}\renewcommand{\thefigure}{S\arabic{figure}}""")

# ------------------------------------------------------------------ vocabulary, notes
m = re.sub(r"(?<!buyer )supplier network", "supplier--buyer network", m)
m = m.replace("the eleven networks", "the eleven networks")
m, n = strip_notes(m)
print(f"notes removed: {n}; remaining todos: {m.count(chr(92) + 'todo{')}")
if not DRY:
    (O / "main.tex").write_text(m.replace("\n", nl), encoding="utf-8")
    print("main.tex written")
else:
    print(f"DRY RUN: {len(MISSES)} missing anchors")
    for x in MISSES:
        print(" -", x)
