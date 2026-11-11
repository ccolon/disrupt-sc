r"""Tooling, round of 11 November 2026 (run once; exact anchors, nothing is written if one is missing):

  si_tables.py     the weekly table of flows turned away at Kaub has no column "total" any more (point 4 of the author's
                   answers); the table of rail weeks is no longer generated (note N12: the table left the SI);
  make_numbers.py  the counts of that table become macros (RailBindFifty, RailBindFiftyyy, RailBindHundredForty,
                   RailBindHundredFortyyy: the profile weeks in which each rail ceiling is reached).
    python patch_tools_20261111.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

STUDY = HERE.parent

# ---- si_tables.py ---------------------------------------------------------------------------------------------------
t = Doc(STUDY / "si_tables.py")
t.sub(r"""        rows.append(f"{t} & {r.week_start} & {tex(r.status)} & {float(r.kaub_cm):.1f} & {lf(float(r.kaub_cm)):.2f} & {cut / 1e3:.0f} & {resent / 1e3:.0f} & {blocked / 1e3:.0f} \\\\")""",
      r"""        # 11 Nov 2026 (the author's answer to open point 4): the column of the total (rerouted + blocked) is no longer printed
        rows.append(f"{t} & {r.week_start} & {tex(r.status)} & {float(r.kaub_cm):.1f} & {lf(float(r.kaub_cm)):.2f} & {resent / 1e3:.0f} & {blocked / 1e3:.0f} \\\\")""")
t.sub(r"""\begin{longtable}{rllrrrrr}
\caption{\textbf{The gate week by week, 2026 reference run.}""",
      r"""\begin{longtable}{rllrrrr}
\caption{\textbf{The gate week by week, 2026 reference run.}""")
t.sub("week & start & status & Kaub & loading share & cut & re-sent & withheld \\\\", "week & start & status & Kaub & loading share & re-sent & withheld \\\\", count=2)
t.sub("revision_table, cross_table, rail_weeks_table, ports_table, modal_table):",
      "revision_table, cross_table, ports_table, modal_table):   # 11 Nov 2026: rail_weeks_table left the SI (its counts are macros RailBind*)")
t.save()

# ---- make_numbers.py ------------------------------------------------------------------------------------------------
m = Doc(STUDY / "make_numbers.py")
m.sub(r"""        put("RailOfferedMax", f"{10 * np.floor(max(offr_) / 10 + 0.5):.0f}", f"the most ({max(offr_):.1f})")
""",
      r"""        put("RailOfferedMax", f"{10 * np.floor(max(offr_) / 10 + 0.5):.0f}", f"the most ({max(offr_):.1f})")
        # 11 Nov 2026: the profile weeks in which each ceiling is reached (the placed tonnage within 0.5 kt of the ceiling), the
        # counts that the caption of the former table of rail weeks carried (si_tables.rail_weeks_table, same rule)
        for mac_, run_, ceil_ in (("RailBindFifty", f"2026_{REV}_rail50", 50), ("RailBindFiftyyy", f"2018_{REV}_rail50", 50),
                                  ("RailBindHundredForty", f"2026_{REV}_rail140", 140), ("RailBindHundredFortyyy", f"2018_{REV}_rail140", 140)):
            np_ = len(pd.read_csv(HERE / "scenarios" / f"{run_[:4]}.csv"))
            nb_ = 0
            for line_ in (RUNS / f"{run_}.log").read_text(encoding="utf-8", errors="replace").splitlines():
                mt_ = re.search(r"Capacity gate t=(\d+):.*relief ([\d,]+) t of ([\d,]+) t offered", line_)
                if mt_ and int(mt_.group(1)) <= np_ and float(mt_.group(3).replace(",", "")) > 0 and float(mt_.group(2).replace(",", "")) / 1e3 >= ceil_ - 0.5:
                    nb_ += 1
            put(mac_, str(nb_), f"{run_}: profile weeks (of {np_}) in which the {ceil_} kt rail ceiling is reached")
""")
m.save()
