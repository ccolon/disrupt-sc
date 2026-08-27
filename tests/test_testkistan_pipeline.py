"""Pipeline regression tests on the bundled Testkistan scope.

These are the smoke tests the model was missing: every previous test was a
leaf-method unit test on synthetic firms, so a regression in the equilibrium
solve, the cascade loop, or goods conservation would reach a paper result
unchallenged — both recently fixed conservation bugs (commits 7962f40 and
cb4acac) shipped without one. The three tests here pin:

1. the t=0 fixed point (an undisrupted step reproduces equilibrium exactly);
2. per-step goods conservation (stock and inventory ledgers) under a
   capital-destruction shock, and that ``set_initial_conditions`` fully
   resets the model afterwards (the state-leakage family);
3. seed determinism of the supply-chain build.

Transport is switched OFF (ensemble mode, as the paper runs): the build
helper does not construct logistic routes, and the conservation logic under
test is identical on the no-transport delivery path.
"""

from __future__ import annotations

import copy

import pytest

from disruptsc.build import build_agents, build_common
from disruptsc.config import build_params, load_config
from disruptsc.run_pipeline.disruption import parse_disruptions
from disruptsc.run_pipeline.simulate import (
    _run_one_time_step, set_initial_conditions,
)

ABS_TOL = 1e-6   # mUSD; model EPSILON is 1e-6
REL_TOL = 1e-9


def _close(a, b, scale=1.0):
    return abs(a - b) <= ABS_TOL + REL_TOL * max(abs(a), abs(b), scale)


@pytest.fixture(scope="session")
def tk():
    """Config, params, and the seed-independent build (once per session)."""
    cfg = load_config("Testkistan")
    cfg["with_transport"] = False
    cfg["export_files"] = False
    tp, sp, ap, lp = build_params(cfg)
    common = build_common(cfg, tp, sp, ap, lp)
    return {"cfg": cfg, "tp": tp, "sp": sp, "ap": ap, "lp": lp, "common": common}


def _fresh_model(tk, seed=0):
    return build_agents(tk["common"], tk["ap"], tk["sp"], tk["tp"], seed=seed)


def _step(t, model, tk, disruptions):
    sc, firms, households, countries = model
    tn = tk["common"]["tn"]
    _run_one_time_step(t, sc, tn, tn, firms, households, countries,
                       tk["tp"], tk["sp"], disruptions=disruptions)


# ----------------------------------------------------------------------
# 1. Fixed point: an undisrupted step reproduces equilibrium
# ----------------------------------------------------------------------

def test_equilibrium_fixed_point(tk):
    model = _fresh_model(tk, seed=0)
    sc, firms, households, countries = model

    _step(0, model, tk, disruptions=[])

    assert firms, "no firms built"
    for f in firms.values():
        assert _close(f.production, f.eq_production, scale=f.eq_production), (
            f"{f.pid}: production {f.production} != eq {f.eq_production}")
        assert f.rationing == pytest.approx(1.0)
        # Prices stay at equilibrium in the undisrupted state
        assert f.price == pytest.approx(f.eq_price)

    for hh in households.values():
        assert abs(hh.consumption_loss) <= ABS_TOL, (
            f"{hh.pid}: consumption_loss {hh.consumption_loss} at equilibrium")
        assert abs(hh.extra_spending) <= ABS_TOL, (
            f"{hh.pid}: extra_spending {hh.extra_spending} at equilibrium")

    for c in countries.values():
        assert abs(c.consumption_loss) <= ABS_TOL


# ----------------------------------------------------------------------
# 2. Conservation ledgers under a shock + full reset afterwards
# ----------------------------------------------------------------------

def _make_capital_shock(tk, model, destroyed_fraction=0.5, duration=3):
    sc, firms, households, countries = model
    sector = sorted({f.sector for f in firms.values()})[0]
    config = [{
        "type": "capital_destruction",
        "description_type": "filter",
        "destroyed_capital": destroyed_fraction,
        "filter": {"sector": [sector]},
        "start_time": 1,
        "duration": duration,
    }]
    disruptions = parse_disruptions(
        config, tk["common"]["te"], tk["common"]["firm_table"], firms,
        tk["tp"].monetary_units, time_resolution=tk["sp"].time_resolution,
    )
    assert disruptions and disruptions[0].description, "shock matched no firm"
    return disruptions


def test_goods_conservation_under_disruption(tk):
    model = _fresh_model(tk, seed=0)
    sc, firms, households, countries = model
    disruptions = _make_capital_shock(tk, model)

    max_shortfall = 0.0
    for t in range(0, 6):
        stock_before = {pid: f.product_stock for pid, f in firms.items()}
        inv_before = {pid: sum(f.inventory.values()) for pid, f in firms.items()}

        _step(t, model, tk, disruptions)
        max_shortfall = max(
            max_shortfall,
            max(f.eq_production - f.production for f in firms.values()),
        )

        # Realized outbound deliveries per firm, read off the links
        sent = {pid: 0.0 for pid in firms}
        for u, v, data in sc.edges(data=True):
            pid = getattr(u, "pid", None)
            if pid in sent:
                sent[pid] += data["object"].realized_delivery

        for pid, f in firms.items():
            # Product-stock ledger: stock_after = stock_before + production
            # − shipped − reconstruction. The max(0, …) clip in the delivery
            # callbacks must never actually create or destroy goods.
            expected = (stock_before[pid] + f.production - sent[pid]
                        - f.reconstruction_produced)
            assert _close(f.product_stock, expected, scale=f.eq_production), (
                f"t={t} {pid}: stock {f.product_stock} != "
                f"{stock_before[pid]} + {f.production} - {sent[pid]}")

            # Inventory ledger: inv_after = inv_before + received − consumed
            expected_inv = inv_before[pid] + f.total_input - f.input_consumed
            assert _close(sum(f.inventory.values()), expected_inv,
                          scale=max(f.eq_production, 1.0)), (
                f"t={t} {pid}: inventory ledger violated")

    # The shock must actually have bitten at some point during the run
    # (otherwise this test proves nothing about conservation under stress).
    assert max_shortfall > ABS_TOL, "capital shock never reduced any production"


def test_set_initial_conditions_resets_everything(tk):
    """The state-leakage family: after a disruption run, one reset must
    restore the exact fixed point — no residual capacity reduction, prices,
    reconstruction fields, or learned satisfaction may survive."""
    model = _fresh_model(tk, seed=0)
    sc, firms, households, countries = model
    disruptions = _make_capital_shock(tk, model, duration=99)  # outlasts the run

    for t in range(0, 3):
        _step(t, model, tk, disruptions)
    assert any(f.production_capacity_reduction > 0 for f in firms.values())

    set_initial_conditions(sc, firms, households, countries, tk["tp"], tk["sp"])

    for f in firms.values():
        assert f.production_capacity_reduction == 0.0
        assert f.remaining_disrupted_time == 0.0
        assert f.reconstruction_demand == 0.0
        assert f.price == pytest.approx(f.eq_price)
        for info in f.suppliers.values():
            assert info["satisfaction"] == pytest.approx(1.0)

    _step(0, model, tk, disruptions=[])
    for f in firms.values():
        assert _close(f.production, f.eq_production, scale=f.eq_production), (
            f"{f.pid}: fixed point not restored after reset")
    for hh in households.values():
        assert abs(hh.consumption_loss) <= ABS_TOL


# ----------------------------------------------------------------------
# 3. Seed determinism of the supply-chain build
# ----------------------------------------------------------------------

def _edge_signature(sc):
    # str() the pids: firm pids are ints while household/country pids are
    # strings, and mixed-type tuples don't sort.
    return sorted(
        (str(u.pid), str(v.pid), data["object"].product, round(data["weight"], 12))
        for u, v, data in sc.edges(data=True)
    )


def test_same_seed_same_network(tk):
    sig_a = _edge_signature(_fresh_model(tk, seed=0)[0])
    sig_b = _edge_signature(_fresh_model(tk, seed=0)[0])
    assert sig_a == sig_b, "same seed produced different supply-chain networks"

    sig_c = _edge_signature(_fresh_model(tk, seed=1)[0])
    # Different seeds should (with overwhelming probability) differ; if the
    # scope is so small that every draw is forced, equality is still fine —
    # only same-seed equality is a hard requirement.
    if sig_c == sig_a:
        pytest.skip("seed 1 network identical to seed 0 (fully forced draws)")
