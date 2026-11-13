r"""si_tables.py for the plain-sentence version of Tables S1, S2, S3 and S7 of the SI (13 November 2026, the author's
request; texts in si_tables_evidence.py). Applied once.

    python studies/rhine2026/review/patch_tools_20261113_evidence_tables.py

- rates_table (S1): the evidence cells are the sentences of si_tables_evidence.RATES_TEXT; the value cells still come
  from the parameters of the reference run. The ten countries with a higher rail cost and the eight waterways that carry
  the Rhine's values are named in the notes, and what the sentences say in words (ten, eight, four times, 20 %) is
  checked against the parameters.
- stocks_table (S2, S3): the rows of S2 are si_tables_evidence.STOCK_ROWS (32 rows: five groups of industries with the
  same value, grade and evidence are one row each); each row is checked against the configuration (one value per row)
  and against evidence/inventory_durations_by_industry.md (the grade). S3 keeps its fourteen rows.
- loading_table (S7): two text columns, "evidence" and "how the value is set", from si_tables_evidence.LOADING_TEXT;
  the loading share quoted in a sentence is checked against the curve.
"""
import re
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "si_tables.py"
raw = P.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
s = raw.replace("\r\n", "\n")
assert "si_tables_evidence" not in s, "already applied"


def between(text: str, start: str, end: str, new: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + new + text[b:]


# ---------------------------------------------------------------- the import
old = "from build_criticality_eu import ICIO_TO_WIOD  # noqa: E402\n"
assert s.count(old) == 1
s = s.replace(old, old + "from si_tables_evidence import (COUNTRY, LOADING_CAPTION, LOADING_TEXT, OVERRIDES, OVERRIDES_CAPTION, OVERRIDES_SERVICES,  # noqa: E402\n"
              "                                RATES_CAPTION, RATES_NOTES, RATES_TEXT, SAME_WATERWAYS, STOCK_ROWS, STOCKS_CAPTION, STOCKS_NOTES, word)\n")

# ---------------------------------------------------------------- S1: the value cells and the table
RATES = r'''def rail_cell(bc, cargo: str) -> str:
    """The rail cost of a cargo class and, where some countries carry a higher one, that cost with their number; the
    countries are named in the notes of the table (13 Nov 2026: the cell listed their codes)."""
    base, var = regional(bc["railways"], cargo)
    dear = {k: v for k, v in var.items() if abs(v - base) > 1e-12}
    if not dear:
        return f"{base:.3f}"
    vals = sorted(set(dear.values()))
    return f"{base:.3f}; {' / '.join(f'{v:.3f}' for v in vals)} in {word(len(dear))} countries$^{{a}}$"


def rail_dear(bc, cargo: str) -> dict:
    """{country: cost} of the countries whose rail cost differs from the base value."""
    base, var = regional(bc["railways"], cargo)
    return {k: v for k, v in var.items() if abs(v - base) > 1e-12}


def water_cell(bc, cargo: str) -> str:
    node = bc["waterways"]
    if not (isinstance(node, dict) and "attribute" in node):
        return f"{regional(node, cargo)[0]:.3f}"
    base, var = regional(node, cargo, base_key="Rhine")
    return f"{base:.3f} on the Rhine; up to {max(var.values()):.3f} on other waterways"


def rates_table(out: Path):
    """13 Nov 2026 (the author's request): the evidence cells are the plain sentences of si_tables_evidence.py (two or
    three figures each); the value cells come from the parameters of the reference run, as before. The table is
    written for the per-class batch (rail costs by country, waterway costs by waterway, seaport fees by port)."""
    lg, from_run = batch_logistics()
    assert from_run, "the table of transport costs is written for the per-class batch (its reference run on disk)"
    bc, vot, dw, lf, sp = lg["basic_cost"], lg["cost_of_time"], lg["dwell_times"], lg["loading_fees"], lg["speeds"]
    T = RATES_TEXT

    def transfer(pair: str) -> str:
        d, f = dw[pair], lf[pair]
        if isinstance(d, dict):
            return "; ".join(f"{lab} {num(d[k])} h / {num(f[k])}" for k, lab in
                             (("container", "containers"), ("dry_bulk", "dry bulk"), ("liquid_bulk", "liquid bulk")))
        return f"{num(d)} h / {num(f)}"

    # what the sentences and the notes say in words, checked against the parameters of the run
    dear = rail_dear(bc, "default")
    assert sorted(dear) == sorted(rail_dear(bc, "liquid_bulk")), "the same countries carry the higher rail cost for every cargo class"
    rail_base = regional(bc["railways"], "default")[0]
    assert all(abs(v / rail_base - 1.2) < 0.03 for v in dear.values()), "the rail cost is 20 % higher in the countries named"
    countries = sorted(COUNTRY[c] for c in dear)
    w_base, w_var = regional(bc["waterways"], "dry_bulk", base_key="Rhine")
    same = sorted(k for k, v in w_var.items() if abs(v - w_base) < 1e-12 and not k.startswith("("))
    assert len(same) == SAME_WATERWAYS.count(",") + 2, f"the notes name {SAME_WATERWAYS.count(',') + 2} waterways with the Rhine's values, the parameters have {len(same)}: {same}"
    times = max(w_var.values()) / w_base
    assert abs(times - round(times)) < 0.05, times
    rail_text = T["rail"].replace("<<n_countries>>", word(len(dear)))
    water_dry_text = T["water_dry"].replace("<<n_waterways>>", word(len(same))).replace("<<times>>", word(round(times)))
    notes = RATES_NOTES.replace("<<countries>>", ", ".join(countries[:-1]) + " and " + countries[-1]).replace("<<waterways>>", SAME_WATERWAYS)

    port_rows = []
    if isinstance(lf.get("by_port"), dict):
        fees = lf["by_port"]
        cont = [float(v["container"] if isinstance(v, dict) else v) for v in fees.values()]
        other = [float(v["default"] if isinstance(v, dict) else v) for v in fees.values()]
        port_rows.append(f"seaport fee, by port & containers {min(cont):g}--{max(cont):g}, other cargo {min(other):g}--{max(other):g} "
                         f"USD per tonne at {len(fees)} ports & {T['port_fee']} \\\\")

    rows = [
        r"\multicolumn{3}{l}{\emph{Line haul, USD per tonne-kilometer}} \\",
        f"road, containers and dry bulk & {bc['roads']['default']:.3f} & {T['road']} \\\\",
        f"road, liquid bulk & {bc['roads']['liquid_bulk']:.3f} & {T['road_liquid']} \\\\",
        f"rail, containers and dry bulk & {rail_cell(bc, 'default')} & {rail_text} \\\\",
        f"rail, liquid bulk & {rail_cell(bc, 'liquid_bulk')} & {T['rail_liquid']} \\\\",
        f"inland waterway, dry bulk & {water_cell(bc, 'dry_bulk')} & {water_dry_text} \\\\",
        f"inland waterway, liquid bulk & {water_cell(bc, 'liquid_bulk')} & {T['water_liquid']} \\\\",
        f"inland waterway, containers & {water_cell(bc, 'container')} & {T['water_container']} \\\\",
        f"sea & {bc['maritime']:.4f} & {T['sea']} \\\\",
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Value of time, USD per tonne-hour}} \\",
        f"containers & {vot['container']['default']:.2f} (road and rail); {vot['container']['waterways']:.2f} (waterways); {vot['container']['maritime']:.2f} (sea) & {T['vot_container']} \\\\",
        f"dry and liquid bulk & {vot['dry_bulk']:.2f} (all modes) & {T['vot_bulk']} \\\\",
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Terminal transfer, hours of dwell time / USD per tonne}} \\",
        f"road--rail & {transfer('roads-railways')} & {T['transfer_road_rail']} \\\\",
        f"road-- or rail--waterway & {transfer('roads-waterways')} & {T['transfer_land_water']} \\\\",
        f"waterway--sea & {transfer('waterways-maritime')} & {T['transfer_water_sea']} \\\\",
        f"road-- or rail--sea & {transfer('roads-maritime')} & {T['transfer_land_sea']} \\\\",
    ] + port_rows + [
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Speed, kilometers per hour}} \\",
        f"road / rail / inland waterway / sea & {num(sp['roads'])} / {num(sp['railways'])} / {num(sp['waterways'])} / {num(sp['maritime'])} & {T['speed']} \\\\",
    ]
    (out / "si_rates.tex").write_text(r"""\begingroup\footnotesize\setlength{\tabcolsep}{4pt}
\begin{longtable}{L{27mm}L{30mm}L{91mm}}
\caption{""" + RATES_CAPTION + r"""}
\label{tab:rates} \\
\toprule
mode, cargo class & value & evidence \\
\midrule
\endfirsthead
\toprule
mode, cargo class & value & evidence \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\multicolumn{3}{L{150mm}}{""" + notes + r"""} \\
\end{longtable}
\endgroup
""", encoding="utf-8")


'''
s = between(s, "def rail_cell(bc, cargo: str) -> str:", "# ------------------------------------------------------------------------------------------------ S1: stocks", RATES)

# ---------------------------------------------------------------- S2 and S3: the rows and the two tables
STOCKS = r'''def stocks_table(out: Path):
    """13 Nov 2026 (the author's request): the rows and their evidence are those of si_tables_evidence.py, in plain
    sentences; five groups of industries that share a value, a grade and their evidence are one row each. Each row
    is checked against the configuration (one value for its industries) and against the evidence file (the grade)."""
    inv = config()["inventory_duration_targets"]
    values, overrides = inv["values"], inv["overrides"]
    record = {}                                           # industry code -> (grade, recommended days) of the evidence file
    for label, rec, lean, grade, basis in _evidence_rows("### 6.2 Recommended table", "### 6.3 Input-type overrides"):
        for c in _codes(label)[0]:
            record[c] = (grade, int(re.match(r"\d+", rec).group()))
    covered = sorted(c for _, _, codes, _, _ in STOCK_ROWS for c in codes)
    assert covered == sorted(record), f"the rows of the table and the evidence file do not cover the same industries: {set(covered) ^ set(record)}"
    rows = []
    for shown, name, codes, grade, text in STOCK_ROWS:
        model = {values[c] for c in codes}
        assert len(model) == 1, (shown, model)
        model = model.pop()
        assert {record[c][0] for c in codes} == {grade}, (shown, grade, {record[c][0] for c in codes})
        for c in codes:
            if record[c][1] != model:
                print(f"WARNING {c}: evidence recommends {record[c][1]} d, the configuration has {model}")
        rows.append(f"{shown} & {tex(name or SECTOR[codes[0]])} & {num(model)} & {grade} & {text} \\\\")
    (out / "si_stocks.tex").write_text(r"""\begingroup\footnotesize\setlength{\tabcolsep}{4pt}
\begin{longtable}{L{16mm}L{38mm}rcL{76mm}}
\caption{""" + STOCKS_CAPTION + r"""}
\label{tab:stocks} \\
\toprule
industry & & days & grade$^{a}$ & evidence \\
\midrule
\endfirsthead
\toprule
industry & & days & grade$^{a}$ & evidence \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\multicolumn{5}{L{150mm}}{""" + STOCKS_NOTES + r"""} \\
\end{longtable}
\endgroup
""", encoding="utf-8")
    rows = []
    for buyer, inp, label, grade, basis in OVERRIDES:
        v = overrides[buyer][inp]
        if buyer == "*":
            assert overrides["*"]["E"] == v
        who, what = label.split(": ", 1)
        who = who if buyer == "*" else f"{who} ({tex(buyer)})"
        what = what if buyer == "*" else f"{what} ({tex(inp)})"
        rows.append(f"{who} & {what} & {num(v)} & {grade} & {basis} \\\\")
    rows.append(f"any buyer & services and construction (F, G--T) & {num(inv['service_days'])} & -- & "
                f"{OVERRIDES_SERVICES.replace('{days}', num(inv['service_days']))} \\\\")
    (out / "si_stock_overrides.tex").write_text(r"""\begingroup\footnotesize\setlength{\tabcolsep}{4pt}
\begin{longtable}{L{30mm}L{36mm}rcL{65mm}}
\caption{""" + OVERRIDES_CAPTION + r"""}
\label{tab:stockoverrides} \\
\toprule
buyer & input & days & grade & evidence and modeling reason \\
\midrule
\endfirsthead
\toprule
buyer & input & days & grade & evidence and modeling reason \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


'''
s = between(s, "# (buyer, input, label, grade, basis): the input-specific targets of the configuration", "# ------------------------------------------------------------------------------------------------ S1: criticality", STOCKS)

# ---------------------------------------------------------------- S7: the loading curve
LOADING = r'''def loading_table(out: Path):
    """The loading curve with its evidence. 13 Nov 2026 (the author's request): two text columns in plain sentences,
    'evidence' and 'how the value is set' (si_tables_evidence.LOADING_TEXT); the ledger of the anchors, with every
    source, what it measures and the transformation, stays scenarios/draught_table_ledger.csv."""
    d = pd.read_csv(HERE / "scenarios" / "draught_table.csv")
    led = pd.read_csv(HERE / "scenarios" / "draught_table_ledger.csv").set_index("kaub_cm")
    anchors = [int(x) for x in d.kaub_cm]
    assert list(led.index) == anchors, "ledger rows must match the table's anchors"
    assert sorted(LOADING_TEXT) == anchors, "the sentences of the table must match the table's anchors"
    for cm, r in zip(d.kaub_cm, d.itertuples()):
        assert abs(led.fleet[int(cm)] - r.load_factor) < 1e-9, (cm, led.fleet[int(cm)], r.load_factor)
    for cm in (15, 25, 30, 40, 55, 78, 100, 120):         # the sentences that quote the loading share quote the curve's
        assert f"{led.fleet[cm]:.2f}" in LOADING_TEXT[cm][1], (cm, led.fleet[cm], LOADING_TEXT[cm][1])
    rows = "\n".join(f"{cm} & {led.fleet[cm]:.2f} & {LOADING_TEXT[cm][0]} & {LOADING_TEXT[cm][1]} \\\\" for cm in anchors)
    (out / "si_loading_table.tex").write_text(r"""\begingroup\footnotesize\setlength{\tabcolsep}{4pt}
\begin{longtable}{rL{11mm}L{70mm}L{58mm}}
\caption{""" + LOADING_CAPTION + r"""}
\label{tab:loading} \\
\toprule
cm & loading share & evidence & how the value is set \\
\midrule
\endfirsthead
\toprule
cm & loading share & evidence & how the value is set \\
\midrule
\endhead
""" + rows + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


'''
s = between(s, "def loading_table(out: Path):", "# ------------------------------------------------------------------------------------------------ S6, S7", LOADING)

P.write_bytes(s.replace("\n", nl).encode("utf-8"))
print("si_tables.py: rates_table, stocks_table and loading_table print the sentences of si_tables_evidence.py")
