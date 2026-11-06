"""KI-50 (6 Nov 2026): cached detours are forgotten whenever the set of closed edges changes, and in the reset.

Before, the 'alternative*' route libraries were cleared only when a cost shock started or ended. A detour cached
under one closure set was reused under another while it stayed open (KI-42 keeps closed edges out), even when a
cheaper path existed - successive floods reused the first event's detours - and it carried from one run to the
next on the same build.
"""
from __future__ import annotations

from disruptsc.network.transport_network import TransportNetwork
from disruptsc.run_pipeline.disruption import Recovery, TransportDisruption

CT = "dry_bulk"


def _network() -> TransportNetwork:
    tn = TransportNetwork()
    tn.cargo_types = [CT]
    for n in (1, 2, 3):
        tn.add_node(n, id=n, long=float(n), lat=0.0, shipments={}, disruption_duration=0, type="road")
    for u, v, eid in [(1, 2, 1), (2, 3, 2), (1, 3, 3)]:
        tn.add_edge(u, v, id=eid, type="roads", km=100.0, name=f"e{eid}", shipments={},
                    disruption_duration=0, closed=False, **{f"cost_per_ton_{CT}": 10.0})
    tn.shortest_path_library = {"alternative": {CT: {(1, 3): "cached"}}, "normal": {CT: {(1, 3): "kept"}}}
    return tn


def _cached(tn):
    return tn.shortest_path_library["alternative"][CT]


def test_a_closure_start_forgets_the_cached_detours_and_keeps_the_normal_routes():
    tn = _network()
    TransportDisruption(description={2: 1.0}, recovery=Recovery(duration=2)).implement(tn)
    assert _cached(tn) == {} and tn.shortest_path_library["normal"][CT] == {(1, 3): "kept"}


def test_a_reopening_forgets_the_detours_cached_while_closed():
    tn = _network()
    TransportDisruption(description={2: 1.0}, recovery=Recovery(duration=2)).implement(tn)
    _cached(tn)[(1, 3)] = "detour"
    tn.update_road_disruption_state()                  # 2 -> 1 step left: still closed, cache kept
    assert _cached(tn) == {(1, 3): "detour"}
    tn.update_road_disruption_state()                  # reopens
    assert _cached(tn) == {}


def test_the_reset_between_runs_forgets_the_detours():
    tn = _network()
    tn.reinitialize_flows_and_disruptions()
    assert _cached(tn) == {}
