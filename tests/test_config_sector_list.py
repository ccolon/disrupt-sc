"""sectors_to_exclude parsing (KI-24).

The shipped default.yaml used to say ``sectors_to_exclude: None``; YAML reads
that as the string "None", and ``tuple("None")`` is ('N', 'o', 'n', 'e') -
which silently excluded every sector literally named "N" (ICIO administrative
and support services) from every scope. These tests pin the fix.
"""

import pytest

from disruptsc.config import _parse_sector_list


@pytest.mark.parametrize("raw", [None, "None", "none", "null", "~", "", "  "])
def test_null_like_values_mean_no_exclusion(raw):
    assert _parse_sector_list(raw) == ()


def test_list_is_kept_as_codes():
    assert _parse_sector_list(["N", "T"]) == ("N", "T")
    assert _parse_sector_list(("C19",)) == ("C19",)


def test_bare_string_is_rejected_not_iterated():
    with pytest.raises(ValueError):
        _parse_sector_list("N,T")
