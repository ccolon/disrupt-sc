"""Rationing-mode tests: household_first priority + rejection of unknown modes."""

import math

import pytest

from disruptsc.agents.firm import Firm
from disruptsc.config import build_params


def _supplier(stock, total_order, eq=100.0):
    f = Firm(pid="s", region="ECU", sector="COM", sector_type="trade", region_sector="ECU_COM")
    f.utilization_rate = 1.0
    f.initialize_production(eq)
    f.product_stock = stock
    f.total_order = total_order
    return f


class Household:   # the firm checks client.__class__.__name__ == "Household"
    def __init__(self, pid):
        self.pid = pid


class Other:
    def __init__(self, pid):
        self.pid = pid


class _Link:
    def __init__(self, order):
        self.order = order
        self.delivery = 0.0
        self.delivery_in_tons = 0.0


class _Sc:
    def __init__(self, edges):
        self._edges = edges

    def out_edges(self, firm, data=True):
        return self._edges

    def in_edges(self, firm, data=True):
        return []


def _sc_two_clients(f, hh_order, other_order):
    """Wire two clients and snapshot their orders the way retrieve_orders does:
    deliveries are computed on the retrieved order_book, not on link.order,
    which the next step's purchasing has already overwritten by delivery time."""
    lhh, lo = _Link(hh_order), _Link(other_order)
    f.order_book = {"hh": hh_order, "other": other_order}
    return _Sc([(None, Household("hh"), {"object": lhh}), (None, Other("other"), {"object": lo})]), lhh, lo


def test_household_first_serves_households_before_firms():
    f = _supplier(stock=70.0, total_order=100.0)        # 60 household + 40 firm
    sc, lhh, lo = _sc_two_clients(f, 60.0, 40.0)
    f._evaluate_quantities_to_deliver(sc, "household_first")
    assert math.isclose(lhh.delivery, 60.0)             # household fully served (70 >= 60)
    assert math.isclose(lo.delivery, 10.0)              # firm gets only the 10 remainder


def test_household_first_rations_households_when_stock_below_household_demand():
    f = _supplier(stock=30.0, total_order=100.0)
    sc, lhh, lo = _sc_two_clients(f, 60.0, 40.0)
    f._evaluate_quantities_to_deliver(sc, "household_first")
    assert math.isclose(lhh.delivery, 30.0)             # 30/60 of the household order
    assert math.isclose(lo.delivery, 0.0)               # nothing left for firms


def test_equal_rations_everyone_proportionally():
    f = _supplier(stock=70.0, total_order=100.0)
    sc, lhh, lo = _sc_two_clients(f, 60.0, 40.0)
    f._evaluate_quantities_to_deliver(sc, "equal")
    assert math.isclose(lhh.delivery, 42.0)             # 60 * 0.7
    assert math.isclose(lo.delivery, 28.0)              # 40 * 0.7


def test_unknown_rationing_mode_rejected():
    with pytest.raises(ValueError):
        build_params({"flow_coverage": 0.9, "rationing_mode": "bogus"})
