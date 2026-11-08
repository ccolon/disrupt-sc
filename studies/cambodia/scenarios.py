"""Flood scenarios of the Cambodia compound-flood paper: road closures by river basin, single, simultaneous or
in succession (5 Nov 2026, port to v2).

A basin is a value of a road-edge attribute of Transport/transport.gpkg: `flood_v3` (the paper's footprint,
CLIMADA, GloFAS 27 Sep 2023: Saigon 3, Mekong 8, Tonle Sap 25 edges) or `flood_disruption` (v4: 6 / 7 / 20,
the attribute the v2 network shipped with). Values are read from the network, never typed: the local config of
9 Jul 2026 wrote Tonle Sap double-encoded and closed no edge (KI-52). `check_footprint` refuses a footprint
whose edge counts differ from the recorded ones.

Scenario names:
  none                 undisturbed (stationarity check)
  single_<basin>       one basin closed from day 1 for `duration` days (basin = saigon | mekong | tonle)
  simul                the three basins closed together from day 1
  lag<L>               succession Saigon -> Mekong -> Tonle Sap, each closed `duration` days, starts L days apart
                       (lag0 = simul; L = duration: back-to-back; L = duration + 1: one open day between events)
  pair_<a>_<b>_tau<T>  two basins only, each closed `duration` days; T = start of b - start of a, any sign: T >= 0
                       closes a from day 1 and b from day 1 + T, T < 0 closes b from day 1 and a from day 1 - T
                       (e.g. pair_mekong_tonle_tau-5: Tonle Sap from day 1, Mekong from day 6; tau0: both from day 1).
                       Added 8 Nov 2026 for the two-flood curve (R_pair, the user's order question).
"""
from __future__ import annotations

from pathlib import Path

# The cascade order of the paper's runs (cluster config, Aug-Dec 2025): Saigon, then Mekong, then Tonle Sap.
BASIN_ORDER = ("saigon", "mekong", "tonle")
BASIN_LABEL = {"saigon": "Saigon", "mekong": "Siem Bok (Mekong)", "tonle": "St. Sen (Tonlè Sap)"}

FOOTPRINTS = {
    # attribute in the roads layer -> expected number of closed edges per basin
    "v3": {"attribute": "flood_v3", "edges": {"saigon": 3, "mekong": 8, "tonle": 25}},
    "v4": {"attribute": "flood_disruption", "edges": {"saigon": 6, "mekong": 7, "tonle": 20}},
}


def _event(attribute: str, basin: str, start: int, duration: int) -> dict:
    return {"type": "transport_disruption", "description_type": "edge_attributes", "attribute": attribute,
            "values": [BASIN_LABEL[basin]], "start_time": int(start), "duration": int(duration)}


def disruptions(scenario: str, duration: int, footprint: str = "v3") -> list[dict]:
    """The `disruptions` list of *scenario* (see the module docstring)."""
    att = FOOTPRINTS[footprint]["attribute"]
    if scenario == "none":
        return []
    if scenario.startswith("single_"):
        basin = scenario[len("single_"):]
        if basin not in BASIN_LABEL:
            raise ValueError(f"unknown basin in {scenario!r}; expected one of {sorted(BASIN_LABEL)}")
        return [_event(att, basin, 1, duration)]
    if scenario == "simul":
        return [_event(att, b, 1, duration) for b in BASIN_ORDER]
    if scenario.startswith("lag"):
        lag = int(scenario[3:])
        if lag < 0:
            raise ValueError(f"negative lag in {scenario!r}")
        return [_event(att, b, 1 + i * lag, duration) for i, b in enumerate(BASIN_ORDER)]
    if scenario.startswith("pair_"):
        a, b, tau = parse_pair(scenario)
        return [_event(att, a, 1 + max(0, -tau), duration), _event(att, b, 1 + max(0, tau), duration)]
    raise ValueError(f"unknown scenario {scenario!r}")


def parse_pair(scenario: str) -> tuple[str, str, int]:
    """pair_<a>_<b>_tau<T> -> (a, b, T); T = start of b - start of a."""
    parts = scenario.split("_")
    if len(parts) != 4 or parts[0] != "pair" or not parts[3].startswith("tau"):
        raise ValueError(f"pair scenario must read pair_<a>_<b>_tau<T>, got {scenario!r}")
    a, b = parts[1], parts[2]
    for basin in (a, b):
        if basin not in BASIN_LABEL:
            raise ValueError(f"unknown basin {basin!r} in {scenario!r}; expected one of {sorted(BASIN_LABEL)}")
    if a == b:
        raise ValueError(f"the two basins of {scenario!r} must differ")
    return a, b, int(parts[3][3:])


def last_closed_day(scenario: str, duration: int) -> int:
    """Last day on which some road of the scenario is closed (0 for none)."""
    if scenario == "none":
        return 0
    if scenario.startswith("pair_"):
        return abs(parse_pair(scenario)[2]) + duration   # second event: days 1 + |T| .. |T| + duration
    lag = int(scenario[3:]) if scenario.startswith("lag") else 0
    return 2 * lag + duration          # third event: days 1 + 2 lag .. 2 lag + duration


def check_footprint(gpkg: Path, footprint: str = "v3") -> dict:
    """Number of road edges per basin in *gpkg*; raises if it differs from the recorded counts."""
    import geopandas as gpd

    spec = FOOTPRINTS[footprint]
    roads = gpd.read_file(gpkg, layer="roads")
    if spec["attribute"] not in roads.columns:
        raise SystemExit(f"{gpkg}: no attribute {spec['attribute']!r} in the roads layer (footprint {footprint}); "
                         f"columns: {list(roads.columns)}")
    counts = {b: int((roads[spec["attribute"]] == BASIN_LABEL[b]).sum()) for b in BASIN_ORDER}
    if counts != spec["edges"]:
        raise SystemExit(f"{gpkg}: footprint {footprint} closes {counts} edges, expected {spec['edges']}")
    return counts
