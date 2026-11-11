r"""Reading tools for the batch of 11 November 2026 (the 2026 runs on the season as observed). Run once, before
make_numbers.py and si_tables.py are run with --lists 20261111; exact anchors, nothing is written if one is missing.

  make_numbers.py  the two stress paths on the outlook's quartiles are gone (macros RevQLow, RevQHigh and their variants);
                   the one conversion of the text from US dollars to euros uses the 2022 average rate, 1.053 USD per EUR
                   (the rate of the note of the transport-cost table), instead of 0.92 EUR per USD.
  si_tables.py     the sensitivity table loses the two rows on the gauge of the forecast weeks; the table of the test on the
                   production index loses the row of the earlier version's measure, and its row of low-water days is labelled
                   for the new profile.
    python patch_tools_20261111_reading.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

STUDY = HERE.parent

m = Doc(STUDY / "make_numbers.py")
m.sub('''("RevDfuel", f"2026_{REV}_dfuel0"), ("RevServ", f"2026_{REV}_serv45"),
                         ("RevQLow", f"2026_{REV}_q25"), ("RevQHigh", f"2026_{REV}_q75")):''',
      '''("RevDfuel", f"2026_{REV}_dfuel0"), ("RevServ", f"2026_{REV}_serv45")):     # 11 Nov 2026: no stress path on the outlook any more''')
m.sub('''    put("AugWaveEurBn", r1(ind[ind.time_step.between(7, 11)].loss.sum() / 1e3 * 0.92), "EUR bn, industry part of the August trough (0.92 EUR per USD)")''',
      '''    # 11 Nov 2026: the 2022 average rate of the ECB, 1.053 USD per EUR, as in the note of the transport-cost table (was 0.92 EUR per USD)
    put("AugWaveEurBn", r1(ind[ind.time_step.between(7, 11)].loss.sum() / 1e3 / 1.053), "EUR bn, industry part of the August trough (1.053 USD per EUR, 2022 average)")''')
m.save()

t = Doc(STUDY / "si_tables.py")
t.sub('''            row("gauge of the forecast weeks", "outlook's median", "25th percentile", "q25"),
            row("", "", "75th percentile", "q75"),
''', "")
t.sub('''    rows = ["model, reference network, index measure & " + " & ".join(cell(d[f"ind_{m}"]) for m in labs) + f" & {cell(d['ind_integrated_pct_months'])} \\\\\\\\",
            "model, reference network, production-weighted B--E (the earlier version's measure) & " + " & ".join(cell(d[f"indprod_{m}"]) for m in labs) + f" & {cell(d['indprod_integrated_pct_months'])} \\\\\\\\"]''',
      '''    # 11 Nov 2026: one measure, the index measure (the row of the production-weighted B-E series of the earlier version is gone)
    rows = ["model, reference network & " + " & ".join(cell(d[f"ind_{m}"]) for m in labs) + f" & {cell(d['ind_integrated_pct_months'])} \\\\\\\\"]''')
t.sub('''            "low-water days (observed to 29 September, then the profile) & "''',
      '''            "low-water days (observed to 10 November, then the forecasts) & "''')
t.save()
