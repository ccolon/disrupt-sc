r"""Provenance of the runs after the batch of 11 November 2026. Run once; exact anchors, nothing is written if one is missing.

  cluster/merge_cluster_tables_20261111.py  writes compare_runs_batch_jobs_20261111_inv075.csv/.txt: the 2018 run at 0.75
                                            times the inventories as repeated on the model code of 2 November
  make_numbers.py, si_tables.py             read that table when the batch has it, else the table of 6 November
  si_tables.py (runs_table)                 the run list names the job list each run was launched from, looked up in
                                            cluster/jobs_*.txt, since the tables of this batch are assembled from several lists
    python patch_tools_20261111_provenance.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

STUDY = HERE.parent

g = Doc(STUDY / "cluster" / "merge_cluster_tables_20261111.py")
g.sub('''        print(f"{inv} on the model code of 2 November against the run of 6 November: " + ("identical in every column" if not diff else f"DIFFERS: {diff}"))
''', '''        print(f"{inv} on the model code of 2 November against the run of 6 November: " + ("identical in every column" if not diff else f"DIFFERS: {diff}"))
        # the repeated run is the one the paper reads: its table, in the shape of the table of 6 November
        out = out_dir / f"compare_runs_batch_jobs_{NEW}_inv075"
        cols = list(read_csv(old_inv).columns)
        new_csv.loc[[inv], cols].to_csv(out.with_suffix(".csv"))
        note = ("assembled by merge_cluster_tables_20261111.py: the 2018 run at 0.75 times the inventories repeated on the model code of "
                "2 November 2026 (jobs_20261111_ref.txt); the run of 6 November is in compare_runs_batch_jobs_20261106_inv075")
        txt = "\\n".join(header(ref.with_suffix(".txt"))) + "\\n" + new_csv.loc[[inv], cols].T.to_string() + "\\n\\n" + MARK + "\\n" + new_wk[[inv]].dropna().to_string() + "\\n\\n" + f"# {note}\\n"
        out.with_suffix(".txt").write_text(txt, encoding="utf-8")
        print(f"   written: {out.name}.csv/.txt")
''')
g.save()

m = Doc(STUDY / "make_numbers.py")
m.sub('''    zv = AD / "compare_runs_batch_jobs_20261106_inv075.csv"           # the rung at x0.75 of 6 Nov 2026 (jobs_20261106_inv075.txt)
''', '''    zv = AD / f"compare_runs_batch_jobs_{date_list}_inv075.csv"         # 11 Nov 2026: the rung at x0.75 repeated on the model code of 2 November (jobs_20261111_ref.txt)
    if not zv.exists():
        zv = AD / "compare_runs_batch_jobs_20261106_inv075.csv"       # the rung at x0.75 of 6 Nov 2026 (jobs_20261106_inv075.txt)
''')
m.sub('''("Inv075", "compare_runs_batch_jobs_20261106_inv075.csv")) if (AD / f_).exists()}''',
      '''("Inv075", zv.name)) if (AD / f_).exists()}''')
m.save()

t = Doc(STUDY / "si_tables.py")
t.sub('''set_batch(os.environ.get("RHINE_TAG", "s07"), os.environ.get("RHINE_LISTS", "20261007"))
''', '''set_batch(os.environ.get("RHINE_TAG", "s07"), os.environ.get("RHINE_LISTS", "20261007"))


def inv075_csv() -> str:
    """The table of the 2018 run at 0.75 times the inventories: the repeat of 11 Nov 2026 on the model code of 2 November
    when the batch has it, else the run of 6 November."""
    f = f"compare_runs_batch_jobs_{LISTS}_inv075.csv"
    return f if (AD / f).exists() else "compare_runs_batch_jobs_20261106_inv075.csv"


def job_list(run: str, table_file: str) -> str:
    """The job list a run was launched from. To the batch of 2 November the table of a list carried the list's name. From
    the batch of 11 November 2026 the tables are assembled from several lists (cluster/merge_cluster_tables_20261111.py),
    so the list is looked up: the latest cluster/jobs_*.txt that names the run (the two reference runs are named without
    _base there)."""
    if LISTS < "20261111":
        return table_file.replace("compare_runs_batch_", "").replace(".csv", ".txt")
    names = {run, run[:-5]} if run in (B26, B18) else {run}
    for f in sorted((HERE / "cluster").glob("jobs_2026*.txt"), reverse=True):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.split("|")[0].strip() in names:
                return f.name
    raise SystemExit(f"runs list: no job list in cluster/ names {run}")
''')
t.sub('''"altriver": f"compare_runs_batch_jobs_{ALT}_altriver.csv", "inv075": "compare_runs_batch_jobs_20261106_inv075.csv"}''',
      '''"altriver": f"compare_runs_batch_jobs_{ALT}_altriver.csv", "inv075": inv075_csv()}''')
t.sub('''            parts.append(pd.DataFrame({"run": t.index, "job_list": f_.replace("compare_runs_batch_", "").replace(".csv", ".txt"),''',
      '''            parts.append(pd.DataFrame({"run": t.index, "job_list": [job_list(r_, f_) for r_ in t.index],''')
t.sub('''f"compare_runs_batch_jobs_{LISTS}_ladder.csv", "compare_runs_batch_jobs_20261106_inv075.csv",''',
      '''f"compare_runs_batch_jobs_{LISTS}_ladder.csv", inv075_csv(),''')
t.save()
