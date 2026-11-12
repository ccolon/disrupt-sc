"""The figure scripts for the author's round of 12 November 2026 (notes N02, N03, N04 and the caption of Fig. 1).
Applied once; the scripts are the record, this file says what was changed and why. Running it again fails on its
first anchor (already applied).

    python studies/rhine2026/review/patch_figures_20261112.py

validation_figure.py, panel (b): one legend entry for the model and the range of the networks, as in (a); the
    alternative river is no longer drawn; the range of the eleven networks is centred on x1; the loading-curve variants
    are two triangles at x1 instead of a segment; no '(statistics)' under the x1 tick; 'capacity reduction' for the
    quantity the variants scale (N01).
wave_figure.py: the figure slightly larger; 'season as it happened' without '(no gap)'; panel (b) without the curve
    at a 15-day refill time (its numbers stay in Table S-crosswaves).
decision_figure.py: no asterisk on 'bulk' (the author cut its explanation from the caption).
"""
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "plots"


def sub(path: Path, old: str, new: str, count: int = 1) -> None:
    s = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in s else "\n"
    s = s.replace("\r\n", "\n")
    assert s.count(old) == count, (path.name, s.count(old), old[:70])
    path.write_bytes(s.replace(old, new).replace("\n", nl).encode("utf-8"))


v = P / "validation_figure.py"
sub(v, '["model (mean, interquartile range, range of 11 networks)", "statistical benchmark (±1 s.d. band)", "alternative river (surcharge, closures)"]',
       '["model (mean, interquartile, min–max of 11 networks)", "statistical benchmark (±1 s.d. band)", "alternative river (surcharge, closures)"]')
sub(v, """    # the loading-curve bar in blue (green was the benchmark's colour); a rung at x0.75 (2018_<TAG>_inv075) when its
    # run is there (the author's question of 6 Nov: the ladder below the balance-sheet level, not a new baseline)
""", """    # the loading-curve bar in blue (green was the benchmark's colour); a rung at x0.75 (2018_<TAG>_inv075) when its
    # run is there (the author's question of 6 Nov: the ladder below the balance-sheet level, not a new baseline)
    # 12 Nov 2026 (the author's notes on the caption): one legend entry for the model and the networks' range, as in
    # (a); no alternative river in this panel; the range of the eleven networks centred on x1; the loading-curve
    # variants as two triangles at x1 instead of a segment; no '(statistics)' under the x1 tick. The line is the
    # reference network (the inventory levels were run on it alone), which the legend says
""")
sub(v, """    h_alt, = ax.plot(list(INT_PRICED), list(INT_PRICED.values()), color=ORANGE, linewidth=1.3, linestyle="--", marker="o", markersize=4)
""", "")
sub(v, """    xl, xr = 0.90, 0.96                                     # the eleven networks' integrals at x1, drawn beside the rung
""", """    xl, xr = 0.965, 1.035                                   # the eleven networks' integrals, centred on x1
""")
sub(v, """    h_curve, = ax.plot([1.0, 1.0], [high["integral"], low["integral"]], color=BLUE, linewidth=2.5, alpha=0.8, solid_capstyle="round", zorder=2)
""", """    h_up, = ax.plot([1.0], [low["integral"]], color=BLUE, marker="^", markersize=5.5, linestyle="none", zorder=5)     # capacity reduction x1.15
    h_dn, = ax.plot([1.0], [high["integral"]], color=BLUE, marker="v", markersize=5.5, linestyle="none", zorder=5)    # capacity reduction x0.85
""")
sub(v, """ax.set_xticklabels([("×1\\n(statistics)" if t == 1.0 else f"×{t:g}") for t in ticks], fontsize=8)""",
       """ax.set_xticklabels([f"×{t:g}" for t in ticks], fontsize=8)""")
sub(v, """    ax.set_ylim(0, 12.5)                                  # room above the band (3.6-7.1) for the six-line legend
    ax.legend([h_model, h_alt, (h_bband, h_bline), (h_nrng, h_niqr), h_curve, h_sup],
              ["model (reference network)", "alternative river (surcharge, closures)", "statistical benchmark (±1 s.d. band)",
               "eleven networks at ×1 (interquartile range, range)", "loading curve, shortfall ×1.15 and ×0.85", "two suppliers per input"],
              handler_map={tuple: HandlerTuple(ndivide=1)}, frameon=True, framealpha=0.9, edgecolor="none", fontsize=7, loc="upper left")
""", """    ax.set_ylim(0, 12.0)                                  # room above the band (3.6-7.1) for the legend
    from matplotlib.legend_handler import HandlerBase
    from matplotlib.lines import Line2D

    class _Pair:                                           # the two triangles as one legend entry
        def __init__(self, *handles):
            self.handles = handles

    class _TwoMarkers(HandlerBase):
        def create_artists(self, legend, orig, x0, y0, width, height, fontsize, trans):
            return [Line2D([x0 + width * (0.32 + 0.36 * k)], [y0 + height / 2], marker=h.get_marker(), color=h.get_color(),
                           markersize=h.get_markersize(), linestyle="none", transform=trans) for k, h in enumerate(orig.handles)]

    ax.legend([(h_nrng, h_niqr, h_model), (h_bband, h_bline), _Pair(h_up, h_dn), h_sup],
              ["model (reference network; at ×1: interquartile\\nand min–max of the 11 networks)", "statistical benchmark (±1 s.d. band)",
               "loading curve, capacity reduction ×1.15 and ×0.85", "two suppliers per input"],
              handler_map={tuple: HandlerTuple(ndivide=1), _Pair: _TwoMarkers()}, frameon=True, framealpha=0.9, edgecolor="none", fontsize=7, loc="upper left")
""")
# the alternative river at x1.5 and x2 is no longer drawn: the x1 run alone is read (for panel a)
sub(v, """    INT_PRICED = {1.0: priced1["integral"], 1.5: matched(runs / PRICED[1.5])["integral"], 2.0: matched(runs / PRICED[2.0])["integral"]}
""", "")

w = P / "wave_figure.py"
sub(w, """    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.1), gridspec_kw={"width_ratios": [1.45, 1]})""",
       """    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.6), gridspec_kw={"width_ratios": [1.3, 1]})   # 12 Nov 2026 (the author's note): slightly larger""")
sub(w, '''"season as it happened (no gap)"''', '''"season as it happened"''')
sub(w, """    ax.plot(gaps, L, color=INK, linewidth=1.8, marker="o", markersize=5, label="in sequence, 30-day refill time")
    cx = AD / f"compare_runs_batch_jobs_{CROSS}_cross.csv"; rv = AD / f"compare_runs_batch_jobs_{LISTS}_rev.csv"
    L15 = []
    if cx.exists() and rv.exists():                            # the batch of 9 Oct: the same experiment at a 15-day refill time
        c, r = table(cx), table(rv)
        s15 = c.loc[f"{WV9}_A_rest15", "DEU_%quarter"] + c.loc[f"{WV9}_B_rest15", "DEU_%quarter"]
        L15 = [r.loc[f"2026_{REV}_rest15", "DEU_%quarter"], c.loc[f"{WV9}_AB_gap2_rest15", "DEU_%quarter"], c.loc[f"{WV9}_AB_gap4_rest15", "DEU_%quarter"]]
        TEAL = "#1f9e9e"
        ax.plot([0, 2, 4], L15, color=TEAL, linewidth=1.6, marker="o", markersize=4.5, label="in sequence, 15-day refill time")
""", """    ax.plot(gaps, L, color=INK, linewidth=1.8, marker="o", markersize=5, label="the two episodes in sequence")
    # 12 Nov 2026 (the author's decision): the same experiment at a 15-day refill time is no longer drawn here; its
    # numbers stay in Table S-crosswaves of the SI (si_tables.py, cross_table), with what bounds the refill
    L15 = []
""")
sub(w, """    ax.set_title("(b) The interaction, by gap and refill time", loc="left", fontsize=9.5, color=INK)""",
       """    ax.set_title("(b) The interaction, by gap", loc="left", fontsize=9.5, color=INK)""")
sub(w, """reference, and the flat profile (the same cumulated capacity shortfall, spread evenly).""",
       """reference, and the flat profile (the same cumulated capacity reduction, spread evenly).""")

d = P / "decision_figure.py"
sub(d, """containers may switch, most bulk waits (the asterisk is explained in the caption)).""",
       """containers may switch, most bulk waits; 12 Nov 2026: no asterisk on 'bulk', the author having cut its note from
the caption).""")
sub(d, '''to rail or road, most\\nbulk* cannot and waits"''', '''to rail or road, most\\nbulk cannot and waits"''')
print("figure scripts patched")
