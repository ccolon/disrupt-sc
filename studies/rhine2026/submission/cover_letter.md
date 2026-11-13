# Cover letter (final text of 13 November 2026, for double-anonymised peer review)

Built into a Word file by `build_cover_letter.py` (the tokens [email], [ORCID] and [date] are filled at build time;
square brackets that remain are for the author to settle). The letter is read by the editors only. Because the author
chose double-anonymised peer review, it carries what the journal's checklist asks to remove from the manuscript:
author, affiliation, funding, author contributions, the full competing-interests statement and the address of the code.

---

Célian Colon
International Institute for Applied Systems Analysis (IIASA)
Schlossplatz 1, 2361 Laxenburg, Austria
[email] · ORCID [ORCID]

[date]

The Editors
Nature Communications

Dear Editors,

Please consider the enclosed manuscript, "Logistics under drought: how the Rhine low water of 2026 propagates through Europe's supply chains", for publication as an Article in Nature Communications. I submit it to the open cross-journal Collection "Managing cascading and non-linear climate risks": the paper follows how a climate extreme on one river cascades through the supply chains of a continent, how two successive episodes compound, and which adaptation measures curb the loss.

In the summer and autumn of 2026 the Rhine, which carries the fuel, ore and building materials of Europe's industrial core, fell to its lowest levels on record, twice. The statistical studies of the previous record, in 2018, tell us what such an event costs German industry, but not how the loss is generated, where it lands or what would curb it. The manuscript answers those questions with a model that follows every shipment of the European economy over the continent's roads, railways, waterways and sea lanes: 12,719 firm agents in the twenty-seven member states and Switzerland, 1.38 million supplier–buyer links, a weekly clock, input inventories at the levels of each industry's balance-sheet statistics, and a river whose weekly carrying capacity follows the Kaub gauge. To my knowledge no supply-chain model of this scope exists: firm-level models of production networks are national and carry no transport layer, the disaster models that represent transport resolve regions, countries and sectors, and the economics of the Rhine itself is statistical. Here every shipment of a continental economy is routed on a shared multimodal network, and the agents that reroute, switch mode, wait or stop are firms.

Three results should interest readers well beyond transport economics. First, the cost of a low river is set by stock-outs, not by freight bills: higher freight rates alone cause no loss of production, while one more week of inventories or a fairway twenty centimeters deeper would each remove two-fifths of the loss. Second, timing and profile matter: the same reduction of river capacity spread evenly over the season would cost 45 % less, and the two low-water episodes of 2026 cost 12 % more in sequence than apart, because the second meets inventories that the first has drained. Third, most of the loss lies outside the industrial zones of the Rhine: services carry the largest share, reached through fuel and building materials, which the production statistics of industry do not measure, and the economy-wide loss is more than two and a half times the industrial loss.

Every parameter is set from external evidence or calibrated on normal traffic; one modeling choice, the representation of the river, was made on the 2018 event, whose published statistical estimate the model reproduces within the estimate's uncertainty band. The simulations use the Rhine as observed to 10 November 2026. The last three weeks of the river profile rest in part on the forecasts of the Federal Institute of Hydrology. During review I will replace them with the observed record and rerun the reference simulation; if the results vary significantly, I will rerun all simulations of 2026 and update every number, and otherwise report the comparison in the Supplementary Information. The estimate was made before the German production statistics of October to December 2026 were published; the monthly path that the model implies is given in the Supplementary Information. The code is open, and every number in the text is generated from the run outputs. The estimates of the 2026 event made during the summer extrapolated the 2018 statistics or ran a regional model of the Rhine corridor; this is, to my knowledge, the first from a model of supply-chain propagation.

The paper suits Nature Communications because it joins three communities the journal serves, climate impacts, complex networks and economics, around a question that policy-makers in Europe are asking now, with a mechanism-level answer that statistics alone cannot give, and with a benchmark on the 2018 event.

This manuscript is not under consideration elsewhere, and there is no related manuscript under consideration or in press. [No preprint has been posted.] The work was not discussed with a Nature Communications editor before submission. I have chosen double-anonymized peer review: the manuscript and the Supplementary Information carry no author information, and what was removed from them is given below.

[Suggested reviewers, to keep only after checking each for conflicts of interest: Elco Koks (Vrije Universiteit Amsterdam), multiregional models of disaster impacts and infrastructure risk in Europe; Hiroyasu Inoue (University of Hyogo), firm-level simulation of supply-chain disruption; Christian Otto (Potsdam Institute for Climate Impact Research), loss propagation in the global supply network; Jasper Verschuur (Delft University of Technology), ports, trade and climate risk; Nils Jannsen (Kiel Institute for the World Economy), the statistical estimate of the 2018 low water that the paper uses as its benchmark; Olaf Jonkeren (Netherlands Institute for Transport Policy Analysis), low water and inland shipping on the Rhine.]

Sincerely,

Célian Colon

Information removed from the manuscript for double-anonymized peer review

Author: Célian Colon, sole and corresponding author, International Institute for Applied Systems Analysis (IIASA), Laxenburg, Austria.

Funding: This work was financially supported by the Jubiläumsfonds of the Austrian Central Bank (OeNB) as part of the FutureGVC project (2024–2028).

Author contributions: C.C. conceived the study, developed the model and the European scope, designed and ran the simulations, analyzed the results, and wrote the paper.

Competing interests: The author declares no competing interests.

Code: DisruptSC is open source under the GPL-3.0 license at https://github.com/ccolon/disrupt-sc; the study scripts are in studies/rhine2026 of that repository. In the anonymized manuscript the address is replaced by a note, and the author's earlier work is cited in the third person. For the reviewers, an anonymized copy of the code (the model, its tests and the study scripts) is submitted as a supplementary software file.

---

If the author switches to single-anonymised review: drop the sentence on double-anonymized review and the block
"Information removed ...", and upload `main_text.pdf` and `supplementary_information.pdf` instead of the two
`*_anonymous.pdf` files.

If the author gives the address of the public repository in the form instead of uploading
`code_for_review_anonymous.zip` (built by `build_review_code_archive.py`): drop the last sentence of the "Code"
paragraph.
