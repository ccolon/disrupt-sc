r"""SI, round of 11 November 2026, part A: the author's version of that morning (Overleaf 41f0e3c) and the answers to the
open points of the round of 10 November that do not depend on the plan for the 2026 test or on the new structure.

  point 4   the column "total" of the weekly table of flows turned away at Kaub goes;
  point 6   the paragraph on the French chain goes (its last sentence, on the tables of chains, joins the paragraph before);
  N04, N05  the acronyms of the transport-cost table become table notes with a superscript at their first use;
  N06       the caption of the inventory table names its sources;
  N07       the grades are explained in a table note, with a superscript in the header;
  N08       work in progress and the ratio series are explained; the row of agriculture says how 49 days become 30;
  N09       the CCNR is named in full at its first uses (the main text does not use the acronym);
  N12       the table of rail weeks goes; its counts stay in a sentence (new macros RailBind*).
  Direct edits checked; four corrected: a doubled "in", a paragraph title without its period, "2\%" and what the
  headroom applies to, and the 10 cm row of the loading curve, which is an anchor of the curve the model uses (restored).

Notes N01 to N03 (evidence on two transfers, the dollar and the euro) are in part B; N10 and N11 wait for the structure.
    python patch_si_20261111_a.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "si.tex")

# ---- S1, transport-cost table: acronyms as table notes (N04, N05), the CCNR in full (N09) ------------------------
d.sub(r"Single motor vessels cost 0.018 (CEMT class Va) to 0.036 (Kempenaar)~\citep{kim2023}",
      r"Single motor vessels cost 0.018 (CEMT class Va$^{a}$) to 0.036 (Kempenaar$^{a}$)~\citep{kim2023}")
d.sub(r"Tanker spot rates: ARA--Karlsruhe 27--29 EUR per tonne", r"Tanker spot rates: ARA$^{b}$--Karlsruhe 27--29 EUR per tonne")
d.sub(r"Rotterdam--Basel 162--178 EUR per TEU upstream in 2015", r"Rotterdam--Basel 162--178 EUR per TEU$^{c}$ upstream in 2015")
d.sub(r"the CCNR publishes indices. ARA\todo{add table note with superscript for this acronym}: Amsterdam--Rotterdam--Antwerp. "
      r"TEU: twenty-foot equivalent unit. CEMT Va and Kempenaar\todo{same: add note}: classes of motor vessels.}",
      r"the Central Commission for the Navigation of the Rhine (CCNR) publishes indices. "
      r"$^{a}$Classes of motor vessels in the European classification of inland waterways (CEMT): class Va carries 1,500 to 3,000 tonnes, "
      r"the Kempenaar (class II) 400 to 650. $^{b}$ARA: the seaports of Amsterdam, Rotterdam and Antwerp. "
      r"$^{c}$TEU: twenty-foot equivalent unit.}")

# ---- S1, inventory table: sources in the caption (N06), grades (N07), work in progress and the ratio series (N08) --
d.line(r"\caption{\textbf{Inventory targets by buying industry.}",
       r"\caption{\textbf{Inventory targets by buying industry.} Days of consumption of purchased goods inputs that each industry holds "
       r"at the baseline. The main source is the corporate balance-sheet statistics of the Bundesbank~\citep{bundesbank2025}, complemented by "
       r"the sector sheets of the Banque de France~\citep{banquefrance2025fiben} and the manufacturers' survey of the US Census "
       r"Bureau~\citep{census2026m3}. Each value carries a grade for its evidence (author's judgment). Input-specific targets are given in "
       r"Table~\ref{tab:stockoverrides}.}")
d.sub(r"industry & & days & grade\todo{add superscript to explain the grade levels} & evidence \\", r"industry & & days & grade$^{a}$ & evidence \\")
d.sub(r"industry & & days & grade & evidence \\", r"industry & & days & grade$^{a}$ & evidence \\")
d.line(r"A01 & Crop and animal production & 30 & C & ",
       r"A01 & Crop and animal production & 30 & C & Ratio series$^{b}$ A: non-finished stock of 49 d of material costs. It counts growing "
       r"crops and livestock as work in progress (WIP), so it is an upper bound; 30 d is assumed below it. Feed and fertilizer stocks sit on "
       r"farms (BLE$^{c}$). \\")
d.sub(r"Ratio series B: 74 d incl. WIP; FIBEN B median 50 d of turnover; RHB not split.",
      r"Ratio series B: 74 d incl. WIP; FIBEN$^{d}$ B median 50 d of turnover; RHB$^{e}$ not split.")
d.sub(r"FIBEN 10 median 18 d; Census food $\sim$15 d", r"FIBEN 10 median 18 d; Census$^{f}$ food $\sim$15 d")
d.sub(r"(Eurostat holder split, May 2025; BAFA 2024 flows)", r"(Eurostat holder split, May 2025; BAFA$^{g}$ 2024 flows)")
d.sub(r"Strategic (EBV/CSE) stocks excluded.", r"Strategic (EBV/CSE$^{h}$) stocks excluded.")
d.sub(r"EKBG minimum 30 d on site for coal reserve plants", r"EKBG$^{i}$ minimum 30 d on site for coal reserve plants")
d.line(r"\multicolumn{5}{L{150mm}}{\emph{Notes.} d: days. Grade A:",
       r"\multicolumn{5}{L{150mm}}{\emph{Notes.} d: days. "
       r"$^{a}$Grade of the evidence: A, balance-sheet data for the industry itself; B, data for a group of industries, or physical stock "
       r"data; C, indirect evidence; D, assumed. "
       r"$^{b}$Ratio series: the ratios that the Bundesbank computes from the annual accounts of German firms, by industry division "
       r"(\emph{Jahresabschlussstatistik, Verh\"altniszahlen}, edition of May 2026). The ratio used here is the non-finished stock, that "
       r"is, inventories less finished goods and merchandise, over material costs, in days. It includes work in progress (WIP), the goods "
       r"that a firm is still making, so it is an upper bound for the purchased inputs. "
       r"$^{c}$BLE: the German Federal Office for Agriculture and Food. "
       r"$^{d}$FIBEN: the sector sheets of the Banque de France~\citep{banquefrance2025fiben} (median stocks over turnover). "
       r"$^{e}$RHB (\emph{Roh-, Hilfs- und Betriebsstoffe}): raw materials, consumables and supplies over material costs, times 365, from "
       r"the extrapolated corporate balance sheets of the Bundesbank~\citep{bundesbank2025}, for 2023, with the 2019 value in brackets. "
       r"$^{f}$Census: the M3 survey of the US Census Bureau~\citep{census2026m3} (materials-and-supplies inventories over the cost of "
       r"materials). "
       r"$^{g}$BAFA: the German Federal Office for Economic Affairs and Export Control (official oil statistics). "
       r"$^{h}$EBV: the German petroleum stockholding association~\citep{ebv2025}; CSE: the central stockholding entities of the other "
       r"member states. "
       r"$^{i}$EKBG: the German reserve-plant act of 2022~\citep{ekbg2022}.} \\")

# ---- S2: the paragraph title, the CCNR in full (N09) ----------------------------------------------------------------
d.line(r"\paragraph{Calibration procedure}", r"\paragraph{Calibration procedure.}")
d.sub(r"the tonnage along the Rhine (the CCNR\todo{define somewhere CCNR in the main text and in the SI} cross-section counts at Emmerich "
      r"and Iffezheim and its estimates between them \citep{ccnr2023})",
      r"the tonnage along the Rhine (the cross-section counts of the Central Commission for the Navigation of the Rhine, CCNR, at Emmerich "
      r"and Iffezheim and its estimates between them \citep{ccnr2023})")

# ---- S3: the 10 cm anchor of the loading curve restored; the headroom ----------------------------------------------
d.sub("\n15 & 0.24 & KBN (Koninklijke Binnenvaart Nederland)",
      "\n10 & 0.18 & as the rows above and below & no measurement at this gauge & an anchor of the curve, on the line between the value "
      "at 5 cm and the count at about 12 cm \\\\\n15 & 0.24 & KBN (Koninklijke Binnenvaart Nederland)")
d.sub(r"the tonnage of the reach in the CCNR cross-section counts \citep{ccnr2023}, with a 2\% headroom. At Kaub,",
      r"the tonnage of the reach in the CCNR cross-section counts \citep{ccnr2023}; the factor 1.02 leaves a headroom of 2\,\% over the "
      r"model's own flow. At Kaub,")

# ---- S5: the weekly table of flows turned away at Kaub without its column "total" (point 4) -----------------------
d.sub("the tonnage that the capacity limit turns away: in total, rerouted on another route and blocked.",
      "the tonnage that the capacity limit turns away, split between what is rerouted on another route and what is blocked.")
inner = d.block("si_gate")
if inner and "{rllrrrrr}" in inner:
    new = inner.replace("{rllrrrrr}", "{rllrrrr}")
    new = new.replace("and the tonnage (kt) that the capacity limit turns away, in total, rerouted on another route and blocked "
                      "(returned to the supplier's inventory).}",
                      "and the tonnage (kt) that the capacity limit turns away: rerouted on another route, or blocked "
                      "(returned to the supplier's inventory).}")
    new = new.replace(r"\multicolumn{3}{c}{flows turned away (kt)}", r"\multicolumn{2}{c}{flows turned away (kt)}")
    new = new.replace(r"\cmidrule(lr){6-8}", r"\cmidrule(lr){6-7}")
    new = new.replace("& loading share & total & rerouted & blocked", "& loading share & rerouted & blocked")
    rows = 0

    def drop_total(m):
        global rows
        rows += 1
        return f"{m.group(1)} & {m.group(2)}"
    new = re.sub(r"^(\d+ & \d{4}-\d{2}-\d{2} & [^&]+ & -?[\d.]+ & [\d.]+) & \d+ & (\d+ & \d+ \\\\)$", drop_total, new, flags=re.M)
    checks = {"caption": "in total" not in new, "header": new.count("& loading share & rerouted & blocked") == 2,
              "group header": new.count(r"\multicolumn{2}{c}{flows turned away (kt)}") == 2, "rule": new.count(r"\cmidrule(lr){6-7}") == 2,
              "rows": rows == 23}
    bad = [k for k, ok in checks.items() if not ok]
    if bad:
        d.fails.append(f"si_gate: {bad} (rows changed: {rows})")
    else:
        d.block("si_gate", new)
elif inner:
    print("   already applied: si_gate has seven columns")

# ---- S6: the French chain (point 6) ---------------------------------------------------------------------------------
d.sub("\n\nFor French buyers, the largest missing deliveries are farm products to the food industry, withheld at the river "
      r"(\FRAFarmWithheldBn~billion), and German inputs (\FRAfromDEUBn~billion), especially chemicals and power; most of these go to "
      "households and to chemical and power plants whose output barely moves. Tables of the disrupted chains",
      " Tables of the disrupted chains")

# ---- S7, S8: the table of rail weeks (N12) --------------------------------------------------------------------------
d.sub(r"(Table~\ref{tab:railweeks}; the cut bulk that finds a rail route is", "(the cut bulk that finds a rail route is")
d.remove_block("si_rail_weeks")
d.sub("The closer fit of the no-substitution rule does not establish that the emergency capacity of 2018 was zero.",
      r"The 50 kt ceiling is reached in \RailBindFifty{} of the 23 profile weeks of 2026 and in \RailBindFiftyyy{} of the 22 of 2018, the "
      r"140 kt ceiling in \RailBindHundredForty{} and \RailBindHundredFortyyy. "
      "The closer fit of the no-substitution rule does not establish that the emergency capacity of 2018 was zero.")

d.save()
