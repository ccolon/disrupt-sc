"""Run-name conventions of the paper's batches, shared by the figure scripts (2 Nov 2026).

The batch of 7 October 2026 named its runs 2026_s07_base, 2018_s07_seed3, wave07_A, 2026_rev_rail50, wave09_A_rest15 and
wrote its tables as compare_runs_batch_jobs_20261007_{main,paired,rev}.csv, ..._20261009_cross.csv and
..._20261020_norail.csv. A later batch carries one tag in every name and one list date: with RHINE_TAG=r6_bycargo and
RHINE_LISTS=20261102 the names are 2026_r6_bycargo_base, wave_r6_bycargo_A, 2026_r6_bycargo_rail50,
wave_r6_bycargo_A_rest15 and the tables compare_runs_batch_jobs_20261102_*.csv. Set the two environment variables before
running a figure script; the defaults reproduce the figures of 7 October. make_numbers.py follows the same conventions
through its --tag and --lists flags.
"""
import os

TAG = os.environ.get("RHINE_TAG", "s07")
LISTS = os.environ.get("RHINE_LISTS", "20261007")
_OLD = TAG == "s07"
WV = TAG.replace("s", "wave") if _OLD else f"wave_{TAG}"       # the waves of the main list: wave07_A
REV = "rev" if _OLD else TAG                                   # the revision runs: 2026_rev_rail50
WV9 = "wave09" if _OLD else f"wave_{TAG}"                      # the waves at a 15-day refill time: wave09_A_rest15
CROSS = "20261009" if _OLD else LISTS                          # the date of the cross list's table
NORAIL = "20261020" if _OLD else LISTS                         # the date of the no-rail list's table
if not _OLD:
    print(f"batch names: tag {TAG}, lists {LISTS} (RHINE_TAG, RHINE_LISTS)")
