"""F8 (now Supplementary): flipped to a horizontal dot plot, no value labels, (a)/(b) labels (decision D5 of 22 Oct)."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/plots/sensitivity_figure.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
start = s.index("        ax.axhline(base, color=INK, linewidth=1.2, linestyle=\"--\")")
end = s.index("        ax.set_title(")
end = s.index("\n", end) + 1
new = '''        ax.axvline(base, color=INK, linewidth=1.2, linestyle="--")
        ax.text(base + 0.02, len(groups) - 0.45, f"reference {base:.2f}", color=INK, fontsize=7.5, ha="left", va="top")
        top = max(max(v) for lab, v, _ in groups if not lab.startswith("no input")) * 1.22
        for y, (lab, vals, col) in enumerate(groups):
            if lab.startswith("no input") and max(vals) > top:
                ax.scatter([top * 0.97], [y], color=col, marker=">", s=40, zorder=3)
                ax.annotate(f"{max(vals):.2f}, off scale", (top * 0.97, y), textcoords="offset points", xytext=(-4, 7), fontsize=7, color=INK, ha="right")
                continue
            network = lab.startswith("network")
            jitter = rng.uniform(-0.12, 0.12, len(vals)) if network else np.zeros(len(vals))
            ax.scatter(vals, y + jitter, color=col, s=26, alpha=0.8, zorder=3)
            if network:
                ax.text(float(np.mean(vals)), y + 0.3, f"{np.mean(vals):.2f} ± {np.std(vals, ddof=1):.2f}", fontsize=7, color=INK, ha="center", va="bottom")
        ax.set_yticks(range(len(groups))); ax.set_yticklabels([g[0].replace("\\n", " ") for g in groups], fontsize=7.5)
        ax.set_ylim(-0.6, len(groups) - 0.3)
        ax.set_xlim(0, top)
        ax.invert_yaxis()
        ax.set_xlabel("German loss (% of a quarter)", color=MUTED, fontsize=8)
        ax.set_title(("(a) " if year == "2026" else "(b) ") + (f"{year}: sources of uncertainty" if year == "2026" else f"{year}"), loc="left", fontsize=9, color=INK)
'''
s = s[:start] + new + s[end:]
s = s.replace('fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), gridspec_kw={"width_ratios": [1.6, 1.0]})',
              'fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.6), gridspec_kw={"width_ratios": [1.0, 1.0]})')
s = s.replace('    ax.grid(axis="y", color=GRID, linewidth=0.6)\n', '    ax.grid(axis="x", color=GRID, linewidth=0.6)\n')
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("sensitivity_figure.py flipped")
