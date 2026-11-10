r"""SI revision of 10 Nov 2026, section S6 Two representations of the river (the author's note N47, and N56 on the
paragraph that receives its message).

N47  The section is removed. Its main message is one paragraph, placed where the note says it was repeated: 'Choice 1'
     of the section on the 2018 event, which now holds the table of the two representations (label tab:representations).
N56  That paragraph is short (the onset decides; the November peak is not discussed) and its two options have one
     name each, those of the main text: the capacity limit, and the floor representation.
The author's draft of the paragraph had the two options the wrong way round ('Option (i) [binary thresholds] captures
the right onset'): it is the capacity limit, with its loading curve, that starts its losses in August; the floor
representation starts in the week of 22 October.
main.tex: the pointer 'Supplementary Sections S6 and S9' reads 'Supplementary Section S9'.

    python patch_si_20261110_s6.py [overleaf]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "si.tex")
MARK = "(edit the caption, headers and text cells here; studies/rhine2026/si_tables.py only checks and refreshes the numbers)"

block = d.remove_block("si_representations")
d.line(r"\subsection*{S6 Two representations of the river}", None)
d.line("Until 22 September 2026 the study represented low water as a price with closures", None)
d.line("%And the shape of the path: a deepest month in November", None)

# the table: a short caption, the two names of the paragraph, 'inventories'
a, b = block.index(r"\caption{"), block.index(r"\label{tab:representations}")
block = (block[:a] + r"\caption{\textbf{Two representations of the river on the 2018 event.} Monthly shortfall of German industrial production (\%), August to December 2018, and its sum over the five months (percent-months): the benchmark, its one-standard-deviation band and its variant with the contemporaneous term only; the capacity limit at five inventory levels; the floor representation at three. All model rows use the same flows, loading curve and supplier--buyer network.}"
         + "\n" + block[b:])
for old, new, n in ((r"benchmark, published specification (central) &", r"benchmark (central) &", 1),
                    (r"benchmark, one-standard-deviation band (16--84\,\%) &", r"benchmark, one-standard-deviation band &", 1),
                    (r"capacity limit, stocks $\times$0.75 &", r"capacity limit, inventories $\times$0.75 &", 1),
                    (r"capacity limit, stocks $\times$1 &", r"capacity limit, inventories $\times$1 &", 1),
                    (r"priced river with closures, $\times$1 &", r"floors, inventories $\times$1 &", 1),
                    (r"priced river with closures, $\times$1.5 &", r"floors, $\times$1.5 &", 1),
                    (r"priced river with closures, $\times$2 &", r"floors, $\times$2 &", 1),
                    (r" & integral \\", r" & sum \\", 1)):
    if block.count(old) != n:
        d.fails.append(f"representations table: {old[:50]}")
    block = block.replace(old, new)

d.line(r"\paragraph{Choice \#1: low water impacts on transport capacity.}",
       r"\paragraph{Choice 1: how low water limits transport.} Two representations of the river were compared on the 2018 event, with the same flows, loading curve, inventories and supplier--buyer network (Table~\ref{tab:representations}). (i) \textit{Capacity limit}: every week the loading curve caps the tonnage that passes Kaub, and a surcharge inversely proportional to the loading share applies. (ii) \textit{Floors}: low water only makes transport dearer, through the same surcharge, until the gauge falls below the floor at which a class of vessels stops sailing (40\,cm for container vessels, 50 for tank barges, 30 for dry-bulk vessels); the reach is then closed to that class. German industrial production was already falling in August 2018, two months before the first week in which any vessel class stopped sailing. The capacity limit reproduces this onset. With the floors the losses start only in the week of \PricedOnsetDate, because a dearer week still moves the full tonnage. The capacity limit was therefore adopted."
       + "\n\n% >>> generated table si_representations " + MARK + "\n" + block + "% <<< generated table si_representations")
d.save()

m = Doc(ov / "main.tex")
m.sub(r"is documented with its results in Supplementary Sections~S6 and S9.", r"is documented with its results in Supplementary Section~S9.")
m.save()
