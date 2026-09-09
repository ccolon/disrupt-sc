"""Input pooling across regions (Rhine study, 9 Sep 2026).

Inputs of the same product from several regions may share a pool: their stocks and
coefficients are summed in the production constraint, a multi-region pool draws from its
members in proportion to their stocks, and the pool's order is split across all its
suppliers by baseline share x fill-rate signal. Without pools every input is its own
pool and the legacy region-keyed behaviour is unchanged.
"""
import math

from disruptsc.agents.firm import Firm


def _make_firm(eq=100.0):
    f = Firm(pid="f1", region="AUT", sector="H49", sector_type="transport", region_sector="AUT_H49")
    f.utilization_rate = 0.8
    f.initialize_production(eq)
    f.production_target = 100.0
    return f


def _two_region_fuel(f, deu_stock, aut_stock, pooled=True):
    f.input_mix = {"DEU_C19": 0.10, "AUT_C19": 0.05, "DEU_C28": 0.02}
    f.inventory = {"DEU_C19": deu_stock, "AUT_C19": aut_stock, "DEU_C28": 10.0}
    f.input_criticality = {"DEU_C19": 1.0, "AUT_C19": 1.0, "DEU_C28": 1.0}
    f.input_pools = {"DEU_C19": "C19", "AUT_C19": "C19"} if pooled else {}


def test_region_keyed_rule_stops_when_one_region_is_empty():
    f = _make_firm()
    _two_region_fuel(f, deu_stock=0.0, aut_stock=20.0, pooled=False)
    f.produce()
    assert f.production == 0.0                       # DEU fuel missing binds although AUT fuel is in stock


def test_pooled_product_uses_the_other_region_stock():
    f = _make_firm()
    _two_region_fuel(f, deu_stock=0.0, aut_stock=20.0, pooled=True)
    f.produce()
    assert math.isclose(f.production, 100.0)         # pooled: 20 / (0.10 + 0.05) = 133 > target 100
    assert math.isclose(f.inventory["AUT_C19"], 20.0 - 0.15 * 100.0)   # drawn from the region that has stock
    assert f.inventory["DEU_C19"] == 0.0


def test_pooled_stock_binds_on_the_sum():
    f = _make_firm()
    _two_region_fuel(f, deu_stock=3.0, aut_stock=3.0, pooled=True)
    f.produce()
    assert math.isclose(f.production, 6.0 / 0.15)    # 40: the pooled stock over the pooled coefficient
    assert math.isclose(f.inventory["DEU_C19"] + f.inventory["AUT_C19"], 0.0, abs_tol=1e-9)


def test_differentiated_input_stays_region_keyed():
    f = _make_firm()
    _two_region_fuel(f, deu_stock=20.0, aut_stock=20.0, pooled=True)
    f.inventory["DEU_C28"] = 0.0                      # machinery from DEU: its own pool, critical
    f.produce()
    assert f.production == 0.0


def _ordering_firm():
    f = _make_firm()
    f.input_mix = {"DEU_C19": 0.10, "AUT_C19": 0.05}
    f.eq_needs = {"DEU_C19": 10.0, "AUT_C19": 5.0}
    f.input_needs = {"DEU_C19": 10.0, "AUT_C19": 5.0}
    f.inventory_duration_target = {"DEU_C19": 1.0, "AUT_C19": 1.0}
    f.inventory_restoration_time = 1.0
    f.inventory = {"DEU_C19": 10.0, "AUT_C19": 5.0}   # at target: orders = needs
    f.suppliers = {"deu": {"sector": "DEU_C19", "weight": 1.0}, "aut": {"sector": "AUT_C19", "weight": 1.0}}
    f.input_pools = {"DEU_C19": "C19", "AUT_C19": "C19"}
    return f


def test_pool_orders_split_by_baseline_share_at_equilibrium():
    f = _ordering_firm()
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=True)
    assert math.isclose(f.purchase_plan["deu"], 10.0) and math.isclose(f.purchase_plan["aut"], 5.0)


def test_pool_orders_move_to_the_region_that_delivers():
    f = _ordering_firm()
    f.suppliers["deu"]["satisfaction"] = 0.0         # DEU refinery delivered nothing (fill-rate signal)
    f.inventory = {"DEU_C19": 0.0, "AUT_C19": 5.0}   # pooled stock 5 of a pooled target 15
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=True)
    assert f.purchase_plan["deu"] == 0.0
    assert math.isclose(f.purchase_plan["aut"], 15.0 + 10.0)   # needs 15 + restoration of the pooled stock (15 - 5) / 1


def test_single_input_pool_is_the_legacy_rule():
    f = _ordering_firm()
    f.input_pools = {}
    f.suppliers["deu"]["satisfaction"] = 0.5
    f._decide_purchase_plan(adaptive_inventories=False, adaptive_weight=True)
    # one supplier per input: the satisfaction cancels in the share, the order is the input's own need
    assert math.isclose(f.purchase_plan["deu"], 10.0) and math.isclose(f.purchase_plan["aut"], 5.0)
