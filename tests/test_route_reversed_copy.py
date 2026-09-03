"""Route.reversed_copy replaces deepcopy+revert on the route-cache path.

deepcopy of a Route (a list subclass with pickle hooks) ran __setstate__ and
then re-appended the original items, so the copy's list part was doubled; it
also cost ~90 minutes for the 763k routes of the EU scope. The cheap rebuild
from the four stored fields must be an exact reversal.
"""

import copy
import pickle

import networkx as nx

from disruptsc.network.route import Route


def _network():
    tn = nx.Graph()
    tn.add_edge(1, 2, id=10, type="roads", km=5.0)
    tn.add_edge(2, 3, id=11, type="multimodal", km=1.0)
    tn.add_edge(3, 4, id=12, type="railways", km=7.0)
    return tn


def test_reversed_copy_is_an_exact_reversal():
    tn = _network()
    r = Route([1, 2, 3, 4], tn, "container")
    rev = r.reversed_copy()
    assert rev.transport_nodes == [4, 3, 2, 1]
    assert rev.transport_edges == [(4, 3), (3, 2), (2, 1)]
    assert rev.transport_edge_ids == [12, 11, 10]
    assert set(rev.transport_modes) == set(r.transport_modes)
    assert rev.length == r.length == 13.0
    # list part = alternating nodes/edges, NOT doubled
    assert len(rev) == len(r) == 7
    assert list(rev) == [(4,), (4, 3), (3,), (3, 2), (2,), (2, 1), (1,)]
    # the original is untouched
    assert r.transport_nodes == [1, 2, 3, 4]


def test_reversed_copy_matches_pickle_roundtrip_of_reverted_route():
    tn = _network()
    r = Route([1, 2, 3, 4], tn, "container")
    via_pickle = pickle.loads(pickle.dumps(r))
    via_pickle.revert()
    rev = r.reversed_copy()
    assert list(rev) == list(via_pickle)
    assert rev.transport_edges == via_pickle.transport_edges
    assert rev.transport_edge_ids == via_pickle.transport_edge_ids


def test_deepcopy_doubling_is_documented_not_relied_upon():
    # Pin the behaviour the cache path used to depend on, so a future change
    # to the pickle hooks that fixes it does not silently break assumptions.
    tn = _network()
    r = Route([1, 2, 3], tn, "container")
    d = copy.deepcopy(r)
    assert d.transport_edges == r.transport_edges
    assert len(d) in (5, 10)
