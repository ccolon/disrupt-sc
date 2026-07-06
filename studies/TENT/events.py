"""Load and normalize the TENT flood-event table.

Source: ``<data>/TENT/Disruption/results_disrupt_sc.xlsx`` (sheet ``Sheet1``).
Each row is one flooded edge for one flood event. An *event* is a unique
(``catchement``, ``return_period``) combination; it floods one or more road
edges (``edge_id`` == the model's transport-edge ``id``) and has a recovery
duration in **days** (``recovery_duration``, uniform across the event's edges).

The normalized event carries:
  - key            (catchment, return_period)
  - edge_ids       sorted list of int edge ids to disrupt
  - duration_days  float, the event's recovery duration
  - duration_steps int, days -> whole time-steps at the run's resolution
                   (daily => round(days), floored at 1 so no flood is a no-op)

Run standalone to print a summary:  python studies/TENT/events.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# data root: <repo>/../disrupt-sc-data  (see src/disruptsc/paths.py)
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_XLSX = ROOT.parent / "disrupt-sc-data" / "TENT" / "Disruption" / "results_disrupt_sc.xlsx"


@dataclass(frozen=True)
class FloodEvent:
    catchment: int
    return_period: int
    edge_ids: tuple[int, ...]
    duration_days: float
    duration_steps: int

    @property
    def key(self) -> str:
        return f"c{self.catchment}_rp{self.return_period}"


def _days_to_steps(days: float, days_per_step: float) -> int:
    """Days -> whole time-steps, floored at 1 (a flood always closes >= 1 step)."""
    return max(1, int(round(days / days_per_step)))


def load_events(xlsx_path: str | Path = DEFAULT_XLSX,
                days_per_step: float = 1.0,
                return_periods: list[int] | None = None) -> list[FloodEvent]:
    """Return the list of FloodEvents, optionally filtered to *return_periods*.

    *days_per_step* converts the day-valued ``recovery_duration`` to model
    steps (1.0 for daily resolution, 7.0 for weekly). Events are ordered by
    (return_period, catchment) for reproducible, resumable batches.
    """
    cols = ["edge_id", "catchement", "return_period", "recovery_duration"]
    df = pd.read_excel(xlsx_path, usecols=cols)
    if return_periods is not None:
        df = df[df["return_period"].isin(return_periods)]

    events: list[FloodEvent] = []
    for (catchment, rp), grp in df.groupby(["catchement", "return_period"], sort=True):
        edge_ids = tuple(sorted(int(e) for e in grp["edge_id"].unique()))
        # duration is uniform across an event's edges; max() guards against any drift
        duration_days = float(grp["recovery_duration"].max())
        events.append(FloodEvent(
            catchment=int(catchment),
            return_period=int(rp),
            edge_ids=edge_ids,
            duration_days=duration_days,
            duration_steps=_days_to_steps(duration_days, days_per_step),
        ))
    events.sort(key=lambda e: (e.return_period, e.catchment))
    return events


def all_flooded_edge_ids(xlsx_path: str | Path = DEFAULT_XLSX) -> set[int]:
    df = pd.read_excel(xlsx_path, usecols=["edge_id"])
    return set(int(e) for e in df["edge_id"].unique())


if __name__ == "__main__":
    evs = load_events(days_per_step=1.0)
    print(f"{len(evs)} events from {DEFAULT_XLSX}")
    n_edges = [len(e.edge_ids) for e in evs]
    dur = [e.duration_days for e in evs]
    print(f"edges/event: min={min(n_edges)} max={max(n_edges)} mean={sum(n_edges)/len(n_edges):.2f}")
    print(f"duration_days: min={min(dur):.3f} max={max(dur):.1f} mean={sum(dur)/len(dur):.1f}")
    print(f"duration_steps (daily): min={min(e.duration_steps for e in evs)} "
          f"max={max(e.duration_steps for e in evs)}")
    by_rp: dict[int, int] = {}
    for e in evs:
        by_rp[e.return_period] = by_rp.get(e.return_period, 0) + 1
    print("events per return_period:", dict(sorted(by_rp.items())))
    print("first 3:", evs[:3])
