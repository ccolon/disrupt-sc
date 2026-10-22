"""F7 layout: short lever labels, one-column legend, monthly ticks, titles that fit."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/plots/paired_lever_figure.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
pairs = [
    ('LEVERS = [("package", "all three together"), ("stock7", "inventories +7 days, all buyers"),\n'
     '          ("deep20", "fairway +20 cm"), ("stock7t", "inventories +7 days, barge-dependent buyers"),\n'
     '          ("fleet", "low-water fleet")]\n',
     'LEVERS = [("package", "all three together"), ("stock7", "inventories +7 days, all buyers"),\n'
     '          ("deep20", "fairway +20 cm"), ("stock7t", "inventories +7 days, targeted"),\n'
     '          ("fleet", "low-water fleet")]\n'),
    ('    fig = plt.figure(figsize=(7.0, 3.0))\n    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.15])\n',
     '    fig = plt.figure(figsize=(7.0, 3.2))\n    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25])\n'),
    ('    ax.set_title("a  Loss avoided, mean of eleven networks", loc="left", fontsize=9, color=INK)\n',
     '    ax.set_title("a  Loss avoided (mean of 11 networks)", loc="left", fontsize=9, color=INK)\n'),
    ('    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))\n    ax.set_ylabel("German loss (% of a week)", color=MUTED, fontsize=8)\n    ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=2)\n',
     '    ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))\n    ax.set_ylabel("German loss (% of a week)", color=MUTED, fontsize=8)\n    ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=1)\n'),
    ('    ax.set_title("b  Weekly German loss, reference network", loc="left", fontsize=9, color=INK)\n',
     '    ax.set_title("b  Weekly loss, reference network", loc="left", fontsize=9, color=INK)\n'),
]
for old, new in pairs:
    n = s.count(old); assert n == 1, f"{n} x {old[:80]!r}"
    s = s.replace(old, new)
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("paired_lever_figure.py relaid")
