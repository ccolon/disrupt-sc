"""KI-59 fixture: can households-first rationing settle a supplier loop into a lower state?

Written first for allocation_priority (Hormuz 2026 MC2, 18 Nov 2026), whose pre-registered
rule reads: if this fixture settles into a lower state, work on allocation_priority stops and
the rule becomes a decision for the lead author before any use.

KI-59 hypothesis (onboarding/references/known-issues.md, Cambodia panel round 1, 16 Nov 2026):
a firm whose output falls below its household orders delivers exactly 0 to its firm clients
under household_first (equal rationing never reaches 0), and a supplier loop at 0 under strict
Leontief stays at 0.

Minimal loop (every number a fixture choice, not data), one region R, strict Leontief:

    A (R_SA) --0.5/unit of B--> B (R_SB) --0.4/unit of A--> A ;  A --> household hh, 60/step
    equilibrium: A produces 75 (60 to hh, 15 to B), B produces 30 (all to A); both hold two
    steps of their input.

Shock: A's productivity falls by half from t=1 for 10 steps (`productivity_shock`), so its
output (at most 75/0.8 x 0.5 with all idle capital mobilized) is below its household orders.
Three allocation arms, all with existing code (rationing_mode is passed to every step):

* equal       - equal rationing throughout (the control);
* hh_first    - household_first throughout (the global rationing_mode of today);
* hh_window   - household_first during the shock window only, equal afterwards. B has no
                household client, so household_first changes A's allocation only: this arm is
                exactly a scoped (region R x sector SA), timed allocation_priority household_first.

"Settled" = back on the undisturbed path at the horizon (104 steps): both firms at their
equilibrium output and no household loss. "Lower state" = stationary but below it.

Outcome (18 Nov 2026): equal rationing recovers (on the path by t=30). Under hh_first and
hh_window A ships 0 to B from t=1, B's stock of A's good runs out (B at 0 from t=3), A's
stock of B's good runs out (A at 0 from t=8), and the loop stays at 0 to t=104 with the
whole household demand lost (60 a step): the KI-59 symptom, absorbing at zero. A window that
ends while the loop still delivers (the same shock over 6 steps) recovers. Per the rule,
allocation_priority was not implemented.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from disruptsc.agents.firm import Firm
from disruptsc.agents.household import Household
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.sc_network import ScNetwork
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import SimParams, TransportParams
from disruptsc.run_pipeline.disruption import parse_disruptions
from disruptsc.run_pipeline.simulate import _run_one_time_step, set_initial_conditions

HORIZON = 104
SHOCK = [{"type": "productivity_shock", "description_type": "filter", "productivity_reduction": 0.5,
          "filter": {"sector": ["SA"]}, "start_time": 1, "duration": 10}]
WINDOW = range(1, 11)


def _loop():
    a = Firm(pid="A", region="R", sector="SA", sector_type="service", region_sector="R_SA",
             input_mix={"R_SB": 0.4}, inventory_duration_target={"R_SB": 2.0}, inventory_restoration_time=4.0)
    b = Firm(pid="B", region="R", sector="SB", sector_type="service", region_sector="R_SB",
             input_mix={"R_SA": 0.5}, inventory_duration_target={"R_SA": 2.0}, inventory_restoration_time=4.0)
    a.suppliers = {"B": {"sector": "R_SB", "weight": 1.0, "satisfaction": 1.0}}
    b.suppliers = {"A": {"sector": "R_SA", "weight": 1.0, "satisfaction": 1.0}}
    hh = Household(pid="hh", region="R", sector_consumption={"R_SA": 60.0},
                   retailers={"A": {"sector": "R_SA", "weight": 1.0}})
    sc = ScNetwork()
    for supplier, buyer, weight, category in ((a, b, 0.5, "domestic_B2B"), (b, a, 0.4, "domestic_B2B"),
                                              (a, hh, 1.0, "domestic_B2C")):
        sc.add_edge(supplier, buyer, weight=weight, object=CommercialLink(
            pid=f"{supplier.pid}->{buyer.pid}", supplier_id=supplier.pid, buyer_id=buyer.pid,
            product=supplier.region_sector, product_type="service", category=category))
        supplier.clients[buyer.pid] = {"sector": getattr(buyer, "sector", "households"), "share": 0.0}
    return sc, {"A": a, "B": b}, {"hh": hh}


def _run(arm: str, shock=SHOCK, horizon=HORIZON, window=WINDOW):
    equal = TransportParams(with_transport=False, transport_to_households=False,
                            rationing_mode="equal", monetary_units="USD")
    hh_first = replace(equal, rationing_mode="household_first")
    sp = SimParams(time_resolution="week", epsilon_stop=0.0, propagate_input_price_change=False)
    sc, firms, households = _loop()
    set_initial_conditions(sc, firms, households, {}, equal, sp)
    disruptions = parse_disruptions(shock, None, None, firms, "USD") if shock else []
    tn = TransportNetwork()
    path = []
    for t in range(horizon + 1):
        if arm == "hh_first" or (arm == "hh_window" and t in window):
            tp = hh_first
        else:
            tp = equal
        _run_one_time_step(t, sc, tn, tn, firms, households, {}, tp, sp,
                           disruptions=disruptions if t > 0 else [])
        path.append({"t": t, "A": firms["A"].production, "B": firms["B"].production,
                     "A_to_B": sc[firms["A"]][firms["B"]]["object"].delivery,
                     "loss": households["hh"].consumption_loss})
    return path, firms


def _settled(path, firms, tol=1e-6):
    last = path[-1]
    return (abs(last["A"] - firms["A"].eq_production) <= tol * firms["A"].eq_production
            and abs(last["B"] - firms["B"].eq_production) <= tol * firms["B"].eq_production
            and last["loss"] <= tol)


def test_undisturbed_loop_is_a_fixed_point():
    path, firms = _run("hh_first", shock=None, horizon=10)
    assert firms["A"].eq_production == pytest.approx(75.0) and firms["B"].eq_production == pytest.approx(30.0)
    assert all(r["A"] == pytest.approx(75.0) and r["B"] == pytest.approx(30.0) and r["loss"] == 0 for r in path)


def test_equal_rationing_recovers_after_the_shock():
    path, firms = _run("equal")
    assert min(r["A_to_B"] for r in path if r["t"] in WINDOW) > 0.0   # equal rationing never reaches 0
    assert _settled(path, firms)


# KI-59 symptom, reproduced on this fixture 18 Nov 2026 (see the module docstring). These two
# tests pin it: they assert the lower state. When KI-59 is resolved they fail and must be turned
# into recovery tests.
@pytest.mark.parametrize("arm", ["hh_first", "hh_window"])
def test_ki59_household_first_settles_the_loop_into_a_lower_state(arm):
    path, firms = _run(arm)
    window = [r for r in path if r["t"] in WINDOW]
    assert all(r["A_to_B"] == 0.0 for r in window)                  # A's output < its household orders
    assert not _settled(path, firms)
    tail = path[-20:]
    assert all(r["A"] == tail[-1]["A"] and r["B"] == tail[-1]["B"] for r in tail)   # stationary
    assert tail[-1]["A"] < firms["A"].eq_production and tail[-1]["loss"] > 0.0      # ... and lower


def test_a_household_first_window_that_ends_while_the_loop_still_delivers_recovers():
    path, firms = _run("hh_window", shock=[dict(SHOCK[0], duration=6)], window=range(1, 7))
    assert min(r["A"] for r in path) == 0.0                           # the loop touched zero (t=8) ...
    assert _settled(path, firms)                                      # ... and came back
