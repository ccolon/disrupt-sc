r"""SI revision of 10 Nov 2026, S4: the crossed experiments are two tables (N44), so the main text's reference to the
waves at a 15-day refill time points to the new one (tab:crosswaves); the reference to the levers under the rail
ceiling keeps tab:cross.   python patch_main_20261110_s4.py [overleaf]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from si_patchlib import OVERLEAF, Doc  # noqa: E402

ov = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERLEAF
d = Doc(ov / "main.tex")
d.sub(r"and with 15 days it disappears (Fig.~\ref{fig:waves}b, Supplementary Table~\ref{tab:cross})",
      r"and with 15 days it disappears (Fig.~\ref{fig:waves}b, Supplementary Table~\ref{tab:crosswaves})")
d.save()
