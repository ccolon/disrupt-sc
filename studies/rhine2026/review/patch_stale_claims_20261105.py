r"""Draft of 5 Nov 2026: the stale verbal claims that paper_gate.py found on Overleaf 991f01c (43 claims in 30 sentences,
against the numbers of the batch of 2 November) and the duplicate PDF anchors of the SI counter reset.

Each edit changes the words to what the current macro says, or (SI S8, main l. 182) puts the macros themselves in the
text; the gate ledger is updated in the same run: the old claim entries are dropped and the new words are bound to
their macros with the range they are true for, so the next batch that moves a macro fails the gate again. One edit is
substantive, not wording: l. 87 said the loading-curve variants bracket the benchmark's central value; both lie below
it (as the Discussion, l. 174, already says).

Dry run by default (prints every change); --apply writes the manuscript and the ledger; --repo / --ledger point at
copies for a verification run; --markdown writes the review table.

    python studies/rhine2026/review/patch_stale_claims_20261105.py [--repo <overleaf>] [--ledger <folder>] [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
LEDGER = HERE.parent / "paper_gate_ledger"

# (file, old, new, the number behind it and why)
EDITS = [
    ("main.tex", r"nearly three times the industrial loss alone",
     r"more than two and a half times the industrial loss alone",
     "abstract: German loss over its industrial part = 2.6 (RatioBase; 100/IndustryShare = 2.63)"),
    ("main.tex", r"leave out an economy-wide loss nearly three times larger",
     r"leave out an economy-wide loss two and a half times larger",
     "2018: 100/IndustryShareyy = 2.44 (2026: 2.6)"),
    ("main.tex", r"while doubling inventories reduces the loss by almost two thirds",
     r"while doubling inventories reduces the loss by almost three quarters",
     "2018 loss with inventories x2: 1 - LadderD/DEUlossQyy = 73 %"),
    ("main.tex", r"spread evenly would cost a quarter less, and the two low-water episodes of 2026 cost an eighth more in sequence than apart, an interaction that four weeks of normal water in between, or a faster refilling of inventories, would remove",
     r"spread evenly would cost two fifths less, and the two low-water episodes of 2026 cost a sixth more in sequence than apart, an interaction that four weeks of normal water in between, or a faster refilling of inventories, would largely remove",
     "flat profile 1 - FlatQ/DEUlossQ = 41 %; interaction WaveInterShare = 16 %; left after a 4-week gap 5 %, with a 15-day refill 1 %"),
    ("main.tex", r"and a fleet built for low water a sixth; what the railway can take on at short notice removes a fifth to a half",
     r"and a fleet built for low water a fifth; what the railway can take on at short notice removes a quarter to more than a half",
     "fleet LevFleetAvg = 21 %; rail 50 / 140 kt RevRailFiftyAbs = 25 %, RevRailHundredFortyAbs = 57 %"),
    ("main.tex", r"and its variants with the shortfall raised and lowered by 15\,\% bracket the benchmark's central value",
     r"and its variants with the shortfall raised and lowered by 15\,\% give \TableLowInt{} and \TableHighInt{} percent-months, both below the benchmark's central value, the larger shortfall just short of its one-standard-deviation band",
     "SUBSTANTIVE: TableLowInt 3.4 and TableHighInt 1.1 are both below RecordInt 5.3; 3.4 is just below RecordIntLow 3.6 (as l. 174 says)"),
    ("main.tex", r"a loss that builds from July and doubles in the autumn",
     r"a loss that builds from July and more than doubles in the autumn",
     "heading: AutumnWaveQ/AugWaveQ = 0.71/0.30 = 2.4"),
    ("main.tex", r"costs \finalbatch{\AutumnWaveQ}\,\%, twice as much",
     r"costs \finalbatch{\AutumnWaveQ}\,\%, more than twice as much",
     "AutumnWaveQ/AugWaveQ = 2.4"),
    ("main.tex", r"about a quarter less than the season as it happened",
     r"about two fifths less than the season as it happened",
     "1 - FlatQ/DEUlossQ = 41 % (the season costs 70 % more than the flat profile, TroughPremium)"),
    ("main.tex", r"the loading curve by about a quarter up or down, two suppliers per input down by more than a half, no pooling up fourfold, no rail bypass for bulk up by a quarter",
     r"the loading curve by about a half up or down, two suppliers per input down by nearly a half, no pooling up threefold, no rail bypass for bulk up by three fifths",
     "loading curve +52 / -45 %; two suppliers -45 %; no pooling x3.06; no rail bypass +61 % (RevNoRailAbs)"),
    ("main.tex", r"are only a fifth of the deliveries that German buyers miss over the event; the other four fifths are rationing along the chains",
     r"are less than a third of the deliveries that German buyers miss over the event; the rest is rationing along the chains",
     "TransportWithheldShare = 29 % (the parenthesis keeps the macro)"),
    ("main.tex", r"doubling them for every buyer divides the 2018 loss by almost three",
     r"doubling them for every buyer divides the 2018 loss by more than three",
     "DEUlossQyy/LadderD = 0.52/0.14 = 3.7"),
    ("main.tex", r"doubling them divides the 2018 loss by almost three",
     r"doubling them divides the 2018 loss by more than three",
     "Discussion: the same 3.7"),
    ("main.tex", r"Goods producers and construction work off a fifth of their backlog",
     r"Goods producers and construction work off nearly a quarter of their backlog",
     "(100 - NetShare)/(100 - PerishableShare) = 9/38 = 24 % (23 % unrounded)"),
    ("main.tex", r"it predicts an economy-wide loss nearly three times larger",
     r"it predicts an economy-wide loss two and a half times larger",
     "2018: 100/IndustryShareyy = 2.44"),
    ("main.tex", r"and one in twenty-five below half of it",
     r"and one in fifty below half of it",
     "CorridorStopRhineAug = 1.9 %"),
    ("main.tex", r"and the second costs a fifth more than it would have alone",
     r"and the second costs a quarter more than it would have alone",
     "WaveBafterAQ/WaveBQ = 0.75/0.60 = 1.25 (WaveBratio)"),
    ("main.tex", r"spread evenly over the season costs a quarter less",
     r"spread evenly over the season costs two fifths less",
     "1 - FlatQ/DEUlossQ = 41 %"),
    ("main.tex", r"to the construction sites, a fifth",
     r"to the construction sites, a sixth",
     "ShareConstruction + ShareCement = 13 + 3 = 16 %"),
    ("main.tex", r"make up a fifth of their backlog once the river reopens",
     r"make up nearly a quarter of their backlog once the river reopens",
     "24 % (23 % unrounded), as l. 136"),
    ("main.tex", r"divides the loss by four compared with a model that keys every input to its region",
     r"divides the loss by three compared with a model that keys every input to its region",
     "NoPoolQ/DEUlossQ = 3.4/1.11 = 3.06"),
    ("main.tex", r"A fleet built for low water removes a sixth of the loss",
     r"A fleet built for low water removes a fifth of the loss",
     "LevFleetAvg = 21 %"),
    ("main.tex", r"and a fifth with its gain extended to 100\,cm",
     r"and a quarter with its gain extended to 100\,cm",
     "RevFleetWideRemoves = 26 %"),
    ("main.tex", r"and the three together four fifths",
     r"and the three together more than four fifths",
     "LevPackageAvg = 84 %"),
    ("main.tex", r"they remove a fifth of the loss, at the scale of the rail response of past low waters a half",
     r"they remove a quarter of the loss, at the scale of the rail response of past low waters more than a half",
     "RevRailFiftyAbs = 25 %, RevRailHundredFortyAbs = 57 %"),
    ("main.tex", r"an assumption without data behind it that is worth a quarter of the loss (without it",
     r"an assumption without data behind it that weighs heavily on the result (without it",
     "the old fraction had no single reading: the bypass lowers the no-rail loss by 38 %, removing it raises the base by 61 % (2018: 124 %); the parenthesis already gives both macros"),
    ("main.tex", r"removes a fifth to a half of the loss",
     r"removes a quarter to more than a half of the loss",
     "RevRailFiftyAbs = 25 %, RevRailHundredFortyAbs = 57 %"),
    ("sections/si.tex", r"It removes a fifth and a half of the 2026 loss and a quarter and three fifths of the 2018 loss",
     r"It removes \RevRailFiftyAbs{} and \RevRailHundredFortyAbs\,\% of the 2026 loss and \RevRailFiftyyyAbs{} and \RevRailHundredFortyyyAbs\,\% of the 2018 loss",
     "SI S8: four fractions, all stale (25 / 57 / 29 / 67 %): the macros themselves, as the SI does elsewhere"),
    ("sections/si.tex", r"the restrictive end of a range whose other end halves the loss",
     r"the restrictive end of a range whose other end removes more than half of the loss",
     "RevRailHundredFortyAbs = 57 % (2018: 67 %)"),
    ("main.tex", r"\setcounter{figure}{0}\renewcommand{\thefigure}{S\arabic{figure}}\renewcommand{\thefigure}{S\arabic{figure}}",
     r"\setcounter{figure}{0}\renewcommand{\thefigure}{S\arabic{figure}}\renewcommand{\theHfigure}{S\arabic{figure}}",
     "anchors: \\thefigure was set twice; the second is \\theHfigure, so hyperref names the SI figures figure.S1... (no clash with Fig. 1-4)"),
    ("main.tex", r"\setcounter{table}{0}\renewcommand{\thetable}{S\arabic{table}}",
     r"\setcounter{table}{0}\renewcommand{\thetable}{S\arabic{table}}\renewcommand{\theHtable}{S\arabic{table}}",
     "anchors: the same for the tables (table.1)"),
]

# the claim entries whose words change (all entries with that text are dropped; 43 in all)
DROP = {
    "main.yaml": [
        "nearly three times the industrial loss alone",
        "leave out an economy-wide loss nearly three times larger",
        "while doubling inventories reduces the loss by almost two thirds",
        "the same total shortfall of river capacity spread evenly would cost a quarter less",
        "the two low-water episodes of 2026 cost an eighth more in sequence than apart",
        "an interaction that four weeks of normal water in between",
        "and a fleet built for low water a sixth",
        "what the railway can take on at short notice removes a fifth to a half",
        r"its variants with the shortfall raised and lowered by 15\,\% bracket the benchmark's central value",
        "a loss that builds from July and doubles in the autumn",
        r"costs \finalbatch{\AutumnWaveQ}\,\%, twice as much",
        "about a quarter less than the season as it happened",
        "the loading curve by about a quarter up or down",
        "two suppliers per input down by more than a half",
        "no pooling up fourfold, no rail bypass for bulk",
        "no rail bypass for bulk up by a quarter",
        "The deliveries withheld at the river are only a fifth of the deliveries",
        "the other four fifths are rationing along the chains",
        "doubling them for every buyer divides the 2018 loss by almost three",
        "Goods producers and construction work off a fifth of their backlog by the end of the run",
        "doubling them divides the 2018 loss by almost three",
        "it predicts an economy-wide loss nearly three times larger",
        "one in twenty-five below half of it",
        "and the second costs a fifth more than it would have alone",
        "spread evenly over the season costs a quarter less",
        "to the construction sites, a fifth",
        "the plants that stop make up a fifth of their backlog once the river reopens",
        "divides the loss by four compared with a model that keys every input to its region",
        "A fleet built for low water removes a sixth of the loss",
        r"and a fifth with its gain extended to 100\,cm",
        "and the three together four fifths",
        "at the tonnage the operator offered in August 2026 they remove a fifth of the loss",
        "at the scale of the rail response of past low waters a half",
        "an assumption without data behind it that is worth a quarter of the loss",
        "removes a fifth to a half of the loss",
    ],
    "si_b.yaml": [
        "for the rest. It removes a fifth",
        "and a half of the 2026 loss and a",
        "the 2026 loss and a quarter and",
        "three fifths of the 2018 loss",
        "the restrictive end of a range whose other end halves the loss",
    ],
}
N_DROPPED = 43

M, S = "main.tex", "sections/si.tex"
WHY = "5 Nov 2026 rewrite (patch_stale_claims_20261105.py); "
ADD = {
    "main.yaml": [
        (M, "more than two and a half times the industrial loss alone", "RatioBase", [2.5, 2.8], "result: 2026 German loss over its industrial part; more than two and a half times = 2.5-2.8"),
        (M, "leave out an economy-wide loss two and a half times larger", "100/IndustryShareyy", [2.3, 2.7], "result: 2018 loss over its industrial part (2026: RatioBase 2.6); two and a half times = 2.3-2.7"),
        (M, "leave out an economy-wide loss two and a half times larger", "RatioBase", [2.3, 2.7], "result: the 2026 ratio, which the same sentence predicts; 2.3-2.7"),
        (M, "while doubling inventories reduces the loss by almost three quarters", "100*(1-LadderD/DEUlossQyy)", [66, 75], "result: % of the 2018 loss removed by inventories x2; almost three quarters = 66-75"),
        (M, "spread evenly would cost two fifths less", "100*(1-FlatQ/DEUlossQ)", [36, 44], "result: flat profile vs the season; two fifths = 36-44"),
        (M, "cost a sixth more in sequence than apart", "WaveInterShare", [15, 18.5], "result: interaction without a gap, % of the sum; a sixth = 15-18.5"),
        (M, "or a faster refilling of inventories, would largely remove", "max(WaveInterFour, WaveInterRest)/WaveInterShare", [-0.5, 0.4], "result: share of the interaction left with a 4-week gap or a 15-day refill; largely remove = at most 40 % left"),
        (M, "and a fleet built for low water a fifth", "LevFleetAvg", [17, 23], "result: fleet lever, mean of the eleven networks; a fifth = 17-23"),
        (M, "what the railway can take on at short notice removes a quarter to more than a half", "RevRailFiftyAbs", [22, 28], "result: rail 50 kt (lower end); a quarter = 22-28"),
        (M, "what the railway can take on at short notice removes a quarter to more than a half", "RevRailHundredFortyAbs", [50.5, 75], "result: rail 140 kt (upper end); more than a half = 50.5-75"),
        (M, "both below the benchmark's central value", "RecordInt - TableLowInt", [0.01, 100], "result: the larger of the two loading-curve variants (TableLowInt) is below the record's centre"),
        (M, "the larger shortfall just short of its one-standard-deviation band", "RecordIntLow - TableLowInt", [0.01, 0.6], "result: the +15 % shortfall variant lies just below the 16th percentile (just short = within 0.6 percent-months)"),
        (M, "a loss that builds from July and more than doubles in the autumn", "AutumnWaveQ/AugWaveQ", [2.0, 2.8], "result: autumn episode over August episode; more than doubles = 2.0-2.8"),
        (M, r"costs \finalbatch{\AutumnWaveQ}\,\%, more than twice as much", "AutumnWaveQ/AugWaveQ", [2.0, 2.8], "result: autumn over August; more than twice = 2.0-2.8"),
        (M, "about two fifths less than the season as it happened", "100*(1-FlatQ/DEUlossQ)", [35, 45], "result: flat profile vs the season; about two fifths = 35-45"),
        (M, "the loading curve by about a half up or down", "100*(TableLowQ/DEUlossQ-1)", [40, 60], "result: 2026 loss with the shortfall +15 %; about a half = 40-60"),
        (M, "the loading curve by about a half up or down", "100*(1-TableHighQ/DEUlossQ)", [40, 60], "result: 2026 loss with the shortfall -15 %; about a half = 40-60"),
        (M, "two suppliers per input down by nearly a half", "100*(1-SupTwoQ/DEUlossQ)", [44, 50], "result: two suppliers per input; nearly a half = 44-50"),
        (M, "no pooling up threefold", "NoPoolQ/DEUlossQ", [2.7, 3.3], "result: no pooling over the base; threefold = 2.7-3.3"),
        (M, "no rail bypass for bulk up by three fifths", "RevNoRailAbs", [56, 64], "result: % rise without the rail bypass; three fifths = 56-64"),
        (M, "are less than a third of the deliveries that German buyers miss", "TransportWithheldShare", [25, 33.3], "result: % of the German delivery shortfall withheld at the river; less than a third = 25-33.3"),
        (M, "doubling them for every buyer divides the 2018 loss by more than three", "DEUlossQyy/LadderD", [3.05, 4.5], "result: 2018 loss over the loss with inventories x2; more than three = 3.05-4.5"),
        (M, "doubling them divides the 2018 loss by more than three", "DEUlossQyy/LadderD", [3.05, 4.5], "result: the same, Discussion"),
        (M, "Goods producers and construction work off nearly a quarter of their backlog", "100*(100-NetShare)/(100-PerishableShare)", [20.5, 25], "result: backlog worked off by the catch-up sectors; nearly a quarter = 20.5-25"),
        (M, "it predicts an economy-wide loss two and a half times larger", "100/IndustryShareyy", [2.3, 2.7], "result: 2018 loss over its industrial part; 2.3-2.7"),
        (M, "and one in fifty below half of it", "CorridorStopRhineAug", [1.6, 2.4], "result: % of the corridor firms below half of baseline in week 7; one in fifty = 1.6-2.4"),
        (M, "and the second costs a quarter more than it would have alone", "100*(WaveBafterAQ/WaveBQ-1)", [22, 28], "result: second episode after the first vs alone; a quarter = 22-28"),
        (M, "spread evenly over the season costs two fifths less", "100*(1-FlatQ/DEUlossQ)", [36, 44], "result: flat profile vs the season; two fifths = 36-44"),
        (M, "to the construction sites, a sixth", "ShareConstruction+ShareCement", [15, 18.5], "result: building-materials chain, % of the German gross loss; a sixth = 15-18.5"),
        (M, "make up nearly a quarter of their backlog once the river reopens", "100*(100-NetShare)/(100-PerishableShare)", [20.5, 25], "result: backlog worked off; nearly a quarter = 20.5-25"),
        (M, "divides the loss by three compared with a model that keys every input to its region", "NoPoolQ/DEUlossQ", [2.7, 3.3], "result: no pooling over the base; by three = 2.7-3.3"),
        (M, "A fleet built for low water removes a fifth of the loss", "LevFleetAvg", [17, 23], "result: fleet lever, mean of the eleven networks; a fifth = 17-23"),
        (M, r"and a quarter with its gain extended to 100\,cm", "RevFleetWideRemoves", [22, 28], "result: fleetwide variant; a quarter = 22-28 (100 cm = design)"),
        (M, "and the three together more than four fifths", "LevPackageAvg", [80.5, 90], "result: package, mean of the eleven networks; more than four fifths = 80.5-90"),
        (M, "they remove a quarter of the loss, at the scale of the rail response", "RevRailFiftyAbs", [22, 28], "result: rail 50 kt; a quarter = 22-28"),
        (M, "of past low waters more than a half", "RevRailHundredFortyAbs", [50.5, 75], "result: rail 140 kt; more than a half = 50.5-75"),
        (M, "removes a quarter to more than a half of the loss", "RevRailFiftyAbs", [22, 28], "result: rail 50 kt (lower end); a quarter = 22-28"),
        (M, "removes a quarter to more than a half of the loss", "RevRailHundredFortyAbs", [50.5, 75], "result: rail 140 kt (upper end); more than a half = 50.5-75"),
    ],
    "si_b.yaml": [
        (S, "the restrictive end of a range whose other end removes more than half of the loss", "min(RevRailHundredFortyAbs, RevRailHundredFortyyyAbs)", [50.5, 100], "result: the 140 kt ceiling removes more than half of the 2026 and the 2018 loss"),
    ],
}
ALLOW = {
    "main.yaml": [
        (M, r"its variants with the shortfall raised and lowered by 15\,\% give", "design: loading-curve variants with the shortfall +-15 % (tablelow / tablehigh)"),
        (M, "and the two low-water episodes of 2026 cost", "count: the two episodes of the 2026 season (August, September-October)"),
        (M, "an interaction that four weeks of normal water in between", "design: the gap of four weeks of the wave-isolation runs (wave_<tag>_AB_gap4)"),
    ],
}


def q(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def drop_claims(text: str, snippets) -> tuple[str, int]:
    """Remove every claim entry ('  - file:' + '    text: <snippet>' + its indented lines) whose text is one of snippets."""
    lines, out, i, n = text.split("\n"), [], 0, 0
    targets = {f"    text: {q(s)}" for s in snippets}
    while i < len(lines):
        if lines[i].startswith("  - file:") and i + 1 < len(lines) and lines[i + 1] in targets:
            j = i + 2
            while j < len(lines) and lines[j].startswith("    "):
                j += 1
            n += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), n


def insert_before(text: str, marker: str, block: str) -> str:
    k = text.index(f"\n{marker}\n")
    return text[:k + 1] + block + text[k + 1:]


def main(repo: Path, ledger: Path, apply: bool, markdown: Path | None):
    docs = {f: (repo / f).read_text(encoding="utf-8") for f in {e[0] for e in EDITS}}
    rows = ["| file | old | new | number behind it |", "|---|---|---|---|"]
    for f, old, new, why in EDITS:
        n = docs[f].count(old)
        if n != 1:
            sys.exit(f"{f}: expected the old text once, found {n}: {old[:80]!r}")
        docs[f] = docs[f].replace(old, new)
        print(f"{f}\n  - {old}\n  + {new}\n    ({why})")
        rows.append(f"| {f} | {old.replace('|', '/')} | {new.replace('|', '/')} | {why.replace('|', '/')} |")
    led = {f: (ledger / f).read_text(encoding="utf-8") for f in set(DROP) | set(ADD) | set(ALLOW)}
    total = 0
    for f, snippets in DROP.items():
        led[f], n = drop_claims(led[f], snippets)
        total += n
    if total != N_DROPPED:
        sys.exit(f"dropped {total} claim entries, expected {N_DROPPED}")
    for f, entries in ADD.items():
        block = f"  # {WHY}words matched to the batch of 2 Nov\n" + "".join(
            f"  - file: {fi}\n    text: {q(t)}\n    expr: {q(e)}\n    range: [{lo}, {hi}]\n    why: {q(w)}\n"
            for fi, t, e, (lo, hi), w in entries)
        led[f] = insert_before(led[f], "pending:", block)
    for f, entries in ALLOW.items():
        block = "".join(f"  - file: {fi}\n    text: {q(t)}\n    why: {q(WHY + w)}\n" for fi, t, w in entries)
        led[f] = insert_before(led[f], "claims:", block)
    print(f"\n{len(EDITS)} edits; ledger: {total} claim entries dropped, {sum(len(v) for v in ADD.values())} added, "
          f"{sum(len(v) for v in ALLOW.values())} allowed added")
    if markdown:
        head = ["# Draft of 5 Nov 2026: the stale verbal claims and the PDF anchors (for the author's approval)", "",
                "Generated by `patch_stale_claims_20261105.py` (dry run): every edit the script would make to the Overleaf copy, "
                "with the number behind it (values of numbers.tex, batch of 2 Nov). Verified on a copy: the gate's ledger, bare "
                "and words checks pass after the patch, the compile no longer reports duplicate anchors, and the edited "
                "sentences read as intended in the PDF. The 117 pending items (model outputs written as literals) are not "
                "part of this draft.", ""]
        markdown.write_text("\n".join(head + rows) + "\n", encoding="utf-8")
    if apply:
        for f, t in docs.items():
            (repo / f).write_text(t, encoding="utf-8")
        for f, t in led.items():
            (ledger / f).write_text(t, encoding="utf-8")
        print(f"written: {', '.join(docs)} in {repo}; {', '.join(led)} in {ledger}")
    else:
        print("dry run: nothing written (--apply to write)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--markdown", default=None)
    a = ap.parse_args()
    main(Path(a.repo), Path(a.ledger), a.apply, Path(a.markdown) if a.markdown else None)
