"""Probe the transport-capacity code paths on the bundled Testkistan scope.

Read-only companion of docs/architecture/transport-capacity.md (21 Sep 2026):
each section reproduces one finding of the review with a number. Nothing is
cached or exported; the run takes about a minute.

    python scripts/capacity_probe_testkistan.py

Sections: A data capacity columns vs edge capacities after the build;
B the congestion multiplier at zero load; C baseline loads; D whether a
capacity binds on a main route; E Dijkstra calls of the candidate generator;
F an override name that matches no edge; G the finite/unlimited threshold vs
time resolution; H rerouting onto a capped bypass under a closure.
"""

from __future__ import annotations

import io
import logging
import sys
import warnings
from pathlib import Path

import networkx as nx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from disruptsc.build import build_agents, build_common  # noqa: E402
from disruptsc.config import build_params, load_config  # noqa: E402
from disruptsc.init_pipeline import routing  # noqa: E402
from disruptsc.init_pipeline.routing import setup_logistic_routes  # noqa: E402
from disruptsc.network.transport_network import _get_cargo_capacity, _refresh_edge_capacity_costs  # noqa: E402
from disruptsc.run_pipeline.disruption import parse_disruptions  # noqa: E402
from disruptsc.run_pipeline.simulate import _run_one_time_step  # noqa: E402

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
LOG = io.StringIO()
_h = logging.StreamHandler(LOG)
_h.setLevel(logging.WARNING)
logging.getLogger().addHandler(_h)
logging.getLogger().setLevel(logging.WARNING)

TRUNK = "Main Road North"


def build(cap_mode="off", overrides=None, bypass_cap_tpd=None):
    """Testkistan build with transport on and routes assigned; optional capped bypass road 0-9-1."""
    cfg = load_config("Testkistan")
    cfg["export_files"] = False
    cfg["capacity_constraint"] = cap_mode
    cfg["transport_capacity_overrides"] = overrides or {}
    tp, sp, ap, lp = build_params(cfg)
    common = build_common(cfg, tp, sp, ap, lp)
    tn = common["tn"]
    if bypass_cap_tpd is not None:
        tn.add_node(9, id=9, long=0.5, lat=0.5, shipments={}, disruption_duration=0,
                    firms_there=[], households_there=None, type="road")
        for eid, (u, v) in ((99, (0, 9)), (98, (9, 1))):
            e = {k: val for k, val in tn[0][1].items() if not k.startswith(("cost_per_ton", "base_"))}
            e.update(id=eid, name="Bypass North", km=45.0, shipments={}, closed=False, overused=False,
                     node_tuple=(u, v), capacity=bypass_cap_tpd * 7)
            tn.add_edge(u, v, **e)
        tn.ingest_logistic_data(cfg["logistics"], use_cargo_types=tp.use_cargo_types)
        te = common["te"]
        common["te"] = pd.concat([te, pd.DataFrame([{"id": 99, "name": "Bypass North", "type": "roads"},
                                                    {"id": 98, "name": "Bypass North", "type": "roads"}])],
                                 ignore_index=True)
    sc, firms, hh, countries = build_agents(common, ap, sp, tp, seed=0)
    setup_logistic_routes(sc, tn, firms, countries, tp, export_folder=None)
    return cfg, tp, sp, common, sc, firms, hh, countries


def edge_by_name(tn, name):
    return next(tn[u][v] for u, v in tn.edges if tn[u][v].get("name") == name)


def step_capturing_load(t, sc, tn, firms, hh, countries, tp, sp, dis, name):
    """Run one step and return the load on edge *name* just before reset_loads wipes it."""
    e = edge_by_name(tn, name)
    out = {}
    orig = tn.reset_loads

    def capturing():
        out["load"] = sum(e.get(f"current_load_{c}", 0) for c in tn.cargo_types)
        out["overused"] = e.get("overused")
        orig()

    tn.reset_loads = capturing
    _run_one_time_step(t, sc, tn, tn, firms, hh, countries, tp, sp, disruptions=dis)
    tn.reset_loads = orig
    return out


def main():
    print("A. GeoPackage capacity column (tons/day) vs edge capacity after the build (tons/step, weekly)")
    cfg, tp, sp, common, sc, firms, hh, countries = build("off")
    tn = common["tn"]
    for u, v in tn.edges:
        e = tn[u][v]
        col = common["te"].loc[common["te"]["id"] == e["id"], "capacity"].iloc[0] / 7.0
        print(f"   {e['name']:<30} {e['type']:<10} file={col:<8.0f} edge['capacity']={e['capacity']:.3g}")

    print("B. congestion multiplier under gradual (cost_per_ton_with_capacity / cost_per_ton)")
    e = edge_by_name(tn, TRUNK)
    ct = tn.cargo_types[0]
    for util in (0.0, 0.5, 0.8, 1.0):
        for c in tn.cargo_types:
            e[f"current_load_{c}"] = 0
        e[f"current_load_{ct}"] = util * _get_cargo_capacity(e, ct)
        _refresh_edge_capacity_costs(e, tn.cargo_types, "gradual")
        print(f"   utilisation {util:.0%}: ratio={e[f'cost_per_ton_with_capacity_{ct}'] / e[f'cost_per_ton_{ct}']:.2f}")
    tn.reset_loads()

    print("C. baseline loads at t=0 (capacity off)")
    flow, _, _ = _run_one_time_step(0, sc, tn, tn, firms, hh, countries, tp, sp, disruptions=[])
    base = {f["id"]: f["flow_total_tons"] for f in flow}
    for u, v in tn.edges:
        e = tn[u][v]
        print(f"   {e['name']:<30} {base.get(e['id'], 0):9.0f} t/step")
    deliv_off = {d["object"].pid: d["object"].realized_delivery for _, _, d in sc.edges(data=True)}
    cap_tpd = base[edge_by_name(tn, TRUNK)["id"]] * 0.1 / 7.0

    print(f"D. '{TRUNK}' capped at 10% of its baseline load ({cap_tpd:.0f} t/day): does it bind on main routes?")
    for mode in ("binary", "gradual"):
        _, tp2, sp2, common2, sc2, firms2, hh2, countries2 = build(mode, {TRUNK: cap_tpd})
        tn2 = common2["tn"]
        e2 = edge_by_name(tn2, TRUNK)
        got = step_capturing_load(0, sc2, tn2, firms2, hh2, countries2, tp2, sp2, [], TRUNK)
        deliv = {d["object"].pid: d["object"].realized_delivery for _, _, d in sc2.edges(data=True)}
        print(f"   {mode:<8} capacity={e2['capacity']:.0f} t/step, load placed={got['load']:.0f} "
              f"({got['load'] / e2['capacity']:.0%}), overused={got['overused']}, "
              f"max|delivery - off|={max(abs(deliv[k] - deliv_off[k]) for k in deliv):.1e}")

    print("E. candidate generation (heuristic): networkx single_source_dijkstra calls vs OD-cargo groups")
    calls = {"n": 0}
    orig = nx.single_source_dijkstra

    def counting(*a, **k):
        calls["n"] += 1
        return orig(*a, **k)

    routing.nx.single_source_dijkstra = counting
    _, tp3, _, _, sc3, *_ = build("binary", {TRUNK: cap_tpd})
    routing.nx.single_source_dijkstra = orig
    specs = routing._collect_link_specs(sc3, tp3)
    groups = routing._build_od_cargo_groups(specs, tp3.chunk_size)
    print(f"   links={len(specs)} groups={len(groups)} dijkstra calls={calls['n']}")

    print("F. override name that matches no edge")
    LOG.truncate(0)
    LOG.seek(0)
    build("binary", {"Main Road Nort": 10.0})
    hits = [line for line in LOG.getvalue().splitlines() if "Main Road Nort" in line]
    print(f"   warnings naming it: {hits or 'none'}")

    print("G. finite/unlimited classification of the default maritime capacity (5e6 t/day) by resolution")
    for res, f in (("day", 1), ("week", 7), ("month", 30), ("year", 365)):
        cap = 5e6 * f
        print(f"   {res:<6} {cap:.3g} t/step -> {'finite' if cap < 1e8 else 'UNLIMITED'} (threshold 1e8)")

    print(f"H. '{TRUNK}' closed at t=1, parallel bypass road capped at 150 t/day: who gets the bypass?")
    for mode, bypass_cap in (("off", 1e9), ("binary", 150.0), ("gradual", 150.0)):
        _, tp4, sp4, common4, sc4, firms4, hh4, countries4 = build(mode, bypass_cap_tpd=bypass_cap)
        tn4 = common4["tn"]
        dis = parse_disruptions(
            [{"type": "transport_disruption", "attribute": "name", "values": [TRUNK], "start_time": 1, "duration": 3}],
            common4["te"], common4["firm_table"], firms4, tp4.monetary_units, time_resolution=sp4.time_resolution)
        _run_one_time_step(0, sc4, tn4, tn4, firms4, hh4, countries4, tp4, sp4, disruptions=dis)
        got = step_capturing_load(1, sc4, tn4, firms4, hh4, countries4, tp4, sp4, dis, "Bypass North")
        links = [d["object"] for _, _, d in sc4.edges(data=True)
                 if d["object"].use_transport_network and d["object"].served_order > 1e-6]
        hit = [link for link in links if link.route.is_edge_in_route(TRUNK, tn4)]
        rerouted = [link for link in hit if link.current_route == "alternative" and link.realized_delivery > 0]
        dropped = [link for link in hit if link.realized_delivery <= 1e-9]
        byp = edge_by_name(tn4, "Bypass North")
        print(f"   {mode:<8} bypass capacity={byp['capacity']:.0f} t/step | {len(hit)} links offered "
              f"{sum(l.delivery_in_tons for l in hit):.0f} t | rerouted {len(rerouted)} "
              f"({sum(l.delivery_in_tons for l in rerouted):.0f} t) | dropped in full {len(dropped)} | "
              f"load on bypass {got['load']:.0f} t")
        if mode != "off":
            # delivery order of _run_one_time_step: countries first, then firms in dict order
            firm_rank = {pid: i for i, pid in enumerate(firms4)}
            hit.sort(key=lambda l: (l.supplier_id in firm_rank, firm_rank.get(l.supplier_id, -1)))
            print("      per link in delivery order (countries first, then firms):",
                  [(l.pid, round(l.delivery_in_tons), "ok" if l.realized_delivery > 0 else "DROPPED") for l in hit])


if __name__ == "__main__":
    main()
