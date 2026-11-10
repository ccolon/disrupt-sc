r"""SI revision of 10 Nov 2026, section S10 (the author's notes N60-N61) and the renumbering that follows.

N60  'Weekly sequence and model specifications' is not a result: it moves up and becomes S4, after Scenario
     construction, as the note names it. The sections after it shift: Mechanism tests S4 -> S5, What crosses Kaub
     S5 -> S6. S7, S8 and S9 keep their numbers (the former S6 was merged into S9).
N61  The paragraph on the fleet lever joins the rail section, renamed 'S8 Rail and the low-water fleet'.
Every pointer to a section is updated in si.tex and in main.tex, one by one, to where its content now is: the
sensitivity runs that sat in the former S4 are in S7 (stress paths, headroom, floor of the loading curve), the
mechanism tests in S5, prices and chains in S6, the specifications in S4, the fleet lever in S8.
E50-E51: punctuation of the two paragraphs the author wrote in this section.

    python patch_si_20261110_s10.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")

# ------------------------------------------------------------------ take the last section apart
start = d.text.index("\\subsection*{S10 Weekly sequence and model specifications")
tail = d.text[start:].rstrip("\n")
d.text = d.text[:start].rstrip("\n") + "\n"
lines = tail.split("\n")
if not lines[0].startswith("\\subsection*{S10 Weekly sequence and model specifications\\todo{"):
    d.fails.append("the heading of S10 is not as expected")
fleet = [ln for ln in lines if ln.startswith("\\paragraph{The fleet lever.")]
if len(fleet) != 1:
    d.fails.append(f"{len(fleet)} fleet paragraphs")
body = [ln for ln in lines[1:] if not ln.startswith("\\paragraph{The fleet lever.")]
while body and body[-1].strip() == "":
    body.pop()
spec = "\\subsection*{S4 Weekly sequence and model specifications}\n" + "\n".join(body) + "\n\n"
head = "\\paragraph{The fleet lever.\\todo{this paragraph is misplaced, consider groupping that with \"S8 rail\"}} "
if fleet and not fleet[0].startswith(head):
    d.fails.append("the fleet paragraph does not start as expected")
fleet_par = "\\paragraph{The low-water fleet.} " + (fleet[0][len(head):] if fleet else "")
d.done += 1

# ------------------------------------------------------------------ new order and names
d.sub("\\subsection*{S4 Mechanism tests}\n", spec + "\\subsection*{S5 Mechanism tests}\n")
d.sub("\\subsection*{S5 What crosses Kaub, and at what price}\n", "\\subsection*{S6 What crosses Kaub, and at what price}\n")
d.sub("\\subsection*{S8 Rail}\n", "\\subsection*{S8 Rail and the low-water fleet}\n")
d.sub("\\subsection*{S9 Selecting the representation of the river on the 2018 low water}\n",
      fleet_par + "\n\n\\subsection*{S9 Selecting the representation of the river on the 2018 low water}\n")
d.sub(r"(0.10 to 78\,cm, 0.08 at 100, 0.03 at 120) is reported in Supplementary Table~\ref{tab:revision}.",
      r"(0.10 to 78\,cm, 0.08 at 100, 0.03 at 120) is reported in Table~\ref{tab:revision}.")

# ------------------------------------------------------------------ the two paragraphs of the specifications
d.sub(r"\paragraph{A few specifications} There are no lead times", r"\paragraph{A few specifications.} There are no lead times")
d.sub("An unfilled order is not carried over as such, next week's order is recomputed from the target and the gap it left, so an unfilled order raises the next.",
      "An unfilled order is not carried over as such: next week's order is recomputed from the target and the gap it left, so an unfilled order raises the next.")
d.sub(r"\paragraph{Stationarity, conservation, and time horizon} Undisrupted runs are stationary. Rejected shipments are conserved, a cut share returns",
      r"\paragraph{Stationarity, conservation, and time horizon.} Undisrupted runs are stationary. Rejected shipments are conserved: a cut share returns")

# ------------------------------------------------------------------ pointers of si.tex, one by one
for old, new in ((r"not as bounds (Section~S4)", r"not as bounds (Section~S7)"),
                 (r"tested at 0.04 and 0.16 (Section S4)", r"tested at 0.04 and 0.16 (Section S7)"),
                 (r"instead of 2 are tested in Section~S4.", r"instead of 2 are tested in Section~S7."),
                 (r"with the capacity limit alone; Section~S4)", r"with the capacity limit alone; Section~S5)"),
                 (r"two experiments cross two changes (Section~S4)", r"two experiments cross two changes (Section~S5)"),
                 (r"outside full runs (Section~S4)", r"outside full runs (Section~S5)"),
                 (r"the pass-through of input costs into prices (Section~S10)", r"the pass-through of input costs into prices (Section~S4)"),
                 (r"at volume during an event (Section~S4)", r"at volume during an event (Section~S5)")):
    d.sub(old, new)
d.save()

# ------------------------------------------------------------------ pointers of main.tex, one by one
m = Doc(ov / "main.tex")
for old, new in ((r"test both ways (Supplementary Sections~S4 and S8)", r"test both ways (Supplementary Sections~S7 and S8)"),
                 (r"relax and tighten the rule (Supplementary Section~S4)", r"relax and tighten the rule (Supplementary Section~S8)"),
                 (r"appears with any gap (Supplementary Section~S4)", r"appears with any gap (Supplementary Section~S5)"),
                 (r"Supplementary Sections~S4, S7 and S8)", r"Supplementary Sections~S7 and S8)"),
                 (r"surcharges of the worst weeks (Supplementary Section~S5)", r"surcharges of the worst weeks (Supplementary Section~S6)"),
                 (r"the chains that start there (Supplementary Section~S5)", r"the chains that start there (Supplementary Section~S6)"),
                 (r"(\finalbatch{\ShareShipping}\,\%) (Supplementary Section~S5)", r"(\finalbatch{\ShareShipping}\,\%) (Supplementary Section~S6)"),
                 (r"rations its clients (Supplementary Section~S5)", r"rations its clients (Supplementary Section~S6)"),
                 (r"of the ten further ones (Supplementary Section~S10)", r"of the ten further ones (Supplementary Section~S8)"),
                 (r"implementation conventions are in Supplementary Section~S10.", r"implementation conventions are in Supplementary Section~S4."),
                 (r"deliveries at Kaub are reported in Supplementary Section~S4", r"deliveries at Kaub are reported in Supplementary Section~S5"),
                 (r"an assumption relaxed in Supplementary Section~S4.", r"an assumption relaxed in Supplementary Sections~S5 and S8."),
                 (r"two stress paths (Supplementary Section~S4), not bounds", r"two stress paths (Supplementary Section~S7), not bounds"),
                 (r"backlog left at the end; Supplementary Section~S10)", r"backlog left at the end; Supplementary Section~S4)"),
                 (r"what the lever holds fixed are in Supplementary Section~S10.", r"what the lever holds fixed are in Supplementary Section~S8.")):
    m.sub(old, new)
m.save()
