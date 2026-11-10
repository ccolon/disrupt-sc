r"""SI revision of 10 Nov 2026, section S3 (the author's notes N25-N33 and the direct edits E24-E31).

N25      the profile built on the outlook of 7 September is no longer described and its table (tab:forecast) is removed;
         one sentence on that outlook's miss stays, because the Discussion cites it and it motivates the stress profiles
N26      'Under the profiles' -> 'Under the 2026 profile'
N27      the sources of the loading table named and cited in place of 'XXX'
N28      one name for the value: 'loading share' (not 'fleet value', not 'traffic rate'), in the text and in the table
N29 N30  loading table without the columns 'vessel' and 'nature'
N31      the capacity per cargo class written as a formula (the larger of two quantities, both named)
N32      the loading share applies to the Kaub reach alone; the other reaches keep their normal capacity: said
N33      the sentence on the Lower Rhine factor rewritten on what its source supports
Also in this paragraph: the forecast's history said that the reissue of 7 October gave the loss of the batch of this paper;
the batch of this paper is the rerun of 2 November (calibrated baseline, capacities per cargo class), which the text now says.

    python patch_si_20261110_s3.py [overleaf]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")

# ------------------------------------------------------------------ Gauges
d.line(r"\paragraph{Gauges.}",
       r"\paragraph{Gauges.} We built weekly means of the Kaub gauge from the PEGELONLINE record \citep{pegelonline2026} (raw 15-minute values) for 2026 and from the record of the Federal Institute of Hydrology for 2018. The 2026 profile (Table~\ref{tab:gate}) takes the observations to 29 September, the six-week outlook of the same institute of 28 September \citep{bfg2026} and an assumed recovery after it. Such an outlook can miss an episode: the one of 7 September had put the weeks of 14, 21 and 28 September at 12, 22 and 42\,cm; the observed means were 25, 7 and about $-2$ (the last from two observed days and the outlook of 28 September). Two stress profiles therefore take the outlook's 25th and 75th percentile for the forecast weeks and shift the assumed recovery by the last forecast week's offset (\texttt{2026\_q25.csv}, \texttt{2026\_q75.csv}); they are marginal quantiles week by week, not trajectories of the ensemble, and are run as two stress paths of the forecast, not as bounds (Section~S4). The forecast was first issued on 30 September 2026 on an earlier loading curve, at \ForecastSepQ\,\% of a quarter, and reissued on 7 October 2026 on the loading curve of Table~\ref{tab:loading}. The batch of this paper, run on 2 November 2026, keeps the hydrological information of 30 September and uses the baseline calibrated as in Section~S2 and one capacity per cargo class (Capacities, below); it gives \DEUlossQ\,\%. No production statistic of the event entered any of these versions. By the outcome publication dates, July 2026 (production index released on 7 September) is retrospective; August (released on 7 October and not used) is a nowcast; September to December is prospective, the first release for September having come on 6 November 2026, after the last version. The manifest of these versions (profile files, loading curves, code commits, run lists, issue dates) is \texttt{studies/rhine2026/forecast\_manifest.md} in the code repository.")
d.sub(r"\paragraph{Monthly loading shares.} Under the profiles\todo{which profile?} the Kaub reach passes on average",
      r"\paragraph{Monthly loading shares.} Under the 2026 profile, the Kaub reach passes on average")

# ------------------------------------------------------------------ Loading table: paragraph and table
d.line(r"\paragraph{Loading table.}",
       r"\paragraph{Loading table.} Table~\ref{tab:loading} describes how the loading curve is built. We gathered evidence from operators' surcharge tables and notices \citep{contargo2026}, the weekly tonnage count of the Dutch inland navigation association \citep{schuttevaer2026}, reports on the payloads of single vessels \citep{wiwo2026,ifw2026} and the literature on the low water of 2018 \citep{vandorsser2020,ademmer2023}, to link gauge values to the share of the normal tonnage that the Kaub reach can pass, the loading share. The model interpolates linearly between those values and stays at 0.08 below 5\,cm. The evidence measures different quantities: single-vessel payloads, a weekly count, operators' thresholds. The resulting loading share is the authors' reading of them.")
inner = d.block("si_loading_table")
rows = []
for ln in inner.split("\n"):
    t = ln.strip()
    if t[:1].isdigit() and t.endswith("\\\\"):          # cm & share & vessel & nature & source & measures & treatment
        cells = [c.strip() for c in re.split(r"(?<!\\)&", t[:-2])]
        if len(cells) == 7:
            ln = " & ".join([cells[0], cells[1], cells[4], cells[5], cells[6]]) + " \\\\"
        elif len(cells) != 5:
            d.fails.append(f"loading table row with {len(cells)} cells: {t[:60]}")
    rows.append(ln)
inner = "\n".join(rows)
for old, new, n in [
    (r"\begin{longtable}{rrrL{18mm}L{33mm}L{29mm}L{36mm}}", r"\begin{longtable}{rL{11mm}L{45mm}L{40mm}L{42mm}}", 1),
    ("cm & traffic rate & vessel \\todo{I would remove this columns}& nature\\todo{also remove this columns, info is in \"treatment\" already} & source & measures & treatment \\\\",
     "cm & loading share & source & measures & treatment \\\\", 1),
    ("cm & fleet & vessel & nature & source & measures & transformation \\\\", "cm & loading share & source & measures & treatment \\\\", 1),
    (" gives the fleet value", " gives the loading share", 4),
    ("vessel share ", "a single-vessel load of ", 3),
    ("do not bound the fleet value", "do not bound the loading share", 1),
    (" (the earlier version of the table took 0.12 here and attributed the count to the 25 cm row; rebuilt 6 Oct 2026)", "", 1),
    ("the count of the week at 23 -> 6 cm (0.22, next row)", "the count of the week in which the gauge fell from 23 to 6 cm (0.22, next row)", 1),
    ("(WirtschaftsWoche 18 Aug 2026); Kaub 5-6 cm on 14-17 Aug 2026 (PEGELONLINE)", r"(WirtschaftsWoche 18 Aug 2026~\citep{wiwo2026}); Kaub 5--6 cm on 14--17 Aug 2026 (PEGELONLINE~\citep{pegelonline2026})", 1),
    ("via Schuttevaer, 14 Aug 2026:", r"via Schuttevaer, 14 Aug 2026~\citep{schuttevaer2026}:", 1),
    ("Kiel Institute statement of 28 Jul 2026 (press):", r"Kiel Institute statement of 28 Jul 2026~\citep{ifw2026}:", 1),
    ("van Dorsser et al. (2020):", r"van Dorsser et al.~\citep{vandorsser2020}:", 1),
    ("Contargo surcharge notice, Aug 2026:", r"Contargo surcharge notice, Aug 2026~\citep{contargo2026}:", 1),
    ("Ademmer et al. (2023):", r"Ademmer et al.~\citep{ademmer2023}:", 1),
]:
    c = inner.count(old)
    if c != n:
        d.fails.append(f"loading table: found {c} (expected {n}): {old[:70]!r}")
    inner = inner.replace(old, new)
d.block("si_loading_table", inner)
d.remove_block("si_forecast")

# ------------------------------------------------------------------ Capacities, rerouting, surcharge
d.line(r"\paragraph{Capacities.}",
       r"\paragraph{Capacities.} Every Rhine reach $r$ has a normal capacity for each cargo class $c$, since container vessels, dry-bulk vessels and tank barges are three fleets: $K_{r,c}=\max\!\big(s_{r,c}\,T_r,\;1.02\,F_{r,c}\big)$, where $F_{r,c}$ is the model's baseline flow of the class on the reach, $s_{r,c}=F_{r,c}/\sum_{c'}F_{r,c'}$ its share of the reach's traffic, and $T_r$ the tonnage of the reach in the CCNR cross-section counts \citep{ccnr2023}. The capacity of a class is therefore its share of the counted tonnage where the counts exceed the model's flow, and the model's own flow plus 2\,\% elsewhere, so that the constraint is inert at full loading. At Kaub this gives 175,900 t a day in total, against 137,000 in the counts: 32,400 for the container vessels, 62,900 for the dry-bulk vessels and 80,600 for the tank barges. Each week, the capacity of the Kaub reach for a class is its normal capacity times the loading share. Headrooms of 10 and 25\,\% instead of 2 are tested in Section~S4.")
d.line(r"\paragraph{Rerouting around a saturated reach.}",
       r"\paragraph{Rerouting around a saturated reach.} After every agent has delivered, each reach compares its load with its capacity. If the load exceeds the capacity, the shipments are cut in proportion, so that the reach is exactly full. A saturated reach is then excluded for the rest of the week, and each cut share looks for a route on the remaining network. The procedure is repeated until no reach is over its capacity; it does not depend on the order of the deliveries. A cut share that finds no acceptable route returns to its supplier's inventory. In the reference run, \GateResentMin{} to \GateResentMax\,\% of the tonnage cut at Kaub finds another route (Table~\ref{tab:gate}). Containers always find a rail or road alternative; only bulk is withheld (Table~\ref{tab:channels}). The loading share applies to the Kaub reach alone: the other reaches keep their normal capacity all year. During the low-water weeks only Kaub saturates. In the recovery weeks the catch-up traffic, which is above the baseline, also exceeds the normal capacity of several other reaches, which delays part of the backlog and of the refill of inventories.")
d.line(r"\paragraph{Surcharge.}",
       r"\paragraph{Surcharge.} The week's multiplier $1/\text{loading share}$, capped at 20, is applied on every reach from Koblenz upstream, and one third of its excess over 1 on the Lower Rhine reaches. This factor of one third is an assumption: operators set the low-water surcharge by gauge \citep{contargo2026}, and the Lower Rhine, with its own gauges, is less restricted than the reach through Kaub. It has a negligible effect on the results: runs with a factor of zero and of one gave the same loss.")
d.save()
