"""Tests for the heterogeneous, absolute, file-based capital-destruction shock.

Locks the adapter path used by the 2016 Ecuador earthquake runs:
``CapitalDestruction.from_subregion_file`` reads a long CSV of
``subregion_canton, sector, destroyed_capital_mUSD``, matches each cell to the
firm(s) in that canton & sector, splits the absolute destroyed capital across
them in proportion to ``capital_initial``, and applies it via
``incur_capital_destruction`` (absolute mode).
"""

import math

import pandas as pd

from disruptsc.agents.firm import Firm
from disruptsc.run_pipeline.disruption import (
    CapitalDestruction, parse_disruptions,
    place_reconstruction_demand, rebuild_from_reconstruction,
)


def _make_firm(pid, canton, sector, eq=100.0, capital=300.0):
    f = Firm(pid=pid, region="ECU", sector=sector, sector_type="service",
             region_sector=f"ECU_{sector}", subregions={"subregion_canton": canton})
    f.utilization_rate = 1.0
    f.initialize_production(eq)            # production_capacity = eq (utilization 1)
    f.capital_initial = capital
    return f


def _write_csv(tmp_path, rows):
    p = tmp_path / "shock.csv"
    pd.DataFrame(rows, columns=["subregion_canton", "sector", "destroyed_capital_mUSD"]).to_csv(p, index=False)
    return p


def test_single_cell_maps_and_reduces_capacity(tmp_path):
    firms = {"f1": _make_firm("f1", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)}
    csv = _write_csv(tmp_path, [["MANABI - PORTOVIEJO", "INM", 30.0]])

    d = CapitalDestruction.from_subregion_file(csv, firms)
    assert d.absolute is True
    assert math.isclose(d.description["f1"], 30.0)
    assert math.isclose(d.applied_capital, 30.0)
    assert d.unmatched_capital == 0.0

    d.implement(firms)
    # reduction = 30/300 = 0.1 -> capacity 90
    assert math.isclose(firms["f1"].current_production_capacity, 90.0)


def test_cell_split_proportional_to_capital(tmp_path):
    firms = {
        "a": _make_firm("a", "MANABI - MANTA", "COM", eq=100.0, capital=300.0),
        "b": _make_firm("b", "MANABI - MANTA", "COM", eq=100.0, capital=100.0),
    }
    csv = _write_csv(tmp_path, [["MANABI - MANTA", "COM", 40.0]])

    d = CapitalDestruction.from_subregion_file(csv, firms)
    # split 300:100 -> 30 and 10; both lose the same 10% of their capital
    assert math.isclose(d.description["a"], 30.0)
    assert math.isclose(d.description["b"], 10.0)

    d.implement(firms)
    assert math.isclose(firms["a"].current_production_capacity, 90.0)
    assert math.isclose(firms["b"].current_production_capacity, 90.0)


def test_unmatched_cell_is_tallied_not_applied(tmp_path):
    firms = {"f1": _make_firm("f1", "MANABI - PORTOVIEJO", "INM")}
    csv = _write_csv(tmp_path, [
        ["MANABI - PORTOVIEJO", "INM", 30.0],
        ["GALAPAGOS - SANTA CRUZ", "INM", 5.0],   # no firm there
        ["MANABI - PORTOVIEJO", "ELE", 7.0],      # canton ok, no ELE firm
    ])

    d = CapitalDestruction.from_subregion_file(csv, firms)
    assert math.isclose(d.applied_capital, 30.0)
    assert math.isclose(d.unmatched_capital, 12.0)   # 5 + 7
    assert set(d.description) == {"f1"}


def test_overflow_when_amount_exceeds_capital(tmp_path):
    firms = {"f1": _make_firm("f1", "MANABI - SUCRE", "INM", eq=100.0, capital=50.0)}
    csv = _write_csv(tmp_path, [["MANABI - SUCRE", "INM", 80.0]])

    d = CapitalDestruction.from_subregion_file(csv, firms)
    assert math.isclose(d.applied_capital, 50.0)      # capped at total capital
    assert math.isclose(d.overflow_capital, 30.0)

    d.implement(firms)
    # reduction capped at 1.0 -> capacity 0
    assert math.isclose(firms["f1"].current_production_capacity, 0.0)


def test_unit_conversion_usd_to_model_musd(tmp_path):
    firms = {"f1": _make_firm("f1", "MANABI - CHONE", "EDU", eq=100.0, capital=300.0)}
    csv = _write_csv(tmp_path, [["MANABI - CHONE", "EDU", 30_000_000.0]])  # USD

    d = CapitalDestruction.from_subregion_file(csv, firms, monetary_units="mUSD", unit="USD")
    assert math.isclose(d.description["f1"], 30.0)    # 30M USD -> 30 mUSD


def test_parse_disruptions_wires_file_mode(tmp_path):
    firms = {"f1": _make_firm("f1", "MANABI - PORTOVIEJO", "INM")}
    csv = _write_csv(tmp_path, [["MANABI - PORTOVIEJO", "INM", 30.0]])
    cfg = [{
        "type": "capital_destruction",
        "description_type": "subregion_file",
        "file": str(csv),
        "unit": "mUSD",
        "start_time": 1,
    }]
    disruptions = parse_disruptions(cfg, transport_edges=None, firm_table=None,
                                    firms=firms, monetary_units="mUSD")
    assert len(disruptions) == 1
    d = disruptions[0]
    assert isinstance(d, CapitalDestruction) and d.absolute is True
    assert d.start_time == 1
    assert math.isclose(d.description["f1"], 30.0)


# ---------------------------------------------------------------------------
# Reconstruction (ARIO-style) — lean functional port of v1.1.6
# ---------------------------------------------------------------------------

def test_rebuild_capital_restores_capacity():
    f = _make_firm("f1", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)
    f.incur_capital_destruction(30.0)
    assert math.isclose(f.current_production_capacity, 90.0)   # reduction 0.1
    f.rebuild_capital(30.0)
    assert math.isclose(f.capital_destroyed, 0.0)
    assert math.isclose(f.current_production_capacity, 100.0)
    f.rebuild_capital(10.0)                                    # clamp at 0
    assert math.isclose(f.capital_destroyed, 0.0)


def test_place_reconstruction_demand_splits_by_mix_and_output():
    a = _make_firm("a", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(30.0)
    con1 = _make_firm("c1", "X - Y", "CON", eq=60.0, capital=10.0)
    con2 = _make_firm("c2", "X - Z", "CON", eq=40.0, capital=10.0)
    firms = {"a": a, "c1": con1, "c2": con2}

    agg = place_reconstruction_demand(firms, reconstruction_target_time=10, capital_input_mix={"CON": 1.0})
    assert math.isclose(agg, 3.0)                              # 30 / 10
    assert math.isclose(a.capital_demanded, 3.0)
    assert math.isclose(a.reconstruction_demand, 0.0)          # INM is not a capital-good sector
    assert math.isclose(con1.reconstruction_demand, 1.8)       # CON demand 3.0 split 60:40 by output
    assert math.isclose(con2.reconstruction_demand, 1.2)


def test_rebuild_from_reconstruction_restores_and_consumes_stock():
    a = _make_firm("a", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(30.0)                          # reduction 0.1, capacity 90
    con = _make_firm("c", "X - Y", "CON", eq=100.0, capital=10.0)
    firms = {"a": a, "c": con}
    place_reconstruction_demand(firms, 10, {"CON": 1.0})       # con.reconstruction_demand=3
    con.product_stock = 5.0                                    # leftover available for reconstruction

    new_cap = rebuild_from_reconstruction(firms, {"CON": 1.0})
    assert math.isclose(con.reconstruction_produced, 3.0)
    assert math.isclose(con.product_stock, 2.0)                # 5 - 3 consumed
    assert math.isclose(new_cap, 3.0)
    assert math.isclose(a.capital_destroyed, 27.0)             # 30 - 3 rebuilt
    assert math.isclose(a.current_production_capacity, 91.0)   # 100 * (1 - 27/300)


def test_reconstruction_leontief_bottleneck_and_import_unconstrained():
    a = _make_firm("a", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(100.0)
    con = _make_firm("c", "X - Y", "CON", eq=1000.0, capital=10.0)
    man = _make_firm("m", "X - Z", "MAN", eq=1000.0, capital=10.0)
    firms = {"a": a, "c": con, "m": man}
    mix = {"CON": 0.7, "MAN": 0.2, "IMP": 0.1}                 # IMP has no firm -> imported
    place_reconstruction_demand(firms, 10, mix)               # agg=10: CON 7, MAN 2
    assert math.isclose(con.reconstruction_demand, 7.0)
    assert math.isclose(man.reconstruction_demand, 2.0)

    con.product_stock = 7.0                                    # CON fully supplied
    man.product_stock = 1.0                                    # MAN supplies only half -> bottleneck
    new_cap = rebuild_from_reconstruction(firms, mix)
    # ratios: CON 7/0.7=10, MAN 1/0.2=5, IMP unconstrained=agg=10 -> min = 5
    assert math.isclose(new_cap, 5.0)
    assert math.isclose(a.capital_destroyed, 95.0)             # 100 - 5
