"""Construct the shock-heterogeneity draws for the idealized experiments (Sec. 3.5).

The experiment holds the destroyed capital fixed at ``--total`` and varies only the
resolution at which it is concentrated: all sectors and cantones (the homogeneous
reference), then one sector, one province, one canton, one province-sector set, or
one canton-sector set.

Because a single unit rarely holds enough capital to absorb the whole amount, a draw
is generally a *group* of units. Three rules define the groups:

1. **Validity.**  A group is valid when its capital is at least the destroyed amount,
   so that the shock can be placed without overflowing. The share of the group's
   capital actually destroyed (``destroyed_fraction``) is recorded per draw: it is
   the mechanism the experiment is about -- concentration means a larger share of a
   smaller economic mass -- and is reported, not controlled for.

2. **Partition.**  Units are partitioned: every unit belongs to exactly one draw.
   This replaces the earlier all-valid-pairs enumeration, which over-represented
   units that paired easily and silently dropped units too small to qualify with
   any partner.

3. **Contiguity.**  Spatial groups must be connected in the canton adjacency graph,
   since a disaster footprint is contiguous. Sector groups carry no analogous
   constraint: a disaster has no reason to strike input-output neighbours together.

For the crossed resolutions, places are first partitioned into connected clusters,
then the (place, sector) cells inside each cluster are partitioned into as many
draws as the cluster's capital supports.

Capital is read firm by firm from a run export and grouped up to cells, so a group
declared valid here really can absorb the shock in the run that destroys it.

Usage
-----
    python build_hetero_draws.py --run <run_dir> --out <dir> [--total 2510.1]
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

LOG = logging.getLogger("hetero_draws")

RESOLUTIONS = ("sector", "province", "canton", "province_sector", "canton_sector")


# --------------------------------------------------------------------------
# name normalisation (same convention as build_model_shock.py)
# --------------------------------------------------------------------------
def norm(x: object) -> str:
    """Uppercase, de-accent, drop punctuation and spaces, for matching only."""
    if x is None:
        return ""
    s = str(x).replace("\ufffd", "N")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s.upper())


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
def load_capital(run_dir: Path) -> pd.Series:
    """Capital per (canton, province, sector), read from the model's own firms.

    Taken firm by firm from a run export -- active plus idle capital at t=0, which is
    capital_to_value_added_ratio times annual value added -- and grouped up to cells.

    It must come from the model rather than be reconstructed from the spatial input
    file. A firm's capital tracks its equilibrium production, and that is a network
    outcome: which clients selected it, under the localization weights and the
    coverage filter. It is not proportional to the output column of firms.geojson.
    Sizing draws on that column instead gets sector totals exactly right, since they
    are fixed by the input--output table, while getting the split across cantones
    badly wrong -- Quito came out at $118bn against the $4.4bn the model gives it.
    Draws built that way ask the run to destroy far more capital than the group holds.
    """
    fd = pd.read_csv(run_dir / "firm_data.csv",
                     usecols=["time_step", "firm", "active_capital", "idle_capital"])
    t0 = fd[fd["time_step"] == fd["time_step"].min()]
    per_firm = (t0["active_capital"] + t0["idle_capital"]).groupby(t0["firm"]).sum()

    gj = json.loads((run_dir / "firm_table.geojson").read_text(encoding="utf-8"))
    rows = []
    for f in gj["features"]:
        p = f["properties"]
        rows.append({"canton": p["subregion_canton"], "province": p["subregion_province"],
                     "sector": p["sector"], "capital": per_firm.get(p["id"], 0.0)})
    cap = (pd.DataFrame(rows).groupby(["canton", "province", "sector"]).capital.sum())
    cap = cap[cap > 0]
    LOG.info("model capital from %s: $%.0fM over %d cells, %d cantones, %d sectors",
             run_dir.name, cap.sum(), len(cap),
             cap.index.get_level_values("canton").nunique(),
             cap.index.get_level_values("sector").nunique())
    return cap.rename("capital")


def load_adjacency(path: Path, cantones: list[str]) -> dict[str, set[str]]:
    """Canton adjacency, keys crosswalked onto the model's exact canton strings."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    by_norm_full = {norm(c): c for c in cantones}
    # canton-only key, for entries filed under a pre-2007 province
    by_norm_canton: dict[str, list[str]] = {}
    for c in cantones:
        by_norm_canton.setdefault(norm(c.split(" - ", 1)[-1]), []).append(c)

    def resolve(name: str) -> str | None:
        """Exact -> canton-only -> containment -> close-spelling, in that order.

        The adjacency file predates the model's naming in places ("RIOVERDE" vs
        "RIO VERDE", "EMPALME" vs "EL EMPALME", "CHAGUARPAMBA" vs "CHAHUARPAMBA",
        "ORELLANA - ORELLANA" vs "ORELLANA - FRANCISCO DE ORELLANA") and still files
        Santa Elena's cantones under Guayas.
        """
        n = norm(name)
        if n in by_norm_full:
            return by_norm_full[n]
        tail = norm(str(name).split(" - ", 1)[-1])
        cand = by_norm_canton.get(tail)
        if cand and len(cand) == 1:
            return cand[0]
        # containment on the canton part: EMPALME in ELEMPALME, ORELLANA in FRANCISCODEORELLANA
        hits = [c for t, cs in by_norm_canton.items() for c in cs
                if len(tail) >= 5 and (tail in t or t in tail)]
        if len(set(hits)) == 1:
            return hits[0]
        # close spelling, same length class: CHAGUARPAMBA ~ CHAHUARPAMBA
        best, score = None, 0.0
        for t, cs in by_norm_canton.items():
            if len(cs) != 1 or not tail or abs(len(t) - len(tail)) > 4:
                continue
            r = SequenceMatcher(None, tail, t).ratio()
            if r > score:
                best, score = cs[0], r
        return best if score >= 0.85 else None

    adj: dict[str, set[str]] = {c: set() for c in cantones}
    unresolved = set()
    for k, vs in raw.items():
        rk = resolve(k)
        if rk is None:
            unresolved.add(k)
            continue
        for v in vs:
            rv = resolve(v)
            if rv is None:
                unresolved.add(v)
            elif rv != rk:
                adj[rk].add(rv)
                adj[rv].add(rk)
    if unresolved:
        LOG.warning("adjacency names not matched to the model (%d): %s",
                    len(unresolved), sorted(unresolved)[:10])
    isolated = [c for c, v in adj.items() if not v]
    if isolated:
        LOG.warning("cantones with no neighbour: %s", isolated)
    return adj


# --------------------------------------------------------------------------
# partitioning
# --------------------------------------------------------------------------
def partition_free(capital: pd.Series, total: float) -> list[list]:
    """Partition units into groups of capital >= total, ignoring adjacency.

    Units big enough alone become singletons. The rest are packed largest-first:
    each group starts from the largest unassigned unit and takes the next largest
    until it is valid. Any tail too small to stand alone is merged into the last
    group, so no unit is discarded.
    """
    s = capital.sort_values(ascending=False)
    groups = [[u] for u in s.index[s >= total]]
    rest = list(s.index[s < total])

    cur: list = []
    acc = 0.0
    for u in rest:
        cur.append(u)
        acc += float(s[u])
        if acc >= total:
            groups.append(cur)
            cur, acc = [], 0.0
    if cur:
        if groups:
            groups[-1].extend(cur)          # absorb the tail; keeps the group valid
        else:
            groups.append(cur)              # degenerate: everything together
    return groups


def partition_contiguous(capital: pd.Series, adj: dict, total: float) -> list[list]:
    """Partition places into connected groups of capital >= total.

    Places big enough alone become singletons. The remainder is grown from the
    *smallest* unassigned place (the hardest to place), repeatedly annexing the
    richest unassigned neighbour, until the group is valid. A group that exhausts
    its connected component while still short is merged into an adjacent finished
    group; if it has no such neighbour it is reported and dropped.
    """
    s = capital.sort_values(ascending=False)
    groups = [[u] for u in s.index[s >= total]]
    assigned = {u for g in groups for u in g}
    remaining = {u for u in s.index if u not in assigned}

    orphans: list[list] = []
    while remaining:
        seed = min(remaining, key=lambda u: float(s[u]))
        group, acc = [seed], float(s[seed])
        remaining.discard(seed)
        while acc < total:
            frontier = {n for u in group for n in adj.get(u, ())} & remaining
            if not frontier:
                break
            nxt = max(frontier, key=lambda u: float(s[u]))
            group.append(nxt)
            acc += float(s[nxt])
            remaining.discard(nxt)
        (groups if acc >= total else orphans).append(group)

    for og in orphans:
        # Merge each short group into its *poorest* adjacent group. Picking the
        # poorest keeps large single-unit draws (Quito, Guayaquil) intact: absorbing
        # a remainder into them would replace a clean "this city alone" draw with a
        # sprawling one whose destroyed fraction is near zero.
        nbrs = {n for u in og for n in adj.get(u, ())}
        cands = [g for g in groups if nbrs & set(g)]
        if not cands:
            LOG.warning("dropped -- short and with no adjacent group: %s", og)
            continue
        min(cands, key=lambda g: float(s[g].sum())).extend(og)
    return groups


# --------------------------------------------------------------------------
# draw construction
# --------------------------------------------------------------------------
def build(resolution: str, cap: pd.Series, adj: dict, total: float) -> pd.DataFrame:
    by_canton = cap.groupby(level="canton").sum()
    by_prov = cap.groupby(level="province").sum()

    def prov_adj() -> dict[str, set[str]]:
        c2p = {c: p for c, p in cap.index.droplevel("sector").unique()}
        out: dict[str, set[str]] = {p: set() for p in by_prov.index}
        for c, ns in adj.items():
            for n in ns:
                if c in c2p and n in c2p and c2p[c] != c2p[n]:
                    out[c2p[c]].add(c2p[n])
                    out[c2p[n]].add(c2p[c])
        return out

    rows = []
    if resolution == "sector":
        groups = partition_free(cap.groupby(level="sector").sum(), total)
        for i, g in enumerate(groups):
            k = float(cap[cap.index.get_level_values("sector").isin(g)].sum())
            rows.append((i, "|".join(sorted(g)), len(g), k))

    elif resolution in ("province", "canton"):
        level = resolution
        series = by_prov if resolution == "province" else by_canton
        graph = prov_adj() if resolution == "province" else adj
        for i, g in enumerate(partition_contiguous(series, graph, total)):
            rows.append((i, "|".join(sorted(g)), len(g), float(series[g].sum())))

    else:  # crossed: cluster places first, then partition cells inside each cluster
        level = "province" if resolution.startswith("province") else "canton"
        series = by_prov if level == "province" else by_canton
        graph = prov_adj() if level == "province" else adj
        draw = 0
        for cluster in partition_contiguous(series, graph, total):
            cells = cap[cap.index.get_level_values(level).isin(cluster)]
            cells = cells[cells > 0]
            if cells.empty:
                continue
            for g in partition_free(cells, total):
                # index tuples are (canton, province, sector); label by the place
                # at this resolution plus the sector
                label = "|".join(sorted(
                    f"{c if level == 'canton' else p}_{s}" for c, p, s in g))
                rows.append((draw, label, len(g), float(cells[g].sum())))
                draw += 1

    df = pd.DataFrame(rows, columns=["draw_id", "units", "n_units", "group_capital_mUSD"])
    df.insert(0, "resolution", resolution)
    df["destroyed_fraction"] = total / df["group_capital_mUSD"]
    # Stamp the build total so the draw list is self-describing: run_hetero.py
    # derives its destroyed total from this column and refuses a mismatching
    # explicit --total (the partition is only valid for the total it was built at).
    df["total_mUSD"] = total
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, type=Path, help="run dir holding firm_data.csv and firm_table.geojson")
    ap.add_argument("--adjacency", type=Path,
                    default=Path(r"C:/Users/Celian/OneDrive/WorldBank/Ecuador/Data/Structured/Admin/canton_adjacency.json"))
    ap.add_argument("--total", type=float, default=2510.1, help="destroyed capital, mUSD")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cap = load_capital(args.run)
    adj = load_adjacency(args.adjacency, sorted(cap.index.get_level_values("canton").unique()))

    args.out.mkdir(parents=True, exist_ok=True)
    frames = []
    for res in RESOLUTIONS:
        df = build(res, cap, adj, args.total)
        df.to_csv(args.out / f"draws_{res}.csv", index=False)
        frames.append(df)
        LOG.info("%-16s %4d draws | units/draw %.1f | destroyed fraction %.1f%%-%.1f%% (median %.1f%%)",
                 res, len(df), df.n_units.mean(),
                 100 * df.destroyed_fraction.min(), 100 * df.destroyed_fraction.max(),
                 100 * df.destroyed_fraction.median())
    allf = pd.concat(frames, ignore_index=True)
    allf.to_csv(args.out / "draws_all.csv", index=False)
    LOG.info("wrote %d draws to %s", len(allf), args.out)


if __name__ == "__main__":
    main()
