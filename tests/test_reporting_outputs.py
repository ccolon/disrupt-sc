"""Reporting-only run outputs (Hormuz 2026 node A26, decision Q28; KI-73; 18 Nov 2026).

Four switches, all off by default:
- export_trade_by_region_sector: trade_by_region_sector.csv, the cross-region deliveries
  of trade_data.csv split by seller region, seller sector and buyer region;
- monitored_edges: edges the logistics report covers without a capacity;
- export_logistics_every_step: the logistics report at every step, not steps 0 and 1 only;
- export_edge_flows_every_step: the per-edge flow GeoJSONs at every step, likewise (split
  from the report on 18 Nov 2026: a file is the whole network, ~1 MB a week on Gulf).

The pipeline test runs the bundled Testkistan scope (with transport, its transport
disruption) three times through ``execute``: switches off; all four on; and the Hormuz
setting (all on but the flow GeoJSONs). It checks that every output the plain run writes
comes out byte-identical in the other two, that the new trade file sums to trade_data.csv
per country and step, that the monitored edges are in the report with the flows of the
flow files, and that the flow files follow their own switch only.
"""

from __future__ import annotations

import copy
import hashlib
import json

import pandas as pd
import pytest

import disruptsc.run_pipeline.cache as cache_mod
from disruptsc.config import build_params, load_config
from disruptsc.run import execute
from disruptsc.run_pipeline.export import monitored_edge_names

MONITORED = ["Main Road North", "Port Terminal", "International Shipping Route"]


# ----------------------------------------------------------------------
# Config parsing and the monitored list
# ----------------------------------------------------------------------

def _params(**overrides):
    cfg = load_config("Testkistan")
    cfg.update(overrides)
    return build_params(cfg)[1]


def test_switches_default_off():
    sp = _params()
    assert sp.export_trade_by_region_sector is False
    assert sp.export_logistics_every_step is False
    assert sp.export_edge_flows_every_step is False
    assert sp.monitored_edges == ()


def test_monitored_edges_parsing():
    sp = _params(monitored_edges=["a", "b", "a"])
    assert sp.monitored_edges == ("a", "b")          # order kept, duplicates dropped
    with pytest.raises(ValueError, match="list of edge names"):
        _params(monitored_edges="Main Road North")   # a bare string is not a list
    with pytest.raises(ValueError, match="non-empty edge name"):
        _params(monitored_edges=["ok", ""])


class _Net:
    def __init__(self, names):
        self._names = names

    def edges(self, data=False):
        return [(i, i + 1, {"name": n}) for i, n in enumerate(self._names)]


def test_monitored_edge_names_merge_and_check():
    net = _Net(["x", "y", "z"])
    assert monitored_edge_names({}, (), net) is None                 # nothing monitored: no report
    assert monitored_edge_names(None, None, net) is None
    assert monitored_edge_names({"x": 10}, None, net) == ["x"]       # the former rule
    assert monitored_edge_names({"x": 10}, ("y", "x"), net) == ["x", "y"]
    with pytest.raises(ValueError, match="match no edge"):
        monitored_edge_names({}, ("y", "Kirkuk\u00e2\u20ac\u201cCeyhan"), net)


def test_validate_inputs_lists_unknown_monitored_edges(monkeypatch):
    import disruptsc.validate_inputs as vi
    monkeypatch.setattr(vi, "_edge_names", lambda filepaths: {"a", "b"})
    errors = []
    vi._check_monitored_edges({}, {"monitored_edges": ["a", "zz", "yy"]}, errors)
    assert len(errors) == 1 and "2 name(s)" in errors[0]
    errors = []
    vi._check_monitored_edges({}, {"monitored_edges": ["a", "b"]}, errors)
    assert not errors


# ----------------------------------------------------------------------
# Testkistan pipeline: identity, sums, monitored flows, every step
# ----------------------------------------------------------------------

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def runs(tmp_path_factory, monkeypatch_module):
    """{"off": no switch, "on": all four, "report": all but the flow GeoJSONs (the Gulf
    configs' setting)} -> export folder."""
    root = tmp_path_factory.mktemp("a26")
    cache_dir = root / "cache"
    cache_dir.mkdir()
    monkeypatch_module.setattr(cache_mod, "get_cache_dir", lambda: cache_dir)

    base = load_config("Testkistan")
    base["export_files"] = True
    base["seed"] = 0
    base["t_final"] = 6
    base["epsilon_stop_condition"] = 0     # the full horizon: steps beyond 1 to report
    out = {"off": execute(copy.deepcopy(base), export_folder=root / "off")}

    for name, edge_flows in (("on", True), ("report", False)):
        cfg = copy.deepcopy(base)
        cfg["export_trade_by_region_sector"] = True
        cfg["export_logistics_every_step"] = True
        cfg["export_edge_flows_every_step"] = edge_flows
        cfg["monitored_edges"] = list(MONITORED)
        out[name] = execute(cfg, export_folder=root / name)
    return out


@pytest.fixture(scope="module")
def two_runs(runs):
    return runs["off"], runs["on"]


@pytest.fixture(scope="module")
def monkeypatch_module():
    mp = pytest.MonkeyPatch()
    yield mp
    mp.undo()


# Files whose content the switches may change: the config snapshot (it holds the switches),
# the log, and the logistics report files the switches are about.
_EXPECTED_TO_DIFFER = {"parameters.yaml", "exp.log"}
_NEW_OR_EXTENDED = {"trade_by_region_sector.csv", "logistics_report.csv",
                    "logistics_summary.csv", "logistics_top_utilized.csv"}


@pytest.mark.parametrize("variant", ["on", "report"])
def test_existing_outputs_identical(runs, variant):
    off, on = runs["off"], runs[variant]
    off_files = {p.name for p in off.iterdir() if p.is_file()}
    on_files = {p.name for p in on.iterdir() if p.is_file()}
    assert off_files <= on_files, f"files missing with the switches on: {off_files - on_files}"
    for name in ("firm_data.csv", "household_data.csv", "household_data_by_sector.csv",
                 "country_data.csv", "trade_data.csv", "loss_summary.csv",
                 "loss_per_country.csv", "loss_per_region_sector_time.csv"):
        assert name in off_files, name
    compared = sorted(off_files - _EXPECTED_TO_DIFFER - _NEW_OR_EXTENDED)
    assert "transport_edges_with_flows_0.geojson" in compared
    diff = [n for n in compared if _sha(off / n) != _sha(on / n)]
    assert not diff, f"outputs changed by reporting-only switches: {diff}"


def test_trade_by_region_sector_sums_to_trade_data(two_runs):
    _, on = two_runs
    tbr = pd.read_csv(on / "trade_by_region_sector.csv")
    td = pd.read_csv(on / "trade_data.csv")
    assert list(tbr.columns) == ["time_step", "seller_region", "seller_sector", "buyer_region",
                                 "quantity", "tons"]
    assert len(tbr) and (tbr["quantity"] > 0).all()
    assert (tbr["seller_region"] != tbr["buyer_region"]).all()
    assert tbr["time_step"].nunique() == td["time_step"].nunique()
    exp = tbr.groupby(["time_step", "seller_region"])["quantity"].sum()
    imp = tbr.groupby(["time_step", "buyer_region"])["quantity"].sum()
    td = td.set_index(["time_step", "country"])
    for col, agg in (("exports", exp), ("imports", imp)):
        agg.index.names = ["time_step", "country"]
        got = agg.reindex(td.index, fill_value=0.0)
        want = td[col]
        rel = ((got - want).abs() / want.abs().clip(lower=1e-300)).where(want != 0, (got - want).abs())
        assert rel.max() <= 1e-9, f"{col}: max relative gap {rel.max():.3g}"


def test_monitored_edges_in_report_with_flows(two_runs):
    _, on = two_runs
    lr = pd.read_csv(on / "logistics_report.csv")
    assert set(MONITORED) <= set(lr["name"])
    steps = sorted(pd.read_csv(on / "firm_data.csv")["time_step"].unique())
    assert sorted(lr["time_step"].unique()) == steps            # every step, not 0 and 1 only
    cap_cols = [c for c in lr.columns if c.startswith("capacity_")]
    assert lr[cap_cols].isna().all().all()                       # no capacity was set
    carried = 0
    for t in steps:
        path = on / f"transport_edges_with_flows_{t}.geojson"
        # a step with no flow anywhere has no flow file (the rule of steps 0 and 1 too)
        flows = json.loads(path.read_text()) if path.exists() else {"features": []}
        tons = {f["properties"]["id"]: f["properties"].get("flow_total_tons") for f in flows["features"]}
        for _, row in lr[lr["time_step"] == t].iterrows():
            expected = tons.get(row["edge_id"])
            expected = 0.0 if expected is None or expected != expected else float(expected)
            assert row["flow_tons"] == pytest.approx(expected, abs=0.051), (t, row["name"])
            carried += row["flow_tons"] > 0
    assert carried, "no monitored edge carried anything: the check would be empty"


def _flow_file_steps(folder):
    return sorted(int(p.stem.rsplit("_", 1)[1]) for p in folder.glob("transport_edges_with_flows_*.geojson"))


def test_flow_files_follow_their_own_switch(runs):
    """export_edge_flows_every_step: a flow file for every step with flow on the network
    (logistics_summary.csv, computed at every step); without it steps 0 and 1 only, with
    the report at every step or not. In this scenario the closure of Main Road North
    stops every shipment at steps 1 and 2."""
    on = runs["on"]
    summary = pd.read_csv(on / "logistics_summary.csv").dropna(subset=["total_tons"])
    steps = sorted(pd.read_csv(on / "firm_data.csv")["time_step"].unique())
    assert sorted(summary["time_step"].astype(int)) == steps
    with_flow = sorted(int(t) for t in summary.loc[summary["total_tons"] > 0, "time_step"])
    assert len([t for t in with_flow if t > 1]) >= 3
    assert _flow_file_steps(on) == with_flow
    assert _flow_file_steps(runs["off"]) == [t for t in with_flow if t <= 1]
    assert _flow_file_steps(runs["report"]) == [t for t in with_flow if t <= 1]


def test_report_independent_of_the_flow_files(runs):
    """The weekly report (and the trade file) are the same with or without the flow GeoJSONs."""
    for name in ("logistics_report.csv", "logistics_summary.csv", "trade_by_region_sector.csv"):
        assert _sha(runs["report"] / name) == _sha(runs["on"] / name), name
    lr = pd.read_csv(runs["report"] / "logistics_report.csv")
    steps = sorted(pd.read_csv(runs["report"] / "firm_data.csv")["time_step"].unique())
    assert sorted(lr["time_step"].unique()) == steps
