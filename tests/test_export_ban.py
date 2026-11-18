"""Export ban (Hormuz 2026 MC2, decisions Q7/Q13; shared with studies/export_controls).

Port of the thesis ``export_stop`` rule (J. Seidler, jsei6020/disrupt-sc_Gloria at
d8e91438) with the audited corrections of codex/export-controls-fixes. The cases
are the thesis audit's verification cases that apply to the rule
(studies/export_controls/design/verification_cases.csv on that branch):

* V05 geography and timing: foreign deliveries withheld on the banned steps only,
  domestic deliveries kept at their rationed share, reopening at start + duration;
* V06 shipment and stock: opening stock + production = deliveries + closing stock,
  the withheld goods stay in the exporter's stock;
* V07 reset: after a run (ban active or over), set_initial_conditions restores the
  fresh state and the undisturbed trajectory;
* V04 (the part that is the ban's): no early stop inside a ban window;
* the overlapping-ban fix 1eedfe6 (later expiry wins, order-independent);

plus MC2's own accept tests: a 5 % ban withholds exactly 5 %, everything returns
to the undisturbed path after the window, and off by default.
"""
from __future__ import annotations

import copy
import itertools
import logging
import math
from types import SimpleNamespace

import pytest

import _export_ban_fixture as fx
from disruptsc.run_pipeline.disruption import (
    ExportBan, export_ban_holds, parse_disruptions, update_export_bans,
)
from disruptsc.run_pipeline.simulate import continue_disruption_run, prepare_disruption_baseline

FOREIGN_LINKS = (("E", "M"), ("E", "CCC"))
DOMESTIC_LINK = ("E", "hh_dom")


def _bans(model, *entries):
    """Parse export_ban config entries against the fixture's firms."""
    cfg = [{"type": "export_ban", "regions": ["AAA"], **e} for e in entries]
    return parse_disruptions(cfg, None, None, model["firms"], "USD", time_resolution="week")


def _run(model, disruptions, t_final, observe=None):
    for t in range(0, t_final + 1):
        opening = {pid: f.product_stock for pid, f in model["firms"].items()}
        fx.step(model, t, disruptions if t > 0 else [])
        if observe:
            observe(t, opening)


def _numeric_gap(a, b, path=()):
    """Largest |a - b| over two nested state dicts; inf if a non-number differs."""
    if isinstance(a, dict):
        if set(a) != set(b):
            return math.inf
        return max([_numeric_gap(a[k], b[k], path + (k,)) for k in a] or [0.0])
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return abs(a - b)
    return 0.0 if a == b else math.inf


# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------

def test_parse_fraction_destinations_and_window():
    m = fx.tiny_model()
    every, per_dest, until, open_ended = _bans(
        m,
        {"fraction": 0.05, "start_time": 3, "duration": 4},
        {"sectors": ["INP"], "destinations": {"BBB": 0.3, "default": 0.1}, "end_time": 9, "product": "acid"},
        {"destinations": {"CCC": 1}, "start_time": 2, "end_time": 2},
        {"fraction": 1.0},
    )
    assert every.firm_pids == ["E"] and every.fractions == {} and every.default_fraction == 0.05
    assert (every.start_time, every.end_time) == (3, 6)            # start s, duration d -> s..s+d-1
    assert per_dest.fractions == {"BBB": 0.3} and per_dest.default_fraction == 0.1
    assert (per_dest.start_time, per_dest.end_time, per_dest.product) == (1, 9, "acid")
    assert until.fractions == {"CCC": 1.0} and until.default_fraction == 0.0
    assert (until.start_time, until.end_time) == (2, 2)
    assert open_ended.end_time == math.inf
    assert [every.is_active(t) for t in (2, 3, 6, 7)] == [False, True, True, False]


@pytest.mark.parametrize("entry, match", [
    ({"fraction": 0.1, "destinations": {"BBB": 0.1}}, "exactly one of"),
    ({}, "exactly one of"),
    ({"fraction": 1.5}, r"\[0, 1\]"),
    ({"destinations": {"BBB": -0.1}}, r"\[0, 1\]"),
    ({"fraction": 0.1, "duration": 0}, ">= 1 step"),
    ({"fraction": 0.1, "duration": 2.5}, "whole number"),
    ({"fraction": 0.1, "duration": 2, "end_time": 3}, "not both"),
    ({"fraction": 0.1, "start_time": 5, "end_time": 4}, "before"),
    ({"fraction": 0.1, "start_time": 0}, ">= 1"),
    ({"fraction": 0.1, "destination": {"BBB": 1}}, "unknown key"),
    ({"fraction": 0.1, "recovery_shape": "linear"}, "unknown key"),
])
def test_parse_rejects_ambiguous_or_invalid_entries(entry, match):
    m = fx.tiny_model()
    with pytest.raises(ValueError, match=match):
        _bans(m, entry)


def test_parse_needs_regions_and_warns_on_no_match(caplog):
    m = fx.tiny_model()
    with pytest.raises(ValueError, match="regions"):
        parse_disruptions([{"type": "export_ban", "fraction": 1.0}], None, None, m["firms"], "USD")
    with caplog.at_level(logging.WARNING):
        (ban,) = parse_disruptions([{"type": "export_ban", "regions": ["ZZZ"], "fraction": 1.0}],
                                   None, None, m["firms"], "USD")
    assert ban.firm_pids == [] and "matched NO firm" in caplog.text


# ----------------------------------------------------------------------
# V05 geography and timing, V06 shipment and stock
# ----------------------------------------------------------------------

@pytest.mark.parametrize("fraction", [1.0, 0.05])
def test_v05_v06_foreign_deliveries_withheld_on_the_window_and_kept_in_stock(fraction):
    m = fx.tiny_model()
    bans = _bans(m, {"fraction": fraction, "start_time": 1, "duration": 4})
    exporter = m["firms"]["E"]
    rows = []

    def observe(t, opening):
        links = {key: fx.link(m, *key) for key in FOREIGN_LINKS + (DOMESTIC_LINK,)}
        shipped = sum(link.realized_delivery for link in links.values())
        rows.append({
            "t": t,
            "residual": opening["E"] + exporter.production - shipped - exporter.product_stock,
            "foreign": {key: links[key].delivery for key in FOREIGN_LINKS},
            "withheld": {key: links[key].export_withheld for key in FOREIGN_LINKS},
            "rationed": {key: links[key].served_order * exporter.rationing for key in FOREIGN_LINKS},
            "domestic": links[DOMESTIC_LINK].delivery,
            "domestic_rationed": exporter.order_book["hh_dom"] * min(
                1.0, (opening["E"] + exporter.production) / exporter.total_order),
            "domestic_withheld": links[DOMESTIC_LINK].export_withheld,
            "closing_stock": exporter.product_stock,
        })

    _run(m, bans, 10, observe)
    banned = {1, 2, 3, 4}
    for r in rows:
        # V06: the stock ledger closes at every step; nothing withheld disappears
        assert abs(r["residual"]) <= 1e-10, r
        # V05: domestic buyers keep their rationed share and are never withheld from
        assert math.isclose(r["domestic"], r["domestic_rationed"], rel_tol=1e-12), r
        assert r["domestic_withheld"] == 0.0
        for key in FOREIGN_LINKS:
            if r["t"] in banned:
                assert math.isclose(r["withheld"][key], fraction * r["rationed"][key], rel_tol=1e-12), r
                assert math.isclose(r["foreign"][key], (1 - fraction) * r["rationed"][key], rel_tol=1e-12), r
            else:
                assert r["withheld"][key] == 0.0
                assert math.isclose(r["foreign"][key], r["rationed"][key], rel_tol=1e-12), r
                assert r["foreign"][key] > 0.0                         # reopened at start + duration
    # the first banned step keeps all the withheld goods in the exporter's stock
    first = rows[1]
    assert math.isclose(first["closing_stock"], sum(first["withheld"].values()), rel_tol=1e-12)
    if fraction == 1.0:
        assert all(r["foreign"][key] == 0.0 for r in rows if r["t"] in banned for key in FOREIGN_LINKS)


def test_a_five_percent_ban_withholds_exactly_five_percent_of_foreign_deliveries():
    banned, twin = fx.tiny_model(), fx.tiny_model()
    bans = _bans(banned, {"fraction": 0.05, "start_time": 1, "duration": 4})
    _run(banned, bans, 1)
    _run(twin, [], 1)
    for key in FOREIGN_LINKS:
        with_ban, without = fx.link(banned, *key), fx.link(twin, *key)
        assert without.delivery > 0
        assert math.isclose(with_ban.delivery, 0.95 * without.delivery, rel_tol=1e-15)
        assert math.isclose(with_ban.export_withheld, 0.05 * without.delivery, rel_tol=1e-12)
    assert fx.link(banned, *DOMESTIC_LINK).delivery == fx.link(twin, *DOMESTIC_LINK).delivery
    total_foreign = sum(fx.link(twin, *k).delivery for k in FOREIGN_LINKS)
    total_withheld = sum(fx.link(banned, *k).export_withheld for k in FOREIGN_LINKS)
    assert math.isclose(total_withheld / total_foreign, 0.05, rel_tol=1e-12)


def test_fraction_per_destination_and_default():
    for destinations, expected in (({"BBB": 0.3, "default": 0.1}, {"M": 0.7, "CCC": 0.9}),
                                   ({"CCC": 0.5}, {"M": 1.0, "CCC": 0.5}),
                                   ({"AAA": 1.0, "BBB": 0.2}, {"M": 0.8, "CCC": 1.0})):
        banned, twin = fx.tiny_model(), fx.tiny_model()
        _run(banned, _bans(banned, {"destinations": destinations, "start_time": 1}), 1)
        _run(twin, [], 1)
        for buyer, ratio in expected.items():
            assert math.isclose(fx.link(banned, "E", buyer).delivery,
                                ratio * fx.link(twin, "E", buyer).delivery, rel_tol=1e-15), (destinations, buyer)
        # a destination equal to the exporting region is domestic: never withheld
        assert fx.link(banned, *DOMESTIC_LINK).delivery == fx.link(twin, *DOMESTIC_LINK).delivery


# ----------------------------------------------------------------------
# After the window: back to the undisturbed path
# ----------------------------------------------------------------------

@pytest.mark.parametrize("fraction, horizon", [(0.05, 60), (1.0, 80)])
def test_everything_returns_to_the_undisturbed_path_after_the_window(fraction, horizon):
    banned, twin = fx.tiny_model(), fx.tiny_model()
    bans = _bans(banned, {"fraction": fraction, "start_time": 1, "duration": 4})
    gaps = {}
    for t in range(0, horizon + 1):
        fx.step(banned, t, bans if t > 0 else [])
        fx.step(twin, t, [])
        gaps[t] = _numeric_gap(fx.state(banned), fx.state(twin))
    assert gaps[0] == 0.0
    assert gaps[4] > 1.0                                       # the ban bites inside its window
    # Converges geometrically through inventory restoration and capital mobilization; by the
    # horizon every firm, link, household and country quantity is the undisturbed one.
    scale = max(abs(v) for v in (twin["firms"]["E"].idle_capital, twin["firms"]["E"].active_capital))
    assert gaps[horizon] <= 1e-12 * scale, gaps[horizon]
    assert all(f.export_ban_shares == {} for f in banned["firms"].values())


# ----------------------------------------------------------------------
# Overlapping bans (thesis fix 1eedfe6): the later expiry wins, in any order
# ----------------------------------------------------------------------

def _blocked_steps(windows, t_final=10):
    """Steps at which the exporter's delivery to CCC was fully withheld (real time steps)."""
    m = fx.tiny_model()
    entries = [{"fraction": 1.0, "start_time": s, **({"duration": d} if d is not None else {})}
               for s, d in windows]
    bans = _bans(m, *entries)
    blocked = []
    _run(m, bans, t_final, lambda t, _: blocked.append(t) if fx.link(m, "E", "CCC").delivery == 0.0 else None)
    return blocked


@pytest.mark.parametrize("windows, expected", [
    ([(1, 4)], [1, 2, 3, 4]),
    ([(1, 8), (3, 2)], list(range(1, 9))),            # a shorter later ban does not truncate
    ([(1, 4), (3, 6)], list(range(1, 9))),
    ([(1, 8), (1, 2)], list(range(1, 9))),            # same start, either order
    ([(1, 2), (1, 8)], list(range(1, 9))),
    ([(1, None)], list(range(1, 11))),                # open-ended
    ([(1, None), (3, 2)], list(range(1, 11))),        # a finite overlap keeps an open-ended ban
    ([(1, 2), (5, 3)], [1, 2, 5, 6, 7]),              # disjoint: reopens between and after
])
def test_overlapping_bans_block_until_the_last_expiry(windows, expected):
    assert _blocked_steps(windows) == expected


def _shares(bans, t=1):
    firm = SimpleNamespace(export_ban_shares={})
    update_export_bans(bans, t, {"E": firm})
    return firm.export_ban_shares


def test_overlap_combination_is_order_independent():
    def ban(fraction, product="", end=8, dest=None):
        return ExportBan(firm_pids=["E"], fractions=dest or {}, default_fraction=fraction,
                         product=product, start_time=1, end_time=end)
    # one product: the larger fraction applies while bans overlap
    for order in itertools.permutations([ban(0.2), ban(0.5, end=2), ban(0.1, end=math.inf)]):
        assert _shares(list(order)) == {None: 0.5}
        assert _shares(list(order), t=5) == {None: 0.2}
        assert _shares(list(order), t=50) == {None: 0.1}
    # different products of the sector: the fractions add, capped at 1
    for order in itertools.permutations([ban(0.2, "acid"), ban(0.3, "urea"), ban(0.1, "acid")]):
        assert _shares(list(order)) == {None: pytest.approx(0.5)}
    assert _shares([ban(0.7, "acid"), ban(0.6, "urea")]) == {None: 1.0}
    # named destinations combine region by region, the default fills the others
    shares = _shares([ban(0.1, "acid", dest={"BBB": 0.4}), ban(0.2, "urea")])
    assert shares == {"BBB": pytest.approx(0.6), None: pytest.approx(0.3)}
    # repetition without time passing is idempotent; inactive bans leave no share
    b = [ban(0.2)]
    firm = SimpleNamespace(export_ban_shares={})
    for _ in range(3):
        update_export_bans(b, 1, {"E": firm})
    assert firm.export_ban_shares == {None: 0.2}
    update_export_bans(b, 9, {"E": firm})
    assert firm.export_ban_shares == {}


# ----------------------------------------------------------------------
# V07 reset, V04 early stop
# ----------------------------------------------------------------------

@pytest.mark.parametrize("final_step", [2, 8])                # ban 1-4 still active / over
def test_v07_reset_after_a_ban_matches_a_fresh_build(final_step):
    used, fresh = fx.tiny_model(), fx.tiny_model()
    _run(used, _bans(used, {"fraction": 1.0, "start_time": 1, "duration": 4}), final_step)
    assert bool(used["firms"]["E"].export_ban_shares) == (final_step == 2)
    fx.reset(used)
    # Per-step outputs (firm rationing, household and country loss) are recomputed in every
    # step before they are read, and set_initial_conditions leaves them as they were for every
    # disruption type; the state that carries over must be the fresh one, and the next steps too.
    def carried(s):
        s = copy.deepcopy(s)
        for f in s["firms"].values():
            f.pop("rationing")
        s.pop("households"), s.pop("countries")
        return s
    assert carried(fx.state(used)) == carried(fx.state(fresh))
    for t in range(5):
        fx.step(used, t, [])
        fx.step(fresh, t, [])
        assert fx.state(used) == fx.state(fresh), t


def test_v04_no_early_stop_inside_a_buffered_ban_window():
    # Ban on the intermediate deliveries to BBB only: the manufacturer's three steps of stock
    # hide the ban from final demand until t=4, so the loss-based stop would end the run at t=2.
    m = fx.tiny_model(epsilon_stop=1e-3)
    bans = _bans(m, {"destinations": {"BBB": 1.0}, "start_time": 1, "duration": 4})
    all_data, lr, rs = prepare_disruption_baseline(m["sc"], m["tn"], m["firms"], m["households"],
                                                   m["countries"], m["tp"], m["sp"])
    all_data, _, _ = continue_disruption_run(m["sc"], m["tn"], m["firms"], m["households"], m["countries"],
                                             m["tp"], m["sp"], bans, 1, 30, all_data, lr, rs)
    loss = {r["time_step"]: r["consumption_loss"] for r in all_data["household"] if r["household"] == "hh_for"}
    assert loss[1] == loss[2] == loss[3] == 0.0
    assert loss[4] > 0.0                                      # reached: the ban's losses are recorded
    assert [export_ban_holds(bans, t) for t in (2, 4, 5)] == [True, True, False]
    assert max(loss) < 30                                     # and the run still stops once settled


# ----------------------------------------------------------------------
# Real build (Testkistan): 5 % exactly, ledgers, off by default
# ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def tk():
    from disruptsc.build import build_common
    from disruptsc.config import build_params, load_config
    cfg = load_config("Testkistan")
    cfg["with_transport"] = False
    cfg["export_files"] = False
    tp, sp, ap, lp = build_params(cfg)
    return {"tp": tp, "sp": sp, "ap": ap, "common": build_common(cfg, tp, sp, ap, lp)}


def _tk_model(tk):
    from disruptsc.build import build_agents
    return build_agents(tk["common"], tk["ap"], tk["sp"], tk["tp"], seed=0)


def _tk_step(tk, model, t, disruptions):
    from disruptsc.run_pipeline.simulate import _run_one_time_step
    sc, firms, households, countries = model
    tn = tk["common"]["tn"]
    _run_one_time_step(t, sc, tn, tn, firms, households, countries, tk["tp"], tk["sp"], disruptions=disruptions)


def _tk_parse(tk, model, config):
    return parse_disruptions(config, tk["common"]["te"], tk["common"]["firm_table"], model[1],
                             tk["tp"].monetary_units, time_resolution=tk["sp"].time_resolution)


def _tk_state(model):
    sc, firms, households, countries = model
    return ({pid: (f.production, f.product_stock, f.total_order, tuple(sorted(f.inventory.items())),
                   f.active_capital, f.idle_capital, f.price, f.profit) for pid, f in firms.items()},
            {(str(u.pid), str(v.pid)): (d["object"].order, d["object"].delivery, d["object"].realized_delivery,
                                        d["object"].price, d["object"].payment)
             for u, v, d in sc.edges(data=True)},
            {pid: (h.consumption_loss, h.extra_spending, h.tot_consumption) for pid, h in households.items()},
            {pid: (c.consumption_loss, c.extra_spending, c.qty_sold) for pid, c in countries.items()})


BAN_MANUF_5PCT = [{"type": "export_ban", "regions": ["TESTKISTAN"], "sectors": ["MANUF"],
                   "destinations": {"FOREIGN": 0.05}, "start_time": 1, "duration": 3}]


def test_testkistan_five_percent_ban_on_a_real_build(tk):
    banned, twin = _tk_model(tk), _tk_model(tk)
    bans = _tk_parse(tk, banned, BAN_MANUF_5PCT)
    assert bans[0].firm_pids
    sc, firms = banned[0], banned[1]
    n_foreign = 0
    for t in range(0, 6):
        opening = {pid: f.product_stock for pid, f in firms.items()}
        _tk_step(tk, banned, t, bans if t > 0 else [])
        _tk_step(tk, twin, t, [])
        sent = {pid: 0.0 for pid in firms}
        for u, v, d in sc.edges(data=True):
            if u.pid in sent:
                sent[u.pid] += d["object"].realized_delivery
        for pid, f in firms.items():                          # stock ledger, as in the pipeline test
            assert abs(opening[pid] + f.production - sent[pid] - f.reconstruction_produced
                       - f.product_stock) <= 1e-6 + 1e-9 * f.eq_production
        if t == 1:
            twin_links = {(u.pid, v.pid): d["object"] for u, v, d in twin[0].edges(data=True)}
            for u, v, d in sc.edges(data=True):
                link, other = d["object"], twin_links[(u.pid, v.pid)]
                if u.pid in bans[0].firm_pids and v.pid == "FOREIGN":
                    n_foreign += 1
                    assert other.delivery > 0
                    assert math.isclose(link.delivery, 0.95 * other.delivery, rel_tol=1e-15)
                    assert math.isclose(link.export_withheld, 0.05 * other.delivery, rel_tol=1e-12)
                else:                                         # nothing else moves in the first step
                    assert link.delivery == other.delivery and link.export_withheld == 0.0
    assert n_foreign >= 1


def test_off_by_default_and_inert_bans_are_bit_identical(tk):
    """No export ban -> the step is the one before the port; a zero ban, a ban that never
    starts and a ban on a region without firms leave every quantity bit-identical."""
    capital = [{"type": "capital_destruction", "description_type": "filter", "destroyed_capital": 0.5,
                "filter": {"sector": ["AGRI"]}, "start_time": 1, "duration": 3}]
    inert = [
        {"type": "export_ban", "regions": ["TESTKISTAN"], "fraction": 0.0, "start_time": 1},
        {"type": "export_ban", "regions": ["TESTKISTAN"], "fraction": 1.0, "start_time": 99},
        {"type": "export_ban", "regions": ["NOWHERE"], "fraction": 1.0, "start_time": 1},
    ]
    reference = _tk_model(tk)
    ref_bans = _tk_parse(tk, reference, capital)
    trajectory = []
    for t in range(0, 6):
        _tk_step(tk, reference, t, ref_bans if t > 0 else [])
        trajectory.append(copy.deepcopy(_tk_state(reference)))
    for extra in inert:
        model = _tk_model(tk)
        disruptions = _tk_parse(tk, model, capital + [extra])
        for t in range(0, 6):
            _tk_step(tk, model, t, disruptions if t > 0 else [])
            assert _tk_state(model) == trajectory[t], (extra, t)


def test_export_bans_are_in_the_run_fingerprint_only_when_present():
    from disruptsc.run_pipeline.fingerprint import build_fingerprint, build_stage_fingerprint, fingerprint_hash
    from disruptsc.validate_inputs import _KNOWN_DISRUPTION_TYPES
    base = {"scope": "X", "disruptions": [{"type": "transport_disruption", "attribute": "id", "values": [1]}]}
    banned = copy.deepcopy(base)
    banned["disruptions"].append(BAN_MANUF_5PCT[0])
    assert "export_bans" not in build_fingerprint(base)
    payload = build_fingerprint(banned)
    assert payload["export_bans"] == BAN_MANUF_5PCT
    assert fingerprint_hash(payload) != fingerprint_hash(build_fingerprint(base))
    for stage in ("transport_network", "agents", "sc_network", "logistic_routes"):  # run-time only
        assert build_stage_fingerprint(banned, stage)["hash"] == build_stage_fingerprint(base, stage)["hash"]
    assert "export_ban" in _KNOWN_DISRUPTION_TYPES
