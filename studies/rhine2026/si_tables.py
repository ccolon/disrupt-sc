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
  si_ports.tex              the seaports of the calibrated baseline against Eurostat 2023, with the mechanism of each gap (S2; 1 Nov 2026)

The parameter values are read from config/user_defined_EU.yaml (the configuration of the batch of 30 Sep 2026); the
stock evidence from evidence/inventory_durations_by_industry.md (sections 6.2 and 6.3); the rate evidence is quoted
from evidence/waterway_rates_by_vessel_type.md; the criticality counts from additional_data/input_criticality.csv.

Usage:
    python studies/rhine2026/si_tables.py [--overleaf <repo folder>] [--tag s07|r6_bycargo] [--lists 20261007|20261102]
The run and table names follow --tag / --lists (or RHINE_TAG / RHINE_LISTS) as in make_numbers.py: the defaults reproduce
the tables of 7 October 2026, --tag r6_bycargo --lists 20261102 writes those of the per-class batch of 2 November (3 Nov 2026).
"""
from __future__ import annotations

import argparse
import os
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
BS = chr(92)   # one backslash, for the generated LaTeX of cross_table
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")

# ---- run and table names of the batch (3 Nov 2026): --tag / --lists as in make_numbers.py and plots/batch_names.py. The
# defaults (s07, 20261007) reproduce the tables of 7 October; --tag r6_bycargo --lists 20261102 (or RHINE_TAG, RHINE_LISTS)
# those of the per-class batch of 2 November. set_batch() fills the names the table functions read.
TAG = LISTS = REV = WV = WV9 = CROSS = NORAIL = ALT = B26 = B18 = None


def set_batch(tag: str, lists: str):
    global TAG, LISTS, REV, WV, WV9, CROSS, NORAIL, ALT, B26, B18
    old = tag == "s07"
    TAG, LISTS = tag, lists
    REV = "rev" if old else tag                      # the revision runs: 2026_rev_rail50 / 2026_r6_bycargo_rail50
    WV = "wave07" if old else f"wave_{tag}"          # the waves of the main list
    WV9 = "wave09" if old else f"wave_{tag}"         # the waves at a 15-day refill time (cross list)
    CROSS = "20261009" if old else lists             # the date of the cross list's table
    NORAIL = "20261020" if old else lists            # the date of the no-rail list's table
    ALT = None if old else "20261103"                # the date of the alternative-river list's table (3 Nov 2026, three 2018 runs)
    B26, B18 = f"2026_{tag}_base", f"2018_{tag}_base"


set_batch(os.environ.get("RHINE_TAG", "s07"), os.environ.get("RHINE_LISTS", "20261007"))

OLD_RUNS_CAPTION = r"""\textbf{Every run of the batches of 7 and 9 October 2026.} German value-added loss as a share of a quarter, its peak (share of a week's value added, run week), the EU loss and the household consumption loss (billion USD). The four job lists of 7 October 2026 (\texttt{cluster/jobs\_20261007\_*.txt}), all on the loading curve rebuilt on 6 October: the paper set (36 runs), the paired levers (60), the sensitivities of the revision (16) and the inventory ladder (3). Names: \texttt{2026\_s07\_*} and \texttt{2018\_s07\_*} the two events on the reference network and their variants (\texttt{s07} for the batch of 7 October; the batch of 30 September on the earlier table carried \texttt{s30}); \texttt{seedN} the further networks; \texttt{wave07\_*} the wave-isolation profiles; \texttt{seedN\_<lever>} a lever paired with the base of the same draw; \texttt{rev\_*} the sensitivities of the revision; \texttt{s07\_invNNN} the inventory ladder; \texttt{rev\_rail50\_<lever>} a lever under the 50 kt rail ceiling and \texttt{wave09\_*\_rest15} the wave-isolation profiles at a 15-day refill time (the batch of 9 October, \texttt{jobs\_20261009\_cross.txt})."""
NEW_RUNS_CAPTION = r"""\textbf{Every run of the batches of 2 and 3 November 2026.} German value-added loss as a share of a quarter, its peak (share of a week's value added, run week), the EU loss and the household consumption loss (billion USD). The job lists of 2 November 2026 (\texttt{cluster/jobs\_20261102\_*.txt}) and the alternative-river list of 3 November (\texttt{jobs\_20261103\_altriver.txt}), all on the capacities per cargo class anchored on 1 November (Supplementary Section~S2): the main table (36 runs: the two reference runs, the ten further 2018 networks of 1 November and the 24 runs of the paper set), the paired levers (60), the sensitivities of the revision (16), the inventory ladder (3), the levers under the 50 kt rail ceiling with the waves at a 15-day refill time (8), the no-rail pair (2) and the priced river with closures on the 2018 benchmark at three inventory levels (3). Names: \texttt{2026\_r6\_bycargo\_*} and \texttt{2018\_r6\_bycargo\_*} the two events on the reference network and their variants (\texttt{r6\_bycargo}: the round-6 calibration with the capacities per cargo class); \texttt{seedN} the further networks; \texttt{wave\_r6\_bycargo\_*} the wave-isolation profiles; \texttt{seedN\_<lever>} a lever paired with the base of the same draw; \texttt{invNNN} the inventory ladder; \texttt{rail50\_<lever>} a lever under the 50 kt rail ceiling and \texttt{*\_rest15} the wave-isolation profiles at a 15-day refill time; \texttt{priced}, \texttt{priced\_inv150} and \texttt{priced\_inv200} the alternative representation of the river (Supplementary Section~S6) at inventories $\times$1, $\times$1.5 and $\times$2."""


def batch_text(key: str) -> str:
    """The caption sentences that name the batch: the 7 October texts, or those of the per-class batch of 2 November 2026."""
    new = LISTS != "20261007"
    return {
        "runs": NEW_RUNS_CAPTION if new else OLD_RUNS_CAPTION,
        "channels": ("In the per-class representation of 2 November 2026 the containers sail the Rhine and are rationed by their own class's capacity "
                     "(Methods); the surcharge moves the shipments with an alternative on their own modes off the river before the cut."
                     if new else
                     "No container is cut by the gate or rerouted around it in any run: the model's containers do not use the gated reaches. "
                     "The surcharge moves bulk with an alternative on its own modes off the river before the cut."),
        "issued": ("river information of 30 September; rerun on 2 November on the capacities per cargo class" if new
                   else "river information of 30 September, issued 7 October"),
        "cross": (r"Batch of 2 November 2026 (\texttt{jobs\_20261102\_cross.txt})" if new
                  else r"Batch of 9 October 2026 (\texttt{jobs\_20261009\_cross.txt})"),
        "revision": (r"for the sensitivities of the review of 5 October 2026, rerun on 2 November on the capacities per cargo class (the review's points in brackets; \texttt{jobs\_20261102\_rev.txt})"
                     if new else
                     r"for the sensitivities run after the review of 5 October 2026 on the rebuilt loading curve (the review's points in brackets; \texttt{jobs\_20261007\_rev.txt})"),
    }[key]


def kaub_kt() -> float:
    """The baseline weekly tonnage of the Kaub reach (kt) from the t=0 flow file of the reference run or of the link-level run
    (the largest feature of the reach, as make_numbers.py reads it); the first version's runs were packed without the flow
    file, whose figure the text carried as 1,036 kt."""
    import json
    for r in (B26, f"2026_{TAG}_full"):
        f = RUNS / r / "transport_edges_with_flows_0.geojson"
        if f.exists():
            best = max((float(ft["properties"].get("flow_total_tons") or 0.0) for ft in json.load(open(f, encoding="utf-8"))["features"]
                        if str(ft["properties"].get("name") or "") == "rhine_mainz_koblenz"), default=0.0)
            if best > 0:
                return best / 1e3
    return 1036.0

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
class _Lenient(yaml.SafeLoader):
    """A run's parameters.yaml holds python/PosixPath tags (file paths); the logistics block needs none of them."""


_Lenient.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)


def batch_logistics() -> tuple[dict, bool]:
    """The logistics parameters the batch's runs used. 5 Nov 2026: the table read config/user_defined_EU.yaml, but the
    runs of the per-class batch add the job lists' overrides (--config-set: rail by country, round 2; waterway costs by
    waterway, round 5; seaport fees by port, round 6; --container-water-vot 0.32), so it printed the config's 0.35 and
    none of the regional costs. The reference run's parameters.yaml records what every run of the batch used. The 7 Oct
    tables (TAG s07) keep reading the config."""
    p = RUNS / B26 / "parameters.yaml"
    if TAG != "s07" and p.exists():
        return yaml.load(p.read_text(encoding="utf-8"), _Lenient)["logistics"], True
    return config()["logistics"], False


def regional(node, cargo: str = "default", base_key: str = "default"):
    """(base value, {region: value}) of a cost node: a number, a {cargo: value} dict, or a regional dict keyed by an
    attribute (country code, waterway name) whose 'default' entry covers the regions not listed."""
    pick = lambda d: float(d.get(cargo, d.get("default"))) if isinstance(d, dict) else float(d)
    if not (isinstance(node, dict) and "attribute" in node):
        return pick(node), {}
    others = {k: pick(v) for k, v in node.items() if k not in ("attribute", base_key)}
    if base_key != "default":
        others["(other waterways)"] = pick(node["default"])
    return pick(node[base_key]), others


def rail_cell(bc, cargo: str) -> str:
    base, var = regional(bc["railways"], cargo)
    dear = {k: v for k, v in var.items() if abs(v - base) > 1e-12}
    if not dear:
        return f"{base:.3f}"
    vals = sorted(set(dear.values()))
    return f"{base:.3f} ({' / '.join(f'{v:.3f}' for v in vals)} in {len(dear)} countries: {', '.join(sorted(dear))})"


def water_cell(bc, cargo: str) -> str:
    node = bc["waterways"]
    if not (isinstance(node, dict) and "attribute" in node):
        return f"{regional(node, cargo)[0]:.3f}"
    base, var = regional(node, cargo, base_key="Rhine")
    return f"{base:.3f} on the Rhine, {min(var.values()):.3f}--{max(var.values()):.3f} on the other waterways"


def rates_table(out: Path):
    lg, from_run = batch_logistics()
    bc, vot, dw, lf, sp = lg["basic_cost"], lg["cost_of_time"], lg["dwell_times"], lg["loading_fees"], lg["speeds"]

    def transfer(pair: str) -> str:
        d, f = dw[pair], lf[pair]
        if isinstance(d, dict):
            return "; ".join(f"{lab} {num(d[k])} h / {num(f[k])}" for k, lab in
                             (("container", "containers"), ("dry_bulk", "dry bulk"), ("liquid_bulk", "liquid bulk")))
        return f"{num(d)} h / {num(f)}"

    # notes and rows that exist only with the job lists' overrides (from_run); the 7 Oct tables are unchanged
    rail_note = (" Dearer in the countries named, where the model over-used rail (calibration round 2, Section~S2)."
                 if from_run and isinstance(bc["railways"], dict) and "attribute" in bc["railways"] else "")
    water_note = ""
    if from_run and "attribute" in bc["waterways"]:
        w_base, w_var = regional(bc["waterways"], "dry_bulk", base_key="Rhine")
        same = sorted(k for k, v in w_var.items() if abs(v - w_base) < 1e-12 and not k.startswith("("))
        water_note = (f" Set by waterway in calibration round 5 (Section~S2): the Rhine's values hold on {len(same)} other "
                      f"named waterways ({', '.join(same)}), the others are up to {max(w_var.values()) / w_base:.0f} times "
                      f"dearer (about the same factors for every cargo class).")
    container_note = ("The per-class batch carries containers on the Rhine (\\KaubContMt~Mt a year through Kaub against "
                      "about 10 in the counts, Section~S2), within the capacities of their vessel class (Methods)."
                      if from_run else "The model routes the Rhine's containers by rail (Methods).")
    port_rows = []
    if from_run and isinstance(lf.get("by_port"), dict):
        fees = lf["by_port"]
        cont = [float(v["container"] if isinstance(v, dict) else v) for v in fees.values()]
        other = [float(v["default"] if isinstance(v, dict) else v) for v in fees.values()]
        port_rows.append(f"seaport fee, by port & containers {min(cont):g}--{max(cont):g}, other cargo {min(other):g}--{max(other):g} "
                         f"USD per tonne at {len(fees)} ports & On top of the transfer above: the feeder ladder of calibration round 6 "
                         f"(Section~S2), a fee that falls with the port's tonnage, so that the small ports do not draw the cargo "
                         f"of the large ones. \\\\")

    rows = [
        r"\multicolumn{3}{l}{\emph{Line haul, USD per tonne-kilometre}} \\",
        f"road, containers and dry bulk & {bc['roads']['default']:.3f} & A full-load long-haul rate. No rate series was collected; the Panteia comparison for 2018 gives 0.115 EUR per tonne-kilometre for a tractor-semitrailer at fleet average, empty legs included. Road is never a line-haul mode for bulk (Methods). Calibrated. \\\\",
        f"road, liquid bulk & {bc['roads']['liquid_bulk']:.3f} & Road tankers: dedicated equipment and cleaning. No rate evidence; set with the rail value so that the German liquid-bulk split by mode matches Eurostat 2023 (28 / 42 / 30 road / rail / waterway). Calibrated. \\\\",
        f"rail, containers and dry bulk & {rail_cell(bc, 'default')} & Within the range of block-train and intermodal rates in Europe (0.02--0.04); lowered from 0.044 in the calibration of the modal split (Fig.~S2). Calibrated.{rail_note} \\\\",
        f"rail, liquid bulk & {rail_cell(bc, 'liquid_bulk')} & Tank cars: as the road tankers. Calibrated. \\\\",
        f"inland waterway, dry bulk & {water_cell(bc, 'dry_bulk')} & Push-convoy cost 0.008--0.012 EUR per tonne-kilometre (ores 0.009, coal 0.008; Panteia for KiM 2023, 2021 prices); the published coal rate Rotterdam--Basel of 2015, 10.5 EUR per tonne (0.013; INFRAS for the Swiss Federal Statistical Office). Single motor vessels cost 0.018 (CEMT Va) to 0.036 (Kempenaar), so grain-type flows in single vessels are under-priced in the model.{water_note} \\\\",
        f"inland waterway, liquid bulk & {water_cell(bc, 'liquid_bulk')} & Tanker spot rates: ARA--Karlsruhe 27--29 EUR per tonne in June--July 2025 (0.042--0.045; Riverlake via OPIS) and about 20 in June 2022 (0.031; Handelsblatt), ARA--Cologne 15--17 (0.047--0.053), ARA--Basel 42 in November 2023 (0.051; Refinitiv series in the CCNR price-formation report); operator cost 0.029 (Panteia for KiM). \\\\",
        f"inland waterway, containers & {water_cell(bc, 'container')} & Operator cost 0.025 (Panteia for KiM); Rotterdam--Basel 162--178 EUR per TEU upstream (INFRAS 2015 worked example); Middle Rhine tariffs 125--140 EUR per TEU (Konings 2009), 12--18 EUR per tonne all-in at 10 tonnes per TEU. {container_note} \\\\",
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
    ] + port_rows + [
        r"\midrule",
        r"\multicolumn{3}{l}{\emph{Speed, kilometres per hour}} \\",
        f"road / rail / inland waterway / sea & {num(sp['roads'])} / {num(sp['railways'])} / {num(sp['waterways'])} / {num(sp['maritime'])} & Motorway line haul; freight trains; Rhine barges (about 10 upstream, 15 downstream); short sea. \\\\",
    ]
    (out / "si_rates.tex").write_text(r"""\begin{table}[tbp]
\centering\footnotesize
\caption{\textbf{Transport cost parameters and the rate evidence.} The values used by every run of this paper (the configuration of the batches of 30 September and 7 October 2026, identical but for the loading curve) and the evidence behind them. Operator costs are the Panteia cost figures for the Netherlands Institute for Transport Policy Analysis (KiM, 2023; price level 2021), fleet averages that include empty legs and waiting; the rates are spot quotes and published tariffs as cited in the evidence dossier of the code repository; USD and EUR are treated as equal. No public source prints a full normal-water rate table by vessel class (the CCNR publishes indices), so the waterway values rest on operator costs and the quoted lanes; the rail and road values are calibrated on the modal split (Fig.~S2). ARA: Amsterdam--Rotterdam--Antwerp.}
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
    if from_run:        # the caption names where the values come from (5 Nov 2026)
        f_ = out / "si_rates.tex"
        f_.write_text(f_.read_text(encoding="utf-8").replace(
            "(the configuration of the batches of 30 September and 7 October 2026, identical but for the loading curve)",
            "(as the reference run of the batch of 2 November 2026 records them: the scope's configuration with the "
            "overrides of the job lists, which set rail costs by country, waterway costs by waterway, seaport fees by "
            "port and the containers' value of time on the waterway)"), encoding="utf-8")


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
\caption{\textbf{The modal-switch rule: classification of the Kaub-crossing bulk pairs and threshold sensitivity.} Offline classification of the 2,831 Kaub-crossing bulk origin--destination pairs (5,707 links) on the network of the first closure week of a ten-week run on the 2026 profile (14--15 September 2026; the priced-river representation with the Kaub reach closed to bulk, and the same search that a cut share runs under the capacity limit): under the kilometre rule 1,553 pairs give up (833 million USD of the week's orders), 1,224 deliver on their own modes (385 million) and 54 on the free path (24 million); the run reproduced the classification link by link. The table gives the share of the week's Kaub bulk orders that gives up under each setting of the rule. The access allowance decides the outcome: for nine tenths of the pairs that give up the alternative is barge to Koblenz, 88\,km of truck around the reach and barge again at a median surcharge of 49\,\% on the freight, rejected because 88\,km exceeds the allowance; the pairs whose normal route already has 100\,km or more of road (35\,\%) lengthen that road leg instead, which is what the adopted rule forbids.}
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
    """The loading curve as a source ledger (6 Oct 2026, review NS1): for each anchor its nature, source and date,
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
\caption{\textbf{The loading curve as a source ledger.} Share of the normal tonnage that the Kaub reach can pass at a weekly mean gauge (fleet, the column the model uses) and the loading share of a single large vessel (for comparison), with, for each anchor, its nature (measured, a convention, interpolated or assumed), its source and date, what the source measures (reach, cargo class, period, denominator) and the transformation to the fleet value. Linear between anchors; below 5\,cm the fleet value is held at 0.08. The anchors mix single-vessel payloads, an association's weekly count, a national monthly response and operators' thresholds; they do not measure one quantity, and the table is the authors' reading of them. The table was rebuilt on this ledger on 6 October 2026 (the low end lifted to the weekly count and the single-vessel loads times the fleet's redeployment; unchanged from 55\,cm up); the band of $\pm$15\,\% on the shortfall and the sensitivity on the floor below 5\,cm (Section~S4) bound the result on either side.}
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
    m = table(AD / f"compare_runs_batch_jobs_{LISTS}_main.csv")
    p = table(AD / f"compare_runs_batch_jobs_{LISTS}_paired.csv")
    extra = [table(AD / f) for f in (f"compare_runs_batch_jobs_{LISTS}_rev.csv", f"compare_runs_batch_jobs_{LISTS}_ladder.csv", f"compare_runs_batch_jobs_{CROSS}_cross.csv", f"compare_runs_batch_jobs_{NORAIL}_norail.csv", f"compare_runs_batch_jobs_{ALT}_altriver.csv") if (AD / f).exists()]
    t = pd.concat([m, p] + extra)
    cols = ["DEU_%quarter", "DEU_peak_%week", "DEU_peak_week", "EU_cum_mUSD", "cons_loss_cum_mUSD"]
    rows = "\n".join(f"{tex(r)} & {v['DEU_%quarter']:.2f} & {v['DEU_peak_%week']:.2f} & {int(v['DEU_peak_week'])} & {v['EU_cum_mUSD'] / 1e3:.1f} & {v['cons_loss_cum_mUSD'] / 1e3:.1f} \\\\"
                     for r, v in t[cols].iterrows())
    (out / "si_runs.tex").write_text(r"""\begin{longtable}{lrrrrr}
\caption{""" + batch_text("runs") + r"""}
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
    """The 2018 benchmark under the two representations at several inventory levels. The 7 Oct tables (TAG s07) read the
    first version's runs of 22-28 Sep (matched_estimand_2018_gsladder.txt, _pipe.txt); a later batch reads
    matched_estimand_2018_<TAG>.txt (matched_estimand_2018.py on 2018_<TAG>_base, _inv125, _inv150, _inv200 and the priced
    river rerun of 3 Nov 2026: 2018_<TAG>_priced, _priced_inv150, _priced_inv200), with the first version's priced rows
    while the rerun is pending."""
    lines = {}
    files = ["matched_estimand_2018_gsladder.txt", "matched_estimand_2018_pipe.txt"] + ([f"matched_estimand_2018_{TAG}.txt"] if TAG != "s07" else [])
    for f in files:
        if not (AD / f).exists():
            continue
        for line in (AD / f).read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if parts and parts[0].startswith("2018_") and len(parts) >= 8:
                lines[parts[0]] = parts[1:6] + [parts[6]]
    if TAG == "s07":
        gate = [("2018_gs_inv100", "capacity limit, stocks $\\times$1"), ("2018_gs_inv125", "capacity limit, $\\times$1.25"),
                ("2018_gs_inv150", "capacity limit, $\\times$1.5"), ("2018_gs", "capacity limit, $\\times$2")]
        priced = [("2018_baseline", "priced river with closures, $\\times$1"), ("2018_inv150", "priced river with closures, $\\times$1.5"),
                  ("2018_pipe", "priced river with closures, $\\times$2")]
    else:
        gate = [(f"2018_{TAG}_base", "capacity limit, stocks $\\times$1"), (f"2018_{TAG}_inv125", "capacity limit, $\\times$1.25"),
                (f"2018_{TAG}_inv150", "capacity limit, $\\times$1.5"), (f"2018_{TAG}_inv200", "capacity limit, $\\times$2")]
        priced = [(f"2018_{TAG}_priced", "priced river with closures, $\\times$1"), (f"2018_{TAG}_priced_inv150", "priced river with closures, $\\times$1.5"),
                  (f"2018_{TAG}_priced_inv200", "priced river with closures, $\\times$2")]
        if not all(k in lines for k, _ in priced):
            priced = [("2018_baseline", "priced river with closures, $\\times$1 (first version)"), ("2018_inv150", "priced river with closures, $\\times$1.5 (first version)"),
                      ("2018_pipe", "priced river with closures, $\\times$2 (first version)")]
    order = gate + priced
    priced_new = order[4][0] != "2018_baseline"
    print(f"  representations: {[k for k, _ in order]}")
    from benchmark_ademmer import record, EVENT_MONTHS
    t, s = record(2018, 1)
    ev = t[t.month.isin(EVENT_MONTHS[2018])]
    rows = ["benchmark, published specification (central) & " + " & ".join(f"{v:.2f}" for v in ev.central) + f" & {s['integral']:.2f} \\\\",
            "benchmark, one-standard-deviation band (16--84\\,\\%) & " + " & ".join(f"{a:.2f}--{b:.2f}" for a, b in zip(ev.p16, ev.p84)) + f" & {s['p16']:.2f}--{s['p84']:.2f} \\\\"]
    t3, s3 = record(2018, 3, draws=1)
    ev3 = t3[t3.month.isin(EVENT_MONTHS[2018])]
    rows.append("benchmark, contemporaneous term only & " + " & ".join(f"{v:.2f}" for v in ev3.central) + f" & {s3['integral']:.2f} \\\\")
    rows.append(r"\midrule")
    for key, lab in order:
        if key in lines:
            v = lines[key]
            rows.append(f"{lab} & " + " & ".join(v[:5]) + f" & {v[5]} \\\\")
    (out / "si_representations.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{Two representations of the river on the 2018 benchmark.} Monthly shortfall of German industrial production (\%; the production-index measure, each sector's shortfall rate weighted by its German value added, sections B--D), August to December 2018, and its integral (percent-months, the plain sum of the months). The benchmark is the production path implied by the published regression (ref.~\citep{ademmer2023}; Table~2, column 1, of the working paper) on the low-water days of the daily gauge record, with the 16--84\,\% band of a Monte Carlo over its coefficients and, for comparison, the contemporaneous-only specification (column 3). The model rows are the capacity limit with the surcharge at four inventory levels and the priced river with closures at three; """ + ("runs of 2 and 3 November 2026 on the reference network and the per-class calibration (the capacity limit from the batch of 2 November, the priced river rerun on 3 November with the same flows, loading curve and inventories)" if priced_new else ("runs of 22--28 September 2026 on the reference network, the industrial path unchanged by the later treatment of construction as a non-storable input" if TAG == "s07" else "the capacity-limit rows from the batch of 2 November 2026 on the per-class calibration, the priced-river rows from the first version's runs of 22--28 September 2026 on the earlier calibration")) + r""". Each month of a model row is the mean of its days, every day carrying the value of the model week it belongs to.}
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
    for run, lab in ((B26, "constraint and surcharge (the paper)"), (f"2026_{TAG}_gateonly", "constraint alone"),
                     (f"2026_{TAG}_surchargeonly", "surcharge alone")):
        s = pd.read_csv(RUNS / run / "routing_summary.csv")
        b = s[s.cargo_type.isin(["dry_bulk", "liquid_bulk"])]; c = s[s.cargo_type == "container"]
        rows.append(f"{lab} & {b.alternative_usd.sum() / 1e3:.1f} & {b.capacity_blocked_usd.sum() / 1e3:.1f} & {c.alternative_usd.sum() / 1e3:.1f} & {c.capacity_blocked_usd.sum() / 1e3:.1f} \\\\")
    (out / "si_channels.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{The two channels at the routing level.} Value (billion USD, summed over the 43 weeks of the 2026 run) that leaves its normal route for an alternative, and value that the capacity gate withholds, by cargo class, in the reference run and with each channel alone. """ + batch_text("channels") + r"""}
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
    """The gate at Kaub week by week in the reference run: loading share, tonnage cut, re-sent and withheld (the run's
    log; review OR1, the offered/accepted/withheld report)."""
    prof = pd.read_csv(HERE / "scenarios" / "2026.csv")
    curve = pd.read_csv(HERE / "scenarios" / "draught_table.csv")
    import numpy as np
    lf = lambda cm: float(np.interp(cm, curve.kaub_cm, curve.load_factor, left=curve.load_factor.iloc[0], right=1.0))
    gt = {}
    for line in (RUNS / f"{B26}.log").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"Capacity gate t=(\d+):.*cut ([\d,]+) t, re-sent ([\d,]+) t, blocked ([\d,]+) t", line)
        if m:
            gt[int(m.group(1))] = tuple(float(m.group(i).replace(",", "")) for i in (2, 3, 4))
    n_prof = len(prof)
    tot = lambda sel: tuple(sum(v[i] for t, v in gt.items() if sel(t)) / 1e6 for i in range(3))
    tp, tr, ta = tot(lambda t: t <= n_prof), tot(lambda t: t > n_prof), tot(lambda t: True)
    n_rec = sum(1 for t in gt if t > n_prof)
    horizon = (f"The table covers the {n_prof} profile weeks (cut {tp[0]:.1f}~Mt, re-sent {tp[1]:.1f}, withheld {tp[2]:.1f}); the gate also cuts in the {n_rec} recovery weeks "
               f"in which the refill traffic exceeds the reopened capacity ({tr[0]:.1f}, {tr[1]:.1f} and {tr[2]:.1f}~Mt), for a season total of {ta[0]:.1f}, {ta[1]:.1f} and {ta[2]:.1f}~Mt, "
               "the totals of the text. The totals of a week sum over its rounds, so a share re-sent in one round and cut again at another reach in the next counts in both.")
    rows = []
    for t in range(1, len(prof) + 1):
        r = prof.iloc[t - 1]
        cut, resent, blocked = gt.get(t, (0.0, 0.0, 0.0))
        rows.append(f"{t} & {r.week_start} & {tex(r.status)} & {float(r.kaub_cm):.1f} & {lf(float(r.kaub_cm)):.2f} & {cut / 1e3:.0f} & {resent / 1e3:.0f} & {blocked / 1e3:.0f} \\\\")
    (out / "si_gate.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{rllrrrrr}
\caption{\textbf{The gate week by week, 2026 reference run.} For each profile week: the status of the gauge, its weekly mean (cm), the loading share of the loading curve, and the tonnage (kt) that the gates of the Rhine chain cut, re-sent on another route and withheld (returned to the supplier's inventory), from the run's log. The cut tonnage is the offered load above capacity; the withheld tonnage is what found no acceptable route. """ + f"The baseline flow at Kaub is {kaub_kt():,.0f} kt a week. " + horizon + r"""}
\label{tab:gate} \\
\toprule
week & start & status & Kaub & loading share & cut & re-sent & withheld \\
\midrule
\endfirsthead
\toprule
week & start & status & Kaub & loading share & cut & re-sent & withheld \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


def prospective_table(out: Path):
    """The prospective test (review NS4, E3): the model's monthly industrial shortfall of 2026 on the reference network
    against the path the published specification implies for the same low-water days."""
    from matched_estimand_2018 import model_path
    from benchmark_ademmer import record, EVENT_MONTHS
    labs = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    d = model_path(RUNS / B26, 2026)
    t, s = record(2026, 1)
    ev = t[t.month.isin(EVENT_MONTHS[2026])]
    rows = [f"model, reference network, index measure ({batch_text('issued')}) & " + " & ".join(f"{d[f'ind_{m}']:.1f}" for m in labs) + f" & {d['ind_integrated_pct_months']:.1f} \\\\",
            "model, reference network, production-weighted B--E (the measure of the earlier version) & " + " & ".join(f"{d[f'indprod_{m}']:.1f}" for m in labs) + f" & {d['indprod_integrated_pct_months']:.1f} \\\\"]
    seeds = [RUNS / B26] + [RUNS / f"2026_{TAG}_seed{s}_base" for s in range(1, 11)]
    band = AD / ("prospective_band_2026.csv" if TAG == "s07" else f"prospective_band_2026_{TAG}.csv")   # the 7 Oct file was written by read_batch_20261007_rev.py
    if all((r_ / "firm_data.csv").exists() for r_ in seeds):
        import numpy as np
        a = np.array([[model_path(r_, 2026)[f"ind_{m}"] for m in labs] for r_ in seeds])
        pd.DataFrame({"month": labs, "min": a.min(axis=0), "max": a.max(axis=0), "mean": a.mean(axis=0)}).to_csv(band, index=False)
    if band.exists():
        bd = pd.read_csv(band)
        rows.append("model, range of the eleven networks & " + " & ".join((f"{a:.1f} to {b:.1f}" if b < 0 else f"{a:.1f}--{b:.1f}") for a, b in zip(bd["min"], bd["max"])) + " & \\\\")
    for run, lab in ((f"2026_{TAG}_tablelow", "model, loading curve with the shortfall $\\times$1.15"), (f"2026_{TAG}_tablehigh", "model, loading curve with the shortfall $\\times$0.85")):
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


def prospective_sectors_table(out: Path):
    """Sectoral signatures of the 2026 forecast (review 8 Oct, G2/E3): monthly production shortfall of the German sectors on
    the river and of the transport operators, reference network, production-weighted within the sector."""
    from matched_estimand_2018 import monthly_from_weekly, FIRST
    run = RUNS / B26
    fd = pd.read_csv(run / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0 = fd[fd.time_step == 0].set_index("firm")["production"]
    de = fd[(fd.region == "DEU") & (fd.time_step >= 1)].copy(); de["base"] = de.firm.map(b0)
    months = ["2026-07", "2026-08", "2026-09", "2026-10", "2026-11", "2026-12"]
    names = [("C19", "refined petroleum (C19)"), ("C20", "chemicals (C20)"), ("C23", "non-metallic minerals, cement (C23)"), ("C24A", "iron and steel (C24A)"),
             ("D", "electricity and gas (D)"), ("F", "construction (F)"), ("H49", "land transport (H49)"), ("H50", "water transport (H50)"),
             ("H52", "warehousing and logistics (H52)"), ("IDX", "industry, index measure (B--D, value-added weights)")]
    rows = []
    for code, lab in names:
        if code == "IDX":
            from matched_estimand_2018 import _series
            s = _series(run)[0]
        else:
            sub = de[de.sector == code]
            if not len(sub):
                continue
            s = 100 * (sub.base - sub.production).groupby(sub.time_step).sum() / sub.base.groupby(sub.time_step).sum()
        mo, _ = monthly_from_weekly(s, FIRST[2026], months)
        rows.append(f"{lab} & " + " & ".join(f"{mo[m]:.1f}" for m in months) + f" & {sum(mo.values()):.1f} \\\\")
    (out / "si_prospective_sectors.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{Sectoral signatures of the 2026 forecast.} Monthly shortfall of production (\%, production-weighted within the sector; negative values are production above the no-event baseline) of the German sectors on the river and of the transport operators, reference network, """ + batch_text("issued") + r"""; the last column is the plain sum of the months (percent-months). Pre-specified for the prospective test of the main text: the production index gives the industrial rows by month, the turnover index of transport and storage the operators' rows.}
\label{tab:prospective_sectors}
\begin{tabular}{lrrrrrrr}
\toprule
 & Jul & Aug & Sep & Oct & Nov & Dec & Jul--Dec \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


def cross_table(out: Path):
    """The batch of 9 October 2026 (review of 8 Oct, OR2 and OR3): the four single levers under the 50 kt rail ceiling
    against their no-rail values, and the wave-isolation gap experiment at a 15-day refill time against 30 days."""
    m = table(AD / f"compare_runs_batch_jobs_{LISTS}_main.csv"); r = table(AD / f"compare_runs_batch_jobs_{LISTS}_rev.csv")
    c = table(AD / f"compare_runs_batch_jobs_{CROSS}_cross.csv")
    q = "DEU_%quarter"
    b0, b50 = m.loc[B26, "DEU_cum_mUSD"], r.loc[f"2026_{REV}_rail50", "DEU_cum_mUSD"]
    rows = [f"reference run (no substitution; 50 kt a week) & {m.loc[B26, q]:.2f} & & {r.loc[f'2026_{REV}_rail50', q]:.2f} & " + BS * 2]
    for k, lab in (("stock7", "stocks +7 days"), ("deep20", "fairway +20" + BS + ",cm"), ("stock7t", "targeted stocks +7 days"), ("fleet", "low-water fleet")):
        a0 = 100 * (1 - m.loc[f"2026_{TAG}_{k}", "DEU_cum_mUSD"] / b0); a50 = 100 * (1 - c.loc[f"2026_{REV}_rail50_{k}", "DEU_cum_mUSD"] / b50)
        rows.append(f"{lab} & {m.loc[f'2026_{TAG}_{k}', q]:.2f} & {a0:.0f} & {c.loc[f'2026_{REV}_rail50_{k}', q]:.2f} & {a50:.0f} " + BS * 2)
    a30, b30 = m.loc[f"{WV}_A", q], m.loc[f"{WV}_B", q]; a15, b15 = c.loc[f"{WV9}_A_rest15", q], c.loc[f"{WV9}_B_rest15", q]
    seq30 = {0: m.loc[B26, q], 2: m.loc[f"{WV}_AB_gap2", q], 4: m.loc[f"{WV}_AB_gap4", q]}
    seq15 = {0: r.loc[f"2026_{REV}_rest15", q], 2: c.loc[f"{WV9}_AB_gap2_rest15", q], 4: c.loc[f"{WV9}_AB_gap4_rest15", q]}
    wrows = [f"first wave alone (A) & {a30:.2f} & & {a15:.2f} & " + BS * 2, f"second wave alone (B) & {b30:.2f} & & {b15:.2f} & " + BS * 2,
             f"A + B & {a30 + b30:.2f} & & {a15 + b15:.2f} & " + BS * 2]
    for g in (0, 2, 4):
        wrows.append(f"A then B, {g} weeks of normal water between & {seq30[g]:.2f} & {100 * (seq30[g] / (a30 + b30) - 1):+.0f} & {seq15[g]:.2f} & {100 * (seq15[g] / (a15 + b15) - 1):+.0f} " + BS * 2)
    (out / "si_cross.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{The levers under finite rail, and the memory of the season at a 15-day refill time.} """ + batch_text("cross") + r""". Upper block: German loss (\% of a quarter) with each single lever, and the share of its base's loss it avoids (\%), under the paper's rule (no substitution for bulk) and under the 50 kt a week rail ceiling. Lower block: the two waves of 2026 alone, their sum and their sequence with 0, 2 and 4 weeks of normal water between them, at the 30-day refill time of the paper and at 15 days; the change is the sequence against the sum (\%).}
\label{tab:cross}
\begin{tabular}{lrrrr}
\toprule
 & \multicolumn{2}{c}{no substitution} & \multicolumn{2}{c}{rail 50 kt a week} \\
 & loss & avoided (\%) & loss & avoided (\%) \\
\midrule
""" + "\n".join(rows) + r"""
\midrule
 & \multicolumn{2}{c}{refill time 30 days} & \multicolumn{2}{c}{refill time 15 days} \\
 & loss & change (\%) & loss & change (\%) \\
\midrule
""" + "\n".join(wrows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


def rail_weeks_table(out: Path):
    """The bounded substitution by rail week by week (review of 12 Oct, OR3): the cut bulk that found an eligible rail route
    (offered) and the tonnage placed under each ceiling, from the logs of the four rail runs."""
    def weeks(run: str) -> dict:
        p = RUNS / f"{run}.log"
        if not p.exists():
            return {}
        out = {}
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"Capacity gate t=(\d+):.*relief ([\d,]+) t of ([\d,]+) t offered", line)
            if m:
                out[int(m.group(1))] = (float(m.group(2).replace(",", "")) / 1e3, float(m.group(3).replace(",", "")) / 1e3)
        return out
    runs = {k: weeks(k) for k in (f"2026_{REV}_rail50", f"2026_{REV}_rail140", f"2018_{REV}_rail50", f"2018_{REV}_rail140")}
    if not all(runs.values()):
        raise FileNotFoundError("rail run logs")
    ceilings = {f"2026_{REV}_rail50": 50, f"2026_{REV}_rail140": 140, f"2018_{REV}_rail50": 50, f"2018_{REV}_rail140": 140}
    prof = {"2026": 23, "2018": 22}
    counts = {}
    for k, w in runs.items():
        yr = k[:4]
        binds_prof = sum(1 for t, (pl, of) in w.items() if t <= prof[yr] and of > 0 and pl >= ceilings[k] - 0.5)
        offer_prof = sum(1 for t, (pl, of) in w.items() if t <= prof[yr] and of > 0)
        binds_rec = sum(1 for t, (pl, of) in w.items() if t > prof[yr] and of > 0 and pl >= ceilings[k] - 0.5)
        offer_rec = sum(1 for t, (pl, of) in w.items() if t > prof[yr] and of > 0)
        counts[k] = (binds_prof, offer_prof, binds_rec, offer_rec)
    tmax = max(max(w) for w in runs.values())
    rows = []
    for t in range(1, tmax + 1):
        vals = []
        for k in (f"2026_{REV}_rail50", f"2026_{REV}_rail140", f"2018_{REV}_rail50", f"2018_{REV}_rail140"):
            pl, of = runs[k].get(t, (0.0, 0.0))
            vals.append(f"{of:.0f} & {pl:.0f}" if of > 0 else "--- & ---")
        if all(v.startswith("---") for v in vals):
            continue
        rows.append(f"{t} & " + " & ".join(vals) + " " + BS * 2)
    cap = (f"The 50 kt ceiling binds (the placed tonnage reaches the ceiling) in {counts[f'2026_{REV}_rail50'][0]} of the {prof['2026']} profile weeks of 2026 "
           f"and {counts[f'2018_{REV}_rail50'][0]} of the {prof['2018']} of 2018, and in {counts[f'2026_{REV}_rail50'][2]} and {counts[f'2018_{REV}_rail50'][2]} of the recovery weeks in which bulk is still cut; "
           f"the 140 kt ceiling in {counts[f'2026_{REV}_rail140'][0]} and {counts[f'2018_{REV}_rail140'][0]} profile weeks and {counts[f'2026_{REV}_rail140'][2]} and {counts[f'2018_{REV}_rail140'][2]} recovery weeks.")
    (out / "si_rail_weeks.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{rrrrrrrrr}
\caption{\textbf{The bounded substitution by rail, week by week.} For each run week of the four rail runs (Supplementary Table~\ref{tab:revision}): the cut bulk that found an eligible rail route (offered, kt) and the tonnage placed under the ceiling (placed, kt), from the runs' logs; a dash is a week without a cut. The offered tonnage differs between the two ceilings of an event because the runs differ. """ + cap + r"""}
\label{tab:railweeks} \\
\toprule
 & \multicolumn{2}{c}{2026, 50 kt} & \multicolumn{2}{c}{2026, 140 kt} & \multicolumn{2}{c}{2018, 50 kt} & \multicolumn{2}{c}{2018, 140 kt} \\
week & offered & placed & offered & placed & offered & placed & offered & placed \\
\midrule
\endfirsthead
\toprule
week & offered & placed & offered & placed & offered & placed & offered & placed \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")
    print("  rail weeks:", counts)


def revision_table(out: Path):
    """The sensitivities of the revision (jobs_20261007_rev.txt) against the reference runs (review of 5 Oct 2026)."""
    m = table(AD / f"compare_runs_batch_jobs_{LISTS}_main.csv"); r = table(AD / f"compare_runs_batch_jobs_{LISTS}_rev.csv")
    nr = AD / f"compare_runs_batch_jobs_{NORAIL}_norail.csv"
    if nr.exists():
        r = pd.concat([r, table(nr)])
    rows = []
    for run, lab, base in (
        (f"2026_{REV}_rail50", "bounded substitution by rail, 50 kt a week (review OR2)", B26),
        (f"2026_{REV}_rail140", "bounded substitution by rail, 140 kt a week", B26),
        (f"2018_{REV}_rail50", "2018: bounded substitution, 50 kt a week", B18),
        (f"2018_{REV}_rail140", "2018: bounded substitution, 140 kt a week", B18),
        (f"2026_{REV}_head10", "headroom of the capacity at normal water 10\\,\\% (OR1)", B26),
        (f"2026_{REV}_head25", "headroom 25\\,\\%", B26),
        (f"2026_{REV}_rest15", "refill time of a stock gap 15 days (OR4)", B26),
        (f"2026_{REV}_rest60", "refill time 60 days", B26),
        (f"2026_{REV}_floor04", "loading-table floor below 5\\,cm at 0.04 (NS1)", B26),
        (f"2026_{REV}_floor16", "floor at 0.16", B26),
        (f"2026_{REV}_deeplocal", "fairway +20\\,cm on the Kaub reach alone (NS3)", B26),
        (f"2026_{REV}_fleetwide", "low-water fleet with its gain carried to 100\\,cm (NS2)", B26),
        (f"2026_{REV}_dfuel0", "power sector's fuel-oil input non-critical (E4)", B26),
        (f"2026_{REV}_serv45", "45-day coping duration for the non-storable inputs (E4)", B26),
        (f"2026_{REV}_q25", "outlook's 25th percentile path (NS4)", B26),
        (f"2026_{REV}_q75", "outlook's 75th percentile path", B26),
        (f"2026_{REV}_norail", "no rail alternative for any bulk shipment (line-haul threshold 500\\,km; 20 Oct)", B26),
        (f"2018_{REV}_norail", "2018: no rail alternative for any bulk shipment", B18),
    ):
        if run not in r.index:
            continue
        v, b = r.loc[run], m.loc[base]
        rows.append(f"{lab} & {v['DEU_%quarter']:.2f} & {100 * (v['DEU_%quarter'] / b['DEU_%quarter'] - 1):+.0f} & {v['DEU_peak_%week']:.2f} & {int(v['DEU_peak_week'])} & {v['EU_cum_mUSD'] / 1e3:.1f} \\\\".replace("+", "$+$").replace("-", "$-$", 1) if False else
                    f"{lab} & {v['DEU_%quarter']:.2f} & {100 * (v['DEU_%quarter'] / b['DEU_%quarter'] - 1):+.0f} & {v['DEU_peak_%week']:.2f} & {int(v['DEU_peak_week'])} & {v['EU_cum_mUSD'] / 1e3:.1f} \\\\")
    b26, b18 = m.loc[B26], m.loc[B18]
    head = [f"reference run 2026 & {b26['DEU_%quarter']:.2f} & & {b26['DEU_peak_%week']:.2f} & {int(b26.DEU_peak_week)} & {b26.EU_cum_mUSD / 1e3:.1f} \\\\",
            f"reference run 2018 & {b18['DEU_%quarter']:.2f} & & {b18['DEU_peak_%week']:.2f} & {int(b18.DEU_peak_week)} & {b18.EU_cum_mUSD / 1e3:.1f} \\\\", r"\midrule"]
    (out / "si_revision.tex").write_text(r"""\begin{table}[tbp]
\centering\small
\caption{\textbf{The sensitivities of the revision.} German value-added loss as a share of a quarter, its change against the reference run of the same event, the peak week (share of a week's value added, run week) and the loss of the 28 economies (billion USD), """ + batch_text("revision") + r""". The rail ceilings are 50 kt a week (the 400 wagons that the national rail freight operator could add at short notice in August 2026, at two rotations a week) and 140 kt (the rail response of past low waters, +0.07\,\% of rail tonnage per low-water day over a full low-water month).}
\label{tab:revision}
\begin{tabular}{lrrrrr}
\toprule
 & DEU (\% of a quarter) & change (\%) & peak (\% of a week) & peak week & 28 economies (bn) \\
\midrule
""" + "\n".join(head + rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ S2: seaports
# the mechanism behind each gap of the calibrated baseline (1 Nov 2026, the read of the recalibration rounds):
# "crude ..." = tonnage the statistics count that is not a transport flow of the model (crude and gas are pipelined
# by the rule, sea-to-sea transhipment does not exist); "transhipment hub" = the same at its extreme; "nearest-coast
# landing" = an import landed at the coastal node nearest its buyer under the uniform sea tariff; "landings at X" =
# the tonnage of this port landed at a nearby node instead.
PORT_NOTES = {
    "Rotterdam": "crude and products, transhipment", "Antwerp-Bruges": "crude and products, transhipment",
    "Amsterdam": "coal and oil products; fee 0.75", "Gdansk": "landings at Szczecin", "Algeciras": "transhipment hub",
    "Constanta": "crude; grain exports and Ukraine transit", "Valencia": "transhipment", "Trieste": "crude terminal (TAL pipeline)",
    "Piraeus": "transhipment hub", "Sines": "crude, gas, transhipment", "Cartagena": "crude terminal",
    "Zeeland Seaports": "crude, chemicals", "Gioia Tauro": "transhipment hub", "Tarragona": "crude terminal",
    "Wilhelmshaven": "crude terminal", "Livorno": "ro-ro ferries", "Huelva": "crude terminal",
    "Klaipeda": "oil products, fertilisers", "Augusta": "crude terminal", "Gdynia": "landings at Szczecin",
    "Porto Foxi": "crude terminal", "Agioi Theodoroi": "crude terminal", "Rostock": "ferries; landings at Szczecin",
    "Venezia": "nearest-coast landing (the lagoon)", "Koper": "landings at the lagoon",
    "Monfalcone": "nearest-coast landing (the lagoon)", "Szczecin": "nearest-coast landing", "Burgas": "nearest-coast landing",
    "Helsinki": "nearest-coast landing", "Oslo": "nearest-coast landing", "Málaga": "nearest-coast landing",
    "Sète": "nearest-coast landing", "Civitavecchia": "nearest-coast landing",
}


def ports_table(out: Path, run: str = "r6_h01_feeder3"):
    """The seaports of the calibrated baseline against Eurostat 2023: the ports.csv of flow_score.py on the base run
    (the forty largest ports by gross weight handled, then the ports outside the forty where the model lands 20 Mt
    or more), with the mechanism of each gap from PORT_NOTES."""
    p = pd.read_csv(RUNS / run / "flow_score" / "ports.csv")
    p = p[p["model_mt"].notna() & p["eurostat_mt"].notna()]
    scored = p["scored"].astype(str).str.lower() == "true"
    top = p[scored].sort_values("eurostat_mt", ascending=False)
    rest = p[~scored & (p["model_mt"] >= 20)].sort_values("model_mt", ascending=False)

    def row(r):
        return (f"{tex(r['label'])} & {r['cc']} & {r['eurostat_mt']:.0f} & {r['model_mt']:.0f} & {r['ratio']:.2f} & "
                f"{tex(PORT_NOTES.get(r['label'], ''))} \\\\")
    rows = [row(r) for _, r in top.iterrows()] + [r"\midrule"] + [row(r) for _, r in rest.iterrows()]
    (out / "si_ports.tex").write_text(r"""\begingroup\footnotesize
\begin{longtable}{llrrrl}
\caption{\textbf{The seaports of the calibrated baseline.} The forty largest seaports by gross weight of goods handled (Eurostat 2023, Mt) and the model's tonnage through their connectors; below the line, the ports outside the forty where the model lands 20~Mt or more. The note names the mechanism of a gap: crude, gas and sea-to-sea transhipment are counted by the statistics but are not transport flows of the model (crude and gas are pipelined by construction, a cargo lands once); a transhipment hub has no hinterland flow; a nearest-coast landing is an import landed at the coastal node nearest its buyer under the uniform sea tariff. Two of the forty (Sk\"oldvik, Las Palmas) have no connector in the network and are not shown.}
\label{tab:ports} \\
\toprule
port & & observed & model & ratio & note \\
\midrule
\endfirsthead
\toprule
port & & observed & model & ratio & note \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\endgroup
""", encoding="utf-8")


def main(overleaf: Path, tag: str = None, lists: str = None):
    if tag or lists:
        set_batch(tag or TAG, lists or LISTS)
    print(f"batch: tag {TAG}, lists {LISTS}")
    out = overleaf / "tables"; out.mkdir(exist_ok=True)
    for fn in (rates_table, stocks_table, criticality_table, thresholds_table, loading_table, forecast_table,
               runs_table, representations_table, channels_table, gate_table, prospective_table, prospective_sectors_table, revision_table, cross_table, rail_weeks_table, ports_table):
        try:
            fn(out)
        except FileNotFoundError as e:      # a table whose runs are not extracted yet keeps its previous version
            print(f"  {fn.__name__}: skipped, missing input {Path(str(e).split(': ')[-1].strip(chr(39))).name}")
    print("tables written to", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    ap.add_argument("--tag", default=None, help="run-name tag of the batch (s07: the 7 Oct batch; r6_bycargo: the per-class batch of 2 Nov); default RHINE_TAG or s07")
    ap.add_argument("--lists", default=None, help="date of the job lists (compare_runs_batch_jobs_<date>_*.csv); default RHINE_LISTS or 20261007")
    a = ap.parse_args()
    main(Path(a.overleaf), a.tag, a.lists)
