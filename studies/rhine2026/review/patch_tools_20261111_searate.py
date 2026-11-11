r"""Tools for the sea-rate run of 11 November 2026 (open point 3) and for the extraction of the batch. Run once; exact
anchors, nothing is written if one is missing.

  cluster/merge_cluster_tables_20261111.py  the row of 2026_<tag>_searate, from the cluster table of its own list
                                            (jobs_20261111_searate_b), joins the table of the sensitivities
  si_tables.py                              one row of the sensitivity table: the sea rate of bulk cargo
  make_numbers.py                           the macros RevSeaRate, RevSeaRateRel, RevSeaRateAbs
  cluster/restore_extract.py                --flows-for: the baseline flow file (30 MB a run) is extracted for the runs
                                            named only; the readers take it from the reference or the link-level run
  benchmark_ademmer.py                      docstring: the daily record now runs to 10 November
    python patch_tools_20261111_searate.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

STUDY = HERE.parent

g = Doc(STUDY / "cluster" / "merge_cluster_tables_20261111.py")
g.sub('''    assert not new_csv.index.duplicated().any(), "a run appears twice in the cluster tables"
''', '''    sea = cluster_dir / f"compare_runs_batch_jobs_{NEW}_searate_b"         # the sea-rate run has a list of its own
    sea_run = f"2026_{T}_searate"
    if sea.with_suffix(".csv").exists():
        new_csv = pd.concat([new_csv, read_csv(sea.with_suffix(".csv")).loc[[sea_run]]])
        new_wk = pd.concat([new_wk, weekly(sea.with_suffix(".txt"))[[sea_run]]], axis=1)
    assert not new_csv.index.duplicated().any(), "a run appears twice in the cluster tables"
''')
g.sub('''    assemble("rev", [r for r in old_rows("rev") if not r.endswith(("_q25", "_q75"))])''',
      '''    assemble("rev", [r for r in old_rows("rev") if not r.endswith(("_q25", "_q75"))] + ([sea_run] if sea_run in new_csv.index else []))''')
g.save()

t = Doc(STUDY / "si_tables.py")
t.sub('''            row("mechanisms", "capacity limit and surcharge", "capacity limit alone", "gateonly"),''',
      '''            row("sea rate of bulk cargo (USD per tkm)", "0.0015, as containers", "0.0034 dry, 0.0051 liquid", "searate"),
            row("mechanisms", "capacity limit and surcharge", "capacity limit alone", "gateonly"),''')
t.save()

m = Doc(STUDY / "make_numbers.py")
m.sub('''("RevDfuel", f"2026_{REV}_dfuel0"), ("RevServ", f"2026_{REV}_serv45")):     # 11 Nov 2026: no stress path on the outlook any more''',
      '''("RevDfuel", f"2026_{REV}_dfuel0"), ("RevServ", f"2026_{REV}_serv45"),      # 11 Nov 2026: no stress path on the outlook any more
                         ("RevSeaRate", f"2026_{REV}_searate")):                                          # 11 Nov 2026: bulk at the sea rates of bulk carriers and tankers''')
m.save()

x = Doc(STUDY / "cluster" / "restore_extract.py")
x.sub('''    ap.add_argument("--dry-run", action="store_true")
''', '''    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--flows-for", default=None,
                    help="comma-separated run names: transport_edges_with_flows_0.geojson (30 MB a run) is taken for these "
                         "runs only; the readers use the one of the reference run or of the link-level run")
''')
x.sub('''    written = same = 0
''', '''    flows_for = None if a.flows_for is None else {r.strip() for r in a.flows_for.split(",") if r.strip()}
    written = same = skipped = 0
''')
x.sub('''            seen_runs.add(run)
''', '''            seen_runs.add(run)
            if flows_for is not None and p.name == "transport_edges_with_flows_0.geojson" and run not in flows_for:
                skipped += 1
                continue
''')
x.sub('''          f"{len(differ)} existing with another size, {len(left_out)} left out; runs {len(seen_runs)} of {len(runs)} named")''',
      '''          f"{len(differ)} existing with another size, {len(left_out)} left out; runs {len(seen_runs)} of {len(runs)} named"
          + (f"; {skipped} baseline flow files not taken (--flows-for)" if flows_for is not None else ""))''')
x.save()

b = Doc(STUDY / "benchmark_ademmer.py")
b.sub('''2026: the low-water days of June to September are observed (PEGELONLINE daily means to 29 September); from 30
September the days follow the weekly means of the profile (the BfG outlook of 28 September and the assumed
recovery), a week below 78 cm counting for all its days. The result is what the published regression implies for
2026 under the same outlook, the comparison line of the prospective test.''',
      '''2026: the low-water days are observed to 10 November (PEGELONLINE daily means; the record of 11 November is a
partial day); from 12 November the days follow the weekly means of the profile (the BfG forecasts of 11 and
9 November), a week below 78 cm counting for all its days. The result is what the published regression implies
for the 2026 season on the same river as the model's runs, the comparison line of the prospective test.''')
b.save()
