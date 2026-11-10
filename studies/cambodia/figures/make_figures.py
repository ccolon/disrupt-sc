"""Figures and numbers.tex of the Cambodia compound-flood paper (node A_fig, 10 Nov 2026).

Draws every figure of the paper and the SI from the run tables of the pipeline folder and writes numbers.tex: each number
the text states is a macro put by the figure that shows it (or listed below as a setting of the experiment). Writes
manifest.txt with the sha256 of every input and the code version. Do not edit numbers.tex by hand: rerun this script
after a batch, and diff the new numbers.tex against the old one.

    python studies/cambodia/figures/make_figures.py --runs <Paper_Cambodia/pipeline/runs>
        --data <disrupt-sc-data/Cambodia> --out <folder> [--only fig2 fig3 ...]

Figures: fig1_direct (S3), fig2_simultaneous (H1), fig3_timing (H2), fig4_mechanism (S1), fig5_transition (S2),
figS_settle (horizon), figS_robustness (inventory targets and restoration times).
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fig1_direct  # noqa: E402
import fig2_h1  # noqa: E402
import fig3_timing  # noqa: E402
import fig4_mechanism  # noqa: E402
import fig5_transition  # noqa: E402
import figS_robustness  # noqa: E402
import figS_settle  # noqa: E402
from paper import BASELINE, PARAMS, TRANS, Inputs, Numbers, count, num, style  # noqa: E402

FIGURES = {"fig1": fig1_direct, "fig2": fig2_h1, "fig3": fig3_timing, "fig4": fig4_mechanism,
           "fig5": fig5_transition, "figS_settle": figS_settle, "figS_rob": figS_robustness}
CARBON_PRICE = 75   # USD/tCO2e: the IMF's ambitious 2035 level for Cambodia (lit/D_fuel.md; decision Q10)


def settings(I, N):
    """Settings of the experiment that the text states: freight costs, base (paper_config.yaml) and taxed (the
    transition runs' --set options, read back from their run names)."""
    cfg = yaml.safe_load((HERE.parent / "paper_config.yaml").read_text(encoding="utf-8"))
    base = cfg["logistics"]["basic_cost"]
    tr = I.csv(TRANS)
    sets = {s for v in tr.variant.unique() for s in v.split("+")}
    taxed = {s.split("=")[0].split(".")[-1]: float(s.split("=")[1]) for s in sets}
    N.put("CarbonPrice", str(CARBON_PRICE), "USD/tCO2e, setting: the IMF's ambitious 2035 level for Cambodia (Q10)")
    for mode, name in (("roads", "Roads"), ("waterways", "Waterways"), ("railways", "Rail")):
        N.put(f"Cost{name}Base", num(base[mode], 4 if mode == "waterways" else 3), f"USD per ton-km, {mode}, base")
        N.put(f"Cost{name}Tax", num(taxed[mode], 4), f"USD per ton-km, {mode}, with the tax")
        N.put(f"CostRise{name}", num(100 * (taxed[mode] / base[mode] - 1), 1), f"% rise of the {mode} cost per ton-km")
    # the model as run: one paper run's parameters.yaml, and the networks' baseline table (baseline_aggregates.py)
    class Loader(yaml.SafeLoader):   # parameters.yaml holds python object tags (paths); read them as nothing
        pass
    Loader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)
    prm = yaml.load(I.path(PARAMS).read_text(encoding="utf-8"), Loader=Loader)
    inv = prm["inventory_duration_targets"]["values"]
    for key, name in (("agriculture", "Agri"), ("manufacturing", "Manufacturing"), ("service", "Service"),
                      ("utility", "Utility"), ("transport", "Transport")):
        N.put(f"InvTarget{name}", str(inv[key]), f"days: firms' inventory target for inputs of type {key}")
    N.put("HhInvTargetAgri", str(prm["household_inventory_duration_target"]["values"]["agriculture"]),
          "days: households' inventory target for agricultural goods")
    N.put("InvRestoration", str(prm["inventory_restoration_time"]), "days: inventory restoration time")
    b = I.csv(BASELINE)
    assert b.firms.nunique() == 1 and b.household_points.nunique() == 1
    N.put("FirmCount", count(b.firms.iloc[0]), "firms in the model (firm_table of the paper runs)")


def code_version():
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, capture_output=True, text=True,
                             check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=HERE, capture_output=True, text=True,
                               check=True).stdout.strip()
        return sha + (" + uncommitted changes in studies/cambodia/figures" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, required=True, help="the pipeline folder's runs/")
    ap.add_argument("--data", type=Path, help="disrupt-sc-data/Cambodia (Fig. 1 only)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", nargs="*", choices=list(FIGURES), help="draw these only (numbers.tex is then partial)")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    style()
    I, N = Inputs(a.runs, a.data), Numbers()
    names = a.only or list(FIGURES)
    made = []
    for k in names:
        made.append(FIGURES[k].make(I, a.out, N))
        print(f"{k}: {made[-1].name} ({len(N.M)} macros so far)")
    if not a.only:
        settings(I, N)
    code = code_version()
    today = dt.date.today().isoformat()
    header = [f"Numbers of the Cambodia compound-flood paper, written {today} by studies/cambodia/figures/make_figures.py "
              f"(disrupt-sc {code}) from the run tables of the pipeline folder (sha256 in manifest.txt).",
              "Do not edit by hand: rerun the script after a batch." + (" PARTIAL: --only " + " ".join(a.only)
                                                                        if a.only else "")]
    (a.out / "numbers.tex").write_text(N.tex(header), encoding="utf-8")
    lines = [f"make_figures.py, {today}, disrupt-sc {code}", "", "inputs (sha256):"]
    lines += [f"  {h}  {p}" for p, h in sorted(I.used.items())]
    lines += ["", "figures:"] + [f"  {p.name}" for p in made] + ["", f"numbers.tex: {len(N.M)} macros"]
    (a.out / "manifest.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"numbers.tex: {len(N.M)} macros; manifest: {len(I.used)} inputs")


if __name__ == "__main__":
    main()
