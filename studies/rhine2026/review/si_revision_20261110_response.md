# The author's revision of the SI (Overleaf 675722a, 10 November 2026): what was done, note by note

The author revised the Supplementary Information in Overleaf on 10 November 2026: `sections/si.tex` moved to `si.tex` at
the project root, about 50 direct text edits (S1 to S10) and 61 inline notes (`\todo{...}`), numbered N01 to N61 here in
file order (S1: N01-N14, S2: N15-N24, S3: N25-N33, S4: N34-N45, S5: N46, S6: N47, S7: N48, S8: N49-N50, S9: N51-N59,
S10: N60-N61). The extraction (notes with context, word-level edits) is reproducible with the script kept in the session
scratchpad (`si_notes_extract.py <overleaf> fc30932:sections/si.tex si.tex <out.md>`).

## How the revision is handled

1. Pull the Overleaf git bridge (fetch, fast-forward). The author's version is the baseline: their wording stays.
2. Compare it with the last version pushed (fc30932): the direct edits on one side, the notes on the other.
3. Direct edits are kept. Each is read for what it may have broken: LaTeX (a `#`, a `\~`), facts (a number, a reversed
   statement), macros, cross-references, typos. Corrections of that kind are listed below under "direct edits corrected".
4. Each note is answered in the text and then removed. A note that needs a decision only the author can take stays in
   place, reworded as an open question.
5. Numbers never go in by hand: they are macros of `numbers.tex` (written by `make_numbers.py` from the runs) or cells
   that `si_tables.py` checks against the runs. A reworded sentence that carries a claim has its entry in the ledger
   (`paper_gate_ledger/`) updated, and `paper_gate.py` is run before each push (lint, numbers, ledger, compile).
6. New references are verified before they enter `refs.bib` (`cite_check.py`); none is written from memory.
7. One commit and one push per SI section, so the Overleaf history shows one version per section. The commit message
   lists the notes it answers.
8. Nothing is posted or resolved in Overleaf's review panel.

New on 10 November, from the author's comment in the rates table ("consider using the .tex as the source of truth"):
the text of every table (caption, headers, row labels, notes, evidence cells) now belongs to `si.tex`; `si_tables.py`
no longer rewrites a table, it compares the numeric cells with the runs and refreshes only those.

## Step 0 (Overleaf 5b4cbb3)

`main.tex` line 51 still read `\input{sections/si}` in the stand-alone SI build: now `\input{si}`. The tooling
(`si_tables.py`, `paper_gate.py`, `lint_manuscript.py`, `submission/wordcount.py`, the ledger files) reads `si.tex`.
The gate on the revision as received: static 1 FAIL (`Choice #1`, an unescaped `#`), ledger 93 entries whose sentence
was reworded or removed, 64 numbers and 24 number words without a ledger entry; these are cleared section by section.

## Step 1 (Overleaf dffd083): the tables' text belongs to si.tex

The author's comment in the rates table asked what the generator adds and whether the .tex could be the source of
truth. Answer: the generator guarantees that every table number equals the run outputs and the configuration, and
refreshes them in one command after a batch; its cost was that captions and labels could not be edited in Overleaf.
From now on `si_tables.py` leaves a table that exists in `si.tex` alone and only compares its numeric cells with the
runs (`--check`), refreshing a cell that differs; captions, headers, row labels, notes and evidence cells are edited in
`si.tex`. A change of structure (a column removed, a table split) still needs the generator brought in line, which is
done here for each such note. The gate now reads the captions as prose.

## S1 Scope and data (Overleaf 85d4323)

| Note | Answer |
|---|---|
| N01, N02 | Sources cited in the Agents paragraph: SPAM 2020, the GEM trackers, Climate TRACE, FINEPRINT, the Eurostat regional accounts (keys already in refs.bib). The Bundesbank statistics are cited in the Inventories paragraph. |
| N03 | A household agent sits at an interior point of its NUTS2 region, near the geometric center (`representative_point` of the polygon in `eurostat_nuts_households.py`); it is not a population-weighted centroid and not the largest city. The sentence now says so. |
| N04 | TENtec cited (new key tentec2026: the Commission's TENtec information system and its public map services). |
| N05 | Rates table: the caption names the main sources in two lines; the general remarks (EUR = USD, what operator costs are, ARA, TEU, vessel classes) are notes under the table. |
| N06 | "The Panteia comparison" is now "the operator cost of a tractor-semitrailer at fleet average, empty legs included, 0.115 EUR per tonne-kilometer in 2018", cited (kim2023). |
| N07 | Yes, the liquid-bulk road and rail values are set on the German split alone; the cell says so. New and worth knowing: the Dutch operator cost of a liquid-bulk charter train is 0.018 EUR per tonne-kilometer (KiM 2023, Table 6.2), 4.7 times below the model's 0.085, so the cell calls the value an effective cost, not a tariff. |
| N08, N10 | Every number of the evidence column carries its source (kim2023, infras2017, konings2009, opis2025riverlake, handelsblatt2022rhine, ccnr2024price, ecorys2005). |
| N09 | Sea rate: KiM 2023, Table 5.5 gives 0.0014 EUR per tonne-kilometer for container carriers, 0.0034 for bulk carriers and 0.0051 for tankers. The model's 0.0015 matches containers and is two to three times too low for bulk; the cell says both. "Do not influence the results" was not kept: no run tests it. The cell says that sea lanes carry no capacity limit and that the rate bears on the port of landing. |
| N11 | Value of time: no commodity-specific value exists in what was found. The meta-analysis of Binsuwadan et al. (2022) gives, for shippers in Germany, 1.59 (road), 0.27 (rail), 0.19 (sea) and 0.09 (inland waterway) USD per tonne-hour. The model's road and sea values for containers and its 0.08 for bulk are in line; its 1.00 on rail and 0.32 on waterways are three to four times higher. The cells say so. |
| N12 | Inventory table: the "lean" column is removed (the 2019 values are in the evidence cells); grades and acronyms are notes under the table. |
| N13 | The input-specific targets are a table of their own (Table S3, label tab:stockoverrides) with the columns buyer, input, days, grade, evidence and modeling reason. |
| N14 | Criticality table: the note column is replaced by lettered notes under the table. |

Not asked but changed with these notes: the rail cell said "within the range of block-train and intermodal rates in
Europe (0.02-0.04)"; no source states that range (KiM 2023: 0.014 for a dry-bulk charter train, 0.045 for a container
shuttle; IRG-Rail: average revenue 0.036 in 2019, 0.047 in 2024), so the cell now gives these figures. In the two
inventory tables, pointers to the evidence dossier ("see 6.3", "see 6.4"), German terms and dates of development runs
were replaced by plain statements. "Stock targets" reads "Inventory targets" in the two captions.

Direct edits corrected: "frm"; "is clipped NUTS3"; "Pichler et al. (2022)~citet" and "Rauch (1999).~citep" (the name
was printed twice); "Facility statuses are taken from the 2022 accounts" (the accounts hold no statuses: now "those of
2022, the reference year of the input-output table"); the sentence without a verb on the number of agents; power plants
were listed among the facilities "kept as points" while they are aggregated to NUTS2; straight quotes in the criticality
caption.

References: 19 entries added to refs.bib from two dossiers written the same day, every source opened
(`evidence/si_refs_datasources_20261110.md`, `evidence/si_evidence_sea_vot_rail_20261110.md`). To confirm by the author:
the title of Destatis table 46321-0014 (the page could not be read by the search), and the June figures of the OPIS
article (the July figures were read, the June ones follow from stated differences).

