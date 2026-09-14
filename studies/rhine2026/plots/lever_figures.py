"""F7 (adaptation levers) and F8 (sensitivity band) from a batch of paired runs.

    python studies/rhine2026/plots/lever_figures.py --runs-dir C:/dsc_runs/rhine2026 --prefix 2026_fc0910_ \
        --base base --levers deep20,fleet40,fleet20,stock7,stock7t,rail04,package \
        --grid liq60,floors_m10,floors_p10,inv050,inv150,lr0,lr1,nopool,seed1,seed2 \
        --out studies/rhine2026/figures --csv studies/rhine2026/additional_data/levers_20260911.csv

Every run is summarised with compare_runs.run_summary (gross / net / delay accounting, weekly series).
F7: avoided German and EU value-added loss by lever (gross bars, net markers, % of the base) and the
weekly German loss of the base and the levers. F8: the German loss of the sensitivity runs against the
base (dot plot, % of a quarter). The table behind both goes to --csv.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "plots"))
from compare_runs import run_summary                     # noqa: E402
from scenario_figures import INK, INK2, SERIES, SURFACE, style  # noqa: E402

LEVER_LABELS = {
    "deep20": "Fairway +20 cm (Abladeoptimierung Mittelrhein)",
    "fleet40": "Tank barges sail to 40 cm",
    "fleet20": "Low-water bulk fleet (sails to 20 cm)",
    "stock7": "+7 days of input stocks, all buyers",
    "stock7t": "+7 days of stocks, barge-dependent buyers",
    "rail04": "Rail at the bulk rate (tank-car trains)",
    "package": "Package: fairway + fleet + stocks",
}
GRID_LABELS = {
    "liq60": "tanker floor 60 cm (base 50)",
    "floors_m10": "all floors −10 cm",
    "floors_p10": "all floors +10 cm",
    "inv050": "input stocks × 0.5",
    "inv150": "input stocks × 1.5",
    "lr0": "Lower Rhine surcharge factor 0",
    "lr1": "Lower Rhine surcharge factor 1",
    "nopool": "no input pooling (region-keyed inputs)",
    "seed1": "supply-chain draw, seed 1",
    "seed2": "supply-chain draw, seed 2",
    "seed3": "supply-chain draw, seed 3",
    "seed4": "supply-chain draw, seed 4",
    "seed5": "supply-chain draw, seed 5",
    "seed6": "supply-chain draw, seed 6",
    "seed7": "supply-chain draw, seed 7",
    "seed8": "supply-chain draw, seed 8",
    "seed9": "supply-chain draw, seed 9",
    "seed10": "supply-chain draw, seed 10",
    "fleet40": "tanker floor 40 cm (base 50)",
}


def summarise_from_batch(csv_path: Path, prefix: str, names: list[str]) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    """Batch summary written by compare_runs.py --csv (one row per run) plus the weekly DEU table of the
    companion .txt (compare_runs.py --weekly DEU): the cluster archive carries firm-level series for a few
    runs only."""
    tab = pd.read_csv(csv_path)
    tab["run"] = tab["run"].astype(str).str.replace(prefix, "", regex=False)
    tab = tab.set_index("run")
    weekly = {}
    txt = csv_path.with_suffix(".txt")
    if txt.exists():
        lines = txt.read_text(encoding="utf-8", errors="replace").splitlines()
        start = next((i for i, l in enumerate(lines) if "weekly value-added loss of DEU" in l), None)
        if start is not None:
            block = [l for l in lines[start + 1:] if l.strip()]
            header = block[0].split()
            rows = []
            for l in block[2:]:
                parts = l.split()
                if not parts or not parts[0].isdigit():
                    break
                rows.append([float(x) if x != "NaN" else float("nan") for x in parts])
            w = pd.DataFrame(rows, columns=["time_step"] + header).set_index("time_step")
            for c in w.columns:
                weekly[c.replace(prefix, "")] = w[c]
    keep = [n for n in names if n in tab.index]
    return tab.loc[keep], weekly


def summarise(runs_dir: Path, prefix: str, names: list[str], rate: float) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    rows, weekly = {}, {}
    for n in names:
        run = runs_dir / f"{prefix}{n}"
        if not (run / "firm_data.csv").exists():
            print(f"   missing: {run}")
            continue
        row, wk = run_summary(run, rate_per_year=rate)
        rows[n] = row
        weekly[n] = wk["DEU"] if "DEU" in wk.columns else wk["EU_mUSD"]
    return pd.DataFrame(rows).T, weekly


def lever_table(base: pd.Series, levers: pd.DataFrame, labels: dict) -> pd.DataFrame:
    out = []
    for n, r in levers.iterrows():
        rec = {"run": n, "label": labels.get(n, n)}
        for c in ("DEU", "EU"):
            g, net = float(r[f"{c}_cum_mUSD"]), float(r[f"{c}_net_mUSD"])
            bg, bnet = float(base[f"{c}_cum_mUSD"]), float(base[f"{c}_net_mUSD"])
            rec[f"{c}_gross_mUSD"] = g
            rec[f"{c}_net_mUSD"] = net
            rec[f"{c}_avoided_gross_mUSD"] = bg - g
            rec[f"{c}_avoided_net_mUSD"] = bnet - net
            rec[f"{c}_avoided_gross_%"] = 100 * (bg - g) / bg if bg else np.nan
        rec["DEU_peak_%week"] = float(r["DEU_peak_%week"])
        rec["DEU_peak_week"] = r["DEU_peak_week"]
        rec["DEU_delay_mUSD"] = float(r["DEU_delay_mUSD"])
        out.append(rec)
    return pd.DataFrame(out).set_index("run")


def fig_levers(base: pd.Series, table: pd.DataFrame, weekly: dict[str, pd.Series], base_name: str, out: Path,
               first_week: str = "22 June 2026"):
    order = table.sort_values("DEU_avoided_gross_mUSD").index.tolist()   # largest at the top of a barh
    fig = plt.figure(figsize=(11, 8.2))
    fig.patch.set_facecolor(SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0], hspace=0.55, wspace=0.18)
    for j, c in enumerate(("DEU", "EU")):
        ax = fig.add_subplot(gs[0, j])
        y = np.arange(len(order))
        g = table.loc[order, f"{c}_avoided_gross_mUSD"].to_numpy()
        net = table.loc[order, f"{c}_avoided_net_mUSD"].to_numpy()
        ax.barh(y, g, color=SERIES[0], height=0.62, label="gross loss avoided")
        ax.scatter(net, y, color=INK, s=22, zorder=3, label="net loss avoided (backlog left)")
        base_g = float(base[f"{c}_cum_mUSD"])
        pad = 0.02 * max(abs(g).max(), abs(net).max(), 1)
        for yi, v, nv in zip(y, g, net):
            ax.text(max(v, nv, 0) + pad, yi, f"{v:,.0f} ({100 * v / base_g:+.0f} %)",
                    va="center", fontsize=7, color=INK2)
        ax.set_yticks(y)
        ax.set_yticklabels([table.loc[n, "label"] for n in order] if j == 0 else [], fontsize=7.5, color=INK)
        ax.axvline(0, color=INK2, linewidth=0.8)
        name = "Germany" if c == "DEU" else "EU"
        style(ax, f"{name}: value-added loss avoided, mUSD (base {base_g:,.0f})", "")
        ax.set_xlim(left=min(0, g.min() * 1.15), right=max(g.max(), net.max()) * 1.35)
        if j == 0:
            ax.legend(frameon=False, fontsize=7, labelcolor=INK2, loc="lower right")
    ax = fig.add_subplot(gs[1, :])
    ax.plot(weekly[base_name].index, weekly[base_name].values, color=INK, linewidth=2.2, label="base")
    shown = [n for n in table.sort_values("DEU_avoided_gross_mUSD", ascending=False).index if n in weekly][:6]
    for i, n in enumerate(shown):
        s = weekly[n]
        ax.plot(s.index, s.values, color=SERIES[(i + 1) % len(SERIES)], linewidth=1.6, label=table.loc[n, "label"])
    style(ax, "Weekly value-added loss of Germany, mUSD: base and levers", "mUSD / week")
    ax.set_xlabel(f"week of the run (1 = {first_week})", fontsize=8, color=INK2)
    ax.legend(frameon=False, fontsize=7, labelcolor=INK2, ncol=2, loc="upper right")
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F7_levers.{ext}", dpi=300, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def fig_sensitivity(base: pd.Series, grid: pd.DataFrame, labels: dict, out: Path):
    vals = grid["DEU_%quarter"].astype(float)
    order = vals.sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(8.5, 0.42 * len(order) + 1.6))
    fig.patch.set_facecolor(SURFACE)
    y = np.arange(len(order))
    b = float(base["DEU_%quarter"])
    ax.axvline(b, color=INK2, linewidth=1, linestyle="--")
    ax.text(b, -0.75, f"base {b:.2f} %", fontsize=7, color=INK2, ha="center", va="top")
    ax.hlines(y, b, vals[order], color=SERIES[0], linewidth=1.2, alpha=0.6)
    ax.scatter(vals[order], y, color=SERIES[0], s=34, zorder=3)
    for yi, n in zip(y, order):
        v = float(vals[n])
        ax.text(v, yi + 0.22, f"{v:.2f} % ({100 * (v - b) / b:+.0f} %)", fontsize=6.5, color=INK2, ha="center")
    ax.set_yticks(y)
    ax.set_yticklabels([labels.get(n, n) for n in order], fontsize=7.5, color=INK)
    style(ax, "Germany: value-added loss as % of a quarter, sensitivity runs vs the base", "")
    ax.set_xlabel("% of one quarter of German value added", fontsize=8, color=INK2)
    lo, hi = min(vals.min(), b), max(vals.max(), b)
    ax.set_xlim(lo - 0.12 * (hi - lo + 1e-9), hi + 0.12 * (hi - lo + 1e-9))
    ax.set_ylim(-1.2, len(order) - 0.2)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"F8_sensitivity.{ext}", dpi=300, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", default="C:/dsc_runs/rhine2026")
    ap.add_argument("--prefix", default="2026_fc0910_")
    ap.add_argument("--base", default="base")
    ap.add_argument("--levers", default="deep20,fleet40,fleet20,stock7,stock7t,rail04,package")
    ap.add_argument("--grid", default="liq60,floors_m10,floors_p10,inv050,inv150,lr0,lr1,nopool,seed1,seed2,fleet40")
    ap.add_argument("--rate", type=float, default=0.13)
    ap.add_argument("--first-week", default="22 June 2026")
    ap.add_argument("--out", default=str(HERE / "figures"))
    ap.add_argument("--csv", default=None)
    ap.add_argument("--summary-csv", default=None,
                    help="batch summary from compare_runs.py --csv (+ .txt with --weekly DEU) instead of run folders")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    levers = [x for x in args.levers.split(",") if x]
    grid = [x for x in args.grid.split(",") if x]
    names = [args.base] + [n for n in levers + grid if n != args.base]
    if args.summary_csv:
        table_all, weekly = summarise_from_batch(Path(args.summary_csv), args.prefix, list(dict.fromkeys(names)))
    else:
        table_all, weekly = summarise(runs_dir, args.prefix, list(dict.fromkeys(names)), args.rate)
    if args.base not in table_all.index:
        raise SystemExit(f"base run {args.prefix}{args.base} not found or incomplete")
    base = table_all.loc[args.base]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    have_levers = [n for n in levers if n in table_all.index]
    if have_levers:
        tab = lever_table(base, table_all.loc[have_levers], LEVER_LABELS)
        fig_levers(base, tab, weekly, args.base, out, args.first_week)
        print("== levers: avoided loss vs base (mUSD; % of the base loss) ==")
        print(tab[["label", "DEU_avoided_gross_mUSD", "DEU_avoided_gross_%", "DEU_avoided_net_mUSD",
                   "EU_avoided_gross_mUSD", "DEU_peak_%week", "DEU_peak_week"]].to_string())
        if args.csv:
            tab.to_csv(args.csv)
            print(f"table written to {args.csv}")
        print(f"F7 written to {out}")
    have_grid = [n for n in grid if n in table_all.index]
    if have_grid:
        fig_sensitivity(base, table_all.loc[have_grid], GRID_LABELS, out)
        g = table_all.loc[have_grid, ["DEU_%quarter", "DEU_cum_mUSD", "EU_cum_mUSD", "DEU_peak_%week"]]
        print("== sensitivity runs ==")
        print(g.to_string())
        print(f"F8 written to {out}")


if __name__ == "__main__":
    main()
