"""shortest_paths_for (scipy Dijkstra + predecessor reconstruction) must
reproduce networkx single-source Dijkstra paths and costs, skip unreachable
pairs, and handle same-node pairs and sources outside the subgraph."""

from __future__ import annotations

import random

import networkx as nx
import pytest

from disruptsc.init_pipeline.routing import shortest_paths_for

W = "cost_per_ton_dry_bulk"


def _random_graph(seed: int, n: int = 120, m: int = 320) -> nx.Graph:
    rng = random.Random(seed)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    while g.number_of_edges() < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v and not g.has_edge(u, v):
            g.add_edge(u, v, **{W: rng.uniform(0.5, 50.0)})   # distinct floats: no ties
    return g


def _cost(g, path):
    return sum(g[u][v][W] for u, v in zip(path[:-1], path[1:]))


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_matches_networkx_paths_and_costs(seed):
    g = _random_graph(seed)
    rng = random.Random(100 + seed)
    dest_by_source = {s: {rng.randrange(120) for _ in range(15)} for s in rng.sample(range(120), 20)}
    got = shortest_paths_for(g, W, dest_by_source, chunk=7)
    for s, dests in dest_by_source.items():
        nx_paths = nx.single_source_dijkstra_path(g, s, weight=W)
        for d in dests:
            if d not in nx_paths:
                assert (s, d) not in got
                continue
            assert (s, d) in got, f"{s}->{d} missing"
            assert got[(s, d)][0] == s and got[(s, d)][-1] == d
            assert _cost(g, got[(s, d)]) == pytest.approx(_cost(g, nx_paths[d]), rel=1e-12)
            assert got[(s, d)] == nx_paths[d]          # unique optimum: identical path


def test_unreachable_same_node_and_missing_source():
    g = nx.Graph()
    g.add_edge(1, 2, **{W: 1.0}); g.add_edge(2, 3, **{W: 1.0}); g.add_edge(10, 11, **{W: 1.0})
    got = shortest_paths_for(g, W, {1: {3, 10, 1}, 99: {1}})
    assert got[(1, 3)] == [1, 2, 3]
    assert got[(1, 1)] == [1]
    assert (1, 10) not in got and (99, 1) not in got


def test_zero_weight_edges_are_still_edges():
    g = nx.Graph()
    g.add_edge(1, 2, **{W: 0.0}); g.add_edge(2, 3, **{W: 5.0}); g.add_edge(1, 3, **{W: 6.0})
    got = shortest_paths_for(g, W, {1: {3}})
    assert got[(1, 3)] == [1, 2, 3]
