"""C/G/I final-demand split: household welfare must be separated from the single
national government + investment accounting agents, both in export_summary and in the
demand subclasses' identity (agent_type + distinct class for rationing/welfare filters)."""

from disruptsc.agents.household import Household, GovernmentDemand, InvestmentDemand
from disruptsc.run_pipeline.export import export_summary


def _row(pid, atype, ts, cl):
    return {"household": pid, "agent_type": atype, "time_step": ts,
            "consumption_loss_per_sector": cl, "extra_spending_per_sector": {}}


def test_export_summary_separates_welfare_from_gov_investment():
    data = [
        _row("hh_0", "household", 1, {"ECU_CAR": 10.0}),
        _row("hh_0", "household", 2, {"ECU_CAR": 5.0}),
        _row("hh_1", "household", 1, {"ECU_FRV": 3.0}),
        _row("government", "government", 1, {"ECU_EDU": 100.0}),
        _row("investment", "investment", 1, {"ECU_CON": 500.0}),
    ]
    out = export_summary(data, [], export_folder=None)
    assert out["household_loss"] == 18.0        # 10 + 5 + 3 -- welfare only, no gov/inv
    assert out["government_loss"] == 100.0
    assert out["investment_loss"] == 500.0


def test_missing_agent_type_defaults_to_household():
    # Back-compat: rows without agent_type (old CSVs / bundled MRIO) count as household.
    data = [{"household": "hh_0", "time_step": 1,
             "consumption_loss_per_sector": {"ECU_CAR": 7.0}, "extra_spending_per_sector": {}}]
    out = export_summary(data, [], export_folder=None)
    assert out["household_loss"] == 7.0
    assert out["government_loss"] == 0.0
    assert out["investment_loss"] == 0.0


def test_demand_subclasses_identity():
    gov = GovernmentDemand(pid="government", region="ECU")
    inv = InvestmentDemand(pid="investment", region="ECU")
    # isinstance(Household) so all household machinery applies, but a DISTINCT class name
    # so household_first rationing (checks __class__.__name__ == "Household") and the
    # welfare filter treat them as non-household.
    assert isinstance(gov, Household) and isinstance(inv, Household)
    assert gov.agent_type == "government" and inv.agent_type == "investment"
    assert gov.__class__.__name__ == "GovernmentDemand"
    assert inv.__class__.__name__ == "InvestmentDemand"
    # collect_data carries the tag so downstream can filter.
    assert gov.collect_data(1)["agent_type"] == "government"
