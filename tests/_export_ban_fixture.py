"""Hand-built two-region fixture for the export-ban tests (tests/test_export_ban.py).

A v2 port of the thesis audit's tiny model (codex/export-controls-fixes,
studies/export_controls/scripts/verify_thesis_mechanisms.py tiny_model): every
quantity below is a fixture choice, not data.

    exporter E (AAA, input good) --0.2/unit--> manufacturer M (BBB) --> household hh_for (BBB), 100/step
    exporter E -------------------------------> household hh_dom (AAA), 10/step   (domestic)
    exporter E -------------------------------> country CCC, 5/step               (foreign, exports)

M holds three steps of E's good. Transport is off (every sector is a service), so
the ledgers are the goods ledgers of the real time step.
"""
from __future__ import annotations

from disruptsc.agents.country import Country
from disruptsc.agents.firm import Firm
from disruptsc.agents.household import Household
from disruptsc.network.commercial_link import CommercialLink
from disruptsc.network.sc_network import ScNetwork
from disruptsc.network.transport_network import TransportNetwork
from disruptsc.params import SimParams, TransportParams
from disruptsc.run_pipeline.simulate import _run_one_time_step, set_initial_conditions

EXPORTER, MANUFACTURER = "E", "M"
INPUT, OUTPUT = "AAA_INP", "BBB_OUT"


def tiny_model(rationing_mode: str = "equal", epsilon_stop: float = 0.0):
    tp = TransportParams(with_transport=False, transport_to_households=False,
                         rationing_mode=rationing_mode, monetary_units="USD")
    sp = SimParams(time_resolution="week", epsilon_stop=epsilon_stop,
                   propagate_input_price_change=False, simulation_type="disruption")
    exporter = Firm(pid=EXPORTER, region="AAA", sector="INP", sector_type="service",
                    region_sector=INPUT, inventory_restoration_time=4.0)
    manufacturer = Firm(pid=MANUFACTURER, region="BBB", sector="OUT", sector_type="service",
                        region_sector=OUTPUT, input_mix={INPUT: 0.2},
                        inventory_duration_target={INPUT: 3.0}, inventory_restoration_time=4.0)
    manufacturer.suppliers = {EXPORTER: {"sector": INPUT, "weight": 1.0, "satisfaction": 1.0}}
    hh_dom = Household(pid="hh_dom", region="AAA", sector_consumption={INPUT: 10.0},
                       retailers={EXPORTER: {"sector": INPUT, "weight": 1.0}})
    hh_for = Household(pid="hh_for", region="BBB", sector_consumption={OUTPUT: 100.0},
                       retailers={MANUFACTURER: {"sector": OUTPUT, "weight": 1.0}})
    country = Country(pid="CCC", region="CCC", sector_type="service", purchase_plan={EXPORTER: 5.0})

    sc = ScNetwork()
    for supplier, buyer, weight, category in ((exporter, manufacturer, 0.2, "export"),
                                              (exporter, hh_dom, 1.0, "domestic_B2C"),
                                              (exporter, country, 1.0, "export"),
                                              (manufacturer, hh_for, 1.0, "domestic_B2C")):
        link = CommercialLink(pid=f"{supplier.pid}->{buyer.pid}", supplier_id=supplier.pid,
                              buyer_id=buyer.pid, product=supplier.region_sector,
                              product_type="service", category=category)
        sc.add_edge(supplier, buyer, object=link, weight=weight)
        supplier.clients[buyer.pid] = {"sector": getattr(buyer, "sector", "households"),
                                       "share": 0.0, "transport_share": 0.0, "distance": 0.0}
    model = {"sc": sc, "tn": TransportNetwork(), "tp": tp, "sp": sp,
             "firms": {EXPORTER: exporter, MANUFACTURER: manufacturer},
             "households": {"hh_dom": hh_dom, "hh_for": hh_for},
             "countries": {"CCC": country}}
    reset(model)
    return model


def reset(model):
    set_initial_conditions(model["sc"], model["firms"], model["households"], model["countries"],
                           model["tp"], model["sp"])


def step(model, t, disruptions):
    _run_one_time_step(t, model["sc"], model["tn"], model["tn"], model["firms"], model["households"],
                       model["countries"], model["tp"], model["sp"], disruptions=disruptions)


def link(model, supplier, buyer):
    for u, v, data in model["sc"].edges(data=True):
        if u.pid == supplier and v.pid == buyer:
            return data["object"]
    raise KeyError((supplier, buyer))


def state(model) -> dict:
    """Everything a step reads or a ledger checks, rounded to nothing (exact comparison)."""
    firms = {pid: {"production": f.production, "production_target": f.production_target,
                   "product_stock": f.product_stock, "inventory": dict(f.inventory),
                   "total_order": f.total_order, "order_book": dict(f.order_book),
                   "rationing": f.rationing, "active_capital": f.active_capital,
                   "idle_capital": f.idle_capital, "price": f.price,
                   "satisfaction": {k: v.get("satisfaction") for k, v in f.suppliers.items()},
                   "export_ban_shares": dict(f.export_ban_shares)}
             for pid, f in model["firms"].items()}
    links = {data["object"].pid: {k: getattr(data["object"], k)
                                  for k in ("order", "served_order", "delivery", "realized_delivery",
                                            "price", "fulfilment_rate", "status", "export_withheld")}
             for _, _, data in model["sc"].edges(data=True)}
    households = {pid: {"loss": h.consumption_loss, "extra": h.extra_spending}
                  for pid, h in model["households"].items()}
    countries = {pid: {"loss": c.consumption_loss, "extra": c.extra_spending}
                 for pid, c in model["countries"].items()}
    return {"firms": firms, "links": links, "households": households, "countries": countries}
