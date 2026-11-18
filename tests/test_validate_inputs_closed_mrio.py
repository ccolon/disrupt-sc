"""validate-inputs and closed MRIO tables (KI-61, 18 Nov 2026).

A closed MRIO has no import rows and no export column: every region is a
firm/household region and the scope has no country agent (the Gulf scope's
GLORIA 15-region table). The loader and the run accept it; the validator used
to reject it ("no import supply", "no export column"), so a valid closed scope
could not pass the pre-run check. A closed table now passes with a warning when
it is valid, and fails when it cannot be balanced (no export cell to pad).
A half-open table (one side missing) stays an error.
"""

from __future__ import annotations

from disruptsc.network.mrio import Mrio
from disruptsc.validate_inputs import _check_mrio

_CFG = {"monetary_units_in_data": "mUSD"}


def _write(tmp_path, header0, header1, rows, name="mrio.csv"):
    lines = [",".join(header0), ",".join(header1)] + [",".join(map(str, r)) for r in rows]
    path = tmp_path / name
    path.write_text("\n".join(lines) + "\n")
    return path


def _closed(tmp_path, b_y_to_a_x=1):
    # Two regions x two sectors, household final demand, a value-added row; no
    # import row, no export column. Every region_sector: output >= input.
    h0 = ["", "", "A", "A", "B", "B", "A", "B"]
    h1 = ["", "", "X", "Y", "X", "Y", "final_demand", "final_demand"]
    rows = [
        ["A", "X", 10, 5, 4, 1, 50, 10],
        ["A", "Y", 3, 8, 2, 2, 40, 5],
        ["B", "X", 2, 1, 9, 4, 6, 60],
        ["B", "Y", b_y_to_a_x, 2, 3, 7, 4, 50],
        ["", "value_added", 60, 50, 40, 70, "", ""],
    ]
    return _write(tmp_path, h0, h1, rows)


def test_closed_balanced_mrio_passes_with_a_warning(tmp_path):
    path = _closed(tmp_path)
    mrio = Mrio.load(path)                       # what the run loads
    assert not mrio.import_label and not mrio.export_label
    assert mrio.external_buying_countries == [] and mrio.external_selling_countries == []
    errors, warnings = [], []
    assert _check_mrio(path, _CFG, errors, warnings) is not None
    assert errors == []
    assert any("closed" in w for w in warnings)


def test_closed_mrio_that_cannot_be_balanced_is_an_error(tmp_path):
    # A_X buys 1,000 from B_Y but sells 80: input > output, and no export cell to pad.
    path = _closed(tmp_path, b_y_to_a_x=1000)
    errors, warnings = [], []
    _check_mrio(path, _CFG, errors, warnings)
    assert any("closed" in e and "input > output" in e for e in errors)


def test_half_open_mrio_is_still_an_error(tmp_path):
    # An export column but no import supply: a missed label, not a closed table.
    h0 = ["", "", "A", "A", "A", "ROW"]
    h1 = ["", "", "X", "Y", "final_demand", "exports"]
    rows = [
        ["A", "X", 10, 5, 50, 20],
        ["A", "Y", 3, 8, 40, 10],
        ["", "value_added", 72, 50, "", ""],
    ]
    path = _write(tmp_path, h0, h1, rows)
    errors, warnings = [], []
    _check_mrio(path, _CFG, errors, warnings)
    assert any("no import supply" in e for e in errors)
    assert not any("closed" in w for w in warnings)


def test_open_mrio_is_unchanged(tmp_path):
    # Testkistan layout: an imports row and an exports column.
    h0 = ["country", "sector", "T", "T", "T", "FOREIGN"]
    h1 = ["", "", "M", "A", "final_demand", "exports"]
    rows = [
        ["T", "M", 500, 200, 800, 100],
        ["T", "A", 150, 300, 600, 50],
        ["FOREIGN", "imports", 10, 5, 0, 0],
        ["", "value_added", 940, 700, "", ""],
    ]
    path = _write(tmp_path, h0, h1, rows)
    errors, warnings = [], []
    _check_mrio(path, _CFG, errors, warnings)
    assert errors == []
    assert not any("closed" in w for w in warnings)
