"""KI-58 (14 Nov 2026): a link with a zero delivery reaches the transport-cost check when its supplier's stock is
empty and its main route is closed (Cambodia, 30-day back-to-back closures). The relative increase must not raise
then, must not depend on the tonnage, and a positive delivery without tonnage must still be caught."""
import pytest

from disruptsc.network.commercial_link import CommercialLink


def _link(delivery, tons):
    return CommercialLink(pid="s->b", supplier_id="s", buyer_id="b", delivery=delivery, delivery_in_tons=tons,
                          route_cost_per_ton=2.0, alternative_route_cost_per_ton=5.0)


def test_zero_delivery_gives_the_per_ton_increase():
    assert _link(0.0, 0.0).calculate_relative_increase_in_transport_cost() == pytest.approx(1.5)


def test_tonnage_does_not_change_the_increase():
    assert _link(10.0, 4.0).calculate_relative_increase_in_transport_cost() == pytest.approx(1.5)


def test_positive_delivery_without_tonnage_still_raises():
    with pytest.raises(ValueError, match="delivery_in_tons is 0"):
        _link(1e-3, 0.0).calculate_relative_increase_in_transport_cost()


def test_cheaper_detour_is_no_increase():
    link = _link(0.0, 0.0)
    link.alternative_route_cost_per_ton = 1.0
    assert link.calculate_relative_increase_in_transport_cost() == 0.0
