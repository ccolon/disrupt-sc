"""Port-specific terminal fees and dwell times (25 Oct 2026): logistics.loading_fees.by_port / dwell_times.by_port are added
on the connectors whose port_name tag matches; nothing changes without the tag or the key."""
from disruptsc.network.transport_network import _get_dwell_time_and_fee

FEES = {"roads-maritime": 7, "railways-maritime": {"default": 7, "container": 5}, "by_port": {"Amsterdam": 1.5, "Venezia": 2.0}}
DWELL = {"roads-maritime": 24, "by_port": {"Venezia": 12}}


def test_untagged_connector_unchanged():
    edge = {"type": "multimodal", "multimodes": "roads-maritime"}
    assert _get_dwell_time_and_fee(edge, DWELL, FEES) == (24, 7)


def test_other_port_unchanged():
    edge = {"type": "multimodal", "multimodes": "roads-maritime", "port_name": "Rotterdam"}
    assert _get_dwell_time_and_fee(edge, DWELL, FEES) == (24, 7)


def test_port_extra_added_to_scalar_and_dict():
    edge = {"type": "multimodal", "multimodes": "roads-maritime", "port_name": "Amsterdam"}
    assert _get_dwell_time_and_fee(edge, DWELL, FEES) == (24, 8.5)
    edge = {"type": "multimodal", "multimodes": "railways-maritime", "port_name": "Venezia"}
    dwell, fee = _get_dwell_time_and_fee(edge, DWELL, FEES)
    assert dwell == 0.0 + 12            # no mode-pair dwell configured for railways-maritime here, the port extra alone
    assert fee == {"default": 9.0, "container": 7.0}


def test_no_by_port_key():
    edge = {"type": "multimodal", "multimodes": "roads-maritime", "port_name": "Amsterdam"}
    assert _get_dwell_time_and_fee(edge, {"roads-maritime": 24}, {"roads-maritime": 7}) == (24, 7)


def test_non_multimodal_edge():
    assert _get_dwell_time_and_fee({"type": "waterways", "port_name": "Amsterdam"}, DWELL, FEES) == (0.0, 0.0)


def test_per_cargo_port_extra():
    """29 Oct 2026: a by_port extra may itself be per-cargo (the feeder-port surcharge falls mainly on containers)."""
    fees = {"roads-maritime": 7, "waterways-maritime": {"default": 2, "container": 2, "dry_bulk": 2},
            "by_port": {"Szczecin": {"container": 5.0, "default": 1.7}}}
    edge = {"type": "multimodal", "multimodes": "roads-maritime", "port_name": "Szczecin"}
    assert _get_dwell_time_and_fee(edge, {}, fees)[1] == {"default": 8.7, "container": 12.0}
    edge = {"type": "multimodal", "multimodes": "waterways-maritime", "port_name": "Szczecin"}
    assert _get_dwell_time_and_fee(edge, {}, fees)[1] == {"default": 3.7, "container": 7.0, "dry_bulk": 3.7}
    # scalar extra on a dict base keeps the old behaviour (every class shifted, no key added)
    edge = {"type": "multimodal", "multimodes": "railways-maritime", "port_name": "Venezia"}
    assert _get_dwell_time_and_fee(edge, DWELL, FEES)[1] == {"default": 9.0, "container": 7.0}
