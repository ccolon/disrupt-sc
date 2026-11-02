"""Assemble the comparison tables of the per-class paper set (lists of 2 Nov 2026) from the cluster's per-list tables.

    python studies/rhine2026/cluster/merge_cluster_tables.py <runs dir with the cluster tables> <additional_data dir> [paired_partial_basename]

The light-export runs carry no firm_data.csv locally, so compare_runs.py cannot be rerun here; the cluster's tables are
merged instead. The main table takes the shape of the 7 October one: the two reference runs under their _base names
(2026_r6_bycargo -> 2026_r6_bycargo_base, 2018_r6_bycargo -> 2018_r6_bycargo_base, from the lists of 2 Nov 13:27 and
1 Nov 21:01), the ten 2018 draws (from the ensemble list of 1 Nov), then the 24 runs of the main list; the ladder table
holds the three inventory runs of the ensemble list; rev, cross and norail are copied as they are; paired is built from
the partial table of the ten 2026 draws when given (the levers follow when their runs finish).
"""
import io
import shutil
import sys
from pathlib import Path

import pandas as pd

T = "r6_bycargo"
MARK = "== weekly value-added loss of DEU (mUSD/week) =="
ORDER_MAIN = ([f"2026_{T}_base", f"2018_{T}_base", f"2026_{T}_nopool", f"2018_{T}_nopool"] + [f"2018_{T}_seed{s}" for s in range(1, 11)]
              + [f"2026_{T}_{k}" for k in ("stock7", "deep20", "fleet", "stock7t", "package")]
              + [f"wave_{T}_{k}" for k in ("A", "B", "AB_gap1", "AB_gap2", "AB_gap4", "AB_gap8", "flat")]
              + [f"2026_{T}_gateonly", f"2026_{T}_surchargeonly", f"2026_{T}_tablelow", f"2026_{T}_tablehigh", f"2018_{T}_tablelow",
                 f"2018_{T}_tablehigh", f"2026_{T}_sup2", f"2018_{T}_sup2", f"2026_{T}_full", f"2018_{T}_full"])
RENAME = {f"2026_{T}": f"2026_{T}_base", f"2018_{T}": f"2018_{T}_base"}


def read_csv(p):
    t = pd.read_csv(p).set_index("run")
    return t.rename(index=RENAME)


def weekly(p):
    txt = Path(p).read_text(encoding="utf-8", errors="replace")
    block = txt.split(MARK)[1]
    lines = [l for l in block.splitlines() if l.strip() and not l.startswith("written") and not l.startswith("#") and not l.startswith("==")
             and not l.startswith("PARTIALDONE")]
    w = pd.read_csv(io.StringIO("\n".join(lines)), sep=r"\s+", engine="python")
    w.index.name = "time_step"
    return w.rename(columns=RENAME)


def header(p):
    return [l for l in Path(p).read_text(encoding="utf-8", errors="replace").splitlines()[:2]]


def write(name, rows, srcs, out_dir, note):
    csvs = pd.concat([read_csv(s.with_suffix(".csv")) for s in srcs])
    wks = pd.concat([weekly(s.with_suffix(".txt")) for s in srcs], axis=1)
    missing = [r for r in rows if r not in csvs.index]
    assert not missing, (name, missing)
    assert all(r in wks.columns for r in rows), (name, [r for r in rows if r not in wks.columns])
    t = csvs.loc[rows]
    w = wks[rows]
    out = out_dir / f"compare_runs_batch_jobs_20261102_{name}"
    t.to_csv(out.with_suffix(".csv"))
    h = header(srcs[0].with_suffix(".txt"))
    txt = "\n".join(h) + "\n" + t.T.to_string() + "\n\n" + MARK + "\n" + w.to_string() + "\n\n" + f"# {note}\n"
    out.with_suffix(".txt").write_text(txt, encoding="utf-8")
    print(f"{name}: {len(t)} runs, {w.shape[0]} weeks -> {out.name}.csv/.txt")


def main(runs, out_dir, partial=None):
    runs, out_dir = Path(runs), Path(out_dir)
    c = lambda n: runs / f"compare_runs_batch_jobs_{n}"
    note = "merged locally on 2 Nov 2026 from the cluster tables of the lists 20261102_main, 20261102_2026_bycargo, 20261101_hindcast_bycargo and 20261101_bycargo_ens (merge_tables.py)"
    write("main", ORDER_MAIN, [c("20261102_main"), c("20261102_2026_bycargo"), c("20261101_hindcast_bycargo"), c("20261101_bycargo_ens")], out_dir, note)
    write("ladder", [f"2018_{T}_inv{k}" for k in (125, 150, 200)], [c("20261101_bycargo_ens")], out_dir,
          "the inventory ladder of the list 20261101_bycargo_ens (merge_tables.py, 2 Nov 2026)")
    for n in ("rev", "cross", "norail"):
        for ext in (".csv", ".txt"):
            shutil.copyfile(c(f"20261102_{n}").with_suffix(ext), out_dir / f"compare_runs_batch_jobs_20261102_{n}{ext}")
        print(f"{n}: copied from the cluster table")
    if partial:
        p = Path(partial)
        rows = list(read_csv(p.with_suffix(".csv")).index)
        write("paired", rows, [p], out_dir, "PARTIAL: the ten 2026 draws (and the seed-3 levers if present), compare_runs.py on the cluster, 2 Nov 2026 21:25; the levers follow")


if __name__ == "__main__":
    main(*sys.argv[1:])
