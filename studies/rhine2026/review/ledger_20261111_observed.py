r"""Ledger of paper_gate.py after the batch of 11 November 2026 (the 2026 runs on the river as observed): entries for the
sentences written by patch_20261111_observed.py, patch_si_20261111_searate_row.py and patch_20261111_results.py, then
the entries whose sentence left the manuscript are dropped and appended to ledger_dropped_20261111.txt. Running it
again changes nothing.

    python studies/rhine2026/review/ledger_20261111_observed.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402
from si_patchlib import OVERLEAF, Doc  # noqa: E402

MAIN, SI = "main.tex", "si.tex"

# ---- one more wording in the Discussion, with the others of patch_20261111_results.py: the fleet removes 23 %
d = Doc(OVERLEAF / MAIN)
d.sub("the same week held by the barge-dependent buyers alone a quarter, a fleet built for low water a fifth (a quarter with its gain "
      "extended to 100\\,cm)",
      "the same week held by the barge-dependent buyers alone a quarter, a fleet built for low water more than a fifth (a quarter with "
      "its gain extended to 100\\,cm)")
d.save()

L = Ledger()
PROFILE = "scenarios/2026.csv (built 11 Nov 2026 by fetch_kaub.py; cluster/batch_20261111.md)"

# ---- the river as observed: Results and Methods of the main text, S3 of the SI
L.allow(MAIN, r"the weekly mean was 2\,cm in the week of 28 September, and the daily mean $-5$\,cm on 1 October",
        f"data: {PROFILE}, week of 28 September 1.8 cm; scenarios/kaub_daily_2026.csv, 1 October -4.8 cm")
L.allow(MAIN, r"It stayed below 25\,cm until late October, rose to 45\,cm in the week of 26 October and fell back to 18\,cm in the first "
              r"week of November",
        f"data: {PROFILE}, weeks of 5, 12 and 19 October 5.8, 13.5 and 21.0 cm; 26 October 45.3; 2 November 18.0")
L.allow(MAIN, r"which have the river above 130\,cm from 16 November",
        f"data: {PROFILE}, weeks of 16 and 23 November 133.3 and 134.0 cm (BfG 14-day forecast of 11 November, six-week outlook of 9 November)")
L.allow(MAIN, r"(23 weeks from 22 June, followed by 20 weeks of recovery)",
        f"design: {PROFILE} has 23 weeks; run_rhine.py --recovery-weeks 20 (43 weeks in all)")
L.allow(MAIN, r"for the 20 weeks from 22 June to 8 November 2026", f"data: {PROFILE}, 20 rows with status observed")
L.allow(MAIN, r"the daily medians of the 14-day forecast of 11 November",
        "source: BfG 14-day forecast of Kaub, issue of 11 November 2026 (scenarios/bfg_14day_kaub_20261111.csv)")
L.allow(MAIN, r"These forecasts have the river above 130\,cm from 16 November",
        f"data: {PROFILE}, weeks of 16 and 23 November 133.3 and 134.0 cm")
L.allow(SI, r"is observed for its first 20 weeks, to 8 November", f"data: {PROFILE}, 20 rows with status observed")
L.allow(SI, r"the daily medians of the institute's 14-day forecast of 11 November",
        "source: BfG 14-day forecast of Kaub, issue of 11 November 2026 (scenarios/bfg_14day_kaub_20261111.csv)")
L.allow(MAIN, r"ten weeks below 50\,cm from 7 September, eight of them below 30\,cm",
        f"data: {PROFILE}, weeks 12 to 21 (7 September to 9 November): 25.3, 25.2, 6.6, 1.8, 5.8, 13.5, 21.0, 45.3, 18.0, 48.4 cm")

# ---- the episodes of the season
L.claim(MAIN, "a loss that builds from July and nearly triples in the autumn", "AutumnWaveQ/AugWaveQ", [2.6, 3.0],
        "result: the autumn episode (weeks 12-23) over the August one (weeks 7-11), reference network; nearly triples = 2.6-3.0")
L.claim(MAIN, "nearly three times as much, because it is longer and deeper", "AutumnWaveQ/AugWaveQ", [2.6, 3.0],
        "result: the autumn episode (weeks 12-23) over the August one (weeks 7-11), reference network; nearly three times = 2.6-3.0")
L.claim(MAIN, "and the second costs a fifth more than it would have alone", "100*(WaveBafterAQ/WaveBQ-1)", [17, 23],
        "result: what the second episode adds after the first against its cost alone, reference network; a fifth = 17-23")
L.claim(MAIN, "divides the loss by about three and a half compared with a model that keys every input to its region", "NoPoolQ/DEUlossQ",
        [3.25, 3.75], "result: the run without pooling over the reference run; about three and a half = 3.25-3.75")
L.claim(MAIN, "and a fleet built for low water more than a fifth", "LevFleetAvg", [20.5, 24.4],
        "result: fleet lever, mean of the eleven networks; more than a fifth = 20.5-24.4")
L.claim(MAIN, "a fleet built for low water more than a fifth (a quarter with its gain", "LevFleetAvg", [20.5, 24.4],
        "result: fleet lever, mean of the eleven networks; more than a fifth = 20.5-24.4")

# ---- S6 and S8 of the SI
# (the sentence on November and December of S6 carries no number: the generated table of the test holds them)
L.claim(SI, "Under the ceiling the levers remove the same or a larger share of a smaller loss than under the paper's rule",
        "min(CrossStockRail - LevStock, CrossDeepRail - LevDeep, CrossStockTRail - LevStockT, CrossFleetRail - LevFleet)", [0, 100],
        "result: % of the loss removed on top of the 50 kt ceiling against the same lever under the paper's rule, reference network")
L.claim(SI, "the targeted inventories gain the most and pass the fleet",
        "(CrossStockTRail - LevStockT) - max(CrossStockRail - LevStock, CrossDeepRail - LevDeep, CrossFleetRail - LevFleet)", [1, 100],
        "result: the gain in share removed is largest for the targeted inventories")
L.claim(SI, "the targeted inventories gain the most and pass the fleet", "CrossStockTRail - CrossFleetRail", [1, 100],
        "result: under the ceiling the targeted inventories remove more than the fleet (under the paper's rule the fleet removes more)")
L.claim(SI, "the targeted inventories gain the most and pass the fleet", "LevFleet - LevStockT", [0.5, 100],
        "result: under the paper's rule, on the reference network, the fleet removes more than the targeted inventories")

# ---- S9: the sea rate
L.allow(SI, r"With dry bulk at 0.0034 and liquid bulk at 0.0051 USD per tonne-kilometer",
        "design: calibration/sea_rate_by_cargo.yaml (run 2026_r6_bycargo_searate); the values are those of kim2023, Table 5.5, in euros")
L.claim(SI, "The smallest effect of the table.", "abs(RevSeaRateThree/DEUlossQThree - 1)*100", [0, 3.9],
        "result: the sea-rate run changes the 2026 loss by less than the next smallest row of the table (loading share below 5 cm at 0.04, 4 %)")

dropped = L.drop_missing(OVERLEAF)
L.save()
if dropped:
    log = Path(__file__).resolve().parent / "ledger_dropped_20261111.txt"
    with open(log, "a", encoding="utf-8") as f:
        f.write("\n# dropped by ledger_20261111_observed.py (the rewording for the season as observed)\n" + "\n".join(dropped) + "\n")
    print(f"{len(dropped)} entries dropped, listed in {log.name}")
