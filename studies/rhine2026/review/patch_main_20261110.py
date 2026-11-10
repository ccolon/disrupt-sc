r"""SI revision of 10 Nov 2026: what the answers to the SI notes require in main.tex and in the forecast manifest.

N25 (S3): the profile built on the outlook of 7 September is no longer described in the SI, so the Methods no longer
point to it. Found with it: the Methods call the reissue of 7 October 'the batches of this paper' and score the series
'as issued on 7 October', while every number of the manuscript comes from the rerun of 2 November (calibrated baseline,
one capacity per cargo class). The SI (S3, Gauges) now states the three versions; in main.tex the two sentences get a
note for the author, who decides the wording and which series is scored. The forecast manifest receives the missing
row of the rerun.

    python patch_main_20261110.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "main.tex")
d.sub(r"and in Supplementary Section~S3, with the profile of the first version (observations to 10 September, the outlook of 7 September), kept for a forecast evaluation, and the outlook's 25th- and 75th-percentile paths, two stress paths",
      r"and in Supplementary Section~S3, with the outlook's 25th- and 75th-percentile paths, two stress paths")
d.sub(r"reissued on 7 October 2026 on the rebuilt table (the batches of this paper); no production statistic of the event entered either version.",
      r"reissued on 7 October 2026 on the rebuilt table (the batches of this paper)\todo{the numbers of this paper come from the rerun of 2 November 2026 (calibrated baseline, one capacity per cargo class), not from the reissue of 7 October; Supplementary Section~S3 now says so; to be said here}; no production statistic of the event entered either version.")
d.sub(r"scores the reference network's series as issued on 7 October, and the mean",
      r"scores the reference network's series as issued on 7 October\todo{to decide: the series issued on 7 October, or the rerun of 2 November that Table~\ref{tab:prospective} shows?}, and the mean")
d.save()

m = Doc(Path(__file__).resolve().parents[1] / "forecast_manifest.md")
row7 = "7 October 2026, Overleaf `cc34ca7` (batch of 7 Oct written in), `d1e453e` (ladder); text revised 9 October (`17b3aa4`), numbers unchanged |\n"
m.sub(row7, row7 +
      "| Rerun of the paper, 2 November 2026 | `ba94dca` (1 Nov: capacities per cargo class), `d72aa00` (2 Nov: the lists); batch read in `410ace9` and `9b17d81` | "
      "`cluster/jobs_20261102_{main,paired,rev,cross,norail}.txt`, `jobs_20261103_altriver.txt`, `jobs_20261106_inv075.txt` (129 runs; results "
      "`additional_data/compare_runs_batch_jobs_20261102_*.csv`) | **1.11** (`2026_r6_bycargo_base`; peak 2.10 in week 18; 13.1 bn); eleven draws 1.12 ± 0.41; "
      "monthly industrial path Jul 0.1 / Aug 1.5 / Sep 0.9 / Oct 2.1 / Nov −0.6 / Dec −1.1 (the prospective table of the manuscript) | "
      "2-3 November 2026, Overleaf `67e15f8` |\n")
old = "entered either issue.\n"
m.sub(old, old + "\nAdded on 10 November 2026. The numbers printed in the manuscript are those of the rerun of 2 November, not of the\n"
      "reissue of 7 October. The rerun keeps the hydrological information set (section 1) and the loading table of the\n"
      "reissue (section 2); it differs by the calibration of the baseline flows on the freight statistics (six rounds between\n"
      "22 and 29 October, `calibration/round1` to `round6`; SI S2) and by the capacities per cargo class (1 November). The\n"
      "production index of August 2026, released on 7 October, was public when these changes were made and was not used; the\n"
      "first release for September came on 6 November 2026, after the rerun. Which series the prospective test scores, the one\n"
      "issued on 7 October or the rerun, is for the author to fix in the Methods (noted in main.tex on 10 November).\n")
m.save()
