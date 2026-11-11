r"""Ledger of paper_gate.py after the new structure of the SI (11 November 2026, patch_si_20261111_structure.py): entries
for the sentences written for S8 and S9, then the entries whose sentence left the manuscript are dropped and appended to
ledger_dropped_20261111.txt. Running it again changes nothing.

    python studies/rhine2026/review/ledger_20261111_structure.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_edit import Ledger  # noqa: E402
from si_patchlib import OVERLEAF  # noqa: E402

L = Ledger()
SI, MAIN = "si.tex", "main.tex"

# ---- S8 Adaptation levers: the definitions (design values, as in the Methods) -----------------------------------------
L.claim(SI, "to every inventory target below the 90-day coping duration, for every buyer of the 28 economies", "NRegions", [28, 28],
        r"design: targets are raised below the 90-day coping duration (run_rhine.py --inventory-add-days 7); the 28 economies are \NRegions")
L.allow(SI, "The inventory that it adds is 7/365 of the buyers' annual purchases of goods inputs", "arithmetic: seven days of a year of purchases")
L.allow(SI, r"The lever adds 20\,cm to the gauge on every reach of the Rhine", "design: run_rhine.py --gauge-offset 20")
L.allow(SI, r"from 1.90 to 2.10\,m at the equivalent low-water level",
        "source: the deepening project of the Middle Rhine (bmv2019, baw2026), the figures of the Methods")
L.allow(SI, r"A variant adds the 20\,cm on the Kaub reach alone", "design: run_rhine.py --gauge-offset 20 --gauge-offset-scope kaub")

# ---- S9 Sensitivity analysis: the list ------------------------------------------------------------------------------
L.claim(SI, "The largest effect. If a buyer could not replace the fuel, grain or cement of one region",
        "(NoPoolQ - max(RevNoRail, TableLowQ, RevRestSixty, GateOnlyQ))/DEUlossQ", [0.01, 100],
        "result: without pooling the 2026 loss exceeds every other run of the sensitivity table")
L.allow(SI, r"If the bulk cut at Kaub may go by rail up to 50 kt a week, the loss is \RevRailFiftyAbs\,\% lower, and up to 140 kt a week",
        "design: the two ceilings of the rail runs (--bulk-relief-tons 50000 and 140000)")
L.allow(SI, r"billion USD of goods at 50 kt and \ReliefBnHundredForty{} billion at 140 kt", "design: the two ceilings of the rail runs")
L.claim(SI, "so the lower ceiling is reached in nearly every week", "min(RailBindFifty/23, RailBindFiftyyy/22)", [0.9, 1.0],
        "result: the 50 kt ceiling is reached in nearly every profile week of both events (23 and 22 weeks)")
L.claim(SI, "at 140 kt the building-materials chain is nearly whole again", "ShareConstructionRailHundredForty", [0, 3],
        "result: construction's share of the German loss under the 140 kt ceiling")
L.allow(SI, "With every inventory target multiplied by 0.75, 1.25, 1.5 and 2",
        "design: the inventory levels of the 2018 runs (--inventory-scale 0.75, 1.25, 1.5, 2 against 1)")
L.allow(SI, r"With the shortfall it implies raised or lowered by 15\,\%",
        "design: the two variants of the loading curve (draught_table_low.csv, draught_table_high.csv: shortfall x1.15 and x0.85)")
L.allow(SI, r"Its lowest value, below 5\,cm, matters less: at half and at twice that value",
        "design: the floor of the loading curve at 0.04 and 0.16 against 0.08 (draught_table_floor04.csv, draught_table_floor16.csv)")
L.claim(SI, "far below the benchmark's band. The reference value of one supplier is kept", "RecordIntLow - SupTwoInt", [1, 100],
        "result: with two suppliers per input the industrial shortfall of 2018 is far below the lower edge of the one-standard-deviation band")
L.allow(SI, "At 15 and 60 days instead of 30", "design: --restoration-days 15 and 60 against the 30 days of the reference run")
L.allow(SI, r"At 10 and 25\,\% instead of 2", "design: the headroom of the anchored capacities in the two headroom runs")
L.allow(SI, "With a coping duration of 45 days instead of 90 for the non-storable inputs",
        "design: inventory_targets_service45.yaml against the 90-day coping duration")
L.claim(SI, "the Kaub reach is the binding one", "abs(RevDeepLocalRemoves - LevDeep)", [0, 10],
        "result: the fairway on the Kaub reach alone removes about as much as the offset on every reach")

# ---- main text: the pointer of a sentence changed -------------------------------------------------------------------
L.allow(MAIN, "two stress paths (Supplementary Section~S9), not bounds", "count: the two stress paths (25th and 75th percentile of the outlook)")

dead = L.drop_missing(OVERLEAF)
L.save()
out = Path(__file__).resolve().parent / "ledger_dropped_20261111.txt"
old = out.read_text(encoding="utf-8") if out.exists() else ""
if dead and "Dropped with the new structure of the SI" not in old:
    out.write_text(old.rstrip("\n") + "\n\nDropped with the new structure of the SI (afternoon of 11 November 2026):\n\n" + "\n".join(sorted(dead)) + "\n",
                   encoding="utf-8")
print(f"{len(dead)} entries dropped")
