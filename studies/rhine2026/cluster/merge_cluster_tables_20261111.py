"""Assemble the comparison tables of the paper set after the batch of 11 November 2026 (the 2026 runs on the season as
observed; batch_20261111.md).

    python studies/rhine2026/cluster/merge_cluster_tables_20261111.py <folder with the two cluster tables> <additional_data dir>

The readers (make_numbers.py, si_tables.py, the figure scripts) take one list date: with --lists 20261111 they read
compare_runs_batch_jobs_20261111_{main,paired,rev,ladder,cross,norail}.csv. This script writes those six tables in the
shape of the tables of 2 November:

  - the rows of the runs that read the 2026 profile come from the cluster's tables of the two lists of 11 November
    (compare_runs_batch_jobs_20261111_ref.* and compare_runs_batch_jobs_20261111_paired.*);
  - the rows of the 2018 runs, which were not rerun, come from the tables of 2 November already in additional_data
    (compare_runs_batch_jobs_20261102_*);
  - the two stress paths on the outlook's quartiles (q25, q75) are gone.

The control run (2026_r6_bycargo_profile0930) and the repeated 2018 run at 0.75 times the inventories are compared with
the batch of 2 November and of 6 November and printed; they enter no table here (the x0.75 row stays in
compare_runs_batch_jobs_20261106_inv075.csv unless the comparison says otherwise).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_cluster_tables import MARK, ORDER_MAIN, RENAME, T, header, read_csv, weekly  # noqa: E402

NEW, OLD = "20261111", "20261102"


def is_2026(run: str) -> bool:
    return run.startswith(("2026_", "wave_"))


def main(cluster_dir, out_dir):
    cluster_dir, out_dir = Path(cluster_dir), Path(out_dir)
    ref = cluster_dir / f"compare_runs_batch_jobs_{NEW}_ref"
    paired = cluster_dir / f"compare_runs_batch_jobs_{NEW}_paired"
    new_csv = pd.concat([read_csv(ref.with_suffix(".csv")), read_csv(paired.with_suffix(".csv"))])
    new_wk = pd.concat([weekly(ref.with_suffix(".txt")), weekly(paired.with_suffix(".txt"))], axis=1)
    sea = cluster_dir / f"compare_runs_batch_jobs_{NEW}_searate_b"         # the sea-rate run has a list of its own
    sea_run = f"2026_{T}_searate"
    if sea.with_suffix(".csv").exists():
        new_csv = pd.concat([new_csv, read_csv(sea.with_suffix(".csv")).loc[[sea_run]]])
        new_wk = pd.concat([new_wk, weekly(sea.with_suffix(".txt"))[[sea_run]]], axis=1)
    assert not new_csv.index.duplicated().any(), "a run appears twice in the cluster tables"

    def assemble(name: str, rows: list[str]):
        old = out_dir / f"compare_runs_batch_jobs_{OLD}_{name}"
        old_csv, old_wk = read_csv(old.with_suffix(".csv")), weekly(old.with_suffix(".txt"))
        parts_csv, parts_wk, src = [], [], []
        for r in rows:
            if is_2026(r):
                assert r in new_csv.index and r in new_wk.columns, (name, r, "missing from the tables of 11 November")
                parts_csv.append(new_csv.loc[[r]]); parts_wk.append(new_wk[r]); src.append("11 Nov")
            else:
                assert r in old_csv.index and r in old_wk.columns, (name, r, "missing from the tables of 2 November")
                parts_csv.append(old_csv.loc[[r]]); parts_wk.append(old_wk[r]); src.append("2 Nov")
        t = pd.concat(parts_csv)
        w = pd.concat(parts_wk, axis=1)
        cols = [c for c in old_csv.columns if c in t.columns]
        assert cols == list(old_csv.columns), (name, "columns differ from the tables of 2 November", list(t.columns))
        out = out_dir / f"compare_runs_batch_jobs_{NEW}_{name}"
        t[cols].to_csv(out.with_suffix(".csv"))
        note = (f"assembled by merge_cluster_tables_20261111.py: {src.count('11 Nov')} runs on the 2026 profile of 11 November 2026 from the "
                f"cluster tables of the lists jobs_20261111_ref and jobs_20261111_paired, {src.count('2 Nov')} runs of 2018 from the table "
                f"compare_runs_batch_jobs_{OLD}_{name} (not rerun)")
        h = header(ref.with_suffix(".txt"))
        txt = "\n".join(h) + "\n" + t[cols].T.to_string() + "\n\n" + MARK + "\n" + w.to_string() + "\n\n" + f"# {note}\n"
        out.with_suffix(".txt").write_text(txt, encoding="utf-8")
        print(f"{name}: {len(t)} runs ({src.count('11 Nov')} of 11 Nov, {src.count('2 Nov')} of 2 Nov), {w.shape[0]} weeks -> {out.name}.csv/.txt")

    old_rows = lambda name: list(read_csv((out_dir / f"compare_runs_batch_jobs_{OLD}_{name}").with_suffix(".csv")).index)   # noqa: E731
    assemble("main", ORDER_MAIN)
    assemble("paired", old_rows("paired"))
    assemble("rev", [r for r in old_rows("rev") if not r.endswith(("_q25", "_q75"))] + ([sea_run] if sea_run in new_csv.index else []))
    assemble("ladder", old_rows("ladder"))
    assemble("cross", old_rows("cross"))
    assemble("norail", old_rows("norail"))

    # ---- the control and the repeated 2018 run ----------------------------------------------------------------------
    print()
    old_main = read_csv((out_dir / f"compare_runs_batch_jobs_{OLD}_main").with_suffix(".csv"))
    ctrl, base = f"2026_{T}_profile0930", f"2026_{T}_base"
    if ctrl in new_csv.index:
        a, b = new_csv.loc[ctrl], old_main.loc[base]
        num = [c for c in old_main.columns if pd.api.types.is_number(b[c])]
        diff = {c: (float(a[c]), float(b[c])) for c in num if float(a[c]) != float(b[c])}
        print(f"CONTROL {ctrl} against {base} of 2 November: " + ("identical in every column" if not diff else f"DIFFERS: {diff}"))
        wa = new_wk[ctrl].astype(float).reset_index(drop=True)
        wb = weekly((out_dir / f"compare_runs_batch_jobs_{OLD}_main").with_suffix(".txt"))[base].astype(float).reset_index(drop=True)
        n = min(len(wa), len(wb))
        same = ((wa[:n] == wb[:n]) | (wa[:n].isna() & wb[:n].isna())).all() and len(wa) == len(wb)      # weeks after the run's end are empty
        print(f"   weekly German loss: {'identical' if same else 'DIFFERS'} over {int(wa[:n].notna().sum())} weeks "
              f"(largest gap {float((wa[:n] - wb[:n]).abs().max()):.6f} mUSD)")
    else:
        print(f"CONTROL {ctrl}: not in the cluster tables")
    inv = f"2018_{T}_inv075"
    old_inv = out_dir / "compare_runs_batch_jobs_20261106_inv075.csv"
    if inv in new_csv.index and old_inv.exists():
        a, b = new_csv.loc[inv], read_csv(old_inv).loc[inv]
        num = [c for c in b.index if pd.api.types.is_number(b[c])]
        diff = {c: (float(a[c]), float(b[c])) for c in num if float(a[c]) != float(b[c])}
        print(f"{inv} on the model code of 2 November against the run of 6 November: " + ("identical in every column" if not diff else f"DIFFERS: {diff}"))
        # the repeated run is the one the paper reads: its table, in the shape of the table of 6 November
        out = out_dir / f"compare_runs_batch_jobs_{NEW}_inv075"
        cols = list(read_csv(old_inv).columns)
        new_csv.loc[[inv], cols].to_csv(out.with_suffix(".csv"))
        note = ("assembled by merge_cluster_tables_20261111.py: the 2018 run at 0.75 times the inventories repeated on the model code of "
                "2 November 2026 (jobs_20261111_ref.txt); the run of 6 November is in compare_runs_batch_jobs_20261106_inv075")
        txt = "\n".join(header(ref.with_suffix(".txt"))) + "\n" + new_csv.loc[[inv], cols].T.to_string() + "\n\n" + MARK + "\n" + new_wk[[inv]].dropna().to_string() + "\n\n" + f"# {note}\n"
        out.with_suffix(".txt").write_text(txt, encoding="utf-8")
        print(f"   written: {out.name}.csv/.txt")
    assert RENAME, "merge_cluster_tables.RENAME is used by read_csv"


if __name__ == "__main__":
    main(*sys.argv[1:])
