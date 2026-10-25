"""transport_network.py: port-specific terminal fees and dwell times (25 Oct 2026, recalibration round 2).

logistics.loading_fees.by_port and logistics.dwell_times.by_port are optional dicts keyed by the connector's port_name
attribute (the tag that tag_network_attributes.py writes on the sea-port connectors of the tagged network); their value is
ADDED to the mode-pair fee or dwell time of that connector (scalar or per-cargo dict), so a port can be made dearer or
cheaper than its peers. Without the tag or without the key nothing changes (all existing tests hold)."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/src/disruptsc/network/transport_network.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
old = '''def _get_dwell_time_and_fee(edge_attr: dict, dwell_times: dict, loading_fees: dict):
    """Returns the configured values for this edge's multimodes key - each may
    be a scalar or a per-cargo dict; resolved per cargo in _calculate_cost_per_ton."""
    if edge_attr["type"] == "multimodal":
        key = edge_attr.get("multimodes", "")
        return dwell_times.get(key, 0.0), loading_fees.get(key, 0.0)
    return 0.0, 0.0
'''
new = '''def _add_port_extra(base, extra):
    """Add a port-specific extra (scalar) to a mode-pair value (scalar or per-cargo dict)."""
    if extra is None:
        return base
    extra = float(extra)
    if isinstance(base, dict):
        return {k: float(v) + extra for k, v in base.items()}
    return float(base) + extra


def _get_dwell_time_and_fee(edge_attr: dict, dwell_times: dict, loading_fees: dict):
    """Returns the configured values for this edge's multimodes key - each may
    be a scalar or a per-cargo dict; resolved per cargo in _calculate_cost_per_ton.
    ``dwell_times["by_port"]`` / ``loading_fees["by_port"]`` (optional dicts keyed by the
    connector's ``port_name`` attribute, 25 Oct 2026) are added on top for that port's
    connectors: the instrument that pins the Rotterdam/Amsterdam or Genoa/Venice split."""
    if edge_attr["type"] == "multimodal":
        key = edge_attr.get("multimodes", "")
        dwell, fee = dwell_times.get(key, 0.0), loading_fees.get(key, 0.0)
        port = edge_attr.get("port_name")
        if port:
            dwell = _add_port_extra(dwell, (dwell_times.get("by_port") or {}).get(port))
            fee = _add_port_extra(fee, (loading_fees.get("by_port") or {}).get(port))
        return dwell, fee
    return 0.0, 0.0
'''
assert s.count(old) == 1, "fee resolver not found"
s = s.replace(old, new)
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("transport_network.py: by_port fees and dwell times added")
