"""The SI and the references for the 22 Oct application: the port residuals in S2 (September baseline, flagged), the fleet
figures in S10, the uncertainty figure moved into S7 (decision D5), and the data-source references of Methods."""
from pathlib import Path

O = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")


def patch(path: Path, pairs):
    s = path.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
    for old, new in pairs:
        n = s.count(old); assert n == 1, f"{path.name}: {n} occurrences of {old[:90]!r}"
        s = s.replace(old, new)
    path.write_text(s.replace("\n", nl), encoding="utf-8"); print(f"{path.name}: {len(pairs)} replacements")


patch(O / "sections" / "si.tex", [
    # S2: the ports are not calibrated; the residuals stated
    (r"""the Lower Rhine deficit is a stated residual of the study.""",
     r"""the Lower Rhine deficit is a stated residual of the study. The missing Lower Rhine tonnage is the container traffic: the model assigns the Rhine's containers to rail, whereas roughly 10~Mt a year of containers pass Kaub and about 29~Mt sail the river \citep{ccnr2023}.

The port tonnages were inspected, not calibrated. Against the Eurostat gross weight of goods handled in 2023 (which includes transhipment and crude), the model's tonnage through the port connectors of the September 2026 baseline, before the pipeline rule removed crude and gas from the network, was within 30\,\% at Hamburg (86~Mt against about 110), Marseille-Fos (73 against 70), Le Havre (55 against 76), Genoa (40 against 47), Gothenburg (36 against 40) and Bilbao (36 against 30), and at Trieste (72 against 55) and Antwerp-Bruges (153 against 242) within a factor of 1.6; it was wrong in structure on the North Sea, Rotterdam carrying 61~Mt against 402 and Amsterdam 124 against about 95, so that the Dutch Rhine delta between Nijmegen and Rotterdam carries a tenth of its observed tonnage while Emmerich is within 3\,\% of the count; Venice (127 against 25), Szczecin-{\'S}winouj{\'s}cie (113 against 33) and the Norwegian gateway (158~Mt, gas and oil that travel by pipeline in reality and are pipelined in the model since) are artefacts of the external-partner gateways and of a uniform sea tariff. Which North Sea port a cargo enters through changes little for Kaub, since Rotterdam, Amsterdam and Antwerp traffic all cross it, and the Kaub tonnage and its bulk composition are the quantities the loss rests on. The modal split shares the same character: German waterways carry 19\,\% of tonne-kilometres against 7\,\% observed and Czech ones 22\,\% against nearly none, because the model uses the Elbe and the canals at the Rhine's rates; rail is over-used in France, Austria and Italy under one European tariff. None of these flows enters the shock. A recalibration of the port costs, the waterway rates by river and the rail rates by country is planned for the post-event revision\todo{port table on the final baseline pending the flows export}."""),
    # S10: the standard vessel at 30 cm
    (r"""against a tenth of that for a standard unit""", r"""against about half of that for a standard unit"""),
    # S7: the uncertainty figure (from the main text, decision D5 of 22 Oct)
    (r"""\subsection*{S8 Rail}""",
     r"""\begin{figure}[tbp]
\centering
\includegraphics[width=\textwidth]{figures/F8_sensitivity.pdf}
\caption{\textbf{Uncertainties, by type.} German loss as a share of a quarter, 2026 (a) and 2018 (b): the eleven versions of the supplier--buyer network (sampling); the loading curve with its shortfall raised and lowered by 15\,\%; two suppliers per input and no input pooling; for 2026, each channel alone (the capacity limit without the surcharge, the surcharge without the limit); and the rules tested in the revision (Table~\ref{tab:revision}): substitution by rail (none for any bulk shipment; a ceiling of 50 and 140 kt a week for all of them), the refill time of inventories at 15 and 60 days instead of 30, and the service inputs (a 45-day coping duration instead of 90; the power sector's fuel-oil input non-critical). The reference network is the dashed line; the loss without pooling is off the scale. The networks are a sample; the other cases are alternative choices and rules, not draws from a distribution.}
\label{fig:sensitivity}
\end{figure}

\subsection*{S8 Rail}"""),
])

refs = O / "refs.bib"
s = refs.read_text(encoding="utf-8")
if "eurostat2025regio" not in s:
    s = s.rstrip("\n") + r"""

@misc{eurostat2025regio,
  author       = {{Eurostat}},
  title        = {Regional economic accounts: employment by NUTS 3 region and NACE activity (nama\_10r\_3empers), and population on 1 January by NUTS 2 region},
  year         = {2025},
  howpublished = {\url{https://ec.europa.eu/eurostat/web/regions/database}}
}

@misc{spam2020,
  author       = {{International Food Policy Research Institute}},
  title        = {Global Spatially-Disaggregated Crop Production Statistics Data for 2020 (SPAM 2020), version 1.0},
  year         = {2024},
  howpublished = {Harvard Dataverse, \url{https://doi.org/10.7910/DVN/SWPENT}}
}

@misc{gem2025,
  author       = {{Global Energy Monitor}},
  title        = {Global Coal Mine Tracker, Global Oil and Gas Extraction Tracker, Global Steel Plant Tracker, Global Cement and Concrete Tracker, and the power plant trackers},
  year         = {2025},
  howpublished = {\url{https://globalenergymonitor.org/}}
}

@misc{climatetrace2024,
  author       = {{Climate TRACE}},
  title        = {Facility-level emissions and activity inventory, 2022 data (release 2024)},
  year         = {2024},
  howpublished = {\url{https://climatetrace.org/}}
}

@article{fineprint2022,
  author  = {Maus, Victor and Giljum, Stefan and da Silva, Dieison M. and Gutschlhofer, Jakob and da Rosa, Robson P. and Luckeneder, Sebastian and Gass, Sidnei L. B. and Lieber, Mirko and McCallum, Ian},
  title   = {An update on global mining land use},
  journal = {Scientific Data},
  volume  = {9},
  pages   = {433},
  year    = {2022},
  doi     = {10.1038/s41597-022-01547-4}
}
"""
    refs.write_text(s + "\n", encoding="utf-8"); print("refs.bib: 5 data-source entries added")
