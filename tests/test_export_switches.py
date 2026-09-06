"""KI-33: link_data.csv and inventory_data.csv are optional per-file exports."""

from __future__ import annotations

from disruptsc.params import SimParams
from disruptsc.run_pipeline.export import AgentWriters


def test_default_writes_every_file(tmp_path):
    with AgentWriters(tmp_path) as w:
        assert w.link is not None and w.inventory is not None
    assert (tmp_path / "link_data.csv").exists() and (tmp_path / "inventory_data.csv").exists()


def test_switches_skip_the_bulk_files(tmp_path):
    with AgentWriters(tmp_path, export_link_data=False, export_inventory_data=False) as w:
        assert w.link is None and w.inventory is None
        w.write_step({}, {}, {}, 0)          # inventory branch returns early
        w.write_links(__import__("networkx").DiGraph(), 0)
    assert (tmp_path / "firm_data.csv").exists()
    assert not (tmp_path / "link_data.csv").exists()
    assert not (tmp_path / "inventory_data.csv").exists()


def test_sim_params_carry_the_switches():
    sp = SimParams(export_link_data=False)
    assert sp.export_link_data is False and sp.export_inventory_data is True
