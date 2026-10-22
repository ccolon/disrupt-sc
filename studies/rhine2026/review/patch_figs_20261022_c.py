"""F9 (validation) and F5b (who loses) per the author's notes of 21 Oct: the model as the mean of the eleven networks with a
grey band and one legend entry, interquartile range in (a) as in (c), plain titles and axis titles, jittered points in (b),
readable event labels in (c); the who-loses panels swapped (countries first), everything in billion USD, a proper legend."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/plots")


def patch(path: Path, pairs):
    s = path.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    for old, new in pairs:
        n = s.count(old); assert n == 1, f"{path.name}: {n} x {old[:80]!r}"
        s = s.replace(old, new)
    path.write_text(s.replace("\n", nl), encoding="utf-8"); print(f"{path.name}: {len(pairs)} replacements")


patch(P / "validation_figure.py", [
    # (a): mean of the eleven, grey band + IQR, one legend entry
    ('    band = np.array([[s[mo] for mo in MONTHS] for s in seeds])\n'
     '    ax.fill_between(x, band.min(axis=0), band.max(axis=0), color=BLUE, alpha=0.13, linewidth=0, label="ten further networks (range)")\n'
     '    ax.fill_between(x, REC16, REC84, color=GREEN, alpha=0.2, linewidth=0, label="statistical benchmark, ±1 s.d. band")\n'
     '    ax.plot(x, REC, color=GREEN, linewidth=1.5, marker="s", markersize=4)\n'
     '    ax.plot(x, [ref[mo] for mo in MONTHS], color=INK, linewidth=2.2, marker="o", markersize=5, label="model, reference network")\n'
     '    ax.plot(x, PRICED_X1, color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=3.5, label="alternative river (surcharge, closures)")\n'
     '    ax.set_xticks(x); ax.set_xticklabels(list(MONTHS), fontsize=8)\n'
     '    ax.set_ylabel("German industrial production, shortfall (%)", color=MUTED, fontsize=8)\n'
     '    ax.set_ylim(0, 3.0)\n'
     '    ax.legend(frameon=False, fontsize=7.5, loc="upper left")\n'
     '    ax.set_title("a  Industrial production through the 2018 low water", loc="left", fontsize=9.5, color=INK)\n',
     '    from matplotlib.legend_handler import HandlerTuple\n'
     '    band = np.array([[s[mo] for mo in MONTHS] for s in seeds] + [[ref[mo] for mo in MONTHS]])   # the eleven networks\n'
     '    h_rng = ax.fill_between(x, band.min(axis=0), band.max(axis=0), color=GREY, alpha=0.35, linewidth=0)\n'
     '    h_iqr = ax.fill_between(x, np.quantile(band, 0.25, axis=0), np.quantile(band, 0.75, axis=0), color=GREY, alpha=0.6, linewidth=0)\n'
     '    h_bench = ax.fill_between(x, REC16, REC84, color=GREEN, alpha=0.2, linewidth=0)\n'
     '    hb, = ax.plot(x, REC, color=GREEN, linewidth=1.5, marker="s", markersize=4)\n'
     '    hm, = ax.plot(x, band.mean(axis=0), color=INK, linewidth=2.2, marker="o", markersize=5)\n'
     '    ha, = ax.plot(x, PRICED_X1, color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=3.5)\n'
     '    ax.set_xticks(x); ax.set_xticklabels(list(MONTHS), fontsize=8)\n'
     '    ax.set_ylabel("shortfall of industrial production (%)", color=MUTED, fontsize=8)\n'
     '    ax.set_ylim(0, 3.0)\n'
     '    ax.legend([(h_rng, h_iqr, hm), (h_bench, hb), ha], ["model (mean, interquartile range, range of 11 networks)", "statistical benchmark (±1 s.d. band)", "alternative river (surcharge, closures)"],\n'
     '              handler_map={tuple: HandlerTuple(ndivide=1)}, frameon=False, fontsize=7, loc="upper left")\n'
     '    ax.set_title("(a) German industrial production, 2018", loc="left", fontsize=9.5, color=INK)\n'),
    # (b): jittered points, plain axis title
    ('    ax.scatter([0.93] * len(ints), ints, color=BLUE, s=14, alpha=0.7, zorder=3, label="ten further networks, ×1")\n',
     '    ints = ints + [ref["integral"]]\n'
     '    ax.scatter(0.93 + np.random.default_rng(5).uniform(-0.035, 0.035, len(ints)), ints, color=BLUE, s=14, alpha=0.7, zorder=3, label="eleven networks, ×1")\n'),
    ('    ax.set_xlabel("inventory multiplier (×1 = balance-sheet statistics)", color=MUTED, fontsize=8)\n', '    ax.set_xlabel("inventory multiplier", color=MUTED, fontsize=8)\n'),
    ('    ax.set_title("b  Size of the loss: inventories, loading curve, suppliers", loc="left", fontsize=9.5, color=INK)\n',
     '    ax.set_title("(b) Cumulated shortfall: inventories, loading curve, suppliers", loc="left", fontsize=9.5, color=INK)\n'),
    # (c): mean of the eleven, grey, one legend entry, readable event labels
    ('    band = ens[cols] * 13 / Q_DEU\n'
     '    ax.fill_between(dates, band.min(axis=1), band.max(axis=1), color=BLUE, alpha=0.15, linewidth=0, label="ten further networks (range)")\n'
     '    ax.fill_between(dates, band.quantile(0.25, axis=1), band.quantile(0.75, axis=1), color=BLUE, alpha=0.3, linewidth=0, label="interquartile range")\n'
     '    ax.plot(dates, ens["2018_s07_base"] * 13 / Q_DEU, color=INK, linewidth=2, label="reference network")\n'
     '    top = float(max(band.max().max(), (ens["2018_s07_base"] * 13 / Q_DEU).max())) * 1.15\n'
     '    ax.set_ylim(0, top)\n'
     '    for d in ("2018-10-22", "2018-10-25"):\n'
     '        ax.axvline(pd.Timestamp(d), color=ORANGE, linewidth=1, linestyle="--")\n'
     '    ax.text(pd.Timestamp("2018-10-20"), top * 0.97, "force majeure, 22 Oct", color=ORANGE, fontsize=7, ha="right", va="top", rotation=90)\n'
     '    ax.text(pd.Timestamp("2018-10-13"), top * 0.97, "fuel-reserve release, 24–26 Oct", color=ORANGE, fontsize=7, ha="right", va="top", rotation=90)\n'
     '    ax.axvspan(pd.Timestamp("2018-11-01"), pd.Timestamp("2018-11-30"), color=ORANGE, alpha=0.08, linewidth=0)\n'
     '    ax.text(pd.Timestamp("2018-12-02"), top * 0.97, "deepest month of\\nproduction: November", color=ORANGE, fontsize=7.5, ha="left", va="top")\n'
     '    ax.set_ylabel("German loss, all sectors (% of a week)", color=MUTED, fontsize=8)\n'
     '    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))\n'
     '    ax.set_xlim(pd.Timestamp("2018-07-16"), pd.Timestamp("2019-01-07"))\n'
     '    ax.legend(frameon=False, fontsize=7.5, loc="upper left")\n'
     '    ax.set_title("c  Weekly loss in 2018 and the observed events", loc="left", fontsize=9.5, color=INK)\n',
     '    band = ens[cols + ["2018_s07_base"]] * 13 / Q_DEU                      # the eleven networks\n'
     '    c_rng = ax.fill_between(dates, band.min(axis=1), band.max(axis=1), color=GREY, alpha=0.35, linewidth=0)\n'
     '    c_iqr = ax.fill_between(dates, band.quantile(0.25, axis=1), band.quantile(0.75, axis=1), color=GREY, alpha=0.6, linewidth=0)\n'
     '    cm, = ax.plot(dates, band.mean(axis=1), color=INK, linewidth=2)\n'
     '    top = float(band.max().max()) * 1.25\n'
     '    ax.set_ylim(0, top)\n'
     '    ax.axvspan(pd.Timestamp("2018-10-22"), pd.Timestamp("2018-10-26"), color=ORANGE, alpha=0.25, linewidth=0)\n'
     '    ax.text(pd.Timestamp("2018-10-24"), top * 0.98, "22–26 Oct: force majeure,\\nfuel-reserve release", color=ORANGE, fontsize=7, ha="center", va="top")\n'
     '    ax.axvspan(pd.Timestamp("2018-11-01"), pd.Timestamp("2018-11-30"), color=ORANGE, alpha=0.08, linewidth=0)\n'
     '    ax.text(pd.Timestamp("2018-11-15"), top * 0.80, "November: deepest month\\nof industrial production", color=ORANGE, fontsize=7, ha="center", va="top")\n'
     '    ax.set_ylabel("weekly national value-added loss (% of a week)", color=MUTED, fontsize=8)\n'
     '    ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))\n'
     '    ax.set_xlim(pd.Timestamp("2018-07-16"), pd.Timestamp("2019-01-07"))\n'
     '    ax.legend([(c_rng, c_iqr, cm)], ["model (mean, interquartile range, range of 11 networks)"], handler_map={tuple: HandlerTuple(ndivide=1)}, frameon=False, fontsize=7, loc="upper left")\n'
     '    ax.set_title("(c) Weekly loss in 2018", loc="left", fontsize=9.5, color=INK)\n'),
    ('    ax.set_title("d  Network-to-network spread", loc="left", fontsize=9.5, color=INK)\n', '    ax.set_title("(d) Network-to-network spread", loc="left", fontsize=9.5, color=INK)\n'),
    ('INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"\n', 'INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"\nGREY = "#9aa0a6"\n'),
])

patch(P / "who_loses_panel.py", [
    ('    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), gridspec_kw={"width_ratios": [1.5, 1]})\n', '    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), gridspec_kw={"width_ratios": [1, 1]})\n'),
    ('    ax = axes[0]\n    ys = np.arange(len(top))[::-1]\n', '    ax = axes[1]\n    ys = np.arange(len(top))[::-1]\n'),
    ('    ax.barh(ys, top.values / 1e3, color=[ORANGE if s[:1] in DEFERRABLE else BLUE for s in top.index], height=0.6, label=None)\n'
     '    ax.scatter([net[s] / 1e3 for s in top.index], ys, color=INK, s=16, zorder=3, label="net of the backlog worked off")\n'
     '    for y, (s, v) in zip(ys, top.items()):\n'
     '        ax.text(v / 1e3 + 0.05, y, f"{100 * v / gross.sum():.0f} %", va="center", fontsize=7.5, color=INK)\n'
     '    ax.set_yticks(ys); ax.set_yticklabels([f"{NAMES.get(s, s)} ({group(s)})" for s in top.index], fontsize=7.5)\n'
     '    ax.set_xlabel("German loss, billion USD (bars: gross; orange: can catch up, blue: cannot)", color=MUTED, fontsize=7.5)\n'
     '    ax.legend(frameon=False, fontsize=7, loc="lower right")\n'
     '    ax.set_title("b  German loss by sector, whole event", loc="left", fontsize=9.5, color=INK)\n'
     '    ax = axes[1]\n',
     '    from matplotlib.patches import Patch\n'
     '    from matplotlib.lines import Line2D\n'
     '    ax.barh(ys, top.values / 1e3, color=[ORANGE if s[:1] in DEFERRABLE else BLUE for s in top.index], height=0.6)\n'
     '    ax.scatter([net[s] / 1e3 for s in top.index], ys, color=INK, s=16, zorder=3)\n'
     '    ax.set_yticks(ys); ax.set_yticklabels([NAMES.get(s, s) for s in top.index], fontsize=7.5)\n'
     '    ax.set_xlabel("German loss, billion USD", color=MUTED, fontsize=8)\n'
     '    ax.legend([Patch(color=ORANGE), Patch(color=BLUE), Line2D([], [], marker="o", color=INK, linestyle="none", markersize=4)],\n'
     '              ["gross, can catch up", "gross, cannot catch up", "net of the backlog worked off"], frameon=False, fontsize=7, loc="lower right")\n'
     '    ax.set_title("(c) German loss by sector", loc="left", fontsize=9.5, color=INK)\n'
     '    ax = axes[0]\n'),
    ('    ax.scatter(cty.values / 1e3, ys, color=GREEN, s=36, zorder=3)\n'
     '    for y, v in zip(ys, cty.values):\n'
     '        ax.text(v / 1e3 * 1.25, y, f"{v / 1e3:.2f}" if v < 100 else f"{v / 1e3:.1f}", va="center", fontsize=7.5, color=INK)\n'
     '    ax.set_yticks(ys); ax.set_yticklabels(list(cty.index), fontsize=8)\n'
     '    ax.set_xscale("log"); ax.set_xlim(0.02, cty.max() / 1e3 * 3)\n'
     '    ax.set_xlabel("billion USD (log scale)", color=MUTED, fontsize=7.5)\n'
     '    ax.set_title("c  By country", loc="left", fontsize=9.5, color=INK)\n',
     '    ax.scatter(cty.values / 1e3, ys, color=GREEN, s=36, zorder=3)\n'
     '    ax.set_yticks(ys); ax.set_yticklabels(list(cty.index), fontsize=8)\n'
     '    ax.set_xscale("log"); ax.set_xlim(0.02, cty.max() / 1e3 * 3)\n'
     '    ax.set_xlabel("value-added loss, billion USD (log scale)", color=MUTED, fontsize=8)\n'
     '    ax.set_title("(b) Loss by country", loc="left", fontsize=9.5, color=INK)\n'),
])
print("done")
