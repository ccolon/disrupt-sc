r"""The author's choice of 13 November 2026 on the detail that left Tables S1, S2, S3 and S7 ("ok for (a)"): each
caption says where the full list of figures and sources is, and the detailed tables go into the data deposit.

    python studies/rhine2026/evidence/build_si_tables_detailed.py      # the document the captions point to
    python studies/rhine2026/review/patch_20261113_captions_detail.py

- si.tex: one sentence at the end of the four captions (the same sentence is in si_tables_evidence.DETAIL, which the
  generator prints for a new block).
- main.tex, Data availability: the detailed evidence is named among what is deposited.
- submission/build_zenodo_package.py: the document (evidence/si_tables_detailed.pdf) and its LaTeX source join the
  package. Nothing is uploaded.
Running it again changes nothing.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(HERE))
from si_patchlib import OVERLEAF, Doc  # noqa: E402
from si_tables_evidence import DETAIL  # noqa: E402

d = Doc(OVERLEAF / "si.tex")
for old, new in (
        (r"on which the road and rail values are calibrated (Section~S2). Notes follow the table.}",
         r"on which the road and rail values are calibrated (Section~S2). " + DETAIL + " Notes follow the table.}"),
        (r"Input-specific targets are given in Table~\ref{tab:stockoverrides}.}", r"Input-specific targets are given in Table~\ref{tab:stockoverrides}. " + DETAIL + "}"),
        (r"Grades as in Table~\ref{tab:stocks}.}", r"Grades as in Table~\ref{tab:stocks}. " + DETAIL + "}"),
        (r"with the evidence for each value and how the value is set.}", r"with the evidence for each value and how the value is set. " + DETAIL + "}")):
    d.sub(old, new)
d.save()

m = Doc(OVERLEAF / "main.tex")
m.sub(r"The gauge profile, the run tables of this paper, and the model's scope data package (network, agents, tables, and scenario files) will be deposited on Zenodo upon acceptance; until then, they are available from the corresponding author.",
      r"The gauge profile, the run tables of this paper, the detailed evidence behind Supplementary Tables~\ref{tab:rates}, \ref{tab:stocks}, \ref{tab:stockoverrides} and~\ref{tab:loading}, and the model's scope data package (network, agents, tables, and scenario files) will be deposited on Zenodo upon acceptance; until then, they are available from the corresponding author.")
m.save()

p = HERE / "submission" / "build_zenodo_package.py"
raw = p.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
s = raw.replace("\r\n", "\n")
if "si_tables_detailed.pdf" not in s:
    anchor = '    ("scenarios", "repo", "studies/rhine2026/scenarios/*.csv",\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor,
                  '    ("evidence", "repo", "studies/rhine2026/evidence/si_tables_detailed.pdf",\n'
                  '     "the detailed evidence behind Supplementary Tables S1, S2, S3 and S7 (transport costs, inventory targets by industry and by input, '
                  'loading curve): every figure, date and source; the Supplementary Information prints a shorter version and points here", "own"),\n'
                  '    ("evidence", "repo", "studies/rhine2026/evidence/si_tables_detailed_20261112.tex", "the LaTeX source of these four tables", "own"),\n'
                  + anchor)
    p.write_bytes(s.replace("\n", nl).encode("utf-8"))
    print("build_zenodo_package.py: the detailed evidence joins the package")
else:
    print("build_zenodo_package.py: already lists the detailed evidence")
