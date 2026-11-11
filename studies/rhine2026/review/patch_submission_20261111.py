r"""Submission files after the author's decision of 11 November 2026 ("out of the manuscript and the repo"): the forecast
manifest leaves the repository, so the files that pointed to it are reworded, and the Zenodo package no longer takes the
gauge profiles and forecasts of earlier states of the 2026 season. Exact anchors; nothing is written if one is missing.

    python patch_submission_20261111.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

SUB = HERE.parent / "submission"

z = Doc(SUB / "build_zenodo_package.py")
z.sub('''"the weekly gauge profiles (2018, 2026 and its vintages, the stress paths q25/q75, the wave experiments), the daily Kaub records, the BfG six-week outlooks, the loading tables''',
      '''"the weekly gauge profiles (2018, 2026, the wave experiments), the daily Kaub records, the two BfG forecasts behind the last three weeks of the 2026 profile, the loading tables''')
z.sub('''"Gauge records from PEGELONLINE (German Federal Waterways and Shipping Administration, WSV); six-week outlooks from the Federal Institute of Hydrology (BfG);''',
      '''"Gauge records from PEGELONLINE (German Federal Waterways and Shipping Administration, WSV); the 14-day forecast and the six-week outlook from the Federal Institute of Hydrology (BfG);''')
z.sub('''BfG outlook: TO CONFIRM the re-use terms of the ENS product (the files hold the weekly medians and the 25th/75th percentiles at Kaub only);''',
      '''BfG forecasts: TO CONFIRM the re-use terms (the files hold the forecast quantiles at Kaub only);''')
z.sub('''EXCLUDED_DEFAULT = [
''', '''# 11 Nov 2026: the 2026 profile is the river as observed; the profiles and forecasts of earlier states of the season stay out
SCENARIOS_LEFT_OUT = {"2026_vintage0910.csv", "2026_vintage0930.csv", "2026_q25.csv", "2026_q75.csv",
                      "bfg_6week_kaub_20260907.csv", "bfg_6week_kaub_20260907_classes.csv", "bfg_6week_kaub_20260930.csv",
                      "bfg_14day_kaub_20260909.csv"}

EXCLUDED_DEFAULT = [
    ("scenarios/2026_vintage*.csv, 2026_q25.csv, 2026_q75.csv, bfg_6week_kaub_20260907*.csv, bfg_6week_kaub_20260930.csv, bfg_14day_kaub_20260909.csv",
     "gauge profiles and forecasts of earlier states of the 2026 season; the paper's runs read the profile on the river as observed (scenarios/2026.csv) and none of these."),
''')
z.sub('''        matches = [m for m in matches if m.is_file() and "__pycache__" not in m.parts]''',
      '''        matches = [m for m in matches if m.is_file() and "__pycache__" not in m.parts
                   and not (zdir == "scenarios" and m.name in SCENARIOS_LEFT_OUT)]''')
z.sub('''repository for the EU folder. The versions of the code that produced each batch of runs are listed, commit by commit,",
        "in `studies/rhine2026/forecast_manifest.md` of the code repository.",''',
      '''repository for the EU folder. The runs of the paper are listed in `studies/rhine2026/additional_data/runs_20261111.csv`",
        "of the code repository; the version of the code that produced them is recorded in `studies/rhine2026/cluster/batch_20261111.md`.",''')
z.save()

r = Doc(SUB / "reporting_summary_notes.md")
r.sub('''https://github.com/ccolon/disrupt-sc, commits recorded in
`studies/rhine2026/forecast_manifest.md`; release tag and Zenodo DOI to be added)''',
      '''https://github.com/ccolon/disrupt-sc, the version of the runs recorded in
`studies/rhine2026/cluster/batch_20261111.md`; release tag and Zenodo DOI to be added)''')
r.sub('''2026 (dates in `forecast_manifest.md` and Supplementary Section S1); no field data.''',
      '''2026 (dates in Supplementary Section S1 and in the provenance files next to each data set); no field data.''')
r.save()
