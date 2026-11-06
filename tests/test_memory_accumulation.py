"""KI-54 (6 Nov 2026): what a run keeps in memory.

- export_summary sums the (agent, time step, sector) losses as it reads them, instead of building one dict per
  (agent, time step, sector): same outputs as the former implementation (kept below as the reference).
- _accumulate_and_write keeps no firm rows and slim household rows.
"""
import random

import numpy as np
import pandas as pd
import pytest

from disruptsc.run_pipeline import simulate
from disruptsc.run_pipeline.export import export_summary, slim_household_record


def _export_summary_reference(household_data, country_data, household_table=None):
    """The implementation before KI-54 (export.py, 5 Nov 2026), outputs only."""
    hh_df = pd.DataFrame(household_data)
    if hh_df.empty:
        return {"household_loss": 0.0, "country_loss": 0.0}, None
    loss_rows = []
    for _, grp in hh_df.groupby("household"):
        for _, row in grp.iterrows():
            es = row.get("extra_spending_per_sector", {})
            cl = row.get("consumption_loss_per_sector", {})
            atype = row.get("agent_type", "household")
            for sector in set(list(es.keys()) + list(cl.keys())):
                loss_rows.append({"household": row["household"], "agent_type": atype, "time_step": row["time_step"],
                                  "sector": sector, "loss": es.get(sector, 0) + cl.get(sector, 0)})
    loss_df_all = pd.DataFrame(loss_rows)

    def _agent_loss(atype):
        if loss_df_all.empty or "agent_type" not in loss_df_all.columns:
            return 0.0
        return float(loss_df_all.loc[loss_df_all["agent_type"] == atype, "loss"].sum())

    out = {"household_loss": _agent_loss("household"), "government_loss": _agent_loss("government"),
           "investment_loss": _agent_loss("investment")}
    if not loss_df_all.empty and "agent_type" in loss_df_all.columns:
        loss_df = loss_df_all[loss_df_all["agent_type"] == "household"].drop(columns=["agent_type"])
    else:
        loss_df = loss_df_all
    if household_table is not None and "id" in household_table.columns and not loss_df.empty:
        ht = household_table.copy()
        ht["id"] = "hh_" + ht["id"].astype(str)
        loss_df["region"] = loss_df["household"].map(ht.set_index("id")["region"])
    groupby_cols = [c for c in ["region", "sector", "time_step"] if c in loss_df.columns]
    if groupby_cols:
        loss_df = loss_df.groupby(groupby_cols, as_index=False)["loss"].sum()
    c_df = pd.DataFrame(country_data)
    out["country_loss"] = 0.0 if c_df.empty else (c_df["extra_spending"] + c_df["consumption_loss"]).sum()
    return out, loss_df


def _synthetic(seed, n_hh=12, n_t=6, with_unmapped=True):
    rng = random.Random(seed)
    sectors = [f"S{i}" for i in range(7)]
    data = []
    agents = [(f"hh_{i}", "household") for i in range(n_hh)] + [("gov", "government"), ("inv", "investment")]
    for t in range(n_t):
        for pid, atype in agents:
            secs = rng.sample(sectors, rng.randint(0, len(sectors)))
            cl = {s: rng.choice([0.0, rng.random()]) for s in secs}
            es = {s: rng.random() for s in rng.sample(secs, len(secs) // 2)}
            data.append({"time_step": t, "household": pid, "agent_type": atype, "region": "R",
                         "consumption_loss": sum(cl.values()), "extra_spending": sum(es.values()),
                         "consumption_loss_per_sector": cl, "extra_spending_per_sector": es})
    ids = range(n_hh - 2) if with_unmapped else range(n_hh)       # two households missing from the table
    table = pd.DataFrame({"id": list(ids), "region": [f"R{i % 3}" for i in ids]})
    countries = [{"time_step": t, "country": c, "extra_spending": rng.random(), "consumption_loss": rng.random()}
                 for t in range(n_t) for c in ("A", "B")]
    return data, countries, table


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("use_table", [True, False])
def test_export_summary_matches_former_implementation(tmp_path, seed, use_table):
    data, countries, table = _synthetic(seed)
    table = table if use_table else None
    ref, ref_df = _export_summary_reference(data, countries, table)
    out = export_summary(data, countries, table, export_folder=tmp_path)
    for k, v in ref.items():
        assert out[k] == pytest.approx(v, rel=1e-12, abs=1e-12), k
    got = pd.read_csv(tmp_path / "loss_per_region_sector_time.csv")
    want = ref_df.reset_index(drop=True)
    assert list(got.columns) == list(want.columns)
    assert len(got) == len(want)
    for c in want.columns:
        if c == "loss":
            np.testing.assert_allclose(got[c].to_numpy(), want[c].to_numpy(), rtol=1e-12, atol=1e-12)
        else:
            assert got[c].astype(str).tolist() == want[c].astype(str).tolist(), c


def test_export_summary_empty_and_zero_rows(tmp_path):
    assert export_summary([], [], export_folder=None) == {"household_loss": 0.0, "country_loss": 0.0}
    rows = [{"time_step": 0, "household": "hh_0", "agent_type": "household",
             "consumption_loss_per_sector": {}, "extra_spending_per_sector": {}}]
    out = export_summary(rows, [], export_folder=tmp_path)
    assert out["household_loss"] == 0.0
    ref, _ = _export_summary_reference(rows, [])
    assert out["household_loss"] == ref["household_loss"]


def test_accumulate_keeps_no_firm_rows_and_slim_households():
    class _Agent:
        def __init__(self, pid):
            self.pid = pid

        def collect_data(self, t):
            return {"time_step": t, "household": self.pid, "agent_type": "household", "region": "R",
                    "consumption_loss": 0.0, "extra_spending": 0.0,
                    "consumption_per_sector": {"A": 1.0}, "spending_per_sector": {"A": 1.0},
                    "consumption_loss_per_sector": {"A": 0.0}, "extra_spending_per_sector": {"A": 0.0}}

    all_data = {"firm": [], "household": [], "country": [], "transport_flow": []}
    firms = {i: _Agent(f"f{i}") for i in range(3)}
    households = {i: _Agent(f"hh_{i}") for i in range(2)}
    simulate._accumulate_and_write(all_data, firms, households, {}, 1, flow_data=None, writers=None)
    assert all_data["firm"] == []
    assert len(all_data["household"]) == 2
    assert "consumption_per_sector" not in all_data["household"][0]
    assert all_data["household"][0]["consumption_loss_per_sector"] == {"A": 0.0}
    assert slim_household_record({"a": 1, "spending_per_sector": {}}) == {"a": 1}
