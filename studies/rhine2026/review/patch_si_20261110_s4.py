r"""SI revision of 10 Nov 2026, section S4 Mechanism tests (the author's notes N34-N45 and the direct edits E32-E42).

N34      an introductory sentence
N35      the caption of the modal-switch table is one sentence; its content is a paragraph, which also says why the
         adopted rule was chosen (road cannot replace the river for bulk)
N36      'Capacity and surcharge' rewritten: what the capacity limit alone does, what the surcharge alone does, both;
         no mention of an earlier version of the paper
N37      the paragraph on supplier weights is removed
N38-N40  the weekly table: heading aligned with the caption, a spanning header over the three flow columns (in kt: the
         table holds tonnages, not million USD), 'cut' named 'total'
N41      the paragraph 'Conservation and stationarity' is removed (its content is in the specifications section)
N42      the paragraph and table of 'the sensitivities of the revision' leave this section for S7 (stage 1 moves them;
         the S7 patch rewrites them as the sensitivity table)
N43-N45  the crossed experiments are two paragraphs and two tables; the reference column is named
Stage 1 edits the text and opens the blocks; then
    python studies/rhine2026/si_tables.py --tag r6_bycargo --lists 20261102 --only cross
fills si_cross and si_cross_waves.

    python patch_si_20261110_s4.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")
MARK = "(edit the caption, headers and text cells here; studies/rhine2026/si_tables.py only checks and refreshes the numbers)"

# ------------------------------------------------------------------ N34, N35: introduction, the modal-switch rule
d.line(r"\todo{give one introductory sentence to this section}",
       r"This section documents the checks made on the mechanisms through which low water acts in the model: the rule that lets a shipment change its route, the respective roles of the capacity limit and of the surcharge, the flows turned away at Kaub week by week, the levers under a rail ceiling, and the interaction of the two waves at a shorter refill time. It ends with the sectoral forecast that accompanies the prospective test of the main text.")
d.line("The penalty-aware alternative search and the line-haul rule were verified link by link",
       r"\paragraph{The modal-switch rule.} When its normal route is cut or surcharged, a shipment may take another route, but bulk may not change its mode of transport: a truck carries 25 tonnes, against 2,000 and more for a barge or an ore train, so road cannot replace the river for bulk at the scale and in the time of an event. In the model, a route counts as a change of mode when it puts more than 50\,km of extra distance on a mode that only served for access on the normal route (the access allowance); a mode is a main-leg mode of the normal route when it carries 100\,km or more of it (the line-haul threshold); and road is never a main-leg mode for bulk. The switching penalty is compared with the surcharge on the normal route before a shipper leaves the river. We verified this rule link by link on the 2,831 origin--destination pairs (5,707 links) whose bulk crosses Kaub, in a ten-week test run on the 2026 profile with the Kaub reach closed to bulk (a test of September 2026, on the baseline before the calibration of Section~S2; the route search is the one that a cut shipment runs under the capacity limit). Under the kilometer thresholds alone, 1,553 pairs find no acceptable route (833 million USD of the week's orders), 1,224 deliver on their own modes (385 million) and 54 on a path without penalty (24 million). Table~\ref{tab:thresholds} gives the share of the week's orders left without a route under each setting of the rule. The access allowance decides the outcome: for nine tenths of the pairs without a route, the alternative is a barge to Koblenz, 88\,km of truck around the reach and a barge again, at a median surcharge of 49\,\% on the freight; it is refused because 88\,km exceeds the allowance. The pairs whose normal route already has 100\,km or more of road (35\,\%) would lengthen that road leg instead, which the adopted rule forbids for the reason given above.")
inner = d.block("si_thresholds")
a, b = inner.index(r"\caption{"), inner.index(r"\label{tab:thresholds}")
inner = inner[:a] + r"\caption{\textbf{The modal-switch rule: sensitivity to its thresholds.} Share of the week's bulk orders across Kaub (\%) left without an acceptable route when the reach is closed to bulk, under each setting of the rule.}" + "\n" + inner[b:]
if inner.count(r"setting of the rule & gives up (\%) \\") != 1:
    d.fails.append("thresholds header")
inner = inner.replace(r"setting of the rule & gives up (\%) \\", r"setting of the rule & without a route (\%) \\")
d.block("si_thresholds", inner)

# ------------------------------------------------------------------ N36: capacity and surcharge
d.line(r"\paragraph{Capacity and surchage.}",
       r"\paragraph{Capacity and surcharge.} Low water acts on the river in two ways: the capacity limit caps the tonnage that passes Kaub, and the surcharge makes every tonne that passes dearer. Table~\ref{tab:channels} separates the two with two runs in which one of them is switched off. With the surcharge alone, shipments leave the river when another route becomes cheaper: \ChanBulkAltSurBn{} billion USD of bulk and \ChanContAltSurBn{} billion of containers are rerouted over the 2026 run, nothing is blocked, and the German loss is \SurchargeOnlyQ\,\% of a quarter. With the capacity limit alone, \ChanBulkHeldGateBn{} billion USD of bulk is blocked and little is rerouted (\ChanBulkAltGateBn{} billion of bulk, \ChanContAltGateBn{} of containers), because shippers stay on the river until they are cut; the loss is \GateOnlyQ\,\%. With both, as in the paper, the surcharge first moves off the river the shipments that have an alternative (\ChanBulkAltBn{} billion of bulk, \ChanContAltBn{} of containers), and the capacity limit then blocks \ChanBulkHeldBn{} billion of bulk that has none; the loss is \DEUlossQ\,\%. The capacity limit is thus what produces the loss, and the surcharge reduces it. Containers are never blocked: they always find a rail or road route.")
inner = d.block("si_channels")
for old, new in ((r"\caption{\textbf{Capacity and surchage.} Rerouted and blocked flows (billion USD, summed over the 43 weeks of the 2026 run), by cargo class, in the reference run.}",
                  r"\caption{\textbf{Capacity and surcharge.} Rerouted and blocked flows (billion USD, summed over the 43 weeks of the 2026 run), by cargo class, in the reference run and with each of the two mechanisms alone.}"),
                 ("capacity and surcharge (the paper) &", "capacity and surcharge (reference run) &")):
    if inner.count(old) != 1:
        d.fails.append(f"channels block: {old[:50]}")
    inner = inner.replace(old, new)
d.block("si_channels", inner)

# ------------------------------------------------------------------ the flat profile (the author's text, corrected)
d.line(r"\paragraph{The flat profile.}",
       r"\paragraph{The flat profile.} We built a counterfactual in which the loading share stays flat at the 2026 season's mean (0.40) for the twenty-three weeks. Over the season \GateHeldMt~Mt of flows are blocked in the reference run and \FlatHeldMt~Mt under the flat profile. The blocked tonnage differs by \FlatHeldDiff\,\%, which confirms that the difference in losses between the two profiles does not come from a difference in the tonnage that passes.")

# ------------------------------------------------------------------ N37, N41: two paragraphs removed
d.line(r"\paragraph{Supplier weights through the season.}", None)
d.line(r"\paragraph{Conservation and stationarity.}", None)

# ------------------------------------------------------------------ N38-N40: the weekly table
d.line(r"\paragraph{The gate week by week.}",
       r"\paragraph{Weekly flows turned away at Kaub.} Table~\ref{tab:gate} gives, for every week of the 2026 profile in the reference run, the gauge, the loading share and the tonnage that the capacity limit turns away: in total, rerouted on another route and blocked. The baseline flow at Kaub is \KaubWeekMt~Mt a week. The table covers the 23 weeks of the profile; the limit also turns flows away in \GateRecWeeks{} recovery weeks, when the catch-up traffic exceeds the normal capacity (Section~S3). Over the whole season \GateCutMt~Mt are turned away, of which \GateResentMt~Mt are rerouted and \GateHeldMt~Mt blocked.")
inner = d.block("si_gate")
HEAD = (r" & & & & & \multicolumn{3}{c}{flows turned away (kt)} \\" + "\n" + r"\cmidrule(lr){6-8}" + "\n"
        + r"week & start & status & Kaub gauge (cm) & loading share & total & rerouted & blocked \\")
for old, new in ((r"\caption{\textbf{Weekly flow through Kaub, 2026 reference run.} For each week: the status of the gauge, its weekly mean (cm), the corresponding loading share, and the tonnage (kt) that the gates of the Rhine chain cut, re-sent on another route and withheld (returned to the supplier's inventory)}\todo{add cell above the last 3 headers with "+ '"Flows (mUSD)"}',
                  r"\caption{\textbf{Weekly flows turned away at Kaub, 2026 reference run.} For each week: the status of the gauge, its weekly mean (cm), the corresponding loading share, and the tonnage (kt) that the capacity limit turns away, in total, rerouted on another route and blocked (returned to the supplier's inventory).}"),
                 (r"week & start & status & Kaub gauge (cm) & loading share & cut \todo{replace by total flow} & rerouted & blocked \\", HEAD),
                 (r"week & start & status & Kaub & loading share & cut & re-sent & withheld \\", HEAD)):
    if inner.count(old) != 1:
        d.fails.append(f"gate block: {old[:60]}")
    inner = inner.replace(old, new)
d.block("si_gate", inner)

# ------------------------------------------------------------------ N42: the sensitivity paragraph and table move to S7
par = d.get_line(r"\paragraph{Sensitivities of the revision.}")
head = r"\paragraph{Sensitivities of the revision.}\todo{we don't need to explain this revision. Consider removing.} Table~\ref{tab:revision} gives the runs made after the review of 5 October 2026 on the rebuilt loading curve. "
if not par.startswith(head):
    d.fails.append("the sensitivity paragraph does not start as expected")
par = r"\paragraph{One-at-a-time sensitivities.} Table~\ref{tab:revision} gives the sensitivity runs, each a change of one rule or parameter of the reference run. " + par[len(head):]
block = d.remove_block("si_revision")
d.line(r"\paragraph{Sensitivities of the revision.}", None)
d.sub("\\subsection*{S7 Sensitivity tables}\n",
      "\\subsection*{S7 Sensitivity tables}\n\n" + par + "\n\n% >>> generated table si_revision " + MARK + "\n" + block + "% <<< generated table si_revision\n")

# ------------------------------------------------------------------ N43-N45: two paragraphs, two tables
d.line(r"\paragraph{The levers under finite rail, and the memory at a 15-day refill time.}",
       r"\paragraph{The levers under a rail ceiling.} Table~\ref{tab:cross} gives the four single levers on top of a rail ceiling of 50 kt a week. Under the ceiling each lever removes a larger share of a smaller loss than under the paper's rule (inventories \CrossStockRail\,\% against \LevStock, fairway \CrossDeepRail{} against \LevDeep, targeted inventories \CrossStockTRail{} against \LevStockT, fleet \CrossFleetRail{} against \LevFleet), in the same order. In absolute terms the benefits overlap: the week of inventories avoids \CrossStockAloneBn{} billion USD alone and \CrossStockOnRailBn{} on top of the rail relief, which avoids \RailAloneBn{} alone, so the two together avoid \CrossStockOverlap\,\% less than the sum of their separate benefits; the overlap is \CrossDeepOverlap\,\% for the fairway, \CrossStockTOverlap{} for the targeted inventories and \CrossFleetOverlap{} for the fleet (the reference network, one ceiling).")
d.block("si_cross", "")
end = "% <<< generated table si_cross\n"
d.sub(end, end + "\n" + r"\paragraph{The two waves at a 15-day refill time.} Table~\ref{tab:crosswaves} repeats the wave experiment of the main text with a refill time of 15 days instead of 30. At 15 days the two waves of 2026 cost \WaveARest{} and \WaveBRest\,\% of a quarter apart and \WaveSeqRest{} in sequence (\WaveInterRest\,\% against the sum, where the 30-day rule gives +\WaveInterShare); with two and four weeks of normal water between them the sequence costs \WaveGapTwoRestAbs{} and \WaveGapFourRestAbs\,\% less than the sum, because at 15 days the buyers hit by the first wave have refilled their inventories before the second wave arrives, and the plants working off their backlog are producing above baseline when it does. The memory that the gap experiment measures therefore depends on the refill time of the inventory rule, jointly with the other constraints of the recovery (the headroom of the reopened reach, Table~\ref{tab:revision}, and the capacity for catch-up); it is not a measured time constant."
      + "\n\n% >>> generated table si_cross_waves " + MARK + "\n% <<< generated table si_cross_waves\n")
d.save()
