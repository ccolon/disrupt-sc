"""Wave figure (F10) and lever figure (F7) per the author's notes of 21 Oct: no vertical line, the sum curve visible, plain
labels and no value labels in the wave figure, the 15-day sum line dropped; the lever figure as one row (Germany bars = the
mean over the eleven networks, no value labels, plus the weekly panel)."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/plots")


def patch(path: Path, pairs):
    s = path.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    for old, new in pairs:
        n = s.count(old); assert n == 1, f"{path.name}: {n} x {old[:80]!r}"
        s = s.replace(old, new)
    path.write_text(s.replace("\n", nl), encoding="utf-8"); print(f"{path.name}: {len(pairs)} replacements")


patch(P / "wave_figure.py", [
    ('    ax.plot(dates, season / wk, color=INK, linewidth=2.2, label="2026 season (A then B)")\n'
     '    ax.plot(dates, total, color=MUTED, linewidth=1.3, linestyle="--", label="A alone + B alone")\n'
     '    ax.plot(dates, a / wk, color=BLUE, linewidth=1.5, label="first episode alone (A, to 30 Aug)")\n'
     '    ax.plot(dates, b_shift / wk, color=GREEN, linewidth=1.5, label="second episode alone (B, from 31 Aug)")\n'
     '    ax.axvline(FIRST + pd.Timedelta(weeks=SPLIT), color=MUTED, linewidth=0.8, linestyle=":")\n',
     '    ax.plot(dates, season / wk, color=INK, linewidth=2.2, label="2026 season", zorder=3)\n'
     '    ax.plot(dates, total, color=ORANGE, linewidth=1.6, linestyle=(0, (3, 2)), label="first episode alone + second episode alone", zorder=4)\n'
     '    ax.plot(dates, a / wk, color=BLUE, linewidth=1.5, label="first episode alone")\n'
     '    ax.plot(dates, b_shift / wk, color=GREEN, linewidth=1.5, label="second episode alone")\n'),
    ('    ax.text(0.1, s + 0.012, f"A + B alone: {s:.2f}", color=MUTED, fontsize=7.5, ha="left", va="bottom")\n'
     '    ax.plot(gaps, L, color=INK, linewidth=1.8, marker="o", markersize=5)\n'
     '    for g, v in zip(gaps, L):\n'
     '        ax.annotate(f"{v:.2f}", (g, v), textcoords="offset points", xytext=(6, 5), fontsize=7.5, color=INK)\n',
     '    ax.text(0.1, s + 0.012, "the two episodes alone, summed", color=MUTED, fontsize=7.5, ha="left", va="bottom")\n'
     '    ax.plot(gaps, L, color=INK, linewidth=1.8, marker="o", markersize=5, label="in sequence, 30-day refill time")\n'),
    ('        ax.axhline(s15, color=TEAL, linewidth=1.1, linestyle="--", alpha=0.8)\n'
     '        ax.text(8.0, s15 + 0.012, f"A + B alone, 15-day refill: {s15:.2f}", color=TEAL, fontsize=7.5, ha="right", va="bottom")\n'
     '        ax.plot([0, 2, 4], L15, color=TEAL, linewidth=1.6, marker="o", markersize=4.5)\n'
     '        for g, v in zip([0, 2, 4], L15):\n'
     '            ax.annotate(f"{v:.2f}", (g, v), textcoords="offset points", xytext=(6, -14), fontsize=7, color=TEAL)\n'
     '        ax.text(4.35, L15[-1] + 0.02, "15-day refill time", color=TEAL, fontsize=7.5, ha="left", va="bottom")\n',
     '        ax.plot([0, 2, 4], L15, color=TEAL, linewidth=1.6, marker="o", markersize=4.5, label="in sequence, 15-day refill time")\n'),
    ('    ax.text(8.0, f + 0.012, f"flat profile, same capacity shortfall: {f:.2f}", color=GREEN, fontsize=7.5, ha="right", va="bottom")\n',
     '    ax.text(8.0, f + 0.012, "flat profile", color=GREEN, fontsize=7.5, ha="right", va="bottom")\n'
     '    ax.legend(frameon=False, fontsize=7, loc="center right")\n'),
])

patch(P / "paired_lever_figure.py", [
    ('    fig = plt.figure(figsize=(7.0, 5.0))\n'
     '    gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.95], width_ratios=[1, 1])\n'
     '    fig.patch.set_facecolor("white")\n'
     '    rng = np.random.default_rng(1)\n'
     '    for col, (region, key) in enumerate((("Germany", "DEU_cum_mUSD"), ("28 economies", "EU_cum_mUSD"))):\n'
     '        ax = fig.add_subplot(gs[0, col]); style(ax); ax.grid(axis="x", color=GRID, linewidth=0.6)\n'
     '        base = m.loc["2026_s07_base", key]\n'
     '        ys = np.arange(len(LEVERS))[::-1]\n'
     '        for y, (lv, lab) in zip(ys, LEVERS):\n'
     '            ref = 100 * (1 - m.loc[f"2026_s07_{lv}", key] / base)\n'
     '            ax.barh(y, ref, color=COLORS[lv], alpha=0.85, height=0.55)\n'
     '            paired = [100 * (1 - p.loc[f"2026_s07_seed{s}_{lv}", key] / p.loc[f"2026_s07_seed{s}_base", key]) for s in range(1, 11)]\n'
     '            ax.scatter(paired, y + rng.uniform(-0.16, 0.16, 10), color=INK, s=13, zorder=3, alpha=0.75)\n'
     '            ax.text(max(ref, max(paired)) + 1.5, y, f"{ref:.0f} % ({min(paired):.0f}–{max(paired):.0f})", va="center", fontsize=7.5, color=INK)\n'
     '        ax.set_yticks(ys); ax.set_yticklabels([lab for _, lab in LEVERS] if col == 0 else [""] * len(LEVERS), fontsize=8)\n'
     '        ax.set_xlim(0, 105); ax.set_xlabel("loss avoided (% of the base)", color=MUTED, fontsize=8)\n'
     '        ax.set_title("a  Germany" if col == 0 else "b  28 economies (EU-27 and Switzerland)", loc="left", fontsize=9, color=INK)\n'
     '    ax = fig.add_subplot(gs[1, :]); style(ax); ax.grid(axis="y", color=GRID, linewidth=0.6)\n',
     '    fig = plt.figure(figsize=(7.0, 3.0))\n'
     '    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.15])\n'
     '    fig.patch.set_facecolor("white")\n'
     '    rng = np.random.default_rng(1)\n'
     '    key = "DEU_cum_mUSD"\n'
     '    ax = fig.add_subplot(gs[0, 0]); style(ax); ax.grid(axis="x", color=GRID, linewidth=0.6)\n'
     '    base = m.loc["2026_s07_base", key]\n'
     '    ys = np.arange(len(LEVERS))[::-1]\n'
     '    for y, (lv, lab) in zip(ys, LEVERS):\n'
     '        ref = 100 * (1 - m.loc[f"2026_s07_{lv}", key] / base)\n'
     '        paired = [100 * (1 - p.loc[f"2026_s07_seed{s}_{lv}", key] / p.loc[f"2026_s07_seed{s}_base", key]) for s in range(1, 11)]\n'
     '        avg = float(np.mean(paired + [ref]))   # the mean over the eleven networks (22 Oct 2026, decision D2)\n'
     '        ax.barh(y, avg, color=COLORS[lv], alpha=0.85, height=0.55)\n'
     '        ax.scatter(paired + [ref], y + rng.uniform(-0.16, 0.16, 11), color=INK, s=13, zorder=3, alpha=0.75)\n'
     '    ax.set_yticks(ys); ax.set_yticklabels([lab for _, lab in LEVERS], fontsize=7.5)\n'
     '    ax.set_xlim(0, 100); ax.set_xlabel("German loss avoided (% of the base)", color=MUTED, fontsize=8)\n'
     '    ax.set_title("a  Loss avoided, mean of eleven networks", loc="left", fontsize=9, color=INK)\n'
     '    ax = fig.add_subplot(gs[0, 1]); style(ax); ax.grid(axis="y", color=GRID, linewidth=0.6)\n'),
    ('    ax.set_title("c  Weekly German loss under each lever (reference network)", loc="left", fontsize=8.8, color=INK)\n'
     '    finish(fig)\n'
     '    fig.tight_layout(h_pad=1.5)\n',
     '    ax.set_title("b  Weekly German loss, reference network", loc="left", fontsize=9, color=INK)\n'
     '    finish(fig)\n'
     '    fig.tight_layout(w_pad=1.5)\n'),
])
print("done")
