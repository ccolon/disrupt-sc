"""LaTeX tables of the Supplementary Information, generated from the study's data (30 Sep 2026; extended 5 Oct 2026).

Writes to the Overleaf repository's tables/ folder:
  si_rates.tex              the transport cost parameters of the runs against the rate evidence (S1)
  si_stocks.tex             the stock targets by buying industry and the input-specific overrides, with their basis (S1)
  si_criticality.tex        the survey industry of each ICIO sector and the criticality counts (S1)
  si_loading_table.tex      the draught table with its anchors (review NS2)
  si_forecast.tex           the 2026 profile: outlook of 7 September against the observations (review NS1)
  si_thresholds.tex         the modal-switch rule: offline classification and threshold sensitivity (S4)
  si_representations.tex    the 2018 monthly industrial path under both representations and stock levels (S6)
  si_runs.tex               every run of the batch of 30 Sep: German and EU loss, peak (review S7)

The parameter values are read from config/user_defined_EU.yaml (the configuration of the batch of 30 Sep 2026); the
stock evidence from evidence/inventory_durations_by_industry.md (sections 6.2 and 6.3); the rate evidence is quoted
from evidence/waterway_rates_by_vessel_type.md; the criticality counts from additional_data/input_criticality.csv.

Usage:
    python studies/rhine2026/si_tables.py [--overleaf <repo folder>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "studies/rhine2026"
AD = HERE / "additional_data"
EVIDENCE = HERE / "evidence"
CONFIG = ROOT / "config" / "user_defined_EU.yaml"
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")

sys.path.insert(0, str(HERE))
from build_criticality_eu import ICIO_TO_WIOD  # noqa: E402

SECTOR = {
    "A01": "Crop and animal production", "A02": "Forestry and logging", "A03": "Fishing and aquaculture",
    "B05": "Mining of coal and lignite", "B06": "Extraction of crude petroleum and natural gas", "B07": "Mining of metal ores",
    "B08": "Other mining and quarrying", "B09": "Mining support services",
    "C10T12": "Food, beverages and tobacco", "C13T15": "Textiles, apparel and leather", "C16": "Wood and wood products",
    "C17_18": "Paper products and printing", "C19": "Coke and refined petroleum products", "C20": "Chemicals",
    "C21": "Pharmaceuticals", "C22": "Rubber and plastics", "C23": "Other non-metallic mineral products",
    "C24A": "Basic iron and steel", "C24B": "Non-ferrous metals", "C25": "Fabricated metal products",
    "C26": "Computer, electronic and optical products", "C27": "Electrical equipment", "C28": "Machinery and equipment",
    "C29": "Motor vehicles", "C301": "Ships and boats", "C302T309": "Other transport equipment",
    "C31T33": "Furniture, other manufacturing, repair", "D": "Electricity, gas and steam", "E": "Water, sewerage and waste",
    "F": "Construction", "G": "Wholesale and retail trade", "H49": "Land transport and pipelines", "H50": "Water transport",
    "H51": "Air transport", "H52": "Warehousing and transport support", "H53": "Postal and courier",
    "I": "Accommodation and food services", "J58T60": "Publishing and audiovisual", "J61": "Telecommunications",
    "J62_63": "IT and information services", "K": "Finance and insurance", "L": "Real estate",
    "M": "Professional and scientific services", "N": "Administrative services", "O": "Public administration",
    "P": "Education", "Q": "Health and social work", "R": "Arts and recreation", "S": "Other services",
    "T": "Households as employers",
}


def tex(s) -> str:
    return (str(s).replace("%", r"\%").replace("&", r"\&").replace("_", r"\_").replace("#", r"\#")
            .replace("~", r"$\sim$"))


def table(path: Path) -> pd.DataFrame:
    t = pd.read_csv(path)
    t = t.set_index(t.columns[0])
    if "DEU_cum_mUSD" not in t.columns:
        t = t.T
    return t.apply(pd.to_numeric, errors="coerce")


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def num(v) -> str:
    return f"{float(v):g}"


# ------------------------------------------------------------------------------------------------ S1: rates
def rates_table(out: Path):
    lg = config()["logistics"]
    bc, vot, dw, lf, sp = lg["basic_cost"], lg["cost_of_time"], lg["dwell_times"], lg["loading_fees"], lg["speeds"]

    def transfer(pair: str) -> str:
        d, f = dw[pair], lf[pair]
        if isinstance(d, dict):
            return "; ".join(f"{lab} {num(d[k])} h / {num(f[k])}" for k, lab in
                             (("container", "containers"), ("dry_bulk", "dry bulk"), ("liquid_bulk", "liquid bulk")))
        return f"{num(d)} h / {num(f)}"

    rows = [
        r"\multicolumn{3}{l}{\emph{Line haul, USD per tonne-kilometre}} \\",
        f"road, containers and dry bulk & {bc['roads']['default']:.3f} & A full-load long-haul rate. No rate series was collected; the Panteia comparison for 2018 gives 0.115 EUR per tonne-kilometre for a tractor-semitrailer at fleet average, empty legs included. Road is never a line-haul mode for bulk (Methods). Calibrated. \\\\",
        f"road, liquid bulk & {bc['roads']['liquid_bulk']:.3f} & Road tankers: dedicated equipment and cleaning. No rate evidence; set with the rail value so that the German liquid-bulk split by mode matches Eurostat 2023 (28 / 42 / 30 road / rail / waterway). Calibrated. \\\\",
        f"rail, containers and dry bulk & {bc['railways']['default']:.3f} & Within the range of block-train and intermodal rates in Europe (0.02--0.04); lowered from 0.044 in the calibration of the modal split (Fig.~S2). Calibrated. \\\\",
        f"rail, liquid bulk & {bc['railways']['liquid_bulk']:.3f} & Tank cars: as the road tankers. Calibrated. \\\\",
        f"inland waterway, dry bulk & {bc['waterways']['dry_bulk']:.3f} & Push-convoy cost 0.008--0.012 EUR per tonne-kilometre (ores 0.009, coal 0.008; Panteia for KiM 2023, 2021 prices); the published coal rate Rotterdam--Basel of 2015, 10.5 EUR per tonne (0.013; INFRAS for the Swiss Federal Statistical Office). Single motor vessels cost 0.018 (CEMT Va) to 0.036 (Kempenaar), so grain-type flows in single vessels are under-priced in the model. \\\\",
        f"inland waterway, liquid bulk & {bc['waterways']['liquid_bulk']:.3f} & Tanker spot rates: ARA--Karlsruhe 27--29 EUR per tonne in June--July 2025 (0.042--0.045; Riverlake via OPIS) and about 20 in June 2022 (0.031; Handelsblatt), ARA--Cologne 15--17 (0.047--0.053), ARA--Basel 42 in November 2023 (0.051; Refinitiv series in the CCNR price-formation report); operator cost 0.029 (Panteia for KiM). \\\\",
        f"inland waterway, containers & {bc['waterways']['container']:.3f} & Operator cost 0.025 (Panteia for KiM); Rotterdam--Basel 162--178 EUR per TEU upstream (INFRAS 2015 worked example); Middle Rhine tariffs 125--140 EUR per TEU (Konings 2009), 12--18 EUR per tonne all-in at 10 tonnes per TEU. The model routes the Rhine's containers by rail (Methods). \\\\",
        f"sea & {bc['maritime']:.4f} & The prior of the scope; sea lanes are unconstrained in this study. \\\\",
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Value of time, USD per tonne-hour}} \\",
        f"containers & {vot['container']['default']:.2f} & On road and rail; {vot['container']['waterways']:.2f} on the waterway and {vot['container']['maritime']:.2f} at sea. A cargo-side (inventory) value: the vessel-side cost of time is 0.02--0.07 EUR per tonne-hour at full load and 0.13--0.26 at fleet average (Panteia for KiM); 0.20 in the European Commission's charging study of 2005. \\\\",
        f"dry and liquid bulk & {vot['dry_bulk']:.2f} & All modes. \\\\",
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Terminal transfer, hours of dwell time / USD per tonne}} \\",
        f"road--rail & {transfer('roads-railways')} & Intermodal terminals and bulk sidings at both ends of a rail trip; tank cars are loaded at the shipper's siding. \\\\",
        f"road-- or rail--waterway & {transfer('roads-waterways')} & The fixed per-voyage element of the rates: tankers 3--7 EUR per tonne across lanes (fit to the spot quotes), two container lifts 70--80 EUR per TEU (Konings 2009; 7--8 EUR per tonne at 10 tonnes per TEU); the liquid-bulk terminal set at 8 h and 3.5 USD in the calibration of the German liquid-bulk split. \\\\",
        f"waterway--sea & {transfer('waterways-maritime')} & Port handling. \\\\",
        f"road-- or rail--sea & {transfer('roads-maritime')} & Port handling; the sea leg is unconstrained in this study. \\\\",
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Speed, kilometres per hour}} \\",
        f"road / rail / inland waterway / sea & {num(sp['roads'])} / {num(sp['railways'])} / {num(sp['waterways'])} / {num(sp['maritime'])} & Motorway line haul; freight trains; Rhine barges (about 10 upstream, 15 downstream); short sea. \\\\",
    ]
    (out / "si_rates.tex").write_text(r"""\begin{table}[tbp]
\centering\footnotesize
\caption{\textbf{Transport cost parameters and the rate evidence.} The values used by every run of this paper (the configuration of the batch of 30 September 2026) and the evidence behind them. Operator costs are the Panteia cost figures for the Netherlands Institute for Transport Policy Analysis (KiM, 2023; price level 2021), fleet averages that include empty legs and waiting; the rates are spot quotes and published tariffs as cited in the evidence dossier of the code repository; USD and EUR are treated as equal. No public source prints a full normal-water rate table by vessel class (the CCNR publishes indices), so the waterway values rest on operator costs and the quoted lanes; the rail and road values are calibrated on the modal split (Fig.~S2). ARA: Amsterdam--Rotterdam--Antwerp.}
\label{tab:rates}
\begin{tabular}{lp{34mm}p{82mm}}
\toprule
mode, cargo class & value & evidence \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S1: stocks
def _evidence_rows(start: str, end: str) -> list[list[str]]:
    text = (EVIDENCE / "inventory_durations_by_industry.md").read_text(encoding="utf-8")
    block = text[text.index(start):text.index(end)]
    lines = [l for l in block.splitlines() if l.startswith("| ") and not l.startswith("|---")]
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines[1:]]   # drop the header row


def _codes(label: str) -> tuple[list[str], str, str]:
    """'B05-B09 Mining and quarrying' -> (['B05', ..., 'B09'], 'B05--B09', 'Mining and quarrying')."""
    tok, name = label.split(" ", 1)
    m = re.match(r"([A-Z])(\d+)-([A-Z])(\d+)$", tok)
    if m:
        codes = [f"{m.group(1)}{n:02d}" for n in range(int(m.group(2)), int(m.group(4)) + 1)]
        return codes, tok.replace("-", "--"), name.strip()
    return [tok], tok, SECTOR[tok]


# (buyer, input, label, grade, basis): the input-specific targets of the configuration, with the reason where the model
# departs from the physical figure (evidence section 6.3 and the calibration log of the data repository)
OVERRIDES = [
    ("*", "D", "any buyer: electricity, gas and steam (D), water (E)", "B",
     "Physically non-storable (about 2 days; Bundesbank D--E stocks 3 days). The model has no grid substitution between plants, so a 2-day buffer turned any plant cut into an economy-wide cascade (run of 4 September 2026); kept at the coping duration of the services, a stated limitation of the transport representation."),
    ("D", "B05", "power plants: coal", "B",
     "Reserve plants must hold 30 days of coal (Energy Industry Act, section 50b, inserted by the reserve-plant act of 2022); Steag 2022: about a week on site, 30 days fleet-wide including Rotterdam."),
    ("D", "B06", "power plants: gas", "B",
     "Pipeline-fed: the pipelined-flows rule delivers B06 outside the network, and the 90 days stand for the storage of the gas system, not for a plant stock."),
    ("D", "C19", "power plants: fuel oil", "B", "Oil plants: the 10-day rule of the same act."),
    ("C19", "B06", "refineries: crude oil (and crude import bundles)", "B",
     "Operators' crude stocks are 10--12 days of primary supply (Eurostat holder split, May 2025; EU-27 operators 18.7 days). Crude reaches the refineries by pipeline, and the 90 days are the stockholding obligation of Directive 2009/119/EC (90 days of net imports) carried by the pipeline system; crude never stops a refinery in the runs, and the refinery pathway of the German loss is refined products."),
    ("C24A", "B07", "steelworks: iron ore", "B",
     "Duisburg normally holds one to two months of ore and coal (Platts, 12 August 2026); stockyard design 7--45 days."),
    ("C24A", "B05", "steelworks: coking coal", "B", "As ore."),
    ("C20", "C19", "chemical plants: liquid feedstocks (naphtha, LPG)", "C",
     "No published figure; the timing of the force-majeure warnings of July 2026 (ICIS) against the balance-sheet average of 30 days for all chemical inputs."),
    ("C20", "B06", "chemical plants: gas and condensate", "C", "As the liquid feedstocks."),
    ("C10T12", "A01", "mills: grain and oilseeds", "B",
     "Flour mills: silo capacity of two production weeks (Verband Deutscher M\\\"uhlen site report); oil mills 5--10 days; feed plants just in time; the grain stocks sit upstream on farms and in trade."),
    ("C23", "B05", "cement plants: coal", "C",
     "Externally supplied fuels 21--30 days (vendor and engineering sources); clinker 7--14 days."),
    ("C23", "C19", "cement plants: petroleum coke", "C", "As coal."),
    ("H49", "C19", "hauliers: fuel", "B", "Bundesbank H raw-material stock 7.3 days (fuel, tyres, spares)."),
]


def stocks_table(out: Path):
    inv = config()["inventory_duration_targets"]
    values, overrides = inv["values"], inv["overrides"]
    rows = []
    for label, rec, lean, grade, basis in _evidence_rows("### 6.2 Recommended table", "### 6.3 Input-type overrides"):
        codes, codes_tex, name = _codes(label)
        model = {values[c] for c in codes}
        assert len(model) == 1, (label, model)
        model = model.pop()
        recommended = int(re.match(r"\d+", rec).group())
        if recommended != model:
            print(f"WARNING {label}: evidence recommends {recommended} d, the configuration has {model}")
        lean_tex = "--" if lean == "-" else lean
        basis = basis.replace("M&S", "materials and supplies").replace("&", " and ")   # no & in a cell: the lint counts them
        rows.append(f"{tex(codes_tex)} & {tex(name)} & {num(model)} & {lean_tex} & {grade} & {tex(basis)} \\\\")
    rows.append(r"\midrule")
    rows.append(r"\multicolumn{6}{l}{\emph{Input-specific targets (buyer: input), overriding the industry value}} \\")
    for buyer, inp, label, grade, basis in OVERRIDES:
        v = overrides[buyer][inp]
        if buyer == "*":
            assert overrides["*"]["E"] == v
        rows.append(f"{tex(buyer if buyer != '*' else 'any')}: {tex(inp)} & {tex(label)} & {num(v)} & -- & {grade} & {basis} \\\\")
    st = ", ".join(inv["service_types"])
    rows.append(f"any: F, G--T & services and construction & {num(inv['service_days'])} & -- & -- & Non-storable inputs (types {tex(st)}): the buyer copes for {num(inv['service_days'])} days without a stock, the model's coping duration. Construction joined the list on 30 September 2026: its buyers had held goods-stock days of it (real estate 10 days, builders 10 days of subcontracting), which cost real estate 2.0 billion USD and doubled the construction loss; the 2026 loss moved from 1.58 to 1.24\\,\\% of a quarter, every other sector and the 2018 industrial path unchanged. \\\\")
    (out / "si_stocks.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{llrrlp{68mm}}
\caption{\textbf{Stock targets by buying industry.} Days of consumption of purchased goods inputs that each buying industry holds at the baseline (the model's value) and the evidence: the lean value of 2019 where the series exists, the grade (A: balance-sheet data for the industry itself; B: data for a group of industries, or physical stock data; C: indirect; D: assumed) and the basis. RHB: raw materials, consumables and supplies over material costs, times 365, from the extrapolated corporate balance sheets of the Bundesbank (2023; the lean column 2019); ratio series: the Bundesbank ratio statistics by division (non-finished stock over material costs, which includes work in progress); FIBEN: the Banque de France sector sheets (median stocks over turnover); Census: the US Census M3 materials-and-supplies inventories over the cost of materials; EKBG: the German reserve-plant act of 2022. The lower block gives the input-specific targets that override the industry value, with the modelling reason where the model departs from the physical figure.}
\label{tab:stocks} \\
\toprule
industry & & days & lean & grade & basis \\
\midrule
\endfirsthead
\toprule
industry & & days & lean & grade & basis \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S1: criticality
NOTE = {
    "B05": "the survey's one mining industry", "B06": "as B05", "B07": "as B05", "B08": "as B05", "B09": "as B05",
    "C17_18": "paper, the larger of the two and the one with physical inputs", "C24A": "basic metals", "C24B": "basic metals",
    "C301": "other transport equipment", "C302T309": "other transport equipment", "C31T33": "furniture and other manufacturing",
    "E": "water supply, the critical utility input", "G": "wholesale; trade margins are a non-critical input in the survey",
    "J58T60": "publishing", "K": "financial services", "M": "legal, accounting and head offices",
    "R": "arts, recreation and other services", "S": "as R",
    "T": "not rated as a buyer in the survey (no real inputs): its inputs are non-critical",
}


def criticality_table(out: Path):
    crit = pd.read_csv(AD / "input_criticality.csv", index_col=0)
    sectors = list(crit.columns)
    rows = []
    for s in sectors:
        col, row = crit[s], crit.loc[s]
        rows.append(f"{tex(s)} & {tex(SECTOR[s])} & {tex(ICIO_TO_WIOD[s])} & {tex(NOTE.get(s, ''))} & "
                    f"{int((col >= 1).sum())} & {int(((col >= 0.5) & (col < 1)).sum())} & {int((col < 0.5).sum())} & {int((row >= 1).sum())} \\\\")
    vals = crit.values.ravel()
    c, i, n = (100 * (vals >= 1).mean(), 100 * ((vals >= 0.5) & (vals < 1)).mean(), 100 * (vals < 0.5).mean())
    (out / "si_criticality.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{llcp{34mm}rrrr}
\caption{\textbf{The criticality survey mapped to the 50 sectors.} Each sector of the input--output table (OECD ICIO, 2025 edition) is matched to one industry of the survey used by ref.~\citep{pichler2022} (55 industries of the World Input--Output Database, NACE Rev.~2); the note gives the judgement where the match is not one to one. The counts are, for the sector as a buyer, how many of its 50 input sectors the survey rates critical (output limited by the input), important (a depleted input halves output) and non-critical, and, for the sector as an input, how many buyers rate it critical. Imports carry the sector of the exporting bloc, so an imported chemical is as critical as a domestic one; an unrated pair is treated as critical; in the model an input also has to exceed 2\,\% of the buyer's input costs to bind (Methods). Over the 2,500 cells: """ + f"{c:.0f}\\,\\% critical, {i:.0f}\\,\\% important, {n:.0f}\\,\\% non-critical." + r"""}
\label{tab:criticality} \\
\toprule
sector & & survey & note & critical & important & non-critical & critical for \\
\midrule
\endfirsthead
\toprule
sector & & survey & note & critical & important & non-critical & critical for \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S4: thresholds
def thresholds_table(out: Path):
    """Numbers of the verification of 14--15 Sep 2026 (calibration log of the data repository, 'Line-haul rule verified'):
    offline classification of the Kaub-crossing bulk pairs on the week-6 network of lrcheck_base_lh and the share of
    the week's Kaub bulk orders (by value) that gives up under each setting of the rule."""
    rows = [
        "kilometre rule alone: access allowance 50\\,km, line-haul threshold 100\\,km & 67 \\\\",
        "access allowance 90--100\\,km & 5 \\\\",
        "line-haul threshold 200\\,km & 86 \\\\",
        "line-haul threshold 500\\,km & 97 \\\\",
        "road never a line-haul mode for bulk, access allowance 50\\,km (the adopted rule) & 85 \\\\",
        "road never a line-haul mode for bulk, access allowance 100\\,km & 22 \\\\",
        "the previous search, not penalty-aware & 81 \\\\",
    ]
    (out / "si_thresholds.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{The modal-switch rule: classification of the Kaub-crossing bulk pairs and threshold sensitivity.} Offline classification of the 2,831 Kaub-crossing bulk origin--destination pairs (5,707 links) on the network of the first closure week of a ten-week run on the 2026 profile (14--15 September 2026; the priced-river representation with the Kaub reach closed to bulk, and the same search that a cut share runs under the quantity constraint): under the kilometre rule 1,553 pairs give up (833 million USD of the week's orders), 1,224 deliver on their own modes (385 million) and 54 on the free path (24 million); the run reproduced the classification link by link. The table gives the share of the week's Kaub bulk orders that gives up under each setting of the rule. The access allowance decides the outcome: for nine tenths of the pairs that give up the alternative is barge to Koblenz, 88\,km of truck around the reach and barge again at a median surcharge of 49\,\% on the freight, rejected because 88\,km exceeds the allowance; the pairs whose normal route already has 100\,km or more of road (35\,\%) lengthen that road leg instead, which is what the adopted rule forbids.}
\label{tab:thresholds}
\begin{tabular}{p{118mm}r}
\toprule
setting of the rule & gives up (\% of the week's Kaub bulk orders) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S3: loading, forecast
def loading_table(out: Path):
    """The loading table as a source ledger (6 Oct 2026, review NS1): for each anchor its nature, source and date,
    what the source measures (reach, cargo, period, denominator) and the transformation to the fleet value."""
    d = pd.read_csv(HERE / "scenarios" / "draught_table.csv")
    led = pd.read_csv(HERE / "scenarios" / "draught_table_ledger.csv").set_index("kaub_cm")
    assert list(led.index) == [int(x) for x in d.kaub_cm], "ledger rows must match the table's anchors"
    for cm, r in zip(d.kaub_cm, d.itertuples()):
        assert abs(led.fleet[int(cm)] - r.load_factor) < 1e-9, (cm, led.fleet[int(cm)], r.load_factor)
    rows = "\n".join(f"{int(cm)} & {led.fleet[int(cm)]:.2f} & {led.vessel[int(cm)]:.2f} & {tex(led.nature[int(cm)])} & {tex(led.source[int(cm)])} & {tex(led.measures[int(cm)])} & {tex(led.transformation[int(cm)])} \\\\"
                     for cm in d.kaub_cm)
    (out / "si_loading_table.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{rrrp{15mm}p{38mm}p{34mm}p{40mm}}
\caption{\textbf{The loading table as a source ledger.} Share of the normal tonnage that the Kaub reach can pass at a weekly mean gauge (fleet, the column the model uses) and the load factor of a single large vessel (for comparison), with, for each anchor, its nature (measured, a convention, interpolated or assumed), its source and date, what the source measures (reach, cargo class, period, denominator) and the transformation to the fleet value. Linear between anchors; below 5\,cm the fleet value is held at 0.08. The anchors mix single-vessel payloads, an association's weekly count, a national monthly response and operators' thresholds; they do not measure one quantity, and the table is the authors' reading of them. The table was rebuilt on this ledger on 6 October 2026 (the low end lifted to the weekly count and the single-vessel loads times the fleet's redeployment; unchanged from 55\,cm up); the band of $\pm$15\,\% on the shortfall and the sensitivity on the floor below 5\,cm (Section~S4) bound the result on either side.}
\label{tab:loading} \\
\toprule
cm & fleet & vessel & nature & source & measures & transformation \\
\midrule
\endfirsthead
\toprule
cm & fleet & vessel & nature & source & measures & transformation \\
\midrule
\endhead
""" + rows + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


def forecast_table(out: Path):
    old = pd.read_csv(HERE / "scenarios" / "2026_vintage0910.csv").set_index("week_start")
    new = pd.read_csv(HERE / "scenarios" / "2026.csv").set_index("week_start")
    rows = []
    for w in new.index:
        o = old.kaub_cm.get(w, float("nan")); os_ = old.status.get(w, "")
        n = new.kaub_cm[w]; ns = new.status[w]
        rows.append(f"{w} & {o:.1f} & {tex(os_)} & {n:.1f} & {tex(ns)} \\\\" if pd.notna(o) else f"{w} & -- & -- & {n:.1f} & {tex(ns)} \\\\")
    (out / "si_forecast.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{The two vintages of the 2026 profile.} Weekly mean gauge at Kaub (cm): the vintage of 10 September (observations to 10 September, the BfG six-week outlook of 7 September, assumed values after it) against the vintage of 30 September (observations to 29 September, the outlook of 28 September, assumed recovery). The outlook of 7 September missed the end-of-September trough by 20 to 40\,cm.}
\label{tab:forecast}
\begin{tabular}{lrlrl}
\toprule
week of & vintage 10 Sep & status & vintage 30 Sep & status \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S6, S7
def runs_table(out: Path):
    m = table(AD / "compare_runs_batch_jobs_20261007_main.csv")
    p = table(AD / "compare_runs_batch_jobs_20261007_paired.csv")
    t = pd.concat([m, p])
    cols = ["DEU_%quarter", "DEU_peak_%week", "DEU_peak_week", "EU_cum_mUSD", "cons_loss_cum_mUSD"]
    rows = "\n".join(f"{tex(r)} & {v['DEU_%quarter']:.2f} & {v['DEU_peak_%week']:.2f} & {int(v['DEU_peak_week'])} & {v['EU_cum_mUSD'] / 1e3:.1f} & {v['cons_loss_cum_mUSD'] / 1e3:.1f} \\\\"
                     for r, v in t[cols].iterrows())
    (out / "si_runs.tex").write_text(r"""\begin{longtable}{lrrrrr}
\caption{\textbf{Every run of the batch of 7 October 2026.} German value-added loss as a share of a quarter, its peak (share of a week's value added, run week), the EU loss and the household consumption loss (billion USD). Names: \texttt{2026\_s30\_*} and \texttt{2018\_s30\_*} the two events on the reference draw and their variants; \texttt{seedN} the further draws; \texttt{wave30\_*} the wave-isolation profiles; \texttt{seedN\_<lever>} a lever paired with the base of the same draw.}
\label{tab:runs} \\
\toprule
run & DEU (\% of a quarter) & peak (\% of a week) & peak week & EU (bn) & consumption (bn) \\
\midrule
\endfirsthead
\toprule
run & DEU (\% of a quarter) & peak (\% of a week) & peak week & EU (bn) & consumption (bn) \\
\midrule
\endhead
""" + rows + r"""
\bottomrule
\end{longtable}
""", encoding="utf-8")


def representations_table(out: Path):
    lines = {}
    for name, f in (("gs", "matched_estimand_2018_gsladder.txt"), ("pipe", "matched_estimand_2018_pipe.txt")):
        for line in (AD / f).read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if parts and parts[0].startswith("2018_") and len(parts) >= 8:
                lines[parts[0]] = parts[1:6] + [parts[6]]
    order = [("2018_gs_inv100", "quantity constraint, stocks $\\times$1"), ("2018_gs_inv125", "quantity constraint, $\\times$1.25"),
             ("2018_gs_inv150", "quantity constraint, $\\times$1.5"), ("2018_gs", "quantity constraint, $\\times$2"),
             ("2018_baseline", "priced river with closures, $\\times$1"), ("2018_inv150", "priced river with closures, $\\times$1.5"),
             ("2018_pipe", "priced river with closures, $\\times$2")]
    from benchmark_ademmer import record, EVENT_MONTHS
    t, s = record(2018, 1)
    ev = t[t.month.isin(EVENT_MONTHS[2018])]
    rows = ["record, published specification (central) & " + " & ".join(f"{v:.2f}" for v in ev.central) + f" & {s['integral']:.2f} \\\\",
            "record, 16--84\\,\\% band & " + " & ".join(f"{a:.2f}--{b:.2f}" for a, b in zip(ev.p16, ev.p84)) + f" & {s['p16']:.2f}--{s['p84']:.2f} \\\\"]
    t3, s3 = record(2018, 3, draws=1)
    ev3 = t3[t3.month.isin(EVENT_MONTHS[2018])]
    rows.append("record, contemporaneous term only & " + " & ".join(f"{v:.2f}" for v in ev3.central) + f" & {s3['integral']:.2f} \\\\")
    rows.append(r"\midrule")
    for key, lab in order:
        if key in lines:
            v = lines[key]
            rows.append(f"{lab} & " + " & ".join(v[:5]) + f" & {v[5]} \\\\")
    (out / "si_representations.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{Two representations of the river on the 2018 record.} Monthly shortfall of German industrial production (\%), August to December 2018, and its integral (percent-months, the plain sum of the months). The record is the dynamic counterfactual of the published specification (ref.~\citep{ademmer2023}; Table~2, column 1, of the working paper) on the low-water days of the daily gauge record, with the 16--84\,\% band of a Monte Carlo over its coefficients and, for comparison, the contemporaneous-only specification (column 3). The model rows are the quantity constraint with the surcharge at four stock levels and the priced river with closures at three; runs of 22--28 September 2026 on the reference draw, the industrial path unchanged by the later treatment of construction as a non-storable input. Each month of a model row is the mean of its days, every day carrying the value of the model week it belongs to.}
\label{tab:representations}
\begin{tabular}{lrrrrrr}
\toprule
 & Aug & Sep & Oct & Nov & Dec & integral \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S4: channels, gate
RUNS = Path("C:/dsc_runs/rhine2026")


def channels_table(out: Path):
    """What leaves the normal route and what the gate withholds, by cargo class, base against each channel alone
    (routing_summary.csv totals over the run; revision of 6 Oct 2026, review C05)."""
    rows = []
    for run, lab in (("2026_s07_base", "constraint and surcharge (the paper)"), ("2026_s07_gateonly", "constraint alone"),
                     ("2026_s07_surchargeonly", "surcharge alone")):
        s = pd.read_csv(RUNS / run / "routing_summary.csv")
        b = s[s.cargo_type.isin(["dry_bulk", "liquid_bulk"])]; c = s[s.cargo_type == "container"]
        rows.append(f"{lab} & {b.alternative_usd.sum() / 1e3:.1f} & {b.capacity_blocked_usd.sum() / 1e3:.1f} & {c.alternative_usd.sum() / 1e3:.1f} & {c.capacity_blocked_usd.sum() / 1e3:.1f} \\\\")
    (out / "si_channels.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{The two channels at the routing level.} Value (billion USD, summed over the 43 weeks of the 2026 run) that leaves its normal route for an alternative, and value that the capacity gate withholds, by cargo class, in the reference run and with each channel alone. No container is cut by the gate or rerouted around it in any run: the model's containers do not use the gated reaches. The surcharge moves bulk with an alternative on its own modes off the river before the cut.}
\label{tab:channels}
\begin{tabular}{lrrrr}
\toprule
 & bulk, alternative & bulk, withheld & containers, alternative & containers, withheld \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


def gate_table(out: Path):
    """The gate at Kaub week by week in the reference run: load factor, tonnage cut, re-sent and withheld (the run's
    log; review OR1, the offered/accepted/withheld report)."""
    prof = pd.read_csv(HERE / "scenarios" / "2026.csv")
    curve = pd.read_csv(HERE / "scenarios" / "draught_table.csv")
    import numpy as np
    lf = lambda cm: float(np.interp(cm, curve.kaub_cm, curve.load_factor, left=curve.load_factor.iloc[0], right=1.0))
    gt = {}
    for line in (RUNS / "2026_s07_base.log").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"Capacity gate t=(\d+):.*cut ([\d,]+) t, re-sent ([\d,]+) t, blocked ([\d,]+) t", line)
        if m:
            gt[int(m.group(1))] = tuple(float(m.group(i).replace(",", "")) for i in (2, 3, 4))
    rows = []
    for t in range(1, len(prof) + 1):
        r = prof.iloc[t - 1]
        cut, resent, blocked = gt.get(t, (0.0, 0.0, 0.0))
        rows.append(f"{t} & {r.week_start} & {tex(r.status)} & {float(r.kaub_cm):.1f} & {lf(float(r.kaub_cm)):.2f} & {cut / 1e3:.0f} & {resent / 1e3:.0f} & {blocked / 1e3:.0f} \\\\")
    (out / "si_gate.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{rllrrrrr}
\caption{\textbf{The gate week by week, 2026 reference run.} For each profile week: the status of the gauge, its weekly mean (cm), the load factor of the loading table, and the tonnage (kt) that the gates of the Rhine chain cut, re-sent on another route and withheld (returned to the supplier's stock), from the run's log. The cut tonnage is the offered load above capacity; the withheld tonnage is what found no acceptable route. The baseline flow at Kaub is 1,036 kt a week.}
\label{tab:gate} \\
\toprule
week & start & status & Kaub & load factor & cut & re-sent & withheld \\
\midrule
\endfirsthead
\toprule
week & start & status & Kaub & load factor & cut & re-sent & withheld \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


def prospective_table(out: Path):
    """The prospective test (review NS4, E3): the model's monthly industrial shortfall of 2026 on the reference draw
    against the path the published specification implies for the same low-water days."""
    from matched_estimand_2018 import model_path
    from benchmark_ademmer import record, EVENT_MONTHS
    labs = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    d = model_path(RUNS / "2026_s07_base", 2026)
    t, s = record(2026, 1)
    ev = t[t.month.isin(EVENT_MONTHS[2026])]
    rows = ["model, reference draw (forecast of 30 September) & " + " & ".join(f"{d[f'ind_{m}']:.1f}" for m in labs) + f" & {d['ind_integrated_pct_months']:.1f} \\\\"]
    band = AD / "prospective_band_2026.csv"      # written by read_batch_20261006.py once the seed bases are repacked with firm data
    if band.exists():
        bd = pd.read_csv(band)
        rows.append("model, range of the eleven draws & " + " & ".join(f"{a:.1f}--{b:.1f}" for a, b in zip(bd["min"], bd["max"])) + " & \\\\")
    for run, lab in (("2026_s07_tablelow", "model, loading table with the shortfall $\\times$1.15"), ("2026_s07_tablehigh", "model, loading table $\\times$0.85")):
        if (RUNS / run / "firm_data.csv").exists():
            dd = model_path(RUNS / run, 2026)
            rows.append(f"{lab} & " + " & ".join(f"{dd[f'ind_{m}']:.1f}" for m in labs) + f" & {dd['ind_integrated_pct_months']:.1f} \\\\")
    rows += ["published specification on the same low-water days & " + " & ".join(f"{v:.1f}" for v in ev.central) + f" & {s['integral']:.1f} \\\\",
            "its 16--84\\,\\% band & " + " & ".join(f"{a:.1f}--{b:.1f}" for a, b in zip(ev.p16, ev.p84)) + f" & {s['p16']:.1f}--{s['p84']:.1f} \\\\",
            "low-water days (observed to 29 September, then the profile) & " + " & ".join(str(int(v)) for v in ev.low_water_days) + " & \\\\"]
    (out / "prospective.tex").write_text(r"""\begin{tabular}{lrrrrrrr}
\toprule
 & Jul & Aug & Sep & Oct & Nov & Dec & Jul--Dec \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
""", encoding="utf-8")


def main(overleaf: Path):
    out = overleaf / "tables"; out.mkdir(exist_ok=True)
    rates_table(out); stocks_table(out); criticality_table(out); thresholds_table(out)
    loading_table(out); forecast_table(out); runs_table(out); representations_table(out)
    channels_table(out); gate_table(out); prospective_table(out)
    print("tables written to", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    a = ap.parse_args()
    main(Path(a.overleaf))
