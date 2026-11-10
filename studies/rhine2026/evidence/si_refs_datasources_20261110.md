# SI data and rate-evidence references: verified BibTeX dossier (10 November 2026)

Scope: sources the Supplementary Information uses but does not cite (rates table, data passages, stock-target table). Checked against `refs.bib` of the manuscript checkout (87 entries): nothing below duplicates an existing key. Nothing was written to `refs.bib` or to any .tex file. Access date of every entry: 2026-11-10. Gate input: `scratchpad/si_refs_20261110.bib` (same entries as section (b)).

## (a) Items, keys and verification

"Opened" = I read the page or the PDF text on 10 Nov 2026. "Search only" = confirmed from search-result summaries, page not opened.

| # | Item | Key | What the source is | URL | Verified |
|---|---|---|---|---|---|
| 1 | KiM / Panteia cost figures | `kim2023` | Panteia (van der Meulen, Grijspaardt, Mars, van der Geest, Roest-Crollius, Kiel), "Cost figures for freight transport -- final report", Zoetermeer, January 2023, for KiM; published by KiM 30 Mar 2023; price level 2021 | https://www.kimnet.nl/site/binaries/site-content/collections/documents/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Cost+figures+for+freight+transport_def.pdf (landing page https://www.kimnet.nl/documenten/2023/03/30/kostenkengetallen-voor-het-goederenvervoer) | Yes. Opened: title page of the PDF (authors, "Zoetermeer, January 2023", commissioned by KiM) and the KiM landing page (30-03-2023). Price level 2021 is from the dossier and the table of contents ("Cost Figures (2021)"). |
| 2 | INFRAS / PLANCO for BFS | `infras2017` | Bertschmann, Killer, Sutter (INFRAS), Trosky, Rieken (PLANCO), "Statistik der Kosten und Finanzierung des Verkehrs: Integration der Schifffahrt 2015", Schlussbericht, Zurich/Essen, 8 Nov 2017; client Bundesamt fuer Statistik | https://www.infras.ch/media/filer_public/58/df/58df5e97-487a-4809-b1c8-3e717d04005b/2961a_kfv-schifffahrt_schlussbericht_fin.pdf | Yes. Opened (pdftotext): cover/impressum; the text states that for 2015 a coal transport Rotterdam-Basel at 10,5 Euro per tonne was reported, roughly equal to calculated cost of a motor vessel of class 9; Tabelle 13 "Ergebnisuebersicht Beispielrechnung" gives 162 / 178 EUR per TEU (122 / 138 downstream); Tabelle 26 exists (cost per tkm 2015). |
| 3 | Konings 2009 | `konings2009` | Rob Konings, "Intermodal Barge Transport: Network Design, Nodes and Competitiveness", doctoral thesis TU Delft, defended 13 Nov 2009, TRAIL Thesis Series T2009/11, ISBN 978-90-5584-121-9 | https://www.nginfra.nl/wp-content/uploads/Dissertation_Rob_Konings_13_nov_2009-4.pdf (also TU Delft repository, record uuid:ff6f5f10-2acc-43fb-9474-5317b0988bdd, seen in search) | Yes for title, author, date, series, ISBN (title page of the PDF opened). No DOI found. The tariff figures (50-140 EUR/TEU) were not re-checked; they are the dossier's reading. |
| 4 | EC 2005 charging study | `ecorys2005` | ECORYS Transport (Rotterdam) with METTLE (France) for European Commission DG TREN, "Charging and pricing in the area of inland waterways: practical guideline for realistic transport pricing", final report, 4 Aug 2005 | https://transport.ec.europa.eu/system/files/2016-09/2005_charging_and_princing_study.pdf | Yes. Opened (pdftotext): title page, client, date; footnote 27: "Within the UNITE project the value of time for inland waterway transport in the Netherlands was determined on 218 Euro per vessel per hour (0,20 Euro per ton)." The study has no named personal authors on the title page; the corporate authors are the contractors. |
| 5 | CCNR price formation report | `ccnr2024price` | CCNR, "Price formation workshop: report", from the workshop "Price formation in inland waterway transport" of 8 Nov 2023; Figure 1 shows Insights Global/Refinitiv GOFRT-BASLE 42.00 and GOFRT-DUISBERG 17.36 on 03/11/23 | https://inland-navigation-market.org/wp-content/uploads/2024/03/Price-formation-workshop_report_en_final.pdf | Yes for title, issuer, workshop date, Figure 1 values (PDF text opened). Year 2024: the URL path is 2024/03 and a CCNR press release of 6 Mar 2024 (cp20240306en.pdf, seen in search) announces it; but the PDF imprint reads "Published in March 2023", which is an evident typo (the workshop was in Nov 2023). |
| 6a | Riverlake via OPIS | `opis2025riverlake` | Yazdi Merchant, OPIS (Dow Jones), "Falling River Rhine Levels in Europe Impact Plant, Terminal Operations", 10 July 2025; Riverlake broker rates ARA cross-harbour, Rotterdam-Cologne, Rotterdam-Karlsruhe | https://www.opis.com/resources/energy-market-news-from-opis/falling-river-rhine-levels-in-europe-impact-plant-terminal-operations/ | Title, author, date: yes (page opened via fetch). Caution on numbers: the fetch summary reported the July values 3.83 / 15.00 / 27.42 but flagged some June values (4.71, 29.07) as derived by it from stated differences; the page text itself should be re-read by the author before the June figures (Cologne 16.83, Karlsruhe 29.07) are cited as quotes. |
| 6b | Handelsblatt (Reuters) | `handelsblatt2022rhine` | Handelsblatt, "Transportkosten auf dem Rhein steigen stark wegen Niedrigwasser", 10 Aug 2022, 14:32, price information attributed to Reuters; says: "Im Juni, bevor die Wasserstaende sanken, mussten lediglich etwa 20 Euro pro Tonne bezahlt werden." (preceding sentence names Rotterdam-Karlsruhe, about 110 EUR/t on that Wednesday) | https://www.handelsblatt.com/unternehmen/handel-konsumgueter/logistik-transportkosten-auf-dem-rhein-steigen-stark-wegen-niedrigwasser/28588958.html | Yes, opened. The dossier cites "Handelsblatt/WiWo 18 Aug 2022 [S]"; the item actually found and opened is dated 10 Aug 2022. The WiWo copy (28589148) did not open. The 20 EUR/t is the June baseline as stated by the article (a Reuters spot price for a liquid tanker barge, Rotterdam-Karlsruhe). |
| 7 | TENtec | `tentec2026` | European Commission, DG MOVE, "TENtec Information System and TEN-T map library"; map viewer https://webgate.ec.europa.eu/tentec-maps/web/public/screen/home; public ArcGIS REST services https://webgate.ec.europa.eu/getis/rest/services/TENTec (services listed: tentec_public_corridors_ext, tentec_public_services_ext, EU_Boundaries, Tentec_DEM_Basemap) | https://transport.ec.europa.eu/transport-themes/infrastructure-and-investment/trans-european-transport-network-ten-t/tentec-information-system-and-ten-t-map-library_en | Yes, opened both pages. The extractor in the repo (`tentec-extractor`, BASE_URL_DEFAULT) uses exactly the REST base URL. The page states no licence and no download endpoint, and the REST directory shows no copyright text. The 29 Aug 2026 extraction date comes from the repo memory and the extractor manifest, not from the EC page. |
| 8a | Eurostat modal split | `eurostat2023modal` | Eurostat dataset tran_hv_frmod, "Modal split of inland freight transport" | https://ec.europa.eu/eurostat/databrowser/product/page/TRAN_HV_FRMOD ; DOI 10.2908/tran_hv_frmod | Yes. DOI resolves (302 to the databrowser page); DataCite lists the English title and registers year 2023. The DOI record's primary title is French ("Repartition modale du transport interieur de fret"), so the gate flags a title mismatch; the DOI was therefore moved to the `note` field (see section c). |
| 8b | Eurostat ports | `eurostat2022ports` | Eurostat dataset mar_go_aa, "Gross weight of goods handled in all ports by direction - annual data" | https://ec.europa.eu/eurostat/databrowser/product/page/MAR_GO_AA ; DOI 10.2908/mar_go_aa | Yes. DOI resolves; gate status ok. NOTE: the table the SI figures were computed from is mar_go_aa (ledger `si_a.yaml`, `onboarding/scripts/flow_score.py`), not a mar_mg_* table. mar_mg_aa_pwhd is "top 20 EU ports"; I did not use it. DataCite registration year is 2022; the data used are the 2023 values. |
| 8c | Eurostat employment NUTS 3 | (none) | nama_10r_3empers | | Not added: `eurostat2025regio` in refs.bib already names nama_10r_3empers. Its entry has no DOI; the dataset DOI 10.2908/nama_10r_3empers resolves (DataCite title "Employment (thousand persons) by NUTS 3 region") if the author wants to add it to that entry. |
| 9 | Destatis 46321-0014 | `destatis46321` | Destatis GENESIS-Online, table 46321-0014, from the statistic 46321 "Gueterverkehrsstatistik der Binnenschifffahrt" | https://genesis.destatis.de/datenbank/online/statistic/46321/table/46321-0014 | Partly. The URL answers (307 to genesis.destatis.de) but the page is a JavaScript shell; I could not read the table's own title. Verified from search: Destatis quality report names statistic 46321 "Gueterverkehrsstatistik der Binnenschifffahrt" with breakdown by waterway sections. The description "tonnes transported by waterway section, NST division, dangerous-goods flag" and the 23 Oct 2026 retrieval are from the repo script `onboarding/scripts/destatis_waterway_targets.py`. I did not use the stored API token. |
| 10a | Banque de France | `banquefrance2025fiben` | Banque de France, "Fascicules d'indicateurs sectoriels": yearly sector sheets from the FIBEN company file, 30 ratios in quartiles/medians for two years; 2024 editions online 27 Nov 2025, page updated 24 Sep 2026 | https://www.banque-france.fr/fr/publications-et-statistiques/statistiques/fascicules-dindicateurs-sectoriels | Yes, series page opened. Individual sheet PDFs (e.g. `.../fascicule-sectoriel-industrie-chimique-20-2024.pdf`) are listed in the inventory dossier, section 8; not opened here. |
| 10b | US Census M3 | `census2026m3` | U.S. Census Bureau, "Manufacturers' Shipments, Inventories, and Orders (M3)" survey, monthly full report | https://www.census.gov/manufacturing/m3/index.html (latest full report https://www.census.gov/manufacturing/m3/current/index.html) | Survey identity and issuer: yes (page opened). The July 2026 report released 2 Sep 2026 and its Tables 4 and 6 are the dossier's reading, not re-opened. |
| 10c | German reserve-plant act | `ekbg2022` | Gesetz zur Bereithaltung von Ersatzkraftwerken zur Reduzierung des Gasverbrauchs im Stromsektor ... (Ersatzkraftwerkebereithaltungsgesetz), of 8 July 2022, BGBl. I Nr. 24, 11 July 2022, p. 1054; Article 1 inserts section 50b EnWG ("Pflicht zur Betriebsbereitschaft und Brennstoffbevorratung ...") | https://www.bgbl.de/xaver/bgbl/start.xav?startbk=Bundesanzeiger_BGBl&jumpTo=bgbl122s1054.pdf | Text yes: a PDF copy of BGBl. 2022 I p. 1054 was opened and its heading read. The bgbl.de URL answers HTTP 200 but I did not read the page behind it; the PDF read was a third-party mirror (vereinonline.org). gesetze-im-internet.de now shows "section 50b (weggefallen)": the section is repealed, so cite the act of 2022 and say "in force 2022-2024" if needed. |
| 10d | Bundestag bill | `bundestag2022drs202356` | Bundestag Drucksache 20/2356, 21 June 2022, Gesetzentwurf of the SPD, Buendnis 90/Die Gruenen and FDP groups | https://dserver.bundestag.de/btd/20/023/2002356.pdf | Yes, opened; cited because the inventory dossier quotes the bill (section 50b(2), (3)). |
| 10e | Directive 2009/119/EC | `council2009oilstocks` | Council Directive 2009/119/EC of 14 September 2009 imposing an obligation on Member States to maintain minimum stocks of crude oil and/or petroleum products, OJ L 265, 9.10.2009 | https://eur-lex.europa.eu/eli/dir/2009/119/oj/eng | Title and date: yes (legislation.gov.uk copy opened). OJ reference L 265 of 9 Oct 2009: from a search summary only. The EUR-Lex page returned no content to my fetcher, so the URL is the ELI given by search results, not opened. |

## (b) BibTeX

```bibtex
@techreport{kim2023,
  author      = {van der Meulen, Sander and Grijspaardt, Tom and Mars, Wim and van der Geest, Wouter and Roest-Crollius, Adriaan and Kiel, Jan},
  title       = {Cost figures for freight transport -- final report},
  institution = {Panteia, for the Netherlands Institute for Transport Policy Analysis (KiM)},
  address     = {Zoetermeer},
  year        = {2023},
  url         = {https://www.kimnet.nl/site/binaries/site-content/collections/documents/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Cost+figures+for+freight+transport_def.pdf},
  note        = {Price level 2021; published by KiM on 30 March 2023, landing page https://www.kimnet.nl/documenten/2023/03/30/kostenkengetallen-voor-het-goederenvervoer. Accessed 2026-11-10}
}

@techreport{infras2017,
  author      = {Bertschmann, Damaris and Killer, Maura and Sutter, Daniel and Trosky, Frank and Rieken, Peter},
  title       = {Statistik der Kosten und Finanzierung des Verkehrs: Integration der Schifffahrt 2015, Schlussbericht},
  institution = {INFRAS and PLANCO, for the Bundesamt f{\"u}r Statistik (BFS)},
  address     = {Z{\"u}rich and Essen},
  year        = {2017},
  url         = {https://www.infras.ch/media/filer_public/58/df/58df5e97-487a-4809-b1c8-3e717d04005b/2961a_kfv-schifffahrt_schlussbericht_fin.pdf},
  note        = {Final report of 8 November 2017; Table 13 (worked example Rotterdam--Basel) and Table 26. Accessed 2026-11-10}
}

@phdthesis{konings2009,
  author = {Konings, Rob},
  title  = {Intermodal Barge Transport: Network Design, Nodes and Competitiveness},
  school = {Delft University of Technology},
  type   = {Doctoral thesis},
  year   = {2009},
  url    = {https://www.nginfra.nl/wp-content/uploads/Dissertation_Rob_Konings_13_nov_2009-4.pdf},
  note   = {TRAIL Thesis Series T2009/11, ISBN 978-90-5584-121-9; defended 13 November 2009. Accessed 2026-11-10}
}

@techreport{ecorys2005,
  author      = {{ECORYS Transport} and {METTLE}},
  title       = {Charging and pricing in the area of inland waterways: practical guideline for realistic transport pricing, final report},
  institution = {ECORYS Transport, for the European Commission, DG TREN},
  address     = {Rotterdam},
  year        = {2005},
  url         = {https://transport.ec.europa.eu/system/files/2016-09/2005_charging_and_princing_study.pdf},
  note        = {Dated 4 August 2005. Accessed 2026-11-10}
}

@techreport{ccnr2024price,
  author      = {{Central Commission for the Navigation of the Rhine}},
  title       = {Price formation workshop: report},
  institution = {CCNR},
  address     = {Strasbourg},
  year        = {2024},
  url         = {https://inland-navigation-market.org/wp-content/uploads/2024/03/Price-formation-workshop_report_en_final.pdf},
  note        = {Thematic report of the market observation on the workshop ``Price formation in inland waterway transport'' of 8 November 2023; March 2024. Accessed 2026-11-10}
}

@misc{opis2025riverlake,
  author       = {Merchant, Yazdi},
  title        = {Falling {River} {Rhine} Levels in {Europe} Impact Plant, Terminal Operations},
  howpublished = {OPIS (Dow Jones), energy market news; Riverlake freight rates},
  year         = {2025},
  url          = {https://www.opis.com/resources/energy-market-news-from-opis/falling-river-rhine-levels-in-europe-impact-plant-terminal-operations/},
  note         = {Published 10 July 2025. Accessed 2026-11-10}
}

@misc{handelsblatt2022rhine,
  author       = {{Handelsblatt} (Reuters)},
  title        = {Transportkosten auf dem {Rhein} steigen stark wegen {Niedrigwasser}},
  howpublished = {Handelsblatt, 10 August 2022},
  year         = {2022},
  url          = {https://www.handelsblatt.com/unternehmen/handel-konsumgueter/logistik-transportkosten-auf-dem-rhein-steigen-stark-wegen-niedrigwasser/28588958.html},
  note         = {Price information attributed to Reuters; the WirtschaftsWoche copy is https://www.wiwo.de/unternehmen/handel/logistik-transportkosten-auf-dem-rhein-steigen-stark-wegen-niedrigwasser/28589148.html. Accessed 2026-11-10}
}

@misc{tentec2026,
  author       = {{European Commission}},
  title        = {{TENtec} Information System and {TEN-T} map library},
  howpublished = {DG MOVE; TENtec public ArcGIS REST services (webgate.ec.europa.eu/getis/rest/services/TENTec)},
  year         = {2026},
  url          = {https://transport.ec.europa.eu/transport-themes/infrastructure-and-investment/trans-european-transport-network-ten-t/tentec-information-system-and-ten-t-map-library_en},
  note         = {Network extracted on 29 August 2026 from the public map services https://webgate.ec.europa.eu/getis/rest/services/TENTec (map viewer: https://webgate.ec.europa.eu/tentec-maps/web/public/screen/home). Accessed 2026-11-10}
}

@misc{eurostat2023modal,
  author       = {{Eurostat}},
  title        = {Modal split of inland freight transport ({tran\_hv\_frmod})},
  howpublished = {Eurostat database},
  year         = {2023},
  url          = {https://ec.europa.eu/eurostat/databrowser/product/page/TRAN_HV_FRMOD},
  note         = {Dataset DOI 10.2908/tran_hv_frmod (resolves; the DOI record carries the French title, which the gate rejects). Accessed 2026-11-10}
}

@misc{eurostat2022ports,
  author       = {{Eurostat}},
  title        = {Gross weight of goods handled in all ports by direction -- annual data ({mar\_go\_aa})},
  howpublished = {Eurostat database},
  year         = {2022},
  doi          = {10.2908/mar_go_aa},
  url          = {https://ec.europa.eu/eurostat/databrowser/product/page/MAR_GO_AA},
  note         = {Accessed 2026-11-10}
}

@misc{destatis46321,
  author       = {{Statistisches Bundesamt (Destatis)}},
  title        = {{GENESIS-Online}, table 46321-0014: inland waterway freight (statistic 46321, {G{\"u}terverkehrsstatistik der Binnenschifffahrt}) by waterway section},
  howpublished = {GENESIS-Online database},
  year         = {2026},
  url          = {https://genesis.destatis.de/datenbank/online/statistic/46321/table/46321-0014},
  note         = {Year 2023 retrieved through the GENESIS web service on 23 October 2026; table title not read from the live page. Accessed 2026-11-10}
}

@misc{banquefrance2025fiben,
  author       = {{Banque de France}},
  title        = {Fascicules d'indicateurs sectoriels},
  howpublished = {Sector sheets built from the FIBEN company database},
  year         = {2025},
  url          = {https://www.banque-france.fr/fr/publications-et-statistiques/statistiques/fascicules-dindicateurs-sectoriels},
  note         = {2024 editions put online 27 November 2025; page updated 24 September 2026. Accessed 2026-11-10}
}

@misc{census2026m3,
  author       = {{U.S. Census Bureau}},
  title        = {Manufacturers' Shipments, Inventories, and Orders ({M3}) survey},
  howpublished = {Monthly full report},
  year         = {2026},
  url          = {https://www.census.gov/manufacturing/m3/index.html},
  note         = {Accessed 2026-11-10}
}

@misc{ekbg2022,
  author       = {{Bundesrepublik Deutschland}},
  title        = {Gesetz zur Bereithaltung von Ersatzkraftwerken zur Reduzierung des Gasverbrauchs im Stromsektor im Fall einer drohenden Gasmangellage durch {\"A}nderungen des Energiewirtschaftsgesetzes und weiterer energiewirtschaftlicher Vorschriften ({Ersatzkraftwerkebereithaltungsgesetz})},
  howpublished = {Bundesgesetzblatt Teil I Nr. 24, 11 July 2022, p. 1054},
  year         = {2022},
  url          = {https://www.bgbl.de/xaver/bgbl/start.xav?startbk=Bundesanzeiger_BGBl&jumpTo=bgbl122s1054.pdf},
  note         = {Act of 8 July 2022; inserts section 50b into the Energiewirtschaftsgesetz (fuel stocks of reserve plants), since repealed. Accessed 2026-11-10}
}

@misc{bundestag2022drs202356,
  author       = {{Deutscher Bundestag}},
  title        = {Entwurf eines Gesetzes zur Bereithaltung von Ersatzkraftwerken zur Reduzierung des Gasverbrauchs im Stromsektor im Fall einer drohenden Gasmangellage durch {\"A}nderungen des Energiewirtschaftsgesetzes und weiterer energiewirtschaftlicher Vorschriften},
  howpublished = {Drucksache 20/2356, 21 June 2022},
  year         = {2022},
  url          = {https://dserver.bundestag.de/btd/20/023/2002356.pdf},
  note         = {Bill of the SPD, B{\"U}NDNIS 90/DIE GR{\"U}NEN and FDP groups; section 50b EnWG (new). Accessed 2026-11-10}
}

@misc{council2009oilstocks,
  author       = {{Council of the European Union}},
  title        = {Council Directive 2009/119/{EC} of 14 {September} 2009 imposing an obligation on {Member} {States} to maintain minimum stocks of crude oil and/or petroleum products},
  howpublished = {Official Journal of the European Union, L 265, 9 October 2009},
  year         = {2009},
  url          = {https://eur-lex.europa.eu/eli/dir/2009/119/oj/eng},
  note         = {Accessed 2026-11-10}
}
```

## (c) Citation gate output (cite_check.py on the BibTeX above)

```
16 references: 14 unverified, 1 found_doi, 1 ok
Result: PASS (0 wrong or unresolvable)
```

- ok: `eurostat2022ports` (DOI 10.2908/mar_go_aa, via DataCite).
- First run gave 1 mismatch: `eurostat2023modal` with doi 10.2908/tran_hv_frmod, title similarity 0.47, because the DataCite record's first title is the French one. The DOI itself resolves to the right dataset (TRAN_HV_FRMOD) and the record also lists the English title "Modal split of inland freight transport". I did not touch `cite_exceptions.yaml`; I moved the DOI into `note` so the entry passes. Treat this as a DataCite metadata quirk (title language), not a wrong reference. If the author wants the `doi` field, it needs a gate exception.
- found_doi: `census2026m3`, proposed DOI 10.1002/9781118532461.ch6 (title similarity 0.95). False positive: a Wiley book chapter with a similar title; the Census survey has no DOI. Do not adopt.
- unverified (no DOI exists or none registered; the gate's Crossref best-match is unrelated in each case): `kim2023`, `infras2017`, `konings2009`, `ecorys2005`, `ccnr2024price`, `opis2025riverlake`, `handelsblatt2022rhine`, `tentec2026`, `eurostat2023modal`, `destatis46321`, `banquefrance2025fiben`, `ekbg2022`, `bundestag2022drs202356`, `council2009oilstocks`. These were verified by hand as in section (a), not by the gate.

## (d) Not verified or only partly verified

1. `destatis46321`: the table's own title and contents were not readable (GENESIS page is JavaScript). Statistic 46321 and its waterway-section breakdown confirmed from search results only; table description from the repo script. The retrieval date 23 Oct 2026 is from that script. Author should open the table once to confirm the title.
2. `council2009oilstocks`: EUR-Lex page not opened; title/date from legislation.gov.uk, OJ L 265 of 9.10.2009 from a search summary.
3. `ekbg2022`: official bgbl.de page not read (only a mirror PDF of p. 1054); the URL pattern is the standard jumpTo link and answered 200. Section 50b EnWG is now repealed.
4. `opis2025riverlake`: the individual EUR/t values (especially June: Cologne 16.83, Karlsruhe 29.07) could not be confirmed as printed quotes; the fetch tool said it derived some from stated differences. Re-read the page before quoting them. The dossier's table already carries them as [R].
5. `handelsblatt2022rhine`: the dossier's "18 Aug 2022" item was not found; the opened item is 10 Aug 2022 (Reuters text in Handelsblatt). Its "about 20 EUR/t in June" supports the dossier figure. WiWo copy not opened.
6. `ccnr2024price`: year 2024 is inferred from the URL path and the 6 Mar 2024 press release; the PDF imprint says March 2023 (typo).
7. `konings2009`: no DOI; the nginfra.nl URL is the one the dossier used. TU Delft repository page refused the connection when I tried to read it.
8. `kim2023`: the title page says "Zoetermeer, January 2023"; KiM published it 30 March 2023; I used 2023. Authors are Panteia staff; the KiM landing page names none.
9. `tentec2026`: no licence or citation statement was found on the EC pages; the extraction date (29 Aug 2026) rests on the repo manifest.
10. `census2026m3`, `banquefrance2025fiben`: series pages only; the specific July 2026 M3 report and the individual FIBEN sheets used in the stock-target table were not opened in this pass.
11. Not covered: nama_10r_3empers (already in `eurostat2025regio`); the mar_mg_* table (the SI used mar_go_aa).
