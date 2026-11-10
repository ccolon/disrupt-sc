"""Shared pieces of the Cambodia paper's figures and numbers (node A_fig, 10 Nov 2026).

- Print style for Economic Modelling (Elsevier): widths 90 / 140 / 190 mm, 7-8 pt text, vector PDF with embedded
  TrueType fonts, PNG at 300 dpi.
- Palette (dataviz reference palette, light surface): the basins take its first three categorical slots, which its
  documentation validates for colour-vision deficiency on all pairs; closure lengths take the ordinal blue ramp
  (steps 250 / 450 / 650); the compound case is drawn in ink, the sum of the singles in muted grey.
- Inputs: every table a figure reads goes through Inputs, which records its sha256 for the manifest.
- Numbers: the macros of numbers.tex (one name, one value, one comment each; no duplicates).
- Tables: loaders that pivot the runs tables to one loss per network and scenario (mUSD) and fail on duplicates.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

MM = 1 / 25.4
WIDTH = {"single": 90 * MM, "onehalf": 140 * MM, "double": 190 * MM}

INK, INK2, MUTED, HAIR, SHADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#f0efec"
BASINS = ("saigon", "mekong", "tonle")
BASIN_COLOR = {"saigon": "#1baf7a", "mekong": "#eb6834", "tonle": "#2a78d6"}
BASIN_LABEL = {"saigon": "Saigon", "mekong": "Mekong", "tonle": "Tonle Sap"}
BASIN_WORD = {"saigon": "Saigon", "mekong": "Mekong", "tonle": "Tonle"}
DURATIONS = (4, 8, 12)
DUR_COLOR = {4: "#86b6ef", 8: "#2a78d6", 12: "#104281"}
WORD = {0: "Zero", 4: "Four", 6: "Six", 8: "Eight", 12: "Twelve", 16: "Sixteen", 24: "TwentyFour", 36: "ThirtySix",
        48: "FortyEight"}
EXCESS = "#f3b9b8"      # light tint of the reference red: the excess of the compound case over the singles
TAX = "#e34948"         # the carbon-tax runs (Fig. 5), against the base in ink
INV_COLOR = "#2a78d6"   # inventory-target variants (blue), restoration variants (orange); marker style tells x0.5/x2
REST_COLOR = "#eb6834"

# Tables of the pipeline folder's runs/ (copies of the cluster's, sha256 checked when copied; registry.yaml)
GRID = {d: f"grid_d{d}_20261108_runs.csv" for d in DURATIONS}
PAIR, PAIR_DAILY = "pair_d12_20261108_runs.csv", "pair_d12_20261108_daily.csv"
ROB = "rob_d12_20261108_runs.csv"
TRANS, TRANS_DAILY, TRANS_NULL = ("trans_d12_20261109_runs.csv", "trans_d12_20261109_daily.csv",
                                  "trans_logs/trans_null.csv")
OVERLAP = "overlap_logs"
# Baseline aggregates of the d = 12 grid's networks (studies/cambodia/baseline_aggregates.py on the cluster) and the
# parameters.yaml of one paper run (the model settings the text states)
BASELINE = "baseline_d12_20261108.csv"
PARAMS = "params/lag0_d12_s1_t116_parameters.yaml"


def style():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "legend.fontsize": 6.5, "legend.frameon": False, "legend.handlelength": 1.6,
        "axes.linewidth": 0.6, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlelocation": "left",
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": HAIR, "grid.linewidth": 0.5, "axes.axisbelow": True,
        "lines.linewidth": 1.2, "lines.markersize": 3.5, "errorbar.capsize": 2,
        "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 300, "figure.dpi": 150,
    })


def panel(ax, letter, title):
    ax.set_title(f"({letter}) {title}", loc="left", fontsize=8)


def save(fig, out: Path, name: str):
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out / f"{name}.pdf"


def ci(x):
    """Mean and 95 % interval (t over the networks)."""
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - h, x.mean() + h


def num(x, nd=2):
    """A number for LaTeX text: fixed decimals, a true minus sign, no negative zero."""
    s = f"{x:.{nd}f}"
    if s.startswith("-"):
        s = s[1:] if float(s) == 0 else r"\ensuremath{-}" + s[1:]
    return s


def count(n):
    return f"{int(n):,}"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class Inputs:
    """Paths of the inputs; records the sha256 of every file read."""

    def __init__(self, runs: Path, data: Path | None):
        self.runs, self.data, self.used = runs, data, {}

    def path(self, rel: str, base: str = "runs") -> Path:
        root = self.runs if base == "runs" else self.data
        if root is None:
            raise SystemExit(f"--{base} is needed for {rel}")
        p = root / rel
        if p.is_file() and str(p) not in self.used:
            self.used[str(p)] = sha256(p)
        return p

    def csv(self, rel: str, **kw) -> pd.DataFrame:
        return pd.read_csv(self.path(rel), **kw)


class Numbers:
    """The macros of numbers.tex, in the order they are put."""

    def __init__(self):
        self.M = {}

    def put(self, name: str, value: str, comment: str = ""):
        assert re.fullmatch(r"[A-Za-z]+", name), f"macro name {name!r}: letters only"
        assert name not in self.M, f"macro {name} put twice"
        assert value not in ("", "nan") and "nan" not in value, f"macro {name}: value {value!r}"
        self.M[name] = (value, comment)

    def ci(self, name: str, x, nd: int, comment: str, scale: float = 1.0, shift: float = 0.0):
        """Mean and its interval as three macros: <name>, <name>Lo, <name>Hi."""
        m, lo, hi = ci((np.asarray(x, float) + shift) * scale)
        self.put(name, num(m, nd), comment)
        self.put(name + "Lo", num(lo, nd), "lower end of the 95 % interval (t over networks)")
        self.put(name + "Hi", num(hi, nd), "upper end of the 95 % interval (t over networks)")
        return m, lo, hi

    def tex(self, header: list[str]) -> str:
        lines = [f"% {h}" for h in header]
        for k, (v, c) in self.M.items():
            lines.append(f"\\newcommand{{\\{k}}}{{{v}}}" + (f"  % {c}" if c else ""))
        return "\n".join(lines) + "\n"


# ---------------- tables ----------------
def grid_wide(I: Inputs, d: int) -> pd.DataFrame:
    """Household loss (mUSD) by network (rows) and scenario (columns) of the grid batch for closure length d."""
    G = I.csv(GRID[d])
    return G.pivot(index="seed", columns="scenario", values="loss_households") / 1e6


def pair_wide(I: Inputs) -> pd.DataFrame:
    """Household loss (mUSD) of the two-flood runs (Mekong + Tonle Sap, d = 12) by network and tau."""
    P = I.csv(PAIR)
    return P.pivot(index="seed", columns="tau", values="loss_households") / 1e6


def pair_ratio(I: Inputs) -> pd.DataFrame:
    """Two-flood loss / (single Mekong + single Tonle Sap) of the same network, by network and tau."""
    P, G = pair_wide(I), grid_wide(I, 12)
    singles = (G.single_mekong + G.single_tonle).loc[P.index]
    return P.div(singles, axis=0)


def rob_wide(I: Inputs) -> pd.DataFrame:
    """Loss (mUSD) by (variant, network) and key (single_mekong, single_tonle, tau0, tau12, tau24), with the base
    (inventory targets x1, restoration 30 days) from the pair and grid batches; adds singles, R<tau> and X<tau>."""
    rob = I.csv(ROB)
    nets = sorted(int(s) for s in rob.seed.unique())
    rows = [(r.variant, int(r.seed), r.scenario if r.scenario.startswith("single_") else f"tau{int(r.tau)}",
             r.loss_households / 1e6) for r in rob.itertuples()]
    P, G = pair_wide(I), grid_wide(I, 12)
    for t in (0, 12, 24):
        rows += [("base", s, f"tau{t}", P.loc[s, t]) for s in nets]
    for sc in ("single_mekong", "single_tonle"):
        rows += [("base", s, sc, G.loc[s, sc]) for s in nets]
    L = pd.DataFrame(rows, columns=["variant", "seed", "key", "loss"])
    assert not L.duplicated(["variant", "seed", "key"]).any(), "duplicate robustness runs"
    L = L.pivot(index=["variant", "seed"], columns="key", values="loss")
    assert L.notna().all().all() and len(L) == 5 * len(nets), "missing robustness runs"
    L["singles"] = L.single_mekong + L.single_tonle
    for t in (0, 12, 24):
        L[f"R{t}"] = L[f"tau{t}"] / L.singles
        L[f"X{t}"] = L[f"tau{t}"] - L.singles
    return L
