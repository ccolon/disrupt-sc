r"""SI, round of 11 November 2026, part B: notes N01 to N03 of the author's version of that morning, in the table of
transport cost parameters. The evidence is in evidence/si_evidence_transfers_fx_20261111.md (every figure read in its source).

  N01  road--rail transfer: the German appraisal rates (Planco et al. 2015, Table 8-25) and two operators' price lists of 2026;
  N02  waterway--sea transfer: the cost of a container lift and the time of a barge in the port of Rotterdam (Konings 2009);
  N03  "USD and EUR are treated as equal" gives way to a statement of the currencies and of the 2022 exchange rate.

Four entries are added to refs.bib: planco2015bvwp, duss2026price, dbis2026price, ecb2026exrusd.
    python patch_si_20261111_b.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "si.tex")
d.sub(r"Intermodal terminals and bulk sidings at both ends of a rail trip\todo{add evidence}. \\",
      r"Intermodal terminals and bulk sidings at both ends of a rail trip. The German appraisal rates for a transfer between road, rail "
      r"and inland vessel are 20.80 EUR per container, 2.60 EUR per tonne of dry bulk and 2.90 of liquid bulk (2012 "
      r"prices)~\citep{planco2015bvwp}; two German terminal operators charge 30.50 EUR per loading unit in "
      r"2026~\citep{duss2026price,dbis2026price}. At 10 tonnes per unit, the container and dry-bulk values are close to the appraisal "
      r"rates, and the liquid-bulk value is a third of its rate. No published dwell time was found; the hours are assumptions. \\")
d.sub(r"waterway--sea & 8 h / 2 & Port handling\todo{add evidence}. \\",
      r"waterway--sea & 8 h / 2 & Port handling. As in the row above, a container lift costs 35--40 EUR per TEU in the port of "
      r"Rotterdam~\citep{konings2009}, that is 3.5--4 EUR per tonne: the model's value is about half of it. A barge spends about 8 hours "
      r"sailing between the terminals of that port and about one hour waiting at each~\citep{konings2009}. No published figure was found "
      r"for bulk. \\")
d.sub(r"\emph{Notes.} USD and EUR are treated as equal\todo{can be easily criticized, it would not cost much to add a conversation factor, "
      r"e.g., 2022 average?}. Operator costs are",
      r"\emph{Notes.} The model is in US dollars of 2022. Values in euros are quoted as their sources give them, at the price level of the "
      r"year named; one euro was worth 1.05 US dollars on average in 2022~\citep{ecb2026exrusd}. Operator costs are")
d.save()

# ---- refs.bib: four sources, each opened on 11 November 2026 (see the dossier) --------------------------------------
NEW = r"""
@techreport{planco2015bvwp,
  author      = {{Planco Consulting GmbH} and {Intraplan Consult GmbH} and {TUBS GmbH}},
  title       = {Grunds{\"a}tzliche {\"U}berpr{\"u}fung und Weiterentwicklung der Nutzen-Kosten-Analyse im Bewertungsverfahren der Bundesverkehrswegeplanung, Endbericht},
  institution = {Bundesministerium f{\"u}r Verkehr und digitale Infrastruktur},
  address     = {Essen, Berlin and M{\"u}nchen},
  year        = {2015},
  url         = {https://svn.vsp.tu-berlin.de/repos/public-svn/publications/vspwp/2014/14-12/PlancoItpTubs2015FeBerichtBvwpMethodik.pdf},
  note        = {FE-Projekt 960974/2011, 24 March 2015; Section 8.1.5.6 and Table 8-25, p. 270 (price level 2012). Accessed 2026-11-11}
}

@misc{duss2026price,
  author = {{Deutsche Umschlaggesellschaft Schiene--Stra{\ss}e (DUSS) mbH}},
  title  = {{DUSS} 2026 Price List},
  year   = {2026},
  url    = {https://duss-terminal.deutschebahn.com/resource/blob/13623682/2bf0e1730edda72f9e02e7f890817b3b/2026-DUSS-price-list_EN-1-1-2026-data.pdf},
  note   = {Valid from 1 January 2026; Section 1. Accessed 2026-11-11}
}

@misc{dbis2026price,
  author = {{DB Intermodal Services GmbH}},
  title  = {Price list for terminal services},
  year   = {2026},
  url    = {https://www.dbcargo.com/resource/blob/13691804/120457d5f820ef173f07a30fa4f67fe3/EN-Price-list-Terminal-Services-2026-data.pdf},
  note   = {Valid from 1 January 2026; Section 1. Accessed 2026-11-11}
}

@misc{ecb2026exrusd,
  author = {{European Central Bank}},
  title  = {Euro foreign exchange reference rates: {US} dollar, annual average (series {EXR.A.USD.EUR.SP00.A})},
  year   = {2026},
  url    = {https://db.nomics.world/ECB/EXR/A.USD.EUR.SP00.A},
  note   = {Read on the DBnomics mirror of the ECB Data Portal; 1.0530 for 2022, as in the Eurostat table ert\_bil\_eur\_a. Accessed 2026-11-11}
}
"""
p = OVERLEAF / "refs.bib"
raw = p.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")
keys = ["planco2015bvwp", "duss2026price", "dbis2026price", "ecb2026exrusd"]
present = [k for k in keys if "{" + k + "," in text]
if len(present) == len(keys):
    print("refs.bib: the four entries are already there")
elif present:
    sys.exit(f"refs.bib: only some of the entries are there ({present}); nothing written")
else:
    text = text.rstrip("\n") + "\n" + NEW
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("refs.bib: 4 entries added")
