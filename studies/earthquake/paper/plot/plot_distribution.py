"""2-panel distribution figure for one run:
  (left)  household loss by sector over months, as % of annual GDP (stacked area)
  (right) province choropleth of household loss (% of annual GDP), mainland focus
          with a Galapagos inset (shared colour scale)

CLI:
    python plot_distribution.py <analyzer_out_dir> --gadm <gadm41_ECU_1.json> [--fig PATH]
where <analyzer_out_dir> holds loss_by_sector_time.csv + loss_by_province_year.csv.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import pandas as pd
import geopandas as gpd

GAL_LON_THRESHOLD = -85.0            # provinces west of this are Galapagos
CMAP = "YlOrRd"


def norm_name(s: object) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def main():
    ap = argparse.ArgumentParser(description="2-panel household-loss distribution figure")
    ap.add_argument("out_dir", type=Path, help="dir with loss_by_sector_time.csv + loss_by_province_year.csv")
    ap.add_argument("--gadm", type=Path, required=True, help="gadm41_ECU_1.json (province polygons)")
    ap.add_argument("--fig", type=Path, default=None)
    args = ap.parse_args()

    st = pd.read_csv(args.out_dir / "loss_by_sector_time.csv")
    pv = pd.read_csv(args.out_dir / "loss_by_province_year.csv")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.25, 1]})

    # ---- LEFT: household loss by sector over months (% of annual GDP) ----
    wide = st.pivot_table(index="time_step", columns="sector_label", values="pct_gdp", aggfunc="sum").fillna(0.0)
    wide = wide[wide.sum().sort_values(ascending=False).index]
    axL.stackplot(wide.index, wide.T.values, labels=wide.columns, alpha=0.9)
    axL.set_xlabel("month since shock")
    axL.set_ylabel("household loss (% of annual GDP), per month")
    axL.set_title("Temporal / sectoral household loss")
    axL.margins(x=0)
    axL.legend(loc="upper right", fontsize=8, ncol=2, frameon=False)

    # ---- RIGHT: province choropleth, mainland + Galapagos inset ----
    g = gpd.read_file(args.gadm)
    pcol = "province" if "province" in g.columns else "NAME_1"
    g["key"] = g[pcol].map(norm_name)
    pv["key"] = pv["province"].map(norm_name)
    g = g.merge(pv[["key", "pct_gdp"]], on="key", how="left")

    b = g.geometry.bounds                              # bbox midpoint (avoids geographic-CRS centroid warning)
    cx = (b.minx + b.maxx) / 2.0
    mainland = g[cx > GAL_LON_THRESHOLD]
    galapagos = g[cx <= GAL_LON_THRESHOLD]
    norm = Normalize(vmin=0.0, vmax=float(g["pct_gdp"].max()))

    common = dict(cmap=CMAP, norm=norm, edgecolor="0.6", linewidth=0.3,
                  missing_kwds={"color": "whitesmoke"})
    mainland.plot(column="pct_gdp", ax=axR, **common)
    minx, miny, maxx, maxy = mainland.total_bounds
    w, h = maxx - minx, maxy - miny
    axR.set_xlim(minx - 0.62 * w, maxx + 0.03 * w)     # wide ocean margin on the LEFT for the inset
    axR.set_ylim(miny - 0.03 * h, maxy + 0.03 * h)
    axR.set_title("Spatial household loss (province, cumulative)")
    axR.set_axis_off()

    if len(galapagos):
        axins = axR.inset_axes([0.01, 0.58, 0.38, 0.40])   # top-left, over the added ocean margin
        galapagos.plot(column="pct_gdp", ax=axins, **common)
        axins.set_title("Galapagos", fontsize=8)
        axins.set_xticks([]); axins.set_yticks([])
        for s in axins.spines.values():
            s.set_edgecolor("0.6"); s.set_linewidth(0.6)

    sm = cm.ScalarMappable(norm=norm, cmap=CMAP); sm.set_array([])
    fig.colorbar(sm, ax=axR, shrink=0.55, label="household loss (% of annual GDP)")

    fig.suptitle("DisruptSC — 2016 Ecuador earthquake: household loss distribution", fontsize=13)
    fig.tight_layout()
    figpath = args.fig or (args.out_dir / "fig_distribution.png")
    fig.savefig(figpath, dpi=140, bbox_inches="tight")
    print(f"-> {figpath}")

    unmatched = pv.loc[~pv.key.isin(set(g.key)), "province"].tolist()
    if unmatched:
        print(f"WARNING unmatched model provinces (no polygon): {unmatched}")


if __name__ == "__main__":
    main()
