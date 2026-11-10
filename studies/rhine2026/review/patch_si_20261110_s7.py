r"""SI revision of 10 Nov 2026, section S7 (the author's note N48; N42 of S4 ends here).

N48  The list of the 129 runs leaves the SI: it is a file of the code repository (additional_data/runs_20261102.csv,
     written by si_tables.runs_table). The section is built on one table (tab:revision, new layout): the rule or
     parameter, its reference value, the alternatives tested, the German loss of 2026 and of 2018 and its change.
     The text gives the approach (one change at a time, same network), what the table shows, and what was not varied
     and why.
N42  The paragraph on 'the sensitivities of the revision' is the reading of that table; it no longer mentions a revision.
Stage 1 edits the text, empties the block of si_revision and removes the block of si_runs; then
    python studies/rhine2026/si_tables.py --tag r6_bycargo --lists 20261102 --only revision,runs
fills the table and writes the CSV.

    python patch_si_20261110_s7.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")

d.sub("\\subsection*{S7 Sensitivity tables}\n", "\\subsection*{S7 Sensitivity analysis}\n")

# ------------------------------------------------------------------ the old paragraphs, taken apart
old = d.get_line(r"\paragraph{One-at-a-time sensitivities.}")
head = r"\paragraph{One-at-a-time sensitivities.} Table~\ref{tab:revision} gives the sensitivity runs, each a change of one rule or parameter of the reference run. "
if not old.startswith(head):
    d.fails.append("the sensitivity paragraph does not start as expected")
reading = old[len(head):]
for a, b in ((r"The bounded substitution by rail is the largest: at 50 kt a week the relief pass places its ceiling in nearly every profile week of both events (Table~\ref{tab:railweeks}; the cut bulk that finds a rail route is",
              r"The rule on rail moves the loss most (Section~S8). A ceiling of 50 kt a week is reached in nearly every profile week of both events (Table~\ref{tab:railweeks}; the cut bulk that finds a rail route is"),
             (r", delivers \ReliefBnFifty{} billion USD over the 2026 run and lowers the loss by", r"; rail then delivers \ReliefBnFifty{} billion USD over the 2026 run and lowers the loss by"),
             ("and the industrial integral falls to", "and the industrial shortfall falls to"),
             (r"The floor of the loading curve below 5\,cm, at half and twice its value, by \RevFloorLowRel{} and \RevFloorHighRel\,\%.",
              r"The loading share below 5\,cm, at half and twice its value, moves it by \RevFloorLowRel{} and \RevFloorHighRel\,\%."),
             ("Their anatomy: at 45 days", "At 45 days"),
             ("The relief of the rail sensitivity serves liquid bulk for", "Under the rail ceilings, rail serves liquid bulk for")):
    if reading.count(a) != 1:
        d.fails.append(f"reading paragraph: {a[:60]}")
    reading = reading.replace(a, b)
runs_par = d.get_line(r"\paragraph{The sensitivity runs.}")
key = "The model's specifications are those selected on the 2018 episode; alternative choices move the result further, in both directions:"
i = runs_par.find(key)
if i < 0:
    d.fails.append("the summary sentence of the sensitivity runs was not found")
summary = runs_par[i:].replace(r"(Fig.~\ref{fig:sensitivity}; Sections~S4 and S8)", r"(Fig.~\ref{fig:sensitivity})")

# ------------------------------------------------------------------ the new section
d.line(r"\paragraph{One-at-a-time sensitivities.}",
       r"\paragraph{Approach.} A sensitivity run changes one rule or parameter of the reference run and keeps everything else, the supplier--buyer network included. Table~\ref{tab:revision} lists these runs: the rule or parameter, its reference value, the alternatives tested, and the German loss that each gives for the 2026 season and, where it was run, for the 2018 event. Figure~\ref{fig:sensitivity} shows the same losses by type of uncertainty. Three sets of runs are of another kind. Ten further supplier--buyer networks, drawn with other seeds, sample the random component of the model (the rows on the supplier--buyer network). The levers of the main text are each run on every network, against the base of that network. And two experiments cross two changes (Section~S4): the levers under a rail ceiling, and the two waves at a shorter refill time.")
d.block("si_revision", "")
end = "% <<< generated table si_revision\n"
d.sub(end, end + "\n" + r"\paragraph{Reading the table.} " + reading + " " + summary + "\n\n"
      + r"\paragraph{What was not varied.} Four groups of parameters stay at their reference values in every run. The transport costs, values of time and transfer costs (Table~\ref{tab:rates}) are set on the freight statistics (Section~S2); changing them would change the baseline flows against which the event is measured. The input--output table, the location of the agents and the criticality of the inputs (Section~S1) are data, apart from the one criticality rating tested in the table. The inventory targets are documented industry by industry (Tables~\ref{tab:stocks} and~\ref{tab:stockoverrides}); only their overall level is varied. The thresholds of the modal-switch rule are examined on the classification of the shipments, outside full runs (Section~S4), and the Lower Rhine surcharge factor has no effect on the loss (Section~S3). The utilization rate of capacity and the pass-through of input costs into prices (Section~S10) were not varied either."
      + "\n")
d.line(r"Table~\ref{tab:runs}\todo{",
       r"\paragraph{The runs.} In all, the paper rests on \NRuns{} runs: \NRunsMain{} in the main list (the two reference runs, their variants, and the ten further networks of the 2018 event), \NRunsPaired{} lever runs on the ten further networks of 2026, \NRunsRev{} one-at-a-time sensitivities, \NRunsLadder{} inventory levels, \NRunsCross{} crossed runs, \NRunsNoRail{} runs without rail substitution and \NRunsAlt{} runs of the floor representation. The list of these runs, with the German loss, its peak, the loss of the 28 economies and the consumption loss of each, is the file \texttt{additional\_data/\allowbreak runs\_20261102.csv} of the study folder in the code repository, with the job lists (\texttt{cluster/\allowbreak jobs\_20261102\_*.txt}, \texttt{jobs\_20261103\_altriver.txt}, \texttt{jobs\_20261106\_inv075.txt}).")
d.line(r"\paragraph{The sensitivity runs.}", None)
d.remove_block("si_runs")
d.sub(r"and the rules tested in the revision (Table~\ref{tab:revision}): substitution by rail", r"and further rules of Table~\ref{tab:revision}: substitution by rail")
d.save()

m = Doc(ov / "main.tex")
m.sub(r"The paper is based on \NRuns{} runs; see Supplementary Table~\ref{tab:runs}.",
      r"The paper is based on \NRuns{} runs, listed in \texttt{additional\_data/\allowbreak runs\_20261102.csv} of the study folder (Supplementary Section~S7).")
m.save()
