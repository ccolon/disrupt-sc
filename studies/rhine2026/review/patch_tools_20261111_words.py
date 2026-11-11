r"""make_numbers.py after the reading of the batch of 11 November 2026: three numbers that the text now prints instead of
a fraction word or a rounded value. Exact anchors.

  FlatLess            % by which the flat profile costs less than the season (the text said "two fifths less"; it is 45 %)
  RevSeaRateThree     the German loss of the sea-rate run to three decimals, with DEUlossQThree for the reference run
  RevSeaRateRelOne    its change against the reference run to one decimal (it rounds to 0 %)
    python patch_tools_20261111_words.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

m = Doc(HERE.parent / "make_numbers.py")
m.sub('''put("TroughPremium", pct(100 * (base / flat - 1)), "% by which the season exceeds the flat profile")''',
      '''put("TroughPremium", pct(100 * (base / flat - 1)), "% by which the season exceeds the flat profile")
    put("FlatLess", pct(100 * (1 - flat / base)), "% by which the flat profile costs less than the season (11 Nov 2026: printed instead of a fraction word)")''')
m.sub('''        for mac, run in (("RevRailFiftyyy", f"2018_{REV}_rail50"), ("RevRailHundredFortyyy", f"2018_{REV}_rail140")):''',
      '''        # 11 Nov 2026: the sea-rate run changes the loss by half a percent, which the two-decimal macros print as no change
        sea_, ref_ = r.loc[f"2026_{REV}_searate", "DEU_%quarter"], m.loc[B, "DEU_%quarter"]
        put("RevSeaRateThree", f"{sea_:.3f}", "the sea-rate run, % of a quarter, three decimals"); put("DEUlossQThree", f"{ref_:.3f}", "the reference run, three decimals")
        put("RevSeaRateRelOne", f"{100 * (sea_ / ref_ - 1):+.1f}".replace("-", "$-$").replace("+", "$+$"), "% against the reference run, one decimal")
        for mac, run in (("RevRailFiftyyy", f"2018_{REV}_rail50"), ("RevRailHundredFortyyy", f"2018_{REV}_rail140")):''')
m.save()
