"""Route memory layout and route sharing across links (KI-30).

On the EU scope the routes pickle restored 786k Route objects for 143k
distinct routes, each ~7 kB (a list subclass carrying three copies of its
tuples plus a dict). The layout now keeps one copy of the tuples, and
`intern_routes` makes links with the same node sequence share one object.
"""

import pickle

import networkx as nx

from disruptsc.init_pipeline.routing import intern_routes
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.route import Route


def _network():
    tn = nx.Graph()
    tn.add_edge(1, 2, id=10, type="roads", km=5.0)
    tn.add_edge(2, 3, id=11, type="multimodal", km=1.0)
    tn.add_edge(3, 4, id=12, type="railways", km=7.0)
    return tn


def test_route_has_no_instance_dict_and_shares_its_tuples():
    r = Route([1, 2, 3, 4], _network(), "container")
    assert not hasattr(r, "__dict__")
    # the edge tuples of transport_edges ARE the list-part tuples
    assert all(a is b for a, b in zip(r.transport_edges, r[1::2]))
    assert r.transport_nodes_and_edges is r
    assert r.transport_edges == [(1, 2), (2, 3), (3, 4)]
    assert list(r) == [(1,), (1, 2), (2,), (2, 3), (3,), (3, 4), (4,)]


def test_pickle_roundtrip_keeps_layout():
    r = Route([1, 2, 3, 4], _network(), "container")
    p = pickle.loads(pickle.dumps(r))
    assert list(p) == list(r)
    assert p.transport_edges == r.transport_edges
    assert p.transport_edge_ids == [10, 11, 12]
    assert p.length == 13.0
    assert not hasattr(p, "__dict__")
    assert all(a is b for a, b in zip(p.transport_edges, p[1::2]))


def test_old_format_state_still_loads():
    # __setstate__ must accept the four-field state written by earlier versions
    r = Route.__new__(Route)
    r.__setstate__({"transport_nodes": [4, 3], "transport_edge_ids": [12],
                    "transport_modes": ["railways"], "length": 7.0})
    assert list(r) == [(4,), (4, 3), (3,)]
    assert r.transport_edges == [(4, 3)]


def test_revert_keeps_shared_layout():
    r = Route([1, 2, 3, 4], _network(), "container")
    r.revert()
    assert r.transport_nodes == [4, 3, 2, 1]
    assert r.transport_edges == [(4, 3), (3, 2), (2, 1)]
    assert r.transport_edge_ids == [12, 11, 10]
    assert all(a is b for a, b in zip(r.transport_edges, r[1::2]))


class _TN(nx.Graph):
    """Transport-network stand-in with a route library."""

    def __init__(self):
        super().__init__()
        self.shortest_path_library = {"normal": {"container": {}}}


def test_intern_routes_shares_identical_routes_between_links_and_library():
    tn = _network()
    sc = nx.DiGraph()
    routes = [Route([1, 2, 3, 4], tn, "container") for _ in range(3)]
    other = Route([1, 2], tn, "container")
    links = []
    for i, r in enumerate(routes + [other]):
        link = CommercialLink(pid=f"l{i}", supplier_id="s", buyer_id=f"b{i}")
        link.store_route_information(r, "main", 1.0)
        link.route_plan = [(r, 1.0)]
        links.append(link)
        sc.add_edge("s", f"b{i}", object=link)
    library = _TN()
    library.shortest_path_library["normal"]["container"][(1, 4)] = Route([1, 2, 3, 4], tn, "container")

    before, after = intern_routes(sc, library)
    assert (before, after) == (5, 2)
    canonical = links[0].route
    assert all(l.route is canonical for l in links[:3])
    assert all(l.route_plan[0][0] is canonical for l in links[:3])
    assert links[3].route is not canonical
    assert library.shortest_path_library["normal"]["container"][(1, 4)] is canonical
    # a second pass is a no-op
    assert intern_routes(sc, library) == (2, 2)
