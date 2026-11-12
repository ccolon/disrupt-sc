r"""si_tables.py and the loading-table ledger after the protocol of the 2026 test left the paper (12 November 2026,
evening; review/patch_20261112_protocol_out.py). The captions that the generator writes for a new block are those of
the manuscript: the two tables are results of the 2026 season, in Section S6 of the SI after the renumbering.
Applied once.

    python studies/rhine2026/review/patch_tools_20261112_protocol_out.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def sub(path: Path, old: str, new: str) -> None:
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    s = raw.replace("\r\n", "\n")
    assert s.count(old) == 1, (path.name, s.count(old), old[:80])
    path.write_bytes(s.replace(old, new).replace("\n", nl).encode("utf-8"))


p = HERE / "si_tables.py"
sub(p, r"\caption{\textbf{The prospective test.} Days of low water at Kaub",
       r"\caption{\textbf{The monthly path of German industrial production, 2026.} Days of low water at Kaub")
sub(p, r"""\caption{\textbf{Sectoral signatures of the 2026 forecast.} Monthly shortfall of production (\%, production-weighted within the sector; negative values are production above the no-event baseline) of the German sectors on the river and of the transport operators, reference network, """ + '""" + batch_text("issued") + r"""' + r"""; the last column is the plain sum of the months (percent-months). Pre-specified for the prospective test of the main text: the production index gives the industrial rows by month, the turnover index of transport and storage the operators' rows.}""",
       r"""\caption{\textbf{The monthly path of the sectors on the river, 2026.} Monthly shortfall of production (\%, production-weighted within the sector; negative values are production above the no-event baseline) of the German sectors on the river and of the transport operators, reference network; the last column is the plain sum of the months (percent-months). In the statistics, the production index gives the industrial rows by month, and the turnover index of transport and storage the operators' rows.}""")
sub(p, '''    """The prospective test (review NS4, E3): the path that the published specification implies for the low-water days
    of 2026, and the model's monthly industrial shortfall on the reference network, with the mean, the lowest and the
    highest of the eleven networks. 12 Nov 2026 (the author's note): a table of Section S6 of the SI (it was the table
    of the main text);''',
       '''    """The monthly path of German industrial production in 2026: the path that the published specification implies for
    the low-water days of 2026, and the model's monthly industrial shortfall on the reference network, with the mean, the
    lowest and the highest of the eleven networks. 12 Nov 2026 (the author's note): a table of the SI (it was the table
    of the main text), in the section on the 2026 season since the protocol of the test left the paper that evening;''')
sub(p, '''    """Sectoral signatures of the 2026 forecast (review 8 Oct, G2/E3): monthly production shortfall of the German sectors on''',
       '''    """The monthly path of the sectors on the river, 2026 (review 8 Oct, G2/E3): monthly production shortfall of the German sectors on''')

sub(HERE / "scenarios" / "draught_table_ledger.csv", "tested at 0.04 and 0.16 (Section S4)", "tested at 0.04 and 0.16 (Section S8)")
print("si_tables.py and scenarios/draught_table_ledger.csv updated")
