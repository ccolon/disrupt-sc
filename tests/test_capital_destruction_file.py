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
    place_reconstruction_demand, rebuild_from_reconstruction, rebuild_public_capital,
)


def _make_firm(pid, canton, sector, eq=100.0, capital=300.0):
    f = Firm(pid=pid, region="ECU", sector=sector, sector_type="service",
             region_sector=f"ECU_{sector}", subregions={"subregion_canton": canton})
    f.utilization_rate = 1.0
    f.initialize_production(eq)            # production_capacity = eq (utilization 1)
    f.capital_initial = capital
    f.initialize_capital()                 # active = capital, idle = 0 (utilization 1)
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


# ---------------------------------------------------------------------------
# Active / idle capital — mobilizable spare capacity (utilization < 1)
# ---------------------------------------------------------------------------

def _make_firm_util(util, eq=100.0, capital=1000.0):
    f = Firm(pid="f", region="ECU", sector="CON", sector_type="construction",
             region_sector="ECU_CON", subregions={"subregion_canton": "D"})
    f.utilization_rate = util
    f.initialize_production(eq)
    f.capital_initial = capital
    f.initialize_capital()
    return f


def test_capital_split_and_resting_capacity():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    assert math.isclose(f.active_capital, 800.0)          # utilization * capital
    assert math.isclose(f.idle_capital, 200.0)
    assert math.isclose(f.production_capacity, 125.0)     # eq / utilization (physical max)
    assert math.isclose(f.current_production_capacity, 100.0)  # rests at eq, not the ceiling


def test_mobilize_idle_capital_booms_to_ceiling():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    f.production_target = 125.0                            # demand at the physical ceiling
    f.adjust_active_capital(activation_fraction=1.0)       # tau <= step -> full mobilization
    assert math.isclose(f.active_capital, 1000.0)
    assert math.isclose(f.idle_capital, 0.0)
    assert math.isclose(f.current_production_capacity, 125.0)   # boomed +25% above eq


def test_mobilize_is_rate_limited_and_geometric():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    f.production_target = 125.0
    f.adjust_active_capital(activation_fraction=0.5)       # only half the idle per step
    assert math.isclose(f.active_capital, 900.0)           # 800 + 0.5*200
    assert math.isclose(f.current_production_capacity, 112.5)
    f.adjust_active_capital(activation_fraction=0.5)       # 0.5 of the *remaining* idle
    assert math.isclose(f.active_capital, 950.0)           # 900 + 0.5*100
    assert math.isclose(f.current_production_capacity, 118.75)


def test_mobilize_capped_by_demand_not_overshooting():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    f.production_target = 110.0                            # modest surge, below the ceiling
    f.adjust_active_capital(activation_fraction=1.0)
    assert math.isclose(f.current_production_capacity, 110.0)   # exactly meets target
    assert math.isclose(f.idle_capital, 120.0)            # only 80 of idle mobilized


def test_deactivate_when_target_falls_below_capacity():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    f.production_target = 110.0
    f.adjust_active_capital(activation_fraction=1.0)       # active 880, idle 120
    f.production_target = 100.0                            # demand back to normal
    f.adjust_active_capital(activation_fraction=1.0)       # mothball the surplus
    assert math.isclose(f.active_capital, 800.0)
    assert math.isclose(f.idle_capital, 200.0)
    assert math.isclose(f.current_production_capacity, 100.0)


def test_destruction_hits_active_and_idle_alike():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    f.incur_capital_destruction(100.0)                    # destroy 10% of total capital
    assert math.isclose(f.active_capital, 720.0)          # 800 * 0.9
    assert math.isclose(f.idle_capital, 180.0)            # 200 * 0.9
    assert math.isclose(f.current_production_capacity, 90.0)    # eq * (1 - 0.1)
    assert math.isclose(f.capital_destroyed, 100.0)       # derived property


def test_rebuild_restores_active_first_then_idle():
    f = _make_firm_util(0.8, eq=100.0, capital=1000.0)
    f.incur_capital_destruction(100.0)                    # active 720, idle 180, missing 100
    f.rebuild_capital(50.0)                               # active-first up to active_0 = 800
    assert math.isclose(f.active_capital, 770.0)
    assert math.isclose(f.idle_capital, 180.0)
    assert math.isclose(f.capital_destroyed, 50.0)
    f.rebuild_capital(100.0)                              # tops active to 800, spills 20 into idle
    assert math.isclose(f.active_capital, 800.0)
    assert math.isclose(f.idle_capital, 200.0)
    assert math.isclose(f.capital_destroyed, 0.0, abs_tol=1e-9)  # fully restored to the split
    assert math.isclose(f.current_production_capacity, 100.0)


# ---------------------------------------------------------------------------
# Public reconstruction share — rebuilt directly, no private B2B trace
# ---------------------------------------------------------------------------

def test_public_share_splits_private_b2b_and_direct_rebuild():
    a = _make_firm("a", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(30.0)                         # capital_destroyed = 30
    con = _make_firm("c", "X - Y", "CON", eq=100.0, capital=10.0)
    firms = {"a": a, "c": con}

    # 80% public: private B2B demand is only 20% of the 30/10 = 3.0 rebuild rate
    place_reconstruction_demand(firms, 10, {"CON": 1.0}, public_share=0.8)
    assert math.isclose(a.capital_demanded, 0.6)              # 0.2 * 3.0 -> private
    assert math.isclose(a.public_capital_demanded, 2.4)      # 0.8 * 3.0 -> public
    assert math.isclose(con.reconstruction_demand, 0.6)      # only the private share hits CON firms

    # public rebuild restores capital directly, no firm output consumed
    con.product_stock = 0.0                                   # no private output available
    rebuild_from_reconstruction(firms, {"CON": 1.0})         # private rebuild = 0 (no stock)
    built = rebuild_public_capital(firms)
    assert math.isclose(built, 2.4)
    assert math.isclose(a.capital_destroyed, 27.6)           # 30 - 2.4 rebuilt publicly


def test_public_share_one_places_no_b2b_demand():
    a = _make_firm("a", "MANABI - PORTOVIEJO", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(30.0)
    con = _make_firm("c", "X - Y", "CON", eq=100.0, capital=10.0)
    firms = {"a": a, "c": con}
    agg = place_reconstruction_demand(firms, 10, {"CON": 1.0}, public_share=1.0)
    assert math.isclose(agg, 0.0)                             # no private aggregate
    assert math.isclose(con.reconstruction_demand, 0.0)      # nothing on the firm network
    assert math.isclose(a.public_capital_demanded, 3.0)      # all public
    rebuild_public_capital(firms)
    assert math.isclose(a.capital_destroyed, 27.0)           # 30 - 3.0


# ---------------------------------------------------------------------------
# Localized reconstruction — route rebuild demand toward firms near the damage
# ---------------------------------------------------------------------------

def test_localized_reconstruction_routes_demand_to_damaged_regions():
    a = _make_firm("a", "D", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(30.0)                      # capital_demanded = 30/10 = 3
    con_d = _make_firm("cd", "D", "CON", eq=50.0, capital=10.0)   # in damaged region D
    con_u = _make_firm("cu", "U", "CON", eq=50.0, capital=10.0)   # in undamaged region U
    firms = {"a": a, "cd": con_d, "cu": con_u}
    damage = {"D": 30.0}                                   # only region D was damaged

    # locality 0 -> national by size -> equal split (con firms are the same size)
    place_reconstruction_demand(firms, 10, {"CON": 1.0}, locality=0.0,
                                damage_by_region=damage, region_key="subregion_canton")
    assert math.isclose(con_d.reconstruction_demand, 1.5)
    assert math.isclose(con_u.reconstruction_demand, 1.5)

    # locality 1 -> all rebuild demand to the firm in the damaged region
    place_reconstruction_demand(firms, 10, {"CON": 1.0}, locality=1.0,
                                damage_by_region=damage, region_key="subregion_canton")
    assert math.isclose(con_d.reconstruction_demand, 3.0)
    assert math.isclose(con_u.reconstruction_demand, 0.0)

    # locality 0.5 -> blend: 0.5*1.5 + 0.5*3.0 and 0.5*1.5 + 0.5*0.0
    place_reconstruction_demand(firms, 10, {"CON": 1.0}, locality=0.5,
                                damage_by_region=damage, region_key="subregion_canton")
    assert math.isclose(con_d.reconstruction_demand, 2.25)
    assert math.isclose(con_u.reconstruction_demand, 0.75)


def test_localized_reconstruction_is_per_sector():
    a = _make_firm("a", "D", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(100.0)                     # capital_demanded = 10
    con_d = _make_firm("cd", "D", "CON", eq=50.0, capital=10.0)
    con_u = _make_firm("cu", "U", "CON", eq=50.0, capital=10.0)
    man_d = _make_firm("md", "D", "MAN", eq=50.0, capital=10.0)
    man_u = _make_firm("mu", "U", "MAN", eq=50.0, capital=10.0)
    firms = {"a": a, "cd": con_d, "cu": con_u, "md": man_d, "mu": man_u}
    damage = {"D": 100.0}

    # CON fully local, MAN national -> CON concentrates, MAN stays split by size
    place_reconstruction_demand(firms, 10, {"CON": 0.7, "MAN": 0.3},
                                locality={"CON": 1.0, "MAN": 0.0},
                                damage_by_region=damage, region_key="subregion_canton")
    assert math.isclose(con_d.reconstruction_demand, 7.0)  # all CON (0.7*10) to damaged region
    assert math.isclose(con_u.reconstruction_demand, 0.0)
    assert math.isclose(man_d.reconstruction_demand, 1.5)  # MAN (0.3*10) split 50:50 nationally
    assert math.isclose(man_u.reconstruction_demand, 1.5)


def test_localized_reconstruction_falls_back_to_national_without_local_supply():
    a = _make_firm("a", "D", "INM", eq=100.0, capital=300.0)
    a.incur_capital_destruction(30.0)
    con_u = _make_firm("cu", "U", "CON", eq=50.0, capital=10.0)
    con_v = _make_firm("cv", "V", "CON", eq=50.0, capital=10.0)  # both CON firms outside damage
    firms = {"a": a, "cu": con_u, "cv": con_v}
    damage = {"D": 30.0}                                   # damaged region has NO capital-good firm

    place_reconstruction_demand(firms, 10, {"CON": 1.0}, locality=1.0,
                                damage_by_region=damage, region_key="subregion_canton")
    # no local supply -> fall back to national split rather than starving the sector
    assert math.isclose(con_u.reconstruction_demand, 1.5)
    assert math.isclose(con_v.reconstruction_demand, 1.5)


def test_parse_disruptions_precomputes_damage_by_region_and_locality(tmp_path):
    firms = {
        "f1": _make_firm("f1", "MANABI - PORTOVIEJO", "INM", capital=300.0),
        "f2": _make_firm("f2", "MANABI - MANTA", "COM", capital=300.0),
        "f3": _make_firm("f3", "ESMERALDAS - ATACAMES", "COM", capital=300.0),
    }
    for pid, prov in (("f1", "MANABI"), ("f2", "MANABI"), ("f3", "ESMERALDAS")):
        firms[pid].subregions["subregion_province"] = prov
    csv = _write_csv(tmp_path, [
        ["MANABI - PORTOVIEJO", "INM", 30.0],
        ["MANABI - MANTA", "COM", 20.0],
        ["ESMERALDAS - ATACAMES", "COM", 5.0],
    ])
    cfg = [{
        "type": "capital_destruction", "description_type": "subregion_file",
        "file": str(csv), "unit": "mUSD", "start_time": 1,
        "reconstruction_market": True, "reconstruction_locality": {"CON": 0.8},
    }]
    d = parse_disruptions(cfg, None, None, firms, "mUSD")[0]
    assert d.reconstruction_locality == {"CON": 0.8}
    assert d.reconstruction_region_key == "subregion_province"          # default
    assert math.isclose(d.damage_by_region["MANABI"], 50.0)             # 30 + 20
    assert math.isclose(d.damage_by_region["ESMERALDAS"], 5.0)


# ---------------------------------------------------------------------------
# Day -> time-step unit conversion (config gives DAYS; code converts to steps)
# ---------------------------------------------------------------------------

def test_reconstruction_target_time_days_to_steps(tmp_path):
    firms = {"f1": _make_firm("f1", "MANABI - PORTOVIEJO", "INM")}
    csv = _write_csv(tmp_path, [["MANABI - PORTOVIEJO", "INM", 30.0]])
    cfg = [{
        "type": "capital_destruction", "description_type": "subregion_file",
        "file": str(csv), "unit": "mUSD", "start_time": 1,
        "reconstruction_market": True, "reconstruction_target_time": 70,  # DAYS
    }]
    d_week = parse_disruptions(cfg, None, None, firms, "mUSD", time_resolution="week")[0]
    assert math.isclose(d_week.reconstruction_target_time, 70 / 7)         # 70 days -> 10 weeks
    d_day = parse_disruptions(cfg, None, None, firms, "mUSD", time_resolution="day")[0]
    assert math.isclose(d_day.reconstruction_target_time, 70.0)            # identity at daily


def test_inventory_restoration_time_days_to_steps():
    from disruptsc.config import build_params
    base = {"flow_coverage": 0.9, "inventory_restoration_time": 90}        # DAYS
    _, _, ap_week, _ = build_params({**base, "time_resolution": "week"})
    assert math.isclose(ap_week.inventory_restoration_time, 90 / 7)
    _, _, ap_day, _ = build_params({**base, "time_resolution": "day"})
    assert math.isclose(ap_day.inventory_restoration_time, 90.0)
