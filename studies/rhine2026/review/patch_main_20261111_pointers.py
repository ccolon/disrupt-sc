r"""Main text, 11 November 2026: the pointers to the sections of the SI follow its new structure
(patch_si_20261111_structure.py). Each pointer is updated to where its content now is:

  former S3, the test paragraphs                 -> S6 The 2026 test
  former S5, the modal-switch rule               -> S5 (same number)
  former S5, flows at Kaub, capacity and surcharge, the waves at a 15-day refill -> S7
  former S6, prices and missing inputs           -> S7
  former S7, sensitivity                         -> S9
  former S8, rail and the fleet                  -> S8 (same number)
  former S9, the 2018 benchmark and the river    -> S5

    python patch_main_20261111_pointers.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

d = Doc(OVERLEAF / "main.tex")
SS = "Supplementary Section~"
PAIRS = [
    (f"kept for evaluation against the statistics ({SS}S3)", f"kept for evaluation against the statistics ({SS}S6)"),
    ("a rule that sensitivity runs test both ways (Supplementary Sections~S7 and S8)", "a rule that sensitivity runs test both ways (Supplementary Sections~S8 and S9)"),
    (f"loading curve and inventories, {SS}S9)", f"loading curve and inventories, {SS}S5)"),
    (f"but out of the wrong months ({SS}S9)", f"but out of the wrong months ({SS}S5)"),
    (f"(Fig.~\\ref{{fig:validation}}b, {SS}S7)", f"(Fig.~\\ref{{fig:validation}}b, {SS}S9)"),
    (f"may explain in part ({SS}S3)", f"may explain in part ({SS}S6)"),
    (f"the catch-up gain appears with any gap ({SS}S5)", f"the catch-up gain appears with any gap ({SS}S7)"),
    ("(Supplementary Fig.~\\ref{fig:sensitivity}; Supplementary Sections~S7 and S8)", "(Supplementary Fig.~\\ref{fig:sensitivity}; Supplementary Sections~S8 and S9)"),
    (f"even at the surcharges of the worst weeks ({SS}S6)", f"even at the surcharges of the worst weeks ({SS}S7)"),
    (f"the rest is rationing along the chains that start there ({SS}S6)", f"the rest is rationing along the chains that start there ({SS}S7)"),
    (f"and water transport (\\ShareShipping\\,\\%) ({SS}S6)", f"and water transport (\\ShareShipping\\,\\%) ({SS}S7)"),
    (f"scored at revision under the protocol of {SS}S3", f"scored at revision under the protocol of {SS}S6"),
    (f"a run with two is reported as a sensitivity ({SS}S7)", f"a run with two is reported as a sensitivity ({SS}S9)"),
    (f"Multiples of these targets are tested in {SS}S7", f"Multiples of these targets are tested in {SS}S9"),
    (f"The weekly demand and deliveries at Kaub are reported in {SS}S5", f"The weekly demand and deliveries at Kaub are reported in {SS}S7"),
    (f"is documented with its results in {SS}S9", f"is documented with its results in {SS}S5"),
    (f"two stress paths ({SS}S7), not bounds", f"two stress paths ({SS}S9), not bounds"),
    (f"the representation of the river, between two options ({SS}S9)", f"the representation of the river, between two options ({SS}S5)"),
    (f"and the comparisons are reported as sensitivities ({SS}S7)", f"and the comparisons are reported as sensitivities ({SS}S9)"),
    (f"{SS}S9 gives the coefficients", f"{SS}S5 gives the coefficients"),
    (f"the wave profiles at a refill time of 15 days) are listed in {SS}S7", "the wave profiles at a refill time of 15 days) are listed in Supplementary Sections~S7 to S9"),
    (f"of the study folder ({SS}S7)", f"of the study folder ({SS}S9)"),
    (f"detailed in {SS}S3, scores", f"detailed in {SS}S6, scores"),
    (f"are pre-specified in {SS}S3 and Table", f"are pre-specified in {SS}S6 and Table"),
]
for old, new in PAIRS:
    d.sub(old, new)
d.save()
