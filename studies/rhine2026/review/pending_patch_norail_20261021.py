"""DEFERRED Overleaf patch (21 Oct 2026): the no-rail runs written into the manuscript.

The user asked on the evening of 20 Oct not to update the Overleaf copy while they revise it. Apply when they allow:

    git -C <overleaf> fetch && git -C <overleaf> pull --rebase origin main      # their edits first
    python studies/rhine2026/review/pending_patch_norail_20261021.py            # this file (asserts every anchor)
    python studies/rhine2026/make_numbers.py                                    # RevNoRail* macros into numbers.tex
    python studies/rhine2026/si_tables.py                                       # the two no-rail rows of Table S-revision
    cp studies/rhine2026/figures/F8_sensitivity.{pdf,png} <overleaf>/figures/   # the rail group: none, 50, 140 kt
    then lint, commit, fetch/rebase, push.

If an anchor fails, the user's revision changed that sentence: re-read it and carry the same content by hand.
Numbers (compare_runs_batch_jobs_20261020_norail.csv): 2026 no-rail 2.02 % of a quarter (+23 % on 1.64), peak 3.01 %/week in
week 17 (unchanged), EU 21.7 bn; 2018 1.29 % (+32 % on 0.98), peak week 21, EU 14.2 bn.
"""
from pathlib import Path

O = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


def patch(path: Path, pairs):
    s = path.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    for old, new in pairs:
        n = s.count(old); assert n == 1, f"{path.name}: {n} occurrences of {old[:90]!r}"
        s = s.replace(old, new)
    path.write_text(s.replace("\n", nl), encoding="utf-8"); print(f"{path.name}: {len(pairs)} replacements")


patch(O / "main.tex", [
    # Results, the capacity section: the placeholder todo
    ("Combined rail--barge transport of bulk cargo exists at the Rhine ports, but we have no data on its share of the Kaub traffic, so this is an assumption of the routing; a pair of runs in which no bulk may use rail at all bounds its effect \\todo{no-rail runs pending: jobs\\_20261020\\_norail.txt}.",
     "Combined rail--barge transport of bulk cargo exists at the Rhine ports, but we have no data on its share of the Kaub traffic, so this is an assumption of the routing, and a pair of runs in which no bulk may use rail at all bounds its weight: without it the 2026 loss is \\finalbatch{\\RevNoRail}\\,\\% of a quarter, \\finalbatch{\\RevNoRailAbs}\\,\\% more, and the 2018 loss \\RevNoRailyy\\,\\%, \\RevNoRailyyAbs\\,\\% more (Supplementary Table~\\ref{tab:revision})."),
    # (the uncertainty paragraph was rewritten by the author on 21 Oct; the rail rule is added there in the comments pass)
    # the caption of the uncertainty figure
    ("substitution by rail at 50 and 140 kt a week, the refill time",
     "substitution by rail (none for any bulk shipment; a ceiling of 50 and 140 kt a week for all of them), the refill time"),
    # Discussion, the limitations paragraph
    ("bulk may not switch, except for the shipments that already use rail for a main leg of their journey, an assumption without data behind it; and a weekly ceiling on rail for all bulk, tested as a sensitivity, removes a fifth to a half of the loss.",
     "bulk may not switch, except for the shipments that already use rail for a main leg of their journey, an assumption without data behind it that is worth a quarter of the loss (without it the 2026 loss is \\finalbatch{\\RevNoRailAbs}\\,\\% higher and the 2018 loss \\RevNoRailyyAbs\\,\\%); and a weekly ceiling on rail for all bulk, tested as a sensitivity, removes a fifth to a half of the loss."),
])

patch(O / "sections" / "si.tex", [
    # S8 Rail: the exception in the rule and the no-rail pair
    ("and bulk cannot switch at all, the representation of the fact that tank barges and ore trains have no road or rail equivalent at volume in the time of an event.",
     "and bulk cannot switch, the representation of the fact that tank barges and ore trains have no road or rail equivalent at volume in the time of an event, except for the shipments whose normal route already carries a main leg by rail (100\\,km or more), which may go around a stretch by rail at no penalty: 15\\,\\% of the bulk orders that cross Kaub have such a route, and the surcharge moves them off the river before the capacity limit cuts them. We have no data on the share of the Kaub traffic that travels combined rail--barge, so a pair of runs raises the main-leg threshold to 500\\,km, which leaves no bulk shipment a rail alternative: the 2026 loss rises from \\DEUlossQ{} to \\RevNoRail\\,\\% of a quarter (\\RevNoRailAbs\\,\\% more) and the 2018 loss from \\DEUlossQyy{} to \\RevNoRailyy\\,\\% (\\RevNoRailyyAbs\\,\\% more), with the same peak weeks (Table~\\ref{tab:revision})."),
])
print("deferred no-rail patch applied; now make_numbers, si_tables, copy F8, lint, commit, push")
