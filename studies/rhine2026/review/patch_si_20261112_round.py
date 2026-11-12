r"""The author's round of 12 November 2026 on si.tex (Overleaf 4dfe508): the notes N10 to N14, the table of the
prospective test (N09, from the main text to Section S6), the word of the loading-curve variants (N01), and the checks
of the direct edits. The answers and the reasons are in review/revision_20261112_response.md. Running the script again
fails on its first anchor.

    python studies/rhine2026/review/patch_si_20261112_round.py
    python studies/rhine2026/si_tables.py --tag r6_bycargo --lists 20261111 --only prospective_table    # fills the new block
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "si.tex")
assert "\\todo{is that conrrect?}" in d.text, "the round of 12 November is not the text of the copy (already applied?)"

# ------------------------------------------------------------------ S5: how bulk switches mode (N10, N11, N12, N13)
d.line(r"\paragraph{How bulk switches mode.}",
       r"\paragraph{How bulk switches mode.} When its normal route is cut or surcharged, a shipment may take another route. For each route, we distinguish line-haul modes from access modes. Take, for instance, a container that travels a long distance by rail and reaches its destination by road: rail is the line-haul mode, and road is only an access mode. In the model, a mode is a line-haul mode of a route when it carries 100\,km or more of it (the line-haul threshold). An alternative route changes mode when it adds more than 50\,km (the access allowance) on a mode that is not a line-haul mode of the normal route, whatever the length that this mode then reaches. More kilometers on a line-haul mode, or a longer access leg within the allowance, are not a change of mode. A change of mode carries a penalty, and a shipper takes the alternative only when it is cheaper, penalty included, than the normal route with its surcharge. For bulk, we add two restrictions, because a truck carries 25 tonnes, against 2,000 and more for a barge or an ore train, so that road cannot replace the river in the time of an event. The penalty is prohibitive, and road is never a line-haul mode: a bulk shipment may not lengthen a road leg beyond the allowance, whatever the length of that leg on its normal route."
       "\n\n"
       r"We verified this rule link by link on the 2,831 origin--destination pairs (5,707 links) whose bulk crosses Kaub, in a test of September 2026 with the reach closed to bulk for a week, on the baseline before the calibration of Section~S2. Under the kilometer thresholds alone, 1,553 pairs find no alternative (833 million USD of the week's orders) and 1,278 deliver on a route that is not a change of mode (409 million). For nine-tenths of the pairs without an alternative, the cheapest route would leave the river at Koblenz, pass the reach by land, and return to a barge. The land leg is 88\,km of truck for two-thirds of the pairs without an alternative, and a shorter truck leg or a train for the others; it is not allowed, because it exceeds the access allowance. The pairs whose normal route already has 100\,km or more of road (35\,\% of all pairs) do deliver under the kilometer thresholds alone, by lengthening that road leg. The adopted rule forbids it, since road is never a line-haul mode for bulk, and the share of the week's orders left without an alternative rises from 67 to 85\,\% (Table~\ref{tab:thresholds}). No observation gives this share: the reach has never been closed, and the freight statistics do not record which shipments combine modes. The thresholds are therefore conventions, not values fitted to evidence. The table shows how much they matter, and their consequence for the loss is tested in full runs through the amount of bulk that may go by rail (Section~S8).")

d.sub(r"under each setting of the rule.\todo{are those indicators compared with some evidence to determine what we take as baseline?}}",
      r"under each setting of the rule.}")

# ------------------------------------------------------------------ S6: the protocol, and the table that comes from the main text (N08, N09)
d.sub(r"\paragraph{The protocol.} Table~\ref{tab:prospective} of the main text gives the model's monthly shortfall of German industrial production from July to December 2026 against the path that the statistical model of \citep{ademmer2023} implies for the same months and the same low-water days (observed to 10 November, forecasted after). The two differ in shape: the model is spiky, with episodes in August and October and a partial recovery in September, whereas the reference network is at baseline in November and above it in December, as the backlogs are worked off; the regression path is smooth and does not rebound.",
      r"\paragraph{The protocol.} Table~\ref{tab:prospective} gives the model's monthly shortfall of German industrial production from July to December 2026 against the path that the statistical model of ref.~\citep{ademmer2023} implies for the same months and the same low-water days (observed to 10 November, forecast after). The two differ in shape. The model is spiky, with episodes in August and October and a partial recovery in September; on the reference network, it is at baseline in November and above it in December, as the backlogs are worked off. The regression path is smooth and does not rebound.")
d.sub(r"(the releases for July and August, of 7 September and 7 October, are not scored).",
      r"(the releases for July and August, of 7 September and 7 October, are not scored). No score is given in this version: it will be computed when the four months are published.")
d.sub("which is why the gross event loss and the signed quarterly change differ.\n\n\\paragraph{The monthly path by sector.}",
      "which is why the gross event loss and the signed quarterly change differ.\n\n"
      "% >>> generated table si_prospective (edit the caption, headers and text cells here; studies/rhine2026/si_tables.py only checks and refreshes the numbers)\n"
      "% <<< generated table si_prospective\n\n"
      "\\paragraph{The monthly path by sector.}")
d.sub(r"the sectoral counterpart of the prospective test of the main text:", r"the sectoral counterpart of Table~\ref{tab:prospective}:")
d.sub(r"Pre-specified for the prospective test of the main text:", r"Pre-specified for the prospective test:")

# ------------------------------------------------------------------ S7: the two episodes at a 15-day refill time (N14, with N03 and N06)
d.line(r"\paragraph{The two waves at a 15-day refill time",
       r"\paragraph{The two episodes at a 15-day refill time.} Table~\ref{tab:crosswaves} repeats the experiment of the main text on the two episodes with a refill time of 15 days instead of 30. At 15 days, the two episodes of 2026 cost \WaveARest{} and \WaveBRest\,\% of a quarter apart and \WaveSeqRest{} in sequence (\WaveInterRest\,\% against the sum, where the 30-day rule gives +\WaveInterShare). With two and four weeks of normal water between them, the sequence costs \WaveGapTwoRestAbs{} and \WaveGapFourRestAbs\,\% less than the sum: at 15 days, the buyers hit by the first episode have refilled their inventories before the second arrives, and the plants working off their backlog are producing above baseline when it does. A faster refill is bounded in the model. A buyer that refills in 15 days orders, each week, twice as large a part of its inventory gap, but it receives only what its suppliers and the river can deliver. A supplier produces at most 125\,\% of its baseline output (the utilization rate of 0.8, Section~S4) and rations its clients beyond that, and the reopened Kaub reach passes at most 102\,\% of its normal tonnage (the headroom, Table~\ref{tab:revision}). Neither bound was varied together with the refill time. The memory that the gap experiment measures therefore depends jointly on the refill time of the inventory rule, on the spare capacity of the suppliers, and on the headroom of the reopened reach; it is not a measured time constant.")
d.sub(r"\caption{\textbf{The two waves of 2026 at two refill times.} German loss (\% of a quarter) of the two waves alone,",
      r"\caption{\textbf{The two episodes of 2026 at two refill times.} German loss (\% of a quarter) of the two episodes alone,")
d.sub("first wave alone (A) &", "first episode alone (A) &")
d.sub("second wave alone (B) &", "second episode alone (B) &")

# ------------------------------------------------------------------ S8: two sentences of the direct edits
d.sub(r"The central table with its loading is raised by 0.10 between 15 and 55\,cm,", r"The loading share of the central table is raised by 0.10 between 15 and 55\,cm,")
d.sub(r"\citep{wiwo2026,contargo2026}. It loads more at every gauge between 15 and 55\,cm", r"\citep{wiwo2026,contargo2026}. This fleet loads more at every gauge between 15 and 55\,cm")
d.sub("Rail is a lever based on the number of trains that can be added at short notice, which is not known.",
      "Rail is a lever whose size depends on the number of trains that can be added at short notice, which is not known.")

# ------------------------------------------------------------------ S9: 'capacity reduction' for what the loading-curve variants scale (N01)
d.sub("loading curve, shortfall & as built", "loading curve, capacity reduction & as built")
d.sub(r"With the shortfall it implies raised or lowered by 15\,\%,",
      r"With its capacity reduction, the share of the normal tonnage that it keeps off the river, raised or lowered by 15\,\%,")
d.sub(r"the loading curve with its shortfall raised and lowered by 15\,\%;", r"the loading curve with its capacity reduction raised and lowered by 15\,\%;")

d.save()
