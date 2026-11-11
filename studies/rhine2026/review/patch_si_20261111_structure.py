r"""SI, 11 November 2026: the structure approved by the author ("no swap": S1 to S4 stay; S5 to S9 are rebuilt by role).

  S5 Modeling choices for the low water   the 2018 benchmark and the one choice made on it (former S9); the modal-switch rule
                                          (first paragraph of the former S5)
  S6 The 2026 test                        the protocol and the estimates of August (the two last paragraphs of the former S3);
                                          the monthly path by sector (last paragraph and table of the former S5)
  S7 The 2026 season in detail            weekly flows at Kaub; capacity and surcharge, with prices; the inputs that go missing
                                          (former S6); the flat profile; the two waves at a shorter refill time
  S8 Adaptation levers: how each is built how a lever is measured (note N10); inventories, fairway, fleet, rail; the levers
                                          under a rail ceiling
  S9 Sensitivity analysis                 one table, a list ranked by size of effect (the paragraphs on the inventories and
                                          on the suppliers merged in; the table of inventory levels goes), what was not varied

The blocks are moved whole; only openers, paragraph titles and the reading of the sensitivity table are rewritten. Notes N10
and N11 are answered by the move (the sentence on the levers run on every network goes to S8; the two crossed experiments
keep their small tables, one in S7 and one in S8). Pointers to sections are updated in si.tex and main.tex.
    python patch_si_20261111_structure.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "si.tex")
if r"\subsection*{S5 Modeling choices for the low water}" in d.text:
    sys.exit("already applied: si.tex has the new structure")
L = d.text.split("\n")


def at(prefix: str, after: int = 0) -> int:
    hits = [i for i, ln in enumerate(L) if i >= after and ln.startswith(prefix)]
    if len(hits) != 1:
        sys.exit(f"anchor: {len(hits)} lines start with {prefix[:70]!r}")
    return hits[0]


A = [at(r"\paragraph{The prospective test: protocol.}"),
     at(r"\paragraph{The estimates of August 2026.}"),
     at(r"\subsection*{S4 Weekly sequence and model specifications}"),
     at(r"\subsection*{S5 Mechanism tests}"),
     at(r"\paragraph{The modal-switch rule.}"),
     at(r"\paragraph{Capacity and surcharge.}"),
     at(r"\paragraph{The flat profile.}"),
     at(r"\paragraph{Weekly flows turned away at Kaub.}"),
     at(r"\paragraph{The levers under a rail ceiling.}"),
     at(r"\paragraph{The two waves at a 15-day refill time.}"),
     at(r"\paragraph{Sectoral signatures of the forecast.}"),
     at(r"\subsection*{S6 What crosses Kaub, and at what price}"),
     at(r"\subsection*{S7 Sensitivity analysis}"),
     at(r"\paragraph{The level of the inventories on the 2018 event.}"),
     at(r"\paragraph{Supplier networks, loading curve and number of suppliers on the 2018 event.}"),
     at(r"\paragraph{What was not varied.}")]
A.append(at(r"\begin{figure}", after=A[-1]))
A += [at(r"\subsection*{S8 Rail and the low-water fleet}"), at(r"\paragraph{The low-water fleet.}"),
      at(r"\subsection*{S9 Selecting the representation of the river on the 2018 low water}")]
if A != sorted(A):
    sys.exit(f"anchors out of order: {A}")
A.append(len(L))
names = ["protocol", "august", "S4", "S5head", "modal", "capsur", "flat", "gate", "cross", "waves15", "sectors", "S6", "S7head",
         "ladder", "suppliers", "notvaried", "fig", "rail", "fleet", "S9"]
seg = {n: L[A[k]:A[k + 1]] for k, n in enumerate(names)}
head = L[:A[0]]


def strip(lines: list[str]) -> list[str]:
    """Without the blank lines at both ends."""
    a, b = 0, len(lines)
    while a < b and not lines[a].strip():
        a += 1
    while b > a and not lines[b - 1].strip():
        b -= 1
    return lines[a:b]


def block(lines: list[str], name: str) -> tuple[list[str], list[str], list[str]]:
    """(before, table block with its markers, after) of the generated table `name` inside `lines`."""
    i = next(k for k, ln in enumerate(lines) if ln.startswith(f"% >>> generated table {name}"))
    j = next(k for k, ln in enumerate(lines) if ln.startswith(f"% <<< generated table {name}"))
    return lines[:i], lines[i:j + 1], lines[j + 1:]


def retitle(lines: list[str], old: str, new: str) -> list[str]:
    hits = [k for k, ln in enumerate(lines) if ln.startswith(old)]
    if len(hits) != 1:
        sys.exit(f"title: {len(hits)} lines start with {old!r}")
    out = list(lines)
    out[hits[0]] = new + out[hits[0]][len(old):]
    return out


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        sys.exit(f"text: found {text.count(old)} of {old[:80]!r}")
    return text.replace(old, new)


# ---- S5: the 2018 benchmark and the choice (former S9), the modal-switch rule ------------------------------------------
s9 = strip(seg["S9"])
if not (s9[0].startswith(r"\subsection*{S9") and s9[2].startswith("This section documents the benchmark built for the 2018 event")):
    sys.exit("the former S9 does not open as expected")
s9_body = retitle(strip(s9[3:]), r"\paragraph{The benchmark.}", r"\paragraph{The 2018 benchmark.}")
modal = retitle(strip(seg["modal"]), r"\paragraph{The modal-switch rule.}", r"\paragraph{Bulk does not change mode: the modal-switch rule.}")
S5 = [r"\subsection*{S5 Modeling choices for the low water}", "",
      "This section gives the reasons for the two rules that decide how a low water acts in the model, with the checks made on each. "
      "The first is that low water limits the tonnage that passes Kaub, a representation chosen on the 2018 event against a statistical "
      "benchmark. The second is that bulk does not change its mode of transport. The level of the inventories and the number of suppliers "
      "per input were also compared with the 2018 benchmark; both stay at their reference values, and the comparison is reported with the "
      "sensitivities (Section~S9).", ""] + s9_body + [""] + modal

# ---- S6: the 2026 test --------------------------------------------------------------------------------------------------
S6 = [r"\subsection*{S6 The 2026 test}", "",
      "This section holds what the main text needs to test the 2026 results against data from outside the model: the protocol of the test "
      "on the production statistics, the monthly path of the sectors on the river, and the comparison with the estimates made during "
      "the event.", ""] + strip(seg["protocol"]) + [""] + strip(seg["sectors"]) + [""] + strip(seg["august"])

# ---- S7: the 2026 season in detail --------------------------------------------------------------------------------------
s6 = strip(seg["S6"])
if not (s6[0].startswith(r"\subsection*{S6") and s6[2].startswith(r"\KaubLinks{} commercial links cross Kaub") and s6[4].startswith("The run with the surcharge alone")
        and len(s6) == 5):
    sys.exit("the former S6 does not have the two paragraphs expected")
first = ("The run with the surcharge alone (no loss, against \\GateOnlyQ\\,\\% of a quarter with the capacity limit alone; Section~S5) is the direct "
         "evidence that the price channel has no output effect at these magnitudes in the model. ")
if not s6[4].startswith(first):
    sys.exit("the first sentence of the second paragraph of the former S6 is not the one expected")
price = (r"\paragraph{What crosses Kaub, and at what price.} " + s6[2] + " "
         + first.strip().replace("; Section~S5)", r"; Table~\ref{tab:channels})"))
missing = r"\paragraph{Which inputs go missing.} " + s6[4][len(first):]
S7 = [r"\subsection*{S7 The 2026 season in detail}", "",
      "This section documents results that back sentences of the main text on the 2026 season: what the capacity limit turns away at Kaub "
      "week by week, the respective roles of the capacity limit and of the surcharge, the prices and the inputs that go missing, and two "
      "checks on the sequence of the season.", ""] \
     + strip(seg["gate"]) + [""] + strip(seg["capsur"]) + ["", price, "", missing, ""] + strip(seg["flat"]) + [""] + strip(seg["waves15"])

# ---- S8: the levers ----------------------------------------------------------------------------------------------------
rail = strip(seg["rail"])
if not (rail[0].startswith(r"\subsection*{S8") and rail[2].startswith("Rail is a lever whose size the model cannot set")):
    sys.exit("the former S8 does not open as expected")
rail_body = [r"\paragraph{Rail, a bounded substitute.} " + rail[2]] + rail[3:]
S8 = [r"\subsection*{S8 Adaptation levers: how each is built}", "",
      "This section defines the levers of the main text and says what each holds fixed. Each lever is one change to the 2026 run. It is run "
      "on the reference network and, against the base of that network, on each of the ten further supplier--buyer networks; the loss "
      "avoided is reported as the mean over the eleven networks, with their range.", "",
      r"\paragraph{Inventories.} The lever adds seven days to every inventory target below the 90-day coping duration, for every buyer of "
      r"the 28 economies (Tables~\ref{tab:stocks} and~\ref{tab:stockoverrides} give the targets). The inventory that it adds is 7/365 of the "
      "buyers' annual purchases of goods inputs. A targeted variant adds the seven days only for the buyers that depend on barges: transport "
      "operators, utilities, chemicals, cement and basic metals. The package of the main text combines the inventories of every buyer with "
      "the fairway and the fleet below.", "",
      r"\paragraph{Fairway.} The lever adds 20\,cm to the gauge on every reach of the Rhine, for the capacity of the Kaub reach and for the "
      "surcharge of all reaches. It is a simple proxy of the deepening project of the Middle Rhine, which raises the fairway between "
      r"Budenheim and St.~Goar from 1.90 to 2.10\,m at the equivalent low-water level~\citep{bmv2019,baw2026}. A variant adds the 20\,cm "
      r"on the Kaub reach alone (Table~\ref{tab:revision}).", ""] \
     + strip(seg["fleet"]) + [""] + rail_body + [""] + strip(seg["cross"])

# ---- S9: sensitivity ---------------------------------------------------------------------------------------------------
s7 = strip(seg["S7head"])
before, table, after = block(s7, "si_revision")
if not (before[0].startswith(r"\subsection*{S7") and strip(after)[0].startswith("The rule on rail moves the loss most") and len(strip(after)) == 1):
    sys.exit("the former S7 does not have the shape expected")
ITEMS = [
    r"\emph{Pooling of commodity inputs.} The largest effect. If a buyer could not replace the fuel, grain or cement of one region with the "
    r"same product of another, the 2026 loss would be \NoPoolQ\,\% of a quarter instead of \DEUlossQ, and the 2018 loss \NoPoolQyy{} "
    r"instead of \DEUlossQyy.",
    r"\emph{Rail for bulk.} With no rail route for any bulk shipment, the 2026 loss is \RevNoRailAbs\,\% higher (2018: \RevNoRailyyAbs). "
    r"If the bulk cut at Kaub may go by rail up to 50 kt a week, the loss is \RevRailFiftyAbs\,\% lower, and up to 140 kt a week "
    r"\RevRailHundredFortyAbs\,\% lower (2018: \RevRailFiftyyyAbs{} and \RevRailHundredFortyyyAbs, with an industrial shortfall of "
    r"\RevRailFiftyInt{} and \RevRailHundredFortyInt{} percent-months). The cut bulk that finds a rail route is \RailOfferedMin{} to "
    r"\RailOfferedMax{} kt a week, so the lower ceiling is reached in nearly every week (Section~S8). Over the 2026 run rail delivers "
    r"\ReliefBnFifty{} billion USD of goods at 50 kt and \ReliefBnHundredForty{} billion at 140 kt, of which \ReliefLiquidShareFifty{} and "
    r"\ReliefLiquidShareHundredForty\,\% is liquid bulk; at 140 kt the building-materials chain is nearly whole again (construction's share "
    r"of the loss \ShareConstructionRailHundredForty\,\% against \ShareConstruction).",
    r"\emph{The level of the inventories.} Tested on the 2018 event. With every inventory target multiplied by 0.75, 1.25, 1.5 and 2, the "
    r"loss is \LadderZ, \LadderA, \LadderB{} and \LadderD\,\% of a quarter instead of \DEUlossQyy, and the industrial shortfall \LadderIntZ, "
    r"\LadderIntA, \LadderIntB{} and \LadderIntD{} percent-months instead of \ModelInt. At three quarters of the balance-sheet values the "
    r"industrial shortfall is nearer the benchmark's \RecordInt{} percent-months than at any other level, but still below its "
    r"one-standard-deviation band. The balance-sheet values are kept: they are the level that the accounts document, and these runs are a "
    r"sensitivity, not a calibration.",
    r"\emph{The supplier--buyer network.} Who buys from whom is drawn among the suppliers that the accounts allow. Over eleven draws the "
    r"2026 loss runs from \EnsMin{} to \EnsMax\,\% of a quarter (mean \EnsMean) and the 2018 loss from \EnsMinyy{} to \EnsMaxyy{} (mean "
    r"\EnsMeanyy). On 2018 the deepest month is November in every draw, and the cumulated industrial shortfall is "
    r"\ModelIntEnsMean\,$\pm$\,\ModelIntEnsSd{} percent-months (range \ModelIntEnsMin--\ModelIntEnsMax): \DrawsInBand{} of the eleven "
    r"networks fall inside the benchmark's one-standard-deviation band (\RecordIntLow--\RecordIntHigh{} percent-months) and "
    r"\DrawsInWideBand{} inside its 95\,\% band, the others below it, and the August--September onset is weaker than the benchmark's on "
    r"average.",
    r"\emph{The loading curve.} The curve turns a gauge into the share of the normal tonnage that passes Kaub. With the shortfall it "
    r"implies raised or lowered by 15\,\%, the 2026 loss is \TableLowQ{} or \TableHighQ\,\% of a quarter instead of \DEUlossQ{} (2018: "
    r"\TableLowQyy{} or \TableHighQyy{} instead of \DEUlossQyy). On 2018 the industrial shortfall is then \TableLowInt{} or \TableHighInt{} "
    r"percent-months, against \ModelInt{} for the curve as built and \RecordInt{} for the benchmark. The curve as built is kept because it "
    r"is what its sources give, not because it fits best. Its lowest value, below 5\,cm, matters less: at half and at twice that value the "
    r"2026 loss moves by \RevFloorLowRel{} and \RevFloorHighRel\,\%.",
    r"\emph{The number of suppliers per input.} With two suppliers per input instead of one, the 2026 loss is \SupTwoQ\,\% of a quarter "
    r"instead of \DEUlossQ{} (2018: \SupTwoQyy{} instead of \DEUlossQyy), and the industrial shortfall of 2018 falls to \SupTwoInt{} "
    r"percent-months, far below the benchmark's band. The reference value of one supplier is kept.",
    r"\emph{The refill time of an inventory gap.} At 15 and 60 days instead of 30, the 2026 loss moves by \RevRestFifteenRel{} and "
    r"\RevRestSixtyRel\,\%.",
    r"\emph{The headroom of the capacity at normal water.} This margin limits the catch-up traffic after an episode. At 10 and 25\,\% "
    r"instead of 2, the 2026 loss moves by \RevHeadTenRel{} and \RevHeadTwentyFiveRel\,\%.",
    r"\emph{The gauge of the forecast weeks.} The outlook's 25th and 75th percentile paths give \RevQLow{} and \RevQHigh\,\% of a quarter "
    r"against \DEUlossQ{} for the median path.",
    r"\emph{Two rules on energy and services.} With the fuel-oil input of the power sector rated non-critical, the 2026 loss moves by "
    r"\RevDfuelRel\,\%; the utilities' share of the German loss falls from \ShareUtilities{} to \ShareUtilitiesDfuel\,\%, the services' "
    r"rises to \ShareServicesDfuel\,\% because the haulers and logistics operators short of fuel remain, and the loss is \RatioDfuel{} "
    r"times its industrial part (\RatioBase{} in the reference run). With a coping duration of 45 days instead of 90 for the non-storable "
    r"inputs, the loss moves by \RevServRel\,\%; the services' share is \ShareServicesServ\,\% (\ShareServices{} in the reference run) "
    r"and the loss is \RatioServ{} times its industrial part.",
    r"\emph{Variants of two levers.} The fairway on the Kaub reach alone removes \RevDeepLocalRemoves\,\% of the loss, against \LevDeep\,\% "
    r"for the offset on every reach: the Kaub reach is the binding one. The low-water fleet with its gain carried to 100\,cm removes "
    r"\RevFleetWideRemoves\,\%, against \LevFleet{} (Section~S8).",
]
S9 = [r"\subsection*{S9 Sensitivity analysis}", "",
      r"A sensitivity run changes one rule or parameter of the reference run and keeps everything else, the supplier--buyer network "
      r"included. Table~\ref{tab:revision} lists these runs: the rule or parameter, its reference value, the alternatives tested, and the "
      r"German loss that each gives for the 2026 season and, where it was run, for the 2018 event. Figure~\ref{fig:sensitivity} shows the "
      r"same losses by type of uncertainty. In all, the paper rests on \NRuns{} runs. The list of these runs with their main outputs is in "
      "the code repository.", ""] + table + ["",
      "The list below reads the table by size of effect, the largest first. The two rows on the mechanisms, the capacity limit alone and "
      "the surcharge alone, are read in Section~S7.",
      r"\begin{itemize}"] + ["    \\item " + it for it in ITEMS] + [r"\end{itemize}", ""] + strip(seg["notvaried"]) + [""] + strip(seg["fig"])

new = strip(head) + [""] + strip(seg["S4"]) + [""] + S5 + [""] + S6 + [""] + S7 + [""] + S8 + [""] + S9 + [""]
text = "\n".join(new)

# ---- pointers inside si.tex ------------------------------------------------------------------------------------------
text = once(text, "for the forecast weeks as sensitivities (Section~S7).", "for the forecast weeks as sensitivities (Section~S9).")
text = once(text, r"Headrooms of 10 and 25\,\% instead of 2 are tested in Section~S7.", r"Headrooms of 10 and 25\,\% instead of 2 are tested in Section~S9.")

# ---- checks: nothing lost but what is meant to go -------------------------------------------------------------------
for n in ("protocol", "august", "S4", "modal", "capsur", "flat", "gate", "cross", "waves15", "sectors", "notvaried", "fig", "fleet"):
    for ln in strip(seg[n]):
        if ln.strip() and not ln.startswith((r"\paragraph{The modal-switch rule.}",)) and ln not in text:
            sys.exit(f"segment {n}: a line is missing from the new file: {ln[:90]!r}")
for name in ("si_thresholds", "si_channels", "si_gate", "si_cross", "si_cross_waves", "si_prospective_sectors", "si_revision", "si_representations"):
    if len(re.findall(rf"^% >>> generated table {name}(?![A-Za-z0-9_])", text, re.M)) != 1 or len(re.findall(rf"^% <<< generated table {name}[ \t]*$", text, re.M)) != 1:
        sys.exit(f"table block {name} is not there exactly once")
if "generated table si_ladder" in text or r"\todo{" in text:
    sys.exit("the table of inventory levels or a note is still there")
heads = [ln for ln in text.split("\n") if ln.startswith(r"\subsection*{S")]
print("\n".join(heads))
d.text = text
d.done += 1
d.save()
