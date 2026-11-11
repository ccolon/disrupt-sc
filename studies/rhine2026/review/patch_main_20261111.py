r"""Main text, round of 11 November 2026: the author's answers to the open points of the SI revision of 10 November.
Applies what does not depend on the plan for the 2026 test:

  - the superscript that flagged the forecast numbers goes: the macro \finalbatch, its uses, the note under the abstract;
  - point 2: one modeling choice was made on the 2018 benchmark (Introduction, Results, Discussion, Methods);
  - point 5: the clause of the Discussion on the outlook of 7 September goes;
  - point 6: the pointer to the French chain of the SI goes;
  - point 10: one short statement on the use of AI tools, in the Methods; the separate section goes;
  - note N12 of the SI (table of rail weeks removed): the pointer to it goes.

Exact anchors (si_patchlib.Doc): a missing or repeated anchor stops the script before anything is written.
    python patch_main_20261111.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "main.tex")

# ---- the superscript -------------------------------------------------------------------------------------------------
pat = re.compile(r"\\finalbatch\{([^{}]*)\}")
uses = len(pat.findall(d.text))
if uses:
    d.text = pat.sub(lambda m: m.group(1), d.text)
    d.done += 1
    print(f"   {uses} uses of the superscript macro removed")
else:
    print("   already applied: no use of the superscript macro")
left = len(re.findall(r"\\finalbatch\{", d.text.replace(r"\newcommand{\finalbatch}", "")))
if left:
    d.fails.append(f"{left} uses of the superscript macro with nested braces are left")
d.line(r"\newcommand{\finalbatch}", None)
d.line(r"\noindent\small\textcolor{orange!80!black}{$^{\dagger}$}", r"\noindent\small \todo{...} marks an open point.\normalsize")

# ---- point 2: one choice made on the 2018 benchmark ----------------------------------------------------------------
d.sub("and three choices among a few candidates each (the representation of the river, the inventory level, the number of "
      "suppliers per input) were made on the 2018 low water (Methods)",
      "and one modeling choice, the representation of the river, was made on the 2018 low water (Methods)")
d.sub("the model's rules, selected on the 2018 episode, move it further in both directions",
      "the model's rules and parameters move it further in both directions")
d.sub("and three choices were made on the 2018 benchmark, which is itself a statistical estimate with a wide band.",
      "and one choice, the representation of the river, was made on the 2018 benchmark, which is itself a statistical "
      "estimate with a wide band.")
d.sub("is a parameter selected on the 2018 benchmark (Calibration, selection and validation).",
      "is a parameter, one in the reference runs; a run with two is reported as a sensitivity (Supplementary Section~S7).")
NEW_CHOICE = ("One modeling choice was made on the 2018 benchmark: the representation of the river, between two options "
              "(Supplementary Section~S9). The level of the inventories and the number of suppliers per input were also compared "
              "with the benchmark; both stay at their reference values, the balance-sheet level and one supplier per input, and "
              "the comparisons are reported as sensitivities (Supplementary Section~S7). The 2018 comparison as a whole is "
              "therefore an in-sample check of consistency, not a validation.")
m = re.findall(r"Three modeling choices were made on the 2018 benchmark:.*?is therefore an in-sample check of consistency, not a validation\.", d.text, re.S)
if len(m) == 1 and "\n" not in m[0]:
    d.text = d.text.replace(m[0], NEW_CHOICE)
    d.done += 1
elif NEW_CHOICE in d.text:
    print("   already applied: the Methods sentence on the choices")
else:
    d.fails.append(f"the Methods sentence on the three choices: {len(m)} match(es)")

# ---- point 5: the outlook of 7 September -----------------------------------------------------------------------------
d.sub(r"; the outlook of 7 September, on which the first version of this paper rested, missed the end-of-September episode "
      r"by 15 to 44\,cm (Supplementary Section~S3)", "")

# ---- point 6: the French chain ---------------------------------------------------------------------------------------
d.sub("and the food industry rations its clients (Supplementary Section~S6); the cost-based routing",
      "and the food industry rations its clients; the cost-based routing")

# ---- point 10: the use of AI tools, once, in the Methods ------------------------------------------------------------
d.line(r"\paragraph{Use of AI tools.}",
       r"\paragraph{Use of AI tools.} A large language model (Claude, Anthropic) was used to collect data, to write code, "
       r"including the scripts that draw the figures, and to draft the manuscript. The author directed and checked this work "
       r"and is responsible for the content.")
d.sub("\\section*{AI disclosure}\nAnthropic Fable 5.1 was used to collect data, write code, produce figures, and draft the manuscript.\n\n\n", "")

# ---- note N12 of the SI: the table of rail weeks is removed --------------------------------------------------------
d.sub(r" The ceiling is reached in nearly every week of both events (Supplementary Table~\ref{tab:railweeks}).",
      " The lower ceiling is reached in nearly every week of both events, the higher one in most.")

d.save()
