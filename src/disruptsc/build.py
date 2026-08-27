"""Shared no-cache model builder for programmatic drivers (studies, tests).

``execute()`` in run.py remains the cached, exporting CLI pipeline; the two
functions here are the plain build path that the paper's ensemble drivers
(run_grid.py, run_hetero.py, sweep_aid.py, …) used to copy-paste — one
canonical implementation so a future change to the build sequence cannot be
silently missed by a stale copy.

Split mirrors the drivers' usage:

* :func:`build_common` — the seed-independent part (transport network, MRIO,
  tables, flow-coverage selection), built once per process;
* :func:`build_agents` — fresh agents + a seeded supply-chain network +
  initial conditions, built once per Monte-Carlo seed on top of ``common``.

Logistic routes are NOT built here — transport-ON runs that need routing
should go through ``execute()``. The ensemble drivers run with
``with_transport: False``.
"""

from __future__ import annotations

import logging
import random
from pathlib import Path

import numpy as np
import pandas as pd

from disruptsc.init_pipeline.transport import build_transport_network
from disruptsc.init_pipeline.load_data import (
    load_mrio, load_sector_table, load_usd_per_ton, filter_sectors,
)
from disruptsc.init_pipeline.agents import (
    create_firm_table, create_firms, load_tech_coefs, load_input_criticality,
    load_inventories, configure_household_inventories,
    create_household_table, create_households, create_countries,
    add_representative_demand_agents,
)
from disruptsc.init_pipeline.supply_chain import build_supply_chain_network
from disruptsc.run_pipeline.simulate import set_initial_conditions


def build_common(config: dict, tp, sp, ap, lp, *, input_criticality=None) -> dict:
    """Seed-independent build: transport network, MRIO, tables, selection.

    Returns the ``common`` dict consumed by :func:`build_agents`.
    *input_criticality* (a path) overrides ``filepaths.input_criticality``.
    """
    fp = config.get("filepaths", {})
    tn, te, tnodes = build_transport_network(
        config.get("transport_modes", ["roads"]), fp, config.get("logistics", {}),
        sp.time_resolution,
        capacity_overrides=config.get("transport_capacity_overrides"),
        default_transport_capacity=config.get("default_transport_capacity"),
        use_cargo_types=tp.use_cargo_types,
    )
    mrio = load_mrio(fp.get("mrio"), ap.monetary_units_in_data)
    sector_table = load_sector_table(fp.get("sector_table"))
    usd_per_ton = load_usd_per_ton(sector_table)
    selection = filter_sectors(mrio, ap.flow_coverage,
                               ap.sectors_to_include, ap.sectors_to_exclude)
    firm_table = create_firm_table(mrio, sector_table, fp.get("firms_spatial"),
                                   fp.get("households_spatial"), usd_per_ton,
                                   tnodes, ap, selection)
    household_table, consumption = create_household_table(
        mrio, fp.get("households_spatial"), tnodes, selection, ap,
        time_resolution=sp.time_resolution,
    )
    crit_path = input_criticality or fp.get("input_criticality")
    crit_df = (pd.read_csv(crit_path, index_col=0)
               if crit_path and Path(crit_path).exists() else None)
    if crit_df is None:
        logging.warning(
            f"No input-criticality matrix at {crit_path} — "
            f"running strict/threshold Leontief"
        )
    return dict(
        tn=tn, te=te, tnodes=tnodes, mrio=mrio, sector_table=sector_table,
        usd_per_ton=usd_per_ton, selection=selection, firm_table=firm_table,
        household_table=household_table, consumption=consumption,
        cargo_map=(lp.sector_to_cargo_type if tp.use_cargo_types
                   else {"default": "any"}),
        countries_path=fp.get("countries_spatial"), crit_df=crit_df,
    )


def build_agents(common: dict, ap, sp, tp, seed=None):
    """Fresh agents + supply-chain network + initial conditions for one seed.

    Seeds Python's ``random`` and ``numpy.random`` immediately before the
    supply-chain build (the RNG-driven stage) when *seed* is given — the
    same seeding point the ensemble drivers used, so a given seed keeps
    producing the same network. Returns ``(sc_network, firms, households,
    countries)``, initialized at input-output equilibrium.
    """
    firms = create_firms(common["firm_table"], ap)
    load_tech_coefs(firms, common["mrio"], common["selection"])
    if common.get("crit_df") is not None:
        load_input_criticality(firms, common["crit_df"])
    load_inventories(firms, ap.inventory_duration_targets,
                     sp.time_resolution, common["sector_table"])
    households = create_households(common["household_table"], common["consumption"])
    households = add_representative_demand_agents(
        households, common["mrio"], common["selection"], ap, sp.time_resolution)
    configure_household_inventories(
        households, ap.enable_household_inventories,
        ap.household_inventory_duration_targets,
        ap.inventory_restoration_time, sp.time_resolution,
        common["sector_table"])
    countries = create_countries(
        common["mrio"], common["tnodes"], common["countries_path"],
        common["usd_per_ton"], sp.time_resolution, ap, common["selection"],
        transport_edges=common["te"],
        countries_no_transport=tp.countries_no_transport)
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    sc_network = build_supply_chain_network(
        firms, households, countries, common["mrio"], common["sector_table"],
        ap.nb_suppliers_per_input, ap.weight_localization_firm,
        ap.weight_localization_household, common["cargo_map"], common["tn"])
    set_initial_conditions(sc_network, firms, households, countries, tp, sp)
    return sc_network, firms, households, countries


def firm_va_shares(firms: dict) -> dict:
    """pid -> equilibrium value-added share of sales (used to turn per-step
    production into a VA/GDP series). Call after initial conditions are set."""
    def _va(f):
        ef = getattr(f, "eq_finance", None) or {}
        s = ef.get("sales", 0.0)
        c = ef.get("costs", {})
        return (s - c.get("input", 0.0) - c.get("transport", 0.0)) / s if s > 1e-12 else 0.0
    return {pid: _va(f) for pid, f in firms.items()}
