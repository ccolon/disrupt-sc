"""make_numbers.py: the macros of the ensemble-mean headline (22 Oct 2026, decision D2) and the net loss in bn USD (D4)."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/make_numbers.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
pairs = [
    ('    put("EnsMean", r2(np.mean(e26)), "ensemble of 11 supply-chain draws, mean"); put("EnsSd", r2(np.std(e26, ddof=1))); put("EnsMin", r2(min(e26))); put("EnsMax", r2(max(e26)))\n',
     '    put("EnsMean", r2(np.mean(e26)), "ensemble of 11 supply-chain draws, mean"); put("EnsSd", r2(np.std(e26, ddof=1))); put("EnsMin", r2(min(e26))); put("EnsMax", r2(max(e26)))\n'
     '    put("EnsMeanBn", r1(np.mean(e26) * q26 / 1e3), "bn USD, the ensemble mean of the German loss (22 Oct 2026: the headline is the mean over the eleven networks)")\n'
     '    eu26 = [p.loc[f"2026_{tag}_seed{s}_base", "EU_cum_mUSD"] for s in range(1, 11)] + [b.EU_cum_mUSD]\n'
     '    put("EUlossEnsBn", r1(np.mean(eu26) / 1e3), "bn USD, the 28 economies, mean over the eleven networks")\n'
     '    put("DEUnetBn", r1(b.DEU_net_mUSD / 1e3), "bn USD, German net loss (backlog left at the end of the run + the perishable sectors), reference network")\n'),
    ('        put(f"Lev{name}Range", f"{pct(min(pairs))}--{pct(max(pairs))}", "range over ten paired draws")\n',
     '        put(f"Lev{name}Range", f"{pct(min(pairs))}--{pct(max(pairs))}", "range over ten paired draws")\n'
     '        put(f"Lev{name}Avg", pct(float(np.mean(pairs + [ref]))), "mean over the eleven networks (reference + ten paired draws)")\n'),
]
for old, new in pairs:
    n = s.count(old); assert n == 1, f"{n} x {old[:80]!r}"
    s = s.replace(old, new)
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("make_numbers.py patched")
