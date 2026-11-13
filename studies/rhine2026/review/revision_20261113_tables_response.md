# 13 November 2026: Tables S1, S2, S3 and S7 of the SI in plain sentences

The author's request: "Regarding table S1 S2 S3 and S7: I found the text hard to read. Very compact. Think about ways
to simplify: are all numbers and words necessary? Is there some overly compact or technical terms that could be
replaced? The goal is not that readers understand exactly how we extracted the information, but rather get a sense of
the evidence. Give a sample in the chat of replacement (2 rows per table) before any change on the Overleaf."

Eight sample rows were shown in chat. The author's answers: the level is right (sentences, two or three figures per
cell); merge the rows of Table S2 that share a value; two text columns in Table S7. One question was not understood
and is asked again below. Result: Overleaf `14d94d0`, one push.

## The rules applied

1. Full sentences, starting with how the value was obtained: measured, calibrated or assumed.
2. Two or three figures per cell: the one that supports the value, and one that shows agreement or disagreement.
3. No abbreviation that needs a footnote.
4. The unit once, in the heading or the notes.
5. Every statement is taken from the detailed version of the tables. No value of the model changed.

In the text cells of the four tables the figures fall from 428 to 180. The words fall little (2,184 to 1,922): fragments
became sentences.

## What changed, table by table

| Table | Before | Now |
|---|---|---|
| S1, transport costs | 16 rows; more than ten figures in some cells; three footnotes for abbreviations | Same 16 rows. The ten countries with a higher rail cost and the eight waterways with the Rhine's values are named in the notes. The quotes by route and date are summed up as a range. |
| S2, inventories by industry | 40 rows; nine footnotes; each cell listed up to four sources with their codes | 32 rows. The caption says what the evidence is unless a row says otherwise (raw materials of German firms in 2023). Two short notes. |
| S3, inventories by input | 14 rows | Same 14 rows, in sentences. |
| S7, loading curve | 12 rows, three text columns (source, what it measures, treatment) | Same 12 rows, two text columns ("evidence", "how the value is set"). The paragraph before the table says that the loading share is what one vessel loads times the number of vessels that sail, and that the number of vessels is assumed. |

Rows merged in Table S2 (same value, same grade, same evidence):

- publishing, telecommunications and IT services (J58--J63), 10 days;
- finance, arts and recreation, other services, households as employers (K, R, S, T), 7 days;
- professional, scientific and administrative services (M, N), 10 days;
- public administration and education (O, P), 15 days;
- ships, boats and other transport equipment (C301--C309), 60 days.

The first, third and fifth go a little beyond "service rows that are all assumed": the rows had one value, one grade
and the same evidence, which is why they are one row.

## What is no longer in the SI

All of it is in `evidence/si_tables_detailed_20261112.tex`, the four tables as they stood.

- S1: the tanker quotes by route and month; the classes of vessels; the footnotes on CEMT, ARA and TEU.
- S2: the 2019 value of each row, replaced by one sentence of the notes ("lower in every industry where both years
  are reported, by up to a fifth in most and by a quarter to a half in machinery, motor vehicles and electronics");
  the figures that include unfinished products where a figure for raw materials exists; the French figures in days of
  turnover where they measure something else (chemicals, steel, vehicles).
- S3: the article of the law, the name of the Eurostat table, the design range of stockyards.
- S7: the dimensions and tonnages of the tanker, the names of the press outlets, the formulas ("0.15 times 1.9"),
  now a sentence each.

## The question that was not understood, asked again

Shortening the cells removed more than half of the figures (428 to 180 in the text cells of the four tables) and several source names from the SI. A referee who
wants them can no longer find them in the paper. Two ways to handle this:

- **(a)** Say in each caption that the full list of figures and sources is in the data deposit, and include the file
  there. Nothing is lost for a reader who looks for it.
- **(b)** Say nothing. The SI gives a sense of the evidence, and the detail stays in the repository only.

Until the author chooses, the captions say nothing (b), and the detailed tables are kept in the repository, so (a) is
one line per caption.

## Checks

`paper_gate.py --regen`: PASS (`review/paper_gate_20261113_evidence_tables.md`); 60 pages. The value cells of the four
tables still come from the configuration of the runs, and what the sentences say in words is checked against it: the
number of countries and of waterways, "20 % higher", "up to four times higher", the loading share quoted in a row of
Table S7, one value and one grade per merged row of Table S2. All 97 references are still cited.

## Scripts

| File | What it is |
|---|---|
| `si_tables_evidence.py` | The sentences of the four tables |
| `review/patch_tools_20261113_evidence_tables.py` | `si_tables.py`: the three generators print these sentences and check them |
| `review/patch_si_20261113_evidence_tables.py` | Keeps the detailed tables, empties the four blocks, adds the sentence before the loading curve |
| `review/ledger_20261113_evidence_tables.py` | Two ledger entries for that sentence |
| `evidence/si_tables_detailed_20261112.tex` | The four tables as they stood on 12 November |
