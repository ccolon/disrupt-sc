"""Probe the transport-capacity mechanics on the bundled Testkistan scope.

Companion of docs/architecture/transport-capacity.md. The first version
(21 Sep 2026, morning) reproduced the defects of the retired code: a capacity
never bound on a main route, first-come-first-served rerouting, the 0.5x
discount of the gradual multiplier, GeoPackage columns overwritten, an
unknown override name ignored (KI-39 to KI-42). This version exercises the
capacity gate that replaced it (run_pipeline/capacity_gate.py) on the same
scenarios. Read-only: nothing is cached or exported; about a minute.

    python scripts/capacity_probe_testkistan.py

Sections: A capacities exist only on the named edges; B baseline loads;
C a trunk capped at a tenth of its load on a tree network (nothing can be
re-sent: the gate withholds, the goods stay in stock); D the trunk closed
with a parallel bypass road capped at 150 t/day (the cut shares of every
shipper are re-sent and share the bypass pro rata, against the archived
first-come outcome); E the time a step costs with the gate on and off.
"""

from __future__ import annotations

import logging
import math
import sys
import time
import warnings
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from disruptsc.build import build_agents, build_common  # noqa: E402
from disruptsc.config import build_params, load_config  # noqa: E402
from disruptsc.init_pipeline.routing import setup_logistic_routes  # noqa: E402
from disruptsc.run_pipeline.disruption import parse_disruptions  # noqa: E402
from disruptsc.run_pipeline.simulate import _run_one_time_step  # noqa: E402

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

TRUNK = "Main Road North"


def build(capacity_constraint=False, overrides=None, bypass_cap_tpd=None):
    """Testkistan with transport on and routes assigned; optional parallel bypass road 0-9-1."""
    cfg = load_config("Testkistan")
    cfg["export_files"] = False
    cfg["capacity_constraint"] = capacity_constraint
    cfg["transport_capacity_overrides"] = dict(overrides or {})
    tp, sp, ap, lp = build_params(cfg)
    common = build_common(cfg, tp, sp, ap, lp)
    tn = common["tn"]
    if bypass_cap_tpd is not None:
        tn.add_node(9, id=9, long=0.5, lat=0.5, shipments={}, disruption_duration=0,
                    firms_there=[], households_there=None, type="road")
        for eid, (u, v) in ((99, (0, 9)), (98, (9, 1))):
            e = {k: val for k, val in tn[0][1].items() if not k.startswith(("cost_per_ton", "base_", "capacity"))}
            e.update(id=eid, name="Bypass North", km=45.0, shipments={}, closed=False, node_tuple=(u, v),
                     capacity=bypass_cap_tpd * 7)
            tn.add_edge(u, v, **e)
        tn.ingest_logistic_data(cfg["logistics"], use_cargo_types=tp.use_cargo_types,
                                cargo_mode_eligibility=tp.cargo_mode_eligibility)
        te = common["te"]
        common["te"] = pd.concat([te, pd.DataFrame([{"id": 99, "name": "Bypass North", "type": "roads"},
                                                    {"id": 98, "name": "Bypass North", "type": "roads"}])],
                                 ignore_index=True)
    sc, firms, hh, countries = build_agents(common, ap, sp, tp, seed=0)
    setup_logistic_routes(sc, tn, firms, countries, tp, export_folder=None)
    return cfg, tp, sp, common, sc, firms, hh, countries


def edge_by_name(tn, name):
    return next(tn[u][v] for u, v in tn.edges if tn[u][v].get("name") == name)


def step(m, t, dis=()):
    cfg, tp, sp, common, sc, firms, hh, countries = m
    return _run_one_time_step(t, sc, common["tn"], common["tn"], firms, hh, countries, tp, sp, disruptions=list(dis))


def links_of(m):
    return [d["object"] for _, _, d in m[4].edges(data=True)
            if d["object"].use_transport_network and d["object"].served_order > 1e-6]


def main():
    print("A. capacity keys exist only on the named edges (transport_capacity_overrides)")
    m = build(True, {TRUNK: 275.0, "Port Terminal": {"container": 500.0}})
    tn = m[3]["tn"]
    for u, v in tn.capacitated_edges():
        e = tn[u][v]
        keys = {k: e[k] for k in e if k == "capacity" or k.startswith("capacity_")}
        print(f"   {e['name']:<30} {keys}")
    print(f"   {len(tn.capacitated_edges())} of {tn.number_of_edges()} edges carry a capacity")

    print("B. baseline loads at t=0 (capacity off)")
    off = build(False)
    flow, _, _ = step(off, 0)
    tn_off = off[3]["tn"]
    base = {f["id"]: f["flow_total_tons"] for f in flow}
    for u, v in tn_off.edges:
        e = tn_off[u][v]
        print(f"   {e['name']:<30} {base.get(e['id'], 0):9.0f} t/step")

    print(f"C. '{TRUNK}' capped at a tenth of its baseline load (tree network: no other route)")
    cap_tpd = round(base[edge_by_name(tn_off, TRUNK)["id"]] * 0.1 / 7.0)
    on = build(True, {TRUNK: float(cap_tpd)})
    tn_on = on[3]["tn"]
    firms = on[5]
    stock_before = sum(f.product_stock for f in firms.values())
    t0 = time.time()
    step(on, 0)
    dt = time.time() - t0
    stats = tn_on.capacity_gate_stats[edge_by_name(tn_on, TRUNK)["id"]]
    ls = links_of(on)
    offered = sum(l.delivery_offered for l in ls)
    delivered = sum(l.realized_delivery for l in ls)
    blocked = sum(l.capacity_blocked for l in ls)
    print(f"   capacity {cap_tpd} t/day = {cap_tpd * 7} t/step | trunk offered {stats['offered_tons']:.0f} t, "
          f"accepted {stats['accepted_tons']:.0f} t, withheld {stats['withheld_tons']:.0f} t, rounds {stats['rounds']}")
    print(f"   links: offered {offered:.2f}, delivered {delivered:.2f}, capacity_blocked {blocked:.2f} (model units); "
          f"the blocked goods sit in the suppliers' stocks")
    hit = [l for l in ls if l.route.is_edge_in_route(TRUNK, tn_on)]
    shares = sorted({round(l.realized_delivery / l.delivery_offered, 4) for l in hit if l.delivery_offered > 1e-9})
    print(f"   {len(hit)} links cross the trunk; delivered share of the offered quantity: {shares} (one value: proportional)")

    print(f"D. '{TRUNK}' closed at t=1, parallel bypass road capped at 150 t/day")
    m2 = build(True, {}, bypass_cap_tpd=150.0)
    cfg2, tp2, sp2, common2, sc2, firms2, hh2, countries2 = m2
    tn2 = common2["tn"]
    dis = parse_disruptions([{"type": "transport_disruption", "attribute": "name", "values": [TRUNK],
                              "start_time": 1, "duration": 3}], common2["te"], common2["firm_table"], firms2,
                            tp2.monetary_units, time_resolution=sp2.time_resolution)
    step(m2, 0, dis)
    step(m2, 1, dis)
    byp = edge_by_name(tn2, "Bypass North")
    st = tn2.capacity_gate_stats[byp["id"]]
    ls = links_of(m2)
    hit = [l for l in ls if l.route.is_edge_in_route(TRUNK, tn2)]
    print(f"   bypass capacity {byp['capacity']:.0f} t/step | offered {st['offered_tons']:.0f} t, accepted "
          f"{st['accepted_tons']:.0f} t, withheld {st['withheld_tons']:.0f} t, rounds {st['rounds']}")
    print(f"   {len(hit)} links crossed the closed trunk, {sum(l.delivery_in_tons for l in hit):.0f} t delivered of "
          f"{sum(l.delivery_offered for l in hit):.2f} offered (model units: "
          f"{sum(l.realized_delivery for l in hit):.2f}); capacity_blocked {sum(l.capacity_blocked for l in hit):.2f}")
    print("   per link: offered -> delivered (share):",
          [(l.pid, round(l.delivery_offered, 2), round(l.realized_delivery, 2),
            round(l.realized_delivery / l.delivery_offered, 3) if l.delivery_offered > 1e-9 else None) for l in hit])
    print("   (archived first-come outcome of the retired code on this scenario: 5 links delivered in full, "
          "4 dropped in full, bypass at 149 % of capacity)")

    print("E. wall time of one step (this scope, 34 links)")
    for label, model, d in (("capacity off", build(False), ()), ("gate on, trunk capped", build(True, {TRUNK: float(cap_tpd)}), ())):
        step(model, 0, d)
        t0 = time.time()
        for t in range(1, 6):
            step(model, t, d)
        print(f"   {label:<24} {(time.time() - t0) / 5 * 1000:7.1f} ms per step")


if __name__ == "__main__":
    main()
