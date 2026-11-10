r"""SI revision of 10 Nov 2026: the 19 references added from the two dossiers of the day
(evidence/si_refs_datasources_20261110.md, evidence/si_evidence_sea_vot_rail_20261110.md) with
evidence/add_refs_from_dossier.py. This script tidies what the tool appended: the dated comment lines, the working
remarks left in three notes, bare URLs and an unescaped underscore in notes, accented letters as LaTeX accents.

    python patch_refs_20261110.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "refs.bib")
d.sub("% ---- positioning review of 7 November 2026 (si_refs_datasources_20261110.md); DOIs verified on Crossref by the review",
      "% ---- SI revision of 10 November 2026 (si_refs_datasources_20261110.md): sources of the SI's data and rate evidence, each opened on that day")
d.sub("% ---- positioning review of 7 November 2026 (si_evidence_sea_vot_rail_20261110.md); DOIs verified on Crossref by the review",
      "% ---- SI revision of 10 November 2026 (si_evidence_sea_vot_rail_20261110.md): evidence on the sea rate, the value of time and rail, each opened on that day")
d.sub("note        = {Price level 2021; published by KiM on 30 March 2023, landing page https://www.kimnet.nl/documenten/2023/03/30/kostenkengetallen-voor-het-goederenvervoer. Accessed 2026-11-10}",
      "note        = {Price level 2021; published by KiM on 30 March 2023. Accessed 2026-11-10}")
d.sub("note         = {Price information attributed to Reuters; the WirtschaftsWoche copy is https://www.wiwo.de/unternehmen/handel/logistik-transportkosten-auf-dem-rhein-steigen-stark-wegen-niedrigwasser/28589148.html. Accessed 2026-11-10}",
      "note         = {Price information attributed to Reuters. Accessed 2026-11-10}")
d.sub("note         = {Network extracted on 29 August 2026 from the public map services https://webgate.ec.europa.eu/getis/rest/services/TENTec (map viewer: https://webgate.ec.europa.eu/tentec-maps/web/public/screen/home). Accessed 2026-11-10}",
      "note         = {Network extracted on 29 August 2026 from the public map services. Accessed 2026-11-10}")
d.sub("note         = {Dataset DOI 10.2908/tran_hv_frmod (resolves; the DOI record carries the French title, which the gate rejects). Accessed 2026-11-10}",
      "note         = {Dataset DOI 10.2908/tran\\_hv\\_frmod. Accessed 2026-11-10}")
d.sub("note         = {Year 2023 retrieved through the GENESIS web service on 23 October 2026; table title not read from the live page. Accessed 2026-11-10}",
      "note         = {Data for 2023, retrieved on 23 October 2026}")
d.sub("title  = {Beförderungsmenge und Beförderungsleistung nach Verkehrsträgern (Güterverkehr)},",
      'title  = {Bef{\\"o}rderungsmenge und Bef{\\"o}rderungsleistung nach Verkehrstr{\\"a}gern ({G{\\"u}terverkehr})},')
d.sub("note   = {Stand 20 April 2026; rail: Jahreserhebung der Schienen-Güterverkehrsstatistik}",
      'note   = {Status of 20 April 2026; rail: annual survey of rail freight statistics}')
d.save()
