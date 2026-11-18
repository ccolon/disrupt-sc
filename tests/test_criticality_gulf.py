"""Gulf criticality builder (studies/hormuz2026/build_criticality_gulf.py, Hormuz node A2, 18 Nov 2026):
the GLORIA 120 -> 19 -> WIOD crosswalk is complete, and the two many-to-one rules (max; output-weighted
mean rounded to the nearest class) behave as documented on a synthetic survey matrix. Needs neither the
data repository nor the Pichler archive."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studies" / "hormuz2026"))

from build_criticality_gulf import GLORIA_19, aggregate, gloria_to_wiod, round_class  # noqa: E402

# the 54 buyer industries of the IHS Markit survey (columns of IHS_Markit_results_compact.csv)
IHS_BUYERS = ["A01", "A02", "A03", "B", "C10-C12", "C13-C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22",
              "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31_C32", "C33", "D35", "E36", "E37-E39",
              "F", "G45", "G46", "G47", "H49", "H50", "H51", "H52", "H53", "I", "J58", "J59_J60", "J61",
              "J62_J63", "K64", "K65", "K66", "L68", "M69_M70", "M71", "M72", "M73", "M74_M75", "N", "O84",
              "P85", "Q", "R_S"]


def test_crosswalk_covers_120_gloria_sectors_once():
    cw = gloria_to_wiod()
    assert len(GLORIA_19) == 19
    assert sum(len(v) for v in GLORIA_19.values()) == 120
    g120 = cw.drop_duplicates("gloria120")
    assert len(g120) == 120 and g120["gloria120"].is_unique
    assert set(cw["wiod"]) <= set(IHS_BUYERS)          # every member is rated as a buyer


def test_crosswalk_judgment_calls():
    cw = gloria_to_wiod()
    members = cw.groupby("gloria19")["wiod"].apply(set).to_dict()
    assert members["Refining"] == {"C19"} and members["Fertilizer"] == {"C20"}
    assert members["Oil"] == members["Gas"] == members["Coal"] == members["Mining"] == {"B"}
    assert members["Other utility"] == {"D35", "E37-E39"} and members["Water"] == {"E36"}
    assert "C20" in members["Other manufacturing"] and "C19" not in members["Other manufacturing"]
    assert "H53" in members["Services"] and "H53" not in members["Transport"]


@pytest.mark.parametrize("v,c", [(0.0, 0.0), (0.2499, 0.0), (0.25, 0.5), (0.7499, 0.5), (0.75, 1.0), (1.0, 1.0)])
def test_round_class_nearest(v, c):
    assert round_class(v) == c


def test_max_and_output_weighted_rules():
    ihs = pd.DataFrame([[1.0, 0.0, 0.5],
                        [0.0, 0.0, np.nan],
                        [0.5, 1.0, 1.0]], index=["a1", "a2", "b1"], columns=["a1", "a2", "b1"])
    go = pd.Series({"a1": 3.0, "a2": 1.0, "b1": 1.0})
    members = {"A": ["a1", "a2"], "B": ["b1"]}
    mx, ow, n_unrated = aggregate(ihs, members, go, ["A", "B"])
    assert n_unrated == 0
    assert mx.at["A", "A"] == 1.0                          # one critical sub-pair makes the cell critical
    assert ow.at["A", "A"] == pytest.approx(9 / 16)        # weights 9, 3, 3, 1 on ratings 1, 0, 0, 0
    assert round_class(ow.at["A", "A"]) == 0.5
    assert mx.at["A", "B"] == 0.5                          # the unrated (a2, b1) pair is left out
    assert ow.at["A", "B"] == pytest.approx(0.5)
    assert ow.at["B", "A"] == pytest.approx((3 * 0.5 + 1 * 1.0) / 4)
    assert (mx.values >= ow.values - 1e-12).all()          # the max dominates any weighted mean


def test_all_unrated_cell_is_critical():
    ihs = pd.DataFrame([[np.nan]], index=["a1"], columns=["a1"])
    mx, ow, n_unrated = aggregate(ihs, {"A": ["a1"]}, pd.Series({"a1": 1.0}), ["A"])
    assert n_unrated == 1 and mx.at["A", "A"] == 1.0 and ow.at["A", "A"] == 1.0
