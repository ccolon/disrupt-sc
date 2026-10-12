"""Legible text at print size (13 Oct 2026).

The figure scripts lay their panels out on 8-13 inch canvases that the manuscript prints at the text width (about
7 inches), which shrinks the 7-8 pt labels they set to 4-5 pt. ``finish(fig)`` multiplies every text size by
canvas width / print width, so that the point sizes written in the scripts are the sizes on the page, raises any
text below ``min_pt`` to that floor, and thickens lines and markers by the square root of the same factor so they
keep their weight. Call it after the panels are built and before tight_layout / savefig.
"""
from __future__ import annotations

import matplotlib
import matplotlib.collections
import matplotlib.lines
import matplotlib.text


def finish(fig, print_width: float = 7.0, min_pt: float = 7.0, legend_handles: bool = True) -> float:
    k = fig.get_figwidth() / print_width
    if abs(k - 1.0) < 1e-6:
        return k
    for t in fig.findobj(matplotlib.text.Text):
        s = t.get_fontsize()
        if s:
            t.set_fontsize(max(float(s), min_pt) * k)
    for ln in fig.findobj(matplotlib.lines.Line2D):
        ln.set_linewidth(ln.get_linewidth() * k ** 0.5)
        ln.set_markersize(ln.get_markersize() * k ** 0.5)
    for c in fig.findobj(matplotlib.collections.PathCollection):          # scatter: sizes are areas (pt^2)
        try:
            c.set_sizes(c.get_sizes() * k)
        except Exception:
            pass
    for ax in fig.get_axes():
        for sp in ax.spines.values():
            sp.set_linewidth(sp.get_linewidth() * k ** 0.5)
        ax.tick_params(width=max(0.6, 0.8 * k ** 0.5), length=3.5 * k ** 0.5)
        leg = ax.get_legend()
        if leg is not None and legend_handles:
            for h in leg.legend_handles:
                if hasattr(h, "set_linewidth"):
                    try:
                        h.set_linewidth(h.get_linewidth() * k ** 0.5)
                    except Exception:
                        pass
    return k
